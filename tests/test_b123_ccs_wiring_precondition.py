"""
B-123 — precondición de cableado del gate Causal Closure Score, como tripwire.

B-123 documenta que el gate CCS está diseñado, probado y NO cableado, porque
sus 4 dimensiones de entrada no las produce nadie. Esa condición de bloqueo
vivía sólo en prosa, y tiene dos filos:

  · mientras nadie produzca las dimensiones, cablear el gate caparía el corpus
    ENTERO a ABSTAIN — no es cosmético, es catastrófico (ver la corrección de
    2026-08-01 en la entrada, que rectifica el razonamiento original);
  · en cuanto ALGUIEN empiece a producirlas, B-123 pasa a ser accionable y
    nadie se entera, porque la prosa no falla.

Este módulo convierte ambos filos en tests.

Nota sobre la dirección del fallo: si estos tests se ponen en rojo NO
significa que algo se rompió. Significa que la precondición cambió y hay que
releer B-123 — que es exactamente lo que se quiere que ocurra.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Las 4 dimensiones que `compute_causal_closure()` acepta. Si alguna aparece en
# un caso del corpus, hay un productor vivo.
_CCS_DIMENSIONS = (
    "temporal_coherence",
    "semantic_resonance",
    "abductive_parsimony",
    "adversarial_silence",
)


def _corpus_cases() -> list[dict]:
    cases: list[dict] = []
    for pattern in ("data/cases/**/*.json", "cases/*.json"):
        for path in REPO.glob(pattern):
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                continue
            for case in (loaded if isinstance(loaded, list) else [loaded]):
                if isinstance(case, dict) and "artifacts" in case:
                    cases.append(case)
    return cases


# ---------------------------------------------------------------------------
# 1. El gate degrada con honestidad (H-04) — la razón por la que NO cablearlo
# ---------------------------------------------------------------------------

def test_gate_does_not_pass_without_information():
    """Sin ninguna dimensión, el gate NO habilita nada y lo declara.

    Ésta es la conducta que la entrada B-123 describía al revés: decía que el
    gate "pasa incondicionalmente" y por tanto cablearlo sería cosmético.
    H-04 (2026-07-23) lo corrigió; la entrada no se actualizó hasta 2026-08-01.
    """
    from vigia.core.causal_closure import compute_causal_closure

    result = compute_causal_closure()

    assert result.dimensions_provided == 0
    assert result.insufficient_coverage is True
    assert result.gate_passed is False, (
        "el gate CCS habilita MALICE_HIGH sin ninguna dimensión de entrada. "
        "Un gate que aprueba por defecto no es un gate — H-04."
    )
    assert result.verdict_cap == "ABSTAIN"
    assert "INSUFFICIENT COVERAGE" in result.explanation


def test_partial_coverage_is_still_insufficient():
    """Una sola dimensión real no basta: 1 de 4 sigue siendo mayoría de
    defaults, y un gate que decide sobre defaults decide sobre nada."""
    from fractions import Fraction

    from vigia.core.causal_closure import compute_causal_closure

    result = compute_causal_closure(temporal_coherence=Fraction(9, 10))

    assert result.dimensions_provided == 1
    assert result.insufficient_coverage is True, (
        "con 1 de 4 dimensiones el gate se declara suficientemente cubierto; "
        "las otras 3 siguen siendo Fraction(1,2) inventado."
    )


# ---------------------------------------------------------------------------
# 2. El tripwire: cuándo B-123 deja de estar bloqueado
# ---------------------------------------------------------------------------

def test_corpus_still_supplies_no_ccs_dimension():
    """Precondición de B-123, ejecutable.

    Mientras esto pase, cablear el gate caparía TODO el corpus a ABSTAIN.
    Cuando falle, significa que apareció un productor: B-123 pasa a ser
    accionable y hay que releerlo — no silenciar este test.
    """
    cases = _corpus_cases()
    assert cases, "no se encontró ningún caso de corpus; revisar las rutas"

    con_dimension = []
    for case in cases:
        blob = json.dumps(case)
        found = [d for d in _CCS_DIMENSIONS if f'"{d}"' in blob]
        if found:
            con_dimension.append((case.get("case_id", "?"), found))

    assert not con_dimension, (
        f"{len(con_dimension)} caso(s) del corpus aportan dimensiones CCS: "
        f"{con_dimension[:5]}.\n"
        f"B-123 estaba bloqueado precisamente por su ausencia. Si ahora hay un "
        f"productor, releer B-123 y decidir el cableado con un dry-run real — "
        f"no ampliar esta lista de excepciones."
    )


def test_wiring_today_would_cap_the_entire_corpus():
    """Cuantifica el coste real de cablear hoy, que la entrada subestimaba.

    No es una advertencia en prosa: se computa el gate con los datos que el
    corpus efectivamente tiene (ninguno) y se comprueba que el resultado es
    ABSTAIN para todos.
    """
    from vigia.core.causal_closure import compute_causal_closure

    cases = _corpus_cases()
    assert cases

    result = compute_causal_closure()  # lo que recibiría cada caso hoy
    assert result.verdict_cap == "ABSTAIN"
    assert result.insufficient_coverage is True, (
        f"cablear el gate CCS hoy aplicaría este resultado a los {len(cases)} "
        f"casos del corpus. Con insufficient_coverage=True eso es un cap a "
        f"ABSTAIN corpus-wide, no una operación cosmética."
    )


# ---------------------------------------------------------------------------
# 3. El gate sigue sin estar cableado
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_path", [
    "vigia_scorer.py",
    "sift_orchestrator.py",
    "vigia_agent.py",
])
def test_ccs_gate_is_not_wired_into_the_verdict_path(module_path):
    """Guarda de doctrina: mientras la precondición no se cumpla, el gate no
    debe aparecer en la ruta de veredicto sellado. Si alguien lo cablea, este
    test lo hace visible en la misma corrida que lo introduce."""
    source = (REPO / module_path).read_text(encoding="utf-8")
    assert "causal_closure" not in source, (
        f"{module_path} referencia causal_closure. B-123 sigue bloqueado por "
        f"4 productores huérfanos; cablearlo hoy capa el corpus entero a "
        f"ABSTAIN. Si el cableado es deliberado, cerrar B-123 con su dry-run "
        f"y retirar esta guarda en el mismo cambio."
    )
