#!/usr/bin/env python3
# Copyright 2026 Anna Tchijova
# Licensed under the Apache License, Version 2.0
#
# vigia_agent.py
#
# VIGÍA Autonomous Forensic Agent
# ================================
# Self-correcting agentic loop for SANS FIND EVIL Hackathon 2026.
#
# Architecture: Custom MCP Server pattern (architectural guardrails, not prompt-based).
# Self-correction: deterministic contradiction detection between modules,
#                  automatic re-analysis with adjusted parameters, full audit trail.
#
# Complies with SANS requirements:
#   - Self-correction without human intervention
#   - Accuracy validation: every finding traceable to artifact + tool + SHA-256
#   - Analytical reasoning: structured investigative narrative output
#   - Audit trail: timestamped execution log, full tool sequence traceable
#   - Architectural guardrails: no ML inference, no floats in scoring
#
# Usage:
#   python3 vigia_agent.py --evidence /path/to/evidence --case-id CASE-001
#   python3 vigia_agent.py --help

from __future__ import annotations

import argparse
import decimal
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.runtime_fingerprint import runtime_execution_fingerprint

# ── Forensic logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("vigia-agent")

# ── Agent constants ──────────────────────────────────────────────────────────
AGENT_VERSION = "1.0.0-SANS-2026"
MAX_ITERATIONS = 3                    # Hard cap — prevents infinite loops
CONTRADICTION_THRESHOLD = 2           # int: minimum contradictions to trigger re-analysis
CONFIDENCE_FLOOR = Fraction(3, 10)    # Minimum MCA threshold for conclusive verdict

# ── Verdict classification ────────────────────────────────────────────────────
# Exit codes (documented): 0=no evil, 1=evil, 2=error, 3=intent, 4=ABSTAIN,
# 5=suspicion. Hasta 2026-07-10 el 3 era compartido "intent/suspicion"
# (SUSPICION no era un veredicto sellado); con B-097 aplicado, SUSPICION es
# veredicto de primera clase y recibe código PROPIO (5) — compartir código
# entre dos veredictos distintos era confuso para cualquier consumidor del
# exit. Se asignó el código NUEVO al veredicto NUEVO: INTENT conserva el 3
# (contrato histórico — todo bundle sellado hasta hoy con exit 3 era familia
# INTENT); ningún consumidor externo de códigos específicos existe en el
# árbol (grep 2026-07-10: solo vigia_agent + tests).
EXIT_NOISE     = 0
EXIT_MALICE    = 1
EXIT_ERROR     = 2
EXIT_INTENT    = 3
EXIT_ABSTAIN   = 4
EXIT_SUSPICION = 5

# Hypotheses that mean "could not analyze / indeterminate" — these must map to
# ABSTAIN, NOT to benign. Convertir un error de extracción o una dependencia
# ausente en "NO EVIL" es el falso-negativo raíz del modo agente (ver
# AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md, P0-A). ABSTAIN es un veredicto
# válido y honesto; benigno afirma que se analizó y no había nada.
ABSTAIN_HYPOTHESES = frozenset({
    "PIPELINE_ERROR",
    "PIPELINE_UNAVAILABLE",
    "PIPELINE_INTERNAL_ERROR",
    "FORMAT_NOT_SUPPORTED",
    "BINARY_EVIDENCE_REQUIRES_SIFT_ORCHESTRATOR",
    "SYMLINK_REJECTED",
    "UNANALYZED_ARTIFACT",
    "UNANALYZED",
    "UNDETERMINED",
    "UNKNOWN",
    "",
    # AUDITORIA_PIPELINE_ROBUSTEZ (F1/F2):
    # REASONER_ERROR — el razonador abductivo crasheó; la extracción corrió
    #   pero no hay inferencia. Sin señales que lo overrideen (L-036), abstener.
    # ABSTAIN_V2 — el motor v2 abstuvo deliberadamente (veto duro, CCS<=1/2 o
    #   empate de hipótesis). Es un ABSTAIN razonado, nunca benigno.
    "REASONER_ERROR",
    "ABSTAIN_V2",
})


def _is_primary_signal(s: Any) -> bool:
    """
    F5 (AUDITORIA_PIPELINE_ROBUSTEZ, N4): una señal cuenta para los gates de
    corroboración solo si es PRIMARIA (proviene de un artefacto). Las señales
    DERIVADAS (motores engine: resonance/patterns/timeline/adv_robust) y los
    marcadores `unanalyzed` no son evidencia. Señales sin metadata se tratan
    como primarias (adaptadores del shim que no etiquetan).
    """
    meta = s.get("metadata") if isinstance(s, dict) else None
    if not isinstance(meta, dict):
        return True
    return meta.get("signal_class") != "derived" and not meta.get("unanalyzed")


def _accuracy_validation(signals: Any) -> bool:
    """
    F8 (N13, B-088): flag sans_compliance.accuracy_validation. Los adaptadores
    del shim (vol3, EBS-JSON, mobile) etiquetan la herramienta como `source`
    mientras los módulos SIFT nativos emiten `tool` — se aceptan ambos para no
    producir un falso negativo de compliance en bundles de camino adaptador.
    Fail-closed: sin señales, o cualquier señal sin herramienta o sin z_score,
    el flag es False.
    """
    return bool(
        signals
        and all(
            (s.get("tool") or s.get("source")) and s.get("z_score") is not None
            for s in signals
        )
    )


def _signal_stats(results: Dict[str, Any]) -> Tuple[int, int]:
    """
    Retorna (n_primary_signals, n_unanalyzed_artifacts) de un resultado de
    pipeline. Ambos alimentan classify_agent_verdict: el primero para el gate
    de corroboración <3, el segundo para degradar NOISE→ABSTAIN cuando hubo
    artefactos que no se pudieron analizar (F7).
    """
    signals = results.get("signals", []) or []
    n_primary = sum(1 for s in signals if _is_primary_signal(s))
    inner = results.get("results")
    unanalyzed = []
    if isinstance(inner, dict):
        unanalyzed = inner.get("unanalyzed_artifacts") or []
    return n_primary, len(unanalyzed)


def classify_agent_verdict(
    abduction: Dict[str, Any],
    n_signals: int,
    n_unanalyzed: int = 0,
) -> str:
    """
    Mapea el estado de la abducción a un veredicto de 4 valores:
    "MALICE" | "INTENT" | "ABSTAIN" | "NOISE".

    Reglas (en orden de precedencia):
      1. Hipótesis de malicia (MALICIOUS/CRITICAL/OVERRIDE) → MALICE.
      2. Hipótesis de intención (INTENT/SUSPICION)          → INTENT.
      3. No se pudo analizar (ABSTAIN_HYPOTHESES) o veredicto
         no-concluyente sin señales suficientes (<3)        → ABSTAIN.
      4. Analizado y limpio (NO_*_ANOMALY_DETECTED, BENIGN) → NOISE.
         F7: si además hubo artefactos NO analizados (n_unanalyzed>0),
         "limpio" no es afirmable sobre lo que no se procesó → ABSTAIN.

    F5: n_signals debe ser el conteo de señales PRIMARIAS (ver
    _is_primary_signal / _signal_stats) — las derivadas de motores engine
    inflaban el conteo y desactivaban el gate de corroboración.

    La regla 3 es la corrección central: antes, todo lo que no fuera malicia
    ni intención caía en NOISE (exit 0), incluidos errores de pipeline y
    ausencia de señal. Ahora esos casos abstienen.

    Semántica de is_conclusive (B-028, definida en Tanda B; ajustada por
    B-065):
      1. Modula el gate de corroboración de la regla 3 (<3 primarias sin
         conclusión firme → ABSTAIN).
      2. (B-065) Ya NO modula el piso del nivel de alerta: el piso se
         calcula sobre el veredicto final que retorna esta función (MALICE
         → HIGH/MEDIUM según posterior; INTENT → mínimo MEDIUM). El proxy
         is_conclusive+substring dejaba el piso muerto para evidencia
         distribuida no-concluyente.
      3. Es informativo para NOISE/SUSPICION.
      4. Incompatible con veredicto ABSTAIN (guard B-027 en _seal_bundle).
    """
    hyp = str(abduction.get("best_hypothesis") or "").upper()

    # §9.4-LIM (enforcement firmado 2026-07-10): techo de veredicto declarado
    # por el productor de la abducción (hoy: shim mobile-only cuando la
    # evidencia fuerte está TODA confinada al canal D3 — sin triangulación,
    # la multiplicidad de dominios lógicos no es corroboración independiente).
    # Solo CAPEA hacia abajo (MALICE/INTENT → SUSPICION); nunca eleva un
    # ABSTAIN/NOISE. Campo ausente o valor no reconocido → byte-idéntico al
    # comportamiento previo (fail-safe).
    _ceiling = str(abduction.get("verdict_ceiling") or "").upper()

    if "MALICIOUS" in hyp or "CRITICAL" in hyp or "OVERRIDE" in hyp:
        return "SUSPICION" if _ceiling == "SUSPICION" else "MALICE"
    if "INTENT" in hyp:
        return "SUSPICION" if _ceiling == "SUSPICION" else "INTENT"
    # B-097 (APLICADO 2026-07-10, firma Anna — supersede el NO APLICADO del
    # gate del día anterior): una hipótesis SUSPICION sella SUSPICION — ya NO
    # se sube a INTENT. El colapso histórico existía porque SUSPICION no era
    # un veredicto sellado; desde §9.4-LIM lo es (exit propio, piso de alerta
    # MEDIUM). Validado por triple fuente independiente sobre los 33 casos
    # afectados: (1) etiqueta ground-truth = SUSPICION en los 30 recuperados;
    # (2) banda interna del motor (0.10<score<=0.33 = SUSPICION, B-076) — el
    # motor calculaba bien, solo el sellado colapsaba; (3) batch ciego Claude
    # Code + Cronos (46 casos, 2026-07-10) confirma SUSPICION. Label-blind
    # (B-075/B-076): mueve TODOS los casos con hipótesis SUSPICION, coincidan
    # o no con su expected_verdict (gate medido: 30 recuperados, 3 expuestos
    # — los 3 pasaban por accidente del colapso; ver B-097 en BUGS_PENDIENTES).
    if "SUSPICION" in hyp:
        return "SUSPICION"
    # B-058 FIX (auditoría de invariantes 2026-07-03): match por SUBSTRING,
    # no solo exacto. El adaptador EBS emite "ABSTAIN_DETECTED" (expected==
    # ABSTAIN), que NO estaba en ABSTAIN_HYPOTHESES → caía a NOISE (exit 0):
    # un caso que el sistema etiqueta explícitamente ABSTAIN se sellaba como
    # benigno (misma familia P0-A). El batch comparator de run_all_agent.py
    # lo enmascaraba con su propio mapeo ABSTAIN_DETECTED→ABSTAIN, dando PASS
    # sobre un bundle con agent_verdict=NOISE. Ahora "ABSTAIN" en cualquier
    # posición de la hipótesis clasifica ABSTAIN.
    if "ABSTAIN" in hyp or hyp in ABSTAIN_HYPOTHESES:
        return "ABSTAIN"
    # Veredicto que se presenta como "limpio" pero se apoya en muy pocas
    # señales: el reasoner no tuvo base suficiente para afirmar benignidad.
    # <3 señales es el gate del propio AbductiveReasoner — sin base, abstener.
    if n_signals < 3 and not abduction.get("is_conclusive", False):
        return "ABSTAIN"
    # F7 (N8): "analizado y limpio" con artefactos sin analizar no es NOISE —
    # 0 hallazgos sobre evidencia no procesada no es evidencia de benignidad.
    if n_unanalyzed > 0:
        return "ABSTAIN"
    return "NOISE"


_VERDICT_EXIT = {
    "MALICE":  EXIT_MALICE,
    "INTENT":  EXIT_INTENT,
    # B-097: SUSPICION es veredicto de primera clase con exit PROPIO (5).
    # Sin entrada explícita caería al fallback EXIT_ABSTAIN (4).
    "SUSPICION": EXIT_SUSPICION,
    "ABSTAIN": EXIT_ABSTAIN,
    "NOISE":   EXIT_NOISE,
}
_VERDICT_LABEL = {
    "MALICE":  "EVIL FOUND",
    "INTENT":  "INTENT DETECTED",
    # B-097: alcanzable por el path motor (banda 0.10<score<=0.33 o gate de
    # corroboración) y por el techo §9.4-LIM (D3-only sin triangulación).
    "SUSPICION": "SUSPICION DETECTED (structural anomaly — no corroboration "
                 "for INTENT/MALICE)",
    "ABSTAIN": "ABSTAIN — could not determine (insufficient/unanalyzed evidence)",
    "NOISE":   "NO EVIL DETECTED",
}


# ── Rational conversion helpers ──────────────────────────────────────────────

def _to_frac(value: Any) -> Fraction:
    """
    Converts any numeric type to Fraction safely and deterministically.
    Never uses float as final result. Raises TypeError for unhandled types.

    Precision note: for float, uses Fraction(str(value)) which converts the
    exact decimal representation of the float, avoiding truncation errors
    of methods like int(value * 1_000_000). For exact base-2 representation,
    Fraction.from_float() would work — but it generates enormous denominators that
    degrade rational performance. str() is the correct balance for VIGÍA.
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        # Use str() to avoid binary float imprecision
        # Fraction("0.1") == Fraction(1, 10) exact; int(0.1 * 1e6) is not
        # FIX P2-9: explicitly reject NaN and infinities — corrupt data
        if value != value or value == float('inf') or value == float('-inf'):
            return Fraction(0, 1)
        try:
            return Fraction(str(value))
        except (ValueError, OverflowError):
            return Fraction(0, 1)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return Fraction(0, 1)
        # Explicitly reject NaN and infinities — corrupt data
        if stripped.lower() in ("nan", "inf", "-inf", "+inf", "infinity", "-infinity"):
            return Fraction(0, 1)
        try:
            return Fraction(stripped)
        except (ValueError, ZeroDivisionError):
            try:
                return Fraction(str(float(stripped)))
            except (ValueError, OverflowError):
                return Fraction(0, 1)
    if value is None:
        return Fraction(0, 1)
    raise TypeError(f"_to_frac: tipo no convertible a Fraction: {type(value)!r} — {value!r}")


def _json_serial(obj: Any) -> Any:
    """
    Canonical JSON serialization for forensic bundles.
    Raises explicit TypeError for unknown types — no str() parachute.
    """
    if isinstance(obj, Fraction):
        return {"__fraction__": True, "num": obj.numerator, "den": obj.denominator}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        # B-105: CAIE computes internally with Decimal; two Fracture
        # constructors leaked it into the sealed results and the whole case
        # died at serialization (a wall-clock time bomb: the offending
        # fracture only fires once evidence trust decays past a threshold).
        # The type-contract fix lives in caie.py; this boundary keeps a
        # future leak from destroying otherwise-valid work (honest
        # degradation, warned at the boundary) while preserving exactness:
        # Fraction(Decimal) is exact.
        logging.getLogger(__name__).warning(
            "[_json_serial] Decimal reached the sealed payload (%s) — "
            "type-contract violation upstream (B-105); encoding exactly "
            "as Fraction.", obj,
        )
        _f = Fraction(obj)
        return {"__fraction__": True, "num": _f.numerator, "den": _f.denominator}
    raise TypeError(f"Tipo no serializable: {type(obj)!r} — {obj!r}")


def _utc_iso_timestamp() -> str:
    """Returns UTC timestamp in ISO 8601 format for audit trail."""
    return datetime.now(timezone.utc).isoformat()




# ════════════════════════════════════════════════════════════════════════════
# AUDIT TRAIL
# ════════════════════════════════════════════════════════════════════════════

class AgentAuditTrail:
    """
    Immutable record of all agent actions.
    Each entry has ISO 8601 timestamp, action, inputs, outputs and SHA-256.
    Auditors can trace any finding back to the tool that produced it.
    """

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.entries: List[Dict[str, Any]] = []
        self.start_time = _utcnow()

    def log(
        self,
        action: str,
        tool: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        iteration: int = 0,
        note: str = "",
    ) -> str:
        """Records an action. Returns the SHA-256 of the entry."""
        entry = {
            "seq": len(self.entries) + 1,
            "timestamp": _utcnow(),
            "case_id": self.case_id,
            "iteration": iteration,
            "action": action,
            "tool": tool,
            "inputs_summary": _summarize(inputs),
            "outputs_summary": _summarize(outputs),
            "note": note,
        }
        # SHA-256 of the entry for integrity
        entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=True).encode()
        entry["entry_sha256"] = hashlib.sha256(entry_bytes).hexdigest()
        self.entries.append(entry)
        logger.info("[%s] iter=%d tool=%s — %s", action, iteration, tool, note or "OK")
        return entry["entry_sha256"]

    def log_contradiction(
        self,
        modules: List[str],
        description: str,
        iteration: int,
    ) -> None:
        """Explicitly records a contradiction detected between modules."""
        self.log(
            action="SELF_CORRECTION_TRIGGERED",
            tool="contradiction_detector",
            inputs={"modules_in_conflict": modules},
            outputs={"description": description},
            iteration=iteration,
            note=f"CONTRADICTION DETECTED: {description}. Re-analysis scheduled.",
        )
        logger.warning(
            "[SELF-CORRECTION] Contradiction between %s: %s", modules, description
        )

    def log_correction(
        self,
        correction_applied: str,
        before: str,
        after: str,
        iteration: int,
    ) -> None:
        """Records the applied correction and verdict change."""
        self.log(
            action="SELF_CORRECTION_APPLIED",
            tool="correction_engine",
            inputs={"before": before},
            outputs={"after": after, "correction": correction_applied},
            iteration=iteration,
            note=f"Verdict adjusted: {before} → {after}",
        )
        logger.info("[SELF-CORRECTION] Applied: %s → %s", before, after)

    def export(self) -> Dict[str, Any]:
        """Exports the full audit trail."""
        return {
            "case_id": self.case_id,
            "agent_version": AGENT_VERSION,
            "start_time": self.start_time,
            "end_time": _utcnow(),
            "total_entries": len(self.entries),
            "entries": self.entries,
        }


# ════════════════════════════════════════════════════════════════════════════
# CONTRADICTION DETECTOR
# Architectural guardrail — not prompt-based
# ════════════════════════════════════════════════════════════════════════════

class ContradictionDetector:
    """
    Detects semantic contradictions between pipeline modules.

    Detected contradiction types:
    1. TEMPORAL_VS_CONTENT: timestamp inconsistent with artifact content
    2. ENTROPY_VS_BEHAVIORAL: high entropy + normal behavior (false negative)
    3. SEMIOTIC_VS_TECHNICAL: no linguistic patterns + high technical anomaly
    4. CONFIDENCE_COLLAPSE: high MCP but all individual modules low
    5. VERDICT_FLIP: opposing verdicts between equal-confidence engines
    """

    def detect(
        self,
        module_results: Dict[str, Any],
        mca_score: Fraction,
    ) -> List[Tuple[List[str], str]]:
        """
        Returns list of (conflicting_modules, description).
        Empty list = no contradictions.
        """
        contradictions = []

        abduction = module_results.get("abduction", {})
        signals = module_results.get("signals", [])
        semiotic = module_results.get("semiotic_result", {})
        technical = module_results.get("technical_result", {})

        # 1. ENTROPY_VS_BEHAVIORAL
        # High artifact entropy + normal temporal behavior
        high_entropy_signals = [
            s for s in signals
            if s.get("tool") in ("memory_forensics", "disk_forensics")
            and abs(_to_frac(s.get("z_score", 0))) > Fraction(5, 2)
        ]
        behavioral_signals = [
            s for s in signals
            if s.get("tool") == "behavioral_fingerprint"
            and abs(_to_frac(s.get("z_score", 0))) < Fraction(1, 2)
        ]
        if high_entropy_signals and behavioral_signals:
            contradictions.append((
                ["memory/disk_forensics", "behavioral_fingerprint"],
                f"High technical anomaly (z>{high_entropy_signals[0].get('z_score', 0):.2f}) "
                f"with normal behavior (z<0.5). Possible behavioral detection evasion."
            ))

        # 2. SEMIOTIC_VS_TECHNICAL
        sem_verdict = semiotic.get("verdict", "NO_SEMIOTIC_ANOMALY_DETECTED")
        tech_alert = technical.get("alert_level", "LOW")
        if sem_verdict == "NO_SEMIOTIC_ANOMALY_DETECTED" and tech_alert in ("HIGH", "CRITICAL"):
            contradictions.append((
                ["semiotic_detector", "technical_detector"],
                f"No adversarial semiotic patterns but technical alert {tech_alert}. "
                f"Possible technical payload without known linguistic signature."
            ))

        # 3. CONFIDENCE_COLLAPSE
        # High MCA score but all individual modules low
        if mca_score > Fraction(6, 10):
            low_confidence_signals = [
                s for s in signals if _to_frac(s.get("confidence", Fraction(1, 1))) < Fraction(3, 10)
            ]
            if len(signals) > 0 and Fraction(len(low_confidence_signals), len(signals)) > Fraction(7, 10):
                contradictions.append((
                    ["mcp_aggregator", "individual_modules"],
                    f"MCA score high ({mca_score.numerator}/{mca_score.denominator}) but "
                    f"{len(low_confidence_signals)}/{len(signals)} modules with confidence < 3/10. "
                    f"Review aggregation weights."
                ))

        # 4. VERDICT_FLIP between abductive reasoning and direct signals
        abductive_verdict = abduction.get("best_hypothesis", "")
        is_conclusive = abduction.get("is_conclusive", False)
        critical_signals = [
            s for s in signals
            if abs(_to_frac(s.get("z_score", 0))) > Fraction(3, 1)
        ]
        if (
            is_conclusive
            and "BENIGN" in abductive_verdict.upper()
            and len(critical_signals) >= 2
        ):
            contradictions.append((
                ["abductive_reasoner", "sift_signals"],
                f"Razonamiento abductivo concluye BENIGN pero hay "
                f"{len(critical_signals)} signals with z_score > 3.0. "
                f"Review abductive hypothesis."
            ))

        return contradictions


# ════════════════════════════════════════════════════════════════════════════
# CORRECTION ENGINE
# Applies deterministic adjustments when contradictions are detected
# ════════════════════════════════════════════════════════════════════════════

class CorrectionEngine:
    """
    Applies deterministic corrections to results when contradictions are detected.
    No ML. No floats in scoring. No prompt-based heuristics.
    """

    def apply(
        self,
        contradiction_type: str,
        modules: List[str],
        original_results: Dict[str, Any],
        iteration: int,
    ) -> Dict[str, Any]:
        """
        Returns a dict with applied corrections and suggested new verdict.
        """
        corrections = {
            "contradiction_type": contradiction_type,
            "modules_adjusted": modules,
            "iteration": iteration,
            "adjustments": [],
            "suggested_verdict_upgrade": False,
        }

        # Correction 1: ENTROPY_VS_BEHAVIORAL
        # High technical entropy but normal behavior —
        # elevate technical signal weight and flag for human review
        if "memory/disk_forensics" in modules or "disk_forensics" in modules:
            corrections["adjustments"].append(
                "Memory/disk signals elevated to 1.5x weight. "
                "Behavioral evasion documented as known attack vector."
            )
            corrections["suggested_verdict_upgrade"] = True
            corrections["recommended_action"] = "REQUIRE_HUMAN_REVIEW"

        # Correction 2: SEMIOTIC_VS_TECHNICAL
        # No linguistic signature + high technical anomaly = advanced operator
        if "semiotic_detector" in modules and "technical_detector" in modules:
            corrections["adjustments"].append(
                "Absence of semiotic patterns recorded as positive indicator "
                "of advanced technical operator (APT). Technical alert preserved without downgrade."
            )
            corrections["recommended_action"] = "ESCALATE_TO_CRITICAL"

        # Correction 3: CONFIDENCE_COLLAPSE
        if "mcp_aggregator" in modules:
            corrections["adjustments"].append(
                "MCP recalculated with uniform per-module weight "
                "(no amplification by individual confidence)."
            )
            corrections["recommended_action"] = "REWEIGHT_AND_RERUN"

        # Correction 4: VERDICT_FLIP
        if "abductive_reasoner" in modules:
            corrections["adjustments"].append(
                "Abductive hypothesis BENIGN overridden. "
                "High-magnitude direct signals take precedence over "
                "abductive inference when z_score > 3.0 across multiple sources."
            )
            corrections["suggested_verdict_upgrade"] = True
            corrections["recommended_action"] = "OVERRIDE_ABDUCTIVE_CONCLUSION"

        return corrections


# ════════════════════════════════════════════════════════════════════════════
# VIGIA AGENT — Main loop
# ════════════════════════════════════════════════════════════════════════════

class VIGIAAgent:
    """
    Autonomous VIGÍA forensic agent.

    Execution loop:
    1. Initialize case and chain of custody
    2. Compute SHA-256 of evidence (integrity)
    3. Execute full VIGÍA pipeline
    4. Detect contradictions between modules
    5. If contradictions found: apply corrections, repeat from 3 (max MAX_ITERATIONS)
    6. Generate investigative narrative
    7. Export sealed bundle with SHA-256

    Self-correction is architectural:
    - ContradictionDetector operates on rational scores, not on text
    - CorrectionEngine applies documented deterministic adjustments
    - Each iteration is recorded in the audit trail with timestamp
    """

    def __init__(self, case_id: str, evidence_path: str,
                 acquisition_overrides: Optional[Dict[str, Any]] = None):
        self.case_id = case_id
        self.evidence_path = Path(evidence_path)
        self.audit = AgentAuditTrail(case_id)
        self.contradiction_detector = ContradictionDetector()
        self.correction_engine = CorrectionEngine()
        self.iteration = 0
        self.corrections_applied: List[Dict] = []
        # L-037: examiner-declared acquisition metadata for CAIE trust gates.
        self.acquisition_overrides: Dict[str, Any] = acquisition_overrides or {}

    def _hash_evidence(self) -> str:
        """SHA-256 of the evidence. Guarantees integrity — no analysis modifies the original."""
        self.audit.log(
            action="EVIDENCE_INTEGRITY_CHECK",
            tool="sha256_hasher",
            inputs={"path": str(self.evidence_path)},
            outputs={},
            iteration=0,
            note="Computing SHA-256 of original evidence",
        )
        h = hashlib.sha256()
        try:
            # SECURITY: reject symlinks — prevents arbitrary file reads from the system
            if self.evidence_path.is_symlink():
                raise ValueError(
                    f"[SECURITY] Evidence path is symlink — rejected: {self.evidence_path}"
                )
            with open(self.evidence_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            digest = h.hexdigest()
        except PermissionError as e:
            # FIX P0-1: permission-denied file — abort instead of returning empty hash
            logger.error("[INTEGRITY] Permission denied reading evidence: %s", self.evidence_path)
            raise RuntimeError(
                f"Evidence file not readable (permissions): {self.evidence_path}"
            ) from e
        except OSError:
            # Directory or other IO error — hash actual content of each file (Merkle-like)
            h_dir = hashlib.sha256()
            if self.evidence_path.is_dir():
                for f in sorted(self.evidence_path.rglob("*")):
                    # SECURITY: skip symlinks — prevents path traversal and FIFO DoS
                    if f.is_symlink():
                        logger.warning("[INTEGRITY] Symlink ignored: %s", f)
                        continue
                    if f.is_file():
                        try:
                            h_file = hashlib.sha256()
                            with open(f, "rb") as fh:
                                for chunk in iter(lambda: fh.read(65536), b""):
                                    h_file.update(chunk)
                            # Incluir ruta relativa + hash del contenido
                            h_dir.update(str(f.relative_to(self.evidence_path)).encode())
                            h_dir.update(h_file.digest())
                        except (OSError, PermissionError) as e:
                            # FIX P0-2: unreadable file in directory — abort instead of
                            # hashing the path (tamper-invisible if only the name is hashed)
                            logger.error(
                                "[INTEGRITY] Cannot read file in evidence dir: %s — %s", f, e
                            )
                            raise RuntimeError(
                                f"Evidence directory contains unreadable file: {f}"
                            ) from e
            digest = h_dir.hexdigest()

        self.audit.log(
            action="EVIDENCE_INTEGRITY_CHECK",
            tool="sha256_hasher",
            inputs={"path": str(self.evidence_path)},
            outputs={"sha256": digest},
            iteration=0,
            note=f"Evidence verified: {digest[:16]}...",
        )
        logger.info("[INTEGRITY] Evidence SHA-256: %s", digest)
        return digest

    def _run_pipeline(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executes the VIGÍA pipeline.
        params allows adjusting weights in correction iterations.
        """
        params = params or {}

        # FIX P2-6: avoid repeated sys.path.insert on each iteration
        parent_path = str(Path(__file__).parent)
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)

        self.audit.log(
            action="PIPELINE_EXECUTE",
            tool="vigia_pipeline",
            inputs={
                "evidence": str(self.evidence_path),
                "iteration": self.iteration,
                "params": params,
            },
            outputs={},
            iteration=self.iteration,
            note=f"Executing pipeline — iteration {self.iteration}",
        )

        try:
            # Try to import the real orchestrator
            # sys.path already adjusted with guard at start of _run_pipeline (FIX P2-6)
            from sift_orchestrator import SIFTOrchestrator
            orchestrator = SIFTOrchestrator(self.case_id)

            # L-037: propagate examiner-declared acquisition metadata to orchestrator.
            if self.acquisition_overrides:
                orchestrator.acquisition_overrides = self.acquisition_overrides

            # Build inputs based on evidence type
            kwargs = _build_orchestrator_kwargs(self.evidence_path, params)
            result = orchestrator.analyze(**kwargs)

        except ImportError:
            # Fallback: use text pipeline if orchestrator is unavailable
            logger.warning("[PIPELINE] SIFTOrchestrator unavailable, using text pipeline")
            result = _run_text_pipeline(self.evidence_path, self.case_id, params)
        except (MemoryError, RecursionError, KeyboardInterrupt, SystemExit):
            # Critical system errors — do NOT mask, propagate
            raise
        except (OSError, ValueError, KeyError, ZeroDivisionError) as e:
            # FIX P1-3: only catch expected operational errors — IO, malformed data,
            # broken schema, division by zero in data.
            # TypeError, AttributeError, RuntimeError, ArithmeticError are NOT caught —
            # they are code bugs and must propagate to be visible.
            logger.error("[PIPELINE] Pipeline operational error: %s", e)
            result = {
                "case_id": self.case_id,
                "error": str(e),
                "signals": [],
                "abduction": {"best_hypothesis": "PIPELINE_ERROR", "is_conclusive": False},
                "pipeline_meta": {"error": str(e), "error_type": type(e).__name__},
            }

        self.audit.log(
            action="PIPELINE_COMPLETE",
            tool="vigia_pipeline",
            inputs={"iteration": self.iteration},
            outputs=_summarize(result),
            iteration=self.iteration,
            note=f"Pipeline completed — {len(result.get('signals', []))} signals",
        )
        return result

    def _detect_and_correct(self, results: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Detects contradictions and applies corrections.
        Returns (had_corrections, updated_results).
        """
        # Rational multiplicative MCP — product of modular confidences
        # If no confidence in signals, use normalized z_score as proxy
        signals = results.get("signals", [])
        if signals:
            # MCA: Rational Arithmetic Confidence Mean
            # Multiplicative product penalizes modularity (n modules × conf 0.9 → 0).
            # Arithmetic mean is stable: 20 signals with conf 9/10 → MCA = 9/10.
            confidences = []
            for s in signals:
                raw = s.get("confidence", None)
                if raw is not None:
                    confidences.append(_to_frac(raw))
            if confidences:
                n = Fraction(len(confidences), 1)
                mca_score = min(
                    Fraction(1, 1),
                    max(Fraction(0, 1),
                        sum((max(Fraction(0, 1), min(Fraction(1, 1), c)) for c in confidences),
                            Fraction(0, 1)) / n)
                )
            else:
                # Fallback: arithmetic mean of normalized z_scores — use _to_frac
                z_fracs = [
                    min(Fraction(1, 1), abs(_to_frac(s.get("z_score", 0))) / Fraction(10, 1))
                    for s in signals
                ]
                n = Fraction(len(z_fracs), 1)
                mca_score = sum(z_fracs, Fraction(0, 1)) / n if n > 0 else Fraction(0, 1)
        else:
            mca_score = Fraction(0, 1)

        contradictions = self.contradiction_detector.detect(results, mca_score)

        # Apply CONTRADICTION_THRESHOLD — only trigger correction if enough contradictions
        if len(contradictions) < CONTRADICTION_THRESHOLD:
            self.audit.log(
                action="CONTRADICTION_CHECK",
                tool="contradiction_detector",
                inputs={"n_signals": len(results.get("signals", []))},
                outputs={"contradictions_found": len(contradictions), "threshold": str(CONTRADICTION_THRESHOLD)},
                iteration=self.iteration,
                note=f"{len(contradictions)} contradiction(s) — below threshold {CONTRADICTION_THRESHOLD}, no correction",
            )
            return False, results

        # Sufficient contradictions found — log and correct
        for modules, description in contradictions:
            self.audit.log_contradiction(modules, description, self.iteration)

        # Apply corrections
        all_corrections = []
        params_for_rerun = {}

        for modules, description in contradictions:
            correction = self.correction_engine.apply(
                contradiction_type=description,
                modules=modules,
                original_results=results,
                iteration=self.iteration,
            )
            all_corrections.append(correction)

            # Translate correction to parameters for the next iteration
            if correction.get("recommended_action") == "REWEIGHT_AND_RERUN":
                params_for_rerun["uniform_weights"] = True
            if correction.get("suggested_verdict_upgrade"):
                params_for_rerun["elevate_technical_signals"] = True

        self.corrections_applied.extend(all_corrections)

        # Apply corrections to current result — mutate verdict if appropriate
        abduction = results.get("abduction", {})
        before_verdict = abduction.get("best_hypothesis", "UNKNOWN")
        after_verdict = before_verdict

        for correction in all_corrections:
            action = correction.get("recommended_action", "")
            if action == "OVERRIDE_ABDUCTIVE_CONCLUSION":
                after_verdict = f"MALICIOUS_INTENT_SUSPECTED [OVERRIDE: {before_verdict}]"
                if "abduction" in results:
                    results["abduction"]["best_hypothesis"] = after_verdict
                    results["abduction"]["override_applied"] = True
                    results["abduction"]["override_reason"] = correction.get("contradiction_type", "")
            elif action == "ESCALATE_TO_CRITICAL":
                if "abduction" in results:
                    results["abduction"]["alert_escalated"] = True
                    results["abduction"]["escalation_reason"] = "Technical anomaly without semiotic signature — advanced operator pattern"

        # Apply CONFIDENCE_FLOOR — if MCA is below floor, mark as INCONCLUSIVE
        if mca_score < CONFIDENCE_FLOOR and after_verdict == before_verdict:
            if "abduction" in results:
                results["abduction"]["best_hypothesis"] = (
                    f"INCONCLUSIVE [MCA={mca_score.numerator}/{mca_score.denominator}"
                    f" < FLOOR={CONFIDENCE_FLOOR.numerator}/{CONFIDENCE_FLOOR.denominator}]"
                )
                results["abduction"]["confidence_floor_applied"] = True

        results["self_corrections"] = all_corrections
        results["corrections_iteration"] = self.iteration
        results["params_for_rerun"] = params_for_rerun

        # Log applied correction with real before/after
        after_note = " + ".join(
            c.get("recommended_action", "") for c in all_corrections if c.get("recommended_action")
        )
        self.audit.log_correction(
            correction_applied=after_note or "ADJUSTMENTS_APPLIED",
            before=before_verdict,
            after=after_verdict,
            iteration=self.iteration,
        )

        return True, results

    def _generate_narrative(self, results: Dict[str, Any], evidence_sha256: str) -> str:
        """
        Generates 100% deterministic investigative narrative.
        No LLMs — all derived from pipeline data.
        Each section references the modules that produced it.

        AUDITORIA_PIPELINE_ROBUSTEZ:
        - F3 (N10): el override L-036 se aplica ANTES de serializar cualquier
          sección — la narrativa y el veredicto sellado no pueden divergir.
        - F4: la sección Peircean se construye desde datos que SIEMPRE existen
          (inventario de señales, anomalías vs umbral, estado de motores); la
          narrativa del reasoner es una capa adicional, no la única fuente.
        - F5 (N4): alerta y override cuentan SOLO señales primarias.
        - F7 (N8): los artefactos no analizados tienen sección propia.
        """
        abduction = results.get("abduction", {})
        signals = results.get("signals", [])
        corrections = results.get("self_corrections", [])
        inner = results.get("results") if isinstance(results.get("results"), dict) else {}

        def _to_frac_z(s: dict) -> Fraction:
            """Local helper — delegates to _to_frac for consistency with the rest of the agent."""
            return abs(_to_frac(s.get("z_score", 0)))

        def _label_of(s: dict) -> str:
            return str(s.get('description') or s.get('source')
                       or s.get('tool') or '?')

        primary = [s for s in signals if _is_primary_signal(s)]
        derived = [s for s in signals if not _is_primary_signal(s)]
        n_critical = sum(1 for s in primary if _to_frac_z(s) > Fraction(3, 1))
        n_high = sum(1 for s in primary if Fraction(2, 1) < _to_frac_z(s) <= Fraction(3, 1))

        # ------------------------------------------------------------------
        # F3: Signal-based hypothesis override (L-036) — PRIMERO, antes de
        # serializar. Cuando el orquestador retorna UNDETERMINED (o el
        # reasoner falló: REASONER_ERROR) pero hay señales PRIMARIAS z>3,
        # la abducción se eleva determinísticamente — sin LLM. Las señales
        # derivadas (meta-indicadores como ADV_ROBUST) no pueden fabricar
        # un veredicto por sí solas (N4). Un ABSTAIN_V2 deliberado del motor
        # v2 NO se overridea: la abstención razonada tiene precedencia.
        # ------------------------------------------------------------------
        override_note = ""
        _hyp_pre = abduction.get("best_hypothesis", "")
        if _hyp_pre in ("", "UNDETERMINED", "UNKNOWN", "REASONER_ERROR", None):
            _new_hyp = None
            if n_critical >= 2:
                _new_hyp = "MALICIOUS_INTENT_DETECTED"
                abduction["is_conclusive"] = True
                abduction["best_posterior"] = str(Fraction(n_critical, max(len(primary), 1)))
                abduction["override_source"] = "signal_count_z>3"
            elif n_critical >= 1:
                _new_hyp = "INTENT_DETECTED"
                abduction["is_conclusive"] = True
                abduction["best_posterior"] = str(Fraction(n_critical, max(len(primary), 1)))
                abduction["override_source"] = "signal_count_z>3"
            elif n_high >= 2:
                _new_hyp = "SUSPICION_DETECTED"
                abduction["is_conclusive"] = False
                abduction["best_posterior"] = str(Fraction(n_high, max(len(primary), 1)))
                abduction["override_source"] = "signal_count_z>2"
            if _new_hyp:
                abduction["best_hypothesis"] = _new_hyp
                abduction["override_of"] = _hyp_pre or "EMPTY"
                override_note = (
                    f"[OVERRIDE L-036 sobre {_hyp_pre or 'EMPTY'}: "
                    f"{n_critical} señal(es) primaria(s) z>3, "
                    f"{n_high} con 2<z<=3]"
                )
                abduction["override_note"] = override_note

        narrative_parts = [
            f"=== VIGÍA FORENSIC AGENT — CASE {self.case_id} ===",
            f"Evidence: {self.evidence_path}",
            f"Evidence SHA-256: {evidence_sha256}",
            f"Analysis iterations: {self.iteration + 1}",
            f"Self-corrections applied: {len(corrections)}",
            "",
            "--- MAIN HYPOTHESIS ---",
            f"Hypothesis: {abduction.get('best_hypothesis', 'UNDETERMINED')}"
            + (f" {override_note}" if override_note else ""),
            f"Posterior confidence: {abduction.get('best_posterior', '0')}",
            f"Conclusive: {'YES' if abduction.get('is_conclusive') else 'NO — requires human review'}",
            "",
        ]

        # ------------------------------------------------------------------
        # F4: PEIRCEAN NARRATIVE — capas deterministas construidas desde las
        # señales (siempre presentes), más la narrativa del reasoner si existe.
        # ------------------------------------------------------------------
        narrative_parts.append("--- PEIRCEAN NARRATIVE ---")

        # FIRSTNESS — inventario fenomenológico: qué se observó.
        def _artifact_type_of(s: dict) -> str:
            meta = s.get("metadata")
            at = meta.get("artifact_type") if isinstance(meta, dict) else None
            return str(at or s.get("tool") or s.get("source") or "?")

        _types = sorted({_artifact_type_of(s) for s in primary}) if primary else []
        firstness = (
            f"[FIRSTNESS] {len(signals)} señal(es): {len(primary)} primaria(s)"
            + (f" de {_types}" if _types else "")
            + f", {len(derived)} derivada(s)/no-analizada(s)."
        )
        if signals:
            _top3 = sorted(signals, key=_to_frac_z, reverse=True)[:3]
            firstness += " Top z: " + ", ".join(
                f"{_label_of(s)[:40]}={float(_to_frac_z(s)):.2f}" for s in _top3
            ) + "."
        narrative_parts.append(firstness)

        # SECONDNESS — contraste contra baseline: qué desvía y cuánto.
        _anomalous = [s for s in primary if _to_frac_z(s) > Fraction(2, 1)]
        if _anomalous:
            secondness = (
                f"[SECONDNESS] {len(_anomalous)} señal(es) primaria(s) sobre "
                f"umbral z>2: " + "; ".join(
                    f"{_label_of(s)[:50]} (z={float(_to_frac_z(s)):.2f})"
                    for s in _anomalous[:5]
                ) + "."
            )
        else:
            secondness = (
                "[SECONDNESS] Ninguna señal primaria supera z>2 — sin "
                "desviación estructural contra baseline en esta iteración."
            )
        _caie_summary = inner.get("caie", {}) if isinstance(inner, dict) else {}
        if _caie_summary:
            _caie_status = _caie_summary.get("status", "OK" if _caie_summary.get("verdict") else "?")
            if _caie_summary.get("verdict"):
                secondness += (
                    f" CAIE: {_caie_summary.get('verdict')} "
                    f"({_caie_summary.get('fractures_detected', 0)} fractura(s))."
                )
            elif _caie_summary.get("source") == "motor_live_caie":
                # B-094: la CAIE viva del scorer no produce un verdict CAIE
                # separado, pero SUS fracturas movieron el veredicto — la
                # SECONDNESS debe decirlo, no afirmar "sin desviación".
                _nf = _caie_summary.get("fractures_detected", 0)
                _fb = _caie_summary.get("fracture_malice_boost", "0")
                secondness += (
                    f" CAIE (viva): {_nf} fractura(s) cross-artefacto "
                    f"contribuyeron al veredicto (boost +{_fb})."
                )
            elif _caie_status == "ERROR":
                secondness += " CAIE: ERROR — correlación cross-artefacto no disponible."
        narrative_parts.append(secondness)

        # THIRDNESS — la ley inferida: hipótesis y cómo se llegó a ella.
        thirdness = (
            f"[THIRDNESS] Hipótesis: {abduction.get('best_hypothesis', 'UNDETERMINED')}. "
            f"Conclusiva: {'sí' if abduction.get('is_conclusive') else 'no — requiere revisión humana'}."
        )
        if override_note:
            thirdness += f" {override_note}"
        if abduction.get("reasoner_error"):
            thirdness += f" Razonador abductivo falló: {abduction['reasoner_error']}."
        narrative_parts.append(thirdness)

        # Capa del reasoner (motor v2 / adaptadores) — verbatim, si existe.
        _reasoner_narr = abduction.get("narrative")
        if _reasoner_narr:
            narrative_parts.append("")
            narrative_parts.append("Razonamiento del motor abductivo:")
            narrative_parts.append(str(_reasoner_narr))
        narrative_parts.append("")

        if signals:
            top_signals = sorted(signals, key=_to_frac_z, reverse=True)[:5]
            narrative_parts.append("--- TOP SIGNALS (top 5 by z-score) ---")
            for s in top_signals:
                z_frac = _to_frac_z(s)
                conf_frac = _to_frac(s.get("confidence", 0))
                _label = _label_of(s)
                _detail = s.get('detail') or s.get('value') or ''
                _class_tag = "" if _is_primary_signal(s) else " [DERIVED]"
                narrative_parts.append(
                    f"  [{_label[:70]}]{_class_tag} z={float(z_frac):.3f} "
                    f"conf={float(conf_frac):.2f} — {str(_detail)[:80]}"
                )
            narrative_parts.append("")

        if corrections:
            narrative_parts.append("--- SELF-CORRECTIONS APPLIED ---")
            for i, c in enumerate(corrections, 1):
                narrative_parts.append(f"  Correction {i}: {str(c.get('contradiction_type', ''))[:80]}")
                for adj in c.get("adjustments", []):
                    narrative_parts.append(f"    → {adj}")
            narrative_parts.append("")

        # B-041: Surface CAIE results in narrative.
        # CAIE runs inside sift_orchestrator.run_full_analysis() and stores
        # its output in results["results"]["caie"].  Until this fix, the
        # agent never read it — fractures were computed but invisible.
        caie = inner.get("caie", {}) if isinstance(inner, dict) else {}
        if caie and caie.get("status") == "OK" and caie.get("source") == "motor_live_caie":
            # B-094: CAIE viva del scorer (path motor). Fiel: reporta fracturas
            # + boost, sin fabricar structural_verdict/composite que el scorer
            # no computó por separado.
            narrative_parts.append("--- CAIE (Cross-Artifact Incongruence Engine — motor) ---")
            narrative_parts.append(
                f"  Fractures: {caie.get('fractures_detected', 0)} "
                f"| Malice boost aplicado: +{caie.get('fracture_malice_boost', '0')}"
            )
            for f in caie.get("fractures", []):
                _ftype = f.get("type", "?")
                _sev = f.get("severity", "?")
                _interp = str(f.get("interpretation", ""))[:120]
                _ttp = f.get("ttp_id", "")
                _ttp_tag = f" [{_ttp}]" if _ttp else ""
                narrative_parts.append(
                    f"  Fracture: {_ftype} severity={_sev}{_ttp_tag} — {_interp}"
                )
            if caie.get("daubert_note"):
                narrative_parts.append(f"  {caie['daubert_note'][:200]}")
            narrative_parts.append("")
        elif caie and caie.get("status") == "OK":
            n_fractures = caie.get("fractures_detected", 0)
            caie_verdict = caie.get("verdict", "NOISE")
            composite = caie.get("composite_score", "0")
            structural = caie.get("structural_verdict", "NOISE")
            golden = caie.get("golden_rules_triggered", 0)
            narrative_parts.append("--- CAIE (Cross-Artifact Incongruence Engine) ---")
            narrative_parts.append(
                f"  Verdict: {caie_verdict} | Structural: {structural} "
                f"| Composite: {composite} | Fractures: {n_fractures} "
                f"| Golden Rules: {golden}"
            )
            for f in caie.get("fractures", []):
                _ftype = f.get("type", "?")
                _sev = f.get("severity", "?")
                _interp = str(f.get("interpretation", ""))[:120]
                _golden_tag = " [GOLDEN RULE]" if f.get("is_golden_rule") else ""
                _struct_tag = " [STRUCTURAL]" if f.get("is_structural") else ""
                narrative_parts.append(
                    f"  Fracture: {_ftype} severity={_sev}"
                    f"{_golden_tag}{_struct_tag} — {_interp}"
                )
            if caie.get("daubert_note"):
                narrative_parts.append(f"  {caie['daubert_note'][:200]}")
            narrative_parts.append("")
        elif caie and caie.get("status") == "NO_ARTIFACTS":
            narrative_parts.append("--- CAIE ---")
            narrative_parts.append("  No artifacts for cross-correlation (0 signals).")
            narrative_parts.append("")
        elif caie and caie.get("status") == "ERROR":
            # F8 (N9): un fallo del motor CAIE era invisible en el reporte.
            narrative_parts.append("--- CAIE ---")
            narrative_parts.append(
                f"  ERROR — el motor de fracturas cross-artefacto falló: "
                f"{str(caie.get('error', ''))[:160]}"
            )
            narrative_parts.append("  La correlación cross-artefacto NO está disponible para este caso.")
            narrative_parts.append("")

        # B-140 (L-029 / FW-009 Fase 1): surfacear la anotación DARVO del
        # scorer — asimetría de inversión de roles (infraestructura de
        # vigilancia operada por el actor acusador + reclamo de cero
        # contacto). SOLO anotación: el veredicto no fue modificado, y la
        # narrativa lo dice explícitamente.
        darvo = inner.get("darvo", {}) if isinstance(inner, dict) else {}
        if darvo and darvo.get("status") == "OK":
            narrative_parts.append("--- DARVO PATTERN (asimetría de inversión de roles — anotación) ---")
            narrative_parts.append(
                f"  Señales de vigilancia: {darvo.get('surveillance_count', 0)} "
                f"| Reclamos de cero contacto: {darvo.get('zero_contact_count', 0)} "
                f"| Penalidad registrada (NO aplicada): {darvo.get('penalty', '0')}"
            )
            _darvo_matched = darvo.get("matched_artifacts") or []
            if _darvo_matched:
                narrative_parts.append(
                    "  Artefactos disparadores: "
                    + ", ".join(str(x) for x in _darvo_matched[:6])
                )
            # F1: el caveat L-004 y la refutación obligatoria viajan CON el
            # bloque hasta la narrativa sellada — nunca como nota al pie
            # externa que un lector pueda no ver.
            if darvo.get("trigger_class"):
                narrative_parts.append(f"  Caveat: {str(darvo['trigger_class'])[:160]}")
            if darvo.get("devil_advocate"):
                narrative_parts.append(
                    f"  Devil's advocate: {str(darvo['devil_advocate'])[:240]}"
                )
            if darvo.get("daubert_note"):
                narrative_parts.append(f"  {str(darvo['daubert_note'])[:250]}")
            narrative_parts.append("")

        # F7 (N8): sección explícita de artefactos no analizados — "no
        # analizado" nunca más enterrado en el JSON del bundle.
        _unanalyzed = inner.get("unanalyzed_artifacts", []) if isinstance(inner, dict) else []
        _engine_errors = {
            k: v.get("error") for k, v in inner.items()
            if isinstance(v, dict) and v.get("error")
        } if isinstance(inner, dict) else {}
        _reasoner_err = inner.get("reasoner_error") if isinstance(inner, dict) else None
        if _unanalyzed or _engine_errors or _reasoner_err:
            narrative_parts.append("--- ARTEFACTOS NO ANALIZADOS / MOTORES CON ERROR ---")
            for art in _unanalyzed:
                narrative_parts.append(f"  NO ANALIZADO: {art}")
            for eng, err in _engine_errors.items():
                narrative_parts.append(f"  MOTOR {eng}: {str(err)[:120]}")
            if _reasoner_err:
                narrative_parts.append(f"  REASONER: {str(_reasoner_err)[:160]}")
            narrative_parts.append(
                "  Nota: 0 hallazgos sobre un artefacto no analizado NO es "
                "evidencia de benignidad."
            )
            narrative_parts.append("")

        if n_critical >= 3:
            alert = "CRITICAL — Multiple high-magnitude signals. Compromise confirmed with high probability."
        elif n_critical >= 1 or n_high >= 3:
            alert = "HIGH — Significant anomalies detected. Priority forensic review recommended."
        elif n_high >= 1:
            alert = "MEDIUM — Moderate anomalies. Additional investigation recommended."
        else:
            # B-065 (parte B): LOW describe magnitud por señal — no afirma
            # benignidad. El texto anterior ("No significant anomalies
            # detected") contradecía un veredicto MALICE dos líneas más abajo.
            alert = (
                "LOW (per-signal magnitude) — no individual primary signal "
                "exceeds z>2 in this iteration."
            )

        # B-065 (parte A — supersede el proxy de B-028): el piso del nivel de
        # alerta se calcula sobre el VEREDICTO FINAL (classify_agent_verdict,
        # el mismo camino único que sella agent_verdict y decide el exit
        # code), no sobre is_conclusive + substring de la hipótesis. El proxy
        # dejaba el piso muerto para evidencia distribuida no-concluyente:
        # 44 bundles del corpus sellaban "Verdict: MALICE" junto a "LOW — No
        # significant anomalies detected" (misma familia que B-058: una
        # re-derivación paralela del veredicto que divergía del clasificador).
        # Umbrales de B-028 intactos: MALICE → HIGH si posterior ≥ 1/8, si no
        # MEDIUM; INTENT → mínimo MEDIUM.
        _n_primary_cls, _n_unanalyzed_cls = _signal_stats(results)
        _final_verdict = classify_agent_verdict(
            abduction, _n_primary_cls, _n_unanalyzed_cls
        )
        _magnitude_alert = alert
        if _final_verdict == "MALICE" and (
                alert.startswith("LOW") or alert.startswith("MEDIUM")):
            _posterior_str = str(abduction.get("best_posterior", "0/1"))
            try:
                _num, _den = map(int, _posterior_str.split("/"))
                _posterior_ratio = Fraction(_num, max(_den, 1))
            except Exception:
                _posterior_ratio = Fraction(0, 1)
            if _posterior_ratio >= Fraction(1, 8):
                alert = (
                    "HIGH — MALICE verdict from Bayesian posterior aggregation. "
                    "Individual z-scores below threshold (distributed evidence "
                    "pattern: no single dominant signal, but aggregate posterior "
                    "is decisive). Alert floored (B-028/B-065)."
                )
            else:
                alert = (
                    "MEDIUM — MALICE verdict from posterior aggregation. "
                    "Individual z-scores below threshold. Full signal review "
                    "recommended. Alert floored (B-028/B-065)."
                )
        elif _final_verdict in ("INTENT", "SUSPICION") and alert.startswith("LOW"):
            # Review fix (B-100 follow-up): name the ACTUAL verdict — the old
            # hardcoded "INTENT verdict" sealed a narrative claiming INTENT on
            # SUSPICION cases, overstating a finding that explicitly did not
            # meet the two-source Refutation Protocol.
            alert = (
                f"MEDIUM — {_final_verdict} verdict with individual z-scores "
                "below threshold. Alert floored (B-028/B-065): an intent-class "
                "finding cannot present as LOW."
            )
        elif _final_verdict == "ABSTAIN":
            # B-100: an ABSTAIN (pipeline error, unanalyzed artifacts,
            # insufficient signals) must not close with an assessed-looking
            # level — 5 sealed corpus bundles paired
            # best_hypothesis=PIPELINE_ERROR with a LOW alert (the
            # FALLO_OCULTO PARCIAL of AUDIT_NARRATIVAS_20260702).
            # Review widening: the first fix only intercepted LOW; an ABSTAIN
            # whose analyzed fragment contained one z>2 signal still sealed an
            # unqualified MEDIUM/HIGH/CRITICAL — same hidden-failure class,
            # over-alarming direction. LOW becomes INDETERMINATE; higher
            # magnitudes keep their level but are explicitly scoped to the
            # analyzed portion.
            _hyp_label = str(abduction.get("best_hypothesis") or "no hypothesis")
            if alert.startswith("LOW"):
                alert = (
                    f"INDETERMINATE — ABSTAIN verdict ({_hyp_label}): the "
                    "evidence was not (fully) analyzed, so no alert level can "
                    "be asserted."
                )
            else:
                alert = (
                    f"{alert} [ABSTAIN verdict ({_hyp_label}): this level "
                    "describes the ANALYZED portion only — the evidence was "
                    "not (fully) analyzed.]"
                )

        narrative_parts.extend([
            "--- FINAL ALERT LEVEL ---",
            alert,
        ])
        # B-065 (parte B): línea de reconciliación — cuando el veredicto y la
        # magnitud por señal divergen, la narrativa explica ambos niveles en
        # vez de imprimirlos contradictorios lado a lado.
        if alert is not _magnitude_alert:
            if _final_verdict == "ABSTAIN":
                # B-100: the aggregation wording below is wrong for ABSTAIN —
                # nothing was aggregated; the magnitude line only describes
                # what little was analyzed.
                narrative_parts.append(
                    f"Reconciliation: ABSTAIN verdict — the per-signal "
                    f"magnitude level ({_magnitude_alert}) describes only the "
                    f"analyzed portion and is not an assessment of the "
                    f"unanalyzed evidence."
                )
            else:
                narrative_parts.append(
                    f"Reconciliation: verdict {_final_verdict} rests on "
                    f"hypothesis-level aggregation, not on any single "
                    f"high-magnitude signal. Per-signal magnitude level was: "
                    f"{_magnitude_alert}"
                )
        narrative_parts.extend([
            "",
            f"Critical signals (z>3, primary): {n_critical}",
            f"High signals (2<z<=3, primary): {n_high}",
            f"Primary signals: {len(primary)} | Derived: {len(derived)} | Total: {len(signals)}",
        ])

        return "\n".join(narrative_parts)

    def _seal_bundle(
        self,
        results: Dict[str, Any],
        narrative: str,
        evidence_sha256: str,
        runtime_fingerprint: str = "UNAVAILABLE",
    ) -> Dict[str, Any]:
        """
        Seals the final bundle with SHA-256.
        Includes full audit trail, results, and narrative.
        """
        abduction = results.get("abduction", {})
        # F5/F7: el veredicto se clasifica sobre señales PRIMARIAS y considera
        # los artefactos no analizados (NOISE con pérdidas → ABSTAIN).
        n_primary, n_unanalyzed = _signal_stats(results)
        agent_verdict = classify_agent_verdict(abduction, n_primary, n_unanalyzed)

        # B-027 (guard central): un bundle con veredicto ABSTAIN no puede
        # sellar is_conclusive=True — "no puedo formar opinión" y "estoy
        # seguro" son mutuamente excluyentes bajo cross-examination. Los
        # adaptadores ya lo evitan en origen; este guard cierra la clase
        # entera para cualquier camino futuro. Se degrada DESPUÉS de
        # clasificar (no cambia el veredicto) y queda anotado.
        if agent_verdict == "ABSTAIN" and abduction.get("is_conclusive"):
            abduction["is_conclusive"] = False
            abduction["is_conclusive_downgraded"] = (
                "B-027: ABSTAIN es incompatible con is_conclusive=True — "
                "degradado en el sellado"
            )
            logger.warning(
                "[SEAL] B-027 guard: is_conclusive=True degradado a False "
                "(veredicto ABSTAIN, hipótesis %s)",
                abduction.get("best_hypothesis"),
            )

        bundle = {
            "vigia_agent_version": AGENT_VERSION,
            "case_id": self.case_id,
            "evidence_path": str(self.evidence_path),
            "evidence_sha256": evidence_sha256,
            # B-166: versioned content manifest of the deterministic runtime.
            # A batch may reuse this sealed result only if its current runtime
            # fingerprint is identical; a valid evidence hash alone is not
            # proof that current code would reach the same result.
            "runtime_fingerprint": runtime_fingerprint,
            "analysis_timestamp": _utcnow(),
            "iterations_executed": self.iteration + 1,
            "self_corrections_applied": len(self.corrections_applied),
            # Veredicto de 4 valores (MALICE/INTENT/ABSTAIN/NOISE) — embebido y
            # sellado para que main() y el bundle no puedan divergir. ABSTAIN
            # distingue "no se pudo analizar" de "analizado y limpio".
            "agent_verdict": agent_verdict,
            # F5/F7: estadísticas que sustentan la clasificación de arriba.
            "signal_stats": {
                "n_total_signals": len(results.get("signals", []) or []),
                "n_primary_signals": n_primary,
                "n_unanalyzed_artifacts": n_unanalyzed,
            },
            "pipeline_results": results,
            "narrative": narrative,
            "audit_trail": self.audit.export(),
            "sans_compliance": {
                # FIX P1-5: real verifications instead of hardcoded True flags
                "self_correction": self.iteration > 0 or len(self.corrections_applied) > 0,
                "accuracy_validation": _accuracy_validation(
                    results.get("signals", [])
                ),
                "analytical_reasoning": bool(
                    results.get("abduction", {}).get("narrative")
                    and results.get("abduction", {}).get("best_hypothesis")
                    not in ("UNKNOWN", "UNDETERMINED", "", None)
                ),
                "audit_trail": len(self.audit.entries) > 0,
                "architectural_guardrails": True,  # Design invariant — always True by construction
                "evidence_integrity": bool(evidence_sha256) and len(evidence_sha256) == 64,
            },
        }

        # Canonical bundle serialization — no embedded hash field.
        # SHA-256 is written EXCLUSIVELY to <output>.sha256.
        # The .json file on disk is exactly the text that is hashed —
        # verifiable with: sha256sum -c <output>.sha256
        bundle_text = json.dumps(
            bundle, indent=2, sort_keys=True, ensure_ascii=True, default=_json_serial
        )
        bundle_digest = hashlib.sha256(bundle_text.encode("utf-8")).hexdigest()
        # bundle_sha256 is NOT embedded in the JSON — avoids self-reference paradox.
        # The bundle_sha256 field only lives in the audit trail and in the .sha256 file.

        self.audit.log(
            action="BUNDLE_SEALED",
            tool="bundle_sealer",
            inputs={},
            outputs={"bundle_sha256": bundle_digest},
            iteration=self.iteration,
            note=f"Bundle sealed: {bundle_digest[:16]}...",
        )
        logger.info("[BUNDLE] SHA-256: %s", bundle_digest)
        return bundle, bundle_text, bundle_digest

    def run(self) -> Dict[str, Any]:
        """
        Main agent loop.
        Returns the sealed bundle with all results.
        """
        logger.info("[AGENT] Starting VIGÍA Agent — case %s", self.case_id)
        logger.info("[AGENT] Evidence: %s", self.evidence_path)

        # B-166: record both the entrypoint and the complete deterministic
        # runtime manifest.  The former remains useful for historical bundles;
        # the latter prevents a cache from hiding a scorer/adapter change.
        try:
            agent_source = Path(__file__).read_bytes()
            agent_sha256 = hashlib.sha256(agent_source).hexdigest()
        except OSError:
            agent_sha256 = "UNAVAILABLE"
        try:
            runtime_fingerprint = runtime_execution_fingerprint(Path(__file__).parent)
        except (OSError, RuntimeError) as exc:
            runtime_fingerprint = "UNAVAILABLE"
            logger.warning("[AGENT] Runtime fingerprint unavailable: %s", exc)
        self.audit.log(
            action="AGENT_INITIALIZED",
            tool="vigia_agent",
            inputs={"case_id": self.case_id, "agent_file": __file__},
            outputs={
                "agent_sha256": agent_sha256,
                "agent_version": AGENT_VERSION,
                "runtime_fingerprint": runtime_fingerprint,
            },
            iteration=0,
            note=(
                "Agent initialized — source SHA-256: "
                f"{agent_sha256[:16]}...; runtime fingerprint: "
                f"{runtime_fingerprint[:16]}..."
            ),
        )
        logger.info("[AGENT] Agent SHA-256: %s", agent_sha256)

        # 1. Verify evidence integrity
        evidence_sha256 = self._hash_evidence()

        # 2. Analysis loop with self-correction
        results = {}
        params = {}
        prev_verdict = None

        for self.iteration in range(MAX_ITERATIONS):
            logger.info("[AGENT] === Iteration %d/%d ===", self.iteration + 1, MAX_ITERATIONS)

            # Ejecutar pipeline
            results = self._run_pipeline(params)

            # Detectar y corregir contradicciones
            had_corrections, results = self._detect_and_correct(results)

            if not had_corrections:
                logger.info("[AGENT] No contradictions — analysis converged at iteration %d", self.iteration + 1)
                break

            # Convergence criterion: same verdict as previous iteration
            current_verdict = results.get("abduction", {}).get("best_hypothesis", "")
            if current_verdict == prev_verdict and prev_verdict is not None:
                logger.info("[AGENT] Convergence detected — stable verdict at iteration %d", self.iteration + 1)
                self.audit.log(
                    action="CONVERGENCE_DETECTED",
                    tool="convergence_check",
                    inputs={"iteration": self.iteration},
                    outputs={"verdict": current_verdict},
                    iteration=self.iteration,
                    note=f"Stable verdict: {current_verdict}",
                )
                break
            prev_verdict = current_verdict

            # Prepare parameters for next iteration
            params = results.pop("params_for_rerun", {})
            logger.info("[AGENT] Corrections applied, re-running with params: %s", params)

        # 3. Generate narrative
        logger.info("[AGENT] Generating investigative narrative")
        # F3 (AUDITORIA_PIPELINE_ROBUSTEZ, N10): la narrativa se genera ANTES
        # del log AGENT_EXIT — _generate_narrative aplica el override L-036,
        # y el audit trail debe registrar el mismo veredicto que se sella.
        narrative = self._generate_narrative(results, evidence_sha256)

        # Log agent exit in audit trail BEFORE sealing — so it appears in the bundle.
        # Usa la misma clasificación de 4 valores que el veredicto sellado.
        _abduction_preview = results.get("abduction", {})
        _n_primary_prev, _n_unanalyzed_prev = _signal_stats(results)
        _verdict_preview = classify_agent_verdict(
            _abduction_preview, _n_primary_prev, _n_unanalyzed_prev
        )
        exit_code_preview = _VERDICT_EXIT.get(_verdict_preview, EXIT_ABSTAIN)
        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": _abduction_preview.get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview, "agent_verdict": _verdict_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} ({_verdict_preview}) — analysis complete.",
        )

        # R7 — deterministic devil_advocate for the agent audit-trail path.
        # sift_orchestrator.py as imported here resolves to the root-level
        # compatibility shim (confirmed by direct diff, 2026-06-19), not
        # vigia/sift/sift_orchestrator.py — CasePatternLibrary is never
        # reachable from this entry point. pattern_signal_metadata=None is
        # architecturally confirmed, not assumed. Never overwrites a
        # human-provided value because this path never had one.
        if exit_code_preview == 1 and not results.get("abduction", {}).get("devil_advocate"):
            from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
            _verdict = results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")
            results.setdefault("abduction", {})["devil_advocate"] = compose_devil_advocate_struct(
                pattern_signal_metadata=None,
                raw_verdict=_verdict,
                mapped_verdict=_verdict,
                score=results.get("pipeline_meta", {}).get("avg_score", "0"),
                confidence=results.get("abduction", {}).get("best_posterior", "0"),
                scope_note="agent audit-trail mode (vigia_agent.py — JSON-replay / autonomous path)",
            )

        # 4. Seal bundle — returns (bundle_dict, canonical_json_text, sha256_digest)
        bundle, bundle_canonical_text, bundle_digest = self._seal_bundle(
            results, narrative, evidence_sha256, runtime_fingerprint
        )
        # Attach temporary fields for main() — extracted with pop() before writing to disk
        bundle["_canonical_text"] = bundle_canonical_text
        bundle["_canonical_digest"] = bundle_digest

        logger.info(
            "[AGENT] Analysis complete — %d iteration(s), %d correction(s) applied",
            self.iteration + 1,
            len(self.corrections_applied),
        )
        return bundle


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

# Backward-compatible alias — the semantically correct name is _utc_iso_timestamp
_utcnow = _utc_iso_timestamp


def _summarize(obj: Any, max_len: int = 200) -> Any:
    """Safe summary of an object for the audit trail."""
    if isinstance(obj, dict):
        return {k: _summarize(v) for k, v in list(obj.items())[:10]}
    if isinstance(obj, list):
        return [_summarize(v) for v in obj[:5]]
    s = str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s


def _build_orchestrator_kwargs(evidence_path: Path, params: Dict) -> Dict:
    """Builds kwargs for SIFTOrchestrator.analyze() based on evidence type."""
    kwargs: Dict[str, Any] = {}

    if evidence_path.is_dir():
        # Evidence directory — search for known artifact types
        for pattern, key in [
            ("*.evtx", "event_logs"),
            ("*.raw", "memory_path"),
            ("*.E01", "disk_path"),
            ("*.e01", "disk_path"),
            ("*.log", "log_path"),
            ("*.pcap", "pcap_path"),
            ("*.pcapng", "pcap_path"),
            ("SAM", "registry_hives"),
            ("SYSTEM", "registry_hives"),
            ("SOFTWARE", "registry_hives"),
            ("SECURITY", "registry_hives"),
            ("NTUSER.DAT", "registry_hives"),
        ]:
            # FIX P2-7: cap at 100 files per pattern and maxdepth 3 — prevents DoS
            matches = []
            for m in sorted(evidence_path.rglob(pattern)):
                if m.is_symlink():
                    continue
                try:
                    depth = len(m.relative_to(evidence_path).parts)
                except ValueError:
                    continue
                if depth > 3:
                    continue
                matches.append(str(m))
                if len(matches) >= 100:
                    logger.warning(
                        "[ORCHESTRATOR] Pattern %s capped at 100 files in %s",
                        pattern, evidence_path,
                    )
                    break
            if matches:
                # Accumulate in list to support segmented images (E01, E02, ...)
                existing = kwargs.get(key)
                if existing is None:
                    kwargs[key] = matches
                elif isinstance(existing, list):
                    kwargs[key] = existing + matches
                else:
                    kwargs[key] = [existing] + matches

        # B-045: detect Android/iOS evidence directories by marker files
        all_names = {f.name for f in evidence_path.rglob("*") if f.is_file() and not f.is_symlink()}

        # P1-A: detectar perfil de navegador (Chromium History / Firefox
        # places.sqlite) por archivos marcador. El parser SQLite real
        # (browser_forensics) analiza descargas e historial. Se pasa el
        # directorio que contiene la base como browser_profile.
        for marker in ("History", "places.sqlite"):
            for f in evidence_path.rglob(marker):
                if f.is_file() and not f.is_symlink():
                    kwargs["browser_profile"] = str(f.parent)
                    break
            if kwargs.get("browser_profile"):
                break

        # P1-B: detectar directorio de Prefetch (archivos .pf) por marcador.
        # El parser real detecta ejecución de herramientas de ataque por nombre
        # (formatos SCCA clásico y MAM comprimido).
        for f in evidence_path.rglob("*.pf"):
            if f.is_file() and not f.is_symlink():
                kwargs["prefetch_dir"] = str(f.parent)
                break

        # P0-C: detectar un $MFT extraído (nombre literal '$MFT' o *.mft). El
        # parser binario (mft_parser) lo convierte a JSON para el analyzer —
        # antes MFT/disco quedaba ciego en modo agente (falso negativo).
        for pat in ("$MFT", "*.mft", "*.MFT"):
            for f in evidence_path.rglob(pat):
                if f.is_file() and not f.is_symlink():
                    kwargs["mft_path"] = str(f)
                    break
            if kwargs.get("mft_path"):
                break
        try:
            from vigia.sift.android_forensics import _ANDROID_MARKER_FILES
            if all_names & _ANDROID_MARKER_FILES:
                kwargs["android_evidence_path"] = str(evidence_path)
        except ImportError:
            pass
        try:
            from vigia.sift.ios_forensics import _IOS_MARKER_FILES
            if all_names & _IOS_MARKER_FILES:
                kwargs["ios_evidence_path"] = str(evidence_path)
        except ImportError:
            pass
        # B-046: detect Google Takeout evidence directories by marker files
        try:
            from vigia.sift.google_takeout_forensics import _TAKEOUT_MARKER_FILES
            if all_names & _TAKEOUT_MARKER_FILES:
                kwargs["takeout_evidence_path"] = str(evidence_path)
        except ImportError:
            pass
        # B-048: detect macOS evidence directories by marker files.
        # Collision guard: History.db (Safari) also lives in _IOS_MARKER_FILES,
        # and every real macOS evidence set has one — detecting macOS on shared
        # names would run both engines over the same artifacts (double count).
        # macOS therefore requires a marker NOT shared with iOS. The two
        # cross-platform databases that used to leak into this exclusive set —
        # knowledgeC.db (B-133) and TCC.db (B-137) — are now iOS markers too,
        # so a full iOS extraction carrying them no longer routes to macOS;
        # the shim precedence guard still resolves any genuine same-directory
        # dual match.
        try:
            from vigia.sift.macos_forensics import _MACOS_MARKER_FILES
            from vigia.sift.ios_forensics import _IOS_MARKER_FILES
            if all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES):
                kwargs["macos_evidence_path"] = str(evidence_path)
        except ImportError:
            pass
    else:
        # Single file — detect type by extension
        suffix = evidence_path.suffix.lower()
        if suffix == ".raw":
            kwargs["memory_path"] = str(evidence_path)
        elif suffix in (".e01", ".E01"):
            kwargs["disk_path"] = str(evidence_path)
        elif suffix == ".evtx":
            kwargs["event_logs"] = [str(evidence_path)]
        elif suffix in (".img", ".vmem", ".mem", ".dmp"):
            # Raw memory image — route to vol3 adapter
            kwargs["memory_path"] = str(evidence_path)
        elif suffix in (".pcap", ".pcapng"):
            kwargs["pcap_path"] = str(evidence_path)
        else:
            # Generic text — use as event_stream
            kwargs["log_path"] = str(evidence_path)

    # Apply correction adjustments if any
    if params.get("elevate_technical_signals"):
        kwargs["signal_weight_override"] = {"memory": Fraction(3, 2), "disk": Fraction(3, 2)}
    if params.get("uniform_weights"):
        kwargs["uniform_module_weights"] = True

    return kwargs


def _run_text_pipeline(evidence_path: Path, case_id: str, params: Dict) -> Dict[str, Any]:
    """
    Text pipeline — fallback when SIFTOrchestrator is unavailable.
    Valid for text evidence only — fails explicitly for binary files.
    """
    # SECURITY: reject symlinks before any read operation
    if evidence_path.is_symlink():
        logger.error("[TEXT_PIPELINE] Evidence path is symlink — rejected for security: %s", evidence_path)
        return {
            "case_id": case_id, "signals": [],
            "abduction": {"best_hypothesis": "SYMLINK_REJECTED", "is_conclusive": False,
                          "narrative": "[SECURITY] Symlink rejected — possible path traversal."},
            "pipeline_meta": {"error": "symlink_rejected"},
        }

    # Reject binary evidence — do not attempt to read as text
    if evidence_path.is_file():
        binary_extensions = {
            ".raw", ".vmdk", ".dd", ".aff", ".img",
            # EnCase image segments — E01 through E09, e01 through e09
            ".e01", ".e02", ".e03", ".e04", ".e05", ".e06", ".e07", ".e08", ".e09",
            ".E01", ".E02", ".E03", ".E04", ".E05", ".E06", ".E07", ".E08", ".E09",
            # Generic numbered segments
            ".001", ".002", ".003",
        }
        if evidence_path.suffix.lower() in binary_extensions:
            return {
                "case_id": case_id,
                "signals": [],
                "abduction": {
                    "best_hypothesis": "BINARY_EVIDENCE_REQUIRES_SIFT_ORCHESTRATOR",
                    "is_conclusive": False,
                    "narrative": "[ERROR] Binary evidence cannot be processed with the text pipeline. "
                                 "SIFTOrchestrator is required for this file type.",
                },
                "pipeline_meta": {"error": f"Binary evidence type: {evidence_path.suffix}"},
            }

    input_path = None
    output_path = None
    try:
        sys.path.insert(0, str(Path(__file__).parent))

        if evidence_path.is_file():
            text = evidence_path.read_text(encoding="utf-8", errors="ignore")[:50000]
        else:
            texts = []
            # SECURITY: filtrar symlinks en rglob — previene lectura arbitraria
            txt_files = [f for f in sorted(evidence_path.rglob("*.txt"))
                         if not f.is_symlink() and f.is_file()][:5]
            for f in txt_files:
                texts.append(f.read_text(encoding="utf-8", errors="ignore")[:10000])
            text = "\n---\n".join(texts) if texts else "No text evidence found."

        # Apply correction params to text pipeline if applicable
        if params.get("elevate_technical_signals"):
            text = f"[ELEVATED_ANALYSIS] {text}"
        if params.get("uniform_weights"):
            # uniform_weights not implemented in text pipeline —
            # los z_scores del texto no tienen pesos modulares diferenciados.
            logger.warning(
                "[TEXT_PIPELINE] uniform_weights requested but not implemented in text "
                "fallback mode. Parameter ignored. Use SIFTOrchestrator for real reweighting."
            )

        import tempfile
        artifacts = [{"artifact_id": f"{case_id}-001", "text": text}]

        fd_in, input_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd_in, 'w') as f:
            json.dump(artifacts, f)

        output_path = input_path.replace(".json", "_out.json")

        # B-054/F-L040-6 FIX (TRIAGE 2026-07-03): el import plano
        # `from run_pipeline import ...` apuntaba a un módulo que no existe
        # en el root del repo → este fallback SIEMPRE degradaba a
        # PIPELINE_UNAVAILABLE (código muerto que aparentaba ser red de
        # seguridad). El módulo real es vigia/scripts/run_pipeline.py, con
        # firma idéntica. Se conserva el import plano como segundo intento
        # para layouts legados.
        try:
            from vigia.scripts.run_pipeline import run as run_pipeline_fn
        except ImportError:
            from run_pipeline import run as run_pipeline_fn  # layout plano legado
        run_pipeline_fn(input_path, output_path, negation_enabled=True)

        with open(output_path) as f:
            pipeline_results = json.load(f)

        # Convertir al formato del agente — z_score como Fraction
        def _tagged_int(v: Any, default: int) -> int:
            """
            B-054 (2do hallazgo): el pipeline semiótico serializa enteros en
            formato canónico taggeado ("29:int"). Este parser esperaba ints
            crudos y crasheaba con TypeError en cuanto el fallback revivió
            (el import roto lo mantuvo como código muerto y el bug latente
            nunca se ejercitó).
            """
            if isinstance(v, bool):
                return default
            if isinstance(v, int):
                return v
            if isinstance(v, str):
                try:
                    return int(v.split(":", 1)[0])
                except ValueError:
                    return default
            return default

        signals = []
        for r in pipeline_results:
            dec = r.get("decision", {})
            agg = r.get("aggregator", {})
            mi = agg.get("mi_final", {"num": 0, "den": 1})
            # Rational Fraction — never float
            z_frac = Fraction(
                _tagged_int(mi.get("num"), 0),
                max(_tagged_int(mi.get("den"), 1), 1),
            )
            # Confidence derived from alert_level — not fabricated
            alert_to_conf = {"LOW": Fraction(1, 10), "MEDIUM": Fraction(4, 10),
                             "HIGH": Fraction(7, 10), "CRITICAL": Fraction(9, 10)}
            conf_frac = alert_to_conf.get(dec.get("alert_level", "LOW"), Fraction(1, 10))
            signals.append({
                "tool": "semiotic_pipeline",
                "z_score": z_frac,
                "confidence": conf_frac,
                "value": dec.get("verdict", ""),
                "metadata": {
                    "artifact_id": r.get("artifact_id"),
                    "alert_level": dec.get("alert_level", "LOW"),
                    "matches": r.get("matches", []),
                }
            })

        high_signals = [s for s in signals if s.get("z_score", 0) > Fraction(2, 1)]  # FIX: z>5 was impossible (Z_CLIP_MAX=5.0); use z>2 (HIGH threshold)
        hypothesis = "MALICIOUS_INTENT_DETECTED" if high_signals else "NO_ANOMALY_DETECTED"

        return {
            "case_id": case_id,
            "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                "best_posterior": str(Fraction(len(high_signals), max(len(signals), 1))),
                "confidence": str(Fraction(7, 10) if high_signals else Fraction(3, 10)),
                "narrative": f"[FIRSTNESS] Semiotic analysis of {len(signals)} artifacts. "
                             f"{'Adversarial patterns detected.' if high_signals else 'No semiotic anomalies.'}",
                "is_conclusive": len(high_signals) >= 2,
            },
            "pipeline_meta": {
                "backend": "text_pipeline",
                "n_artifacts": len(pipeline_results),
                "n_signals": len(signals),
                "params_applied": list(params.keys()),
            }
        }

    except ImportError as e:
        logger.error("[TEXT_PIPELINE] run_pipeline not available: %s", e)
        return {
            "case_id": case_id, "signals": [],
            "abduction": {"best_hypothesis": "PIPELINE_UNAVAILABLE", "is_conclusive": False,
                          "narrative": f"[ERROR] run_pipeline not found: {e}"},
            "pipeline_meta": {"error": str(e)},
        }
    except (MemoryError, RecursionError, KeyboardInterrupt, SystemExit):
        raise
    except (OSError, IOError, UnicodeDecodeError, json.JSONDecodeError) as e:
        # Errores operativos esperados — IO, encoding, parsing de archivos de evidencia
        logger.error("[TEXT_PIPELINE] Operational error: %s", e)
        return {
            "case_id": case_id, "signals": [],
            "abduction": {"best_hypothesis": "PIPELINE_ERROR", "is_conclusive": False,
                          "narrative": f"[ERROR] Operational failure: {e}"},
            "pipeline_meta": {"error": str(e), "error_type": type(e).__name__},
        }
    # NameError, SyntaxError, AttributeError, TypeError in run_pipeline.py
    # are code bugs — do NOT mask, propagate for visible failure
    finally:
        # Guarantee cleanup of temporary files
        for p in [input_path, output_path]:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except OSError:
                    pass




# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

# B-101: venv-vs-requirements drift check. defusedxml is declared in all
# three manifests (requirements.txt, requirements-ci.txt, pyproject.toml) but
# was absent from the runtime environment for weeks: 10/200 corpus cases
# silently lost their XML/EVTX signal (degrading to UNANALYZED/ABSTAIN per
# design — but the operator was never told why at startup). Degradation stays
# non-fatal by design (tests/test_tanda_a_triage.py enshrines degrade-not-
# crash); the drift itself must be loud.
# Review fix: the first version hardcoded only defusedxml, while the B-101
# registry names BOTH declared-but-absent deps — the check itself was a
# hand-maintained parallel manifest. Both known offenders are covered with
# their concrete degradation consequence.
_CRITICAL_RUNTIME_DEPS = {
    "defusedxml": "XML/EVTX evidence will degrade to UNANALYZED/ABSTAIN",
    "psutil": "process/resource monitoring tools will degrade",
}


def _warn_missing_critical_deps() -> None:
    import importlib.util

    for _dep, _consequence in _CRITICAL_RUNTIME_DEPS.items():
        if importlib.util.find_spec(_dep) is None:
            print(
                f"[VIGIA][StartupCheck] WARNING: dependency '{_dep}' is "
                f"declared in requirements.txt but NOT installed in this "
                f"environment. {_consequence}. Fix: pip install {_dep}",
                file=sys.stderr,
            )


def main() -> None:
    _warn_missing_critical_deps()
    parser = argparse.ArgumentParser(
        description="VIGÍA Autonomous Forensic Agent — SANS FIND EVIL Hackathon 2026",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 vigia_agent.py --evidence /cases/ROCBA --case-id ROCBA-001
  python3 vigia_agent.py --evidence /cases/xp-tdungan.raw --case-id XP-001
  python3 vigia_agent.py --evidence /cases/evidence.json --case-id TEST-001 --output report.json

Self-correction: automatic — no flags needed.
Narrative: 100% deterministic — no LLMs in core analysis.
Max iterations: 3 (hard cap, prevents infinite loops).

Exit codes:
  0  NO EVIL     — analyzed, no anomaly (NOISE / benign)
  1  EVIL        — MALICE
  2  ERROR       — agent-level exception (evidence unreadable, etc.)
  3  INTENT      — INTENT / SUSPICION
  4  ABSTAIN     — could not determine: pipeline error, missing dependency,
                   unanalyzed artifact, or insufficient signals. NOT benign.
        """,
    )
    parser.add_argument(
        "--evidence", required=True,
        help="Path to evidence file or directory (disk image, memory dump, log files, JSON)"
    )
    parser.add_argument(
        "--case-id", required=True,
        help="Case identifier (e.g. ROCBA-001, XP-TDUNGAN-001)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output path for sealed bundle JSON (default: <case-id>_bundle.json)"
    )
    parser.add_argument(
        "--audit-only", action="store_true",
        help="Export only the audit trail (no full bundle)"
    )
    # L-037: Examiner-declared acquisition metadata for CAIE trust gates.
    # Without these flags, CAIE honestly degrades trust for the missing fields.
    parser.add_argument(
        "--acquisition-tool", default=None,
        help="Forensic acquisition tool (e.g. 'ftk imager', 'dd', 'axiom'). "
             "Must match CAIE whitelist for gate G2."
    )
    parser.add_argument(
        "--write-blocker-used", default=None, choices=["true", "false"],
        help="Whether a write blocker was used during acquisition (true/false). "
             "Only 'true' passes CAIE gate G4."
    )
    parser.add_argument(
        "--examiner-id", default=None,
        help="Identity of the forensic examiner who acquired the evidence."
    )
    args = parser.parse_args()

    # Validate evidence
    evidence_path = Path(args.evidence)
    if not evidence_path.exists():
        logger.error("[FATAL] Evidence not found: %s", evidence_path)
        sys.exit(2)

    # FIX (auditoría FN, P0-B): publicar el directorio de evidencia en
    # VIGIA_EVIDENCE_DIR para que PathGuard lo incluya en su allowlist. Sin
    # esto, la evidencia pasada por --evidence fuera de las bases estáticas de
    # PathGuard se rechazaba en silencio → 0 señales → veredicto benigno espurio.
    # No sobreescribe un valor ya configurado por el operador.
    if not os.environ.get("VIGIA_EVIDENCE_DIR", "").strip():
        _ev_dir = evidence_path if evidence_path.is_dir() else evidence_path.parent
        os.environ["VIGIA_EVIDENCE_DIR"] = str(_ev_dir.absolute())
        logger.info("[AGENT] VIGIA_EVIDENCE_DIR=%s (PathGuard allowlist)",
                    os.environ["VIGIA_EVIDENCE_DIR"])

    # Output path
    # Sanitizar case-id para uso seguro como nombre de archivo
    safe_case_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", args.case_id)
    output_path = args.output or f"{safe_case_id}_bundle.json"

    # FIX P1-4: sanitize output to prevent path traversal
    output_path_obj = Path(output_path)
    try:
        resolved = output_path_obj.resolve()
        cwd = Path.cwd().resolve()
        # Use is_relative_to() — str.startswith() has edge cases with path prefixes
        if not resolved.is_relative_to(cwd):
            logger.error("[FATAL] Output path escapes working directory: %s", output_path)
            sys.exit(2)
    except (OSError, RuntimeError) as e:
        logger.error("[FATAL] Invalid output path: %s — %s", output_path, e)
        sys.exit(2)
    output_path = str(output_path_obj)

    # L-037: Build acquisition overrides from CLI flags
    _acq_overrides: Dict[str, Any] = {}
    if args.acquisition_tool:
        _acq_overrides["acquisition_tool"] = args.acquisition_tool
    if args.write_blocker_used is not None:
        _acq_overrides["write_blocker_used"] = (args.write_blocker_used == "true")
    if args.examiner_id:
        _acq_overrides["examiner_id"] = args.examiner_id

    # Execute agent
    agent = VIGIAAgent(
        case_id=args.case_id,
        evidence_path=str(evidence_path),
        acquisition_overrides=_acq_overrides or None,
    )

    t0 = time.monotonic()
    bundle = agent.run()
    elapsed = time.monotonic() - t0

    # Extract canonical text and digest from bundle
    bundle_canonical_text = bundle.pop("_canonical_text", None)
    bundle_canonical_digest = bundle.pop("_canonical_digest", None)

    # Export result
    # L-023 (auditoría 2026-07-06, F-1): la escritura del bundle sellado —
    # artefacto de custodia primario del Modo 1 — pasa por atomic_io
    # (mkstemp+fsync+os.replace+fsync de directorio), en paridad con
    # BundleBuilder.save y con los writers de vigia/pipeline. Antes se usaba
    # Path.write_text directo: el patrón NO atómico que L-023 vino a corregir,
    # aún presente en el camino primario.
    from vigia.core.atomic_io import atomic_write_text

    if args.audit_only:
        output_text = json.dumps(bundle["audit_trail"], indent=2, sort_keys=True,
                                 default=_json_serial, ensure_ascii=True)
    else:
        # Write EXACTLY the canonical text that was hashed — sha256sum -c guarantee
        output_text = bundle_canonical_text or json.dumps(
            bundle, indent=2, sort_keys=True, default=_json_serial, ensure_ascii=True
        )
    atomic_write_text(output_path, output_text)

    # Write .sha256 file — verifies exactly what is on disk
    if bundle_canonical_text and not args.audit_only:
        sha256_path = output_path + ".sha256"
        # F-1b (auditoría 2026-07-06): el digest se computa RE-LEYENDO el archivo
        # de disco, no sobre output_text en memoria. Antes se hasheaba la variable
        # en memoria y se comparaba contra bundle_canonical_digest (también
        # memoria): un chequeo tautológico que NO detectaba write parcial, swap
        # concurrente ni symlink. Ahora el .sha256 atesta exactamente lo escrito
        # — paridad con BundleBuilder.save, que ya re-lee de disco.
        with open(output_path, "rb") as _bf:
            disk_bytes = _bf.read()
        disk_digest = hashlib.sha256(disk_bytes).hexdigest()
        # FIX P2-8: verify that what was written to disk matches the bundle digest
        if bundle_canonical_digest and disk_digest != bundle_canonical_digest:
            logger.error(
                "[BUNDLE] DISK MISMATCH: bundle_digest=%s disk_digest=%s",
                bundle_canonical_digest, disk_digest,
            )
            raise RuntimeError(
                "Bundle hash mismatch after write — possible filesystem corruption or race condition"
            )
        # Use absolute path so sha256sum -c works from any directory
        abs_output_path = str(Path(output_path).resolve())
        atomic_write_text(sha256_path, f"{disk_digest}  {abs_output_path}\n")
        logger.info("[BUNDLE] Verification: sha256sum -c %s", sha256_path)

    # Reasoning trace (Cronos-in-VIGÍA): a PROCESS-evidence sibling of the bundle,
    # sealed with its own ToolExecutionLogChain and written OUTSIDE the
    # bundle_digest. The agent bundle hashes its ENTIRE dict (sha256sum -c), so
    # the trace CANNOT live inside it without changing the digest — it lives in a
    # separate <stem>_reasoning_trace.json. verify_reasoning_trace() binds the two
    # by asserting the trace verdict == agent_verdict. Fail-soft: a trace-write
    # error must never discard the already-sealed bundle (§5.3 honest degradation).
    if not args.audit_only:
        try:
            from vigia.core.reasoning_trace import build_from_agent_bundle
            _trace_dict = build_from_agent_bundle(bundle)
            _trace_path = (output_path[:-5] + "_reasoning_trace.json"
                           if output_path.endswith(".json")
                           else output_path + "_reasoning_trace.json")
            atomic_write_text(_trace_path, json.dumps(
                _trace_dict, indent=2, sort_keys=True, ensure_ascii=True, default=_json_serial))
            logger.info("[TRACE] reasoning trace: %s (verdict=%s, chain_tip=%s)",
                        _trace_path, _trace_dict.get("verdict"),
                        str(_trace_dict.get("chain_tip_sha256", ""))[:16])
        except Exception as _trace_err:  # noqa: BLE001 — non-critical, fail-soft
            logger.warning("[TRACE] reasoning trace not written (non-fatal): %s", _trace_err)

    # Console summary
    abduction = bundle.get("pipeline_results", {}).get("abduction", {})
    hypothesis = abduction.get("best_hypothesis", "UNDETERMINED")
    # Veredicto de 4 valores: leído del bundle sellado (no recomputado — así el
    # exit code no puede divergir del veredicto que quedó firmado en disco).
    agent_verdict = bundle.get("agent_verdict") or classify_agent_verdict(
        abduction, *_signal_stats(bundle.get("pipeline_results", {}))
    )

    print("\n" + "=" * 60)
    print(f"VIGÍA AGENT — CASE {args.case_id}")
    print("=" * 60)
    print(f"Evidence SHA-256  : {bundle.get('evidence_sha256', 'N/A')[:32]}...")
    # bundle_sha256 not in dict (no paradox) — read from computed digest
    _display_digest = bundle_canonical_digest or "see .sha256 file"
    print(f"Bundle SHA-256    : {_display_digest[:32]}...")
    print(f"Iterations        : {bundle.get('iterations_executed', 1)}")
    print(f"Corrections       : {bundle.get('self_corrections_applied', 0)}")
    print(f"Analysis time     : {elapsed:.2f}s")
    print(f"Hypothesis        : {hypothesis}")
    print(f"Verdict           : {agent_verdict}")
    print(f"Evil found        : {'YES' if agent_verdict == 'MALICE' else 'NO'}")
    print(f"Output            : {output_path}")
    print("=" * 60)

    # Print narrative
    print("\n" + bundle.get("narrative", "[No narrative]"))

    # Documented exit code — 0=no evil, 1=evil, 2=error, 3=intent, 4=ABSTAIN, 5=suspicion (B-097)
    exit_code = _VERDICT_EXIT.get(agent_verdict, EXIT_ABSTAIN)
    _exit_label = _VERDICT_LABEL.get(agent_verdict, agent_verdict)
    logger.info("[AGENT] Exit code: %d (%s)", exit_code, _exit_label)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
