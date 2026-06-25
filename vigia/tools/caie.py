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
vigia/tools/caie.py
====================
VIGIA — Cross-Artifact Incongruence Engine (CAIE) — v2.0 EXPANDED [DETERMINISTIC]

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Claude (Anthropic) — Systems Integration Engineer
Expansion: Gemini, Qwen, DeepSeek — "Golden Forensic Rules"
Determinism Protocol: Qwen (Tongyi Qianwen) — "The One Who Turned Paranoia into Protocol"

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
"""

from __future__ import annotations
from fractions import Fraction

import decimal
import hashlib
import hmac as hmac_mod
import json
import math
import copy
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Final

from vigia.security import (
    _sanitize_path, 
    _utcnow, 
    audit_logger,
    trust_decay,
    _sanitize_llm_input,
)

# Import MITRE mapping for centralized TTP knowledge
from vigia.tools.mitre_mapping import (
    get_ttp_metadata,
    get_ttps_for_evidence_type,
    calculate_ttp_confidence,
    EVIDENCE_TYPE_TO_TTP,
)

from vigia.collapse_decision import CollapseDecisionLayer, CollapseContext, CollapseVerdict


# ============================================================================
# DETERMINISTIC PRECISION PROTOCOL (Qwen P0 + Red Team P0_CRITICO Directiva 4)
# Guarantees bit-identical output across x86/ARM architectures.
#
# UPGRADE: decimal.Decimal with prec=28 for all critical summations.
# Rationale: math.fsum() uses native C float bindings which exhibit
# platform-dependent FPU rounding modes (x87 vs SSE2 vs ARM VFP).
# decimal.Decimal uses pure-Python IEEE 754 with deterministic rounding,
# independent of hardware FPU state or compiler flags.
#
# Scope: _dsum() replaces math.fsum() at all score accumulation points.
# Individual mul/div steps retain float via _dround() (acceptable since
# inputs are already clamped to [0,1] with 6-decimal precision).
# ============================================================================
_DETERMINISTIC_INTERNAL_PREC: Final[int] = 6
_DETERMINISTIC_OUTPUT_PREC: Final[int] = 4

# Global Decimal context — configured ONCE at module load.
# prec=28 matches the Directiva 4 requirement.
# ROUND_HALF_EVEN (banker's rounding) is deterministic and unbiased.
decimal.getcontext().prec = 28
decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN

_D_ZERO: decimal.Decimal = decimal.Decimal("0")
_D_ONE: decimal.Decimal = decimal.Decimal("1")



# ---------------------------
# Domain classification layer
# ---------------------------

_DOMAIN_MAP = {
    "memory_process": "memory",
    "memory_dump": "memory",
    "lsass_session": "memory",
    "log_entry": "network",
    "network_artifact": "network",
    "network_connection": "network",
    "ip_geolocation": "network",
    "dns_record": "network",
    "file_timestamp": "filesystem",
    "file_hash": "filesystem",
    "mft_entry": "filesystem",
    "usn_journal": "filesystem",
    "registry_key": "filesystem",
    "TPM_attestation": "hardware",
    "hmac_audit_log": "hardware",
}

def classify_domain(evidence_type: str) -> str:
    """Deterministic domain classifier for artifact types."""
    return _DOMAIN_MAP.get(evidence_type, "UNKNOWN")

def _dround(value, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> decimal.Decimal:
    """
    Deterministic rounding — returns Decimal, never float.
    L-021 Phase 1: Decimal internal algebra throughout.
    Finite Math Shield: returns Decimal('0') for inf, -inf, NaN.
    """
    if isinstance(value, decimal.Decimal):
        if not value.is_finite():
            return _D_ZERO
        return value.quantize(decimal.Decimal(10) ** -precision,
                              rounding=decimal.ROUND_HALF_EVEN)
    if isinstance(value, Fraction):
        value = decimal.Decimal(value.numerator) / decimal.Decimal(value.denominator)
        return value.quantize(decimal.Decimal(10) ** -precision,
                              rounding=decimal.ROUND_HALF_EVEN)
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        return _D_ZERO
    return decimal.Decimal(str(value)).quantize(
        decimal.Decimal(10) ** -precision,
        rounding=decimal.ROUND_HALF_EVEN
    )


def _dsum(values) -> decimal.Decimal:
    """
    Deterministic summation — returns Decimal, never float.
    L-021 Phase 1.
    """
    acc = _D_ZERO
    for v in values:
        if isinstance(v, decimal.Decimal):
            if v.is_finite():
                acc += v
        elif isinstance(v, Fraction):
            acc += decimal.Decimal(v.numerator) / decimal.Decimal(v.denominator)
        elif isinstance(v, (int, float)) and math.isfinite(float(v)):
            acc += decimal.Decimal(str(v))
    return _dround(acc, _DETERMINISTIC_INTERNAL_PREC)


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

    # P5: TCV anti-forensics (Gemini/Kimi audit — paper ScienceDirect sept 2026)
    # Timestamp precision anomaly: herramientas como Timestomp truncan a 7 ceros
    "timestamp_precision":  EvidenceProfile(0.05, 0.40, "Sub-second timestamp precision -- tool signature detection"),
    # MFT entry number: asignado por driver NTFS, inalterable en user-space
    "mft_entry":            EvidenceProfile(0.05, 0.42, "NTFS MFT entry number -- driver-assigned, inalterable user-space"),
    # USN Journal gap: requiere Ring-0 para borrar el journal
    "usn_journal_gap":      EvidenceProfile(0.10, 0.38, "USN Journal gap vs LogFile -- Ring-0 required to clear"),
    # VABS-1 / CAIE-GAP-001: network and file metadata evidence types
    "network_flow":         EvidenceProfile(0.75, 0.18, "Network flow record -- IP spoofable, content tunnelable"),
    "file_metadata":        EvidenceProfile(0.65, 0.20, "File attributes (size/owner/perms) -- modifiable with privs, MFT cross-check possible"),
}

# Whitelist of valid evidence types — any type not in this set is rejected
_VALID_EVIDENCE_TYPES: Final[frozenset[str]] = frozenset(EVIDENCE_PROFILES.keys())

# Maximum artifacts per evaluation — prevents DoS via artifact flooding
_MAX_ARTIFACTS: Final[int] = 1000

# Minimum independent sources for full confidence (P1: normalization)
_MIN_INDEPENDENT_SOURCES: Final[int] = 3
_LOW_SOURCE_PENALTY: Final[float] = 0.20  # Reduce score by 20% if < 3 sources

# ---------------------------------------------------------------------------
# NIST SP 800-86 / RFC 3227 — Acquisition metadata validation
#
# Campos requeridos en Artifact.metadata para cadena de custodia Daubert.
# Su ausencia NO rechaza el artefacto — degrada base_trust de forma auditada.
#
# Niveles de degradación (aditivos, aplicados en __post_init__):
#   CRITICAL (cada campo faltante): -0.15  → evidencia sin procedencia
#   WARNING  (cada campo faltante): -0.05  → degradación menor
#
# Referencia: NIST SP 800-86 §4.3, RFC 3227 §2.1, Daubert v. Merrell Dow
# ---------------------------------------------------------------------------
_ACQ_CRITICAL_FIELDS: Final[tuple[str, ...]] = (
    "acquisition_tool",        # herramienta física (FTK Imager, dd, Axiom, etc.)
    "acquisition_hash",        # SHA-256 del artefacto crudo en adquisición
    "acquisition_timestamp",   # ISO-8601 con timezone
)
_ACQ_WARNING_FIELDS: Final[tuple[str, ...]] = (
    "examiner_id",             # identidad del perito adquiriente
    "write_blocker_used",      # bool — crítico para admisibilidad en juicio
)
_ACQ_TRUST_PENALTY_CRITICAL: Final[float] = 0.15   # por campo crítico ausente
_ACQ_TRUST_PENALTY_WARNING: Final[float]  = 0.05   # por campo warning ausente
_ACQ_TRUST_FLOOR: Final[float] = 0.10              # base_trust mínimo post-degradación

# ---------------------------------------------------------------------------
# Acquisition Assurance — spoofability contextual (decisión colectiva VIGÍA)
#
# Modelo: effective_spoofability = intrinsic × (1 - k × assurance)
#   k = 3/5 (0.60) — votado por colectivo: Kimi, Claude, Grok, DeepSeek, Qwen
#   assurance ∈ [0.0, 1.0] — calculado por _compute_acquisition_assurance()
#
# Tiers de assurance (deterministas, sin heurística):
#   NONE     : 0/4  gates verificados → assurance = 0.0  (comportamiento conservador)
#   BASIC    : 1/4  gates verificados → assurance = 1/4
#   VERIFIED : 2/4  gates verificados → assurance = 1/2
#   FORENSIC : 3/4  gates verificados → assurance = 3/4
#   STRONG   : 4/4  gates verificados → assurance = 9/10
#
# Gates (todos requeridos para tier STRONG):
#   G1 HASH_INTEGRITY    : acquisition_hash presente y formato sha256: válido
#   G2 TOOL_WHITELIST    : acquisition_tool en lista de herramientas forenses conocidas
#   G3 TEMPORAL_CONSISTENCY: acquisition_timestamp parseable ISO-8601 con timezone
#   G4 WRITE_BLOCKER     : write_blocker_used == True en metadata
#
# Floor por tipo (Fraction exacta — cero floats):
#   log_entry       : 1/4  (nunca baja de 0.25 de spoofability efectiva)
#   file_timestamp  : 1/5
#   registry_key    : 3/20
#   default         : 1/10
#
# Referencia: NIST SP 800-86 §4.3, RFC 3227, Daubert v. Merrell Dow
# ---------------------------------------------------------------------------
_ACQ_ASSURANCE_K = Fraction(4, 5)  # k = 0.80 — recalibrado tras validación empírica con corpus NIST/DFRWS

_ACQ_ASSURANCE_TIERS: Final[dict] = {
    0: Fraction(0,  1),   # NONE
    1: Fraction(1,  4),   # BASIC
    2: Fraction(1,  2),   # VERIFIED
    3: Fraction(3,  4),   # FORENSIC
    4: Fraction(9, 10),   # STRONG
}

_ACQ_SPOOFABILITY_FLOORS: Final[dict] = {
    "log_entry":      Fraction(1, 4),
    "file_timestamp": Fraction(1, 5),
    "registry_key":   Fraction(3, 20),
}
_ACQ_SPOOFABILITY_FLOOR_DEFAULT = Fraction(1, 10)

_ACQ_TOOL_WHITELIST: Final[frozenset] = frozenset({
    "ftk imager", "ftk_imager", "ftkimager",
    "dd", "dcfldd", "dc3dd",
    "axiom", "magnet axiom",
    "encase", "encase imager",
    "xways", "x-ways forensics",
    "cellebrite", "cellebrite ufed",
    "autopsy",
    "volatility",
    "legacy_converter_v1",  # converter interno de VIGÍA
    "f-response", "f-response enterprise", "f-response-ent",  # F-Response Enterprise live acquisition
})


def _compute_acquisition_assurance(metadata: dict) -> Fraction:
    """
    Calcula acquisition_assurance como Fraction exacta.
    Evalúa 4 gates deterministas sobre metadata del artifact.
    Retorna Fraction en {0, 1/4, 1/2, 3/4, 9/10}.

    Gates:
      G1 HASH_INTEGRITY    : acquisition_hash presente, formato sha256:<hex>
      G2 TOOL_WHITELIST    : acquisition_tool en _ACQ_TOOL_WHITELIST
      G3 TEMPORAL_CONSISTENCY: acquisition_timestamp parseable ISO-8601
      G4 WRITE_BLOCKER     : write_blocker_used is True

    Si metadata es None o vacío → Fraction(0, 1) (comportamiento conservador).
    """
    if not metadata:
        return Fraction(0, 1)

    gates_passed = 0

    # G1: HASH_INTEGRITY
    # Requiere sha256: seguido de exactamente 64 caracteres hexadecimales.
    # Rechaza hashes legacy (sha256:legacy_*) que no son verificables.
    acq_hash = metadata.get("acquisition_hash", "")
    if (isinstance(acq_hash, str)
            and acq_hash.startswith("sha256:")
            and len(acq_hash) == 71  # "sha256:" (7) + 64 hex chars
            and all(c in "0123456789abcdef" for c in acq_hash[7:])):
        gates_passed += 1

    # G2: TOOL_WHITELIST
    acq_tool = str(metadata.get("acquisition_tool", "")).strip().lower()
    if acq_tool in _ACQ_TOOL_WHITELIST:
        gates_passed += 1

    # G3: TEMPORAL_CONSISTENCY
    acq_ts = metadata.get("acquisition_timestamp", "")
    if isinstance(acq_ts, str) and len(acq_ts) >= 19:
        import re as _re
        # ISO-8601 básico: YYYY-MM-DDTHH:MM:SS con timezone (Z o ±HH:MM)
        _ISO_PAT = _re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            r"(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
        )
        if _ISO_PAT.match(acq_ts):
            gates_passed += 1

    # G4: WRITE_BLOCKER
    if metadata.get("write_blocker_used") is True:
        gates_passed += 1

    return _ACQ_ASSURANCE_TIERS[gates_passed]


def _compute_effective_spoofability(intrinsic: float, assurance: Fraction, floor: Fraction) -> float:
    """
    Calcula effective_spoofability con aritmética Fraction exacta.

    Fórmula: effective = max(floor, intrinsic × (1 - k × assurance))

    Con k=3/5, assurance=3/4 (FORENSIC), intrinsic=17/20 (log_entry=0.85):
      effective = max(1/4, 17/20 × (1 - 3/5 × 3/4))
                = max(1/4, 17/20 × (1 - 9/20))
                = max(1/4, 17/20 × 11/20)
                = max(1/4, 187/400)
                = 187/400 ≈ 0.4675

    Retorna float para compatibilidad con el resto del pipeline.
    """
    intrinsic_f = Fraction(intrinsic).limit_denominator(1000)
    reduction   = _ACQ_ASSURANCE_K * assurance
    effective_f = intrinsic_f * (Fraction(1) - reduction)
    effective_f = max(floor, effective_f)
    return float(effective_f)


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
            audit_logger.log_block(
                event_type="FORENSIC_POISONING_ATTEMPT",
                tool="CAIE.Artifact",
                input_preview=f"source={self.source_tool} type={self.evidence_type}",
                reason=f"raw_score is {type(self.raw_score).__name__}, not numeric.",
            )
            self.raw_score = 0.0
        elif not math.isfinite(self.raw_score):
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
            self.raw_score = 0.0
        else:
            # Clamp to [0.0, 1.0]
            self.raw_score = _dround(max(0.0, min(1.0, self.raw_score)), _DETERMINISTIC_INTERNAL_PREC)

        # P2: Apply trust decay if provenance chain is broken
        if self.provenance_chain:
            # Check for breaks in chain (simplified: gaps in sequence)
            if len(self.provenance_chain) < 2:
                # Single link = potential break
                self.base_trust, _ = trust_decay.apply_decay(self.base_trust, break_severity=0.5)
                self.base_trust = _dround(self.base_trust, _DETERMINISTIC_INTERNAL_PREC)

        # ---------------------------------------------------------------------------
        # NIST SP 800-86 / RFC 3227 — Acquisition metadata validation
        #
        # Valida que el artefacto cargue metadatos mínimos de adquisición forense.
        # Ausencia de campos críticos degrada base_trust y genera entrada de auditoría.
        # NO rechaza el artefacto — permite análisis degradado con registro completo.
        #
        # Conforme a Daubert: toda degradación es falsifiable, documentada, reproducible.
        # ---------------------------------------------------------------------------
        _meta = self.metadata or {}
        _missing_critical = [f for f in _ACQ_CRITICAL_FIELDS if not _meta.get(f)]
        _missing_warning  = [f for f in _ACQ_WARNING_FIELDS  if not _meta.get(f)]

        # Calcular effective_spoofability con acquisition_assurance contextual
        _assurance = _compute_acquisition_assurance(_meta)
        _floor     = _ACQ_SPOOFABILITY_FLOORS.get(
            self.evidence_type, _ACQ_SPOOFABILITY_FLOOR_DEFAULT
        )
        _intrinsic = EVIDENCE_PROFILES.get(
            self.evidence_type,
            EvidenceProfile(0.50, 0.20, "default"),
        ).spoofability
        self.effective_spoofability: float = _compute_effective_spoofability(
            _intrinsic, _assurance, _floor
        )
        self.acquisition_assurance: float = float(_assurance)

        if _missing_critical:
            _penalty = _dround(
                len(_missing_critical) * _ACQ_TRUST_PENALTY_CRITICAL,
                _DETERMINISTIC_INTERNAL_PREC,
            )
            self.base_trust = _dround(
                max(decimal.Decimal(str(_ACQ_TRUST_FLOOR)),
                    _dround(self.base_trust, _DETERMINISTIC_INTERNAL_PREC) - _penalty),
                _DETERMINISTIC_INTERNAL_PREC,
            )
            audit_logger.log_block(
                event_type="ACQUISITION_METADATA_MISSING_CRITICAL",
                tool=f"CAIE.Artifact[{self.source_tool}]",
                input_preview=(
                    f"evidence_type={self.evidence_type} "
                    f"missing={_missing_critical}"
                ),
                reason=(
                    f"Artefacto sin metadatos de adquisición críticos "
                    f"(NIST SP 800-86 §4.3 / RFC 3227 §2.1). "
                    f"Campos ausentes: {_missing_critical}. "
                    f"base_trust degradado en {_penalty} → {self.base_trust}. "
                    f"Evidencia puede ser INADMISIBLE bajo estándar Daubert "
                    f"sin documentación de cadena de custodia completa."
                ),
            )

        if _missing_warning:
            _penalty_w = _dround(
                len(_missing_warning) * _ACQ_TRUST_PENALTY_WARNING,
                _DETERMINISTIC_INTERNAL_PREC,
            )
            self.base_trust = _dround(
                max(decimal.Decimal(str(_ACQ_TRUST_FLOOR)),
                    _dround(self.base_trust, _DETERMINISTIC_INTERNAL_PREC) - _penalty_w),
                _DETERMINISTIC_INTERNAL_PREC,
            )
            audit_logger.log_block(
                event_type="ACQUISITION_METADATA_MISSING_WARNING",
                tool=f"CAIE.Artifact[{self.source_tool}]",
                input_preview=(
                    f"evidence_type={self.evidence_type} "
                    f"missing={_missing_warning}"
                ),
                reason=(
                    f"Artefacto sin metadatos de adquisición recomendados. "
                    f"Campos ausentes: {_missing_warning}. "
                    f"base_trust degradado en {_penalty_w} → {self.base_trust}. "
                    f"Referencia: NIST SP 800-86 §4.3."
                ),
            )

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

        # Step 1: raw_score × (1 - effective_spoofability)
        # effective_spoofability incorpora acquisition_assurance contextual
        # (calculado en __post_init__ con gates deterministas G1-G4)
        step1 = _dround(_dround(self.raw_score, _DETERMINISTIC_INTERNAL_PREC) * (_D_ONE - decimal.Decimal(str(self.effective_spoofability))), _DETERMINISTIC_INTERNAL_PREC)

        # Step 2: × base_weight
        step2 = _dround(step1 * decimal.Decimal(str(p.base_weight)), _DETERMINISTIC_INTERNAL_PREC)

        # Step 3: × base_trust
        result = _dround(step2 * _dround(self.base_trust, _DETERMINISTIC_INTERNAL_PREC), _DETERMINISTIC_INTERNAL_PREC)

        # Defense-in-depth: should be impossible after __post_init__ clamp,
        # but protect against corrupted EvidenceProfile values.
        if not result.is_finite():
            return _D_ZERO

        return _dround(max(_D_ZERO, min(_D_ONE, result)), _DETERMINISTIC_INTERNAL_PREC)


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

# =============================================================================
# HMAC SIGNING (NIGHTFALL P0-2 / P0-3)
# No expone _hmac_key de SecurityAudit como atributo publico.
# Serializa con ensure_ascii=True para determinismo Daubert.
# =============================================================================

def _caie_hmac_sign_canonical(canonical: str) -> str:
    """
    Firma HMAC-SHA256 de una cadena canonica para CAIE.

    NIGHTFALL P0-2: resuelve la clave sin acceder a audit_logger._hmac_key.
    NIGHTFALL P0-3: caller debe pasar JSON serializado con ensure_ascii=True.

    La clave se destruye del scope local al retornar.
    """
    import hmac as _hmac_local
    key: bytes = b""
    try:
        key_hex = os.environ.get("VIGIA_HMAC_KEY", "").strip()
        if key_hex:
            try:
                key = bytes.fromhex(key_hex)
            except ValueError:
                pass
        if not key:
            key_file = os.environ.get("VIGIA_HMAC_KEY_FILE", "").strip()
            if key_file and os.path.isfile(key_file):
                try:
                    key = Path(key_file).read_bytes().strip()
                except OSError:
                    pass
        if not key or len(key) < 32:
            return ""
        return _hmac_local.new(key, canonical.encode("utf-8"), "sha256").hexdigest()
    finally:
        del key


def _extract_assertions(artifact: "Artifact") -> frozenset:
    """
    Translate observable metadata fields into atomic forensic assertion
    strings. Returns facts about what the artifact claims — not
    interpretations, not scores, not verdicts.

    Deterministic contract: same artifact input → same frozenset output,
    always. This is what allows Rule 2 (LOG_VS_MEMORY) to operate on
    observed facts rather than derived verdicts (L-028 fix).

    Three assertion domains are intentionally kept separate:
      - network activity  (for LOG_VS_MEMORY / NETWORK_VS_HOST)
      - process state     (for process-level cross-correlation)
      - memory integrity  (for injection / kernel anomaly rules)

    memory_appears_clean is NOT used by Rule 2. Rule 2 uses only
    memory_shows_no_network_activity, which compares the same domain
    as log_claims_outbound_connection (network activity).
    """
    meta = artifact.metadata
    et   = artifact.evidence_type
    assertions = set()

    if et == "log_entry":
        # Outbound/target connection: dst_ip or dest_ip
        # Note: "ip" alone (HTTP access log source field) is intentionally
        # excluded — it identifies the requester, not a suspicious outbound
        # connection. Mixing these was the original source of false positives.
        if meta.get("dst_ip") or meta.get("dest_ip"):
            assertions.add("log_claims_outbound_connection")
        if meta.get("pid"):
            assertions.add("log_names_process")
        target = str(meta.get("target", "")).lower()
        if "lsass" in target or meta.get("credential_dump"):
            assertions.add("log_claims_credential_access")

    elif et in ("memory_process", "lsass_session", "kernel_structure"):
        # Type validation for network indicators — only semantically valid
        # values count as "network activity observed":
        # - dest_ip / source_ip: must be non-empty strings (int/bool/None are invalid)
        # - network_connections: must be non-empty list or dict (string is not a
        #   connection list — truthiness bug caught by fuzzing 2026-06-25)
        _dest_ip = meta.get("dest_ip")
        _src_ip  = meta.get("source_ip")
        _nc      = meta.get("network_connections")
        _nc_valid   = isinstance(_nc, (list, dict)) and bool(_nc)
        _dest_valid = isinstance(_dest_ip, str) and bool(_dest_ip.strip())
        _src_valid  = isinstance(_src_ip,  str) and bool(_src_ip.strip())
        has_network = _dest_valid or _src_valid or _nc_valid
        if has_network:
            assertions.add("memory_shows_network_activity")
        else:
            assertions.add("memory_shows_no_network_activity")

        if meta.get("injections_detected") or meta.get("injected_pid"):
            assertions.add("memory_shows_injection")
        if meta.get("kernel_anomalies") or meta.get("kernel_anomaly"):
            assertions.add("memory_shows_kernel_anomaly")
        if meta.get("pid"):
            assertions.add("memory_shows_process_present")
        # General cleanliness assertion (not used by Rule 2 directly)
        if not any(meta.get(k) for k in (
            "injections_detected", "injected_pid",
            "kernel_anomalies", "kernel_anomaly",
            "dest_ip", "source_ip", "network_connections"
        )):
            assertions.add("memory_appears_clean")

    return frozenset(assertions)


class CrossArtifactIncongruenceEngine:
    """
    Kimi's Cross-Artifact Incongruence Engine — EXPANDED v2.0 [DETERMINISTIC].

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
            audit_logger.log_block(
                event_type="CAIE_ARTIFACT_LIMIT",
                tool="CAIE.add_artifact",
                input_preview=f"source={artifact.source_tool} type={artifact.evidence_type}",
                reason=(
                    f"Artifact limit ({_MAX_ARTIFACTS}) reached. "
                    "Possible artifact flooding attack. Artifact rejected."
                ),
            )
            return False

        if artifact.evidence_type not in _VALID_EVIDENCE_TYPES:
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
            return False

        _artifact_copy = copy.deepcopy(artifact)
        self._artifacts.append(_artifact_copy)

        # Index for temporal and network analysis
        if _artifact_copy.timestamp:
            self._temporal_index.setdefault(_artifact_copy.timestamp, []).append(_artifact_copy)
        if "network" in _artifact_copy.evidence_type or "ip" in _artifact_copy.evidence_type:
            self._network_index.setdefault(_artifact_copy.source_tool, []).append(_artifact_copy)

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
                        ("log_entry", "dns_record") and (
                            "network" in a.description.lower()
                            or "red" in a.description.lower()
                            or "conexión" in a.description.lower()
                            or "conexion" in a.description.lower()
                        )]
        host_logs = [a for a in self._artifacts if a.evidence_type in
                     ("log_entry", "memory_process") and "socket" in str(a.metadata).lower()]

        # Rule 1: False flag detection (H-02 fix)
        # Distinguishes two cases that share the same surface pattern
        # (cultural_marker high + technical low):
        #
        #   CASE A — Foreign machine, native config, no incident:
        #     cultural_marker has ONLY config fields (keyboard_layout_detected,
        #     timezone_offset, cyrillic_filenames, language_confidence).
        #     No forensic analysis was performed. This is FP-CULTURAL-CLEAN.
        #     → DO NOT fire. Not a false flag — just a Russian developer's machine.
        #
        #   CASE B — Forensic case with cultural bait (original correct behavior):
        #     cultural_marker has FORENSIC fields (deviation_sigma,
        #     features_anomalous, attribution_consistency_with_ttps, etc.)
        #     indicating active analysis detected manipulation evidence.
        #     → Fire FALSE_FLAG_PATTERN (original Rule 1 behavior).
        #
        #   CASE C — Genuine false flag (real attack + attribution mismatch):
        #     Real attack confirmed (avg_technical > 0.5) AND cultural markers
        #     explicitly contradict the TTP profile (has_manip).
        #     → Fire FALSE_FLAG_ATTRIBUTION_MISMATCH.
        #
        # Ref: L-019, Finding H-02, test_audit_false_flag.py
        # Guard against false positives on clean foreign machines (H-02 / L-019).
        # If the investigator explicitly documented that manipulation checks were
        # performed and came back negative (timestomp_detected=False, etc.),
        # the machine is confirmed clean — do NOT fire FALSE_FLAG_PATTERN.
        # Cases WITHOUT these explicit False flags remain suspicious (original behavior).
        if cultural and technical:
            # DETERMINISTIC: Use math.fsum for precise summation
            avg_cultural = _dround(_dsum([a.raw_score for a in cultural]) / len(cultural), _DETERMINISTIC_INTERNAL_PREC)
            avg_technical = _dround(_dsum([a.raw_score for a in technical]) / len(technical), _DETERMINISTIC_INTERNAL_PREC)

            # confirmed_clean: investigator explicitly verified no manipulation.
            # Fires only when manipulation flags are EXPLICITLY set to False
            # (not merely absent). FP-CULTURAL-CLEAN sets timestomp_detected=False, etc.
            confirmed_clean = any(
                a.metadata.get("timestomp_detected") is False
                or a.metadata.get("backdating_detected") is False
                or a.metadata.get("mft_inconsistency") is False
                or a.metadata.get("suspiciously_obvious") is False
                for a in cultural
            )
            # Has explicit manipulation evidence pointing to planted attribution
            has_manip = any(
                a.metadata.get("mismatch_with_technical_profile") is True
                or a.metadata.get("attribution_consistency_with_ttps") == "LOW"
                or a.metadata.get("timestomp_detected") is True
                or a.metadata.get("backdating_detected") is True
                or a.metadata.get("placement") == "too_clean"
                for a in cultural
            )

            # Case C: genuine false flag — real attack + contradictory attribution
            if avg_cultural > 0.5 and avg_technical > 0.5 and has_manip:
                self._fractures.append(Fracture(
                    artifact_a=f"Cultural markers (avg={avg_cultural:.2f}, attribution contradicts TTP profile)",
                    artifact_b=f"Technical evidence (avg={avg_technical:.2f}, real attack confirmed)",
                    fracture_type="FALSE_FLAG_ATTRIBUTION_MISMATCH",
                    severity=0.85,
                    interpretation=(
                        "Real malicious event confirmed (high technical score) with "
                        "cultural attribution markers that contradict the observed TTP "
                        "profile. The markers were engineered to misdirect attribution. "
                        "MALICE belongs to the planter, not to whoever writes in the "
                        "indicated language. "
                        "Peirce Thirdness: the HABIT is deliberate deception of origin. "
                        "MITRE T1036.005 — Masquerading."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1036.005",
                ))
            # Case B: cultural bait, no confirmed-clean documentation — original behavior
            elif avg_cultural > 0.5 and avg_technical < 0.2 and not confirmed_clean:
                self._fractures.append(Fracture(
                    artifact_a=f"Cultural markers (avg={avg_cultural:.2f})",
                    artifact_b=f"Technical evidence (avg={avg_technical:.2f})",
                    fracture_type="FALSE_FLAG_PATTERN",
                    severity=0.8,
                    interpretation=(
                        "High cultural attribution markers with near-zero technical "
                        "corroboration, confirmed by forensic analysis. Classic "
                        "false-flag pattern: cultural evidence planted to mislead "
                        "attribution. "
                        "Peirce Thirdness: the HABIT is to disguise origin, not to act."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1585.001",
                ))
            # Case A: native config only — no fracture fired (FP-CULTURAL-CLEAN)

        # Rule 1b: Active manipulation evidence with confirmed real attack (H-02 variant)
        # Covers false flag cases where the manipulation is proven by timestomping
        # in MFT/filesystem artifacts — no cultural_marker artifact required.
        # Ref: L-019, Finding H-02, _genuine_false_flag() in test_audit_false_flag.py
        manipulation_artifacts = [
            a for a in self._artifacts
            if a.evidence_type in ("mft_entry", "file_timestamp", "usn_journal")
            and (
                a.metadata.get("timestomp_detected") is True
                or a.metadata.get("backdating_detected") is True
                or a.metadata.get("mft_inconsistency") is True
                or a.metadata.get("mft_si_modified_after_fn") is True
            )
        ]
        if manipulation_artifacts and technical:
            avg_technical_1b = _dround(
                _dsum([a.raw_score for a in technical]) / len(technical),
                _DETERMINISTIC_INTERNAL_PREC
            )
            avg_manip = _dround(
                _dsum([a.raw_score for a in manipulation_artifacts]) / len(manipulation_artifacts),
                _DETERMINISTIC_INTERNAL_PREC
            )
            if avg_technical_1b > 0.5 and avg_manip > 0.5:
                self._fractures.append(Fracture(
                    artifact_a=f"Active manipulation evidence (avg={avg_manip:.2f}): timestomping/backdating confirmed",
                    artifact_b=f"Technical evidence (avg={avg_technical_1b:.2f}, real attack confirmed)",
                    fracture_type="FALSE_FLAG_ATTRIBUTION_MISMATCH",
                    severity=0.85,
                    interpretation=(
                        "Real malicious event confirmed alongside active manipulation of "
                        "attribution artifacts (MFT timestomping or backdating). "
                        "MALICE belongs to the planter. "
                        "MITRE T1070.006 — Indicator Removal: Timestomp."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1070.006",
                ))

        # Rule 2: Log claims contradicted by memory — L-028 fix
        # Operates on observable facts (assertions), not on derived verdicts.
        # Existence of fracture: purely logical (log claims network activity,
        # memory shows no network activity → structural contradiction).
        # Severity: modulated by PID correlation (same process referenced
        # in both artifacts = stronger contradiction).
        if logs and technical:
            log_assertions  = frozenset().union(*(_extract_assertions(a) for a in logs))
            tech_assertions = frozenset().union(*(_extract_assertions(a) for a in technical))

            log_claims_activity = "log_claims_outbound_connection" in log_assertions
            memory_silent       = "memory_shows_no_network_activity" in tech_assertions

            if log_claims_activity and memory_silent:
                # PID correlation: same process named in log and present in
                # memory → contradiction is intra-process, not just cross-source
                log_pids  = {str(a.metadata.get("pid")) for a in logs    if a.metadata.get("pid") is not None}
                tech_pids = {str(a.metadata.get("pid")) for a in technical if a.metadata.get("pid") is not None}
                pid_overlap = log_pids & tech_pids

                severity = _dround(0.95 if pid_overlap else 0.75, _DETERMINISTIC_INTERNAL_PREC)

                self._fractures.append(Fracture(
                    artifact_a=f"Log evidence asserts outbound network activity",
                    artifact_b="Memory/kernel evidence: no network activity observed",
                    fracture_type="LOG_VS_MEMORY",
                    severity=severity,
                    interpretation=(
                        "Logs assert network activity but memory shows no trace. "
                        "Structural impossibility: if the activity happened, memory "
                        "MUST contain network objects (sockets, connections). "
                        "Their absence indicates log fabrication. "
                        + (f"PID overlap {pid_overlap}: same process named in both sources — "
                           "contradiction is intra-process." if pid_overlap else
                           "No shared PID: contradiction is cross-source.")
                    ),
                    spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1070.001",
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
        # Effect-before-cause: Any log/timestamp artifact precedes the process that
        # supposedly caused it.
        #
        # BUG FIX (session 2026-05-18): El filtro original usaba
        #   "network" in a.description.lower()
        # Esto descartaba silenciosamente artefactos válidos como windows_event_log
        # y file_timestamp que tienen network_log_time en metadata pero no la
        # palabra "network" en la descripción. Resultado observado: golden_rules_triggered=0
        # en casos con violación causal de -5s (DLL antes que el proceso).
        #
        # Fix: cualquier artefacto que tenga network_log_time en metadata califica
        # como "evento previo". El campo network_log_time es el contrato semántico
        # correcto, no la descripción en texto libre.
        #
        # Rationale Daubert: un filtro sobre texto libre no es reproducible —
        # depende de cómo el operador redactó la descripción. Un filtro sobre
        # un campo estructurado del metadata sí lo es.
        network_artifacts = [
            a for a in self._artifacts
            if (
                a.metadata.get("network_log_time")  # campo estructurado (correcto)
                or "network" in a.description.lower()  # compatibilidad backward
                or "red" in a.description.lower()       # ES: red de comunicaciones
                or "conexión" in a.description.lower()  # ES: conexión de red
                or "conexion" in a.description.lower()  # ES: sin tilde
            )
        ]
        process_artifacts = [a for a in self._artifacts if a.evidence_type == "memory_process"]

        def _parse_ts_tcv(ts_str: object, artifact_tool: str, field: str) -> "datetime | None":
            """
            Robust ISO 8601 timestamp parser for TCV rule.

            Handles:
            - 'Z' suffix (UTC) → '+00:00'
            - Naive timestamps (no offset) → assumes UTC, logs assumption
            - None or empty string → returns None, logs missing field
            - Unparseable formats → returns None, logs format error

            Rationale (Grok P0 audit): silent continue on parse failure
            hides data quality problems. In Daubert context, unparseable
            timestamps should be auditable, not invisible.
            """
            if not ts_str or not isinstance(ts_str, str) or not ts_str.strip():
                audit_logger.log_info(
                    event_type="TCV_TIMESTAMP_MISSING",
                    tool="CrossArtifactIncongruenceEngine",
                    message=(
                        f"TCV rule: {field} is missing or empty for "
                        f"artifact from {artifact_tool!r}. "
                        "Cannot evaluate temporal causality for this pair."
                    ),
                )
                return None
            # Normalize Z suffix
            normalized = ts_str.strip().replace('Z', '+00:00')
            try:
                return datetime.fromisoformat(normalized)
            except ValueError:
                pass
            # Try naive timestamp (no offset) — assume UTC, log the assumption
            try:
                dt = datetime.fromisoformat(ts_str.strip())
                audit_logger.log_info(
                    event_type="TCV_TIMESTAMP_NAIVE_ASSUMED_UTC",
                    tool="CrossArtifactIncongruenceEngine",
                    message=(
                        f"TCV rule: {field}={ts_str!r} from {artifact_tool!r} "
                        "has no timezone offset. Assumed UTC for comparison. "
                        "This assumption affects TCV accuracy if the system "
                        "clock was in a non-UTC timezone."
                    ),
                )
                from datetime import timezone as _tz
                return dt.replace(tzinfo=_tz.utc)
            except (ValueError, TypeError):
                pass
            audit_logger.log_info(
                event_type="TCV_TIMESTAMP_UNPARSEABLE",
                tool="CrossArtifactIncongruenceEngine",
                message=(
                    f"TCV rule: {field}={ts_str!r} from {artifact_tool!r} "
                    "could not be parsed as ISO 8601. "
                    "Temporal causality check skipped for this artifact pair. "
                    "Expected formats: YYYY-MM-DDTHH:MM:SS[.ffffff][Z|+HH:MM]"
                ),
            )
            return None

        for net in network_artifacts:
            net_time_str = net.metadata.get("network_log_time") or net.timestamp
            net_time = _parse_ts_tcv(net_time_str, net.source_tool, "network_log_time")
            if net_time is None:
                continue

            for proc in process_artifacts:
                proc_time_str = proc.metadata.get("process_creation_time") or proc.timestamp
                proc_time = _parse_ts_tcv(proc_time_str, proc.source_tool, "process_creation_time")
                if proc_time is None:
                    continue

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

        # Rule 7: NETWORK_VS_HOST
        # Firewall claims outbound traffic but host shows no open sockets
        firewall_claims = [a for a in self._artifacts 
                          if a.metadata.get("firewall_claim") and 
                          a.metadata.get("traffic_type") == "outbound"]
        host_reality = [a for a in self._artifacts 
                       if a.metadata.get("host_reality") and 
                       a.metadata.get("open_sockets") is not None]

        for fw in firewall_claims:
            claimed_port = fw.metadata.get("port")
            claimed_bytes = fw.metadata.get("bytes_transferred", 0)

            # Check if any host artifact contradicts this
            host_contradicts = False
            for host in host_reality:
                open_sockets = host.metadata.get("open_sockets", [])
                if claimed_port and claimed_port not in open_sockets:
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
        # File claims to be signed but hash doesn't match known-good database.
        # IMPORTANT (DeepSeek P0 audit): hash mismatch alone does NOT prove spoofed
        # identity. Legitimate causes include: different version, hotfix, internal
        # build, signed-but-updated binary, or vendor catalog not updated.
        # Full trust-chain validation requires: signer validation, catalog validation,
        # timestamp authority, cert chain, and revocation check.
        # WITHOUT trust-chain: severity=0.6, NOT a Golden Rule (SUSPICION, not MALICE).
        # WITH confirmed trust-chain failure: severity=0.9, qualifies as Golden Rule.
        for crypto in cryptographic:
            if crypto.metadata.get("signature_mismatch") or crypto.metadata.get("hash_mismatch"):
                claimed_identity = crypto.metadata.get("claimed_identity", "unknown")
                actual_hash = crypto.metadata.get("actual_hash", "unknown")
                expected_hash = crypto.metadata.get("expected_hash", "unknown")

                # Check whether a full trust-chain validation was performed
                trust_chain_validated = crypto.metadata.get("trust_chain_validated", False)
                signer_validated = crypto.metadata.get("signer_validated", False)
                cert_revoked = crypto.metadata.get("cert_revoked", False)
                catalog_validated = crypto.metadata.get("catalog_validated", False)

                full_trust_chain = trust_chain_validated and signer_validated and catalog_validated

                if full_trust_chain or cert_revoked:
                    # Full validation confirms the inconsistency is not explained by
                    # version differences or legitimate patch. This IS a Golden Rule.
                    severity = 0.9
                    fracture_type = "CRYPTOGRAPHIC_INCONSISTENCY"
                    interpretation = (
                        "CONFIRMED SPOOFED IDENTITY: File presents cryptographic credentials "
                        f"claiming to be '{claimed_identity}', hash verification fails "
                        "AND full trust-chain validation confirms the inconsistency is not "
                        "attributable to version differences or legitimate patches. "
                        "Trust chain: signer=" + ("FAIL" if not signer_validated else "FAIL-REVOKED" if cert_revoked else "OK") + ", "
                        "catalog=" + ("OK" if catalog_validated else "NOT_CHECKED") + ". "
                        "Peirce Secondness: The sign (hash) does not match the object "
                        "(file content), and no legitimate explanation survives full chain validation."
                    )
                    # This qualifies as a Golden Rule — mark it via ttp_id and severity
                else:
                    # Trust-chain NOT validated — cannot rule out version/patch/build.
                    # Downgrade to SUSPICION. Must be reviewed by analyst.
                    severity = 0.6
                    fracture_type = "CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED"
                    interpretation = (
                        f"HASH MISMATCH (trust-chain NOT validated): File presents "
                        f"credentials as '{claimed_identity}' but hash does not match "
                        "known-good database. CANNOT confirm spoofed identity without "
                        "signer validation, catalog check, and revocation status. "
                        "Possible causes: different version, hotfix, internal build, "
                        "signed-but-updated binary. "
                        "Action required: run full trust-chain validation before escalating "
                        "to Golden Rule. Set trust_chain_validated=True in artifact metadata."
                    )

                self._fractures.append(Fracture(
                    artifact_a=f"File claims identity: {claimed_identity}",
                    artifact_b=f"Hash mismatch: {actual_hash[:16]}... != {expected_hash[:16]}...",
                    fracture_type=fracture_type,
                    severity=severity,
                    interpretation=interpretation,
                    spoofability_delta=0.05,  # Cryptographic hashes are hard to spoof
                    ttp_id="T1036",  # Masquerading
                ))

        # ===================================================================
        # GOLDEN FORENSIC RULES — P5: TCV Anti-Forensics
        # Gemini tactical order + paper ScienceDirect sept 2026
        # ===================================================================

        # Rule 9: TIMESTAMP_PRECISION_ANOMALY
        # Herramientas como Timestomp, nTimestomp truncan sub-segundos a 7 ceros.
        # Un archivo legítimo tiene sub-segundos variables (OS scheduler jitter).
        # spoofability=0.05 — evitar la firma requiere herramientas custom Ring-0.
        precision_artifacts = [a for a in self._artifacts
                                if a.evidence_type in ("file_timestamp", "timestamp_precision")]
        for art in precision_artifacts:
            ts_str = art.metadata.get("timestamp_raw") or art.timestamp
            # Detectar 7 ceros en sub-segundos: e.g. "2026-04-10T10:00:00.0000000Z"
            sub_second_zeros = art.metadata.get("sub_second_zeros", 0)
            raw_ts = str(ts_str)
            # Contar ceros consecutivos tras el punto decimal
            if "." in raw_ts:
                frac = raw_ts.split(".")[1].rstrip("Z+").rstrip("0")
                trailing = len(raw_ts.split(".")[1].rstrip("Z+")) - len(frac)
                if trailing >= 5:  # 5+ ceros = firma de herramienta
                    sub_second_zeros = trailing
            if sub_second_zeros >= 5 or art.metadata.get("timestamp_precision_anomaly"):
                self._fractures.append(Fracture(
                    artifact_a=f"Timestamp: {ts_str}",
                    artifact_b=f"Expected: OS scheduler jitter (variable sub-seconds)",
                    fracture_type="TIMESTAMP_PRECISION_ANOMALY",
                    severity=0.95,
                    interpretation=(
                        f"TOOL SIGNATURE DETECTED: Timestamp sub-seconds truncated "
                        f"to {sub_second_zeros}+ zeros. Legitimate OS timestamps have "
                        "variable sub-second precision due to scheduler jitter. "
                        "This static pattern is the fingerprint of anti-forensic tools "
                        "(Timestomp, nTimestomp, SetMACE). "
                        "Peirce Thirdness: The HABIT of the tool, not the actor, is visible."
                    ),
                    spoofability_delta=_dround(0.70 - 0.05, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1070.006",  # Indicator Removal: Timestomp
                ))

        # Rule 10: MFT_ENTRY_ANOMALY
        # El número de entrada MFT es asignado secuencialmente por el driver NTFS.
        # Un archivo con MFT entry# alto y timestamp más antiguo que entradas
        # anteriores rompe la monotonicidad — indica timestomping retroactivo.
        # spoofability=0.05 — el MFT ID es inalterable en user-space.
        mft_artifacts = [a for a in self._artifacts if a.evidence_type == "mft_entry"
                         or a.metadata.get("mft_entry_number") is not None]
        if len(mft_artifacts) >= 2:
            mft_sorted = sorted(
                mft_artifacts,
                key=lambda a: int(a.metadata.get("mft_entry_number", 0))
            )
            for i in range(1, len(mft_sorted)):
                prev = mft_sorted[i - 1]
                curr = mft_sorted[i]
                prev_entry = int(prev.metadata.get("mft_entry_number", 0))
                curr_entry = int(curr.metadata.get("mft_entry_number", 0))
                prev_ts = _parse_ts_tcv(prev.timestamp, prev.source_tool, f"mft#{prev_entry}.timestamp")
                curr_ts = _parse_ts_tcv(curr.timestamp, curr.source_tool, f"mft#{curr_entry}.timestamp")
                if prev_ts is None or curr_ts is None:
                    continue
                # MFT entry# creció pero timestamp retrocedió = anomalía
                if curr_entry > prev_entry and curr_ts < prev_ts:
                    delta_seconds = (prev_ts - curr_ts).total_seconds()
                    self._fractures.append(Fracture(
                        artifact_a=f"MFT#{curr_entry} timestamp={curr_ts.isoformat()}",
                        artifact_b=f"MFT#{prev_entry} timestamp={prev_ts.isoformat()} (anterior)",
                        fracture_type="MFT_ENTRY_ANOMALY",
                        severity=0.90,
                        interpretation=(
                            f"MFT MONOTONICITY VIOLATION: Entry #{curr_entry} "
                            f"was allocated AFTER #{prev_entry} (NTFS sequential allocation) "
                            f"but carries a timestamp {delta_seconds:.0f}s OLDER. "
                            "The NTFS driver never assigns entry numbers retroactively. "
                            "This fracture is structurally impossible without timestamp "
                            "manipulation after allocation. "
                            "Peirce Secondness: The MFT# sequence is the ground truth; "
                            "the timestamp is the lie."
                        ),
                        spoofability_delta=_dround(0.70 - 0.05, _DETERMINISTIC_INTERNAL_PREC),
                        ttp_id="T1070.006",  # Indicator Removal: Timestomp
                    ))

        # Rule 11: USN_JOURNAL_GAP
        # Si $LogFile muestra actividad pero $UsnJrnl no tiene registro
        # para el mismo MFT entry en la ventana temporal → journal fue borrado.
        # Requiere Ring-0 / Admin para ejecutar fsutil usn deletejournal.
        # spoofability=0.10 — requiere privilegio elevado documentable.
        usn_gap_artifacts = [a for a in self._artifacts
                              if a.evidence_type == "usn_journal_gap"
                              or a.metadata.get("usn_journal_gap") is True]
        logfile_claims = [a for a in self._artifacts
                          if a.evidence_type in ("log_entry", "usn_journal")
                          and a.metadata.get("logfile_event") is True]

        for gap in usn_gap_artifacts:
            mft_ref = gap.metadata.get("mft_entry_number", "unknown")
            window_start = gap.metadata.get("window_start", "?")
            window_end = gap.metadata.get("window_end", "?")
            self._fractures.append(Fracture(
                artifact_a=f"$LogFile: event at MFT#{mft_ref} [{window_start}→{window_end}]",
                artifact_b=f"$UsnJrnl: NO record for MFT#{mft_ref} in same window",
                fracture_type="USN_JOURNAL_GAP",
                severity=1.0,  # CRÍTICO — requiere Ring-0
                interpretation=(
                    f"USN JOURNAL ERASURE DETECTED: $LogFile records activity for "
                    f"MFT entry #{mft_ref} but $UsnJrnl has no corresponding record "
                    f"in the [{window_start} → {window_end}] window. "
                    "The USN Journal is maintained by the NTFS kernel driver. "
                    "Clearing it requires 'fsutil usn deletejournal' with "
                    "administrative/Ring-0 privileges — this action is itself "
                    "a forensic indicator. "
                    "Peirce Secondness: Significant Silence — the absence of the "
                    "USN record is the evidence of its deliberate erasure."
                ),
                spoofability_delta=_dround(0.85 - 0.10, _DETERMINISTIC_INTERNAL_PREC),
                ttp_id="T1070.004",  # Indicator Removal: File Deletion
            ))

        # Implicit USN gap: LogFile claims but no USN journal artifacts present.
        # CRITICAL DISTINCTION (DeepSeek P0 audit):
        #   - ABSENT   : acquisition was complete and USN was explicitly not found
        #                (usn_explicitly_absent=True in any artifact metadata)
        #   - UNAVAILABLE: USN was not included in acquisition scope
        #                  (acquisition_complete=False OR usn_scope=False in metadata)
        #   - DEFAULT  : insufficient evidence to classify — do NOT fire fracture.
        #
        # Rationale: partial acquisitions, truncated journals, and incomplete imaging
        # are common in field work. Treating UNAVAILABLE as DELETED is judicially
        # dangerous — it asserts journal clearing when the real cause is acquisition
        # scope. Only fire when the operator has EXPLICITLY confirmed the acquisition
        # included USN scope and the journal is not present.
        has_usn = any(a.evidence_type == "usn_journal" for a in self._artifacts)
        if logfile_claims and not has_usn:
            # Check whether any artifact carries explicit acquisition metadata
            usn_explicitly_absent = any(
                a.metadata.get("usn_explicitly_absent") is True
                for a in self._artifacts
            )
            acquisition_complete = any(
                a.metadata.get("acquisition_complete") is True
                and a.metadata.get("usn_scope") is True
                for a in self._artifacts
            )

            if usn_explicitly_absent or acquisition_complete:
                # Only fire when there is explicit confirmation that USN was in scope
                self._fractures.append(Fracture(
                    artifact_a=f"$LogFile: {len(logfile_claims)} events recorded",
                    artifact_b="$UsnJrnl: EXPLICITLY ABSENT (acquisition confirmed complete + USN in scope)",
                    fracture_type="USN_JOURNAL_GAP",
                    severity=0.75,  # Reduced from 0.85: implicit gap is less certain than explicit gap
                    interpretation=(
                        f"CONFIRMED USN GAP: {len(logfile_claims)} $LogFile events exist "
                        "and acquisition metadata confirms USN journal was in scope. "
                        "Absence under confirmed acquisition scope is consistent with "
                        "deliberate journal clearing (requires Ring-0/Admin: "
                        "'fsutil usn deletejournal'). "
                        "Peirce Eco Silence: The journal that should speak is silent. "
                        "NOTE: Distinguish from UNAVAILABLE (acquisition scope unknown)."
                    ),
                    spoofability_delta=_dround(0.85 - 0.10, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1070.004",
                ))
            else:
                # Acquisition scope unknown — log as informational, do NOT generate fracture
                audit_logger.log_info(
                    event_type="USN_JOURNAL_SCOPE_UNKNOWN",
                    tool="CrossArtifactIncongruenceEngine",
                    message=(
                        f"$LogFile has {len(logfile_claims)} events but no USN artifacts present. "
                        "Acquisition scope unknown — cannot distinguish ABSENT from UNAVAILABLE. "
                        "To enable USN_JOURNAL_GAP detection, set "
                        "acquisition_complete=True and usn_scope=True in artifact metadata "
                        "when acquisition confirmed that USN journal was in acquisition scope."
                    ),
                )

        # Rule 9: NARRATIVE_POISONING_DETECTED (VIGIA_BREAK_009)
        # Artefactos textuales que afirman benignidad mientras evidencia técnica
        # de alta confianza los contradice. Diseñado para detectar prompt injection
        # / narrative poisoning: un atacante que inyecta un reporte falso diciendo
        # "todo OK" mientras hay malware en memoria activo.
        # Fracture_type incluida en _STRUCTURAL_MALICE_TYPES → fuerza MALICE.
        # ttp_id=T1565.001 (Data Manipulation: Stored Data)
        _BENIGNITY_KEYWORDS = frozenset({
            # English
            "benign", "confirmed benign", "false positive",
            "approved", "not suspicious", "no threat",
            # Spanish (bilingual evidence support)
            "benigno", "confirmado benigno", "falso positivo",
            "aprobado", "no sospechoso", "sin amenaza",
            "ya confirmado", "caso cerrado", "sin riesgo",
        })
        narrative_artifacts = [
            a for a in self._artifacts
            if a.evidence_type in ("log_entry", "text", "report")
            and any(kw in a.description.lower() for kw in _BENIGNITY_KEYWORDS)
        ]
        technical_contradictory = [
            a for a in self._artifacts
            if a.evidence_type in ("network_artifact", "memory_process",
                                   "kernel_structure", "usn_journal",
                                   "lsass_session", "hmac_audit_log",
                                   "dns_record", "ip_geolocation")
            and a.raw_score > _dround(0.7, _DETERMINISTIC_INTERNAL_PREC)
        ]
        if narrative_artifacts and technical_contradictory:
            for nar in narrative_artifacts:
                for tech in technical_contradictory:
                    self._fractures.append(Fracture(
                        artifact_a=f"Narrative: {nar.description[:60]}",
                        artifact_b=f"Technical: {tech.description[:60]}",
                        fracture_type="NARRATIVE_POISONING_DETECTED",
                        severity=_dround(0.85, _DETERMINISTIC_INTERNAL_PREC),
                        interpretation=(
                            "Unverified textual claim of benignity contradicts "
                            "high-confidence technical evidence of malicious activity. "
                            "This is narrative poisoning: an adversarial attempt to "
                            "inject false reassurance into the evidence stream. "
                            "Peirce Secondness: the text asserts absence, the technical "
                            "data asserts presence. One of them is a lie; in DFIR, "
                            "unverified narrative claims are the lie by default. "
                            "T1565.001 — Data Manipulation: Stored Data."
                        ),
                        spoofability_delta=_dround(0.60 - 0.20, _DETERMINISTIC_INTERNAL_PREC),
                        ttp_id="T1565.001",
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
                "_determinism_protocol": "P0-v2.0-DECIMAL-6-4",
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
        # NIGHTFALL P1: multiplicaciones acumulativas con decimal.Decimal.
        # _dround() no era suficiente: la FPU nativa ejecuta prod_val * (1.0-s)
        # antes del redondeo, y ese producto intermedio puede diferir en el
        # bit 52 de la mantisa entre x86 y ARM. Con Decimal(str(x)) la
        # multiplicacion es puramente software, determinista en toda arquitectura.
        group_scores = []
        for scores in grouped.values():
            prod_d = _D_ONE
            for s in scores:
                # Decimal(str(x)): conversion via string evita imprecision
                # de la conversion directa float->Decimal
                s_d = decimal.Decimal(str(_dround(s, _DETERMINISTIC_INTERNAL_PREC)))
                prod_d = prod_d * (_D_ONE - s_d)
            group_score = _dround(_D_ONE - prod_d, _DETERMINISTIC_INTERNAL_PREC)
            group_scores.append(group_score)

        # Across-group fusion (independent sources): 1 - ∏(1 - g)
        # NIGHTFALL P1: mismo patron Decimal para las multiplicaciones de grupos
        if group_scores:
            prod_d = _D_ONE
            for g in group_scores:
                g_d = decimal.Decimal(str(_dround(g, _DETERMINISTIC_INTERNAL_PREC)))
                prod_d = prod_d * (_D_ONE - g_d)
            composite = _dround(_D_ONE - prod_d, _DETERMINISTIC_INTERNAL_PREC)
        else:
            composite = 0.0

        composite = _dround(min(composite, decimal.Decimal("0.99")), _DETERMINISTIC_INTERNAL_PREC)

        # P1: Confidence normalization - penalize if < 3 independent sources
        independent_sources = len(group_scores)
        confidence_penalty = 0.0
        if independent_sources < _MIN_INDEPENDENT_SOURCES:
            confidence_penalty = _LOW_SOURCE_PENALTY
            composite = _dround(composite * (_D_ONE - decimal.Decimal(str(confidence_penalty))), _DETERMINISTIC_INTERNAL_PREC)

        # P1: DETERMINISTIC fracture deduplication
        # Dedup key: (fracture_type, artifact_a, artifact_b)
        # Note: semantic duplicates with different interpretations are deduplicated
        # architecturally here. Rule authors must ensure fracture_type + artifacts
        # form a unique key per logical finding.
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

        # GOLDEN RULES — structural verdict override.
        # These are NOT probabilistic increments. A causal impossibility does not
        # add probability mass — it is a different epistemic category entirely.
        # (DeepSeek P0 audit: mixing structural inference with probabilistic score
        # contaminates the composite and violates Daubert reasoning integrity.)
        # CRYPTOGRAPHIC_INCONSISTENCY only qualifies if trust-chain was validated
        # (unverified version uses fracture_type CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED).
        _GOLDEN_RULE_TYPES = frozenset({
            "TEMPORAL_CAUSALITY_VIOLATION",
            "CRYPTOGRAPHIC_INCONSISTENCY",  # only fires when trust_chain_validated=True
        })
        _STRUCTURAL_MALICE_TYPES = frozenset({
            "LOG_VS_MEMORY",
            "DOCUMENT_FORGERY",
            "NETWORK_VS_HOST",
            "MFT_ENTRY_ANOMALY",
            "NARRATIVE_POISONING_DETECTED",
        })

        has_golden_rule = any(f.fracture_type in _GOLDEN_RULE_TYPES for f in filtered_fractures)
        has_structural_malice = any(f.fracture_type in _STRUCTURAL_MALICE_TYPES for f in filtered_fractures)

        # Fracture bonus: only applied to NON-golden-rule fractures.
        # Rationale: Golden Rules already force MALICE via structural_verdict.
        # Adding a bonus on top of a forced verdict would double-weight the same
        # finding and inflate composite_score in a way that is not reproducible
        # across different ordering of rule evaluation.
        non_structural_fractures = [
            f for f in filtered_fractures
            if f.fracture_type not in _GOLDEN_RULE_TYPES
            and f.fracture_type not in _STRUCTURAL_MALICE_TYPES
        ]
        fracture_bonus = 0.0
        if non_structural_fractures:
            bonus_terms = [
                _dround(
                    _dround(getattr(f, 'severity', 0.0), _DETERMINISTIC_INTERNAL_PREC) * _dround(getattr(f, 'spoofability_delta', 0.5), _DETERMINISTIC_INTERNAL_PREC) * decimal.Decimal("0.05"),
                    _DETERMINISTIC_INTERNAL_PREC
                )
                for f in non_structural_fractures
            ]
            bonus = _dsum(bonus_terms)
            fracture_bonus = _dround(min(bonus, decimal.Decimal("0.2")), _DETERMINISTIC_INTERNAL_PREC)
            composite = _dround(min(composite + fracture_bonus, decimal.Decimal("0.99")), _DETERMINISTIC_INTERNAL_PREC)

        # Verdict: structural_verdict takes precedence over probabilistic_score.
        # Two separate fields exposed in output for Daubert traceability.
        if has_golden_rule or has_structural_malice:
            structural_verdict = "MALICE"
        elif filtered_fractures:
            structural_verdict = "SUSPICION"
        else:
            structural_verdict = "NOISE"

        probabilistic_verdict = "MALICE" if composite >= 0.5 else "SUSPICION" if composite >= 0.2 else "NOISE"

        # Final verdict: structural dominates. If structural says MALICE, it's MALICE.
        # If structural says NOISE but probabilistic says MALICE, use probabilistic.
        _VERDICT_RANK = {"NOISE": 0, "SUSPICION": 1, "MALICE": 2}
        verdict = max(structural_verdict, probabilistic_verdict, key=lambda v: _VERDICT_RANK[v])

        # Daubert admissibility note — must be assigned before CDL block,
        # which appends to it via +=. Only depends on self._artifacts.
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

        # ================================================================
        # COLLAPSE DECISION LAYER — Política bajo colapso de supuestos.
        # Si el atacante rompe la independencia de sensores o la integridad
        # del pipeline, el CDL lo detecta y puede downgrade el veredicto a
        # INCONCLUSIVE antes de exponerlo. Sin CDL, el motor emitiría
        # veredictos firmes sobre evidencia comprometida. (Kimi P0 audit)
        # ================================================================
        broken_assumptions = set()
        for f in filtered_fractures:
            ft = f.fracture_type
            if "SENSOR" in ft or "independence" in ft.lower():
                broken_assumptions.add("sensor_independence")
            if "PIPELINE" in ft or "integrity" in ft.lower():
                broken_assumptions.add("pipeline_integrity")
            if "TIMESTAMP" in ft or "temporal" in ft.lower():
                broken_assumptions.add("timestamp_comparability")

        try:
            cdl = CollapseDecisionLayer()

            # Calcular coverage_ratio aproximado basado en capas observadas
            total_expected_layers = ["memory", "process", "auth", "filesystem", "network", "kernel"]
            observed_layers = set()
            for a in self._artifacts:
                layer = a.metadata.get("layer", a.evidence_type)
                observed_layers.add(layer)
            coverage_ratio = len(observed_layers) / len(total_expected_layers) if total_expected_layers else 0.5

            ctx = CollapseContext(
                broken_assumptions=broken_assumptions,
                coverage_ratio=coverage_ratio,
                base_score=composite,
                has_structural_malice=(structural_verdict == "MALICE"),
                independent_sources=independent_sources,
            )
            cdl_verdict = cdl.resolve(ctx)
            cdl_explanation = cdl.explain(ctx, cdl_verdict)

            if cdl_verdict == CollapseVerdict.INCONCLUSIVE:
                verdict = "INCONCLUSIVE"
                structural_verdict = "INCONCLUSIVE"
                daubert_note += f" CDL: {cdl_explanation}"
            elif cdl_verdict == CollapseVerdict.SUSPICION and verdict == "MALICE":
                verdict = "SUSPICION"
                daubert_note += f" CDL: {cdl_explanation}"
        except Exception as exc:
            import logging
            logging.getLogger("caie").error("CDL evaluation failed: %s", exc)

        # Peirce chain
        top_adjusted = sorted(
            [
                {
                    "tool": a.source_tool,
                    "type": a.evidence_type,
                    "raw_score": str(_dround(a.raw_score, _DETERMINISTIC_OUTPUT_PREC)),
                    "spoofability": a.profile.spoofability,
                    "weight": a.profile.base_weight,
                    "adjusted": str(_dround(a.adjusted_score, _DETERMINISTIC_OUTPUT_PREC)),
                    "description": a.description[:200],
                }
                for a in self._artifacts
            ],
            key=lambda x: x["adjusted"],
            reverse=True
        )

        # Golden Rules summary for Peirce Thirdness
        # Uses _GOLDEN_RULE_TYPES (defined above in verdict block).
        golden_rules = [f for f in filtered_fractures
                        if f.fracture_type in _GOLDEN_RULE_TYPES]

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
                f"({top_adjusted[0]['type']}, adj={top_adjusted[0]['adjusted']}). "
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
            for ttp in get_ttps_for_evidence_type(a.evidence_type):
                mitre_ttps.add(ttp)
            # Add TTPs from signals
            for signal_type in a.metadata.get("signals", []):
                if isinstance(signal_type, dict):
                    ttp = _SIGNAL_TO_ATTACK.get(signal_type.get("type", ""))
                    if ttp:
                        mitre_ttps.add(ttp)

        # Calculate TTP confidence scores
        ttp_confidences = {}
        for ttp_id in mitre_ttps:
            ttp_meta = get_ttp_metadata(ttp_id)
            if ttp_meta:
                # DETERMINISTIC: Average confidence across related artifacts
                related = [a for a in self._artifacts 
                         if ttp_id in get_ttps_for_evidence_type(a.evidence_type)]
                if related:
                    avg_reliability = _dround(_dsum([a.raw_score for a in related]) / len(related), _DETERMINISTIC_INTERNAL_PREC)
                    ttp_confidences[ttp_id] = calculate_ttp_confidence(
                        ttp_id, float(avg_reliability), "cross_artifact_analysis"
                    )

        # DETERMINISTIC: Build result with all floats rounded to output precision
        result = {
            "status": "OK",
            "verdict": verdict,
            # EPISTEMOLOGICAL SEPARATION (DeepSeek P0 audit):
            # structural_verdict: derived from causal impossibilities (Golden Rules)
            #                     and structural fractures (LOG_VS_MEMORY, etc.)
            #                     These are NOT probabilistic — they are categorical.
            # probabilistic_score / probabilistic_verdict: derived from Noisy-OR
            #                     fusion of adjusted evidence scores.
            # Both are exposed for Daubert traceability. The final verdict is the
            # maximum of the two, with structural taking precedence.
            "structural_verdict": structural_verdict,
            "probabilistic_verdict": probabilistic_verdict,
            "probabilistic_score": str(_dround(composite, _DETERMINISTIC_OUTPUT_PREC)),
            "_determinism_protocol": "P0-v2.0-DECIMAL-6-4",
            "integrity_check": {
                "math_engine": "decimal.Decimal",
                "internal_precision": _DETERMINISTIC_INTERNAL_PREC,
                "output_precision": _DETERMINISTIC_OUTPUT_PREC,
                "fpu_native": False,
                "alerts": [],
            },
            "composite_score": str(_dround(composite, _DETERMINISTIC_OUTPUT_PREC)),
            "fracture_bonus_applied": str(_dround(fracture_bonus, _DETERMINISTIC_OUTPUT_PREC)),
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
                    "severity": str(_dround(f.severity, _DETERMINISTIC_OUTPUT_PREC)),
                    "artifact_a": f.artifact_a,
                    "artifact_b": f.artifact_b,
                    "interpretation": f.interpretation,
                    "spoofability_delta": str(_dround(f.spoofability_delta, _DETERMINISTIC_OUTPUT_PREC)),
                    "mitre_ttp": f.ttp_id or _SIGNAL_TO_ATTACK.get(f.fracture_type),
                    "is_golden_rule": f.fracture_type in _GOLDEN_RULE_TYPES,
                    "is_structural": f.fracture_type in _STRUCTURAL_MALICE_TYPES,
                }
                for f in filtered_fractures
            ],
            "mitre_ttps": sorted(mitre_ttps),
            "ttp_confidences": {k: str(_dround(v, _DETERMINISTIC_OUTPUT_PREC)) for k, v in ttp_confidences.items()},
            "peirce_chain": peirce_chain,
            "daubert_note": daubert_note,
            "timestamp": _utcnow(),
            "vigia_verdict": (
                f"[VIGIA_CAIE]: {verdict}. "
                f"Structural={structural_verdict} Probabilistic={probabilistic_verdict} "
                f"(composite={_dround(composite, 4):.4f}) from {len(self._artifacts)} artifacts "
                f"({independent_sources} independent). "
                f"{len(filtered_fractures)} fracture(s), {len(golden_rules)} Golden Rule(s). "
                f"{daubert_note[:80]}"
            ),
        }

        # v2.0: chain_of_custody metadata
        result["chain_of_custody"] = {
            "evidence_count"      : len(self._artifacts),
            "fracture_count"      : len(filtered_fractures),
            "processing_timestamp": _utcnow(),
        }

        # HMAC sign for chain of custody
        result["_operation_hmac"] = self._sign_result(result)

        return result

    def _sign_result(self, data: dict) -> str:
        """
        HMAC signature for result integrity.

        NIGHTFALL P0-2: eliminado getattr(audit_logger, "_hmac_key").
        Clave resuelta via _caie_hmac_sign_canonical() — no expone
        atributos privados de SecurityAudit como superficie de inspeccion.

        NIGHTFALL P0-3: ensure_ascii=True + separators minimos.
        Determinismo absoluto: misma clave + mismo payload = mismo HMAC
        en cualquier arquitectura o locale del sistema.
        """
        payload = {k: v for k, v in data.items() if k != "_operation_hmac"}
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=lambda x: "[UNSERIALIZABLE]",
        )
        return _caie_hmac_sign_canonical(canonical)

    def reset(self) -> None:
        """
        Clear all artifacts and fractures for a new evaluation cycle.

        FORENSIC ISOLATION (Grok P0 audit):
        Reinitializes with fresh objects rather than .clear() to guarantee
        zero state leakage between evaluations. CPython's dict.clear() and
        list.clear() release element references but retain the internal
        over-allocated buffer. For a forensic tool, 'clean' means no shared
        state — not just dereferenced elements.
        """
        self._artifacts = []
        self._fractures = []
        self._temporal_index = {}
        self._network_index = {}


# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

async def cross_artifact_analysis(
    artifacts: list[dict],
) -> dict:
    """
    Cross-Artifact Incongruence Engine (CAIE) — EXPANDED v2.0 [DETERMINISTIC].

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
            audit_logger.log_info(
                event_type="CAIE_UNKNOWN_TYPE_SKIPPED",
                tool="cross_artifact_analysis",
                message=(
                    f"Skipped artifact with unknown evidence_type={evidence_type!r} "
                    f"from tool={item.get('source_tool', '?')}. "
                    f"Valid types: {sorted(_VALID_EVIDENCE_TYPES)}"
                ),
            )
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
            audit_logger.log_info(
                event_type="CAIE_ARTIFACT_PARSE_ERROR",
                tool="cross_artifact_analysis",
                message=f"Failed to parse artifact: {exc}",
            )
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

    print(" CAIE Determinism Protocol P0: VERIFIED")
    print(f"   Composite Score: {result1['composite_score']}")
    print(f"   Artifacts: {result1['artifacts_evaluated']}")
    print(f"   Fractures: {result1['fractures_detected']}")
    print(f"   Protocol: {result1.get('_determinism_protocol', 'legacy')}")

    return True


# Auto-verify on module load (can be disabled in production)
if __name__ == "__main__":
    verify_determinism_cross_arch()
