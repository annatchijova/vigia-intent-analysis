"""Regression contract for the two supported FastAPI import paths.

Both ``vigia_api`` and ``vigia.vigia_api`` describe themselves as the VIGÍA
OpenWebUI gateway.  A caller must not get a weaker protocol or browser
boundary merely by choosing the package import path.
"""

from __future__ import annotations

import importlib

import pytest
from fastapi.middleware.cors import CORSMiddleware


WRAPPERS = ("vigia_api", "vigia.vigia_api")
OPENAI_COMPATIBLE_PATHS = {"/v1/models", "/v1/chat/completions"}


def _paths(module) -> set[str]:
    return {route.path for route in module.app.routes}


def _cors_origins(module) -> list[str]:
    middleware = next(
        entry for entry in module.app.user_middleware if entry.cls is CORSMiddleware
    )
    return list(middleware.kwargs["allow_origins"])


def test_all_documented_api_import_paths_expose_openai_compatibility_contract():
    for wrapper in WRAPPERS:
        module = importlib.import_module(wrapper)
        assert OPENAI_COMPATIBLE_PATHS <= _paths(module)


def test_all_documented_api_import_paths_reject_wildcard_browser_origins_by_default():
    for wrapper in WRAPPERS:
        module = importlib.import_module(wrapper)
        assert "*" not in _cors_origins(module)


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_openai_chat_contract_executes_the_wrapper_local_pipeline(monkeypatch, wrapper):
    module = importlib.import_module(wrapper)
    monkeypatch.setattr(
        module,
        "_run_pipeline",
        lambda _path: {
            "verdict": "ABSTAIN",
            "score": 0.0,
            "confidence": 0.0,
            "reason": "fixture",
            "bundle_hash": "fixture",
            "verify": "PASS",
            "pipeline_ms": 1,
        },
    )
    monkeypatch.setattr(module, "_run_narrative", lambda _path: "")

    response = module.chat_completions(module.ChatRequest(messages=[{
        "role": "user", "content": '{"case_id": "fixture", "artifacts": []}',
    }]))

    assert "ABSTAIN" in response["choices"][0]["message"]["content"]
