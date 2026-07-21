"""B-166 — cached batch verdicts require matching evidence and runtime bytes."""

from __future__ import annotations

from pathlib import Path

import run_all_agent as runner
from vigia.core.runtime_fingerprint import (
    runtime_execution_fingerprint,
    runtime_source_fingerprint,
)


def _bundle(*, evidence: str = "e" * 64, runtime: str = "r" * 64) -> dict:
    return {
        "agent_verdict": "NOISE",
        "evidence_sha256": evidence,
        "runtime_fingerprint": runtime,
    }


def test_cache_reuses_only_when_evidence_and_runtime_match():
    assert runner.cache_reuse_reason(
        _bundle(), evidence_sha256="e" * 64, runtime_fingerprint="r" * 64
    ) is None


def test_cache_rejects_changed_evidence_before_runtime_comparison():
    assert runner.cache_reuse_reason(
        _bundle(), evidence_sha256="x" * 64, runtime_fingerprint="r" * 64
    ) == "evidence_changed"


def test_cache_rejects_historical_bundle_without_runtime_fingerprint():
    historical = _bundle()
    historical.pop("runtime_fingerprint")
    assert runner.cache_reuse_reason(
        historical, evidence_sha256="e" * 64, runtime_fingerprint="r" * 64
    ) == "runtime_or_context_changed_or_legacy_bundle"


def test_cache_rejects_changed_runtime_with_identical_evidence():
    assert runner.cache_reuse_reason(
        _bundle(), evidence_sha256="e" * 64, runtime_fingerprint="x" * 64
    ) == "runtime_or_context_changed_or_legacy_bundle"


def test_cache_rejects_unsealed_bundle():
    assert runner.cache_reuse_reason(
        {}, evidence_sha256="e" * 64, runtime_fingerprint="r" * 64
    ) == "unsealed_bundle"


def _write_runtime_root(root: Path) -> None:
    (root / "vigia" / "core").mkdir(parents=True)
    (root / "vigia_agent.py").write_text("AGENT = 1\n")
    (root / "vigia_scorer.py").write_text("SCORER = 1\n")
    (root / "sift_orchestrator.py").write_text("ORCHESTRATOR = 1\n")
    (root / "vigia" / "core" / "scorer.py").write_text("VALUE = 1\n")


def test_runtime_fingerprint_is_content_and_path_sensitive(tmp_path):
    _write_runtime_root(tmp_path)
    original = runtime_source_fingerprint(tmp_path)
    (tmp_path / "vigia" / "core" / "scorer.py").write_text("VALUE = 2\n")
    changed = runtime_source_fingerprint(tmp_path)
    assert original != changed


def test_execution_fingerprint_binds_semantic_environment_without_key_material(tmp_path):
    _write_runtime_root(tmp_path)
    base = runtime_execution_fingerprint(
        tmp_path, {"VIGIA_EBS_RESOLVE": "motor", "VIGIA_HMAC_KEY": "first"}
    )
    changed_mode = runtime_execution_fingerprint(
        tmp_path, {"VIGIA_EBS_RESOLVE": "legacy", "VIGIA_HMAC_KEY": "first"}
    )
    changed_key = runtime_execution_fingerprint(
        tmp_path, {"VIGIA_EBS_RESOLVE": "motor", "VIGIA_HMAC_KEY": "second"}
    )
    assert base != changed_mode
    assert base == changed_key


def test_effective_agent_environment_supplies_agent_evidence_default(tmp_path, monkeypatch):
    monkeypatch.delenv("VIGIA_EVIDENCE_DIR", raising=False)
    case = tmp_path / "case.json"
    case.write_text("{}")
    assert runner._agent_effective_environment(case)["VIGIA_EVIDENCE_DIR"] == str(tmp_path)


def test_case_hash_refuses_symlink(tmp_path):
    original = tmp_path / "case.json"
    original.write_text("{}")
    alias = tmp_path / "alias.json"
    alias.symlink_to(original)
    assert runner._sha256_regular_file(alias) is None
