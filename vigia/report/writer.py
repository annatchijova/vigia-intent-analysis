"""Write audience reports as sibling files of a sealed bundle.

Every target path goes through
``vigia.security.output_boundary.validate_external_output_path`` (refuses
``VIGIA_EVIDENCE_DIR`` and symlinked components) and is then written with
``vigia.core.atomic_io.atomic_write_text`` (temp file, fsync, rename), the same
pair every other derived-artifact writer in the repository uses.

Reports never go inside a bundle: all three families hash their whole payload,
so a presentation inside the seal would change the digest. Precedent for the
sibling layout: ``<stem>_reasoning_trace.json`` next to an agent bundle.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional

from vigia.report import AUDIENCES, LANGS
from vigia.report.adapter import load_view
from vigia.report.renderers import render

ARTIFACT_LABEL = "audience report"


def sibling_path(bundle_path: str, audience: str, lang: str,
                 output_dir: Optional[str] = None) -> str:
    """``<dir>/<stem>_report_<audience>_<lang>.md`` for a bundle path.

    ``<dir>`` is the bundle's own directory unless ``output_dir`` is given.
    A ``.json`` suffix is dropped from the stem; any other suffix is kept so
    two differently named inputs can never collide.
    """
    if audience not in AUDIENCES:
        raise ValueError(f"unknown audience {audience!r}; expected one of {AUDIENCES}")
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}; expected one of {LANGS}")
    directory, name = os.path.split(bundle_path)
    stem = name[:-5] if name.endswith(".json") else name
    target_dir = output_dir if output_dir is not None else (directory or ".")
    return os.path.join(target_dir, f"{stem}_report_{audience}_{lang}.md")


def write_report(text: str, output_path: str) -> str:
    """Validate the boundary, then write atomically. Returns the resolved path.

    Raises ``vigia.security.output_boundary.SecurityError`` when the target is
    inside ``VIGIA_EVIDENCE_DIR`` or crosses a symlink. The imports are local
    so that importing ``vigia.report`` stays free of the security package.
    """
    from vigia.core.atomic_io import atomic_write_text
    from vigia.security.output_boundary import validate_external_output_path

    target = validate_external_output_path(output_path, artifact_label=ARTIFACT_LABEL)
    parent = os.path.dirname(target)
    if parent:
        os.makedirs(parent, exist_ok=True)
    atomic_write_text(target, text)
    return target


def write_all(bundle_path: str, audiences: Iterable[str] = AUDIENCES,
              langs: Iterable[str] = LANGS, output_dir: Optional[str] = None) -> list[str]:
    """Render and write every requested (audience, lang) pair for one bundle.

    Returns the written paths in a fixed order (audiences, then langs, as
    given). Raises ``ValueError`` for an unreadable bundle and
    ``SecurityError`` for a refused target; nothing is written past the first
    failure, and the bundle file itself is never opened for writing.
    """
    with open(bundle_path, "rb") as fh:
        raw = fh.read()
    view = load_view(raw, source_name=os.path.basename(bundle_path))
    written: list[str] = []
    for audience in audiences:
        for lang in langs:
            text = render(view, audience, lang)
            written.append(write_report(text, sibling_path(bundle_path, audience, lang, output_dir)))
    return written


__all__ = ["ARTIFACT_LABEL", "sibling_path", "write_report", "write_all"]
