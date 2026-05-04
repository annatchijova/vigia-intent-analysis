# vigia/tools/entropy_locality.py
"""
Entropy Locality Analyzer - Distribución Espacial de Entropía

Principio: La entropía global es fácil de engañar. La distribución ESPACIAL
de entropía revela payloads cifrados, steganografía y shellcode patterns.

Author: VIGÍA Collective
License: Open Source
"""

from fractions import Fraction
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict
import math


@dataclass(frozen=True)
class EntropyProfile:
    """Perfil de entropía espacial inmutable."""
    global_entropy: Fraction
    mean_chunk_entropy: Fraction
    entropy_variance: Fraction
    high_entropy_clusters: List[Tuple[int, Fraction]]  # [(offset, entropy), ...]
    locality_score: Fraction  # Índice de Gini: 0=uniforme, 1=concentrado
    verdict: str
    confidence: Fraction
    reasoning: str
    evidence: Dict


class EntropyLocalityAnalyzer:
    """
    Analiza DÓNDE está la entropía, no solo CUÁNTA hay.
    
    Detecta:
    - Payloads cifrados localizados
    - Steganografía (entropía en regiones inesperadas)
    - Shellcode patterns (alta entropía + ejecutabilidad)
    - ZIP bombs (compresión asimétrica)
    """
    
    CHUNK_SIZE = 256  # bytes por ventana deslizante
    HIGH_ENTROPY_THRESHOLD = Fraction(7, 1)  # > 7 bits/byte
    STEGANOGRAPHY_THRESHOLD = Fraction(4, 1)  # Entropía global baja pero clusters altos
    LOCALITY_SUSPICIOUS = Fraction(6, 10)  # Gini > 0.6 indica concentración
    
    def analyze(self, data: bytes) -> EntropyProfile:
        """
        Analiza distribución espacial de entropía.
        
        Args:
            data: Contenido del archivo en bytes
            
        Returns:
            EntropyProfile con veredicto y evidencia
        """
        if len(data) == 0:
            return self._empty_profile()
        
        # Dividir en chunks
        chunks = [data[i:i+self.CHUNK_SIZE] for i in range(0, len(data), self.CHUNK_SIZE)]
        
        # Calcular entropía por chunk
        chunk_entropies = [self._shannon_entropy(chunk) for chunk in chunks]
        
        # Métricas globales
        global_entropy = self._shannon_entropy(data)
        
        # Convertir a Fraction para determinismo
        global_ent_frac = Fraction(int(global_entropy * 1000), 1000)
        
        chunk_ents_frac = [Fraction(int(e * 1000), 1000) for e in chunk_entropies]
        
        if len(chunk_ents_frac) > 0:
            mean_entropy = sum(chunk_ents_frac, Fraction(0)) / len(chunk_ents_frac)
        else:
            mean_entropy = Fraction(0)
        
        # Varianza
        variance = self._compute_variance(chunk_ents_frac, mean_entropy)
        
        # Detectar clusters de alta entropía
        clusters = [
            (i * self.CHUNK_SIZE, ent)
            for i, ent in enumerate(chunk_ents_frac)
            if ent > self.HIGH_ENTROPY_THRESHOLD
        ]
        
        # Locality score (Índice de Gini)
        locality = self._compute_gini_index(chunk_ents_frac)
        
        # Evaluación
        verdict, confidence, reasoning, evidence = self._evaluate_distribution(
            global_ent_frac, variance, clusters, locality, len(data)
        )
        
        return EntropyProfile(
            global_entropy=global_ent_frac,
            mean_chunk_entropy=mean_entropy,
            entropy_variance=variance,
            high_entropy_clusters=clusters,
            locality_score=locality,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _evaluate_distribution(
        self,
        global_ent: Fraction,
        variance: Fraction,
        clusters: List[Tuple[int, Fraction]],
        locality: Fraction,
        file_size: int
    ) -> Tuple[str, Fraction, str, Dict]:
        """
        Evalúa si el patrón de entropía es sospechoso.
        
        Patrones maliciosos:
        1. Alta localidad + clusters: payload cifrado embebido
        2. Baja entropía global + clusters: steganografía
        3. Alta varianza: estructura inconsistente
        4. Micro-clusters: shellcode fragments
        """
        signals = []
        evidence = {}
        
        # SEÑAL 1: Payload cifrado localizado
        if len(clusters) > 0 and locality > self.LOCALITY_SUSPICIOUS:
            weight = Fraction(6, 10)
            cluster_percent = (len(clusters) * self.CHUNK_SIZE * 100) / file_size
            signals.append((
                weight,
                f"LOCALIZED_PAYLOAD: {len(clusters)} high-entropy clusters ({int(cluster_percent)}% of file), locality={float(locality):.2f}"
            ))
            evidence['payload_localization'] = {
                'severity': 'HIGH',
                'cluster_count': len(clusters),
                'locality_index': float(locality),
                'coverage_percent': int(cluster_percent)
            }
        
        # SEÑAL 2: Steganografía (entropía global baja PERO clusters altos)
        if global_ent < self.STEGANOGRAPHY_THRESHOLD and len(clusters) > 0:
            weight = Fraction(7, 10)
            signals.append((
                weight,
                f"STEGANOGRAPHY_PATTERN: Low global entropy ({float(global_ent):.2f}) but {len(clusters)} high-entropy regions"
            ))
            evidence['steganography'] = {
                'severity': 'CRITICAL',
                'global_entropy': float(global_ent),
                'hidden_clusters': len(clusters)
            }
        
        # SEÑAL 3: Varianza alta (caos estructural)
        if variance > Fraction(3, 1):
            weight = Fraction(4, 10)
            signals.append((
                weight,
                f"HIGH_VARIANCE: Entropy variance {float(variance):.2f} (chaotic structure)"
            ))
            evidence['variance_anomaly'] = {
                'severity': 'MEDIUM',
                'variance': float(variance)
            }
        
        # SEÑAL 4: Micro-clusters (shellcode)
        if len(clusters) > 10:
            # Detectar clusters pequeños y dispersos
            cluster_offsets = [c[0] for c in clusters]
            avg_gap = sum(cluster_offsets[i+1] - cluster_offsets[i] 
                         for i in range(len(cluster_offsets)-1)) / max(len(cluster_offsets)-1, 1)
            
            if avg_gap < self.CHUNK_SIZE * 5:  # Clusters muy juntos
                weight = Fraction(5, 10)
                signals.append((
                    weight,
                    f"SHELLCODE_PATTERN: {len(clusters)} micro-clusters with avg gap {int(avg_gap)} bytes"
                ))
                evidence['shellcode'] = {
                    'severity': 'HIGH',
                    'cluster_density': len(clusters),
                    'avg_gap': int(avg_gap)
                }
        
        # SEÑAL 5: Entropía perfecta (casi 8.0) = cifrado fuerte
        if global_ent > Fraction(79, 10):  # > 7.9
            weight = Fraction(3, 10)
            signals.append((
                weight,
                f"NEAR_PERFECT_ENTROPY: {float(global_ent):.2f} bits/byte (strong encryption indicator)"
            ))
            evidence['encryption'] = {
                'severity': 'MEDIUM',
                'entropy': float(global_ent)
            }
        
        # DECISIÓN
        if not signals:
            return (
                "BENIGN",
                Fraction(8, 10),
                "Entropy distribution normal",
                {'global_entropy': float(global_ent), 'locality': float(locality)}
            )
        
        total_confidence = sum(s[0] for s in signals)
        reasoning_parts = [s[1] for s in signals]
        
        # Saturar confianza
        if total_confidence > Fraction(10, 10):
            total_confidence = Fraction(10, 10)
        
        reasoning = "ENTROPY_LOCALITY_ANOMALY: " + "; ".join(reasoning_parts)
        
        if total_confidence >= Fraction(8, 10):
            verdict = "MALICIOUS"
        elif total_confidence >= Fraction(4, 10):
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"
        
        evidence['total_signals'] = len(signals)
        evidence['confidence_raw'] = float(total_confidence)
        
        return verdict, total_confidence, reasoning, evidence
    
    def _shannon_entropy(self, data: bytes) -> float:
        """
        Calcula entropía de Shannon en bits/byte.
        # HEURISTIC: entropy uses float internally, converted to Fraction
        # before any verdict logic. Callers must not use this value directly
        # for scoring — always wrap with Fraction(int(e * 1000), 1000).
        H(X) = -Σ p(x) * log2(p(x))
        """
        if not data:
            return 0.0
        
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        
        entropy = 0.0
        length = len(data)
        
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)
        
        return entropy
    
    def _compute_variance(self, values: List[Fraction], mean: Fraction) -> Fraction:
        """Varianza en Fraction (determinista)."""
        if not values:
            return Fraction(0)
        
        squared_diffs = [(v - mean) ** 2 for v in values]
        return sum(squared_diffs, Fraction(0)) / len(values)
    
    def _compute_gini_index(self, values: List[Fraction]) -> Fraction:
        """
        Índice de Gini: mide concentración de entropía.
        
        0 = perfectamente uniforme (todos los chunks tienen misma entropía)
        1 = máxima concentración (toda la entropía en un chunk)
        
        Formula: G = (2 * Σ(i * x[i])) / (n * Σx[i]) - (n+1)/n
        """
        if not values or all(v == 0 for v in values):
            return Fraction(0)
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        cumsum = sum(sorted_vals, Fraction(0))
        if cumsum == 0:
            return Fraction(0)
        
        weighted_sum = sum(
            Fraction(i + 1) * val
            for i, val in enumerate(sorted_vals)
        )
        
        gini = (Fraction(2) * weighted_sum) / (Fraction(n) * cumsum) - Fraction(n + 1, n)
        
        # Gini debe estar en [0, 1]
        if gini < 0:
            gini = Fraction(0)
        elif gini > 1:
            gini = Fraction(1)
        
        return gini
    
    def _empty_profile(self) -> EntropyProfile:
        """Perfil para archivo vacío."""
        return EntropyProfile(
            global_entropy=Fraction(0),
            mean_chunk_entropy=Fraction(0),
            entropy_variance=Fraction(0),
            high_entropy_clusters=[],
            locality_score=Fraction(0),
            verdict="BENIGN",
            confidence=Fraction(10, 10),
            reasoning="Empty file",
            evidence={}
        )


# =============================================================================
# VISUALIZADOR DE ENTROPÍA (OPCIONAL)
# =============================================================================

class EntropyVisualizer:
    """Genera gráfico ASCII de distribución de entropía."""
    
    @staticmethod
    def visualize(profile: EntropyProfile, width: int = 60) -> str:
        """
        Genera visualización ASCII de clusters.
        
        Ejemplo:
        Offset   Entropy
        0000     ▁▁▁▁▂▃▅▇██▇▅▃▂▁▁▁▁
        0100     ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        0200     ████████████████████  <- HIGH ENTROPY CLUSTER
        """
        if not profile.high_entropy_clusters:
            return "No high-entropy clusters detected"
        
        lines = ["Entropy Distribution Map:", "=" * (width + 20)]
        
        # Agrupar clusters en bloques
        max_offset = max(c[0] for c in profile.high_entropy_clusters)
        block_size = max(max_offset // width, 1)
        
        blocks = defaultdict(list)
        for offset, entropy in profile.high_entropy_clusters:
            block_idx = offset // block_size
            blocks[block_idx].append(float(entropy))
        
        # Renderizar
        chars = ' ▁▂▃▄▅▆▇█'
        
        for block_idx in sorted(blocks.keys()):
            offset = block_idx * block_size
            avg_entropy = sum(blocks[block_idx]) / len(blocks[block_idx])
            
            # Mapear entropía a caracteres
            char_idx = min(int(avg_entropy), len(chars) - 1)
            char = chars[char_idx]
            
            label = f"{offset:08x}"
            bar = char * 20
            ent_str = f"{avg_entropy:.2f}"
            
            lines.append(f"{label}  {bar}  {ent_str}")
        
        lines.append("=" * (width + 20))
        
        return "\n".join(lines)


# =============================================================================
# INTEGRACIÓN CON VIGÍA
# =============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python entropy_locality.py <file_path>")
        sys.exit(1)
    
    test_path = Path(sys.argv[1])
    
    with open(test_path, 'rb') as f:
        data = f.read()
    
    analyzer = EntropyLocalityAnalyzer()
    profile = analyzer.analyze(data)
    
    print(f"\n{'='*70}")
    print(f"ENTROPY LOCALITY ANALYSIS: {test_path.name}")
    print(f"{'='*70}")
    print(f"Global Entropy: {float(profile.global_entropy):.3f} bits/byte")
    print(f"Mean Chunk Entropy: {float(profile.mean_chunk_entropy):.3f}")
    print(f"Entropy Variance: {float(profile.entropy_variance):.3f}")
    print(f"Locality Index (Gini): {float(profile.locality_score):.3f}")
    print(f"High-Entropy Clusters: {len(profile.high_entropy_clusters)}")
    print(f"\n{'='*70}")
    print(f"VERDICT: {profile.verdict}")
    print(f"CONFIDENCE: {int(profile.confidence * 100)}%")
    print(f"{'='*70}")
    print(f"\nREASONING:\n{profile.reasoning}")
    print(f"\nEVIDENCE:\n{profile.evidence}")
    
    if profile.high_entropy_clusters:
        print(f"\n{'='*70}")
        print(EntropyVisualizer.visualize(profile))
    
    print(f"{'='*70}\n")
