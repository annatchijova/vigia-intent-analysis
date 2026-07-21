"""B-172 — a declared temporal hard-gate claim must match source artifacts.

L-062 established that the old hard gate issued categorical MALICE from an
examiner-authored ``EFFECT_BEFORE_CAUSE`` entry alone.  These tests deliberately
keep the existing no-tolerance policy out of scope: a real negative ordering
continues to trigger the gate, while a declared claim contradicted by artifact
timestamps must fail closed as ABSTAIN.
"""
from __future__ import annotations

import copy

import pytest

_scorer = pytest.importorskip(
    "vigia_scorer",
    reason="vigia_scorer not importable (run with PYTHONPATH=$(pwd))",
)
_vigia_score = _scorer._vigia_score


def _case(*, effect_timestamp: str) -> dict:
    return {
        "case_id": "B172-hard-temporal-validation",
        "artifacts": [
            {
                "artifact_id": "cause", "evidence_type": "memory_process",
                "source_tool": "list_processes",
                "timestamp": "2026-04-10T10:00:05Z",
                "raw_score": 0.4, "prior_trust": 0.9,
                "provenance_chain": ["sha256:cause"], "description": "process",
                "metadata": {},
            },
            {
                "artifact_id": "effect", "evidence_type": "file_timestamp",
                "source_tool": "read_evidence", "timestamp": effect_timestamp,
                "raw_score": 0.3, "prior_trust": 0.8,
                "provenance_chain": ["sha256:effect"], "description": "file",
                "metadata": {},
            },
        ],
        "temporal_violations": [{
            "type": "EFFECT_BEFORE_CAUSE", "severity": 1.0,
            "cause": {"artifact_id": "cause", "timestamp": "2026-04-10T10:00:05Z"},
            "effect": {"artifact_id": "effect", "timestamp": "2026-04-10T10:00:00Z"},
            "delta_seconds": -5,
        }],
        "caie_fractures": [], "expected_verdict": "UNKNOWN", "peirce_chain": {},
    }


def test_asserted_inversion_contradicted_by_artifacts_abstains():
    """The violation says -5 seconds, but the actual effect is two seconds
    after the cause.  A JSON assertion cannot create categorical MALICE."""
    result = _vigia_score(_case(effect_timestamp="2026-04-10T10:00:07Z"))

    assert result["verdict"] == "ABSTAIN"
    assert result["hard_temporal_gate"] is False
    assert len(result["unverified_hard_temporal_violations"]) == 1
    assert result["hard_temporal_authority"] == "unverified_json_no_verdict_authority"


def test_verified_artifact_inversion_keeps_hard_gate():
    """This is not the H-01 tolerance decision: a real five-second inversion
    retains the current categorical gate once the artifact pair verifies it."""
    result = _vigia_score(_case(effect_timestamp="2026-04-10T10:00:00Z"))

    assert result["verdict"] == "MALICE"
    assert result["hard_temporal_gate"] is True
    assert result["hard_temporal_authority"] == "validated_artifact_pair"


def test_missing_artifact_pair_cannot_trigger_hard_gate():
    case = copy.deepcopy(_case(effect_timestamp="2026-04-10T10:00:00Z"))
    case["temporal_violations"][0]["effect"]["artifact_id"] = "absent"

    result = _vigia_score(case)

    assert result["verdict"] == "ABSTAIN"
    assert result["hard_temporal_gate"] is False
    assert result["unverified_hard_temporal_violations"][0]["reason"] == "artifact_not_found"
