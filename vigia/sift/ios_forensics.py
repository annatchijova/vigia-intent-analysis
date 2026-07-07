"""
vigia/sift/ios_forensics.py

iOS forensic artifact analyzer for VIGÍA.
Parses SQLite databases (sms.db, AddressBook, CallHistory, Safari History),
plists, and keychain exports from iOS extractions (GrayKey, Cellebrite, etc.).

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
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated
from vigia.sift._sql_utils import safe_sqlite_connect

logger = logging.getLogger(__name__)

TOOL_NAME = "IOS_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(70, 100)  # iOS SQLite is binary, checksummed

# Core Data Reference Date: 2001-01-01 00:00:00 UTC in Unix epoch
_COREDATA_EPOCH_OFFSET = 978307200

# ──────────────────────────────────────────────────────────────────────────────
# CATALOGS — severity in Fraction, MITRE TTP, description
# Ordered by severity DESCENDING so break-on-first-match gets highest severity
# ──────────────────────────────────────────────────────────────────────────────

ENCRYPTED_APPS: Dict[str, Tuple[str, Fraction]] = {
    "com.mywickr.wickr":            ("Wickr Me — E2E + auto-destruct + Psiphon VPN", Fraction(80, 100)),
    "org.whispersystems.signal":    ("Signal — E2E encrypted messaging", Fraction(60, 100)),
    "ch.protonmail.protonmail":     ("ProtonMail — encrypted email", Fraction(55, 100)),
    "com.wire":                     ("Wire — E2E encrypted messaging", Fraction(60, 100)),
    "com.tencent.xin":              ("WeChat — messaging with Chinese encryption", Fraction(50, 100)),
    "org.telegram.Telegram":        ("Telegram — optional E2E (Secret Chats)", Fraction(45, 100)),
    "com.facebook.Messenger":       ("Messenger — optional E2E", Fraction(20, 100)),
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

PHISHING_PATTERNS: List[Tuple[str, Fraction, str]] = [
    (r"ow\.ly/|bit\.ly/|tinyurl\.com/", Fraction(40, 100), "T1566.003"),
    (r"(?i)verify.*account|confirm.*identity", Fraction(35, 100), "T1566.001"),
    (r"(?i)you.*won|prize|claim\s+now", Fraction(30, 100), "T1566.003"),
]

# Known iOS artifact files — used to validate evidence directory
_IOS_MARKER_FILES = {
    "sms.db", "AddressBook.sqlitedb", "CallHistory.storedata",
    "History.db", "Info.plist", "keychain-2.db",
    "signal.sqlite",
}


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class iOSFinding:
    finding_type: str
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str
    timestamp: int = 0
    # Correlation group tag — findings with the same group are correlated
    corr_group: str = ""


@dataclass
class iOSAnalysisResult:
    """Result of iOS forensic analysis."""
    source_path: str = ""
    device_name: str = ""
    ios_version: str = ""
    owner_name: str = ""
    total_sms: int = 0
    total_contacts: int = 0
    total_calls: int = 0
    # B-072: solo un conteo EXITOSO de 0 es evidencia de data_minimization.
    # Un parseo fallido o una DB ausente dejan total_*=0 por default, lo que NO
    # debe escalar el veredicto (falso INTENT/MALICE). Estos flags distinguen
    # "parseado y vacío" de "no determinado".
    contacts_parsed: bool = False
    calls_parsed: bool = False
    total_safari_entries: int = 0
    encrypted_apps: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[iOSFinding] = field(default_factory=list)
    opsec_indicators: List[Dict[str, Any]] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)

        n_encrypted = len(self.encrypted_apps)
        n_opsec = len(self.opsec_indicators)
        has_hacking_search = any(
            f.finding_type.startswith("SAFARI_SUSPICIOUS") for f in self.findings
        )
        has_exploit_research = any(
            f.finding_type == "SAFARI_EXPLOIT_RESEARCH" for f in self.findings
        )
        has_phishing = any(
            f.finding_type == "SMS_PHISHING_RECEIVED" for f in self.findings
        )
        # B-072: empty solo si el conteo fue EXITOSO y dio 0. Un parseo fallido
        # o una DB ausente (parsed=False) NO cuenta como agenda/llamadas vacías
        # — no puede escalar data_minimization (evita falso INTENT/MALICE).
        empty_contacts = self.contacts_parsed and self.total_contacts == 0
        empty_calls = self.calls_parsed and self.total_calls == 0
        data_minimization = empty_contacts and empty_calls

        # Bump for opsec_indicators (BUG-011 fix: opsec contributes to z)
        opsec_bump = Fraction(0)
        if n_opsec >= 3:
            opsec_bump = Fraction(4, 10)
        elif n_opsec >= 2:
            opsec_bump = Fraction(2, 10)

        # Z-score escalation ladder — deterministic, no floats
        if has_exploit_research:
            z = Fraction(35, 10)
        elif n_encrypted >= 3 and data_minimization and has_hacking_search:
            z = Fraction(34, 10)
        elif n_encrypted >= 3 and data_minimization:
            z = Fraction(30, 10)
        elif n_encrypted >= 2 and has_hacking_search:
            z = Fraction(28, 10)
        elif has_hacking_search and data_minimization:
            z = Fraction(26, 10)
        elif n_encrypted >= 3:
            z = Fraction(24, 10)
        elif has_phishing and (n_encrypted >= 2 or data_minimization):
            # B-073 v2 — decisión de doctrina (Anna, opción b): phishing
            # recibido PUEDE alcanzar SUSPICION combinado con otras señales
            # (apps cifradas o data_minimization parseada), nunca solo.
            # z=2.2 cruza el umbral estricto >2 de _mobile_hypothesis; queda
            # debajo de las combinaciones con búsqueda ACTIVA (2.6/2.8)
            # porque el phishing sigue siendo una señal pasiva.
            z = Fraction(22, 10)
        elif n_encrypted >= 2:
            z = Fraction(20, 10)
        elif has_hacking_search:
            z = Fraction(18, 10)
        elif has_phishing:
            # B-073: phishing SOLO — señal PASIVA (recibido, no generado por
            # el usuario), pesa menos que la búsqueda activa de exploits
            # (has_hacking_search=1.8) y por sí sola no alcanza SUSPICION (>2)
            # ni con el opsec_bump máximo (1.6+0.4=2.0, y el umbral es
            # estricto). La vía a SUSPICION es la rama combinada de arriba
            # (doctrina B-073 v2).
            z = Fraction(16, 10)
        elif n_encrypted >= 1 and (empty_contacts or empty_calls):
            z = Fraction(16, 10)
        elif self.findings:
            z = Fraction(12, 10)

        # Apply opsec bump (capped at Z_CLIP_MAX)
        z = min(z + opsec_bump, Fraction(int(Z_CLIP_MAX), 1))

        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))

        # SignalOutput boundary: value and z_score are float by SignalOutput contract.
        # Fraction arithmetic ends here — same boundary as event_log_correlator.py.
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip) if z_clip > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "device_name": self.device_name,
                "ios_version": self.ios_version,
                "owner_name": self.owner_name,
                "total_sms": self.total_sms,
                "total_contacts": self.total_contacts,
                "total_calls": self.total_calls,
                "total_safari_entries": self.total_safari_entries,
                "encrypted_apps_count": n_encrypted,
                "opsec_indicators_count": n_opsec,
                "data_minimization": data_minimization,
                "findings_count": len(self.findings),
                "composite_score": str(self.composite_score),
                "artifact_type": "ios_forensic",
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

class iOSForensicsAnalyzer:
    """
    Analyzes iOS forensic extractions (GrayKey, Cellebrite, manual).

    Expects a directory containing any combination of:
    - sms.db / SMS database
    - AddressBook.sqlitedb
    - CallHistory.storedata
    - Safari/History.db
    - *.plist files (keychain, app configs)
    - passwords.txt (extracted keychain)
    - pchistory.txt (passcode history)
    """

    def __init__(self):
        self._findings: List[iOSFinding] = []
        self._encrypted_apps: List[Dict[str, Any]] = []
        self._opsec_indicators: List[Dict[str, Any]] = []

    def analyze(
        self,
        evidence_path: Path,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> iOSAnalysisResult:
        self._findings = []
        self._encrypted_apps = []
        self._opsec_indicators = []

        evidence_path = Path(evidence_path)
        if not evidence_path.is_dir():
            logger.warning("[IOS] Evidence path is not a directory: %s", evidence_path)
            return iOSAnalysisResult(
                source_path=str(evidence_path),
                analysis_notes=["Evidence path is not a directory."],
            )

        result = iOSAnalysisResult(source_path=str(evidence_path))

        # Validate this looks like iOS evidence (BUG-007 fix)
        all_files = {f.name for f in evidence_path.rglob("*") if f.is_file() and not f.is_symlink()}
        ios_markers = all_files & _IOS_MARKER_FILES
        if not ios_markers:
            logger.warning("[IOS] No iOS artifacts found in %s", evidence_path)
            result.analysis_notes.append(
                "No iOS-specific artifacts found (sms.db, AddressBook.sqlitedb, etc.). "
                "Directory may not contain iOS evidence."
            )
            # Continue anyway — plist/passwords might still be present

        # 1. SMS / iMessage database
        for sms_db in self._safe_rglob(evidence_path, "sms.db", limit=3):
            try:
                self._analyze_sms(sms_db, result)
            except Exception as e:
                logger.error("[IOS] SMS analysis failed for %s: %s", sms_db, e)
                result.analysis_notes.append(f"SMS parse error: {e}")

        # 2. AddressBook
        for ab in self._safe_rglob(evidence_path, "AddressBook.sqlitedb", limit=3):
            try:
                self._analyze_contacts(ab, result)
            except Exception as e:
                logger.error("[IOS] Contacts analysis failed: %s", e)
                result.analysis_notes.append(f"Contacts parse error: {e}")

        # 3. Call history
        for ch in self._safe_rglob(evidence_path, "CallHistory.storedata", limit=3):
            try:
                self._analyze_call_history(ch, result)
            except Exception as e:
                logger.error("[IOS] Call history analysis failed: %s", e)
                result.analysis_notes.append(f"Call history parse error: {e}")

        # 4. Safari history
        for sdb in self._safe_rglob(evidence_path, "History.db", limit=3):
            try:
                self._analyze_safari(sdb, result)
            except Exception as e:
                logger.error("[IOS] Safari analysis failed: %s", e)
                result.analysis_notes.append(f"Safari parse error: {e}")

        # 5. App detection
        self._detect_installed_apps(evidence_path, result)

        # 6. Passwords / keychain
        for pw_file in self._safe_rglob(evidence_path, "passwords.txt", limit=2):
            try:
                self._analyze_passwords(pw_file, result)
            except Exception as e:
                logger.error("[IOS] Passwords analysis failed: %s", e)
                result.analysis_notes.append(f"Passwords parse error: {e}")

        # 7. Passcode history
        for pc_file in self._safe_rglob(evidence_path, "pchistory.txt", limit=2):
            try:
                self._analyze_passcode_history(pc_file, result)
            except Exception as e:
                logger.error("[IOS] Passcode history failed: %s", e)
                result.analysis_notes.append(f"Passcode parse error: {e}")

        # 8. OPSEC composite assessment
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
    def _safe_sqlite_connect(db_path: Path) -> Optional[sqlite3.Connection]:
        """Open SQLite evidence read-only + immutable (B-071 → _sql_utils).
        Never writes to evidence, never creates an empty DB on a missing path."""
        return safe_sqlite_connect(db_path, "IOS", logger)

    # ── SMS ─────────────────────────────────────────────────────────────────

    def _analyze_sms(self, db_path: Path, result: iOSAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"sms.db: could not open {db_path}")
            return
        try:
            conn.row_factory = sqlite3.Row
            try:
                count = conn.execute("SELECT COUNT(*) FROM message").fetchone()[0]
                result.total_sms = count
            except sqlite3.OperationalError:
                result.analysis_notes.append("sms.db: 'message' table not found")
                return

            try:
                rows = conn.execute(
                    "SELECT ROWID, text, is_from_me, date, service "
                    "FROM message WHERE text IS NOT NULL LIMIT 500"
                ).fetchall()
            except sqlite3.OperationalError:
                return

            for row in rows:
                text = row["text"] or ""
                ts = row["date"] or 0

                text_safe = text[:2000]  # ReDoS guard
                for pattern, severity, mitre in PHISHING_PATTERNS:
                    if re.search(pattern, text_safe):
                        self._findings.append(iOSFinding(
                            finding_type="SMS_PHISHING_RECEIVED",
                            severity=severity,
                            description=f"SMS matches phishing pattern",
                            evidence=text[:200] + ("[truncated]" if len(text) > 200 else ""),
                            mitre_technique=mitre,
                            rule_ref="IOS-SMS-PHISH",
                            timestamp=ts,
                            corr_group="sms_phishing",
                        ))
                        break

                for app_id, (desc, sev) in ENCRYPTED_APPS.items():
                    app_short = app_id.split(".")[-1].lower()
                    if app_short in text_safe.lower() and row["is_from_me"]:
                        self._findings.append(iOSFinding(
                            finding_type="SMS_ENCRYPTED_RECRUITMENT",
                            severity=sev,
                            description=f"Outgoing SMS recruiting contact to {desc}",
                            evidence=text[:200] + ("[truncated]" if len(text) > 200 else ""),
                            mitre_technique="T1573",
                            rule_ref="IOS-SMS-RECRUIT",
                            timestamp=ts,
                            corr_group="encrypted_apps",
                        ))
                        break
        finally:
            conn.close()

    # ── Contacts ────────────────────────────────────────────────────────────

    def _analyze_contacts(self, db_path: Path, result: iOSAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"AddressBook: could not open {db_path}")
            return
        parsed = False
        try:
            try:
                count = conn.execute("SELECT COUNT(*) FROM ABPerson").fetchone()[0]
                result.total_contacts = count
                parsed = True
            except sqlite3.OperationalError:
                try:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM ABPersonFullTextSearch_content"
                    ).fetchone()[0]
                    result.total_contacts = count
                    parsed = True
                except sqlite3.OperationalError:
                    result.analysis_notes.append("AddressBook: could not count contacts")
        finally:
            conn.close()

        result.contacts_parsed = parsed

        # B-072: no conflar "no-parseable" con "vacío". Solo un conteo EXITOSO
        # de 0 es evidencia de agenda borrada (data_minimization). Un fallo de
        # parseo (schema desconocido) NO puede escalar el veredicto — sería
        # incapacidad de análisis presentada como señal (familia P0-A). El
        # analysis_note ya deja rastro para que el veredicto abstenga. El flag
        # contacts_parsed corta la escalación en to_signal (no solo el finding).
        if parsed and result.total_contacts == 0:
            self._opsec_indicators.append({
                "indicator": "EMPTY_CONTACTS",
                "severity": str(Fraction(60, 100)),
                "description": "AddressBook completely empty — all comms via encrypted apps",
            })
            # Also add to findings so it contributes to score (P2-003 fix)
            self._findings.append(iOSFinding(
                finding_type="EMPTY_CONTACTS",
                severity=Fraction(45, 100),
                description="AddressBook database is completely empty despite active device use",
                evidence=f"ABPerson count: 0 in {db_path.name}",
                mitre_technique="T1070",
                rule_ref="IOS-CONTACTS-EMPTY",
                corr_group="data_minimization",
            ))

    # ── Call History ────────────────────────────────────────────────────────

    def _analyze_call_history(self, db_path: Path, result: iOSAnalysisResult) -> None:
        conn = self._safe_sqlite_connect(db_path)
        if conn is None:
            result.analysis_notes.append(f"CallHistory: could not open {db_path}")
            return
        try:
            try:
                count = conn.execute("SELECT COUNT(*) FROM ZCALLRECORD").fetchone()[0]
                result.total_calls = count
                result.calls_parsed = True  # B-072
            except sqlite3.OperationalError:
                result.analysis_notes.append("CallHistory: 'ZCALLRECORD' table not found")
                return
        finally:
            conn.close()

        if result.total_calls == 0:
            self._opsec_indicators.append({
                "indicator": "EMPTY_CALL_HISTORY",
                "severity": str(Fraction(55, 100)),
                "description": "Call history completely empty",
            })
            self._findings.append(iOSFinding(
                finding_type="EMPTY_CALL_HISTORY",
                severity=Fraction(40, 100),
                description="Call history database is completely empty",
                evidence=f"ZCALLRECORD count: 0 in {db_path.name}",
                mitre_technique="T1070",
                rule_ref="IOS-CALLS-EMPTY",
                corr_group="data_minimization",
            ))

    # ── Safari ──────────────────────────────────────────────────────────────

    def _analyze_safari(self, db_path: Path, result: iOSAnalysisResult) -> None:
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

                # Patterns are sorted by severity descending — break gets highest
                for pattern, severity, mitre in SUSPICIOUS_SEARCH_PATTERNS:
                    if re.search(pattern, combined):
                        finding_type = (
                            "SAFARI_EXPLOIT_RESEARCH"
                            if severity >= Fraction(80, 100)
                            else "SAFARI_SUSPICIOUS"
                        )
                        self._findings.append(iOSFinding(
                            finding_type=finding_type,
                            severity=severity,
                            description=f"Safari history matches suspicious pattern",
                            evidence=(
                                f"URL: {url[:150]}"
                                + ("[truncated]" if len(url) > 150 else "")
                                + f" | Title: {title[:100]}"
                            ),
                            mitre_technique=mitre,
                            rule_ref="IOS-SAFARI-SUSP",
                            timestamp=ts,
                            corr_group="browser_suspicious",
                        ))
                        break  # Highest severity first, so break is safe
        finally:
            conn.close()

    # ── App Detection ───────────────────────────────────────────────────────

    def _detect_installed_apps(self, evidence_path: Path, result: iOSAnalysisResult) -> None:
        """Detect installed encrypted/suspicious apps by scanning for app directories."""
        for bundle_id, (desc, severity) in ENCRYPTED_APPS.items():
            # Search for exact app container directory (BUG-006 fix: avoid substring matches)
            # iOS stores apps in containers: Library/Application Support/<bundle_id>/
            # or Containers/Data/Application/<uuid>/ with metadata plist containing bundle_id
            matches = list(evidence_path.rglob(f"*/{bundle_id}"))
            if not matches:
                # Fallback: search for bundle ID in plist files
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

        # Signal detection by filename — logical extractions (loose files without
        # full iOS app directory structure) expose signal.sqlite directly.
        # Same weight as detection by bundle_id "org.whispersystems.signal".
        signal_db_matches = (
            list(evidence_path.glob("signal.sqlite"))
            + [p for d in evidence_path.iterdir() if d.is_dir()
               for p in d.glob("signal.sqlite")]
        )
        if signal_db_matches and not any(
            app["bundle_id"] == "org.whispersystems.signal"
            for app in self._encrypted_apps
        ):
            self._encrypted_apps.append({
                "bundle_id": "org.whispersystems.signal",
                "description": "Signal — end-to-end encrypted messaging (filename detection)",
                "severity": str(Fraction(60, 100)),
                "paths_found": len(signal_db_matches),
            })

        # Psiphon tunneling framework
        # Case-insensitive Psiphon detection
        psiphon_matches = [
            p for p in evidence_path.rglob("*")
            if not p.is_symlink() and "psiphon" in p.name.lower()
        ]
        if psiphon_matches:
            self._findings.append(iOSFinding(
                finding_type="PSIPHON_TUNNELING_DETECTED",
                severity=Fraction(75, 100),
                description="PsiphonTunnel framework — censorship circumvention VPN",
                evidence=str(psiphon_matches[0].name)[:200],
                mitre_technique="T1572",
                rule_ref="IOS-APP-PSIPHON",
                corr_group="encrypted_apps",
            ))

    # ── Passwords ───────────────────────────────────────────────────────────

    def _analyze_passwords(self, pw_path: Path, result: iOSAnalysisResult) -> None:
        """Analyze exported keychain passwords for credential reuse patterns."""
        text = pw_path.read_text(encoding="utf-8", errors="ignore")[:50000]

        # Only parse files that look like keychain exports (BUG-009 fix)
        if not any(kw in text[:500].lower() for kw in ("password", "keychain", "service", "account")):
            return

        passwords = re.findall(r'password["\s:=]+([^\s"]{4,})', text, re.IGNORECASE)
        if len(passwords) < 3:
            return

        suffixes: Dict[str, int] = {}
        for pw in passwords:
            if len(pw) >= 4:
                suffix = pw[-4:]
                suffixes[suffix] = suffixes.get(suffix, 0) + 1

        for suffix, count in suffixes.items():
            if count >= 3:
                self._findings.append(iOSFinding(
                    finding_type="CREDENTIAL_REUSE_PATTERN",
                    severity=Fraction(35, 100),
                    description=f"Credential reuse: suffix '{suffix}' in {count}+ passwords",
                    evidence=f"Suffix: {suffix}, count: {count}",
                    mitre_technique="T1078",
                    rule_ref="IOS-CRED-REUSE",
                    corr_group="credential_patterns",
                ))
                break

    # ── Passcode History ────────────────────────────────────────────────────

    def _analyze_passcode_history(self, pc_path: Path, result: iOSAnalysisResult) -> None:
        text = pc_path.read_text(encoding="utf-8", errors="ignore")[:5000]

        weak_patterns = [
            r"(\d)\1{5}",          # 000000, 111111
            r"123456|654321",       # Sequential
            r"000000|999999",       # Trivial
            r"(\d{3})\1",          # Repeating triple (185185)
        ]
        for pattern in weak_patterns:
            if re.search(pattern, text):
                self._findings.append(iOSFinding(
                    finding_type="WEAK_PASSCODE",
                    severity=Fraction(20, 100),
                    description="Weak device passcode in passcode history",
                    evidence=f"Pattern: {pattern}",
                    mitre_technique="T1110",
                    rule_ref="IOS-PASSCODE-WEAK",
                    corr_group="credential_patterns",
                ))
                break

    # ── OPSEC Assessment ────────────────────────────────────────────────────

    def _assess_opsec(self, result: iOSAnalysisResult) -> None:
        n_encrypted = len(self._encrypted_apps)
        empty_contacts = result.total_contacts == 0
        empty_calls = result.total_calls == 0

        if n_encrypted >= 3:
            self._opsec_indicators.append({
                "indicator": "MULTI_ENCRYPTED_APPS",
                "severity": str(Fraction(70, 100)),
                "description": f"{n_encrypted} encrypted messaging apps installed",
            })
            self._findings.append(iOSFinding(
                finding_type="OPSEC_MULTI_ENCRYPTED_APPS",
                severity=Fraction(70, 100),
                description=f"{n_encrypted} encrypted messaging apps — deliberate OPSEC posture",
                evidence=", ".join(a["bundle_id"] for a in self._encrypted_apps),
                mitre_technique="T1573",
                rule_ref="IOS-OPSEC-MULTI",
                corr_group="encrypted_apps",
            ))
        elif n_encrypted >= 2:
            self._opsec_indicators.append({
                "indicator": "DUAL_ENCRYPTED_APPS",
                "severity": str(Fraction(50, 100)),
                "description": f"{n_encrypted} encrypted messaging apps installed",
            })

        if empty_contacts and empty_calls and n_encrypted >= 1:
            self._findings.append(iOSFinding(
                finding_type="OPSEC_DATA_MINIMIZATION",
                severity=Fraction(65, 100),
                description="Data minimization: zero contacts + zero calls + encrypted app presence",
                evidence=f"contacts={result.total_contacts}, calls={result.total_calls}, "
                         f"encrypted_apps={n_encrypted}",
                mitre_technique="T1070",
                rule_ref="IOS-OPSEC-MINIMIZE",
                corr_group="data_minimization",
            ))
