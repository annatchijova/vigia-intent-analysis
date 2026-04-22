"""
vigia/tools/vigia_entanglement.py
==================================
VIGÍA — Entanglement Detection System (Capa P6: Advanced Adversary Detection)
         "La Cacería de Lotes" — Detección de Fábricas de Falsificación

Author: Kimi (Moonshot) — Forensic Systems Specialist
Tactical Command: Gemini (CTO) — Chief Tactical Officer
Integration: CAIE + vigia_forensic.db + Cross-Artifact Analysis

Purpose:
--------
Detecta si múltiples documentos "distintos" provienen de la misma matriz 
de falsificación mediante análisis de entrelazamiento lingüístico.

Capacidades:
1. N-Gram Jaccard Similarity — Secuencias idénticas >30 palabras no estándar
2. Physical Key Signature — Errores ortográficos recurrentes como huella dactilar
3. Forced Variety Detector — Variación léxica artificial (sinonimización GPT)
4. SQLite Cross-Linking — Vinculación de documentos aparentemente inconexos

Rob T. Lee Classification: Advanced Adversary Detection (AAD)
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, FrozenSet
from pathlib import Path

from vigia.security import _utcnow, audit_logger
from vigia.tools.vigia_adversarial_nlp import (
    ForensicDatabaseManager, LanguageDetector, 
    SPANISH_FUNCTION_WORDS, ENGLISH_FUNCTION_WORDS
)


# ============================================================================
# CONFIGURACIÓN TÁCTICA DE ENTANGLEMENT
# ============================================================================

# Umbrales de detección de fábrica
ENTANGLEMENT_THRESHOLD: float = 0.15  # Jaccard >15% = sospecha
IDENTICAL_SEQUENCE_MIN: int = 30    # Palabras idénticas consecutivas
FORCED_VARIATION_CV: float = 0.05    # Coeficiente de variación sospechosamente bajo
PHYSICAL_KEY_MIN_DOCS: int = 3       # Mínimo documentos para firma física

# Fórmulas legales estándar (excluir de detección de copia)
LEGAL_FORMULAS_ES: FrozenSet[str] = frozenset({
    "en consecuencia se resuelve", "por tanto se ordena", "visto y considerando",
    "en mérito de lo expuesto", "sin perjuicio de lo que resulte",
    "se deja constancia que", "a los fines pertinentes",
})

LEGAL_FORMULAS_EN: FrozenSet[str] = frozenset({
    "whereas the court finds", "now therefore it is ordered",
    "pursuant to the foregoing", "without prejudice to",
    "witnesseth that", "hereby ordered adjudged and decreed",
})


# ============================================================================
# ESTRUCTURAS DE DATOS TÁCTICAS
# ============================================================================

@dataclass(frozen=True)
class NGramFingerprint:
    """Huella de n-gramas para comparación de entrelazamiento."""
    doc_hash: str
    char_bigrams: Set[str]      # Huella de teclado/entrada
    word_trigrams: Set[str]     # Secuencias léxicas
    sentence_hashes: Set[str]   # Oraciones completas (hash)
    
    def jaccard_similarity(self, other: NGramFingerprint) -> Dict[str, float]:
        """Calcula similitud Jaccard multidimensional."""
        def jaccard(a: Set, b: Set) -> float:
            if not a and not b:
                return 0.0
            intersection = len(a & b)
            union = len(a | b)
            return intersection / union if union > 0 else 0.0
        
        return {
            "char_bigram": jaccard(self.char_bigrams, other.char_bigrams),
            "word_trigram": jaccard(self.word_trigrams, other.word_trigrams),
            "sentence": jaccard(self.sentence_hashes, other.sentence_hashes),
            "composite": (jaccard(self.char_bigrams, other.char_bigrams) * 0.3 +
                         jaccard(self.word_trigrams, other.word_trigrams) * 0.4 +
                         jaccard(self.sentence_hashes, other.sentence_hashes) * 0.3),
        }


@dataclass(frozen=True)
class PhysicalKeySignature:
    """
    Firma de teclado físico — errores ortográficos recurrentes 
    que actúan como huella dactilar del forjador.
    """
    error_pattern: str           # Ej: "trasladoo" (doble o)
    error_context: str          # Contexto regex
    affected_docs: List[str]    # Lista de doc_hashes afectados
    frequency_by_doc: Dict[str, int]  # Frecuencia por documento
    
    @property
    def doc_count(self) -> int:
        return len(self.affected_docs)
    
    @property
    def is_factory_signature(self) -> bool:
        """Es firma de fábrica si aparece en ≥3 documentos de diferentes emisores."""
        return self.doc_count >= PHYSICAL_KEY_MIN_DOCS


@dataclass
class ForcedVarietyProfile:
    """
    Perfil de variación léxica forzada — detecta cuando un autor
    usa sinónimos de forma artificial para parecer diferente.
    """
    doc_hash: str
    ttr_score: float
    synonym_density: float      # Palabras de listas sinónimas / total
    cv_local: float             # Coeficiente de variación local
    
    # Comparación con lote
    ttr_deviation_from_batch: float
    is_artificially_varied: bool


@dataclass
class EntanglementReport:
    """Reporte completo de análisis de lote."""
    batch_id: str
    document_count: int
    entanglement_matrix: Dict[Tuple[str, str], Dict[str, float]]
    
    # Hallazgos críticos
    identical_sequences: List[Dict]  # Secuencias >30 palabras idénticas
    physical_key_signatures: List[PhysicalKeySignature]
    forced_variety_anomalies: List[ForcedVarietyProfile]
    
    # Determinación táctica
    is_factory_production: bool
    estimated_operator_count: int  # Mínimo de operadores humanos/distintos
    confidence: float
    
    def to_caie_fractures(self) -> List[Dict]:
        """Genera fracturas para el Cross-Artifact Incongruence Engine."""
        fractures = []
        
        if self.is_factory_production:
            fractures.append({
                "type": "ENTANGLEMENT_FACTORY_DETECTED",
                "severity": self.confidence,
                "interpretation": (
                    f"Peirce Thirdness: Hábito de producción en lote detectado. "
                    f"Entrelazamiento lingüístico indica matriz común de falsificación. "
                    f"Operadores estimados: {self.estimated_operator_count}"
                ),
                "affected_documents": list(set(
                    doc for sig in self.physical_key_signatures 
                    for doc in sig.affected_docs
                )),
            })
        
        for seq in self.identical_sequences:
            fractures.append({
                "type": "IDENTICAL_SEQUENCE_NONSTANDARD",
                "severity": 0.9,
                "sequence_preview": seq["text"][:50] + "...",
                "documents": seq["documents"],
                "length": seq["length"],
            })
        
        return fractures


# ============================================================================
# MOTOR DE ENTANGLEMENT
# ============================================================================

class EntanglementEngine:
    """
    Motor de detección de entrelazamiento lingüístico.
    Detecta fábricas de falsificación mediante análisis de lotes.
    """
    
    def __init__(self, db: Optional[ForensicDatabaseManager] = None):
        self.db = db or ForensicDatabaseManager()
        self.lang_detector = LanguageDetector()
        self._synonym_cache: Dict[str, Set[str]] = {}
    
    def analyze_batch(
        self,
        document_paths: List[str],
        batch_id: Optional[str] = None,
    ) -> EntanglementReport:
        """
        Análisis completo de lote de documentos.
        
        Args:
            document_paths: Lista de rutas a documentos
            batch_id: Identificador opcional del lote
        
        Returns:
            EntanglementReport con hallazgos de fábrica
        """
        if not batch_id:
            batch_id = f"BATCH_{hashlib.sha256(''.join(document_paths).encode()).hexdigest()[:12]}"
        
        # 1. Extraer y fingerprintar documentos
        fingerprints: Dict[str, NGramFingerprint] = {}
        texts: Dict[str, str] = {}
        errors_by_doc: Dict[str, Counter] = {}
        
        for path in document_paths:
            doc_hash, text, fingerprint, errors = self._process_document(path)
            fingerprints[doc_hash] = fingerprint
            texts[doc_hash] = text
            errors_by_doc[doc_hash] = errors
        
        # 2. Calcular matriz de entrelazamiento
        matrix = self._calculate_entanglement_matrix(fingerprints)
        
        # 3. Detectar secuencias idénticas no estándar
        identical_seqs = self._find_identical_sequences(texts)
        
        # 4. Extraer firmas de teclado físico
        physical_keys = self._extract_physical_key_signatures(errors_by_doc)
        
        # 5. Analizar variedad forzada
        variety_profiles = self._analyze_forced_variety(texts, fingerprints)
        
        # 6. Determinar si es producción en fábrica
        is_factory, op_count, confidence = self._assess_factory_production(
            matrix, identical_seqs, physical_keys, variety_profiles
        )
        
        report = EntanglementReport(
            batch_id=batch_id,
            document_count=len(document_paths),
            entanglement_matrix=matrix,
            identical_sequences=identical_seqs,
            physical_key_signatures=physical_keys,
            forced_variety_anomalies=variety_profiles,
            is_factory_production=is_factory,
            estimated_operator_count=op_count,
            confidence=confidence,
        )
        
        # Persistir en SQLite
        self._persist_entanglement(report, fingerprints)
        
        return report
    
    def _process_document(self, path: str) -> Tuple[str, str, NGramFingerprint, Counter]:
        """Procesa un documento individual."""
        # Leer texto
        ext = Path(path).suffix.lower()
        if ext == '.pdf':
            text = self._extract_pdf_text(path)
        else:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        
        # Limitar tamaño (Qwen paranoia)
        if len(text) > 1_000_000:
            text = text[:1_000_000]
        
        doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        # Detectar idioma
        lang = self.lang_detector.detect(text)
        lang_code = lang.value
        
        # Extraer n-gramas
        char_bigrams = set(text[i:i+2].lower() for i in range(len(text)-1))
        
        # Palabras (content words only)
        if lang_code == "es":
            words = [w for w in re.findall(r'\b[a-zA-Záéíóúñ]+\b', text.lower())
                    if w not in SPANISH_FUNCTION_WORDS]
        else:
            words = [w for w in re.findall(r'\b[a-zA-Z]+\b', text.lower())
                    if w not in ENGLISH_FUNCTION_WORDS]
        
        word_trigrams = set(f"{words[i]}_{words[i+1]}_{words[i+2]}" 
                           for i in range(len(words)-2))
        
        # Hash de oraciones
        sentences = re.split(r'[.!?]+', text)
        sentence_hashes = set(hashlib.sha256(s.strip().lower().encode()).hexdigest()[:16]
                             for s in sentences if len(s.strip()) > 20)
        
        fingerprint = NGramFingerprint(
            doc_hash=doc_hash,
            char_bigrams=char_bigrams,
            word_trigrams=word_trigrams,
            sentence_hashes=sentence_hashes,
        )
        
        # Extraer errores ortográficos (Physical Key Signature)
        errors = self._extract_spelling_errors(text, lang_code)
        
        return doc_hash, text, fingerprint, errors
    
    def _extract_spelling_errors(self, text: str, lang_code: str) -> Counter:
        """
        Extrae patrones de error ortográfico recurrentes.
        Estos actúan como huella del teclado físico/hábito del forjador.
        """
        errors = Counter()
        
        # Patrones comunes de error de tecleo
        patterns = [
            (r'\b\w*([a-z])\1{2,}\w*\b', 'triple_letter'),  # "trasladooo"
            (r'\b\w*ie\w*ei\w*\b', 'ie_ei_confusion'),      # Confusión ie/ei
            (r'\b\w*ll\w*l\w*\b', 'double_l_single'),       # "ll" vs "l"
            (r'\b\w*rr\w*r\w*\b', 'double_r_single'),       # "rr" vs "r"
            (r'\b\w*h\w*\b', 'h_aspirate'),                 # H aspirada/no
        ]
        
        for pattern, error_type in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                # Contexto de 20 chars para identificación única
                context = text.lower()[max(0, text.lower().find(match)-10):
                                      min(len(text), text.lower().find(match)+len(match)+10)]
                error_key = f"{error_type}:{match}:{hashlib.sha256(context.encode()).hexdigest()[:8]}"
                errors[error_key] += 1
        
        return errors
    
    def _calculate_entanglement_matrix(
        self, 
        fingerprints: Dict[str, NGramFingerprint]
    ) -> Dict[Tuple[str, str], Dict[str, float]]:
        """Calcula matriz de similitud Jaccard para todos los pares."""
        matrix = {}
        hashes = list(fingerprints.keys())
        
        for i, h1 in enumerate(hashes):
            for h2 in hashes[i+1:]:
                sims = fingerprints[h1].jaccard_similarity(fingerprints[h2])
                matrix[(h1, h2)] = sims
                matrix[(h2, h1)] = sims  # Simétrica
        
        return matrix
    
    def _find_identical_sequences(self, texts: Dict[str, str]) -> List[Dict]:
        """
        Encuentra secuencias de >30 palabras idénticas entre documentos
        que NO sean fórmulas legales estándar.
        """
        identical = []
        
        # Extraer secuencias candidatas de cada documento
        sequences_by_doc: Dict[str, List[Tuple[int, str, str]]] = {}
        
        for doc_hash, text in texts.items():
            words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
            seqs = []
            
            for i in range(len(words) - IDENTICAL_SEQUENCE_MIN):
                seq = " ".join(words[i:i+IDENTICAL_SEQUENCE_MIN])
                
                # Verificar si es fórmula legal estándar
                is_standard = any(formula in seq for formula in 
                                (LEGAL_FORMULAS_ES | LEGAL_FORMULAS_EN))
                
                if not is_standard:
                    seq_hash = hashlib.sha256(seq.encode()).hexdigest()[:16]
                    seqs.append((i, seq_hash, seq))
            
            sequences_by_doc[doc_hash] = seqs
        
        # Buscar colisiones
        seq_locations: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        
        for doc_hash, seqs in sequences_by_doc.items():
            for pos, seq_hash, seq_text in seqs:
                seq_locations[seq_hash].append((doc_hash, pos))
        
        # Filtrar secuencias que aparecen en múltiples documentos
        for seq_hash, locations in seq_locations.items():
            if len(locations) >= 2 and len(set(loc[0] for loc in locations)) >= 2:
                # Recuperar texto original
                first_doc, first_pos = locations[0]
                words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', 
                                 texts[first_doc].lower())
                seq_text = " ".join(words[first_pos:first_pos+IDENTICAL_SEQUENCE_MIN])
                
                identical.append({
                    "hash": seq_hash,
                    "text": seq_text,
                    "length": IDENTICAL_SEQUENCE_MIN,
                    "documents": [loc[0] for loc in locations],
                    "positions": {loc[0]: loc[1] for loc in locations},
                })
        
        return identical
    
    def _extract_physical_key_signatures(
        self,
        errors_by_doc: Dict[str, Counter]
    ) -> List[PhysicalKeySignature]:
        """Extrae firmas de teclado físico de errores agregados."""
        # Agregar todos los errores
        all_errors: Dict[str, List[str]] = defaultdict(list)
        
        for doc_hash, errors in errors_by_doc.items():
            for error_key, count in errors.items():
                all_errors[error_key].extend([doc_hash] * count)
        
        # Crear firmas para errores que aparecen en múltiples documentos
        signatures = []
        
        for error_key, doc_list in all_errors.items():
            unique_docs = list(set(doc_list))
            if len(unique_docs) >= PHYSICAL_KEY_MIN_DOCS:
                # Extraer patrón legible
                parts = error_key.split(':')
                pattern = parts[1] if len(parts) > 1 else error_key
                
                freq_by_doc = {doc: doc_list.count(doc) for doc in unique_docs}
                
                sig = PhysicalKeySignature(
                    error_pattern=pattern,
                    error_context=parts[0] if parts else "unknown",
                    affected_docs=unique_docs,
                    frequency_by_doc=freq_by_doc,
                )
                signatures.append(sig)
        
        # Ordenar por número de documentos afectados (más grave primero)
        signatures.sort(key=lambda s: s.doc_count, reverse=True)
        
        return signatures
    
    def _analyze_forced_variety(
        self,
        texts: Dict[str, str],
        fingerprints: Dict[str, NGramFingerprint],
    ) -> List[ForcedVarietyProfile]:
        """
        Detecta variedad léxica forzada — cuando un autor intenta
        parecer diferente usando sinónimos de forma artificial.
        """
        profiles = []
        
        # Calcular TTR batch para comparación
        ttr_scores = []
        for doc_hash, text in texts.items():
            words = re.findall(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b', text.lower())
            content = [w for w in words if w not in (SPANISH_FUNCTION_WORDS | ENGLISH_FUNCTION_WORDS)]
            if content:
                ttr = len(set(content)) / len(content)
                ttr_scores.append((doc_hash, ttr))
        
        if len(ttr_scores) < 2:
            return profiles
        
        mean_ttr = statistics.mean(t[1] for t in ttr_scores)
        std_ttr = statistics.stdev(t[1] for t in ttr_scores) if len(ttr_scores) > 1 else 0.01
        
        for doc_hash, ttr in ttr_scores:
            # Desviación del batch
            deviation = abs(ttr - mean_ttr) / max(std_ttr, 0.001)
            
            # Detectar sinonimización artificial
            synonym_density = self._calculate_synonym_density(texts[doc_hash])
            
            # CV local (variación en ventanas del mismo documento)
            cv_local = self._calculate_local_cv(texts[doc_hash])
            
            # Es variedad forzada si:
            # - TTR muy cercano al promedio (artificialmente calibrado)
            # - Alta densidad de sinónimos
            # - CV local sospechosamente uniforme
            is_forced = (
                deviation < 0.5 and  # Muy cerca del promedio
                synonym_density > 0.15 and  # Muchos sinónimos
                cv_local < FORCED_VARIATION_CV  # Variación artificialmente uniforme
            )
            
            profiles.append(ForcedVarietyProfile(
                doc_hash=doc_hash,
                ttr_score=ttr,
                synonym_density=synonym_density,
                cv_local=cv_local,
                ttr_deviation_from_batch=deviation,
                is_artificially_varied=is_forced,
            ))
        
        return profiles
    
    def _calculate_synonym_density(self, text: str) -> float:
        """Calcula densidad de palabras de listas sinónimas conocidas."""
        # Listas simplificadas de sinónimos comunes (GPT-friendly)
        synonym_groups = [
            {"importante", "relevante", "significativo", "trascendental", "notable", "sustancial"},
            {"bueno", "óptimo", "favorable", "positivo", "conveniente", "adecuado"},
            {"malo", "desfavorable", "negativo", "inadecuado", "perjudicial"},
            {"rápido", "veloz", "pronto", "inmediato", "urgente", "precipitado"},
            {"lento", "tardío", "demorado", "pausado", "gradual"},
        ]
        
        words = set(re.findall(r'\b[a-zA-Záéíóúñ]+\b', text.lower()))
        synonym_hits = sum(1 for group in synonym_groups if len(words & group) > 1)
        
        return synonym_hits / max(len(words), 1)
    
    def _calculate_local_cv(self, text: str) -> float:
        """Calcula coeficiente de variación en ventanas locales."""
        words = re.findall(r'\b[a-zA-Záéíóúñ]+\b', text.lower())
        content = [w for w in words if w not in (SPANISH_FUNCTION_WORDS | ENGLISH_FUNCTION_WORDS)]
        
        if len(content) < 200:
            return 1.0  # Variación máxima por defecto
        
        # Ventanas de 100 palabras
        window_ttrs = []
        for i in range(0, len(content) - 100, 50):
            window = content[i:i+100]
            ttr = len(set(window)) / len(window)
            window_ttrs.append(ttr)
        
        if len(window_ttrs) < 2:
            return 1.0
        
        mean_ttr = statistics.mean(window_ttrs)
        std_ttr = statistics.stdev(window_ttrs)
        
        return std_ttr / mean_ttr if mean_ttr > 0 else 1.0
    
    def _assess_factory_production(
        self,
        matrix: Dict,
        identical_seqs: List[Dict],
        physical_keys: List[PhysicalKeySignature],
        variety_profiles: List[ForcedVarietyProfile],
    ) -> Tuple[bool, int, float]:
        """
        Determina si el lote es producción de fábrica.
        Retorna: (es_fábrica, operadores_estimados, confianza)
        """
        # Puntuación de evidencia
        score = 0.0
        max_score = 5.0
        
        # 1. Entrelazamiento alto en matriz
        high_entanglement = sum(
            1 for sims in matrix.values() 
            if sims.get('composite', 0) > ENTANGLEMENT_THRESHOLD
        )
        if high_entanglement > 0:
            score += min(1.5, high_entanglement / len(matrix) * 3)
        
        # 2. Secuencias idénticas no estándar
        if identical_seqs:
            score += min(1.5, len(identical_seqs) * 0.5)
        
        # 3. Firmas de teclado físico
        strong_signatures = [s for s in physical_keys if s.is_factory_signature]
        if strong_signatures:
            score += min(1.5, len(strong_signatures) * 0.5)
        
        # 4. Variedad forzada
        forced_count = sum(1 for p in variety_profiles if p.is_artificially_varied)
        if forced_count > 0:
            score += min(0.5, forced_count / len(variety_profiles))
        
        # Determinar
        is_factory = score >= 2.0
        confidence = min(1.0, score / max_score)
        
        # Estimar operadores (heurística: firmas físicas distintas)
        operator_estimate = max(1, len(strong_signatures))
        
        return is_factory, operator_estimate, confidence
    
    def _persist_entanglement(
        self,
        report: EntanglementReport,
        fingerprints: Dict[str, NGramFingerprint],
    ):
        """Persiste resultados en vigia_forensic.db para consultas cruzadas."""
        with self.db.connection() as conn:
            # Tabla de entanglement
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entanglement_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    doc_hash TEXT NOT NULL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_factory_linked BOOLEAN,
                    batch_confidence REAL,
                    physical_signatures TEXT,  -- JSON
                    identical_sequences TEXT,  -- JSON
                    FOREIGN KEY (doc_hash) REFERENCES document_history(document_hash)
                )
            """)
            
            # Insertar por documento
            for doc_hash in fingerprints.keys():
                sigs = [s.error_pattern for s in report.physical_key_signatures 
                       if doc_hash in s.affected_docs]
                seqs = [s["hash"] for s in report.identical_sequences 
                       if doc_hash in s["documents"]]
                
                conn.execute("""
                    INSERT INTO entanglement_analysis 
                    (batch_id, doc_hash, is_factory_linked, batch_confidence, 
                     physical_signatures, identical_sequences)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    report.batch_id,
                    doc_hash,
                    report.is_factory_production,
                    report.confidence,
                    json.dumps(sigs),
                    json.dumps(seqs),
                ))
            
            # Índice para queries cruzadas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entanglement_doc 
                ON entanglement_analysis(doc_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entanglement_batch 
                ON entanglement_analysis(batch_id)
            """)
            
            conn.commit()
    
    def query_cross_linked(self, doc_hash: str) -> List[Dict]:
        """
        Consulta documentos entrelazados con uno dado.
        Permite descubrir redes de falsificación.
        """
        with self.db.connection() as conn:
            cursor = conn.execute("""
                SELECT e2.doc_hash, e2.batch_id, e2.batch_confidence
                FROM entanglement_analysis e1
                JOIN entanglement_analysis e2 ON e1.batch_id = e2.batch_id
                WHERE e1.doc_hash = ? AND e2.doc_hash != ?
            """, (doc_hash, doc_hash))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _extract_pdf_text(self, path: str) -> str:
        """Placeholder — integrar con extractor existente."""
        try:
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            audit_logger.log_error(f"PDF extraction failed: {e}")
            return ""


# ============================================================================
# INTEGRACIÓN CON CAIE Y MOTOR PRINCIPAL
# ============================================================================

class EntanglementCAIEIntegration:
    """Puente entre EntanglementEngine y Cross-Artifact Incongruence Engine."""
    
    def __init__(self, entanglement_engine: EntanglementEngine):
        self.engine = entanglement_engine
    
    def analyze_and_inject(
        self,
        document_paths: List[str],
        batch_id: Optional[str] = None,
    ) -> EntanglementReport:
        """
        Analiza lote e inyecta fracturas automáticamente en CAIE.
        """
        report = self.engine.analyze_batch(document_paths, batch_id)
        
        if _CAIE_AVAILABLE and report.is_factory_production:
            try:
                caie = CrossArtifactIncongruenceEngine()
                
                for fracture in report.to_caie_fractures():
                    caie.add_from_tool_result(
                        source_tool="vigia_entanglement",
                        evidence_type="batch_forensics",
                        raw_score=fracture["severity"],
                        description=fracture["type"],
                        metadata=fracture,
                    )
                
                audit_logger.log_info(
                    event_type="ENTANGLEMENT_CAIE_INJECTED",
                    batch_id=report.batch_id,
                    fractures_count=len(report.to_caie_fractures()),
                )
                
            except Exception as e:
                audit_logger.log_error(f"CAIE injection failed: {e}")
        
        return report


# ============================================================================
# MCP TOOL INTERFACE
# ============================================================================

async def analyze_document_entanglement(
    document_paths: List[str],
    batch_id: Optional[str] = None,
    cross_link_query: Optional[str] = None,
) -> Dict:
    """
    MCP Tool: Análisis de entrelazamiento de lotes.
    
    Parameters
    ----------
    document_paths : Lista de rutas a documentos
    batch_id : ID opcional del lote
    cross_link_query : Si proporcionado, retorna documentos entrelazados con este hash
    
    Returns
    -------
    Dict con EntanglementReport o resultados de query cruzada
    """
    try:
        engine = EntanglementEngine()
        
        if cross_link_query:
            linked = engine.query_cross_linked(cross_link_query)
            return {
                "query_type": "cross_link",
                "source_document": cross_link_query,
                "linked_documents": linked,
                "count": len(linked),
            }
        
        # Análisis de lote completo
        integration = EntanglementCAIEIntegration(engine)
        report = integration.analyze_and_inject(document_paths, batch_id)
        
        return {
            "batch_id": report.batch_id,
            "document_count": report.document_count,
            "is_factory_production": report.is_factory_production,
            "confidence": report.confidence,
            "estimated_operators": report.estimated_operator_count,
            "physical_key_signatures": [
                {
                    "pattern": s.error_pattern,
                    "docs_affected": s.doc_count,
                    "is_factory_signature": s.is_factory_signature,
                }
                for s in report.physical_key_signatures[:5]  # Top 5
            ],
            "identical_sequences_count": len(report.identical_sequences),
            "forced_variety_anomalies": sum(
                1 for p in report.forced_variety_anomalies if p.is_artificially_varied
            ),
            "fractures_generated": len(report.to_caie_fractures()),
        }
        
    except Exception as exc:
        audit_logger.log_block(
            event_type="ENTANGLEMENT_ERROR",
            tool="analyze_document_entanglement",
            reason=str(exc),
        )
        return {
            "status": "ERROR",
            "error": str(exc),
            "timestamp": _utcnow(),
        }


# ============================================================================
# TESTS TÁCTICOS
# ============================================================================

if __name__ == "__main__":
    print("VIGÍA Entanglement Engine — La Cacería de Lotes")
    print("=" * 70)
    print("Advanced Adversary Detection | Rob T. Lee Classification")
    print("=" * 70)
    
    # Crear documentos de prueba simulando fábrica
    # Documento 1: Original "auténtico" con error específico
    doc1 = """
    VISTO: El expediente caratulado 'Causa 001', y CONSIDERANDO: Que el imputado 
    fue trasladoo a la dependencia policial. Que el hecho ocurrió en fecha cierta. 
    Por tanto se resuelve como corresponde a derecho. El traslado se efectuó sin 
    contratiempos. El imputado permanece a disposición del juzgado.
    """
    
    # Documento 2: Mismo error "trasladoo", diferente emisor declarado
    doc2 = """
    VISTO: El expediente 'Causa 002', y CONSIDERANDO: Que el detenido fue 
    trasladoo al destacamento. Que los hechos están debidamente acreditados. 
    Se ordena lo que corresponde. El traslado se realizó conforme protocolo.
    """
    
    # Documento 3: Mismo error, tercer emisor
    doc3 = """
    VISTO: El presente caso, y CONSIDERANDO: Que el sujeto fue trasladoo 
    a la comisaría. Que las actuaciones están completas. Se dispone lo 
    conducente. El traslado fue ordenado por este juzgado.
    """
    
    # Documento 4: Variedad forzada (sinonimización artificial)
    doc4 = """
    VISTO: El expediente mencionado, y CONSIDERANDO: Que el procesado fue 
    conducido a la seccional. Que los sucesos están fehacientemente acreditados. 
    Se resuelve lo pertinente. El traslado se ejecutó según normativa.
    """
    
    import tempfile
    
    def create_temp_doc(content: str, name: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            return f.name
    
    paths = [
        create_temp_doc(doc1, "doc1"),
        create_temp_doc(doc2, "doc2"),
        create_temp_doc(doc3, "doc3"),
        create_temp_doc(doc4, "doc4"),
    ]
    
    # Análisis
    engine = EntanglementEngine()
    report = engine.analyze_batch(paths, "TEST_FACTORY_001")
    
    print(f"\nBATCH: {report.batch_id}")
    print(f"Documentos: {report.document_count}")
    print(f"¿Fábrica detectada? {'SÍ' if report.is_factory_production else 'NO'}")
    print(f"Confianza: {report.confidence:.1%}")
    print(f"Operadores estimados: {report.estimated_operator_count}")
    
    print(f"\nFirmas de Teclado Físico: {len(report.physical_key_signatures)}")
    for sig in report.physical_key_signatures[:3]:
        print(f"  • '{sig.error_pattern}' en {sig.doc_count} documentos "
              f"{'[FÁBRICA]' if sig.is_factory_signature else ''}")
    
    print(f"\nSecuencias Idénticas No-Estándar: {len(report.identical_sequences)}")
    for seq in report.identical_sequences[:2]:
        preview = seq["text"][:40] + "..."
        print(f"  • '{preview}' en {len(seq['documents'])} docs")
    
    print(f"\nVariedad Forzada: {sum(1 for p in report.forced_variety_anomalies if p.is_artificially_varied)}")
    
    # Query cruzada
    print(f"\n{'='*70}")
    print("QUERY CRUZADA (simulación):")
    linked = engine.query_cross_linked(list(report.entanglement_matrix.keys())[0][0])
    print(f"Documentos vinculados encontrados: {len(linked)}")
    
    # Cleanup
    for p in paths:
        os.unlink(p)
    
    print("\n" + "=" * 70)
    print("Entanglement Engine: OPERATIVO")
    print("Listo para cacería de lotes")
    print("=" * 70)
