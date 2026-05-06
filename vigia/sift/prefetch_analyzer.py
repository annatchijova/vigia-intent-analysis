"""
vigia/sift/prefetch_analyzer.py

Analizador de Prefetch de Windows.
Detecta ejecución de programas sospechosos, borrado selectivo de prefetch
(indicador de anti-forense), y correlación con otros artefactos.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

TOOL_NAME = "PREFETCH_ANALYZER"
ARTIFACT_RELIABILITY = Fraction(70, 100)

# Hash de archivos prefetch conocidos por ser borrados en anti-forense
ANTI_FORENSIC_PREFETCH_SIGNS = [
    "mimikatz.exe", "psexec.exe", "procdump.exe", "nc.exe", "netcat.exe",
    "rundll32.exe", "regsvr32.exe", "mshta.exe", "certutil.exe",
]


@dataclass
class PrefetchRecord:
    filename: str
    hash: str
    last_execution_time: str
    run_count: int
    volume_serial: str
    volume_path: str
    dependencies: List[str]


@dataclass
class PrefetchAnalysisResult:
    source_path: str
    total_files: int
    suspicious_executions: List[Dict[str, Any]]
    anti_forensic_deletions: List[Dict[str, Any]]
    timeline_gaps: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.anti_forensic_deletions:
            z = Fraction(32, 10)
        elif len(self.suspicious_executions) >= 3:
            z = Fraction(25, 10)
        elif self.suspicious_executions:
            z = Fraction(18, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "source_path": self.source_path,
                "total_files": self.total_files,
                "suspicious_count": len(self.suspicious_executions),
                "anti_forensic_count": len(self.anti_forensic_deletions),
                "artifact_type": "prefetch",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "stub": True,
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_executions
                ) | set(
                    a.get("type", "UNKNOWN") for a in self.anti_forensic_deletions
                ))),
            }
        )


class PrefetchAnalyzer:
    """Analiza archivos .pf de Windows Prefetch."""

    def __init__(self):
        self._suspicious_names = {n.lower() for n in ANTI_FORENSIC_PREFETCH_SIGNS}

    def analyze_directory(
        self,
        prefetch_dir: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> PrefetchAnalysisResult:
        from vigia.sift._math_utils import _parse_iso_timestamp

        p = Path(prefetch_dir).resolve()
        if not p.exists() or not p.is_dir():
            return PrefetchAnalysisResult(
                source_path=str(p), total_files=0,
                suspicious_executions=[], anti_forensic_deletions=[], timeline_gaps=[],
            )

        pf_files = sorted(p.glob("*.pf"))
        suspicious = []
        anti_forensic = []

        for pf in pf_files:
            try:
                record = self._parse_pf(pf)
                if record.filename.lower() in self._suspicious_names:
                    suspicious.append({
                        "type": "SUSPICIOUS_EXECUTION",
                        "filename": record.filename,
                        "run_count": record.run_count,
                        "last_execution": record.last_execution_time,
                        "severity": str(Fraction(85, 100)),
                    })
            except Exception:
                continue

        # Detección de borrado: si hay menos de 10 archivos .pf en un sistema
        # Windows típico (que suele tener 50-150), es sospechoso
        if len(pf_files) < 10 and len(pf_files) > 0:
            anti_forensic.append({
                "type": "PREFETCH_WIPE",
                "file_count": len(pf_files),
                "expected_min": 50,
                "severity": str(Fraction(75, 100)),
                "description": "Cantidad anormalmente baja de archivos prefetch",
            })

        # Calcular composite score
        sev_sum = sum(Fraction(s["severity"]) for s in suspicious)
        af_sum = sum(Fraction(a["severity"]) for a in anti_forensic)
        composite = min(sev_sum + af_sum, Fraction(95, 100))

        if chain:
            chain.acquire(b"PREFETCH_ANALYSIS", "PREFETCH_ANALYZER", timestamp_utc)

        return PrefetchAnalysisResult(
            source_path=str(p),
            total_files=len(pf_files),
            suspicious_executions=suspicious,
            anti_forensic_deletions=anti_forensic,
            timeline_gaps=[],
            composite_score=composite,
        )

    def _parse_pf(self, path: Path) -> PrefetchRecord:
        """Parseo simplificado de Prefetch v17 (Windows 10)."""
        data = path.read_bytes()
        if len(data) < 8:
            raise ValueError("Archivo prefetch demasiado pequeño")

        version = struct.unpack("<I", data[0:4])[0]
        sig = data[4:8]

        if sig != b"MAM\x04" and sig != b"MAM\x03":
            raise ValueError("Firma de prefetch inválida")

        # Simplificación: extraer nombre del archivo del path
        filename = path.stem.replace("-", "")

        # Hash del archivo para integridad
        file_hash = hashlib.sha256(data).hexdigest()[:16]

        return PrefetchRecord(
            filename=filename,
            hash=file_hash,
            last_execution_time="unknown",
            run_count=1,
            volume_serial="unknown",
            volume_path="unknown",
            dependencies=[],
        )
