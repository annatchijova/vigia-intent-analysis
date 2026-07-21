"""
vigia/models/ebs_v1.py
─────────────────────────────────────────────────────────────────────────────
Evidence Bundle Specification v1.0 — Contratos de datos VIGÍA Forensic Suite

ARQUITECTURA: Capa 0 — Datos y Contratos (INMUTABLE)
REGLA DE AISLAMIENTO: Esta capa NO importa nada de capas superiores.
    models → (nada)

CONTRATOS IMPLEMENTADOS:
    SignalOutput       — output canónico de toda herramienta forense
    EvidenceEdge       — arista del grafo con estabilidad bootstrap (π ≥ 0.85)
    EvidenceGraph      — grafo de dependencias emergente (no hardcoded)
    DecisionTrace      — tríada posterior/risk/decision con veredicto
    PolicyRule         — regla individual de gobernanza
    PolicySpec         — especificación de política verificable externamente
    ActionRecord       — acción ejecutada con trazabilidad completa
    SystemState        — estado de parámetros adaptativos (λ, γ, ε)
    IntegrityBlock     — hashes SHA-256 encadenados del bundle completo
    ForensicBundle     — artefacto sellado EBS v1 exportable a SIFT

INVARIANTES DEL ESTÁNDAR (no negociables):
    I1 — Determinismo:       mismo input analítico → mismo resultado; este
                              módulo legacy asigna UUID/timestamp por corrida
                              y no debe usarse para comparar bundle_hash de replays
    I2 — Integridad encadenada: bundle_hash cubre TODO el contenido
    I3 — Política verificable: policy_spec es independiente del runtime
    I4 — Acciones explícitas: no existen efectos implícitos
    I5 — Decisión explicable: risk y posterior SIEMPRE presentes

COMPATIBILIDAD:
    Python 3.10+
    Pydantic v2 (preferido) con fallback a dataclasses puro
    Sin dependencias de capas superiores

SIFT INTEGRATION:
    ForensicBundle es el artefacto de entrega a SIFT.
    El verificador independiente (forensics/verify_ebs_v1.py) consume
    únicamente este módulo + stdlib.

Diseño acordado: ChatGPT / Gemini / DeepSeek / Claude — SANS FIND EVIL 2026
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

# ---------------------------------------------------------------------------
# Pydantic v2 preferido; fallback a dataclasses puros para entornos mínimos
# ---------------------------------------------------------------------------
try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    _USE_PYDANTIC = True
except ImportError:
    from dataclasses import dataclass, field
    BaseModel = object  # type: ignore
    _USE_PYDANTIC = False


# ---------------------------------------------------------------------------
# Constantes del estándar
# ---------------------------------------------------------------------------

EBS_VERSION: str = "1.0"
STABILITY_THRESHOLD_FORENSIC: float = 0.85  # π mínimo para aristas fuertes
STABILITY_THRESHOLD_EXPLORATORY: float = 0.60
Z_CLIP_MAX: float = 5.0   # extendido de 3.0 con Ledoit-Wolf activo
EPS_NUMERIC: float = 1e-9


# ---------------------------------------------------------------------------
# Helpers criptográficos — sin dependencias externas
# ---------------------------------------------------------------------------

# Lockstep con vigia/core/canonicalize.py (R3-2): v2 default, v1 legacy.
import unicodedata as _unicodedata
from fractions import Fraction as _Fraction

_V2_STR_PREFIX = "s:"


def _v2_norm_str(s):
    return _unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n"))


def _canonicalize_v1(obj: Any) -> Any:
    """Esquema v1 (LEGACY — solo verificacion de bundles historicos)."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return obj
    if obj is None:
        return "null"
    if isinstance(obj, dict):
        return {k: _canonicalize_v1(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v1(v) for v in obj]
    return str(obj)


def _canonicalize_v2(obj: Any) -> Any:
    """Esquema v2 (R3-2) — DEFAULT. Escalares identicos a v1; strings escapados
    (s: + NFC/CRLF->LF); Fraction explicito. Cierra las colisiones de tipo."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return _V2_STR_PREFIX + _v2_norm_str(obj)
    if obj is None:
        return "null"
    if isinstance(obj, _Fraction):
        return f"{obj.numerator}/{obj.denominator}:frac"
    if isinstance(obj, dict):
        return {k: _canonicalize_v2(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v2(v) for v in obj]
    return _V2_STR_PREFIX + _v2_norm_str(str(obj))


def _canonicalize(obj: Any) -> Any:
    """Forma canonica DEFAULT (v2). Ver vigia/core/canonicalize.py."""
    return _canonicalize_v2(obj)


def _sha256_dict(obj: Dict) -> str:
    """SHA-256 determinístico con canonicalización estricta (H22)."""
    canonical  = _canonicalize(obj)
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# CAPA 0A — SignalOutput
# Contrato canónico de toda herramienta forense.
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class SignalOutput(BaseModel):
        """
        Output canónico de herramienta forense.

        Toda herramienta (SDA, ACP, CLI, ROI, GCI, DGPI, ELA, CLIP, etc.)
        DEBE producir un SignalOutput. El LikelihoodEngine consume EXCLUSIVAMENTE
        este contrato. El LLM nunca participa en su cálculo.

        Campos:
            tool_name  : identificador de herramienta (ej: "SDA", "GCI")
            signal_id  : UUID único de esta instancia de análisis
            value      : valor bruto en escala propia de la herramienta
            z_score    : (value - baseline_mean) / baseline_MAD
                         Calculado con MAD para robustez ante outliers (Peirce/Thirdness).
                         NUNCA calculado por LLM.
            confidence : calidad de la señal [0.0, 1.0] — NO es P(fraude)
            metadata   : payload de trazabilidad Daubert
                         Incluir: emitter_type, generator_version, transform_chain
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
            """Clipping defensivo — outliers no deben explotar el LR."""
            return max(-Z_CLIP_MAX, min(Z_CLIP_MAX, float(v)))

        @field_validator("confidence")
        @classmethod
        def _clamp_confidence(cls, v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

else:
    @dataclass
    class SignalOutput:  # type: ignore
        tool_name: str
        value: float
        z_score: float
        signal_id: str = field(default_factory=_new_uuid)
        confidence: float = 1.0
        metadata: Optional[Dict[str, Any]] = None

        def __post_init__(self) -> None:
            self.z_score = max(-Z_CLIP_MAX, min(Z_CLIP_MAX, float(self.z_score)))
            self.confidence = max(0.0, min(1.0, float(self.confidence)))

        def to_dict(self) -> Dict[str, Any]:
            return {
                "tool_name": self.tool_name,
                "signal_id": self.signal_id,
                "value": self.value,
                "z_score": self.z_score,
                "confidence": self.confidence,
                "metadata": self.metadata,
            }


# ---------------------------------------------------------------------------
# CAPA 0B — EvidenceEdge y EvidenceGraph
# Grafo emergente de dependencias (bootstrap stability selection).
# NO es hardcoded: las aristas emergen del dato.
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class EvidenceEdge(BaseModel):
        """
        Arista del grafo de evidencia con estabilidad bootstrap.

        π_ij = frecuencia de aparición de la arista (i,j) en B=500 remuestreos.
        Solo aristas con π ≥ threshold son incluidas en el grafo final.

        Interpretación forense (defendible en tribunal):
            "Esta relación aparece consistentemente en [π*100]% de los mundos
             estadísticos posibles del dataset."
        """
        source: str
        target: str
        stability: float = Field(ge=0.0, le=1.0)
        weight_mean: float = 0.0
        confidence_interval: Tuple[float, float] = (0.0, 1.0)
        dependency_type: str = "statistical_dependency"  # spearman / MI / partial_corr

        @field_validator("stability")
        @classmethod
        def _clamp_stability(cls, v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        def is_forensically_stable(self) -> bool:
            """True si π ≥ 0.85 (umbral forense fuerte)."""
            return self.stability >= STABILITY_THRESHOLD_FORENSIC

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

    class EvidenceGraph(BaseModel):
        """
        Grafo de dependencias entre señales forenses.

        Producido por GraphStabilityEngine (engine/graph_stability.py).
        Sellado criptográficamente al construir el ForensicBundle.

        Propiedad clave: los clusters NO son hardcoded. Emergen del dato
        via bootstrap + stability selection. Esto es auditablemente correcto
        ante Daubert: "la estructura fue aprendida del dataset, no impuesta."
        """
        nodes: List[str]
        edges: List[EvidenceEdge]
        bootstrap_rounds: int = 500
        stability_threshold: float = STABILITY_THRESHOLD_FORENSIC
        graph_hash: str = ""
        generated_at: str = Field(default_factory=_now_iso)

        def compute_graph_hash(self) -> str:
            payload = {
                "nodes": sorted(self.nodes),
                "edges": [e.to_dict() for e in sorted(
                    self.edges, key=lambda x: (x.source, x.target)
                )],
                "bootstrap_rounds": self.bootstrap_rounds,
                "threshold": self.stability_threshold,
            }
            return _sha256_dict(payload)

        def global_stability(self) -> float:
            """
            Estabilidad promedio del grafo.
            Usado por RiskBoundedDecisionLayer como factor S en r_total.
            """
            if not self.edges:
                return 0.0
            return sum(e.stability for e in self.edges) / len(self.edges)

        def connected_components(self) -> List[List[str]]:
            """
            Componentes conexas del grafo estable.
            Reemplazan los CLUSTERS hardcoded del sistema v0.
            """
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
                for neighbor in adj.get(node, set()):
                    if neighbor not in visited:
                        dfs(neighbor, comp)

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
    # Fallback dataclasses — funcionalidad mínima garantizada
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
        generated_at: str = field(default_factory=_now_iso)

        def compute_graph_hash(self) -> str:
            payload = {
                "nodes": sorted(self.nodes),
                "edges": [e.to_dict() for e in self.edges],
            }
            return _sha256_dict(payload)

        def global_stability(self) -> float:
            if not self.edges:
                return 0.0
            return sum(e.stability for e in self.edges) / len(self.edges)

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
                for n in adj.get(node, set()):
                    if n not in visited:
                        dfs(n, comp)

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


# ---------------------------------------------------------------------------
# CAPA 0C — DecisionTrace
# Tríada posterior / risk / decision. Siempre explícita.
# ---------------------------------------------------------------------------

DecisionVerdict = Literal["ACCEPT", "REJECT", "ABSTAIN"]

if _USE_PYDANTIC:
    class DecisionTrace(BaseModel):
        """
        Resultado del RiskBoundedDecisionLayer.

        decision : ACCEPT / REJECT / ABSTAIN
                   ABSTAIN es salida válida — no indica error del sistema.
                   Indica que r_total ∈ (ε_accept, 1 - ε_reject): zona de
                   incertidumbre donde forzar decisión sería indefendible.

        posterior: P(fabricación | evidencia) ∈ [0, 1]
        risk     : r_total = (1-P)·(1+λD)·(1+γ(1-S)) ∈ [0, ∞)
                   clipeado a [0, 1] para la regla de decisión.
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
        reason_code: str = "OK"
        abstain_reason: Optional[str] = None
        omega_intention: float = 0.5

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
        reason_code: str = "OK"
        abstain_reason: Optional[str] = None
        omega_intention: float = 0.5

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ---------------------------------------------------------------------------
# CAPA 0D — PolicyRule y PolicySpec
# Gobernanza verificable externamente (independiente del runtime).
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class PolicyRule(BaseModel):
        """Regla individual de gobernanza. Inmutable durante ejecución."""
        variable: str
        max_delta: float = Field(gt=0.0)
        allowed_roles: List[str] = Field(default_factory=lambda: ["system"])
        requires_approval: bool = False
        description: str = ""

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

    class PolicySpec(BaseModel):
        """
        Especificación de política verificable externamente.

        INVARIANTE I3: policy_spec es independiente del sistema.
        Un auditor externo puede validar esta política sin acceso al runtime.

        La política se incluye en el ForensicBundle y su hash queda sellado.
        """
        version: str = "1.0"
        rules: List[PolicyRule] = Field(default_factory=list)
        epsilon_accept: float = Field(default=0.05, ge=0.0, le=0.5)
        epsilon_reject: float = Field(default=0.05, ge=0.0, le=0.5)
        lambda_drift_init: float = 2.0
        gamma_stability_init: float = 2.0
        description: str = ""
        created_at: str = Field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            d = self.model_dump()
            d["rules"] = [r.to_dict() for r in self.rules]
            return d

        def get_rule(self, variable: str) -> Optional[PolicyRule]:
            for r in self.rules:
                if r.variable == variable:
                    return r
            return None

else:
    @dataclass
    class PolicyRule:  # type: ignore
        variable: str
        max_delta: float
        allowed_roles: List[str] = field(default_factory=lambda: ["system"])
        requires_approval: bool = False
        description: str = ""

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))

    @dataclass
    class PolicySpec:  # type: ignore
        version: str = "1.0"
        rules: List[Any] = field(default_factory=list)
        epsilon_accept: float = 0.05
        epsilon_reject: float = 0.05
        lambda_drift_init: float = 2.0
        gamma_stability_init: float = 2.0
        description: str = ""
        created_at: str = field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            d = dict(vars(self))
            d["rules"] = [r.to_dict() for r in self.rules]
            return d

        def get_rule(self, variable: str):
            for r in self.rules:
                if r.variable == variable:
                    return r
            return None


# ---------------------------------------------------------------------------
# CAPA 0E — ActionRecord
# Toda acción ejecutada queda sellada. Sin efectos implícitos (I4).
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class ActionRecord(BaseModel):
        """
        Registro de intervención ejecutada por SafeActionExecutor.

        INVARIANTE I4: no existen efectos implícitos.
        Toda modificación del estado del sistema queda documentada aquí.
        """
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
        action_id: str = field(default_factory=_new_uuid)
        decision_after: Optional[str] = None
        risk_after: Optional[float] = None
        approved: bool = False
        actor: str = "system"
        timestamp: str = field(default_factory=_now_iso)
        policy_check_result: str = "PENDING"
        rollback_available: bool = True

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ---------------------------------------------------------------------------
# CAPA 0F — SystemState
# Estado de parámetros adaptativos. Trazable por versión.
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class SystemState(BaseModel):
        """
        Estado del sistema en el momento de producción del bundle.

        Incluye parámetros adaptativos (λ, γ, ε) y métricas de drift.
        Queda sellado en el ForensicBundle para reproducibilidad.
        """
        lambda_drift: float = 2.0
        gamma_stability: float = 2.0
        epsilon_accept: float = 0.05
        epsilon_reject: float = 0.05
        drift_score: float = 0.0
        graph_stability_global: float = 1.0
        calibration_model_hash: str = ""
        engine_version: str = "vigia-ebs-v1.0"
        ollama_backend: Optional[str] = None   # modelo Ollama activo si aplica
        timestamp: str = Field(default_factory=_now_iso)
        extra: Optional[Dict[str, Any]] = None

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
        ollama_backend: Optional[str] = None
        timestamp: str = field(default_factory=_now_iso)
        extra: Optional[Dict[str, Any]] = None

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ---------------------------------------------------------------------------
# CAPA 0G — IntegrityBlock
# SHA-256 encadenados. Cobertura total del bundle.
# ---------------------------------------------------------------------------

if _USE_PYDANTIC:
    class IntegrityBlock(BaseModel):
        """
        Hashes SHA-256 encadenados del bundle.

        INVARIANTE I2: bundle_hash cubre TODO el contenido.
        Cualquier modificación de cualquier campo → bundle inválido.

        Campos adicionales para SIFT:
            engine_attestation_hash: hash(source_code + deps + build_spec)
            ecl_hash: External Constraint Layer (referencia inmutable externa)
        """
        bundle_hash: str = ""
        graph_hash: str = ""
        policy_hash: str = ""
        decision_hash: str = ""
        engine_attestation_hash: str = ""
        ecl_hash: str = ""  # External Constraint Layer — vacío si no aplica
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
        sealed_at: str = field(default_factory=_now_iso)

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ---------------------------------------------------------------------------
# CAPA 0H — ForensicBundle (artefacto sellado EBS v1)
# Este es el objeto de entrega final a SIFT.
# ---------------------------------------------------------------------------

class ForensicBundle:
    """
    Artefacto sellado EBS v1 — unidad de entrega a SIFT.

    CONTIENE:
        evidence_graph  : grafo probabilístico emergente
        decision_trace  : posterior / risk / decision con trazabilidad
        policy_spec     : política activa verificable externamente
        actions         : historial de intervenciones ejecutadas
        system_state    : parámetros del sistema en el momento del sellado
        integrity       : hashes SHA-256 encadenados (sellado criptográfico)

    PROPIEDADES:
        - Legacy custody seal: mismo input preserva la salida analítica, pero
          UUID/timestamp nuevos hacen que cada `bundle_hash` sea por corrida
        - Autocontenido: auditable sin acceso al runtime
        - Portable: compatible con cualquier verificador EBS v1
        - SIFT-ready: exportable directamente como JSON

    REGLA DE ORO:
        El LLM (PeircePlanner) NO participa en la construcción del bundle.
        Su única función es traducir el bundle sellado a narrativa humana.
        La decisión matemática ya está cerrada cuando el LLM entra.
    """

    VERSION = EBS_VERSION

    def __init__(
        self,
        evidence_graph: EvidenceGraph,
        decision_trace: DecisionTrace,
        policy_spec: PolicySpec,
        actions: Optional[List[ActionRecord]] = None,
        system_state: Optional[SystemState] = None,
        abduction_trace: Optional[Any] = None,
    ) -> None:
        self.bundle_id: str = _new_uuid()
        self.bundle_version: str = self.VERSION
        self.timestamp: str = _now_iso()
        self.evidence_graph: EvidenceGraph = evidence_graph
        self.decision_trace: DecisionTrace = decision_trace
        self.policy_spec: PolicySpec = policy_spec
        self.actions: List[ActionRecord] = actions or []
        self.system_state: SystemState = system_state or SystemState()
        self.abduction_trace = abduction_trace
        self.integrity: IntegrityBlock = IntegrityBlock()
        self._sealed: bool = False

    # ------------------------------------------------------------------
    # Sellado criptográfico
    # ------------------------------------------------------------------

    def seal(self, engine_attestation_hash: str = "", ecl_hash: str = "") -> "ForensicBundle":
        """
        Sella el bundle calculando todos los hashes encadenados.

        Una vez sellado, cualquier modificación invalida bundle_hash.
        El sellado es idempotente si el contenido no cambia.

        INVARIANTE I2: bundle_hash cubre TODO.
        """
        if self._sealed:
            # Re-sellar si se llama de nuevo (permite reconstrucción)
            self._sealed = False

        # Paso 1: hashes de sub-componentes
        # graph_hash se calcula sobre el grafo SIN el campo graph_hash
        # (ese campo es el resultado, no puede ser input de sí mismo)
        graph_dict_full = self.evidence_graph.to_dict()
        graph_dict_for_hash = {k: v for k, v in graph_dict_full.items() if k != "graph_hash"}
        policy_dict = self.policy_spec.to_dict()
        decision_dict = self.decision_trace.to_dict()

        graph_hash = _sha256_dict(graph_dict_for_hash)
        policy_hash = _sha256_dict(policy_dict)
        decision_hash = _sha256_dict(decision_dict)

        # Paso 2: asignar graph_hash al objeto y actualizar el dict
        self.evidence_graph.graph_hash = graph_hash
        graph_dict_final = self.evidence_graph.to_dict()  # ahora incluye graph_hash

        # Paso 3: bundle_hash cubre TODO el contenido (incluye graph_hash en el grafo)
        bundle_payload = {
            "bundle_id": self.bundle_id,
            "bundle_version": self.bundle_version,
            "timestamp": self.timestamp,
            "evidence_graph": graph_dict_final,
            "decision_trace": decision_dict,
            "policy_spec": policy_dict,
            "actions": [a.to_dict() for a in self.actions],
            "system_state": self.system_state.to_dict(),
            "abduction_trace": (
                self.abduction_trace.to_dict()
                if hasattr(self.abduction_trace, "to_dict") else
                (self.abduction_trace or {})
            ),
        }
        bundle_hash = _sha256_dict(bundle_payload)

        self.integrity = IntegrityBlock(
            bundle_hash=bundle_hash,
            graph_hash=graph_hash,
            policy_hash=policy_hash,
            decision_hash=decision_hash,
            engine_attestation_hash=engine_attestation_hash,
            ecl_hash=ecl_hash,
        )
        self._sealed = True
        return self

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialización canónica para SIFT / verificador independiente."""
        if not self._sealed:
            raise RuntimeError(
                "ForensicBundle no sellado. Llamar .seal() antes de exportar."
            )
        return {
            "bundle_id": self.bundle_id,
            "bundle_version": self.bundle_version,
            "timestamp": self.timestamp,
            "evidence_graph": self.evidence_graph.to_dict(),
            "decision_trace": self.decision_trace.to_dict(),
            "policy_spec": self.policy_spec.to_dict(),
            "actions": [a.to_dict() for a in self.actions],
            "system_state": self.system_state.to_dict(),
            "abduction_trace": (
                self.abduction_trace.to_dict()
                if hasattr(self.abduction_trace, "to_dict") else
                (self.abduction_trace or {})
            ),
            "integrity": self.integrity.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        """JSON canónico para exportación a archivo."""
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent, default=str)

    def save(self, path: str) -> str:
        """
        Guarda el bundle sellado en disco.
        Retorna el hash del archivo para verificación de transporte.

        L-023 (Q4): escritura ATÓMICA vía atomic_io (mkstemp mismo directorio
        + fsync + os.replace + fsync del directorio) — paridad con
        vigia/core/bundle_builder.py y vigia_agent.py. El hash retornado se
        computa RE-LEYENDO de disco (lo que se atesta es lo que quedó escrito,
        no la variable en memoria) y se verifica contra el hash en memoria —
        divergencia = RuntimeError, nunca un hash que no corresponde al archivo.
        """
        # Import en scope de función: preserva la regla de aislamiento de capa
        # (models no importa vigia.* a nivel módulo; atomic_io es stdlib-only).
        from vigia.core.atomic_io import atomic_write_text

        content = self.to_json()
        mem_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        atomic_write_text(path, content)
        with open(path, "rb") as f:
            disk_hash = hashlib.sha256(f.read()).hexdigest()
        if disk_hash != mem_hash:
            raise RuntimeError(
                f"L-023: hash en disco difiere del hash en memoria tras la "
                f"escritura atómica ({disk_hash[:16]} != {mem_hash[:16]}) — "
                f"posible corrupción de filesystem o tampering concurrente."
            )
        return disk_hash

    # ------------------------------------------------------------------
    # Verificación rápida interna (no reemplaza verify_ebs_v1.py)
    # ------------------------------------------------------------------

    def quick_verify(self) -> Tuple[bool, str]:
        """
        Verificación interna rápida de integridad.
        El verificador externo completo está en forensics/verify_ebs_v1.py.

        Retorna: (is_valid: bool, message: str)
        """
        if not self._sealed:
            return False, "Bundle no sellado"

        d = self.to_dict()

        # Recomputar bundle_hash
        payload = {
            "bundle_id": d["bundle_id"],
            "bundle_version": d["bundle_version"],
            "timestamp": d["timestamp"],
            "evidence_graph": d["evidence_graph"],
            "decision_trace": d["decision_trace"],
            "policy_spec": d["policy_spec"],
            "actions": d["actions"],
            "system_state": d["system_state"],
        }
        recomputed = _sha256_dict(payload)
        stored = d["integrity"]["bundle_hash"]

        if recomputed != stored:
            return False, f"bundle_hash no coincide: {recomputed[:8]}... != {stored[:8]}..."

        return True, "OK — bundle íntegro"

    def __repr__(self) -> str:
        status = "SELLADO" if self._sealed else "NO SELLADO"
        decision = self.decision_trace.decision if hasattr(self.decision_trace, "decision") else "?"
        return (
            f"<ForensicBundle id={self.bundle_id[:8]} "
            f"decision={decision} "
            f"status={status}>"
        )


# ---------------------------------------------------------------------------
# Factory helpers — para construcción rápida en tests y pipelines
# ---------------------------------------------------------------------------

def make_default_policy(
    epsilon: float = 0.05,
    lambda_drift: float = 2.0,
    gamma_stability: float = 2.0,
) -> PolicySpec:
    """Política por defecto para entornos de desarrollo y testing."""
    rules = [
        PolicyRule(
            variable="posterior",
            max_delta=0.10,
            allowed_roles=["system", "analyst"],
            description="Límite de cambio en probabilidad posterior",
        ),
        PolicyRule(
            variable="drift",
            max_delta=0.15,
            allowed_roles=["system"],
            description="Límite de corrección de drift",
        ),
        PolicyRule(
            variable="graph_stability",
            max_delta=0.05,
            allowed_roles=["system"],
            requires_approval=True,
            description="Cambios en estabilidad del grafo requieren aprobación",
        ),
        PolicyRule(
            variable="lambda_drift",
            max_delta=1.0,
            allowed_roles=["system"],
            description="Ajuste adaptativo de sensibilidad al drift",
        ),
        PolicyRule(
            variable="gamma_stability",
            max_delta=1.0,
            allowed_roles=["system"],
            description="Ajuste adaptativo de sensibilidad estructural",
        ),
    ]
    return PolicySpec(
        version="1.0",
        rules=rules,
        epsilon_accept=epsilon,
        epsilon_reject=epsilon,
        lambda_drift_init=lambda_drift,
        gamma_stability_init=gamma_stability,
        description="Política VIGÍA por defecto — SANS FIND EVIL 2026",
    )


# =============================================================================
# STUBS — clases requeridas por pipeline.py, pendientes de implementación full
# Cumplen la interfaz mínima para que el pipeline no crashee en import/init.
# =============================================================================

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class AbductionTrace:
    """Traza abductiva Peirce (Firstness/Secondness/Thirdness) del pipeline."""
    peirce_firstness: str = ""
    peirce_secondness: str = ""
    peirce_thirdness: str = ""
    tools_available: int = 0
    tools_executed: int = 0
    tools_skipped: int = 0
    dominant_signal: str = ""
    dominant_z_score: float = 0.0
    cluster_name: str = ""
    anomalies_found: int = 0
    execution_plan_rationale: str = ""
    abort_triggered: bool = False
    inference_mode: str = "heuristic"
    clustering_method: str = "heuristic_default"
    correlation_penalties_applied: bool = False

    def to_dict(self) -> dict:
        return {
            "peirce_firstness":  self.peirce_firstness,
            "peirce_secondness": self.peirce_secondness,
            "peirce_thirdness":  self.peirce_thirdness,
            "dominant_signal":   self.dominant_signal,
            "dominant_z_score":  self.dominant_z_score,
            "cluster_name":      self.cluster_name,
            "inference_mode":    self.inference_mode,
            "abort_triggered":   self.abort_triggered,
        }


class PolicyStabilityController:
    """Controlador de estabilidad de política — stub mínimo."""
    def __init__(self):
        self.stability_score: float = 1.0
        self.drift_count: int = 0

    def record_drift(self, delta: float = 0.0) -> None:
        self.drift_count += 1
        self.stability_score = max(0.0, self.stability_score - abs(delta) * 0.1)

    def is_stable(self, threshold: float = 0.7) -> bool:
        return self.stability_score >= threshold


class SelfAdaptiveRiskPolicy:
    """Política de riesgo auto-adaptativa — stub mínimo."""
    def __init__(
        self,
        lambda_init: float = 0.5,
        gamma_init: float = 0.5,
        epsilon_init: float = 0.05,
        stability_controller: Optional[PolicyStabilityController] = None,
    ):
        self.lambda_drift = lambda_init
        self.gamma_stability = gamma_init
        self.epsilon = epsilon_init
        self._ctrl = stability_controller or PolicyStabilityController()

    def update(self, observed_drift: float, observed_stability: float) -> None:
        self._ctrl.record_drift(observed_drift - self.lambda_drift)
        self.lambda_drift = round(
            self.lambda_drift * 0.9 + observed_drift * 0.1, 6
        )
        self.gamma_stability = round(
            self.gamma_stability * 0.9 + observed_stability * 0.1, 6
        )

    def get_params(self) -> dict:
        return {
            "lambda_drift":    self.lambda_drift,
            "gamma_stability": self.gamma_stability,
            "epsilon":         self.epsilon,
            "stable":          self._ctrl.is_stable(),
        }


# =============================================================================
# STUBS — AbductionTrace, PolicyStabilityController, SelfAdaptiveRiskPolicy
# Requeridos por pipeline.py. Implementación mínima funcional.
# =============================================================================
from dataclasses import dataclass as _dataclass
from typing import Optional as _Optional

@_dataclass
class AbductionTrace:
    """Traza abductiva Peirce del pipeline."""
    peirce_firstness: str = ""
    peirce_secondness: str = ""
    peirce_thirdness: str = ""
    tools_available: int = 0
    tools_executed: int = 0
    tools_skipped: int = 0
    dominant_signal: str = ""
    dominant_z_score: float = 0.0
    cluster_name: str = ""
    anomalies_found: int = 0
    execution_plan_rationale: str = ""
    abort_triggered: bool = False
    inference_mode: str = "heuristic"
    clustering_method: str = "heuristic_default"
    correlation_penalties_applied: bool = False

    def to_dict(self) -> dict:
        return {
            "peirce_firstness":  self.peirce_firstness,
            "peirce_secondness": self.peirce_secondness,
            "peirce_thirdness":  self.peirce_thirdness,
            "dominant_signal":   self.dominant_signal,
            "dominant_z_score":  self.dominant_z_score,
            "cluster_name":      self.cluster_name,
            "inference_mode":    self.inference_mode,
            "abort_triggered":   self.abort_triggered,
        }


class PolicyStabilityController:
    def __init__(self):
        self.stability_score: float = 1.0
        self.drift_count: int = 0

    def record_drift(self, delta: float = 0.0) -> None:
        self.drift_count += 1
        self.stability_score = max(0.0, self.stability_score - abs(delta) * 0.1)

    def is_stable(self, threshold: float = 0.7) -> bool:
        return self.stability_score >= threshold


class SelfAdaptiveRiskPolicy:
    def __init__(
        self,
        lambda_init: float = 0.5,
        gamma_init: float = 0.5,
        epsilon_init: float = 0.05,
        stability_controller: _Optional[PolicyStabilityController] = None,
    ):
        self.lambda_drift = lambda_init
        self.gamma_stability = gamma_init
        self.epsilon = epsilon_init
        self._ctrl = stability_controller or PolicyStabilityController()
        # Aliases que usa pipeline.py
        self.lambda_t = lambda_init
        self.gamma_t  = gamma_init

    def update(self, observed_drift: float, observed_stability: float) -> None:
        self._ctrl.record_drift(observed_drift - self.lambda_drift)
        self.lambda_drift = round(self.lambda_drift * 0.9 + observed_drift * 0.1, 6)
        self.gamma_stability = round(self.gamma_stability * 0.9 + observed_stability * 0.1, 6)

    def get_params(self) -> dict:
        return {
            "lambda_drift":    self.lambda_drift,
            "gamma_stability": self.gamma_stability,
            "epsilon":         self.epsilon,
            "stable":          self._ctrl.is_stable(),
        }


# =============================================================================
# BundleBuilder — wrapper estático sobre ForensicBundle para pipeline.py
# pipeline.py llama BundleBuilder.seal(bundle, ...) como método de clase.
# =============================================================================

class BundleBuilder:
    """
    Wrapper de clase estática sobre ForensicBundle.
    Permite que pipeline.py use BundleBuilder.seal(bundle, ...) sin instanciar.
    """

    @staticmethod
    def seal(
        bundle: "ForensicBundle",
        engine_attestation_hash: str = "",
        ecl_hash: str = "",
    ) -> dict:
        """
        Sella el bundle y retorna el dict canónico listo para verificación.
        Delega en ForensicBundle.seal() que ya implementa el hash chain EBS v1.
        """
        sealed_bundle = bundle.seal(
            engine_attestation_hash=engine_attestation_hash,
            ecl_hash=ecl_hash,
        )
        return sealed_bundle.to_dict()

    @staticmethod
    def quick_verify(sealed_dict: dict) -> tuple:
        """
        Verificación rápida de integridad sobre un dict ya sellado.
        Reconstruye ForensicBundle desde dict y llama quick_verify().
        """
        bundle_hash = sealed_dict.get("bundle_hash", "")
        if not bundle_hash:
            return False, "bundle_hash ausente"
        # Verificación mínima: recomputar hash sobre payload
        import hashlib as _hl, json as _json
        payload = {k: v for k, v in sealed_dict.items()
                   if k not in ("bundle_hash", "integrity")}
        try:
            canonical = _json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
            computed = _hl.sha256(canonical.encode("utf-8")).hexdigest()
        except Exception as e:
            return False, f"Error al recomputar hash: {e}"
        if computed == bundle_hash:
            return True, "OK — bundle_hash verificado"
        return False, f"HASH MISMATCH: esperado={bundle_hash[:16]}… calculado={computed[:16]}…"

    @staticmethod
    def save(sealed_dict: dict, path: str) -> str:
        """
        Guarda el dict sellado en disco. Retorna hash del archivo.

        L-023 (Q4): atómico vía atomic_io + hash re-leído de disco y verificado
        contra memoria — mismo contrato que vigia/core/bundle_builder.py.save.
        """
        import hashlib as _hl, json as _json
        from vigia.core.atomic_io import atomic_write_text
        content = _json.dumps(sealed_dict, sort_keys=True, indent=2, default=str)
        mem_hash = _hl.sha256(content.encode("utf-8")).hexdigest()
        atomic_write_text(path, content)
        with open(path, "rb") as f:
            disk_hash = _hl.sha256(f.read()).hexdigest()
        if disk_hash != mem_hash:
            raise RuntimeError(
                f"L-023: hash en disco difiere del hash en memoria tras la "
                f"escritura atómica ({disk_hash[:16]} != {mem_hash[:16]}) — "
                f"posible corrupción de filesystem o tampering concurrente."
            )
        return disk_hash
