#!/usr/bin/env python3
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
from vigia.api_case_paths import CasePathError, resolve_case_path

REPO = Path(os.environ.get("VIGIA_REPO", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(REPO))

app = FastAPI(title="VIGÍA Forensic Intelligence API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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
    # Validar el mismo caso normalizado antes de invocar el scorer. Un caso
    # inválido no debe consumir una ruta de decisión y luego fallar al sellar.
    case_ebs = normalize_case_schema(dict(case))
    validate_case_schema(case_ebs)
    case_norm = _normalize_case(case_ebs)

    t0 = time.perf_counter()
    score = _vigia_score(case_norm)

    # Pipeline EBS v1 para bundle hash
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
        case_path = resolve_case_path(REPO, payload.case_path)
    except CasePathError:
        raise HTTPException(404, "Caso no encontrado en los directorios permitidos")
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
    import uvicorn
    uvicorn.run(
        app,
        host=os.environ.get("VIGIA_HOST", "127.0.0.1"),
        port=int(os.environ.get("VIGIA_PORT", "8000")),
        reload=False,
    )
