#!/usr/bin/env python3
"""
B-116 — fresh comparative dry-run for the SignalQualityGate shadow wiring.

The 2026-07-22 promotion to shadow mode was gated on a pre-registered
"0 flips" comparison over the 202-case corpus (snapshot before the shadow
annex existed vs after). Since then B-215, B-220, B-224, and new AI-agent
cases touched the pipeline and corpus. This re-measures the same invariant
against the CURRENT corpus and CURRENT scorer: does the shadow annex ever
change verdict/score/confidence?

Method: run _vigia_score(case) once with the real shadow_signal_quality
wired (today's behavior), and once with it monkeypatched to a stub that
returns a fixed placeholder -- isolating exactly the shadow's causal
effect, not an arbitrary before/after diff. verdict/score/confidence are
fixed as local variables in _vigia_score BEFORE the shadow call runs (it
only appends to the result dict afterward), so a flip here would mean the
shadow call has a side effect beyond its documented contract.

Exit code is always 0 -- this is a measurement, not a gate.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_b116_shadow_refresh.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from vigia_scorer import _vigia_score  # noqa: E402
from dryrun_signal_quality_gate import find_cases  # noqa: E402

import json


def _stub_shadow(artifacts):
    return {"mode": "shadow_warn", "stubbed": True}


def main() -> None:
    cases = find_cases()
    flips = []
    shadow_dist = {"QUALITY_OK": 0, "WARN": 0, "no_annex": 0, "error": 0}
    n_evaluated = 0

    for path in cases:
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(case, dict) or "artifacts" not in case:
            continue

        try:
            with patch("vigia.core.signal_quality_shadow.shadow_signal_quality", _stub_shadow):
                baseline = _vigia_score(dict(case))
        except Exception as exc:
            print(f"[SKIP baseline-error] {path.stem}: {type(exc).__name__}: {exc}")
            continue

        try:
            real = _vigia_score(dict(case))
        except Exception as exc:
            print(f"[SKIP real-error] {path.stem}: {type(exc).__name__}: {exc}")
            continue

        n_evaluated += 1

        shadow = real.get("signal_quality_shadow")
        if shadow is None:
            shadow_dist["no_annex"] += 1
        elif isinstance(shadow, dict) and "error" in shadow:
            shadow_dist["error"] += 1
        elif isinstance(shadow, dict) and shadow.get("mode") == "shadow_warn" and not shadow.get("stubbed"):
            # Real schema (signal_quality_shadow.py): "passed": bool, not a
            # "status"/"verdict" string -- reading those (absent) keys made
            # every case fall through to the WARN default. Fixed to read
            # "passed" directly.
            if shadow.get("passed") is True:
                shadow_dist["QUALITY_OK"] += 1
            else:
                shadow_dist["WARN"] += 1
        else:
            shadow_dist["no_annex"] += 1

        for field in ("verdict", "score", "confidence"):
            b = baseline.get(field)
            r = real.get(field)
            if b != r:
                flips.append((path.stem, field, b, r))

    print(f"Corpus evaluated: {n_evaluated} cases")
    print(f"Shadow distribution (real run): {shadow_dist}")
    print()
    print(f"FLIPS (verdict/score/confidence changed by the shadow annex): {len(flips)}")
    for stem, field, b, r in flips:
        print(f"  {stem}: {field} baseline={b!r} real={r!r}")
    print()
    if not flips:
        print("PASS — 0 flips. Shadow annex remains causally inert on the current corpus/pipeline.")
    else:
        print("FAIL — shadow annex changed a sealed field. Investigate before trusting the WARN-only contract.")


if __name__ == "__main__":
    main()
