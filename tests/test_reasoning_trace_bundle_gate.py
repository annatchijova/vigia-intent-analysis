"""
tests/test_reasoning_trace_bundle_gate.py
=========================================
Phase 1.5 gate — the reasoning trace is a PROCESS-evidence sibling that must not
touch the sealed bundle. Proven against REAL sealed bundles in results/agent_batch/:

  (a/b) building the trace does NOT change the bundle_digest — the bundle dict is
        never mutated and the trace lives in a separate file, so every existing
        case's digest is byte-identical before and after;
  (c+)  the derived trace verifies against each real bundle (verdict pairing +
        own chain intact).

The bundle itself is inherently non-deterministic (wall-clock analysis_timestamp),
so "same digest as stored across a re-run" is not a meaningful invariant; the
meaningful one — adding the trace changes nothing in the bundle — is what this
gate proves.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os

import pytest

from vigia.core.reasoning_trace import build_from_agent_bundle, verify_reasoning_trace

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BUNDLES = sorted(glob.glob(os.path.join(_REPO, "results/agent_batch/*_agent_bundle.json")))[:15]


def _digest(bundle: dict) -> str:
    # Mirror vigia_agent._seal_bundle's canonicalization for a stable comparison.
    text = json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.mark.skipif(not _BUNDLES, reason="no sealed agent bundles in results/agent_batch/")
@pytest.mark.parametrize("path", _BUNDLES, ids=[os.path.basename(p) for p in _BUNDLES])
def test_trace_leaves_bundle_digest_unchanged_and_verifies(path):
    with open(path, encoding="utf-8") as f:
        bundle = json.load(f)
    if not bundle.get("agent_verdict"):
        pytest.skip("bundle has no sealed agent_verdict")

    before = _digest(bundle)
    trace = build_from_agent_bundle(bundle)   # must not mutate the bundle dict
    after = _digest(bundle)

    assert before == after, f"trace build mutated the sealed bundle: {os.path.basename(path)}"

    result = verify_reasoning_trace(bundle, trace)
    assert result.valid, (os.path.basename(path), result.to_dict())
