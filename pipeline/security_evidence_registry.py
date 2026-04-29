# vigia/security/evidence_registry.py

from __future__ import annotations

import hashlib
import json
import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(data: Dict[str, Any]) -> str:
    """
    Serialización determinística (CRÍTICO para verificabilidad).
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Ledger Entry
# ---------------------------------------------------------------------------

class EvidenceEntry:
    def __init__(
        self,
        index: int,
        timestamp: str,
        event_type: str,
        payload: Dict[str, Any],
        actor: str,
        prev_hash: str,
    ) -> None:
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.payload = payload
        self.actor = actor
        self.prev_hash = prev_hash

        self.entry_hash = self._compute_hash()
        self.signature: Optional[str] = None

    def _compute_hash(self) -> str:
        canonical_payload = _canonical_json(self.payload)

        raw = (
            str(self.index)
            + self.timestamp
            + self.event_type
            + canonical_payload
            + self.actor
            + self.prev_hash
        ).encode()

        return _sha256(raw)

    def sign(self, private_key: Optional[Any] = None) -> None:
        """
        Firma opcional (placeholder).
        """
        if private_key is None:
            return
        self.signature = f"SIGNED({self.entry_hash[:16]})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "actor": self.actor,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "signature": self.signature,
        }


# ---------------------------------------------------------------------------
# Ledger principal
# ---------------------------------------------------------------------------

class EvidenceLedger:
    """
    Ledger de evidencia con hashes encadenados.
    """

    def __init__(self) -> None:
        self._entries: List[EvidenceEntry] = []
        self._create_genesis_block()

    # -----------------------------------------------------------------------
    # Genesis
    # -----------------------------------------------------------------------

    def _create_genesis_block(self) -> None:
        genesis = EvidenceEntry(
            index=0,
            timestamp=_utc_now(),
            event_type="GENESIS",
            payload={"message": "VIGIA Evidence Ledger Initialized"},
            actor="SYSTEM",
            prev_hash="0" * 64,
        )
        self._entries.append(genesis)

    # -----------------------------------------------------------------------
    # Append
    # -----------------------------------------------------------------------

    def append(
        self,
        event_type: str,
        payload: Dict[str, Any],
        actor: str,
        private_key: Optional[Any] = None,
    ) -> EvidenceEntry:
        prev = self._entries[-1]

        entry = EvidenceEntry(
            index=len(self._entries),
            timestamp=_utc_now(),
            event_type=event_type,
            payload=payload,
            actor=actor,
            prev_hash=prev.entry_hash,
        )

        entry.sign(private_key)
        self._entries.append(entry)

        return entry

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    def verify(self) -> Dict[str, Any]:
        """
        Verifica integridad completa del ledger.
        """
        errors = []

        for i in range(1, len(self._entries)):
            current = self._entries[i]
            previous = self._entries[i - 1]

            # Check linkage
            if current.prev_hash != previous.entry_hash:
                errors.append(
                    f"Broken chain at index {i}: prev_hash mismatch"
                )

            # Recompute hash
            if current.entry_hash != current._compute_hash():
                errors.append(
                    f"Tampering detected at index {i}: hash mismatch"
                )

        return {
            "is_valid": len(errors) == 0,
            "entries_checked": len(self._entries),
            "errors": errors,
        }

    # -----------------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_length": len(self._entries),
            "entries": [e.to_dict() for e in self._entries],
        }

    def export_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    # -----------------------------------------------------------------------
    # Hash global
    # -----------------------------------------------------------------------

    def root_hash(self) -> str:
        """
        Hash del último bloque (estado actual del ledger).
        """
        return self._entries[-1].entry_hash
