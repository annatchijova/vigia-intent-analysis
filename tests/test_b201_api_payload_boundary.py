"""Availability boundary for untrusted JSON supplied through the HTTP APIs."""

from __future__ import annotations

import importlib
import json

import pytest
from fastapi import HTTPException
from vigia.api_payload import MAX_CASE_JSON_BYTES


WRAPPERS = ("vigia_api", "vigia.vigia_api")


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_analyze_json_rejects_excessive_artifact_cardinality_before_pipeline(
    monkeypatch, wrapper
):
    module = importlib.import_module(wrapper)

    def must_not_run(_path):
        raise AssertionError("oversized request reached the scorer")

    monkeypatch.setattr(module, "_run_pipeline", must_not_run)
    payload = module.CasePayload(case_data={"artifacts": [{}] * 1025})

    with pytest.raises(HTTPException) as error:
        module.analyze_by_json(payload)

    assert error.value.status_code == 422
    assert "artifact" in error.value.detail.lower()


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_openai_compat_rejects_excessive_case_before_writing_or_scoring(
    monkeypatch, wrapper
):
    module = importlib.import_module(wrapper)

    def must_not_run(_path):
        raise AssertionError("oversized chat request reached the scorer")

    monkeypatch.setattr(module, "_run_pipeline", must_not_run)
    response = module.chat_completions(module.ChatRequest(messages=[{
        "role": "user",
        "content": json.dumps({"artifacts": [{}] * 1025}),
    }]))

    content = response["choices"][0]["message"]["content"].lower()
    assert "artifact" in content
    assert "limit" in content


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_analyze_json_rejects_oversized_serialized_case_before_pipeline(
    monkeypatch, wrapper
):
    module = importlib.import_module(wrapper)

    def must_not_run(_path):
        raise AssertionError("oversized request reached the scorer")

    monkeypatch.setattr(module, "_run_pipeline", must_not_run)
    payload = module.CasePayload(case_data={"notes": "x" * MAX_CASE_JSON_BYTES})

    with pytest.raises(HTTPException) as error:
        module.analyze_by_json(payload)

    assert error.value.status_code == 422
    assert "byte" in error.value.detail.lower()
