"""Versioned, content-addressed identity for the deterministic agent runtime.

The fingerprint intentionally covers the three root execution modules and the
``vigia/`` package, not generated evidence, reports, tests, or repository
metadata.  A sealed result can therefore be reused only when it was produced
from the same source runtime as the caller is about to invoke.
"""

from __future__ import annotations

import hashlib
import os
import stat
import sys
from pathlib import Path
from typing import Iterable, Mapping


_MANIFEST_VERSION = b"VIGIA_RUNTIME_SOURCE_MANIFEST_V1\0"
_EXECUTION_CONTEXT_VERSION = b"VIGIA_RUNTIME_EXECUTION_CONTEXT_V1\0"
_ROOT_RUNTIME_FILES = (
    "vigia_agent.py",
    "vigia_scorer.py",
    "sift_orchestrator.py",
)


def _regular_source(path: Path) -> bool:
    """Return True only for a regular, non-symlink source file."""
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise RuntimeError(f"cannot stat runtime source: {path}") from exc
    if stat.S_ISLNK(mode):
        raise RuntimeError(f"runtime source symlink is not permitted: {path}")
    return stat.S_ISREG(mode)


def runtime_source_paths(repo_root: Path | str) -> Iterable[Path]:
    """Yield the deterministic source scope in canonical relative-path order."""
    root = Path(repo_root).resolve(strict=True)
    paths: list[Path] = []
    for name in _ROOT_RUNTIME_FILES:
        candidate = root / name
        if not _regular_source(candidate):
            raise RuntimeError(f"runtime entrypoint is not a regular file: {candidate}")
        paths.append(candidate)

    package_root = root / "vigia"
    if not package_root.is_dir():
        raise RuntimeError(f"runtime package is absent: {package_root}")
    for candidate in package_root.rglob("*.py"):
        if _regular_source(candidate):
            paths.append(candidate)

    return tuple(sorted(paths, key=lambda p: p.relative_to(root).as_posix()))


def runtime_source_fingerprint(repo_root: Path | str) -> str:
    """Return a SHA-256 manifest of all deterministic runtime source bytes.

    This is a provenance identifier, not a cryptographic signature.  It is
    deliberately strict: an unreadable or symlinked source file prevents cache
    reuse rather than silently producing a weaker identity.
    """
    root = Path(repo_root).resolve(strict=True)
    digest = hashlib.sha256()
    digest.update(_MANIFEST_VERSION)
    for path in runtime_source_paths(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        file_digest = hashlib.sha256(path.read_bytes()).digest()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(file_digest)
    return digest.hexdigest()


def _context_value(name: str, value: str) -> bytes:
    """Represent a semantic environment value without serializing secrets."""
    secret_markers = ("KEY", "TOKEN", "SECRET", "SALT", "PASSWORD")
    if any(marker in name for marker in secret_markers):
        return b"<present>" if value else b"<absent>"
    return value.encode("utf-8", "surrogateescape")


def runtime_execution_fingerprint(
    repo_root: Path | str,
    environment: Mapping[str, str] | None = None,
) -> str:
    """Hash source identity plus decision-relevant, non-secret process context.

    VIGÍA's deterministic entry point is configured by ``VIGIA_*`` variables
    such as ``VIGIA_EBS_RESOLVE`` and ``VIGIA_VOL3_TIMEOUT``.  Values are
    incorporated without serializing them into bundles.  Secret-shaped values
    contribute only presence/absence so a cache identity cannot leak keys.
    """
    env = os.environ if environment is None else environment
    digest = hashlib.sha256()
    digest.update(_EXECUTION_CONTEXT_VERSION)
    digest.update(runtime_source_fingerprint(repo_root).encode("ascii"))
    interpreter = (
        f"{sys.implementation.name}:{sys.version_info.major}."
        f"{sys.version_info.minor}.{sys.version_info.micro}"
    ).encode("ascii")
    digest.update(len(interpreter).to_bytes(4, "big"))
    digest.update(interpreter)
    names = sorted(
        name for name in env
        if name.startswith("VIGIA_") or name == "PYTHONHASHSEED"
    )
    for name in names:
        key = name.encode("utf-8")
        value = _context_value(name, str(env[name]))
        digest.update(len(key).to_bytes(4, "big"))
        digest.update(key)
        digest.update(len(value).to_bytes(4, "big"))
        digest.update(value)
    return digest.hexdigest()
