# vigia/tools/behavioral_fingerprint.py
"""
Behavioral Fingerprint Analyzer - Detección por Desviación de Hábitos

Principio: Un atacante puede falsificar UN artefacto, pero no puede falsificar
6 meses de historial de comportamiento consistente.

Author: VIGÍA Collective
License: Open Source
"""

from fractions import Fraction
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, time
import re
import hashlib


@dataclass(frozen=True)
class BehavioralProfile:
    """Perfil de comportamiento de un usuario/sistema."""
    user_id: str
    
    # Patrones de naming
    naming_patterns: List[str]  # regex patterns
    naming_consistency: Fraction
    
    # Horarios típicos (0-23)
    typical_hours: List[int]
    hour_consistency: Fraction
    
    # Software habitual
    typical_software: Dict[str, int]  # {"Adobe Acrobat DC": 45, ...}
    software_diversity: Fraction  # Qué tan diverso es el software usado
    
    # Vocabulario característico
    typical_vocabulary: Set[str]
    vocabulary_size: int
    
    # Estructuras de archivos
    typical_file_sizes: Dict[str, Tuple[int, int]]  # {ext: (min, max)}
    
    # Metadata
    sample_count: int
    date_range: Tuple[datetime, datetime]
    profile_hash: str  # Hash del perfil para verificación


@dataclass(frozen=True)
class BehavioralDeviation:
    """Desviación detectada del perfil."""
    category: str  # "naming", "timing", "software", "vocabulary", "structure"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    confidence: Fraction
    description: str
    evidence: Dict


@dataclass(frozen=True)
class BehavioralAnalysis:
    """Resultado de análisis de comportamiento."""
    user_id: str
    artifact_analyzed: str
    profile_used: Optional[BehavioralProfile]
    deviations: List[BehavioralDeviation]
    verdict: str
    confidence: Fraction
    reasoning: str
    evidence: Dict


class BehavioralFingerprintAnalyzer:
    """
    Detecta desviaciones de comportamiento habitual.
    
    Casos de uso:
    - BEC (Business Email Compromise): CEO "enviando" email desde patrón inusual
    - Account takeover: Atacante usando cuenta comprometida
    - Insider threat: Usuario legítimo con comportamiento anómalo
    """
    
    # Umbrales de desviación
    NAMING_MISMATCH_THRESHOLD = Fraction(7, 10)  # 70% de archivos deben seguir patrón
    HOUR_DEVIATION_THRESHOLD = 3  # Actividad fuera de ventana típica
    SOFTWARE_NEVER_USED_WEIGHT = Fraction(6, 10)
    VOCABULARY_UNKNOWN_THRESHOLD = Fraction(3, 10)  # >30% palabras nuevas
    FILESIZE_DEVIATION_FACTOR = 3  # 3x el tamaño típico
    
    def __init__(self):
        self.profiles: Dict[str, BehavioralProfile] = {}
    
    def learn_profile(
        self,
        user_id: str,
        historical_artifacts: List[Dict]
    ) -> BehavioralProfile:
        """
        Aprende perfil de comportamiento de corpus histórico.
        
        Args:
            user_id: Identificador único del usuario
            historical_artifacts: Lista de dicts con:
                - filename: str
                - timestamp: datetime
                - software_used: str (opcional)
                - content: str (opcional)
                - file_size: int (opcional)
                - file_type: str (opcional)
        
        Returns:
            BehavioralProfile aprendido
        """
        if not historical_artifacts:
            raise ValueError("Need at least 1 historical artifact")
        
        # Extraer patrones de naming
        filenames = [a['filename'] for a in historical_artifacts]
        patterns = self._extract_naming_patterns(filenames)
        naming_consistency = self._measure_pattern_consistency(filenames, patterns)
        
        # Analizar horarios
        timestamps = [a['timestamp'] for a in historical_artifacts if 'timestamp' in a]
        typical_hours = self._find_typical_hours(timestamps)
        hour_consistency = self._measure_hour_consistency(timestamps, typical_hours)
        
        # Analizar software
        software_counts = defaultdict(int)
        for a in historical_artifacts:
            if 'software_used' in a and a['software_used']:
                software_counts[a['software_used']] += 1
        
        software_diversity = self._calculate_diversity(software_counts)
        
        # Analizar vocabulario
        vocab = set()
        for a in historical_artifacts:
            if 'content' in a and a['content']:
                words = self._tokenize_content(a['content'])
                vocab.update(words)
        
        # Analizar tamaños de archivo por tipo
        file_sizes = defaultdict(list)
        for a in historical_artifacts:
            if 'file_size' in a and 'file_type' in a:
                file_sizes[a['file_type']].append(a['file_size'])
        
        typical_sizes = {
            ftype: (min(sizes), max(sizes))
            for ftype, sizes in file_sizes.items()
        }
        
        # Metadata temporal
        if timestamps:
            date_range = (min(timestamps), max(timestamps))
        else:
            date_range = (datetime.now(), datetime.now())
        
        # Generar hash del perfil
        profile_data = {
            'user_id': user_id,
            'patterns': sorted(patterns),
            'hours': sorted(typical_hours),
            'software': sorted(software_counts.keys()),
            'vocab_sample': sorted(list(vocab)[:100])  # Primeras 100 palabras
        }
        profile_hash = hashlib.sha256(
            str(profile_data).encode()
        ).hexdigest()[:16]
        
        profile = BehavioralProfile(
            user_id=user_id,
            naming_patterns=patterns,
            naming_consistency=naming_consistency,
            typical_hours=typical_hours,
            hour_consistency=hour_consistency,
            typical_software=dict(software_counts),
            software_diversity=software_diversity,
            typical_vocabulary=vocab,
            vocabulary_size=len(vocab),
            typical_file_sizes=typical_sizes,
            sample_count=len(historical_artifacts),
            date_range=date_range,
            profile_hash=profile_hash
        )
        
        self.profiles[user_id] = profile
        return profile
    
    def analyze_deviation(
        self,
        user_id: str,
        artifact: Dict
    ) -> BehavioralAnalysis:
        """
        Analiza cuánto se desvía un artefacto del perfil habitual.
        
        Args:
            user_id: ID del usuario
            artifact: Dict con:
                - filename: str
                - timestamp: datetime
                - software_used: str (opcional)
                - content: str (opcional)
                - file_size: int (opcional)
                - file_type: str (opcional)
        
        Returns:
            BehavioralAnalysis con veredicto
        """
        if user_id not in self.profiles:
            return BehavioralAnalysis(
                user_id=user_id,
                artifact_analyzed=artifact.get('filename', 'unknown'),
                profile_used=None,
                deviations=[],
                verdict="ABSTAIN",
                confidence=Fraction(0),
                reasoning="No behavioral profile available for user",
                evidence={}
            )
        
        profile = self.profiles[user_id]
        deviations = []
        
        # DESVIACIÓN 1: Naming pattern
        if 'filename' in artifact:
            naming_dev = self._check_naming_deviation(artifact['filename'], profile)
            if naming_dev:
                deviations.append(naming_dev)
        
        # DESVIACIÓN 2: Timing
        if 'timestamp' in artifact:
            timing_dev = self._check_timing_deviation(artifact['timestamp'], profile)
            if timing_dev:
                deviations.append(timing_dev)
        
        # DESVIACIÓN 3: Software
        if 'software_used' in artifact and artifact['software_used']:
            software_dev = self._check_software_deviation(artifact['software_used'], profile)
            if software_dev:
                deviations.append(software_dev)
        
        # DESVIACIÓN 4: Vocabulario
        if 'content' in artifact and artifact['content']:
            vocab_dev = self._check_vocabulary_deviation(artifact['content'], profile)
            if vocab_dev:
                deviations.append(vocab_dev)
        
        # DESVIACIÓN 5: Tamaño de archivo
        if 'file_size' in artifact and 'file_type' in artifact:
            size_dev = self._check_filesize_deviation(
                artifact['file_size'],
                artifact['file_type'],
                profile
            )
            if size_dev:
                deviations.append(size_dev)
        
        # Evaluación
        verdict, confidence, reasoning, evidence = self._evaluate_deviations(
            deviations, profile
        )
        
        return BehavioralAnalysis(
            user_id=user_id,
            artifact_analyzed=artifact.get('filename', 'unknown'),
            profile_used=profile,
            deviations=deviations,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _check_naming_deviation(
        self,
        filename: str,
        profile: BehavioralProfile
    ) -> Optional[BehavioralDeviation]:
        """Verifica si filename sigue patrones habituales."""
        if not profile.naming_patterns:
            return None
        
        matches = self._matches_patterns(filename, profile.naming_patterns)
        
        if not matches and profile.naming_consistency > self.NAMING_MISMATCH_THRESHOLD:
            return BehavioralDeviation(
                category="naming",
                severity="HIGH",
                confidence=Fraction(5, 10),
                description=f"Filename '{filename}' doesn't match typical patterns",
                evidence={
                    'expected_patterns': profile.naming_patterns,
                    'consistency_baseline': str(profile.naming_consistency)
                }
            )
        
        return None
    
    def _check_timing_deviation(
        self,
        timestamp: datetime,
        profile: BehavioralProfile
    ) -> Optional[BehavioralDeviation]:
        """Verifica si timing es consistente con horarios habituales."""
        hour = timestamp.hour
        
        if hour not in profile.typical_hours:
            # Calcular cuán lejos está de la ventana típica
            if profile.typical_hours:
                min_hour = min(profile.typical_hours)
                max_hour = max(profile.typical_hours)
                
                # P0-EVA-006: distancia circular para horas (wrap 23→0)
                def _circ_dist(h, t):
                    d = abs(h - t)
                    return min(d, 24 - d)
                deviation_hours = min(
                    _circ_dist(hour, min_hour),
                    _circ_dist(hour, max_hour),
                )
                
                if deviation_hours > self.HOUR_DEVIATION_THRESHOLD:
                    severity = "CRITICAL" if deviation_hours > 6 else "HIGH"
                    
                    return BehavioralDeviation(
                        category="timing",
                        severity=severity,
                        confidence=Fraction(4, 10),
                        description=f"Activity at {hour:02d}:00 (typical: {profile.typical_hours})",
                        evidence={
                            'timestamp': timestamp.isoformat(),
                            'deviation_hours': deviation_hours,
                            'typical_range': (min_hour, max_hour)
                        }
                    )
        
        return None
    
    def _check_software_deviation(
        self,
        software: str,
        profile: BehavioralProfile
    ) -> Optional[BehavioralDeviation]:
        """Verifica si software es consistente con uso habitual."""
        if software not in profile.typical_software:
            return BehavioralDeviation(
                category="software",
                severity="HIGH",
                confidence=self.SOFTWARE_NEVER_USED_WEIGHT,
                description=f"Software '{software}' never used before",
                evidence={
                    'software_used': software,
                    'typical_software': list(profile.typical_software.keys())[:5]
                }
            )
        
        return None
    
    def _check_vocabulary_deviation(
        self,
        content: str,
        profile: BehavioralProfile
    ) -> Optional[BehavioralDeviation]:
        """Verifica si vocabulario es consistente."""
        if not profile.typical_vocabulary:
            return None
        
        words = self._tokenize_content(content)
        if not words:
            return None
        
        unknown_words = set(words) - profile.typical_vocabulary
        unknown_ratio = Fraction(len(unknown_words), len(words))
        
        if unknown_ratio > self.VOCABULARY_UNKNOWN_THRESHOLD:
            severity = "HIGH" if unknown_ratio > 0.5 else "MEDIUM"
            
            return BehavioralDeviation(
                category="vocabulary",
                severity=severity,
                confidence=Fraction(int(unknown_ratio * 10), 10),
                description=f"Vocabulary mismatch: {len(unknown_words)}/{len(words)} words never used before",
                evidence={
                    'unknown_ratio': unknown_ratio,
                    'sample_unknown_words': list(unknown_words)[:10],
                    'vocabulary_size_baseline': profile.vocabulary_size
                }
            )
        
        return None
    
    def _check_filesize_deviation(
        self,
        file_size: int,
        file_type: str,
        profile: BehavioralProfile
    ) -> Optional[BehavioralDeviation]:
        """Verifica si tamaño es consistente con tipo de archivo."""
        if file_type not in profile.typical_file_sizes:
            return None
        
        min_size, max_size = profile.typical_file_sizes[file_type]
        
        if file_size > max_size * self.FILESIZE_DEVIATION_FACTOR:
            return BehavioralDeviation(
                category="structure",
                severity="MEDIUM",
                confidence=Fraction(3, 10),
                description=f"File size {file_size} >> typical range ({min_size}-{max_size})",
                evidence={
                    'file_size': file_size,
                    'typical_range': (min_size, max_size),
                    'deviation_factor': file_size / max_size
                }
            )
        
        return None
    
    def _evaluate_deviations(
        self,
        deviations: List[BehavioralDeviation],
        profile: BehavioralProfile
    ) -> Tuple[str, Fraction, str, Dict]:
        """Evalúa desviaciones y genera veredicto."""
        if not deviations:
            return (
                "BENIGN",
                Fraction(9, 10),
                "Consistent with behavioral profile",
                {'profile_hash': profile.profile_hash}
            )
        
        # Ponderar por severidad
        severity_weights = {
            'LOW': Fraction(1, 10),
            'MEDIUM': Fraction(3, 10),
            'HIGH': Fraction(5, 10),
            'CRITICAL': Fraction(8, 10)
        }
        
        total_confidence = sum(
            severity_weights[dev.severity] * dev.confidence
            for dev in deviations
        )
        
        # Saturar
        if total_confidence > Fraction(10, 10):
            total_confidence = Fraction(10, 10)
        
        # Generar reasoning
        reasoning_parts = [
            f"{dev.category.upper()}: {dev.description}"
            for dev in deviations
        ]
        reasoning = "BEHAVIORAL_ANOMALY: " + "; ".join(reasoning_parts)
        
        # Veredicto
        if total_confidence >= Fraction(8, 10):
            verdict = "MALICIOUS"
        elif total_confidence >= Fraction(5, 10):
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"
        
        evidence = {
            'deviation_count': len(deviations),
            'categories': [dev.category for dev in deviations],
            'severities': [dev.severity for dev in deviations],
            'profile_sample_count': profile.sample_count,
            'profile_date_range': [
                profile.date_range[0].isoformat(),
                profile.date_range[1].isoformat()
            ]
        }
        
        return verdict, total_confidence, reasoning, evidence
    
    def _extract_naming_patterns(self, filenames: List[str]) -> List[str]:
        """
        Extrae patrones de naming comunes.
        
        Estrategia:
        1. Buscar fechas ISO (YYYY-MM-DD)
        2. Buscar versiones (_vN, _version_N)
        3. Buscar prefijos/sufijos comunes
        4. Buscar estructuras con guiones/underscores
        """
        patterns = []
        
        # Patrón 1: Fechas ISO
        date_count = sum(1 for f in filenames if re.search(r'\d{4}-\d{2}-\d{2}', f))
        if date_count > len(filenames) * 0.3:  # >30% tienen fechas
            patterns.append(r'\d{4}-\d{2}-\d{2}')
        
        # Patrón 2: Versiones
        version_count = sum(1 for f in filenames if re.search(r'_v\d+|_version_\d+', f, re.I))
        if version_count > len(filenames) * 0.3:
            patterns.append(r'_v\d+|_version_\d+')
        
        # Patrón 3: Prefijos comunes
        prefixes = defaultdict(int)
        for f in filenames:
            # Dividir por _ o -
            parts = re.split(r'[_\-\s]', f)
            if parts:
                prefix = parts[0].lower()
                prefixes[prefix] += 1
        
        if prefixes:
            most_common_prefix = max(prefixes.items(), key=lambda x: x[1])
            if most_common_prefix[1] > len(filenames) * 0.5:  # >50%
                patterns.append(f"^{re.escape(most_common_prefix[0])}")
        
        # Patrón 4: Estructura con underscores
        underscore_count = sum(1 for f in filenames if '_' in f)
        if underscore_count > len(filenames) * 0.7:  # >70%
            patterns.append(r'.*_.*')  # Contiene al menos un underscore
        
        return patterns
    
    def _matches_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Verifica si filename matchea algún patrón."""
        return any(re.search(p, filename, re.I) for p in patterns)
    
    def _measure_pattern_consistency(
        self,
        filenames: List[str],
        patterns: List[str]
    ) -> Fraction:
        """Mide qué % de archivos históricos siguen los patrones."""
        if not filenames:
            return Fraction(0)
        
        matches = sum(1 for f in filenames if self._matches_patterns(f, patterns))
        return Fraction(matches, len(filenames))
    
    def _find_typical_hours(self, timestamps: List[datetime]) -> List[int]:
        """
        Encuentra horario típico (hours que cubren 80% de actividad).
        
        Returns:
            Lista de horas (0-23) ordenadas
        """
        if not timestamps:
            return list(range(9, 18))  # Default: 9am-5pm
        
        hours = [ts.hour for ts in timestamps]
        counts = Counter(hours)
        total = sum(counts.values())
        threshold = total * 0.8
        
        # Ordenar por frecuencia
        sorted_hours = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        typical = []
        cumsum = 0
        for hour, count in sorted_hours:
            typical.append(hour)
            cumsum += count
            if cumsum >= threshold:
                break
        
        return sorted(typical)
    
    def _measure_hour_consistency(
        self,
        timestamps: List[datetime],
        typical_hours: List[int]
    ) -> Fraction:
        """Mide qué % de actividad ocurre en horario típico."""
        if not timestamps:
            return Fraction(0)
        
        in_range = sum(1 for ts in timestamps if ts.hour in typical_hours)
        return Fraction(in_range, len(timestamps))
    
    def _calculate_diversity(self, counts: Dict[str, int]) -> Fraction:
        """
        Calcula diversidad de software (índice de Shannon).
        
        0 = siempre el mismo software
        1 = máxima diversidad
        """
        if not counts:
            return Fraction(0)
        
        total = sum(counts.values())
        
        # Shannon diversity index normalizado
        import math
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log(p)
        
        # Normalizar a [0, 1]
        max_entropy = math.log(len(counts))
        if max_entropy > 0:
            normalized = entropy / max_entropy
        else:
            normalized = 0.0
        
        return Fraction(int(normalized * 1000), 1000)
    
    def _tokenize_content(self, content: str) -> Set[str]:
        """Tokeniza contenido en palabras únicas (lowercase)."""
        # Remover puntuación y convertir a lowercase
        words = re.findall(r'\b\w{3,}\b', content.lower())  # Palabras de 3+ letras
        
        # Filtrar stopwords comunes (simplificado)
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'has'}
        
        return set(w for w in words if w not in stopwords)


# =============================================================================
# INTEGRACIÓN CON VIGÍA
# =============================================================================

if __name__ == '__main__':
    import sys
    from datetime import datetime, timedelta
    
    # Test de ejemplo
    print("="*70)
    print("BEHAVIORAL FINGERPRINT ANALYZER - TEST")
    print("="*70)
    
    # Simular perfil histórico de CFO
    historical = []
    for i in range(50):
        historical.append({
            'filename': f'Financial_Report_2024-Q{(i%4)+1}_v{i+1}.pdf',
            'timestamp': datetime(2024, (i%12)+1, 15, 14, 30),  # Siempre 14:30
            'software_used': 'Adobe Acrobat DC',
            'content': 'revenue ebitda forecast approved financial quarter budget',
            'file_size': 450000 + (i * 1000),
            'file_type': 'pdf'
        })
    
    # Crear analizador y aprender perfil
    analyzer = BehavioralFingerprintAnalyzer()
    profile = analyzer.learn_profile('cfo@company.com', historical)
    
    print(f"\nProfile learned for: {profile.user_id}")
    print(f"Sample count: {profile.sample_count}")
    print(f"Naming patterns: {profile.naming_patterns}")
    print(f"Typical hours: {profile.typical_hours}")
    print(f"Typical software: {list(profile.typical_software.keys())}")
    print(f"Vocabulary size: {profile.vocabulary_size}")
    
    # Analizar email sospechoso
    suspicious = {
        'filename': 'urgent_payment.pdf',
        'timestamp': datetime(2025, 1, 20, 3, 47),  # 3:47 AM (sospechoso)
        'software_used': 'PDFtk Server',  # Nunca usado
        'content': 'wire transfer urgent payment please send money account',  # Vocabulario distinto
        'file_size': 85000,  # Mucho más pequeño
        'file_type': 'pdf'
    }
    
    result = analyzer.analyze_deviation('cfo@company.com', suspicious)
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS RESULT")
    print(f"{'='*70}")
    print(f"Artifact: {result.artifact_analyzed}")
    print(f"Deviations found: {len(result.deviations)}")
    
    for dev in result.deviations:
        print(f"\n  [{dev.severity}] {dev.category.upper()}")
        print(f"  Confidence: {int(dev.confidence * 100)}%")
        print(f"  {dev.description}")
    
    print(f"\n{'='*70}")
    print(f"VERDICT: {result.verdict}")
    print(f"CONFIDENCE: {int(result.confidence * 100)}%")
    print(f"{'='*70}")
    print(f"\nREASONING:\n{result.reasoning}")
    print(f"\nEVIDENCE:\n{result.evidence}")
    print(f"{'='*70}\n")
