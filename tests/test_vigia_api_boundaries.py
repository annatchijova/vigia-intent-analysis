"""Regression tests for the two local FastAPI wrapper boundaries.

The tests call endpoint functions directly with inert pipeline/narration stubs;
they never bind a socket or inspect a non-fixture file.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi import HTTPException


WRAPPERS = ("vigia_api", "vigia.vigia_api")


@pytest.fixture(params=WRAPPERS)
def api_module(request):
    return importlib.import_module(request.param)


def _fixture_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    case_dir = repo / "data" / "cases"
    case_dir.mkdir(parents=True)
    allowed = case_dir / "allowed.json"
    allowed.write_text('{"case_id": "fixture", "artifacts": []}')
    return repo, allowed


def _install_inert_pipeline(monkeypatch, module):
    monkeypatch.setattr(module, "_run_pipeline", lambda path: {"verdict": "NOISE"})
    monkeypatch.setattr(module, "_run_narrative", lambda path: "")


def test_analyze_path_accepts_regular_json_case_inside_declared_roots(
    tmp_path, monkeypatch, api_module
):
    repo, allowed = _fixture_repo(tmp_path)
    monkeypatch.setattr(api_module, "REPO", repo)
    _install_inert_pipeline(monkeypatch, api_module)

    result = api_module.analyze_by_path(
        api_module.CasePath(case_path="data/cases/allowed.json")
    )

    assert result["verdict"] == "NOISE"
    assert result["case"] == allowed.name


@pytest.mark.parametrize("requested", ["../outside.json", "data/cases/../allowed.json"])
def test_analyze_path_rejects_parent_traversal(tmp_path, monkeypatch, api_module, requested):
    repo, _ = _fixture_repo(tmp_path)
    monkeypatch.setattr(api_module, "REPO", repo)
    _install_inert_pipeline(monkeypatch, api_module)

    with pytest.raises(HTTPException) as error:
        api_module.analyze_by_path(api_module.CasePath(case_path=requested))

    assert error.value.status_code == 404


def test_analyze_path_rejects_absolute_and_prefix_escape(tmp_path, monkeypatch, api_module):
    repo, _ = _fixture_repo(tmp_path)
    outside_root = tmp_path / "repo-neighbor"
    outside_root.mkdir()
    outside = outside_root / "outside.json"
    outside.write_text('{"case_id": "outside", "artifacts": []}')
    monkeypatch.setattr(api_module, "REPO", repo)
    _install_inert_pipeline(monkeypatch, api_module)

    for requested in (str(outside), "repo-neighbor/outside.json"):
        with pytest.raises(HTTPException) as error:
            api_module.analyze_by_path(api_module.CasePath(case_path=requested))
        assert error.value.status_code == 404


def test_analyze_path_rejects_symlink_directory_and_wrong_extension(
    tmp_path, monkeypatch, api_module
):
    repo, allowed = _fixture_repo(tmp_path)
    case_dir = allowed.parent
    outside = tmp_path / "outside.json"
    outside.write_text('{"case_id": "outside", "artifacts": []}')
    link = case_dir / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable in this test environment: {exc}")
    (case_dir / "directory.json").mkdir()
    (case_dir / "wrong-extension.txt").write_text("fixture")
    monkeypatch.setattr(api_module, "REPO", repo)
    _install_inert_pipeline(monkeypatch, api_module)

    for requested in (
        "data/cases/linked.json",
        "data/cases/directory.json",
        "data/cases/wrong-extension.txt",
    ):
        with pytest.raises(HTTPException) as error:
            api_module.analyze_by_path(api_module.CasePath(case_path=requested))
        assert error.value.status_code == 404


@pytest.mark.parametrize("payload", ["42", "null", "[]"])
def test_openai_chat_degrades_scalar_or_list_json_to_usage_guidance(payload):
    root_api = importlib.import_module("vigia_api")

    response = root_api.chat_completions(
        root_api.ChatRequest(messages=[{"role": "user", "content": payload}])
    )

    content = response["choices"][0]["message"]["content"]
    assert "VIGÍA" in content
    assert "artifacts" in content


def test_openai_chat_still_runs_only_object_case_with_artifacts(monkeypatch):
    root_api = importlib.import_module("vigia_api")
    monkeypatch.setattr(root_api, "_run_pipeline", lambda path: {
        "verdict": "ABSTAIN", "score": 0.0, "confidence": 0.0,
        "reason": "fixture", "bundle_hash": "fixture", "verify": "PASS", "pipeline_ms": 1,
    })
    monkeypatch.setattr(root_api, "_run_narrative", lambda path: "")

    response = root_api.chat_completions(root_api.ChatRequest(messages=[{
        "role": "user", "content": '{"case_id": "fixture", "artifacts": []}',
    }]))

    assert "ABSTAIN" in response["choices"][0]["message"]["content"]


def test_packaged_api_defaults_to_checkout_root_without_environment_override(monkeypatch):
    monkeypatch.delenv("VIGIA_REPO", raising=False)
    package_api = importlib.reload(importlib.import_module("vigia.vigia_api"))

    assert package_api.REPO == Path(package_api.__file__).resolve().parent.parent
