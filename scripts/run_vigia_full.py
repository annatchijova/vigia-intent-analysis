#!/usr/bin/env python3
"""
run_vigia_full.py — Runner completo: razonamiento + bundle hash + verificación.
Uso: python3 run_vigia_full.py <caso.json>
"""
import sys, os, json, time, subprocess, tempfile

if len(sys.argv) < 2:
    print("Uso: python3 run_vigia_full.py <caso.json>")
    sys.exit(1)

case_file = sys.argv[1]

# 1. Razonamiento forense
subprocess.run([sys.executable, "tests/run_vigia_case.py", case_file])

# 2. Bundle hash + verificación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pipeline.vigia_integration_bridge import CaseAdapter, normalize_case_schema, validate_case_schema
    from pipeline.pipeline import VigiaPipeline

    with open(case_file) as f:
        case = json.load(f)
    case = normalize_case_schema(case)
    validate_case_schema(case)
    adapter = CaseAdapter()
    signals, _ = adapter.to_signals(case)
    drift = CaseAdapter.compute_drift(case)

    t0 = time.perf_counter()
    result = VigiaPipeline().run_full(signals=signals, drift_score=drift)
    elapsed = (time.perf_counter() - t0) * 1000

    sd = result.get("sealed_dict", {})
    integ = sd.get("integrity", {})
    bh = integ.get("bundle_hash", "N/A")
    ts = integ.get("sealed_at", sd.get("timestamp", "N/A"))

    tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    json.dump(sd, tf, sort_keys=True, indent=2, default=str)
    tf.close()
    v = subprocess.run(["python3", "forensics/verify_ebs_v1.py", tf.name],
                       capture_output=True, text=True)
    verif = "PASS" if "PASS" in v.stdout else "FAIL"
    level = next((l for l in ["Level 3", "Level 2", "Level 1"] if l in v.stdout), "?")
    os.unlink(tf.name)

    BLD="\033[1m"; RST="\033[0m"; GRN="\033[92m"; RED="\033[91m"
    col = GRN if verif == "PASS" else RED
    print(f"  {BLD}BUNDLE INTEGRITY:{RST}")
    print(f"  ┌─ HASH      : {bh}")
    print(f"  ├─ TIMESTAMP : {ts}")
    print(f"  ├─ VERIFY    : {col}{verif}{RST} — {level}")
    print(f"  └─ PIPELINE  : {elapsed:.1f} ms")
    print(f"\n{'=' * 62}\n")
except Exception as e:
    print(f"  [BUNDLE] Error: {e}")
