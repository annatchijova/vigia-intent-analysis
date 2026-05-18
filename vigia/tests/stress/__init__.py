"""
VIGIA Stress Test Suite - Level "Break the Assumptions"

Designed to test structural limits, not syntax or parsing.
Targets: evidence independence, observability bias, causal inference,
sensor trust collapse, and the "absence ≠ benign" problem.
"""

from .runner import StressTestRunner
from .metrics import StressMetrics
from .report_generator import generate_report, generate_json_report

__all__ = ["StressTestRunner", "StressMetrics", "generate_report", "generate_json_report"]
