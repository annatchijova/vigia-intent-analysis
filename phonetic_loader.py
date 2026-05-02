"""
vigia/phonetic_loader.py
========================
VIGÍA — Loader unificado del diccionario fonético.

Problema que resuelve
---------------------
Antes de este módulo, el diccionario fonético se cargaba desde dos rutas
distintas e incompatibles:

  * phonetic_loader.py (raíz del proyecto)
      → carga <project_root>/phonetic_dict.json
      → usado por vigia_sift_bridge.py

  * vigia/tools/document_integrity.py
      → carga <project_root>/vigia/data/phonetic_dict.json
      → ruta hardcodeada que no existía en todos los entornos

Este módulo centraliza la carga con una estrategia de resolución de rutas
en cascada:

  1. Variable de entorno VIGIA_PHONETIC_DICT  (máxima prioridad — prod/CI)
  2. <vigia_package>/data/phonetic_dict.json  (instalación normal del paquete)
  3. <project_root>/phonetic_dict.json        (compatibilidad con bridge raíz)
  4. <cwd>/phonetic_dict.json                 (fallback desarrollo)

Si ninguna ruta produce un JSON válido, exporta dicts vacíos y logea el
error — nunca crashea en import.

Uso
---
    from vigia.phonetic_loader import (
        PHONETIC_MAP,
        HIGH_RISK_SET,
        RAW_DATA,
        reload_dict,
        get_stats,
    )

Compatibilidad con phonetic_loader.py de raíz
----------------------------------------------
El bridge (vigia_sift_bridge.py) importa desde el phonetic_loader.py
del raíz del proyecto. Ambos módulos exportan la misma interfaz:
PHONETIC_MAP, HIGH_RISK_SET, reload_dict, get_stats.
No hace falta migrar el bridge — puede seguir importando desde el raíz.
Este módulo es para uso interno de vigia/tools/*.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

# ── Audit logger for forensic trail (HMAC-signed) ────────────────────────
# Errors in the phonetic loader are security-relevant: a corrupted or
# tampered dictionary can cause false negatives in evasion detection.
# All failures are recorded in the HMAC-signed forensic audit log.
try:
    from vigia.security import audit_logger as _audit_logger
    _HAS_AUDIT_LOGGER = True
except ImportError:
    _HAS_AUDIT_LOGGER = False

# ---------------------------------------------------------------------------
# Estrategia de resolución de rutas (cascada)
# ---------------------------------------------------------------------------

_HERE: Final[Path] = Path(__file__).parent   # vigia/

_CANDIDATE_PATHS: list[Path] = [
    # 1. Variable de entorno — permite override en prod/CI sin cambiar código
    Path(os.environ["VIGIA_PHONETIC_DICT"])
    if "VIGIA_PHONETIC_DICT" in os.environ
    else Path("/dev/null"),   # placeholder — se filtra abajo

    # 2. vigia/data/phonetic_dict.json (instalación normal del paquete)
    _HERE / "data" / "phonetic_dict.json",

    # 3. <project_root>/phonetic_dict.json (compatibilidad con bridge raíz)
    _HERE.parent / "phonetic_dict.json",

    # 4. cwd fallback para desarrollo
    Path.cwd() / "phonetic_dict.json",
]

# Filtrar el placeholder si VIGIA_PHONETIC_DICT no está seteado
_CANDIDATE_PATHS = [p for p in _CANDIDATE_PATHS if str(p) != "/dev/null"]


def _resolve_dict_path() -> Path | None:
    """
    Recorre _CANDIDATE_PATHS y retorna el primero que existe.
    Retorna None si ninguno existe.
    """
    for candidate in _CANDIDATE_PATHS:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Secciones a ignorar al aplanar el dict
# ---------------------------------------------------------------------------

_SKIP_SECTIONS: Final[frozenset[str]] = frozenset({"_metadata", "homoglyph_patterns"})

# ---------------------------------------------------------------------------
# Estado interno (mutable en reload)
# ---------------------------------------------------------------------------

_raw_data: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Exports públicos
# ---------------------------------------------------------------------------

PHONETIC_MAP: dict[str, str] = {}    # fonético → "cirílico (traducción) [RISK]"
HIGH_RISK_SET: set[str]      = set() # claves con [HIGH RISK]
HOMOGLYPH_NOTES: dict[str, str] = {} # tabla de referencia de homoglifos
RAW_DATA: dict[str, Any]     = {}    # dict completo sin aplanar (para tools forenses)


# ---------------------------------------------------------------------------
# Lógica de carga
# ---------------------------------------------------------------------------

def _build_flat_map(
    raw: dict,
) -> tuple[dict[str, str], set[str], dict[str, str]]:
    """
    Aplana todas las secciones del dict en un mapa único de búsqueda.

    Retorna:
        flat        : {fonético: "cirílico..."} — para infer_intent
        high_risk   : {fonético, ...}           — subconjunto alto riesgo
        homoglyphs  : {char: description}       — tabla de referencia
    """
    flat: dict[str, str]       = {}
    high_risk: set[str]        = set()
    homoglyphs: dict[str, str] = {}

    for section_name, section in raw.items():
        if section_name in _SKIP_SECTIONS:
            continue
        if section_name == "_meta":
            continue
        if section_name == "homoglyph_patterns":
            entries = section.get("entries", section) if isinstance(section, dict) else {}
            homoglyphs = {
                k: v for k, v in entries.items()
                if not k.startswith("_")
            }
            continue
        if not isinstance(section, dict):
            continue
        # Soportar dos estructuras:
        # 1. {phonetic: meaning, ...}  — flat
        # 2. {description: ..., entries: {phonetic: {original, meaning, confidence}, ...}}
        entries = section.get("entries") if "entries" in section else section
        if not isinstance(entries, dict):
            continue
        for phonetic, meaning in entries.items():
            if phonetic.startswith("_") or phonetic == "description":
                continue
            # Si el valor es un dict con "meaning", extraer solo el string
            if isinstance(meaning, dict):
                display = meaning.get("meaning", str(meaning))
                confidence = meaning.get("confidence", 0.5)
                if confidence >= 0.9:
                    display += " [HIGH RISK]"
            else:
                display = str(meaning)
            flat[phonetic] = display
            if "[HIGH RISK]" in display:
                high_risk.add(phonetic)

    return flat, high_risk, homoglyphs


def reload_dict(path: Path | str | None = None) -> bool:
    """
    Carga o recarga el diccionario fonético desde disco.

    Si path es None, usa la estrategia de resolución de rutas en cascada.

    Retorna True si la carga fue exitosa, False si falló (mantiene estado
    anterior — nunca deja el módulo en estado parcial).

    Es seguro llamar en runtime sin reiniciar el servidor MCP.
    """
    global _raw_data, PHONETIC_MAP, HIGH_RISK_SET, HOMOGLYPH_NOTES, RAW_DATA

    def _log_error(event: str, msg: str) -> None:
        """Log to both stdlib logger and forensic audit trail."""
        logger.error(msg)
        if _HAS_AUDIT_LOGGER:
            _audit_logger.log_block(
                event_type=event,
                tool="vigia.phonetic_loader.reload_dict",
                input_preview=str(path or "(cascade)"),
                reason=msg,
            )

    def _log_info(msg: str) -> None:
        logger.info(msg)
        if _HAS_AUDIT_LOGGER:
            _audit_logger.log_info(
                event_type="PHONETIC_DICT_LOADED",
                tool="vigia.phonetic_loader",
                message=msg,
            )

    if path is not None:
        target = Path(path)
    else:
        target = _resolve_dict_path()

    if target is None:
        _log_error(
            "PHONETIC_DICT_NOT_FOUND",
            "phonetic_dict no encontrado en ninguna ruta candidata: "
            + ", ".join(str(p) for p in _CANDIDATE_PATHS)
            + ". Las tools forenses degradaran a reglas hardcodeadas."
        )
        return False

    # P3 fix (2026-04 audit): validacion basica de path.
    target_str = str(target)
    if ".." in target.parts:
        _log_error("PHONETIC_DICT_PATH_TRAVERSAL", f"path contiene '..': {target_str}")
        return False
    if "\x00" in target_str:
        _log_error("PHONETIC_DICT_NULL_BYTE", "path contiene null byte")
        return False
    if target.is_symlink():
        _log_error("PHONETIC_DICT_SYMLINK", f"path es un symlink: {target_str}")
        return False
    if not target_str.endswith(".json"):
        _log_error("PHONETIC_DICT_INVALID_EXT", f"path no termina en .json: {target_str}")
        return False

    if not target.exists():
        _log_error("PHONETIC_DICT_MISSING", f"phonetic_dict no existe: {target}")
        return False

    try:
        with open(target, "rb") as fh_bin:
            raw_bytes = fh_bin.read()

        # Gemini P0-5: Dictionary integrity check.
        # If VIGIA_PHONETIC_HASH is set, verify SHA-256 before parsing.
        # A poisoned dictionary can flip verdicts (e.g. remove all
        # Russian phonetic patterns → evasion goes undetected).
        expected_hash = os.getenv("VIGIA_PHONETIC_HASH", "").strip()
        if expected_hash:
            import hashlib
            actual_hash = hashlib.sha256(raw_bytes).hexdigest()
            if actual_hash != expected_hash:
                _log_error(
                    "PHONETIC_DICT_TAMPERED",
                    f"phonetic_dict SHA-256 mismatch. "
                    f"Expected: {expected_hash[:16]}... "
                    f"Got: {actual_hash[:16]}... "
                    f"File: {target}. Dictionary poisoning suspected."
                )
                return False

        new_raw = json.loads(raw_bytes.decode("utf-8"))

        flat, high_risk, homoglyphs = _build_flat_map(new_raw)

        # Swap atomico — nunca deja estado parcial
        _raw_data       = new_raw
        PHONETIC_MAP    = flat
        HIGH_RISK_SET   = high_risk
        HOMOGLYPH_NOTES = homoglyphs
        RAW_DATA        = new_raw

        _log_info(
            f"phonetic_dict cargado desde {target}: "
            f"{len(flat)} entradas, "
            f"{len(high_risk)} alto riesgo, "
            f"{len(homoglyphs)} notas de homoglifos."
        )
        return True

    except json.JSONDecodeError as exc:
        _log_error("PHONETIC_DICT_INVALID_JSON", f"JSON invalido en ({target}): {exc}")
        return False
    except OSError as exc:
        _log_error("PHONETIC_DICT_IO_ERROR", f"Error leyendo phonetic_dict ({target}): {exc}")
        return False


def get_stats() -> dict:
    """
    Retorna estadísticas del estado actual del diccionario.
    Útil para el tool get_phonetic_dict_stats del bridge.
    """
    resolved = _resolve_dict_path()
    return {
        "total_entries"     : len(PHONETIC_MAP),
        "high_risk_entries" : len(HIGH_RISK_SET),
        "homoglyph_notes"   : len(HOMOGLYPH_NOTES),
        "sections"          : [k for k in _raw_data if k not in _SKIP_SECTIONS],
        "resolved_path"     : str(resolved) if resolved else None,
        "candidate_paths"   : [str(p) for p in _CANDIDATE_PATHS],
        "loaded"            : bool(PHONETIC_MAP),
    }


def get_raw_section(section_name: str) -> dict:
    """
    Retorna una sección específica del diccionario sin aplanar.
    Usado por document_integrity.py para acceder a patrones estructurados
    (ej: document_forgery_indicators, gender_role_patterns_es_rioplatense).

    Retorna dict vacío si la sección no existe.
    """
    return _raw_data.get(section_name, {})


# ---------------------------------------------------------------------------
# Carga inicial al importar el módulo
# ---------------------------------------------------------------------------

reload_dict()
