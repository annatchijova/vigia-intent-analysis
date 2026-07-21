#!/usr/bin/env python3
"""
vigia/core/semiotic_detector_v2.py

Detector semiótico determinista v2.2 — final consolidado.
Incorpora fixes críticos del Colectivo VIGÍA:
1. Carga real de fuzzy_config.json (5 patrones, 25 variantes)
2. Subsecuencia correcta (índice manual, sin iterador consumible)
3. TTL real en SessionPatternMemory (limpieza por tiempo + cap por cantidad)
4. ECO_SEMIOTIC_COLLISION como campo estructurado (critical_patterns)
5. Determinismo integer-only (Fraction) en todo scoring interno
6. Forensic Signal Vector con breakdown granular

NO usa ML. NO usa floating point en scoring. Aritmética racional.
"""

import json
import re
import sqlite3
import threading
import unicodedata


# ── Sanitización de texto Unicode (P0 seguridad forense) ─────────────────

def _sanitize_text(text: str) -> str:
    """
    Normaliza Unicode antes del análisis semiótico.

    1. NFC: macOS/iOS generan NFD por defecto. 'destrucción' en NFD no matchea
       regexes compiladas en NFC — evasión silenciosa (Gemini V18).
    2. ZWNJ/ZWSP/BOM: caracteres invisibles que rompen word boundaries \\b
       y desalinean offsets del Negation Handler (Gemini V15).
    3. Purga también U+00AD (soft hyphen) que invisibiliza palabras clave.
    """
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFEFF\u00AD]', '', text)
    return text
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta, timezone
from fractions import Fraction

# ── Configuración determinista ───────────────────────────────────────────

NGRAM_SIZE = 3
SIMILARITY_THRESHOLD_NUM = 13
SIMILARITY_THRESHOLD_DEN = 20
WINDOW_SIZE = 10
TEMPORAL_SPAN = 300  # segundos

# ── Constantes de seguridad ────────────────────────────────────────────────
# Top-K: limita all_matches antes de sinergia — previene DoS O(R×P²) (DeepSeek V20)
TOP_K_MATCHES = 15
# Timeout por regex: previene ReDoS/catastrophic backtracking (Gemini V3/ReDoS)
REGEX_TIMEOUT_SECONDS = 2.0
# Sybil: peso mínimo para NO ser expulsado de memoria por flood de ruido (DeepSeek V4/Sybil)
MAX_TEXT_SIZE_BYTES = 10 * 1024 * 1024  # 10MB — previene OOM por payload asimétrico (Gemini V12)

# ── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class PatternMatch:
    pattern_name: str
    category: str
    peirce_layer: str
    weight_num: int
    weight_den: int
    confidence_boost_num: int
    confidence_boost_den: int
    matched_text: str
    description: str
    case_origin: str
    match_type: str = "regex"
    similarity_ratio: Optional[Tuple[int, int]] = None
    negation_detected: bool = False  # True si el Negation Handler atenuó este match

    @property
    def weight(self) -> float:
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

# ── Negation Handler — constantes ─────────────────────────────────────────

NEGATION_STRONG = frozenset([
    "no", "nunca", "jamás", "tampoco", "ni", "ningún", "ninguna",
    "ninguno", "nadie", "nada", "never", "not", "neither", "nor",
])
NEGATION_WEAK = frozenset([
    "sin", "apenas", "difícilmente", "hardly", "without",
])
NEGATION_WINDOW_CHARS = 50  # ventana bidireccional en caracteres

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
    text = text.casefold()  # casefold correcto para ß, ı, etc.
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
        # Lock para thread safety: dos llamadas MCP concurrentes no corrompen _history
        # (DeepSeek V18 / Race condition en memoria de sesión)
        self._lock = threading.Lock()

    def add(self, timestamp: str, pattern_name: str, artifact_id: str) -> None:
        phase = PATTERN_TO_PHASE.get(pattern_name, "UNKNOWN")
        # Truncar artifact_id — protege contra DoS por metadatos inflados (Gemini V20)
        safe_aid = str(artifact_id)[:255]

        # Parsear ISO8601 a datetime con forzado UTC y manejo de overflow (Gemini V14)
        try:
            if timestamp.endswith("Z"):
                ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                ts = datetime.fromisoformat(timestamp)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, OverflowError):
            ts = datetime.now(timezone.utc)

        with self._lock:
            self._expire_old(ts)
            self._history.append({
                "timestamp": timestamp,
                "ts": ts,
                "pattern": pattern_name,
                "phase": phase,
                "artifact_id": safe_aid,
            })
            if len(self._history) > self.window_size:
                # Sybil-resistant cap: eventos con fase conocida tienen prioridad.
                # Si hay flood de UNKNOWN, los known sobreviven. Sin esta lógica,
                # (known + unknown)[-N:] podría devolver solo unknowns si el flood
                # supera window_size (DeepSeek Sybil Attack).
                known = [h for h in self._history if h["phase"] != "UNKNOWN"]
                unknown = [h for h in self._history if h["phase"] == "UNKNOWN"]
                keep = known[:self.window_size]
                if len(keep) < self.window_size:
                    keep += unknown[:self.window_size - len(keep)]
                self._history = keep

    def _expire_old(self, now: datetime) -> None:
        """Elimina entradas más viejas que TEMPORAL_SPAN segundos.
        Usa timedelta puro — sin conversión a float64 (.timestamp()),
        que introduce redondeo de punto flotante y viola I2 (Punto 1)."""
        cutoff = now - timedelta(seconds=self.temporal_span)
        self._history = [h for h in self._history if h["ts"] > cutoff]

    def check_sequences(self) -> List[SequenceEvent]:
        with self._lock:
            history_snapshot = list(self._history)  # copia para no bloquear durante iteración
        detected = []
        phases = [h["phase"] for h in history_snapshot if h["phase"] != "UNKNOWN"]
        for rule in SEQUENCE_RULES:
            if self._is_subsequence(rule["phases"], phases):
                matched = sorted([h["pattern"] for h in history_snapshot if h["phase"] in rule["phases"]])
                detected.append(SequenceEvent(
                    rule_id=rule["id"], description=rule["description"],
                    bonus_num=rule["bonus_num"], bonus_den=rule["bonus_den"],
                    matched_patterns=matched, mitre_ttp=rule["mitre_ttp"],
                ))
        return detected

    def _is_subsequence(self, target: List[str], source: List[str]) -> bool:
        """Verifica subsecuencia SIN consumir iterador (fix crítico DeepSeek)."""
        t_idx = 0
        for s_phase in source:
            if t_idx < len(target) and s_phase == target[t_idx]:
                t_idx += 1
        return t_idx == len(target)


# ── Detector principal ─────────────────────────────────────────────────────

class SemioticDetectorV2:
    """
    Detector semiótico v2.2 — final consolidado.
    """

    def __init__(self, db_path: str = "vigia/tools/forensic_patterns.sqlite",
                 negation_enabled: bool = True):
        self.db_path = db_path
        self.negation_handler_enabled = negation_enabled
        self._patterns: List[Dict] = []
        self._fuzzy_patterns: Dict[str, Dict] = {}
        self._memory = SessionPatternMemory()
        self._load_patterns()
        self._load_fuzzy_patterns()

    def _detect_negation(self, text: str, match_start: int, match_end: int) -> Tuple[bool, str]:
        """
        Detecta negación en ventana bidireccional de NEGATION_WINDOW_CHARS caracteres.
        Retorna (negation_found, negation_type) donde negation_type ∈ {"strong","weak","none"}.
        Tokeniza por palabras — no usa substring para evitar falsos positivos (fix Kimi).
        """
        window_start = max(0, match_start - NEGATION_WINDOW_CHARS)
        window_end = min(len(text), match_end + NEGATION_WINDOW_CHARS)
        window = text[window_start:window_end].casefold()  # casefold: correcto para ß, ı, etc. (V19)
        tokens = re.findall(r"[a-záéíóúüñ']+", window)
        for tok in tokens:
            if tok in NEGATION_STRONG:
                return True, "strong"
            if tok in NEGATION_WEAK:
                return True, "weak"
        return False, "none"

    def _load_patterns(self) -> None:
        # mode=ro: herramienta forense estéril — VIGÍA nunca escribe en su DB de patrones.
        # Bloquea inyección en runtime y cumple aislamiento Daubert (Gemini V23).
        db_uri = Path(self.db_path).expanduser().resolve(strict=False).as_uri() + "?mode=ro"
        conn = None
        try:
            conn = sqlite3.connect(db_uri, uri=True)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT pattern_name, category, pattern_regex, weight,
                       description, case_origin, peirce_layer, confidence_boost
                FROM nlp_patterns ORDER BY weight DESC
            """).fetchall()
        except sqlite3.Error as exc:
            # Do not pretend that an empty in-memory database is a usable
            # detector.  Callers convert this unavailable component to a
            # detector fault / ABSTAIN instead of a clean-looking NOISE.
            raise RuntimeError(
                f"semiotic pattern database unavailable: {self.db_path}"
            ) from exc
        finally:
            if conn is not None:
                conn.close()
        for row in rows:
            try:
                pattern_str = row["pattern_regex"]
                # ReDoS detection: rechazar patrones con cuantificadores anidados
                # que pueden causar backtracking catastrófico (Gemini V3/ReDoS)
                if re.search(r'\([^)]*[+*][^)]*\)[+*]|\([^)]*\{[0-9,]+\}[^)]*\)[+*{]', pattern_str):
                    continue  # patrón potencialmente vulnerable, omitir
                compiled = re.compile(pattern_str, re.IGNORECASE)
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
        """Carga desde fuzzy_config.json con fallback mínimo (fix crítico #1)."""
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
            # Fallback mínimo determinista (solo 3, como antes)
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
        # OOM: rechazar payloads asimétricos (Gemini V12)
        if len(text.encode("utf-8")) > MAX_TEXT_SIZE_BYTES:
            text = text[:MAX_TEXT_SIZE_BYTES // 3]  # truncar pero analizar (no crashear)

        # Normalizar Unicode antes de cualquier análisis (NFC + purga ZWNJ/ZWSP)
        text = _sanitize_text(text)

        matches = self._match_patterns(text)
        fuzzy_matches = self._match_fuzzy(text)
        all_matches = matches + fuzzy_matches

        # Top-K: previene DoS O(R×P²) por saturación de patrones (DeepSeek V20)
        # Los matches se ordenan por peso — los más pesados sobreviven
        if len(all_matches) > TOP_K_MATCHES:
            all_matches = sorted(
                all_matches,
                key=lambda m: Fraction(m.weight_num, m.weight_den),
                reverse=True
            )[:TOP_K_MATCHES]

        # Sinergia
        synergy_events = self._check_synergy(all_matches)

        # Memoria temporal
        for m in all_matches:
            self._memory.add(timestamp, m.pattern_name, artifact_id)
        sequence_events = self._memory.check_sequences()

        # FSV
        fsv = self._compute_fsv(all_matches, synergy_events, sequence_events, text)

        # Critical patterns (ECO_SEMIOTIC_COLLISION estructurado — fix crítico #4)
        critical_patterns = [m.pattern_name for m in all_matches if m.pattern_name == "ECO_SEMIOTIC_COLLISION"]

        # Ajuste de confianza total (racional, cap 30/100)
        base_boost_num = sum(m.confidence_boost_num for m in all_matches)
        base_boost_den = 100
        synergy_boost_num = sum(e.applied_bonus_num for e in synergy_events)
        synergy_boost_den = sum(e.applied_bonus_den for e in synergy_events) if synergy_events else 1
        sequence_boost_num = sum(e.bonus_num for e in sequence_events)
        sequence_boost_den = sum(e.bonus_den for e in sequence_events) if sequence_events else 1

        total_num = base_boost_num + synergy_boost_num + sequence_boost_num
        total_den = base_boost_den + synergy_boost_den + sequence_boost_den
        cap_num, cap_den = 30, 100
        if total_num * cap_den > cap_num * total_den:
            total_num, total_den = cap_num, cap_den

        # Alert level
        alert_level = "NORMAL"
        if critical_patterns:
            alert_level = "CRITICAL"
            total_num, total_den = 25, 100

        return {
            "matches": [self._match_to_dict(m) for m in all_matches],
            "critical_patterns": critical_patterns,
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
            "_confidence_adjustment": total_num / total_den,  # display only (I7)
            "alert_level": alert_level,
            "dominant_category": self._dominant_category(all_matches),
            "_max_weight": max((m.weight_num / m.weight_den for m in all_matches), default=0.0),  # display only (I7)
        }

    def _match_patterns(self, text: str) -> List[PatternMatch]:
        matches = []
        for pat in self._patterns:
            mobj = pat["regex"].search(text)
            if mobj:
                start = max(0, mobj.start() - 20)
                end = min(len(text), mobj.end() + 20)
                w_num = pat["weight_num"]
                w_den = pat["weight_den"]
                b_num = pat["boost_num"]
                b_den = pat["boost_den"]
                neg_detected = False
                if self.negation_handler_enabled:
                    neg_found, neg_type = self._detect_negation(text, mobj.start(), mobj.end())
                    if neg_found:
                        neg_detected = True
                        if neg_type == "strong":
                            # Factor 1/2: duplicar denominador
                            w_num = w_num
                            w_den = w_den * 2
                            b_num = b_num
                            b_den = b_den * 2
                        else:
                            # Factor 3/4
                            w_num = w_num * 3
                            w_den = w_den * 4
                            b_num = b_num * 3
                            b_den = b_den * 4
                matches.append(PatternMatch(
                    pattern_name=pat["name"], category=pat["category"],
                    peirce_layer=pat["layer"], weight_num=w_num, weight_den=w_den,
                    confidence_boost_num=b_num, confidence_boost_den=b_den,
                    matched_text=text[start:end],
                    description=pat["description"], case_origin=pat["origin"],
                    match_type="regex",
                    negation_detected=neg_detected,
                ))
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
                    w_num = base["weight_num"] * 70
                    w_den = base["weight_den"] * 100
                    b_num = base["boost_num"] * 70
                    b_den = base["boost_den"] * 100
                    if w_num % 10 == 0 and w_den % 10 == 0:
                        w_num, w_den = w_num // 10, w_den // 10
                    if b_num % 10 == 0 and b_den % 10 == 0:
                        b_num, b_den = b_num // 10, b_den // 10
                    # Negation Handler en fuzzy — mismo mecanismo que en regex (Kimi P1-4)
                    # "mejor no borrar el archivo" detecta el fuzzy pero debe atenuarse
                    neg_detected = False
                    if self.negation_handler_enabled:
                        idx = text.casefold().find(variant.casefold())
                        if idx >= 0:
                            neg_found, neg_type = self._detect_negation(text, idx, idx + len(variant))
                            if neg_found:
                                neg_detected = True
                                if neg_type == "strong":
                                    w_den = w_den * 2
                                    b_den = b_den * 2
                                else:
                                    w_num = w_num * 3
                                    w_den = w_den * 4
                                    b_num = b_num * 3
                                    b_den = b_den * 4

                    matches.append(PatternMatch(
                        pattern_name=name, category=base["category"],
                        peirce_layer=base["layer"], weight_num=w_num, weight_den=w_den,
                        confidence_boost_num=b_num, confidence_boost_den=b_den,
                        matched_text=variant, description=base["description"] + " [FUZZY]",
                        case_origin=base["origin"], match_type="fuzzy",
                        similarity_ratio=(inter, union),
                        negation_detected=neg_detected,
                    ))
        matches.sort(key=lambda m: (-m.weight_num, m.pattern_name))
        return matches

    def _check_synergy(self, matches: List[PatternMatch]) -> List[SynergyEvent]:
        matched_names = {m.pattern_name for m in matches}
        events = []
        for rule in SYNERGY_RULES:
            # sorted() garantiza determinismo I2: los sets no preservan orden
            # entre ejecuciones. Mismo input → mismo JSON → mismo hash (Gemini P0).
            rule_patterns = sorted(rule["patterns"])
            if all(p in matched_names for p in rule_patterns):
                base_score_num = sum(m.weight_num for m in matches if m.pattern_name in rule["patterns"])
                base_score_den = 100
                delta_num = rule["multiplier_num"] - rule["multiplier_den"]
                delta_den = rule["multiplier_den"]
                impact_num = base_score_num * delta_num
                impact_den = base_score_den * delta_den
                cap_num = rule["bonus_cap_num"]
                cap_den = rule["bonus_cap_den"]
                if impact_num * cap_den > cap_num * impact_den:
                    bonus_num, bonus_den = cap_num, cap_den
                else:
                    bonus_num, bonus_den = impact_num, impact_den
                # Clamp a [0,1] (fix crítico #4)
                if bonus_den == 0:
                    bonus_num, bonus_den = 0, 1
                if bonus_num < 0:
                    bonus_num = 0
                if bonus_num > bonus_den:
                    bonus_num = bonus_den
                g = self._gcd(abs(bonus_num), abs(bonus_den))
                if g > 1:
                    bonus_num, bonus_den = bonus_num // g, bonus_den // g
                events.append(SynergyEvent(
                    rule_id=rule["id"], patterns=sorted(rule["patterns"]),
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
        mi_num = 4 * thirdness_num + 2 * secondness_num + firstness_num
        mi_den = 700
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
            "peirce_layer": m.peirce_layer,
            "weight_num": m.weight_num, "weight_den": m.weight_den,
            "_weight": m.weight,          # display only — usar weight_num/den en lógica (I7)
            "confidence_boost_num": m.confidence_boost_num,
            "confidence_boost_den": m.confidence_boost_den,
            "_confidence_boost": m.confidence_boost,  # display only (I7)
            "matched_text": m.matched_text,
            "description": m.description, "case_origin": m.case_origin,
            "match_type": m.match_type,
            "negation_detected": m.negation_detected,
        }
        if m.similarity_ratio:
            d["similarity"] = {"num": m.similarity_ratio[0], "den": m.similarity_ratio[1]}
        return d

    def _synergy_to_dict(self, e):
        return {
            "rule_id": e.rule_id,
            "patterns": sorted(e.patterns),
            "multiplier_num": e.multiplier_num,
            "multiplier_den": e.multiplier_den,
            "applied_bonus_num": e.applied_bonus_num,
            "applied_bonus_den": e.applied_bonus_den,
            # alias para compatibilidad con aggregator
            "impact_num": e.applied_bonus_num,
            "impact_den": e.applied_bonus_den,
            "rationale": e.rationale,
        }

    def _sequence_to_dict(self, e):
        return {
            "rule_id": e.rule_id,
            "description": e.description,
            "bonus_num": e.bonus_num,
            "bonus_den": e.bonus_den,
            "matched_patterns": sorted(e.matched_patterns),
            "mitre_ttp": e.mitre_ttp,
        }


# ── API de conveniencia ───────────────────────────────────────────────────

def analyze_artifact(text: str, artifact_id: str, timestamp: str,
                     db_path: str = "vigia/tools/forensic_patterns.sqlite",
                     negation_enabled: bool = True) -> Dict[str, Any]:
    """Entry point canónico. negation_enabled activa/desactiva el Negation Handler."""
    detector = SemioticDetectorV2(db_path=db_path, negation_enabled=negation_enabled)
    return detector.analyze(text, artifact_id, timestamp)
