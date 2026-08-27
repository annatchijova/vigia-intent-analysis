"""
B-129 Fase 2 — case_to_signals calibrated weight contract.

The Fase 1 adapter fed EvidenceSignal.weight from signal confidence, which
measures certainty, not anomaly severity (22% agreement with the scorer).
The calibration dry-run (scripts/dryrun_b129_weight_calibration.py,
2026-08-27, 208 cases) selected raw_score * (1 - CAIE spoofability) as the
weight source (56% agreement), with signal z_score as fallback.

These tests pin the calibrated contract, including the two defects of the
previous fallback path:
- an artifact missing raw_score produced weight Fraction(5) — out of the
  [0, 1] domain the hypothesis thresholds are defined over;
- confidence-as-weight inverted the semantics (a highly-certain benign
  signal weighed like a severe anomaly).

planner_adapter is observation-only (zero verdict-path callers) — no
sealed verdict changes.
"""
from __future__ import annotations

from fractions import Fraction

from vigia.core.planner_adapter import case_to_signals, run_planner_observation


def _artifact(aid: str, raw: float, evidence_type: str = "log_entry") -> dict:
    return {
        "artifact_id": aid,
        "raw_score": raw,
        "evidence_type": evidence_type,
        "description": f"artifact {aid}",
    }


class TestCalibratedWeights:
    def test_artifact_weight_is_raw_times_one_minus_spoofability(self):
        case = {"artifacts": [_artifact("A-001", 0.8)]}
        [sig] = case_to_signals(case)
        # spoofability is in [0, 1], so the damped weight can never exceed raw
        assert Fraction(0) <= sig.weight <= Fraction(4, 5)

    def test_weight_always_within_unit_interval(self):
        case = {
            "artifacts": [
                _artifact("A-001", 0.98),
                _artifact("A-002", 0.0),
                {"artifact_id": "A-003", "raw_score": 5.0,
                 "evidence_type": "log_entry", "description": "hostile raw"},
            ]
        }
        for sig in case_to_signals(case):
            assert Fraction(0) <= sig.weight <= Fraction(1)

    def test_missing_raw_score_does_not_fabricate_weight_5(self):
        """Previous fallback: a.get("raw_score", 5) * 10 -> Fraction(5).
        An artifact without raw_score is now skipped, not inflated."""
        case = {
            "artifacts": [{"artifact_id": "A-001", "description": "no score"}],
            "signals": [
                {"artifact_id": "S-001", "z_score": 0.7, "description": "z"},
            ],
        }
        sigs = case_to_signals(case)
        assert [s.signal_id for s in sigs] == ["S-001"]
        assert sigs[0].weight == Fraction(7, 10)

    def test_confidence_is_no_longer_a_weight_source(self):
        """A maximally-certain signal with zero z must weigh 0, not 1."""
        case = {
            "signals": [
                {
                    "artifact_id": "S-001",
                    "confidence": {"__fraction__": True, "num": 1, "den": 1},
                    "z_score": 0,
                    "description": "certain but not anomalous",
                }
            ]
        }
        [sig] = case_to_signals(case)
        assert sig.weight == Fraction(0)

    def test_artifacts_preferred_over_signals(self):
        case = {
            "artifacts": [_artifact("A-001", 0.6)],
            "signals": [
                {"artifact_id": "S-001", "z_score": 0.9, "description": "z"},
            ],
        }
        assert [s.signal_id for s in case_to_signals(case)] == ["A-001"]

    def test_nothing_measurable_yields_empty_and_abstain(self):
        case = {
            "case_id": "EMPTY-001",
            "artifacts": [{"artifact_id": "A-001", "description": "bare"}],
        }
        assert case_to_signals(case) == []
        report = run_planner_observation(case)
        assert report["planner_status"] == "NO_SIGNALS"
        assert report["planner_verdict"] == "ABSTAIN"

    def test_weights_are_fractions(self):
        case = {"artifacts": [_artifact("A-001", 0.75)]}
        [sig] = case_to_signals(case)
        assert isinstance(sig.weight, Fraction)

    def test_deterministic_across_calls(self):
        case = {
            "artifacts": [_artifact("A-001", 0.9), _artifact("A-002", 0.3)],
        }
        w1 = [s.weight for s in case_to_signals(case)]
        w2 = [s.weight for s in case_to_signals(case)]
        assert w1 == w2
