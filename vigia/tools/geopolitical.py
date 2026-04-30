#!/usr/bin/env python3
"""
vigia/tools/geopolitical.py — Quinto Pilar: Motor de Intención Geopolítica

Detecta false flags por inconsistencia estratégica entre:
- Atribución técnica propuesta
- Doctrina documentada del actor
- Intereses geopolíticos en el momento del incidente
- Consistencia de infraestructura
- Marcadores lingüísticos genuinos vs plantados

Principio Peirceano: Thirdness — la mediación entre el signo técnico
y el objeto real (el atacante) requiere un interpretante que modele
patrones históricos, doctrina estatal y costo de desinformación.
"""

from __future__ import annotations

from fractions import Fraction
from math import exp
from typing import Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput

# ── Base de conocimiento de actores APT ──────────────────────────
APT_PROFILES = {
    "APT28": {
        "aliases": ["Fancy Bear", "Sofacy", "Pawn Storm", "Strontium"],
        "state_sponsor": "Russian Federation (GRU)",
        "doctrine": "military_intelligence_priority",
        "historical_targets": ["government", "military", "defense_contractors",
                               "political_organizations", "NATO_members"],
        "temporal_pattern": "aligned_with_russian_geopolitical_events",
        "known_false_flags": ["Olympic Destroyer 2018 (posed as Lazarus)"],
        "infrastructure_habits": ["bulletproof_hosting", "domain_fronting"],
        "malware_families": ["X-Agent", "X-Tunnel", "Sofacy", "Zebrocy"],
        "linguistic_markers": {
            "compile_time_utc_offset": "+3 Moscow",
            "keyboard_layout_slips": "RU",
            "code_comments_language": "Russian"
        }
    },
    "APT34": {
        "aliases": ["OilRig", "Helix Kitten", "APT34"],
        "state_sponsor": "Islamic Republic of Iran",
        "doctrine": "industrial_sabotage_priority",
        "historical_targets": ["energy", "financial_services", "government",
                               "critical_infrastructure", "middle_east"],
        "temporal_pattern": "retaliatory_after_sanctions",
        "known_false_flags": [],
        "infrastructure_habits": ["poison_frog_panels", "domestic_hosting"],
        "malware_families": ["ISFB", "ISMAgent", "Poison Frog"],
        "linguistic_markers": {
            "compile_time_utc_offset": "+3:30 Tehran",
            "keyboard_layout_slips": "FA",
            "code_comments_language": "Persian"
        }
    },
    "Lazarus": {
        "aliases": ["HIDDEN COBRA", "Zinc", "Diamond Sleet"],
        "state_sponsor": "Democratic People's Republic of Korea",
        "doctrine": "financial_theft_and_espionage",
        "historical_targets": ["financial_services", "cryptocurrency",
                               "government", "defense"],
        "temporal_pattern": "diplomatic_outreach_and_sanctions_evasion",
        "known_false_flags": [],
        "infrastructure_habits": ["southeast_asia_vps", "chinese_domains"],
        "malware_families": ["AppleJeus", "Blindingcan", "Crowdoor"],
        "linguistic_markers": {
            "compile_time_utc_offset": "+9 Pyongyang",
            "keyboard_layout_slips": "KO",
            "code_comments_language": "Korean"
        }
    }
}

# ── Eventos geopolíticos ─────────────────────────────────────────
GEOPOLITICAL_EVENTS = {
    "olympic_winter_2018": {
        "date_range": ("2018-02-09", "2018-02-25"),
        "location": "Pyeongchang, South Korea",
        "russian_motivation": "retaliation_for_doping_ban",
        "north_korean_motivation": "diplomatic_outreach_during_games",
        "third_parties_interested_in_tension": ["Russian Federation"]
    }
}

# ── Parámetros de fusión ──────────────────────────────────────────
RULE_WEIGHTS = {
    "cui_bono":               0.30,
    "temporal_opportunity":    0.25,
    "doctrine_consistency":    0.15,
    "infrastructure_seizure":  0.15,
    "linguistic_false_flag":   0.15,
}

RULE_DEPENDENCIES = {
    ("cui_bono", "temporal_opportunity"):       0.15,
    ("infrastructure_seizure", "linguistic_false_flag"): 0.20,
}

SIGMOID_SCALE = 3.0
SIGMOID_SHIFT = 0.35
PENALTY_SCALE = 0.7


# ── Fusión de reglas ──────────────────────────────────────────────

def _fuse_rule_scores(scores: dict) -> float:
    """
    Fusión log-odds con:
    - Penalización por dependencia (evita doble conteo)
    - Penalty scaling independiente (evita destruir señal fuerte)
    - Clamping robusto (evita valores fuera de dominio)
    - Normalización dinámica (no asume pesos fijos)
    - Sigmoide calibrada (alineada al baseline empírico)
    """
    linear_sum = 0.0
    for rule_name, score in scores.items():
        weight = RULE_WEIGHTS.get(rule_name, 0.10)
        linear_sum += weight * float(score)

    raw_penalty = 0.0
    seen_pairs = set()
    for (rule_a, rule_b), lambda_ij in RULE_DEPENDENCIES.items():
        key = tuple(sorted((rule_a, rule_b)))
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        if rule_a in scores and rule_b in scores:
            score_a = float(scores[rule_a])
            score_b = float(scores[rule_b])
            raw_penalty += lambda_ij * score_a * score_b

    penalty = PENALTY_SCALE * raw_penalty

    max_logit = max(sum(RULE_WEIGHTS.values()), 1e-6)
    logit_raw = linear_sum - penalty
    logit_raw = max(0.0, min(logit_raw, max_logit))

    logit_normalized = logit_raw / max_logit
    logit_calibrated = SIGMOID_SCALE * (logit_normalized - SIGMOID_SHIFT)

    try:
        probability = 1.0 / (1.0 + exp(-logit_calibrated))
        return round(probability, 4)
    except OverflowError:
        return 0.9999 if logit_calibrated > 0 else 0.0001


# ── Motor principal ───────────────────────────────────────────────

class GeopoliticalIntentEngine:
    """
    Quinto pilar de VIGÍA.
    Detecta false flags por inconsistencia estratégica.
    """

    # ── Reglas individuales ──────────────────────────────────────

    def rule_cui_bono(self, attributed_actor: str, victim_sector: str,
                      victim_geo: str) -> float:
        profile = APT_PROFILES.get(attributed_actor)
        if not profile:
            return 0.0
        sector_match = victim_sector in profile["historical_targets"]
        geo_match = victim_geo in profile.get("geographic_focus", [])
        if sector_match and geo_match:
            return 0.0
        elif sector_match or geo_match:
            return 0.3
        else:
            return 0.7

    def rule_doctrine_consistency(self, attributed_actor: str,
                                  observed_ttps: List[str]) -> float:
        profile = APT_PROFILES.get(attributed_actor)
        if not profile:
            return 0.0
        doctrine = profile["doctrine"]
        mismatch_penalty = 0.0
        for ttp in observed_ttps:
            if doctrine == "military_intelligence_priority":
                if ttp in ["industrial_sabotage", "ransomware_financial"]:
                    mismatch_penalty += 0.25
            elif doctrine == "industrial_sabotage_priority":
                if ttp in ["military_reconnaissance", "diplomatic_espionage"]:
                    mismatch_penalty += 0.25
        return min(mismatch_penalty, 0.8)

    def rule_temporal_opportunity(self, attributed_actor: str,
                                  incident_date: str) -> float:
        profile = APT_PROFILES.get(attributed_actor)
        if not profile:
            return 0.0
        temporal_pattern = profile["temporal_pattern"]
        relevant_events = self._find_relevant_events(incident_date)
        inconsistency_score = 0.0
        for event in relevant_events:
            actor_motivation = event.get(
                self._get_event_key_for_actor(attributed_actor), "unknown"
            )
            if actor_motivation == "diplomatic_outreach":
                inconsistency_score += 0.6
            elif actor_motivation == "retaliation" and temporal_pattern == "diplomatic_outreach":
                inconsistency_score += 0.8
        third_party_benefit = self._find_third_party_benefit(incident_date, attributed_actor)
        if third_party_benefit:
            inconsistency_score += 0.3
        return min(inconsistency_score, 0.9)

    def rule_infrastructure_seizure_risk(self, attributed_actor: str,
                                         infrastructure_evidence: Dict) -> float:
        profile = APT_PROFILES.get(attributed_actor)
        if not profile:
            return 0.0
        expected_habits = profile["infrastructure_habits"]
        observed_infra = infrastructure_evidence
        seizure_indicators = 0
        if "operation_hours_utc" in observed_infra:
            expected_offset = profile["linguistic_markers"]["compile_time_utc_offset"]
            observed_hours = observed_infra["operation_hours_utc"]
            if self._hours_match_timezone(observed_hours, "+3 Moscow") and expected_offset == "+3:30 Tehran":
                seizure_indicators += 0.5
        if "infrastructure_type" in observed_infra:
            if observed_infra["infrastructure_type"] not in expected_habits:
                for other_actor, other_profile in APT_PROFILES.items():
                    if other_actor != attributed_actor:
                        if observed_infra["infrastructure_type"] in other_profile["infrastructure_habits"]:
                            seizure_indicators += 0.4
                            break
        return min(seizure_indicators, 0.8)

    def rule_linguistic_false_flag_detection(self, attributed_actor: str,
                                             linguistic_evidence: Dict) -> float:
        profile = APT_PROFILES.get(attributed_actor)
        if not profile:
            return 0.0
        expected_lang = profile["linguistic_markers"]["code_comments_language"]
        observed_lang = linguistic_evidence.get("comment_language", "unknown")
        is_layout_slip = linguistic_evidence.get("is_layout_slip", False)
        if observed_lang == expected_lang and is_layout_slip:
            return 0.0
        elif observed_lang == expected_lang and not is_layout_slip:
            return 0.2
        elif observed_lang != expected_lang and observed_lang != "unknown":
            return 0.7
        else:
            return 0.0

    # ── Helpers ──────────────────────────────────────────────────

    def _find_relevant_events(self, incident_date: str) -> List[Dict]:
        return []

    def _get_event_key_for_actor(self, attributed_actor: str) -> str:
        return "north_korean_motivation"

    def _find_third_party_benefit(self, incident_date: str, attributed_actor: str) -> bool:
        return False

    def _hours_match_timezone(self, hours: List[int], timezone: str) -> bool:
        return False

    # ── Inferencia principal ─────────────────────────────────────

    def infer_strategic_intent(self,
                               attributed_actor: str,
                               attribution_confidence: float,
                               victim_sector: str,
                               victim_geo: str,
                               incident_date: str,
                               observed_ttps: List[str],
                               infrastructure_evidence: Dict,
                               linguistic_evidence: Dict) -> SignalOutput:

        cui_bono_score = self.rule_cui_bono(attributed_actor, victim_sector, victim_geo)
        doctrine_score = self.rule_doctrine_consistency(attributed_actor, observed_ttps)
        temporal_score = self.rule_temporal_opportunity(attributed_actor, incident_date)
        seizure_score = self.rule_infrastructure_seizure_risk(attributed_actor, infrastructure_evidence)
        linguistic_score = self.rule_linguistic_false_flag_detection(attributed_actor, linguistic_evidence)

        scores = {
            "cui_bono": cui_bono_score,
            "temporal_opportunity": temporal_score,
            "doctrine_consistency": doctrine_score,
            "infrastructure_seizure": seizure_score,
            "linguistic_false_flag": linguistic_score,
        }

        false_flag_likelihood = _fuse_rule_scores(scores)

        BASELINE_MEAN = 0.15
        BASELINE_MAD = 0.10
        z_score = (false_flag_likelihood - BASELINE_MEAN) / BASELINE_MAD

        if false_flag_likelihood >= 0.7:
            confidence = false_flag_likelihood
            determination = "LIKELY_FALSE_FLAG"
        elif false_flag_likelihood >= 0.4:
            confidence = false_flag_likelihood
            determination = "SUSPICIOUS_ATTRIBUTION"
        else:
            confidence = 1 - false_flag_likelihood
            determination = "CONSISTENT_ATTRIBUTION"

        return SignalOutput(
            tool_name="GEOPOLITICAL",
            value=false_flag_likelihood,
            z_score=round(z_score, 4),
            confidence=round(confidence, 4),
            metadata={
                "determination": determination,
                "rule_scores": {
                    "cui_bono": round(cui_bono_score, 4),
                    "doctrine_consistency": round(doctrine_score, 4),
                    "temporal_opportunity": round(temporal_score, 4),
                    "infrastructure_seizure": round(seizure_score, 4),
                    "linguistic_false_flag": round(linguistic_score, 4),
                },
                "attributed_actor": attributed_actor,
                "attribution_confidence_input": round(attribution_confidence, 4),
            }
        )
