"""
vigia/sift/android_forensics.py

Android forensic artifact analyzer for VIGÍA.
Parses SQLite databases (mmssms.db, contacts2.db, browser history),
package manifests, and filesystem artifacts from Android extractions
(Cellebrite, ADB, Magisk root, logical/physical).

Architecture: deterministic Fraction arithmetic throughout verdict path.
No floats in scoring. LLM never touches verdict.

FIX P0: All numerical values in evidence dict use Fraction/str. NEVER float.
"""

from __future__ import annotations

import heapq
import json
import logging
import re
import sqlite3
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._fs_utils import scan_marker_names
from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated
from vigia.sift._sql_utils import safe_sqlite_connect

logger = logging.getLogger(__name__)

TOOL_NAME = "ANDROID_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(70, 100)

# Chrome timestamp epoch: microseconds since 1601-01-01
_CHROME_EPOCH_OFFSET = 11644473600

# ──────────────────────────────────────────────────────────────────────────────
# CATALOGS
# ──────────────────────────────────────────────────────────────────────────────

ENCRYPTED_APPS: Dict[str, Tuple[str, Fraction]] = {
    "com.wire":                     ("Wire — E2E encrypted messaging", Fraction(60, 100)),
    "org.thoughtcrime.securesms":   ("Signal — E2E encrypted messaging", Fraction(60, 100)),
    "com.wickr.pro":                ("Wickr Pro — E2E + auto-destruct", Fraction(80, 100)),
    "com.mywickr.wickr":            ("Wickr Me — E2E + auto-destruct", Fraction(80, 100)),
    "ch.protonmail.android":        ("ProtonMail — encrypted email", Fraction(55, 100)),
    "org.telegram.messenger":       ("Telegram — optional E2E", Fraction(45, 100)),
    "com.tencent.mm":               ("WeChat — messaging", Fraction(50, 100)),
    "org.briarproject.briar":       ("Briar — P2P encrypted mesh", Fraction(85, 100)),
    "im.conversations.android":     ("Conversations — XMPP/OMEMO E2E", Fraction(60, 100)),
    "network.loki.messenger":       ("Session — decentralized E2E", Fraction(75, 100)),
}

ROOT_INDICATORS: Dict[str, Tuple[str, Fraction]] = {
    "com.topjohnwu.magisk":         ("Magisk — systemless root", Fraction(70, 100)),
    "eu.chainfire.supersu":         ("SuperSU — legacy root", Fraction(70, 100)),
    "com.koushikdutta.superuser":   ("Superuser — legacy root", Fraction(70, 100)),
    "com.noshufou.android.su":      ("Superuser — legacy root", Fraction(70, 100)),
}

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

# Known Android artifact markers for validation
_ANDROID_MARKER_FILES = {
    "mmssms.db", "contacts2.db", "calllog.db", "packages.xml",
    "packages.list", "accounts_de.db", "accounts_ce.db",
}


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AndroidFinding:
    finding_type: str
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""


@dataclass
class AndroidAnalysisResult:
    """Result of Android forensic analysis."""
    source_path: str = ""
    device_model: str = ""
    android_version: str = ""
    owner_email: str = ""
    is_rooted: bool = False
    root_method: str = ""
    total_sms: int = 0
    total_contacts: int = 0
    total_calls: int = 0
    # B-072: solo un conteo EXITOSO de 0 es evidencia de data_minimization
    # (ver iOSAnalysisResult). Un parseo fallido/DB ausente no escala.
    contacts_parsed: bool = False
    calls_parsed: bool = False
    total_browser_entries: int = 0
    encrypted_apps: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[AndroidFinding] = field(default_factory=list)
    opsec_indicators: List[Dict[str, Any]] = field(default_factory=list)
    accounts: List[Dict[str, str]] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)

        n_encrypted = len(self.encrypted_apps)
        n_opsec = len(self.opsec_indicators)
        has_exploit_research = any(
            f.finding_type in ("BROWSER_EXPLOIT_RESEARCH", "BROWSER_EXPLOIT_BOOKMARKED")
            for f in self.findings
        )
        has_root = self.is_rooted
        # B-072: empty solo si el conteo fue EXITOSO y dio 0 (ver iOS to_signal).
        empty_contacts = self.contacts_parsed and self.total_contacts == 0
        empty_calls = self.calls_parsed and self.total_calls == 0
        data_minimization = empty_contacts and empty_calls

        # Opsec bump (BUG-011 fix)
        opsec_bump = Fraction(0)
        if n_opsec >= 3:
            opsec_bump = Fraction(4, 10)
        elif n_opsec >= 2:
            opsec_bump = Fraction(2, 10)

        # Z-score escalation ladder
        if has_exploit_research and has_root:
            z = Fraction(38, 10)
        elif has_exploit_research:
            z = Fraction(35, 10)
        elif has_root and n_encrypted >= 2 and data_minimization:
            z = Fraction(34, 10)
        elif n_encrypted >= 3 and data_minimization:
            z = Fraction(30, 10)
        elif has_root and n_encrypted >= 2:
            z = Fraction(28, 10)
        elif n_encrypted >= 3:
            z = Fraction(24, 10)
        elif has_root:
            z = Fraction(20, 10)
        elif n_encrypted >= 2:
            z = Fraction(18, 10)
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
                "device_model": self.device_model,
                "android_version": self.android_version,
                "owner_email": self.owner_email,
                "is_rooted": self.is_rooted,
                "root_method": self.root_method,
                "total_sms": self.total_sms,
                "total_contacts": self.total_contacts,
                "total_calls": self.total_calls,
                "encrypted_apps_count": n_encrypted,
                "opsec_indicators_count": n_opsec,
                "data_minimization": data_minimization,
                "findings_count": len(self.findings),
                "composite_score": str(self.composite_score),
                "artifact_type": "android_forensic",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "chains": n_encrypted + n_opsec + (1 if has_root else 0),
                "finding_types": sorted(list(set(
                    f.finding_type for f in self.findings
                ))),
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

class AndroidForensicsAnalyzer:
    """
    Analyzes Android forensic extractions.

    Expects a directory containing the /data partition or logical extraction.
    """

    def __init__(self):
        self._findings: List[AndroidFinding] = []
        self._encrypted_apps: List[Dict[str, Any]] = []
        self._opsec_indicators: List[Dict[str, Any]] = []

    def analyze(
        self,
        evidence_path: Path,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> AndroidAnalysisResult:
        self._findings = []
        self._encrypted_apps = []
        self._opsec_indicators = []

        evidence_path = Path(evidence_path)
        if not evidence_path.is_dir():
            logger.warning("[ANDROID] Evidence path is not a directory: %s", evidence_path)
            return AndroidAnalysisResult(
                source_path=str(evidence_path),
                analysis_notes=["Evidence path is not a directory."],
            )

        result = AndroidAnalysisResult(source_path=str(evidence_path))

        # Validate Android evidence (BUG-007 fix).
        # B-139: bounded scan — O(markers) memory, capped walk with WARNING.
        android_markers = scan_marker_names(
            evidence_path, _ANDROID_MARKER_FILES, engine="ANDROID", logger=logger
        )
        if not android_markers:
            logger.warning("[ANDROID] No Android artifacts found in %s", evidence_path)
            result.analysis_notes.append(
                "No Android-specific artifacts found. Directory may not contain Android evidence."
            )

        # 1. Root detection
        self._detect_root(evidence_path, result)

        # 2. SMS
        for db in self._safe_rglob(evidence_path, "mmssms.db", limit=3):
            try:
                self._analyze_sms(db, result)
            except Exception as e:
                logger.error("[ANDROID] SMS analysis failed: %s", e)
                result.analysis_notes.append(f"SMS parse error: {e}")

        # 3. Contacts
        for db in self._safe_rglob(evidence_path, "contacts2.db", limit=3):
            try:
                self._analyze_contacts(db, result)
            except Exception as e:
                logger.error("[ANDROID] Contacts analysis failed: %s", e)
                result.analysis_notes.append(f"Contacts parse error: {e}")

        # 4. Call log
        for db in self._safe_rglob(evidence_path, "calllog.db", limit=3):
            try:
                self._analyze_call_log(db, result)
            except Exception as e:
                logger.error("[ANDROID] Call log analysis failed: %s", e)
                result.analysis_notes.append(f"Call log parse error: {e}")

        # 5. Chrome history
        for db in self._safe_rglob(evidence_path, "History", limit=3):
            # Verify it's actually a SQLite database (BUG: P1-004 fix)
            try:
                with open(db, "rb") as f:
                    header = f.read(16)
                if not header.startswith(b"SQLite format 3"):
                    continue
            except (OSError, IOError):
                continue
            try:
                self._analyze_chrome(db, result)
            except Exception as e:
                logger.error("[ANDROID] Chrome analysis failed: %s", e)
                result.analysis_notes.append(f"Chrome parse error: {e}")

        # 6. App detection
        self._detect_installed_apps(evidence_path, result)

        # 7. Accounts
        self._analyze_accounts(evidence_path, result)

        # 8. Bluetooth
        self._analyze_bluetooth(evidence_path, result)

        # 9. OPSEC assessment
        self._assess_opsec(result)

        result.findings = self._findings
        result.encrypted_apps = self._encrypted_apps
        result.opsec_indicators = self._opsec_indicators

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
        """rglob with symlink filtering, deterministic sort, and limit.

        S4 (AUDITORIA_COBERTURA_MOBILE_SIFT §C): antes materializaba y ordenaba
        el arbol ENTERO antes del slice — el limit no protegia la memoria ante
        un arbol de evidencia hostil/gigante. heapq.nsmallest produce los
        mismos primeros N en orden global determinista con memoria O(limit).
        """
        if not base.is_dir():
            return []
        return heapq.nsmallest(
            limit,
            (f for f in base.rglob(pattern)
             if not f.is_symlink() and f.is_file()),
            key=lambda p: str(p),
        )

    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; replaces List[List[int]] format)."""
        return build_correlation_groups([f.corr_group for f in self._findings])

    @staticmethod
    def _chrome_ts_to_unix(ts: int) -> int:
        """Convert Chrome/WebKit timestamp to Unix epoch.
        2024 magnitudes: micros ~1.7e16, millis ~1.7e13, secs ~1.7e10."""
        if ts is None or ts <= 0:
            return 0
        # P0-001 census §5.4: división entera — int(ts / 1_000_000) pasaba por
        # float y podía cruzar el borde de segundo (p.ej. ts=18396007234999999
        # daba ...235 en vez de ...234). Para ts>0, // equivale a la truncación
        # de int() sin el redondeo IEEE 754 intermedio.
        if ts > 1_000_000_000_000_000:
            return int(ts) // 1_000_000 - _CHROME_EPOCH_OFFSET
        elif ts > 1_000_000_000_000:
            return int(ts) // 1_000 - _CHROME_EPOCH_OFFSET
        elif ts > 10_000_000_000:
            return int(ts) - _CHROME_EPOCH_OFFSET
        return int(ts)

    @staticmethod
    def _safe_sqlite_connect(db_path: Path) -> Optional[sqlite3.Connection]:
        """Open SQLite evidence read-only + immutable (B-071 → _sql_utils).
        Never writes to evidence, never creates an empty DB on a missing path."""
        return safe_sqlite_connect(db_path, "ANDROID", logger)

    # ── Root Detection ──────────────────────────────────────────────────────

    def _detect_root(self, evidence_path: Path, result: AndroidAnalysisResult) -> None:
        # Magisk
        magisk_apk = list(evidence_path.rglob("com.topjohnwu.magisk"))
        magisk_backup = list(evidence_path.rglob("magisk_backup_*"))
        magisk_db = list(evidence_path.rglob("magisk.db"))  # BUG-014 fix

        if magisk_apk or magisk_backup or magisk_db:
            result.is_rooted = True
            result.root_method = "Magisk"
            # Try to find version
            for mp in evidence_path.rglob("*magisk*"):
                match = re.search(r"magisk[_-]?(?:patched[_-]?)?(\d+)", mp.name.lower())
                if match:
                    result.root_method = f"Magisk v{match.group(1)}"
                    break

            self._findings.append(AndroidFinding(
                finding_type="DEVICE_ROOTED",
                severity=Fraction(70, 100),
                description=f"Device rooted via {result.root_method}",
                evidence=f"Magisk artifacts: apk={len(magisk_apk)}, backup={len(magisk_backup)}, db={len(magisk_db)}",
                mitre_technique="T1398",
                rule_ref="ANDROID-ROOT-MAGISK",
                corr_group="root",
            ))

        # SuperSU
        supersu = list(evidence_path.rglob("eu.chainfire.supersu"))
        if supersu and not result.is_rooted:
            result.is_rooted = True
            result.root_method = "SuperSU"
            self._findings.append(AndroidFinding(
                finding_type="DEVICE_ROOTED",
                severity=Fraction(70, 100),
                description="Device rooted via SuperSU",
                evidence=str(supersu[0].name)[:200],
                mitre_technique="T1398",
                rule_ref="ANDROID-ROOT-SUPERSU",
                corr_group="root",
            ))

        # su binary in system paths (BUG-014 fix)
        su_system_bin = list(evidence_path.rglob("system/bin/su"))
        su_system_xbin = list(evidence_path.rglob("system/xbin/su"))
        if (su_system_bin or su_system_xbin) and not result.is_rooted:
            result.is_rooted = True
            result.root_method = "su binary"

    # ── SMS ─────────────────────────────────────────────────────────────────

    def _analyze_sms(self, db_path: Path, result: AndroidAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"mmssms.db: could not open {db_path}")
            return
        try:
            conn.row_factory = sqlite3.Row
            try:
                count = conn.execute("SELECT COUNT(*) FROM sms").fetchone()[0]
                result.total_sms = count
            except sqlite3.OperationalError:
                result.analysis_notes.append("mmssms.db: 'sms' table not found")
                return

            rows = conn.execute(
                "SELECT _id, address, body, date, type, thread_id "
                "FROM sms WHERE body IS NOT NULL LIMIT 500"
            ).fetchall()

            for row in rows:
                body = str(row["body"] or "")
                ts = int(row["date"] or 0)
                msg_type = int(row["type"] or 0)

                if msg_type == 2:  # Sent
                    for pkg, (desc, sev) in ENCRYPTED_APPS.items():
                        short = pkg.split(".")[-1].lower()
                        if short in body.lower():
                            self._findings.append(AndroidFinding(
                                finding_type="SMS_ENCRYPTED_RECRUITMENT",
                                severity=sev,
                                description=f"Outgoing SMS recruiting contact to {desc}",
                                evidence=body[:200] + ("[truncated]" if len(body) > 200 else ""),
                                mitre_technique="T1573",
                                rule_ref="ANDROID-SMS-RECRUIT",
                                timestamp=ts,
                                corr_group="encrypted_apps",
                            ))
                            break
        finally:
            conn.close()

    # ── Contacts ────────────────────────────────────────────────────────────

    def _analyze_contacts(self, db_path: Path, result: AndroidAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"contacts2.db: could not open {db_path}")
            return
        parsed = False
        try:
            try:
                count = conn.execute("SELECT COUNT(*) FROM raw_contacts").fetchone()[0]
                result.total_contacts = count
                parsed = True
            except sqlite3.OperationalError:
                try:
                    count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
                    result.total_contacts = count
                    parsed = True
                except sqlite3.OperationalError:
                    result.analysis_notes.append("contacts2.db: could not count contacts")
        finally:
            conn.close()

        result.contacts_parsed = parsed

        # B-072: fallo de parseo != agenda vacía. Solo un conteo exitoso de 0
        # escala data_minimization (ver iOS _analyze_contacts). El flag
        # contacts_parsed corta la escalación en to_signal, no solo el finding.
        if parsed and result.total_contacts == 0:
            self._opsec_indicators.append({
                "indicator": "EMPTY_CONTACTS",
                "severity": str(Fraction(60, 100)),
                "description": "Contacts database is empty",
            })
            self._findings.append(AndroidFinding(
                finding_type="EMPTY_CONTACTS",
                severity=Fraction(45, 100),
                description="Contacts database is completely empty",
                evidence=f"raw_contacts count: 0 in {db_path.name}",
                mitre_technique="T1070",
                rule_ref="ANDROID-CONTACTS-EMPTY",
                corr_group="data_minimization",
            ))

    # ── Call Log ────────────────────────────────────────────────────────────

    def _analyze_call_log(self, db_path: Path, result: AndroidAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"calllog.db: could not open {db_path}")
            return
        parsed = False
        try:
            try:
                count = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
                result.total_calls = count
                parsed = True
            except sqlite3.OperationalError:
                result.analysis_notes.append("calllog.db: 'calls' table not found")
        finally:
            conn.close()

        result.calls_parsed = parsed

        # B-072: fallo de parseo != call log vacío (ver iOS _analyze_contacts).
        if parsed and result.total_calls == 0:
            self._opsec_indicators.append({
                "indicator": "EMPTY_CALL_LOG",
                "severity": str(Fraction(55, 100)),
                "description": "Call log completely empty",
            })
            self._findings.append(AndroidFinding(
                finding_type="EMPTY_CALL_LOG",
                severity=Fraction(40, 100),
                description="Call log is completely empty",
                evidence=f"calls count: 0 in {db_path.name}",
                mitre_technique="T1070",
                rule_ref="ANDROID-CALLS-EMPTY",
                corr_group="data_minimization",
            ))

    # ── Chrome ──────────────────────────────────────────────────────────────

    def _analyze_chrome(self, db_path: Path, result: AndroidAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"Chrome History: could not open {db_path}")
            return
        try:
            conn.row_factory = sqlite3.Row
            try:
                count = conn.execute("SELECT COUNT(*) FROM urls").fetchone()[0]
                result.total_browser_entries = count
            except sqlite3.OperationalError:
                return

            rows = conn.execute(
                "SELECT url, title, visit_count, last_visit_time "
                "FROM urls ORDER BY last_visit_time DESC LIMIT 500"
            ).fetchall()

            for row in rows:
                url = str(row["url"] or "")
                title = str(row["title"] or "")
                raw_ts = row["last_visit_time"]
                try:
                    # P0-001 census §3.1: los timestamps WebKit en µs (~1.7e16)
                    # exceden 2^53 — int(float(x)) perdía hasta ±2 µs de mantisa.
                    # Decimal(str(x)) acepta int, string decimal y notación
                    # científica sin pasar por IEEE 754.
                    ts = self._chrome_ts_to_unix(int(Decimal(str(raw_ts)))) if raw_ts is not None else 0
                except (ValueError, TypeError, ArithmeticError):
                    ts = 0
                combined = f"{url[:500]} {title[:200]}"  # ReDoS guard

                for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                    if re.search(pattern, combined):
                        finding_type = (
                            "BROWSER_EXPLOIT_RESEARCH"
                            if severity >= Fraction(80, 100)
                            else "BROWSER_SUSPICIOUS"
                        )
                        self._findings.append(AndroidFinding(
                            finding_type=finding_type,
                            severity=severity,
                            description=f"Chrome history matches suspicious pattern",
                            evidence=(
                                f"URL: {url[:150]}"
                                + ("[truncated]" if len(url) > 150 else "")
                                + f" | Title: {title[:100]}"
                            ),
                            mitre_technique=mitre,
                            rule_ref="ANDROID-CHROME-SUSP",
                            timestamp=ts,
                            corr_group="browser_suspicious",
                        ))
                        break

            # Check bookmarks
            try:
                bm_rows = conn.execute(
                    "SELECT url, title FROM bookmarks WHERE url IS NOT NULL LIMIT 200"
                ).fetchall()
                for bm in bm_rows:
                    url = str(bm["url"] or "")
                    title = str(bm["title"] or "")
                    combined = f"{url[:500]} {title[:200]}"  # ReDoS guard
                    for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                        if re.search(pattern, combined) and severity >= Fraction(80, 100):
                            # Clamp severity to 1.0 (P0-002 fix)
                            bm_severity = min(severity + Fraction(5, 100), Fraction(1, 1))
                            self._findings.append(AndroidFinding(
                                finding_type="BROWSER_EXPLOIT_BOOKMARKED",
                                severity=bm_severity,
                                description=f"Exploit tutorial BOOKMARKED — intentional preservation",
                                evidence=f"Bookmark: {url[:150]}" + ("[truncated]" if len(url) > 150 else ""),
                                mitre_technique=mitre,
                                rule_ref="ANDROID-CHROME-BM-EXPLOIT",
                                corr_group="browser_suspicious",
                            ))
                            break
            except sqlite3.OperationalError:
                pass
        finally:
            conn.close()

    # ── App Detection ───────────────────────────────────────────────────────

    def _detect_installed_apps(self, evidence_path: Path, result: AndroidAnalysisResult) -> None:
        for pkg, (desc, severity) in ENCRYPTED_APPS.items():
            # Search for exact package directory (BUG-006 fix)
            # Android stores apps in data/data/<package>/ or data/app/<package>-*/
            matches = list(evidence_path.rglob(f"data/{pkg}"))
            if not matches:
                matches = [
                    p for p in evidence_path.rglob(f"*/{pkg}")
                    if p.is_dir()
                ]
            if matches:
                self._encrypted_apps.append({
                    "package": pkg,
                    "description": desc,
                    "severity": str(severity),
                    "paths_found": len(matches),
                })

        for pkg, (desc, severity) in ROOT_INDICATORS.items():
            matches = list(evidence_path.rglob(f"data/{pkg}"))
            if not matches:
                matches = [p for p in evidence_path.rglob(f"*/{pkg}") if p.is_dir()]
            if matches and not result.is_rooted:
                result.is_rooted = True
                result.root_method = desc
                self._findings.append(AndroidFinding(
                    finding_type="DEVICE_ROOTED",
                    severity=severity,
                    description=f"Root indicator: {desc}",
                    evidence=str(matches[0].name)[:200],
                    mitre_technique="T1398",
                    rule_ref="ANDROID-ROOT-PKG",
                    corr_group="root",
                ))

        # ADB debugging — verify the value, not just file existence (P2-002 fix)
        for prop_file in evidence_path.rglob("*persist.sys.usb.config*"):
            if prop_file.is_symlink():
                continue
            try:
                content = prop_file.read_text(encoding="utf-8", errors="ignore")[:1000]
                if "adb" in content.lower():
                    self._opsec_indicators.append({
                        "indicator": "ADB_ENABLED",
                        "severity": str(Fraction(40, 100)),
                        "description": "USB debugging (ADB) enabled",
                    })
                    break
            except (OSError, IOError):
                pass

    # ── Accounts ────────────────────────────────────────────────────────────

    def _analyze_accounts(self, evidence_path: Path, result: AndroidAnalysisResult) -> None:
        accounts_dbs = (
            list(evidence_path.rglob("accounts_de.db"))
            + list(evidence_path.rglob("accounts_ce.db"))
        )
        for db_path in accounts_dbs[:3]:
            if db_path.is_symlink():
                continue
            conn = self._safe_sqlite_connect(db_path)
            if conn is None:
                continue
            try:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT name, type FROM accounts LIMIT 50"
                ).fetchall()
                for row in rows:
                    name = str(row["name"] or "")
                    acct_type = str(row["type"] or "")
                    result.accounts.append({"name": name, "type": acct_type})
                    if "gmail.com" in name.lower() and not result.owner_email:
                        result.owner_email = name
            except Exception as e:
                logger.error("[ANDROID] Accounts analysis failed for %s: %s", db_path, e)
                result.analysis_notes.append(f"Accounts parse error: {e}")
            finally:
                conn.close()

    # ── Bluetooth ───────────────────────────────────────────────────────────

    def _analyze_bluetooth(self, evidence_path: Path, result: AndroidAnalysisResult) -> None:
        for bt in self._safe_rglob(evidence_path, "bt_config.bak", limit=3):
            try:
                text = bt.read_text(encoding="utf-8", errors="ignore")[:10000]
                devices = re.findall(r"Name\s*=\s*(.+)", text)
                macs = re.findall(r"([0-9a-fA-F:]{17})", text)
                if devices or macs:
                    result.analysis_notes.append(
                        f"Bluetooth: {len(devices)} paired devices, {len(macs)} MAC addresses"
                    )
            except Exception as e:
                logger.error("[ANDROID] Bluetooth analysis failed: %s", e)
                result.analysis_notes.append(f"Bluetooth parse error: {e}")

    # ── OPSEC Assessment ────────────────────────────────────────────────────

    def _assess_opsec(self, result: AndroidAnalysisResult) -> None:
        n_encrypted = len(self._encrypted_apps)

        if n_encrypted >= 3:
            self._opsec_indicators.append({
                "indicator": "MULTI_ENCRYPTED_APPS",
                "severity": str(Fraction(70, 100)),
                "description": f"{n_encrypted} encrypted messaging apps installed",
            })
            self._findings.append(AndroidFinding(
                finding_type="OPSEC_MULTI_ENCRYPTED_APPS",
                severity=Fraction(70, 100),
                description=f"{n_encrypted} encrypted messaging apps detected",
                evidence=", ".join(a["package"] for a in self._encrypted_apps),
                mitre_technique="T1573",
                rule_ref="ANDROID-OPSEC-MULTI",
                corr_group="encrypted_apps",
            ))

        if result.total_contacts == 0 and result.total_calls == 0 and n_encrypted >= 1:
            self._findings.append(AndroidFinding(
                finding_type="OPSEC_DATA_MINIMIZATION",
                severity=Fraction(65, 100),
                description="Data minimization: zero contacts + zero calls + encrypted app presence",
                evidence=f"contacts={result.total_contacts}, calls={result.total_calls}, "
                         f"encrypted_apps={n_encrypted}",
                mitre_technique="T1070",
                rule_ref="ANDROID-OPSEC-MINIMIZE",
                corr_group="data_minimization",
            ))

        if result.is_rooted and n_encrypted >= 2:
            self._findings.append(AndroidFinding(
                finding_type="OPSEC_ROOT_PLUS_ENCRYPTED",
                severity=Fraction(75, 100),
                description=f"Rooted ({result.root_method}) + {n_encrypted} encrypted apps",
                evidence=f"Root: {result.root_method}, Apps: {n_encrypted}",
                mitre_technique="T1398",
                rule_ref="ANDROID-OPSEC-ROOT-ENC",
                corr_group="root",
            ))
