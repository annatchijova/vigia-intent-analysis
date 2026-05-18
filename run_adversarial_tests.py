#!/usr/bin/env python3
"""
Run Adversarial Assumption Fuzzing against VIGIA

Tests what happens when the system's epistemological assumptions break.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigia.tests.adversarial.fuzzer import AdversarialFuzzer
from vigia.tests.adversarial.runner import AdversarialRunner


def main():
    print("=" * 70)
    print("VIGIA ADVERSARIAL ASSUMPTION FUZZING")
    print("Testing system stability under epistemological assumption collapse")
    print("=" * 70)
    print()
    
    # Generar casos adversariales
    print("📝 Generating adversarial test cases...")
    fuzzer = AdversarialFuzzer()
    test_dir = Path("vigia/tests/adversarial/generated_cases")
    cases = fuzzer.generate_test_suite(test_dir)
    print(f"   Generated {len(cases)} cases")
    print()
    
    # Ejecutar casos
    print("🏃 Running adversarial tests...")
    runner = AdversarialRunner(test_dir)
    results = runner.run_all()
    summary = runner.summary()
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Total cases: {summary['total']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  HIGH RISK false confidence: {summary['high_risk_false_confidence']}")
    
    if summary['high_risk_cases']:
        print()
        print("⚠️  HIGH RISK CASES (system overconfident when assumptions broken):")
        for case_id in summary['high_risk_cases']:
            print(f"     - {case_id}")
    
    print()
    print("=" * 70)
    print("EPISTEMOLOGICAL NOTE")
    print("These tests measure degradation under assumption collapse.")
    print("'Failed' means the system was overconfident when it shouldn't be.")
    print("This is a feature of the adversarial harness, not a bug report.")
    print("=" * 70)
    
    # Exit with error if any high risk cases found
    if summary['high_risk_false_confidence'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
