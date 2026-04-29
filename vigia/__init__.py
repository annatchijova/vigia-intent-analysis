"""
VIGÍA — Forensic Integrity Engine for Adversarial Environments
==============================================================
SANS FIND EVIL Hackathon 2026

Paquete principal. Expone los módulos core para uso externo.
"""

__version__ = "2.0.0"
__author__ = "Anna Tchijova / VIGÍA AI Collective"
__license__ = "AGPL-3.0-or-later"

# ---------------------------------------------------------------------------
# Auto-verificación de integridad del paquete en boot (H25)
#
# VIGÍA se basa en que el motor es soberano. Si alguien modifica un módulo
# para inyectar un logger que filtre resultados, el sistema debe saberlo.
#
# Mecanismo: en el primer import, se calcula el engine_attestation_hash
# del código fuente y se compara contra VIGIA_ENGINE_HASH (env var).
# Si hay discrepancia → Kernel Panic Forense: log de ERROR + RuntimeError.
#
# Para obtener el hash inicial:
#     python -c "from vigia.core.bundle_builder import BundleBuilder; print(BundleBuilder.compute_engine_attestation())"
#
# Luego exportar: export VIGIA_ENGINE_HASH=<hash>
#
# En modo permisivo (VIGIA_STRICT_ENGINE_CHECK != "true") solo emite warning.
# ---------------------------------------------------------------------------

import logging as _log
import os as _os

_logger = _log.getLogger(__name__)

def _boot_integrity_check() -> None:
    """Verifica integridad del paquete contra VIGIA_ENGINE_HASH al importar."""
    expected_hash = _os.getenv("VIGIA_ENGINE_HASH", "").strip()
    if not expected_hash:
        # Sin hash configurado — modo advertencia
        _logger.debug(
            "[VIGÍA boot] VIGIA_ENGINE_HASH no configurado — "
            "auto-verificación de integridad desactivada. "
            "Para producción forense: exportar el hash del motor."
        )
        return

    try:
        from vigia.core.bundle_builder import BundleBuilder
        actual_hash = BundleBuilder.compute_engine_attestation()
        if not actual_hash:
            _logger.warning("[VIGÍA boot] No se pudo calcular engine_attestation_hash.")
            return

        if actual_hash != expected_hash:
            msg = (
                f"[VIGÍA KERNEL PANIC FORENSE] "
                f"engine_attestation_hash no coincide con VIGIA_ENGINE_HASH. "
                f"Esperado: {expected_hash[:16]}… | Calculado: {actual_hash[:16]}… "
                f"El código fuente del motor fue modificado después del sellado. "
                f"NO ejecutar análisis forense con este motor — los resultados "
                f"no son admisibles bajo estándar Daubert."
            )
            strict = _os.getenv("VIGIA_STRICT_ENGINE_CHECK", "false").lower() == "true"
            if strict:
                _logger.critical(msg)
                raise RuntimeError(msg)
            else:
                _logger.error(msg)
        else:
            _logger.info(
                "[VIGÍA boot] Integridad del motor verificada. Hash: %s…",
                actual_hash[:16],
            )
    except ImportError:
        _logger.debug("[VIGÍA boot] BundleBuilder no disponible — verificación omitida.")
    except RuntimeError:
        raise
    except Exception as _e:
        _logger.warning("[VIGÍA boot] Auto-verificación falló: %s", _e)


_boot_integrity_check()
