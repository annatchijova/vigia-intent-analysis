"""
CAIE independent_sources materiality fix -- cognitive flood turned out to
have a scoring-consequential twin.

The original hypothesis was purely human-factors: does padding a case with
many low-value artifacts make it LOOK more corroborated to a human reader
without moving the math? It does (see test_caie_narrative_priority.py's
sibling investigation), but checking it exposed a second, more serious bug
in the same mechanism: independent_sources = len(group_scores) counts every
distinct (source_tool, evidence_type) GROUP, with zero regard for how much
that group actually contributed. _MIN_INDEPENDENT_SOURCES=3 gates a 20%
confidence_penalty meant to signal "resting on fewer than 3 corroborating
sources" -- but "source" was defined as "a label", not "evidence", so it is
gameable: pad with cheap, distinct-labeled, near-worthless artifacts to
cross the count threshold and waive the penalty entirely.

Confirmed empirically before this fix: 2 solid artifacts (raw_score=0.8,
low-spoofability evidence_type) score 0.3083 with the penalty correctly
applied. Adding 3 trivial-but-distinct-group artifacts (raw_score=0.02,
high-spoofability evidence_type) pushes independent_sources from 2 to 5,
waives the penalty, and raises the score to 0.3879 (+26%) -- from evidence
that, standing alone, would barely register (each padding artifact's own
group_score is on the order of 1e-3 to 1e-2).

Fix: independent_sources now only counts groups whose own group_score
clears _SOURCE_MATERIALITY_FLOOR (0.05) -- chosen because it sits cleanly
between padding-level group scores (~0.0003-0.02 in the reproduction) and
genuinely weak-but-real single-artifact scores (~0.1-0.25), so legitimately
weak corroborating evidence -- the whole point of allowing 3 weak sources
to combine -- is not swept up in the fix. The raw, unweighted group count
is preserved under a new field, source_groups_total, so no information is
lost, only mislabeled. Low-scoring groups still contribute their small,
honest amount to the fused composite_score -- they are excluded only from
counting toward the corroboration-penalty gate.
"""

from __future__ import annotations

from vigia.tools.caie import Artifact, CrossArtifactIncongruenceEngine

_ACQ = {
    "acquisition_tool": "test_harness",
    "acquisition_hash": "sha256:0000000000000000",
    "acquisition_timestamp": "2026-01-01T00:00:00Z",
    "examiner_id": "vigia_test",
    "write_blocker_used": True,
}


def _solid_pair() -> list[Artifact]:
    return [
        Artifact(
            source_tool=f"tool{i}", evidence_type="memory_process", raw_score=0.8,
            description=f"finding {i}", metadata=dict(_ACQ),
            timestamp=f"2026-01-01T10:0{i}:00Z",
        )
        for i in range(2)
    ]


def _padding_triplet() -> list[Artifact]:
    return [
        Artifact(
            source_tool=f"noise{i}", evidence_type="ip_geolocation", raw_score=0.02,
            description=f"trivial noise {i}", metadata=dict(_ACQ),
            timestamp=f"2026-01-01T11:{i:02d}:00Z",
        )
        for i in range(3)
    ]


class TestPaddingCannotWaiveTheConfidencePenalty:
    def test_penalty_still_applies_after_padding_to_five_groups(self):
        solo = CrossArtifactIncongruenceEngine()
        solo.reset()
        for a in _solid_pair():
            solo.add_artifact(a)
        solo_result = solo.evaluate()

        padded = CrossArtifactIncongruenceEngine()
        padded.reset()
        for a in _solid_pair():
            padded.add_artifact(a)
        for a in _padding_triplet():
            padded.add_artifact(a)
        padded_result = padded.evaluate()

        assert solo_result["confidence_penalty_applied"] is True
        assert padded_result["confidence_penalty_applied"] is True, (
            "5 distinct-labeled groups escaped the low-source penalty even "
            "though only 2 of them are materially independent"
        )
        assert padded_result["independent_sources"] == 2
        assert padded_result["source_groups_total"] == 5

    def test_padding_does_not_meaningfully_move_the_composite_score(self):
        solo = CrossArtifactIncongruenceEngine()
        solo.reset()
        for a in _solid_pair():
            solo.add_artifact(a)
        solo_score = float(solo.evaluate()["probabilistic_score"])

        padded = CrossArtifactIncongruenceEngine()
        padded.reset()
        for a in _solid_pair():
            padded.add_artifact(a)
        for a in _padding_triplet():
            padded.add_artifact(a)
        padded_score = float(padded.evaluate()["probabilistic_score"])

        # Padding still contributes its own small, honest amount via Noisy-OR
        # (it is real, if weak, evidence) -- but must not swing the score by
        # tens of percent the way escaping the penalty did before the fix.
        assert padded_score >= solo_score
        assert padded_score < solo_score * 1.05

    def test_source_groups_total_reflects_the_raw_unweighted_count(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for a in _solid_pair():
            engine.add_artifact(a)
        for a in _padding_triplet():
            engine.add_artifact(a)

        result = engine.evaluate()
        assert result["source_groups_total"] == 5
        assert result["independent_sources"] == 2


class TestLegitimateWeakSourcesAreNotOverCorrected:
    def test_three_weak_but_real_sources_still_avoid_the_penalty(self):
        """The materiality floor must not defeat the original purpose of
        _MIN_INDEPENDENT_SOURCES: letting several genuinely weak corroborating
        sources combine into a confident result without a penalty."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for i in range(3):
            engine.add_artifact(Artifact(
                source_tool=f"tool{i}", evidence_type="memory_process", raw_score=0.35,
                description=f"weak finding {i}", metadata=dict(_ACQ),
                timestamp=f"2026-01-01T10:0{i}:00Z",
            ))

        result = engine.evaluate()
        assert result["independent_sources"] == 3
        assert result["source_groups_total"] == 3
        assert result["confidence_penalty_applied"] is False


class TestNarrativeDiscloseMaterialityAlongsideRawCounts:
    def test_firstness_and_secondness_report_both_counts(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for a in _solid_pair():
            engine.add_artifact(a)
        for a in _padding_triplet():
            engine.add_artifact(a)

        result = engine.evaluate()
        firstness = result["peirce_chain"]["firstness"]
        secondness = result["peirce_chain"]["secondness"]

        assert "5 artifacts from 5 tools" in firstness
        assert "2 materially independent of 5 distinct source/type groups" in firstness
        assert "2 materially independent" in secondness
