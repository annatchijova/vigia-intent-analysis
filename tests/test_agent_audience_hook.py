"""vigia_agent.py --audience: presentation siblings written after the seal.

Contract (same as the reasoning-trace sibling, vigia_agent.py main()):
  * written LAST, next to the bundle, as <stem>_report_<audience>_<lang>.md;
  * the bundle bytes and the .sha256 sidecar are exactly what they would be
    without the flag (the reports live outside the seal);
  * VIGIA_AUDIENCE_REPORTS_ENABLED=false skips the step;
  * fail-soft: a writer failure is logged and the agent still exits with the
    verdict's exit code, bundle intact.

End-to-end runs use the subprocess pattern of
tests/test_b105_decimal_serialization.py (output inside the repo because the
agent's PathGuard refuses paths outside its working directory).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import vigia_agent
from tests.test_report_adapter import make_mcp_doc_kiwi

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASE = os.path.join(REPO_ROOT, "data", "cases", "FF-GENUINE-001.json")

SIBLINGS = [
    "_report_junior_en.md", "_report_junior_es.md",
    "_report_expert_en.md", "_report_expert_es.md",
]


# ---------------------------------------------------------------------------
# Unit: the hook function
# ---------------------------------------------------------------------------

def _bundle_file(tmp_path: Path) -> Path:
    p = tmp_path / "CASE_bundle.json"
    p.write_text(json.dumps(make_mcp_doc_kiwi(), indent=2, sort_keys=True), encoding="utf-8")
    return p


def test_hook_writes_four_siblings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("VIGIA_AUDIENCE_REPORTS_ENABLED", raising=False)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path / "evidence"))
    bundle = _bundle_file(tmp_path)
    before = bundle.read_bytes()

    written = vigia_agent._write_audience_reports(str(bundle), "all", "all")

    assert [Path(p).name for p in written] == ["CASE_bundle" + s for s in SIBLINGS]
    assert all(Path(p).exists() for p in written)
    assert bundle.read_bytes() == before


def test_hook_single_audience_and_lang(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path / "evidence"))
    bundle = _bundle_file(tmp_path)
    written = vigia_agent._write_audience_reports(str(bundle), "junior", "es")
    assert [Path(p).name for p in written] == ["CASE_bundle_report_junior_es.md"]


def test_hook_kill_switch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VIGIA_AUDIENCE_REPORTS_ENABLED", "false")
    bundle = _bundle_file(tmp_path)
    assert vigia_agent._write_audience_reports(str(bundle), "all", "all") == []
    assert sorted(p.name for p in tmp_path.iterdir()) == ["CASE_bundle.json"]


def test_hook_is_fail_soft(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import vigia.report.writer as writer

    def boom(*_a, **_k):
        raise RuntimeError("simulated writer failure")

    monkeypatch.delenv("VIGIA_AUDIENCE_REPORTS_ENABLED", raising=False)
    monkeypatch.setattr(writer, "write_all", boom)
    bundle = _bundle_file(tmp_path)
    assert vigia_agent._write_audience_reports(str(bundle), "all", "all") == []
    assert sorted(p.name for p in tmp_path.iterdir()) == ["CASE_bundle.json"]


def test_hook_refuses_evidence_dir_without_raising(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """The boundary refusal is swallowed (fail-soft) and nothing lands in evidence."""
    monkeypatch.delenv("VIGIA_AUDIENCE_REPORTS_ENABLED", raising=False)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path))
    bundle = _bundle_file(tmp_path)
    assert vigia_agent._write_audience_reports(str(bundle), "all", "all") == []
    assert sorted(p.name for p in tmp_path.iterdir()) == ["CASE_bundle.json"]


# ---------------------------------------------------------------------------
# End to end: the real agent, with and without the flag
# ---------------------------------------------------------------------------

def _run_agent(out: str, extra: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("VIGIA_EVIDENCE_DIR", None)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "vigia_agent.py"),
         "--evidence", CASE, "--case-id", "FF-GENUINE-001", "--output", out, *extra],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=180, env=env,
    )


def _cleanup(out: str) -> None:
    stem = out[:-5]
    for leftover in [out, out + ".sha256", stem + "_reasoning_trace.json"] + [stem + s for s in SIBLINGS]:
        if os.path.exists(leftover):
            os.unlink(leftover)


@pytest.mark.skipif(not os.path.isfile(CASE), reason="corpus case not present")
def test_agent_audience_all_writes_siblings_after_the_seal():
    out = os.path.join(REPO_ROOT, "audience_hook_tmp_bundle.json")
    _cleanup(out)
    try:
        proc = _run_agent(out, ["--audience", "all"])
        assert os.path.isfile(out), proc.stderr[-800:]
        stem = out[:-5]
        for s in SIBLINGS:
            assert os.path.isfile(stem + s), (s, proc.stderr[-800:])

        # Sidecar attests exactly the bytes on disk; the reports bind to them.
        disk_digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
        assert open(out + ".sha256", encoding="utf-8").read().split()[0] == disk_digest
        for s in SIBLINGS:
            text = open(stem + s, encoding="utf-8").read()
            assert disk_digest in text
            assert "**MALICE**" in text or "MALICE" in text

        bundle = json.load(open(out, encoding="utf-8"))
        assert bundle["agent_verdict"] == "MALICE"
        assert proc.returncode == 1  # MALICE exit code, unchanged by the flag
        assert "audience report" not in json.dumps(bundle), "nothing about reports inside the seal"
    finally:
        _cleanup(out)


@pytest.mark.skipif(not os.path.isfile(CASE), reason="corpus case not present")
def test_agent_default_writes_no_siblings_and_kill_switch_holds():
    out = os.path.join(REPO_ROOT, "audience_hook_tmp2_bundle.json")
    _cleanup(out)
    try:
        proc = _run_agent(out, [])
        assert os.path.isfile(out), proc.stderr[-800:]
        stem = out[:-5]
        assert not any(os.path.exists(stem + s) for s in SIBLINGS), "default must stay opt-in"
        _cleanup(out)

        proc = _run_agent(out, ["--audience", "all"], {"VIGIA_AUDIENCE_REPORTS_ENABLED": "false"})
        assert os.path.isfile(out), proc.stderr[-800:]
        assert not any(os.path.exists(stem + s) for s in SIBLINGS), "kill switch ignored"
        assert proc.returncode == 1
    finally:
        _cleanup(out)
