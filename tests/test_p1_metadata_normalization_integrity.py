"""
P1 (2026-07-17) — Evidence-integrity: metadata normalization must not silently
discard forensic assertions.

Confirmed by induction before the fix: an artifact arriving with a *present but
non-dict* ``metadata`` (e.g. ``[]``) was silently coerced to ``{}`` by
``_normalize_artifact_legacy``, erasing a ``process_creation_time`` that CAIE's
temporal-causality rule reads. The case passed validation with no rejection, no
counter and no marker, and a live verdict dropped from SUSPICION to NOISE — a
false "analyzed and clean" bill of health on real evidence.

The fix is fail-visible and provenance-preserving (never "make [] acceptable"):
  1. normalization records a ``normalization_failures`` marker instead of
     silently discarding (vigia/pipeline/vigia_integration_bridge.py);
  2. the scorer converts that marker into an explicit ABSTAIN rather than a
     false-clean NOISE, and seals the provenance in the result (vigia_scorer.py);
  3. validate_case_schema rejects a present non-dict metadata (defense in depth).

Invariant: an artifact that fails normalization can never REDUCE a case's
severity relative to the same, correctly-typed evidence — the ABSTAIN gate fires
only on NOISE, so it can never soften a SUSPICION/MALICE finding.
"""

import copy
import logging
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia_scorer import _vigia_score, _normalize_case  # noqa: E402
from vigia.pipeline.vigia_integration_bridge import (  # noqa: E402
    validate_case_schema,
    CaseSchemaError,
)

logging.disable(logging.CRITICAL)  # silence the acquisition-metadata alerts

# net event (10:00:05) precedes the process (10:00:10) that supposedly caused it
# -> effect-before-cause -> TEMPORAL_CAUSALITY_VIOLATION when both times survive.
_NET_TIME = "2023-06-01T10:00:05Z"
_PROC_TIME = "2023-06-01T10:00:10Z"


def _case(mem_metadata):
    return {
        "case_id": "P1-REGRESSION",
        "artifacts": [
            {
                "artifact_id": "net-1",
                "evidence_type": "network_flow",
                "raw_score": 0.6,
                "source_tool": "zeek",
                "description": "outbound C2 beacon in network flow",
                "acquisition_tool": "zeek_sensor_v1",
                "metadata": {"network_log_time": _NET_TIME},
            },
            {
                "artifact_id": "mem-1",
                "evidence_type": "memory_process",
                "raw_score": 0.6,
                "source_tool": "volatility",
                "description": "suspicious process in memory image",
                # deliberately NO acquisition_tool: that is the precondition that
                # makes the legacy normalizer touch this artifact's metadata.
                "metadata": mem_metadata,
            },
        ],
    }


def _score(mem_metadata):
    return _vigia_score(copy.deepcopy(_case(mem_metadata)))


# --------------------------------------------------------------------------- #
# 1. Baseline: the temporal fracture exists on correctly-typed evidence.
# --------------------------------------------------------------------------- #

def test_valid_metadata_yields_suspicion():
    r = _score({"process_creation_time": _PROC_TIME})
    assert r["verdict"] == "SUSPICION", r


def test_caie_sees_the_fracture_when_metadata_is_a_dict():
    """Mechanism level: process_creation_time survives normalization and CAIE
    detects exactly one TEMPORAL_CAUSALITY_VIOLATION."""
    from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact as CaieArtifact
    valid = {"source_tool", "evidence_type", "raw_score", "description",
             "metadata", "provenance_chain", "base_trust", "timestamp"}
    case = _normalize_case(_case({"process_creation_time": _PROC_TIME}))
    mem = next(a for a in case["artifacts"] if a["artifact_id"] == "mem-1")
    assert mem["metadata"].get("process_creation_time") == _PROC_TIME
    eng = CrossArtifactIncongruenceEngine()
    for a in case["artifacts"]:
        eng.add_artifact(CaieArtifact(**{k: v for k, v in a.items() if k in valid}))
    frs = eng.detect_fractures()
    assert any(f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION" for f in frs)


# --------------------------------------------------------------------------- #
# 2. Malformed metadata must not end as a clean NOISE.
# --------------------------------------------------------------------------- #

def test_malformed_metadata_abstains_not_noise():
    r = _score([])
    assert r["verdict"] == "ABSTAIN", r
    assert r["verdict"] != "NOISE"


def test_malformed_metadata_loses_the_assertion_at_caie():
    """Root cause is real: coercion erases process_creation_time, so CAIE can no
    longer detect the fracture. (The disposition gate is what keeps this honest.)"""
    case = _normalize_case(_case([]))
    mem = next(a for a in case["artifacts"] if a["artifact_id"] == "mem-1")
    assert isinstance(mem["metadata"], dict)
    assert "process_creation_time" not in mem["metadata"]


# --------------------------------------------------------------------------- #
# 3. The rejected/degraded artifact is visible in the sealed result.
# --------------------------------------------------------------------------- #

def test_sealed_result_carries_normalization_failure_provenance():
    r = _score([])
    failures = r.get("normalization_failures")
    assert failures, "normalization_failures must be sealed into the result"
    assert failures[0]["artifact_id"] == "mem-1"
    assert failures[0]["field"] == "metadata"
    assert failures[0]["reason"] == "metadata_type_invalid"
    assert failures[0]["original_type"] == "list"


# --------------------------------------------------------------------------- #
# 4. Decision invariant: malformed evidence never yields a cleaner verdict.
# --------------------------------------------------------------------------- #

def test_malformed_is_never_cleaner_than_typed():
    typed = _score({"process_creation_time": _PROC_TIME})["verdict"]
    malformed = _score([])["verdict"]
    assert typed == "SUSPICION"
    # The malformed run must not be certified clean (NOISE) while the same,
    # correctly-typed evidence raises suspicion.
    assert malformed != "NOISE"
    assert malformed == "ABSTAIN"


# --------------------------------------------------------------------------- #
# Defense in depth + no false alarms.
# --------------------------------------------------------------------------- #

def test_validate_case_schema_rejects_nondict_metadata():
    raw = {
        "case_id": "raw",
        "artifacts": [
            {"artifact_id": "x", "evidence_type": "memory_process",
             "raw_score": 0.5, "metadata": []},
        ],
    }
    with pytest.raises(CaseSchemaError):
        validate_case_schema(raw)


def test_absent_metadata_is_not_flagged_as_loss():
    """A missing/None metadata is legitimately empty (no evidence to lose) and
    must not raise a false normalization_failures marker."""
    case = _normalize_case({
        "case_id": "no-md",
        "artifacts": [
            {"artifact_id": "y", "evidence_type": "memory_process",
             "raw_score": 0.5},  # no metadata key at all
        ],
    })
    art = case["artifacts"][0]
    assert "normalization_failures" not in art
    assert isinstance(art["metadata"], dict)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
