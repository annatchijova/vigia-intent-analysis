"""B-195 — scenario prose must not impersonate deterministic reasoning.

The JSON adapter accepts ``case.description`` as examiner-supplied scenario
context.  It can be useful to retain that context, but it is not an output of
the scorer and must never be emitted as the motor's abductive narrative.
"""

from __future__ import annotations

import json

from sift_orchestrator import SIFTOrchestrator
from vigia_agent import VIGIAAgent


_INJECTED_CLAIM = (
    "UNSUPPORTED-SCENARIO-CLAIM: exfiltration was completed and the operator "
    "was physically identified."
)


def _case() -> dict:
    return {
        "case_id": "B195-SCENARIO",
        "description": _INJECTED_CLAIM,
        "expected_verdict": "MALICE",
        "artifacts": [
            {
                "artifact_id": "memory-1",
                "evidence_type": "memory_process",
                "source_tool": "vol3",
                "raw_score": 0.8,
                "prior_trust": 0.9,
                "description": "Observed RWX region in an analyzed process.",
                "metadata": {},
            }
        ],
    }


def _resolved(_: SIFTOrchestrator, __: dict) -> dict:
    return {
        "hypothesis": "SUSPICION_DETECTED",
        "confidence": "3/4",
        "is_conclusive": True,
        "resolve_meta": {
            "selection_function": "test scorer",
            "motor_verdict": "SUSPICION",
            "motor_score": "1/5",
            "motor_confidence": "3/4",
            "motor_reason": "Observed memory anomaly requires corroboration.",
        },
        "caie_summary": None,
        "darvo_summary": None,
    }


def _analyze(tmp_path, monkeypatch) -> dict:
    path = tmp_path / "case.json"
    path.write_text(json.dumps(_case()), encoding="utf-8")
    monkeypatch.setenv("VIGIA_EBS_RESOLVE", "motor")
    monkeypatch.setattr(SIFTOrchestrator, "_resolve_hypothesis", _resolved)
    return SIFTOrchestrator("B195-SCENARIO")._analyze_ebs_json(str(path))


def test_case_description_is_not_motor_reasoning(tmp_path, monkeypatch):
    result = _analyze(tmp_path, monkeypatch)
    abduction = result["abduction"]

    assert _INJECTED_CLAIM not in abduction["narrative"]
    assert "Observed memory anomaly requires corroboration." in abduction["narrative"]
    assert abduction["scenario_context"] == _INJECTED_CLAIM
    assert abduction["scenario_context_provenance"] == "case_description_unverified"


def test_agent_labels_retained_scenario_context_as_unverified(tmp_path, monkeypatch):
    result = _analyze(tmp_path, monkeypatch)
    report = VIGIAAgent("B195-SCENARIO", ".")._generate_narrative(
        result, "a" * 64
    )

    motor_section = report.split("--- CASE CONTEXT", 1)[0]
    assert _INJECTED_CLAIM not in motor_section
    assert "Razonamiento del motor abductivo:" in motor_section
    assert "Observed memory anomaly requires corroboration." in motor_section
    assert "--- CASE CONTEXT (UNVERIFIED INPUT — NOT ANALYTICAL EVIDENCE) ---" in report
    assert _INJECTED_CLAIM in report
