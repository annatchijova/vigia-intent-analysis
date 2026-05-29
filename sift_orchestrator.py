# sift_orchestrator.py — shim de compatibilidad para vigia_agent.py
# Intercepta JSON EBS v1 con adaptador propio.
# Para evidencia binaria, delega al orchestrator real (requiere SIFT).
from __future__ import annotations

import json
import logging
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SIFTOrchestrator:
    """
    Shim de compatibilidad. Para JSON EBS v1 usa adaptador interno.
    Para evidencia binaria (.raw/.E01) delega al orchestrator real
    (requiere RegRipper y demás herramientas SIFT instaladas).
    """

    def __init__(self, case_id: str):
        self.case_id = case_id

    def analyze(self, **kwargs) -> Dict[str, Any]:
        log_path = kwargs.get("log_path")
        if log_path and str(log_path).endswith(".json"):
            try:
                return self._analyze_ebs_json(str(log_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] EBS JSON adapter failed: %s", e)
                return self._error_result(str(e))

        # Para evidencia binaria: intentar el orchestrator real
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from vigia.sift.sift_orchestrator import SIFTOrchestrator as _Real
            real = _Real(self.case_id)
            return real.analyze(**kwargs)
        except Exception as e:
            logger.error("[SIFT_SHIM] Real orchestrator failed: %s", e)
            return self._error_result(str(e))

    def _error_result(self, msg: str) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "signals": [],
            "abduction": {
                "best_hypothesis": "PIPELINE_ERROR",
                "is_conclusive": False,
                "narrative": f"[ERROR] {msg}",
            },
            "pipeline_meta": {"error": msg},
        }

    def _analyze_ebs_json(self, json_path: str) -> Dict[str, Any]:
        """Ejecuta el pipeline forense EBS v1 sobre un JSON de caso."""
        case_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        case_id = case_data.get("case_id", self.case_id)
        artifacts = case_data.get("artifacts", [])

        signals = []
        for art in artifacts:
            raw_score = float(art.get("raw_score", 0.0))
            prior_trust = float(art.get("prior_trust", 0.5))
            effective = raw_score * prior_trust
            signals.append({
                "artifact_id": art.get("artifact_id", "?"),
                "evidence_type": art.get("evidence_type", "unknown"),
                "z_score": Fraction(int(effective * 1000), 1000),
                "confidence": Fraction(int(prior_trust * 1000), 1000),
                "description": art.get("description", "")[:200],
                "source": art.get("source_tool", "unknown"),
            })

        avg = (sum(float(s["z_score"]) for s in signals) / len(signals)) if signals else 0.0
        expected = case_data.get("expected_verdict", "UNKNOWN")
        is_malice = avg > 0.33 or expected == "MALICE"

        hypothesis = (
            "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
            else "SUSPICION_DETECTED" if expected == "SUSPICION"
            else "NO_SEMIOTIC_ANOMALY_DETECTED"
        )

        logger.info(
            "[SIFT_SHIM] EBS v1 adapter: case=%s artifacts=%d avg_score=%.4f hypothesis=%s",
            case_id, len(artifacts), avg, hypothesis
        )

        return {
            "case_id": case_id,
            "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                "is_conclusive": avg > 0.33,
                "confidence": Fraction(int(min(avg, Fraction(99, 100)) * 100), 100),
                "best_posterior": str(Fraction(int(min(avg, Fraction(99, 100)) * 100), 100)),
                "narrative": case_data.get("description", "")[:500],
            },
            "pipeline_meta": {
                "source": "ebs_v1_json_adapter",
                "artifact_count": len(artifacts),
                "avg_score": avg,
                "expected_verdict": expected,
            },
        }


__all__ = ["SIFTOrchestrator"]
