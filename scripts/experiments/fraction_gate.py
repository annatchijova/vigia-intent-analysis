#!/usr/bin/env python3
"""
fraction_gate.py — bit-identity acceptance gate for decision-path arithmetic
changes in vigia_scorer.

Purpose: any change to the scorer's arithmetic (e.g. the Fraction migration of
the fracture boost/penalty accumulators) must produce a BIT-IDENTICAL corpus:
same verdict, same repr() of score / fracture_malice_boost /
fracture_credibility_penalty, same reason string, for every scoreable case.
This script is the gate, portable to any branch:

  # before the change:
  python3 scripts/experiments/fraction_gate.py snapshot /path/before.json
  # after the change:
  python3 scripts/experiments/fraction_gate.py snapshot /path/after.json
  python3 scripts/experiments/fraction_gate.py compare /path/before.json /path/after.json

compare exits 0 only on zero differences and prints a SHA-256 of both
snapshots for the gate record. repr() is used (not rounding) so 1-ulp float
drift fails the gate.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
os.chdir(REPO)
logging.disable(logging.CRITICAL)


def snapshot(out_path: str) -> None:
    from run_all_agent import CASES_DIRS, find_cases
    from vigia_scorer import _vigia_score

    snap = {}
    for p in find_cases(CASES_DIRS):
        try:
            case = json.loads(p.read_text())
        except Exception:
            continue
        if not isinstance(case, dict):
            continue
        try:
            r = _vigia_score(case)
            rec = {
                "verdict": r["verdict"],
                "score_repr": repr(r["score"]),
                "boost_repr": repr(r.get("fracture_malice_boost")),
                "penalty_repr": repr(r.get("fracture_credibility_penalty")),
                "reason": r.get("reason", ""),
            }
        except Exception as e:
            rec = {"verdict": "ERROR", "error": f"{type(e).__name__}: {e}"}
        snap[case.get("case_id", p.stem)] = rec
    body = json.dumps(snap, indent=1, ensure_ascii=False, sort_keys=True)
    Path(out_path).write_text(body)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    print(f"snapshot: {len(snap)} cases -> {out_path}")
    print(f"sha256  : {digest}")


def compare(before_path: str, after_path: str) -> int:
    before = json.loads(Path(before_path).read_text())
    after = json.loads(Path(after_path).read_text())
    diffs = []
    for cid in sorted(set(before) | set(after)):
        b, a = before.get(cid), after.get(cid)
        if b != a:
            diffs.append((cid, b, a))
    for path in (before_path, after_path):
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        print(f"sha256 {path}: {digest}")
    if not diffs:
        print(f"GATE PASS: {len(before)} cases bit-identical "
              f"(verdict, score repr, boost repr, penalty repr, reason)")
        return 0
    print(f"GATE FAIL: {len(diffs)} case(s) differ")
    for cid, b, a in diffs[:20]:
        print(f"  {cid}:")
        print(f"    before: {json.dumps(b, ensure_ascii=False)[:200]}")
        print(f"    after : {json.dumps(a, ensure_ascii=False)[:200]}")
    return 1


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "snapshot":
        snapshot(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "compare":
        sys.exit(compare(sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
