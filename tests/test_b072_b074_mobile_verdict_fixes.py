"""
B-072 / B-073 / B-074 — defectos de veredicto confirmados por
AUDITORIA_COBERTURA_MOBILE_SIFT, corregidos.

B-072: conflación "no-parseable == vacío". Un schema desconocido (OperationalError)
       dejaba el contador en default 0 -> EMPTY_* -> data_minimization -> falso
       INTENT/MALICE. Ahora solo un conteo EXITOSO de 0 escala.
B-073: has_phishing (iOS) se computaba y nunca entraba a la escalera (rama muerta).
B-074: has_sip_disabled (macOS) siempre False (SIP_DISABLED nunca se emitía) ->
       ramas de veredicto z=3.4/z=2.4 muertas. Ahora _detect_sip_status lo emite.
"""

import sqlite3
from fractions import Fraction

import pytest

from vigia.sift.ios_forensics import iOSForensicsAnalyzer, iOSAnalysisResult, iOSFinding
from vigia.sift.android_forensics import AndroidForensicsAnalyzer, AndroidAnalysisResult
from vigia.sift.macos_forensics import MacOSForensicsAnalyzer, MacOSAnalysisResult


# ===========================================================================
# B-072 — no-parseable != vacío
# ===========================================================================

def _make_db(path, schema_sql):
    c = sqlite3.connect(str(path))
    for stmt in schema_sql:
        c.execute(stmt)
    c.commit()
    c.close()


class TestB072ContactsConflation:
    def test_ios_unknown_schema_does_not_emit_empty(self, tmp_path):
        """AddressBook con schema desconocido (ni ABPerson ni FTS) -> NO EMPTY_CONTACTS."""
        db = tmp_path / "AddressBook.sqlitedb"
        _make_db(db, ["CREATE TABLE some_other_table(x)"])
        a = iOSForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = iOSAnalysisResult()
        a._analyze_contacts(db, r)
        assert not any(f.finding_type == "EMPTY_CONTACTS" for f in a._findings), \
            "schema no-parseable no debe emitir EMPTY_CONTACTS"
        assert any("could not count contacts" in n for n in r.analysis_notes)

    def test_ios_genuinely_empty_still_emits(self, tmp_path):
        """ABPerson existe y está vacía -> SÍ EMPTY_CONTACTS (conteo exitoso de 0)."""
        db = tmp_path / "AddressBook.sqlitedb"
        _make_db(db, ["CREATE TABLE ABPerson(ROWID INTEGER)"])
        a = iOSForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = iOSAnalysisResult()
        a._analyze_contacts(db, r)
        assert any(f.finding_type == "EMPTY_CONTACTS" for f in a._findings)

    def test_android_unknown_schema_no_empty(self, tmp_path):
        db = tmp_path / "contacts2.db"
        _make_db(db, ["CREATE TABLE other(x)"])
        a = AndroidForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = AndroidAnalysisResult()
        a._analyze_contacts(db, r)
        assert not any(f.finding_type == "EMPTY_CONTACTS" for f in a._findings)

    def test_android_call_log_unknown_schema_no_empty(self, tmp_path):
        db = tmp_path / "calllog.db"
        _make_db(db, ["CREATE TABLE other(x)"])
        a = AndroidForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = AndroidAnalysisResult()
        a._analyze_call_log(db, r)
        assert not any(f.finding_type == "EMPTY_CALL_LOG" for f in a._findings)

    def test_android_call_log_genuinely_empty_still_emits(self, tmp_path):
        db = tmp_path / "calllog.db"
        _make_db(db, ["CREATE TABLE calls(_id INTEGER)"])
        a = AndroidForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = AndroidAnalysisResult()
        a._analyze_call_log(db, r)
        assert any(f.finding_type == "EMPTY_CALL_LOG" for f in a._findings)


# ===========================================================================
# B-073 — has_phishing entra a la escalera iOS
# ===========================================================================

def _ios_finding(ft):
    return iOSFinding(finding_type=ft, severity=Fraction(1, 2), description="d",
                      evidence="e", mitre_technique="T1", rule_ref="r", corr_group="g")


class TestB073PhishingLadder:
    def test_phishing_now_lifts_zscore_above_floor(self):
        r = iOSAnalysisResult()
        r.findings = [_ios_finding("SMS_PHISHING_RECEIVED")]
        z_phish = r.to_signal().z_score

        r2 = iOSAnalysisResult()
        r2.findings = [_ios_finding("SOME_OTHER_FINDING")]
        z_generic = r2.to_signal().z_score

        # phishing (1.6) debe pesar más que un finding genérico (1.2)
        assert z_phish > z_generic
        assert z_phish == pytest.approx(1.6)

    def test_phishing_alone_below_suspicion(self):
        """Señal pasiva: phishing solo no alcanza SUSPICION (z>2 en _mobile_hypothesis)."""
        r = iOSAnalysisResult()
        r.findings = [_ios_finding("SMS_PHISHING_RECEIVED")]
        assert r.to_signal().z_score <= 2.0


# ===========================================================================
# B-074 — SIP_DISABLED se emite desde chequeo real -> ramas vivas
# ===========================================================================

class TestB074SipDetection:
    def test_csrutil_disable_in_history_emits_sip_disabled(self, tmp_path):
        # árbol con marcador macOS + shell history con csrutil disable
        (tmp_path / "SystemVersion.plist").write_bytes(b"bplist00")
        hist = tmp_path / ".zsh_history"
        hist.write_text("cd /tmp\ncsrutil disable\nsudo reboot\n")
        a = MacOSForensicsAnalyzer()
        a._findings = []
        r = MacOSAnalysisResult()
        a._detect_sip_status(tmp_path, r)
        assert any(f.finding_type == "SIP_DISABLED" for f in a._findings)

    def test_no_evidence_emits_no_finding_but_notes(self, tmp_path):
        hist = tmp_path / ".bash_history"
        hist.write_text("ls -la\ncd Documents\n")
        a = MacOSForensicsAnalyzer()
        a._findings = []
        r = MacOSAnalysisResult()
        a._detect_sip_status(tmp_path, r)
        assert not any(f.finding_type == "SIP_DISABLED" for f in a._findings)
        assert any("SIP status undetermined" in n for n in r.analysis_notes)

    def test_sip_disabled_makes_dead_branch_reachable(self):
        """Con SIP_DISABLED + ANTIFORENSIC la rama z=2.4 (antes muerta) fira."""
        from vigia.sift.macos_forensics import MacOSFinding

        def mf(ft):
            return MacOSFinding(finding_type=ft, severity=Fraction(1, 2), description="d",
                                evidence="e", mitre_technique="T1", rule_ref="r", corr_group="antiforensic")
        r = MacOSAnalysisResult()
        r.findings = [mf("SIP_DISABLED"), mf("ANTIFORENSIC_LOG_DELETION")]
        z = r.to_signal().z_score
        # la rama has_sip_disabled and has_antiforensic -> z=2.4 (antes inalcanzable)
        assert z == pytest.approx(2.4)
