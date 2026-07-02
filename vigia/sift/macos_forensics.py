"""
vigia/sift/macos_forensics.py

macOS forensic artifact analyzer for VIGÍA.
Parses SQLite databases (Safari History.db, QuarantineEventsV2, KnowledgeC.db,
TCC.db), plist files, and filesystem artifacts from macOS disk images
(E01, dd, APFS snapshots) or logical extractions.

Architecture: deterministic Fraction arithmetic throughout verdict path.
No floats in scoring. LLM never touches verdict.

FIX P0: All numerical values in evidence dict use Fraction/str. NEVER float.
"""

from __future__ import annotations

import logging
import plistlib
import re
import sqlite3
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated

logger = logging.getLogger(__name__)

TOOL_NAME = "MACOS_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(70, 100)

# Core Data Reference Date: 2001-01-01 00:00:00 UTC in Unix epoch
_COREDATA_EPOCH_OFFSET = 978307200

# ──────────────────────────────────────────────────────────────────────────────
# CATALOGS — severity in Fraction, MITRE TTP, description
# Ordered by severity DESCENDING so break-on-first-match gets highest severity
# ──────────────────────────────────────────────────────────────────────────────

ENCRYPTED_APPS: Dict[str, Tuple[str, Fraction]] = {
    "com.wickr.desktop":            ("Wickr — E2E + auto-destruct", Fraction(80, 100)),
    "org.whispersystems.signal-desktop": ("Signal Desktop — E2E encrypted messaging", Fraction(60, 100)),
    "ch.protonmail.desktop":        ("ProtonMail Desktop — encrypted email", Fraction(55, 100)),
    "com.wire":                     ("Wire — E2E encrypted messaging", Fraction(60, 100)),
    "com.tencent.xinWeChat":        ("WeChat — messaging", Fraction(50, 100)),
    "org.telegram.desktop":         ("Telegram Desktop — optional E2E", Fraction(45, 100)),
    "com.facebook.Messenger":       ("Messenger — optional E2E", Fraction(20, 100)),
    "com.getbrave.browser":         ("Brave — privacy-focused browser", Fraction(30, 100)),
    "org.torproject.torbrowser":    ("Tor Browser — anonymized browsing", Fraction(75, 100)),
}

# Sorted by severity descending — break gets highest match
SUSPICIOUS_SEARCH_PATTERNS: List[Tuple[str, Fraction, str]] = [
    (r"(?i)cve-\d{4}-\d+|exploit|metasploit|payload", Fraction(85, 100), "T1203"),
    (r"(?i)log4shell|log4j", Fraction(85, 100), "T1190"),
    (r"(?i)how\s+to\s+hack", Fraction(75, 100), "T1595"),
    (r"(?i)delete.*history|clear.*cache|wipe.*disk|secure.*erase", Fraction(70, 100), "T1070"),
    (r"(?i)what\s+to\s+do\s+if\s+.*hacked", Fraction(65, 100), "T1592"),
    (r"(?i)burner\s+phone|prepaid.*anonymous", Fraction(65, 100), "T1583"),
    (r"(?i)fix.*hacked.*computer", Fraction(60, 100), "T1592"),
    (r"(?i)kali\s+linux|parrot\s+os|pentesting", Fraction(60, 100), "T1588.002"),
    (r"(?i)computer\s+fix\s+near\s+me", Fraction(55, 100), "T1592"),
    (r"(?i)whatsmyip|what.*my.*ip", Fraction(50, 100), "T1590"),
    (r"(?i)vpn|proxy|tor\s+browser", Fraction(45, 100), "T1090"),
    (r"(?i)signal\s+messenger|wire\s+app|wickr|briar", Fraction(35, 100), "T1573"),
]

# macOS-specific anti-forensic search patterns
ANTIFORENSIC_SEARCH_PATTERNS: List[Tuple[str, Fraction, str]] = [
    (r"(?i)srm\b|secure.?rm|shred|bleachbit", Fraction(75, 100), "T1070.004"),
    (r"(?i)disable.*sip|csrutil|rootless", Fraction(80, 100), "T1562.001"),
    (r"(?i)hide.*file|chflags.*hidden|\.DS_Store", Fraction(40, 100), "T1564.001"),
    (r"(?i)diskutil.*erase|disk.*wipe", Fraction(70, 100), "T1485"),
    (r"(?i)privacy.*tcc|full.*disk.*access|bypass.*gatekeeper", Fraction(65, 100), "T1553.001"),
]

# Known macOS artifact markers for validation
_MACOS_MARKER_FILES = {
    # Safari
    "History.db",
    # Quarantine events (Gatekeeper)
    "com.apple.LaunchServices.QuarantineEventsV2",
    # Application usage (KnowledgeC)
    "knowledgeC.db",
    # Privacy/permissions
    "TCC.db",
    # System logs
    "system.log",
    # FSEvents
    ".fseventsd",
    # Spotlight
    ".Spotlight-V100",
    # Plists (generic but ubiquitous)
    "com.apple.loginitems.plist",
    "com.apple.recentitems.plist",
    "SystemVersion.plist",
}


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MacOSFinding:
    finding_type: str
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""


@dataclass
class MacOSAnalysisResult:
    """Result of macOS forensic analysis."""
    source_path: str = ""
    hostname: str = ""
    macos_version: str = ""
    owner_name: str = ""
    total_safari_entries: int = 0
    total_quarantine_events: int = 0
    encrypted_apps: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[MacOSFinding] = field(default_factory=list)
    opsec_indicators: List[Dict[str, Any]] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)

        n_encrypted = len(self.encrypted_apps)
        n_opsec = len(self.opsec_indicators)
        has_suspicious_search = any(
            f.finding_type.startswith("SAFARI_SUSPICIOUS") for f in self.findings
        )
        has_exploit_research = any(
            f.finding_type == "SAFARI_EXPLOIT_RESEARCH" for f in self.findings
        )
        has_antiforensic = any(
            f.finding_type.startswith("ANTIFORENSIC") for f in self.findings
        )
        has_quarantine_suspicious = any(
            f.finding_type == "QUARANTINE_SUSPICIOUS_SOURCE" for f in self.findings
        )
        has_sip_disabled = any(
            f.finding_type == "SIP_DISABLED" for f in self.findings
        )

        # Opsec bump (same pattern as iOS/Android — BUG-011 fix)
        opsec_bump = Fraction(0)
        if n_opsec >= 3:
            opsec_bump = Fraction(4, 10)
        elif n_opsec >= 2:
            opsec_bump = Fraction(2, 10)

        # Z-score escalation ladder — deterministic, no floats
        if has_exploit_research and has_antiforensic:
            z = Fraction(38, 10)
        elif has_exploit_research:
            z = Fraction(35, 10)
        elif has_antiforensic and n_encrypted >= 2 and has_sip_disabled:
            z = Fraction(34, 10)
        elif n_encrypted >= 3 and has_suspicious_search:
            z = Fraction(30, 10)
        elif has_antiforensic and n_encrypted >= 2:
            z = Fraction(28, 10)
        elif n_encrypted >= 3:
            z = Fraction(24, 10)
        elif has_sip_disabled and has_antiforensic:
            z = Fraction(24, 10)
        elif n_encrypted >= 2:
            z = Fraction(20, 10)
        elif has_suspicious_search and has_quarantine_suspicious:
            z = Fraction(18, 10)
        elif has_suspicious_search:
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
                "hostname": self.hostname,
                "macos_version": self.macos_version,
                "owner_name": self.owner_name,
                "total_safari_entries": self.total_safari_entries,
                "total_quarantine_events": self.total_quarantine_events,
                "encrypted_apps_count": n_encrypted,
                "opsec_indicators_count": n_opsec,
                "findings_count": len(self.findings),
                "composite_score": str(self.composite_score),
                "artifact_type": "macos_forensic",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "chains": n_encrypted + n_opsec,
                "finding_types": sorted(list(set(
                    f.finding_type for f in self.findings
                ))),
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

class MacOSForensicsAnalyzer:
    """
    Analyzes macOS forensic extractions.

    Expects a directory containing macOS filesystem artifacts from a disk image
    mount, logical extraction, or APFS snapshot. Typical structure:
      /private/var/db/  — QuarantineEventsV2, TCC.db
      /Users/<user>/Library/Safari/  — History.db
      /Users/<user>/Library/Application Support/  — app data
      /System/Library/CoreServices/  — SystemVersion.plist
    """

    def __init__(self):
        self._findings: List[MacOSFinding] = []
        self._encrypted_apps: List[Dict[str, Any]] = []
        self._opsec_indicators: List[Dict[str, Any]] = []

    def analyze(
        self,
        evidence_path: Path,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> MacOSAnalysisResult:
        self._findings = []
        self._encrypted_apps = []
        self._opsec_indicators = []

        evidence_path = Path(evidence_path)
        if not evidence_path.is_dir():
            logger.warning("[MACOS] Evidence path is not a directory: %s", evidence_path)
            return MacOSAnalysisResult(
                source_path=str(evidence_path),
                analysis_notes=["Evidence path is not a directory."],
            )

        result = MacOSAnalysisResult(source_path=str(evidence_path))

        # Validate macOS evidence
        all_files = set()
        all_dirs = set()
        for p in evidence_path.rglob("*"):
            if p.is_symlink():
                continue
            if p.is_file():
                all_files.add(p.name)
            elif p.is_dir():
                all_dirs.add(p.name)
        macos_markers = (all_files | all_dirs) & _MACOS_MARKER_FILES
        if not macos_markers:
            logger.warning("[MACOS] No macOS artifacts found in %s", evidence_path)
            result.analysis_notes.append(
                "No macOS-specific artifacts found. Directory may not contain macOS evidence."
            )

        # 1. System identification — version, hostname, owner
        self._identify_system(evidence_path, result)

        # 2. Safari history (SQLite — same schema as iOS Safari)
        for db in self._safe_rglob(evidence_path, "History.db", limit=5):
            # Only process Safari History.db, not Chrome/other browsers
            if "Safari" not in str(db):
                continue
            try:
                self._analyze_safari(db, result)
            except Exception as e:
                logger.error("[MACOS] Safari analysis failed: %s", e)
                result.analysis_notes.append(f"Safari parse error: {e}")

        # 3. Quarantine events (Gatekeeper download tracking)
        for db in self._safe_rglob(
            evidence_path,
            "com.apple.LaunchServices.QuarantineEventsV2",
            limit=3,
        ):
            try:
                self._analyze_quarantine(db, result)
            except Exception as e:
                logger.error("[MACOS] Quarantine analysis failed: %s", e)
                result.analysis_notes.append(f"Quarantine parse error: {e}")

        # 4. App detection (installed apps)
        self._detect_installed_apps(evidence_path, result)

        # 5. TCC.db — privacy permissions
        # TODO: implement _analyze_tcc (SQLite, schema: access table with
        #       service, client, auth_value columns)
        # for db in self._safe_rglob(evidence_path, "TCC.db", limit=3):
        #     self._analyze_tcc(db, result)

        # 6. KnowledgeC.db — app usage and screen time
        # TODO: implement _analyze_knowledgec (SQLite, Core Data epoch timestamps,
        #       ZOBJECT table with ZSTREAMNAME, ZVALUESTRING, ZCREATIONDATE)
        # for db in self._safe_rglob(evidence_path, "knowledgeC.db", limit=2):
        #     self._analyze_knowledgec(db, result)

        # 7. Plist analysis — login items, LaunchAgents, app preferences
        try:
            self._analyze_plists(evidence_path, result)
        except Exception as e:
            logger.error("[MACOS] Plist analysis failed: %s", e)
            result.analysis_notes.append(f"Plist analysis error: {e}")

        # 8. FSEvents — filesystem event journal
        # TODO: implement _analyze_fsevents (binary format, requires dedicated
        #       parser — consider python-fsevents or manual struct.unpack;
        #       look for file deletion clusters, .Trash patterns, timestamp gaps)
        # self._analyze_fsevents(evidence_path, result)

        # 9. OPSEC assessment
        self._assess_opsec(result)

        # Assign findings
        result.findings = self._findings
        result.encrypted_apps = self._encrypted_apps
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
    def _safe_rglob(base: Path, pattern: str, limit: int = 5) -> List[Path]:
        """rglob with symlink filtering, deterministic sort, and limit."""
        if not base.is_dir():
            return []
        return [f for f in sorted(base.rglob(pattern), key=lambda p: str(p))
                if not f.is_symlink() and f.is_file()][:limit]

    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; replaces List[List[int]] format)."""
        return build_correlation_groups([f.corr_group for f in self._findings])

    @staticmethod
    def _coredata_to_unix(ts: int) -> int:
        """Convert Core Data timestamp (since 2001-01-01) to Unix epoch.
        2024 magnitudes: nanos ~7.3e17, micros ~7.3e14, millis ~7.3e11, secs ~7.3e8."""
        if ts is None or ts <= 0:
            return 0
        if ts > 100_000_000_000_000_000:   # nanoseconds
            ts = ts // 1_000_000_000
        elif ts > 100_000_000_000_000:     # microseconds
            ts = ts // 1_000_000
        elif ts > 100_000_000_000:         # milliseconds
            ts = ts // 1_000
        return ts + _COREDATA_EPOCH_OFFSET

    @staticmethod
    def _cocoa_ts_to_unix(ts: float) -> int:
        """Convert Cocoa/CFAbsoluteTime (seconds since 2001-01-01) to Unix epoch.
        Used by QuarantineEventsV2 timestamps."""
        if ts is None or ts <= 0:
            return 0
        return int(ts) + _COREDATA_EPOCH_OFFSET

    @staticmethod
    def _safe_sqlite_connect(db_path: Path) -> Optional[sqlite3.Connection]:
        """Connect to SQLite with proper error handling (BUG-003 fix)."""
        try:
            return sqlite3.connect(str(db_path))
        except (sqlite3.Error, OSError) as e:
            logger.error("[MACOS] Cannot open SQLite database %s: %s", db_path, e)
            return None

    # ── System Identification ──────────────────────────────────────────────

    def _identify_system(self, evidence_path: Path, result: MacOSAnalysisResult) -> None:
        """Extract macOS version, hostname, and owner from SystemVersion.plist
        and other system artifacts. plistlib.load() autodetects binary/XML."""
        for sv in self._safe_rglob(evidence_path, "SystemVersion.plist", limit=2):
            try:
                with open(sv, "rb") as f:
                    plist = plistlib.load(f)
                version = plist.get("ProductVersion", "")
                build = plist.get("ProductBuildVersion", "")
                if version:
                    result.macos_version = f"{version} ({build})" if build else version
            except (OSError, plistlib.InvalidFileException) as e:
                result.analysis_notes.append(
                    f"SystemVersion.plist: could not parse {sv}: {e}"
                )

    # ── Safari ─────────────────────────────────────────────────────────────

    def _analyze_safari(self, db_path: Path, result: MacOSAnalysisResult) -> None:
        """Analyze Safari History.db — identical SQLite schema to iOS Safari.

        Tables: history_items (id, url, visit_count, ...) joined to
                history_visits (history_item, visit_time) via id→history_item.
        visit_time is Core Data epoch (seconds since 2001-01-01).
        """
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"Safari: could not open {db_path}")
            return
        try:
            conn.row_factory = sqlite3.Row
            try:
                count = conn.execute("SELECT COUNT(*) FROM history_items").fetchone()[0]
                result.total_safari_entries = count
            except sqlite3.OperationalError:
                result.analysis_notes.append("Safari: 'history_items' table not found")
                return

            try:
                rows = conn.execute(
                    "SELECT hi.url, hv.title, hv.visit_time "
                    "FROM history_items hi "
                    "JOIN history_visits hv ON hi.id = hv.history_item "
                    "ORDER BY hv.visit_time DESC LIMIT 500"
                ).fetchall()
            except sqlite3.OperationalError:
                try:
                    rows = conn.execute(
                        "SELECT url, '', 0 FROM history_items LIMIT 500"
                    ).fetchall()
                except sqlite3.OperationalError:
                    return

            for row in rows:
                url = str(row[0] or "")
                title = str(row[1] or "")
                raw_ts = row[2]
                try:
                    ts = self._coredata_to_unix(int(raw_ts)) if raw_ts is not None else 0
                except (ValueError, TypeError):
                    ts = 0
                combined = f"{url[:500]} {title[:200]}"  # ReDoS guard

                # General suspicious patterns (sorted by severity desc)
                for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                    if re.search(pattern, combined):
                        finding_type = (
                            "SAFARI_EXPLOIT_RESEARCH"
                            if severity >= Fraction(80, 100)
                            else "SAFARI_SUSPICIOUS"
                        )
                        self._findings.append(MacOSFinding(
                            finding_type=finding_type,
                            severity=severity,
                            description="Safari history matches suspicious pattern",
                            evidence=(
                                f"URL: {url[:150]}"
                                + ("[truncated]" if len(url) > 150 else "")
                                + f" | Title: {title[:100]}"
                            ),
                            mitre_technique=mitre,
                            rule_ref="MACOS-SAFARI-SUSP",
                            timestamp=ts,
                            corr_group="browser_suspicious",
                        ))
                        break

                # macOS-specific anti-forensic search patterns
                for pattern, severity, mitre in ANTIFORENSIC_SEARCH_PATTERNS:
                    if re.search(pattern, combined):
                        self._findings.append(MacOSFinding(
                            finding_type="ANTIFORENSIC_SEARCH",
                            severity=severity,
                            description="Safari history matches anti-forensic search",
                            evidence=(
                                f"URL: {url[:150]}"
                                + ("[truncated]" if len(url) > 150 else "")
                                + f" | Title: {title[:100]}"
                            ),
                            mitre_technique=mitre,
                            rule_ref="MACOS-SAFARI-ANTIFORENSIC",
                            timestamp=ts,
                            corr_group="antiforensic",
                        ))
                        break
        finally:
            conn.close()

    # ── Quarantine Events ──────────────────────────────────────────────────

    def _analyze_quarantine(self, db_path: Path, result: MacOSAnalysisResult) -> None:
        """Analyze com.apple.LaunchServices.QuarantineEventsV2.

        SQLite schema:
          LSQuarantineEvent (
            LSQuarantineEventIdentifier TEXT,
            LSQuarantineTimeStamp REAL,       -- CFAbsoluteTime (since 2001-01-01)
            LSQuarantineAgentBundleIdentifier TEXT,
            LSQuarantineAgentName TEXT,        -- e.g. "Safari", "curl", "Chrome"
            LSQuarantineDataURLString TEXT,    -- download URL
            LSQuarantineSenderName TEXT,
            LSQuarantineSenderAddress TEXT,
            LSQuarantineTypeNumber INTEGER,
            LSQuarantineOriginTitle TEXT,
            LSQuarantineOriginURLString TEXT,
            LSQuarantineOriginAlias BLOB
          )
        Forensic value: records every file downloaded + source URL, even after
        the file itself is deleted. Anti-forensic actors clear this or use tools
        that bypass Gatekeeper quarantine flags.
        """
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"Quarantine: could not open {db_path}")
            return
        try:
            conn.row_factory = sqlite3.Row
            try:
                count = conn.execute(
                    "SELECT COUNT(*) FROM LSQuarantineEvent"
                ).fetchone()[0]
                result.total_quarantine_events = count
            except sqlite3.OperationalError:
                result.analysis_notes.append(
                    "Quarantine: 'LSQuarantineEvent' table not found"
                )
                return

            try:
                rows = conn.execute(
                    "SELECT LSQuarantineTimeStamp, "
                    "       LSQuarantineAgentName, "
                    "       LSQuarantineDataURLString, "
                    "       LSQuarantineOriginURLString, "
                    "       LSQuarantineSenderName "
                    "FROM LSQuarantineEvent "
                    "ORDER BY LSQuarantineTimeStamp DESC LIMIT 500"
                ).fetchall()
            except sqlite3.OperationalError:
                return

            for row in rows:
                raw_ts = row["LSQuarantineTimeStamp"]
                agent = str(row["LSQuarantineAgentName"] or "")
                data_url = str(row["LSQuarantineDataURLString"] or "")
                origin_url = str(row["LSQuarantineOriginURLString"] or "")
                sender = str(row["LSQuarantineSenderName"] or "")

                try:
                    ts = self._cocoa_ts_to_unix(float(raw_ts)) if raw_ts else 0
                except (ValueError, TypeError):
                    ts = 0

                combined = f"{data_url[:500]} {origin_url[:300]} {agent}"

                # Suspicious download agents (curl, wget = command-line downloads)
                if agent.lower() in ("curl", "wget", "python", "aria2c"):
                    self._findings.append(MacOSFinding(
                        finding_type="QUARANTINE_CLI_DOWNLOAD",
                        severity=Fraction(45, 100),
                        description=f"File downloaded via CLI tool: {agent}",
                        evidence=f"Agent: {agent} | URL: {data_url[:150]}",
                        mitre_technique="T1105",
                        rule_ref="MACOS-QUARANTINE-CLI",
                        timestamp=ts,
                        corr_group="quarantine_suspicious",
                    ))

                # Suspicious URL patterns in downloads
                for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                    if re.search(pattern, combined):
                        self._findings.append(MacOSFinding(
                            finding_type="QUARANTINE_SUSPICIOUS_SOURCE",
                            severity=severity,
                            description="Quarantine event from suspicious source",
                            evidence=(
                                f"Agent: {agent} | URL: {data_url[:150]}"
                                + f" | Origin: {origin_url[:100]}"
                            ),
                            mitre_technique=mitre,
                            rule_ref="MACOS-QUARANTINE-SUSP",
                            timestamp=ts,
                            corr_group="quarantine_suspicious",
                        ))
                        break

            # Anti-forensic signal: quarantine DB exists but is empty
            if count == 0:
                self._findings.append(MacOSFinding(
                    finding_type="ANTIFORENSIC_QUARANTINE_EMPTY",
                    severity=Fraction(65, 100),
                    description=(
                        "Quarantine database exists but is empty — "
                        "possible manual clearing of download history"
                    ),
                    evidence=f"LSQuarantineEvent count: 0 in {db_path.name}",
                    mitre_technique="T1070.004",
                    rule_ref="MACOS-QUARANTINE-EMPTY",
                    corr_group="antiforensic",
                ))
        finally:
            conn.close()

    # ── App Detection ──────────────────────────────────────────────────────

    def _detect_installed_apps(
        self, evidence_path: Path, result: MacOSAnalysisResult
    ) -> None:
        """Detect installed encrypted/suspicious apps by scanning for .app
        bundles and Application Support directories."""
        for bundle_id, (desc, severity) in ENCRYPTED_APPS.items():
            # macOS stores apps in /Applications/<Name>.app/Contents/Info.plist
            # with CFBundleIdentifier matching bundle_id, and data in
            # ~/Library/Application Support/<bundle_id>/
            matches = list(evidence_path.rglob(f"*/{bundle_id}"))
            if not matches:
                matches = [
                    p for p in evidence_path.rglob(f"*{bundle_id}*")
                    if p.is_dir() and bundle_id in p.name
                ]
            if matches:
                self._encrypted_apps.append({
                    "bundle_id": bundle_id,
                    "description": desc,
                    "severity": str(severity),
                    "paths_found": len(matches),
                })

        # Tor Browser detection (may not use standard bundle ID)
        tor_matches = [
            p for p in evidence_path.rglob("*")
            if not p.is_symlink() and "torbrowser" in p.name.lower()
        ]
        if tor_matches and not any(
            a["bundle_id"] == "org.torproject.torbrowser"
            for a in self._encrypted_apps
        ):
            self._findings.append(MacOSFinding(
                finding_type="TOR_BROWSER_DETECTED",
                severity=Fraction(75, 100),
                description="Tor Browser artifacts found — anonymized browsing capability",
                evidence=str(tor_matches[0].name)[:200],
                mitre_technique="T1090.003",
                rule_ref="MACOS-APP-TOR",
                corr_group="encrypted_apps",
            ))

    # ── Plist Analysis ─────────────────────────────────────────────────────

    # Forensically interesting plist filenames → (description, what to look for)
    _INTERESTING_PLISTS = {
        "com.apple.loginitems.plist": "Login items — programs launched at user login",
        "com.apple.recentitems.plist": "Recent items — recently opened files/apps/servers",
        "loginwindow.plist": "Login window config — auto-login, hidden users",
        "com.apple.dock.plist": "Dock — persistent apps, recently used",
    }

    # LaunchAgent/LaunchDaemon directories (relative patterns for rglob)
    _LAUNCH_DIRS = ("LaunchAgents", "LaunchDaemons")

    def _analyze_plists(
        self, evidence_path: Path, result: MacOSAnalysisResult
    ) -> None:
        """Scan for forensically relevant plist files.

        Covers three categories:
        1. LaunchAgents/LaunchDaemons — persistence mechanisms (T1543.001)
        2. Login items — user-level persistence (T1547.015)
        3. Recent items — user activity footprint
        """
        self._analyze_launch_plists(evidence_path, result)
        self._analyze_loginitems_plists(evidence_path, result)

    def _safe_plist_load(self, path: Path) -> Optional[dict]:
        """Load a plist file (binary or XML). Returns None on failure."""
        try:
            with open(path, "rb") as f:
                return plistlib.load(f)
        except (OSError, plistlib.InvalidFileException, Exception) as e:
            logger.debug("[MACOS] Plist parse failed for %s: %s", path, e)
            return None

    def _analyze_launch_plists(
        self, evidence_path: Path, result: MacOSAnalysisResult
    ) -> None:
        """Scan LaunchAgents and LaunchDaemons for persistence mechanisms.

        Each .plist in these directories defines a job loaded at boot or login.
        Suspicious indicators:
        - ProgramArguments pointing to /tmp, /var/tmp, hidden paths
        - RunAtLoad=True with non-Apple label
        - KeepAlive=True (auto-restart = C2 resilience)
        """
        for launch_dir_name in self._LAUNCH_DIRS:
            for launch_dir in evidence_path.rglob(launch_dir_name):
                if not launch_dir.is_dir() or launch_dir.is_symlink():
                    continue
                plists = [
                    p for p in sorted(launch_dir.iterdir())
                    if p.suffix == ".plist" and p.is_file() and not p.is_symlink()
                ][:50]  # cap to prevent rglob explosion

                for plist_path in plists:
                    plist = self._safe_plist_load(plist_path)
                    if plist is None:
                        continue

                    label = str(plist.get("Label", ""))
                    program_args = plist.get("ProgramArguments", [])
                    program = plist.get("Program", "")
                    run_at_load = plist.get("RunAtLoad", False)
                    keep_alive = plist.get("KeepAlive", False)

                    # Build the executable path from ProgramArguments[0] or Program
                    exe = ""
                    if isinstance(program_args, list) and program_args:
                        exe = str(program_args[0])
                    elif program:
                        exe = str(program)

                    # Skip Apple-signed system jobs
                    if label.startswith("com.apple."):
                        continue

                    # Flag: executable in suspicious paths
                    suspicious_paths = ("/tmp/", "/var/tmp/", "/private/tmp/", "/Users/Shared/")
                    exe_in_suspicious_path = any(
                        exe.startswith(sp) for sp in suspicious_paths
                    )
                    # Flag: hidden executable (starts with dot after last /)
                    exe_hidden = "/." in exe

                    if exe_in_suspicious_path or exe_hidden:
                        self._findings.append(MacOSFinding(
                            finding_type="PERSISTENCE_SUSPICIOUS_LAUNCHAGENT",
                            severity=Fraction(75, 100),
                            description=(
                                f"LaunchAgent/Daemon with suspicious executable path"
                            ),
                            evidence=(
                                f"Label: {label[:100]} | "
                                f"Exe: {exe[:150]} | "
                                f"RunAtLoad: {run_at_load} | "
                                f"Dir: {launch_dir_name}"
                            ),
                            mitre_technique="T1543.001",
                            rule_ref="MACOS-PERSIST-LAUNCH-SUSP",
                            corr_group="persistence",
                        ))
                    elif run_at_load and keep_alive:
                        # Non-Apple job that auto-starts and auto-restarts
                        self._findings.append(MacOSFinding(
                            finding_type="PERSISTENCE_RESILIENT_LAUNCHAGENT",
                            severity=Fraction(50, 100),
                            description=(
                                f"Non-Apple LaunchAgent/Daemon with RunAtLoad + KeepAlive"
                            ),
                            evidence=(
                                f"Label: {label[:100]} | "
                                f"Exe: {exe[:150]} | "
                                f"Dir: {launch_dir_name}"
                            ),
                            mitre_technique="T1543.001",
                            rule_ref="MACOS-PERSIST-LAUNCH-RESILIENT",
                            corr_group="persistence",
                        ))

    def _analyze_loginitems_plists(
        self, evidence_path: Path, result: MacOSAnalysisResult
    ) -> None:
        """Scan login item plists for user-level persistence."""
        for li in self._safe_rglob(
            evidence_path, "com.apple.loginitems.plist", limit=5
        ):
            plist = self._safe_plist_load(li)
            if plist is None:
                continue

            # SessionItems → CustomListItems contains login items
            session_items = plist.get("SessionItems", {})
            if not isinstance(session_items, dict):
                continue
            custom_list = session_items.get("CustomListItems", [])
            if not isinstance(custom_list, list):
                continue

            for item in custom_list[:20]:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("Name", ""))
                # Login items with hidden names
                if name.startswith("."):
                    self._findings.append(MacOSFinding(
                        finding_type="PERSISTENCE_HIDDEN_LOGIN_ITEM",
                        severity=Fraction(65, 100),
                        description=f"Hidden login item: '{name}'",
                        evidence=f"Name: {name} | Plist: {li.name}",
                        mitre_technique="T1547.015",
                        rule_ref="MACOS-PERSIST-LOGIN-HIDDEN",
                        corr_group="persistence",
                    ))

    # ── OPSEC Assessment ───────────────────────────────────────────────────

    def _assess_opsec(self, result: MacOSAnalysisResult) -> None:
        n_encrypted = len(self._encrypted_apps)

        if n_encrypted >= 3:
            self._opsec_indicators.append({
                "indicator": "MULTI_ENCRYPTED_APPS",
                "severity": str(Fraction(70, 100)),
                "description": f"{n_encrypted} encrypted/privacy apps installed",
            })
            self._findings.append(MacOSFinding(
                finding_type="OPSEC_MULTI_ENCRYPTED_APPS",
                severity=Fraction(70, 100),
                description=f"{n_encrypted} encrypted/privacy apps — deliberate OPSEC posture",
                evidence=", ".join(a["bundle_id"] for a in self._encrypted_apps),
                mitre_technique="T1573",
                rule_ref="MACOS-OPSEC-MULTI",
                corr_group="encrypted_apps",
            ))
        elif n_encrypted >= 2:
            self._opsec_indicators.append({
                "indicator": "DUAL_ENCRYPTED_APPS",
                "severity": str(Fraction(50, 100)),
                "description": f"{n_encrypted} encrypted/privacy apps installed",
            })

        # Empty quarantine + encrypted apps = possible anti-forensic posture
        has_empty_quarantine = any(
            f.finding_type == "ANTIFORENSIC_QUARANTINE_EMPTY" for f in self._findings
        )
        if has_empty_quarantine and n_encrypted >= 1:
            self._findings.append(MacOSFinding(
                finding_type="OPSEC_ANTIFORENSIC_POSTURE",
                severity=Fraction(65, 100),
                description=(
                    "Cleared quarantine DB + encrypted apps — "
                    "combined anti-forensic and OPSEC behavior"
                ),
                evidence=(
                    f"quarantine_empty=True, encrypted_apps={n_encrypted}"
                ),
                mitre_technique="T1070",
                rule_ref="MACOS-OPSEC-COMBINED",
                corr_group="antiforensic",
            ))
