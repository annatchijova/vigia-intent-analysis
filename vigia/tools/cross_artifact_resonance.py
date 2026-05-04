# vigia/tools/cross_artifact_resonance.py
"""
Cross-Artifact Resonance Analyzer - Coherencia Semántica Multi-Artefacto

Principio: Un atacante puede falsificar un email perfecto y un PDF perfecto,
pero es difícil que sean semánticamente coherentes cuando se analizan juntos.

Author: VIGÍA Collective
License: Open Source
"""

from fractions import Fraction
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict
import re
import hashlib


@dataclass(frozen=True)
class ArtifactClaim:
    """Claim extraído de un artefacto."""
    source: str  # "Email:Subject", "PDF:Title", etc
    claim_type: str  # "temporal", "topic", "entity", "action"
    value: str
    confidence: Fraction
    evidence: Dict


@dataclass(frozen=True)
class SemanticConflict:
    """Conflicto semántico entre artefactos."""
    artifact1: str
    artifact2: str
    conflict_type: str  # "temporal", "topic", "entity", "causality"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    evidence: Dict


@dataclass(frozen=True)
class ResonanceAnalysis:
    """Resultado de análisis de resonancia."""
    artifacts_analyzed: List[str]
    claims_extracted: List[ArtifactClaim]
    conflicts_detected: List[SemanticConflict]
    coherence_score: Fraction  # 0=total incoherencia, 1=coherencia perfecta
    verdict: str
    confidence: Fraction
    reasoning: str
    evidence: Dict


class CrossArtifactResonanceAnalyzer:
    """
    Detecta incoherencias semánticas entre artefactos relacionados.
    
    Detecta:
    - Temporal mismatches (email habla de Q4 2024, PDF dice Q1 2023)
    - Topic mismatches (email: "financial report", PDF: "vacation photos")
    - Entity mismatches (email: "John Smith", PDF metadata: "Unknown Author")
    - Causality violations (email: "adjunto reporte", pero no hay attachment)
    """
    
    # Taxonomía de topics
    TOPIC_TAXONOMY = {
        'financial': {'revenue', 'ebitda', 'budget', 'forecast', 'profit', 'loss', 'quarter', 'fiscal'},
        'personal': {'vacation', 'family', 'personal', 'holiday', 'birthday', 'anniversary'},
        'technical': {'server', 'database', 'code', 'bug', 'deployment', 'infrastructure'},
        'legal': {'contract', 'agreement', 'lawsuit', 'attorney', 'court', 'settlement'},
        'medical': {'patient', 'diagnosis', 'treatment', 'prescription', 'symptoms', 'doctor'}
    }
    
    # Palabras de acción que implican attachments
    ATTACHMENT_VERBS = {
        'attach', 'attached', 'adjunto', 'included', 'enclosed',
        'find', 'see', 'review', 'please find'
    }
    
    def analyze(self, artifacts: List[Dict]) -> ResonanceAnalysis:
        """
        Analiza coherencia entre múltiples artefactos.
        
        Args:
            artifacts: Lista de dicts con:
                - type: 'email' | 'pdf' | 'docx' | 'image'
                - content: str (texto extraído)
                - metadata: dict (autor, fecha, etc)
                - path: Path (opcional)
        
        Returns:
            ResonanceAnalysis con veredicto
        """
        if len(artifacts) < 2:
            return self._insufficient_artifacts()
        
        # Extraer claims de cada artefacto
        all_claims = []
        for artifact in artifacts:
            claims = self._extract_claims(artifact)
            all_claims.extend(claims)
        
        # Detectar conflictos entre claims
        conflicts = self._detect_conflicts(all_claims, artifacts)
        
        # Calcular coherence score
        coherence = self._calculate_coherence(all_claims, conflicts)
        
        # Evaluación
        verdict, confidence, reasoning, evidence = self._evaluate_resonance(
            conflicts, coherence, len(artifacts)
        )
        
        return ResonanceAnalysis(
            artifacts_analyzed=[a.get('type', 'unknown') for a in artifacts],
            claims_extracted=all_claims,
            conflicts_detected=conflicts,
            coherence_score=coherence,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _extract_claims(self, artifact: Dict) -> List[ArtifactClaim]:
        """
        Extrae claims de un artefacto.
        
        Claims son afirmaciones verificables:
        - Temporal: "Q4 2024", "January 2025"
        - Topic: "financial report", "vacation photos"
        - Entity: "John Smith", "Acme Corp"
        - Action: "attached file", "see below"
        """
        claims = []
        artifact_type = artifact.get('type', 'unknown')
        content = artifact.get('content', '')
        metadata = artifact.get('metadata', {})
        
        # CLAIM 1: Temporal claims
        temporal_claims = self._extract_temporal_claims(content, artifact_type)
        claims.extend(temporal_claims)
        
        # CLAIM 2: Topic claims
        topic_claims = self._extract_topic_claims(content, artifact_type)
        claims.extend(topic_claims)
        
        # CLAIM 3: Entity claims (de metadata)
        entity_claims = self._extract_entity_claims(metadata, artifact_type)
        claims.extend(entity_claims)
        
        # CLAIM 4: Action claims
        action_claims = self._extract_action_claims(content, artifact_type)
        claims.extend(action_claims)
        
        return claims
    
    def _extract_temporal_claims(self, content: str, source: str) -> List[ArtifactClaim]:
        """Extrae referencias temporales."""
        claims = []
        
        # Años (YYYY)
        years = re.findall(r'\b(20[12]\d)\b', content)
        for year in set(years):
            claims.append(ArtifactClaim(
                source=f"{source}:Year",
                claim_type="temporal",
                value=year,
                confidence=Fraction(8, 10),
                evidence={'pattern': 'YYYY', 'raw': year}
            ))
        
        # Quarters (Q1-Q4)
        quarters = re.findall(r'\b(Q[1-4])\s*(20[12]\d)?\b', content, re.I)
        for quarter_match in quarters:
            quarter = quarter_match[0].upper()
            year = quarter_match[1] if quarter_match[1] else ''
            value = f"{quarter} {year}".strip()
            claims.append(ArtifactClaim(
                source=f"{source}:Quarter",
                claim_type="temporal",
                value=value,
                confidence=Fraction(9, 10),
                evidence={'pattern': 'Q[1-4] YYYY', 'raw': value}
            ))
        
        # Meses
        months = re.findall(
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s*(20[12]\d)?\b',
            content,
            re.I
        )
        for month_match in months:
            month = month_match[0].capitalize()
            year = month_match[1] if month_match[1] else ''
            value = f"{month} {year}".strip()
            claims.append(ArtifactClaim(
                source=f"{source}:Month",
                claim_type="temporal",
                value=value,
                confidence=Fraction(7, 10),
                evidence={'pattern': 'Month YYYY', 'raw': value}
            ))
        
        return claims
    
    def _extract_topic_claims(self, content: str, source: str) -> List[ArtifactClaim]:
        """Extrae topic principal del contenido."""
        claims = []
        content_lower = content.lower()
        
        # Buscar matches con taxonomía
        topic_scores = defaultdict(int)
        for topic, keywords in self.TOPIC_TAXONOMY.items():
            for keyword in keywords:
                if keyword in content_lower:
                    topic_scores[topic] += 1
        
        # Claim del topic dominante
        if topic_scores:
            dominant_topic = max(topic_scores.items(), key=lambda x: x[1])
            topic_name, score = dominant_topic
            
            # Confianza proporcional a score
            confidence = min(Fraction(score, 10), Fraction(10, 10))
            
            claims.append(ArtifactClaim(
                source=f"{source}:Topic",
                claim_type="topic",
                value=topic_name,
                confidence=confidence,
                evidence={'keyword_matches': score, 'keywords_found': topic_scores}
            ))
        
        return claims
    
    def _extract_entity_claims(self, metadata: Dict, source: str) -> List[ArtifactClaim]:
        """Extrae entidades de metadata."""
        claims = []
        
        # Autor
        if 'author' in metadata and metadata['author']:
            author = metadata['author']
            # Filtrar valores genéricos
            if author.lower() not in {'unknown', 'user', 'admin', ''}:
                claims.append(ArtifactClaim(
                    source=f"{source}:Author",
                    claim_type="entity",
                    value=author,
                    confidence=Fraction(7, 10),
                    evidence={'metadata_field': 'author'}
                ))
        
        # Título
        if 'title' in metadata and metadata['title']:
            title = metadata['title']
            claims.append(ArtifactClaim(
                source=f"{source}:Title",
                claim_type="entity",
                value=title,
                confidence=Fraction(8, 10),
                evidence={'metadata_field': 'title'}
            ))
        
        # Subject (emails)
        if 'subject' in metadata and metadata['subject']:
            subject = metadata['subject']
            claims.append(ArtifactClaim(
                source=f"{source}:Subject",
                claim_type="entity",
                value=subject,
                confidence=Fraction(9, 10),
                evidence={'metadata_field': 'subject'}
            ))
        
        return claims
    
    def _extract_action_claims(self, content: str, source: str) -> List[ArtifactClaim]:
        """Extrae acciones mencionadas (ej: 'attached file')."""
        claims = []
        content_lower = content.lower()
        
        # Detectar referencias a attachments
        for verb in self.ATTACHMENT_VERBS:
            if verb in content_lower:
                claims.append(ArtifactClaim(
                    source=f"{source}:Action",
                    claim_type="action",
                    value=f"references_attachment:{verb}",
                    confidence=Fraction(6, 10),
                    evidence={'verb': verb, 'context': content_lower[:200]}
                ))
                break  # Solo un claim de attachment
        
        return claims
    
    def _detect_conflicts(
        self,
        claims: List[ArtifactClaim],
        artifacts: List[Dict]
    ) -> List[SemanticConflict]:
        """Detecta conflictos entre claims."""
        conflicts = []
        
        # Agrupar claims por tipo
        temporal_claims = [c for c in claims if c.claim_type == "temporal"]
        topic_claims = [c for c in claims if c.claim_type == "topic"]
        action_claims = [c for c in claims if c.claim_type == "action"]
        
        # CONFLICTO 1: Temporal mismatch
        conflicts.extend(self._detect_temporal_conflicts(temporal_claims))
        
        # CONFLICTO 2: Topic mismatch
        conflicts.extend(self._detect_topic_conflicts(topic_claims))
        
        # CONFLICTO 3: Missing attachments
        conflicts.extend(self._detect_missing_attachments(action_claims, artifacts))
        
        # CONFLICTO 4: Entity mismatch
        entity_claims = [c for c in claims if c.claim_type == "entity"]
        conflicts.extend(self._detect_entity_conflicts(entity_claims))
        
        return conflicts
    
    def _detect_temporal_conflicts(self, claims: List[ArtifactClaim]) -> List[SemanticConflict]:
        """Detecta inconsistencias temporales entre artefactos."""
        conflicts = []
        
        # Extraer años mencionados por artefacto
        years_by_artifact = defaultdict(set)
        for claim in claims:
            artifact = claim.source.split(':')[0]
            # Extraer año del value
            year_match = re.search(r'20[12]\d', claim.value)
            if year_match:
                years_by_artifact[artifact].add(year_match.group())
        
        # Comparar pares de artefactos
        artifacts = list(years_by_artifact.keys())
        for i, art1 in enumerate(artifacts):
            for art2 in artifacts[i+1:]:
                years1 = years_by_artifact[art1]
                years2 = years_by_artifact[art2]
                
                # Si no hay overlap, es sospechoso
                if years1 and years2 and not years1.intersection(years2):
                    conflicts.append(SemanticConflict(
                        artifact1=art1,
                        artifact2=art2,
                        conflict_type="temporal",
                        severity="HIGH",
                        description=f"Temporal mismatch: {art1} mentions {years1}, {art2} mentions {years2}",
                        evidence={
                            'years1': list(years1),
                            'years2': list(years2)
                        }
                    ))
        
        return conflicts
    
    def _detect_topic_conflicts(self, claims: List[ArtifactClaim]) -> List[SemanticConflict]:
        """Detecta inconsistencias de topic."""
        conflicts = []
        
        # Extraer topics por artefacto
        topics_by_artifact = {}
        for claim in claims:
            artifact = claim.source.split(':')[0]
            topics_by_artifact[artifact] = claim.value
        
        # Definir topics incompatibles
        incompatible_pairs = [
            ('financial', 'personal'),
            ('financial', 'medical'),
            ('technical', 'personal'),
            ('legal', 'personal')
        ]
        
        # Comparar pares
        artifacts = list(topics_by_artifact.keys())
        for i, art1 in enumerate(artifacts):
            for art2 in artifacts[i+1:]:
                topic1 = topics_by_artifact[art1]
                topic2 = topics_by_artifact[art2]
                
                # Verificar si son incompatibles
                if (topic1, topic2) in incompatible_pairs or (topic2, topic1) in incompatible_pairs:
                    conflicts.append(SemanticConflict(
                        artifact1=art1,
                        artifact2=art2,
                        conflict_type="topic",
                        severity="CRITICAL",
                        description=f"Topic mismatch: {art1} is '{topic1}', {art2} is '{topic2}'",
                        evidence={
                            'topic1': topic1,
                            'topic2': topic2,
                            'incompatible': True
                        }
                    ))
        
        return conflicts
    
    def _detect_missing_attachments(
        self,
        action_claims: List[ArtifactClaim],
        artifacts: List[Dict]
    ) -> List[SemanticConflict]:
        """Detecta referencias a attachments que no existen."""
        conflicts = []
        
        # Contar artefactos no-email
        non_email_artifacts = [a for a in artifacts if a.get('type') != 'email']
        
        # Buscar claims de attachment en emails
        attachment_refs = [c for c in action_claims if 'references_attachment' in c.value]
        
        # Si hay referencia pero no hay attachments
        if attachment_refs and not non_email_artifacts:
            conflicts.append(SemanticConflict(
                artifact1="email",
                artifact2="missing",
                conflict_type="causality",
                severity="CRITICAL",
                description="Email references attachment but none found",
                evidence={
                    'reference_count': len(attachment_refs),
                    'verbs': [c.evidence.get('verb') for c in attachment_refs]
                }
            ))
        
        return conflicts
    
    def _detect_entity_conflicts(self, claims: List[ArtifactClaim]) -> List[SemanticConflict]:
        """Detecta inconsistencias en entidades (autor, título)."""
        conflicts = []
        
        # Agrupar autores
        authors = [c for c in claims if 'Author' in c.source]
        if len(set(c.value for c in authors)) > 1:
            # Múltiples autores distintos
            author_values = {c.value for c in authors}
            conflicts.append(SemanticConflict(
                artifact1="multiple",
                artifact2="artifacts",
                conflict_type="entity",
                severity="MEDIUM",
                description=f"Multiple authors claimed: {author_values}",
                evidence={'authors': list(author_values)}
            ))
        
        return conflicts
    
    def _calculate_coherence(
        self,
        claims: List[ArtifactClaim],
        conflicts: List[SemanticConflict]
    ) -> Fraction:
        """
        Calcula score de coherencia global.
        
        coherence = 1 - (weighted_conflicts / total_possible_conflicts)
        """
        if not claims:
            return Fraction(0)
        
        # Calcular conflictos ponderados
        severity_weights = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        
        weighted_conflicts = sum(
            severity_weights.get(c.severity, 1)
            for c in conflicts
        )
        
        # Máximo posible (todos los claims en conflicto)
        max_possible = len(claims) * 4  # Asumiendo severity CRITICAL
        
        if max_possible == 0:
            return Fraction(1)
        
        # Coherence = 1 - (conflictos / máximo)
        coherence = Fraction(1) - Fraction(weighted_conflicts, max_possible)
        
        # Saturar en [0, 1]
        if coherence < 0:
            coherence = Fraction(0)
        
        return coherence
    
    def _evaluate_resonance(
        self,
        conflicts: List[SemanticConflict],
        coherence: Fraction,
        artifact_count: int
    ) -> Tuple[str, Fraction, str, Dict]:
        """Evalúa resonancia y genera veredicto."""
        if not conflicts:
            return (
                "BENIGN",
                Fraction(9, 10),
                "Cross-artifact coherence verified",
                {'coherence_score': str(coherence)}
            )
        
        # Contar por severidad
        critical = sum(1 for c in conflicts if c.severity == "CRITICAL")
        high = sum(1 for c in conflicts if c.severity == "HIGH")
        medium = sum(1 for c in conflicts if c.severity == "MEDIUM")
        
        # Calcular confianza
        confidence = Fraction(0)
        
        if critical > 0:
            confidence += Fraction(8, 10)
        if high > 0:
            confidence += Fraction(5, 10)
        if medium > 0:
            confidence += Fraction(3, 10)
        
        # Saturar
        if confidence > Fraction(10, 10):
            confidence = Fraction(10, 10)
        
        # Reasoning
        reasoning_parts = []
        if critical:
            reasoning_parts.append(f"{critical} CRITICAL conflicts")
        if high:
            reasoning_parts.append(f"{high} HIGH conflicts")
        if medium:
            reasoning_parts.append(f"{medium} MEDIUM conflicts")
        
        reasoning = f"CROSS_ARTIFACT_INCOHERENCE: " + ", ".join(reasoning_parts)
        reasoning += f" (coherence score: {float(coherence):.2f})"
        
        # Veredicto
        if confidence >= Fraction(8, 10):
            verdict = "MALICIOUS"
        elif confidence >= Fraction(5, 10):
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"
        
        evidence = {
            'conflict_count': len(conflicts),
            'critical': critical,
            'high': high,
            'medium': medium,
            'coherence_score': str(coherence),
            'artifacts_analyzed': artifact_count,
            'examples': [
                {
                    'type': c.conflict_type,
                    'severity': c.severity,
                    'description': c.description
                }
                for c in conflicts[:3]  # Top 3
            ]
        }
        
        return verdict, confidence, reasoning, evidence
    
    def _insufficient_artifacts(self) -> ResonanceAnalysis:
        """Resultado para caso con < 2 artefactos."""
        return ResonanceAnalysis(
            artifacts_analyzed=[],
            claims_extracted=[],
            conflicts_detected=[],
            coherence_score=Fraction(0),
            verdict="ABSTAIN",
            confidence=Fraction(0),
            reasoning="Need at least 2 artifacts for resonance analysis",
            evidence={}
        )


# =============================================================================
# INTEGRACIÓN CON VIGÍA
# =============================================================================

if __name__ == '__main__':
    # Test de ejemplo: BEC attack
    print("="*70)
    print("CROSS-ARTIFACT RESONANCE ANALYZER - TEST")
    print("="*70)
    
    # Caso: Email del "CFO" con PDF sospechoso
    email_artifact = {
        'type': 'email',
        'content': """
        Subject: Q4 2024 Financial Report
        
        Dear Team,
        
        Please find attached the Q4 2024 financial report for your review.
        The revenue projections and EBITDA forecast are included.
        
        Best regards,
        CFO
        """,
        'metadata': {
            'subject': 'Q4 2024 Financial Report',
            'author': 'CFO',
            'date': '2025-01-20'
        }
    }
    
    pdf_artifact = {
        'type': 'pdf',
        'content': """
        Vacation Photos - Summer 2023
        
        Family trip to beach. Great weather!
        """,
        'metadata': {
            'title': 'Vacation Photos 2023',
            'author': 'Unknown',
            'creationDate': '2023-08-15'
        }
    }
    
    # Analizar
    analyzer = CrossArtifactResonanceAnalyzer()
    result = analyzer.analyze([email_artifact, pdf_artifact])
    
    print(f"\nArtifacts analyzed: {result.artifacts_analyzed}")
    print(f"Claims extracted: {len(result.claims_extracted)}")
    
    print(f"\nClaims:")
    for claim in result.claims_extracted:
        print(f"  - {claim.source}: {claim.claim_type} = '{claim.value}' (confidence: {int(claim.confidence*100)}%)")
    
    print(f"\nConflicts detected: {len(result.conflicts_detected)}")
    for conflict in result.conflicts_detected:
        print(f"  [{conflict.severity}] {conflict.conflict_type.upper()}")
        print(f"  {conflict.description}")
    
    print(f"\n{'='*70}")
    print(f"COHERENCE SCORE: {float(result.coherence_score):.2f}")
    print(f"VERDICT: {result.verdict}")
    print(f"CONFIDENCE: {int(result.confidence * 100)}%")
    print(f"{'='*70}")
    print(f"\nREASONING:\n{result.reasoning}")
    print(f"\nEVIDENCE:\n{result.evidence}")
    print(f"{'='*70}\n")
