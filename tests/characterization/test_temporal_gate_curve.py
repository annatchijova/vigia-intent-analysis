"""
tests/characterization/test_temporal_gate_curve.py
==================================================
CHARACTERIZATION test for the temporal gate (H-01). Generated 2026-07-17.

This test DOES NOT JUDGE. It pins the CURRENT behavior of both temporal
paths so that any future change — deliberate or accidental — is visible in
the diff. It is the empirical dataset for the H-01 window decision: you do
not decide the tolerance window from intuition, you decide it against this
curve.

What it documents (revised 2026-07-21 after B-172, still BEFORE any tolerance
window exists):

  PATH (a) — scorer hard gate (vigia_scorer._vigia_score):
    B-172 re-derives the asserted pair from the two referenced artifact
    timestamps. Negative ordering still yields MALICE under the legacy
    no-tolerance policy. Zero/positive ordering cannot become MALICE merely
    because JSON asserts it: the result is ABSTAIN with the unverified claim
    preserved. `clock_source` remains dead metadata: B-172 fixes claim
    validation, not the separate skew-window decision.

  PATH (b) — CAIE TCV rule (CrossArtifactIncongruenceEngine.detect_fractures):
    Computes the sign correctly from real structured timestamps
    (net_time < proc_time, caie.py L1784). But `severity` is a hard-coded
    1.0 for ANY negative delta (L1790): a -0.1s skew and a -3600s timestomp
    are indistinguishable. `clock_source` is again ignored.
    => This is where a magnitude-scaled severity (or an intra-source vs.
       cross-source distinction) would live.

CONTRACT: these are pins, not aspirations. If you implement the H-01
tolerance window, the negative-delta cells may move — that is intended. Update
the pinned values in the same commit that changes the behavior, and cross-check
that the change matches the documented window decision. Do not silence a
failure here without understanding which cell of the curve moved and why.

Run: PYTHONPATH=$(pwd) pytest tests/characterization/ -v --no-cov
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

_scorer = pytest.importorskip(
    "vigia_scorer",
    reason="vigia_scorer not importable (run with PYTHONPATH=$(pwd))",
)
_vigia_score = _scorer._vigia_score

caie = pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie not importable (run with PYTHONPATH=$(pwd))",
)
CrossArtifactIncongruenceEngine = caie.CrossArtifactIncongruenceEngine
Artifact = caie.Artifact


_PROC_TIME = "2026-04-10T10:00:05Z"
_PROC_DT = datetime.fromisoformat("2026-04-10T10:00:05+00:00")

# Delta of the network event relative to the process creation time, in
# seconds. Negative => network BEFORE process (the "violation" region).
# Positive/zero => network AT or AFTER process (no violation).
_DELTAS = [-3600.0, -60.0, -30.0, -10.0, -5.0, -1.0, -0.1, 0.0, 2.0]
_CLOCK_SOURCES = ["host_ntp", "ids_sensor"]


def _net_time(delta_seconds: float) -> str:
    return (_PROC_DT + timedelta(seconds=delta_seconds)).isoformat()


def _scorer_case(delta_seconds: float, clock_source: str) -> dict:
    net_t = _net_time(delta_seconds)
    return {
        "case_id": "CHAR-TEMPORAL-SKEW",
        "artifacts": [
            {
                "artifact_id": "proc_001", "evidence_type": "memory_process",
                "source_tool": "list_processes", "timestamp": _PROC_TIME,
                "raw_score": 0.40, "prior_trust": 0.95,
                "provenance_chain": ["sha256:p1"], "description": "proc",
                "metadata": {"pid": 4412, "clock_source": "host_ntp",
                             "process_creation_time": _PROC_TIME},
            },
            {
                "artifact_id": "net_001", "evidence_type": "log_entry",
                "source_tool": "read_evidence", "timestamp": net_t,
                "raw_score": 0.30, "prior_trust": 0.70,
                "provenance_chain": ["sha256:n1"], "description": "net",
                "metadata": {"clock_source": clock_source,
                             "network_log_time": net_t},
            },
        ],
        # The upstream-asserted violation. Present for EVERY delta, including
        # the non-violating ones — this is the whole point of path (a): the
        # scorer never re-derives it from the timestamps.
        "temporal_violations": [{
            "type": "EFFECT_BEFORE_CAUSE", "severity": 1.0,
            "cause": {"artifact_id": "proc_001", "timestamp": _PROC_TIME},
            "effect": {"artifact_id": "net_001", "timestamp": net_t},
            "delta_seconds": delta_seconds,
        }],
        "caie_fractures": [], "expected_verdict": "UNKNOWN", "peirce_chain": {},
    }


# ---------------------------------------------------------------------------
# PATH (a): scorer hard gate — validates pair, but no skew tolerance yet
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delta", _DELTAS)
@pytest.mark.parametrize("clock_source", _CLOCK_SOURCES)
def test_char_scorer_hard_gate_requires_artifact_inversion(delta, clock_source):
    """PIN: B-172 separates a real negative ordering from a contradicted JSON
    claim. H-01 tolerance is intentionally not decided here, so every verified
    negative delta still takes the existing hard gate."""
    result = _vigia_score(_scorer_case(delta, clock_source))
    if delta < 0:
        assert result.get("hard_temporal_gate") is True
        assert result.get("verdict") == "MALICE"
        assert result.get("hard_temporal_authority") == "validated_artifact_pair"
    else:
        assert result.get("hard_temporal_gate") is False
        assert result.get("verdict") == "ABSTAIN"
        assert result.get("hard_temporal_authority") == (
            "unverified_json_no_verdict_authority"
        )


def test_char_scorer_rejects_positive_order_claim():
    """PIN (explicit): an event after its alleged cause cannot produce MALICE
    from an `EFFECT_BEFORE_CAUSE` declaration. This validates authority, not
    the still-unresolved tolerance for genuinely negative deltas."""
    positive = _vigia_score(_scorer_case(2.0, "host_ntp"))
    assert positive.get("verdict") == "ABSTAIN"
    assert positive.get("hard_temporal_gate") is False


# ---------------------------------------------------------------------------
# PATH (b): CAIE TCV rule — pinned BINARY severity (1.0 for any negative delta)
# ---------------------------------------------------------------------------

def _caie_tcv_max_severity(delta_seconds: float, clock_source: str) -> float | None:
    engine = CrossArtifactIncongruenceEngine()
    net_t = _net_time(delta_seconds)
    engine.add_artifact(Artifact(
        source_tool="firewall", evidence_type="log_entry", raw_score=0.3,
        description="net",
        metadata={"network_log_time": net_t, "clock_source": clock_source},
        provenance_chain=["sha256:n1"], base_trust=0.7,
    ))
    engine.add_artifact(Artifact(
        source_tool="list_processes", evidence_type="memory_process",
        raw_score=0.4, description="proc",
        metadata={"process_creation_time": _PROC_TIME, "socket": True},
        provenance_chain=["sha256:p1"], base_trust=0.95,
    ))
    tcv = [f for f in engine.detect_fractures()
           if f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION"]
    return max((getattr(f, "severity", 0.0) for f in tcv), default=None)


@pytest.mark.parametrize("delta", [-3600.0, -60.0, -30.0, -10.0, -5.0, -1.0, -0.1])
@pytest.mark.parametrize("clock_source", _CLOCK_SOURCES)
def test_char_caie_tcv_severity_is_binary(delta, clock_source):
    """PIN: every NEGATIVE delta fires exactly one TCV at severity 1.0, with
    no scaling by magnitude and no sensitivity to clock_source. A -0.1s skew
    and a -3600s timestomp are indistinguishable here.

    If the H-01 fix makes severity scale with |delta| (or suppresses it below
    a tolerance), this pin moves. Update it with the window decision.
    """
    sev = _caie_tcv_max_severity(delta, clock_source)
    assert sev == 1.0, (
        f"CHARACTERIZATION PIN MOVED (path b): delta={delta}, "
        f"clock_source={clock_source} TCV severity is now {sev!r}, was 1.0. "
        "If this is the H-01 tolerance/scaling fix, update the pin."
    )


@pytest.mark.parametrize("clock_source", _CLOCK_SOURCES)
def test_char_caie_tcv_silent_when_no_violation(clock_source):
    """PIN (positive control): a positive delta (network AFTER process) fires
    NO TCV. This is the one place the current design already gets the sign
    right — the H-01 window must not break it.
    """
    sev = _caie_tcv_max_severity(2.0, clock_source)
    assert sev is None, (
        "CHARACTERIZATION PIN MOVED (path b): a non-violating positive delta "
        f"produced a TCV (severity={sev!r}). The sign logic regressed."
    )
