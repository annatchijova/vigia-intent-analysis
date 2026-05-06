"""
vigia/sift/amcache_shimcache.py

Analiza Amcache.hve y ShimCache (AppCompatCache).
Amcache: registra TODOS los programas ejecutados (incluyendo malware).
ShimCache: registra programas que Windows "consideró" ejecutar (incluyendo fallidos).

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

TOOL_NAME = "AMCACHE_SHIMCACHE"
ARTIFACT_RELIABILITY = Fraction(70, 100)

# Programas que NUNCA deberían aparecer en un sistema legítimo
BLACKLISTED_PROGRAMS = {
    "mimikatz.exe", "mimilib.dll", "psexec.exe", "procdump.exe",
    "nc.exe", "netcat.exe", "cryptcat.exe", "pwdump.exe",
    "fgdump.exe", "gsecdump.exe", "wce.exe", "fgdump.exe",
}


@dataclass
class AmcacheRecord:
    program_name: str
    full_path: str
    sha1_hash: str
    first_run_time: str
    last_modified_time: str
    version: str
    publisher: str
    is_os_component: bool


@dataclass
class ShimcacheRecord:
    path: str
    last_modified: str
    execution_flag: bool  # True = ejecutado, False = solo "considerado"
    insert_flag: bool


@dataclass
class AmcacheAnalysisResult:
    amcache_path: str
    shimcache_path: str
    total_entries: int
    blacklisted_executions: List[Dict[str, Any]]
    suspicious_first_runs: List[Dict[str, Any]]
    execution_after_deletion: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.blacklisted_executions:
            z = Fraction(35, 10)
        elif len(self.suspicious_first_runs) >= 3:
            z = Fraction(25, 10)
        elif self.suspicious_first_runs:
            z = Fraction(18, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "amcache_path": self.amcache_path,
                "shimcache_path": self.shimcache_path,
                "total_entries": self.total_entries,
                "blacklisted_count": len(self.blacklisted_executions),
                "suspicious_first_run_count": len(self.suspicious_first_runs),
                "artifact_type": "amcache",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "stub": True,
                "finding_types": sorted(list(set(
                    b.get("type", "UNKNOWN") for b in self.blacklisted_executions
                ) | set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_first_runs
                ))),
            }
        )


class AmcacheShimcacheAnalyzer:
    """Analiza Amcache.hve y SYSTEM hive (ShimCache)."""

    def analyze(
        self,
        amcache_path: Optional[str] = None,
        system_hive_path: Optional[str] = None,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> AmcacheAnalysisResult:
        blacklisted = []
        suspicious_first = []
        exec_after_del = []

        # Stub: en producción, parsear Amcache.hve con regipy o herramientas especializadas
        # Amcache: Software\Microsoft\Windows\CurrentVersion\AppCompat\Flags\Compatibility Assistant\Store
        # ShimCache: SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache

        if chain:
            chain.acquire(b"AMCACHE_ANALYSIS", "AMCACHE_SHIMCACHE", timestamp_utc)

        composite = Fraction(0, 1)
        return AmcacheAnalysisResult(
            amcache_path=amcache_path or "",
            shimcache_path=system_hive_path or "",
            total_entries=0,  # Stub
            blacklisted_executions=blacklisted,
            suspicious_first_runs=suspicious_first,
            execution_after_deletion=exec_after_del,
            composite_score=composite,
        )

    def _is_blacklisted(self, program_name: str) -> bool:
        """Verifica si un programa está en la lista negra."""
        return program_name.lower() in {p.lower() for p in BLACKLISTED_PROGRAMS}
