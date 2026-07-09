#!/usr/bin/env python3
"""
A4 / B-069 — experimento MEDIDO de re-fit de perfiles (SOLO MEDICIÓN).

NO modifica `vigia/tools/caie.py`. Deriva perfiles candidatos desde el dataset
Tanda C, los inyecta por monkeypatch, re-puntúa el corpus y reporta los flips
vs baseline y vs expected. La decisión de aplicar es del operador (patrón
B-069: medir; si empeora o es nula, NO aplicar).

MÉTODO (documentado, defendible):
  - Alcance: los 36 perfiles "legacy pin" (spoof 0.50 / weight 0.20, B-067
    "Uncalibrated"), restringido a los que aparecen en el corpus con ≥
    MIN_SIGNALS señales (derivar un perfil de 1-4 señales no es defendible).
  - Solo se re-deriva `spoofability` por DIAGNOSTICIDAD; `base_weight` NO se
    toca (fue la palanca de inflación que hundió el intento de B-069).
  - spoofability_cand = clamp(0.50 - K·(incul_frac - base_rate), 0.15, 0.85)
    donde incul_frac = fracción de señales de ese tipo en casos inculpatorios
    (MALICE/INTENT/SUSPICION) y base_rate = fracción inculpatoria global.
    Tipos enriquecidos en malice bajan spoofability (más diagnósticos); tipos
    enriquecidos en benigno la suben. Movimiento BIDIRECCIONAL, no un raise
    uniforme.

Uso:
    PYTHONPATH=$(pwd) python3 scripts/experiment_a4_profile_refit.py [--k 0.6] [--min-signals 5]
"""
from __future__ import annotations

import argparse
import contextlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import run_all_agent as R  # noqa: E402
import vigia_scorer as _scorer  # noqa: E402
from vigia.tools import caie as _caie  # noqa: E402

INCUL = {"MALICE", "INTENT", "SUSPICION"}
BENIGN = {"NOISE", "BENIGN", "ABSTAIN"}


def _latest_dataset() -> Path:
    import glob
    m = sorted(glob.glob(str(_ROOT / "data" / "signal_calibration_dataset_*.json")))
    if not m:
        raise SystemExit("no hay dataset Tanda C — correr build_signal_calibration_dataset.py")
    return Path(m[-1])


def derive_candidates(k: float, min_signals: int) -> Dict[str, float]:
    """Deriva spoofability candidata por diagnosticidad para tipos legacy."""
    P = _caie.EVIDENCE_PROFILES
    legacy = {t for t, v in P.items()
              if abs(float(v.spoofability) - 0.50) < 1e-9
              and abs(float(v.base_weight) - 0.20) < 1e-9}

    ds = json.loads(_latest_dataset().read_text())
    recs = [r for r in ds["records"] if r["signal_source"] == "ebs_scorer"]

    # base rate inculpatorio global (sobre señales etiquetadas)
    lab = [r for r in recs if r["ground_truth"] in (INCUL | BENIGN)]
    base_rate = sum(1 for r in lab if r["ground_truth"] in INCUL) / max(1, len(lab))

    by_type: Dict[str, List[str]] = {}
    for r in recs:
        if r["evidence_type"] in legacy and r["ground_truth"] in (INCUL | BENIGN):
            by_type.setdefault(r["evidence_type"], []).append(r["ground_truth"])

    cand: Dict[str, float] = {}
    for t, gts in by_type.items():
        if len(gts) < min_signals:
            continue
        incul_frac = sum(1 for g in gts if g in INCUL) / len(gts)
        spoof = 0.50 - k * (incul_frac - base_rate)
        spoof = max(0.15, min(0.85, spoof))
        cand[t] = round(spoof, 4)
    return cand, base_rate, len(legacy)


def _verdicts(cases) -> Dict[str, str]:
    out = {}
    with open(os.devnull, "w") as dn, contextlib.redirect_stderr(dn):
        for cp in cases:
            try:
                case = json.loads(cp.read_text())
                res = _scorer._vigia_score(case)
                out[cp.stem] = str(res.get("verdict", "ERROR"))
            except Exception:
                out[cp.stem] = "ERROR"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, default=0.6)
    ap.add_argument("--min-signals", type=int, default=5)
    args = ap.parse_args()
    logging.disable(logging.CRITICAL)

    cand, base_rate, n_legacy = derive_candidates(args.k, args.min_signals)
    print(f"[A4-exp] base_rate inculpatorio = {base_rate:.3f}")
    print(f"[A4-exp] perfiles legacy totales = {n_legacy}; candidatos derivados (≥{args.min_signals} señales) = {len(cand)}")
    for t, s in sorted(cand.items(), key=lambda x: x[1]):
        arrow = "↓ más diagnóstico" if s < 0.50 else ("↑ más spoofable" if s > 0.50 else "=")
        print(f"    {t:26} spoof 0.50 → {s:.4f}   {arrow}")

    cases = R.find_cases(R.CASES_DIRS, "")
    expected = {cp.stem: R.extract_expected(cp) for cp in cases}

    # Baseline
    base_v = _verdicts(cases)

    # Candidato (monkeypatch — restaurado al salir)
    saved = {t: _caie.EVIDENCE_PROFILES[t] for t in cand}
    try:
        for t, s in cand.items():
            old = _caie.EVIDENCE_PROFILES[t]
            _caie.EVIDENCE_PROFILES[t] = _caie.EvidenceProfile(
                spoofability=s, base_weight=old.base_weight,
                description=old.description + " [A4-exp refit]",
            )
        cand_v = _verdicts(cases)
    finally:
        for t, v in saved.items():
            _caie.EVIDENCE_PROFILES[t] = v

    # ── Comparación vs expected (doctrina del comparador batch) ──────────────
    def ok(exp, got):
        al = {"BENIGN": "NOISE"}
        g = al.get(got, got); e = al.get(exp, exp)
        if exp == "UNKNOWN":
            return True
        return g == e or (e == "INTENT" and g == "MALICE") or (e == "SUSPICION" and g == "INTENT")

    fixed, broken, moved = [], [], []
    base_pass = cand_pass = 0
    for stem in base_v:
        exp = expected.get(stem, "UNKNOWN")
        bo = ok(exp, base_v[stem]); co = ok(exp, cand_v[stem])
        base_pass += bo; cand_pass += co
        if base_v[stem] != cand_v[stem]:
            moved.append((stem, exp, base_v[stem], cand_v[stem], bo, co))
        if bo and not co:
            broken.append((stem, exp, base_v[stem], cand_v[stem]))
        if co and not bo:
            fixed.append((stem, exp, base_v[stem], cand_v[stem]))

    n = len(base_v)
    print(f"\n[A4-exp] GATE COMPARATIVO ({n} casos)")
    print(f"    PASS baseline : {base_pass}/{n}")
    print(f"    PASS candidato: {cand_pass}/{n}   (Δ {cand_pass-base_pass:+d})")
    print(f"    veredictos movidos: {len(moved)}")
    print(f"    FIXED  (baseline FAIL → candidato PASS): {len(fixed)}")
    for f in fixed:
        print("        +", f)
    print(f"    BROKEN (baseline PASS → candidato FAIL): {len(broken)}")
    for b in broken:
        print("        -", b)
    if moved and not fixed and not broken:
        print("    (movimientos sin cambio de pass/fail — muestra:)")
        for mrow in moved[:8]:
            print("        ·", mrow)

    verdict = ("APLICAR" if cand_pass > base_pass and not broken
               else "NO APLICAR" if cand_pass < base_pass or broken
               else "NEUTRO — decisión Daubert (0 flips)")
    print(f"\n[A4-exp] RECOMENDACIÓN: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
