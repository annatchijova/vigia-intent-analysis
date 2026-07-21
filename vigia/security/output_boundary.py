"""Shared write-boundary validation for derived forensic artifacts."""
from __future__ import annotations

import os
import stat
from pathlib import Path


class SecurityError(Exception):
    """A requested filesystem operation would violate a security boundary."""


def validate_external_output_path(output_path: str, *, artifact_label: str) -> str:
    """Return a canonical output target that cannot mutate source evidence.

    A caller-provided output path carries write authority. Derived artifacts
    must be validated before their parent directory exists, and every existing
    component is checked with ``lstat`` so an intermediate symlink cannot turn
    an apparently external target into an evidence write.
    """
    if not isinstance(output_path, str) or not output_path.strip():
        raise SecurityError("Output path must be a non-empty string")
    if "\x00" in output_path:
        raise SecurityError("Output path contains a null byte")

    raw_target = Path(os.path.abspath(os.path.expanduser(output_path)))
    current = Path(raw_target.anchor)
    for component in raw_target.parts[1:]:
        current /= component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            # Descendants cannot exist until this component does.
            break
        except OSError as exc:
            raise SecurityError(
                f"Cannot inspect output path component: {current}"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise SecurityError(
                f"Output path contains symlink component: {current}"
            )

    try:
        target = raw_target.resolve(strict=False)
    except OSError as exc:
        raise SecurityError(f"Cannot resolve output path: {raw_target}") from exc

    evidence_dir = os.environ.get("VIGIA_EVIDENCE_DIR", "").strip()
    if evidence_dir:
        try:
            evidence_root = Path(
                os.path.abspath(os.path.expanduser(evidence_dir))
            ).resolve(strict=False)
        except OSError as exc:
            raise SecurityError(
                f"Cannot resolve VIGIA_EVIDENCE_DIR: {evidence_dir}"
            ) from exc
        if target == evidence_root or target.is_relative_to(evidence_root):
            raise SecurityError(
                f"Refusing to write {artifact_label} inside VIGIA_EVIDENCE_DIR "
                "(forensic evidence is read-only)"
            )

    return str(target)
