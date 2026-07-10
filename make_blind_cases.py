#!/usr/bin/env python3
"""
make_blind_cases.py — Genera versiones ciegas de casos VIGÍA para
contraste con Claude vía MCP, sin fuga de etiqueta.

Uso:
    python3 make_blind_cases.py

Busca cada case_id en las CASES_DIRS conocidas del repo, remueve los
campos que filtran la respuesta esperada, y escribe:
  - out_dir/<case_id>.json           (versión ciega)
  - out_dir/_manifest.json           (ciego -> original, con el
                                       expected_verdict real oculto
                                       ahí para comparar DESPUÉS)

Nunca modifica los archivos originales del corpus.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

# ── Configuración ──────────────────────────────────────────────────────────

# Directorios donde puede vivir un caso, en orden de prioridad de búsqueda.
# Ajustar si el repo tiene otras rutas (coincide con las CASES_DIRS de
# check_label_consistency / run_all_agent.py).
CASES_DIRS = [
    "data/cases",
    "data/cases/converted",
    "data/cases/benign",
    "data/cases/consolidated_canonical",
    "data/cases/legacy",
    "data/cases/red-team",
    "cases",
    "results/agent_batch",  # algunos casos solo existen como *_agent_bundle.json
]

OUT_DIR = Path("blind_cases_for_mcp")

# Los 30 sin ningún material LLM previo (prioridad real de la investigación)
CASOS_SIN_MATERIAL_LLM = [
    "VIGIA-NITROBA-M57-001",
    "VIGIA-REAL-M57-JO-Dec07",
    "VIGIA-REAL-M57-PAT-Dec07",
    "VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT",
    "VIGIA-REAL-MAGNET-2021-IOS-ELI",
    "VIGIA-REAL-MAGNET-2022-ANDROID",
    "VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL",
    "VIGIA-SET630-001",
    "VIGIA-SEP800-001",
    "VIGIA-SET68I-001",
    "VIGIA-CAN-014",
    "VIGIA-CAN-016",
    "VIGIA-CAN-017",
    "VIGIA-CAN-032",
    "VIGIA-2026-DEMO-004",
    "VIGIA-2026-DEMO-007",
    "VIGIA-2026-DEMO-008",
    "VIGIA-2026-DEMO-009",
    "VIGIA-LINUX-005",
    "VIGIA-LINUX-006",
    "VIGIA-LINUX-008",
    "VIGIA-NGDC-003",
    "case_002_log_fabrication",
    "case_008_multi_source_fraud_demo",
    "VIGIA-PAGINA-WEB-PAPA-2026",
    "VIGIA-WEDLM-2025",
    "VIGIA-ANDROID11-001",
    "VIGIA-ASCIISTUDIO-2025",
    "VIGIA-BEN-012",
    "VIGIA-BEN-014",
]

# Los 16 con material LLM contaminado (fuga de etiqueta en el prompt
# original, o ground truth desincronizado) — re-correr ciego para que
# valgan como contraste independiente.
CASOS_CONTAMINADOS_RECORRER = [
    "FP-CULTURAL-CLEAN",
    "FP-CULTURAL-CLEAN-001",
    "VIGIA-FN-001",
    "VIGIA-FN-002",
    "VIGIA-FN-003",
    "VIGIA-FP-002",
    "VIGIA-FP-003",
    "VIGIA-REAL-005",
    "VIGIA-REAL-007",
    "VIGIA_BREAK_001_SILENT_INCONSISTENCY",
    "VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE",
    "VIGIA_BREAK_004_SIGNAL_DROWNING",
    "VIGIA_BREAK_006_PERFECT_ATTACK",
    "VIGIA_BREAK_007_MISSING_LOGS",
    "VIGIA_BREAK_008_AMBIGUOUS",
    "VIGIA_BREAK_009_PROMPT_POISON",
]

TODOS_LOS_CASOS = CASOS_SIN_MATERIAL_LLM + CASOS_CONTAMINADOS_RECORRER

# Campos que filtran la respuesta esperada y deben removerse de la
# versión ciega. expected_mitre_ttps también filtra (se usa para
# inferir benignidad en normalize_case_schema), así que sale también.
CAMPOS_A_REMOVER = [
    "expected_verdict",
    "expected_mitre_ttps",
    "fallback_verdict",   # solo aparece en bundles LLM viejos, no en casos
    "llm_verdict",        # idem — por si el archivo encontrado es un bundle
    "audit_note",         # algunas audit_note narran el resultado esperado
]


def find_case_file(case_id: str) -> Path | None:
    """Busca el JSON del caso por nombre exacto o por sufijo _agent_bundle."""
    candidatos = [
        f"{case_id}.json",
        f"{case_id}_agent_bundle.json",
    ]
    for base_dir in CASES_DIRS:
        base = Path(base_dir)
        if not base.exists():
            continue
        for nombre in candidatos:
            p = base / nombre
            if p.exists():
                return p
    # búsqueda recursiva de último recurso
    for base_dir in CASES_DIRS:
        base = Path(base_dir)
        if not base.exists():
            continue
        for nombre in candidatos:
            hits = list(base.rglob(nombre))
            if hits:
                return hits[0]
    return None


def strip_leaking_fields(case: dict) -> tuple[dict, dict]:
    """Remueve los campos que filtran la respuesta. Devuelve (ciego, removidos)."""
    ciego = dict(case)
    removidos = {}
    for campo in CAMPOS_A_REMOVER:
        if campo in ciego:
            removidos[campo] = ciego.pop(campo)
    return ciego, removidos


def main():
    OUT_DIR.mkdir(exist_ok=True)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Casos ciegos para contraste independiente Claude/MCP. "
            "El campo 'expected_verdict_OCULTO' NO debe mostrarse a Claude "
            "hasta despues de que emita su veredicto — es solo para que "
            "Anna compare al final."
        ),
        "casos": {},
    }

    no_encontrados = []
    ok = []

    for case_id in TODOS_LOS_CASOS:
        origen = find_case_file(case_id)
        if origen is None:
            no_encontrados.append(case_id)
            continue

        try:
            data = json.loads(origen.read_text())
        except Exception as e:
            no_encontrados.append(f"{case_id} (error leyendo: {e})")
            continue

        # Si el archivo es un bundle (tiene 'agent_verdict' sellado en vez
        # de un caso crudo), avisamos — no es el formato esperado para
        # correr de nuevo por el agente.
        es_bundle = "agent_verdict" in data or "bundle_version" in data

        ciego, removidos = strip_leaking_fields(data)

        out_path = OUT_DIR / f"{case_id}.json"
        out_path.write_text(json.dumps(ciego, indent=2, ensure_ascii=False))

        manifest["casos"][case_id] = {
            "archivo_ciego": str(out_path),
            "archivo_original": str(origen),
            "es_bundle_no_caso_crudo": es_bundle,
            "expected_verdict_OCULTO": removidos.get("expected_verdict", "?"),
            "campos_removidos": list(removidos.keys()),
            "grupo": (
                "sin_material_llm"
                if case_id in CASOS_SIN_MATERIAL_LLM
                else "contaminado_recorrer"
            ),
        }
        ok.append(case_id)

    manifest_path = OUT_DIR / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"\n{'='*72}")
    print(f"Casos ciegos generados: {len(ok)} / {len(TODOS_LOS_CASOS)}")
    print(f"Carpeta: {OUT_DIR.resolve()}")
    print(f"Manifiesto (con las respuestas ocultas): {manifest_path.resolve()}")
    if no_encontrados:
        print(f"\n⚠️  NO encontrados ({len(no_encontrados)}):")
        for c in no_encontrados:
            print(f"   - {c}")
        print(
            "\n   Ajustá CASES_DIRS al principio del script si tus casos "
            "viven en otra ruta, o pasame el path real y lo corrijo."
        )
    bundles = [c for c, v in manifest["casos"].items() if v["es_bundle_no_caso_crudo"]]
    if bundles:
        print(f"\n⚠️  Estos {len(bundles)} son BUNDLES (ya sellados), no casos crudos:")
        for c in bundles:
            print(f"   - {c}  (revisar si hay un caso crudo real en otra carpeta)")
    print(f"{'='*72}\n")


if __name__ == "__main__":
    main()
