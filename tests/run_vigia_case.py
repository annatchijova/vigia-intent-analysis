"""
scripts/run_vigia_case.py
==========================
VIGÍA — Demo Runner: ejecuta un caso forense y muestra el veredicto.

Uso:
    python run_vigia_case.py cases/case_001_temporal.json
    python run_vigia_case.py cases/case_004_provenance_break.json

Output: veredicto, confianza, fractures CAIE, report Daubert.
SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Normalizador de schema legacy → EBS v1 (casos REAL y demo avanzados)
try:
    import sys; sys.path.insert(0, "."); sys.path.insert(0, "vigia/pipeline"); from vigia_integration_bridge import normalize_case_schema as _normalize_case
except ImportError:
    def _normalize_case(c):  # type: ignore[misc]
        return c  # fallback no-op: el caso se procesa como viene

# Colores ANSI para terminal
RED = "\033[91m"
YEL = "\033[93m"
GRN = "\033[92m"
BLU = "\033[94m"
CYA = "\033[96m"
RST = "\033[0m"
BLD = "\033[1m"


# Funciones de scoring importadas desde vigia_scorer.py (versión canónica con todos los fixes)
# B1-B4, P2, P4, P5, P6 — ver vigia_scorer.py para historial completo de patches
import sys as _sys
import os as _os
_sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from vigia_scorer import (
        _verdict_color,
        _compute_temporal_factor,
        _naive_score,
        _vigia_score,
    )
except ImportError:
    # Fallback: buscar en vigia/core/
    _sys.path.insert(0, str(Path(__file__).parent.parent / "vigia" / "core"))
    from vigia_scorer import (
        _verdict_color,
        _compute_temporal_factor,
        _naive_score,
        _vigia_score,
    )

def run_case(case_path: str) -> None:
    path = Path(case_path)
    if not path.exists():
        print(f"{RED}ERROR: File not found: {case_path}{RST}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        case = json.load(f)
    case = _normalize_case(case)  # compatibilidad schema legacy → EBS v1

    print(f"\n{BLD}{'=' * 62}{RST}")
    print(f"{BLD}VIGÍA FORENSIC ANALYSIS{RST}")
    print(f"Case: {BLU}{case.get('name', case.get('case_id'))}{RST}")
    print(f"{'=' * 62}")
    print(f"\n{case.get('description', '')}\n")

    result = _vigia_score(case)
    naive = _naive_score(case.get("artifacts", []))

    vc = _verdict_color(result["verdict"])
    print(f"{'─' * 62}")
    print(f"  VERDICT  :  {vc}{result['verdict']}{RST}")
    print(f"  Score    :  {result['score']:.4f}  (naive baseline: {naive:.4f})")
    print(f"  Confidence:  {result['confidence']:.2%}")
    print(f"  Reason   :  {result['reason']}")
    print(f"{'─' * 62}")

    if result["hard_temporal_gate"]:
        print(f"\n  {RED}{BLD}⚠ HARD GATE TRIGGERED: EFFECT_BEFORE_CAUSE{RST}")
        for v in case.get("temporal_violations", []):
            if v.get("type") == "EFFECT_BEFORE_CAUSE":
                print(f"    {v.get('interpretation', '')}")

    if case.get("caie_fractures"):
        print(f"\n  {YEL}CAIE FRACTURES:{RST}")
        for f in case["caie_fractures"]:
            print(f"    [{f.get('fracture_type')}] severity={f.get('severity'):.2f}")
            print(f"    → {f.get('interpretation', '')[:80]}")

    if result["peirce_chain"]:
        pc = result["peirce_chain"]
        print(f"\n  {CYA}PEIRCE ABDUCTIVE CHAIN:{RST}")
        print(f"    Firstness  : {pc.get('firstness', '')}")
        print(f"    Secondness : {pc.get('secondness', '')}")
        print(f"    Thirdness  : {pc.get('thirdness', '')}")

    qs = result.get("quadripartite_state", {})
    vs = qs.get("verdict_state", "")
    if vs and vs not in ("UNAVAILABLE", "QUADRIPARTITE_ERROR"):
        print(f"\n  QUADRIPARTITE 8-STATE:")
        print(f"    State   : {qs.get('display_label', vs)}")
        print(f"    Action  : {qs.get('action_required', '?')}")
        print(f"    Conf    : {qs.get('confidence_pct', '?')}%  |  Stability: {qs.get('stability_pct', '?')}%")
        summary = str(qs.get('analyst_summary', '')).strip()
        if summary:
            print(f"    Summary : {summary[:120]}")

    expected = result["expected_verdict"]
    actual = result["verdict"]
    match = actual == expected
    status = f"{GRN}PASS{RST}" if match else f"{RED}FAIL (expected {expected}){RST}"
    print(f"\n  Validation : {status}")

    print(f"\n  Effective Trust per artifact:")
    for et in result["effective_trusts"]:
        bar = "█" * int(et["effective_trust"] * 20)
        print(f"    {et['artifact_id'][:30]:30s} {bar:<20s} {et['effective_trust']:.4f}")

    # ------------------------------------------------------------------
    # Bundle integrity hashes
    # ------------------------------------------------------------------
    case_id = case.get("case_id", "")
    bundle_path = Path(__file__).parent.parent / "vigia_output" / f"bundle_{case_id}.json"
    if bundle_path.exists():
        raw = bundle_path.read_bytes()
        hmac_key = os.environ.get("VIGIA_HMAC_KEY", "vigia-integrity-key").encode()
        h_sha256 = hashlib.sha256(raw).hexdigest()
        h_md5    = hashlib.md5(raw).hexdigest()
        h_sha1   = hashlib.sha1(raw).hexdigest()
        h_hmac   = hmac.new(hmac_key, raw, hashlib.sha256).hexdigest()
        print(f"  {CYA}Bundle: {bundle_path.name}{RST}")
        print(f"    SHA-256 : {h_sha256}")
        print(f"    MD5     : {h_md5}")
        print(f"    SHA-1   : {h_sha1}")
        print(f"    HMAC    : {h_hmac}")

    print(f"\n{'=' * 62}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA — Demo runner para casos forenses"
    )
    parser.add_argument("case_file", help="Path al JSON del caso (e.g. cases/case_001_temporal.json)")
    args = parser.parse_args()
    run_case(args.case_file)


if __name__ == "__main__":
    main()
