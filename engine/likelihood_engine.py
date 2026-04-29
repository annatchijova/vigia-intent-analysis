from vigia.core.likelihood_engine import *
from vigia.core.likelihood_engine import _correlation_penalty as _correlation_penalty_full

def _correlation_penalty(signals):
    """Wrapper compatible con tests EBS v1 — retorna solo penalty (float)."""
    result = _correlation_penalty_full(signals)
    if isinstance(result, tuple):
        return result[0]
    return result
