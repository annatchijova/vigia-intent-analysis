"""B-194: the API must bind its case inspection to the verified directory tree.

``resolve_case_path`` correctly rejects a symlink it can see.  That alone is
not sufficient: an actor who can mutate a case root concurrently could replace
the leaf (or the ``cases`` directory) after that inspection and before the
pipeline opens the returned path.  The API must create its input snapshot via
directory descriptors, not by reopening the previously checked pathname.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import vigia.api_case_paths as case_paths


def _case_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    case_root = repo / "data" / "cases"
    case_root.mkdir(parents=True)
    (case_root / "allowed.json").write_text(
        '{"case_id":"allowed","artifacts":[]}', encoding="utf-8"
    )
    return repo, case_root


def test_snapshot_refuses_leaf_swapped_to_symlink_after_path_validation(
    tmp_path, monkeypatch
):
    repo, case_root = _case_repo(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text('{"case_id":"outside","artifacts":[]}', encoding="utf-8")
    original_resolver = case_paths.resolve_case_path

    def replace_after_resolution(root: Path, requested: str) -> Path:
        candidate = original_resolver(root, requested)
        candidate.unlink()
        candidate.symlink_to(outside)
        return candidate

    monkeypatch.setattr(case_paths, "resolve_case_path", replace_after_resolution)

    with pytest.raises(case_paths.CasePathError):
        with case_paths.snapshot_case_file(repo, "data/cases/allowed.json"):
            pytest.fail("a symlink substituted after validation must never open")


def test_snapshot_refuses_case_root_swapped_to_symlink_after_path_validation(
    tmp_path, monkeypatch
):
    repo, case_root = _case_repo(tmp_path)
    outside_root = tmp_path / "outside-cases"
    outside_root.mkdir()
    (outside_root / "allowed.json").write_text(
        '{"case_id":"outside","artifacts":[]}', encoding="utf-8"
    )
    original_resolver = case_paths.resolve_case_path

    def replace_after_resolution(root: Path, requested: str) -> Path:
        candidate = original_resolver(root, requested)
        replacement = case_root.with_name("cases-original")
        case_root.rename(replacement)
        case_root.symlink_to(outside_root, target_is_directory=True)
        return candidate

    monkeypatch.setattr(case_paths, "resolve_case_path", replace_after_resolution)

    with pytest.raises(case_paths.CasePathError):
        with case_paths.snapshot_case_file(repo, "data/cases/allowed.json"):
            pytest.fail("a directory symlink substituted after validation must never open")


def test_snapshot_preserves_regular_case_bytes_in_private_temporary_file(tmp_path):
    repo, _ = _case_repo(tmp_path)

    with case_paths.snapshot_case_file(repo, "data/cases/allowed.json") as snapshot:
        assert snapshot.suffix == ".json"
        assert snapshot.parent != repo / "data" / "cases"
        assert json.loads(snapshot.read_text(encoding="utf-8"))["case_id"] == "allowed"

    assert not snapshot.exists()
