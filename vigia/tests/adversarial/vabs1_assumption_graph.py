# vigia/tests/adversarial/vabs1_assumption_graph.py
#
# VIGÍA Adversarial Benchmark Suite v1 — Assumption Graph
# =========================================================
# Supuestos epistemológicos adicionales cubiertos por VABS-1.
# Complementa assumption_graph_nuevos.py (P3, S1-S10).
#
# Taxonomía:
#   VABS-T1  Epistemic collapse (observational equivalence)
#   VABS-T2  Causal graph manipulation
#   VABS-T3  Sensor dependency exploits
#   VABS-T4  Statistical invariance attacks
#   VABS-T5  Cross-layer semantic decoupling
#   VABS-T6  Temporal manipulation
#   VABS-T7  Baseline poisoning
#   VABS-T8  Fractal consistency
#
# INTEGRACION:
#   from .vabs1_assumption_graph import ASSUMPTION_GRAPH_VABS1, propagate_breaks_vabs1
#   from .assumption_graph_nuevos import ASSUMPTION_GRAPH_NUEVOS, propagate_breaks_nuevos
#
# Los IDs de dependencia que referencian supuestos de P3/base:
#   "pipeline_integrity", "causal_ordering", "sensor_independence",
#   "evidence_reliability", "anomaly_significance", "golden_rule_soundness",
#   "structural_malice", "log_completeness", "timestamp_comparability",
#   "memory_ground_truth"
#
# AUDITORIA: Claude (Anthropic), mayo 2026. Basado en analisis de
# ChatGPT (red team) y Kimi/Moonshot (auditoria epistemica).

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Set


@dataclass
class AssumptionVABS:
    name: str
    description: str
    vabs_category: str           # T1..T8
    gap_ids: List[str]           # GAP-NN del P2_SPEC
    dependencies: List[str] = field(default_factory=list)
    criticality: Fraction = Fraction(1, 2)
    recoverable: bool = True
    failure_mode: str = ""       # que rompe si se viola


# Criticality como Fraction — sin floats, Daubert-safe
ASSUMPTION_GRAPH_VABS1 = {

    # ── T1: Equivalencia observacional ────────────────────────────────────

    "world_distinguishability": AssumptionVABS(
        name="world_distinguishability",
        description=(
            "Two generative worlds (benign vs malicious) that produce identical "
            "artifact distributions are distinguishable by VIGIA. "
            "Violation: P(E|benign) == P(E|malicious) for all observable E."
        ),
        vabs_category="T1",
        gap_ids=["GAP-03"],
        dependencies=["pipeline_integrity", "evidence_reliability"],
        criticality=Fraction(19, 20),   # 0.95
        recoverable=False,
        failure_mode=(
            "LR collapses to 1.0; CAIE finds no fractures; "
            "system enters permanent ABSTAIN regardless of true label."
        ),
    ),

    "null_signal_epistemology": AssumptionVABS(
        name="null_signal_epistemology",
        description=(
            "VIGIA can only reason over observable artifacts. "
            "An adversary operating entirely outside the observable boundary "
            "produces no detectable signal — this is a hard epistemological limit, "
            "not a bug."
        ),
        vabs_category="T1",
        gap_ids=["GAP-03"],
        dependencies=["log_completeness"],
        criticality=Fraction(9, 10),    # 0.90
        recoverable=False,
        failure_mode=(
            "System MUST emit ABSTAIN_EPISTEMIC, not a false BENIGN/MALICE verdict. "
            "Violation: emitting a confident verdict when no signal exists."
        ),
    ),

    # ── T2: Causal graph manipulation ─────────────────────────────────────

    "node_identity_invariance": AssumptionVABS(
        name="node_identity_invariance",
        description=(
            "CAIE causal graph analysis depends on node label identity, not only "
            "on graph structure. Adversary can permute labels while preserving "
            "statistical structure, inverting semantic meaning without triggering "
            "structural detectors."
        ),
        vabs_category="T2",
        gap_ids=["GAP-06"],
        dependencies=["causal_ordering", "pipeline_integrity"],
        criticality=Fraction(17, 20),   # 0.85
        recoverable=True,
        failure_mode=(
            "CAIE accepts permuted causal graph as valid. "
            "Process A->B vs B->A structurally identical, semantically inverted."
        ),
    ),

    "post_hoc_causality_rejection": AssumptionVABS(
        name="post_hoc_causality_rejection",
        description=(
            "A configuration or log entry that appears AFTER an effect it is meant "
            "to explain cannot retroactively justify that effect. "
            "EFFECT_BEFORE_CAUSE must fire even when the cause appears post-hoc "
            "as a legitimately generated system artifact."
        ),
        vabs_category="T2",
        gap_ids=["GAP-06"],
        dependencies=["causal_ordering", "timestamp_comparability"],
        criticality=Fraction(9, 10),    # 0.90
        recoverable=True,
        failure_mode=(
            "Latent delayed causality attack succeeds: "
            "automatic system config appears 10 minutes after triggered event, "
            "EFFECT_BEFORE_CAUSE does not fire because cause timestamp > effect timestamp."
        ),
    ),

    # ── T3: Sensor dependency ──────────────────────────────────────────────

    "sensor_physical_independence": AssumptionVABS(
        name="sensor_physical_independence",
        description=(
            "Two distinct source_tool labels are assumed to represent physically "
            "independent sensors. A single physical sensor presenting under multiple "
            "tool names (after cert rotation, migration, or aliasing) inflates "
            "Noisy-OR independence assumptions."
        ),
        vabs_category="T3",
        gap_ids=[],   # No P2 GAP directly — new gap candidate
        dependencies=["sensor_independence"],
        criticality=Fraction(4, 5),     # 0.80
        recoverable=False,
        failure_mode=(
            "Noisy-OR double-counts single sensor. "
            "LR inflated by false independence. "
            "Composite score artificially strong."
        ),
    ),

    "shared_upstream_model_detection": AssumptionVABS(
        name="shared_upstream_model_detection",
        description=(
            "Sensors that are physically distinct may be logically correlated "
            "via a shared upstream decision model (compromised SIEM, shared "
            "detection ruleset). This induced correlation violates the "
            "independence assumption in Noisy-OR even when source_tool differs."
        ),
        vabs_category="T3",
        gap_ids=[],   # New gap candidate
        dependencies=["sensor_independence", "evidence_reliability"],
        criticality=Fraction(17, 20),   # 0.85
        recoverable=False,
        failure_mode=(
            "Multi-sensor consensus is fabricated via shared latent model. "
            "All sensors report correlated false positive in synchrony."
        ),
    ),

    # ── T4: Statistical invariance ────────────────────────────────────────

    "entropy_semantic_coupling": AssumptionVABS(
        name="entropy_semantic_coupling",
        description=(
            "Statistical invariants (global entropy, correlation matrix) are "
            "coupled to semantic meaning. An attacker that preserves entropy "
            "while inverting causal meaning defeats entropy-based detectors."
        ),
        vabs_category="T4",
        gap_ids=["GAP-01", "GAP-02"],
        dependencies=["pipeline_integrity"],
        criticality=Fraction(17, 20),   # 0.85
        recoverable=True,
        failure_mode=(
            "P2 metrics report normal entropy while causal structure is inverted. "
            "No CAIE fracture triggered."
        ),
    ),

    "lr_discriminative_power": AssumptionVABS(
        name="lr_discriminative_power",
        description=(
            "LR retains discriminative power when P(E|malicious) and P(E|benign) "
            "are intentionally engineered to be approximately equal. "
            "Adversarial equilibrium trap: attacker constructs evidence where "
            "both likelihoods converge."
        ),
        vabs_category="T4",
        gap_ids=["GAP-03"],
        dependencies=["evidence_reliability", "anomaly_significance"],
        criticality=Fraction(9, 10),    # 0.90
        recoverable=False,
        failure_mode=(
            "LR -> 1.0 always. System emits ABSTAIN permanently. "
            "Attacker achieves denial of forensic analysis."
        ),
    ),

    # ── T5: Cross-layer semantic decoupling ───────────────────────────────

    "global_constraint_solver_existence": AssumptionVABS(
        name="global_constraint_solver_existence",
        description=(
            "VIGIA can detect contradictions that only emerge at the intersection "
            "of multiple layers (logs + memory + network + audit). "
            "A per-layer consistent picture can be globally inconsistent. "
            "The system needs cross-layer constraint evaluation, not just "
            "pairwise artifact comparison."
        ),
        vabs_category="T5",
        gap_ids=["GAP-06"],
        dependencies=["pipeline_integrity", "evidence_reliability"],
        criticality=Fraction(9, 10),    # 0.90
        recoverable=True,
        failure_mode=(
            "DAG isolation assumption violated: "
            "each layer passes individual checks but global semantic "
            "contradiction is invisible to pairwise CAIE evaluation."
        ),
    ),

    # ── T6: Temporal manipulation ─────────────────────────────────────────

    "external_clock_anchor": AssumptionVABS(
        name="external_clock_anchor",
        description=(
            "Timestamp consistency is validated against an external reference clock, "
            "not only against internal cross-machine consistency. "
            "Synchronized clock drift across all machines is internally consistent "
            "but inconsistent with real elapsed time."
        ),
        vabs_category="T6",
        gap_ids=[],   # New gap candidate
        dependencies=["timestamp_comparability", "causal_ordering"],
        criticality=Fraction(3, 4),     # 0.75
        recoverable=True,
        failure_mode=(
            "Consistent clock drift attack succeeds: all machines coherent "
            "internally, inconsistency only observable against external NTP reference "
            "not available to VIGIA at analysis time."
        ),
    ),

    # ── T7: Baseline poisoning ────────────────────────────────────────────

    "baseline_ground_truth_immutability": AssumptionVABS(
        name="baseline_ground_truth_immutability",
        description=(
            "The historical baseline used for z-score and MAD computation "
            "reflects true ground truth and has not been gradually poisoned. "
            "Adaptive normalization (baseline_mean and MAD evolving with the attack) "
            "makes the attacker's behavior appear normal."
        ),
        vabs_category="T7",
        gap_ids=["GAP-03", "GAP-07"],
        dependencies=["evidence_reliability", "pipeline_integrity"],
        criticality=Fraction(9, 10),    # 0.90
        recoverable=False,
        failure_mode=(
            "z-score always approximately 0. "
            "Gradual drift normalization capture: attacks redefined as baseline. "
            "Circular detection: cannot detect drift using a drifted baseline."
        ),
    ),

    # ── T8: Fractal consistency ───────────────────────────────────────────

    "cross_scale_consistency_mapping": AssumptionVABS(
        name="cross_scale_consistency_mapping",
        description=(
            "Consistency at micro/meso/macro analysis scales implies "
            "a coherent cross-scale mapping. An attack can be consistent "
            "at every individual scale while the mapping between scales is undefined "
            "or contradictory."
        ),
        vabs_category="T8",
        gap_ids=["GAP-06"],
        dependencies=["pipeline_integrity", "evidence_reliability"],
        criticality=Fraction(17, 20),   # 0.85
        recoverable=True,
        failure_mode=(
            "CCS does not detect cross-scale contradiction. "
            "Noisy-OR does not see inter-group inconsistency. "
            "Scale-invariant attack passes all per-level checks."
        ),
    ),

    "absence_topology_evaluation": AssumptionVABS(
        name="absence_topology_evaluation",
        description=(
            "VIGIA evaluates the topological structure of correlated absences, "
            "not only individual absent signals. Three individually explicable "
            "absences can form a complete alternative causal structure that is "
            "only visible when their correlation topology is analyzed."
        ),
        vabs_category="T8",
        gap_ids=["GAP-03"],
        dependencies=["log_completeness", "causal_ordering"],
        criticality=Fraction(17, 20),   # 0.85
        recoverable=True,
        failure_mode=(
            "Balanced absence attack succeeds: no TIER-1 triggered because "
            "no individual absence is critical. "
            "Absence topology invisible to point-wise absence detection."
        ),
    ),
}


def propagate_breaks_vabs1(broken: Set[str]) -> Set[str]:
    """
    Propaga rupturas dentro del grafo VABS-1.
    Para propagacion cross-grafo (P3 + VABS-1) usar propagate_breaks_unified().
    """
    impacted = set(broken)
    changed = True
    while changed:
        changed = False
        for name, assumption in ASSUMPTION_GRAPH_VABS1.items():
            if name not in impacted:
                if any(dep in impacted for dep in assumption.dependencies):
                    impacted.add(name)
                    changed = True
    return impacted


def criticality_vabs1(broken: Set[str]) -> Fraction:
    """
    Devuelve criticidad total de los supuestos rotos como Fraction.
    Sin floats — Daubert-safe.
    """
    if not broken:
        return Fraction(0)
    numerator = sum(
        ASSUMPTION_GRAPH_VABS1[a].criticality
        for a in broken
        if a in ASSUMPTION_GRAPH_VABS1
    )
    denominator = sum(a.criticality for a in ASSUMPTION_GRAPH_VABS1.values())
    if denominator == 0:
        return Fraction(0)
    result = numerator / denominator
    # Clamp a [0, 1]
    return min(Fraction(1), result)


def propagate_breaks_unified(broken: Set[str]) -> Set[str]:
    """
    Propaga rupturas en el grafo unificado P3 + VABS-1.
    Importar ambos grafos para coverage completo.
    Uso:
        from .assumption_graph_nuevos import ASSUMPTION_GRAPH_NUEVOS
        from .vabs1_assumption_graph import ASSUMPTION_GRAPH_VABS1
        combined = {**ASSUMPTION_GRAPH_NUEVOS, **ASSUMPTION_GRAPH_VABS1}
    """
    # Importacion local para evitar dependencia circular en CI
    try:
        from .assumption_graph_nuevos import ASSUMPTION_GRAPH_NUEVOS
        combined = {**ASSUMPTION_GRAPH_NUEVOS}
    except ImportError:
        combined = {}
    combined.update(ASSUMPTION_GRAPH_VABS1)

    impacted = set(broken)
    changed = True
    while changed:
        changed = False
        for name, assumption in combined.items():
            if name not in impacted:
                if any(dep in impacted for dep in assumption.dependencies):
                    impacted.add(name)
                    changed = True
    return impacted
