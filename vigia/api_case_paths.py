"""Confinement for filesystem-backed FastAPI case selection.

This boundary is deliberately separate from JSON-body analysis: a caller of
``/analyze/path`` may name only a regular JSON fixture beneath the repository's
declared case roots.  It does not follow symlinks while deciding that scope.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path


class CasePathError(ValueError):
    """The requested filesystem case is missing or outside the API contract."""


def _lexical_absolute(path: os.PathLike[str] | str) -> Path:
    """Make a stable lexical path without resolving or following symlinks."""
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(candidate: Path, root: Path) -> None:
    """Reject a symlink at the leaf or between the candidate and its case root."""
    current = candidate
    while True:
        try:
            if current.is_symlink():
                raise CasePathError("case path must not traverse a symlink")
        except OSError as exc:
            raise CasePathError("case path could not be inspected") from exc
        if current == root:
            return
        current = current.parent


def resolve_case_path(repo: os.PathLike[str] | str, requested: str) -> Path:
    """Return one regular ``.json`` case below ``cases/`` or ``data/cases/``.

    The function rejects instead of repairing traversal syntax.  This keeps the
    selected on-disk object and its stated acquisition path unambiguous.
    """
    if not isinstance(requested, str):
        raise CasePathError("case path must be text")

    raw = Path(requested)
    if raw.is_absolute() or ".." in raw.parts:
        raise CasePathError("case path must be a confined relative path")
    if raw.suffix.lower() != ".json":
        raise CasePathError("case path must name a JSON file")

    repo_root = _lexical_absolute(repo)
    candidate = _lexical_absolute(repo_root / raw)
    roots = tuple(
        _lexical_absolute(repo_root / relative)
        for relative in (Path("cases"), Path("data") / "cases")
    )
    root = next(
        (allowed for allowed in roots if candidate == allowed or allowed in candidate.parents),
        None,
    )
    if root is None:
        raise CasePathError("case path is outside declared case roots")

    _reject_symlink_components(candidate, root)
    try:
        metadata = candidate.lstat()
    except FileNotFoundError as exc:
        raise CasePathError("case path does not exist") from exc
    except OSError as exc:
        raise CasePathError("case path could not be inspected") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise CasePathError("case path must be a regular file")
    return candidate
