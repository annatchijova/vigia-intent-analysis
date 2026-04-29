"""
vigia/core/signal_contract.py
─────────────────────────────────────────────────────────────────────────────
Contrato de señales unificado para VIGÍA.

MANDATORIO: Toda herramienta forense (SDA, CLI, GCI, ACP) DEBE retornar
un SignalOutput.  El LikelihoodEngine consume EXCLUSIVAMENTE este contrato.

Sin este contrato → el LikelihoodEngine no puede operar → Daubert indefendible.

Decisión de arquitectura (consenso ChatGPT / Gemini / DeepSeek / Claude):
    EVIDENCE LAYER  → determinístico, sin LLM, retorna SignalOutput
    INFERENCE LAYER → LikelihoodEngine consume SignalOutput
    REPORT LAYER    → LLM recibe resultado numérico, genera narrativa ENFSI

Este módulo no tiene dependencias de terceros más allá de la stdlib.
Pydantic V2 se usa si está disponible; fallback a dataclass puro.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Intentamos Pydantic V2; si no está, usamos dataclass puro.
# Mismo patrón que vigia/config.py (canónico).
# ---------------------------------------------------------------------------
try:
    from pydantic import BaseModel, Field, field_validator

    class SignalOutput(BaseModel):
        """
        Objeto de transferencia entre la capa de evidencia y la de inferencia.

        Campos:
            tool_name   : nombre de la herramienta que emitió la señal
                          (ej: "SDA", "CLI", "GCI", "ACP")
            signal_id   : identificador único de la instancia de análisis
                          (ej: "SDA-<sha256[:8]>-<epoch_ms>")
            value       : valor bruto del indicador (escala propia de la herramienta)
            z_score     : desviación respecto al baseline AUTHENTIC.
                          DEBE calcularse como (value - baseline_mean) / baseline_MAD.
                          El LLM nunca participa en este cálculo.
            confidence  : confianza interna de la herramienta [0.0, 1.0].
                          Refleja calidad de la señal, no probabilidad de fraude.
            metadata    : payload opcional para trazabilidad (Daubert).
                          Incluir: emitter_type, generator_version, transform_chain.
        """
        tool_name: str
        signal_id: str
        value: float
        z_score: float
        confidence: float = Field(default=1.0, ge=0.0, le=1.0)
        metadata: Optional[Dict[str, Any]] = None

        @field_validator("confidence")
        @classmethod
        def _clamp_confidence(cls, v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        @field_validator("z_score", "value")
        @classmethod
        def _must_be_finite(cls, v: float) -> float:
            if not math.isfinite(v):
                raise ValueError(f"SignalOutput requiere valores finitos; recibido: {v}")
            return float(v)

    _PYDANTIC_AVAILABLE = True

except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class SignalOutput:  # type: ignore[no-redef]
        tool_name: str
        signal_id: str
        value: float
        z_score: float
        confidence: float = 1.0
        metadata: Optional[Dict[str, Any]] = None

        def __post_init__(self) -> None:
            if not math.isfinite(self.value):
                raise ValueError(f"value debe ser finito; recibido: {self.value}")
            if not math.isfinite(self.z_score):
                raise ValueError(f"z_score debe ser finito; recibido: {self.z_score}")
            self.confidence = max(0.0, min(1.0, float(self.confidence)))

    _PYDANTIC_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helper: generador de signal_id reproducible
# ---------------------------------------------------------------------------

def _make_signal_id(tool_name: str, discriminator: str = "") -> str:
    """
    Genera un ID único para la señal.
    Formato: <TOOL>-<discriminator[:8]>-<epoch_ms>
    Trazable pero sin datos sensibles.
    """
    epoch_ms = int(time.time() * 1000)
    disc = (discriminator[:8] if discriminator else "00000000")
    return f"{tool_name.upper()}-{disc}-{epoch_ms}"


# ---------------------------------------------------------------------------
# SignalBuilder: factory method para reducir boilerplate en cada herramienta
# ---------------------------------------------------------------------------

class SignalBuilder:
    """
    Factory para construir SignalOutput con validaciones defensivas.

    Uso:
        sig = SignalBuilder.from_raw(
            tool_name="SDA",
            value=nv_ratio,
            baseline_mean=baseline.nv_ratio_mean,
            baseline_mad=baseline.nv_ratio_mad,
            confidence=0.9,
            metadata={"emitter_type": "COURT", "generator_version": "v2.0"},
        )

    La instancia se puede pasar directamente al LikelihoodEngine.
    """

    @staticmethod
    def from_raw(
        tool_name: str,
        value: float,
        baseline_mean: float,
        baseline_mad: float,
        confidence: float = 1.0,
        discriminator: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        is_pre_normalized: bool = False,
    ) -> SignalOutput:
        """
        Construye SignalOutput desde un valor crudo o ya normalizado.

        is_pre_normalized=False (default):
            z = (value - baseline_mean) / MAD
            Usar cuando value es una métrica bruta (ratio, índice, densidad).

        is_pre_normalized=True:
            z = value  — se pasa directo sin recalcular.
            Usar cuando value YA es un z-score (ej: sigma_max de SDA,
            max_zscore de ACP). Evita la doble normalización que sesga el LR.

        Trazabilidad Daubert: el flag queda registrado en metadata.
        """
        if not math.isfinite(value) or not math.isfinite(baseline_mean):
            raise ValueError(
                f"[SignalBuilder] Valores no finitos: value={value}, "
                f"baseline_mean={baseline_mean}"
            )

        if is_pre_normalized:
            # value ya es z-score — no recalcular contra baseline
            if not math.isfinite(value):
                raise ValueError(
                    f"[SignalBuilder] is_pre_normalized=True pero value no es finito: {value}"
                )
            z = value
        else:
            safe_mad = max(abs(baseline_mad), 1e-9)
            z = (value - baseline_mean) / safe_mad

        sig_id = _make_signal_id(tool_name, discriminator)
        meta = dict(metadata or {})
        meta["is_pre_normalized"] = is_pre_normalized

        return SignalOutput(
            tool_name=tool_name,
            signal_id=sig_id,
            value=value,
            z_score=z,
            confidence=confidence,
            metadata=meta,
        )

    @staticmethod
    def from_z_score(
        tool_name: str,
        value: float,
        z_score: float,
        confidence: float = 1.0,
        discriminator: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SignalOutput:
        """
        Para herramientas que ya calculan z_score internamente (SDA, CLI legacy).
        Envuelve el resultado en el contrato sin re-calcular.
        """
        sig_id = _make_signal_id(tool_name, discriminator)
        return SignalOutput(
            tool_name=tool_name,
            signal_id=sig_id,
            value=value,
            z_score=z_score,
            confidence=confidence,
            metadata=metadata or {},
        )


# ---------------------------------------------------------------------------
# Escala ENFSI — usada por REPORT LAYER para traducir LR a lenguaje forense
# ---------------------------------------------------------------------------

ENFSI_SCALE = [
    (10_000,  "EXTREMADAMENTE FUERTE — Evidencia concluyente bajo estándar ENFSI"),
    (1_000,   "MUY FUERTE — Alto soporte para hipótesis de fabricación"),
    (100,     "FUERTE — Soporte sustancial, requiere corroboración"),
    (10,      "MODERADA — Indicios consistentes, insuficiente de forma aislada"),
    (1,       "DÉBIL / NEUTRA — Evidencia no discriminante"),
]


def enfsi_label(lr: float) -> str:
    """Traduce un Likelihood Ratio a su categoría ENFSI verbal."""
    if not math.isfinite(lr) or lr <= 0:
        return "NO CALCULABLE — LR inválido"
    for threshold, label in ENFSI_SCALE:
        if lr >= threshold:
            return label
    return "DÉBIL / NEUTRA — Evidencia no discriminante"
