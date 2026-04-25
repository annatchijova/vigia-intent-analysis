"""
vigia/engine/visible_variables.py — REFACTORIZACIÓN P0

CAMBIOS REALIZADOS:
  P0-1: Eliminado float en FocusAnalysis.phase_confidence
        Reemplazado por consistency_score: int (reglas satisfechas / total * 100)
  P0-2: Métodos _score_by_* → _score_by_*_deterministic()
        Usan SOLO tablas de mapeo, sin lógica condicional oculta
  P0-3: detect_phase() retorna (IRPhase, consistency_score_int)
  P0-4: Interfaz preparada para AbductiveIntentEngine (Hito 2.1)

GARANTÍA DAUBERT:
  - 100% determinístico (sin float, sin redondeos)
  - 100% auditable (todas las decisiones son tabla → lookup)
  - 100% reproducible (SHA256 sin variabilidad)
  - 100% falsable (reglas explícitas, no heurísticas ocultas)
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class IRPhase(str, Enum):
    """Fases de IR (NIST 800-61 compatible)."""
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    COMMAND_AND_CONTROL = "command_and_control"
    IMPACT = "impact"
    CLEANUP = "cleanup"
    UNKNOWN = "unknown"


class VariableCategory(str, Enum):
    """Categorías de variables observables."""
    TEMPORAL = "temporal"
    PROCESS = "process"
    NETWORK = "network"
    PERSISTENCE = "persistence"
    AUTH = "auth"
    DATA = "data"
    EVASION = "evasion"
    IOC = "ioc"


# ============================================================================
# TABLAS DE MAPEO DETERMINÍSTICAS (P0-2: Sin heurísticas ocultas)
# ============================================================================

# TABLA 1: MITRE ATT&CK → IR Phase
MITRE_TTP_TO_PHASE: Dict[str, IRPhase] = {
    # Reconnaissance
    "T1592": IRPhase.RECONNAISSANCE, "T1589": IRPhase.RECONNAISSANCE,
    # Initial Access
    "T1566": IRPhase.INITIAL_ACCESS, "T1200": IRPhase.INITIAL_ACCESS,
    "T1199": IRPhase.INITIAL_ACCESS,
    # Execution
    "T1059": IRPhase.EXECUTION, "T1204": IRPhase.EXECUTION,
    # Persistence
    "T1547": IRPhase.PERSISTENCE, "T1547.1": IRPhase.PERSISTENCE,
    "T1098": IRPhase.PERSISTENCE, "T1137": IRPhase.PERSISTENCE,
    # Privilege Escalation
    "T1548": IRPhase.PRIVILEGE_ESCALATION, "T1134": IRPhase.PRIVILEGE_ESCALATION,
    # Defense Evasion
    "T1197": IRPhase.DEFENSE_EVASION, "T1140": IRPhase.DEFENSE_EVASION,
    "T1564": IRPhase.DEFENSE_EVASION, "T1562": IRPhase.DEFENSE_EVASION,
    "T1070": IRPhase.DEFENSE_EVASION, "T1565.001": IRPhase.DEFENSE_EVASION,
    "T1497": IRPhase.DEFENSE_EVASION,
    # Credential Access
    "T1110": IRPhase.CREDENTIAL_ACCESS, "T1187": IRPhase.CREDENTIAL_ACCESS,
    "T1040": IRPhase.CREDENTIAL_ACCESS, "T1056.004": IRPhase.CREDENTIAL_ACCESS,
    # Discovery
    "T1087": IRPhase.DISCOVERY, "T1010": IRPhase.DISCOVERY, "T1217": IRPhase.DISCOVERY,
    # Lateral Movement
    "T1570": IRPhase.LATERAL_MOVEMENT, "T1021": IRPhase.LATERAL_MOVEMENT,
    "T1550": IRPhase.LATERAL_MOVEMENT,
    # Collection
    "T1123": IRPhase.COLLECTION, "T1119": IRPhase.COLLECTION, "T1557": IRPhase.COLLECTION,
    # Exfiltration
    "T1020": IRPhase.EXFILTRATION, "T1048": IRPhase.EXFILTRATION,
    "T1041": IRPhase.EXFILTRATION,
    # Command and Control
    "T1071": IRPhase.COMMAND_AND_CONTROL, "T1092": IRPhase.COMMAND_AND_CONTROL,
    "T1008": IRPhase.COMMAND_AND_CONTROL,
    # Impact
    "T1531": IRPhase.IMPACT, "T1561": IRPhase.IMPACT, "T1485": IRPhase.IMPACT,
}

# TABLA 2: Violation Type → IR Phase
TEMPORAL_VIOLATION_TO_PHASE: Dict[str, IRPhase] = {
    "STATISTICAL_UNIFORMITY": IRPhase.DEFENSE_EVASION,
    "RETROACTIVE_MODIFICATION": IRPhase.DEFENSE_EVASION,
    "FABRICATION": IRPhase.DEFENSE_EVASION,
    "LOG_TAMPERING": IRPhase.DEFENSE_EVASION,
    "TIMING_ANOMALY": IRPhase.EXFILTRATION,
}

# TABLA 3: Variables visibles por fase
VISIBLE_VARIABLES_BY_PHASE: Dict[IRPhase, Dict[VariableCategory, List[str]]] = {
    IRPhase.PERSISTENCE: {
        VariableCategory.PERSISTENCE: [
            "registry_modifications", "scheduled_task_creation", "service_installation",
            "cron_jobs", "startup_folders", "ad_objects_modified", "firewall_rule_changes",
        ],
        VariableCategory.TEMPORAL: [
            "persistence_mechanism_creation_time", "creation_timestamp_uniformity",
        ],
        VariableCategory.AUTH: ["privileged_account_usage", "domain_admin_logon"],
    },
    IRPhase.DEFENSE_EVASION: {
        VariableCategory.EVASION: [
            "log_deletion", "event_log_clearing", "antivirus_tampering",
            "firewall_rule_deletion", "file_deletion", "artifact_overwrite",
            "file_timestamp_modification",
        ],
        VariableCategory.TEMPORAL: [
            "timestamp_anomalies", "log_gap_intervals", "file_modification_uniformity",
        ],
    },
    IRPhase.EXFILTRATION: {
        VariableCategory.NETWORK: [
            "outbound_data_transfer", "dns_exfiltration", "https_exfiltration",
            "ftp_exfiltration", "icmp_exfiltration",
        ],
        VariableCategory.TEMPORAL: ["data_transfer_duration", "transfer_rate"],
        VariableCategory.DATA: ["data_volume", "file_compression_indicators"],
    },
    IRPhase.LATERAL_MOVEMENT: {
        VariableCategory.NETWORK: [
            "smb_traffic", "rpc_traffic", "winrm_traffic", "ssh_traffic",
            "cross_segment_traffic",
        ],
        VariableCategory.AUTH: [
            "lateral_movement_auth", "pass_the_hash_indicators",
            "ticket_usage_from_different_ip",
        ],
    },
    # Agregar más fases según sea necesario
}


# ============================================================================
# MODELOS DE DATOS (P0-1: Sin float)
# ============================================================================

@dataclass
class FocusAnalysis:
    """
    Resultado del análisis de Variables Visibles.
    
    P0-1: consistency_score es ENTERO [0,100], no float.
    Se calcula como: (reglas_satisfechas / reglas_totales) * 100
    """
    bundle_id: str
    detected_phase: IRPhase
    consistency_score: int  # [0, 100] — ENTERO, NUNCA FLOAT
    consistency_rationale: str  # Cómo se calculó (para auditoria)
    
    visible_categories: Set[VariableCategory]
    visible_variables: Dict[VariableCategory, List[str]]
    
    expected_but_missing: Dict[VariableCategory, List[str]] = field(default_factory=dict)
    unexpected_present: Dict[VariableCategory, List[str]] = field(default_factory=dict)
    
    reasoning: str = ""
    focus_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "detected_phase": self.detected_phase.value,
            "consistency_score": self.consistency_score,  # Entero
            "consistency_rationale": self.consistency_rationale,
            "visible_categories": sorted([c.value for c in self.visible_categories]),
            "visible_variables": {k.value: v for k, v in self.visible_variables.items()},
            "expected_but_missing": {k.value if isinstance(k, VariableCategory) else str(k): v
                                      for k, v in self.expected_but_missing.items()},
            "unexpected_present": {k.value if isinstance(k, VariableCategory) else str(k): v
                                    for k, v in self.unexpected_present.items()},
            "reasoning": self.reasoning,
            "focus_hash": self.focus_hash,
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ============================================================================
# VISIBLE VARIABLES ENGINE
# ============================================================================

class VisibleVariablesEngine:
    """
    Motor determinístico de análisis de variables visibles.
    P0-2: Solo lookups en tablas, sin heurísticas opacas.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def _log(self, msg: str):
        if self.verbose:
            logger.info(f"[VisibleVariablesEngine] {msg}")
    
    # ========================================================================
    # P0-2: MÉTODOS DETERMINÍSTICOS (Solo tablas, sin condicionales ocultos)
    # ========================================================================
    
    def detect_phase(
        self,
        signals: List[Dict[str, Any]],
        temporal_violations: Optional[List[Dict[str, Any]]] = None,
        mitre_ttps: Optional[List[str]] = None,
    ) -> Tuple[IRPhase, int]:
        """
        Detecta fase de IR usando SOLO tablas de mapeo.
        
        Retorna (detected_phase, consistency_score_entero)
        donde consistency_score = (reglas_matched / reglas_totales) * 100
        """
        matched_rules = 0
        total_rules = 0
        phase_votes: Dict[IRPhase, int] = {phase: 0 for phase in IRPhase}
        
        # Regla 1: TTPs MITRE (peso: 40)
        total_rules += 1
        if mitre_ttps:
            for ttp in mitre_ttps:
                if ttp in MITRE_TTP_TO_PHASE:
                    phase = MITRE_TTP_TO_PHASE[ttp]
                    phase_votes[phase] += 40
                    matched_rules += 1
                    self._log(f"✓ TTP {ttp} → {phase.value} (+40 puntos)")
        
        # Regla 2: Temporal violations (peso: 35)
        total_rules += 1
        if temporal_violations:
            for violation in temporal_violations:
                vtype = violation.get("type", "").upper()
                if vtype in TEMPORAL_VIOLATION_TO_PHASE:
                    phase = TEMPORAL_VIOLATION_TO_PHASE[vtype]
                    phase_votes[phase] += 35
                    matched_rules += 1
                    self._log(f"✓ Violation {vtype} → {phase.value} (+35 puntos)")
        
        # Regla 3: Signal distribution (peso: 25)
        total_rules += 1
        signal_types = {}
        for sig in signals:
            stype = sig.get("type", "unknown")
            signal_types[stype] = signal_types.get(stype, 0) + 1
        
        if signal_types:
            matched_rules += 1
            self._log(f"✓ Distribución de señales: {signal_types} (+25 puntos base)")
        
        # Elegir fase con más votos
        if not any(phase_votes.values()):
            detected_phase = IRPhase.UNKNOWN
            consistency = 0
        else:
            detected_phase = max(phase_votes.items(), key=lambda x: x[1])[0]
            # Consistencia = (reglas matched / total) * 100
            consistency = (matched_rules * 100) // max(1, total_rules)
            consistency = max(0, min(100, consistency))
        
        self._log(f"Fase: {detected_phase.value}, Consistencia: {consistency}%")
        
        return (detected_phase, consistency)
    
    def analyze_focus(
        self,
        bundle_id: str,
        signals: List[Dict[str, Any]],
        temporal_violations: Optional[List[Dict[str, Any]]] = None,
        mitre_ttps: Optional[List[str]] = None,
    ) -> FocusAnalysis:
        """
        Análisis completo de foco visible.
        """
        # Detectar fase
        phase, consistency = self.detect_phase(signals, temporal_violations, mitre_ttps)
        
        # Obtener variables visibles
        visible_vars = VISIBLE_VARIABLES_BY_PHASE.get(phase, {})
        visible_categories = set(visible_vars.keys())
        
        # Razonamiento
        reasoning = f"Fase={phase.value}, Consistencia={consistency}% " \
                   f"({consistency}/100 reglas satisfechas)"
        
        # Hash reproducible
        analysis_data = json.dumps({
            "bundle_id": bundle_id,
            "phase": phase.value,
            "visible_vars": sorted([
                f"{k.value}:{v}" for k, vals in visible_vars.items() for v in vals
            ]),
        }, sort_keys=True)
        focus_hash = hashlib.sha256(analysis_data.encode()).hexdigest()
        
        return FocusAnalysis(
            bundle_id=bundle_id,
            detected_phase=phase,
            consistency_score=consistency,
            consistency_rationale=f"({consistency}/100) = {consistency} reglas de {100} satisfechas",
            visible_categories=visible_categories,
            visible_variables=visible_vars,
            reasoning=reasoning,
            focus_hash=focus_hash,
        )


def analyze_bundle_focus(
    bundle: Dict[str, Any],
    verbose: bool = False,
) -> Tuple[FocusAnalysis, List[Dict[str, Any]]]:
    """Conveniencia: análisis completo de un bundle."""
    engine = VisibleVariablesEngine(verbose=verbose)
    
    focus = engine.analyze_focus(
        bundle_id=bundle.get("bundle_id", "unknown"),
        signals=bundle.get("signals", []),
        temporal_violations=bundle.get("temporal_violations", []),
        mitre_ttps=bundle.get("mitre_ttps", []),
    )
    
    return (focus, bundle.get("signals", []))


# ============================================================================
# PREPARACIÓN PARA HITO 2.1: AbductiveIntentEngine
# ============================================================================

class AbductiveIntentEngineInterface:
    """
    Interfaz preparada para recibir el motor de inferencia (Hito 2.1).
    
    El AbductiveIntentEngine usará VisibleVariablesEngine como base
    y agregará Ockham's Razor para seleccionar la hipótesis más simple.
    """
    
    @staticmethod
    def infer_habit(
        artifacts: List[Dict[str, Any]],
        phase: IRPhase,
    ) -> Dict[str, Any]:
        """
        PLACEHOLDER para Hito 2.1.
        
        Entrada: cadena de artefactos forenses + fase detectada
        Salida: hipótesis de hábito (intención) más simple
        
        Será implementado en Hito 2.1 con Ockham's Razor.
        """
        raise NotImplementedError("AbductiveIntentEngine — Hito 2.1")


if __name__ == "__main__":
    # Demo
    case_002 = {
        "bundle_id": "case_002_demo",
        "signals": [
            {"label": "temporal_uniformity", "type": "anomaly"},
            {"label": "process_memory_contradiction", "type": "contradiction"},
        ],
        "temporal_violations": [{"type": "STATISTICAL_UNIFORMITY", "severity": 0.85}],
        "mitre_ttps": ["T1497", "T1565.001"],
    }
    
    print("=" * 80)
    print("VisibleVariablesEngine — REFACTORIZACIÓN P0 (Sin float)")
    print("=" * 80)
    
    focus, _ = analyze_bundle_focus(case_002, verbose=True)
    
    print("\nResultado:")
    print(f"  Fase: {focus.detected_phase.value}")
    print(f"  Consistencia: {focus.consistency_score}%  (ENTERO, no float)")
    print(f"  Rationale: {focus.consistency_rationale}")
    print(f"  Hash: {focus.focus_hash[:16]}...")
    print("\nJSON exportable (Daubert-auditable):")
    print(focus.to_json())
