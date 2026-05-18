"""
Stress Test Runner - Evaluates VIGIA against adversarial test cases
"""

import json
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vigia.tools.caie import (
    CrossArtifactIncongruenceEngine,
    Artifact,
    _VALID_EVIDENCE_TYPES,
)


@dataclass
class StressResult:
    case_id: str
    passed: bool
    actual: dict[str, Any]
    expected: dict[str, Any]
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StressTestRunner:
    def __init__(self, test_cases_dir: Path | None = None):
        self.test_cases_dir = test_cases_dir or Path(__file__).parent / "test_cases"
        self.results: list[StressResult] = []

    def run_all(self) -> list[StressResult]:
        """Run all JSON test cases in the test_cases directory"""
        json_files = sorted(self.test_cases_dir.glob("case_*.json"))
        if not json_files:
            print(f"Warning: No test cases found in {self.test_cases_dir}")
            return []
        
        for json_file in json_files:
            with open(json_file) as f:
                case = json.load(f)
            result = self.run_single(case)
            self.results.append(result)
        return self.results

    def run_single(self, case: dict) -> StressResult:
        """Run a single test case and return result"""
        case_id = case.get("case_id", "UNKNOWN")
        artifacts_data = case.get("artifacts", [])
        expected = case.get("expected", {})
        
        engine = CrossArtifactIncongruenceEngine()
        
        # Add artifacts
        for a_data in artifacts_data:
            evidence_type = a_data.get("evidence_type", "log_entry")
            if evidence_type not in _VALID_EVIDENCE_TYPES:
                # Map common test types to valid ones
                mapping = {
                    "memory": "memory_process",
                    "auth": "lsass_session",
                    "network": "log_entry",
                    "fs": "file_timestamp",
                    "log": "log_entry",
                    "kernel": "kernel_structure",
                    "ticket": "log_entry",
                }
                evidence_type = mapping.get(evidence_type, "log_entry")
            
            # Merge system_state into metadata if present
            metadata = a_data.get("metadata", {})
            if "system_state" in case:
                metadata.update(case["system_state"])
            
            artifact = Artifact(
                source_tool=a_data.get("source_tool", "stress_test"),
                evidence_type=evidence_type,
                raw_score=a_data.get("raw_score", 0.5),
                description=a_data.get("description", ""),
                metadata=metadata,
            )
            engine.add_artifact(artifact)
        
        # Add system_state artifacts if needed (for coverage metadata)
        system_state = case.get("system_state", {})
        if system_state.get("acquisition_confirmed_complete"):
            engine.add_artifact(Artifact(
                source_tool="acquisition",
                evidence_type="log_entry",
                raw_score=0.0,
                description="Acquisition metadata",
                metadata={
                    "acquisition_complete": True,
                    "usn_scope": system_state.get("usn_scope", False),
                    "coverage_score": system_state.get("coverage_score", 0.5),
                }
            ))
        
        # Evaluate
        result = engine.evaluate()
        
        # Validate against expectations
        failures = []
        warnings = []
        
        # Check verdict
        expected_verdict = expected.get("verdict")
        if expected_verdict:
            actual_verdict = result.get("verdict")
            if actual_verdict != expected_verdict:
                failures.append(f"verdict: expected {expected_verdict}, got {actual_verdict}")
        
        # Check must_not_be verdicts
        for forbidden in expected.get("must_not_be", []):
            if result.get("verdict") == forbidden:
                failures.append(f"verdict must not be {forbidden}, but got {forbidden}")
        
        # Check probabilistic score max
        max_score = expected.get("probabilistic_score_max")
        if max_score is not None:
            actual_score = result.get("probabilistic_score", 0.0)
            if actual_score > max_score:
                failures.append(f"probabilistic_score {actual_score} > {max_score}")
        
        # Check max independent sources
        max_sources = expected.get("max_independent_sources")
        if max_sources is not None:
            actual_sources = result.get("independent_sources", 0)
            if actual_sources > max_sources:
                failures.append(f"independent_sources {actual_sources} > {max_sources}")
        
        # Check daubert note contains required strings
        for required in expected.get("daubert_note_must_contain", []):
            daubert = result.get("daubert_note", "")
            if required.lower() not in daubert.lower():
                warnings.append(f"daubert_note missing '{required}'")
        
        # Check structural verdict
        expected_structural = expected.get("structural_verdict")
        if expected_structural:
            actual_structural = result.get("structural_verdict")
            if actual_structural != expected_structural:
                failures.append(f"structural_verdict: expected {expected_structural}, got {actual_structural}")
        
        passed = len(failures) == 0
        
        return StressResult(
            case_id=case_id,
            passed=passed,
            actual=result,
            expected=expected,
            failures=failures,
            warnings=warnings,
        )
    
    def summary(self) -> dict:
        """Return summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "results": self.results,
        }
