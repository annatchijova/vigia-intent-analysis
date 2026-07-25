"""
CAIE duplicate-artifact epistemology bug — invariant interaction, not a
per-module bug.

Every individual CAIE property (Noisy-OR commutativity, f(A)==f(A)
idempotence across separate runs, deterministic rounding) already had its
own passing test in vigia/tests/adversarial/test_order_sensitivity.py. None
of them tested a different, more basic idempotence axis: does adding the
SAME artifact twice produce the same result as adding it once?

It did not. evaluate() groups artifacts by (source_tool, evidence_type) and
fuses each group via Noisy-OR (1 - prod(1 - adjusted_score)) -- a model
that assumes every term is an independent observation. Submitting the
identical artifact N times (a duplicate log entry, a tool re-run whose
output gets ingested twice, or deliberate padding) is not N independent
observations, it is one fact reported N times, yet the fusion compounded it
every time. _MIN_INDEPENDENT_SOURCES only counts distinct (source_tool,
evidence_type) pairs, not distinct underlying facts within a pair, so the
"3 independent sources" corroboration gate did not catch this either.

Reproduced before the fix: 3 genuinely distinct weak artifacts (one per
source/type, raw_score=0.55 each) scored SUSPICION (composite ~0.24).
Duplicating each artifact 3x (9 submissions, still only 3 source/type
pairs, zero new facts) reached MALICE (composite ~0.56), with
structural_verdict staying NOISE throughout -- the entire escalation was
duplicate-driven, not evidence-driven. This is exactly the class of bug
where every module passes its own tests but the interaction (repeated
submission x Noisy-OR fusion x the source/type-pair corroboration count)
was never demonstrated.

Fix: CrossArtifactIncongruenceEngine.add_artifact() now rejects an artifact
whose full content signature (source_tool, evidence_type, raw_score,
description, metadata, provenance_chain, timestamp) exactly matches one
already accepted in the same evaluation. A genuinely distinct second
occurrence (different PID, different acquisition_hash, different
timestamp, ...) gets a different signature and is still accepted as new
evidence -- only byte-identical resubmissions are rejected.
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


def _one_of_each() -> list[Artifact]:
    """3 genuinely distinct weak artifacts, one per (source_tool, evidence_type)."""
    return [
        Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata=dict(_ACQ),
        ),
        Artifact(
            source_tool="shimcache", evidence_type="file_metadata", raw_score=0.55,
            description="Executable with exec flag", metadata=dict(_ACQ),
        ),
        Artifact(
            source_tool="plaso", evidence_type="log_entry", raw_score=0.55,
            description="Logon event", metadata=dict(_ACQ),
        ),
    ]


def _evaluate(artifacts: list[Artifact]) -> tuple[dict, int]:
    engine = CrossArtifactIncongruenceEngine()
    engine.reset()
    accepted = sum(1 for a in artifacts if engine.add_artifact(a))
    return engine.evaluate(), accepted


class TestDuplicateArtifactDoesNotInflateScore:
    def test_duplicating_every_artifact_does_not_change_composite_or_verdict(self):
        baseline_result, baseline_accepted = _evaluate(_one_of_each())

        base = _one_of_each()
        duplicated = [a for a in base for _ in range(3)]  # each artifact submitted 3x
        dup_result, dup_accepted = _evaluate(duplicated)

        assert baseline_accepted == 3
        assert dup_accepted == 3, (
            "add_artifact() must reject the 6 exact resubmissions -- only the "
            "first occurrence of each of the 3 distinct artifacts counts."
        )
        assert dup_result["probabilistic_score"] == baseline_result["probabilistic_score"]
        assert dup_result["verdict"] == baseline_result["verdict"]

    def test_duplicate_padding_does_not_escalate_suspicion_to_malice(self):
        """Historical reproduction: before the fix, 9 submissions (3 facts x 3
        copies) crossed the composite>=0.5 MALICE threshold that 3 facts alone
        (composite ~0.24, SUSPICION) never reached."""
        base = _one_of_each()
        heavily_duplicated = [a for a in base for _ in range(8)]  # 24 submissions
        result, accepted = _evaluate(heavily_duplicated)

        assert accepted == 3
        assert result["verdict"] == "SUSPICION"
        assert float(result["probabilistic_score"]) < 0.5

    def test_add_artifact_returns_false_for_exact_duplicate(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        artifact = _one_of_each()[0]

        assert engine.add_artifact(artifact) is True
        assert engine.add_artifact(artifact) is False
        assert len(engine._artifacts) == 1


class TestDistinctArtifactsAreNeverConflated:
    """The dedup fix must not over-reject genuinely distinct evidence that
    happens to share tool/type/score/description but differs elsewhere."""

    def test_different_metadata_is_accepted_as_a_new_artifact(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        a1 = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata={**_ACQ, "pid": 100},
        )
        a2 = Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.55,
            description="Kernel hook observed", metadata={**_ACQ, "pid": 200},
        )

        assert engine.add_artifact(a1) is True
        assert engine.add_artifact(a2) is True
        assert len(engine._artifacts) == 2

    def test_different_timestamp_is_accepted_as_a_new_artifact(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        a1 = Artifact(
            source_tool="win_evtx", evidence_type="log_entry", raw_score=0.55,
            description="Logon event 4624", metadata=dict(_ACQ),
            timestamp="2026-01-01T00:00:00Z",
        )
        a2 = Artifact(
            source_tool="win_evtx", evidence_type="log_entry", raw_score=0.55,
            description="Logon event 4624", metadata=dict(_ACQ),
            timestamp="2026-01-01T01:00:00Z",
        )

        assert engine.add_artifact(a1) is True
        assert engine.add_artifact(a2) is True
        assert len(engine._artifacts) == 2

    def test_reset_clears_duplicate_tracking(self):
        engine = CrossArtifactIncongruenceEngine()
        artifact = _one_of_each()[0]

        assert engine.add_artifact(artifact) is True
        engine.reset()
        # Same artifact must be accepted again in a fresh evaluation cycle.
        assert engine.add_artifact(artifact) is True
