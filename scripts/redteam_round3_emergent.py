#!/usr/bin/env python3
"""
Red-Team Round 3 — Emergent / architectural fractures (property-based)
=====================================================================
Method: Abductive Engineering (A-D-I) + Red-Team Auditing (epistemic ladder).
Scope : composition of individually-correct modules. READ-ONLY audit — no
        product code is modified by this script.

Four targets, each a reproducible induction:

  R3-1  Temporal consistency — an artifact carrying an epoch-edge timestamp
        (1970) fabricates a maximum-severity CAIE temporal-causality fracture
        with NO absolute-range validation, flipping the verdict.
  R3-2  Canonicalization — _canonicalize maps DISTINCT inputs to ONE hash
        (True/"true", 1/"1:int", None/"null", 0.1/"0.10000000") and ONE
        logical string to TWO hashes (NFC/NFD, CRLF/LF).
  R3-3  Duplicate case shadowing — enumerate every stem present in >1 case
        dir and flag divergent expected_verdict labels.
  R3-4  Audit-chain plausibility — a v2 tool-log chain with causally
        impossible timestamps (backwards, 1970, duplicated event content)
        verifies as CHAIN VERIFIED. seq+content integrity != causal order.

Run:
    cd <repo root>
    PYTHONPATH=$(pwd) python3 scripts/redteam_round3_emergent.py
    PYTHONPATH=$(pwd) python3 scripts/redteam_round3_emergent.py R3-1   # one target
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def hr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# ---------------------------------------------------------------------------
# R3-1 — Temporal consistency: epoch-edge timestamp fabricates a fracture
# ---------------------------------------------------------------------------
def r3_1_temporal():
    hr("R3-1  Temporal — epoch-edge (1970) timestamp fabricates MALICE signal")
    from vigia_scorer import _vigia_score

    def art(i, e, raw, ts, meta):
        return {
            "artifact_id": f"A{i}", "evidence_type": e, "raw_score": raw,
            "prior_trust": 0.85, "source_tool": f"t{i}",
            "description": f"{e} artifact {i}", "timestamp": ts,
            "provenance_chain": ["acq"], "metadata": meta,
        }

    def net(ts):
        return art(0, "network_flow", 0.2, ts, {"network_log_time": ts})

    def proc(ts):
        return art(1, "memory_process", 0.2, ts, {"process_creation_time": ts})

    scen = {
        "BASELINE  net@2026-10h proc@2026-09h": [net("2026-03-01T10:00:00Z"), proc("2026-03-01T09:00:00Z")],
        "1970      net@1970     proc@2026-09h": [net("1970-01-01T00:00:00Z"), proc("2026-03-01T09:00:00Z")],
        "2099-proc net@2026     proc@2099    ": [net("2026-03-01T10:00:00Z"), proc("2099-01-01T00:00:00Z")],
        "2099-net  net@2099     proc@2026-09h": [net("2099-01-01T00:00:00Z"), proc("2026-03-01T09:00:00Z")],
    }
    print("PREDICTION: 1970 on the earlier event (network) and 2099 on the later")
    print("event (process) both fire a severity-1.0 TEMPORAL_CAUSALITY_VIOLATION;")
    print("no absolute-range/plausibility gate rejects the sentinel value.\n")
    base_v = None
    hit = False
    for name, arts in scen.items():
        r = _vigia_score({"case_id": name, "artifacts": arts})
        if base_v is None:
            base_v = r["verdict"]
        flip = r["verdict"] != base_v
        if flip and r["fracture_malice_boost"] > 0:
            hit = True
        print(f"  {name}: verdict={r['verdict']:9} score={r['score']:<7} "
              f"fractures={r['caie_fractures']} boost={r['fracture_malice_boost']} "
              f"src={r['caie_fractures_source']}")
    print("\nRESULT: " + ("CONFIRMED — a data-quality timestamp fabricates a malice fracture"
                          if hit else "HOLDS"))
    return hit


# ---------------------------------------------------------------------------
# R3-2 — Canonicalization collisions and instability
# ---------------------------------------------------------------------------
def r3_2_canonicalize():
    hr("R3-2  Canonicalization — distinct->1 hash, 1 logical->2 hashes")
    from vigia.core.canonicalize import _canonicalize

    def H(x):
        return hashlib.sha256(
            json.dumps(_canonicalize(x), sort_keys=True, ensure_ascii=True).encode()
        ).hexdigest()

    print("PREDICTION: str passthrough + type tags collide across the type "
          "boundary; str passthrough leaves Unicode/newline forms unnormalized.\n")
    collisions = [
        (True, "true"), (False, "false"), (None, "null"),
        (1, "1:int"), (0.1, "0.10000000"),
        ({"verdict": True}, {"verdict": "true"}),
        ({"n": 1}, {"n": "1:int"}),
    ]
    n_coll = 0
    print("  TWO DISTINCT INPUTS -> ONE HASH:")
    for a, b in collisions:
        c = H(a) == H(b)
        n_coll += c
        print(f"    {str(a):22} vs {str(b):18} {'COLLISION' if c else 'distinct'}  {H(a)[:16]}")

    nfc = unicodedata.normalize("NFC", "café")
    nfd = unicodedata.normalize("NFD", "café")
    crlf, lf = "a\r\nb", "a\nb"
    n_unstable = 0
    print("  ONE LOGICAL INPUT -> TWO HASHES:")
    for name, x, y in [("NFC vs NFD 'café'", nfc, nfd), ("CRLF vs LF", crlf, lf)]:
        u = H(x) != H(y)
        n_unstable += u
        print(f"    {name:22} equal_str={x==y!s:5} {'UNSTABLE' if u else 'stable'}  {H(x)[:12]} / {H(y)[:12]}")

    fr = _canonicalize(Fraction(1, 2))
    fl = _canonicalize(0.5)
    print(f"  Fraction fallback: Fraction(1,2)->{fr!r}  vs  float 0.5->{fl!r}  "
          f"({'DIVERGENT' if fr != fl else 'same'})")
    ok = n_coll >= 5 and n_unstable == 2
    print(f"\nRESULT: {'CONFIRMED' if ok else 'PARTIAL'} — {n_coll} collisions, {n_unstable} instabilities")
    return ok


# ---------------------------------------------------------------------------
# R3-3 — Duplicate case shadowing with divergent labels
# ---------------------------------------------------------------------------
def r3_3_shadowing():
    hr("R3-3  Duplicate case shadowing — divergent labels across case dirs")
    CASES_DIRS = ["data/cases", "data/cases/converted", "data/cases/benign",
                  "data/cases/consolidated_canonical", "data/cases/legacy"]
    SKIP = {"_index", "dataset", "calibration", "covariance", "correlation",
            "vigia_forensic_cases", "vigia_60_cases", "vigia_cases_canonical",
            "vigia_input_defcon", "fsv_schema", "phonetic_dict"}

    def label(f):
        try:
            d = json.loads(Path(f).read_text())
            if isinstance(d, list):
                return "MALFORMED(list)"
            return (d.get("expected_verdict")
                    or d.get("ground_truth", {}).get("expected_verdict") or "UNKNOWN")
        except Exception as e:
            return f"ERR:{type(e).__name__}"

    locs = defaultdict(list)
    for d in CASES_DIRS:
        p = Path(d)
        if not p.exists():
            continue
        for f in sorted(p.glob("*.json")):
            s = f.stem.lower()
            if s in SKIP or any(k in s for k in SKIP):
                continue
            locs[f.stem].append(str(f))

    dups = {k: v for k, v in locs.items() if len(v) > 1}
    print(f"PREDICTION: the runner dedups by stem (first CASES_DIRS wins); some")
    print(f"duplicated stems carry DIFFERENT expected_verdict across locations.\n")
    print(f"  total stems: {len(locs)}  duplicated: {len(dups)}")
    divergent = []
    malformed = []
    for stem, ls in sorted(dups.items()):
        labs = [(l, label(l)) for l in ls]
        vals = {v for _, v in labs}
        if any("MALFORMED" in v or "ERR" in v for _, v in labs):
            malformed.append((stem, labs))
        if len(vals) > 1:
            divergent.append((stem, labs))
    print(f"  DIVERGENT-label duplicates: {len(divergent)}")
    for stem, labs in divergent:
        print(f"    {stem}  (runner uses '{labs[0][1]}' from {labs[0][0]})")
        for l, v in labs:
            print(f"        {v:16} {l}")
    if malformed:
        print(f"  MALFORMED/unparseable duplicated stems: {len(malformed)}")
        for stem, labs in malformed:
            print(f"    {stem}: {[v for _,v in labs]}")
    ok = len(divergent) > 0
    print(f"\nRESULT: {'CONFIRMED' if ok else 'HOLDS'} — {len(divergent)} silent label conflicts")
    return ok


# ---------------------------------------------------------------------------
# R3-4 — Audit-chain accepts a causally impossible history
# ---------------------------------------------------------------------------
def r3_4_audit_chain():
    hr("R3-4  Audit-chain — causally impossible timestamps still VERIFY")
    from vigia.core.tool_log_chain import (
        ToolExecutionLogChain, verify_tool_execution_log,
    )

    print("PREDICTION: the v2 verifier checks seq monotonicity + content hash +")
    print("linkage, but NEVER validates timestamp order/range. A chain whose")
    print("timestamps run BACKWARDS, sit at 1970, and duplicate a prior event")
    print("verifies as valid — the chain proves insertion order, not causality.\n")

    chain = ToolExecutionLogChain(mode="claude_code", use_env_key=False)
    log = []
    # seq=1 at a normal time
    log.append(chain.append("generate_forensic_hash", "/evidence/disk.img",
                            "sha256=ab12 4GB", {"path": "/evidence/disk.img"},
                            event_id="e1", timestamp="2026-03-01T12:00:00Z"))
    # seq=2 BEFORE seq=1 (effect before cause)
    log.append(chain.append("read_evidence", "/evidence/disk.img",
                            "read 4GB", {"path": "/evidence/disk.img"},
                            event_id="e2", timestamp="2026-03-01T08:00:00Z"))
    # seq=3 at the unix epoch (1970 sentinel)
    log.append(chain.append("infer_intent", "artifact://A1",
                            "verdict=MALICE", {"artifact": "A1"},
                            event_id="e3", timestamp="1970-01-01T00:00:00Z"))
    # seq=4 duplicates seq=1's content exactly except (seq, timestamp far future)
    log.append(chain.append("generate_forensic_hash", "/evidence/disk.img",
                            "sha256=ab12 4GB", {"path": "/evidence/disk.img"},
                            event_id="e4", timestamp="2099-12-31T23:59:59Z"))

    v = verify_tool_execution_log(log)
    verified = v.valid
    ts = [e["timestamp"] for e in log]
    backwards = any(ts[i] > ts[i + 1] for i in range(len(ts) - 1))
    print("  chain (seq -> timestamp):")
    for e in log:
        print(f"    seq={e['seq']}  {e['timestamp']:26} {e['tool']}")
    print(f"\n  timestamps monotonic increasing? {not backwards}")
    print(f"  contains 1970 epoch sentinel?    {'1970-01-01T00:00:00Z' in ts}")
    print(f"  verifier verdict:  valid={verified}  hmac_checked={v.hmac_checked}  "
          f"seq_discontinuities={len(v.seq_discontinuities)}  broken_links={len(v.broken_links)}")
    ok = verified and backwards
    print(f"\nRESULT: {'CONFIRMED' if ok else 'HOLDS'} — a causally impossible "
          f"history seals and verifies as intact")
    return ok


TARGETS = {
    "R3-1": r3_1_temporal,
    "R3-2": r3_2_canonicalize,
    "R3-3": r3_3_shadowing,
    "R3-4": r3_4_audit_chain,
}


def main():
    print("VIGIA Red-Team Round 3 — Emergent / architectural fractures")
    want = [a.upper() for a in sys.argv[1:]] or list(TARGETS)
    res = {}
    for t in want:
        if t in TARGETS:
            res[t] = TARGETS[t]()
    hr("SUMMARY")
    for t, ok in res.items():
        print(f"  {t}: {'CONFIRMED' if ok else 'HOLDS'}")


if __name__ == "__main__":
    main()
