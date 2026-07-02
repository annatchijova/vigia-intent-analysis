#!/usr/bin/env python3
"""
vigia/core/chain_of_custody.py

Cadena de custodia forense para VIGÍA.
Registra operaciones sobre evidencia digital con hash, timestamp y actor.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CustodyRecord:
    """Registro individual de custodia."""
    operation: str
    timestamp: str
    actor: str
    artifact_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChainOfCustody:
    """
    Cadena de custodia para evidencia forense.
    
    Mantiene un registro inmutable de todas las operaciones
    realizadas sobre un artefacto digital.
    """

    def __init__(self, case_id: str = "UNKNOWN", artifact_id: str = "UNKNOWN"):
        self.case_id = case_id
        self.artifact_id = artifact_id
        self.records: List[CustodyRecord] = []

    def add_record(
        self,
        operation: str,
        actor: str = "vigia_system",
        artifact_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CustodyRecord:
        """Añade un registro a la cadena de custodia."""
        record = CustodyRecord(
            operation=operation,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            artifact_hash=artifact_hash,
            metadata=metadata or {},
        )
        self.records.append(record)
        return record

    def acquire(
        self,
        data: bytes,
        actor: str = "vigia_system",
        timestamp: str = "",
        notes: str = "",
    ) -> None:
        """Compatibility shim: records raw-data acquisition into custody chain.
        Called by SIFT modules as chain.acquire(bytes, actor, timestamp[, notes]).

        `notes` es opcional: disk_forensics (y otros motores) lo pasan para
        anotar la adquisición. Antes acquire() no lo aceptaba y el motor de
        disco fallaba con TypeError — bug latente que solo se disparaba cuando
        el MFT llegaba realmente al motor (nunca ocurría en modo agente hasta
        que se cableó el parser de $MFT).
        """
        import hashlib
        artifact_hash = hashlib.sha256(data).hexdigest()
        meta = {"data_size": len(data), "timestamp_utc": timestamp}
        if notes:
            meta["notes"] = notes
        self.add_record(
            operation="ACQUIRE",
            actor=actor,
            artifact_hash=artifact_hash,
            metadata=meta,
        )

    def hash_file(self, path: str) -> str:
        """Calcula SHA-256 de un archivo."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def export_for_bundle(self) -> Dict[str, Any]:
        """Exporta la cadena para inclusion en evidence bundle."""
        return {
            "case_id": self.case_id,
            "artifact_id": self.artifact_id,
            "n_records": len(self.records),
            "records": [
                {
                    "operation": r.operation,
                    "timestamp": r.timestamp,
                    "actor": r.actor,
                    "artifact_hash": r.artifact_hash,
                    "metadata": r.metadata,
                }
                for r in self.records
            ],
        }

    def __len__(self) -> int:
        return len(self.records)

    def __bool__(self) -> bool:
        return True
