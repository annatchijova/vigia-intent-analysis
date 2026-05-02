"""
vigia/tools/adversarial_nlp.py
================================
VIGÍA — Motores NLP Adversariales para Análisis Forense de Documentos.

Extraído y refactorizado desde: adversarial_nlp_pericial_EN_ES.py (raíz)
Responsabilidad: análisis lingüístico de documentos para detectar
fabricación, spoofing de identidad y ofuscación deliberada.

CAPAS DE ANÁLISIS (pipeline MCP)
----------------------------------
P2 — SDA-NR  : Sintáctico-Discursivo de Nominalización/Registro
               Detecta registro institucional incongruente
P3 — CLI     : Cognitive Load Indicators
               Detecta estrés cognitivo del falsificador
P4 — ACP     : Authorship Consistency Protocol
               Detecta spoofing de identidad autoral vía z-scores
P5 — ROI     : Readability/Obfuscation Index
               Detecta ofuscación deliberada (Gunning Fog + Flesch)

MCP (Multiplicador de Certeza Pericial): 1.0x–5.0x
  - 1.0x: AUTÉNTICO
  - 2.5x–4.0x: SOSPECHOSO
  - 4.0x–5.0x: FABRICADO

COMPLIANCE
----------
- Daubert Standard: determinismo total, cero NLP externas
- Rob T. Lee: zero external NLP dependencies
- Qwen: memory paranoia (ventanas, cursores, límites)
- DeepSeek: secure file handling

SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import statistics
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from vigia.security import _utcnow, audit_logger, _sanitize_path
from vigia.tools.nlp_constants import (
    # Tipos base
    Language, InstitutionalEmitter, ForensicThresholds, LanguageConfig,
    # Límites
    MAX_TEXT_LENGTH, MAX_WINDOW_SIZE, MAX_CACHE_ENTRIES, ACP_WINDOW_SIZE,
    CONFIG_PERMISSIONS,
    # Sigmas
    SIGMA_WARNING, SIGMA_CRITICAL, SIGMA_DEFINITIVE, SIGMA_SPOOFING,
    # Lexicón ES
    SPANISH_FUNCTION_WORDS, SPANISH_LEGAL_MARKERS, SPANISH_TECHNICAL_MARKERS,
    SPANISH_NARRATIVE_MARKERS, SPANISH_URGENT_MARKERS,
    # Lexicón EN
    ENGLISH_FUNCTION_WORDS, ENGLISH_LEGAL_MARKERS, ENGLISH_TECHNICAL_MARKERS,
    ENGLISH_NARRATIVE_MARKERS, ENGLISH_URGENT_MARKERS,
    # Cognitive markers
    CognitiveMarkers,
)
from vigia.tools.forensic_db import ForensicDatabaseManager

# CAIE integration (opcional — no bloquea si no está disponible)
try:
    from vigia.tools.caie import CrossArtifactIncongruenceEngine
    _CAIE_AVAILABLE = True
except ImportError:
    _CAIE_AVAILABLE = False
    CrossArtifactIncongruenceEngine = None  # type: ignore


# ============================================================================
# CARGA DE CONFIGURACIÓN EXTERNA (auditable Daubert)
# ============================================================================

class ConfigLoader:
    """
    Carga configuración forense desde JSON/YAML externo.
    Permite auditoría y modificación sin cambiar código fuente.
    Fallback a DEFAULT_CONFIG si no hay archivo externo.
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "languages": {
            "es": {
                "function_words": list(SPANISH_FUNCTION_WORDS),
                "legal_markers": list(SPANISH_LEGAL_MARKERS),
                "technical_markers": list(SPANISH_TECHNICAL_MARKERS),
                "narrative_markers": list(SPANISH_NARRATIVE_MARKERS),
                "urgent_markers": list(SPANISH_URGENT_MARKERS),
                "exclusion_markers": list(CognitiveMarkers.EXCLUSION_MARKERS_ES),
                "certainty_markers": list(CognitiveMarkers.CERTAINTY_QUANT_ES),
                "distancing_markers": list(CognitiveMarkers.DISTANCING_MARKERS_ES),
                "prepositions": ["a", "ante", "bajo", "con", "contra", "de", "desde", "en", "entre"],
                "noun_suffixes": ["ción", "sión", "tad", "dad", "miento", "anza"],
                "verb_suffixes": ["ar", "er", "ir", "ando", "ado", "aba", "ía"],
                "adj_suffixes": ["able", "ible", "oso", "ico", "ivo", "al"],
                "adv_suffixes": ["mente"],
                "fog_thresholds": {"simple": 8, "standard": 12, "complex": 16, "obscure": 20},
            },
            "en": {
                "function_words": list(ENGLISH_FUNCTION_WORDS),
                "legal_markers": list(ENGLISH_LEGAL_MARKERS),
                "technical_markers": list(ENGLISH_TECHNICAL_MARKERS),
                "narrative_markers": list(ENGLISH_NARRATIVE_MARKERS),
                "urgent_markers": list(ENGLISH_URGENT_MARKERS),
                "exclusion_markers": list(CognitiveMarkers.EXCLUSION_MARKERS_EN),
                "certainty_markers": list(CognitiveMarkers.CERTAINTY_QUANT_EN),
                "distancing_markers": list(CognitiveMarkers.DISTANCING_MARKERS_EN),
                "prepositions": ["of", "in", "to", "for", "with", "on", "at", "from", "by", "about"],
                "noun_suffixes": ["tion", "sion", "ment", "ness", "ity", "er", "or"],
                "verb_suffixes": ["ing", "ed", "en", "ize", "ate", "ify"],
                "adj_suffixes": ["able", "ible", "al", "ful", "ous", "ive"],
                "adv_suffixes": ["ly", "ward", "wise"],
                "fog_thresholds": {"simple": 6, "standard": 12, "complex": 16, "obscure": 20},
            },
        },
        "institutional_baselines": {
            "MPF": {
                "nv_ratio": {"mean": 3.2, "std": 0.4},
                "nominalization": {"mean": 0.58, "std": 0.06},
                "exclusion": {"mean": 0.03, "std": 0.01},
                "certainty": {"mean": 0.08, "std": 0.02},
                "ttr": {"mean": 0.42, "std": 0.05},
                "fog": {"mean": 14.5, "std": 1.8},
                "info_density": {"mean": 0.35, "std": 0.04},
            },
            "LE": {
                "nv_ratio": {"mean": 2.8, "std": 0.5},
                "nominalization": {"mean": 0.52, "std": 0.07},
                "exclusion": {"mean": 0.04, "std": 0.015},
                "certainty": {"mean": 0.12, "std": 0.03},
                "ttr": {"mean": 0.38, "std": 0.06},
                "fog": {"mean": 12.0, "std": 2.2},
                "info_density": {"mean": 0.32, "std": 0.05},
            },
            "COURT": {
                "nv_ratio": {"mean": 3.8, "std": 0.3},
                "nominalization": {"mean": 0.62, "std": 0.05},
                "exclusion": {"mean": 0.025, "std": 0.008},
                "certainty": {"mean": 0.06, "std": 0.015},
                "ttr": {"mean": 0.45, "std": 0.04},
                "fog": {"mean": 16.2, "std": 1.5},
                "info_density": {"mean": 0.38, "std": 0.03},
            },
            "UNKNOWN": {
                "nv_ratio": {"mean": 3.0, "std": 0.5},
                "nominalization": {"mean": 0.55, "std": 0.08},
                "exclusion": {"mean": 0.035, "std": 0.012},
                "certainty": {"mean": 0.09, "std": 0.025},
                "ttr": {"mean": 0.40, "std": 0.06},
                "fog": {"mean": 13.0, "std": 2.0},
                "info_density": {"mean": 0.33, "std": 0.05},
            },
        },
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    if self.config_path.endswith((".yaml", ".yml")):
                        return yaml.safe_load(f) or self.DEFAULT_CONFIG
                    return json.load(f)
            except Exception as exc:
                audit_logger.log_info(
                    event_type="CONFIG_LOAD_FAILED",
                    tool="ConfigLoader",
                    message=f"Config load failed: {exc} — using defaults",
                )
        return self.DEFAULT_CONFIG

    def get_language_config(self, lang: str) -> LanguageConfig:
        cfg = self.config["languages"].get(lang, self.config["languages"]["es"])
        return LanguageConfig(
            code=lang,
            function_words=frozenset(cfg["function_words"]),
            legal_markers=frozenset(cfg["legal_markers"]),
            technical_markers=frozenset(cfg["technical_markers"]),
            narrative_markers=frozenset(cfg["narrative_markers"]),
            urgent_markers=frozenset(cfg["urgent_markers"]),
            exclusion_markers=frozenset(cfg["exclusion_markers"]),
            certainty_markers=frozenset(cfg["certainty_markers"]),
            distancing_markers=frozenset(cfg["distancing_markers"]),
            prepositions=frozenset(cfg["prepositions"]),
            noun_suffixes=tuple(cfg["noun_suffixes"]),
            verb_suffixes=tuple(cfg["verb_suffixes"]),
            adj_suffixes=tuple(cfg["adj_suffixes"]),
            adv_suffixes=tuple(cfg["adv_suffixes"]),
            fog_thresholds=cfg["fog_thresholds"],
        )

    def get_institutional_baseline(self, emitter: InstitutionalEmitter) -> ForensicThresholds:
        key = emitter.name
        baselines = self.config["institutional_baselines"]
        cfg = baselines.get(key, baselines.get("UNKNOWN", baselines.get("MPF")))
        return ForensicThresholds(
            nv_ratio_mean=cfg["nv_ratio"]["mean"],
            nv_ratio_std=cfg["nv_ratio"]["std"],
            nominalization_mean=cfg["nominalization"]["mean"],
            nominalization_std=cfg["nominalization"]["std"],
            exclusion_mean=cfg["exclusion"]["mean"],
            exclusion_std=cfg["exclusion"]["std"],
            certainty_mean=cfg["certainty"]["mean"],
            certainty_std=cfg["certainty"]["std"],
            ttr_mean=cfg["ttr"]["mean"],
            ttr_std=cfg["ttr"]["std"],
            fog_mean=cfg["fog"]["mean"],
            fog_std=cfg["fog"]["std"],
            info_density_mean=cfg["info_density"]["mean"],
            info_density_std=cfg["info_density"]["std"],
        )

    def save_default_config(self, path: str) -> None:
        abs_path = os.path.abspath(os.path.expanduser(path))
        parent = os.path.dirname(abs_path)
        if not os.path.exists(parent):
            os.makedirs(parent, mode=0o750)
        with open(abs_path, "w", encoding="utf-8") as f:
            if path.endswith((".yaml", ".yml")):
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)
            else:
                json.dump(self.DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        os.chmod(abs_path, CONFIG_PERMISSIONS)


# ============================================================================
# MOTOR P0 — DETECCIÓN DE IDIOMA
# ============================================================================

@dataclass(frozen=True)
class LanguageProfile:
    """
    Perfil forense por idioma. Umbrales sintácticos y léxicos calibrados
    específicamente para cada familia lingüística.
    Agregado en merge P4 — canónico adversarial_nlp multilingüe (2026-05-02).
    """
    code: str
    name: str
    nv_ratio_min: float
    nv_ratio_max: float
    nominalization_min: float
    fog_simple: float
    fog_standard: float
    fog_complex: float
    fog_obscure: float
    noun_suffixes: tuple
    verb_suffixes: tuple
    adj_suffixes: tuple
    adv_suffixes: tuple
    function_words: frozenset
    legal_markers: frozenset
    technical_markers: frozenset
    narrative_markers: frozenset
    urgent_markers: frozenset


ENGLISH_PROFILE = LanguageProfile(
    code="en", name="English",
    nv_ratio_min=2.5, nv_ratio_max=6.0, nominalization_min=0.50,
    fog_simple=6.0, fog_standard=12.0, fog_complex=16.0, fog_obscure=20.0,
    noun_suffixes=("tion", "sion", "ment", "ness", "ity", "er", "or", "ism",
                   "ure", "age", "ance", "ence", "dom", "ship", "hood"),
    verb_suffixes=("ing", "ed", "en", "ize", "ise", "ify", "ate"),
    adj_suffixes=("able", "ible", "al", "ful", "less", "ous", "ive", "ic", "ish"),
    adv_suffixes=("ly", "ward", "wards", "wise"),
    function_words=ENGLISH_FUNCTION_WORDS,
    legal_markers=ENGLISH_LEGAL_MARKERS,
    technical_markers=ENGLISH_TECHNICAL_MARKERS,
    narrative_markers=ENGLISH_NARRATIVE_MARKERS,
    urgent_markers=ENGLISH_URGENT_MARKERS,
)

SPANISH_PROFILE = LanguageProfile(
    code="es", name="Spanish",
    nv_ratio_min=1.8, nv_ratio_max=4.0, nominalization_min=0.45,
    fog_simple=8.0, fog_standard=12.0, fog_complex=16.0, fog_obscure=20.0,
    noun_suffixes=("ción", "sión", "dad", "miento", "anza", "encia", "eza",
                   "ura", "aje", "or", "ario", "orio"),
    verb_suffixes=("ando", "iendo", "ado", "ido", "aba", "ía", "ará", "ería"),
    adj_suffixes=("able", "ible", "oso", "ico", "ivo", "al", "ario"),
    adv_suffixes=("mente",),
    function_words=SPANISH_FUNCTION_WORDS,
    legal_markers=SPANISH_LEGAL_MARKERS,
    technical_markers=SPANISH_TECHNICAL_MARKERS,
    narrative_markers=SPANISH_NARRATIVE_MARKERS,
    urgent_markers=SPANISH_URGENT_MARKERS,
)


@dataclass
class AuthorialBaseline:
    """Baseline estilométrico por autor — dependencia de AuthorialFingerprintingEngine."""
    author_id: str
    document_count: int = 0
    mean_ttr: float = 0.0
    std_ttr: float = 0.01
    mean_lexical_entropy: float = 0.0
    mean_zipf: float = 0.0

    def update(self, ttr: float, lex_entropy: float, zipf: float) -> None:
        self.document_count += 1
        n = self.document_count
        prev_mean = self.mean_ttr
        self.mean_ttr = prev_mean + (ttr - prev_mean) / n
        self.mean_lexical_entropy = self.mean_lexical_entropy + (lex_entropy - self.mean_lexical_entropy) / n
        self.mean_zipf = self.mean_zipf + (zipf - self.mean_zipf) / n
        if n > 1:
            self.std_ttr = max(0.01, abs(ttr - self.mean_ttr) * 0.5 + self.std_ttr * 0.5)


@dataclass(frozen=True)
class GriceanAnalysis:
    """Resultado de análisis de violación de Manera de Grice."""
    fog_index: float
    ambiguity_density: float
    avg_sentence_length: float
    ambiguity_count: int
    manner_violation_score: float
    register_content_mismatch: bool
    severity: float

    def to_dict(self) -> dict:
        return {
            "fog_index": round(self.fog_index, 4),
            "ambiguity_density": round(self.ambiguity_density, 4),
            "avg_sentence_length": round(self.avg_sentence_length, 4),
            "ambiguity_count": self.ambiguity_count,
            "manner_violation_score": round(self.manner_violation_score, 4),
            "register_content_mismatch": self.register_content_mismatch,
            "severity": round(self.severity, 4),
        }


class LanguageDetector:
    """
    Detector de idioma basado en bigramas de alta frecuencia.
    Versión extendida del canónico (2026-05-02): usa LanguageProfile,
    bigramas ampliados, y expone get_profile() para las capas P4.
    """

    EN_BIGRAMS: frozenset = frozenset({
        "th", "he", "in", "er", "an", "re", "on", "at", "en", "nd",
        "ti", "es", "or", "te", "of", "ed", "is", "it", "al", "ar",
        "st", "to", "nt", "ng", "se", "ha", "as", "ou", "io", "le",
        "ve", "co", "me", "de", "hi", "ri", "ro", "ic", "ne", "ea",
    })
    ES_BIGRAMS: frozenset = frozenset({
        "de", "la", "el", "en", "os", "ar", "ue", "es", "ra", "as",
        "ad", "or", "nt", "te", "co", "re", "na", "al", "do", "on",
        "io", "ro", "se", "li", "ta", "an", "qu", "ie", "ll", "rr",
    })
    EN_FUNCTION: frozenset = ENGLISH_FUNCTION_WORDS
    ES_FUNCTION: frozenset = SPANISH_FUNCTION_WORDS

    @classmethod
    def detect(cls, text: str) -> Language:
        text_lower = text[:10_000].lower()
        bigrams = {text_lower[i:i+2] for i in range(len(text_lower)-1)
                   if text_lower[i:i+2].isalpha()}
        score_en = len(bigrams & cls.EN_BIGRAMS)
        score_es = len(bigrams & cls.ES_BIGRAMS) * 2
        if any(c in text for c in "áéíóúñÁÉÍÓÚÑ"):
            score_es += 20
        words = set(re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", text_lower))
        score_en += len(words & cls.EN_FUNCTION) * 5
        score_es += len(words & cls.ES_FUNCTION) * 5
        if re.search(r'\b(the|and|of|to|in|is|that|for|with|as)\b', text_lower):
            score_en += 15
        if score_es > score_en * 1.3:
            return Language.SPANISH
        if score_en > score_es * 1.3:
            return Language.ENGLISH
        if any(c in text for c in "áéíóúñ"):
            return Language.SPANISH
        return Language.ENGLISH if score_en > score_es else Language.UNKNOWN

    @classmethod
    def get_profile(cls, lang: Language) -> LanguageProfile:
        if lang == Language.ENGLISH:
            return ENGLISH_PROFILE
        return SPANISH_PROFILE  # default español para SANS compliance


# ============================================================================
# MOTOR P2 — SDA-NR (Sintáctico-Discursivo Nominalización/Registro)
# ============================================================================

class SDA_NominalizationAnalyzer:
    """Detecta incongruencia de registro institucional via ratio sustantivo/verbo."""

    PREPOSITIONS_ES = frozenset({"a", "ante", "bajo", "con", "contra", "de", "desde", "en", "entre"})
    PREPOSITIONS_EN = frozenset({"of", "in", "to", "for", "with", "on", "at", "from", "by", "about"})

    def __init__(self, config: ConfigLoader) -> None:
        self.config = config
        self.lang_detector = LanguageDetector()

    def analyze(self, text: str, emitter: InstitutionalEmitter, lang_code: Optional[str] = None) -> Dict:
        text = text[:MAX_TEXT_LENGTH]
        if lang_code is None:
            lang_code = self.lang_detector.detect(text).value

        lang_cfg = self.config.get_language_config(lang_code)
        baseline = self.config.get_institutional_baseline(emitter)
        words = self._tokenize_safe(text, lang_code)

        if not words:
            return self._empty_result(lang_code)

        nouns = verbs = adjs = preps = 0
        for w in words:
            if self._is_noun(w, lang_cfg):
                nouns += 1
            elif self._is_verb(w, lang_cfg):
                verbs += 1
            elif self._is_adj(w, lang_cfg):
                adjs += 1
            if w in lang_cfg.prepositions:
                preps += 1

        nv_ratio = nouns / max(verbs, 1)
        nominalization = nouns / max(nouns + verbs + adjs, 1)
        prep_density = preps / len(words)

        z_nv = (nv_ratio - baseline.nv_ratio_mean) / max(baseline.nv_ratio_std, 0.001)
        z_nom = (nominalization - baseline.nominalization_mean) / max(baseline.nominalization_std, 0.001)
        sigma_max = max(abs(z_nv), abs(z_nom))
        fab_prob = self._calc_fabrication_prob(sigma_max)

        return {
            "language": lang_code,
            "counts": {"nouns": nouns, "verbs": verbs, "adjs": adjs, "preps": preps},
            "nv_ratio": nv_ratio,
            "nominalization": nominalization,
            "prep_density": prep_density,
            "z_nv": z_nv,
            "z_nom": z_nom,
            "sigma_max": sigma_max,
            "is_inconsistent": sigma_max > SIGMA_CRITICAL,
            "fabrication_probability": fab_prob,
        }

    def _tokenize_safe(self, text: str, lang_code: str) -> List[str]:
        pattern = r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b" if lang_code == "es" else r"\b[a-zA-Z]+\b"
        if len(text) > 100_000:
            words: List[str] = []
            for i in range(0, len(text), 100_000):
                words.extend(re.findall(pattern, text[i:i+100_000].lower()))
                if len(words) > MAX_WINDOW_SIZE * 10:
                    break
            return words[:MAX_WINDOW_SIZE * 10]
        return re.findall(pattern, text.lower())

    def _is_noun(self, w: str, cfg: LanguageConfig) -> bool:
        if w in cfg.legal_markers or w in cfg.technical_markers:
            return True
        return any(w.endswith(s) for s in cfg.noun_suffixes if len(w) > len(s) + 2)

    def _is_verb(self, w: str, cfg: LanguageConfig) -> bool:
        return any(w.endswith(s) for s in cfg.verb_suffixes if len(w) > len(s) + 1)

    def _is_adj(self, w: str, cfg: LanguageConfig) -> bool:
        return any(w.endswith(s) for s in cfg.adj_suffixes if len(w) > len(s) + 2)

    def _empty_result(self, lang_code: str) -> Dict:
        return {
            "language": lang_code,
            "counts": {"nouns": 0, "verbs": 0, "adjs": 0, "preps": 0},
            "nv_ratio": 0.0, "nominalization": 0.0, "prep_density": 0.0,
            "z_nv": 0.0, "z_nom": 0.0, "sigma_max": 0.0,
            "is_inconsistent": False, "fabrication_probability": 0.0,
        }

    def _calc_fabrication_prob(self, sigma: float) -> float:
        if sigma < SIGMA_WARNING:
            return 0.0
        if sigma < SIGMA_CRITICAL:
            return (sigma - SIGMA_WARNING) / (SIGMA_CRITICAL - SIGMA_WARNING) * 0.3
        if sigma < SIGMA_DEFINITIVE:
            return 0.3 + (sigma - SIGMA_CRITICAL) / (SIGMA_DEFINITIVE - SIGMA_CRITICAL) * 0.5
        return min(1.0, 0.8 + (sigma - SIGMA_DEFINITIVE) * 0.1)


# ============================================================================
# MOTOR P3 — CLI (Cognitive Load Indicators)
# ============================================================================

class CLI_Analyzer:
    """Detecta estrés cognitivo del falsificador via marcadores epistémicos."""

    def __init__(self, config: ConfigLoader) -> None:
        self.config = config
        self.lang_detector = LanguageDetector()

    def analyze(self, text: str, emitter: InstitutionalEmitter, lang_code: Optional[str] = None) -> Dict:
        text = text[:MAX_TEXT_LENGTH]
        if lang_code is None:
            lang_code = self.lang_detector.detect(text).value

        lang_cfg = self.config.get_language_config(lang_code)
        baseline = self.config.get_institutional_baseline(emitter)
        text_lower = text.lower()
        total = max(len(text_lower.split()), 1)

        excl = self._count_markers(text_lower, lang_cfg.exclusion_markers) / total
        cert = self._count_markers(text_lower, lang_cfg.certainty_markers) / total
        dist = self._count_markers(text_lower, lang_cfg.distancing_markers) / total

        z_excl = (excl - baseline.exclusion_mean) / max(baseline.exclusion_std, 0.001)
        z_cert = (cert - baseline.certainty_mean) / max(baseline.certainty_std, 0.001)
        stress = abs(z_excl) * 0.3 + abs(z_cert) * 0.5 + (dist * 10)
        is_fab = abs(z_excl) > 2.0 or abs(z_cert) > 2.5 or stress > 3.0

        return {
            "exclusion_density": excl,
            "certainty_density": cert,
            "distancing_density": dist,
            "z_exclusion": z_excl,
            "z_certainty": z_cert,
            "cognitive_stress_index": stress,
            "is_fabrication_indicator": is_fab,
            "fabrication_likelihood": (
                min(1.0, (abs(z_excl) + abs(z_cert)) / 6.0 + stress / 10.0)
                if is_fab else 0.0
            ),
        }

    def _count_markers(self, text: str, markers: frozenset) -> int:
        return sum(text.count(m) for m in markers)


# ============================================================================
# MOTOR P4 — ACP (Authorship Consistency Protocol)
# ============================================================================

class ACP_Protocol:
    """Detecta spoofing de identidad autoral comparando con baseline SQLite."""

    def __init__(self, db: ForensicDatabaseManager, config: ConfigLoader) -> None:
        self.db = db
        self.config = config
        self.lang_detector = LanguageDetector()
        self._cache: Dict[str, Dict] = {}
        self._cache_lock = threading.Lock()

    def analyze(
        self,
        text: str,
        emitter_id: str,
        emitter_type: InstitutionalEmitter,
        lexical_entropy: float,
        lang_code: Optional[str] = None,
    ) -> Dict:
        text = text[:MAX_TEXT_LENGTH]
        if lang_code is None:
            lang_code = self.lang_detector.detect(text).value

        ttr = self._calc_ttr(text, lang_code)
        sync_complexity = self._calc_sync_complexity(text, lang_code)
        doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        profile = self._get_profile(emitter_id)

        if profile is None or profile.get("document_count", 0) < 2:
            return {
                "emitter_id": emitter_id,
                "baseline_documents": 0,
                "current_ttr": ttr,
                "is_identity_spoofing": False,
                "spoofing_confidence": 0.0,
                "reason": "INSUFFICIENT_BASELINE",
                "document_hash": doc_hash,
            }

        z_ttr = (ttr - profile["ttr_mean"]) / max(profile["ttr_std"], 0.001)
        z_lex = (lexical_entropy - profile["entropy_mean"]) / max(profile["entropy_std"], 0.001)
        z_sync = (sync_complexity - profile["sync_mean"]) / max(profile["sync_std"], 0.001)
        max_z = max(abs(z_ttr), abs(z_lex), abs(z_sync))
        is_spoofing = max_z > SIGMA_SPOOFING

        if max_z > 3.5:
            confidence = min(1.0, 0.9 + (max_z - 3.5) * 0.05)
        elif max_z > SIGMA_SPOOFING:
            confidence = 0.7 + (max_z - SIGMA_SPOOFING) / (3.5 - SIGMA_SPOOFING) * 0.2
        else:
            confidence = 0.0

        return {
            "emitter_id": emitter_id,
            "language": lang_code,
            "baseline_documents": profile.get("document_count", 0),
            "current_ttr": ttr,
            "baseline_ttr_mean": profile.get("ttr_mean", 0),
            "baseline_ttr_std": profile.get("ttr_std", 0),
            "zscore_ttr": z_ttr,
            "zscore_lex_entropy": z_lex,
            "zscore_sync": z_sync,
            "max_zscore": max_z,
            "is_identity_spoofing": is_spoofing,
            "spoofing_confidence": confidence,
            "document_hash": doc_hash,
        }

    def update_baseline(
        self,
        emitter_id: str,
        emitter_type: InstitutionalEmitter,
        language: str,
        metrics: Dict[str, float],
        verdict: str,
        mcp: float,
        document_hash: str,
    ) -> bool:
        return self.db.update_profile(
            emitter_id=emitter_id,
            emitter_type=emitter_type.name,
            language=language,
            metrics=metrics,
            verdict=verdict,
            mcp=mcp,
            document_hash=document_hash,
        )

    def _get_profile(self, emitter_id: str) -> Optional[Dict]:
        with self._cache_lock:
            if emitter_id in self._cache:
                return self._cache[emitter_id]
        profile = self.db.get_profile(emitter_id)
        with self._cache_lock:
            if len(self._cache) >= MAX_CACHE_ENTRIES:
                self._cache.pop(next(iter(self._cache)))
            if profile:
                self._cache[emitter_id] = profile
        return profile

    def _calc_ttr(self, text: str, lang_code: str) -> float:
        cfg = self.config.get_language_config(lang_code)
        pattern = r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b" if lang_code == "es" else r"\b[a-zA-Z]+\b"
        words = re.findall(pattern, text.lower())
        content = [w for w in words if w not in cfg.function_words]
        if not content:
            return 0.0
        window = 400 if lang_code == "en" else 350
        if len(content) > window:
            ttrs = []
            for i in range(0, len(content) - window + 1, window // 2):
                w = content[i:i+window]
                ttrs.append(len(set(w)) / len(w))
                if len(ttrs) > 100:
                    break
            return statistics.mean(ttrs) if ttrs else 0.0
        return len(set(content)) / len(content)

    def _calc_sync_complexity(self, text: str, lang_code: str) -> float:
        simple = len(re.findall(r"[.!?]+", text))
        if lang_code == "es":
            compound = len(re.findall(r"[,;](?=\s*y|o|pero|sin embargo)", text.lower()))
        else:
            compound = len(re.findall(r"[,;](?=\s*and|but|however)", text.lower()))
        return compound / max(simple + compound, 1)


# ============================================================================
# MOTOR P5 — ROI (Readability/Obfuscation Index)
# ============================================================================

class ROI_Analyzer:
    """Detecta ofuscación deliberada via Gunning Fog y Flesch."""

    def __init__(self, config: ConfigLoader) -> None:
        self.config = config
        self.lang_detector = LanguageDetector()
        self.sda = SDA_NominalizationAnalyzer(config)

    def analyze(self, text: str, emitter: InstitutionalEmitter, lang_code: Optional[str] = None) -> Dict:
        text = text[:MAX_TEXT_LENGTH]
        if lang_code is None:
            lang_code = self.lang_detector.detect(text).value

        lang_cfg = self.config.get_language_config(lang_code)
        baseline = self.config.get_institutional_baseline(emitter)

        pattern = r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b" if lang_code == "es" else r"\b[a-zA-Z]+\b"
        words = re.findall(pattern, text.lower())
        sentences = [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]

        if not sentences or not words:
            return {
                "gunning_fog": 0.0, "flesch_score": 0.0, "information_density": 0.0,
                "redundancy_ratio": 0.0, "is_obfuscation_attack": False,
                "obfuscation_type": "NONE", "attack_confidence": 0.0,
            }

        asl = len(words) / len(sentences)
        if lang_code == "es":
            complex_words = [w for w in words if self._syllables_es(w) > 3]
        else:
            complex_words = [w for w in words if len(re.findall(r"[aeiouy]+", w)) > 2]
        fog = 0.4 * (asl + 100 * len(complex_words) / len(words))
        flesch = self._flesch_es(text) if lang_code == "es" else self._flesch_en(text)

        sda_result = self.sda.analyze(text, emitter, lang_code)
        info_density = sda_result["nominalization"]
        redundancy = self._redundancy(words, lang_cfg)

        z_fog = (fog - baseline.fog_mean) / max(baseline.fog_std, 0.001)
        z_info = (info_density - baseline.info_density_mean) / max(baseline.info_density_std, 0.001)

        obsc_threshold = lang_cfg.fog_thresholds["obscure"]
        complexity_surplus = fog > obsc_threshold and info_density < 0.25
        density_deficit = (
            redundancy > 0.4
            and info_density < baseline.info_density_mean - baseline.info_density_std
        )
        is_obf = complexity_surplus or density_deficit
        obf_type = (
            "COMBINED" if (complexity_surplus and density_deficit)
            else "COMPLEXITY_SURPLUS" if complexity_surplus
            else "DENSITY_DEFICIT" if density_deficit
            else "NONE"
        )
        confidence = (
            min(1.0, (abs(z_fog) / 3.0) * 0.4 + (abs(z_info) / 3.0) * 0.4 + (redundancy / 0.4) * 0.2)
            if is_obf else 0.0
        )
        return {
            "gunning_fog": fog, "flesch_score": flesch,
            "information_density": info_density, "redundancy_ratio": redundancy,
            "z_fog": z_fog, "z_info_density": z_info,
            "is_obfuscation_attack": is_obf, "obfuscation_type": obf_type,
            "attack_confidence": confidence,
        }

    def _syllables_es(self, word: str) -> int:
        vowels = "aeiouáéíóúü"
        count, prev = 0, False
        for c in word.lower():
            is_v = c in vowels
            if is_v and not prev:
                count += 1
            prev = is_v
        return max(1, count)

    def _flesch_es(self, text: str) -> float:
        words = re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", text.lower())
        sentences = [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
        if not sentences or not words:
            return 0.0
        asl = len(words) / len(sentences)
        asw = sum(self._syllables_es(w) for w in words) / len(words)
        return 206.835 - 1.015 * asl - 84.6 * asw

    def _flesch_en(self, text: str) -> float:
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        sentences = [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
        if not sentences or not words:
            return 0.0
        asl = len(words) / len(sentences)
        asw = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in words) / len(words)
        return 206.835 - 1.015 * asl - 84.6 * asw

    def _redundancy(self, words: List[str], cfg: LanguageConfig) -> float:
        content = [w for w in words if w not in cfg.function_words]
        if len(content) < 5:
            return 0.0
        from collections import Counter
        bigrams = [f"{content[i]}_{content[i+1]}" for i in range(len(content)-1)]
        if not bigrams:
            return 0.0
        freq = Counter(bigrams)
        repeated = sum(1 for c in freq.values() if c > 1)
        return repeated / len(bigrams)


# ============================================================================
# VEREDICTO FORENSE Y MCP
# ============================================================================

# ============================================================================
# ZIPF IMPERFECTION ANALYZER — Carnegie Inversion: "Imperfección Calculada"
# Gemini tactical order + Kimi NLP intelligence (2026)
#
# FUNDAMENTO CIENTÍFICO:
#   Los errores humanos reales (typos, hesitaciones) siguen la ley de Zipf:
#   P(f) ∝ f^(-α) con α ≈ 1.0, R² > 0.85 en regresión log-log.
#   Los atacantes que simulan "imperfección" para evadir detección de
#   "demasiado limpio" generan ruido con distribución uniforme o gaussiana
#   (randomización sin estructura fractal).
#
#   DETECCIÓN: si R² bajo o α diverge de 1.0 → IMPERFECTION_CALCULATED.
# ============================================================================

_ZIPF_ALPHA_AUTHENTIC_MEAN: float = 1.02
_ZIPF_ALPHA_AUTHENTIC_STD:  float = 0.18
_ZIPF_R2_THRESHOLD:         float = 0.75
_ZIPF_MIN_OOV_TOKENS:       int   = 5
_ZIPF_ALPHA_DIVERGENCE:     float = 0.40


class ZipfImperfectionAnalyzer:
    """
    Detecta 'imperfección calculada' — errores artificiales añadidos por
    atacantes para evadir detección de perfección AI.

    Los errores humanos reales siguen ley de Zipf (α ≈ 1.0, R² > 0.85).
    Los errores AI-simulados tienden a distribución uniforme (R² bajo)
    porque el atacante randomiza para evitar repetir el mismo typo.

    Output compatible con SignalOutput para alimentar al cluster NLP
    del LikelihoodEngine (tool_name="GCI").

    Referencia Peirce:
        Firstness:  Distribución de frecuencias de anomalías léxicas
        Secondness: Divergencia del fit Zipf respecto al baseline humano
        Thirdness:  El HÁBITO del atacante es randomizar — eso lo delata
    """

    def __init__(
        self,
        alpha_mean: float = _ZIPF_ALPHA_AUTHENTIC_MEAN,
        alpha_std: float  = _ZIPF_ALPHA_AUTHENTIC_STD,
        r2_threshold: float = _ZIPF_R2_THRESHOLD,
        min_oov: int = _ZIPF_MIN_OOV_TOKENS,
    ) -> None:
        self._alpha_mean   = alpha_mean
        self._alpha_std    = alpha_std
        self._r2_threshold = r2_threshold
        self._min_oov      = min_oov

    def analyze(self, text: str, lang_code: str = "es") -> Dict[str, Any]:
        """
        Analiza la distribución de anomalías léxicas del texto.

        Retorna dict con:
            is_calculated_imperfection: bool
            zipf_alpha, zipf_r2, alpha_zscore, n_oov_tokens
            confidence, signal_value, fractura
            tool_name: "GCI" — alimenta cluster NLP del LikelihoodEngine
            peirce_firstness/secondness/thirdness
        """
        tokens    = self._tokenize(text)
        oov       = self._extract_oov(tokens, lang_code)

        if len(oov) < self._min_oov:
            return self._insufficient_data(len(oov))

        alpha, r2   = self._fit_zipf(oov)
        alpha_z     = self._alpha_zscore(alpha)
        is_calc     = self._is_calculated_imperfection(alpha, r2, alpha_z)
        confidence  = self._compute_confidence(alpha, r2, alpha_z, is_calc)
        signal_val  = confidence if is_calc else 0.0

        fractura = (
            f"IMPERFECTION_CALCULATED: α={alpha:.3f} (esperado≈1.0), "
            f"R²={r2:.3f} (umbral={self._r2_threshold:.2f}), "
            f"z_α={alpha_z:.2f} — ruido artificial sin estructura fractal"
        ) if is_calc else None

        return {
            "is_calculated_imperfection": is_calc,
            "zipf_alpha":   round(alpha, 6),
            "zipf_r2":      round(r2, 6),
            "alpha_zscore": round(alpha_z, 6),
            "n_oov_tokens": len(oov),
            "confidence":   round(confidence, 6),
            "signal_value": round(signal_val, 6),
            "fractura":     fractura,
            "tool_name":    "GCI",
            "peirce_firstness":  (
                f"{len(oov)} anomalías léxicas detectadas; "
                "distribución de frecuencias analizada"
            ),
            "peirce_secondness": (
                f"Fit Zipf: α={alpha:.3f}, R²={r2:.3f}; "
                f"baseline humano α≈{self._alpha_mean:.2f}±{self._alpha_std:.2f}"
            ),
            "peirce_thirdness": (
                "HÁBITO DEL ATACANTE: randomización de errores para evadir "
                "detección de perfección → distribución no-fractal delata "
                "la intencionalidad artificial"
                if is_calc else
                "Distribución de errores consistente con variabilidad humana natural"
            ),
        }

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [
            w.lower() for w in re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3,}\b", text)
        ]

    @staticmethod
    def _extract_oov(tokens: List[str], lang_code: str) -> List[str]:
        """
        Extrae tokens Out-Of-Vocabulary heurísticos:
          - Mezcla dígitos+letras (l33tspeak)
          - 4+ consonantes consecutivas (≥75% del token)
          - Doble vocal no-diptongo

        SEGURIDAD: solo estructura fonológica — no evalúa contenido.

        DAUBERT NOTE: OOV extraction is purely structural (token frequency
        distribution) to evaluate fractal scaling (Zipf's Law). Semantic
        validation via lang_code is intentionally bypassed to avoid
        language-specific biases. The Zipf alpha coefficient and R² are
        language-agnostic statistical properties of the error distribution —
        not dependent on vocabulary membership in any specific language corpus.
        This design choice ensures reproducibility and cross-linguistic
        admissibility of the forensic metric.
        """
        oov: List[str] = []
        for token in tokens:
            if re.search(r"[a-zA-Z][0-9]|[0-9][a-zA-Z]", token):
                oov.append(token); continue
            consonants = re.sub(r"[aeiouáéíóúàèìòùäëïöüâêîôû]", "", token, flags=re.I)
            if len(consonants) >= 4 and len(consonants) / max(len(token), 1) > 0.75:
                oov.append(token); continue
            if re.search(r"[aou]{2,}|[áóú]{2,}", token):
                oov.append(token)
        return oov

    @staticmethod
    def _fit_zipf(tokens: List[str]) -> Tuple[float, float]:
        """
        Ajusta ley de potencia via regresión log-log (OLS, stdlib puro).
        Retorna (alpha, r2). Sin numpy — determinista en modo FALLBACK.
        """
        from collections import Counter
        freq = Counter(tokens)
        if len(freq) < 3:
            return 0.0, 0.0

        sorted_freqs = sorted(freq.values(), reverse=True)
        n         = len(sorted_freqs)
        log_ranks = [math.log(r + 1) for r in range(n)]
        log_freqs = [math.log(max(f, 1)) for f in sorted_freqs]

        mean_x = statistics.mean(log_ranks)
        mean_y = statistics.mean(log_freqs)
        ss_xy  = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_ranks, log_freqs))
        ss_xx  = sum((x - mean_x) ** 2 for x in log_ranks)

        if abs(ss_xx) < 1e-10:
            return 0.0, 0.0

        slope    = ss_xy / ss_xx
        alpha    = -slope
        intercept = mean_y - slope * mean_x
        y_pred   = [slope * x + intercept for x in log_ranks]
        ss_res   = sum((y - yp) ** 2 for y, yp in zip(log_freqs, y_pred))
        ss_tot   = sum((y - mean_y) ** 2 for y in log_freqs)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0.0

        return round(max(0.0, alpha), 6), round(max(0.0, min(1.0, r2)), 6)

    def _alpha_zscore(self, alpha: float) -> float:
        if self._alpha_std < 1e-9:
            return 0.0
        z = (alpha - self._alpha_mean) / self._alpha_std
        return round(max(-10.0, min(10.0, z)), 6)

    def _is_calculated_imperfection(
        self, alpha: float, r2: float, alpha_z: float
    ) -> bool:
        """Requiere ≥ 2 indicadores activos — conservador para Daubert."""
        active = sum([
            r2 < self._r2_threshold,
            abs(alpha - 1.0) > _ZIPF_ALPHA_DIVERGENCE,
            abs(alpha_z) > 2.0,
        ])
        return active >= 2

    def _compute_confidence(
        self, alpha: float, r2: float, alpha_z: float, is_calc: bool
    ) -> float:
        if not is_calc:
            return 0.0
        r2_p    = max(0.0, self._r2_threshold - r2) / self._r2_threshold
        alpha_p = min(1.0, abs(alpha - 1.0) / (2.0 * _ZIPF_ALPHA_DIVERGENCE))
        z_p     = min(1.0, abs(alpha_z) / 5.0)
        return round(min(1.0, max(0.05, (r2_p + alpha_p + z_p) / 3.0)), 6)

    @staticmethod
    def _insufficient_data(n_oov: int) -> Dict[str, Any]:
        return {
            "is_calculated_imperfection": False,
            "zipf_alpha": 0.0, "zipf_r2": 0.0, "alpha_zscore": 0.0,
            "n_oov_tokens": n_oov, "confidence": 0.0, "signal_value": 0.0,
            "fractura": None, "tool_name": "GCI",
            "reason": f"INSUFFICIENT_OOV_TOKENS (n={n_oov} < {_ZIPF_MIN_OOV_TOKENS})",
            "peirce_firstness":  f"Solo {n_oov} anomalías léxicas — muestra insuficiente",
            "peirce_secondness": "Análisis Zipf no aplicable",
            "peirce_thirdness":  "No determinable",
        }


@dataclass(frozen=True)
class ForensicVerdict:
    document_id: str
    emitter_id: str
    emitter_type: str
    language: str
    sda_nr: Dict[str, Any]
    cli: Dict[str, Any]
    acp: Dict[str, Any]
    roi: Dict[str, Any]
    mcp: float                        # Multiplicador de Certeza Pericial 1.0–5.0
    mcp_breakdown: Dict[str, float]
    final_verdict: str                # AUTÉNTICO | SOSPECHOSO | FABRICADO
    confidence: float
    fracturas: List[str]
    timestamp: str
    # GCI: análisis de imperfección calculada (Zipf) — opcional por compatibilidad
    zipf: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        d = {
            "document": {
                "id": self.document_id,
                "emitter": {"id": self.emitter_id, "type": self.emitter_type},
                "language": self.language,
            },
            "analisis_capas": {
                "sda_nr": self.sda_nr, "cli": self.cli,
                "acp": self.acp, "roi": self.roi,
            },
            "mcp": {
                "valor": round(self.mcp, 2),
                "desglose": {k: round(v, 4) for k, v in self.mcp_breakdown.items()},
            },
            "veredicto": {
                "categoria": self.final_verdict,
                "confianza": round(self.confidence, 4),
            },
            "fracturas_detectadas": self.fracturas,
            "timestamp": self.timestamp,
            "daubert_compliant": True,
        }
        if self.zipf is not None:
            d["analisis_capas"]["zipf_imperfection"] = self.zipf
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ============================================================================
# MOTOR FORENSE UNIFICADO
# ============================================================================

def calculate_entropy_profile(text: str) -> Dict[str, float]:
    """Calcula perfil de entropía léxica para ACP."""
    from collections import Counter
    words = re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", text.lower())
    if not words:
        return {"lexical_entropy": 0.0, "char_entropy": 0.0}
    freq = Counter(words)
    total = len(words)
    lex_entropy = -sum((c / total) * math.log2(c / total) for c in freq.values() if c > 0)
    chars = [c for c in text.lower() if c.isalpha()]
    if chars:
        cfreq = Counter(chars)
        ctotal = len(chars)
        char_entropy = -sum((c / ctotal) * math.log2(c / ctotal) for c in cfreq.values() if c > 0)
    else:
        char_entropy = 0.0
    return {"lexical_entropy": lex_entropy, "char_entropy": char_entropy}


class ForensicEngine:
    """Motor pericial unificado — orquesta SDA, CLI, ACP, ROI y calcula MCP."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        db_path: Optional[str] = None,
    ) -> None:
        self.config = ConfigLoader(config_path)
        self.db = ForensicDatabaseManager(db_path)
        self.sda = SDA_NominalizationAnalyzer(self.config)
        self.cli_analyzer = CLI_Analyzer(self.config)
        self.acp = ACP_Protocol(self.db, self.config)
        self.roi = ROI_Analyzer(self.config)
        self.lang_detector = LanguageDetector()
        # GCI: Zipf Imperfection Analyzer — detecta "imperfección calculada"
        self.zipf = ZipfImperfectionAnalyzer()

    def analyze(
        self,
        text: str,
        emitter_id: str,
        emitter_type: InstitutionalEmitter,
        document_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> ForensicVerdict:
        text = text[:MAX_TEXT_LENGTH]
        lang_code = language or self.lang_detector.detect(text).value
        entropy_profile = calculate_entropy_profile(text)
        lexical_entropy = entropy_profile.get("lexical_entropy", 0.0)

        sda_result  = self.sda.analyze(text, emitter_type, lang_code)
        cli_result  = self.cli_analyzer.analyze(text, emitter_type, lang_code)
        acp_result  = self.acp.analyze(text, emitter_id, emitter_type, lexical_entropy, lang_code)
        roi_result  = self.roi.analyze(text, emitter_type, lang_code)
        zipf_result = self.zipf.analyze(text, lang_code)

        mcp, breakdown, fracturas = self._calculate_mcp(
            sda_result, cli_result, acp_result, roi_result, zipf_result
        )

        verdict    = "FABRICADO" if mcp >= 4.0 else "SOSPECHOSO" if mcp >= 2.5 else "AUTÉNTICO"
        confidence = min(1.0, (mcp - 1.0) / 4.0)

        if acp_result.get("document_hash"):
            metrics = {
                "ttr": acp_result.get("current_ttr", 0.0),
                "entropy": lexical_entropy,
                "sync": acp_result.get("zscore_sync", 0.0),
            }
            updated = self.acp.update_baseline(
                emitter_id=emitter_id, emitter_type=emitter_type,
                language=lang_code, metrics=metrics,
                verdict=verdict, mcp=mcp,
                document_hash=acp_result["document_hash"],
            )
            if not updated:
                audit_logger.log_info(
                    event_type="BASELINE_UPDATE_REJECTED",
                    tool="ForensicEngine",
                    message=f"Baseline update rejected for {emitter_id} — MCP={mcp:.2f}",
                )

        doc_id = document_id or acp_result.get(
            "document_hash", hashlib.sha256(text.encode()).hexdigest()[:16]
        )

        return ForensicVerdict(
            document_id=doc_id, emitter_id=emitter_id,
            emitter_type=emitter_type.value, language=lang_code,
            sda_nr=sda_result, cli=cli_result, acp=acp_result, roi=roi_result,
            mcp=mcp, mcp_breakdown=breakdown, final_verdict=verdict,
            confidence=confidence, fracturas=fracturas, timestamp=_utcnow(),
            zipf=zipf_result,
        )

    def _calculate_mcp(
        self,
        sda: Dict, cli: Dict, acp: Dict, roi: Dict,
        zipf: Optional[Dict] = None,
    ) -> Tuple[float, Dict[str, float], List[str]]:
        breakdown = {"sda_nr": 0.0, "cli": 0.0, "acp": 0.0, "roi": 0.0, "gci_zipf": 0.0}
        fracturas: List[str] = []

        if sda.get("is_inconsistent"):
            breakdown["sda_nr"] = sda.get("fabrication_probability", 0.0)
            fracturas.append(f"SDA-NR: σ={sda.get('sigma_max', 0):.2f}")
        if cli.get("is_fabrication_indicator"):
            breakdown["cli"] = cli.get("fabrication_likelihood", 0.0)
            fracturas.append(f"CLI: stress={cli.get('cognitive_stress_index', 0):.2f}")
        if acp.get("is_identity_spoofing"):
            breakdown["acp"] = acp.get("spoofing_confidence", 0.0)
            fracturas.append(f"ACP: z_max={acp.get('max_zscore', 0):.2f}")
        if roi.get("is_obfuscation_attack"):
            breakdown["roi"] = roi.get("attack_confidence", 0.0)
            fracturas.append(f"ROI: {roi.get('obfuscation_type', 'UNKNOWN')}")

        # GCI: señal de imperfección calculada (Zipf) — nueva señal NLP
        # Se integra como componente independiente del cluster NLP.
        # Peso conservador (0.80) — señal nueva sin calibración real todavía.
        if zipf and zipf.get("is_calculated_imperfection"):
            zipf_conf = float(zipf.get("confidence", 0.0))
            breakdown["gci_zipf"] = round(zipf_conf * 0.80, 6)
            fracturas.append(
                f"GCI-ZIPF: α={zipf.get('zipf_alpha', 0):.3f} "
                f"R²={zipf.get('zipf_r2', 0):.3f} "
                f"z_α={zipf.get('alpha_zscore', 0):.2f} — "
                "IMPERFECTION_CALCULATED"
            )

        base   = sum(breakdown.values())
        active = sum(1 for v in breakdown.values() if v > 0.3)
        synergy = 1.0 + (active * 0.25) if active >= 2 else 1.0
        mcp = min(5.0, max(1.0, 1.0 + base * 2.5 * synergy))
        return mcp, breakdown, fracturas

    def export_for_sift(self, export_path: str) -> str:
        return self.db.export_for_sift(export_path)

    def save_config_template(self, path: str) -> None:
        self.config.save_default_config(path)


# ============================================================================
# CAPA P4: ESTILOMETRÍA FORENSE MULTILINGÜE
# Merge del canónico adversarial_nlp — 2026-05-02
# Autores: Gemini (diseño P4), Kimi (calibración), Claude (integración)
# ============================================================================

@dataclass(frozen=True)
class SyntacticDensityProfile:
    noun_count: int
    verb_count: int
    adj_count: int
    adv_count: int
    noun_verb_ratio: float
    nominalization_score: float
    syntactic_density_index: float
    language: str

    def to_dict(self) -> dict:
        return {
            "noun_count": self.noun_count,
            "verb_count": self.verb_count,
            "adj_count": self.adj_count,
            "adv_count": self.adv_count,
            "noun_verb_ratio": round(self.noun_verb_ratio, 4),
            "nominalization_score": round(self.nominalization_score, 4),
            "syntactic_density_index": round(self.syntactic_density_index, 4),
            "language": self.language,
        }


class SyntacticDensityAnalyzer:
    """
    Analizador de densidad sintáctica multilingüe.
    Aplica umbrales específicos según el idioma detectado.
    """

    def __init__(self):
        self.lang_detector = LanguageDetector()

    def _is_noun_proxy(self, word: str, profile: LanguageProfile) -> bool:
        w = word.lower()
        if w in profile.legal_markers or w in profile.technical_markers:
            return True
        for suffix in profile.noun_suffixes:
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                if any(w.endswith(vs) for vs in profile.verb_suffixes[:3]):
                    return False
                return True
        return False

    def _is_verb_proxy(self, word: str, profile: LanguageProfile) -> bool:
        w = word.lower()
        for suffix in profile.verb_suffixes:
            if w.endswith(suffix) and len(w) > len(suffix) + 1:
                return True
        return False

    def _is_adjective_proxy(self, word: str, profile: LanguageProfile) -> bool:
        w = word.lower()
        for suffix in profile.adj_suffixes:
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                return True
        return False

    def _is_adverb_proxy(self, word: str, profile: LanguageProfile) -> bool:
        w = word.lower()
        for suffix in profile.adv_suffixes:
            if w.endswith(suffix) and len(w) > len(suffix) + 2:
                return True
        if profile.code == "es":
            return w in {"muy", "más", "menos", "bastante", "demasiado", "poco", "mucho"}
        return w in {"very", "more", "most", "quite", "rather", "too", "so", "really"}

    def analyze(self, text: str) -> SyntacticDensityProfile:
        lang = self.lang_detector.detect(text)
        profile = self.lang_detector.get_profile(lang)
        if profile.code == "es":
            words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
        else:
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        total_words = len(words)
        if total_words == 0:
            return SyntacticDensityProfile(0, 0, 0, 0, 0.0, 0.0, 0.0, profile.code)
        nouns = sum(1 for w in words if self._is_noun_proxy(w, profile))
        verbs = sum(1 for w in words if self._is_verb_proxy(w, profile))
        adjectives = sum(1 for w in words if self._is_adjective_proxy(w, profile))
        adverbs = sum(1 for w in words if self._is_adverb_proxy(w, profile))
        nv_ratio = nouns / max(verbs, 1)
        content_words = max(nouns + verbs + adjectives, 1)
        nominalization = nouns / content_words
        sdi = ((nouns * 1.5) + (adjectives * 0.8)) / max(verbs + adverbs, 1)
        return SyntacticDensityProfile(
            noun_count=nouns, verb_count=verbs,
            adj_count=adjectives, adv_count=adverbs,
            noun_verb_ratio=nv_ratio, nominalization_score=nominalization,
            syntactic_density_index=sdi, language=profile.code,
        )

    def detect_syntactic_dance_malice(
        self,
        profile: SyntacticDensityProfile,
        declared_register: str = "legal_judicial",
    ) -> tuple:
        if declared_register != "legal_judicial":
            return False, 0.0, "SDA only applies to legal register"
        lang_prof = ENGLISH_PROFILE if profile.language == "en" else SPANISH_PROFILE
        violations = []
        severity_acc = 0.0
        if profile.noun_verb_ratio < lang_prof.nv_ratio_min:
            dev = (lang_prof.nv_ratio_min - profile.noun_verb_ratio) / lang_prof.nv_ratio_min
            severity_acc += min(0.5, dev * 0.5)
            violations.append(f"N/V={profile.noun_verb_ratio:.2f} < {lang_prof.nv_ratio_min}")
        if profile.nominalization_score < lang_prof.nominalization_min:
            dev = (lang_prof.nominalization_min - profile.nominalization_score) / lang_prof.nominalization_min
            severity_acc += min(0.4, dev * 0.4)
            violations.append(f"Nom={profile.nominalization_score:.2f} < {lang_prof.nominalization_min}")
        if profile.syntactic_density_index < 1.5:
            severity_acc += 0.3
            violations.append(f"SDI={profile.syntactic_density_index:.2f}")
        is_malice = len(violations) > 0 and severity_acc > 0.3
        reason = " | ".join(violations) if violations else "Syntax consistent with legal register"
        return is_malice, min(1.0, severity_acc), reason


class AuthorialFingerprintingEngine:
    """
    Motor de huella dactilar con TTR normalizado por idioma.
    Usa function words específicas para filtrado.
    """

    ZSCORE_CRITICAL: float = 2.0
    ZSCORE_SEVERE: float = 3.0

    def __init__(self):
        self.baselines: dict = {}
        self.lang_detector = LanguageDetector()

    def get_or_create_baseline(self, author_id: str, lang: Language) -> AuthorialBaseline:
        key = f"{author_id}_{lang.value if hasattr(lang, 'value') else lang}"
        if key not in self.baselines:
            self.baselines[key] = AuthorialBaseline(author_id=key)
        return self.baselines[key]

    def calculate_ttr(self, text: str, language: Optional[Language] = None) -> float:
        if language is None:
            language = self.lang_detector.detect(text)
        profile = self.lang_detector.get_profile(language)
        if profile.code == "es":
            words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
        else:
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return 0.0
        content_words = [w for w in words if w not in profile.function_words]
        if not content_words:
            return 0.0
        window_size = 400 if profile.code == "en" else 350
        if len(content_words) > window_size:
            ttrs = []
            for i in range(0, len(content_words) - window_size + 1, window_size):
                window = content_words[i:i + window_size]
                ttrs.append(len(set(window)) / len(window))
            return statistics.mean(ttrs) if ttrs else 0.0
        return len(set(content_words)) / len(content_words)

    def analyze_authorial_consistency(
        self, text: str, author_id: str,
        lexical_entropy: float, zipf_slope: float,
    ) -> dict:
        language = self.lang_detector.detect(text)
        current_ttr = self.calculate_ttr(text, language)
        baseline = self.get_or_create_baseline(author_id, language)
        if baseline.document_count < 2:
            baseline.update(current_ttr, lexical_entropy, zipf_slope)
            return {
                "author_id": author_id,
                "language": str(language),
                "baseline_documents": baseline.document_count,
                "current_ttr": round(current_ttr, 4),
                "zscore_ttr": 0.0,
                "is_inconsistent": False,
                "severity": 0.0,
                "reason": "INSUFFICIENT_BASELINE",
            }
        z_ttr = self._zscore(current_ttr, baseline.mean_ttr, baseline.std_ttr)
        z_lex = self._zscore(lexical_entropy, baseline.mean_lexical_entropy, baseline.std_ttr or 0.01)
        z_zipf = self._zscore(zipf_slope, baseline.mean_zipf, baseline.std_ttr or 0.01)
        outlier_dims = sum([
            abs(z_ttr) > self.ZSCORE_CRITICAL,
            abs(z_lex) > self.ZSCORE_CRITICAL,
            abs(z_zipf) > self.ZSCORE_CRITICAL,
        ])
        is_inconsistent = outlier_dims >= 2 or max(abs(z_ttr), abs(z_lex), abs(z_zipf)) > self.ZSCORE_SEVERE
        max_z = max(abs(z_ttr), abs(z_lex), abs(z_zipf))
        severity = (min(1.0, (max_z - self.ZSCORE_SEVERE) / 2.0 + 0.7)
                    if max_z > self.ZSCORE_SEVERE
                    else min(0.6, (max_z - self.ZSCORE_CRITICAL) / 1.0 + 0.3)
                    if max_z > self.ZSCORE_CRITICAL else 0.0)
        if not is_inconsistent:
            baseline.update(current_ttr, lexical_entropy, zipf_slope)
        return {
            "author_id": author_id,
            "language": str(language),
            "baseline_documents": baseline.document_count,
            "current_ttr": round(current_ttr, 4),
            "baseline_ttr_mean": round(baseline.mean_ttr, 4),
            "zscore_ttr": round(z_ttr, 4),
            "is_inconsistent": is_inconsistent,
            "severity": round(severity, 4),
            "reason": "AUTHORIAL_INCONSISTENCY" if is_inconsistent else "CONSISTENT",
        }

    @staticmethod
    def _zscore(value: float, mean: float, std: float) -> float:
        return 0.0 if std == 0 else (value - mean) / std


class GriceanMannerAnalyzer:
    """
    Análisis de Violación de Manera con Gunning Fog calibrado por idioma.
    """

    EN_AMBIGUITY_MARKERS: frozenset = frozenset({
        "perhaps", "maybe", "possibly", "probably", "likely", "presumably",
        "in a sense", "sort of", "kind of", "more or less", "approximately",
        "around", "about", "roughly", "somehow", "somewhat", "relatively",
        "fairly", "quite", "rather", "basically", "essentially", "practically",
        "allegedly", "reportedly", "supposedly", "apparently", "seemingly",
        "in due course", "as appropriate", "where applicable", "if necessary",
        "subject to", "without prejudice", "pending review",
    })
    ES_AMBIGUITY_MARKERS: frozenset = frozenset({
        "podría", "quizás", "tal vez", "posiblemente", "probablemente",
        "en cierto modo", "de alguna forma", "más o menos", "aproximadamente",
        "en torno a", "sin perjuicio de", "salvo mejor opinión",
        "a los efectos oportunos", "en su caso", "según corresponda",
        "previo análisis", "no obstante lo cual", "en virtud de lo expuesto",
    })

    def __init__(self):
        self.lang_detector = LanguageDetector()

    def count_syllables(self, word: str, language: Language) -> int:
        w = word.lower().strip()
        if not w:
            return 0
        vowels_es = "aeiouáéíóúü"
        vowels_en = "aeiouy"
        vowels = vowels_es if (hasattr(language, 'value') and
                               str(language) in ("Language.SPANISH", "SPANISH", "es")) else vowels_en
        syllables = 0
        prev_vowel = False
        for c in w:
            is_v = c in vowels
            if is_v and not prev_vowel:
                syllables += 1
            prev_vowel = is_v
        if vowels == vowels_en and w.endswith("e") and syllables > 1 and not w.endswith("le"):
            syllables -= 1
        return max(1, syllables)

    def analyze(self, text: str, declared_register: str = "legal_judicial") -> GriceanAnalysis:
        language = self.lang_detector.detect(text)
        profile = self.lang_detector.get_profile(language)
        if profile.code == "es":
            sentences = [s.strip() for s in re.split(r'[.!?;]+', text) if len(s.strip()) > 5]
            words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
        else:
            sentences = [s.strip() for s in re.split(r'[.!?;]+', text) if len(s.strip()) > 5]
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words or not sentences:
            return GriceanAnalysis(0.0, 0.0, 0.0, 0, 0.0, False, 0.0)
        avg_sent_len = len(words) / len(sentences)
        threshold = 2 if profile.code == "en" else 3
        complex_words = [w for w in words if self.count_syllables(w, language) > threshold]
        complex_ratio = len(complex_words) / len(words)
        fog = 0.4 * (avg_sent_len + 100 * complex_ratio)
        text_lower = text.lower()
        amb_markers = self.ES_AMBIGUITY_MARKERS if profile.code == "es" else self.EN_AMBIGUITY_MARKERS
        amb_count = sum(text_lower.count(m) for m in amb_markers)
        amb_density = amb_count / len(words)
        register_content_mismatch = (
            declared_register in ("legal_judicial", "academic_scientific")
            and fog > profile.fog_obscure
        )
        manner_score = 0.0
        if fog > profile.fog_obscure:
            manner_score += min(0.4, (fog - profile.fog_obscure) / 20.0)
        elif fog > profile.fog_complex:
            manner_score += min(0.2, (fog - profile.fog_complex) / 20.0)
        if amb_density > 0.05:
            manner_score += min(0.3, amb_density * 3.0)
        elif amb_density > 0.02:
            manner_score += min(0.15, amb_density * 2.0)
        if avg_sent_len > 40:
            manner_score += min(0.2, (avg_sent_len - 40) / 100.0)
        if register_content_mismatch:
            manner_score += 0.2
        severity = min(1.0, manner_score)
        return GriceanAnalysis(
            fog_index=round(fog, 4),
            ambiguity_density=round(amb_density, 4),
            avg_sentence_length=round(avg_sent_len, 4),
            ambiguity_count=amb_count,
            manner_violation_score=round(manner_score, 4),
            register_content_mismatch=register_content_mismatch,
            severity=round(severity, 4),
        )


# ============================================================================
# INTERFAZ PÚBLICA MCP
# ============================================================================

class VigiaAdversarialNLP:
    """Interfaz principal — compatible hacia atrás con análisis pericial integrado."""

    def __init__(
        self, config_path: Optional[str] = None, db_path: Optional[str] = None
    ) -> None:
        self.engine = ForensicEngine(config_path, db_path)

    def analyze_document(
        self,
        document_path: str,
        declared_register: str = "legal_judicial",
        auto_inject_caie: bool = True,
        author_id: Optional[str] = None,
        emitter_type: str = "UNKNOWN",
        force_language: Optional[str] = None,
        **_kwargs: Any,
    ) -> Dict:
        ext = Path(document_path).suffix.lower()
        if ext == ".pdf":
            text = self._extract_pdf(document_path)
        else:
            with open(_sanitize_path(document_path, must_exist=True), "r",
                      encoding="utf-8", errors="ignore") as f:
                text = f.read()

        try:
            inst_type = InstitutionalEmitter[emitter_type.upper()]
        except KeyError:
            inst_type = InstitutionalEmitter.UNKNOWN

        verdict = self.engine.analyze(
            text=text,
            emitter_id=author_id or f"unknown_{inst_type.name.lower()}",
            emitter_type=inst_type,
            language=force_language,
        )

        if auto_inject_caie and verdict.fracturas:
            self._inject_caie_fractures(verdict)

        return verdict.to_dict()

    def _extract_pdf(self, path: str) -> str:
        try:
            import PyPDF2
            parts: List[str] = []
            with open(_sanitize_path(path, must_exist=True), "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
            return "\n".join(parts)
        except Exception as exc:
            audit_logger.log_info(
                event_type="PDF_EXTRACTION_FAILED",
                tool="VigiaAdversarialNLP",
                message=str(exc),
            )
            return ""

    def _inject_caie_fractures(self, verdict: ForensicVerdict) -> None:
        if not _CAIE_AVAILABLE or CrossArtifactIncongruenceEngine is None:
            return
        try:
            caie = CrossArtifactIncongruenceEngine()
            for fractura in verdict.fracturas:
                caie.add_from_tool_result(
                    source_tool="vigia_adversarial_nlp",
                    evidence_type="linguistic_forensics",
                    raw_score=verdict.mcp,
                    description=fractura,
                    metadata={"mcp": verdict.mcp, "language": verdict.language,
                              "verdict": verdict.final_verdict},
                )
        except Exception as exc:
            audit_logger.log_info(
                event_type="CAIE_INJECTION_FAILED",
                tool="VigiaAdversarialNLP",
                message=str(exc),
            )

    def export_database(self, path: str) -> str:
        return self.engine.export_for_sift(path)


async def analyze_document_register(
    document_path: str,
    declared_register: str = "legal_judicial",
    auto_inject_caie: bool = True,
    author_id: Optional[str] = None,
    emitter_type: str = "UNKNOWN",
    content_category: Optional[str] = None,
    force_language: Optional[str] = None,
    export_db_path: Optional[str] = None,
) -> Dict:
    """MCP Tool: análisis pericial completo con MCP y exportación opcional para SIFT."""
    try:
        analyzer = VigiaAdversarialNLP()
        result = analyzer.analyze_document(
            document_path=document_path,
            declared_register=declared_register,
            auto_inject_caie=auto_inject_caie,
            author_id=author_id,
            emitter_type=emitter_type,
            force_language=force_language,
        )
        if export_db_path:
            result["sift_export_path"] = analyzer.export_database(export_db_path)
        return result
    except Exception as exc:
        audit_logger.log_block(
            event_type="PERICIAL_ANALYSIS_ERROR",
            tool="analyze_document_register",
            input_preview=document_path,
            reason=str(exc),
        )
        return {
            "status": "ERROR",
            "error": str(exc),
            "document_path": document_path,
            "timestamp": _utcnow(),
        }
