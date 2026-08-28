"""B-151(b) — the CLAUDE.md-mandated chained `contradiction_detector`
self-correction event, end to end in Mode-1.

CLAUDE.md's "Self-Correction Event Schema" requires every gate-driven downgrade
to append a `contradiction_detector` entry through `ToolExecutionLogChain`.
B-151(b) recorded this as unwired. The 2026-07-26 update corrected the
attribution: `vigia/core/reasoning_trace.py` implements and wires the mechanism,
and what was missing was the INPUT -- `ContradictionDetector` could not fire for
any possible input (B-224), so `pipeline_results["self_corrections"]` was always
empty and the chain had nothing to carry.

B-224 is now fixed, so the input path exists. This test drives the whole route
-- detector fires, CorrectionEngine records a correction, the sealing path turns
it into a chained entry -- so the closure of B-151(b) rests on an executed
assertion rather than on reading the two halves and inferring they meet.
"""

from __future__ import annotations

from pathlib import Path

from vigia_agent import VIGIAAgent
from vigia.core.reasoning_trace import build_from_agent_bundle

REPO = Path(__file__).resolve().parent.parent


def _corrected_results():
    """A Mode-1-shaped input that triggers the one live rule (VERDICT_FLIP):
    a conclusive benign hypothesis contradicted by two independent
    high-magnitude signals."""
    return {
        "abduction": {
            "best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED",
            "is_conclusive": True,
        },
        "signals": [
            {"evidence_type": "memory_process", "source": "sift_volatility",
             "z_score": 5.0, "confidence": 0.9},
            {"evidence_type": "network_flow", "source": "sift_netflow",
             "z_score": 4.0, "confidence": 0.9},
        ],
    }


def test_correction_reaches_the_sealed_reasoning_trace_as_a_chained_entry():
    agent = VIGIAAgent(
        case_id="B151B-CHAIN",
        evidence_path=str(REPO / "cases/input/VIGIA-REAL-007.json"),
    )
    had_corrections, results = agent._detect_and_correct(_corrected_results())
    assert had_corrections, "detector produced no correction -- B-224 regressed"
    assert results.get("self_corrections"), "self_corrections not populated"

    bundle = {
        "case_id": "B151B-CHAIN",
        "agent_verdict": "MALICE",
        "evidence_path": "synthetic",
        "analysis_timestamp": "2026-08-15T00:00:00+00:00",
        "pipeline_results": results,
    }
    trace = build_from_agent_bundle(bundle)

    entries = trace.get("tool_execution_log") or []
    chained = [e for e in entries if e.get("tool") == "contradiction_detector"]
    assert chained, (
        f"no contradiction_detector entry in the trace; tools present: "
        f"{sorted({e.get('tool') for e in entries})}"
    )

    entry = chained[0]
    # The chain fields CLAUDE.md's schema requires.
    for field in ("seq", "timestamp", "tool", "result_summary",
                  "input_hash", "prev_hash", "entry_hash"):
        assert field in entry, f"chained entry missing {field!r}: {entry}"
    assert "BEFORE" in entry["result_summary"] and "AFTER" in entry["result_summary"], (
        f"self-correction summary must carry before/after: {entry['result_summary']!r}"
    )


def test_trace_carries_the_bundle_level_tail_anchor():
    """R3-5: truncating the log tail must remain detectable."""
    agent = VIGIAAgent(
        case_id="B151B-ANCHOR",
        evidence_path=str(REPO / "cases/input/VIGIA-REAL-007.json"),
    )
    _, results = agent._detect_and_correct(_corrected_results())
    trace = build_from_agent_bundle({
        "case_id": "B151B-ANCHOR",
        "agent_verdict": "MALICE",
        "analysis_timestamp": "2026-08-15T00:00:00+00:00",
        "pipeline_results": results,
    })
    assert trace.get("chain_tip_sha256"), "tail anchor absent from the trace"
    entries = trace.get("tool_execution_log") or []
    assert trace["chain_tip_sha256"] == entries[-1]["entry_hash"], (
        "chain_tip_sha256 does not match the last entry's hash"
    )


def test_no_correction_means_no_contradiction_entry():
    """Control: the entry appears because a correction happened, not because the
    trace builder emits one unconditionally."""
    trace = build_from_agent_bundle({
        "case_id": "B151B-QUIET",
        "agent_verdict": "SUSPICION",
        "analysis_timestamp": "2026-08-15T00:00:00+00:00",
        "pipeline_results": {
            "abduction": {"best_hypothesis": "SUSPICION_DETECTED"},
            "self_corrections": [],
        },
    })
    entries = trace.get("tool_execution_log") or []
    assert not [e for e in entries if e.get("tool") == "contradiction_detector"]
