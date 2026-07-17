"""
B-136 phase 2 — the four orphan CAIE injections become case-stream routing.

Kimi confirmed by induction that all four sites built a LOCAL
CrossArtifactIncongruenceEngine, added artifacts, and discarded it without
ever calling detect_fractures(): a structural no-op, with misleading success
logs (CAIE_ARTIFACT_INJECTED / ENTANGLEMENT_CAIE_INJECTED) and, in three of
the four, kwargs that raise TypeError against the real wrapper signature.

Option 1 contract (docs/PROPUESTA_B136_CAIE_WIRING_20260717.md): each tool
BUILDS case-ready artifact dicts and EXPOSES them in its own result under
"caie_artifacts"; the case assembler incorporates them into the case's
artifact stream, where the scorer consumes them with the B-136 profiles and
CONTEXTUAL role. No ephemeral engine, no false success logs.

Every artifact dict must satisfy the real guardrail (add_artifact accepts
it) and carry raw_score in [0, 1] — verdict.mcp is 1.0-5.0, so the original
raw_score=mcp would have poisoned the composite even if wired.
"""

from fractions import Fraction

import pytest

from vigia.tools.caie import Artifact, CrossArtifactIncongruenceEngine

_CASE_ARTIFACT_KEYS = {"source_tool", "evidence_type", "raw_score",
                       "description", "metadata", "provenance_chain"}


def _assert_case_ready(artifact: dict, expected_type: str) -> None:
    """Shared contract: the dict has the canonical case-artifact shape,
    raw_score is bounded, and the REAL guardrail path accepts it."""
    assert _CASE_ARTIFACT_KEYS <= set(artifact), (
        f"missing keys: {_CASE_ARTIFACT_KEYS - set(artifact)}"
    )
    assert artifact["evidence_type"] == expected_type
    assert 0.0 <= artifact["raw_score"] <= 1.0, (
        "B-136: raw_score must be normalized to [0,1] before it can feed "
        "raw x (1-spoofability) x weight x trust"
    )
    engine = CrossArtifactIncongruenceEngine()
    assert engine.add_artifact(Artifact(
        source_tool=artifact["source_tool"],
        evidence_type=artifact["evidence_type"],
        raw_score=artifact["raw_score"],
        description=artifact["description"],
        metadata=artifact["metadata"],
        provenance_chain=artifact["provenance_chain"],
    )) is True


class TestAdversarialNlpWiring:
    def _verdict(self, mcp=3.0, fracturas=("SDA_NR_INCOHERENT", "CLI_DRIFT")):
        from vigia.tools.adversarial_nlp import ForensicVerdict
        return ForensicVerdict(
            document_id="doc-b136", emitter_id="e1", emitter_type="JUDICIAL",
            language="es", sda_nr={}, cli={}, acp={}, roi={},
            mcp=mcp, mcp_breakdown={}, final_verdict="SOSPECHOSO",
            confidence=min(1.0, (mcp - 1.0) / 4.0),
            fracturas=list(fracturas), timestamp="2026-07-17T00:00:00Z",
        )

    def test_builds_one_case_ready_artifact_per_fracture(self):
        """Invariant: N fracturas -> N linguistic_forensics artifacts, each
        accepted by the real guardrail. Mutation caught: reviving the local
        engine (returns None) or passing raw mcp (1-5) as raw_score."""
        from vigia.tools.adversarial_nlp import VigiaAdversarialNLP
        tool = VigiaAdversarialNLP.__new__(VigiaAdversarialNLP)  # no engine init
        verdict = self._verdict()
        artifacts = tool._build_caie_fractures(verdict)
        assert len(artifacts) == 2
        for a in artifacts:
            _assert_case_ready(a, "linguistic_forensics")
            # raw_score is the canonical normalization, not raw mcp
            assert a["raw_score"] == pytest.approx(0.5)

    def test_no_fracturas_builds_nothing(self):
        from vigia.tools.adversarial_nlp import VigiaAdversarialNLP
        tool = VigiaAdversarialNLP.__new__(VigiaAdversarialNLP)
        assert tool._build_caie_fractures(self._verdict(fracturas=())) == []


class TestEntanglementWiring:
    def _report(self):
        from vigia.core.entanglement import EntanglementReport
        return EntanglementReport(
            batch_id="batch-b136",
            document_count=3,
            entanglement_matrix={},
            identical_sequences=[],
            physical_key_signatures=[],
            forced_variety_anomalies=[],
            is_factory_production=True,
            estimated_operator_count=1,
            confidence=0.8,
        )

    def test_builds_case_ready_artifacts_from_report(self):
        """Invariant: each CAIE fracture of a factory-production report
        becomes a batch_forensics case artifact with bounded severity."""
        from vigia.core.entanglement import EntanglementCAIEIntegration
        bridge = EntanglementCAIEIntegration.__new__(EntanglementCAIEIntegration)
        artifacts = bridge.build_caie_artifacts(self._report())
        assert len(artifacts) >= 1
        for a in artifacts:
            _assert_case_ready(a, "batch_forensics")

    def test_non_factory_report_builds_nothing(self):
        from vigia.core.entanglement import EntanglementCAIEIntegration
        report = self._report()
        report.is_factory_production = False
        report.identical_sequences = []
        bridge = EntanglementCAIEIntegration.__new__(EntanglementCAIEIntegration)
        assert bridge.build_caie_artifacts(report) == []


class TestTemporalWiring:
    def test_fracture_dict_becomes_case_ready_artifact(self):
        """Invariant: a temporal fraud fracture routes as temporal_fraud
        with severity clamped to [0,1]."""
        from vigia.forensics.temporal_forensics_redteam import (
            _build_temporal_caie_artifact,
        )
        fracture = {"type": "TEMPORAL_ANACHRONISM", "severity": 0.9,
                    "anachronisms": 2}
        artifact = _build_temporal_caie_artifact(fracture, "doc-hash-1")
        _assert_case_ready(artifact, "temporal_fraud")
        assert artifact["raw_score"] == pytest.approx(0.9)

    def test_out_of_range_severity_is_clamped(self):
        from vigia.forensics.temporal_forensics_redteam import (
            _build_temporal_caie_artifact,
        )
        artifact = _build_temporal_caie_artifact(
            {"type": "X", "severity": 3.7}, "doc-hash-2")
        assert artifact["raw_score"] == 1.0


class TestVisionWiring:
    def test_builds_visual_and_geometry_artifacts(self):
        """Invariant: MALICE verdict with digital perfection builds both
        document_visual and document_geometry case artifacts (types already
        profiled since P3) with bounded scores and no ephemeral engine."""
        from vigia.forensics.vision_audit import _build_caie_artifacts
        artifacts = _build_caie_artifacts(
            image_path="/evidence/fake-deed.png",
            forensic_result={"digital_perfection_detected": True,
                             "confidence": 0.7, "anomaly_regions": []},
            clip_verdict="MALICE",
            malice_score=0.9,
            exif_forensics={"metadata_suspicious": True,
                            "exif_tag_count": 0, "software_stripped": True},
        )
        types = [a["evidence_type"] for a in artifacts]
        assert types == ["document_visual", "document_geometry"]
        for a in artifacts:
            _assert_case_ready(a, a["evidence_type"])

    def test_without_digital_perfection_only_visual(self):
        from vigia.forensics.vision_audit import _build_caie_artifacts
        artifacts = _build_caie_artifacts(
            image_path="/evidence/x.png",
            forensic_result={"digital_perfection_detected": False,
                             "confidence": 0.2},
            clip_verdict="SUSPICION",
            malice_score=0.4,
            exif_forensics={},
        )
        assert [a["evidence_type"] for a in artifacts] == ["document_visual"]


class TestFalseSuccessLogsAreGone:
    def test_no_ephemeral_engine_and_no_false_success_events(self):
        """The four wired modules must no longer instantiate a local engine
        nor emit the false success events Kimi flagged. Source-level check:
        cheap, and it is exactly the regression an accidental revert would
        reintroduce."""
        from pathlib import Path
        sources = {
            "vigia/tools/adversarial_nlp.py",
            "vigia/core/entanglement.py",
            "vigia/forensics/temporal_forensics_redteam.py",
            "vigia/forensics/vision_audit.py",
        }
        root = Path(__file__).resolve().parents[1]
        for rel in sources:
            text = (root / rel).read_text()
            assert "CrossArtifactIncongruenceEngine()" not in text, (
                f"{rel}: ephemeral local CAIE engine is back (B-136 regression)"
            )
            # Match the EMISSION form, not comments that document the history.
            assert 'event_type="CAIE_ARTIFACT_INJECTED"' not in text
            assert 'event_type="ENTANGLEMENT_CAIE_INJECTED"' not in text
