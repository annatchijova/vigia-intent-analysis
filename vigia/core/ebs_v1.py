# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vigia/models/ebs_v1.py
─────────────────────────────────────────────────────────────────────────────
Evidence Bundle Specification v1.0 — Modelos de Datos PUROS

ARQUITECTURA: Capa 0 — Datos y Contratos (INMUTABLE)

REGLA ABSOLUTA: Este módulo es SOLO datos.
    - Sin lógica de negocio
    - Sin hashing
    - Sin sellado
    - Sin referencias a LLM, Ollama, backends de narrativa
    - Sin imports de capas superiores

El sellado criptografico vive en forensics/bundle_builder.py.
La narrativa LLM vive en pipeline.py como post-procesador externo.

RAZON (auditores Gemini + DeepSeek):
    Un bundle que se hashea a si mismo permite que un motor comprometido
    selle su propia mentira. El sellado debe ser un proceso externo de
    atestacion, independiente del modelo que produce los datos.

    El SystemState es matematico puro. Contaminarlo con variables de
    infraestructura no determinista (modelo LLM) hace el hash impugnable
    ante Daubert: cambiar el modelo de narrativa no debe cambiar la prueba.

INVARIANTES:
    I1 Determinismo:            mismo input -> mismo bundle
    I2 Integridad encadenada:   bundle_hash cubre TODO el contenido
    I3 Politica verificable:    policy_spec independiente del runtime
    I4 Acciones explicitas:     sin efectos implicitos
    I5 Decision explicable:     risk y posterior SIEMPRE presentes

COMPATIBILIDAD:
    Python 3.10+
    Pydantic v2 preferido, fallback dataclasses stdlib
    Sin dependencias externas en fallback
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

try:
    from pydantic import BaseModel, Field, field_validator
    _USE_PYDANTIC = True
except ImportError:
    from dataclasses import dataclass, field as dc_field
    BaseModel = object  # type: ignore
    _USE_PYDANTIC = False


# ---------------------------------------------------------------------------
# Constantes del estandar
# NOTA: verify_ebs_v1.py las replica localmente — no las importa desde aqui.
# ---------------------------------------------------------------------------

EBS_VERSION: str = "1.0"
STABILITY_THRESHOLD_FORENSIC: float = 0.85
STABILITY_THRESHOLD_EXPLORATORY: float = 0.60
Z_CLIP_MAX: float = 5.0
EPS_NUMERIC: float = 1e-9


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ===========================================================================
# SignalOutput
# ===========================================================================

if _USE_PYDANTIC:
    class SignalOutput(BaseModel):
        """
        Output canonico de herramienta forense.
        z_score = (value - baseline_mean) / baseline_MAD
        Calculado determinisiticamente. El LLM nunca participa.
        """
        tool_name: str
        signal_id: str = Field(default_factory=_new_uuid)
        value: float
        z_score: float
        confidence: float = Field(default=1.0, ge=0.0, le=1.0)
        metadata: Optional[Dict[str, Any]] = None

        @field_validator("z_score")
        @classmethod
        def _clip_z(cls, v: float) -> float:
            return max(-Z_CLIP_MAX, min(Z_CLIP_MAX, float(v)))

        @field_validator("confidence")
        @classmethod
        def _clamp_conf(cls, v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class SignalOutput:  # type: ignore
        tool_name: str
        value: float
        z_score: float
        signal_id: str = dc_field(default_factory=_new_uuid)
        confidence: float = 1.0
        metadata: Optional[Dict[str, Any]] = None

        def __post_init__(self) -> None:
            self.z_score = max(-Z_CLIP_MAX, min(Z_CLIP_MAX, float(self.z_score)))
            self.confidence = max(0.0, min(1.0, float(self.confidence)))

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# EvidenceEdge y EvidenceGraph
# ===========================================================================

if _USE_PYDANTIC:
    class EvidenceEdge(BaseModel):
        """
        Arista del grafo de evidencia con estabilidad bootstrap.
        pi_ij = freq(arista ij en B=500 remuestreos).
        Interpretacion forense: relacion estadisticamente robusta, no correlacion puntual.
        """
        source: str
        target: str
        stability: float = Field(ge=0.0, le=1.0)
        weight_mean: float = 0.0
        confidence_interval: Tuple[float, float] = (0.0, 1.0)
        dependency_type: str = "statistical_dependency"

        def is_forensically_stable(self) -> bool:
            return self.stability >= STABILITY_THRESHOLD_FORENSIC

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

    class EvidenceGraph(BaseModel):
        """
        Grafo de dependencias entre senales forenses.
        Producido por GraphStabilityEngine.
        graph_hash asignado por bundle_builder.py externamente.
        """
        nodes: List[str]
        edges: List[EvidenceEdge]
        bootstrap_rounds: int = 500
        stability_threshold: float = STABILITY_THRESHOLD_FORENSIC
        graph_hash: str = ""
        generated_at: str = Field(default_factory=_now_iso)

        def global_stability(self) -> float:
            """
            Estabilidad global PENALIZADA por fractura del grafo.

            CORRECCION CRITICA (Gemini):
            Si el grafo es un caos y queda solo una arista fuerte, el promedio
            simple de esa arista reportaria 0.9, enganando al RiskBoundedLayer.

            Formula correcta:
                S = mean(pi_estable) * (n_aristas_estables / n_aristas_posibles)

            Si el grafo esta fracturado, S -> 0 -> riesgo explota -> ABSTAIN.
            """
            n = len(self.nodes)
            if n == 0:
                return 1.0
            if n == 1:
                return 0.0

            n_possible = n * (n - 1) / 2.0
            stable = [e for e in self.edges if e.stability >= self.stability_threshold]

            if not stable:
                return 0.0

            mean_pi = sum(e.stability for e in stable) / len(stable)
            coverage = len(stable) / n_possible
            return mean_pi * coverage

        def connected_components(self) -> List[List[str]]:
            """Componentes conexas del grafo estable."""
            from collections import defaultdict
            adj: Dict[str, set] = defaultdict(set)
            for e in self.edges:
                if e.stability >= self.stability_threshold:
                    adj[e.source].add(e.target)
                    adj[e.target].add(e.source)

            visited: set = set()
            components: List[List[str]] = []

            def dfs(node: str, comp: List[str]) -> None:
                visited.add(node)
                comp.append(node)
                for nb in adj.get(node, set()):
                    if nb not in visited:
                        dfs(nb, comp)

            for node in self.nodes:
                if node not in visited:
                    comp: List[str] = []
                    dfs(node, comp)
                    components.append(comp)

            return components

        def to_dict(self) -> Dict[str, Any]:
            d = self.model_dump()
            d["edges"] = [e.to_dict() for e in self.edges]
            return d

else:
    @dataclass
    class EvidenceEdge:  # type: ignore
        source: str
        target: str
        stability: float
        weight_mean: float = 0.0
        confidence_interval: Tuple[float, float] = (0.0, 1.0)
        dependency_type: str = "statistical_dependency"

        def is_forensically_stable(self) -> bool:
            return self.stability >= STABILITY_THRESHOLD_FORENSIC

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))

    @dataclass
    class EvidenceGraph:  # type: ignore
        nodes: List[str]
        edges: List[Any]
        bootstrap_rounds: int = 500
        stability_threshold: float = STABILITY_THRESHOLD_FORENSIC
        graph_hash: str = ""
        generated_at: str = dc_field(default_factory=_now_iso)

        def global_stability(self) -> float:
            n = len(self.nodes)
            if n == 0:
                return 1.0
            if n == 1:
                return 0.0
            n_possible = n * (n - 1) / 2.0
            stable = [e for e in self.edges if e.stability >= self.stability_threshold]
            if not stable:
                return 0.0
            mean_pi = sum(e.stability for e in stable) / len(stable)
            coverage = len(stable) / n_possible
            return mean_pi * coverage

        def connected_components(self) -> List[List[str]]:
            from collections import defaultdict
            adj: Dict[str, set] = defaultdict(set)
            for e in self.edges:
                if e.stability >= self.stability_threshold:
                    adj[e.source].add(e.target)
                    adj[e.target].add(e.source)
            visited: set = set()
            components: List[List[str]] = []

            def dfs(node: str, comp: List[str]) -> None:
                visited.add(node)
                comp.append(node)
                for nb in adj.get(node, set()):
                    if nb not in visited:
                        dfs(nb, comp)

            for node in self.nodes:
                if node not in visited:
                    comp: List[str] = []
                    dfs(node, comp)
                    components.append(comp)
            return components

        def to_dict(self) -> Dict[str, Any]:
            return {
                "nodes": self.nodes,
                "edges": [e.to_dict() for e in self.edges],
                "bootstrap_rounds": self.bootstrap_rounds,
                "stability_threshold": self.stability_threshold,
                "graph_hash": self.graph_hash,
                "generated_at": self.generated_at,
            }


# ===========================================================================
# DecisionTrace
# ===========================================================================

DecisionVerdict = Literal["ACCEPT", "REJECT", "ABSTAIN"]

if _USE_PYDANTIC:
    class DecisionTrace(BaseModel):
        """
        Resultado del RiskBoundedDecisionLayer.
        Campos 100% matematicos. Sin referencias a LLM o infraestructura.
        ABSTAIN es salida valida — indica zona de incertidumbre honesta.

        Campos de trazabilidad forense (H18):
            reason_code    : código máquina del motivo de la decisión.
                             ACCEPT_POSTERIOR | REJECT_POSTERIOR |
                             ABSTAIN_DRIFT | ABSTAIN_INSTABILITY |
                             ABSTAIN_INTENTION | ABSTAIN_ZONE
            abstain_reason : descripción humana cuando decision == ABSTAIN.
            omega_intention: factor ω de consistencia de intención abductiva.
                             Inyectado por AbductiveIntentEngine. [0,1]
        """
        decision: DecisionVerdict
        posterior: float = Field(ge=0.0, le=1.0)
        risk: float = Field(ge=0.0)
        log_lr: float = 0.0
        lr: float = 0.0
        drift_score: float = 0.0
        graph_stability: float = Field(default=1.0, ge=0.0, le=1.0)
        lambda_drift: float = 2.0
        gamma_stability: float = 2.0
        epsilon_used: float = 0.05
        components_used: int = 0
        signal_contributions: Optional[List[Dict[str, Any]]] = None
        # H18: trazabilidad de causa de decisión
        reason_code: str = "UNKNOWN"
        abstain_reason: str = ""
        # Integración soberana: factor omega de intención abductiva
        omega_intention: float = Field(default=1.0, ge=0.0, le=1.0)
        consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class DecisionTrace:  # type: ignore
        decision: str
        posterior: float
        risk: float
        log_lr: float = 0.0
        lr: float = 0.0
        drift_score: float = 0.0
        graph_stability: float = 1.0
        lambda_drift: float = 2.0
        gamma_stability: float = 2.0
        epsilon_used: float = 0.05
        components_used: int = 0
        signal_contributions: Optional[List[Dict[str, Any]]] = None
        # H18
        reason_code: str = "UNKNOWN"
        abstain_reason: str = ""
        # Integración soberana
        omega_intention: float = 1.0
        consistency_score: float = 1.0

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# PolicyRule y PolicySpec
# ===========================================================================

if _USE_PYDANTIC:
    class PolicyRule(BaseModel):
        variable: str
        max_delta: float = Field(gt=0.0)
        allowed_roles: List[str] = Field(default_factory=lambda: ["system"])
        requires_approval: bool = False
        description: str = ""

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

    class PolicySpec(BaseModel):
        version: str = "1.0"
        rules: List[PolicyRule] = Field(default_factory=list)
        epsilon_accept: float = Field(default=0.05, ge=0.0, le=0.5)
        epsilon_reject: float = Field(default=0.05, ge=0.0, le=0.5)
        lambda_drift_init: float = 2.0
        gamma_stability_init: float = 2.0
        description: str = ""
        created_at: str = Field(default_factory=_now_iso)

        def get_rule(self, variable: str) -> Optional[PolicyRule]:
            for r in self.rules:
                if r.variable == variable:
                    return r
            return None

        def to_dict(self) -> Dict[str, Any]:
            d = self.model_dump()
            d["rules"] = [r.to_dict() for r in self.rules]
            return d

else:
    @dataclass
    class PolicyRule:  # type: ignore
        variable: str
        max_delta: float
        allowed_roles: List[str] = dc_field(default_factory=lambda: ["system"])
        requires_approval: bool = False
        description: str = ""

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))

    @dataclass
    class PolicySpec:  # type: ignore
        version: str = "1.0"
        rules: List[Any] = dc_field(default_factory=list)
        epsilon_accept: float = 0.05
        epsilon_reject: float = 0.05
        lambda_drift_init: float = 2.0
        gamma_stability_init: float = 2.0
        description: str = ""
        created_at: str = dc_field(default_factory=_now_iso)

        def get_rule(self, variable: str):
            for r in self.rules:
                if r.variable == variable:
                    return r
            return None

        def to_dict(self) -> Dict[str, Any]:
            d = dict(vars(self))
            d["rules"] = [r.to_dict() for r in self.rules]
            return d


# ===========================================================================
# ActionRecord
# ===========================================================================

if _USE_PYDANTIC:
    class ActionRecord(BaseModel):
        """Intervencion ejecutada. Sin efectos implicitos (I4)."""
        action_id: str = Field(default_factory=_new_uuid)
        variable: str
        delta: float
        pre_value: float
        post_value: float
        decision_before: DecisionVerdict
        decision_after: Optional[DecisionVerdict] = None
        risk_before: float
        risk_after: Optional[float] = None
        approved: bool = False
        actor: str = "system"
        timestamp: str = Field(default_factory=_now_iso)
        policy_check_result: str = "PENDING"
        rollback_available: bool = True

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class ActionRecord:  # type: ignore
        variable: str
        delta: float
        pre_value: float
        post_value: float
        decision_before: str
        risk_before: float
        action_id: str = dc_field(default_factory=_new_uuid)
        decision_after: Optional[str] = None
        risk_after: Optional[float] = None
        approved: bool = False
        actor: str = "system"
        timestamp: str = dc_field(default_factory=_now_iso)
        policy_check_result: str = "PENDING"
        rollback_available: bool = True

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# SystemState — PURIFICADO: solo parametros matematicos, sin LLM
# ===========================================================================

if _USE_PYDANTIC:
    class SystemState(BaseModel):
        """
        Estado matematico del sistema en el momento del sellado.

        PURIFICADO (DeepSeek + Gemini):
        Sin ollama_backend, sin claude_code, sin referencias a LLM.
        Si cambia el modelo de narrativa, el hash del bundle NO debe cambiar.
        La narrativa es post-procesador externo, no forma parte de la prueba.
        """
        lambda_drift: float = 2.0
        gamma_stability: float = 2.0
        epsilon_accept: float = 0.05
        epsilon_reject: float = 0.05
        drift_score: float = 0.0
        graph_stability_global: float = 1.0
        calibration_model_hash: str = ""
        engine_version: str = "vigia-ebs-v1.0"
        timestamp: str = Field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class SystemState:  # type: ignore
        lambda_drift: float = 2.0
        gamma_stability: float = 2.0
        epsilon_accept: float = 0.05
        epsilon_reject: float = 0.05
        drift_score: float = 0.0
        graph_stability_global: float = 1.0
        calibration_model_hash: str = ""
        engine_version: str = "vigia-ebs-v1.0"
        timestamp: str = dc_field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# IntegrityBlock
# ===========================================================================

if _USE_PYDANTIC:
    class IntegrityBlock(BaseModel):
        """
        Hashes SHA-256 encadenados.
        Producido por bundle_builder.py — nunca por ForensicBundle.
        """
        bundle_hash: str = ""
        graph_hash: str = ""
        policy_hash: str = ""
        decision_hash: str = ""
        engine_attestation_hash: str = ""
        ecl_hash: str = ""
        sealed_at: str = Field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class IntegrityBlock:  # type: ignore
        bundle_hash: str = ""
        graph_hash: str = ""
        policy_hash: str = ""
        decision_hash: str = ""
        engine_attestation_hash: str = ""
        ecl_hash: str = ""
        sealed_at: str = dc_field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# AbductionTrace — trazabilidad del razonamiento abductivo (PeircePlanner)
# ===========================================================================
# Este objeto registra el "por que" el sistema priorizo ciertas senales.
# Es el rastro Semiotico: Firstness -> Secondness -> Thirdness.
# Vive en ForensicBundle.abduction_trace para auditoria del perito.
# ===========================================================================

if _USE_PYDANTIC:
    class AbductionTrace(BaseModel):
        """
        Traza del razonamiento abductivo que fundamento la priorización de señales.

        Peirce Semiotics aplicada a DFIR:
            Firstness  — señal cruda observada (raw_signals_observed)
            Secondness — anomalia detectada respecto al baseline (anomalies_found)
            Thirdness  — hipotesis/ley del atacante que emerge de la correlacion
                         (hypothesis + execution_plan_rationale)

        Este objeto responde a la pregunta del perito:
            "¿Por qué el sistema priorizó ELA sobre CLIP?
             ¿Por qué abortó las pericias pesadas?
             ¿Qué señal desencadenó el REJECT?"

        REGLA: AbductionTrace es readonly post-sellado.
        BundleBuilder lo incluye en el bundle_hash.
        """
        # Firstness: lo que estaba disponible
        tools_available: List[str] = Field(default_factory=list)
        tools_executed: List[str] = Field(default_factory=list)
        tools_skipped: List[str] = Field(default_factory=list)

        # Secondness: que senales resultaron anomalas
        dominant_signal: Optional[str] = None
        dominant_z_score: float = 0.0
        cluster_name: Optional[str] = None
        anomalies_found: List[Dict[str, Any]] = Field(default_factory=list)

        # Thirdness: la hipotesis emergente
        peirce_firstness: str = ""   # "Señal SDA con z=3.2 detectada"
        peirce_secondness: str = ""  # "Anomalia respecto a baseline AUTHENTIC"
        peirce_thirdness: str = ""   # "Patron consistente con fabricacion LLM"

        # Razon de priorizacion del ResourceOptimizer
        execution_plan_rationale: List[Dict[str, Any]] = Field(default_factory=list)
        abort_reason: Optional[str] = None
        abort_triggered: bool = False

        # Metadatos de trazabilidad
        inference_mode: str = "FALLBACK"
        clustering_method: str = "heuristic_default"
        correlation_penalties_applied: bool = False

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class AbductionTrace:  # type: ignore
        tools_available: List[str] = dc_field(default_factory=list)
        tools_executed: List[str] = dc_field(default_factory=list)
        tools_skipped: List[str] = dc_field(default_factory=list)
        dominant_signal: Optional[str] = None
        dominant_z_score: float = 0.0
        cluster_name: Optional[str] = None
        anomalies_found: List[Dict[str, Any]] = dc_field(default_factory=list)
        peirce_firstness: str = ""
        peirce_secondness: str = ""
        peirce_thirdness: str = ""
        execution_plan_rationale: List[Dict[str, Any]] = dc_field(default_factory=list)
        abort_reason: Optional[str] = None
        abort_triggered: bool = False
        inference_mode: str = "FALLBACK"
        clustering_method: str = "heuristic_default"
        correlation_penalties_applied: bool = False

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# ForensicBundle — ESTRUCTURA DE DATOS PURA
# Sin seal(), sin hashing, sin quick_verify()
# El sellado es responsabilidad exclusiva de forensics/bundle_builder.py
# ===========================================================================

class ForensicBundle:
    """
    Artefacto EBS v1 — contenedor de datos puro.

    REFACTORIZADO: Este objeto NO se sella a si mismo.
    El sellado es ejecutado por forensics/bundle_builder.py como proceso
    externo de atestacion. Esto garantiza que un motor comprometido no pueda
    sellar su propia mentira.

    Flujo correcto:
        bundle = ForensicBundle(...)          # datos puros
        sealed_dict = BundleBuilder.seal(bundle)   # atestacion externa
        BundleBuilder.save(sealed_dict, path)
        # => verify_ebs_v1.py path  (stdlib puro, sin imports de produccion)
    """

    VERSION = EBS_VERSION

    def __init__(
        self,
        evidence_graph: EvidenceGraph,
        decision_trace: DecisionTrace,
        policy_spec: PolicySpec,
        actions: Optional[List[ActionRecord]] = None,
        system_state: Optional[SystemState] = None,
        abduction_trace: Optional[AbductionTrace] = None,
    ) -> None:
        self.bundle_id: str = _new_uuid()
        self.bundle_version: str = self.VERSION
        self.timestamp: str = _now_iso()
        self.evidence_graph: EvidenceGraph = evidence_graph
        self.decision_trace: DecisionTrace = decision_trace
        self.policy_spec: PolicySpec = policy_spec
        self.actions: List[ActionRecord] = actions or []
        self.system_state: SystemState = system_state or SystemState()
        # abduction_trace: trazabilidad del razonamiento abductivo (PeircePlanner)
        # Responde al perito: "por que se priorizaron estas senales"
        self.abduction_trace: Optional[AbductionTrace] = abduction_trace
        # integrity: asignado externamente por BundleBuilder.seal()
        self.integrity: Optional[IntegrityBlock] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa el contenido del bundle (sin integrity — la agrega BundleBuilder).

        Incluye abduction_trace si esta presente: es parte del hash del bundle
        y permite al auditor verificar el razonamiento abductivo completo.
        """
        d = {
            "bundle_id": self.bundle_id,
            "bundle_version": self.bundle_version,
            "timestamp": self.timestamp,
            "evidence_graph": self.evidence_graph.to_dict(),
            "decision_trace": self.decision_trace.to_dict(),
            "policy_spec": self.policy_spec.to_dict(),
            "actions": [a.to_dict() for a in self.actions],
            "system_state": self.system_state.to_dict(),
        }
        # abduction_trace es opcional — si existe, se incluye en el bundle_hash (I2)
        if self.abduction_trace is not None:
            d["abduction_trace"] = self.abduction_trace.to_dict()
        return d

    def __repr__(self) -> str:
        sealed = self.integrity is not None
        decision = getattr(self.decision_trace, "decision", "?")
        return (
            f"<ForensicBundle id={self.bundle_id[:8]} "
            f"decision={decision} "
            f"sealed={'YES' if sealed else 'NO'}>"
        )


# ===========================================================================
# Factory
# ===========================================================================

def make_default_policy(
    epsilon: float = 0.05,
    lambda_drift: float = 2.0,
    gamma_stability: float = 2.0,
) -> PolicySpec:
    rules = [
        PolicyRule(variable="posterior", max_delta=0.10,
                   allowed_roles=["system", "analyst"],
                   description="Limite de cambio en probabilidad posterior"),
        PolicyRule(variable="drift", max_delta=0.15,
                   allowed_roles=["system"],
                   description="Limite de correccion de drift"),
        PolicyRule(variable="graph_stability", max_delta=0.05,
                   allowed_roles=["system"], requires_approval=True,
                   description="Cambios en estabilidad del grafo requieren aprobacion"),
        PolicyRule(variable="lambda_drift", max_delta=1.0,
                   allowed_roles=["system"],
                   description="Ajuste adaptativo de sensibilidad al drift"),
        PolicyRule(variable="gamma_stability", max_delta=1.0,
                   allowed_roles=["system"],
                   description="Ajuste adaptativo de sensibilidad estructural"),
    ]
    return PolicySpec(
        version="1.0", rules=rules,
        epsilon_accept=epsilon, epsilon_reject=epsilon,
        lambda_drift_init=lambda_drift, gamma_stability_init=gamma_stability,
        description="Politica VIGIA por defecto — SANS FIND EVIL 2026",
    )
