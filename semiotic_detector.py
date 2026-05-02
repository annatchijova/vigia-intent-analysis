#!/usr/bin/env python3
"""
vigia/core/semiotic_detector_v2.py

Detector semiótico determinista v2.1 — con sinergia, fuzzy matching,
memoria temporal y Forensic Signal Vector.

NO usa ML. NO usa floating point en scoring. Aritmética racional.
"""

import json
import re
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

# ── Configuración determinista ───────────────────────────────────────────

NGRAM_SIZE = 3
SIMILARITY_THRESHOLD_NUM = 13
SIMILARITY_THRESHOLD_DEN = 20
MAX_LEVENSHTEIN = 2
WINDOW_SIZE = 10
TEMPORAL_SPAN = 300

# ── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class PatternMatch:
    pattern_name: str
    category: str
    peirce_layer: str
    weight_num: int          # peso como entero (ej: 0.85 → 85, escala 100)
    weight_den: int          # siempre 100 para patrones base
    confidence_boost_num: int
    confidence_boost_den: int
    matched_text: str
    description: str
    case_origin: str
    match_type: str = "regex"  # "regex" | "fuzzy"
    similarity_ratio: Optional[Tuple[int, int]] = None  # (num, den)

    @property
    def weight(self) -> float:
        """Compatibilidad con consumidores que esperan float."""
        return self.weight_num / self.weight_den

    @property
    def confidence_boost(self) -> float:
        return self.confidence_boost_num / self.confidence_boost_den


@dataclass
class SynergyEvent:
    rule_id: str
    patterns: List[str]
    multiplier_num: int
    multiplier_den: int
    applied_bonus_num: int
    applied_bonus_den: int
    rationale: str


@dataclass
class SequenceEvent:
    rule_id: str
    description: str
    bonus_num: int
    bonus_den: int
    matched_patterns: List[str]
    mitre_ttp: str


# ── Cargar sinergia desde JSON ─────────────────────────────────────────────

SYNERGY_RULES = []

def _load_synergy_rules(path: str = "vigia/core/synergy_matrix.json") -> None:
    global SYNERGY_RULES
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        SYNERGY_RULES = data.get("rules", [])
    except FileNotFoundError:
        SYNERGY_RULES = [
            {"id": "SYN-001", "patterns": ["CARNEGIE_HELPER_TRAP", "GRICE_QUANTITY_STARVATION"],
             "multiplier_num": 5, "multiplier_den": 4, "bonus_cap_num": 1, "bonus_cap_den": 20,
             "rationale": "Inserción + ocultamiento"},
            {"id": "SYN-002", "patterns": ["CARNEGIE_ARTIFICIAL_URGENCY", "GRICE_DEFENSIVE_EVASION"],
             "multiplier_num": 13, "multiplier_den": 10, "bonus_cap_num": 3, "bonus_cap_den": 50,
             "rationale": "Urgencia + evasión"},
            {"id": "SYN-003", "patterns": ["ECO_KEYBOARD_SLIP_CYRILLIC", "GRICE_MANNER_AMBIGUITY"],
             "multiplier_num": 6, "multiplier_den": 5, "bonus_cap_num": 1, "bonus_cap_den": 25,
             "rationale": "Anomalía física + opacidad"},
            {"id": "SYN-004", "patterns": ["CARNEGIE_FLATTERY_MIRRORING", "CARNEGIE_HELPER_TRAP", "CARNEGIE_ARTIFICIAL_URGENCY"],
             "multiplier_num": 3, "multiplier_den": 2, "bonus_cap_num": 1, "bonus_cap_den": 10,
             "rationale": "Cadena de ingeniería social"},
            {"id": "SYN-005", "patterns": ["GRICE_QUALITY_UNVERIFIABLE", "CARNEGIE_BORROWED_CREDIBILITY"],
             "multiplier_num": 7, "multiplier_den": 5, "bonus_cap_num": 1, "bonus_cap_den": 20,
             "rationale": "Autoridad falsa + calidad inverosímil"},
            {"id": "SYN-006", "patterns": ["ECO_SYNTHETIC_JITTER", "ECO_INHUMAN_PERFECTION"],
             "multiplier_num": 5, "multiplier_den": 4, "bonus_cap_num": 1, "bonus_cap_den": 20,
             "rationale": "Dos índices de automatización"},
            {"id": "SYN-007", "patterns": ["CARNEGIE_PREEMPTIVE_CONFESSION", "GRICE_EVIDENCE_CLEANING"],
             "multiplier_num": 8, "multiplier_den": 5, "bonus_cap_num": 3, "bonus_cap_den": 50,
             "rationale": "Confesión menor + limpieza mayor"},
            {"id": "SYN-008", "patterns": ["ECO_FALSE_AMATEUR_TRAIL", "ECO_ANACHRONISM_TOOL"],
             "multiplier_num": 9, "multiplier_den": 5, "bonus_cap_num": 1, "bonus_cap_den": 10,
             "rationale": "Teatro de incompetencia + herramienta vieja"},
        ]

_load_synergy_rules()

# ── Fuzzy matching determinista ───────────────────────────────────────────

def _char_ngrams(text: str, n: int = NGRAM_SIZE) -> set:
    text = text.lower()
    text = "".join(c for c in text if c.isalnum() or c.isspace())
    text = " ".join(text.split())
    return {text[i:i+n] for i in range(len(text) - n + 1)} if len(text) >= n else set()


def _ngram_similarity(a: set, b: set) -> Tuple[int, int]:
    return (len(a & b), len(a | b)) if (a and b) else (0, 1)


def _is_fuzzy_match(text: str, variants: List[str]) -> Optional[Tuple[str, int, int]]:
    text_ngrams = _char_ngrams(text)
    if not text_ngrams:
        return None
    for variant in variants:
        variant_ngrams = _char_ngrams(variant)
        if not variant_ngrams:
            continue
        inter, union = _ngram_similarity(text_ngrams, variant_ngrams)
        # Determinista: comparación cruzada evita división float
        if inter * SIMILARITY_THRESHOLD_DEN >= SIMILARITY_THRESHOLD_NUM * union:
            return (variant, inter, union)
    return None


# ── Memoria temporal con expiración real ──────────────────────────────────

PATTERN_TO_PHASE = {
    "CARNEGIE_FLATTERY_MIRRORING": "FLATTERY",
    "CARNEGIE_HELPER_TRAP": "HELPER",
    "CARNEGIE_ARTIFICIAL_URGENCY": "URGENCY",
    "GRICE_DEFENSIVE_EVASION": "EVASION",
    "GRICE_DESTRUCTION_REQUEST": "EVASION",
    "GRICE_EVIDENCE_CLEANING": "CLEANING",
    "CARNEGIE_PREEMPTIVE_CONFESSION": "CONFESSION",
    "CARNEGIE_NORMALIZATION_PRESSURE": "NORMALIZATION",
    "ECO_KEYBOARD_SLIP_CYRILLIC": "PHYSICAL_SLIP",
    "ECO_SYNTHETIC_JITTER": "PHYSICAL_SLIP",
    "ECO_PLATFORM_CONTAMINATION": "PHYSICAL_SLIP",
    "T1567_EXFILTRATION": "EXFILTRATION",
    "T1070_INDICATOR_REMOVAL": "CLEANING",
    "T1055_PROCESS_INJECTION": "PERSISTENCE",
}

SEQUENCE_RULES = [
    {"id": "SEQ-SOCIAL-ENGINEERING", "phases": ["FLATTERY", "HELPER", "URGENCY", "EVASION", "EXFILTRATION"],
     "bonus_num": 3, "bonus_den": 20, "mitre_ttp": "T1566",
     "description": "Cadena clásica de ingeniería social de 5 fases"},
    {"id": "SEQ-INSIDER-SETUP", "phases": ["CONFESSION", "CLEANING", "NORMALIZATION", "PERSISTENCE"],
     "bonus_num": 1, "bonus_den": 10, "mitre_ttp": "T1078",
     "description": "Insider que se confiesa, limpia, normaliza e instala persistencia"},
    {"id": "SEQ-OPSEC-FAILURE", "phases": ["PHYSICAL_SLIP", "CORRECTION", "COVER_ATTEMPT", "REPETITION"],
     "bonus_num": 1, "bonus_den": 5, "mitre_ttp": "T1585",
     "description": "Desliz físico, corrección consciente, intento de cubrir, repetición"},
]


class SessionPatternMemory:
    def __init__(self, window_size: int = WINDOW_SIZE, temporal_span: int = TEMPORAL_SPAN):
        self.window_size = window_size
        self.temporal_span = temporal_span
        self._history: List[Dict] = []

    def add(self, timestamp: str, pattern_name: str, artifact_id: str) -> None:
        phase = PATTERN_TO_PHASE.get(pattern_name, "UNKNOWN")
        # Parsear ISO8601 a datetime para comparación real
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            ts = datetime.now(timezone.utc)
        self._history.append({
            "timestamp": timestamp,
            "ts": ts,
            "pattern": pattern_name,
            "phase": phase,
            "artifact_id": artifact_id,
        })
        self._expire_old(ts)
        if len(self._history) > self.window_size:
            self._history = self._history[-self.window_size:]

    def _expire_old(self, now: datetime) -> None:
        """Elimina entradas más viejas que TEMPORAL_SPAN segundos."""
        cutoff = now.timestamp() - self.temporal_span
        self._history = [h for h in self._history if h["ts"].timestamp() > cutoff]

    def check_sequences(self) -> List[SequenceEvent]:
        detected = []
        phases = [h["phase"] for h in self._history if h["phase"] != "UNKNOWN"]
        for rule in SEQUENCE_RULES:
            if self._is_subsequence(rule["phases"], phases):
                matched = [h["pattern"] for h in self._history if h["phase"] in rule["phases"]]
                detected.append(SequenceEvent(
                    rule_id=rule["id"], description=rule["description"],
                    bonus_num=rule["bonus_num"], bonus_den=rule["bonus_den"],
                    matched_patterns=matched, mitre_ttp=rule["mitre_ttp"],
                ))
        return detected

    def _is_subsequence(self, target: List[str], source: List[str]) -> bool:
        it = iter(source)
        return all(phase in it for phase in target)


# ── Detector principal ─────────────────────────────────────────────────────

class SemioticDetectorV2:
    """
    Detector semiótico v2.1 con sinergia, fuzzy matching y memoria temporal.
    """

    def __init__(self, db_path: str = "vigia/tools/forensic_patterns.sqlite"):
        self.db_path = db_path
        self._patterns: List[Dict] = []
        self._fuzzy_patterns: Dict[str, Dict] = {}
        self._memory = SessionPatternMemory()
        self._load_patterns()
        self._load_fuzzy_patterns()

    def _load_patterns(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT pattern_name, category, pattern_regex, weight, 
                   description, case_origin, peirce_layer, confidence_boost
            FROM nlp_patterns ORDER BY weight DESC
        """).fetchall()
        conn.close()
        for row in rows:
            try:
                compiled = re.compile(row["pattern_regex"], re.IGNORECASE)
                # Convertir float de DB a racional (escala 100)
                w_num = int(round(row["weight"] * 100))
                b_num = int(round(row["confidence_boost"] * 100))
                self._patterns.append({
                    "name": row["pattern_name"], "category": row["category"],
                    "regex": compiled, "weight_num": w_num, "weight_den": 100,
                    "description": row["description"], "origin": row["case_origin"],
                    "layer": row["peirce_layer"], "boost_num": b_num, "boost_den": 100,
                })
            except re.error:
                pass

    def _load_fuzzy_patterns(self) -> None:
        path = Path("vigia/core/fuzzy_config.json")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            config = data.get("patterns", {})
            for name, pdata in config.items():
                variants = pdata.get("variants", [])
                self._fuzzy_patterns[name] = {
                    "variants": variants,
                    "ngrams": [_char_ngrams(v) for v in variants],
                }
        else:
            # Fallback determinista mínimo
            defaults = {
                "GRICE_DESTRUCTION_REQUEST": {
                    "variants": ["quizás convendría omitir ese fragmento", "mejor no dejar rastro de esto",
                                 "podrías resumir sin citar", "evitemos dejar constancia escrita"],
                },
                "CARNEGIE_HELPER_TRAP": {
                    "variants": ["si querés te doy una mano", "así lo hacés más rápido",
                                 "te lo paso directo para que no pierdas tiempo", "dejame que lo hago yo por vos"],
                },
                "CARNEGIE_ARTIFICIAL_URGENCY": {
                    "variants": ["esto debería resolverse antes de que escale", "necesitamos cerrar esto hoy",
                                 "si no lo hacés ahora se complica", "el tiempo apremia"],
                },
            }
            for name, data in defaults.items():
                self._fuzzy_patterns[name] = {
                    "variants": data["variants"],
                    "ngrams": [_char_ngrams(v) for v in data["variants"]],
                }

    def analyze(self, text: str, artifact_id: str, timestamp: str) -> Dict[str, Any]:
        """
        Análisis completo: regex + fuzzy + sinergia + secuencia + FSV.
        """
        matches = self._match_patterns(text)
        fuzzy_matches = self._match_fuzzy(text)
        all_matches = matches + fuzzy_matches

        # Sinergia
        synergy_events = self._check_synergy(all_matches)

        # Memoria temporal
        for m in all_matches:
            self._memory.add(timestamp, m.pattern_name, artifact_id)
        sequence_events = self._memory.check_sequences()

        # FSV
        fsv = self._compute_fsv(all_matches, synergy_events, sequence_events, text)

        # Ajuste de confianza total (racional, cap 30/100)
        base_boost_num = sum(m.confidence_boost_num for m in all_matches)
        base_boost_den = 100
        synergy_boost_num = sum(e.applied_bonus_num * e.applied_bonus_den for e in synergy_events)  # normalizado
        synergy_boost_den = sum(e.applied_bonus_den for e in synergy_events) if synergy_events else 1
        sequence_boost_num = sum(e.bonus_num for e in sequence_events)
        sequence_boost_den = sum(e.bonus_den for e in sequence_events) if sequence_events else 1

        total_num = base_boost_num + synergy_boost_num + sequence_boost_num
        total_den = base_boost_den + synergy_boost_den + sequence_boost_den
        # Cap en 30/100 → si total_num/total_den > 30/100, capamos
        cap_num, cap_den = 30, 100
        if total_num * cap_den > cap_num * total_den:
            total_num, total_den = cap_num, cap_den

        # Detección de colisión semiótica (meta-ataque)
        alert_level = "NORMAL"
        if any(m.pattern_name == "ECO_SEMIOTIC_COLLISION" for m in all_matches):
            alert_level = "CRITICAL"
            # Override del cap para colisiones: máximo 25/100 extra
            total_num, total_den = 25, 100

        return {
            "matches": [self._match_to_dict(m) for m in all_matches],
            "synergy": {
                "triggered_rules": [self._synergy_to_dict(e) for e in synergy_events],
                "total_bonus_num": synergy_boost_num,
                "total_bonus_den": synergy_boost_den,
            },
            "sequences": {
                "triggered_rules": [self._sequence_to_dict(e) for e in sequence_events],
                "total_bonus_num": sequence_boost_num,
                "total_bonus_den": sequence_boost_den,
            },
            "fsv": fsv,
            "confidence_adjustment_num": total_num,
            "confidence_adjustment_den": total_den,
            "confidence_adjustment": total_num / total_den,  # compatibilidad
            "alert_level": alert_level,
            "dominant_category": self._dominant_category(all_matches),
            "max_weight": max((m.weight_num / m.weight_den for m in all_matches), default=0.0),
        }

    def _match_patterns(self, text: str) -> List[PatternMatch]:
        matches = []
        for pat in self._patterns:
            mobj = pat["regex"].search(text)
            if mobj:
                start = max(0, mobj.start() - 20)
                end = min(len(text), mobj.end() + 20)
                matches.append(PatternMatch(
                    pattern_name=pat["name"], category=pat["category"],
                    peirce_layer=pat["layer"], weight_num=pat["weight_num"], weight_den=pat["weight_den"],
                    confidence_boost_num=pat["boost_num"], confidence_boost_den=pat["boost_den"],
                    matched_text=text[start:end],
                    description=pat["description"], case_origin=pat["origin"],
                    match_type="regex",
                ))
        # Orden determinista: peso descendente, nombre ascendente como tie-breaker
        matches.sort(key=lambda m: (-m.weight_num, m.pattern_name))
        return matches

    def _match_fuzzy(self, text: str) -> List[PatternMatch]:
        matches = []
        for name, data in self._fuzzy_patterns.items():
            result = _is_fuzzy_match(text, data["variants"])
            if result:
                variant, inter, union = result
                base = next((p for p in self._patterns if p["name"] == name), None)
                if base:
                    # Fuzzy = 70% del peso base → 70/100
                    w_num = base["weight_num"] * 70
                    w_den = base["weight_den"] * 100
                    b_num = base["boost_num"] * 70
                    b_den = base["boost_den"] * 100
                    # Simplificar dividiendo por 10 si es divisible
                    if w_num % 10 == 0 and w_den % 10 == 0:
                        w_num, w_den = w_num // 10, w_den // 10
                    if b_num % 10 == 0 and b_den % 10 == 0:
                        b_num, b_den = b_num // 10, b_den // 10
                    matches.append(PatternMatch(
                        pattern_name=name, category=base["category"],
                        peirce_layer=base["layer"], weight_num=w_num, weight_den=w_den,
                        confidence_boost_num=b_num, confidence_boost_den=b_den,
                        matched_text=variant, description=base["description"] + " [FUZZY]",
                        case_origin=base["origin"], match_type="fuzzy",
                        similarity_ratio=(inter, union),
                    ))
        matches.sort(key=lambda m: (-m.weight_num, m.pattern_name))
        return matches

    def _check_synergy(self, matches: List[PatternMatch]) -> List[SynergyEvent]:
        matched_names = {m.pattern_name for m in matches}
        events = []
        for rule in SYNERGY_RULES:
            if all(p in matched_names for p in rule["patterns"]):
                # Base score: suma de pesos de los matches involucrados (escala 100)
                base_score_num = sum(m.weight_num for m in matches if m.pattern_name in rule["patterns"])
                base_score_den = 100
                # Multiplicador racional: (mult_num - mult_den) / mult_den
                # Impacto = base_score * (mult_num - mult_den) / mult_den
                delta_num = rule["multiplier_num"] - rule["multiplier_den"]
                delta_den = rule["multiplier_den"]
                impact_num = base_score_num * delta_num
                impact_den = base_score_den * delta_den
                # Cap racional
                cap_num = rule["bonus_cap_num"]
                cap_den = rule["bonus_cap_den"]
                # min(impact, cap) → comparación cruzada
                if impact_num * cap_den > cap_num * impact_den:
                    bonus_num, bonus_den = cap_num, cap_den
                else:
                    bonus_num, bonus_den = impact_num, impact_den
                # Simplificar si es posible (dividir por GCD básico)
                g = self._gcd(abs(bonus_num), abs(bonus_den))
                if g > 1:
                    bonus_num, bonus_den = bonus_num // g, bonus_den // g
                events.append(SynergyEvent(
                    rule_id=rule["id"], patterns=rule["patterns"],
                    multiplier_num=rule["multiplier_num"], multiplier_den=rule["multiplier_den"],
                    applied_bonus_num=bonus_num, applied_bonus_den=bonus_den,
                    rationale=rule["rationale"],
                ))
        return events

    @staticmethod
    def _gcd(a: int, b: int) -> int:
        while b:
            a, b = b, a % b
        return a

    def _compute_fsv(self, matches, synergy_events, sequence_events, text):
        firstness_num = sum(m.weight_num for m in matches if m.peirce_layer == "FIRSTNESS")
        secondness_num = sum(m.weight_num for m in matches if m.peirce_layer == "SECONDNESS")
        thirdness_num = sum(m.weight_num for m in matches if m.peirce_layer == "THIRDNESS")
        # Manipulation Index: (4*thirdness + 2*secondness + firstness) / 700
        # Escala: los pesos están en 0-100, suma máxima teórica ~300
        mi_num = 4 * thirdness_num + 2 * secondness_num + firstness_num
        mi_den = 700
        # Normalizar a escala 100 si excede
        if mi_num > mi_den:
            mi_num = mi_den
        return {
            "firstness": {"num": firstness_num, "den": 100},
            "secondness": {"num": secondness_num, "den": 100},
            "thirdness": {"num": thirdness_num, "den": 100},
            "manipulation_index": {"num": mi_num, "den": mi_den},
            "synergy_count": len(synergy_events),
            "sequence_count": len(sequence_events),
            "total_patterns": len(matches),
        }

    def _dominant_category(self, matches):
        if not matches:
            return None
        cat_weights: Dict[str, int] = {}
        for m in matches:
            cat_weights[m.category] = cat_weights.get(m.category, 0) + m.weight_num
        return max(cat_weights, key=cat_weights.get)

    def _match_to_dict(self, m):
        d = {
            "pattern_name": m.pattern_name, "category": m.category,
            "peirce_layer": m.peirce_layer, "weight": m.weight,
            "confidence_boost": m.confidence_boost, "matched_text": m.matched_text,
            "description": m.description, "case_origin": m.case_origin,
            "match_type": m.match_type,
        }
        if m.similarity_ratio:
            d["similarity"] = {"num": m.similarity_ratio[0], "den": m.similarity_ratio[1]}
        return d

    def _synergy_to_dict(self, e):
        return {
            "rule_id": e.rule_id, "patterns": e.patterns,
            "multiplier": f"{e.multiplier_num}/{e.multiplier_den}",
            "applied_bonus": f"{e.applied_bonus_num}/{e.applied_bonus_den}",
            "rationale": e.rationale,
        }

    def _sequence_to_dict(self, e):
        return {
            "rule_id": e.rule_id, "description": e.description,
            "bonus": f"{e.bonus_num}/{e.bonus_den}",
            "matched_patterns": e.matched_patterns, "mitre_ttp": e.mitre_ttp,
        }


# ── API de conveniencia ───────────────────────────────────────────────────

def analyze_artifact(text: str, artifact_id: str, timestamp: str,
                   db_path: str = "vigia/tools/forensic_patterns.sqlite") -> Dict[str, Any]:
    detector = SemioticDetectorV2(db_path)
    return detector.analyze(text, artifact_id, timestamp)
