# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# vigia/report/report_builder.py

import base64
import io
import json
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Helper: encode matplotlib figure as base64 (embebible en HTML/JSON)
# ---------------------------------------------------------------------------

def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ---------------------------------------------------------------------------
# Plot builders
# ---------------------------------------------------------------------------

def build_roc_plot(fpr, tpr, auc: float) -> str:
    fig = plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    return _fig_to_base64(fig)


def build_calibration_plot(prob_true, prob_pred) -> str:
    fig = plt.figure()
    plt.plot(prob_pred, prob_true, marker="o")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Frequency")
    plt.title("Calibration Curve")
    return _fig_to_base64(fig)


# ---------------------------------------------------------------------------
# Narrativa ENFSI (controlada, no creativa)
# ---------------------------------------------------------------------------

def build_enfsi_narrative(lr: float, label: str) -> str:
    return (
        f"El análisis probabilístico basado en modelos estadísticos calibrados "
        f"produce un Likelihood Ratio (LR) de {lr:.2f}. "
        f"De acuerdo con la escala ENFSI, esto corresponde a un nivel de evidencia: "
        f"'{label}'. "
        f"Este resultado debe interpretarse en conjunto con el resto de la evidencia del caso."
    )


# ---------------------------------------------------------------------------
# Report Builder
# ---------------------------------------------------------------------------

def build_report(
    case_result: Dict[str, Any],
    evaluation_metrics: Dict[str, Any],
    model_metadata: Dict[str, Any],
    include_plots: bool = True,
) -> Dict[str, Any]:
    """
    Construye un reporte pericial completo.

    case_result:
        Output de run_full_pipeline()

    evaluation_metrics:
        Output de evaluate_model + calibration + bootstrap

    model_metadata:
        Metadata de calibración KDE + covarianza NLP
    """

    # -----------------------------------------------------------------------
    # Extraer métricas
    # -----------------------------------------------------------------------

    auc = evaluation_metrics.get("auc")
    brier = evaluation_metrics.get("brier_score")
    ece = evaluation_metrics.get("ece")

    auc_ci = evaluation_metrics.get("auc_ci", {})
    fpr = evaluation_metrics.get("fpr")
    tpr = evaluation_metrics.get("tpr")

    prob_true = evaluation_metrics.get("prob_true")
    prob_pred = evaluation_metrics.get("prob_pred")

    # -----------------------------------------------------------------------
    # Gráficos
    # -----------------------------------------------------------------------

    roc_plot = None
    calibration_plot = None

    if include_plots and fpr is not None:
        roc_plot = build_roc_plot(fpr, tpr, auc)

    if include_plots and prob_true is not None:
        calibration_plot = build_calibration_plot(prob_true, prob_pred)

    # -----------------------------------------------------------------------
    # Resultado del caso
    # -----------------------------------------------------------------------

    lr = case_result["lr_record"]["lr"]
    posterior = case_result["posterior_probability"]
    enfsi_label = case_result["enfsi_label"]

    narrative = build_enfsi_narrative(lr, enfsi_label)

    # -----------------------------------------------------------------------
    # Construcción del reporte
    # -----------------------------------------------------------------------

    report = {
        "report_version": "v1.0",
        "case": {
            "document_id": case_result.get("document_id"),
            "analysis_timestamp": case_result.get("baseline", {}).get("version"),
        },

        # -------------------------------------------------------------------
        # RESULTADO FORENSE
        # -------------------------------------------------------------------
        "forensic_result": {
            "likelihood_ratio": lr,
            "posterior_probability": posterior,
            "enfsi_label": enfsi_label,
            "narrative": narrative,
        },

        # -------------------------------------------------------------------
        # MÉTRICAS DEL MODELO
        # -------------------------------------------------------------------
        "model_performance": {
            "auc": auc,
            "auc_confidence_interval": auc_ci,
            "brier_score": brier,
            "expected_calibration_error": ece,
        },

        # -------------------------------------------------------------------
        # TRAZABILIDAD (DAUBERT)
        # -------------------------------------------------------------------
        "model_traceability": {
            "dataset_hash": model_metadata.get("dataset_hash"),
            "calibration_date": model_metadata.get("calibration_date"),
            "tools_calibrated": model_metadata.get("tools_calibrated"),
            "bandwidths": model_metadata.get("bandwidths"),
            "covariance_used": model_metadata.get("covariance_used", False),
        },

        # -------------------------------------------------------------------
        # DETALLE DE SEÑALES
        # -------------------------------------------------------------------
        "signals": case_result.get("signals"),

        # -------------------------------------------------------------------
        # GRÁFICOS (BASE64)
        # -------------------------------------------------------------------
        "plots": {
            "roc_curve": roc_plot,
            "calibration_curve": calibration_plot,
        },

        # -------------------------------------------------------------------
        # LIMITACIONES
        # -------------------------------------------------------------------
        "limitations": [
            "El modelo está calibrado sobre dataset bootstrap (no corpus real).",
            "Se asume independencia entre clusters (NLP vs TEMPORAL).",
            "La covarianza NLP se estima con shrinkage (Ledoit-Wolf).",
            "Las probabilidades pueden estar sujetas a recalibración adicional.",
        ],
    }

    return report
