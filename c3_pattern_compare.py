#!/usr/bin/env python3
"""
c3_pattern_compare.py
=====================
Compara el patrón FALSE_FAMILIARITY original (subcadena) contra el fix
(límite de palabra + contexto de segunda persona) sobre el corpus real.

No modifica código; solo mide.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

CORPUS_DIR = Path("results")
BUNDLE_GLOB = "**/*_agent_bundle.json"

OLD_PATTERN = re.compile(
    r"(?i)(?:as\s+)?(?:you\s+)?(?:know|should\s+know|obviously|naturally|of\s+course)"
)
NEW_PATTERN = re.compile(
    r"(?i)\b(?:(?:as\s+)?you\s+(?:know|should\s+know)|obviously|naturally|of\s+course)\b"
)


def measure(pattern: re.Pattern) -> tuple[int, int, Counter]:
    flagged = 0
    total = 0
    matched_lines: Counter = Counter()
    for p in sorted(CORPUS_DIR.glob(BUNDLE_GLOB)):
        try:
            bundle = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        narrative_text = bundle.get("narrative")
        if not isinstance(narrative_text, str) or not narrative_text.strip():
            continue
        total += 1
        hit = False
        for line in narrative_text.splitlines():
            if pattern.search(line):
                hit = True
                matched_lines[line[:120]] += 1
        if hit:
            flagged += 1
    return total, flagged, matched_lines


def main() -> int:
    total, old_flagged, old_lines = measure(OLD_PATTERN)
    _, new_flagged, new_lines = measure(NEW_PATTERN)

    print(f"Bundles con narrative: {total}")
    print(f"Patrón antiguo marca:  {old_flagged} ({old_flagged / max(total, 1) * 100:.1f}%)")
    print(f"Patrón nuevo marca:    {new_flagged} ({new_flagged / max(total, 1) * 100:.1f}%)")
    print()

    print("Líneas más frecuentes del patrón antiguo (top 10):")
    for line, count in old_lines.most_common(10):
        print(f"  {count:>3}  {line!r}")
    print()

    if new_lines:
        print("Líneas del patrón nuevo:")
        for line, count in new_lines.most_common():
            print(f"  {count:>3}  {line!r}")
    else:
        print("Patrón nuevo: sin matches en este corpus.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
