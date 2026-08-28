"""FastAPI application for the VIGÍA local web UI.

Standalone app — deliberately separate from ``vigia_api.py`` / ``vigia/vigia_api.py``
(the Mode 5 wrappers guarded by ``tests/test_b168_api_contract_parity.py``): those
files are not modified and this app does not mount their routes.

Security posture (mirrors INSTALL.md §11): no application auth layer, so the
server binds loopback only by default (``vigia/api_defaults.py::DEFAULT_HOST``)
and must sit behind an authenticated boundary for any wider exposure. No CORS
middleware is installed (same-origin SPA). State-changing POSTs additionally
require a local Origin/Referer and a JSON content type, which blocks
cross-site form submissions from other pages in the same browser.
"""

from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from vigia.ui import normalizer
from vigia.ui.bundle_index import BundleIndex

UI_VERSION = "1.0.0"

_MAX_RAW_BYTES = 10 * 1024 * 1024
_LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}

_STATIC_DIR = Path(__file__).parent / "static"


# Module-level models: with `from __future__ import annotations` in effect,
# FastAPI resolves stringified annotations against module globals, so these
# must not be defined inside create_app().

class VerifyRequest(BaseModel):
    verifier: str = Field(pattern="^(ebs_v1|tool_log|sidecar)$")
    hmac_key_hex: Optional[str] = Field(default=None, max_length=1024,
                                        pattern="^[0-9a-fA-F]*$")


class InvestigationRequest(BaseModel):
    evidence_path: str = Field(min_length=1, max_length=4096)
    case_id: str = Field(min_length=1, max_length=64)
    examiner_id: Optional[str] = Field(default=None, max_length=128)
    acquisition_tool: Optional[str] = Field(default=None, max_length=128)
    write_blocker_used: Optional[bool] = None


def _origin_is_local(value: str) -> bool:
    """True when an Origin/Referer header points at a loopback host."""
    m = re.match(r"^[a-z][a-z0-9+.-]*://([^/:]+|\[[0-9a-fA-F:]+\])(:\d+)?", value)
    if not m:
        return False
    return m.group(1).lower() in _LOCAL_HOSTS


class _BundleView:
    """Resolves opaque bundle ids to files and loads them. The HTTP layer never
    accepts a raw path for reads — ids only."""

    def __init__(self, index: BundleIndex):
        self.index = index

    def entry_or_404(self, bundle_id: str) -> dict:
        entry = self.index.get(bundle_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="unknown bundle id")
        return entry

    def path_or_404(self, bundle_id: str) -> Path:
        path = self.entry_or_404(bundle_id)["abs_path"]
        if not path.is_file():
            raise HTTPException(status_code=404, detail="bundle file no longer exists")
        return path


def create_app(repo_root: Optional[Path] = None) -> FastAPI:
    repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
    index = BundleIndex(repo_root)
    index.refresh()
    view = _BundleView(index)

    @contextlib.asynccontextmanager
    async def _lifespan(app_: FastAPI):
        yield
        runner = getattr(app_.state, "job_runner", None)
        if runner is not None:
            runner.shutdown()

    app = FastAPI(title="VIGÍA Web UI", version=UI_VERSION, docs_url=None,
                  redoc_url=None, openapi_url=None, lifespan=_lifespan)
    app.state.repo_root = repo_root
    app.state.bundle_index = index

    # -- origin guard on all state-changing requests ------------------------

    @app.middleware("http")
    async def _reject_cross_site_writes(request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            for header in ("origin", "referer"):
                value = request.headers.get(header)
                if value and not _origin_is_local(value):
                    return JSONResponse(
                        status_code=403,
                        content={"detail": f"cross-site {header} rejected"},
                    )
            ctype = request.headers.get("content-type", "")
            if not ctype.lower().startswith("application/json"):
                return JSONResponse(
                    status_code=415,
                    content={"detail": "application/json required"},
                )
        return await call_next(request)

    # -- health -------------------------------------------------------------

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "ui_version": UI_VERSION,
            "repo_root": str(repo_root),
            "bundle_count": len(index),
            "schemas": index.counts_by_schema(),
        }

    # -- bundles ------------------------------------------------------------

    @app.get("/api/bundles")
    def list_bundles(verdict: Optional[str] = None, schema: Optional[str] = None,
                     case: Optional[str] = None, q: Optional[str] = None,
                     limit: int = 100, offset: int = 0, refresh: int = 0):
        if refresh:
            index.refresh()
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        return index.query(verdict=verdict, schema=schema, case=case, q=q,
                           limit=limit, offset=offset)

    @app.get("/api/bundles/{bundle_id}")
    def bundle_detail(bundle_id: str):
        entry = view.entry_or_404(bundle_id)
        path = view.path_or_404(bundle_id)
        try:
            doc = normalizer.load_bundle(path)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return {
                "schema": "unparseable",
                "rel_path": entry["rel_path"],
                "error": f"bundle could not be parsed: {exc.__class__.__name__}",
                "warnings": ["file is not valid JSON — no content is shown"],
            }
        norm = normalizer.normalize(doc, entry["rel_path"])
        norm["sidecar"] = {
            "has_sha256_sidecar": entry["has_sha256_sidecar"],
            "has_reasoning_trace": entry["has_reasoning_trace"],
        }
        return norm

    @app.get("/api/bundles/{bundle_id}/raw")
    def bundle_raw(bundle_id: str):
        path = view.path_or_404(bundle_id)
        size = path.stat().st_size
        if size > _MAX_RAW_BYTES:
            raise HTTPException(status_code=413,
                                detail=f"bundle is {size} bytes; raw view capped "
                                       f"at {_MAX_RAW_BYTES}")
        return Response(content=path.read_bytes(), media_type="application/json")

    # -- verify (phase 3) ---------------------------------------------------

    @app.post("/api/bundles/{bundle_id}/verify")
    def bundle_verify(bundle_id: str, req: VerifyRequest):
        from vigia.ui import verify as verify_mod
        path = view.path_or_404(bundle_id)
        if req.verifier == "ebs_v1":
            return verify_mod.run_ebs_v1(repo_root, path)
        if req.verifier == "tool_log":
            return verify_mod.run_tool_log(repo_root, path,
                                           hmac_key_hex=req.hmac_key_hex)
        return verify_mod.check_sidecar(path)

    # -- investigations (phase 4) -------------------------------------------

    def _runner(request: Request):
        runner = getattr(request.app.state, "job_runner", None)
        if runner is None:
            from vigia.ui.jobs import JobRunner
            runner = JobRunner(repo_root, bundle_index=index)
            request.app.state.job_runner = runner
        return runner

    @app.get("/api/evidence")
    def list_evidence():
        from vigia.ui import evidence_paths
        return evidence_paths.list_evidence_roots(repo_root)

    @app.post("/api/investigations", status_code=202)
    def launch_investigation(req: InvestigationRequest, request: Request):
        from vigia.ui.jobs import JobBusyError, JobValidationError
        runner = _runner(request)
        try:
            job_id = runner.submit(
                evidence_path=req.evidence_path,
                case_id=req.case_id,
                examiner_id=req.examiner_id,
                acquisition_tool=req.acquisition_tool,
                write_blocker_used=req.write_blocker_used,
            )
        except JobValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        except JobBusyError as exc:
            raise HTTPException(status_code=409, detail=str(exc))
        return {"job_id": job_id}

    @app.get("/api/investigations")
    def list_investigations(request: Request):
        return _runner(request).list_jobs()

    @app.get("/api/investigations/{job_id}")
    def investigation_detail(job_id: str, request: Request):
        job = _runner(request).get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="unknown job id")
        return job

    @app.get("/api/investigations/{job_id}/log")
    def investigation_log(job_id: str, request: Request, offset: int = 0):
        result = _runner(request).read_log(job_id, max(0, offset))
        if result is None:
            raise HTTPException(status_code=404, detail="unknown job id")
        return result

    # -- static SPA ---------------------------------------------------------

    @app.get("/")
    def spa_root():
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    return app
