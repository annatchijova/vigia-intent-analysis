# vigia/tests/adversarial/test_invariant_stress_harness.py
#
# Invariant Stress Harness — CAIE Representational Invariance
# =============================================================================
# Designed by: Anna Tchijova + Claude (Anthropic) + ChatGPT + Kimi (Moonshot), 2026-06-24
#
# Theoretical basis (ChatGPT, 2026-06-24):
#   A forensic system is Daubert-grade only if it is an equivalence class
#   function — same semantic content must produce same epistemic state
#   regardless of representational path.
#
#   Formally: given semantic input S and two valid representations R1(S), R2(S):
#     F(R1(S)) == F(R2(S))   ← what this harness verifies
#
#   Three possible failure modes, in order of severity:
#     A. Representational divergence (benign) — same CAIE state, different
#        serialization/formatting. Fixable.
#     B. Pipeline divergence (structural) — same semantic input, different
#        signal construction, CAIE sees different data.
#     C. Semantic divergence (grave) — same input, different fracture graph
#        and/or verdict. System is not a function of semantic content.
#
# Architecture of this harness:
#   Two layers extracted BEFORE sealing/serialization:
#
#   CAIELogicalState — must be STRICTLY invariant across representations:
#     - verdict, structural_verdict, probabilistic_verdict
#     - fracture_graph (canonicalized by type+ttp+structural+severity,
#       NOT by narrative strings — artifact_a/artifact_b are excluded
#       because they are formatting-dependent)
#     - golden_rules_fired, has_structural_malice
#
#   CAIEDerivedMetrics — compared AFTER logical state passes:
#     - composite_score (float, 6 decimal places)
#     - n_fractures, n_independent_sources
#     - confidence_penalty_applied
#
# Known limitation (documented, not a bug):
#   rule_trace is NOT PRESENT in evaluate() output — there is no field
#   exposing which specific rule inside detect_fractures() fired. Only the
#   result is observable, not the activation path. This limits diagnostic
#   precision when two paths produce the same fracture_graph via different
#   rule chains. Documented as a future improvement target.
#
# Run:
#   pytest vigia/tests/adversarial/test_invariant_stress_harness.py -v --no-cov

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vigia.tools.caie import Artifact, CrossArtifactIncongruenceEngine  # noqa: E402


# ---------------------------------------------------------------------------
# CAIE State Extraction
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CAIELogicalState:
    """
    Epistemic state of CAIE before any serialization.
    Must be strictly invariant across representational paths.
    """
    verdict: str
    structural_verdict: str
    probabilistic_verdict: str
    fracture_graph: frozenset[tuple]  # frozenset of (type, mitre_ttp, is_structural, is_golden_rule, severity)
    golden_rules_fired: int
    has_structural_malice: bool


@dataclass(frozen=True)
class CAIEDerivedMetrics:
    """
    Quantitative metrics derived from CAIE evaluation.
    Compared after logical state passes — divergence here is less severe
    but still indicates pipeline inconsistency.
    """
    composite_score_str: str        # str from evaluate() boundary (L-021 Phase 1: canonical string)
    n_fractures: int
    n_independent_sources: int
    confidence_penalty_applied: bool


def _canonicalize_fracture(f: dict) -> tuple:
    """
    Project a fracture to its structural identity.

    Deliberately EXCLUDES:
      - artifact_a, artifact_b: narrative strings, formatting-dependent
      - interpretation: free-text, can vary across paths
      - spoofability_delta: derived metric, not a logical property

    Includes:
      - type: the rule that fired (stable identifier)
      - mitre_ttp: the ATT&CK technique (stable)
      - is_structural: whether it forces structural_verdict
      - is_golden_rule: whether it bypasses probabilistic scoring
      - severity: canonical string from evaluate() boundary (L-021 Phase 1:
        _dround output is str-serialized, e.g. "0.7500").
        No float() conversion — the string IS the canonical form.
    """
    return (
        f.get("type", "").upper(),
        f.get("mitre_ttp", ""),
        bool(f.get("is_structural", False)),
        bool(f.get("is_golden_rule", False)),
        # L-021 guarantees str. Guard against callers that pass non-str directly.
        (lambda s: s if isinstance(s, str) else str(s))(f.get("severity", "0.0000")),
    )


def extract_logical_state(r: dict) -> CAIELogicalState:
    fractures = r.get("fractures", [])
    return CAIELogicalState(
        verdict=r.get("verdict", ""),
        structural_verdict=r.get("structural_verdict", ""),
        probabilistic_verdict=r.get("probabilistic_verdict", ""),
        fracture_graph=frozenset(_canonicalize_fracture(f) for f in fractures),
        golden_rules_fired=int(r.get("golden_rules_triggered", 0)),
        has_structural_malice=any(f.get("is_structural", False) for f in fractures),
    )


def extract_derived_metrics(r: dict) -> CAIEDerivedMetrics:
    # composite_score is str since L-021 Phase 1 — use directly, no float() needed
    raw_score = r.get("composite_score", "0.000000")
    return CAIEDerivedMetrics(
        composite_score_str=raw_score if isinstance(raw_score, str) else f"{float(raw_score):.6f}",
        n_fractures=len(r.get("fractures", [])),  # single source of truth — fractures_unique may differ
        n_independent_sources=int(r.get("independent_sources", 0)),
        confidence_penalty_applied=bool(r.get("confidence_penalty_applied", False)),
    )


def _run_caie(artifacts: list[tuple]) -> dict:
    """
    Run CAIE on a list of (source_tool, evidence_type, raw_score, description, metadata)
    tuples. Returns evaluate() output dict.
    """
    eng = CrossArtifactIncongruenceEngine()
    eng.reset()
    for source_tool, evidence_type, raw_score, description, metadata in artifacts:
        eng.add_artifact(Artifact(
            source_tool=source_tool,
            evidence_type=evidence_type,
            raw_score=raw_score,
            description=description,
            metadata=metadata,
        ))
    return eng.evaluate()


# ---------------------------------------------------------------------------
# Invariance assertion helpers
# ---------------------------------------------------------------------------

def assert_logical_invariance(r1: dict, r2: dict, label: str) -> None:
    """
    Assert that two evaluate() results have identical logical state.
    Reports which specific component diverged for diagnostic precision.
    """
    s1 = extract_logical_state(r1)
    s2 = extract_logical_state(r2)

    assert s1.verdict == s2.verdict, (
        f"[{label}] verdict divergence: {s1.verdict!r} vs {s2.verdict!r}"
    )
    assert s1.structural_verdict == s2.structural_verdict, (
        f"[{label}] structural_verdict divergence: "
        f"{s1.structural_verdict!r} vs {s2.structural_verdict!r}"
    )
    assert s1.probabilistic_verdict == s2.probabilistic_verdict, (
        f"[{label}] probabilistic_verdict divergence: "
        f"{s1.probabilistic_verdict!r} vs {s2.probabilistic_verdict!r}"
    )
    assert s1.fracture_graph == s2.fracture_graph, (
        f"[{label}] fracture_graph divergence.\n"
        f"  Only in R1: {s1.fracture_graph - s2.fracture_graph}\n"
        f"  Only in R2: {s2.fracture_graph - s1.fracture_graph}"
    )
    assert s1.golden_rules_fired == s2.golden_rules_fired, (
        f"[{label}] golden_rules_fired divergence: "
        f"{s1.golden_rules_fired} vs {s2.golden_rules_fired}"
    )
    assert s1.has_structural_malice == s2.has_structural_malice, (
        f"[{label}] has_structural_malice divergence: "
        f"{s1.has_structural_malice} vs {s2.has_structural_malice}"
    )


def assert_metric_invariance(r1: dict, r2: dict, label: str) -> None:
    m1 = extract_derived_metrics(r1)
    m2 = extract_derived_metrics(r2)
    # Strong invariance: structural counts and penalty flag
    assert m1.n_fractures == m2.n_fractures, (
        f"[{label}] n_fractures divergence: {m1.n_fractures} vs {m2.n_fractures}"
    )
    assert m1.n_independent_sources == m2.n_independent_sources, (
        f"[{label}] n_independent_sources divergence: "
        f"{m1.n_independent_sources} vs {m2.n_independent_sources}"
    )
    assert m1.confidence_penalty_applied == m2.confidence_penalty_applied, (
        f"[{label}] confidence_penalty_applied divergence: "
        f"{m1.confidence_penalty_applied} vs {m2.confidence_penalty_applied}"
    )
    # Weak invariance: composite_score_str should be stable but is not
    # a hard contract if CAIE scoring pipeline evolves.
    assert m1.composite_score_str == m2.composite_score_str, (
        f"[{label}] composite_score_str divergence (weak invariant): "
        f"{m1.composite_score_str!r} vs {m2.composite_score_str!r}"
    )


# ---------------------------------------------------------------------------
# Test fixtures — semantic inputs used across multiple invariance tests
# ---------------------------------------------------------------------------

# S1: C2 connection log + clean memory (the T-5 scenario, now fixed)
_S1_ARTIFACTS = [
    ("log_tool", "log_entry", 0.9, "Outbound C2 connection",
     {"dst_ip": "203.0.113.77", "pid": 4521}),
    # B-154: memory that was ACTUALLY network-analyzed and found no connections
    # (network_connections present-but-empty) — a genuine contradiction against
    # the log's outbound claim. Previously this was {"pid": 4521} with NO network
    # field, which under the four-state model is NOT_ANALYZED (memory never
    # examined for network), not "analyzed, no activity" — and must not accuse.
    ("mem_tool", "memory_process", 0.1, "Process memory analyzed — no network objects",
     {"pid": 4521, "network_connections": []}),
]

# S2: Benign HTTP access log (should NOT trigger LOG_VS_MEMORY)
_S2_ARTIFACTS = [
    ("web_tool", "log_entry", 0.2, "HTTP GET request",
     {"ip": "1.2.3.4", "status": 200, "method": "GET"}),
    ("mem_tool", "memory_process", 0.1, "Process clean",
     {"pid": 1234}),
]

# S3: No artifacts — edge case
_S3_ARTIFACTS: list = []

# S4: Single artifact — below independent sources threshold
_S4_ARTIFACTS = [
    ("single_tool", "log_entry", 0.9, "Single source",
     {"dst_ip": "10.0.0.1"}),
]


# ---------------------------------------------------------------------------
# I1 — Insertion order invariance
# CAIE must produce identical logical state regardless of artifact order.
# ---------------------------------------------------------------------------

class TestInsertionOrderInvariance:
    """
    I1: Same artifacts in different insertion order → same epistemic state.
    This is the most basic form of representational invariance.
    If CAIE fails this, the system is order-dependent by design — a
    reproducibility violation under Daubert.
    """

    def test_s1_order_forward_vs_reverse(self):
        r1 = _run_caie(_S1_ARTIFACTS)
        r2 = _run_caie(list(reversed(_S1_ARTIFACTS)))
        assert_logical_invariance(r1, r2, "S1 order forward/reverse")
        assert_metric_invariance(r1, r2, "S1 order forward/reverse")

    def test_s2_benign_order_invariant(self):
        r1 = _run_caie(_S2_ARTIFACTS)
        r2 = _run_caie(list(reversed(_S2_ARTIFACTS)))
        assert_logical_invariance(r1, r2, "S2 benign order invariant")

    def test_s1_all_permutations_agree(self):
        """
        With only 2 artifacts there are 2 permutations — test both.
        For N artifacts the combinatorial explosion becomes infeasible,
        so we limit to 2-artifact cases here.
        """
        import itertools
        results = [_run_caie(list(p)) for p in itertools.permutations(_S1_ARTIFACTS)]
        ref = extract_logical_state(results[0])
        for i, r in enumerate(results[1:], 1):
            s = extract_logical_state(r)
            assert s == ref, (
                f"Permutation {i} diverges from reference.\n"
                f"  verdict: {s.verdict} vs {ref.verdict}\n"
                f"  fracture_graph diff: {s.fracture_graph ^ ref.fracture_graph}"
            )


# ---------------------------------------------------------------------------
# I2 — Re-evaluation invariance (idempotency)
# Same engine, same artifacts, evaluated twice → same result.
# ---------------------------------------------------------------------------

class TestReEvaluationInvariance:
    """
    I2: evaluate() called on the same engine state produces identical output.
    Detects: stateful side effects, random seeds, timestamp-dependent logic.
    """

    def test_s1_double_evaluation(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.reset()
        for source_tool, evidence_type, raw_score, description, metadata in _S1_ARTIFACTS:
            eng.add_artifact(Artifact(
                source_tool=source_tool,
                evidence_type=evidence_type,
                raw_score=raw_score,
                description=description,
                metadata=metadata,
            ))
        r1 = eng.evaluate()
        r2 = eng.evaluate()
        assert_logical_invariance(r1, r2, "S1 double evaluation")
        assert_metric_invariance(r1, r2, "S1 double evaluation")

    def test_s1_fresh_engine_vs_reused(self):
        """
        Fresh engine must produce same result as reset engine.
        Detects: residual state from previous evaluations not cleared by reset().
        """
        r1 = _run_caie(_S1_ARTIFACTS)

        # Pollute with S2, then reset and re-run S1
        eng = CrossArtifactIncongruenceEngine()
        for source_tool, evidence_type, raw_score, description, metadata in _S2_ARTIFACTS:
            eng.add_artifact(Artifact(
                source_tool=source_tool,
                evidence_type=evidence_type,
                raw_score=raw_score,
                description=description,
                metadata=metadata,
            ))
        eng.reset()
        for source_tool, evidence_type, raw_score, description, metadata in _S1_ARTIFACTS:
            eng.add_artifact(Artifact(
                source_tool=source_tool,
                evidence_type=evidence_type,
                raw_score=raw_score,
                description=description,
                metadata=metadata,
            ))
        r2 = eng.evaluate()

        assert_logical_invariance(r1, r2, "S1 fresh vs reset engine")


# ---------------------------------------------------------------------------
# I3 — Score representational invariance
# composite_score must be deterministic across repeated instantiations.
# ---------------------------------------------------------------------------

class TestScoreRepresentationalInvariance:
    """
    I3: composite_score is a deterministic function of artifacts.
    Detects: float non-determinism, random initialization, time-dependent scoring.
    """

    def test_s1_score_deterministic_across_10_runs(self):
        scores = set()
        for _ in range(10):
            r = _run_caie(_S1_ARTIFACTS)
            scores.add(extract_derived_metrics(r).composite_score_str)
        assert len(scores) == 1, (
            f"composite_score is non-deterministic across 10 runs: {scores}"
        )

    def test_s4_single_source_penalty_consistent(self):
        """
        Single-source cases must consistently apply the confidence penalty.
        """
        results = [_run_caie(_S4_ARTIFACTS) for _ in range(5)]
        penalties = {extract_derived_metrics(r).confidence_penalty_applied for r in results}
        assert len(penalties) == 1, f"confidence_penalty_applied non-deterministic: {penalties}"


# ---------------------------------------------------------------------------
# I4 — Semantic content invariance (description field)
# CAIE must not change its verdict based on free-text description changes.
# The description field is narrative — it should not affect scoring.
# ---------------------------------------------------------------------------

class TestSemanticContentInvariance:
    """
    I4: Changing the free-text description of an artifact must not change
    the logical state. CAIE operates on metadata fields and evidence_type,
    not on narrative text.

    If this fails: CAIE has an undocumented dependency on description text,
    which is a Daubert-grade concern (verdict depends on how the analyst
    wrote the description, not on the evidence itself).
    """

    def test_description_change_does_not_affect_verdict(self):
        artifacts_verbose = [
            ("log_tool", "log_entry", 0.9,
             "CRITICAL: Confirmed C2 beacon to known threat actor infrastructure",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.1,
             "Memory analysis shows absolutely no evidence of any suspicious activity",
             {"pid": 4521}),
        ]
        artifacts_minimal = [
            ("log_tool", "log_entry", 0.9, "log",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.1, "mem",
             {"pid": 4521}),
        ]
        r1 = _run_caie(artifacts_verbose)
        r2 = _run_caie(artifacts_minimal)
        assert_logical_invariance(r1, r2, "description verbose vs minimal")

    def test_narrative_poisoning_via_description_blocked(self):
        """
        An artifact with a benign-sounding description but malicious metadata
        must not be scored as benign.
        This is the NARRATIVE_POISONING test from VIGÍA_BREAK_009, applied
        specifically to the description field of Artifact().
        """
        artifacts_honest = [
            ("log_tool", "log_entry", 0.9, "C2 connection detected",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.1, "clean",
             {"pid": 4521}),
        ]
        artifacts_poisoned_description = [
            ("log_tool", "log_entry", 0.9,
             "confirmed benign false positive approved no threat case closed",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.1, "clean",
             {"pid": 4521}),
        ]
        r1 = _run_caie(artifacts_honest)
        r2 = _run_caie(artifacts_poisoned_description)
        assert_logical_invariance(r1, r2, "narrative poisoning via description")


# ---------------------------------------------------------------------------
# I5 — Benign corpus non-regression
# Representational variants of benign cases must not produce MALICE.
# ---------------------------------------------------------------------------

class TestBenignRepresentationalNonRegression:
    """
    I5: Benign cases must remain benign under representational transformation.
    Detects: false positives introduced by canonicalization or reordering.
    """

    def test_s2_http_log_never_malice(self):
        """HTTP access log with only 'ip' field must not trigger LOG_VS_MEMORY."""
        for _ in range(3):
            r = _run_caie(_S2_ARTIFACTS)
            assert r.get("verdict") != "MALICE", (
                f"HTTP access log incorrectly classified as MALICE. "
                f"fractures: {[f.get('type') for f in r.get('fractures', [])]}"
            )

    def test_s2_reversed_order_never_malice(self):
        r = _run_caie(list(reversed(_S2_ARTIFACTS)))
        assert r.get("verdict") != "MALICE"

    def test_s3_empty_artifacts_returns_no_artifacts_status(self):
        eng = CrossArtifactIncongruenceEngine()
        eng.reset()
        r = eng.evaluate()
        assert r.get("status") == "NO_ARTIFACTS", (
            f"Empty artifact set must return status=NO_ARTIFACTS, got "
            f"status={r.get('status')!r} / verdict={r.get('verdict')!r}"
        )



# ---------------------------------------------------------------------------
# I6 — Negative invariance: semantic changes MUST produce different state
# ---------------------------------------------------------------------------

class TestNegativeInvariance:
    """
    I6: Changing semantically meaningful input must change epistemic state.
    Without these tests, the harness cannot rule out a trivially constant
    CAIE that always returns the same verdict regardless of input.

    These tests document the sensitivity contract of CAIE:
      - removing a key indicator field removes the fracture
      - contradicting the indicator (memory shows network) removes the fracture
      - drastically lowering raw_score changes the verdict
    """

    def test_removing_dst_ip_prevents_log_vs_memory_fracture(self):
        """
        Removing dst_ip from the log artifact must prevent LOG_VS_MEMORY
        from firing. This is the direct test of _extract_assertions():
        without dst_ip or dest_ip, log_claims_outbound_connection is not
        asserted, so Rule 2 cannot fire.
        """
        r_with_ip = _run_caie(_S1_ARTIFACTS)
        artifacts_no_ip = [
            ("log_tool", "log_entry", 0.9, "Log without outbound indicator",
             {"status": 200, "method": "GET", "ip": "1.2.3.4"}),  # only HTTP fields
            ("mem_tool", "memory_process", 0.1, "Process memory clean",
             {"pid": 4521}),
        ]
        r_without_ip = _run_caie(artifacts_no_ip)

        s_with    = extract_logical_state(r_with_ip)
        s_without = extract_logical_state(r_without_ip)

        # P1.2 fix: membership assertions, not total-difference comparison.
        # Total difference is overconstrained — if S1 has no fractures for
        # any reason, both frozensets are empty and the assertion fires a
        # false alarm. We only care about LOG_VS_MEMORY specifically.
        # P1.3 fix: check fracture type only, not exact tuple — severity and
        # TTP mapping may change without being a bug.
        assert any(t[0] == "LOG_VS_MEMORY" for t in s_with.fracture_graph), (
            "S1 (with dst_ip) must have LOG_VS_MEMORY fracture. "
            "If this fails, _extract_assertions is not producing "
            "log_claims_outbound_connection for dst_ip inputs."
        )
        assert not any(t[0] == "LOG_VS_MEMORY" for t in s_without.fracture_graph), (
            "S1 without dst_ip must NOT have LOG_VS_MEMORY fracture. "
            "Only 'ip' (HTTP source field) is present — must not trigger rule."
        )

    def test_memory_with_network_activity_prevents_log_vs_memory(self):
        """
        If memory shows network activity (dest_ip or network_connections
        present), LOG_VS_MEMORY must NOT fire — both sources agree.
        The fracture is defined as contradiction; agreement is not a fracture.
        """
        artifacts_corroborated = [
            ("log_tool", "log_entry", 0.9, "Outbound C2 connection",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.8, "Memory also shows network",
             {"pid": 4521, "dest_ip": "203.0.113.77", "network_connections": ["203.0.113.77:443"]}),
        ]
        r_contradicted  = _run_caie(_S1_ARTIFACTS)
        r_corroborated  = _run_caie(artifacts_corroborated)

        s_contradicted = extract_logical_state(r_contradicted)
        s_corroborated = extract_logical_state(r_corroborated)

        # Strong assertion: contradicted case MUST have LOG_VS_MEMORY
        assert any(t[0] == "LOG_VS_MEMORY" for t in s_contradicted.fracture_graph), (
            "S1 (contradicted) must have LOG_VS_MEMORY fracture. "
            "If this fails, the negative invariance test is vacuous."
        )
        # Strong assertion: corroborated case must NOT have LOG_VS_MEMORY
        assert not any(t[0] == "LOG_VS_MEMORY" for t in s_corroborated.fracture_graph), (
            "When memory corroborates log network activity, LOG_VS_MEMORY "
            "must NOT fire. Both sources agree — no contradiction exists."
        )
        # Secondary: global fracture_graph difference (weaker, but documents intent)
        assert s_contradicted.fracture_graph != s_corroborated.fracture_graph, (
            "Corroborated evidence (memory confirms log) must produce a "
            "different fracture_graph than contradicted evidence."
        )

    def test_low_raw_score_produces_different_verdict_than_high(self):
        """
        Drastically changing raw_score must change the verdict or score.
        Verifies CAIE is sensitive to the quantitative evidence strength,
        not just to artifact presence/absence.
        """
        artifacts_high = [
            ("log_tool", "log_entry", 0.95, "Strong C2 signal",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.05, "Very clean memory",
             {"pid": 4521}),
        ]
        artifacts_low = [
            ("log_tool", "log_entry", 0.05, "Weak ambiguous signal",
             {"dst_ip": "203.0.113.77", "pid": 4521}),
            ("mem_tool", "memory_process", 0.05, "Clean memory",
             {"pid": 4521}),
        ]
        r_high = _run_caie(artifacts_high)
        r_low  = _run_caie(artifacts_low)

        m_high = extract_derived_metrics(r_high)
        m_low  = extract_derived_metrics(r_low)

        assert m_high.composite_score_str != m_low.composite_score_str, (
            f"Drastically different raw_scores (0.95 vs 0.05) must produce "
            f"different composite_score. Got identical: {m_high.composite_score_str!r}. "
            "CAIE may be insensitive to raw_score magnitude."
        )

# ---------------------------------------------------------------------------
# Diagnostic: print state vectors for manual inspection (not a test)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== S1: C2 log + clean memory ===")
    r = _run_caie(_S1_ARTIFACTS)
    print("logical:", extract_logical_state(r))
    print("metrics:", extract_derived_metrics(r))
    print()
    print("=== S2: benign HTTP log ===")
    r = _run_caie(_S2_ARTIFACTS)
    print("logical:", extract_logical_state(r))
    print("metrics:", extract_derived_metrics(r))
