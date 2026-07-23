# B-210: este __init__ tenía DOS bloques de import casi idénticos con el
# __all__ atrapado entre ambos — el segundo agregaba _sanitize_llm_input
# pero el __all__ (definido antes) no lo listaba. Consolidado en un único
# bloque canónico; el conjunto de nombres importables no cambia.
from vigia.security.security import (
    SecurityAudit,
    audit_logger,
    llm_shield,
    _utcnow,
    _sanitize_path,
    _sanitize_llm_input,
    _truncate,
    rate_limit,
    RateLimitExceeded,
    TrustExponentialDecay,
    trust_decay,
)
from vigia.security.sandbox import sandboxed_execute, safe_grep

__all__ = [
    "SecurityAudit",
    "audit_logger",
    "llm_shield",
    "_utcnow",
    "_sanitize_path",
    "_sanitize_llm_input",
    "_truncate",
    "rate_limit",
    "RateLimitExceeded",
    "TrustExponentialDecay",
    "trust_decay",
    "sandboxed_execute",
    "safe_grep",
]
