"""Verifier wrappers for the VIGÍA web UI.

Both repo verifiers are stdlib-only by deliberate forensic design — their
independence from ``vigia.*`` is what makes third-party verification
meaningful. They are therefore invoked as subprocesses and NEVER imported;
the UI reports their output verbatim and never overrides an exit code.

- ``forensics/verify_ebs_v1.py <bundle> --json``  → exit 0 PASS / 1 FAIL,
  JSON payload with {passed, conformity_level, conformity_label, checks[]}.
- ``verify_tool_log.py <bundle>``                 → exit 0 VERIFIED /
  1 BROKEN / 2 NO_LOG; human-readable stdout (no --json flag exists, and
  adding one is out of scope: the verifier stays untouched).
- ``verify_tool_log.py <trace> --paired-bundle <bundle>`` → same exit codes,
  and since R7-1 it also asserts the trace's case_id and verdict match the
  bundle it is presented with (R8-2).

Secrets: an HMAC key supplied by the caller is handed to the child through its
ENVIRONMENT, never through argv — ``/proc/<pid>/cmdline`` is readable by any
local process while the verifier runs (R8-1).

The sidecar check is pure Python here: recompute SHA-256 of the bundle file
and compare against the ``<bundle>.json.sha256`` sidecar.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

_TIMEOUT_S = 60
_TOOL_LOG_STATUS = {0: "VERIFIED", 1: "BROKEN", 2: "NO_LOG"}


def _run(cmd: list, cwd: Path,
         extra_env: Optional[dict] = None) -> Optional[subprocess.CompletedProcess]:
    env = None
    if extra_env:
        env = dict(os.environ)
        env.update(extra_env)
    try:
        return subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=_TIMEOUT_S, env=env,
        )
    except subprocess.TimeoutExpired:
        return None


def run_ebs_v1(repo_root: Path, bundle_path: Path) -> dict:
    verifier = repo_root / "forensics" / "verify_ebs_v1.py"
    if not verifier.is_file():
        return {"verifier": "ebs_v1", "status": "ERROR", "exit_code": None,
                "detail": "forensics/verify_ebs_v1.py not found in this checkout"}
    proc = _run([sys.executable, str(verifier), str(bundle_path), "--json"],
                cwd=repo_root)
    if proc is None:
        return {"verifier": "ebs_v1", "status": "TIMEOUT", "exit_code": None,
                "detail": f"verifier exceeded {_TIMEOUT_S}s"}
    result = {
        "verifier": "ebs_v1",
        "exit_code": proc.returncode,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
    }
    try:
        payload = json.loads(proc.stdout)
        result["conformity_level"] = payload.get("conformity_level")
        result["conformity_label"] = payload.get("conformity_label")
        result["checks"] = payload.get("checks", [])
        result["passed"] = payload.get("passed")
    except (json.JSONDecodeError, ValueError):
        # verifier crashed before emitting JSON — report its output verbatim
        result["status"] = "ERROR" if proc.returncode not in (0, 1) else result["status"]
        result["detail"] = (proc.stdout + proc.stderr)[-4000:]
    return result


def run_tool_log(repo_root: Path, bundle_path: Path,
                 hmac_key_hex: Optional[str] = None) -> dict:
    verifier = repo_root / "verify_tool_log.py"
    if not verifier.is_file():
        return {"verifier": "tool_log", "status": "ERROR", "exit_code": None,
                "detail": "verify_tool_log.py not found in this checkout"}
    cmd = [sys.executable, str(verifier), str(bundle_path)]
    # R8-1: la clave va por el ENTORNO del hijo, no por argv.
    # /proc/<pid>/cmdline es legible por cualquier proceso local mientras el
    # verificador corre — medido: la clave aparece completa ahi. /proc/<pid>/environ
    # esta restringido al usuario dueno del proceso. No cierra el caso "mismo
    # usuario o root", pero saca la clave del alcance de cualquier usuario local.
    # verify_tool_log._resolve_hmac_key ya lee VIGIA_HMAC_KEY del entorno.
    extra_env = {"VIGIA_HMAC_KEY": hmac_key_hex} if hmac_key_hex else None
    proc = _run(cmd, cwd=repo_root, extra_env=extra_env)
    if proc is None:
        return {"verifier": "tool_log", "status": "TIMEOUT", "exit_code": None,
                "detail": f"verifier exceeded {_TIMEOUT_S}s"}
    return {
        "verifier": "tool_log",
        "exit_code": proc.returncode,
        "status": _TOOL_LOG_STATUS.get(proc.returncode, "ERROR"),
        "detail": (proc.stdout + proc.stderr)[-8000:],
    }


def run_reasoning_trace(repo_root: Path, bundle_path: Path,
                        hmac_key_hex: Optional[str] = None) -> dict:
    """R8-2: verifica la reasoning trace hermana Y su emparejamiento con el bundle.

    El indice marca `has_reasoning_trace` con la sola existencia del archivo
    `<stem>_reasoning_trace.json` — nunca lo abria. Medido: un bundle MALICE con
    la traza de OTRO caso (veredicto SUSPICION) puesta al lado se mostraba con el
    badge "trace" y `verdict_disagreement: False`, porque esa bandera compara
    campos DENTRO de un mismo bundle, no bundle contra traza.

    `verify_tool_log.py` sobre el archivo de traza verifica su cadena y, desde
    R7-1, autodetecta el bundle hermano y compara case_id + veredicto.
    """
    verifier = repo_root / "verify_tool_log.py"
    if not verifier.is_file():
        return {"verifier": "reasoning_trace", "status": "ERROR", "exit_code": None,
                "detail": "verify_tool_log.py not found in this checkout"}
    trace_path = bundle_path.with_name(
        bundle_path.name.replace(".json", "_reasoning_trace.json"))
    if not trace_path.is_file():
        return {"verifier": "reasoning_trace", "status": "ABSENT", "exit_code": None,
                "detail": f"no reasoning trace {trace_path.name} next to the bundle"}
    cmd = [sys.executable, str(verifier), str(trace_path),
           "--paired-bundle", str(bundle_path)]
    extra_env = {"VIGIA_HMAC_KEY": hmac_key_hex} if hmac_key_hex else None
    proc = _run(cmd, cwd=repo_root, extra_env=extra_env)
    if proc is None:
        return {"verifier": "reasoning_trace", "status": "TIMEOUT", "exit_code": None,
                "detail": f"verifier exceeded {_TIMEOUT_S}s"}
    return {
        "verifier": "reasoning_trace",
        "exit_code": proc.returncode,
        "status": _TOOL_LOG_STATUS.get(proc.returncode, "ERROR"),
        "detail": (proc.stdout + proc.stderr)[-8000:],
    }


def check_sidecar(bundle_path: Path) -> dict:
    sidecar = bundle_path.with_name(bundle_path.name + ".sha256")
    if not sidecar.is_file():
        return {"verifier": "sidecar", "status": "ABSENT", "exit_code": None,
                "detail": f"no sidecar {sidecar.name} next to the bundle"}
    recorded = sidecar.read_text(encoding="utf-8", errors="replace").split()
    if not recorded or len(recorded[0]) != 64:
        return {"verifier": "sidecar", "status": "ERROR", "exit_code": None,
                "detail": "sidecar does not start with a 64-hex SHA-256"}
    h = hashlib.sha256()
    with open(bundle_path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    actual = h.hexdigest()
    match = actual == recorded[0].lower()
    return {
        "verifier": "sidecar",
        "status": "MATCH" if match else "MISMATCH",
        "exit_code": None,
        "detail": f"recorded {recorded[0]}\ncomputed {actual}",
    }
