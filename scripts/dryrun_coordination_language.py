#!/usr/bin/env python3
"""
B-207 dry-run — coordination-language detector against the JSON corpus,
WITHOUT wiring it to the scorer.

Answers two questions: (1) how many real corpus artifacts would this
candidate detector flag, and (2) how many ordinary/benign scheduling
messages would it false-positive on. The corpus has zero known negatives
for content-rich legacy artifacts, so a hand-built synthetic benign set
stands in for the missing polarity (see BUGS_PENDIENTES.md B-207 and the
L-033 calibration precedent this candidate does not yet meet).

The detector is NOT wired here or anywhere else. Exit code is always 0;
the output is a measurement, not a gate.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_coordination_language.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from vigia.tools.coordination_language import detect_coordination_handoff  # noqa: E402

CASES_DIRS = [
    REPO / "data/cases",
    REPO / "data/cases/converted",
    REPO / "data/cases/benign",
    REPO / "data/cases/consolidated_canonical",
    REPO / "data/cases/legacy",
]
SKIP_STEMS = {
    "_index", "dataset", "calibration", "covariance", "correlation",
    "vigia_forensic_cases", "vigia_60_cases", "vigia_cases_canonical",
    "vigia_input_defcon", "fsv_schema", "phonetic_dict",
}

# Synthetic benign scheduling messages — the corpus has no real negatives
# for content-rich legacy artifacts, so this set stands in for the missing
# polarity. Kept in sync with tests/test_b207_coordination_language_detector.py.
BENIGN_MESSAGES = [
    "let's meet for coffee at 5 tomorrow",
    "see you tonight for dinner, can't wait!",
    "I'll text you when I land",
    "call me when you're free later today",
    "running late, will message you on whatsapp when I'm close",
    "confirmation email for your flight arrives in 24 hours",
    "reminder: dentist appointment today at 3pm",
    "happy birthday! let's celebrate this weekend",
    "meeting moved to tomorrow morning, sorry for the short notice",
    "thanks for the delivery, it arrived safely",
]


def find_cases() -> list[Path]:
    seen: dict[str, Path] = {}
    for d in CASES_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            if f.stem in SKIP_STEMS or f.stem.startswith("_"):
                continue
            seen.setdefault(f.stem, f)
    return list(seen.values())


def _texts_in_content(content) -> list[str]:
    """Extract candidate text strings from an artifact's `content` field
    only — never from `metadata.significance` (authored scenario prose
    must never acquire verdict authority, per B-162)."""
    if isinstance(content, str):
        return [content]
    if isinstance(content, dict):
        return [v for v in content.values() if isinstance(v, str)]
    return []


def scan_corpus() -> None:
    cases = find_cases()
    n_cases_evaluated = 0
    n_artifacts_evaluated = 0
    matches: list[tuple[str, str, dict]] = []
    for path in cases:
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(case, dict):
            continue
        artifacts = case.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            continue
        n_cases_evaluated += 1
        for art in artifacts:
            if not isinstance(art, dict):
                continue
            n_artifacts_evaluated += 1
            for text in _texts_in_content(art.get("content")):
                finding = detect_coordination_handoff(text)
                if finding is not None:
                    matches.append((path.stem, art.get("id", art.get("artifact_id", "?")), finding))

    print(f"=== Corpus scan ({n_cases_evaluated} cases, {n_artifacts_evaluated} artifacts) ===")
    print(f"  Artifacts matched: {len(matches)}")
    cases_with_matches = sorted({m[0] for m in matches})
    print(f"  Cases with >=1 match: {len(cases_with_matches)}")
    for case_stem, artifact_id, finding in matches:
        print(f"    {case_stem} / {artifact_id}: channel={finding['matched_channel_word']!r} "
              f"timing={finding['matched_timing_phrase']!r}")


def scan_benign_set() -> None:
    print(f"\n=== Synthetic benign set ({len(BENIGN_MESSAGES)} messages) ===")
    false_positives = []
    for msg in BENIGN_MESSAGES:
        finding = detect_coordination_handoff(msg)
        if finding is not None:
            false_positives.append((msg, finding))
    print(f"  False positives: {len(false_positives)}")
    for msg, finding in false_positives:
        print(f"    {msg!r} -> channel={finding['matched_channel_word']!r} "
              f"timing={finding['matched_timing_phrase']!r}")


def main() -> None:
    print("B-207 dry-run — coordination-language detector vs corpus")
    print("Detector is NOT wired to the scorer; this is a measurement only.")
    scan_corpus()
    scan_benign_set()
    print(
        "\nCalibration status: BLOCKED per L-033 precedent (needs >=20 signals, "
        ">=3 cases per polarity, both polarities represented). See "
        "BUGS_PENDIENTES.md B-207."
    )


if __name__ == "__main__":
    main()
