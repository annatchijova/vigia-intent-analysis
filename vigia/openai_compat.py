"""Shared, deliberately narrow OpenAI-compatible chat surface for VIGÍA.

The HTTP wrappers own evidence-root configuration and pipeline execution.  This
module owns only the protocol translation needed by OpenWebUI, so the two
supported import paths cannot silently expose different chat capabilities.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


class ChatRequest(BaseModel):
    model: str = "vigia-forensic"
    messages: list
    stream: bool = False


def _usage_guidance() -> str:
    """Return protocol help without treating malformed input as a case."""
    return (
        "**VIGÍA Forensic Intelligence API**\n\n"
        "Para analizar un caso, enviá el JSON objeto del caso completo como mensaje "
        "(debe incluir `artifacts`).\n\n"
        "O usá los endpoints directos:\n"
        "- `POST /analyze/path` — caso existente por nombre\n"
        "- `POST /analyze/json` — caso como JSON en el body\n"
        "- `GET /cases` — listar casos disponibles\n"
        "- `GET /health` — estado del sistema"
    )


def install_openai_compatibility(
    app: FastAPI,
    *,
    run_pipeline: Callable[[Path], dict],
    run_narrative: Callable[[Path], str],
):
    """Install the exact OpenAI-compatible surface required by OpenWebUI.

    Callables are supplied lazily by each wrapper.  That preserves each
    wrapper's configured repository root and lets boundary tests replace the
    expensive pipeline without mutating this protocol module.
    """

    @app.get("/v1/models")
    def list_models():
        """OpenWebUI calls this endpoint to discover the available model."""
        return {
            "object": "list",
            "data": [
                {
                    "id": "vigia-forensic",
                    "object": "model",
                    "owned_by": "vigia",
                    "created": 1716000000,
                }
            ],
        }

    @app.post("/v1/chat/completions")
    def chat_completions(req: ChatRequest):
        """Translate an OpenAI chat request to a bounded VIGÍA case analysis."""
        user_messages = [
            message
            for message in req.messages
            if (
                (isinstance(message, dict) and message.get("role") == "user")
                or (hasattr(message, "role") and message.role == "user")
            )
        ]
        if not user_messages:
            content = "No se recibió mensaje de usuario."
        else:
            last = user_messages[-1]
            text = last.get("content", "") if isinstance(last, dict) else last.content
            try:
                case_data = json.loads(text)
                if not isinstance(case_data, dict):
                    content = _usage_guidance()
                elif "artifacts" not in case_data:
                    content = (
                        "VIGÍA recibió JSON sin campo `artifacts`. "
                        "Enviá un caso forense con estructura `{\"artifacts\": [...]}` "
                        "o usá `/analyze/path` con el nombre de un caso existente."
                    )
                else:
                    temporary_case = tempfile.NamedTemporaryFile(
                        suffix=".json", delete=False, mode="w"
                    )
                    json.dump(case_data, temporary_case)
                    temporary_case.close()
                    try:
                        result = run_pipeline(Path(temporary_case.name))
                        try:
                            narrative = run_narrative(Path(temporary_case.name))
                        except Exception:
                            narrative = ""
                        content = (
                            "**VIGÍA — Análisis Forense**\n\n"
                            f"**Veredicto:** {result.get('verdict', 'UNKNOWN')}\n"
                            f"**Score:** {result.get('score', 0.0):.4f} | "
                            f"**Confianza:** {result.get('confidence', 0.0):.2f}\n"
                            f"**Razón:** {result.get('reason', '')}\n"
                            f"**Bundle hash:** `{result.get('bundle_hash', 'N/A')}`\n"
                            f"**Verificación EBS:** {result.get('verify', 'N/A')}\n"
                            f"**Veredicto forense sellado:** "
                            f"{result.get('sealed_forensic_verdict', 'N/A')}\n"
                            f"**Decisión EBS:** {result.get('ebs_decision', 'N/A')}\n"
                            f"**Alcance del sello:** {result.get('seal_scope', 'N/A')}\n"
                            f"**Pipeline:** {result.get('pipeline_ms', 0)}ms\n"
                        )
                        if narrative:
                            content += f"\n**Análisis Peirciano:**\n{narrative}"
                    except Exception:
                        content = "Error interno en pipeline forense. Contacte al administrador."
                    finally:
                        try:
                            os.unlink(temporary_case.name)
                        except Exception:
                            pass
            except (json.JSONDecodeError, TypeError, ValueError):
                content = _usage_guidance()

        return {
            "id": f"vigia-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    return list_models, chat_completions
