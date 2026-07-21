"""B-167 — bounded Android SMS parsing must remain visible to the verdict path.

The Android parser intentionally caps content inspection to protect the
runtime.  A cap is not a clean analysis of every message, though: if the
cap is reached, the resulting bundle must carry an ``unanalyzed`` marker so
the agent cannot present the unexplored suffix as clean evidence.
"""
from __future__ import annotations

import sqlite3

from sift_orchestrator import SIFTOrchestrator
from vigia.sift.android_forensics import AndroidForensicsAnalyzer
from vigia_agent import _signal_stats


def _write_sms_db(root, rows: int = 501) -> None:
    db_path = root / "mmssms.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE sms (_id INTEGER PRIMARY KEY, address TEXT, body TEXT, "
            "date INTEGER, type INTEGER, thread_id INTEGER)"
        )
        conn.executemany(
            "INSERT INTO sms VALUES (?, ?, ?, ?, ?, ?)",
            [
                (index, "+15550000000", f"ordinary message {index}", index, 1, 1)
                for index in range(1, rows + 1)
            ],
        )


class TestB167AndroidSmsTruncation:
    def test_exact_content_bound_is_complete(self, tmp_path):
        _write_sms_db(tmp_path, rows=500)

        result = AndroidForensicsAnalyzer().analyze(tmp_path)
        signal = result.to_signal()

        assert result.sms_analyzable_rows == 500
        assert result.sms_analyzed_rows == 500
        assert result.sms_content_truncated is False
        assert signal.metadata["sms_content_truncated"] is False

    def test_engine_declares_bounded_sms_content_analysis(self, tmp_path):
        _write_sms_db(tmp_path)

        result = AndroidForensicsAnalyzer().analyze(tmp_path)
        signal = result.to_signal()

        assert result.total_sms == 501
        assert result.sms_analyzable_rows == 501
        assert result.sms_content_truncated is True
        assert any("SMS content analysis truncated" in note for note in result.analysis_notes)
        assert signal.metadata["sms_content_truncated"] is True
        assert signal.metadata["sms_analyzable_rows"] == 501
        assert signal.metadata["sms_analyzed_rows"] == 500

    def test_shim_marks_bounded_sms_suffix_unanalyzed(self, tmp_path):
        _write_sms_db(tmp_path)

        result = SIFTOrchestrator("B167-SMS-TRUNCATION").analyze(
            android_evidence_path=str(tmp_path)
        )
        markers = [
            signal
            for signal in result.get("signals", [])
            if (signal.get("metadata") or {}).get("unanalyzed")
        ]

        assert any(
            marker.get("tool") == "ANDROID_SMS_UNANALYZED"
            and (marker.get("metadata") or {}).get("artifact_type") == "android_sms"
            for marker in markers
        ), "The bounded SMS suffix disappeared without an unanalyzed marker."
        _, n_unanalyzed = _signal_stats(result)
        assert n_unanalyzed >= 1
