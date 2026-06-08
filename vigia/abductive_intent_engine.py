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
from vigia.tools.visible_variables import VariableCategory, IRPhase


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
    
    # ========================================================================
    # FASE: RECONNAISSANCE (Kimi)
    # ========================================================================
    IRPhase.RECONNAISSANCE: [
        AbductiveHypothesis(
            hypothesis_id="H_RE_001",
            intent_type="targeted_reconnaissance",
            phase=IRPhase.RECONNAISSANCE,
            required_artifacts=["port_scans", "dns_enumeration", "http_crawling"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante realizó reconocimiento activo del objetivo: "
                "escaneo de puertos, enumeración DNS, y crawling HTTP. "
                "Todo es observable en los logs de red. "
                "Indica intención de compromiso planificado, no oportunista."
            ),
            what_would_falsify=(
                "Falsa si las consultas provienen de un motor de búsqueda legítimo "
                "(Googlebot, Bingbot) o si el escaneo es de un auditor interno."
            ),
            supporting_rules=[
                "RULE_RE_001: Port scan + DNS enum + HTTP crawl = reconocimiento activo",
                "RULE_RE_002: Patrón secuencial (puertos 80→443→8080) = no es aleatorio",
            ],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_RE_002",
            intent_type="osint_gathering",
            phase=IRPhase.RECONNAISSANCE,
            required_artifacts=["whois_queries", "social_media_osint"],
            assumed_artifacts=["attacker_knows_employee_names"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante recolectó inteligencia de fuentes abiertas (OSINT): "
                "WHOIS para infraestructura, social media para nombres/cargos."
            ),
            what_would_falsify=(
                "Falsa si las queries WHOIS provienen de un registrar legítimo "
                "en proceso de transferencia de dominio."
            ),
            supporting_rules=["RULE_RE_003: WHOIS + social media = OSINT direccionado"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_RE_003",
            intent_type="opportunistic_scanning",
            phase=IRPhase.RECONNAISSANCE,
            required_artifacts=["port_scans"],
            assumed_artifacts=["attacker_is_shodan_bot", "no_specific_target"],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante realizó escaneo masivo no direccionado. "
                "Solo port_scan observable. Consistente con Shodan o botnet masivo."
            ),
            what_would_falsify=(
                "Falsa si el escaneo es parte de un penetration test contratado "
                "y documentado."
            ),
            supporting_rules=["RULE_RE_004: Solo port scan masivo = no hay intención específica"],
        ),
    ],
    
    # ========================================================================
    # FASE: INITIAL_ACCESS (Kimi)
    # ========================================================================
    IRPhase.INITIAL_ACCESS: [
        AbductiveHypothesis(
            hypothesis_id="H_IA_001",
            intent_type="spearphishing_execution",
            phase=IRPhase.INITIAL_ACCESS,
            required_artifacts=["phishing_email_delivered", "malicious_attachment_executed"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante obtuvo acceso inicial vía spearphishing: "
                "email malicioso entregado, adjunto ejecutado por la víctima."
            ),
            what_would_falsify=(
                "Falsa si el email tiene SPF/DKIM/DMARC válidos "
                "y el adjunto está firmado por la organización."
            ),
            supporting_rules=[
                "RULE_IA_001: Phishing + ejecución de adjunto = acceso inicial clásico",
            ],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_IA_002",
            intent_type="exploitation_public_facing",
            phase=IRPhase.INITIAL_ACCESS,
            required_artifacts=["exploitation_public_facing_app", "shell_established"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante explotó una aplicación expuesta a internet "
                "(web server, VPN gateway, RDP) para establecer shell."
            ),
            what_would_falsify=(
                "Falsa si la conexión proviene de un pentester autorizado "
                "o si el 'exploit' es un health check automatizado."
            ),
            supporting_rules=["RULE_IA_003: Exploit + shell sin credenciales = vulnerabilidad pública"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_IA_003",
            intent_type="supply_chain_compromise",
            phase=IRPhase.INITIAL_ACCESS,
            required_artifacts=["hardware_additions"],
            assumed_artifacts=["attacker_has_physical_access", "compromised_vendor"],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante introdujo hardware malicioso a través de la cadena de suministro. "
                "Requiere suponer acceso físico o relación de confianza con vendor."
            ),
            what_would_falsify=(
                "Falsa si el hardware es IT asset management autorizado "
                "y la variante de firmware es estándar corporativa."
            ),
            supporting_rules=["RULE_IA_004: Hardware no autorizado + sin registro = supply chain"],
        ),
    ],
    
    # ========================================================================
    # FASE: EXECUTION (Kimi)
    # ========================================================================
    IRPhase.EXECUTION: [
        AbductiveHypothesis(
            hypothesis_id="H_EX_001",
            intent_type="command_line_abuse",
            phase=IRPhase.EXECUTION,
            required_artifacts=["command_line_execution", "script_execution"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante ejecutó comandos y scripts directamente en el sistema. "
                "Patrón clásico post-exploitation: cmd.exe, PowerShell, bash."
            ),
            what_would_falsify=(
                "Falsa si los comandos son de un admin legítimo durante "
                "sesión de mantenimiento documentada."
            ),
            supporting_rules=["RULE_EX_001: Cmd + script + no parent legítimo = ejecución atacante"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_EX_002",
            intent_type="scheduled_task_abuse",
            phase=IRPhase.EXECUTION,
            required_artifacts=["scheduled_task_execution", "service_execution"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante abusó de mecanismos legítimos: scheduled task o service "
                "para ejecutar payload sin interacción humana."
            ),
            what_would_falsify=(
                "Falsa si el scheduled task fue creado por GPO corporativa "
                "y el binario está firmado por la organización."
            ),
            supporting_rules=["RULE_EX_002: Task/Service + binario no firmado = abuso"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_EX_003",
            intent_type="powershell_living_off_the_land",
            phase=IRPhase.EXECUTION,
            required_artifacts=["powershell_abuse", "encoded_commands"],
            assumed_artifacts=["attacker_avoids_disk_touch"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante usó PowerShell con comandos codificados (base64, -enc) "
                "para ejecutar sin escribir a disco. Técnica LOTL."
            ),
            what_would_falsify=(
                "Falsa si el PowerShell es un script de administración legítimo "
                "que usa encoding por legibilidad."
            ),
            supporting_rules=["RULE_EX_003: PowerShell -enc + sin script en disco = LOTL"],
        ),
    ],
    
    # ========================================================================
    # FASE: PRIVILEGE_ESCALATION (Kimi - nuevas hipótesis)
    # ========================================================================
    IRPhase.PRIVILEGE_ESCALATION: [
        AbductiveHypothesis(
            hypothesis_id="H_PE_004",
            intent_type="token_impersonation",
            phase=IRPhase.PRIVILEGE_ESCALATION,
            required_artifacts=["token_impersonation", "process_injection"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante escaló privilegios vía robo de token de proceso privilegiado "
                "seguido de inyección en proceso legítimo."
            ),
            what_would_falsify=(
                "Falsa si el proceso que recibe la inyección es un debugger legítimo "
                "o una herramienta de EDR con firma válida."
            ),
            supporting_rules=["RULE_PV_001: Token steal + injection = privesc sin exploit"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_PE_005",
            intent_type="exploit_vulnerability",
            phase=IRPhase.PRIVILEGE_ESCALATION,
            required_artifacts=["exploit_vulnerability", "kernel_mode_execution"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante explotó una vulnerabilidad de escalada local "
                "para ejecutar en modo kernel."
            ),
            what_would_falsify=(
                "Falsa si el driver vulnerable es un hotfix desplegado por IT "
                "y el 'exploit' es un test de regresión."
            ),
            supporting_rules=["RULE_PV_002: Kernel execution = exploit de LPE"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_PE_006",
            intent_type="kerberoasting",
            phase=IRPhase.PRIVILEGE_ESCALATION,
            required_artifacts=["kerberoasting_indicators", "ticket_granting_service_request"],
            assumed_artifacts=["attacker_has_domain_access"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante solicitó tickets de servicio Kerberos para cuentas con SPN "
                "y los crackeó offline."
            ),
            what_would_falsify=(
                "Falsa si las solicitudes TGS provienen de un script de auditoría "
                "de contraseñas de servicio."
            ),
            supporting_rules=["RULE_PV_003: TGS request + SPN + cracking = Kerberoasting"],
        ),
    ],
    
    # ========================================================================
    # FASE: CREDENTIAL_ACCESS (Kimi)
    # ========================================================================
    IRPhase.CREDENTIAL_ACCESS: [
        AbductiveHypothesis(
            hypothesis_id="H_CA_001",
            intent_type="credential_dumping",
            phase=IRPhase.CREDENTIAL_ACCESS,
            required_artifacts=["credential_dumping", "lsass_access"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante accedió a LSASS para extraer hashes de credenciales. "
                "Técnica estándar: Mimikatz, Procdump."
            ),
            what_would_falsify=(
                "Falsa si LSASS fue accedido por un EDR legítimo con política documentada."
            ),
            supporting_rules=["RULE_CA_001: LSASS access + dump = credential extraction"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_CA_002",
            intent_type="brute_force",
            phase=IRPhase.CREDENTIAL_ACCESS,
            required_artifacts=["brute_force_attempts", "failed_logon_spike"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante intentó adivinar credenciales vía fuerza bruta: "
                "múltiples intentos fallidos en ventana corta."
            ),
            what_would_falsify=(
                "Falsa si son intentos fallidos de un usuario que olvidó contraseña, "
                "sin patrón de diccionario."
            ),
            supporting_rules=["RULE_CA_002: Failed logon spike + diccionario = brute force"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_CA_003",
            intent_type="keylogger_deployment",
            phase=IRPhase.CREDENTIAL_ACCESS,
            required_artifacts=["keylogger_activity", "input_capture_indicators"],
            assumed_artifacts=["attacker_wants_long_term_cred_theft"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante desplegó keylogger para capturar credenciales en tiempo real. "
                "Requiere suponer intención de robo continuo."
            ),
            what_would_falsify=(
                "Falsa si es una herramienta de RPA o software de asistencia remota "
                "autorizado con logging para debugging."
            ),
            supporting_rules=["RULE_CA_003: Keylogger + no RPA policy = cred theft"],
        ),
    ],
    
    # ========================================================================
    # FASE: COMMAND_AND_CONTROL (Kimi)
    # ========================================================================
    IRPhase.COMMAND_AND_CONTROL: [
        AbductiveHypothesis(
            hypothesis_id="H_C2_001",
            intent_type="domain_fronting_beacon",
            phase=IRPhase.COMMAND_AND_CONTROL,
            required_artifacts=["beaconing_pattern", "domain_fronting_indicators"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante estableció comunicación C2 vía domain fronting: "
                "tráfico aparentemente legítimo a CDN que comunica con servidor atacante."
            ),
            what_would_falsify=(
                "Falsa si el tráfico es de una aplicación empresarial legítima "
                "que usa el mismo CDN."
            ),
            supporting_rules=[
                "RULE_C2_001: CDN traffic + SNI mismatch = domain fronting",
                "RULE_C2_002: Intervalo regular = beacon",
            ],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_C2_002",
            intent_type="dns_tunnel_c2",
            phase=IRPhase.COMMAND_AND_CONTROL,
            required_artifacts=["dns_c2_queries", "domain_generation_algorithm"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante usa DNS como canal C2: queries TXT/A con payload codificado, "
                "o DGA para evadir blacklists."
            ),
            what_would_falsify=(
                "Falsa si las queries DNS son de un software de actualización "
                "que usa TXT records para verificación."
            ),
            supporting_rules=["RULE_C2_003: TXT queries + DGA = DNS tunnel"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_C2_003",
            intent_type="dead_drop_resolver",
            phase=IRPhase.COMMAND_AND_CONTROL,
            required_artifacts=["dead_drop_resolver", "social_media_c2"],
            assumed_artifacts=["attacker_reads_public_platforms"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante usa plataformas públicas (Twitter, GitHub) como C2: "
                "publica instrucciones ofuscadas, el malware las lee periódicamente."
            ),
            what_would_falsify=(
                "Falsa si las conexiones son de un usuario legítimo "
                "y el payload es un documento público."
            ),
            supporting_rules=["RULE_C2_004: GitHub/Twitter + patrones = dead drop"],
        ),
    ],
    
    # ========================================================================
    # FASE: COLLECTION (Kimi)
    # ========================================================================
    IRPhase.COLLECTION: [
        AbductiveHypothesis(
            hypothesis_id="H_CO_001",
            intent_type="data_staging_for_exfil",
            phase=IRPhase.COLLECTION,
            required_artifacts=["data_staging_directory", "archive_collection"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante está recolectando y preparando datos para exfiltración: "
                "archivos copiados a staging, comprimidos. Fase previa a exfiltración."
            ),
            what_would_falsify=(
                "Falsa si es un backup automatizado de la organización "
                "y el archivo es .bak programado por IT."
            ),
            supporting_rules=["RULE_CO_001: Staging + archive = preparación exfil"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_CO_002",
            intent_type="clipboard_and_screen_capture",
            phase=IRPhase.COLLECTION,
            required_artifacts=["clipboard_collection", "screen_capture"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante recolecta información de sesiones activas: "
                "capturas de pantalla para documentos, clipboard para credenciales."
            ),
            what_would_falsify=(
                "Falsa si es software de monitoring de empleados (DLP) "
                "con política de consentimiento."
            ),
            supporting_rules=["RULE_CO_002: Screen cap + clipboard = espionaje activo"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_CO_003",
            intent_type="audio_and_video_surveillance",
            phase=IRPhase.COLLECTION,
            required_artifacts=["audio_capture"],
            assumed_artifacts=["attacker_wants_conversations", "long_term_eavesdropping"],
            cost=2,
            coverage_score=0,
            explanation=(
                "Atacante activó micrófono para capturar conversaciones. "
                "Indica APT sofisticado con intención de espionaje verbal."
            ),
            what_would_falsify=(
                "Falsa si es una app de videoconferencia legítima (Teams, Zoom) "
                "con indicador de grabación visible."
            ),
            supporting_rules=["RULE_CO_003: Mic access + sin app de conferencia = espionaje"],
        ),
    ],
    
    # ========================================================================
    # FASE: IMPACT (Kimi)
    # ========================================================================
    IRPhase.IMPACT: [
        AbductiveHypothesis(
            hypothesis_id="H_IM_001",
            intent_type="ransomware_deployment",
            phase=IRPhase.IMPACT,
            required_artifacts=["ransomware_note", "file_encryption_indicators"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante desplegó ransomware: nota de rescate visible, "
                "archivos cifrados, mensaje de pago. Intención financiera explícita."
            ),
            what_would_falsify=(
                "Falsa si el 'ransomware note' es mensaje de IT sobre "
                "política de cifrado corporativo (BitLocker)."
            ),
            supporting_rules=["RULE_IM_001: Ransom note + files renamed = ransomware"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_IM_002",
            intent_type="wiper_destruction",
            phase=IRPhase.IMPACT,
            required_artifacts=["data_destruction", "disk_wipe_activity"],
            assumed_artifacts=[],
            cost=0,
            coverage_score=0,
            explanation=(
                "Atacante destruyó datos intencionalmente sin pedir rescate: "
                "sobrescritura de sectores, destrucción de backups. Sabotaje."
            ),
            what_would_falsify=(
                "Falsa si es resultado de un disk cleanup tool mal configurado, "
                "o un secure erase autorizado."
            ),
            supporting_rules=["RULE_IM_002: Destrucción + no rescate = sabotaje"],
        ),
        AbductiveHypothesis(
            hypothesis_id="H_IM_003",
            intent_type="defacement_and_humiliation",
            phase=IRPhase.IMPACT,
            required_artifacts=["defacement_indicator", "service_stop"],
            assumed_artifacts=["attacker_wants_publicity"],
            cost=1,
            coverage_score=0,
            explanation=(
                "Atacante modificó sitios web para enviar mensaje político/ideológico. "
                "Intención de publicidad (hacktivismo)."
            ),
            what_would_falsify=(
                "Falsa si es un rediseño autorizado o error de deployment de CMS "
                "verificable en pipeline CI/CD."
            ),
            supporting_rules=["RULE_IM_003: Defacement + mensaje = hacktivismo"],
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
    
    def infer(
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
    result = engine.infer(artifacts, IRPhase.DEFENSE_EVASION)
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL (JSON Daubert-auditable)")
    print("=" * 80)
    print(result.to_json())
    
    print("\n" + "=" * 80)
    print("VERIFICACIÓN: Determinismo Bit-a-Bit")
    print("=" * 80)
    result2 = engine.infer(artifacts, IRPhase.DEFENSE_EVASION)
    print(f"Hash ejecución 1: {result.result_hash}")
    print(f"Hash ejecución 2: {result2.result_hash}")
    print(f"¿Idénticos? {result.result_hash == result2.result_hash}")

