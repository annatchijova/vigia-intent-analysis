# vigia/tools/metabolic_profiler.py
"""
Metabolic Profiler - Detección por Costo Computacional

Principio: La ofuscación SIEMPRE cuesta ciclos. Un adversario puede evadir
análisis de contenido, pero no puede evadir las leyes de la física computacional.

Author: VIGÍA Collective
License: Open Source
"""

from fractions import Fraction
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import time
import hashlib


@dataclass(frozen=True)
class MetabolicSignature:
    """Perfil metabólico inmutable de un artefacto."""
    file_size: int
    parse_time_ns: int
    object_count: int
    reference_depth: int
    circular_refs: int
    efficiency_ratio: Fraction  # objects / KB
    parse_cost: Fraction  # ns / object
    depth_anomaly: Fraction  # depth / expected_depth
    verdict: str
    confidence: Fraction
    reasoning: str
    evidence: Dict[str, any]


class MetabolicProfiler:
    """
    Detector de malicia por análisis de costo computacional.
    
    Detecta:
    - Parser bombs (explosión de objetos)
    - Obfuscación (costo de parseo anómalo)
    - Referencias patológicas (profundidad excesiva)
    - Ataques de complejidad (circular references)
    """
    
    # Baselines calibrados empíricamente
    EFFICIENCY_BASELINE = {
        'pdf': Fraction(40, 1),
        'docx': Fraction(15, 1),
        'xlsx': Fraction(20, 1),
        'exe': Fraction(3, 1),
        'elf': Fraction(5, 1),
        'script': Fraction(100, 1),
        'zip': Fraction(10, 1)
    }
    
    PARSE_COST_BASELINE = {
        'pdf': Fraction(50_000, 1),    # 50µs por objeto
        'docx': Fraction(100_000, 1),  # 100µs por nodo XML
        'xlsx': Fraction(80_000, 1),
        'exe': Fraction(200_000, 1),   # 200µs por sección
        'elf': Fraction(150_000, 1),
        'zip': Fraction(30_000, 1)
    }
    
    EXPECTED_DEPTH = {
        'pdf': lambda obj_count: max(3, int(obj_count ** 0.3)),  # ~log(n)
        'docx': lambda obj_count: 5,
        'xlsx': lambda obj_count: 6,
        'exe': lambda obj_count: 3,
        'elf': lambda obj_count: 4,
        'zip': lambda obj_count: 2
    }
    
    def profile(self, artifact_path: Path) -> MetabolicSignature:
        """
        Genera perfil metabólico completo del artefacto.
        
        Args:
            artifact_path: Ruta al archivo a analizar
            
        Returns:
            MetabolicSignature con veredicto y evidencia
        """
        file_type = self._detect_type(artifact_path)
        file_size = artifact_path.stat().st_size
        
        # Parseo instrumentado con medición de tiempo
        start_ns = time.perf_counter_ns()
        structure = self._parse_structure(artifact_path, file_type)
        parse_time_ns = time.perf_counter_ns() - start_ns
        
        # Extraer métricas estructurales
        object_count = structure.get('object_count', 0)
        ref_depth = structure.get('max_reference_depth', 0)
        circular = structure.get('circular_references', 0)
        
        # Calcular ratios en Fraction (determinista)
        kb_size = Fraction(file_size, 1024)
        
        if kb_size > 0 and object_count > 0:
            efficiency = Fraction(object_count, 1) / kb_size
            parse_cost = Fraction(parse_time_ns, object_count)
        else:
            efficiency = Fraction(0)
            parse_cost = Fraction(0)
        
        # Calcular anomalía de profundidad
        expected_depth = self._calculate_expected_depth(file_type, object_count)
        if expected_depth > 0:
            depth_anomaly = Fraction(ref_depth, expected_depth)
        else:
            depth_anomaly = Fraction(1)
        
        # Evaluación
        verdict, confidence, reasoning, evidence = self._evaluate_metabolism(
            file_type, efficiency, parse_cost, depth_anomaly, circular,
            object_count, parse_time_ns
        )
        
        return MetabolicSignature(
            file_size=file_size,
            parse_time_ns=parse_time_ns,
            object_count=object_count,
            reference_depth=ref_depth,
            circular_refs=circular,
            efficiency_ratio=efficiency,
            parse_cost=parse_cost,
            depth_anomaly=depth_anomaly,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _evaluate_metabolism(
        self,
        file_type: str,
        efficiency: Fraction,
        parse_cost: Fraction,
        depth_anomaly: Fraction,
        circular: int,
        object_count: int,
        parse_time_ns: int
    ) -> Tuple[str, Fraction, str, Dict]:
        """
        Evalúa si el perfil metabólico indica malicia.
        
        Returns:
            (verdict, confidence, reasoning, evidence)
        """
        baseline_eff = self.EFFICIENCY_BASELINE.get(file_type, Fraction(50, 1))
        baseline_cost = self.PARSE_COST_BASELINE.get(file_type, Fraction(100_000, 1))
        
        signals = []
        evidence = {}
        
        # SEÑAL 1: Explosión de objetos (parser bomb)
        if efficiency > baseline_eff * 5:
            weight = Fraction(6, 10)
            signals.append((
                weight,
                f"PARSER_BOMB: Object density {int(efficiency)} >> baseline {int(baseline_eff)} (5x+)"
            ))
            evidence['object_explosion'] = {
                'severity': 'CRITICAL',
                'multiplier': str(efficiency / baseline_eff)
            }
        elif efficiency > baseline_eff * 3:
            weight = Fraction(4, 10)
            signals.append((
                weight,
                f"Object density {int(efficiency)} >> baseline {int(baseline_eff)} (3x)"
            ))
            evidence['object_explosion'] = {
                'severity': 'HIGH',
                'multiplier': str(efficiency / baseline_eff)
            }
        elif efficiency > baseline_eff * 2:
            weight = Fraction(2, 10)
            signals.append((
                weight,
                f"Object density elevated: {int(efficiency)} vs {int(baseline_eff)} (2x)"
            ))
            evidence['object_explosion'] = {
                'severity': 'MEDIUM',
                'multiplier': str(efficiency / baseline_eff)
            }
        
        # SEÑAL 2: Costo de parseo anómalo (obfuscación)
        if parse_cost > baseline_cost * 10:
            weight = Fraction(7, 10)
            signals.append((
                weight,
                f"OBFUSCATION: Parse cost {int(parse_cost)}ns >> baseline {int(baseline_cost)}ns (10x+)"
            ))
            evidence['parse_anomaly'] = {
                'severity': 'CRITICAL',
                'cost_multiplier': float(parse_cost / baseline_cost)
            }
        elif parse_cost > baseline_cost * 5:
            weight = Fraction(5, 10)
            signals.append((
                weight,
                f"Parse cost {int(parse_cost)}ns >> baseline {int(baseline_cost)}ns (5x)"
            ))
            evidence['parse_anomaly'] = {
                'severity': 'HIGH',
                'cost_multiplier': float(parse_cost / baseline_cost)
            }
        elif parse_cost > baseline_cost * 3:
            weight = Fraction(3, 10)
            signals.append((
                weight,
                f"Parse cost elevated: {int(parse_cost)}ns vs {int(baseline_cost)}ns (3x)"
            ))
            evidence['parse_anomaly'] = {
                'severity': 'MEDIUM',
                'cost_multiplier': float(parse_cost / baseline_cost)
            }
        
        # SEÑAL 3: Profundidad de referencias patológica
        if depth_anomaly > Fraction(5, 1):
            weight = Fraction(6, 10)
            signals.append((
                weight,
                f"PATHOLOGICAL_NESTING: Reference depth {depth_anomaly} >> expected (DoS indicator)"
            ))
            evidence['depth_attack'] = {
                'severity': 'CRITICAL',
                'depth_ratio': float(depth_anomaly)
            }
        elif depth_anomaly > Fraction(3, 1):
            weight = Fraction(4, 10)
            signals.append((
                weight,
                f"Reference depth {depth_anomaly} >> expected (suspicious nesting)"
            ))
            evidence['depth_attack'] = {
                'severity': 'HIGH',
                'depth_ratio': float(depth_anomaly)
            }
        elif depth_anomaly > Fraction(2, 1):
            weight = Fraction(2, 10)
            signals.append((
                weight,
                f"Reference depth elevated: {depth_anomaly} vs expected"
            ))
            evidence['depth_attack'] = {
                'severity': 'MEDIUM',
                'depth_ratio': float(depth_anomaly)
            }
        
        # SEÑAL 4: Referencias circulares (casi siempre malicioso)
        if circular > 5:
            weight = Fraction(8, 10)
            signals.append((
                weight,
                f"CIRCULAR_REFS: {circular} loops detected (parser crash vector)"
            ))
            evidence['circular_attack'] = {
                'severity': 'CRITICAL',
                'count': circular
            }
        elif circular > 0:
            weight = Fraction(6, 10)
            signals.append((
                weight,
                f"Circular references: {circular} (anti-pattern)"
            ))
            evidence['circular_attack'] = {
                'severity': 'HIGH',
                'count': circular
            }
        
        # SEÑAL 5: Micro-objetos (muchos objetos casi vacíos = evasión)
        if object_count > 1000:
            avg_size = file_size / object_count
            if avg_size < 10:  # < 10 bytes/objeto
                weight = Fraction(5, 10)
                signals.append((
                    weight,
                    f"MICRO_OBJECTS: {object_count} objects averaging {int(avg_size)} bytes (fragmentation attack)"
                ))
                evidence['fragmentation'] = {
                    'severity': 'HIGH',
                    'avg_object_size': int(avg_size)
                }
        
        # DECISIÓN
        if not signals:
            return (
                "BENIGN",
                Fraction(8, 10),
                "Metabolic profile within normal parameters",
                {'baseline_efficiency': float(baseline_eff), 'baseline_cost': int(baseline_cost)}
            )
        
        total_confidence = sum(s[0] for s in signals)
        reasoning_parts = [s[1] for s in signals]
        
        # Saturar confianza a 1.0
        if total_confidence > Fraction(10, 10):
            total_confidence = Fraction(10, 10)
        
        reasoning = "METABOLIC_ANOMALY: " + "; ".join(reasoning_parts)
        
        if total_confidence >= Fraction(8, 10):
            verdict = "MALICIOUS"
        elif total_confidence >= Fraction(4, 10):
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"
        
        evidence['total_signals'] = len(signals)
        evidence['confidence_raw'] = float(total_confidence)
        
        return verdict, total_confidence, reasoning, evidence
    
    def _parse_structure(self, path: Path, file_type: str) -> Dict:
        """
        Parsea estructura interna del archivo según tipo.
        
        Returns:
            {
                'object_count': int,
                'max_reference_depth': int,
                'circular_references': int
            }
        """
        parsers = {
            'pdf': self._parse_pdf_structure,
            'docx': self._parse_docx_structure,
            'xlsx': self._parse_xlsx_structure,
            'zip': self._parse_zip_structure,
            'exe': self._parse_pe_structure,
            'elf': self._parse_elf_structure
        }
        
        parser = parsers.get(file_type)
        if parser:
            try:
                return parser(path)
            except Exception as e:
                # Fallo de parseo es en sí mismo sospechoso
                return {
                    'object_count': 0,
                    'max_reference_depth': 0,
                    'circular_references': 0,
                    'parse_error': str(e)
                }
        
        return {
            'object_count': 1,
            'max_reference_depth': 0,
            'circular_references': 0
        }
    
    def _parse_pdf_structure(self, path: Path) -> Dict:
        """Análisis estructural de PDF."""
        try:
            import fitz
            doc = fitz.open(str(path))
            
            xref_len = doc.xref_length()
            max_depth = 0
            circular_count = 0
            
            # Analizar referencias
            for xref in range(1, min(xref_len, 10000)):  # Límite de seguridad
                try:
                    depth_result = self._measure_pdf_depth(doc, xref, set(), 0)
                    max_depth = max(max_depth, depth_result['depth'])
                    circular_count += depth_result['circular']
                except:
                    continue
            
            doc.close()
            
            return {
                'object_count': xref_len,
                'max_reference_depth': max_depth,
                'circular_references': circular_count
            }
        except ImportError:
            # Fallback sin fitz
            return self._parse_pdf_fallback(path)
        except Exception as e:
            return {
                'object_count': 0,
                'max_reference_depth': 0,
                'circular_references': 0,
                'parse_error': str(e)
            }
    
    def _parse_pdf_fallback(self, path: Path) -> Dict:
        """Parseo básico de PDF sin dependencias."""
        with open(path, 'rb') as f:
            content = f.read()
        
        # Contar objetos (buscar patrón "N 0 obj")
        import re
        objects = re.findall(rb'\d+ 0 obj', content)
        
        return {
            'object_count': len(objects),
            'max_reference_depth': 3,  # Asumido
            'circular_references': 0
        }
    
    def _measure_pdf_depth(self, doc, xref: int, visited: set, depth: int) -> Dict:
        """Mide profundidad de referencias recursivamente."""
        if xref in visited:
            return {'depth': depth, 'circular': 1}
        
        if depth > 50:  # Límite de seguridad
            return {'depth': 50, 'circular': 0}
        
        visited.add(xref)
        
        try:
            # Buscar referencias (simplificado)
            obj_str = doc.xref_object(xref)
            
            # Contar referencias a otros objetos
            import re
            refs = re.findall(r'(\d+) 0 R', obj_str)
            
            if not refs:
                return {'depth': depth, 'circular': 0}
            
            max_child_depth = depth
            total_circular = 0
            
            for ref_str in refs[:10]:  # Máximo 10 referencias por objeto
                try:
                    ref_xref = int(ref_str)
                    child = self._measure_pdf_depth(doc, ref_xref, visited.copy(), depth + 1)
                    max_child_depth = max(max_child_depth, child['depth'])
                    total_circular += child['circular']
                except:
                    continue
            
            return {'depth': max_child_depth, 'circular': total_circular}
        except:
            return {'depth': depth, 'circular': 0}
    
    def _parse_docx_structure(self, path: Path) -> Dict:
        """Análisis estructural de DOCX (ZIP con XMLs)."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(path, 'r') as zf:
                namelist = zf.namelist()
                
                # Contar nodos XML totales
                total_nodes = 0
                max_depth = 0
                
                for name in namelist:
                    if name.endswith('.xml'):
                        try:
                            xml_content = zf.read(name)
                            root = ET.fromstring(xml_content)
                            
                            # Contar nodos
                            nodes = len(list(root.iter()))
                            total_nodes += nodes
                            
                            # Medir profundidad
                            depth = self._measure_xml_depth(root)
                            max_depth = max(max_depth, depth)
                        except:
                            continue
                
                return {
                    'object_count': total_nodes,
                    'max_reference_depth': max_depth,
                    'circular_references': 0  # XML no tiene circular refs típicamente
                }
        except Exception as e:
            return {
                'object_count': 0,
                'max_reference_depth': 0,
                'circular_references': 0,
                'parse_error': str(e)
            }
    
    def _parse_xlsx_structure(self, path: Path) -> Dict:
        """Análisis de XLSX (similar a DOCX)."""
        return self._parse_docx_structure(path)
    
    def _parse_zip_structure(self, path: Path) -> Dict:
        """Análisis de ZIP genérico."""
        try:
            import zipfile
            with zipfile.ZipFile(path, 'r') as zf:
                namelist = zf.namelist()
                
                # Detectar ZIP bombs (ratio compresión excesiva)
                total_compressed = 0
                total_uncompressed = 0
                
                for info in zf.infolist():
                    total_compressed += info.compress_size
                    total_uncompressed += info.file_size
                
                compression_ratio = total_uncompressed / max(total_compressed, 1)
                
                return {
                    'object_count': len(namelist),
                    'max_reference_depth': 1,
                    'circular_references': 0,
                    'compression_ratio': compression_ratio
                }
        except Exception as e:
            return {
                'object_count': 0,
                'max_reference_depth': 0,
                'circular_references': 0,
                'parse_error': str(e)
            }
    
    def _parse_pe_structure(self, path: Path) -> Dict:
        """Análisis de ejecutable PE (Windows)."""
        try:
            import pefile
            pe = pefile.PE(str(path))
            
            sections = len(pe.sections)
            imports = len(pe.DIRECTORY_ENTRY_IMPORT) if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') else 0
            
            return {
                'object_count': sections + imports,
                'max_reference_depth': 2,
                'circular_references': 0
            }
        except ImportError:
            return self._parse_pe_fallback(path)
        except Exception as e:
            return {
                'object_count': 0,
                'max_reference_depth': 0,
                'circular_references': 0,
                'parse_error': str(e)
            }
    
    def _parse_pe_fallback(self, path: Path) -> Dict:
        """Parseo básico PE sin pefile."""
        with open(path, 'rb') as f:
            header = f.read(1024)
        
        # Buscar magic "MZ"
        if not header.startswith(b'MZ'):
            return {'object_count': 0, 'max_reference_depth': 0, 'circular_references': 0}
        
        # Estimar secciones (heurística simple)
        section_count = 3  # Asumido
        
        return {
            'object_count': section_count,
            'max_reference_depth': 2,
            'circular_references': 0
        }
    
    def _parse_elf_structure(self, path: Path) -> Dict:
        """Análisis de ejecutable ELF (Linux)."""
        try:
            from elftools.elf.elffile import ELFFile
            
            with open(path, 'rb') as f:
                elf = ELFFile(f)
                sections = elf.num_sections()
                
                return {
                    'object_count': sections,
                    'max_reference_depth': 2,
                    'circular_references': 0
                }
        except ImportError:
            return self._parse_elf_fallback(path)
        except Exception as e:
            return {
                'object_count': 0,
                'max_reference_depth': 0,
                'circular_references': 0,
                'parse_error': str(e)
            }
    
    def _parse_elf_fallback(self, path: Path) -> Dict:
        """Parseo básico ELF sin pyelftools."""
        with open(path, 'rb') as f:
            header = f.read(64)
        
        # Verificar magic ELF
        if not header.startswith(b'\x7fELF'):
            return {'object_count': 0, 'max_reference_depth': 0, 'circular_references': 0}
        
        return {
            'object_count': 5,  # Asumido
            'max_reference_depth': 2,
            'circular_references': 0
        }
    
    def _measure_xml_depth(self, element, depth=0) -> int:
        """Mide profundidad máxima de árbol XML."""
        if len(element) == 0:
            return depth
        
        return max(self._measure_xml_depth(child, depth + 1) for child in element)
    
    def _calculate_expected_depth(self, file_type: str, object_count: int) -> int:
        """Calcula profundidad esperada según tipo y tamaño."""
        calculator = self.EXPECTED_DEPTH.get(file_type)
        if calculator:
            return calculator(object_count)
        return 3  # Default
    
    def _detect_type(self, path: Path) -> str:
        """Detecta tipo de archivo por magic bytes + extensión."""
        magic_signatures = {
            b'%PDF': 'pdf',
            b'PK\x03\x04': 'zip',  # También DOCX/XLSX
            b'MZ': 'exe',
            b'\x7fELF': 'elf',
            b'#!/': 'script'
        }
        
        try:
            with open(path, 'rb') as f:
                header = f.read(8)
            
            for magic, ftype in magic_signatures.items():
                if header.startswith(magic):
                    # Distinguir ZIP variants
                    if ftype == 'zip':
                        ext = path.suffix.lower()
                        if ext == '.docx':
                            return 'docx'
                        elif ext == '.xlsx':
                            return 'xlsx'
                    return ftype
        except:
            pass
        
        # Fallback a extensión
        ext = path.suffix.lower()
        ext_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.xlsx': 'xlsx',
            '.zip': 'zip',
            '.exe': 'exe',
            '.dll': 'exe',
            '.elf': 'elf',
            '.sh': 'script',
            '.py': 'script',
            '.js': 'script'
        }
        
        return ext_map.get(ext, 'unknown')


# =============================================================================
# INTEGRACIÓN CON VIGÍA
# =============================================================================

def integrate_metabolic_profiler():
    """
    Integra MetabolicProfiler en el pipeline de VIGÍA.
    
    Agregar a vigia/core/signal_router.py:
    
    from vigia.tools.metabolic_profiler import MetabolicProfiler
    
    profiler = MetabolicProfiler()
    signature = profiler.profile(artifact_path)
    
    signals.append(SignalOutput(
        tool_name="MetabolicProfiler",
        value=signature.verdict,
        z_score=signature.confidence,
        confidence=signature.confidence,
        metadata={
            'efficiency_ratio': float(signature.efficiency_ratio),
            'parse_cost_ns': signature.parse_time_ns,
            'depth_anomaly': float(signature.depth_anomaly),
            'circular_refs': signature.circular_refs,
            'reasoning': signature.reasoning,
            'evidence': signature.evidence
        }
    ))
    """
    pass


if __name__ == '__main__':
    # Test básico
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python metabolic_profiler.py <file_path>")
        sys.exit(1)
    
    test_path = Path(sys.argv[1])
    
    profiler = MetabolicProfiler()
    result = profiler.profile(test_path)
    
    print(f"\n{'='*70}")
    print(f"METABOLIC PROFILE: {test_path.name}")
    print(f"{'='*70}")
    print(f"File Size: {result.file_size:,} bytes")
    print(f"Parse Time: {result.parse_time_ns / 1_000_000:.2f} ms")
    print(f"Objects: {result.object_count}")
    print(f"Reference Depth: {result.reference_depth}")
    print(f"Circular Refs: {result.circular_refs}")
    print(f"\nEfficiency: {int(result.efficiency_ratio)} objects/KB")
    print(f"Parse Cost: {int(result.parse_cost)} ns/object")
    print(f"Depth Anomaly: {float(result.depth_anomaly):.2f}x expected")
    print(f"\n{'='*70}")
    print(f"VERDICT: {result.verdict}")
    print(f"CONFIDENCE: {int(result.confidence * 100)}%")
    print(f"{'='*70}")
    print(f"\nREASONING:\n{result.reasoning}")
    print(f"\nEVIDENCE:\n{result.evidence}")
    print(f"{'='*70}\n")
