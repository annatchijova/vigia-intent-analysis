"""
vigia/core/forensic_adapter.py
Adapter central: SignalOutput → CAIE + AbductiveReasonerV2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from fractions import Fraction
import hashlib
import json

try:
    from vigia.core.ebs_v1 import SignalOutput
except ImportError:
    @dataclass
    class SignalOutput:
        tool_name: str = ""
        value: str = ""
        z_score: float = 0.0
        confidence: float = 0.0
        metadata: Dict[str, Any] = field(default_factory=dict)

try:
    from vigia.tools.caie import Artifact as CAIEArtifact
except ImportError:
    @dataclass
    class CAIEArtifact:
        source_tool: str = ""
        evidence_type: str = ""
        raw_score: float = 0.0
        description: str = ""
        metadata: Dict[str, Any] = field(default_factory=dict)
        provenance_chain: List[str] = field(default_factory=list)
        base_trust: float = 1.0

try:
    from vigia.inference.abductive_reasoner_v2 import (
        ArtifactRecord, EvidenceLayer, OntologicalLevel, CausalLink,
        LAYER_EPISTEMIC_WEIGHT
    )
except ImportError:
    from enum import Enum, auto
    class EvidenceLayer(Enum):
        MEMORY = auto(); NETWORK = auto(); REGISTRY = auto(); DISK_MFT = auto()
    class OntologicalLevel(Enum):
        TECHNIQUE = 0; TACTIC = 1; OBJECTIVE = 2
    @dataclass(frozen=True)
    class ArtifactRecord:
        artifact_id: str = ""; source_path: str = ""; sha256_hash: str = ""
        acquisition_timestamp_utc: str = ""; byte_size: int = 0
        layer: EvidenceLayer = EvidenceLayer.DISK_MFT
        ontology_level: OntologicalLevel = OntologicalLevel.TECHNIQUE
        observed: bool = True
    @dataclass
    class CausalLink:
        link_id: str = ""; description: str = ""; weight: Fraction = Fraction(1,2)
        evidence_present: bool = True; consistent_with_hypothesis: bool = True
        is_broken: bool = False
    LAYER_EPISTEMIC_WEIGHT = {
        EvidenceLayer.MEMORY: Fraction(9,10),
        EvidenceLayer.NETWORK: Fraction(8,10),
        EvidenceLayer.REGISTRY: Fraction(6,10),
        EvidenceLayer.DISK_MFT: Fraction(4,10),
    }


@dataclass
class ForensicContext:
    signals: List[SignalOutput] = field(default_factory=list)
    caie_artifacts: List[CAIEArtifact] = field(default_factory=list)
    abductive_records: List[ArtifactRecord] = field(default_factory=list)
    causal_links: List[CausalLink] = field(default_factory=list)
    raw_results: Dict[str, Any] = field(default_factory=dict)


_LAYER_MAP = {
    "memory": EvidenceLayer.MEMORY, "network": EvidenceLayer.NETWORK,
    "registry": EvidenceLayer.REGISTRY, "mft": EvidenceLayer.DISK_MFT,
    "disk": EvidenceLayer.DISK_MFT, "prefetch": EvidenceLayer.DISK_MFT,
    "usb": EvidenceLayer.REGISTRY, "browser": EvidenceLayer.DISK_MFT,
    "shellbag": EvidenceLayer.REGISTRY, "amcache": EvidenceLayer.DISK_MFT,
    "event_log": EvidenceLayer.REGISTRY, "unknown": EvidenceLayer.DISK_MFT,
    # B-096/B6: el EventLogCorrelator emite artifact_type="windows_event_log"
    # (señal primaria), no "event_log" — sin esta clave caía a DISK_MFT (4/10)
    # en vez de REGISTRY (6/10), sub-ponderando el log de eventos de Windows en
    # la capa abductiva del path on-disk. Tratamiento idéntico a "event_log".
    "windows_event_log": EvidenceLayer.REGISTRY,
    # B-066/B-060: tipos mobile — bases SQLite en disco → DISK_MFT explícito
    # (antes caían al mismo default en silencio; ahora es una decisión).
    "chat_message": EvidenceLayer.DISK_MFT, "sms": EvidenceLayer.DISK_MFT,
    "call_log": EvidenceLayer.DISK_MFT, "web_search": EvidenceLayer.DISK_MFT,
    "app_data": EvidenceLayer.DISK_MFT, "social_media": EvidenceLayer.DISK_MFT,
    "location_data": EvidenceLayer.DISK_MFT, "contact_data": EvidenceLayer.DISK_MFT,
    # Etiquetas agregadas de motor (hasta B-052-P2, señal única por motor)
    "android_forensic": EvidenceLayer.DISK_MFT, "ios_forensic": EvidenceLayer.DISK_MFT,
    "macos_forensic": EvidenceLayer.DISK_MFT, "google_takeout": EvidenceLayer.DISK_MFT,
}

_EVIDENCE_MAP = {
    "memory": "memory_process",
    "network": "ip_geolocation",
    "registry": "registry_key",
    "mft": "file_timestamp",
    "disk": "file_timestamp",
    "prefetch": "prefetch",
    "usb": "registry_key",
    "browser": "log_entry",
    "shellbag": "registry_key",
    "amcache": "registry_key",
    "event_log": "windows_event_log",
    "windows_event_log": "windows_event_log",
    "cultural_marker": "cultural_marker",
    "memory_process": "memory_process",
    "lsass_session": "lsass_session",
    "kernel_structure": "kernel_structure",
    "usn_journal": "usn_journal",
    "hmac_audit_log": "hmac_audit_log",
    "hardware_serial": "hardware_serial",
    "file_hash": "file_hash",
    "dns_record": "dns_record",
    "user_agent": "user_agent",
    "ip_geolocation": "ip_geolocation",
    "timestamp_precision": "timestamp_precision",
    "mft_entry": "mft_entry",
    "usn_journal_gap": "usn_journal_gap",
    "unknown": "log_entry",
    # B-066/B-060: tipos mobile canónicos (identidad — están en
    # EVIDENCE_PROFILES) + etiquetas agregadas de motor mapeadas a app_data
    # (perfil 0.50/0.22, el más cercano al carácter heterogéneo del agregado)
    # hasta que B-052-P2 tipifique por hallazgo.
    "chat_message": "chat_message", "sms": "sms",
    "call_log": "call_log", "web_search": "web_search",
    "app_data": "app_data", "social_media": "social_media",
    "location_data": "location_data", "contact_data": "contact_data",
    "android_forensic": "app_data", "ios_forensic": "app_data",
    "macos_forensic": "app_data", "google_takeout": "app_data",
}

_ONTOLOGY_MAP = {
    "memory": OntologicalLevel.TECHNIQUE, "network": OntologicalLevel.TACTIC,
    "registry": OntologicalLevel.TACTIC, "mft": OntologicalLevel.TECHNIQUE,
    "disk": OntologicalLevel.TECHNIQUE, "prefetch": OntologicalLevel.TECHNIQUE,
    "usb": OntologicalLevel.TECHNIQUE, "browser": OntologicalLevel.TECHNIQUE,
    "shellbag": OntologicalLevel.TECHNIQUE, "amcache": OntologicalLevel.TECHNIQUE,
    "event_log": OntologicalLevel.TECHNIQUE, "unknown": OntologicalLevel.TECHNIQUE,
    # B-096/B6: par de "windows_event_log" en _LAYER_MAP — mismo nivel que event_log.
    "windows_event_log": OntologicalLevel.TECHNIQUE,
    # B-066/B-060: mobile — contenido de comunicación/ubicación es TACTIC
    # (qué hizo el actor); storage genérico de app es TECHNIQUE.
    "chat_message": OntologicalLevel.TACTIC, "sms": OntologicalLevel.TACTIC,
    "call_log": OntologicalLevel.TACTIC, "web_search": OntologicalLevel.TACTIC,
    "social_media": OntologicalLevel.TACTIC, "location_data": OntologicalLevel.TACTIC,
    "app_data": OntologicalLevel.TECHNIQUE, "contact_data": OntologicalLevel.TECHNIQUE,
    "android_forensic": OntologicalLevel.TECHNIQUE, "ios_forensic": OntologicalLevel.TECHNIQUE,
    "macos_forensic": OntologicalLevel.TECHNIQUE, "google_takeout": OntologicalLevel.TECHNIQUE,
}


def check_adapter_map_consistency(
    layer_map: Dict[str, Any] | None = None,
    ontology_map: Dict[str, Any] | None = None,
    evidence_map: Dict[str, Any] | None = None,
) -> list[str]:
    """B-060 guard: verify the three adapter maps stay mutually consistent.

    Every map routes an artifact type with a SILENT default
    (``.get(art_type, DEFAULT)``). A type categorized in one map but missing
    from another falls through to that default with no signal — a mapping no
    maintainer ever decided. This returns a list of violation messages
    (empty == consistent) so it can back both a contract test and, if desired,
    an import-time assertion.

    Contract:
      1. ``_LAYER_MAP`` and ``_ONTOLOGY_MAP`` share the exact same key set —
         both are keyed by the raw art_type category and move in lockstep.
      2. Every ``_LAYER_MAP``/``_ONTOLOGY_MAP`` key is also an ``_EVIDENCE_MAP``
         key — a categorized type always has an explicit evidence mapping,
         never the identity fallback.
      3. ``_EVIDENCE_MAP`` may be a superset; the extra keys are canonical
         evidence types (identity-mapped, ``value == key``) that arrive
         pre-typed and need no layer/ontology categorization.
    """
    layer = layer_map if layer_map is not None else _LAYER_MAP
    ontology = ontology_map if ontology_map is not None else _ONTOLOGY_MAP
    evidence = evidence_map if evidence_map is not None else _EVIDENCE_MAP

    violations: list[str] = []

    only_layer = set(layer) - set(ontology)
    only_ontology = set(ontology) - set(layer)
    for t in sorted(only_layer):
        violations.append(
            f"{t!r} in _LAYER_MAP but not _ONTOLOGY_MAP "
            f"(would silently default ontology to TECHNIQUE)"
        )
    for t in sorted(only_ontology):
        violations.append(
            f"{t!r} in _ONTOLOGY_MAP but not _LAYER_MAP "
            f"(would silently default layer to DISK_MFT)"
        )

    for t in sorted(set(layer) - set(evidence)):
        violations.append(
            f"{t!r} categorized in _LAYER_MAP/_ONTOLOGY_MAP but absent from "
            f"_EVIDENCE_MAP (would silently identity-map the evidence type)"
        )

    for t in sorted(set(evidence) - set(layer)):
        if evidence[t] != t:
            violations.append(
                f"{t!r} in _EVIDENCE_MAP with a non-identity value "
                f"{evidence[t]!r} but missing from _LAYER_MAP/_ONTOLOGY_MAP "
                f"(a raw art_type must be categorized in all three maps)"
            )

    return violations


def _canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)

def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class ForensicAdapter:
    @staticmethod
    def signal_to_caie_artifact(sig: SignalOutput) -> CAIEArtifact:
        # B-063: SignalOutput.metadata tiene default None (ebs_v1.py) — el CLI
        # run_vigia() construye señales sin metadata y el .get() sobre None
        # tiraba TypeError, capturado aguas arriba como "CAIE failed
        # (non-blocking)" → CAIE se salteaba en silencio.
        _meta = sig.metadata or {}
        art_type = str(_meta.get("evidence_type", "unknown")).lower()
        # If art_type is already a canonical CAIE evidence type (e.g. file_timestamp,
        # memory_process) it won't appear as a key in _EVIDENCE_MAP, which maps legacy
        # labels (e.g. "mft" → "file_timestamp").  Fall back to art_type itself so that
        # signals already carrying canonical types pass through unchanged.
        evidence_type = _EVIDENCE_MAP.get(art_type, art_type)
        z = float(getattr(sig, 'z_score', 0.0))
        raw_score = float(sig.value)
        desc = str(_meta.get("description", sig.value or f"Signal from {sig.tool_name}"))[:500]
        meta = dict(_meta)
        meta["z_score_original"] = sig.z_score
        canonical = _canonical_json({"tool": sig.tool_name, "value": sig.value, "z": sig.z_score})
        provenance = [_sha256(canonical)]
        # L-037b FIX (Tanda B, PR-B2): base_trust deja de ser 1.0 fijo — se
        # propaga la confiabilidad que el motor SIFT declara en su metadata
        # (artifact_reliability, serializada como Fraction-string). Un event
        # log fabricable ya no pesa igual que un dump de memoria en CAIE.
        # Defensivo: ausente/no-parseable → 1.0 (comportamiento previo);
        # fuera de rango → clamp [0,1].
        _rel = meta.get("artifact_reliability", "1")
        try:
            base_trust = max(0.0, min(1.0, float(Fraction(str(_rel)))))
        except (ValueError, ZeroDivisionError):
            base_trust = 1.0
        return CAIEArtifact(
            source_tool=sig.tool_name, evidence_type=evidence_type,
            raw_score=raw_score, description=desc, metadata=meta,
            provenance_chain=provenance, base_trust=base_trust,
        )

    @staticmethod
    def signal_to_abductive_record(sig: SignalOutput) -> ArtifactRecord:
        _meta = sig.metadata or {}  # B-063: metadata puede ser None
        art_type = str(_meta.get("artifact_type", "unknown")).lower()
        layer = _LAYER_MAP.get(art_type, EvidenceLayer.DISK_MFT)
        ontology = _ONTOLOGY_MAP.get(art_type, OntologicalLevel.TECHNIQUE)
        artifact_id = f"{sig.tool_name}-{art_type}-{id(sig)}"
        source_path = _meta.get("source_path", _meta.get("path", "unknown"))
        ts = _meta.get("timestamp", "2026-05-15T00:00:00Z")
        canonical = _canonical_json({"tool": sig.tool_name, "value": sig.value, "z": sig.z_score, "meta_keys": sorted(_meta.keys())})
        sha256_hash = _sha256(canonical)
        byte_size = len(canonical.encode("utf-8"))
        return ArtifactRecord(
            artifact_id=artifact_id, source_path=source_path,
            sha256_hash=sha256_hash, acquisition_timestamp_utc=ts,
            byte_size=byte_size, layer=layer, ontology_level=ontology,
            observed=True,
        )

    @staticmethod
    def signal_to_causal_link(sig: SignalOutput, consistent: bool = True) -> CausalLink:
        _meta = sig.metadata or {}  # B-063: metadata puede ser None
        art_type = str(_meta.get("artifact_type", "unknown")).lower()
        layer = _LAYER_MAP.get(art_type, EvidenceLayer.DISK_MFT)
        weight = LAYER_EPISTEMIC_WEIGHT.get(layer, Fraction(5, 10))
        desc = str(_meta.get("description", sig.value or f"{sig.tool_name} signal"))[:200]
        return CausalLink(
            link_id=f"link-{sig.tool_name}-{art_type}", description=desc,
            weight=weight, evidence_present=True,
            consistent_with_hypothesis=consistent, is_broken=False,
        )

    # B-136 phase 3: keys a tool-exposed caie_artifact dict must carry.
    # Matches the shape the four document-forensics tools build (see
    # vision_audit._build_caie_artifacts and siblings).
    _CAIE_ARTIFACT_KEYS = frozenset({
        "source_tool", "evidence_type", "raw_score",
        "description", "metadata", "provenance_chain",
    })

    @classmethod
    def _caie_artifacts_from_raw_results(cls, raw_results: Dict[str, Any]) -> list:
        """B-136 phase 3: absorb the case-ready artifacts the document-
        forensics tools expose in their results under "caie_artifacts".

        Fail-closed: malformed entries are skipped, raw_score is clamped to
        [0,1], and custody metadata is never synthesized — an artifact
        without acquisition metadata self-degrades inside CAIE (B-131 law),
        which is the honest outcome.
        """
        absorbed = []
        for result in (raw_results or {}).values():
            if not isinstance(result, dict):
                continue
            entries = result.get("caie_artifacts")
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict) or not cls._CAIE_ARTIFACT_KEYS <= set(entry):
                    continue
                try:
                    absorbed.append(CAIEArtifact(
                        source_tool=str(entry["source_tool"]),
                        evidence_type=str(entry["evidence_type"]),
                        raw_score=min(1.0, max(0.0, float(entry["raw_score"]))),
                        description=str(entry["description"])[:500],
                        metadata=entry["metadata"] if isinstance(entry["metadata"], dict) else {},
                        provenance_chain=list(entry["provenance_chain"] or []),
                    ))
                except (TypeError, ValueError):
                    continue
        return absorbed

    @classmethod
    def build_context(cls, signals: List[SignalOutput], raw_results: Dict[str, Any] = None) -> ForensicContext:
        caie = [cls.signal_to_caie_artifact(s) for s in signals]
        # B-136 phase 3: tool results may carry case-ready caie_artifacts
        # (linguistic_forensics, batch_forensics, temporal_fraud,
        # document_visual/geometry) — this is the single incorporation
        # point for both assemblers (pipeline and sift orchestrator).
        caie.extend(cls._caie_artifacts_from_raw_results(raw_results or {}))
        abductive = [cls.signal_to_abductive_record(s) for s in signals]
        links = [cls.signal_to_causal_link(s) for s in signals]
        return ForensicContext(
            signals=signals, caie_artifacts=caie,
            abductive_records=abductive, causal_links=links,
            raw_results=raw_results or {},
        )
