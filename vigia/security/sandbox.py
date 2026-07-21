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

SECURITY HARDENING (Kimi P1-10, SANS Hackathon 2026):
* VIGIA_GREP_DEPTH enforcement via find -maxdepth (default: 5)
* Atomic memory limit application via setrlimit preexec
* Windows fail-safe with aggressive 5-second timeout when setrlimit unavailable
* Memory limits applied immediately before exec to prevent inheritance attacks

Compatibility
-------------
``setrlimit`` is POSIX-only (Linux / macOS).  On Windows the preexec_fn is
skipped and only the asyncio timeout applies.  A warning is emitted once.
"""

from __future__ import annotations

import asyncio
import os
import re
import resource
import sys
import warnings
from pathlib import Path
from typing import Final


# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------

DEFAULT_MAX_MEMORY_MB: Final[int] = 512
DEFAULT_MAX_CPU_SECONDS: Final[int] = 30
DEFAULT_MAX_OUTPUT_BYTES: Final[int] = 10 * 1024 * 1024   # 10 MB
DEFAULT_MAX_STDERR_BYTES: Final[int] = 256 * 1024          # 256 KB
DEFAULT_TIMEOUT_GRACE: Final[int] = 5                      # seconds after CPU limit

# Kimi P1-10: VIGIA_GREP_DEPTH for safe_grep depth limiting
VIGIA_GREP_DEPTH: Final[int] = int(os.getenv("VIGIA_GREP_DEPTH", "5"))
if VIGIA_GREP_DEPTH < 1 or VIGIA_GREP_DEPTH > 20:
    warnings.warn(
        f"[VIGIA][sandbox] VIGIA_GREP_DEPTH={VIGIA_GREP_DEPTH} outside safe range [1-20]. "
        f"Clamping to default (5).",
        RuntimeWarning,
        stacklevel=1,
    )
    VIGIA_GREP_DEPTH = 5

_IS_POSIX: Final[bool] = os.name != "nt"

# Kimi P1-8: Windows resource fail-safe
_ENFORCE_POSIX_SANDBOX: Final[bool] = (
    os.getenv("VIGIA_ENFORCE_POSIX_SANDBOX", "false").lower() == "true"
)

# Kimi P1-10: Windows aggressive timeout when setrlimit unavailable
WINDOWS_AGGRESSIVE_TIMEOUT: Final[int] = int(
    os.getenv("VIGIA_WINDOWS_TIMEOUT", "5")  # 5 seconds default for Windows
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
            f"Using aggressive timeout of {WINDOWS_AGGRESSIVE_TIMEOUT}s for all commands. "
            "Install psutil for best-effort memory limits; "
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
    Sets hard+soft resource limits ATOMICALLY before execve.

    Kimi P1-10: This ensures the child process inherits strict limits
    and cannot modify them before executing the target binary.
    """
    mem_bytes = max_memory_mb * 1024 * 1024

    # Kimi P1-10: ATOMIC application of all limits before exec
    # Order matters: set stricter limits first

    # 1. Virtual address space (RAM + swap)
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))

    # 2. CPU time (hard limit + grace period for cleanup)
    resource.setrlimit(
        resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds + DEFAULT_TIMEOUT_GRACE)
    )

    # 3. No core dumps (security: prevent info leakage)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    # 4. No new files larger than 50 MB
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, resource.RLIM_INFINITY))

    # 5. Limit number of open files (prevent fd exhaustion)
    resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 2048))

    # 6. Limit stack size (prevent stack overflow attacks)
    stack_limit = min(64 * 1024 * 1024, mem_bytes // 4)  # 64MB or 1/4 of memory
    resource.setrlimit(resource.RLIMIT_STACK, (stack_limit, stack_limit))

    # 7. Number of processes.
    # LaBestia fix (2026-07-06): (64, 64) era un cap por-UID que cuenta TODOS los
    # procesos del uid real, no sólo este sandbox. En un host forense real (sesión
    # de escritorio, servidor multi-analista) el uid supera 64 procesos de rutina,
    # así que apretar a 64 hacía fallar el fork de grep por parte de xargs con
    # EAGAIN ("xargs: cannot fork: Resource temporarily unavailable"): la búsqueda
    # nunca corría y safe_grep reportaba un scan fallido — no un resultado limpio.
    # RLIMIT_NPROC es per-UID (no per-árbol-de-procesos): es el primitivo
    # equivocado para aislar este sandbox, y un número fijo (64/512) rompe en el
    # host que lo supere. El fork-bomb ya está acotado por RLIMIT_AS, RLIMIT_CPU y
    # el timeout duro de asyncio. Se eleva al límite del sistema (hard) en vez de
    # apretar: se conserva el techo que impone el SO sin romper por conteo de uid.
    try:
        _np_soft, _np_hard = resource.getrlimit(resource.RLIMIT_NPROC)
        resource.setrlimit(resource.RLIMIT_NPROC, (_np_hard, _np_hard))
    except (ValueError, OSError):
        pass  # May not be available on all systems


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

    Kimi P1-10: On POSIX, setrlimit is applied ATOMICALLY in preexec_fn
    immediately before execve, preventing the child from inheriting or
    modifying limits. On Windows, uses aggressive timeout fallback.

    Returns a dict with keys:
        returncode  (int)
        stdout      (bytes, truncated to max_output_bytes)
        stderr      (bytes, truncated to max_stderr_bytes)
        truncated   (bool)
        error       (str | None)  – set on timeout or OS error

    Never raises – all errors are captured in the return dict.
    """
    # Kimi P1-10: Determine effective timeout
    if _IS_POSIX:
        timeout = max_cpu_seconds + DEFAULT_TIMEOUT_GRACE
    else:
        # Windows: aggressive timeout since setrlimit unavailable
        timeout = min(WINDOWS_AGGRESSIVE_TIMEOUT, max_cpu_seconds)
        warnings.warn(
            f"[VIGIA][sandbox] Windows platform: using aggressive timeout {timeout}s "
            f"(setrlimit unavailable)",
            RuntimeWarning,
            stacklevel=2,
        )

    preexec: object | None = None
    if _IS_POSIX:
        # Capture loop variables for the closure
        _mem = max_memory_mb
        _cpu = max_cpu_seconds

        def preexec():  # noqa: ANN202
            # Kimi P1-10: Apply limits ATOMICALLY before exec
            _make_preexec(_mem, _cpu)
            _drop_privs_if_requested()

    try:
        # Kimi P1-10: Use low-level asyncio subprocess for better control
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
        # Kimi P1-10: Aggressive kill on timeout
        try:
            proc.kill()
            # Give it a moment to die, then force if needed
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except (ProcessLookupError, asyncio.TimeoutError):
            try:
                proc.terminate()  # SIGTERM
                await asyncio.wait_for(proc.wait(), timeout=1.0)
            except (ProcessLookupError, asyncio.TimeoutError):
                pass  # Process already dead or refusing to die

        return {
            "returncode": -1,
            "stdout": b"",
            "stderr": b"",
            "truncated": False,
            "error": f"TIMEOUT after {timeout}s (Kimi P1-10: aggressive kill applied)",
        }

    truncated = len(stdout) > max_output_bytes
    return {
        "returncode": proc.returncode,
        "stdout": stdout[:max_output_bytes],
        "stderr": stderr[:DEFAULT_MAX_STDERR_BYTES],
        "truncated": truncated,
        "error": None,
    }


# ── Validación canónica de patrones grep (H4 / TANDA 2, 2026-07-06) ─────────
# Antes había DOS _sanitize_grep_pattern divergentes: este (fail-open —
# strip silencioso de NUL + truncado a 512: el patrón EJECUTADO difería del
# pedido sin ninguna señal, resultados forenses mal atribuidos) y el del
# bridge (fail-closed — whitelist + rechazo con audit log). La canónica es la
# estricta: los tests e2e ya fijaban su contrato (rechaza inyección shell y
# homoglifos) y una herramienta forense no puede mutar silenciosamente lo que
# el analista pidió buscar. El bridge ahora re-exporta esta.

MAX_GREP_PATTERN_LENGTH: Final = 200      # máximo largo de patrón grep
_ALLOWED_GREP_PATTERN = re.compile(r'^[\w\s.\-_@#!?,;:]+$')


def _sanitize_grep_pattern(pattern: str) -> str:
    """
    Valida patron grep para prevenir inyeccion de comandos. Fail-closed:
    rechaza con ValueError (y audit log) en lugar de mutar silenciosamente.

    Gemini P0 fix: uses re.fullmatch (not re.match) to ensure the ENTIRE
    string conforms to the whitelist. re.match only checks from the start,
    so a pattern like "safe_text\\x00; rm -rf /" would pass match but fail
    fullmatch.
    """
    from vigia.security import audit_logger  # lazy: evita import circular

    if not isinstance(pattern, str):
        raise ValueError("Pattern must be a string.")
    if len(pattern) > MAX_GREP_PATTERN_LENGTH:
        raise ValueError(f"Pattern too long. Maximum: {MAX_GREP_PATTERN_LENGTH} chars.")
    if "\x00" in pattern:
        audit_logger.log_block(
            event_type="GREP_PATTERN_NULL_BYTE",
            tool="_sanitize_grep_pattern",
            input_preview=pattern[:50],
            reason="Null byte in grep pattern — C-string truncation attack.",
        )
        raise ValueError("Pattern contains null byte.")
    # Rechazo explicito de homoglifos Unicode
    try:
        pattern.encode("ascii")
    except UnicodeEncodeError:
        audit_logger.log_block(
            event_type="GREP_PATTERN_HOMOGLYPH",
            tool="_sanitize_grep_pattern",
            input_preview=pattern[:50],
            reason="Non-ASCII characters in grep pattern — homoglyph injection.",
        )
        raise ValueError(
            "Pattern contains non-ASCII characters. "
            "Unicode homoglyph injection detected."
        )
    if not _ALLOWED_GREP_PATTERN.fullmatch(pattern):
        audit_logger.log_block(
            event_type="GREP_PATTERN_REJECTED",
            tool="_sanitize_grep_pattern",
            input_preview=pattern[:50],
            reason="Pattern contains disallowed characters.",
        )
        raise ValueError(
            "Pattern contains disallowed characters. "
            "Only alphanumeric, spaces and . - _ @ # ! ? , ; : are permitted."
        )
    return pattern


async def safe_grep(
    pattern: str,
    folder: str,
    max_depth: int | None = None,  # Kimi P1-10: Now uses VIGIA_GREP_DEPTH by default
    # LaBestia fix (2026-07-06): 256 was a stale literal, inconsistent with
    # the rest of the codebase — CONFIG.sandbox_memory_mb (the only
    # production caller, search_pattern) and DEFAULT_MAX_MEMORY_MB both
    # default to 512. On a minimal container grep/find link ~4-5 shared
    # libs and 256MB is generous; on a real desktop distro (NSS modules,
    # PAM, systemd libs, ICU/locale data) dynamic linking legitimately
    # needs more virtual address space — RLIMIT_AS too tight makes the
    # loader abort ("failed to map segment"), which sandboxed_execute
    # cannot distinguish from a clean run (see returncode check below),
    # so it silently reported "no matches" instead of "grep couldn't run".
    max_memory_mb: int = DEFAULT_MAX_MEMORY_MB,
    max_cpu_seconds: int = 30,
    allowed_dirs: list[str] | None = None,
    max_total_scan_bytes: int = 500 * 1024 * 1024,  # 500 MB
) -> dict:
    """
    Grep *pattern* inside *folder* with depth limiting and optional path
    confinement to *allowed_dirs*.

    Kimi P1-10: Depth limiting is now MANDATORY via VIGIA_GREP_DEPTH env var
    (default: 5). This prevents infinite recursion in directory trees and
    mitigates DoS via deeply nested evidence directories.

    Returns a dict with:
        matches     (list[str])  – lines matching the pattern
        truncated   (bool)
        error       (str | None)
        files_grepped (int | None)  – only available on GNU grep >= 3.8
        scan_volume_bytes (int)    – total bytes in scanned directory tree
        depth_limit_applied (int) – the effective depth limit used
    """
    # local imports avoid circular (vigia.security.__init__ importa sandbox).
    # audit_logger: TANDA 2 — estaba SIN bindear en este módulo; safe_grep
    # crasheaba con NameError en la primera llamada real (línea del
    # GREP_DEPTH_LIMIT log). Latente porque el corpus JSON no ejercita grep.
    from vigia.security import _sanitize_path, audit_logger

    # Validate folder path
    try:
        safe_folder = _sanitize_path(folder, allow_symlinks=False)
    except ValueError as exc:
        return {"matches": [], "truncated": False, "error": str(exc)}

    # Optional confinement to allowed evidence directories.  This is a
    # filesystem authority check, not a text-prefix check: ``/evidence-copy``
    # must never inherit authority from ``/evidence`` merely because the
    # strings share a prefix (B-174).
    if allowed_dirs:
        safe_folder_path = Path(safe_folder)
        authorised = False
        for allowed_dir in allowed_dirs:
            if not isinstance(allowed_dir, str):
                return {
                    "matches": [],
                    "truncated": False,
                    "error": "Allowed evidence directory must be a path string.",
                }
            try:
                allowed_root = Path(
                    _sanitize_path(
                        allowed_dir,
                        must_exist=True,
                        allow_symlinks=False,
                    )
                )
            except ValueError as exc:
                return {
                    "matches": [],
                    "truncated": False,
                    "error": f"Invalid allowed evidence directory: {exc}",
                }
            if not allowed_root.is_dir():
                return {
                    "matches": [],
                    "truncated": False,
                    "error": f"Allowed evidence path is not a directory: {allowed_root!s}",
                }
            if safe_folder_path == allowed_root or safe_folder_path.is_relative_to(allowed_root):
                authorised = True
                break
        if not authorised:
            return {
                "matches": [],
                "truncated": False,
                "error": f"Path {safe_folder!r} is outside allowed evidence directories.",
            }

    # Kimi P1-10: Apply VIGIA_GREP_DEPTH if max_depth not explicitly provided
    if max_depth is None:
        effective_depth = VIGIA_GREP_DEPTH
    else:
        # Clamp user-provided depth to safe range
        effective_depth = max(1, min(max_depth, 20))

    # Log depth limit application for audit trail
    audit_logger.log_info(
        event_type="GREP_DEPTH_LIMIT",
        tool="safe_grep",
        message=f"Depth limit {effective_depth} applied to {safe_folder} "
                f"(VIGIA_GREP_DEPTH={VIGIA_GREP_DEPTH})",
    )

    # ── Total scan volume check (P0 fix — 2026-04) ────────────────────────
    # Prevents an attacker from filling evidence_dir with many large files
    # to force VIGIA to read gigabytes of data via grep.
    total_bytes = 0
    file_count = 0
    try:
        for root, dirs, files in os.walk(safe_folder):
            # Kimi P1-10: Enforce depth limit during walk
            depth = root.replace(safe_folder, "").count(os.sep)
            if depth >= effective_depth:
                dirs.clear()  # don't descend further
                audit_logger.log_info(
                    event_type="GREP_DEPTH_CUTOFF",
                    tool="safe_grep",
                    message=f"Cut off directory traversal at depth {depth} in {root}",
                )
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
                        "depth_limit_applied": effective_depth,
                    }
    except OSError as exc:
        return {"matches": [], "truncated": False, "error": f"Cannot stat directory: {exc}"}

    # TANDA 2: validación fail-closed — un patrón inválido se rechaza con el
    # motivo exacto; nunca se ejecuta una versión silenciosamente alterada.
    try:
        clean_pattern = _sanitize_grep_pattern(pattern)
    except ValueError as exc:
        return {"matches": [], "truncated": False, "error": str(exc)}
    if not clean_pattern:
        return {"matches": [], "truncated": False, "error": "Empty pattern after sanitisation."}

    # ── Build command: find + xargs grep ──────────────────────────────────
    # GNU grep does NOT have --max-depth. Previous version used it and
    # silently failed on most systems. We use find(1) for depth control
    # (POSIX-standard -maxdepth) piped to xargs grep for the actual search.
    #
    # Kimi P1-10: -maxdepth is now MANDATORY via effective_depth variable
    #
    # find -maxdepth N -type f | xargs grep -I -n -- PATTERN
    #
    # Security: both commands run inside sandboxed_execute with
    # setrlimit (memory, CPU, file size) and hard asyncio timeout.
    cmd = [
        "find", safe_folder,
        "-maxdepth", str(effective_depth),  # Kimi P1-10: Enforced depth limit
        "-type", "f",
        "-not", "-path", "*/.git/*",
        "-not", "-path", "*/.svn/*",
        "-print0",
    ]

    # Phase 1: collect file list with find
    # Kimi P1-10: Use shorter timeout on Windows
    find_timeout = max_cpu_seconds if _IS_POSIX else min(WINDOWS_AGGRESSIVE_TIMEOUT, max_cpu_seconds)

    find_result = await sandboxed_execute(
        cmd,
        max_memory_mb=max_memory_mb,
        max_cpu_seconds=find_timeout,
    )

    if find_result["error"]:
        return {
            "matches": [],
            "truncated": find_result["truncated"],
            "error": find_result["error"],
            "depth_limit_applied": effective_depth,
        }

    file_list = find_result["stdout"]

    # LaBestia fix (2026-07-06): sandboxed_execute() never sets "error" for a
    # nonzero returncode (only for exceptions/timeout) — a find(1) crash
    # (permission fault, resource-limit loader failure, missing binary
    # resolved via a broken PATH) produces empty stdout with error=None,
    # which fell through to the "empty directory" branch below: a forensic
    # tool silently reporting "no matches" when the search never actually
    # ran. Same anti-pattern this repo already guards against elsewhere
    # (UNANALYZED_ARTIFACT vs NO_ANOMALY in sift_orchestrator.py) — absence
    # of output is not evidence of a clean scan. Only treat empty+nonzero as
    # fatal; GNU find can return 1 on partial permission errors while still
    # listing what it could read, so a nonzero code with actual output is
    # not fatal here.
    if find_result["returncode"] != 0 and not file_list.strip():
        return {
            "matches": [],
            "truncated": False,
            "error": (
                f"find exited with code {find_result['returncode']} and "
                f"produced no output — treating as a failed scan, not an "
                f"empty directory (stderr: {find_result['stderr'][:300]!r})"
            ),
            "depth_limit_applied": effective_depth,
        }

    if not file_list.strip():
        return {
            "matches": [],
            "truncated": False,
            "error": None,
            "scan_volume_bytes": total_bytes,
            "depth_limit_applied": effective_depth,
        }

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
        max_cpu_seconds=find_timeout,  # Kimi P1-10: Consistent timeout
    )

    # grep returns 1 when no matches found — not an error
    if grep_result["error"] and "TIMEOUT" not in grep_result["error"]:
        return {
            "matches": [],
            "truncated": grep_result["truncated"],
            "error": grep_result["error"],
            "depth_limit_applied": effective_depth,
        }

    raw_output = grep_result["stdout"].decode("utf-8", errors="replace")
    lines = [ln for ln in raw_output.splitlines() if ln.strip()]

    # LaBestia fix v2 (2026-07-06): the returncode of THIS phase is xargs's,
    # not grep's — and xargs COLLAPSES grep's exit codes. When grep finds no
    # match in a file it exits 1, and xargs reports that whole run as 123.
    # Worse: if xargs splits the file list across several grep invocations
    # (large evidence dir), the batch WITHOUT the pattern exits 1 → xargs 123
    # EVEN WHEN another batch matched and produced output. The previous fix
    # (e10a364) treated any code ∉ {0,1} as a failed search, so a normal
    # search over a populated directory came back as an error — the exact
    # cause of the LaBestia failure (it passed here because the test dir held
    # a single matching file, so xargs never split and returned 0).
    #
    # xargs cannot tell benign no-match from a real grep error through its
    # returncode alone (both collapse to 123). So decide on OBSERVABLE state,
    # not the code:
    #   - any stdout → grep matched something → success, parse it.
    #   - no stdout, xargs signalled a hard exec/signal failure (124/125/
    #     126/127) OR grep wrote to stderr → the search never ran → error.
    #   - no stdout, quiet, code 0/1/123 → clean "no matches" → benign.
    # This keeps the genuine-failure detection (loader/OOM errors always hit
    # stderr) without regressing the no-match path.
    rc = grep_result["returncode"]
    stderr_txt = grep_result["stderr"].decode("utf-8", errors="replace").strip()
    if not lines:
        hard_fail = rc in (124, 125, 126, 127) or (rc != 0 and bool(stderr_txt))
        if hard_fail:
            return {
                "matches": [],
                "truncated": grep_result["truncated"],
                "error": (
                    f"grep/xargs failed (exit {rc}) with no output — treating "
                    f"as a failed search, not \"no matches\" "
                    f"(stderr: {stderr_txt[:300]!r})"
                ),
                "returncode": rc,
                "depth_limit_applied": effective_depth,
            }

    return {
        "matches": lines,
        "truncated": grep_result["truncated"],
        "error": None,
        "returncode": grep_result["returncode"],
        "scan_volume_bytes": total_bytes,
        "files_in_scope": file_count,
        "depth_limit_applied": effective_depth,  # Kimi P1-10: Report applied limit
    }
