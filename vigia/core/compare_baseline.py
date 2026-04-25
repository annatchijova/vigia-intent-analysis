# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3
# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
scripts/compare_baseline.py
============================
VIGÍA vs Naive Baseline — Comparación para demo hackathon.

Uso:
    python compare_baseline.py                         # todos los casos
    python compare_baseline.py --case cases/case_002_log_fabrication.json

OUTPUT KEY:
  Naive  → promedio de raw_scores sin ajuste de confianza
  VIGÍA  → pipeline completo: TrustFusion + CorrelationDecay + CAIE
  Delta  → VIGÍA - Naive (negativo = VIGÍA es más conservador)

El momento clave del demo (Kimi roadmap):
  "case_002: Naive→MALICE. VIGÍA→SUSPICION. Delta negativo.
   Esto es exactamente el false positive que cuesta investigaciones reales."

SANS FIND EVIL Hackathon 2026
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

RED = "\033[91m"; YEL = "\033[93m"; GRN = "\033[92m"
BLU = "\033[94m"; CYA = "\033[96m"; RST = "\033[0m"; BLD = "\033[1m"

sys.path.insert(0, str(Path(__file__).parent))
from run_vigia_case import _vigia_score, _naive_score, _verdict_color


VERDICT_ORDER = {"MALICE": 2, "SUSPICION": 1, "NOISE": 0}


def verdict_changed(naive_score: float, vigia_verdict: str) -> bool:
    naive_verdict = "MALICE" if naive_score > 0.65 else "SUSPICION" if naive_score > 0.35 else "NOISE"
    return naive_verdict != vigia_verdict


def print_comparison(case: dict, vigia: dict, naive: float) -> None:
    case_id = case.get("case_id", "?")
    name = case.get("name", "?")

    naive_verdict = "MALICE" if naive > 0.65 else "SUSPICION" if naive > 0.35 else "NOISE"
    vigia_verdict = vigia["verdict"]
    changed = verdict_changed(naive, vigia_verdict)

    nvc = _verdict_color(naive_verdict)
    vvc = _verdict_color(vigia_verdict)

    delta = vigia["score"] - naive
    delta_str = f"{delta:+.4f}"
    delta_color = GRN if delta < -0.1 else RED if delta > 0.1 else ""

    print(f"\n  {BLD}[{case_id}]{RST} {name}")
    print(f"  {'─' * 60}")
    print(f"  Naive  : {nvc}{naive_verdict:10s}{RST}  score={naive:.4f}")
    print(f"  VIGÍA  : {vvc}{vigia_verdict:10s}{RST}  score={vigia['score']:.4f}  conf={vigia['confidence']:.2%}")
    print(f"  Δ Score: {delta_color}{delta_str}{RST}   Verdict changed: {'YES ← KEY' if changed else 'no'}")

    if vigia.get("hard_temporal_gate"):
        print(f"  {RED}  → HARD GATE: physical impossibility detected{RST}")

    if case.get("temporal_violations"):
        for v in case["temporal_violations"]:
            print(f"  {YEL}  → [{v.get('type')}] severity={v.get('severity'):.2f}: {str(v.get('interpretation',''))[:70]}{RST}")

    if case.get("caie_fractures"):
        for f in case["caie_fractures"]:
            print(f"  {CYA}  → FRACTURE [{f.get('fracture_type')}] sev={f.get('severity'):.2f}{RST}")

    pc = case.get("peirce_chain", {})
    if pc.get("thirdness"):
        print(f"  Thirdness: {pc['thirdness']}")


def run_comparison(case_files: list[Path]) -> None:
    print(f"\n{BLD}{'=' * 72}{RST}")
    print(f"{BLD}  VIGÍA vs NAIVE BASELINE — SANS FIND EVIL 2026{RST}")
    print(f"{'=' * 72}")

    comparisons = []
    for cf in case_files:
        with open(cf, encoding="utf-8") as f:
            case = json.load(f)
        vigia = _vigia_score(case)
        naive = _naive_score(case.get("artifacts", []))
        print_comparison(case, vigia, naive)
        comparisons.append({
            "case_id": case.get("case_id"),
            "naive_score": naive,
            "vigia_score": vigia["score"],
            "vigia_verdict": vigia["verdict"],
            "delta": vigia["score"] - naive,
            "verdict_changed": verdict_changed(naive, vigia["verdict"]),
            "expected": case.get("expected_verdict", "?"),
            "vigia_correct": vigia["verdict"] == case.get("expected_verdict", "?"),
        })

    # Resumen
    print(f"\n{'─' * 72}")
    print(f"\n  {BLD}SUMMARY{RST}")
    print(f"  {'Case':<30} {'Naive':>8} {'VIGÍA':>8} {'Delta':>8} {'Changed':>8} {'Correct':>8}")
    print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
    for c in comparisons:
        chg = f"{YEL}YES{RST}" if c["verdict_changed"] else "no"
        cor = f"{GRN}{RST}" if c["vigia_correct"] else f"{RED}{RST}"
        delta_c = GRN if c["delta"] < -0.1 else RED if c["delta"] > 0.1 else ""
        print(
            f"  {c['case_id']:<30} {c['naive_score']:>8.4f} {c['vigia_score']:>8.4f} "
            f"{delta_c}{c['delta']:>+8.4f}{RST} {chg:>8} {cor:>8}"
        )

    total = len(comparisons)
    correct = sum(1 for c in comparisons if c["vigia_correct"])
    changed = sum(1 for c in comparisons if c["verdict_changed"])
    mean_delta = sum(c["delta"] for c in comparisons) / total

    print(f"\n  Correct verdicts : {GRN}{correct}/{total}{RST}")
    print(f"  Verdict changes  : {changed}/{total}  (VIGÍA disagreed with naive)")
    print(f"  Mean delta score : {mean_delta:+.4f}")
    print(f"\n  {BLD}KEY INSIGHT:{RST}")
    print(f"  VIGÍA es más conservador en {sum(1 for c in comparisons if c['delta'] < 0)} casos.")
    print(f"  Esto significa menos falsos positivos — exactamente lo que SIFT necesita.")
    print(f"\n{'=' * 72}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compara VIGÍA vs baseline naive"
    )
    parser.add_argument("--case", help="Caso específico (JSON path)")
    parser.add_argument("--cases-dir", default="cases", help="Directorio de casos")
    args = parser.parse_args()

    if args.case:
        case_files = [Path(args.case)]
    else:
        cases_dir = Path(args.cases_dir)
        if not cases_dir.exists():
            print(f"{RED}ERROR: {cases_dir} not found{RST}")
            sys.exit(1)
        case_files = sorted(cases_dir.glob("*.json"))

    if not case_files:
        print(f"{YEL}No cases found.{RST}")
        sys.exit(0)

    run_comparison(case_files)


if __name__ == "__main__":
    main()
