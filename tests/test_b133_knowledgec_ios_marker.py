"""
B-133 — knowledgeC.db in _MACOS_MARKER_FILES silently skips the iOS engine.

knowledgeC.db (CoreDuet application-activity database) exists on BOTH
macOS and iOS (iOS path: /private/var/mobile/Library/CoreDuet/Knowledge/).
It was listed only in _MACOS_MARKER_FILES, so the B-048 macOS-precedence
guard in vigia_agent._build_orchestrator_kwargs treated any full iOS
extraction containing it as macOS evidence:

    all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES)  ->  non-empty

which set macos_evidence_path; the shim then skipped the iOS engine with
"macOS engine takes precedence (B-048)" and the bundle sealed with zero
ios_forensics signals (observed: VIGIA-MAGNET-2022-iOS-JESS, 2026-07-14).

Fix: add knowledgeC.db to _IOS_MARKER_FILES so the macOS-exclusive set
no longer contains a file that ships on every full iOS extraction.
Real macOS evidence keeps triggering the macOS engine through genuinely
exclusive markers (.fseventsd, .Spotlight-V100, system.log,
QuarantineEventsV2, ...), and the shim same-directory precedence guard
still prevents double processing when both engines match.

Note: TCC.db is no longer a valid witness of macOS-exclusivity — B-137
moved it to _IOS_MARKER_FILES for the same reason B-133 moved
knowledgeC.db, so this test uses system.log instead.
"""

from pathlib import Path

import pytest

import vigia_agent
from vigia.sift.ios_forensics import _IOS_MARKER_FILES
from vigia.sift.macos_forensics import _MACOS_MARKER_FILES


def _touch_all(base: Path, names) -> None:
    for name in names:
        (base / name).write_bytes(b"\x00")


class TestB133Markers:
    def test_knowledgec_is_an_ios_marker(self):
        assert "knowledgeC.db" in _IOS_MARKER_FILES, (
            "B-133: knowledgeC.db ships on every full iOS extraction "
            "(CoreDuet); it must be a valid iOS marker."
        )

    def test_knowledgec_not_in_macos_exclusive_set(self):
        assert "knowledgeC.db" not in (_MACOS_MARKER_FILES - _IOS_MARKER_FILES), (
            "B-133: knowledgeC.db must not count as a macOS-exclusive marker "
            "or the B-048 guard hijacks iOS extractions."
        )

    def test_macos_still_has_exclusive_markers(self):
        """Regression guard for B-048 itself: the macOS detector must keep a
        non-empty exclusive marker set after the B-133 change."""
        exclusive = _MACOS_MARKER_FILES - _IOS_MARKER_FILES
        # system.log is macOS-only (TCC.db was moved to iOS markers by B-137).
        assert "system.log" in exclusive
        assert ".fseventsd" in exclusive
        assert len(exclusive) >= 5


class TestB133Routing:
    def test_full_ios_extraction_routes_to_ios_engine(self, tmp_path):
        """A GrayKey-style full iOS extraction (sms.db + knowledgeC.db)
        must set ios_evidence_path and must NOT set macos_evidence_path."""
        _touch_all(tmp_path, ["sms.db", "knowledgeC.db", "Info.plist"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("ios_evidence_path") == str(tmp_path)
        assert "macos_evidence_path" not in kwargs, (
            "B-133: knowledgeC.db alone must not activate the macOS engine "
            "for an iOS extraction — the B-048 precedence guard would then "
            "silently skip the iOS engine."
        )

    def test_real_macos_extraction_still_routes_to_macos(self, tmp_path):
        """macOS evidence with genuinely exclusive markers keeps working."""
        _touch_all(tmp_path, ["History.db", "knowledgeC.db", "TCC.db", "system.log"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("macos_evidence_path") == str(tmp_path)

    def test_macos_dir_matching_both_keeps_shim_precedence(self, tmp_path):
        """When a directory matches both engines (History.db is shared, and
        knowledgeC.db is now shared too), both paths point to the same
        directory, which is exactly the case the shim B-048 precedence
        guard resolves (iOS skipped, macOS runs). Routing must preserve
        that equality instead of dropping the macOS path."""
        _touch_all(tmp_path, ["History.db", "knowledgeC.db", "TCC.db", ".fseventsd"])
        kwargs = vigia_agent._build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("macos_evidence_path") == str(tmp_path)
        assert kwargs.get("ios_evidence_path") == str(tmp_path)
