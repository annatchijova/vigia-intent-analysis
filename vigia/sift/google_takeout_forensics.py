"""
vigia/sift/google_takeout_forensics.py

Google Takeout forensic artifact analyzer for VIGÍA.
Parses JSON exports from Google Takeout: Location History, Semantic Location
History, Chrome BrowserHistory, and Google Play Store Installs.

This module analyzes evidence from a Google *account* export, not from an
operating system. The artifacts are JSON files extracted from a Takeout .zip.

Architecture: deterministic Fraction arithmetic throughout verdict path.
No floats in scoring. LLM never touches verdict.

FIX P0: All numerical values in evidence dict use Fraction/str. NEVER float.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated

logger = logging.getLogger(__name__)

TOOL_NAME = "GOOGLE_TAKEOUT_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(65, 100)  # JSON export, no binary checksums

# ──────────────────────────────────────────────────────────────────────────────
# CATALOGS
# ──────────────────────────────────────────────────────────────────────────────

# Sorted by severity descending — break gets highest match
SUSPICIOUS_SEARCH_PATTERNS: List[Tuple[str, Fraction, str]] = [
    (r"(?i)cve-\d{4}-\d+|exploit|metasploit|payload", Fraction(85, 100), "T1203"),
    (r"(?i)log4shell|log4j", Fraction(85, 100), "T1190"),
    (r"(?i)how\s+to\s+hack", Fraction(75, 100), "T1595"),
    (r"(?i)delete.*history|clear.*cache|wipe.*phone", Fraction(70, 100), "T1070"),
    (r"(?i)what\s+to\s+do\s+if\s+.*hacked", Fraction(65, 100), "T1592"),
    (r"(?i)burner\s+phone|prepaid.*anonymous", Fraction(65, 100), "T1583"),
    (r"(?i)fix.*hacked.*computer", Fraction(60, 100), "T1592"),
    (r"(?i)kali\s+linux|parrot\s+os|pentesting", Fraction(60, 100), "T1588.002"),
    (r"(?i)computer\s+fix\s+near\s+me", Fraction(55, 100), "T1592"),
    (r"(?i)whatsmyip|what.*my.*ip", Fraction(50, 100), "T1590"),
    (r"(?i)vpn|proxy|tor\s+browser", Fraction(45, 100), "T1090"),
    (r"(?i)signal\s+messenger|wire\s+app|wickr|briar", Fraction(35, 100), "T1573"),
]

# Installed app title patterns — matched against Google Play Store Installs.json
# Takeout uses display titles (not bundle IDs), so we match by title regex.
# Sorted by severity descending.
SUSPICIOUS_INSTALLED_APPS: List[Tuple[str, Fraction, str, str]] = [
    # (pattern, severity, MITRE TTP, description)
    (r"(?i)^root\s*checker", Fraction(60, 100), "T1398", "Root verification tool"),
    (r"(?i)^termux$", Fraction(55, 100), "T1059", "Terminal emulator on mobile"),
    (r"(?i)exif.*editor|metadata.*editor", Fraction(50, 100), "T1070", "Metadata editing — anti-forensic capability"),
    (r"(?i)hacker.*keyboard", Fraction(40, 100), "T1059", "Terminal-oriented keyboard"),
]

# Minimum gap (in seconds) to flag as a location history gap.
# 24 hours — shorter gaps are normal (sleep, indoors, battery saver).
_LOCATION_GAP_THRESHOLD_SECS = 86400

# Known Takeout artifact markers for validation
_TAKEOUT_MARKER_FILES = {
    "Location History.json",
    "BrowserHistory.json",
    "Installs.json",
    "Hangouts.json",
}


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TakeoutFinding:
    finding_type: str
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""


@dataclass
class TakeoutAnalysisResult:
    """Result of Google Takeout forensic analysis."""
    source_path: str = ""
    account_email: str = ""
    device_model: str = ""
    total_location_points: int = 0
    total_semantic_places: int = 0
    user_confirmed_places: int = 0
    total_browser_entries: int = 0
    total_installed_apps: int = 0
    location_date_range: str = ""
    location_unique_days: int = 0
    location_gaps: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[TakeoutFinding] = field(default_factory=list)
    opsec_indicators: List[Dict[str, Any]] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)

        n_opsec = len(self.opsec_indicators)
        has_exploit_research = any(
            f.finding_type == "BROWSER_EXPLOIT_RESEARCH" for f in self.findings
        )
        has_suspicious_search = any(
            f.finding_type == "BROWSER_SUSPICIOUS" for f in self.findings
        )
        has_suspicious_app = any(
            f.finding_type == "SUSPICIOUS_INSTALLED_APP" for f in self.findings
        )
        has_root_tool = any(
            f.finding_type == "ROOT_TOOL_INSTALLED" for f in self.findings
        )
        has_location_gap = any(
            f.finding_type == "LOCATION_HISTORY_GAP" for f in self.findings
        )

        # Opsec bump (same pattern as Android/iOS/macOS — BUG-011 fix)
        opsec_bump = Fraction(0)
        if n_opsec >= 3:
            opsec_bump = Fraction(4, 10)
        elif n_opsec >= 2:
            opsec_bump = Fraction(2, 10)

        # Z-score escalation ladder — deterministic, no floats
        if has_exploit_research and has_root_tool:
            z = Fraction(38, 10)
        elif has_exploit_research:
            z = Fraction(35, 10)
        elif has_root_tool and has_suspicious_search and has_location_gap:
            z = Fraction(30, 10)
        elif has_root_tool and has_suspicious_search:
            z = Fraction(28, 10)
        elif has_root_tool and has_suspicious_app:
            z = Fraction(24, 10)
        elif has_suspicious_search and has_location_gap:
            z = Fraction(22, 10)
        elif has_root_tool:
            z = Fraction(20, 10)
        elif has_suspicious_search:
            z = Fraction(18, 10)
        elif has_suspicious_app and has_location_gap:
            z = Fraction(16, 10)
        elif self.findings:
            z = Fraction(12, 10)

        z = min(z + opsec_bump, Fraction(int(Z_CLIP_MAX), 1))
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))

        # SignalOutput boundary: Fraction → float (same as all other SIFT modules)
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip) if z_clip > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "account_email": self.account_email,
                "device_model": self.device_model,
                "total_location_points": self.total_location_points,
                "total_semantic_places": self.total_semantic_places,
                "user_confirmed_places": self.user_confirmed_places,
                "total_browser_entries": self.total_browser_entries,
                "total_installed_apps": self.total_installed_apps,
                "location_date_range": self.location_date_range,
                "location_unique_days": self.location_unique_days,
                "location_gaps_count": len(self.location_gaps),
                "opsec_indicators_count": n_opsec,
                "findings_count": len(self.findings),
                "composite_score": str(self.composite_score),
                "artifact_type": "google_takeout",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "chains": n_opsec,
                "finding_types": sorted(list(set(
                    f.finding_type for f in self.findings
                ))),
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

class GoogleTakeoutForensicsAnalyzer:
    """
    Analyzes Google Takeout exports.

    Expects a directory containing the extracted Takeout .zip. The evidence
    root may be the Takeout/ folder itself or a parent containing it.
    Typical structure:
      Takeout/
        Location History/Location History.json
        Location History/Semantic Location History/YYYY/YYYY_MONTH.json
        Chrome/BrowserHistory.json
        Google Play Store/Installs.json
        Hangouts/Hangouts.json
    """

    def __init__(self):
        self._findings: List[TakeoutFinding] = []
        self._opsec_indicators: List[Dict[str, Any]] = []

    def analyze(
        self,
        evidence_path: Path,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> TakeoutAnalysisResult:
        self._findings = []
        self._opsec_indicators = []

        evidence_path = Path(evidence_path)
        if not evidence_path.is_dir():
            logger.warning("[TAKEOUT] Evidence path is not a directory: %s", evidence_path)
            return TakeoutAnalysisResult(
                source_path=str(evidence_path),
                analysis_notes=["Evidence path is not a directory."],
            )

        result = TakeoutAnalysisResult(source_path=str(evidence_path))

        # Resolve Takeout root — may be evidence_path itself or a child
        takeout_root = self._resolve_takeout_root(evidence_path)
        if takeout_root is None:
            logger.warning("[TAKEOUT] No Takeout structure found in %s", evidence_path)
            result.analysis_notes.append(
                "No Google Takeout artifacts found. Directory may not contain "
                "a Takeout export."
            )
            return result

        # Validate Takeout markers
        all_files = {f.name for f in takeout_root.rglob("*")
                     if f.is_file() and not f.is_symlink()}
        takeout_markers = all_files & _TAKEOUT_MARKER_FILES
        if not takeout_markers:
            result.analysis_notes.append(
                "No Takeout-specific markers found (Location History.json, "
                "BrowserHistory.json, etc.)."
            )

        # 1. Location History
        lh_path = takeout_root / "Location History" / "Location History.json"
        if lh_path.is_file():
            try:
                self._analyze_location_history(lh_path, result)
            except Exception as e:
                logger.error("[TAKEOUT] Location History analysis failed: %s", e)
                result.analysis_notes.append(f"Location History parse error: {e}")

        # 2. Semantic Location History (multiple files, glob recursivo)
        slh_dir = takeout_root / "Location History" / "Semantic Location History"
        if slh_dir.is_dir():
            for slh_file in sorted(slh_dir.rglob("*.json")):
                if slh_file.is_symlink():
                    continue
                try:
                    self._analyze_semantic_location(slh_file, result)
                except Exception as e:
                    logger.error(
                        "[TAKEOUT] Semantic Location analysis failed for %s: %s",
                        slh_file.name, e,
                    )
                    result.analysis_notes.append(
                        f"Semantic Location parse error ({slh_file.name}): {e}"
                    )

        # 3. Chrome Browser History
        bh_path = takeout_root / "Chrome" / "BrowserHistory.json"
        if bh_path.is_file():
            try:
                self._analyze_browser_history(bh_path, result)
            except Exception as e:
                logger.error("[TAKEOUT] Browser History analysis failed: %s", e)
                result.analysis_notes.append(f"Browser History parse error: {e}")

        # 4. Installed Apps (Google Play Store)
        installs_path = takeout_root / "Google Play Store" / "Installs.json"
        if installs_path.is_file():
            try:
                self._analyze_installed_apps(installs_path, result)
            except Exception as e:
                logger.error("[TAKEOUT] Installs analysis failed: %s", e)
                result.analysis_notes.append(f"Installs parse error: {e}")

        # 5. My Activity — HTML, not JSON
        # TODO: implement _analyze_my_activity (requires HTML parsing;
        #       My Activity/Search/MyActivity.html, My Activity/Chrome/MyActivity.html,
        #       etc. — each contains timestamped activity records)

        # 6. Mail — *.mbox
        # TODO: implement _analyze_mail (requires mailbox module from stdlib;
        #       parse .mbox files for email metadata, sender/recipient patterns)

        # 7. Hangouts — stub for future use
        # Hangouts.json in this corpus is empty ({"conversations": []}).
        # A full implementation would parse conversation participants, message
        # content, and timestamps. Deferred until corpus with real data.

        # 8. OPSEC assessment
        self._assess_opsec(result)

        # Assign findings
        result.findings = self._findings
        result.opsec_indicators = self._opsec_indicators

        # Compute composite score with correlation groups (P0-003 fix)
        if self._findings:
            severities = [f.severity for f in self._findings]
            corr_groups = self._build_correlation_groups()
            result.composite_score = noisy_or_correlated(
                severities, corr_groups, Fraction(15, 100)
            )
        else:
            result.composite_score = Fraction(0)

        return result

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_takeout_root(evidence_path: Path) -> Optional[Path]:
        """Find the Takeout root directory.

        The evidence_path may be:
        - The Takeout/ directory itself
        - A parent containing a Takeout/ subdirectory
        - A directory with Takeout artifacts directly (no Takeout/ wrapper)
        """
        # Direct: evidence_path IS the Takeout dir
        if evidence_path.name == "Takeout":
            return evidence_path

        # One level down: evidence_path/Takeout/
        candidate = evidence_path / "Takeout"
        if candidate.is_dir():
            return candidate

        # No Takeout wrapper — check if artifacts are at root level
        for marker in _TAKEOUT_MARKER_FILES:
            matches = list(evidence_path.rglob(marker))
            if matches:
                return evidence_path

        return None

    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; canonical semantics live there)."""
        return build_correlation_groups([f.corr_group for f in self._findings])

    @staticmethod
    def _safe_json_load(path: Path, max_bytes: int = 50_000_000) -> Optional[Any]:
        """Load a JSON file with size guard."""
        try:
            size = path.stat().st_size
            if size > max_bytes:
                logger.warning(
                    "[TAKEOUT] JSON file too large (%d bytes): %s", size, path
                )
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("[TAKEOUT] Cannot load JSON %s: %s", path, e)
            return None

    # ── Location History ───────────────────────────────────────────────────

    def _analyze_location_history(
        self, lh_path: Path, result: TakeoutAnalysisResult
    ) -> None:
        """Analyze Location History.json.

        Schema: {"locations": [{
            "timestampMs": "1583370610621",  (epoch milliseconds, STRING)
            "latitudeE7": 444738218,         (divide by 1e7 for degrees)
            "longitudeE7": -732032782,
            "accuracy": 16,
            "activity": [{"timestampMs": "...", "activity": [{type, confidence}]}]
        }, ...]}
        """
        data = self._safe_json_load(lh_path)
        if data is None:
            result.analysis_notes.append(
                f"Location History: could not load {lh_path}"
            )
            return

        locations = data.get("locations", [])
        if not isinstance(locations, list):
            result.analysis_notes.append("Location History: 'locations' is not a list")
            return

        result.total_location_points = len(locations)
        if not locations:
            return

        # Extract timestamps (milliseconds → seconds)
        timestamps_secs: List[int] = []
        for loc in locations:
            ts_ms = loc.get("timestampMs")
            if ts_ms is not None:
                try:
                    timestamps_secs.append(int(ts_ms) // 1000)
                except (ValueError, TypeError):
                    continue

        if not timestamps_secs:
            result.analysis_notes.append(
                "Location History: no valid timestamps found"
            )
            return

        timestamps_secs.sort()

        # Date range and unique days
        from datetime import datetime, timezone
        first_ts = timestamps_secs[0]
        last_ts = timestamps_secs[-1]
        first_dt = datetime.fromtimestamp(first_ts, tz=timezone.utc)
        last_dt = datetime.fromtimestamp(last_ts, tz=timezone.utc)
        result.location_date_range = (
            f"{first_dt.strftime('%Y-%m-%d')} to {last_dt.strftime('%Y-%m-%d')}"
        )

        unique_days = set()
        for ts in timestamps_secs:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            unique_days.add(dt.date())
        result.location_unique_days = len(unique_days)

        # Detect gaps in the INTERIOR of the coverage period.
        # Only between first and last timestamp — edges are not gaps.
        gaps: List[Dict[str, Any]] = []
        for i in range(1, len(timestamps_secs)):
            delta = timestamps_secs[i] - timestamps_secs[i - 1]
            if delta >= _LOCATION_GAP_THRESHOLD_SECS:
                gap_start_dt = datetime.fromtimestamp(
                    timestamps_secs[i - 1], tz=timezone.utc
                )
                gap_end_dt = datetime.fromtimestamp(
                    timestamps_secs[i], tz=timezone.utc
                )
                gap_hours = delta / 3600
                gaps.append({
                    "start": gap_start_dt.isoformat(),
                    "end": gap_end_dt.isoformat(),
                    "duration_hours": round(gap_hours, 1),
                })

        result.location_gaps = gaps

        if gaps:
            # Report as a single finding with summary of all gaps
            longest_gap = max(gaps, key=lambda g: g["duration_hours"])
            self._findings.append(TakeoutFinding(
                finding_type="LOCATION_HISTORY_GAP",
                severity=Fraction(35, 100),
                description=(
                    f"{len(gaps)} gap(s) >24h in location history; "
                    f"longest: {longest_gap['duration_hours']}h"
                ),
                evidence=(
                    f"Longest gap: {longest_gap['start']} to {longest_gap['end']} "
                    f"({longest_gap['duration_hours']}h) | "
                    f"Total gaps: {len(gaps)}"
                ),
                mitre_technique="T1070",
                rule_ref="TAKEOUT-LOC-GAP",
                corr_group="location_gaps",
            ))

        # Extract device model from first entry with deviceTag or activity
        # (not always available — device info comes from Installs.json)

    # ── Semantic Location History ──────────────────────────────────────────

    def _analyze_semantic_location(
        self, slh_path: Path, result: TakeoutAnalysisResult
    ) -> None:
        """Analyze a Semantic Location History JSON file.

        Schema: {"timelineObjects": [{
            "placeVisit": {
                "location": {
                    "latitudeE7": ..., "longitudeE7": ...,
                    "name": "Champlain College",
                    "address": "163 S Willard St...",
                    "placeId": "ChIJ...",
                    "locationConfidence": 100.0
                },
                "duration": {
                    "startTimestampMs": "1583370610000",
                    "endTimestampMs": "1583423908000"
                },
                "placeConfidence": "USER_CONFIRMED",
                "visitConfidence": 100,
                "otherCandidateLocations": [...]
            }
        }, ...]}

        Multiple files exist — one per month (e.g., 2020_MARCH.json).
        This method is called once per file; counters accumulate.
        """
        data = self._safe_json_load(slh_path)
        if data is None:
            result.analysis_notes.append(
                f"Semantic Location: could not load {slh_path.name}"
            )
            return

        timeline_objects = data.get("timelineObjects", [])
        if not isinstance(timeline_objects, list):
            return

        for obj in timeline_objects:
            place_visit = obj.get("placeVisit")
            if not isinstance(place_visit, dict):
                continue

            result.total_semantic_places += 1

            place_confidence = place_visit.get("placeConfidence", "")
            if place_confidence == "USER_CONFIRMED":
                result.user_confirmed_places += 1

    # ── Browser History ────────────────────────────────────────────────────

    def _analyze_browser_history(
        self, bh_path: Path, result: TakeoutAnalysisResult
    ) -> None:
        """Analyze Chrome/BrowserHistory.json.

        Schema: {"Browser History": [{
            "page_transition": "LINK",
            "title": "Page Title",
            "url": "http://...",
            "client_id": "...",
            "time_usec": 1585007602037581  (epoch MICROSECONDS, integer)
        }, ...]}
        """
        data = self._safe_json_load(bh_path)
        if data is None:
            result.analysis_notes.append(
                f"Browser History: could not load {bh_path}"
            )
            return

        entries = data.get("Browser History", [])
        if not isinstance(entries, list):
            result.analysis_notes.append(
                "Browser History: 'Browser History' key is not a list"
            )
            return

        result.total_browser_entries = len(entries)

        for entry in entries:
            url = str(entry.get("url", ""))
            title = str(entry.get("title", ""))
            time_usec = entry.get("time_usec", 0)

            try:
                ts = int(time_usec) // 1_000_000  # microseconds → seconds
            except (ValueError, TypeError):
                ts = 0

            combined = f"{url[:500]} {title[:200]}"  # ReDoS guard

            for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                if re.search(pattern, combined):
                    finding_type = (
                        "BROWSER_EXPLOIT_RESEARCH"
                        if severity >= Fraction(80, 100)
                        else "BROWSER_SUSPICIOUS"
                    )
                    self._findings.append(TakeoutFinding(
                        finding_type=finding_type,
                        severity=severity,
                        description="Browser history matches suspicious pattern",
                        evidence=(
                            f"URL: {url[:150]}"
                            + ("[truncated]" if len(url) > 150 else "")
                            + f" | Title: {title[:100]}"
                        ),
                        mitre_technique=mitre,
                        rule_ref="TAKEOUT-BROWSER-SUSP",
                        timestamp=ts,
                        corr_group="browser_suspicious",
                    ))
                    break  # Highest severity first

    # ── Installed Apps ─────────────────────────────────────────────────────

    def _analyze_installed_apps(
        self, installs_path: Path, result: TakeoutAnalysisResult
    ) -> None:
        """Analyze Google Play Store/Installs.json.

        Schema: [{"install": {
            "doc": {"documentType": "Android Apps", "title": "App Name"},
            "firstInstallationTime": "2020-01-21T17:20:20.002010Z",
            "deviceAttribute": {
                "model": "Pixel 3",
                "carrier": "T-Mobile - US",
                "manufacturer": "Google",
                ...
            }
        }}, ...]
        """
        data = self._safe_json_load(installs_path)
        if data is None:
            result.analysis_notes.append(
                f"Installs: could not load {installs_path}"
            )
            return

        if not isinstance(data, list):
            result.analysis_notes.append("Installs: top-level is not a list")
            return

        result.total_installed_apps = len(data)

        # Extract device model from first entry
        if data and not result.device_model:
            first_install = data[0].get("install", {})
            dev_attr = first_install.get("deviceAttribute", {})
            model = dev_attr.get("model", "")
            manufacturer = dev_attr.get("manufacturer", "")
            if model:
                result.device_model = (
                    f"{manufacturer} {model}" if manufacturer else model
                )

        for item in data:
            install = item.get("install", {})
            doc = install.get("doc", {})
            title = str(doc.get("title", ""))
            if not title:
                continue

            for pattern, severity, mitre, desc in SUSPICIOUS_INSTALLED_APPS:
                if re.search(pattern, title):
                    finding_type = (
                        "ROOT_TOOL_INSTALLED"
                        if mitre == "T1398"
                        else "SUSPICIOUS_INSTALLED_APP"
                    )
                    self._findings.append(TakeoutFinding(
                        finding_type=finding_type,
                        severity=severity,
                        description=f"Installed: {title} — {desc}",
                        evidence=f"App: {title[:150]}",
                        mitre_technique=mitre,
                        rule_ref="TAKEOUT-APP-SUSP",
                        corr_group="suspicious_apps",
                    ))
                    break  # One finding per app

    # ── OPSEC Assessment ───────────────────────────────────────────────────

    def _assess_opsec(self, result: TakeoutAnalysisResult) -> None:
        n_suspicious_apps = sum(
            1 for f in self._findings
            if f.finding_type in ("SUSPICIOUS_INSTALLED_APP", "ROOT_TOOL_INSTALLED")
        )
        has_root_tool = any(
            f.finding_type == "ROOT_TOOL_INSTALLED" for f in self._findings
        )
        has_location_gap = any(
            f.finding_type == "LOCATION_HISTORY_GAP" for f in self._findings
        )

        if n_suspicious_apps >= 3:
            self._opsec_indicators.append({
                "indicator": "MULTI_SUSPICIOUS_APPS",
                "severity": str(Fraction(65, 100)),
                "description": f"{n_suspicious_apps} suspicious apps installed",
            })

        if has_root_tool and n_suspicious_apps >= 2:
            self._opsec_indicators.append({
                "indicator": "ROOT_PLUS_TOOLS",
                "severity": str(Fraction(70, 100)),
                "description": "Root checker + other suspicious tools installed",
            })
            self._findings.append(TakeoutFinding(
                finding_type="OPSEC_ROOT_TOOLCHAIN",
                severity=Fraction(65, 100),
                description=(
                    "Root verification tool + additional suspicious apps — "
                    "technical capability posture"
                ),
                evidence=f"root_tool=True, suspicious_apps={n_suspicious_apps}",
                mitre_technique="T1398",
                rule_ref="TAKEOUT-OPSEC-ROOT",
                corr_group="suspicious_apps",
            ))

        if has_location_gap and has_root_tool:
            self._opsec_indicators.append({
                "indicator": "ROOT_PLUS_LOCATION_GAPS",
                "severity": str(Fraction(60, 100)),
                "description": "Root tool + location history gaps — possible data manipulation",
            })
