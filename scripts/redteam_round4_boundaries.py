#!/usr/bin/env python3
"""
Red-Team Round 4 — Boundary conditions in the scorer (property-based)
=====================================================================
Method: Abductive Engineering (A-D-I) + Red-Team Auditing (epistemic ladder).
Scope : vigia_scorer._vigia_score at boundary inputs. READ-ONLY probe.

Questions (from the brief):
  Q1  0 artifacts        — clean verdict or crash?
  Q2  completely empty case ({} , None-ish fields) — crash?
  Q3  1000 same-type artifacts — bounded score/time, or blowup?

Also probes adjacent boundaries a thorough audit must cover:
  Q4  malformed artifacts (missing fields, wrong types)
  Q5  scaling curve of the M2-1 best-prefix decay (is it quadratic?)

Run:  PYTHONPATH=$(pwd) python3 scripts/redteam_round4_boundaries.py
"""
from __future__ import annotations

import time
import traceback

from vigia_scorer import _vigia_score


def hr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def safe(label, case):
    """Run the scorer; report verdict/score or the exception (a crash IS the
    finding for a boundary probe)."""
    t0 = time.perf_counter()
    try:
        r = _vigia_score(case)
        dt = time.perf_counter() - t0
        v, s = r.get("verdict"), r.get("score")
        print(f"  {label:38} -> verdict={v!s:9} score={s!s:8} ({dt*1000:.1f} ms)")
        return r, dt
    except Exception as e:
        dt = time.perf_counter() - t0
        print(f"  {label:38} -> CRASH {type(e).__name__}: {e}  ({dt*1000:.1f} ms)")
        traceback.print_exc()
        return None, dt


def art(i, etype="log_entry", raw=0.85, prior=0.85):
    return {
        "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": prior, "source_tool": f"t{i}", "description": f"a{i}",
        "timestamp": f"2026-01-01T10:00:{i%60:02d}Z",
        "provenance_chain": ["acq"], "metadata": {},
    }


def q1_zero_artifacts():
    hr("Q1 — zero artifacts")
    print("PREDICTION: clean ERROR/ABSTAIN verdict, never a crash.")
    safe("{'artifacts': []}", {"case_id": "z", "artifacts": []})
    safe("{'artifacts': [], others}", {"case_id": "z", "artifacts": [],
                                       "temporal_violations": [], "caie_fractures": []})


def q2_empty_case():
    hr("Q2 — completely empty / degenerate case")
    print("PREDICTION: guarded; no KeyError/TypeError on missing fields.")
    safe("{}", {})
    safe("{'artifacts': None}", {"artifacts": None})
    safe("None case", None)
    safe("{'artifacts': [{}]}", {"artifacts": [{}]})        # one empty artifact
    safe("{'artifacts': [{}, {}, {}]}", {"artifacts": [{}, {}, {}]})


def q3_same_type_flood():
    hr("Q3 — 1000 artifacts, all same type")
    print("PREDICTION: score stays in [0,0.99], deterministic, no crash; time?")
    for n in (10, 100, 500, 1000):
        r, dt = safe(f"{n}x log_entry raw=0.85",
                     {"case_id": f"flood{n}",
                      "artifacts": [art(i, "log_entry", 0.85) for i in range(n)]})
        if r is not None:
            assert 0.0 <= r["score"] <= 0.99, f"score out of range: {r['score']}"
    # determinism at n=1000
    a = [art(i, "log_entry", 0.85) for i in range(1000)]
    r1 = _vigia_score({"case_id": "d1", "artifacts": a})
    r2 = _vigia_score({"case_id": "d2", "artifacts": [art(i, "log_entry", 0.85) for i in range(1000)]})
    print(f"  determinism @1000: {'OK' if r1['score'] == r2['score'] else 'DIVERGENT'} "
          f"(score={r1['score']})")


def q4_malformed():
    hr("Q4 — malformed artifacts (missing / wrong-typed fields)")
    print("PREDICTION: Finite-Math/type shields absorb these; no crash.")
    safe("raw_score=None",     {"artifacts": [{"evidence_type": "log_entry", "raw_score": None}]})
    safe("raw_score='high'",   {"artifacts": [{"evidence_type": "log_entry", "raw_score": "high"}]})
    safe("raw_score=inf",      {"artifacts": [{"evidence_type": "log_entry", "raw_score": float("inf")}]})
    safe("prior_trust=-5",     {"artifacts": [{"evidence_type": "log_entry", "raw_score": 0.9, "prior_trust": -5}]})
    safe("evidence_type=None", {"artifacts": [{"evidence_type": None, "raw_score": 0.9}]})
    safe("evidence_type=123",  {"artifacts": [{"evidence_type": 123, "raw_score": 0.9}]})
    safe("chain=str",          {"artifacts": [{"evidence_type": "log_entry", "raw_score": 0.9, "provenance_chain": "nope"}]})


def q5_scaling_curve():
    hr("Q5 — scaling curve of the M2-1 best-prefix decay (same type)")
    print("PREDICTION (rival A): near-linear.  (rival B): quadratic O(n^2) —")
    print("the best-prefix loop is per-type: sum_{k=1..n} k list-builds+prod.")
    prev = None
    for n in (250, 500, 1000, 2000):
        arts = [art(i, "log_entry", 0.85) for i in range(n)]
        t0 = time.perf_counter()
        _vigia_score({"case_id": f"s{n}", "artifacts": arts})
        dt = time.perf_counter() - t0
        ratio = f"  x{dt/prev:.2f} vs prev" if prev else ""
        print(f"  n={n:5}  {dt*1000:8.1f} ms{ratio}")
        prev = dt
    print("  (doubling n and time ~x4 => quadratic; ~x2 => linear)")


def main():
    print("VIGIA Red-Team Round 4 — Boundary conditions")
    q1_zero_artifacts()
    q2_empty_case()
    q3_same_type_flood()
    q4_malformed()
    q5_scaling_curve()


if __name__ == "__main__":
    main()
