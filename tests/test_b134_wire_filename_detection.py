"""
B-134 — Wire not detected on iOS: bundle-ID directory search cannot see
apps stored in UUID-named containers.

iOS stores third-party apps under
/private/var/mobile/Containers/Data/Application/<UUID>/ — no directory is
ever named "com.wire", so _detect_installed_apps' bundle-ID directory scan
returns nothing for Wire even when the extraction contains
store.wiredatabase (Wire's message database, which ios_forensics already
knows how to locate and parse). Signal has the same problem and already
has a filename-based special case (signal.sqlite); Wire gets the same
treatment.

Detected in VIGIA-MAGNET-2022-iOS-JESS (Mode 2 analysis, 2026-07-14).
"""

from fractions import Fraction
from pathlib import Path

import pytest

from vigia.sift.ios_forensics import iOSForensicsAnalyzer, iOSAnalysisResult


def _detect(tmp_path: Path):
    analyzer = iOSForensicsAnalyzer()
    result = iOSAnalysisResult()
    analyzer._detect_installed_apps(tmp_path, result)
    return analyzer._encrypted_apps


class TestB134WireDetection:
    def test_wire_detected_via_store_wiredatabase(self, tmp_path):
        (tmp_path / "store.wiredatabase").write_bytes(b"\x00")
        apps = _detect(tmp_path)
        assert any(a["bundle_id"] == "com.wire" for a in apps), (
            "B-134: store.wiredatabase present but Wire not reported as an "
            "installed encrypted app (UUID container gap)."
        )

    def test_wire_detected_in_subdirectory(self, tmp_path):
        """Logical extractions may keep the DB one level down, same layout
        the signal.sqlite special case covers."""
        sub = tmp_path / "wire_export"
        sub.mkdir()
        (sub / "store.wiredatabase").write_bytes(b"\x00")
        apps = _detect(tmp_path)
        assert any(a["bundle_id"] == "com.wire" for a in apps)

    def test_no_double_count_with_bundle_dir(self, tmp_path):
        """If the container directory IS named com.wire (jailbroken/manual
        export), filename detection must not add a second entry."""
        (tmp_path / "containers" / "com.wire").mkdir(parents=True)
        (tmp_path / "store.wiredatabase").write_bytes(b"\x00")
        apps = _detect(tmp_path)
        assert sum(1 for a in apps if a["bundle_id"] == "com.wire") == 1

    def test_signal_sqlite_regression(self, tmp_path):
        """The pre-existing Signal filename special case keeps working."""
        (tmp_path / "signal.sqlite").write_bytes(b"\x00")
        apps = _detect(tmp_path)
        assert any(a["bundle_id"] == "org.whispersystems.signal" for a in apps)

    def test_empty_dir_detects_nothing(self, tmp_path):
        assert _detect(tmp_path) == []
