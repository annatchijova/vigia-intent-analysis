"""
vigia.sift._sql_utils — acceso compartido a SQLite de evidencia (B-071).

Cierra el patrón sistémico S1 de AUDITORIA_COBERTURA_MOBILE_SIFT y el falso
negativo que el red-team (AUDITORIA_REDTEAM_P1_MOBILE) encontró en el fix v1.

Invariante #1 de CLAUDE.md: la evidencia es READ-ONLY. Abrir la SQLite de
evidencia en su lugar es imposible de hacer bien:
  - `sqlite3.connect(str(path))` (crudo) → read-WRITE: auto-recovery de un
    WAL/journal sucio escribe `-wal`/`-journal` en `VIGIA_EVIDENCE_DIR`, y un
    path ausente CREA una DB vacía (0 hallazgos lee limpio).
  - `mode=ro` → crea el `-shm` (32 KB) en el directorio de evidencia.
  - `mode=ro&immutable=1` → NO escribe, pero IGNORA el `-wal`: una DB en modo
    WAL con datos en el `-wal` (estado normal de un teléfono vivo) se lee como
    tabla vacía → falso negativo GRAVE (evidencia inculpatoria invisible).

Solución forense estándar (fix v2 — copy-to-working-dir): copiar la familia
`db` + `-wal` + `-shm` + `-journal` a un working dir efímero y abrir la COPIA
read-write ahí. Satisface los dos invariantes a la vez: cero escritura en
evidencia Y lectura completa del WAL. El working dir se borra al cerrar la
conexión (y por backstop de GC si el caller no cierra).

Limitación (L, honesta §5.3): copia el archivo — costo O(tamaño de la DB) por
artefacto. Aceptable: los callers acotan cuántas DBs abren (`_safe_rglob`
limit=N). Para una imagen estática la copia es punto-en-tiempo y consistente.
"""

import os
import shutil
import sqlite3
import tempfile
import weakref
from typing import Optional

# Sidecars que SQLite usa junto al archivo principal — deben copiarse con el
# MISMO basename para que el motor los encuentre.
_SQLITE_SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")


class _WorkingCopyConnection(sqlite3.Connection):
    """sqlite3.Connection sobre una copia de trabajo: borra su working dir al
    cerrar. La copia es descartable, así que la conexión es read-write sin
    riesgo — la evidencia original nunca se abre."""

    _vigia_workdir: Optional[str] = None

    def close(self) -> None:
        try:
            super().close()
        finally:
            wd = self.__dict__.get("_vigia_workdir")
            if wd:
                shutil.rmtree(wd, ignore_errors=True)
                self.__dict__["_vigia_workdir"] = None


def safe_sqlite_connect(db_path, module_tag: str, logger) -> Optional[sqlite3.Connection]:
    """Abre una SQLite de evidencia SIN tocarla: copia la familia de archivos a
    un working dir efímero y abre la copia. Retorna la conexión (que limpia su
    working dir al cerrar), o None si el archivo no existe / no se puede abrir.
    Nunca crea ni escribe en el path de evidencia. Un error de DB malformada es
    lazy — surge en el primer query, y lo captura el parser que la usa.
    """
    db_path = str(db_path)
    if not os.path.isfile(db_path):
        # path ausente → None (nunca crea). Distinto de una DB vacía real.
        return None

    workdir = None
    try:
        workdir = tempfile.mkdtemp(prefix="vigia_sqlite_")
        base = os.path.basename(db_path)
        shutil.copy2(db_path, os.path.join(workdir, base))
        for suffix in _SQLITE_SIDECAR_SUFFIXES:
            side = db_path + suffix
            if os.path.isfile(side):
                shutil.copy2(side, os.path.join(workdir, base + suffix))

        conn = sqlite3.connect(
            os.path.join(workdir, base), factory=_WorkingCopyConnection
        )
        conn.__dict__["_vigia_workdir"] = workdir
        # Backstop: si el caller nunca cierra, el GC borra el working dir.
        weakref.finalize(conn, shutil.rmtree, workdir, True)
        return conn
    except (OSError, sqlite3.Error) as e:
        logger.error(
            "[%s] Cannot open SQLite evidence %s (working copy): %s",
            module_tag, db_path, e,
        )
        if workdir:
            shutil.rmtree(workdir, ignore_errors=True)
        return None
