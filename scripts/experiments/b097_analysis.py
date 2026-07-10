#!/usr/bin/env python3
"""
B-097 ROOT CAUSE — análisis de los 33 casos como UN conjunto (investigación
pura, cero cambios de producto). Para cada caso: evidencia real (artefactos,
tipos, dominios, spoofability), qué calculó el motor (score/verdict/reason,
rama del ladder), y distancia al gate MALICE (qué le falta a cada rama).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path("/home/user/vigia-intent-analysis")
sys.path.insert(0, str(REPO))

from run_all_agent import find_cases, CASES_DIRS, extract_expected
from vigia_scorer import _vigia_score
from vigia.tools import caie

CASES_33 = [
    "VIGIA-BREAK-013", "VIGIA-BREAK-014", "VIGIA-LINUX-005", "VIGIA-NGDC-003",
    "VIGIA-NITROBA-M57-001", "VIGIA-REAL-005", "VIGIA-REAL-M57-JO-Dec07",
    "VIGIA-REAL-M57-PAT-Dec07", "VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT",
    "VIGIA-REAL-MAGNET-2021-IOS-ELI", "VIGIA-REAL-MAGNET-2022-ANDROID",
    "VIGIA-SET630-001", "VIGIA_KIWI_001", "VIGIA_KIWI_002_ZAPALLO_POV",
    "case_002_log_fabrication", "case_008_multi_source_fraud_demo",
    "VIGIA-2026-DEMO-008", "VIGIA-REAL-NFURY",
    "VIGIA_BREAK_001_SILENT_INCONSISTENCY",
    "VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE", "VIGIA_BREAK_004_SIGNAL_DROWNING",
    "VIGIA_BREAK_006_PERFECT_ATTACK", "VIGIA_BREAK_007_MISSING_LOGS",
    "VIGIA_BREAK_008_AMBIGUOUS", "VIGIA_BREAK_009_PROMPT_POISON",
    "VIGIA_BREAK_010_OVERPERFECT", "VIGIA-CAN-014", "VIGIA-CAN-016",
    "VIGIA-CAN-017", "VIGIA-CAN-032",
    "VIGIA-MAGNET-2014-TIMELINE", "VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN",
    "VIGIA-MAGNET-2022-iOS-JESS",
]

_DOM = getattr(caie, "_DOMAIN_MAP", {})
_PROF = getattr(caie, "EVIDENCE_PROFILES", {})

# rama S1: "no corroboration branch opens (N domain(s), H/A hard..., P per-cost..."
_RE_S1 = re.compile(
    r"no corroboration branch opens \((\d+) domain\(s\), (\d+)/(\d+) hard "
    r"class\(es\)/artifact\(s\), (\d+) per-cost")


def domain_of(et: str) -> str:
    d = _DOM.get(et)
    return d[1] if d else f"UNK({et})"


def spoof_of(et: str):
    p = _PROF.get(et)
    return p.spoofability if p is not None else None


def main():
    cases = {c.stem: c for c in find_cases(CASES_DIRS)}
    rows = []
    for stem in CASES_33:
        path = cases[stem]
        data = json.loads(path.read_text())
        expected = extract_expected(path)
        blind = {k: v for k, v in data.items() if k != "expected_verdict"}
        motor = _vigia_score(blind)
        arts = data.get("artifacts", [])
        ets = [str(a.get("evidence_type", "?")) for a in arts]
        et_counts = Counter(ets)
        doms = Counter(domain_of(e) for e in ets)
        spoofs = {e: spoof_of(e) for e in et_counts}
        score = str(motor.get("score", "?"))
        reason = str(motor.get("reason", ""))
        m = _RE_S1.search(reason)
        if m:
            branch = "S1 (>0.33, gate corroboración CERRADO)"
            gate = {"n_domains": int(m.group(1)), "hard_types": int(m.group(2)),
                    "hard_arts": int(m.group(3)), "per_cost": int(m.group(4))}
        elif "Significant signal" in reason:
            branch = "S2 (0.10<score<=0.33)"
            gate = None
        elif "Broken chain" in reason:
            branch = "S3 (fracturas + trust bajo)"
            gate = None
        else:
            branch = f"OTRA: {reason[:60]}"
            gate = None
        rows.append({
            "case": stem, "expected": expected,
            "motor_verdict": motor.get("verdict"), "score": score,
            "branch": branch, "gate": gate,
            "n_arts": len(arts), "n_types": len(et_counts),
            "evidence_types": dict(et_counts), "domains": dict(doms),
            "spoofability": spoofs,
            "reason": reason[:220],
        })

    # ── detalle por caso ────────────────────────────────────────────────────
    for r in rows:
        print("=" * 96)
        print(f"{r['case']}   expected={r['expected']}   motor={r['motor_verdict']}"
              f"   score={r['score']}")
        print(f"  rama    : {r['branch']}")
        if r["gate"]:
            g = r["gate"]
            print(f"  gate    : dominios={g['n_domains']} "
                  f"hard={g['hard_types']}t/{g['hard_arts']}a "
                  f"per-cost={g['per_cost']}")
        print(f"  n_arts={r['n_arts']}  n_types={r['n_types']}")
        print(f"  types   : {r['evidence_types']}")
        print(f"  domains : {r['domains']}")
        print(f"  spoof   : { {k: v for k, v in r['spoofability'].items()} }")
        print(f"  reason  : {r['reason']}")

    # ── agregados ───────────────────────────────────────────────────────────
    print("\n" + "#" * 96)
    print("AGREGADOS SOBRE LOS 33 (un solo conjunto)")
    print("#" * 96)
    print("\nramas del ladder:", dict(Counter(r["branch"] for r in rows)))
    print("\nexpected:", dict(Counter(r["expected"] for r in rows)))
    print("\nn_domains del gate (solo S1):",
          dict(Counter(r["gate"]["n_domains"] for r in rows if r["gate"])))
    dom_all = Counter()
    for r in rows:
        dom_all.update(r["domains"])
    print("\ndominios de artefactos (todos los casos):", dict(dom_all))
    et_all = Counter()
    for r in rows:
        et_all.update(r["evidence_types"])
    print("\nevidence_types (top 20):", dict(et_all.most_common(20)))
    print("\nn_arts:", dict(Counter(r["n_arts"] for r in rows)))
    print("n_types:", dict(Counter(r["n_types"] for r in rows)))
    # distancia al gate para S1
    print("\nS1 — qué le falta a cada rama del gate MALICE:")
    for r in rows:
        if not r["gate"]:
            continue
        g = r["gate"]
        need = []
        # rama 1: >=2 dominios Y (n_arts>=4 o n_types>=3) — n_gate_arts no está
        # en el reason; aproximamos con n_arts/n_types del caso (cota superior).
        if g["n_domains"] < 2:
            need.append(f"rama1: +{2-g['n_domains']} dominio(s)")
        else:
            need.append("rama1: dominios OK — masa insuficiente")
        if g["hard_types"] < 3 and g["hard_arts"] < 4:
            need.append(f"rama2: hard {g['hard_types']}/3t o {g['hard_arts']}/4a")
        if g["per_cost"] < 4:
            need.append(f"rama3: per-cost {g['per_cost']}/4")
        print(f"  {r['case']:<45} {'; '.join(need)}")
    # los 3 con etiqueta INTENT
    print("\nLOS 3 exp=INTENT dentro del conjunto:")
    for r in rows:
        if r["expected"] == "INTENT":
            print(f"  {r['case']}: rama={r['branch']} score={r['score']} "
                  f"domains={r['domains']}")


if __name__ == "__main__":
    main()
