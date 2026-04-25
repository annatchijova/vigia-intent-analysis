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
vigia/tools/mitre_mapping.py
=============================
VIGÍA — MITRE ATT&CK Intelligence Hub

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Centralized TTP mapping para CAIE, Planner, y STIX export.

PURPOSE
-------
Resuelve el hallazgo crítico "Mapping vacío" centralizando todo el
conocimiento TTP. Garantiza que CAIE y Planner usen mappings MITRE ATT&CK
consistentes para interoperabilidad STIX 2.1 con OpenCTI, SIFT y otras
plataformas DFIR.

NOTA DE EXTRACCIÓN
------------------
Este archivo fue extraído desde mitre_mapping.py (raíz del proyecto) donde
el código estaba encerrado en un string Python (`mitre_mapping_code = '''...'''`)
y por lo tanto NUNCA era ejecutable como módulo.
Diagnóstico: 20-abr-2026 — Claude (Systems Integration Engineer).

FEATURES
--------
* Master Dictionary: evidence_type → MITRE_TTP_ID con versioning
* Dynamic Severity: base_severity + spoofability_score por TTP
* STIX Wrapper: to_stix_sdo() convierte artifacts VIGÍA a STIX SDOs válidos
* Confidence Scoring: confianza TTP basada en reliability de evidencia
* TPM/Hardware trust: spoofability 0.05 (prácticamente no falsificable)

REFERENCIAS
-----------
* MITRE ATT&CK Enterprise v14.1
* STIX 2.1 Specification (OASIS)
* VIGÍA Audit PDF: Spoofability table (Memory=0.1, Logs=0.5, IP=0.8)
* ChatGPT vs Kimi debate: TPM_attestation con spoof bajo = evidencia fuerte
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Final

from vigia.security import _utcnow, audit_logger


# ---------------------------------------------------------------------------
# MITRE ATT&CK Enterprise v14.1 — Tactics
# ---------------------------------------------------------------------------

class AttackTactic(str, Enum):
    """MITRE ATT&CK Tactics (columnas de la matriz)."""
    RECONNAISSANCE = "TA0043"
    RESOURCE_DEVELOPMENT = "TA0042"
    INITIAL_ACCESS = "TA0001"
    EXECUTION = "TA0002"
    PERSISTENCE = "TA0003"
    PRIVILEGE_ESCALATION = "TA0004"
    DEFENSE_EVASION = "TA0005"
    CREDENTIAL_ACCESS = "TA0006"
    DISCOVERY = "TA0007"
    LATERAL_MOVEMENT = "TA0008"
    COLLECTION = "TA0009"
    COMMAND_AND_CONTROL = "TA0011"
    EXFILTRATION = "TA0010"
    IMPACT = "TA0040"


@dataclass(frozen=True)
class TTPMetadata:
    """
    Metadata para una técnica MITRE ATT&CK.

    Fields
    ------
    technique_id   : MITRE TTP ID (e.g., "T1055")
    name           : Nombre legible
    tactics        : Tácticas a las que pertenece
    platforms      : Plataformas objetivo
    base_severity  : Severidad intrínseca (0.0-1.0)
    spoofability_score : Facilidad de falsificación (0.0=difícil, 1.0=trivial)
    evidence_types : evidence_types internos de VIGÍA que mapean a esta TTP
    description    : Descripción MITRE
    url            : Link directo a MITRE ATT&CK
    version        : Versión ATT&CK validada
    """
    technique_id: str
    name: str
    tactics: tuple[str, ...]
    platforms: tuple[str, ...]
    base_severity: float
    spoofability_score: float
    evidence_types: tuple[str, ...]
    description: str
    url: str
    version: str = "14.1"

    def __post_init__(self) -> None:
        if not 0.0 <= self.base_severity <= 1.0:
            raise ValueError(
                f"base_severity must be in [0.0, 1.0], got {self.base_severity}"
            )
        if not 0.0 <= self.spoofability_score <= 1.0:
            raise ValueError(
                f"spoofability_score must be in [0.0, 1.0], got {self.spoofability_score}"
            )


# ---------------------------------------------------------------------------
# MASTER TTP DICTIONARY
# Mapping centralizado: VIGÍA evidence types → MITRE ATT&CK TTPs
# Spoofability actualizada con TPM/hardware trust (hallazgo del debate)
# ---------------------------------------------------------------------------

MASTER_TTP_DICTIONARY: Final[dict[str, TTPMetadata]] = {

    # --- Memory / Kernel (MUY difíciles de falsificar) ---

    "T1055": TTPMetadata(
        technique_id="T1055",
        name="Process Injection",
        tactics=(AttackTactic.PRIVILEGE_ESCALATION, AttackTactic.DEFENSE_EVASION, AttackTactic.EXECUTION),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.85,
        spoofability_score=0.10,
        evidence_types=("memory_process", "kernel_structure", "lsass_session"),
        description="Adversaries may inject code into processes to evade defenses and elevate privileges.",
        url="https://attack.mitre.org/techniques/T1055",
    ),

    "T1218": TTPMetadata(
        technique_id="T1218",
        name="Signed Binary Proxy Execution",
        tactics=(AttackTactic.DEFENSE_EVASION, AttackTactic.EXECUTION),
        platforms=("Windows",),
        base_severity=0.75,
        spoofability_score=0.30,
        evidence_types=("memory_process", "prefetch", "registry_key"),
        description="Adversaries may use signed binaries to proxy execution of malicious payloads.",
        url="https://attack.mitre.org/techniques/T1218",
    ),

    "T1497": TTPMetadata(
        technique_id="T1497",
        name="Virtualization/Sandbox Evasion",
        tactics=(AttackTactic.DEFENSE_EVASION, AttackTactic.DISCOVERY),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.80,
        spoofability_score=0.25,
        evidence_types=("memory_process", "cultural_marker", "user_agent"),
        description="Adversaries may employ various means to detect and avoid virtualization/sandbox environments.",
        url="https://attack.mitre.org/techniques/T1497",
    ),

    # --- Hardware Trust (MÍNIMA spoofability — hallazgo debate ChatGPT vs Kimi) ---

    "T1553.006": TTPMetadata(
        technique_id="T1553.006",
        name="Subvert Trust Controls: Code Signing Policy Modification",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "macOS"),
        base_severity=0.90,
        spoofability_score=0.05,   # TPM_attestation: prácticamente no falsificable
        evidence_types=("TPM_attestation", "kernel_structure"),
        description="TPM attestation violations — hardware trust anchor breach.",
        url="https://attack.mitre.org/techniques/T1553/006",
    ),

    # --- File System / Timestamps (moderada spoofability) ---

    "T1036": TTPMetadata(
        technique_id="T1036",
        name="Masquerading",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.60,
        spoofability_score=0.50,
        evidence_types=("file_timestamp", "file_hash", "document_visual", "document_geometry"),
        description="Adversaries may attempt to masquerade artifacts as legitimate entities.",
        url="https://attack.mitre.org/techniques/T1036",
    ),

    "T1036.005": TTPMetadata(
        technique_id="T1036.005",
        name="Masquerading: Match Legitimate Name or Location",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.65,
        spoofability_score=0.40,
        evidence_types=("cultural_marker", "file_hash", "log_entry"),
        description="Adversaries may match legitimate resource names to masquerade malicious artifacts.",
        url="https://attack.mitre.org/techniques/T1036/005",
    ),

    "T1036.004": TTPMetadata(
        technique_id="T1036.004",
        name="Masquerade Task or Service",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.70,
        spoofability_score=0.35,
        evidence_types=("document_visual", "document_geometry", "memory_process"),
        description="Adversaries may masquerade malicious services or tasks as legitimate ones.",
        url="https://attack.mitre.org/techniques/T1036/004",
    ),

    "T1070.006": TTPMetadata(
        technique_id="T1070.006",
        name="Indicator Removal: Timestomp",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.70,
        spoofability_score=0.70,
        evidence_types=("file_timestamp", "usn_journal", "log_entry"),
        description="Adversaries may modify file time attributes to hide modifications.",
        url="https://attack.mitre.org/techniques/T1070/006",
    ),

    "T1070.001": TTPMetadata(
        technique_id="T1070.001",
        name="Indicator Removal: Clear Windows Event Logs",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows",),
        base_severity=0.80,
        spoofability_score=0.50,
        evidence_types=("log_entry", "hmac_audit_log"),
        description="Adversaries may clear Windows Event Logs to hide activity.",
        url="https://attack.mitre.org/techniques/T1070/001",
    ),

    "T1070.002": TTPMetadata(
        technique_id="T1070.002",
        name="Indicator Removal: Clear Linux or Mac System Logs",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Linux", "macOS"),
        base_severity=0.80,
        spoofability_score=0.50,
        evidence_types=("log_entry", "hmac_audit_log", "file_timestamp"),
        description="Temporal causality violation — logs cleared to hide impossible timeline.",
        url="https://attack.mitre.org/techniques/T1070/002",
    ),

    # --- Logs / Network (alta spoofability) ---

    "T1059": TTPMetadata(
        technique_id="T1059",
        name="Command and Scripting Interpreter",
        tactics=(AttackTactic.EXECUTION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.70,
        spoofability_score=0.45,
        evidence_types=("memory_process", "log_entry", "file_hash"),
        description="Adversaries may abuse command and script interpreters to execute commands.",
        url="https://attack.mitre.org/techniques/T1059",
    ),

    "T1564": TTPMetadata(
        technique_id="T1564",
        name="Hide Artifacts",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.65,
        spoofability_score=0.55,
        evidence_types=("file_timestamp", "registry_key", "log_entry"),
        description="Adversaries may attempt to hide artifacts associated with malicious behavior.",
        url="https://attack.mitre.org/techniques/T1564",
    ),

    "T1564.001": TTPMetadata(
        technique_id="T1564.001",
        name="Hide Artifacts: Hidden Files and Directories",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.60,
        spoofability_score=0.50,
        evidence_types=("file_timestamp", "usn_journal"),
        description="Adversaries may set files and directories to be hidden.",
        url="https://attack.mitre.org/techniques/T1564/001",
    ),

    "T1564.002": TTPMetadata(
        technique_id="T1564.002",
        name="Hide Artifacts: Run Virtual Instance",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.75,
        spoofability_score=0.40,
        evidence_types=("document_visual", "document_geometry", "file_hash"),
        description="Document forgery requiring technical skill — moderate spoofability.",
        url="https://attack.mitre.org/techniques/T1564/002",
    ),

    # --- IP / Network / Social (MUY alta spoofability) ---

    "T1566": TTPMetadata(
        technique_id="T1566",
        name="Phishing",
        tactics=(AttackTactic.INITIAL_ACCESS,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.75,
        spoofability_score=0.60,
        evidence_types=("document_visual", "document_geometry", "cultural_marker"),
        description="Adversaries may send phishing messages to gain access to victim systems.",
        url="https://attack.mitre.org/techniques/T1566",
    ),

    "T1566.003": TTPMetadata(
        technique_id="T1566.003",
        name="Phishing: Spearphishing via Service",
        tactics=(AttackTactic.INITIAL_ACCESS,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.80,
        spoofability_score=0.65,
        evidence_types=("document_visual", "cultural_marker", "log_entry"),
        description="Adversaries may send spearphishing messages via third-party services.",
        url="https://attack.mitre.org/techniques/T1566/003",
    ),

    "T1586": TTPMetadata(
        technique_id="T1586",
        name="Compromise Accounts",
        tactics=(AttackTactic.RESOURCE_DEVELOPMENT,),
        platforms=("PRE",),
        base_severity=0.70,
        spoofability_score=0.85,
        evidence_types=("cultural_marker", "ip_geolocation", "user_agent", "log_entry"),
        description="Adversaries may compromise accounts to use in malicious operations.",
        url="https://attack.mitre.org/techniques/T1586",
    ),

    "T1585.001": TTPMetadata(
        technique_id="T1585.001",
        name="Establish Accounts: Social Media Accounts",
        tactics=(AttackTactic.RESOURCE_DEVELOPMENT,),
        platforms=("PRE",),
        base_severity=0.60,
        spoofability_score=0.90,
        evidence_types=("cultural_marker", "user_agent", "ip_geolocation"),
        description="Adversaries may create social media accounts for malicious operations.",
        url="https://attack.mitre.org/techniques/T1585/001",
    ),

    "T1498": TTPMetadata(
        technique_id="T1498",
        name="Network Denial of Service",
        tactics=(AttackTactic.IMPACT,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.85,
        spoofability_score=0.20,
        evidence_types=("log_entry", "dns_record", "ip_geolocation"),
        description="Adversaries may perform Network Denial of Service attacks.",
        url="https://attack.mitre.org/techniques/T1498",
    ),

    # --- Cloud / Multi-tenant ---

    "T1078.004": TTPMetadata(
        technique_id="T1078.004",
        name="Valid Accounts: Cloud Accounts",
        tactics=(AttackTactic.PERSISTENCE, AttackTactic.PRIVILEGE_ESCALATION, AttackTactic.INITIAL_ACCESS),
        platforms=("IaaS", "Azure AD", "Google Workspace", "SaaS"),
        base_severity=0.80,
        spoofability_score=0.60,
        evidence_types=("cloud_metadata", "kubernetes_audit_log", "log_entry"),
        description="Cloud vs on-prem account discrepancy — CLOUD_VS_ONPREM fracture.",
        url="https://attack.mitre.org/techniques/T1078/004",
    ),

    "T1611": TTPMetadata(
        technique_id="T1611",
        name="Escape to Host",
        tactics=(AttackTactic.PRIVILEGE_ESCALATION,),
        platforms=("Containers",),
        base_severity=0.90,
        spoofability_score=0.15,
        evidence_types=("kubernetes_audit_log", "memory_process", "kernel_structure"),
        description="Multi-tenant isolation breach — container escape to host.",
        url="https://attack.mitre.org/techniques/T1611",
    ),

    "T1006": TTPMetadata(
        technique_id="T1006",
        name="Direct Volume Access",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows",),
        base_severity=0.85,
        spoofability_score=0.20,
        evidence_types=("usn_journal", "file_timestamp", "memory_process"),
        description="Live response vs disk discrepancy — direct volume bypass.",
        url="https://attack.mitre.org/techniques/T1006",
    ),

    "T1559": TTPMetadata(
        technique_id="T1559",
        name="Inter-Process Communication",
        tactics=(AttackTactic.EXECUTION,),
        platforms=("Windows",),
        base_severity=0.75,
        spoofability_score=0.30,
        evidence_types=("memory_process", "kernel_structure"),
        description="Cryptographic inconsistency in IPC channel.",
        url="https://attack.mitre.org/techniques/T1559",
    ),

    "T1565.001": TTPMetadata(
        technique_id="T1565.001",
        name="Data Manipulation: Stored Data Manipulation",
        tactics=(AttackTactic.IMPACT,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.80,
        spoofability_score=0.40,
        evidence_types=("log_entry", "hmac_audit_log", "file_hash"),
        description="Log vs memory mismatch — stored data manipulation.",
        url="https://attack.mitre.org/techniques/T1565/001",
    ),

    "T1562.001": TTPMetadata(
        technique_id="T1562.001",
        name="Impair Defenses: Disable or Modify Tools",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.85,
        spoofability_score=0.35,
        evidence_types=("memory_process", "registry_key", "log_entry"),
        description="Verdict conflict — defensive tools tampered.",
        url="https://attack.mitre.org/techniques/T1562/001",
    ),

    "T1585": TTPMetadata(
        technique_id="T1585",
        name="Establish Accounts",
        tactics=(AttackTactic.RESOURCE_DEVELOPMENT,),
        platforms=("PRE",),
        base_severity=0.60,
        spoofability_score=0.88,
        evidence_types=("cultural_marker", "ip_geolocation"),
        description="False attribution — accounts created for false flag pattern.",
        url="https://attack.mitre.org/techniques/T1585",
    ),

    "T1565": TTPMetadata(
        technique_id="T1565",
        name="Data Manipulation",
        tactics=(AttackTactic.IMPACT,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.80,
        spoofability_score=0.45,
        evidence_types=("network_traffic", "log_entry", "dns_record"),
        description="Network vs host inconsistency — data manipulation at network layer.",
        url="https://attack.mitre.org/techniques/T1565",
    ),
}


# ---------------------------------------------------------------------------
# REVERSE LOOKUP: Evidence Type → TTP IDs
# ---------------------------------------------------------------------------

EVIDENCE_TYPE_TO_TTP: Final[dict[str, tuple[str, ...]]] = {
    "memory_process":        ("T1055", "T1218", "T1497", "T1059", "T1036.004", "T1562.001", "T1559"),
    "kernel_structure":      ("T1055", "T1553.006", "T1611"),
    "lsass_session":         ("T1055", "T1218"),
    "TPM_attestation":       ("T1553.006",),          # hardware trust — spoof casi imposible
    "file_timestamp":        ("T1036", "T1070.006", "T1564", "T1564.001", "T1006"),
    "file_hash":             ("T1036", "T1059", "T1564.002", "T1565.001"),
    "document_visual":       ("T1036", "T1566", "T1564.002", "T1036.004", "T1566.003"),
    "document_geometry":     ("T1036", "T1566", "T1564.002", "T1036.004", "T1566.003"),
    "cultural_marker":       ("T1036.005", "T1497", "T1586", "T1566", "T1585.001", "T1566.003", "T1585"),
    "log_entry":             ("T1036.005", "T1070.006", "T1564", "T1059", "T1498", "T1070.001",
                              "T1070.002", "T1566.003", "T1565.001", "T1562.001"),
    "ip_geolocation":        ("T1586", "T1498", "T1585.001", "T1585"),
    "user_agent":            ("T1497", "T1586", "T1585.001"),
    "usn_journal":           ("T1070.006", "T1564.001", "T1006"),
    "registry_key":          ("T1218", "T1564", "T1562.001"),
    "prefetch":              ("T1218",),
    "dns_record":            ("T1498", "T1565"),
    "hmac_audit_log":        ("T1070.001", "T1070.002", "T1565.001"),
    "cloud_metadata":        ("T1078.004",),
    "kubernetes_audit_log":  ("T1078.004", "T1611"),
    "hardware_serial":       ("T1553.006",),
    "eBPF_trace":            ("T1055", "T1611"),
    "network_traffic":       ("T1565", "T1498"),
}

# Validación en import: todas las TTPs referenciadas existen en MASTER_TTP_DICTIONARY
_all_referenced_ttps: set[str] = set()
for _ttps in EVIDENCE_TYPE_TO_TTP.values():
    _all_referenced_ttps.update(_ttps)
_missing_ttps = _all_referenced_ttps - set(MASTER_TTP_DICTIONARY.keys())
if _missing_ttps:
    import warnings
    warnings.warn(
        f"[mitre_mapping] TTPs referenciadas sin metadata: {_missing_ttps}",
        RuntimeWarning,
        stacklevel=1,
    )


# ---------------------------------------------------------------------------
# STIX 2.1 Domain Object Wrapper
# ---------------------------------------------------------------------------

class STIXObjectType(str, Enum):
    """STIX 2.1 Object Types."""
    ATTACK_PATTERN = "attack-pattern"
    INDICATOR = "indicator"
    OBSERVED_DATA = "observed-data"
    TOOL = "tool"
    VULNERABILITY = "vulnerability"
    IDENTITY = "identity"
    REPORT = "report"


@dataclass
class STIXDomainObject:
    """Representa un STIX 2.1 Domain Object (SDO)."""
    type: str
    id: str
    created: str
    modified: str
    labels: list[str] = field(default_factory=list)
    created_by_ref: str | None = None
    revoked: bool = False
    confidence: int = 0
    lang: str = "en"
    external_references: list[dict] = field(default_factory=list)
    object_marking_refs: list[str] = field(default_factory=list)
    granular_markings: list[dict] = field(default_factory=list)
    name: str | None = None
    description: str | None = None
    pattern: str | None = None
    pattern_type: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    kill_chain_phases: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "spec_version": "2.1",
            "id": self.id,
            "created": self.created,
            "modified": self.modified,
        }
        if self.labels:
            result["labels"] = self.labels
        if self.created_by_ref:
            result["created_by_ref"] = self.created_by_ref
        if self.revoked:
            result["revoked"] = True
        if self.confidence > 0:
            result["confidence"] = self.confidence
        if self.lang != "en":
            result["lang"] = self.lang
        if self.external_references:
            result["external_references"] = self.external_references
        if self.object_marking_refs:
            result["object_marking_refs"] = self.object_marking_refs
        if self.granular_markings:
            result["granular_markings"] = self.granular_markings
        if self.name:
            result["name"] = self.name
        if self.description:
            result["description"] = self.description
        if self.pattern:
            result["pattern"] = self.pattern
            result["pattern_type"] = self.pattern_type or "stix"
        if self.valid_from:
            result["valid_from"] = self.valid_from
        if self.valid_until:
            result["valid_until"] = self.valid_until
        if self.kill_chain_phases:
            result["kill_chain_phases"] = self.kill_chain_phases
        return result

    def to_json(self, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Core Functions (importadas por CAIE y Planner)
# ---------------------------------------------------------------------------

def get_ttp_metadata(technique_id: str) -> TTPMetadata | None:
    """Retrieve metadata para una TTP MITRE ATT&CK."""
    return MASTER_TTP_DICTIONARY.get(technique_id)


def get_ttps_for_evidence_type(evidence_type: str) -> tuple[str, ...]:
    """Get todas las TTPs asociadas a un evidence_type de VIGÍA."""
    return EVIDENCE_TYPE_TO_TTP.get(evidence_type, ())


def calculate_ttp_confidence(
    technique_id: str,
    evidence_reliability: float,
    detection_method: str,
) -> float:
    """
    Calcula confidence score para la detección de una TTP.

    Formula: base_severity * evidence_reliability * method_reliability * (1 - spoofability)
    """
    ttp = get_ttp_metadata(technique_id)
    if not ttp:
        return 0.0

    method_reliability = {
        "memory_forensics": 0.95,
        "kernel_analysis":  0.90,
        "tpm_attestation":  0.98,
        "hmac_audit":       0.85,
        "ebpf_trace":       0.88,
        "file_system":      0.70,
        "network_logs":     0.60,
        "behavioral":       0.50,
        "heuristic":        0.40,
    }.get(detection_method, 0.50)

    confidence = (
        ttp.base_severity
        * evidence_reliability
        * method_reliability
        * (1.0 - ttp.spoofability_score)
    )
    return min(confidence, 0.99)


def get_spoofability_for_evidence_type(evidence_type: str) -> float:
    """
    Promedio de spoofability para un evidence_type a través de todas sus TTPs.
    Retorna 0.50 si no hay TTPs asociadas (moderado conservador).
    """
    ttps = get_ttps_for_evidence_type(evidence_type)
    if not ttps:
        return 0.50
    scores = [
        ttp.spoofability_score
        for ttp_id in ttps
        if (ttp := get_ttp_metadata(ttp_id)) is not None
    ]
    return sum(scores) / len(scores) if scores else 0.50


# ---------------------------------------------------------------------------
# STIX Builder Functions
# ---------------------------------------------------------------------------

def to_stix_sdo(
    artifact: dict[str, Any],
    technique_id: str,
    created_by: str = "identity--vigia-tool-v1",
    confidence: int | None = None,
) -> STIXDomainObject:
    """
    Convierte un artifact VIGÍA a un STIX 2.1 Domain Object.

    Args
    ----
    artifact    : dict con keys: evidence_type, description, timestamp, source_tool, raw_score
    technique_id: MITRE ATT&CK technique ID
    created_by  : STIX identity ID del tool creador
    confidence  : 0-100 (auto-calculado si None)
    """
    ttp = get_ttp_metadata(technique_id)
    if not ttp:
        raise ValueError(f"Unknown technique ID: {technique_id!r}")

    now = _utcnow()

    if confidence is None:
        evidence_reliability = float(artifact.get("raw_score", 0.5))
        detection_method = str(artifact.get("source_tool", "heuristic"))
        confidence = int(
            calculate_ttp_confidence(technique_id, evidence_reliability, detection_method) * 100
        )

    kill_chain_phases = [
        {
            "kill_chain_name": "mitre-attack",
            "phase_name": str(tactic).lower().replace("_", "-"),
        }
        for tactic in ttp.tactics
    ]

    external_refs = [
        {
            "source_name": "mitre-attack",
            "external_id": ttp.technique_id,
            "url": ttp.url,
            "description": f"MITRE ATT&CK {ttp.version}",
        }
    ]

    artifact_hash = hashlib.sha256(
        json.dumps(artifact, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]

    return STIXDomainObject(
        type=STIXObjectType.ATTACK_PATTERN,
        id=f"attack-pattern--{artifact_hash}",
        created=artifact.get("timestamp", now),
        modified=now,
        name=ttp.name,
        description=artifact.get("description", ttp.description),
        confidence=confidence,
        created_by_ref=created_by,
        labels=["vigia-detected", artifact.get("evidence_type", "unknown")],
        external_references=external_refs,
        kill_chain_phases=kill_chain_phases,
    )


def to_stix_indicator(
    artifact: dict[str, Any],
    pattern: str,
    technique_id: str,
    valid_days: int = 30,
) -> STIXDomainObject:
    """Crea un STIX Indicator object desde un artifact VIGÍA."""
    ttp = get_ttp_metadata(technique_id)
    now = _utcnow()
    valid_until = (
        datetime.now(timezone.utc) + timedelta(days=valid_days)
    ).isoformat()
    pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()[:16]

    return STIXDomainObject(
        type=STIXObjectType.INDICATOR,
        id=f"indicator--{pattern_hash}",
        created=artifact.get("timestamp", now),
        modified=now,
        name=f"VIGÍA: {ttp.name if ttp else technique_id}",
        description=artifact.get("description", ""),
        pattern=pattern,
        pattern_type="stix",
        valid_from=artifact.get("timestamp", now),
        valid_until=valid_until,
        confidence=int(artifact.get("raw_score", 0.5) * 100),
        labels=["malicious-activity", "vigia-indicator"],
        external_references=[
            {
                "source_name": "mitre-attack",
                "external_id": technique_id,
                "url": ttp.url if ttp else f"https://attack.mitre.org/techniques/{technique_id}",
            }
        ] if ttp else [],
    )


def create_stix_bundle(
    objects: list[STIXDomainObject],
    bundle_id: str | None = None,
) -> dict[str, Any]:
    """
    Crea un STIX 2.1 bundle desde múltiples SDOs.

    NOTA: usa json.dumps con sort_keys=True y separators=(",", ":") para
    canonical JSON (más determinístico entre entornos).
    """
    now = _utcnow()
    bundle = {
        "type": "bundle",
        "id": bundle_id or f"bundle--{uuid.uuid4()}",
        "spec_version": "2.1",
        "created": now,
        "objects": [obj.to_dict() for obj in objects],
    }
    # Audit log del bundle para trazabilidad forense
    bundle_hash = hashlib.sha256(
        json.dumps(bundle, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    audit_logger.log_info(
        event_type="STIX_BUNDLE_CREATED",
        tool="mitre_mapping.create_stix_bundle",
        message=f"bundle_id={bundle['id']} objects={len(objects)} sha256={bundle_hash[:16]}",
    )
    return bundle


def validate_stix_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Valida un STIX bundle por campos requeridos. Retorna (is_valid, errores)."""
    errors: list[str] = []
    if bundle.get("type") != "bundle":
        errors.append("Bundle type must be 'bundle'")
    if bundle.get("spec_version") != "2.1":
        errors.append("Spec version must be '2.1'")
    objects = bundle.get("objects", [])
    if not objects:
        errors.append("Bundle must contain at least one object")
    for i, obj in enumerate(objects):
        if not obj.get("id"):
            errors.append(f"Object {i} missing 'id'")
        if not obj.get("type"):
            errors.append(f"Object {i} missing 'type'")
        if not obj.get("created"):
            errors.append(f"Object {i} missing 'created'")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Export Functions (consumidas por CAIE y PeircePlanner)
# ---------------------------------------------------------------------------

def export_for_caie() -> dict[str, Any]:
    """
    Exporta TTP mappings en formato optimizado para consumo del CAIE.
    CAIE solo consume — no define TTPs.
    """
    return {
        "evidence_type_to_ttp": {
            et: list(ttps) for et, ttps in EVIDENCE_TYPE_TO_TTP.items()
        },
        "ttp_metadata": {
            ttp_id: {
                "name": meta.name,
                "base_severity": meta.base_severity,
                "spoofability_score": meta.spoofability_score,
                "tactics": list(meta.tactics),
            }
            for ttp_id, meta in MASTER_TTP_DICTIONARY.items()
        },
        "version": "14.1",
        "generated_at": _utcnow(),
    }


def export_for_planner() -> dict[str, list[str]]:
    """
    Exporta mapeo simplificado TTP → signal_type para PeircePlanner.
    El planner consume señales, no TTPs directamente.
    """
    _signal_map: dict[str, str] = {
        "memory_process":      "PROCESS_INJECTION_DETECTED",
        "document_visual":     "DIGITAL_PERFECTION_ANOMALY",
        "document_geometry":   "DOCUMENT_FORGERY",
        "cultural_marker":     "LINGUISTIC_CONTAGION",
        "log_entry":           "SIGNIFICANT_SILENCE",
        "file_timestamp":      "TIMESTAMP_MANIPULATION",
        "ip_geolocation":      "FALSE_FLAG_PATTERN",
        "TPM_attestation":     "HARDWARE_TRUST_ANCHOR",
        "kubernetes_audit_log":"MULTI_TENANT_ISOLATION_BREACH",
        "usn_journal":         "LIVE_RESPONSE_VS_DISK",
    }
    ttp_to_signals: dict[str, list[str]] = {}
    for ttp_id, meta in MASTER_TTP_DICTIONARY.items():
        signals = [
            _signal_map[et]
            for et in meta.evidence_types
            if et in _signal_map
        ]
        ttp_to_signals[ttp_id] = signals
    return ttp_to_signals
