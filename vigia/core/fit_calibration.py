"""
scripts/fit_calibration.py
─────────────────────────────────────────────────────────────────────────────
Calibracion Empirica del LikelihoodEngine — VIGIA Forensic Suite
Grado Gubernamental / Daubert-compliant

PRODUCE:
    models/calibrated_lr_models.pkl
        KDE por herramienta (H0=AUTHENTIC, H1=FABRICATED)
        Bandwidth seleccionado por GridSearchCV — no hardcodeado

    models/nlp_covariance.pkl
        Covarianza Ledoit-Wolf regularizada para cluster NLP
        Tools: SDA, ACP, CLI, ROI
        Campos: cov_h0, cov_h1, precision_h0, precision_h1, mean_h0, mean_h1

    models/calibration_metadata.json
        Trazabilidad completa: dataset_hash, bandwidths, n_samples, shrinkage

DEFENSA DAUBERT:
    1. El bandwidth NO es 0.3 hardcodeado.
       Es seleccionado por GridSearchCV (neg_log_loss en CV-5) sobre el
       dataset de calibracion. Justificacion: "bandwidth optimo por
       validacion cruzada sobre dataset bootstrap documentado."

    2. La covarianza NO es identidad.
       Es Ledoit-Wolf regularizada: combina covarianza muestral con
       estimador diagonal para matriz bien condicionada con pocas muestras.
       Permite LR multivariado que evita doble conteo de senales NLP
       correlacionadas (SDA + CLI).

    3. El dataset_hash es reproducible.
       SHA-256 del dataset en orden canonico (sort_keys=True).
       Permite al perito contrario verificar que los modelos
       corresponden a un dataset especifico.

FORMATO DEL DATASET:
    [
        {
            "ground_truth": "AUTHENTIC" | "FABRICATED" | "ADVERSARIAL",
            "z_scores": {
                "SDA": float,
                "ACP": float,
                "CLI": float,
                "ROI": float,
                "GCI": float,
                "DGPI": float
            }
        },
        ...
    ]

USO:
    # Con dataset real:
    python3 scripts/fit_calibration.py --dataset data/corpus.json

    # Con dataset sintetico para testing:
    python3 scripts/fit_calibration.py --generate-synthetic --n 180

    # Solo Ledoit-Wolf:
    python3 scripts/fit_calibration.py --dataset data/corpus.json --kde-only=false
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import pickle
import random
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Patron de raiz dinamica
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

# ---------------------------------------------------------------------------
# Dependencias — verificacion temprana
# ---------------------------------------------------------------------------
try:
    import numpy as np
except ImportError as _e:
    raise ImportError(
        "numpy is required for fit_calibration: pip install numpy"
    ) from _e

try:
    from sklearn.neighbors import KernelDensity
    from sklearn.model_selection import GridSearchCV, cross_val_score
    from sklearn.covariance import LedoitWolf
    from sklearn.preprocessing import StandardScaler
except ImportError as _e:
    raise ImportError(
        "scikit-learn is required for fit_calibration: pip install scikit-learn"
    ) from _e


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SCRIPT_VERSION = "2.0.0"

# Cluster NLP: herramientas con correlacion conocida entre si
TOOLS_NLP = ["SDA", "ACP", "CLI", "ROI"]
TOOLS_TEMPORAL = ["GCI", "DGPI"]
ALL_TOOLS = TOOLS_NLP + TOOLS_TEMPORAL

MIN_SAMPLES = 10       # minimo para KDE defendible
CV_FOLDS = 5           # folds para GridSearchCV

# Grid de bandwidth: 0.01 a 10.0 en escala logaritmica
# Justificacion: rango cubre desde KDE muy ajustado (0.01) hasta muy suavizado (10)
BANDWIDTH_GRID = np.logspace(-2, 1, 25).tolist()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def dataset_hash(samples: List[Dict]) -> str:
    """SHA-256 canonico del dataset para trazabilidad Daubert."""
    canonical = [
        {
            "gt": s.get("ground_truth", ""),
            "z":  {k: round(float(v), 6) for k, v in sorted(s.get("z_scores", {}).items())}
        }
        for s in samples
    ]
    payload = json.dumps(canonical, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def partition_by_hypothesis(
    samples: List[Dict],
    tool: str,
) -> Tuple[List[float], List[float]]:
    """
    Separa z_scores de una herramienta por hipotesis:
        H0: AUTHENTIC
        H1: FABRICATED + ADVERSARIAL

    Retorna: (z_h0, z_h1)
    """
    z_h0, z_h1 = [], []
    for s in samples:
        z = s.get("z_scores", {}).get(tool)
        if z is None:
            continue
        gt = s.get("ground_truth", "").upper()
        if gt == "AUTHENTIC":
            z_h0.append(float(z))
        elif gt in ("FABRICATED", "ADVERSARIAL"):
            z_h1.append(float(z))
    return z_h0, z_h1


def validate_dataset(samples: List[Dict]) -> Tuple[bool, List[str]]:
    """Valida formato del dataset. Retorna (is_valid, errores)."""
    errors = []
    if not samples:
        return False, ["Dataset vacio"]

    valid_gt = {"AUTHENTIC", "FABRICATED", "ADVERSARIAL"}
    for i, s in enumerate(samples[:10]):
        gt = s.get("ground_truth", "").upper()
        if gt not in valid_gt:
            errors.append(f"Muestra {i}: ground_truth invalido '{gt}'")
        if not isinstance(s.get("z_scores"), dict):
            errors.append(f"Muestra {i}: z_scores debe ser dict")

    n_auth = sum(1 for s in samples if s.get("ground_truth", "").upper() == "AUTHENTIC")
    n_fab  = sum(1 for s in samples if s.get("ground_truth", "").upper() in ("FABRICATED", "ADVERSARIAL"))

    if n_auth < MIN_SAMPLES:
        errors.append(f"Pocas muestras AUTHENTIC: {n_auth} < {MIN_SAMPLES}")
    if n_fab < MIN_SAMPLES:
        errors.append(f"Pocas muestras FABRICATED: {n_fab} < {MIN_SAMPLES}")

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# KDE calibrado con GridSearchCV
# ---------------------------------------------------------------------------

def fit_kde(
    z_values: List[float],
    bandwidth_grid: Optional[List[float]] = None,
) -> Tuple[KernelDensity, float, Dict[str, Any]]:
    """
    Ajusta KDE con seleccion de bandwidth por GridSearchCV.

    JUSTIFICACION DAUBERT:
        El bandwidth es el parametro critico del KDE.
        Si lo fijamos en 0.3, el perito contrario puede preguntar:
        "¿Por que 0.3? ¿Por que no 0.1 o 1.0?"
        Sin respuesta, el modelo cae.

        Con GridSearchCV (cross-validation leave-k-out):
        "El bandwidth fue seleccionado maximizando la log-likelihood
        del KDE sobre el dataset de calibracion por validacion cruzada
        de 5 folds. Este procedimiento es reproducible y documentado."
        El modelo se sostiene.

    Retorna: (kde_fitted, best_bandwidth, diagnostics)
    """
    bw_grid = bandwidth_grid or BANDWIDTH_GRID
    z_arr = np.array(z_values).reshape(-1, 1)
    n = len(z_values)

    diagnostics: Dict[str, Any] = {"n_samples": n, "method": "GridSearchCV_CV5"}

    if n < MIN_SAMPLES:
        # Fallback conservador documentado
        bw = 0.5
        kde = KernelDensity(kernel="gaussian", bandwidth=bw)
        kde.fit(z_arr)
        diagnostics["method"] = "fixed_0.5_fallback_insufficient_samples"
        diagnostics["bandwidth"] = bw
        logger.warning("KDE fallback bandwidth=0.5 (n=%d < min=%d)", n, MIN_SAMPLES)
        return kde, bw, diagnostics

    # GridSearchCV — scoring por defecto es el scorer del estimador (log-likelihood para KDE)
    gs = GridSearchCV(
        KernelDensity(kernel="gaussian"),
        {"bandwidth": bw_grid},
        cv=min(CV_FOLDS, n),
        n_jobs=-1,
    )
    gs.fit(z_arr)

    best_bw = float(gs.best_params_["bandwidth"])
    best_score = float(gs.best_score_)

    diagnostics["bandwidth"] = best_bw
    diagnostics["best_cv_score"] = round(best_score, 6)
    diagnostics["n_candidates"] = len(bw_grid)

    logger.info("  KDE: n=%d bw=%.4f cv_score=%.4f", n, best_bw, best_score)
    return gs.best_estimator_, best_bw, diagnostics


# ---------------------------------------------------------------------------
# Calibracion KDE por herramienta
# ---------------------------------------------------------------------------

def fit_kde_per_tool(
    samples: List[Dict],
    tools: Optional[List[str]] = None,
    bandwidth_grid: Optional[List[float]] = None,
) -> Tuple[Dict, Dict]:
    """
    Ajusta un par de KDE (H0, H1) por herramienta.

    Retorna:
        models   : {tool: (kde_h0, kde_h1)}
        metadata : trazabilidad Daubert completa
    """
    tools = tools or ALL_TOOLS
    models: Dict[str, Tuple[KernelDensity, KernelDensity]] = {}
    meta: Dict[str, Any] = {
        "script_version": SCRIPT_VERSION,
        "calibration_date": datetime.now(timezone.utc).isoformat(),
        "dataset_hash": dataset_hash(samples),
        "dataset_size": len(samples),
        "tools_requested": tools,
        "tools_calibrated": [],
        "tools_skipped": [],
        "kde_diagnostics": {},
        "bandwidth_selection": "GridSearchCV_neg_log_likelihood_CV5",
        "min_samples_threshold": MIN_SAMPLES,
    }

    for tool in tools:
        z_h0, z_h1 = partition_by_hypothesis(samples, tool)

        if len(z_h0) < MIN_SAMPLES or len(z_h1) < MIN_SAMPLES:
            logger.warning(
                "Tool %s omitida: H0=%d H1=%d (min=%d)",
                tool, len(z_h0), len(z_h1), MIN_SAMPLES,
            )
            meta["tools_skipped"].append(
                {"tool": tool, "n_h0": len(z_h0), "n_h1": len(z_h1)}
            )
            continue

        logger.info("Calibrando KDE: %s (H0=%d H1=%d)", tool, len(z_h0), len(z_h1))
        kde_h0, bw_h0, diag_h0 = fit_kde(z_h0, bandwidth_grid)
        kde_h1, bw_h1, diag_h1 = fit_kde(z_h1, bandwidth_grid)

        models[tool] = (kde_h0, kde_h1)
        meta["tools_calibrated"].append(tool)
        meta["kde_diagnostics"][tool] = {
            "h0": diag_h0,
            "h1": diag_h1,
        }

    logger.info(
        "KDE: %d/%d herramientas calibradas | hash=%s",
        len(models), len(tools), meta["dataset_hash"][:16],
    )
    return models, meta


# ---------------------------------------------------------------------------
# Ledoit-Wolf: covarianza regularizada para cluster NLP
# ---------------------------------------------------------------------------

def fit_ledoit_wolf_nlp(
    samples: List[Dict],
    tools: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Ajusta matrices de covarianza Ledoit-Wolf regularizada para el cluster NLP.
    Tools por defecto: SDA, ACP, CLI, ROI.

    LEDOIT-WOLF:
        El estimador muestral de covarianza con pocas muestras es inestable
        (matriz mal condicionada, inversas numericamente inestables).
        Ledoit-Wolf combina el estimador muestral con un estimador diagonal
        usando un factor de regularizacion (shrinkage) optimo analitico.

        Resultado: matriz bien condicionada, invertible, estable.
        Justificacion Daubert: "regularizacion Ledoit-Wolf (Oracle Approximating
        Shrinkage), metodo estandar en la literatura estadistica, implementado
        en scikit-learn segun Ledoit & Wolf (2004)."

    CAMPOS PRODUCIDOS:
        cov_h0, cov_h1           : matrices de covarianza (n_tools x n_tools)
        precision_h0, precision_h1: inversas regularizadas
        mean_h0, mean_h1         : vectores de media
        shrinkage_h0, shrinkage_h1: factor de regularizacion (0=muestral, 1=diagonal)
        condition_number_h0/h1   : numero de condicion (< 1e6 es aceptable)
        tools                    : orden de las variables en las matrices
    """
    tools = tools or TOOLS_NLP
    logger.info("Ajustando Ledoit-Wolf NLP para tools: %s", tools)

    def extract_matrix(samples, hypothesis_values):
        vecs = []
        for s in samples:
            gt = s.get("ground_truth", "").upper()
            if gt not in hypothesis_values:
                continue
            z = s.get("z_scores", {})
            vec = [z.get(t) for t in tools]
            if all(v is not None for v in vec):
                vecs.append([float(v) for v in vec])
        return np.array(vecs) if vecs else np.zeros((0, len(tools)))

    mat_h0 = extract_matrix(samples, {"AUTHENTIC"})
    mat_h1 = extract_matrix(samples, {"FABRICATED", "ADVERSARIAL"})

    n_h0, n_h1 = len(mat_h0), len(mat_h1)
    logger.info("  Muestras: H0=%d H1=%d", n_h0, n_h1)

    if n_h0 < 4 or n_h1 < 4:
        raise ValueError(
            f"Insuficientes muestras para Ledoit-Wolf: H0={n_h0} H1={n_h1} (min=4)"
        )

    # Ajustar Ledoit-Wolf — shrinkage optimo analitico
    lw_h0 = LedoitWolf(assume_centered=False).fit(mat_h0)
    lw_h1 = LedoitWolf(assume_centered=False).fit(mat_h1)

    # Numero de condicion (diagnostico numerico)
    cond_h0 = float(np.linalg.cond(lw_h0.covariance_))
    cond_h1 = float(np.linalg.cond(lw_h1.covariance_))

    # Verificar que las matrices son invertibles
    try:
        inv_h0 = np.linalg.inv(lw_h0.covariance_)
        inv_h1 = np.linalg.inv(lw_h1.covariance_)
    except np.linalg.LinAlgError as e:
        raise ValueError(f"Covarianza singular tras Ledoit-Wolf: {e}")

    result = {
        # Covarianzas regularizadas
        "cov_h0": lw_h0.covariance_.tolist(),
        "cov_h1": lw_h1.covariance_.tolist(),
        # Precisiones (inversas regularizadas) — usadas directamente por LikelihoodEngine
        "precision_h0": lw_h0.precision_.tolist(),
        "precision_h1": lw_h1.precision_.tolist(),
        # Medias
        "mean_h0": lw_h0.location_.tolist(),
        "mean_h1": lw_h1.location_.tolist(),
        # Metadatos de regularizacion
        "shrinkage_h0": float(lw_h0.shrinkage_),
        "shrinkage_h1": float(lw_h1.shrinkage_),
        "condition_number_h0": round(cond_h0, 2),
        "condition_number_h1": round(cond_h1, 2),
        # Trazabilidad
        "tools": tools,
        "n_h0": n_h0,
        "n_h1": n_h1,
        "method": "LedoitWolf_sklearn",
        "sklearn_version": _get_sklearn_version(),
    }

    logger.info(
        "  Ledoit-Wolf OK | shrinkage H0=%.4f H1=%.4f | cond H0=%.1e H1=%.1e",
        result["shrinkage_h0"], result["shrinkage_h1"],
        cond_h0, cond_h1,
    )

    if cond_h0 > 1e8 or cond_h1 > 1e8:
        logger.warning(
            "  ADVERTENCIA: numero de condicion alto (H0=%.1e H1=%.1e). "
            "Considerar mas muestras.",
            cond_h0, cond_h1,
        )

    return result


def _get_sklearn_version() -> str:
    try:
        import sklearn
        return sklearn.__version__
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Dataset sintetico para testing
# ---------------------------------------------------------------------------

def generate_synthetic_dataset(
    n: int = 180,
    seed: int = 42,
    authentic_ratio: float = 0.5,
) -> List[Dict]:
    """
    Genera dataset sintetico con distribucion realista.

    H0 (AUTHENTIC): z-scores con media baja, distribucion centrada cerca de 0-1
    H1 (FABRICATED): z-scores con media alta, sesgo hacia valores positivos
        - LLM-generated: z alto en SDA y CLI (estilo uniforme, sin marcadores)
        - Adversarial:   z moderado en todo con GCI alto (patron periodico)

    ADVERTENCIA: Solo para testing. Un perito puede impugnar cualquier
    sistema calibrado exclusivamente sobre datos sinteticos.
    """
    np_rng = np.random.RandomState(seed)
    rng = random.Random(seed)
    samples = []

    n_auth = int(n * authentic_ratio)
    n_fab  = n - n_auth

    # AUTHENTIC: z-scores consistentes con texto humano
    for _ in range(n_auth):
        z = {
            "SDA":  float(np_rng.normal(0.4, 0.7)),
            "ACP":  float(np_rng.normal(0.3, 0.8)),
            "CLI":  float(np_rng.normal(0.5, 0.6)),
            "ROI":  float(np_rng.normal(0.4, 0.7)),
            "GCI":  float(np_rng.normal(0.2, 0.5)),
            "DGPI": float(np_rng.normal(0.3, 0.6)),
        }
        samples.append({"ground_truth": "AUTHENTIC", "z_scores": z})

    # FABRICATED: z-scores anomalos
    for i in range(n_fab):
        gt = "ADVERSARIAL" if i % 4 == 0 else "FABRICATED"
        if gt == "FABRICATED":
            # LLM: SDA y CLI muy altos (estilo homogeneo)
            z = {
                "SDA":  float(np_rng.normal(2.5, 0.8)),
                "ACP":  float(np_rng.normal(1.8, 0.9)),
                "CLI":  float(np_rng.normal(2.2, 0.7)),
                "ROI":  float(np_rng.normal(1.5, 0.8)),
                "GCI":  float(np_rng.normal(1.2, 0.6)),
                "DGPI": float(np_rng.normal(1.0, 0.7)),
            }
        else:
            # Adversarial: todos moderados + GCI muy alto
            z = {
                "SDA":  float(np_rng.normal(1.2, 0.6)),
                "ACP":  float(np_rng.normal(1.0, 0.7)),
                "CLI":  float(np_rng.normal(1.1, 0.6)),
                "ROI":  float(np_rng.normal(0.9, 0.7)),
                "GCI":  float(np_rng.normal(3.0, 0.8)),
                "DGPI": float(np_rng.normal(2.5, 0.9)),
            }
        samples.append({"ground_truth": gt, "z_scores": z})

    rng.shuffle(samples)
    logger.warning(
        "ADVERTENCIA: Dataset SINTETICO (%d muestras, seed=%d). "
        "NO usar para peritaje real.", n, seed,
    )
    return samples


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def save_all(
    kde_models: Dict,
    kde_metadata: Dict,
    lw_data: Optional[Dict],
    output_dir: str,
) -> Dict[str, str]:
    """Guarda todos los artefactos de calibracion."""
    os.makedirs(output_dir, exist_ok=True)
    paths: Dict[str, str] = {}

    # KDE
    kde_path = os.path.join(output_dir, "calibrated_lr_models.pkl")
    with open(kde_path, "wb") as f:
        pickle.dump({"models": kde_models, "metadata": kde_metadata}, f, protocol=4)
    paths["kde"] = kde_path
    logger.info("KDE guardado: %s", kde_path)

    # Metadata JSON legible
    meta_path = os.path.join(output_dir, "calibration_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(kde_metadata, f, sort_keys=True, indent=2, default=str)
    paths["metadata"] = meta_path
    logger.info("Metadata: %s", meta_path)

    # Ledoit-Wolf
    if lw_data:
        lw_path = os.path.join(output_dir, "nlp_covariance.pkl")
        with open(lw_path, "wb") as f:
            pickle.dump(lw_data, f, protocol=4)
        paths["covariance"] = lw_path
        logger.info("Ledoit-Wolf: %s", lw_path)

        # Ledoit-Wolf JSON legible (sin las matrices completas)
        lw_summary = {
            k: v for k, v in lw_data.items()
            if k not in ("cov_h0", "cov_h1", "precision_h0", "precision_h1")
        }
        lw_json_path = os.path.join(output_dir, "nlp_covariance_summary.json")
        with open(lw_json_path, "w", encoding="utf-8") as f:
            json.dump(lw_summary, f, sort_keys=True, indent=2, default=str)
        paths["covariance_summary"] = lw_json_path

    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calibrador empirico VIGIA — KDE + Ledoit-Wolf (Daubert-compliant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("USO:")[1].split("\n\n")[0] if "USO:" in __doc__ else "",
    )
    parser.add_argument("--dataset", "-d", help="Path al dataset JSON")
    parser.add_argument("--output", "-o", default="models", help="Directorio de salida")
    parser.add_argument("--generate-synthetic", action="store_true")
    parser.add_argument("--n", type=int, default=180)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tools", nargs="+", default=ALL_TOOLS)
    parser.add_argument("--nlp-tools", nargs="+", default=TOOLS_NLP,
                        help="Herramientas para Ledoit-Wolf (default: SDA ACP CLI ROI)")
    parser.add_argument("--skip-covariance", action="store_true",
                        help="Omitir Ledoit-Wolf")
    parser.add_argument("--skip-kde", action="store_true",
                        help="Omitir KDE")

    args = parser.parse_args()

    # Cargar dataset
    if args.generate_synthetic:
        samples = generate_synthetic_dataset(n=args.n, seed=args.seed)
    elif args.dataset:
        try:
            with open(args.dataset, "r", encoding="utf-8") as f:
                samples = json.load(f)
        except Exception as e:
            logger.error("Error al cargar dataset: %s", e)
            return 1
    else:
        logger.error("Especificar --dataset o --generate-synthetic")
        return 1

    # Validar
    is_valid, errors = validate_dataset(samples)
    if not is_valid:
        for err in errors:
            logger.error("Dataset invalido: %s", err)
        return 1

    n_auth = sum(1 for s in samples if s.get("ground_truth", "").upper() == "AUTHENTIC")
    n_fab  = sum(1 for s in samples if s.get("ground_truth", "").upper() in ("FABRICATED", "ADVERSARIAL"))
    logger.info(
        "Dataset: %d total | AUTHENTIC=%d | FABRICATED/ADVERSARIAL=%d | hash=%s",
        len(samples), n_auth, n_fab, dataset_hash(samples)[:16],
    )

    # KDE
    kde_models, kde_meta = {}, {}
    if not args.skip_kde:
        logger.info("=" * 50)
        logger.info("FASE 1: KDE por herramienta")
        logger.info("=" * 50)
        kde_models, kde_meta = fit_kde_per_tool(samples, tools=args.tools)
        if not kde_models:
            logger.error("KDE: ningun modelo producido — abortar")
            return 1
    else:
        kde_meta = {"script_version": SCRIPT_VERSION, "dataset_hash": dataset_hash(samples)}

    # Ledoit-Wolf
    lw_data = None
    if not args.skip_covariance:
        logger.info("=" * 50)
        logger.info("FASE 2: Ledoit-Wolf NLP (%s)", args.nlp_tools)
        logger.info("=" * 50)
        try:
            lw_data = fit_ledoit_wolf_nlp(samples, tools=args.nlp_tools)
        except ValueError as e:
            logger.error("Ledoit-Wolf fallido: %s — continuando sin covarianza", e)
        except Exception as e:
            logger.error("Error inesperado en Ledoit-Wolf: %s", e)

    # Guardar
    logger.info("=" * 50)
    logger.info("GUARDANDO ARTEFACTOS")
    logger.info("=" * 50)
    paths = save_all(kde_models, kde_meta, lw_data, args.output)

    logger.info("=" * 50)
    logger.info("CALIBRACION COMPLETADA")
    logger.info("  Herramientas KDE: %s", kde_meta.get("tools_calibrated", []))
    logger.info("  Ledoit-Wolf: %s", "OK" if lw_data else "OMITIDO")
    logger.info("  Archivos:")
    for k, v in paths.items():
        logger.info("    %s: %s", k, v)
    logger.info("=" * 50)

    if args.generate_synthetic:
        logger.warning("RECORDATORIO: Calibrado con datos SINTETICOS — no usar en produccion")

    return 0


if __name__ == "__main__":
    sys.exit(main())
