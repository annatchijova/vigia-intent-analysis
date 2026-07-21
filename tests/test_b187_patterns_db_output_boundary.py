"""B-187 — pattern-db initialization must never mutate source evidence."""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from vigia.security.output_boundary import SecurityError
from vigia.tools.init_patterns_db import init_db


def test_b187_refuses_pattern_database_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        init_db(str(evidence / "forensic_patterns.sqlite"))

    assert list(evidence.iterdir()) == []


def test_b187_refuses_pattern_database_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "patterns-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        init_db(str(redirect / "forensic_patterns.sqlite"))

    assert list(evidence.iterdir()) == []


def test_b187_allows_external_pattern_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "private-work" / "forensic_patterns.sqlite"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    init_db(str(target))

    assert target.is_file()
    with sqlite3.connect(target) as connection:
        count = connection.execute("SELECT COUNT(*) FROM nlp_patterns").fetchone()[0]
    assert count > 0
    assert list(evidence.iterdir()) == []


def test_b187_documented_direct_script_invocation_remains_available() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "vigia/tools/init_patterns_db.py", "--help"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--db" in result.stdout
