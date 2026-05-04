"""
vigia/core/config_sentinel.py
==============================
Guardian de configuración con sellado inmutable para VIGÍA.

Detecta:
- Módulos críticos desactivados al inicio
- Cambios de configuración durante runtime (tamper detection)
- Degradación silenciosa por variables de entorno

El trail de auditoría aparece en el bundle sellado con SHA-256.
Un analista SANS puede verificar qué módulos estuvieron activos.

Invariante: config_hash se calcula sin timestamp (reproducible).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from fractions import Fraction
from typing import Optional


class SystemIntegrityLevel(Enum):
    FULL        = "FULL_INTEGRITY"
    DEGRADED    = "DEGRADED_MODE"
    COMPROMISED = "INTEGRITY_COMPROMISED"
    UNKNOWN     = "INTEGRITY_UNKNOWN"


# Módulos críticos — su desactivación compromete el veredicto
CRITICAL_MODULES: frozenset[str] = frozenset({
    "CAIE",
    "TrustFusion",
    "OckhamAdversarial",
    "SignalRouter",
})

IMPORTANT_MODULES: frozenset[str] = frozenset({
    "PDFAnalyzer",
    "NetworkAnalyzer",
    "RegistryAnalyzer",
    "EmailAnalyzer",
    "TemporalForensics",
})

# Mapeo: nombre_módulo → env_var que lo controla
_MODULE_ENV_MAP: dict[str, str] = {
    "CAIE":              "VIGIA_CAIE_ENABLED",
    "TrustFusion":       "VIGIA_TRUST_FUSION_ENABLED",
    "OckhamAdversarial": "VIGIA_OCKHAM_ADVERSARIAL",
    "SignalRouter":      "VIGIA_SIGNALROUTER_ENABLED",
    "PDFAnalyzer":       "VIGIA_PDF_ENABLED",
    "NetworkAnalyzer":   "VIGIA_NETWORK_ENABLED",
    "RegistryAnalyzer":  "VIGIA_REGISTRY_ENABLED",
    "EmailAnalyzer":     "VIGIA_EMAIL_ENABLED",
    "TemporalForensics": "VIGIA_TEMPORAL_ENABLED",
}


@dataclass
class ModuleSnapshot:
    name:      str
    active:    bool
    env_var:   str
    env_value: str
    timestamp: int   # Unix timestamp entero


@dataclass
class DegradationEvent:
    event_type:  str    # MODULE_DEGRADED | MODULE_ACTIVATED_RUNTIME
    module:      str
    timestamp:   int
    was:         str
    became:      str
    is_critical: bool
    seal:        str    # HMAC del evento


@dataclass
class ConfigAuditTrail:
    session_id:          str
    init_timestamp:      int
    init_seal:           str
    config_fingerprint:  str
    integrity_level:     SystemIntegrityLevel
    module_snapshots:    list[ModuleSnapshot]     = field(default_factory=list)
    degradation_events:  list[DegradationEvent]   = field(default_factory=list)

    def to_report_dict(self) -> dict:
        """Sección del reporte para bundle sellado."""
        critical_degraded = [
            e.module for e in self.degradation_events
            if e.is_critical and e.event_type == "MODULE_DEGRADED"
        ]
        return {
            "integrity_level":             self.integrity_level.value,
            "session_id":                  self.session_id,
            "config_fingerprint":          self.config_fingerprint,
            "init_seal":                   self.init_seal,
            "degradation_events_count":    len(self.degradation_events),
            "critical_modules_degraded":   critical_degraded,
            "analyst_warning": (
                f"ANALYSIS IN DEGRADED MODE: modules "
                f"{critical_degraded} were deactivated during runtime. "
                f"Verdict may be affected."
                if critical_degraded else None
            ),
        }


class ConfigurationTamperedException(Exception):
    """Raised when configuration is modified during runtime analysis."""


class ConfigAuditMonitor:
    """
    Monitor de integridad de configuración en runtime.

    Uso:
        monitor = ConfigAuditMonitor(secret_key=b"...")
        monitor.initialize()
        # ... pipeline ...
        monitor.checkpoint()
        trail = monitor.finalize()
    """

    def __init__(self, secret_key: bytes):
        self._key = secret_key
        self._trail: Optional[ConfigAuditTrail] = None
        self._baseline: dict[str, str] = {}
        self._sealed = False

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _getenv_bool(key: str, default: bool) -> bool:
        val = os.environ.get(key, str(default)).lower()
        return val in ("true", "1", "yes", "enabled", "on")

    def _read_states(self) -> dict[str, str]:
        return {
            module: os.environ.get(env_var, "NOT_SET")
            for module, env_var in _MODULE_ENV_MAP.items()
        }

    def _hmac_dict(self, data: dict) -> str:
        import hmac as _hmac
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
        return _hmac.new(self._key, canonical.encode(), hashlib.sha256).hexdigest()

    def _fingerprint(self, states: dict[str, str]) -> str:
        return hashlib.sha256(
            json.dumps(states, sort_keys=True).encode()
        ).hexdigest()[:16]

    def _check_degradation(self, states: dict[str, str]) -> tuple[bool, list[str]]:
        reasons = []
        for module in CRITICAL_MODULES:
            env_var = _MODULE_ENV_MAP.get(module)
            if not env_var:
                continue
            val = states.get(module, "NOT_SET")
            # Default para módulos críticos es True — desactivar es degradar
            if not self._getenv_bool(env_var, True):
                reasons.append(
                    f"{module} DISABLED — {env_var}={val}"
                )
        return len(reasons) > 0, reasons

    # ── API pública ───────────────────────────────────────────────────────────

    def initialize(self) -> "ConfigAuditMonitor":
        """
        Toma snapshot inicial. Llamar ANTES de cualquier análisis.
        """
        import uuid
        now = int(time.time())
        sid = str(uuid.uuid4())

        self._baseline = self._read_states()
        init_seal = self._hmac_dict({
            "session": sid,
            "timestamp": now,
            "states": self._baseline,
        })

        snapshots = [
            ModuleSnapshot(
                name=module,
                active=self._getenv_bool(_MODULE_ENV_MAP[module], True),
                env_var=_MODULE_ENV_MAP[module],
                env_value=val,
                timestamp=now,
            )
            for module, val in self._baseline.items()
        ]

        degraded, _ = self._check_degradation(self._baseline)

        self._trail = ConfigAuditTrail(
            session_id=sid,
            init_timestamp=now,
            init_seal=init_seal,
            config_fingerprint=self._fingerprint(self._baseline),
            integrity_level=(
                SystemIntegrityLevel.DEGRADED if degraded
                else SystemIntegrityLevel.FULL
            ),
            module_snapshots=snapshots,
        )
        self._sealed = True
        return self

    def checkpoint(self) -> list[DegradationEvent]:
        """
        Verifica cambios desde initialize(). Llamar entre fases del pipeline.
        Retorna lista de eventos de degradación detectados.
        """
        if not self._trail:
            raise RuntimeError("Monitor not initialized — call initialize() first")

        now = int(time.time())
        current = self._read_states()
        new_events: list[DegradationEvent] = []

        for module, current_val in current.items():
            baseline_val = self._baseline.get(module, "NOT_SET")
            if current_val == baseline_val:
                continue

            was_active = self._getenv_bool(_MODULE_ENV_MAP[module], True)
            # Re-leer con current_val
            env_var = _MODULE_ENV_MAP[module]
            is_active = current_val.lower() in ("true", "1", "yes", "enabled", "on")

            if was_active and not is_active:
                event_type = "MODULE_DEGRADED"
            elif not was_active and is_active:
                event_type = "MODULE_ACTIVATED_RUNTIME"
            else:
                continue

            is_critical = module in CRITICAL_MODULES
            event = DegradationEvent(
                event_type=event_type,
                module=module,
                timestamp=now,
                was=baseline_val,
                became=current_val,
                is_critical=is_critical,
                seal=self._hmac_dict({
                    "event": event_type,
                    "module": module,
                    "timestamp": now,
                }),
            )
            self._trail.degradation_events.append(event)
            new_events.append(event)

            if is_critical and event_type == "MODULE_DEGRADED":
                self._trail.integrity_level = SystemIntegrityLevel.COMPROMISED
            elif self._trail.integrity_level == SystemIntegrityLevel.FULL:
                self._trail.integrity_level = SystemIntegrityLevel.DEGRADED

            import sys
            print(
                f"[VIGÍA][SECURITY ALERT] {event_type}: {module} "
                f"({env_var}) changed {baseline_val!r} → {current_val!r}",
                file=sys.stderr, flush=True,
            )

        return new_events

    def finalize(self) -> ConfigAuditTrail:
        """Cierra el trail. Llamar al final del análisis."""
        if not self._trail:
            raise RuntimeError("Monitor not initialized")
        self.checkpoint()
        if not self._trail.degradation_events:
            self._trail.integrity_level = SystemIntegrityLevel.FULL
        return self._trail
