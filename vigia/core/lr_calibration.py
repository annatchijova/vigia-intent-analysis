"""
vigia/core/lr_calibration.py
─────────────────────────────────────────────────────────────────────────────
Calibración Empírica del Likelihood Ratio

PROBLEMA (ChatGPT, auditoriaparaarreglar.md §1):
    log_lr = z²/2 asume distribución gaussiana. Las distribuciones de señales
    lingüísticas forenses NO son normales (sesgadas, heavy-tailed, multimodales).
    Sin calibración: Brier Score alto, FPR explosivo — sistema indefendible.

SOLUCIÓN:
    Reemplazar z²/2 por un mapeo empírico aprendido del dataset bootstrap.
    Dos opciones disponibles (selección automática por disponibilidad):
        1. Logistic Calibration (sklearn)  — preferida
        2. Isotonic Regression (sklearn)   — si logistic no converge
        3. Platt Scaling manual (stdlib)   — fallback sin dependencias

GARANTÍAS DAUBERT:
    - El modelo de calibración se entrena SÓLO sobre clase AUTHENTIC del bootstrap.
    - Se serializa con versión y hash del dataset de entrenamiento.
    - Es reproducible: mismo seed → mismo modelo.
    - La curva de calibración (reliability curve) queda guardada para peritaje.

USO:
    calibrator = LRCalibrator()
    calibrator.fit(authentic_z_scores, fabricated_z_scores)
    calibrated_lr = calibrator.transform(z_score)

    # O desde el LikelihoodEngine:
    engine = LikelihoodEngine(calibrator=calibrator)
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import math
import statistics
import hashlib
import datetime
from typing import Dict, List, Optional, Tuple


def candidate_calibrator_paths(calibration_path: Optional[str]) -> List[str]:
    """Candidate LRCalibrator files for calibration_path, in priority order.

    Single source of truth for calibrator path resolution (B-098 / review
    finding B-102): historically each loader resolved the path its own way —
    H28 looked only for '<name>_isotonic.json' (a file no tool in this repo
    produces; scripts/run_calibration.py writes 'calibrated_lr.json') while
    LikelihoodEngine loaded the bare path — so the same calibration_path
    could calibrate one layer and leave another in FALLBACK. The legacy
    isotonic variant is kept as first candidate for backward compatibility;
    the path itself is the candidate that makes the documented flow work.
    """
    if not calibration_path:
        return []
    from pathlib import Path

    p = Path(calibration_path)
    variant = str(p.with_name(p.stem + "_isotonic" + p.suffix))
    return [variant, calibration_path]


# ---------------------------------------------------------------------------
# Platt Scaling manual — fallback sin sklearn
# ---------------------------------------------------------------------------

def _sigmoid(x: float) -> float:
    """Sigmoid estable numéricamente."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    exp_x = math.exp(x)
    return exp_x / (1.0 + exp_x)


def _fit_platt_scaling(
    z_scores: List[float],
    labels: List[int],
    lr_rate: float = 0.01,
    n_iter: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """
    Ajusta un modelo logístico simple: P(fab) = sigmoid(A * z + B)
    por descenso de gradiente.

    Retorna: (A, B) — parámetros del modelo.
    """
    import random
    rng = random.Random(seed)

    A = rng.gauss(0.5, 0.1)
    B = rng.gauss(0.0, 0.1)

    for _ in range(n_iter):
        grad_A = grad_B = 0.0
        for z, y in zip(z_scores, labels):
            p = _sigmoid(A * z + B)
            err = p - y
            grad_A += err * z
            grad_B += err

        n = len(z_scores)
        A -= lr_rate * grad_A / n
        B -= lr_rate * grad_B / n

    return A, B


class PlattCalibrator:
    """
    Calibrador Platt Scaling (logistic) sin dependencias externas.
    Usado cuando sklearn no está disponible.
    """

    def __init__(self) -> None:
        self._A: float = 1.0
        self._B: float = 0.0
        self._fitted: bool = False
        self._train_hash: str = ""
        self._version: str = "PlattCalibrator-v0"

    def fit(
        self,
        authentic_z: List[float],
        fabricated_z: List[float],
        seed: int = 42,
    ) -> "PlattCalibrator":
        """
        Ajusta el calibrador con z-scores del dataset bootstrap.

        Args:
            authentic_z:  Z-scores de muestras AUTHENTIC (label=0)
            fabricated_z: Z-scores de muestras FABRICATED+ADVERSARIAL (label=1)
        """
        z_all = authentic_z + fabricated_z
        y_all = [0] * len(authentic_z) + [1] * len(fabricated_z)

        if len(set(y_all)) < 2:
            raise ValueError("El dataset de calibración necesita ambas clases (0 y 1).")

        self._A, self._B = _fit_platt_scaling(z_all, y_all, seed=seed)
        self._fitted = True
        self._train_hash = _dataset_hash(z_all, y_all)
        return self

    def calibrated_posterior(self, z_score: float) -> float:
        """
        Retorna P(fabricado | z_score) calibrada.
        """
        if not self._fitted:
            raise RuntimeError("PlattCalibrator: llamar fit() antes de calibrated_posterior().")
        if not math.isfinite(z_score):
            return 0.5
        z_cap = max(min(z_score, 3.0), -3.0)
        return _sigmoid(self._A * z_cap + self._B)

    def calibrated_log_lr(self, z_score: float) -> float:
        """
        Retorna log(LR) calibrado.
        LR = P(z|H1) / P(z|H0) = p / (1-p) donde p = calibrated_posterior.
        """
        p = self.calibrated_posterior(z_score)
        p = max(1e-9, min(1 - 1e-9, p))
        return math.log(p / (1.0 - p))

    def to_dict(self) -> Dict:
        return {
            "version": self._version,
            "type": "platt_scaling",
            "A": self._A,
            "B": self._B,
            "fitted": self._fitted,
            "train_hash": self._train_hash,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "PlattCalibrator":
        cal = cls()
        cal._A = d["A"]
        cal._B = d["B"]
        cal._fitted = d.get("fitted", True)
        cal._train_hash = d.get("train_hash", "")
        return cal


# ---------------------------------------------------------------------------
# SklearnCalibrator — preferido si sklearn disponible
# ---------------------------------------------------------------------------

class SklearnCalibrator:
    """
    Calibrador usando sklearn.calibration.CalibratedClassifierCV o
    LogisticRegression directamente sobre z-scores.

    Más robusto que Platt manual para distribuciones no lineales.
    """

    def __init__(self) -> None:
        self._model = None
        self._coef: Optional[float] = None
        self._intercept: Optional[float] = None
        self._fitted: bool = False
        self._train_hash: str = ""
        self._version: str = "SklearnLogisticCalibrator-v0"
        self._method: str = "logistic"

    def fit(
        self,
        authentic_z: List[float],
        fabricated_z: List[float],
        seed: int = 42,
    ) -> "SklearnCalibrator":
        try:
            from sklearn.linear_model import LogisticRegression
            import numpy as np

            z_all = authentic_z + fabricated_z
            y_all = [0] * len(authentic_z) + [1] * len(fabricated_z)

            X = np.array(z_all).reshape(-1, 1)
            y = np.array(y_all)

            self._model = LogisticRegression(
                C=1.0, solver="lbfgs", random_state=seed, max_iter=1000
            )
            self._model.fit(X, y)
            self._fitted = True
            self._train_hash = _dataset_hash(z_all, y_all)
            self._method = "logistic_sklearn"
            return self

        except ImportError:
            raise ImportError(
                "sklearn no disponible. Usar PlattCalibrator como fallback."
            )

    def calibrated_posterior(self, z_score: float) -> float:
        if not self._fitted:
            raise RuntimeError("SklearnCalibrator: llamar fit() primero o cargar via from_dict().")
        z_cap = max(min(z_score, 3.0), -3.0)
        if self._model is not None:
            import numpy as np
            X = np.array([[z_cap]])
            return float(self._model.predict_proba(X)[0, 1])
        if self._coef is not None and self._intercept is not None:
            # Reconstruido desde disco: forma cerrada equivalente — regresion
            # logistica de 1 feature es matematicamente sigmoid(coef*z + intercept).
            # No requiere reinstanciar un objeto sklearn ni importar sklearn aqui.
            return _sigmoid(self._coef * z_cap + self._intercept)
        raise RuntimeError(
            "SklearnCalibrator: estado inconsistente — fitted=True pero sin "
            "_model ni (_coef, _intercept). No se debe continuar."
        )

    def calibrated_log_lr(self, z_score: float) -> float:
        p = self.calibrated_posterior(z_score)
        p = max(1e-9, min(1 - 1e-9, p))
        return math.log(p / (1.0 - p))

    def to_dict(self) -> Dict:
        # Invariante explicito (P1, auditoria 2026-06-22): exactamente una de las
        # dos fuentes debe existir. No se asume ninguna via ternario silencioso.
        if self._model is not None:
            coef = float(self._model.coef_[0][0])
            intercept = float(self._model.intercept_[0])
        elif self._coef is not None and self._intercept is not None:
            coef, intercept = self._coef, self._intercept
        else:
            raise RuntimeError(
                "SklearnCalibrator.to_dict: sin _model ni (_coef, _intercept) — "
                "no hay nada que serializar (calibrador no ajustado)."
            )
        return {
            "version": self._version,
            "type": self._method,
            "fitted": self._fitted,
            "train_hash": self._train_hash,
            "coef": coef,
            "intercept": intercept,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "SklearnCalibrator":
        """
        Reconstruye sin reinstanciar un objeto sklearn (evita romperse si la
        version de sklearn que carga difiere de la que entreno).
        """
        if "coef" not in d or "intercept" not in d:
            raise ValueError(
                "SklearnCalibrator.from_dict: faltan 'coef'/'intercept' en el JSON. "
                "Este archivo fue guardado con la version anterior del codigo "
                "(bug de serializacion, corregido 2026-06-22) y no puede "
                "reconstruirse sin perder la calibracion. Re-ejecutar "
                "run_calibration.py para regenerarlo."
            )
        coef, intercept = d["coef"], d["intercept"]
        if not isinstance(coef, (int, float)) or isinstance(coef, bool) \
                or not isinstance(intercept, (int, float)) or isinstance(intercept, bool):
            raise ValueError(
                f"SklearnCalibrator.from_dict: 'coef'/'intercept' deben ser numericos. "
                f"Recibido coef={coef!r} ({type(coef).__name__}), "
                f"intercept={intercept!r} ({type(intercept).__name__})."
            )
        if not math.isfinite(coef) or not math.isfinite(intercept):
            raise ValueError(
                f"SklearnCalibrator.from_dict: 'coef'/'intercept' no finitos "
                f"(coef={coef}, intercept={intercept}) — JSON corrupto o "
                "calibrador ajustado sobre datos degenerados."
            )
        cal = cls()
        cal._coef = float(coef)
        cal._intercept = float(intercept)
        cal._fitted = d.get("fitted", True)
        cal._train_hash = d.get("train_hash", "")
        cal._method = d.get("type", "logistic_sklearn")
        cal._model = None
        return cal


# ---------------------------------------------------------------------------
# LRCalibrator — fachada unificada
# ---------------------------------------------------------------------------

class LRCalibrator:
    """
    Fachada unificada. Selecciona automáticamente sklearn o Platt según disponibilidad.

    Uso típico:
        cal = LRCalibrator()
        cal.fit(authentic_zs, fabricated_zs)
        log_lr = cal.calibrated_log_lr(z=2.3)

    Para persistencia entre sesiones:
        cal.save("calibrator_v1.json")
        cal2 = LRCalibrator.load("calibrator_v1.json")
    """

    def __init__(self) -> None:
        self._backend: Optional[object] = None
        self._fitted: bool = False
        self._meta: Dict = {}

    def fit(
        self,
        authentic_z: List[float],
        fabricated_z: List[float],
        seed: int = 42,
    ) -> "LRCalibrator":
        """
        Ajusta con z-scores del dataset bootstrap.
        Intenta sklearn primero; fallback a Platt manual.
        """
        if not authentic_z or not fabricated_z:
            raise ValueError("Se requieren z-scores de ambas clases para calibrar.")

        try:
            backend = SklearnCalibrator()
            backend.fit(authentic_z, fabricated_z, seed=seed)
            self._backend = backend
            self._meta["backend"] = "sklearn_logistic"
        except ImportError:
            backend = PlattCalibrator()
            backend.fit(authentic_z, fabricated_z, seed=seed)
            self._backend = backend
            self._meta["backend"] = "platt_manual"

        self._fitted = True
        self._meta.update({
            "fit_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "n_authentic": len(authentic_z),
            "n_fabricated": len(fabricated_z),
            "authentic_z_median": round(statistics.median(authentic_z), 4),
            "fabricated_z_median": round(statistics.median(fabricated_z), 4),
            "version": "LRCalibrator-v0",
        })
        return self

    def calibrated_log_lr(self, z_score: float) -> float:
        """
        Retorna log(LR) calibrado para un z_score dado.
        Usado por LikelihoodEngine en reemplazo de z²/2.
        """
        if self._fitted and self._backend is None:
            raise RuntimeError(
                "LRCalibrator: estado inconsistente — fitted=True pero backend=None. "
                "load() no pudo reconstruir el backend serializado. No continuar "
                "con el placeholder sin calibrar silenciosamente."
            )
        if not self._fitted:
            # Fallback intencional al placeholder z²/2 si nunca se calibro
            z_cap = max(min(z_score, 3.0), -3.0)
            return (z_cap ** 2) / 2.0
        return self._backend.calibrated_log_lr(z_score)  # type: ignore

    def calibrated_posterior(self, z_score: float) -> float:
        """P(fabricado | z_score)"""
        if self._fitted and self._backend is None:
            raise RuntimeError(
                "LRCalibrator: estado inconsistente — fitted=True pero backend=None. "
                "load() no pudo reconstruir el backend serializado. No continuar "
                "con el placeholder sin calibrar silenciosamente."
            )
        if not self._fitted:
            z_cap = max(min(z_score, 3.0), -3.0)
            lr = math.exp((z_cap ** 2) / 2.0)
            return lr / (1.0 + lr)
        return self._backend.calibrated_posterior(z_score)  # type: ignore

    def reliability_curve(
        self, z_scores: List[float], labels: List[int], n_bins: int = 10
    ) -> Dict:
        """
        Curva de calibración (reliability curve) para reporte Daubert.
        Muestra si las probabilidades predichas son honestas.
        """
        if not z_scores:
            return {"bins": [], "mean_predicted": [], "fraction_positive": []}

        posteriors = [self.calibrated_posterior(z) for z in z_scores]

        bins = [i / n_bins for i in range(n_bins + 1)]
        mean_pred = []
        frac_pos = []

        for i in range(n_bins):
            lo, hi = bins[i], bins[i + 1]
            in_bin = [
                (posteriors[j], labels[j])
                for j in range(len(posteriors))
                if lo <= posteriors[j] < hi
            ]
            if in_bin:
                mean_pred.append(round(statistics.mean(p for p, _ in in_bin), 4))
                frac_pos.append(round(statistics.mean(y for _, y in in_bin), 4))
            else:
                mean_pred.append(None)
                frac_pos.append(None)

        return {
            "bins": [round(b, 2) for b in bins[:-1]],
            "mean_predicted": mean_pred,
            "fraction_positive": frac_pos,
            "calibration_error": self._ece(posteriors, labels, n_bins),
        }

    @staticmethod
    def _ece(posteriors: List[float], labels: List[int], n_bins: int = 10) -> float:
        """Expected Calibration Error — métrica de honestidad probabilística."""
        n = len(posteriors)
        if n == 0:
            return 1.0
        ece = 0.0
        bin_size = 1.0 / n_bins
        for i in range(n_bins):
            lo = i * bin_size
            hi = (i + 1) * bin_size
            in_bin = [(posteriors[j], labels[j]) for j in range(n) if lo <= posteriors[j] < hi]
            if in_bin:
                acc = statistics.mean(y for _, y in in_bin)
                conf = statistics.mean(p for p, _ in in_bin)
                ece += (len(in_bin) / n) * abs(acc - conf)
        return round(ece, 4)

    def save(self, path: str) -> None:
        """Serializa el calibrador para persistencia entre sesiones."""
        data = {
            "meta": self._meta,
            "fitted": self._fitted,
            "backend": self._backend.to_dict() if self._backend else None,  # type: ignore
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str, expected_train_hash: str = "") -> "LRCalibrator":
        """
        Load a serialized calibrator from disk.

        Args:
            path: path to the JSON file produced by save().
            expected_train_hash: if non-empty, the train_hash stored in
                the file must match this value exactly. Raises ValueError
                if they differ — this means the calibrator was trained on
                a different dataset than the one currently in use.
                If empty (default), no validation is performed and the
                calibrator loads silently as before (backward compatible).
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cal = cls()
        cal._meta = data.get("meta", {})
        cal._fitted = data.get("fitted", False)
        backend_data = data.get("backend")
        if backend_data:
            btype = backend_data.get("type", "platt_scaling")
            if btype.startswith("platt"):
                cal._backend = PlattCalibrator.from_dict(backend_data)
            elif btype.startswith("logistic"):
                cal._backend = SklearnCalibrator.from_dict(backend_data)
            else:
                raise ValueError(
                    f"LRCalibrator.load: tipo de backend desconocido '{btype}'. "
                    "Antes este caso dejaba _backend=None y caia silenciosamente "
                    "al placeholder sin calibrar — ahora se aborta explicitamente."
                )
        if expected_train_hash:
            stored_hash = (cal._backend._train_hash if cal._backend else "")
            if stored_hash != expected_train_hash:
                raise ValueError(
                    f"LRCalibrator.load: train_hash mismatch. "
                    f"Stored: '{stored_hash}', expected: '{expected_train_hash}'. "
                    "The calibrator was trained on a different dataset. "
                    "Re-run scripts/run_calibration.py to regenerate."
                )
        return cal

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def meta(self) -> Dict:
        return dict(self._meta)


# ---------------------------------------------------------------------------
# Helper — hash reproducible del dataset de entrenamiento
# ---------------------------------------------------------------------------

def _dataset_hash(z_scores: List[float], labels: List[int]) -> str:
    """Hash SHA-256 del dataset de calibración para trazabilidad Daubert.
    P1-15: usar Decimal exacto — sin round() para evitar colisiones de hash.
    """
    from decimal import Decimal
    payload = json.dumps(
        {"z": [str(Decimal(str(z))) for z in z_scores], "y": labels},
        sort_keys=True
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Función de conveniencia: calibrar desde validate_dataset directamente
# ---------------------------------------------------------------------------

def build_calibrator_from_bootstrap(
    samples: List[Dict],
    seed: int = 42,
    sda_baseline_median: Optional[float] = None,
    sda_baseline_mad: Optional[float] = None,
) -> LRCalibrator:
    """
    Construye y ajusta un LRCalibrator a partir de las muestras del dataset bootstrap.

    Extrae z-scores de SDA (señal principal) separados por clase.
    """
    import math as _math

    if sda_baseline_median is None:
        authentic = [s for s in samples if s["ground_truth"] == "AUTHENTIC"]
        vals = [s["sda_sigma_max"] for s in authentic if _math.isfinite(s["sda_sigma_max"])]
        if not vals:
            raise ValueError("No hay muestras AUTHENTIC en el bootstrap.")
        sda_baseline_median = statistics.median(vals)
        sda_baseline_mad = max(
            statistics.median([abs(v - sda_baseline_median) for v in vals]), 1e-9
        )

    def to_z(val: float) -> float:
        return (val - sda_baseline_median) / max(sda_baseline_mad, 1e-9)  # type: ignore

    authentic_z = [
        to_z(s["sda_sigma_max"])
        for s in samples
        if s["ground_truth"] == "AUTHENTIC" and _math.isfinite(s["sda_sigma_max"])
    ]
    fabricated_z = [
        to_z(s["sda_sigma_max"])
        for s in samples
        if s["ground_truth"] in ("FABRICATED", "ADVERSARIAL")
        and _math.isfinite(s["sda_sigma_max"])
    ]

    cal = LRCalibrator()
    cal.fit(authentic_z, fabricated_z, seed=seed)
    return cal
