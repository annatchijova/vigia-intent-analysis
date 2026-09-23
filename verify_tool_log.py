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
    - chain_tip_sha256 (R3-5, opcional, nivel-bundle): ancla el entry_hash de
      la ÚLTIMA entrada FUERA del arreglo tool_execution_log. Sin esto,
      borrar las últimas N entradas deja el resto de la cadena internamente
      válida — nada lo nota. chain_tip_hmac (si hay clave) cierra el
      residual de que chain_tip_sha256 por sí solo es recomputable por
      cualquiera con acceso de escritura.

R5-1 — ANTI-DEGRADACION: el esquema se deduce de TODOS los marcadores v2
(chain_version="2", entry_hash, entry_hmac en cualquier entrada;
chain_tip_sha256 / chain_tip_hmac a nivel bundle), nunca de un unico campo
borrable. Un bundle v2 al que se le borre entry_hash NO cae a la via v1: se
verifica como v2 y falla como contenido alterado. Con clave HMAC provista, un
log v1 se reporta como degradacion salvo --allow-legacy-v1.

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
_V2_ENTRY_MARKERS = ("entry_hash", "entry_hmac")
_V2_BUNDLE_MARKERS = ("chain_tip_sha256", "chain_tip_hmac")
_TRACE_SEMANTIC_FIELDS = (
    "trace_id", "case_id", "trace_version", "sealed_at", "verdict",
    "confidence_submitted", "confidence_stored", "confidence_warnings",
    "quality", "diversity", "contradictions", "steps",
)


def _detect_schema(log: list, bundle: dict) -> tuple:
    """R5-1: el esquema se decide por TODOS los marcadores v2 del bundle, no
    por `log[0]["entry_hash"]`.

    Elegir el esquema a partir de un solo campo borrable convierte al dato
    controlado por el atacante en selector del algoritmo de verificacion: con
    borrar `entry_hash` de la primera entrada, la cadena se validaba por la
    via v1 — que no cubre timestamp/tool/target/input_hash, no recibe la clave
    HMAC y no mira chain_tip_sha256. Si CUALQUIER entrada o el bundle declara
    v2, se verifica como v2; una entrada a la que le falte entry_hash falla
    entonces como contenido alterado, que es lo que es.

    Devuelve (version, markers) — markers documenta por que se eligio v2.
    """
    markers = []
    for entry in log:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("chain_version", "")) == "2":
            markers.append(f'seq={entry.get("seq", "?")}: chain_version="2"')
        for field in _V2_ENTRY_MARKERS:
            if field in entry:
                markers.append(f'seq={entry.get("seq", "?")}: {field}')
    markers += [f"bundle: {f}" for f in _V2_BUNDLE_MARKERS if f in bundle]
    return ("2" if markers else "1"), markers


# R3-4: ventana forense plausible (mismos limites fijos que la libreria /
# regla TCV R3-1). Techo 2038 = overflow epoch 32-bit.
from datetime import datetime as _dt, timezone as _tz
_PLAUSIBLE_MIN = _dt(2000, 1, 1, tzinfo=_tz.utc)
_PLAUSIBLE_MAX = _dt(2038, 1, 19, 3, 14, 7, tzinfo=_tz.utc)


def _parse_iso_ts(ts):
    if not isinstance(ts, str) or not ts.strip():
        return None
    try:
        d = _dt.fromisoformat(ts.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo is not None else d.replace(tzinfo=_tz.utc)


def _check_timeline(log):
    """R3-4: plausibilidad del orden causal, SEPARADA de la integridad del
    hash. Devuelve (plausible: bool, anomalies: list). Una historia
    causalmente imposible NO rompe el sello — la cadena prueba orden de
    insercion e integridad, no causalidad."""
    anomalies = []
    prev_ts = prev_seq = None
    seen = {}
    for entry in log:
        seq = entry.get("seq", "?")
        dt = _parse_iso_ts(entry.get("timestamp"))
        if dt is not None:
            if not (_PLAUSIBLE_MIN <= dt < _PLAUSIBLE_MAX):
                anomalies.append((seq, "OUT_OF_RANGE_TIMESTAMP", entry.get("timestamp")))
            if prev_ts is not None and dt < prev_ts:
                anomalies.append((seq, "NON_MONOTONIC_TIMESTAMP",
                                  f"antes de seq={prev_seq}"))
            prev_ts, prev_seq = dt, seq
        sig = _canonical_hash({k: v for k, v in entry.items()
                               if k not in _STRUCTURAL_FIELDS
                               and k not in ("timestamp", "event_id")})
        if sig in seen:
            anomalies.append((seq, "DUPLICATE_CONTENT", f"= seq={seen[sig]}"))
        else:
            seen[sig] = seq
    return (not anomalies), anomalies


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

def _verify_v1(log: list, verbose: bool, hmac_key: bytes | None = None,
               allow_legacy: bool = False) -> bool:
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
    # R5-1 (residual): quien tiene la clave espera autenticidad. El esquema v1
    # no puede darla — no hay entry_hmac que verificar — asi que un atacante
    # que borre TODOS los marcadores v2 quedaria indistinguible de un bundle
    # legacy. Con clave en mano eso se reporta como degradacion, no como
    # "VERIFIED". --allow-legacy-v1 es la via explicita para bundles historicos.
    if hmac_key is not None and not allow_legacy:
        print(
            "  [FAIL] esquema v1 con clave HMAC provista: v1 no lleva "
            "entry_hmac, asi que la cadena no puede autenticarse. Si el bundle "
            "fue sellado en v2, esto es una DEGRADACION de esquema; si es un "
            "bundle historico genuino, re-ejecutar con --allow-legacy-v1."
        )
        ok = False
    return ok


# ── Verificación v2 (contenido completo + HMAC opcional) ─────────────────

def _verify_v2(
    log: list, verbose: bool, hmac_key: bytes | None,
    expected_tip: str | None = None, expected_tip_hmac: str | None = None,
) -> bool:
    ok = True
    expected_prev = GENESIS_V2
    expected_seq = 1
    # R5-2: "este bundle fue sellado con clave" es observable por el entry_hmac
    # de las entradas, no por lo que el atacante haya dejado a nivel bundle.
    keyed_entries = any(
        isinstance(e, dict) and e.get("entry_hmac") for e in log
    )

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

    # R3-5: anclaje de cola — expected_prev sostiene el tip recomputado
    # (entry_hash de la última entrada, o GENESIS_V2 si el log está vacío).
    if expected_tip is not None:
        if expected_prev != expected_tip:
            print(
                f"  [FAIL] chain_tip_sha256 | bundle declara "
                f"{expected_tip[:16]}..., recomputado {expected_prev[:16]}... "
                f"— entradas borradas o agregadas después del sellado"
            )
            ok = False
        else:
            print(f"  [OK  ] chain_tip_sha256 | coincide con la punta recomputada")
        if hmac_key is not None and expected_tip_hmac is None and keyed_entries:
            # R5-2: mismo borrado, un campo mas adentro — chain_tip_sha256 solo
            # es recomputable por cualquiera con acceso de escritura; el HMAC de
            # la punta es lo unico que lo ancla. Borrarlo lo deja recomputable.
            print(
                "  [FAIL] chain_tip_hmac ausente en un bundle con entry_hmac: "
                "chain_tip_sha256 sin su HMAC es recomputable por quien escriba "
                "el archivo."
            )
            ok = False
        if hmac_key is not None and expected_tip_hmac is not None:
            expected = _hmac.new(hmac_key, expected_prev.encode("utf-8"), "sha256").hexdigest()
            if not _hmac.compare_digest(expected_tip_hmac, expected):
                print(
                    "  [FAIL] chain_tip_hmac | no recomputa — la punta fue "
                    "recalculada sin la clave"
                )
                ok = False
            else:
                print("  [OK  ] chain_tip_hmac | coincide")
    elif hmac_key is not None and keyed_entries:
        # R5-2: un bundle sellado con clave SIEMPRE lleva chain_tip_sha256 y
        # chain_tip_hmac (ToolExecutionLogChain.bundle_fields los emite juntos).
        # Si las entradas traen entry_hmac pero el ancla no esta, fue borrada
        # despues del sellado — y sin ancla, truncar la cola vuelve a ser
        # indetectable. Ausencia != bundle viejo cuando hay HMAC por entrada.
        print(
            "  [FAIL] chain_tip_sha256 ausente en un bundle con entry_hmac: "
            "el sellado keyed siempre ancla la punta. El ancla fue borrada — "
            "truncar la cola seria indetectable."
        )
        ok = False
    else:
        print(
            "\n  [NOTE] Sin chain_tip_sha256 en el bundle: truncar la cola "
            "(borrar las últimas entradas) es indetectable solo por linkage "
            "— ver R3-5 en docs/REDTEAM_ROUND3_EMERGENT.md."
        )

    if hmac_key is None:
        print(
            "\n  [NOTE] Sin clave HMAC: verificada estructura y contenido, "
            "pero una cadena íntegramente recomputada por un atacante con "
            "acceso de escritura no es detectable sin clave. Pasar "
            "--hmac-key-hex/--hmac-key-file o VIGIA_HMAC_KEY para "
            "verificación keyed."
        )
    return ok


def _looks_like_trace(doc: dict) -> bool:
    """Una reasoning trace sellada: artefacto hermano del bundle, con cadena
    propia. Se reconoce por trace_id + verdict (ver vigia/core/reasoning_trace)."""
    return isinstance(doc.get("trace_id"), str) and "verdict" in doc


def _trace_payload_hash(trace: dict) -> str:
    """Stdlib mirror of reasoning_trace._trace_payload_hash()."""
    payload = {field: trace.get(field) for field in _TRACE_SEMANTIC_FIELDS}
    encoded = json.dumps(
        payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _check_trace_manifest(trace: dict) -> bool:
    """Verify that the displayed trace, not only its tool log, is sealed.

    The manifest is embedded in the HMAC-covered DECISION entry.  This keeps a
    valid chain from authenticating mutable sibling fields such as ``steps``.
    """
    declared = trace.get("trace_payload_sha256")
    if not isinstance(declared, str) or declared != _trace_payload_hash(trace):
        print("  [FAIL] trace semantic manifest absent or does not match displayed content")
        return False

    entries = [
        entry for entry in trace.get("tool_execution_log", [])
        if isinstance(entry, dict) and entry.get("tool") == "reasoning:decision"
    ]
    marker = f"trace_payload_sha256={declared};"
    if len(entries) != 1 or not str(entries[0].get("result_summary", "")).startswith(marker):
        print("  [FAIL] trace semantic manifest is not bound by the DECISION chain entry")
        return False

    decisions = [
        step for step in trace.get("steps", []) if isinstance(step, dict)
        and step.get("kind") == "decision" and isinstance(step.get("payload"), dict)
    ]
    if len(decisions) != 1 or decisions[0]["payload"].get("verdict") != trace.get("verdict"):
        print("  [FAIL] trace top-level verdict disagrees with its DECISION step")
        return False
    print("  [OK  ] trace semantic manifest + DECISION binding")
    return True


def _find_sibling_bundle(trace_path: str):
    """<stem>_reasoning_trace.json -> <stem>.json, si existe."""
    p = Path(trace_path)
    marker = "_reasoning_trace.json"
    if not p.name.endswith(marker):
        return None
    sibling = p.with_name(p.name[: -len(marker)] + ".json")
    return sibling if sibling.is_file() else None


def _check_trace_pairing(trace: dict, trace_path: str, bundle_arg: str) -> bool:
    """R7-1: la traza vive FUERA del digest del bundle — es un archivo aparte
    con integridad propia. Su cadena puede estar perfectamente intacta y aun asi
    explicar OTRO caso: nada en la cadena dice a que bundle pertenece.

    `vigia/core/reasoning_trace.verify_reasoning_trace` implementa la
    comparacion (case_id + verdict) y su docstring la declara obligatoria
    — "MUST fail verification, never be silently reconciled" — pero solo se
    llamaba desde un test: ningun CLI la exponia. Medido: la traza de un caso
    SUSPICION presentada junto al bundle de un caso MALICE daba
    "CHAIN VERIFIED", exit 0.

    Devuelve True si el emparejamiento es correcto o no habia con que
    compararlo; False si diverge. Nunca pasa en silencio: cuando no se puede
    comparar, lo dice.
    """
    path = bundle_arg or _find_sibling_bundle(trace_path)
    if not path:
        print("\n  [NOTE] Reasoning trace verificada EN AISLAMIENTO: no se "
              "encontro el bundle hermano. La cadena prueba que la traza no "
              "fue alterada, NO que explique el bundle que la acompana. "
              "Pasar --paired-bundle <path> para verificar el emparejamiento.")
        return True
    try:
        bundle = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"\n  [FAIL] Pairing: no se pudo leer el bundle {path}: {exc}")
        return False

    ok = _check_trace_manifest(trace)
    print(f"\nPairing traza <-> bundle: {path}")
    t_case, b_case = trace.get("case_id"), bundle.get("case_id")
    if t_case != b_case:
        print(f"  [FAIL] case_id | traza={t_case!r} bundle={b_case!r}")
        ok = False
    else:
        print(f"  [OK  ] case_id | {t_case!r}")

    t_verdict = trace.get("verdict")
    b_verdict = bundle.get("agent_verdict")
    if b_verdict is None:
        print("  [NOTE] el bundle no declara agent_verdict: veredicto NO comparado")
    elif t_verdict != b_verdict:
        print(f"  [FAIL] veredicto | la traza registro {t_verdict!r} pero el "
              f"bundle sellado dice {b_verdict!r} — la traza se construyo a "
              f"partir de otro resultado que el que se sello")
        ok = False
    else:
        print(f"  [OK  ] veredicto | {t_verdict!r}")
    return ok


def verify_chain(bundle_path: str, verbose: bool = False, args=None) -> int:
    try:
        bundle = json.loads(Path(bundle_path).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    log = bundle.get("tool_execution_log", [])
    if not log:
        # R6-3: un bundle que declara chain_tip_sha256 SELLO una cadena. Si el
        # arreglo no esta, no es "un bundle EBS sin log" — es un log borrado.
        # Sin este chequeo, borrar el log entero daba exit 2 (NO_LOG) mientras
        # el sello seguia intacto: nadie decia que faltaba algo que se sello.
        if bundle.get("chain_tip_sha256"):
            print("NO tool_execution_log, pero el bundle declara "
                  f"chain_tip_sha256={bundle['chain_tip_sha256'][:16]}...")
            print("  [FAIL] el bundle sello una cadena de herramientas y el "
                  "arreglo no esta: el log fue borrado despues del sellado.")
            print("\nResult: CHAIN BROKEN")
            return 1
        print("NO tool_execution_log — fallback/EBS bundle.")
        print("Use: python3 forensics/verify_ebs_v1.py <bundle> --verbose")
        return 2

    # R5-3 (hygiene): un log malformado debe dar un diagnostico, no un
    # traceback. El exit code ya era 1 por la excepcion — fail-safe — pero un
    # traceback no le dice a un perito que mirar.
    if not isinstance(log, list):
        print(f"ERROR: tool_execution_log debe ser una lista, es {type(log).__name__}")
        return 1
    bad = [i for i, e in enumerate(log) if not isinstance(e, dict)]
    if bad:
        print(f"ERROR: entradas malformadas (no son objetos JSON) en los "
              f"indices {bad[:10]} de tool_execution_log")
        return 1

    case_id = (bundle.get("case_id")
               or bundle.get("metadata", {}).get("case_id", "UNKNOWN"))
    version, markers = _detect_schema(log, bundle)
    hmac_key = _resolve_hmac_key(args) if args else None
    allow_legacy = bool(getattr(args, "allow_legacy_v1", False))
    print(f"Bundle : {bundle_path}")
    print(f"Case   : {case_id}")
    print(f"Schema : chain v{version}")
    print(f"Entries: {len(log)} MCP tool calls")
    if version == "2":
        print(f"v2 markers: {len(markers)} ({', '.join(markers[:3])}"
              f"{', ...' if len(markers) > 3 else ''})")
    print()

    if version == "2":
        expected_tip = bundle.get("chain_tip_sha256")
        expected_tip_hmac = bundle.get("chain_tip_hmac")
        ok = _verify_v2(log, verbose, hmac_key, expected_tip, expected_tip_hmac)
    else:
        ok = _verify_v1(log, verbose, hmac_key, allow_legacy)

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

    # R7-1: si el archivo es una reasoning trace, su cadena intacta NO prueba
    # que pertenezca al bundle con el que se la presenta.
    if _looks_like_trace(bundle):
        if not _check_trace_pairing(bundle, bundle_path,
                                    getattr(args, "paired_bundle", "") if args else ""):
            ok = False

    status = f"CHAIN VERIFIED ({len(log)} entries, schema v{version})" if ok else "CHAIN BROKEN"
    print(f"\nResult: {status}")

    # R3-4: plausibilidad temporal — reportada por SEPARADO. Una linea de tiempo
    # implausible NO invalida el sello (no cambia el exit code): la cadena
    # prueba orden de insercion e integridad, no causalidad. Se informa para que
    # "CHAIN VERIFIED" nunca se lea como "la cronologia es plausible".
    plausible, anomalies = _check_timeline(log)
    if plausible:
        print("Timeline: PLAUSIBLE (timestamps monotonos y en rango)")
    else:
        print(f"Timeline: {len(anomalies)} ANOMALIA(S) — cronologia implausible "
              f"(NO invalida el sello; la cadena prueba orden de insercion, no causalidad):")
        for seq, kind, detail in anomalies:
            print(f"  seq={seq} | {kind} | {detail}")

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
    # dest propio: el argumento posicional ya ocupa "bundle", y una colision
    # de dest hace que el flag pise la ruta del archivo a verificar.
    p.add_argument("--paired-bundle", dest="paired_bundle", default="",
                   help="Bundle sellado con el que emparejar una reasoning "
                        "trace (case_id + veredicto). Por defecto se busca el "
                        "hermano <stem>.json — R7-1.")
    p.add_argument("--allow-legacy-v1", action="store_true",
                   help="Aceptar un bundle esquema v1 aunque se haya provisto "
                        "clave HMAC (bundles historicos). Sin este flag, v1 + "
                        "clave se reporta como degradacion de esquema — R5-1.")
    cli_args = p.parse_args()
    sys.exit(verify_chain(cli_args.bundle, cli_args.verbose, cli_args))
