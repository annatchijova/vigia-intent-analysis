"""
Contrato: los `argvalues` de @pytest.mark.parametrize deben ser re-iterables.

Fósil que este contrato cierra (detectado 2026-08-01 al montar mutation
testing, docs/MUTATION_TESTING.md):

`tests/caie/test_canonical_cases.py` pasaba un GENERADOR a
@pytest.mark.parametrize:

    @pytest.mark.parametrize("case", canonical_case_params())   # generador

El objeto generador queda capturado en el marcador, a nivel de módulo. Un
generador se agota al consumirse. En una sesión pytest normal el módulo se
colecta una sola vez y todo funciona — por eso pasó desapercibido. Pero en
cualquier proceso que colecte DOS veces con el módulo ya en sys.modules
(mutmut, que comparte proceso entre list_all_tests / stats / clean run; un
pytest.main() repetido; un runner embebido), la segunda colección recibe un
generador YA AGOTADO y produce CERO parámetros.

Consecuencia: los 52 casos canónicos del corpus CAIE dejan de existir. No
como fallo — como ausencia. pytest reporta "not found" por cada id y sale
con exit 4, o directamente no colecta nada. Un corpus de regresión que se
evapora en silencio mientras la suite sigue "verde" es exactamente la clase
de fallo que este repositorio persigue: cobertura aparente sin verificación.

pytest ya lo señalaba —PytestRemovedIn10Warning, "Passing a non-Collection
iterable to parametrize is deprecated"— y dejará de funcionar en pytest 10.

Este test NO depende de mutmut: reproduce la doble colección directamente.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. El caso concreto que falló
# ---------------------------------------------------------------------------

def test_canonical_case_params_is_not_a_generator():
    """La regresión exacta: canonical_case_params() devolvía un generador."""
    from tests.caie.test_canonical_cases import canonical_case_params

    assert not inspect.isgeneratorfunction(canonical_case_params), (
        "canonical_case_params() es una función generadora. El objeto que "
        "devuelve se consume UNA vez y queda capturado en el marcador "
        "@pytest.mark.parametrize: en una segunda colección dentro del mismo "
        "proceso produce cero parámetros y los casos canónicos desaparecen "
        "sin error. Devolver una lista."
    )

    result = canonical_case_params()
    assert not inspect.isgenerator(result), (
        "canonical_case_params() devuelve un generador (aunque no sea una "
        "función generadora). Mismo fallo: un solo consumo."
    )


def test_canonical_case_params_survives_being_consumed_twice():
    """Lo que rompía: consumir dos veces debe dar el mismo conjunto de ids.

    Éste es el test que reproduce la doble colección sin necesitar mutmut.
    """
    from tests.caie.test_canonical_cases import canonical_case_params

    params = canonical_case_params()

    first = [p.id for p in params]
    second = [p.id for p in params]

    assert first, "la parametrización canónica está vacía en el primer consumo"
    assert second == first, (
        f"segundo consumo devuelve {len(second)} parámetros frente a "
        f"{len(first)} del primero. Los argvalues no son re-iterables: en una "
        f"segunda colección el corpus canónico se evapora."
    )


def test_canonical_corpus_is_not_silently_empty():
    """Guarda de fondo: cero parámetros es un fallo, no un éxito trivial.

    Sin esta guarda, un cambio que vaciara load_canonical_cases() dejaría el
    test anterior pasando (dos listas vacías son iguales) mientras el corpus
    entero deja de ejercitarse.
    """
    from tests.caie.test_canonical_cases import canonical_case_params

    ids = [p.id for p in canonical_case_params()]
    assert len(ids) >= 50, (
        f"sólo {len(ids)} casos canónicos parametrizados. El corpus documentado "
        f"tiene 52 (ver test_all_cases_load). Un corpus que encoge en silencio "
        f"reduce la cobertura de regresión sin que nada falle."
    )
    assert len(ids) == len(set(ids)), "hay ids de caso canónico duplicados"


# ---------------------------------------------------------------------------
# 2. La clase entera, no sólo la ocurrencia
# ---------------------------------------------------------------------------

def _parametrized_call_sources() -> list[tuple[Path, int, str]]:
    """Localiza `@pytest.mark.parametrize(...)` en la suite, por AST."""
    import ast

    found: list[tuple[Path, int, str]] = []
    for path in sorted(REPO.glob("tests/**/*.py")) + sorted(REPO.glob("vigia/tests/**/*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):  # pragma: no cover
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            # pytest.mark.parametrize(...) / mark.parametrize(...)
            if isinstance(func, ast.Attribute) and func.attr == "parametrize":
                if len(node.args) >= 2:
                    found.append((path, node.lineno, ast.unparse(node.args[1])))
    return found


def test_no_generator_expression_passed_to_parametrize():
    """Cierra la clase: una genexp inline tiene el mismo defecto de un solo uso.

    `parametrize("x", (f(i) for i in ...))` es el mismo fallo escrito en una
    línea. Se detecta estructuralmente para no depender de que alguien
    recuerde la lección.
    """
    import ast

    offenders = []
    for path, lineno, src in _parametrized_call_sources():
        try:
            expr = ast.parse(src, mode="eval").body
        except SyntaxError:  # pragma: no cover
            continue
        if isinstance(expr, ast.GeneratorExp):
            offenders.append(f"{path.relative_to(REPO)}:{lineno} -> {src}")

    assert not offenders, (
        "argvalues de parametrize son expresiones generadoras (un solo "
        "consumo; ver el docstring de este módulo):\n  " + "\n  ".join(offenders)
        + "\nEnvolver en list(...)."
    )
