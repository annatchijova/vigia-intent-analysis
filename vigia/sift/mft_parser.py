"""
vigia/sift/mft_parser.py
=========================
Parser de `$MFT` binario (NTFS Master File Table) → JSON consumible por
`disk_forensics.MFTTimelineAnalyzer`.

Motivación (auditoría FN, P0-C): `MFTTimelineAnalyzer.analyze()` NO parsea el
`$MFT` binario — espera un JSON pre-extraído con `entries`. En modo agente
nada producía ese JSON, así que TODO análisis de disco/MFT quedaba ciego
(0 hallazgos = falso negativo). Este módulo cierra esa brecha con un parser
stdlib puro (struct), sin dependencias externas.

Alcance y límites (documentados para Daubert):
  - Extrae por registro FILE: record_number, flags (in-use/directory),
    hardlink_count, los 4 timestamps MACE de $STANDARD_INFORMATION (si_times)
    y de $FILE_NAME (fn_times), el nombre, el tamaño ($DATA), y los nombres de
    ADS ($DATA con nombre).
  - Suficiente para la detección de timestomping ($SI vs $FN), ADS, hardlinks
    y anomalías de secuencia que implementa MFTTimelineAnalyzer.
  - NO aplica el fixup de Update Sequence Array (USA). Los timestamps viven en
    el primer sector del registro, antes del primer límite de sector, así que
    el fixup no los afecta en la práctica. Se documenta como limitación.
  - entropy no se calcula (requiere el contenido de $DATA no-residente, que no
    está en el $MFT) → 0.

Timestamps NTFS: FILETIME de 64 bits = intervalos de 100ns desde 1601-01-01.
Se convierten a ISO 8601 UTC.
"""
from __future__ import annotations

import json
import struct
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# FILETIME(1601) → Unix(1970): segundos entre ambas épocas.
_FILETIME_EPOCH_DIFF = 11644473600
_HUNDREDS_NS = 10_000_000

# Flags del header del registro FILE
_FLAG_IN_USE = 0x01
_FLAG_DIRECTORY = 0x02

# Tipos de atributo NTFS
_ATTR_STANDARD_INFORMATION = 0x10
_ATTR_FILE_NAME = 0x30
_ATTR_DATA = 0x80
_ATTR_END = 0xFFFFFFFF

_RECORD_SIZE_DEFAULT = 1024


def _filetime_to_iso(ft: int) -> str:
    """FILETIME (100ns desde 1601) → ISO 8601 UTC. '' si es 0/ inválido."""
    if ft <= 0:
        return ""
    unix = ft / _HUNDREDS_NS - _FILETIME_EPOCH_DIFF
    if unix < 0 or unix > 32503680000:  # fuera de [1970, 3000] → corrupto
        return ""
    try:
        return datetime.fromtimestamp(unix, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, OverflowError, OSError):
        return ""


def _parse_standard_information(content: bytes) -> List[str]:
    """4 timestamps MACE de $STANDARD_INFORMATION: created, modified, mft_mod, accessed."""
    if len(content) < 32:
        return []
    created, modified, mft_modified, accessed = struct.unpack_from("<QQQQ", content, 0)
    return [_filetime_to_iso(t) for t in (created, modified, mft_modified, accessed)]


def _parse_file_name(content: bytes) -> Dict[str, Any]:
    """
    $FILE_NAME: 4 timestamps MACE (offset 8), tamaño, flags, y el nombre
    (UTF-16LE) al final. Namespace en offset 0x41.
    """
    if len(content) < 66:
        return {}
    created, modified, mft_modified, accessed = struct.unpack_from("<QQQQ", content, 8)
    name_len = content[64]
    namespace = content[65]
    name = ""
    try:
        raw = content[66:66 + name_len * 2]
        name = raw.decode("utf-16-le", errors="replace")
    except Exception:
        name = ""
    return {
        "fn_times": [_filetime_to_iso(t) for t in (created, modified, mft_modified, accessed)],
        "filename": name,
        "namespace": namespace,
    }


def _parse_record(data: bytes, record_number: int) -> Optional[Dict[str, Any]]:
    """Parsea un registro FILE de la MFT. Devuelve el dict de entrada o None."""
    if len(data) < 48 or data[0:4] != b"FILE":
        return None

    hardlink_count = struct.unpack_from("<H", data, 0x12)[0]
    first_attr_off = struct.unpack_from("<H", data, 0x14)[0]
    flags_word = struct.unpack_from("<H", data, 0x16)[0]
    in_use = bool(flags_word & _FLAG_IN_USE)
    is_dir = bool(flags_word & _FLAG_DIRECTORY)

    si_times: List[str] = []
    fn_candidates: List[Dict[str, Any]] = []
    ads_names: List[str] = []
    file_size = 0

    offset = first_attr_off
    # Recorrer la lista de atributos hasta el marcador de fin o el borde.
    while offset + 4 <= len(data):
        attr_type = struct.unpack_from("<I", data, offset)[0]
        if attr_type == _ATTR_END or attr_type == 0:
            break
        if offset + 8 > len(data):
            break
        attr_len = struct.unpack_from("<I", data, offset + 4)[0]
        if attr_len == 0 or offset + attr_len > len(data):
            break
        non_resident = data[offset + 8]
        name_len = data[offset + 9]
        name_off = struct.unpack_from("<H", data, offset + 10)[0]
        attr_name = ""
        if name_len:
            try:
                attr_name = data[offset + name_off:offset + name_off + name_len * 2].decode(
                    "utf-16-le", errors="replace")
            except Exception:
                attr_name = ""

        if non_resident == 0:  # atributo residente
            content_size = struct.unpack_from("<I", data, offset + 16)[0]
            content_off = struct.unpack_from("<H", data, offset + 20)[0]
            content = data[offset + content_off:offset + content_off + content_size]
            if attr_type == _ATTR_STANDARD_INFORMATION:
                si_times = _parse_standard_information(content)
            elif attr_type == _ATTR_FILE_NAME:
                parsed = _parse_file_name(content)
                if parsed:
                    fn_candidates.append(parsed)
            elif attr_type == _ATTR_DATA:
                if attr_name:  # $DATA con nombre = Alternate Data Stream
                    ads_names.append(attr_name)
                else:
                    file_size = max(file_size, content_size)
        else:  # atributo no-residente
            if offset + 0x38 <= len(data):
                real_size = struct.unpack_from("<Q", data, offset + 0x30)[0]
                if attr_type == _ATTR_DATA:
                    if attr_name:
                        ads_names.append(attr_name)
                    else:
                        file_size = max(file_size, real_size)

        offset += attr_len

    # Elegir el $FILE_NAME preferente: namespace Win32(1)/Win32+DOS(3) sobre DOS(2).
    fn_times: List[str] = []
    filename = ""
    if fn_candidates:
        best = sorted(
            fn_candidates,
            key=lambda c: {1: 0, 3: 0, 0: 1, 2: 2}.get(c.get("namespace", 0), 3),
        )[0]
        fn_times = best.get("fn_times", [])
        filename = best.get("filename", "")

    flags: List[str] = []
    flags.append("IN_USE" if in_use else "NOT_IN_USE")
    if is_dir:
        flags.append("DIRECTORY")
    if file_size <= 1024 and not is_dir:
        # $DATA residente cabe en el registro (heurística usada por el analyzer)
        flags.append("RESIDENT")

    return {
        "record_number": record_number,
        "filename": filename or "UNKNOWN",
        "filepath": "",
        "si_times": si_times,
        "fn_times": fn_times,
        "hardlink_count": hardlink_count,
        "ads": sorted(ads_names),
        "file_size": file_size,
        "flags": flags,
        "entropy": 0,
    }


def parse_mft_bytes(data: bytes, record_size: int = _RECORD_SIZE_DEFAULT) -> Dict[str, Any]:
    """
    Parsea un `$MFT` completo en memoria → {"entries": [...]}.

    Solo se incluyen registros con firma FILE válida. Los registros libres
    (no FILE) se saltan. Determinístico: mismo input → mismo output.
    """
    entries: List[Dict[str, Any]] = []
    if not data:
        return {"entries": []}

    n_records = len(data) // record_size
    for i in range(n_records):
        chunk = data[i * record_size:(i + 1) * record_size]
        entry = _parse_record(chunk, i)
        if entry is not None:
            entries.append(entry)
    return {"entries": entries}


def parse_mft_file(path: str, record_size: int = _RECORD_SIZE_DEFAULT) -> str:
    """Lee un `$MFT` de disco y devuelve el JSON de entries (string)."""
    with open(path, "rb") as f:
        data = f.read()
    return json.dumps(parse_mft_bytes(data, record_size), sort_keys=True)
