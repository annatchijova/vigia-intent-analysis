"""Confinement for filesystem-backed FastAPI case selection.

This boundary is deliberately separate from JSON-body analysis: a caller of
``/analyze/path`` may name only a regular JSON fixture beneath the repository's
declared case roots.  It does not follow symlinks while deciding that scope.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import os
import shutil
import stat
import tempfile
from pathlib import Path


class CasePathError(ValueError):
    """The requested filesystem case is missing or outside the API contract."""


_CASE_ROOT_PARTS = (("cases",), ("data", "cases"))


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


def _parse_case_request(requested: str) -> tuple[Path, tuple[str, ...], tuple[str, ...]]:
    """Validate the lexical request and identify its declared case root.

    This deliberately does no filesystem inspection.  It is shared by the
    presentation resolver and the descriptor-based snapshot opener below so
    their declared scope cannot drift.
    """
    if not isinstance(requested, str):
        raise CasePathError("case path must be text")

    raw = Path(requested)
    if raw.is_absolute() or ".." in raw.parts:
        raise CasePathError("case path must be a confined relative path")
    if raw.suffix.lower() != ".json":
        raise CasePathError("case path must name a JSON file")

    parts = raw.parts
    for root_parts in _CASE_ROOT_PARTS:
        if parts[:len(root_parts)] == root_parts and len(parts) > len(root_parts):
            return raw, root_parts, parts[len(root_parts):]
    raise CasePathError("case path is outside declared case roots")


def resolve_case_path(repo: os.PathLike[str] | str, requested: str) -> Path:
    """Return one regular ``.json`` case below ``cases/`` or ``data/cases/``.

    The function rejects instead of repairing traversal syntax.  This keeps the
    selected on-disk object and its stated acquisition path unambiguous.
    """
    raw, root_parts, _relative_parts = _parse_case_request(requested)

    repo_root = _lexical_absolute(repo)
    candidate = _lexical_absolute(repo_root / raw)
    root = _lexical_absolute(repo_root.joinpath(*root_parts))

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


def _secure_case_open_flags(*, directory: bool) -> int:
    """Return the POSIX flags required to refuse symlink traversal.

    The HTTP case selector is a forensic scope boundary.  A platform without
    descriptor-relative, no-follow opens cannot make this guarantee and must
    fail closed instead of quietly falling back to a pathname race.
    """
    required = ("O_NOFOLLOW", "O_DIRECTORY")
    if not all(hasattr(os, name) for name in required) or not hasattr(os, "open"):
        raise CasePathError("secure case opening is unavailable on this platform")
    flags = os.O_RDONLY | os.O_NOFOLLOW
    if directory:
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    return flags


def _open_case_from_repo(
    repo_root: Path,
    root_parts: tuple[str, ...],
    relative_parts: tuple[str, ...],
) -> int:
    """Open one case through trusted directory descriptors.

    ``lstat`` followed by ``open(path)`` is vulnerable to a leaf or directory
    swap in between.  Starting at the trusted repository descriptor and using
    ``dir_fd`` plus ``O_NOFOLLOW`` for every component binds the opened object
    to the inspected case tree.
    """
    directory_flags = _secure_case_open_flags(directory=True)
    file_flags = _secure_case_open_flags(directory=False)
    directory_fd: int | None = None
    try:
        directory_fd = os.open(os.fspath(repo_root), directory_flags)
        for component in (*root_parts, *relative_parts[:-1]):
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        file_fd = os.open(relative_parts[-1], file_flags, dir_fd=directory_fd)
        metadata = os.fstat(file_fd)
        if not stat.S_ISREG(metadata.st_mode):
            os.close(file_fd)
            raise CasePathError("case path must be a regular file")
        return file_fd
    except CasePathError:
        raise
    except OSError as exc:
        raise CasePathError("case path changed or could not be safely opened") from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


@contextmanager
def snapshot_case_file(
    repo: os.PathLike[str] | str, requested: str
) -> Iterator[Path]:
    """Yield a private immutable-in-practice copy of one verified case file.

    The API uses the snapshot for both the deterministic pipeline and optional
    narration, so neither can reopen a caller-selected pathname after it was
    checked.  The temporary file has the platform's private ``NamedTemporaryFile``
    permissions and is removed on every normal or exceptional exit.
    """
    raw, root_parts, relative_parts = _parse_case_request(requested)
    repo_root = _lexical_absolute(repo)
    # Preserve the existing regular-file/not-symlink contract for errors and
    # then bind the actual open to directory descriptors.  The second step is
    # authoritative: it handles a replacement after this inspection returns.
    resolve_case_path(repo_root, str(raw))
    file_fd = _open_case_from_repo(repo_root, root_parts, relative_parts)
    snapshot: Path | None = None
    try:
        with os.fdopen(file_fd, "rb") as source:
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as target:
                snapshot = Path(target.name)
                shutil.copyfileobj(source, target, length=64 * 1024)
                target.flush()
                os.fsync(target.fileno())
    except OSError as exc:
        if snapshot is not None:
            try:
                snapshot.unlink()
            except FileNotFoundError:
                pass
        raise CasePathError("case file could not be snapshotted safely") from exc
    try:
        yield snapshot
    finally:
        if snapshot is not None:
            try:
                snapshot.unlink()
            except FileNotFoundError:
                pass
