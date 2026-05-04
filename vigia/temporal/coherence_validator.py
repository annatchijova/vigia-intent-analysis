"""
vigia/temporal/coherence_validator.py
=======================================
Validador de coherencia temporal para VIGÍA.

Principio: Un atacante que fabrica evidencia viola el reloj de Lamport
porque no tiene acceso al historial completo del sistema.
Timestamps inconsistentes = señal de fabricación.

Implementación completa de los stubs del documento original.

Invariantes:
- Todo scoring usa Fraction — sin floats en lógica de veredicto
- TemporalEvent es frozen dataclass
- audit_hash determinista desde contenido de anomalías
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Optional


class AnomalyType(Enum):
    CAUSALITY_VIOLATION        = "causality_violation"
    ENTITY_PREDATES_EXISTENCE  = "entity_predates_existence"
    TIMEZONE_INCONSISTENCY     = "timezone_inconsistency"
    CLOCK_SKEW_SYSTEMATIC      = "clock_skew_systematic"
    DURATION_IMPOSSIBLE        = "duration_impossible"


class AnomalySeverity(Enum):
    CRITICAL = 4
    HIGH     = 3
    MEDIUM   = 2
    LOW      = 1


@dataclass(frozen=True)
class TemporalEvent:
    event_id:   str
    artifact:   str
    field:      str
    timestamp:  int          # Unix timestamp entero
    timezone:   str
    requires:   frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class TemporalAnomaly:
    artifact_a:          str
    artifact_b:          str
    field_a:             str
    field_b:             str
    timestamp_a:         int
    timestamp_b:         int
    delta_seconds:       int
    anomaly_type:        AnomalyType
    severity:            AnomalySeverity
    forensic_weight:     Fraction
    hard_to_fake:        bool
    description:         str
    investigation_hint:  str


@dataclass
class ValidationResult:
    anomalies:          list[TemporalAnomaly]
    fabrication_signal: Fraction
    coherence_score:    Fraction
    audit_hash:         str
    summary:            str


# Pesos forenses por tipo de anomalía
_ANOMALY_WEIGHTS: dict[AnomalyType, Fraction] = {
    AnomalyType.CAUSALITY_VIOLATION:       Fraction(9, 10),
    AnomalyType.ENTITY_PREDATES_EXISTENCE: Fraction(8, 10),
    AnomalyType.TIMEZONE_INCONSISTENCY:    Fraction(6, 10),
    AnomalyType.CLOCK_SKEW_SYSTEMATIC:     Fraction(7, 10),
    AnomalyType.DURATION_IMPOSSIBLE:       Fraction(8, 10),
}

# Anomalías difíciles de fabricar correctamente
_HARD_TO_FAKE: frozenset[AnomalyType] = frozenset({
    AnomalyType.CAUSALITY_VIOLATION,
    AnomalyType.ENTITY_PREDATES_EXISTENCE,
    AnomalyType.CLOCK_SKEW_SYSTEMATIC,
})


class TemporalCoherenceValidator:
    """
    Construye un grafo de dependencias temporales entre artefactos
    y detecta violaciones de causalidad (Lamport clocks aplicados a forense).
    """

    def __init__(self) -> None:
        self._events: list[TemporalEvent] = []

    def add_event(self, event: TemporalEvent) -> None:
        self._events.append(event)

    def validate(self) -> ValidationResult:
        """
        Valida todos los eventos registrados y retorna anomalías detectadas.
        """
        anomalies: list[TemporalAnomaly] = []

        # Índice por event_id para lookups rápidos
        event_index: dict[str, TemporalEvent] = {e.event_id: e for e in self._events}

        # Validación 1: causalidad (B requiere A → timestamp(A) < timestamp(B))
        for event in self._events:
            for required_id in event.requires:
                if required_id not in event_index:
                    continue
                required = event_index[required_id]
                if event.timestamp <= required.timestamp:
                    # Violación: el dependiente ocurre antes o igual que su prerequisito
                    delta = event.timestamp - required.timestamp
                    anomalies.append(TemporalAnomaly(
                        artifact_a=required.artifact,
                        artifact_b=event.artifact,
                        field_a=required.field,
                        field_b=event.field,
                        timestamp_a=required.timestamp,
                        timestamp_b=event.timestamp,
                        delta_seconds=delta,
                        anomaly_type=AnomalyType.CAUSALITY_VIOLATION,
                        severity=AnomalySeverity.CRITICAL,
                        forensic_weight=_ANOMALY_WEIGHTS[AnomalyType.CAUSALITY_VIOLATION],
                        hard_to_fake=True,
                        description=(
                            f"'{event.event_id}' requiere '{required_id}' "
                            f"pero ocurre {abs(delta)}s antes o simultáneamente. "
                            f"Imposible causalmente."
                        ),
                        investigation_hint=(
                            f"Verificar timestamp de {event.artifact}/{event.field} "
                            f"contra log de {required.artifact}. "
                            f"Un atacante que fabricó {event.artifact} "
                            f"no conocía el timestamp real de {required.artifact}."
                        ),
                    ))

        # Validación 2: inconsistencia de timezone
        tz_events: dict[str, list[TemporalEvent]] = {}
        for event in self._events:
            tz_events.setdefault(event.timezone, []).append(event)

        if len(tz_events) > 1:
            # Múltiples timezones en el mismo incidente es sospechoso
            tzones = list(tz_events.keys())
            # Comparar el primer evento de cada timezone distinta
            base_tz = tzones[0]
            base_event = tz_events[base_tz][0]
            for other_tz in tzones[1:]:
                other_event = tz_events[other_tz][0]
                anomalies.append(TemporalAnomaly(
                    artifact_a=base_event.artifact,
                    artifact_b=other_event.artifact,
                    field_a=base_event.field,
                    field_b=other_event.field,
                    timestamp_a=base_event.timestamp,
                    timestamp_b=other_event.timestamp,
                    delta_seconds=other_event.timestamp - base_event.timestamp,
                    anomaly_type=AnomalyType.TIMEZONE_INCONSISTENCY,
                    severity=AnomalySeverity.MEDIUM,
                    forensic_weight=_ANOMALY_WEIGHTS[AnomalyType.TIMEZONE_INCONSISTENCY],
                    hard_to_fake=False,
                    description=(
                        f"Timezone {base_tz!r} en {base_event.artifact} "
                        f"vs {other_tz!r} en {other_event.artifact}. "
                        f"Un atacante usó su hora local al fabricar uno de los artefactos."
                    ),
                    investigation_hint=(
                        f"Comparar offset UTC de {base_event.artifact} y {other_event.artifact}. "
                        f"La timezone del atacante puede identificar su ubicación geográfica."
                    ),
                ))

        # Validación 3: skew sistemático (todos los eventos del mismo artefacto
        # están desplazados por exactamente el mismo delta)
        artifact_events: dict[str, list[TemporalEvent]] = {}
        for event in self._events:
            artifact_events.setdefault(event.artifact, []).append(event)

        if len(artifact_events) >= 2:
            artifacts = list(artifact_events.keys())
            for i in range(len(artifacts) - 1):
                evs_a = artifact_events[artifacts[i]]
                evs_b = artifact_events[artifacts[i + 1]]
                if len(evs_a) >= 2 and len(evs_b) >= 2:
                    # Calcular deltas internos
                    deltas_a = [evs_a[j+1].timestamp - evs_a[j].timestamp for j in range(len(evs_a)-1)]
                    deltas_b = [evs_b[j+1].timestamp - evs_b[j].timestamp for j in range(len(evs_b)-1)]
                    # Si los deltas son idénticos entre artefactos distintos → copia masiva
                    if deltas_a == deltas_b and len(deltas_a) > 0:
                        anomalies.append(TemporalAnomaly(
                            artifact_a=artifacts[i],
                            artifact_b=artifacts[i+1],
                            field_a="timestamp_sequence",
                            field_b="timestamp_sequence",
                            timestamp_a=evs_a[0].timestamp,
                            timestamp_b=evs_b[0].timestamp,
                            delta_seconds=evs_b[0].timestamp - evs_a[0].timestamp,
                            anomaly_type=AnomalyType.CLOCK_SKEW_SYSTEMATIC,
                            severity=AnomalySeverity.HIGH,
                            forensic_weight=_ANOMALY_WEIGHTS[AnomalyType.CLOCK_SKEW_SYSTEMATIC],
                            hard_to_fake=True,
                            description=(
                                f"Secuencia de timestamps idéntica en {artifacts[i]} "
                                f"y {artifacts[i+1]}. Indica copia masiva de timestamps."
                            ),
                            investigation_hint=(
                                f"Comparar secuencia completa de timestamps entre "
                                f"{artifacts[i]} y {artifacts[i+1]}. "
                                f"Diferencia constante indica timestamp transplantado."
                            ),
                        ))

        # Calcular fabrication_signal y coherence_score
        fabrication_signal, coherence_score = _compute_scores(anomalies)
        audit_hash = _compute_audit_hash(anomalies)
        summary = _build_summary(anomalies, fabrication_signal, coherence_score)

        return ValidationResult(
            anomalies=anomalies,
            fabrication_signal=fabrication_signal,
            coherence_score=coherence_score,
            audit_hash=audit_hash,
            summary=summary,
        )


def _compute_scores(
    anomalies: list[TemporalAnomaly],
) -> tuple[Fraction, Fraction]:
    """Calcula fabrication_signal y coherence_score desde lista de anomalías."""
    if not anomalies:
        return Fraction(0), Fraction(1)

    # Fabrication signal: suma ponderada de pesos forenses, saturada a 1
    total_weight = sum(a.forensic_weight for a in anomalies)
    # Penalizar más si hay anomalías hard_to_fake
    hard_count = sum(1 for a in anomalies if a.hard_to_fake)
    if hard_count > 0:
        total_weight = min(total_weight + Fraction(hard_count, 10), Fraction(1))
    fabrication_signal = min(total_weight, Fraction(1))

    # Coherence score: inverso de la señal de fabricación
    coherence_score = Fraction(1) - fabrication_signal
    if coherence_score < Fraction(0):
        coherence_score = Fraction(0)

    return fabrication_signal, coherence_score


def _compute_audit_hash(anomalies: list[TemporalAnomaly]) -> str:
    content = json.dumps(
        [
            {
                "artifact_a": a.artifact_a,
                "artifact_b": a.artifact_b,
                "delta": a.delta_seconds,
                "type": a.anomaly_type.value,
                "weight": str(a.forensic_weight),
            }
            for a in anomalies
        ],
        sort_keys=True,
    )
    return hashlib.sha256(content.encode()).hexdigest()


def _build_summary(
    anomalies: list[TemporalAnomaly],
    fabrication_signal: Fraction,
    coherence_score: Fraction,
) -> str:
    if not anomalies:
        return "Temporal coherence validated. No anomalies detected."

    critical = [a for a in anomalies if a.severity == AnomalySeverity.CRITICAL]
    hard = [a for a in anomalies if a.hard_to_fake]

    parts = [
        f"{len(anomalies)} temporal anomaly/anomalies detected.",
        f"Fabrication signal: {int(fabrication_signal * 100)}%.",
        f"Coherence score: {int(coherence_score * 100)}%.",
    ]
    if critical:
        parts.append(
            f"{len(critical)} CRITICAL anomaly/anomalies (causality violations)."
        )
    if hard:
        parts.append(
            f"{len(hard)} anomaly/anomalies are hard to fake — "
            f"strong indicator of evidence fabrication."
        )
    return " ".join(parts)
