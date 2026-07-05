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


class TestB072DataMinimizationEscalation:
    """El bug REAL (red-team): removimos el finding EMPTY_* pero to_signal
    escalaba igual vía data_minimization = (total_contacts==0 and total_calls==0),
    leyendo el contador crudo (0 por default tras un parseo fallido). El fix con
    centinela contacts_parsed/calls_parsed corta la escalación, no solo el finding."""

    def _ios(self, contacts_parsed, calls_parsed):
        r = iOSAnalysisResult()
        r.encrypted_apps = [{"a": 1}, {"a": 2}, {"a": 3}]
        r.total_contacts = 0
        r.total_calls = 0
        r.contacts_parsed = contacts_parsed
        r.calls_parsed = calls_parsed
        r.findings = [iOSFinding(finding_type="X", severity=Fraction(1, 2),
                                 description="d", evidence="e", mitre_technique="T1",
                                 rule_ref="r", corr_group="g")]
        return r

    def test_parse_failure_does_not_escalate(self):
        """Contadores 0 por PARSEO FALLIDO (parsed=False) -> NO data_minimization."""
        z_fail = self._ios(False, False).to_signal().z_score
        # mismo caso con datos reales (no vacío) para comparar
        r = self._ios(True, True)
        r.total_contacts = 50
        r.total_calls = 30
        z_data = r.to_signal().z_score
        assert z_fail == z_data, (
            f"parseo fallido escaló ({z_fail}) distinto que datos reales ({z_data}) "
            f"— data_minimization todavía se dispara sobre no-parseable (bug cosmético)"
        )

    def test_genuinely_empty_still_escalates(self):
        """Agenda REAL vacía (parsed=True, count=0) -> SÍ data_minimization."""
        z_empty = self._ios(True, True).to_signal().z_score
        z_fail = self._ios(False, False).to_signal().z_score
        assert z_empty > z_fail, "el empty real parseado debe seguir escalando"

    def test_end_to_end_unparseable_leaves_flags_false(self, tmp_path):
        """_analyze_contacts sobre schema desconocido deja contacts_parsed=False."""
        db = tmp_path / "AddressBook.sqlitedb"
        _make_db(db, ["CREATE TABLE nope(x)"])
        a = iOSForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = iOSAnalysisResult()
        a._analyze_contacts(db, r)
        assert r.contacts_parsed is False

    def test_end_to_end_parsed_sets_flag_true(self, tmp_path):
        db = tmp_path / "AddressBook.sqlitedb"
        _make_db(db, ["CREATE TABLE ABPerson(ROWID INTEGER)"])
        a = iOSForensicsAnalyzer()
        a._findings = []
        a._opsec_indicators = []
        r = iOSAnalysisResult()
        a._analyze_contacts(db, r)
        assert r.contacts_parsed is True


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

    def test_phishing_alone_with_max_bump_still_below_suspicion(self):
        """Doctrina B-073 (b): ni con el opsec_bump máximo el phishing solo
        cruza — 1.6+0.4=2.0 y el umbral de _mobile_hypothesis es estricto >2."""
        r = iOSAnalysisResult()
        r.findings = [_ios_finding("SMS_PHISHING_RECEIVED")]
        r.opsec_indicators = [{"i": 1}, {"i": 2}, {"i": 3}]
        assert r.to_signal().z_score <= 2.0


class TestB073DoctrineCombined:
    """Doctrina B-073 v2 (decisión de Anna, opción b): phishing recibido PUEDE
    alcanzar SUSPICION combinado con otras señales — nunca solo."""

    def _base(self):
        r = iOSAnalysisResult()
        r.findings = [_ios_finding("SMS_PHISHING_RECEIVED")]
        r.contacts_parsed = r.calls_parsed = True
        r.total_contacts, r.total_calls = 50, 30
        return r

    def test_phishing_plus_encrypted_apps_reaches_suspicion(self):
        r = self._base()
        r.encrypted_apps = [{"a": 1}, {"a": 2}]
        z = r.to_signal().z_score
        assert z > 2.0, f"phishing + 2 apps cifradas debe cruzar SUSPICION (z={z})"

    def test_phishing_plus_parsed_data_minimization_reaches_suspicion(self):
        r = self._base()
        r.total_contacts, r.total_calls = 0, 0  # parseado Y vacío
        z = r.to_signal().z_score
        assert z > 2.0

    def test_phishing_plus_unparsed_counters_does_not_combine(self):
        """Interacción con B-072: contadores en 0 por parseo FALLIDO no son
        data_minimization — la rama combinada NO se habilita."""
        r = iOSAnalysisResult()
        r.findings = [_ios_finding("SMS_PHISHING_RECEIVED")]
        r.total_contacts, r.total_calls = 0, 0  # parsed=False (default)
        assert r.to_signal().z_score <= 2.0

    def test_combined_stays_below_active_search_combos(self):
        """El phishing es pasivo: su combinación (2.2) queda debajo de las
        combinaciones con búsqueda ACTIVA (hacking+data_min=2.6, enc2+hacking=2.8)."""
        r = self._base()
        r.encrypted_apps = [{"a": 1}, {"a": 2}]
        z_phish_combo = r.to_signal().z_score

        r2 = self._base()
        r2.findings = [_ios_finding("SAFARI_SUSPICIOUS_SITE")]
        r2.encrypted_apps = [{"a": 1}, {"a": 2}]
        z_active_combo = r2.to_signal().z_score
        assert z_phish_combo < z_active_combo

    def test_existing_branches_unchanged(self):
        """Sin phishing, nada se mueve: 2 apps=2.0, hacking solo=1.8."""
        r = iOSAnalysisResult()
        r.encrypted_apps = [{"a": 1}, {"a": 2}]
        assert r.to_signal().z_score == pytest.approx(2.0)
        r2 = iOSAnalysisResult()
        r2.findings = [_ios_finding("SAFARI_SUSPICIOUS_SITE")]
        assert r2.to_signal().z_score == pytest.approx(1.8)


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


class TestB074NvramAuthoritative:
    """B-074 v2: la fuente autoritativa es la NVRAM csr-active-config, para
    recall real (el red-team mostró que shell-history solo rara vez fira)."""

    def _nvram(self, tmp_path, value):
        import plistlib
        with open(tmp_path / "nvram.plist", "wb") as f:
            plistlib.dump({"csr-active-config": value.to_bytes(4, "little")}, f)

    def _run(self, tmp_path):
        (tmp_path / "SystemVersion.plist").write_bytes(b"x")
        a = MacOSForensicsAnalyzer()
        a._findings = []
        r = MacOSAnalysisResult()
        a._detect_sip_status(tmp_path, r)
        return a._findings, r.analysis_notes

    def test_nvram_disabled_emits_finding_with_flags(self, tmp_path):
        self._nvram(tmp_path, 0x77)  # csrutil disable típico
        findings, _ = self._run(tmp_path)
        sip = [f for f in findings if f.finding_type == "SIP_DISABLED"]
        assert sip
        assert "0x77" in sip[0].evidence
        assert "UNRESTRICTED_FS" in sip[0].evidence
        assert sip[0].rule_ref == "MACOS-SIP-DISABLED-NVRAM"

    def test_nvram_enabled_no_finding_authoritative_note(self, tmp_path):
        self._nvram(tmp_path, 0x0)
        findings, notes = self._run(tmp_path)
        assert not any(f.finding_type == "SIP_DISABLED" for f in findings)
        assert any("SIP enabled (authoritative" in n for n in notes)

    def test_nvram_overrides_shell_history(self, tmp_path):
        """NVRAM 0x0 (SIP ON) gana sobre un csrutil disable en history (intento
        fallido / re-habilitado). El estado autoritativo manda."""
        self._nvram(tmp_path, 0x0)
        (tmp_path / ".zsh_history").write_text("csrutil disable\n")
        findings, notes = self._run(tmp_path)
        assert not any(f.finding_type == "SIP_DISABLED" for f in findings)
        assert any("SIP enabled (authoritative" in n for n in notes)

    def test_nvram_guid_prefixed_key(self, tmp_path):
        import plistlib
        key = "7C436110-AB2A-4BBB-A880-FE41995C9F82:csr-active-config"
        with open(tmp_path / "nvram.plist", "wb") as f:
            plistlib.dump({key: (0x77).to_bytes(4, "little")}, f)
        findings, _ = self._run(tmp_path)
        assert any(f.finding_type == "SIP_DISABLED" for f in findings)


class TestB074CsrParser:
    def test_parse_bytes_little_endian(self):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer as M
        v, flags = M._parse_csr_config((0x77).to_bytes(4, "little"))
        assert v == 0x77
        assert "UNRESTRICTED_FS" in flags

    def test_parse_zero(self):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer as M
        v, flags = M._parse_csr_config(b"\x00\x00\x00\x00")
        assert v == 0 and flags == []

    def test_parse_hex_string_and_int(self):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer as M
        assert M._parse_csr_config("0x3")[0] == 3
        assert M._parse_csr_config(3)[0] == 3

    def test_parse_garbage_returns_none(self):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer as M
        assert M._parse_csr_config(b"") is None
        assert M._parse_csr_config("notanumber") is None
        assert M._parse_csr_config(True) is None  # bool no es int válido acá


class TestB074SipAntiforensicDoctrine:
    """Doctrina B-074 (Anna): SIP_DISABLED cuenta como anti-forense (T1562.001)
    y escala por sí solo — PERO sin inflar perfiles inocentes (SIP + apps de
    mensajería normales) a INTENT. Las combinaciones fuertes exigen un acto
    anti-forense SEPARADO."""

    def _mf(self, ft):
        from vigia.sift.macos_forensics import MacOSFinding
        return MacOSFinding(finding_type=ft, severity=Fraction(1, 2), description="d",
                            evidence="e", mitre_technique="T1", rule_ref="r", corr_group="g")

    def _z(self, findings=(), n_enc=0):
        r = MacOSAnalysisResult()
        r.findings = [self._mf(f) for f in findings]
        r.encrypted_apps = [{"a": i} for i in range(n_enc)]
        return r.to_signal().z_score

    def test_sip_alone_reaches_suspicion(self):
        """El objetivo de la doctrina: SIP escala por sí solo (>2)."""
        assert self._z(["SIP_DISABLED"]) == pytest.approx(2.4)

    def test_sip_plus_normal_apps_stays_suspicion_not_intent(self):
        """FP-avoidance: SIP + apps cifradas normales NO salta a INTENT."""
        z2 = self._z(["SIP_DISABLED"], n_enc=2)
        z3 = self._z(["SIP_DISABLED"], n_enc=3)
        assert z2 == pytest.approx(2.4) and z2 <= 3.0
        assert z3 == pytest.approx(2.4)

    def test_sip_plus_exploit_escalates(self):
        """SIP cuenta como anti-forense en el combo con exploit -> 3.8."""
        assert self._z(["SIP_DISABLED", "SAFARI_EXPLOIT_RESEARCH"]) == pytest.approx(3.8)

    def test_genuine_triple_still_distinguished(self):
        """SIP + acto anti-forense REAL + apps -> 3.4 (el triple genuino)."""
        assert self._z(["SIP_DISABLED", "ANTIFORENSIC_LOG_DELETION"], n_enc=2) == pytest.approx(3.4)

    def test_controls_unchanged(self):
        """Sin SIP, nada se mueve."""
        assert self._z(["ANTIFORENSIC_LOG_DELETION"], n_enc=2) == pytest.approx(2.8)
        assert self._z(n_enc=2) == pytest.approx(2.0)
        assert self._z(["SAFARI_EXPLOIT_RESEARCH"]) == pytest.approx(3.5)
