"""B-116 — the pending SignalQualityGate must accept Fraction z_scores.

Same latent class as B-211: the gate's reason_detail strings use
f"{...:.2f}" / f"{...:.3f}", which Fraction does not support on
Python < 3.12. The VIGIA pipeline transports z_scores as Fraction, so the
moment the gate is wired it would have crashed on the CI-pinned 3.11.
Zero production callers today — this guards the pending-to-wire capability,
it does not wire it.
"""
from __future__ import annotations

from fractions import Fraction
from types import SimpleNamespace

from vigia.core.signal_quality_gate import SignalQualityGate


def _signal(tool: str, z) -> SimpleNamespace:
    return SimpleNamespace(
        tool_name=tool, z_score=z, source_tool=tool, evidence_type="log"
    )


class TestFractionZScores:
    def test_fraction_z_does_not_crash_and_passes(self) -> None:
        sigs = [_signal(f"tool{i}", Fraction(5 + i, 2)) for i in range(3)]
        result = SignalQualityGate().evaluate(sigs)
        assert result.reason_code == "QUALITY_OK"
        assert "max_z=" in result.reason_detail

    def test_fraction_z_weak_signals_still_degrade(self) -> None:
        sigs = [_signal(f"tool{i}", Fraction(1, 2)) for i in range(3)]
        result = SignalQualityGate().evaluate(sigs)
        assert result.passed is False
        assert result.reason_code == "ABSTAIN_WEAK_SIGNALS"

    def test_fraction_and_float_z_agree(self) -> None:
        gate = SignalQualityGate()
        as_fraction = [
            _signal("a", Fraction(5, 2)),
            _signal("b", Fraction(3, 1)),
            _signal("c", Fraction(9, 4)),
        ]
        as_float = [
            _signal("a", 2.5),
            _signal("b", 3.0),
            _signal("c", 2.25),
        ]
        r_frac = gate.evaluate(as_fraction)
        r_float = gate.evaluate(as_float)
        assert r_frac.passed == r_float.passed
        assert r_frac.reason_code == r_float.reason_code

    def test_negative_fraction_z_uses_magnitude(self) -> None:
        sigs = [
            _signal("a", Fraction(-5, 2)),
            _signal("b", Fraction(3, 1)),
            _signal("c", Fraction(-9, 4)),
        ]
        result = SignalQualityGate().evaluate(sigs)
        assert result.reason_code == "QUALITY_OK"
