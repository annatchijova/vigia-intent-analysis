#!/usr/bin/env python3
"""
recalibrate_cases.py
====================
Actualiza expected_verdict en los JSONs de casos para reflejar el
comportamiento actual del scorer (EBS v1 + todos los patches).

SOLO actualiza casos que NO están en KNOWN_LIMITATIONS.
Los casos con limitaciones documentadas se reportan pero no se tocan.

Uso:
    python3 recalibrate_cases.py --dry-run        # ver qué cambiaría
    python3 recalibrate_cases.py --apply          # aplicar cambios
    python3 recalibrate_cases.py --apply --cases-dir data/cases/

SANS FIND EVIL Hackathon 2026
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Casos con limitaciones documentadas — NO recalibrar
# Fuente: known_limitations.md (versiones ES y EN)
KNOWN_LIMITATIONS = {
    "VIGIA_BREAK_001_SILENT_INCONSISTENCY",  # L-006: decisión de diseño
    "VIGIA_BREAK_002_VALID_BENIGN",          # L-005: contexto organizacional
    "VIGIA_BREAK_004_SIGNAL_DROWNING",       # L-002: señal ahogada en ruido
    "VIGIA_BREAK_005_AUTHORIZED",            # L-005: actividad autorizada
    "VIGIA_BREAK_006_PERFECT_ATTACK",        # L-001: ataque perfecto sin anomalías
    "VIGIA_BREAK_007_MISSING_LOGS",          # L-003: ausencia de logs
    "VIGIA_BREAK_009_PROMPT_POISON",         # L-004: narrativa engañosa
}

# Mapeo de score a veredicto (mismo que vigia_scorer.py)
def _score_to_verdict(score: float, hard_temporal: bool,
                      provenance_collapsed: bool,
                      mean_effective: float, fractures: int) -> str:
    if hard_temporal:
        return "MALICE"
    if provenance_collapsed:
        return "NOISE"
    if mean_effective < 0.15 and fractures > 0:
        return "SUSPICION"
    if score > 0.75:
        return "MALICE"
    if score > 0.55:
        return "SUSPICION"
    if score > 0.25:
        return "UNKNOWN"
    return "NOISE"


def main():
    parser = argparse.ArgumentParser(description="Recalibrar expected_verdict en casos VIGÍA")
    parser.add_argument("--cases-dir", default="cases", help="Directorio con JSON de casos")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Solo mostrar cambios sin aplicar")
    mode.add_argument("--apply",   action="store_true", help="Aplicar cambios a los JSONs")
    args = parser.parse_args()

    cases_dir = Path(args.cases_dir)
    if not cases_dir.exists():
        print(f"ERROR: directorio no encontrado: {cases_dir}")
        sys.exit(1)

    # Importar scorer
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from vigia_scorer import _vigia_score, _normalize_case
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent / "vigia" / "core"))
        from vigia_scorer import _vigia_score, _normalize_case

    case_files = sorted(cases_dir.glob("*.json"))
    if not case_files:
        print(f"No se encontraron casos en {cases_dir}")
        sys.exit(0)

    updated   = []
    skipped   = []
    unchanged = []
    errors    = []

    print(f"\n{'='*70}")
    print(f"  VIGÍA — Recalibración de expected_verdicts")
    print(f"  Modo: {'DRY RUN (sin cambios)' if args.dry_run else 'APPLY (escribe JSONs)'}")
    print(f"  Casos: {len(case_files)}")
    print(f"{'='*70}\n")

    for cf in case_files:
        case_id = cf.stem
        try:
            with open(cf, encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            errors.append((case_id, str(e)))
            continue

        # Casos con limitaciones documentadas — skip
        if case_id in KNOWN_LIMITATIONS:
            old_exp = raw.get("expected_verdict", "?")
            skipped.append((case_id, old_exp))
            print(f"  [SKIP - LIMITACIÓN] {case_id:50s} expected={old_exp}")
            continue

        try:
            case_norm = _normalize_case(dict(raw))
            result    = _vigia_score(case_norm)
        except Exception as e:
            errors.append((case_id, str(e)))
            print(f"  [ERROR] {case_id}: {e}")
            continue

        new_verdict = result["verdict"]
        old_verdict = raw.get("expected_verdict", "NOT_SET")
        score       = result["score"]
        source      = result.get("caie_fractures_source", "?")
        fractures   = result.get("caie_fractures", 0)

        if old_verdict == new_verdict:
            unchanged.append(case_id)
            print(f"  [OK]    {case_id:50s} {old_verdict} (score={score:.4f})")
            continue

        # Cambio detectado
        print(f"  [UPD]   {case_id:50s} {old_verdict} → {new_verdict} "
              f"(score={score:.4f}, caie={source}/{fractures}f)")
        updated.append((case_id, old_verdict, new_verdict, score))

        if args.apply:
            raw["expected_verdict"] = new_verdict
            raw["_recalibrated"] = {
                "previous_expected": old_verdict,
                "new_expected":      new_verdict,
                "score":             score,
                "caie_source":       source,
                "caie_fractures":    fractures,
                "recalibrated_by":   "recalibrate_cases.py EBS v1 2026-05-19",
            }
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False, sort_keys=False)
                f.write("\n")

    # Resumen
    print(f"\n{'='*70}")
    print(f"  RESUMEN")
    print(f"{'='*70}")
    print(f"  Total casos      : {len(case_files)}")
    print(f"  Sin cambio       : {len(unchanged)}")
    print(f"  Actualizados     : {len(updated)}")
    print(f"  Saltados (límit.): {len(skipped)}")
    print(f"  Errores          : {len(errors)}")

    if updated:
        print(f"\n  Cambios detectados:")
        for cid, old, new, sc in updated:
            print(f"    {cid}: {old} → {new} (score={sc:.4f})")

    if errors:
        print(f"\n  Errores:")
        for cid, err in errors:
            print(f"    {cid}: {err}")

    if args.dry_run and updated:
        print(f"\n  Para aplicar: python3 recalibrate_cases.py --apply")

    print()


if __name__ == "__main__":
    main()
