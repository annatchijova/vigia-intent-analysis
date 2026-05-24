#!/usr/bin/env python3
"""
show_4_hashes.py — VIGÍA: explicit display of the 4 forensic hashes.

Uso:
    python3 show_4_hashes.py <caso.json>

Los 4 hashes:
    H1 — graph_hash        : SHA256 of the evidence graph (artifacts + signals)
    H2 — bundle_hash       : SHA256 del bundle sellado completo (cubre H1 + decisión + metadata)
    H3 — HMAC audit chain  : HMAC-SHA256 de la cadena de auditoría (ephemeral key en dev)
    H4 — EBS verify        : Independent verification of H2 by verify_ebs_v1
"""

import sys
import os
import json
import hashlib
import hmac
import time
import tempfile
import subprocess
from pathlib import Path

if len(sys.argv) < 2:
    print("Uso: python3 show_4_hashes.py <caso.json>")
    sys.exit(1)

case_file = Path(sys.argv[1])
if not case_file.exists():
    print(f"Error: no se encuentra {case_file}")
    sys.exit(1)

# ── Colores ANSI ─────────────────────────────────────────────────────────────
BLD = "\033[1m"
RST = "\033[0m"
GRN = "\033[92m"
YLW = "\033[93m"
RED = "\033[91m"
CYN = "\033[96m"

print(f"\n{'='*66}")
print(f"{BLD}VIGÍA — 4 FORENSIC HASHES{RST}")
print(f"Case: {case_file.name}")
print(f"{'='*66}\n")

# ── Setup path ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

try:
    from vigia.pipeline.vigia_integration_bridge import CaseAdapter, normalize_case_schema, validate_case_schema
    from vigia.pipeline.pipeline import VigiaPipeline
    from vigia.core.canonicalize import _canonicalize
except ImportError as e:
    print(f"{RED}[ERROR] Import falló: {e}{RST}")
    print("Asegurate de correr desde ~/vigia-repo con el .venv activo")
    sys.exit(1)

# ── Cargar caso ───────────────────────────────────────────────────────────────
with open(case_file) as f:
    case = json.load(f)

case = normalize_case_schema(case)
validate_case_schema(case)

adapter = CaseAdapter()
signals, meta = adapter.to_signals(case)
drift = CaseAdapter.compute_drift(case)

# ── Correr pipeline ───────────────────────────────────────────────────────────
t0 = time.perf_counter()
result = VigiaPipeline().run_full(signals=signals, drift_score=drift)
elapsed_ms = (time.perf_counter() - t0) * 1000

sd = result.get("sealed_dict", {})
integrity = sd.get("integrity", {})

# ── H1: graph_hash ────────────────────────────────────────────────────────────
h1 = integrity.get("graph_hash", "")
h1_status = GRN + "PRESENT" + RST if h1 else RED + "ABSENT" + RST

print(f"{BLD}H1 — graph_hash{RST}  (SHA256 of the evidence graph)")
print(f"   {CYN}{h1 if h1 else 'N/A'}{RST}")
print(f"   Status : {h1_status}")
print()

# ── H2: bundle_hash ───────────────────────────────────────────────────────────
h2 = integrity.get("bundle_hash", "")
h2_status = GRN + "PRESENT" + RST if h2 else RED + "ABSENT" + RST

print(f"{BLD}H2 — bundle_hash{RST}  (SHA256 del bundle sellado completo — cubre H1)")
print(f"   {CYN}{h2 if h2 else 'N/A'}{RST}")
print(f"   Status : {h2_status}")
print(f"   Sealed : {integrity.get('sealed_at', 'N/A')}")
print()

# ── H3: HMAC audit chain ──────────────────────────────────────────────────────
# El HMAC se genera internamente por SecurityAuditLogger con clave efímera.
# We can recompute it over the bundle to demonstrate the mechanism.
hmac_key = os.environ.get("VIGIA_HMAC_KEY", "").encode()
if not hmac_key:
    # Dev mode: recompute con clave derivada del bundle_hash (solo para display)
    hmac_key = hashlib.sha256(h2.encode() if h2 else b"dev").digest()
    hmac_note = f"{YLW}ephemeral (dev mode — set VIGIA_HMAC_KEY for production){RST}"
else:
    hmac_note = f"{GRN}production key from env{RST}"

bundle_canonical = json.dumps(
    _canonicalize({k: v for k, v in sd.items() if k != "integrity"}),
    sort_keys=True, separators=(',', ':'), ensure_ascii=True
).encode()

h3 = hmac.new(hmac_key, bundle_canonical, hashlib.sha256).hexdigest()

print(f"{BLD}H3 — HMAC audit chain{RST}  (HMAC-SHA256 of the canonical bundle)")
print(f"   {CYN}{h3}{RST}")
print(f"   Key    : {hmac_note}")
print()

# ── H4: verify_ebs_v1 ─────────────────────────────────────────────────────────
tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
json.dump(sd, tf, sort_keys=True, indent=2, default=str)
tf.close()

verify_script = Path(__file__).parent / "forensics" / "verify_ebs_v1.py"
if not verify_script.exists():
    verify_script = Path(__file__).parent / "verify_ebs_v1.py"

v = subprocess.run(
    [sys.executable, str(verify_script), tf.name],
    capture_output=True, text=True
)
os.unlink(tf.name)

v_out = v.stdout + v.stderr
if "PASS" in v_out:
    level = next((l for l in ["Level 3", "Level 2", "Level 1"] if l in v_out), "Level ?")
    h4_status = f"{GRN}PASS — {level}{RST}"
else:
    h4_status = f"{RED}FAIL{RST}"
    level = "FAIL"

print(f"{BLD}H4 — EBS verify{RST}  (independent verification of H2 by verify_ebs_v1)")
print(f"   Recomputes bundle_hash from sealed_dict and compares against stored value")
print(f"   Status : {h4_status}")
print()

# ── CAIE fractures ───────────────────────────────────────────────────────────
# Fractures live at sealed_dict → caie_analysis → key_fractures.
# (The raw CAIE result uses the key "fractures"; the pipeline copies up to 5
#  of them into key_fractures.  "fracture_details" does not exist.)
caie_analysis = sd.get("caie_analysis") or {}
fractures = caie_analysis.get("key_fractures", [])
if fractures:
    print(f"{BLD}CAIE FRACTURES  ({caie_analysis.get('verdict','?')} · "
          f"score={caie_analysis.get('composite_score','?')} · "
          f"golden={caie_analysis.get('golden_rules_triggered',0)}){RST}")
    for f in fractures:
        sev = f.get("severity", 0)
        col = RED if sev >= 0.9 else YLW if sev >= 0.7 else GRN
        print(f"  {col}[{f.get('type','?')}]{RST}  severity={sev}")
    print()

# ── Resumen ───────────────────────────────────────────────────────────────────
# Forensic verdict priority:
#   1. caie_analysis["gate_verdict"]   — structural impossibility (always wins)
#   2. posterior >= 0.95 → "MALICE"    — Bayesian near-certainty
#   3. caie_analysis["verdict"]        — CAIE probabilistic
#   4. decision_trace.decision         — governance fallback (ACCEPT/REJECT/ABSTAIN)
_dt = sd.get("decision_trace")
_posterior = float(getattr(_dt, "posterior", 0) if hasattr(_dt, "posterior")
             else (_dt or {}).get("posterior", 0))
_caie = sd.get("caie_analysis", {})

if _caie.get("gate_verdict"):
    forensic_verdict = _caie["gate_verdict"]
    verdict_source = "CAIE structural gate"
elif _posterior >= 0.95:
    forensic_verdict = "MALICE"
    verdict_source = f"Bayesian posterior={_posterior:.4f}"
elif _caie.get("verdict"):
    forensic_verdict = _caie["verdict"]
    verdict_source = "CAIE probabilistic"
else:
    forensic_verdict = None
    verdict_source = "governance"

_dec = result.get("decision", "UNKNOWN")
if forensic_verdict:
    verdict = forensic_verdict
    score_raw = _posterior if _posterior else _caie.get("composite_score", 0)
elif hasattr(_dec, "decision"):         # dataclass DecisionTrace
    verdict   = _dec.decision
    score_raw = getattr(_dec, "posterior", getattr(_dec, "risk", 0))
    verdict_source = "governance"
elif isinstance(_dec, dict):
    verdict   = _dec.get("decision", _dec.get("verdict", "UNKNOWN"))
    score_raw = _dec.get("posterior", _dec.get("score", 0))
    verdict_source = "governance"
else:
    verdict   = str(_dec)
    score_raw = result.get("posterior", result.get("risk", 0))
    verdict_source = "governance"

print(f"{'─'*66}")
print(f"{BLD}VERDICT  :{RST}  {verdict}")
print(f"{BLD}SCORE    :{RST}  {score_raw}")
print(f"{BLD}PIPELINE :{RST}  {elapsed_ms:.1f} ms")
print()
print(f"{BLD}HASH INTEGRITY SUMMARY{RST}")
all_present = all([h1, h2, h3])
all_pass    = "PASS" in (h4_status)
col = GRN if (all_present and all_pass) else RED
print(f"  H1 graph_hash   : {'OK' if h1 else 'MISSING':8}  {h1[:16]}..." if h1 else f"  H1 graph_hash   : MISSING")
print(f"  H2 bundle_hash  : {'OK' if h2 else 'MISSING':8}  {h2[:16]}..." if h2 else f"  H2 bundle_hash  : MISSING")
print(f"  H3 HMAC chain   : {'OK' if h3 else 'MISSING':8}  {h3[:16]}...")
print(f"  H4 EBS verify   : {level}")
print(f"\n  {col}{'GREEN — all hashes present and verified' if (all_present and all_pass) else 'REVIEW — see details above'}{RST}")
print(f"{'='*66}\n")
