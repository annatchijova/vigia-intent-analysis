"""
vigia/sift/fsevents_parser.py

Parser autocontenido del journal FSEvents de macOS (`/.fseventsd/`).

Formato (page-based, gzip): cada archivo del directorio `.fseventsd` (nombre =
16 dígitos hex del event-stream id) es gzip. Descomprimido, es una secuencia de
PÁGINAS; cada página:

    signature : 4 bytes  — b"1SLD" (v1 / DLS1) | b"2SLD" (v2 / DLS2)
    unknown   : uint32 LE
    page_size : uint32 LE — tamaño total de la página, header incluido

seguido de registros hasta consumir `page_size`:

    v1 (DLS1): path (cstring UTF-8 null-terminated) + event_id uint64 LE
               + flags uint32 LE
    v2 (DLS2): idem + node_id uint64 LE   (inode/CNID)

La firma de página y el layout siguen la definición de plaso
(`fseventsd`, Apache-2.0). El mapa de FLAGS es de INGENIERÍA INVERSA de la
comunidad DFIR (mac_apt / FSEventsParser) — NO especificación de Apple; se
expone el entero crudo `flags` además de los nombres para trazabilidad Daubert.

Sin timestamp por registro: FSEvents solo ordena por event_id. El tiempo se
acota por rango externo (mtime del archivo, eventos Mount/Unmount, correlación
con otros artefactos). Los consumidores deben tratar el tiempo como acotado,
no puntual.

Determinismo: parser puro, sin floats. Techo de tamaño (S5) contra bombas de
descompresión.
"""

from __future__ import annotations

import gzip
import logging
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

logger = logging.getLogger(__name__)

# Firmas de página (bytes on-disk, convención plaso).
_SIG_V1 = b"1SLD"
_SIG_V2 = b"2SLD"
_HEADER = struct.Struct("<4sII")   # signature, unknown, page_size
_HEADER_LEN = _HEADER.size          # 12

# S5: techo de descompresión por archivo (los .fseventsd reales miden KB–MB;
# 64 MiB es holgado por órdenes de magnitud y corta bombas de gzip).
_MAX_DECOMPRESSED = 64 * 1024 * 1024

# Mapa de flags — INGENIERÍA INVERSA (mac_apt / FSEventsParser), NO Apple.
# Se usa el subconjunto ampliamente coincidente entre referencias.
FSEVENT_FLAGS = {
    0x00000001: "FolderEvent",
    0x00000002: "Mount",
    0x00000004: "Unmount",
    0x00000020: "EndOfTransaction",
    0x00000800: "LastHardLinkRemoved",
    0x00001000: "HardLink",
    0x00004000: "SymbolicLink",
    0x00008000: "FileEvent",
    0x00010000: "PermissionChange",
    0x00020000: "ExtendedAttrModified",
    0x00040000: "ExtendedAttrRemoved",
    0x00100000: "DocumentRevisioning",
    0x00400000: "Created",
    0x00800000: "Removed",
    0x01000000: "InodeMetaMod",
    0x02000000: "Renamed",
    0x04000000: "Modified",
    0x08000000: "Exchange",
    0x10000000: "FinderInfoMod",
    0x20000000: "FolderCreated",
    0x40000000: "Mount2",
    0x80000000: "Unmount2",
}

# Bits de mayor valor forense (bien coincididos entre referencias).
FLAG_CREATED = 0x00400000
FLAG_REMOVED = 0x00800000
FLAG_RENAMED = 0x02000000
FLAG_MOUNT = 0x00000002
FLAG_UNMOUNT = 0x00000004


@dataclass(frozen=True)
class FSEvent:
    path: str
    event_id: int
    flags: int
    node_id: int = 0             # 0 en DLS1 (no existe)
    version: int = 2

    @property
    def flag_names(self) -> List[str]:
        return [name for bit, name in sorted(FSEVENT_FLAGS.items())
                if self.flags & bit]

    @property
    def is_removed(self) -> bool:
        return bool(self.flags & FLAG_REMOVED)

    @property
    def is_created(self) -> bool:
        return bool(self.flags & FLAG_CREATED)


@dataclass
class FSEventsParseResult:
    events: List[FSEvent]
    pages_parsed: int = 0
    unsupported_pages: int = 0    # firma desconocida (p.ej. DLS3) — honesto
    files_parsed: int = 0
    files_rejected: int = 0       # techo de tamaño / gzip inválido
    store_uuid: str = ""
    notes: List[str] = None       # type: ignore

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


def _iter_page_records(page: bytes, version: int) -> Iterator[FSEvent]:
    """Itera registros de UNA página (sin header). Tolerante: se detiene ante
    un registro truncado en vez de crashear (degradación honesta)."""
    off = 0
    n = len(page)
    id_struct = struct.Struct("<Q")
    flags_struct = struct.Struct("<I")
    while off < n:
        nul = page.find(b"\x00", off)
        if nul == -1:
            break  # path sin terminador → cola truncada
        try:
            path = page[off:nul].decode("utf-8", errors="replace")
        except Exception:
            path = page[off:nul].decode("latin-1", errors="replace")
        cur = nul + 1
        # event_id (8) + flags (4) [+ node_id (8) en v2]
        need = 12 + (8 if version >= 2 else 0)
        if cur + need > n:
            break  # registro truncado
        event_id = id_struct.unpack_from(page, cur)[0]
        cur += 8
        flags = flags_struct.unpack_from(page, cur)[0]
        cur += 4
        node_id = 0
        if version >= 2:
            node_id = id_struct.unpack_from(page, cur)[0]
            cur += 8
        off = cur
        yield FSEvent(path=path, event_id=event_id, flags=flags,
                      node_id=node_id, version=version)


def parse_fsevents_bytes(data: bytes, result: FSEventsParseResult) -> None:
    """Parsea el contenido DESCOMPRIMIDO de un archivo .fseventsd (una o más
    páginas) y acumula en `result`. Firma desconocida → cuenta como
    unsupported_page y se detiene (no adivina layout)."""
    off = 0
    total = len(data)
    while off + _HEADER_LEN <= total:
        sig, _unknown, page_size = _HEADER.unpack_from(data, off)
        if sig == _SIG_V1:
            version = 1
        elif sig == _SIG_V2:
            version = 2
        else:
            result.unsupported_pages += 1
            result.notes.append(
                f"firma de página no soportada {sig!r} (¿DLS3/corrupción?) — "
                f"omitida (degradación honesta)"
            )
            break
        if page_size < _HEADER_LEN or off + page_size > total:
            result.notes.append(
                f"page_size inválido ({page_size}) en offset {off} — detenido"
            )
            break
        body = data[off + _HEADER_LEN: off + page_size]
        for ev in _iter_page_records(body, version):
            result.events.append(ev)
        result.pages_parsed += 1
        off += page_size


def _safe_decompress(path: Path) -> Optional[bytes]:
    """gzip-descomprime con techo de tamaño (S5). Devuelve None si el archivo
    no es gzip válido o excede el techo (registrado como rechazo)."""
    try:
        with gzip.open(path, "rb") as f:
            data = f.read(_MAX_DECOMPRESSED + 1)
        if len(data) > _MAX_DECOMPRESSED:
            logger.warning("[FSEVENTS] %s excede %d bytes descomprimidos — "
                           "rechazado (S5)", path, _MAX_DECOMPRESSED)
            return None
        return data
    except Exception as e:
        # Amplio a propósito: un .fseventsd controlado por el atacante puede ser
        # gzip válido con deflate corrupto (zlib.error — NO subclase de OSError),
        # truncado (EOFError), o cualquier otra corrupción. El contrato es
        # degradación HONESTA por-archivo: un archivo hostil rechaza SOLO ese
        # archivo, nunca aborta el análisis del resto (ni de otros dominios).
        logger.debug("[FSEVENTS] archivo ilegible %s: %s", path, e)
        return None


def parse_fseventsd_dir(fsdir: Path, limit: int = 200) -> FSEventsParseResult:
    """Parsea un directorio `.fseventsd`. Ordena los archivos por nombre
    (determinista); los nombres hex ordenan por event-stream id. `limit`
    acota el número de archivos procesados (memoria)."""
    result = FSEventsParseResult(events=[])
    if not fsdir.is_dir():
        result.notes.append(f"{fsdir} no es un directorio")
        return result
    files = []
    for p in sorted(fsdir.iterdir(), key=lambda x: x.name):
        if p.is_symlink() or not p.is_file():
            continue
        if p.name == "fseventsd-uuid":
            try:
                result.store_uuid = p.read_text(errors="replace").strip()[:64]
            except OSError:
                pass
            continue
        files.append(p)
    for p in files[:limit]:
        data = _safe_decompress(p)
        if data is None:
            result.files_rejected += 1
            continue
        parse_fsevents_bytes(data, result)
        result.files_parsed += 1
    if len(files) > limit:
        result.notes.append(
            f"{len(files) - limit} archivo(s) .fseventsd omitido(s) por limit={limit}"
        )
    return result
