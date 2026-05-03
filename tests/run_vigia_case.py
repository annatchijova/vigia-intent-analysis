"""
scripts/run_vigia_case.py
==========================
VIGÍA — Demo Runner: ejecuta un caso forense y muestra el veredicto.

Uso:
    python run_vigia_case.py cases/case_001_temporal.json
    python run_vigia_case.py cases/case_004_provenance_break.json

Output: veredicto, confianza, fractures CAIE, report Daubert.
SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# Normalizador de schema legacy → EBS v1 (casos REAL y demo avanzados)
try:
    import sys; sys.path.insert(0, "pipeline"); from vigia_integration_bridge import normalize_case_schema as _normalize_case
except ImportError:
    def _normalize_case(c):  # type: ignore[misc]
        return c  # fallback no-op: el caso se procesa como viene

# Colores ANSI para terminal
RED = "\033[91m"
YEL = "\033[93m"
GRN = "\033[92m"
BLU = "\033[94m"
CYA = "\033[96m"
RST = "\033[0m"
BLD = "\033[1m"


def _verdict_color(verdict: str) -> str:
    return {
        "MALICE": RED + BLD,
        "SUSPICION": YEL + BLD,
        "NOISE": GRN,
    }.get(verdict.upper(), BLU)


def _compute_temporal_factor(violations: list[dict], artifact_id: str) -> float:
    """Inline — no depende del paquete vigia para poder correr en demo."""
    weights = {
        "EFFECT_BEFORE_CAUSE":    1.0,
        "TOO_FAST":               0.7,
        "STATISTICAL_UNIFORMITY": 0.6,
        "IDENTICAL_TIMESTAMP":    0.5,
        "CLOCK_SKEW":             0.4,
    }
    relevant = [
        v for v in violations
        if v.get("cause", {}).get("artifact_id") == artifact_id
        or v.get("effect", {}).get("artifact_id") == artifact_id
    ]
    if not relevant:
        return 1.0
    ws = [v.get("severity", 0.5) * weights.get(v.get("type", ""), 0.5) for v in relevant]
    return round(max(0.0, min(1.0, math.exp(-2.0 * max(ws)))), 4)


def _naive_score(artifacts: list[dict]) -> float:
    """Baseline ingenuo: promedio de raw_scores sin ajuste."""
    if not artifacts:
        return 0.0
    return round(sum(a.get("raw_score", 0) for a in artifacts) / len(artifacts), 4)


def _vigia_score(case: dict) -> dict:
    """
    Pipeline VIGÍA simplificado para demo standalone.
    No requiere que el paquete vigia esté instalado.
    Replica la lógica de: TrustFusion → CorrelationDecay → CAIE → Decision.
    """
    artifacts = case.get("artifacts", [])
    violations = case.get("temporal_violations", [])
    fractures = case.get("caie_fractures", [])
    provenance = case.get("provenance_analysis", {})

    if not artifacts:
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": []}

    # --- Paso 1: Calcular effective_trust por artefacto ---
    effective_trusts = []
    for a in artifacts:
        prov_trust = a.get("prior_trust", 1.0)
        # Cadena de provenance rota
        chain = a.get("provenance_chain", [])
        if provenance.get("chain_status") == "BROKEN" or not chain:
            epc_factor = 0.1
        else:
            epc_factor = min(1.0, 0.95 ** max(0, len(chain) - 3))

        temp_factor = _compute_temporal_factor(violations, a.get("artifact_id", ""))
        effective = round(prov_trust * epc_factor * temp_factor, 4)
        effective_trusts.append({
            "artifact_id": a.get("artifact_id"),
            "evidence_type": a.get("evidence_type"),
            "raw_score": a.get("raw_score", 0),
            "effective_trust": effective,
            "adjusted_score": round(a.get("raw_score", 0) * (1 - a.get("raw_score", 0) * 0.3) * (0.5 + 0.5 * effective), 4),
        })

    # --- Paso 2: Correlation decay simplificado ---
    # Misma fuente → penalización. Tipos hetero → bonus.
    source_counts: dict[str, int] = {}
    for a in artifacts:
        src = a.get("metadata", {}).get("acquisition_record", a.get("evidence_type", "?"))
        source_counts[src] = source_counts.get(src, 0) + 1

    unique_types = len(set(a.get("evidence_type") for a in artifacts))
    diversity_bonus = min(0.2, (unique_types - 1) * 0.05)

    adj_scores = []
    for et in effective_trusts:
        et_type = et["evidence_type"]
        count = source_counts.get(et_type, 1)
        source_penalty = min(0.5, (count - 1) * 0.15)
        adj = round(et["adjusted_score"] * (1 - source_penalty), 4)
        adj_scores.append(adj)

    if not adj_scores:
        composite = 0.0
    else:
        composite = round(
            1.0 - math.prod([max(0.0, 1.0 - s) for s in adj_scores]) + diversity_bonus,
            4
        )
        composite = min(0.99, composite)

    # --- Paso 3: CAIE fracture analysis ---
    # DISTINCIÓN CRÍTICA (hallazgo arquitectural):
    #   Fractures que indican PLANTACIÓN DELIBERADA (FALSE_FLAG, STATISTICAL_UNIFORMITY)
    #   → elevan el score de intención maliciosa (alguien actuó para engañar)
    #   → pero reducen la credibilidad de los artefactos individuales
    #
    # Fractures que indican INCONSISTENCIA INTERNA (VERDICT_CONFLICT)
    #   → reducen el score (la evidencia no es coherente)
    #
    # Referencia: debate ChatGPT vs Kimi — "CAIE decide coherencia global, no ejecución"
    fracture_malice_boost = 0.0
    fracture_credibility_penalty = 0.0
    MALICIOUS_FRACTURE_TYPES = {
        "FALSE_FLAG_PATTERN",
        "STATISTICAL_UNIFORMITY",  # automatización = agente deliberado
        "TEMPORAL_CAUSALITY_VIOLATION",
        "CRYPTOGRAPHIC_INCONSISTENCY",
        "LIVE_RESPONSE_VS_DISK",
    }
    CREDIBILITY_REDUCING_TYPES = {
        "VERDICT_CONFLICT",
        "CLOUD_VS_ONPREM",
    }

    for f in fractures:
        sev = f.get("severity", 0.5)
        ft = f.get("fracture_type", "")
        if ft in MALICIOUS_FRACTURE_TYPES:
            # Fractura maliciosa: evidencia de que alguien actuó → sube score de intent
            fracture_malice_boost += sev * 0.45
        elif ft in CREDIBILITY_REDUCING_TYPES:
            fracture_credibility_penalty += sev * 0.25

    fracture_malice_boost = min(0.5, fracture_malice_boost)
    fracture_credibility_penalty = min(0.35, fracture_credibility_penalty)

    # Violación temporal STATISTICAL_UNIFORMITY también eleva intención maliciosa
    for v in violations:
        if v.get("type") == "STATISTICAL_UNIFORMITY":
            fracture_malice_boost += v.get("severity", 0) * 0.35

    fracture_malice_boost = min(0.5, fracture_malice_boost)

    # Fractura temporal HARD GATE
    hard_temporal = any(
        v.get("type") == "EFFECT_BEFORE_CAUSE" and v.get("severity", 0) >= 0.9
        for v in violations
    )

    # --- Paso 4: Decisión ---
    # Score base = composite (evidencia directa)
    # Score final = composite + fracture_boost - credibility_penalty
    # Semántica: "¿qué tan probable es que hubo un agente malicioso actuando?"
    raw_intent_score = round(
        max(0.0, min(0.99, composite + fracture_malice_boost - fracture_credibility_penalty)),
        4
    )
    import math as _math
    n_artifacts = len(artifacts)
    support_score = round(min(1.0, _math.log(1 + n_artifacts) / _math.log(5)), 4)
    isolation_penalty = 0.85 if n_artifacts <= 2 else 1.0
    n_boost = 1.0 + max(0, (n_artifacts - 2) * 0.03)
    final_score = round(raw_intent_score * (0.9 + 0.1 * support_score), 4)

    mean_effective = sum(e["effective_trust"] for e in effective_trusts) / len(effective_trusts)

    # Provenance total ROTA anula incluso el boost por fractures
    # (no podemos acusar sin cadena de custodia)
    provenance_collapsed = (
        mean_effective < 0.01
        and not fractures  # si hay fractures, es evidencia de plantación → SUSPICION
    )

    if n_artifacts < 2 and final_score > 0.65:
        final_score = 0.65
    if hard_temporal:
        verdict = "MALICE"
        confidence = 0.95
        reason = "HARD GATE: EFFECT_BEFORE_CAUSE — physical law violation"
    elif provenance_collapsed:
        verdict = "NOISE"
        confidence = round(1.0 - mean_effective, 2)
        reason = "Provenance chain collapsed, sin fractures activas — inadmissible under Daubert"
    elif mean_effective < 0.15 and fractures:
        # Cadena rota PERO hay fractures → alguien la rompió deliberadamente
        verdict = "SUSPICION"
        confidence = round(min(0.75, fracture_malice_boost + 0.3), 2)
        reason = f"Cadena de custodia rota + {len(fractures)} fracture(s) activas — manipulación deliberada"
    elif final_score > 0.75:
        verdict = "MALICE"
        confidence = round(final_score, 2)
        reason = f"Intent score {final_score:.2f} excede umbral MALICE"
    elif final_score > 0.55:
        verdict = "SUSPICION"
        confidence = round(final_score, 2)
        reason = f"Señal significativa con soporte estructural (score={final_score:.2f})"
    elif final_score > 0.25:
        verdict = "UNKNOWN"
        confidence = round(final_score * 0.5, 2)
        reason = f"Anomalía sin suficiente soporte estructural (score={final_score:.2f})"
    else:
        verdict = "NOISE"
        confidence = round(1.0 - final_score, 2)
        reason = f"Sin evidencia suficiente de intención maliciosa (score={final_score:.2f})"

    return {
        "verdict": verdict,
        "score": final_score,
        "confidence": confidence,
        "reason": reason,
        "mean_effective_trust": round(mean_effective, 4),
        "composite_base": round(composite, 4),
        "fracture_malice_boost": round(fracture_malice_boost, 4),
        "fracture_credibility_penalty": round(fracture_credibility_penalty, 4),
        "diversity_bonus": round(diversity_bonus, 4),
        "hard_temporal_gate": hard_temporal,
        "effective_trusts": effective_trusts,
        "temporal_violations": len(violations),
        "caie_fractures": len(fractures),
        "peirce_chain": case.get("peirce_chain", {}),
        "expected_verdict": case.get("expected_verdict", "UNKNOWN"),
    }


def run_case(case_path: str) -> None:
    path = Path(case_path)
    if not path.exists():
        print(f"{RED}ERROR: File not found: {case_path}{RST}")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        case = json.load(f)
    case = _normalize_case(case)  # compatibilidad schema legacy → EBS v1

    print(f"\n{BLD}{'=' * 62}{RST}")
    print(f"{BLD}VIGÍA FORENSIC ANALYSIS{RST}")
    print(f"Case: {BLU}{case.get('name', case.get('case_id'))}{RST}")
    print(f"{'=' * 62}")
    print(f"\n{case.get('description', '')}\n")

    result = _vigia_score(case)
    naive = _naive_score(case.get("artifacts", []))

    vc = _verdict_color(result["verdict"])
    print(f"{'─' * 62}")
    print(f"  VERDICT  :  {vc}{result['verdict']}{RST}")
    print(f"  Score    :  {result['score']:.4f}  (naive baseline: {naive:.4f})")
    print(f"  Confidence:  {result['confidence']:.2%}")
    print(f"  Reason   :  {result['reason']}")
    print(f"{'─' * 62}")

    if result["hard_temporal_gate"]:
        print(f"\n  {RED}{BLD}⚠ HARD GATE TRIGGERED: EFFECT_BEFORE_CAUSE{RST}")
        for v in case.get("temporal_violations", []):
            if v.get("type") == "EFFECT_BEFORE_CAUSE":
                print(f"    {v.get('interpretation', '')}")

    if case.get("caie_fractures"):
        print(f"\n  {YEL}CAIE FRACTURES:{RST}")
        for f in case["caie_fractures"]:
            print(f"    [{f.get('fracture_type')}] severity={f.get('severity'):.2f}")
            print(f"    → {f.get('interpretation', '')[:80]}")

    if result["peirce_chain"]:
        pc = result["peirce_chain"]
        print(f"\n  {CYA}PEIRCE ABDUCTIVE CHAIN:{RST}")
        print(f"    Firstness  : {pc.get('firstness', '')}")
        print(f"    Secondness : {pc.get('secondness', '')}")
        print(f"    Thirdness  : {pc.get('thirdness', '')}")

    expected = result["expected_verdict"]
    actual = result["verdict"]
    match = actual == expected
    status = f"{GRN}PASS{RST}" if match else f"{RED}FAIL (expected {expected}){RST}"
    print(f"\n  Validation : {status}")

    print(f"\n  Effective Trust per artifact:")
    for et in result["effective_trusts"]:
        bar = "█" * int(et["effective_trust"] * 20)
        print(f"    {et['artifact_id'][:30]:30s} {bar:<20s} {et['effective_trust']:.4f}")

    print(f"\n{'=' * 62}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="VIGÍA — Demo runner para casos forenses"
    )
    parser.add_argument("case_file", help="Path al JSON del caso (e.g. cases/case_001_temporal.json)")
    args = parser.parse_args()
    run_case(args.case_file)


if __name__ == "__main__":
    main()
