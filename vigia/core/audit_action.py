"""
vigia/audit/evidence_graph_diff.py
vigia/action/safe_action_executor.py
─────────────────────────────────────────────────────────────────────────────
Auditoría y Acción — VIGÍA Forensic Suite EBS v1

ARQUITECTURA: Capa 4 — Auditoría y Acción
REGLA DE AISLAMIENTO: Lee de models/, engine/, governance/.
    No escribe hacia abajo. No llama a LLM.

COMPONENTES:
    EvidenceGraphDiff      — descompone cambio de decisión en deltas causales
    InterventionOptimizer  — búsqueda greedy de mínima intervención
    FormalPolicyEngine     — validación contra reglas JSON (ALLOW/DENY/REQUIRE_APPROVAL)
    SafeActionExecutor     — ejecutor con trazabilidad + rollback + auditoría

PRINCIPIO DE DISEÑO:
    "Ninguna acción puede ejecutarse sin dejar evidencia verificable y reversible."
    (Invariante I4: no existen efectos implícitos)

INTEGRACIÓN SIFT:
    Cada ActionRecord queda en ForensicBundle.actions.
    El verificador independiente puede validar que cada acción respetó la política.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import concurrent.futures
import logging
import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

import os as _os_aud, sys as _sys_aud
_ROOT_AUD = _os_aud.path.dirname(_os_aud.path.dirname(_os_aud.path.abspath(__file__)))
if _ROOT_AUD not in _sys_aud.path:
    _sys_aud.path.insert(0, _ROOT_AUD)

from vigia.core.ebs_v1 import (
    EvidenceGraph, DecisionTrace, PolicySpec, ActionRecord,
    SystemState, EPS_NUMERIC,
)
from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Decorador de timeout forense (H23 — antídoto pixel bomb / bomba logarítmica)
# ---------------------------------------------------------------------------

def forensic_timeout(seconds: int = 30):
    """
    Decorador que impone un timeout a cualquier método del SafeActionExecutor.

    Si la ejecución supera `seconds`, lanza concurrent.futures.TimeoutError
    que el caller debe capturar y registrar como TIMEOUT_ERROR en el bundle.

    Uso:
        @forensic_timeout(30)
        def execute_something(self, ...):
            ...

    Diseño:
    - Usa ThreadPoolExecutor(max_workers=1) para no bloquear el hilo principal
    - Compatible con métodos de instancia (self se pasa como argumento)
    - No usa SIGALRM (no funciona en Windows ni en hilos secundarios)
    - El timeout es configurable por instancia via SafeActionExecutor.ACTION_TIMEOUT_SEC
    """
    import functools

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Respetar override de instancia si existe
            _self = args[0] if args else None
            _timeout = getattr(_self, "ACTION_TIMEOUT_SEC", seconds)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(fn, *args, **kwargs)
                return future.result(timeout=_timeout)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# EvidenceGraphDiff
# ---------------------------------------------------------------------------

class EvidenceGraphDiff:
    """
    Descompone el cambio de decisión entre dos estados en deltas causales.

    Responde a la pregunta:
        "¿Qué cambió entre el estado A y el estado B que justifica
         el cambio de decisión de X a Y?"

    Esto es clave para la narrativa de SIFT y para defendibilidad ante perito.
    El LLM (PeircePlanner) usará este diff como input para generar narrativa.
    """

    def diff_decisions(
        self,
        trace_before: DecisionTrace,
        trace_after: DecisionTrace,
        graph_before: Optional[EvidenceGraph] = None,
        graph_after: Optional[EvidenceGraph] = None,
    ) -> Dict[str, Any]:
        """
        Calcula diferencias entre dos DecisionTrace y opcionalmente dos grafos.

        Returns:
            {
                "decision_changed": bool
                "decision_delta": str         — "ACCEPT→REJECT", etc.
                "posterior_delta": float
                "risk_delta": float
                "drift_delta": float
                "stability_delta": float
                "causal_factors": list        — factores que causaron el cambio
                "graph_diff": dict            — si se proveen ambos grafos
            }
        """
        decision_changed = trace_before.decision != trace_after.decision
        delta_transition = f"{trace_before.decision}→{trace_after.decision}"

        posterior_delta = trace_after.posterior - trace_before.posterior
        risk_delta = trace_after.risk - trace_before.risk
        drift_delta = trace_after.drift_score - trace_before.drift_score
        stability_delta = trace_after.graph_stability - trace_before.graph_stability

        # Análisis causal
        causal_factors = []

        if abs(posterior_delta) > 0.05:
            direction = "aumentó" if posterior_delta > 0 else "disminuyó"
            causal_factors.append({
                "factor": "posterior",
                "direction": direction,
                "magnitude": abs(posterior_delta),
                "description": f"P(fabricación) {direction} en {abs(posterior_delta):.3f}",
            })

        if abs(drift_delta) > 0.02:
            direction = "aumentó" if drift_delta > 0 else "disminuyó"
            causal_factors.append({
                "factor": "drift",
                "direction": direction,
                "magnitude": abs(drift_delta),
                "description": f"Drift {direction} en {abs(drift_delta):.3f} — inflación de riesgo",
            })

        if abs(stability_delta) > 0.05:
            direction = "mejoró" if stability_delta > 0 else "empeoró"
            causal_factors.append({
                "factor": "graph_stability",
                "direction": direction,
                "magnitude": abs(stability_delta),
                "description": f"Estabilidad del grafo {direction} en {abs(stability_delta):.3f}",
            })

        if abs(trace_after.lambda_drift - trace_before.lambda_drift) > 0.1:
            causal_factors.append({
                "factor": "lambda_adaptation",
                "magnitude": abs(trace_after.lambda_drift - trace_before.lambda_drift),
                "description": "Política adaptativa cambió λ (sensibilidad al drift)",
            })

        # Diff de grafos (si disponibles)
        graph_diff: Dict[str, Any] = {}
        if graph_before and graph_after:
            old_edges = {(e.source, e.target): e.stability for e in graph_before.edges}
            new_edges = {(e.source, e.target): e.stability for e in graph_after.edges}

            gained = [f"{k[0]}->{k[1]}" for k in new_edges if k not in old_edges]
            lost = [f"{k[0]}->{k[1]}" for k in old_edges if k not in new_edges]
            stability_changes = {
                f"{k[0]}->{k[1]}": round(new_edges[k] - old_edges[k], 4)
                for k in old_edges if k in new_edges
            }

            graph_diff = {
                "edges_gained": gained,
                "edges_lost": lost,
                "stability_changes": stability_changes,
                "global_stability_delta": round(
                    graph_after.global_stability() - graph_before.global_stability(), 4
                ),
            }

        return {
            "decision_changed": decision_changed,
            "decision_delta": delta_transition,
            "posterior_delta": round(posterior_delta, 6),
            "risk_delta": round(risk_delta, 6),
            "drift_delta": round(drift_delta, 6),
            "stability_delta": round(stability_delta, 6),
            "causal_factors": causal_factors,
            "graph_diff": graph_diff,
        }


# ---------------------------------------------------------------------------
# InterventionOptimizer
# ---------------------------------------------------------------------------

class InterventionOptimizer:
    """
    Búsqueda greedy de la intervención mínima de menor costo.

    OBJETIVO:
        Dado un estado que produjo REJECT o ABSTAIN, encontrar la
        intervención de menor magnitud que lo cambiaría a ACCEPT.

    ESTRATEGIA: Greedy search sobre 3 dimensiones:
        - posterior (mejorar evidencia)
        - drift     (reducir drift — ej: recolectar más data)
        - stability (mejorar estabilidad del grafo — ej: más bootstrap samples)

    SEMÁNTICA FORENSE:
        No es "cómo engañar al sistema". Es "qué evidencia adicional
        o qué mejora operacional cambiaría la conclusión."
    """

    def __init__(
        self,
        risk_layer: RiskBoundedDecisionLayer,
        step_size: float = 0.05,
        max_steps: int = 20,
        cost_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        self._risk_layer = risk_layer
        self.step_size = step_size
        self.max_steps = max_steps
        # Costo relativo de cada tipo de intervención
        self.cost_weights = cost_weights or {
            "posterior": 1.0,   # evidencia nueva — costo bajo
            "drift": 0.8,       # más datos para reducir drift — moderado
            "stability": 1.5,   # re-bootstrap del grafo — más caro
        }

    def recommend(
        self,
        current_state: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Recomienda la intervención mínima para cambiar la decisión a ACCEPT.

        current_state: {
            "posterior": float,
            "drift_score": float,
            "graph_stability": float
        }

        Returns: {
            "feasible": bool
            "best_intervention": dict | None
            "alternatives": list
            "current_decision": str
        }
        """
        posterior = current_state.get("posterior", 0.5)
        drift = current_state.get("drift_score", 0.0)
        stability = current_state.get("graph_stability", 1.0)

        current_trace = self._risk_layer.decide(posterior, drift, stability)

        if current_trace.decision == "ACCEPT":
            return {
                "feasible": True,
                "best_intervention": None,
                "alternatives": [],
                "current_decision": "ACCEPT",
                "message": "Ya en estado ACCEPT — no se requiere intervención",
            }

        candidates = []

        # Explorar intervenciones sobre cada variable
        for variable in ["posterior", "drift", "stability"]:
            for step in range(1, self.max_steps + 1):
                delta = step * self.step_size

                if variable == "posterior":
                    new_p = min(1.0, posterior + delta)
                    new_d = drift
                    new_s = stability
                elif variable == "drift":
                    new_p = posterior
                    new_d = max(0.0, drift - delta)
                    new_s = stability
                else:  # stability
                    new_p = posterior
                    new_d = drift
                    new_s = min(1.0, stability + delta)

                new_trace = self._risk_layer.decide(new_p, new_d, new_s)

                if new_trace.decision == "ACCEPT":
                    cost = delta * self.cost_weights.get(variable, 1.0)
                    candidates.append({
                        "variable": variable,
                        "delta": delta,
                        "cost": cost,
                        "new_state": {
                            "posterior": new_p,
                            "drift_score": new_d,
                            "graph_stability": new_s,
                        },
                        "new_risk": new_trace.risk,
                        "steps_required": step,
                    })
                    break  # mínimo para esta variable

        if not candidates:
            return {
                "feasible": False,
                "best_intervention": None,
                "alternatives": [],
                "current_decision": current_trace.decision,
                "message": "No se encontró intervención factible en rango dado",
            }

        # Ordenar por costo (greedy mínimo)
        candidates.sort(key=lambda x: x["cost"])

        return {
            "feasible": True,
            "best_intervention": candidates[0],
            "alternatives": candidates[1:],
            "current_decision": current_trace.decision,
            "message": f"Intervención mínima: modificar {candidates[0]['variable']} en {candidates[0]['delta']:.3f}",
        }


# ---------------------------------------------------------------------------
# FormalPolicyEngine
# ---------------------------------------------------------------------------

class FormalPolicyEngine:
    """
    Validación de acciones contra política formal (reglas JSON).

    INVARIANTE I4: no existen efectos implícitos.
    Toda acción debe pasar por este engine antes de ejecutarse.

    Retorna: ALLOW / DENY / REQUIRE_APPROVAL
    """

    def __init__(self, policy_spec: PolicySpec) -> None:
        self._policy = policy_spec
        self._rule_map = {r.variable: r for r in policy_spec.rules}

    def check(
        self,
        variable: str,
        delta: float,
        actor: str = "system",
    ) -> Dict[str, Any]:
        """
        Valida una acción propuesta contra la política formal.

        Returns:
            {
                "result": "ALLOW" | "DENY" | "REQUIRE_APPROVAL"
                "reason": str
                "max_delta": float | None
                "allowed_roles": list | None
            }
        """
        rule = self._rule_map.get(variable)

        if rule is None:
            return {
                "result": "DENY",
                "reason": f"Sin política definida para variable '{variable}'",
                "max_delta": None,
                "allowed_roles": None,
            }

        # Control de rol
        if actor not in rule.allowed_roles:
            return {
                "result": "DENY",
                "reason": f"Actor '{actor}' no autorizado para '{variable}'",
                "max_delta": rule.max_delta,
                "allowed_roles": rule.allowed_roles,
            }

        # Control de magnitud
        if abs(delta) > rule.max_delta:
            return {
                "result": "DENY",
                "reason": (
                    f"|delta|={abs(delta):.4f} supera max_delta={rule.max_delta:.4f} "
                    f"para '{variable}'"
                ),
                "max_delta": rule.max_delta,
                "allowed_roles": rule.allowed_roles,
            }

        # Aprobación explícita requerida
        if rule.requires_approval:
            return {
                "result": "REQUIRE_APPROVAL",
                "reason": f"'{variable}' requiere aprobación explícita",
                "max_delta": rule.max_delta,
                "allowed_roles": rule.allowed_roles,
            }

        return {
            "result": "ALLOW",
            "reason": "OK",
            "max_delta": rule.max_delta,
            "allowed_roles": rule.allowed_roles,
        }

    def check_action_record(self, action: ActionRecord) -> Dict[str, Any]:
        """Valida un ActionRecord completo."""
        return self.check(
            variable=action.variable,
            delta=action.delta,
            actor=action.actor,
        )


# ---------------------------------------------------------------------------
# SafeActionExecutor
# ---------------------------------------------------------------------------

class SafeActionExecutor:
    """
    Ejecutor de intervenciones con trazabilidad total, validación de política y rollback.

    PRINCIPIO:
        "Ninguna acción puede ejecutarse sin dejar evidencia verificable y reversible."

    FLUJO:
        1. Optimizer recomienda intervención
        2. FormalPolicyEngine valida la acción
        3. Si ALLOW → ejecutar + registrar ActionRecord
        4. Si REQUIRE_APPROVAL → proponer sin ejecutar (flag auto_apply)
        5. Si DENY → rechazar + registrar razón
        6. Rollback disponible para toda acción ejecutada

    INTEGRACIÓN EBS v1:
        El historial de acciones se incluye en ForensicBundle.actions.
        El verificador independiente puede validar cada acción.

    LÍMITE DE MEMORIA (H4):
        _state_stack tiene maxlen=MAX_STACK_DEPTH para prevenir OOM en análisis
        masivos. Si se supera el límite, los estados más antiguos se descartan
        (FIFO). El rollback solo alcanza hasta el estado más antiguo en el stack.
        Configurar MAX_STACK_DEPTH según RAM disponible en el entorno SIFT.
    """

    # Límite de profundidad del stack de rollback — protege contra OOM (H4)
    # 500 estados × ~1KB/estado ≈ 500KB máximo — seguro en cualquier entorno SIFT
    MAX_STACK_DEPTH: int = 500

    def __init__(
        self,
        risk_layer: RiskBoundedDecisionLayer,
        policy_engine: FormalPolicyEngine,
        optimizer: Optional[InterventionOptimizer] = None,
        max_stack_depth: Optional[int] = None,
    ) -> None:
        self._risk_layer = risk_layer
        self._policy_engine = policy_engine
        self._optimizer = optimizer or InterventionOptimizer(risk_layer)
        self._history: List[ActionRecord] = []
        # deque con maxlen — descarta silenciosamente los estados más antiguos
        # cuando se supera la capacidad, previniendo OOM en análisis masivos (H4)
        _depth = max_stack_depth if max_stack_depth is not None else self.MAX_STACK_DEPTH
        from collections import deque
        self._state_stack: deque = deque(maxlen=_depth)

    @forensic_timeout(30)
    def execute_recommendation(
        self,
        current_state: Dict[str, float],
        actor: str = "system",
        auto_apply: bool = False,
    ) -> Dict[str, Any]:
        """
        Obtiene recomendación del optimizer y la ejecuta si pasa la política.

        Decorado con @forensic_timeout(30) — H23:
        Si la ejecución supera ACTION_TIMEOUT_SEC (default 30s), el decorador
        lanza TimeoutError. El pipeline debe capturarlo como TIMEOUT_ERROR.
        El sistema prefiere "abortado por tiempo" antes que quedar congelado.

        Args:
            current_state: {"posterior", "drift_score", "graph_stability"}
            actor        : identificador del ejecutor
            auto_apply   : si False, requiere aprobación explícita (recomendado)

        Returns:
            {
                "executed": bool
                "action": ActionRecord | None
                "policy_result": str
                "reason": str
                "proposal": dict | None (si no ejecutado)
            }
        """
        # Obtener recomendación
        recommendation = self._optimizer.recommend(current_state)

        if not recommendation["feasible"]:
            return {
                "executed": False,
                "action": None,
                "policy_result": "NO_INTERVENTION",
                "reason": recommendation["message"],
                "proposal": None,
            }

        if recommendation["best_intervention"] is None:
            return {
                "executed": False,
                "action": None,
                "policy_result": "ALREADY_ACCEPT",
                "reason": "Estado ya es ACCEPT",
                "proposal": None,
            }

        best = recommendation["best_intervention"]
        variable = best["variable"]
        delta = best["delta"]

        # Calcular pre/post valores
        pre_value = current_state.get(variable, 0.0)
        post_value = best["new_state"].get(variable, pre_value)

        # Validar contra política formal
        policy_check = self._policy_engine.check(variable, delta, actor)

        # Calcular DecisionTrace pre/post
        trace_before = self._risk_layer.decide(
            current_state.get("posterior", 0.5),
            current_state.get("drift_score", 0.0),
            current_state.get("graph_stability", 1.0),
        )

        action = ActionRecord(
            action_id=str(uuid.uuid4()),
            variable=variable,
            delta=delta,
            pre_value=pre_value,
            post_value=post_value,
            decision_before=trace_before.decision,
            risk_before=trace_before.risk,
            approved=False,
            actor=actor,
            timestamp=_now_iso(),
            policy_check_result=policy_check["result"],
            rollback_available=True,
        )

        if policy_check["result"] == "DENY":
            action.policy_check_result = "DENY"
            return {
                "executed": False,
                "action": action,
                "policy_result": "DENY",
                "reason": policy_check["reason"],
                "proposal": best,
            }

        if policy_check["result"] == "REQUIRE_APPROVAL" and not auto_apply:
            action.policy_check_result = "PENDING_APPROVAL"
            return {
                "executed": False,
                "action": action,
                "policy_result": "REQUIRE_APPROVAL",
                "reason": "Aprobación explícita requerida — usar auto_apply=True para forzar",
                "proposal": best,
            }

        # Ejecutar intervención — el decorador @forensic_timeout maneja el timeout
        # (H23). Si se supera ACTION_TIMEOUT_SEC, TimeoutError sube al decorador
        # que lo propaga al caller. El estado apilado se debe limpiar en el handler.
        self._state_stack.append(current_state.copy())

        new_state = best["new_state"]
        trace_after = self._risk_layer.decide(
            new_state.get("posterior", 0.5),
            new_state.get("drift_score", 0.0),
            new_state.get("graph_stability", 1.0),
        )

        action.decision_after = trace_after.decision
        action.risk_after = trace_after.risk
        action.approved = True
        action.policy_check_result = "ALLOW"

        self._history.append(action)

        logger.info(
            "[SafeActionExecutor] Acción ejecutada: %s Δ=%.4f | %s→%s (r: %.4f→%.4f)",
            variable, delta,
            action.decision_before, action.decision_after,
            action.risk_before, action.risk_after,
        )

        return {
            "executed": True,
            "action": action,
            "policy_result": "ALLOW",
            "reason": "Ejecutado y registrado",
            "new_state": new_state,
            "new_trace": trace_after,
        }

    def rollback(self, n: int = 1) -> Optional[Dict[str, float]]:
        """
        Revierte las últimas n acciones del historial.

        Retorna el estado anterior si hay rollback disponible, None si no.
        """
        if len(self._state_stack) < n:
            logger.warning("[SafeActionExecutor] No hay estado para rollback")
            return None

        for _ in range(n):
            self._state_stack.pop()
            if self._history:
                reverted = self._history.pop()
                reverted.rollback_available = False
                logger.info(
                    "[SafeActionExecutor] Rollback: acción %s revertida",
                    reverted.action_id[:8],
                )

        return self._state_stack[-1] if self._state_stack else None

    def get_action_history(self) -> List[ActionRecord]:
        """Retorna historial de acciones para incluir en ForensicBundle."""
        return list(self._history)

    def audit_log(self) -> List[Dict[str, Any]]:
        """Log de auditoría completo para SIFT."""
        return [a.to_dict() for a in self._history]
