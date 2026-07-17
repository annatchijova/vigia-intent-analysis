"""
B-136 phase 1 — EVIDENCE_PROFILES entries for the three document-domain types.

Kimi's audit confirmed (CONFIRMED BY INDUCTION) that the three orphan CAIE
injection sites use evidence types absent from EVIDENCE_PROFILES, so even a
mechanically-fixed call would be rejected by the add_artifact whitelist
(CAIE_INVALID_EVIDENCE_TYPE). Option 1 (route the fractures into the case
stream) requires the profiles to exist first.

Calibration decided per docs/PROPUESTA_B136_CAIE_WIRING_20260717.md, by
analogy with the existing scale (the same method B-066 used for the mobile
band). All three are document-domain, not device-domain, so their B-070
epistemic role is CONTEXTUAL: they inform the malice composite but are NOT
an independent device source — they must never corroborate the device gate.

Each test names the invariant it defends and the mutation it would catch.
"""

from fractions import Fraction

import pytest

from vigia.tools.caie import (
    _VALID_EVIDENCE_TYPES,
    EVIDENCE_PROFILES,
    EVIDENCE_ROLE_CONTEXTUAL,
    EVIDENCE_ROLE_DEVICE,
    Artifact,
    CrossArtifactIncongruenceEngine,
    evidence_role,
)

# (type, spoofability, base_weight) — the collective-signed calibration.
_B136_PROFILES = [
    ("linguistic_forensics", 0.60, 0.18),
    ("batch_forensics", 0.45, 0.22),
    ("temporal_fraud", 0.55, 0.20),
]


class TestB136Profiles:
    @pytest.mark.parametrize("etype,spoof,weight", _B136_PROFILES)
    def test_profile_exists_with_signed_calibration(self, etype, spoof, weight):
        """Invariant: the three document-domain types carry exactly the
        calibration the collective signed off on. Mutation caught: silently
        changing spoofability/weight (which moves adjusted_score) goes red."""
        profile = EVIDENCE_PROFILES.get(etype)
        assert profile is not None, (
            f"B-136: {etype!r} must be profiled — without a profile the "
            "add_artifact whitelist rejects it and the CAIE wiring is dead."
        )
        assert profile.spoofability == spoof
        assert profile.base_weight == weight

    @pytest.mark.parametrize("etype,spoof,weight", _B136_PROFILES)
    def test_type_passes_the_whitelist(self, etype, spoof, weight):
        """Invariant: the whitelist accepts the three types (it is derived
        from EVIDENCE_PROFILES keys). Mutation caught: removing the profile
        or building the whitelist from a stale copy."""
        assert etype in _VALID_EVIDENCE_TYPES

    @pytest.mark.parametrize("etype,spoof,weight", _B136_PROFILES)
    def test_add_artifact_accepts_the_type(self, etype, spoof, weight):
        """Induction: the real guardrail path (add_artifact) accepts an
        artifact of each new type. Before this fix it returned False with
        CAIE_INVALID_EVIDENCE_TYPE."""
        engine = CrossArtifactIncongruenceEngine()
        accepted = engine.add_artifact(Artifact(
            source_tool="b136_test",
            evidence_type=etype,
            raw_score=0.5,
            description="B-136 profile acceptance probe",
        ))
        assert accepted is True


class TestB136EpistemicRole:
    @pytest.mark.parametrize("etype,spoof,weight", _B136_PROFILES)
    def test_role_is_contextual(self, etype, spoof, weight):
        """Invariant (B-070): document-domain fractures inform the composite
        but are NOT an independent device source — they must not corroborate
        the device gate. Mutation caught: dropping the _EVIDENCE_ROLE entry
        (the default is DEVICE, which WOULD corroborate) goes red."""
        assert evidence_role(etype) == EVIDENCE_ROLE_CONTEXTUAL, (
            f"B-136: {etype!r} is document-domain; as DEVICE it would count "
            "as an independent corroboration source in the scorer gate, "
            "letting a single-modality stylometric fracture unlock verdicts."
        )

    def test_unknown_types_still_default_to_device(self):
        """Regression guard: the conservative DEVICE default for unknown
        types (B-070 design) must survive this change."""
        assert evidence_role("some_type_never_registered") == EVIDENCE_ROLE_DEVICE

    def test_existing_document_types_keep_their_current_role(self):
        """Documented asymmetry (proposal section 2): document_visual and
        document_geometry stay DEVICE for now — reclassifying them moves
        artifacts already in the corpus and needs its own comparison run.
        This test freezes the deliberate decision; flipping them without a
        corpus run goes red here first."""
        assert evidence_role("document_visual") == EVIDENCE_ROLE_DEVICE
        assert evidence_role("document_geometry") == EVIDENCE_ROLE_DEVICE
