#!/usr/bin/env python3
"""
Migración del corpus sintético — inyección de señales computadas (opción 2).

Para cada caso bajo data/cases/**/*.json SIN campo `signals` ni `evidence`:
  - si existe su bundle en results/agent_batch/{case_id}_agent_bundle.json,
    extrae `pipeline_results.signals` y lo inyecta en el JSON del caso como
    campo `signals`, más un campo `_migration_note` con fecha y fuente;
  - si NO existe bundle, lo etiqueta `corpus_type: "narrative_legacy"` para
    distinguirlo en el comparador — con una excepción: los fixtures de
    data/cases/red-team/ NO se etiquetan (son fixtures EBS red-team de
    2026-07-04 deliberadamente fuera del universo del runner, no casos
    narrativos legacy; etiquetarlos introduciría metadata falsa).

Exclusiones duras (nunca se modifican):
  - corpus real: VIGIA-REAL-*, VIGIA-SRL-*, *ROCBA*;
  - índices y agregados (SKIP_STEMS de run_all_agent: _index, dataset,
    calibration, vigia_cases_canonical, …);
  - archivos que ya tienen `signals` o `evidence`;
  - JSONs que no parsean o no son dict (se reportan).

Seguridad:
  - DRY-RUN por default: imprime el plan completo y no toca nada.
  - --apply ejecuta; ANTES de modificar cada archivo escribe un backup que
    preserva la ruta relativa bajo --backup-dir. El respaldo durable es el
    tag de git creado antes de la corrida (protocolo de la sesión).

Las señales del bundle conservan su codificación canónica
({"__fraction__": true, "num": N, "den": D}) — son datos derivados del
motor determinista, se inyectan tal cual. La inyección es INERTE para el
scoring: ni `_vigia_score` ni `_analyze_ebs_json` leen `signals` a nivel de
caso (leen `artifacts`); el gate con run_all_agent.py lo verifica.

Uso:
    python3 scripts/migrate_corpus_signals.py                 # dry-run
    python3 scripts/migrate_corpus_signals.py --apply \
        --backup-dir /ruta/backups
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from run_all_agent import SKIP_STEMS  # noqa: E402

CASES_ROOT = REPO / "data" / "cases"
BUNDLES_DIR = REPO / "results" / "agent_batch"
MIGRATION_DATE = "2026-07-06"

REAL_PREFIXES = ("VIGIA-REAL-", "VIGIA-SRL-")
REDTEAM_DIR = CASES_ROOT / "red-team"


def is_skipped_stem(stem: str) -> bool:
    s = stem.lower()
    return s in SKIP_STEMS or any(k in s for k in SKIP_STEMS)


def is_real_corpus(stem: str) -> bool:
    return stem.startswith(REAL_PREFIXES) or "ROCBA" in stem.upper()


def classify(path: Path, bundles: dict[str, Path]):
    """→ (acción, detalle) con acción ∈ {migrate, tag_legacy, skip_*}."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return "skip_unparseable", f"{type(e).__name__}"
    if not isinstance(data, dict):
        return "skip_not_dict", type(data).__name__
    if "signals" in data or "evidence" in data:
        return "skip_has_signals", ""
    if is_skipped_stem(path.stem):
        return "skip_aggregate", ""
    if is_real_corpus(path.stem):
        return "skip_real_corpus", ""
    if path.stem in bundles:
        return "migrate", str(bundles[path.stem].relative_to(REPO))
    if REDTEAM_DIR in path.parents:
        return "skip_redteam_fixture", "sin bundle por diseño (fuera del runner)"
    return "tag_legacy", "sin bundle"


def extract_signals(bundle_path: Path):
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    pr = bundle.get("pipeline_results")
    signals = pr.get("signals") if isinstance(pr, dict) else None
    if signals is None:
        signals = bundle.get("signals")
    if not isinstance(signals, list):
        raise ValueError(f"bundle sin pipeline_results.signals: {bundle_path.name}")
    return signals


def apply_migrate(path: Path, bundle_rel: str, backup_dir: Path) -> int:
    signals = extract_signals(REPO / bundle_rel)
    data = json.loads(path.read_text(encoding="utf-8"))
    backup = backup_dir / path.relative_to(REPO)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    data["signals"] = signals
    data["_migration_note"] = {
        "date": MIGRATION_DATE,
        "source": bundle_rel,
        "method": ("señales computadas por el pipeline determinista (modo motor, "
                   "B-075/B-076) extraídas de pipeline_results.signals del bundle "
                   "sellado; codificación Fraction canónica preservada"),
        "n_signals": len(signals),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return len(signals)


def apply_tag_legacy(path: Path, backup_dir: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    backup = backup_dir / path.relative_to(REPO)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    data["corpus_type"] = "narrative_legacy"
    data["_migration_note"] = {
        "date": MIGRATION_DATE,
        "source": None,
        "method": "sin bundle en results/agent_batch — marcado narrative_legacy "
                  "para distinguirlo en el comparador",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="ejecutar (default: dry-run, no toca nada)")
    ap.add_argument("--backup-dir", type=Path, default=None,
                    help="directorio de backups (obligatorio con --apply)")
    args = ap.parse_args()

    if args.apply and not args.backup_dir:
        ap.error("--apply requiere --backup-dir")

    bundles = {p.stem.removesuffix("_agent_bundle"): p
               for p in BUNDLES_DIR.glob("*_agent_bundle.json")}

    plan: dict[str, list] = {}
    for path in sorted(CASES_ROOT.rglob("*.json")):
        action, detail = classify(path, bundles)
        plan.setdefault(action, []).append((path, detail))

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== migrate_corpus_signals — {mode} ===")
    print(f"bundles disponibles: {len(bundles)}")
    for action in ("migrate", "tag_legacy", "skip_redteam_fixture",
                   "skip_real_corpus", "skip_aggregate", "skip_has_signals",
                   "skip_not_dict", "skip_unparseable"):
        items = plan.get(action, [])
        print(f"\n[{action}] {len(items)}")
        show = items if action in ("tag_legacy", "skip_redteam_fixture",
                                   "skip_not_dict", "skip_unparseable") \
            else items[:5]
        for path, detail in show:
            print(f"    {path.relative_to(REPO)}  {detail}")
        if len(items) > len(show):
            print(f"    … y {len(items) - len(show)} más")

    if not args.apply:
        print("\nDry-run: no se modificó nada. Ejecutar con --apply --backup-dir …")
        return

    backup_dir = args.backup_dir.resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    n_sig_total = 0
    for path, detail in plan.get("migrate", []):
        n_sig_total += apply_migrate(path, detail, backup_dir)
    for path, _ in plan.get("tag_legacy", []):
        apply_tag_legacy(path, backup_dir)

    # Verificación post-escritura: todo JSON modificado debe re-parsear.
    bad = []
    for path, _ in plan.get("migrate", []) + plan.get("tag_legacy", []):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(path)
    print(f"\nAPPLY: {len(plan.get('migrate', []))} migrados "
          f"({n_sig_total} señales), {len(plan.get('tag_legacy', []))} "
          f"etiquetados narrative_legacy, backups en {backup_dir}")
    if bad:
        print(f"ERROR: {len(bad)} archivos no re-parsean: {bad}")
        sys.exit(1)
    print("Verificación JSON: OK")


if __name__ == "__main__":
    main()
