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
vigia/tools/entanglement.py
============================
VIGÍA — Entanglement Detection System (Capa P6: Advanced Adversary Detection)
         "La Cacería de Lotes" — Detección de Fábricas de Falsificación

Author: Kimi (Moonshot) — Forensic Systems Specialist
Tactical Command: Gemini (CTO) — Chief Tactical Officer
Integration: CAIE + vigia_forensic.db + Cross-Artifact Analysis

Extraído desde: entanglement_bridge.py (raíz del proyecto)
Los imports ahora apuntan a los módulos del paquete en lugar de
importar directamente desde la raíz.

PURPOSE
-------
Detecta si múltiples documentos "distintos" provienen de la misma
matriz de falsificación mediante análisis de entrelazamiento lingüístico.

MÉTODOS DE DETECCIÓN (4 capas)
--------------------------------
1. N-Gram Jaccard Similarity  — secuencias idénticas >30 palabras no estándar
2. Physical Key Signature      — errores ortográficos recurrentes como huella
3. Forced Variety Detector     — variación léxica artificial (sinonimización GPT)
4. SQLite Cross-Linking        — vinculación de documentos aparentemente inconexos

Rob T. Lee Classification: Advanced Adversary Detection (AAD)
SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from vigia.security import _utcnow, audit_logger
from vigia.tools.forensic_db import ForensicDatabaseManager
from vigia.tools.adversarial_nlp import LanguageDetector
from vigia.tools.nlp_constants import (
    SPANISH_FUNCTION_WORDS,
    ENGLISH_FUNCTION_WORDS,
)

# CAIE integration (opcional)
try:
    from vigia.tools.caie import CrossArtifactIncongruenceEngine
    _CAIE_AVAILABLE = True
except ImportError:
    _CAIE_AVAILABLE = False
    CrossArtifactIncongruenceEngine = None  # type: ignore


# ============================================================================
# CONFIGURACIÓN TÁCTICA
# ============================================================================

ENTANGLEMENT_THRESHOLD: float = 0.15   # Jaccard >15% = sospecha
IDENTICAL_SEQUENCE_MIN: int = 30        # Palabras idénticas consecutivas mínimas
FORCED_VARIATION_CV: float = 0.05       # CV sospechosamente bajo
PHYSICAL_KEY_MIN_DOCS: int = 3          # Mínimo docs para firma física

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
# ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass(frozen=True)
class NGramFingerprint:
    """Huella n-gram para comparación de entrelazamiento."""
    doc_hash: str
    char_bigrams: FrozenSet[str]
    word_trigrams: FrozenSet[str]
    sentence_hashes: FrozenSet[str]

    def jaccard_similarity(self, other: "NGramFingerprint") -> Dict[str, float]:
        def _j(a: FrozenSet, b: FrozenSet) -> float:
            u = len(a | b)
            return len(a & b) / u if u else 0.0

        char_j = _j(self.char_bigrams, other.char_bigrams)
        word_j = _j(self.word_trigrams, other.word_trigrams)
        sent_j = _j(self.sentence_hashes, other.sentence_hashes)
        composite = char_j * 0.2 + word_j * 0.5 + sent_j * 0.3
        return {
            "char_bigram": round(char_j, 4),
            "word_trigram": round(word_j, 4),
            "sentence": round(sent_j, 4),
            "composite": round(composite, 4),
        }


@dataclass
class PhysicalKeySignature:
    """Huella de teclado físico — errores ortográficos recurrentes."""
    error_pattern: str
    error_context: str
    affected_docs: List[str]
    frequency_by_doc: Dict[str, int]

    @property
    def doc_count(self) -> int:
        return len(self.affected_docs)

    @property
    def is_factory_signature(self) -> bool:
        return self.doc_count >= PHYSICAL_KEY_MIN_DOCS


@dataclass
class ForcedVarietyProfile:
    """Perfil de variedad léxica artificial."""
    doc_hash: str
    ttr_score: float
    synonym_density: float
    cv_local: float
    ttr_deviation_from_batch: float
    is_artificially_varied: bool


@dataclass
class EntanglementReport:
    """Reporte de análisis de entrelazamiento."""
    batch_id: str
    document_count: int
    entanglement_matrix: Dict[Tuple[str, str], Dict[str, float]]
    identical_sequences: List[Dict]
    physical_key_signatures: List[PhysicalKeySignature]
    forced_variety_anomalies: List[ForcedVarietyProfile]
    is_factory_production: bool
    estimated_operator_count: int
    confidence: float

    def to_caie_fractures(self) -> List[Dict]:
        """Convierte hallazgos en fracturas para inyección en CAIE."""
        fractures: List[Dict] = []

        if self.is_factory_production:
            fractures.append({
                "type": "FACTORY_PRODUCTION_DETECTED",
                "severity": self.confidence,
                "batch_id": self.batch_id,
                "estimated_operators": self.estimated_operator_count,
                "mitre_ttp": "T1585",
            })

        if self.identical_sequences:
            fractures.append({
                "type": "IDENTICAL_SEQUENCES_CROSS_DOCUMENT",
                "severity": min(0.95, len(self.identical_sequences) * 0.2),
                "count": len(self.identical_sequences),
                "mitre_ttp": "T1036.005",
            })

        strong_keys = [s for s in self.physical_key_signatures if s.is_factory_signature]
        if strong_keys:
            fractures.append({
                "type": "PHYSICAL_KEY_SIGNATURE_MATCH",
                "severity": min(0.90, len(strong_keys) * 0.3),
                "signatures_found": len(strong_keys),
                "mitre_ttp": "T1585.001",
            })

        return fractures


# ============================================================================
# MOTOR DE ENTRELAZAMIENTO
# ============================================================================

class EntanglementEngine:
    """
    Motor de detección de entrelazamiento lingüístico.
    Detecta fábricas de falsificación mediante análisis de lotes.
    """

    def __init__(self, db: Optional[ForensicDatabaseManager] = None) -> None:
        self.db = db or ForensicDatabaseManager()
        self.lang_detector = LanguageDetector()

    def analyze_batch(
        self,
        document_paths: List[str],
        batch_id: Optional[str] = None,
    ) -> EntanglementReport:
        """Análisis completo de lote de documentos."""
        if not batch_id:
            batch_id = (
                f"BATCH_{hashlib.sha256(''.join(document_paths).encode()).hexdigest()[:12]}"
            )

        fingerprints: Dict[str, NGramFingerprint] = {}
        texts: Dict[str, str] = {}
        errors_by_doc: Dict[str, Counter] = {}

        for path in document_paths:
            doc_hash, text, fingerprint, errors = self._process_document(path)
            fingerprints[doc_hash] = fingerprint
            texts[doc_hash] = text
            errors_by_doc[doc_hash] = errors

        matrix = self._calc_entanglement_matrix(fingerprints)
        identical_seqs = self._find_identical_sequences(texts)
        physical_keys = self._extract_physical_key_signatures(errors_by_doc)
        variety_profiles = self._analyze_forced_variety(texts)
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

        self._persist_entanglement(report, fingerprints)
        return report

    # ------------------------------------------------------------------
    # Procesamiento de documento individual
    # ------------------------------------------------------------------

    def _process_document(
        self, path: str
    ) -> Tuple[str, str, NGramFingerprint, Counter]:
        ext = Path(path).suffix.lower()
        if ext == ".pdf":
            text = self._extract_pdf_text(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        text = text[:1_000_000]  # Límite memoria (Qwen)
        doc_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        lang_code = self.lang_detector.detect(text).value

        char_bigrams = frozenset(text[i:i+2].lower() for i in range(len(text)-1))

        if lang_code == "es":
            words = [
                w for w in re.findall(r"\b[a-zA-Záéíóúñ]+\b", text.lower())
                if w not in SPANISH_FUNCTION_WORDS
            ]
        else:
            words = [
                w for w in re.findall(r"\b[a-zA-Z]+\b", text.lower())
                if w not in ENGLISH_FUNCTION_WORDS
            ]

        word_trigrams = frozenset(
            f"{words[i]}_{words[i+1]}_{words[i+2]}"
            for i in range(len(words)-2)
        )

        sentences = re.split(r"[.!?]+", text)
        sentence_hashes = frozenset(
            hashlib.sha256(s.strip().lower().encode()).hexdigest()[:16]
            for s in sentences if len(s.strip()) > 20
        )

        fingerprint = NGramFingerprint(
            doc_hash=doc_hash,
            char_bigrams=char_bigrams,
            word_trigrams=word_trigrams,
            sentence_hashes=sentence_hashes,
        )
        errors = self._extract_spelling_errors(text)
        return doc_hash, text, fingerprint, errors

    def _extract_pdf_text(self, path: str) -> str:
        try:
            import PyPDF2
            parts: List[str] = []
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
            return "\n".join(parts)
        except Exception as exc:
            audit_logger.log_info(
                event_type="ENTANGLEMENT_PDF_FAIL",
                tool="EntanglementEngine",
                message=str(exc),
            )
            return ""

    def _extract_spelling_errors(self, text: str) -> Counter:
        errors: Counter = Counter()
        patterns = [
            (r"\b\w*([a-z])\1{2,}\w*\b", "triple_letter"),
            (r"\b\w*ie\w*ei\w*\b", "ie_ei_confusion"),
            (r"\b\w*ll\w*l\w*\b", "double_l_single"),
            (r"\b\w*rr\w*r\w*\b", "double_r_single"),
            (r"\b\w*h\w*\b", "h_aspirate"),
        ]
        for pattern, error_type in patterns:
            for match in re.findall(pattern, text.lower()):
                ctx_start = max(0, text.lower().find(match) - 10)
                ctx_end = min(len(text), text.lower().find(match) + len(match) + 10)
                ctx = text.lower()[ctx_start:ctx_end]
                key = f"{error_type}:{match}:{hashlib.sha256(ctx.encode()).hexdigest()[:8]}"
                errors[key] += 1
        return errors

    # ------------------------------------------------------------------
    # Análisis de entrelazamiento
    # ------------------------------------------------------------------

    def _calc_entanglement_matrix(
        self, fingerprints: Dict[str, NGramFingerprint]
    ) -> Dict[Tuple[str, str], Dict[str, float]]:
        matrix: Dict[Tuple[str, str], Dict[str, float]] = {}
        hashes = list(fingerprints.keys())
        for i, h1 in enumerate(hashes):
            for h2 in hashes[i+1:]:
                sims = fingerprints[h1].jaccard_similarity(fingerprints[h2])
                matrix[(h1, h2)] = sims
                matrix[(h2, h1)] = sims
        return matrix

    def _find_identical_sequences(self, texts: Dict[str, str]) -> List[Dict]:
        seqs_by_doc: Dict[str, List[Tuple[int, str, str]]] = {}
        for doc_hash, text in texts.items():
            words = re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", text.lower())
            seqs = []
            for i in range(len(words) - IDENTICAL_SEQUENCE_MIN):
                seq = " ".join(words[i:i+IDENTICAL_SEQUENCE_MIN])
                is_std = any(
                    formula in seq
                    for formula in (LEGAL_FORMULAS_ES | LEGAL_FORMULAS_EN)
                )
                if not is_std:
                    seq_hash = hashlib.sha256(seq.encode()).hexdigest()[:16]
                    seqs.append((i, seq_hash, seq))
            seqs_by_doc[doc_hash] = seqs

        locations: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        for doc_hash, seqs in seqs_by_doc.items():
            for pos, seq_hash, _ in seqs:
                locations[seq_hash].append((doc_hash, pos))

        identical = []
        for seq_hash, locs in locations.items():
            if len(locs) >= 2 and len({l[0] for l in locs}) >= 2:
                first_doc, first_pos = locs[0]
                words = re.findall(
                    r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", texts[first_doc].lower()
                )
                seq_text = " ".join(words[first_pos:first_pos+IDENTICAL_SEQUENCE_MIN])
                identical.append({
                    "hash": seq_hash,
                    "text": seq_text,
                    "length": IDENTICAL_SEQUENCE_MIN,
                    "documents": [l[0] for l in locs],
                    "positions": {l[0]: l[1] for l in locs},
                })
        return identical

    def _extract_physical_key_signatures(
        self, errors_by_doc: Dict[str, Counter]
    ) -> List[PhysicalKeySignature]:
        all_errors: Dict[str, List[str]] = defaultdict(list)
        for doc_hash, errors in errors_by_doc.items():
            for key, count in errors.items():
                all_errors[key].extend([doc_hash] * count)

        signatures = []
        for error_key, doc_list in all_errors.items():
            unique_docs = list(set(doc_list))
            if len(unique_docs) >= PHYSICAL_KEY_MIN_DOCS:
                parts = error_key.split(":")
                pattern = parts[1] if len(parts) > 1 else error_key
                sig = PhysicalKeySignature(
                    error_pattern=pattern,
                    error_context=parts[0] if parts else "unknown",
                    affected_docs=unique_docs,
                    frequency_by_doc={d: doc_list.count(d) for d in unique_docs},
                )
                signatures.append(sig)
        signatures.sort(key=lambda s: s.doc_count, reverse=True)
        return signatures

    def _analyze_forced_variety(
        self, texts: Dict[str, str]
    ) -> List[ForcedVarietyProfile]:
        all_words = SPANISH_FUNCTION_WORDS | ENGLISH_FUNCTION_WORDS
        ttr_scores: List[Tuple[str, float]] = []

        for doc_hash, text in texts.items():
            words = re.findall(r"\b[a-zA-ZáéíóúñÁÉÍÓÚÑ]+\b", text.lower())
            content = [w for w in words if w not in all_words]
            if content:
                ttr_scores.append((doc_hash, len(set(content)) / len(content)))

        if len(ttr_scores) < 2:
            return []

        mean_ttr = statistics.mean(t[1] for t in ttr_scores)
        std_ttr = statistics.stdev(t[1] for t in ttr_scores) if len(ttr_scores) > 1 else 0.01

        profiles = []
        for doc_hash, ttr in ttr_scores:
            deviation = abs(ttr - mean_ttr) / max(std_ttr, 0.001)
            syn_density = self._synonym_density(texts[doc_hash])
            cv_local = self._local_cv(texts[doc_hash])
            is_forced = deviation < 0.5 and syn_density > 0.15 and cv_local < FORCED_VARIATION_CV
            profiles.append(ForcedVarietyProfile(
                doc_hash=doc_hash, ttr_score=ttr,
                synonym_density=syn_density, cv_local=cv_local,
                ttr_deviation_from_batch=deviation,
                is_artificially_varied=is_forced,
            ))
        return profiles

    def _synonym_density(self, text: str) -> float:
        synonym_groups = [
            {"importante", "relevante", "significativo", "trascendental", "notable", "sustancial"},
            {"bueno", "óptimo", "favorable", "positivo", "conveniente", "adecuado"},
            {"malo", "desfavorable", "negativo", "inadecuado", "perjudicial"},
            {"rápido", "veloz", "pronto", "inmediato", "urgente", "precipitado"},
            {"lento", "tardío", "demorado", "pausado", "gradual"},
        ]
        words = set(re.findall(r"\b[a-zA-Záéíóúñ]+\b", text.lower()))
        hits = sum(1 for g in synonym_groups if len(words & g) > 1)
        return hits / max(len(words), 1)

    def _local_cv(self, text: str) -> float:
        all_words = SPANISH_FUNCTION_WORDS | ENGLISH_FUNCTION_WORDS
        words = re.findall(r"\b[a-zA-Záéíóúñ]+\b", text.lower())
        content = [w for w in words if w not in all_words]
        if len(content) < 200:
            return 1.0
        window_ttrs = []
        for i in range(0, len(content) - 100, 50):
            w = content[i:i+100]
            window_ttrs.append(len(set(w)) / len(w))
        if len(window_ttrs) < 2:
            return 1.0
        mean_t = statistics.mean(window_ttrs)
        std_t = statistics.stdev(window_ttrs)
        return std_t / mean_t if mean_t > 0 else 1.0

    def _assess_factory_production(
        self,
        matrix: Dict,
        identical_seqs: List[Dict],
        physical_keys: List[PhysicalKeySignature],
        variety_profiles: List[ForcedVarietyProfile],
    ) -> Tuple[bool, int, float]:
        score = 0.0

        if matrix:
            high_ent = sum(
                1 for sims in matrix.values()
                if sims.get("composite", 0) > ENTANGLEMENT_THRESHOLD
            )
            score += min(1.5, high_ent / max(len(matrix), 1) * 3)

        if identical_seqs:
            score += min(1.5, len(identical_seqs) * 0.5)

        strong = [s for s in physical_keys if s.is_factory_signature]
        if strong:
            score += min(1.5, len(strong) * 0.5)

        forced = sum(1 for p in variety_profiles if p.is_artificially_varied)
        if forced and variety_profiles:
            score += min(0.5, forced / len(variety_profiles))

        return score >= 2.0, max(1, len(strong)), min(1.0, score / 5.0)

    # ------------------------------------------------------------------
    # Persistencia SQLite
    # ------------------------------------------------------------------

    def _persist_entanglement(
        self, report: EntanglementReport, fingerprints: Dict[str, NGramFingerprint]
    ) -> None:
        with self.db.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entanglement_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    doc_hash TEXT NOT NULL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_factory_linked BOOLEAN,
                    batch_confidence REAL,
                    physical_signatures TEXT,
                    identical_sequences TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entanglement_doc
                ON entanglement_analysis(doc_hash)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_entanglement_batch
                ON entanglement_analysis(batch_id)
            """)

            for doc_hash in fingerprints:
                sigs = [
                    s.error_pattern
                    for s in report.physical_key_signatures
                    if doc_hash in s.affected_docs
                ]
                seqs = [
                    s["hash"]
                    for s in report.identical_sequences
                    if doc_hash in s["documents"]
                ]
                conn.execute("""
                    INSERT INTO entanglement_analysis
                    (batch_id, doc_hash, is_factory_linked, batch_confidence,
                     physical_signatures, identical_sequences)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    report.batch_id, doc_hash,
                    report.is_factory_production, report.confidence,
                    json.dumps(sigs), json.dumps(seqs),
                ))
            conn.commit()

    def query_cross_linked(self, doc_hash: str) -> List[Dict]:
        """Consulta documentos entrelazados — descubre redes de falsificación."""
        with self.db.connection() as conn:
            rows = conn.execute("""
                SELECT e2.doc_hash, e2.batch_id, e2.batch_confidence
                FROM entanglement_analysis e1
                JOIN entanglement_analysis e2
                    ON e1.batch_id = e2.batch_id
                    AND e1.doc_hash != e2.doc_hash
                WHERE e1.doc_hash = ?
                AND e1.is_factory_linked = 1
            """, (doc_hash,)).fetchall()
        return [dict(r) for r in rows]


# ============================================================================
# INTEGRACIÓN CON CAIE
# ============================================================================

class EntanglementCAIEIntegration:
    """Puente entre EntanglementEngine y CrossArtifactIncongruenceEngine."""

    def __init__(self, engine: EntanglementEngine) -> None:
        self.engine = engine

    def analyze_and_inject(
        self,
        document_paths: List[str],
        batch_id: Optional[str] = None,
    ) -> EntanglementReport:
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
                    tool="EntanglementCAIEIntegration",
                    message=(
                        f"batch_id={report.batch_id} "
                        f"fractures={len(report.to_caie_fractures())}"
                    ),
                )
            except Exception as exc:
                audit_logger.log_info(
                    event_type="ENTANGLEMENT_CAIE_FAILED",
                    tool="EntanglementCAIEIntegration",
                    message=str(exc),
                )

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
    document_paths   : Lista de rutas a documentos del lote
    batch_id         : ID opcional del lote (auto-generado si None)
    cross_link_query : Si se proporciona, retorna docs entrelazados con este hash

    Returns
    -------
    Dict con EntanglementReport o resultados de query cruzada.
    is_factory_production=True significa que los documentos del lote
    probablemente provienen de la misma matriz de falsificación.
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
                "timestamp": _utcnow(),
            }

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
                for s in report.physical_key_signatures[:5]
            ],
            "identical_sequences_count": len(report.identical_sequences),
            "forced_variety_anomalies": sum(
                1 for p in report.forced_variety_anomalies if p.is_artificially_varied
            ),
            "fractures_generated": len(report.to_caie_fractures()),
            "mitre_ttps": list({
                f.get("mitre_ttp") for f in report.to_caie_fractures()
                if f.get("mitre_ttp")
            }),
            "timestamp": _utcnow(),
        }

    except Exception as exc:
        audit_logger.log_block(
            event_type="ENTANGLEMENT_ERROR",
            tool="analyze_document_entanglement",
            input_preview=str(document_paths)[:100],
            reason=str(exc),
        )
        return {
            "status": "ERROR",
            "error": str(exc),
            "timestamp": _utcnow(),
        }
