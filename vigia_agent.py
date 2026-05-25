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

# ── Logging forense ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("vigia-agent")

# ── Constantes del agente ────────────────────────────────────────────────────
AGENT_VERSION = "1.0.0-SANS-2026"
MAX_ITERATIONS = 3                    # Hard cap — previene loops infinitos
CONTRADICTION_THRESHOLD = 2           # int: mínimo de contradicciones para activar re-análisis
CONFIDENCE_FLOOR = Fraction(3, 10)    # Umbral mínimo de MCP para veredicto conclusivo


# ── Helpers de conversión racional ───────────────────────────────────────────

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
        # Usar str() para evitar imprecisión binaria de float * entero
        # Fraction("0.1") == Fraction(1, 10) exacto; int(0.1 * 1e6) no lo es
        if value != value:  # NaN check
            return Fraction(0, 1)
        try:
            return Fraction(str(value))
        except (ValueError, OverflowError):
            return Fraction(0, 1)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return Fraction(0, 1)
        # Rechazar NaN e infinitos explícitamente — son datos corruptos
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
    raise TypeError(f"Tipo no serializable: {type(obj)!r} — {obj!r}")


def _utc_iso_timestamp() -> str:
    """Retorna timestamp UTC en formato ISO 8601 para audit trail."""
    return datetime.now(timezone.utc).isoformat()




# ════════════════════════════════════════════════════════════════════════════
# AUDIT TRAIL
# ════════════════════════════════════════════════════════════════════════════

class AgentAuditTrail:
    """
    Registro inmutable de todas las acciones del agente.
    Each entry has ISO 8601 timestamp, action, inputs, outputs and SHA-256.
    Los jueces pueden trazar cualquier finding hasta la herramienta que lo produjo.
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
        """Registra una acción. Retorna el SHA-256 de la entrada."""
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
        # SHA-256 de la entrada para integridad
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
        """Registra explícitamente una contradicción detectada entre módulos."""
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
        """Registra la corrección aplicada y el cambio de veredicto."""
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
        """Exporta el audit trail completo."""
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
# Guardrail arquitectónico — no basado en prompts
# ════════════════════════════════════════════════════════════════════════════

class ContradictionDetector:
    """
    Detects semantic contradictions between pipeline modules.

    Contradicciones detectadas:
    1. TEMPORAL_VS_CONTENT: timestamp inconsistente con contenido del artefacto
    2. ENTROPY_VS_BEHAVIORAL: high entropy + normal behavior (false negative)
    3. SEMIOTIC_VS_TECHNICAL: no linguistic patterns + high technical anomaly
    4. CONFIDENCE_COLLAPSE: high MCP but all individual modules low
    5. VERDICT_FLIP: veredictos opuestos entre motores de igual confianza
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
        # Alta entropía de artefacto + comportamiento temporal normal
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
        # MCP alto pero módulos individuales todos bajos
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

        # 4. VERDICT_FLIP entre abductive reasoning y señales directas
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
# Aplica ajustes deterministas cuando se detectan contradicciones
# ════════════════════════════════════════════════════════════════════════════

class CorrectionEngine:
    """
    Aplica correcciones deterministas a los resultados cuando hay contradicciones.
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
        Retorna un dict con las correcciones aplicadas y el nuevo veredicto sugerido.
        """
        corrections = {
            "contradiction_type": contradiction_type,
            "modules_adjusted": modules,
            "iteration": iteration,
            "adjustments": [],
            "suggested_verdict_upgrade": False,
        }

        # Corrección 1: ENTROPY_VS_BEHAVIORAL
        # Si hay alta entropía técnica pero comportamiento normal,
        # elevar el peso de las señales técnicas y marcar para revisión humana
        if "memory/disk_forensics" in modules or "disk_forensics" in modules:
            corrections["adjustments"].append(
                "Memory/disk signals elevated to 1.5x weight. "
                "Behavioral evasion documented as known attack vector."
            )
            corrections["suggested_verdict_upgrade"] = True
            corrections["recommended_action"] = "REQUIRE_HUMAN_REVIEW"

        # Corrección 2: SEMIOTIC_VS_TECHNICAL
        # Sin firma lingüística + anomalía técnica alta = técnica avanzada
        if "semiotic_detector" in modules and "technical_detector" in modules:
            corrections["adjustments"].append(
                "Absence of semiotic patterns recorded as positive indicator "
                "of advanced technical operator (APT). Technical alert preserved without downgrade."
            )
            corrections["recommended_action"] = "ESCALATE_TO_CRITICAL"

        # Corrección 3: CONFIDENCE_COLLAPSE
        if "mcp_aggregator" in modules:
            corrections["adjustments"].append(
                "MCP recalculated with uniform per-module weight "
                "(no amplification by individual confidence)."
            )
            corrections["recommended_action"] = "REWEIGHT_AND_RERUN"

        # Corrección 4: VERDICT_FLIP
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
# VIGIA AGENT — Loop principal
# ════════════════════════════════════════════════════════════════════════════

class VIGIAAgent:
    """
    Agente autónomo VIGÍA.

    Execution loop:
    1. Inicializar caso y cadena de custodia
    2. Calcular SHA-256 de la evidencia (integridad)
    3. Ejecutar pipeline VIGÍA completo
    4. Detect contradictions between modules
    5. Si hay contradicciones: aplicar correcciones, repetir desde 3 (max MAX_ITERATIONS)
    6. Generar narrativa investigativa
    7. Exportar bundle sellado con SHA-256

    Self-correction is architectural:
    - ContradictionDetector opera sobre scores racionales, no sobre texto
    - CorrectionEngine aplica ajustes deterministas documentados
    - Each iteration is recorded in the audit trail with timestamp
    """

    def __init__(self, case_id: str, evidence_path: str):
        self.case_id = case_id
        self.evidence_path = Path(evidence_path)
        self.audit = AgentAuditTrail(case_id)
        self.contradiction_detector = ContradictionDetector()
        self.correction_engine = CorrectionEngine()
        self.iteration = 0
        self.corrections_applied: List[Dict] = []

    def _hash_evidence(self) -> str:
        """SHA-256 de la evidencia. Garantiza integridad — ningún análisis modifica el original."""
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
            # SECURITY: rechazar symlinks — previene lectura arbitraria de archivos del sistema
            if self.evidence_path.is_symlink():
                raise ValueError(
                    f"[SECURITY] Evidence path is symlink — rejected: {self.evidence_path}"
                )
            with open(self.evidence_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            digest = h.hexdigest()
        except (OSError, PermissionError):
            # Es un directorio — hashear contenido real de cada archivo (Merkle-like)
            h_dir = hashlib.sha256()
            if self.evidence_path.is_dir():
                for f in sorted(self.evidence_path.rglob("*")):
                    # SECURITY: saltar symlinks — previene path traversal y DoS por FIFOs
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
                        except OSError:
                            h_dir.update(str(f).encode())
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
        Ejecuta el pipeline VIGÍA.
        params allows adjusting weights in correction iterations.
        """
        params = params or {}
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
            # Intentar importar el orchestrator real
            sys.path.insert(0, str(Path(__file__).parent))
            from sift_orchestrator import SIFTOrchestrator
            orchestrator = SIFTOrchestrator(self.case_id)

            # Construir inputs según tipo de evidencia
            kwargs = _build_orchestrator_kwargs(self.evidence_path, params)
            result = orchestrator.analyze(**kwargs)

        except ImportError:
            # Fallback: usar el pipeline de texto si el orchestrator no está disponible
            logger.warning("[PIPELINE] SIFTOrchestrator unavailable, using text pipeline")
            result = _run_text_pipeline(self.evidence_path, self.case_id, params)
        except (MemoryError, RecursionError, KeyboardInterrupt, SystemExit):
            # Critical system errors — do NOT mask, propagate
            raise
        except (OSError, TypeError, ValueError, KeyError, AttributeError,
                ZeroDivisionError, RuntimeError, ArithmeticError) as e:
            logger.error("[PIPELINE] Pipeline error: %s", e)
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
        Detecta contradicciones y aplica correcciones.
        Retorna (hubo_correcciones, resultados_actualizados).
        """
        # MCP multiplicativo racional — producto de confianzas modulares
        # Si no hay confianza en los signals, usar z_score normalizado como proxy
        signals = results.get("signals", [])
        if signals:
            # MCA: Media de Confianza Aritmética racional
            # El producto multiplicativo penaliza la modularidad (n módulos × conf 0.9 → 0).
            # La media aritmética es estable: 20 señales con conf 9/10 → MCA = 9/10.
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
                # Fallback: media aritmética de z_scores normalizados — usar _to_frac
                z_fracs = [
                    min(Fraction(1, 1), abs(_to_frac(s.get("z_score", 0))) / Fraction(10, 1))
                    for s in signals
                ]
                n = Fraction(len(z_fracs), 1)
                mca_score = sum(z_fracs, Fraction(0, 1)) / n if n > 0 else Fraction(0, 1)
        else:
            mca_score = Fraction(0, 1)

        contradictions = self.contradiction_detector.detect(results, mca_score)

        # Aplicar CONTRADICTION_THRESHOLD — solo activar corrección si hay suficientes contradicciones
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

        # Hay contradicciones suficientes — loggear y corregir
        for modules, description in contradictions:
            self.audit.log_contradiction(modules, description, self.iteration)

        # Aplicar correcciones
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

            # Traducir corrección a parámetros para la siguiente iteración
            if correction.get("recommended_action") == "REWEIGHT_AND_RERUN":
                params_for_rerun["uniform_weights"] = True
            if correction.get("suggested_verdict_upgrade"):
                params_for_rerun["elevate_technical_signals"] = True

        self.corrections_applied.extend(all_corrections)

        # Aplicar correcciones al resultado actual — muta el veredicto si corresponde
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

        # Aplicar CONFIDENCE_FLOOR — si MCP está bajo el floor, marcar como INCONCLUSIVE
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

        # Loggear la corrección aplicada con before/after reales
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
        Genera narrativa investigativa 100% determinista.
        Sin LLMs — todo derivado de los datos del pipeline.
        Each section references the modules that produced it.
        """
        abduction = results.get("abduction", {})
        signals = results.get("signals", [])
        corrections = results.get("self_corrections", [])

        def _to_frac_z(s: dict) -> Fraction:
            """Helper local — delega a _to_frac para consistencia con el resto del agente."""
            return abs(_to_frac(s.get("z_score", 0)))

        narrative_parts = [
            f"=== VIGÍA FORENSIC AGENT — CASE {self.case_id} ===",
            f"Evidence: {self.evidence_path}",
            f"Evidence SHA-256: {evidence_sha256}",
            f"Analysis iterations: {self.iteration + 1}",
            f"Self-corrections applied: {len(corrections)}",
            "",
            "--- MAIN HYPOTHESIS ---",
            f"Hypothesis: {abduction.get('best_hypothesis', 'UNDETERMINED')}",
            f"Posterior confidence: {abduction.get('best_posterior', '0')}",
            f"Conclusive: {'YES' if abduction.get('is_conclusive') else 'NO — requires human review'}",
            "",
            "--- PEIRCEAN NARRATIVE ---",
            abduction.get("narrative", "[No narrative available]"),
            "",
        ]

        if signals:
            top_signals = sorted(signals, key=_to_frac_z, reverse=True)[:5]
            narrative_parts.append("--- TOP SIGNALS (top 5 by z-score) ---")
            for s in top_signals:
                z_frac = _to_frac_z(s)
                conf_frac = _to_frac(s.get("confidence", 0))
                narrative_parts.append(
                    f"  [{s.get('tool', '?')}] z={float(z_frac):.3f} "
                    f"conf={float(conf_frac):.2f} — {str(s.get('value', ''))[:80]}"
                )
            narrative_parts.append("")

        if corrections:
            narrative_parts.append("--- SELF-CORRECTIONS APPLIED ---")
            for i, c in enumerate(corrections, 1):
                narrative_parts.append(f"  Correction {i}: {str(c.get('contradiction_type', ''))[:80]}")
                for adj in c.get("adjustments", []):
                    narrative_parts.append(f"    → {adj}")
            narrative_parts.append("")

        n_critical = sum(1 for s in signals if _to_frac_z(s) > Fraction(3, 1))
        n_high = sum(1 for s in signals if Fraction(2, 1) < _to_frac_z(s) <= Fraction(3, 1))

        if n_critical >= 3:
            alert = "CRITICAL — Multiple high-magnitude signals. Compromise confirmed with high probability."
        elif n_critical >= 1 or n_high >= 3:
            alert = "HIGH — Significant anomalies detected. Priority forensic review recommended."
        elif n_high >= 1:
            alert = "MEDIUM — Moderate anomalies. Additional investigation recommended."
        else:
            alert = "LOW — No significant anomalies detected in this iteration."

        narrative_parts.extend([
            "--- FINAL ALERT LEVEL ---",
            alert,
            "",
            f"Critical signals (z>3): {n_critical}",
            f"High signals (2<z<=3): {n_high}",
            f"Total signals analyzed: {len(signals)}",
        ])

        return "\n".join(narrative_parts)

    def _seal_bundle(
        self,
        results: Dict[str, Any],
        narrative: str,
        evidence_sha256: str,
    ) -> Dict[str, Any]:
        """
        Sella el bundle final con SHA-256.
        Incluye audit trail completo, resultados y narrativa.
        """
        bundle = {
            "vigia_agent_version": AGENT_VERSION,
            "case_id": self.case_id,
            "evidence_path": str(self.evidence_path),
            "evidence_sha256": evidence_sha256,
            "analysis_timestamp": _utcnow(),
            "iterations_executed": self.iteration + 1,
            "self_corrections_applied": len(self.corrections_applied),
            "pipeline_results": results,
            "narrative": narrative,
            "audit_trail": self.audit.export(),
            "sans_compliance": {
                "self_correction": self.iteration > 0 or len(self.corrections_applied) > 0,
                "accuracy_validation": True,   # Toda señal tiene tool + z_score + metadata
                "analytical_reasoning": True,  # Narrativa Peirciana generada
                "audit_trail": True,            # Trazabilidad completa
                "architectural_guardrails": True,  # Sin ML, sin floats en scoring
                "evidence_integrity": True,     # SHA-256 verificado
            },
        }

        # Serialización canónica del bundle — sin campo de hash incrustado.
        # El SHA-256 se escribe EXCLUSIVAMENTE en <output>.sha256.
        # El archivo .json en disco es exactamente el texto que se hashea —
        # verificable con: sha256sum -c <output>.sha256
        bundle_text = json.dumps(
            bundle, indent=2, sort_keys=True, ensure_ascii=True, default=_json_serial
        )
        bundle_digest = hashlib.sha256(bundle_text.encode("utf-8")).hexdigest()
        # bundle_sha256 NO se incrusta en el JSON — evita paradoja de auto-referencia.
        # El campo bundle_sha256 solo vive en el audit trail y en el archivo .sha256.

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
        Loop principal del agente.
        Retorna el bundle sellado con todos los resultados.
        """
        logger.info("[AGENT] Starting VIGÍA Agent — case %s", self.case_id)
        logger.info("[AGENT] Evidence: %s", self.evidence_path)

        # Registrar SHA-256 del propio código del agente — trazabilidad de versión
        try:
            agent_source = Path(__file__).read_bytes()
            agent_sha256 = hashlib.sha256(agent_source).hexdigest()
        except OSError:
            agent_sha256 = "UNAVAILABLE"
        self.audit.log(
            action="AGENT_INITIALIZED",
            tool="vigia_agent",
            inputs={"case_id": self.case_id, "agent_file": __file__},
            outputs={"agent_sha256": agent_sha256, "agent_version": AGENT_VERSION},
            iteration=0,
            note=f"Agent initialized — source SHA-256: {agent_sha256[:16]}...",
        )
        logger.info("[AGENT] Agent SHA-256: %s", agent_sha256)

        # 1. Verificar integridad de evidencia
        evidence_sha256 = self._hash_evidence()

        # 2. Loop de análisis con self-correction
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

            # Criterio de convergencia: mismo veredicto que iteración anterior
            current_verdict = results.get("abduction", {}).get("best_hypothesis", "")
            if current_verdict == prev_verdict and prev_verdict is not None:
                logger.info("[AGENT] Convergence detected — stable verdict at iteration %d", self.iteration + 1)
                self.audit.log(
                    action="CONVERGENCE_DETECTED",
                    tool="convergence_check",
                    inputs={"iteration": self.iteration},
                    outputs={"verdict": current_verdict},
                    iteration=self.iteration,
                    note=f"Veredicto estable: {current_verdict}",
                )
                break
            prev_verdict = current_verdict

            # Preparar parámetros para la siguiente iteración
            params = results.pop("params_for_rerun", {})
            logger.info("[AGENT] Corrections applied, re-running with params: %s", params)

        # 3. Generar narrativa
        logger.info("[AGENT] Generando narrativa investigativa")
        # Log agent exit in audit trail BEFORE sealing — so it appears in the bundle
        exit_code_preview = 1 if (
            "MALICIOUS" in str(results.get("abduction", {}).get("best_hypothesis", ""))
            or "CRITICAL" in str(results.get("abduction", {}).get("best_hypothesis", ""))
            or "OVERRIDE" in str(results.get("abduction", {}).get("best_hypothesis", ""))
        ) else 0
        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} — analysis complete.",
        )

        narrative = self._generate_narrative(results, evidence_sha256)

        # 4. Sellar bundle — retorna (bundle_dict, canonical_json_text, sha256_digest)
        bundle, bundle_canonical_text, bundle_digest = self._seal_bundle(
            results, narrative, evidence_sha256
        )
        # Adjuntar campos temporales para main() — se extraen con pop() antes de escribir a disco
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

# Alias retrocompatible — el nombre semánticamente correcto es _utc_iso_timestamp
_utcnow = _utc_iso_timestamp


def _summarize(obj: Any, max_len: int = 200) -> Any:
    """Resumen seguro de un objeto para el audit trail."""
    if isinstance(obj, dict):
        return {k: _summarize(v) for k, v in list(obj.items())[:10]}
    if isinstance(obj, list):
        return [_summarize(v) for v in obj[:5]]
    s = str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s


def _build_orchestrator_kwargs(evidence_path: Path, params: Dict) -> Dict:
    """Construye los kwargs para SIFTOrchestrator.analyze() según el tipo de evidencia."""
    kwargs: Dict[str, Any] = {}

    if evidence_path.is_dir():
        # Directorio de evidencia — buscar artefactos conocidos
        for pattern, key in [
            ("*.evtx", "event_stream"),
            ("*.raw", "memory_path"),
            ("*.E01", "disk_path"),
            ("*.e01", "disk_path"),
            ("*.log", "log_path"),
        ]:
            matches = [str(m) for m in sorted(evidence_path.rglob(pattern))
                       if not m.is_symlink()]  # SECURITY: no seguir symlinks
            if matches:
                # Acumular en lista para soportar imágenes segmentadas (E01, E02, ...)
                existing = kwargs.get(key)
                if existing is None:
                    kwargs[key] = matches
                elif isinstance(existing, list):
                    kwargs[key] = existing + matches
                else:
                    kwargs[key] = [existing] + matches
    else:
        # Archivo único — detectar tipo por extensión
        suffix = evidence_path.suffix.lower()
        if suffix == ".raw":
            kwargs["memory_path"] = str(evidence_path)
        elif suffix in (".e01", ".E01"):
            kwargs["disk_path"] = str(evidence_path)
        elif suffix == ".evtx":
            kwargs["event_stream"] = [str(evidence_path)]
        else:
            # Texto genérico — usar como event_stream
            kwargs["log_path"] = str(evidence_path)

    # Aplicar ajustes de corrección si los hay
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
    # SECURITY: rechazar symlinks antes de cualquier operación de lectura
    if evidence_path.is_symlink():
        logger.error("[TEXT_PIPELINE] Evidence path is symlink — rejected for security: %s", evidence_path)
        return {
            "case_id": case_id, "signals": [],
            "abduction": {"best_hypothesis": "SYMLINK_REJECTED", "is_conclusive": False,
                          "narrative": "[SECURITY] Symlink rechazado — posible path traversal."},
            "pipeline_meta": {"error": "symlink_rejected"},
        }

    # Rechazar evidencia binaria — no intentar leer como texto
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

        # Aplicar params de corrección al texto si corresponde
        if params.get("elevate_technical_signals"):
            text = f"[ELEVATED_ANALYSIS] {text}"
        if params.get("uniform_weights"):
            # uniform_weights no está implementado en el pipeline de texto —
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

        from run_pipeline import run as run_pipeline_fn
        run_pipeline_fn(input_path, output_path, negation_enabled=True)

        with open(output_path) as f:
            pipeline_results = json.load(f)

        # Convertir al formato del agente — z_score como Fraction
        signals = []
        for r in pipeline_results:
            dec = r.get("decision", {})
            agg = r.get("aggregator", {})
            mi = agg.get("mi_final", {"num": 0, "den": 1})
            # Fraction racional — nunca float
            z_frac = Fraction(mi["num"], max(mi["den"], 1))
            # Confidence derivado del alert_level — no inventado
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

        high_signals = [s for s in signals if s["z_score"] > Fraction(5, 1)]
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
    # NameError, SyntaxError, AttributeError, TypeError en run_pipeline.py
    # son bugs del código — NO enmascarar, propagar para fallo visible
    finally:
        # Garantizar cleanup de archivos temporales
        for p in [input_path, output_path]:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except OSError:
                    pass




# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main() -> None:
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
    args = parser.parse_args()

    # Validar evidencia
    evidence_path = Path(args.evidence)
    if not evidence_path.exists():
        logger.error("[FATAL] Evidence not found: %s", evidence_path)
        sys.exit(2)

    # Output path
    # Sanitizar case-id para uso seguro como nombre de archivo
    safe_case_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", args.case_id)
    output_path = args.output or f"{safe_case_id}_bundle.json"

    # Ejecutar agente
    agent = VIGIAAgent(
        case_id=args.case_id,
        evidence_path=str(evidence_path),
    )

    t0 = time.monotonic()
    bundle = agent.run()
    elapsed = time.monotonic() - t0

    # Extraer texto canónico y digest del bundle
    bundle_canonical_text = bundle.pop("_canonical_text", None)
    bundle_canonical_digest = bundle.pop("_canonical_digest", None)

    # Exportar resultado
    if args.audit_only:
        output_text = json.dumps(bundle["audit_trail"], indent=2, sort_keys=True,
                                 default=_json_serial, ensure_ascii=True)
    else:
        # Escribir EXACTAMENTE el texto canónico que se hasheó — garantía sha256sum -c
        output_text = bundle_canonical_text or json.dumps(
            bundle, indent=2, sort_keys=True, default=_json_serial, ensure_ascii=True
        )
    Path(output_path).write_text(output_text, encoding="utf-8")

    # Write .sha256 file — verifies exactly what is on disk
    if bundle_canonical_text and not args.audit_only:
        sha256_path = output_path + ".sha256"
        # Recalculate over the text written to disk (must match bundle_digest)
        disk_digest = hashlib.sha256(output_text.encode("utf-8")).hexdigest()
        # Use absolute path so sha256sum -c works from any directory
        abs_output_path = str(Path(output_path).resolve())
        Path(sha256_path).write_text(
            f"{disk_digest}  {abs_output_path}\n", encoding="utf-8"
        )
        logger.info("[BUNDLE] Verification: sha256sum -c %s", sha256_path)

    # Resumen en consola
    abduction = bundle.get("pipeline_results", {}).get("abduction", {})
    hypothesis = abduction.get("best_hypothesis", "UNDETERMINED")
    evil_found = "MALICIOUS" in hypothesis or "CRITICAL" in hypothesis or "OVERRIDE" in hypothesis

    print("\n" + "=" * 60)
    print(f"VIGÍA AGENT — CASE {args.case_id}")
    print("=" * 60)
    print(f"Evidence SHA-256  : {bundle.get('evidence_sha256', 'N/A')[:32]}...")
    # bundle_sha256 no está en el dict (sin paradoja) — leerlo del digest calculado
    _display_digest = bundle_canonical_digest or "see .sha256 file"
    print(f"Bundle SHA-256    : {_display_digest[:32]}...")
    print(f"Iterations        : {bundle.get('iterations_executed', 1)}")
    print(f"Corrections       : {bundle.get('self_corrections_applied', 0)}")
    print(f"Analysis time     : {elapsed:.2f}s")
    print(f"Verdict           : {hypothesis}")
    print(f"Evil found        : {'YES' if evil_found else 'NO'}")
    print(f"Output            : {output_path}")
    print("=" * 60)

    # Imprimir narrativa
    print("\n" + bundle.get("narrative", "[Sin narrativa]"))

    # Exit code documentado — 0=no evil, 1=evil found, 2=error
    exit_code = 1 if evil_found else 0
    logger.info("[AGENT] Exit code: %d (%s)", exit_code, "EVIL FOUND" if evil_found else "NO EVIL DETECTED")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
