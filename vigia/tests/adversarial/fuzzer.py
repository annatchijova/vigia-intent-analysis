# vigia/tests/adversarial/fuzzer.py

import itertools
import json
import random
from typing import Set, List, Dict, Any
from pathlib import Path
from datetime import datetime

from .assumption_graph import ASSUMPTION_GRAPH, propagate_breaks, assumption_criticality_score


class AdversarialFuzzer:
    """
    Genera casos de prueba rompiendo supuestos epistemológicos.
    No combina dimensiones ingenuamente - propaga rupturas por el grafo.
    """
    
    def __init__(self):
        self.assumptions = list(ASSUMPTION_GRAPH.keys())
        
    def generate_single_break(self, assumption_name: str) -> Dict[str, Any]:
        """Genera un caso que rompe un supuesto específico"""
        assumption = ASSUMPTION_GRAPH[assumption_name]
        
        # Base case template
        case = {
            "case_id": f"ASSUMPTION_BREAK_{assumption_name}",
            "description": f"Breaks assumption: {assumption.description}",
            "breaks": [assumption_name],
            "propagated_breaks": [],
            "artifacts": self._generate_artifacts_for_break(assumption_name),
            "expected_behavior": self._expected_behavior(assumption_name),
        }
        
        # Propagar rupturas
        all_broken = propagate_breaks({assumption_name})
        case["propagated_breaks"] = list(all_broken)
        case["criticality_score"] = assumption_criticality_score(all_broken)
        
        return case
    
    def generate_combinatorial_breaks(self, max_depth: int = 3) -> List[Dict[str, Any]]:
        """Genera casos rompiendo combinaciones de supuestos (con propagación)"""
        cases = []
        
        # Nivel 1: ruptura simple (ya está)
        for assumption in self.assumptions[:10]:  # Limitamos a 10 por ahora
            cases.append(self.generate_single_break(assumption))
        
        # Nivel 2: pares de supuestos base (sin dependencia entre ellos)
        base_assumptions = [a for a in self.assumptions 
                           if not ASSUMPTION_GRAPH[a].dependencies]
        
        for a1, a2 in itertools.combinations(base_assumptions[:6], 2):
            broken = {a1, a2}
            case = {
                "case_id": f"ASSUMPTION_BREAK_{a1}_AND_{a2}",
                "description": f"Breaks: {a1} + {a2}",
                "breaks": list(broken),
                "propagated_breaks": list(propagate_breaks(broken)),
                "artifacts": self._generate_artifacts_for_multi_break([a1, a2]),
                "expected_behavior": self._expected_multi_behavior([a1, a2]),
            }
            case["criticality_score"] = assumption_criticality_score(set(case["propagated_breaks"]))
            cases.append(case)
        
        return cases
    
    def _generate_artifacts_for_break(self, assumption_name: str) -> List[Dict]:
        """Genera artifacts que violan el supuesto específico"""
        # Mapeo de supuesto a violación concreta
        violations = {
            "timestamp_comparability": [
                {"source_tool": "log_a", "evidence_type": "log_entry", 
                 "raw_score": 0.7, "metadata": {"timestamp": "2026-05-18T10:00:00Z"}},
                {"source_tool": "log_b", "evidence_type": "log_entry",
                 "raw_score": 0.7, "metadata": {"timestamp": "2026-05-18T09:55:00Z", "timezone": "UTC-5"}},
            ],
            "sensor_independence": [
                {"source_tool": "edr_1", "evidence_type": "memory_process", "raw_score": 0.8, "metadata": {"sensor_fingerprint": "same_sensor"}},
                {"source_tool": "edr_2", "evidence_type": "memory_process", "raw_score": 0.8, "metadata": {"sensor_fingerprint": "same_sensor"}},
            ],
            "pipeline_integrity": [
                {"source_tool": "sensor", "evidence_type": "memory_process", "raw_score": 0.9,
                 "metadata": {"pipeline_hash": "compromised", "provenance_trust": 0.1}},
            ],
            "memory_ground_truth": [
                {"source_tool": "memory_dump", "evidence_type": "memory_process", "raw_score": 0.1,
                 "metadata": {"sampling_interval": 60, "event_time": "2026-05-18T10:00:00Z"}},
                {"source_tool": "log", "evidence_type": "log_entry", "raw_score": 0.9,
                 "metadata": {"event_time": "2026-05-18T10:00:30Z"}},
            ],
            "filesystem_monotonicity": [
                {"source_tool": "fs_scan", "evidence_type": "mft_entry", "raw_score": 0.5,
                 "metadata": {"mft_entry_number": 100, "timestamp": "2026-05-18T10:00:00Z"}},
                {"source_tool": "fs_scan", "evidence_type": "mft_entry", "raw_score": 0.5,
                 "metadata": {"mft_entry_number": 99, "timestamp": "2026-05-18T10:05:00Z"}},
            ],
        }
        
        return violations.get(assumption_name, [
            {"source_tool": "test", "evidence_type": "log_entry", 
             "raw_score": 0.5, "description": f"Violates {assumption_name}"}
        ])
    
    def _generate_artifacts_for_multi_break(self, assumptions: List[str]) -> List[Dict]:
        """Combina violaciones de múltiples supuestos"""
        artifacts = []
        for a in assumptions:
            artifacts.extend(self._generate_artifacts_for_break(a))
        return artifacts
    
    def _expected_behavior(self, assumption_name: str) -> Dict:
        """Define comportamiento esperado cuando se rompe un supuesto"""
        # Algunos supuestos el sistema puede detectar, otros no
        detectable = {
            "filesystem_monotonicity": True,   # MFT_ENTRY_ANOMALY
            "sensor_independence": True,        # Agrupamiento parcial
            "timestamp_comparability": False,   # No detecta drift suave
            "pipeline_integrity": False,        # Sin TPM
            "memory_ground_truth": False,       # Sampling gaps invisibles
        }
        
        return {
            "detectable": detectable.get(assumption_name, False),
            "graceful_degradation": True,  # Idealmente sí
            "should_alert_operator": detectable.get(assumption_name, False),
        }
    
    def _expected_multi_behavior(self, assumptions: List[str]) -> Dict:
        """Comportamiento esperado para ruptura múltiple"""
        any_detectable = any(self._expected_behavior(a)["detectable"] for a in assumptions)
        return {
            "detectable": any_detectable,
            "graceful_degradation": True,
            "should_alert_operator": any_detectable,
        }
    
    def generate_test_suite(self, output_dir: Path) -> None:
        """Genera el suite completo de tests adversariales"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar casos
        all_cases = self.generate_combinatorial_breaks(max_depth=3)
        
        # Guardar cada caso como JSON
        for case in all_cases:
            filename = output_dir / f"{case['case_id']}.json"
            with open(filename, "w") as f:
                json.dump(case, f, indent=2)
        
        # Guardar índice
        index = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_cases": len(all_cases),
            "cases": [c["case_id"] for c in all_cases],
        }
        with open(output_dir / "index.json", "w") as f:
            json.dump(index, f, indent=2)
        
        print(f"✅ Generated {len(all_cases)} adversarial test cases in {output_dir}")
        return all_cases
