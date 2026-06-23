#!/usr/bin/env python3
# Copyright 2026 Anna Tchijova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
VIGÍA API — FastAPI wrapper para OpenWebUI.
Expone el pipeline real (run_vigia_full.py + vigia_ask.sh) como endpoints REST.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(os.environ.get("VIGIA_REPO", Path(__file__).parent))
sys.path.insert(0, str(REPO))

app = FastAPI(title="VIGÍA Forensic Intelligence API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["https://your-openwebui-domain.com"], allow_methods=["*"], allow_headers=["*"])


class CasePayload(BaseModel):
    case_data: dict


class CasePath(BaseModel):
    case_path: str


def _run_pipeline(case_path: Path) -> dict:
    """Corre el scorer forense + pipeline EBS v1 para bundle hash."""
    import time, subprocess as _sub, tempfile as _tmp
    # Scorer forense (mismo que run_vigia_case.py)
    from vigia_scorer import _vigia_score, _normalize_case
    from vigia.pipeline.vigia_integration_bridge import CaseAdapter, normalize_case_schema, validate_case_schema
    from vigia.pipeline.pipeline import VigiaPipeline

    with open(case_path) as f:
        case = json.load(f)
    case_norm = _normalize_case(case)

    t0 = time.perf_counter()
    score = _vigia_score(case_norm)

    # Pipeline EBS v1 para bundle hash
    case_ebs = normalize_case_schema(dict(case))
    validate_case_schema(case_ebs)
    adapter = CaseAdapter()
    signals, _ = adapter.to_signals(case_ebs)
    drift = CaseAdapter.compute_drift(case_ebs)
    result = VigiaPipeline().run_full(signals=signals, drift_score=drift)
    elapsed = (time.perf_counter() - t0) * 1000

    sd = result.get("sealed_dict", {})
    integ = sd.get("integrity", {})
    bh = integ.get("bundle_hash", "N/A")
    ts = integ.get("sealed_at", sd.get("timestamp", "N/A"))

    tf = _tmp.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(sd, tf, sort_keys=True, indent=2, default=str)
    tf.close()
    v = _sub.run(["python3", str(REPO / "forensics/verify_ebs_v1.py"), tf.name],
                  capture_output=True, text=True)
    verif = "PASS" if "PASS" in v.stdout else "FAIL"
    level = next((l for l in ["Level 3", "Level 2", "Level 1"] if l in v.stdout), "?")
    os.unlink(tf.name)

    return {
        "verdict":     score["verdict"],
        "score":       score["score"],
        "confidence":  score["confidence"],
        "reason":      score["reason"],
        "bundle_hash": bh,
        "timestamp":   ts,
        "verify":      f"{verif} — {level}",
        "pipeline_ms": round(elapsed, 1),
    }


def _run_narrative(case_path: Path) -> str:
    """Corre vigia_ask.sh (Ollama) y retorna el texto narrativo."""
    ask_sh = REPO / "scripts/vigia_ask.sh"
    if not ask_sh.exists():
        return ""
    r = subprocess.run(["bash", str(ask_sh), str(case_path)],
                       capture_output=True, text=True, timeout=300)
    out = r.stdout
    if "...done thinking." in out:
        out = out.split("...done thinking.")[-1].strip()
    return out


@app.get("/health")
def health():
    return {"status": "VIGÍA operativo", "repo": str(REPO)}


# ---------------------------------------------------------------------------
# Shim OpenAI-compatible — requerido por OpenWebUI
# OpenWebUI espera /v1/models y /v1/chat/completions.
# Estos endpoints traducen el protocolo de chat al pipeline forense VIGÍA.
# ---------------------------------------------------------------------------

@app.get("/v1/models")
def list_models():
    """OpenWebUI llama esto al conectar para descubrir modelos disponibles."""
    return {
        "object": "list",
        "data": [
            {
                "id":       "vigia-forensic",
                "object":   "model",
                "owned_by": "vigia",
                "created":  1716000000,
            }
        ],
    }


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "vigia-forensic"
    messages: list
    stream: bool = False


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    """
    Endpoint OpenAI-compatible para OpenWebUI.

    El último mensaje del usuario se interpreta como:
    - Si contiene JSON válido con campo 'artifacts': se analiza como caso forense.
    - En cualquier otro caso: se responde con instrucciones de uso.
    """
    import time

    # Extraer el último mensaje del usuario
    user_messages = [m for m in req.messages if (
        (isinstance(m, dict) and m.get("role") == "user") or
        (hasattr(m, "role") and m.role == "user")
    )]
    if not user_messages:
        content = "No se recibió mensaje de usuario."
    else:
        last = user_messages[-1]
        text = last.get("content", "") if isinstance(last, dict) else last.content

        # Intentar parsear como caso forense JSON
        try:
            case_data = json.loads(text)
            if "artifacts" in case_data:
                tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
                json.dump(case_data, tf)
                tf.close()
                try:
                    result = _run_pipeline(Path(tf.name))
                    try:
                        narrative = _run_narrative(Path(tf.name))
                    except Exception:
                        narrative = ""
                    verdict  = result.get("verdict", "UNKNOWN")
                    score    = result.get("score", 0.0)
                    conf     = result.get("confidence", 0.0)
                    reason   = result.get("reason", "")
                    bh       = result.get("bundle_hash", "N/A")
                    verify   = result.get("verify", "N/A")
                    ms       = result.get("pipeline_ms", 0)
                    content  = (
                        f"**VIGÍA — Análisis Forense**\n\n"
                        f"**Veredicto:** {verdict}\n"
                        f"**Score:** {score:.4f} | **Confianza:** {conf:.2f}\n"
                        f"**Razón:** {reason}\n"
                        f"**Bundle hash:** `{bh}`\n"
                        f"**Verificación EBS:** {verify}\n"
                        f"**Pipeline:** {ms}ms\n"
                    )
                    if narrative:
                        content += f"\n**Análisis Peirciano:**\n{narrative}"
                except Exception as e:
                    content = "Error interno en pipeline forense. Contacte al administrador."
                finally:
                    try:
                        os.unlink(tf.name)
                    except Exception:
                        pass
            else:
                content = (
                    "VIGÍA recibió JSON sin campo `artifacts`. "
                    "Enviá un caso forense con estructura `{\"artifacts\": [...]}` "
                    "o usá `/analyze/path` con el nombre de un caso existente."
                )
        except (json.JSONDecodeError, ValueError):
            content = (
                "**VIGÍA Forensic Intelligence API**\n\n"
                "Para analizar un caso, enviá el JSON del caso completo como mensaje.\n\n"
                "O usá los endpoints directos:\n"
                "- `POST /analyze/path` — caso existente por nombre\n"
                "- `POST /analyze/json` — caso como JSON en el body\n"
                "- `GET /cases` — listar casos disponibles\n"
                "- `GET /health` — estado del sistema"
            )

    return {
        "id":      f"vigia-{int(time.time())}",
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   req.model,
        "choices": [
            {
                "index":         0,
                "message":       {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@app.get("/cases")
def list_cases():
    """Lista casos disponibles por categoría."""
    cats = {
        "real":    sorted((REPO / "data/cases").glob("VIGIA-REAL-*.json")),
        "syn":     sorted((REPO / "data/cases").glob("VIGIA-SYN-*.json")),
        "benign":  sorted((REPO / "data/cases").glob("VIGIA-BEN-*.json")),
        "demo":    sorted((REPO / "cases").glob("case_0*.json")),
    }
    return {k: [p.name for p in v] for k, v in cats.items()}


@app.post("/analyze/path")
def analyze_by_path(payload: CasePath):
    """Analiza un caso forense VIGÍA dado su path relativo al repo (ej: data/cases/VIGIA-REAL-001.json). USAR ESTE ENDPOINT para analizar casos existentes."""
    case_path = REPO / payload.case_path
    if not case_path.exists():
        raise HTTPException(404, f"Caso no encontrado: {payload.case_path}")
    try:
        pipeline = _run_pipeline(case_path)
        try:
            narrative = _run_narrative(case_path)
        except Exception:
            narrative = "[narrativa no disponible]"
        return {**pipeline, "narrative": narrative, "case": case_path.name}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/analyze/json")
def analyze_by_json(payload: CasePayload):
    """Analiza un caso pasado como JSON crudo en el body."""
    tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(payload.case_data, tf)
    tf.close()
    try:
        pipeline = _run_pipeline(Path(tf.name))
        try:
            narrative = _run_narrative(Path(tf.name))
        except Exception:
            narrative = "[narrativa no disponible]"
        return {**pipeline, "narrative": narrative,
                "case": payload.case_data.get("case_id", "inline")}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        os.unlink(tf.name)


if __name__ == "__main__":
    import os
    import uvicorn
    _host = os.environ.get("VIGIA_HOST", "0.0.0.0")
    _port = int(os.environ.get("VIGIA_PORT", "8000"))
    uvicorn.run(app, host=_host, port=_port, reload=False)
