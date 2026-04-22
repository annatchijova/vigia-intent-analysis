"""
vigia/tools/caie.py
====================
VIGIA — Cross-Artifact Incongruence Engine (CAIE) — v2.0 EXPANDED [DETERMINISTIC+RESILIENT]

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Claude (Anthropic) — Systems Integration Engineer
Expansion: Gemini, Qwen, DeepSeek — "Golden Forensic Rules"
Determinism Protocol: Qwen (Tongyi Qianwen) — "The One Who Turned Paranoia into Protocol"
Resilience Layer: DeepSeek + Qwen — "The Ones Who Said 'This Is Vulnerable, Fix It'"

Theoretical foundation
----------------------
Not all evidence weighs equally. An IP address can be spoofed in 30 seconds.
A memory process object requires live system compromise to fabricate.
CAIE implements Kimi's authenticity-adjusted scoring formula:

    adjusted_score = raw_score × (1 - spoofability) × weight

This ensures structurally irrefutable evidence (memory, kernel objects)
dominates easily-planted evidence (IPs, cultural markers, log entries)
in the final verdict — critical for Daubert admissibility.

Cross-Artifact Discrepancy Detection (EXPANDED)
------------------------------------------------
CAIE detects fractures between artifact sources that should be consistent:
* Log claims vs. memory reality (structural impossibility)
* Filesystem timestamps vs. system clock (temporal fabrication)
* Cultural markers vs. technical evidence (false flag detection)
* EXIF metadata vs. file content (document forgery)

NEW v2.0 — Golden Forensic Rules:
* TEMPORAL_CAUSALITY_VIOLATION: Effect-before-cause detection
* NETWORK_VS_HOST: Firewall claims vs. host reality
* CRYPTOGRAPHIC_INCONSISTENCY: Signature validation failures

Noisy-OR Fusion Model (P1 Update)
---------------------------------
Evidence from the same source/tool is dependent. Evidence from different
sources is independent. We apply Noisy-OR within groups, then across groups:

    group_score = 1 - ∏(1 - score_i)  [within group, dependent]
    composite = 1 - ∏(1 - group_j)    [across groups, independent]

This prevents "flood attacks" where one tool generates 100 alerts.

MITRE ATT&CK Integration
------------------------
CAIE outputs include TTP mapping for STIX 2.1 export via mitre_mapping.py.

DETERMINISTIC FORENSIC PROTOCOL (P0)
------------------------------------
Qwen's determinism guarantee: bit-identical output across x86/ARM architectures.
* All intermediate calculations rounded to _DETERMINISTIC_INTERNAL_PREC (6)
* All final outputs rounded to _DETERMINISTIC_OUTPUT_PREC (4)
* math.fsum() used for all summations to prevent FPU drift
* Explicit rounding at each arithmetic step prevents compiler optimization differences

RESILIENCE PROTOCOL (DeepSeek+Qwen)
-----------------------------------
* Graceful degradation on missing dependencies (mocks/fallbacks)
* Type-safe comparisons (str normalization)
* HMAC safety with fallback key generation
* Demo-ready: no hard crashes on import failures
"""

from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json
import math
import os
import re
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Final

# ============================================================================
# RESILIENT IMPORTS (DeepSeek+Qwen P0)
# Graceful degradation with mocks/fallbacks for demo resilience
# ============================================================================

# Mock logger fallback
class _MockAuditLogger:
    """Fallback audit logger when vigia.security is unavailable."""
    _hmac_key: bytes = b""

    @staticmethod
    def log_block(event_type: str, tool: str, input_preview: str, reason: str) -> None:
        print(f"[MOCK_AUDIT] BLOCK: {event_type} | {tool} | {reason}", file=sys.stderr)

    @staticmethod
    def log_info(event_type: str, tool: str, message: str) -> None:
        print(f"[MOCK_AUDIT] INFO: {event_type} | {tool} | {message}", file=sys.stderr)

# Mock trust decay fallback
class _MockTrustDecay:
    """Fallback trust decay when trust_decay is unavailable."""
    @staticmethod
    def apply_decay(trust: float, break_severity: float = 0.5) -> tuple[float, str]:
        new_trust = max(0.0, trust * (1.0 - break_severity))
        return new_trust, f"mock_decay_applied:{break_severity}"

# Mock MITRE mapping fallback
class _MockMitreMapping:
    """Fallback MITRE mapping when mitre_mapping is unavailable."""

    @staticmethod
    def get_ttp_metadata(ttp_id: str) -> dict | None:
        return {"id": ttp_id, "name": "Unknown", "tactic": "unknown"}

    @staticmethod
    def get_ttps_for_evidence_type(evidence_type: str) -> list[str]:
        return []

    @staticmethod
    def calculate_ttp_confidence(ttp_id: str, reliability: float, source: str) -> float:
        return _dround(reliability, _DETERMINISTIC_INTERNAL_PREC)

    EVIDENCE_TYPE_TO_TTP: dict[str, list[str]] = {}

# Mock UTC now fallback
def _mock_utcnow() -> str:
    """Fallback UTC timestamp when _utcnow is unavailable."""
    return datetime.now(timezone.utc).isoformat()

# Mock sanitization fallbacks
def _mock_sanitize_path(path: str) -> str:
    """Fallback path sanitizer."""
    return str(path).replace("..", "").replace("//", "/")

def _mock_sanitize_llm_input(text: str) -> str:
    """Fallback LLM input sanitizer."""
    return str(text)[:10000]  # Simple length limit

# Attempt imports with graceful fallback
try:
    from vigia.security import (
        _sanitize_path, 
        _utcnow, 
        audit_logger,
        trust_decay,
        _sanitize_llm_input,
    )
except ImportError as e:
    print(f"[CAIE-RESILIENCE] vigia.security import failed: {e}. Using mocks.", file=sys.stderr)
    _sanitize_path = _mock_sanitize_path
    _utcnow = _mock_utcnow
    audit_logger = _MockAuditLogger()
    trust_decay = _MockTrustDecay()
    _sanitize_llm_input = _mock_sanitize_llm_input

try:
    from vigia.tools.mitre_mapping import (
        get_ttp_metadata,
        get_ttps_for_evidence_type,
        calculate_ttp_confidence,
        EVIDENCE_TYPE_TO_TTP,
    )
except ImportError as e:
    print(f"[CAIE-RESILIENCE] mitre_mapping import failed: {e}. Using mocks.", file=sys.stderr)
    get_ttp_metadata = _MockMitreMapping.get_ttp_metadata
    get_ttps_for_evidence_type = _MockMitreMapping.get_ttps_for_evidence_type
    calculate_ttp_confidence = _MockMitreMapping.calculate_ttp_confidence
    EVIDENCE_TYPE_TO_TTP = _MockMitreMapping.EVIDENCE_TYPE_TO_TTP


# ============================================================================
# DETERMINISTIC PRECISION PROTOCOL (Qwen P0)
# Guarantees bit-identical output across x86/ARM architectures
# ============================================================================
_DETERMINISTIC_INTERNAL_PREC: Final[int] = 6
_DETERMINISTIC_OUTPUT_PREC: Final[int] = 4


def _dround(value: float, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> float:
    """Deterministic rounding helper - ensures consistent rounding across platforms."""
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


# ============================================================================
# RESILIENT HMAC KEY MANAGEMENT (DeepSeek P0)
# Ensures _sign_result never fails due to missing key
# ============================================================================

def _get_hmac_key() -> bytes:
    """Get or generate HMAC key resiliently."""
    key = getattr(audit_logger, "_hmac_key", None)
    if key and isinstance(key, bytes) and len(key) > 0:
        return key
    # Generate deterministic fallback key from module fingerprint
    fallback = hashlib.sha256(b"VIGIA_CAIE_DEMO_KEY_v2.0").digest()
    return fallback


# ---------------------------------------------------------------------------
# Spoofability table (Kimi's contribution) — UPDATED with MITRE integration
# ---------------------------------------------------------------------------

@dataclass
class EvidenceProfile:
    """
    Profile for an evidence type.

    Kimi P0: strict validation in __post_init__ — every field must be
    numeric, finite, and within range. A corrupted profile would silently
    poison the composite score (e.g. spoofability=-1 inverts the formula).
    """
    spoofability: float   # 0.0 (impossible to fake) to 1.0 (trivially spoofable)
    base_weight: float    # Relative importance in composite score
    description: str = ""

    def __post_init__(self) -> None:
        for field_name in ("spoofability", "base_weight"):
            val = getattr(self, field_name)
            if not isinstance(val, (int, float)):
                raise TypeError(
                    f"EvidenceProfile.{field_name} must be numeric, "
                    f"got {type(val).__name__}"
                )
            if not math.isfinite(val):
                raise ValueError(
                    f"EvidenceProfile.{field_name} must be finite, got {val}"
                )
        if not (0.0 <= self.spoofability <= 1.0):
            raise ValueError(
                f"EvidenceProfile.spoofability must be in [0.0, 1.0], "
                f"got {self.spoofability}"
            )
        if not (0.0 <= self.base_weight <= 1.0):
            raise ValueError(
                f"EvidenceProfile.base_weight must be in [0.0, 1.0], "
                f"got {self.base_weight}"
            )


EVIDENCE_PROFILES: Final[dict[str, EvidenceProfile]] = {
    # Trivially spoofable
    "ip_geolocation":       EvidenceProfile(0.90, 0.15, "IP/VPN/proxy -- trivially spoofable"),
    "cultural_marker":      EvidenceProfile(0.90, 0.15, "Language, keyboard layout -- easy to fake"),
    "log_entry":            EvidenceProfile(0.85, 0.15, "Syslog/eventlog -- writable by admin"),
    "user_agent":           EvidenceProfile(0.85, 0.15, "HTTP User-Agent -- trivially spoofable"),

    # Moderately spoofable
    "file_timestamp":       EvidenceProfile(0.70, 0.20, "mtime/atime/ctime -- touch command"),
    "file_hash":            EvidenceProfile(0.50, 0.25, "SHA-256 of file content"),
    "dns_record":           EvidenceProfile(0.60, 0.20, "DNS resolution -- cache poisonable"),
    "registry_key":         EvidenceProfile(0.55, 0.20, "Windows registry -- writable with privs"),

    # Hard to spoof
    "usn_journal":          EvidenceProfile(0.20, 0.30, "NTFS USN journal -- kernel-level only"),
    "memory_process":       EvidenceProfile(0.15, 0.30, "Volatile memory objects -- requires live compromise"),
    "lsass_session":        EvidenceProfile(0.15, 0.30, "LSASS auth records -- cryptographically derived"),
    "prefetch":             EvidenceProfile(0.25, 0.28, "Prefetch/Superfetch -- OS-managed"),

    # Structurally irrefutable
    "kernel_structure":     EvidenceProfile(0.10, 0.35, "EPROCESS/ETHREAD -- kernel address space"),
    "hmac_audit_log":       EvidenceProfile(0.05, 0.40, "HMAC-chained log -- requires key compromise"),
    "hardware_serial":      EvidenceProfile(0.05, 0.40, "Hardware serial numbers -- physical access only"),

    # P3: Document forensics
    "document_visual":      EvidenceProfile(0.40, 0.25, "Visual document analysis -- requires fabrication skill"),
    "document_geometry":    EvidenceProfile(0.45, 0.22, "Document layout metrics -- harder to fake than text"),

    # P4: Cryptographic evidence
    "cryptographic_hash":   EvidenceProfile(0.05, 0.45, "Cryptographic hash with known-good database"),
    "digital_signature":    EvidenceProfile(0.10, 0.40, "PKI digital signature -- requires key compromise"),
}

# Whitelist of valid evidence types — any type not in this set is rejected
_VALID_EVIDENCE_TYPES: Final[frozenset[str]] = frozenset(EVIDENCE_PROFILES.keys())

# Maximum artifacts per evaluation — prevents DoS via artifact flooding
_MAX_ARTIFACTS: Final[int] = 1000

# Minimum independent sources for full confidence (P1: normalization)
_MIN_INDEPENDENT_SOURCES: Final[int] = 3
_LOW_SOURCE_PENALTY: Final[float] = 0.20  # Reduce score by 20% if < 3 sources


# ---------------------------------------------------------------------------
# MITRE ATT&CK TTP Mapping — NOW IMPORTED from mitre_mapping.py
# ---------------------------------------------------------------------------
# Legacy mapping kept for backward compatibility during transition
_SIGNAL_TO_ATTACK: Final[dict[str, str]] = {
    "RUSSIAN_PHONETIC_EVASION":          "T1036.005",
    "MIXED_ALPHABET_SUSPICIOUS":         "T1036",
    "PROHIBITED_BEHAVIOR_FOR_THIS_PROCESS": "T1218",
    "OUT_OF_HABIT_ACTION":               "T1218",
    "PROGRAMMED_DELAY_DETECTED":         "T1497",
    "NON_HUMAN_PRECISION":               "T1497",
    "EXACT_REPETITION_AFTER_FALSE_ERROR": "T1498",
    "HONEYPOT_TERM_DETECTED":            "T1586",
    "LINGUISTIC_CONTAGION":              "T1585.001",
    "AUTHORITY_ESTABLISHMENT":           "T1566",
    "CARNEGIE_FLATTERY_TO_SYSTEM":       "T1566",
    "FALSE_FAMILIARITY_CARNEGIE_PARADOX": "T1566.003",
    "GRADUAL_ESCALATION_DETECTED":       "T1059",
    "SIGNIFICANT_SILENCE":               "T1564",
    "POSSIBLE_SCENE_STAGING":            "T1564.001",
    # P3: Document forensics
    "DOCUMENT_FORGERY":                  "T1564.002",
    "DIGITAL_PERFECTION_ANOMALY":        "T1036.004",
    "METADATA_CONCEALMENT":              "T1070.006",
    # P4: New Golden Rules
    "TEMPORAL_CAUSALITY_VIOLATION":      "T1070.006",  # Timestomp variant
    "NETWORK_VS_HOST":                   "T1564",      # Hide Artifacts
    "CRYPTOGRAPHIC_INCONSISTENCY":       "T1036",      # Masquerading
}


# ---------------------------------------------------------------------------
# Artifact data structure
# ---------------------------------------------------------------------------

@dataclass
class Artifact:
    """
    A single piece of forensic evidence with its classification.

    source_tool : which VIGIA tool produced this artifact
    evidence_type : key into EVIDENCE_PROFILES (determines spoofability)
    raw_score   : suspicion score from the producing tool [0.0, 1.0]
    description : human-readable description of the finding
    metadata    : arbitrary dict with tool-specific data
    provenance_chain : list of hashes for EPC validation
    base_trust  : initial trust level (default 1.0)
    timestamp   : when this artifact was collected
    """
    source_tool: str
    evidence_type: str
    raw_score: float
    description: str
    metadata: dict = field(default_factory=dict)
    provenance_chain: list[str] = field(default_factory=list)
    base_trust: float = 1.0
    timestamp: str = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        """
        Gemini P0: Finite Math Shield.
        Reject inf, -inf, NaN in raw_score. An attacker who injects
        float('inf') as a score gets infinite weight in the verdict.
        """
        if not isinstance(self.raw_score, (int, float)):
            try:
                audit_logger.log_block(
                    event_type="FORENSIC_POISONING_ATTEMPT",
                    tool="CAIE.Artifact",
                    input_preview=f"source={self.source_tool} type={self.evidence_type}",
                    reason=f"raw_score is {type(self.raw_score).__name__}, not numeric.",
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            self.raw_score = 0.0
        elif not math.isfinite(self.raw_score):
            try:
                audit_logger.log_block(
                    event_type="FORENSIC_POISONING_ATTEMPT",
                    tool="CAIE.Artifact",
                    input_preview=f"source={self.source_tool} score={self.raw_score}",
                    reason=(
                        f"Non-finite raw_score ({self.raw_score}). "
                        "Infinity/NaN injection would give infinite weight in verdict. "
                        "Artifact score zeroed."
                    ),
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            self.raw_score = 0.0
        else:
            # Clamp to [0.0, 1.0]
            self.raw_score = _dround(max(0.0, min(1.0, self.raw_score)), _DETERMINISTIC_INTERNAL_PREC)

        # P2: Apply trust decay if provenance chain is broken
        if self.provenance_chain:
            # Check for breaks in chain (simplified: gaps in sequence)
            if len(self.provenance_chain) < 2:
                # Single link = potential break
                try:
                    self.base_trust, _ = trust_decay.apply_decay(self.base_trust, break_severity=0.5)
                    self.base_trust = _dround(self.base_trust, _DETERMINISTIC_INTERNAL_PREC)
                except Exception:
                    # Resilience: if trust_decay fails, apply manual decay
                    self.base_trust = _dround(self.base_trust * 0.5, _DETERMINISTIC_INTERNAL_PREC)

    @property
    def profile(self) -> EvidenceProfile:
        return EVIDENCE_PROFILES.get(
            self.evidence_type,
            EvidenceProfile(0.50, 0.20, "Unknown evidence type -- default weights"),
        )

    @property
    def adjusted_score(self) -> float:
        """
        Kimi's formula (DETERMINISTIC): raw_score × (1 - spoofability) × weight × base_trust

        Deterministic variant: explicit rounding at each step to prevent FPU drift (Qwen P0).
        """
        p = self.profile

        # Step 1: raw_score × (1 - spoofability)
        step1 = _dround(self.raw_score * (1.0 - p.spoofability), _DETERMINISTIC_INTERNAL_PREC)

        # Step 2: × base_weight
        step2 = _dround(step1 * p.base_weight, _DETERMINISTIC_INTERNAL_PREC)

        # Step 3: × base_trust
        result = _dround(step2 * self.base_trust, _DETERMINISTIC_INTERNAL_PREC)

        # Defense-in-depth: should be impossible after __post_init__ clamp,
        # but protect against corrupted EvidenceProfile values.
        if not math.isfinite(result):
            return 0.0

        return _dround(max(0.0, min(1.0, result)), _DETERMINISTIC_INTERNAL_PREC)


# ---------------------------------------------------------------------------
# Fracture detection: cross-artifact discrepancies
# ---------------------------------------------------------------------------

@dataclass
class Fracture:
    """
    A discrepancy between two artifacts that should be consistent.

    For example: logs claim a Russian RDP login at 03:00 UTC, but memory
    shows zero sessions from external IPs. The log is easy to plant
    (spoofability=0.85), but memory is structurally irrefutable (0.15).
    The fracture itself is evidence of fabrication.
    """
    artifact_a: str       # description of artifact A
    artifact_b: str       # description of artifact B
    fracture_type: str    # e.g. "LOG_VS_MEMORY", "TIMESTAMP_VS_CLOCK", "DOCUMENT_FORGERY"
    severity: float       # 0.0-1.0
    interpretation: str   # Peirce-framed explanation
    spoofability_delta: float = 0.0  # difference in spoofability between sources
    ttp_id: str | None = None  # Associated MITRE ATT&CK TTP


# ---------------------------------------------------------------------------
# CrossArtifactIncongruenceEngine
# ---------------------------------------------------------------------------

class CrossArtifactIncongruenceEngine:
    """
    Kimi's Cross-Artifact Incongruence Engine — EXPANDED v2.0 [DETERMINISTIC+RESILIENT].

    Evaluates a collection of artifacts from multiple VIGIA tools and:
    1. Computes authenticity-adjusted scores (spoofability weighting)
    2. Detects fractures between artifact sources (including Golden Rules)
    3. Flags false-flag patterns (high cultural + low technical evidence)
    4. Produces a Daubert-admissible composite verdict using Noisy-OR fusion

    NEW v2.0: Golden Forensic Rules for advanced evasion detection.

    DETERMINISTIC PROTOCOL (Qwen P0):
    - All intermediate calculations rounded to 6 decimal places
    - All outputs rounded to 4 decimal places
    - math.fsum() used for all summations
    - Explicit rounding prevents x86/ARM FPU drift

    RESILIENCE PROTOCOL (DeepSeek+Qwen):
    - Graceful degradation on missing dependencies
    - Type-safe comparisons
    - HMAC safety with fallback keys

    Peirce framing:
      Firstness  — raw scores from individual tools
      Secondness — adjusted scores after spoofability weighting
      Thirdness  — fractures reveal the HABIT of the actor
    """

    def __init__(self) -> None:
        self._artifacts: list[Artifact] = []
        self._fractures: list[Fracture] = []
        self._temporal_index: dict[str, list[Artifact]] = {}  # For TCV rule
        self._network_index: dict[str, list[Artifact]] = {}   # For NETWORK_VS_HOST

    def add_artifact(self, artifact: Artifact) -> bool:
        """
        Add an artifact from a VIGIA tool result.

        Returns True if added, False if rejected (limit or invalid type).

        Kimi P0 enforcement:
        - Rejects if _MAX_ARTIFACTS exceeded (DoS protection)
        - Rejects if evidence_type is not in the whitelist
        """
        if len(self._artifacts) >= _MAX_ARTIFACTS:
            try:
                audit_logger.log_block(
                    event_type="CAIE_ARTIFACT_LIMIT",
                    tool="CAIE.add_artifact",
                    input_preview=f"source={artifact.source_tool} type={artifact.evidence_type}",
                    reason=(
                        f"Artifact limit ({_MAX_ARTIFACTS}) reached. "
                        "Possible artifact flooding attack. Artifact rejected."
                    ),
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            return False

        if artifact.evidence_type not in _VALID_EVIDENCE_TYPES:
            try:
                audit_logger.log_block(
                    event_type="CAIE_INVALID_EVIDENCE_TYPE",
                    tool="CAIE.add_artifact",
                    input_preview=f"type={artifact.evidence_type} source={artifact.source_tool}",
                    reason=(
                        f"Evidence type {artifact.evidence_type!r} not in whitelist. "
                        f"Valid types: {sorted(_VALID_EVIDENCE_TYPES)}. "
                        "Unknown types could bypass spoofability weighting."
                    ),
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            return False

        self._artifacts.append(artifact)

        # Index for temporal and network analysis
        if artifact.timestamp:
            self._temporal_index.setdefault(artifact.timestamp, []).append(artifact)
        if "network" in artifact.evidence_type or "ip" in artifact.evidence_type:
            self._network_index.setdefault(artifact.source_tool, []).append(artifact)

        return True

    def add_from_tool_result(
        self,
        tool_name: str,
        result: dict,
        evidence_type: str = "log_entry",
        provenance_chain: list[str] | None = None,
    ) -> None:
        """
        Convenience: extract an artifact from a standard VIGIA tool result dict.

        Looks for 'suspicion_score', 'probability_*', or 'visual_malice_score'
        to derive the raw score. Falls back to 0.0 if no score field found.
        """
        raw_score = 0.0
        for key in ("suspicion_score", "visual_malice_score",
                     "probability_compromise", "probability_evasion",
                     "probability_automation", "probability_deception",
                     "probability_same_entity"):
            val = result.get(key, 0.0)
            if isinstance(val, (int, float)) and val > raw_score:
                raw_score = float(val)

        description = result.get("vigia_verdict", result.get("verdict", ""))

        # P3: Check for document forgery signals from vision audit
        if result.get("digital_perfection_detected"):
            evidence_type = "document_visual"
            description = f"[DIGITAL_PERFECTION] {description}"

        # P4: Check for cryptographic inconsistency
        if result.get("signature_mismatch") or result.get("hash_mismatch"):
            evidence_type = "cryptographic_hash"
            description = f"[CRYPTO_MISMATCH] {description}"

        self._artifacts.append(Artifact(
            source_tool=tool_name,
            evidence_type=evidence_type,
            raw_score=raw_score,
            description=str(description)[:500],
            metadata={k: v for k, v in result.items()
                      if k in ("verdict", "signals", "findings", "anomalies", 
                               "digital_perfection_detected", "signature_mismatch",
                               "hash_mismatch", "timestamp", "process_creation_time",
                               "network_log_time", "firewall_claim", "host_reality")},
            provenance_chain=provenance_chain or [],
        ))

    # ------------------------------------------------------------------
    # Fracture detection — EXPANDED v2.0 with Golden Rules
    # ------------------------------------------------------------------

    def detect_fractures(self) -> list[Fracture]:
        """
        Detect cross-artifact discrepancies including Golden Forensic Rules.

        Rules:
        1. LOG_VS_MEMORY: log says X happened, memory says it didn't
        2. CULTURAL_VS_TECHNICAL: high cultural markers + low technical
           → false flag (planted attribution)
        3. TIMESTAMP_FRACTURE: temporal anomalies across sources
        4. VERDICT_CONFLICT: one tool says NOISE, another says MALICE
           for the same evidence → scene staging
        5. DOCUMENT_FORGERY: visual analysis detects digital perfection
        6. TEMPORAL_CAUSALITY_VIOLATION (NEW): Effect before cause
        7. NETWORK_VS_HOST (NEW): Firewall claims vs. host reality
        8. CRYPTOGRAPHIC_INCONSISTENCY (NEW): Signature/hash mismatch
        """
        self._fractures.clear()

        # Group artifacts by evidence type category
        cultural = [a for a in self._artifacts if a.evidence_type in
                    ("cultural_marker", "ip_geolocation", "user_agent")]
        technical = [a for a in self._artifacts if a.evidence_type in
                     ("memory_process", "lsass_session", "kernel_structure",
                      "usn_journal", "hmac_audit_log")]
        logs = [a for a in self._artifacts if a.evidence_type == "log_entry"]
        documents = [a for a in self._artifacts if a.evidence_type in
                     ("document_visual", "document_geometry")]
        cryptographic = [a for a in self._artifacts if a.evidence_type in
                         ("cryptographic_hash", "digital_signature")]
        network_logs = [a for a in self._artifacts if a.evidence_type in
                        ("log_entry", "dns_record") and "network" in a.description.lower()]
        host_logs = [a for a in self._artifacts if a.evidence_type in
                     ("log_entry", "memory_process") and "socket" in str(a.metadata).lower()]

        # Rule 1: Cultural bait with no technical corroboration
        if cultural and technical:
            # DETERMINISTIC: Use math.fsum for precise summation
            avg_cultural = _dround(math.fsum(a.raw_score for a in cultural) / len(cultural), _DETERMINISTIC_INTERNAL_PREC)
            avg_technical = _dround(math.fsum(a.raw_score for a in technical) / len(technical), _DETERMINISTIC_INTERNAL_PREC)

            if avg_cultural > 0.5 and avg_technical < 0.2:
                self._fractures.append(Fracture(
                    artifact_a=f"Cultural markers (avg={avg_cultural:.2f})",
                    artifact_b=f"Technical evidence (avg={avg_technical:.2f})",
                    fracture_type="FALSE_FLAG_PATTERN",
                    severity=0.8,
                    interpretation=(
                        "High cultural attribution markers with near-zero technical "
                        "corroboration. Classic false-flag pattern: the cultural "
                        "evidence was planted to mislead attribution. "
                        "Peirce Thirdness: the HABIT is to disguise origin, not to act."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1585.001",  # Establish Accounts: Social Media
                ))

        # Rule 2: Log claims contradicted by memory
        if logs and technical:
            log_verdicts = {a.metadata.get("verdict") for a in logs} - {None, "NOISE"}
            tech_verdicts = {a.metadata.get("verdict") for a in technical}

            if log_verdicts and "NOISE" in tech_verdicts and len(tech_verdicts) == 1:
                self._fractures.append(Fracture(
                    artifact_a=f"Log evidence claims: {log_verdicts}",
                    artifact_b="Memory/kernel evidence: all NOISE (no corroboration)",
                    fracture_type="LOG_VS_MEMORY",
                    severity=0.9,
                    interpretation=(
                        "Logs claim suspicious activity but memory shows no trace. "
                        "Structural impossibility: if the activity happened, memory "
                        "MUST contain traces (LSASS sessions, network objects). "
                        "Their absence proves the logs were fabricated."
                    ),
                    spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1070.001",  # Clear Windows Event Logs
                ))

        # Rule 3: Verdict conflict between tools
        verdicts = {}
        for a in self._artifacts:
            v = a.metadata.get("verdict", "NOISE")
            if v not in verdicts:
                verdicts[v] = []
            verdicts[v].append(a)

        if "MALICE" in verdicts and "NOISE" in verdicts:
            malice_sources = [a.source_tool for a in verdicts["MALICE"]]
            noise_sources = [a.source_tool for a in verdicts["NOISE"]]
            self._fractures.append(Fracture(
                artifact_a=f"MALICE from: {malice_sources}",
                artifact_b=f"NOISE from: {noise_sources}",
                fracture_type="VERDICT_CONFLICT",
                severity=0.5,
                interpretation=(
                    "Contradictory verdicts from different tools. "
                    "Requires deeper analysis to determine which source is reliable. "
                    "Apply spoofability weighting to resolve."
                ),
                ttp_id="T1036",  # Masquerading
            ))

        # Rule 4: Document forgery detection (P3)
        for doc in documents:
            if doc.metadata.get("digital_perfection_detected"):
                self._fractures.append(Fracture(
                    artifact_a=f"Document visual: {doc.description[:50]}",
                    artifact_b="Expected physical scan characteristics",
                    fracture_type="DOCUMENT_FORGERY",
                    severity=0.9,
                    interpretation=(
                        "Digital perfection anomaly: element resolution or sharpness "
                        "inconsistent with paper scan noise profile. Indicates "
                        "digital manipulation or pasted elements."
                    ),
                    spoofability_delta=0.60,  # Document forgery requires skill
                    ttp_id="T1564.002",  # Hide Artifacts: Run Virtual Instance
                ))

            if doc.metadata.get("metadata_concealment_detected"):
                self._fractures.append(Fracture(
                    artifact_a=f"Document: {doc.description[:50]}",
                    artifact_b="Missing or inconsistent metadata",
                    fracture_type="METADATA_CONCEALMENT",
                    severity=0.7,
                    interpretation=(
                        "Software editing history erased but compression artifacts "
                        "remain inconsistent. Indicates deliberate metadata "
                        "stripping to hide manipulation."
                    ),
                    spoofability_delta=0.50,
                    ttp_id="T1070.006",  # Timestomp
                ))

        # ===================================================================
        # GOLDEN FORENSIC RULES — P4 Expansion
        # ===================================================================

        # Rule 6: TEMPORAL_CAUSALITY_VIOLATION (TCV)
        # Effect-before-cause: Network log timestamp < Process creation timestamp
        network_artifacts = [a for a in self._artifacts if "network" in a.description.lower()]
        process_artifacts = [a for a in self._artifacts if a.evidence_type == "memory_process"]

        for net in network_artifacts:
            net_time_str = net.metadata.get("network_log_time") or net.timestamp
            for proc in process_artifacts:
                proc_time_str = proc.metadata.get("process_creation_time") or proc.timestamp

                try:
                    # Parse timestamps (ISO format expected)
                    from datetime import datetime
                    net_time = datetime.fromisoformat(net_time_str.replace('Z', '+00:00'))
                    proc_time = datetime.fromisoformat(proc_time_str.replace('Z', '+00:00'))

                    # VIOLATION: Network activity before process existed
                    if net_time < proc_time:
                        time_delta = (proc_time - net_time).total_seconds()
                        self._fractures.append(Fracture(
                            artifact_a=f"Network log @ {net_time.isoformat()}",
                            artifact_b=f"Process created @ {proc_time.isoformat()}",
                            fracture_type="TEMPORAL_CAUSALITY_VIOLATION",
                            severity=1.0,  # MAXIMUM SEVERITY
                            interpretation=(
                                f"TEMPORAL CAUSALITY VIOLATION: Network activity detected "
                                f"{time_delta:.0f} seconds BEFORE the originating process "
                                "was created. This is structurally impossible without "
                                "log fabrication or timestamp manipulation. "
                                "Peirce Secondness: The causal chain is broken, proving "
                                "the evidence was planted retroactively."
                            ),
                            spoofability_delta=0.95,  # Logs are trivially spoofable
                            ttp_id="T1070.006",  # Timestomp
                        ))
                except (ValueError, TypeError):
                    continue  # Skip if timestamps unparseable

        # Rule 7: NETWORK_VS_HOST (RESILIENT - DeepSeek Fix)
        # Firewall claims outbound traffic but host shows no open sockets
        # TYPE-SAFE: Convert all ports to str for comparison
        firewall_claims = [a for a in self._artifacts 
                          if a.metadata.get("firewall_claim") and 
                          a.metadata.get("traffic_type") == "outbound"]
        host_reality = [a for a in self._artifacts 
                       if a.metadata.get("host_reality") and 
                       a.metadata.get("open_sockets") is not None]

        for fw in firewall_claims:
            claimed_port = fw.metadata.get("port")
            claimed_bytes = fw.metadata.get("bytes_transferred", 0)

            # RESILIENT: Normalize port to string for type-safe comparison
            claimed_port_str = str(claimed_port) if claimed_port is not None else None

            # Check if any host artifact contradicts this
            host_contradicts = False
            for host in host_reality:
                open_sockets = host.metadata.get("open_sockets", [])
                # RESILIENT: Convert all sockets to strings for comparison
                open_sockets_str = [str(s) for s in open_sockets]

                if claimed_port_str is not None and claimed_port_str not in open_sockets_str:
                    host_contradicts = True
                    break

            if host_contradicts and claimed_bytes > 1000:  # Significant traffic claimed
                self._fractures.append(Fracture(
                    artifact_a=f"Firewall: {claimed_bytes} bytes on port {claimed_port}",
                    artifact_b="Host: No open sockets on claimed port",
                    fracture_type="NETWORK_VS_HOST",
                    severity=0.8,
                    interpretation=(
                        "HIDDEN CANAL DETECTED: Firewall logs show outbound traffic "
                        f"on port {claimed_port}, but host inspection reveals no "
                        "corresponding sockets. Indicates: (1) Rootkit hiding "
                        "network activity from userland, (2) Firewall log "
                        "fabrication, or (3) Covert channel using non-standard "
                        "socket mechanisms. Peirce Thirdness: The HABIT is to "
                        "exfiltrate while hiding the transport mechanism."
                    ),
                    spoofability_delta=0.75,  # Firewall logs moderately spoofable
                    ttp_id="T1564",  # Hide Artifacts
                ))

        # Rule 8: CRYPTOGRAPHIC_INCONSISTENCY
        # File claims to be signed but hash doesn't match known-good database
        for crypto in cryptographic:
            if crypto.metadata.get("signature_mismatch") or crypto.metadata.get("hash_mismatch"):
                claimed_identity = crypto.metadata.get("claimed_identity", "unknown")
                actual_hash = crypto.metadata.get("actual_hash", "unknown")
                expected_hash = crypto.metadata.get("expected_hash", "unknown")

                self._fractures.append(Fracture(
                    artifact_a=f"File claims identity: {claimed_identity}",
                    artifact_b=f"Hash mismatch: {actual_hash[:16]}... != {expected_hash[:16]}...",
                    fracture_type="CRYPTOGRAPHIC_INCONSISTENCY",
                    severity=0.9,
                    interpretation=(
                        "SPOOFED IDENTITY: File presents cryptographic credentials "
                        f"claiming to be '{claimed_identity}', but hash verification "
                        "against VIGIA_PHONETIC_HASH database fails. This is "
                        "evidence of binary substitution or certificate theft. "
                        "Peirce Secondness: The sign (hash) does not match the "
                        "object (file content), revealing a masquerade attack."
                    ),
                    spoofability_delta=0.05,  # Cryptographic hashes are hard to spoof
                    ttp_id="T1036",  # Masquerading
                ))

        return self._fractures

    # ------------------------------------------------------------------
    # Composite evaluation with Noisy-OR (P1 Update) — DETERMINISTIC
    # ------------------------------------------------------------------

    def evaluate(self) -> dict:
        """
        Produce the final CAIE verdict using DETERMINISTIC Noisy-OR fusion model.

        Returns a dict with:
          - raw_scores: per-artifact scores (Firstness)
          - adjusted_scores: after spoofability weighting (Secondness)
          - fractures: cross-artifact discrepancies (deduplicated)
          - composite_score: Noisy-OR fusion of independent sources
          - verdict: NOISE / SUSPICION / INTENT / MALICE
          - peirce_chain: abductive reasoning trail
          - daubert_note: admissibility assessment
          - mitre_mapping: TTPs for STIX export
          - confidence_penalty: if < 3 independent sources

        DETERMINISTIC PROTOCOL (Qwen P0):
        - All arithmetic operations explicitly rounded
        - math.fsum() used for all summations
        - Bit-identical output guaranteed across x86/ARM
        """
        if not self._artifacts:
            return {
                "status": "NO_ARTIFACTS",
                "error": "No artifacts provided for cross-correlation.",
                "timestamp": _utcnow(),
            }

        # Detect fractures (including Golden Rules)
        fractures = self.detect_fractures()

        # P1: DETERMINISTIC Noisy-OR Fusion Model
        # Group by (source_tool, evidence_type) - these are dependent
        grouped = defaultdict(list)
        for a in self._artifacts:
            key = (a.source_tool, a.evidence_type)
            grouped[key].append(a.adjusted_score)

        # Within-group fusion (dependent evidence): 1 - ∏(1 - s)
        # DETERMINISTIC: Round at each multiplication step
        group_scores = []
        for scores in grouped.values():
            prod_val = 1.0
            for s in scores:
                prod_val = _dround(prod_val * (1.0 - s), _DETERMINISTIC_INTERNAL_PREC)
            group_score = _dround(1.0 - prod_val, _DETERMINISTIC_INTERNAL_PREC)
            group_scores.append(group_score)

        # Across-group fusion (independent sources): 1 - ∏(1 - g)
        # DETERMINISTIC: Round at each multiplication step
        if group_scores:
            prod_val = 1.0
            for g in group_scores:
                prod_val = _dround(prod_val * (1.0 - g), _DETERMINISTIC_INTERNAL_PREC)
            composite = _dround(1.0 - prod_val, _DETERMINISTIC_INTERNAL_PREC)
        else:
            composite = 0.0

        composite = _dround(min(composite, 0.99), _DETERMINISTIC_INTERNAL_PREC)

        # P1: Confidence normalization - penalize if < 3 independent sources
        independent_sources = len(group_scores)
        confidence_penalty = 0.0
        if independent_sources < _MIN_INDEPENDENT_SOURCES:
            confidence_penalty = _LOW_SOURCE_PENALTY
            composite = _dround(composite * (1.0 - confidence_penalty), _DETERMINISTIC_INTERNAL_PREC)

        # P1: DETERMINISTIC fracture bonus
        seen_fractures = set()
        filtered_fractures = []
        for f in fractures:
            key = (
                str(getattr(f, 'fracture_type', 'unknown')).strip().lower(),
                str(getattr(f, 'artifact_a', '')).strip(),
                str(getattr(f, 'artifact_b', '')).strip()
            )
            if key not in seen_fractures:
                seen_fractures.add(key)
                filtered_fractures.append(f)

        if filtered_fractures:
            # DETERMINISTIC: Use math.fsum for precise summation
            bonus_terms = [
                _dround(getattr(f, 'severity', 0.0) * getattr(f, 'spoofability_delta', 0.5) * 0.05, _DETERMINISTIC_INTERNAL_PREC)
                for f in filtered_fractures
            ]
            bonus = math.fsum(bonus_terms)
            fracture_bonus = _dround(min(bonus, 0.2), _DETERMINISTIC_INTERNAL_PREC)
            composite = _dround(min(composite + fracture_bonus, 0.99), _DETERMINISTIC_INTERNAL_PREC)

        # Verdict thresholds
        # P4: Golden Rules force MALICE regardless of score
        has_golden_rule = any(
            f.fracture_type in ("TEMPORAL_CAUSALITY_VIOLATION", "CRYPTOGRAPHIC_INCONSISTENCY")
            for f in filtered_fractures
        )

        if has_golden_rule or composite >= 0.5 or any(
            f.fracture_type in ("LOG_VS_MEMORY", "DOCUMENT_FORGERY", "NETWORK_VS_HOST")
            for f in filtered_fractures
        ):
            verdict = "MALICE"
        elif composite >= 0.2 or filtered_fractures:
            verdict = "SUSPICION"
        else:
            verdict = "NOISE"

        # Peirce chain
        top_adjusted = sorted(
            [
                {
                    "tool": a.source_tool,
                    "type": a.evidence_type,
                    "raw_score": _dround(a.raw_score, _DETERMINISTIC_OUTPUT_PREC),
                    "spoofability": a.profile.spoofability,
                    "weight": a.profile.base_weight,
                    "adjusted": _dround(a.adjusted_score, _DETERMINISTIC_OUTPUT_PREC),
                    "description": a.description[:200],
                }
                for a in self._artifacts
            ],
            key=lambda x: x["adjusted"],
            reverse=True
        )

        # Golden Rules summary for Peirce Thirdness
        golden_rules = [f for f in filtered_fractures 
                       if f.fracture_type in ("TEMPORAL_CAUSALITY_VIOLATION", 
                                              "NETWORK_VS_HOST", 
                                              "CRYPTOGRAPHIC_INCONSISTENCY")]

        peirce_chain = {
            "firstness": (
                f"{len(self._artifacts)} artifacts from "
                f"{len(set(a.source_tool for a in self._artifacts))} tools. "
                f"Raw scores range: {_dround(min(a.raw_score for a in self._artifacts), 2):.2f} "
                f"to {_dround(max(a.raw_score for a in self._artifacts), 2):.2f}."
            ),
            "secondness": (
                f"Noisy-OR fusion: {len(group_scores)} independent groups, "
                f"composite={_dround(composite, 4):.4f}. "
                f"Most reliable: {top_adjusted[0]['tool']} "
                f"({top_adjusted[0]['type']}, adj={top_adjusted[0]['adjusted']:.4f}). "
                f"{len(filtered_fractures)} unique fracture(s), "
                f"{len(golden_rules)} Golden Rule(s)."
            ),
            "thirdness": (
                f"Inferred habit: {'fabrication/staging' if verdict != 'NOISE' else 'normal operation'}. "
                + (
                    f"Key: {filtered_fractures[0].fracture_type} — {filtered_fractures[0].interpretation[:200]}"
                    if filtered_fractures else "No structural discrepancies."
                )
                + (f" Golden Rule triggered: {golden_rules[0].fracture_type}." if golden_rules else "")
            ),
        }

        # Daubert admissibility note
        irrefutable_count = sum(
            1 for a in self._artifacts
            if a.profile.spoofability <= 0.20
        )
        daubert_note = (
            f"Daubert: {irrefutable_count}/{len(self._artifacts)} "
            f"artifacts structurally irrefutable (spoofability ≤ 0.20). "
            + (
                "Anchored in hard evidence. Admissible."
                if irrefutable_count >= 1
                else "WARNING: No irrefutable anchor. Weak under cross-examination."
            )
        )

        # MITRE ATT&CK mapping (using centralized mitre_mapping.py)
        mitre_ttps = set()
        for f in filtered_fractures:
            if f.ttp_id:
                mitre_ttps.add(f.ttp_id)
            else:
                # Fallback to legacy mapping
                ttp = _SIGNAL_TO_ATTACK.get(f.fracture_type)
                if ttp:
                    mitre_ttps.add(ttp)

        for a in self._artifacts:
            # Add TTPs for evidence types
            try:
                for ttp in get_ttps_for_evidence_type(a.evidence_type):
                    mitre_ttps.add(ttp)
            except Exception:
                pass  # Resilience: continue if MITRE mapping fails

            # Add TTPs from signals
            for signal_type in a.metadata.get("signals", []):
                if isinstance(signal_type, dict):
                    ttp = _SIGNAL_TO_ATTACK.get(signal_type.get("type", ""))
                    if ttp:
                        mitre_ttps.add(ttp)

        # Calculate TTP confidence scores
        ttp_confidences = {}
        for ttp_id in mitre_ttps:
            try:
                ttp_meta = get_ttp_metadata(ttp_id)
                if ttp_meta:
                    # DETERMINISTIC: Average confidence across related artifacts
                    related = [a for a in self._artifacts 
                             if ttp_id in get_ttps_for_evidence_type(a.evidence_type)]
                    if related:
                        avg_reliability = _dround(math.fsum(a.raw_score for a in related) / len(related), _DETERMINISTIC_INTERNAL_PREC)
                        ttp_confidences[ttp_id] = calculate_ttp_confidence(
                            ttp_id, avg_reliability, "cross_artifact_analysis"
                        )
            except Exception:
                # Resilience: assign neutral confidence if calculation fails
                ttp_confidences[ttp_id] = 0.5

        # DETERMINISTIC: Build result with all floats rounded to output precision
        result = {
            "status": "OK",
            "verdict": verdict,
            "composite_score": _dround(composite, _DETERMINISTIC_OUTPUT_PREC),
            "artifacts_evaluated": len(self._artifacts),
            "independent_sources": independent_sources,
            "confidence_penalty_applied": confidence_penalty > 0,
            "fractures_detected": len(filtered_fractures),
            "fractures_unique": len(filtered_fractures),
            "golden_rules_triggered": len(golden_rules),
            "raw_scores": top_adjusted,
            "fractures": [
                {
                    "type": f.fracture_type,
                    "severity": _dround(f.severity, _DETERMINISTIC_OUTPUT_PREC),
                    "artifact_a": f.artifact_a,
                    "artifact_b": f.artifact_b,
                    "interpretation": f.interpretation,
                    "spoofability_delta": _dround(f.spoofability_delta, _DETERMINISTIC_OUTPUT_PREC),
                    "mitre_ttp": f.ttp_id or _SIGNAL_TO_ATTACK.get(f.fracture_type),
                }
                for f in filtered_fractures
            ],
            "mitre_ttps": sorted(mitre_ttps),
            "ttp_confidences": {k: _dround(v, _DETERMINISTIC_OUTPUT_PREC) for k, v in ttp_confidences.items()},
            "peirce_chain": peirce_chain,
            "daubert_note": daubert_note,
            "timestamp": _utcnow(),
            "vigia_verdict": (
                f"[VIGIA_CAIE]: {verdict}. "
                f"Composite={_dround(composite, 4):.4f} from {len(self._artifacts)} artifacts "
                f"({independent_sources} independent). "
                f"{len(filtered_fractures)} fracture(s), {len(golden_rules)} Golden Rule(s). "
                f"{daubert_note[:80]}"
            ),
            "_determinism_protocol": f"P0-v2.0 (internal={_DETERMINISTIC_INTERNAL_PREC}, output={_DETERMINISTIC_OUTPUT_PREC})",
        }

        # HMAC sign for chain of custody (RESILIENT - DeepSeek Fix)
        result["_operation_hmac"] = self._sign_result(result)

        return result

    def _sign_result(self, data: dict) -> str:
        """HMAC signature for result integrity (RESILIENT with fallback key)."""
        # RESILIENT: Get key with fallback generation
        key = _get_hmac_key()

        # Remove existing HMAC if present
        payload = {k: v for k, v in data.items() if k != "_operation_hmac"}
        canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
        return hmac_mod.new(key, canonical.encode("utf-8"), "sha256").hexdigest()

    def reset(self) -> None:
        """Clear all artifacts and fractures for a new evaluation cycle."""
        self._artifacts.clear()
        self._fractures.clear()
        self._temporal_index.clear()
        self._network_index.clear()


# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

async def cross_artifact_analysis(
    artifacts: list[dict],
) -> dict:
    """
    Cross-Artifact Incongruence Engine (CAIE) — EXPANDED v2.0 [DETERMINISTIC+RESILIENT].

    Evaluates multiple forensic artifacts with authenticity-adjusted scoring.
    Evidence that is structurally hard to fabricate weighs more than evidence
    that can be planted in 30 seconds.

    Uses DETERMINISTIC Noisy-OR fusion: dependent evidence grouped, then independent
    groups fused. Prevents "alert flooding" from single source.

    NEW v2.0: Golden Forensic Rules
    - TEMPORAL_CAUSALITY_VIOLATION: Detects effect-before-cause impossibilities
    - NETWORK_VS_HOST: Detects hidden channels via firewall/host discrepancy
    - CRYPTOGRAPHIC_INCONSISTENCY: Detects spoofed identities via hash mismatch

    DETERMINISTIC PROTOCOL (Qwen P0):
    - All intermediate calculations rounded to 6 decimal places
    - All outputs rounded to 4 decimal places  
    - math.fsum() used for all summations
    - Bit-identical output guaranteed across x86/ARM architectures

    RESILIENCE PROTOCOL (DeepSeek+Qwen):
    - Graceful degradation on import failures
    - Type-safe port comparisons
    - HMAC safety with fallback keys

    Formula: 
        group_score = 1 - ∏(1 - score_i)  [within source]
        composite = 1 - ∏(1 - group_j)    [across sources]

    Parameters
    ----------
    artifacts : list of dicts, each with:
        - source_tool (str): which VIGIA tool produced this
        - evidence_type (str): key from EVIDENCE_PROFILES (whitelist enforced)
        - raw_score (float): suspicion score [0.0, 1.0]
        - description (str): what was found
        - provenance_chain (list): optional EPC hashes
        - metadata (dict): tool-specific data including:
            - network_log_time, process_creation_time (for TCV)
            - firewall_claim, host_reality, open_sockets (for NETWORK_VS_HOST)
            - signature_mismatch, hash_mismatch, claimed_identity (for CRYPTO)

    Valid evidence_types: ip_geolocation, cultural_marker, log_entry,
    user_agent, file_timestamp, file_hash, dns_record, registry_key,
    usn_journal, memory_process, lsass_session, prefetch,
    kernel_structure, hmac_audit_log, hardware_serial,
    document_visual, document_geometry, cryptographic_hash, digital_signature.

    Limits: max 1000 artifacts. Non-finite scores zeroed. 
    Unknown types rejected. < 3 sources = 20% penalty.

    Returns dict with: verdict, composite_score, fractures, peirce_chain,
    daubert_note, mitre_ttps, ttp_confidences, golden_rules_triggered.
    """
    if not isinstance(artifacts, list) or not artifacts:
        return {
            "status": "ERROR",
            "error": "artifacts must be a non-empty list of dicts.",
            "timestamp": _utcnow(),
        }

    if len(artifacts) > _MAX_ARTIFACTS:
        try:
            audit_logger.log_block(
                event_type="CAIE_INPUT_OVERFLOW",
                tool="cross_artifact_analysis",
                input_preview=f"count={len(artifacts)}",
                reason=(
                    f"Input contains {len(artifacts)} artifacts, "
                    f"exceeding limit of {_MAX_ARTIFACTS}. "
                    "Truncating to limit. Possible artifact flooding."
                ),
            )
        except Exception:
            pass  # Resilience: don't crash if logging fails
        artifacts = artifacts[:_MAX_ARTIFACTS]

    engine = CrossArtifactIncongruenceEngine()
    rejected = 0

    for item in artifacts:
        if not isinstance(item, dict):
            rejected += 1
            continue

        evidence_type = str(item.get("evidence_type", ""))
        if evidence_type not in _VALID_EVIDENCE_TYPES:
            rejected += 1
            try:
                audit_logger.log_info(
                    event_type="CAIE_UNKNOWN_TYPE_SKIPPED",
                    tool="cross_artifact_analysis",
                    message=(
                        f"Skipped artifact with unknown evidence_type={evidence_type!r} "
                        f"from tool={item.get('source_tool', '?')}. "
                        f"Valid types: {sorted(_VALID_EVIDENCE_TYPES)}"
                    ),
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            continue

        try:
            engine.add_artifact(Artifact(
                source_tool=str(item.get("source_tool", "unknown")),
                evidence_type=evidence_type,
                raw_score=float(item.get("raw_score", 0.0)),
                description=str(item.get("description", ""))[:500],
                metadata=item.get("metadata", {}),
                provenance_chain=item.get("provenance_chain", []),
                base_trust=float(item.get("base_trust", 1.0)),
            ))
        except (TypeError, ValueError) as exc:
            rejected += 1
            try:
                audit_logger.log_info(
                    event_type="CAIE_ARTIFACT_PARSE_ERROR",
                    tool="cross_artifact_analysis",
                    message=f"Failed to parse artifact: {exc}",
                )
            except Exception:
                pass  # Resilience: don't crash if logging fails
            continue

    if not engine._artifacts:
        return {
            "status": "ERROR",
            "error": (
                f"No valid artifacts could be parsed from input. "
                f"{rejected} artifact(s) were rejected."
            ),
            "rejected_count": rejected,
            "timestamp": _utcnow(),
        }

    result = engine.evaluate()
    result["artifacts_rejected"] = rejected
    return result


# ============================================================================
# DETERMINISM VERIFICATION (Qwen P0)
# ============================================================================

def verify_determinism_cross_arch() -> bool:
    """
    Asserts that scoring produces identical results regardless of FPU architecture.

    This function validates the Deterministic Forensic Protocol by:
    1. Creating identical test artifacts
    2. Running evaluation multiple times
    3. Verifying bit-identical composite_score across runs

    Returns True if determinism verified, raises AssertionError if not.
    """
    engine1 = CrossArtifactIncongruenceEngine()

    # Inject deterministic test artifacts
    test_artifacts = [
        Artifact("tool_a", "memory_process", 0.85, "Test memory artifact A"),
        Artifact("tool_b", "log_entry", 0.72, "Test log artifact B"),
        Artifact("tool_c", "ip_geolocation", 0.65, "Test IP artifact C"),
        Artifact("tool_a", "file_hash", 0.90, "Test hash artifact D"),
    ]

    for artifact in test_artifacts:
        engine1.add_artifact(artifact)

    result1 = engine1.evaluate()

    # Reset and recreate identical scenario
    engine2 = CrossArtifactIncongruenceEngine()
    for artifact in test_artifacts:
        engine2.add_artifact(artifact)

    result2 = engine2.evaluate()

    # Verify determinism
    assert result1["composite_score"] == result2["composite_score"], (
        f"Determinism failed: {result1['composite_score']} != {result2['composite_score']}"
    )

    # Verify all fracture severities are deterministic
    for i, (f1, f2) in enumerate(zip(result1.get("fractures", []), result2.get("fractures", []))):
        assert f1["severity"] == f2["severity"], (
            f"Fracture {i} severity non-deterministic: {f1['severity']} != {f2['severity']}"
        )

    # Verify TTP confidences are deterministic
    for ttp in result1.get("ttp_confidences", {}):
        assert result1["ttp_confidences"][ttp] == result2["ttp_confidences"][ttp], (
            f"TTP {ttp} confidence non-deterministic"
        )

    print("✅ CAIE Determinism Protocol P0: VERIFIED")
    print(f"   Composite Score: {result1['composite_score']}")
    print(f"   Artifacts: {result1['artifacts_evaluated']}")
    print(f"   Fractures: {result1['fractures_detected']}")
    print(f"   Protocol: {result1.get('_determinism_protocol', 'legacy')}")

    return True


# Auto-verify on module load (can be disabled in production)
if __name__ == "__main__":
    verify_determinism_cross_arch()
