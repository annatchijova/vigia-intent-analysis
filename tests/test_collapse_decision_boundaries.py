"""
CollapseDecisionLayer — fronteras de decisión y textos centinela.

Origen: primera línea base de mutation testing (docs/MUTATION_BASELINE.md).
`vigia/collapse_decision.py` puntuaba 4 mutantes muertos de 29 — **13,8%** —
con 77,94% de cobertura de línea. Es la demostración de manual de la
diferencia entre las dos métricas: las líneas se ejecutaban, el
comportamiento no se verificaba.

Los 25 supervivientes eran todos huecos reales, ninguno equivalente, y de
tres clases:

  1. CADENAS CENTINELA. `"sensor_independence"` -> `"XXsensor_independenceXX"`
     sobrevivía. Esa comparación es la REGLA CLAVE declarada del módulo
     ("cualquier ruptura de sensor_independence -> INCONCLUSIVE"): nadie
     comprobaba que la regla dispara con la cadena que realmente se usa.
  2. OPERADORES DE FRONTERA. `>=` -> `>`, `<` -> `<=`. Cambian el veredicto
     exactamente en el punto de corte, que es donde una decisión forense se
     juega.
  3. CONSTANTES DE UMBRAL. `base_score >= 0.5` -> `>= 1.5` sobrevivía: el
     umbral de MALICE podía moverse a un valor inalcanzable sin que nada
     fallara.

Cada test de aquí abajo mata mutantes concretos. La disciplina que impone:
probar el punto de corte EXACTO (0.5, 0.2, 0.3, len==2), no un valor cómodo
a mitad del intervalo — un test con base_score=0.9 pasa igual con el umbral
en 0.5 que en 0.8, y por eso no mata nada.

Nota de diseño observada, deliberadamente NO corregida aquí: `explain()`
recalcula el motivo por su cuenta en vez de recibirlo de `resolve()`, así
que ambas escaleras de condiciones pueden divergir en silencio. Los tests
fijan las dos por separado, que es lo que se puede afirmar hoy.
"""

from __future__ import annotations

import pytest

from vigia.collapse_decision import (
    CollapseContext,
    CollapseDecisionLayer,
    CollapseVerdict,
)


@pytest.fixture
def layer() -> CollapseDecisionLayer:
    return CollapseDecisionLayer()


def _ctx(
    *,
    broken=(),
    coverage_ratio: float = 1.0,
    base_score: float = 0.0,
    has_structural_malice: bool = False,
    independent_sources: int = 3,
) -> CollapseContext:
    """Contexto neutro: sin colapso y NOISE, salvo lo que cada test mueva."""
    return CollapseContext(
        broken_assumptions=set(broken),
        coverage_ratio=coverage_ratio,
        base_score=base_score,
        has_structural_malice=has_structural_malice,
        independent_sources=independent_sources,
    )


# ---------------------------------------------------------------------------
# resolve() — cadenas centinela
# ---------------------------------------------------------------------------

def test_sensor_independence_exact_string_triggers_inconclusive(layer):
    """Mata resolve__mutmut_2/3 ("XXsensor_independenceXX", "SENSOR_INDEPENDENCE").

    La regla clave del módulo. El contexto es por lo demás perfectamente
    benigno (cobertura plena, score 0) para que el único motivo posible de
    INCONCLUSIVE sea esta cadena.
    """
    verdict = layer.resolve(_ctx(broken=["sensor_independence"]))
    assert verdict is CollapseVerdict.INCONCLUSIVE


def test_pipeline_integrity_exact_string_triggers_inconclusive(layer):
    """Mata resolve__mutmut_5/6."""
    verdict = layer.resolve(_ctx(broken=["pipeline_integrity"]))
    assert verdict is CollapseVerdict.INCONCLUSIVE


def test_unknown_broken_assumption_alone_does_not_collapse(layer):
    """Contrapunto de los dos anteriores: sin él, un test que exigiera
    INCONCLUSIVE para cualquier cadena pasaría con los centinelas rotos."""
    assert layer.resolve(_ctx(broken=["algo_no_reconocido"])) is CollapseVerdict.NOISE


# ---------------------------------------------------------------------------
# resolve() — fronteras
# ---------------------------------------------------------------------------

def test_exactly_two_broken_assumptions_collapse(layer):
    """Mata resolve__mutmut_8 (`> 2`) y _9 (`>= 3`).

    Dos supuestos NO centinela: el colapso sólo puede venir del recuento.
    """
    ctx = _ctx(broken=["supuesto_a", "supuesto_b"])
    assert layer.resolve(ctx) is CollapseVerdict.INCONCLUSIVE


def test_one_broken_assumption_does_not_collapse_by_count(layer):
    """Frontera por abajo: len==1 no debe colapsar."""
    assert layer.resolve(_ctx(broken=["supuesto_a"])) is CollapseVerdict.NOISE


def test_coverage_exactly_at_threshold_is_not_too_low(layer):
    """Mata resolve__mutmut_10 (`< 0.3` -> `<= 0.3`).

    0.3 exacto NO es "demasiado bajo". base_score alto para que, si el gate
    no dispara, el veredicto sea distinguible de INCONCLUSIVE.
    """
    ctx = _ctx(coverage_ratio=0.3, base_score=0.6)
    assert layer.resolve(ctx) is CollapseVerdict.MALICE


def test_coverage_just_below_threshold_collapses(layer):
    """El otro lado del corte: por debajo de 0.3 sí colapsa."""
    ctx = _ctx(coverage_ratio=0.29, base_score=0.6)
    assert layer.resolve(ctx) is CollapseVerdict.INCONCLUSIVE


def test_base_score_exactly_at_malice_threshold_is_malice(layer):
    """Mata resolve__mutmut_12 (`> 0.5`) y _13 (`>= 1.5`).

    0.5 exacto es MALICE. Un test con 0.9 no distingue el umbral 0.5 del 0.8
    y no mata nada: hay que pisar el punto de corte.
    """
    assert layer.resolve(_ctx(base_score=0.5)) is CollapseVerdict.MALICE


def test_base_score_just_below_malice_threshold_is_suspicion(layer):
    assert layer.resolve(_ctx(base_score=0.49)) is CollapseVerdict.SUSPICION


def test_base_score_exactly_at_suspicion_threshold_is_suspicion(layer):
    """Mata resolve__mutmut_14 (`> 0.2`) y _15 (`>= 1.2`)."""
    assert layer.resolve(_ctx(base_score=0.2)) is CollapseVerdict.SUSPICION


def test_base_score_just_below_suspicion_threshold_is_noise(layer):
    assert layer.resolve(_ctx(base_score=0.19)) is CollapseVerdict.NOISE


def test_structural_malice_outranks_a_noise_level_score(layer):
    """La bandera estructural decide antes que el score numérico."""
    assert layer.resolve(_ctx(base_score=0.0, has_structural_malice=True)) is (
        CollapseVerdict.MALICE
    )


def test_collapse_outranks_structural_malice(layer):
    """Orden de precedencia: un colapso de supuestos gana a MALICE estructural.

    Es la política declarada del módulo ("política agresiva") y conviene que
    esté fijada: invertir el orden de esos bloques no rompería ningún otro
    test de este fichero.
    """
    ctx = _ctx(broken=["sensor_independence"], has_structural_malice=True)
    assert layer.resolve(ctx) is CollapseVerdict.INCONCLUSIVE


# ---------------------------------------------------------------------------
# explain() — 0 de 14 mutantes muertos antes de este bloque
# ---------------------------------------------------------------------------

def test_explain_sensor_independence_message(layer):
    """Mata explain__mutmut_2/3/4 (centinela y `not in`)."""
    ctx = _ctx(broken=["sensor_independence"])
    msg = layer.explain(ctx, CollapseVerdict.INCONCLUSIVE)
    assert msg == (
        "INCONCLUSIVE: Sensor independence broken - cannot trust evidence correlation"
    )


def test_explain_pipeline_integrity_message(layer):
    """Mata explain__mutmut_5/6/7."""
    ctx = _ctx(broken=["pipeline_integrity"])
    msg = layer.explain(ctx, CollapseVerdict.INCONCLUSIVE)
    assert msg == "INCONCLUSIVE: Pipeline integrity compromised"


def test_explain_counts_broken_assumptions(layer):
    """Mata explain__mutmut_8 (`> 2`) y _9 (`>= 3`)."""
    ctx = _ctx(broken=["supuesto_a", "supuesto_b"])
    msg = layer.explain(ctx, CollapseVerdict.INCONCLUSIVE)
    assert msg == "INCONCLUSIVE: 2 assumptions broken"


def test_explain_low_coverage_is_reported_as_a_percentage(layer):
    """Mata explain__mutmut_11 (`< 1.3`) por el lado del disparo."""
    ctx = _ctx(coverage_ratio=0.25)
    msg = layer.explain(ctx, CollapseVerdict.INCONCLUSIVE)
    assert msg == "INCONCLUSIVE: Coverage too low (25.0%)"


def test_explain_coverage_exactly_at_threshold_is_not_reported_as_low(layer):
    """Mata explain__mutmut_10 (`<= 0.3`).

    Con 0.3 exacto y ningún supuesto roto no hay motivo que reportar, aunque
    el veredicto que se pase sea INCONCLUSIVE.
    """
    ctx = _ctx(coverage_ratio=0.3)
    assert layer.explain(ctx, CollapseVerdict.INCONCLUSIVE) == "Standard verdict"


def test_explain_coverage_above_threshold_is_not_reported_as_low(layer):
    """Mata explain__mutmut_11 (`< 0.3` -> `< 1.3`) por el lado del no-disparo.

    Con 0.5 el original no reporta nada; el mutante `< 1.3` sí reportaría
    "Coverage too low (50.0%)" — una afirmación falsa en la narrativa
    orientada a Daubert.
    """
    ctx = _ctx(coverage_ratio=0.5)
    assert layer.explain(ctx, CollapseVerdict.INCONCLUSIVE) == "Standard verdict"


@pytest.mark.parametrize(
    "verdict",
    [CollapseVerdict.MALICE, CollapseVerdict.SUSPICION, CollapseVerdict.NOISE],
)
def test_explain_returns_standard_verdict_for_non_inconclusive(layer, verdict):
    """Mata explain__mutmut_1 (`==` -> `!=`) y _12/_13/_14 (texto exacto).

    El contexto lleva sensor_independence roto a propósito: con el
    comparador invertido, el mutante entraría en el bloque y devolvería el
    mensaje de INCONCLUSIVE para un veredicto que no lo es.
    """
    ctx = _ctx(broken=["sensor_independence"])
    assert layer.explain(ctx, verdict) == "Standard verdict"
