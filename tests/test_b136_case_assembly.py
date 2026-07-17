"""
B-136 phase 3 — the case assembler incorporates tool-exposed caie_artifacts.

Phases 1-2 made the four document-forensics tools BUILD case-ready artifact
dicts under "caie_artifacts" in their results. This phase closes the loop:
ForensicAdapter.build_context() — the single point where both assemblers
(vigia/pipeline/pipeline.py and vigia/sift/sift_orchestrator.py) construct
the CAIE artifact list — now also absorbs caie_artifacts found in
raw_results, so the fractures finally reach the engine that both
assemblers actually run (cross_artifact_analysis).

Fail-closed contract: a malformed entry (missing keys, non-dict, unbounded
raw_score) is skipped, never raises, and never silently becomes a
different artifact. Custody metadata is NOT synthesized — an artifact
without acquisition metadata self-degrades inside CAIE (B-131 law), which
is the honest outcome.
"""

import pytest

from vigia.core.forensic_adapter import ForensicAdapter


def _tool_artifact(**over):
    base = {
        "source_tool": "vigia_adversarial_nlp",
        "evidence_type": "linguistic_forensics",
        "raw_score": 0.5,
        "description": "SDA_NR_INCOHERENT",
        "metadata": {"mcp": 3.0, "document_id": "doc-1"},
        "provenance_chain": ["doc-1"],
    }
    base.update(over)
    return base


class TestRawResultsAbsorption:
    def test_tool_caie_artifacts_reach_the_context(self):
        """Invariant: a tool result carrying caie_artifacts contributes them
        to context.caie_artifacts. Mutation caught: reverting build_context
        to signals-only (the artifact count drops)."""
        ctx = ForensicAdapter.build_context(
            [], raw_results={"adversarial_nlp": {"caie_artifacts": [_tool_artifact()]}}
        )
        assert len(ctx.caie_artifacts) == 1
        art = ctx.caie_artifacts[0]
        assert art.evidence_type == "linguistic_forensics"
        assert art.raw_score == 0.5
        assert art.provenance_chain == ["doc-1"]

    def test_multiple_tools_accumulate(self):
        ctx = ForensicAdapter.build_context([], raw_results={
            "nlp": {"caie_artifacts": [_tool_artifact()]},
            "temporal": {"caie_artifacts": [_tool_artifact(
                source_tool="vigia_temporal", evidence_type="temporal_fraud",
                raw_score=0.9, description="TEMPORAL_ANACHRONISM")]},
            "other_tool": {"status": "OK"},  # no caie_artifacts: ignored
        })
        assert {a.evidence_type for a in ctx.caie_artifacts} == {
            "linguistic_forensics", "temporal_fraud"}

    def test_empty_raw_results_keeps_previous_behavior(self):
        assert ForensicAdapter.build_context([], raw_results={}).caie_artifacts == []
        assert ForensicAdapter.build_context([]).caie_artifacts == []


class TestFailClosed:
    def test_malformed_entries_are_skipped_not_raised(self):
        """Hostile inputs: non-dict entries, missing keys, wrong container.
        None of them may raise or produce a phantom artifact."""
        ctx = ForensicAdapter.build_context([], raw_results={
            "bad1": {"caie_artifacts": ["not-a-dict", 42, None]},
            "bad2": {"caie_artifacts": [{"raw_score": 0.5}]},  # missing keys
            "bad3": {"caie_artifacts": "not-a-list"},
            "good": {"caie_artifacts": [_tool_artifact()]},
        })
        assert len(ctx.caie_artifacts) == 1

    def test_out_of_range_raw_score_is_clamped(self):
        """Bound everything: a tool bug (or tampered result) with raw_score
        outside [0,1] must not poison the composite formula."""
        ctx = ForensicAdapter.build_context([], raw_results={
            "t": {"caie_artifacts": [_tool_artifact(raw_score=7.3),
                                     _tool_artifact(raw_score=-2.0)]},
        })
        scores = sorted(a.raw_score for a in ctx.caie_artifacts)
        assert scores == [0.0, 1.0]

    def test_custody_metadata_is_never_synthesized(self):
        """B-131 law: the adapter must not invent acquisition metadata.
        The artifact keeps exactly the metadata the tool provided; honest
        degradation happens downstream inside CAIE."""
        ctx = ForensicAdapter.build_context(
            [], raw_results={"t": {"caie_artifacts": [_tool_artifact()]}})
        meta = ctx.caie_artifacts[0].metadata
        for forbidden in ("acquisition_tool", "write_blocker_used", "examiner_id"):
            assert forbidden not in meta


class TestOrchestratorPathIntegration:
    """The sift orchestrator already called build_context with
    raw_results=results (its engines' result dict) BEFORE phase 3, so the
    absorption path is live there with zero extra plumbing. These tests
    freeze that contract against the orchestrator's real calling shape."""

    def test_engine_results_dict_shape_is_absorbed(self):
        """An orchestrator-style results dict — engine name -> result dict,
        one of them exposing caie_artifacts — contributes its artifacts."""
        results = {
            "metabolic": {"verdict": "OK", "signals": []},
            "unified_forensic": {
                "document_id": "abc123",
                "unified_mcp": 2.4,
                "caie_artifacts": [_tool_artifact(
                    source_tool="vigia_temporal",
                    evidence_type="temporal_fraud",
                    raw_score=0.8,
                    description="TEMPORAL_ANACHRONISM")],
            },
            "caie": {"verdict": "NOISE", "composite_score": 0.1},
        }
        ctx = ForensicAdapter.build_context([], raw_results=results)
        assert [a.evidence_type for a in ctx.caie_artifacts] == ["temporal_fraud"]

    def test_caie_own_result_cannot_feed_back(self):
        """No self-ingestion loop: cross_artifact_analysis results carry
        verdict/composite/fractures, never caie_artifacts — and even a
        hostile result claiming that key with a bad shape is skipped."""
        results = {"caie": {"verdict": "MALICE", "composite_score": 0.9,
                            "fractures_detected": 3,
                            "caie_artifacts": [{"verdict": "MALICE"}]}}
        ctx = ForensicAdapter.build_context([], raw_results=results)
        assert ctx.caie_artifacts == []
