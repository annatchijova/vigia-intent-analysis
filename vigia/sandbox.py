# vigia/sandbox.py — shim de compatibilidad
# sandboxed_execute y safe_grep se consolidaron en vigia.security.sandbox
# Este shim mantiene la interfaz pública sin modificar el bridge.
from vigia.security.sandbox import sandboxed_execute, safe_grep

__all__ = ["sandboxed_execute", "safe_grep"]
