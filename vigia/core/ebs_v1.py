# Copyright 2026 Anna Tchijova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
vigia/models/ebs_v1.py
─────────────────────────────────────────────────────────────────────────────
Evidence Bundle Specification v1.0 — Pure Data Models

ARCHITECTURE: Layer 0 — Data & Contracts (IMMUTABLE)

ABSOLUTE RULE: This module contains DATA ONLY.
    - No business logic
    - No hashing
    - No sealing
    - No references to LLMs, Ollama, or narrative backends
    - No imports from higher layers

Cryptographic sealing lives in forensics/bundle_builder.py.
LLM narrative lives in pipeline.py as an external post-processor.

RATIONALE (Gemini + DeepSeek auditors):
    A bundle that hashes itself allows a compromised engine to seal its own
    lie. Sealing must be an external attestation process, independent of the
    inference engine that produced the data.

    SystemState is pure mathematics. Contaminating it with non-deterministic
    infrastructure variables (LLM model) makes the hash challengeable under
    Daubert: changing the narrative model must not change the evidence.

INVARIANTS:
    I1 Determinism:          same input -> same bundle
    I2 Chained integrity:    bundle_hash covers ALL content
    I3 Verifiable policy:    policy_spec independent of runtime
    I4 Explicit actions:     no implicit side effects
    I5 Explainable decision: risk and posterior ALWAYS present

COMPATIBILITY:
    Python 3.10+
    Pydantic v2 preferred, stdlib dataclasses fallback
    No external dependencies in fallback path
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
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
# Standard constants
# NOTE: verify_ebs_v1.py replicates these locally — it does not import from here.
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
        Canonical output of a forensic tool.
        z_score = (value - baseline_mean) / baseline_MAD
        Computed deterministically. The LLM never participates.
        """
        tool_name: str
        signal_id: str = Field(default_factory=_new_uuid)
        value: float
        z_score: float
        confidence: float = Field(default=1.0, ge=0.0, le=1.0)
        metadata: Optional[Dict[str, Any]] = None
        description: Optional[str] = None

        @field_validator("value", "z_score")
        @classmethod
        def _must_be_finite(cls, v: float) -> float:
            # B-083: fail-closed como signal_contract. Antes, min() con NaN
            # retornaba Z_CLIP_MAX (nan < x es False) → un z_score corrupto
            # entraba en silencio como señal CRÍTICA z=5.0.
            if not math.isfinite(v):
                raise ValueError(f"SignalOutput requiere valores finitos; recibido: {v}")
            return float(v)

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
        description: Optional[str] = None

        def __post_init__(self) -> None:
            # B-083: fail-closed como signal_contract (ver validador Pydantic).
            for _fname in ("value", "z_score"):
                _v = float(getattr(self, _fname))
                if not math.isfinite(_v):
                    raise ValueError(
                        f"SignalOutput requiere valores finitos; recibido {_fname}={_v}"
                    )
            self.z_score = max(-Z_CLIP_MAX, min(Z_CLIP_MAX, float(self.z_score)))
            self.confidence = max(0.0, min(1.0, float(self.confidence)))

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# EvidenceEdge and EvidenceGraph
# ===========================================================================

if _USE_PYDANTIC:
    class EvidenceEdge(BaseModel):
        """
        Evidence graph edge with bootstrap stability.
        pi_ij = freq(edge ij across B=500 resampling rounds).
        Forensic interpretation: statistically robust relationship, not a point correlation.
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
        Dependency graph between forensic signals.
        Produced by GraphStabilityEngine.
        graph_hash is assigned externally by bundle_builder.py.
        """
        nodes: List[str]
        edges: List[EvidenceEdge]
        bootstrap_rounds: int = 500
        stability_threshold: float = STABILITY_THRESHOLD_FORENSIC
        graph_hash: str = ""
        generated_at: str = Field(default_factory=_now_iso)

        def global_stability(self) -> float:
            """
            Global stability PENALIZED by graph fragmentation.

            CRITICAL FIX (Gemini):
            If the graph is fragmented and only one strong edge remains, a naive
            mean would report 0.9, misleading the RiskBoundedLayer.

            Correct formula:
                S = mean(pi_stable) * (n_stable_edges / n_possible_edges)

            If the graph is fractured, S -> 0 -> risk explodes -> ABSTAIN.
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
            """Connected components of the stable graph."""
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
        Output of the RiskBoundedDecisionLayer.
        All fields are 100% mathematical. No LLM or infrastructure references.
        ABSTAIN is a valid output — it signals an honest uncertainty zone.

        Forensic traceability fields (H18):
            reason_code    : machine-readable decision reason code.
                             ACCEPT_POSTERIOR | REJECT_POSTERIOR |
                             ABSTAIN_DRIFT | ABSTAIN_INSTABILITY |
                             ABSTAIN_INTENTION | ABSTAIN_ZONE
            abstain_reason : human-readable reason when decision == ABSTAIN.
            omega_intention: omega factor for abductive intention consistency.
                             Injected by AbductiveIntentEngine. [0,1]
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
        # H18: decision cause traceability
        reason_code: str = "UNKNOWN"
        abstain_reason: str = ""
        # Sovereign integration: omega factor for abductive intention
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
        # H18: decision cause traceability
        reason_code: str = "UNKNOWN"
        abstain_reason: str = ""
        # Sovereign integration
        omega_intention: float = 1.0
        consistency_score: float = 1.0

        def to_dict(self) -> Dict[str, Any]:
            return dict(vars(self))


# ===========================================================================
# PolicyRule and PolicySpec
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
        """Executed intervention. No implicit side effects (I4)."""
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
# SystemState — PURIFIED: mathematical parameters only, no LLM references
# ===========================================================================

if _USE_PYDANTIC:
    class SystemState(BaseModel):
        """
        Mathematical state of the system at sealing time.

        PURIFIED (DeepSeek + Gemini):
        No ollama_backend, no claude_code, no LLM references.
        If the narrative model changes, the bundle hash MUST NOT change.
        The narrative is an external post-processor — it is not part of the evidence.
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
        Chained SHA-256 hashes.
        Produced by bundle_builder.py — never by ForensicBundle itself.
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
# AbductionTrace — abductive reasoning traceability (PeircePlanner)
# ===========================================================================
# Records *why* the system prioritized certain signals over others.
# Semiotic trace: Firstness -> Secondness -> Thirdness.
# Lives in ForensicBundle.abduction_trace for expert witness audit.
# ===========================================================================

if _USE_PYDANTIC:
    class AbductionTrace(BaseModel):
        """
        Trace of the abductive reasoning that grounded signal prioritization.

        Peircean Semiotics applied to DFIR:
            Firstness  — raw signal observed (raw_signals_observed)
            Secondness — anomaly detected against baseline (anomalies_found)
            Thirdness  — attacker hypothesis/law emerging from correlation
                         (hypothesis + execution_plan_rationale)

        This object answers the expert witness question:
            "Why did the system prioritize ELA over CLIP?
             Why were heavy forensic tools aborted?
             Which signal triggered the REJECT?"

        RULE: AbductionTrace is readonly after sealing.
        BundleBuilder includes it in the bundle_hash.
        """
        # Firstness: what was available
        tools_available: List[str] = Field(default_factory=list)
        tools_executed: List[str] = Field(default_factory=list)
        tools_skipped: List[str] = Field(default_factory=list)

        # Secondness: which signals were anomalous
        dominant_signal: Optional[str] = None
        dominant_z_score: float = 0.0
        cluster_name: Optional[str] = None
        anomalies_found: List[Dict[str, Any]] = Field(default_factory=list)

        # Thirdness: the emerging hypothesis
        peirce_firstness: str = ""   # e.g. "SDA signal with z=3.2 detected"
        peirce_secondness: str = ""  # e.g. "Anomaly vs AUTHENTIC baseline"
        peirce_thirdness: str = ""   # e.g. "Pattern consistent with LLM fabrication"

        # ResourceOptimizer prioritization rationale
        execution_plan_rationale: List[Dict[str, Any]] = Field(default_factory=list)
        abort_reason: Optional[str] = None
        abort_triggered: bool = False

        # Traceability metadata
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
# ForensicBundle — PURE DATA STRUCTURE
# No seal(), no hashing, no quick_verify()
# Sealing is the exclusive responsibility of forensics/bundle_builder.py
# ===========================================================================

class ForensicBundle:
    """
    EBS v1 artifact — pure data container.

    REFACTORED: This object does NOT seal itself.
    Sealing is performed by forensics/bundle_builder.py as an external
    attestation process. This guarantees a compromised engine cannot seal
    its own lie.

    Correct flow:
        bundle = ForensicBundle(...)               # pure data
        sealed_dict = BundleBuilder.seal(bundle)   # external attestation
        BundleBuilder.save(sealed_dict, path)
        # => verify_ebs_v1.py path  (stdlib only, no production imports)
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
        # abduction_trace: traceability of abductive reasoning (PeircePlanner)
        # Answers the expert witness: "why were these signals prioritized"
        self.abduction_trace: Optional[AbductionTrace] = abduction_trace
        # integrity: assigned externally by BundleBuilder.seal()
        self.integrity: Optional[IntegrityBlock] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize bundle contents (without integrity — BundleBuilder appends it).

        Includes abduction_trace if present: it is part of the bundle_hash
        and allows the auditor to verify the complete abductive reasoning.
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
        # abduction_trace is optional — if present, it is included in bundle_hash (I2)
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
# Factory helpers
# ===========================================================================

def make_default_policy(
    epsilon: float = 0.05,
    lambda_drift: float = 2.0,
    gamma_stability: float = 2.0,
) -> PolicySpec:
    rules = [
        PolicyRule(variable="posterior", max_delta=0.10,
                   allowed_roles=["system", "analyst"],
                   description="Maximum allowed change in posterior probability"),
        PolicyRule(variable="drift", max_delta=0.15,
                   allowed_roles=["system"],
                   description="Maximum allowed drift correction"),
        PolicyRule(variable="graph_stability", max_delta=0.05,
                   allowed_roles=["system"], requires_approval=True,
                   description="Graph stability changes require explicit approval"),
        PolicyRule(variable="lambda_drift", max_delta=1.0,
                   allowed_roles=["system"],
                   description="Adaptive drift sensitivity adjustment"),
        PolicyRule(variable="gamma_stability", max_delta=1.0,
                   allowed_roles=["system"],
                   description="Adaptive structural sensitivity adjustment"),
    ]
    return PolicySpec(
        version="1.0", rules=rules,
        epsilon_accept=epsilon, epsilon_reject=epsilon,
        lambda_drift_init=lambda_drift, gamma_stability_init=gamma_stability,
        description="VIGIA default policy — SANS FIND EVIL 2026",
    )

# B-059 (TANDA 1, 2026-07-06): la escala ENFSI vive en un módulo único.
# Esta era la implementación canónica (la que se sella en el bundle) — se
# movió a vigia/core/enfsi.py con semántica bit-idéntica para LR finito.
# Re-export para compatibilidad: `from vigia.core.ebs_v1 import enfsi_label`
# sigue funcionando (likelihood_ratio.py y consumidores externos).
from vigia.core.enfsi import enfsi_label  # noqa: E402,F401
