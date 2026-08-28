"""Evidence-path confinement for the web UI's Mode 1 launcher.

Modeled on ``vigia/api_case_paths.py`` (lexical validation, no ``..``, no
symlink components between root and leaf), relaxed where evidence legitimately
differs from API case fixtures: directories are allowed (``vigia_agent.py``
accepts them) and any file extension is allowed (raw, log, json, evtx…).

Scope note (honest limitation, mirrors the module it is modeled on only in
part): no snapshot copy is taken — the agent must see the real path, and
CLAUDE.md declares evidence read-only. This confinement is therefore scope
control for what the HTTP layer may name, not a TOCTOU-proof snapshot.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

# Relative to the repo root. Directories under these roots may be named as
# --evidence targets. Deliberately excludes results/ (outputs), vigia/ (code)
# and anything outside the checkout.
EVIDENCE_ROOT_PARTS = (
    ("cases",),
    ("data", "cases"),
    ("evidence",),
    ("blind_cases_for_mcp",),
    ("results", "input"),
)

_MAX_LIST_ENTRIES = 500


class EvidencePathError(ValueError):
    """The requested evidence path is missing or outside the allowed roots."""


def _lexical_absolute(path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(candidate: Path, root: Path) -> None:
    current = candidate
    while True:
        try:
            if current.is_symlink():
                raise EvidencePathError("evidence path must not traverse a symlink")
        except OSError as exc:
            raise EvidencePathError("evidence path could not be inspected") from exc
        if current == root:
            return
        current = current.parent


def resolve_evidence_path(repo, requested: str) -> Path:
    """Return a validated absolute path to a file or directory beneath one of
    the declared evidence roots. Rejects instead of repairing."""
    if not isinstance(requested, str) or not requested:
        raise EvidencePathError("evidence path must be non-empty text")

    raw = Path(requested)
    if raw.is_absolute() or ".." in raw.parts:
        raise EvidencePathError("evidence path must be a confined relative path")

    parts = raw.parts
    root_parts = None
    for candidate_root in EVIDENCE_ROOT_PARTS:
        if parts[: len(candidate_root)] == candidate_root and len(parts) > len(candidate_root):
            root_parts = candidate_root
            break
    if root_parts is None:
        allowed = ", ".join("/".join(r) for r in EVIDENCE_ROOT_PARTS)
        raise EvidencePathError(
            f"evidence path is outside declared evidence roots ({allowed})"
        )

    repo_root = _lexical_absolute(repo)
    candidate = _lexical_absolute(repo_root / raw)
    root = _lexical_absolute(repo_root.joinpath(*root_parts))

    _reject_symlink_components(candidate, root)
    try:
        metadata = candidate.lstat()
    except FileNotFoundError as exc:
        raise EvidencePathError("evidence path does not exist") from exc
    except OSError as exc:
        raise EvidencePathError("evidence path could not be inspected") from exc
    if not (stat.S_ISREG(metadata.st_mode) or stat.S_ISDIR(metadata.st_mode)):
        raise EvidencePathError("evidence path must be a regular file or directory")
    return candidate


def list_evidence_roots(repo) -> dict:
    """Shallow listing of the allowlisted evidence roots for the UI picker.
    Symlinks are omitted entirely — they could point outside the scope."""
    repo_root = _lexical_absolute(repo)
    roots = []
    for root_parts in EVIDENCE_ROOT_PARTS:
        root = repo_root.joinpath(*root_parts)
        if not root.is_dir() or root.is_symlink():
            continue
        entries = []
        try:
            children = sorted(root.iterdir())
        except OSError:
            continue
        for child in children[:_MAX_LIST_ENTRIES]:
            try:
                if child.is_symlink():
                    continue
                kind = "dir" if child.is_dir() else "file"
                size = child.stat().st_size if kind == "file" else None
            except OSError:
                continue
            entries.append({"rel_path": child.name, "kind": kind, "size": size})
        roots.append({"root": "/".join(root_parts), "entries": entries})
    return {"roots": roots}
