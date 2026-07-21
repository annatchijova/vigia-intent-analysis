"""An allowed but oversized API fixture must not masquerade as missing."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi import HTTPException

from vigia.api_payload import MAX_CASE_JSON_BYTES


WRAPPERS = ("vigia_api", "vigia.vigia_api")


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_analyze_path_reports_declared_size_rejection_not_not_found(
    tmp_path, monkeypatch, wrapper
):
    module = importlib.import_module(wrapper)
    repo = tmp_path / "repo"
    case_dir = repo / "data" / "cases"
    case_dir.mkdir(parents=True)
    (case_dir / "oversized.json").write_bytes(
        b'{"case_id":"oversized","padding":"'
        + (b"x" * MAX_CASE_JSON_BYTES)
        + b'"}'
    )
    monkeypatch.setattr(module, "REPO", repo)

    def must_not_run(_path):
        raise AssertionError("oversized fixture reached the scorer")

    monkeypatch.setattr(module, "_run_pipeline", must_not_run)

    with pytest.raises(HTTPException) as error:
        module.analyze_by_path(
            module.CasePath(case_path="data/cases/oversized.json")
        )

    assert error.value.status_code == 422
    assert "byte api limit" in error.value.detail.lower()
