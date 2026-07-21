#!/usr/bin/env python3
"""
VIGÍA API — FastAPI wrapper para OpenWebUI.
Expone el pipeline real (run_vigia_full.py + vigia_ask.sh) como endpoints REST.
"""
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vigia.api_case_paths import (
    CasePathError,
    CaseSnapshotLimitError,
    snapshot_case_file,
)
from vigia.api_defaults import DEFAULT_CORS_ORIGINS, DEFAULT_HOST, DEFAULT_PORT
from vigia.api_payload import CasePayloadError, validate_case_payload
from vigia.openai_compat import ChatRequest, install_openai_compatibility

REPO = Path(os.environ.get("VIGIA_REPO", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(REPO))
logger = logging.getLogger(__name__)

app = FastAPI(title="VIGÍA Forensic Intelligence API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(DEFAULT_CORS_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
)


class CasePayload(BaseModel):
    case_data: dict


class CasePath(BaseModel):
    case_path: str


def _run_pipeline(case_path: Path) -> dict:
    """Score one case and seal that exact standalone-scorer analysis."""
    import time, subprocess as _sub, tempfile as _tmp
    # Scorer forense (mismo que run_vigia_case.py)
    from vigia_scorer import _vigia_score, _normalize_case
    from vigia.core.bundle_builder import build_bundle
    from vigia.pipeline.vigia_integration_bridge import normalize_case_schema, validate_case_schema

    with open(case_path) as f:
        case = json.load(f)
    # Validar el mismo caso normalizado antes de invocar el scorer. Un caso
    # inválido no debe consumir una ruta de decisión y luego fallar al sellar.
    case_ebs = normalize_case_schema(dict(case))
    validate_case_schema(case_ebs)
    case_norm = _normalize_case(case_ebs)

    t0 = time.perf_counter()
    score = _vigia_score(case_norm)

    # Seal the same direct scorer result returned to the caller.  Do not attach
    # the hash of an independently-derived pipeline result: its vocabulary and
    # risk semantics are different and can contradict this forensic verdict.
    sd = build_bundle(case_ebs, score)
    elapsed = (time.perf_counter() - t0) * 1000

    integ = sd.get("integrity", {})
    bh = integ.get("bundle_hash", "N/A")
    ts = integ.get("sealed_at", sd.get("timestamp", "N/A"))

    tf = _tmp.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(sd, tf, sort_keys=True, indent=2, default=str)
    tf.close()
    verifier_path = REPO / "forensics" / "verify_ebs_v1.py"
    try:
        if not verifier_path.is_file():
            logger.error("EBS verifier unavailable at configured repository")
            verif, level = "UNAVAILABLE", "?"
        else:
            try:
                v = _sub.run(
                    ["python3", str(verifier_path), tf.name],
                    capture_output=True,
                    text=True,
                )
            except OSError:
                logger.exception("EBS verifier process could not be started")
                verif, level = "UNAVAILABLE", "?"
            else:
                if "Resultado   : PASS" in v.stdout:
                    verif = "PASS"
                elif "Resultado   : FAIL" in v.stdout:
                    verif = "FAIL"
                else:
                    logger.error("EBS verifier did not produce a verification result")
                    verif = "UNAVAILABLE"
                level = next(
                    (line for line in ["Level 3", "Level 2", "Level 1"] if line in v.stdout),
                    "?",
                )
    finally:
        os.unlink(tf.name)

    sealed_forensic_verdict = sd.get("caie_analysis", {}).get("verdict")
    if sealed_forensic_verdict != score["verdict"]:
        raise RuntimeError(
            "direct scorer verdict differs from the verdict preserved in its seal"
        )

    return {
        "verdict":     score["verdict"],
        "score":       score["score"],
        "confidence":  score["confidence"],
        "reason":      score["reason"],
        "bundle_hash": bh,
        "timestamp":   ts,
        "verify":      f"{verif} — {level}",
        "sealed_forensic_verdict": sealed_forensic_verdict,
        "ebs_decision": sd.get("decision_trace", {}).get("decision"),
        "seal_scope": "DIRECT_SCORER_ANALYSIS_ONLY",
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


list_models, chat_completions = install_openai_compatibility(
    app,
    run_pipeline=lambda case_path: _run_pipeline(case_path),
    run_narrative=lambda case_path: _run_narrative(case_path),
)


@app.get("/health")
def health():
    return {"status": "VIGÍA operativo"}


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
    try:
        with snapshot_case_file(REPO, payload.case_path) as case_snapshot:
            pipeline = _run_pipeline(case_snapshot)
            try:
                narrative = _run_narrative(case_snapshot)
            except Exception:
                narrative = "[narrativa no disponible]"
        return {**pipeline, "narrative": narrative, "case": Path(payload.case_path).name}
    except CaseSnapshotLimitError as exc:
        raise HTTPException(422, str(exc)) from None
    except CasePathError:
        raise HTTPException(404, "Caso no encontrado en los directorios permitidos")
    except Exception:
        logger.exception("Fallo interno al analizar un caso por path")
        raise HTTPException(500, "Error interno en el pipeline forense.") from None


@app.post("/analyze/json")
def analyze_by_json(payload: CasePayload):
    """Analiza un caso pasado como JSON crudo en el body."""
    try:
        validate_case_payload(payload.case_data)
    except CasePayloadError as exc:
        raise HTTPException(422, str(exc)) from None
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
    except Exception:
        logger.exception("Fallo interno al analizar un caso JSON")
        raise HTTPException(500, "Error interno en el pipeline forense.") from None
    finally:
        os.unlink(tf.name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.environ.get("VIGIA_HOST", DEFAULT_HOST),
        port=int(os.environ.get("VIGIA_PORT", str(DEFAULT_PORT))),
        reload=False,
    )
