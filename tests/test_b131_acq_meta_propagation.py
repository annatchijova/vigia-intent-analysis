"""
B-131 — Acquisition metadata must propagate to engine-derived signals.

The Gamma loop (step 4 of run_full_analysis) injects examiner-declared
acquisition metadata (acquisition_tool, examiner_id, write_blocker_used,
plus chain-derived acquisition_hash / acquisition_timestamp) into every
raw SIFT signal. Signals created AFTER the Gamma loop — engine motors
(step 6: Metabolic, Resonance, Behavioral, Patterns), the unified
timeline (step 7) and the adversarial robustness signal (step 8) —
bypassed that injection entirely, so CAIE degraded their base_trust to
0.10 for missing chain-of-custody fields (NIST SP 800-86 §4.3) even when
the examiner had declared them via CLI flags.

Detected in VIGIA-REAL-VANKO-2026 RAW run 2026-07-14 (CROSS_RESONANCE,
CASE_PATTERN_LIBRARY, ADV_ROBUST lost all acquisition fields).

The fix injects the same _acq_meta mapping into every post-Gamma signal
with the merge precedence used by the Gamma loop: the signal's own
metadata wins over injected acquisition fields.
"""

import logging

import pytest

from vigia.sift.sift_orchestrator import SIFTOrchestrator
from vigia.tools.signal_contract import SignalOutput

logging.disable(logging.CRITICAL)

_ACQ_OVERRIDES = {
    "acquisition_tool": "test-imager 1.0",
    "examiner_id": "EX-01",
    "write_blocker_used": True,
}

# 20 irregular but deterministic timestamps so MetabolicProfiler and
# BehavioralFingerprint produce a real profile (>= 2 events required).
_EVENTS = [{"timestamp": 1_700_000_000 + i * 37, "event": f"e{i}"} for i in range(20)]


def _run_with_overrides():
    orch = SIFTOrchestrator("B131-TEST")
    orch.acquisition_overrides = dict(_ACQ_OVERRIDES)
    result = orch.run_full_analysis(event_stream=list(_EVENTS))
    return result["signals"]


def _derived_engine_signals(signals):
    """Engine-derived signals (not honest 'unanalyzed' stubs, which pass
    through the Gamma loop and were never affected by B-131)."""
    return [
        s for s in signals
        if isinstance(s.get("metadata"), dict)
        and s["metadata"].get("signal_class") == "derived"
        and not s["metadata"].get("unanalyzed")
    ]


class TestB131AcqMetaPropagation:
    def test_derived_engine_signals_exist(self):
        derived = _derived_engine_signals(_run_with_overrides())
        assert derived, (
            "Recon precondition failed: no engine-derived signals produced — "
            "the propagation assertions below would be vacuous."
        )

    def test_derived_signals_carry_examiner_declared_fields(self):
        derived = _derived_engine_signals(_run_with_overrides())
        missing = {
            s.get("tool") or s.get("tool_name"): [
                k for k in _ACQ_OVERRIDES if k not in s["metadata"]
            ]
            for s in derived
        }
        offenders = {tool: gap for tool, gap in missing.items() if gap}
        assert not offenders, (
            "B-131: engine-derived signals lost examiner-declared acquisition "
            f"metadata (CAIE degrades their base_trust to 0.10): {offenders}"
        )

    def test_signal_own_metadata_takes_precedence(self):
        """The merge must be {**acq_meta, **sig.metadata}: a signal that
        already carries its own acquisition fields is NOT overwritten."""
        sig = SignalOutput(
            tool_name="X",
            signal_id="X-test-0001",
            value=1.0,
            z_score=0.0,
            confidence=0.5,
            metadata={"acquisition_tool": "engine-declared"},
        )
        merged = SIFTOrchestrator._inject_acq_meta(sig, dict(_ACQ_OVERRIDES))
        assert merged.metadata["acquisition_tool"] == "engine-declared"
        assert merged.metadata["examiner_id"] == "EX-01"
        assert merged.metadata["write_blocker_used"] is True

    def test_empty_acq_meta_is_noop(self):
        sig = SignalOutput(
            tool_name="X", signal_id="X-test-0002", value=1.0, z_score=0.0,
            confidence=0.5, metadata={"k": "v"},
        )
        merged = SIFTOrchestrator._inject_acq_meta(sig, {})
        assert merged.metadata == {"k": "v"}

    def test_none_signal_passthrough(self):
        assert SIFTOrchestrator._inject_acq_meta(None, dict(_ACQ_OVERRIDES)) is None
