"""
tests/run_all_cases.py
========================
VIGÍA — Runs the full case suite and reports results.

Usage:
    python tests/run_all_cases.py --cases-dir data/cases/consolidated_canonical
    python tests/run_all_cases.py --cases-dir data/cases
    python tests/run_all_cases.py --cases-dir data/cases/benign
    python tests/run_all_cases.py --cases-dir data/cases --filter VIGIA-REAL
    python tests/run_all_cases.py --cases-dir data/cases --filter VIGIA-BREAK

SANS FIND EVIL Hackathon 2026
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

RED = "\033[91m"; YEL = "\033[93m"; GRN = "\033[92m"
BLU = "\033[94m"; CYA = "\033[96m"; RST = "\033[0m"; BLD = "\033[1m"

sys.path.insert(0, str(Path(__file__).parent.parent))
from tests.run_vigia_case import _vigia_score, _naive_score, _verdict_color

# ---------------------------------------------------------------------------
# Verdict aliases
# The VIGÍA scorer emits: MALICE, SUSPICION, UNKNOWN, NOISE.
# Some case JSONs use "BENIGN" or "ABSTAIN". Conservative mapping:
#   BENIGN  -> NOISE   (no malicious signal detected)
#   ABSTAIN -> NOISE | UNKNOWN  (insufficient evidence to decide)
# ---------------------------------------------------------------------------
_ALIASES: dict[str, list[str]] = {
    "BENIGN":  ["NOISE"],
    "ABSTAIN": ["NOISE", "UNKNOWN"],
}

# Files to skip — not individual case files (indexes, collections, datasets)
_SKIP_STEMS = {
    "_index",
    "vigia_cases_canonical_v2",
    "vigia_input_defcon_nist",
    "vigia_break_canonical_001-010",   # duplicate batch — already in VIGIA_BREAK_001-010.json
    "vigia_60_cases_dataset",
    "calibration_dataset",
    "dataset_test_cases",
    "calibration_metadata",
    "calibrated_lr",
    "nlp_covariance_summary",
    "correlation_groups",
    "fsv_schema",
    "baselines_institucionales",
    "phonetic_dict",
}


def _match(actual: str, expected: str) -> bool:
    """Match with alias support for BENIGN/ABSTAIN vocabulary."""
    return actual == expected or actual in _ALIASES.get(expected, [])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="VIGÍA — Full case runner")
    parser.add_argument("--cases-dir", default="cases", help="Directory with case JSON files")
    parser.add_argument("--filter", default="", dest="filter_str",
                        help="Only run cases whose filename contains this string (e.g. VIGIA-REAL, VIGIA-BREAK, VIGIA-BEN)")
    args = parser.parse_args()

    cases_dir = Path(args.cases_dir)
    if not cases_dir.exists():
        print(f"{RED}ERROR: cases dir not found: {cases_dir}{RST}")
        sys.exit(1)

    case_files = sorted(cases_dir.glob("*.json"))
    # Skip known non-case files
    case_files = [
        f for f in case_files
        if f.stem not in _SKIP_STEMS and not f.stem.startswith("_")
    ]
    # Apply --filter if given
    if args.filter_str:
        case_files = [f for f in case_files if args.filter_str in f.stem]

    if not case_files:
        print(f"{YEL}No case files found in {cases_dir}"
              + (f" matching '{args.filter_str}'" if args.filter_str else "")
              + f"{RST}")
        sys.exit(0)

    print(f"\n{BLD}{'=' * 72}{RST}")
    print(f"{BLD}  VIGÍA — FULL FORENSIC SUITE  ({len(case_files)} files){RST}")
    print(f"{BLD}  SANS FIND EVIL Hackathon 2026{RST}")
    if args.filter_str:
        print(f"{BLD}  Filter: {args.filter_str}{RST}")
    print(f"{'=' * 72}\n")

    results = []
    skipped = 0

    for cf in case_files:
        with open(cf, encoding="utf-8") as f:
            raw = json.load(f)

        cases_to_process = raw if isinstance(raw, list) else [raw]

        for idx, case in enumerate(cases_to_process):
            audit_note = case.get("audit_note", "")
            if "DO NOT include in run_all_cases" in audit_note:
                print(f"  {YEL}[SKIP]{RST} [{case.get('case_id', idx)}] — excluded by audit_note (H-02)")
                continue

            # Skip legacy schema v0 cases (no EBS v1 artifact structure)
            if not isinstance(case, dict) or "artifacts" not in case:
                print(f"  {YEL}[SKIP]{RST} [{cf.stem}] — legacy schema v0 (no EBS v1)")
                skipped += 1
                continue

            try:
                result = _vigia_score(case)
            except Exception as e:
                print(f"  {RED}[ERROR]{RST} [{cf.stem}] — {e}")
                skipped += 1
                continue

            naive    = _naive_score(case.get("artifacts", []))
            expected = case.get("expected_verdict", "?")
            case_id  = case.get("case_id", cf.stem)

            # Skip cases with undefined expected verdict
            if expected in ("?", None):
                print(f"  {YEL}[SKIP]{RST} [{case_id}] — no expected_verdict defined (legacy)")
                skipped += 1
                continue

            match = _match(result["verdict"], expected)
            results.append({
                "case_id":       case_id,
                "vigia_verdict": result["verdict"],
                "vigia_score":   result["score"],
                "naive_score":   naive,
                "expected":      expected,
                "pass":          match,
            })

            vc = _verdict_color(result["verdict"])
            status = f"{GRN}{RST}" if match else f"{RED}{RST}"
            print(f"  {status} [{case_id}]")
            print(f"      VIGÍA  -> {vc}{result['verdict']:10s}{RST} score={result['score']:.4f}  conf={result['confidence']:.2%}")
            print(f"      Naive  -> score={naive:.4f}")
            print(f"      Delta  : {result['score'] - naive:+.4f}  |  Expected: {expected}")
            if result.get("hard_temporal_gate"):
                print(f"      {RED}HARD GATE: EFFECT_BEFORE_CAUSE{RST}")
            print()

    passed = sum(1 for r in results if r["pass"])
    total  = len(results)
    fails  = [r for r in results if not r["pass"]]

    print(f"{'─' * 72}")
    print(f"  Results: {GRN}{passed}/{total} PASS{RST}", end="")
    if passed < total:
        print(f"  {RED}{total - passed} FAIL{RST}", end="")
    if skipped:
        print(f"  {YEL}{skipped} SKIPPED{RST}", end="")
    print()

    if fails:
        print(f"\n  {RED}FAILED CASES:{RST}")
        for r in fails:
            delta = r["vigia_score"] - r["naive_score"]
            print(f"    - {r['case_id']}: VIGIA={r['vigia_verdict']} (exp={r['expected']}) "
                  f"score={r['vigia_score']:.4f} delta={delta:+.4f}")

    if total > 0:
        mean_v = sum(r["vigia_score"] for r in results) / total
        mean_n = sum(r["naive_score"] for r in results) / total
        print(f"  Mean VIGÍA score : {mean_v:.4f}")
        print(f"  Mean Naive score : {mean_n:.4f}")
        print(f"  Mean Delta       : {mean_v - mean_n:+.4f}")

    print(f"\n{'=' * 72}\n")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
