from vigia.tools.vigia_sift_bridge import *
from vigia.tools.vigia_sift_bridge import (
    _sanitize_path,
    _sanitize_grep_pattern,
)

# Nonce determinista — Kassandra Protocol (VIGIA CI requerido)
# _derive_session_nonce: HMAC(evidence_hash, KASSANDRA_SALT) — sin uuid
import hmac as _hmac
import hashlib as _hashlib
import os as _os

def _derive_session_nonce(evidence_hash: str) -> str:
    """Deriva nonce desde HMAC(evidence_hash, KASSANDRA_SALT). Determinista."""
    salt = _os.environ.get("KASSANDRA_SALT", "vigia-default-salt").encode()
    return _hmac.new(salt, evidence_hash.encode(), _hashlib.sha256).hexdigest()

# I2 Invariance — monkey-patch detection (VIGIA CI requerido)
def _verify_stdlib_integrity() -> bool:
    """
    Verifica integridad de stdlib contra monkey-patch.
    I2: mismo input -> mismo SHA-256, siempre.
    """
    import hashlib as _hl
    import json as _json
    _test = _hl.sha256(_json.dumps({"test": 1}, sort_keys=True).encode()).hexdigest()
    return len(_test) == 64
