"""B-198 — distinguish a reproducible analysis from a per-run custody seal.

The full ``bundle_hash`` deliberately binds a freshly assigned UUID and wall
clock metadata.  It is therefore an identity of *this execution*, not a
stable identifier for replaying the same analytical input.  A new sealed EBS
bundle must also carry an ``analysis_fingerprint`` over its deterministic
projection.  The standalone verifier must re-derive that optional field; old
bundles without it remain valid historical artifacts.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

from vigia.core.bundle_builder import BundleBuilder
from vigia.core.ebs_v1 import (
    DecisionTrace,
    EvidenceGraph,
    ForensicBundle,
    SystemState,
    make_default_policy,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "verify_ebs_v1_b198", REPO_ROOT / "forensics" / "verify_ebs_v1.py"
)
_verifier = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_verifier)


def _seal() -> dict:
    return BundleBuilder.seal(
        ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=["A0"], edges=[]),
            decision_trace=DecisionTrace(
                decision="ABSTAIN", posterior=0.5, risk=0.1,
                reason_code="B198: fixed analytical fixture",
            ),
            policy_spec=make_default_policy(),
            system_state=SystemState(drift_score=0.0, graph_stability_global=0.5),
        )
    )


def _check(result, rule: str) -> dict:
    matches = [entry for entry in result.checks if entry["rule"] == rule]
    assert matches, f"verifier did not emit {rule}"
    return matches[0]


def test_same_analysis_has_stable_fingerprint_but_unique_custody_seal():
    first = _seal()
    second = _seal()

    assert first["integrity"]["bundle_hash"] != second["integrity"]["bundle_hash"], (
        "full custody seals must bind their distinct per-run identities"
    )
    assert first["integrity"]["analysis_fingerprint"] == second["integrity"]["analysis_fingerprint"], (
        "identical analytical content needs a stable replay identifier"
    )


def test_analysis_fingerprint_is_rederived_by_both_verifiers():
    sealed = _seal()
    tampered = copy.deepcopy(sealed)
    tampered["integrity"]["analysis_fingerprint"] = "00" * 32

    quick_ok, quick_message = BundleBuilder.quick_verify(tampered)
    assert not quick_ok
    assert "analysis_fingerprint" in quick_message

    result = _verifier.verify_bundle(tampered)
    check = _check(result, "R1_ANALYSIS_FINGERPRINT")
    assert not check["passed"]
    assert not result.passed


def test_historical_bundle_without_analysis_fingerprint_remains_verifiable():
    sealed = _seal()
    sealed["integrity"].pop("analysis_fingerprint")

    quick_ok, quick_message = BundleBuilder.quick_verify(sealed)
    assert quick_ok, quick_message

    result = _verifier.verify_bundle(sealed)
    check = _check(result, "R1_ANALYSIS_FINGERPRINT")
    assert check["passed"]
    assert "legacy" in check["message"].lower()


def test_public_pipeline_result_exposes_the_replay_identifier():
    """A caller must not have to parse a full custody artifact to compare runs."""
    from vigia.pipeline.pipeline import run_vigia

    result = run_vigia([
        {
            "tool_name": "SDA", "value": 0.8, "z_score": 2.3,
            "confidence": 0.88,
            "metadata": {
                "acquisition_tool": "fixture", "acquisition_hash": "a" * 64,
                "acquisition_timestamp": "2026-07-21T00:00:00Z",
            },
        },
    ])
    sealed = json.loads(result["bundle_json"])
    assert result["analysis_fingerprint"] == sealed["integrity"]["analysis_fingerprint"]
