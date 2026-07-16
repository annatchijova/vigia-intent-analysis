"""
B-114 — add_from_tool_result() must pass through add_artifact() guardrails.

add_from_tool_result() built an Artifact and appended it directly to
self._artifacts, bypassing the two Kimi P0 guardrails that add_artifact()
enforces for every other caller:

1. _MAX_ARTIFACTS anti-flooding limit (DoS protection)
2. evidence_type whitelist (_VALID_EVIDENCE_TYPES from EVIDENCE_PROFILES)
   — an arbitrary evidence_type would enter without a defined
   spoofability weighting.

The bypass is structural: any MCP tool using the convenience wrapper
inherits the hole (vision_intent_audit was the only correct-signature
caller and happened to pass whitelisted types, so it was never exploited).

Fix: add_from_tool_result() delegates to add_artifact() and propagates its
boolean verdict. Side effect of delegation (intended): artifacts added via
the wrapper now also get temporal/network indexing, same as every other
artifact.

Note: the scorer (vigia_scorer.py) feeds CAIE via add_artifact() directly,
so this change does not touch the verdict path.
"""

import pytest

from vigia.tools.caie import (
    Artifact,
    CrossArtifactIncongruenceEngine,
    _MAX_ARTIFACTS,
    _VALID_EVIDENCE_TYPES,
)


def _make_engine_at_limit() -> CrossArtifactIncongruenceEngine:
    engine = CrossArtifactIncongruenceEngine()
    art = Artifact(
        source_tool="filler",
        evidence_type="log_entry",
        raw_score=0.1,
        description="filler artifact",
    )
    # Reach the cap through the private list (constructing 1000 deepcopies
    # via add_artifact works too but is pointlessly slow for a unit test).
    engine._artifacts = [art] * _MAX_ARTIFACTS
    return engine


class TestB114GuardrailDelegation:
    def test_flooding_rejected_at_limit(self):
        engine = _make_engine_at_limit()
        added = engine.add_from_tool_result(
            tool_name="flooder",
            result={"suspicion_score": 0.9, "verdict": "MALICE"},
            evidence_type="log_entry",
        )
        assert added is False, (
            "B-114: add_from_tool_result must honor _MAX_ARTIFACTS."
        )
        assert len(engine._artifacts) == _MAX_ARTIFACTS

    def test_non_whitelisted_evidence_type_rejected(self):
        engine = CrossArtifactIncongruenceEngine()
        added = engine.add_from_tool_result(
            tool_name="rogue_tool",
            result={"suspicion_score": 0.9},
            evidence_type="totally_made_up_type",
        )
        assert added is False, (
            "B-114: add_from_tool_result must honor the evidence_type "
            "whitelist — unknown types have no spoofability weighting."
        )
        assert engine._artifacts == []

    def test_whitelisted_addition_still_works(self):
        engine = CrossArtifactIncongruenceEngine()
        added = engine.add_from_tool_result(
            tool_name="vision_intent_audit",
            result={"visual_malice_score": 0.7, "verdict": "SUSPICION"},
            evidence_type="document_visual",
        )
        assert added is True
        assert len(engine._artifacts) == 1
        art = engine._artifacts[0]
        assert art.source_tool == "vision_intent_audit"
        assert art.evidence_type == "document_visual"
        assert float(art.raw_score) == pytest.approx(0.7)

    def test_digital_perfection_override_passes_whitelist(self):
        """The P3 evidence_type override to document_visual must survive
        delegation (document_visual is whitelisted)."""
        engine = CrossArtifactIncongruenceEngine()
        added = engine.add_from_tool_result(
            tool_name="vision_intent_audit",
            result={
                "visual_malice_score": 0.8,
                "digital_perfection_detected": True,
                "verdict": "MALICE",
            },
            evidence_type="log_entry",
        )
        assert added is True
        art = engine._artifacts[0]
        assert art.evidence_type == "document_visual"
        assert art.description.startswith("[DIGITAL_PERFECTION]")

    def test_delegated_artifacts_get_temporal_index(self):
        """Delegation side effect: wrapper artifacts are now indexed like
        every add_artifact() artifact (they were invisible to the TCV and
        NETWORK_VS_HOST rules before)."""
        engine = CrossArtifactIncongruenceEngine()
        engine.add_from_tool_result(
            tool_name="vision_intent_audit",
            result={"visual_malice_score": 0.7},
            evidence_type="document_visual",
        )
        assert len(engine._temporal_index) == 1

    def test_score_extraction_regression(self):
        """Highest known score key wins; unknown keys ignored."""
        engine = CrossArtifactIncongruenceEngine()
        engine.add_from_tool_result(
            tool_name="t",
            result={
                "suspicion_score": 0.3,
                "probability_evasion": 0.6,
                "not_a_score": 0.99,
            },
            evidence_type="log_entry",
        )
        assert float(engine._artifacts[0].raw_score) == pytest.approx(0.6)
