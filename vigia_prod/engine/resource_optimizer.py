"""
vigia/engine/resource_optimizer.py
─────────────────────────────────────────────────────────────────────────────
Resource Optimizer — VIGIA Forensic Suite EBS v1

PROPOSITO:
    Gestionar el orden de ejecucion de pericias forenses y decidir cuándo
    abortar el procesamiento de señales pesadas (ELA, CLIP, etc.) cuando
    el motor de inferencia ya alcanzo el umbral de confianza.

LOGICA CENTRAL:
    Prioridad de una pericia:
        P = log_LR_esperado / costo_relativo

    Donde:
        log_LR_esperado : contribucion promedio historica de la herramienta
                          (o estimacion inicial si no hay historial)
        costo_relativo  : tiempo/recursos normalizados de la herramienta

    Regla de Aborto:
        Si el posterior acumulado actual supera el umbral de confianza
        definido en la politica (1 - epsilon), omitir señales pendientes.
        "Si ya es REJECT con certeza, no hace falta correr CLIP."

CATALOGO DE COSTOS (relativos, 1.0 = baseline):
    SDA  (Stylometric Analysis)    : 0.5  — texto, rapido
    ACP  (Authorship Comparison)   : 0.7  — texto comparativo
    CLI  (Command-Line Indicators) : 0.3  — metadata, muy rapido
    ROI  (Region of Interest)      : 0.8  — imagen/texto
    GCI  (Generative Content Ind.) : 1.0  — baseline
    DGPI (Deep Generative Pattern) : 1.2  — mas costoso que GCI
    ELA  (Error Level Analysis)    : 2.0  — procesamiento de imagen
    CLIP (Contrastive LIP)         : 3.5  — modelo de vision, costoso
    OCR  (Optical Character Rec.)  : 1.5  — imagen a texto

INTEGRACION CON PIPELINE:
    optimizer = ResourceOptimizer(policy_spec)
    plan = optimizer.build_execution_plan(available_tools, prior_posterior=0.5)
    for tool in plan:
        signal = tool.run(evidence)
        result = engine.infer([signal])
        if optimizer.should_abort(result["posterior"], tool.name):
            break
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Patron de raiz dinamica
_HERE_RO = os.path.dirname(os.path.abspath(__file__))
_ROOT_RO = os.path.dirname(_HERE_RO)
if _ROOT_RO not in sys.path:
    sys.path.insert(0, _ROOT_RO)

from models.ebs_v1 import PolicySpec, EPS_NUMERIC


# ---------------------------------------------------------------------------
# Catalogo de costos por defecto
# ---------------------------------------------------------------------------

DEFAULT_TOOL_COSTS: Dict[str, float] = {
    "CLI":  0.3,   # metadata — muy rapido
    "SDA":  0.5,   # estilometria — rapido
    "ACP":  0.7,   # comparacion de autoria
    "ROI":  0.8,   # region de interes
    "GCI":  1.0,   # baseline
    "DGPI": 1.2,
    "OCR":  1.5,
    "ELA":  2.0,   # analisis de nivel de error — imagen
    "CLIP": 3.5,   # modelo de vision — costoso
}

# Log-LR esperado inicial por herramienta (prior sin historial)
# Basado en experiencia forense documentada.
DEFAULT_EXPECTED_LOG_LR: Dict[str, float] = {
    "CLI":  0.8,
    "SDA":  1.5,
    "ACP":  1.2,
    "ROI":  1.0,
    "GCI":  2.0,
    "DGPI": 1.8,
    "OCR":  0.6,
    "ELA":  2.5,
    "CLIP": 3.0,
}


# ---------------------------------------------------------------------------
# ToolSpec — especificacion de una herramienta ejecutable
# ---------------------------------------------------------------------------

@dataclass
class ToolSpec:
    """
    Especificacion de una herramienta forense en el plan de ejecucion.

    Campos:
        name          : identificador de la herramienta
        priority      : P = log_LR_esperado / costo (calculado por optimizer)
        cost          : costo relativo de ejecucion
        expected_log_lr: contribucion esperada al log-LR total
        is_heavy      : True si la herramienta es candidata a ser abortada
        executed      : True si ya fue ejecutada en este pipeline
        skipped       : True si fue omitida por regla de aborto
        actual_log_lr : contribucion real (post-ejecucion)
    """
    name: str
    priority: float = 0.0
    cost: float = 1.0
    expected_log_lr: float = 1.0
    is_heavy: bool = False
    executed: bool = False
    skipped: bool = False
    actual_log_lr: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "priority": round(self.priority, 4),
            "cost": self.cost,
            "expected_log_lr": round(self.expected_log_lr, 4),
            "is_heavy": self.is_heavy,
            "executed": self.executed,
            "skipped": self.skipped,
            "actual_log_lr": self.actual_log_lr,
        }


# ---------------------------------------------------------------------------
# AbortDecision — resultado de la evaluacion de aborto
# ---------------------------------------------------------------------------

@dataclass
class AbortDecision:
    should_abort: bool
    reason: str
    posterior: float
    threshold: float
    tools_remaining: List[str]
    accumulated_cost: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "should_abort": self.should_abort,
            "reason": self.reason,
            "posterior": round(self.posterior, 4),
            "threshold": round(self.threshold, 4),
            "tools_remaining": self.tools_remaining,
            "accumulated_cost": round(self.accumulated_cost, 4),
        }


# ---------------------------------------------------------------------------
# ResourceOptimizer
# ---------------------------------------------------------------------------

class ResourceOptimizer:
    """
    Gestiona el plan de ejecucion de pericias forenses.

    Dos responsabilidades:
        1. Ordenar herramientas por prioridad P = log_LR / costo
        2. Decidir si abortar herramientas pesadas cuando ya hay certeza

    La regla de aborto es conservadora:
        - Solo aborta si posterior >= 1 - epsilon (certeza de REJECT)
        - Nunca aborta si el posterior indica zona de ACCEPT o ABSTAIN
        - El aborto se registra en el ExecutionLog para el ForensicBundle
    """

    # Umbral de costo para clasificar una herramienta como "pesada"
    HEAVY_TOOL_COST_THRESHOLD: float = 1.5

    def __init__(
        self,
        policy: Optional[PolicySpec] = None,
        tool_costs: Optional[Dict[str, float]] = None,
        expected_log_lr: Optional[Dict[str, float]] = None,
        heavy_threshold: float = 1.5,
    ) -> None:
        self._policy = policy
        self._costs = {**DEFAULT_TOOL_COSTS, **(tool_costs or {})}
        self._expected_lr = {**DEFAULT_EXPECTED_LOG_LR, **(expected_log_lr or {})}
        self.heavy_threshold = heavy_threshold

        # Historial de ejecuciones para actualizar expected_log_lr
        self._execution_history: List[Dict[str, Any]] = []

        # Epsilon de la politica (umbral de decision)
        self._epsilon = 0.05
        if policy is not None:
            self._epsilon = getattr(policy, "epsilon_accept", 0.05)

    # ------------------------------------------------------------------
    # Construccion del plan de ejecucion
    # ------------------------------------------------------------------

    def build_execution_plan(
        self,
        available_tools: List[str],
        prior_posterior: float = 0.5,
        max_cost_budget: Optional[float] = None,
    ) -> List[ToolSpec]:
        """
        Construye el plan de ejecucion ordenado por prioridad.

        FAIL-SAFE:
            Si cualquier error ocurre durante la construccion del plan
            (division por cero, tipo invalido, etc.), el metodo retorna
            un plan plano con todas las herramientas en orden original.
            El pipeline NUNCA se detiene por un fallo del optimizer.

        Args:
            available_tools   : herramientas disponibles en este caso
            prior_posterior   : posterior actual antes de ejecutar pericias
            max_cost_budget   : presupuesto maximo de costo acumulado (None = sin limite)

        Returns:
            Lista de ToolSpec ordenada de mayor a menor prioridad.
            En modo fail-safe: orden original, costo=1.0, priority=1.0.
        """
        try:
            return self._build_plan_internal(available_tools, prior_posterior, max_cost_budget)
        except Exception as e:
            # OPTIMIZER_FAIL_SAFE: cualquier error en el plan fuerza ejecucion completa.
            # spec.skipped = False para todas — ningun herramienta omitida sin evidencia.
            logger.error(
                "[ResourceOptimizer] OPTIMIZER_FAIL_SAFE: %s — "                "forzando ejecucion de todas las herramientas (skipped=False).",
                e,
            )
            fail_safe_plan = [
                ToolSpec(
                    name=t,
                    priority=1.0,
                    cost=self._costs.get(t, 1.0),
                    expected_log_lr=self._get_expected_log_lr(t),
                    is_heavy=self._costs.get(t, 1.0) >= self.heavy_threshold,
                    executed=False,
                    skipped=False,   # CRITICO: ninguna herramienta omitida en fail-safe
                )
                for t in available_tools
            ]
            return fail_safe_plan

    def _build_plan_internal(
        self,
        available_tools: List[str],
        prior_posterior: float = 0.5,
        max_cost_budget: Optional[float] = None,
    ) -> List[ToolSpec]:
        """Implementacion interna del plan. Wrapeada por build_execution_plan para fail-safe."""
        plan: List[ToolSpec] = []
        accumulated_cost = 0.0

        for tool_name in available_tools:
            cost = self._costs.get(tool_name, 1.0)
            expected = self._get_expected_log_lr(tool_name)

            # Ajuste por information gain marginal:
            # Si el posterior ya es alto, las herramientas de baja contribucion
            # tienen aun menos valor esperado
            posterior_factor = 1.0
            if prior_posterior > 0.7 or prior_posterior < 0.3:
                # Ya hay evidencia fuerte — herramientas de bajo expected_lr
                # contribuyen menos marginalmenete
                posterior_factor = max(0.5, 1.0 - abs(prior_posterior - 0.5))

            adjusted_expected = expected * posterior_factor
            priority = adjusted_expected / max(cost, EPS_NUMERIC)
            is_heavy = cost >= self.heavy_threshold

            spec = ToolSpec(
                name=tool_name,
                priority=priority,
                cost=cost,
                expected_log_lr=adjusted_expected,
                is_heavy=is_heavy,
            )

            # Aplicar presupuesto si se especifica
            if max_cost_budget is not None:
                if accumulated_cost + cost > max_cost_budget:
                    logger.debug(
                        "[ResourceOptimizer] %s excede presupuesto (%.2f + %.2f > %.2f)",
                        tool_name, accumulated_cost, cost, max_cost_budget,
                    )
                    continue

            plan.append(spec)
            accumulated_cost += cost

        # Ordenar: no-pesadas por prioridad desc, pesadas al final por prioridad desc
        light = sorted([t for t in plan if not t.is_heavy], key=lambda t: -t.priority)
        heavy = sorted([t for t in plan if t.is_heavy], key=lambda t: -t.priority)

        ordered = light + heavy

        logger.info(
            "[ResourceOptimizer] Plan: %d herramientas (%d livianas, %d pesadas) | "
            "costo_total=%.2f",
            len(ordered), len(light), len(heavy),
            sum(t.cost for t in ordered),
        )

        return ordered

    # ------------------------------------------------------------------
    # Evaluacion de aborto
    # ------------------------------------------------------------------

    def should_abort(
        self,
        current_posterior: float,
        pending_tools: List[str],
        accumulated_cost: float = 0.0,
    ) -> AbortDecision:
        # FAIL-SAFE: si should_abort falla por cualquier motivo, no abortar.
        # Es siempre mas seguro continuar ejecutando pericias que omitirlas.
        try:
            return self._should_abort_internal(current_posterior, pending_tools, accumulated_cost)
        except Exception as e:
            logger.error("[ResourceOptimizer] FAIL-SAFE en should_abort: %s — no abortar.", e)
            return AbortDecision(
                should_abort=False,
                reason=f"Fail-safe activado (error: {e}) — continuando todas las pericias",
                posterior=current_posterior,
                threshold=1.0,
                tools_remaining=pending_tools,
                accumulated_cost=accumulated_cost,
            )

    def _should_abort_internal(
        self,
        current_posterior: float,
        pending_tools: List[str],
        accumulated_cost: float = 0.0,
    ) -> AbortDecision:
        """
        Evalua si abortar las herramientas pesadas pendientes.

        REGLA DE ABORTO (conservadora):
            Abortar si: posterior >= 1 - epsilon  (certeza de REJECT)
            No abortar si: posterior <= epsilon    (certeza de ACCEPT — verificar igual)
            No abortar si: zona ABSTAIN            (incertidumbre — necesitamos más evidencia)

        RAZON DE CONSERVADURISMO:
            En forensica, un falso negativo (perder evidencia de fabricacion)
            es mas costoso que un falso positivo. Solo se aborta con certeza
            de REJECT — no con certeza de ACCEPT. Para ACCEPT necesitamos
            evidencia completa.

        Args:
            current_posterior: P(fabricacion) acumulado hasta ahora
            pending_tools    : herramientas que aun no ejecutaron
            accumulated_cost : costo total acumulado hasta ahora

        Returns:
            AbortDecision con should_abort y razon
        """
        threshold = 1.0 - self._epsilon  # umbral de certeza de REJECT
        heavy_pending = [t for t in pending_tools
                         if self._costs.get(t, 1.0) >= self.heavy_threshold]

        # Condicion de aborto: certeza de REJECT Y hay herramientas pesadas pendientes
        if current_posterior >= threshold and heavy_pending:
            return AbortDecision(
                should_abort=True,
                reason=(
                    f"Posterior={current_posterior:.4f} >= umbral={threshold:.4f}. "
                    f"REJECT con certeza. Omitiendo {len(heavy_pending)} pericia(s) pesada(s): "
                    f"{', '.join(heavy_pending)}"
                ),
                posterior=current_posterior,
                threshold=threshold,
                tools_remaining=heavy_pending,
                accumulated_cost=accumulated_cost,
            )

        # Zona de ABSTAIN o ACCEPT — necesitamos más evidencia, no abortamos
        if current_posterior < threshold:
            return AbortDecision(
                should_abort=False,
                reason=(
                    f"Posterior={current_posterior:.4f} < umbral={threshold:.4f}. "
                    f"Incertidumbre activa — continuar pericias."
                ),
                posterior=current_posterior,
                threshold=threshold,
                tools_remaining=pending_tools,
                accumulated_cost=accumulated_cost,
            )

        # Posterior >= threshold pero sin herramientas pesadas pendientes
        return AbortDecision(
            should_abort=False,
            reason="Sin herramientas pesadas pendientes — nada que abortar.",
            posterior=current_posterior,
            threshold=threshold,
            tools_remaining=pending_tools,
            accumulated_cost=accumulated_cost,
        )

    # ------------------------------------------------------------------
    # Actualizacion de expected_log_lr con historial real
    # ------------------------------------------------------------------

    def update_from_execution(
        self,
        tool_name: str,
        actual_log_lr: float,
        alpha: float = 0.3,
    ) -> float:
        """
        Actualiza el expected_log_lr de una herramienta con la observacion real.

        Usa exponential moving average:
            E[t+1] = (1-alpha) * E[t] + alpha * actual

        alpha=0.3 — aprende rapido pero no sobreajusta a un caso.

        Retorna el nuevo expected_log_lr.
        """
        current = self._expected_lr.get(tool_name, 1.0)
        updated = (1.0 - alpha) * current + alpha * actual_log_lr
        self._expected_lr[tool_name] = updated

        self._execution_history.append({
            "tool": tool_name,
            "actual_log_lr": actual_log_lr,
            "expected_before": current,
            "expected_after": updated,
        })

        logger.debug(
            "[ResourceOptimizer] Update %s: E=%.4f -> %.4f (actual=%.4f)",
            tool_name, current, updated, actual_log_lr,
        )
        return updated

    # ------------------------------------------------------------------
    # ROI del plan ejecutado
    # ------------------------------------------------------------------

    def compute_plan_roi(self, executed_specs: List[ToolSpec]) -> Dict[str, Any]:
        """
        Calcula el Return on Investment del plan ejecutado.

        ROI = log_LR_total_real / costo_total
        Eficiencia = log_LR_real / log_LR_esperado

        FAIL-SAFE: si el calculo falla (ej. division por cero, lista vacia),
        retorna un dict con valores neutros en lugar de propagar la excepcion.
        El pipeline no se interrumpe por un fallo en la metrica de ROI.
        """
        try:
            return self._compute_roi_internal(executed_specs)
        except Exception as e:
            # OPTIMIZER_FAIL_SAFE: ROI no disponible — retornar metricas neutras.
            # El bundle NO se invalida por un error en metricas de eficiencia.
            logger.error("[ResourceOptimizer] OPTIMIZER_FAIL_SAFE en compute_plan_roi: %s", e)
            # Forzar skipped=False en todos los specs afectados
            for spec in executed_specs:
                spec.skipped = False
            return {
                "total_cost_incurred": 0.0, "cost_saved_by_abort": 0.0,
                "expected_log_lr": 0.0, "actual_log_lr": 0.0,
                "expected_log_lr_lost_by_abort": 0.0,
                "roi": 0.0, "efficiency": 0.0,
                "n_executed": 0, "n_skipped": 0,
                "error": f"OPTIMIZER_FAIL_SAFE: {e}",
            }

    def _compute_roi_internal(self, executed_specs: List[ToolSpec]) -> Dict[str, Any]:
        """Implementacion interna de ROI. Wrapeada para fail-safe."""
        total_cost = sum(t.cost for t in executed_specs if t.executed)
        total_expected = sum(t.expected_log_lr for t in executed_specs if t.executed)
        total_actual = sum(
            t.actual_log_lr for t in executed_specs
            if t.executed and t.actual_log_lr is not None
        )
        skipped_cost_saved = sum(t.cost for t in executed_specs if t.skipped)
        skipped_expected_lr_lost = sum(
            t.expected_log_lr for t in executed_specs if t.skipped
        )

        roi = total_actual / max(total_cost, EPS_NUMERIC)
        efficiency = total_actual / max(total_expected, EPS_NUMERIC)

        return {
            "total_cost_incurred": round(total_cost, 3),
            "cost_saved_by_abort": round(skipped_cost_saved, 3),
            "expected_log_lr": round(total_expected, 4),
            "actual_log_lr": round(total_actual, 4),
            "expected_log_lr_lost_by_abort": round(skipped_expected_lr_lost, 4),
            "roi": round(roi, 4),
            "efficiency": round(efficiency, 4),
            "n_executed": sum(1 for t in executed_specs if t.executed),
            "n_skipped": sum(1 for t in executed_specs if t.skipped),
        }

    # ------------------------------------------------------------------
    # Helper interno
    # ------------------------------------------------------------------

    def _get_expected_log_lr(self, tool_name: str) -> float:
        """Retorna expected_log_lr con fallback a 1.0."""
        return self._expected_lr.get(tool_name, 1.0)

    def tool_priority(self, tool_name: str) -> float:
        """Calcula prioridad P = expected_log_lr / cost para una herramienta."""
        expected = self._get_expected_log_lr(tool_name)
        cost = self._costs.get(tool_name, 1.0)
        return expected / max(cost, EPS_NUMERIC)

    def get_execution_history(self) -> List[Dict[str, Any]]:
        return list(self._execution_history)

    def reset_history(self) -> None:
        self._execution_history.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el estado del optimizer para inclusion en el bundle."""
        return {
            "epsilon": self._epsilon,
            "heavy_threshold": self.heavy_threshold,
            "tool_costs": self._costs,
            "expected_log_lr": {k: round(v, 4) for k, v in self._expected_lr.items()},
            "execution_history_count": len(self._execution_history),
        }


# ---------------------------------------------------------------------------
# ExecutionLog — registro de ejecucion para ForensicBundle
# ---------------------------------------------------------------------------

@dataclass
class ExecutionLog:
    """
    Registro del plan de ejecucion para inclusion en el ForensicBundle.
    Permite al auditor reconstruir qué pericias se ejecutaron y por qué.
    """
    plan: List[ToolSpec] = field(default_factory=list)
    abort_decisions: List[AbortDecision] = field(default_factory=list)
    roi: Optional[Dict[str, Any]] = None
    total_cost: float = 0.0
    aborted: bool = False

    def record_execution(self, spec: ToolSpec, actual_log_lr: float) -> None:
        spec.executed = True
        spec.actual_log_lr = actual_log_lr
        self.total_cost += spec.cost

    def record_skip(self, spec: ToolSpec, reason: str) -> None:
        spec.skipped = True
        spec.executed = False

    def record_abort(self, decision: AbortDecision) -> None:
        self.abort_decisions.append(decision)
        if decision.should_abort:
            self.aborted = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan": [t.to_dict() for t in self.plan],
            "abort_decisions": [d.to_dict() for d in self.abort_decisions],
            "roi": self.roi,
            "total_cost": round(self.total_cost, 4),
            "aborted": self.aborted,
        }
