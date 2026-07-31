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

    r_total = P · (1 + λ·D) · (1 + γ·(1 - S)) · (1 + ω·(1 - I))

    Donde:
        P = posterior ∈ [0, 1]      — P(fabricación | evidencia)
        D = drift_score ∈ [0, 1]   — PSI / KL de la distribución actual vs referencia
        S = graph_stability ∈ [0,1] — estabilidad promedio del EvidenceGraph
        I = consistency_score ∈ [0,1] — consistencia de intención abductiva (AbductiveIntentEngine)
        λ = sensibilidad al drift (adaptativo)
        γ = sensibilidad a inestabilidad estructural (adaptativo)
        ω = sensibilidad a disonancia de intención (adaptativo, default 1.0)

    SEMÁNTICA CRÍTICA (B-117, fix de inversión 2026-07-14):
        P = P(fabricación | evidencia) — emitido por LikelihoodEngine.infer().
        r = riesgo de fabricación = P * factores_de_inflación.
        Caso fabricado:  P alto (~0.99) -> r alto -> REJECT.
        Caso genuino:    P bajo (~0.01) -> r bajo -> ACCEPT.

        BUG ORIGINAL: la fórmula usaba (1-P), lo que INVERTÍA los veredictos:
        P alto (fabricado) producía r bajo -> ACCEPT el fabricado.
        El huérfano governance/risk_bounded_layer_v2.py documentaba este bug
        como fix P0-001 cambiando la semántica de P a P(autenticidad), pero
        nunca se cableó. El fix correcto es mantener P = P(fabricación) (que
        es lo que emite el LikelihoodEngine) y usar r = P * (...), no (1-P).

    PROPIEDADES MATEMÁTICAS:
        - D=0, S=1 → r = P            — riesgo base puro
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
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _NP_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    _NP_AVAILABLE = False

# B-097 root cause: this module inserted <repo>/vigia into sys.path at
# import time (under aliased names, invisible to naive greps), shadowing
# top-level packages process-wide. All imports here are vigia.-qualified;
# the insert served nothing.

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
        r_total = P · (1 + λ·D) · (1 + γ·(1 - S))

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

        r = P · (1+λD) · (1+γ(1-S)) · (1+ω(1-I))

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
        #
        # B-117 (2026-07-14): r = P * (...), NOT (1-P) * (...).
        # P = P(fabricación | evidencia) from LikelihoodEngine.
        # P alto (fabricado) -> r alto -> REJECT.
        # The original (1-P) INVERTED this: P alto -> r bajo -> ACCEPT.
        # See module docstring for full derivation of the fix.
        _D = Decimal
        r = (
            _D(str(p))
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

        # B-218 fix: epsilon_used must name the threshold that actually
        # decided the verdict -- ACCEPT is gated by eps_accept, REJECT by
        # eps_reject. Before this fix, epsilon_used was always eps_accept
        # regardless of verdict, so a REJECT decided by eps_reject sealed
        # the wrong threshold on the trace (and, downstream, on the bundle
        # -- see pipeline.py's SystemState construction, fixed separately).
        # ABSTAIN has no single deciding threshold (the case fell strictly
        # between both); eps_accept is kept as the reference value there,
        # unchanged from prior behavior -- abstain_reason already surfaces
        # both real values in its text for that case.
        if verdict == "REJECT":
            epsilon_used = self._eps_reject
        else:
            epsilon_used = self._eps_accept

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
            epsilon_used=epsilon_used,
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

        WARNING (B-099): do NOT use this for drift over small samples. Its
        eps=1e-6 empty-bin handling blows PSI past the 0.25 saturation
        threshold whenever the actual sample is small (measured: drift=1.0
        for benign and anomalous input alike up to n~50), and the 0.25
        large-sample rule ignores the PSI null distribution (~chi2(k-1)/n).
        For case-level internal drift use internal_drift_from_z_scores(),
        which replaced every production call site of this function.

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
    # B-104: exact rational constants — k is clamped to 12 (df <= 11), so the
    # table always covers the request and no runtime sqrt fallback exists.
    _CHI2_95 = {
        2: Fraction(5991, 1000), 3: Fraction(7815, 1000),
        4: Fraction(9488, 1000), 5: Fraction(11070, 1000),
        6: Fraction(12592, 1000), 7: Fraction(14067, 1000),
        8: Fraction(15507, 1000), 9: Fraction(16919, 1000),
        10: Fraction(18307, 1000), 11: Fraction(19675, 1000),
    }

    # B-104: frozen N(0,1) reference bin probabilities per bin count k, as
    # exact rationals (numerators over 10**17; the middle bin absorbs the
    # rounding residue so each row sums to exactly 1). Generated once from
    # the normal CDF and FROZEN — determinism comes from fixing the
    # constants, not from recomputing them through a platform's libm erf.
    _P_REF_SCALE = 10 ** 17
    _P_REF_NUM = {
        3: [15865525393145708, 68268949213708584, 15865525393145708],
        4: [6680720126885809, 43319279873114192, 43319279873114190,
            6680720126885809],
        5: [3593031911292582, 23832279863714772, 45149376449985270,
            23832279863714788, 3593031911292588],
        6: [2275013194817921, 13590512198327786, 34134474606854292,
            34134474606854294, 13590512198327786, 2275013194817921],
        7: [1606228560382833, 8320911123950270, 23484617405429360,
            33176485820475064, 23484617405429376, 8320911123950259,
            1606228560382838],
        8: [1222447265504473, 5458272861381336, 15982015110801012,
            27337264762313180, 27337264762313173, 15982015110801018,
            5458272861381341, 1222447265504467],
        9: [981532862864532, 3797502364416938, 11086490165864238,
            21078608625030652, 26111731963647260, 21078608625030672,
            11086490165864238, 3797502364416938, 981532862864532],
        10: [819753592459616, 2773278318832967, 7913935110878240,
             15918344752836532, 22574688224992644, 22574688224992623,
             15918344752836556, 7913935110878234, 2773278318832972,
             819753592459616],
        11: [705314147368980, 2107204116729366, 5821583806839076,
             12028566703744598, 18590474652695944, 21493713145244057,
             18590474652695944, 12028566703744614, 5821583806839070,
             2107204116729366, 705314147368985],
        12: [620966532577616, 1654046662240305, 4405706932067888,
             9184805266259898, 14988228479452980, 19146246127401312,
             19146246127401314, 14988228479452980, 9184805266259898,
             4405706932067888, 1654046662240305, 620966532577616],
    }

    # ln(2) to 28 digits, exact rational — anchor for the range reduction.
    _LN2 = Fraction(6931471805599453094172321215, 10 ** 28)

    @classmethod
    def _ln_fraction(cls, x: Fraction, terms: int = 12) -> Fraction:
        """Natural log over Fraction — deterministic, no libm (B-104).

        Power-of-two range reduction to [3/4, 3/2), then the atanh series
        ln(x) = 2*sum(z^(2i+1)/(2i+1)) with z=(x-1)/(x+1), |z| <= 0.2, which
        converges past double precision within 12 terms (validated worst
        error 8.9e-16 against math.log over [1e-6, 1e6]). The result is
        denominator-limited to keep Fraction arithmetic bounded.
        """
        if x <= 0:
            raise ValueError("ln domain: x must be > 0")
        e = 0
        while x >= 2:
            x /= 2
            e += 1
        while x < 1:
            x *= 2
            e -= 1
        if x > Fraction(3, 2):
            x /= 2
            e += 1
        z = (x - 1) / (x + 1)
        z2 = z * z
        term = z
        total = Fraction(0)
        for i in range(terms):
            total += term / (2 * i + 1)
            term *= z2
        return (2 * total + e * cls._LN2).limit_denominator(10 ** 30)

    @classmethod
    def internal_drift_from_z_scores(
        cls,
        z_scores: List[float],
        alpha: int = 1,
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

        - Reference probabilities are FROZEN rational constants per bin
          count (_P_REF_NUM) — no RNG, no sampling noise, no libm.
        - Actual proportions use Dirichlet smoothing toward the reference
          (alpha), so an empty bin contributes a bounded term instead of the
          eps-blowup that made compute_psi saturate.
        - Under H0 (no drift) the sampled PSI is approximately chi2(k-1)/n,
          which alone exceeds the 0.25 large-sample rule for n <= ~15. The
          0.95 null quantile is subtracted before normalizing, so genuine
          data yields drift 0 (false-saturation measured <= 2%) while shifted
          or extreme data still saturates from n=4.

        Determinism (B-104, review follow-up of B-099 / invariant #4): the
        whole kernel is integer/rational arithmetic — bin count k from
        bit_length (not log2), bin assignment via exact Fraction conversion
        of each z, PSI via _ln_fraction, chi2 constants rational. The single
        float() at the end is a correctly-rounded conversion of an exactly
        computed rational, so the sealed drift_score is bit-for-bit
        reproducible across platforms and libm versions. Values agree with
        the previous float implementation to <2e-15 (3000-sweep validation,
        zero boundary flips).

        Returns None when fewer than 4 FINITE z-scores are available: below
        that the test has no power in either direction (even all-z=5 input
        scores 0), so the honest output is "indeterminate", not a number.
        Callers must fall back to their documented external drift and log the
        degradation.

        Non-finite values (NaN/inf) are dropped here rather than trusted to
        callers (B-103): Python's min/max comparison semantics silently clip
        NaN into the top bin, so unfiltered NaN z-scores counted as extreme
        +3 observations and drove drift to 1.0.
        """
        details = cls.internal_drift_details(z_scores, alpha=alpha)
        return None if details is None else details["drift"]

    @classmethod
    def internal_drift_details(
        cls,
        z_scores: List[float],
        alpha: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Full H27 drift computation with its audit-trail intermediates
        (B-110, review follow-up: the raw PSI was unrecoverable from any
        output — an examiner auditing why internal and external drift
        diverged could not distinguish "PSI barely above the chi2 null"
        from "PSI far above it").

        Returns None when indeterminate (same contract as
        internal_drift_from_z_scores), else a dict with:
        drift (float, the sealed value), raw_psi, null_95, n_finite,
        n_dropped_nonfinite, bins.
        """
        finite = [float(z) for z in z_scores if math.isfinite(z)]
        n = len(finite)
        if n < 4:
            return None

        # Sturges via integer arithmetic: ceil(1 + log2(n)) == 1 + ceil(log2(n))
        # == 1 + (n-1).bit_length() for n >= 2 — no libm boundary risk.
        # Clamped to 12 (n > 2048 gains nothing statistically; keeps the
        # frozen tables and chi2 constants total).
        k = min(12, max(3, 1 + (n - 1).bit_length()))
        p_ref = [Fraction(num, cls._P_REF_SCALE) for num in cls._P_REF_NUM[k]]

        lo, hi = Fraction(-3), Fraction(3)
        counts = [0] * k
        for z in finite:
            zf = Fraction(z)  # exact float-to-rational conversion
            zc = max(lo, min(hi, zf))
            idx = int((zc - lo) * k / (hi - lo))  # exact rational binning
            counts[min(k - 1, idx)] += 1

        psi = Fraction(0)
        for i in range(k):
            p_act = (counts[i] + alpha * p_ref[i]) / (n + alpha)
            psi += (p_act - p_ref[i]) * cls._ln_fraction(p_act / p_ref[i])

        chi2_95 = cls._CHI2_95[k - 1]
        null_95 = chi2_95 / n
        drift = (psi - null_95) * 4  # /0.25 as exact rational
        drift = min(Fraction(1), max(Fraction(0), drift))
        logger.debug(
            "[RiskLayer] H27 drift: n=%d k=%d raw_psi=%s null95=%s -> drift=%s",
            n, k, float(psi), float(null_95), float(drift),
        )
        return {
            "drift": float(drift),
            "raw_psi": float(psi),
            "null_95": float(null_95),
            "n_finite": n,
            "n_dropped_nonfinite": len(z_scores) - n,
            "bins": k,
        }
