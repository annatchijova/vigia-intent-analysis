#!/usr/bin/env python3
"""
B-116 MODE C dry-run — SignalQualityGate with REAL z-scores, still UNWIRED.

MODE A/B (scripts/dryrun_signal_quality_gate.py) fed the gate raw_score
verbatim or raw_score*4 — both unit fictions. MODE C computes an honest
per-signal z-score against a BENIGN baseline with documented provenance:

    z = (raw_score - median_benign[evidence_type]) / (1.4826 * MAD_benign)

Baseline source: data/signal_calibration_dataset_20260709.json (Tanda C,
1004 labeled signals). Benign population = ground_truth in {NOISE, BENIGN}
(106 signals). Policy, stated up front (no silent caps):

  - evidence_type with n_benign >= MIN_N (5): its own (median, MAD).
  - otherwise: pooled baseline over ALL benign signals, and the type is
    listed in the report as FALLBACK_POOLED.
  - MAD floor 0.05: a degenerate MAD would make every z explode.

This script WIRES NOTHING. Exit code is always 0. It exists to measure
B-116 unblocking condition 4 ("0 true-positive MALICE cases degraded")
with real units instead of MODE B's rescaling fiction.

Usage:
    PYTHONPATH=. python3 scripts/dryrun_b116_mode_c.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from vigia.core.signal_quality_gate import SignalQualityGate  # noqa: E402
from dryrun_signal_quality_gate import find_cases  # noqa: E402

DATASET = REPO / "data" / "signal_calibration_dataset_20260709.json"
BENIGN_LABELS = {"NOISE", "BENIGN"}
MIN_N = 5
MAD_FLOOR = 0.05
MAD_TO_SIGMA = 1.4826  # consistency constant: sigma ~= 1.4826*MAD under normality


def _median(xs: list[float]) -> float:
    ys = sorted(xs)
    n = len(ys)
    mid = n // 2
    return ys[mid] if n % 2 else (ys[mid - 1] + ys[mid]) / 2.0


def build_baseline() -> tuple[dict[str, tuple[float, float]], tuple[float, float], list[str]]:
    """Returns (per-type baseline, pooled baseline, types using own baseline)."""
    data = json.loads(DATASET.read_text())
    benign = [r for r in data["records"] if r.get("ground_truth") in BENIGN_LABELS]
    by_type: dict[str, list[float]] = defaultdict(list)
    pooled: list[float] = []
    for r in benign:
        try:
            raw = float(r.get("raw_score", 0.0))
        except (TypeError, ValueError):
            continue
        by_type[str(r.get("evidence_type", "default"))].append(raw)
        pooled.append(raw)

    def stats(xs: list[float]) -> tuple[float, float]:
        med = _median(xs)
        mad = _median([abs(x - med) for x in xs])
        return med, max(mad, MAD_FLOOR)

    pooled_stats = stats(pooled)
    baseline = {t: stats(xs) for t, xs in by_type.items() if len(xs) >= MIN_N}
    return baseline, pooled_stats, sorted(baseline)


def z_for(raw: float, etype: str, baseline, pooled) -> float:
    med, mad = baseline.get(etype, pooled)
    return (raw - med) / (MAD_TO_SIGMA * mad)


def main() -> None:
    baseline, pooled, own = build_baseline()
    print("B-116 MODE C dry-run — real z-scores vs benign baseline (gate UNWIRED)")
    print(f"  Baseline dataset : {DATASET.name}")
    print(f"  Types with own baseline (n>=%d): %s" % (MIN_N, ", ".join(own)))
    print(f"  Pooled fallback  : median={pooled[0]:.3f}, MAD={pooled[1]:.3f}")

    gate = SignalQualityGate()
    cases = find_cases()
    reasons: Counter[str] = Counter()
    degraded_malice: list[str] = []
    fallback_types: Counter[str] = Counter()
    passed = 0
    evaluated = 0
    for path in cases:
        try:
            case = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(case, dict):
            continue
        sigs = []
        for art in case.get("artifacts", []):
            try:
                raw = float(art.get("raw_score", 0.0))
            except (TypeError, ValueError):
                raw = 0.0
            etype = str(art.get("evidence_type", "default"))
            if etype not in baseline:
                fallback_types[etype] += 1
            sigs.append({
                "tool_name": art.get("tool_name"),
                "source_tool": art.get("source_tool"),
                "evidence_type": etype,
                "z_score": z_for(raw, etype, baseline, pooled),
            })
        result = gate.evaluate(sigs)
        evaluated += 1
        if result.passed:
            passed += 1
        else:
            reasons[result.reason_code] += 1
            if str(case.get("expected_verdict", "")).upper() == "MALICE":
                degraded_malice.append(path.stem)

    print(f"\n=== MODE C (z = (raw - median_benigno) / (1.4826*MAD)) ===")
    print(f"  Cases evaluated : {evaluated}")
    print(f"  Passed gate     : {passed}")
    print(f"  Degraded        : {sum(reasons.values())}")
    for code, n in reasons.most_common():
        print(f"    {code:35s} {n}")
    print(f"  Degraded cases with expected_verdict=MALICE: {len(degraded_malice)}")
    for stem in degraded_malice:
        print(f"    - {stem}")
    print("\n  Evidence types WITHOUT own baseline (signals hit pooled fallback):")
    for t, n in fallback_types.most_common(15):
        print(f"    {t:28s} {n} signals")
    print("\n  Gate remains UNWIRED. Condition 4 target: 0 degraded expected-MALICE.")


if __name__ == "__main__":
    main()
