"""
vigia/abduction/hypothesis_lineage.py
=======================================
Árbol genealógico de hipótesis durante el ciclo abductivo de VIGÍA.

El analista SANS ve no solo el veredicto final sino el "mapa de alternativas":
qué evidencia adicional cambiaría el veredicto y hacia dónde.

Implementación completa de los stubs del documento original.

Invariantes:
- HypothesisNode es frozen dataclass
- Todos los costs son Fraction
- audit_hash determinista desde traza completa
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional


@dataclass(frozen=True)
class HypothesisNode:
    hypothesis_id:      str
    hypothesis_name:    str
    verdict:            str           # BENIGN | MALICE | ABSTAIN
    iteration:          int
    cost_ockham:        Fraction
    cost_adversarial:   Fraction
    cost_final:         Fraction
    signals_covered:    frozenset[str]
    signals_ignored:    frozenset[str]
    parent_id:          Optional[str] = None
    elimination_reason: Optional[str] = None


@dataclass(frozen=True)
class PivotSignal:
    """Señal cuya presencia o ausencia cambiaría el veredicto."""
    signal_name:     str
    current_state:   str        # "present" | "absent" | "unknown"
    if_found:        str        # Veredicto si se encontrara
    if_not_found:    str        # Veredicto si se confirmara ausencia
    confidence_delta: Fraction  # Cuánto cambiaría la confianza


@dataclass
class LineageReport:
    winner:               HypothesisNode
    verdict_stability:    Fraction
    near_misses:          list[HypothesisNode]
    pivot_signals:        list[PivotSignal]
    investigation_roadmap: list[str]
    audit_hash:           str


class HypothesisLineageTracker:
    """
    Registra el ciclo abductivo completo para trazabilidad Daubert.
    """

    def __init__(self) -> None:
        self._nodes: list[HypothesisNode] = []

    def record(
        self,
        hypothesis_id:    str,
        hypothesis_name:  str,
        verdict:          str,
        iteration:        int,
        cost_ockham:      Fraction,
        cost_adversarial: Fraction,
        cost_final:       Fraction,
        signals_covered:  frozenset[str],
        signals_ignored:  frozenset[str],
        parent_id:        Optional[str] = None,
        elimination_reason: Optional[str] = None,
    ) -> None:
        """Registra una hipótesis en el árbol."""
        self._nodes.append(HypothesisNode(
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            verdict=verdict,
            iteration=iteration,
            cost_ockham=cost_ockham,
            cost_adversarial=cost_adversarial,
            cost_final=cost_final,
            signals_covered=signals_covered,
            signals_ignored=signals_ignored,
            parent_id=parent_id,
            elimination_reason=elimination_reason,
        ))

    def finalize(self, winner_id: str) -> LineageReport:
        """
        Cierra el ciclo abductivo y produce el reporte de linaje.

        Args:
            winner_id: hypothesis_id de la hipótesis ganadora

        Returns:
            LineageReport con near-misses, pivot signals y roadmap
        """
        if not self._nodes:
            raise ValueError("No hay hipótesis registradas")

        # Encontrar ganadora
        winner_nodes = [n for n in self._nodes if n.hypothesis_id == winner_id]
        if not winner_nodes:
            raise ValueError(f"Hipótesis ganadora no encontrada: {winner_id}")
        winner = winner_nodes[-1]  # Última versión si hubo iteraciones

        # Near misses: hipótesis con cost_final dentro del 20% del ganador
        threshold = Fraction(1, 5)
        near_misses = [
            n for n in self._nodes
            if n.hypothesis_id != winner_id
            and n.cost_final > Fraction(0)
            and abs(n.cost_final - winner.cost_final) / max(winner.cost_final, Fraction(1, 100)) <= threshold
        ]
        # Ordenar por cercanía al ganador
        near_misses.sort(key=lambda n: abs(n.cost_final - winner.cost_final))

        # Verdict stability: proporción de iteraciones donde el ganador era líder
        winner_iterations = sum(1 for n in self._nodes if n.hypothesis_id == winner_id)
        total_iterations = len(set(n.iteration for n in self._nodes))
        verdict_stability = (
            Fraction(winner_iterations, total_iterations)
            if total_iterations > 0
            else Fraction(1)
        )

        # Pivot signals: señales ignoradas por el ganador que podrían cambiar veredicto
        pivot_signals = _compute_pivot_signals(winner, self._nodes)

        # Investigation roadmap
        roadmap = _build_roadmap(winner, near_misses, pivot_signals)

        audit_hash = _compute_lineage_hash(self._nodes, winner_id)

        return LineageReport(
            winner=winner,
            verdict_stability=verdict_stability,
            near_misses=near_misses,
            pivot_signals=pivot_signals,
            investigation_roadmap=roadmap,
            audit_hash=audit_hash,
        )


def _compute_pivot_signals(
    winner: HypothesisNode,
    all_nodes: list[HypothesisNode],
) -> list[PivotSignal]:
    """
    Identifica señales cuya presencia cambiaría el veredicto.
    Se basa en las señales ignoradas por el ganador que otros candidatos cubrían.
    """
    pivots: list[PivotSignal] = []

    # Señales ignoradas por el ganador
    ignored = winner.signals_ignored

    # Ver qué hipótesis alternativas cubrían esas señales
    for signal in ignored:
        covering_alternatives = [
            n for n in all_nodes
            if n.hypothesis_id != winner.hypothesis_id
            and signal in n.signals_covered
        ]

        if not covering_alternatives:
            continue

        # La alternativa más cercana al ganador
        best_alt = min(covering_alternatives, key=lambda n: n.cost_final)

        # Delta de confianza: cuánto cambiaría el costo si se encontrara la señal
        cost_delta = best_alt.cost_final - winner.cost_final
        confidence_delta = min(abs(cost_delta), Fraction(1))

        pivots.append(PivotSignal(
            signal_name=signal,
            current_state="absent",
            if_found=best_alt.verdict,
            if_not_found=winner.verdict,
            confidence_delta=confidence_delta,
        ))

    # Ordenar por impacto potencial
    pivots.sort(key=lambda p: p.confidence_delta, reverse=True)
    return pivots[:5]  # Top 5 señales pivot


def _build_roadmap(
    winner: HypothesisNode,
    near_misses: list[HypothesisNode],
    pivot_signals: list[PivotSignal],
) -> list[str]:
    """
    Genera roadmap de investigación para el analista SANS.
    """
    roadmap: list[str] = []

    # Instrucción base
    roadmap.append(
        f"Winning hypothesis: {winner.hypothesis_name} "
        f"(verdict={winner.verdict}, cost={winner.cost_final})"
    )

    # Near misses
    if near_misses:
        roadmap.append(
            f"{len(near_misses)} near-miss hypothesis/hypotheses within 20% cost margin:"
        )
        for nm in near_misses[:3]:
            roadmap.append(
                f"  → {nm.hypothesis_name} (verdict={nm.verdict}, "
                f"cost={nm.cost_final}, "
                f"delta={abs(nm.cost_final - winner.cost_final)})"
            )

    # Pivot signals
    if pivot_signals:
        roadmap.append("Pivot signals — verify these to increase certainty:")
        for ps in pivot_signals:
            roadmap.append(
                f"  → '{ps.signal_name}': "
                f"if found → {ps.if_found}, "
                f"if confirmed absent → {ps.if_not_found} "
                f"(confidence delta: {int(ps.confidence_delta * 100)}%)"
            )

    # Señales ignoradas por el ganador
    if winner.signals_ignored:
        roadmap.append(
            f"Signals not explained by winning hypothesis "
            f"({len(winner.signals_ignored)}):"
        )
        for sig in sorted(winner.signals_ignored)[:5]:
            roadmap.append(f"  → {sig}")

    return roadmap


def _compute_lineage_hash(
    nodes: list[HypothesisNode],
    winner_id: str,
) -> str:
    content = json.dumps(
        {
            "winner_id": winner_id,
            "nodes": [
                {
                    "id":      n.hypothesis_id,
                    "verdict": n.verdict,
                    "cost":    str(n.cost_final),
                    "iter":    n.iteration,
                }
                for n in nodes
            ],
        },
        sort_keys=True,
    )
    return hashlib.sha256(content.encode()).hexdigest()
