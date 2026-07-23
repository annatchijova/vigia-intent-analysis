"""B-123/B-124 — characterization tests for the orphaned CCS producers.

AdversarialSilenceDetector and HypothesisLineageTracker had ZERO tests
(verified 2026-07-23 excavation: no import outside their own modules; the
CCS coupling lives only in causal_closure.py docstrings). These tests pin
CURRENT behavior — exact Fraction values probed before writing — so any
future wiring (B-123 roadmap) has a characterized base to diff against.
They assert what the code DOES, not what it should do.
"""
from __future__ import annotations

from fractions import Fraction

from vigia.abduction.hypothesis_lineage import HypothesisLineageTracker
from vigia.patterns.adversarial_silence import AdversarialSilenceDetector

import pytest


class TestAdversarialSilenceCharacterization:
    def test_empty_detector_yields_zero_scores_not_crash(self) -> None:
        result = AdversarialSilenceDetector().analyze()
        assert result.silence_score == Fraction(0)
        assert result.selectivity_score == Fraction(0)
        assert result.fabrication_likelihood == Fraction(0)

    def test_windows_process_execution_missing_prefetch_exact_values(self) -> None:
        # Canonical scenario: process executed, prefetch (hard to erase)
        # confirmed absent. Values probed 2026-07-23 — exact Fractions.
        det = AdversarialSilenceDetector("windows")
        det.register_primary_action("process_execution")
        det.register_confirmed_absent("prefetch_entry")
        result = det.analyze()
        assert result.silence_score == Fraction(9, 32)
        assert result.selectivity_score == Fraction(1, 3)
        assert result.erasure_sophistication == Fraction(4, 5)
        assert result.fabrication_likelihood == Fraction(487, 1200)
        # El CCS consumiría 1 - fabrication_likelihood — debe caer en [0,1]
        assert Fraction(0) <= 1 - result.fabrication_likelihood <= Fraction(1)

    def test_unknown_action_contributes_nothing(self) -> None:
        det = AdversarialSilenceDetector("windows")
        det.register_primary_action("acción_inexistente_en_kb")
        det.register_confirmed_absent("prefetch_entry")
        result = det.analyze()
        assert result.fabrication_likelihood == Fraction(0)

    def test_audit_hash_deterministic_across_instances(self) -> None:
        def _run():
            det = AdversarialSilenceDetector("windows")
            det.register_primary_action("process_execution")
            det.register_confirmed_absent("prefetch_entry")
            return det.analyze().audit_hash
        assert _run() == _run()

    def test_all_scores_are_fractions(self) -> None:
        det = AdversarialSilenceDetector("windows")
        det.register_primary_action("process_execution")
        det.register_confirmed_absent("mft_entry")
        result = det.analyze()
        for value in (result.silence_score, result.selectivity_score,
                      result.erasure_sophistication, result.fabrication_likelihood):
            assert isinstance(value, Fraction), value


class TestHypothesisLineageCharacterization:
    @staticmethod
    def _tracker() -> HypothesisLineageTracker:
        t = HypothesisLineageTracker()
        t.record("h1", "Benigna", "NOISE", 1, Fraction(2), Fraction(0),
                 Fraction(2), frozenset({"s1"}), frozenset({"s2"}))
        t.record("h2", "Maliciosa", "MALICE", 2, Fraction(1), Fraction(0),
                 Fraction(1), frozenset({"s1", "s2"}), frozenset())
        t.record("h2", "Maliciosa", "MALICE", 3, Fraction(1), Fraction(0),
                 Fraction(1), frozenset({"s1", "s2"}), frozenset())
        return t

    def test_verdict_stability_is_winner_iterations_over_total(self) -> None:
        # Winner h2 present in 2 of 3 distinct iterations → 2/3 exact.
        report = self._tracker().finalize("h2")
        assert report.verdict_stability == Fraction(2, 3)
        assert isinstance(report.verdict_stability, Fraction)
        # This is the scalar the CCS would consume as abductive_parsimony.
        assert Fraction(0) <= report.verdict_stability <= Fraction(1)

    def test_finalize_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            HypothesisLineageTracker().finalize("h1")

    def test_finalize_unknown_winner_raises(self) -> None:
        with pytest.raises(ValueError):
            self._tracker().finalize("no_existe")

    def test_audit_hash_deterministic(self) -> None:
        assert (self._tracker().finalize("h2").audit_hash
                == self._tracker().finalize("h2").audit_hash)
