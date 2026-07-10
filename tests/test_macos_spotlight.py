"""
Tests del análisis Spotlight en macos_forensics._analyze_spotlight
(MACOS_MODULES_DESIGN §5, Fase 1).

Sin artefacto real en el corpus → fixtures sintéticos. Cubre:
- Shortcuts: consultas tecleadas suspicious/anti-forenses → findings.
- store.db (.Spotlight-V100): presencia registrada, NO parseada (Fase 1) —
  degradación honesta.
"""

from __future__ import annotations

import plistlib

import pytest

from vigia.sift.macos_forensics import MacOSForensicsAnalyzer


def _root(tmp_path):
    (tmp_path / "SystemVersion.plist").write_bytes(
        plistlib.dumps({"ProductVersion": "13.0"}))
    return tmp_path


def _analyze(root):
    return MacOSForensicsAnalyzer().analyze(root)


def _write_shortcuts(root, queries: dict, name="com.apple.spotlight.Shortcuts"):
    d = root / "Users" / "x" / "Library" / "Preferences"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_bytes(plistlib.dumps(queries))


class TestSpotlightShortcuts:
    def test_suspicious_query_flagged(self, tmp_path):
        root = _root(tmp_path)
        _write_shortcuts(root, {
            "weather": {"DISPLAY_NAME": "Weather"},
            "how to hack wifi": {"DISPLAY_NAME": "hacking"},
        })
        r = _analyze(root)
        susp = [f for f in r.findings
                if f.finding_type == "SPOTLIGHT_SUSPICIOUS_QUERY"]
        assert susp, [f.finding_type for f in r.findings]
        assert susp[0].corr_group == "spotlight_intent"

    def test_antiforensic_query_feeds_antiforensic_group(self, tmp_path):
        root = _root(tmp_path)
        _write_shortcuts(root, {"bleachbit": {"DISPLAY_NAME": "cleaner"}})
        r = _analyze(root)
        af = [f for f in r.findings
              if f.finding_type == "ANTIFORENSIC_SPOTLIGHT_QUERY"]
        assert af and af[0].corr_group == "antiforensic"
        # prefijo ANTIFORENSIC → alimenta has_antiforensic_finding de to_signal
        assert af[0].finding_type.startswith("ANTIFORENSIC")

    def test_benign_queries_no_findings(self, tmp_path):
        root = _root(tmp_path)
        _write_shortcuts(root, {"safari": {}, "mail": {}, "calculator": {}})
        r = _analyze(root)
        assert not any("SPOTLIGHT" in f.finding_type for f in r.findings)
        assert any("3 consulta(s)" in n for n in r.analysis_notes)

    def test_archiver_keys_skipped(self, tmp_path):
        # Claves internas ($archiver/$objects) no se tratan como consultas.
        root = _root(tmp_path)
        _write_shortcuts(root, {"$archiver": "x", "$version": 1, "real query": {}})
        r = _analyze(root)
        note = [n for n in r.analysis_notes if "consulta(s)" in n]
        assert note and "1 consulta(s)" in note[0]

    def test_v3_shortcuts_name_also_parsed(self, tmp_path):
        root = _root(tmp_path)
        _write_shortcuts(root, {"metasploit exploit": {}},
                         name="com.apple.spotlight.Shortcuts.v3")
        r = _analyze(root)
        assert any(f.finding_type in ("SPOTLIGHT_SUSPICIOUS_QUERY",
                                      "SPOTLIGHT_EXPLOIT")
                   or "SPOTLIGHT" in f.finding_type for f in r.findings)


class TestSpotlightStoreDB:
    def test_store_db_presence_noted_not_parsed(self, tmp_path):
        root = _root(tmp_path)
        sv = root / ".Spotlight-V100" / "Store-V2" / "UUID"
        sv.mkdir(parents=True)
        (sv / "store.db").write_bytes(b"\x00binary spotlight index\x00")
        r = _analyze(root)
        assert any("store.db" in n and "NO analizado" in n
                   for n in r.analysis_notes), r.analysis_notes
        # Fase 1: NO se emiten findings del store binario.
        assert not any("STORE" in f.finding_type for f in r.findings)

    def test_no_spotlight_is_inert(self, tmp_path):
        root = _root(tmp_path)
        r = _analyze(root)
        assert not any("Spotlight analysis error" in n for n in r.analysis_notes)
        assert not any("SPOTLIGHT" in f.finding_type for f in r.findings)
