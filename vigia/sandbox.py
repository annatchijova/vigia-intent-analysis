"""
sandbox.py — Ejecución segura de procesos y grep limitado por recursos.

Implementación stdlib-only (asyncio + subprocess + resource).
Reemplaza la dependencia huérfana vigia.security.sandbox que no existía.

Invariantes de seguridad:
  - max_memory_mb y max_cpu_seconds son límites duros (setrlimit en Linux)
  - allowed_dirs en safe_grep previene path traversal
  - stdout truncado a MAX_OUTPUT_BYTES para prevenir DoS por output flooding
"""
from __future__ import annotations

import asyncio
import os
import resource
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["sandboxed_execute", "safe_grep"]

_MAX_OUTPUT_BYTES = 512 * 1024  # 512 KB


def _apply_limits(max_memory_mb: int, max_cpu_seconds: int) -> None:
    try:
        mem_bytes = max_memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    except (ValueError, resource.error):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))
    except (ValueError, resource.error):
        pass


async def sandboxed_execute(
    cmd: List[str],
    max_memory_mb: int = 256,
    max_cpu_seconds: int = 30,
    timeout: Optional[float] = None,
    input_data: Optional[bytes] = None,
    allowed_cmds: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Ejecuta un comando con límites de recursos. Retorna dict stdout/stderr/returncode/error."""
    if not cmd:
        return {"stdout": b"", "stderr": b"", "returncode": -1, "error": "cmd vacío", "truncated": False}
    if allowed_cmds is not None and cmd[0] not in allowed_cmds:
        return {"stdout": b"", "stderr": b"", "returncode": -1,
                "error": f"Comando '{cmd[0]}' no autorizado", "truncated": False}

    effective_timeout = timeout or float(max_cpu_seconds + 5)

    def _preexec():
        _apply_limits(max_memory_mb, max_cpu_seconds)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL if input_data is None else asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=_preexec,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=input_data), timeout=effective_timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            return {"stdout": b"", "stderr": b"", "returncode": -1,
                    "error": f"Timeout ({effective_timeout}s)", "truncated": False}

        truncated = len(stdout) > _MAX_OUTPUT_BYTES
        return {"stdout": stdout[:_MAX_OUTPUT_BYTES], "stderr": stderr[:4096],
                "returncode": proc.returncode, "error": None, "truncated": truncated}

    except FileNotFoundError:
        return {"stdout": b"", "stderr": b"", "returncode": -1,
                "error": f"Binario no encontrado: {cmd[0]}", "truncated": False}
    except Exception as e:
        return {"stdout": b"", "stderr": b"", "returncode": -1,
                "error": str(e), "truncated": False}


async def safe_grep(
    pattern: str,
    folder: str,
    max_depth: int = 4,
    max_memory_mb: int = 256,
    max_cpu_seconds: int = 30,
    allowed_dirs: Optional[List[str]] = None,
    max_matches: int = 500,
) -> Dict[str, Any]:
    """Grep recursivo con prevención de path traversal y límites de recursos."""
    try:
        resolved = str(Path(folder).resolve())
    except Exception as e:
        return {"matches": [], "error": f"Path inválido: {e}", "truncated": False}

    if allowed_dirs:
        allowed_resolved = [str(Path(d).resolve()) for d in allowed_dirs]
        if not any(resolved.startswith(a) for a in allowed_resolved):
            return {"matches": [], "error": f"Directorio fuera de rutas permitidas",
                    "truncated": False}

    if not os.path.isdir(resolved):
        return {"matches": [], "error": f"Directorio no existe: {resolved}", "truncated": False}

    cmd = ["grep", "--recursive", f"--max-depth={max_depth}",
           "--line-number", "--max-count=50", "-E", pattern, resolved]

    result = await sandboxed_execute(cmd=cmd, max_memory_mb=max_memory_mb,
                                      max_cpu_seconds=max_cpu_seconds)
    if result["error"] and result["returncode"] == -1:
        return {"matches": [], "error": result["error"], "truncated": False}

    lines = [l for l in result["stdout"].decode("utf-8", errors="replace").splitlines() if l.strip()]
    truncated = len(lines) > max_matches or result["truncated"]
    return {"matches": lines[:max_matches], "error": None, "truncated": truncated}

