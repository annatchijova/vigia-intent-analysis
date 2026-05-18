#!/usr/bin/env python3
"""
Run VIGIA stress tests and generate report

Usage:
    python run_stress_tests.py
    python run_stress_tests.py --json
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tests.stress import StressTestRunner, StressMetrics, generate_report


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()
    
    print("Running VIGIA Stress Tests...")
    print("Target: Break the Assumptions (independence, observability, causality, sensor trust)")
    print()
    
    runner = StressTestRunner()
    results = runner.run_all()
    metrics = StressMetrics.full_report(results)
    
    if args.json:
        from vigia.tests.stress.report_generator import generate_json_report
        report = generate_json_report(results, metrics)
        print(json.dumps(report, indent=2))
    else:
        report = generate_report(results, metrics)
        print(report)
    
    # Exit with error code if any test failed
    if metrics["overall"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
