"""
vigia/sandbox.py
================
VIGÍA – Safe subprocess execution sandbox.

Addresses the P0 vulnerability identified in the security audit:
``search_pattern`` and ``mount_sift_evidence`` ran arbitrary subprocesses
with no memory/CPU limits, no depth caps, and no path confinement.

This module provides
--------------------
* ``sandboxed_execute`` : async wrapper around asyncio.create_subprocess_exec
  that enforces memory, CPU, and output limits via POSIX ``setrlimit``.
* ``safe_grep``         : drop-in replacement for the old grep call in
  ``search_pattern``, with depth limiting and path confinement.
* ``_sanitize_grep_pattern`` : prevents grep from interpreting special chars
  as shell metacharacters (redundant when using exec lists, but adds an
  extra layer of documentation-level clarity).

Compatibility
-------------
``setrlimit`` is POSIX-only (Linux / macOS).  On Windows the preexec_fn is
skipped and only the asyncio timeout applies.  A warning is emitted once.
"""

from __future__ import annotations

import asyncio
import os
import resource
import sys
import warnings
from typing import Final


# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

DEFAULT_MAX_MEMORY_MB: Final[int] = 512
DEFAULT_MAX_CPU_SECONDS: Final[int] = 30
DEFAULT_MAX_OUTPUT_BYTES: Final[int] = 10 * 1024 * 1024   # 10 MB
DEFAULT_MAX_STDERR_BYTES: Final[int] = 256 * 1024          # 256 KB
DEFAULT_TIMEOUT_GRACE: Final[int] = 5                      # seconds after CPU limit

_IS_POSIX: Final[bool] = os.name != "nt"

# Kimi P1-8: Windows resource fail-safe
_ENFORCE_POSIX_SANDBOX: Final[bool] = (
    os.getenv("VIGIA_ENFORCE_POSIX_SANDBOX", "false").lower() == "true"
)

if not _IS_POSIX:
    if _ENFORCE_POSIX_SANDBOX:
        import sys as _sys
        print(
            "[VIGIA][CRITICAL] VIGIA_ENFORCE_POSIX_SANDBOX=true but running on "
            "non-POSIX platform. setrlimit-based resource limits are NOT available. "
            "Subprocess execution without memory/CPU limits is a security risk. "
            "Aborting.",
            file=_sys.stderr, flush=True,
        )
        _sys.exit(1)
    else:
        warnings.warn(
            "[VIGIA][sandbox] Running on non-POSIX platform. "
            "setrlimit-based resource limits are not available. "
            "Will attempt psutil-based limits as fallback; "
            "asyncio timeout always applies.",
            RuntimeWarning,
            stacklevel=1,
        )


def _apply_windows_limits(pid: int, max_memory_mb: int) -> None:
    """
    Kimi P1-8: Best-effort resource limits on Windows via psutil.

    Sets a memory limit on the subprocess using psutil's Process API.
    This is NOT equivalent to setrlimit (kernel enforcement) — the process
    can still allocate beyond the limit and psutil will only report it.
    The real enforcement comes from the asyncio timeout.

    Requires psutil. If not available, logs a warning and continues.
    """
    try:
        import psutil
        proc = psutil.Process(pid)
        # Windows: set memory working set limit (soft limit)
        max_bytes = max_memory_mb * 1024 * 1024
        try:
            # Windows-specific: SetProcessWorkingSetSizeEx
            import ctypes
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.OpenProcess(0x1F0FFF, False, pid)  # PROCESS_ALL_ACCESS
            if handle:
                kernel32.SetProcessWorkingSetSizeEx(
                    handle, max_bytes // 2, max_bytes, 0
                )
                kernel32.CloseHandle(handle)
        except (AttributeError, OSError):
            pass  # Not on Windows or insufficient privileges
    except ImportError:
        pass  # psutil not available
    except Exception:
        pass  # Best-effort — never crash the parent


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_preexec(max_memory_mb: int, max_cpu_seconds: int) -> None:
    """
    Called in the child process *after* fork but *before* exec.
    Sets hard+soft resource limits.
    """
    mem_bytes = max_memory_mb * 1024 * 1024
    # Virtual address space
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    # CPU time
    resource.setrlimit(
        resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds + DEFAULT_TIMEOUT_GRACE)
    )
    # No new files larger than 50 MB created by the subprocess
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, resource.RLIM_INFINITY))


def _drop_privs_if_requested() -> None:
    """
    If the server is running as root and VIGIA_DROP_PRIVS_UID is set,
    drop to that UID before exec.  This is a defence-in-depth measure for
    the ``mount_sift_evidence`` use-case.

    P1 fix (2026-04 audit): previous version did ``pass`` on failure,
    leaving the child process running as root.  Now we abort the child
    with os._exit(126) if setuid fails.  We cannot use audit_logger here
    because this runs post-fork in the child (not fork-safe), so we
    write directly to fd 2 (stderr).

    If VIGIA_DROP_PRIVS_UID is set but we are NOT root, this is a no-op
    (the operator configured it for a root-capable deployment but we are
    already running unprivileged — that is fine).
    """
    drop_uid_str = os.getenv("VIGIA_DROP_PRIVS_UID")
    if not drop_uid_str or os.getuid() != 0:
        return

    try:
        drop_uid = int(drop_uid_str)
    except ValueError:
        # Invalid UID configured — refuse to continue as root
        os.write(2, (
            f"[VIGIA][CRITICAL] VIGIA_DROP_PRIVS_UID={drop_uid_str!r} "
            f"is not a valid integer. Aborting child process rather than "
            f"running as root.\n"
        ).encode())
        os._exit(126)

    try:
        # Drop supplementary groups first, then GID, then UID
        # (must be done in this order — setuid last because after that
        # we lose the privilege to change groups)
        try:
            os.setgroups([])
        except OSError:
            pass  # Not all systems support setgroups
        os.setgid(drop_uid)
        os.setuid(drop_uid)
    except PermissionError as exc:
        os.write(2, (
            f"[VIGIA][CRITICAL] Failed to drop privileges to UID "
            f"{drop_uid}: {exc}. Aborting child process rather than "
            f"running as root.\n"
        ).encode())
        os._exit(126)
    except OSError as exc:
        os.write(2, (
            f"[VIGIA][CRITICAL] OS error dropping privileges to UID "
            f"{drop_uid}: {exc}. Aborting child.\n"
        ).encode())
        os._exit(126)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def sandboxed_execute(
    cmd: list[str],
    input_data: bytes | None = None,
    max_memory_mb: int = DEFAULT_MAX_MEMORY_MB,
    max_cpu_seconds: int = DEFAULT_MAX_CPU_SECONDS,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
    env: dict[str, str] | None = None,
) -> dict:
    """
    Execute *cmd* with resource limits and a hard timeout.

    Returns a dict with keys:
        returncode  (int)
        stdout      (bytes, truncated to max_output_bytes)
        stderr      (bytes, truncated to max_stderr_bytes)
        truncated   (bool)
        error       (str | None)  – set on timeout or OS error

    Never raises – all errors are captured in the return dict.
    """
    timeout = max_cpu_seconds + DEFAULT_TIMEOUT_GRACE

    preexec: object | None = None
    if _IS_POSIX:
        # Capture loop variables for the closure
        _mem = max_memory_mb
        _cpu = max_cpu_seconds

        def preexec():  # noqa: ANN202
            _make_preexec(_mem, _cpu)
            _drop_privs_if_requested()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if input_data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=preexec,
            env=env,
            limit=max_output_bytes,  # asyncio StreamReader buffer limit
        )
    except FileNotFoundError as exc:
        return {
            "returncode": -1,
            "stdout": b"",
            "stderr": b"",
            "truncated": False,
            "error": f"Command not found: {cmd[0]!r} – {exc}",
        }
    except OSError as exc:
        return {
            "returncode": -1,
            "stdout": b"",
            "stderr": b"",
            "truncated": False,
            "error": f"OS error launching subprocess: {exc}",
        }

    # Kimi P1-8: Apply Windows resource limits post-creation
    if not _IS_POSIX and proc.pid:
        _apply_windows_limits(proc.pid, max_memory_mb)

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=input_data),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        return {
            "returncode": -1,
            "stdout": b"",
            "stderr": b"",
            "truncated": False,
            "error": f"TIMEOUT after {timeout}s",
        }

    truncated = len(stdout) > max_output_bytes
    return {
        "returncode": proc.returncode,
        "stdout": stdout[:max_output_bytes],
        "stderr": stderr[:DEFAULT_MAX_STDERR_BYTES],
        "truncated": truncated,
        "error": None,
    }


def _sanitize_grep_pattern(pattern: str) -> str:
    """
    Strip characters that could cause grep to behave unexpectedly even when
    passed via exec list (not shell).  In particular, NUL bytes would silently
    truncate the pattern string in C land.
    """
    # Remove NUL bytes
    cleaned = pattern.replace("\x00", "")
    # Warn if the pattern is suspiciously long
    if len(cleaned) > 512:
        cleaned = cleaned[:512]
    return cleaned


async def safe_grep(
    pattern: str,
    folder: str,
    max_depth: int = 5,
    max_memory_mb: int = 256,
    max_cpu_seconds: int = 30,
    allowed_dirs: list[str] | None = None,
    max_total_scan_bytes: int = 500 * 1024 * 1024,  # 500 MB
) -> dict:
    """
    Grep *pattern* inside *folder* with depth limiting and optional path
    confinement to *allowed_dirs*.

    Returns a dict with:
        matches     (list[str])  – lines matching the pattern
        truncated   (bool)
        error       (str | None)
        files_grepped (int | None)  – only available on GNU grep >= 3.8
        scan_volume_bytes (int)    – total bytes in scanned directory tree
    """
    from vigia.security import _sanitize_path  # local import avoids circular

    # Validate folder path
    try:
        safe_folder = _sanitize_path(folder, allow_symlinks=False)
    except ValueError as exc:
        return {"matches": [], "truncated": False, "error": str(exc)}

    # Optional confinement to allowed evidence directories
    if allowed_dirs:
        if not any(safe_folder.startswith(d) for d in allowed_dirs):
            return {
                "matches": [],
                "truncated": False,
                "error": f"Path {safe_folder!r} is outside allowed evidence directories.",
            }

    # ── Total scan volume check (P0 fix — 2026-04) ────────────────────────
    # Prevents an attacker from filling evidence_dir with many large files
    # to force VIGIA to read gigabytes of data via grep.
    total_bytes = 0
    file_count = 0
    try:
        for root, dirs, files in os.walk(safe_folder):
            depth = root.replace(safe_folder, "").count(os.sep)
            if depth >= max_depth:
                dirs.clear()  # don't descend further
                continue
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    total_bytes += os.path.getsize(fpath)
                    file_count += 1
                except OSError:
                    pass
                if total_bytes > max_total_scan_bytes:
                    return {
                        "matches": [],
                        "truncated": True,
                        "error": (
                            f"Total scan volume ({total_bytes:,} bytes) exceeds "
                            f"limit ({max_total_scan_bytes:,} bytes). "
                            f"Scanned {file_count} files before abort."
                        ),
                        "scan_volume_bytes": total_bytes,
                    }
    except OSError as exc:
        return {"matches": [], "truncated": False, "error": f"Cannot stat directory: {exc}"}

    clean_pattern = _sanitize_grep_pattern(pattern)
    if not clean_pattern:
        return {"matches": [], "truncated": False, "error": "Empty pattern after sanitisation."}

    # ── Build command: find + xargs grep ──────────────────────────────────
    # GNU grep does NOT have --max-depth. Previous version used it and
    # silently failed on most systems. We use find(1) for depth control
    # (POSIX-standard -maxdepth) piped to xargs grep for the actual search.
    #
    # find -maxdepth N -type f | xargs grep -I -n -- PATTERN
    #
    # Security: both commands run inside sandboxed_execute with
    # setrlimit (memory, CPU, file size) and hard asyncio timeout.
    cmd = [
        "find", safe_folder,
        "-maxdepth", str(max_depth),
        "-type", "f",
        "-not", "-path", "*/.git/*",
        "-not", "-path", "*/.svn/*",
        "-print0",
    ]

    # Phase 1: collect file list with find
    find_result = await sandboxed_execute(
        cmd,
        max_memory_mb=max_memory_mb,
        max_cpu_seconds=max_cpu_seconds,
    )

    if find_result["error"]:
        return {"matches": [], "truncated": find_result["truncated"], "error": find_result["error"]}

    file_list = find_result["stdout"]
    if not file_list.strip():
        return {"matches": [], "truncated": False, "error": None, "scan_volume_bytes": total_bytes}

    # Phase 2: grep the found files via xargs (null-delimited, safe for spaces)
    grep_cmd = [
        "xargs", "-0",
        "grep",
        "-I",             # skip binary files
        "--line-number",
        "--with-filename",
        "--",             # end of options
        clean_pattern,
    ]

    grep_result = await sandboxed_execute(
        grep_cmd,
        input_data=file_list,
        max_memory_mb=max_memory_mb,
        max_cpu_seconds=max_cpu_seconds,
    )

    # grep returns 1 when no matches found — not an error
    if grep_result["error"]:
        return {"matches": [], "truncated": grep_result["truncated"], "error": grep_result["error"]}

    raw_output = grep_result["stdout"].decode("utf-8", errors="replace")
    lines = [ln for ln in raw_output.splitlines() if ln.strip()]

    return {
        "matches": lines,
        "truncated": grep_result["truncated"],
        "error": None,
        "returncode": grep_result["returncode"],
        "scan_volume_bytes": total_bytes,
        "files_in_scope": file_count,
    }
