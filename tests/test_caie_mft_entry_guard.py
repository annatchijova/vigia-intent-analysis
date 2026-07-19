"""
tests/test_caie_mft_entry_guard.py
==================================
S-3 (docs/PATTERN_HUNT_20260718.md, 2026-07-18): the MFT_ENTRY_ANOMALY rule
coerced mft_entry_number with a bare `int(a.metadata.get("mft_entry_number",
0))`, which had two silent failure modes:

  (a) a MISSING number defaulted to entry 0 → two such artifacts collapsed to
      0, `curr > prev` never held, the sev-0.90 fracture could not fire, with
      no disclosure;
  (b) a PRESENT-but-unparseable value ("abc") raised ValueError with no local
      guard → toppled the whole detect_fractures() into the scorer's
      json_fallback (one bad field degrading the entire mode).

Fix mirrors the TCV doctrine: a missing/unparseable entry number is
decision-relevant MISSING DATA (not entry "0"); the artifact is excluded from
the monotonicity check and the skip is recorded on temporal_pairs_skipped
(already surfaced in the sealed result and read by the scorer's ABSTAIN gate).
"""
from __future__ import annotations

import pytest

caie = pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie not importable (run with PYTHONPATH=$(pwd))",
)
CrossArtifactIncongruenceEngine = caie.CrossArtifactIncongruenceEngine
Artifact = caie.Artifact


def _mft(entry, ts, i, source="mft"):
    return Artifact(
        source_tool=source, evidence_type="mft_entry", raw_score=0.5,
        description="mft", metadata={"mft_entry_number": entry} if entry is not None else {},
        provenance_chain=[f"sha256:m{i}"], base_trust=0.9, timestamp=ts,
    )


def _mft_fractures(engine):
    return [f for f in engine.detect_fractures()
            if f.fracture_type == "MFT_ENTRY_ANOMALY"]


def _mft_skips(engine):
    return [s for s in engine._temporal_pairs_skipped
            if s.get("rule") == "MFT_ENTRY_ANOMALY"]


class TestUnparseableDoesNotCrash:
    def test_unparseable_entry_number_no_crash_and_disclosed(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.add_artifact(_mft("abc", "2026-04-10T10:00:05Z", 0))
        eng.add_artifact(_mft("5", "2026-04-10T10:00:03Z", 1))
        # Must not raise (previously ValueError → whole-engine json_fallback).
        eng.detect_fractures()
        skips = _mft_skips(eng)
        assert len(skips) == 1
        assert skips[0]["reason"] == "unparseable"
        assert skips[0]["field"] == "mft_entry_number"

    def test_unparseable_leaves_only_one_valid_so_no_fracture(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.add_artifact(_mft("abc", "2020-01-01T00:00:00Z", 0))
        eng.add_artifact(_mft("50", "2026-01-01T00:00:00Z", 1))
        assert _mft_fractures(eng) == []  # one valid entry cannot form a pair


class TestMissingDoesNotFabricateEntryZero:
    def test_two_missing_entries_excluded_and_disclosed(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.add_artifact(_mft(None, "2026-01-01T00:00:00Z", 0))
        eng.add_artifact(_mft(None, "2026-01-02T00:00:00Z", 1))
        assert _mft_fractures(eng) == []  # not collapsed to entry 0
        assert len(_mft_skips(eng)) == 2
        assert all(s["reason"] == "missing" for s in _mft_skips(eng))


class TestRealAnomalyStillFires:
    def test_monotonicity_violation_still_detected(self):
        eng = CrossArtifactIncongruenceEngine()
        # entry #100 allocated after #50, but carries an OLDER timestamp
        eng.add_artifact(_mft("100", "2020-01-01T00:00:00Z", 0))
        eng.add_artifact(_mft("50", "2026-01-01T00:00:00Z", 1))
        frs = _mft_fractures(eng)
        assert len(frs) == 1
        assert frs[0].severity == 0.90
        assert _mft_skips(eng) == []  # clean input produces no false skip

    def test_integer_entry_numbers_also_work(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.add_artifact(_mft(100, "2020-01-01T00:00:00Z", 0))
        eng.add_artifact(_mft(50, "2026-01-01T00:00:00Z", 1))
        assert len(_mft_fractures(eng)) == 1
