"""Availability boundary for descriptor-bound API case snapshots."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

import vigia.api_case_paths as case_paths
from vigia.api_payload import MAX_CASE_JSON_BYTES


def _oversized_case_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    case_dir = repo / "data" / "cases"
    case_dir.mkdir(parents=True)
    (case_dir / "oversized.json").write_bytes(
        b'{"case_id":"oversized","padding":"'
        + (b"x" * MAX_CASE_JSON_BYTES)
        + b'"}'
    )
    return repo


def test_snapshot_rejects_oversized_fixture_before_creating_a_tempfile(
    tmp_path, monkeypatch
):
    repo = _oversized_case_repo(tmp_path)

    def must_not_create_tempfile(*_args, **_kwargs):
        raise AssertionError("oversized case reached temporary-file creation")

    monkeypatch.setattr(case_paths.tempfile, "NamedTemporaryFile", must_not_create_tempfile)

    with pytest.raises(case_paths.CasePathError, match="byte API limit"):
        with case_paths.snapshot_case_file(repo, "data/cases/oversized.json"):
            pytest.fail("an oversized repository case must not be snapshotted")


def test_bounded_copy_rejects_post_open_growth_without_extending_snapshot():
    source = BytesIO(b"x" * (MAX_CASE_JSON_BYTES + 1))
    target = BytesIO()

    with pytest.raises(case_paths.CasePathError, match="byte API limit"):
        case_paths._copy_case_snapshot_bounded(source, target)

    assert len(target.getvalue()) == MAX_CASE_JSON_BYTES
