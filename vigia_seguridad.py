"""
vigia_seguridad.py — Módulo "Cocinero"
=======================================
Centralizes all security primitives for VIGÍA:
  - ASCII sanitization      (filtrar_ascii)
  - Path sandboxing         (validar_ruta)
  - Prompt injection shield (limpiar_para_llm)
  - Subprocess whitelist    (ejecutar_sift)

Import this module from vigia_sift_bridge.py; do NOT scatter security
logic across tool implementations.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import re
import subprocess
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# SANDBOX CONSTANT
# ─────────────────────────────────────────────────────────────────────────────

EVIDENCE_SANDBOX: str = os.environ.get("VIGIA_EVIDENCE_DIR", "/evidence")

# Cached resolved path — avoid a stat() syscall on every validar_ruta call.
# Re-resolved only if EVIDENCE_SANDBOX is overridden by tests at import time.
_RESOLVED_SANDBOX: pathlib.Path = pathlib.Path(EVIDENCE_SANDBOX).resolve()


# ─────────────────────────────────────────────────────────────────────────────
# SUBPROCESS WHITELIST
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_COMMANDS: frozenset = frozenset({
    "ss",               # socket statistics (network audit)
    "ewfmount",         # Expert Witness Format mounting
    "mount",            # disk image mounting
    "sha256sum",        # file integrity (fallback to hashlib)
    "vol",              # Volatility 3 memory forensics
    "vol.py",           # Volatility 3 (alternate invocation)
    "log2timeline.py",  # Plaso timeline generation
    "psort.py",         # Plaso sort/output
    "pinfo.py",         # Plaso container info
    "yara",             # YARA rule matching
})

# Argument-level whitelist: only safe shell-neutral characters permitted.
# Blocks metacharacters (; & | ` $ ( ) { } < > ! ?) in every argv slot.
_SAFE_ARG_RE = re.compile(r"^[a-zA-Z0-9/_\-\.\:@=, +]+$")


# ─────────────────────────────────────────────────────────────────────────────
# ASCII FILTER
# ─────────────────────────────────────────────────────────────────────────────

def filtrar_ascii(texto: str, reemplazar: str = "") -> str:
    """
    Strip non-ASCII codepoints from *texto*.

    Prevents homoglyph injection (e.g. Cyrillic 'е' passed as Latin 'e')
    from reaching pattern-match or log-parsing logic downstream.

    Args:
        texto:      Input string; coerced to str if needed.
        reemplazar: Replacement for each stripped character (default: remove).

    Returns:
        ASCII-only string.
    """
    if not isinstance(texto, str):
        texto = str(texto)
    return "".join(c if ord(c) < 128 else reemplazar for c in texto)


# ─────────────────────────────────────────────────────────────────────────────
# PATH SANDBOX
# ─────────────────────────────────────────────────────────────────────────────

def validar_ruta(
    ruta: str,
    base_dir: Optional[str] = None,
    debe_existir: bool = False,
) -> str:
    """
    Resolve *ruta* inside the evidence sandbox; reject traversal attempts.

    Checks (in order):
      1. Null-byte injection
      2. Dangerous patterns (.., ~, //, \\, $, `, |, ;, &)
      3. commonpath() containment inside resolved sandbox
      4. Existence (optional)

    Args:
        ruta:        Relative or absolute path supplied by caller.
        base_dir:    Sandbox root (defaults to EVIDENCE_SANDBOX).
        debe_existir: If True, raise if the resolved path does not exist.

    Returns:
        Absolute resolved path string guaranteed to be inside the sandbox.

    Raises:
        ValueError on any policy violation.
    """
    if not isinstance(ruta, str):
        raise ValueError("Path must be a string.")
    if "\x00" in ruta:
        raise ValueError("Path contains null bytes.")

    dangerous = ["..", "~", "//", "\\", "$", "`", "|", ";", "&"]
    for pat in dangerous:
        if pat in ruta:
            raise ValueError(f"Path contains dangerous pattern: {repr(pat)}")

    if base_dir is not None:
        base_resolved = pathlib.Path(base_dir).resolve()
    else:
        base_resolved = _RESOLVED_SANDBOX

    base = pathlib.Path(base_dir or EVIDENCE_SANDBOX)
    try:
        resolved = (base / ruta).resolve(strict=False)

        # Separate the commonpath call so its ValueError (different drives on
        # Windows) is NOT confused with the intentional traversal-blocked raise.
        try:
            common = os.path.commonpath([str(resolved), str(base_resolved)])
        except ValueError:
            raise ValueError(f"Invalid path resolution for: {ruta!r}")

        if common != str(base_resolved):
            raise ValueError(
                f"Path traversal blocked: {ruta!r} resolves outside {base_resolved}"
            )

        if debe_existir and not resolved.exists():
            raise ValueError(f"Path does not exist: {resolved}")

        return str(resolved)

    except (OSError, ValueError) as e:
        raise ValueError(f"Path validation failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT INJECTION SHIELD
# ─────────────────────────────────────────────────────────────────────────────

MAX_SHIELD_LENGTH: int = 10_000

_INJECTION_PATTERNS: list[str] = [
    # Role and instruction override
    r"ignore\s+(previous|all|the\s+above|your)\s+(instructions?|rules?|prompt|system)",
    r"(you\s+are|act\s+as|pretend\s+to\s+be|roleplay\s+as|simulate)\s+.{0,40}"
    r"(different|new|evil|jailbroken|unrestricted|without\s+restrictions?)",
    r"forget\s+(everything|all\s+previous|your\s+instructions?)",
    r"(new|updated|revised)\s+(instructions?|system\s+prompt|directives?|role)",
    r"disregard\s+(your|all|previous)\s+(instructions?|guidelines?|rules?|restrictions?)",
    # DAN and jailbreak
    r"\b(jailbreak|jail[-\s]?break|do[\s_]?anything[\s_]?now)\b",
    r"\b(developer|god|admin|root|superuser|unrestricted)\s+mode\b",
    r"(bypass|override|disable|circumvent)\s+(safety|filter|restriction|guardrail|alignment)",
    # Token injection / delimiter smuggling
    r"```\s*(system|instructions?|prompt|override)",
    r"<\|im_start\|>|<\|im_end\|>|<\|system\|>|\[INST\]|\[\/INST\]|<<SYS>>",
    # Prompt exfiltration
    r"(print|output|reveal|disclose|leak|exfiltrate)\s+.{0,60}"
    r"(system\s+prompt|instructions?|api\s+key|context)",
    # Authority override
    r"(anthropic|openai|developer|manufacturer)\s+(says?|allows?|permits?|has\s+authorized)",
]

_COMPILED_PATTERNS: list = [
    re.compile(p, re.IGNORECASE | re.DOTALL) for p in _INJECTION_PATTERNS
]


def limpiar_para_llm(texto: str, campo: str = "input") -> str:
    """
    Prompt injection shield for all user-supplied strings reaching the LLM.

    Truncates to MAX_SHIELD_LENGTH first (token-flooding defence), then
    scans for 13 adversarial patterns.  Raises ValueError on any match.

    Args:
        texto: User-supplied string (evidence, context, etc.).
        campo: Field name used in the error message for diagnostics.

    Returns:
        Truncated, clean string ready for LLM consumption.

    Raises:
        ValueError with "[LLMSHIELD]" prefix if injection is detected.
    """
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto[:MAX_SHIELD_LENGTH]

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(texto):
            raise ValueError(
                f"[LLMSHIELD] Prompt injection attempt detected in '{campo}'. "
                f"Input rejected to preserve forensic reasoning integrity."
            )
    return texto


# ─────────────────────────────────────────────────────────────────────────────
# SAFE SUBPROCESS EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

async def ejecutar_sift(cmd: list[str], timeout: int = 60) -> str:
    """
    Execute a whitelisted SIFT tool safely.

    Enforces two layers of validation:
      1. Binary whitelist  — argv[0] (basename) must be in ALLOWED_COMMANDS.
      2. Argument regex    — every subsequent argument must match _SAFE_ARG_RE,
                            blocking metacharacters that could enable injection
                            even without shell=True.

    No shell=True is ever used.  Raises ValueError on any policy violation.

    Args:
        cmd:     Command list, e.g. ["yara", "-r", "/rules/mal.yar", "/evidence"].
        timeout: Subprocess timeout in seconds (default 60).

    Returns:
        Combined stdout+stderr output as a decoded UTF-8 string.

    Raises:
        ValueError if whitelist or argument validation fails.
        subprocess.CalledProcessError / subprocess.TimeoutExpired on execution error.
    """
    if not cmd:
        raise ValueError("[ALLOWED_COMMANDS] Empty command list rejected.")

    executable = os.path.basename(str(cmd[0]))
    if executable not in ALLOWED_COMMANDS:
        raise ValueError(
            f"[ALLOWED_COMMANDS] '{executable}' is not a permitted SIFT tool. "
            f"Permitted executables: {sorted(ALLOWED_COMMANDS)}"
        )

    for arg in cmd[1:]:
        if not _SAFE_ARG_RE.match(arg):
            raise ValueError(
                f"[ALLOWED_COMMANDS] Argument {arg!r} contains forbidden characters. "
                f"Only alphanumerics and /_-.@:=, + are permitted."
            )

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(
        None,
        lambda: subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, timeout=timeout
        ),
    )
    return raw.decode("utf-8", errors="replace")
