#!/usr/bin/env python3
"""
Red Team Round 5 — degradacion de esquema del tool_execution_log.

Reproduce, con antes/despues medible, los vectores de docs/REDTEAM_ROUND5_DOWNGRADE.md
contra `verify_tool_log.py` (el verificador standalone de terceros).

Modelo de amenaza: el atacante REESCRIBE el bundle JSON despues del sellado.
NO tiene la clave HMAC, NO modifica codigo, NO toca el verificador.

Uso:
    python3 scripts/redteam_round5_downgrade.py                 # verificador actual
    python3 scripts/redteam_round5_downgrade.py --verifier X.py # p.ej. la version pre-fix

Exit 0 si cada vector da el resultado esperado POST-fix; 1 si alguno difiere.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia.core.tool_log_chain import ToolExecutionLogChain  # noqa: E402

KEY = b"a" * 32          # clave fija: el experimento debe ser reproducible
KEY_HEX = KEY.hex()


def keyed_bundle(n: int = 4) -> dict:
    """Bundle sellado en v2 CON clave — entry_hmac + chain_tip_sha256 + tip_hmac."""
    chain = ToolExecutionLogChain(mode="claude_code", hmac_key=KEY)
    calls = [
        ("generate_forensic_hash", "disk.e01", "SHA-256 ef2c3c0c INTEGRITY_VERIFIED"),
        ("search_pattern", "/mnt/evid/logs", "12 hits: wevtutil cl / timestomp"),
        ("detect_habit_incongruence", "process_list.csv",
         "svchost.exe parent=explorer.exe ANOMALY"),
        ("validate_and_correct_analysis", "CASE-R5",
         "VERDICT: MALICE | anti-forensics confirmed"),
    ][:n]
    log = [chain.append(tool=t, target=g, result_summary=s, arguments={"t": g})
           for t, g, s in calls]
    return {"case_id": "CASE-R5", "tool_execution_log": log, **chain.bundle_fields()}


def rewrite_as_v1(bundle: dict, strip_all_markers: bool = False) -> dict:
    """Reescribe el log con el esquema v1 legacy: sin entry_hash/entry_hmac,
    prev_hash = SHA-256(result_summary anterior), "GENESIS" en seq=1."""
    out = copy.deepcopy(bundle)
    prev = None
    for entry in out["tool_execution_log"]:
        entry.pop("entry_hash", None)
        entry.pop("entry_hmac", None)
        if strip_all_markers:
            entry.pop("chain_version", None)
        entry["prev_hash"] = ("GENESIS" if prev is None
                              else hashlib.sha256(prev.encode()).hexdigest())
        prev = entry["result_summary"]
    if strip_all_markers:
        out.pop("chain_tip_sha256", None)
        out.pop("chain_tip_hmac", None)
    return out


def flip_verdict(bundle: dict) -> dict:
    """MALICE -> NOISE en la ultima entrada; ademas reescribe un target
    (campo que el esquema v1 deja sin proteger)."""
    out = copy.deepcopy(bundle)
    out["tool_execution_log"][-1]["result_summary"] = "VERDICT: NOISE | nothing found"
    out["tool_execution_log"][1]["target"] = "/mnt/evid/unrelated"
    return out


def run(verifier: Path, bundle: dict, keyed: bool = True, extra=()) -> tuple:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "bundle.json"
        path.write_text(json.dumps(bundle, indent=2))
        cmd = [sys.executable, str(verifier), str(path), *extra]
        if keyed:
            cmd += ["--hmac-key-hex", KEY_HEX]
        env = {k: v for k, v in os.environ.items() if k != "VIGIA_HMAC_KEY"}
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(REPO))
    schema = next((l.split(":", 1)[1].strip()
                   for l in p.stdout.splitlines() if l.startswith("Schema")), "?")
    return p.returncode, schema


# (id, descripcion, bundle, keyed, extra_args, exit esperado POST-fix)
def vectors():
    base = keyed_bundle()
    tampered = flip_verdict(base)
    truncated = copy.deepcopy(base)
    truncated["tool_execution_log"] = truncated["tool_execution_log"][:2]
    trunc_stripped = copy.deepcopy(truncated)
    trunc_stripped.pop("chain_tip_sha256", None)
    trunc_stripped.pop("chain_tip_hmac", None)
    no_tip_hmac = copy.deepcopy(base)
    no_tip_hmac.pop("chain_tip_hmac", None)
    one_field = copy.deepcopy(base)
    del one_field["tool_execution_log"][0]["entry_hash"]

    return [
        ("E0", "control: bundle intacto, verificado con clave", base, True, (), 0),
        ("E1", "control: MALICE->NOISE bajo v2", tampered, True, (), 1),
        ("R5-1a", "DEGRADACION v2->v1 + MALICE->NOISE + target reescrito",
         rewrite_as_v1(tampered), True, (), 1),
        ("R5-1b", "degradacion con el ancla de cola PRESENTE (y obsoleta)",
         rewrite_as_v1(tampered), True, (), 1),
        ("R5-1c", "un solo campo borrado: entry_hash de seq=1",
         one_field, True, (), 1),
        ("R5-1d", "strip total de marcadores v2, CON clave",
         rewrite_as_v1(tampered, strip_all_markers=True), True, (), 1),
        ("R5-1e", "RESIDUAL: strip total, SIN clave (limite documentado)",
         rewrite_as_v1(tampered, strip_all_markers=True), False, (), 0),
        ("R5-1f", "escape hatch: bundle legacy con --allow-legacy-v1",
         rewrite_as_v1(tampered, strip_all_markers=True), True,
         ("--allow-legacy-v1",), 0),
        ("R5-2a", "truncar la cola y BORRAR el ancla", trunc_stripped, True, (), 1),
        ("R5-2b", "control: truncar dejando el ancla", truncated, True, (), 1),
        ("R5-2c", "borrar solo chain_tip_hmac", no_tip_hmac, True, (), 1),
        ("R5-3", "hygiene: entrada no-dict", {"tool_execution_log": ["x"]}, False, (), 1),
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", default=str(REPO / "verify_tool_log.py"))
    args = ap.parse_args()
    verifier = Path(args.verifier)

    print(f"Verificador : {verifier}")
    print(f"Clave HMAC  : {KEY_HEX[:16]}... (fija, reproducible)")
    print(f"{'ID':<7} {'exp':<4} {'got':<4} {'schema':<9} descripcion")
    print("-" * 88)
    mismatches = 0
    for vid, desc, bundle, keyed, extra, expected in vectors():
        code, schema = run(verifier, bundle, keyed, extra)
        flag = "" if code == expected else "   <-- DIFIERE del esperado post-fix"
        if code != expected:
            mismatches += 1
        print(f"{vid:<7} {expected:<4} {code:<4} {schema:<9} {desc}{flag}")
    print("-" * 88)
    print(f"exit 0 = CHAIN VERIFIED | exit 1 = CHAIN BROKEN | vectores divergentes: {mismatches}")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
