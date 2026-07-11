"""Regression tests for B-099 — degenerate H27 internal-drift PSI.

Both H27 blocks (run_vigia seed-42 sampled reference; run_full split-half)
saturated to drift=1.0 for benign and anomalous input alike at forensic
sample sizes: a constant disguised as a measurement, sealed into the decision
path, where drift multiplies risk up to x3 and can flip
ACCEPT -> ABSTAIN -> REJECT.

Fixed behavior under test (RiskBoundedDecisionLayer.internal_drift_from_z_scores):
- genuine N(0,1) z-scores do NOT saturate (the old code gave 1.0 on 100% of
  20k genuine samples at n=2-3, 67-100% up to n=50);
- shifted / extreme z-scores still saturate (discrimination preserved);
- n < 4 returns None (indeterminate: below that even all-z=5 has no power),
  and the pipeline falls back to the documented external drift;
- deterministic and input-order invariant (no RNG).
"""

import json
import random
import sys

import pytest

from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer as RBL


class TestInternalDriftUnit:
    def test_indeterminate_below_four_signals(self):
        assert RBL.internal_drift_from_z_scores([]) is None
        assert RBL.internal_drift_from_z_scores([0.1]) is None
        assert RBL.internal_drift_from_z_scores([0.1, -0.2]) is None
        # Even extreme input is indeterminate at n<4 — no power either way.
        assert RBL.internal_drift_from_z_scores([5.0, 5.0, 5.0]) is None

    def test_genuine_gaussian_does_not_saturate(self):
        # 50 fixed-seed genuine N(0,1) samples at the sizes that used to
        # saturate 100% of the time. Allow the documented <=2% false-
        # saturation rate: over 150 draws, more than 10 saturations means
        # the degenerate estimator is back.
        saturated = 0
        for n in (4, 10, 30):
            for seed in range(50):
                rng = random.Random(seed)
                zs = [rng.gauss(0, 1) for _ in range(n)]
                d = RBL.internal_drift_from_z_scores(zs)
                assert d is not None
                if d >= 1.0:
                    saturated += 1
        assert saturated <= 10, (
            f"{saturated}/150 genuine N(0,1) samples saturated to drift=1.0 "
            "(B-099 regression: constant disguised as measurement)"
        )

    def test_extreme_input_still_saturates(self):
        assert RBL.internal_drift_from_z_scores([5.0] * 8) == 1.0

    def test_shifted_input_detected(self):
        rng = random.Random(7)
        zs = [rng.gauss(2, 1) for _ in range(12)]
        d = RBL.internal_drift_from_z_scores(zs)
        assert d is not None and d > 0.5

    def test_non_finite_values_are_dropped(self):
        # B-103: Python min/max comparison semantics silently clipped NaN
        # into the top bin, so NaN z-scores counted as extreme +3
        # observations — 6 benign values scored 0.0 but adding 3 NaNs drove
        # drift to 1.0, and [nan]*4 scored 1.0 instead of "indeterminate".
        nan = float("nan")
        benign = [0.1, -0.2, 0.3, -0.1, 0.05, -0.3]
        clean = RBL.internal_drift_from_z_scores(benign)
        polluted = RBL.internal_drift_from_z_scores(benign + [nan, nan, nan])
        assert polluted == clean, (
            "NaN z-scores must be dropped, not binned as extreme values"
        )
        assert RBL.internal_drift_from_z_scores([nan] * 4) is None, (
            "fewer than 4 FINITE values is indeterminate"
        )
        assert RBL.internal_drift_from_z_scores(
            [float("inf"), float("-inf"), 0.1, 0.2]
        ) is None

    def test_rational_ln_matches_libm(self):
        # B-104: the kernel's rational ln must agree with libm to double
        # precision over the ratio range PSI actually feeds it.
        import math
        from fractions import Fraction

        for num, den in [(1, 100), (1, 7), (999, 1000), (1, 1), (3, 2),
                         (7, 1), (1000, 1), (1, 10**6), (10**6, 1)]:
            x = Fraction(num, den)
            assert abs(float(RBL._ln_fraction(x)) - math.log(x)) < 1e-14

    def test_bitforbit_golden_values(self):
        # B-104: the kernel is pure integer/rational arithmetic over frozen
        # constants, so these exact outputs pin cross-platform determinism —
        # any last-bit difference here means libm re-entered the sealed path.
        golden = [0.5, -0.3, 1.2, 0.1, -0.9, 2.1]
        d = RBL.internal_drift_from_z_scores(golden)
        assert d == RBL.internal_drift_from_z_scores(list(golden))
        assert d == 0.0
        d5 = RBL.internal_drift_from_z_scores([5.0] * 8)
        assert d5 == 1.0

    def test_large_n_clamps_bins_and_stays_covered(self):
        # k clamps at 12, so the frozen tables and chi2 constants always
        # cover the request — no runtime fallback path exists.
        import random
        rng = random.Random(5)
        zs = [rng.gauss(0, 1) for _ in range(5000)]
        d = RBL.internal_drift_from_z_scores(zs)
        assert d is not None and 0.0 <= d < 1.0

    def test_deterministic_and_order_invariant(self):
        rng = random.Random(3)
        zs = [rng.gauss(0.5, 1) for _ in range(16)]
        d1 = RBL.internal_drift_from_z_scores(zs)
        d2 = RBL.internal_drift_from_z_scores(list(zs))
        shuffled = list(zs)
        random.Random(99).shuffle(shuffled)
        d3 = RBL.internal_drift_from_z_scores(shuffled)
        assert d1 == d2 == d3


class TestDriftDetailsAndProvenance:
    def test_details_expose_raw_psi(self):
        # B-110: raw PSI was unrecoverable from any output.
        import random
        rng = random.Random(3)
        zs = [rng.gauss(0, 1) for _ in range(16)]
        d = RBL.internal_drift_details(zs)
        assert d is not None
        assert set(d) == {"drift", "raw_psi", "null_95", "n_finite",
                          "n_dropped_nonfinite", "bins"}
        assert d["drift"] == RBL.internal_drift_from_z_scores(zs)
        assert d["n_finite"] == 16 and d["n_dropped_nonfinite"] == 0
        assert d["raw_psi"] >= 0.0

    def test_details_indeterminate_matches_scalar_contract(self):
        assert RBL.internal_drift_details([0.1, 0.2]) is None

    def test_run_full_returns_drift_provenance(self):
        from vigia.core.ebs_v1 import SignalOutput
        from vigia.pipeline.pipeline import VigiaPipeline

        pipeline = VigiaPipeline()
        signals = [
            SignalOutput(tool_name=f"T{i}", value=0.5, z_score=z, confidence=0.9)
            for i, z in enumerate([0.4, -0.2, 1.1, 0.3, -0.5])
        ]
        result = pipeline.run_full(signals, drift_score=0.7)
        prov = result["drift_provenance"]
        assert prov["source"] == "internal_h27"
        assert prov["requested_external"] == 0.7
        assert prov["applied"] == result["bundle"].system_state.drift_score
        assert "raw_psi" in prov and "null_95" in prov

    def test_run_full_provenance_external_fallback(self):
        from vigia.core.ebs_v1 import SignalOutput
        from vigia.pipeline.pipeline import VigiaPipeline

        pipeline = VigiaPipeline()
        signals = [
            SignalOutput(tool_name="T0", value=0.5, z_score=0.4, confidence=0.9),
            SignalOutput(tool_name="T1", value=0.5, z_score=-0.2, confidence=0.9),
        ]
        result = pipeline.run_full(signals, drift_score=0.25)
        prov = result["drift_provenance"]
        assert prov["source"] == "external_fallback"
        assert prov["reason"] == "indeterminate_below_4_finite_signals"
        assert prov["applied"] == 0.25


class TestPipelineIntegration:
    @staticmethod
    def _sealed_drift(result):
        bundle = json.loads(result["bundle_json"])
        return bundle["system_state"]["drift_score"]

    @staticmethod
    def _signals(z_scores):
        return [
            {"tool_name": f"T{i}", "value": 0.5, "z_score": z, "confidence": 0.9}
            for i, z in enumerate(z_scores)
        ]

    def test_benign_signals_no_longer_seal_drift_one(self):
        from vigia.pipeline.pipeline import run_vigia

        rng = random.Random(11)
        zs = [rng.gauss(0, 1) for _ in range(8)]
        result = run_vigia(self._signals(zs), drift_score=0.0)
        assert self._sealed_drift(result) < 1.0, (
            "benign z-scores sealed drift=1.0 (B-099 regression)"
        )

    def test_below_gate_falls_back_to_external_drift(self):
        from vigia.pipeline.pipeline import run_vigia

        result = run_vigia(self._signals([0.1, -0.2, 0.3]), drift_score=0.2)
        assert self._sealed_drift(result) == pytest.approx(0.2), (
            "with n<4 the documented fallback is the external drift"
        )

    def test_extreme_signals_still_seal_drift_one(self):
        from vigia.pipeline.pipeline import run_vigia

        result = run_vigia(self._signals([5.0] * 8), drift_score=0.0)
        assert self._sealed_drift(result) == 1.0, (
            "anti-evasion lost: extreme z-scores must still max out drift"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
