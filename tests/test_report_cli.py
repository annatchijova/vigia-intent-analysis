"""python3 -m vigia.report — exit codes and file layout, via subprocess."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.test_report_adapter import make_mcp_doc_kiwi
from tests.test_webui_normalizer import make_agent_doc

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(args: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": REPO,
           "PYTHONHASHSEED": "0"}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, "-m", "vigia.report", *args],
                          capture_output=True, text=True, env=env, cwd=REPO)


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    p = tmp_path / "work" / "KIWI_bundle.json"
    p.parent.mkdir()
    p.write_text(json.dumps(make_mcp_doc_kiwi(), indent=2, sort_keys=True), encoding="utf-8")
    return p


def test_stdout_single_variant(bundle: Path):
    out = _run([str(bundle), "--stdout", "--audience", "junior", "--lang", "es"])
    assert out.returncode == 0, out.stderr
    assert out.stdout.startswith("# Veredicto VIGÍA")
    assert "**SUSPICION**" in out.stdout
    assert list(bundle.parent.iterdir()) == [bundle], "--stdout must not write files"


def test_stdout_requires_single_variant(bundle: Path):
    out = _run([str(bundle), "--stdout"])
    assert out.returncode == 2
    assert "--stdout needs exactly one" in out.stderr


def test_writes_all_four_next_to_bundle(bundle: Path):
    out = _run([str(bundle)])
    assert out.returncode == 0, out.stderr
    names = sorted(p.name for p in bundle.parent.iterdir())
    assert names == [
        "KIWI_bundle.json",
        "KIWI_bundle_report_expert_en.md", "KIWI_bundle_report_expert_es.md",
        "KIWI_bundle_report_junior_en.md", "KIWI_bundle_report_junior_es.md",
    ]
    printed = sorted(Path(l).name for l in out.stdout.splitlines() if l.strip())
    assert printed == names[1:]


def test_output_dir_and_subset(bundle: Path, tmp_path: Path):
    out_dir = tmp_path / "reports"
    out = _run([str(bundle), "--audience", "expert", "--lang", "en", "--output-dir", str(out_dir)])
    assert out.returncode == 0, out.stderr
    assert sorted(p.name for p in out_dir.iterdir()) == ["KIWI_bundle_report_expert_en.md"]
    assert list(bundle.parent.iterdir()) == [bundle]


def test_refuses_evidence_dir(bundle: Path, tmp_path: Path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    out = _run([str(bundle), "--output-dir", str(evidence)],
               env_extra={"VIGIA_EVIDENCE_DIR": str(evidence)})
    assert out.returncode == 1
    assert "refused" in out.stderr and "VIGIA_EVIDENCE_DIR" in out.stderr
    assert list(evidence.iterdir()) == []


def test_unreadable_bundle_exit_1(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    out = _run([str(bad)])
    assert out.returncode == 1
    assert "cannot read bundle" in out.stderr
    missing = _run([str(tmp_path / "missing.json")])
    assert missing.returncode == 1


def test_usage_error_exit_2(bundle: Path):
    assert _run([str(bundle), "--audience", "manager"]).returncode == 2
    assert _run([]).returncode == 2


def test_agent_bundle_via_cli_is_deterministic(tmp_path: Path):
    p = tmp_path / "AGENT_bundle.json"
    p.write_text(json.dumps(make_agent_doc(), indent=2, sort_keys=True), encoding="utf-8")
    a = _run([str(p), "--stdout", "--audience", "expert", "--lang", "en"])
    b = _run([str(p), "--stdout", "--audience", "expert", "--lang", "en"],
             env_extra={"PYTHONHASHSEED": "7", "TZ": "Asia/Tokyo"})
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout
    assert "`53/100`" in a.stdout
