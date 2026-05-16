#!/usr/bin/env python3
"""
Batch test de casos VIGÍA — rápido y limpio
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

cases_dir = Path("cases")
case_files = sorted(cases_dir.glob("*.json"))

print("=" * 70)
print(f"VIGÍA BATCH TEST — {len(case_files)} casos")
print("=" * 70)

results = []
for case_file in case_files:
    case_id = case_file.stem
    print(f"\n--- {case_id} ---")
    
    # Correr run_vigia_full.py y capturar veredicto
    result = subprocess.run(
        ["python3", "scripts/run_vigia_full.py", str(case_file)],
        capture_output=True, text=True, timeout=30
    )
    
    output = result.stdout + result.stderr
    
    # Extraer veredicto
    verdict = "UNKNOWN"
    if "VERDICT  :  MALICE" in output:
        verdict = "MALICE"
    elif "VERDICT  :  SUSPICION" in output:
        verdict = "SUSPICION"
    elif "VERDICT  :  NOISE" in output:
        verdict = "NOISE"
    elif "VERDICT  :  ABSTAIN" in output:
        verdict = "ABSTAIN"
    
    # Extraer VERIFY level
    verify = "UNKNOWN"
    if "VERIFY    : PASS" in output:
        if "Level 2" in output:
            verify = "PASS-L2"
        elif "Level 3" in output:
            verify = "PASS-L3"
        else:
            verify = "PASS"
    elif "VERIFY    : FAIL" in output:
        verify = "FAIL"
    
    # Extraer CAIE fracturas
    caie_fractures = 0
    if "CAIE FRACTURES:" in output:
        # Contar líneas de fracturas
        caie_fractures = output.count("[") - output.count("CAIE FRACTURES:")
    
    print(f"  Verdict: {verdict} | Verify: {verify} | CAIE: {caie_fractures}")
    results.append({
        "case": case_id,
        "verdict": verdict,
        "verify": verify,
        "caie_fractures": caie_fractures,
    })

# Resumen
print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

verdicts = {}
verifies = {}
for r in results:
    verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    verifies[r["verify"]] = verifies.get(r["verify"], 0) + 1

print(f"\nVerdicts:")
for v, c in sorted(verdicts.items()):
    print(f"  {v}: {c}")

print(f"\nVerify:")
for v, c in sorted(verifies.items()):
    print(f"  {v}: {c}")

print(f"\nCAIE fracturas detectadas: {sum(r['caie_fractures'] for r in results)}")

print("\n" + "=" * 70)
print("✓ BATCH COMPLETADO")
print("=" * 70)
