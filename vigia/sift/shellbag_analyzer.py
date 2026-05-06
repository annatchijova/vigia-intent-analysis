"""
vigia/sift/shellbag_analyzer.py

Analiza shellbags de Windows (NTUSER.DAT).
Los shellbags registran qué carpetas el usuario "navegó" en Explorer.
Detectan acceso a carpetas sensibles que el usuario dice no conocer.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

TOOL_NAME = "SHELLBAG_ANALYZER"
ARTIFACT_RELIABILITY = Fraction(65, 100)

# Carpetas que indican reconocimiento de estructura del sistema
SENSITIVE_FOLDER_PATTERNS = [
    "secret", "password", "finance", "hr", "executive", "admin",
    "backup", "archivo", "confidencial", "privado", "restricted",
]


@dataclass
class ShellbagRecord:
    path: str
    last_accessed: str
    node_slot: int
    folder_flags: List[str]
    view_mode: str
    position: Dict[str, int]


@dataclass
class ShellbagAnalysisResult:
    hive_path: str
    total_bags: int
    sensitive_access: List[Dict[str, Any]]
    deleted_folders_still_visible: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.deleted_folders_still_visible:
            z = Fraction(28, 10)
        elif len(self.sensitive_access) >= 5:
            z = Fraction(22, 10)
        elif self.sensitive_access:
            z = Fraction(15, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "hive_path": self.hive_path,
                "total_bags": self.total_bags,
                "sensitive_count": len(self.sensitive_access),
                "deleted_visible_count": len(self.deleted_folders_still_visible),
                "artifact_type": "shellbag",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "stub": True,
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.sensitive_access
                ) | set(
                    d.get("type", "UNKNOWN") for d in self.deleted_folders_still_visible
                ))),
            }
        )


class ShellbagAnalyzer:
    """Analiza shellbags desde NTUSER.DAT usando RegRipper o regipy."""

    def analyze_hive(
        self,
        hive_path: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> ShellbagAnalysisResult:
        p = Path(hive_path).resolve()
        if not p.exists():
            return ShellbagAnalysisResult(
                hive_path=str(p), total_bags=0,
                sensitive_access=[], deleted_folders_still_visible=[],
            )

        sensitive = []
        deleted_visible = []

        # Stub: en producción, usar RegRipper plugin shellbags o parsear regipy
        # Los shellbags están en NTUSER.DAT\Software\Microsoft\Windows\Shell\BagMRU

        # Heurística de detección:
        # 1. Carpetas sensibles accedidas
        # 2. Carpetas que ya no existen en disco pero aparecen en shellbags
        #    (indica que el usuario las vio antes de que fueran borradas)

        if chain:
            chain.acquire(b"SHELLBAG_ANALYSIS", "SHELLBAG_ANALYZER", timestamp_utc)

        composite = Fraction(0, 1)
        return ShellbagAnalysisResult(
            hive_path=str(p),
            total_bags=0,  # Stub
            sensitive_access=sensitive,
            deleted_folders_still_visible=deleted_visible,
            composite_score=composite,
        )

    def _is_sensitive_path(self, path: str) -> bool:
        """Determina si una ruta es sensible."""
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in SENSITIVE_FOLDER_PATTERNS)
