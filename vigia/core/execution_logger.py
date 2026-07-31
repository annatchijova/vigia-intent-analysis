#!/usr/bin/env python3
"""
vigia/core/execution_logger.py

Logger estructurado JSONL para Agent Execution Logs.
Entregable obligatorio del SANS Find Evil! Hackathon 2026.

Cada evento registra:
  timestamp UTC ISO 8601, phase (IR), peirce_layer,
  artifact, finding, intent_hypothesis, devil_advocate,
  tool_called, verdict_partial, _event_hash (SHA-256 completo, 64 hex
  desde log_version 1.1 — antes truncado a 16 hex),
  _seq (número de secuencia, canonicalizado como int)

El archivo se genera fuera de la evidencia: en ``VIGIA_EXECUTION_LOG_DIR`` si
está definido; si no, en ``$VIGIA_WORK_DIR/logs`` o en el estado privado del
usuario. Un llamador puede indicar explícitamente un directorio externo.
Formato: JSONL (una línea JSON por evento), sort_keys=True, ensure_ascii=True.
Apto para cadena de custodia Daubert.

Autor: Kimi (template), Claude (integración), Colectivo VIGÍA
Versión: 2.3
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, Optional

from vigia.security.output_boundary import validate_external_output_path


# ── Utilidades canónicas ──────────────────────────────────────────────────

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_execution_log_dir() -> str:
    """Return a private operational directory for derived JSONL logs.

    Execution logs are derived audit artifacts, not source evidence.  A
    repository-relative default made their destination depend on the process
    current working directory, which can itself be an evidence directory.
    """
    explicit = os.environ.get("VIGIA_EXECUTION_LOG_DIR", "").strip()
    if explicit:
        return explicit

    work_dir = os.environ.get("VIGIA_WORK_DIR", "").strip()
    if work_dir:
        return os.path.join(work_dir, "logs")

    state_root = os.environ.get("XDG_STATE_HOME", "").strip()
    if not state_root:
        state_root = os.path.join(os.path.expanduser("~"), ".local", "state")
    return os.path.join(state_root, "vigia", "logs")


def _validate_case_id(case_id: str) -> str:
    """Accept a case label, never a path fragment with write authority."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    if "\x00" in case_id:
        raise ValueError("case_id contains a null byte")
    if case_id in {".", ".."} or "/" in case_id or "\\" in case_id:
        raise ValueError("case_id must not contain path separators")
    return case_id


# P1-19: importar _canonicalize canónico — unificación de esquemas.
# R3-2: este logger usa la forma canónica como REPRESENTACIÓN ALMACENADA del
# JSONL (no solo como insumo de hash) — `_seq` se guarda como "N:int",
# strings verbatim, etc., y los consumidores parsean ese formato. El fix v2
# (prefijo "s:" en strings) es para la CANONICALIZACIÓN DE BUNDLES SELLADOS
# (bundle_builder / hash_chain / verificadores), NO para este log local de
# ejecución. Se fija a v1 para preservar el formato de almacenamiento estable.
from vigia.core.canonicalize import _canonicalize_v1 as _canonicalize  # noqa: F401


# ── Logger principal ──────────────────────────────────────────────────────

class VigiaExecutionLogger:
    """
    Logger JSONL de ejecución forense para trazabilidad Daubert.

    Uso:
        logger = VigiaExecutionLogger("VIGIA-REAL-006")
        logger.log_tool_call("read_evidence", {"artifact_id": "ART-001"}, "Email parsed")
        logger.log_event(
            phase="LATERAL_MOVEMENT",
            peirce_layer="SECONDNESS",
            artifact="ART-001",
            finding="Return-Path spoofeado",
            intent_hypothesis="spoofing_de_identidad",
            devil_advocate="Configuración de forwarding legítima",
            verdict_partial="INTENT",
        )
        logger.log_verdict("MALICE", 91, reason_code="REJECT_POSTERIOR_MALICE")
        print(logger.log_file)
    """

    def __init__(self, case_id: str, output_dir: Optional[str] = None,
                 deterministic_timestamp: Optional[str] = None) -> None:
        self.case_id = _validate_case_id(case_id)
        requested_dir = output_dir if output_dir is not None else _default_execution_log_dir()
        requested_path = os.path.join(
            requested_dir, f"{self.case_id}_execution.jsonl"
        )
        self.log_path = validate_external_output_path(
            requested_path, artifact_label="execution log"
        )
        self.output_dir = os.path.dirname(self.log_path)
        os.makedirs(self.output_dir, mode=0o750, exist_ok=True)
        # Check again after directory creation: an unexpected filesystem
        # substitution must not turn a validated parent into source evidence.
        self.log_path = validate_external_output_path(
            self.log_path, artifact_label="execution log"
        )
        self._event_count = 0
        # Timestamp fijo para runs de evaluación deterministas; real para producción
        self._session_start = deterministic_timestamp or _utcnow_iso()
        self._bundle_hash_partial = "0" * 64

        # Evento SESSION_START — primer evento de la cadena.
        # log_version 1.1: digests completos de 64 hex (antes 16 hex / 64 bits).
        # Los logs 1.0 existentes siguen siendo verificables con su esquema.
        self._write({
            "event_type": "SESSION_START",
            "case_id": self.case_id,
            "session_start": self._session_start,
            "log_version": "1.1",
            "standard": "SANS_FIND_EVIL_2026",
        })

    def _write(self, event: Dict[str, Any]) -> None:
        """Escribe un evento al archivo JSONL con hash de integridad."""
        self._event_count += 1
        event["_seq"] = self._event_count
        event["timestamp"] = _utcnow_iso()
        event["case_id"] = self.case_id

        # Hash calculado ANTES de _local_timestamp — garantiza que el hash
        # sea idéntico en cualquier zona horaria (Qwen: trazabilidad cruzada Daubert).
        # Digests COMPLETOS (64 hex): truncar a 16 hex deja 64 bits — colisión
        # birthday en ~2^32, atacable con GPU. Inaceptable para Daubert.
        canonical = json.dumps(_canonicalize(event), sort_keys=True, ensure_ascii=True)
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        bundle_input = f"{self._bundle_hash_partial}:{event_hash}"
        self._bundle_hash_partial = hashlib.sha256(
            bundle_input.encode("utf-8")
        ).hexdigest()

        event["_event_hash"] = event_hash
        event["_bundle_hash_partial"] = self._bundle_hash_partial

        # _local_timestamp agregado DESPUÉS del hash — es display-only para el perito.
        # No afecta el hash de integridad. En Argentina: -03:00, en UTC: +00:00.
        event["_local_timestamp"] = datetime.now().astimezone().isoformat()

        # Recanonicalizar con todos los campos para la línea final del JSONL
        final_line = json.dumps(_canonicalize(event), sort_keys=True, ensure_ascii=True)
        # Append directo al JSONL.
        # O_APPEND es atómico para writes < PIPE_BUF (4KB) en Linux/POSIX —
        # suficiente para líneas JSONL. El tempfile+rename anterior sobrescribía
        # el archivo en cada evento, perdiendo todo excepto el último (Kimi CRÍTICO 4).
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(final_line + "\n")

    def log_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result_summary: str,
        duration_ms: Optional[int] = None,
    ) -> None:
        """Registra una llamada a herramienta MCP."""
        event: Dict[str, Any] = {
            "event_type": "MCP_TOOL_CALL",
            "tool_name": tool_name,
            "parameters": parameters,
            "parameters_hash": hashlib.sha256(
                json.dumps(_canonicalize(parameters), sort_keys=True).encode()
            ).hexdigest(),
            "result_summary": result_summary,
        }
        if duration_ms is not None:
            event["duration_ms"] = duration_ms
        self._write(event)

    def log_event(
        self,
        phase: str,
        peirce_layer: str,
        artifact: str,
        finding: str,
        intent_hypothesis: Optional[str] = None,
        devil_advocate: Optional[str] = None,
        tool_called: Optional[str] = None,
        confidence: Optional[int] = None,
        verdict_partial: Optional[str] = None,
        pattern_detected: Optional[str] = None,
        pattern_weight_num: Optional[int] = None,
        pattern_weight_den: Optional[int] = None,
    ) -> None:
        """Registra un hallazgo forense con capas Peirce."""
        event: Dict[str, Any] = {
            "event_type": "FORENSIC_FINDING",
            "phase": phase,
            "peirce_layer": peirce_layer,
            "artifact": artifact,
            "finding": finding,
        }
        if intent_hypothesis:
            event["intent_hypothesis"] = intent_hypothesis
        if devil_advocate:
            event["devil_advocate"] = devil_advocate
        if tool_called:
            event["tool_called"] = tool_called
        if confidence is not None:
            event["confidence"] = confidence
        if verdict_partial:
            event["verdict_partial"] = verdict_partial
        if pattern_detected:
            event["pattern_detected"] = pattern_detected
        if pattern_weight_num is not None:
            # {num, den} — no float directo (I7). _prefix para display (Gemini V3/Qwen).
            event["_pattern_weight"] = {
                "num": pattern_weight_num,
                "den": pattern_weight_den or 1
            }
        self._write(event)

    def log_abductive_hypothesis(
        self,
        hypothesis_id: str,
        hypothesis: str,
        supporting_artifacts: list,
        devil_advocate: str,
        devil_strength: float,
        ockham_cost: int,
        phase: str = "ABDUCTION",
    ) -> None:
        """Registra inferencia abductiva (Capa 3 — Thirdness)."""
        self._write({
            "event_type": "ABDUCTIVE_HYPOTHESIS",
            "hypothesis_id": hypothesis_id,
            "hypothesis": hypothesis,
            "supporting_artifacts": supporting_artifacts,
            "devil_advocate": devil_advocate,
            "devil_strength": devil_strength,
            "ockham_cost": ockham_cost,
            "phase": phase,
        })

    def log_epistemic_check(
        self,
        posterior: str,
        consistency_score: float,
        consistency_threshold: float = 0.5,
        phase: str = "GOLDEN_RULE",
    ) -> None:
        """
        Registra la verificación epistémica (Golden Rule).
        Si posterior=FABRICATED pero consistency_score < threshold → ABSTAIN.
        """
        dissonance = (
            posterior in ("FABRICATED", "MALICE")
            and consistency_score < consistency_threshold
        )
        self._write({
            "event_type": "EPISTEMIC_CHECK",
            "phase": phase,
            "posterior": posterior,
            "consistency_score": consistency_score,
            "consistency_threshold": consistency_threshold,
            "dissonance_detected": dissonance,
            "abstention_triggered": dissonance,
            "check": "posterior=FABRICATED but consistency_score<threshold?",
            "note": (
                "Semantic dissonance detected — ABSTAIN triggered"
                if dissonance
                else "No semantic dissonance: posterior and consistency are aligned"
            ),
        })

    def log_risk_calculation(
        self,
        r_value: float,
        variables: Dict[str, float],
        formula: str,
        decision: str,
        reason_code: str,
        threshold_reject: float = 0.35,
        threshold_accept: float = 0.15,
        phase: str = "DECISION",
    ) -> None:
        """Registra el cálculo de riesgo acotado."""
        self._write({
            "event_type": "RISK_CALCULATION",
            "phase": phase,
            "formula": formula,
            "r_value": r_value,
            "variables": variables,
            "decision": decision,
            "reason_code": reason_code,
            "threshold_accept": threshold_accept,
            "threshold_reject": threshold_reject,
        })

    def log_mi_decision(
        self,
        mi: float,
        alert_level: str,
        thresholds: Dict[str, float],
        decision: str,
        reason_code: str,
        reason: str,
        phase: str = "DECISION",
    ) -> None:
        """Registra la decisión del motor MI-threshold (decision_layer.decide()).

        Distinto de log_risk_calculation (motor risk_bounded_layer, con
        variables P/D/S/I y fórmula r=P·(1+λD)·(1+γ(1-S))·(1+ω(1-I))):
        decision_layer no calcula drift, graph_stability, ni consistency_score
        — no rellenar esos campos con valores fabricados aquí (B-223).
        """
        self._write({
            "event_type": "MI_DECISION",
            "phase": phase,
            "engine": "vigia.core.decision_layer.RiskBoundedDecisionLayer",
            "mi": mi,
            "alert_level": alert_level,
            "thresholds": thresholds,
            "decision": decision,
            "reason_code": reason_code,
            "reason": reason,
        })

    def log_abstain(self, reason_code: str, explanation: str) -> None:
        """Registra una abstención epistémica — válida en Daubert."""
        self._write({
            "event_type": "EPISTEMIC_ABSTENTION",
            "reason_code": reason_code,
            "explanation": explanation,
            "daubert_note": (
                "ABSTAIN is a valid forensic output — indicates honest "
                "uncertainty rather than a forced conclusion."
            ),
        })

    def log_verdict(
        self,
        verdict: str,
        confidence: int,
        reason_code: str = "THRESHOLD_BASED",
        bundle_hash: Optional[str] = None,
        carnegie_pattern: Optional[str] = None,
        mitre_ttps: Optional[list] = None,
        devil_advocate_final: Optional[str] = None,
        devil_refuted_by: Optional[str] = None,
    ) -> None:
        """Registra el veredicto final — último evento de la cadena."""
        event: Dict[str, Any] = {
            "event_type": "FINAL_VERDICT",
            "verdict": verdict,
            "confidence": confidence,
            "reason_code": reason_code,
            "total_events": self._event_count,
            "session_start": self._session_start,
        }
        if bundle_hash:
            event["bundle_hash"] = bundle_hash
        if carnegie_pattern:
            event["carnegie_pattern"] = carnegie_pattern
        if mitre_ttps:
            event["mitre_ttps"] = mitre_ttps
        if devil_advocate_final:
            event["devil_advocate_final"] = devil_advocate_final
        if devil_refuted_by:
            event["devil_refuted_by"] = devil_refuted_by
        self._write(event)

    @property
    def log_file(self) -> str:
        return self.log_path

    @property
    def event_count(self) -> int:
        return self._event_count

    @property
    def bundle_hash(self) -> str:
        return self._bundle_hash_partial
