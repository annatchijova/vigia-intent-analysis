"""
Contrato de configuración de mutation testing ([tool.mutmut] en pyproject.toml).

Un barrido de mutación es caro (horas) y se ejecuta desatendido (workflow
semanal). Toda la clase de fallo que este contrato cierra es la misma: **el
barrido corre, termina "sin novedad", y no midió lo que creíamos**. Las cuatro
variantes vistas al montarlo:

  1. Un módulo de `only_mutate` se renombra/mueve. mutmut no lo encuentra,
     genera 0 mutantes para él, y el score sube porque se dejó de medir la
     parte difícil. Silencioso.
  2. Un path de `also_copy` desaparece. Los tests fallan dentro de mutants/
     por FileNotFoundError y TODOS los mutantes se declaran muertos — por la
     razón equivocada. Score 100% falso.
  3. Un módulo de test excluido se renombra. La exclusión deja de aplicar, el
     runner vuelve a colectar un módulo que no colecta en el sandbox, y el
     barrido aborta antes de medir nada.
  4. `mutants/` deja de estar ignorado por git. Es el peor: mutants/ contiene
     una copia de la ruta de veredicto CON DEFECTOS DELIBERADOS INYECTADOS.
     Commitearla mete código de scoring mutado en el repo. Misma clase de
     riesgo que el benchmark tests/unit/test_m4_floor.py, que .gitignore ya
     trata igual por la misma razón.

Ver docs/MUTATION_TESTING.md. Este test NO ejecuta mutmut — valida su contrato.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PYPROJECT = REPO / "pyproject.toml"

# tomllib es stdlib desde 3.11; el proyecto declara 3.10+ (README/pyproject).
# Mismo patrón de fallback que usa el propio mutmut para leer pyproject.toml.
if sys.version_info >= (3, 11):
    import tomllib as _toml_reader
else:  # pragma: no cover - sólo se ejerce en 3.10
    _toml_reader = pytest.importorskip(
        "tomli",
        reason="Python <3.11 sin `tomli`: no se puede leer [tool.mutmut] de "
               "pyproject.toml. El contrato de mutation testing queda sin "
               "verificar en este intérprete (CI corre 3.11).",
    )


def _mutmut_config() -> dict:
    with PYPROJECT.open("rb") as fh:
        data = _toml_reader.load(fh)
    try:
        return data["tool"]["mutmut"]
    except KeyError:  # pragma: no cover - el propio test lo reporta
        pytest.fail(
            "pyproject.toml no tiene sección [tool.mutmut]. La infraestructura "
            "de mutation testing se documenta en docs/MUTATION_TESTING.md; si "
            "se retira deliberadamente, retirar también este contrato y el "
            "workflow .github/workflows/mutation.yml."
        )


CONFIG = _mutmut_config()


# ---------------------------------------------------------------------------
# 1. Los módulos mutados existen
# ---------------------------------------------------------------------------

def test_only_mutate_lists_existing_modules():
    """Variante 1: un módulo renombrado se deja de mutar en silencio."""
    only_mutate = CONFIG.get("only_mutate", [])
    assert only_mutate, "only_mutate vacío: el barrido mutaría TODO source_paths"

    missing = [p for p in only_mutate if "*" not in p and not (REPO / p).is_file()]
    assert not missing, (
        f"only_mutate apunta a módulos inexistentes: {missing}. mutmut genera 0 "
        f"mutantes para ellos y el mutation score SUBE por haber dejado de "
        f"medir. Actualizar la ruta en pyproject.toml [tool.mutmut]."
    )


def test_only_mutate_covers_the_sealed_verdict_scorer():
    """El scorer raíz es la ruta de veredicto sellado. Si algo se muta, es esto.

    Guarda de alcance, no de estilo: acotar el barrido a módulos periféricos
    y reportar un score alto sería exactamente la métrica-teatro que
    docs/MUTATION_TESTING.md §4 previene.
    """
    only_mutate = CONFIG.get("only_mutate", [])
    assert "vigia_scorer.py" in only_mutate, (
        "vigia_scorer.py fuera de only_mutate: el mutation score dejaría de "
        "cubrir la aritmética que produce el veredicto sellado."
    )


# ---------------------------------------------------------------------------
# 2. Los datos que la suite necesita en el sandbox existen
# ---------------------------------------------------------------------------

def test_also_copy_paths_exist():
    """Variante 2: un path que falta mata todos los mutantes por FileNotFound."""
    missing = [p for p in CONFIG.get("also_copy", []) if not (REPO / p).exists()]
    assert not missing, (
        f"also_copy referencia paths inexistentes: {missing}. Dentro de "
        f"mutants/ la suite fallaría por FileNotFoundError y TODOS los "
        f"mutantes se declararían muertos — score 100% falso."
    )


def test_source_paths_exist_and_include_root_decision_modules():
    """source_paths es lo que se copia al sandbox: sin esto no hay nada que mutar."""
    source_paths = CONFIG.get("source_paths", [])
    missing = [p for p in source_paths if not (REPO / p).exists()]
    assert not missing, f"source_paths inexistentes: {missing}"

    # Los módulos raíz de la ruta de decisión viven fuera del paquete vigia/.
    # Es el mismo conjunto que [tool.coverage.run].source cubre por la misma
    # razón: SON el pipeline de veredicto sellado.
    for root_module in ("vigia_scorer.py", "vigia_agent.py", "sift_orchestrator.py"):
        assert root_module in source_paths, (
            f"{root_module} fuera de source_paths: no se copiaría a mutants/ y "
            f"los tests que lo importan fallarían por ModuleNotFoundError."
        )


# ---------------------------------------------------------------------------
# 3. Las exclusiones siguen apuntando a algo
# ---------------------------------------------------------------------------

def test_ignored_test_modules_still_exist():
    """Variante 3: una exclusión que apunta a un fichero renombrado no excluye nada.

    Cada `--ignore=` de la selección está justificado en
    docs/MUTATION_TESTING.md §5 (tests meta-repo que inspeccionan fuente, y
    módulos que importan el bridge MCP). Si el fichero se renombra, la
    exclusión deja de aplicar y el barrido aborta al colectar.
    """
    selection = CONFIG.get("pytest_add_cli_args_test_selection", [])
    ignored = [a.split("=", 1)[1] for a in selection if a.startswith("--ignore=")]
    assert ignored, "sin --ignore= en la selección: revisar docs/MUTATION_TESTING.md §5"

    missing = [p for p in ignored if not (REPO / p).exists()]
    assert not missing, (
        f"--ignore= apunta a rutas inexistentes: {missing}. La exclusión ya no "
        f"aplica; si el módulo se renombró, actualizar pyproject.toml, y si se "
        f"borró, retirar el --ignore y su justificación en "
        f"docs/MUTATION_TESTING.md §5."
    )


def test_tests_are_never_mutated():
    """Mutar un test no significa nada: mide el mutante, no la suite."""
    do_not_mutate = CONFIG.get("do_not_mutate", [])
    assert any("test" in pattern for pattern in do_not_mutate), (
        "do_not_mutate no protege los tests: mutmut mutaría los propios "
        "asserts y el score dejaría de tener sentido."
    )


# ---------------------------------------------------------------------------
# 4. Lo declarado se mide de verdad
# ---------------------------------------------------------------------------

def test_ci_matrix_covers_every_module_in_only_mutate():
    """Quinta variante de la misma clase: declarado pero nunca medido.

    El workflow reparte un job por módulo (obligado: los 8 en un solo job
    suman ~359 min y el tope duro de un job en GitHub Actions es 360). Esa
    matriz es una segunda lista de módulos, y dos listas que deben coincidir
    se desincronizan solas: añadir un módulo a only_mutate y olvidarlo en la
    matriz lo deja fuera de la medición semanal para siempre, sin que nada
    falle. Al revés — un módulo en la matriz que no está en only_mutate —
    gasta un runner entero para no mutar nada.
    """
    yaml = pytest.importorskip("yaml")

    workflow = REPO / ".github" / "workflows" / "mutation.yml"
    assert workflow.is_file(), (
        "falta .github/workflows/mutation.yml: el barrido semanal es lo que "
        "mide los módulos que no caben en una sesión interactiva."
    )

    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    matrix = data["jobs"]["mutation"]["strategy"]["matrix"]["module"]

    declared = set(CONFIG.get("only_mutate", []))
    measured = set(matrix)

    assert declared == measured, (
        f"only_mutate y la matriz de mutation.yml difieren.\n"
        f"  declarados pero NO medidos por CI: {sorted(declared - measured)}\n"
        f"  en la matriz pero NO declarados:   {sorted(measured - declared)}"
    )


def test_ci_job_timeout_stays_under_the_github_hard_limit():
    """El tope duro de un job en GitHub Actions es 360 min: un timeout mayor
    no protege de nada — el job muere igual y deja un barrido a medias, que
    es exactamente lo que docs/MUTATION_BASELINE.md §1 descarta como
    medición válida."""
    yaml = pytest.importorskip("yaml")

    data = yaml.safe_load((REPO / ".github" / "workflows" / "mutation.yml").read_text(encoding="utf-8"))
    timeout = data["jobs"]["mutation"]["timeout-minutes"]
    assert timeout < 360, (
        f"timeout-minutes={timeout} >= 360, el tope duro de GitHub Actions. "
        f"El job se cancelaría sin resultado utilizable."
    )


# ---------------------------------------------------------------------------
# 5. El sandbox mutado nunca entra al repo
# ---------------------------------------------------------------------------

def test_mutants_dir_is_gitignored():
    """Variante 4 — la de mayor severidad.

    mutants/ contiene una copia de vigia_scorer.py y caie.py con defectos
    inyectados a propósito. Commitearla pondría lógica de veredicto mutada en
    el árbol. .gitignore ya trata igual el benchmark test_m4_floor.py, que
    reescribe fuente en tiempo de pytest, y por el mismo motivo.
    """
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    entries = {line.strip() for line in gitignore.splitlines()}
    assert "mutants/" in entries, (
        ".gitignore no ignora mutants/. Ese directorio es una copia de la ruta "
        "de veredicto CON DEFECTOS INYECTADOS: si se commitea, entra código de "
        "scoring mutado al repositorio."
    )
