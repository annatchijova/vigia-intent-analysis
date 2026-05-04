#!/usr/bin/env python3
"""
vigia/core/execution_logger.py

Logger estructurado JSONL para Agent Execution Logs.
Entregable obligatorio del SANS Find Evil! Hackathon 2026.

Cada evento registra:
  timestamp UTC ISO 8601, phase (IR), peirce_layer,
  artifact, finding, intent_hypothesis, devil_advocate,
  tool_called, verdict_partial, _event_hash (SHA-256 parcial),
  _seq (número de secuencia, canonicalizado como int)

El archivo se genera en data/logs/{case_id}_execution.jsonl.
Formato: JSONL (una línea JSON por evento), sort_keys=True, ensure_ascii=True.
Apto para cadena de custodia Daubert.

Autor: Kimi (template), Claude (integración), Colectivo VIGÍA
Versión: 2.3
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from typing import Any, Dict, Optional


# ── Utilidades canónicas ──────────────────────────────────────────────────

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonicalize(obj: Any) -> Any:
    """
    Canonicalización unificada para cadena de custodia.
    Prefijos de dominio explícitos para evitar colisión de tipos (Gemini V17).
    Debe ser idéntica en todo el pipeline (run_pipeline, evaluate_detector, execution_logger).
    """
    if isinstance(obj, bool):
        return "true:bool" if obj else "false:bool"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, str):
        return f"str:{obj}"
    if obj is None:
        return "null:none"
    if isinstance(obj, float):
        if obj != obj:  # NaN
            return "nan:float"
        return f"{obj:.8f}:float"
    if isinstance(obj, Fraction):
        return {"num": obj.numerator, "den": obj.denominator}
    if isinstance(obj, Decimal):
        return f"{float(obj):.8f}:float"
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, dict):
        return {k: _canonicalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]
    return str(obj)


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

    def __init__(self, case_id: str, output_dir: str = "data/logs",
                 deterministic_timestamp: Optional[str] = None) -> None:
        self.case_id = case_id
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log_path = os.path.join(output_dir, f"{case_id}_execution.jsonl")
        self._event_count = 0
        # Timestamp fijo para runs de evaluación deterministas; real para producción
        self._session_start = deterministic_timestamp or _utcnow_iso()
        self._bundle_hash_partial = "0" * 16

        # Evento SESSION_START — primer evento de la cadena
        self._write({
            "event_type": "SESSION_START",
            "case_id": case_id,
            "session_start": self._session_start,
            "log_version": "1.0",
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
        canonical = json.dumps(_canonicalize(event), sort_keys=True, ensure_ascii=True)
        event_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        bundle_input = f"{self._bundle_hash_partial}:{event_hash}"
        self._bundle_hash_partial = hashlib.sha256(
            bundle_input.encode("utf-8")
        ).hexdigest()[:16]

        event["_event_hash"] = event_hash
        event["_bundle_hash_partial"] = self._bundle_hash_partial

        # _local_timestamp agregado DESPUÉS del hash — es display-only para el perito.
        # No afecta el hash de integridad. En Argentina: -03:00, en UTC: +00:00.
        event["_local_timestamp"] = datetime.now().astimezone().isoformat()

        # Recanonicalizar con todos los campos para la línea final del JSONL
        final_line = json.dumps(_canonicalize(event), sort_keys=True, ensure_ascii=True)
        # P1-17: validar tamaño antes de escribir — O_APPEND atómico solo < PIPE_BUF (4KB)
        _PIPE_BUF = 4096
        _encoded = (final_line + "\n").encode("utf-8")
        if len(_encoded) > _PIPE_BUF:
            # Truncar el evento y agregar nota de truncado
            _trunc_event = {"_truncated": True, "_original_size": len(_encoded),
                            "event_type": event.get("event_type", "UNKNOWN"),
                            "_local_timestamp": event.get("_local_timestamp")}
            _encoded = (json.dumps(_trunc_event, sort_keys=True) + "\n").encode("utf-8")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(_encoded.decode("utf-8"))

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
            ).hexdigest()[:12],
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
