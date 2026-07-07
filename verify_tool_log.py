#!/usr/bin/env python3
"""
verify_tool_log.py  — VIGÍA tool_execution_log chain verifier
Standalone, stdlib only. No VIGÍA installation required.
(Mantiene su propia copia de la canonicalización por diseño —
mismo patrón que forensics/verify_ebs_v1.py.)

Soporta ambos esquemas de cadena:

  v1 (legacy, bundles históricos):
    - seq=1 has prev_hash="GENESIS"
    - seq=N has prev_hash == SHA-256(seq=N-1 result_summary)
    - CAVEAT: solo result_summary está protegido. Los demás campos no
      son tamper-evident bajo v1 — el verificador lo reporta.

  v2 (chain_version="2", entry_hash presente):
    - entry_hash = SHA-256(canonical(entrada completa + seq + prev_hash))
    - prev_hash  = entry_hash del entry anterior ("0"*64 en seq=1)
    - entry_hmac = HMAC-SHA256(key, entry_hash) — verificado si se pasa
      --hmac-key-hex / --hmac-key-file o VIGIA_HMAC_KEY[_FILE] en el entorno.
    - Cualquier campo alterado rompe la cadena.

self_correction_events are reported separately (not in hash chain by design).

Usage:
    python3 verify_tool_log.py results/srl2018/VIGIA-REAL-VANKO_bundle.json
    python3 verify_tool_log.py bundle.json --verbose
    python3 verify_tool_log.py bundle.json --hmac-key-hex <hex>
    echo $?   # 0=VERIFIED  1=BROKEN  2=NO_LOG
"""
import argparse
import hashlib
import hmac as _hmac
import json
import os
import sys
from pathlib import Path

GENESIS_V1 = "GENESIS"
GENESIS_V2 = "0" * 64
_STRUCTURAL_FIELDS = frozenset({"seq", "prev_hash", "entry_hash", "entry_hmac"})


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── Copia stdlib-only de vigia/core/canonicalize.py ───────────────────────
# Mantiene su propia copia por diseño (verificador de terceros, sin imports de
# produccion). DEBE quedar en lockstep con vigia/core/canonicalize.py — lo
# verifica tests/test_canonicalize_lockstep.py.
import unicodedata as _unicodedata
from fractions import Fraction as _Fraction

_V2_STR_PREFIX = "s:"


def _v2_norm_str(s):
    return _unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n"))


def _canonicalize_v1(obj):
    """Esquema v1 (LEGACY — solo para verificar bundles historicos)."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return obj
    if obj is None:
        return "null"
    if isinstance(obj, dict):
        return {k: _canonicalize_v1(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v1(v) for v in obj]
    return str(obj)


def _canonicalize_v2(obj):
    """Esquema v2 (R3-2) — DEFAULT. Escalares identicos a v1; strings escapados
    (s: + NFC/CRLF->LF); Fraction explicito. Cierra las colisiones de tipo."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return _V2_STR_PREFIX + _v2_norm_str(obj)
    if obj is None:
        return "null"
    if isinstance(obj, _Fraction):
        return f"{obj.numerator}/{obj.denominator}:frac"
    if isinstance(obj, dict):
        return {k: _canonicalize_v2(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v2(v) for v in obj]
    return _V2_STR_PREFIX + _v2_norm_str(str(obj))


def _canonicalize(obj):
    """Forma canonica DEFAULT (v2)."""
    return _canonicalize_v2(obj)


def _canonical_hash(payload: dict, canon=_canonicalize) -> str:
    canonical = json.dumps(canon(payload), sort_keys=True, ensure_ascii=True)
    return _sha256(canonical)


def _entry_hash_v2(entry: dict, canon=_canonicalize) -> str:
    payload = {k: v for k, v in entry.items() if k not in _STRUCTURAL_FIELDS}
    payload["seq"] = entry.get("seq")
    payload["prev_hash"] = entry.get("prev_hash", "")
    return _canonical_hash(payload, canon=canon)


def _entry_hash_matches(entry: dict, stored: str) -> bool:
    """True si el entry_hash almacenado recomputa bajo v2 O v1 (R3-2 compat)."""
    return any(
        _entry_hash_v2(entry, canon=c) == stored
        for c in (_canonicalize_v2, _canonicalize_v1)
    )


def _resolve_hmac_key(args) -> bytes | None:
    """CLI flags primero; después VIGIA_HMAC_KEY / VIGIA_HMAC_KEY_FILE."""
    if args.hmac_key_hex:
        return bytes.fromhex(args.hmac_key_hex)
    if args.hmac_key_file:
        return Path(args.hmac_key_file).read_bytes().strip()
    key_hex = os.getenv("VIGIA_HMAC_KEY", "").strip()
    if key_hex:
        try:
            return bytes.fromhex(key_hex)
        except ValueError:
            pass
    key_file = os.getenv("VIGIA_HMAC_KEY_FILE", "").strip()
    if key_file and Path(key_file).is_file():
        return Path(key_file).read_bytes().strip()
    return None


# ── Verificación v1 (legacy) ──────────────────────────────────────────────

def _verify_v1(log: list, verbose: bool) -> bool:
    ok = True
    prev_result = None
    for entry in log:
        seq = entry.get("seq", "?")
        tool = entry.get("tool", "?")[:42]
        result = entry.get("result_summary", "")
        prev_hash = entry.get("prev_hash", "")

        if seq == 1:
            if prev_hash != GENESIS_V1:
                print(f"  [FAIL] seq=01 | prev_hash must be GENESIS, got {prev_hash!r}")
                ok = False
            else:
                print(f"  [OK  ] seq=01 | {tool:<42} | GENESIS")
        else:
            expected = _sha256(prev_result) if prev_result is not None else ""
            if prev_hash == expected:
                print(f"  [OK  ] seq={seq:02d} | {tool:<42} | {prev_hash[:16]}...")
            else:
                print(f"  [FAIL] seq={seq:02d} | {tool}")
                print(f"         expected : {expected[:32]}...")
                print(f"         got      : {(prev_hash or '(empty)')[:32]}...")
                ok = False

        if verbose:
            print(f"         result   : {result[:80]}")
        prev_result = result

    print(
        "\n  [CAVEAT v1] Solo result_summary está encadenado. timestamp/tool/"
        "target/input_hash NO son tamper-evident bajo el esquema v1, y el "
        "result_summary de la última entrada es editable. Re-sellar con "
        "chain_version=2 para cobertura completa."
    )
    return ok


# ── Verificación v2 (contenido completo + HMAC opcional) ─────────────────

def _verify_v2(log: list, verbose: bool, hmac_key: bytes | None) -> bool:
    ok = True
    expected_prev = GENESIS_V2
    expected_seq = 1

    for entry in log:
        seq = entry.get("seq", "?")
        tool = str(entry.get("tool", "?"))[:42]
        errors = []

        if seq != expected_seq:
            errors.append(f"seq esperado {expected_seq}, encontrado {seq}")
            expected_seq = seq if isinstance(seq, int) else expected_seq
        if entry.get("prev_hash", "") != expected_prev:
            errors.append("prev_hash no coincide con entry_hash anterior")
        stored = entry.get("entry_hash", "")
        if not _entry_hash_matches(entry, stored):
            recomputed = _entry_hash_v2(entry)
            errors.append(
                f"entry_hash no recomputa (contenido alterado, ni v2 ni v1): "
                f"esperado {recomputed[:16]}..., almacenado {(stored or '(empty)')[:16]}..."
            )
        if hmac_key is not None:
            stored_hmac = entry.get("entry_hmac", "")
            expected_hmac = _hmac.new(
                hmac_key, stored.encode("utf-8"), "sha256"
            ).hexdigest()
            if not stored_hmac:
                errors.append("entry_hmac ausente (clave provista)")
            elif not _hmac.compare_digest(stored_hmac, expected_hmac):
                errors.append("entry_hmac no recomputa — cadena recomputada sin la clave")

        if errors:
            print(f"  [FAIL] seq={seq:>02} | {tool}")
            for err in errors:
                print(f"         {err}")
            ok = False
        else:
            print(f"  [OK  ] seq={seq:>02} | {tool:<42} | {stored[:16]}...")

        if verbose:
            print(f"         result   : {str(entry.get('result_summary', ''))[:80]}")

        expected_prev = stored
        expected_seq = (seq + 1) if isinstance(seq, int) else expected_seq

    if hmac_key is None:
        print(
            "\n  [NOTE] Sin clave HMAC: verificada estructura y contenido, "
            "pero una cadena íntegramente recomputada por un atacante con "
            "acceso de escritura no es detectable sin clave. Pasar "
            "--hmac-key-hex/--hmac-key-file o VIGIA_HMAC_KEY para "
            "verificación keyed."
        )
    return ok


def verify_chain(bundle_path: str, verbose: bool = False, args=None) -> int:
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
    version = "2" if log[0].get("entry_hash") else "1"
    print(f"Bundle : {bundle_path}")
    print(f"Case   : {case_id}")
    print(f"Schema : chain v{version}")
    print(f"Entries: {len(log)} MCP tool calls")
    print()

    if version == "2":
        hmac_key = _resolve_hmac_key(args) if args else None
        ok = _verify_v2(log, verbose, hmac_key)
    else:
        ok = _verify_v1(log, verbose)

    sc = bundle.get("self_correction_events", [])
    if sc:
        print(f"\nself_correction_events: {len(sc)} (not in hash chain — internal ops)")
        for e in sc:
            # Los campos pueden variar según la versión del agente
            seq_val = e.get("seq") or e.get("sequence") or "?"
            tool_val = e.get("tool") or e.get("tool_name") or e.get("event_type") or "?"
            rs_val = (e.get("result_summary") or e.get("summary")
                      or e.get("reason") or e.get("description") or "")
            if not any([e.get("seq"), e.get("tool"), e.get("result_summary")]):
                # Bundle antiguo: mostrar todas las claves disponibles
                rs_val = str({k: str(v)[:40] for k, v in e.items()})[:120]
            print(f"  seq={seq_val} | {str(tool_val)[:30]} | {str(rs_val)[:80]}")

    note = bundle.get("tool_execution_log_note", "")
    if note:
        print(f"\nNote: {note[:140]}")

    status = f"CHAIN VERIFIED ({len(log)} entries, schema v{version})" if ok else "CHAIN BROKEN"
    print(f"\nResult: {status}")
    return 0 if ok else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Verify VIGÍA tool_execution_log hash chain, v1 y v2 (stdlib only)"
    )
    p.add_argument("bundle", help="Path to sealed bundle JSON")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Print result_summary for each entry")
    p.add_argument("--hmac-key-hex", default="",
                   help="Clave HMAC en hex para verificación keyed (v2)")
    p.add_argument("--hmac-key-file", default="",
                   help="Archivo con la clave HMAC en bytes crudos (v2)")
    cli_args = p.parse_args()
    sys.exit(verify_chain(cli_args.bundle, cli_args.verbose, cli_args))
