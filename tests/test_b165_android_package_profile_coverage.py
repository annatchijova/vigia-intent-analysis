"""B-165 — Android package-profile evidence must not be called absent.

An application-only Android extraction can preserve
``com.android.chrome/app_chrome/Default/History`` while omitting the broader
platform databases used as the original marker set.  The analyzer still parsed
that History database, but emitted the contradictory note that no Android
artifacts existed.  Recognizing this layout is a coverage correction only: it
must not turn ordinary browsing into an intentionality finding.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from vigia.sift.android_forensics import AndroidForensicsAnalyzer


def _make_chromium_history(path: Path) -> None:
    path.parent.mkdir(parents=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            "CREATE TABLE urls (url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER)"
        )
        conn.commit()
    finally:
        conn.close()


def test_b165_android_chrome_package_profile_is_coverage_not_a_finding(tmp_path: Path) -> None:
    history = tmp_path / "com.android.chrome" / "app_chrome" / "Default" / "History"
    _make_chromium_history(history)

    result = AndroidForensicsAnalyzer().analyze(tmp_path)

    assert not any(
        "No Android-specific artifacts found" in note
        for note in result.analysis_notes
    )
    assert any("Android Chrome application profile detected" in note for note in result.analysis_notes)
    # B-165 is provenance/coverage only: no narrative URL is promoted to a
    # scored finding by recognizing a source layout.
    assert result.findings == []
    assert result.to_signal().z_score == 0.0


def test_b165_generic_chromium_history_is_not_misidentified_as_android(tmp_path: Path) -> None:
    _make_chromium_history(tmp_path / "desktop-profile" / "Default" / "History")

    result = AndroidForensicsAnalyzer().analyze(tmp_path)

    assert any(
        "No Android-specific artifacts found" in note
        for note in result.analysis_notes
    )
