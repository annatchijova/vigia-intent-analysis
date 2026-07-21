"""B-162 — unmodeled structured legacy content must not seal a clean NOISE.

The test fixture deliberately carries an `id`, a mobile taxonomy name, and a
nested content record, but no pre-scored anomalies.  The generic adapter may
preserve and classify that shape; it must not treat the scenario's prose as a
score.  Until a source-specific extractor exists, a would-be NOISE is ABSTAIN.
"""
from __future__ import annotations

import copy

from vigia.pipeline.vigia_integration_bridge import normalize_case_schema
from vigia_scorer import _vigia_score


def _structured_legacy_case(expected_verdict: str = "SUSPICION") -> dict:
    return {
        "case_id": "B162-STRUCTURED-LEGACY",
        "expected_verdict": expected_verdict,
        "artifacts": [{
            "id": "MOBILE-CHAT-01",
            "type": "instant_message",
            "source": "mobile_chat_cache",
            "content": {
                "from": "owner",
                "to": "counterparty",
                "message": "content whose semantics no generic adapter models",
            },
            "metadata": {
                "significance": "Scenario annotation, never a score input",
            },
        }],
    }


def test_structured_legacy_content_keeps_its_identity_and_taxonomy():
    normalized = normalize_case_schema(_structured_legacy_case())
    artifact = normalized["artifacts"][0]

    assert artifact["artifact_id"] == "MOBILE-CHAT-01"
    assert artifact["evidence_type"] == "chat_message"


def test_unmodeled_structured_legacy_content_abstains_not_noise():
    normalized = normalize_case_schema(_structured_legacy_case())
    result = _vigia_score(normalized)

    assert result["verdict"] == "ABSTAIN", result
    failures = result.get("normalization_failures") or []
    assert failures == [{
        "artifact_id": "MOBILE-CHAT-01",
        "field": "content",
        "reason": "structured_content_without_semantic_extractor",
        "legacy_type": "instant_message",
    }]


def test_schema_degradation_is_blind_to_the_expected_label():
    suspicion = normalize_case_schema(_structured_legacy_case("SUSPICION"))
    malice = normalize_case_schema(_structured_legacy_case("MALICE"))

    assert copy.deepcopy(suspicion["artifacts"]) == malice["artifacts"]
