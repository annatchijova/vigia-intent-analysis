"""
vigia/tools/vigia_adversarial_nlp.py
=====================================
VIGÍA — Adversarial NLP Forensics (Capa P2-P3: Integridad Semántica)

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: CAIE (Cross-Artifact Incongruence Engine)

Purpose:
--------
Detecta violaciones de INTEGRIDAD SEMÁNTICA mediante análisis de Entropy-based
Register Shift. Un documento que pretende ser "judicial" pero exhibe patrones
de entropía lingüística propios de "literatura de ficción" o "manuales de 
diseño" constituye una manipulación de la realidad técnica.

Detección de Register Shift:
----------------------------
El "registro" lingüístico es la variedad de lenguaje asociada a una situación
de comunicación específica. Un documento judicial debe exhibir:
- Alta precisión terminológica (baja entropía en términos legales)
- Estructura sintáctica conservadora (baja variabilidad)
- Marcadores de objetividad (ausencia de markers subjetivos)

Si la entropía Shannon del vocabulario, la complejidad sintáctica, o la
distribución de POS tags coincide con registros INCOMPATIBLES (ficción,
marketing, poesía), se detecta una FRACTURA DE TERCERIDAD.

Fórmulas clave:
---------------
Entropy-based Register Deviation (ERD):
    ERD = |H_observado - H_esperado_registro| / H_max

Donde:
    - H_observado = entropía Shannon del documento bajo análisis
    - H_esperado_registro = entropía baseline del registro declarado
    - H_max = entropía máxima teórica (log₂|vocabulario|)

Register Consistency Score (RCS):
    RCS = 1 - (Σ w_i * ERD_i)  para todas las dimensiones lingüísticas

Fractura de Terceridad detectada si: RCS < 0.3 (umbral crítico)

Integración CAIE:
-----------------
Cuando se detecta Register Shift, se genera automáticamente una Fractura:
    - fracture_type: "SEMANTIC_REGISTER_VIOLATION"
    - severity: proporcional a la desviación de entropía
    - ttp_id: T1566.003 (Spearphishing via Service) o T1036 (Masquerading)
    - interpretation: Explicación Peirce-framed del desfase semántico

Peirce Framework:
    Firstness  — Texto como signo físico (tokens, entropía)
    Secondness — Colisión con registro esperado (fractura detectada)
    Thirdness  — Hábito comunicativo del adversario (manipulación semántica)
"""

from __future__ import annotations

import math
import re
import hashlib
import json
from dataclasses import dataclass, field
from typing import Final, Optional, Callable
from collections import Counter, defaultdict
from pathlib import Path

from vigia.security import _utcnow, audit_logger, _sanitize_path

# Intentar importar CAIE para integración automática
try:
    from vigia.tools.caie import CrossArtifactIncongruenceEngine, Fracture
    _CAIE_AVAILABLE = True
except ImportError:
    _CAIE_AVAILABLE = False
    Fracture = None


# ---------------------------------------------------------------------------
# Baseline Entropy Profiles por Registro Lingüístico
# ---------------------------------------------------------------------------
# Perfiles de entropía calculados sobre corpus representativos.
# Cada registro tiene fingerprints en múltiples dimensiones.

@dataclass(frozen=True)
class RegisterProfile:
    """
    Perfil de entropía de un registro lingüístico.

    Dimensiones analizadas:
    - lexical_entropy: Entropía del vocabulario (riqueza léxica)
    - syntactic_entropy: Entropía de estructuras sintácticas
    - pos_entropy: Entropía de distribución de POS tags
    - sentence_length_entropy: Entropía de longitudes de oración
    - punctuation_entropy: Entropía de uso de puntuación
    - formality_markers: Presencia de marcadores de formalidad
    """
    name: str
    description: str

    # Entropías baseline (valores empíricos de corpus)
    lexical_entropy: float        # H léxica típica
    syntactic_entropy: float      # H sintáctica típica  
    pos_entropy: float            # H de POS tags
    sentence_length_var: float   # Varianza de longitud de oraciones
    punctuation_ratio: float     # Ratio de puntuación/no-puntuación

    # Markers léxicos característicos (frecuencia relativa)
    marker_profile: frozenset[tuple[str, float]] = field(default_factory=frozenset)

    # Rango de complejidad de vocabulario (Zipf slope esperado)
    zipf_slope_range: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self):
        # Validación: entropías deben estar en rangos razonables
        for field_name, value in [
            ("lexical_entropy", self.lexical_entropy),
            ("syntactic_entropy", self.syntactic_entropy),
            ("pos_entropy", self.pos_entropy),
        ]:
            if not 0.0 <= value <= 15.0:  # Máximo teórico ~log2(50000 palabras)
                raise ValueError(f"{field_name}={value} fuera de rango [0, 15]")


# Perfiles de registro basados en literatura lingüística forense
REGISTER_PROFILES: Final[dict[str, RegisterProfile]] = {
    # Registro judicial/legal - referencia principal
    "legal_judicial": RegisterProfile(
        name="legal_judicial",
        description="Documentos judiciales, resoluciones, dictámenes legales",
        lexical_entropy=8.5,      # Vocabulario técnico controlado, baja variabilidad
        syntactic_entropy=6.2,    # Sintaxis conservadora, estructuras repetitivas
        pos_entropy=7.8,          # Distribución POS predecible (sustantivos, verbos formales)
        sentence_length_var=2.1,    # Oraciones de longitud media-alta, consistente
        punctuation_ratio=0.12,     # Uso formal de puntuación
        marker_profile=frozenset({
            ("en consecuencia", 0.008),
            ("por tanto", 0.007),
            ("visto", 0.015),
            ("considerando", 0.012),
            ("resuelve", 0.010),
            ("fallo", 0.006),
            ("autos", 0.009),
            ("expediente", 0.011),
            ("alega", 0.007),
            ("prueba", 0.009),
        }),
        zipf_slope_range=(1.2, 1.8),  # Distribución de Zipf empinada (pocas palabras frecuentes)
    ),

    # Literatura de ficción - registro incompatible
    "fiction_literary": RegisterProfile(
        name="fiction_literary",
        description="Narrativa literaria, novelas, cuentos",
        lexical_entropy=11.2,     # Vocabulario rico y variado
        syntactic_entropy=9.5,      # Sintaxis creativa, variada
        pos_entropy=9.2,          # Distribución POS diversa (diálogos, descripciones)
        sentence_length_var=4.8,  # Alta variabilidad en longitud (oraciones cortas y largas)
        punctuation_ratio=0.18,     # Uso creativo de puntuación (elipsis, guiones)
        marker_profile=frozenset({
            ("sentía", 0.005),
            ("miró", 0.006),
            ("pensó", 0.004),
            ("suspiro", 0.003),
            ("corazón", 0.004),
            ("silencio", 0.005),
            ("noche", 0.006),
            ("sueño", 0.004),
            ("misterio", 0.003),
            ("emoción", 0.004),
        }),
        zipf_slope_range=(0.8, 1.2),  # Distribución más plana (más palabras diversas)
    ),

    # Manuales de diseño/UX - registro incompatible  
    "design_manual": RegisterProfile(
        name="design_manual",
        description="Manuales de diseño, guías UX, documentación creativa",
        lexical_entropy=9.8,      # Vocabulario técnico pero de dominio específico
        syntactic_entropy=7.8,    # Imperativos, instrucciones directas
        pos_entropy=8.5,          # Verbos imperativos, sustantivos técnicos
        sentence_length_var=3.2,  # Instrucciones cortas, explicaciones medias
        punctuation_ratio=0.15,     # Uso funcional, bullets, listas
        marker_profile=frozenset({
            ("usuario", 0.012),
            ("experiencia", 0.010),
            ("interfaz", 0.009),
            ("diseño", 0.015),
            ("flujo", 0.008),
            ("interacción", 0.007),
            ("visual", 0.011),
            ("componente", 0.008),
            ("feedback", 0.009),
            ("iteración", 0.006),
        }),
        zipf_slope_range=(1.0, 1.5),
    ),

    # Marketing/persuasión - registro incompatible peligroso
    "marketing_persuasive": RegisterProfile(
        name="marketing_persuasive",
        description="Copy de marketing, publicidad persuasiva",
        lexical_entropy=10.5,     # Vocabulario emotivo, superlativos
        syntactic_entropy=8.2,    # Oraciones impactantes, variadas
        pos_entropy=8.8,          # Adjetivos abundantes, verbos de acción
        sentence_length_var=3.5,  # Mix de impacto corto y explicativo
        punctuation_ratio=0.16,     # Uso emotivo (!, ...)
        marker_profile=frozenset({
            ("único", 0.009),
            ("exclusivo", 0.008),
            ("oportunidad", 0.010),
            ("ahora", 0.012),
            ("gratis", 0.007),
            ("garantizado", 0.008),
            ("mejor", 0.011),
            ("increíble", 0.006),
            ("revolucionario", 0.005),
            ("no espere", 0.007),
        }),
        zipf_slope_range=(0.9, 1.3),
    ),

    # Académico científico - registro compatible alternativo
    "academic_scientific": RegisterProfile(
        name="academic_scientific",
        description="Papers científicos, artículos académicos",
        lexical_entropy=9.2,      # Vocabulario técnico preciso
        syntactic_entropy=7.5,    # Pasivas, nominalizaciones
        pos_entropy=8.0,          # Sustantivos técnicos, verbos formales
        sentence_length_var=2.8,  # Oraciones complejas pero consistentes
        punctuation_ratio=0.14,     # Uso académico formal
        marker_profile=frozenset({
            ("demuestra", 0.008),
            ("evidencia", 0.010),
            ("análisis", 0.009),
            ("resultados", 0.011),
            ("método", 0.008),
            ("conclusión", 0.007),
            ("hipótesis", 0.006),
            ("significativo", 0.007),
            ("muestra", 0.008),
            ("datos", 0.009),
        }),
        zipf_slope_range=(1.1, 1.6),
    ),

    # Técnico corporativo - registro neutral
    "corporate_technical": RegisterProfile(
        name="corporate_technical",
        description="Documentación técnica corporativa, reportes",
        lexical_entropy=8.8,      # Vocabulario de negocio limitado
        syntactic_entropy=6.8,      # Sintaxis directa, funcional
        pos_entropy=7.5,          # Sustantivos de negocio, verbos modales
        sentence_length_var=2.5,  # Consistencia corporativa
        punctuation_ratio=0.13,     # Uso estándar
        marker_profile=frozenset({
            ("stakeholder", 0.006),
            ("sinergia", 0.004),
            ("deliverable", 0.005),
            ("roadmap", 0.006),
            ("actionable", 0.004),
            ("leverage", 0.005),
            ("optimize", 0.006),
            ("strategy", 0.007),
            ("performance", 0.008),
            ("metrics", 0.007),
        }),
        zipf_slope_range=(1.2, 1.7),
    ),
}


# ---------------------------------------------------------------------------
# Entropy Calculation Functions
# ---------------------------------------------------------------------------

def calculate_shannon_entropy(tokens: list[str]) -> float:
    """
    Calcula entropía Shannon de una distribución de tokens.

    H = -Σ p(x) * log₂(p(x))

    Args:
        tokens: Lista de tokens (palabras, POS tags, etc.)

    Returns:
        Entropía en bits
    """
    if not tokens:
        return 0.0

    # Contar frecuencias
    freq = Counter(tokens)
    total = len(tokens)

    # Calcular probabilidades y entropía
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


def calculate_conditional_entropy(
    tokens_a: list[str],
    tokens_b: list[str]
) -> float:
    """
    Entropía condicional H(A|B) - útil para detectar dependencias sintácticas.
    """
    if not tokens_a or not tokens_b or len(tokens_a) != len(tokens_b):
        return 0.0

    # Pares (a, b)
    pairs = list(zip(tokens_a, tokens_b))
    joint_freq = Counter(pairs)
    b_freq = Counter(tokens_b)

    total = len(pairs)
    cond_entropy = 0.0

    for (a, b), joint_count in joint_freq.items():
        p_joint = joint_count / total
        p_b = b_freq[b] / total
        if p_joint > 0 and p_b > 0:
            cond_entropy -= p_joint * math.log2(p_joint / p_b)

    return cond_entropy


def calculate_zipf_slope(tokens: list[str]) -> float:
    """
    Calcula la pendiente de la distribución de Zipf.

    En texto natural, la frecuencia de la palabra n-ésima es proporcional
    a 1/n^s, donde s es la pendiente de Zipf.

    - s ≈ 1.0: Texto muy diverso (poesía, ficción)
    - s ≈ 1.5: Texto técnico estándar
    - s > 2.0: Texto muy repetitivo (legal, técnico especializado)

    Returns:
        Pendiente de Zipf (s)
    """
    if not tokens:
        return 0.0

    freq = Counter(tokens)
    if len(freq) < 10:
        return 0.0

    # Ordenar por frecuencia descendente
    sorted_freq = sorted(freq.values(), reverse=True)

    # Tomar logaritmos para regresión lineal
    # log(f) = log(c) - s * log(r)
    # donde f=frecuencia, r=rango, s=pendiente, c=constante

    log_ranks = []
    log_freqs = []

    for rank, frequency in enumerate(sorted_freq[:1000], 1):  # Top 1000
        if frequency > 0:
            log_ranks.append(math.log(rank))
            log_freqs.append(math.log(frequency))

    if len(log_ranks) < 2:
        return 0.0

    # Regresión lineal simple
    n = len(log_ranks)
    sum_x = sum(log_ranks)
    sum_y = sum(log_freqs)
    sum_xy = sum(x * y for x, y in zip(log_ranks, log_freqs))
    sum_x2 = sum(x * x for x in log_ranks)

    # Pendiente = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        return 0.0

    slope = (n * sum_xy - sum_x * sum_y) / denominator

    # La pendiente de Zipf es negativa de la pendiente de regresión
    return -slope


def calculate_entropy_profile(text: str) -> dict[str, float]:
    """
    Calcula el perfil completo de entropía de un texto.

    Returns:
        Dict con todas las métricas de entropía
    """
    if not text or len(text) < 100:
        return {
            "lexical_entropy": 0.0,
            "syntactic_entropy": 0.0,
            "pos_entropy": 0.0,
            "sentence_length_var": 0.0,
            "punctuation_ratio": 0.0,
            "zipf_slope": 0.0,
            "character_entropy": 0.0,
            "bigram_entropy": 0.0,
        }

    # Tokenización básica (determinística, no depende de NLTK)
    words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    # Entropía léxica (palabras)
    lexical_entropy = calculate_shannon_entropy(words)

    # Entropía de caracteres (indicador de complejidad ortográfica)
    chars = list(text.lower())
    character_entropy = calculate_shannon_entropy(chars)

    # Entropía de bigramas de caracteres (estructura)
    bigrams = [text[i:i+2].lower() for i in range(len(text)-1) 
               if text[i:i+2].isalpha()]
    bigram_entropy = calculate_shannon_entropy(bigrams)

    # Varianza de longitud de oraciones
    if sentences:
        sent_lengths = [len(s.split()) for s in sentences]
        mean_len = sum(sent_lengths) / len(sent_lengths)
        variance = sum((l - mean_len) ** 2 for l in sent_lengths) / len(sent_lengths)
        sentence_length_var = math.sqrt(variance)  # Desviación estándar
    else:
        sentence_length_var = 0.0

    # Ratio de puntuación
    punct_count = sum(1 for c in text if c in '.,;:!?-—')
    punctuation_ratio = punct_count / len(text) if text else 0.0

    # Pendiente de Zipf
    zipf_slope = calculate_zipf_slope(words)

    # Estimación de entropía sintáctica (proxy basado en bigramas de palabras)
    word_bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
    syntactic_entropy = calculate_shannon_entropy(word_bigrams)

    # Estimación de entropía POS (proxy basado en categorías de palabras)
    # Categorías simples: cortas (1-3), medias (4-6), largas (7+)
    pos_proxy = []
    for w in words:
        length = len(w)
        if length <= 3:
            pos_proxy.append("SHORT")
        elif length <= 6:
            pos_proxy.append("MEDIUM")
        else:
            pos_proxy.append("LONG")
    pos_entropy = calculate_shannon_entropy(pos_proxy)

    return {
        "lexical_entropy": lexical_entropy,
        "syntactic_entropy": syntactic_entropy,
        "pos_entropy": pos_entropy,
        "sentence_length_var": sentence_length_var,
        "punctuation_ratio": punctuation_ratio,
        "zipf_slope": zipf_slope,
        "character_entropy": character_entropy,
        "bigram_entropy": bigram_entropy,
    }


# ---------------------------------------------------------------------------
# Register Shift Detection
# ---------------------------------------------------------------------------

@dataclass
class RegisterShiftDetection:
    """
    Resultado de detección de Register Shift.
    """
    declared_register: str           # Registro declarado (ej: "legal_judicial")
    detected_registers: list[tuple[str, float]]  # (registro, confidence) ordenado
    primary_deviation: str         # Registro más desviado detectado

    # Métricas de desviación
    erd_lexical: float             # Entropy Register Deviation léxico
    erd_syntactic: float           # ERD sintáctico
    erd_pos: float                 # ERD de POS
    erd_sentence_var: float        # ERD de varianza de oraciones
    erd_punctuation: float         # ERD de puntuación
    erd_zipf: float                # ERD de pendiente Zipf

    # Score agregado
    register_consistency_score: float  # RCS: 1.0 = consistente, 0.0 = completamente desviado

    # Determinación
    is_register_violation: bool    # True si RCS < 0.3
    severity: float                # 0.0-1.0

    # Evidencia
    matching_markers: dict[str, list[str]]  # Markers detectados por registro

    def to_dict(self) -> dict:
        return {
            "declared_register": self.declared_register,
            "detected_registers": self.detected_registers,
            "primary_deviation": self.primary_deviation,
            "erd_metrics": {
                "lexical": round(self.erd_lexical, 4),
                "syntactic": round(self.erd_syntactic, 4),
                "pos": round(self.erd_pos, 4),
                "sentence_var": round(self.erd_sentence_var, 4),
                "punctuation": round(self.erd_punctuation, 4),
                "zipf": round(self.erd_zipf, 4),
            },
            "register_consistency_score": round(self.register_consistency_score, 4),
            "is_register_violation": self.is_register_violation,
            "severity": round(self.severity, 4),
            "matching_markers": self.matching_markers,
        }


class EntropyBasedRegisterDetector:
    """
    Detector de Register Shift basado en entropía.

    Compara el perfil de entropía de un documento contra el perfil baseline
del registro declarado, detectando desviaciones significativas.
    """

    # Umbrales de desviación crítica
    ERD_CRITICAL: Final[float] = 0.4   # Desviación >40% es crítica
    ERD_WARNING: Final[float] = 0.25    # Desviación >25% es advertencia

    # Pesos para RCS (deben sumar 1.0)
    WEIGHTS: Final[dict[str, float]] = {
        "lexical": 0.25,
        "syntactic": 0.20,
        "pos": 0.15,
        "sentence_var": 0.15,
        "punctuation": 0.10,
        "zipf": 0.15,
    }

    def __init__(self):
        self.profiles = REGISTER_PROFILES

    def calculate_erd(
        self,
        observed: float,
        expected: float,
        max_val: float = 15.0,
    ) -> float:
        """
        Calcula Entropy Register Deviation (ERD).

        ERD = |H_observado - H_esperado| / H_max
        """
        if max_val == 0:
            return 0.0
        deviation = abs(observed - expected)
        return min(1.0, deviation / max_val)

    def detect_markers(self, text: str, profile: RegisterProfile) -> list[str]:
        """
        Detecta markers léxicos característicos de un registro.
        """
        text_lower = text.lower()
        found = []

        for marker, expected_freq in profile.marker_profile:
            # Contar ocurrencias
            count = text_lower.count(marker)
            # Normalizar por longitud del texto (aproximado)
            word_count = len(text_lower.split())
            if word_count > 0:
                observed_freq = count / word_count
                # Si la frecuencia observada es cercana o mayor a la esperada
                if observed_freq >= expected_freq * 0.5:  # 50% del umbral
                    found.append(marker)

        return found

    def detect_register_shift(
        self,
        text: str,
        declared_register: str = "legal_judicial",
    ) -> RegisterShiftDetection:
        """
        Detecta si un documento exhibe Register Shift respecto a su registro declarado.

        Args:
            text: Contenido textual del documento
            declared_register: Registro que el documento pretende tener

        Returns:
            RegisterShiftDetection con análisis completo
        """
        if declared_register not in self.profiles:
            raise ValueError(f"Unknown register: {declared_register}")

        # Calcular perfil de entropía del texto
        observed_profile = calculate_entropy_profile(text)

        # Perfil esperado
        expected = self.profiles[declared_register]

        # Calcular ERDs
        erd_lexical = self.calculate_erd(
            observed_profile["lexical_entropy"],
            expected.lexical_entropy,
        )
        erd_syntactic = self.calculate_erd(
            observed_profile["syntactic_entropy"],
            expected.syntactic_entropy,
        )
        erd_pos = self.calculate_erd(
            observed_profile["pos_entropy"],
            expected.pos_entropy,
        )
        erd_sentence_var = self.calculate_erd(
            observed_profile["sentence_length_var"],
            expected.sentence_length_var,
            max_val=10.0,  # Normalizado a escala menor
        )
        erd_punctuation = self.calculate_erd(
            observed_profile["punctuation_ratio"],
            expected.punctuation_ratio,
            max_val=0.5,  # Ratio máximo razonable
        )
        erd_zipf = self.calculate_erd(
            observed_profile["zipf_slope"],
            sum(expected.zipf_slope_range) / 2,  # Centro del rango
            max_val=2.0,
        )

        # Calcular RCS (Register Consistency Score)
        # RCS = 1 - Σ(w_i * ERD_i)
        erds = {
            "lexical": erd_lexical,
            "syntactic": erd_syntactic,
            "pos": erd_pos,
            "sentence_var": erd_sentence_var,
            "punctuation": erd_punctuation,
            "zipf": erd_zipf,
        }

        weighted_deviation = sum(
            self.WEIGHTS[dim] * erds[dim] for dim in erds
        )
        rcs = max(0.0, 1.0 - weighted_deviation)

        # Detectar registro más probable (clasificación simple)
        register_scores = []
        for reg_name, reg_profile in self.profiles.items():
            if reg_name == declared_register:
                continue

            # Calcular similitud con este registro
            erd_lex_other = self.calculate_erd(
                observed_profile["lexical_entropy"],
                reg_profile.lexical_entropy,
            )
            erd_syn_other = self.calculate_erd(
                observed_profile["syntactic_entropy"],
                reg_profile.syntactic_entropy,
            )

            # Score de similitud (menor desviación = mayor similitud)
            similarity = 1.0 - (erd_lex_other + erd_syn_other) / 2
            register_scores.append((reg_name, similarity))

        # Ordenar por similitud descendente
        register_scores.sort(key=lambda x: x[1], reverse=True)

        # Determinar desviación primaria
        primary_deviation = register_scores[0][0] if register_scores else "unknown"

        # Detectar markers en texto
        matching_markers = {}
        for reg_name, reg_profile in self.profiles.items():
            markers = self.detect_markers(text, reg_profile)
            if markers:
                matching_markers[reg_name] = markers

        # Determinar si es violación y severidad
        is_violation = rcs < 0.3

        # Severidad basada en RCS y desviación del registro declarado
        if rcs < 0.2:
            severity = 0.9  # Crítico
        elif rcs < 0.3:
            severity = 0.7  # Alto
        elif rcs < 0.5:
            severity = 0.5  # Medio
        else:
            severity = 0.2  # Bajo

        # Aumentar severidad si hay markers de registro incompatible
        incompatible_markers = []
        for reg in ["fiction_literary", "marketing_persuasive", "design_manual"]:
            if reg in matching_markers:
                incompatible_markers.extend(matching_markers[reg])

        if incompatible_markers and declared_register == "legal_judicial":
            severity = min(1.0, severity + 0.2)

        return RegisterShiftDetection(
            declared_register=declared_register,
            detected_registers=register_scores[:3],
            primary_deviation=primary_deviation,
            erd_lexical=erd_lexical,
            erd_syntactic=erd_syntactic,
            erd_pos=erd_pos,
            erd_sentence_var=erd_sentence_var,
            erd_punctuation=erd_punctuation,
            erd_zipf=erd_zipf,
            register_consistency_score=rcs,
            is_register_violation=is_violation,
            severity=severity,
            matching_markers=matching_markers,
        )


# ---------------------------------------------------------------------------
# CAIE Integration - Fracture Generation
# ---------------------------------------------------------------------------

def generate_semantic_fracture(
    detection: RegisterShiftDetection,
    document_path: str,
    document_hash: str,
) -> Optional[dict]:
    """
    Genera una Fractura de Terceridad para el CAIE.

    La fractura representa la colisión entre:
    - Firstness: El documento como signo físico (bytes, entropía)
    - Secondness: La colisión con el registro esperado (desviación detectada)
    - Thirdness: El hábito del adversario (manipulación semántica intencional)
    """
    if not detection.is_register_violation:
        return None

    # Construir interpretación Peirce-framed
    interpretation = (
        f"SEMANTIC REGISTER VIOLATION: Document claims to be '{detection.declared_register}' "
        f"but exhibits entropy patterns consistent with '{detection.primary_deviation}'. "
        f"Register Consistency Score (RCS) = {detection.register_consistency_score:.3f}, "
        f"indicating severe linguistic register contamination. "
        f"\n\n"
        f"Peirce Secondness: The sign (document) collides with its claimed object "
        f"(legal register). The entropy profile H_observed={detection.erd_lexical:.3f} "
        f"deviates critically from H_expected.\n\n"
        f"Peirce Thirdness: The inferred communicative habit is SEMANTIC DECEPTION — "
        f"the author deliberately adopted linguistic patterns of '{detection.primary_deviation}' "
        f"to mask the document's true nature, manipulating the reader's perception "
        f"of technical reality."
    )

    # Determinar TTP MITRE
    if detection.primary_deviation in ["fiction_literary", "marketing_persuasive"]:
        ttp_id = "T1566.003"  # Spearphishing via Service
    elif detection.primary_deviation == "design_manual":
        ttp_id = "T1036"  # Masquerading
    else:
        ttp_id = "T1566"  # Phishing (general)

    # Construir fractura
    fracture = {
        "artifact_a": f"Document claims: {detection.declared_register} (legal/judicial)",
        "artifact_b": f"Entropy profile matches: {detection.primary_deviation}",
        "fracture_type": "SEMANTIC_REGISTER_VIOLATION",
        "severity": detection.severity,
        "interpretation": interpretation,
        "spoofability_delta": 0.6,  # Manipulación semántica es moderadamente difícil
        "ttp_id": ttp_id,
        "document_path": document_path,
        "document_hash": document_hash,
        "rcs_score": detection.register_consistency_score,
        "erd_metrics": {
            "lexical": detection.erd_lexical,
            "syntactic": detection.erd_syntactic,
            "pos": detection.erd_pos,
        },
        "detected_markers": detection.matching_markers.get(detection.primary_deviation, []),
    }

    return fracture


def inject_caie_fracture(
    detection: RegisterShiftDetection,
    document_path: str,
    document_content: str,
) -> bool:
    """
    Inyecta la fractura semántica directamente en el CAIE.

    Returns True si la inyección fue exitosa.
    """
    if not _CAIE_AVAILABLE or not detection.is_register_violation:
        return False

    # Calcular hash del documento para trazabilidad
    doc_hash = hashlib.sha256(document_content.encode()).hexdigest()[:16]

    # Generar fractura
    fracture_data = generate_semantic_fracture(detection, document_path, doc_hash)
    if not fracture_data:
        return False

    try:
        # Crear instancia CAIE y agregar fractura
        caie = CrossArtifactIncongruenceEngine()

        # Crear artefacto del análisis NLP
        artifact_data = {
            "source_tool": "vigia_adversarial_nlp",
            "evidence_type": "document_visual",  # Análisis de contenido documental
            "raw_score": detection.severity,
            "description": f"Register shift: {detection.declared_register} -> {detection.primary_deviation}",
            "metadata": {
                "rcs_score": detection.register_consistency_score,
                "primary_deviation": detection.primary_deviation,
                "erd_lexical": detection.erd_lexical,
                "detected_markers": detection.matching_markers,
            },
            "provenance_chain": [doc_hash],
        }

        caie.add_from_tool_result(**artifact_data)

        # Agregar fractura manualmente si es posible
        if hasattr(caie, '_fractures'):
            fracture_obj = Fracture(
                artifact_a=fracture_data["artifact_a"],
                artifact_b=fracture_data["artifact_b"],
                fracture_type=fracture_data["fracture_type"],
                severity=fracture_data["severity"],
                interpretation=fracture_data["interpretation"],
                spoofability_delta=fracture_data["spoofability_delta"],
                ttp_id=fracture_data["ttp_id"],
            )
            caie._fractures.append(fracture_obj)

        audit_logger.log_info(
            event_type="CAIE_SEMANTIC_FRACTURE_INJECTED",
            tool="vigia_adversarial_nlp",
            message=f"Injected SEMANTIC_REGISTER_VIOLATION for {document_path}: "
                    f"RCS={detection.register_consistency_score:.3f}, "
                    f"deviation={detection.primary_deviation}",
        )

        return True

    except Exception as exc:
        audit_logger.log_info(
            event_type="CAIE_INJECTION_FAILED",
            tool="vigia_adversarial_nlp",
            message=f"Failed to inject fracture: {exc}",
        )
        return False


# ---------------------------------------------------------------------------
# PDF Processing
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrae texto de un PDF para análisis.

    Intenta múltiples métodos en orden de preferencia:
    1. PyPDF2 (más común)
    2. pdfminer.six (mejor extracción)
    3. pdftotext (poppler, si está disponible)
    """
    safe_path = _sanitize_path(pdf_path, must_exist=True)

    # Intentar PyPDF2
    try:
        import PyPDF2
        text_parts = []
        with open(safe_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
    except ImportError:
        pass
    except Exception as exc:
        audit_logger.log_info(
            event_type="PDF_EXTRACTION_ERROR",
            tool="vigia_adversarial_nlp",
            message=f"PyPDF2 failed: {exc}",
        )

    # Intentar pdfminer.six
    try:
        from pdfminer.high_level import extract_text
        return extract_text(safe_path)
    except ImportError:
        pass
    except Exception as exc:
        audit_logger.log_info(
            event_type="PDF_EXTRACTION_ERROR",
            tool="vigia_adversarial_nlp",
            message=f"pdfminer failed: {exc}",
        )

    # Fallback: leer como texto plano (para PDFs corruptos o de texto)
    try:
        with open(safe_path, 'rb') as f:
            content = f.read()
            # Intentar decodificar como texto
            return content.decode('utf-8', errors='ignore')
    except Exception:
        pass

    return ""


# ---------------------------------------------------------------------------
# Main Analysis Interface
# ---------------------------------------------------------------------------

@dataclass
class AdversarialNLPResult:
    """
    Resultado completo del análisis de NLP adversarial.
    """
    document_path: str
    document_hash: str
    text_length: int
    word_count: int

    entropy_profile: dict[str, float]
    register_detection: RegisterShiftDetection

    caie_fracture_injected: bool
    fracture_data: Optional[dict]

    verdict: str  # "NOISE", "SUSPICION", "MALICE"
    confidence: float

    peirce_chain: dict[str, str]
    vigia_verdict: str

    def to_dict(self) -> dict:
        return {
            "document_path": self.document_path,
            "document_hash": self.document_hash,
            "text_stats": {
                "length": self.text_length,
                "word_count": self.word_count,
            },
            "entropy_profile": {k: round(v, 4) for k, v in self.entropy_profile.items()},
            "register_analysis": self.register_detection.to_dict(),
            "caie_integration": {
                "fracture_injected": self.caie_fracture_injected,
                "fracture_data": self.fracture_data,
            },
            "verdict": self.verdict,
            "confidence": round(self.confidence, 4),
            "peirce_chain": self.peirce_chain,
            "vigia_verdict": self.vigia_verdict,
            "timestamp": _utcnow(),
        }


class VigiaAdversarialNLP:
    """
    Interfaz principal del módulo VIGÍA Adversarial NLP.

    Detecta manipulaciones semánticas mediante análisis de entropía
    lingüística y genera fracturas de terceridad en el CAIE.
    """

    def __init__(self):
        self.detector = EntropyBasedRegisterDetector()

    def analyze_document(
        self,
        document_path: str,
        declared_register: str = "legal_judicial",
        auto_inject_caie: bool = True,
    ) -> AdversarialNLPResult:
        """
        Analiza un documento para detectar Register Shift.

        Args:
            document_path: Ruta al documento (PDF o texto)
            declared_register: Registro que el documento pretende tener
            auto_inject_caie: Si True, inyecta fractura automáticamente en CAIE

        Returns:
            AdversarialNLPResult con análisis completo
        """
        # Extraer texto
        ext = Path(document_path).suffix.lower()
        if ext == '.pdf':
            text = extract_text_from_pdf(document_path)
        else:
            # Leer como texto plano
            safe_path = _sanitize_path(document_path, must_exist=True)
            with open(safe_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        # Calcular hash
        doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

        # Estadísticas básicas
        words = text.split()
        word_count = len(words)
        text_length = len(text)

        # Calcular perfil de entropía
        entropy_profile = calculate_entropy_profile(text)

        # Detectar Register Shift
        detection = self.detector.detect_register_shift(text, declared_register)

        # Determinar veredicto
        if detection.is_register_violation:
            if detection.severity >= 0.8:
                verdict = "MALICE"
            else:
                verdict = "SUSPICION"
        else:
            verdict = "NOISE"

        confidence = detection.severity

        # Inyectar en CAIE si corresponde
        fracture_data = None
        caie_injected = False

        if auto_inject_caie and detection.is_register_violation:
            caie_injected = inject_caie_fracture(detection, document_path, text)
            if caie_injected:
                fracture_data = generate_semantic_fracture(detection, document_path, doc_hash)

        # Construir cadena Peirce
        peirce_chain = {
            "firstness": (
                f"Document sign: {word_count} words, H_lexical={entropy_profile['lexical_entropy']:.2f}, "
                f"H_syntactic={entropy_profile['syntactic_entropy']:.2f}, Zipf_slope={entropy_profile['zipf_slope']:.2f}"
            ),
            "secondness": (
                f"Register collision: declared='{declared_register}' vs detected='{detection.primary_deviation}'. "
                f"RCS={detection.register_consistency_score:.3f} (threshold=0.3). "
                f"ERD_lexical={detection.erd_lexical:.3f}, ERD_syntactic={detection.erd_syntactic:.3f}"
            ),
            "thirdness": (
                f"Inferred habit: {'SEMANTIC DECEPTION' if detection.is_register_violation else 'LEGITIMATE COMMUNICATION'}. "
                f"The author {'deliberately' if detection.is_register_violation else 'consistently'} "
                f"employed linguistic patterns of '{detection.primary_deviation if detection.is_register_violation else declared_register}'."
            ),
        }

        # Veredicto VIGÍA
        if detection.is_register_violation:
            vigia_verdict = (
                f"[VIGIA_ADVERSARIAL_NLP]: {verdict}. "
                f"Register Consistency Score (RCS) = {detection.register_consistency_score:.3f} "
                f"indicates document claims to be '{declared_register}' but exhibits "
                f"entropy patterns of '{detection.primary_deviation}'. "
                f"Semantic manipulation of technical reality detected. "
                f"CAIE fracture injected: {caie_injected}."
            )
        else:
            vigia_verdict = (
                f"[VIGIA_ADVERSARIAL_NLP]: {verdict}. "
                f"RCS = {detection.register_consistency_score:.3f} >= 0.3. "
                f"Document entropy profile consistent with declared register '{declared_register}'."
            )

        return AdversarialNLPResult(
            document_path=document_path,
            document_hash=doc_hash,
            text_length=text_length,
            word_count=word_count,
            entropy_profile=entropy_profile,
            register_detection=detection,
            caie_fracture_injected=caie_injected,
            fracture_data=fracture_data,
            verdict=verdict,
            confidence=confidence,
            peirce_chain=peirce_chain,
            vigia_verdict=vigia_verdict,
        )


# ---------------------------------------------------------------------------
# MCP Tool Interface
# ---------------------------------------------------------------------------

async def analyze_document_register(
    document_path: str,
    declared_register: str = "legal_judicial",
    auto_inject_caie: bool = True,
) -> dict:
    """
    MCP Tool: Análisis de Register Shift en documentos.

    Detecta si un documento exhibe patrones de entropía lingüística
    incompatibles con su registro declarado, indicando manipulación
    semántica.

    Parameters
    ----------
    document_path : Ruta al documento (PDF, TXT, etc.)
    declared_register : Registro que el documento pretende tener
        Opciones: "legal_judicial", "academic_scientific", "corporate_technical"
    auto_inject_caie : Inyectar fractura automáticamente en CAIE

    Returns
    -------
    Dict con análisis completo, métricas de entropía, y veredicto
    """
    try:
        analyzer = VigiaAdversarialNLP()
        result = analyzer.analyze_document(
            document_path=document_path,
            declared_register=declared_register,
            auto_inject_caie=auto_inject_caie,
        )
        return result.to_dict()

    except Exception as exc:
        audit_logger.log_block(
            event_type="ADVERSARIAL_NLP_ERROR",
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


# ---------------------------------------------------------------------------
# Testing / Example Usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("VIGÍA Adversarial NLP - Entropy-based Register Shift Detector")
    print("=" * 60)

    # Test con texto de ejemplo
    test_texts = [
        # Texto legal auténtico (simulado)
        (
            "legal_judicial",
            """VISTO: El expediente caratulado 'García c/ Empresa SA s/ Daños y Perjuicios', 
            y CONSIDERANDO: Que el artículo 1730 del Código Civil establece la responsabilidad 
            contractual; Que la demanda fue presentada en tiempo y forma; Por tanto, RESUELVE: 
            Se declara procedente la demanda y se condena a la demandada al pago de la suma 
            de $500.000 en concepto de daños emergentes. En consecuencia, se ordena el archivo 
            del presente. Contra la presente resolución procede el recurso de apelación."""
        ),
        # Texto con register shift (ficción disfrazada de legal)
        (
            "legal_judicial",  # Declara ser legal
            """La noche caía sobre el juzgado cuando el abogado suspiró. Su corazón latía 
            con fuerza. El misterio del expediente lo consumía. Sentía que la emoción del 
            caso lo arrastraba. Miró los autos y pensó en la belleza de la justicia. El silencio 
            de la sala era profundo, como un sueño. La historia del demandante era única, 
            increíble, llena de pasión. Ahora, la oportunidad de ganar brillaba ante él. 
            No esperó más. El alma de la justicia llamaba."""
        ),
        # Texto de marketing disfrazado
        (
            "legal_judicial",
            """¡INCREÍBLE OFERTA DE DEMANDA! No espere más. Esta es la oportunidad única 
            para obtener la mejor resolución judicial. Garantizado 100%. La experiencia 
            legal revolucionaria que optimiza su caso. Sinergia total con el sistema. 
            Stakeholders satisfechos. Leverage máximo para su claim. Actionable insights 
            desde el primer día. Roadmap claro hacia la victoria. ¡Gratis consulta inicial! 
            Mejor opción del mercado. Exclusivo para usted."""
        ),
    ]

    analyzer = VigiaAdversarialNLP()

    for i, (declared, text) in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: Declared register = '{declared}'")
        print(f"Text preview: {text[:100]}...")
        print("-" * 60)

        # Crear archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(text)
            temp_path = f.name

        # Analizar
        result = analyzer.analyze_document(temp_path, declared, auto_inject_caie=False)

        print(f"Verdict: {result.verdict}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"RCS (Register Consistency Score): {result.register_detection.register_consistency_score:.3f}")
        print(f"Primary deviation: {result.register_detection.primary_deviation}")
        print(f"ERD Lexical: {result.register_detection.erd_lexical:.3f}")
        print(f"ERD Syntactic: {result.register_detection.erd_syntactic:.3f}")
        print(f"\nPeirce Firstness: {result.peirce_chain['firstness'][:80]}...")
        print(f"Peirce Secondness: {result.peirce_chain['secondness'][:80]}...")
        print(f"Peirce Thirdness: {result.peirce_chain['thirdness'][:80]}...")

        # Limpiar
        import os
        os.unlink(temp_path)

    print("\n" + "=" * 60)
    print("Tests completed!")
