#!/usr/bin/env python3
"""
B-129 Fase 2 dry-run — planner weight calibration against the live scorer.

The Fase 1 observation baseline (2026-07-14, script never committed) measured
22% agreement between run_bounded_planner() and the scorer, using signal
confidence as EvidenceSignal.weight, and attributed the 90 under-alerts to
confidence being a certainty measure, not an anomaly-severity measure.

This script separates the TWO variables that were conflated in that baseline:

1. WEIGHT SOURCE — what number feeds EvidenceSignal.weight:
     conf       : signal confidence (Fase 1 baseline; the pre-calibration
                  case_to_signals logic, kept verbatim inline here so the
                  22% baseline stays reproducible)
     z          : signal z_score (corpus z_scores live in [0,1] — measured
                  2026-08-27: p95=0.855, max=0.96 — no rescaling needed);
                  artifact raw_score fallback for signal-less cases
     raw_spoof  : artifact raw_score * (1 - spoofability), spoofability from
                  the same CAIE Artifact instantiation the scorer uses
                  (vigia_scorer.py Step 1); conservative 0.50 fallback
     composite  : per artifact, max(z, raw_spoof) — the most alert-sensitive
                  combination of the two anomaly measures
     adapter    : planner_adapter.case_to_signals as shipped (calibrated to
                  raw_spoof with z fallback after this measurement — must
                  track the raw_spoof row)

2. SELECTION FUNCTION — how _select_best ranks hypotheses:
     legacy     : coverage * (1 - cost/max_cost), the pre-fix formula, kept
                  inline here so the Fase 1 baseline (22% with weight=conf)
                  stays reproducible. It gives the maximum-cost hypothesis
                  (H_MALICE, cost 4 = max) a score of exactly 0 for any
                  coverage — structurally unreachable (measured 2026-08-27:
                  0 planner MALICE over 208 cases, scorer 113).
     shipped    : the module's _select_best as fixed for B-129 Fase 2 —
                  coverage / cost, the contract its docstring always stated.

Ground truth: the live scorer verdict from _vigia_score(case) (same method
as scripts/dryrun_b116_shadow_refresh.py). Verdict mapping for agreement:
planner BENIGN <-> scorer NOISE; SUSPICION, MALICE, ABSTAIN map identically.

Determinism check: every (case, combo) is computed twice; the script aborts
on any divergence (deterministic-core discipline).

Observation only: exit 0, nothing is wired, no state is written.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_b129_weight_calibration.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Callable, Optional

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from dryrun_signal_quality_gate import find_cases  # noqa: E402
from vigia_scorer import _vigia_score  # noqa: E402
from vigia.core import peirceplanner_bounded as ppb  # noqa: E402
from vigia.core.peirceplanner_bounded import (  # noqa: E402
    EvidenceSignal,
    Hypothesis,
    HypothesisStatus,
    run_bounded_planner,
    _signal_coverage,
)
from vigia.core.planner_adapter import (  # noqa: E402
    _artifact_spoofability,
    _signal_z_fraction,
    _to_fraction,
    build_hypotheses,
    case_to_signals,
)

# ---------------------------------------------------------------------------
# Weight strategies
# ---------------------------------------------------------------------------


def _clamp01(f: Fraction) -> Fraction:
    return max(Fraction(0), min(Fraction(1), f))


# Spoofability: single source of truth is planner_adapter._artifact_spoofability
# (the same CAIE instantiation vigia_scorer.py Step 1 performs) — the copy
# this script carried was removed so the strategies cannot drift from the
# shipped adapter (adversarial review 2026-08-27).
_spoofability_for = _artifact_spoofability


def _raw_fraction(a: dict) -> Optional[Fraction]:
    raw = a.get("raw_score")
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    try:
        return _clamp01(Fraction(str(raw)).limit_denominator(10000))
    except (ValueError, ZeroDivisionError):
        return None


def signals_conf(case: dict) -> list[EvidenceSignal]:
    """Fase 1 baseline: the pre-calibration case_to_signals logic, verbatim
    (signal confidence preferred; artifact fallback with the historical
    int(raw*10)/10 conversion and its out-of-range default of 5)."""
    signals_raw = case.get("signals", [])
    if signals_raw:
        return [
            EvidenceSignal(
                signal_id=s.get("artifact_id", f"S-{i:03d}"),
                description=str(s.get("description", ""))[:200],
                weight=_to_fraction(
                    s.get("confidence", s.get("z_score", Fraction(1, 10)))
                ),
            )
            for i, s in enumerate(signals_raw)
            if isinstance(s, dict)
        ]
    return [
        EvidenceSignal(
            signal_id=a.get("artifact_id", f"A-{i:03d}"),
            description=str(a.get("description", ""))[:200],
            weight=Fraction(int(a.get("raw_score", 5) * 10), 10),
        )
        for i, a in enumerate(case.get("artifacts", []))
        if isinstance(a, dict)
    ]


def signals_z(case: dict) -> list[EvidenceSignal]:
    # Absent-vs-zero discipline mirrors the shipped adapter (adversarial
    # review 2026-08-27): a signal without z_score or an artifact without
    # raw_score is unmeasured and gets skipped, never fabricated as 0.
    out = []
    for i, s in enumerate(case.get("signals") or []):
        if not isinstance(s, dict):
            continue
        z = _signal_z_fraction(s)
        if z is None:
            continue
        out.append(EvidenceSignal(
            signal_id=s.get("artifact_id", f"S-{i:03d}"),
            description=str(s.get("description", ""))[:200],
            weight=z,
        ))
    if out:
        return out
    for i, a in enumerate(case.get("artifacts") or []):
        if not isinstance(a, dict):
            continue
        raw = _raw_fraction(a)
        if raw is None:
            continue
        out.append(EvidenceSignal(
            signal_id=a.get("artifact_id", f"A-{i:03d}"),
            description=str(a.get("description", ""))[:200],
            weight=raw,
        ))
    return out


def signals_raw_spoof(case: dict) -> list[EvidenceSignal]:
    arts = [a for a in (case.get("artifacts") or []) if isinstance(a, dict)]
    if arts:
        out = []
        for i, a in enumerate(arts):
            raw = _raw_fraction(a)
            if raw is None:
                continue
            out.append(EvidenceSignal(
                signal_id=a.get("artifact_id", f"A-{i:03d}"),
                description=str(a.get("description", ""))[:200],
                weight=_clamp01(raw * (Fraction(1) - _spoofability_for(a))),
            ))
        if out:
            return out
        # Artifacts exist but none carries raw_score (25 corpus cases at
        # first measurement): fall back to z rather than reporting
        # NO_SIGNALS for a case that does have measurable signals.
    return signals_z(case)


def signals_composite(case: dict) -> list[EvidenceSignal]:
    """max(z, raw_spoof) per artifact_id — most alert-sensitive combination."""
    z_by_id: dict[str, Fraction] = {}
    for s in (case.get("signals") or []):
        if isinstance(s, dict) and isinstance(s.get("artifact_id"), str):
            z_by_id[s["artifact_id"]] = _clamp01(_to_fraction(s.get("z_score", 0)))
    base = signals_raw_spoof(case)
    if not base:
        return signals_z(case)
    return [
        EvidenceSignal(
            signal_id=sig.signal_id,
            description=sig.description,
            weight=max(sig.weight, z_by_id.get(sig.signal_id, Fraction(0))),
        )
        for sig in base
    ]


WEIGHT_STRATEGIES: dict[str, Callable[[dict], list[EvidenceSignal]]] = {
    "conf": signals_conf,
    "z": signals_z,
    "raw_spoof": signals_raw_spoof,
    "composite": signals_composite,
    "adapter": case_to_signals,
}

# ---------------------------------------------------------------------------
# Selection functions
# ---------------------------------------------------------------------------

_SELECT_SHIPPED = ppb._select_best


def _select_legacy(
    hypotheses: list[Hypothesis],
    signals: list[EvidenceSignal],
) -> Optional[Hypothesis]:
    """Pre-fix formula, verbatim: coverage * (1 - cost/max_cost)."""
    active = [h for h in hypotheses if h.status == HypothesisStatus.ACTIVE]
    if not active:
        return None

    max_cost = max(h.ockham_cost for h in active) or Fraction(1)

    def score(h: Hypothesis) -> Fraction:
        cov = _signal_coverage(h, signals)
        norm = h.ockham_cost / max_cost if max_cost > 0 else Fraction(0)
        return cov * (Fraction(1) - norm)

    return max(active, key=score)


SELECTORS = {"legacy": _select_legacy, "shipped": _SELECT_SHIPPED}

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_PLANNER_TO_SCORER = {"BENIGN": "NOISE"}


def planner_verdict(case: dict, weights_fn, selector) -> str:
    signals = weights_fn(case)
    if not signals:
        return "NO_SIGNALS"
    ppb._select_best = selector
    try:
        result = run_bounded_planner(
            initial_hypotheses=build_hypotheses(signals),
            signals=signals,
        )
    finally:
        ppb._select_best = _SELECT_SHIPPED
    v = result.winning_hypothesis.verdict if result.winning_hypothesis else "ABSTAIN"
    return _PLANNER_TO_SCORER.get(v, v)


def main() -> None:
    cases = []
    for path in find_cases():
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(case, dict) or "artifacts" not in case:
            continue
        try:
            scored = _vigia_score(dict(case))
        except Exception as exc:
            print(f"[SKIP scorer-error] {path.stem}: {type(exc).__name__}: {exc}")
            continue
        verdict = scored.get("verdict")
        if not isinstance(verdict, str):
            print(f"[SKIP no-verdict] {path.stem}")
            continue
        cases.append((path.stem, case, verdict))

    print(f"Corpus evaluated: {len(cases)} cases")
    scorer_dist = Counter(v for _, _, v in cases)
    print(f"Scorer verdict distribution: {dict(scorer_dist.most_common())}")
    print()

    for sel_name, selector in SELECTORS.items():
        for w_name, weights_fn in WEIGHT_STRATEGIES.items():
            agree = 0
            confusion: Counter = Counter()
            planner_dist: Counter = Counter()
            for stem, case, scorer_v in cases:
                pv1 = planner_verdict(case, weights_fn, selector)
                pv2 = planner_verdict(case, weights_fn, selector)
                if pv1 != pv2:
                    print(f"DETERMINISM VIOLATION: {stem} {sel_name}/{w_name}: "
                          f"{pv1} != {pv2}")
                    sys.exit(1)
                planner_dist[pv1] += 1
                confusion[(pv1, scorer_v)] += 1
                if pv1 == scorer_v:
                    agree += 1
            pct = 100 * agree // len(cases) if cases else 0
            print(f"selector={sel_name:<7} weight={w_name:<9} "
                  f"agreement={agree}/{len(cases)} ({pct}%)  "
                  f"planner_dist={dict(planner_dist.most_common())}")
            top_disagree = [
                (f"{p}->{s}", n) for (p, s), n in confusion.most_common()
                if p != s
            ][:4]
            print(f"    top disagreements: {top_disagree}")
    print()
    print("Observation only — nothing wired, no state written.")


if __name__ == "__main__":
    main()
