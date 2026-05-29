#!/usr/bin/env python3
"""
validate_case.py — Validador de schema EBS v1 para VIGÍA

Corre ANTES del pipeline. Detecta campos faltantes o mal ubicados
que causan NOISE/trust degradado sin mensaje claro.

Uso:
    python3 validate_case.py <caso.json>
    python3 validate_case.py <caso.json> --autofix
"""
import json
import sys
import hashlib
from pathlib import Path

# Campos críticos — su ausencia en metadata causa NOISE silencioso
ACQ_CRITICAL = ["acquisition_tool", "acquisition_hash", "acquisition_timestamp"]
ACQ_RECOMMENDED = ["write_blocker_used", "examiner_id"]
ARTIFACT_REQUIRED = ["artifact_id", "evidence_type", "source_tool",
                     "description", "raw_score", "prior_trust", "timestamp"]
CASE_REQUIRED = ["case_id", "case_name", "description",
                 "expected_verdict", "schema_version", "artifacts"]

ERRORS = []
WARNINGS = []
FIXES = []

def err(msg): ERRORS.append(f"  [ERROR] {msg}")
def warn(msg): WARNINGS.append(f"  [WARN]  {msg}")
def fix(msg): FIXES.append(f"  [FIX]   {msg}")


def validate_case(path: str, autofix: bool = False) -> bool:
    p = Path(path)
    if not p.exists():
        print(f"FATAL: archivo no encontrado: {path}")
        return False

    try:
        case = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"FATAL: JSON inválido — {e}")
        return False

    print(f"\nValidando: {path}")
    print("=" * 60)

    # 1. Campos obligatorios del caso
    for field in CASE_REQUIRED:
        if field not in case:
            err(f"Required field missing at case root: '{field}'")

    artifacts = case.get("artifacts", [])
    if not artifacts:
        err("'artifacts' está vacío — el pipeline no tiene señales para analizar")
        _print_results()
        return False

    # 2. Validar cada artefacto
    modified = False
    for art in artifacts:
        aid = art.get("artifact_id", "?")

        # Campos obligatorios del artefacto
        for field in ARTIFACT_REQUIRED:
            if field not in art:
                err(f"{aid}: campo obligatorio ausente: '{field}'")

        # provenance_chain
        chain = art.get("provenance_chain")
        if not chain:
            err(f"{aid}: 'provenance_chain' vacío o ausente — "
                f"causes epc_factor=0.1 → trust collapsed to 10% → NOISE likely")
            if autofix:
                art["provenance_chain"] = [
                    "Adquisición forense",
                    "Análisis con herramienta SIFT/Volatility",
                    "VIGÍA EBS v1 converter"
                ]
                fix(f"{aid}: provenance_chain placeholder agregado — ACTUALIZAR con cadena real")
                modified = True

        # metadata
        meta = art.get("metadata")
        if not isinstance(meta, dict):
            err(f"{aid}: 'metadata' ausente o no es dict — "
                f"acquisition_assurance=0 → trust degradado en cascada")
            if autofix:
                art["metadata"] = {}
                meta = art["metadata"]
                fix(f"{aid}: empty metadata dict created")
                modified = True

        if isinstance(meta, dict):
            # Skip acquisition-context-only artifacts
            _is_ctx = (float(art.get("prior_trust",1))==0.0 and float(art.get("raw_score",1))==0.0) or \
                       art.get("role")=="ACQUISITION_CONTEXT_NOT_ATTACK_EVIDENCE"
            # Campos críticos dentro de metadata
            for field in ACQ_CRITICAL:
                if _is_ctx:
                    break
                if not meta.get(field):
                    # Ver si está en top-level (error de ubicación común)
                    top_val = art.get(field)
                    if top_val:
                        err(f"{aid}: '{field}' está en top-level pero NO en metadata — "
                            f"CAIE lee de metadata, causa acquisition_assurance=0")
                        if autofix:
                            meta[field] = top_val
                            fix(f"{aid}: '{field}' copied from top-level to metadata")
                            modified = True
                    else:
                        err(f"{aid}: '{field}' ausente en metadata — "
                            f"acquisition_assurance=0 → NOISE posible")

            for field in ACQ_RECOMMENDED:
                if not meta.get(field) and meta.get(field) is not False:
                    warn(f"{aid}: '{field}' ausente en metadata — "
                         f"degrada base_trust en 0.1")
                    if autofix and field == "write_blocker_used":
                        meta[field] = False
                        fix(f"{aid}: write_blocker_used=False (live acquisition default)")
                        modified = True

        # raw_score fuera de rango
        rs = art.get("raw_score", -1)
        if not (0.0 <= float(rs) <= 1.0):
            err(f"{aid}: raw_score={rs} fuera de rango [0.0, 1.0]")

        pt = art.get("prior_trust", -1)
        if not (0.0 <= float(pt) <= 1.0):
            err(f"{aid}: prior_trust={pt} fuera de rango [0.0, 1.0]")

    _print_results()

    if modified and autofix:
        backup = p.with_suffix(".json.bak_validate")
        backup.write_text(p.read_text())
        p.write_text(json.dumps(case, indent=2, ensure_ascii=False))
        print(f"\n[AUTOFIX] Backup saved to: {backup.name}")
        print(f"[AUTOFIX] Case corrected in: {path}")
        print("[AUTOFIX] WARNING: review placeholder fields before running the pipeline")

    ok = len(ERRORS) == 0
    print(f"\n{'PASS' if ok else 'FAIL'} — {len(ERRORS)} error(es), {len(WARNINGS)} warning(s)")
    if not ok:
        print("Pipeline may produce NOISE or degraded trust with these errors.")
    return ok


def _print_results():
    if ERRORS:
        print(f"\nCritical errors ({len(ERRORS)}):")
        for e in ERRORS: print(e)
    if WARNINGS:
        print(f"\nWarnings ({len(WARNINGS)}):")
        for w in WARNINGS: print(w)
    if FIXES:
        print(f"\nFixes applied ({len(FIXES)}):")
        for f in FIXES: print(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 validate_case.py <caso.json> [--autofix]")
        sys.exit(1)

    autofix = "--autofix" in sys.argv
    path = next(a for a in sys.argv[1:] if not a.startswith("--"))
    ok = validate_case(path, autofix=autofix)
    sys.exit(0 if ok else 1)
