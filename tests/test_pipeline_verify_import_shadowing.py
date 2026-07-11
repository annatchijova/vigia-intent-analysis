"""Regression tests for B-097 — forensics package shadowing.

Importing vigia.pipeline.pipeline puts "<repo>/vigia" on sys.path (inserted at
import time by vigia.core.bundle_builder and others), so the bare top-level
name "forensics" resolves to vigia/forensics/ — which has no verify_ebs_v1
module. Before the fix, VigiaPipeline.load_and_verify() and the in-process
fallback of verify_bundle_external() crashed with
"No module named 'forensics.verify_ebs_v1'" in any fresh process that had not
imported the real top-level forensics/ package first.

The fix loads the standalone verifier by explicit file path (importlib), so it
must work regardless of import order. These tests run the whole flow in a
fresh subprocess with the pipeline imported FIRST — the exact order that used
to crash.
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Child script: import pipeline FIRST (establishes the shadow), then seal a
# minimal bundle, save it, and verify it through both code paths under test.
CHILD_SCRIPT = r"""
import json, sys, tempfile, os

# Order matters: this import is what shadows the top-level "forensics" package.
from vigia.pipeline.pipeline import VigiaPipeline

import forensics  # noqa: F401 — prove the shadow is active in this process
assert "vigia" in forensics.__file__.replace(os.sep, "/"), (
    "precondition failed: 'forensics' did not resolve to vigia/forensics/ — "
    "the shadowing scenario this test guards against no longer exists"
)

from vigia.core.ebs_v1 import (
    EvidenceGraph, DecisionTrace, SystemState, ForensicBundle,
    make_default_policy,
)
from vigia.core.bundle_builder import BundleBuilder

bundle = ForensicBundle(
    evidence_graph=EvidenceGraph(nodes=["A0"], edges=[]),
    decision_trace=DecisionTrace(
        decision="ABSTAIN", posterior=0.5, risk=0.1, reason_code="TEST:B097"
    ),
    policy_spec=make_default_policy(),
    system_state=SystemState(drift_score=0.0, graph_stability_global=0.5),
)
sealed = BundleBuilder.seal(bundle)

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    bundle_path = f.name
BundleBuilder.save(sealed, bundle_path)

pipeline = VigiaPipeline()

# Path 1: in-process verification (crashed before the fix)
result = pipeline.load_and_verify(bundle_path)
assert isinstance(result, dict), f"load_and_verify returned {type(result)}"

# Path 2: external verification — the script path must exist at the repo root
# (the old dirname(__file__)-relative path never existed)
ext = pipeline.verify_bundle_external(bundle_path)
assert isinstance(ext, dict), f"verify_bundle_external returned {type(ext)}"
assert "error" not in ext, f"verify_bundle_external errored: {ext}"

os.unlink(bundle_path)
print(json.dumps({"load_and_verify": result, "external": ext}))
"""


def _run_child():
    env = dict(os.environ)
    env["PYTHONPATH"] = REPO_ROOT
    return subprocess.run(
        [sys.executable, "-c", CHILD_SCRIPT],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=120,
    )


def test_load_and_verify_survives_forensics_shadowing():
    proc = _run_child()
    assert proc.returncode == 0, (
        f"fresh-process verification crashed (B-097 regression):\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    assert isinstance(payload["load_and_verify"], dict)
    assert isinstance(payload["external"], dict)


def test_verify_script_exists_at_repo_root():
    # The subprocess path of verify_bundle_external depends on this file.
    assert os.path.isfile(
        os.path.join(REPO_ROOT, "forensics", "verify_ebs_v1.py")
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
