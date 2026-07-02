"""
vigia/sift/sift_orchestrator.py

SIFT Orchestrator V4 — Integración completa Colectivo VIGÍA.
FIX V4: 14+ motores SIFT, PathGuard TOCTOU, SignalMapper CCS Gate,
        Metabolic/Resonance/Behavioral/Pattern engines, UnifiedTimeline,
        IOC enrichment, Adversarial robustness, Abductive reasoning.

Determinismo: todos los paths se validan antes de tocar disco.
Resiliencia: cada motor en try/except — un stub no rompe el pipeline.
"""

from __future__ import annotations

import json
import asyncio
import logging
import os
from decimal import Decimal, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.chain_of_custody import ChainOfCustody
from vigia.core.ebs_v1 import SignalOutput
from vigia.core.path_guard import PathGuard, SecurityException
from vigia.inference.abductive_reasoner import AbductiveReasoner

# SIFT motores originales
from vigia.sift._math_utils import (
    apply_artifact_reliability,
    apply_artifact_reliability_dynamic,
    build_redundancy_groups,
    process_all_groups,
)
from vigia.sift.memory_forensics import MemoryForensicsEngine, MemoryAnalysisResult
from vigia.sift.registry_timeline_reconstructor import RegistryTimelineReconstructor, RegistryAnalysisResult
from vigia.sift.event_log_correlator import EventLogCorrelator, EventLogAnalysisResult
from vigia.sift.disk_forensics import MFTTimelineAnalyzer, MFTAnalysisResult
from vigia.sift.network_forensics import NetworkForensicsEngine, NetworkAnalysisResult

# SIFT motores nuevos (con fallback si no existen todavía)
try:
    from vigia.sift.prefetch_analyzer import PrefetchAnalyzer, PrefetchAnalysisResult
except ImportError:
    PrefetchAnalyzer = None  # type: ignore
try:
    from vigia.sift.usb_device_tracker import USBDeviceTracker, USBAnalysisResult
except ImportError:
    USBDeviceTracker = None  # type: ignore
try:
    from vigia.sift.browser_forensics import BrowserForensicsEngine, BrowserAnalysisResult
except ImportError:
    BrowserForensicsEngine = None  # type: ignore
try:
    from vigia.sift.shellbag_analyzer import ShellbagAnalyzer, ShellbagAnalysisResult
except ImportError:
    ShellbagAnalyzer = None  # type: ignore
try:
    from vigia.sift.amcache_shimcache import AmcacheShimcacheAnalyzer, AmcacheAnalysisResult
except ImportError:
    AmcacheShimcacheAnalyzer = None  # type: ignore
try:
    from vigia.sift.ioc_manager import IOCManager, IOCMatchResult
except ImportError:
    IOCManager = None  # type: ignore
try:
    from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine, TimelineAnalysisResult
except ImportError:
    UnifiedTimelineEngine = None  # type: ignore

# Core / Engine motores (con fallback)
try:
    from vigia.core.signal_mapper import SignalMapper
except ImportError:
    SignalMapper = None  # type: ignore
try:
    from vigia.inference.metabolic_profiler import MetabolicProfiler, MetabolicAnalysisResult
except ImportError:
    MetabolicProfiler = None  # type: ignore
try:
    from vigia.inference.cross_artifact_resonance import CrossArtifactResonance, ResonanceResult
except ImportError:
    CrossArtifactResonance = None  # type: ignore
try:
    from vigia.inference.behavioral_fingerprint import BehavioralFingerprint, BehavioralFingerprintResult
except ImportError:
    BehavioralFingerprint = None  # type: ignore
try:
    from vigia.inference.case_pattern_library import CasePatternLibrary, CasePatternResult
except ImportError:
    CasePatternLibrary = None  # type: ignore
try:
    from vigia.tools.adversarial_robustness import AdversarialRobustnessEngine
except ImportError:
    AdversarialRobustnessEngine = None  # type: ignore

logger = logging.getLogger(__name__)

# Bases estáticas de la allowlist de PathGuard (rutas de despliegue conocidas).
_STATIC_ALLOWLIST = (
    Path('/var/vigia'),
    Path('/tmp/vigia'),
    Path('/home/vigia/cases'),
    Path.home() / 'vigia-repo' / 'evidence',
    Path.home() / 'vigia-repo' / 'data',
    Path('/mnt'),
)


def _evidence_allowlist(extra_dirs: Optional[List[str]] = None) -> List[Path]:
    """
    Construye la allowlist de PathGuard incluyendo el directorio de evidencia
    configurado por el operador.

    FIX (auditoría FN, P0-B): antes la allowlist era 100% hardcodeada y
    VIGIA_EVIDENCE_DIR — la variable que el CLAUDE.md documenta como el punto
    de entrada de evidencia — NO se consultaba en ningún punto del modo agente.
    Un operador que siguiera la doc y apuntara la evidencia a cualquier ruta
    fuera de las seis bases estáticas obtenía 0 señales (rechazo silencioso de
    PathGuard) → veredicto benigno espurio. Ahora VIGIA_EVIDENCE_DIR y el
    directorio de evidencia efectivo se agregan a la allowlist.

    La seguridad se mantiene: PathGuard sigue rechazando symlinks, TOCTOU y
    path traversal. Solo se amplía la base permitida a directorios que el
    propio operador declaró como fuente de evidencia.
    """
    allowed: List[Path] = list(_STATIC_ALLOWLIST)
    env_dir = os.environ.get("VIGIA_EVIDENCE_DIR", "").strip()
    if env_dir:
        try:
            allowed.append(Path(env_dir).absolute())
        except (OSError, ValueError):
            logger.warning("[PATHGUARD] VIGIA_EVIDENCE_DIR inválido: %r", env_dir)
    for d in (extra_dirs or []):
        if not d:
            continue
        try:
            allowed.append(Path(d).absolute())
        except (OSError, ValueError):
            logger.warning("[PATHGUARD] evidence dir inválido: %r", d)
    return allowed


# Artifact reliability mapping per source
ARTIFACT_GAMMA: Dict[str, str] = {
    "memory": "memory",
    "registry": "registry",
    "eventlog": "event_log",
    "disk": "mft",
    "network": "network",
    "prefetch": "prefetch",
    "usb": "usb",
    "browser": "browser",
    "shellbag": "shellbag",
    "amcache": "amcache",
}


class SIFTOrchestrator:
    """
    Orchestrator unificado del pipeline forense VIGÍA.

    Flujo V4:
    1. PathGuard TOCTOU en todos los inputs
    2. Ejecución paralela por módulo SIFT (con try/except por motor)
    3. Conversión a SignalOutput
    4. SignalMapper CCS Gate (si aplica)
    5. Gamma (Artifact Reliability)
    6. FRS + Ghost In The Shell + Anti-Silencing
    7. Motores Engine: Metabolic, Resonance, Behavioral, Pattern
    8. UnifiedTimelineEngine (cross-source temporal)
    9. IOC enrichment (si hay base de datos)
    10. AdversarialRobustnessEngine
    11. AbductiveReasoner
    12. Custody export
    """

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.chain = ChainOfCustody(case_id)
        # L-037: Examiner-declared acquisition metadata (CLI flags).
        # Keys accepted: acquisition_tool, write_blocker_used, examiner_id.
        # These are merged into every signal at the gamma convergence point
        # so CAIE can evaluate all 4 gates.  Only set when the examiner
        # explicitly provides them — absent fields degrade trust honestly.
        self.acquisition_overrides: Dict[str, Any] = {}
        self.path_guard = PathGuard(allowed_base_paths=_evidence_allowlist())

        # SIFT motores originales
        self.memory = MemoryForensicsEngine()
        self.registry = RegistryTimelineReconstructor()
        self.eventlog = EventLogCorrelator()
        self.disk = MFTTimelineAnalyzer()
        self.network = NetworkForensicsEngine()

        # SIFT motores nuevos (instanciar solo si existen)
        self.prefetch = PrefetchAnalyzer() if PrefetchAnalyzer else None
        self.usb = USBDeviceTracker() if USBDeviceTracker else None
        self.browser = BrowserForensicsEngine() if BrowserForensicsEngine else None
        self.shellbag = ShellbagAnalyzer() if ShellbagAnalyzer else None
        self.amcache = AmcacheShimcacheAnalyzer() if AmcacheShimcacheAnalyzer else None
        self.ioc = IOCManager() if IOCManager else None
        self.timeline_engine = UnifiedTimelineEngine() if UnifiedTimelineEngine else None

        # Core / Engine motores
        self.signal_mapper = SignalMapper() if SignalMapper else None
        self.metabolic = MetabolicProfiler() if MetabolicProfiler else None
        self.resonance = CrossArtifactResonance() if CrossArtifactResonance else None
        self.behavioral = BehavioralFingerprint() if BehavioralFingerprint else None
        self.patterns = CasePatternLibrary() if CasePatternLibrary else None
        self.adv_robust = AdversarialRobustnessEngine() if AdversarialRobustnessEngine else None
        self.reasoner = AbductiveReasoner()

    def _safe_path(self, path_str: Optional[str], for_read: bool = True) -> Optional[Path]:
        """
        FIX V4+P2: PathGuard con TOCTOU completo. Si falla, loggea y retorna None.
        Usa safe_read para lecturas seguras integradas.
        """
        if not path_str:
            return None
        try:
            check = self.path_guard.validate(path_str, for_read=for_read)
            if not check.valid:
                logger.error("PathGuard REJECT %s: %s", path_str, check.reason)
                return None
            return Path(path_str).absolute()
        except SecurityException as e:
            logger.error("SecurityException en %s: %s", path_str, e)
            return None

    def _safe_read(self, path_str: str) -> Optional[bytes]:
        """Lectura segura con TOCTOU completo."""
        try:
            return self.path_guard.safe_read(path_str)
        except (PermissionError, SecurityException) as e:
            logger.error("PathGuard safe_read REJECT %s: %s", path_str, e)
            return None

    def _to_signal_safe(self, result, method_name: str) -> Optional[SignalOutput]:
        """Convierte un resultado a SignalOutput, loggea errores."""
        try:
            if hasattr(result, "to_signal"):
                return result.to_signal()
            return None
        except Exception as e:
            logger.error("Error en to_signal de %s: %s", method_name, e)
            return None

    def run_full_analysis(
        self,
        memory_dump_path: Optional[str] = None,
        registry_hives: Optional[List[str]] = None,
        event_logs: Optional[List[str]] = None,
        mft_json: Optional[str] = None,
        network_flows: Optional[List[Any]] = None,
        prefetch_dir: Optional[str] = None,
        usb_hive_path: Optional[str] = None,
        browser_profile: Optional[str] = None,
        shellbag_hive: Optional[str] = None,
        amcache_path: Optional[str] = None,
        system_hive_path: Optional[str] = None,
        ioc_db_path: Optional[str] = None,
        event_stream: Optional[List[Dict[str, Any]]] = None,
        normal_events: Optional[List[Dict[str, Any]]] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> Dict[str, Any]:
        """
        Pipeline completo V4.

        Args nuevos:
            prefetch_dir: Directorio con archivos .pf
            usb_hive_path: Hive de registry con USBSTOR
            browser_profile: Ruta a perfil Chrome/Edge/Firefox
            shellbag_hive: NTUSER.DAT para shellbags
            amcache_path: Amcache.hve
            system_hive_path: SYSTEM hive para ShimCache
            ioc_db_path: Base de datos JSON de IOCs
            event_stream: Lista de eventos para MetabolicProfiler
            normal_events: Baseline para BehavioralFingerprint
        """
        raw_signals: List[SignalOutput] = []
        results: Dict[str, Any] = {}

        # ============================================================
        # 1. SIFT ORIGINALES (5 mundos)
        # ============================================================

        # 1.1 Memory
        if memory_dump_path:
            v = self._safe_path(memory_dump_path)
            if v:
                try:
                    mem_result = self.memory.analyze(str(v), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(mem_result, "memory")
                    if sig:
                        sig.metadata["artifact_type"] = "memory"
                        raw_signals.append(sig)
                        results["memory"] = sig.metadata
                except Exception as e:
                    logger.error("MemoryForensicsEngine falló: %s", e)
                    results["memory"] = {"error": str(e)}

        # 1.2 Registry
        if registry_hives:
            registry_signals = []
            for hive in sorted(registry_hives):
                v = self._safe_path(hive)
                if not v:
                    continue
                try:
                    reg_result = self.registry.analyze_hive(
                        str(v), chain=self.chain, timestamp_utc=timestamp_utc
                    )
                    sig = self._to_signal_safe(reg_result, "registry")
                    if sig:
                        sig.metadata["artifact_type"] = "registry"
                        registry_signals.append(sig)
                        raw_signals.append(sig)
                except Exception as e:
                    logger.error("RegistryTimelineReconstructor falló para %s: %s", hive, e)
            results["registry"] = [s.metadata for s in registry_signals]

        # 1.3 Event Logs
        if event_logs:
            safe_logs = []
            for lp in event_logs:
                v = self._safe_path(lp)
                if v:
                    safe_logs.append(str(v))
            if safe_logs:
                try:
                    ev_result = self.eventlog.analyze(sorted(safe_logs), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(ev_result, "eventlog")
                    if sig:
                        sig.metadata["artifact_type"] = "windows_event_log"
                        raw_signals.append(sig)
                        results["eventlog"] = sig.metadata
                except Exception as e:
                    logger.error("EventLogCorrelator falló: %s", e)
                    results["eventlog"] = {"error": str(e)}

        # 1.4 Disk (MFT)
        if mft_json:
            try:
                mft_bytes = json.dumps(json.loads(mft_json), sort_keys=True, separators=(",", ":")).encode()
                disk_result = self.disk.analyze(mft_bytes, mft_json, self.chain, timestamp_utc)
                sig = self._to_signal_safe(disk_result, "disk")
                if sig:
                    sig.metadata["artifact_type"] = "mft"
                    raw_signals.append(sig)
                    results["disk"] = sig.metadata
            except Exception as e:
                logger.error("MFTTimelineAnalyzer falló: %s", e)
                results["disk"] = {"error": str(e)}

        # 1.5 Network
        if network_flows:
            try:
                net_result = self.network.analyze(
                    sorted(network_flows, key=lambda f: (f.timestamp, f.src_ip, f.dst_ip))
                )
                sig = self._to_signal_safe(net_result, "network")
                if sig:
                    sig.metadata["artifact_type"] = "network"
                    raw_signals.append(sig)
                    results["network"] = sig.metadata
            except Exception as e:
                logger.error("NetworkForensicsEngine falló: %s", e)
                results["network"] = {"error": str(e)}

        # ============================================================
        # 2. SIFT NUEVOS (6 motores)
        # ============================================================

        # 2.1 Prefetch
        if prefetch_dir and self.prefetch:
            v = self._safe_path(prefetch_dir)
            if v:
                try:
                    pf_result = self.prefetch.analyze_directory(str(v), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(pf_result, "prefetch")
                    if sig:
                        sig.metadata["artifact_type"] = "prefetch"
                        raw_signals.append(sig)
                        results["prefetch"] = sig.metadata
                except Exception as e:
                    logger.error("PrefetchAnalyzer falló: %s", e)

        # 2.2 USB
        if usb_hive_path and self.usb:
            v = self._safe_path(usb_hive_path)
            if v:
                try:
                    usb_result = self.usb.analyze_registry_hive(str(v), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(usb_result, "usb")
                    if sig:
                        sig.metadata["artifact_type"] = "usb"
                        raw_signals.append(sig)
                        results["usb"] = sig.metadata
                except Exception as e:
                    logger.error("USBDeviceTracker falló: %s", e)

        # 2.3 Browser
        if browser_profile and self.browser:
            v = self._safe_path(browser_profile)
            if v:
                try:
                    br_result = self.browser.analyze_profile(str(v), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(br_result, "browser")
                    if sig:
                        sig.metadata["artifact_type"] = "browser"
                        raw_signals.append(sig)
                        results["browser"] = sig.metadata
                except Exception as e:
                    logger.error("BrowserForensicsEngine falló: %s", e)

        # 2.4 Shellbag
        if shellbag_hive and self.shellbag:
            v = self._safe_path(shellbag_hive)
            if v:
                try:
                    sh_result = self.shellbag.analyze_hive(str(v), self.chain, timestamp_utc)
                    sig = self._to_signal_safe(sh_result, "shellbag")
                    if sig:
                        sig.metadata["artifact_type"] = "shellbag"
                        raw_signals.append(sig)
                        results["shellbag"] = sig.metadata
                except Exception as e:
                    logger.error("ShellbagAnalyzer falló: %s", e)

        # 2.5 Amcache/Shimcache
        if (amcache_path or system_hive_path) and self.amcache:
            try:
                am_result = self.amcache.analyze(
                    amcache_path=amcache_path,
                    system_hive_path=system_hive_path,
                    chain=self.chain,
                    timestamp_utc=timestamp_utc,
                )
                sig = self._to_signal_safe(am_result, "amcache")
                if sig:
                    sig.metadata["artifact_type"] = "amcache"
                    raw_signals.append(sig)
                    results["amcache"] = sig.metadata
            except Exception as e:
                logger.error("AmcacheShimcacheAnalyzer falló: %s", e)

        # 2.6 IOC enrichment (si hay base de datos externa)
        if self.ioc:
            try:
                if ioc_db_path:
                    self.ioc = IOCManager(ioc_db_path)
                # Enriquecer señales existentes con IOCs
                enriched = []
                for sig in raw_signals:
                    try:
                        enriched_sig = self.ioc.enrich_signal(sig)
                        enriched.append(enriched_sig)
                    except Exception:
                        enriched.append(sig)
                raw_signals = enriched
            except Exception as e:
                logger.error("IOCManager falló: %s", e)

        # ============================================================
        # 3. SIGNAL MAPPER — CCS Gate (si hay event_stream crudo)
        # ============================================================
        if event_stream and self.signal_mapper:
            try:
                mapped = self.signal_mapper.from_ccs(
                    [{"tool_name": s.tool_name, "value": s.value, "z_score": s.z_score,
                      "confidence": s.confidence, "metadata": s.metadata} for s in raw_signals]
                )
                if mapped:
                    raw_signals = mapped
                    results["ccs_gate"] = {"applied": True, "count": len(mapped)}
            except Exception as e:
                logger.error("SignalMapper CCS Gate falló: %s", e)

        # ============================================================
        # 4. GAMMA (Artifact Reliability)
        # ============================================================

        # L-037 FIX: Build acquisition metadata from ChainOfCustody.
        # CAIE degrades base_trust when acquisition_hash and
        # acquisition_timestamp are absent (NIST SP 800-86 §4.3).
        # The chain already records ACQUIRE operations with hashes and
        # timestamps — we propagate them to every signal here, at the
        # single convergence point where all signals are re-packaged.
        #
        # Only acquisition_hash and acquisition_timestamp are injected
        # (they exist in the chain).  acquisition_tool, write_blocker_used,
        # and examiner_id are NOT synthesised — they must be declared
        # explicitly by the examiner (vigia_agent.py CLI flags).  Absent
        # fields cause honest trust degradation, not a hidden bug.
        _acq_meta: Dict[str, Any] = {}
        if self.chain.records:
            _first = self.chain.records[0]
            if _first.artifact_hash and len(_first.artifact_hash) == 64:
                _acq_meta["acquisition_hash"] = f"sha256:{_first.artifact_hash}"
            if _first.timestamp:
                _acq_meta["acquisition_timestamp"] = _first.timestamp
        # Merge examiner-declared overrides (CLI flags: --acquisition-tool,
        # --write-blocker-used, --examiner-id).  These take precedence over
        # chain-derived values for the same keys.
        if self.acquisition_overrides:
            _acq_meta.update(self.acquisition_overrides)

        gamma_adjusted = []
        for sig in raw_signals:
            try:
                art_type = sig.metadata.get("artifact_type", "unknown")
                z_frac = Fraction(Decimal(str(sig.z_score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
                z_adjusted = apply_artifact_reliability_dynamic(z_frac, art_type, metadata=sig.metadata)
                # Merge: signal's own metadata > gamma fields > acquisition metadata.
                # _acq_meta is injected first so that any signal that already
                # carries its own acquisition fields is NOT overwritten.
                merged_meta = {
                    **_acq_meta,
                    **sig.metadata,
                    "gamma_applied": True,
                    "gamma_type": art_type,
                    "z_original": sig.z_score,
                }
                new_sig = SignalOutput(
                    tool_name=sig.tool_name,
                    value=sig.value,
                    z_score=float(z_adjusted),
                    confidence=sig.confidence,
                    metadata=merged_meta,
                )
                gamma_adjusted.append(new_sig)
            except Exception as e:
                logger.error("Gamma falló para %s: %s", sig.tool_name, e)
                gamma_adjusted.append(sig)

        # ============================================================
        # 5. FRS + Ghost In The Shell + Anti-Silencing
        # ============================================================
        def _entity_key_fn(sig):
            meta = sig.metadata
            pid = meta.get("pid", meta.get("PID", 0))
            if pid:
                return (f"pid:{pid}", meta.get("timestamp", 0))
            ip = meta.get("dst_ip", meta.get("remote_addr", ""))
            if ip:
                return (f"ip:{ip}", meta.get("timestamp", 0))
            return (sig.tool_name, meta.get("timestamp", 0))

        try:
            frs_groups = build_redundancy_groups(gamma_adjusted, _entity_key_fn, delta_t=60)
            frs_adjusted = process_all_groups(gamma_adjusted, frs_groups, score_attr="z_score")
        except Exception as e:
            logger.error("FRS pipeline falló: %s", e)
            frs_adjusted = gamma_adjusted
            frs_groups = []

        # ============================================================
        # 6. ENGINE MOTORES (Metabolic, Resonance, Behavioral, Pattern)
        # ============================================================
        engine_signals: List[SignalOutput] = []

        # 6.1 Metabolic Profiler
        if event_stream and self.metabolic:
            try:
                meta_result = self.metabolic.analyze(event_stream)
                sig = self._to_signal_safe(meta_result, "metabolic")
                if sig:
                    engine_signals.append(sig)
                    results["metabolic"] = sig.metadata
            except Exception as e:
                logger.error("MetabolicProfiler falló: %s", e)

        # 6.2 Cross-Artifact Resonance
        if frs_adjusted and self.resonance:
            try:
                res_result = self.resonance.analyze(frs_adjusted)
                sig = self._to_signal_safe(res_result, "resonance")
                if sig:
                    engine_signals.append(sig)
                    results["resonance"] = sig.metadata
            except Exception as e:
                logger.error("CrossArtifactResonance falló: %s", e)

        # 6.3 Behavioral Fingerprint
        if self.behavioral:
            try:
                if normal_events:
                    self.behavioral.train_baseline(normal_events)
                if event_stream:
                    beh_result = self.behavioral.analyze(event_stream)
                    sig = self._to_signal_safe(beh_result, "behavioral")
                    if sig:
                        engine_signals.append(sig)
                        results["behavioral"] = sig.metadata
            except Exception as e:
                logger.error("BehavioralFingerprint falló: %s", e)

        # 6.4 Case Pattern Library
        if frs_adjusted and self.patterns:
            try:
                pat_result = self.patterns.match(frs_adjusted)
                sig = self._to_signal_safe(pat_result, "patterns")
                if sig:
                    engine_signals.append(sig)
                    results["patterns"] = sig.metadata
            except Exception as e:
                logger.error("CasePatternLibrary falló: %s", e)

        # Combinar señales SIFT + Engine
        all_signals = frs_adjusted + engine_signals

        # ============================================================
        # 7. UNIFIED TIMELINE (cross-source temporal)
        # ============================================================
        if all_signals and self.timeline_engine:
            try:
                tl_result = self.timeline_engine.build_timeline(all_signals)
                sig = self._to_signal_safe(tl_result, "timeline")
                if sig:
                    all_signals.append(sig)
                    results["timeline"] = sig.metadata
            except Exception as e:
                logger.error("UnifiedTimelineEngine falló: %s", e)

        # ============================================================
        # 8. ADVERSARIAL ROBUSTNESS
        # ============================================================
        adv_signal: Optional[SignalOutput] = None
        if all_signals and self.adv_robust:
            try:
                adv_signal = self.adv_robust.analyze(all_signals)
                if adv_signal:
                    all_signals.append(adv_signal)
                    results["adversarial"] = adv_signal.metadata
            except Exception as e:
                logger.error("AdversarialRobustnessEngine falló: %s", e)

        # ============================================================
        # 9. ABDUCTIVE REASONING
        # ============================================================
        abduction = None
        try:
            abduction = self.reasoner.reason(all_signals)
        except Exception as e:
            logger.error("AbductiveReasoner falló: %s", e)

        # ============================================================
        # 10. CUSTODY EXPORT
        # ============================================================
        try:
            custody_export = self.chain.export_for_bundle()
        except Exception as e:
            logger.error("ChainOfCustody export falló: %s", e)
            custody_export = {}


        # ====================== CAIE INTEGRATION v1.0 ======================
        caie_result = None
        try:
            from vigia.core.forensic_adapter import ForensicAdapter
            context = ForensicAdapter.build_context(all_signals, raw_results=results)
            if context.caie_artifacts:
                caie_input = [
                    {
                        "source_tool": a.source_tool,
                        "evidence_type": a.evidence_type,
                        "raw_score": a.raw_score,
                        "description": a.description,
                        "metadata": a.metadata,
                        "base_trust": getattr(a, 'base_trust', 1.0),
                    }
                    for a in context.caie_artifacts
                ]
                from vigia.tools.caie import cross_artifact_analysis
                caie_result = asyncio.run(cross_artifact_analysis(caie_input))
                results["caie"] = caie_result
                logger.info("CAIE executed: %s | composite=%s | fractures=%s",
                           caie_result.get('verdict'),
                           caie_result.get('composite_score'),
                           caie_result.get('fractures_detected', 0))
            else:
                results["caie"] = {"status": "NO_ARTIFACTS"}
        except Exception as e:
            logger.error("CAIE failed (non-blocking): %s", e)
            results["caie"] = {"status": "ERROR", "error": str(e)}
        # ====================== ABDUCTIVE V2 PLACEHOLDER ======================
        abduction_v2 = None
        try:
            from vigia.core.forensic_adapter import ForensicAdapter
            context = ForensicAdapter.build_context(all_signals, raw_results=results)
            if context.abductive_records and context.causal_links:
                abduction_v2 = {
                    "status": "READY",
                    "n_artifacts": len(context.abductive_records),
                    "layers": sorted(set(r.layer.name for r in context.abductive_records)),
                    "n_causal_links": len(context.causal_links),
                    "note": "Para ejecutar run_pipeline(), proporcionar candidate_hypotheses",
                }
        except Exception as e:
            logger.error("AbductiveV2 prep failed: %s", e)
        # ====================================================================
        return {
            "case_id": self.case_id,
            "custody": custody_export,
            "signals": [self._signal_to_dict(s) for s in all_signals],
            "abduction": {
                "best_hypothesis": abduction.best_hypothesis if abduction else "UNDETERMINED",
                "best_posterior": str(abduction.best_posterior) if abduction else "0",
                "confidence": str(abduction.confidence) if abduction else "0",
                "narrative": abduction.peirce_narrative if abduction else "[FIRSTNESS] Pipeline error.",
                "ontological_level": abduction.ontological_level if abduction else None,
                "is_conclusive": abduction.is_conclusive if abduction else False,
            },
            "results": results,
            "pipeline_meta": {
                "n_sift_signals": len(frs_adjusted),
                "n_engine_signals": len(engine_signals),
                "n_total_signals": len(all_signals),
                "frs_groups": len(frs_groups),
                "gamma_applied": True,
                "anti_silencing": True,
                "version": "V4-COLECTIVO-2026-05-06",
            }
        }

    @staticmethod
    def _signal_to_dict(signal: SignalOutput) -> Dict[str, Any]:
        return {
            "tool": signal.tool_name,
            "z_score": signal.z_score,
            "confidence": signal.confidence,
            "value": signal.value,
            "metadata": signal.metadata,
        }
