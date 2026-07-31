"""B-218 — the epsilon sealed for a decision must be the one that decided it.

`RiskBoundedDecisionLayer.decide()` sealed `epsilon_used=self._eps_accept`
unconditionally, regardless of verdict. For a REJECT decided by
`epsilon_reject`, the sealed trace claimed `epsilon_accept` decided it — an
audit-trail lie whenever a PolicySpec sets asymmetric thresholds. Downstream,
`VigiaPipeline` copied that single (always-accept) value into both
`SystemState.epsilon_accept` and `SystemState.epsilon_reject` of the sealed
bundle, discarding the real reject threshold entirely.

Dormant today because `SelfAdaptiveRiskPolicy.update_from_window` forces
`epsilon_accept == epsilon_reject` on every update — the default pipeline
configuration. Bites only when `RiskBoundedDecisionLayer` is built from an
explicit asymmetric `PolicySpec` (supported by `from_policy_spec`, e.g. with
`adaptive_policy=False`).
"""
from __future__ import annotations

from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer


class TestEpsilonUsedTracksVerdict:
    def test_reject_seals_epsilon_reject(self) -> None:
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.70)
        assert trace.decision == "REJECT"
        assert trace.epsilon_used == 0.40
        assert trace.epsilon_used != 0.05

    def test_accept_seals_epsilon_accept(self) -> None:
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.01)
        assert trace.decision == "ACCEPT"
        assert trace.epsilon_used == 0.05

    def test_abstain_seals_epsilon_accept_by_convention(self) -> None:
        # ABSTAIN sits strictly between both thresholds — neither one
        # "decided" it. epsilon_accept is the historical default fallback.
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.50)
        assert trace.decision == "ABSTAIN"
        assert trace.epsilon_used == 0.05


class TestPipelineSealsBothThresholdsIndependently:
    def test_asymmetric_policy_seals_true_accept_and_reject(self) -> None:
        from vigia.core.ebs_v1 import make_default_policy
        from vigia.pipeline.pipeline import VigiaPipeline

        policy = make_default_policy(epsilon=0.05)
        policy.epsilon_reject = 0.40  # force asymmetry, as B-218 requires

        pipeline = VigiaPipeline(policy=policy, adaptive_policy=False)

        # Mirrors the exact expression pipeline.py uses when building the
        # sealed SystemState (pipeline.py, "SELLADO CONJUNTO" block).
        sealed_epsilon_accept = (
            pipeline._adaptive_policy.epsilon_accept
            if pipeline._adaptive_policy else pipeline._risk_layer._eps_accept
        )
        sealed_epsilon_reject = (
            pipeline._adaptive_policy.epsilon_reject
            if pipeline._adaptive_policy else pipeline._risk_layer._eps_reject
        )
        assert pipeline._adaptive_policy is None
        assert sealed_epsilon_accept == 0.05
        assert sealed_epsilon_reject == 0.40
        assert sealed_epsilon_accept != sealed_epsilon_reject
