#!/usr/bin/env python3
"""
vigia/core/pipeline.py

Pipeline VIGÍA completo: Detection → Aggregation → Decision.

Flujo:
1. SemioticDetectorV2.analyze() → detección de patrones, sinergia, secuencias, FSV
2. EvidenceAggregator.aggregate() → combinación probabilística con alpha
3. RiskBoundedDecisionLayer.decide() → veredicto final con threshold

Autor: Colectivo VIGÍA
Versión: 1.0
"""

from typing import Dict, Any

from .semiotic_detector_v2 import SemioticDetectorV2
from .evidence_aggregator import EvidenceAggregator
from .decision_layer import RiskBoundedDecisionLayer


class VigiaPipeline:
    """
    Pipeline VIGÍA completo.
    """

    def __init__(
        self,
        db_path: str = "vigia/tools/forensic_patterns.sqlite",
        threshold_num: int = 15,
        critical_num: int = 30
    ):
        self.detector = SemioticDetectorV2(db_path)
        self.aggregator = EvidenceAggregator()
        self.decision = RiskBoundedDecisionLayer(threshold_num, critical_num)

    def analyze(self, text: str, artifact_id: str, timestamp: str) -> Dict[str, Any]:
        """
        Análisis completo de un artefacto textual.

        Args:
            text: Texto a analizar
            artifact_id: Identificador del artefacto
            timestamp: Timestamp del artefacto

        Returns:
            Resultado completo con veredicto
        """
        # Capa 1: Detection
        detection = self.detector.analyze(text, artifact_id, timestamp)

        # Capa 2: Aggregation
        aggregation = self.aggregator.aggregate(
            detection.get("fsv", {}),
            detection.get("synergy", {}),
            detection.get("sequences", {})
        )

        # Capa 3: Decision
        decision = self.decision.decide(aggregation)

        return {
            "artifact_id": artifact_id,
            "timestamp": timestamp,
            "text_snippet": text[:200] + "..." if len(text) > 200 else text,
            "matches": detection.get("matches", []),
            "synergy": detection.get("synergy", {}),
            "sequences": detection.get("sequences", {}),
            "aggregated_fsv": aggregation,
            "verdict": decision["verdict"],
            "alert_level": decision["alert_level"],
            "confidence": decision["confidence"],
            "score": decision["score"],
            "reason": decision["reason"]
        }


# ── API de conveniencia ───────────────────────────────────────────────────

def analyze_artifact(
    text: str,
    artifact_id: str = "default",
    timestamp: str = "2026-04-28T00:00:00Z",
    db_path: str = "vigia/tools/forensic_patterns.sqlite"
) -> Dict[str, Any]:
    """API de alto nivel para el pipeline VIGÍA."""
    pipeline = VigiaPipeline(db_path)
    return pipeline.analyze(text, artifact_id, timestamp)
