"""
CAIE artifact REFINEMENT / subsumption — the generalization of the
duplicate-artifact idempotence fix (see tests/test_caie_duplicate_artifact_
idempotence.py) to near-duplicates, not just byte-identical ones.

Exact-duplicate rejection alone leaves a sibling gap: a tool that re-parses
the same evidence and emits a MORE DETAILED version of a finding ("Suspicious
process" -> "Suspicious process" + pid + sha256) is not a byte-identical
resubmission, so it sailed straight past the exact-match check and got
counted as a second independent artifact -- inflating Noisy-OR fusion by
the same mechanism as the original bug, just triggered by refinement instead
of verbatim duplication. Empirically: a vague finding alone and the same
finding "duplicated + refined" (vague, then a refined version with the same
timestamp) doubled composite_score from ~0.13 to ~0.24 before this fix.

Fix: add_artifact() now recognizes a REFINEMENT -- a new artifact whose
metadata is a superset of an already-accepted artifact's metadata for the
same event -- and replaces the stored artifact in place instead of adding a
second one. "Same event" requires source_tool, evidence_type, description,
provenance_chain, and (UTC-canonicalized) timestamp to all match; only
metadata and raw_score are allowed to differ. This is deliberately strict:
requiring an exact anchor (provenance_chain + timestamp) before collapsing
two artifacts is the conservative direction to fail in for a forensic tool
-- under-merging costs a little corroboration-count precision, over-merging
could silently drop a genuinely distinct anomaly (a real MFT-entry test in
this repo already relies on two same-shaped-but-different-timestamp
artifacts staying separate: tests/test_caie_mft_entry_guard.py).

The design choice to canonicalize the identity signature's *timestamp*
field (UTC-normalize, not byte-compare) rather than fuzzy-match arbitrary
metadata (case-fold, type-coerce) is deliberate: canonicalization is a pure
function (one instant -> one string), so equality built on top of it stays
a true equivalence relation (transitive). Fuzzy/similarity matching would
not be: A~B and B~C does not generally imply A~C for a distance threshold.
"""

from __future__ import annotations

from vigia.tools.caie import (
    Artifact,
    CrossArtifactIncongruenceEngine,
    _canonical_timestamp,
)

_ACQ = {
    "acquisition_tool": "test_harness",
    "acquisition_hash": "sha256:0000000000000000",
    "acquisition_timestamp": "2026-01-01T00:00:00Z",
    "examiner_id": "vigia_test",
    "write_blocker_used": True,
}
_TS = "2026-01-01T12:00:00Z"


def _vague() -> Artifact:
    return Artifact(
        source_tool="volatility", evidence_type="memory_process", raw_score=0.60,
        description="Suspicious process", metadata=dict(_ACQ), timestamp=_TS,
    )


def _refined(raw_score: float = 0.60) -> Artifact:
    return Artifact(
        source_tool="volatility", evidence_type="memory_process", raw_score=raw_score,
        description="Suspicious process",
        metadata={**_ACQ, "pid": 4812, "sha256": "deadbeef" * 8},
        timestamp=_TS,
    )


class TestRefinementSupersedesVagueArtifact:
    def test_refined_version_replaces_vague_one(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()

        assert engine.add_artifact(_vague()) is True
        assert engine.add_artifact(_refined()) is True

        assert len(engine._artifacts) == 1
        assert sorted(engine._artifacts[0].metadata.keys()) == sorted(
            {**_ACQ, "pid": 4812, "sha256": "deadbeef" * 8}.keys()
        )

    def test_score_matches_a_single_refined_artifact_not_double_counted(self):
        solo = CrossArtifactIncongruenceEngine()
        solo.reset()
        solo.add_artifact(_refined())
        solo_result = solo.evaluate()

        sequence = CrossArtifactIncongruenceEngine()
        sequence.reset()
        sequence.add_artifact(_vague())
        sequence.add_artifact(_refined())
        sequence_result = sequence.evaluate()

        assert sequence_result["probabilistic_score"] == solo_result["probabilistic_score"]
        assert sequence_result["verdict"] == solo_result["verdict"]

    def test_refinement_order_independence(self):
        """vague-then-refined and refined-then-vague must converge to the
        same final state -- a real algebraic property (confluence), not
        just "doesn't crash."""
        vague_first = CrossArtifactIncongruenceEngine()
        vague_first.reset()
        vague_first.add_artifact(_vague())
        vague_first.add_artifact(_refined())
        r1 = vague_first.evaluate()

        refined_first = CrossArtifactIncongruenceEngine()
        refined_first.reset()
        refined_first.add_artifact(_refined())
        refined_first.add_artifact(_vague())
        r2 = refined_first.evaluate()

        assert len(vague_first._artifacts) == len(refined_first._artifacts) == 1
        assert r1["probabilistic_score"] == r2["probabilistic_score"]
        assert (
            vague_first._artifacts[0].metadata.keys()
            == refined_first._artifacts[0].metadata.keys()
        )

    def test_refinement_never_decreases_raw_score(self):
        """A more detailed report with a LOWER raw_score than the vague one
        it replaces must not make the retained artifact look less
        confident."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        vague_high_score = Artifact(
            source_tool="shimcache", evidence_type="file_metadata", raw_score=0.70,
            description="Executable with exec flag", metadata=dict(_ACQ), timestamp=_TS,
        )
        refined_lower_score = Artifact(
            source_tool="shimcache", evidence_type="file_metadata", raw_score=0.40,
            description="Executable with exec flag",
            metadata={**_ACQ, "sha256": "cafebabe" * 8}, timestamp=_TS,
        )

        engine.add_artifact(vague_high_score)
        engine.add_artifact(refined_lower_score)

        assert len(engine._artifacts) == 1
        assert engine._artifacts[0].raw_score == vague_high_score.raw_score

    def test_redundant_subset_resubmission_is_rejected(self):
        """The mirror case: a new artifact carrying LESS metadata than one
        already stored for the same event adds no information and must be
        rejected outright, not appended."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        engine.add_artifact(_refined())

        assert engine.add_artifact(_vague()) is False
        assert len(engine._artifacts) == 1
        assert "pid" in engine._artifacts[0].metadata


class TestRefinementRequiresAMatchingIdentityAnchor:
    """Metadata-superset alone is not enough: without a matching timestamp
    and provenance_chain, two artifacts must NOT be collapsed, even if one
    artifact's metadata happens to be a superset of the other's."""

    def test_different_timestamp_blocks_collapse(self):
        """Regression: two MFT records that are both missing
        mft_entry_number share source_tool/evidence_type/description and
        both have metadata={} (trivially a mutual "subset"), but represent
        two distinct events. Different timestamps must keep them separate."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        a = Artifact(
            source_tool="mft", evidence_type="mft_entry", raw_score=0.5,
            description="mft", metadata={}, provenance_chain=["sha256:m0"],
            timestamp="2026-01-01T00:00:00Z",
        )
        b = Artifact(
            source_tool="mft", evidence_type="mft_entry", raw_score=0.5,
            description="mft", metadata={}, provenance_chain=["sha256:m1"],
            timestamp="2026-01-02T00:00:00Z",
        )

        assert engine.add_artifact(a) is True
        assert engine.add_artifact(b) is True
        assert len(engine._artifacts) == 2

    def test_different_provenance_chain_blocks_collapse(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        a = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata=dict(_ACQ),
            provenance_chain=["sha256:aaa"], timestamp=_TS,
        )
        b = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata={**_ACQ, "pid": 4812},
            provenance_chain=["sha256:bbb"], timestamp=_TS,
        )

        assert engine.add_artifact(a) is True
        assert engine.add_artifact(b) is True
        assert len(engine._artifacts) == 2

    def test_incomparable_metadata_with_matching_anchor_stays_independent(self):
        """Same timestamp/provenance_chain, but genuinely conflicting
        metadata (pid=100 vs pid=200 -- two different processes): must stay
        two artifacts, neither a subset of the other."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        a = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata={**_ACQ, "pid": 100},
            timestamp=_TS,
        )
        b = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata={**_ACQ, "pid": 200},
            timestamp=_TS,
        )

        assert engine.add_artifact(a) is True
        assert engine.add_artifact(b) is True
        assert len(engine._artifacts) == 2


class TestTimestampCanonicalization:
    """_canonical_timestamp: equivalent instants in different UTC-offset
    representations must produce the same canonical form, and the function
    must degrade gracefully (never raise) on unparseable input."""

    def test_equivalent_instants_different_offsets_canonicalize_equal(self):
        assert _canonical_timestamp("2025-01-01T12:00:00Z") == _canonical_timestamp(
            "2025-01-01T09:00:00-03:00"
        )

    def test_genuinely_different_instants_do_not_collapse(self):
        assert _canonical_timestamp("2025-01-01T12:00:00Z") != _canonical_timestamp(
            "2025-01-01T12:00:01Z"
        )

    def test_unparseable_timestamp_falls_back_to_raw_string_without_raising(self):
        assert _canonical_timestamp("not-a-timestamp") == "not-a-timestamp"

    def test_refinement_recognized_across_equivalent_utc_offsets(self):
        """The identity anchor used for refinement/duplicate detection must
        also benefit from timestamp canonicalization, not just direct byte
        comparison."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        vague_z = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.60,
            description="Suspicious process", metadata=dict(_ACQ),
            timestamp="2026-01-01T12:00:00Z",
        )
        refined_offset = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.60,
            description="Suspicious process",
            metadata={**_ACQ, "pid": 4812},
            timestamp="2026-01-01T09:00:00-03:00",  # same instant, different offset
        )

        assert engine.add_artifact(vague_z) is True
        assert engine.add_artifact(refined_offset) is True
        assert len(engine._artifacts) == 1
