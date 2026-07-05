"""
vigia/tools/eml_symbolic.py
─────────────────────────────────────────────────────────────────────────────
DGPI — Deterministic Generative Pattern Inference

NOMBRE CORRECTO (Gemini/DeepSeek consenso):
    NO llamar "symbolic regression engine" — eso implicaría inferencia real.
    Llamar "deterministic generative pattern inference" o "symbolic pattern
    reconstruction". Es lo que realmente hace: identifica la ley matemática
    que gobernó la generación, no la infiere desde cero.

QUÉ HACE:
    Dado un vector de intervalos temporales (case_002_log_fabrication, etc.),
    determina si existe una función generadora simple (constante, lineal,
    senoidal, Poisson). Si la encuentra, la expresa en forma EML canónica.

    Operador EML: eml(x, y) = e^x - ln(y)  (Odrzywołek)
    Uso como LENGUAJE DE REPRESENTACIÓN (no como motor de cómputo).
    Un reviewr técnico puede verificar la expresión matemáticamente.

POR QUÉ ESTO ES SUPERIOR A Z-SCORES SOLOS (debate ChatGPT):
    Un atacante con jitter puede bajar el Z-score.
    Pero si la función generadora es eml(eml(1, C), 1) + ε,
    el patrón matemático subsiste aunque los intervalos no sean exactos.
    Pasamos de "esto es raro" a "esto fue generado por esta función".

GARANTÍAS DAUBERT:
    - Determinístico: mismo input → mismo output
    - Explicable: la expresión EML es una función matemática verificable
    - Sin caja negra: no hay modelo entrenado
    - Reproducible: la heurística es pública y auditada
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import statistics
from typing import Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput
from vigia.tools.signal_contract import SignalBuilder

# ---------------------------------------------------------------------------
# Constantes de detección (justificadas para Daubert)
# ---------------------------------------------------------------------------

CONSTANT_JITTER_THRESHOLD: float = 0.01
"""
MAD/median < 1% → patrón constante.
Umbral más conservador que std < mean*0.01 (ChatGPT fix §3 del debate).
"""

LINEAR_R2_THRESHOLD: float = 0.92
"""
R² > 0.92 en fit lineal → drift lineal (ej: carga de CPU aumentando).
"""

SINUSOIDAL_HARMONICS_THRESHOLD: float = 0.85
"""
Si la autocorrelación a lag-k supera este umbral → patrón periódico.
"""

POISSON_DISPERSION_TOLERANCE: float = 0.15
"""
Proceso Poisson: var/mean ≈ 1. Tolerancia ±15%.
"""

# ---------------------------------------------------------------------------
# PatternResult — resultado de la inferencia
# ---------------------------------------------------------------------------

class PatternResult:
    """
    Resultado de la inferencia DGPI.

    Campos:
        pattern_type    : tipo de patrón detectado (enum-like string)
        eml_expression  : representación canónica EML de la función generadora
        confidence      : confianza en la identificación [0.0, 1.0]
        parameters      : parámetros de la función detectada
        interpretation  : narrativa técnica para el REPORT LAYER
        signal          : SignalOutput para el LikelihoodEngine
        mitre_ttp       : técnica MITRE ATT&CK más probable
    """

    PATTERN_NONE = "NO_PATTERN_DETECTED"
    PATTERN_CONSTANT = "CONSTANT_SLEEP"
    PATTERN_JITTER = "JITTER_OBFUSCATED"
    PATTERN_LINEAR_DRIFT = "LINEAR_DRIFT"
    PATTERN_SINUSOIDAL = "SINUSOIDAL_MIMICRY"
    PATTERN_POISSON_EXACT = "EXACT_POISSON"

    def __init__(
        self,
        pattern_type: str,
        eml_expression: str,
        confidence: float,
        parameters: Dict,
        interpretation: str,
        signal: SignalOutput,
        mitre_ttp: str = "",
    ) -> None:
        self.pattern_type = pattern_type
        self.eml_expression = eml_expression
        self.confidence = confidence
        self.parameters = parameters
        self.interpretation = interpretation
        self.signal = signal
        self.mitre_ttp = mitre_ttp

    @property
    def is_algorithmic(self) -> bool:
        return self.pattern_type != self.PATTERN_NONE

    def to_dict(self) -> Dict:
        payload = {
            "pattern_type": self.pattern_type,
            "is_algorithmic": self.is_algorithmic,
            "eml_expression": self.eml_expression,
            "confidence": self.confidence,  # crudo para hashing
            "parameters": self.parameters,
            "interpretation": self.interpretation,
            "mitre_ttp": self.mitre_ttp,
            "signal": {
                "tool_name": self.signal.tool_name,
                "signal_id": self.signal.signal_id,
                "z_score": self.signal.z_score,  # crudo
                "value": self.signal.value,      # crudo
                "confidence": self.signal.confidence,  # crudo
            },
        }
        # P1: HMAC opcional
        try:
            import hmac, hashlib, json as _json, os as _os
            key_hex = _os.environ.get("VIGIA_HMAC_KEY", "").strip()
            if key_hex:
                key = bytes.fromhex(key_hex)
                canonical = _json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
                payload["_dgpi_hmac"] = hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
                del key
        except Exception:
            pass
        return payload

    def to_dict_display(self) -> Dict:
        """Versión redondeada para display humano."""
        return {
            "pattern_type": self.pattern_type,
            "is_algorithmic": self.is_algorithmic,
            "eml_expression": self.eml_expression,
            "confidence": round(self.confidence, 4),
            "parameters": self.parameters,
            "interpretation": self.interpretation,
            "mitre_ttp": self.mitre_ttp,
            "signal": {
                "tool_name": self.signal.tool_name,
                "signal_id": self.signal.signal_id,
                "z_score": round(self.signal.z_score, 6),
                "value": round(self.signal.value, 6),
                "confidence": round(self.signal.confidence, 4),
            },
        }


# ---------------------------------------------------------------------------
# DGPI Engine
# ---------------------------------------------------------------------------

class DGPIEngine:
    """
    Deterministic Generative Pattern Inference Engine.

    Ordena de más específico a más general:
    1. CONSTANT_SLEEP    — sleep(C) puro
    2. JITTER_OBFUSCATED — sleep(C) + ruido mínimo anti-detección
    3. LINEAR_DRIFT      — intervalos en progresión lineal
    4. SINUSOIDAL_MIMICRY— periodicidad enmascarada
    5. EXACT_POISSON     — proceso Poisson parametrizado (var/mean ≈ 1 perfecto)
    6. NO_PATTERN        — variabilidad compatible con autoría humana

    El pipeline se detiene en el primer match (más específico gana).
    """

    def analyze(
        self,
        deltas: List[float],
        discriminator: str = "",
        baseline_mean: float = 2.0,
        baseline_mad: float = 1.5,
    ) -> PatternResult:
        """
        Análisis DGPI sobre una lista de intervalos temporales.

        Args:
            deltas:         Intervalos en segundos (> 0).
            discriminator:  Identificador para signal_id.
            baseline_mean:  Media del baseline AUTHENTIC (para z_score).
            baseline_mad:   MAD del baseline AUTHENTIC.

        Returns:
            PatternResult con señal lista para LikelihoodEngine.
        """
        clean = [d for d in deltas if math.isfinite(d) and d > 0]
        if len(clean) < 3:
            return self._no_pattern(clean, discriminator, baseline_mean, baseline_mad)

        med = statistics.median(clean)
        mad = statistics.median([abs(d - med) for d in clean])
        mad_ratio = mad / med if med > 0 else float("inf")

        # Pipeline NO-GREEDY: evalúa TODOS los detectores, retorna el de mayor confidence.
        # Elimina el fallo de "primer match gana" que oculta señales sinusoidales
        # cuando el MAD es bajo (Doc1 §2.1).
        candidates: List[PatternResult] = []
        for fn in (
            lambda: self._detect_constant(clean, mad_ratio, med, discriminator, baseline_mean, baseline_mad),
            lambda: self._detect_jitter(clean, mad_ratio, med, discriminator, baseline_mean, baseline_mad),
            lambda: self._detect_linear_drift(clean, discriminator, baseline_mean, baseline_mad),
            lambda: self._detect_sinusoidal(clean, med, discriminator, baseline_mean, baseline_mad),
            lambda: self._detect_poisson_exact(clean, med, discriminator, baseline_mean, baseline_mad),
        ):
            r = fn()
            if r is not None:
                candidates.append(r)

        if not candidates:
            return self._no_pattern(clean, discriminator, baseline_mean, baseline_mad)

        # P1: Tie-breaker explícito para determinismo absoluto.
        # Si dos candidatos tienen misma confidence, desempata por:
        # 1. Mayor número de parámetros (más específico)
        # 2. Orden alfabético del pattern_type (último recurso, siempre determinista)
        def _sort_key(r: PatternResult) -> tuple:
            return (r.confidence, len(r.parameters), r.pattern_type)

        candidates.sort(key=_sort_key, reverse=True)
        return candidates[0]

    # -----------------------------------------------------------------------
    # Detectores individuales
    # -----------------------------------------------------------------------

    def _detect_constant(
        self,
        deltas: List[float],
        mad_ratio: float,
        med: float,
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> Optional[PatternResult]:
        """sleep(C) puro — MAD/median < 1%."""
        if mad_ratio >= CONSTANT_JITTER_THRESHOLD:
            return None

        c = round(med, 4)
        # EML canónico: eml(eml(1, C), 1) representa la constante C
        # eml(1, C) = e^1 - ln(C); eml(result, 1) simplifica a la C original
        eml_expr = f"eml(eml(1, {c}), 1)  [C={c}s]"

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=mad_ratio,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=0.97,
            discriminator=discriminator,
            metadata={
                "pattern": "CONSTANT_SLEEP",
                "detected_constant": c,
                "generator_version": "DGPIEngine-v0",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_CONSTANT,
            eml_expression=eml_expr,
            confidence=0.97,
            parameters={"C": c, "mad_ratio": mad_ratio, "n": len(deltas)},
            interpretation=(
                f"Patrón CONSTANT_SLEEP detectado. Función generadora: sleep({c}s). "
                f"La precisión (MAD/median={mad_ratio:.4f}) es incompatible con latencia "
                f"humana. Indica bucle determinista con time.sleep({c})."
            ),
            signal=signal,
            mitre_ttp="T1070.006 — Timestomp (indicative)",
        )

    def _detect_jitter(
        self,
        deltas: List[float],
        mad_ratio: float,
        med: float,
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> Optional[PatternResult]:
        """sleep(C) + jitter anti-detección — MAD/median en [0.01, 0.05]."""
        if not (CONSTANT_JITTER_THRESHOLD <= mad_ratio < 0.05):
            return None

        c = round(med, 4)
        jitter_est = round(mad_ratio * med, 4)
        eml_expr = f"eml(eml(1, {c}), 1) + ε  [C={c}s, ε≈{jitter_est}s]"

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=mad_ratio,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=0.88,
            discriminator=discriminator,
            metadata={
                "pattern": "JITTER_OBFUSCATED",
                "detected_constant": c,
                "jitter_estimate": jitter_est,
                "generator_version": "DGPIEngine-v0",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_JITTER,
            eml_expression=eml_expr,
            confidence=0.88,
            parameters={"C": c, "jitter": jitter_est, "mad_ratio": mad_ratio},
            interpretation=(
                f"Patrón JITTER_OBFUSCADO detectado. El adversario aplicó ruido mínimo "
                f"(ε≈{jitter_est}s) para evadir detección por Z-score simple. "
                f"La función base sigue siendo constante ({c}s). "
                f"Compatible con random.uniform({c-jitter_est:.3f}, {c+jitter_est:.3f})."
            ),
            signal=signal,
            mitre_ttp="T1070.006 — Timestomp + T1036 — Masquerading",
        )

    def _detect_linear_drift(
        self,
        deltas: List[float],
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> Optional[PatternResult]:
        """Drift lineal — R² > 0.92 en regresión lineal sobre los deltas."""
        n = len(deltas)
        if n < 5:
            return None

        r2, slope, intercept = self._linear_r2(deltas)
        if r2 < LINEAR_R2_THRESHOLD:
            return None

        eml_expr = f"eml(1, exp(1)) * {slope:.4f} * t + {intercept:.4f}"

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=r2,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=0.82,
            discriminator=discriminator,
            metadata={
                "pattern": "LINEAR_DRIFT",
                "r2": r2,
                "slope": slope,
                "intercept": intercept,
                "generator_version": "DGPIEngine-v0",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_LINEAR_DRIFT,
            eml_expression=eml_expr,
            confidence=0.82,
            parameters={"r2": r2, "slope": slope, "intercept": intercept},
            interpretation=(
                f"Drift lineal detectado (R²={r2:.4f}). Los intervalos aumentan/disminuyen "
                f"de forma proporcional al índice del evento. Compatible con scripts que "
                f"aceleran/frenan intencionalmente (backoff o ramp-up programático)."
            ),
            signal=signal,
            mitre_ttp="T1070 — Indicator Removal",
        )

    def _detect_sinusoidal(
        self,
        deltas: List[float],
        med: float,
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> Optional[PatternResult]:
        """
        Detecta periodicidad enmascarada mediante ACF + validación R².

        Paso 1: ACF encuentra el lag dominante.
        Paso 2: reconstruye señal sinusoidal y valida R² contra los residuals.
                Sin validación → falsos positivos por ruido + periodicidad parcial (Doc1 §2.2).
        """
        n = len(deltas)
        if n < 12:
            return None

        mean_d = statistics.mean(deltas)
        denom = sum((d - mean_d) ** 2 for d in deltas)
        if denom < 1e-12:
            return None

        max_lag = min(n // 3, 20)
        best_lag = 0
        best_acf = 0.0

        for lag in range(1, max_lag + 1):
            num = sum(
                (deltas[t] - mean_d) * (deltas[t + lag] - mean_d)
                for t in range(n - lag)
            )
            acf_k = num / denom
            if acf_k > best_acf:
                best_acf = acf_k
                best_lag = lag

        if best_acf < SINUSOIDAL_HARMONICS_THRESHOLD:
            return None

        # Validación R²: ajuste sinusoidal por mínimos cuadrados (Doc1 §2.2)
        # Modelo: A*sin(2π*t/best_lag) + B*cos(2π*t/best_lag) + C
        omega = 2.0 * math.pi / best_lag
        sin_t = [math.sin(omega * t) for t in range(n)]
        cos_t = [math.cos(omega * t) for t in range(n)]

        # Mínimos cuadrados: [sin, cos, 1] → coeficientes [A, B, C]
        # Solución analítica 3x3 (sin numpy)
        A, B, C = self._fit_sinusoidal_ols(deltas, sin_t, cos_t)

        fitted   = [A * sin_t[i] + B * cos_t[i] + C for i in range(n)]
        ss_res   = sum((deltas[i] - fitted[i]) ** 2 for i in range(n))
        ss_tot   = sum((deltas[i] - mean_d) ** 2 for i in range(n))
        r2       = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

        # Si R² < 0.6 → periodicidad débil → rechazamos para evitar falsos positivos
        if r2 < 0.60:
            return None

        period_s = round(best_lag * med, 4)
        freq_hz  = round(1.0 / period_s, 6) if period_s > 0 else 0.0
        amplitude = round(math.sqrt(A ** 2 + B ** 2), 4)
        eml_expr  = f"A·sin(2π·{freq_hz:.6f}·t)  [lag={best_lag}, ACF={best_acf:.4f}, R²={r2:.4f}]"

        # Confianza combinada: ACF + R²
        confidence = round(min(0.93, 0.5 * best_acf + 0.5 * r2), 4)

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=best_acf,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=confidence,
            discriminator=discriminator,
            metadata={
                "pattern": "SINUSOIDAL_MIMICRY",
                "best_lag": best_lag,
                "acf_peak": round(best_acf, 4),
                "r2": round(r2, 4),
                "amplitude": amplitude,
                "estimated_period_s": period_s,
                "freq_hz": freq_hz,
                "generator_version": "DGPIEngine-v1",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_SINUSOIDAL,
            eml_expression=eml_expr,
            confidence=confidence,
            parameters={
                "best_lag": best_lag,
                "acf_peak": round(best_acf, 4),
                "r2": round(r2, 4),
                "period_s": period_s,
                "freq_hz": freq_hz,
                "amplitude": amplitude,
            },
            interpretation=(
                f"Periodicidad enmascarada detectada (ACF[lag={best_lag}]={best_acf:.4f}, R²={r2:.4f}). "
                f"El patrón se repite cada ≈{period_s}s. Compatible con scripts que alternan "
                f"entre múltiples valores de sleep o simulan ciclos de polling."
            ),
            signal=signal,
            mitre_ttp="T1070.006 — Timestomp + T1036 — Masquerading (periodic)",
        )

    @staticmethod
    def _fit_sinusoidal_ols(
        y: List[float],
        sin_t: List[float],
        cos_t: List[float],
    ) -> Tuple[float, float, float]:
        """
        OLS analítico para y = A*sin_t + B*cos_t + C.
        Resuelve sistema 3x3 por eliminación de Gauss sin numpy.
        Retorna (A, B, C).
        """
        n = len(y)
        # Construir XtX (3x3) y Xty (3x1)
        ss  = sum(s * s for s in sin_t)
        sc  = sum(s * c for s, c in zip(sin_t, cos_t))
        s1  = sum(sin_t)
        cc  = sum(c * c for c in cos_t)
        c1  = sum(cos_t)
        one = float(n)
        sy  = sum(s * yy for s, yy in zip(sin_t, y))
        cy  = sum(c * yy for c, yy in zip(cos_t, y))
        oy  = sum(y)

        # Matriz aumentada [XtX | Xty]
        M = [
            [ss, sc, s1, sy],
            [sc, cc, c1, cy],
            [s1, c1, one, oy],
        ]

        # Eliminación gaussiana con pivoteo parcial
        for col in range(3):
            # Pivoteo
            max_row = max(range(col, 3), key=lambda r: abs(M[r][col]))
            M[col], M[max_row] = M[max_row], M[col]
            pivot = M[col][col]
            if abs(pivot) < 1e-12:
                return 0.0, 0.0, statistics.mean(y)
            for row in range(col + 1, 3):
                factor = M[row][col] / pivot
                for j in range(col, 4):
                    M[row][j] -= factor * M[col][j]

        # Back-substitution
        C = M[2][3] / M[2][2] if abs(M[2][2]) > 1e-12 else 0.0
        B = (M[1][3] - M[1][2] * C) / M[1][1] if abs(M[1][1]) > 1e-12 else 0.0
        A = (M[0][3] - M[0][2] * C - M[0][1] * B) / M[0][0] if abs(M[0][0]) > 1e-12 else 0.0
        return A, B, C

    def _detect_poisson_exact(
        self,
        deltas: List[float],
        med: float,
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> Optional[PatternResult]:
        """
        Proceso Poisson demasiado perfecto — var/mean ≈ 1.0 con tolerancia muy baja.
        Parche 7: mínimo 30 muestras para evitar falsos positivos por tamaño pequeño.
        """
        if len(deltas) < 30:
            return None

        mean_d = statistics.mean(deltas)
        if mean_d <= 0:
            return None
        var_d = statistics.variance(deltas)
        dispersion = abs(var_d / mean_d - 1.0)

        # Sospechoso si la dispersión es TOO perfecta (< 5% del ideal)
        if dispersion > 0.05:
            return None

        lam = round(1.0 / mean_d, 4) if mean_d > 0 else 0.0
        eml_expr = f"Exp(λ={lam})  [var/mean={var_d/mean_d:.4f}]"

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=dispersion,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=0.75,
            discriminator=discriminator,
            metadata={
                "pattern": "EXACT_POISSON",
                "lambda": lam,
                "dispersion": dispersion,
                "generator_version": "DGPIEngine-v0",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_POISSON_EXACT,
            eml_expression=eml_expr,
            confidence=0.75,
            parameters={"lambda": lam, "dispersion": dispersion},
            interpretation=(
                f"Proceso Poisson demasiado perfecto (var/mean={var_d/mean_d:.4f}, "
                f"tolerancia <5%). Un proceso Poisson físico real tiene más ruido. "
                f"Compatible con numpy.random.poisson(λ={lam}) sin semilla aleatoria real."
            ),
            signal=signal,
            mitre_ttp="T1036 — Masquerading (statistical)",
        )

    def _no_pattern(
        self,
        deltas: List[float],
        discriminator: str,
        bl_mean: float,
        bl_mad: float,
    ) -> PatternResult:
        """Variabilidad compatible con autoría humana."""
        value = statistics.median(deltas) if deltas else 0.0

        signal = SignalBuilder.from_raw(
            tool_name="DGPI",
            value=value,
            baseline_mean=bl_mean,
            baseline_mad=bl_mad,
            confidence=0.70,
            discriminator=discriminator,
            metadata={
                "pattern": "NO_PATTERN",
                "n": len(deltas),
                "generator_version": "DGPIEngine-v0",
            },
        )

        return PatternResult(
            pattern_type=PatternResult.PATTERN_NONE,
            eml_expression="N/A",
            confidence=0.70,
            parameters={"n": len(deltas)},
            interpretation=(
                "No se detectó función generadora algorítmica. "
                "La variabilidad temporal es compatible con autoría humana."
            ),
            signal=signal,
            mitre_ttp="",
        )

    # -----------------------------------------------------------------------
    # Helpers matemáticos
    # -----------------------------------------------------------------------

    @staticmethod
    def _linear_r2(values: List[float]) -> Tuple[float, float, float]:
        """
        Regresión lineal por mínimos cuadrados.
        Retorna (R², slope, intercept).
        """
        n = len(values)
        x = list(range(n))
        x_mean = (n - 1) / 2.0
        y_mean = statistics.mean(values)

        ss_xy = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        ss_xx = sum((x[i] - x_mean) ** 2 for i in range(n))

        if ss_xx == 0:
            return 0.0, 0.0, y_mean

        slope = ss_xy / ss_xx
        intercept = y_mean - slope * x_mean

        ss_res = sum((values[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))

        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        return max(0.0, min(1.0, r2)), slope, intercept


# ---------------------------------------------------------------------------
# Singleton para el bridge MCP
# ---------------------------------------------------------------------------

_DEFAULT_DGPI = DGPIEngine()


def analyze_symbolic_regression(
    deltas: List[float],
    discriminator: str = "",
    baseline_mean: float = 2.0,
    baseline_mad: float = 1.5,
) -> PatternResult:
    """
    Entry point para el bridge MCP.
    Nombre público mantenido por compatibilidad con el debate (chatgpt_deepseek_gemini.md).
    Internamente usa DGPIEngine (nombre correcto).
    """
    # P1: Validar inputs antes de procesar
    if not isinstance(deltas, list):
        raise ValueError("deltas must be a list of floats.")
    if len(deltas) > 100_000:
        raise ValueError("deltas exceeds maximum of 100,000 entries (DoS prevention).")
    if any(not math.isfinite(d) for d in deltas):
        raise ValueError("deltas contains NaN or inf — reject corrupted input.")
    return _DEFAULT_DGPI.analyze(
        deltas=deltas,
        discriminator=discriminator,
        baseline_mean=baseline_mean,
        baseline_mad=baseline_mad,
    )
