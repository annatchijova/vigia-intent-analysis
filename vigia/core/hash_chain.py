"""
vigia/core/hash_chain.py
=========================
Primitiva única de hash chain tamper-evident para VIGÍA.

Unifica los esquemas de encadenamiento que hoy divergen entre
verify_tool_log.py (solo result_summary), vigia_chain_of_custody.py
(bundle_hash:prev:seq), execution_logger.py (hashes truncados a 16 hex)
y SecurityAuditLog (HMAC sobre entrada completa).

Esquema v2:
  entry_hash = SHA-256( canonical( payload ∪ {seq, prev_hash} ) )
  entry_hmac = HMAC-SHA256( key, entry_hash )          [opcional, dual]

  - El payload COMPLETO entra al hash — cualquier campo alterado rompe
    la cadena (a diferencia del esquema v1 del tool_execution_log, que
    solo protegía result_summary).
  - seq explícito dentro del hash previene reordenamiento.
  - GENESIS_HASH ancla el primer eslabón.
  - La canonicalización es la fuente de verdad v1 de core/canonicalize.py
    (bool→"true", int→"N:int", float→8 decimales) + json sort_keys,
    ensure_ascii=True — idéntica a bundle_builder / verify_ebs_v1.

Diseño dual hash/HMAC (deliberado):
  - entry_hash (sin clave): un tercero verifica la ESTRUCTURA de la cadena
    con stdlib, sin acceso a la clave — requisito de verificación
    independiente Daubert.
  - entry_hmac (con clave): detecta al atacante interno con acceso de
    escritura que recomputa la cadena completa. Sin clave, SHA-256 puro
    es recomputable en milisegundos; con HMAC no.

Verificación: verify_chain acumula TODOS los errores por categoría
(discontinuidad de seq, linkage roto, contenido alterado, HMAC inválido)
— el perito ve el mapa completo del daño, no solo el primer eslabón.

Este módulo es puro respecto a la cadena: sin I/O de log, sin DB.
La única lectura de entorno es resolve_hmac_key() (VIGIA_HMAC_KEY /
VIGIA_HMAC_KEY_FILE — mismas variables que SecurityAuditLog).
"""
from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from vigia.core.canonicalize import (
    _canonicalize,       # default v2
    _canonicalize_v1,
    _canonicalize_v2,
)

CHAIN_SCHEMA_VERSION: str = "2"
GENESIS_HASH: str = "0" * 64

# R3-4 (docs/REDTEAM_ROUND3_EMERGENT.md): ventana forense plausible para los
# timestamps de la cadena. MISMOS limites FIJOS que la regla TCV (R3-1) — un
# timestamp fuera de rango (1970 epoch / 1601 FILETIME / 2099) es implausible.
# Limites fijos (no now()) para reproducibilidad; techo 2038 = overflow epoch
# 32-bit. Esto NO es integridad criptografica: es plausibilidad temporal,
# reportada por SEPARADO (una historia causalmente imposible no rompe el sello).
_PLAUSIBLE_MIN = datetime(2000, 1, 1, tzinfo=timezone.utc)
_PLAUSIBLE_MAX = datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc)


def _parse_iso_ts(ts):
    """Parseo ISO-8601 tolerante para el chequeo de plausibilidad. Devuelve un
    datetime tz-aware (naive -> UTC) o None si no es parseable/ausente."""
    if not isinstance(ts, str) or not ts.strip():
        return None
    try:
        dt = datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _content_signature(payload: Dict[str, Any]) -> str:
    """Firma de contenido de un eslabon para detectar eventos duplicados —
    excluye lo que legitimamente varia entre eventos (timestamp, event_id) y
    los campos estructurales (ya fuera del payload)."""
    body = {k: v for k, v in payload.items() if k not in ("timestamp", "event_id")}
    return canonical_hash(body)

# Mismas variables de entorno que SecurityAuditLog (vigia/security/security.py)
_HMAC_KEY_ENV = "VIGIA_HMAC_KEY"
_HMAC_KEY_FILE_ENV = "VIGIA_HMAC_KEY_FILE"


# ──────────────────────────────────────────────────────────────────────────
# Hashing
# ──────────────────────────────────────────────────────────────────────────

def canonical_hash(payload: Dict[str, Any], canon=_canonicalize) -> str:
    """SHA-256 del payload en forma canónica (canonicalize.py). `canon` elige
    el esquema: default v2 (sellos nuevos); v1 solo para verificar historicos."""
    canonical = json.dumps(
        canon(payload), sort_keys=True, ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_entry_hash(seq: int, prev_hash: str, payload: Dict[str, Any],
                       canon=_canonicalize) -> str:
    """
    Hash de un eslabón: payload completo + seq + prev_hash.

    El payload NO debe contener las claves 'seq' ni 'prev_hash' (se
    agregan acá). Si las contiene, se sobreescriben — el hash siempre
    usa los valores estructurales de la cadena.

    `canon` = esquema de canonicalizacion: default v2. La verificacion prueba
    v2 y cae a v1 para eslabones sellados bajo el esquema legacy (R3-2).
    """
    return canonical_hash({**payload, "seq": seq, "prev_hash": prev_hash}, canon=canon)


def _entry_hash_matches(link: "ChainLink") -> bool:
    """True si el entry_hash almacenado recomputa bajo v2 O bajo v1 (R3-2
    backward-compat). Un eslabon manipulado no reproduce ninguno de los dos:
    ofrecer dos formas canonicas no ayuda al falsificador (ambas son
    resistentes a preimagen), pero permite verificar cadenas legacy v1."""
    for canon in (_canonicalize_v2, _canonicalize_v1):
        if compute_entry_hash(link.seq, link.prev_hash, link.payload, canon=canon) == link.entry_hash:
            return True
    return False


def compute_entry_hmac(key: bytes, entry_hash: str) -> str:
    """HMAC-SHA256 del entry_hash. Capa keyed del diseño dual."""
    return _hmac.new(key, entry_hash.encode("utf-8"), "sha256").hexdigest()


def resolve_hmac_key() -> Optional[bytes]:
    """
    Resuelve la clave HMAC del entorno (VIGIA_HMAC_KEY hex, o
    VIGIA_HMAC_KEY_FILE con bytes crudos).

    Retorna None si no hay clave configurada — a diferencia de
    SecurityAuditLog, NO genera clave efímera: una cadena firmada con
    clave irrecuperable es indistinguible de una cadena manipulada.
    Sin clave, la cadena opera en modo hash-only (documentado, no error).
    """
    key_hex = os.getenv(_HMAC_KEY_ENV, "").strip()
    if key_hex:
        try:
            key = bytes.fromhex(key_hex)
            if len(key) < 32:
                print(
                    f"[VIGIA][hash_chain] WARNING: {_HMAC_KEY_ENV} tiene "
                    f"{len(key)} bytes — mínimo recomendado 32.",
                    file=sys.stderr, flush=True,
                )
            return key
        except ValueError:
            print(
                f"[VIGIA][hash_chain] WARNING: {_HMAC_KEY_ENV} no es hex "
                "válido. Probando VIGIA_HMAC_KEY_FILE.",
                file=sys.stderr, flush=True,
            )

    key_file = os.getenv(_HMAC_KEY_FILE_ENV, "").strip()
    if key_file:
        try:
            key_path = Path(key_file)
            if key_path.is_file():
                key = key_path.read_bytes().strip()
                if len(key) >= 32:
                    return key
                print(
                    f"[VIGIA][hash_chain] WARNING: {key_file} contiene solo "
                    f"{len(key)} bytes — mínimo 32. Ignorada.",
                    file=sys.stderr, flush=True,
                )
        except OSError as exc:
            print(
                f"[VIGIA][hash_chain] WARNING: no se pudo leer {key_file}: {exc}",
                file=sys.stderr, flush=True,
            )
    return None


# ──────────────────────────────────────────────────────────────────────────
# Estructuras
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ChainLink:
    """Un eslabón ya almacenado, listo para verificar."""
    seq: int
    prev_hash: str
    entry_hash: str
    payload: Dict[str, Any]  # payload SIN seq/prev_hash (se agregan al verificar)
    entry_hmac: Optional[str] = None


@dataclass
class ChainVerification:
    """
    Resultado de verificación con acumulación completa de errores.

    valid es True solo si TODAS las categorías están vacías.
    first_invalid_seq apunta al primer eslabón con cualquier error —
    el punto de manipulación más temprano.
    """
    valid: bool
    length: int
    first_invalid_seq: Optional[int] = None
    seq_discontinuities: List[Dict[str, Any]] = field(default_factory=list)
    broken_links: List[Dict[str, Any]] = field(default_factory=list)
    tampered_content: List[Dict[str, Any]] = field(default_factory=list)
    hmac_failures: List[Dict[str, Any]] = field(default_factory=list)
    hmac_checked: bool = False
    # R3-4: eje SEPARADO de plausibilidad temporal. NO afecta `valid` (que es
    # integridad criptografica): una historia causalmente imposible se sella y
    # verifica perfecto; esto solo advierte que la LINEA DE TIEMPO registrada no
    # es plausible (orden no monotono, fuera de rango, evento duplicado).
    timeline_plausible: bool = True
    temporal_anomalies: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "length": self.length,
            "first_invalid_seq": self.first_invalid_seq,
            "seq_discontinuities": self.seq_discontinuities,
            "broken_links": self.broken_links,
            "tampered_content": self.tampered_content,
            "hmac_failures": self.hmac_failures,
            "hmac_checked": self.hmac_checked,
            "timeline_plausible": self.timeline_plausible,
            "temporal_anomalies": self.temporal_anomalies,
            "summary": {
                "seq_discontinuities": len(self.seq_discontinuities),
                "broken_links": len(self.broken_links),
                "tampered_content": len(self.tampered_content),
                "hmac_failures": len(self.hmac_failures),
                "temporal_anomalies": len(self.temporal_anomalies),
            },
        }


# ──────────────────────────────────────────────────────────────────────────
# Appender puro
# ──────────────────────────────────────────────────────────────────────────

def build_link(
    seq: int,
    prev_hash: str,
    payload: Dict[str, Any],
    hmac_key: Optional[bytes] = None,
) -> ChainLink:
    """Construye el eslabón siguiente (puro — el caller persiste)."""
    entry_hash = compute_entry_hash(seq, prev_hash, payload)
    entry_hmac = compute_entry_hmac(hmac_key, entry_hash) if hmac_key else None
    return ChainLink(
        seq=seq, prev_hash=prev_hash, entry_hash=entry_hash,
        payload=payload, entry_hmac=entry_hmac,
    )


# ──────────────────────────────────────────────────────────────────────────
# Verificación
# ──────────────────────────────────────────────────────────────────────────

def verify_chain(
    links: Sequence[ChainLink],
    *,
    first_seq: int = 1,
    hmac_key: Optional[bytes] = None,
) -> ChainVerification:
    """
    Verifica una cadena completa, ordenada por seq ascendente.

    Acumula TODOS los errores (estilo vigia_chain_of_custody.verify):
      - seq_discontinuities : eslabones borrados/insertados en el medio
      - broken_links        : prev_hash no coincide con el entry_hash anterior
      - tampered_content    : entry_hash no recomputa desde el contenido
      - hmac_failures       : entry_hmac ausente o no recomputa (si hay clave)

    NOTA truncation: borrar los ÚLTIMOS eslabones deja una cadena
    internamente válida — eso solo lo detecta un checkpoint de punta
    anclado fuera del almacén (ver ChainOfCustody.checkpoint / RFC 3161).
    """
    result = ChainVerification(
        valid=True, length=len(links), hmac_checked=hmac_key is not None,
    )
    expected_prev = GENESIS_HASH
    expected_seq = first_seq

    def _flag(seq: int) -> None:
        result.valid = False
        if result.first_invalid_seq is None or seq < result.first_invalid_seq:
            result.first_invalid_seq = seq

    for link in links:
        if link.seq != expected_seq:
            result.seq_discontinuities.append({
                "expected_seq": expected_seq,
                "found_seq": link.seq,
                "note": f"discontinuidad: esperado seq={expected_seq}, "
                        f"encontrado seq={link.seq} — eslabón borrado o insertado",
            })
            _flag(link.seq)
            expected_seq = link.seq  # seguir verificando el resto

        if link.prev_hash != expected_prev:
            result.broken_links.append({
                "seq": link.seq,
                "stored_prev": link.prev_hash[:16] + "...",
                "expected_prev": expected_prev[:16] + "...",
                "note": "prev_hash no coincide con el entry_hash del eslabón anterior",
            })
            _flag(link.seq)

        if not _entry_hash_matches(link):
            recomputed = compute_entry_hash(link.seq, link.prev_hash, link.payload)
            result.tampered_content.append({
                "seq": link.seq,
                "stored": link.entry_hash[:16] + "...",
                "recomputed": recomputed[:16] + "...",
                "note": "entry_hash no recomputa desde el contenido (ni v2 ni v1) — entrada modificada",
            })
            _flag(link.seq)

        if hmac_key is not None:
            if not link.entry_hmac:
                result.hmac_failures.append({
                    "seq": link.seq,
                    "note": "entry_hmac ausente — eslabón escrito sin clave o campo borrado",
                })
                _flag(link.seq)
            elif not _hmac.compare_digest(
                link.entry_hmac, compute_entry_hmac(hmac_key, link.entry_hash)
            ):
                result.hmac_failures.append({
                    "seq": link.seq,
                    "note": "entry_hmac no recomputa — cadena recomputada sin la clave",
                })
                _flag(link.seq)

        expected_prev = link.entry_hash
        expected_seq = link.seq + 1

    # ── R3-4: plausibilidad temporal (eje separado, NO afecta `valid`) ──────
    _check_timeline_plausibility(links, result)
    return result


def _check_timeline_plausibility(
    links: Sequence[ChainLink], result: "ChainVerification"
) -> None:
    """
    R3-4: valida el ORDEN CAUSAL de la linea de tiempo registrada — separado de
    la integridad criptografica. Detecta:
      - NON_MONOTONIC_TIMESTAMP : un eslabon con timestamp ANTERIOR al previo
        (efecto antes que la causa en el orden de insercion).
      - OUT_OF_RANGE_TIMESTAMP  : fuera de [2000, 2038) — 1970/1601/2099.
      - DUPLICATE_CONTENT        : contenido identico a un eslabon anterior
        (mismo evento re-registrado).
    Un timestamp ausente/no parseable NO marca implausible (no se puede juzgar);
    se anota como MISSING/UNPARSEABLE solo si acompaña a otra anomalia? No — se
    omite en silencio para no inflar el reporte. `timeline_plausible` = sin
    anomalias duras. Esto es plausibilidad, no un veredicto de manipulacion.
    """
    prev_ts = None
    prev_seq = None
    seen_sig: Dict[str, int] = {}
    for link in links:
        ts_raw = link.payload.get("timestamp")
        dt = _parse_iso_ts(ts_raw)
        if dt is not None:
            if not (_PLAUSIBLE_MIN <= dt < _PLAUSIBLE_MAX):
                result.temporal_anomalies.append({
                    "seq": link.seq,
                    "type": "OUT_OF_RANGE_TIMESTAMP",
                    "timestamp": str(ts_raw),
                    "note": f"timestamp fuera de la ventana forense plausible "
                            f"[{_PLAUSIBLE_MIN.date()}, {_PLAUSIBLE_MAX.date()}) "
                            f"— sentinela epoch/overflow, no un instante real",
                })
            if prev_ts is not None and dt < prev_ts:
                result.temporal_anomalies.append({
                    "seq": link.seq,
                    "type": "NON_MONOTONIC_TIMESTAMP",
                    "timestamp": str(ts_raw),
                    "note": f"timestamp anterior al del eslabon seq={prev_seq} "
                            f"— orden causal imposible (efecto antes que causa)",
                })
            prev_ts, prev_seq = dt, link.seq

        sig = _content_signature(link.payload)
        if sig in seen_sig:
            result.temporal_anomalies.append({
                "seq": link.seq,
                "type": "DUPLICATE_CONTENT",
                "note": f"contenido identico al eslabon seq={seen_sig[sig]} "
                        f"— evento re-registrado (la cadena prueba insercion, "
                        f"no unicidad causal)",
            })
        else:
            seen_sig[sig] = link.seq

    result.timeline_plausible = not result.temporal_anomalies
