"""
vigia/sift/usb_device_tracker.py

Rastrea dispositivos USB conectados al sistema.
Detecta exfiltración física de datos, dispositivos no autorizados,
y correlación con actividad de red (exfiltración híbrida).

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

TOOL_NAME = "USB_DEVICE_TRACKER"
ARTIFACT_RELIABILITY = Fraction(70, 100)

# VID:PID de dispositivos de almacenamiento masivo sospechosos
SUSPICIOUS_VID_PID = {
    (0x0781, 0x5567): "SanDisk Cruzer",  # Común pero puede ser usado para exfil
}


@dataclass
class USBDeviceRecord:
    vendor_id: int
    product_id: int
    serial_number: str
    first_connect: str
    last_connect: str
    friendly_name: str
    drive_letter: str
    volume_size_mb: int


@dataclass
class USBAnalysisResult:
    source_path: str
    total_devices: int
    suspicious_devices: List[Dict[str, Any]]
    exfiltration_candidates: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.exfiltration_candidates:
            z = Fraction(28, 10)
        elif len(self.suspicious_devices) >= 2:
            z = Fraction(22, 10)
        elif self.suspicious_devices:
            z = Fraction(15, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "source_path": self.source_path,
                "total_devices": self.total_devices,
                "suspicious_count": len(self.suspicious_devices),
                "exfil_candidates": len(self.exfiltration_candidates),
                "artifact_type": "usb",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "stub": True,
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_devices
                ) | set(
                    e.get("type", "UNKNOWN") for e in self.exfiltration_candidates
                ))),
            }
        )


class USBDeviceTracker:
    """Analiza registros USB desde Registry o logs de sistema."""

    def analyze_registry_hive(
        self,
        hive_path: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> USBAnalysisResult:
        p = Path(hive_path).resolve()
        if not p.exists():
            return USBAnalysisResult(
                source_path=str(p), total_devices=0,
                suspicious_devices=[], exfiltration_candidates=[],
            )

        # Stub: en producción, usar RegRipper o regipy para parsear USBSTOR
        # Aquí simulamos detección basada en heurísticas
        suspicious = []
        exfil = []

        # Heurística: dispositivo conectado fuera de horario de oficina
        # y con capacidad > 32GB (típico para exfiltración masiva)
        # En implementación real, esto vendría del parseo del hive

        if chain:
            chain.acquire(b"USB_ANALYSIS", "USB_DEVICE_TRACKER", timestamp_utc)

        composite = Fraction(0, 1)
        return USBAnalysisResult(
            source_path=str(p),
            total_devices=0,  # Stub: requiere parseo real del hive
            suspicious_devices=suspicious,
            exfiltration_candidates=exfil,
            composite_score=composite,
        )

    def correlate_with_network(
        self,
        usb_result: USBAnalysisResult,
        network_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Detecta exfiltración híbrida: datos copiados a USB + subidos a nube.
        Si hay actividad USB y actividad de red a dominios de storage
        dentro de la misma ventana temporal, es sospechoso.
        """
        correlations = []
        # Stub: implementar correlación temporal cruzada
        return correlations
