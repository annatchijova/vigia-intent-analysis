# test_m4_floor_comparison.py
"""Compara m4_floor = 2, 3, 4 en múltiples conjuntos de casos."""

import subprocess, json, os, sys
from collections import defaultdict

FLOORS = [2, 3, 4]
CASE_DIRS = {
    "maliciosos": "data/cases/VIGIA-REAL-*.json",  # 10 casos
    "benignos": "data/cases/benign/VIGIA-BEN-*.json",  # 15 casos
}

def run_benchmark(floor_value):
    """Modifica temporalmente m4_floor y ejecuta todos los casos."""
    # Leer detector actual
    with open("vigia/core/forensic_technical_detector.py", "r") as f:
        original = f.read()
    
    # Modificar m4_floor
    import re
    modified = re.sub(
        r'self\._m4_floor\s*=\s*\d+',
        f'self._m4_floor = {floor_value}',
        original
    )
    
    with open("vigia/core/forensic_technical_detector.py", "w") as f:
        f.write(modified)
    
    results = {"maliciosos": {}, "benignos": {}}
    
    for category, pattern in CASE_DIRS.items():
        import glob
        cases = sorted(glob.glob(pattern))
        for case_path in cases:
            case_name = os.path.basename(case_path).replace(".json", "")
            
            # Generar señales
            sig_path = f"/tmp/sig_{case_name}.json"
            subprocess.run(
                ["python3", "vigia/tools/vigia_case_adapter.py", case_path, sig_path],
                capture_output=True
            )
            
            # Ejecutar pipeline
            r = subprocess.run(
                ["python3", "pipeline/pipeline.py", "--signals", sig_path],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": "."}
            )
            
            try:
                d = json.loads(r.stdout)
                case_data = json.load(open(case_path))
                expected = case_data.get("expected_verdict", "?")
                decision = d["decision"]
                posterior = d["posterior"]
                
                # Determinar si es correcto
                if category == "maliciosos":
                    # Para MALICE, ACCEPT es correcto
                    # Para SUSPICION (REAL-005), ABSTAIN es correcto
                    if expected == "SUSPICION":
                        correct = decision == "ABSTAIN"
                    else:
                        correct = decision == "ACCEPT"
                else:  # benignos
                    correct = decision != "ACCEPT"
                
                results[category][case_name] = {
                    "expected": expected,
                    "decision": decision,
                    "posterior": round(posterior, 3),
                    "correct": correct
                }
            except Exception as e:
                results[category][case_name] = {
                    "expected": "?",
                    "decision": "ERROR",
                    "posterior": 0,
                    "correct": False,
                    "error": str(e)[:100]
                }
    
    # Restaurar archivo original
    with open("vigia/core/forensic_technical_detector.py", "w") as f:
        f.write(original)
    
    return results


# ── Ejecutar comparación ──────────────────────────────────────────
print("=" * 70)
print("COMPARACIÓN m4_floor = 2 vs 3 vs 4")
print("=" * 70)

all_results = {}
for floor in FLOORS:
    print(f"\nProbando m4_floor = {floor}...")
    all_results[floor] = run_benchmark(floor)
    
    # Resumen rápido
    for category in ["maliciosos", "benignos"]:
        cases = all_results[floor][category]
        correct = sum(1 for c in cases.values() if c["correct"])
        total = len(cases)
        print(f"  {category}: {correct}/{total} correctos")

# ── Tabla comparativa ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("TABLA COMPARATIVA DETALLADA")
print("=" * 70)
print(f"{'Caso':<15} {'Expected':<12} {'Floor=2':<10} {'Floor=3':<10} {'Floor=4':<10}")
print("-" * 70)

for category in ["maliciosos", "benignos"]:
    # Obtener todos los casos de esta categoría (usando floor=2 como referencia)
    case_names = sorted(all_results[2][category].keys())
    for case_name in case_names:
        expected = all_results[2][category][case_name]["expected"]
        decisions = []
        for floor in FLOORS:
            d = all_results[floor][category].get(case_name, {})
            if d.get("correct"):
                decisions.append(f"✅ {d['decision']}")
            else:
                decisions.append(f"❌ {d['decision']}")
        print(f"{case_name:<15} {expected:<12} {decisions[0]:<10} {decisions[1]:<10} {decisions[2]:<10}")

# ── Resumen final ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
for floor in FLOORS:
    mal_correct = sum(1 for c in all_results[floor]["maliciosos"].values() if c["correct"])
    ben_correct = sum(1 for c in all_results[floor]["benignos"].values() if c["correct"])
    mal_total = len(all_results[floor]["maliciosos"])
    ben_total = len(all_results[floor]["benignos"])
    total_correct = mal_correct + ben_correct
    total_cases = mal_total + ben_total
    print(f"Floor={floor}: {total_correct}/{total_cases} total | Maliciosos: {mal_correct}/{mal_total} | Benignos: {ben_correct}/{ben_total}")

# ── Análisis de casos discordantes ────────────────────────────────
print("\n" + "=" * 70)
print("CASOS DONDE LOS FLOORS DISCREPAN")
print("=" * 70)
for category in ["maliciosos", "benignos"]:
    case_names = sorted(all_results[2][category].keys())
    for case_name in case_names:
        results_per_floor = {}
        for floor in FLOORS:
            results_per_floor[floor] = all_results[floor][category][case_name]["correct"]
        
        # Si no todos los floors coinciden
        if len(set(results_per_floor.values())) > 1:
            expected = all_results[2][category][case_name]["expected"]
            print(f"\n  {case_name} (expected={expected}):")
            for floor in FLOORS:
                d = all_results[floor][category][case_name]
                status = "✅" if d["correct"] else "❌"
                print(f"    floor={floor}: {status} decision={d['decision']} posterior={d['posterior']}")
