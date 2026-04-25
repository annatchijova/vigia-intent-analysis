# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vigia/core/shadow_mode.py
─────────────────────────────────────────────────────────────────────────────
ShadowModeLogger — Modo Sombra VIGÍA

Loggea en paralelo el resultado del sistema MCP heurístico VIEJO
y el resultado del LikelihoodEngine NUEVO.

PROPÓSITO:
    Transición segura: el sistema MCP sigue siendo el veredicto operativo
    hasta que el LikelihoodEngine esté calibrado y auditado.
    El shadow log permite medir la divergencia ANTES de hacer el cutover.

FORMATO DEL LOG:
    Cada fila es un JSON-line (JSONL) con:
        - timestamp
        - case_id
        - mcp_verdict (resultado heurístico)
        - lr_record (ForensicRecord del LikelihoodEngine)
        - divergence (¿difieren los veredictos?)
        - ground_truth (si disponible, para métricas de validación)

INTEGRACIÓN:
    Activar con VIGIA_SHADOW_MODE=true (variable de entorno).
    El log se escribe en VIGIA_SHADOW_LOG_PATH (default: /tmp/vigia_shadow.jsonl).

    En el bridge MCP, después de cada herramienta que retorna resultado,
    llamar:
        shadow_logger.log(case_id, mcp_result, lr_record, ground_truth)

DAUBERT:
    El shadow log es evidencia de validación continua.
    Permite reportar la Tasa de Error Conocida requerida por Daubert.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import os
import threading
import hashlib
import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from vigia.core.likelihood_ratio import ForensicRecord

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

_ENV_ENABLED = "VIGIA_SHADOW_MODE"
_ENV_LOG_PATH = "VIGIA_SHADOW_LOG_PATH"
# P1: /tmp es world-writable — usar directorio seguro bajo EVIDENCE_BASE_DIR
_EVIDENCE_BASE = os.environ.get("VIGIA_EVIDENCE_DIR", "").strip()
if not _EVIDENCE_BASE:
    import tempfile
    _EVIDENCE_BASE = tempfile.mkdtemp(prefix="vigia_evidence_")
    os.chmod(_EVIDENCE_BASE, 0o700)
_DEFAULT_LOG_PATH = os.path.join(_EVIDENCE_BASE, "shadow", "vigia_shadow.jsonl")

_MAX_LOG_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB — rotación automática


# ---------------------------------------------------------------------------
# ShadowEntry — una fila del log
# ---------------------------------------------------------------------------

class ShadowEntry:
    """Representa una comparación MCP vs LR para un caso."""

    def __init__(
        self,
        case_id: str,
        mcp_verdict: str,
        mcp_score: float,
        lr_record: ForensicRecord,
        ground_truth: Optional[str] = None,
        extra: Optional[Dict] = None,
    ) -> None:
        self.case_id = case_id
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        self.mcp_verdict = mcp_verdict
        self.mcp_score = mcp_score
        self.lr_record = lr_record
        self.ground_truth = ground_truth
        self.extra = extra or {}

    @property
    def lr_verdict(self) -> str:
        """Veredicto del LikelihoodEngine basado en probabilidad posterior."""
        p = self.lr_record.posterior_probability
        if p >= 0.85:
            return "FABRICATED"
        if p >= 0.60:
            return "SUSPICIOUS"
        if p >= 0.40:
            return "BORDERLINE"
        return "AUTHENTIC"

    @property
    def diverges(self) -> bool:
        """True si MCP y LR difieren en sus veredictos binarios."""
        mcp_fab = self.mcp_verdict in ("FABRICATED", "HIGH_SUSPICION", "SUSPICION")
        lr_fab = self.lr_verdict in ("FABRICATED", "SUSPICIOUS")
        return mcp_fab != lr_fab

    def to_dict(self) -> Dict[str, Any]:
        # P1: Datos crudos para hashing forense (sin round)
        return {
            "case_id": self.case_id,
            "timestamp": self.timestamp,
            "mcp": {
                "verdict": self.mcp_verdict,
                "score": self.mcp_score,  # crudo
            },
            "lr": {
                "record_id": self.lr_record.record_id,
                "posterior_probability": self.lr_record.posterior_probability,  # crudo
                "lr_combined": self.lr_record.lr_combined,  # crudo
                "enfsi_label": self.lr_record.enfsi_label,
                "verdict": self.lr_verdict,
                "correction_factor": self.lr_record.correction_factor,  # crudo
            },
            "diverges": self.diverges,
            "ground_truth": self.ground_truth,
            "extra": self.extra,
        }

    def to_dict_display(self) -> Dict[str, Any]:
        """Versión redondeada para display humano (NO para hashing)."""
        return {
            "case_id": self.case_id,
            "timestamp": self.timestamp,
            "mcp": {
                "verdict": self.mcp_verdict,
                "score": round(self.mcp_score, 6),
            },
            "lr": {
                "record_id": self.lr_record.record_id,
                "posterior_probability": round(self.lr_record.posterior_probability, 6),
                "lr_combined": round(self.lr_record.lr_combined, 6),
                "enfsi_label": self.lr_record.enfsi_label,
                "verdict": self.lr_verdict,
                "correction_factor": round(self.lr_record.correction_factor, 6),
            },
            "diverges": self.diverges,
            "ground_truth": self.ground_truth,
            "extra": self.extra,
        }

    def to_jsonl(self) -> str:
        # P1: El JSONL es para humanos (display), pero el HMAC se calcula sobre crudo
        return json.dumps(self.to_dict_display(), ensure_ascii=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# ShadowModeLogger
# ---------------------------------------------------------------------------

class ShadowModeLogger:
    """
    Logger thread-safe para el modo sombra de VIGÍA.

    Uso:
        logger = ShadowModeLogger()
        if logger.enabled:
            logger.log(
                case_id="case_002",
                mcp_verdict="SUSPICION",
                mcp_score=0.72,
                lr_record=forensic_record,
                ground_truth="FABRICATED",
            )

    El log se puede leer con ShadowModeLogger.read_log() o con jq/grep.
    """

    def __init__(
        self,
        log_path: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self._lock = threading.Lock()

        # Enabled: variable de entorno > parámetro > default False
        if enabled is not None:
            self.enabled = enabled
        else:
            self.enabled = os.getenv(_ENV_ENABLED, "false").lower() in ("true", "1", "yes")

        # Path del log
        raw_path = log_path or os.getenv(_ENV_LOG_PATH, _DEFAULT_LOG_PATH)
        self._log_path = Path(raw_path)

        if self.enabled:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        case_id: str,
        mcp_verdict: str,
        mcp_score: float,
        lr_record: ForensicRecord,
        ground_truth: Optional[str] = None,
        extra: Optional[Dict] = None,
    ) -> Optional[ShadowEntry]:
        """
        Escribe una entrada en el shadow log.

        Returns:
            ShadowEntry si el logger está habilitado, None si no.
        """
        if not self.enabled:
            return None

        entry = ShadowEntry(
            case_id=case_id,
            mcp_verdict=mcp_verdict,
            mcp_score=mcp_score,
            lr_record=lr_record,
            ground_truth=ground_truth,
            extra=extra,
        )

        with self._lock:
            try:
                # Rotación si el log supera el límite
                if self._log_path.exists() and self._log_path.stat().st_size > _MAX_LOG_SIZE_BYTES:
                    self._rotate_log()

                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(entry.to_jsonl() + "\n")
            except OSError as e:
                # No debe interrumpir el flujo forense principal
                _shadow_warn(f"ShadowModeLogger: error escribiendo log: {e}")

        return entry

    def read_log(self, last_n: int = 100, verify_hmac: bool = False) -> list:
        """
        Lee las últimas N entradas del shadow log.
        Útil para análisis de divergencia en tiempo real.

        P1: límite de 10,000 líneas para evitar OOM.
        Si verify_hmac=True, valida la integridad de cada entrada.
        """
        last_n = min(last_n, 10_000)
        if not self._log_path.exists():
            return []

        with self._lock:
            with open(self._log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        entries = []
        for line in lines[-last_n:]:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    # Validación HMAC opcional
                    if verify_hmac and "_entry_hmac" in entry:
                        stored_hmac = entry.pop("_entry_hmac")
                        try:
                            import hmac, hashlib, json as _json, os as _os
                            key_hex = _os.environ.get("VIGIA_HMAC_KEY", "").strip()
                            if key_hex:
                                key = bytes.fromhex(key_hex)
                                canonical = _json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
                                expected = hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
                                del key
                                if not hmac.compare_digest(stored_hmac, expected):
                                    _shadow_warn(f"HMAC mismatch in shadow log entry — possible tampering: {entry.get('case_id', '?')}")
                                    continue
                        except Exception:
                            pass
                    entries.append(entry)
                except json.JSONDecodeError:
                    pass
        return entries

    def compute_divergence_stats(self) -> Dict[str, Any]:
        """
        Calcula estadísticas de divergencia MCP vs LR sobre el log completo.

        Retorna:
            total, divergent_count, divergence_rate, verdicts_by_ground_truth
        """
        entries = self.read_log(last_n=100_000)
        if not entries:
            return {"error": "Log vacío o no encontrado", "path": str(self._log_path)}

        total = len(entries)
        divergent = sum(1 for e in entries if e.get("diverges", False))

        # Por ground truth
        gt_stats: Dict[str, Dict[str, int]] = {}
        for e in entries:
            gt = e.get("ground_truth") or "UNKNOWN"
            if gt not in gt_stats:
                gt_stats[gt] = {"total": 0, "divergent": 0, "lr_correct": 0, "mcp_correct": 0}
            gt_stats[gt]["total"] += 1
            if e.get("diverges"):
                gt_stats[gt]["divergent"] += 1
                # ¿Quién tenía razón?
                lr_v = e.get("lr", {}).get("verdict", "")
                mcp_v = e.get("mcp", {}).get("verdict", "")
                fab_expected = gt in ("FABRICATED", "ADVERSARIAL")
                lr_fab = lr_v in ("FABRICATED", "SUSPICIOUS")
                mcp_fab = mcp_v in ("FABRICATED", "HIGH_SUSPICION", "SUSPICION")
                if lr_fab == fab_expected:
                    gt_stats[gt]["lr_correct"] += 1
                if mcp_fab == fab_expected:
                    gt_stats[gt]["mcp_correct"] += 1

        return {
            "total_entries": total,
            "divergent_count": divergent,
            "divergence_rate": round(divergent / total, 4) if total > 0 else 0.0,
            "by_ground_truth": gt_stats,
            "log_path": str(self._log_path),
        }

    def clear_log(self, force: bool = False) -> None:
        """
        Elimina el log actual. Usar sólo en testing.
        P1: Requiere force=True en producción para evitar borrado accidental.
        """
        if not force:
            _shadow_warn("clear_log() ignorado: pasá force=True para confirmar.")
            return
        with self._lock:
            if self._log_path.exists():
                self._log_path.unlink()

    def _rotate_log(self) -> None:
        """Renombra el log actual con timestamp antes de crear uno nuevo."""
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        rotated = self._log_path.with_suffix(f".{ts}.jsonl")
        self._log_path.rename(rotated)


def _shadow_warn(msg: str) -> None:
    """Warning interno que no interrumpe el flujo forense."""
    import sys
    print(f"[VIGIA_SHADOW_WARN] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Singleton global (configurable vía env vars)
# ---------------------------------------------------------------------------

shadow_logger = ShadowModeLogger()
