"""Mode 1 investigation runner for the web UI.

Spawns ``python3 vigia_agent.py --evidence … --case-id … --output …`` as a
subprocess (argv list, no shell) and captures its combined stdout/stderr into
a bounded ring buffer for the UI's log polling.

Verdict handling honors the CLAUDE.md invariant — the UI never restates a
verdict. A finished job exposes three facts side by side: the process exit
code, the documented exit-code→verdict label (``vigia_agent.py::_VERDICT_EXIT``:
0 NOISE, 1 MALICE, 2 ERROR, 3 INTENT, 4 ABSTAIN, 5 SUSPICION incl. B-097),
and ``agent_verdict`` read from the sealed bundle. Disagreements are surfaced,
never reconciled.

Output bundles go to ``results/webui/<case_id>_<job_id>_bundle.json`` — the
job-id suffix means a re-run can never overwrite an already sealed bundle.
"""

from __future__ import annotations

import collections
import datetime
import json
import re
import subprocess
import sys
import threading
import os
import uuid
from pathlib import Path
from typing import Optional

from vigia.ui.evidence_paths import EvidencePathError, resolve_evidence_path

CASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

# Documented exit-code map (vigia_agent.py::_VERDICT_EXIT, B-097).
EXIT_LABELS = {0: "NOISE", 1: "MALICE", 2: "ERROR", 3: "INTENT",
               4: "ABSTAIN", 5: "SUSPICION"}

_LOG_MAXLEN = 5000
_DEFAULT_TIMEOUT_S = 30 * 60
_TERMINATE_GRACE_S = 10


class JobValidationError(ValueError):
    pass


class JobBusyError(RuntimeError):
    pass


def _utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class _Job:
    def __init__(self, job_id: str, case_id: str, evidence_rel: str,
                 output_path: Path):
        self.job_id = job_id
        self.case_id = case_id
        self.evidence_rel = evidence_rel
        self.output_path = output_path
        self.state = "queued"          # queued | running | done | error
        self.created_at = _utcnow()
        self.finished_at: Optional[str] = None
        self.exit_code: Optional[int] = None
        self.error: Optional[str] = None
        self.verdict_from_bundle: Optional[str] = None
        self.bundle_id: Optional[str] = None
        self.proc: Optional[subprocess.Popen] = None
        self.log: collections.deque = collections.deque(maxlen=_LOG_MAXLEN)
        self.log_start = 0             # absolute offset of log[0]
        self.log_total = 0             # total lines ever appended
        self.lock = threading.Lock()

    def append_line(self, line: str) -> None:
        with self.lock:
            if len(self.log) == self.log.maxlen:
                self.log_start += 1
            self.log.append(line.rstrip("\n"))
            self.log_total += 1

    def snapshot(self) -> dict:
        with self.lock:
            exit_label = (EXIT_LABELS.get(self.exit_code)
                          if self.exit_code is not None else None)
            return {
                "job_id": self.job_id,
                "case_id": self.case_id,
                "evidence_path": self.evidence_rel,
                "state": self.state,
                "created_at": self.created_at,
                "finished_at": self.finished_at,
                "exit_code": self.exit_code,
                "exit_code_verdict": exit_label,
                "verdict_from_bundle": self.verdict_from_bundle,
                "verdicts_agree": (
                    None if exit_label is None or self.verdict_from_bundle is None
                    else exit_label == self.verdict_from_bundle
                ),
                "output_bundle_rel_path": str(self.output_path),
                "bundle_id": self.bundle_id,
                "error": self.error,
            }


class JobRunner:
    def __init__(self, repo_root: Path, bundle_index=None,
                 agent_script: Optional[Path] = None,
                 max_jobs: Optional[int] = None,
                 timeout_s: int = _DEFAULT_TIMEOUT_S):
        self.repo_root = Path(repo_root).resolve()
        self.bundle_index = bundle_index
        self.agent_script = agent_script or self.repo_root / "vigia_agent.py"
        self.timeout_s = timeout_s
        if max_jobs is None:
            max_jobs = int(os.environ.get("VIGIA_UI_MAX_JOBS", "1"))
        self._slots = threading.BoundedSemaphore(max(1, max_jobs))
        self._jobs: dict[str, _Job] = {}
        self._jobs_lock = threading.Lock()

    # -- submission ---------------------------------------------------------

    def submit(self, evidence_path: str, case_id: str,
               examiner_id: Optional[str] = None,
               acquisition_tool: Optional[str] = None,
               write_blocker_used: Optional[bool] = None) -> str:
        if not CASE_ID_RE.match(case_id or ""):
            raise JobValidationError(
                "case_id must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
            )
        try:
            evidence_abs = resolve_evidence_path(self.repo_root, evidence_path)
        except EvidencePathError as exc:
            raise JobValidationError(str(exc)) from exc
        if not self.agent_script.is_file():
            raise JobValidationError("vigia_agent.py not found in this checkout")

        if not self._slots.acquire(blocking=False):
            running = [j.job_id for j in self._jobs.values()
                       if j.state in ("queued", "running")]
            raise JobBusyError(
                f"an investigation is already running ({', '.join(running) or 'unknown'})"
            )

        job_id = uuid.uuid4().hex[:12]
        out_dir = self.repo_root / "results" / "webui"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = (out_dir / f"{case_id}_{job_id}_bundle.json"
                       ).relative_to(self.repo_root)
        job = _Job(job_id, case_id, evidence_path, output_path)
        with self._jobs_lock:
            self._jobs[job_id] = job

        cmd = [sys.executable, str(self.agent_script),
               "--evidence", str(evidence_abs),
               "--case-id", case_id,
               "--output", str(self.repo_root / output_path)]
        if examiner_id:
            cmd += ["--examiner-id", examiner_id]
        if acquisition_tool:
            cmd += ["--acquisition-tool", acquisition_tool]
        if write_blocker_used is not None:
            cmd += ["--write-blocker-used", "true" if write_blocker_used else "false"]

        thread = threading.Thread(target=self._run, args=(job, cmd), daemon=True)
        thread.start()
        return job_id

    # -- execution ----------------------------------------------------------

    def _run(self, job: _Job, cmd: list) -> None:
        try:
            job.state = "running"
            job.append_line(f"$ {' '.join(cmd[1:3])} … --case-id {job.case_id}")
            proc = subprocess.Popen(
                cmd, cwd=str(self.repo_root),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", start_new_session=True,
            )
            job.proc = proc
            timer = threading.Timer(self.timeout_s, self._kill, args=(job,))
            timer.daemon = True
            timer.start()
            try:
                assert proc.stdout is not None
                for line in proc.stdout:
                    job.append_line(line)
                proc.wait()
            finally:
                timer.cancel()
            job.exit_code = proc.returncode
            if job.error is None and proc.returncode < 0:
                job.error = f"process terminated by signal {-proc.returncode}"
            self._read_sealed_bundle(job)
            job.state = "error" if job.error else "done"
        except Exception as exc:  # noqa: BLE001 — job thread must never die silently
            job.error = f"{exc.__class__.__name__}: {exc}"
            job.state = "error"
        finally:
            job.finished_at = _utcnow()
            self._slots.release()

    def _kill(self, job: _Job) -> None:
        proc = job.proc
        if proc is None or proc.poll() is not None:
            return
        job.error = f"timeout after {self.timeout_s}s — process terminated"
        job.append_line(f"[webui] {job.error}")
        try:
            proc.terminate()
            try:
                proc.wait(timeout=_TERMINATE_GRACE_S)
            except subprocess.TimeoutExpired:
                proc.kill()
        except OSError:
            pass

    def _read_sealed_bundle(self, job: _Job) -> None:
        """Read agent_verdict from the sealed bundle — the bundle, not the
        exit code, is authoritative; both are exposed side by side."""
        bundle_path = self.repo_root / job.output_path
        if not bundle_path.is_file():
            if job.error is None and job.exit_code not in (None, 2):
                job.append_line("[webui] no sealed bundle found at the output path")
            return
        try:
            doc = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            job.append_line(f"[webui] sealed bundle unreadable: {exc.__class__.__name__}")
            return
        if isinstance(doc, dict):
            job.verdict_from_bundle = doc.get("agent_verdict")
        if self.bundle_index is not None:
            entry = self.bundle_index.register_file(bundle_path)
            if entry:
                job.bundle_id = entry["id"]

    # -- queries ------------------------------------------------------------

    def get(self, job_id: str) -> Optional[dict]:
        job = self._jobs.get(job_id)
        return job.snapshot() if job else None

    def list_jobs(self) -> list:
        with self._jobs_lock:
            jobs = list(self._jobs.values())
        return sorted((j.snapshot() for j in jobs),
                      key=lambda s: s["created_at"], reverse=True)

    def read_log(self, job_id: str, offset: int = 0) -> Optional[dict]:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        with job.lock:
            start = job.log_start
            lines = list(job.log)
            total = job.log_total
            state = job.state
        if offset < start:
            visible = lines
            truncated = True
        else:
            visible = lines[offset - start:]
            truncated = False
        return {
            "lines": visible,
            "next_offset": total,
            "truncated": truncated,
            "state": state,
        }

    def shutdown(self) -> None:
        """Terminate running jobs (used on server shutdown)."""
        for job in self._jobs.values():
            proc = job.proc
            if proc is not None and proc.poll() is None:
                try:
                    proc.terminate()
                except OSError:
                    pass
