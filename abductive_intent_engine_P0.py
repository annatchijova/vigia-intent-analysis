"""
vigia/engine/abductive_intent_engine.py — HITO 2.1

MOTOR DE INFERENCIA ABDUCTIVA CON OCKHAM'S RAZOR

Fundamento:
  Peirce: Abducción es la sugerencia de una hipótesis que explica lo observado.
  Ockham: La hipótesis con menos supuestos no observados es más probable.
  
Principio VIGÍA:
  Primeridad (datos) → Segundidad (correlaciones) → Terceridad (ley/hábito)
  
  "¿Qué hábito del atacante explica MEJOR esta cadena de artefactos?"
  → La hipótesis con MENOR costo Ockham (menos supuestos)
  → Determinista: mismo input → misma hipótesis ganadora

GARANTÍA DAUBERT:
  - Costo Ockham = conteo entero (no float)
  - Cobertura = porcentaje entero (no float)
  - Rationale es auditablemente legible
  - Tablas de templates son explícitas (no lógica condicional oculta)

ARQUITECTURA:
  Artifact (Primeridad)
    → AbductiveIntentEngine._score_hypothesis()
    → AbductiveHypothesis (Terceridad)
    → AbductiveResult (hipótesis ganadora + alternatives)
    → PICERLMapper (mapea a PICERL-I)

────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

# Importar desde módulos P0 existentes
from visible_variables_P0 import VariableCategory, IRPhase


# ============================================================================
# MODELOS DE DATOS (Primeridad, Segundidad, Terceridad)
# ============================================================================

@dataclass
class Artifact:
    """
    Artefacto forense de Primeridad (dato bruto observado).
    
    En Peirce: el signo en su forma más cruda.
    En IR: un observable del sistema (timestamp, proceso, flujo de red, etc.)
    """
    
    artifact_id: str                    # "A001", "A002"
    category: VariableCategory          # temporal, process, network, persistence, auth, data, evasion, ioc
    name: str                           # "timestamp_uniformity", "registry_modification"
    value: Any                          # valor observado (bool, int, list, dict)
    observed_at: str                    # ISO 8601 timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "category": self.category.value,
            "name": self.name,
            "value": str(self.value),
            "observed_at": self.observed_at,
        }


@dataclass
class AbductiveHypothesis:
    """
    Hipótesis explicativa de Terceridad.
    
    Responde: "¿Qué hábito/ley del atacante explica esta cadena de artefactos?"
    
    Ockham's Razor aplicado:
    - cost = número de supuestos no observados
    - coverage_score = qué tan bien se ajusta a los datos
    
    Menor cost + mayor coverage = hipótesis ganadora
    """
    
    hypothesis_id: str                  # "H_DE_001", "H_PE_002"
    intent_type: str                    # "log_fabrication", "persistence", "lateral_movement"
    phase: IRPhase                      # fase IR a la que aplica
    
    # Artefactos que REQUIERE observar esta hipótesis
    required_artifacts: List[str]       # ["timestamp_uniformity", "process_memory_contradiction"]
    
    # Artefactos que SUPONE pero NO observó (costo Ockham)
    assumed_artifacts: List[str]        # ["attacker_has_rootkit", "exfiltration_occurred"]
    
    # COSTO OCKHAM: número de supuestos no observados (ENTERO, no float)
    # cost = len(missing_required) + len(assumed_artifacts)
    cost: int                           # [0, N] — menor es mejor
    
    # COBERTURA: qué porcentaje de lo requerido observamos (ENTERO, no float)
    # coverage = (observed_required / required_artifacts) * 100
    coverage_score: int                 # [0, 100] — mayor es mejor
    
    # Narrativa explicativa (para el reporte)
    explanation: str
    
    # Crítico para Daubert: cómo refutar esta hipótesis
    what_would_falsify: str
    
    # Reglas que justifican (tabla, no heurística)
    supporting_rules: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "intent_type": self.intent_type,
            "phase": self.phase.value,
            "required_artifacts": self.required_artifacts,
            "assumed_artifacts": self.assumed_artifacts,
            "cost": self.cost,  # ENTERO
            "coverage_score": self.coverage_score,  # ENTERO
            "explanation": self.explanation,
            "what_would_falsify": self.what_would_falsify,
            "supporting_rules": self.supporting_rules,
        }


@dataclass
class AbductiveResult:
    """
    Salida del motor: hipótesis ganadora + runners-up (ordenadas por Ockham).
    
    El winner es la hipótesis con:
    1. Menor cost (menos supuestos)
    2. Mayor coverage_score (mejor ajuste a datos)
    """
    
    winner: AbductiveHypothesis
    alternatives: List[AbductiveHypothesis]  # ordenadas por costo ascendente
    ockham_rationale: str                     # explicación de la elección
    result_hash: str = ""                     # SHA256 reproducible
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "winner": self.winner.to_dict(),
            "alternatives": [h.to_dict() for h in self.alternatives],
            "ockham_rationale": self.ockham_rationale,
            "result_hash": self.result_hash,
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ============================================================================
# TABLAS DE HIPÓTESIS TEMPLATES (DETERMINÍSTICAS, AUDITABLES)
# ============================================================================

HYPOTHESIS_TEMPLATES: Dict[IRPhase, List[AbductiveHypothesis]] = {
    
    # ========================================================================
    # FASE: DEFENSE_EVASION
    # ========================================================================
    IRPhase.DEFENSE_EVASION: [
        AbductiveHypothesis(
            hypothesis_id="H_DE_001",
            intent_type="log_fabrication",
            phase=IRPhase.DEFENSE_EVASION,
            required_artifacts=[
                "timestamp_uniformity",
                "process_memory_contradiction",
                "log_gap_intervals",
            ],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante fabricó logs para simular actividad normal. "
                "Los intervalos son demasiado uniformes (naturaleza no es así) "
                "y ningún proceso en memoria los genera."
            ),
            what_would_falsify=(
                "Esta hipótesis es falsa si encontramos el proceso que genera "
                "los logs y sus timestamps tienen variabilidad natural "
                "(desviación estándar > 0.1s entre eventos)."
            ),
            supporting_rules=[
                "RULE_DE_001: Uniformidad temporal en logs de sistema = artificial",
                "RULE_DE_002: Proceso ausente en memoria = origen no-legítimo",
            ],
        ),
        
        AbductiveHypothesis(
            hypothesis_id="H_DE_002",
            intent_type="log_deletion_after_exfil",
            phase=IRPhase.DEFENSE_EVASION,
            required_artifacts=[
                "log_deletion",
                "event_log_clearing",
            ],
            assumed_artifacts=[
                "exfiltration_occurred",
                "attacker_wants_stealth",
            ],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante borró logs DESPUÉS de exfiltrar datos. "
                "La eliminación es post-hoc, no preventiva."
            ),
            what_would_falsify=(
                "Falsa si no hay evidencia de transferencia de datos "
                "(network flows, data volume anomaly) en las 24h previas."
            ),
            supporting_rules=[
                "RULE_DE_003: Log deletion + data transfer previo = cover-up post-exfil",
            ],
        ),
        
        AbductiveHypothesis(
            hypothesis_id="H_DE_003",
            intent_type="anti_forensics_preparation",
            phase=IRPhase.DEFENSE_EVASION,
            required_artifacts=[
                "artifact_overwrite",
                "file_timestamp_modification",
            ],
            assumed_artifacts=[
                "attacker_has_advanced_tools",
                "attacker_expects_investigation",
            ],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante preparó anti-forensics ANTES de actuar. "
                "Manipuló timestamps y sobrescribió artefactos conocidos. "
                "Requiere conocimiento de herramientas forenses."
            ),
            what_would_falsify=(
                "Falsa si las herramientas de anti-forensics no están presentes "
                "en el sistema (no hay binarios de CCleaner, BCWipe, etc.)"
            ),
            supporting_rules=[
                "RULE_DE_004: Timestamp manipulation = anti-forensics avanzado",
            ],
        ),
    ],
    
    # ========================================================================
    # FASE: PERSISTENCE
    # ========================================================================
    IRPhase.PERSISTENCE: [
        AbductiveHypothesis(
            hypothesis_id="H_PE_001",
            intent_type="single_persistence",
            phase=IRPhase.PERSISTENCE,
            required_artifacts=[
                "registry_modifications",
            ],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante instaló un único mecanismo de persistencia vía registry. "
                "Mínima huella, máxima simplicidad."
            ),
            what_would_falsify=(
                "Falsa si no hay modificaciones de registry en los últimos 7 días "
                "o si las modificaciones son de software legítimo (firma válida)."
            ),
            supporting_rules=[
                "RULE_PE_001: Registry Run key = persistencia básica",
            ],
        ),
        
        AbductiveHypothesis(
            hypothesis_id="H_PE_002",
            intent_type="multi_mechanism_persistence",
            phase=IRPhase.PERSISTENCE,
            required_artifacts=[
                "registry_modifications",
                "scheduled_task_creation",
                "service_installation",
            ],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante instaló múltiples mecanismos de persistencia "
                "(registry + scheduled task + service). "
                "Redundancia sin supuestos extra — todo está en los datos."
            ),
            what_would_falsify=(
                "Falsa si los 3 artefactos no fueron creados por el mismo "
                "proceso/parent PID en una ventana temporal coherente (< 1 hora)."
            ),
            supporting_rules=[
                "RULE_PE_002: Múltiples persistencias con mismo origen = intencionalidad",
            ],
        ),
        
        AbductiveHypothesis(
            hypothesis_id="H_PE_003",
            intent_type="redundant_persistence",
            phase=IRPhase.PERSISTENCE,
            required_artifacts=[
                "registry_modifications",
                "scheduled_task_creation",
                "service_installation",
            ],
            assumed_artifacts=[
                "attacker_expects_detection",
                "attacker_wants_high_availability",
            ],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante instaló múltiples mecanismos de persistencia. "
                "Solo se explica si anticipa que algunos serán detectados/eliminados. "
                "Requiere suponer intención defensiva del atacante."
            ),
            what_would_falsify=(
                "Falsa si el sistema es un sandbox/entorno de prueba donde "
                "la redundancia es configuración normal del admin."
            ),
            supporting_rules=[
                "RULE_PE_003: >2 persistencias = expectativa de detección",
            ],
        ),
    ],
    
    # ========================================================================
    # FASE: LATERAL_MOVEMENT
    # ========================================================================
    IRPhase.LATERAL_MOVEMENT: [
        AbductiveHypothesis(
            hypothesis_id="H_LM_001",
            intent_type="pass_the_hash",
            phase=IRPhase.LATERAL_MOVEMENT,
            required_artifacts=[
                "lateral_movement_auth",
                "ticket_usage_from_different_ip",
            ],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante reutilizó hash de credencial para moverse lateralmente. "
                "Autenticación válida desde IP no asociada al usuario."
            ),
            what_would_falsify=(
                "Falsa si el usuario tiene registro de VPN/rotación de IP "
                "legítima en el período."
            ),
            supporting_rules=[
                "RULE_LM_001: Auth desde IP nueva + ticket reutilizado = PtH",
            ],
        ),
    ],
    
    # ========================================================================
    # FASE: EXFILTRATION
    # ========================================================================
    IRPhase.EXFILTRATION: [
        AbductiveHypothesis(
            hypothesis_id="H_EX_001",
            intent_type="bulk_data_exfiltration",
            phase=IRPhase.EXFILTRATION,
            required_artifacts=[
                "outbound_data_transfer",
                "data_volume",
            ],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante exfiltró volumen masivo de datos. "
                "Máxima cobertura, mínimos supuestos."
            ),
            what_would_falsify=(
                "Falsa si la transferencia es backup automatizado "
                "con política de retención documentada."
            ),
            supporting_rules=[
                "RULE_EX_001: Volumen + outbound = exfiltración intencional",
            ],
        ),
    ],
}


# ============================================================================
# MOTOR DE INFERENCIA ABDUCTIVA
# ============================================================================

class AbductiveIntentEngine:
    """
    Motor de inferencia abductiva con Ockham's Razor operacionalizado.
    
    PRINCIPIO: Dadas N hipótesis candidatas para una fase de IR,
    elegir la que requiera menos supuestos no observados (menor cost Ockham).
    
    DETERMINISMO: Mismo input → misma hipótesis ganadora (bit-a-bit reproducible).
    
    GARANTÍA DAUBERT: Costo y cobertura son enteros (no float opaco).
    """
    
    def __init__(
        self,
        templates: Optional[Dict[IRPhase, List[AbductiveHypothesis]]] = None,
        verbose: bool = False,
    ):
        """
        Args:
            templates: Diccionario de hipótesis por fase (default: HYPOTHESIS_TEMPLATES)
            verbose: Logging detallado
        """
        self.templates = templates or HYPOTHESIS_TEMPLATES
        self.verbose = verbose
    
    def infer_habit(
        self,
        artifacts: List[Artifact],
        phase: IRPhase,
    ) -> AbductiveResult:
        """
        Abduce la intención del atacante desde una cadena de artefactos.
        
        Algoritmo:
        1. Cargar templates (hipótesis candidatas) para esta fase
        2. Para cada candidata, calcular cost y coverage (ENTEROS)
        3. Ordenar por cost ascendente, luego coverage descendente
        4. La primera es la ganadora (Ockham)
        5. Construir rationale explicando por qué
        
        Args:
            artifacts: Cadena de artefactos forenses observados (Primeridad)
            phase: Fase de IR detectada por VisibleVariablesEngine
        
        Returns:
            AbductiveResult con hipótesis ganadora + alternativas descartadas
        """
        if self.verbose:
            print(f"\n[AbductiveIntentEngine] Inferring habit for phase={phase.value}")
        
        # Cargar templates para esta fase
        candidates = self.templates.get(phase, [])
        
        if not candidates:
            if self.verbose:
                print(f"[AbductiveIntentEngine] ✗ No templates for {phase.value}")
            return self._empty_result(phase)
        
        # Observados: names de artefactos presentes
        observed_names = {a.name for a in artifacts}
        if self.verbose:
            print(f"[AbductiveIntentEngine] Observed artifacts: {observed_names}")
        
        # Puntuación de cada candidata
        scored = []
        for template in candidates:
            hypothesis = self._score_hypothesis(template, observed_names)
            scored.append(hypothesis)
            if self.verbose:
                print(f"  {hypothesis.hypothesis_id}: cost={hypothesis.cost}, "
                      f"coverage={hypothesis.coverage_score}%")
        
        # Ordenar: primero por cost (menor), luego por coverage (mayor)
        scored.sort(key=lambda h: (h.cost, -h.coverage_score))
        
        # Ganadora
        winner = scored[0]
        
        # Rationale Ockham
        rationale = self._build_ockham_rationale(winner, scored[1:5] if len(scored) > 1 else [])
        
        # Hash reproducible
        result_dict = {
            "winner": winner.hypothesis_id,
            "cost": winner.cost,
            "coverage": winner.coverage_score,
            "phase": phase.value,
        }
        result_hash = hashlib.sha256(
            json.dumps(result_dict, sort_keys=True).encode()
        ).hexdigest()
        
        if self.verbose:
            print(f"[AbductiveIntentEngine] ✓ WINNER: {winner.hypothesis_id}")
            print(f"[AbductiveIntentEngine] Rationale:\n{rationale}")
        
        return AbductiveResult(
            winner=winner,
            alternatives=scored[1:],
            ockham_rationale=rationale,
            result_hash=result_hash,
        )
    
    def _score_hypothesis(
        self,
        template: AbductiveHypothesis,
        observed_names: set,
    ) -> AbductiveHypothesis:
        """
        Calcula cost y coverage para una hipótesis dada artefactos observados.
        
        DETERMINÍSTICO: mismo input → mismos scores siempre (aritmética entera).
        """
        # Artefactos requeridos que SÍ observamos
        observed_required = [
            req for req in template.required_artifacts
            if req in observed_names
        ]
        
        # Artefactos requeridos que NO observamos → COSTO
        missing_required = [
            req for req in template.required_artifacts
            if req not in observed_names
        ]
        
        # COBERTURA (ENTERO): qué porcentaje observamos de lo requerido
        total_required = len(template.required_artifacts)
        if total_required > 0:
            coverage = (len(observed_required) * 100) // total_required
        else:
            coverage = 100
        
        # COSTO OCKHAM (ENTERO): supuestos no observados
        cost = len(missing_required) + len(template.assumed_artifacts)
        
        return AbductiveHypothesis(
            hypothesis_id=template.hypothesis_id,
            intent_type=template.intent_type,
            phase=template.phase,
            required_artifacts=template.required_artifacts,
            assumed_artifacts=missing_required + template.assumed_artifacts,
            cost=cost,
            coverage_score=coverage,
            explanation=template.explanation,
            what_would_falsify=template.what_would_falsify,
            supporting_rules=template.supporting_rules + [
                f"OBSERVED: {len(observed_required)}/{total_required}",
                f"MISSING: {len(missing_required)}",
                f"EXPLICIT_ASSUMPTIONS: {len(template.assumed_artifacts)}",
            ],
        )
    
    def _build_ockham_rationale(
        self,
        winner: AbductiveHypothesis,
        runners_up: List[AbductiveHypothesis],
    ) -> str:
        """Construye la justificación de por qué Ockham eligió esta hipótesis."""
        rationale = (
            f"GANADORA: {winner.hypothesis_id}\n"
            f"  Costo Ockham: {winner.cost} supuestos\n"
            f"  Cobertura: {winner.coverage_score}% de datos requeridos\n"
            f"  Explicación: {winner.explanation}\n\n"
        )
        
        if runners_up:
            rationale += "DESCARTADAS:\n"
            for runner in runners_up[:3]:
                extra_cost = runner.cost - winner.cost
                rationale += (
                    f"  {runner.hypothesis_id}: costo={runner.cost} "
                    f"(+{extra_cost} supuestos extra), "
                    f"cobertura={runner.coverage_score}%\n"
                )
        
        return rationale
    
    def _empty_result(self, phase: IRPhase) -> AbductiveResult:
        """Resultado vacío cuando no hay templates para la fase."""
        return AbductiveResult(
            winner=AbductiveHypothesis(
                hypothesis_id="NO_HYPOTHESIS",
                intent_type="unknown",
                phase=phase,
                required_artifacts=[],
                assumed_artifacts=[],
                cost=999,
                coverage_score=0,
                explanation="No hay templates definidos para esta fase.",
                what_would_falsify="N/A — no hay hipótesis que falsificar.",
                supporting_rules=[],
            ),
            alternatives=[],
            ockham_rationale=f"No hay templates de hipótesis para {phase.value}.",
        )


# ============================================================================
# DEMO: case_002 (Log Fabrication)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("AbductiveIntentEngine — HITO 2.1 (Ockham's Razor)")
    print("=" * 80)
    
    # Artefactos observados en case_002
    artifacts = [
        Artifact(
            "A001",
            VariableCategory.TEMPORAL,
            "timestamp_uniformity",
            True,
            "2026-04-24T10:00:00Z"
        ),
        Artifact(
            "A002",
            VariableCategory.PROCESS,
            "process_memory_contradiction",
            True,
            "2026-04-24T10:00:00Z"
        ),
        Artifact(
            "A003",
            VariableCategory.TEMPORAL,
            "log_gap_intervals",
            [2000, 2000, 2000],
            "2026-04-24T10:00:00Z"
        ),
    ]
    
    # Motor
    engine = AbductiveIntentEngine(verbose=True)
    result = engine.infer_habit(artifacts, IRPhase.DEFENSE_EVASION)
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL (JSON Daubert-auditable)")
    print("=" * 80)
    print(result.to_json())
    
    print("\n" + "=" * 80)
    print("VERIFICACIÓN: Determinismo Bit-a-Bit")
    print("=" * 80)
    result2 = engine.infer_habit(artifacts, IRPhase.DEFENSE_EVASION)
    print(f"Hash ejecución 1: {result.result_hash}")
    print(f"Hash ejecución 2: {result2.result_hash}")
    print(f"¿Idénticos? {result.result_hash == result2.result_hash}")
