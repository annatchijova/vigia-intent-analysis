#!/usr/bin/env python3
"""
Tanda C — constructor del dataset de calibración a nivel señal (precondición A3/A4).

Regla L-033: no tocar la cadena gamma×FRS ni re-fitear perfiles sin ≥20 SEÑALES
REALES con ground truth. Este script las extrae del corpus — nunca las fabrica.

DOS SUBSTRATOS DISJUNTOS, etiquetados por `signal_source`:

  · "ebs_scorer"  — un registro por artefacto tomado de
    `vigia_scorer._vigia_score(...)["effective_trusts"]` (evidence_type,
    raw_score, spoofability, weight, effective_trust, adjusted_score). Cubre
    TODOS los evidence_types EBS del corpus. Substrato de **A4** (re-fit de
    `EVIDENCE_PROFILES`, B-069).

  · "sift_raw"    — señales SIFT tomadas de los bundles sellados de evidencia
    cruda (`results/agent_batch/*_agent_bundle.json`), filtradas a los
    evidence_types que la tabla gamma cubre (memory, mft, registry, event_log,
    windows_event_log, network, prefetch, browser, usb, shellbag, amcache).
    gamma se anota con la función REAL `apply_artifact_reliability` (sin
    duplicar la tabla). Substrato de **A3** (gamma×FRS, L-033/L-034/L-038).

GROUND TRUTH = `expected_verdict` del caso. Casos sin etiqueta (RT-NOLABEL) se
registran con `ground_truth="UNLABELED"` — señal real sin label, excluida del
conteo etiquetado, conservada para trazabilidad.

DAUBERT: emite `dataset_sha256` (canónico, sort_keys) + proveniencia + un
reporte de cobertura que declara EXPLÍCITAMENTE si L-033 (≥20 reales
etiquetadas) se cumple para A3 (gamma) y para A4 (perfiles) por separado.

NO es un cambio de scoring. Solo lectura sobre el corpus + bundles sellados.

Uso:
    PYTHONPATH=$(pwd) python3 scripts/build_signal_calibration_dataset.py \
        --output data/signal_calibration_dataset_YYYYMMDD.json
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# NOTA: NO se llama logging.disable() a nivel módulo — sería un efecto global que
# silenciaría logging para cualquier test que importe este script en el mismo
# proceso. El ruido de auditoría por-caso ya se suprime con redirect_stderr en
# _collect_ebs_records; el CLI (main) scopea la supresión localmente.

import run_all_agent as R  # noqa: E402  (find_cases, extract_expected, CASES_DIRS)
import vigia_scorer as _scorer  # noqa: E402
from vigia.sift._math_utils import apply_artifact_reliability  # noqa: E402

# Clases que la tabla gamma cubre (vigia/sift/_math_utils.apply_artifact_reliability).
# Se derivan importando la función, no re-listando la tabla: si un tipo tiene
# gamma < 1 es gamma-relevante.
_GAMMA_PROBE_TYPES = [
    "memory", "mft", "registry", "event_log", "windows_event_log",
    "network", "prefetch", "browser", "usb", "shellbag", "amcache",
]
GAMMA_TYPES = {
    t for t in _GAMMA_PROBE_TYPES
    if apply_artifact_reliability(Fraction(1, 1), t) < Fraction(1, 1)
}

RED_TEAM_DIR = _ROOT / "data" / "cases" / "red-team"

# Verdicts que cuentan como ground-truth etiquetado (BENIGN se alia a NOISE
# igual que en el comparador batch; UNKNOWN es etiqueta débil pero real).
_LABELED = {"MALICE", "INTENT", "SUSPICION", "NOISE", "ABSTAIN", "BENIGN", "UNKNOWN"}


def _to_float(v: Any) -> Optional[float]:
    """Coerciona float/Decimal/str/Fraction-dict a float. None si no se puede."""
    if v is None:
        return None
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict) and v.get("__fraction__"):
        try:
            return float(Fraction(int(v["num"]), int(v["den"])))
        except Exception:
            return None
    try:
        return float(v)
    except Exception:
        try:
            return float(Fraction(str(v)))
        except Exception:
            return None


def _gamma_for(evidence_type: str) -> Optional[float]:
    """gamma estático real para un evidence_type gamma-relevante, o None."""
    if evidence_type not in GAMMA_TYPES:
        return None
    return float(apply_artifact_reliability(Fraction(1, 1), evidence_type))


def _collect_ebs_records(case_path: Path, ground_truth: str) -> List[Dict[str, Any]]:
    """Corre el scorer sobre el caso y extrae un registro por artefacto."""
    try:
        case = json.loads(case_path.read_text())
    except Exception:
        return []
    try:
        with open(os.devnull, "w") as _dn, contextlib.redirect_stderr(_dn):
            out = _scorer._vigia_score(case)
    except Exception:
        return []
    if not isinstance(out, dict):
        return []
    ets = out.get("effective_trusts") or []
    case_verdict = str(out.get("verdict", ""))
    case_score = _to_float(out.get("score"))
    recs: List[Dict[str, Any]] = []
    # FRS/redundancia: tamaño del grupo por evidence_type dentro del caso.
    type_counts: Dict[str, int] = {}
    for et in ets:
        type_counts[str(et.get("evidence_type"))] = type_counts.get(str(et.get("evidence_type")), 0) + 1
    for et in ets:
        etype = str(et.get("evidence_type"))
        recs.append({
            "signal_source": "ebs_scorer",
            "case_id": case_path.stem,
            "ground_truth": ground_truth,
            "artifact_id": et.get("artifact_id"),
            "evidence_type": etype,
            "raw_score": _to_float(et.get("raw_score")),
            "spoofability": _to_float(et.get("spoofability")),
            "weight": _to_float(et.get("weight")),
            "effective_trust": _to_float(et.get("effective_trust")),
            "adjusted_score": _to_float(et.get("adjusted_score")),
            "gamma_static": _gamma_for(etype),          # None salvo tipos SIFT
            "is_gamma_class": etype in GAMMA_TYPES,
            "n_same_type_in_case": type_counts.get(etype, 1),
            "case_motor_verdict": case_verdict,
            "case_score": case_score,
        })
    return recs


def _collect_sift_records(bundle_path: Path, ground_truth: str,
                          case_id: str) -> List[Dict[str, Any]]:
    """Extrae señales SIFT gamma-relevantes de un bundle sellado."""
    try:
        d = json.loads(bundle_path.read_text())
    except Exception:
        return []
    sigs = (d.get("pipeline_results", {}) or {}).get("signals", []) or []
    # FRS: tamaño del grupo por evidence_type gamma dentro del caso.
    type_counts: Dict[str, int] = {}
    for s in sigs:
        et = str(s.get("evidence_type"))
        if et in GAMMA_TYPES:
            type_counts[et] = type_counts.get(et, 0) + 1
    recs: List[Dict[str, Any]] = []
    for s in sigs:
        etype = str(s.get("evidence_type"))
        if etype not in GAMMA_TYPES:
            continue
        z = _to_float(s.get("z_score"))
        gamma = _gamma_for(etype)
        recs.append({
            "signal_source": "sift_raw",
            "case_id": case_id,
            "ground_truth": ground_truth,
            "artifact_id": s.get("artifact_id"),
            "evidence_type": etype,
            "z_score": z,
            "confidence": _to_float(s.get("confidence")),
            "gamma_static": gamma,
            "z_post_gamma": (z * gamma) if (z is not None and gamma is not None) else None,
            "is_gamma_class": True,
            "n_same_type_in_case": type_counts.get(etype, 1),
            "source_tool": s.get("source"),
        })
    return recs


def dataset_sha256(records: List[Dict[str, Any]]) -> str:
    payload = json.dumps(records, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build(output: Path) -> Dict[str, Any]:
    cases = R.find_cases(R.CASES_DIRS, "")
    stem2path = {c.stem: c for c in cases}

    # Fixtures red-team (fuera de CASES_DIRS por diseño).
    rt_cases = sorted(RED_TEAM_DIR.glob("*.json")) if RED_TEAM_DIR.exists() else []

    records: List[Dict[str, Any]] = []
    bundles_dir = _ROOT / "results" / "agent_batch"

    def _gt(path: Path) -> str:
        v = R.extract_expected(path)
        return v if v in _LABELED else "UNLABELED"

    seen_cases = 0
    for cp in list(cases) + rt_cases:
        gt = _gt(cp)
        records.extend(_collect_ebs_records(cp, gt))
        b = bundles_dir / f"{cp.stem}_agent_bundle.json"
        if b.exists():
            records.extend(_collect_sift_records(b, gt, cp.stem))
        seen_cases += 1

    # ── Cobertura ───────────────────────────────────────────────────────────
    def _labeled(recs):
        return [r for r in recs if r["ground_truth"] in (_LABELED - {"UNKNOWN"})]

    ebs = [r for r in records if r["signal_source"] == "ebs_scorer"]
    sift = [r for r in records if r["signal_source"] == "sift_raw"]
    ebs_lab = _labeled(ebs)
    sift_lab = _labeled(sift)

    def _dist(recs, key):
        out: Dict[str, int] = {}
        for r in recs:
            out[str(r.get(key))] = out.get(str(r.get(key)), 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    # L-033: ≥20 reales etiquetadas, y ambas polaridades (inculpatoria vs benigna).
    def _polarities(recs):
        pos = sum(1 for r in recs if r["ground_truth"] in ("MALICE", "INTENT", "SUSPICION"))
        neg = sum(1 for r in recs if r["ground_truth"] in ("NOISE", "BENIGN", "ABSTAIN"))
        return pos, neg

    a4_pos, a4_neg = _polarities(ebs_lab)
    a3_pos, a3_neg = _polarities(sift_lab)

    coverage = {
        "n_cases_scanned": seen_cases,
        "n_records_total": len(records),
        "ebs_scorer": {
            "n_total": len(ebs),
            "n_labeled": len(ebs_lab),
            "by_ground_truth": _dist(ebs_lab, "ground_truth"),
            "by_evidence_type": _dist(ebs_lab, "evidence_type"),
            "polarity": {"inculpatory": a4_pos, "benign": a4_neg},
            "L033_ready_for_A4_profiles": len(ebs_lab) >= 20 and a4_pos >= 1 and a4_neg >= 1,
        },
        "sift_raw": {
            "n_total": len(sift),
            "n_labeled": len(sift_lab),
            "by_ground_truth": _dist(sift_lab, "ground_truth"),
            "by_evidence_type": _dist(sift_lab, "evidence_type"),
            "polarity": {"inculpatory": a3_pos, "benign": a3_neg},
            "L033_ready_for_A3_gamma": len(sift_lab) >= 20 and a3_pos >= 1 and a3_neg >= 1,
        },
        "gamma_types_covered": sorted(GAMMA_TYPES),
    }

    dataset = {
        "schema_version": "1.0.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Tanda C — dataset de calibración a nivel señal (precondición A3/A4). "
            "Regla L-033: ≥20 señales reales etiquetadas antes de tocar gamma/perfiles."
        ),
        "provenance": {
            "cases_dirs": [str(p.relative_to(_ROOT)) for p in R.CASES_DIRS],
            "red_team_dir": str(RED_TEAM_DIR.relative_to(_ROOT)),
            "sift_bundles_dir": "results/agent_batch",
            "ebs_source": "vigia_scorer._vigia_score(...)['effective_trusts'] (faithful engine output)",
            "sift_source": "results/agent_batch/*_agent_bundle.json pipeline_results.signals",
            "gamma_annotation": "vigia.sift._math_utils.apply_artifact_reliability (imported, not duplicated)",
            "synthetic": False,
        },
        "coverage": coverage,
        "dataset_sha256": dataset_sha256(records),
        "records": records,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dataset, indent=2, ensure_ascii=False, sort_keys=False))
    return dataset


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    default_out = f"data/signal_calibration_dataset_{datetime.now().strftime('%Y%m%d')}.json"
    ap.add_argument("--output", "-o", default=default_out)
    args = ap.parse_args()

    # Supresión de ruido de logging SOLO en el CLI (scope local, no al importar).
    logging.disable(logging.CRITICAL)

    out = Path(args.output)
    if not out.is_absolute():
        out = _ROOT / out
    ds = build(out)
    cov = ds["coverage"]
    # Reporte a stdout (logging.disable no afecta print).
    print(f"[signal-calib] cases scanned : {cov['n_cases_scanned']}")
    print(f"[signal-calib] records total : {cov['n_records_total']}")
    print(f"[signal-calib] EBS  labeled  : {cov['ebs_scorer']['n_labeled']}  "
          f"(A4 ready: {cov['ebs_scorer']['L033_ready_for_A4_profiles']})")
    print(f"[signal-calib] SIFT labeled  : {cov['sift_raw']['n_labeled']}  "
          f"(A3 ready: {cov['sift_raw']['L033_ready_for_A3_gamma']})")
    print(f"[signal-calib] sha256        : {ds['dataset_sha256'][:16]}")
    print(f"[signal-calib] written       : {out.relative_to(_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
