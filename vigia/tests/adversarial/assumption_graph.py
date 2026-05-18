# vigia/tests/adversarial/assumption_graph.py

from dataclasses import dataclass, field
from typing import Optional, Set, List


@dataclass
class Assumption:
    """Un supuesto epistemológico del sistema"""
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    criticality: float = 0.5  # 0.0 = bajo, 1.0 = crítico
    recoverable: bool = True   # ¿El sistema puede detectar la ruptura?


# ASSUMPTION GRAPH - 15 nodos (cubre CAIE v2.0)
ASSUMPTION_GRAPH = {
    # Nivel 1: Supuestos base (no dependen de otros)
    "timestamp_comparability": Assumption(
        name="timestamp_comparability",
        description="Todos los timestamps son comparables (misma zona horaria, sin drift)",
        dependencies=[],
        criticality=0.9,
        recoverable=False,  # CAIE no detecta drift suave
    ),
    "sensor_independence": Assumption(
        name="sensor_independence",
        description="Diferentes sensores producen evidencia independiente",
        dependencies=[],
        criticality=0.8,
        recoverable=True,   # CAIE puede detectar por source_tool agrupamiento parcial
    ),
    "pipeline_integrity": Assumption(
        name="pipeline_integrity",
        description="La cadena de adquisición no está comprometida",
        dependencies=[],
        criticality=0.95,
        recoverable=False,  # Sin TPM/hardware anchor, no se detecta
    ),
    "memory_ground_truth": Assumption(
        name="memory_ground_truth",
        description="Memory artifacts reflejan el estado real del sistema en el momento",
        dependencies=[],
        criticality=0.85,
        recoverable=False,  # Sampling gaps no detectables
    ),
    "filesystem_monotonicity": Assumption(
        name="filesystem_monotonicity",
        description="MFT/USN son monotónicos y no manipulables user-space",
        dependencies=[],
        criticality=0.8,
        recoverable=True,   # MFT_ENTRY_ANOMALY detecta violaciones
    ),
    "log_completeness": Assumption(
        name="log_completeness",
        description="Los logs son eventos completos, no muestreados",
        dependencies=[],
        criticality=0.7,
        recoverable=False,  # No hay forma de saber si un log faltante es sampling o borrado
    ),
    
    # Nivel 2: Supuestos derivados (dependen de otros)
    "causal_ordering": Assumption(
        name="causal_ordering",
        description="El orden temporal de eventos refleja causalidad real",
        dependencies=["timestamp_comparability"],
        criticality=0.9,
        recoverable=False,
    ),
    "coverage_validity": Assumption(
        name="coverage_validity",
        description="La cobertura observada es representativa del espacio de ataque",
        dependencies=["sensor_independence", "pipeline_integrity"],
        criticality=0.75,
        recoverable=False,
    ),
    "evidence_reliability": Assumption(
        name="evidence_reliability",
        description="La confianza en la evidencia es función solo de spoofability",
        dependencies=["pipeline_integrity", "memory_ground_truth"],
        criticality=0.7,
        recoverable=False,
    ),
    "anomaly_significance": Assumption(
        name="anomaly_significance",
        description="Las anomalías detectadas son indicadores de malicia, no de ruido",
        dependencies=["causal_ordering", "coverage_validity"],
        criticality=0.65,
        recoverable=False,
    ),
    "noisy_or_validity": Assumption(
        name="noisy_or_validity",
        description="El modelo Noisy-OR de fusión de evidencia es válido",
        dependencies=["sensor_independence"],
        criticality=0.6,
        recoverable=False,
    ),
    
    # Nivel 3: Supuestos estructurales (alta dependencia)
    "structural_malice": Assumption(
        name="structural_malice",
        description="Inconsistencia estructural implica malicia adversarial",
        dependencies=["causal_ordering", "evidence_reliability"],
        criticality=0.9,
        recoverable=False,
    ),
    "absence_meaning": Assumption(
        name="absence_meaning",
        description="Ausencia de evidencia con alta cobertura implica ausencia de ataque",
        dependencies=["coverage_validity", "log_completeness"],
        criticality=0.8,
        recoverable=False,
    ),
    "golden_rule_soundness": Assumption(
        name="golden_rule_soundness",
        description="Las Golden Rules son suficientes y necesarias para MALICE",
        dependencies=["causal_ordering", "filesystem_monotonicity", "memory_ground_truth"],
        criticality=0.85,
        recoverable=False,
    ),
    "daubert_defensibility": Assumption(
        name="daubert_defensibility",
        description="El sistema produce evidencia admisible bajo Daubert",
        dependencies=["evidence_reliability", "structural_malice"],
        criticality=0.9,
        recoverable=True,  # El daubert_note documenta límites
    ),
}


def propagate_breaks(broken_assumptions: Set[str]) -> Set[str]:
    """
    Propaga rupturas a través del grafo de dependencias.
    
    Si A depende de B, y B está roto, entonces A está implícitamente roto.
    """
    impacted = set(broken_assumptions)
    changed = True
    
    while changed:
        changed = False
        for name, assumption in ASSUMPTION_GRAPH.items():
            if name not in impacted:
                # Si alguna dependencia está en impacted, este supuesto se rompe
                if any(dep in impacted for dep in assumption.dependencies):
                    impacted.add(name)
                    changed = True
    
    return impacted


def assumption_criticality_score(broken: Set[str]) -> float:
    """Calcula el impacto crítico de las rupturas (0.0 = bajo, 1.0 = catastrófico)"""
    if not broken:
        return 0.0
    
    total_criticality = sum(ASSUMPTION_GRAPH[a].criticality for a in broken)
    max_possible = sum(a.criticality for a in ASSUMPTION_GRAPH.values())
    
    return min(1.0, total_criticality / max_possible)
