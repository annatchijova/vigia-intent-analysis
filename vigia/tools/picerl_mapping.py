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
vigia/forensics/picerl_mapping.py — REFACTORIZACIÓN P0

CAMBIOS REALIZADOS:
  P0-1: IntentHypothesis.confidence (float) → consistency_score (int)
  P0-3: _classify_intent_type y _generate_falsifiable_statement ahora usan TABLAS
        (no lógica condicional oculta, todo auditable)
  P0-4: Todos los mapeos explícitos en CAPS como constantes de módulo

GARANTÍA DAUBERT:
  - 100% auditable: IR Phase → PICERL Phase es tabla (no función)
  - 100% reproducible: mismo input → mismo output siempre
  - 100% falsable: cada hipótesis tiene what_would_falsify (campo obligatorio)
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING

logger = logging.getLogger(__name__)

# TYPE_CHECKING: Evitar circular imports
if TYPE_CHECKING:
    from abductive_intent_engine_P0 import AbductiveResult


# ============================================================================
# ENUMS
# ============================================================================

class IRPhase(str, Enum):
    """Fases de IR."""
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


class PICERLPhase(str, Enum):
    """Fases del ciclo PICERL (SANS)."""
    PREPARATION = "preparation"
    IDENTIFICATION = "identification"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    LESSONS_LEARNED = "lessons_learned"


# ============================================================================
# TABLAS DE MAPEO DETERMINÍSTICAS (P0-3: Sin lógica condicional oculta)
# ============================================================================

# TABLA 1: IR Phase → PICERL Phase
IR_TO_PICERL_MAPPING: Dict[IRPhase, PICERLPhase] = {
    IRPhase.RECONNAISSANCE: PICERLPhase.PREPARATION,
    IRPhase.INITIAL_ACCESS: PICERLPhase.IDENTIFICATION,
    IRPhase.EXECUTION: PICERLPhase.IDENTIFICATION,
    IRPhase.PERSISTENCE: PICERLPhase.CONTAINMENT,
    IRPhase.PRIVILEGE_ESCALATION: PICERLPhase.CONTAINMENT,
    IRPhase.DEFENSE_EVASION: PICERLPhase.ERADICATION,
    IRPhase.LATERAL_MOVEMENT: PICERLPhase.CONTAINMENT,
    IRPhase.COLLECTION: PICERLPhase.ERADICATION,
    IRPhase.EXFILTRATION: PICERLPhase.ERADICATION,
    IRPhase.COMMAND_AND_CONTROL: PICERLPhase.CONTAINMENT,
    IRPhase.IMPACT: PICERLPhase.ERADICATION,
    IRPhase.CLEANUP: PICERLPhase.RECOVERY,
    IRPhase.CREDENTIAL_ACCESS: PICERLPhase.CONTAINMENT,
    IRPhase.DISCOVERY: PICERLPhase.CONTAINMENT,
    IRPhase.UNKNOWN: PICERLPhase.IDENTIFICATION,
}

# TABLA 2: IR Phase → Intent Type (P0-3: Sin _classify_intent_type())
INTENT_TYPE_BY_PHASE: Dict[IRPhase, str] = {
    IRPhase.RECONNAISSANCE: "reconnaissance",
    IRPhase.INITIAL_ACCESS: "initial_compromise",
    IRPhase.EXECUTION: "code_execution",
    IRPhase.PERSISTENCE: "persistence",
    IRPhase.PRIVILEGE_ESCALATION: "privilege_escalation",
    IRPhase.DEFENSE_EVASION: "defense_evasion",
    IRPhase.CREDENTIAL_ACCESS: "credential_theft",
    IRPhase.DISCOVERY: "reconnaissance",
    IRPhase.LATERAL_MOVEMENT: "lateral_movement",
    IRPhase.COLLECTION: "data_collection",
    IRPhase.EXFILTRATION: "exfiltration",
    IRPhase.COMMAND_AND_CONTROL: "command_control",
    IRPhase.IMPACT: "sabotage",
    IRPhase.CLEANUP: "anti_forensics",
    IRPhase.UNKNOWN: "unknown",
}

# TABLA 3: IR Phase → Intent Description
INTENT_DESCRIPTION_BY_PHASE: Dict[IRPhase, str] = {
    IRPhase.RECONNAISSANCE: (
        "Atacante está realizando reconocimiento del entorno "
        "para identificar objetivos y vectores de ataque."
    ),
    IRPhase.INITIAL_ACCESS: (
        "Atacante obtuvo acceso inicial al entorno mediante "
        "un vector de puerta de entrada (email, web, etc.)."
    ),
    IRPhase.EXECUTION: (
        "Atacante ejecutó código malicioso en el sistema comprometido."
    ),
    IRPhase.PERSISTENCE: (
        "Atacante está instalando mecanismos de persistencia "
        "para mantener acceso a largo plazo."
    ),
    IRPhase.PRIVILEGE_ESCALATION: (
        "Atacante está intentando obtener privilegios superiores "
        "en el sistema o dominio."
    ),
    IRPhase.DEFENSE_EVASION: (
        "Atacante está ocultando su actividad, manipulando logs, "
        "o usando técnicas de evasión de detección."
    ),
    IRPhase.CREDENTIAL_ACCESS: (
        "Atacante está intentando obtener credenciales válidas "
        "para expandir su acceso."
    ),
    IRPhase.DISCOVERY: (
        "Atacante está reconociendo el entorno comprometido "
        "para planificar pasos posteriores."
    ),
    IRPhase.LATERAL_MOVEMENT: (
        "Atacante está moviéndose lateralmente por la red "
        "para comprometer sistemas adicionales."
    ),
    IRPhase.COLLECTION: (
        "Atacante está recopilando datos de interés para exfiltración."
    ),
    IRPhase.EXFILTRATION: (
        "Atacante está sacando datos del entorno comprometido."
    ),
    IRPhase.COMMAND_AND_CONTROL: (
        "Atacante está comunicándose con servidores de comando y control "
        "para recibir órdenes."
    ),
    IRPhase.IMPACT: (
        "Atacante está causando daño directo al entorno "
        "(encriptación, borrado, etc.)."
    ),
    IRPhase.CLEANUP: (
        "Atacante está borrando evidencia de su actividad."
    ),
    IRPhase.UNKNOWN: (
        "No se puede determinar la intención del atacante con claridad."
    ),
}

# TABLA 4: IR Phase → Falsifiable Statement (P0-3: Sin _generate_falsifiable_statement())
FALSIFIABLE_STATEMENT_BY_PHASE: Dict[IRPhase, str] = {
    IRPhase.PERSISTENCE: (
        "Esta hipótesis sería falsa si no encontramos artefactos "
        "de persistencia (registry, scheduled tasks, services, cron) "
        "después de un análisis completo del sistema."
    ),
    IRPhase.EXFILTRATION: (
        "Esta hipótesis sería falsa si el análisis de tráfico de red "
        "no muestra transferencias de datos salientes hacia IPs/dominios externos."
    ),
    IRPhase.DEFENSE_EVASION: (
        "Esta hipótesis sería falsa si los logs están íntegros "
        "y muestran una cadena de eventos coherente y sin vacíos."
    ),
    IRPhase.LATERAL_MOVEMENT: (
        "Esta hipótesis sería falsa si el análisis de flujos de red "
        "no muestra conexiones entre múltiples hosts."
    ),
    IRPhase.CREDENTIAL_ACCESS: (
        "Esta hipótesis sería falsa si no hay evidencia de intentos "
        "de acceso con credenciales en los logs de autenticación."
    ),
    IRPhase.INITIAL_ACCESS: (
        "Esta hipótesis sería falsa si el análisis de logs de perimeter "
        "no muestra conexiones entrantes desde direcciones externas."
    ),
    IRPhase.UNKNOWN: (
        "Esta hipótesis sería falsa si el análisis forense completo "
        "no revela evidencia consistente con la fase detectada."
    ),
}

# TABLA 5: IR Phase → MITRE TTPs
MITRE_TTPS_BY_PHASE: Dict[IRPhase, List[str]] = {
    IRPhase.PERSISTENCE: ["T1547", "T1547.1", "T1098", "T1137"],
    IRPhase.EXFILTRATION: ["T1020", "T1030", "T1048", "T1041"],
    IRPhase.LATERAL_MOVEMENT: ["T1570", "T1021", "T1091", "T1550"],
    IRPhase.DEFENSE_EVASION: ["T1548", "T1197", "T1140", "T1564", "T1562", "T1070"],
    IRPhase.PRIVILEGE_ESCALATION: ["T1548", "T1134", "T1547", "T1053"],
    IRPhase.INITIAL_ACCESS: ["T1566", "T1200", "T1199"],
    IRPhase.EXECUTION: ["T1059", "T1204"],
    IRPhase.UNKNOWN: [],
}

# TABLA 6: IR Phase → CIS Controls
CIS_CONTROLS_BY_PHASE: Dict[IRPhase, List[str]] = {
    IRPhase.PERSISTENCE: ["CIS 3.3", "CIS 3.4", "CIS 6.1", "CIS 8.5"],
    IRPhase.EXFILTRATION: ["CIS 7.1", "CIS 8.1", "CIS 8.3", "CIS 9.1"],
    IRPhase.LATERAL_MOVEMENT: ["CIS 3.5", "CIS 6.1", "CIS 6.2", "CIS 8.2"],
    IRPhase.DEFENSE_EVASION: ["CIS 3.8", "CIS 6.3", "CIS 7.3", "CIS 8.4"],
    IRPhase.UNKNOWN: [],
}

# P1: Congelar tablas de mapeo para evitar mutación en runtime
try:
    from types import MappingProxyType
    IR_TO_PICERL_MAPPING = MappingProxyType(IR_TO_PICERL_MAPPING)  # type: ignore[misc]
    INTENT_TYPE_BY_PHASE = MappingProxyType(INTENT_TYPE_BY_PHASE)  # type: ignore[misc]
    INTENT_DESCRIPTION_BY_PHASE = MappingProxyType(INTENT_DESCRIPTION_BY_PHASE)  # type: ignore[misc]
    FALSIFIABLE_STATEMENT_BY_PHASE = MappingProxyType(FALSIFIABLE_STATEMENT_BY_PHASE)  # type: ignore[misc]
    MITRE_TTPS_BY_PHASE = MappingProxyType(MITRE_TTPS_BY_PHASE)  # type: ignore[misc]
    CIS_CONTROLS_BY_PHASE = MappingProxyType(CIS_CONTROLS_BY_PHASE)  # type: ignore[misc]
    _TABLES_FROZEN = True
except ImportError:
    _TABLES_FROZEN = False


# ============================================================================
# MODELOS DE DATOS
# ============================================================================

@dataclass
class IntentHypothesis:
    """
    Hipótesis formal de intención del atacante.
    
    P0-1: consistency_score es ENTERO [0,100], no float.
    """
    
    hypothesis_id: str
    picerl_phase: PICERLPhase
    ir_phase: IRPhase
    
    intent_description: str
    intent_type: str
    consistency_score: int  # [0, 100] ENTERO, no float
    
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    what_would_falsify: str = ""  # OBLIGATORIO para Daubert
    
    related_mitre_ttps: List[str] = field(default_factory=list)
    related_cis_controls: List[str] = field(default_factory=list)
    
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        # P1: Validar rango de consistency_score (Daubert)
        cs = max(0, min(100, int(self.consistency_score)))
        payload = {
            "hypothesis_id": self.hypothesis_id,
            "picerl_phase": self.picerl_phase.value,
            "ir_phase": self.ir_phase.value,
            "intent_description": self.intent_description,
            "intent_type": self.intent_type,
            "consistency_score": cs,  # Entero clamped [0,100]
            "supporting_evidence": sorted(self.supporting_evidence),
            "contradicting_evidence": sorted(self.contradicting_evidence),
            "what_would_falsify": self.what_would_falsify,
            "related_mitre_ttps": sorted(self.related_mitre_ttps),
            "related_cis_controls": sorted(self.related_cis_controls),
            "notes": self.notes,
        }
        # P1: HMAC opcional de integridad
        try:
            import hmac, hashlib, os as _os
            key_hex = _os.environ.get("VIGIA_HMAC_KEY", "").strip()
            if key_hex:
                key = bytes.fromhex(key_hex)
                canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
                payload["_intent_hmac"] = hmac.new(key, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
                del key
        except Exception:
            pass
        return payload


# ============================================================================
# PICERL MAPPER
# ============================================================================

class PICERLMapper:
    """Motor de mapeo IR Phase → PICERL-I (usando solo tablas determinísticas)."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def _log(self, msg: str):
        if self.verbose:
            logger.info(f"[PICERLMapper] {msg}")
    
    def map_focus_analysis_to_intent(
        self,
        ir_phase: IRPhase,
        consistency_score: int,
        bundle_id: str,
    ) -> IntentHypothesis:
        """
        Traduce IR Phase → IntentHypothesis usando SOLO tablas (P0-3).
        
        No hay _classify_intent_type() opaca.
        No hay _generate_falsifiable_statement() mágica.
        Todo es TABLE LOOKUP.
        """
        # P0-3: Lookups en tablas, no funciones
        picerl_phase = IR_TO_PICERL_MAPPING.get(ir_phase, PICERLPhase.IDENTIFICATION)
        intent_type = INTENT_TYPE_BY_PHASE.get(ir_phase, "unknown")
        description = INTENT_DESCRIPTION_BY_PHASE.get(ir_phase, "Intención desconocida")
        falsifiable = FALSIFIABLE_STATEMENT_BY_PHASE.get(
            ir_phase,
            "Esta hipótesis sería falsa si no hay evidencia relevante."
        )
        mitre_ttps = MITRE_TTPS_BY_PHASE.get(ir_phase, [])
        cis_controls = CIS_CONTROLS_BY_PHASE.get(ir_phase, [])
        
        hypothesis = IntentHypothesis(
            hypothesis_id=f"INTENT-{bundle_id[:8]}-{ir_phase.value}",
            picerl_phase=picerl_phase,
            ir_phase=ir_phase,
            intent_description=description,
            intent_type=intent_type,
            consistency_score=consistency_score,  # Entero [0,100]
            what_would_falsify=falsifiable,  # Obligatorio para Daubert
            related_mitre_ttps=mitre_ttps,
            related_cis_controls=cis_controls,
        )
        
        self._log(f"Hipótesis generada: {intent_type} (consistency={consistency_score}%)")
        
        return hypothesis
    
    def map_abductive_result(
        self,
        abductive_result: "AbductiveResult",
        focus_consistency: int,
        bundle_id: str,
    ) -> IntentHypothesis:
        """
        Mapea AbductiveResult (motor Ockham) → IntentHypothesis (PICERL-I).
        
        Reemplaza la fase manual: ya no adivinamos intención desde IRPhase,
        usamos la hipótesis ganadora del AbductiveIntentEngine.
        
        Args:
            abductive_result: AbductiveResult del motor Ockham
            focus_consistency: consistency_score de FocusAnalysis [0,100]
            bundle_id: identificador del bundle
        
        Returns:
            IntentHypothesis mapeada a PICERL-I
        """
        winner = abductive_result.winner
        
        # P0-3: PICERL phase desde tabla (igual que antes)
        picerl_phase = IR_TO_PICERL_MAPPING.get(
            winner.phase, 
            PICERLPhase.IDENTIFICATION
        )
        
        # MITRE TTPs desde tabla de la fase
        mitre_ttps = MITRE_TTPS_BY_PHASE.get(winner.phase, [])
        cis_controls = CIS_CONTROLS_BY_PHASE.get(winner.phase, [])
        
        hypothesis = IntentHypothesis(
            hypothesis_id=winner.hypothesis_id,  # "H_DE_001" en vez de "INTENT-xxx"
            picerl_phase=picerl_phase,
            ir_phase=winner.phase,
            intent_description=winner.explanation,  # Explicación del motor Ockham
            intent_type=winner.intent_type,
            consistency_score=focus_consistency,  # Entero desde FocusAnalysis
            what_would_falsify=winner.what_would_falsify,  # Daubert requirement
            related_mitre_ttps=mitre_ttps,
            related_cis_controls=cis_controls,
            supporting_evidence=winner.supporting_rules,  # Reglas de soporte
        )
        
        self._log(
            f"Hipótesis abductiva mapeada: {winner.hypothesis_id} "
            f"({winner.intent_type}, cost={winner.cost})"
        )
        return hypothesis
    
    def generate_picerl_i_report(
        self,
        bundle_id: str,
        hypotheses: List[IntentHypothesis],
    ) -> str:
        """Genera reporte PICERL-I en formato legible."""
        parts = [
            "=" * 80,
            "VIGÍA — Reporte de Intención Forense (PICERL-I)",
            "=" * 80,
            f"\nBundle ID: {bundle_id}",
            f"Versión: VIGÍA v1.0 (SANS-compatible, REFACTORIZACIÓN P0)",
            "\n" + "-" * 80,
            "RESUMEN POR FASE PICERL",
            "-" * 80,
        ]
        
        hypotheses_by_picerl = {}
        for h in hypotheses:
            if h.picerl_phase not in hypotheses_by_picerl:
                hypotheses_by_picerl[h.picerl_phase] = []
            hypotheses_by_picerl[h.picerl_phase].append(h)
        
        for picerl_phase in PICERLPhase:
            if picerl_phase in hypotheses_by_picerl:
                parts.append(f"\n[{picerl_phase.value.upper()}]")
                for h in hypotheses_by_picerl[picerl_phase]:
                    parts.append(f"  Intención: {h.intent_description}")
                    parts.append(f"  Tipo: {h.intent_type}")
                    parts.append(f"  Consistencia: {h.consistency_score}%  (ENTERO)")
                    if h.related_mitre_ttps:
                        parts.append(f"  TTPs MITRE: {', '.join(h.related_mitre_ttps[:3])}")
        
        parts.append("\n" + "-" * 80)
        parts.append("HIPÓTESIS DE INTENCIÓN (DETALLADO)")
        parts.append("-" * 80)
        
        for i, h in enumerate(hypotheses, 1):
            parts.append(f"\n[{i}] {h.hypothesis_id}")
            parts.append(f"    Descripción: {h.intent_description}")
            parts.append(f"    Consistencia: {h.consistency_score}%")
            parts.append(f"    Falsabilidad: {h.what_would_falsify}")
        
        parts.append("\n" + "=" * 80)
        
        return "\n".join(parts)


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("PICERLMapper — REFACTORIZACIÓN P0 (Tablas determinísticas)")
    print("=" * 80)
    
    mapper = PICERLMapper(verbose=True)
    
    # Simular FocusAnalysis sin usar visible_variables
    hyp = mapper.map_focus_analysis_to_intent(
        ir_phase=IRPhase.DEFENSE_EVASION,
        consistency_score=95,
        bundle_id="case_002_demo",
    )
    
    report = mapper.generate_picerl_i_report("case_002_demo", [hyp])
    print(report)
