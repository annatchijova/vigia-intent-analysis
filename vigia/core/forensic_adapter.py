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
}

_ONTOLOGY_MAP = {
    "memory": OntologicalLevel.TECHNIQUE, "network": OntologicalLevel.TACTIC,
    "registry": OntologicalLevel.TACTIC, "mft": OntologicalLevel.TECHNIQUE,
    "disk": OntologicalLevel.TECHNIQUE, "prefetch": OntologicalLevel.TECHNIQUE,
    "usb": OntologicalLevel.TECHNIQUE, "browser": OntologicalLevel.TECHNIQUE,
    "shellbag": OntologicalLevel.TECHNIQUE, "amcache": OntologicalLevel.TECHNIQUE,
    "event_log": OntologicalLevel.TECHNIQUE, "unknown": OntologicalLevel.TECHNIQUE,
}


def _canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)

def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class ForensicAdapter:
    @staticmethod
    def signal_to_caie_artifact(sig: SignalOutput) -> CAIEArtifact:
        art_type = str(sig.metadata.get("evidence_type", "unknown")).lower()
        # If art_type is already a canonical CAIE evidence type (e.g. file_timestamp,
        # memory_process) it won't appear as a key in _EVIDENCE_MAP, which maps legacy
        # labels (e.g. "mft" → "file_timestamp").  Fall back to art_type itself so that
        # signals already carrying canonical types pass through unchanged.
        evidence_type = _EVIDENCE_MAP.get(art_type, art_type)
        z = float(getattr(sig, 'z_score', 0.0))
        raw_score = float(sig.value)
        desc = str(sig.metadata.get("description", sig.value or f"Signal from {sig.tool_name}"))[:500]
        meta = dict(sig.metadata) if sig.metadata else {}
        meta["z_score_original"] = sig.z_score
        canonical = _canonical_json({"tool": sig.tool_name, "value": sig.value, "z": sig.z_score})
        provenance = [_sha256(canonical)]
        return CAIEArtifact(
            source_tool=sig.tool_name, evidence_type=evidence_type,
            raw_score=raw_score, description=desc, metadata=meta,
            provenance_chain=provenance, base_trust=1.0,
        )

    @staticmethod
    def signal_to_abductive_record(sig: SignalOutput) -> ArtifactRecord:
        art_type = str(sig.metadata.get("artifact_type", "unknown")).lower()
        layer = _LAYER_MAP.get(art_type, EvidenceLayer.DISK_MFT)
        ontology = _ONTOLOGY_MAP.get(art_type, OntologicalLevel.TECHNIQUE)
        artifact_id = f"{sig.tool_name}-{art_type}-{id(sig)}"
        source_path = sig.metadata.get("source_path", sig.metadata.get("path", "unknown"))
        ts = sig.metadata.get("timestamp", "2026-05-15T00:00:00Z")
        canonical = _canonical_json({"tool": sig.tool_name, "value": sig.value, "z": sig.z_score, "meta_keys": sorted(sig.metadata.keys())})
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
        art_type = str(sig.metadata.get("artifact_type", "unknown")).lower()
        layer = _LAYER_MAP.get(art_type, EvidenceLayer.DISK_MFT)
        weight = LAYER_EPISTEMIC_WEIGHT.get(layer, Fraction(5, 10))
        desc = str(sig.metadata.get("description", sig.value or f"{sig.tool_name} signal"))[:200]
        return CausalLink(
            link_id=f"link-{sig.tool_name}-{art_type}", description=desc,
            weight=weight, evidence_present=True,
            consistent_with_hypothesis=consistent, is_broken=False,
        )

    @classmethod
    def build_context(cls, signals: List[SignalOutput], raw_results: Dict[str, Any] = None) -> ForensicContext:
        caie = [cls.signal_to_caie_artifact(s) for s in signals]
        abductive = [cls.signal_to_abductive_record(s) for s in signals]
        links = [cls.signal_to_causal_link(s) for s in signals]
        return ForensicContext(
            signals=signals, caie_artifacts=caie,
            abductive_records=abductive, causal_links=links,
            raw_results=raw_results or {},
        )
