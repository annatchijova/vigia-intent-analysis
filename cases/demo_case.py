#!/usr/bin/env python3
"""
demo_case.py — VIGÍA Forensic Suite: Demo End-to-End
─────────────────────────────────────────────────────────────────────────────
Script de demostración para el jurado SANS FIND EVIL Hackathon 2026.

USO:
    python3 demo_case.py --input case_001_temporal.json
    python3 demo_case.py --input case_001_temporal.json --output ./output
    python3 demo_case.py --input case_001_temporal.json --ollama llama3.2
    python3 demo_case.py --all-cases

PRODUCE:
    output/bundle_<case_id>.json    → verificable con verify_ebs_v1.py
    output/report_<case_id>.json    → reporte ENFSI con AbductionTrace

VERIFICACIÓN INMEDIATA:
    python3 verify_ebs_v1__3_.py output/bundle_<case_id>.json

REQUISITOS:
    - Python 3.9+
    - Sin instalación de paquete necesaria (stdlib + dependencias opcionales)
    - Para narrativa: Ollama corriendo en localhost:11434

ARQUITECTURA (Carnegie dual-use):
    Las técnicas de persuasión de Carnegie (credibilidad, consistencia,
    urgencia de señal) están INVERTIDAS como detectores DFIR:
        - Credibilidad inflada → z-score SDA elevado
        - Inconsistencia temporal → drift_score alto → REJECT
        - Patrones algorítmicos → GCI/DGPI positivo → AbductionTrace

NIVEL DE CONFORMIDAD EBS v1:
    Level 2: Criptográficamente válido (bundle_hash + graph_hash)
    Level 3: Con ecl_hash (baselines_institucionales.yaml presente)
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

# Candidatos de raíz del paquete EBS v1 — canónico primero
_VIGIA_PROD_CANDIDATES = [
    os.path.join(_SCRIPT_DIR, "vigia_prod"),
    os.path.join(_SCRIPT_DIR, "..", "vigia_prod"),
    _SCRIPT_DIR,
]
for _vp in _VIGIA_PROD_CANDIDATES:
    _vp_real = os.path.realpath(_vp)
    if os.path.isdir(_vp_real) and _vp_real not in sys.path:
        sys.path.insert(0, _vp_real)

if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# Directorios donde buscar archivos de caso JSON
_CASE_SEARCH_DIRS = [
    _SCRIPT_DIR,
    os.path.join(_SCRIPT_DIR, "vigia_prod"),
    os.path.join(_SCRIPT_DIR, "cases"),
    "/mnt/project",  # entorno de desarrollo VIGÍA
]

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
_BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║          VIGÍA — Forensic Intentionality Analysis Suite          ║
║          EBS v1 | SANS FIND EVIL Hackathon 2026                  ║
║          Target: SIFT Integration | Daubert-Grade Evidence       ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ---------------------------------------------------------------------------
# Casos disponibles por defecto
# ---------------------------------------------------------------------------
_DEFAULT_CASES = [
    "case_001_temporal__2_.json",
    "case_002_log_fabrication__1_.json",
    "case_003_false_flag__1_.json",
    "case_004_provenance_break__2_.json",
    "case_005_multi_source__1_.json",
]


def _find_case_file(name: str) -> Optional[str]:
    """
    Busca el archivo de caso en todos los directorios candidatos.
    Acepta nombre exacto o nombre base sin sufijo numérico (__N_).
    """
    # Candidato exacto (path absoluto o relativo al cwd)
    if os.path.isfile(name):
        return os.path.realpath(name)

    # Buscar en todos los directorios conocidos — exacto primero
    base = os.path.splitext(os.path.basename(name))[0]
    base_prefix = base.split("__")[0]  # "case_001_temporal" de "case_001_temporal__2_"

    for search_dir in _CASE_SEARCH_DIRS:
        if not os.path.isdir(search_dir):
            continue
        # Nombre exacto
        candidate = os.path.join(search_dir, os.path.basename(name))
        if os.path.isfile(candidate):
            return os.path.realpath(candidate)
        # Búsqueda por prefijo (tolerancia a sufijos __N_.json)
        try:
            for fname in sorted(os.listdir(search_dir)):
                if fname.endswith(".json") and fname.startswith(base_prefix):
                    full = os.path.join(search_dir, fname)
                    if os.path.isfile(full):
                        return os.path.realpath(full)
        except OSError:
            continue
    return None


def _print_separator(char: str = "─", width: int = 68) -> None:
    print(char * width)


def _print_result(result: Dict[str, Any], verbose: bool = False) -> None:
    """Imprime el resultado del caso de forma legible para el jurado."""
    _print_separator("═")
    print(f"  CASO:      {result['case_id']}")
    print(f"  DECISIÓN:  {result['decision']}")
    print(f"  POSTERIOR: {result['posterior']:.4f}")
    print(f"  RIESGO:    {result['risk']:.4f}")
    print(f"  MODO:      {result['mode']}")
    print(f"  HASH:      {result['bundle_hash'][:32]}…")
    if result.get("ecl_hash"):
        print(f"  ECL HASH:  {result['ecl_hash']} (Level 3)")
    if result.get("bundle_path"):
        print(f"  BUNDLE:    {result['bundle_path']}")
    if result.get("report_path"):
        print(f"  REPORTE:   {result['report_path']}")
    print(f"  VERIFY:    {'OK' if result['verify']['passed'] else 'FAIL'} — {result['verify']['message']}")
    if result.get("warnings"):
        print(f"  WARNINGS:  {len(result['warnings'])}")
        if verbose:
            for w in result["warnings"]:
                print(f"             {w}")
    if result.get("narrative"):
        _print_separator()
        print("  NARRATIVA OLLAMA:")
        print(f"  {result['narrative'][:500]}")
    _print_separator("═")


def _run_verifier(bundle_path: str) -> int:
    """
    Ejecuta verify_ebs_v1.py sobre el bundle producido.
    Retorna el exit code del verificador.
    """
    verifier_candidates = [
        os.path.join(_SCRIPT_DIR, "verify_ebs_v1__3_.py"),
        os.path.join(_SCRIPT_DIR, "forensics", "verify_ebs_v1.py"),
        "verify_ebs_v1__3_.py",
        "/mnt/project/verify_ebs_v1__3_.py",
        os.path.join(_SCRIPT_DIR, "vigia_prod", "forensics", "verify_ebs_v1.py"),
    ]
    verifier = None
    for c in verifier_candidates:
        if os.path.isfile(c):
            verifier = c
            break

    if not verifier:
        print("  [WARN] verify_ebs_v1.py no encontrado — verificación automática omitida")
        return 0

    print(f"\n  Ejecutando verificador externo: {verifier}")
    _print_separator()
    try:
        proc = subprocess.run(
            [sys.executable, verifier, bundle_path],
            capture_output=False,
            timeout=30,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        print("  [WARN] Verificador tardó más de 30s — abortado")
        return 1
    except Exception as e:
        print(f"  [WARN] Error ejecutando verificador: {e}")
        return 1


def run_single_case(
    case_path: str,
    output_dir: str,
    ollama_model: Optional[str],
    run_verify: bool,
    verbose: bool,
) -> Dict[str, Any]:
    """
    Corre el pipeline completo para un caso.
    Retorna el resultado del VigiaIntegrationEngine.
    """
    from vigia_integration_bridge import VigiaIntegrationEngine  # type: ignore
    _bl_candidates = [
        os.path.join(_SCRIPT_DIR, "baselines_institucionales.yaml"),
        os.path.join(_SCRIPT_DIR, "vigia_prod", "baselines_institucionales.yaml"),
        "/mnt/project/baselines_institucionales.yaml",
    ]
    _baselines_path = next((p for p in _bl_candidates if os.path.isfile(p)), None)


    engine = VigiaIntegrationEngine(
        output_dir=output_dir,
        ollama_model=ollama_model,
        baselines_yaml_path=_baselines_path,
    )

    print(f"\n  Procesando: {case_path}")
    t0 = time.monotonic()
    result = engine.run_case_file(
        json_path=case_path,
        save_bundle=True,
        save_report=True,
    )
    elapsed = time.monotonic() - t0
    print(f"  Tiempo: {elapsed:.2f}s")

    _print_result(result, verbose=verbose)

    # Verificación externa automática
    if run_verify and result.get("bundle_path") and os.path.isfile(result["bundle_path"]):
        verify_exit = _run_verifier(result["bundle_path"])
        if verify_exit != 0:
            print(f"  [WARN] Verificador externo retornó exit={verify_exit}")

    return result


def main() -> int:
    print(_BANNER)

    parser = argparse.ArgumentParser(
        description="VIGÍA Demo — Pipeline forense end-to-end",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 demo_case.py --input case_001_temporal__2_.json
  python3 demo_case.py --input case_001_temporal__2_.json --ollama llama3.2
  python3 demo_case.py --all-cases --output ./results
  python3 demo_case.py --input case_001_temporal__2_.json --no-verify
        """,
    )
    parser.add_argument(
        "--input", "-i",
        metavar="CASE_JSON",
        help="Archivo JSON del caso forense",
    )
    parser.add_argument(
        "--all-cases",
        action="store_true",
        help="Ejecutar todos los casos de test disponibles",
    )
    parser.add_argument(
        "--output", "-o",
        default="./vigia_output",
        metavar="DIR",
        help="Directorio de salida (default: ./vigia_output)",
    )
    parser.add_argument(
        "--ollama",
        metavar="MODEL",
        default=None,
        help="Modelo Ollama para narrativa (ej: llama3.2). "
             "Solo post-procesamiento — no afecta el bundle.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="No ejecutar verify_ebs_v1.py automáticamente",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar warnings detallados y audit_log",
    )

    args = parser.parse_args()

    if not args.input and not args.all_cases:
        parser.print_help()
        print("\n  ERROR: especificar --input ARCHIVO o --all-cases")
        return 2

    # Verificar que el bridge está disponible
    try:
        import vigia_integration_bridge  # type: ignore  # noqa: F401
    except ImportError as e:
        print(f"\n  ERROR CRÍTICO: vigia_integration_bridge.py no importable: {e}")
        print(f"  sys.path: {sys.path[:3]}")
        return 1

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    print(f"  Directorio de salida: {output_dir}")

    run_verify = not args.no_verify
    results = []
    failures = []

    if args.all_cases:
        print("\n  Modo batch — ejecutando todos los casos disponibles")
        _print_separator()
        case_files = []
        for fname in _DEFAULT_CASES:
            found = _find_case_file(fname)
            if found:
                case_files.append(found)
            else:
                print(f"  [WARN] Caso no encontrado: {fname}")

        if not case_files:
            print("  ERROR: no se encontraron casos JSON")
            return 1

        for cf in case_files:
            try:
                r = run_single_case(cf, output_dir, args.ollama, run_verify, args.verbose)
                results.append(r)
            except Exception as e:
                print(f"\n  [ERROR] Caso {cf}: {e}")
                failures.append({"case": cf, "error": str(e)})
    else:
        case_path = _find_case_file(args.input)
        if not case_path:
            print(f"\n  ERROR: archivo no encontrado: '{args.input}'")
            print(f"  Buscado en: {_SCRIPT_DIR}")
            return 1
        try:
            r = run_single_case(case_path, output_dir, args.ollama, run_verify, args.verbose)
            results.append(r)
        except Exception as e:
            print(f"\n  [ERROR] {e}")
            import traceback
            if args.verbose:
                traceback.print_exc()
            return 1

    # Resumen final
    if len(results) > 1:
        _print_separator("═")
        print(f"\n  RESUMEN BATCH: {len(results)} casos procesados, {len(failures)} errores")
        decisions = {}
        for r in results:
            d = r.get("decision", "UNKNOWN")
            decisions[d] = decisions.get(d, 0) + 1
        for k, v in sorted(decisions.items()):
            print(f"    {k}: {v}")

        # Guardar resumen JSON
        summary_path = os.path.join(output_dir, "batch_summary.json")
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": len(results) + len(failures),
            "successful": len(results),
            "failed": len(failures),
            "decisions": decisions,
            "results": [
                {
                    "case_id":    r.get("case_id"),
                    "decision":   r.get("decision"),
                    "posterior":  r.get("posterior"),
                    "bundle_hash": r.get("bundle_hash", "")[:16] + "…",
                    "verify_ok":  r.get("verify", {}).get("passed", False),
                }
                for r in results
            ],
            "failures": failures,
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, sort_keys=True, indent=2, default=str)
        print(f"\n  Resumen guardado: {summary_path}")

    print("\n  Pipeline VIGÍA completado.")
    print("  Para verificar un bundle:")
    print(f"    python3 verify_ebs_v1__3_.py {output_dir}/bundle_<case_id>.json\n")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
