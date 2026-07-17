"""
P1 (2026-07-17) — Evidence-integrity: CAIE must not silently omit a temporal
comparison it could not evaluate.

Confirmed by induction before the fix: CAIE's TEMPORAL_CAUSALITY_VIOLATION rule
omits a network/process pair when a required event timestamp (network_log_time /
process_creation_time) is *present but unparseable or out-of-range*
(vigia/tools/caie.py::_parse_ts_tcv returns None -> the loop `continue`s). The
omission was logged only to the HMAC audit; the returned CAIE result and the
sealed pipeline output carried NO marker. A single unparseable timestamp on an
artifact that otherwise carries a real temporal fracture flipped a sealed verdict
SUSPICION -> NOISE — a false "analyzed and clean" bill on a comparison that never
ran. Same family as the metadata P1, different trigger (a bad *value* inside a
well-formed dict, which the metadata gate does not catch).

Fix (narrowest honest form): CAIE records each skipped pair and surfaces it in
its (HMAC-signed) result as ``temporal_pairs_skipped``; the scorer honours that
marker in the same ABSTAIN gate — NOISE + a skipped decision-relevant comparison
becomes an explicit ABSTAIN. The gate fires only on NOISE, so it can never soften
a SUSPICION/MALICE finding.
"""

import copy
import logging
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia_scorer import _vigia_score  # noqa: E402
from vigia.tools.caie import (  # noqa: E402
    CrossArtifactIncongruenceEngine,
    Artifact as CaieArtifact,
)

logging.disable(logging.CRITICAL)

_NET_TIME = "2023-06-01T10:00:05Z"        # precedes the process it caused
_PROC_TIME = "2023-06-01T10:00:10Z"       # valid -> fracture fires
_UNPARSEABLE = "definitely-not-a-date"    # present but unusable
_OUT_OF_RANGE = "1970-01-01T00:00:00Z"    # epoch sentinel -> range guard -> None

_VALID = {"source_tool", "evidence_type", "raw_score", "description", "metadata",
          "provenance_chain", "base_trust", "timestamp"}


def _case(proc_time):
    return {
        "case_id": "TCV-SKIP",
        "artifacts": [
            {"artifact_id": "net-1", "evidence_type": "network_flow", "raw_score": 0.6,
             "source_tool": "zeek", "description": "beacon", "acquisition_tool": "zeek_v1",
             "metadata": {"network_log_time": _NET_TIME}},
            {"artifact_id": "mem-1", "evidence_type": "memory_process", "raw_score": 0.6,
             "source_tool": "volatility", "description": "proc", "acquisition_tool": "vol_v1",
             "metadata": {"process_creation_time": proc_time}},
        ],
    }


def _engine(proc_time):
    eng = CrossArtifactIncongruenceEngine()
    for a in _case(proc_time)["artifacts"]:
        eng.add_artifact(CaieArtifact(**{k: v for k, v in a.items() if k in _VALID}))
    return eng


def _score(proc_time):
    return _vigia_score(copy.deepcopy(_case(proc_time)))


# --------------------------------------------------------------------------- #
# CAIE level: the skip is recorded and surfaced in the (signed) result.
# --------------------------------------------------------------------------- #

def test_valid_timestamps_no_skip_one_fracture():
    eng = _engine(_PROC_TIME)
    frs = eng.detect_fractures()
    assert any(f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION" for f in frs)
    assert eng._temporal_pairs_skipped == []
    result = eng.evaluate()
    assert result["temporal_pairs_skipped"] == []
    assert result["temporal_pairs_skipped_count"] == 0


def test_unparseable_timestamp_is_recorded_as_skip():
    eng = _engine(_UNPARSEABLE)
    frs = eng.detect_fractures()
    assert not any(f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION" for f in frs)
    skipped = eng._temporal_pairs_skipped
    assert len(skipped) == 1
    assert skipped[0]["field"] == "process_creation_time"
    assert skipped[0]["reason"] == "unparseable"
    assert skipped[0]["rule"] == "TEMPORAL_CAUSALITY_VIOLATION"
    result = eng.evaluate()
    assert result["temporal_pairs_skipped_count"] == 1


def test_out_of_range_timestamp_is_not_recorded_r3_1_inert():
    """R3-1 invariant preserved: an out-of-range endpoint (1970 epoch sentinel)
    is DELIBERATELY treated as missing data, never a signal — it must NOT be
    recorded as a decision-relevant skip and must NOT move the verdict, so this
    fix does not re-open the false-MALICE-fabrication R3-1 closed."""
    eng = _engine(_OUT_OF_RANGE)
    eng.detect_fractures()
    assert eng._temporal_pairs_skipped == []
    # And end-to-end it stays NOISE (not ABSTAIN): R3-1's inert path is intact.
    assert _score(_OUT_OF_RANGE)["verdict"] == "NOISE"


# --------------------------------------------------------------------------- #
# Sealed pipeline: NOISE on a skipped comparison becomes ABSTAIN.
# --------------------------------------------------------------------------- #

def test_valid_pipeline_is_suspicion():
    assert _score(_PROC_TIME)["verdict"] == "SUSPICION"


def test_unparseable_pipeline_abstains_not_noise():
    r = _score(_UNPARSEABLE)
    assert r["verdict"] == "ABSTAIN"
    assert r["verdict"] != "NOISE"


def test_sealed_result_carries_temporal_skip_provenance():
    r = _score(_UNPARSEABLE)
    skipped = r.get("temporal_pairs_skipped")
    assert skipped, "temporal_pairs_skipped must be sealed into the pipeline result"
    assert skipped[0]["field"] == "process_creation_time"
    assert skipped[0]["value"] == _UNPARSEABLE
    assert skipped[0]["reason"] == "unparseable"


def test_valid_pipeline_has_no_false_skip_marker():
    r = _score(_PROC_TIME)
    assert r["verdict"] == "SUSPICION"
    assert not r.get("temporal_pairs_skipped")  # absent or empty


# --------------------------------------------------------------------------- #
# Decision invariant: the skip never yields a cleaner verdict than valid data.
# --------------------------------------------------------------------------- #

def test_skip_is_never_cleaner_than_valid():
    valid = _score(_PROC_TIME)["verdict"]
    skipped = _score(_UNPARSEABLE)["verdict"]
    assert valid == "SUSPICION"
    assert skipped != "NOISE"
    assert skipped == "ABSTAIN"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
