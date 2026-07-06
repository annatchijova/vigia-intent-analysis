#!/usr/bin/env python3
"""
VIGÍA — Batch runner: corre todos los casos JSON con vigia_agent.py
Guarda bundles en results/agent_batch/ y reporta pass/fail vs expected_verdict.

Usage:
    python3 run_all_agent.py                          # todos los casos
    python3 run_all_agent.py --filter VIGIA-FN        # solo FN
    python3 run_all_agent.py --filter VIGIA-BREAK     # solo BREAK
    python3 run_all_agent.py --dir data/cases/benign  # un subdirectorio
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
REPO         = Path(__file__).parent
CASES_DIRS   = [
    REPO / "data/cases",
    REPO / "data/cases/converted",
    REPO / "data/cases/benign",
    REPO / "data/cases/consolidated_canonical",
    REPO / "data/cases/legacy",
]
OUTPUT_DIR   = REPO / "results" / "agent_batch"
AGENT        = REPO / "vigia_agent.py"
PYTHON       = sys.executable

# Archivos que no son casos individuales
SKIP_STEMS = {
    "_index", "dataset", "calibration", "covariance", "correlation",
    "vigia_forensic_cases", "vigia_60_cases", "vigia_cases_canonical",
    "vigia_input_defcon", "fsv_schema", "phonetic_dict",
}

RED  = "\033[91m"; GRN = "\033[92m"; YEL = "\033[93m"
CYA  = "\033[96m"; RST = "\033[0m";  BLD = "\033[1m"


def check_label_consistency(dirs: list[Path] | None = None) -> list[dict]:
    """
    R3-3 (docs/REDTEAM_ROUND3_EMERGENT.md): guard de fuente-unica-de-verdad.

    El runner deduplica casos por stem tomando el primer directorio de
    CASES_DIRS, asi que una copia sombra de un caso en CUALQUIER otra carpeta
    (converted/, legacy/, consolidated_canonical/, benign/) con expected_verdict
    distinto al que gana por precedencia queda muerta y puede voltear la metrica
    en silencio (fue el bug del shadow de VIGIA-FP-001, Ronda 2.1, y del shadow
    legacy/ de case_008). Este chequeo agrupa por stem TODAS las copias en TODAS
    las carpetas y devuelve las divergencias de expected_verdict. main() aborta
    fuerte si la lista no esta vacia.

    Censo COMPLETO (no solo data/cases vs converted): cierra todos los shadows,
    no un par especifico de carpetas.
    """
    dirs = dirs if dirs is not None else CASES_DIRS

    def _label(path: Path) -> str:
        try:
            d = json.loads(path.read_text())
            if isinstance(d, dict):
                return (d.get("expected_verdict")
                        or d.get("ground_truth", {}).get("expected_verdict")
                        or "UNKNOWN")
            return "MALFORMED"
        except Exception:
            return "ERROR"

    # Agrupar por stem todas las copias, en el ORDEN de precedencia de dirs
    # (el primero es el que usa el runner).
    by_stem: dict[str, list[Path]] = {}
    for d in dirs:
        d = Path(d)
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            s = f.stem.lower()
            # Honrar la misma lista de no-casos que find_cases.
            if s in SKIP_STEMS or any(skip in s for skip in SKIP_STEMS):
                continue
            by_stem.setdefault(f.stem, []).append(f)

    conflicts: list[dict] = []
    for stem, paths in sorted(by_stem.items()):
        if len(paths) < 2:
            continue
        labels = {str(p): _label(p) for p in paths}
        if len(set(labels.values())) > 1:
            conflicts.append({
                "stem": stem,
                "winner": str(paths[0]),          # el que usa el runner
                "labels": labels,
            })
    return conflicts


def find_cases(dirs: list[Path], filter_str: str = "") -> list[Path]:
    seen = set()
    cases = []
    for d in dirs:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if f.stem.lower() in SKIP_STEMS:
                continue
            if any(skip in f.stem.lower() for skip in SKIP_STEMS):
                continue
            if filter_str and filter_str.upper() not in f.stem.upper():
                continue
            if f.stem in seen:
                continue
            seen.add(f.stem)
            cases.append(f)
    return cases


def extract_expected(case_path: Path) -> str:
    try:
        data = json.loads(case_path.read_text())
        return (data.get("expected_verdict")
                or data.get("ground_truth", {}).get("expected_verdict")
                or "UNKNOWN")
    except Exception:
        return "UNKNOWN"


# B-058 (B10): el veredicto sellado por el agente (agent_verdict, escrito por
# _seal_bundle vía classify_agent_verdict) es la ÚNICA fuente autoritativa —
# es el mismo valor que decide el exit code. Su escala es de 4 valores:
# {MALICE, INTENT, ABSTAIN, NOISE}. NO tiene escalón SUSPICION (SUSPICION_DETECTED
# se sella como INTENT) ni UNKNOWN.
_AGENT_VERDICT_VALUES = {"MALICE", "INTENT", "ABSTAIN", "NOISE"}

# Derivación legacy desde best_hypothesis — SOLO para bundles previos al campo
# agent_verdict. Re-derivar de best_hypothesis puede DIVERGIR del veredicto
# sellado (p.ej. SUSPICION_DETECTED → "SUSPICION" acá vs "INTENT" sellado), que
# es exactamente la divergencia que B-058 pedía dejar de enmascarar.
_HYP_MAP = {
    "MALICE": "MALICE", "SUSPICION": "SUSPICION", "UNKNOWN": "UNKNOWN",
    "NOISE": "NOISE", "ABSTAIN": "ABSTAIN", "BENIGN": "NOISE", "INTENT": "INTENT",
    "MALICIOUS_INTENT_DETECTED": "MALICE",
    "MALICIOUS_ACTIVITY_DETECTED": "MALICE",
    "INTENT_DETECTED": "INTENT",
    "SUSPICION_DETECTED": "SUSPICION",
    "NO_SEMIOTIC_ANOMALY_DETECTED": "NOISE",
    "ABSTAIN_DETECTED":           "ABSTAIN",
    "NO_THREAT_DETECTED": "NOISE",
    "BENIGN_ACTIVITY": "NOISE",
    "INSUFFICIENT_EVIDENCE": "UNKNOWN",
    "INCONCLUSIVE": "UNKNOWN",
}


def extract_verdict_from_bundle(bundle_path: Path) -> str:
    """Lee el veredicto SELLADO del bundle (agent_verdict), sin re-derivarlo.

    B-058 (B10): lee el campo top-level `agent_verdict` que `_seal_bundle`
    embebe — el mismo veredicto que decide el exit code del agente. Solo si el
    campo está ausente (bundles previos a su introducción) cae al camino legacy
    de re-derivación desde `best_hypothesis`. Así el batch nunca reporta un
    veredicto distinto del que el agente efectivamente selló.
    """
    try:
        data = json.loads(bundle_path.read_text())
        # 0. B10 (B-058): el campo top-level `agent_verdict` es el veredicto
        #    SELLADO — la salida de classify_agent_verdict, el camino único que
        #    sella el bundle y decide el exit (CLAUDE.md). Es POST-gate: cuando la
        #    auto-correccion pre-emision de VIGIA ajusta el veredicto del reasoner,
        #    `agent_verdict` y `best_hypothesis` (pre-gate) divergen. Leerlo directo
        #    evita re-derivar el equivocado. Solo se acepta si es un veredicto
        #    canonico conocido; cualquier otra cosa (None, legacy, vocabulario
        #    futuro) cae a la heuristica de abajo, preservando la compatibilidad.
        sealed = data.get("agent_verdict")
        if isinstance(sealed, str) and sealed in _HYP_MAP:
            return _HYP_MAP[sealed]
        # 1. Campo verdict directo (audit_trail entry)
        for entry in data.get("audit_trail", {}).get("entries", []):
            if entry.get("action") == "AGENT_EXIT":
                v = entry.get("inputs_summary", {}).get("verdict", "")
                if v in _HYP_MAP:
                    return _HYP_MAP[v]
        # 2. pipeline_results.abduction.best_hypothesis
        hyp = (data.get("pipeline_results", {})
                   .get("abduction", {})
                   .get("best_hypothesis", ""))
        if hyp in _HYP_MAP:
            return _HYP_MAP[hyp]
        # 3. Prefix matching para variantes no conocidas (legacy).
        hyp_up = hyp.upper()
        if "MALICI" in hyp_up or "MALICE" in hyp_up:
            return "MALICE"
        if "NO_SEMIOTIC" in hyp_up or "NO_THREAT" in hyp_up or "BENIGN" in hyp_up:
            return "NOISE"
        if "SUSPICION" in hyp_up:
            return "SUSPICION"
        return "UNKNOWN"
    except Exception:
        return "ERROR"


def verdict_matches(expected: str, got: str) -> bool:
    """Doctrina de comparación etiqueta-esperada vs veredicto-del-agente.

    El veredicto del agente vive en su escala de 4 valores
    {MALICE, INTENT, ABSTAIN, NOISE}; las etiquetas del corpus son de 6
    (agregan SUSPICION y UNKNOWN). Reglas:

      * alias BENIGN → NOISE en ambos lados.
      * expected == UNKNOWN → siempre PASS (caso sin ground truth accionable).
      * over-severity: expected INTENT + got MALICE → PASS (MALICE ⊃ INTENT +
        ocultamiento; sobre-severidad, no error de dirección — Fase 2 §4).
      * expected SUSPICION + got INTENT → PASS: la escala del agente no tiene
        escalón SUSPICION; su tier INTENT representa "INTENT/SUSPICION"
        (documentado en B-073). La sub-severidad (INTENT→SUSPICION) NO existe
        acá porque el agente nunca emite SUSPICION.
    """
    aliases = {"BENIGN": "NOISE"}
    g = aliases.get(got, got)
    e = aliases.get(expected, expected)
    if expected == "UNKNOWN":
        return True
    if g == e:
        return True
    if e == "INTENT" and g == "MALICE":
        return True
    if e == "SUSPICION" and g == "INTENT":
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", default="", help="Filtrar por nombre de caso")
    parser.add_argument("--dir", default="", help="Directorio específico")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar casos sin correr")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout por caso (seg)")
    parser.add_argument("--rerun", action="store_true",
                        help="Forzar re-ejecución del agente aunque exista un "
                             "bundle sellado (default: bundle existente gana)")
    args = parser.parse_args()

    # R3-3: fail-loud si data/cases/ y data/cases/converted/ discrepan en la
    # etiqueta de un mismo stem — el runner usaria una y descartaria la otra en
    # silencio (bug del shadow de VIGIA-FP-001, Ronda 2.1).
    conflicts = check_label_consistency()
    if conflicts:
        print(f"{RED}{BLD}[R3-3] ETIQUETAS DIVERGENTES entre data/cases/ y "
              f"data/cases/converted/ — fuente de verdad ambigua:{RST}")
        for c in conflicts:
            print(f"  {c['stem']}: {c['labels']}")
        print(f"{RED}Reconcilie las copias antes de correr el corpus "
              f"(o corrija check_label_consistency).{RST}")
        sys.exit(2)

    dirs = [Path(args.dir)] if args.dir else CASES_DIRS
    cases = find_cases(dirs, args.filter)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"  VIGÍA Batch Agent Runner — {len(cases)} casos")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*70}\n")

    if args.dry_run:
        for c in cases:
            print(f"  {c.stem}")
        return

    results = []
    start_total = time.time()

    for i, case_path in enumerate(cases, 1):
        case_id = case_path.stem
        expected = extract_expected(case_path)
        output_path = OUTPUT_DIR / f"{case_id}_agent_bundle.json"

        print(f"[{i:3d}/{len(cases)}] {case_id:<40} exp={expected:<12}", end="", flush=True)

        t0 = time.time()
        try:
            # ── Cache de bundles sellados (2026-07-06, pedido de Anna) ──────
            # Default: si ya existe un bundle con agent_verdict sellado, se
            # usa ese veredicto sin re-correr el agente. --rerun fuerza la
            # re-ejecución. PROCEDENCIA: cada bundle declara su era via
            # pipeline_meta.ebs_adapter_mode ("motor" = post-B-075 ciego a la
            # etiqueta; "legacy" = eco de etiqueta explícito; AUSENTE =
            # sellado pre-B-075, era del label leak P2-C). El censo de
            # procedencia se imprime en el resumen: un PASS sostenido por un
            # bundle pre-B-075/legacy mide reproducción de etiqueta, no
            # detección (docs/FASE1_RESOLVE_EBS.md).
            cached = False
            cache_mode = None
            if not args.rerun and output_path.exists():
                try:
                    _bundle = json.loads(output_path.read_text())
                    _sealed = _bundle.get("agent_verdict")
                    if _sealed:
                        cached = True
                        cache_mode = (_bundle.get("pipeline_results", {})
                                      .get("pipeline_meta", {})
                                      .get("ebs_adapter_mode") or "pre-B075")
                        got = extract_verdict_from_bundle(output_path)
                except (json.JSONDecodeError, OSError):
                    cached = False  # bundle ilegible → correr el agente

            if not cached:
                proc = subprocess.run(
                    [PYTHON, str(AGENT),
                     "--evidence", str(case_path),
                     "--case-id", case_id,
                     "--output", str(output_path)],
                    capture_output=True, text=True,
                    timeout=args.timeout,
                    cwd=REPO,
                )
                if output_path.exists():
                    got = extract_verdict_from_bundle(output_path)
                else:
                    got = "NO_BUNDLE"
            elapsed = time.time() - t0

            # B-058 (B10): doctrina de comparación centralizada en
            # verdict_matches (over-severity INTENT⊆MALICE, SUSPICION⊆tier
            # INTENT del agente, UNKNOWN siempre PASS, alias BENIGN→NOISE).
            ok = verdict_matches(expected, got)

            status = f"{GRN}PASS{RST}" if ok else f"{RED}FAIL{RST}"
            tag = f" {CYA}[CACHED:{cache_mode}]{RST}" if cached else ""
            print(f"  got={got:<12} {status}  ({elapsed:.1f}s){tag}")

            results.append({
                "case_id": case_id,
                "expected": expected,
                "got": got,
                "pass": ok,
                "elapsed": round(elapsed, 1),
                "cached": cached,
                "cache_mode": cache_mode,
            })

        except subprocess.TimeoutExpired:
            print(f"  {YEL}TIMEOUT{RST} ({args.timeout}s)")
            results.append({"case_id": case_id, "expected": expected, "got": "TIMEOUT", "pass": False, "elapsed": args.timeout})
        except Exception as e:
            print(f"  {RED}ERROR: {e}{RST}")
            elapsed = time.time() - t0
            results.append({"case_id": case_id, "expected": expected, "got": "ERROR", "pass": False, "elapsed": round(elapsed, 1)})

    # ── Resumen ───────────────────────────────────────────────────────────────
    total_elapsed = time.time() - start_total
    passed = sum(1 for r in results if r["pass"])
    failed = [r for r in results if not r["pass"]]

    print(f"\n{'─'*70}")
    print(f"  Results: {GRN}{passed}/{len(results)} PASS{RST}  {RED}{len(failed)} FAIL{RST}")

    # ── Censo de procedencia del cache ────────────────────────────────────────
    n_cached = sum(1 for r in results if r.get("cached"))
    if n_cached:
        from collections import Counter
        census = Counter(r.get("cache_mode") for r in results if r.get("cached"))
        census_str = ", ".join(f"{m}: {n}" for m, n in census.most_common())
        print(f"  Cache: {n_cached}/{len(results)} desde bundle sellado ({census_str})")
        stale = sum(n for m, n in census.items() if m != "motor")
        if stale:
            print(f"  {YEL}⚠ {stale} bundle(s) cacheados son pre-B-075/legacy: sus "
                  f"veredictos provienen de la era del eco de etiqueta (P2-C).{RST}")
            print(f"  {YEL}  Un PASS sostenido por esos bundles mide reproducción de "
                  f"etiqueta, no detección. Para la métrica honesta: --rerun{RST}")
    if failed:
        print(f"\n  FAILED CASES:")
        for r in failed:
            print(f"    - {r['case_id']}: agent={r['got']} (exp={r['expected']})")
    print(f"\n  Total time: {total_elapsed:.0f}s  |  Avg: {total_elapsed/max(len(results),1):.1f}s/caso")
    print(f"{'='*70}\n")

    # Guardar resumen
    summary_path = OUTPUT_DIR / "_batch_summary.json"
    import datetime
    summary = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_elapsed_s": round(total_elapsed, 1),
        "avg_elapsed_s": round(total_elapsed / max(len(results), 1), 1),
        "passed": passed,
        "total": len(results),
        "results": results,
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"  Resumen guardado en: {summary_path}")


if __name__ == "__main__":
    main()
