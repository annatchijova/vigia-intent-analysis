"""
vigia/engine/case_pattern_library.py

Biblioteca de patrones de casos forenses conocidos.
Permite detectar campañas de ataque comparando contra patrones históricos.

FIX P0: Validación de denominador > 0 en TODAS las operaciones de Fraction.
FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

TOOL_NAME = "CASE_PATTERN_LIBRARY"
ARTIFACT_RELIABILITY = Fraction(85, 100)


@dataclass
class CasePattern:
    pattern_name: str
    description: str
    required_signals: List[str]
    optional_signals: List[str]
    temporal_constraints: List[Dict[str, Any]]
    similarity_threshold: Fraction


@dataclass
class PatternMatchResult:
    pattern_name: str
    match_score: Fraction
    matched_signals: List[str]
    missing_signals: List[str]
    temporal_violations: List[Dict[str, Any]]


@dataclass
class CasePatternResult:
    total_patterns: int
    matches: List[PatternMatchResult]
    best_match: Optional[str]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.matches:
            best = max(m.match_score for m in self.matches)
            z = Fraction(35, 10) if best >= Fraction(9, 10) else Fraction(25, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "total_patterns": self.total_patterns,
                "match_count": len(self.matches),
                "best_match": self.best_match or "NONE",
                "artifact_type": "pattern",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    m.pattern_name for m in self.matches
                ))),
                # R7 — raw data for deterministic devil_advocate composition.
                # Fraction serialised as str (H22: no floats on the verdict path).
                # Every key here already cleared its own pattern.similarity_threshold
                # inside match() — no separate confidence filter is applied downstream.
                "missing_signals_by_pattern": {
                    m.pattern_name: m.missing_signals for m in self.matches
                },
                "match_score_by_pattern": {
                    m.pattern_name: str(m.match_score) for m in self.matches
                },
            }
        )


class CasePatternLibrary:
    """
    Biblioteca de patrones de casos forenses.

    Patrones built-in:
    - APT29 (Cozy Bear): spear-phishing + PowerShell + credential dumping
    - APT28 (Fancy Bear): exploit kit + lateral movement + data exfil
    - Ransomware: file encryption + shadow copy deletion + ransom note
    - Insider Threat: data access + USB + email exfil
    """

    def __init__(self):
        self._patterns: List[CasePattern] = self._load_builtin_patterns()

    def _load_builtin_patterns(self) -> List[CasePattern]:
        """Carga patrones built-in."""
        return [
            CasePattern(
                pattern_name="APT29_STYLE_CAMPAIGN",
                description="Spear-phishing → PowerShell → Credential Dumping → Lateral Movement",
                required_signals=["EVENT_LOG", "MEMORY_FORENSICS", "NETWORK_FORENSICS"],
                optional_signals=["REGISTRY_RTR", "BROWSER_FORENSICS"],
                temporal_constraints=[
                    {"from": "EVENT_LOG", "to": "MEMORY_FORENSICS", "max_delta_minutes": 60},
                    {"from": "MEMORY_FORENSICS", "to": "NETWORK_FORENSICS", "max_delta_minutes": 120},
                ],
                similarity_threshold=Fraction(7, 10),
            ),
            CasePattern(
                pattern_name="RANSOMWARE_ATTACK",
                description="File Encryption + Shadow Copy Deletion + Ransom Note",
                required_signals=["MFT_ANALYZER", "EVENT_LOG"],
                optional_signals=["REGISTRY_RTR", "MEMORY_FORENSICS"],
                temporal_constraints=[
                    {"from": "MFT_ANALYZER", "to": "EVENT_LOG", "max_delta_minutes": 30},
                ],
                similarity_threshold=Fraction(8, 10),
            ),
            CasePattern(
                pattern_name="INSIDER_THREAT_EXFIL",
                description="Data Access + USB Connection + Email/Network Exfiltration",
                required_signals=["USB_DEVICE_TRACKER", "NETWORK_FORENSICS"],
                optional_signals=["SHELLBAG_ANALYZER", "BROWSER_FORENSICS"],
                temporal_constraints=[
                    {"from": "SHELLBAG_ANALYZER", "to": "USB_DEVICE_TRACKER", "max_delta_minutes": 1440},
                ],
                similarity_threshold=Fraction(6, 10),
            ),
        ]

    def match(self, signals: List[SignalOutput]) -> CasePatternResult:
        """
        Matchea señales actuales contra patrones de la biblioteca.
        """
        matches: List[PatternMatchResult] = []

        for pattern in self._patterns:
            result = self._match_pattern(pattern, signals)
            if result.match_score >= pattern.similarity_threshold:
                matches.append(result)

        best = None
        if matches:
            best_match = max(matches, key=lambda m: m.match_score)
            best = best_match.pattern_name

        composite = Fraction(0, 1)
        if matches:
            composite = min(max(m.match_score for m in matches), Fraction(95, 100))

        return CasePatternResult(
            total_patterns=len(self._patterns),
            matches=matches,
            best_match=best,
            composite_score=composite,
        )

    def _match_pattern(
        self,
        pattern: CasePattern,
        signals: List[SignalOutput],
    ) -> PatternMatchResult:
        """Matchea un patrón contra señales."""
        present_tools = {s.tool_name for s in signals}

        # Señales requeridas presentes
        matched_required = [t for t in pattern.required_signals if t in present_tools]
        missing_required = [t for t in pattern.required_signals if t not in present_tools]

        # Señales opcionales presentes
        matched_optional = [t for t in pattern.optional_signals if t in present_tools]

        # Score de match: required valen más que optional
        # FIX P0: Validación de denominador > 0
        total_required = len(pattern.required_signals)
        total_optional = len(pattern.optional_signals)

        required_score = Fraction(len(matched_required), max(total_required, 1))
        optional_score = Fraction(len(matched_optional), max(total_optional, 1)) if total_optional > 0 else Fraction(0, 1)

        match_score = (
            required_score * Fraction(7, 10) +
            optional_score * Fraction(3, 10)
        )

        # Verificar constraints temporales
        temporal_violations = []
        for constraint in pattern.temporal_constraints:
            from_tool = constraint["from"]
            to_tool = constraint["to"]
            max_delta = constraint["max_delta_minutes"] * 60  # a segundos

            from_signals = [s for s in signals if s.tool_name == from_tool]
            to_signals = [s for s in signals if s.tool_name == to_tool]

            if from_signals and to_signals:
                from_ts = self._extract_timestamp(from_signals[0])
                to_ts = self._extract_timestamp(to_signals[0])
                if abs(to_ts - from_ts) > max_delta:
                    temporal_violations.append({
                        "constraint": f"{from_tool} → {to_tool}",
                        "expected_max": max_delta,
                        "actual_delta": abs(to_ts - from_ts),
                    })

        # Penalizar violaciones temporales
        if temporal_violations:
            penalty = Fraction(len(temporal_violations), max(len(pattern.temporal_constraints), 1)) * Fraction(2, 10)
            match_score = max(match_score - penalty, Fraction(0, 1))

        return PatternMatchResult(
            pattern_name=pattern.pattern_name,
            match_score=match_score,
            matched_signals=matched_required + matched_optional,
            missing_signals=missing_required,
            temporal_violations=temporal_violations,
        )

    def _extract_timestamp(self, signal: SignalOutput) -> int:
        """Extrae timestamp de signal."""
        from vigia.sift._math_utils import _parse_iso_timestamp
        ts_str = signal.metadata.get("timestamp", "1970-01-01T00:00:00Z")
        return _parse_iso_timestamp(ts_str)
