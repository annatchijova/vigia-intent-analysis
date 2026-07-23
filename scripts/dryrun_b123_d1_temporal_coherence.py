#!/usr/bin/env python3
"""
B-123 D1 dry-run — dos candidatas para `temporal_coherence`, SIN cablear.

El CCS (vigia/core/causal_closure.py) espera `temporal_coherence: Fraction
∈ [0,1]`. Este script mide sobre el corpus las dos opciones de método del
informe de excavación (docs/B123_EXCAVATION_20260723.md §5-D1), para que
la decisión de doctrina se tome con distribuciones reales y no a ciegas.

Ambas opciones comparten la base doctrinal ya sellada del scorer:
  - Solo cuentan violaciones EFFECT_BEFORE_CAUSE VALIDADAS contra los
    timestamps reales de los artefactos (contrato B-172: la declaración
    del examinador no tiene autoridad; se reutiliza
    vigia_scorer._validate_hard_temporal_violation como única fuente de
    verdad — cero validación nueva).
  - Sin ningún timestamp parseable en los artefactos → None (dimensión NO
    medible; el CCS la trata como ausente). Nunca se imputa un valor.
  - Timestamps presentes y cero violaciones validadas → coherence = 1.

OPCIÓN A — fiel al TCV huérfano (vigia/temporal/coherence_validator.py):
    fabrication = min(1, Σ w_causality + Fraction(n_hard, 10))
    con w_causality = Fraction(9,10) por violación validada (la tabla
    _ANOMALY_WEIGHTS del TCV) y bonus hard_to_fake = n/10.
    coherence = 1 − fabrication.
    Carácter: casi binaria — UNA violación validada satura (9/10+1/10=1).

OPCIÓN B — fiel a la severidad del scorer:
    fabrication = min(1, Σ _frac_sev(severity_i)) sobre validadas
    coherence = 1 − fabrication.
    Carácter: graduada por la severidad declarada (pero solo de pares
    verificados), consistente con cómo el scorer pesa lo temporal.

Aritmética: Fraction exclusivamente (deterministic-core Regla 1). El
script computa cada caso DOS veces y aborta si difieren (Regla 4).
Observación pura: exit 0, no escribe estado, no cablea nada.

Uso:
    PYTHONPATH=. python3 scripts/dryrun_b123_d1_temporal_coherence.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from dryrun_signal_quality_gate import find_cases  # noqa: E402
from vigia_scorer import (  # noqa: E402 — única fuente de verdad B-172
    _frac_sev,
    _parse_hard_temporal_timestamp,
    _validate_hard_temporal_violation,
)

_W_CAUSALITY = Fraction(9, 10)   # TCV _ANOMALY_WEIGHTS["causality_violation"]
_HARD_BONUS_UNIT = Fraction(1, 10)  # TCV: += Fraction(hard_count, 10)


def _validated_violations(case: dict) -> tuple[list[dict], bool]:
    """(violaciones EFFECT_BEFORE_CAUSE validadas, hay_timestamps_parseables)."""
    artifacts = case.get("artifacts") or []
    if not isinstance(artifacts, list):
        artifacts = []
    by_id: dict[str, dict] = {}
    dupes: set[str] = set()
    for a in artifacts:
        if not isinstance(a, dict):
            continue
        aid = a.get("artifact_id")
        if not isinstance(aid, str) or not aid:
            continue
        if aid in by_id:
            dupes.add(aid)
        by_id[aid] = a
    has_ts = any(
        _parse_hard_temporal_timestamp(a.get("timestamp")) is not None
        for a in artifacts if isinstance(a, dict)
    )
    validated = []
    violations = case.get("temporal_violations") or []
    if not isinstance(violations, list):
        violations = []
    for v in violations:
        if not isinstance(v, dict) or v.get("type") != "EFFECT_BEFORE_CAUSE":
            continue
        pair, _reason = _validate_hard_temporal_violation(v, by_id, dupes)
        if pair is not None:
            validated.append(v)
    return validated, has_ts


def coherence_option_a(case: dict) -> Optional[Fraction]:
    validated, has_ts = _validated_violations(case)
    if not has_ts:
        return None
    if not validated:
        return Fraction(1)
    fabrication = min(
        Fraction(1),
        _W_CAUSALITY * len(validated) + _HARD_BONUS_UNIT * len(validated),
    )
    return Fraction(1) - fabrication


def coherence_option_b(case: dict) -> Optional[Fraction]:
    validated, has_ts = _validated_violations(case)
    if not has_ts:
        return None
    if not validated:
        return Fraction(1)
    fabrication = min(
        Fraction(1),
        sum((_frac_sev(v.get("severity", 0.5)) for v in validated), Fraction(0)),
    )
    return Fraction(1) - fabrication


def _bucket(fr: Optional[Fraction]) -> str:
    if fr is None:
        return "None (no medible)"
    if fr == 1:
        return "= 1"
    if fr == 0:
        return "= 0"
    return "(0,1) intermedio"


def main() -> None:
    print("B-123 D1 dry-run — temporal_coherence, opciones A (TCV) vs B (severidad)")
    print("Nada cableado; medición pura sobre el corpus.\n")
    dist_a: dict[str, Counter] = defaultdict(Counter)
    dist_b: dict[str, Counter] = defaultdict(Counter)
    disagreements: list[tuple[str, str, str, str]] = []
    n = 0
    for path in find_cases():
        try:
            case = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(case, dict):
            continue
        n += 1
        expected = str(case.get("expected_verdict", "?")).upper() or "?"
        a1, a2 = coherence_option_a(case), coherence_option_a(case)
        b1, b2 = coherence_option_b(case), coherence_option_b(case)
        # Regla 4 (deterministic-core): mismo input, mismo output exacto.
        assert a1 == a2 and b1 == b2, f"NO DETERMINISTA en {path.stem}"
        dist_a[expected][_bucket(a1)] += 1
        dist_b[expected][_bucket(b1)] += 1
        if _bucket(a1) != _bucket(b1):
            disagreements.append((path.stem, expected, str(a1), str(b1)))

    for label, dist in (("OPCIÓN A (TCV, casi binaria)", dist_a),
                        ("OPCIÓN B (severidad graduada)", dist_b)):
        print(f"=== {label} — casos {n} ===")
        for verdict in sorted(dist):
            row = ", ".join(f"{k}: {v}" for k, v in sorted(dist[verdict].items()))
            print(f"  {verdict:12s} {row}")
        print()
    print(f"Desacuerdos de bucket A vs B: {len(disagreements)}")
    for stem, exp, va, vb in disagreements[:20]:
        print(f"  {stem:32s} exp={exp:9s} A={va:8s} B={vb}")


if __name__ == "__main__":
    main()
