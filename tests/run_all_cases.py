"""
scripts/run_all_cases.py
========================
VIGÍA — Ejecuta la suite completa de casos y genera reporte de resultados.

Uso:
    python run_all_cases.py
    python run_all_cases.py --cases-dir cases/

SANS FIND EVIL Hackathon 2026
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

RED = "\033[91m"; YEL = "\033[93m"; GRN = "\033[92m"
BLU = "\033[94m"; CYA = "\033[96m"; RST = "\033[0m"; BLD = "\033[1m"

# Importar el runner inline
sys.path.insert(0, str(Path(__file__).parent))
from run_vigia_case import _vigia_score, _naive_score, _verdict_color


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-dir", default="data/cases", help="Directorio con JSON de casos")
    args = parser.parse_args()

    cases_dir = Path(args.cases_dir)
    if not cases_dir.exists():
        print(f"{RED}ERROR: cases dir not found: {cases_dir}{RST}")
        sys.exit(1)

    case_files = sorted(cases_dir.glob("*.json"))
    if not case_files:
        print(f"{YEL}No case files found in {cases_dir}{RST}")
        sys.exit(0)

    print(f"\n{BLD}{'=' * 72}{RST}")
    print(f"{BLD}  VIGÍA — FULL FORENSIC SUITE  ({len(case_files)} cases){RST}")
    print(f"{BLD}  SANS FIND EVIL Hackathon 2026{RST}")
    print(f"{'=' * 72}\n")

    results = []
    for cf in case_files:
        with open(cf, encoding="utf-8") as f:
            raw = json.load(f)
        
        # Handle batch files (list of cases) vs single case (dict)
        if isinstance(raw, list):
            cases_to_process = raw
        else:
            cases_to_process = [raw]
        
        for idx, case in enumerate(cases_to_process):
            result = _vigia_score(case)
            naive = _naive_score(case.get("artifacts", []))
            expected = case.get("expected_verdict", "?")
            match = result["verdict"] == expected
            results.append({
                "case_id": case.get("case_id", f"{cf.stem}_{idx}"),
                "name": case.get("name", cf.stem)[:45],
                "vigia_verdict": result["verdict"],
                "vigia_score": result["score"],
                "naive_score": naive,
                "expected": expected,
                "pass": match,
            })

            vc = _verdict_color(result["verdict"])
            status = f"{GRN}{RST}" if match else f"{RED}{RST}"
            print(f"  {status} [{cf.stem}]")
            print(f"      VIGÍA  → {vc}{result['verdict']:10s}{RST} score={result['score']:.4f}  conf={result['confidence']:.2%}")
            print(f"      Naive  → score={naive:.4f}")
            print(f"      Delta  : {result['score'] - naive:+.4f}  |  Expected: {expected}")
            if result.get("hard_temporal_gate"):
                print(f"      {RED}HARD GATE: EFFECT_BEFORE_CAUSE{RST}")
            print()

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    fails = [r for r in results if not r["pass"]]
    print(f"{'─' * 72}")
    print(f"  Results: {GRN}{passed}/{total} PASS{RST}", end="")
    if passed < total:
        print(f"  {RED}{total-passed} FAIL{RST}", end="")
    print()

    if fails:
        print(f"\n  {RED}FAILED CASES:{RST}")
        for r in fails:
            delta = r["vigia_score"] - r["naive_score"]
            print(f"    - {r['case_id']}: VIGIA={r['vigia_verdict']} (exp={r['expected']}) score={r['vigia_score']:.4f} delta={delta:+.4f}")

    mean_vigia = sum(r["vigia_score"] for r in results) / len(results)
    mean_naive = sum(r["naive_score"] for r in results) / len(results)
    print(f"  Mean VIGÍA score : {mean_vigia:.4f}")
    print(f"  Mean Naive score : {mean_naive:.4f}")
    print(f"  Mean Delta       : {mean_vigia - mean_naive:+.4f}")
    print(f"\n{'=' * 72}\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
