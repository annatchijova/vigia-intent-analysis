"""
B-218: RiskBoundedDecisionLayer.decide() always sealed epsilon_used as
self._eps_accept regardless of verdict, so a REJECT decided by
epsilon_reject recorded the wrong threshold on the DecisionTrace. Separately
and more severely, VigiaPipeline.run_full() derived BOTH
SystemState.epsilon_accept and SystemState.epsilon_reject from that single
decision_trace.epsilon_used field, so the sealed bundle collapsed two
possibly-distinct policy thresholds into one, misrepresenting whichever one
the verdict didn't use.

Confirmed dormant under the default configuration before this fix:
VigiaPipeline(adaptive_policy=True) (the default) constructs a
SelfAdaptiveRiskPolicy with epsilon_init=policy_spec.epsilon_accept alone,
which sets both self.epsilon_accept and self.epsilon_reject to that same
value at construction time -- before update_from_window() even runs. So the
bug only bites when a PolicySpec sets distinct epsilon_accept/epsilon_reject
AND adaptive_policy=False (bypassing that collapse). This test locks in both
the previously-broken asymmetric case and the always-worked symmetric
default, so neither regresses.

Fix: RiskBoundedDecisionLayer.decide() now seals epsilon_used as
eps_reject for a REJECT verdict, eps_accept otherwise (ABSTAIN keeps
eps_accept as a reference value -- neither threshold decided, and
abstain_reason already carries both real values in its text).
VigiaPipeline.run_full() now seals epsilon_accept/epsilon_reject directly
from the adaptive policy or risk layer (same pattern already used for
lambda_drift/gamma_stability just above it), not derived from the trace's
single epsilon_used field.
"""

from __future__ import annotations

from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer


class TestDecisionTraceSealsTheDecidingThreshold:
    def test_reject_seals_epsilon_reject(self):
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.70)
        assert trace.decision == "REJECT"
        assert trace.epsilon_used == 0.40

    def test_accept_seals_epsilon_accept(self):
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.01)
        assert trace.decision == "ACCEPT"
        assert trace.epsilon_used == 0.05

    def test_abstain_keeps_epsilon_accept_as_reference(self):
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
        trace = layer.decide(posterior=0.30)
        assert trace.decision == "ABSTAIN"
        assert trace.epsilon_used == 0.05

    def test_symmetric_epsilons_unaffected(self):
        """Sanity: the common case (both epsilons equal) must be unchanged."""
        layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.05)
        for posterior in (0.01, 0.5, 0.99):
            trace = layer.decide(posterior=posterior)
            assert trace.epsilon_used == 0.05


class TestPipelineSealsBothThresholdsIndependently:
    def _run_full_with_policy(self, epsilon_accept, epsilon_reject, adaptive_policy):
        from vigia.core.ebs_v1 import PolicySpec, SignalOutput
        from vigia.pipeline.pipeline import VigiaPipeline

        policy = PolicySpec(epsilon_accept=epsilon_accept, epsilon_reject=epsilon_reject)
        pipeline = VigiaPipeline(policy=policy, adaptive_policy=adaptive_policy)
        signals = [
            SignalOutput(tool_name=f"T{i}", value=0.9, z_score=4.0, confidence=0.95)
            for i in range(5)
        ]
        pipeline.run_full(signals, drift_score=0.0)
        return pipeline.last_bundle.system_state

    def test_asymmetric_policy_without_adaptive_seals_both_true_values(self):
        ss = self._run_full_with_policy(
            epsilon_accept=0.05, epsilon_reject=0.40, adaptive_policy=False
        )
        assert ss.epsilon_accept == 0.05
        assert ss.epsilon_reject == 0.40

    def test_default_adaptive_policy_seals_equal_thresholds_unchanged(self):
        """The common, default path: adaptive_policy collapses both epsilons
        to the same value at construction, independent of this fix -- must
        stay unchanged (regression guard on the non-buggy path)."""
        ss = self._run_full_with_policy(
            epsilon_accept=0.05, epsilon_reject=0.40, adaptive_policy=True
        )
        assert ss.epsilon_accept == ss.epsilon_reject == 0.05
