"""
tests/test_disk_forensics_ingest_guard.py
=========================================
B-147: MFTTimelineAnalyzer.analyze() must degrade honestly (not crash) when its
external `parsed_json` parameter carries malformed / adversarial JSON.

Context: analyze() already guards its other external input, `timestamp_utc`
("FIX P2 (Kimi post-patch): capturar ValueError ... no crashear"), but the
sibling `json.loads(parsed_json or "{}")` was unguarded (disk_forensics.py:131).
A malformed value raised json.JSONDecodeError (or RecursionError on deep
nesting) uncaught, crashing MFT analysis instead of degrading to zero entries.

Red-first: the two adversarial cases fail against the unguarded json.loads;
the valid case is a regression guard that must stay green before and after.
"""
from __future__ import annotations

import json

from vigia.sift.disk_forensics import MFTTimelineAnalyzer, MFTAnalysisResult


def test_malformed_parsed_json_degrades_not_crashes():
    res = MFTTimelineAnalyzer().analyze(mft_bytes=b"MFTDATA", parsed_json="{not valid json")
    assert isinstance(res, MFTAnalysisResult)
    assert res.total_entries == 0


def test_deeply_nested_parsed_json_degrades_not_crashes():
    # Depth-100000 nested array -> RecursionError from json.loads; must be caught,
    # not propagated. (Empirically bounded: no hang/OOM, but still an uncaught
    # crash before the guard.)
    payload = "[" * 100000 + "]" * 100000
    res = MFTTimelineAnalyzer().analyze(mft_bytes=b"MFTDATA", parsed_json=payload)
    assert isinstance(res, MFTAnalysisResult)
    assert res.total_entries == 0


def test_valid_json_but_not_an_object_degrades_not_crashes():
    # Valid JSON whose top level is a list (not a dict) must not raise
    # AttributeError on .get("entries") — degrade to zero entries.
    res = MFTTimelineAnalyzer().analyze(mft_bytes=b"MFTDATA", parsed_json="[1, 2, 3]")
    assert isinstance(res, MFTAnalysisResult)
    assert res.total_entries == 0


def test_valid_parsed_json_still_parses():
    # Regression: a well-formed payload must be unaffected by the guard.
    out = {"entries": [{"record_number": 5, "filename": "a.txt"}]}
    res = MFTTimelineAnalyzer().analyze(mft_bytes=b"MFTDATA", parsed_json=json.dumps(out))
    assert res.total_entries == 1
