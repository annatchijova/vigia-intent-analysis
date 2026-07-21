"""B-185 — operational SQLite state must never default into evidence."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.security.output_boundary import SecurityError
from vigia.tools import forensic_db as fdb


@pytest.fixture(autouse=True)
def _isolated_forensic_db_singleton():
    """The manager is process-global; keep each boundary probe independent."""
    saved = fdb.ForensicDatabaseManager._instance
    fdb.ForensicDatabaseManager._instance = None
    try:
        yield
    finally:
        fdb.ForensicDatabaseManager._instance = saved


def test_b185_refuses_explicit_operational_db_inside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="evidence"):
        fdb.ForensicDatabaseManager(str(evidence / "vigia_forensic.db"))

    assert list(evidence.iterdir()) == []


def test_b185_refuses_operational_db_through_symlinked_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    redirect = tmp_path / "db-redirect"
    evidence.mkdir()
    redirect.symlink_to(evidence, target_is_directory=True)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    with pytest.raises(SecurityError, match="symlink|evidence"):
        fdb.ForensicDatabaseManager(str(redirect / "vigia_forensic.db"))

    assert list(evidence.iterdir()) == []


def test_b185_default_uses_work_dir_not_legacy_evidence_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_EVIDENCE_PATH", str(evidence))
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.delenv("VIGIA_FORENSIC_DB_PATH", raising=False)

    manager = fdb.ForensicDatabaseManager()

    assert Path(manager.db_path) == work / "vigia_forensic.db"
    assert Path(manager.db_path).is_file()
    assert list(evidence.iterdir()) == []


def test_b185_allows_explicit_external_operational_db(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    target = tmp_path / "work" / "vigia_forensic.db"
    evidence.mkdir()
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))

    manager = fdb.ForensicDatabaseManager(str(target))

    assert Path(manager.db_path) == target
    assert target.is_file()
    assert list(evidence.iterdir()) == []
