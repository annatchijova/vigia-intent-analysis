#!/usr/bin/env python3
"""
scorer_gate.py — harness de exploración por ablación de fracturas sobre el motor
REAL (`_vigia_score`), con diff narrativo.

Origen: FOSSIL HUNT 2026-07-11 (docs/FOSSIL_HUNT_20260711.md). Materializa el
harness de scratchpad usado en la cacería para que sea reproducible por terceros.

SOLO LECTURA. No escribe en el repo, no modifica casos, no toca el motor: la
ablación se hace envolviendo `detect_fractures` en memoria (el equivalente a
tapar una fractura y volver a preguntar al scorer, sin tocar el composite).

Uso:
  # Baseline + fracturas de un caso
  python3 scripts/experiments/scorer_gate.py data/cases/VIGIA-FN-001.json

  # Ablación de un tipo (todas sus instancias) con diff narrativo
  python3 scripts/experiments/scorer_gate.py CASE.json \
      --filter TEMPORAL_CAUSALITY_VIOLATION --narrative-diff

  # Ablación de UNA instancia (índice del listado baseline)
  python3 scripts/experiments/scorer_gate.py CASE.json --instance 2 --narrative-diff

  # Barrido de corpus: casos cuyo veredicto cae al ablacionar un tipo
  python3 scripts/experiments/scorer_gate.py --corpus --filter FALSE_FLAG_PATTERN

Salida --json: objeto machine-readable con baseline, ablated y narrative_diff.
"""
from __future__ import annotations

import argparse
import copy
import json
import logging
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

logging.disable(logging.CRITICAL)

from vigia_scorer import _vigia_score            # noqa: E402
import vigia.tools.caie as _caie                 # noqa: E402

_ORIG_DETECT = _caie.CrossArtifactIncongruenceEngine.detect_fractures

# Estado del filtro de ablación (proceso-local, restaurado tras cada score()).
_ABLATE = {"types": None, "keys": None}

VERDICT_RANK = {"NOISE": 0, "UNKNOWN": 1, "ABSTAIN": 1, "SUSPICION": 2,
                "INTENT": 3, "MALICE": 4, "ERROR": -1}


def _fkey(f) -> str:
    return f"{f.fracture_type}||{f.artifact_a}||{f.artifact_b}"


def _patched_detect(self):
    frs = _ORIG_DETECT(self)
    t, k = _ABLATE["types"], _ABLATE["keys"]
    if t is None and k is None:
        return frs
    out = []
    for f in frs:
        if t and f.fracture_type in t:
            continue
        if k and _fkey(f) in k:
            continue
        out.append(f)
    return out


_caie.CrossArtifactIncongruenceEngine.detect_fractures = _patched_detect


def load_case(path: Path) -> dict:
    case = json.loads(path.read_text())
    if isinstance(case, list):
        if len(case) == 1 and isinstance(case[0], dict):
            return case[0]
        raise SystemExit(f"{path}: el JSON es una lista de {len(case)} elementos — "
                         "no es un caso individual")
    if not isinstance(case, dict):
        raise SystemExit(f"{path}: no es un objeto caso")
    return case


def score(case: dict, ablate_types=None, ablate_keys=None) -> dict:
    _ABLATE["types"] = set(ablate_types) if ablate_types else None
    _ABLATE["keys"] = set(ablate_keys) if ablate_keys else None
    try:
        return _vigia_score(copy.deepcopy(case))
    finally:
        _ABLATE["types"] = None
        _ABLATE["keys"] = None


def narrative_diff(base: dict, abl: dict) -> dict:
    """Qué cambia en la capa narrativa/sellable al remover la(s) fractura(s)."""
    base_frs = {(f.get("fracture_type"), str(f.get("artifact_a")), str(f.get("artifact_b"))): f
                for f in base.get("caie_fracture_details", [])}
    abl_frs = {(f.get("fracture_type"), str(f.get("artifact_a")), str(f.get("artifact_b")))
               for f in abl.get("caie_fracture_details", [])}
    removed = [v for k, v in base_frs.items() if k not in abl_frs]
    return {
        "verdict": {"before": base["verdict"], "after": abl["verdict"],
                    "drops": VERDICT_RANK.get(abl["verdict"], 0) < VERDICT_RANK.get(base["verdict"], 0)},
        "score": {"before": float(base["score"]), "after": float(abl["score"]),
                  "delta": round(float(abl["score"]) - float(base["score"]), 4)},
        "fracture_malice_boost": {"before": float(base.get("fracture_malice_boost", 0)),
                                  "after": float(abl.get("fracture_malice_boost", 0))},
        "reason": {"before": base.get("reason", ""), "after": abl.get("reason", "")},
        "quadripartite": {"before": base.get("quadripartite_state"),
                          "after": abl.get("quadripartite_state")},
        "removed_fracture_narratives": [
            {"type": f.get("fracture_type"),
             "severity": float(f.get("severity", 0) or 0),
             "artifact_a": str(f.get("artifact_a")),
             "artifact_b": str(f.get("artifact_b")),
             "sealed_interpretation": str(f.get("interpretation", ""))}
            for f in removed
        ],
    }


def print_case_report(case_path: Path, case: dict, args) -> None:
    base = score(case)
    frs = base.get("caie_fracture_details", [])
    print(f"CASE  : {case.get('case_id', case_path.stem)}  [{case_path}]")
    print(f"BASE  : verdict={base['verdict']}  score={float(base['score']):.4f}  "
          f"boost={float(base.get('fracture_malice_boost', 0)):.4f}  "
          f"expected={case.get('expected_verdict', '?')}")
    print(f"        reason: {base.get('reason', '')}")
    print(f"FRACTURAS ({len(frs)}):")
    for i, f in enumerate(frs):
        print(f"  [{i}] {f.get('fracture_type')} sev={f.get('severity')}")
        print(f"      a: {str(f.get('artifact_a'))[:110]}")
        print(f"      b: {str(f.get('artifact_b'))[:110]}")

    ablate_types = ablate_keys = None
    if args.instance is not None:
        if not (0 <= args.instance < len(frs)):
            raise SystemExit(f"--instance {args.instance} fuera de rango (0..{len(frs)-1})")
        f = frs[args.instance]
        ablate_keys = {f"{f.get('fracture_type')}||{f.get('artifact_a')}||{f.get('artifact_b')}"}
        label = f"instancia [{args.instance}] {f.get('fracture_type')}"
    elif args.filter:
        ablate_types = {t.strip() for t in args.filter.split(",") if t.strip()}
        label = f"tipo(s) {sorted(ablate_types)}"
    else:
        return

    abl = score(case, ablate_types=ablate_types, ablate_keys=ablate_keys)
    diff = narrative_diff(base, abl)

    if args.json:
        print(json.dumps({"case_id": case.get("case_id", case_path.stem),
                          "ablated": label, "diff": diff},
                         indent=1, ensure_ascii=False, default=str))
        return

    print(f"\nABLACION: {label}")
    v = diff["verdict"]
    arrow = "CAE" if v["drops"] else "se mantiene"
    print(f"  verdict : {v['before']} -> {v['after']}  ({arrow})")
    s = diff["score"]
    print(f"  score   : {s['before']:.4f} -> {s['after']:.4f}  (delta {s['delta']:+.4f})")
    b = diff["fracture_malice_boost"]
    print(f"  boost   : {b['before']:.4f} -> {b['after']:.4f}")
    if args.narrative_diff:
        print("\nDIFF NARRATIVO (lo que dejaria de sellarse):")
        print(f"  reason antes  : {diff['reason']['before']}")
        print(f"  reason despues: {diff['reason']['after']}")
        for r in diff["removed_fracture_narratives"]:
            print(f"\n  - {r['type']} (sev={r['severity']})")
            print(f"    a: {r['artifact_a'][:110]}")
            print(f"    b: {r['artifact_b'][:110]}")
            print(f"    interpretacion sellada que se removeria:")
            print(f"      {r['sealed_interpretation'][:400]}")
        qb, qa = diff["quadripartite"]["before"], diff["quadripartite"]["after"]
        if qb != qa:
            print(f"\n  quadripartite: {json.dumps(qb, default=str)[:160]}")
            print(f"             ->  {json.dumps(qa, default=str)[:160]}")


def corpus_sweep(args) -> None:
    from run_all_agent import CASES_DIRS, find_cases
    ablate_types = {t.strip() for t in args.filter.split(",")} if args.filter else None
    if not ablate_types:
        raise SystemExit("--corpus requiere --filter TIPO[,TIPO]")
    print(f"Barrido de corpus — ablacion de {sorted(ablate_types)}")
    hits = 0
    for p in find_cases(CASES_DIRS):
        try:
            case = load_case(p)
        except SystemExit:
            continue
        try:
            base = score(case)
        except Exception:
            continue
        if not any(f.get("fracture_type") in ablate_types
                   for f in base.get("caie_fracture_details", [])):
            continue
        abl = score(case, ablate_types=ablate_types)
        drops = VERDICT_RANK.get(abl["verdict"], 0) < VERDICT_RANK.get(base["verdict"], 0)
        flag = "DECIDE" if drops else "      "
        print(f"  {flag} {case.get('case_id', p.stem):45s} "
              f"{base['verdict']:9s}->{abl['verdict']:9s} "
              f"{float(base['score']):.3f}->{float(abl['score']):.3f}  "
              f"exp={case.get('expected_verdict', '?')}")
        hits += 1
    print(f"casos con la(s) fractura(s): {hits}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case", nargs="?", help="ruta a un caso JSON")
    ap.add_argument("--filter", help="tipo(s) de fractura a ablacionar, coma-separados")
    ap.add_argument("--instance", type=int, help="ablacionar solo la instancia N del baseline")
    ap.add_argument("--narrative-diff", action="store_true",
                    help="mostrar el diff de la capa narrativa sellable")
    ap.add_argument("--corpus", action="store_true",
                    help="barrer el corpus find_cases(CASES_DIRS) con --filter")
    ap.add_argument("--json", action="store_true", help="salida machine-readable")
    args = ap.parse_args()

    if args.corpus:
        corpus_sweep(args)
        return
    if not args.case:
        ap.error("falta la ruta del caso (o --corpus)")
    p = Path(args.case)
    if not p.is_absolute():
        p = REPO / p
    print_case_report(p, load_case(p), args)


if __name__ == "__main__":
    main()
