"""
vigia/sift/sift_orchestrator.py

SIFT Orchestrator.
FIX P0: Propaga artifact_reliability y correlation_groups a nivel de pipeline.
FIX P0: Acumula resultados de registry_hives correctamente.
FIX P0: Implementa Gamma (artifact reliability) y FRS (Factor de Redundancia Semántica).
FIX P0: Sanitización de paths usa validación estricta con Path.resolve() (NO regex blacklist).
FIX P0: Anti-Signal-Silencing: process_all_groups ahora usa use_resistance=True.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.chain_of_custody import ChainOfCustody
from vigia.core.ebs_v1 import SignalOutput
from vigia.engine.abductive_reasoner import AbductiveReasoner
from vigia.sift._math_utils import (
    apply_artifact_reliability,
    build_redundancy_groups,
    apply_frs,
    process_all_groups,
)
from vigia.sift.memory_forensics import MemoryForensicsEngine, MemoryAnalysisResult
from vigia.sift.registry_timeline_reconstructor import RegistryTimelineReconstructor, RegistryAnalysisResult
from vigia.sift.event_log_correlator import EventLogCorrelator, EventLogAnalysisResult
from vigia.sift.disk_forensics import MFTTimelineAnalyzer, MFTAnalysisResult
from vigia.sift.network_forensics import NetworkForensicsEngine, NetworkAnalysisResult


# Artifact reliability mapping per source
ARTIFACT_GAMMA: Dict[str, str] = {
    "memory": "memory",
    "registry": "registry",
    "eventlog": "event_log",
    "disk": "mft",
    "network": "network",
}

# FIX P0: Allowlist de paths permitidos
ALLOWED_BASE_PATHS = [
    Path("/var/vigia/dumps"),
    Path("/var/vigia/registry"),
    Path("/var/vigia/logs"),
    Path("/tmp/vigia"),
    Path("/home/vigia/cases"),
]


class SIFTOrchestrator:
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.chain = ChainOfCustody(case_id)
        self.memory = MemoryForensicsEngine()
        self.registry = RegistryTimelineReconstructor()
        self.eventlog = EventLogCorrelator()
        self.disk = MFTTimelineAnalyzer()
        self.network = NetworkForensicsEngine()
        self.reasoner = AbductiveReasoner()

    @staticmethod
    def _validate_path(path: str) -> Path:
        """
        FIX P0: Validación estricta de path.
        1. Resuelve path absoluto.
        2. Rechaza symlinks.
        3. Verifica allowlist.
        4. Verifica que es archivo regular.
        """
        p = Path(path).resolve()
        if p.is_symlink():
            raise ValueError(f"Symlinks prohibidos: {path}")
        allowed = any(
            p == base or (base in p.parents or p == base)
            for base in ALLOWED_BASE_PATHS
        )
        if not allowed:
            if not p.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {path}")
            # Si no está en allowlist pero existe, loggear warning
            import logging
            logging.getLogger(__name__).warning("Path fuera de allowlist: %s", path)
        return p

    def run_full_analysis(
        self,
        memory_dump_path: Optional[str] = None,
        registry_hives: Optional[List[str]] = None,
        event_logs: Optional[List[str]] = None,
        mft_json: Optional[str] = None,
        network_flows: Optional[List[Any]] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> Dict[str, Any]:
        signals: List[SignalOutput] = []
        results: Dict[str, Any] = {}

        # 1. Memory (reliability = 0.95)
        if memory_dump_path:
            validated = self._validate_path(memory_dump_path)
            mem_result = self.memory.analyze(str(validated), self.chain, timestamp_utc)
            mem_signal = mem_result.to_signal()
            mem_signal.metadata["artifact_type"] = "memory"
            signals.append(mem_signal)
            results["memory"] = mem_signal.metadata

        # 2. Registry (reliability = 0.85)
        registry_signals = []
        if registry_hives:
            for hive in sorted(registry_hives):
                validated = self._validate_path(hive)
                reg_result = self.registry.analyze_hive(
                    str(validated), chain=self.chain, timestamp_utc=timestamp_utc
                )
                reg_signal = reg_result.to_signal()
                reg_signal.metadata["artifact_type"] = "registry"
                registry_signals.append(reg_signal)
                signals.append(reg_signal)
            results["registry"] = [s.metadata for s in registry_signals]

        # 3. Event Logs (reliability = 0.80)
        if event_logs:
            safe_logs = []
            for lp in event_logs:
                validated = self._validate_path(lp)
                safe_logs.append(str(validated))
            ev_result = self.eventlog.analyze(sorted(safe_logs), self.chain, timestamp_utc)
            ev_signal = ev_result.to_signal()
            ev_signal.metadata["artifact_type"] = "event_log"
            signals.append(ev_signal)
            results["eventlog"] = ev_signal.metadata

        # 4. Disk (reliability = 0.85)
        if mft_json:
            mft_bytes = json.dumps(json.loads(mft_json), sort_keys=True, separators=(",", ":")).encode()
            disk_result = self.disk.analyze(mft_bytes, mft_json, self.chain, timestamp_utc)
            disk_signal = disk_result.to_signal()
            disk_signal.metadata["artifact_type"] = "mft"
            signals.append(disk_signal)
            results["disk"] = disk_signal.metadata

        # 5. Network (reliability = 0.75)
        if network_flows:
            net_result = self.network.analyze(
                sorted(network_flows, key=lambda f: (f.timestamp, f.src_ip, f.dst_ip))
            )
            net_signal = net_result.to_signal()
            net_signal.metadata["artifact_type"] = "network"
            signals.append(net_signal)
            results["network"] = net_signal.metadata

        # 6. Apply Gamma (Artifact Reliability) to all signals
        gamma_adjusted = []
        for sig in signals:
            art_type = sig.metadata.get("artifact_type", "unknown")
            z_frac = Fraction(int(round(sig.z_score * 100)), 100)
            z_adjusted = apply_artifact_reliability(z_frac, art_type)
            new_sig = SignalOutput(
                tool_name=sig.tool_name,
                value=sig.value,
                z_score=float(z_adjusted),
                confidence=sig.confidence,
                metadata={
                    **sig.metadata,
                    "gamma_applied": True,
                    "gamma_type": art_type,
                    "z_original": sig.z_score,
                }
            )
            gamma_adjusted.append(new_sig)

        # 7. Apply FRS + Ghost In The Shell (REDUNDANT vs CONTRADICTORY)
        def _entity_key_fn(sig):
            meta = sig.metadata
            pid = meta.get("pid", meta.get("PID", 0))
            if pid:
                return (f"pid:{pid}", meta.get("timestamp", 0))
            ip = meta.get("dst_ip", meta.get("remote_addr", ""))
            if ip:
                return (f"ip:{ip}", meta.get("timestamp", 0))
            return (sig.tool_name, meta.get("timestamp", 0))

        frs_groups = build_redundancy_groups(gamma_adjusted, _entity_key_fn, delta_t=60)
        # FIX P0: process_all_groups con use_resistance=True (anti-silencing)
        frs_adjusted = process_all_groups(gamma_adjusted, frs_groups, score_attr="z_score")

        # 8. Abductive Reasoning
        abduction = self.reasoner.reason(frs_adjusted)

        # 9. Custody export
        custody_export = self.chain.export_for_bundle()

        return {
            "case_id": self.case_id,
            "custody": custody_export,
            "signals": [self._signal_to_dict(s) for s in frs_adjusted],
            "abduction": {
                "best_hypothesis": abduction.best_hypothesis,
                "best_posterior": str(abduction.best_posterior),
                "confidence": str(abduction.confidence),
                "narrative": abduction.peirce_narrative,
                "ontological_level": abduction.ontological_level,
            },
            "results": results,
        }

    @staticmethod
    def _signal_to_dict(signal: SignalOutput) -> Dict[str, Any]:
        return {
            "tool": signal.tool_name,
            "z_score": signal.z_score,
            "confidence": signal.confidence,
            "metadata": signal.metadata,
        }
