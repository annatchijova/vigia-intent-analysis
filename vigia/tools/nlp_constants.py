"""
vigia/tools/nlp_constants.py
=============================
VIGÍA — Constantes léxicas y tipos base para análisis NLP forense.

Extraído de: adversarial_nlp_pericial_EN_ES.py (raíz del proyecto)
Diagnóstico: estas constantes estaban INDEFINIDAS en el archivo original —
el módulo las usaba en línea 506+ pero nunca las definía, lo que causaría
NameError en runtime. Resuelto acá.

Responsabilidad de este módulo:
  - Enumeraciones (Language, InstitutionalEmitter)
  - Dataclasses base (ForensicThresholds, LanguageConfig)
  - Constantes léxicas ES/EN (function words, markers, CognitiveMarkers)
  - Constantes sigma y límites de memoria

Importado por:
  - vigia/tools/forensic_db.py
  - vigia/tools/adversarial_nlp.py
  - vigia/tools/entanglement.py

SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, Set, Tuple


# ============================================================================
# ENUMERACIONES BASE
# ============================================================================

class Language(Enum):
    ENGLISH = "en"
    SPANISH = "es"
    UNKNOWN = "unknown"


class InstitutionalEmitter(Enum):
    MPF = "Ministerio_Publico_Fiscal"
    LE = "Law_Enforcement"
    COURT = "Poder_Judicial"
    FORENSIC_LAB = "Laboratorio_Forense"
    PRIVATE_LEGAL = "Estudio_Juridico_Privado"
    UNKNOWN = "Emisor_Desconocido"


# ============================================================================
# DATACLASSES BASE
# ============================================================================

@dataclass(frozen=True)
class ForensicThresholds:
    """Umbrales σ por idioma e institución (Daubert-calibrados)."""
    nv_ratio_mean: float
    nv_ratio_std: float
    nominalization_mean: float
    nominalization_std: float
    exclusion_mean: float
    exclusion_std: float
    certainty_mean: float
    certainty_std: float
    ttr_mean: float
    ttr_std: float
    fog_mean: float
    fog_std: float
    info_density_mean: float
    info_density_std: float


@dataclass(frozen=True)
class LanguageConfig:
    """Configuración lingüística por idioma."""
    code: str
    function_words: FrozenSet[str]
    legal_markers: FrozenSet[str]
    technical_markers: FrozenSet[str]
    narrative_markers: FrozenSet[str]
    urgent_markers: FrozenSet[str]
    exclusion_markers: FrozenSet[str]
    certainty_markers: FrozenSet[str]
    distancing_markers: FrozenSet[str]
    prepositions: FrozenSet[str]
    noun_suffixes: Tuple[str, ...]
    verb_suffixes: Tuple[str, ...]
    adj_suffixes: Tuple[str, ...]
    adv_suffixes: Tuple[str, ...]
    fog_thresholds: Dict[str, float]


# ============================================================================
# LÍMITES DE MEMORIA Y SEGURIDAD (Qwen Paranoia Protocol)
# ============================================================================

MAX_TEXT_LENGTH: int = 10_000_000   # 10 MB
MAX_WINDOW_SIZE: int = 1_000        # tokens por ventana
MAX_DB_SIZE: int = 500_000_000      # 500 MB límite DB
MAX_CACHE_ENTRIES: int = 1_000      # entradas cache en memoria
ACP_WINDOW_SIZE: int = 20           # ventana deslizante ACP

DB_PERMISSIONS: int = 0o640         # rw-r----- (owner+group)
CONFIG_PERMISSIONS: int = 0o644     # rw-r--r--
EVIDENCE_PATH_ENV: str = "VIGIA_EVIDENCE_PATH"

# Umbrales sigma periciales (Daubert-calibrados)
SIGMA_WARNING: float = 1.96
SIGMA_CRITICAL: float = 2.5
SIGMA_DEFINITIVE: float = 3.0
SIGMA_SPOOFING: float = 2.5


# ============================================================================
# LEXICÓN ESPAÑOL — function words y markers
# Fuente: corpus de documentos jurídicos argentinos (MPF, Poder Judicial)
# ============================================================================

SPANISH_FUNCTION_WORDS: FrozenSet[str] = frozenset({
    # Artículos
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    # Preposiciones
    "a", "ante", "bajo", "con", "contra", "de", "desde", "durante",
    "en", "entre", "hacia", "hasta", "mediante", "para", "por",
    "según", "sin", "sobre", "tras",
    # Conjunciones
    "y", "e", "ni", "o", "u", "pero", "sino", "aunque", "porque",
    "que", "si", "como", "cuando", "donde", "mientras", "pues",
    # Pronombres funcionales
    "se", "le", "les", "lo", "la", "los", "las", "me", "te",
    "nos", "os", "su", "sus", "mi", "mis", "tu", "tus",
    # Adverbios de frecuencia y cantidad
    "muy", "más", "menos", "tan", "tanto", "cuanto", "bien",
    "ya", "aún", "también", "tampoco", "no", "sí",
})

SPANISH_LEGAL_MARKERS: FrozenSet[str] = frozenset({
    "visto", "considerando", "resuelve", "ordena", "dispone",
    "acreditado", "acredita", "fehacientemente", "resolución",
    "expediente", "caratulado", "actuaciones", "auto", "decreto",
    "sentencia", "fallo", "providencia", "constancia", "certifica",
    "articulo", "artículo", "inciso", "párrafo", "ley", "código",
    "normativa", "vigente", "aplicable", "estrictamente", "previsto",
    "prevista", "dispuesto", "dispuesta", "establecido", "establecida",
    "mérito", "virtud", "atento", "precedentemente", "oportunamente",
    "asimismo", "asimismo", "asiste", "corresponde",
})

SPANISH_TECHNICAL_MARKERS: FrozenSet[str] = frozenset({
    "análisis", "pericial", "forense", "evidencia", "indicio",
    "prueba", "perito", "dictamen", "informe", "técnico",
    "científico", "metodología", "estándar", "protocolo",
    "procedimiento", "verificación", "autenticación", "validación",
    "determinación", "constatación", "comprobación", "identificación",
    "hash", "firma", "digital", "integridad", "cadena", "custodia",
})

SPANISH_NARRATIVE_MARKERS: FrozenSet[str] = frozenset({
    "luego", "después", "entonces", "finalmente", "primero",
    "segundo", "tercero", "además", "igualmente", "posteriormente",
    "anteriormente", "previamente", "seguidamente", "consecuentemente",
    "resultando", "resultó", "ocurrió", "procedió",
})

SPANISH_URGENT_MARKERS: FrozenSet[str] = frozenset({
    "urgente", "inmediatamente", "sin demora", "de inmediato",
    "prioritariamente", "con carácter urgente", "inaplazable",
    "perentorio", "plazo fatal",
})


# ============================================================================
# LEXICÓN INGLÉS — function words y markers
# Fuente: corpus de documentos legales US/UK (federal courts, law enforcement)
# ============================================================================

ENGLISH_FUNCTION_WORDS: FrozenSet[str] = frozenset({
    # Articles
    "the", "a", "an",
    # Prepositions
    "of", "in", "to", "for", "with", "on", "at", "from", "by",
    "about", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further",
    # Conjunctions
    "and", "but", "or", "nor", "so", "yet", "both", "either",
    "neither", "not", "only", "also", "however", "although",
    "because", "since", "while", "if", "unless", "until",
    "that", "which", "who", "whom", "whose", "when", "where",
    # Pronouns
    "it", "its", "they", "them", "their", "this", "these",
    "those", "he", "she", "his", "her", "we", "our", "you",
    # Auxiliaries
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "shall", "should", "may", "might", "must", "can", "could",
})

ENGLISH_LEGAL_MARKERS: FrozenSet[str] = frozenset({
    "whereas", "therefore", "hereby", "herein", "therein",
    "pursuant", "notwithstanding", "aforesaid", "aforementioned",
    "heretofore", "hereafter", "thereto", "thereof", "therefrom",
    "witnesseth", "adjudged", "decreed", "ordered", "resolved",
    "stipulated", "covenanted", "warranted", "represented",
    "jurisdiction", "venue", "plaintiff", "defendant", "counsel",
    "honorable", "court", "judgment", "statute", "pursuant",
})

ENGLISH_TECHNICAL_MARKERS: FrozenSet[str] = frozenset({
    "analysis", "forensic", "evidence", "examination", "specimen",
    "methodology", "protocol", "procedure", "validation", "verification",
    "authentication", "certification", "documentation", "identification",
    "determination", "assessment", "evaluation", "investigation",
    "hash", "signature", "digital", "integrity", "chain", "custody",
})

ENGLISH_NARRATIVE_MARKERS: FrozenSet[str] = frozenset({
    "first", "second", "third", "then", "next", "finally",
    "subsequently", "previously", "furthermore", "moreover",
    "additionally", "consequently", "therefore", "thus", "hence",
    "accordingly", "thereafter", "meanwhile",
})

ENGLISH_URGENT_MARKERS: FrozenSet[str] = frozenset({
    "urgent", "immediately", "forthwith", "without delay",
    "expeditiously", "as soon as possible", "asap", "priority",
    "time-sensitive", "emergency",
})


# ============================================================================
# COGNITIVE MARKERS — Patrones de carga cognitiva y distanciamiento
# Indicadores de fabricación via análisis de marcadores epistémicos
# ============================================================================

class CognitiveMarkers:
    """
    Marcadores cognitivos para detección de fabricación documental.
    Basados en lingüística forense (Coulthard, Johnson, Woolls).
    """

    # Marcadores de exclusión — sobreuso indica estrés cognitivo del fabricante
    EXCLUSION_MARKERS_ES: FrozenSet[str] = frozenset({
        "excepto", "salvo", "menos", "sino", "a excepción",
        "con excepción", "excluyendo", "exceptuando",
        "no obstante", "sin embargo", "a pesar de",
    })
    EXCLUSION_MARKERS_EN: FrozenSet[str] = frozenset({
        "except", "unless", "without", "excluding", "save",
        "other than", "apart from", "besides", "notwithstanding",
        "however", "nevertheless", "despite",
    })

    # Marcadores de certeza — sobreuso (absolutos) es señal de fabricación
    CERTAINTY_QUANT_ES: FrozenSet[str] = frozenset({
        "siempre", "nunca", "jamás", "absolutamente", "totalmente",
        "completamente", "definitivamente", "ciertamente", "evidentemente",
        "claramente", "obviamente", "indudablemente", "incuestionablemente",
        "sin duda", "con certeza", "fehacientemente",
    })
    CERTAINTY_QUANT_EN: FrozenSet[str] = frozenset({
        "always", "never", "absolutely", "totally", "completely",
        "definitely", "certainly", "clearly", "obviously",
        "undoubtedly", "unquestionably", "without doubt",
        "without question", "categorically", "positively",
    })

    # Marcadores de distanciamiento — indican no-autoría o redacción forzada
    DISTANCING_MARKERS_ES: FrozenSet[str] = frozenset({
        "supuestamente", "presuntamente", "aparentemente",
        "se dice que", "según se informa", "al parecer",
        "dizque", "supuestamente", "en teoría", "teóricamente",
    })
    DISTANCING_MARKERS_EN: FrozenSet[str] = frozenset({
        "allegedly", "supposedly", "apparently", "reportedly",
        "purportedly", "ostensibly", "it is claimed", "it appears",
        "it would seem", "theoretically", "in theory",
    })
