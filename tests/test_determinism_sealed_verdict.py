"""
tests/test_determinism_sealed_verdict.py
========================================
Determinism of the sealed decision path (invariant 5.2: "Deterministic core").

These tests guard the Daubert admissibility property that the same evidence
must produce the same verdict and the same seal, bit-for-bit, regardless of
when or in which process the analysis runs. They exercise the LIVE decision
path directly:

  - vigia_scorer._vigia_score  : the canonical scoring pipeline (root module,
                                 previously outside the --cov scope).
  - bundle_builder._canonicalize / _sha256_dict : the strict canonical encoder
                                 (H22) that gives one input exactly one hash.

The invariant is asserted as EQUALITY BETWEEN RUNS, never against a hardcoded
score. A concrete score is a moving target as the engine evolves; determinism
is the contract that must hold whatever the score is.

Failure modes these tests would catch:
  - a float reaching a place where an int was canonicalized (1 vs 1.0 collision)
  - dict/set ordering leaking into a hash (PYTHONHASHSEED sensitivity)
  - the verdict depending on the order evidence was collected
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from vigia_scorer import _vigia_score
from vigia.core.bundle_builder import _canonicalize, _sha256_dict

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Shared fixture — a non-trivial DEVICE-evidence case that yields a real
# (non-ABSTAIN) verdict, so the whole pipeline is exercised, not a short path.
# ---------------------------------------------------------------------------

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


def _reference_case() -> dict:
    return {
        "case_id": "DET-TEST-001",
        "artifacts": [
            _artifact(0, "memory_process"),
            _artifact(1, "keylogger_capture"),
            _artifact(2, "email_content"),
        ],
    }


# ---------------------------------------------------------------------------
# Canonical encoder (H22) — one input, one hash
# ---------------------------------------------------------------------------

class TestCanonicalizationDeterminism:
    def test_int_and_float_do_not_collide(self):
        # JSON alone renders 1 and 1.0 to distinct strings but round-trips them
        # into the same Python type; the canonical encoder must keep them apart
        # so an int score and a float score never seal to the same bundle_hash.
        assert _canonicalize(1) == "1:int"
        assert _canonicalize(1.0) == "1.00000000"
        assert _canonicalize(1) != _canonicalize(1.0)
        assert _sha256_dict({"x": 1}) != _sha256_dict({"x": 1.0})

    def test_bool_is_encoded_before_int(self):
        # bool is a subclass of int; if the int branch ran first, True would
        # canonicalize to "1:int" and collide with the integer 1.
        assert _canonicalize(True) == "true"
        assert _canonicalize(False) == "false"
        assert _sha256_dict({"x": True}) != _sha256_dict({"x": 1})

    def test_none_is_explicit(self):
        assert _canonicalize(None) == "null"

    def test_dict_key_order_is_irrelevant(self):
        # Insertion order must not change the seal — keys are sorted.
        a = {"alpha": 1, "beta": 2, "gamma": 3}
        b = {"gamma": 3, "beta": 2, "alpha": 1}
        assert _sha256_dict(a) == _sha256_dict(b)

    def test_list_order_is_significant(self):
        # Lists are ordered; reordering them is a real content change and MUST
        # change the hash. This documents the contract (contrast with dicts).
        assert _sha256_dict({"xs": [1, 2, 3]}) != _sha256_dict({"xs": [3, 2, 1]})

    def test_hash_is_stable_across_calls(self):
        payload = {"verdict": "MALICE", "score": 0.4357, "n": 3, "flag": True}
        assert _sha256_dict(payload) == _sha256_dict(dict(payload))


# ---------------------------------------------------------------------------
# Scorer determinism — the live decision path
# ---------------------------------------------------------------------------

class TestScorerDeterminism:
    def test_same_input_same_output(self):
        case = _reference_case()
        r1 = _vigia_score(case)
        r2 = _vigia_score(_reference_case())
        # Full structural equality via canonical JSON — every field, not just
        # the verdict, must be reproducible.
        assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)

    def test_verdict_is_invariant_to_evidence_order(self):
        # The order in which evidence was collected must not change the verdict:
        # a forensic result cannot depend on filesystem walk order.
        arts = _reference_case()["artifacts"]
        forward = _vigia_score({"case_id": "ORD", "artifacts": list(arts)})
        reverse = _vigia_score({"case_id": "ORD", "artifacts": list(reversed(arts))})
        assert forward["verdict"] == reverse["verdict"]
        assert forward["score"] == reverse["score"]
        assert forward["confidence"] == reverse["confidence"]

    def test_deterministic_across_fresh_processes(self, tmp_path):
        # A dict/set-ordering leak is invisible within one process but shows up
        # when PYTHONHASHSEED changes. Run the scorer in two fresh interpreters
        # with different seeds and assert byte-identical verdicts.
        probe = tmp_path / "det_probe.py"
        probe.write_text(
            "import json\n"
            "from vigia_scorer import _vigia_score\n"
            "def a(i, e):\n"
            "    return {'artifact_id': f'A{i}', 'evidence_type': e, 'raw_score': 0.9,\n"
            "            'source_tool': f'tool{i}', 'description': f'desc{i}',\n"
            "            'prior_trust': 0.85, 'provenance_chain': ['a','b','c'],\n"
            "            'timestamp': f'2026-01-0{i+1}T10:00:00Z', 'metadata': {}}\n"
            "arts = [a(0,'memory_process'), a(1,'keylogger_capture'), a(2,'email_content')]\n"
            "r = _vigia_score({'case_id': 'DET-TEST-001', 'artifacts': arts})\n"
            "print('RESULT:' + json.dumps({k: r[k] for k in ('verdict','score','confidence')}, sort_keys=True))\n"
        )

        def _run(seed: str) -> str:
            env = {
                "PYTHONHASHSEED": seed,
                "PYTHONPATH": str(REPO_ROOT),
                "PATH": "/usr/bin:/bin:/usr/local/bin",
            }
            out = subprocess.run(
                [sys.executable, str(probe)],
                capture_output=True, text=True, env=env, cwd=str(REPO_ROOT),
            )
            assert out.returncode == 0, f"probe failed (seed={seed}): {out.stderr[-2000:]}"
            lines = [ln for ln in out.stdout.splitlines() if ln.startswith("RESULT:")]
            assert lines, f"probe produced no RESULT line (seed={seed}): {out.stdout[-2000:]}"
            return lines[-1]

        assert _run("0") == _run("1")
