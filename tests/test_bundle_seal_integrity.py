"""
tests/test_bundle_seal_integrity.py
===================================
Cryptographic sealing and tamper detection for the ForensicBundle
(EBS v1 invariants I1 Determinism and I2 Chained integrity).

The bundle is the artifact a court receives. `bundle_builder.build_bundle`
turns a scorer result into a sealed dict; `BundleBuilder.quick_verify`
recomputes the chained hashes and reports whether the content still matches
its seal. These tests assert:

  - a freshly built bundle verifies clean (round-trip),
  - the content hashes that exclude wall-clock fields (graph/decision/policy)
    are reproducible across rebuilds (I1),
  - any mutation of the sealed payload is detected (I2) — a value change, a
    nested field, and a dropped field.

`quick_verify` deliberately reimplements the hashing (it does not import the
producing code) so a bug in the sealer cannot mask itself in the verifier.
"""
from __future__ import annotations

import copy

import pytest

from vigia_scorer import _vigia_score
from vigia.core.bundle_builder import build_bundle, BundleBuilder


def _artifact(i: int, etype: str, raw: float = 0.9) -> dict:
    return {
        "artifact_id": f"A{i}",
        "evidence_type": etype,
        "raw_score": raw,
        "source_tool": f"tool{i}",
        "description": f"desc{i}",
        "prior_trust": 0.85,
        "provenance_chain": ["a", "b", "c"],
        "timestamp": f"2026-01-0{i + 1}T10:00:00Z",
        "metadata": {},
    }


def _sealed_reference():
    case = {
        "case_id": "SEAL-TEST-001",
        "artifacts": [
            _artifact(0, "memory_process"),
            _artifact(1, "keylogger_capture"),
            _artifact(2, "email_content"),
        ],
    }
    scorer_result = _vigia_score(case)
    return case, scorer_result, build_bundle(case, scorer_result)


# ---------------------------------------------------------------------------
# Round-trip and determinism (I1)
# ---------------------------------------------------------------------------

class TestSealRoundTrip:
    def test_fresh_bundle_verifies_clean(self):
        _, _, sealed = _sealed_reference()
        ok, msg = BundleBuilder.quick_verify(sealed)
        assert ok, f"freshly sealed bundle failed verification: {msg}"

    def test_integrity_block_is_populated(self):
        _, _, sealed = _sealed_reference()
        integrity = sealed["integrity"]
        for field in ("bundle_hash", "graph_hash", "policy_hash", "decision_hash"):
            assert integrity.get(field), f"missing/empty integrity.{field}"
        # SHA-256 hex digests are 64 chars.
        assert len(integrity["bundle_hash"]) == 64

    def test_content_hashes_are_reproducible(self):
        # graph_hash / decision_hash / policy_hash exclude wall-clock fields
        # (generated_at, created_at, top-level timestamp), so two builds of the
        # same case+result must produce identical content hashes (I1).
        case, scorer_result, sealed1 = _sealed_reference()
        sealed2 = build_bundle(case, scorer_result)
        for field in ("graph_hash", "decision_hash", "policy_hash"):
            assert sealed1["integrity"][field] == sealed2["integrity"][field], (
                f"{field} not reproducible across rebuilds"
            )


# ---------------------------------------------------------------------------
# Tamper detection (I2) — bundle_hash covers ALL content
# ---------------------------------------------------------------------------

class TestTamperDetection:
    def test_verdict_field_tamper_is_detected(self):
        _, _, sealed = _sealed_reference()
        tampered = copy.deepcopy(sealed)
        tampered["decision_trace"]["risk"] = 0.123456
        ok, msg = BundleBuilder.quick_verify(tampered)
        assert not ok
        assert "bundle_hash" in msg

    def test_evidence_graph_tamper_is_detected(self):
        _, _, sealed = _sealed_reference()
        tampered = copy.deepcopy(sealed)
        # Rewrite a node label — the kind of edit that would reassign evidence.
        tampered["evidence_graph"]["nodes"][0] = "ATTACKER_INJECTED_NODE"
        ok, msg = BundleBuilder.quick_verify(tampered)
        assert not ok

    def test_nested_caie_field_tamper_is_detected(self):
        _, _, sealed = _sealed_reference()
        tampered = copy.deepcopy(sealed)
        # Downgrade the sealed verdict inside caie_analysis without touching the
        # integrity block — must not pass.
        tampered.setdefault("caie_analysis", {})["verdict"] = "NOISE"
        ok, _ = BundleBuilder.quick_verify(tampered)
        assert not ok

    def test_dropped_field_is_detected(self):
        _, _, sealed = _sealed_reference()
        tampered = copy.deepcopy(sealed)
        tampered.pop("config_attestation", None)
        ok, _ = BundleBuilder.quick_verify(tampered)
        assert not ok

    def test_untouched_copy_still_verifies(self):
        # Control: a deep copy that is NOT modified must still verify, proving
        # the detections above come from the mutation, not from copying.
        _, _, sealed = _sealed_reference()
        ok, msg = BundleBuilder.quick_verify(copy.deepcopy(sealed))
        assert ok, msg
