"""B-173 — the MCP bridge must not create operational state in evidence.

``VIGIA_EVIDENCE_DIR`` is an immutable forensic input root.  Importing the
bridge used to create honey-token, quarantine, and mount directories there,
mutating the directory before any tool read an artifact.  Operational state
belongs under a disjoint ``VIGIA_WORK_DIR`` instead.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Without the bridge's MCP dependency the import fails, in-process and in the
# child processes ``_import_bridge`` spawns.  Skipping the module is the honest
# outcome: otherwise ``test_b173_rejects_work_root_nested_in_evidence`` observes
# a non-zero returncode caused by the missing import rather than by the
# rejection it is meant to prove.
pytest.importorskip("mcp.server.fastmcp")

REPO = Path(__file__).resolve().parent.parent


def _import_bridge(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import vigia.vigia_sift_bridge"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def _bridge_env(evidence: Path, work: Path, logs: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": str(REPO),
        "VIGIA_EVIDENCE_DIR": str(evidence),
        "VIGIA_WORK_DIR": str(work),
        "VIGIA_LOG_DIR": str(logs),
    })
    return env


def test_b173_import_leaves_configured_evidence_root_empty(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    logs = tmp_path / "logs"
    evidence.mkdir()

    completed = _import_bridge(_bridge_env(evidence, work, logs))

    assert completed.returncode == 0, completed.stderr
    assert list(evidence.iterdir()) == []
    assert {path.name for path in work.iterdir()} == {
        "honey_tokens", "mounted", "purgatory",
    }


def test_b173_rejects_work_root_nested_in_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    completed = _import_bridge(
        _bridge_env(evidence, evidence / "work", tmp_path / "logs")
    )

    assert completed.returncode != 0
    assert "VIGIA_WORK_DIR" in completed.stderr
    assert list(evidence.iterdir()) == []


def test_b173_mounted_leaf_remains_a_confined_read_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import vigia.vigia_sift_bridge as bridge

    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    mounted = work / "mounted"
    evidence.mkdir()
    mounted.mkdir(parents=True)
    monkeypatch.setattr(bridge, "EVIDENCE_BASE_DIR", str(evidence))
    monkeypatch.setattr(bridge, "WORK_BASE_DIR", str(work))
    monkeypatch.setattr(bridge, "_MOUNT_ROOT", str(mounted))

    target = bridge._sanitize_mount_point("nexus5")

    assert target == str(mounted / "nexus5")
    assert bridge._sanitize_path_local(target) == target
    with pytest.raises(ValueError):
        bridge._sanitize_path_local(str(work / "honey_tokens"))
