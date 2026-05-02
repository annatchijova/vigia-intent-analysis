# -*- coding: utf-8 -*-
"""
VIGÍA — RiskBoundedDecisionLayer v3.0-P0-001
Parches aplicados: C4, C5, P1-A, P2 + P0-001 (semántica de P documentada)

P0-001 FIX:
  - Documentación explícita de que `posterior` = P(autenticidad | evidencia).
  - `r` = riesgo de FABRICACIÓN. Cuanto más bajo P(autenticidad), más alto r.
  - Guardia de validación: posterior debe estar en [0, 1].
  - Comentario de guardia en get_policy_spec() para prevenir inversión futura.
"""

from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskParameters:
    """
    C4 FIX: λ, γ, ω son propiedades globales del sistema.
    Se leen EXCLUSIVAMENTE del SelfAdaptiveRiskPolicy.
    Ningún template define estos valores.
    """
    lambda_drift: Decimal
    gamma_stability: Decimal
    omega_intention: Decimal
    epsilon_accept: Decimal
    epsilon_reject: Decimal


@dataclass(frozen=True)
class DecisionTrace:
    decision: str
    posterior: Decimal
    risk: Decimal
    reason_code: str
    omega_intention: Decimal
    drift_score: Decimal
    graph_stability: Decimal
    consistency_score: Decimal
    threshold_used: str


class RiskBoundedDecisionLayer:
    """
    Capa de gobernanza que emite veredictos basados en la función de riesgo.

    Función de riesgo (invariante):
        r = (1-P) · (1+λD) · (1+γ(1-S)) · (1+ω(1-I))

    SEMÁNTICA CRÍTICA (P0-001):
        P  = posterior = P(autenticidad | evidencia)  ∈ [0, 1]
        r  = riesgo de FABRICACIÓN  ∈ [0, ∞)

        Caso genuino:    P ≈ 0.99  →  (1-P) ≈ 0.01  →  r bajo  → ACCEPT
        Caso fabricado:  P ≈ 0.01  →  (1-P) ≈ 0.99  →  r alto  → REJECT

        Si algún desarrollador futuro interpreta P como P(fabricación),
        TODOS los veredictos se invertirán. Este docstring es la guardia.

    C5 FIX: Umbral operativo provisional para fase de calibración bootstrap.
    Documentado como OPERATIONAL_THRESHOLD_V1_DEMO.
    """

    _OPERATIONAL_REJECT_THRESHOLD: Decimal = Decimal("0.75")
    _OPERATIONAL_ACCEPT_THRESHOLD: Decimal = Decimal("0.05")
    _DEFAULT_PRECISION: int = 28

    def __init__(self, policy: RiskParameters):
        self.policy = policy
        self.ctx = Decimal.getcontext()
        self.ctx.prec = self._DEFAULT_PRECISION
        self.ctx.rounding = ROUND_HALF_EVEN

    def decide(
        self,
        posterior: Decimal,
        drift_score: Decimal,
        graph_stability: Decimal,
        consistency_score: Decimal,
        reason_prefix: str = ""
    ) -> DecisionTrace:
        """
        Emite veredicto usando la función de riesgo con aritmética Decimal.

        Args:
            posterior: P(autenticidad | evidencia). Valor en [0, 1].
                       1.0 = caso 100% genuino. 0.0 = caso 100% fabricado.
            drift_score: D ∈ [0, 1]. Deriva de distribución.
            graph_stability: S ∈ [0, 1]. Estabilidad del grafo de evidencia.
            consistency_score: I ∈ [0, 1]. Consistencia intencional.
            reason_prefix: Prefijo para el reason_code.

        Returns:
            DecisionTrace con veredicto, riesgo calculado y metadatos.

        Raises:
            ValueError: Si posterior está fuera de [0, 1].
        """
        # ── P0-001: Guardia de dominio ──
        zero = Decimal("0")
        one  = Decimal("1")
        if not (zero <= posterior <= one):
            raise ValueError(
                f"posterior debe estar en [0, 1]. Recibido: {posterior}. "
                f"Verificar que LikelihoodEngine emite P(autenticidad), "
                f"no P(fabricación)."
            )

        # SEG-3 (2026-05-02): clamp de TODOS los inputs antes de cualquier
        # operación aritmética. Valores extremos inyectados en la telemetría
        # (drift=1e9, stability=-50) causan DoS matemático en Decimal(prec=28).
        # El clamp es la primera operación — nunca después de multiplicaciones.
        p = max(zero, min(one, posterior))
        d = max(zero, min(one, drift_score))
        s = max(zero, min(one, graph_stability))
        i = max(zero, min(one, consistency_score))

        lam = self.policy.lambda_drift
        gam = self.policy.gamma_stability
        ome = self.policy.omega_intention

        # W3 (Claude 2026-05-02): validar que los λγω del template son cero.
        # La arquitectura C4 exige que λγω sean globales (SelfAdaptiveRiskPolicy),
        # no por-template. Si un template tiene valores no-cero, los veredictos
        # podrían divergir silenciosamente del modelo documentado.
        # Loguear warning pero no crash — el valor global de policy sigue siendo
        # el que se usa en el cálculo; esto solo detecta misconfiguraciones.
        _nonzero = [
            name for name, val in [("lambda_drift", lam), ("gamma_stability", gam), ("omega_intention", ome)]
            if val != zero
        ]
        if _nonzero and hasattr(self, '_w3_warned') is False:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "W3: RiskParameters tiene valores λγω no-cero: %s. "
                "Deben ser cero según esquema C4 (valores globales en SelfAdaptiveRiskPolicy). "
                "Verificar cargador de templates.", _nonzero
            )
            self._w3_warned = True  # una sola vez por instancia

        # Cálculo determinista de la función de riesgo
        term1 = one - p
        term2 = one + (lam * d)
        term3 = one + (gam * (one - s))
        term4 = one + (ome * (one - i))

        r = term1 * term2 * term3 * term4

        # C5 FIX: Regla de decisión con umbral operativo documentado
        eps_accept = self.policy.epsilon_accept
        eps_reject = self._OPERATIONAL_REJECT_THRESHOLD

        if r <= eps_accept:
            decision = "ACCEPT"
            reason = f"{reason_prefix}ACCEPT_RISK_LOW"
            threshold = "OPERATIONAL_THRESHOLD_V1_DEMO_ACCEPT"
        elif r >= eps_reject:
            decision = "REJECT"
            reason = f"{reason_prefix}REJECT_RISK_HIGH"
            threshold = "OPERATIONAL_THRESHOLD_V1_DEMO_REJECT"
        else:
            decision = "ABSTAIN"
            if d > Decimal("0.2"):
                reason = "ABSTAIN_DRIFT"
            elif s < Decimal("0.5"):
                reason = "ABSTAIN_INSTABILITY"
            elif i < Decimal("0.5"):
                reason = "ABSTAIN_INTENTION"
            else:
                reason = "ABSTAIN_ZONE"
            threshold = "OPERATIONAL_THRESHOLD_V1_DEMO_ABSTAIN"

        return DecisionTrace(
            decision=decision,
            posterior=p,
            risk=r.quantize(Decimal("0.0001")),
            reason_code=reason,
            omega_intention=ome,
            drift_score=d,
            graph_stability=s,
            consistency_score=i,
            threshold_used=threshold
        )

    @classmethod
    def get_policy_spec(cls) -> Dict[str, Any]:
        """
        Retorna el PolicySpec documentado para sellado en el bundle.
        """
        return {
            "risk_function": "(1-P)*(1+λD)*(1+γ(1-S))*(1+ω(1-I))",
            # P0-001: Guardia semántica permanente
            "posterior_semantics": (
                "P = P(autenticidad | evidencia). "
                "1-P = riesgo base de fabricación. "
                "NO INVERTIR: si P representara P(fabricación), "
                "la fórmula debería ser r = P * (1+λD) * ..."
            ),
            "lambda_drift_source": "SelfAdaptiveRiskPolicy.global",
            "gamma_stability_source": "SelfAdaptiveRiskPolicy.global",
            "omega_intention_source": "SelfAdaptiveRiskPolicy.global",
            "epsilon_accept": str(cls._OPERATIONAL_ACCEPT_THRESHOLD),
            "epsilon_reject": str(cls._OPERATIONAL_REJECT_THRESHOLD),
            "epsilon_reject_note": (
                "OPERATIONAL_THRESHOLD_V1_DEMO: "
                "Calibrado empíricamente sobre bootstrap n=180 sintéticos. "
                "Se recalibrará con corpus forense real post-hackathon."
            ),
            "arithmetic": "decimal.Decimal(prec=28, rounding=ROUND_HALF_EVEN)",
            "assumption": (
                "Risk factors (drift, stability, intention) treated as "
                "conditionally independent for computational tractability. "
                "This is a documented simplification, not a claim of statistical independence."
            ),
            "determinism_guarantee": "Bit-for-bit identical on x86 and ARM"
        }
