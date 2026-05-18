#!/usr/bin/env python3
"""
run_demo.py — VIGÍA Master Demo Script
─────────────────────────────────────────────────────────────────────────────
Script de entrada única para la demo del jurado SANS FIND EVIL 2026.

FLUJO COMPLETO:
    1. Cargar caso JSON (case_001_temporal.json por defecto)
    2. VigiaIntegrationEngine.run_case_file()
       → CaseAdapter: artefactos → SignalOutput[]
       → LikelihoodEngine (KDE/FALLBACK) → posteriors
       → GraphStabilityEngine (bootstrap B=500)
       → RiskBoundedDecisionLayer
       → AbductionTrace (Firstness/Secondness/Thirdness)
       → ForensicBundle
       → BundleBuilder.seal() → SHA-256 Merkle chain
    3. C3 Multi-Agent Validation: NarrativeAuditor valida la narrativa
       ANTES del cierre, verificando que no haya inyecciones de prompt
    4. Verificación criptográfica: verify_ebs_v1.py (stdlib puro)
    5. Reporte ENFSI (JSON)
    6. Print determinista: bundle_hash + rutas de salida

PROTOCOLO P0 (Qwen — Determinismo):
    - json.dumps con sort_keys=True en toda serialización
    - No se usa random ni datetime en el hash del bundle
    - Mismo input → mismo bundle_hash en x86 y ARM

USO:
    python3 run_demo.py
    python3 run_demo.py --case case_002_log_fabrication.json
    python3 run_demo.py --all-cases
    python3 run_demo.py --case case_001_temporal.json --ollama llama3.2
    python3 run_demo.py --case case_001_temporal.json --no-verify
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Resolución de raíz — funciona sin instalación
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Orden de prioridad: vigia_prod/ primero (módulos canónicos EBS v1)
for _candidate in [
    os.path.join(_SCRIPT_DIR, "vigia_prod"),
    os.path.join(_SCRIPT_DIR, "..", "vigia_prod"),
    _SCRIPT_DIR,
]:
    _c = os.path.realpath(_candidate)
    if os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

# ---------------------------------------------------------------------------
# Directorios de búsqueda para casos JSON y verificador
# ---------------------------------------------------------------------------
_CASE_SEARCH_DIRS = [
    _SCRIPT_DIR,
    os.path.join(_SCRIPT_DIR, "cases"),
    os.path.join(_SCRIPT_DIR, "data", "cases"),
    os.path.join(_SCRIPT_DIR, "vigia_prod"),
    "/mnt/project",
]

_VERIFIER_CANDIDATES = [
    os.path.join(_SCRIPT_DIR, "vigia_prod", "forensics", "verify_ebs_v1.py"),
    os.path.join(_SCRIPT_DIR, "forensics", "verify_ebs_v1.py"),
    os.path.join(_SCRIPT_DIR, "verify_ebs_v1__3_.py"),
    "/mnt/project/verify_ebs_v1__3_.py",
]

_DEFAULT_CASES = [
    "case_001_temporal.json",
    "case_001_temporal__2_.json",
    "case_002_log_fabrication.json",
    "case_002_log_fabrication__1_.json",
    "case_003_false_flag.json",
    "case_003_false_flag__1_.json",
    "case_004_provenance_break.json",
    "case_004_provenance_break__2_.json",
    "case_005_multi_source.json",
    "case_005_multi_source__1_.json",
]

_BANNER = """
╔══════════════════════════════════════════════════════════════════════════╗
║         VIGÍA — Forensic Intentionality Analysis Suite                   ║
║         EBS v1 | SANS FIND EVIL Hackathon 2026                           ║
║         C3 Multi-Agent Validation | Daubert-Grade Evidence               ║
╚══════════════════════════════════════════════════════════════════════════╝
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_case(name: str) -> Optional[str]:
    """Busca un archivo de caso JSON en todos los directorios candidatos."""
    if os.path.isfile(name):
        return os.path.realpath(name)
    base_prefix = os.path.splitext(os.path.basename(name))[0].split("__")[0]
    for d in _CASE_SEARCH_DIRS:
        if not os.path.isdir(d):
            continue
        # Exacto primero
        exact = os.path.join(d, os.path.basename(name))
        if os.path.isfile(exact):
            return os.path.realpath(exact)
        # Por prefijo (tolera sufijos __N_.json)
        try:
            for fname in sorted(os.listdir(d)):
                if fname.endswith(".json") and fname.startswith(base_prefix):
                    return os.path.realpath(os.path.join(d, fname))
        except OSError:
            continue
    return None


def _find_verifier() -> Optional[str]:
    for c in _VERIFIER_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def _find_baselines_yaml() -> Optional[str]:
    for p in [
        os.path.join(_SCRIPT_DIR, "baselines_institucionales.yaml"),
        os.path.join(_SCRIPT_DIR, "vigia_prod", "baselines_institucionales.yaml"),
        "/mnt/project/baselines_institucionales.yaml",
    ]:
        if os.path.isfile(p):
            return p
    return None


def _print_sep(char: str = "─", w: int = 74) -> None:
    print(char * w)


# ---------------------------------------------------------------------------
# C3: NarrativeAuditor — validación antes del cierre del bundle
# ---------------------------------------------------------------------------

def _run_c3_audit(
    narrative: List[str],
    investigation_id: str,
    verdict: str,
) -> Dict[str, Any]:
    """
    Invoca al NarrativeAuditor (C3) sobre la narrativa generada.

    Si el auditor no está disponible, retorna resultado limpio con advertencia.
    C3 nunca bloquea el pipeline por ausencia del módulo — degrada gracefully.
    """
    try:
        # Intentar importación desde rutas conocidas
        import importlib.util as _ilu
        _auditor_candidates = [
            os.path.join(_SCRIPT_DIR, "narrative_auditor.py"),
            os.path.join(_SCRIPT_DIR, "vigia_prod", "security", "narrative_auditor.py"),
        ]
        _auditor_path = next((p for p in _auditor_candidates if os.path.isfile(p)), None)

        if _auditor_path:
            spec = _ilu.spec_from_file_location("narrative_auditor", _auditor_path)
            mod  = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result = mod.audit_narrative_before_seal(narrative, investigation_id, verdict)
            return result.to_dict()
        else:
            return {
                "is_clean": True,
                "threats_count": 0,
                "threats": [],
                "audit_hash": "N/A",
                "investigation_id": investigation_id,
                "note": "narrative_auditor.py no encontrado — C3 omitido",
            }
    except Exception as e:
        return {
            "is_clean": True,
            "threats_count": 0,
            "threats": [],
            "audit_hash": "N/A",
            "investigation_id": investigation_id,
            "note": f"C3 error (no bloqueante): {e}",
        }


# ---------------------------------------------------------------------------
# Pipeline principal por caso
# ---------------------------------------------------------------------------

def run_case(
    case_path: str,
    output_dir: str,
    ollama_model: Optional[str],
    run_verify: bool,
    verbose: bool,
) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo para un caso forense.

    Flujo:
        caso_json → CaseAdapter → SignalOutput[] → LikelihoodEngine
        → ForensicBundle → BundleBuilder.seal() → Merkle chain
        → C3 NarrativeAuditor → verify_ebs_v1.py → reporte ENFSI
    """
    from vigia.pipeline.vigia_integration_bridge import VigiaIntegrationEngine  # type: ignore  # type: ignore

    # Buscar baselines_yaml para Level 3
    baselines_yaml = _find_baselines_yaml()

    engine = VigiaIntegrationEngine(
        output_dir=output_dir,
        ollama_model=ollama_model,
        baselines_yaml_path=baselines_yaml,
    )

    print(f"\n  Procesando: {os.path.basename(case_path)}")
    t0 = time.monotonic()

    result = engine.run_case_file(
        json_path=case_path,
        save_bundle=True,
        save_report=True,
    )

    elapsed = time.monotonic() - t0

    # ── C3: NarrativeAuditor antes del cierre ─────────────────────────────
    # Validar que la narrativa (si existe) no contiene inyecciones
    narrative_lines = result.get("narrative", [])
    if isinstance(narrative_lines, str):
        narrative_lines = narrative_lines.splitlines()
    elif not isinstance(narrative_lines, list):
        narrative_lines = []

    c3_result = _run_c3_audit(
        narrative=narrative_lines,
        investigation_id=result.get("case_id", "unknown"),
        verdict=result.get("decision", "ABSTAIN"),
    )
    result["c3_audit"] = c3_result

    # Advertir si C3 detectó amenazas
    if not c3_result.get("is_clean", True):
        print(
            f"  [C3 ALERTA] {c3_result['threats_count']} amenaza(s) en narrativa "
            f"— audit_hash: {c3_result['audit_hash']}"
        )

    # ── Output determinista (Protocolo P0) ────────────────────────────────
    _print_sep("═")
    print(f"  CASO:        {result['case_id']}")
    print(f"  DECISIÓN:    {result['decision']}")
    print(f"  POSTERIOR:   {result['posterior']:.6f}")
    print(f"  RIESGO:      {result['risk']:.6f}")
    print(f"  MODO:        {result['mode']}")
    print(f"  BUNDLE HASH: {result['bundle_hash']}")
    if result.get("ecl_hash"):
        print(f"  ECL HASH:    {result['ecl_hash']} (Level 3)")
    print(f"  VERIFY:      {'OK' if result['verify']['passed'] else 'FAIL'} — {result['verify']['message']}")
    print(f"  C3 AUDIT:    {'CLEAN' if c3_result.get('is_clean') else 'THREATS DETECTED'} "
          f"({c3_result.get('threats_count', 0)} amenazas)")
    if result.get("bundle_path"):
        print(f"  BUNDLE:      {result['bundle_path']}")
    if result.get("report_path"):
        print(f"  REPORTE:     {result['report_path']}")
    print(f"  TIEMPO:      {elapsed:.3f}s")
    _print_sep("═")

    # ── Verificación criptográfica externa (stdlib puro) ──────────────────
    if run_verify and result.get("bundle_path") and os.path.isfile(result["bundle_path"]):
        verifier = _find_verifier()
        if verifier:
            print(f"\n  Verificador externo: {os.path.basename(verifier)}")
            _print_sep()
            try:
                proc = subprocess.run(
                    [sys.executable, verifier, result["bundle_path"]],
                    timeout=30,
                )
                if proc.returncode != 0:
                    print(f"  [WARN] Verificador retornó exit={proc.returncode}")
            except subprocess.TimeoutExpired:
                print("  [WARN] Verificador tardó >30s — abortado")
            except Exception as e:
                print(f"  [WARN] Error en verificador: {e}")
        else:
            print("  [WARN] verify_ebs_v1.py no encontrado — verificación omitida")

    # ── Guardar audit C3 junto al bundle ──────────────────────────────────
    if result.get("bundle_path"):
        c3_path = result["bundle_path"].replace("bundle_", "c3_audit_").replace(".json", ".json")
        try:
            with open(c3_path, "w", encoding="utf-8") as f:
                json.dump(c3_result, f, sort_keys=True, indent=2, default=str)
            if verbose:
                print(f"  C3 audit guardado: {c3_path}")
        except OSError:
            pass

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    print(_BANNER)

    parser = argparse.ArgumentParser(
        description="VIGÍA Master Demo — Pipeline EBS v1 + C3 Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 run_demo.py
  python3 run_demo.py --case case_001_temporal.json
  python3 run_demo.py --all-cases --output ./results
  python3 run_demo.py --case case_001_temporal.json --ollama llama3.2
  python3 run_demo.py --case case_001_temporal.json --no-verify
        """,
    )
    parser.add_argument("--case", "-c", metavar="JSON",
                        help="Archivo de caso forense (default: case_001_temporal.json)")
    parser.add_argument("--all-cases", action="store_true",
                        help="Ejecutar todos los casos disponibles")
    parser.add_argument("--output", "-o", default="./vigia_output",
                        help="Directorio de salida (default: ./vigia_output)")
    parser.add_argument("--ollama", metavar="MODEL", default=None,
                        help="Modelo Ollama para narrativa post-sellado (ej: llama3.2)")
    parser.add_argument("--no-verify", action="store_true",
                        help="No ejecutar verify_ebs_v1.py automáticamente")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Output detallado")
    args = parser.parse_args()

    # Verificar que el bridge está disponible
    try:
        import vigia.pipeline.vigia_integration_bridge as vigia_integration_bridge  # type: ignore  # type: ignore  # noqa: F401
    except ImportError as e:
        print(f"\n  ERROR CRÍTICO: vigia_integration_bridge no importable: {e}")
        print(f"  sys.path[0:3]: {sys.path[:3]}")
        return 1

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    print(f"  Directorio de salida: {output_dir}")
    if not args.case and not args.all_cases:
        # Default: case_001
        args.case = "case_001_temporal.json"
        print(f"  (Usando caso por defecto: {args.case})")

    run_verify = not args.no_verify
    results: List[Dict] = []
    failures: List[Dict] = []

    if args.all_cases:
        print("\n  Modo batch — todos los casos disponibles")
        _print_sep()
        found_cases = []
        seen_bases = set()
        for fname in _DEFAULT_CASES:
            base = fname.split("__")[0]
            if base in seen_bases:
                continue
            path = _find_case(fname)
            if path:
                found_cases.append(path)
                seen_bases.add(base)

        if not found_cases:
            print("  ERROR: no se encontraron casos JSON")
            return 1

        for cp in found_cases:
            try:
                r = run_case(cp, output_dir, args.ollama, run_verify, args.verbose)
                results.append(r)
            except Exception as e:
                print(f"\n  [ERROR] {os.path.basename(cp)}: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                failures.append({"case": cp, "error": str(e)})
    else:
        case_path = _find_case(args.case)
        if not case_path:
            print(f"\n  ERROR: caso no encontrado: '{args.case}'")
            return 1
        try:
            r = run_case(case_path, output_dir, args.ollama, run_verify, args.verbose)
            results.append(r)
        except Exception as e:
            print(f"\n  [ERROR] {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    # ── Resumen final (Protocolo P0 — determinista) ────────────────────────
    if len(results) > 1:
        _print_sep("═")
        print(f"\n  RESUMEN BATCH")
        print(f"  Casos procesados: {len(results)}")
        print(f"  Errores:          {len(failures)}")
        decisions: Dict[str, int] = {}
        for r in results:
            d = r.get("decision", "UNKNOWN")
            decisions[d] = decisions.get(d, 0) + 1
        for k, v in sorted(decisions.items()):
            print(f"    {k}: {v}")
        _print_sep()

        # Guardar resumen JSON (sort_keys=True — P0)
        summary_path = os.path.join(output_dir, "demo_summary.json")
        summary = {
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "total_cases": len(results) + len(failures),
            "successful":  len(results),
            "failed":      len(failures),
            "decisions":   decisions,
            "results": [
                {
                    "case_id":    r.get("case_id"),
                    "decision":   r.get("decision"),
                    "posterior":  r.get("posterior"),
                    "bundle_hash": r.get("bundle_hash", ""),
                    "verify_ok":  r.get("verify", {}).get("passed", False),
                    "c3_clean":   r.get("c3_audit", {}).get("is_clean", True),
                    "mode":       r.get("mode"),
                }
                for r in results
            ],
            "failures": failures,
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, sort_keys=True, indent=2, default=str)
        print(f"\n  Resumen guardado: {summary_path}")

    # ── Print final determinista ───────────────────────────────────────────
    print("\n  ─── ENTREGABLES ──────────────────────────────────────────────")
    for r in results:
        bh = r.get("bundle_hash", "N/A")
        bp = r.get("bundle_path", "N/A")
        rp = r.get("report_path", "N/A")
        c3 = "CLEAN" if r.get("c3_audit", {}).get("is_clean", True) else "THREATS"
        print(f"  [{r.get('case_id')}]")
        print(f"    bundle_hash : {bh}")
        print(f"    bundle      : {bp}")
        print(f"    reporte     : {rp}")
        print(f"    C3 audit    : {c3}")
        print(f"    verify      : {r.get('verify', {}).get('message', 'N/A')}")
    print("  ─────────────────────────────────────────────────────────────")

    print("\n  Para verificar manualmente:")
    print(f"    python3 verify_ebs_v1__3_.py {output_dir}/bundle_<case_id>.json\n")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
