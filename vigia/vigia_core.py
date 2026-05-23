#!/usr/bin/env python3
"""
vigia/engine/vigia_core.py — Núcleo de análisis forense de VIGÍA.

Orquestación del ciclo peirceano completo:
  Firstness (descripción) → Secondness (anomalías) →
  Thirdness (abducción de intención) → Geopolitical (false flag) →
  Devil's Advocate (refutación) → Veredicto
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import (
    SignalOutput, EvidenceEdge, EvidenceGraph,
    DecisionTrace, ForensicBundle, PolicySpec
)
from vigia.inference.likelihood_engine import LikelihoodEngine
from vigia.inference.risk_bounded_layer import RiskBoundedDecisionLayer
from vigia.tools.geopolitical import GeopoliticalIntentEngine, APT_PROFILES


class VigiaCore:
    """Motor principal de análisis forense abductivo."""

    def __init__(self, llm_backend=None, likelihood_engine=None, risk_layer=None):
        self.llm = llm_backend
        self.likelihood_engine = likelihood_engine or LikelihoodEngine()
        self.risk_layer = risk_layer or RiskBoundedDecisionLayer()
        self.geopolitical = GeopoliticalIntentEngine()

    # ── API principal ────────────────────────────────────────────

    def analyze_case(self, case_data: Dict) -> ForensicBundle:
        # Fase 1: Firstness
        firstness = self.llm.analyze_firstness(case_data.get("artifacts", []))

        # Fase 2: Secondness
        anomaly_signals = self._run_deterministic_tools(case_data)
        secondness = self.llm.analyze_secondness(anomaly_signals)

        # Fase 3: Thirdness
        thirdness = self.llm.analyze_thirdness(firstness, secondness)

        # Fase 4: Geopolitical (CORREGIDO: no recibe thirdness)
        attributed_actor, attribution_confidence = self._extract_attribution_from_evidence(case_data)

        geopolitical_signal = self.geopolitical.infer_strategic_intent(
            attributed_actor=attributed_actor,
            attribution_confidence=attribution_confidence,
            victim_sector=case_data.get("victim_sector", "unknown"),
            victim_geo=case_data.get("victim_geo", "unknown"),
            incident_date=case_data.get("incident_date", "2026-01-01"),
            observed_ttps=self._extract_ttps(case_data),
            infrastructure_evidence=case_data.get("infrastructure", {}),
            linguistic_evidence=case_data.get("linguistic", {})
        )

        # Dampening: reducir CONFIDENCE, no VALUE
        if attribution_confidence < 0.4:
            MIN_CONFIDENCE = 0.05
            adjusted_conf = max(
                geopolitical_signal.confidence * attribution_confidence,
                MIN_CONFIDENCE
            )
            geopolitical_signal = SignalOutput(
                tool_name="GEOPOLITICAL",
                value=geopolitical_signal.value,
                z_score=geopolitical_signal.z_score,
                confidence=adjusted_conf,
                metadata={
                    **geopolitical_signal.metadata,
                    "attribution_uncertainty": round(1.0 - attribution_confidence, 2),
                    "confidence_floor_applied": adjusted_conf == MIN_CONFIDENCE,
                    "uncertainty_note": (
                        f"Attribution to {attributed_actor} has low confidence "
                        f"({attribution_confidence:.2f}). The geopolitical signal is "
                        f"maintained with reduced confidence (floor={MIN_CONFIDENCE}). "
                        f"A real false flag typically begins with uncertain attribution."
                    )
                }
            )

        # Fase 5: Devil's Advocate
        devil_advocate = self.llm.generate_devil_advocate(
            thirdness,
            evidence={
                **case_data,
                "geopolitical_signal": geopolitical_signal,
                "attribution_confidence": attribution_confidence
            }
        )

        # Fase 6: Veredicto
        verdict = self._compute_verdict(
            firstness, secondness, thirdness,
            devil_advocate, geopolitical_signal
        )

        # Construir bundle
        bundle = ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=[], edges=[]),
            decision_trace=DecisionTrace(
                decision=verdict.get("decision", "ABSTAIN"),
                posterior=verdict.get("posterior", 0.5),
                risk=verdict.get("risk", 0.5),
                reason_code=verdict.get("reason_code", "ABSTAIN_ZONE"),
                omega_intention=verdict.get("omega_intention", 0.0)
            ),
            policy_spec=PolicySpec(),
            integrity=True
        )

        return bundle

    # ── Extracción de atribución ─────────────────────────────────

    def _extract_attribution_from_evidence(self, case_data: Dict) -> tuple:
        """
        Extrae atribución propuesta de evidencia técnica CRUDA.
        Usa MÁXIMO por categoría (no suma) para evitar inflación.
        Maneja empates devolviendo 'unknown'.
        """
        category_scores = {
            "malware": defaultdict(float),
            "infrastructure": defaultdict(float),
            "linguistic": defaultdict(float),
        }

        for artifact in case_data.get("artifacts", []):
            content = str(artifact.get("content", "")).casefold()
            anomalies = " ".join(str(a) for a in artifact.get("forensic_anomalies", []))
            full_text = content + " " + anomalies

            for actor_name, profile in APT_PROFILES.items():
                for family in profile.get("malware_families", []):
                    if family.casefold() in full_text:
                        category_scores["malware"][actor_name] = max(
                            category_scores["malware"][actor_name], 0.7
                        )

            infra = case_data.get("infrastructure", {})
            infra_type = infra.get("infrastructure_type", "")
            for actor_name, profile in APT_PROFILES.items():
                if infra_type in profile.get("infrastructure_habits", []):
                    category_scores["infrastructure"][actor_name] = max(
                        category_scores["infrastructure"][actor_name], 0.3
                    )

        linguistic = case_data.get("linguistic", {})
        if linguistic.get("keyboard_layout_slips"):
            for actor_name, profile in APT_PROFILES.items():
                if profile["linguistic_markers"].get("keyboard_layout_slips") == linguistic["keyboard_layout_slips"]:
                    category_scores["linguistic"][actor_name] = max(
                        category_scores["linguistic"][actor_name], 0.2
                    )

        actor_total_scores = {}
        all_actors = set()
        for cat in category_scores.values():
            all_actors.update(cat.keys())

        for actor in all_actors:
            actor_total_scores[actor] = (
                category_scores["malware"].get(actor, 0.0) +
                category_scores["infrastructure"].get(actor, 0.0) +
                category_scores["linguistic"].get(actor, 0.0)
            )

        if not actor_total_scores:
            return "unknown", 0.0

        best_score = max(actor_total_scores.values())
        candidates = [a for a, s in actor_total_scores.items() if s == best_score]

        if len(candidates) > 1:
            confidence = min(best_score / 1.2, 1.0)
            return "unknown", confidence

        best_actor = candidates[0]
        confidence = min(best_score / 1.2, 1.0)
        return best_actor, confidence

    # ── Helpers ──────────────────────────────────────────────────

    def _run_deterministic_tools(self, case_data: Dict) -> List:
        return []

    def _extract_ttps(self, case_data: Dict) -> List[str]:
        return []

    def _compute_verdict(self, firstness, secondness, thirdness,
                         devil_advocate, geopolitical_signal) -> Dict:
        return {
            "decision": "ABSTAIN",
            "posterior": 0.5,
            "risk": 0.5,
            "reason_code": "NOT_IMPLEMENTED",
            "omega_intention": 0.0
        }
