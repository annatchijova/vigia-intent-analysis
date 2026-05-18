"""
Metrics for stress test evaluation
"""

from typing import Any
from .runner import StressResult


class StressMetrics:
    """Calculate metrics from stress test results"""
    
    @staticmethod
    def false_confidence_inflation(results: list[StressResult]) -> dict:
        """Detect cases where confidence should be low but is high"""
        inflated = []
        for r in results:
            if "false_high_confidence" in str(r.expected).lower():
                actual_score = r.actual.get("probabilistic_score", 0.0)
                if actual_score > 0.5:
                    inflated.append({
                        "case_id": r.case_id,
                        "score": actual_score,
                        "severity": "HIGH" if actual_score > 0.7 else "MEDIUM",
                    })
        return {"inflated_cases": inflated, "count": len(inflated)}
    
    @staticmethod
    def benign_overtrust(results: list[StressResult]) -> dict:
        """Detect cases that incorrectly return NOISE or MALICE when should be INCONCLUSIVE"""
        overtrust = []
        for r in results:
            if "STRESS_002" in r.case_id or "STRESS_007" in r.case_id or "STRESS_008" in r.case_id:
                if r.actual.get("verdict") == "NOISE" and r.actual.get("probabilistic_score", 0) < 0.3:
                    # This might be correct, but check if should be INCONCLUSIVE
                    if "must_return_inconclusive" in str(r.expected).lower():
                        overtrust.append({"case_id": r.case_id, "verdict": r.actual.get("verdict")})
        return {"overtrust_cases": overtrust, "count": len(overtrust)}
    
    @staticmethod
    def collapse_handling(results: list[StressResult]) -> dict:
        """Detect proper handling of observability collapse (cases 3 and 10)"""
        collapse_results = []
        for r in results:
            if "STRESS_003" in r.case_id or "STRESS_010" in r.case_id:
                collapse_results.append({
                    "case_id": r.case_id,
                    "verdict": r.actual.get("verdict"),
                    "passed": r.passed,
                    "failures": r.failures,
                })
        return {"collapse_cases": collapse_results, "passed": sum(1 for c in collapse_results if c["passed"])}
    
    @staticmethod
    def full_report(results: list[StressResult]) -> dict:
        """Generate full metrics report"""
        return {
            "false_confidence_inflation": StressMetrics.false_confidence_inflation(results),
            "benign_overtrust": StressMetrics.benign_overtrust(results),
            "collapse_handling": StressMetrics.collapse_handling(results),
            "overall": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            }
        }
