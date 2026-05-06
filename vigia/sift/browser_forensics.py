"""
vigia/sift/browser_forensics.py

Analiza artefactos de navegador: historial, downloads, cookies, cache.
Detecta descarga de herramientas de ataque, navegación a dominios C2,
y correlación con actividad de red.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

TOOL_NAME = "BROWSER_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(65, 100)

# Dominios sospechosos asociados a descarga de herramientas de ataque
MALICIOUS_DOMAINS = {
    "github.com/mimikatz", "github.com/gentilkiwi",
    "download.sysinternals.com",  # Legítimo pero usado en ataques
}

# Extensiones de archivo sospechosas en downloads
SUSPICIOUS_EXTENSIONS = {".exe",".dll",".ps1",".bat",".cmd",".vbs",".js",".hta"}


@dataclass
class BrowserDownloadRecord:
    url: str
    filename: str
    download_time: str
    file_size: int
    target_path: str
    danger_type: str
    opened: bool


@dataclass
class BrowserHistoryRecord:
    url: str
    title: str
    visit_time: str
    visit_count: int
    transition_type: str


@dataclass
class BrowserAnalysisResult:
    source_profile: str
    total_downloads: int
    suspicious_downloads: List[Dict[str, Any]]
    c2_navigation: List[Dict[str, Any]]
    credential_access: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.c2_navigation:
            z = Fraction(30, 10)
        elif len(self.suspicious_downloads) >= 3:
            z = Fraction(25, 10)
        elif self.suspicious_downloads:
            z = Fraction(18, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "source_profile": self.source_profile,
                "total_downloads": self.total_downloads,
                "suspicious_count": len(self.suspicious_downloads),
                "c2_count": len(self.c2_navigation),
                "artifact_type": "browser",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "stub": True,
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_downloads
                ) | set(
                    c.get("type", "UNKNOWN") for c in self.c2_navigation
                ))),
            }
        )


class BrowserForensicsEngine:
    """Analiza perfiles de Chrome/Edge/Firefox."""

    def analyze_profile(
        self,
        profile_path: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> BrowserAnalysisResult:
        p = Path(profile_path).resolve()
        if not p.exists() or not p.is_dir():
            return BrowserAnalysisResult(
                source_profile=str(p), total_downloads=0,
                suspicious_downloads=[], c2_navigation=[], credential_access=[],
            )

        suspicious = []
        c2_nav = []
        cred_access = []

        # Analizar Downloads
        downloads_db = p / "Downloads"
        if downloads_db.exists():
            # Stub: en producción, parsear SQLite
            pass

        # Analizar History
        history_db = p / "History"
        if history_db.exists():
            # Stub: en producción, parsear SQLite con visit_count
            pass

        # Heurísticas de detección
        # Stub: implementar parseo real de SQLite

        if chain:
            chain.acquire(b"BROWSER_ANALYSIS", "BROWSER_FORENSICS", timestamp_utc)

        composite = Fraction(0, 1)
        return BrowserAnalysisResult(
            source_profile=str(p),
            total_downloads=0,
            suspicious_downloads=suspicious,
            c2_navigation=c2_nav,
            credential_access=cred_access,
            composite_score=composite,
        )

    def _is_suspicious_download(self, url: str, filename: str) -> bool:
        """Determina si una descarga es sospechosa."""
        url_lower = url.lower()
        filename_lower = filename.lower()

        # Herramientas de ataque conocidas
        for domain in MALICIOUS_DOMAINS:
            if domain in url_lower:
                return True

        # Extensiones ejecutables
        if any(filename_lower.endswith(ext) for ext in SUSPICIOUS_EXTENSIONS):
            return True

        return False
