"""
Generate human-readable reports from stress test results
"""

from typing import Any
from datetime import datetime
from .runner import StressResult


def generate_report(results: list[StressResult], metrics: dict[str, Any]) -> str:
    """Generate a formatted report"""
    
    lines = []
    lines.append("=" * 70)
    lines.append("VIGIA STRESS TEST REPORT - \"Break the Assumptions\"")
    lines.append("=" * 70)
    lines.append(f"Timestamp: {datetime.utcnow().isoformat()}")
    lines.append("")
    
    # Overall summary
    overall = metrics.get("overall", {})
    lines.append("## OVERALL SUMMARY")
    lines.append(f"  Total cases: {overall.get('total', 0)}")
    lines.append(f"  Passed: {overall.get('passed', 0)}")
    lines.append(f"  Failed: {overall.get('failed', 0)}")
    lines.append(f"  Pass rate: {overall.get('passed', 0) / overall.get('total', 1):.1%}")
    lines.append("")
    
    # Critical findings
    lines.append("## CRITICAL FINDINGS")
    
    false_confidence = metrics.get("false_confidence_inflation", {})
    if false_confidence.get("count", 0) > 0:
        lines.append(f"  ⚠️ FALSE CONFIDENCE INFLATION: {false_confidence['count']} cases")
        for case in false_confidence.get("inflated_cases", []):
            lines.append(f"      - {case['case_id']}: score={case['score']:.2f} ({case['severity']})")
    else:
        lines.append("  ✓ No false confidence inflation detected")
    
    overtrust = metrics.get("benign_overtrust", {})
    if overtrust.get("count", 0) > 0:
        lines.append(f"  ⚠️ BENIGN OVERTRUST: {overtrust['count']} cases")
    else:
        lines.append("  ✓ No benign overtrust detected")
    
    collapse = metrics.get("collapse_handling", {})
    lines.append(f"  📊 COLLAPSE HANDLING: {collapse.get('passed', 0)}/{len(collapse.get('collapse_cases', []))} passed")
    lines.append("")
    
    # Detailed failures
    lines.append("## DETAILED FAILURES")
    failures = [r for r in results if not r.passed]
    if failures:
        for r in failures:
            lines.append(f"  ❌ {r.case_id}")
            for failure in r.failures:
                lines.append(f"      - {failure}")
    else:
        lines.append("  No failures detected")
    lines.append("")
    
    # Warnings
    all_warnings = [(r.case_id, w) for r in results for w in r.warnings]
    if all_warnings:
        lines.append("## WARNINGS (non-critical)")
        for case_id, warning in all_warnings[:10]:  # Limit to 10
            lines.append(f"  ⚠️ {case_id}: {warning}")
        if len(all_warnings) > 10:
            lines.append(f"  ... and {len(all_warnings) - 10} more")
    lines.append("")
    
    # Epistemological limit note
    lines.append("## EPISTEMOLOGICAL LIMIT NOTE")
    lines.append("  Cases 003 and 010 test the fundamental limit of closed-system inference:")
    lines.append("  'Cannot distinguish NO EVIDENCE from PERFECTLY HIDDEN without external trust anchor'")
    lines.append("  These cases are EXPECTED to be difficult or impossible to pass fully.")
    lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def generate_json_report(results: list[StressResult], metrics: dict[str, Any]) -> dict:
    """Generate JSON report for programmatic consumption"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "results": [
            {
                "case_id": r.case_id,
                "passed": r.passed,
                "failures": r.failures,
                "warnings": r.warnings,
                "actual_verdict": r.actual.get("verdict"),
                "actual_score": r.actual.get("probabilistic_score"),
            }
            for r in results
        ],
    }
