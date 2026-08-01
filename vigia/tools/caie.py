# Copyright 2026 Anna Tchijova
# Licensed under the Apache License, Version 2.0
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
# Reused for artifact-signature timestamp canonicalization (see
# _canonical_timestamp): same tolerant ISO-8601 parser already used by the
# tool_execution_log hash chain, instead of a second ad-hoc implementation.
from vigia.core.hash_chain import _parse_iso_ts

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

# R4-3 (docs/TAXA_DOMINIOS_RECOLECCION.md, taxonomía v2 validada por el
# colectivo con CR-001..004 de Kimi): dominios de RECOLECCIÓN por modo de
# fabricación compartido — si un solo acto del atacante puede producir dos
# artefactos, su corroboración mutua vale menos que la de dos dominios
# distintos. El mapa v1 era código muerto (0 consumidores) y clasificaba
# log_entry como "network" — un syslog que habla de red no es telemetría de
# red: comparte modo de fabricación con cualquier otro log.
# Formato: evidence_type -> (dominio, sub_banda). Las sub-bandas (D1a/D1b,
# D5-hard/media/soft) refinan el factor de fabricación INTRA-dominio.
_DOMAIN_MAP: dict = {
    # D1 — log_symbolic (texto declarativo; nada estructural que comprometer)
    "log_entry":                    ("log_symbolic", "D1a"),
    "event_log":                    ("log_symbolic", "D1a"),
    "plaintext_credential":         ("log_symbolic", "D1a"),
    "email_account_creation":       ("log_symbolic", "D1a"),
    "windows_event_log":            ("log_symbolic", "D1b"),  # EVTX tamper-evident (CR-002)
    "hmac_audit_log":               ("log_symbolic", "D1b"),
    # D2 — memory_kernel (compromiso live / Ring-0)
    "memory_process":               ("memory_kernel", "D2"),
    "memory_dump":                  ("memory_kernel", "D2"),
    "lsass_session":                ("memory_kernel", "D2"),
    "kernel_structure":             ("memory_kernel", "D2"),
    "memory_os_profile":            ("memory_kernel", "D2"),
    "keylogger_capture":            ("memory_kernel", "D2"),  # implante vivo (CR-001)
    # D3 — filesystem_metadata (misma imagen de disco / registro del OS)
    "file_timestamp":               ("filesystem_metadata", "D3"),
    "file_hash":                    ("filesystem_metadata", "D3"),
    "file_metadata":                ("filesystem_metadata", "D3"),
    "registry_key":                 ("filesystem_metadata", "D3"),
    "registry_hive":                ("filesystem_metadata", "D3"),
    "mft_entry":                    ("filesystem_metadata", "D3"),
    "shimcache":                    ("filesystem_metadata", "D3"),
    "filesystem_artifact":          ("filesystem_metadata", "D3"),
    "deleted_file_recovery":        ("filesystem_metadata", "D3"),
    "disk_image":                   ("filesystem_metadata", "D3"),
    "usn_journal":                  ("filesystem_metadata", "D3"),
    "usn_journal_gap":              ("filesystem_metadata", "D3"),
    "timestamp_precision":          ("filesystem_metadata", "D3"),
    "prefetch":                     ("filesystem_metadata", "D3"),
    # B-092 — banda mobile de EVIDENCE_PROFILES (TAXA no la censó: ausente de
    # data/cases). Registros locales en disco escritos por apps en user-space,
    # fabricables editando el archivo (un loop inserta N filas en el SQLite):
    # canal D3, no D1 (el contenido no define el dominio) ni D5 (sin costo
    # por-artefacto). location_data: cache local del dispositivo; si un caso
    # aporta telemetría de OPERADOR debe tipificarse distinto (D4), no
    # reclasificar este tipo. Ver MACOS_MODULES_DESIGN.md §9.1-b.
    "web_search":                   ("filesystem_metadata", "D3"),
    "app_data":                     ("filesystem_metadata", "D3"),
    "contact_data":                 ("filesystem_metadata", "D3"),
    "call_log":                     ("filesystem_metadata", "D3"),
    "sms":                          ("filesystem_metadata", "D3"),
    "chat_message":                 ("filesystem_metadata", "D3"),
    "location_data":                ("filesystem_metadata", "D3"),
    # D4 — network_telemetry (control del canal en el momento del tráfico)
    "network_flow":                 ("network_telemetry", "D4"),
    "network_traffic":              ("network_telemetry", "D4"),
    "network_capture":              ("network_telemetry", "D4"),
    "network_artifact":             ("network_telemetry", "D4"),
    "network_connection":           ("network_telemetry", "D4"),
    "network_communication_pattern": ("network_telemetry", "D4"),
    "dns_record":                   ("network_telemetry", "D4"),
    "ip_geolocation":               ("network_telemetry", "D4"),
    "user_agent":                   ("network_telemetry", "D4"),
    "malware_infrastructure":       ("network_telemetry", "D4"),
    # B-092: registro del lado del servicio — no fabricable editando el disco
    # local; su fabricación exige controlar la cuenta/plataforma (canal D4).
    "social_media":                 ("network_telemetry", "D4"),
    # D5 — content_artifact (fabricación de contenido, costo por-artefacto)
    "cryptographic_hash":           ("content_artifact", "D5-hard"),
    "TPM_attestation":              ("content_artifact", "D5-hard"),  # CR-003
    "digital_signature":            ("content_artifact", "D5-hard"),
    "hardware_serial":              ("content_artifact", "D5-hard"),
    "binary":                       ("content_artifact", "D5-media"),
    "binary_executable":            ("content_artifact", "D5-media"),
    "pe_executable":                ("content_artifact", "D5-media"),
    "elf_executable":               ("content_artifact", "D5-media"),
    "binary_diff":                  ("content_artifact", "D5-media"),
    "malware_static_analysis":      ("content_artifact", "D5-media"),
    "document":                     ("content_artifact", "D5-media"),
    "document_visual":              ("content_artifact", "D5-media"),
    "document_geometry":            ("content_artifact", "D5-media"),
    "spreadsheet":                  ("content_artifact", "D5-media"),
    "file_text":                    ("content_artifact", "D5-media"),
    "email_content":                ("content_artifact", "D5-media"),
    "web_artifact":                 ("content_artifact", "D5-media"),
    "archive":                      ("content_artifact", "D5-media"),
    "container_zip":                ("content_artifact", "D5-media"),
    "git_forensics":                ("content_artifact", "D5-media"),
    "cultural_marker":              ("content_artifact", "D5-soft"),
    "osint":                        ("content_artifact", "D5-soft"),
    # B-136: fracturas documentales. D5-soft y NO D5-media deliberadamente:
    # la exención D5-media asume costo por-artefacto ("10 binarios SON 10
    # actos de fabricación"), pero estos tipos emiten N fracturas del MISMO
    # documento/lote analizado (adversarial_nlp: una por fractura del mismo
    # verdict; entanglement: N del mismo batch) — correlacionadas, no actos
    # independientes. Exentarlas del decay de cola dejaría que un solo
    # documento infle el composite sin límite (el drowning que R4-3 mató).
    "linguistic_forensics":         ("content_artifact", "D5-soft"),
    "batch_forensics":              ("content_artifact", "D5-soft"),
    "temporal_fraud":               ("content_artifact", "D5-soft"),
    # D0 — assurance_context (describe la ADQUISICIÓN, no el ataque;
    # alineado con _EVIDENCE_ROLE de B-070)
    "acquisition_context":          ("assurance_context", "D0"),
    "device_acquisition_timeline":  ("assurance_context", "D0"),
    "behavioral_context":           ("assurance_context", "D0"),
    "behavioral_profile":           ("assurance_context", "D0"),
    "outcome_signal":               ("assurance_context", "D0"),
}

def classify_domain(evidence_type: str) -> str:
    """Dominio de recolección de un evidence_type (R4-3, taxonomía v2).

    Un tipo desconocido recibe su PROPIO dominio ("UNKNOWN:<tipo>") —
    conservador: no satura contra otros desconocidos distintos, pero N
    copias del mismo tipo desconocido sí comparten grupo de saturación."""
    entry = _DOMAIN_MAP.get(evidence_type)
    if entry is None:
        return f"UNKNOWN:{evidence_type}"
    return entry[0]


def classify_domain_subband(evidence_type: str) -> tuple:
    """(dominio, sub_banda) — las sub-bandas D1a/D1b y D5-hard/media/soft
    refinan el factor de fabricación intra-dominio (TAXA v2, CR-002/CR-004)."""
    entry = _DOMAIN_MAP.get(evidence_type)
    if entry is None:
        return (f"UNKNOWN:{evidence_type}", "UNKNOWN")
    return entry

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
    "windows_event_log":    EvidenceProfile(0.55, 0.25, "Windows EVTX -- binary format, record IDs, chunk checksums, tamper-evident"),
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

    # B-066 (AUDITORIA_MOBILE_WHITELIST §2): mobile forensics evidence types.
    # Calibración por analogía con la escala existente: "editable con root"
    # ≈ registry_key (0.55, "writable with privs"); lo que sube el peso es la
    # correlacionabilidad externa (carrier CDR, server-side, cell towers).
    # Cero apariciones en el corpus al momento de agregarlos — extensión sin
    # efecto retroactivo.
    "chat_message":         EvidenceProfile(0.35, 0.28, "App chat DB (SQLite WAL + FK integrity) -- server-correlatable, coherent forgery requires root + tooling"),
    "sms":                  EvidenceProfile(0.40, 0.26, "mmssms.db / sms.db -- editable with root, carrier CDR correlatable"),
    "call_log":             EvidenceProfile(0.40, 0.26, "calllog.db -- editable with root, carrier CDR correlatable"),
    "web_search":           EvidenceProfile(0.45, 0.24, "Browser history SQLite -- editable with root, visit chains cross-checkable"),
    "app_data":             EvidenceProfile(0.50, 0.22, "App-private storage -- heterogeneous, no uniform guarantee"),
    "social_media":         EvidenceProfile(0.55, 0.22, "Social app client cache -- editable, server-side correlation out of local exam scope"),
    "location_data":        EvidenceProfile(0.30, 0.30, "Location history (GPS/Takeout) -- consistent forgery vs cell towers is hard"),
    "contact_data":         EvidenceProfile(0.60, 0.20, "contacts2.db -- trivially editable with root; value is structural (empty/unknown-sender)"),

    # B-136 (docs/PROPUESTA_B136_CAIE_WIRING_20260717.md): document-domain
    # types used by the three orphan CAIE injection sites (adversarial_nlp,
    # entanglement, temporal_forensics_redteam). Calibrated by analogy with
    # the existing scale — the same method B-066 used for the mobile band.
    # Anchors: document_visual 0.40, document_geometry 0.45 ("harder to fake
    # than text"), file_timestamp 0.70. Zero corpus occurrences at the time
    # of addition — extension with no retroactive effect. Their B-070 role
    # is CONTEXTUAL (see _EVIDENCE_ROLE below): they inform the composite
    # but never corroborate the device gate.
    "linguistic_forensics": EvidenceProfile(0.60, 0.18, "Stylometric/linguistic incongruence -- text is the most fakeable document layer (imitable style, LLM laundering); a DETECTED incongruence is real but single-modality"),
    "batch_forensics":      EvidenceProfile(0.45, 0.22, "Cross-document batch entanglement -- retroactively forging statistical independence across a batch is hard; analogous to document_geometry"),
    "temporal_fraud":       EvidenceProfile(0.55, 0.20, "Intra-document temporal contradiction -- document date claims are spoofable (cf. file_timestamp), but an engineered self-consistent contradiction is harder than a single timestamp"),
}

# B-067: tipos EN USO en el corpus que nunca fueron perfilados. Hasta este
# fix viajaban con el fallback implícito (0.50, 0.20); la corrida comparativa
# demostró que sus veredictos dependen de facto de esos valores (6 flips al
# endurecer el fallback, 3 contra expected_verdict). Se pinnean EXPLÍCITOS al
# valor legacy exacto — comportamiento bit a bit idéntico, cero flips — y el
# fallback para tipos realmente desconocidos pasa a la peor clase conocida.
# PENDIENTE DE CALIBRACIÓN: estos valores son el legacy heredado, no una
# decisión forense por tipo. Calibrarlos es un trabajo aparte (ver
# AUDITORIA_MOBILE_WHITELIST §3.1: mover estos perfiles mueve ~193 artefactos).
_LEGACY_UNCALIBRATED = EvidenceProfile(
    0.50, 0.20, "Uncalibrated -- pinned at legacy fallback value (B-067), pending per-type calibration"
)
EVIDENCE_PROFILES.update({
    t: _LEGACY_UNCALIBRATED for t in (
        "binary", "binary_executable", "elf_executable", "pe_executable",
        "binary_diff", "malware_static_analysis", "malware_infrastructure",
        "document", "spreadsheet", "file_text", "web_artifact",
        "container_zip", "archive", "disk_image", "filesystem_artifact",
        "deleted_file_recovery", "registry_hive", "shimcache", "event_log",
        "network_traffic", "network_capture", "network_communication_pattern",
        "email_content", "email_account_creation", "keylogger_capture",
        "osint", "git_forensics", "TPM_attestation", "acquisition_context",
        "memory_os_profile", "device_acquisition_timeline",
        "behavioral_context", "behavioral_profile", "outcome_signal",
        "plaintext_credential",
        # Placeholder que normalize_case_schema asigna a artefactos SIN
        # evidence_type declarado — población legacy sin etiquetar, no un
        # tipo adversarial inventado (case_009 dependía de él).
        "default",
    )
})

# Whitelist of valid evidence types — any type not in this set is rejected
_VALID_EVIDENCE_TYPES: Final[frozenset[str]] = frozenset(EVIDENCE_PROFILES.keys())

# ---------------------------------------------------------------------------
# B-070 — Rol epistémico del evidence_type (device / contextual / narrative)
#
# Fuente ÚNICA de verdad (semilla del registro unificado de tipos de B-060).
# Resuelve la causa raíz (b) del FP NGDC-003 (AUDITORIA_ABDUCTIVA_NGDC003_FP):
# el modelo de datos no distinguía evidencia-de-dispositivo de contexto-
# narrativo, así que ambos fluían al composite de malicia y al gate de
# corroboración por igual. Con esto, cada consumidor (scorer, gate, CAIE)
# consulta el mismo registro en vez de parchear su propia lista.
#
#   DEVICE     — evidencia derivada del dispositivo. Cuenta en el composite
#                de malicia Y como fuente de corroboración (gate). Default:
#                un tipo desconocido se trata como DEVICE (conservador — no
#                deja de contar por no estar clasificado).
#   CONTEXTUAL — evidencia device-adyacente (OSINT, metadata de adquisición).
#                Cuenta en el composite (puede portar señal de anomalía real,
#                ej. un deployment off-hours) pero NO es una fuente
#                independiente de dispositivo → NO corrobora (gate).
#   NARRATIVE  — documentación de escenario: motivo, persona, desenlace. NO
#                mueve el score de malicia ni corrobora. Informa solo la
#                narrativa del reporte. Es la clase cuyo propio texto suele
#                declarar la intención indecidible ("consistent with both
#                hypotheses") — contarla como malicia es la inversión que
#                producía el FP.
# ---------------------------------------------------------------------------
EVIDENCE_ROLE_DEVICE: Final[str] = "device"
EVIDENCE_ROLE_CONTEXTUAL: Final[str] = "contextual"
EVIDENCE_ROLE_NARRATIVE: Final[str] = "narrative"

_EVIDENCE_ROLE: Final[dict[str, str]] = {
    # Narrativa de escenario — fuera del composite y del gate
    "behavioral_context":          EVIDENCE_ROLE_NARRATIVE,
    "behavioral_profile":          EVIDENCE_ROLE_NARRATIVE,
    "outcome_signal":              EVIDENCE_ROLE_NARRATIVE,
    # Contextual device-adyacente — en el composite, fuera del gate
    "osint":                       EVIDENCE_ROLE_CONTEXTUAL,
    "acquisition_context":         EVIDENCE_ROLE_CONTEXTUAL,
    "device_acquisition_timeline": EVIDENCE_ROLE_CONTEXTUAL,
    # B-136: forense documental — informa el composite (una fractura
    # estilométrica/de lote/temporal es señal real de malicia) pero NO es
    # una fuente independiente de dispositivo: una fractura single-modality
    # no debe desbloquear el gate de corroboración. Asimetría documentada:
    # document_visual/document_geometry siguen DEVICE por ahora (moverlos
    # tiene efecto retroactivo sobre el corpus; decisión aparte con su
    # propia corrida comparativa — PROPUESTA_B136 §2).
    "linguistic_forensics":        EVIDENCE_ROLE_CONTEXTUAL,
    "batch_forensics":             EVIDENCE_ROLE_CONTEXTUAL,
    "temporal_fraud":              EVIDENCE_ROLE_CONTEXTUAL,
    # (todo lo demás → DEVICE por defecto, incluido cualquier tipo desconocido)
}


def evidence_role(evidence_type: str) -> str:
    """Rol epistémico de un evidence_type (B-070). Default DEVICE:
    un tipo no clasificado cuenta como evidencia de dispositivo (conservador —
    nunca deja de contar por falta de clasificación)."""
    return _EVIDENCE_ROLE.get(evidence_type, EVIDENCE_ROLE_DEVICE)


# R3-1 — Ventana forense plausible para timestamps en la regla TCV.
# LIMITES FIJOS (no now()): la reproducibilidad bit-a-bit del pipeline (Daubert,
# invariante 4 de CLAUDE.md) prohibe reloj de pared en el scoring path — el
# mismo caso debe puntuar identico hoy y en 2030. Fechas fuera de esta ventana
# se leen como DATO AUSENTE, no como senal temporal.
#   MIN 2000-01-01 : era de la forensia digital moderna; descarta 1970 (epoch
#                    Unix / sentinela de fecha no parseada) y 1601 (FILETIME).
#   MAX 2038-01-19 : desbordamiento del epoch Unix de 32 bits con signo — techo
#                    forense natural y bien entendido; descarta 2099/9999.
# El corpus real vive en [2004, 2026] (medido) — cero artefactos legitimos
# tocados. Revisar el techo antes de 2038 (limitacion documentada).
_TCV_PLAUSIBLE_MIN: Final[datetime] = datetime(2000, 1, 1, tzinfo=timezone.utc)
_TCV_PLAUSIBLE_MAX: Final[datetime] = datetime(2038, 1, 19, 3, 14, 7, tzinfo=timezone.utc)

# Maximum artifacts per evaluation — prevents DoS via artifact flooding
_MAX_ARTIFACTS: Final[int] = 1000

# Minimum independent sources for full confidence (P1: normalization)
_MIN_INDEPENDENT_SOURCES: Final[int] = 3
_LOW_SOURCE_PENALTY: Final[float] = 0.20  # Reduce score by 20% if < 3 sources

# COGNITIVE/SCORING FLOOD FIX: independent_sources originally counted every
# distinct (source_tool, evidence_type) GROUP, regardless of how much that
# group actually contributed to the fused score -- a group's own raw_score
# and spoofability never entered the count, only its existence as a label.
# This is gameable in a way that is NOT just a narrative/display problem:
# padding a case with cheap, distinct-labeled, near-worthless artifacts (a
# tool that emits low-confidence findings, or an attacker manufacturing
# junk categories) can push independent_sources across the
# _MIN_INDEPENDENT_SOURCES=3 line and WAIVE the 20% confidence_penalty
# entirely, even though nothing was genuinely corroborated. Confirmed
# empirically: 2 solid artifacts alone score 0.3083 with the penalty
# correctly applied (INCONCLUSIVE); adding 3 trivial-but-distinct-group
# artifacts (raw_score=0.02 each, high-spoofability evidence_type) escapes
# the penalty entirely and raises the score to 0.3879 (+26%) and the
# verdict to SUSPICION -- from evidence that, standing alone, would barely
# register.
#
# _SOURCE_MATERIALITY_FLOOR: a group only counts toward independent_sources
# if SOME member artifact's own RAW_SCORE (pre-spoofability) reaches this
# floor -- deliberately RAW, not the spoofability-adjusted group_score.
# First attempt used group_score and immediately broke a legitimate case:
# a real log_entry finding at raw_score=0.55 (a genuine, moderate-confidence
# assertion) adjusts down to 0.0404 given log_entry's spoofability=0.85 --
# BELOW a 0.05 floor on the adjusted score, so a real corroborating source
# would have been wrongly excluded for being an inherently-spoofable
# evidence TYPE, which is a different thing from being unsubstantiated
# padding. raw_score isolates "did the tool/analyst assert at least minimal
# analytical confidence" from "how much do we discount this evidence type",
# which is exactly what spoofability weighting already does correctly
# downstream in adjusted_score / composite_score -- materiality should not
# re-apply that discount a second time. The padding reproduction above used
# raw_score=0.02, deliberately near zero; 0.05 sits well below any
# genuine finding in this codebase's own test corpus while still excluding
# that padding. This does NOT remove low-scoring groups from the composite
# Noisy-OR fusion itself (their small, honest contribution to
# composite_score is correct and stays); it only stops manufactured
# near-zero-confidence artifacts from also buying an exemption from the
# low-corroboration penalty.
_SOURCE_MATERIALITY_FLOOR: Final[str] = "0.05"

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
    "windows_event_log": Fraction(1, 5),
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
        # B-067: fuente única — self.profile (que trata el tipo desconocido
        # como la peor clase conocida). Acá había un default duplicado
        # (0.50, 0.20) que reabría el bypass aunque profile estuviera bien.
        _intrinsic = self.profile.spoofability
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

        # Normalize metadata keys: strip whitespace and NFKC-fold Unicode
        # Prevents invisible characters (ZWSP, NBSP, cyrillic lookalikes) from
        # bypassing field detection in _extract_assertions().
        # B-016 fix: 'dst_ip\u200b' was silently treated as unknown field.
        import unicodedata
        if self.metadata:
            self.metadata = {
                unicodedata.normalize("NFKC", k).strip().strip("\u200b\u200c\u200d\u200e\u200f\ufeff\u2060"): v
                for k, v in self.metadata.items()
            }

    @property
    def profile(self) -> EvidenceProfile:
        # B-067: el default para tipo DESCONOCIDO no puede ser mejor que la
        # peor clase conocida. Con (0.50, 0.20), un tipo inventado puntuaba
        # MÁS ALTO que log_entry (0.85, 0.15) — el bypass exacto que el
        # whitelist de add_artifact dice prevenir ("Unknown types could
        # bypass spoofability weighting"), abierto en el camino del scorer.
        # (0.90, 0.15) = ip_geolocation/cultural_marker, la peor clase real:
        # invariante (1-spoof)×weight del desconocido ≤ mínimo de la tabla.
        return EVIDENCE_PROFILES.get(
            self.evidence_type,
            EvidenceProfile(0.90, 0.15, "Unknown evidence type -- treated as worst known class (B-067)"),
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


_RESERVED_IPS: frozenset = frozenset({
    "127.0.0.1", "localhost", "::1",
    "0.0.0.0", "::",
    "255.255.255.255",
})


def _is_reserved_ip(ip: str) -> bool:
    """
    Returns True if ip is a reserved/non-routable address that cannot
    represent a real outbound C2 connection.
    Daubert rationale: a connection to 127.0.0.1 is intra-process —
    structurally impossible to be exfiltration.
    RFC 1918 private ranges (10.x, 172.16.x, 192.168.x) are intentionally
    NOT filtered — lateral movement to internal hosts is a valid IOC.
    """
    ip_clean = ip.strip().lower()
    if ip_clean in _RESERVED_IPS:
        return True
    if ip_clean.startswith("127."):
        return True
    if ip_clean.startswith("fe80:"):
        return True
    return False


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
        _dst = meta.get("dst_ip") or meta.get("dest_ip")
        if _dst and isinstance(_dst, str) and _dst.strip() and not _is_reserved_ip(_dst):
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
        # B-154: "analyzed, no activity" and "network layer never analyzed" are
        # OPPOSITE epistemic states, not two ways of saying the same thing. The
        # old two-valued model (has_network True/False) collapsed them, so an
        # ABSENT network field emitted memory_shows_no_network_activity — a
        # positive observation that then feeds the LOG_VS_MEMORY fabrication rule
        # (line ~1528), letting "I did not look" accuse a log of fabrication.
        # Four-state model (Forge disposition.py / Cronos detect_negation
        # doctrine, both ported from VIGÍA: not-analyzed != clean; absence !=
        # negative confirmation). Key PRESENCE ("in meta") decides whether the
        # network layer was analyzed at all — .get() truthiness cannot.
        _NET_KEYS = ("dest_ip", "source_ip", "network_connections")
        _net_present = {k: meta[k] for k in _NET_KEYS if k in meta}
        _nc      = _net_present.get("network_connections")
        _dest_ip = _net_present.get("dest_ip")
        _src_ip  = _net_present.get("source_ip")
        _nc_valid   = isinstance(_nc, (list, dict)) and bool(_nc)
        _dest_valid = isinstance(_dest_ip, str) and bool(_dest_ip.strip())
        _src_valid  = isinstance(_src_ip,  str) and bool(_src_ip.strip())
        has_network = _dest_valid or _src_valid or _nc_valid
        # A present network key whose value is the wrong type is a FAILED
        # analysis (e.g. network_connections arriving as a string), not a clean
        # negative — it must not accuse either.
        _malformed = (
            ("network_connections" in _net_present and not isinstance(_nc, (list, dict)))
            or ("dest_ip" in _net_present and not isinstance(_dest_ip, str))
            or ("source_ip" in _net_present and not isinstance(_src_ip, str))
        )
        if has_network:
            assertions.add("memory_shows_network_activity")      # ANALYZED_WITH_ACTIVITY
        elif not _net_present:
            assertions.add("memory_network_not_analyzed")        # NOT_ANALYZED
        elif _malformed:
            assertions.add("memory_network_analysis_failed")     # ANALYSIS_FAILED
        else:
            assertions.add("memory_shows_no_network_activity")   # ANALYZED_NO_ACTIVITY

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


def _canonical_timestamp(ts: str) -> str:
    """
    UTC-normalized ISO-8601 form of *ts*, so two artifacts describing the
    exact same instant hash identically regardless of which UTC offset the
    producing tool happened to print (e.g. "2025-01-01T12:00:00Z" and
    "2025-01-01T09:00:00-03:00" are the same instant). Falls back to the raw
    string if unparseable -- never raise on a malformed timestamp, just
    don't canonicalize it (same tolerant contract as _parse_iso_ts itself).

    This is deliberately a pure canonicalization (one instant -> one
    string), not similarity/fuzzy matching: signature equality built on top
    of it stays an exact-equality relation (reflexive, symmetric,
    transitive) rather than a "close enough" comparison, which would not be
    transitive in general (A~B and B~C does not imply A~C for a distance
    threshold).
    """
    dt = _parse_iso_ts(ts)
    return dt.astimezone(timezone.utc).isoformat() if dt is not None else ts


def _artifact_content_signature(artifact: Artifact) -> str:
    """
    SHA-256 over every identity-relevant field of *artifact* (post
    __post_init__ normalization): source_tool, evidence_type, raw_score,
    description, metadata, provenance_chain, timestamp (UTC-canonicalized).
    Two artifacts with an identical signature are the exact same submitted
    fact, not two independently-corroborating observations.

    This is a forensic-identity signature, not a byte-identity hash: "same
    fact" is intentionally slightly broader than "same JSON bytes" — right
    now that means timestamp UTC-normalization (see _canonical_timestamp).
    It deliberately does NOT fold case or coerce types across all of
    metadata (e.g. host="SERVER01" vs "server01", pid="123" vs 123):
    hostnames are case-insensitive but a Linux path is not, and blanket
    normalization would trade a false-negative (missed duplicate) for a
    false-positive (two genuinely different facts conflated) in fields
    whose semantics this function cannot know. See
    CrossArtifactIncongruenceEngine.add_artifact's superset-based
    REFINEMENT handling for the complementary case: an artifact that adds
    strictly more metadata to an existing one (not a different
    representation of the same fields) supersedes it instead of being
    treated as independent corroboration.
    """
    payload = {
        "source_tool": artifact.source_tool,
        "evidence_type": artifact.evidence_type,
        "raw_score": str(artifact.raw_score),
        "description": artifact.description,
        "metadata": artifact.metadata,
        "provenance_chain": artifact.provenance_chain,
        "timestamp": _canonical_timestamp(artifact.timestamp),
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _metadata_is_subset(smaller: dict, larger: dict) -> bool:
    """
    True if every key in *smaller* has an identical value in *larger*
    (recursing into nested dicts); *larger* may have additional keys
    *smaller* lacks. List/scalar values must match exactly — no partial
    credit for lists, since "subset of a list" is order/membership-
    ambiguous and not worth the complexity here. Used to detect when one
    artifact is a strict REFINEMENT of another (same fact, more detail),
    as opposed to a conflicting or genuinely independent observation (e.g.
    pid=100 vs pid=200 is neither a subset nor a superset — two different
    processes, correctly kept as two artifacts).
    """
    for k, v in smaller.items():
        if k not in larger:
            return False
        lv = larger[k]
        if isinstance(v, dict) and isinstance(lv, dict):
            if not _metadata_is_subset(v, lv):
                return False
        elif v != lv:
            return False
    return True


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
        # P1 (evidence integrity): TCV pairs omitted because a required event
        # timestamp was present but unparseable/out-of-range. Recorded here so
        # the omission is surfaced in the (signed) result and can drive an
        # honest disposition, instead of only living in the HMAC audit log.
        self._temporal_pairs_skipped: list[dict] = []
        # Duplicate-artifact epistemology fix (see add_artifact): content
        # signatures of every artifact accepted so far, to reject exact
        # resubmissions before they inflate Noisy-OR fusion.
        self._seen_content_signatures: set[str] = set()

    def add_artifact(self, artifact: Artifact) -> bool:
        """
        Add an artifact from a VIGIA tool result.

        Returns True if added or if it refined/replaced an existing
        artifact in place (see REFINEMENT below); False if rejected (limit,
        invalid type, exact duplicate, or redundant refinement).

        Kimi P0 enforcement:
        - Rejects if _MAX_ARTIFACTS exceeded (DoS protection)
        - Rejects if evidence_type is not in the whitelist

        Duplicate-content rejection (epistemology fix): evaluate() fuses
        artifacts within a (source_tool, evidence_type) group via Noisy-OR
        (1 - prod(1 - s)), which compounds every additional score as if it
        were independent corroboration. Submitting the exact same artifact
        N times (a duplicate log entry, a tool re-run whose output gets
        ingested twice, or deliberate padding) is not N independent
        observations -- it is one fact reported N times -- yet each
        resubmission still raised composite_score, and
        _MIN_INDEPENDENT_SOURCES only counts distinct (source_tool,
        evidence_type) pairs, not distinct underlying facts within a pair.
        Empirically: 3 genuinely distinct weak artifacts (one per
        source/type, raw_score=0.55 each) scored SUSPICION (composite
        ~0.24); duplicating each one 3x (9 total artifacts, still only 3
        source/type pairs, zero new facts) reached MALICE (composite
        ~0.56) with structural_verdict staying NOISE throughout -- the
        entire escalation was duplicate-driven, not evidence-driven.
        _artifact_content_signature() rejects only byte-identical
        resubmissions (same source_tool, evidence_type, raw_score,
        description, metadata, provenance_chain, timestamp); a genuinely
        distinct second occurrence (different PID, different
        acquisition_hash, different timestamp, ...) still gets a different
        signature and is accepted as new evidence.
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

        _sig = _artifact_content_signature(_artifact_copy)
        if _sig in self._seen_content_signatures:
            audit_logger.log_block(
                event_type="CAIE_DUPLICATE_ARTIFACT",
                tool="CAIE.add_artifact",
                input_preview=f"source={artifact.source_tool} type={artifact.evidence_type}",
                reason=(
                    "Artifact is byte-identical to one already added in this "
                    "evaluation (same source_tool, evidence_type, raw_score, "
                    "description, metadata, provenance_chain, timestamp). "
                    "Duplicate submissions are not independent corroboration -- "
                    "Noisy-OR fusion would double-count the same fact. Rejected."
                ),
            )
            return False

        # REFINEMENT / SUBSUMPTION (I-0XX generalization): a new artifact
        # that adds strictly more metadata to an already-accepted artifact
        # describing the exact same EVENT is not a second independent
        # observation either — a tool re-parsing the same evidence with more
        # detail ("Suspicious process" -> "Suspicious process" + pid +
        # sha256) is one fact reported twice at different resolutions, and
        # would otherwise inflate Noisy-OR fusion exactly like the
        # exact-duplicate case. Symmetrically: if the NEW artifact carries
        # strictly LESS metadata than one already stored for the same event,
        # it is redundant and rejected outright (the stored one already
        # dominates it). Neither branch fires when metadata is incomparable
        # (e.g. pid=100 vs pid=200) or the description differs — those are
        # kept as genuinely independent artifacts, unchanged from prior
        # behavior.
        #
        # "Same event" REQUIRES matching timestamp and provenance_chain, not
        # just source_tool/evidence_type/description: two artifacts that
        # both happen to carry empty/no metadata (e.g. two MFT records both
        # missing mft_entry_number) share source_tool+evidence_type+
        # description and are trivially "metadata subsets" of each other,
        # but a different timestamp or provenance_chain means a genuinely
        # different occurrence — collapsing them would silently destroy a
        # real, distinct MFT_ENTRY_ANOMALY-eligible artifact
        # (test_caie_mft_entry_guard.py caught exactly this while adding
        # this fix). Timestamp is compared canonicalized (same instant,
        # different UTC offset, still counts as the same event).
        for _i, _existing in enumerate(self._artifacts):
            if not (
                _existing.source_tool == _artifact_copy.source_tool
                and _existing.evidence_type == _artifact_copy.evidence_type
                and _existing.description == _artifact_copy.description
                and _existing.provenance_chain == _artifact_copy.provenance_chain
                and _canonical_timestamp(_existing.timestamp)
                == _canonical_timestamp(_artifact_copy.timestamp)
            ):
                continue
            if _metadata_is_subset(_existing.metadata, _artifact_copy.metadata):
                # New artifact refines/supersedes the stored one. Retain the
                # higher raw_score -- a refinement must never look LESS
                # confident than the vaguer report it replaces.
                if _existing.raw_score > _artifact_copy.raw_score:
                    _artifact_copy.raw_score = _existing.raw_score
                self._seen_content_signatures.discard(
                    _artifact_content_signature(_existing)
                )
                self._remove_from_indices(_existing)
                self._artifacts[_i] = _artifact_copy
                self._seen_content_signatures.add(
                    _artifact_content_signature(_artifact_copy)
                )
                self._add_to_indices(_artifact_copy)
                audit_logger.log_info(
                    event_type="CAIE_ARTIFACT_REFINED",
                    tool="CAIE.add_artifact",
                    message=(
                        f"source={artifact.source_tool} type={artifact.evidence_type}: "
                        "new artifact carries a superset of an existing artifact's "
                        "metadata for the same event -- replaced in place instead of "
                        "counted as independent corroboration."
                    ),
                )
                return True
            if _metadata_is_subset(_artifact_copy.metadata, _existing.metadata):
                # New artifact carries no information the stored one lacks.
                audit_logger.log_block(
                    event_type="CAIE_REDUNDANT_REFINEMENT",
                    tool="CAIE.add_artifact",
                    input_preview=f"source={artifact.source_tool} type={artifact.evidence_type}",
                    reason=(
                        "Artifact's metadata is a subset of an already-accepted "
                        "artifact describing the same event (same source_tool, "
                        "evidence_type, description). It carries no new information "
                        "-- rejected rather than double-counted."
                    ),
                )
                return False

        self._seen_content_signatures.add(_sig)
        self._artifacts.append(_artifact_copy)
        self._add_to_indices(_artifact_copy)
        return True

    def _add_to_indices(self, artifact: "Artifact") -> None:
        """Index a stored artifact for temporal (TCV) and network correlation."""
        if artifact.timestamp:
            self._temporal_index.setdefault(artifact.timestamp, []).append(artifact)
        if "network" in artifact.evidence_type or "ip" in artifact.evidence_type:
            self._network_index.setdefault(artifact.source_tool, []).append(artifact)

    def _remove_from_indices(self, artifact: "Artifact") -> None:
        """
        Remove *artifact* (by identity, not equality) from the temporal and
        network indices. Required when a REFINEMENT replaces an artifact
        in-place: without this, the superseded object stays reachable from
        _temporal_index / _network_index (used by TCV and NETWORK_VS_HOST
        fracture rules) even though it is no longer in self._artifacts --
        a stale reference to evidence the engine has otherwise forgotten.
        """
        bucket = self._temporal_index.get(artifact.timestamp)
        if bucket is not None:
            bucket[:] = [a for a in bucket if a is not artifact]
            if not bucket:
                del self._temporal_index[artifact.timestamp]
        net_bucket = self._network_index.get(artifact.source_tool)
        if net_bucket is not None:
            net_bucket[:] = [a for a in net_bucket if a is not artifact]
            if not net_bucket:
                del self._network_index[artifact.source_tool]

    def add_from_tool_result(
        self,
        tool_name: str,
        result: dict,
        evidence_type: str = "log_entry",
        provenance_chain: list[str] | None = None,
    ) -> bool:
        """
        Convenience: extract an artifact from a standard VIGIA tool result dict.

        Looks for 'suspicion_score', 'probability_*', or 'visual_malice_score'
        to derive the raw score. Falls back to 0.0 if no score field found.

        B-114: delegates to add_artifact() so the Kimi P0 guardrails
        (_MAX_ARTIFACTS anti-flooding limit, evidence_type whitelist) apply
        to this path too — the previous direct append bypassed both, and any
        MCP tool using this wrapper inherited the hole. Returns add_artifact's
        verdict: True if added, False if rejected.
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

        return self.add_artifact(Artifact(
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
        self._temporal_pairs_skipped.clear()

        # Group artifacts by evidence type category
        technical = [a for a in self._artifacts if a.evidence_type in
                     ("memory_process", "lsass_session", "kernel_structure",
                      "usn_journal", "hmac_audit_log")]
        logs = [a for a in self._artifacts if a.evidence_type == "log_entry"]
        documents = [a for a in self._artifacts if a.evidence_type in
                     ("document_visual", "document_geometry")]
        cryptographic = [a for a in self._artifacts if a.evidence_type in
                         ("cryptographic_hash", "digital_signature")]
        host_logs = [a for a in self._artifacts if a.evidence_type in
                     ("log_entry", "memory_process") and "socket" in str(a.metadata).lower()]

        # Rule 1: marker-class discrimination (M2)
        # Ref: docs/M2_DISCRIMINATORS_DESIGN_20260711.md and
        # docs/FOSSIL_HUNT_20260711.md (mechanism M2, F-07..F-28).
        #
        # The pre-M2 rule collapsed every high-scoring cultural_marker with
        # weak memory corroboration into one theory — "cultural evidence
        # planted to mislead attribution" — which was the sealed narrative in
        # 22 corpus firings where it was never true: genuine linguistic traces
        # that ATTRIBUTE the actor (the exact inverse of planted), social-
        # engineering patterns with no attribution question at all, and two
        # clean-foreign-machine controls (H-02 / L-019). The evidence class is
        # now read from the marker's own metadata (deterministic field
        # inventory — typing errors in evidence_type must not decide the
        # sealed theory), and each class carries a theory that matches it:
        #
        #   attribution_bait   -> FALSE_FLAG_PATTERN / _ATTRIBUTION_MISMATCH
        #                         (planted-evidence theory REQUIRES manipulation
        #                         evidence: too_clean placement, TTP mismatch,
        #                         timestomp/backdating on the markers)
        #   attribution_genuine-> LINGUISTIC_ATTRIBUTION_SIGNAL (the trace is
        #                         real and betrays the actor; nothing planted)
        #   social_engineering -> SOCIAL_ENGINEERING_PATTERN (Carnegie layer;
        #                         no attribution claim is made)
        #   config_native      -> no fracture (Case A is now the default for
        #                         config-only markers: absence of manipulation
        #                         evidence is never treated as guilt, and the
        #                         explicit-False confirmed_clean flags are no
        #                         longer required to stay safe)
        #   unclassified       -> no fracture (a marker whose metadata asserts
        #                         no analysis class carries no theory to seal)
        _MARKER_BOOKKEEPING = frozenset({
            "acquisition_tool", "acquisition_timestamp", "acquisition_hash",
            "acquisition_note", "write_blocker_used", "examiner_id",
        })
        _MARKER_CONFIG_FIELDS = frozenset({
            "cyrillic_filenames", "keyboard_layout_detected", "timezone_offset",
            "language_confidence", "organic_user_files", "normal_creation_dates",
            "document_properties_valid",
        })
        _MARKER_ATTRIBUTION_FIELDS = frozenset({
            # linguistic origin / calque analysis
            "linguistic_origin", "native_language_prob", "attribution_region",
            "intended_russian", "intended_meaning", "calco_source", "calco_1",
            # keyboard/locale slips
            "locale_detected", "keyboard_layout_probability",
            "keyboard_mapping_confidence", "input_method",
            # stylometric deviation / authorship linkage
            "deviation_sigma", "features_anomalous", "shared_anomaly",
            "ttr_similarity", "style_entropy", "stylometric_match",
        })
        _MARKER_SOCIAL_FIELDS = frozenset({
            "tone", "manager_appeal", "guilt_inversion", "phrases_matched",
            "source_phrases", "style_match_score", "tickets_analyzed",
            "messages_analyzed", "pattern_match_count", "response_latency_ms",
            "behavioral_shift", "historical_normalization_count",
            "pattern_entropy", "time_variance_sec", "bot_likelihood",
            "verification_source",
        })

        def _marker_has_manip(md: dict) -> bool:
            # Value-sensitive on purpose: the confirmed-clean controls carry
            # these keys with explicit False values.
            return (
                md.get("mismatch_with_technical_profile") is True
                or md.get("attribution_consistency_with_ttps") == "LOW"
                or md.get("timestomp_detected") is True
                or md.get("backdating_detected") is True
                or md.get("placement") == "too_clean"
            )

        def _marker_class(a: "Artifact") -> str:
            md = a.metadata if isinstance(a.metadata, dict) else {}
            keys = set(md) - _MARKER_BOOKKEEPING
            if _marker_has_manip(md):
                return "attribution_bait"
            if keys & _MARKER_ATTRIBUTION_FIELDS:
                return "attribution_genuine"
            if a.evidence_type != "cultural_marker":
                # Rescued artifacts (below) only qualify via attribution/manip
                # metadata; anything else stays whatever its type says it is.
                return "unclassified"
            if keys & _MARKER_SOCIAL_FIELDS:
                return "social_engineering"
            if keys and keys <= _MARKER_CONFIG_FIELDS:
                return "config_native"
            return "unclassified"

        # Marker pool: cultural_marker-typed artifacts, plus artifacts of any
        # other type whose metadata asserts attribution analysis or marker
        # manipulation (typing errors must not hide attribution evidence:
        # the corpus carries a layout-slip analysis typed ip_geolocation and
        # a stylometric analysis typed file_hash). ip_geolocation/user_agent
        # WITHOUT such fields are network/client telemetry, not culture —
        # they no longer enter this rule at all.
        _marker_pool = [
            a for a in self._artifacts
            if a.evidence_type == "cultural_marker"
            or (isinstance(a.metadata, dict)
                and (set(a.metadata) & _MARKER_ATTRIBUTION_FIELDS
                     or _marker_has_manip(a.metadata)))
        ]
        _by_class: dict = {}
        for _a in _marker_pool:
            _by_class.setdefault(_marker_class(_a), []).append(_a)
        bait_markers = _by_class.get("attribution_bait", [])
        genuine_markers = _by_class.get("attribution_genuine", [])
        social_markers = _by_class.get("social_engineering", [])

        def _avg_raw(arts: list) -> object:
            return _dround(_dsum([a.raw_score for a in arts]) / len(arts),
                           _DETERMINISTIC_INTERNAL_PREC)

        avg_technical = _avg_raw(technical) if technical else _dround(0.0, _DETERMINISTIC_INTERNAL_PREC)

        # confirmed_clean: investigator explicitly verified no manipulation
        # (explicit False values, never mere absence). Scanned across ALL
        # artifacts: the negative controls document it on filesystem
        # artifacts, not only on the marker itself.
        confirmed_clean = any(
            a.metadata.get("timestomp_detected") is False
            or a.metadata.get("backdating_detected") is False
            or a.metadata.get("mft_inconsistency") is False
            or a.metadata.get("suspiciously_obvious") is False
            for a in self._artifacts
        )

        if bait_markers and technical:
            avg_bait = _avg_raw(bait_markers)
            # Case C: genuine false flag — real attack + contradictory attribution
            if avg_bait > 0.5 and avg_technical > 0.5:
                self._fractures.append(Fracture(
                    artifact_a=f"Cultural markers (avg={avg_bait:.2f}, attribution contradicts TTP profile)",
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
            # Case B: planted bait without a real attack behind it. Only fires
            # on markers whose OWN metadata evidences manipulation — "high
            # cultural + low technical" alone is no longer a planting theory.
            elif avg_bait > 0.5 and avg_technical < 0.2 and not confirmed_clean:
                self._fractures.append(Fracture(
                    artifact_a=f"Cultural markers (avg={avg_bait:.2f}, manipulation evidence on markers)",
                    artifact_b=f"Technical evidence (avg={avg_technical:.2f})",
                    fracture_type="FALSE_FLAG_PATTERN",
                    severity=0.8,
                    interpretation=(
                        "Cultural attribution markers carrying manipulation evidence "
                        "(too-clean placement, TTP mismatch, timestomp/backdating) "
                        "with near-zero technical corroboration. False-flag pattern: "
                        "the markers were planted to mislead attribution. "
                        "Peirce Thirdness: the HABIT is to disguise origin, not to act."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1585.001",
                ))

        # attribution_genuine: the trace is real evidence attributing the
        # action; the theory sealed here must never assert planting.
        if genuine_markers:
            avg_genuine = _avg_raw(genuine_markers)
            if avg_genuine > 0.5:
                self._fractures.append(Fracture(
                    artifact_a=f"Linguistic attribution markers (avg={avg_genuine:.2f})",
                    artifact_b=f"Claimed identity / technical context (avg_technical={avg_technical:.2f})",
                    fracture_type="LINGUISTIC_ATTRIBUTION_SIGNAL",
                    severity=0.8,
                    interpretation=(
                        "Involuntary linguistic or behavioral trace (keyboard-layout "
                        "slip, semantic calque, stylometric deviation, authorship "
                        "linkage across personas) inconsistent with the claimed "
                        "identity — or stylistic consistency exceeding human "
                        "biological variance, the signature of machine-fabricated "
                        "style. The trace is genuine evidence ATTRIBUTING the "
                        "action; no evidence-planting theory is asserted. "
                        "Peirce Secondness: the index resists the claimed identity — "
                        "habit betrays the actor."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1036",
                ))

        # social_engineering: Carnegie-layer manipulation of the human control
        # plane; no cultural-attribution claim is made.
        if social_markers:
            avg_social = _avg_raw(social_markers)
            if avg_social > 0.5:
                self._fractures.append(Fracture(
                    artifact_a=f"Social-engineering markers (avg={avg_social:.2f})",
                    artifact_b=f"Technical corroboration (avg_technical={avg_technical:.2f})",
                    fracture_type="SOCIAL_ENGINEERING_PATTERN",
                    severity=0.8,
                    interpretation=(
                        "Systematic interpersonal-manipulation pattern targeting the "
                        "human control layer (Carnegie taxonomy: mirroring, "
                        "normalization, fabricated authority, defensive aggression, "
                        "coordinated panic, instrumental doubt). No cultural-"
                        "attribution claim is made and no evidence-planting theory "
                        "is asserted. "
                        "Peirce Thirdness: the HABIT is to neutralize the human "
                        "verifier, not to disguise origin."
                    ),
                    spoofability_delta=_dround(0.90 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1656",
                ))
        # config_native / unclassified markers: no fracture (Case A default).

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
                log_pids  = {str(a.metadata.get("pid")).strip() for a in logs    if a.metadata.get("pid") is not None}
                tech_pids = {str(a.metadata.get("pid")).strip() for a in technical if a.metadata.get("pid") is not None}
                pid_overlap = log_pids & tech_pids

                # B-105: Fracture.severity is declared float; _dround returns
                # Decimal, which crashes the agent's canonical serializer when
                # this fracture fires. Exact literals need no rounding.
                severity = 0.95 if pid_overlap else 0.75

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
        # Effect-before-cause: a network event precedes the process that
        # supposedly caused it.
        #
        # M1 (docs/FOSSIL_HUNT_20260711.md): structured-fields-only TCV.
        # A pair qualifies only when BOTH event times are asserted as
        # structured metadata: network_log_time for the network event and
        # process_creation_time for the process. Two former branches are
        # removed as inadmissible:
        #   - free-text matching ("network"/"red"/"conexión" as substrings of
        #     the description) classified ANY artifact as network activity on
        #     words like "registered", "flickered", "credentials" or "stored",
        #     and sustained 6 sealed verdicts on comparisons with no causal
        #     relation (registry install keys vs. memory-acquisition snapshot,
        #     vacation-request logs vs. file uploads — gaps up to 11 years);
        #   - fallback to the generic artifact timestamp, which is
        #     collection/acquisition time, not event time. Comparing it
        #     against an event time is a category error, and its _utcnow()
        #     default fabricated a severity-1.0 fracture out of millisecond
        #     object-creation skew on artifacts with no timestamps at all
        #     (VIGIA-REAL-006).
        # An artifact lacking the structured field simply does not enter the
        # rule: absence of an asserted event time is missing data, never a
        # causality signal.
        network_artifacts = [
            a for a in self._artifacts if a.metadata.get("network_log_time")
        ]
        process_artifacts = [
            a for a in self._artifacts
            if a.evidence_type == "memory_process"
            and a.metadata.get("process_creation_time")
        ]

        def _range_guard_tcv(dt: "datetime", ts_str: str, artifact_tool: str,
                             field: str) -> "datetime | None":
            """
            R3-1 (docs/REDTEAM_ROUND3_EMERGENT.md): guard de RANGO ABSOLUTO.

            _parse_ts_tcv aceptaba cualquier fecha ISO sintacticamente valida.
            La regla TCV compara net_time < proc_time sin cota, asi que un
            timestamp fuera de rango — sobre todo 1970-01-01 (el sentinela
            universal de "fecha no parseada"/epoch-0, y su primo Windows
            FILETIME 1601) o un futuro absurdo (2099) — fabricaba un
            TEMPORAL_CAUSALITY_VIOLATION severity=1.0 y volteaba el veredicto.

            Una fecha fuera de _TCV_PLAUSIBLE_MIN.._TCV_PLAUSIBLE_MAX se lee
            como DATO AUSENTE (return None): un endpoint implausible no es
            evidencia de plantado, es un defecto de calidad de dato. Los
            limites son FIJOS (no now()) para preservar la reproducibilidad
            bit-a-bit Daubert del pipeline; ver constantes del modulo.
            """
            cmp_dt = dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
            if not (_TCV_PLAUSIBLE_MIN <= cmp_dt < _TCV_PLAUSIBLE_MAX):
                audit_logger.log_info(
                    event_type="TCV_TIMESTAMP_OUT_OF_RANGE",
                    tool="CrossArtifactIncongruenceEngine",
                    message=(
                        f"TCV rule: {field}={ts_str!r} from {artifact_tool!r} "
                        f"is outside the plausible forensic window "
                        f"[{_TCV_PLAUSIBLE_MIN.date()}, {_TCV_PLAUSIBLE_MAX.date()}). "
                        "Treated as MISSING, not as a temporal-causality signal "
                        "(epoch/overflow sentinels must not fabricate MALICE). "
                        "R3-1."
                    ),
                )
                return None
            return cmp_dt

        # P1 (evidence integrity): dedup set for genuinely-unparseable event
        # timestamps recorded as skipped TCV comparisons. Scoped per
        # detect_fractures() call. Out-of-range values are deliberately NOT
        # recorded here — R3-1 treats an implausible endpoint as missing data
        # (inert), never a signal, to avoid fabricating a false fracture.
        _tcv_skip_seen: set = set()

        def _parse_ts_tcv(ts_str: object, artifact_tool: str, field: str) -> "datetime | None":
            """
            Robust ISO 8601 timestamp parser for TCV rule.

            Handles:
            - 'Z' suffix (UTC) → '+00:00'
            - Naive timestamps (no offset) → assumes UTC, logs assumption
            - None or empty string → returns None, logs missing field
            - Unparseable formats → returns None, logs format error
            - Out-of-range dates → returns None, logs (R3-1 range guard)

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
                return _range_guard_tcv(
                    datetime.fromisoformat(normalized), ts_str, artifact_tool, field
                )
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
                return _range_guard_tcv(dt, ts_str, artifact_tool, field)
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
            # P1: a *present but unparseable* required event time means a
            # decision-relevant temporal comparison could not run. Record it once
            # so the result cannot read as clean/no-fracture without disclosing
            # the gap (the omission was previously only in the HMAC audit log).
            _sk = (artifact_tool, field, str(ts_str))
            if _sk not in _tcv_skip_seen:
                _tcv_skip_seen.add(_sk)
                self._temporal_pairs_skipped.append({
                    "source_tool": artifact_tool,
                    "field":       field,
                    "value":       ts_str if isinstance(ts_str, str) else repr(ts_str),
                    "reason":      "unparseable",
                    "rule":        "TEMPORAL_CAUSALITY_VIOLATION",
                })
            return None

        for net in network_artifacts:
            net_time_str = net.metadata.get("network_log_time")
            net_time = _parse_ts_tcv(net_time_str, net.source_tool, "network_log_time")
            if net_time is None:
                continue

            for proc in process_artifacts:
                proc_time_str = proc.metadata.get("process_creation_time")
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
        # S-3 (docs/PATTERN_HUNT_20260718.md, 2026-07-18): parse mft_entry_number
        # SAFELY. `int(a.metadata.get("mft_entry_number", 0))` had two silent
        # failure modes: (a) a missing number defaulted to entry 0, so two such
        # artifacts collapsed to 0 and `curr > prev` was never true — the
        # MFT_ENTRY_ANOMALY (sev 0.90) could not fire, silently; (b) a present-
        # but-unparseable value ("abc") raised ValueError with no local guard,
        # toppling the whole detect_fractures() into the scorer's json_fallback
        # (one bad field degrading the entire mode). Mirror the TCV doctrine: an
        # entry number that is missing or unparseable is decision-relevant
        # MISSING DATA, never entry "0" — exclude the artifact from the
        # monotonicity check and record the skip (surfaced via
        # temporal_pairs_skipped → ABSTAIN gate), never fabricate an ordering.
        _mft_valid: list = []
        for a in mft_artifacts:
            raw_entry = a.metadata.get("mft_entry_number")
            try:
                _mft_valid.append((int(raw_entry), a))
            except (TypeError, ValueError):
                self._temporal_pairs_skipped.append({
                    "source_tool": a.source_tool,
                    "field": "mft_entry_number",
                    "value": repr(raw_entry)[:64],
                    "reason": "missing" if raw_entry is None else "unparseable",
                    "rule": "MFT_ENTRY_ANOMALY",
                })
        if len(_mft_valid) >= 2:
            mft_sorted = sorted(_mft_valid, key=lambda t: t[0])
            for i in range(1, len(mft_sorted)):
                prev_entry, prev = mft_sorted[i - 1]
                curr_entry, curr = mft_sorted[i]
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
                        # B-105: severity must be float (dataclass contract) —
                        # the Decimal from _dround leaked into the sealed
                        # results and crashed serialization the moment this
                        # fracture fired (time-gated by trust decay, so the
                        # crash appeared only once the case evidence aged past
                        # the raw_score threshold: a wall-clock time bomb).
                        severity=0.85,
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

        # ===================================================================
        # CANONICAL TTP DETECTORS (2026-07-12, docs/CASE_RECOVERY_20260712.md)
        # Structured-metadata detectors for three canonical anti-forensic /
        # masquerade IoIs that the engine previously produced no fracture for
        # (all real cases with genuine multi-domain evidence stalled at
        # composite 0.30, just under MALICE — the dossier's "fracture-detector
        # coverage is the sole malicious-side bottleneck" finding). Each keys
        # ONLY on structured metadata fields (never free text, never
        # annotation fields), and each maps to a named MITRE TTP that any DFIR
        # engine should detect independent of this corpus. All three verified
        # FP-safe corpus-wide (fire only on genuine targets, break zero
        # currently-correct verdicts).
        # ===================================================================

        # Rule 12: PROCESS_MASQUERADE
        # A process whose basename matches a legitimate system binary but whose
        # directory differs — the canonical masquerade IoI (svchost from
        # C:\Users\Temp, systemd-logind from /var/tmp). Peirce Thirdness:
        # borrowing a trusted name to suppress analyst scrutiny.
        for a in self._artifacts:
            mal_path = a.metadata.get("malicious_path")
            leg_path = a.metadata.get("legitimate_path")
            if not (mal_path and leg_path):
                continue
            mal_path, leg_path = str(mal_path), str(leg_path)
            if (os.path.basename(mal_path) == os.path.basename(leg_path)
                    and os.path.dirname(mal_path) != os.path.dirname(leg_path)):
                self._fractures.append(Fracture(
                    artifact_a=f"Process at anomalous path: {mal_path}",
                    artifact_b=f"Legitimate system path: {leg_path}",
                    fracture_type="PROCESS_MASQUERADE",
                    severity=0.85,
                    interpretation=(
                        f"PROCESS MASQUERADE: a process named "
                        f"'{os.path.basename(mal_path)}' executes from {os.path.dirname(mal_path)} "
                        f"but the legitimate binary lives in {os.path.dirname(leg_path)}. "
                        "A system-process name in a non-system path is a structural "
                        "impossibility for a genuine OS binary, not a misconfiguration. "
                        "Peirce Thirdness: the HABIT is to borrow a trusted name to "
                        "suppress analyst scrutiny. MITRE T1036.005 — Masquerading: "
                        "Match Legitimate Name or Location."
                    ),
                    spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1036.005",
                ))

        # Rule 13: DEFENSE_EVASION_ARTIFACT
        # Volume Shadow Copy deletion (vssadmin delete shadows — the
        # pathognomonic ransomware precursor) or host firewall disabled. Both
        # are deliberate, privilege-requiring anti-forensic / anti-recovery
        # acts with no benign automated equivalent.
        for a in self._artifacts:
            deleted_vsc = a.metadata.get("deleted_vsc") is True
            fw_off = str(a.metadata.get("firewall_state", "")).strip().lower() == "off"
            if not (deleted_vsc or fw_off):
                continue
            _acts = []
            if deleted_vsc:
                _acts.append("Volume Shadow Copies deleted (vssadmin delete shadows)")
            if fw_off:
                _acts.append("host firewall disabled")
            self._fractures.append(Fracture(
                artifact_a=f"Defense-evasion action: {'; '.join(_acts)}",
                artifact_b="Baseline: system recovery and perimeter controls intact",
                fracture_type="DEFENSE_EVASION_ARTIFACT",
                severity=0.85,
                interpretation=(
                    "DEFENSE EVASION: " + "; ".join(_acts) + ". Shadow-copy deletion "
                    "destroys the primary recovery path (the pathognomonic ransomware "
                    "precursor) and firewall disable removes perimeter controls — both "
                    "are deliberate, privilege-requiring acts with no benign automated "
                    "equivalent. Peirce Thirdness: the HABIT is to remove recovery and "
                    "detection before acting. MITRE T1490 — Inhibit System Recovery / "
                    "T1562.004 — Disable or Modify System Firewall."
                ),
                spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                ttp_id="T1490",
            ))

        # Rule 14: PROCESS_INJECTION_ANTIFORENSIC
        # Process hollowing / injection or a deliberately hidden PID — a
        # process executing code that is not its on-disk image, or absent from
        # the userland process list. Requires active manipulation of a running
        # process; no benign generator.
        _INJECTION_TECHNIQUES = frozenset({
            "process_hollowing", "process_injection", "reflective_dll",
            "thread_hijacking", "process_doppelganging",
        })
        for a in self._artifacts:
            technique = str(a.metadata.get("injection_technique", "")).strip().lower()
            pid_hidden = a.metadata.get("pid_hidden") is True
            if technique not in _INJECTION_TECHNIQUES and not pid_hidden:
                continue
            _detail = (f"injection technique '{technique}'" if technique in _INJECTION_TECHNIQUES
                       else "process hidden from the userland process list")
            self._fractures.append(Fracture(
                artifact_a=f"Process manipulation: {_detail}",
                artifact_b="Baseline: process executes its on-disk image and is listed",
                fracture_type="PROCESS_INJECTION_ANTIFORENSIC",
                severity=0.85,
                interpretation=(
                    f"PROCESS INJECTION / HIDING: {_detail}. The process executes code "
                    "that is not its legitimate on-disk image, or has been unlinked from "
                    "the process list — active, privilege-requiring manipulation of a "
                    "running process with no benign generator. Peirce Secondness: the "
                    "in-memory reality contradicts the on-disk identity. MITRE T1055.012 "
                    "— Process Hollowing / T1055 — Process Injection."
                ),
                spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                ttp_id="T1055.012",
            ))

        # Rule 15: CLAIM_VS_RECORD_FABRICATION
        # A subject asserts a corroborating fact (claimed_*==True) that the
        # executed record check refutes (a matching *_found==False in the same
        # artifact). The claim was fabricated to survive scrutiny; the record
        # is ground truth. General deception pattern (e.g. "I already spoke
        # with the manager" — communication_found=False over a 48h window).
        for a in self._artifacts:
            md = a.metadata if isinstance(a.metadata, dict) else {}
            claims = [k for k in md if k.startswith("claimed_") and md.get(k) is True]
            refuted = [k for k in md if k.endswith("_found") and md.get(k) is False]
            if claims and refuted:
                self._fractures.append(Fracture(
                    artifact_a=f"Asserted corroboration: {', '.join(sorted(claims))}",
                    artifact_b=f"Executed record check refutes it: {', '.join(sorted(refuted))}",
                    fracture_type="CLAIM_VS_RECORD_FABRICATION",
                    severity=0.85,
                    interpretation=(
                        "FABRICATED CORROBORATION: the subject asserts a corroborating "
                        "fact that the executed record check does not support "
                        f"({', '.join(sorted(claims))} vs {', '.join(sorted(refuted))}). "
                        "The record is ground truth; the claim was manufactured to "
                        "survive scrutiny. Peirce Secondness: the assertion collides "
                        "with the observable record. MITRE T1565.001 — Data "
                        "Manipulation: Stored Data."
                    ),
                    spoofability_delta=_dround(0.85 - 0.15, _DETERMINISTIC_INTERNAL_PREC),
                    ttp_id="T1565.001",
                ))

        # Rule 4 extension: DOCUMENT_FORGERY via mass date-regex substitution.
        # A corpus of documents whose dates were rewritten by regex/script
        # (modification_pattern=='date_regex_substitution') is fabricated
        # evidence — the same DOCUMENT_FORGERY theory as digital-perfection,
        # reached through a different structured marker (kept as the existing
        # type, not a new one, to avoid catalogue duplication).
        for a in self._artifacts:
            md = a.metadata if isinstance(a.metadata, dict) else {}
            if str(md.get("modification_pattern", "")) == "date_regex_substitution":
                self._fractures.append(Fracture(
                    artifact_a=f"Document set: {a.description[:50]}",
                    artifact_b="Expected: authored documents with organic timestamps",
                    fracture_type="DOCUMENT_FORGERY",
                    severity=0.9,
                    interpretation=(
                        "MASS DOCUMENT FORGERY: document dates were rewritten by "
                        "regex/script substitution (not authored) — a manufactured "
                        "evidentiary corpus. Peirce Thirdness: the HABIT is to "
                        "fabricate a paper trail on demand. MITRE T1564.002."
                    ),
                    spoofability_delta=0.60,
                    ttp_id="T1564.002",
                ))

        # Rule 16: LOG_TAMPERING_DETECTED
        # An append-only log was manually edited (VIM/nano/sed signature in
        # slack space, or inode mtime after last chronological entry) AND/OR
        # events confirmed by an independent source (netflow, auditd, EDR)
        # are absent from the log. Either condition alone is sufficient:
        # editing an append-only log IS tampering; a contradiction between
        # the log and an independent record IS evidence suppression.
        # spoofability=0.10 — the metadata fields reflect filesystem facts
        # (inode timestamps, slack space tool signatures) that require
        # physical access or root to fabricate.
        for a in self._artifacts:
            md = a.metadata if isinstance(a.metadata, dict) else {}
            log_edited = md.get("log_edited_with_tool") is not None
            inode_gap = md.get("inode_mtime_after_last_entry") is True
            entries_missing = md.get("entries_missing_from_independent_source") is True
            if not (log_edited or inode_gap or entries_missing):
                continue
            _details = []
            if log_edited:
                _details.append(f"log edited with {md['log_edited_with_tool']}")
            if inode_gap:
                gap = md.get("mtime_gap_seconds", "unknown")
                _details.append(f"inode mtime {gap}s after last log entry")
            if entries_missing:
                src = md.get("independent_source_type", "independent source")
                _details.append(f"events from {src} absent in log")
            self._fractures.append(Fracture(
                artifact_a=f"Log tampering: {'; '.join(_details)}",
                artifact_b="Baseline: append-only log with entries matching all independent sources",
                fracture_type="LOG_TAMPERING_DETECTED",
                severity=0.90,
                interpretation=(
                    "LOG TAMPERING: " + "; ".join(_details) + ". "
                    "System logs are append-only by design (syslog/rsyslog write, "
                    "never edit). Manual editing (tool signature in slack space or "
                    "inode mtime gap) or entries absent from the log but confirmed "
                    "by an independent source (netflow, auditd) are structurally "
                    "impossible without deliberate evidence suppression. "
                    "Peirce Thirdness: the HABIT is to erase traces of presence. "
                    "MITRE T1070.002 — Indicator Removal: Clear Linux or Mac System Logs."
                ),
                spoofability_delta=_dround(0.70 - 0.10, _DETERMINISTIC_INTERNAL_PREC),
                ttp_id="T1070.002",
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
            key = (a.source_tool.strip().casefold(), a.evidence_type.strip().casefold())
            grouped[key].append((a.adjusted_score, a.raw_score))

        # Within-group fusion (dependent evidence): 1 - ∏(1 - s)
        # NIGHTFALL P1: multiplicaciones acumulativas con decimal.Decimal.
        # _dround() no era suficiente: la FPU nativa ejecuta prod_val * (1.0-s)
        # antes del redondeo, y ese producto intermedio puede diferir en el
        # bit 52 de la mantisa entre x86 y ARM. Con Decimal(str(x)) la
        # multiplicacion es puramente software, determinista en toda arquitectura.
        #
        # group_is_material tracks, per group, the MAX raw_score (pre-
        # spoofability) any member artifact asserted -- see
        # _SOURCE_MATERIALITY_FLOOR below for why this must be raw_score and
        # not the fused/adjusted group_score.
        group_scores = []
        group_is_material = []
        _materiality_floor = decimal.Decimal(_SOURCE_MATERIALITY_FLOOR)
        for members in grouped.values():
            prod_d = _D_ONE
            max_raw_d = _D_ZERO
            for adjusted, raw in members:
                # Decimal(str(x)): conversion via string evita imprecision
                # de la conversion directa float->Decimal
                s_d = decimal.Decimal(str(_dround(adjusted, _DETERMINISTIC_INTERNAL_PREC)))
                prod_d = prod_d * (_D_ONE - s_d)
                raw_d = decimal.Decimal(str(_dround(raw, _DETERMINISTIC_INTERNAL_PREC)))
                if raw_d > max_raw_d:
                    max_raw_d = raw_d
            group_score = _dround(_D_ONE - prod_d, _DETERMINISTIC_INTERNAL_PREC)
            group_scores.append(group_score)
            group_is_material.append(max_raw_d >= _materiality_floor)

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
        #
        # source_groups_total: raw count of distinct (source_tool,
        # evidence_type) groups -- purely mechanical, says nothing about how
        # much each group actually contributed.
        # independent_sources: only groups where SOME member artifact's own
        # raw_score cleared _SOURCE_MATERIALITY_FLOOR (group_is_material,
        # computed above). This is what gates confidence_penalty (see the
        # constant's docstring for why the raw count was gameable) and it is
        # the number exposed under the "independent_sources" key -- callers
        # relying on that name for the corroboration count get the fixed
        # semantics automatically.
        source_groups_total = len(group_scores)
        independent_sources = sum(1 for m in group_is_material if m)
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
            "LOG_TAMPERING_DETECTED",
        })

        has_golden_rule = any(f.fracture_type in _GOLDEN_RULE_TYPES for f in filtered_fractures)
        has_structural_malice = any(f.fracture_type in _STRUCTURAL_MALICE_TYPES for f in filtered_fractures)

        # HUMAN-FACING PRESENTATION ORDER (attack-against-the-auditor fix):
        # filtered_fractures previously stayed in raw rule-execution order
        # (Rule 1, Rule 2, ... Rule 8) — an artifact of which detect_fractures()
        # check happens to run first, not of forensic importance. The verdict
        # itself was always computed correctly (has_golden_rule/
        # has_structural_malice scan the WHOLE list), but the narrative below
        # picked filtered_fractures[0] as "the Key finding" and golden_rules[0]
        # as "the Golden Rule" -- whichever fired first, not whichever mattered
        # most. Confirmed empirically: a VERDICT_CONFLICT (severity 0.5, "requires
        # deeper analysis... to resolve") that happens to fire before a
        # TEMPORAL_CAUSALITY_VIOLATION (severity 1.0 -- MAXIMUM, "proving the
        # evidence was planted retroactively") produced a Thirdness narrative
        # that LEADS with the uncertain-sounding low-severity finding and tacks
        # the maximum-severity structural proof on as an afterthought clause at
        # the end -- primacy bias against the human reader, on a case the
        # machine verdict (correctly) already called MALICE.
        #
        # Priority is Golden Rule > structural malice > everything else (the
        # code's own stated epistemology just above: a causal impossibility is
        # "a different epistemic category entirely", not just a high number),
        # severity descending within each tier. Pure severity-sort alone is not
        # equivalent: CRYPTOGRAPHIC_INCONSISTENCY (Golden Rule) can be severity
        # 0.9, below a LOG_VS_MEMORY structural-malice fracture at 0.95, so a
        # plain sort would still rank the Golden Rule second — hence the
        # explicit tier first, severity only as the tiebreak within a tier.
        # Stable sort (Python's sorted()) keeps this deterministic: ties within
        # a tier+severity fall back to original detection order, never random.
        def _fracture_narrative_priority(f: "Fracture") -> tuple[int, float]:
            if f.fracture_type in _GOLDEN_RULE_TYPES:
                tier = 0
            elif f.fracture_type in _STRUCTURAL_MALICE_TYPES:
                tier = 1
            else:
                tier = 2
            return (tier, -float(f.severity))

        fractures_by_priority = sorted(filtered_fractures, key=_fracture_narrative_priority)

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
            #
            # KNOWN GAP (investigated, only partially fixed here -- see
            # docs/CDL_COVERAGE_RATIO_GAP.md for the full writeup): this is
            # the same "count distinct labels, not weight/membership" defect
            # class as the independent_sources bug fixed earlier in this
            # branch, in a sibling mechanism. Two confirmed problems:
            #
            # 1. UNBOUNDED RATIO (fixed below): observed_layers counts every
            #    DISTINCT label seen, with no bound and no membership check
            #    against total_expected_layers. len(observed_layers) can
            #    exceed 6, so coverage_ratio could exceed 1.0 (verified:
            #    10 distinct evidence_type values -> coverage_ratio=1.667,
            #    167% -- nonsensical for a value CollapseDecisionLayer.explain()
            #    formats as a percentage). Capped at 1.0 below.
            #
            # 2. NOT ACTUALLY MEMBERSHIP-TESTED (NOT fixed here -- needs a
            #    real evidence_type -> layer taxonomy, which is a separate,
            #    larger task requiring domain judgment this fix should not
            #    rush): `a.metadata.get("layer", a.evidence_type)` is meant
            #    to let a producer explicitly declare one of the 6 canonical
            #    layers via metadata["layer"], falling back to evidence_type.
            #    Verified: metadata["layer"] is never set anywhere in this
            #    codebase (grep found zero producers), and NONE of the 70+
            #    _VALID_EVIDENCE_TYPES strings are members of
            #    total_expected_layers (zero-element intersection). So in
            #    100% of current real usage, coverage_ratio measures "how
            #    many distinct evidence_type labels were used, capped at
            #    6/6" -- not genuine memory/process/auth/filesystem/network/
            #    kernel domain coverage. The CollapseVerdict.INCONCLUSIVE
            #    gate at coverage_ratio < 0.3 (collapse_decision.py) is
            #    trivially cleared by just 2 distinct evidence_type labels
            #    (2/6 = 0.333), regardless of whether they represent
            #    genuinely diverse forensic domains -- e.g. memory_process +
            #    kernel_structure are both memory/kernel-adjacent yet count
            #    as 2 full "layers". A real fix requires an explicit,
            #    reviewed evidence_type -> {memory, process, auth,
            #    filesystem, network, kernel, other} mapping (most of the 70+
            #    types, e.g. chat_message/social_media/osint/document_visual,
            #    do not fit this 6-layer host-forensics taxonomy at all) and
            #    must be validated against the full canonical case corpus
            #    before landing, the same way the independent_sources fix
            #    above was -- a naive mapping risks silently downgrading real
            #    verdicts to INCONCLUSIVE for the wrong reason, which is a
            #    worse failure than the current (over-lenient) gate.
            total_expected_layers = ["memory", "process", "auth", "filesystem", "network", "kernel"]
            observed_layers = set()
            for a in self._artifacts:
                layer = a.metadata.get("layer", a.evidence_type)
                observed_layers.add(layer)
            coverage_ratio = (
                min(len(observed_layers), len(total_expected_layers)) / len(total_expected_layers)
                if total_expected_layers else 0.5
            )

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

        # Golden Rules summary for Peirce Thirdness. Sourced from
        # fractures_by_priority (not filtered_fractures): golden_rules[0] must
        # be the highest-priority Golden Rule, not merely the first one the
        # rule engine happened to detect.
        golden_rules = [f for f in fractures_by_priority
                        if f.fracture_type in _GOLDEN_RULE_TYPES]

        peirce_chain = {
            # COGNITIVE FLOOD FIX: the raw artifact/tool count alone invites a
            # "broad corroboration" impression that does not distinguish 3
            # solid findings from 3 solid findings plus 30 near-worthless
            # ones -- Noisy-OR fusion barely reacts to the padding
            # (spoofability weighting keeps its score contribution small),
            # but "N artifacts from M tools" reads the same either way to a
            # human skimming it. Naming how many of those tools materially
            # cleared _SOURCE_MATERIALITY_FLOOR alongside the raw count lets
            # the reader tell "broad AND substantive" apart from "wide but
            # thin" at a glance, without hiding the raw number.
            "firstness": (
                f"{len(self._artifacts)} artifacts from "
                f"{len(set(a.source_tool for a in self._artifacts))} tools "
                f"({independent_sources} materially independent of "
                f"{source_groups_total} distinct source/type groups). "
                f"Raw scores range: {_dround(min(a.raw_score for a in self._artifacts), 2):.2f} "
                f"to {_dround(max(a.raw_score for a in self._artifacts), 2):.2f}."
            ),
            "secondness": (
                f"Noisy-OR fusion: {source_groups_total} group(s) fused "
                f"({independent_sources} materially independent), "
                f"composite={_dround(composite, 4):.4f}. "
                f"Most reliable: {top_adjusted[0]['tool']} "
                f"({top_adjusted[0]['type']}, adj={top_adjusted[0]['adjusted']}). "
                f"{len(filtered_fractures)} unique fracture(s), "
                f"{len(golden_rules)} Golden Rule(s)."
            ),
            "thirdness": (
                f"Inferred habit: {'fabrication/staging' if verdict != 'NOISE' else 'normal operation'}. "
                + (
                    f"Key: {fractures_by_priority[0].fracture_type} "
                    f"(severity={_dround(fractures_by_priority[0].severity, 2)}) — "
                    f"{fractures_by_priority[0].interpretation[:200]}"
                    if fractures_by_priority else "No structural discrepancies."
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
            "source_groups_total": source_groups_total,
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
                # Golden Rule > structural malice > everything else, severity
                # descending within a tier (see fractures_by_priority above) --
                # a human or downstream tool reading this list top-to-bottom
                # sees the most forensically significant finding first, not
                # whichever rule the engine happened to check first.
                for f in fractures_by_priority
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

        # P1 (evidence integrity): a required TCV event timestamp that was present
        # but unparseable/out-of-range omits the pair from the temporal-causality
        # rule. That omission previously lived only in the HMAC audit log, so a
        # returned result could read as clean/no-fracture with no signal that a
        # decision-relevant comparison was skipped (confirmed: it flipped a sealed
        # verdict SUSPICION -> NOISE). Surface it inside the signed result.
        result["temporal_pairs_skipped"] = list(self._temporal_pairs_skipped)
        result["temporal_pairs_skipped_count"] = len(self._temporal_pairs_skipped)

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
        self._seen_content_signatures = set()


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
    if result1["composite_score"] != result2["composite_score"]:
        raise RuntimeError(
            f"Determinism failed: {result1['composite_score']} != {result2['composite_score']}"
        )

    # Verify all fracture severities are deterministic
    for i, (f1, f2) in enumerate(zip(result1.get("fractures", []), result2.get("fractures", []))):
        if f1["severity"] != f2["severity"]:
            raise RuntimeError(
                f"Fracture {i} severity non-deterministic: {f1['severity']} != {f2['severity']}"
            )

    # Verify TTP confidences are deterministic
    for ttp in result1.get("ttp_confidences", {}):
        if result1["ttp_confidences"][ttp] != result2["ttp_confidences"][ttp]:
            raise RuntimeError(
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
