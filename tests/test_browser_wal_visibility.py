"""
Browser forensics — visibilidad del WAL no-checkpointeado (fix B-071 aplicado
a browser_forensics; diseñado en docs/SAFARI_WAL_FIX_ANALYSIS.md §5.2).

El FN cuantificado en tuck-2019 (macOS Safari): una History en modo WAL con
rows solo en el `-wal` era invisible para `mode=ro&immutable=1` — hasta el
100% de la señal perdida. `browser_forensics._connect_ro` (ruta Windows
Chrome/Edge/Firefox) tenía la misma apertura.

Fixtures: generadas EN LABORATORIO por este test (SQLite WAL con
wal_autocheckpoint=0 y el writer abierto durante el análisis, para que el
`-wal` no se checkpointee — misma receta que
tests/test_b071_sqlite_readonly.py::test_wal_data_is_visible). No son
evidencia real y no lo pretenden: prueban el contrato de lectura, no un caso.

Contrato verificado:
1. Rows solo-WAL de Chromium (downloads + urls) entran al análisis.
2. Rows solo-WAL de Firefox (moz_places) entran al análisis.
3. La evidencia NO se modifica: ni la DB ni su -wal cambian de hash, y no
   aparecen archivos nuevos en el directorio de evidencia.
4. Fallo de apertura (safe_sqlite_connect → None) se reporta como
   UNANALYZED_ARTIFACT, nunca como perfil limpio (patrón N7/N8).
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from vigia.sift.browser_forensics import BrowserForensicsEngine


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _chromium_wal_fixture(path: Path):
    """History de Chromium con baseline benigno en el main y los rows
    incriminatorios SOLO en el -wal. Retorna el writer ABIERTO — el caller
    debe cerrarlo después del análisis (si se cierra antes, SQLite
    checkpointea el WAL y el test no prueba nada)."""
    db = path / "History"
    w = sqlite3.connect(str(db))
    w.execute("PRAGMA journal_mode=WAL")
    w.execute("PRAGMA wal_autocheckpoint=0")
    w.executescript(
        "CREATE TABLE downloads (id INTEGER PRIMARY KEY, target_path TEXT, "
        "total_bytes INT, opened INT, danger_type INT, tab_url TEXT);"
        "CREATE TABLE downloads_url_chains (id INT, chain_index INT, url TEXT);"
        "CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INT);"
    )
    # baseline benigno → main DB
    w.execute("INSERT INTO urls VALUES (1, 'https://wikipedia.org', 'wiki', 100)")
    w.commit()
    w.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    # rows incriminatorios → SOLO al -wal
    w.execute("INSERT INTO downloads VALUES (1, 'C:\\\\Users\\\\x\\\\Downloads\\\\mimikatz.exe', "
              "1000, 1, 0, 'http://evil.example/mimikatz.exe')")
    w.execute("INSERT INTO downloads_url_chains VALUES (1, 0, 'http://evil.example/mimikatz.exe')")
    w.execute("INSERT INTO urls VALUES (2, 'https://github.com/gentilkiwi/mimikatz', 'mk', 3)")
    w.commit()
    assert (path / "History-wal").exists() and (path / "History-wal").stat().st_size > 0
    return w


def _firefox_wal_fixture(path: Path):
    """places.sqlite con el row C2 SOLO en el -wal. Retorna el writer abierto."""
    db = path / "places.sqlite"
    w = sqlite3.connect(str(db))
    w.execute("PRAGMA journal_mode=WAL")
    w.execute("PRAGMA wal_autocheckpoint=0")
    w.execute("CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT, "
              "title TEXT, visit_count INT)")
    w.execute("INSERT INTO moz_places VALUES (1, 'https://example.org', 'ok', 9)")
    w.commit()
    w.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    w.execute("INSERT INTO moz_places VALUES "
              "(2, 'https://download.sysinternals.com/psexec', 'psexec', 2)")
    w.commit()
    assert (path / "places.sqlite-wal").exists()
    return w


class TestChromiumWAL:
    def test_wal_only_rows_enter_analysis(self, tmp_path):
        w = _chromium_wal_fixture(tmp_path)
        try:
            r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        finally:
            w.close()
        # el download y la navegación C2 viven SOLO en el -wal
        assert r.total_downloads == 1, "download solo-WAL invisible (FN inmutable)"
        assert [s["filename"] for s in r.suspicious_downloads] == ["mimikatz.exe"]
        assert len(r.c2_navigation) == 1
        assert r.c2_navigation[0]["matched_domain"] == "github.com/gentilkiwi"
        assert r.to_signal().z_score == pytest.approx(3.0)

    def test_evidence_family_not_modified(self, tmp_path):
        w = _chromium_wal_fixture(tmp_path)
        try:
            hashes_before = {p.name: _sha(p) for p in sorted(tmp_path.iterdir())}
            BrowserForensicsEngine().analyze_profile(str(tmp_path))
            names_after = {p.name for p in tmp_path.iterdir()}
            assert names_after == set(hashes_before), "archivos nuevos en evidencia"
            # ni la DB ni el -wal fueron checkpointeados/escritos in place
            for p in sorted(tmp_path.iterdir()):
                assert _sha(p) == hashes_before[p.name], f"{p.name} modificado"
        finally:
            w.close()


class TestFirefoxWAL:
    def test_wal_only_history_enters_analysis(self, tmp_path):
        w = _firefox_wal_fixture(tmp_path)
        try:
            r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        finally:
            w.close()
        assert len(r.c2_navigation) == 1, "URL C2 solo-WAL invisible (FN inmutable)"
        assert r.c2_navigation[0]["matched_domain"] == "download.sysinternals.com"


class TestOpenFailureIsUnanalyzed:
    def test_none_connection_marks_unanalyzed_not_clean(self, tmp_path, monkeypatch):
        """safe_sqlite_connect retorna None (fallo de copia/apertura a nivel OS):
        el perfil debe salir UNANALYZED, jamás 'limpio con 0 hallazgos'."""
        import vigia.sift.browser_forensics as bf
        (tmp_path / "History").write_bytes(b"SQLite format 3\x00" + b"\x00" * 100)
        monkeypatch.setattr(bf, "safe_sqlite_connect", lambda *a, **k: None)
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert r.unanalyzed is True
        assert any("UNANALYZED_ARTIFACT" in n for n in r.analysis_notes)
