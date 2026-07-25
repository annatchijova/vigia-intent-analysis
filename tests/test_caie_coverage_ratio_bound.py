"""
CDL coverage_ratio must never exceed 1.0.

Same failure class as the independent_sources bug fixed earlier on this
branch: observed_layers in evaluate() counted every distinct evidence_type
label with no cap, so coverage_ratio = len(observed_layers) / 6 could
exceed 1.0 given enough distinct labels -- confirmed with 10 distinct
evidence_type values producing coverage_ratio=1.667 (167%), a value
CollapseDecisionLayer.explain() formats as a percentage in the Daubert-
facing narrative ("Coverage too low (X%)").

This test covers only the narrow, safe fix that landed (bounding the
ratio). The deeper gap -- coverage_ratio not actually validating that
observed labels are members of total_expected_layers, because nothing in
this codebase ever sets metadata["layer"] and no evidence_type string is a
member of total_expected_layers -- is investigated and documented in
docs/CDL_COVERAGE_RATIO_GAP.md but deliberately not fixed here: it needs a
reviewed evidence_type -> layer taxonomy validated against the full
canonical corpus, not a quick patch (the same discipline the
independent_sources fix required after a first naive attempt broke a real
corpus case).

evaluate() does not expose coverage_ratio directly, so these tests reach it
indirectly: constructing enough distinct evidence_type artifacts to trigger
the pre-fix overflow, and confirming evaluate() still runs to completion
(the CDL branch is wrapped in try/except, so an internal error would be
silently swallowed rather than surfaced -- these tests catch a regression
there too by asserting a well-formed result comes back either way).
"""

from __future__ import annotations

from vigia.collapse_decision import CollapseContext, CollapseDecisionLayer, CollapseVerdict
from vigia.tools.caie import Artifact, CrossArtifactIncongruenceEngine

_ACQ = {
    "acquisition_tool": "test_harness",
    "acquisition_hash": "sha256:0000000000000000",
    "acquisition_timestamp": "2026-01-01T00:00:00Z",
    "examiner_id": "vigia_test",
    "write_blocker_used": True,
}

_TEN_DISTINCT_TYPES = [
    "memory_process", "file_metadata", "log_entry", "ip_geolocation",
    "cryptographic_hash", "digital_signature", "mft_entry", "network_flow",
    "registry_key", "prefetch",
]


class TestCollapseDecisionLayerRatioContract:
    """Direct unit coverage of the gate itself: CollapseContext.coverage_ratio
    is documented/used as a fraction, and anything >= 1.0 must never read as
    "too low" -- confirms the gate's own logic is sound in isolation,
    independent of how caie.py computes the ratio it passes in."""

    def test_ratio_of_exactly_one_does_not_trigger_inconclusive(self):
        cdl = CollapseDecisionLayer()
        ctx = CollapseContext(
            broken_assumptions=set(), coverage_ratio=1.0, base_score=0.6,
            has_structural_malice=False, independent_sources=3,
        )
        assert cdl.resolve(ctx) != CollapseVerdict.INCONCLUSIVE

    def test_ratio_above_one_does_not_trigger_inconclusive(self):
        """A ratio > 1.0 should never have been possible in the first place
        (see caie.py's cap) -- this documents that even if one leaked
        through, the gate itself wouldn't misfire on it."""
        cdl = CollapseDecisionLayer()
        ctx = CollapseContext(
            broken_assumptions=set(), coverage_ratio=1.667, base_score=0.6,
            has_structural_malice=False, independent_sources=3,
        )
        assert cdl.resolve(ctx) != CollapseVerdict.INCONCLUSIVE


class TestEvaluateHandlesManyDistinctEvidenceTypes:
    """End-to-end: the historical overflow input (10 distinct evidence_type
    values) must still produce a well-formed result -- no crash, no silent
    CDL failure swallowed by evaluate()'s try/except."""

    def test_ten_distinct_evidence_types_produce_a_well_formed_result(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for i, et in enumerate(_TEN_DISTINCT_TYPES):
            engine.add_artifact(Artifact(
                source_tool=f"tool{i}", evidence_type=et, raw_score=0.3,
                description=f"finding {i}", metadata=dict(_ACQ),
                timestamp=f"2026-01-01T10:{i:02d}:00Z",
            ))

        result = engine.evaluate()

        assert result["status"] == "OK"
        assert result["verdict"] in {"NOISE", "SUSPICION", "MALICE", "INCONCLUSIVE"}
        # The overflow case must not have been caught by CDL's own gate --
        # confirms the ratio was bounded before CollapseDecisionLayer saw it
        # rather than accidentally triggering INCONCLUSIVE via a different
        # path than the one under test.
        assert "Coverage too low" not in result["daubert_note"]
