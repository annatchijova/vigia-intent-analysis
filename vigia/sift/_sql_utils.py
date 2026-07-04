"""
vigia.sift._sql_utils — acceso compartido a SQLite de evidencia (B-071).

Cierra el patrón sistémico S1 de AUDITORIA_COBERTURA_MOBILE_SIFT: los tres
motores mobile (iOS/Android/macOS) tenían `_safe_sqlite_connect` idénticos que
abrían la DB con `sqlite3.connect(str(path))` — read-WRITE, y sobre un path
inexistente CREAN una DB vacía. Consecuencias forenses:

- **Escritura en evidencia:** una DB con WAL/journal sucio dispara auto-recovery
  de SQLite que escribe `-wal`/`-journal` de vuelta en `VIGIA_EVIDENCE_DIR` →
  viola el invariante #1 de CLAUDE.md (evidencia read-only) y rompe la cadena
  de custodia bajo Daubert.
- **DB vacía silenciosa:** `connect()` a un path ausente crea un archivo vacío
  → 0 hallazgos → lee como "limpio" (familia P0-A: incapacidad presentada como
  benignidad).

`mode=ro&immutable=1` garantiza cero escrituras y se niega a crear/recuperar.
Una sola implementación, un solo test de contrato.
"""

import sqlite3
import urllib.parse
from pathlib import Path
from typing import Optional


def safe_sqlite_connect(db_path, module_tag: str, logger) -> Optional[sqlite3.Connection]:
    """Abre una SQLite de evidencia READ-ONLY + immutable.

    Retorna la conexión, o None si el archivo no existe / no se puede abrir
    (nunca crea, nunca escribe). El error de una DB malformada es lazy —
    surge en el primer query, y lo captura el parser que la usa.
    """
    try:
        uri = "file:" + urllib.parse.quote(str(db_path)) + "?mode=ro&immutable=1"
        return sqlite3.connect(uri, uri=True)
    except (sqlite3.Error, OSError) as e:
        logger.error("[%s] Cannot open SQLite database %s (read-only): %s",
                     module_tag, db_path, e)
        return None
