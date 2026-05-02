"""
vigia/core/risk_bounded_layer.py
Adaptador de RiskBoundedDecisionLayer para pipeline.py.
Agrega from_policy_spec() que no existe en risk_bounded_layer_v2.
"""
import importlib as _il, sys as _sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _root not in _sys.path: _sys.path.insert(0, _root)

_base_mod = _il.import_module("risk_bounded_layer_v2")
globals().update({k: getattr(_base_mod, k) for k in dir(_base_mod) if not k.startswith("__")})

_BaseRisk = _base_mod.RiskBoundedDecisionLayer
_RiskParams = _base_mod.RiskParameters

class RiskBoundedDecisionLayer(_BaseRisk):
    """
    RiskBoundedDecisionLayer con from_policy_spec() para pipeline.py.
    """
    @classmethod
    def from_policy_spec(cls, policy_spec) -> "RiskBoundedDecisionLayer":
        """Construye la capa de riesgo desde un PolicySpec EBS v1."""
        from decimal import Decimal as _D
        params = _RiskParams(
            lambda_drift=_D(str(getattr(policy_spec, "lambda_drift_init", 2.0))),
            gamma_stability=_D(str(getattr(policy_spec, "gamma_stability_init", 2.0))),
            omega_intention=_D("0.0"),  # C4: ω global viene de SelfAdaptiveRiskPolicy
            epsilon_accept=_D(str(getattr(policy_spec, "epsilon_accept", 0.05))),
            epsilon_reject=_D(str(getattr(policy_spec, "epsilon_reject", 0.05))),
        )
        instance = cls(policy=params)
        # Atributos de acceso directo que usa pipeline
        instance._lambda = float(params.lambda_drift)
        instance._gamma  = float(params.gamma_stability)
        return instance

    def decide(
        self,
        posterior,
        drift_score,
        graph_stability,
        consistency_score=1.0,   # default para llamadas internas (InterventionOptimizer)
        inference_result=None,
        reason_prefix: str = "",
    ):
        """
        Decide con interfaz extendida y retorna DecisionTrace de ebs.py.
        """
        from decimal import Decimal as _D
        import importlib as _il
        _ebs = _il.import_module("ebs")
        _DT = _ebs.DecisionTrace

        raw = super().decide(
            posterior=_D(str(posterior)),
            drift_score=_D(str(drift_score)),
            graph_stability=_D(str(graph_stability)),
            consistency_score=_D(str(consistency_score)),
            reason_prefix=reason_prefix,
        )

        # Convertir DecisionTrace de risk_bounded_layer_v2 → DecisionTrace de ebs.py
        reason = getattr(raw, "reason_code", "OK")
        return _DT(
            decision=str(raw.decision),
            posterior=float(raw.posterior),
            risk=float(raw.risk),
            drift_score=float(raw.drift_score),
            graph_stability=float(raw.graph_stability),
            lambda_drift=float(self.policy.lambda_drift),
            gamma_stability=float(self.policy.gamma_stability),
            epsilon_used=float(self.policy.epsilon_accept),
            reason_code=reason,
            abstain_reason=getattr(raw, "abstain_reason", None),
            omega_intention=float(getattr(raw, "omega_intention", 0.5)),
        )


# SelfAdaptiveRiskPolicy y PolicyStabilityController viven en ebs.py
_ebs = _il.import_module("ebs")
SelfAdaptiveRiskPolicy = _ebs.SelfAdaptiveRiskPolicy
PolicyStabilityController = _ebs.PolicyStabilityController
