"""
tests/test_audit_gates.py
=========================
Red-team audit — decision gates.

H-04  Causal Closure Score: with no information, it must not enable MALICE_HIGH.
H-05  Corroboration gate counts quantity/label, not independent sources.
H-10  Artifacts silently discarded must appear in the verdict.
"""
from __future__ import annotations

from fractions import Fraction

import pytest


# ===========================================================================
# H-04 — Causal Closure Score: without information, MALICE_HIGH must not be enabled
# ===========================================================================

ccs_mod = pytest.importorskip(
    "vigia.core.causal_closure",
    reason="vigia.core.causal_closure not importable (run with PYTHONPATH=$(pwd))",
)
compute_causal_closure = ccs_mod.compute_causal_closure
GATE_THRESHOLD = ccs_mod.GATE_THRESHOLD


def test_ccs_all_none_sits_exactly_on_threshold():
    """
    Documents current behavior: with all 4 dimensions at None, each is
    substituted by 1/2 and the weights sum to 1, so CCS == 1/2 == threshold.
    This test is NOT xfail: it pins the boundary so the fix is visible.
    """
    result = compute_causal_closure()
    assert result.causal_closure_score == Fraction(1, 2), (
        f"CCS with all None should be exactly 1/2, got "
        f"{result.causal_closure_score}."
    )
    assert GATE_THRESHOLD == Fraction(1, 2), (
        f"This test assumes GATE_THRESHOLD == 1/2; adjust if it changed "
        f"(current: {GATE_THRESHOLD})."
    )


@pytest.mark.xfail(
    reason="H-04: with zero information (all dimensions None) the gate passes "
           "because 1/2 >= 1/2 and enables MALICE_HIGH. The defensible behavior is ABSTAIN. "
           "Transitions to XPASS when total absence forces ABSTAIN.",
    strict=False,
)
def test_ccs_no_information_forces_abstain():
    result = compute_causal_closure()
    assert result.verdict_cap == "ABSTAIN", (
        "With zero causal coherence information, the maximum verdict should be "
        f"ABSTAIN. Got verdict_cap={result.verdict_cap!r}, "
        f"gate_passed={result.gate_passed}."
    )


@pytest.mark.xfail(
    reason="H-04: insufficient coverage (2+ dimensions None) should abstain "
           "before evaluating the gate.",
    strict=False,
)
def test_ccs_insufficient_coverage_abstains():
    # Only one dimension present (temporal), the rest unknown.
    result = compute_causal_closure(temporal_coherence=Fraction(9, 10))
    assert result.verdict_cap == "ABSTAIN", (
        "With 3 of 4 dimensions unknown there is insufficient causal closure; "
        f"should ABSTAIN. Got: {result.verdict_cap!r}."
    )


# ===========================================================================
# H-05 — Corroboration: MALICE requires INDEPENDENT sources, not quantity
# ===========================================================================

_scorer = pytest.importorskip(
    "vigia_scorer",
    reason="vigia_scorer not importable (run with PYTHONPATH=$(pwd))",
)
_vigia_score = _scorer._vigia_score


def _single_source_clones() -> dict:
    """
    Four artifacts from the SAME tool and the SAME evidence_type, with a
    STATISTICAL_UNIFORMITY violation that pushes the score upward.
    There is no real heterogeneous corroboration: it is a single source repeated.
    """
    arts = [
        {
            "artifact_id": f"log_{i}",
            "evidence_type": "log_entry",
            "source_tool": "read_evidence",
            "timestamp": f"2026-04-10T10:0{i}:00Z",
            "raw_score": 0.9,
            "prior_trust": 0.9,
            "provenance_chain": [f"sha256:c{i}"],
            "description": "Same tool, same type — replicated entry.",
            "metadata": {"idx": i},
        }
        for i in range(4)
    ]
    return {
        "case_id": "FP-CORROBORATION-CLONES",
        "artifacts": arts,
        "temporal_violations": [
            {"type": "STATISTICAL_UNIFORMITY", "severity": 0.9,
             "cause": {"artifact_id": "log_0"}, "effect": {"artifact_id": "log_1"}}
        ],
        "caie_fractures": [],
        "expected_verdict": "SUSPICION",
        "peirce_chain": {},
    }


def test_malice_requires_independent_sources():
    """H-05 — RESOLVED (B-068 gate, R4-3 v2): this test now guards the gate.

    History: the original version was xfail(strict=False) and only asserted
    when the verdict was already MALICE, so it sat permanently in XPASS
    without exercising anything. Verified 2026-07-17: the clone case scores
    0.4638 — ABOVE the 0.33 MALICE threshold — and it is the R4-3 v2
    corroboration gate (single soft collection domain, same tool/type) that
    caps the verdict at SUSPICION. That is exactly the property H-05
    demanded, so the test is rewritten as a direct, always-armed guard:

    1. The score must stay above the MALICE threshold — otherwise the gate
       is not the deciding factor and the guard silently stops testing it
       (the trap the old NOTE warned about). If a recalibration drops the
       clone score below 0.33, raise the fixture's raw_scores.
    2. Four same-tool same-type artifacts must NOT reach MALICE, and the
       reason must attribute the cap to the corroboration gate.
    """
    result = _vigia_score(_single_source_clones())
    score = float(result.get("score", 0))
    assert score > 0.33, (
        "The clone fixture no longer crosses the MALICE threshold "
        f"(score={score}); the corroboration gate is not being exercised. "
        "Raise the fixture's raw_scores so this guard keeps testing the gate."
    )
    assert result.get("verdict") != "MALICE", (
        "MALICE was reached with a single source repeated 4 times. "
        "Corroboration must count independent sources, not artifact quantity "
        f"or labels. reason={result.get('reason')!r}."
    )
    assert "corroborat" in str(result.get("reason", "")).lower(), (
        "The verdict was capped below MALICE but not by the corroboration "
        "gate — the H-05 property is not what is being tested. "
        f"reason={result.get('reason')!r}."
    )


# ===========================================================================
# H-10 — A silently discarded artifact must be reported in the verdict
# ===========================================================================

# The silent drop (`except Exception: continue`) only occurs in the live CAIE
# branch. If CAIE is not available, _vigia_score uses fallback and does not go
# through that path, so the test requires CAIE importable.
pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie not importable; the silent drop only occurs with live CAIE",
)


def _case_with_one_malformed_artifact() -> dict:
    return {
        "case_id": "AUDIT-REJECTION-VISIBLE",
        "artifacts": [
            {
                "artifact_id": "good_001",
                "evidence_type": "memory_process",
                "source_tool": "list_processes",
                "timestamp": "2026-04-10T10:00:00Z",
                "raw_score": 0.7,
                "prior_trust": 0.9,
                "provenance_chain": ["sha256:g1"],
                "description": "valid artifact",
                "metadata": {},
            },
            {
                # raw_score not numeric -> breaks CAIE construction ->
                # currently discarded with `continue` without leaving a trace.
                "artifact_id": "broken_001",
                "evidence_type": "memory_process",
                "source_tool": "list_processes",
                "timestamp": "2026-04-10T10:00:01Z",
                "raw_score": "not_a_number",
                "prior_trust": 0.9,
                "provenance_chain": ["sha256:b1"],
                "description": "malformed artifact that would have produced a fracture",
                "metadata": {},
            },
        ],
        "temporal_violations": [],
        "caie_fractures": [],
        "expected_verdict": "UNKNOWN",
        "peirce_chain": {},
    }


@pytest.mark.xfail(
    reason="H-10: malformed artifact is discarded with `except Exception: continue` "
           "without being reported. The verdict must expose a rejection count "
           "(artifacts_rejected) to preserve reproducibility/completeness.",
    strict=False,
)
def test_rejected_artifact_is_surfaced_in_verdict():
    result = _vigia_score(_case_with_one_malformed_artifact())
    rejected = (
        result.get("artifacts_rejected")
        or result.get("rejected_count")
        or result.get("rejected_artifacts")
    )
    assert rejected, (
        "A malformed artifact was discarded without reporting it in the output. "
        "A silent discard changes the verdict in an un-auditable way. "
        f"Result keys: {sorted(result.keys())}."
    )
