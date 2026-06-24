"""
vigia/core/likelihood_ratio.py
─────────────────────────────────────────────────────────────────────────────
LikelihoodEngine v0 — Motor de Inferencia Bayesiana de VIGÍA.

DISEÑO: Consenso ChatGPT / Gemini / DeepSeek / Claude (15-jun-2026 hackathon)

    PIPELINE:
        SignalOutput[] → z_clipping → log-LR → penalización por correlación
                      → LR combinado → P(fabricación) → Statement ENFSI

    GARANTÍAS:
        - Determinístico: dado el mismo input, mismo output siempre.
        - Sin LLM: el motor no llama a ningún modelo de lenguaje.
        - Trazable: cada paso queda en el ForensicRecord.
        - Auditabilidad Daubert: tasa de error medible sobre dataset bootstrap.

    FÓRMULAS:
        z_clipped   = clip(z, -3.0, 3.0)           — evita explosión de LR
        log_lr_i    = (z_clipped ** 2) / 2          — aproximación gaussiana
        mean_corr   = mean(|corr_matrix[i,j]|, i≠j) — penalización dependencia
        combined_log_lr = Σ log_lr_i * (1 - mean_corr)
        LR          = exp(combined_log_lr)
        P           = LR / (1 + LR)                 — prior neutral 0.5

    NOTA SOBRE z²/2:
        Esta transformación asume colas gaussianas.  Es un "placeholder operativo"
        (consenso ChatGPT) pendiente de reemplazar por calibración empírica
        (logistic/isotonic) una vez que tengamos el dataset bootstrap completo.
        Se documenta explícitamente para Daubert.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, enfsi_label

# Calibrador opcional — import lazy para evitar dependencia circular
try:
    from vigia.core.lr_calibration import LRCalibrator as _LRCalibrator
    _CALIBRATION_AVAILABLE = True
except ImportError:
    _LRCalibrator = None  # type: ignore
    _CALIBRATION_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constantes — justificadas para Daubert
# ---------------------------------------------------------------------------

Z_CLIP_CAP: float = 3.0
"""
z = 3 → log_lr ≈ 4.5 → LR ≈ 90 (Evidencia FUERTE ENFSI).
Sin clipping, un outlier → LR → ∞ → sistema indefendible.
(ChatGPT: "Correcto y necesario"; DeepSeek: "dejalo fijo en 3.0")
"""

TRUST_DECAY_ALGORITHMIC: float = 0.4
"""
Factor de degradación de confianza cuando GCI detecta patrón algorítmico.
Aplicado en TrustFusion: prior_trust *= 0.4.
"""

MIN_CORRELATION_SIGNALS: int = 2
"""
Mínimo de señales necesarias para calcular matriz de correlación.
Con menos señales, la penalización no aplica (factor = 1.0).
"""


# ---------------------------------------------------------------------------
# ForensicRecord — trazabilidad completa de cada inferencia
# ---------------------------------------------------------------------------

@dataclass
class ForensicRecord:
    """
    Registro completo y reproducible de una inferencia VIGÍA.
    Exportable a JSON para peritaje y shadow mode.

    Este objeto ES la cadena de custodia del razonamiento.
    """
    record_id: str
    timestamp_utc: str
    signals_in: List[Dict]
    z_scores_clipped: List[float]
    log_lrs: List[float]
    correlation_matrix: Optional[List[List[float]]]
    mean_correlation: float
    correction_factor: float
    combined_log_lr: float
    lr_combined: float
    posterior_probability: float
    enfsi_label: str
    engine_version: str = "LikelihoodEngine-v0"
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "timestamp_utc": self.timestamp_utc,
            "engine_version": self.engine_version,
            "signals_count": len(self.signals_in),
            "signals": self.signals_in,
            "z_scores_clipped": [round(z, 6) for z in self.z_scores_clipped],
            "log_lrs": [round(lr, 6) for lr in self.log_lrs],
            "correlation_matrix": self.correlation_matrix,
            "mean_correlation": round(self.mean_correlation, 6),
            "correction_factor": round(self.correction_factor, 6),
            "combined_log_lr": round(self.combined_log_lr, 6),
            "lr_combined": round(self.lr_combined, 6),
            "posterior_probability": round(self.posterior_probability, 6),
            "enfsi_label": self.enfsi_label,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def record_hash(self) -> str:
        """SHA-256 del registro serializado. Integridad para cadena de custodia."""
        raw = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# LikelihoodEngine — motor principal
# ---------------------------------------------------------------------------

class LikelihoodEngine:
    """
    Motor bayesiano determinista de VIGÍA.

    No instancia modelos de lenguaje.
    No hace llamadas de red.
    No tiene estado mutable entre llamadas (stateless por diseño).

    Uso:
        engine = LikelihoodEngine()
        record = engine.infer(signals=[sda_sig, cli_sig, gci_sig])
        print(record.enfsi_label)
        print(record.to_json())
    """

    def __init__(
        self,
        z_cap: float = Z_CLIP_CAP,
        calibrator: Optional[object] = None,
    ) -> None:
        if not (0.5 <= z_cap <= 10.0):
            raise ValueError(f"z_cap fuera de rango razonable [0.5, 10.0]: {z_cap}")
        self._z_cap = z_cap
        # calibrator: instancia de LRCalibrator.
        # Si está presente, reemplaza z²/2 por log_lr calibrado empíricamente.
        self._calibrator = calibrator

    # -----------------------------------------------------------------------
    # API pública
    # -----------------------------------------------------------------------

    def infer(
        self,
        signals: List[SignalOutput],
        correlation_matrix: Optional[List[List[float]]] = None,
    ) -> ForensicRecord:
        """
        Inferencia bayesiana sobre una lista de señales.

        Args:
            signals:            Lista de SignalOutput de las herramientas forenses.
            correlation_matrix: Matriz de correlación de Pearson entre las señales
                                (calculada sobre el dataset bootstrap AUTHENTIC).
                                Si es None, se asume independencia (sin penalización).

        Returns:
            ForensicRecord — registro completo y trazable de la inferencia.

        Raises:
            ValueError: si la lista de señales está vacía o contiene NaN/Inf.
        """
        if not signals:
            raise ValueError("LikelihoodEngine.infer() requiere al menos 1 señal.")

        self._validate_signals(signals)

        # Paso 1: Clipping de z-scores
        z_clipped = [self._clip_z(s.z_score) for s in signals]

        # Paso 2: Log-LR por señal
        # Si hay calibrador: usa log_lr calibrado empíricamente (reemplaza z²/2)
        # Si no: placeholder z²/2 (documentado para Daubert)
        if self._calibrator is not None:
            log_lrs = [self._calibrator.calibrated_log_lr(z) for z in z_clipped]  # type: ignore
            calibration_note = f"log_lr calibrado empiricamente (LRCalibrator — {getattr(self._calibrator, 'meta', {}).get('backend', 'unknown')})"
        else:
            log_lrs = [self._log_lr_from_z(z) for z in z_clipped]
            calibration_note = ("log_lr = z²/2 (placeholder gaussiano — pendiente calibración empírica. "
                                "Ver lr_calibration.py)")

        # Confidence weighting: scale each log_lr by signal's prior_trust propagated value
        for i, s in enumerate(signals):
            log_lrs[i] *= s.confidence

        # Paso 3: Penalización por correlación
        mean_corr, correction_factor = self._compute_correction(
            signals, correlation_matrix
        )

        # Paso 4: LR combinado en log-space (suma, no producto → más estable)
        combined_log_lr = sum(log_lrs) * correction_factor

        # Paso 5: LR y probabilidad posterior (prior neutral 0.5)
        lr_combined = math.exp(combined_log_lr)
        posterior = lr_combined / (1.0 + lr_combined)

        # Paso 6: Etiqueta ENFSI para el REPORT LAYER
        label = enfsi_label(lr_combined)

        # Construcción del registro de trazabilidad
        record_id = self._make_record_id(signals)
        record = ForensicRecord(
            record_id=record_id,
            timestamp_utc=_utcnow(),
            signals_in=[
                {
                    "tool_name": s.tool_name,
                    "signal_id": s.signal_id,
                    "value": s.value,
                    "z_score": s.z_score,
                    "confidence": s.confidence,
                    "metadata": s.metadata or {},
                }
                for s in signals
            ],
            z_scores_clipped=z_clipped,
            log_lrs=log_lrs,
            correlation_matrix=correlation_matrix,
            mean_correlation=mean_corr,
            correction_factor=correction_factor,
            combined_log_lr=combined_log_lr,
            lr_combined=lr_combined,
            posterior_probability=posterior,
            enfsi_label=label,
            notes=calibration_note,
        )
        return record

    # -----------------------------------------------------------------------
    # Métodos internos — no llamar desde fuera del módulo
    # -----------------------------------------------------------------------

    def _clip_z(self, z: float) -> float:
        """Clipping simétrico. Previene explosiones de LR por outliers."""
        return max(min(z, self._z_cap), -self._z_cap)

    @staticmethod
    def _log_lr_from_z(z_clipped: float) -> float:
        """
        log(LR) = z² / 2.

        Equivalente a asumir distribución gaussiana unitaria bajo H1 vs H0.
        Garantiza: simetría, crecimiento suave, interpretabilidad.
        Trabajar en log-space evita overflow numérico.
        """
        return (z_clipped ** 2) / 2.0

    def _compute_correction(
        self,
        signals: List[SignalOutput],
        correlation_matrix: Optional[List[List[float]]],
    ) -> Tuple[float, float]:
        """
        Calcula factor de corrección por dependencia entre señales.

        Si mean_corr > 0.6 → NO se pueden multiplicar LRs sin corrección
        (DeepSeek: "El modelo es forensemente inválido sin esto").

        Retorna: (mean_corr, correction_factor)
            correction_factor = 1 - mean_corr
        """
        if correlation_matrix is None or len(signals) < MIN_CORRELATION_SIGNALS:
            # Sin matriz → asumimos independencia → sin penalización
            return 0.0, 1.0

        n = len(correlation_matrix)
        if n < 2:
            return 0.0, 1.0

        # Promedio de correlaciones absolutas fuera de la diagonal
        vals = []
        for i in range(n):
            for j in range(i + 1, n):
                val = correlation_matrix[i][j]
                if math.isfinite(val):
                    vals.append(abs(val))

        if not vals:
            return 0.0, 1.0

        mean_corr = sum(vals) / len(vals)
        correction_factor = max(0.0, 1.0 - mean_corr)

        return mean_corr, correction_factor

    @staticmethod
    def _validate_signals(signals: List[SignalOutput]) -> None:
        """Validación defensiva de cada señal antes de procesarla."""
        for i, s in enumerate(signals):
            if not math.isfinite(s.z_score):
                raise ValueError(
                    f"Señal [{i}] '{s.tool_name}' tiene z_score no finito: {s.z_score}"
                )
            if not math.isfinite(s.value):
                raise ValueError(
                    f"Señal [{i}] '{s.tool_name}' tiene value no finito: {s.value}"
                )
            if not (0.0 <= s.confidence <= 1.0):
                raise ValueError(
                    f"Señal [{i}] '{s.tool_name}' tiene confidence fuera de [0,1]: {s.confidence}"
                )

    @staticmethod
    def _make_record_id(signals: List[SignalOutput]) -> str:
        """ID único del record: hash de los signal_ids concatenados."""
        concat = "|".join(s.signal_id for s in signals)
        digest = hashlib.sha256(concat.encode()).hexdigest()[:12]
        epoch_ms = int(time.time() * 1000)
        return f"LR-{digest}-{epoch_ms}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    """ISO 8601 UTC sin dependencias externas."""
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"


def compute_correlation_matrix_from_values(
    signal_values: Dict[str, List[float]],
) -> Tuple[List[str], List[List[float]]]:
    """
    Calcula la matriz de correlación de Pearson sobre valores históricos.

    Args:
        signal_values: {tool_name: [val1, val2, ...]} — dataset bootstrap.

    Returns:
        (tool_names, corr_matrix) — ordenados, para usar en LikelihoodEngine.infer().

    Usar únicamente con clase AUTHENTIC del dataset bootstrap.
    (Gemini/DeepSeek: "Los Z-scores se calibran usando SOLO la clase AUTHENTIC")
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError(
            "numpy requerido para calcular matriz de correlación. "
            "pip install numpy"
        )

    tool_names = sorted(signal_values.keys())
    matrix_data = [signal_values[t] for t in tool_names]

    # Validar longitud uniforme
    lengths = [len(v) for v in matrix_data]
    if len(set(lengths)) > 1:
        raise ValueError(
            f"Los vectores de señales tienen longitudes distintas: "
            f"{dict(zip(tool_names, lengths))}"
        )

    arr = np.array(matrix_data, dtype=float)
    corr = np.corrcoef(arr)

    # Reemplazar NaN (señales constantes) por 0
    corr = np.where(np.isfinite(corr), corr, 0.0)

    return tool_names, corr.tolist()


def build_baseline_from_authentic(
    authentic_values: Dict[str, List[float]],
) -> Dict[str, Dict[str, float]]:
    """
    Construye el baseline (media + MAD) por herramienta usando SÓLO clase AUTHENTIC.

    MAD = median(|x_i - median(x)|) — más robusto que std para distribuciones
    no-normales. (Requisito explícito del refactor GCI Engine.)

    Retorna:
        {tool_name: {"mean": float, "mad": float}}
    """
    import statistics

    baseline = {}
    for tool_name, values in authentic_values.items():
        if not values:
            raise ValueError(f"Valores vacíos para herramienta '{tool_name}'")
        med = statistics.median(values)
        mad = statistics.median([abs(v - med) for v in values])
        baseline[tool_name] = {
            "mean": med,
            "mad": max(mad, 1e-9),  # evitar división por cero
        }
    return baseline
