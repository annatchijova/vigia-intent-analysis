"""
vigia/sift/__init__.py

Paquete de integración SIFT/SANS para VIGÍA.
Incluye todos los motores forenses, utilidades matemáticas,
y el orquestador principal.

FIX P0: Todos los módulos exportados con Fraction purity.
"""

from vigia.sift._math_utils import (
    _log_rational, _exp_rational, _sqrt_fraction, _entropy_shannon, _parse_iso_timestamp,
    apply_artifact_reliability, build_redundancy_groups, apply_frs,
    classify_group, apply_conflict_penalty, process_all_groups,
    noisy_or_correlated, RESISTANCE_FACTOR,
)
from vigia.sift.memory_forensics import MemoryForensicsEngine, MemoryAnalysisResult
from vigia.sift.registry_timeline_reconstructor import RegistryTimelineReconstructor, RegistryAnalysisResult
from vigia.sift.event_log_correlator import EventLogCorrelator, EventLogAnalysisResult
from vigia.sift.disk_forensics import MFTTimelineAnalyzer, MFTAnalysisResult
from vigia.sift.network_forensics import NetworkForensicsEngine, NetworkAnalysisResult
from vigia.sift.sift_orchestrator import SIFTOrchestrator

# NUEVOS módulos del ecosistema SIFT
from vigia.sift.prefetch_analyzer import PrefetchAnalyzer, PrefetchAnalysisResult
from vigia.sift.usb_device_tracker import USBDeviceTracker, USBAnalysisResult
from vigia.sift.browser_forensics import BrowserForensicsEngine, BrowserAnalysisResult
from vigia.sift.shellbag_analyzer import ShellbagAnalyzer, ShellbagAnalysisResult
from vigia.sift.amcache_shimcache import AmcacheShimcacheAnalyzer, AmcacheAnalysisResult
from vigia.sift.ioc_manager import IOCManager, IOCMatchResult
from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine, TimelineAnalysisResult

__all__ = [
    # Math utils
    "_log_rational", "_exp_rational", "_sqrt_fraction", "_entropy_shannon", "_parse_iso_timestamp",
    "apply_artifact_reliability", "build_redundancy_groups", "apply_frs",
    "classify_group", "apply_conflict_penalty", "process_all_groups",
    "noisy_or_correlated", "RESISTANCE_FACTOR",
    # Core SIFT engines
    "MemoryForensicsEngine", "MemoryAnalysisResult",
    "RegistryTimelineReconstructor", "RegistryAnalysisResult",
    "EventLogCorrelator", "EventLogAnalysisResult",
    "MFTTimelineAnalyzer", "MFTAnalysisResult",
    "NetworkForensicsEngine", "NetworkAnalysisResult",
    "SIFTOrchestrator",
    # Extended ecosystem
    "PrefetchAnalyzer", "PrefetchAnalysisResult",
    "USBDeviceTracker", "USBAnalysisResult",
    "BrowserForensicsEngine", "BrowserAnalysisResult",
    "ShellbagAnalyzer", "ShellbagAnalysisResult",
    "AmcacheShimcacheAnalyzer", "AmcacheAnalysisResult",
    "IOCManager", "IOCMatchResult",
    "UnifiedTimelineEngine", "TimelineAnalysisResult",
]
