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

    def test_deterministic_and_order_invariant(self):
        rng = random.Random(3)
        zs = [rng.gauss(0.5, 1) for _ in range(16)]
        d1 = RBL.internal_drift_from_z_scores(zs)
        d2 = RBL.internal_drift_from_z_scores(list(zs))
        shuffled = list(zs)
        random.Random(99).shuffle(shuffled)
        d3 = RBL.internal_drift_from_z_scores(shuffled)
        assert d1 == d2 == d3


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
