# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vigia/tools/vigia_temporal_forensics.py
=======================================
VIGÍA — Temporal Forensics & Anachronism Detection (Capa P7)
         "El Reloj Roto" — Detección de Desplazamiento Temporal

Author: Kimi (Moonshot) — Forensic Systems Specialist
Tactical Command: Gemini (CTO)
Integration: EntanglementEngine + CAIE + vigia_forensic.db

Purpose:
--------
Detecta anacronismos lingüísticos que demuestran que un documento 
fue escrito en una época diferente a la declarada.

Capacidades:
1. Lexical Anachronism Detection — Palabras de época incorrecta
2. Grammatical Shift Analysis — Cambios en norma gramatical prescriptiva
3. Technology Reference Dating — Referencias tecnológicas imposibles
4. Semantic Drift Tracking — Cambios de significado a través del tiempo

Rob T. Lee Classification: Temporal Adversary Detection (TAD)
"""

from __future__ import annotations

import json
import re
import sqlite3
import statistics  #  FIX: Importado
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Set, Tuple, Optional, FrozenSet
from collections import defaultdict

from vigia.security import _utcnow, audit_logger
from vigia.tools.vigia_adversarial_nlp import ForensicDatabaseManager, LanguageDetector


# ============================================================================
# CONSTANTES DE SEGURIDAD (LÍMITES)
# ============================================================================

MAX_DOCUMENT_BYTES: int = 10 * 1024 * 1024  # 10 MB - Prevención DoS
MAX_WORDS_TO_PROCESS: int = 50000  # Límite de palabras por documento
MAX_BATCH_DOCUMENTS: int = 1000  # Límite para procesamiento por lotes
MAX_TECH_REFS_PER_DOC: int = 100  # Límite de referencias tecnológicas


# ============================================================================
# DICCIONARIO TEMPORAL FORENSE (ES/EN)
# ============================================================================

# Palabras que no existían antes de cierta fecha (anacronismos léxicos)
LEXICAL_ANACHRONISMS_ES: Dict[str, int] = {
    # Tecnología
    "email": 1995, "correo electrónico": 1995, "e-mail": 1995,
    "internet": 1995, "web": 1995, "website": 1996, "sitio web": 1996,
    "google": 1998, "gmail": 2004, "yahoo": 1995,
    "whatsapp": 2009, "facebook": 2004, "twitter": 2006, "x": 2023,
    "instagram": 2010, "tiktok": 2016, "smartphone": 2007, "celular": 1995,
    "móvil": 1995, "app": 2008, "aplicación móvil": 2008,
    "wifi": 2000, "bluetooth": 2000, "usb": 1998, "pendrive": 2002,
    "cloud": 2008, "nube": 2008, "streaming": 2010, "bitcoin": 2009,
    "blockchain": 2009, "criptomoneda": 2013, "nft": 2021,
    "ia": 2015, "inteligencia artificial": 2015, "chatgpt": 2022,
    "deepfake": 2018, "zoom": 2020, "teams": 2017, "slack": 2013,
    
    # Conceptos sociales/políticos
    "género fluido": 2015, "no binario": 2015, "transgénero": 1990,
    "cisgénero": 2010, "feminismo": 1970, "me too": 2017, "brecha salarial": 2005,
    "sustainability": 2005, "sustentabilidad": 2005, "cambio climático": 1990,
    "calentamiento global": 1990, "huella de carbono": 2005,
    "vegano": 2010, "plant based": 2015, "gluten free": 2010, "sin gluten": 2010,
    "keto": 2015, "crossfit": 2005, "mindfulness": 2005, "wellness": 2005,
    
    # Económicos
    "startup": 2000, "unicornio": 2013, "fintech": 2015, "proptech": 2015,
    "edtech": 2015, "gig economy": 2015, "economía colaborativa": 2015,
    "uber": 2010, "airbnb": 2008, "netflix": 1998, "spotify": 2008,
    "amazon": 1995, "mercado libre": 1999, "mercadolibre": 1999,
    
    # Pandemia
    "covid": 2020, "coronavirus": 2020, "pandemia": 2020, "cuarentena": 2020,
    "confinamiento": 2020, "distanciamiento social": 2020, "barbijo": 2020,
    "tapabocas": 2020, "mascarilla": 2020, "vacuna": 2020, "pfizer": 2020,
    "moderna": 2020, "astrazeneca": 2020, "sputnik": 2020, "zoom fatigue": 2020,
}

LEXICAL_ANACHRONISMS_EN: Dict[str, int] = {
    # Technology
    "email": 1995, "e-mail": 1995, "website": 1996, "web": 1995,
    "google": 1998, "gmail": 2004, "yahoo": 1995, "search engine": 1995,
    "smartphone": 2007, "app": 2008, "iphone": 2007, "android": 2008,
    "wifi": 2000, "bluetooth": 2000, "usb": 1998, "flash drive": 2002,
    "cloud computing": 2008, "streaming": 2010, "binge watching": 2013,
    "bitcoin": 2009, "blockchain": 2009, "cryptocurrency": 2013, "nft": 2021,
    "ai": 2015, "artificial intelligence": 2015, "machine learning": 2015,
    "chatgpt": 2022, "gpt": 2020, "deepfake": 2018, "zoom": 2020,
    "slack": 2013, "discord": 2015, "tiktok": 2016, "instagram": 2010,
    "snapchat": 2011, "hashtag": 2007, "selfie": 2013, "meme": 2000,
    "viral": 2005, "influencer": 2010, "content creator": 2015,
    "podcast": 2004, "blog": 1999, "vlog": 2005, "livestream": 2010,
    
    # Social
    "gender fluid": 2015, "non-binary": 2015, "transgender": 1990,
    "cisgender": 2010, "me too": 2017, "cancel culture": 2015,
    "social justice warrior": 2015, "wokeness": 2015, "woke": 2015,
    "sustainability": 2005, "carbon footprint": 2005, "greenwashing": 2005,
    "vegan": 2010, "plant-based": 2015, "gluten-free": 2010,
    "keto": 2015, "paleo": 2010, "crossfit": 2005, "mindfulness": 2005,
    "wellness": 2005, "self-care": 2015, "work-life balance": 2005,
    
    # Economic
    "startup": 2000, "unicorn": 2013, "fintech": 2015, "proptech": 2015,
    "edtech": 2015, "gig economy": 2015, "sharing economy": 2015,
    "uber": 2010, "airbnb": 2008, "lyft": 2012, "doordash": 2013,
    "netflix": 1998, "spotify": 2008, "hulu": 2007, "prime": 2005,
    "amazon": 1995, "ebay": 1995, "paypal": 1998, "stripe": 2010,
    "venmo": 2009, "cashapp": 2013, "cryptowallet": 2015,
    
    # Pandemic
    "covid": 2020, "coronavirus": 2020, "pandemic": 2020, "quarantine": 2020,
    "lockdown": 2020, "social distancing": 2020, "mask mandate": 2020,
    "vaccine": 2020, "pfizer": 2020, "moderna": 2020, "astrazeneca": 2020,
    "zoom fatigue": 2020, "work from home": 2020, "remote work": 2020,
    "hybrid work": 2021, "the new normal": 2020,
}

# Cambios gramaticales prescriptivos (RAE / academic)
GRAMMATICAL_SHIFTS_ES: List[Tuple[str, str, int, str]] = [
    (r"\b(murió|falleció) a los \d+ años de edad\b", 
     r"\b(murió|falleció) a los \d+ años\b", 2010, 
     "omisión de 'de edad'"),
    (r"\b(ábaco|víveres|trébol)\b", 
     r"\b(ábaco|víveres|trébol)\b", 2010, 
     "tilde en monosílabos diptongados"),
    (r"\b(sólo|éste|ése|aquél)\b", 
     r"\b(solo|este|ese|aquel)\b", 2010, 
     "tilde en demostrativos y 'solo'"),
    (r"\b(cuál|cuáles|quién|quiénes)\b.*\?", 
     r"\b(cual|cuales|quien|quienes)\b.*\?", 2010, 
     "tilde en interrogativos indirectos"),
    (r"\bemail\b", r"\bcorreo electrónico\b", 2015, 
     "preferencia por castellanismo"),
    (r"\bwifi\b", r"\bwi-fi\b", 2015, 
     "guion en siglas técnicas"),
]

GRAMMATICAL_SHIFTS_EN: List[Tuple[str, str, int, str]] = [
    (r"\bshall\b", r"\bwill\b", 1950, "decline of 'shall'"),
    (r"\bwhom\b", r"\bwho\b", 2000, "decline of 'whom'"),
    (r"\bdata are\b", r"\bdata is\b", 2010, "singularization of 'data'"),
    (r"\bthe Internet\b", r"\bthe internet\b", 2016, "decapitalization"),
    (r"\be-mail\b", r"\bemail\b", 2011, "loss of hyphen"),
    (r"\bweb site\b", r"\bwebsite\b", 2005, "compounding"),
    (r"\bcell phone\b", r"\bmobile\b", 2010, "terminology shift US→UK"),
    (r"\bMr\.\s+[A-Z][a-z]+", r"\bMr\s+[A-Z][a-z]+", 2015, "loss of period in titles"),
]

# Referencias tecnológicas que datan documentos
TECH_REFERENCE_PATTERNS: Dict[str, Dict[str, Tuple[int, int]]] = {
    "es": {
        r"\bdiskette?\b|\bdisco flexible\b": (1970, 2005),
        r"\b(cd|dvd)\b|\bcompact disc\b": (1985, 2015),
        r"\bminidisc\b|\bmd\b": (1992, 2010),
        r"\bvhs\b|\bcassette\b|\bcinta de video\b": (1976, 2005),
        r"\bdial[- ]?up\b|\bmodem telefónico\b": (1990, 2005),
        r"\bmsn\b|\bmessenger\b": (1999, 2013),
        r"\bhi5\b|\bhi5\b": (2004, 2010),
        r"\bfotolog\b|\bflickr\b": (2002, 2015),
        r"\bmyspace\b": (2003, 2010),
        r"\borkut\b": (2004, 2014),
        r"\bblackberry\b|\bbbm\b": (2002, 2015),
        r"\bnokia\b|\bmotorola\b": (1990, 2010),
        r"\bwalkman\b|\bdiscman\b": (1979, 2005),
        r"\bipod\b": (2001, 2014),
        r"\bzune\b": (2006, 2011),
        r"\bgoogle plus\b|\bg\+\b": (2011, 2019),
        r"\bvine\b": (2013, 2017),
        r"\bperiscope\b": (2015, 2021),
    },
    "en": {
        r"\bfloppy\s*(disk|diskette)?\b": (1970, 2005),
        r"\b(cd|dvd)[- ]?(rom|r|rw)?\b": (1985, 2015),
        r"\bminidisc\b|\bmd\b": (1992, 2010),
        r"\bvhs\b|\bcassette\b|\bbetamax\b": (1976, 2005),
        r"\bdial[- ]?up\b": (1990, 2005),
        r"\baol\b|\bamerica online\b": (1993, 2010),
        r"\bmsn\b|\bmessenger\b": (1999, 2013),
        r"\bmyspace\b": (2003, 2010),
        r"\bfriendster\b": (2002, 2009),
        r"\borkut\b": (2004, 2014),
        r"\bblackberry\b|\bbbm\b|\bberry\b": (2002, 2015),
        r"\bnokia\b|\bmotorola razr\b": (1990, 2010),
        r"\bwalkman\b|\bdiscman\b": (1979, 2005),
        r"\bipod\b|\bclick wheel\b": (2001, 2014),
        r"\bzune\b": (2006, 2011),
        r"\bgoogle\s*plus\b|\bg\+\b": (2011, 2019),
        r"\bvine\b": (2013, 2017),
        r"\bgoogle\s*wave\b": (2009, 2012),
        r"\bgoogle\s*buzz\b": (2010, 2011),
    },
}


# ============================================================================
# ESTRUCTURAS DE DATOS TEMPORALES
# ============================================================================

@dataclass
class AnachronismFinding:
    """Hallazgo de anacronismo específico."""
    anachronism_type: str
    token: str
    position: int
    detected_date: int
    earliest_possible: int
    temporal_impossibility: int
    confidence: float


@dataclass
class TemporalForensicsReport:
    """Reporte completo de análisis temporal."""
    document_id: str
    declared_date: Optional[date]
    estimated_creation_window: Tuple[int, int]
    anachronisms: List[AnachronismFinding]
    lexical_drift_score: float
    grammatical_modernity: float
    tech_reference_date: Optional[int]
    is_temporally_fraudulent: bool
    temporal_fraud_confidence: float
    explanation: str
    
    def to_caie_fracture(self) -> Optional[Dict]:
        """Genera fractura temporal para CAIE."""
        if not self.is_temporally_fraudulent:
            return None
        
        current_year = datetime.now().year
        
        return {
            "type": "TEMPORAL_ANACHRONISM_FRAUD",
            "severity": self.temporal_fraud_confidence,
            "interpretation": (
                f"Peirce Thirdness: Hábito de falsificación temporal. "
                f"Documento declara época {self.declared_date or 'desconocida'} "
                f"pero contiene elementos lingüísticos imposibles antes de "
                f"{self.estimated_creation_window[0]}. "
                f"Anacronismos léxicos: {len([a for a in self.anachronisms if a.anachronism_type == 'lexical'])}, "
                f"gramaticales: {len([a for a in self.anachronisms if a.anachronism_type == 'grammatical'])}."
            ),
            "earliest_possible_date": self.estimated_creation_window[0],
            "latest_possible_date": self.estimated_creation_window[1],
            "declared_vs_detected_gap": (
                (self.declared_date.year - self.estimated_creation_window[0])
                if self.declared_date else None
            ),
        }


# ============================================================================
# MOTOR DE ANÁLISIS TEMPORAL
# ============================================================================

class TemporalForensicsEngine:
    """
    Motor de detección de anacronismos y datación lingüística.
    """
    
    def __init__(self, db: Optional[ForensicDatabaseManager] = None):
        self.db = db or ForensicDatabaseManager()
        self.lang_detector = LanguageDetector()
    
    def _truncate_text(self, text: str, max_bytes: int = MAX_DOCUMENT_BYTES) -> str:
        """Trunca texto para prevenir DoS."""
        encoded = text.encode('utf-8')
        if len(encoded) > max_bytes:
            truncated = encoded[:max_bytes].decode('utf-8', errors='ignore')
            audit_logger.log_info(
                "TEXT_TRUNCATED",
                "TemporalForensicsEngine",
                f"Truncated from {len(encoded)} to {max_bytes} bytes"
            )
            return truncated
        return text
    
    def analyze(
        self,
        text: str,
        document_id: str,
        declared_date: Optional[date] = None,
        language: Optional[str] = None,
    ) -> TemporalForensicsReport:
        """
        Análisis completo de coherencia temporal.
        """
        #  FIX: Truncar texto para prevenir DoS
        text = self._truncate_text(text)
        
        # Detección de idioma
        if language is None:
            lang = self.lang_detector.detect(text)
            lang_code = lang.value
        else:
            lang_code = language
        
        # 1. Anacronismos léxicos
        lexical = self._detect_lexical_anachronisms(text, lang_code)
        
        # 2. Cambios gramaticales
        grammatical = self._detect_grammatical_shifts(text, lang_code)
        
        # 3. Referencias tecnológicas datables
        tech_refs = self._detect_tech_references(text, lang_code)
        
        # 4. Calcular ventana de creación
        earliest, latest = self._calculate_creation_window(
            lexical, grammatical, tech_refs, declared_date
        )
        
        # 5. Determinar fraude temporal
        is_fraud, confidence, explanation = self._assess_temporal_fraud(
            declared_date, earliest, latest, lexical, grammatical
        )
        
        # Agregar todos los anacronismos
        all_anachronisms = lexical + grammatical
        
        # Calcular scores
        word_count = max(len(text.split()), 1)
        lexical_score = len(lexical) / min(word_count / 100, 1.0)
        gram_modernity = self._calculate_grammatical_modernity(grammatical)
        
        report = TemporalForensicsReport(
            document_id=document_id,
            declared_date=declared_date,
            estimated_creation_window=(earliest, latest),
            anachronisms=all_anachronisms,
            lexical_drift_score=min(1.0, lexical_score),
            grammatical_modernity=gram_modernity,
            tech_reference_date=tech_refs.get("median_date"),
            is_temporally_fraudulent=is_fraud,
            temporal_fraud_confidence=confidence,
            explanation=explanation,
        )
        
        # Persistir
        self._persist_temporal_analysis(report)
        
        return report
    
    def _detect_lexical_anachronisms(
        self, 
        text: str, 
        lang_code: str
    ) -> List[AnachronismFinding]:
        """Detecta palabras que no existían en la época declarada."""
        anachronisms = []
        
        lexicon = LEXICAL_ANACHRONISMS_ES if lang_code == "es" else LEXICAL_ANACHRONISMS_EN
        
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text_lower)
        
        #  FIX: Limitar número de palabras a procesar
        if len(words) > MAX_WORDS_TO_PROCESS:
            words = words[:MAX_WORDS_TO_PROCESS]
            audit_logger.log_info(
                "LEXICAL_SCAN_TRUNCATED",
                "TemporalForensicsEngine",
                f"Truncated from {len(words)} to {MAX_WORDS_TO_PROCESS} words"
            )
        
        current_year = datetime.now().year
        
        for word in words:
            if word in lexicon:
                earliest_year = lexicon[word]
                
                # Calcular confianza basada en especificidad
                confidence = 0.9 if word in ["google", "facebook", "whatsapp", "chatgpt"] else 0.7
                
                finding = AnachronismFinding(
                    anachronism_type="lexical",
                    token=word,
                    position=text_lower.find(word),
                    detected_date=current_year,
                    earliest_possible=earliest_year,
                    temporal_impossibility=current_year - earliest_year,
                    confidence=confidence,
                )
                anachronisms.append(finding)
        
        return anachronisms
    
    def _detect_grammatical_shifts(
        self,
        text: str,
        lang_code: str,
    ) -> List[AnachronismFinding]:
        """Detecta uso de normas gramaticales modernas en documento antiguo."""
        anachronisms = []
        
        shifts = GRAMMATICAL_SHIFTS_ES if lang_code == "es" else GRAMMATICAL_SHIFTS_EN
        current_year = datetime.now().year
        
        for old_pattern, new_pattern, year_change, description in shifts:
            #  FIX: Buscar patrón ARCAICO (no moderno) para detectar falsificación
            matches = re.finditer(old_pattern, text, re.IGNORECASE)
            
            for match in matches:
                finding = AnachronismFinding(
                    anachronism_type="grammatical",
                    token=match.group(),
                    position=match.start(),
                    detected_date=current_year,
                    earliest_possible=year_change,
                    temporal_impossibility=current_year - year_change,
                    confidence=0.6,
                )
                anachronisms.append(finding)
        
        return anachronisms
    
    def _detect_tech_references(
        self,
        text: str,
        lang_code: str,
    ) -> Dict[str, any]:
        """Extrae referencias tecnológicas datables."""
        refs = TECH_REFERENCE_PATTERNS.get(lang_code, {})
        
        found_refs = []
        dates = []
        
        text_lower = text.lower()
        
        for pattern, (start_year, end_year) in refs.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                #  FIX: Limitar número de referencias
                for match in matches[:MAX_TECH_REFS_PER_DOC]:
                    found_refs.append({
                        "pattern": pattern[:50],
                        "match": match[:50] if isinstance(match, str) else str(match)[:50],
                        "active_period": (start_year, end_year),
                        "median_year": (start_year + end_year) // 2,
                    })
                    dates.append((start_year + end_year) // 2)
        
        return {
            "references_found": found_refs[:MAX_TECH_REFS_PER_DOC],
            "count": len(found_refs),
            "median_date": statistics.median(dates) if dates else None,
            "date_range": (min(dates), max(dates)) if len(dates) >= 2 else None,
        }
    
    def _calculate_creation_window(
        self,
        lexical: List[AnachronismFinding],
        grammatical: List[AnachronismFinding],
        tech_refs: Dict,
        declared_date: Optional[date],
    ) -> Tuple[int, int]:
        """
        Calcula ventana más probable de creación.
        """
        current_year = datetime.now().year
        
        # Límite inferior: el anacronismo más reciente
        all_earliest = [a.earliest_possible for a in lexical + grammatical]
        
        if tech_refs.get("median_date"):
            all_earliest.append(tech_refs["median_date"])
        
        if not all_earliest:
            return (1950, current_year)
        
        earliest = max(all_earliest)
        
        # Límite superior
        latest = current_year
        if declared_date and declared_date.year >= earliest:
            latest = declared_date.year
        
        return (earliest, latest)
    
    def _assess_temporal_fraud(
        self,
        declared_date: Optional[date],
        earliest: int,
        latest: int,
        lexical: List[AnachronismFinding],
        grammatical: List[AnachronismFinding],
    ) -> Tuple[bool, float, str]:
        """
        Determina si hay fraude temporal.
        """
        if not declared_date:
            return False, 0.0, "Fecha declarada no proporcionada"
        
        declared_year = declared_date.year
        
        if declared_year < earliest:
            gap = earliest - declared_year
            confidence = min(1.0, 0.5 + (gap / 20))
            
            explanation = (
                f"Documento declara fecha {declared_year} pero contiene "
                f"elementos lingüísticos imposibles antes de {earliest}. "
                f"Gap temporal: {gap} años."
            )
            return True, confidence, explanation
        
        if declared_year < earliest + 2 and len(lexical) > 2:
            return True, 0.7, (
                f"Fecha declarada ({declared_year}) coincide con límite inferior "
                f"de posibilidad ({earliest}). Múltiples anacronismos sugieren "
                f"falsificación reciente de documento antiguo."
            )
        
        return False, 0.0, "Fecha declarada consistente con análisis lingüístico"
    
    def _calculate_grammatical_modernity(
        self,
        grammatical: List[AnachronismFinding],
    ) -> float:
        """Calcula qué tan moderno es el uso gramatical (0-1)."""
        if not grammatical:
            return 0.5
        
        current_year = datetime.now().year
        
        weighted_sum = sum(g.confidence * (current_year - g.earliest_possible) / 100 
                          for g in grammatical)
        total_weight = sum(g.confidence for g in grammatical)
        
        return min(1.0, weighted_sum / max(total_weight, 1))
    
    def _persist_temporal_analysis(self, report: TemporalForensicsReport):
        """Guarda en SQLite para consultas cruzadas."""
        with self.db.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT UNIQUE NOT NULL,
                    declared_date TEXT,
                    earliest_possible INTEGER,
                    latest_possible INTEGER,
                    is_fraudulent BOOLEAN,
                    fraud_confidence REAL,
                    anachronism_count INTEGER,
                    lexical_drift REAL,
                    grammatical_modernity REAL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """)
            
            #  FIX: Transacción explícita con rollback
            try:
                conn.execute("BEGIN TRANSACTION")
                
                conn.execute("""
                    INSERT OR REPLACE INTO temporal_analysis
                    (document_id, declared_date, earliest_possible, latest_possible,
                     is_fraudulent, fraud_confidence, anachronism_count,
                     lexical_drift, grammatical_modernity, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.document_id,
                    report.declared_date.isoformat() if report.declared_date else None,
                    report.estimated_creation_window[0],
                    report.estimated_creation_window[1],
                    report.is_temporally_fraudulent,
                    report.temporal_fraud_confidence,
                    len(report.anachronisms),
                    report.lexical_drift_score,
                    report.grammatical_modernity,
                    json.dumps([{
                        "type": a.anachronism_type,
                        "token": a.token,
                        "earliest": a.earliest_possible,
                    } for a in report.anachronisms[:100]]),  # Limitar detalles
                ))
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                audit_logger.log_info(
                    "TEMPORAL_PERSIST_ERROR",
                    "TemporalForensicsEngine",
                    f"Failed to persist: {e}"
                )
                raise


# ============================================================================
# RED TEAM (VERSIÓN SIMPLIFICADA)
# ============================================================================

class AdversarialRedTeam:
    """
    Genera documentos falsos para verificar límites de detección.
    """
    
    TEST_SCENARIOS = [
        "naive_forgery",
        "style_transfer_gpt",
        "professional_forger",
        "institutional_mole",
        "adversarial_optimization",
        "temporal_fraud",
        "factory_production",
    ]
    
    def __init__(self, target_engine):
        self.engine = target_engine
    
    def generate_naive_forgery(self, template: str, modifications: Dict) -> str:
        """Falsificación básica."""
        text = template
        for old, new in modifications.items():
            text = text.replace(old, new)
        return text
    
    def generate_temporal_fraud(self, modern_text: str, target_year: int) -> str:
        """Intenta hacer que texto moderno parezca antiguo."""
        archaisms = {
            "email": "correspondencia",
            "internet": "red de comunicaciones",
            "whatsapp": "mensajería",
            "google": "enciclopedia",
            "celular": "teléfono",
            "smartphone": "agenda electrónica",
        }
        
        text = modern_text.lower()
        for modern, archaic in archaisms.items():
            text = re.sub(r'\b' + modern + r'\b', archaic, text)
        
        return text
    
    def evaluate_detection(self, original: str, forgery: str, 
                          declared_metadata: Dict) -> Dict:
        """Evalúa detección de falsificación."""
        #  FIX: Crear fecha desde metadata
        declared_date = None
        if declared_metadata.get("date"):
            try:
                declared_date = date.fromisoformat(declared_metadata["date"])
            except (ValueError, TypeError):
                pass
        
        forgery_analysis = self.engine.analyze(
            forgery, "TEST_FORGERY", declared_date
        )
        
        return {
            "detection_success": forgery_analysis.is_temporally_fraudulent,
            "confidence": forgery_analysis.temporal_fraud_confidence,
            "anachronisms_found": len(forgery_analysis.anachronisms),
        }


# ============================================================================
# TESTS TÁCTICOS TEMPORALES
# ============================================================================

if __name__ == "__main__":
    print("VIGÍA Temporal Forensics — El Reloj Roto")
    print("=" * 70)
    
    engine = TemporalForensicsEngine()
    redteam = AdversarialRedTeam(engine)
    
    doc_2024_con_fecha_1990 = """
    VISTO: El expediente caratulado 'Causa 001/1990', y CONSIDERANDO:
    Que el imputado fue notificado vía email de la resolución.
    Que se ha verificado su identidad mediante reconocimiento facial.
    Por tanto, se ordena su comparecencia vía Zoom para el día de la fecha.
    """
    
    doc_1990_autentico = """
    VISTO: El expediente caratulado 'Causa 001/1990', y CONSIDERANDO:
    Que el imputado fue notificado por telegrama de la resolución.
    Que se ha verificado su identidad mediante cédula de identidad.
    Por tanto, se ordena su comparecencia personal.
    """
    
    tests = [
        ("FRAUDE_TEMPORAL_OBVIO", doc_2024_con_fecha_1990, date(1990, 5, 15)),
        ("DOCUMENTO_EPOCA_CORRECTA", doc_1990_autentico, date(1990, 5, 15)),
    ]
    
    for name, text, declared in tests:
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print(f"Fecha declarada: {declared}")
        
        report = engine.analyze(text, f"TEST_{name}", declared)
        
        print(f"Ventana estimada: {report.estimated_creation_window[0]}-{report.estimated_creation_window[1]}")
        print(f"¿Fraude temporal? {'SÍ' if report.is_temporally_fraudulent else 'NO'}")
        print(f"Confianza: {report.temporal_fraud_confidence:.1%}")
        
        if report.anachronisms:
            print(f"\nAnacronismos detectados ({len(report.anachronisms)}):")
            for a in report.anachronisms[:5]:
                print(f"  • '{a.token}' (tipo: {a.anachronism_type}, "
                      f"imposible antes de {a.earliest_possible})")
