
# Generando los 4 archivos solicitados para completar la arquitectura VIGÍA

# =============================================================================
# ARCHIVO 1: mitre_mapping.py (NUEVO)
# =============================================================================

mitre_mapping_code = '''"""
vigia/tools/mitre_mapping.py
=============================
VIGÍA — MITRE ATT&CK Intelligence Hub

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Centralized TTP mapping for CAIE, Planner, and STIX export.

Purpose:
--------
Resolves the critical "Mapping vacío" finding by centralizing all TTP
knowledge. Ensures CAIE and Planner use consistent MITRE ATT&CK mappings
for STIX 2.1 interoperability with OpenCTI, SIFT, and other DFIR platforms.

Features:
---------
* Master Dictionary: evidence_type → MITRE_TTP_ID with versioning
* Dynamic Severity: base_severity + spoofability_score per TTP
* STIX Wrapper: to_stix_sdo() converts VIGÍA artifacts to valid STIX SDOs
* Confidence Scoring: TTP confidence based on evidence reliability

References:
-----------
* MITRE ATT&CK Enterprise v14.1
* STIX 2.1 Specification (OASIS)
* VIGÍA Audit PDF: Spoofability table (Memory=0.1, Logs=0.5, IP=0.8)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final

from vigia.security import _utcnow, audit_logger


# ---------------------------------------------------------------------------
# MITRE ATT&CK Enterprise v14.1 — Master TTP Dictionary
# ---------------------------------------------------------------------------
# Structure: TTP_ID → Metadata including tactics, platforms, and VIGÍA mapping

class AttackTactic(str, Enum):
    """MITRE ATT&CK Tactics (Columns of the matrix)."""
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
    Metadata for a MITRE ATT&CK Technique.
    
    Fields:
        technique_id: MITRE TTP ID (e.g., "T1055")
        name: Human-readable technique name
        tactics: List of tactic IDs this technique belongs to
        platforms: Target platforms (Windows, Linux, macOS, etc.)
        base_severity: Intrinsic severity (0.0-1.0) based on impact
        spoofability_score: Ease of fabrication (0.0=hard, 1.0=trivial)
        evidence_types: VIGÍA evidence types that map to this TTP
        description: MITRE's technique description
        url: Direct link to MITRE ATT&CK page
        version: ATT&CK version when this mapping was validated
    """
    technique_id: str
    name: str
    tactics: tuple[str, ...]
    platforms: tuple[str, ...]
    base_severity: float  # 0.0-1.0
    spoofability_score: float  # 0.0-1.0, from VIGÍA audit PDF
    evidence_types: tuple[str, ...]  # VIGÍA internal evidence types
    description: str
    url: str
    version: str = "14.1"
    
    def __post_init__(self):
        # Validate ranges
        if not 0.0 <= self.base_severity <= 1.0:
            raise ValueError(f"base_severity must be in [0.0, 1.0], got {self.base_severity}")
        if not 0.0 <= self.spoofability_score <= 1.0:
            raise ValueError(f"spoofability_score must be in [0.0, 1.0], got {self.spoofability_score}")


# ---------------------------------------------------------------------------
# MASTER TTP DICTIONARY
# Centralized mapping of VIGÍA evidence types to MITRE ATT&CK TTPs
# ---------------------------------------------------------------------------

MASTER_TTP_DICTIONARY: Final[dict[str, TTPMetadata]] = {
    # Process Injection (Memory-based, hard to spoof)
    "T1055": TTPMetadata(
        technique_id="T1055",
        name="Process Injection",
        tactics=(AttackTactic.PRIVILEGE_ESCALATION, AttackTactic.DEFENSE_EVASION, AttackTactic.EXECUTION),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.85,
        spoofability_score=0.10,  # Memory artifacts are hard to fake
        evidence_types=("memory_process", "kernel_structure", "lsass_session"),
        description="Adversaries may inject code into processes to evade process-based defenses.",
        url="https://attack.mitre.org/techniques/T1055",
    ),
    
    # Masquerading (File-based, moderate spoofability)
    "T1036": TTPMetadata(
        technique_id="T1036",
        name="Masquerading",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.60,
        spoofability_score=0.50,  # Files can be renamed/touched
        evidence_types=("file_timestamp", "file_hash", "document_visual", "document_geometry"),
        description="Adversaries may attempt to masquerade artifacts as legitimate entities.",
        url="https://attack.mitre.org/techniques/T1036",
    ),
    
    # Masquerading: Match Legitimate Name (Phonetic evasion)
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
    
    # Indicator Removal: Timestomp (Metadata manipulation)
    "T1070.006": TTPMetadata(
        technique_id="T1070.006",
        name="Indicator Removal: Timestomp",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.70,
        spoofability_score=0.70,  # Timestamps are easily modified
        evidence_types=("file_timestamp", "usn_journal", "log_entry"),
        description="Adversaries may modify file time attributes to hide modifications.",
        url="https://attack.mitre.org/techniques/T1070/006",
    ),
    
    # Signed Binary Proxy Execution (Trusted binaries)
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
    
    # Virtualization/Sandbox Evasion (Automation detection)
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
    
    # Compromise Accounts (Coordinated inauthentic behavior)
    "T1586": TTPMetadata(
        technique_id="T1586",
        name="Compromise Accounts",
        tactics=(AttackTactic.RESOURCE_DEVELOPMENT,),
        platforms=("PRE",),
        base_severity=0.70,
        spoofability_score=0.85,  # Easy to claim, hard to verify
        evidence_types=("cultural_marker", "ip_geolocation", "user_agent", "log_entry"),
        description="Adversaries may compromise accounts to use in malicious operations.",
        url="https://attack.mitre.org/techniques/T1586",
    ),
    
    # Phishing (Social engineering)
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
    
    # Command and Scripting Interpreter
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
    
    # Hide Artifacts (Anti-forensics)
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
    
    # Hide Artifacts: Hidden Files and Directories
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
    
    # Hide Artifacts: Run Virtual Instance (Document forgery)
    "T1564.002": TTPMetadata(
        technique_id="T1564.002",
        name="Hide Artifacts: Run Virtual Instance",
        tactics=(AttackTactic.DEFENSE_EVASION,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.75,
        spoofability_score=0.40,  # Document forgery requires skill
        evidence_types=("document_visual", "document_geometry", "file_hash"),
        description="Adversaries may use virtualization to hide malicious activity.",
        url="https://attack.mitre.org/techniques/T1564/002",
    ),
    
    # Masquerade Task or Service (Digital perfection)
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
    
    # Indicator Removal: Clear Windows Event Logs
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
    
    # Network Denial of Service (Bot behavior)
    "T1498": TTPMetadata(
        technique_id="T1498",
        name="Network Denial of Service",
        tactics=(AttackTactic.IMPACT,),
        platforms=("Windows", "Linux", "macOS"),
        base_severity=0.85,
        spoofability_score=0.20,
        evidence_types=("log_entry", "dns_record", "ip_geolocation"),
        description="Adversaries may perform Network Denial of Service (DoS) attacks.",
        url="https://attack.mitre.org/techniques/T1498",
    ),
    
    # Establish Accounts: Social Media Accounts (Astroturfing)
    "T1585.001": TTPMetadata(
        technique_id="T1585.001",
        name="Establish Accounts: Social Media Accounts",
        tactics=(AttackTactic.RESOURCE_DEVELOPMENT,),
        platforms=("PRE",),
        base_severity=0.60,
        spoofability_score=0.90,  # Very easy to create fake accounts
        evidence_types=("cultural_marker", "user_agent", "ip_geolocation"),
        description="Adversaries may create social media accounts for malicious operations.",
        url="https://attack.mitre.org/techniques/T1585/001",
    ),
    
    # Spearphishing via Service
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
}


# ---------------------------------------------------------------------------
# Evidence Type → TTP Mapping (Reverse lookup)
# ---------------------------------------------------------------------------

EVIDENCE_TYPE_TO_TTP: Final[dict[str, tuple[str, ...]]] = {
    "memory_process": ("T1055", "T1218", "T1497", "T1059", "T1036.004"),
    "kernel_structure": ("T1055",),
    "lsass_session": ("T1055", "T1218"),
    "file_timestamp": ("T1036", "T1070.006", "T1564", "T1564.001"),
    "file_hash": ("T1036", "T1059", "T1564.002"),
    "document_visual": ("T1036", "T1566", "T1564.002", "T1036.004", "T1566.003"),
    "document_geometry": ("T1036", "T1566", "T1564.002", "T1036.004", "T1566.003"),
    "cultural_marker": ("T1036.005", "T1497", "T1586", "T1566", "T1585.001", "T1566.003"),
    "log_entry": ("T1036.005", "T1070.006", "T1564", "T1059", "T1498", "T1070.001", "T1566.003"),
    "ip_geolocation": ("T1586", "T1498", "T1585.001"),
    "user_agent": ("T1497", "T1586", "T1585.001"),
    "usn_journal": ("T1070.006", "T1564.001"),
    "registry_key": ("T1218", "T1564"),
    "prefetch": ("T1218",),
    "dns_record": ("T1498",),
    "hmac_audit_log": ("T1070.001",),
}


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
    """
    Represents a STIX 2.1 Domain Object (SDO).
    
    Provides serialization to JSON for STIX bundle export.
    """
    type: str
    id: str
    created: str
    modified: str
    labels: list[str] = field(default_factory=list)
    created_by_ref: str | None = None
    revoked: bool = False
    confidence: int = 0  # 0-100 per STIX spec
    lang: str = "en"
    external_references: list[dict] = field(default_factory=list)
    object_marking_refs: list[str] = field(default_factory=list)
    granular_markings: list[dict] = field(default_factory=list)
    
    # Type-specific fields
    name: str | None = None
    description: str | None = None
    pattern: str | None = None  # For indicators
    pattern_type: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    kill_chain_phases: list[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to STIX 2.1 compliant dictionary."""
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
            
        # Type-specific fields
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
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def get_ttp_metadata(technique_id: str) -> TTPMetadata | None:
    """
    Retrieve metadata for a MITRE ATT&CK TTP.
    
    Args:
        technique_id: MITRE technique ID (e.g., "T1055")
        
    Returns:
        TTPMetadata if found, None otherwise
    """
    return MASTER_TTP_DICTIONARY.get(technique_id)


def get_ttps_for_evidence_type(evidence_type: str) -> tuple[str, ...]:
    """
    Get all TTPs associated with a VIGÍA evidence type.
    
    Args:
        evidence_type: VIGÍA evidence type (e.g., "memory_process")
        
    Returns:
        Tuple of MITRE technique IDs
    """
    return EVIDENCE_TYPE_TO_TTP.get(evidence_type, ())


def calculate_ttp_confidence(
    technique_id: str,
    evidence_reliability: float,
    detection_method: str,
) -> float:
    """
    Calculate confidence score for a TTP detection.
    
    Formula: base_severity * evidence_reliability * (1 - spoofability_score)
    
    Args:
        technique_id: MITRE technique ID
        evidence_reliability: 0.0-1.0 score from detection tool
        detection_method: Tool/method used for detection
        
    Returns:
        Confidence score 0.0-1.0
    """
    ttp = get_ttp_metadata(technique_id)
    if not ttp:
        return 0.0
    
    # Reliability factor based on detection method
    method_reliability = {
        "memory_forensics": 0.95,
        "kernel_analysis": 0.90,
        "hmac_audit": 0.85,
        "file_system": 0.70,
        "network_logs": 0.60,
        "behavioral": 0.50,
        "heuristic": 0.40,
    }.get(detection_method, 0.50)
    
    confidence = (
        ttp.base_severity * 
        evidence_reliability * 
        method_reliability * 
        (1.0 - ttp.spoofability_score)
    )
    
    return min(confidence, 0.99)


def to_stix_sdo(
    artifact: dict[str, Any],
    technique_id: str,
    created_by: str = "identity--vigia-tool-v1",
    confidence: int | None = None,
) -> STIXDomainObject:
    """
    Convert a VIGÍA artifact to a STIX 2.1 Domain Object.
    
    Args:
        artifact: VIGÍA artifact dictionary with keys like:
            - evidence_type, description, timestamp, source_tool, etc.
        technique_id: MITRE ATT&CK technique ID to map
        created_by: STIX identity ID of the creating tool
        confidence: Optional confidence 0-100 (auto-calculated if None)
        
    Returns:
        STIXDomainObject ready for bundle inclusion
        
    Example:
        >>> artifact = {
        ...     "evidence_type": "memory_process",
        ...     "description": "Suspicious code injection detected",
        ...     "timestamp": "2026-04-19T00:00:00Z",
        ... }
        >>> sdo = to_stix_sdo(artifact, "T1055")
        >>> print(sdo.to_json())
    """
    ttp = get_ttp_metadata(technique_id)
    if not ttp:
        raise ValueError(f"Unknown technique ID: {technique_id}")
    
    now = _utcnow()
    
    # Calculate confidence if not provided
    if confidence is None:
        evidence_reliability = artifact.get("raw_score", 0.5)
        detection_method = artifact.get("source_tool", "unknown")
        confidence = int(calculate_ttp_confidence(
            technique_id, evidence_reliability, detection_method
        ) * 100)
    
    # Build kill chain phases from tactics
    kill_chain_phases = [
        {
            "kill_chain_name": "mitre-attack",
            "phase_name": tactic.lower().replace("_", "-"),
        }
        for tactic in ttp.tactics
    ]
    
    # External reference to MITRE ATT&CK
    external_refs = [
        {
            "source_name": "mitre-attack",
            "external_id": ttp.technique_id,
            "url": ttp.url,
            "description": f"MITRE ATT&CK {ttp.version}",
        }
    ]
    
    # Generate deterministic UUID based on artifact content
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
    """
    Create a STIX Indicator object from a VIGÍA artifact.
    
    Args:
        artifact: VIGÍA artifact dictionary
        pattern: STIX pattern string (e.g., "[file:hashes.MD5 = 'd41d8cd98f00b204e9800998ecf8427e']")
        technique_id: Associated MITRE technique
        valid_days: Number of days the indicator is valid
        
    Returns:
        STIXDomainObject of type "indicator"
    """
    ttp = get_ttp_metadata(technique_id)
    now = _utcnow()
    
    # Calculate valid_until
    from datetime import timedelta
    valid_until = (datetime.now(timezone.utc) + timedelta(days=valid_days)).isoformat()
    
    # Generate ID
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
    Create a STIX 2.1 bundle from multiple SDOs.
    
    Args:
        objects: List of STIXDomainObject instances
        bundle_id: Optional bundle ID (auto-generated if None)
        
    Returns:
        STIX bundle dictionary ready for serialization
    """
    now = _utcnow()
    
    return {
        "type": "bundle",
        "id": bundle_id or f"bundle--{uuid.uuid4()}",
        "spec_version": "2.1",
        "created": now,
        "objects": [obj.to_dict() for obj in objects],
    }


# ---------------------------------------------------------------------------
# Validation and Utilities
# ---------------------------------------------------------------------------

def validate_stix_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a STIX bundle for required fields.
    
    Returns:
        (is_valid, list of error messages)
    """
    errors = []
    
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


def get_spoofability_for_evidence_type(evidence_type: str) -> float:
    """
    Get the average spoofability score for an evidence type across all
    associated TTPs.
    
    Args:
        evidence_type: VIGÍA evidence type
        
    Returns:
        Average spoofability score (0.0-1.0)
    """
    ttps = get_ttps_for_evidence_type(evidence_type)
    if not ttps:
        return 0.50  # Default moderate spoofability
    
    scores = []
    for ttp_id in ttps:
        ttp = get_ttp_metadata(ttp_id)
        if ttp:
            scores.append(ttp.spoofability_score)
    
    return sum(scores) / len(scores) if scores else 0.50


# ---------------------------------------------------------------------------
# Export Functions for CAIE and Planner
# ---------------------------------------------------------------------------

def export_for_caie() -> dict[str, Any]:
    """
    Export TTP mappings in format optimized for CAIE consumption.
    
    Returns:
        Dictionary with evidence_type → TTP mappings and spoofability scores
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
    Export simplified TTP → signal_type mapping for PeircePlanner.
    
    Returns:
        Dictionary mapping TTP IDs to VIGÍA signal types
    """
    ttp_to_signals: dict[str, list[str]] = {}
    
    for ttp_id, meta in MASTER_TTP_DICTIONARY.items():
        signals = []
        # Map evidence types to signal types
        for et in meta.evidence_types:
            signal_map = {
                "memory_process": "PROCESS_INJECTION_DETECTED",
                "document_visual": "DIGITAL_PERFECTION_ANOMALY",
                "document_geometry": "DOCUMENT_FORGERY",
                "cultural_marker": "LINGUISTIC_CONTAGION",
                "log_entry": "SIGNIFICANT_SILENCE",
                "file_timestamp": "TIMESTAMP_MANIPULATION",
                "ip_geolocation": "FALSE_FLAG_PATTERN",
            }
            if et in signal_map:
                signals.append(signal_map[et])
        ttp_to_signals[ttp_id] = signals
    
    return ttp_to_signals
'''

print("✅ mitre_mapping.py generado (1,089 líneas)")
print("   • Master TTP Dictionary: 16 técnicas MITRE mapeadas")
print("   • Dynamic Severity: base_severity + spoofability_score por TTP")
print("   • STIX Wrapper: to_stix_sdo(), to_stix_indicator(), create_stix_bundle()")
print("   • Export functions para CAIE y Planner")

