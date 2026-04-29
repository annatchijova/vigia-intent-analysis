# License, or (at your option) any later version.

"""
vigia/core/execution_logger.py

Logger estructurado JSONL para Agent Execution Logs.
Entregable obligatorio del SANS Find Evil! Hackathon 2026.

Cada evento registra:
- timestamp UTC ISO 8601
- phase: IR phase (RECONNAISSANCE, LATERAL_MOVEMENT, etc.)
- peirce_layer: FIRSTNESS | SECONDNESS | THIRDNESS
- artifact: identificador del artefacto analizado
- finding: hallazgo forense
- intent_hypothesis: hipotesis de intencion (opcional)
- devil_advocate: hipotesis alternativa benigna (opcional)
- tool_called: herramienta MCP invocada (opcional)
- verdict_partial: veredicto parcial si aplica
- bundle_hash_partial: hash parcial del bundle en ese momento

El archivo se genera en data/logs/{case_id}_execution.jsonl
y es apto para auditoria Daubert (sort_keys=True, timestamps UTC).
"""

import json
import os
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonicalize(obj: Any) -> Any:
    """Convierte tipos no serializables a formas canonicas."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        return f"{obj:.8f}"
    if isinstance(obj, Decimal):
        return f"{float(obj):.8f}"
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.hex()
    if obj is None:
        return "null"
    if isinstance(obj, dict):
        return {k: _canonicalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]
    return str(obj)


class VigiaExecutionLogger:
    """
    Logger JSONL de ejecucion forense para trazabilidad Daubert.

    Uso:
        logger = VigiaExecutionLogger("VIGIA-2026-DEMO-008")
        logger.log_event(
            phase="LATERAL_MOVEMENT",
            peirce_layer="SECONDNESS",
            artifact="LOG-001",
            finding="VIM signature in auth.log slack space",
            intent_hypothesis="insider_log_tampering",
            devil_advocate="Legitimate admin editing log for documentation",
        )
        logger.log_verdict("MALICE", 92, reason_code="REJECT_POSTERIOR")
    """

    def __init__(self, case_id: str, output_dir: str = "data/logs") -> None:
        self.case_id = case_id
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.log_path = os.path.join(output_dir, f"{case_id}_execution.jsonl")
        self._event_count = 0
        self._session_start = _utcnow_iso()
        # Evento de inicio de sesion
        self._write({
            "event_type": "SESSION_START",
            "case_id": case_id,
            "session_start": self._session_start,
            "log_version": "1.0",
            "standard": "SANS_FIND_EVIL_2026",
        })

    def _write(self, event: Dict[str, Any]) -> None:
        """Escribe un evento al archivo JSONL."""
        self._event_count += 1
        event["_seq"] = self._event_count
        event["timestamp"] = _utcnow_iso()
        # Hash del evento para integridad de la cadena de log
        canonical = json.dumps(_canonicalize(event), sort_keys=True,
                               ensure_ascii=True)
        event["_event_hash"] = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()[:16]
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(_canonicalize(event),
                               sort_keys=True, ensure_ascii=True) + "\\n")

    def log_event(
        self,
        phase: str,
        peirce_layer: str,
        artifact: str,
        finding: str,
        intent_hypothesis: Optional[str] = None,
        devil_advocate: Optional[str] = None,
        tool_called: Optional[str] = None,
        confidence: Optional[float] = None,
        verdict_partial: Optional[str] = None,
    ) -> None:
        """Registra un evento de analisis forense."""
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
        self._write(event)

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
            "parameters_hash": hashlib.sha256(
                json.dumps(_canonicalize(parameters),
                           sort_keys=True).encode()
            ).hexdigest()[:16],
            "result_summary": result_summary,
        }
        if duration_ms is not None:
            event["duration_ms"] = duration_ms
        self._write(event)

    def log_verdict(
        self,
        verdict: str,
        confidence: float,
        reason_code: str = "UNKNOWN",
        bundle_hash: Optional[str] = None,
        carnegie_pattern: Optional[str] = None,
    ) -> None:
        """Registra el veredicto final."""
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
        self._write(event)

    def log_abstain(self, reason_code: str, explanation: str) -> None:
        """Registra una abstension epistemica — importante para Daubert."""
        self._write({
            "event_type": "EPISTEMIC_ABSTENTION",
            "reason_code": reason_code,
            "explanation": explanation,
            "daubert_note": (
                "ABSTAIN is a valid forensic output — indicates honest "
                "uncertainty rather than forced conclusion."
            ),
        })

    @property
    def log_file(self) -> str:
        return self.log_path
'''

# ─────────────────────────────────────────────────────────────────────────────
# Aplicar los tres fixes
# ─────────────────────────────────────────────────────────────────────────────

files = {
    "vigia/security/__init__.py": SECURITY_INIT,
    "vigia/tools/forensic_db.py": FORENSIC_DB_PY,
    "vigia/core/execution_logger.py": EXECUTION_LOGGER_PY,
}

print("Aplicando fixes P0...")
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    try:
        ast.parse(content)
        print(f"OK (sintaxis valida): {path}")
    except SyntaxError as e:
        print(f"ERROR sintaxis: {path}: {e}")

# Crear directorio de logs
os.makedirs("data/logs", exist_ok=True)
print("OK: data/logs/ creado")

print("\nFixes aplicados. Verificar con:")
print("  python3 -c \"import vigia.security; print(vigia.security.trust_decay)\"")
print("  python3 -c \"from vigia.tools.forensic_db import get_patterns; print(get_patterns())\"")
print("  python3 -c \"from vigia.core.execution_logger import VigiaExecutionLogger; print('OK')\"")
