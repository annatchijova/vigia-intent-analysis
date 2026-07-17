"""
B-137 — TCC.db in _MACOS_MARKER_FILES silently skips the iOS engine.

TCC.db (Transparency, Consent & Control privacy database) exists on BOTH
macOS and iOS (iOS path: /private/var/mobile/Library/TCC/TCC.db). It was
listed only in _MACOS_MARKER_FILES, so the B-048 macOS-precedence guard in
vigia_agent._build_orchestrator_kwargs treated any full iOS extraction
containing it as macOS evidence:

    all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES)  ->  non-empty

which set macos_evidence_path; the shim then skipped the iOS engine and the
bundle sealed with zero ios_forensics signals (SMS, contacts, calls lost).

This is the same bug class B-133 closed for knowledgeC.db, and it was the
explicit "residual risk" documented under B-048. Kimi's adversarial audit
(K-1, 2026-07-17) surfaced it as still-open. Fix: add TCC.db to
_IOS_MARKER_FILES so the macOS-exclusive set no longer contains a file that
ships on every full iOS extraction.

Symmetric edge (a macOS directory whose ONLY exclusive marker is TCC.db):
as hypothetical as the knowledgeC.db case, and benign — the iOS engine over
macOS-only TCC.db produces ~zero findings and every real macOS extraction
still carries genuinely exclusive markers (.fseventsd, system.log, ...).
"""

from pathlib import Path

import pytest

import vigia_agent
from vigia.sift.ios_forensics import _IOS_MARKER_FILES
from vigia.sift.macos_forensics import _MACOS_MARKER_FILES


def _touch_all(base: Path, names) -> None:
    for name in names:
        (base / name).write_bytes(b"\x00")


class TestB203Markers:
    def test_tcc_is_an_ios_marker(self):
        assert "TCC.db" in _IOS_MARKER_FILES, (
            "B-137: TCC.db ships on every full iOS extraction "
            "(/private/var/mobile/Library/TCC/TCC.db); it must be a valid "
            "iOS marker."
        )

    def test_tcc_not_in_macos_exclusive_set(self):
        assert "TCC.db" not in (_MACOS_MARKER_FILES - _IOS_MARKER_FILES), (
            "B-137: TCC.db must not count as a macOS-exclusive marker or the "
            "B-048 guard hijacks iOS extractions."
        )

    def test_macos_still_has_exclusive_markers(self):
        """B-048 regression guard: dropping TCC.db from the exclusive set must
        not empty it — macOS keeps genuinely exclusive markers."""
        exclusive = _MACOS_MARKER_FILES - _IOS_MARKER_FILES
        assert ".fseventsd" in exclusive
        assert "system.log" in exclusive
        assert len(exclusive) >= 5


class TestB203Routing:
    def test_full_ios_extraction_with_tcc_routes_to_ios_engine(self, tmp_path):
        """A full iOS extraction (sms.db + TCC.db) must set ios_evidence_path
        and must NOT set macos_evidence_path — the exact hijack B-137 fixes."""
        _touch_all(tmp_path, ["sms.db", "TCC.db", "Info.plist"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("ios_evidence_path") == str(tmp_path)
        assert "macos_evidence_path" not in kwargs, (
            "B-137: TCC.db alone must not activate the macOS engine for an "
            "iOS extraction — the B-048 precedence guard would then silently "
            "skip the iOS engine and lose SMS/contacts/calls."
        )

    def test_real_macos_extraction_still_routes_to_macos(self, tmp_path):
        """macOS evidence with genuinely exclusive markers keeps working even
        though TCC.db is now shared."""
        _touch_all(tmp_path, ["History.db", "TCC.db", "system.log", ".fseventsd"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("macos_evidence_path") == str(tmp_path)

    def test_both_cross_platform_dbs_together_route_to_ios(self, tmp_path):
        """knowledgeC.db (B-133) and TCC.db (B-137) together, with an iOS-only
        marker, must route purely to iOS with no macOS hijack."""
        _touch_all(tmp_path, ["sms.db", "knowledgeC.db", "TCC.db"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("ios_evidence_path") == str(tmp_path)
        assert "macos_evidence_path" not in kwargs
