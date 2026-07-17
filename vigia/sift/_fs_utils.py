"""Shared bounded filesystem helpers for the SIFT engines.

B-139: the marker-validation step of the iOS/Android/macOS engines
materialized every name in the evidence tree
(``{f.name for f in base.rglob("*")}``) before intersecting with the marker
set — O(tree) memory and an unbounded walk on a hostile or giant tree. That
is the same class S4 (AUDITORIA_COBERTURA_MOBILE_SIFT §C) closed for the
pattern-specific lookups via ``_safe_rglob``, left open at the three
``rglob("*")`` call sites (WHAT_IS_NEXT §1.3 residual). This module is the
shared, bounded replacement — same repo pattern as ``_math_utils`` (B-047)
and ``_sql_utils`` (B-071).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import AbstractSet, Set

# Generous ceiling: no legitimate mobile/macOS extraction in the corpus
# comes near this many directory entries. The bound exists so a hostile or
# runaway tree cannot make the marker scan walk (and stat) forever; hitting
# it is loudly reported, never silent.
MARKER_SCAN_MAX_ENTRIES = 500_000


def scan_marker_names(
    base: Path,
    markers: AbstractSet[str],
    *,
    engine: str,
    logger: logging.Logger,
    include_dirs: bool = False,
    max_entries: int = MARKER_SCAN_MAX_ENTRIES,
) -> Set[str]:
    """Return the subset of ``markers`` whose names exist under ``base``.

    Equivalent to ``{p.name for p in base.rglob("*") ...} & markers`` for
    any tree with at most ``max_entries`` entries, but with
    O(len(markers)) memory (only marker names are retained) and an explicit
    stop plus a visible WARNING beyond the bound — honest degradation: the
    caller keeps working and the truncation is on the record
    (ENGINEERING_DISCIPLINE §5.3), instead of an unbounded walk.

    Symlinks never count. Directories count only with ``include_dirs=True``
    (macOS: ``.fseventsd`` is a directory marker).
    """
    found: Set[str] = set()
    scanned = 0
    for p in base.rglob("*"):
        scanned += 1
        if scanned > max_entries:
            logger.warning(
                "[%s] Marker scan truncated at %d entries under %s — "
                "marker detection may be incomplete",
                engine,
                max_entries,
                base,
            )
            break
        # Name check first: it is free, while is_symlink/is_file stat the
        # filesystem — only marker-named entries pay that cost.
        if p.name not in markers or p.is_symlink():
            continue
        if p.is_file() or (include_dirs and p.is_dir()):
            found.add(p.name)
    return found
