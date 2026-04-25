"""
MITRE ATT&CK Clustering — Hito 2.2

Mapea cada hipótesis abductiva a:
  1. MITRE Tactics (Reconnaissance, Initial Access, etc.)
  2. MITRE Techniques (T1592, T1566, etc.)
  3. MITRE Sub-Techniques (specific variants)
  4. Motivación del atacante (intent cluster)

Principio: No es suficiente decir "log_fabrication" (intent_type).
Necesitás conectar a MITRE para que SOC/analistas puedan:
  - Buscar detecciones existentes
  - Correlacionar con threat intel
  - Mapear a frameworks (NIST, ISO, etc.)
  - Alinear con controles de mitigación

Determinismo:
  - Cada hipótesis → lista INMUTABLE de técnicas MITRE
  - Sin ML, sin scoring: tablas explícitas
  - Falsable: ¿hay evidencia de esta técnica MITRE?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
from enum import Enum
from abductive_intent_engine_P0 import IRPhase, AbductiveHypothesis


# ============================================================================
# MITRE ATT&CK FRAMEWORK (TABLAS)
# ============================================================================

class MITRETactic(str, Enum):
    """MITRE ATT&CK 13 tácticas (Cyber Kill Chain)"""
    RECONNAISSANCE = "Reconnaissance"
    RESOURCE_DEVELOPMENT = "Resource Development"
    INITIAL_ACCESS = "Initial Access"
    EXECUTION = "Execution"
    PERSISTENCE = "Persistence"
    PRIVILEGE_ESCALATION = "Privilege Escalation"
    DEFENSE_EVASION = "Defense Evasion"
    CREDENTIAL_ACCESS = "Credential Access"
    DISCOVERY = "Discovery"
    LATERAL_MOVEMENT = "Lateral Movement"
    COLLECTION = "Collection"
    COMMAND_AND_CONTROL = "Command and Control"
    EXFILTRATION = "Exfiltration"
    IMPACT = "Impact"


@dataclass
class MITRETechnique:
    """Una técnica MITRE ATT&CK específica"""
    technique_id: str  # T1592, T1566, etc.
    technique_name: str  # "Gather Victim Org Information", etc.
    tactics: List[MITRETactic]  # Puede aplicarse a múltiples tácticas
    description: str = ""
    subtechniques: List[str] = field(default_factory=list)  # T1592.001, T1592.002, etc.


# ============================================================================
# TABLA MAESTRA: Hipótesis → MITRE Técnicas
# ============================================================================

HYPOTHESIS_TO_MITRE: Dict[str, List[MITRETechnique]] = {
    # RECONNAISSANCE
    "H_RE_001": [  # targeted_reconnaissance
        MITRETechnique(
            technique_id="T1592",
            technique_name="Gather Victim Org Information",
            tactics=[MITRETactic.RECONNAISSANCE],
            subtechniques=["T1592.001", "T1592.002"],
        ),
        MITRETechnique(
            technique_id="T1589",
            technique_name="Gather Victim Identity Information",
            tactics=[MITRETactic.RECONNAISSANCE],
        ),
    ],
    
    "H_RE_002": [  # osint_gathering
        MITRETechnique(
            technique_id="T1591",
            technique_name="Gather Victim Identity Information",
            tactics=[MITRETactic.RECONNAISSANCE],
            subtechniques=["T1591.004"],  # Social media
        ),
        MITRETechnique(
            technique_id="T1598",
            technique_name="Phishing for Information",
            tactics=[MITRETactic.RECONNAISSANCE],
        ),
    ],
    
    "H_RE_003": [  # opportunistic_scanning
        MITRETechnique(
            technique_id="T1595",
            technique_name="Active Scanning",
            tactics=[MITRETactic.RECONNAISSANCE],
            subtechniques=["T1595.001", "T1595.002", "T1595.003"],
        ),
    ],
    
    # INITIAL_ACCESS
    "H_IA_001": [  # spearphishing_execution
        MITRETechnique(
            technique_id="T1566",
            technique_name="Phishing",
            tactics=[MITRETactic.INITIAL_ACCESS],
            subtechniques=["T1566.001", "T1566.002"],  # Email, spearphishing
        ),
    ],
    
    "H_IA_002": [  # exploitation_public_facing
        MITRETechnique(
            technique_id="T1190",
            technique_name="Exploit Public-Facing Application",
            tactics=[MITRETactic.INITIAL_ACCESS],
        ),
    ],
    
    "H_IA_003": [  # supply_chain_compromise
        MITRETechnique(
            technique_id="T1195",
            technique_name="Supply Chain Compromise",
            tactics=[MITRETactic.INITIAL_ACCESS],
            subtechniques=["T1195.001", "T1195.002", "T1195.003"],
        ),
    ],
    
    # EXECUTION
    "H_EX_001": [  # command_line_abuse
        MITRETechnique(
            technique_id="T1059",
            technique_name="Command and Scripting Interpreter",
            tactics=[MITRETactic.EXECUTION],
            subtechniques=["T1059.001", "T1059.003"],  # Cmd, Powershell
        ),
    ],
    
    "H_EX_002": [  # scheduled_task_abuse
        MITRETechnique(
            technique_id="T1053",
            technique_name="Scheduled Task/Job",
            tactics=[MITRETactic.EXECUTION, MITRETactic.PERSISTENCE],
            subtechniques=["T1053.005", "T1053.006"],  # Windows Task, cron
        ),
    ],
    
    "H_EX_003": [  # powershell_living_off_the_land
        MITRETechnique(
            technique_id="T1059",
            technique_name="Command and Scripting Interpreter",
            tactics=[MITRETactic.EXECUTION],
            subtechniques=["T1059.001"],  # PowerShell
        ),
        MITRETechnique(
            technique_id="T1140",
            technique_name="Deobfuscate/Decode Files or Information",
            tactics=[MITRETactic.DEFENSE_EVASION],
        ),
    ],
    
    # PERSISTENCE
    "H_PE_001": [  # single_persistence
        MITRETechnique(
            technique_id="T1547",
            technique_name="Boot or Logon Autostart Execution",
            tactics=[MITRETactic.PERSISTENCE, MITRETactic.PRIVILEGE_ESCALATION],
            subtechniques=["T1547.001"],  # Registry run keys
        ),
    ],
    
    "H_PE_002": [  # multi_mechanism_persistence
        MITRETechnique(
            technique_id="T1547",
            technique_name="Boot or Logon Autostart Execution",
            tactics=[MITRETactic.PERSISTENCE],
        ),
        MITRETechnique(
            technique_id="T1053",
            technique_name="Scheduled Task/Job",
            tactics=[MITRETactic.PERSISTENCE],
        ),
        MITRETechnique(
            technique_id="T1543",
            technique_name="Create or Modify System Process",
            tactics=[MITRETactic.PERSISTENCE],
            subtechniques=["T1543.004"],  # Windows Service
        ),
    ],
    
    "H_PE_003": [  # redundant_persistence
        MITRETechnique(
            technique_id="T1547",
            technique_name="Boot or Logon Autostart Execution",
            tactics=[MITRETactic.PERSISTENCE],
        ),
        MITRETechnique(
            technique_id="T1098",
            technique_name="Account Manipulation",
            tactics=[MITRETactic.PERSISTENCE],
        ),
    ],
    
    # PRIVILEGE_ESCALATION
    "H_PE_004": [  # token_impersonation
        MITRETechnique(
            technique_id="T1134",
            technique_name="Access Token Manipulation",
            tactics=[MITRETactic.PRIVILEGE_ESCALATION, MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1134.001", "T1134.003"],  # Token impersonation, make and impersonate
        ),
    ],
    
    "H_PE_005": [  # exploit_vulnerability
        MITRETechnique(
            technique_id="T1068",
            technique_name="Exploitation for Privilege Escalation",
            tactics=[MITRETactic.PRIVILEGE_ESCALATION],
        ),
    ],
    
    "H_PE_006": [  # kerberoasting
        MITRETechnique(
            technique_id="T1558",
            technique_name="Steal or Forge Kerberos Tickets",
            tactics=[MITRETactic.CREDENTIAL_ACCESS],
            subtechniques=["T1558.003"],  # Kerberoasting
        ),
    ],
    
    # DEFENSE_EVASION
    "H_DE_001": [  # log_fabrication
        MITRETechnique(
            technique_id="T1562",
            technique_name="Impair Defenses",
            tactics=[MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1562.002"],  # Clear Windows event logs
        ),
        MITRETechnique(
            technique_id="T1070",
            technique_name="Indicator Removal",
            tactics=[MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1070.001"],  # Clear logs
        ),
    ],
    
    "H_DE_002": [  # log_deletion_after_exfil
        MITRETechnique(
            technique_id="T1070",
            technique_name="Indicator Removal",
            tactics=[MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1070.001"],  # Clear logs
        ),
    ],
    
    "H_DE_003": [  # anti_forensics_preparation
        MITRETechnique(
            technique_id="T1070",
            technique_name="Indicator Removal",
            tactics=[MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1070.006"],  # Timestomp
        ),
    ],
    
    "H_SE_001": [  # false_security_theater (NUEVO)
        MITRETechnique(
            technique_id="T1036",
            technique_name="Masquerading",
            tactics=[MITRETactic.DEFENSE_EVASION],
            subtechniques=["T1036.006"],  # Match legitimate name/location
        ),
        MITRETechnique(
            technique_id="T1078",
            technique_name="Valid Accounts",
            tactics=[MITRETactic.DEFENSE_EVASION, MITRETactic.PERSISTENCE],
        ),
    ],
    
    # CREDENTIAL_ACCESS
    "H_CA_001": [  # credential_dumping
        MITRETechnique(
            technique_id="T1110",
            technique_name="Brute Force",
            tactics=[MITRETactic.CREDENTIAL_ACCESS],
        ),
        MITRETechnique(
            technique_id="T1187",
            technique_name="Forced Authentication",
            tactics=[MITRETactic.CREDENTIAL_ACCESS],
        ),
    ],
    
    "H_CA_002": [  # brute_force
        MITRETechnique(
            technique_id="T1110",
            technique_name="Brute Force",
            tactics=[MITRETactic.CREDENTIAL_ACCESS],
            subtechniques=["T1110.001", "T1110.003"],  # Password guessing, password spraying
        ),
    ],
    
    "H_CA_003": [  # keylogger_deployment
        MITRETechnique(
            technique_id="T1056",
            technique_name="Input Capture",
            tactics=[MITRETactic.COLLECTION, MITRETactic.CREDENTIAL_ACCESS],
            subtechniques=["T1056.004"],  # Keylogging
        ),
    ],
    
    # LATERAL_MOVEMENT
    "H_LM_001": [  # pass_the_hash
        MITRETechnique(
            technique_id="T1550",
            technique_name="Use Alternate Authentication Material",
            tactics=[MITRETactic.LATERAL_MOVEMENT],
            subtechniques=["T1550.002"],  # Pass the hash
        ),
    ],
    
    # COLLECTION
    "H_CO_001": [  # data_staging_for_exfil
        MITRETechnique(
            technique_id="T1123",
            technique_name="Audio Capture",
            tactics=[MITRETactic.COLLECTION],
        ),
        MITRETechnique(
            technique_id="T1119",
            technique_name="Automated Exfiltration",
            tactics=[MITRETactic.EXFILTRATION],
        ),
    ],
    
    "H_CO_002": [  # clipboard_and_screen_capture
        MITRETechnique(
            technique_id="T1115",
            technique_name="Clipboard Data",
            tactics=[MITRETactic.COLLECTION],
        ),
        MITRETechnique(
            technique_id="T1113",
            technique_name="Screen Capture",
            tactics=[MITRETactic.COLLECTION],
        ),
    ],
    
    "H_CO_003": [  # audio_and_video_surveillance
        MITRETechnique(
            technique_id="T1123",
            technique_name="Audio Capture",
            tactics=[MITRETactic.COLLECTION],
        ),
        MITRETechnique(
            technique_id="T1125",
            technique_name="Video Capture",
            tactics=[MITRETactic.COLLECTION],
        ),
    ],
    
    # COMMAND_AND_CONTROL
    "H_C2_001": [  # domain_fronting_beacon
        MITRETechnique(
            technique_id="T1071",
            technique_name="Application Layer Protocol",
            tactics=[MITRETactic.COMMAND_AND_CONTROL],
            subtechniques=["T1071.001"],  # Web Protocols
        ),
    ],
    
    "H_C2_002": [  # dns_tunnel_c2
        MITRETechnique(
            technique_id="T1071",
            technique_name="Application Layer Protocol",
            tactics=[MITRETactic.COMMAND_AND_CONTROL],
            subtechniques=["T1071.004"],  # DNS
        ),
    ],
    
    "H_C2_003": [  # dead_drop_resolver
        MITRETechnique(
            technique_id="T1008",
            technique_name="Fallback Channels",
            tactics=[MITRETactic.COMMAND_AND_CONTROL],
        ),
    ],
    
    # EXFILTRATION
    "H_EX_001": [  # bulk_data_exfiltration
        MITRETechnique(
            technique_id="T1030",
            technique_name="Data Transfer Size Limits",
            tactics=[MITRETactic.EXFILTRATION],
        ),
        MITRETechnique(
            technique_id="T1020",
            technique_name="Automated Exfiltration",
            tactics=[MITRETactic.EXFILTRATION],
        ),
    ],
    
    # IMPACT
    "H_IM_001": [  # ransomware_deployment
        MITRETechnique(
            technique_id="T1486",
            technique_name="Data Encrypted for Impact",
            tactics=[MITRETactic.IMPACT],
        ),
    ],
    
    "H_IM_002": [  # wiper_destruction
        MITRETechnique(
            technique_id="T1561",
            technique_name="Disk Wipe",
            tactics=[MITRETactic.IMPACT],
            subtechniques=["T1561.001"],  # Disk content wipe
        ),
        MITRETechnique(
            technique_id="T1531",
            technique_name="Account Access Removal",
            tactics=[MITRETactic.IMPACT],
        ),
    ],
    
    "H_IM_003": [  # defacement_and_humiliation
        MITRETechnique(
            technique_id="T1491",
            technique_name="Defacement",
            tactics=[MITRETactic.IMPACT],
            subtechniques=["T1491.001"],  # Internal defacement
        ),
    ],
}


# ============================================================================
# CLUSTERING SEMÁNTICO (Intent Clusters)
# ============================================================================

@dataclass
class IntentCluster:
    """Agrupa hipótesis por motivación común del atacante"""
    cluster_id: str  # "STEALTH", "FINANCIAL", "DISRUPTION", etc.
    cluster_name: str
    hypotheses: List[str]  # IDs de hipótesis en este cluster
    description: str
    attacker_rationale: str


INTENT_CLUSTERS: Dict[str, IntentCluster] = {
    "STEALTH": IntentCluster(
        cluster_id="STEALTH",
        cluster_name="Invisibilidad y Ocultamiento",
        hypotheses=[
            "H_RE_003",  # Escaneo no direccionado
            "H_DE_001",  # Log fabrication
            "H_DE_002",  # Log deletion after exfil
            "H_DE_003",  # Anti-forensics prep
            "H_SE_001",  # False security theater
            "H_EX_003",  # PowerShell LOTL
        ],
        description="Atacante prioriza no ser detectado. Imita normalidad, oculta huellas, simula defensas.",
        attacker_rationale="No quiero que sepas que estuve aquí.",
    ),
    
    "PERSISTENCE": IntentCluster(
        cluster_id="PERSISTENCE",
        cluster_name="Arraigo y Control Duradero",
        hypotheses=[
            "H_PE_001",  # Single persistence
            "H_PE_002",  # Multi persistence
            "H_PE_003",  # Redundant persistence
            "H_C2_001",  # Domain fronting beacon
            "H_C2_002",  # DNS tunnel
            "H_C2_003",  # Dead drop resolver
        ],
        description="Atacante establece múltiples mecanismos de reingreso. Planea estar aquí largo tiempo.",
        attacker_rationale="Quiero poder volver cuando quiera, por cualquier vector.",
    ),
    
    "EXFILTRATION": IntentCluster(
        cluster_id="EXFILTRATION",
        cluster_name="Robo de Datos",
        hypotheses=[
            "H_CA_001",  # Credential dumping
            "H_CA_002",  # Brute force
            "H_CA_003",  # Keylogger
            "H_CO_001",  # Data staging
            "H_CO_002",  # Screen + clipboard
            "H_CO_003",  # Audio surveillance
            "H_EX_001",  # Bulk exfiltration
        ],
        description="Atacante recolecta información sensible para robar. Acceso a credenciales, data.",
        attacker_rationale="Quiero sacar información de aquí sin que se den cuenta.",
    ),
    
    "DISRUPTION": IntentCluster(
        cluster_id="DISRUPTION",
        cluster_name="Sabotaje y Daño",
        hypotheses=[
            "H_IM_001",  # Ransomware
            "H_IM_002",  # Wiper destruction
            "H_IM_003",  # Defacement
        ],
        description="Atacante quiere destruir, cifrar o sabotear. No oculta su presencia.",
        attacker_rationale="Quiero causar el máximo daño posible, y que todos lo sepan.",
    ),
    
    "ESCALATION": IntentCluster(
        cluster_id="ESCALATION",
        cluster_name="Elevación de Privilegios",
        hypotheses=[
            "H_PE_004",  # Token impersonation
            "H_PE_005",  # Exploit vulnerability
            "H_PE_006",  # Kerberoasting
            "H_LM_001",  # Pass the hash
        ],
        description="Atacante busca más poder. Escalada desde usuario normal a admin/SYSTEM.",
        attacker_rationale="Necesito más permisos para hacer lo que quiero.",
    ),
}


# ============================================================================
# CLUSTERING CLASS
# ============================================================================

class MITREClusterer:
    """Agrupa hipótesis por MITRE tácticas e intención semántica"""
    
    def __init__(self):
        self.hypothesis_to_mitre = HYPOTHESIS_TO_MITRE
        self.intent_clusters = INTENT_CLUSTERS
    
    def get_mitre_techniques_for_hypothesis(self, hyp_id: str) -> List[MITRETechnique]:
        """Retorna técnicas MITRE para una hipótesis"""
        return self.hypothesis_to_mitre.get(hyp_id, [])
    
    def get_intent_cluster_for_hypothesis(self, hyp_id: str) -> IntentCluster | None:
        """Retorna el cluster de intención (STEALTH, PERSISTENCE, etc.) para una hipótesis"""
        for cluster in self.intent_clusters.values():
            if hyp_id in cluster.hypotheses:
                return cluster
        return None
    
    def cluster_by_tactic(self) -> Dict[MITRETactic, List[str]]:
        """Agrupa hipótesis por MITRE tactic"""
        tactic_to_hyps = {}
        for hyp_id, techniques in self.hypothesis_to_mitre.items():
            for tech in techniques:
                for tactic in tech.tactics:
                    if tactic not in tactic_to_hyps:
                        tactic_to_hyps[tactic] = []
                    if hyp_id not in tactic_to_hyps[tactic]:
                        tactic_to_hyps[tactic].append(hyp_id)
        return tactic_to_hyps
    
    def cluster_by_intent(self) -> Dict[str, List[str]]:
        """Agrupa hipótesis por intención semántica (STEALTH, PERSISTENCE, etc.)"""
        intent_to_hyps = {}
        for cluster in self.intent_clusters.values():
            intent_to_hyps[cluster.cluster_id] = cluster.hypotheses
        return intent_to_hyps
    
    def export_json(self) -> Dict:
        """Exporta clustering como JSON auditable"""
        return {
            "hypothesis_to_mitre": {
                hyp_id: [
                    {
                        "technique_id": tech.technique_id,
                        "technique_name": tech.technique_name,
                        "tactics": [t.value for t in tech.tactics],
                        "subtechniques": tech.subtechniques,
                    }
                    for tech in techniques
                ]
                for hyp_id, techniques in self.hypothesis_to_mitre.items()
            },
            "intent_clusters": {
                cluster_id: {
                    "name": cluster.cluster_name,
                    "hypotheses": cluster.hypotheses,
                    "description": cluster.description,
                }
                for cluster_id, cluster in self.intent_clusters.items()
            },
        }


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    clusterer = MITREClusterer()
    
    print("=" * 80)
    print("HITO 2.2 — MITRE ATT&CK CLUSTERING")
    print("=" * 80)
    
    # Ejemplo 1: Una hipótesis
    print("\n✅ Ejemplo: H_SE_001 (False Security Theater)")
    techniques = clusterer.get_mitre_techniques_for_hypothesis("H_SE_001")
    print(f"   MITRE Techniques:")
    for tech in techniques:
        print(f"     • {tech.technique_id}: {tech.technique_name}")
        print(f"       Tactics: {', '.join([t.value for t in tech.tactics])}")
    
    intent_cluster = clusterer.get_intent_cluster_for_hypothesis("H_SE_001")
    if intent_cluster:
        print(f"   Intent Cluster: {intent_cluster.cluster_id} ({intent_cluster.cluster_name})")
        print(f"   Rationale: {intent_cluster.attacker_rationale}")
    
    # Ejemplo 2: Clustering por tactic
    print("\n✅ Clustering por MITRE Tactic:")
    tactic_clusters = clusterer.cluster_by_tactic()
    for tactic in sorted(tactic_clusters.keys(), key=lambda t: t.value):
        hyps = tactic_clusters[tactic]
        print(f"   {tactic.value}: {len(hyps)} hipótesis")
        for hyp in hyps[:3]:
            print(f"      • {hyp}")
        if len(hyps) > 3:
            print(f"      ... y {len(hyps)-3} más")
    
    # Ejemplo 3: Clustering por intención
    print("\n✅ Clustering por Intent Semántico:")
    intent_clusters = clusterer.cluster_by_intent()
    for intent_id, hyps in intent_clusters.items():
        cluster = clusterer.intent_clusters[intent_id]
        print(f"   {cluster.cluster_name} ({intent_id}): {len(hyps)} hipótesis")
        print(f"      Rationale: {cluster.attacker_rationale}")
    
    print("\n✅ JSON Export ready for auditing")
    print(f"   Keys: hypothesis_to_mitre, intent_clusters")
    print(f"   Deterministic: ✓ (no ML, tablas explícitas)")
    print(f"   Falsable: ✓ (cada hipótesis tiene técnicas MITRE verificables)")
