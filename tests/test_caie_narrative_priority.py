"""
CAIE narrative presentation order — "attack against the auditor", not the
detector.

Every prior CAIE fix in this series targeted the SCORE / VERDICT (the
machine's own conclusion). This one targets a different surface: the
human-readable text a perito, judge, or analyst actually reads. The verdict
computation was never wrong here -- has_golden_rule / has_structural_malice
in evaluate() always scanned the FULL fracture list regardless of order.
What was wrong is which finding the narrative HIGHLIGHTS.

filtered_fractures kept raw rule-execution order (Rule 1, Rule 2, ... Rule 8
in detect_fractures()) -- an artifact of which check happens to run first in
the method body, with zero forensic meaning. The Peirce "thirdness" narrative
picked filtered_fractures[0] as "the Key finding" and golden_rules[0] as "the
Golden Rule", i.e. whichever fired first, not whichever mattered most.

Confirmed empirically before the fix: a VERDICT_CONFLICT fracture (severity
0.5, interpretation ends "Requires deeper analysis... to resolve") that fires
before a TEMPORAL_CAUSALITY_VIOLATION (severity 1.0 -- MAXIMUM, interpretation
"proving the evidence was planted retroactively") produced this narrative on
a case the machine verdict correctly called MALICE:

    "Key: VERDICT_CONFLICT -- Contradictory verdicts from different tools.
    Requires deeper analysis to determine which source is reliable. Apply
    spoofability weighting to resolve. Golden Rule triggered:
    TEMPORAL_CAUSALITY_VIOLATION."

A human skimming that sentence reads "ambiguous, needs more work" -- primacy
bias -- while the actual driver of the MALICE verdict, a structural proof of
evidence fabrication, is buried in a trailing clause. Same evidence, same
correct verdict, different induced interpretation depending on which rule
happened to execute first: exactly the "two bundles, same evidence and
verdict, different human interpretation by presentation order alone" failure
this test suite is named for.

Fix: fractures_by_priority sorts by (tier, -severity) where tier is Golden
Rule (0) < structural malice (1) < everything else (2), before anything
downstream reads [0]. Tier, not raw severity, is primary: severity numbers
alone do not preserve the code's own stated epistemology (a Golden Rule is
"a different epistemic category entirely", not just a high number) --
CRYPTOGRAPHIC_INCONSISTENCY (Golden Rule) can be severity 0.9, below a
LOG_VS_MEMORY structural-malice fracture at 0.95, so a plain severity sort
would still rank the Golden Rule second.
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


def _verdict_conflict_pair() -> list[Artifact]:
    """VERDICT_CONFLICT, severity 0.5 -- fires as an early rule."""
    return [
        Artifact(
            source_tool="tool_a", evidence_type="log_entry", raw_score=0.5,
            description="Tool A verdict", metadata={**_ACQ, "verdict": "MALICE"},
            timestamp="2026-01-01T10:00:00Z",
        ),
        Artifact(
            source_tool="tool_b", evidence_type="log_entry", raw_score=0.5,
            description="Tool B verdict", metadata={**_ACQ, "verdict": "NOISE"},
            timestamp="2026-01-01T10:00:01Z",
        ),
    ]


def _temporal_causality_violation_pair() -> list[Artifact]:
    """TEMPORAL_CAUSALITY_VIOLATION, severity 1.0 (Golden Rule) -- fires as a
    later rule than VERDICT_CONFLICT in detect_fractures()'s execution order."""
    return [
        Artifact(
            source_tool="firewall", evidence_type="log_entry", raw_score=0.6,
            description="Network log", metadata={**_ACQ, "network_log_time": "2026-01-01T09:00:00Z"},
            timestamp="2026-01-01T09:00:00Z",
        ),
        Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.6,
            description="Process creation", metadata={**_ACQ, "process_creation_time": "2026-01-01T09:30:00Z"},
            timestamp="2026-01-01T09:30:00Z",
        ),
    ]


def _log_vs_memory_pair() -> list[Artifact]:
    """LOG_VS_MEMORY with PID overlap, severity 0.95 -- structural malice, NOT
    a Golden Rule."""
    return [
        Artifact(
            source_tool="plaso", evidence_type="log_entry", raw_score=0.7,
            description="Log claims outbound connection",
            metadata={**_ACQ, "dst_ip": "8.8.8.8", "pid": "4812"},
            timestamp="2026-01-01T10:00:00Z",
        ),
        Artifact(
            source_tool="volatility", evidence_type="memory_process", raw_score=0.7,
            description="Memory clean, no network",
            metadata={**_ACQ, "network_connections": [], "pid": "4812"},
            timestamp="2026-01-01T10:00:01Z",
        ),
    ]


def _cryptographic_inconsistency_confirmed() -> Artifact:
    """CRYPTOGRAPHIC_INCONSISTENCY, severity 0.9 (Golden Rule) -- lower raw
    severity than LOG_VS_MEMORY (0.95), despite being the categorically more
    significant finding."""
    return Artifact(
        source_tool="authenticode", evidence_type="digital_signature", raw_score=0.7,
        description="Signature check",
        metadata={
            **_ACQ, "signature_mismatch": True, "trust_chain_validated": True,
            "signer_validated": True, "catalog_validated": True,
            "claimed_identity": "Microsoft Corp",
        },
        timestamp="2026-01-01T10:00:02Z",
    )


class TestNarrativeLeadsWithHighestPriorityFinding:
    def test_max_severity_golden_rule_leads_even_when_detected_second(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for a in _verdict_conflict_pair():  # low severity, detected FIRST
            engine.add_artifact(a)
        for a in _temporal_causality_violation_pair():  # max severity, detected SECOND
            engine.add_artifact(a)

        result = engine.evaluate()

        assert result["verdict"] == "MALICE"
        assert result["fractures"][0]["type"] == "TEMPORAL_CAUSALITY_VIOLATION"
        assert result["fractures"][0]["severity"] == "1.0000"
        assert "Key: TEMPORAL_CAUSALITY_VIOLATION" in result["peirce_chain"]["thirdness"]
        # The lower-priority finding must still be present, just not first.
        types = [f["type"] for f in result["fractures"]]
        assert "VERDICT_CONFLICT" in types
        assert types.index("TEMPORAL_CAUSALITY_VIOLATION") < types.index("VERDICT_CONFLICT")

    def test_golden_rule_outranks_higher_raw_severity_non_golden_fracture(self):
        """Tier beats raw severity number: CRYPTOGRAPHIC_INCONSISTENCY (Golden
        Rule, severity 0.9) must lead over LOG_VS_MEMORY (structural malice,
        severity 0.95) -- a plain severity sort would get this backwards."""
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for a in _log_vs_memory_pair():
            engine.add_artifact(a)
        engine.add_artifact(_cryptographic_inconsistency_confirmed())

        result = engine.evaluate()

        severities = {f["type"]: float(f["severity"]) for f in result["fractures"]}
        assert severities["LOG_VS_MEMORY"] > severities["CRYPTOGRAPHIC_INCONSISTENCY"]
        assert result["fractures"][0]["type"] == "CRYPTOGRAPHIC_INCONSISTENCY"
        assert result["fractures"][0]["is_golden_rule"] is True
        assert "Key: CRYPTOGRAPHIC_INCONSISTENCY" in result["peirce_chain"]["thirdness"]

    def test_golden_rules_list_is_also_priority_ordered(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        for a in _verdict_conflict_pair():
            engine.add_artifact(a)
        for a in _temporal_causality_violation_pair():
            engine.add_artifact(a)

        result = engine.evaluate()
        assert "Golden Rule triggered: TEMPORAL_CAUSALITY_VIOLATION." in result["peirce_chain"]["thirdness"]

    def test_no_fractures_produces_the_documented_fallback_text(self):
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        engine.add_artifact(Artifact(
            source_tool="tool_a", evidence_type="log_entry", raw_score=0.1,
            description="Benign entry", metadata=dict(_ACQ),
        ))

        result = engine.evaluate()
        assert result["fractures"] == []
        assert "No structural discrepancies." in result["peirce_chain"]["thirdness"]

    def test_ordering_is_deterministic_across_runs(self):
        def _run():
            engine = CrossArtifactIncongruenceEngine()
            engine.reset()
            for a in _verdict_conflict_pair():
                engine.add_artifact(a)
            for a in _temporal_causality_violation_pair():
                engine.add_artifact(a)
            return engine.evaluate()

        r1, r2 = _run(), _run()
        assert [f["type"] for f in r1["fractures"]] == [f["type"] for f in r2["fractures"]]
        assert r1["peirce_chain"]["thirdness"] == r2["peirce_chain"]["thirdness"]
