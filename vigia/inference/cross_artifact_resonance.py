"""
vigia/engine/cross_artifact_resonance.py

Analiza resonancia entre artefactos cross-source.
Detecta cuando múltiples artefactos "resuenan" (correlacionan) de forma
que sugiere un fenómeno subyacente único.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Set, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

TOOL_NAME = "CROSS_RESONANCE"
ARTIFACT_RELIABILITY = Fraction(80, 100)


@dataclass
class ResonancePattern:
    pattern_id: str
    sources: List[str]
    resonance_score: Fraction
    temporal_coherence: Fraction
    semantic_coherence: Fraction
    description: str


@dataclass
class ResonanceResult:
    patterns: List[ResonancePattern]
    total_resonance: Fraction
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.patterns:
            max_res = max(p.resonance_score for p in self.patterns)
            z = Fraction(35, 10) if max_res >= Fraction(9, 10) else Fraction(25, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "pattern_count": len(self.patterns),
                "total_resonance": str(self.total_resonance),
                "artifact_type": "resonance",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    p.pattern_id for p in self.patterns
                ))),
            }
        )


class CrossArtifactResonance:
    """
    Detecta resonancia entre artefactos de diferentes fuentes.

    Ejemplo: Un proceso aparece en memoria (malfind), en registry (Run key),
    y en logs (Event ID 4688) — esto "resuena" como un patrón de persistencia.
    """

    def analyze(self, signals: List[SignalOutput]) -> ResonanceResult:
        """
        Analiza señales buscando patrones de resonancia cross-source.
        """
        if len(signals) < 2:
            return ResonanceResult(
                patterns=[], total_resonance=Fraction(0, 1), composite_score=Fraction(0, 1),
            )

        patterns: List[ResonancePattern] = []

        # Resonancia 1: Persistencia completa
        # Memory (proceso inyectado) + Registry (Run key) + EventLog (ejecución)
        mem_signals = [s for s in signals if s.metadata.get("artifact_type") == "memory"]
        reg_signals = [s for s in signals if s.metadata.get("artifact_type") == "registry"]
        ev_signals = [s for s in signals if s.metadata.get("artifact_type") == "event_log"]

        if mem_signals and reg_signals and ev_signals:
            resonance = self._calculate_triple_resonance(
                mem_signals[0], reg_signals[0], ev_signals[0]
            )
            if resonance >= Fraction(5, 10):
                patterns.append(ResonancePattern(
                    pattern_id="COMPLETE_PERSISTENCE",
                    sources=["memory", "registry", "event_log"],
                    resonance_score=resonance,
                    temporal_coherence=self._temporal_coherence([mem_signals[0], reg_signals[0], ev_signals[0]]),
                    semantic_coherence=Fraction(9, 10),
                    description="Proceso inyectado + persistencia en registry + ejecución loggeada",
                ))

        # Resonancia 2: Exfiltración híbrida
        # Network (beaconing) + USB (dispositivo conectado) + Disk (archivos copiados)
        net_signals = [s for s in signals if s.metadata.get("artifact_type") == "network"]
        usb_signals = [s for s in signals if s.metadata.get("artifact_type") == "usb"]
        disk_signals = [s for s in signals if s.metadata.get("artifact_type") == "mft"]

        if net_signals and usb_signals:
            resonance = self._calculate_dual_resonance(net_signals[0], usb_signals[0])
            if resonance >= Fraction(6, 10):
                patterns.append(ResonancePattern(
                    pattern_id="HYBRID_EXFILTRATION",
                    sources=["network", "usb"],
                    resonance_score=resonance,
                    temporal_coherence=self._temporal_coherence([net_signals[0], usb_signals[0]]),
                    semantic_coherence=Fraction(85, 100),
                    description="Actividad de red sospechosa + dispositivo USB conectado",
                ))

        # Resonancia 3: Anti-forense
        # EventLog (log borrado) + Disk (timestomping) + Registry (LastWrite manipulado)
        if any(s.metadata.get("artifact_type") == "event_log" and s.z_score > 2.0 for s in signals):
            if any(s.metadata.get("artifact_type") == "mft" and s.z_score > 2.0 for s in signals):
                patterns.append(ResonancePattern(
                    pattern_id="ANTI_FORENSIC_CAMPAIGN",
                    sources=["event_log", "mft"],
                    resonance_score=Fraction(88, 100),
                    temporal_coherence=Fraction(9, 10),
                    semantic_coherence=Fraction(95, 100),
                    description="Borrado de logs + manipulación de timestamps = anti-forense coordinado",
                ))

        total_res = sum(p.resonance_score for p in patterns)
        composite = min(total_res, Fraction(95, 100))

        return ResonanceResult(
            patterns=patterns,
            total_resonance=total_res,
            composite_score=composite,
        )

    def _calculate_triple_resonance(self, a: SignalOutput, b: SignalOutput, c: SignalOutput) -> Fraction:
        """Calcula resonancia entre tres señales."""
        # Resonancia = producto de z_scores normalizado
        z_a = Fraction(int(round(a.z_score * 100)), 100)
        z_b = Fraction(int(round(b.z_score * 100)), 100)
        z_c = Fraction(int(round(c.z_score * 100)), 100)

        product = z_a * z_b * z_c
        # Normalizar: máximo teórico = 3.5^3 = 42.875
        max_theoretical = Fraction(42875, 1000)
        return min(product / max_theoretical, Fraction(1, 1))

    def _calculate_dual_resonance(self, a: SignalOutput, b: SignalOutput) -> Fraction:
        """Calcula resonancia entre dos señales."""
        z_a = Fraction(int(round(a.z_score * 100)), 100)
        z_b = Fraction(int(round(b.z_score * 100)), 100)

        product = z_a * z_b
        max_theoretical = Fraction(1225, 100)  # 3.5^2
        return min(product / max_theoretical, Fraction(1, 1))

    def _temporal_coherence(self, signals: List[SignalOutput]) -> Fraction:
        """Calcula coherencia temporal: qué tan cercanos están los timestamps."""
        from vigia.sift._math_utils import _parse_iso_timestamp

        timestamps = []
        for s in signals:
            ts_str = s.metadata.get("timestamp", "1970-01-01T00:00:00Z")
            ts = _parse_iso_timestamp(ts_str)
            timestamps.append(ts)

        if len(timestamps) < 2:
            return Fraction(1, 1)

        max_diff = max(timestamps) - min(timestamps)
        # Coherencia = 1 / (1 + diff_en_minutos)
        diff_minutes = Fraction(max_diff, 60)
        coherence = Fraction(1, 1) / (Fraction(1, 1) + diff_minutes)
        return min(coherence, Fraction(1, 1))
