# -*- coding: utf-8 -*-
"""
VIGÍA — NormalizationLayer v2.0
Unifica el espacio probabilístico de todos los módulos:
- Semiótico (Fraction / int escalado)
- Geopolítico (float sigmoide)
- CAIE (float con spoofability)
- LikelihoodEngine (float posterior)

Todas las señales terminan en NormalizedSignal con:
- value: Decimal en [0,1]
- z_score: Decimal centrado en baseline AUTHENTIC (MAD crudo, sin factor 1.4826)
- confidence: Decimal en [0,1]
- baseline_version: trazabilidad de calibración
"""

from decimal import Decimal, ROUND_HALF_EVEN
from enum import Enum
from fractions import Fraction
from typing import Union, Dict, Any
from dataclasses import dataclass


class ToolName(str, Enum):
    """
    Enum estricto de nombres de herramienta forense válidos.

    Fix B (2026-05-02): tool_name NO puede ser un string arbitrario del log.
    Un atacante que controla art_type puede elegir un nombre de herramienta
    con baseline más permisivo (SDA tiene mean=-0.40, mad=0.50 — el más amplio)
    para reducir artificialmente el z_score de un artefacto sospechoso.
    Ejemplo: etiquetar un artefacto de red (GCI, z≈9.5→REJECT) como
    "process" (SDA, z≈1.8→ABSTAIN) con el mismo valor raw.

    El Enum fuerza que solo los 7 nombres con baseline conocido sean aceptados.
    Cualquier art_type desconocido cae al fallback UNKNOWN, que usa el baseline
    más conservador (mean=0.5, mad=0.1 → z-scores altos para valores extremos).
    """
    GCI          = "GCI"
    DGPI         = "DGPI"
    CAIE         = "CAIE"
    SDA          = "SDA"
    CLI          = "CLI"
    ROI          = "ROI"
    ACP          = "ACP"
    GEOPOLITICAL = "GEOPOLITICAL"
    ENTANGLEMENT = "ENTANGLEMENT"
    UNKNOWN      = "UNKNOWN"  # fallback conservador — baseline neutro


@dataclass(frozen=True)
class NormalizedSignal:
    tool_name: str
    value: Decimal        # [0,1]
    z_score: Decimal      # centrado en baseline AUTHENTIC (MAD crudo, sin factor 1.4826)
    confidence: Decimal   # [0,1]
    metadata: Dict[str, Any]
    normalization_source: str  # trazabilidad
    baseline_version: str = "bootstrap_v2"  # P2-A: versionado de baseline
    baseline_source: str = "expert_elicitation_180_samples"  # P2-A: trazabilidad


class NormalizationLayer:
    """
    Pasarela de normalización unificada.
    Ningún módulo downstream puede bypass esta capa.
    """

    _PRECISION = 28
    _ROUNDING = ROUND_HALF_EVEN

    # Baselines AUTHENTIC por herramienta (calibrados empíricamente)
    _BASELINES: Dict[str, Dict[str, Decimal]] = {
        "GCI":        {"mean": Decimal("0.12"), "mad": Decimal("0.04")},
        "DGPI":       {"mean": Decimal("0.15"), "mad": Decimal("0.05")},
        "CAIE":       {"mean": Decimal("0.20"), "mad": Decimal("0.06")},
        "SDA":        {"mean": Decimal("-0.40"), "mad": Decimal("0.50")},  # log-normal
        "CLI":        {"mean": Decimal("0.25"), "mad": Decimal("0.10")},
        "GEOPOLITICAL":{"mean": Decimal("0.30"), "mad": Decimal("0.15")},
        "ENTANGLEMENT":{"mean": Decimal("0.35"), "mad": Decimal("0.12")},
    }

    def __init__(self):
        import decimal as _decimal_module
        self.ctx = _decimal_module.getcontext()
        self.ctx.prec = self._PRECISION
        self.ctx.rounding = self._ROUNDING

    # Límite de dígitos para prevenir DoS matemático (Fix A — 2026-05-02)
    # Un string numérico con 10k dígitos antes del Decimal() satura la mantisa
    # de precisión 28 y puede causar consumo de CPU excesivo o InvalidOperation.
    _MAX_NUMERIC_STR_LEN: int = 50

    def normalize(
        self,
        tool_name: str,
        raw_value: Union[int, float, Fraction, Decimal],
        raw_confidence: Union[int, float, Decimal] = 0.0,
        metadata: Dict[str, Any] = None
    ) -> "NormalizedSignal":
        """
        Normaliza cualquier señal cruda a espacio común Decimal.
        """
        meta = metadata or {}

        # --- Paso 0b: Validar tool_name contra Enum (Fix B) ---
        # tool_name viene del campo art_type del artefacto — controlable por el atacante.
        # Si no está en el Enum, forzar a UNKNOWN con baseline conservador (mean=0.5).
        # Esto impide que un artefacto de red se disfrace de proceso para
        # obtener el baseline permisivo de SDA y reducir su z_score artificialmente.
        try:
            validated_tool = ToolName(tool_name).value
        except ValueError:
            validated_tool = ToolName.UNKNOWN.value

        # --- Paso 0: Guardia contra DoS por input extremo ---
        # Un string numérico muy largo (ej: "1." + "3"*10000) puede saturar
        # la CPU del motor de inferencia al convertirse a Decimal(str(x)).
        # Validar longitud antes de cualquier conversión aritmética.
        raw_str = str(raw_value)
        if len(raw_str) > self._MAX_NUMERIC_STR_LEN:
            raise ValueError(
                f"raw_value excede el límite de {self._MAX_NUMERIC_STR_LEN} caracteres "
                f"({len(raw_str)} chars). Posible intento de DoS por input extremo. "
                "Verificar origen del artefacto."
            )

        # --- Paso 1: Convertir a Decimal según origen ---
        if isinstance(raw_value, Fraction):
            # Origen semiótico: Fraction → Decimal exacto
            dec_value = Decimal(raw_value.numerator) / Decimal(raw_value.denominator)
            source = "fraction_rational"
        elif isinstance(raw_value, int):
            # Origen semiótico escalado (ej: int(weight*100))
            dec_value = Decimal(raw_value) / Decimal("100")
            source = "integer_scaled"
        elif isinstance(raw_value, float):
            # Origen geopolítico/CAIE: float → Decimal con discretización
            dec_value = Decimal(str(raw_value))
            source = "float_discretized"
        elif isinstance(raw_value, Decimal):
            dec_value = raw_value
            source = "decimal_native"
        else:
            raise TypeError(f"Tipo numérico no soportado: {type(raw_value)}")

        # --- Paso 2: Clamp a [0,1] solo para herramientas con baseline positivo ---
        # EXCEPCIÓN SDA (log-normal): baseline mean=-0.40 → raw_value puede ser
        # negativo y es información válida. Clampar antes del z-score destruye
        # silenciosamente esa señal: raw=-1.5 → clamp a 0.0 → z=0.8 (aparece
        # sospechoso cuando en realidad es benigno). Para SDA se clampea DESPUÉS
        # del cálculo del z-score. Para todas las demás herramientas, clamp aquí.
        zero = Decimal("0")
        one  = Decimal("1")
        _sda_raw_signal = validated_tool == ToolName.SDA.value
        if not _sda_raw_signal:
            dec_value = max(zero, min(one, dec_value))

        # --- Paso 3: Calcular z-score contra baseline AUTHENTIC ---
        # validated_tool garantiza que solo nombres de Enum acceden al baseline.
        baseline = self._BASELINES.get(validated_tool, {"mean": Decimal("0.5"), "mad": Decimal("0.1")})
        mean = baseline["mean"]
        mad  = baseline["mad"]

        if mad == zero:
            z_score = Decimal("0")
        else:
            z_score = (dec_value - mean) / mad

        # Clip z-score para evitar explosión (Daubert)
        z_clip_max = Decimal("5.0")
        z_clip_min = Decimal("-5.0")
        z_score = max(z_clip_min, min(z_clip_max, z_score))

        # SDA: clamp del value DESPUÉS del z-score para no perder la señal.
        # El z-score ya fue calculado sobre el valor real — ahora sí clampar
        # para que el campo value quede en [0,1] para el pipeline downstream.
        if _sda_raw_signal:
            dec_value = max(zero, min(one, dec_value))

        # --- Paso 4: Normalizar confianza ---
        if isinstance(raw_confidence, (int, float)):
            dec_conf = Decimal(str(raw_confidence))
        else:
            dec_conf = raw_confidence
        dec_conf = max(zero, min(one, dec_conf))

        return NormalizedSignal(
            tool_name=validated_tool,
            value=dec_value.quantize(Decimal("0.0001")),
            z_score=z_score.quantize(Decimal("0.0001")),
            confidence=dec_conf.quantize(Decimal("0.0001")),
            metadata=meta,
            normalization_source=source,
            baseline_version="bootstrap_v2",
            baseline_source="expert_elicitation_180_samples"
        )

    def get_baseline_spec(self) -> dict:
        """P2-A: Especificación del baseline para auditoría externa."""
        return {
            "version": "bootstrap_v2",
            "samples": 180,
            "distribution": "log_normal_and_beta_mixture",
            "calibration_date": "2026-04-30",
            "method": "MAD_crude_no_1.4826_factor",
            "note": (
                "z-scores use raw MAD without the 1.4826 scaling factor. "
                "This is documented and consistent across all tools. "
                "Scores are comparable within the system but not to standard z-scores."
            )
        }

    def batch_normalize(self, signals: list) -> list:
        """Normaliza una lista de señales crudas."""
        return [self.normalize(s["tool"], s["value"], s.get("confidence", 0.0), s.get("meta", {}))
                for s in signals]
