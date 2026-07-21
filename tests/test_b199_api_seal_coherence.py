"""Regression contract for the standalone scorer / EBS API boundary.

The public API must not return a direct forensic verdict while attaching the
seal of a second, independently-derived pipeline decision.  The standalone
scorer's intent score is not a calibrated EBS fabrication-risk posterior, so
the EBS envelope may seal the analysis but must abstain from an EBS decision.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from forensics.verify_ebs_v1 import verify_bundle
from vigia.core.bundle_builder import build_bundle


def _case() -> dict:
    return {
        "case_id": "B199-API-SEAL-COHERENCE",
        "artifacts": [{
            "artifact_id": "b199-a1",
            "evidence_type": "memory_process",
            "raw_score": 0.9,
            "prior_trust": 0.9,
            "provenance_chain": ["acquisition", "hash"],
            "source_tool": "fixture",
            "description": "fixture artifact",
            "timestamp": "2026-07-21T00:00:00Z",
        }],
    }


@pytest.mark.parametrize(
    ("raw_verdict", "score"),
    (("NOISE", 0.02), ("SUSPICION", 0.25), ("MALICE", 0.98)),
)
def test_standalone_bundle_seals_raw_analysis_without_inventing_ebs_risk(
    raw_verdict, score
):
    sealed = build_bundle(
        _case(),
        {
            "verdict": raw_verdict,
            "score": score,
            "confidence": 0.9,
            "reason": "controlled B199 fixture",
        },
    )

    verification = verify_bundle(sealed)

    assert verification.passed, verification.checks
    assert sealed["caie_analysis"]["verdict"] == raw_verdict
    assert sealed["caie_analysis"]["composite_score"] == score
    assert sealed["decision_trace"]["decision"] == "ABSTAIN"
    assert sealed["decision_trace"]["risk"] == 0.5
    assert (
        sealed["decision_trace"]["reason_code"]
        == "STANDALONE_SCORER_UNCALIBRATED_EBS_RISK"
    )


@pytest.mark.parametrize("wrapper", ("vigia_api", "vigia.vigia_api"))
def test_api_returns_the_same_forensic_verdict_its_bundle_preserves(
    wrapper, tmp_path, monkeypatch
):
    module = importlib.import_module(wrapper)
    # The wrapper intentionally supports a VIGIA_REPO override.  This
    # regression tests this checkout's verifier contract, not a caller's
    # separately configured repository location.
    monkeypatch.setattr(module, "REPO", Path(__file__).resolve().parents[1])
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps(_case()), encoding="utf-8")

    result = module._run_pipeline(case_path)

    assert result["verify"].startswith("PASS")
    assert result["sealed_forensic_verdict"] == result["verdict"]
    assert result["ebs_decision"] == "ABSTAIN"
    assert result["seal_scope"] == "DIRECT_SCORER_ANALYSIS_ONLY"


@pytest.mark.parametrize("wrapper", ("vigia_api", "vigia.vigia_api"))
def test_api_does_not_mislabel_an_unavailable_verifier_as_bundle_failure(
    wrapper, tmp_path, monkeypatch
):
    module = importlib.import_module(wrapper)
    monkeypatch.setattr(module, "REPO", tmp_path / "missing-configured-repository")
    case_path = tmp_path / "case.json"
    case_path.write_text(json.dumps(_case()), encoding="utf-8")

    result = module._run_pipeline(case_path)

    assert result["verify"].startswith("UNAVAILABLE —")
    assert "FAIL" not in result["verify"]
