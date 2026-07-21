"""B-163 — agent presentation must use the same normalized artifacts as scoring.

The fixture intentionally has a legacy ``id``, a mobile type, and nested
content. It must remain semantically unscored (ABSTAIN), but the agent's own
signals must not replace its preserved identifier and taxonomy with ``?`` and
``unknown``.
"""
from __future__ import annotations

import json
from fractions import Fraction

from sift_orchestrator import SIFTOrchestrator
from vigia.pipeline.vigia_integration_bridge import normalize_case_schema


def _legacy_mobile_case(expected_verdict: str) -> dict:
    return {
        "case_id": "B163-PROJECTION",
        "expected_verdict": expected_verdict,
        "artifacts": [{
            "id": "MOBILE-CHAT-02",
            "type": "instant_message",
            "source": "mobile_chat_cache",
            "content": {"message": "not a score input"},
            "metadata": {"significance": "scenario annotation only"},
        }],
    }


def _run(tmp_path, monkeypatch, expected_verdict: str) -> dict:
    monkeypatch.setenv("VIGIA_EBS_RESOLVE", "motor")
    path = tmp_path / f"{expected_verdict.lower()}.json"
    path.write_text(json.dumps(_legacy_mobile_case(expected_verdict)), encoding="utf-8")
    return SIFTOrchestrator("B163-PROJECTION")._analyze_ebs_json(str(path))


def test_agent_signals_project_normalized_legacy_identity_and_taxonomy(tmp_path, monkeypatch):
    result = _run(tmp_path, monkeypatch, "SUSPICION")
    normalized = normalize_case_schema(_legacy_mobile_case("SUSPICION"))["artifacts"][0]
    signal = result["signals"][0]

    assert result["abduction"]["best_hypothesis"] == "ABSTAIN_DETECTED"
    assert len(result["signals"]) == 1
    assert signal["artifact_id"] == normalized["artifact_id"]
    assert signal["evidence_type"] == normalized["evidence_type"]
    assert signal["source"] == normalized["source_tool"]
    # The EBS renderer's z-score is its ordinary raw-score × trust projection.
    # This is a presentation equivalence check, not permission to score nested
    # content or metadata.significance.
    assert signal["z_score"] == Fraction(str(normalized["raw_score"])) * Fraction(
        str(normalized["prior_trust"])
    )
    assert signal["confidence"] == Fraction(str(normalized["prior_trust"]))
    assert signal["description"] == normalized["description"][:200]


def test_agent_presentation_remains_blind_to_expected_label(tmp_path, monkeypatch):
    suspicion = _run(tmp_path, monkeypatch, "SUSPICION")
    malice = _run(tmp_path, monkeypatch, "MALICE")

    assert suspicion["signals"] == malice["signals"]
    assert suspicion["abduction"] == malice["abduction"]
