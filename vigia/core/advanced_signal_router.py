"""
vigia/core/advanced_signal_router.py

Router avanzado de señales.
Dirige señales a los módulos de análisis apropiados basado en tipo de artefacto.

FIX P0: Import corregido: vigia.core.signal_output → vigia.models.signal_output
FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional

# FIX P0: Import corregido
from vigia.core.ebs_v1 import SignalOutput


class AdvancedSignalRouter:
    """
    Router que dirige señales a pipelines de análisis según tipo de artefacto.

    Mapeo:
    - memory → MemoryForensicsEngine
    - registry → RegistryTimelineReconstructor
    - event_log → EventLogCorrelator
    - mft/disk → MFTTimelineAnalyzer
    - network → NetworkForensicsEngine
    - prefetch → PrefetchAnalyzer
    - usb → USBDeviceTracker
    - browser → BrowserForensicsEngine
    - shellbag → ShellbagAnalyzer
    - amcache → AmcacheShimcacheAnalyzer
    """

    ROUTING_TABLE = {
        "memory": "vigia.sift.memory_forensics.MemoryForensicsEngine",
        "registry": "vigia.sift.registry_timeline_reconstructor.RegistryTimelineReconstructor",
        "event_log": "vigia.sift.event_log_correlator.EventLogCorrelator",
        "mft": "vigia.sift.disk_forensics.MFTTimelineAnalyzer",
        "disk": "vigia.sift.disk_forensics.MFTTimelineAnalyzer",
        "network": "vigia.sift.network_forensics.NetworkForensicsEngine",
        "prefetch": "vigia.sift.prefetch_analyzer.PrefetchAnalyzer",
        "usb": "vigia.sift.usb_device_tracker.USBDeviceTracker",
        "browser": "vigia.sift.browser_forensics.BrowserForensicsEngine",
        "shellbag": "vigia.sift.shellbag_analyzer.ShellbagAnalyzer",
        "amcache": "vigia.sift.amcache_shimcache.AmcacheShimcacheAnalyzer",
    }

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def route(self, signal: SignalOutput) -> str:
        """
        Determina el módulo destino para una señal.

        Returns:
            String con path del módulo, o "UNKNOWN" si no hay match.
        """
        art_type = signal.metadata.get("artifact_type", "unknown")
        return self.ROUTING_TABLE.get(art_type, "UNKNOWN")

    def route_batch(self, signals: List[SignalOutput]) -> Dict[str, List[SignalOutput]]:
        """
        Agrupa señales por módulo destino.

        Returns:
            Dict {module_path: [signals]}
        """
        batches: Dict[str, List[SignalOutput]] = {}
        for signal in signals:
            dest = self.route(signal)
            batches.setdefault(dest, []).append(signal)
        return batches

    def get_handler(self, artifact_type: str):
        """
        Obtiene instancia del handler para un tipo de artefacto.
        Usa caché para evitar reconstrucción.
        """
        if artifact_type in self._cache:
            return self._cache[artifact_type]

        module_path = self.ROUTING_TABLE.get(artifact_type)
        if not module_path:
            return None

        # Import dinámico
        try:
            module_name, class_name = module_path.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            handler_class = getattr(module, class_name)
            instance = handler_class()
            self._cache[artifact_type] = instance
            return instance
        except (ImportError, AttributeError):
            return None
