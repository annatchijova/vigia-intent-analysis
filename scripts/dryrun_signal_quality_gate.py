#!/usr/bin/env python3
"""
B-116 dry-run — SignalQualityGate against the JSON corpus, WITHOUT wiring.

Reconstruction of the 2026-07-14 dry-run (the original script was run but
never committed; this version is committed so the measurement is
reproducible). It answers one question: if the gate were wired to the
scorer today, how many corpus cases would it degrade to ABSTAIN, and why?

Modes (same as the original dry-run):
  MODE A — raw_score passed directly as z_score (unit mismatch, kept for
           comparability with the 2026-07-14 numbers).
  MODE B — raw_score * 4.0 as z_score (generous rescaling).

The gate is NOT wired by this script. Exit code is always 0; the output is
a measurement, not a gate.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_signal_quality_gate.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from vigia.core.signal_quality_gate import SignalQualityGate  # noqa: E402

# Same precedence and skip list as run_all_agent.py (single source of truth
# for what counts as a corpus case).
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


def signals_for(case: dict, z_factor: float) -> list[dict]:
    sigs = []
    for art in case.get("artifacts", []):
        raw = art.get("raw_score", 0.0)
        try:
            raw = float(raw)
        except (TypeError, ValueError):
            raw = 0.0
        sigs.append({
            "tool_name": art.get("tool_name"),
            "source_tool": art.get("source_tool"),
            "evidence_type": art.get("evidence_type"),
            "z_score": raw * z_factor,
        })
    return sigs


def run_mode(cases: list[Path], z_factor: float, label: str) -> None:
    gate = SignalQualityGate()
    reasons: Counter[str] = Counter()
    degraded_malice: list[str] = []
    passed = 0
    for path in cases:
        try:
            case = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(case, dict):
            # A handful of auxiliary JSON files are top-level lists, not
            # case dicts — they are not corpus cases.
            continue
        result = gate.evaluate(signals_for(case, z_factor))
        if result.passed:
            passed += 1
        else:
            reasons[result.reason_code] += 1
            if str(case.get("expected_verdict", "")).upper() == "MALICE":
                degraded_malice.append(path.stem)
    total = passed + sum(reasons.values())
    print(f"\n=== {label} (z = raw_score * {z_factor}) ===")
    print(f"  Cases evaluated : {total}")
    print(f"  Passed gate     : {passed}")
    print(f"  Degraded        : {sum(reasons.values())}")
    for code, n in reasons.most_common():
        print(f"    {code:35s} {n}")
    print(f"  Degraded cases with expected_verdict=MALICE: {len(degraded_malice)}")
    for stem in degraded_malice:
        print(f"    - {stem}")


def main() -> None:
    cases = find_cases()
    print(f"B-116 dry-run — SignalQualityGate vs corpus ({len(cases)} cases)")
    print("Gate is NOT wired; this is a measurement only.")
    run_mode(cases, 1.0, "MODE A")
    run_mode(cases, 4.0, "MODE B")


if __name__ == "__main__":
    main()
