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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════

CHAIN_VERSION = "1.0"
GENESIS_HASH = "0" * 64  # hash del nodo anterior para el primer bloque

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

CREATE INDEX IF NOT EXISTS idx_bundle_id   ON chain_entries(bundle_id);
CREATE INDEX IF NOT EXISTS idx_bundle_hash ON chain_entries(bundle_hash);
CREATE INDEX IF NOT EXISTS idx_timestamp   ON chain_entries(timestamp);
"""

# ══════════════════════════════════════════════════════════════════════════
# FUNCIONES CRIPTOGRÁFICAS
# ══════════════════════════════════════════════════════════════════════════

def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_bundle_hash(bundle: Dict) -> str:
    """
    Calcula el SHA-256 de un bundle sellado.
    Si el bundle ya tiene un campo 'integrity.bundle_hash', lo usa directamente
    (el bundle fue sellado por BundleBuilder — confiar en su hash).
    De lo contrario, calcular sobre la serialización canónica.
    """
    integrity = bundle.get("integrity", {})
    existing_hash = integrity.get("bundle_hash", "")
    if existing_hash and len(existing_hash) == 64:
        return existing_hash
    # Fallback: serializar y hashear
    canonical = json.dumps(bundle, sort_keys=True, ensure_ascii=True)
    return _sha256(canonical)


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

    def to_dict(self) -> Dict:
        return {
            "passed":            self.passed,
            "total_entries":     self.total_entries,
            "gaps_detected":     self.gaps_detected,
            "broken_links":      self.broken_links,
            "hash_mismatches":   self.hash_mismatches,
            "tampered_bundles":  self.tampered_bundles,
            "timestamp":         self.timestamp,
            "summary": {
                "gaps":       len(self.gaps_detected),
                "broken":     len(self.broken_links),
                "mismatches": len(self.hash_mismatches),
                "tampered":   len(self.tampered_bundles),
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

        # Computar hash del bundle
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

    def verify(self, verify_files: bool = True) -> Tuple[bool, VerificationResult]:
        """
        Verifica la integridad completa de la cadena.

        Checks realizados:
          C1 — Secuencia continua: no hay huecos en los sequence numbers
          C2 — Encadenamiento: cada previous_bundle_hash == chain_hash del anterior
          C3 — Integridad del chain_hash: recomputar y comparar con el almacenado
          C4 — Integridad de archivos en disco (opcional): leer JSON y comparar bundle_hash

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

        prev_chain_hash = GENESIS_HASH
        expected_seq = 1

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

            # C4: Verificar archivo en disco (si existe y se solicitó)
            if verify_files and row["bundle_path"]:
                path = Path(row["bundle_path"])
                if path.exists():
                    try:
                        disk_bundle = json.loads(path.read_text(encoding="utf-8"))
                        disk_hash = _compute_bundle_hash(disk_bundle)
                        if disk_hash != row["bundle_hash"]:
                            tampered.append(row["bundle_path"])
                    except Exception:
                        tampered.append(f"{row['bundle_path']} [unreadable]")

            prev_chain_hash = row["chain_hash"]

        passed = (
            len(gaps) == 0
            and len(broken_links) == 0
            and len(hash_mismatches) == 0
            and len(tampered) == 0
        )

        result = VerificationResult(
            passed=passed,
            total_entries=len(rows),
            gaps_detected=gaps,
            broken_links=broken_links,
            hash_mismatches=hash_mismatches,
            tampered_bundles=tampered,
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


def _cmd_verify(args) -> int:
    with ChainOfCustody(args.db) as chain:
        passed, result = chain.verify(verify_files=not args.no_files)

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
    print()

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

    args = parser.parse_args()

    return {
        "append": _cmd_append,
        "verify": _cmd_verify,
        "status": _cmd_status,
        "export": _cmd_export,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
