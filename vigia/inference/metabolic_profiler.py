"""
vigia/engine/metabolic_profiler.py

Perfil metabólico del sistema: analiza el "ritmo" de actividad del sistema
para detectar desviaciones comportamentales.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
FIX P0: Todos los cálculos internos usan Fraction. Conversión a float solo
en el constructor de SignalOutput (inevitable por API).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

TOOL_NAME = "METABOLIC_PROFILER"
ARTIFACT_RELIABILITY = Fraction(75, 100)


@dataclass
class MetabolicProfile:
    baseline_entropy: Fraction
    activity_frequency: Fraction
    burst_pattern: Fraction
    rest_pattern: Fraction
    anomaly_score: Fraction


@dataclass
class MetabolicAnalysisResult:
    profile: MetabolicProfile
    deviations: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.profile.anomaly_score >= Fraction(8, 10):
            z = Fraction(30, 10)
        elif self.profile.anomaly_score >= Fraction(5, 10):
            z = Fraction(20, 10)
        elif self.deviations:
            z = Fraction(15, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "baseline_entropy": str(self.profile.baseline_entropy),
                "activity_frequency": str(self.profile.activity_frequency),
                "burst_pattern": str(self.profile.burst_pattern),
                "rest_pattern": str(self.profile.rest_pattern),
                "anomaly_score": str(self.profile.anomaly_score),
                "deviation_count": len(self.deviations),
                "artifact_type": "behavioral",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    d.get("type", "UNKNOWN") for d in self.deviations
                ))),
            }
        )


class MetabolicProfiler:
    """
    Analiza el metabolismo del sistema: frecuencia de eventos, patrones de
    actividad/reposo, y entropía del comportamiento.
    """

    def analyze(
        self,
        event_stream: List[Dict[str, Any]],
        window_seconds: int = 3600,
    ) -> MetabolicAnalysisResult:
        """
        Analiza un stream de eventos y construye perfil metabólico.

        Args:
            event_stream: Lista de eventos con 'timestamp' (int, epoch seconds)
            window_seconds: Ventana de análisis en segundos
        """
        if not event_stream:
            return MetabolicAnalysisResult(
                profile=MetabolicProfile(
                    baseline_entropy=Fraction(0, 1),
                    activity_frequency=Fraction(0, 1),
                    burst_pattern=Fraction(0, 1),
                    rest_pattern=Fraction(0, 1),
                    anomaly_score=Fraction(0, 1),
                ),
                deviations=[],
                composite_score=Fraction(0, 1),
            )

        # Ordenar por timestamp
        sorted_events = sorted(event_stream, key=lambda e: e.get("timestamp", 0))
        timestamps = [e.get("timestamp", 0) for e in sorted_events]

        if len(timestamps) < 2:
            return MetabolicAnalysisResult(
                profile=MetabolicProfile(
                    baseline_entropy=Fraction(0, 1),
                    activity_frequency=Fraction(0, 1),
                    burst_pattern=Fraction(0, 1),
                    rest_pattern=Fraction(0, 1),
                    anomaly_score=Fraction(0, 1),
                ),
                deviations=[],
                composite_score=Fraction(0, 1),
            )

        # Calcular intervalos
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]

        # Entropía de baseline (variabilidad de intervalos)
        from vigia.sift._math_utils import _entropy_shannon
        # FIX P2: Pasar lista directa
        entropy = _entropy_shannon(intervals)

        # Frecuencia de actividad (eventos por ventana)
        total_time = max(timestamps) - min(timestamps)
        if total_time > 0:
            freq = Fraction(len(timestamps), total_time) * Fraction(window_seconds, 1)
        else:
            freq = Fraction(0, 1)

        # Patrón de burst (clustering de eventos)
        burst_score = self._calculate_burst_pattern(intervals)

        # Patrón de reposo (periodos de inactividad largos)
        rest_score = self._calculate_rest_pattern(intervals)

        # Score de anomalía: desviación del comportamiento baseline
        # Un sistema comprometido suele tener:
        # - Menor entropía (más predecible)
        # - Mayor burst (actividad concentrada)
        # - Menor reposo (siempre activo) o mayor reposo (dormido por backdoor)
        anomaly = self._calculate_anomaly(entropy, burst_score, rest_score)

        # Detectar desviaciones
        deviations = []
        if entropy < Fraction(2, 1):
            deviations.append({
                "type": "LOW_ENTROPY_BEHAVIOR",
                "entropy": str(entropy),
                "severity": str(Fraction(75, 100)),
                "description": "Comportamiento del sistema demasiado predecible",
            })
        if burst_score > Fraction(8, 10):
            deviations.append({
                "type": "BURST_ACTIVITY",
                "burst_score": str(burst_score),
                "severity": str(Fraction(70, 100)),
                "description": "Actividad concentrada en bursts (posible ataque automatizado)",
            })
        if rest_score > Fraction(9, 10):
            deviations.append({
                "type": "EXTENDED_DORMANCY",
                "rest_score": str(rest_score),
                "severity": str(Fraction(65, 100)),
                "description": "Periodos de inactividad inusualmente largos",
            })

        composite = min(
            sum(Fraction(d["severity"]) for d in deviations),
            Fraction(95, 100)
        ) if deviations else Fraction(0, 1)

        return MetabolicAnalysisResult(
            profile=MetabolicProfile(
                baseline_entropy=entropy,
                activity_frequency=freq,
                burst_pattern=burst_score,
                rest_pattern=rest_score,
                anomaly_score=anomaly,
            ),
            deviations=deviations,
            composite_score=composite,
        )

    def _calculate_burst_pattern(self, intervals: List[int]) -> Fraction:
        """Calcula score de burst: 0 (uniforme) a 1 (totalmente burst)."""
        if not intervals:
            return Fraction(0, 1)

        mean = Fraction(sum(intervals), len(intervals))
        if mean == 0:
            return Fraction(0, 1)

        # Coeficiente de variación inverso: CV bajo = uniforme, CV alto = burst
        variance = Fraction(sum((Fraction(i) - mean) ** 2 for i in intervals), len(intervals))
        from vigia.sift._math_utils import _sqrt_fraction
        std = _sqrt_fraction(variance)
        cv = std / mean if mean > 0 else Fraction(0, 1)

        # Normalizar: burst_score = 1 - (1 / (1 + cv))
        burst = Fraction(1, 1) - (Fraction(1, 1) / (Fraction(1, 1) + cv))
        return min(burst, Fraction(1, 1))

    def _calculate_rest_pattern(self, intervals: List[int]) -> Fraction:
        """Calcula score de reposo: proporción de intervalos largos (>5 min)."""
        if not intervals:
            return Fraction(0, 1)

        long_intervals = sum(1 for i in intervals if i > 300)
        return Fraction(long_intervals, len(intervals))

    def _calculate_anomaly(self, entropy: Fraction, burst: Fraction, rest: Fraction) -> Fraction:
        """Calcula score compuesto de anomalía metabólica."""
        # Peso: entropía baja es más anómala que burst alto
        entropy_factor = (Fraction(47, 10) - entropy) / Fraction(47, 10)  # Normalizado
        burst_factor = burst
        rest_factor = rest * Fraction(5, 10)  # Reposo menos anómalo

        return min(
            entropy_factor * Fraction(5, 10) + 
            burst_factor * Fraction(3, 10) + 
            rest_factor * Fraction(2, 10),
            Fraction(1, 1)
        )
