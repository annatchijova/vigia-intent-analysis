#!/usr/bin/env python3
"""
clean_thinking_artifacts.py
Removes Kimi thinking-artifact lines from docs_merged/ markdown files.

Usage:
    python3 clean_thinking_artifacts.py            # preview only (no changes)
    python3 clean_thinking_artifacts.py --apply    # write changes to disk
"""

import sys
import hashlib
from pathlib import Path

DOCS_DIR = Path("/home/labestiadevigia/vigia-repo/docs_merged")

# Lines whose stripped content starts with any of these are removed.
# Order matters: more specific first to avoid redundant checks.
PREFIXES = (
    "Wait,",
    "Now ESPAÑOL:",
    "Now ENGLISH:",
    "Now ZH:",
    "Now RU:",
    "Now РУССКИЙ:",
    "Now 中文:",
    "The user wants",
    "Let me",
)


def is_artifact(line: str) -> bool:
    s = line.rstrip("\n").lstrip()
    return any(s.startswith(p) for p in PREFIXES)


def clean(lines: list[str]) -> list[str]:
    out = []
    prev_blank = False
    for line in lines:
        if is_artifact(line):
            continue
        blank = not line.strip()
        # Collapse consecutive blank lines into one
        if blank and prev_blank:
            continue
        out.append(line)
        prev_blank = blank
    return out


def sha256(lines: list[str]) -> str:
    return hashlib.sha256("".join(lines).encode()).hexdigest()


def diff_sample(path: Path, context: int = 3) -> None:
    original = path.read_text(encoding="utf-8").splitlines(keepends=True)
    cleaned  = clean(original)

    removed_idx = [i for i, l in enumerate(original) if is_artifact(l)]
    n_removed   = len(original) - len(cleaned)

    print(f"\n{'─'*64}")
    print(f"  FILE  : {path.name}")
    print(f"  BEFORE: {len(original)} lines   AFTER: {len(cleaned)} lines   (-{n_removed})")
    print(f"{'─'*64}")

    if not removed_idx:
        print("  (no artifact lines found)")
        return

    shown_blocks = 0
    reported = set()
    for idx in removed_idx:
        if shown_blocks >= 4:
            break
        start = max(0, idx - context)
        end   = min(len(original), idx + context + 1)
        # Skip if this block overlaps a already-shown block
        if any(r in range(start, end) for r in reported):
            continue
        print(f"\n  ↓ context around original line {idx + 1}")
        for i in range(start, end):
            prefix = "  ✗ " if is_artifact(original[i]) else "    "
            print(f"  {prefix}[{i+1:4d}] {original[i].rstrip()}")
        reported.update(range(start, end))
        shown_blocks += 1

    extra = len(removed_idx) - len([i for i in removed_idx if i in reported])
    if extra > 0:
        print(f"\n  ... (+{extra} more artifact lines not shown)")

    # Show tail of cleaned file
    print(f"\n  ── cleaned tail (last 4 lines) ──")
    for line in cleaned[-4:]:
        print(f"    {line.rstrip()}")


def apply_all(md_files: list[Path]) -> None:
    changed = 0
    for path in md_files:
        original = path.read_text(encoding="utf-8").splitlines(keepends=True)
        cleaned  = clean(original)
        if cleaned == original:
            continue
        n = len(original) - len(cleaned)
        path.write_text("".join(cleaned), encoding="utf-8")
        print(f"  CLEANED {path.name:40s}  -{n:3d} lines"
              f"  sha256_after={sha256(cleaned)[:12]}…")
        changed += 1
    print(f"\n  {changed} files modified, {len(md_files) - changed} unchanged.")


if __name__ == "__main__":
    apply_mode = "--apply" in sys.argv
    md_files   = sorted(DOCS_DIR.glob("*.md"))

    if not md_files:
        print(f"No .md files found in {DOCS_DIR}")
        sys.exit(1)

    # Count affected files
    affected = [f for f in md_files
                if any(is_artifact(l)
                       for l in f.read_text(encoding="utf-8").splitlines(keepends=True))]

    if not apply_mode:
        print("=" * 64)
        print("  DRY RUN — no files will be modified")
        print(f"  Patterns checked : {len(PREFIXES)}")
        print(f"  Total .md files  : {len(md_files)}")
        print(f"  Files with hits  : {len(affected)}")
        print("=" * 64)
        print("\n  Showing 3 sample diffs:\n")
        for f in affected[:3]:
            diff_sample(f)
        print(f"\n\n  Run with --apply to write all {len(affected)} files.")
    else:
        print("=" * 64)
        print("  APPLY MODE — writing changes to disk")
        print(f"  Files to modify  : {len(affected)}")
        print("=" * 64 + "\n")
        apply_all(md_files)
