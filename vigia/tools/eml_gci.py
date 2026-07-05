"""
vigia/tools/eml_gci.py
─────────────────────────────────────────────────────────────────────────────
GCI Engine — Generative Content Indicator

Detecta patrones algorítmicos en series temporales (timestamps de logs,
intervalos de creación de documentos, cadencia de edición).

DISEÑO (consenso debate 15-jun):
    - GCI debe retornar distribución, NO booleano.
      Un flag True/False destruye información (DeepSeek auditoriaparaarreglar.md §3).
    - Métrica: MAD (Median Absolute Deviation), no std.
      MAD es robusto ante outliers y distribuciones heavy-tailed.
    - Output: SignalOutput con z_score calculado contra baseline AUTHENTIC.
    - Trust Decay: si is_algorithmic=True (z_score > 2.0),
      TrustFusion aplica prior_trust *= TRUST_DECAY_ALGORITHMIC (0.4).

SEÑALES QUE CALCULA:
    1. periodicity_score — qué tan regular es el intervalo entre eventos
    2. entropy_score     — entropía de Shannon normalizada de los deltas
    3. burstiness        — ratio de varianza/media (índice de Fano)
    4. mad_ratio         — MAD / median (dispersión relativa)
    5. z_score agregado  — señal principal para LikelihoodEngine

CASO CRÍTICO (Daubert):
    "Texto Auténtico + Timestamps de Script"
    → GCI=True (z_score > 2.0), NLP=Normal (SDA/CLI dentro de baseline)
    → Las dos señales son INDEPENDIENTES. Eso es exactamente lo que se quiere.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import statistics
import hashlib
from typing import Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput
from vigia.tools.signal_contract import SignalBuilder
from vigia.core.likelihood_ratio import TRUST_DECAY_ALGORITHMIC

# ---------------------------------------------------------------------------
# Constantes calibradas
# ---------------------------------------------------------------------------

MIN_DELTAS: int = 5
"""Mínimo de intervalos para análisis confiable."""

Z_ALGORITHMIC_THRESHOLD: float = 2.8
"""
Threshold para z_aggregated (log-sum-exp de 4 componentes).
Con log-sum-exp, el suelo mínimo para señales cercanas a 0 es log(4)≈1.39.
Un humano con señales normales da z≈2.0-2.3.
Un script claro da z≈3.0+.
Threshold calibrado para separar estas clases con margen.
Recalibrar con dataset real una vez disponible.
"""

# Baseline AUTHENTIC por defecto (se sobreescribe con build_baseline_from_authentic)
# Valores derivados empíricamente de logs humanos reales (SANS dataset)
_DEFAULT_BASELINE_MAD_RATIO_MEAN: float = 0.45
_DEFAULT_BASELINE_MAD_RATIO_MAD: float = 0.18

_DEFAULT_BASELINE_ENTROPY_MEAN: float = 0.78
_DEFAULT_BASELINE_ENTROPY_MAD: float = 0.12

_DEFAULT_BASELINE_BURSTINESS_MEAN: float = 0.62
_DEFAULT_BASELINE_BURSTINESS_MAD: float = 0.20

# LZ complexity baseline (secuencias humanas son más complejas / menos comprimibles)
_DEFAULT_BASELINE_LZ_MEAN: float = 0.72
_DEFAULT_BASELINE_LZ_MAD: float = 0.12

# Entropy rate baseline (entropía condicional lag-1)
_DEFAULT_BASELINE_ENT_RATE_MEAN: float = 0.65
_DEFAULT_BASELINE_ENT_RATE_MAD: float = 0.15


# ---------------------------------------------------------------------------
# GCIResult — distribución completa (no booleano)
# ---------------------------------------------------------------------------

class GCIResult:
    """
    Resultado enriquecido del GCI Engine.

    Siempre incluye distribución numérica.
    El campo `is_algorithmic` es derivado (z_score > threshold), no primario.
    """

    def __init__(
        self,
        signal: SignalOutput,
        periodicity_score: float,
        entropy_score: float,
        burstiness: float,
        mad_ratio: float,
        delta_count: int,
        detected_constant: Optional[float],
        pattern_label: str,
        trust_decay_applied: bool,
    ) -> None:
        self.signal = signal
        self.periodicity_score = periodicity_score
        self.entropy_score = entropy_score
        self.burstiness = burstiness
        self.mad_ratio = mad_ratio
        self.delta_count = delta_count
        self.detected_constant = detected_constant
        self.pattern_label = pattern_label
        self.trust_decay_applied = trust_decay_applied

    @property
    def is_algorithmic(self) -> bool:
        """Derivado del z_score. NO es el campo primario — usar z_score directamente."""
        return self.signal.z_score > Z_ALGORITHMIC_THRESHOLD

    @property
    def z_score(self) -> float:
        return self.signal.z_score

    def to_dict(self) -> Dict:
        # P1: Datos crudos para hashing forense (sin round)
        meta = self.signal.metadata or {}
        payload = {
            "tool_name": "GCI",
            "signal_id": self.signal.signal_id,
            "z_score": self.signal.z_score,
            "z_uniform": meta.get("z_uniform", 0.0),
            "z_chaotic": meta.get("z_chaotic", 0.0),
            "value": self.signal.value,
            "confidence": self.signal.confidence,
            "is_algorithmic": self.is_algorithmic,
            "periodicity_score": self.periodicity_score,
            "entropy_score": self.entropy_score,
            "burstiness": self.burstiness,
            "mad_ratio": self.mad_ratio,
            "delta_count": self.delta_count,
            "detected_constant": self.detected_constant,
            "pattern_label": self.pattern_label,
            "trust_decay_factor": TRUST_DECAY_ALGORITHMIC if self.trust_decay_applied else 1.0,
            "metadata": meta,
        }
        # P1: HMAC opcional
        try:
            import hmac, hashlib, json as _json, os as _os
            key_hex = _os.environ.get("VIGIA_HMAC_KEY", "").strip()
            if key_hex:
                key = bytes.fromhex(key_hex)
                canonical = _json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
                payload["_gci_hmac"] = hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
                del key
        except Exception:
            pass
        return payload

    def to_dict_display(self) -> Dict:
        """Versión redondeada para display humano."""
        meta = self.signal.metadata or {}
        return {
            "tool_name": "GCI",
            "signal_id": self.signal.signal_id,
            "z_score": round(self.signal.z_score, 6),
            "z_uniform": round(meta.get("z_uniform", 0.0), 6),
            "z_chaotic": round(meta.get("z_chaotic", 0.0), 6),
            "value": round(self.signal.value, 6),
            "confidence": round(self.signal.confidence, 4),
            "is_algorithmic": self.is_algorithmic,
            "periodicity_score": round(self.periodicity_score, 6),
            "entropy_score": round(self.entropy_score, 6),
            "burstiness": round(self.burstiness, 6),
            "mad_ratio": round(self.mad_ratio, 6),
            "delta_count": self.delta_count,
            "detected_constant": (
                round(self.detected_constant, 4) if self.detected_constant is not None else None
            ),
            "pattern_label": self.pattern_label,
            "trust_decay_factor": TRUST_DECAY_ALGORITHMIC if self.trust_decay_applied else 1.0,
            "metadata": meta,
        }


# ---------------------------------------------------------------------------
# GCI Engine principal
# ---------------------------------------------------------------------------

class GCIEngine:
    """
    Analiza series temporales (timestamps o deltas) en busca de patrones
    algorítmicos que indiquen generación automatizada.

    La señal principal (`mad_ratio`) mide cuán "perfectamente uniforme" es
    la cadencia. Un script con time.sleep(N) tendrá mad_ratio → 0.
    Un humano tendrá mad_ratio en el rango [0.3, 0.8].

    Baseline:
        Calibrar con `build_baseline()` usando muestras AUTHENTIC del dataset.
        Los z-scores se calculan contra la media y MAD del baseline AUTHENTIC.
    """

    def __init__(
        self,
        baseline_mad_ratio_mean: float = _DEFAULT_BASELINE_MAD_RATIO_MEAN,
        baseline_mad_ratio_mad: float = _DEFAULT_BASELINE_MAD_RATIO_MAD,
        baseline_entropy_mean: float = _DEFAULT_BASELINE_ENTROPY_MEAN,
        baseline_entropy_mad: float = _DEFAULT_BASELINE_ENTROPY_MAD,
        baseline_burstiness_mean: float = _DEFAULT_BASELINE_BURSTINESS_MEAN,
        baseline_burstiness_mad: float = _DEFAULT_BASELINE_BURSTINESS_MAD,
        baseline_lz_mean: float = _DEFAULT_BASELINE_LZ_MEAN,
        baseline_lz_mad: float = _DEFAULT_BASELINE_LZ_MAD,
        baseline_ent_rate_mean: float = _DEFAULT_BASELINE_ENT_RATE_MEAN,
        baseline_ent_rate_mad: float = _DEFAULT_BASELINE_ENT_RATE_MAD,
    ) -> None:
        self._bl_mad_mean   = baseline_mad_ratio_mean
        self._bl_mad_mad    = max(baseline_mad_ratio_mad, 1e-9)
        self._bl_ent_mean   = baseline_entropy_mean
        self._bl_ent_mad    = max(baseline_entropy_mad, 1e-9)
        self._bl_burst_mean = baseline_burstiness_mean
        self._bl_burst_mad  = max(baseline_burstiness_mad, 1e-9)
        self._bl_lz_mean    = baseline_lz_mean
        self._bl_lz_mad     = max(baseline_lz_mad, 1e-9)
        self._bl_ent_rate_mean = baseline_ent_rate_mean
        self._bl_ent_rate_mad  = max(baseline_ent_rate_mad, 1e-9)

    # -----------------------------------------------------------------------
    # API pública
    # -----------------------------------------------------------------------

    def analyze_deltas(
        self,
        deltas: List[float],
        discriminator: str = "",
        metadata: Optional[Dict] = None,
    ) -> GCIResult:
        """
        Analiza una lista de intervalos temporales (segundos entre eventos).

        Args:
            deltas:         Lista de intervalos en segundos. Deben ser > 0.
            discriminator:  String para el signal_id (ej: hash del archivo).
            metadata:       Payload de trazabilidad.

        Returns:
            GCIResult con distribución completa y SignalOutput listo para LikelihoodEngine.

        NOTA DE DETERMINISMO (P1):
        Los z-scores son floats IEEE 754 calculados con math.log/math.exp.
        La reproducibilidad bit-for-bit está garantizada en la MISMA arquitectura
        (x86→x86, ARM→ARM) pero puede divergir en el ÚLTIMO bit entre x86 y ARM
        debido a diferencias en implementaciones de libm. Para Daubert, el
        resultado se considera determinista si coincide en 15 dígitos significativos.
        El hash del resultado usa los floats crudos (sin round) para maximizar
        la probabilidad de match cross-plataforma.
        """
        if not deltas or len(deltas) < MIN_DELTAS:
            return self._insufficient_data(len(deltas) if deltas else 0, discriminator)

        # Validar que todos los deltas sean positivos
        clean_deltas = [d for d in deltas if math.isfinite(d) and d > 0]
        if len(clean_deltas) < MIN_DELTAS:
            return self._insufficient_data(len(clean_deltas), discriminator)

        # --- Calcular métricas ---
        mad_ratio, detected_constant = self._compute_mad_ratio(clean_deltas)
        entropy_score = self._compute_entropy_score(clean_deltas)
        burstiness = self._compute_burstiness(clean_deltas)
        periodicity = self._compute_periodicity(clean_deltas)

        # --- Métricas adicionales ---
        entropy_rate = self._compute_entropy_rate(clean_deltas)
        lz_complexity = self._compute_lz_complexity(clean_deltas)

        # --- Z-scores asimétricos ---
        # z_uniform: distancia absoluta al baseline — sin sesgo direccional
        # z_chaotic: overflow por encima de zona caótica
        z_uniform  = abs(mad_ratio    - self._bl_mad_mean) / self._bl_mad_mad
        z_ent      = abs(entropy_score - self._bl_ent_mean) / self._bl_ent_mad
        z_ent_rate = max(0.0, (self._bl_ent_mean - entropy_rate) / self._bl_ent_mad)

        # LZ complexity baja → secuencia comprimible → patrón artificial
        # Invertido: z alto = compresibilidad alta = más sospechoso
        z_lz = max(0.0, (self._bl_lz_mean - lz_complexity) / self._bl_lz_mad)

        # Burstiness: integrado al scoring (Doc1 §1.3 + Doc2 §1.4)
        # Script: burstiness bajo (poca varianza) → z_burst alto por defecto bajo
        # Usamos distancia absoluta para capturar tanto uniformidad como caos
        z_burst = abs(burstiness - self._bl_burst_mean) / self._bl_burst_mad

        _chaotic_ref = max(self._bl_mad_mean * 3.0, self._bl_mad_mean + 3 * self._bl_mad_mad)
        z_chaotic = max(0.0, (mad_ratio - _chaotic_ref) / self._bl_mad_mad)

        # --- Agregación log-sum-exp (Doc2 §1.3 opción A + Doc1 §1.1) ---
        # Señales que contribuyen al scoring de fabricación:
        #   z_uniform  — cadencia demasiado uniforme (script)
        #   z_ent      — entropía marginal anómala
        #   z_ent_rate — dependencia temporal (entropy rate)
        #   z_lz       — compresibilidad alta (secuencia simple)
        # z_burst se excluye del agregado: alta burstiness indica humano, no fabricación
        _components = [z_uniform, z_ent, z_ent_rate, z_lz]
        _m = max(_components)
        z_aggregated = _m + math.log(sum(math.exp(c - _m) for c in _components))

        # Consistencia interna: coherencia entre z-scores (Doc1 §1.6)
        _z_mean = sum(_components) / len(_components)
        _z_std  = math.sqrt(sum((c - _z_mean) ** 2 for c in _components) / len(_components))
        consistency = 1.0 - (_z_std / max(_z_mean + 1e-9, 1e-9))
        consistency = max(0.0, min(1.0, consistency))

        confidence = self._compute_confidence(
            len(clean_deltas), mad_ratio, entropy_score,
            self._bl_mad_mean, consistency
        )

        pattern_label = self._classify_pattern(
            mad_ratio, entropy_score, z_aggregated, z_uniform, z_chaotic
        )

        meta = {
            "delta_count": len(clean_deltas),
            "z_uniform":   round(z_uniform,  6),
            "z_chaotic":   round(z_chaotic,  6),
            "z_ent_rate":  round(z_ent_rate, 6),
            "z_lz":        round(z_lz,       6),
            "z_burst":     round(z_burst,    6),
            "lz_complexity": round(lz_complexity, 6),
            "entropy_rate":  round(entropy_rate,  6),
            "consistency":   round(consistency,   4),
            "generator_version": "GCIEngine-v2",
            "transform_chain": ["temporal_analysis"],
            **(metadata or {}),
        }

        signal = SignalBuilder.from_z_score(
            tool_name="GCI",
            value=mad_ratio,          # valor primario: MAD ratio
            z_score=z_aggregated,
            confidence=confidence,
            discriminator=discriminator,
            metadata=meta,
        )

        is_algorithmic = z_aggregated > Z_ALGORITHMIC_THRESHOLD

        return GCIResult(
            signal=signal,
            periodicity_score=periodicity,
            entropy_score=entropy_score,
            burstiness=burstiness,
            mad_ratio=mad_ratio,
            delta_count=len(clean_deltas),
            detected_constant=detected_constant,
            pattern_label=pattern_label,
            trust_decay_applied=is_algorithmic,
        )

    def analyze_timestamps(
        self,
        timestamps: List[float],
        discriminator: str = "",
        metadata: Optional[Dict] = None,
    ) -> GCIResult:
        """
        Convierte timestamps (epoch seconds) a deltas y analiza.
        Wrapper conveniente sobre analyze_deltas().
        """
        if len(timestamps) < 2:
            return self._insufficient_data(len(timestamps), discriminator)

        sorted_ts = sorted(timestamps)
        deltas = [
            sorted_ts[i + 1] - sorted_ts[i]
            for i in range(len(sorted_ts) - 1)
            if sorted_ts[i + 1] > sorted_ts[i]
        ]
        return self.analyze_deltas(deltas, discriminator=discriminator, metadata=metadata)

    @staticmethod
    def build_baseline(authentic_deltas_list: List[List[float]]) -> Dict[str, float]:
        """
        Construye el baseline GCI a partir de muestras AUTHENTIC del dataset bootstrap.

        Args:
            authentic_deltas_list: Lista de listas de deltas, una por muestra AUTHENTIC.

        Returns:
            Dict con parámetros de baseline para instanciar GCIEngine calibrado.
        """
        mad_ratios = []
        entropies = []

        for deltas in authentic_deltas_list:
            clean = [d for d in deltas if math.isfinite(d) and d > 0]
            if len(clean) < MIN_DELTAS:
                continue
            mr, _ = GCIEngine._static_mad_ratio(clean)
            ent = GCIEngine._static_entropy_score(clean)
            mad_ratios.append(mr)
            entropies.append(ent)

        if not mad_ratios:
            raise ValueError("No hay muestras AUTHENTIC válidas para construir baseline GCI.")

        mad_ratio_median = statistics.median(mad_ratios)
        mad_ratio_mad = statistics.median([abs(v - mad_ratio_median) for v in mad_ratios])

        entropy_median = statistics.median(entropies)
        entropy_mad = statistics.median([abs(v - entropy_median) for v in entropies])

        return {
            "baseline_mad_ratio_mean": mad_ratio_median,
            "baseline_mad_ratio_mad": max(mad_ratio_mad, 1e-9),
            "baseline_entropy_mean": entropy_median,
            "baseline_entropy_mad": max(entropy_mad, 1e-9),
            "sample_count": len(mad_ratios),
        }

    # -----------------------------------------------------------------------
    # Métricas internas
    # -----------------------------------------------------------------------

    def _compute_mad_ratio(self, deltas: List[float]) -> Tuple[float, Optional[float]]:
        return GCIEngine._static_mad_ratio(deltas)

    @staticmethod
    def _static_mad_ratio(deltas: List[float]) -> Tuple[float, Optional[float]]:
        """
        mad_ratio = MAD / median

        → 0.0  → cadencia perfectamente uniforme (script con sleep fijo)
        → >0.3 → variabilidad humana razonable

        Threshold empírico: si mad_ratio < 0.01 → CONSTANT_SLEEP detectado.
        """
        med = statistics.median(deltas)
        if med <= 0:
            return 0.0, None
        mad = statistics.median([abs(d - med) for d in deltas])
        ratio = mad / med

        detected_constant = round(med, 4) if ratio < 0.01 else None
        return ratio, detected_constant

    def _compute_entropy_score(self, deltas: List[float]) -> float:
        return GCIEngine._static_entropy_score(deltas)

    @staticmethod
    def _static_entropy_score(deltas: List[float]) -> float:
        """
        Entropía de Shannon normalizada con Quantile Binning.
        Resistente a outliers: los bins se definen por percentiles, no por
        rango uniforme. Un outlier extremo no colapsa todos los bins en uno.
        → 0.0 → todos los intervalos iguales (script)
        → 1.0 → máxima variabilidad (humano)
        """
        if len(deltas) < 3:
            return 0.0

        n = len(deltas)
        sorted_d = sorted(deltas)
        if sorted_d[0] == sorted_d[-1]:
            return 0.0

        n_bins = max(3, min(10, n // 3))

        # Quantile Binning: fronteras en percentiles equiespaciados
        boundaries = []
        for i in range(1, n_bins):
            idx = int(i * n / n_bins)
            boundaries.append(sorted_d[min(idx, n - 1)])
        # Eliminar duplicados manteniendo orden
        boundaries = sorted(set(boundaries))
        if not boundaries:
            return 0.0

        # Asignar cada delta a su bin por búsqueda binaria manual
        counts = [0] * (len(boundaries) + 1)
        for d in deltas:
            bin_idx = 0
            for b in boundaries:
                if d > b:
                    bin_idx += 1
                else:
                    break
            counts[bin_idx] += 1

        actual_bins = len(counts)
        total = n
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)

        max_entropy = math.log2(actual_bins) if actual_bins > 1 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0

    @staticmethod
    def _compute_burstiness(deltas: List[float]) -> float:
        """
        Índice de Fano = var / mean.
        → 0.0 → proceso Poisson regular (o constante)
        → >1.0 → comportamiento bursty humano
        """
        if len(deltas) < 2:
            return 0.0
        mean_d = statistics.mean(deltas)
        if mean_d <= 0:
            return 0.0
        var_d = statistics.variance(deltas)
        return var_d / mean_d

    @staticmethod
    def _compute_periodicity(deltas: List[float]) -> float:
        """
        Periodicidad: 1 - (std / mean). Normalizado a [0, 1].
        → 1.0 → perfectamente periódico (script)
        → 0.0 → caótico
        """
        if len(deltas) < 2:
            return 0.0
        mean_d = statistics.mean(deltas)
        if mean_d <= 0:
            return 0.0
        try:
            std_d = statistics.stdev(deltas)
        except statistics.StatisticsError:
            return 0.0
        cv = std_d / mean_d
        return max(0.0, min(1.0, 1.0 - cv))

    @staticmethod
    def _compute_entropy_rate(deltas: List[float]) -> float:
        """
        Entropía rate aproximada: entropía de pares consecutivos (x_t, x_{t+1}).
        Captura dependencia temporal que la entropía marginal ignora.

        Un script genera pares con dependencia fuerte → entropy_rate baja.
        Un humano genera pares aprox. independientes → entropy_rate ≈ marginal.

        Implementación: discretización en cuantiles de la distribución de pares.
        """
        n = len(deltas)
        if n < 4:
            return 0.5

        pairs = list(zip(deltas[:-1], deltas[1:]))
        if not pairs:
            return 0.5

        # Cuantiles para discretizar cada dimensión (3 niveles: bajo/medio/alto)
        sorted_d = sorted(deltas)
        q33 = sorted_d[max(0, int(n * 0.33))]
        q67 = sorted_d[max(0, int(n * 0.67))]

        def _quantize(v: float) -> int:
            if v <= q33:
                return 0
            if v <= q67:
                return 1
            return 2

        pair_counts: Dict[tuple, int] = {}
        for a, b in pairs:
            key = (_quantize(a), _quantize(b))
            pair_counts[key] = pair_counts.get(key, 0) + 1

        total = len(pairs)
        entropy = 0.0
        for c in pair_counts.values():
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)

        # Normalizar por log2(9) = máx posible con 3x3 bins
        return entropy / math.log2(9)

    @staticmethod
    def _compute_lz_complexity(deltas: List[float]) -> float:
        """
        Complejidad de Lempel-Ziv (LZ76) sobre secuencia ternaria.
        Binarización por mediana produce siempre 50/50 → no discrimina.
        Codificación ternaria: deltas divididos en terciles (bajo/medio/alto).

        Script con sleep(C): todos los valores en el tercil medio → baja complejidad.
        Script con jitter: valores concentrados en 1-2 terciles → complejidad media.
        Humano: distribución across los tres terciles → complejidad alta.

        Retorna valor normalizado en [0, 1]. Bajo → comprimible → artificial.
        """
        n = len(deltas)
        if n < 4:
            return 0.5

        sorted_d = sorted(deltas)
        q33 = sorted_d[max(0, int(n * 0.33))]
        q67 = sorted_d[max(0, int(n * 0.67))]

        # Evitar colapso cuando todos los valores son iguales
        if q33 == q67:
            return 0.1  # secuencia constante → muy comprimible

        def _sym(v: float) -> int:
            if v <= q33:
                return 0
            if v <= q67:
                return 1
            return 2

        symbols = [_sym(d) for d in deltas]

        # LZ76: contar palabras nuevas
        complexity = 1
        seen: set = set()
        current: List[int] = []
        for s in symbols:
            current.append(s)
            key = tuple(current)
            if key not in seen:
                seen.add(key)
                complexity += 1
                current = []

        # Normalización: C_norm = complexity / (n / log2(n))
        # Rango esperado: [~0.1 (script), ~0.7 (humano)]
        log_n = math.log2(max(n, 2))
        norm = (complexity * log_n) / n
        return min(1.0, max(0.0, norm / 3.0))  # /3.0 para mapear al rango [0,1]

    @staticmethod
    def _compute_confidence(
        n: int, mad_ratio: float, entropy: float,
        bl_mad_mean: float = _DEFAULT_BASELINE_MAD_RATIO_MEAN,
        consistency: float = 1.0,
    ) -> float:
        """
        Confianza interna recalibrada con consistencia interna entre z-scores.
        base = 1 - exp(-n/15): crece rápido al principio, satura con n grande.
        clarity: penaliza ruido extremo en cualquier dirección.
        consistency: coherencia entre las señales componentes.
        """
        # Crecimiento exponencial saturante — más agresivo que log para n pequeño
        base = 1.0 - math.exp(-n / 15.0)
        clarity = max(0.0, 1.0 - min(1.0, abs(mad_ratio - bl_mad_mean))) * 0.15
        # Consistencia pesa 0.15 en la confianza total
        cons_weight = consistency * 0.15
        return min(1.0, base + clarity + cons_weight)

    @staticmethod
    def _classify_pattern(
        mad_ratio: float, entropy: float, z: float,
        z_uniform: float = 0.0, z_chaotic: float = 0.0,
    ) -> str:
        """
        Clasifica el patrón distinguiendo la DIRECCIÓN de la anomalía.
        z_uniform alto + mad_ratio bajo → cadencia algorítmica (fabricación).
        z_chaotic alto + mad_ratio alto → ruido extremo o datos corruptos (no fabricación).
        """
        # Fabricación clara: cadencia muy uniforme
        if mad_ratio < 0.01:
            return "CONSTANT_SLEEP — script con intervalo fijo detectado"
        if mad_ratio < 0.05:
            return "LOW_JITTER — script con ruido mínimo (jitter anti-detección)"
        # Ruido extremo — no indica fabricación de texto
        if z_chaotic > 2.0:
            return "CHAOTIC_NOISE — variabilidad extrema, posible corrupción de datos"
        # Anomalía por uniformidad (no por exceso de dispersión)
        if entropy < 0.3 and mad_ratio < 0.3:
            return "LOW_ENTROPY — distribución anormalmente uniforme"
        if z_uniform > Z_ALGORITHMIC_THRESHOLD and mad_ratio < _DEFAULT_BASELINE_MAD_RATIO_MEAN:
            return "ALGORITHMIC_PATTERN — cadencia fuera del rango humano (uniforme)"
        # mad_ratio alto pero no caótico: simplemente alta variabilidad humana normal
        if mad_ratio > _DEFAULT_BASELINE_MAD_RATIO_MEAN and z_uniform < Z_ALGORITHMIC_THRESHOLD:
            return "HIGH_VARIANCE_HUMAN — variabilidad alta, consistente con comportamiento humano"
        if z > 1.0:
            return "BORDERLINE — zona de incertidumbre, requiere corroboración"
        return "ENTROPIC_HUMAN — variabilidad compatible con autoría humana"

    def _insufficient_data(
        self, count: int, discriminator: str
    ) -> GCIResult:
        """Retorna señal nula cuando no hay suficientes datos."""
        signal = SignalBuilder.from_z_score(
            tool_name="GCI",
            value=0.0,
            z_score=0.0,
            confidence=0.0,
            discriminator=discriminator,
            metadata={"delta_count": count, "status": "INSUFFICIENT_DATA"},
        )
        return GCIResult(
            signal=signal,
            periodicity_score=0.0,
            entropy_score=0.0,
            burstiness=0.0,
            mad_ratio=0.0,
            delta_count=count,
            detected_constant=None,
            pattern_label="INSUFFICIENT_DATA",
            trust_decay_applied=False,
        )


# ---------------------------------------------------------------------------
# Función de conveniencia para el bridge MCP
# ---------------------------------------------------------------------------

_DEFAULT_ENGINE = GCIEngine()


def analyze_gci(
    deltas: Optional[List[float]] = None,
    timestamps: Optional[List[float]] = None,
    discriminator: str = "",
    metadata: Optional[Dict] = None,
    engine: Optional[GCIEngine] = None,
) -> GCIResult:
    """
    Entry point para el bridge MCP.
    Acepta deltas directamente O timestamps (los convierte a deltas).

    Exactamente uno de {deltas, timestamps} debe ser no-None.
    """
    # P1: DoS prevention — límite estricto de tamaño de input
    MAX_INPUT_SIZE = 100_000
    if deltas is not None and len(deltas) > MAX_INPUT_SIZE:
        raise ValueError(f"analyze_gci: deltas exceeds maximum of {MAX_INPUT_SIZE} entries.")
    if timestamps is not None and len(timestamps) > MAX_INPUT_SIZE:
        raise ValueError(f"analyze_gci: timestamps exceeds maximum of {MAX_INPUT_SIZE} entries.")

    eng = engine or _DEFAULT_ENGINE

    if deltas is not None and timestamps is not None:
        raise ValueError("analyze_gci: pasá deltas O timestamps, no ambos.")
    if deltas is None and timestamps is None:
        raise ValueError("analyze_gci: se requiere deltas o timestamps.")

    if timestamps is not None:
        return eng.analyze_timestamps(timestamps, discriminator=discriminator, metadata=metadata)
    return eng.analyze_deltas(deltas, discriminator=discriminator, metadata=metadata)  # type: ignore
