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
# L-024 FIX (Tanda B, 2026-07-03, prefijos aprobados por la operadora):
# `/mnt` genérico salió de la allowlist — permitía leer CUALQUIER montaje del
# host (NFS corporativo, discos personales). Solo los puntos de montaje
# forenses declarados entran, vía _forensic_mounts(). Un montaje fuera de
# esos prefijos requiere exportar VIGIA_EVIDENCE_DIR (el contrato documentado
# en CLAUDE.md), y su rechazo es VISIBLE (señal PATHGUARD unanalyzed, F7).
_STATIC_ALLOWLIST = (
    Path('/var/vigia'),
    Path('/tmp/vigia'),
    Path('/home/vigia/cases'),
    Path.home() / 'vigia-repo' / 'evidence',
    Path.home() / 'vigia-repo' / 'data',
)

# Prefijos de montaje forense permitidos bajo /mnt (glob), decisión Tanda B:
#   /mnt/vigia_*  — montajes propios del operador
#   /mnt/ewf*     — ewfmount (imágenes E01)
#   /mnt/evidence — punto de montaje genérico documentado
_FORENSIC_MOUNT_GLOBS = ("vigia_*", "ewf*", "evidence")


def _forensic_mounts(base: Path = Path('/mnt')) -> List[Path]:
    """
    Expande los prefijos forenses de /mnt a puntos de montaje EXISTENTES al
    momento de construir el orquestador. Un montaje creado después requiere
    re-instanciar (o VIGIA_EVIDENCE_DIR). Determinista: orden sorted.
    `base` es parametrizable solo para tests.
    """
    mounts: List[Path] = []
    mnt = base
    if not mnt.is_dir():
        return mounts
    for pattern in _FORENSIC_MOUNT_GLOBS:
        try:
            for p in sorted(mnt.glob(pattern)):
                if p.is_dir() and not p.is_symlink():
                    mounts.append(p)
        except OSError:
            continue
    return mounts


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
    # L-024: puntos de montaje forenses existentes bajo /mnt (prefijos
    # aprobados), en lugar del /mnt genérico anterior.
    allowed.extend(_forensic_mounts())
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
        # F7 (AUDITORIA_PIPELINE_ROBUSTEZ): visibilidad de pérdidas silenciosas.
        # _rejected_paths: rechazos de PathGuard (antes: log + skip invisible).
        # _signal_drops: resultados que fallaron la conversión a SignalOutput.
        self._rejected_paths: List[Tuple[str, str]] = []
        self._signal_drops: List[str] = []

        # SIFT motores originales.
        # FIX (auditoría FN, P1-D): construcción resiliente. Algunos motores
        # validan un binario externo en su __init__ (MemoryForensicsEngine →
        # `vol`, RegistryTimelineReconstructor → `rip.pl`) y lanzan si falta.
        # Antes eso tumbaba el orquestador ENTERO, deshabilitando incluso los
        # motores que no necesitan ese binario (browser/event log/network/MFT,
        # que son stdlib). Ahora una dependencia ausente deshabilita SOLO su
        # motor (queda None); el resto del pipeline opera.
        self.memory = self._safe_engine("memory", MemoryForensicsEngine)
        self.registry = self._safe_engine("registry", RegistryTimelineReconstructor)
        self.eventlog = self._safe_engine("eventlog", EventLogCorrelator)
        self.disk = self._safe_engine("disk", MFTTimelineAnalyzer)
        self.network = self._safe_engine("network", NetworkForensicsEngine)

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

    @staticmethod
    def _safe_engine(name: str, ctor):
        """
        Instancia un motor; si su constructor falla (p.ej. binario externo
        ausente), lo deshabilita (None) en vez de propagar el fallo al
        orquestador completo. La dependencia ausente se degrada a "motor no
        disponible", no a "pipeline caído".
        """
        try:
            return ctor()
        except Exception as e:  # pylint: disable=broad-except
            logger.error("[SIFT] Motor '%s' no disponible (dependencia ausente?): %s",
                         name, e)
            return None

    def _safe_path(self, path_str: Optional[str], for_read: bool = True,
                   allow_dir: bool = False) -> Optional[Path]:
        """
        FIX V4+P2: PathGuard con TOCTOU completo. Si falla, loggea y retorna None.
        Usa safe_read para lecturas seguras integradas.

        allow_dir=True para motores que operan sobre directorios (browser
        profile, prefetch dir) — sin esto PathGuard rechazaba el directorio con
        NOT_A_REGULAR_FILE y el motor nunca corría (falso negativo, P1-A/P0-C).
        """
        if not path_str:
            return None
        try:
            check = self.path_guard.validate(path_str, for_read=for_read, allow_dir=allow_dir)
            if not check.valid:
                logger.error("PathGuard REJECT %s: %s", path_str, check.reason)
                # F7: el rechazo deja de ser invisible — se registra para
                # emitir una señal `unanalyzed` al final del pipeline.
                self._rejected_paths.append((path_str, str(check.reason)))
                return None
            return Path(path_str).absolute()
        except SecurityException as e:
            logger.error("SecurityException en %s: %s", path_str, e)
            self._rejected_paths.append((path_str, f"SecurityException: {e}"))
            return None

    def _safe_read(self, path_str: str) -> Optional[bytes]:
        """Lectura segura con TOCTOU completo."""
        try:
            return self.path_guard.safe_read(path_str)
        except (PermissionError, SecurityException) as e:
            logger.error("PathGuard safe_read REJECT %s: %s", path_str, e)
            return None

    # B-089: conversiones de motores DERIVADOS — sus crashes de to_signal()
    # se contabilizan (F8) pero NO emiten stub *_UNANALYZED (ver except abajo).
    # Debe coincidir con los method_name de las conexiones bajo "ENGINE
    # MOTORES" y "UNIFIED TIMELINE" en run_full_analysis.
    _DERIVED_CONVERSIONS = frozenset(
        {"metabolic", "resonance", "behavioral", "patterns",
         "timeline", "adversarial"}
    )

    def _to_signal_safe(self, result, method_name: str) -> Optional[SignalOutput]:
        """Convierte un resultado a SignalOutput, loggea errores."""
        try:
            if hasattr(result, "to_signal"):
                return result.to_signal()
            return None
        except Exception as e:
            logger.error("Error en to_signal de %s: %s", method_name, e)
            # F8 (N14): el drop se contabiliza — pipeline_meta lo expone.
            self._signal_drops.append(f"{method_name}: {type(e).__name__}: {e}")
            # B-089 (N14): un artefacto PRIMARIO cuya conversión crashea debe
            # quedar visible como *_UNANALYZED (mecanismo F7) — entra en
            # n_unanalyzed_artifacts y en la narrativa, y puede degradar
            # NOISE→ABSTAIN. Las conversiones DERIVADAS (síntesis sobre
            # señales ya emitidas) quedan fuera: F7 nunca marcó sus crashes
            # de motor, y "falló una síntesis" no es "evidencia sin analizar"
            # — un stub derivado degradaría el veredicto sin pérdida de
            # evidencia real.
            if method_name in self._DERIVED_CONVERSIONS:
                return None
            return self._unanalyzed_signal(
                method_name, method_name,
                f"to_signal: {type(e).__name__}: {e}",
            )

    @staticmethod
    def _unanalyzed_signal(engine: str, artifact_type: str, error: str) -> SignalOutput:
        """
        F7 (N7): señal sintética que marca un artefacto como NO ANALIZADO
        cuando su motor lanzó una excepción o PathGuard rechazó su ruta.
        z=0 y signal_class=derived: no aporta al veredicto ni a los gates de
        corroboración — solo hace visible la pérdida (0 hallazgos sobre
        evidencia no analizada NO es evidencia de benignidad).
        """
        return SignalOutput(
            tool_name=f"{engine.upper()}_UNANALYZED",
            value=0.0,
            z_score=0.0,
            confidence=0.0,
            metadata={
                "artifact_type": artifact_type,
                "unanalyzed": True,
                "signal_class": "derived",
                "error": str(error)[:200],
            },
        )

    @staticmethod
    def _mark_derived(sig: Optional[SignalOutput]) -> Optional[SignalOutput]:
        """
        F5 (N4): etiqueta una señal como DERIVADA (motores engine, timeline,
        adversarial robustness). Las derivadas no cuentan para el gate de
        corroboración ≥3 del reasoner ni para el override L-036 del agente.
        """
        if sig is None:
            return None
        meta = dict(sig.metadata) if isinstance(sig.metadata, dict) else {}
        meta["signal_class"] = "derived"
        sig.metadata = meta
        return sig

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
        # F7/F8: estado de visibilidad limpio por corrida.
        self._rejected_paths = []
        self._signal_drops = []

        # ============================================================
        # 1. SIFT ORIGINALES (5 mundos)
        # ============================================================

        # 1.1 Memory
        if memory_dump_path and self.memory:
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
                    raw_signals.append(self._unanalyzed_signal("memory", "memory", e))

        # 1.2 Registry
        if registry_hives and self.registry:
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
                    raw_signals.append(self._unanalyzed_signal("registry", "registry", f"{hive}: {e}"))
            results["registry"] = [s.metadata for s in registry_signals]

        # 1.3 Event Logs
        if event_logs and self.eventlog:
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
                    raw_signals.append(self._unanalyzed_signal("eventlog", "windows_event_log", e))

        # 1.4 Disk (MFT)
        if mft_json and self.disk:
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
                raw_signals.append(self._unanalyzed_signal("disk", "mft", e))

        # 1.5 Network
        if network_flows and self.network:
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
                raw_signals.append(self._unanalyzed_signal("network", "network", e))

        # ============================================================
        # 2. SIFT NUEVOS (6 motores)
        # ============================================================

        # 2.1 Prefetch
        if prefetch_dir and self.prefetch:
            v = self._safe_path(prefetch_dir, allow_dir=True)
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
                    raw_signals.append(self._unanalyzed_signal("prefetch", "prefetch", e))

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
                    raw_signals.append(self._unanalyzed_signal("usb", "usb", e))

        # 2.3 Browser
        if browser_profile and self.browser:
            v = self._safe_path(browser_profile, allow_dir=True)
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
                    raw_signals.append(self._unanalyzed_signal("browser", "browser", e))

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
                    raw_signals.append(self._unanalyzed_signal("shellbag", "shellbag", e))

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
                raw_signals.append(self._unanalyzed_signal("amcache", "amcache", e))

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

        # Part 4 fix (AUDITORIA_COBERTURA_MOTOR): un motor deshabilitado por
        # dependencia ausente (self.<engine> is None vía _safe_engine) con su
        # artefacto presente se salteaba SIN marca F7 — el guard de cada bloque
        # `if <artefacto> and self.<engine>:` es falso y el _unanalyzed_signal
        # (que vive en el `except`) nunca se alcanza. Simetría con el caso
        # "engine presente pero lanzó excepción": aquí se materializa la
        # NO-disponibilidad como señal `unanalyzed` para que el artefacto no
        # desaparezca en silencio (posible NOISE espurio → ahora ABSTAIN).
        _engine_artifacts = (
            (memory_dump_path, self.memory, "memory", "memory"),
            (registry_hives, self.registry, "registry", "registry"),
            (event_logs, self.eventlog, "eventlog", "windows_event_log"),
            (mft_json, self.disk, "disk", "mft"),
            (network_flows, self.network, "network", "network"),
            (prefetch_dir, getattr(self, "prefetch", None), "prefetch", "prefetch"),
            (usb_hive_path, getattr(self, "usb", None), "usb", "usb"),
            (browser_profile, getattr(self, "browser", None), "browser", "browser"),
            (shellbag_hive, getattr(self, "shellbag", None), "shellbag", "shellbag"),
            (amcache_path or system_hive_path, getattr(self, "amcache", None),
             "amcache", "amcache"),
        )
        for _artifact, _engine, _name, _art_type in _engine_artifacts:
            if _artifact and _engine is None:
                logger.warning(
                    "[SIFT] Artefacto '%s' presente pero motor '%s' no disponible "
                    "(dependencia ausente) — marcado UNANALYZED, no benigno.",
                    _art_type, _name,
                )
                raw_signals.append(self._unanalyzed_signal(
                    _name, _art_type, "engine unavailable (dependency absent)"
                ))

        # F7 (N7 variante PathGuard): cada ruta rechazada por PathGuard se
        # materializa como señal `unanalyzed` — el rechazo silencioso era el
        # candidato más fuerte del patrón "agente no ve lo que Claude sí ve".
        for rejected_path, reason in self._rejected_paths:
            raw_signals.append(self._unanalyzed_signal(
                "pathguard_reject",
                "pathguard_reject",
                f"{rejected_path}: {reason}",
            ))

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
                # F5 (N4): clase de señal. Las señales SIFT de artefacto son
                # PRIMARIAS; las `unanalyzed` (stubs honestos, motores caídos,
                # rechazos PathGuard) son DERIVADAS — marcan pérdida, no
                # evidencia. setdefault respeta etiquetas ya presentes.
                if merged_meta.get("unanalyzed"):
                    merged_meta["signal_class"] = "derived"
                else:
                    merged_meta.setdefault("signal_class", "primary")
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
                sig = self._mark_derived(self._to_signal_safe(meta_result, "metabolic"))
                if sig:
                    engine_signals.append(sig)
                    results["metabolic"] = sig.metadata
            except Exception as e:
                logger.error("MetabolicProfiler falló: %s", e)

        # 6.2 Cross-Artifact Resonance
        if frs_adjusted and self.resonance:
            try:
                res_result = self.resonance.analyze(frs_adjusted)
                sig = self._mark_derived(self._to_signal_safe(res_result, "resonance"))
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
                    sig = self._mark_derived(self._to_signal_safe(beh_result, "behavioral"))
                    if sig:
                        engine_signals.append(sig)
                        results["behavioral"] = sig.metadata
            except Exception as e:
                logger.error("BehavioralFingerprint falló: %s", e)

        # 6.4 Case Pattern Library
        if frs_adjusted and self.patterns:
            try:
                pat_result = self.patterns.match(frs_adjusted)
                sig = self._mark_derived(self._to_signal_safe(pat_result, "patterns"))
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
                sig = self._mark_derived(self._to_signal_safe(tl_result, "timeline"))
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
                adv_signal = self._mark_derived(self.adv_robust.analyze(all_signals))
                if adv_signal:
                    all_signals.append(adv_signal)
                    results["adversarial"] = adv_signal.metadata
            except Exception as e:
                logger.error("AdversarialRobustnessEngine falló: %s", e)

        # ============================================================
        # 9. ABDUCTIVE REASONING
        # ============================================================
        # F2 (AUDITORIA_PIPELINE_ROBUSTEZ, N1): el error del reasoner nunca
        # más genérico ni solo-en-logs. reason() ya devuelve REASONER_ERROR
        # ante cualquier excepción interna; este except es la segunda red
        # (defensa en profundidad) y conserva tipo+mensaje para el bundle.
        abduction = None
        reasoner_error: Optional[str] = None
        try:
            abduction = self.reasoner.reason(all_signals)
        except Exception as e:
            logger.exception("AbductiveReasoner falló")
            reasoner_error = f"{type(e).__name__}: {e}"
            results["reasoner_error"] = reasoner_error

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
        # Artefactos NO analizados (motores stub / DBs ilegibles / dependencias
        # ausentes). Visibilidad para que el agente distinga "no analizado" de
        # "analizado y limpio" — 0 hallazgos aquí NO es evidencia de benignidad.
        unanalyzed_artifacts = sorted({
            s.metadata.get("artifact_type", s.tool_name)
            for s in all_signals
            if isinstance(s.metadata, dict) and s.metadata.get("unanalyzed")
        })
        if unanalyzed_artifacts:
            results["unanalyzed_artifacts"] = unanalyzed_artifacts
            logger.warning("[SIFT] Artefactos no analizados: %s", unanalyzed_artifacts)

        # F2: narrativa degradada honesta si el reasoner crasheó pese a su
        # propia red interna. Nunca más "[FIRSTNESS] Pipeline error." seco:
        # la extracción SÍ corrió — se narra qué hay y qué falló exactamente.
        if abduction is not None:
            _narrative = abduction.peirce_narrative
        else:
            _narrative = (
                f"[FIRSTNESS] {len(all_signals)} señales extraídas y selladas "
                f"por el pipeline ({len(frs_adjusted)} SIFT, "
                f"{len(engine_signals)} engine).\n"
                f"[SECONDNESS] El razonador abductivo falló antes de emitir "
                f"inferencia: {reasoner_error or 'error desconocido'}.\n"
                f"[THIRDNESS] Sin inferencia abductiva disponible — el "
                f"veredicto se resuelve por override determinista de señales "
                f"(L-036) o ABSTAIN. El fallo del razonador NO es evidencia "
                f"de benignidad ni de malicia."
            )

        # F8 (N14): drops de conversión visibles en el resultado.
        if self._signal_drops:
            results["signal_conversion_drops"] = list(self._signal_drops)
            logger.warning("[SIFT] Señales perdidas en to_signal: %s",
                           self._signal_drops)

        return {
            "case_id": self.case_id,
            "custody": custody_export,
            "signals": [self._signal_to_dict(s) for s in all_signals],
            "abduction": {
                "best_hypothesis": abduction.best_hypothesis if abduction else "REASONER_ERROR",
                "best_posterior": str(abduction.best_posterior) if abduction else "0",
                "confidence": str(abduction.confidence) if abduction else "0",
                "narrative": _narrative,
                "ontological_level": abduction.ontological_level if abduction else None,
                "is_conclusive": abduction.is_conclusive if abduction else False,
                **({"reasoner_error": reasoner_error} if reasoner_error else {}),
            },
            "results": results,
            "pipeline_meta": {
                # N11 (Tanda B, opción B): Metabolic/Behavioral requieren
                # event_stream, que el modo agente nunca genera (el shim
                # re-mapea event_stream→event_logs). Se declara explícito —
                # "no corrió por diseño" ≠ "corrió y no encontró nada".
                # Patrón B-052-P1. Alimentarlos desde los EventRecord ya
                # parseados queda como mejora futura (ver PROPUESTA_TANDA_B
                # ítem 7, opción A).
                **({"engines_not_run_no_event_stream": sorted(
                    name for name, eng in (
                        ("metabolic", self.metabolic),
                        ("behavioral", self.behavioral),
                    ) if eng is not None
                )} if not event_stream else {}),
                "n_sift_signals": len(frs_adjusted),
                "n_engine_signals": len(engine_signals),
                "n_total_signals": len(all_signals),
                "n_primary_signals": len([
                    s for s in all_signals
                    if not isinstance(s.metadata, dict)
                    or (s.metadata.get("signal_class") != "derived"
                        and not s.metadata.get("unanalyzed"))
                ]),
                "n_unanalyzed_artifacts": len(unanalyzed_artifacts),
                "n_pathguard_rejects": len(self._rejected_paths),
                "n_signal_conversion_drops": len(self._signal_drops),
                "frs_groups": len(frs_groups),
                "gamma_applied": True,
                "anti_silencing": True,
                "version": "V4-COLECTIVO-2026-07-03",
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
