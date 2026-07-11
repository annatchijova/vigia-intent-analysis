"""
vigia/governance/risk_bounded_layer.py
─────────────────────────────────────────────────────────────────────────────
Gobernanza y Riesgo — VIGÍA Forensic Suite EBS v1

ARQUITECTURA: Capa 3 — Gobernanza
REGLA DE AISLAMIENTO: Lee de models/ y engine/. No lee de audit/ ni action/.

COMPONENTES:
    RiskBoundedDecisionLayer   — función de riesgo + regla ACCEPT/REJECT/ABSTAIN
    SelfAdaptiveRiskPolicy     — actualización de λ, γ, ε via feedback histórico
    PolicyStabilityController  — momentum + amortiguación para evitar oscilación

FUNCIÓN DE RIESGO (formulación final acordada por colectivo):

    r_total = (1 - P) · (1 + λ·D) · (1 + γ·(1 - S)) · (1 + ω·(1 - I))

    Donde:
        P = posterior ∈ [0, 1]      — P(fabricación | evidencia)
        D = drift_score ∈ [0, 1]   — PSI / KL de la distribución actual vs referencia
        S = graph_stability ∈ [0,1] — estabilidad promedio del EvidenceGraph
        I = consistency_score ∈ [0,1] — consistencia de intención abductiva (AbductiveIntentEngine)
        λ = sensibilidad al drift (adaptativo)
        γ = sensibilidad a inestabilidad estructural (adaptativo)
        ω = sensibilidad a disonancia de intención (adaptativo, default 1.0)

    PROPIEDADES MATEMÁTICAS:
        - D=0, S=1 → r = (1-P)       — riesgo base puro
        - D alto → r inflado          — drift infla incertidumbre
        - S bajo → r inflado          — grafo caótico fuerza ABSTAIN
        - r nunca → 0 por S alto      — sin sobreconfianza estructural

    REGLA DE DECISIÓN (ε-bounded):
        ACCEPT  si r ≤ ε_accept
        REJECT  si r ≥ 1 - ε_reject
        ABSTAIN en caso contrario  (zona de incertidumbre honesta)

INVARIANTES DE GOBERNANZA (no negociables):
    - drift siempre inflaciona riesgo (λ > 0 siempre)
    - inestabilidad estructural nunca reduce riesgo (γ > 0 siempre)
    - ABSTAIN es salida válida y auditaable — no indica fallo del sistema
    - posterior nunca se fuerza a 0 ni a 1 por política

META-CALIBRACIÓN (SelfAdaptiveRiskPolicy):
    El sistema aprende sus propios parámetros de sensibilidad sin ML opaco:
        λ_t = λ_{t-1} · (1 + α_fn · fn_rate - α_fp · fp_rate)
        γ_t = γ_{t-1} · (1 + fp_rate - fn_rate)
        ε_t = ε_{t-1} · (1 + abst_rate - target_abst_rate)

    Estabilizado por PolicyStabilityController (momentum + damping).
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _NP_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    _NP_AVAILABLE = False

import os as _os_gov, sys as _sys_gov
_ROOT_GOV = _os_gov.path.dirname(_os_gov.path.dirname(_os_gov.path.abspath(__file__)))
if _ROOT_GOV not in _sys_gov.path:
    _sys_gov.path.insert(0, _ROOT_GOV)

from vigia.core.ebs_v1 import (
    DecisionTrace, PolicySpec, SystemState,
    DecisionVerdict, EPS_NUMERIC,
)


# ---------------------------------------------------------------------------
# PolicyStabilityController
# ---------------------------------------------------------------------------

class PolicyStabilityController:
    """
    Controlador de estabilidad para parámetros adaptativos (λ, γ, ε).

    PROBLEMA QUE RESUELVE:
        Con actualización adaptativa, λ/γ/ε pueden amplificarse mutuamente
        generando inestabilidad de segundo orden (ciclos de feedback).

    SOLUCIÓN:
        - Momentum acumulado: suaviza cambios bruscos
        - Damping: amortiguación si Δθ > τ (cambio excesivo)
        - Clamping: rangos absolutos fuera de los cuales el sistema es indefendible

    Esto convierte la política en un controlador estable tipo PD discreto.
    """

    # Rangos absolutos — fuera de esto el sistema es indefendible ante Daubert
    LAMBDA_RANGE: Tuple[float, float] = (0.1, 15.0)
    GAMMA_RANGE: Tuple[float, float] = (0.1, 15.0)
    EPSILON_RANGE: Tuple[float, float] = (0.005, 0.30)

    def __init__(
        self,
        tau: float = 0.20,        # umbral de cambio excesivo
        damping: float = 0.5,     # factor de amortiguación
        momentum: float = 0.80,   # inercia del controlador
    ) -> None:
        self.tau = tau
        self.damping = damping
        self.momentum = momentum

        self._prev_theta: Optional[List[float]] = None

        if _NP_AVAILABLE:
            self._velocity = np.zeros(3)
        else:
            self._velocity = [0.0, 0.0, 0.0]

    def stabilize(
        self,
        lambda_t: float,
        gamma_t: float,
        epsilon_t: float,
    ) -> Tuple[float, float, float]:
        """
        Aplica control de estabilidad a los parámetros propuestos.

        Retorna: (lambda_estabilizado, gamma_estabilizado, epsilon_estabilizado)
        """
        theta = [lambda_t, gamma_t, epsilon_t]

        if self._prev_theta is None:
            self._prev_theta = theta[:]
            return lambda_t, gamma_t, epsilon_t

        if _NP_AVAILABLE:
            theta_arr = np.array(theta)
            prev_arr = np.array(self._prev_theta)

            delta = theta_arr - prev_arr

            # Actualizar velocidad con momentum
            self._velocity = (
                self.momentum * self._velocity +
                (1.0 - self.momentum) * delta
            )

            norm_delta = float(np.linalg.norm(delta))

            # Amortiguar si el cambio es demasiado brusco
            if norm_delta > self.tau:
                theta_arr = prev_arr + self.damping * delta

            # Corrección por momentum suave (inercia estabilizadora)
            theta_arr = theta_arr - 0.1 * self._velocity

            result = theta_arr.tolist()
        else:
            # Fallback stdlib
            delta = [theta[i] - self._prev_theta[i] for i in range(3)]
            norm_delta = math.sqrt(sum(d ** 2 for d in delta))

            for i in range(3):
                self._velocity[i] = (
                    self.momentum * self._velocity[i] +
                    (1.0 - self.momentum) * delta[i]
                )

            if norm_delta > self.tau:
                theta = [self._prev_theta[i] + self.damping * delta[i] for i in range(3)]

            result = [theta[i] - 0.1 * self._velocity[i] for i in range(3)]

        # Clamping absoluto
        result[0] = max(self.LAMBDA_RANGE[0], min(self.LAMBDA_RANGE[1], result[0]))
        result[1] = max(self.GAMMA_RANGE[0], min(self.GAMMA_RANGE[1], result[1]))
        result[2] = max(self.EPSILON_RANGE[0], min(self.EPSILON_RANGE[1], result[2]))

        self._prev_theta = result[:]
        return result[0], result[1], result[2]

    def reset(self) -> None:
        """Resetea el estado del controlador (ej: al cargar nuevo caso)."""
        self._prev_theta = None
        if _NP_AVAILABLE:
            self._velocity = np.zeros(3)
        else:
            self._velocity = [0.0, 0.0, 0.0]


# ---------------------------------------------------------------------------
# SelfAdaptiveRiskPolicy
# ---------------------------------------------------------------------------

class SelfAdaptiveRiskPolicy:
    """
    Política de sensibilidad al riesgo autoajustable.

    No usa ML opaco. Usa feedback control basado en error histórico:
        - Falsos positivos (fp): sistema muy agresivo → reducir λ, γ
        - Falsos negativos (fn): sistema muy conservador → aumentar λ
        - Abstenciones excesivas: sistema incierto → ajustar ε

    Estabilizado por PolicyStabilityController para evitar oscilación.

    INVARIANTES QUE NO CAMBIAN (anclas del sistema):
        - λ > 0 siempre  → drift siempre inflaciona riesgo
        - γ > 0 siempre  → inestabilidad nunca reduce riesgo
        - ABSTAIN sigue siendo salida válida independientemente de ε
    """

    def __init__(
        self,
        lambda_init: float = 2.0,
        gamma_init: float = 2.0,
        epsilon_init: float = 0.05,
        target_abstain_rate: float = 0.10,   # ~10% abstención es saludable en DFIR
        stability_controller: Optional[PolicyStabilityController] = None,
    ) -> None:
        self.lambda_t = lambda_init
        self.gamma_t = gamma_init
        self.epsilon_accept = epsilon_init
        self.epsilon_reject = epsilon_init

        self.target_abstain_rate = target_abstain_rate
        self._controller = stability_controller or PolicyStabilityController()

        self._history: List[Dict[str, Any]] = []
        self._update_count = 0

    def update_from_window(
        self,
        history_window: List[Dict[str, Any]],
        window_size: int = 50,
    ) -> Dict[str, float]:
        """
        Actualiza λ, γ, ε basándose en una ventana de errores históricos.

        history_window: lista de dicts con campos:
            {"fp": bool, "fn": bool, "abstain": bool, "ground_truth": str, "decision": str}

        Retorna: {"lambda": float, "gamma": float, "epsilon": float}
        """
        if not history_window:
            return self._current_params()

        window = history_window[-window_size:]
        n = len(window) + EPS_NUMERIC

        fp_rate = sum(1 for h in window if h.get("fp", False)) / n
        fn_rate = sum(1 for h in window if h.get("fn", False)) / n
        abst_rate = sum(1 for h in window if h.get("abstain", False)) / n

        # Reglas de actualización estructurales (no ML)
        # λ: sube si hay FN (perdimos fabricaciones), baja si hay FP
        lambda_new = self.lambda_t * (1.0 + 0.5 * fn_rate - 0.5 * fp_rate)

        # γ: sube si hay FP (grafo inestable producía decisiones erróneas)
        gamma_new = self.gamma_t * (1.0 + fp_rate - 0.5 * fn_rate)

        # ε: sube si hay demasiadas abstenciones (sistema demasiado incierto)
        epsilon_new = self.epsilon_accept * (
            1.0 + (abst_rate - self.target_abstain_rate)
        )

        # Estabilizar con PolicyStabilityController
        lambda_stable, gamma_stable, epsilon_stable = self._controller.stabilize(
            lambda_new, gamma_new, epsilon_new
        )

        self.lambda_t = lambda_stable
        self.gamma_t = gamma_stable
        self.epsilon_accept = epsilon_stable
        self.epsilon_reject = epsilon_stable
        self._update_count += 1

        logger.debug(
            "[AdaptivePolicy] Update #%d: λ=%.3f γ=%.3f ε=%.4f | fp=%.2f fn=%.2f abst=%.2f",
            self._update_count,
            self.lambda_t, self.gamma_t, self.epsilon_accept,
            fp_rate, fn_rate, abst_rate,
        )

        return self._current_params()

    def record_decision(
        self,
        decision: str,
        ground_truth: Optional[str],
        posterior: float,
    ) -> None:
        """
        Registra una decisión para feedback futuro.

        ground_truth: "FABRICATED" | "AUTHENTIC" | None (si no está disponible)
        """
        if ground_truth is None:
            return

        is_fabricated = ground_truth.upper() in ("FABRICATED", "ADVERSARIAL", "REJECT")
        is_authentic = ground_truth.upper() in ("AUTHENTIC", "ACCEPT")

        fp = (decision == "REJECT" and is_authentic)
        fn = (decision == "ACCEPT" and is_fabricated)
        abstain = (decision == "ABSTAIN")

        self._history.append({
            "decision": decision,
            "ground_truth": ground_truth,
            "posterior": posterior,
            "fp": fp,
            "fn": fn,
            "abstain": abstain,
        })

    def _current_params(self) -> Dict[str, float]:
        return {
            "lambda": self.lambda_t,
            "gamma": self.gamma_t,
            "epsilon_accept": self.epsilon_accept,
            "epsilon_reject": self.epsilon_reject,
        }

    def to_system_state(self, **kwargs) -> SystemState:
        """Exporta parámetros actuales como SystemState para el bundle."""
        return SystemState(
            lambda_drift=self.lambda_t,
            gamma_stability=self.gamma_t,
            epsilon_accept=self.epsilon_accept,
            epsilon_reject=self.epsilon_reject,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# RiskBoundedDecisionLayer
# ---------------------------------------------------------------------------

class RiskBoundedDecisionLayer:
    """
    Capa de decisión con límites formales de riesgo.

    Implementa la función de riesgo acordada por el colectivo:
        r_total = (1 - P) · (1 + λ·D) · (1 + γ·(1 - S))

    PROPIEDAD FORMAL:
        Bajo drift acotado D ≤ δ, se garantiza:
            P(error decisión) ≤ ε (con ε y δ apropiados)

    El sistema PREFIERE ABSTENCIÓN antes que un error no controlado bajo drift.
    Esta es la diferencia fundamental respecto a sistemas heurísticos:
        - Sistema heurístico: fuerza decisión aunque el riesgo sea alto
        - VIGÍA: ABSTAIN si r_total ∈ (ε_accept, 1 - ε_reject)
    """

    # Límites absolutos de riesgo — hardcoded, no adaptables
    R_MIN: float = 0.0
    R_MAX: float = 5.0   # teóricamente puede superar 1.0 → siempre REJECT

    def __init__(
        self,
        policy: Optional[SelfAdaptiveRiskPolicy] = None,
        epsilon_accept: float = 0.05,
        epsilon_reject: float = 0.05,
        lambda_drift: float = 2.0,
        gamma_stability: float = 2.0,
    ) -> None:
        self._policy = policy
        # Si hay política adaptativa, sus parámetros tienen precedencia
        if policy is not None:
            self._lambda = policy.lambda_t
            self._gamma = policy.gamma_t
            self._eps_accept = policy.epsilon_accept
            self._eps_reject = policy.epsilon_reject
        else:
            self._lambda = lambda_drift
            self._gamma = gamma_stability
            self._eps_accept = epsilon_accept
            self._eps_reject = epsilon_reject

    @classmethod
    def from_policy_spec(cls, policy_spec) -> "RiskBoundedDecisionLayer":
        """
        Construye RiskBoundedDecisionLayer desde PolicySpec sellado en el bundle.
        BLOQUE 4: la decision ACCEPT/REJECT lee epsilon_accept/epsilon_reject
        del PolicySpec — ningun umbral hardcodeado en el codigo.
        """
        return cls(
            epsilon_accept=policy_spec.epsilon_accept,
            epsilon_reject=policy_spec.epsilon_reject,
            lambda_drift=policy_spec.lambda_drift_init,
            gamma_stability=policy_spec.gamma_stability_init,
        )

    def compute_risk(
        self,
        posterior: float,
        drift_score: float = 0.0,
        graph_stability: float = 1.0,
        lambda_override: Optional[float] = None,
        gamma_override: Optional[float] = None,
        consistency_score: float = 1.0,
        omega_override: Optional[float] = None,
    ) -> float:
        """
        Calcula r_total usando aritmética de punto fijo (Decimal) para
        determinismo cross-plataforma (Intel x86 / ARM / RISC-V).

        r = (1-P) · (1+λD) · (1+γ(1-S)) · (1+ω(1-I))

        Args:
            posterior        : P(fabricación | evidencia) ∈ [0, 1]
            drift_score      : D ∈ [0, 1]
            graph_stability  : S ∈ [0, 1]
            consistency_score: I ∈ [0, 1] — del AbductiveIntentEngine (H3/soberana)
            lambda_override  : sobreescribe λ actual
            gamma_override   : sobreescribe γ actual
            omega_override   : sobreescribe ω actual

        Returns:
            r_total como float — calculado internamente con Decimal (28 dígitos)
        """
        # Sincronizar con política adaptativa si existe
        if self._policy is not None:
            self._lambda = self._policy.lambda_t
            self._gamma = self._policy.gamma_t
            self._eps_accept = self._policy.epsilon_accept
            self._eps_reject = self._policy.epsilon_reject

        lam = lambda_override if lambda_override is not None else self._lambda
        gam = gamma_override if gamma_override is not None else self._gamma
        ome = omega_override if omega_override is not None else getattr(self, "_omega", 1.0)

        # Clipping defensivo de inputs — antes de convertir a Decimal
        p = max(0.0, min(1.0, posterior))
        d = max(0.0, min(1.0, drift_score))
        s = max(0.0, min(1.0, graph_stability))
        i_score = max(0.0, min(1.0, consistency_score))
        lam = max(0.0, lam)
        gam = max(0.0, gam)
        ome = max(0.0, ome)

        # Aritmética Decimal — 28 dígitos significativos, ROUND_HALF_EVEN
        # Elimina variación de FPU entre arquitecturas (H3 — Daubert determinismo)
        _D = Decimal
        r = (
            (_D(1) - _D(str(p)))
            * (_D(1) + _D(str(lam)) * _D(str(d)))
            * (_D(1) + _D(str(gam)) * (_D(1) - _D(str(s))))
            * (_D(1) + _D(str(ome)) * (_D(1) - _D(str(i_score))))
        )

        # Convertir a float para compatibilidad con el resto del sistema
        r_float = float(r.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))
        return max(self.R_MIN, min(self.R_MAX, r_float))

    def decide(
        self,
        posterior: float,
        drift_score: float = 0.0,
        graph_stability: float = 1.0,
        inference_result: Optional[Dict[str, Any]] = None,
        consistency_score: float = 1.0,
    ) -> DecisionTrace:
        """
        Produce una DecisionTrace completa con veredicto, trazabilidad y reason_code.

        Args:
            posterior        : del LikelihoodEngine.infer()
            drift_score      : del DriftMonitor o PSI externo
            graph_stability  : del EvidenceGraph.global_stability()
            inference_result : resultado completo del LikelihoodEngine
            consistency_score: del AbductiveIntentEngine [0,1] — factor I

        Returns:
            DecisionTrace con ACCEPT / REJECT / ABSTAIN, reason_code y causa explícita
        """
        # Sincronizar parámetros
        if self._policy is not None:
            self._lambda = self._policy.lambda_t
            self._gamma = self._policy.gamma_t
            self._eps_accept = self._policy.epsilon_accept
            self._eps_reject = self._policy.epsilon_reject

        r = self.compute_risk(
            posterior, drift_score, graph_stability,
            consistency_score=consistency_score,
        )

        # Regla de decisión ε-bounded con reason_code explícito (H18)
        if r <= self._eps_accept:
            verdict: DecisionVerdict = "ACCEPT"
            reason_code = "ACCEPT_POSTERIOR"
            abstain_reason = ""
        elif r >= (1.0 - self._eps_reject):
            verdict = "REJECT"
            reason_code = "REJECT_POSTERIOR"
            abstain_reason = ""
        else:
            verdict = "ABSTAIN"
            # Determinar causa dominante del ABSTAIN para el perito
            d_clamp = max(0.0, min(1.0, drift_score))
            s_clamp = max(0.0, min(1.0, graph_stability))
            i_clamp = max(0.0, min(1.0, consistency_score))
            if d_clamp > 0.2 and d_clamp >= (1.0 - s_clamp) and d_clamp >= (1.0 - i_clamp):
                reason_code = "ABSTAIN_DRIFT"
                abstain_reason = (
                    f"Drift severo (D={d_clamp:.3f} > 0.2) — distribución de señales "
                    "diverge de la referencia. Verificar integridad del dataset."
                )
            elif s_clamp < 0.8 and (1.0 - s_clamp) >= (1.0 - i_clamp):
                reason_code = "ABSTAIN_INSTABILITY"
                abstain_reason = (
                    f"Inestabilidad estructural (S={s_clamp:.3f} < 0.8) — grafo de "
                    "evidencia inconsistente. Revisar artefactos contradictorios."
                )
            elif i_clamp < 0.5:
                reason_code = "ABSTAIN_INTENTION"
                abstain_reason = (
                    f"Disonancia semántica (I={i_clamp:.3f} < 0.5) — el motor de "
                    "abducción no encontró hipótesis de intención consistente con "
                    "el posterior estadístico."
                )
            else:
                reason_code = "ABSTAIN_ZONE"
                abstain_reason = (
                    f"Zona de incertidumbre honesta (r={r:.4f}, "
                    f"ε_accept={self._eps_accept:.4f}, "
                    f"ε_reject={self._eps_reject:.4f}). "
                    "Evidencia insuficiente para decisión unilateral."
                )

        # Extraer contribuciones de señales si hay resultado de inferencia
        signal_contributions = None
        log_lr = 0.0
        lr = 1.0
        components_used = 0
        if inference_result:
            signal_contributions = inference_result.get("contributions", [])
            log_lr = inference_result.get("log_lr", 0.0)
            lr = inference_result.get("lr", 1.0)
            components_used = inference_result.get("components_used", 0)

        omega = getattr(self, "_omega", 1.0)
        trace = DecisionTrace(
            decision=verdict,
            posterior=max(0.0, min(1.0, posterior)),
            risk=r,
            log_lr=log_lr,
            lr=lr,
            drift_score=drift_score,
            graph_stability=graph_stability,
            lambda_drift=self._lambda,
            gamma_stability=self._gamma,
            epsilon_used=self._eps_accept,
            components_used=components_used,
            signal_contributions=signal_contributions,
            reason_code=reason_code,
            abstain_reason=abstain_reason,
            omega_intention=omega,
            consistency_score=consistency_score,
        )

        logger.info(
            "[RiskLayer] P=%.4f D=%.4f S=%.4f I=%.4f → r=%.6f → %s [%s]",
            posterior, drift_score, graph_stability, consistency_score,
            r, verdict, reason_code,
        )

        return trace

    # ------------------------------------------------------------------
    # PSI (Population Stability Index) — drift básico
    # ------------------------------------------------------------------

    @staticmethod
    def compute_psi(
        expected: List[float],
        actual: List[float],
        bins: Optional[int] = None,
    ) -> float:
        """
        Calcula PSI entre distribución de referencia y actual.

        PSI < 0.1  → sin drift
        PSI 0.1-0.2 → drift moderado
        PSI > 0.2  → drift severo

        El número de bins es dinámico por regla de Sturges (H6):
            bins = ceil(1 + log2(n))
        Esto evita división por cero y sesgo estadístico con muestras pequeñas.
        El parámetro bins permite override explícito para tests de regresión.
        """
        if not expected or not actual:
            return 0.0

        eps = 1e-6
        all_vals = expected + actual
        v_min, v_max = min(all_vals), max(all_vals)

        if v_max == v_min:
            return 0.0

        # Regla de Sturges: k = ceil(1 + log2(n)) con n = tamaño de referencia
        if bins is None:
            n_ref = len(expected)
            bins = max(3, math.ceil(1.0 + math.log2(max(n_ref, 2))))

        def hist_freq(vals: List[float]) -> List[float]:
            counts = [0] * bins
            for v in vals:
                idx = min(bins - 1, int((v - v_min) / (v_max - v_min + eps) * bins))
                counts[idx] += 1
            n = len(vals) + eps
            return [(c + eps) / n for c in counts]

        e_freq = hist_freq(expected)
        a_freq = hist_freq(actual)

        psi = sum(
            (e - a) * math.log(e / a)
            for e, a in zip(e_freq, a_freq)
        )
        return max(0.0, psi)

    @staticmethod
    def psi_to_drift_score(psi: float) -> float:
        """Normaliza PSI a [0, 1] para usar en compute_risk."""
        # PSI > 0.25 → drift severo (score = 1.0)
        return min(1.0, psi / 0.25)

    # chi-square 0.95 quantiles by degrees of freedom, for the H27 null gate.
    # Fallback for uncovered df: df + 2*sqrt(2*df) (normal approximation).
    _CHI2_95 = {
        2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592,
        7: 14.067, 8: 15.507, 9: 16.919, 10: 18.307,
    }

    @classmethod
    def internal_drift_from_z_scores(
        cls,
        z_scores: List[float],
        alpha: float = 1.0,
    ) -> Optional[float]:
        """
        H27 internal drift: PSI of the case's z-scores against the analytic
        standard normal N(0,1), gated by the PSI null distribution (B-099).

        Replaces two degenerate estimators that both saturated to drift=1.0
        for benign and anomalous input alike at forensic sample sizes
        (measured: 100% of 20k genuine N(0,1) samples at n=2-3, 67-100% up to
        n=50 for the seed-42 sampled reference; 82-97% for the split-half
        variant, which additionally cannot detect a shift at all because both
        halves share it):

        - Reference probabilities are computed from the normal CDF per bin —
          no RNG, no sampling noise, fully deterministic.
        - Actual proportions use Dirichlet smoothing toward the reference
          (alpha), so an empty bin contributes a bounded term instead of the
          eps-blowup that made compute_psi saturate.
        - Under H0 (no drift) the sampled PSI is approximately chi2(k-1)/n,
          which alone exceeds the 0.25 large-sample rule for n <= ~15. The
          0.95 null quantile is subtracted before normalizing, so genuine
          data yields drift 0 (false-saturation measured <= 2%) while shifted
          or extreme data still saturates from n=4.

        Returns None when n < 4: below that the test has no power in either
        direction (even all-z=5 input scores 0), so the honest output is
        "indeterminate", not a number. Callers must fall back to their
        documented external drift and log the degradation.
        """
        n = len(z_scores)
        if n < 4:
            return None

        k = max(3, math.ceil(1.0 + math.log2(n)))
        lo, hi = -3.0, 3.0
        width = (hi - lo) / k

        def _phi(x: float) -> float:
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        # Reference bin probabilities from N(0,1); tails folded into end bins
        # to mirror the clipping of the actual values below.
        p_ref = []
        for i in range(k):
            p_lo = 0.0 if i == 0 else _phi(lo + i * width)
            p_hi = 1.0 if i == k - 1 else _phi(lo + (i + 1) * width)
            p_ref.append(p_hi - p_lo)

        counts = [0] * k
        for z in z_scores:
            zc = max(lo, min(hi - 1e-12, float(z)))
            counts[min(k - 1, int((zc - lo) / width))] += 1

        psi = 0.0
        for i in range(k):
            p_act = (counts[i] + alpha * p_ref[i]) / (n + alpha)
            psi += (p_act - p_ref[i]) * math.log(p_act / p_ref[i])

        df = k - 1
        chi2_95 = cls._CHI2_95.get(df, df + 2.0 * math.sqrt(2.0 * df))
        null_95 = chi2_95 / n
        return min(1.0, max(0.0, psi - null_95) / 0.25)
