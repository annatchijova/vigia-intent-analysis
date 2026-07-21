"""B-178 — SIFT database exports must never contaminate source evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.tools.forensic_db import ForensicDatabaseManager, SecurityError


@pytest.fixture
def forensic_db(tmp_path: Path):
    """Build an isolated SQLite source without leaking the global singleton."""
    saved_instance = ForensicDatabaseManager._instance
    ForensicDatabaseManager._instance = None
    manager = ForensicDatabaseManager(str(tmp_path / "work" / "source.db"))
    try:
        yield manager
    finally:
        ForensicDatabaseManager._instance = saved_instance


def test_b178_refuses_sift_export_into_evidence_before_creating_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, forensic_db: ForensicDatabaseManager
) -> None:
    """Derived SQLite must not be written beside immutable source evidence."""
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    target = evidence / "sift-export.db"
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        forensic_db.export_for_sift(str(target))

    assert list(evidence.iterdir()) == []


def test_b178_allows_sift_export_to_external_work_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, forensic_db: ForensicDatabaseManager
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    target = tmp_path / "exports" / "sift-export.db"
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    result = forensic_db.export_for_sift(str(target))

    assert Path(result) == target
    assert target.is_file()
    assert list(evidence.iterdir()) == []


def test_b178_refuses_symlinked_export_parent_that_resolves_into_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, forensic_db: ForensicDatabaseManager
) -> None:
    """Checking only the final filename must not miss a symlinked parent."""
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "export-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        forensic_db.export_for_sift(str(redirect / "sift-export.db"))

    assert list(evidence.iterdir()) == []
