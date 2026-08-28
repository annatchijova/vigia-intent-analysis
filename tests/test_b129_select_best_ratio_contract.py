"""
B-129 Fase 2 — _select_best must honor its documented contract.

The docstring of vigia.core.peirceplanner_bounded._select_best states:
"Selecciona hipótesis con mejor ratio cobertura/costo". The pre-fix
implementation computed coverage * (1 - cost/max_cost) instead, which
assigns a score of exactly 0 to the maximum-cost hypothesis for ANY
coverage: H_MALICE (cost 4, the max among the adapter's three hypotheses)
could never be selected while any other hypothesis remained active.

Measured consequence (scripts/dryrun_b129_weight_calibration.py,
2026-08-27, 208 cases): the planner emitted 0 MALICE verdicts under every
weight strategy, against 113 scorer MALICE cases — an agreement ceiling of
~45%, below the Fase 2 target of 70%, unreachable by weight calibration
alone.

These tests are red against the pre-fix implementation (verified) and pin
the ratio contract plus the module's first behavioral guarantees.

The module has zero production callers (B-124 cluster; the only consumer
is the observation-only planner_adapter) — no sealed verdict changes.
"""
from __future__ import annotations

from fractions import Fraction

from vigia.core.peirceplanner_bounded import (
    EvidenceSignal,
    Hypothesis,
    HypothesisStatus,
    PlannerTerminationReason,
    _select_best,
    run_bounded_planner,
)
from vigia.core.planner_adapter import build_hypotheses


def _sig(sid: str, weight: Fraction) -> EvidenceSignal:
    return EvidenceSignal(signal_id=sid, description=sid, weight=weight)


def _hyp(hid: str, cost: Fraction, explains: list[str]) -> Hypothesis:
    return Hypothesis(
        hypothesis_id=hid,
        description=hid,
        ockham_cost=cost,
        verdict=hid,
        signals_explained=explains,
    )


class TestRatioContract:
    def test_max_cost_hypothesis_with_full_coverage_is_selectable(self):
        """RED pre-fix: the max-cost hypothesis scored exactly 0 and could
        never beat a zero-coverage cheap hypothesis (tie at 0 resolved by
        list order)."""
        signals = [_sig("s1", Fraction(9, 10)), _sig("s2", Fraction(8, 10))]
        cheap_no_cover = _hyp("H_BENIGN", Fraction(1), [])
        expensive_full = _hyp("H_MALICE", Fraction(4), ["s1", "s2"])
        best = _select_best([cheap_no_cover, expensive_full], signals)
        assert best is not None
        assert best.hypothesis_id == "H_MALICE"

    def test_score_is_coverage_over_cost(self):
        """Full-coverage cheap beats full-coverage expensive: 1/1 > 1/4."""
        signals = [_sig("s1", Fraction(1, 10))]
        benign = _hyp("H_BENIGN", Fraction(1), ["s1"])
        malice = _hyp("H_MALICE", Fraction(4), ["s1"])
        best = _select_best([malice, benign], signals)
        assert best.hypothesis_id == "H_BENIGN"

    def test_partial_coverage_ratio_ordering(self):
        """cov=1/2 at cost 2 (score 1/4) loses to cov=1 at cost 2 (1/2)."""
        signals = [_sig("s1", Fraction(1, 2)), _sig("s2", Fraction(1, 2))]
        half = _hyp("H_HALF", Fraction(2), ["s1"])
        full = _hyp("H_FULL", Fraction(2), ["s1", "s2"])
        best = _select_best([half, full], signals)
        assert best.hypothesis_id == "H_FULL"

    def test_non_positive_cost_scores_zero(self):
        """Degenerate cost <= 0 must not crash nor divide by zero; the
        well-formed hypothesis wins."""
        signals = [_sig("s1", Fraction(1, 2))]
        broken = _hyp("H_BROKEN", Fraction(0), ["s1"])
        sane = _hyp("H_SANE", Fraction(1), ["s1"])
        best = _select_best([broken, sane], signals)
        assert best.hypothesis_id == "H_SANE"

    def test_no_active_hypotheses_returns_none(self):
        signals = [_sig("s1", Fraction(1, 2))]
        h = _hyp("H_X", Fraction(1), ["s1"])
        h.status = HypothesisStatus.DISCARDED
        assert _select_best([h], signals) is None

    def test_all_zero_scores_tie_keeps_list_order(self):
        """With every score at 0, max() keeps the first-listed hypothesis —
        the adapter lists H_BENIGN first, so ties stay conservative."""
        signals = [_sig("s1", Fraction(9, 10))]
        benign = _hyp("H_BENIGN", Fraction(1), [])
        susp = _hyp("H_SUSPICION", Fraction(2), [])
        best = _select_best([benign, susp], signals)
        assert best.hypothesis_id == "H_BENIGN"


class TestPlannerEndToEnd:
    def test_high_anomaly_case_can_reach_malice(self):
        """RED pre-fix: with every signal above the SUSPICION threshold
        (weight > 1/2), only H_MALICE explains anything, yet the planner
        still returned H_BENIGN because H_MALICE scored 0."""
        signals = [
            _sig("s1", Fraction(9, 10)),
            _sig("s2", Fraction(85, 100)),
            _sig("s3", Fraction(8, 10)),
        ]
        result = run_bounded_planner(
            initial_hypotheses=build_hypotheses(signals),
            signals=signals,
        )
        assert result.winning_hypothesis is not None
        assert result.winning_hypothesis.hypothesis_id == "H_MALICE"
        assert result.termination_reason in (
            PlannerTerminationReason.SIGNAL_COVERAGE,
            PlannerTerminationReason.OCKHAM_CONVERGENCE,
        )

    def test_low_anomaly_case_stays_benign(self):
        """All signals at or below the BENIGN threshold: H_BENIGN has full
        coverage at the lowest cost and must win."""
        signals = [_sig("s1", Fraction(1, 10)), _sig("s2", Fraction(1, 5))]
        result = run_bounded_planner(
            initial_hypotheses=build_hypotheses(signals),
            signals=signals,
        )
        assert result.winning_hypothesis is not None
        assert result.winning_hypothesis.hypothesis_id == "H_BENIGN"

    def test_mid_anomaly_case_reaches_suspicion(self):
        """Signals in (1/5, 1/2]: H_SUSPICION covers all at cost 2 (score
        1/2) and beats H_MALICE (1/4) and H_BENIGN (0)."""
        signals = [_sig("s1", Fraction(2, 5)), _sig("s2", Fraction(1, 2))]
        result = run_bounded_planner(
            initial_hypotheses=build_hypotheses(signals),
            signals=signals,
        )
        assert result.winning_hypothesis is not None
        assert result.winning_hypothesis.hypothesis_id == "H_SUSPICION"

    def test_determinism_same_input_same_audit_hash(self):
        signals = [
            _sig("s1", Fraction(9, 10)),
            _sig("s2", Fraction(3, 10)),
            _sig("s3", Fraction(1, 10)),
        ]
        r1 = run_bounded_planner(build_hypotheses(signals), signals)
        r2 = run_bounded_planner(build_hypotheses(signals), signals)
        assert r1.audit_hash == r2.audit_hash
        assert (
            r1.winning_hypothesis.hypothesis_id
            == r2.winning_hypothesis.hypothesis_id
        )
