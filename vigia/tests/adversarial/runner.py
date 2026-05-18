# vigia/tests/adversarial/runner.py

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact
from .assumption_graph import propagate_breaks, assumption_criticality_score


class AdversarialRunner:
    """Ejecuta casos adversariales y mide degradación del sistema"""
    
    def __init__(self, test_cases_dir: Path):
        self.test_cases_dir = test_cases_dir
        self.results = []
    
    def run_all(self) -> List[Dict]:
        """Ejecuta todos los casos adversariales"""
        index_file = self.test_cases_dir / "index.json"
        if not index_file.exists():
            print(f"No index found in {self.test_cases_dir}")
            return []
        
        with open(index_file) as f:
            index = json.load(f)
        
        for case_name in index["cases"]:
            case_file = self.test_cases_dir / f"{case_name}.json"
            with open(case_file) as f:
                case = json.load(f)
            result = self.run_single(case)
            self.results.append(result)
        
        return self.results
    
    def run_single(self, case: Dict) -> Dict:
        """Ejecuta un caso adversarial y mide el resultado"""
        engine = CrossArtifactIncongruenceEngine()
        
        # Agregar artifacts
        for a_data in case.get("artifacts", []):
            artifact = Artifact(
                source_tool=a_data.get("source_tool", "adversarial"),
                evidence_type=a_data.get("evidence_type", "log_entry"),
                raw_score=a_data.get("raw_score", 0.5),
                description=a_data.get("description", ""),
                metadata=a_data.get("metadata", {}),
            )
            engine.add_artifact(artifact)
        
        # Evaluar
        result = engine.evaluate()
        
        # Calcular métricas de degradación
        broken = set(case.get("breaks", []))
        propagated = set(case.get("propagated_breaks", []))
        criticality = case.get("criticality_score", 0.0)
        
        # El sistema debería degradarse elegantemente
        expected_verdict = case.get("expected_behavior", {}).get("should_output", "INCONCLUSIVE")
        
        degradation = {
            "case_id": case["case_id"],
            "criticality": criticality,
            "broken_assumptions": list(broken),
            "propagated_assumptions": list(propagated),
            "actual_verdict": result.get("verdict"),
            "actual_score": result.get("probabilistic_score"),
            "structural_verdict": result.get("structural_verdict"),
            "detection_degraded": self._detection_degradation(case, result),
            "passed": self._evaluate_pass(case, result),
        }
        
        return degradation
    
    def _detection_degradation(self, case: Dict, result: Dict) -> str:
        """Mide cuánto degradó la detección"""
        criticality = case.get("criticality_score", 0.0)
        actual_score = result.get("probabilistic_score", 0.0)
        
        if criticality > 0.7 and actual_score > 0.6:
            return "HIGH_RISK_FALSE_CONFIDENCE"
        elif criticality > 0.5 and actual_score > 0.5:
            return "MEDIUM_RISK"
        else:
            return "LOW_RISK"
    
    def _evaluate_pass(self, case: Dict, result: Dict) -> bool:
        """Determina si el caso pasó (comportamiento aceptable)"""
        expected = case.get("expected_behavior", {})
        
        # Si el sistema debería detectar la ruptura y no lo hace
        if expected.get("detectable") and result.get("structural_verdict") == "NOISE":
            return False
        
        # Si la criticalidad es alta y el sistema tiene alta confianza (falsa)
        criticality = case.get("criticality_score", 0.0)
        if criticality > 0.7 and result.get("probabilistic_score", 0.0) > 0.7:
            return False
        
        return True
    
    def summary(self) -> Dict:
        """Resumen de resultados"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        
        high_risk = [r for r in self.results if r["detection_degraded"] == "HIGH_RISK_FALSE_CONFIDENCE"]
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "high_risk_false_confidence": len(high_risk),
            "high_risk_cases": [r["case_id"] for r in high_risk],
        }
