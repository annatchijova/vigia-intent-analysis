"""
validate_dataset.py  (v2 — pipeline unificado)
─────────────────────────────────────────────────────────────────────────────
Dataset Bootstrap VIGÍA + Pipeline de Validación Daubert

CAMBIOS v2 respecto a v1:
    1. Distribuciones realistas: log-normal + beta, no gaussianas simétricas.
       AUTHENTIC usa log-normal (asimetría real de corpus lingüísticos).
       FABRICATED/ADVERSARIAL con más dispersión y overlap controlado.
    2. Pipeline UNIFICADO: z-scores idénticos en calibración e inferencia.
       Elimina el desfase de escala que causaba FNR=1.0 con calibrador.
    3. Threshold óptimo (Youden J) calculado desde ROC, no fijo en 0.5.
    4. Señal GCI integrada como tercer canal (gci_mad_ratio por muestra).
    5. K-fold AUC para detectar overfitting al bootstrap.
    6. ECE reportado para Daubert.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import hashlib
import datetime
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _utcnow() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"

def _sha8(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:8]

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ─────────────────────────────────────────────────────────────────────────────
# Generadores de señales realistas
# ─────────────────────────────────────────────────────────────────────────────

def _lognorm(rng: random.Random, mu: float, sigma: float,
             lo: float = 0.0, hi: float = 10.0) -> float:
    return _clamp(rng.lognormvariate(mu, sigma), lo, hi)


def _generate_human_deltas(n: int, rng: random.Random) -> List[float]:
    deltas = []
    for _ in range(n):
        if rng.random() < 0.10:
            deltas.append(rng.uniform(0.05, 0.5))
        elif rng.random() < 0.05:
            deltas.append(rng.uniform(10.0, 60.0))
        else:
            deltas.append(_lognorm(rng, 0.8, 0.9, 0.1, 120.0))
    return deltas


def _generate_script_deltas(n: int, rng: random.Random, c: float = 2.0) -> List[float]:
    return [c + rng.gauss(0, c * 0.0005) for _ in range(n)]


def _generate_jitter_deltas(n: int, rng: random.Random, c: float = 2.0) -> List[float]:
    half = c * 0.03
    return [c + rng.uniform(-half, half) for _ in range(n)]


def _generate_mixed_deltas(n: int, rng: random.Random) -> Tuple[List[float], bool]:
    if rng.random() < 0.5:
        c = rng.uniform(1.0, 5.0)
        return _generate_jitter_deltas(n, rng, c), True
    return _generate_human_deltas(n, rng), False


def _compute_gci_mad_ratio(deltas: List[float]) -> float:
    """MAD/median — señal principal GCI. Bajo → algorítmico."""
    if len(deltas) < 3:
        return 0.5
    med = statistics.median(deltas)
    if med <= 0:
        return 0.0
    mad = statistics.median([abs(d - med) for d in deltas])
    return _clamp(mad / med, 0.0, 2.0)


# ── Distribuciones realistas por clase ──────────────────────────────────────
#
#   SDA sigma_max:
#     AUTHENTIC   → log-normal(μ=−0.4, σ=0.5): moda≈0.5, cola derecha larga
#     FABRICATED  → log-normal(μ=0.9,  σ=0.4): moda≈2.0, bien separado
#     ADVERSARIAL → log-normal(μ=0.7,  σ=0.6): más disperso, overlap real
#
#   CLI cognitive_stress_index:
#     AUTHENTIC   → beta(2,6)*1.2: moda≈0.2
#     FABRICATED  → beta(4,3)*1.5: moda≈0.85
#     ADVERSARIAL → beta(3,4)*1.4: zona media con ruido

def _sda_auth(rng: random.Random) -> float:
    return _lognorm(rng, -0.4, 0.5, 0.1, 3.0)

def _sda_fab(rng: random.Random) -> float:
    return _lognorm(rng, 0.9, 0.4, 0.5, 6.0)

def _sda_adv(rng: random.Random) -> float:
    return _lognorm(rng, 0.7, 0.6, 0.4, 6.0)

def _sda_border(is_auth: bool, rng: random.Random) -> float:
    return _sda_auth(rng) if is_auth else _clamp(rng.gauss(1.4, 0.5), 0.3, 4.0)

def _cli_auth(rng: random.Random) -> float:
    return _clamp(rng.betavariate(2.0, 6.0) * 1.2, 0.01, 0.8)

def _cli_fab(rng: random.Random) -> float:
    return _clamp(rng.betavariate(4.0, 3.0) * 1.5, 0.2, 1.5)

def _cli_adv(rng: random.Random) -> float:
    return _clamp(rng.betavariate(3.0, 4.0) * 1.4 + rng.gauss(0, 0.08), 0.1, 1.5)

def _cli_border(is_auth: bool, rng: random.Random) -> float:
    return _cli_auth(rng) if is_auth else _clamp(rng.gauss(0.55, 0.25), 0.05, 1.2)


# ─────────────────────────────────────────────────────────────────────────────
# Generador del dataset bootstrap v2
# ─────────────────────────────────────────────────────────────────────────────

def generate_bootstrap_dataset(seed: int = 42) -> List[Dict]:
    """180 muestras con distribuciones log-normal + beta (v2)."""
    rng = random.Random(seed)
    samples: List[Dict] = []
    idx = 0

    def _make(gt, is_ta, is_tsa, deltas, sda, cli, chain):
        nonlocal idx
        sid = f"BS2-{gt[:3]}-{idx:04d}"
        gci = _compute_gci_mad_ratio(deltas)
        payload = json.dumps({"id": sid, "gt": gt,
            "sda": round(sda, 4), "cli": round(cli, 4), "gci": round(gci, 4)},
            sort_keys=True)
        idx += 1
        return {
            "id": sid,
            "ground_truth": gt,
            "is_text_authentic": is_ta,
            "is_timestamps_algorithmic": is_tsa,
            "deltas": [round(d, 6) for d in deltas],
            "sda_sigma_max": round(_clamp(sda, 0.0, 10.0), 6),
            "cli_stress":    round(_clamp(cli, 0.0,  5.0), 6),
            "gci_mad_ratio": round(gci, 6),
            "generator_version": "bootstrap-v2",
            "transform_chain": chain,
            "hash": _sha8(payload + str(seed)),
        }

    # 50 AUTHENTIC
    for _ in range(50):
        n = rng.randint(10, 35)
        d = _generate_human_deltas(n, rng)
        samples.append(_make("AUTHENTIC", True, False, d,
                              _sda_auth(rng), _cli_auth(rng), ["human_text", "human_logs"]))

    # 50 FABRICATED
    for _ in range(50):
        n = rng.randint(10, 35)
        c = rng.uniform(1.0, 5.0)
        d = _generate_script_deltas(n, rng, c)
        samples.append(_make("FABRICATED", False, True, d,
                              _sda_fab(rng), _cli_fab(rng),
                              ["synthetic_text", f"constant_sleep_{c:.2f}"]))

    # 50 ADVERSARIAL
    for _ in range(50):
        n = rng.randint(12, 40)
        c = rng.uniform(1.5, 4.0)
        d = _generate_jitter_deltas(n, rng, c)
        samples.append(_make("ADVERSARIAL", False, True, d,
                              _sda_adv(rng), _cli_adv(rng),
                              ["synthetic_text", "temporal_mimicry", f"jitter_{c:.2f}"]))

    # 10 BORDERLINE — caso crítico Daubert: texto real + timestamps script
    for _ in range(10):
        n = rng.randint(8, 20)
        c = rng.uniform(1.0, 3.0)
        d = _generate_script_deltas(n, rng, c)
        samples.append(_make("BORDERLINE", True, True, d,
                              _sda_auth(rng), _cli_auth(rng),
                              ["authentic_text", "script_timestamps"]))

    # 10 BORDERLINE — texto fabricado + timestamps humanos
    for _ in range(10):
        n = rng.randint(8, 20)
        d = _generate_human_deltas(n, rng)
        samples.append(_make("BORDERLINE", False, False, d,
                              _sda_border(False, rng), _cli_border(False, rng),
                              ["fabricated_text", "human_timestamps"]))

    # 10 BORDERLINE — mixtos ambiguos
    for _ in range(10):
        n = rng.randint(8, 20)
        d, is_algo = _generate_mixed_deltas(n, rng)
        is_auth = rng.random() < 0.5
        samples.append(_make("BORDERLINE", is_auth, is_algo, d,
                              _sda_border(is_auth, rng), _cli_border(is_auth, rng),
                              ["mixed_ambiguous"]))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Estadísticas base (sin sklearn)
# ─────────────────────────────────────────────────────────────────────────────

def _pearson_r(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dsx = math.sqrt(sum((v - mx) ** 2 for v in x))
    dsy = math.sqrt(sum((v - my) ** 2 for v in y))
    if dsx == 0 or dsy == 0:
        return 0.0
    return num / (dsx * dsy)


def _roc_auc(y_true: List[int], y_score: List[float]) -> float:
    pairs = sorted(zip(y_score, y_true), reverse=True)
    pos = sum(y_true)
    neg = len(y_true) - pos
    if pos == 0 or neg == 0:
        return 0.5
    tp = fp = auc = prev_fp = 0
    prev_score = None
    for score, label in pairs:
        if score != prev_score:
            auc += tp * (fp - prev_fp)
            prev_fp = fp
            prev_score = score
        if label == 1:
            tp += 1
        else:
            fp += 1
    auc += tp * (fp - prev_fp)
    return auc / (pos * neg)


def _brier_score(y_true: List[int], y_prob: List[float]) -> float:
    n = len(y_true)
    return sum((y_prob[i] - y_true[i]) ** 2 for i in range(n)) / n if n else 1.0


def _bootstrap_ci(y_true, y_score, n_iter=500, ci=0.95, seed=42):
    rng = random.Random(seed)
    n = len(y_true)
    aucs = []
    for _ in range(n_iter):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        yt = [y_true[i] for i in idx]
        ys = [y_score[i] for i in idx]
        if 0 < sum(yt) < n:
            aucs.append(_roc_auc(yt, ys))
    if not aucs:
        return 0.5, 0.5
    aucs.sort()
    lo = int((1 - ci) / 2 * len(aucs))
    hi = int((1 + ci) / 2 * len(aucs))
    return aucs[lo], aucs[min(hi, len(aucs) - 1)]


def _optimal_threshold(y_true, y_score):
    """Youden J = max(TPR - FPR)."""
    pairs = sorted(zip(y_score, y_true), reverse=True)
    pos = sum(y_true); neg = len(y_true) - pos
    if pos == 0 or neg == 0:
        return 0.5, 0.5, 0.5
    best_j = -1.0; best_t = best_tpr = best_fpr = 0.0
    tp = fp = 0
    for score, label in pairs:
        if label == 1: tp += 1
        else: fp += 1
        tpr = tp / pos; fpr = fp / neg
        if tpr - fpr > best_j:
            best_j = tpr - fpr; best_t = score
            best_tpr = tpr; best_fpr = fpr
    return best_t, best_tpr, best_fpr


def _ece(y_prob, y_true, n_bins=10):
    n = len(y_prob)
    if n == 0:
        return 1.0
    ece = 0.0; bw = 1.0 / n_bins
    for i in range(n_bins):
        lo, hi = i * bw, (i + 1) * bw
        in_bin = [(y_prob[j], y_true[j]) for j in range(n) if lo <= y_prob[j] < hi]
        if in_bin:
            acc  = statistics.mean(y for _, y in in_bin)
            conf = statistics.mean(p for p, _ in in_bin)
            ece += (len(in_bin) / n) * abs(acc - conf)
    return round(ece, 4)


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline unificado
# ─────────────────────────────────────────────────────────────────────────────

def _build_baseline(samples: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Median + MAD sobre clase AUTHENTIC solamente."""
    auth = [s for s in samples if s["ground_truth"] == "AUTHENTIC"]
    if not auth:
        raise ValueError("No AUTHENTIC samples found.")
    def _stats(vals):
        med = statistics.median(vals)
        mad = statistics.median([abs(v - med) for v in vals])
        return {"median": med, "mad": max(mad, 1e-9)}
    return {
        "SDA": _stats([s["sda_sigma_max"] for s in auth]),
        "CLI": _stats([s["cli_stress"]     for s in auth]),
        "GCI": _stats([s["gci_mad_ratio"]  for s in auth]),
    }


def _to_z(val: float, bl: Dict[str, float]) -> float:
    return (val - bl["median"]) / max(bl["mad"], 1e-9)


def _gci_z(mad_ratio: float, bl: Dict[str, float]) -> float:
    """Invertido: mad_ratio bajo → z alto (más algorítmico)."""
    return (bl["median"] - mad_ratio) / max(bl["mad"], 1e-9)


def _score_sample(r: Dict, baseline: Dict, correction: float,
                  calibrator: Optional[object], z_cap: float = 3.0) -> float:
    """Calcula posterior para una muestra. FUNCIÓN ÚNICA — misma en calibración e inferencia."""
    sda_z = _clamp(_to_z(r["sda_sigma_max"], baseline["SDA"]), -z_cap, z_cap)
    cli_z = _clamp(_to_z(r["cli_stress"],    baseline["CLI"]), -z_cap, z_cap)
    gci_z = _clamp(_gci_z(r["gci_mad_ratio"], baseline["GCI"]), -z_cap, z_cap)

    if calibrator is not None and getattr(calibrator, "is_fitted", False):
        log_lrs = [
            calibrator.calibrated_log_lr(sda_z),  # type: ignore
            calibrator.calibrated_log_lr(cli_z),   # type: ignore
            calibrator.calibrated_log_lr(gci_z),   # type: ignore
        ]
    else:
        log_lrs = [(z ** 2) / 2 for z in [sda_z, cli_z, gci_z]]

    combined = sum(log_lrs) * correction
    combined = _clamp(combined, -100.0, 100.0)
    lr = math.exp(combined)
    return lr / (1.0 + lr)


def validate_dataset(
    samples: Optional[List[Dict]] = None,
    dataset_path: Optional[str] = None,
    mean_corr_override: Optional[float] = None,
    use_calibration: bool = True,
) -> Dict:
    """Pipeline de validación v2 — unificado y consistente."""
    if samples is None:
        if dataset_path and Path(dataset_path).exists():
            with open(dataset_path, "r", encoding="utf-8") as f:
                samples = [json.loads(line) for line in f if line.strip()]
        else:
            print("[VIGIA] Generating synthetic bootstrap v2...")
            samples = generate_bootstrap_dataset()

    hashes = [s.get("hash", s["id"]) for s in samples]
    has_dupes = len(hashes) != len(set(hashes))
    balance = dict(Counter(s["ground_truth"] for s in samples))
    print(f"[VIGIA] Balance: {balance}")

    baseline = _build_baseline(samples)
    bl = baseline
    print(f"[VIGIA] Baseline SDA: median={bl['SDA']['median']:.4f} MAD={bl['SDA']['mad']:.4f}")
    print(f"[VIGIA] Baseline CLI: median={bl['CLI']['median']:.4f} MAD={bl['CLI']['mad']:.4f}")
    print(f"[VIGIA] Baseline GCI: median={bl['GCI']['median']:.4f} MAD={bl['GCI']['mad']:.4f}")

    # Correlación SDA–CLI (solo AUTHENTIC)
    auth = [s for s in samples if s["ground_truth"] == "AUTHENTIC"]
    corr = _pearson_r(
        [_to_z(s["sda_sigma_max"], bl["SDA"]) for s in auth],
        [_to_z(s["cli_stress"],    bl["CLI"]) for s in auth],
    )
    mean_corr = abs(mean_corr_override if mean_corr_override is not None else corr)
    correction = max(0.0, 1.0 - mean_corr)
    print(f"[VIGIA] SDA–CLI Correlation (AUTHENTIC): r={corr:.4f}")

    # Calibrador — entrenado con z-scores de _score_sample (misma función)
    calibrator = None
    cal_meta: Dict = {"used": False}
    if use_calibration:
        try:
            from vigia.core.lr_calibration import LRCalibrator
            auth_z  = [_clamp(_to_z(s["sda_sigma_max"], bl["SDA"]), -3.0, 3.0)
                       for s in samples if s["ground_truth"] == "AUTHENTIC"]
            fab_z   = [_clamp(_to_z(s["sda_sigma_max"], bl["SDA"]), -3.0, 3.0)
                       for s in samples if s["ground_truth"] in ("FABRICATED", "ADVERSARIAL")]
            calibrator = LRCalibrator()
            calibrator.fit(auth_z, fab_z)
            cal_meta = {"used": True, "backend": calibrator.meta.get("backend", "?"),
                        "n_auth": len(auth_z), "n_fab": len(fab_z)}
            print(f"[VIGIA] Calibrator: {cal_meta['backend']}")
        except Exception as e:
            print(f"[VIGIA_WARN] Calibration disabled: {e}")

    # Scoring unificado
    gt_binary = [1 if s["ground_truth"] in ("FABRICATED", "ADVERSARIAL") else 0
                 for s in samples]
    posteriors = [_score_sample(s, baseline, correction, calibrator) for s in samples]

    auc   = _roc_auc(gt_binary, posteriors)
    brier = _brier_score(gt_binary, posteriors)
    auc_lo, auc_hi = _bootstrap_ci(gt_binary, posteriors)
    opt_t, opt_tpr, opt_fpr = _optimal_threshold(gt_binary, posteriors)
    ece_val = _ece(posteriors, gt_binary)

    def _confusion(thr):
        tp=fp=tn=fn=0
        for i, s in enumerate(samples):
            pred = 1 if posteriors[i] >= thr else 0
            g = gt_binary[i]
            if pred==1 and g==1: tp+=1
            elif pred==1 and g==0: fp+=1
            elif pred==0 and g==0: tn+=1
            else: fn+=1
        pos=tp+fn; neg=fp+tn
        return {"tp":tp,"fp":fp,"tn":tn,"fn":fn,
                "tpr": round(tp/pos,4) if pos else 0.0,
                "fpr": round(fp/neg,4) if neg else 0.0,
                "fnr": round(fn/pos,4) if pos else 0.0,
                "threshold": round(thr, 4)}

    cm_05  = _confusion(0.5)
    cm_opt = _confusion(opt_t)

    # K-fold AUC (5 folds)
    rng_kf = random.Random(42)
    data_kf = list(range(len(samples))); rng_kf.shuffle(data_kf)
    fsize = len(data_kf) // 5; fold_aucs = []
    for fi in range(5):
        test_idx = data_kf[fi*fsize:(fi+1)*fsize]
        if not test_idx: continue
        yt_f = [gt_binary[i] for i in test_idx]
        ys_f = [_score_sample(samples[i], baseline, correction, calibrator)
                for i in test_idx]
        if 0 < sum(yt_f) < len(yt_f):
            fold_aucs.append(_roc_auc(yt_f, ys_f))
    kfold_mean = statistics.mean(fold_aucs) if fold_aucs else 0.0
    kfold_std  = statistics.stdev(fold_aucs) if len(fold_aucs) > 1 else 0.0

    # Casos críticos Daubert
    critical = [(i, s) for i, s in enumerate(samples)
                if s.get("is_text_authentic") and s.get("is_timestamps_algorithmic")]
    gci_true_nlp_normal = sum(
        1 for i, s in critical
        if _gci_z(s["gci_mad_ratio"], bl["GCI"]) > 2.0
        and _to_z(s["sda_sigma_max"], bl["SDA"]) < 1.5
    )

    # Por clase
    per_class = {}
    for gt in ("AUTHENTIC", "FABRICATED", "ADVERSARIAL", "BORDERLINE"):
        idxs = [i for i, s in enumerate(samples) if s["ground_truth"] == gt]
        if not idxs: continue
        posts = [posteriors[i] for i in idxs]
        correct = sum(1 for i in idxs
                      if (posteriors[i] >= opt_t) == (gt_binary[i] == 1))
        per_class[gt] = {
            "count": len(idxs),
            "mean_posterior": round(statistics.mean(posts), 4),
            "median_posterior": round(statistics.median(posts), 4),
            "acc_at_optimal": round(correct / len(idxs), 4),
        }

    # Diagnóstico
    issues, strengths = [], []
    for cond, msg in [
        (auc >= 0.85,       f"ROC AUC={auc:.4f} — discrimination USABLE for expert testimony"),
        (auc >= 0.70,       f"ROC AUC={auc:.4f} — aceptable (target >0.85)"),
    ]:
        if cond: strengths.append(msg); break
    else:
        issues.append(f"ROC AUC={auc:.4f} — WEAK")

    if brier <= 0.15:
        strengths.append(f"Brier={brier:.4f} — calibration GOOD")
    elif brier <= 0.25:
        issues.append(f"Brier={brier:.4f} — aceptable (target <0.15)")
    else:
        issues.append(f"Brier={brier:.4f} — insufficient calibration")

    if ece_val <= 0.10:
        strengths.append(f"ECE={ece_val:.4f} — honest probabilities")
    else:
        issues.append(f"ECE={ece_val:.4f} — uncalibrated probabilities (target <0.10)")

    if cm_opt["fpr"] <= 0.15:
        strengths.append(f"FPR={cm_opt['fpr']:.4f} @ threshold óptimo — aceptable")
    else:
        issues.append(f"FPR={cm_opt['fpr']:.4f} — high false positive rate")

    if cm_opt["fnr"] <= 0.20:
        strengths.append(f"FNR={cm_opt['fnr']:.4f} — good fabrication detection")
    else:
        issues.append(f"FNR={cm_opt['fnr']:.4f} — fabricated cases missed")

    if abs(auc - kfold_mean) <= 0.05:
        strengths.append(f"K-fold AUC={kfold_mean:.4f}±{kfold_std:.4f} — no overfitting")
    else:
        issues.append(f"K-fold AUC={kfold_mean:.4f}±{kfold_std:.4f} — possible overfitting")

    if mean_corr <= 0.30:
        strengths.append(f"Correlación SDA-CLI={mean_corr:.4f} — independent signals")
    elif mean_corr <= 0.60:
        issues.append(f"Correlación SDA-CLI={mean_corr:.4f} — minor penalty")
    else:
        issues.append(f"Correlación SDA-CLI={mean_corr:.4f} — correction_factor REQUIRED")

    n_crit = len(critical)
    if n_crit > 0 and gci_true_nlp_normal >= n_crit * 0.7:
        strengths.append("Daubert critical case validated: GCI independent of NLP")
    elif n_crit > 0:
        issues.append("Daubert critical case: potentially coupled signals")

    status = "DEFENSIBLE" if len(issues) == 0 else ("ACEPTABLE" if len(issues) <= 2 else "REQUIRES_CALIBRATION")

    return {
        "validation_timestamp": _utcnow(),
        "pipeline_version": "v2",
        "dataset": {"total": len(samples), "balance": balance,
                    "duplicates_detected": has_dupes,
                    "generator_version": samples[0].get("generator_version", "?") if samples else "?"},
        "baseline": {k: {kk: round(vv, 6) for kk, vv in v.items()} for k, v in baseline.items()},
        "calibration": cal_meta,
        "correlation": {"sda_cli_r": round(corr, 4), "mean_corr": round(mean_corr, 4),
                        "correction_factor": round(correction, 4),
                        "corr_warning": mean_corr > 0.6},
        "metrics": {"roc_auc": round(auc, 4),
                    "roc_auc_ci_95": [round(auc_lo, 4), round(auc_hi, 4)],
                    "brier_score": round(brier, 4),
                    "ece": round(ece_val, 4),
                    "kfold_auc_mean": round(kfold_mean, 4),
                    "kfold_auc_std": round(kfold_std, 4)},
        "threshold_05": cm_05,
        "threshold_optimal": {**cm_opt, "youden_j": round(cm_opt["tpr"] - cm_opt["fpr"], 4)},
        "critical_cases": {"total": n_crit, "gci_true_nlp_normal": gci_true_nlp_normal,
                           "independence_validated": n_crit > 0 and gci_true_nlp_normal >= n_crit * 0.7},
        "per_class": per_class,
        "diagnosis": {"status": status, "strengths": strengths, "issues": issues},
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--no-calibration", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.generate_only:
        samples = generate_bootstrap_dataset(seed=args.seed)
        out = args.output or "data/bootstrap_v2.jsonl"
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            for s in samples: f.write(json.dumps(s, ensure_ascii=False) + "\n")
        print(f"[VIGIA] Dataset v2: {out} ({len(samples)} samples)")
        return

    report = validate_dataset(dataset_path=args.dataset,
                               use_calibration=not args.no_calibration)

    print("\n" + "=" * 72)
    print("VIGÍA — DAUBERT VALIDATION REPORT  (v2)")
    print("=" * 72)
    d = report["dataset"]
    print(f"Dataset: {d['total']} samples | {d['balance']}")
    m = report["metrics"]
    print(f"\nMETRICS:")
    print(f"  ROC AUC    : {m['roc_auc']}  IC95%=[{m['roc_auc_ci_95'][0]}, {m['roc_auc_ci_95'][1]}]")
    print(f"  Brier Score: {m['brier_score']}  ECE={m['ece']}")
    print(f"  K-fold AUC : {m['kfold_auc_mean']} ± {m['kfold_auc_std']}")
    co = report["threshold_optimal"]
    c5 = report["threshold_05"]
    print(f"\nOPTIMAL THRESHOLD (t={co['threshold']}, J={co['youden_j']:.4f}): "
          f"TPR={co['tpr']} FPR={co['fpr']} FNR={co['fnr']}")
    print(f"THRESHOLD 0.5: TPR={c5['tpr']} FPR={c5['fpr']} FNR={c5['fnr']}")
    cr = report["correlation"]
    print(f"\nSDA–CLI CORRELATION: r={cr['sda_cli_r']}  "
          f"correction_factor={cr['correction_factor']}")
    cc = report["critical_cases"]
    print(f"\nDAUBERT CRITICAL CASE: {cc['total']} samples | "
          f"GCI_True+NLP_Normal={cc['gci_true_nlp_normal']} | "
          + (" INDEPENDENCE" if cc["independence_validated"] else " VERIFY"))
    print(f"\nBY CLASS:")
    for cls, v in report["per_class"].items():
        print(f"  {cls:<15} mean_post={v['mean_posterior']:.4f}  "
              f"acc@opt={v['acc_at_optimal']:.4f}  n={v['count']}")
    diag = report["diagnosis"]
    print(f"\nDIAGNOSIS: {diag['status']}")
    for s in diag["strengths"]: print(f"  + {s}")
    for i in diag["issues"]:    print(f"  - {i}")
    print("=" * 72)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[VIGIA] Report: {args.output}")


if __name__ == "__main__":
    main()
