"""
vigia/core/peirceplanner_bounded.py
=====================================
PeircePlanner con límite de Miller (N=7) y detección de oscilación para VIGÍA.

Principio: El razonamiento abductivo sin límite puede oscilar infinitamente
entre hipótesis contradictorias o sobreajustarse a ruido. El límite de Miller
(7±2, George Miller 1956) formaliza el límite cognitivo humano que un perito
forense aplica instintivamente.

Condiciones de parada (en orden):
1. Cobertura completa de señales
2. Convergencia Ockham (costo estable entre iteraciones)
3. Oscilación detectada A→B→A (ABSTAIN — evidencia contradictoria)
4. Límite duro de Miller: 7 iteraciones

Kimi fix aplicado:
- display usa int(confidence * 100) — nunca round()
- PlannerResult.display_confidence_pct() para reportes

Invariantes:
- Todos los costos son Fraction
- OscillationDetector es determinista con ventana fija
- audit_hash generado de la traza completa
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Callable, Optional

# Límite de Miller — 7 iteraciones máximas
MILLER_LIMIT: int = 7


class PlannerTerminationReason(Enum):
    SIGNAL_COVERAGE      = "signal_coverage"
    OCKHAM_CONVERGENCE   = "ockham_convergence"
    OSCILLATION_DETECTED = "oscillation_detected"
    MILLER_LIMIT_REACHED = "miller_limit_reached"
    HYPOTHESIS_EXHAUSTED = "hypothesis_exhausted"


class HypothesisStatus(Enum):
    ACTIVE    = "active"
    CONFIRMED = "confirmed"
    DISCARDED = "discarded"
    SUSPENDED = "suspended"


@dataclass
class EvidenceSignal:
    signal_id:   str
    description: str
    weight:      Fraction
    explained_by: Optional[str] = None


@dataclass
class Hypothesis:
    hypothesis_id:     str
    description:       str
    ockham_cost:       Fraction
    verdict:           str = "UNKNOWN"    # BENIGN | MALICE | ABSTAIN
    status:            HypothesisStatus = HypothesisStatus.ACTIVE
    signals_explained: list[str] = field(default_factory=list)
    iteration_created: int = 0
    iteration_discarded: Optional[int] = None

    def digest(self) -> str:
        """Hash determinista de la hipótesis para detección de ciclos."""
        content = f"{self.hypothesis_id}|{self.ockham_cost}|{sorted(self.signals_explained)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class PlannerIteration:
    iteration_number:         int
    active_hypothesis_id:     str
    ockham_cost:              Fraction
    signals_covered:          int
    signals_total:            int
    action:                   str
    new_hypotheses_generated: list[str] = field(default_factory=list)
    discarded_hypotheses:     list[str] = field(default_factory=list)


@dataclass
class PlannerResult:
    winning_hypothesis:  Optional[Hypothesis]
    termination_reason:  PlannerTerminationReason
    iterations_used:     int
    iterations_trace:    list[PlannerIteration]
    oscillation_detected: bool
    oscillation_pattern: Optional[str]
    uncovered_signals:   list[str]
    forensic_verdict:    str
    audit_hash:          str

    def display_confidence_pct(self) -> int:
        """Kimi fix: int() truncado, nunca round()."""
        if self.winning_hypothesis is None:
            return 0
        # Confianza inversa al costo normalizado
        max_cost = Fraction(5, 1)
        clamped  = min(self.winning_hypothesis.ockham_cost, max_cost)
        raw      = Fraction(1) - (clamped / max_cost)
        return int(raw * 100)

    def to_report(self) -> str:
        lines = [
            "═" * 62,
            "              ABDUCTIVE REASONING TRACE",
            "═" * 62,
            f"TERMINATION: {self.termination_reason.value}",
            f"ITERATIONS:  {self.iterations_used} / {MILLER_LIMIT}",
            f"CONFIDENCE:  {self.display_confidence_pct()}%",
            f"VERDICT:     {self.forensic_verdict[:120]}",
        ]
        if self.oscillation_detected:
            lines += [
                "",
                "⚠  OSCILLATION DETECTED",
                f"   Pattern: {self.oscillation_pattern}",
                "   Contradictory evidence — manual review required.",
            ]
        if self.uncovered_signals:
            lines += [
                "",
                f"UNCOVERED SIGNALS ({len(self.uncovered_signals)}):",
            ] + [f"  • {s}" for s in self.uncovered_signals]
        lines.append("═" * 62)
        return "\n".join(lines)


# ─── Oscillation detector ─────────────────────────────────────────────────────

class OscillationDetector:
    """
    Detecta el patrón A→B→A en la secuencia de hipótesis ganadoras.
    Ventana deslizante determinista.
    """

    def __init__(self, window_size: int = 4):
        self._window = window_size
        self._history: list[str] = []

    def record(self, hypothesis_id: str) -> None:
        self._history.append(hypothesis_id)
        if len(self._history) > self._window * 2:
            self._history = self._history[-(self._window * 2):]

    def detect(self) -> tuple[bool, Optional[str]]:
        h = self._history
        n = len(h)

        if n < 3:
            return False, None

        # Patrón directo A→B→A
        if h[-3] == h[-1] and h[-2] != h[-1]:
            return True, f"{h[-3]}→{h[-2]}→{h[-1]}"

        # Patrón extendido A→B→C→A→B→C
        if n >= 6:
            first  = h[-6:-3]
            second = h[-3:]
            if first == second:
                pattern = "→".join(first) + "→" + "→".join(second)
                return True, f"LONG_CYCLE:{pattern}"

        return False, None


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _signal_coverage(
    hypothesis: Hypothesis,
    signals:    list[EvidenceSignal],
) -> Fraction:
    """Fracción ponderada de señales cubiertas por la hipótesis."""
    total = sum(s.weight for s in signals)
    if total == Fraction(0):
        return Fraction(0)
    covered = sum(s.weight for s in signals if s.signal_id in hypothesis.signals_explained)
    return covered / total


def _select_best(
    hypotheses: list[Hypothesis],
    signals:    list[EvidenceSignal],
) -> Optional[Hypothesis]:
    """
    Selecciona hipótesis con mejor ratio cobertura/costo.
    score = coverage × (1 − normalized_cost)
    Todo en Fraction.
    """
    active = [h for h in hypotheses if h.status == HypothesisStatus.ACTIVE]
    if not active:
        return None

    max_cost = max(h.ockham_cost for h in active) or Fraction(1)

    def score(h: Hypothesis) -> Fraction:
        cov  = _signal_coverage(h, signals)
        norm = h.ockham_cost / max_cost if max_cost > 0 else Fraction(0)
        return cov * (Fraction(1) - norm)

    return max(active, key=score)


# ─── Main planner ─────────────────────────────────────────────────────────────

def run_bounded_planner(
    initial_hypotheses:        list[Hypothesis],
    signals:                   list[EvidenceSignal],
    hypothesis_generator:      Optional[Callable[[Hypothesis, list[EvidenceSignal]], list[Hypothesis]]] = None,
    miller_limit:              int = MILLER_LIMIT,
    ockham_convergence_delta:  Fraction = Fraction(1, 100),
) -> PlannerResult:
    """
    Motor de abducción con límite de Miller y detección de oscilación.

    hypothesis_generator: función que genera nuevas hipótesis desde la actual
                          y las señales no explicadas. Opcional.
    ockham_convergence_delta: si costo entre iteraciones cambia menos que esto,
                              se considera convergido.
    """
    hypotheses         = list(initial_hypotheses)
    osc_detector       = OscillationDetector()
    iterations_trace:  list[PlannerIteration] = []

    prev_best_id:      Optional[str]      = None
    prev_ockham_cost:  Optional[Fraction] = None
    oscillation_detected = False
    oscillation_pattern: Optional[str] = None
    termination_reason: Optional[PlannerTerminationReason] = None
    winning_hypothesis: Optional[Hypothesis] = None

    for iteration in range(1, miller_limit + 1):

        best = _select_best(hypotheses, signals)
        if best is None:
            termination_reason = PlannerTerminationReason.HYPOTHESIS_EXHAUSTED
            break

        osc_detector.record(best.hypothesis_id)
        is_oscillating, pattern = osc_detector.detect()

        if is_oscillating:
            oscillation_detected = True
            oscillation_pattern  = pattern
            # Suspender hipótesis que causó oscilación
            if prev_best_id:
                for h in hypotheses:
                    if h.hypothesis_id == prev_best_id:
                        h.status = HypothesisStatus.SUSPENDED
                        h.iteration_discarded = iteration
                        break
            best = _select_best(hypotheses, signals)
            if best is None:
                termination_reason = PlannerTerminationReason.OSCILLATION_DETECTED
                break

        # Convergencia Ockham
        if (prev_ockham_cost is not None
                and abs(best.ockham_cost - prev_ockham_cost) < ockham_convergence_delta
                and best.hypothesis_id == prev_best_id):
            termination_reason = PlannerTerminationReason.OCKHAM_CONVERGENCE
            winning_hypothesis = best
            iterations_trace.append(PlannerIteration(
                iteration_number=iteration,
                active_hypothesis_id=best.hypothesis_id,
                ockham_cost=best.ockham_cost,
                signals_covered=len(best.signals_explained),
                signals_total=len(signals),
                action=f"CONVERGENCE: delta < {ockham_convergence_delta}",
            ))
            break

        # Cobertura completa
        coverage = _signal_coverage(best, signals)
        if coverage == Fraction(1):
            termination_reason = PlannerTerminationReason.SIGNAL_COVERAGE
            winning_hypothesis = best
            iterations_trace.append(PlannerIteration(
                iteration_number=iteration,
                active_hypothesis_id=best.hypothesis_id,
                ockham_cost=best.ockham_cost,
                signals_covered=len(best.signals_explained),
                signals_total=len(signals),
                action="FULL_COVERAGE: all signals explained",
            ))
            break

        # Generar nuevas hipótesis
        new_ids:     list[str] = []
        discarded:   list[str] = []

        if hypothesis_generator and coverage < Fraction(8, 10):
            for h in hypothesis_generator(best, signals):
                h.iteration_created = iteration
                hypotheses.append(h)
                new_ids.append(h.hypothesis_id)

        # Descartar hipótesis dominadas
        for h in hypotheses:
            if h.status != HypothesisStatus.ACTIVE or h.hypothesis_id == best.hypothesis_id:
                continue
            if (_signal_coverage(h, signals) < _signal_coverage(best, signals)
                    and h.ockham_cost > best.ockham_cost):
                h.status = HypothesisStatus.DISCARDED
                h.iteration_discarded = iteration
                discarded.append(h.hypothesis_id)

        iterations_trace.append(PlannerIteration(
            iteration_number=iteration,
            active_hypothesis_id=best.hypothesis_id,
            ockham_cost=best.ockham_cost,
            signals_covered=len(best.signals_explained),
            signals_total=len(signals),
            action=(
                f"OSCILLATION_MITIGATED:{pattern}" if is_oscillating
                else f"ITERATING: coverage={coverage}"
            ),
            new_hypotheses_generated=new_ids,
            discarded_hypotheses=discarded,
        ))

        prev_best_id      = best.hypothesis_id
        prev_ockham_cost  = best.ockham_cost
        winning_hypothesis = best

    else:
        termination_reason = PlannerTerminationReason.MILLER_LIMIT_REACHED

    # Señales no cubiertas
    explained = set(winning_hypothesis.signals_explained) if winning_hypothesis else set()
    uncovered = [s.signal_id for s in signals if s.signal_id not in explained]

    # Veredicto forense
    if termination_reason == PlannerTerminationReason.OSCILLATION_DETECTED:
        forensic_verdict = (
            f"ABSTAIN: Planner oscillated ({oscillation_pattern}). "
            f"Contradictory signals — possible manipulated evidence or "
            f"adversarially designed scenario. Manual review required."
        )
    elif termination_reason == PlannerTerminationReason.MILLER_LIMIT_REACHED:
        cov = _signal_coverage(winning_hypothesis, signals) if winning_hypothesis else Fraction(0)
        forensic_verdict = (
            f"PARTIAL: Miller limit ({miller_limit} iterations) reached. "
            f"Final coverage: {int(cov * 100)}%. "
            f"Uncovered signals: {uncovered}. "
            f"Case exceeds expected complexity — consider segmentation."
        )
    elif winning_hypothesis:
        forensic_verdict = (
            f"RESOLVED via {termination_reason.value}: "
            f"winning={winning_hypothesis.hypothesis_id} "
            f"({winning_hypothesis.description}) "
            f"ockham_cost={winning_hypothesis.ockham_cost} "
            f"in {len(iterations_trace)} iterations."
        )
    else:
        forensic_verdict = "ABSTAIN: No viable hypothesis. Insufficient evidence."

    # Audit hash
    trace_content = "|".join(
        f"{it.iteration_number}:{it.active_hypothesis_id}:{it.ockham_cost}"
        for it in iterations_trace
    )
    audit_hash = hashlib.sha256(trace_content.encode()).hexdigest()

    return PlannerResult(
        winning_hypothesis=winning_hypothesis,
        termination_reason=termination_reason,
        iterations_used=len(iterations_trace),
        iterations_trace=iterations_trace,
        oscillation_detected=oscillation_detected,
        oscillation_pattern=oscillation_pattern,
        uncovered_signals=uncovered,
        forensic_verdict=forensic_verdict,
        audit_hash=audit_hash,
    )
