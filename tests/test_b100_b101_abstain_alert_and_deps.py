"""Regression tests for B-100 and B-101.

B-100: an ABSTAIN verdict (pipeline error, unanalyzed artifacts, insufficient
signals) closed its narrative with an assessed-looking "LOW (per-signal
magnitude)" alert. Five sealed corpus bundles paired
best_hypothesis=PIPELINE_ERROR with a LOW alert (the FALLO_OCULTO PARCIAL of
docs/AUDIT_NARRATIVAS_20260702.md). The alert must read INDETERMINATE and the
reconciliation line must not claim "hypothesis-level aggregation" when
nothing was aggregated.

B-101: dependencies declared in all three manifests (defusedxml, psutil) were
absent from the runtime environment for weeks with no startup signal — 10/200
corpus cases silently lost their XML/EVTX signal. vigia_agent.main() now
emits a loud, non-fatal stderr warning for declared-but-missing critical
runtime deps (degradation itself stays non-fatal by design, see
tests/test_tanda_a_triage.py).
"""
from __future__ import annotations

import sys

import pytest

from vigia_agent import (
    VIGIAAgent,
    _warn_missing_critical_deps,
    classify_agent_verdict,
    _signal_stats,
)


def _sig_dict(tool: str, z: float, conf: float = 0.8) -> dict:
    return {"tool": tool, "z_score": z, "confidence": conf,
            "value": abs(z), "metadata": {}}


def _final_alert_block(narrative: str) -> str:
    assert "--- FINAL ALERT LEVEL ---" in narrative
    return narrative.split("--- FINAL ALERT LEVEL ---")[1]


class TestB100AbstainAlert:
    def test_pipeline_error_presents_indeterminate_not_low(self):
        results = {
            "signals": [],
            "abduction": {"best_hypothesis": "PIPELINE_ERROR",
                          "is_conclusive": False, "narrative": "x"},
            "results": {},
        }
        assert classify_agent_verdict(
            results["abduction"], *_signal_stats(results)) == "ABSTAIN"

        agent = VIGIAAgent("T-B100", ".")
        narrative = agent._generate_narrative(results, "a" * 64)
        alert_block = _final_alert_block(narrative)
        assert not alert_block.strip().startswith("LOW"), (
            "an errored/unanalyzed case must not close with an "
            "assessed-looking LOW alert (B-100 regression)"
        )
        assert "INDETERMINATE" in alert_block
        assert "PIPELINE_ERROR" in alert_block
        assert "hypothesis-level aggregation" not in alert_block, (
            "the aggregation reconciliation wording is wrong for ABSTAIN"
        )

    def test_abstain_with_high_magnitude_is_scoped_not_unqualified(self):
        # Review widening of B-100: an ABSTAIN whose analyzed fragment shows
        # real magnitude must not seal an unqualified assessed-looking
        # MEDIUM/HIGH alert — the level is kept but explicitly scoped to
        # the analyzed portion, and the ABSTAIN reconciliation line fires.
        # (One primary signal in 2<z<=3 yields a MEDIUM alert while staying
        # ABSTAIN: z>3 triggers the L-036 override to INTENT_DETECTED and
        # three 2<z<=3 primaries trigger the SUSPICION_DETECTED escalation,
        # so those variants stop being ABSTAIN before the alert floor runs.)
        results = {
            "signals": [_sig_dict("MFT_ANALYZER", 2.5)],
            "abduction": {"best_hypothesis": "UNDETERMINED",
                          "is_conclusive": False, "narrative": "x"},
            "results": {},
        }
        assert classify_agent_verdict(
            results["abduction"], *_signal_stats(results)) == "ABSTAIN"

        agent = VIGIAAgent("T-B100-HIGH", ".")
        narrative = agent._generate_narrative(results, "a" * 64)
        alert_block = _final_alert_block(narrative)
        assert "ABSTAIN verdict" in alert_block, (
            "non-LOW magnitude on an ABSTAIN case must carry the ABSTAIN "
            "qualification (B-100 review gap)"
        )
        assert "ANALYZED portion only" in alert_block
        assert "Reconciliation: ABSTAIN verdict" in narrative

    def test_clean_analyzed_case_keeps_low_alert(self):
        # No behavior change for genuine NOISE: analyzed clean evidence
        # still presents the per-signal LOW magnitude level.
        results = {
            "signals": [
                _sig_dict("MFT_ANALYZER", 0.0),
                _sig_dict("EVENT_LOG", 0.1),
                _sig_dict("REGISTRY", -0.2),
            ],
            "abduction": {"best_hypothesis": "NO_TEMPORAL_ANOMALY_DETECTED",
                          "is_conclusive": True, "narrative": "x"},
            "results": {},
        }
        assert classify_agent_verdict(
            results["abduction"], *_signal_stats(results)) == "NOISE"

        agent = VIGIAAgent("T-B100-NOISE", ".")
        narrative = agent._generate_narrative(results, "a" * 64)
        assert _final_alert_block(narrative).strip().startswith("LOW")


class TestB101StartupDepCheck:
    def test_missing_dep_warns_on_stderr(self, monkeypatch, capsys):
        import importlib.util
        monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
        _warn_missing_critical_deps()
        err = capsys.readouterr().err
        assert "[VIGIA][StartupCheck] WARNING" in err
        assert "defusedxml" in err

    def test_present_deps_stay_silent(self, capsys):
        pytest.importorskip("defusedxml")
        _warn_missing_critical_deps()
        assert "[VIGIA][StartupCheck]" not in capsys.readouterr().err


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
