#!/usr/bin/env python3
"""
verify_tool_log.py  — VIGÍA tool_execution_log chain verifier
Standalone, stdlib only. No VIGÍA installation required.

Verifies:
  - seq=1 has prev_hash="GENESIS"
  - seq=N has prev_hash == SHA-256(seq=N-1 result_summary)
  - self_correction_events are reported separately (not in hash chain by design)

Usage:
    python3 verify_tool_log.py results/srl2018/VIGIA-REAL-VANKO_bundle.json
    python3 verify_tool_log.py results/srl2018/VIGIA-REAL-NROMANOFF_bundle.json --verbose
    echo $?   # 0=VERIFIED  1=BROKEN  2=NO_LOG
"""
import json, hashlib, sys, argparse
from pathlib import Path


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_chain(bundle_path: str, verbose: bool = False) -> int:
    try:
        bundle = json.loads(Path(bundle_path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    log = bundle.get("tool_execution_log", [])
    if not log:
        print("NO tool_execution_log — fallback/EBS bundle.")
        print("Use: python3 forensics/verify_ebs_v1.py <bundle> --verbose")
        return 2

    case_id = (bundle.get("case_id")
               or bundle.get("metadata", {}).get("case_id", "UNKNOWN"))
    print(f"Bundle : {bundle_path}")
    print(f"Case   : {case_id}")
    print(f"Entries: {len(log)} MCP tool calls")
    print()

    ok = True
    prev_result: str | None = None

    for entry in log:
        seq       = entry.get("seq", "?")
        tool      = entry.get("tool", "?")[:42]
        result    = entry.get("result_summary", "")
        prev_hash = entry.get("prev_hash", "")

        if seq == 1:
            if prev_hash != "GENESIS":
                print(f"  [FAIL] seq=01 | prev_hash must be GENESIS, got {prev_hash!r}")
                ok = False
            else:
                print(f"  [OK  ] seq=01 | {tool:<42} | GENESIS")
        else:
            expected = _sha256(prev_result) if prev_result is not None else ""
            if prev_hash == expected:
                marker = prev_hash[:16] + "..."
                print(f"  [OK  ] seq={seq:02d} | {tool:<42} | {marker}")
            else:
                print(f"  [FAIL] seq={seq:02d} | {tool}")
                print(f"         expected : {expected[:32]}...")
                print(f"         got      : {(prev_hash or '(empty)')[:32]}...")
                ok = False

        if verbose:
            print(f"         result   : {result[:80]}")

        prev_result = result

    sc = bundle.get("self_correction_events", [])
    if sc:
        print(f"\nself_correction_events: {len(sc)} (not in hash chain — internal ops)")
        for e in sc:
            # Los campos pueden variar según la versión del agente
            seq_val  = e.get("seq") or e.get("sequence") or "?"
            tool_val = e.get("tool") or e.get("tool_name") or e.get("event_type") or "?"
            rs_val   = (e.get("result_summary") or e.get("summary")
                        or e.get("reason") or e.get("description") or "")
            if not any([e.get("seq"), e.get("tool"), e.get("result_summary")]):
                # Bundle antiguo: mostrar todas las claves disponibles
                rs_val = str({k: str(v)[:40] for k, v in e.items()})[:120]
            print(f"  seq={seq_val} | {str(tool_val)[:30]} | {str(rs_val)[:80]}")

    note = bundle.get("tool_execution_log_note", "")
    if note:
        print(f"\nNote: {note[:140]}")

    status = f"CHAIN VERIFIED ({len(log)} entries)" if ok else "CHAIN BROKEN"
    print(f"\nResult: {status}")
    return 0 if ok else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Verify VIGÍA tool_execution_log prev_hash chain (stdlib only)"
    )
    p.add_argument("bundle", help="Path to sealed bundle JSON")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print result_summary for each entry")
    args = p.parse_args()
    sys.exit(verify_chain(args.bundle, args.verbose))
