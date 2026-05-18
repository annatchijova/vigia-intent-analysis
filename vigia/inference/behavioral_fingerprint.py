"""
vigia/engine/behavioral_fingerprint.py

Fingerprint comportamental del sistema.
Crea una "huella digital" del comportamiento normal del sistema para detectar
desviaciones que indican compromiso.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

TOOL_NAME = "BEHAVIORAL_FINGERPRINT"
ARTIFACT_RELIABILITY = Fraction(70, 100)


@dataclass
class BehavioralProfile:
    process_entropy: Fraction
    network_entropy: Fraction
    temporal_entropy: Fraction
    composite_entropy: Fraction


@dataclass
class BehavioralFingerprintResult:
    baseline_profile: BehavioralProfile
    current_profile: BehavioralProfile
    deviation_score: Fraction
    anomalies: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.deviation_score >= Fraction(8, 10):
            z = Fraction(30, 10)
        elif self.deviation_score >= Fraction(5, 10):
            z = Fraction(20, 10)
        elif self.anomalies:
            z = Fraction(15, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "baseline_entropy": str(self.baseline_profile.composite_entropy),
                "current_entropy": str(self.current_profile.composite_entropy),
                "deviation_score": str(self.deviation_score),
                "anomaly_count": len(self.anomalies),
                "artifact_type": "behavioral",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    a.get("type", "UNKNOWN") for a in self.anomalies
                ))),
            }
        )


class BehavioralFingerprint:
    """
    Crea y compara fingerprints comportamentales del sistema.

    Uso:
        1. Entrenar baseline con comportamiento normal
        2. Comparar contra comportamiento actual
        3. Detectar desviaciones significativas
    """

    def __init__(self):
        self._baseline: Optional[BehavioralProfile] = None

    def train_baseline(self, normal_events: List[Dict[str, Any]]) -> BehavioralProfile:
        """Entrena perfil baseline con comportamiento normal."""
        self._baseline = self._compute_profile(normal_events)
        return self._baseline

    def analyze(self, current_events: List[Dict[str, Any]]) -> BehavioralFingerprintResult:
        """Comportamiento actual contra baseline."""
        current = self._compute_profile(current_events)

        if self._baseline is None:
            return BehavioralFingerprintResult(
                baseline_profile=current,
                current_profile=current,
                deviation_score=Fraction(0, 1),
                anomalies=[],
                composite_score=Fraction(0, 1),
            )

        # Calcular desviación
        dev_process = abs(current.process_entropy - self._baseline.process_entropy)
        dev_network = abs(current.network_entropy - self._baseline.network_entropy)
        dev_temporal = abs(current.temporal_entropy - self._baseline.temporal_entropy)

        # Desviación compuesta (peso mayor a process entropy)
        deviation = (
            dev_process * Fraction(5, 10) +
            dev_network * Fraction(3, 10) +
            dev_temporal * Fraction(2, 10)
        )

        anomalies = []
        if dev_process >= Fraction(3, 10):
            anomalies.append({
                "type": "PROCESS_ENTROPY_DEVIATION",
                "baseline": str(self._baseline.process_entropy),
                "current": str(current.process_entropy),
                "severity": str(min(dev_process * Fraction(2, 1), Fraction(95, 100))),
            })
        if dev_network >= Fraction(3, 10):
            anomalies.append({
                "type": "NETWORK_ENTROPY_DEVIATION",
                "baseline": str(self._baseline.network_entropy),
                "current": str(current.network_entropy),
                "severity": str(min(dev_network * Fraction(2, 1), Fraction(95, 100))),
            })
        if dev_temporal >= Fraction(3, 10):
            anomalies.append({
                "type": "TEMPORAL_ENTROPY_DEVIATION",
                "baseline": str(self._baseline.temporal_entropy),
                "current": str(current.temporal_entropy),
                "severity": str(min(dev_temporal * Fraction(2, 1), Fraction(95, 100))),
            })

        composite = min(
            sum(Fraction(a["severity"]) for a in anomalies),
            Fraction(95, 100)
        ) if anomalies else Fraction(0, 1)

        return BehavioralFingerprintResult(
            baseline_profile=self._baseline,
            current_profile=current,
            deviation_score=deviation,
            anomalies=anomalies,
            composite_score=composite,
        )

    def _compute_profile(self, events: List[Dict[str, Any]]) -> BehavioralProfile:
        """Computa perfil comportamental desde eventos."""
        from vigia.sift._math_utils import _entropy_shannon

        # Entropía de procesos (qué procesos corren)
        process_names = [e.get("process_name", "UNKNOWN") for e in events if "process_name" in e]
        # FIX P2: Pasar lista directa
        process_entropy = _entropy_shannon(process_names) if process_names else Fraction(0, 1)

        # Entropía de red (qué IPs/ports se contactan)
        network_targets = []
        for e in events:
            if "dst_ip" in e:
                network_targets.append(e["dst_ip"])
            if "dst_port" in e:
                network_targets.append(str(e["dst_port"]))
        # FIX P2: Pasar lista directa
        network_entropy = _entropy_shannon(network_targets) if network_targets else Fraction(0, 1)

        # Entropía temporal (cuándo ocurren eventos)
        timestamps = [e.get("timestamp", 0) for e in events]
        # FIX P2: Pasar lista directa
        temporal_entropy = _entropy_shannon(timestamps) if timestamps else Fraction(0, 1)

        # Compuesto
        composite = (
            process_entropy * Fraction(4, 10) +
            network_entropy * Fraction(3, 10) +
            temporal_entropy * Fraction(3, 10)
        )

        return BehavioralProfile(
            process_entropy=process_entropy,
            network_entropy=network_entropy,
            temporal_entropy=temporal_entropy,
            composite_entropy=composite,
        )
