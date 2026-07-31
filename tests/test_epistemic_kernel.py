"""
Regression tests for the epistemic kernel (vigia/core/ontology.py and
vigia/core/reasoning/abduction.py).

Architecture by Kimi (Moonshot AI); design review by ChatGPT (OpenAI);
integration and defect repair by Claude (Anthropic). See
docs/EPISTEMIC_KERNEL.md for the full record.

Each test in the DEFECTS section pins one failure that was present in the
pre-integration revision. They are written so that reverting the fix makes
them fail, not so that they pass against the current code by construction.
"""

import subprocess
import sys
from datetime import datetime, timezone

import pytest

from vigia.core.ontology import (
    AuthorityLayer,
    AuthoritySource,
    ClaimContext,
    ClaimRole,
    ClaimStatus,
    Domain,
    DuplicateClaimError,
    JustificationMode,
    Observation,
    ObservationKind,
    ObservationPayload,
    OntologyClaim,
    OntologyRegistry,
    OriginKind,
    PayloadEncoding,
    RevisionPolicy,
    SourceType,
    TemporalCoverage,
    TemporalWindow,
)
from vigia.core.reasoning.abduction import (
    AbductivePattern,
    AbductiveTribunal,
    AbductiveVerdict,
    ClaimGraph,
    ClaimNode,
    EvaluationState,
    HypothesisMode,
    NodeType,
    TribunalRule,
)

CLOCK = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

AUTHORITY = AuthoritySource(
    name="RFC-9999",
    source_type=SourceType.RFC,
    origin_kind=OriginKind.ENGINEERING_CONVENTION,
    justification_mode=JustificationMode.DOCUMENTED_SPECIFICATION,
)


def make_claim(claim_id, domain=Domain.IMAGE, deps=frozenset(),
               policy=RevisionPolicy.VERSIONED, statement="s",
               authority=AUTHORITY, layer=AuthorityLayer.TECHNICAL):
    return OntologyClaim(
        claim_id=claim_id,
        statement=statement,
        domain=domain,
        layer=layer,
        claim_role=ClaimRole.DESCRIBES,
        origin_kind=OriginKind.ENGINEERING_CONVENTION,
        justification_mode=JustificationMode.DOCUMENTED_SPECIFICATION,
        authority=authority,
        temporal_window=TemporalWindow(),
        context=ClaimContext(),
        revision_policy=policy,
        dependencies=deps,
    )


def make_observation(obs_id="obs.1", domain=Domain.IMAGE,
                     kind=ObservationKind.METADATA_STRUCTURE, context=()):
    return Observation(
        obs_id=obs_id,
        statement="observed",
        domain=domain,
        kind=kind,
        payload=(ObservationPayload("k", "v", PayloadEncoding.RAW),),
        context=context,
    )


# =============================================================================
# DEFECTS present in the pre-integration revision
# =============================================================================

class TestRepairedDefects:

    def test_d1_temporal_window_assess_returns_coverage_enum(self):
        """
        D-1: the validity-interval dataclass and the coverage enum shared the
        name TemporalCoverage in one module, so the dataclass shadowed the
        enum and assess() raised AttributeError on every call.
        """
        window = TemporalWindow(
            valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
            valid_until=datetime(2026, 12, 31, tzinfo=timezone.utc),
        )
        assert window.assess(None) is TemporalCoverage.UNKNOWN
        assert window.assess(datetime(2026, 6, 1, tzinfo=timezone.utc)) is \
            TemporalCoverage.WITHIN_SCOPE
        assert window.assess(datetime(2025, 6, 1, tzinfo=timezone.utc)) is \
            TemporalCoverage.OUTSIDE_SCOPE
        assert window.assess(datetime(2027, 6, 1, tzinfo=timezone.utc)) is \
            TemporalCoverage.OUTSIDE_SCOPE

    def test_d1_coverage_enum_and_window_are_distinct_types(self):
        assert TemporalCoverage is not TemporalWindow
        assert isinstance(TemporalWindow(), TemporalWindow)

    def test_d2_abductive_pattern_is_constructible(self):
        """
        D-2: `causal_template` (no default) followed two defaulted fields,
        which is a TypeError at class-definition time. The module could not
        be imported at all.
        """
        pattern = AbductivePattern(
            pattern_id="p.1",
            observation_kind=ObservationKind.METADATA_STRUCTURE,
            causal_template="metadata rewritten after acquisition",
        )
        assert pattern.causal_template == "metadata rewritten after acquisition"
        assert pattern.hypothesis_mode is HypothesisMode.EXPLANATORY

    def test_d3_hypothesis_preserves_required_context_key_names(self):
        """
        D-3: required context was rebuilt as N empty ClaimContext objects,
        preserving the count of declared keys and discarding every name.
        """
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(
            obs_kind=ObservationKind.METADATA_STRUCTURE,
            verdict=AbductiveVerdict.GENERATES_HYPOTHESIS,
            generates_hypothesis="acquisition tool rewrote the metadata block",
            required_context=("acquisition_tool", "chain_of_custody"),
            hypothesis_mode=HypothesisMode.CAUSAL,
        ))
        verdict, hypo = tribunal.evaluate(make_observation(), make_claim("c.1"))
        assert verdict is AbductiveVerdict.GENERATES_HYPOTHESIS
        assert hypo is not None
        assert hypo.required_context_keys == ("acquisition_tool", "chain_of_custody")
        assert hypo.evaluation_state is EvaluationState.GENERATED
        assert hypo.hypothesis_mode is HypothesisMode.CAUSAL

    def test_d4_cascade_question_marks_transitive_dependents(self):
        """
        D-4: the reverse dependency graph was built and documented as
        supporting cascade invalidation, but no traversal existed.
        """
        reg = OntologyRegistry()
        reg.register(make_claim("c.root"))
        reg.register(make_claim("c.mid", deps=frozenset({"c.root"})))
        reg.register(make_claim("c.leaf", deps=frozenset({"c.mid"})))
        reg.register(make_claim("c.unrelated"))

        questioned = reg.cascade_question("c.root", "acquisition disputed", CLOCK)

        assert questioned == ("c.root", "c.mid", "c.leaf")
        for cid in ("c.root", "c.mid", "c.leaf"):
            assert reg.status(cid) is ClaimStatus.QUESTIONED
        assert reg.status("c.unrelated") is ClaimStatus.ACTIVE
        # Provenance of the cascade is recorded, not just the end state.
        assert "cascade from c.root" in reg.history("c.leaf")[-1][2]

    def test_d4_cascade_terminates_on_cycles(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.a", deps=frozenset({"c.b"})))
        reg.register(make_claim("c.b", deps=frozenset({"c.a"})))
        assert set(reg.cascade_question("c.a", "cycle", CLOCK)) == {"c.a", "c.b"}

    def test_d4_cascade_does_not_overwrite_non_active_status(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.root"))
        reg.register(make_claim("c.mid", deps=frozenset({"c.root"})))
        reg.register(make_claim("c.leaf", deps=frozenset({"c.mid"})))
        reg.supersede("c.mid", "c.mid.v2", "versioned", CLOCK)

        questioned = reg.cascade_question("c.root", "disputed", CLOCK)

        assert reg.status("c.mid") is ClaimStatus.SUPERSEDED
        assert "c.mid" not in questioned
        # An inactive claim does not sever the graph: the leaf beyond it is
        # still reached.
        assert "c.leaf" in questioned

    def test_d5_graph_dependents_and_dependencies_are_not_transposed(self):
        """
        D-5: ClaimGraph.dependents() returned the forward edge set and
        dependencies() the reverse one, inverting both accessors relative to
        the registry's reading of the same relation.
        """
        graph = ClaimGraph()
        for nid in ("n.a", "n.b", "n.c"):
            graph.add_node(ClaimNode(node_id=nid, node_type=NodeType.CLAIM))
        graph.add_dependency("n.a", "n.b")   # a depends on b
        graph.add_dependency("n.b", "n.c")   # b depends on c

        assert graph.dependencies("n.a") == ("n.b",)
        assert graph.dependents("n.b") == ("n.a",)
        assert graph.dependencies("n.c") == ()
        assert graph.dependents("n.c") == ("n.b",)

        # subgraph walks real dependencies: from a we reach b and c.
        sub = graph.subgraph(frozenset({"n.a"}))
        assert sub.node_ids() == ("n.a", "n.b", "n.c")

    def test_d6_authority_hash_covers_jurisdiction_and_reference(self):
        """
        D-6: claim hashing used AuthoritySource.__str__, which omits
        jurisdiction and url_or_ref, so two distinct authorities hashed alike.
        """
        base = dict(name="LAW-1", source_type=SourceType.LAW,
                    origin_kind=OriginKind.INSTITUTIONAL_DECISION,
                    justification_mode=JustificationMode.INSTITUTIONAL_ACCEPTANCE)
        reg_ar = OntologyRegistry()
        reg_ar.register(make_claim("c.1", authority=AuthoritySource(jurisdiction="AR", **base)))
        reg_uy = OntologyRegistry()
        reg_uy.register(make_claim("c.1", authority=AuthoritySource(jurisdiction="UY", **base)))

        assert reg_ar.snapshot(CLOCK).claims_hash != reg_uy.snapshot(CLOCK).claims_hash

    def test_d7_canonical_encoding_is_injective_across_field_boundaries(self):
        """
        D-7: fields were joined with "|", so content containing the separator
        could reproduce another claim's byte string.
        """
        reg_a = OntologyRegistry()
        reg_a.register(make_claim("c.1", statement="alpha|beta"))
        reg_b = OntologyRegistry()
        reg_b.register(make_claim("c.1|alpha", statement="beta"))

        assert reg_a.snapshot(CLOCK).claims_hash != reg_b.snapshot(CLOCK).claims_hash

    def test_d8_payload_encoding_is_typed(self):
        payload = ObservationPayload("k", "v", PayloadEncoding.HASH)
        assert isinstance(payload.encoding, PayloadEncoding)
        assert not hasattr(payload, "value_type")


# =============================================================================
# DETERMINISM (project invariant: no wall-clock reads, stable ordering)
# =============================================================================

class TestDeterminism:

    def test_snapshot_is_stable_across_registration_order(self):
        ids = ["c.1", "c.2", "c.3", "c.4"]
        forward = OntologyRegistry()
        for cid in ids:
            forward.register(make_claim(cid))
        backward = OntologyRegistry()
        for cid in reversed(ids):
            backward.register(make_claim(cid))

        assert forward.snapshot(CLOCK).claims_hash == backward.snapshot(CLOCK).claims_hash

    def test_snapshot_changes_with_status(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1"))
        before = reg.snapshot(CLOCK).claims_hash
        reg.question_claim("c.1", "disputed", CLOCK)
        assert reg.snapshot(CLOCK).claims_hash != before

    def test_accessors_return_sorted_tuples_not_sets(self):
        reg = OntologyRegistry()
        for cid in ("c.3", "c.1", "c.2"):
            reg.register(make_claim(cid))
        claims = reg.by_domain(Domain.IMAGE)
        assert isinstance(claims, tuple)
        assert [c.claim_id for c in claims] == ["c.1", "c.2", "c.3"]

    def test_kernel_hash_is_stable_under_hash_randomization(self):
        """
        A set-ordered accessor would leak PYTHONHASHSEED into any downstream
        serialization. Run the same kernel in two subprocesses with different
        seeds and require an identical digest.
        """
        program = (
            "from datetime import datetime, timezone;"
            "import sys; sys.path.insert(0, '.');"
            "from vigia.core.ontology import *;"
            "a=AuthoritySource('A', SourceType.RFC, OriginKind.FORMALIZATION,"
            " JustificationMode.FORMAL_PROOF);"
            "r=OntologyRegistry();"
            "[r.register(OntologyClaim(c, 'st', Domain.IMAGE, AuthorityLayer.TECHNICAL,"
            " ClaimRole.DESCRIBES, OriginKind.FORMALIZATION, JustificationMode.FORMAL_PROOF,"
            " a, TemporalWindow(), ClaimContext(prerequisites=frozenset({'x','y','z'})),"
            " RevisionPolicy.VERSIONED, frozenset({'d1','d2'}))) for c in"
            " ['c.9','c.1','c.5','c.3']];"
            "print(r.snapshot(datetime(2026,1,1,tzinfo=timezone.utc)).claims_hash)"
        )
        digests = set()
        for seed in ("0", "1", "12345"):
            out = subprocess.run(
                [sys.executable, "-c", program],
                capture_output=True, text=True, env={"PYTHONHASHSEED": seed, "PATH": ""},
            )
            assert out.returncode == 0, out.stderr
            digests.add(out.stdout.strip())
        assert len(digests) == 1, f"kernel hash varies with PYTHONHASHSEED: {digests}"

    def test_evaluate_all_iterates_claims_in_sorted_order(self):
        reg = OntologyRegistry()
        for cid in ("c.3", "c.1", "c.2"):
            reg.register(make_claim(cid))
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(verdict=AbductiveVerdict.COMPATIBLE))
        results = tribunal.evaluate_all(make_observation(), reg)
        assert list(results.keys()) == ["c.1", "c.2", "c.3"]


# =============================================================================
# ARCHITECTURAL INVARIANTS the layer exists to protect
# =============================================================================

class TestEpistemicInvariants:

    def test_observation_never_refutes_a_claim_directly(self):
        """
        The Tribunal's primary output space contains no refutation verdict.
        An observation modifies the abductive space; it does not destroy a
        claim.
        """
        names = {v.name for v in AbductiveVerdict}
        assert names == {"COMPATIBLE", "GENERATES_HYPOTHESIS",
                         "REQUIRES_CONTEXT", "ABSTAIN"}

    def test_origin_and_justification_remain_separate_dimensions(self):
        """
        The two enums must not be merged: "born from a formalization" is not
        "justified by a formal proof".
        """
        assert OriginKind is not JustificationMode
        assert {e.name for e in OriginKind} != {e.name for e in JustificationMode}

    def test_registry_never_deletes_and_refuses_silent_overwrite(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1", statement="original"))
        with pytest.raises(DuplicateClaimError):
            reg.register(make_claim("c.1", statement="replacement"))
        assert reg.get("c.1").statement == "original"

    def test_archived_claim_is_retained_with_its_reason(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1"))
        reg.archive("c.1", "internally inconsistent with c.2", CLOCK)
        assert reg.status("c.1") is ClaimStatus.ARCHIVED
        assert reg.get("c.1") is not None
        assert reg.history("c.1")[-1][2] == "internally inconsistent with c.2"

    def test_dangling_dependencies_are_visible_not_silent(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1", deps=frozenset({"c.absent"})))
        assert reg.dangling_dependencies() == (("c.1", "c.absent"),)
        # Registration is permitted; the claim is active and intact.
        assert reg.status("c.1") is ClaimStatus.ACTIVE

    def test_dangling_dependency_resolves_when_the_target_registers_later(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1", deps=frozenset({"c.late"})))
        assert reg.dangling_dependencies()
        reg.register(make_claim("c.late"))
        assert reg.dangling_dependencies() == ()
        assert reg.cascade_question("c.late", "late arrival disputed", CLOCK) == \
            ("c.late", "c.1")

    def test_conflicting_rules_abstain_rather_than_pick_the_first(self):
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(verdict=AbductiveVerdict.COMPATIBLE))
        tribunal.add_rule(TribunalRule(
            verdict=AbductiveVerdict.GENERATES_HYPOTHESIS,
            generates_hypothesis="h",
        ))
        verdict, hypo = tribunal.evaluate(make_observation(), make_claim("c.1"))
        assert verdict is AbductiveVerdict.ABSTAIN
        assert hypo is None

    def test_rival_abductions_under_one_verdict_abstain(self):
        """
        Two rules agreeing on GENERATES_HYPOTHESIS but proposing different
        explanations do not agree. Emitting the first-registered one would
        silently discard a rival abduction.
        """
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(
            verdict=AbductiveVerdict.GENERATES_HYPOTHESIS,
            generates_hypothesis="tool rewrote metadata",
        ))
        tribunal.add_rule(TribunalRule(
            verdict=AbductiveVerdict.GENERATES_HYPOTHESIS,
            generates_hypothesis="operator edited metadata by hand",
        ))
        verdict, hypo = tribunal.evaluate(make_observation(), make_claim("c.1"))
        assert verdict is AbductiveVerdict.ABSTAIN
        assert hypo is None

    def test_no_matching_rule_abstains(self):
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(target_domain=Domain.NETWORK,
                                       verdict=AbductiveVerdict.COMPATIBLE))
        verdict, hypo = tribunal.evaluate(make_observation(domain=Domain.IMAGE),
                                          make_claim("c.1", domain=Domain.IMAGE))
        assert verdict is AbductiveVerdict.ABSTAIN
        assert hypo is None

    def test_non_active_claims_are_excluded_from_evaluation(self):
        reg = OntologyRegistry()
        reg.register(make_claim("c.1"))
        reg.register(make_claim("c.2"))
        reg.archive("c.2", "superseded by external standard", CLOCK)
        tribunal = AbductiveTribunal()
        tribunal.add_rule(TribunalRule(verdict=AbductiveVerdict.COMPATIBLE))
        assert list(tribunal.evaluate_all(make_observation(), reg)) == ["c.1"]

    def test_pattern_matching_requires_declared_context_keys(self):
        tribunal = AbductiveTribunal()
        tribunal.add_pattern(AbductivePattern(
            pattern_id="p.1",
            observation_kind=ObservationKind.METADATA_STRUCTURE,
            causal_template="t",
            required_context_keys=("acquisition_tool",),
        ))
        assert tribunal.match_patterns(make_observation()) == []
        with_ctx = make_observation(context=(("acquisition_tool", "ftk"),))
        assert [p.pattern_id for p in tribunal.match_patterns(with_ctx)] == ["p.1"]


# =============================================================================
# SCOPE: this layer must stay out of the sealed verdict path
# =============================================================================

def test_kernel_is_not_imported_by_the_scoring_pipeline():
    """
    The epistemic kernel generates hypotheses, never verdicts. If a module in
    the sealed decision path starts importing it, that is an architectural
    change requiring deliberate review, not a silent one.
    """
    out = subprocess.run(
        ["git", "grep", "-l", "-E",
         r"core\.reasoning\.abduction|core import ontology|core\.ontology",
         "--",
         # Production code only. `*.py` as a git pathspec matches at any depth,
         # so the test suite (which imports the kernel by design) has to be
         # excluded explicitly, along with the kernel's own package.
         "vigia/", "*.py",
         ":(exclude)tests/", ":(exclude)vigia/tests/",
         ":(exclude)vigia/core/ontology.py", ":(exclude)vigia/core/reasoning/"],
        capture_output=True, text=True,
    )
    assert out.returncode in (0, 1), out.stderr
    importers = {line for line in out.stdout.splitlines() if line}
    assert importers == set(), (
        f"epistemic kernel reached the pipeline via: {sorted(importers)}"
    )
