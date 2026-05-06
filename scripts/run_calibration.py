#!/usr/bin/env python3
"""
run_calibration.py — Calibración empírica del LRCalibrator de VIGÍA.

Extrae z-scores del corpus SYN + REAL + BEN, ajusta LRCalibrator,
guarda el modelo en models/calibrated_lr.json y actualiza
models/calibration_metadata.json con métricas de calidad.

Garantías Daubert:
    - Reproducible: mismo seed → mismo modelo
    - Auditables: hash del corpus de entrenamiento guardado
    - Separación: test set 20% estratificado, nunca visto en entrenamiento

Uso:
    python3 run_calibration.py
    python3 run_calibration.py --out models/calibrated_lr.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vigia_integration_bridge import (
    CaseAdapter, normalize_case_schema, validate_case_schema, CaseSchemaError,
)
from likelihood_ratio import LikelihoodEngine
from lr_calibration import LRCalibrator

# ---------------------------------------------------------------------------
# Etiquetado: qué verdicts son "fabricated" (señal alta) vs "authentic" (ruido)
# ---------------------------------------------------------------------------
_FABRICATED_VERDICTS = {"MALICE", "INTENT", "SUSPICION"}
_AUTHENTIC_VERDICTS  = {"NOISE", "BENIGN", "ABSTAIN"}


def _corpus_hash(files: list[str]) -> str:
    """SHA-256 del conjunto de archivos del corpus (determinista)."""
    h = hashlib.sha256()
    for f in sorted(files):
        h.update(f.encode())
        with open(f, "rb") as fp:
            h.update(fp.read())
    return h.hexdigest()


def extract_z_scores(
    case_files: list[str],
) -> tuple[list[float], list[float], dict]:
    """
    Extrae z-scores del corpus y los clasifica en authentic/fabricated.

    Retorna:
        authentic_z  : z-scores de casos genuinos (NOISE/BENIGN)
        fabricated_z : z-scores de casos manipulados (MALICE/INTENT)
        stats        : métricas del proceso de extracción
    """
    adapter = CaseAdapter()
    engine  = LikelihoodEngine()

    authentic_z:  list[float] = []
    fabricated_z: list[float] = []
    skipped = 0
    processed = 0

    for f in case_files:
        try:
            with open(f) as fp:
                case = json.load(fp)

            expected = case.get("expected_verdict", case.get("verdict", "")).upper()
            if not expected:
                skipped += 1
                continue

            # Normalizar schema y validar
            case = normalize_case_schema(case)
            try:
                validate_case_schema(case)
            except CaseSchemaError:
                skipped += 1
                continue

            signals, _ = adapter.to_signals(case)
            if not signals:
                skipped += 1
                continue

            record = engine.infer(signals=signals)
            # z-score promedio de las señales
            z_scores = getattr(record, "z_scores", None)
            if z_scores and len(z_scores) > 0:
                z_mean = sum(z_scores) / len(z_scores)
            else:
                # Derivar desde combined_log_lr: z ≈ sqrt(2 * log_lr)
                log_lr = record.combined_log_lr
                z_mean = math.sqrt(max(0.0, 2.0 * log_lr)) if log_lr > 0 else 0.0

            if expected in _FABRICATED_VERDICTS:
                fabricated_z.append(z_mean)
            elif expected in _AUTHENTIC_VERDICTS:
                authentic_z.append(z_mean)
            else:
                skipped += 1
                continue

            processed += 1

        except Exception as e:
            print(f"  [WARN] {os.path.basename(f)}: {e}", file=sys.stderr)
            skipped += 1

    stats = {
        "processed": processed,
        "skipped": skipped,
        "n_authentic": len(authentic_z),
        "n_fabricated": len(fabricated_z),
    }
    return authentic_z, fabricated_z, stats


def evaluate_calibrator(
    calibrator: LRCalibrator,
    authentic_z: list[float],
    fabricated_z: list[float],
) -> dict:
    """
    Evalúa el calibrador con métricas básicas Daubert-defensibles.

    Brier Score: mide calibración probabilística (0 = perfecto, 1 = terrible)
    FPR @ threshold 0.5: tasa de falsos positivos en el umbral estándar
    """
    all_z = authentic_z + fabricated_z
    all_y = [0] * len(authentic_z) + [1] * len(fabricated_z)

    if not all_z:
        return {"brier_score": None, "fpr": None, "tpr": None}

    brier = 0.0
    tp = fp = tn = fn = 0
    for z, y in zip(all_z, all_y):
        p_fab = calibrator.calibrated_posterior(z)
        brier += (p_fab - y) ** 2
        pred = 1 if p_fab >= 0.5 else 0
        if pred == 1 and y == 1: tp += 1
        elif pred == 1 and y == 0: fp += 1
        elif pred == 0 and y == 0: tn += 1
        else: fn += 1

    n = len(all_z)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "brier_score": round(brier / n, 4),
        "fpr_at_0.5":  round(fpr, 4),
        "tpr_at_0.5":  round(tpr, 4),
        "n_eval":      n,
    }


def main():
    parser = argparse.ArgumentParser(description="Calibración empírica LRCalibrator VIGÍA")
    parser.add_argument("--out", default="models/calibrated_lr.json",
                        help="Ruta de salida del calibrador (JSON)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla para reproducibilidad")
    parser.add_argument("--test-split", type=float, default=0.2,
                        help="Fracción para test set (default: 0.2)")
    args = parser.parse_args()

    # ── Recopilar corpus ──────────────────────────────────────────────
    base = os.path.dirname(os.path.abspath(__file__))
    files = (
        glob.glob(os.path.join(base, "VIGIA-SYN-*.json")) +
        glob.glob(os.path.join(base, "VIGIA-BEN-*.json")) +
        glob.glob(os.path.join(base, "VIGIA-REAL-*.json")) +
        glob.glob(os.path.join(base, "case_00*.json"))
    )
    files = sorted(set(files))
    print(f"\n[Calibración] Corpus: {len(files)} casos")

    corpus_hash = _corpus_hash(files)
    print(f"[Calibración] Corpus hash: {corpus_hash[:16]}…")

    # ── Extraer z-scores ──────────────────────────────────────────────
    print("[Calibración] Extrayendo z-scores…")
    authentic_z, fabricated_z, stats = extract_z_scores(files)

    print(f"  authentic  (NOISE/BENIGN): {stats['n_authentic']} casos")
    print(f"  fabricated (MALICE/INTENT): {stats['n_fabricated']} casos")
    print(f"  skipped: {stats['skipped']}")

    if stats["n_authentic"] < 5 or stats["n_fabricated"] < 5:
        print("\n[ERROR] Corpus insuficiente — se necesitan ≥5 casos por clase.")
        print("        El calibrador queda en modo FALLBACK (z²/2).")
        sys.exit(1)

    # ── Split train/test estratificado ────────────────────────────────
    import random
    rng = random.Random(args.seed)

    def _split(zs, frac):
        shuffled = list(zs)
        rng.shuffle(shuffled)
        cut = max(1, int(len(shuffled) * frac))
        return shuffled[cut:], shuffled[:cut]   # train, test

    auth_train, auth_test   = _split(authentic_z,  args.test_split)
    fab_train,  fab_test    = _split(fabricated_z, args.test_split)

    print(f"\n[Calibración] Train: {len(auth_train)} authentic + {len(fab_train)} fabricated")
    print(f"[Calibración] Test:  {len(auth_test)} authentic + {len(fab_test)} fabricated")

    # ── Ajustar calibrador ────────────────────────────────────────────
    print("\n[Calibración] Ajustando LRCalibrator…")
    calibrator = LRCalibrator()
    calibrator.fit(auth_train, fab_train, seed=args.seed)
    print(f"  Backend: {calibrator._meta.get('backend', 'unknown')}")

    # ── Evaluar ───────────────────────────────────────────────────────
    print("\n[Calibración] Evaluando en test set…")
    metrics = evaluate_calibrator(calibrator, auth_test, fab_test)
    print(f"  Brier Score : {metrics['brier_score']} (< 0.15 = bueno)")
    print(f"  FPR @ 0.5   : {metrics['fpr_at_0.5']}  (< 0.10 = bueno)")
    print(f"  TPR @ 0.5   : {metrics['tpr_at_0.5']}")

    # Alerta si el calibrador no es útil
    if metrics["brier_score"] and metrics["brier_score"] > 0.25:
        print("\n[WARN] Brier Score alto — corpus pequeño o muy sesgado.")
        print("       El calibrador ayuda, pero el corpus necesita más casos.")

    # ── Guardar calibrador ────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.join(base, args.out)), exist_ok=True)
    out_path = os.path.join(base, args.out)
    calibrator.save(out_path)
    print(f"\n[Calibración] Calibrador guardado: {out_path}")

    # ── Guardar metadata Daubert ──────────────────────────────────────
    meta_path = os.path.join(base, "models/calibration_metadata.json")
    meta = {
        "calibration_date":    datetime.datetime.utcnow().isoformat() + "Z",
        "script_version":      "run_calibration-v1.0",
        "corpus_hash":         corpus_hash,
        "corpus_size":         len(files),
        "seed":                args.seed,
        "test_split":          args.test_split,
        "n_authentic_train":   len(auth_train),
        "n_fabricated_train":  len(fab_train),
        "n_authentic_test":    len(auth_test),
        "n_fabricated_test":   len(fab_test),
        "backend":             calibrator._meta.get("backend", "unknown"),
        "metrics_test":        metrics,
        "calibrator_path":     args.out,
        "authentic_verdicts":  sorted(_AUTHENTIC_VERDICTS),
        "fabricated_verdicts": sorted(_FABRICATED_VERDICTS),
    }
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, sort_keys=True)
    print(f"[Calibración] Metadata guardada: {meta_path}")
    print("\n[Calibración] Completada. Sistema sale de modo FALLBACK.")
    print(f"              Para activar: VigiaPipeline(calibration_path='{args.out}')")


if __name__ == "__main__":
    main()
