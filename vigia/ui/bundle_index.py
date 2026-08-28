"""Bundle index for the VIGÍA web UI.

Scans the result roots for ``*.json`` bundle files, classifies each with the
normalizer's schema detector, and hands the HTTP layer an opaque id per file:
``bundle_id = sha256(rel_path)[:16]``. The HTTP layer resolves ids through
this map only and never accepts a raw path for reads, which structurally
removes path traversal from the read side.

``*_reasoning_trace.json`` and ``*.sha256`` files are not indexed as bundles;
they are recorded as attributes of their sibling bundle. Files whose JSON
fails to parse are listed honestly with ``schema="unparseable"`` rather than
hidden.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

from vigia.ui import normalizer

logger = logging.getLogger("vigia.ui.bundle_index")

# Relative to the repo root. Recursive.
DEFAULT_SCAN_ROOTS = (
    ("results",),
    ("cases",),
    ("vigia", "results"),
)

SCHEMA_UNPARSEABLE = "unparseable"

_MAX_PARSE_BYTES = 50 * 1024 * 1024  # refuse to parse anything absurd


def bundle_id_for(rel_path: str) -> str:
    return hashlib.sha256(rel_path.encode("utf-8")).hexdigest()[:16]


class BundleIndex:
    """In-memory index over the bundle corpus, cached per (mtime, size)."""

    def __init__(self, repo_root: Path, scan_roots=DEFAULT_SCAN_ROOTS):
        self.repo_root = Path(repo_root).resolve()
        self.scan_roots = scan_roots
        # bundle_id -> entry dict; entry["abs_path"] is internal, not serialized
        self._entries: dict[str, dict] = {}
        # rel_path -> (mtime_ns, size) snapshot of the last scan
        self._stat_cache: dict[str, tuple] = {}

    # -- scanning -----------------------------------------------------------

    def _iter_candidate_files(self):
        for root_parts in self.scan_roots:
            root = self.repo_root.joinpath(*root_parts)
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*.json")):
                if not path.is_file():
                    continue
                if path.name.endswith("_reasoning_trace.json"):
                    continue
                yield path

    def _summarize(self, path: Path, rel_path: str) -> dict:
        entry = {
            "id": bundle_id_for(rel_path),
            "rel_path": rel_path,
            "abs_path": path,
            "schema": SCHEMA_UNPARSEABLE,
            "case_id": None,
            "verdicts": [],
            "sealed_at": None,
            "size_bytes": path.stat().st_size,
            "has_sha256_sidecar": path.with_name(path.name + ".sha256").exists(),
            "has_reasoning_trace": path.with_name(
                path.name.replace(".json", "_reasoning_trace.json")
            ).exists(),
        }
        if entry["size_bytes"] > _MAX_PARSE_BYTES:
            return entry
        try:
            doc = normalizer.load_bundle(path)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return entry
        norm = normalizer.normalize(doc, rel_path)
        entry["schema"] = norm["schema"]
        entry["case_id"] = norm["case_id"]
        entry["sealed_at"] = norm["sealed_at"]
        entry["verdicts"] = [
            {"source": v["source"], "verdict": v["verdict"]}
            for v in norm["verdicts"]
        ]
        entry["verdict_disagreement"] = norm["verdict_disagreement"]
        return entry

    def refresh(self, force: bool = False) -> None:
        """Rescan roots; re-summarize only files whose (mtime, size) changed."""
        seen: set[str] = set()
        for path in self._iter_candidate_files():
            rel_path = str(path.relative_to(self.repo_root))
            seen.add(rel_path)
            st = path.stat()
            sig = (st.st_mtime_ns, st.st_size)
            if not force and self._stat_cache.get(rel_path) == sig:
                continue
            entry = self._summarize(path, rel_path)
            self._entries[entry["id"]] = entry
            self._stat_cache[rel_path] = sig
        # drop deleted files
        for rel_path in list(self._stat_cache):
            if rel_path not in seen:
                del self._stat_cache[rel_path]
                self._entries.pop(bundle_id_for(rel_path), None)

    # -- queries ------------------------------------------------------------

    def get(self, bundle_id: str) -> Optional[dict]:
        return self._entries.get(bundle_id)

    def register_file(self, path: Path) -> Optional[dict]:
        """Index a single new file (e.g. a bundle a job just sealed).
        Returns the entry, or None when the path is outside the repo root."""
        path = Path(path).resolve()
        try:
            rel_path = str(path.relative_to(self.repo_root))
        except ValueError:
            logger.warning("refusing to index file outside repo root: %s", path)
            return None
        entry = self._summarize(path, rel_path)
        self._entries[entry["id"]] = entry
        st = path.stat()
        self._stat_cache[rel_path] = (st.st_mtime_ns, st.st_size)
        return entry

    def query(self, verdict: Optional[str] = None, schema: Optional[str] = None,
              case: Optional[str] = None, q: Optional[str] = None,
              limit: int = 100, offset: int = 0) -> dict:
        rows = list(self._entries.values())
        if verdict:
            v = verdict.upper()
            rows = [r for r in rows
                    if any((e["verdict"] or "").upper() == v for e in r["verdicts"])]
        if schema:
            rows = [r for r in rows if r["schema"] == schema]
        if case:
            needle = case.lower()
            rows = [r for r in rows if needle in (r["case_id"] or "").lower()]
        if q:
            needle = q.lower()
            rows = [r for r in rows
                    if needle in r["rel_path"].lower()
                    or needle in (r["case_id"] or "").lower()]
        rows.sort(key=lambda r: (r["sealed_at"] or "", r["rel_path"]), reverse=True)
        total = len(rows)
        page = rows[offset:offset + limit]
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [{k: v for k, v in r.items() if k != "abs_path"} for r in page],
        }

    def counts_by_schema(self) -> dict:
        counts: dict[str, int] = {}
        for r in self._entries.values():
            counts[r["schema"]] = counts.get(r["schema"], 0) + 1
        return counts

    def __len__(self) -> int:
        return len(self._entries)
