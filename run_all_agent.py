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
    # R3-3c: bundle pre-migración (lista JSON de 10 casos que existen
    # individualmente en converted/) — double-contaba y auto-pasaba como
    # UNKNOWN. Se conserva en disco como historia; no es un caso.
    "vigia_break_001-010",
}


def _is_skipped(stem: str) -> bool:
    """R3-3c: matching por PREFIJO, no substring. El substring se tragaba el
    caso real VIGIA_BREAK_005_FALSE_CORRELATION (contiene "correlation") —
    nunca entró al corpus. Los términos de SKIP_STEMS nombran familias de
    archivos auxiliares por prefijo (dataset_*, vigia_cases_canonical_*, ...);
    censo 2026-07-07: prefijo cubre todos los auxiliares reales sin falsos
    positivos."""
    s = stem.lower()
    return s in SKIP_STEMS or any(s.startswith(t) for t in SKIP_STEMS)

RED  = "\033[91m"; GRN = "\033[92m"; YEL = "\033[93m"
CYA  = "\033[96m"; RST = "\033[0m";  BLD = "\033[1m"


def check_label_consistency(base_dir: Path | None = None,
                            converted_dir: Path | None = None,
                            dirs: list[Path] | None = None) -> list[dict]:
    """
    R3-3 (docs/REDTEAM_ROUND3_EMERGENT.md): guard de fuente-unica-de-verdad.

    El runner deduplica casos por stem tomando el primer directorio de
    CASES_DIRS, asi que una copia sombra con expected_verdict distinto queda
    muerta y puede voltear la metrica en silencio (fue exactamente el bug del
    shadow de VIGIA-FP-001, Ronda 2.1). Este chequeo enumera los stems
    duplicados y devuelve la lista de divergencias de expected_verdict.
    main() aborta fuerte si la lista no esta vacia.

    R3-3b (censo 2026-07-07): la version original solo comparaba data/cases/
    contra converted/ — la divergencia viva estaba en legacy/
    (case_008_multi_source_fraud_demo, relabel cdeb32f nunca propagado).
    Ahora cubre TODOS los pares de directorios: `dirs` (default: CASES_DIRS
    completo). base_dir/converted_dir se conservan por compatibilidad.
    """
    if dirs is None:
        if base_dir is not None or converted_dir is not None:
            dirs = [
                Path(base_dir) if base_dir else (REPO / "data/cases"),
                Path(converted_dir) if converted_dir else (REPO / "data/cases/converted"),
            ]
        else:
            dirs = CASES_DIRS

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

    # stem -> {path: label} sobre todos los dirs, honrando la misma lista de
    # no-casos que find_cases: un archivo que el runner nunca carga como caso
    # no es ground truth.
    by_stem: dict[str, dict[str, str]] = {}
    for d in dirs:
        d = Path(d)
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if _is_skipped(f.stem):
                continue
            by_stem.setdefault(f.stem, {})[str(f)] = _label(f)

    conflicts: list[dict] = []
    for stem, labels in sorted(by_stem.items()):
        if len(labels) > 1 and len(set(labels.values())) > 1:
            conflicts.append({"stem": stem, "labels": labels})
    return conflicts


def find_cases(dirs: list[Path], filter_str: str = "") -> list[Path]:
    seen = set()
    cases = []
    for d in dirs:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if _is_skipped(f.stem):
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


def extract_verdict_from_bundle(bundle_path: Path) -> str:
    """Lee el veredicto del bundle usando campos estructurados, sin búsqueda en texto libre."""
    _MAP = {
        # Veredictos canónicos
        "MALICE": "MALICE", "SUSPICION": "SUSPICION", "UNKNOWN": "UNKNOWN",
        "NOISE": "NOISE", "ABSTAIN": "ABSTAIN", "BENIGN": "NOISE", "INTENT": "INTENT",
        # Veredictos del agente (best_hypothesis)
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
    try:
        data = json.loads(bundle_path.read_text())
        # 1. Campo verdict directo (audit_trail entry)
        for entry in data.get("audit_trail", {}).get("entries", []):
            if entry.get("action") == "AGENT_EXIT":
                v = entry.get("inputs_summary", {}).get("verdict", "")
                if v in _MAP:
                    return _MAP[v]
        # 2. pipeline_results.abduction.best_hypothesis
        hyp = (data.get("pipeline_results", {})
                   .get("abduction", {})
                   .get("best_hypothesis", ""))
        if hyp in _MAP:
            return _MAP[hyp]
        # 3. Prefix matching para variantes no conocidas
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", default="", help="Filtrar por nombre de caso")
    parser.add_argument("--dir", default="", help="Directorio específico")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar casos sin correr")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout por caso (seg)")
    args = parser.parse_args()

    # R3-3/R3-3b: fail-loud si CUALQUIER par de CASES_DIRS discrepa en la
    # etiqueta de un mismo stem — el runner usaria una y descartaria la otra en
    # silencio (bug del shadow de VIGIA-FP-001, Ronda 2.1; divergencia de
    # case_008 en legacy/, censo 2026-07-07).
    conflicts = check_label_consistency(dirs=CASES_DIRS)
    if conflicts:
        print(f"{RED}{BLD}[R3-3] ETIQUETAS DIVERGENTES entre directorios del "
              f"corpus — fuente de verdad ambigua:{RST}")
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
            proc = subprocess.run(
                [PYTHON, str(AGENT),
                 "--evidence", str(case_path),
                 "--case-id", case_id,
                 "--output", str(output_path)],
                capture_output=True, text=True,
                timeout=args.timeout,
                cwd=REPO,
            )
            elapsed = time.time() - t0

            if output_path.exists():
                got = extract_verdict_from_bundle(output_path)
            else:
                got = "NO_BUNDLE"

            # Alias BENIGN → NOISE para comparación
            aliases = {"BENIGN": "NOISE"}
            got_norm = aliases.get(got, got)
            exp_norm = aliases.get(expected, expected)

            # Doctrina 2026-07-05 (Fase 2 §4, decisión de Anna, opción (a)):
            # MALICE donde la etiqueta dice INTENT es SOBRE-severidad, no
            # error de dirección — la escala define MALICE ⊃ INTENT +
            # ocultamiento y el ladder del motor no tiene escalón INTENT
            # (espacio {MALICE, SUSPICION, UNKNOWN, NOISE, ABSTAIN}). La
            # sub-severidad NO se acepta: INTENT→SUSPICION sigue siendo FAIL.
            over_severity = (exp_norm == "INTENT" and got_norm == "MALICE")

            ok = (got_norm == exp_norm) or (expected == "UNKNOWN") or over_severity

            status = f"{GRN}PASS{RST}" if ok else f"{RED}FAIL{RST}"
            print(f"  got={got:<12} {status}  ({elapsed:.1f}s)")

            results.append({
                "case_id": case_id,
                "expected": expected,
                "got": got,
                "pass": ok,
                "elapsed": round(elapsed, 1),
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
