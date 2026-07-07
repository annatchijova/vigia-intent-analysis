#!/usr/bin/env python3
"""
vigia_chain_of_custody.py
─────────────────────────────────────────────────────────────────────────────
VIGÍA Forensic Suite — Cadena de Custodia Inmutable (Merkle Log)

Convierte los ForensicBundles de VIGÍA en una cadena criptográfica
ininterrumpida donde cada bundle incluye el hash del bundle anterior.
Si un atacante borra el bundle de las 03:00, el bundle de las 03:05
falla la verificación porque `previous_bundle_hash` no coincide con
ningún bundle en la cadena — detectando el hueco.

Estructura de la cadena:
  GENESIS → Bundle[0] → Bundle[1] → ... → Bundle[N]

Cada nodo de la cadena es un ForensicBundle aumentado con:
  chain_entry = {
      "sequence":             int,          # posición en la cadena
      "bundle_id":            str,          # del bundle sellado
      "bundle_hash":          str,          # SHA-256 del bundle
      "previous_bundle_hash": str,          # SHA-256 del nodo anterior
      "chain_hash":           str,          # SHA-256(bundle_hash ∥ previous_bundle_hash ∥ sequence)
      "timestamp":            str,          # ISO 8601 UTC
      "bundle_path":          str | None,   # ruta al archivo en disco
  }

Garantías:
  1. Detección de huecos: un bundle faltante rompe la cadena en el siguiente nodo
  2. Detección de inserción: un bundle insertado retroactivamente cambia todos los
     chain_hash subsiguientes
  3. Detección de modificación: cualquier cambio en un bundle sellado cambia su
     bundle_hash, invalidando su chain_hash y todos los sucesores
  4. Stdlib-only: el verificador independiente usa exclusivamente hashlib + json + sqlite3
  5. Persistencia SQLite: el ledger es un archivo SQLite auditablemente legible

Uso:
  # Agregar un bundle a la cadena
  from vigia_chain_of_custody import ChainOfCustody
  chain = ChainOfCustody("vigia_chain.db")
  entry = chain.append(sealed_bundle_dict, bundle_path="bundles/bundle_001.json")
  print(entry["chain_hash"])

  # Verificar la cadena completa
  ok, report = chain.verify()
  assert ok, report

  # CLI
  python3 vigia_chain_of_custody.py append bundle.json
  python3 vigia_chain_of_custody.py verify
  python3 vigia_chain_of_custody.py status

─────────────────────────────────────────────────────────────────────────────
VIGÍA SANS FIND EVIL Hackathon 2026
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import hmac as _hmac_mod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════

CHAIN_VERSION = "1.1"
GENESIS_HASH = "0" * 64  # hash del nodo anterior para el primer bloque

# Campos agregados FUERA del payload hasheado por BundleBuilder.seal():
#   integrity      — lo escribe el propio seal() (contiene el bundle_hash)
#   forensic_chain — lo inyecta seal_with_chain() (metadata de esta cadena)
#   pki            — lo inyecta pki_tools (receipt RFC 3161 / firma HSM)
# La recomputación del bundle_hash debe excluirlos — mismo esquema que
# BundleBuilder.quick_verify() y forensics/verify_ebs_v1.py.
_PRESENTATION_FIELDS = ("integrity", "forensic_chain", "pki")

# Schema SQLite — inmutable post-creación
_SCHEMA = """
CREATE TABLE IF NOT EXISTS chain_entries (
    sequence             INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id            TEXT    NOT NULL,
    bundle_hash          TEXT    NOT NULL,
    previous_bundle_hash TEXT    NOT NULL,
    chain_hash           TEXT    NOT NULL UNIQUE,
    timestamp            TEXT    NOT NULL,
    bundle_path          TEXT,
    chain_version        TEXT    NOT NULL DEFAULT '1.0'
);

CREATE TABLE IF NOT EXISTS chain_metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Checkpoints de punta: anclan (tip, total) contra truncation attack.
-- Borrar las últimas N entradas deja una cadena internamente válida;
-- el checkpoint (idealmente HMAC-firmado y/o sellado por TSA RFC 3161)
-- prueba que en un momento dado la cadena llegaba hasta cierta punta.
CREATE TABLE IF NOT EXISTS chain_checkpoints (
    checkpoint_seq  INTEGER PRIMARY KEY AUTOINCREMENT,
    at_sequence     INTEGER NOT NULL,
    tip_chain_hash  TEXT    NOT NULL,
    total_entries   INTEGER NOT NULL,
    checkpoint_hmac TEXT,
    tsa_receipt     TEXT,
    created_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bundle_id   ON chain_entries(bundle_id);
CREATE INDEX IF NOT EXISTS idx_bundle_hash ON chain_entries(bundle_hash);
CREATE INDEX IF NOT EXISTS idx_timestamp   ON chain_entries(timestamp);
"""

# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES CRIPTOGRÁFICAS
# ══════════════════════════════════════════════════════════════════════════

def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# Canonicalización idéntica a BundleBuilder._canonicalize / verify_ebs_v1.
# Import del paquete cuando está instalado; copia local para ejecución
# standalone del CLI (mismo patrón que los verificadores stdlib-only).
try:
    from vigia.core.canonicalize import _canonicalize
except ImportError:  # pragma: no cover — solo CLI standalone
    import unicodedata as _unicodedata
    from fractions import Fraction as _Fraction

    def _canonicalize(obj):
        # v2 (R3-2): escalares idénticos a v1; strings escapados (s: + NFC/
        # CRLF->LF); Fraction explícito. Lockstep con vigia/core/canonicalize.py.
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, int):
            return f"{obj}:int"
        if isinstance(obj, float):
            if obj != obj:
                return "nan"
            if obj == float("inf"):
                return "inf"
            if obj == float("-inf"):
                return "-inf"
            return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
        if isinstance(obj, str):
            return "s:" + _unicodedata.normalize("NFC", obj.replace("\r\n", "\n").replace("\r", "\n"))
        if obj is None:
            return "null"
        if isinstance(obj, _Fraction):
            return f"{obj.numerator}/{obj.denominator}:frac"
        if isinstance(obj, dict):
            return {k: _canonicalize(v) for k, v in sorted(obj.items())}
        if isinstance(obj, (list, tuple)):
            return [_canonicalize(v) for v in obj]
        return "s:" + _unicodedata.normalize("NFC", str(obj).replace("\r\n", "\n").replace("\r", "\n"))


def _recompute_sealed_bundle_hash(bundle: Dict) -> str:
    """
    Recomputa el bundle_hash con el MISMO esquema que BundleBuilder.seal():
    SHA-256 del payload canónico excluyendo los campos de presentación
    (integrity, forensic_chain, pki).
    """
    payload = {k: v for k, v in bundle.items() if k not in _PRESENTATION_FIELDS}
    canonical = json.dumps(_canonicalize(payload), sort_keys=True, ensure_ascii=True)
    return _sha256(canonical)


def _compute_bundle_hash(bundle: Dict) -> str:
    """
    SHA-256 de un bundle para la cadena de custodia.

    Bundle sellado (tiene integrity.bundle_hash): SIEMPRE se recomputa
    desde el contenido canónico. El hash declarado NUNCA se acepta sin
    verificación — un bundle fabricado con un hash inventado no debe
    entrar a la cadena como legítimo. La comparación declarado-vs-
    recomputado la hace el caller (append rechaza; verify marca tampered).

    Bundle sin sellar (sin integrity): serialización completa, esquema
    legacy sin canonicalize — compatible con ledgers existentes.
    """
    integrity = bundle.get("integrity", {})
    if integrity.get("bundle_hash", ""):
        return _recompute_sealed_bundle_hash(bundle)
    # Fallback legacy: serializar y hashear el dict completo
    canonical = json.dumps(bundle, sort_keys=True, ensure_ascii=True)
    return _sha256(canonical)


def _declared_hash_mismatch(bundle: Dict) -> Optional[str]:
    """
    Si el bundle declara integrity.bundle_hash y NO recomputa desde el
    contenido, retorna el motivo. None si coincide o si no hay declarado.
    """
    declared = bundle.get("integrity", {}).get("bundle_hash", "")
    if not declared:
        return None
    recomputed = _recompute_sealed_bundle_hash(bundle)
    if recomputed != declared:
        return (
            f"integrity.bundle_hash declarado ({declared[:16]}...) no "
            f"recomputa desde el contenido canónico ({recomputed[:16]}...). "
            "Bundle fabricado o alterado post-sellado."
        )
    return None


def _compute_chain_hash(
    bundle_hash: str,
    previous_bundle_hash: str,
    sequence: int,
) -> str:
    """
    chain_hash = SHA256(bundle_hash ∥ previous_bundle_hash ∥ sequence)

    La inclusión explícita de sequence previene ataques de reordenamiento:
    si dos nodos se intercambian, sus chain_hashes son incorrectos aunque
    ambos bundle_hashes sean válidos individualmente.
    """
    payload = f"{bundle_hash}:{previous_bundle_hash}:{sequence}"
    return _sha256(payload)


# ══════════════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE DATOS
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class ChainEntry:
    sequence: int
    bundle_id: str
    bundle_hash: str
    previous_bundle_hash: str
    chain_hash: str
    timestamp: str
    bundle_path: Optional[str] = None
    chain_version: str = CHAIN_VERSION

    def to_dict(self) -> Dict:
        return {
            "sequence":             self.sequence,
            "bundle_id":            self.bundle_id,
            "bundle_hash":          self.bundle_hash,
            "previous_bundle_hash": self.previous_bundle_hash,
            "chain_hash":           self.chain_hash,
            "timestamp":            self.timestamp,
            "bundle_path":          self.bundle_path,
            "chain_version":        self.chain_version,
        }


@dataclass
class VerificationResult:
    passed: bool
    total_entries: int
    gaps_detected: List[Dict]       # huecos en la secuencia
    broken_links: List[Dict]        # previous_hash no coincide
    hash_mismatches: List[Dict]     # chain_hash recomputado != almacenado
    tampered_bundles: List[str]     # bundles en disco con hash diferente al de la cadena
    timestamp: str
    truncation_findings: List[Dict] = field(default_factory=list)  # cola borrada vs checkpoints
    checkpoints_verified: int = 0

    def to_dict(self) -> Dict:
        return {
            "passed":            self.passed,
            "total_entries":     self.total_entries,
            "gaps_detected":     self.gaps_detected,
            "broken_links":      self.broken_links,
            "hash_mismatches":   self.hash_mismatches,
            "tampered_bundles":  self.tampered_bundles,
            "truncation_findings": self.truncation_findings,
            "checkpoints_verified": self.checkpoints_verified,
            "timestamp":         self.timestamp,
            "summary": {
                "gaps":       len(self.gaps_detected),
                "broken":     len(self.broken_links),
                "mismatches": len(self.hash_mismatches),
                "tampered":   len(self.tampered_bundles),
                "truncations": len(self.truncation_findings),
            },
        }


# ══════════════════════════════════════════════════════════════════════════
# CHAIN OF CUSTODY ENGINE
# ══════════════════════════════════════════════════════════════════════════

class ChainOfCustody:
    """
    Ledger criptográfico inmutable para ForensicBundles VIGÍA.

    Cada bundle appended se encadena al anterior via SHA-256.
    La cadena es detectable-tamper por diseño:
    - Borrar un entry → el siguiente entry tiene un previous_hash incorrecto
    - Modificar un entry → su chain_hash no coincide con el recomputado
    - Insertar un entry → los sequence numbers y chain_hashes subsiguientes
      son incorrectos
    """

    def __init__(self, db_path: str = "vigia_chain.db") -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.executescript(_SCHEMA)
        # Registrar versión del ledger
        self._conn.execute(
            "INSERT OR IGNORE INTO chain_metadata (key, value) VALUES (?, ?)",
            ("chain_version", CHAIN_VERSION),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO chain_metadata (key, value) VALUES (?, ?)",
            ("created_at", datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def _get_last_entry(self) -> Optional[ChainEntry]:
        row = self._conn.execute(
            "SELECT * FROM chain_entries ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return ChainEntry(
            sequence=row["sequence"],
            bundle_id=row["bundle_id"],
            bundle_hash=row["bundle_hash"],
            previous_bundle_hash=row["previous_bundle_hash"],
            chain_hash=row["chain_hash"],
            timestamp=row["timestamp"],
            bundle_path=row["bundle_path"],
            chain_version=row["chain_version"],
        )

    def append(
        self,
        bundle: Dict,
        bundle_path: Optional[str] = None,
    ) -> ChainEntry:
        """
        Agrega un ForensicBundle sellado a la cadena.

        Args:
            bundle:       Dict del bundle sellado (salida de BundleBuilder.seal())
            bundle_path:  Ruta al archivo JSON en disco (para verificación futura)

        Returns:
            ChainEntry con todos los hashes calculados y la posición en la cadena.

        Raises:
            ValueError: si el bundle no tiene bundle_id o integridad básica.
        """
        bundle_id = bundle.get("bundle_id", "")
        if not bundle_id:
            raise ValueError("bundle must have a non-empty 'bundle_id' field")

        # El hash declarado DEBE recomputar desde el contenido — un bundle
        # fabricado con integrity.bundle_hash inventado no entra a la cadena.
        mismatch = _declared_hash_mismatch(bundle)
        if mismatch:
            raise ValueError(f"bundle '{bundle_id}' rechazado: {mismatch}")

        # Computar hash del bundle (recomputado, nunca el declarado a ciegas)
        bundle_hash = _compute_bundle_hash(bundle)

        # Obtener el hash del nodo anterior (o GENESIS si es el primero)
        last = self._get_last_entry()
        previous_hash = last.chain_hash if last is not None else GENESIS_HASH
        next_sequence = (last.sequence + 1) if last is not None else 1

        # Computar chain_hash encadenando
        chain_hash = _compute_chain_hash(bundle_hash, previous_hash, next_sequence)

        # FIX-TIMESTAMP-2026-05-16: usar fuente de verdad del bundle, no reloj del sistema
        # Prioridad: bundle.timestamp > integrity.sealed_at > datetime.now() [fallback]
        # Motivación: datetime.now() es spoofable por timestomping del host OS.
        ts_sources = [
            bundle.get("timestamp"),
            bundle.get("integrity", {}).get("sealed_at"),
        ]
        ts = next((t for t in ts_sources if t and isinstance(t, str)), None)
        if not ts:
            import warnings
            ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            warnings.warn(
                f"[VIGIA-COC] bundle '{bundle_id}' no contiene timestamp sellado. "
                "Usando reloj del sistema — spoofable por timestomping del host OS. "
                "En producción forense, el bundle DEBE incluir timestamp sellado.",
                RuntimeWarning,
                stacklevel=2,
            )

        # Insertar en el ledger (atómico)
        self._conn.execute(
            """
            INSERT INTO chain_entries
                (bundle_id, bundle_hash, previous_bundle_hash, chain_hash, timestamp, bundle_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (bundle_id, bundle_hash, previous_hash, chain_hash, ts, bundle_path),
        )
        self._conn.commit()

        entry = ChainEntry(
            sequence=next_sequence,
            bundle_id=bundle_id,
            bundle_hash=bundle_hash,
            previous_bundle_hash=previous_hash,
            chain_hash=chain_hash,
            timestamp=ts,
            bundle_path=bundle_path,
        )
        return entry

    # ------------------------------------------------------------------
    # Checkpoints de punta — defensa contra truncation attack
    # ------------------------------------------------------------------

    @staticmethod
    def _checkpoint_payload(at_sequence: int, tip_chain_hash: str,
                            total_entries: int, created_at: str) -> str:
        return f"{tip_chain_hash}:{at_sequence}:{total_entries}:{created_at}"

    def checkpoint(
        self,
        hmac_key: Optional[bytes] = None,
        tsa_receipt: Optional[Dict] = None,
    ) -> Dict:
        """
        Ancla la punta actual de la cadena en un checkpoint.

        Un checkpoint registra (tip_chain_hash, at_sequence, total_entries)
        con HMAC opcional (clave fuera del ledger) y receipt RFC 3161
        opcional (testigo temporal independiente — ver pki_tools /
        rfc3161_chain). verify() usa los checkpoints para detectar
        truncation: si la cadena actual es más corta que un checkpoint,
        alguien borró la cola.

        Sin hmac_key ni tsa_receipt el checkpoint vive en el mismo SQLite
        que la cadena — detecta truncation accidental pero un atacante con
        acceso al archivo puede borrarlo también. La clave/TSA es lo que
        lo hace resistente a ese atacante; se documenta, no se exige.

        Returns: dict del checkpoint creado.

        Raises:
            ValueError: si la cadena está vacía (nada que anclar).
        """
        last = self._get_last_entry()
        if last is None:
            raise ValueError("cadena vacía — no hay punta que anclar")

        count = self._conn.execute(
            "SELECT COUNT(*) FROM chain_entries"
        ).fetchone()[0]
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        payload = self._checkpoint_payload(
            last.sequence, last.chain_hash, count, created_at
        )
        checkpoint_hmac = (
            _hmac_mod.new(hmac_key, payload.encode("utf-8"), "sha256").hexdigest()
            if hmac_key else None
        )
        self._conn.execute(
            """
            INSERT INTO chain_checkpoints
                (at_sequence, tip_chain_hash, total_entries, checkpoint_hmac,
                 tsa_receipt, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (last.sequence, last.chain_hash, count, checkpoint_hmac,
             json.dumps(tsa_receipt) if tsa_receipt else None, created_at),
        )
        self._conn.commit()
        return {
            "at_sequence":     last.sequence,
            "tip_chain_hash":  last.chain_hash,
            "total_entries":   count,
            "checkpoint_hmac": checkpoint_hmac,
            "tsa_stamped":     tsa_receipt is not None,
            "created_at":      created_at,
        }

    def _verify_checkpoints(
        self,
        max_sequence: int,
        chain_hash_by_seq: Dict[int, str],
        hmac_key: Optional[bytes],
    ) -> Tuple[List[Dict], int]:
        """
        C5 — Anti-truncation: cada checkpoint debe apuntar a un entry que
        exista y cuyo chain_hash coincida con la punta anclada.
        """
        findings: List[Dict] = []
        rows = self._conn.execute(
            "SELECT * FROM chain_checkpoints ORDER BY checkpoint_seq ASC"
        ).fetchall()
        for row in rows:
            at_seq = row["at_sequence"]
            if hmac_key is not None and row["checkpoint_hmac"]:
                expected = _hmac_mod.new(
                    hmac_key,
                    self._checkpoint_payload(
                        at_seq, row["tip_chain_hash"],
                        row["total_entries"], row["created_at"],
                    ).encode("utf-8"),
                    "sha256",
                ).hexdigest()
                if not _hmac_mod.compare_digest(expected, row["checkpoint_hmac"]):
                    findings.append({
                        "checkpoint_seq": row["checkpoint_seq"],
                        "at_sequence": at_seq,
                        "note": "checkpoint_hmac no recomputa — checkpoint alterado.",
                    })
                    continue
            if at_seq > max_sequence:
                findings.append({
                    "checkpoint_seq": row["checkpoint_seq"],
                    "at_sequence": at_seq,
                    "current_max_sequence": max_sequence,
                    "note": (
                        f"TRUNCATION: el checkpoint del {row['created_at']} ancla "
                        f"la cadena hasta sequence={at_seq}, pero la cadena actual "
                        f"termina en sequence={max_sequence}. Se borraron "
                        f"{at_seq - max_sequence} entrada(s) de la cola."
                    ),
                })
            elif chain_hash_by_seq.get(at_seq) != row["tip_chain_hash"]:
                findings.append({
                    "checkpoint_seq": row["checkpoint_seq"],
                    "at_sequence": at_seq,
                    "note": (
                        "El chain_hash anclado por el checkpoint no coincide con "
                        "el entry actual en esa posición — historia reescrita."
                    ),
                })
        return findings, len(rows)

    def verify(
        self,
        verify_files: bool = True,
        hmac_key: Optional[bytes] = None,
    ) -> Tuple[bool, VerificationResult]:
        """
        Verifica la integridad completa de la cadena.

        Checks realizados:
          C1 — Secuencia continua: no hay huecos en los sequence numbers
          C2 — Encadenamiento: cada previous_bundle_hash == chain_hash del anterior
          C3 — Integridad del chain_hash: recomputar y comparar con el almacenado
          C4 — Integridad de archivos en disco (opcional): leer JSON, recomputar
               el bundle_hash canónico y comparar (el hash declarado en el
               archivo NO se acepta a ciegas)
          C5 — Anti-truncation: la cadena debe alcanzar la punta anclada por
               cada checkpoint (HMAC del checkpoint verificado si hay clave)

        Returns:
            (passed: bool, result: VerificationResult)
        """
        rows = self._conn.execute(
            "SELECT * FROM chain_entries ORDER BY sequence ASC"
        ).fetchall()

        gaps: List[Dict] = []
        broken_links: List[Dict] = []
        hash_mismatches: List[Dict] = []
        tampered: List[str] = []
        chain_hash_by_seq: Dict[int, str] = {}

        prev_chain_hash = GENESIS_HASH
        expected_seq = 1
        max_sequence = 0

        for row in rows:
            seq = row["sequence"]

            # C1: Detección de huecos
            if seq != expected_seq:
                gaps.append({
                    "expected_sequence": expected_seq,
                    "found_sequence":    seq,
                    "gap_size":          seq - expected_seq,
                    "bundle_id":         row["bundle_id"],
                    "note": (
                        f"Hueco detectado: faltan {seq - expected_seq} entrada(s) "
                        f"entre sequence {expected_seq - 1} y {seq}. "
                        f"Un atacante pudo haber borrado bundles en ese rango temporal."
                    ),
                })
                # Actualizar expected_seq para seguir verificando el resto
                expected_seq = seq + 1
            else:
                expected_seq += 1

            # C2: Encadenamiento (previous_bundle_hash debe coincidir con chain_hash anterior)
            stored_prev = row["previous_bundle_hash"]
            if stored_prev != prev_chain_hash:
                broken_links.append({
                    "sequence":            seq,
                    "bundle_id":           row["bundle_id"],
                    "stored_prev_hash":    stored_prev[:16] + "...",
                    "expected_prev_hash":  prev_chain_hash[:16] + "...",
                    "note": (
                        f"Enlace roto en sequence={seq}. "
                        f"El previous_hash almacenado no coincide con el chain_hash "
                        f"del nodo anterior. Posible: entry anterior borrado o modificado."
                    ),
                })

            # C3: Recomputar chain_hash y comparar
            recomputed = _compute_chain_hash(
                row["bundle_hash"],
                row["previous_bundle_hash"],
                seq,
            )
            if recomputed != row["chain_hash"]:
                hash_mismatches.append({
                    "sequence":         seq,
                    "bundle_id":        row["bundle_id"],
                    "stored_hash":      row["chain_hash"][:16] + "...",
                    "recomputed_hash":  recomputed[:16] + "...",
                    "note": "chain_hash almacenado no coincide con el recomputado — entry modificado.",
                })

            # C4: Verificar archivo en disco (si existe y se solicitó).
            # El bundle_hash se RECOMPUTA desde el contenido canónico — un
            # archivo alterado que conserva su integrity.bundle_hash original
            # también se detecta (antes pasaba: se confiaba en el declarado).
            if verify_files and row["bundle_path"]:
                path = Path(row["bundle_path"])
                if path.exists():
                    try:
                        disk_bundle = json.loads(path.read_text(encoding="utf-8"))
                        disk_hash = _compute_bundle_hash(disk_bundle)
                        if disk_hash != row["bundle_hash"]:
                            tampered.append(row["bundle_path"])
                        elif _declared_hash_mismatch(disk_bundle):
                            tampered.append(
                                f"{row['bundle_path']} [declared-hash-mismatch]"
                            )
                    except Exception:
                        tampered.append(f"{row['bundle_path']} [unreadable]")

            prev_chain_hash = row["chain_hash"]
            chain_hash_by_seq[seq] = row["chain_hash"]
            max_sequence = max(max_sequence, seq)

        # C5: checkpoints de punta — detección de cola borrada
        truncations, n_checkpoints = self._verify_checkpoints(
            max_sequence, chain_hash_by_seq, hmac_key
        )

        passed = (
            len(gaps) == 0
            and len(broken_links) == 0
            and len(hash_mismatches) == 0
            and len(tampered) == 0
            and len(truncations) == 0
        )

        result = VerificationResult(
            passed=passed,
            total_entries=len(rows),
            gaps_detected=gaps,
            broken_links=broken_links,
            hash_mismatches=hash_mismatches,
            tampered_bundles=tampered,
            truncation_findings=truncations,
            checkpoints_verified=n_checkpoints,
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        return passed, result

    def status(self) -> Dict:
        """Resumen del estado actual de la cadena."""
        count = self._conn.execute(
            "SELECT COUNT(*) FROM chain_entries"
        ).fetchone()[0]
        last = self._get_last_entry()
        first_ts = self._conn.execute(
            "SELECT timestamp FROM chain_entries ORDER BY sequence ASC LIMIT 1"
        ).fetchone()
        return {
            "total_entries":  count,
            "chain_tip":      last.chain_hash[:32] + "..." if last else None,
            "last_bundle_id": last.bundle_id if last else None,
            "last_timestamp": last.timestamp if last else None,
            "first_timestamp": first_ts[0] if first_ts else None,
            "db_path":        self.db_path,
            "chain_version":  CHAIN_VERSION,
        }

    def get_entry(self, sequence: int) -> Optional[ChainEntry]:
        row = self._conn.execute(
            "SELECT * FROM chain_entries WHERE sequence = ?", (sequence,)
        ).fetchone()
        if row is None:
            return None
        return ChainEntry(**dict(row))

    def export_chain(self) -> List[Dict]:
        """Exporta la cadena completa como lista de dicts (para auditoría)."""
        rows = self._conn.execute(
            "SELECT * FROM chain_entries ORDER BY sequence ASC"
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ChainOfCustody":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# ══════════════════════════════════════════════════════════════════════════
# WRAPPER: enriquecer un bundle con su entrada de cadena
# ══════════════════════════════════════════════════════════════════════════

def seal_with_chain(
    bundle: Dict,
    chain: ChainOfCustody,
    bundle_path: Optional[str] = None,
) -> Tuple[Dict, ChainEntry]:
    """
    Agrega un bundle a la cadena y retorna el bundle aumentado con
    los metadatos de la cadena inyectados en `forensic_chain`.

    El campo `forensic_chain` es un objeto de solo-lectura en el bundle
    que un perito puede inspeccionar para verificar la posición del
    bundle en la historia completa de capturas.

    IMPORTANTE: el bundle_hash original NO cambia — el campo `forensic_chain`
    se agrega FUERA del payload hasheado, en la capa de presentación.
    """
    entry = chain.append(bundle, bundle_path=bundle_path)

    # Inyectar metadatos de cadena en el bundle (fuera del bundle_hash original)
    augmented = dict(bundle)
    augmented["forensic_chain"] = {
        "sequence":             entry.sequence,
        "chain_hash":           entry.chain_hash,
        "previous_bundle_hash": entry.previous_bundle_hash,
        "chain_timestamp":      entry.timestamp,
        "chain_version":        CHAIN_VERSION,
        "verification_note": (
            "Este campo es metadata de cadena de custodia. "
            "El campo 'integrity.bundle_hash' sigue siendo la fuente "
            "de verdad para la integridad del bundle individual. "
            "El campo 'chain_hash' vincula este bundle al historial completo."
        ),
    }
    return augmented, entry


# ══════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════

def _cmd_append(args) -> int:
    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        print(f"ERROR: {bundle_path} no encontrado", file=sys.stderr)
        return 1
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido: {e}", file=sys.stderr)
        return 1

    with ChainOfCustody(args.db) as chain:
        entry = chain.append(bundle, bundle_path=str(bundle_path.resolve()))

    print(f"[OK] Bundle appended")
    print(f"     Sequence:   {entry.sequence}")
    print(f"     Bundle ID:  {entry.bundle_id}")
    print(f"     Bundle hash:{entry.bundle_hash[:32]}...")
    print(f"     Prev hash:  {entry.previous_bundle_hash[:32]}...")
    print(f"     Chain hash: {entry.chain_hash[:32]}...")
    return 0


def _resolve_env_hmac_key() -> Optional[bytes]:
    """VIGIA_HMAC_KEY (hex) o VIGIA_HMAC_KEY_FILE — mismas vars que security.py."""
    key_hex = os.getenv("VIGIA_HMAC_KEY", "").strip()
    if key_hex:
        try:
            return bytes.fromhex(key_hex)
        except ValueError:
            print("WARNING: VIGIA_HMAC_KEY no es hex válido — ignorada",
                  file=sys.stderr)
    key_file = os.getenv("VIGIA_HMAC_KEY_FILE", "").strip()
    if key_file and Path(key_file).is_file():
        return Path(key_file).read_bytes().strip()
    return None


def _cmd_checkpoint(args) -> int:
    hmac_key = _resolve_env_hmac_key()
    if hmac_key is None:
        print(
            "WARNING: sin VIGIA_HMAC_KEY[_FILE] — checkpoint sin firma. "
            "Detecta truncation accidental pero no a un atacante con "
            "acceso de escritura al ledger.",
            file=sys.stderr,
        )

    tsa_receipt = None
    if args.tsa:
        # Testigo temporal independiente: sellar la punta vía TSA RFC 3161.
        # Se sella un archivo temporal con el estado de la punta — la
        # infraestructura existente (rfc3161_chain) trabaja sobre paths.
        try:
            from vigia.forensics.rfc3161_chain import RFC3161Timestamper
            with ChainOfCustody(args.db) as chain:
                s = chain.status()
            import tempfile
            with tempfile.NamedTemporaryFile(
                "w", suffix="_chain_tip.json", delete=False
            ) as tmp:
                json.dump(s, tmp, sort_keys=True)
                tip_path = tmp.name
            record = RFC3161Timestamper().seal_artifact(tip_path)
            tsa_receipt = record.__dict__ if hasattr(record, "__dict__") else dict(record)
            os.unlink(tip_path)
        except Exception as exc:  # TSA caída/red ausente — checkpoint local válido
            print(f"WARNING: TSA no disponible ({exc}) — checkpoint sin "
                  "testigo externo.", file=sys.stderr)

    with ChainOfCustody(args.db) as chain:
        try:
            cp = chain.checkpoint(hmac_key=hmac_key, tsa_receipt=tsa_receipt)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    print("[OK] Checkpoint anclado")
    print(f"     Sequence:   {cp['at_sequence']}")
    print(f"     Tip hash:   {cp['tip_chain_hash'][:32]}...")
    print(f"     Firmado:    {'HMAC' if cp['checkpoint_hmac'] else 'NO (sin clave)'}")
    print(f"     TSA:        {'RFC 3161' if cp['tsa_stamped'] else 'no'}")
    return 0


def _cmd_verify(args) -> int:
    with ChainOfCustody(args.db) as chain:
        passed, result = chain.verify(
            verify_files=not args.no_files,
            hmac_key=_resolve_env_hmac_key(),
        )

    if args.json_out:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        return 0 if passed else 1

    print("═" * 60)
    print("VIGÍA Chain of Custody — Verificación")
    print("═" * 60)
    print(f"  Entradas totales: {result.total_entries}")
    print(f"  Huecos:           {len(result.gaps_detected)}")
    print(f"  Enlaces rotos:    {len(result.broken_links)}")
    print(f"  Hash inválidos:   {len(result.hash_mismatches)}")
    print(f"  Archivos alterados: {len(result.tampered_bundles)}")
    print(f"  Truncations:      {len(result.truncation_findings)} "
          f"(checkpoints verificados: {result.checkpoints_verified})")
    print()

    if result.truncation_findings:
        print("  TRUNCATION DETECTADO:")
        for t in result.truncation_findings:
            print(f"    {t['note']}")

    if result.gaps_detected:
        print("  HUECOS DETECTADOS:")
        for g in result.gaps_detected:
            print(f"    Seq esperada {g['expected_sequence']}, encontrada {g['found_sequence']}")
            print(f"    {g['note']}")

    if result.broken_links:
        print("  ENLACES ROTOS:")
        for b in result.broken_links:
            print(f"    Seq={b['sequence']} bundle={b['bundle_id']}")
            print(f"    {b['note']}")

    if result.tampered_bundles:
        print("  ARCHIVOS ALTERADOS EN DISCO:")
        for t in result.tampered_bundles:
            print(f"    {t}")

    status = "[PASS] Cadena íntegra" if passed else "[FAIL] Integridad comprometida"
    print(f"\n  RESULTADO: {status}")
    return 0 if passed else 1


def _cmd_status(args) -> int:
    with ChainOfCustody(args.db) as chain:
        s = chain.status()
    print(json.dumps(s, indent=2))
    return 0


def _cmd_export(args) -> int:
    with ChainOfCustody(args.db) as chain:
        entries = chain.export_chain()
    out = {
        "chain_version": CHAIN_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "entries": entries,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VIGÍA Chain of Custody — Ledger criptográfico de ForensicBundles",
    )
    parser.add_argument("--db", default="vigia_chain.db",
                        help="Ruta al ledger SQLite (default: vigia_chain.db)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_append = sub.add_parser("append", help="Agregar un bundle a la cadena")
    p_append.add_argument("bundle", help="Ruta al ForensicBundle sellado (.json)")

    p_verify = sub.add_parser("verify", help="Verificar integridad de la cadena")
    p_verify.add_argument("--no-files", action="store_true",
                           help="No verificar archivos en disco")
    p_verify.add_argument("--json", dest="json_out", action="store_true",
                           help="Salida en JSON")

    sub.add_parser("status", help="Estado actual de la cadena")
    sub.add_parser("export", help="Exportar cadena completa como JSON")

    p_checkpoint = sub.add_parser(
        "checkpoint",
        help="Anclar la punta de la cadena (anti-truncation; HMAC vía "
             "VIGIA_HMAC_KEY; --tsa para testigo RFC 3161)",
    )
    p_checkpoint.add_argument("--tsa", action="store_true",
                              help="Sellar la punta con TSA RFC 3161 externa")

    args = parser.parse_args()

    return {
        "append": _cmd_append,
        "verify": _cmd_verify,
        "status": _cmd_status,
        "export": _cmd_export,
        "checkpoint": _cmd_checkpoint,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
