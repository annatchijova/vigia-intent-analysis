"""
B-071 — acceso SQLite de evidencia read-only + immutable (patrón sistémico S1).

Contrato compartido (cierra la clase en los 3 módulos a la vez):
1. Abre una DB válida y LEE, sin escribir ningún archivo nuevo (-wal/-journal).
2. La conexión es read-only: un INSERT falla.
3. Un path inexistente NO crea DB vacía y retorna None.
4. Los tres _safe_sqlite_connect delegan al helper y comparten el contrato.
"""

import os
import sqlite3
import logging

import pytest

from vigia.sift._sql_utils import safe_sqlite_connect
from vigia.sift.ios_forensics import iOSForensicsAnalyzer
from vigia.sift.android_forensics import AndroidForensicsAnalyzer
from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

_LOG = logging.getLogger("test_b071")


@pytest.fixture
def valid_db(tmp_path):
    p = tmp_path / "evidence.db"
    c = sqlite3.connect(str(p))
    c.execute("CREATE TABLE msg(id INTEGER, body TEXT)")
    c.execute("INSERT INTO msg VALUES (1, 'hola')")
    c.commit()
    c.close()
    return p


class TestSharedContract:
    def test_reads_without_writing(self, valid_db, tmp_path):
        before = set(os.listdir(tmp_path))
        conn = safe_sqlite_connect(valid_db, "TEST", _LOG)
        assert conn is not None
        rows = conn.execute("SELECT body FROM msg").fetchall()
        conn.close()
        assert rows == [("hola",)]
        # invariante evidencia: ningún archivo nuevo (no -wal, no -journal)
        assert set(os.listdir(tmp_path)) == before

    def test_connection_is_readonly(self, valid_db):
        conn = safe_sqlite_connect(valid_db, "TEST", _LOG)
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("INSERT INTO msg VALUES (2, 'x')")
        conn.close()

    def test_missing_path_returns_none_and_creates_nothing(self, tmp_path):
        missing = tmp_path / "does_not_exist.db"
        conn = safe_sqlite_connect(missing, "TEST", _LOG)
        assert conn is None
        assert not missing.exists()  # NO se creó DB vacía

    def test_malformed_db_opens_lazy_error_at_query(self, tmp_path):
        p = tmp_path / "bad.db"
        p.write_bytes(b"SQLite format 3\x00" + b"\xff" * 200)
        conn = safe_sqlite_connect(p, "TEST", _LOG)
        # connect es lazy: abre; el error surge en el query (lo captura el parser)
        assert conn is not None
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute("SELECT * FROM sqlite_master").fetchall()
        conn.close()


class TestModulesDelegate:
    @pytest.mark.parametrize("analyzer_cls", [
        iOSForensicsAnalyzer, AndroidForensicsAnalyzer, MacOSForensicsAnalyzer,
    ])
    def test_module_safe_connect_is_readonly(self, analyzer_cls, valid_db):
        a = analyzer_cls()
        conn = a._safe_sqlite_connect(valid_db)
        assert conn is not None
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("INSERT INTO msg VALUES (9, 'z')")
        conn.close()

    @pytest.mark.parametrize("analyzer_cls", [
        iOSForensicsAnalyzer, AndroidForensicsAnalyzer, MacOSForensicsAnalyzer,
    ])
    def test_module_missing_path_no_create(self, analyzer_cls, tmp_path):
        missing = tmp_path / "nope.db"
        a = analyzer_cls()
        assert a._safe_sqlite_connect(missing) is None
        assert not missing.exists()
