"""
Tests del parser de plists satélite de Safari (Bookmarks.plist /
LastSession.plist) en macos_forensics._analyze_safari_plists
(MACOS_MODULES_DESIGN §3.1).

Doble validación:
- GROUND TRUTH: los 13 bookmarks reales de cases/tuck-2019-macos (todos
  benignos → 0 findings) — prueba que la extracción es correcta sobre datos
  reales, no solo sintéticos.
- SINTÉTICO: bookmarks/pestañas con URLs de exploit plantadas → findings
  SAFARI_* que integran a la misma escalera que el historial.
"""

from __future__ import annotations

import plistlib
from pathlib import Path

import pytest

from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

_TUCK = Path("cases/tuck-2019-macos")


def _analyze(root: Path):
    return MacOSForensicsAnalyzer().analyze(root)


def _safari_dir(tmp_path: Path) -> Path:
    d = tmp_path / "Users" / "x" / "Library" / "Safari"
    d.mkdir(parents=True)
    # marker macOS para que analyze() no aborte por "no macOS artifacts"
    (tmp_path / "SystemVersion.plist").write_bytes(
        plistlib.dumps({"ProductVersion": "13.0"}))
    return d


def _write_bookmarks(safari: Path, leaves):
    children = [
        {"WebBookmarkType": "WebBookmarkTypeLeaf",
         "URLString": url,
         "URIDictionary": {"title": title}}
        for url, title in leaves
    ]
    tree = {"WebBookmarkType": "WebBookmarkTypeList", "Children": children}
    (safari / "Bookmarks.plist").write_bytes(plistlib.dumps(tree))


def _write_session(safari: Path, tabs):
    doc = {"SessionVersion": "1.0", "SessionWindows": [
        {"TabStates": [{"TabURL": u, "TabTitle": t} for u, t in tabs]}
    ]}
    (safari / "LastSession.plist").write_bytes(plistlib.dumps(doc))


class TestRealTuckBookmarks:
    def test_tuck_bookmarks_parse_but_are_benign(self):
        if not (_TUCK / "Safari" / "Bookmarks.plist").exists():
            pytest.skip("tuck-2019 fixture ausente")
        r = _analyze(_TUCK)
        # El parser leyó los 13 bookmarks reales (nota de conteo) …
        assert any("13 bookmark(s)" in n for n in r.analysis_notes), r.analysis_notes
        # … y ninguno es sospechoso → 0 findings de bookmark (los 23
        # SAFARI_SUSPICIOUS del historial no cambian).
        bookmark_findings = [
            f for f in r.findings
            if "BOOKMARK" in f.rule_ref or "bookmark" in f.evidence.lower()
        ]
        assert bookmark_findings == []

    def test_tuck_verdict_signal_unchanged(self):
        if not (_TUCK / "Safari" / "Bookmarks.plist").exists():
            pytest.skip("tuck-2019 fixture ausente")
        r = _analyze(_TUCK)
        assert r.to_signal().z_score == 1.6  # sin cambio (B-052-P2 baseline)


class TestSyntheticSuspiciousBookmarks:
    def test_exploit_bookmark_flagged(self, tmp_path):
        safari = _safari_dir(tmp_path)
        _write_bookmarks(safari, [
            ("https://www.apple.com/", "Apple"),
            ("https://exploit-db.com/exploits/CVE-2024-1234", "metasploit payload"),
        ])
        r = _analyze(tmp_path)
        fts = [f for f in r.findings if f.finding_type == "SAFARI_EXPLOIT_RESEARCH"]
        assert fts, [f.finding_type for f in r.findings]
        f = fts[0]
        assert f.corr_group == "browser_suspicious"
        assert "bookmark" in f.evidence.lower()

    def test_suspicious_session_tab_flagged(self, tmp_path):
        safari = _safari_dir(tmp_path)
        _write_session(safari, [
            ("https://news.example.com", "News"),
            ("https://forum.example/how-to-hack-wifi", "how to hack"),
        ])
        r = _analyze(tmp_path)
        assert any(f.finding_type == "SAFARI_SUSPICIOUS"
                   and "session" in f.evidence.lower() for f in r.findings)

    def test_antiforensic_bookmark_goes_to_antiforensic_group(self, tmp_path):
        safari = _safari_dir(tmp_path)
        _write_bookmarks(safari, [
            ("https://www.bleachbit.org/download", "BleachBit disk cleaner"),
        ])
        r = _analyze(tmp_path)
        af = [f for f in r.findings if f.finding_type == "ANTIFORENSIC_SEARCH"]
        assert af and af[0].corr_group == "antiforensic"

    def test_benign_bookmarks_no_findings(self, tmp_path):
        safari = _safari_dir(tmp_path)
        _write_bookmarks(safari, [
            ("https://www.apple.com/", "Apple"),
            ("https://www.wikipedia.org/", "Wikipedia"),
        ])
        r = _analyze(tmp_path)
        assert not any("bookmark" in f.evidence.lower() for f in r.findings)

    def test_nskeyedarchiver_bookmarks_degraded_not_crash(self, tmp_path):
        safari = _safari_dir(tmp_path)
        (safari / "Bookmarks.plist").write_bytes(plistlib.dumps({
            "$archiver": "NSKeyedArchiver", "$objects": [], "$top": {}}))
        r = _analyze(tmp_path)
        assert any("NSKeyedArchiver no desreferenciado" in n
                   for n in r.analysis_notes)
        assert not any("Safari plist error" in n for n in r.analysis_notes)

    def test_deeply_nested_bookmarks_do_not_hang(self, tmp_path):
        # Guard de profundidad: árbol de 100 niveles no debe crashear/colgar.
        safari = _safari_dir(tmp_path)
        node = {"WebBookmarkType": "WebBookmarkTypeLeaf",
                "URLString": "https://x", "URIDictionary": {"title": "x"}}
        for _ in range(100):
            node = {"WebBookmarkType": "WebBookmarkTypeList", "Children": [node]}
        (safari / "Bookmarks.plist").write_bytes(plistlib.dumps(node))
        r = _analyze(tmp_path)  # no debe lanzar
        assert not any("Safari plist error" in n for n in r.analysis_notes)


class TestSecurityHardening:
    def test_shared_ref_dag_does_not_hang(self, tmp_path):
        # Hallazgo code-review: un bplist con refs compartidas (DAG) explotaba
        # exponencial. Se construye un DAG de 20 niveles donde cada nivel
        # apunta 100 veces al mismo nodo siguiente — como árbol serían 100^20
        # visitas; con dedup por id() es O(20). Debe terminar de inmediato.
        import time
        leaf = {"WebBookmarkType": "WebBookmarkTypeLeaf",
                "URLString": "https://x", "URIDictionary": {"title": "x"}}
        node = leaf
        for _ in range(20):
            node = {"WebBookmarkType": "WebBookmarkTypeList",
                    "Children": [node] * 100}  # 100 refs AL MISMO objeto
        out = []
        t0 = time.perf_counter()
        MacOSForensicsAnalyzer._iter_bookmark_leaves(node, out)
        assert time.perf_counter() - t0 < 2.0, "DAG bplist colgó el parser"
        # con dedup, la hoja compartida se visita una vez
        assert len(out) == 1

    def test_decoy_bookmarks_do_not_evict_real_safari(self, tmp_path):
        # Hallazgo code-review: decoys Bookmarks.plist fuera de Safari,
        # ordenados antes, evictaban el real. Se plantan 3 decoys en rutas que
        # ordenan antes de "Users/.../Safari" y el real con un exploit.
        for i, d in enumerate(("Applications/A", "Library/B", "Library/C")):
            dd = tmp_path / d
            dd.mkdir(parents=True)
            (dd / "Bookmarks.plist").write_bytes(plistlib.dumps(
                {"WebBookmarkType": "WebBookmarkTypeList", "Children": []}))
        safari = _safari_dir(tmp_path)
        _write_bookmarks(safari, [
            ("https://exploit-db.com/CVE-2024-9999", "metasploit"),
        ])
        r = _analyze(tmp_path)
        # el real (bajo Safari) NO fue evictado por los decoys → exploit flagged
        assert any(f.finding_type == "SAFARI_EXPLOIT_RESEARCH"
                   and "bookmark" in f.evidence.lower() for f in r.findings)
