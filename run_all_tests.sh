#!/bin/bash
echo "=========================================="
echo "Running all VIGIA tests (85 tests + 186 cases)"
echo "=========================================="

echo ""
echo "[1/5] Running pytest suite..."
python -m pytest tests/ -v --tb=short 2>&1 | tee test_results.log
echo "Exit code: $?"

echo ""
echo "[2/5] Running all cases (186)..."
python tests/run_all_cases.py 2>&1 | tee cases.log

echo ""
echo "[3/5] Running dataset validation..."
python tests/validate_dataset.py 2>&1 | tee validate.log

echo ""
echo "[4/5] Running CI validation..."
python tests/vigia_ci_validate.py 2>&1 | tee ci.log

echo ""
echo "[5/5] Running stress tests (new)..."
python run_stress_tests.py 2>&1 | tee stress.log

echo ""
echo "[6/6] Running adversarial tests (new)..."
python run_adversarial_tests.py 2>&1 | tee adversarial.log

echo ""
echo "=========================================="
echo "All tests completed"
echo "=========================================="
