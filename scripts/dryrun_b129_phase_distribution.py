#!/usr/bin/env python3
"""
B-129 / L-027 groundwork — empirical detect_phase() distribution on the
JSON corpus.

The 2026-08-01 B-129 addendum prescribed, before designing ANY
tool_name -> artifact_type mapping table: measure which IRPhases
VisibleVariablesEngine.detect_phase() actually detects over the real
corpus, given the mitre_ttps / temporal_violations that exist TODAY (not
the theoretical universe of 15 phases). This script is that measurement.

Three sections:

1. HONEST RUN — detect_phase() with the inputs the JSON corpus really
   carries. Corpus census (2026-08-27): the input field `mitre_ttps`
   exists in 0/209 cases (what exists is `expected_mitre_ttps`, an
   EXPECTED-OUTPUT label — feeding it as input would be label leakage,
   the same class as B-162's label-leak guards). `temporal_violations`
   is non-empty in 15 cases.

2. VIOLATION-TYPE TABLE COVERAGE — which observed temporal_violation
   types are present in TEMPORAL_VIOLATION_TO_PHASE. Notably,
   EFFECT_BEFORE_CAUSE (the only violation type the scorer validates as
   authoritative, B-172) is absent from the table.

3. COUNTERFACTUAL CEILING — clearly labeled as NOT an honest input:
   detect_phase() fed with expected_mitre_ttps, to answer "if a TTP
   producer existed and matched the labels, which phases would become
   detectable, and how much of the label vocabulary does
   MITRE_TTP_TO_PHASE cover?" This bounds the value of building the
   producer; it must never be wired as live input.

Determinism: every case is computed twice; the script aborts on any
divergence. Observation only: exit 0, nothing written, nothing wired.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_b129_phase_distribution.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from dryrun_signal_quality_gate import find_cases  # noqa: E402
from vigia.tools.visible_variables import (  # noqa: E402
    MITRE_TTP_TO_PHASE,
    TEMPORAL_VIOLATION_TO_PHASE,
    VisibleVariablesEngine,
)


def _load_cases() -> list[tuple[str, dict]]:
    out = []
    for path in find_cases():
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(case, dict):
            out.append((path.stem, case))
    return out


def _detect(engine: VisibleVariablesEngine, case: dict, ttps) -> tuple[str, int]:
    signals = [s for s in (case.get("signals") or []) if isinstance(s, dict)]
    violations = [
        v for v in (case.get("temporal_violations") or []) if isinstance(v, dict)
    ]
    phase, consistency = engine.detect_phase(
        signals=signals,
        temporal_violations=violations or None,
        mitre_ttps=ttps or None,
    )
    return phase.value, consistency


def main() -> None:
    engine = VisibleVariablesEngine()
    cases = _load_cases()
    print(f"Corpus loaded: {len(cases)} cases")
    print()

    # --- 1. Honest run -----------------------------------------------------
    print("1. HONEST RUN (real corpus inputs: no mitre_ttps field exists; "
          "temporal_violations as carried)")
    dist: Counter = Counter()
    consistencies: Counter = Counter()
    for stem, case in cases:
        r1 = _detect(engine, case, None)
        r2 = _detect(engine, case, None)
        if r1 != r2:
            print(f"DETERMINISM VIOLATION: {stem}: {r1} != {r2}")
            sys.exit(1)
        dist[r1[0]] += 1
        consistencies[r1[1]] += 1
    print(f"   phase distribution: {dict(dist.most_common())}")
    print(f"   consistency distribution: {dict(consistencies.most_common())}")
    print()

    # --- 2. Violation-type table coverage ----------------------------------
    print("2. TEMPORAL VIOLATION TYPE COVERAGE vs TEMPORAL_VIOLATION_TO_PHASE")
    observed: Counter = Counter()
    for _, case in cases:
        for v in (case.get("temporal_violations") or []):
            if isinstance(v, dict):
                observed[str(v.get("type", "")).upper()] += 1
    table_keys = set(TEMPORAL_VIOLATION_TO_PHASE)
    mapped = {t: n for t, n in observed.items() if t in table_keys}
    unmapped = {t: n for t, n in observed.items() if t not in table_keys}
    print(f"   table keys ({len(table_keys)}): {sorted(table_keys)}")
    print(f"   observed types mapped by table: {mapped or '{}'}")
    print(f"   observed types NOT in table: {dict(sorted(unmapped.items()))}")
    print()

    # --- 3. Counterfactual ceiling (NOT an honest input) --------------------
    print("3. COUNTERFACTUAL CEILING — expected_mitre_ttps fed as input "
          "(LABEL, not pipeline output; never wire this)")
    dist_cf: Counter = Counter()
    label_ttps: Counter = Counter()
    for stem, case in cases:
        ttps = [
            str(t) for t in (case.get("expected_mitre_ttps") or [])
            if isinstance(t, str)
        ]
        label_ttps.update(ttps)
        r1 = _detect(engine, case, ttps)
        r2 = _detect(engine, case, ttps)
        if r1 != r2:
            print(f"DETERMINISM VIOLATION: {stem}: {r1} != {r2}")
            sys.exit(1)
        dist_cf[r1[0]] += 1
    known = {t: n for t, n in label_ttps.items() if t in MITRE_TTP_TO_PHASE}
    unknown = {t: n for t, n in label_ttps.items() if t not in MITRE_TTP_TO_PHASE}
    print(f"   phase distribution: {dict(dist_cf.most_common())}")
    print(f"   distinct label TTPs: {len(label_ttps)} "
          f"(mapped by MITRE_TTP_TO_PHASE: {len(known)}, "
          f"unmapped: {len(unknown)})")
    print(f"   top mapped: {dict(Counter(known).most_common(8))}")
    print(f"   top unmapped: {dict(Counter(unknown).most_common(8))}")
    print()
    print("Observation only — nothing wired, no state written.")


if __name__ == "__main__":
    main()
