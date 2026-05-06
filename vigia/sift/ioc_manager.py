"""
vigia/sift/ioc_manager.py

Motor de Indicadores de Compromiso (IOC).
Matchea hallazgos forenses contra bases de datos de amenazas conocidas.
Soporta IOCs de tipo hash, filename, registry key, IP, domain, y MITRE technique.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

def _safe_fraction(value) -> Fraction:
    # FIX P2 (V19): Evita Fraction gigante o fuera de rango.
    if isinstance(value, float):
        if value < 0.0 or value > 1.0:
            raise ValueError(f"IOC confidence fuera de rango [0,1]: {value}")
        return Fraction(value).limit_denominator(1000)
    if isinstance(value, int):
        if value < 0 or value > 1:
            raise ValueError(f"IOC confidence fuera de rango [0,1]: {value}")
        return Fraction(value, 1)
    if isinstance(value, str):
        f = Fraction(value)
        if f < 0 or f > 1:
            raise ValueError(f"IOC confidence fuera de rango [0,1]: {value}")
        return f.limit_denominator(1000)
    raise ValueError(f"Tipo de confidence no soportado: {type(value)}")



from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

TOOL_NAME = "IOC_MANAGER"
ARTIFACT_RELIABILITY = Fraction(90, 100)  # IOCs son datos de inteligencia


@dataclass(frozen=True)
class IOCRecord:
    ioc_type: str  # hash, filename, registry, ip, domain, technique
    value: str
    threat_family: str
    mitre_technique: str
    confidence: Fraction
    source: str
    first_seen: str
    last_seen: str


@dataclass
class IOCMatchResult:
    total_iocs_loaded: int
    matches: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.matches:
            max_conf = max(Fraction(m["match_confidence"]) for m in self.matches)
            z = Fraction(35, 10) if max_conf >= Fraction(9, 10) else Fraction(28, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "total_iocs": self.total_iocs_loaded,
                "match_count": len(self.matches),
                "artifact_type": "ioc",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    m.get("ioc_type", "UNKNOWN") for m in self.matches
                ))),
            }
        )


class IOCManager:
    """Gestiona base de datos de IOCs y realiza matching contra hallazgos forenses."""

    def __init__(self, ioc_database_path: Optional[str] = None):
        self._iocs: Dict[str, List[IOCRecord]] = {
            "hash": [],
            "filename": [],
            "registry": [],
            "ip": [],
            "domain": [],
            "technique": [],
        }
        if ioc_database_path:
            self._load_database(ioc_database_path)
        else:
            self._load_builtin_iocs()

    def _load_builtin_iocs(self) -> None:
        """Carga IOCs built-in para detección básica."""
        # Hashes SHA256 de herramientas de ataque conocidas (stubs)
        builtin = [
            IOCRecord("filename", "mimikatz.exe", "Credential Dumping", "T1003", Fraction(95, 100), "builtin", "2024-01-01", "2024-12-31"),
            IOCRecord("filename", "psexec.exe", "Lateral Movement", "T1021.002", Fraction(90, 100), "builtin", "2024-01-01", "2024-12-31"),
            IOCRecord("filename", "procdump.exe", "Credential Dumping", "T1003.001", Fraction(85, 100), "builtin", "2024-01-01", "2024-12-31"),
            IOCRecord("registry", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run\svchost", "Persistence", "T1547.001", Fraction(88, 100), "builtin", "2024-01-01", "2024-12-31"),
            IOCRecord("ip", "185.220.101.42", "C2 Infrastructure", "T1071", Fraction(92, 100), "builtin", "2024-01-01", "2024-12-31"),
            IOCRecord("domain", "evil-c2.example.com", "C2 Infrastructure", "T1071.001", Fraction(90, 100), "builtin", "2024-01-01", "2024-12-31"),
        ]
        for ioc in builtin:
            self._iocs.setdefault(ioc.ioc_type, []).append(ioc)

    def _load_database(self, path: str) -> None:
        """Carga base de datos de IOCs desde archivo JSON."""
        import json
        p = Path(path).resolve()
        if not p.exists():
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            for ioc_data in data.get("iocs", []):
                ioc = IOCRecord(
                    ioc_type=ioc_data["type"],
                    value=ioc_data["value"],
                    threat_family=ioc_data.get("threat_family", "UNKNOWN"),
                    mitre_technique=ioc_data.get("mitre_technique", ""),
                    confidence=_safe_fraction(ioc_data["confidence"]),
                    source=ioc_data.get("source", "external"),
                    first_seen=ioc_data.get("first_seen", ""),
                    last_seen=ioc_data.get("last_seen", ""),
                )
                self._iocs.setdefault(ioc.ioc_type, []).append(ioc)
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    def match_against_findings(
        self,
        findings: List[Dict[str, Any]],
        finding_type: str = "filename",
    ) -> IOCMatchResult:
        """
        Matchea hallazgos forenses contra la base de datos de IOCs.

        Args:
            findings: Lista de dicts con clave "value" para matchear.
            finding_type: Tipo de IOC a matchear (hash, filename, registry, etc.)
        """
        matches = []
        ioc_list = self._iocs.get(finding_type, [])

        for finding in findings:
            finding_value = finding.get("value", "").lower()
            for ioc in ioc_list:
                if ioc.value.lower() == finding_value:
                    matches.append({
                        "ioc_type": ioc.ioc_type,
                        "matched_value": finding_value,
                        "threat_family": ioc.threat_family,
                        "mitre_technique": ioc.mitre_technique,
                        "match_confidence": str(ioc.confidence),
                        "source": ioc.source,
                    })

        total_iocs = sum(len(v) for v in self._iocs.values())
        composite = Fraction(0, 1)
        if matches:
            composite = min(
                max(Fraction(m["match_confidence"]) for m in matches),
                Fraction(95, 100)
            )

        return IOCMatchResult(
            total_iocs_loaded=total_iocs,
            matches=matches,
            composite_score=composite,
        )

    def enrich_signal(self, signal: SignalOutput) -> SignalOutput:
        """
        Enriquece un SignalOutput con matches de IOCs si aplica.
        Stub: implementar enriquecimiento basado en metadata del signal.
        """
        return signal
