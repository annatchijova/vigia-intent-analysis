# vigia/core/advanced_signal_router.py
"""

Integra:
1. MetabolicProfiler
2. EntropyLocalityAnalyzer
3. TemporalDriftDetector
4. BehavioralFingerprintAnalyzer
5. CrossArtifactResonanceAnalyzer
"""

from pathlib import Path
from typing import List
from fractions import Fraction

from vigia.tools.metabolic_profiler import MetabolicProfiler
from vigia.tools.entropy_locality import EntropyLocalityAnalyzer
from vigia.tools.temporal_drift import TemporalDriftDetector, TimestampExtractor
from vigia.tools.behavioral_fingerprint import BehavioralFingerprintAnalyzer
from vigia.tools.cross_artifact_resonance import CrossArtifactResonanceAnalyzer

from vigia.core.signal_output import SignalOutput


class AdvancedSignalRouter:
    """Router con análisis avanzados."""
    
    def __init__(self):
        self.metabolic = MetabolicProfiler()
        self.entropy = EntropyLocalityAnalyzer()
        self.temporal = TemporalDriftDetector()
        self.behavioral = BehavioralFingerprintAnalyzer()
        self.resonance = CrossArtifactResonanceAnalyzer()
    
    def route_advanced(self, artifact_path: Path, context: dict = None) -> List[SignalOutput]:
        """
        Ejecuta análisis avanzados y retorna señales.
        
        Args:
            artifact_path: Ruta al artefacto
            context: Contexto adicional (usuario, artefactos relacionados, etc)
        
        Returns:
            Lista de SignalOutput
        """
        signals = []
        
        # ANÁLISIS 1: Metabolic Profiling
        try:
            metabolic_sig = self.metabolic.profile(artifact_path)
            signals.append(SignalOutput(
                tool_name="MetabolicProfiler",
                value=metabolic_sig.verdict,
                z_score=metabolic_sig.confidence,
                confidence=metabolic_sig.confidence,
                metadata={
                    'efficiency_ratio': float(metabolic_sig.efficiency_ratio),
                    'parse_cost_ns': metabolic_sig.parse_time_ns,
                    'depth_anomaly': float(metabolic_sig.depth_anomaly),
                    'circular_refs': metabolic_sig.circular_refs,
                    'reasoning': metabolic_sig.reasoning,
                    'evidence': metabolic_sig.evidence
                }
            ))
        except Exception as e:
            signals.append(SignalOutput(
                tool_name="MetabolicProfiler",
                value="ERROR",
                z_score=Fraction(0),
                confidence=Fraction(0),
                metadata={'error': str(e)}
            ))
        
        # ANÁLISIS 2: Entropy Locality
        try:
            with open(artifact_path, 'rb') as f:
                data = f.read()
            
            entropy_profile = self.entropy.analyze(data)
            signals.append(SignalOutput(
                tool_name="EntropyLocality",
                value=entropy_profile.verdict,
                z_score=entropy_profile.confidence,
                confidence=entropy_profile.confidence,
                metadata={
                    'global_entropy': float(entropy_profile.global_entropy),
                    'locality_score': float(entropy_profile.locality_score),
                    'cluster_count': len(entropy_profile.high_entropy_clusters),
                    'reasoning': entropy_profile.reasoning,
                    'evidence': entropy_profile.evidence
                }
            ))
        except Exception as e:
            signals.append(SignalOutput(
                tool_name="EntropyLocality",
                value="ERROR",
                z_score=Fraction(0),
                confidence=Fraction(0),
                metadata={'error': str(e)}
            ))
        
        # ANÁLISIS 3: Temporal Drift
        try:
            # Extraer eventos temporales según tipo de archivo
            if artifact_path.suffix.lower() == '.pdf':
                events = TimestampExtractor.extract_from_pdf(artifact_path)
            elif artifact_path.suffix.lower() in ['.eml', '.msg']:
                events = TimestampExtractor.extract_from_email(artifact_path)
            else:
                events = []
            
            if events:
                temporal_analysis = self.temporal.analyze(events)
                signals.append(SignalOutput(
                    tool_name="TemporalDrift",
                    value=temporal_analysis.verdict,
                    z_score=temporal_analysis.confidence,
                    confidence=temporal_analysis.confidence,
                    metadata={
                        'impossible_sequences': len(temporal_analysis.impossible_sequences),
                        'excessive_drifts': len(temporal_analysis.excessive_drifts),
                        'timezone_violations': len(temporal_analysis.timezone_violations),
                        'reasoning': temporal_analysis.reasoning,
                        'evidence': temporal_analysis.evidence
                    }
                ))
        except Exception as e:
            signals.append(SignalOutput(
                tool_name="TemporalDrift",
                value="ERROR",
                z_score=Fraction(0),
                confidence=Fraction(0),
                metadata={'error': str(e)}
            ))
        
        # ANÁLISIS 4: Behavioral Fingerprint (si hay contexto de usuario)
        if context and 'user_id' in context:
            try:
                # Construir artifact dict
                artifact_dict = {
                    'filename': artifact_path.name,
                    'timestamp': context.get('timestamp'),
                    'software_used': context.get('software'),
                    'file_size': artifact_path.stat().st_size,
                    'file_type': artifact_path.suffix.lower()[1:]
                }
                
                # Solo analizar si hay perfil
                if context['user_id'] in self.behavioral.profiles:
                    behavioral_analysis = self.behavioral.analyze_deviation(
                        context['user_id'],
                        artifact_dict
                    )
                    
                    signals.append(SignalOutput(
                        tool_name="BehavioralFingerprint",
                        value=behavioral_analysis.verdict,
                        z_score=behavioral_analysis.confidence,
                        confidence=behavioral_analysis.confidence,
                        metadata={
                            'deviation_count': len(behavioral_analysis.deviations),
                            'reasoning': behavioral_analysis.reasoning,
                            'evidence': behavioral_analysis.evidence
                        }
                    ))
            except Exception as e:
                signals.append(SignalOutput(
                    tool_name="BehavioralFingerprint",
                    value="ERROR",
                    z_score=Fraction(0),
                    confidence=Fraction(0),
                    metadata={'error': str(e)}
                ))
        
        # ANÁLISIS 5: Cross-Artifact Resonance (si hay artefactos relacionados)
        if context and 'related_artifacts' in context:
            try:
                resonance_analysis = self.resonance.analyze(context['related_artifacts'])
                
                signals.append(SignalOutput(
                    tool_name="CrossArtifactResonance",
                    value=resonance_analysis.verdict,
                    z_score=resonance_analysis.confidence,
                    confidence=resonance_analysis.confidence,
                    metadata={
                        'conflict_count': len(resonance_analysis.conflicts_detected),
                        'coherence_score': float(resonance_analysis.coherence_score),
                        'reasoning': resonance_analysis.reasoning,
                        'evidence': resonance_analysis.evidence
                    }
                ))
            except Exception as e:
                signals.append(SignalOutput(
                    tool_name="CrossArtifactResonance",
                    value="ERROR",
                    z_score=Fraction(0),
                    confidence=Fraction(0),
                    metadata={'error': str(e)}
                ))
        
        return signals
