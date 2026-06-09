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

try:
    from vigia.core.bundle_builder import build_bundle as _build_bundle
    _HAS_BUNDLE_BUILDER = True
except (ImportError, Exception):
    _HAS_BUNDLE_BUILDER = False

# Colores ANSI para terminal
RED = "\033[91m"
YEL = "\033[93m"
GRN = "\033[92m"
BLU = "\033[94m"
CYA = "\033[96m"
RST = "\033[0m"
BLD = "\033[1m"


def _display_4_hashes(sealed: dict) -> None:
    """Muestra los 4 hashes forenses del bundle sellado."""
    integrity = sealed.get("integrity", {})
    h1 = integrity.get("graph_hash", "")
    h2 = integrity.get("bundle_hash", "")

    # H3: HMAC-SHA256 sobre el bundle canónico (sin integrity block)
    try:
        from vigia.core.bundle_builder import _canonicalize
        bundle_payload = {k: v for k, v in sealed.items() if k != "integrity"}
        canonical_bytes = json.dumps(
            _canonicalize(bundle_payload),
            sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("utf-8")
    except ImportError:
        bundle_payload = {k: v for k, v in sealed.items() if k != "integrity"}
        canonical_bytes = json.dumps(
            bundle_payload, sort_keys=True, ensure_ascii=True, default=str,
        ).encode("utf-8")

    hmac_key_env = os.environ.get("VIGIA_HMAC_KEY", "").encode()
    if not hmac_key_env:
        hmac_key_env = hashlib.sha256(h2.encode() if h2 else b"dev").digest()
        h3_note = f"{YEL}ephemeral (dev — set VIGIA_HMAC_KEY for production){RST}"
    else:
        h3_note = f"{GRN}production key{RST}"
    h3 = hmac.new(hmac_key_env, canonical_bytes, hashlib.sha256).hexdigest()

    # H4: quick_verify interno
    try:
        from vigia.core.bundle_builder import BundleBuilder as _BB
        h4_ok, h4_msg = _BB.quick_verify(sealed)
        h4_status = f"{GRN}PASS — {h4_msg}{RST}" if h4_ok else f"{RED}FAIL — {h4_msg}{RST}"
    except Exception as exc:
        h4_status = f"{YEL}N/A ({exc}){RST}"

    print(f"\n  {BLD}FORENSIC BUNDLE — 4 HASHES{RST}")
    print(f"  {'─' * 60}")
    if h1:
        print(f"  {BLD}H1{RST} graph_hash")
        print(f"     {CYA}{h1}{RST}")
    else:
        print(f"  {BLD}H1{RST} graph_hash    {RED}ABSENT{RST}")
    if h2:
        print(f"  {BLD}H2{RST} bundle_hash")
        print(f"     {CYA}{h2}{RST}")
    else:
        print(f"  {BLD}H2{RST} bundle_hash   {RED}ABSENT{RST}")
    print(f"  {BLD}H3{RST} HMAC audit chain ({h3_note})")
    print(f"     {CYA}{h3}{RST}")
    print(f"  {BLD}H4{RST} EBS verify     {h4_status}")
    print(f"  {'─' * 60}")
    print(f"  Sealed at : {integrity.get('sealed_at', 'N/A')}")


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

    # ── Bundle sealing — 4 hashes forenses ───────────────────────────────────
    if _HAS_BUNDLE_BUILDER:
        try:
            _sealed = _build_bundle(case, result)
            _display_4_hashes(_sealed)
        except Exception as _bundle_exc:
            print(f"\n  {YEL}[BUNDLE] Sealing falló: {_bundle_exc}{RST}")
    else:
        print(f"\n  {YEL}[BUNDLE] bundle_builder no disponible — corriendo en modo standalone{RST}")

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
