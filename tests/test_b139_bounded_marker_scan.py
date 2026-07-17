"""
B-139 — bounded marker scan for the SIFT engines (tests written RED first).

Firstness: the marker-validation step of the iOS/Android/macOS engines
materialized every name in the evidence tree
(`{f.name for f in evidence_path.rglob("*")}`) before intersecting with the
marker set — O(tree) memory and an unbounded walk on a hostile or giant
tree. This is the exact class S4 (AUDITORIA_COBERTURA_MOBILE_SIFT §C)
already closed for the pattern-specific lookups via `_safe_rglob`, left
open at the three `rglob("*")` call sites (WHAT_IS_NEXT §1.3 residual).

Contract under test:
  - `scan_marker_names()` returns the same subset of markers the old
    pattern computed, for any tree within the bound (equivalence pins);
  - symlinks never count; directories count only with `include_dirs=True`
    (macOS: `.fseventsd` is a directory marker — the semantic that must
    not regress);
  - beyond `max_entries` the walk STOPS and a visible WARNING is logged
    (honest degradation, ENGINEERING_DISCIPLINE §5.3) instead of walking
    to completion;
  - the three engines still detect / miss markers exactly as before on
    synthetic trees.
"""

import logging

import pytest

from vigia.sift._fs_utils import MARKER_SCAN_MAX_ENTRIES, scan_marker_names

logger = logging.getLogger("test_b139")


# ── Helper unit contract ────────────────────────────────────────────────────


class TestScanMarkerNames:
    def test_finds_file_markers(self, tmp_path):
        (tmp_path / "nested" / "deep").mkdir(parents=True)
        (tmp_path / "nested" / "deep" / "sms.db").write_bytes(b"x")
        (tmp_path / "unrelated.txt").write_bytes(b"x")
        found = scan_marker_names(
            tmp_path, {"sms.db", "keychain-2.db"}, engine="TEST", logger=logger
        )
        assert found == {"sms.db"}

    def test_empty_tree_and_missing_markers(self, tmp_path):
        assert (
            scan_marker_names(tmp_path, {"sms.db"}, engine="TEST", logger=logger)
            == set()
        )

    def test_directory_not_counted_by_default(self, tmp_path):
        (tmp_path / "sms.db").mkdir()  # a DIRECTORY named like the marker
        found = scan_marker_names(
            tmp_path, {"sms.db"}, engine="TEST", logger=logger
        )
        assert found == set()

    def test_directory_counted_with_include_dirs(self, tmp_path):
        (tmp_path / ".fseventsd").mkdir()
        (tmp_path / "system.log").write_bytes(b"x")
        found = scan_marker_names(
            tmp_path,
            {".fseventsd", "system.log"},
            engine="TEST",
            logger=logger,
            include_dirs=True,
        )
        assert found == {".fseventsd", "system.log"}

    def test_symlink_never_counts(self, tmp_path):
        real = tmp_path / "real.bin"
        real.write_bytes(b"x")
        try:
            (tmp_path / "sms.db").symlink_to(real)
        except OSError:
            pytest.skip("symlinks not supported on this filesystem")
        found = scan_marker_names(
            tmp_path, {"sms.db"}, engine="TEST", logger=logger
        )
        assert found == set()

    def test_equivalence_with_old_pattern(self, tmp_path):
        # The exact expression this helper replaces (iOS/Android variant).
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "sms.db").write_bytes(b"x")
        (tmp_path / "keychain-2.db").write_bytes(b"x")
        (tmp_path / "noise.dat").write_bytes(b"x")
        markers = {"sms.db", "keychain-2.db", "absent.db"}
        old = {
            f.name
            for f in tmp_path.rglob("*")
            if f.is_file() and not f.is_symlink()
        } & markers
        new = scan_marker_names(tmp_path, markers, engine="TEST", logger=logger)
        assert new == old == {"sms.db", "keychain-2.db"}

    def test_truncation_stops_and_warns(self, tmp_path, caplog):
        # rglob traversal order is filesystem-dependent, so the stop is
        # proven with a bound of 0: the very first entry exceeds it, the
        # marker (present in the tree) must NOT be found, and the WARNING
        # must be on the record.
        (tmp_path / "marker.db").write_bytes(b"x")
        with caplog.at_level(logging.WARNING):
            found = scan_marker_names(
                tmp_path,
                {"marker.db"},
                engine="TEST",
                logger=logger,
                max_entries=0,
            )
        assert found == set()
        assert any("truncated" in r.message for r in caplog.records)
        # Same tree without the bound: the marker IS found — the miss above
        # was the cap, not the scan.
        assert scan_marker_names(
            tmp_path, {"marker.db"}, engine="TEST", logger=logger
        ) == {"marker.db"}

    def test_no_warning_within_bound(self, tmp_path, caplog):
        (tmp_path / "sms.db").write_bytes(b"x")
        with caplog.at_level(logging.WARNING):
            scan_marker_names(
                tmp_path, {"sms.db"}, engine="TEST", logger=logger, max_entries=100
            )
        assert not any("truncated" in r.message for r in caplog.records)

    def test_default_bound_is_generous(self):
        assert MARKER_SCAN_MAX_ENTRIES >= 100_000


# ── Engine-level pins: behavior identical to the pre-B-139 scan ────────────

_NO_MARKER_NOTE = {
    "ios": "No iOS-specific artifacts found",
    "android": "No Android-specific artifacts found",
    "macos": "No macOS-specific artifacts found",
}


class TestEnginesStillValidateMarkers:
    def test_ios_marker_detected(self, tmp_path):
        from vigia.sift.ios_forensics import iOSForensicsAnalyzer

        (tmp_path / "backup").mkdir()
        (tmp_path / "backup" / "sms.db").write_bytes(b"")
        result = iOSForensicsAnalyzer().analyze(tmp_path)
        assert not any(
            _NO_MARKER_NOTE["ios"] in n for n in result.analysis_notes
        )

    def test_ios_no_marker_note(self, tmp_path):
        from vigia.sift.ios_forensics import iOSForensicsAnalyzer

        (tmp_path / "random.txt").write_bytes(b"x")
        result = iOSForensicsAnalyzer().analyze(tmp_path)
        assert any(_NO_MARKER_NOTE["ios"] in n for n in result.analysis_notes)

    def test_android_marker_detected(self, tmp_path):
        from vigia.sift.android_forensics import AndroidForensicsAnalyzer

        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "mmssms.db").write_bytes(b"")
        result = AndroidForensicsAnalyzer().analyze(tmp_path)
        assert not any(
            _NO_MARKER_NOTE["android"] in n for n in result.analysis_notes
        )

    def test_android_no_marker_note(self, tmp_path):
        from vigia.sift.android_forensics import AndroidForensicsAnalyzer

        (tmp_path / "random.txt").write_bytes(b"x")
        result = AndroidForensicsAnalyzer().analyze(tmp_path)
        assert any(
            _NO_MARKER_NOTE["android"] in n for n in result.analysis_notes
        )

    def test_macos_dir_marker_detected(self, tmp_path):
        # .fseventsd is a DIRECTORY marker — the include_dirs semantic.
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

        (tmp_path / ".fseventsd").mkdir()
        result = MacOSForensicsAnalyzer().analyze(tmp_path)
        assert not any(
            _NO_MARKER_NOTE["macos"] in n for n in result.analysis_notes
        )

    def test_macos_no_marker_note(self, tmp_path):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

        (tmp_path / "random.txt").write_bytes(b"x")
        result = MacOSForensicsAnalyzer().analyze(tmp_path)
        assert any(
            _NO_MARKER_NOTE["macos"] in n for n in result.analysis_notes
        )
