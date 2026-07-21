"""B-190 — execution logs are derived artifacts, never source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.core.execution_logger import VigiaExecutionLogger
from vigia.security.output_boundary import SecurityError


def test_b190_refuses_execution_log_directory_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        VigiaExecutionLogger("B190-001", output_dir=str(evidence))

    assert list(evidence.iterdir()) == []


def test_b190_refuses_execution_log_directory_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "log-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        VigiaExecutionLogger("B190-002", output_dir=str(redirect))

    assert list(evidence.iterdir()) == []


def test_b190_refuses_case_id_traversal_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(ValueError, match="case_id"):
        VigiaExecutionLogger("../evidence/escape", output_dir=str(work))

    assert list(evidence.iterdir()) == []


def test_b190_default_execution_log_uses_work_dir_even_from_evidence_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    evidence.mkdir()
    monkeypatch.chdir(evidence)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.delenv("VIGIA_EXECUTION_LOG_DIR", raising=False)

    logger = VigiaExecutionLogger("B190-003")

    assert Path(logger.log_file) == work / "logs" / "B190-003_execution.jsonl"
    assert Path(logger.log_file).is_file()
    assert list(evidence.iterdir()) == []


def test_b190_allows_external_execution_log_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target_dir = tmp_path / "private-work" / "logs"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    logger = VigiaExecutionLogger("B190-004", output_dir=str(target_dir))
    logger.log_abstain("FIXTURE", "boundary check")

    assert Path(logger.log_file).is_file()
    assert Path(logger.log_file).parent == target_dir
    assert list(evidence.iterdir()) == []
