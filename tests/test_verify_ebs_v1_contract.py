"""
tests/test_verify_ebs_v1_contract.py
====================================
Contract guard for the INDEPENDENT verifier (forensics/verify_ebs_v1.py) —
V-3 / V-4 / V-5 of docs/PATTERN_HUNT_20260718.md (2026-07-18).

Why this file exists as a REAL pytest module: the historical verifier checks
lived in tests/integration/test_ebs_v1_integration.py, whose homegrown @test
decorator swallows AssertionError at collection time (U-1 of the same hunt) —
under pytest those checks can fail silently. These guards are collected and
enforced by pytest itself.

What it pins:
  V-3 — decision_hash is now RE-DERIVED by the verifier (R1_DECISION_HASH).
        Before 2026-07-18 it was sealed in every bundle's IntegrityBlock but
        no verifier recomputed it: 64-hex garbage passed every check
        (decorative integrity field). The regression test here is the exact
        tamper that used to be invisible.
  V-4 — R4 (engine_attestation_hash) verifies PRESENCE + FORMAT only, and
        must SAY so: the stdlib-only verifier cannot re-derive the engine
        hash without the pinned source tree. The honesty is load-bearing —
        a fabricated 64-hex attestation passes R4 by design (documented
        boundary), so the success message must never read as proof of origin.
  Backward compatibility — the three EBS-shaped historical bundles under
        results/ must keep verifying at their pre-fix levels, decision_hash
        included (verified empirically before landing the fix: SRL-DMZ-FTP
        Level 2, NINA Level 3, VANKO-CORRECTED Level 3).
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load the verifier the same way a third party would: by file path, no package
# imports (it is stdlib-only by design; keep the test faithful to that mode).
_spec = importlib.util.spec_from_file_location(
    "verify_ebs_v1_under_test", REPO_ROOT / "forensics" / "verify_ebs_v1.py"
)
_verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_verifier)
verify_bundle = _verifier.verify_bundle

ebs = pytest.importorskip(
    "vigia.core.ebs_v1",
    reason="vigia.core.ebs_v1 not importable (run with PYTHONPATH=$(pwd))",
)
from vigia.core.bundle_builder import BundleBuilder  # noqa: E402


def _sealed_bundle() -> dict:
    bundle = ebs.ForensicBundle(
        evidence_graph=ebs.EvidenceGraph(nodes=["n1"], edges=[]),
        decision_trace=ebs.DecisionTrace(
            decision="ABSTAIN", posterior=0.5, risk=0.1, drift_score=0.0
        ),
        policy_spec=ebs.make_default_policy(),
        system_state=ebs.SystemState(drift_score=0.0, graph_stability_global=0.5),
    )
    return BundleBuilder.seal(bundle)


def _check(result, rule: str) -> dict:
    hits = [c for c in result.checks if c["rule"] == rule]
    assert hits, f"rule {rule} missing from verifier output — check not wired"
    return hits[0]


# ---------------------------------------------------------------------------
# V-3 — decision_hash re-derivation
# ---------------------------------------------------------------------------

class TestDecisionHashReDerived:
    def test_fresh_bundle_passes_with_decision_hash_check_present(self):
        result = verify_bundle(_sealed_bundle())
        assert result.passed
        c = _check(result, "R1_DECISION_HASH")
        assert c["passed"], c["message"]

    def test_tampered_decision_hash_now_fails(self):
        """THE regression: before 2026-07-18 this exact tamper passed every
        verifier (decision_hash was sealed but never recomputed)."""
        sealed = _sealed_bundle()
        sealed["integrity"]["decision_hash"] = "ab" * 32
        result = verify_bundle(sealed)
        c = _check(result, "R1_DECISION_HASH")
        assert not c["passed"], (
            "64-hex garbage in integrity.decision_hash passed verification — "
            "the decorative-field defect (V-3) regressed"
        )
        assert not result.passed
        assert result.conformity_level < 2

    def test_missing_decision_hash_fails(self):
        sealed = _sealed_bundle()
        sealed["integrity"]["decision_hash"] = ""
        result = verify_bundle(sealed)
        assert not _check(result, "R1_DECISION_HASH")["passed"]

    def test_decision_content_tamper_still_caught_by_bundle_hash(self):
        """Defense in depth sanity: decision_trace content was ALWAYS covered
        by bundle_hash (that is why V-3 was decorative, not a content hole).
        The new check must not have weakened that."""
        sealed = _sealed_bundle()
        tampered = copy.deepcopy(sealed)
        tampered["decision_trace"]["risk"] = 0.99
        result = verify_bundle(tampered)
        assert not result.passed
        # Both layers must catch it now: content (bundle_hash) and the
        # re-derived decision_hash (content changed under the stored hash).
        assert not _check(result, "R1_BUNDLE_HASH")["passed"]
        assert not _check(result, "R1_DECISION_HASH")["passed"]


# ---------------------------------------------------------------------------
# V-4 — R4 honesty: format-only, and it must say so
# ---------------------------------------------------------------------------

class TestAttestationHonesty:
    def test_fabricated_attestation_passes_r4_as_documented_boundary(self):
        """A plausible 64-hex attestation PASSES R4 — by design (stdlib-only
        verifier cannot re-derive origin). This test pins the boundary as a
        FACT so nobody 'fixes' the label back into an overclaim without
        noticing they are claiming origin verification that does not happen."""
        sealed = _sealed_bundle()
        sealed["integrity"]["engine_attestation_hash"] = "cd" * 32
        result = verify_bundle(sealed)
        c = _check(result, "R4_ENGINE_ATTESTATION")
        assert c["passed"]  # format-only: fabricated value is NOT detected here

    def test_r4_success_message_declares_format_only(self):
        """The honesty is load-bearing (V-4): the SUCCESS message must state
        that only the format was verified and origin is NOT re-derived. If
        this assert fails, the verifier went back to implying origin proof.

        The attestation is injected explicitly: the minimal seal fixture may
        legitimately produce no attestation in some environments, and this
        test targets the success-path wording, not the producer."""
        sealed = _sealed_bundle()
        sealed["integrity"]["engine_attestation_hash"] = "ef" * 32
        result = verify_bundle(sealed)
        c = _check(result, "R4_ENGINE_ATTESTATION")
        assert c["passed"], c["message"]
        msg = c["message"].lower()
        assert "formato" in msg and "origen" in msg, (
            "R4 success message no longer discloses its format-only scope: "
            f"{c['message']!r}"
        )


# ---------------------------------------------------------------------------
# Backward compatibility — historical sealed bundles keep verifying
# ---------------------------------------------------------------------------

_HISTORICAL = [
    ("results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json", 2),
    ("results/agent_batch/bundle_VIGIA-REAL-NINA.json", 3),
    ("results/agent_batch/bundle_VIGIA-REAL-VANKO-CORRECTED.json", 3),
]


class TestHistoricalBundlesStillVerify:
    @pytest.mark.parametrize("rel,expected_level", _HISTORICAL)
    def test_historical_bundle_level_preserved(self, rel, expected_level):
        path = REPO_ROOT / rel
        if not path.exists():
            pytest.skip(f"historical bundle not present in this checkout: {rel}")
        with open(path, encoding="utf-8") as f:
            bundle = json.load(f)
        result = verify_bundle(bundle)
        assert result.passed, (
            f"{rel}: historical bundle stopped verifying after the "
            f"decision_hash check landed — backward-compat broken"
        )
        assert result.conformity_level == expected_level, (
            f"{rel}: conformity level moved "
            f"({result.conformity_level} != pre-fix {expected_level})"
        )
        assert _check(result, "R1_DECISION_HASH")["passed"], (
            f"{rel}: historical decision_hash does not re-derive — the "
            "dual-canon (v2/v1) fallback is not covering this bundle"
        )
