#!/bin/bash
# Ejecuta los 10 casos VIGIA_BREAK y muestra resultados para el Accuracy Report

CASES_FILE="data/cases/VIGIA_BREAK_001-010.json"
PASS=0
FAIL=0
TOTAL=0

echo "=============================================================="
echo "VIGÍA BREAK TEST SUITE — Accuracy Report"
echo "=============================================================="
echo ""

# Extraer cada caso del JSON array y correrlo
python3 -c "
import json, subprocess, sys

with open('$CASES_FILE') as f:
    cases = json.load(f)

for case in cases:
    cid = case['case_id']
    desc = case.get('description', '')
    expected = case.get('expected', {})
    
    # Guardar caso temporal
    tmp = f'/tmp/vigia_break_{cid}.json'
    with open(tmp, 'w') as tf:
        json.dump(case, tf)
    
    # Ejecutar
    r = subprocess.run(
        ['python3', 'tests/run_vigia_case.py', tmp],
        capture_output=True, text=True, timeout=30
    )
    
    verdict_line = [l for l in r.stdout.split('\n') if 'VERDICT' in l]
    score_line = [l for l in r.stdout.split('\n') if 'Score' in l]
    validation = [l for l in r.stdout.split('\n') if 'Validation' in l]
    
    verdict = verdict_line[0].split(':')[1].strip() if verdict_line else 'ERROR'
    score = score_line[0].split(':')[1].strip().split()[0] if score_line else '0'
    
    # Evaluar contra expected
    exp_verdict = expected.get('verdict', '')
    if exp_verdict and exp_verdict in verdict:
        match = 'PASS'
    elif 'BENIGN' in str(expected) and verdict in ['NOISE', 'SUSPICION']:
        match = 'PASS'
    elif expected.get('confidence_range'):
        lo, hi = expected['confidence_range']
        if lo <= float(score) <= hi:
            match = 'PASS'
        else:
            match = 'FAIL'
    else:
        match = 'CHECK'
    
    print(f'[{match}] {cid}')
    print(f'       Desc: {desc[:80]}...')
    print(f'       Veredicto: {verdict} | Score: {score}')
    if 'must_flag' in expected:
        print(f'       Flag esperado: {expected[\"must_flag\"]}')
    print()
"
