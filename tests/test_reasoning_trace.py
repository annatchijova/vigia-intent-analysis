"""
tests/test_reasoning_trace.py
=============================
Tests for vigia/core/reasoning_trace.py — the native Cronos-adapted reasoning
trace. Covers determinism, the B-148 honest-degradation doctrine enforced at the
API, the diversity/confidence epistemics, contradiction detection, and the
B-151b self-correction chaining via ToolExecutionLogChain.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from vigia.core.reasoning_trace import (
    ForensicReasoningTrace,
    ObservationState,
    TraceQuality,
    detect_negation,
)

_TS = "2026-01-01T00:00:00+00:00"  # injected, deterministic seal timestamp


def _full_trace(case_id="CASE-DET"):
    t = ForensicReasoningTrace(case_id=case_id, objective="why this path")
    t.record_tool_call("infer_intent", "artifact-3", "intent=deliberate")
    t.add_hypothesis("malice", "deliberate anti-forensics")
    t.add_hypothesis("benign", "careless sysadmin")
    t.add_evidence("log deletion observed in memory", ObservationState.ANALYZED, supports="malice")
    t.discard_hypothesis("benign", "no config change explains the deletion")
    return t


# ── Determinism ────────────────────────────────────────────────────────────────

def test_same_investigation_seals_identically():
    a = _full_trace().seal("SUSPICION", Fraction(3, 5), sealed_at=_TS)
    b = _full_trace().seal("SUSPICION", Fraction(3, 5), sealed_at=_TS)
    assert a["chain_tip_sha256"] == b["chain_tip_sha256"]
    assert a == b  # full structural equality — no uuid4/now() leaked in


def test_trace_id_is_derived_from_case_id():
    t = ForensicReasoningTrace(case_id="CASE-42", objective="o")
    assert t.trace_id == "rt-CASE-42"


# ── B-148 doctrine enforced at the API ─────────────────────────────────────────

@pytest.mark.parametrize("state", [ObservationState.NOT_ANALYZED, ObservationState.ANALYSIS_FAILED])
def test_non_analyzed_evidence_cannot_support(state):
    t = ForensicReasoningTrace(case_id="C", objective="o")
    t.add_hypothesis("malice", "d")
    with pytest.raises(ValueError, match="absence of analysis is not a positive observation"):
        t.add_evidence("memory had no network fields", state, supports="malice")


def test_not_analyzed_evidence_allowed_without_link():
    t = ForensicReasoningTrace(case_id="C", objective="o")
    t.add_evidence("network layer never analyzed", ObservationState.NOT_ANALYZED)  # OK: attenuating


def test_evidence_cannot_both_support_and_refute():
    t = ForensicReasoningTrace(case_id="C", objective="o")
    with pytest.raises(ValueError, match="cannot both support and refute"):
        t.add_evidence("x", ObservationState.ANALYZED, supports="a", refutes="b")


# ── Diversity / confidence ceiling: NOT_ANALYZED must not inflate ──────────────

def test_not_analyzed_evidence_does_not_raise_diversity_or_ceiling():
    # Tools + hypotheses present, but the only "evidence" is NOT_ANALYZED.
    t = ForensicReasoningTrace(case_id="C", objective="o")
    t.record_tool_call("list_files", "/ev", "3 files")
    t.add_hypothesis("malice", "d")
    t.add_evidence("network never analyzed", ObservationState.NOT_ANALYZED)  # group B must NOT count
    sealed = t.seal("SUSPICION", Fraction(9, 10), sealed_at=_TS)
    # Only 2 of 3 groups (TOOL + HYPOTHESIS) → ceiling 0.85; the 0.90 is capped.
    assert sealed["quality"] == TraceQuality.PARTIAL.value
    assert sealed["confidence_stored"] == "17/20"
    assert sealed["confidence_warnings"]


def test_analyzed_evidence_reaches_full_diversity():
    sealed = _full_trace().seal("SUSPICION", Fraction(1), sealed_at=_TS)
    assert sealed["quality"] == TraceQuality.FULL.value
    assert sealed["diversity"] == "3/3"
    assert sealed["confidence_stored"] == "1/1"  # no ceiling at full diversity


# ── Contradiction detection ────────────────────────────────────────────────────

def test_contradiction_detected_on_support_and_refute():
    t = ForensicReasoningTrace(case_id="C", objective="o")
    t.add_hypothesis("malice", "d")
    t.add_evidence("log deletion", ObservationState.ANALYZED, supports="malice")
    t.add_evidence("but the deletion is a documented rotation job", ObservationState.ANALYZED, refutes="malice")
    sealed = t.seal("ABSTAIN", Fraction(1, 2), sealed_at=_TS)
    assert any("Type A" in c and "malice" in c for c in sealed["contradictions"])


# ── B-151b: self-correction chained as contradiction_detector ──────────────────

def test_self_correction_chained_as_contradiction_detector():
    t = ForensicReasoningTrace(case_id="C", objective="o")
    t.add_hypothesis("malice", "d")
    t.record_self_correction("F-001", "MALICE", "SUSPICION",
                             "single-source: Daubert corroboration gate")
    sealed = t.seal("SUSPICION", Fraction(1, 2), sealed_at=_TS)
    sc = [e for e in sealed["tool_execution_log"] if e["tool"] == "contradiction_detector"]
    assert len(sc) == 1
    assert "BEFORE: MALICE | AFTER: SUSPICION" in sc[0]["result_summary"]


# ── Chain integrity of the produced log ────────────────────────────────────────

def test_produced_log_verifies_intact():
    from vigia.core.tool_log_chain import verify_tool_execution_log
    sealed = _full_trace().seal("SUSPICION", Fraction(3, 5), sealed_at=_TS)
    result = verify_tool_execution_log(sealed["tool_execution_log"])
    assert result.valid, result.to_dict()


def test_tampering_breaks_the_chain():
    from vigia.core.tool_log_chain import verify_tool_execution_log
    sealed = _full_trace().seal("SUSPICION", Fraction(3, 5), sealed_at=_TS)
    log = sealed["tool_execution_log"]
    log[1]["result_summary"] = "TAMPERED"
    result = verify_tool_execution_log(log)
    assert not result.valid


# ── Invariants ─────────────────────────────────────────────────────────────────

def test_confidence_must_be_fraction():
    t = ForensicReasoningTrace(case_id="C", objective="o")
    with pytest.raises(TypeError, match="Fraction"):
        t.seal("SUSPICION", 0.6, sealed_at=_TS)  # float rejected


def test_no_steps_after_seal():
    t = _full_trace()
    t.seal("SUSPICION", Fraction(3, 5), sealed_at=_TS)
    with pytest.raises(RuntimeError, match="already sealed"):
        t.add_hypothesis("late", "too late")


def test_detect_negation():
    assert detect_negation("no network activity observed")
    assert detect_negation("the socket table was absent")
    assert not detect_negation("outbound connection to 8.8.8.8 confirmed")
