"""
tests/characterization/test_temporal_gate_curve.py
==================================================
CHARACTERIZATION test for the temporal gate (H-01). Generated 2026-07-17.

This test DOES NOT JUDGE. It pins the CURRENT behavior of both temporal
paths so that any future change — deliberate or accidental — is visible in
the diff. It is the empirical dataset for the H-01 window decision: you do
not decide the tolerance window from intuition, you decide it against this
curve.

What it documents (verified 2026-07-17, this is the behavior BEFORE any
tolerance window exists):

  PATH (a) — scorer hard gate (vigia_scorer._vigia_score):
    The hard gate reads ONLY `type == EFFECT_BEFORE_CAUSE` and
    `severity >= 0.9` from the pre-computed `temporal_violations` list
    (vigia_scorer.py L1120-1122). It NEVER parses the timestamps and NEVER
    reads `delta_seconds`. Consequence, pinned below: the verdict is MALICE
    for EVERY delta — including delta = 0 and delta = +2 (the network event
    AFTER the process, i.e. NO violation at all) — because the fixture
    asserts the violation and the scorer trusts it verbatim. `clock_source`
    is dead metadata: no production code path reads it.
    => The tolerance window for path (a) CANNOT live in the scorer's hard
       gate (it has no delta to test). It must live wherever
       `temporal_violations` is POPULATED upstream, or the hard gate must
       start validating the asserted pair against the real timestamps.

  PATH (b) — CAIE TCV rule (CrossArtifactIncongruenceEngine.detect_fractures):
    Computes the sign correctly from real structured timestamps
    (net_time < proc_time, caie.py L1784). But `severity` is a hard-coded
    1.0 for ANY negative delta (L1790): a -0.1s skew and a -3600s timestomp
    are indistinguishable. `clock_source` is again ignored.
    => This is where a magnitude-scaled severity (or an intra-source vs.
       cross-source distinction) would live.

CONTRACT: these are pins, not aspirations. If you implement the H-01
tolerance window, THESE TESTS WILL FAIL — that is intended. Update the
pinned values in the same commit that changes the behavior, and cross-check
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
# PATH (a): scorer hard gate — pinned FLAT (MALICE everywhere, delta ignored)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("delta", _DELTAS)
@pytest.mark.parametrize("clock_source", _CLOCK_SOURCES)
def test_char_scorer_hard_gate_is_flat(delta, clock_source):
    """PIN: scorer verdict is MALICE + hard_temporal_gate for every delta and
    clock_source, because the hard gate trusts the asserted violation without
    reading timestamps. This includes delta >= 0 (no real violation).

    If the H-01 window lands and this cell stops being MALICE, update the pin.
    """
    result = _vigia_score(_scorer_case(delta, clock_source))
    assert result.get("hard_temporal_gate") is True, (
        f"CHARACTERIZATION PIN MOVED (path a): delta={delta}, "
        f"clock_source={clock_source} no longer trips the hard gate. If this "
        "is the H-01 tolerance fix, update this pin and the curve docstring."
    )
    assert result.get("verdict") == "MALICE", (
        f"CHARACTERIZATION PIN MOVED (path a): delta={delta}, "
        f"clock_source={clock_source} verdict is now "
        f"{result.get('verdict')!r}, was MALICE."
    )


def test_char_scorer_ignores_clock_source_and_delta_sign():
    """PIN (explicit): path (a) is blind to both the delta sign and the clock
    source. delta=+2 (network AFTER process, no violation) still yields MALICE
    because the fixture asserts EFFECT_BEFORE_CAUSE and the scorer does not
    re-derive it. This is the load-bearing finding for the H-01 decision:
    the tolerance window cannot be implemented in the scorer's hard gate.
    """
    positive = _vigia_score(_scorer_case(2.0, "host_ntp"))
    assert positive.get("verdict") == "MALICE", (
        "CHARACTERIZATION PIN MOVED: path (a) started distinguishing a "
        "non-violating positive delta. That means the scorer now validates "
        "the asserted violation against timestamps — a real H-01 change."
    )


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
