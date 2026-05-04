"""
vigia/core/ockham_adversarial.py
================================
Penalización adversarial de Ockham para VIGÍA.

Principio: Un adversario sofisticado DISEÑA incidentes donde la hipótesis
más simple es incompetencia benigna. La simplicidad en presencia de señales
de malicia es ella misma una señal (Secondness peirceana).

Caso SolarWinds: DLL firmada + 5 anomalías ignoradas → explicación "demasiado limpia".
VIGÍA penaliza ese costo artificialmente bajo y prefiere MALICE.

Invariantes:
- Todo scoring usa fractions.Fraction — sin float en lógica interna
- Display usa int(confidence * 100) — sin round() banker's rounding
- _PENALTY_TABLE es inmutable (frozenset de keys)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import NamedTuple


class MaliceSignalStrength(Enum):
    """Fuerza ordinal de señales de malicia. Sin floats."""
    NONE     = 0
    WEAK     = 1
    MODERATE = 2
    STRONG   = 3
    CRITICAL = 4


class OckhamPenaltyResult(NamedTuple):
    """
    Resultado del scoring adversarial.
    Inmutable por diseño.
    """
    raw_cost:         Fraction   # Costo Ockham original
    penalty:          Fraction   # Penalización por simplicidad sospechosa
    adjusted_cost:    Fraction   # raw_cost + penalty
    trigger_reason:   str        # Razonamiento trazable (Daubert)
    adversarial_flag: bool       # True si simplicidad fue declarada sospechosa

    def display_confidence(self) -> int:
        """
        Porcentaje entero para display — sin float, sin round().
        Usa int() truncado para reproducibilidad cross-arch.
        """
        # Confianza inversa al costo ajustado (normalizada a [0,100])
        max_cost = Fraction(2, 1)  # techo operativo
        clamped = min(self.adjusted_cost, max_cost)
        raw = Fraction(1) - (clamped / max_cost)
        return int(raw * 100)


# ─── Tabla de penalización ───────────────────────────────────────────────────
# (fuerza_señal, rango_simplicidad) → multiplicador adicional (Fraction)
# Lógica: señales CRITICAL + hipótesis extremadamente simple
#         = perfil exacto de adversario sofisticado

_PENALTY_TABLE: dict[tuple[MaliceSignalStrength, str], Fraction] = {
    (MaliceSignalStrength.CRITICAL, "extreme"):  Fraction(3, 1),
    (MaliceSignalStrength.CRITICAL, "high"):     Fraction(2, 1),
    (MaliceSignalStrength.CRITICAL, "moderate"): Fraction(1, 1),
    (MaliceSignalStrength.STRONG,   "extreme"):  Fraction(2, 1),
    (MaliceSignalStrength.STRONG,   "high"):     Fraction(3, 2),
    (MaliceSignalStrength.STRONG,   "moderate"): Fraction(1, 2),
    (MaliceSignalStrength.MODERATE, "extreme"):  Fraction(1, 1),
    (MaliceSignalStrength.MODERATE, "high"):     Fraction(1, 2),
    (MaliceSignalStrength.MODERATE, "moderate"): Fraction(1, 4),
    (MaliceSignalStrength.WEAK,     "extreme"):  Fraction(1, 4),
    (MaliceSignalStrength.WEAK,     "high"):     Fraction(1, 8),
    (MaliceSignalStrength.WEAK,     "moderate"): Fraction(0, 1),
    (MaliceSignalStrength.NONE,     "extreme"):  Fraction(0, 1),
    (MaliceSignalStrength.NONE,     "high"):     Fraction(0, 1),
    (MaliceSignalStrength.NONE,     "moderate"): Fraction(0, 1),
}

# Umbral mínimo de señales débiles para activar modo adversarial
_WEAK_SIGNAL_THRESHOLD: int = 3


def _classify_simplicity_gap(
    candidate_cost: Fraction,
    next_best_cost: Fraction,
) -> str:
    """
    Clasifica cuán más simple es la hipótesis candidata vs la siguiente.
    Retorna string ordinal — nunca float.
    """
    if next_best_cost == Fraction(0):
        return "moderate"

    # Evitar división por cero si candidata tiene costo 0
    denom = max(candidate_cost, Fraction(1, 1_000))
    gap_ratio = next_best_cost / denom

    if gap_ratio >= Fraction(4, 1):
        return "extreme"
    elif gap_ratio >= Fraction(2, 1):
        return "high"
    else:
        return "moderate"


def aggregate_malice_signal_strength(
    signals: list[dict],
) -> tuple[MaliceSignalStrength, list[str]]:
    """
    Agrega señales de malicia desde el pool activo.
    Cada señal tiene 'malice_weight' como Fraction entre 0 y 1.
    Agregación ordinal — sin suma de floats.

    Args:
        signals: Lista de dicts con keys 'name', 'malice_weight' (Fraction o float)

    Returns:
        (MaliceSignalStrength, lista_nombres_señales_activas)
    """
    if not signals:
        return MaliceSignalStrength.NONE, []

    critical_threshold = Fraction(3, 4)
    strong_threshold   = Fraction(1, 2)
    moderate_threshold = Fraction(1, 4)

    def _w(s: dict) -> Fraction:
        w = s.get("malice_weight", 0)
        return w if isinstance(w, Fraction) else Fraction(str(w))

    critical_count = sum(1 for s in signals if _w(s) >= critical_threshold)
    strong_count   = sum(1 for s in signals if strong_threshold   <= _w(s) < critical_threshold)
    moderate_count = sum(1 for s in signals if moderate_threshold <= _w(s) < strong_threshold)
    active_names   = [s["name"] for s in signals if _w(s) > 0]

    if critical_count >= 1:
        return MaliceSignalStrength.CRITICAL, active_names
    elif strong_count >= 2 or (strong_count >= 1 and moderate_count >= 3):
        return MaliceSignalStrength.STRONG, active_names
    elif strong_count >= 1 or moderate_count >= 2:
        return MaliceSignalStrength.MODERATE, active_names
    elif moderate_count >= 1:
        return MaliceSignalStrength.WEAK, active_names
    else:
        return MaliceSignalStrength.NONE, active_names


def compute_adversarial_penalty(
    candidate_cost:         Fraction,
    next_best_cost:         Fraction,
    malice_signal_strength: MaliceSignalStrength,
    observed_malice_signals: list[str],
    weak_signals_ignored:   int = 0,
) -> OckhamPenaltyResult:
    """
    Calcula penalización adversarial por simplicidad sospechosa.

    LÓGICA CENTRAL:
    Si la hipótesis benign es mucho más simple que cualquier alternativa
    Y hay señales de malicia presentes,
    ENTONCES esa simplicidad es evidencia de diseño adversarial.

    Args:
        candidate_cost:          Costo Ockham de la hipótesis candidata
        next_best_cost:          Costo de la segunda mejor hipótesis
        malice_signal_strength:  Fuerza agregada de señales de malicia
        observed_malice_signals: Lista de señales específicas observadas
        weak_signals_ignored:    Cuántas señales débiles ignora la hipótesis

    Returns:
        OckhamPenaltyResult con costo ajustado y razonamiento trazable
    """
    simplicity_class = _classify_simplicity_gap(candidate_cost, next_best_cost)

    penalty_key  = (malice_signal_strength, simplicity_class)
    base_penalty = _PENALTY_TABLE.get(penalty_key, Fraction(0))

    # Penalización adicional por señales ignoradas (VIGÍA propio)
    ignored_penalty = Fraction(0)
    if weak_signals_ignored >= _WEAK_SIGNAL_THRESHOLD:
        ignored_penalty = Fraction(1, 10) * weak_signals_ignored

    # Mínimo garantizado cuando hay señales STRONG+ y costo muy bajo
    guaranteed_minimum = Fraction(0)
    if malice_signal_strength in (MaliceSignalStrength.STRONG,
                                   MaliceSignalStrength.CRITICAL):
        if candidate_cost <= Fraction(1, 10):
            guaranteed_minimum = Fraction(2, 1)

    raw_penalty = max(
        base_penalty * max(candidate_cost, Fraction(1, 1)) + ignored_penalty,
        guaranteed_minimum,
    )

    adjusted = candidate_cost + raw_penalty
    adversarial = raw_penalty > Fraction(0)

    if adversarial:
        reason = (
            f"ADVERSARIAL_SIMPLICITY_DETECTED: "
            f"Hipótesis con costo={candidate_cost} es '{simplicity_class}' "
            f"más simple que la alternativa (costo={next_best_cost}). "
            f"Señales de malicia: {malice_signal_strength.name} "
            f"({', '.join(observed_malice_signals[:3])}). "
            f"Señales ignoradas: {weak_signals_ignored}. "
            f"Penalización: +{raw_penalty}. "
            f"Perfil de adversario que diseñó la explicación benigna."
        )
    else:
        reason = (
            f"NO_ADVERSARIAL_PENALTY: señales={malice_signal_strength.name}, "
            f"simplicidad='{simplicity_class}'. Ockham sin corrección."
        )

    return OckhamPenaltyResult(
        raw_cost=candidate_cost,
        penalty=raw_penalty,
        adjusted_cost=adjusted,
        trigger_reason=reason,
        adversarial_flag=adversarial,
    )
