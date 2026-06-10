"""
tests/test_audit_temporal_skew.py
=================================
Red-team audit — Finding H-01: hard temporal gate without tolerance or external
clock anchor.

The hard gate fires MALICE unconditionally (confidence 0.95) as soon as
net_time < proc_time, with no tolerance window. But clock skew between sensors
(IDS/firewall/EDR/host) is the norm in DFIR, not the exception. Three seconds
of NTP drift is not a "violation of the laws of physics".

Two code paths:
  (a) case["temporal_violations"] with type=EFFECT_BEFORE_CAUSE, sev>=0.9
      -> hard_temporal in _vigia_score -> MALICE unconditional.
  (b) CAIE detects TEMPORAL_CAUSALITY_VIOLATION (severity 1.0) comparing
      network_log_time vs process_creation_time.

These tests cover both. They are xfail until a configurable tolerance exists
(sealed in PolicySpec) and cross-corroboration beyond timestamps is required.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Path (a): hard gate in the scorer
# ---------------------------------------------------------------------------

_scorer = pytest.importorskip(
    "vigia_scorer",
    reason="vigia_scorer not importable (run with PYTHONPATH=$(pwd))",
)
_vigia_score = _scorer._vigia_score


def _skew_case(delta_seconds: int = -2) -> dict:
    """
    Case with a small negative delta between process creation and an event
    attributed to it. Ground truth: benign clock skew between two distinct
    sources, NOT timestomp.
    """
    return {
        "case_id": "FP-TEMPORAL-SKEW",
        "artifacts": [
            {
                "artifact_id": "proc_001",
                "evidence_type": "memory_process",
                "source_tool": "list_processes",
                "timestamp": "2026-04-10T10:00:05Z",
                "raw_score": 0.40,
                "prior_trust": 0.95,
                "provenance_chain": ["sha256:p1", "sha256:p2"],
                "description": "Process svchost.exe spawned (host clock).",
                "metadata": {"pid": 4412, "clock_source": "host_ntp"},
            },
            {
                "artifact_id": "net_001",
                "evidence_type": "log_entry",
                "source_tool": "read_evidence",
                "timestamp": "2026-04-10T10:00:03Z",
                "raw_score": 0.30,
                "prior_trust": 0.70,
                "provenance_chain": ["sha256:n1"],
                "description": "Network connection log (IDS clock, +2s drift vs host).",
                "metadata": {"clock_source": "ids_sensor"},
            },
        ],
        # The skew is presented as EFFECT_BEFORE_CAUSE with small delta.
        # Ground truth: NOT manipulation. The system should tolerate it.
        "temporal_violations": [
            {
                "type": "EFFECT_BEFORE_CAUSE",
                "severity": 1.0,
                "cause": {"artifact_id": "proc_001", "timestamp": "2026-04-10T10:00:05Z"},
                "effect": {"artifact_id": "net_001", "timestamp": "2026-04-10T10:00:03Z"},
                "delta_seconds": delta_seconds,
                "interpretation": "Network event 2s before process — likely NTP skew.",
            }
        ],
        "caie_fractures": [],
        "expected_verdict": "UNKNOWN",
        "peirce_chain": {},
    }


@pytest.mark.xfail(
    reason="H-01: the hard gate fires MALICE for 2s of skew. Transitions to XPASS "
           "when tolerance_seconds exists and the gate requires cross-corroboration.",
    strict=False,
)
def test_small_skew_does_not_hard_gate_to_malice():
    result = _vigia_score(_skew_case(delta_seconds=-2))

    assert result.get("hard_temporal_gate") is not True, (
        "The hard temporal gate activated for a 2-second skew. "
        "This turns synchronization noise into unconditional MALICE."
    )
    assert result.get("verdict") != "MALICE", (
        "Unconditional MALICE verdict from benign clock skew. "
        f"Got: {result.get('verdict')} / reason={result.get('reason')!r}."
    )


def test_large_negative_delta_still_flags():
    """
    Positive control: a large, deliberate delta (e.g. -3600s) MUST still be
    detected. This test is NOT xfail — it protects against over-correction
    (the tolerance fix must not nullify real timestomp detection).
    Adjust the threshold if your final tolerance differs.
    """
    result = _vigia_score(_skew_case(delta_seconds=-3600))
    assert result.get("verdict") in ("MALICE", "SUSPICION"), (
        "A delta of -1h (clear timestomp) must still be detected. "
        f"Got: {result.get('verdict')}."
    )


# ---------------------------------------------------------------------------
# Path (b): TCV rule in CAIE
# ---------------------------------------------------------------------------

caie = pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie not importable (run with PYTHONPATH=$(pwd))",
)
CrossArtifactIncongruenceEngine = caie.CrossArtifactIncongruenceEngine
Artifact = caie.Artifact


@pytest.mark.xfail(
    reason="H-01: the TCV rule emits severity 1.0 for any negative delta, "
           "without a tolerance window. Transitions to XPASS when |delta| <= "
           "tolerance stops generating TEMPORAL_CAUSALITY_VIOLATION at max severity.",
    strict=False,
)
def test_tcv_rule_tolerates_small_skew():
    engine = CrossArtifactIncongruenceEngine()
    engine.add_artifact(Artifact(
        source_tool="firewall",
        evidence_type="log_entry",
        raw_score=0.3,
        description="network connection (red) outbound — IDS sensor clock",
        metadata={"network_log_time": "2026-04-10T10:00:03Z", "clock_source": "ids"},
        provenance_chain=["sha256:n1"],
        base_trust=0.7,
    ))
    engine.add_artifact(Artifact(
        source_tool="list_processes",
        evidence_type="memory_process",
        raw_score=0.4,
        description="process creation — host clock",
        metadata={"process_creation_time": "2026-04-10T10:00:05Z", "socket": True},
        provenance_chain=["sha256:p1"],
        base_trust=0.95,
    ))

    fractures = engine.detect_fractures()
    tcv = [f for f in fractures if f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION"]

    assert not any(getattr(f, "severity", 0) >= 0.9 for f in tcv), (
        "The TCV rule marked max severity for a 2s skew between two different "
        "clocks. It needs a tolerance window before declaring a physical impossibility."
    )
