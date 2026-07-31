"""B-215 — graph_hash must be a case-specific integrity anchor, not a constant.

`run_full` never bootstrap-fits an EvidenceGraph, so it used to seal a constant
empty graph (nodes=[], edges=[]). graph_hash was therefore identical across
every case (94147b51...) — an integrity anchor anchoring nothing. Verified in
the bug report: OWL-NEXUS5 (22 signals), MAGNET-iOS (6), OWL-COMPLETE (30) all
shared one hash while decision_hash correctly differed.

Fix (anchor-only, Anna's architecture decision): seal a deterministic
per-signal descriptor for the integrity anchor WITHOUT feeding it into scoring
— graph_stability stays 1.0 (the honest no-graph default) and no sealed verdict
changes. bootstrap_rounds=0 marks the descriptor as unfitted.
"""
from __future__ import annotations

from vigia.core.ebs_v1 import SignalOutput
from vigia.pipeline.pipeline import VigiaPipeline


def _sigs(spec):
    return [SignalOutput(tool_name=t, value=v, z_score=z) for (t, v, z) in spec]


CASE_A = [("entropy", 0.9, 3.1), ("network", 0.5, 1.2), ("habit", 0.7, 2.0)]
CASE_B = [("entropy", 0.1, 0.2), ("metadata", 0.4, 0.9)]  # different content and size


class TestGraphHashCaseSpecific:
    def test_different_cases_get_different_graph_hash(self) -> None:
        ha = VigiaPipeline().run(_sigs(CASE_A)).integrity.graph_hash
        hb = VigiaPipeline().run(_sigs(CASE_B)).integrity.graph_hash
        assert ha and hb
        assert ha != hb  # red-first: the pre-fix constant graph_hash made these equal

    def test_same_case_is_deterministic_across_fresh_pipelines(self) -> None:
        h1 = VigiaPipeline().run(_sigs(CASE_A)).integrity.graph_hash
        h2 = VigiaPipeline().run(_sigs(CASE_A)).integrity.graph_hash
        assert h1 == h2  # a random signal_id in the anchor would break this

    def test_anchor_is_order_independent(self) -> None:
        h1 = VigiaPipeline().run(_sigs(CASE_A)).integrity.graph_hash
        h2 = VigiaPipeline().run(_sigs(list(reversed(CASE_A)))).integrity.graph_hash
        assert h1 == h2  # labels are sorted → same signal set, same anchor


class TestScoringUntouched:
    def test_graph_stability_sealed_stays_one(self) -> None:
        bundle = VigiaPipeline().run(_sigs(CASE_A))
        # The descriptor must NOT leak into the scoring path: graph_stability
        # is the honest no-graph default, sealed independently in decision_trace.
        assert bundle.decision_trace.graph_stability == 1.0

    def test_descriptor_marked_unfitted(self) -> None:
        bundle = VigiaPipeline().run(_sigs(CASE_A))
        assert bundle.evidence_graph.bootstrap_rounds == 0
        assert len(bundle.evidence_graph.nodes) == len(CASE_A)
        assert bundle.evidence_graph.edges == []
