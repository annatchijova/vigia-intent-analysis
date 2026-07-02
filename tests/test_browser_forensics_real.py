"""
tests/test_browser_forensics_real.py
======================================
Parser SQLite real de browser_forensics (antes stub que devolvía 0 → falso
negativo garantizado). Verifica Chromium + Firefox, extracción de nombre de
archivo Windows/POSIX, el caso UNANALYZED (DB ilegible) vs perfil vacío, y
que la evidencia NO se modifica (apertura read-only inmutable).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from vigia.sift.browser_forensics import BrowserForensicsEngine


def _chromium_history(path: Path, downloads, urls):
    db = path / "History"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        "CREATE TABLE downloads (id INTEGER PRIMARY KEY, target_path TEXT, "
        "total_bytes INT, opened INT, danger_type INT, tab_url TEXT);"
        "CREATE TABLE downloads_url_chains (id INT, chain_index INT, url TEXT);"
        "CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, visit_count INT);"
    )
    for i, (url, target) in enumerate(downloads, start=1):
        conn.execute("INSERT INTO downloads VALUES (?,?,?,?,?,?)",
                     (i, target, 1000, 1, 0, url))
        conn.execute("INSERT INTO downloads_url_chains VALUES (?,?,?)", (i, 0, url))
    for i, (url, title, vc) in enumerate(urls, start=1):
        conn.execute("INSERT INTO urls VALUES (?,?,?,?)", (i, url, title, vc))
    conn.commit()
    conn.close()
    return db


def _firefox_places(path: Path, urls):
    db = path / "places.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url TEXT, "
                 "title TEXT, visit_count INT)")
    for i, (url, title, vc) in enumerate(urls, start=1):
        conn.execute("INSERT INTO moz_places VALUES (?,?,?,?)", (i, url, title, vc))
    conn.commit()
    conn.close()
    return db


class TestChromium:
    def test_suspicious_download_detected(self, tmp_path):
        _chromium_history(
            tmp_path,
            downloads=[("http://evil.example/mimikatz.exe",
                        r"C:\Users\x\Downloads\mimikatz.exe"),
                       ("http://ok.example/notes.pdf",
                        r"C:\Users\x\Downloads\notes.pdf")],
            urls=[("https://news.example", "news", 5)],
        )
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert r.total_downloads == 2
        names = [s["filename"] for s in r.suspicious_downloads]
        assert "mimikatz.exe" in names          # basename Windows extraído
        assert "notes.pdf" not in names          # .pdf no es sospechoso
        assert r.to_signal().z_score >= 1.8

    def test_c2_navigation_detected(self, tmp_path):
        _chromium_history(
            tmp_path, downloads=[],
            urls=[("https://github.com/gentilkiwi/mimikatz", "mk", 3),
                  ("https://wikipedia.org", "wiki", 100)],
        )
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert len(r.c2_navigation) == 1
        assert r.c2_navigation[0]["matched_domain"] == "github.com/gentilkiwi"
        assert r.to_signal().z_score == pytest.approx(3.0)

    def test_clean_profile_is_benign_not_unanalyzed(self, tmp_path):
        _chromium_history(
            tmp_path,
            downloads=[("http://ok.example/report.pdf", r"C:\dl\report.pdf")],
            urls=[("https://wikipedia.org", "wiki", 100)],
        )
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert not r.suspicious_downloads and not r.c2_navigation
        assert r.unanalyzed is False              # limpio, no "no analizado"
        assert r.to_signal().z_score == 0.0


class TestFirefox:
    def test_c2_in_history(self, tmp_path):
        _firefox_places(tmp_path, urls=[
            ("https://download.sysinternals.com/psexec", "psexec", 2),
            ("https://example.org", "ok", 9),
        ])
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert len(r.c2_navigation) == 1
        assert r.c2_navigation[0]["matched_domain"] == "download.sysinternals.com"


class TestUnanalyzedVsEmpty:
    def test_corrupt_db_is_unanalyzed(self, tmp_path):
        (tmp_path / "History").write_bytes(b"not a sqlite database at all")
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert r.unanalyzed is True
        assert any("UNANALYZED_ARTIFACT" in n for n in r.analysis_notes)
        assert r.to_signal().metadata["unanalyzed"] is True

    def test_no_browser_db_is_not_unanalyzed(self, tmp_path):
        (tmp_path / "random.txt").write_text("nothing browser here")
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path))
        assert r.unanalyzed is False

    def test_missing_profile(self, tmp_path):
        r = BrowserForensicsEngine().analyze_profile(str(tmp_path / "nope"))
        assert r.total_downloads == 0 and not r.suspicious_downloads

    def test_signal_metadata_not_stub(self, tmp_path):
        _chromium_history(tmp_path, downloads=[], urls=[("https://x.org", "x", 1)])
        meta = BrowserForensicsEngine().analyze_profile(str(tmp_path)).to_signal().metadata
        assert "stub" not in meta                 # ya no es stub


class TestReadOnlyEvidence:
    def test_evidence_not_modified(self, tmp_path):
        # Apertura read-only inmutable: no se crean -wal/-journal ni se toca la DB.
        db = _chromium_history(
            tmp_path,
            downloads=[("http://evil/mimikatz.exe", r"C:\d\mimikatz.exe")],
            urls=[],
        )
        before = db.stat().st_mtime_ns
        BrowserForensicsEngine().analyze_profile(str(tmp_path))
        after = db.stat().st_mtime_ns
        assert before == after                    # mtime intacto
        aux = {p.name for p in tmp_path.iterdir()}
        assert aux == {"History"}                 # sin -wal / -journal


class TestBasename:
    @pytest.mark.parametrize("path,expected", [
        (r"C:\Users\x\Downloads\evil.exe", "evil.exe"),
        ("/home/u/dl/evil.exe", "evil.exe"),
        ("evil.exe", "evil.exe"),
        ("", ""),
    ])
    def test_basename_cross_platform(self, path, expected):
        assert BrowserForensicsEngine._basename(path) == expected


class TestAgentWiring:
    def test_build_kwargs_detects_browser_profile(self, tmp_path):
        # _build_orchestrator_kwargs debe fijar browser_profile al ver 'History'.
        from vigia_agent import _build_orchestrator_kwargs
        prof = tmp_path / "Default"
        prof.mkdir()
        (prof / "History").write_bytes(b"x")
        kwargs = _build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("browser_profile") == str(prof)

    def test_build_kwargs_detects_firefox_profile(self, tmp_path):
        from vigia_agent import _build_orchestrator_kwargs
        prof = tmp_path / "abc.default"
        prof.mkdir()
        (prof / "places.sqlite").write_bytes(b"x")
        kwargs = _build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("browser_profile") == str(prof)
