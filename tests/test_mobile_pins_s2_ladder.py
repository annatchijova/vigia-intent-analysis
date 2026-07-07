"""
Pins S2 — escalera to_signal COMPLETA de los 3 módulos mobile
(AUDITORIA_COBERTURA_MOBILE_SIFT §A; WHAT_IS_NEXT §1.3.1).

Propósito: arnés previo a B-052-P2. Cada rama de cada escalera queda fijada
con inputs mínimos que la alcanzan exactamente — un cambio de lógica que
mueva cualquier z rompe acá primero, con un diff legible (rama por rama), no
como una regresión opaca de corpus.

Incluye el CAZADOR DE RAMAS MUERTAS (la clase de defecto S2 que B-073/B-074
cerraron): todo finding_type que la escalera LEE debe tener un emisor en el
módulo fuera de to_signal. Hoy 0 ramas muertas — este pin impide reintroducirlas.
"""

import re
from fractions import Fraction
from pathlib import Path

import pytest

from vigia.sift.android_forensics import AndroidAnalysisResult, AndroidFinding
from vigia.sift.ios_forensics import iOSAnalysisResult, iOSFinding
from vigia.sift.macos_forensics import MacOSAnalysisResult, MacOSFinding

REPO = Path(__file__).resolve().parent.parent

# ── constructores mínimos ──────────────────────────────────────────────────


def _f_ios(ftype):
    return iOSFinding(ftype, Fraction(1, 2), "d", "e", "T0000", "R-0")


def _f_and(ftype):
    return AndroidFinding(ftype, Fraction(1, 2), "d", "e", "T0000", "R-0")


def _f_mac(ftype):
    return MacOSFinding(ftype, Fraction(1, 2), "d", "e", "T0000", "R-0")


def _apps(n):
    return [{"app": f"enc-{i}"} for i in range(n)]


def _ops(n):
    return [{"indicator": f"op-{i}"} for i in range(n)]


def _z(result):
    return result.to_signal().z_score


# ── iOS: las 13 ramas, en orden de precedencia ─────────────────────────────

IOS_LADDER = [
    # (id, kwargs, z esperado)
    ("exploit_research", dict(findings=[_f_ios("SAFARI_EXPLOIT_RESEARCH")]), 3.5),
    ("enc3+dm+hack", dict(encrypted_apps=_apps(3), contacts_parsed=True,
                          calls_parsed=True,
                          findings=[_f_ios("SAFARI_SUSPICIOUS_SEARCH")]), 3.4),
    ("enc3+dm", dict(encrypted_apps=_apps(3), contacts_parsed=True,
                     calls_parsed=True, findings=[_f_ios("EMPTY_CONTACTS")]), 3.0),
    ("enc2+hack", dict(encrypted_apps=_apps(2),
                       findings=[_f_ios("SAFARI_SUSPICIOUS_SEARCH")]), 2.8),
    ("hack+dm", dict(contacts_parsed=True, calls_parsed=True,
                     findings=[_f_ios("SAFARI_SUSPICIOUS_SEARCH")]), 2.6),
    ("enc3", dict(encrypted_apps=_apps(3),
                  findings=[_f_ios("OPSEC_MULTI_ENCRYPTED_APPS")]), 2.4),
    ("phishing+enc2 (B-073v2)", dict(encrypted_apps=_apps(2),
                                     findings=[_f_ios("SMS_PHISHING_RECEIVED")]), 2.2),
    ("phishing+dm (B-073v2)", dict(contacts_parsed=True, calls_parsed=True,
                                   findings=[_f_ios("SMS_PHISHING_RECEIVED")]), 2.2),
    ("enc2", dict(encrypted_apps=_apps(2),
                  findings=[_f_ios("OPSEC_MULTI_ENCRYPTED_APPS")]), 2.0),
    ("hack_solo", dict(findings=[_f_ios("SAFARI_SUSPICIOUS_SEARCH")]), 1.8),
    ("phishing_solo (B-073)", dict(findings=[_f_ios("SMS_PHISHING_RECEIVED")]), 1.6),
    ("enc1+empty_contacts", dict(encrypted_apps=_apps(1), contacts_parsed=True,
                                 findings=[_f_ios("EMPTY_CONTACTS")]), 1.6),
    ("findings_solo", dict(findings=[_f_ios("WEAK_PASSCODE")]), 1.2),
    ("nada", dict(), 0.0),
]


class TestIOSLadder:
    @pytest.mark.parametrize("branch,kwargs,expected",
                             IOS_LADDER, ids=[b[0] for b in IOS_LADDER])
    def test_branch(self, branch, kwargs, expected):
        assert _z(iOSAnalysisResult(**kwargs)) == expected

    def test_opsec_bump_crossing_3_0_to_3_4(self):
        # La interacción no fijada que el audit señaló: enc3+dm = 3.0 y el
        # bump de 3 indicadores (+0.4) la CRUZA sobre el umbral estricto >3
        # de _mobile_hypothesis (SUSPICION→INTENT). Queda pineada como
        # comportamiento vigente — si B-052-P2 la cambia, que sea a propósito.
        r = iOSAnalysisResult(encrypted_apps=_apps(3), contacts_parsed=True,
                              calls_parsed=True,
                              findings=[_f_ios("EMPTY_CONTACTS")],
                              opsec_indicators=_ops(3))
        assert _z(r) == 3.4

    def test_opsec_bump_tiers(self):
        base = dict(findings=[_f_ios("WEAK_PASSCODE")])  # piso 1.2
        assert _z(iOSAnalysisResult(**base, opsec_indicators=_ops(1))) == 1.2
        assert _z(iOSAnalysisResult(**base, opsec_indicators=_ops(2))) == 1.4
        assert _z(iOSAnalysisResult(**base, opsec_indicators=_ops(3))) == 1.6

    def test_b072_unparsed_zero_does_not_minimize(self):
        # contadores en 0 con parsed=False: NO es data_minimization.
        r = iOSAnalysisResult(encrypted_apps=_apps(3),
                              findings=[_f_ios("OPSEC_MULTI_ENCRYPTED_APPS")])
        assert _z(r) == 2.4  # enc3, no enc3+dm=3.0

    def test_max_reachable_z_below_clip(self):
        # Techo real de la escalera: 3.5 + 0.4 = 3.9 < Z_CLIP_MAX=5.
        r = iOSAnalysisResult(findings=[_f_ios("SAFARI_EXPLOIT_RESEARCH")],
                              opsec_indicators=_ops(3))
        assert _z(r) == 3.9

    def test_confidence_cap(self):
        r = iOSAnalysisResult(findings=[_f_ios("WEAK_PASSCODE")],
                              composite_score=Fraction(2, 1))
        assert r.to_signal().confidence == 0.95

    def test_value_is_z_over_clip(self):
        s = iOSAnalysisResult(findings=[_f_ios("SAFARI_EXPLOIT_RESEARCH")]).to_signal()
        assert s.value == 3.5 / 5


# ── Android: las 10 ramas ──────────────────────────────────────────────────

AND_LADDER = [
    ("exploit+root", dict(is_rooted=True,
                          findings=[_f_and("BROWSER_EXPLOIT_RESEARCH")]), 3.8),
    ("exploit", dict(findings=[_f_and("BROWSER_EXPLOIT_RESEARCH")]), 3.5),
    ("exploit_bookmarked", dict(findings=[_f_and("BROWSER_EXPLOIT_BOOKMARKED")]), 3.5),
    ("root+enc2+dm", dict(is_rooted=True, encrypted_apps=_apps(2),
                          contacts_parsed=True, calls_parsed=True,
                          findings=[_f_and("DEVICE_ROOTED")]), 3.4),
    ("enc3+dm", dict(encrypted_apps=_apps(3), contacts_parsed=True,
                     calls_parsed=True, findings=[_f_and("EMPTY_CONTACTS")]), 3.0),
    ("root+enc2", dict(is_rooted=True, encrypted_apps=_apps(2),
                       findings=[_f_and("DEVICE_ROOTED")]), 2.8),
    ("enc3", dict(encrypted_apps=_apps(3),
                  findings=[_f_and("OPSEC_MULTI_ENCRYPTED_APPS")]), 2.4),
    ("root_solo", dict(is_rooted=True, findings=[_f_and("DEVICE_ROOTED")]), 2.0),
    ("enc2", dict(encrypted_apps=_apps(2),
                  findings=[_f_and("OPSEC_MULTI_ENCRYPTED_APPS")]), 1.8),
    ("findings_solo", dict(findings=[_f_and("SMS_ENCRYPTED_RECRUITMENT")]), 1.2),
    ("nada", dict(), 0.0),
]


class TestAndroidLadder:
    @pytest.mark.parametrize("branch,kwargs,expected",
                             AND_LADDER, ids=[b[0] for b in AND_LADDER])
    def test_branch(self, branch, kwargs, expected):
        assert _z(AndroidAnalysisResult(**kwargs)) == expected

    def test_opsec_bump_crossing(self):
        # enc3+dm=3.0 + bump 0.4 cruza el umbral estricto >3 (mismo cruce iOS).
        r = AndroidAnalysisResult(encrypted_apps=_apps(3), contacts_parsed=True,
                                  calls_parsed=True,
                                  findings=[_f_and("EMPTY_CONTACTS")],
                                  opsec_indicators=_ops(3))
        assert _z(r) == 3.4

    def test_b072_unparsed_zero_does_not_minimize(self):
        r = AndroidAnalysisResult(is_rooted=True, encrypted_apps=_apps(2),
                                  findings=[_f_and("DEVICE_ROOTED")])
        assert _z(r) == 2.8  # root+enc2, no root+enc2+dm=3.4

    def test_max_reachable_z_below_clip(self):
        r = AndroidAnalysisResult(is_rooted=True,
                                  findings=[_f_and("BROWSER_EXPLOIT_RESEARCH")],
                                  opsec_indicators=_ops(3))
        assert _z(r) == 4.2  # 3.8 + 0.4 — techo real, todavía < 5


# ── macOS: las 12 ramas (incluye la guarda anti-FP de B-074) ───────────────

MAC_LADDER = [
    ("exploit+af", dict(findings=[_f_mac("SAFARI_EXPLOIT_RESEARCH"),
                                  _f_mac("ANTIFORENSIC_SEARCH")]), 3.8),
    ("exploit+sip (af inclusivo)", dict(findings=[_f_mac("SAFARI_EXPLOIT_RESEARCH"),
                                                  _f_mac("SIP_DISABLED")]), 3.8),
    ("exploit", dict(findings=[_f_mac("SAFARI_EXPLOIT_RESEARCH")]), 3.5),
    ("triple B-074: af_real+enc2+sip", dict(encrypted_apps=_apps(2),
                                            findings=[_f_mac("ANTIFORENSIC_SEARCH"),
                                                      _f_mac("SIP_DISABLED")]), 3.4),
    ("enc3+search", dict(encrypted_apps=_apps(3),
                         findings=[_f_mac("SAFARI_SUSPICIOUS_SEARCH")]), 3.0),
    ("af_real+enc2", dict(encrypted_apps=_apps(2),
                          findings=[_f_mac("ANTIFORENSIC_SEARCH")]), 2.8),
    ("enc3", dict(encrypted_apps=_apps(3),
                  findings=[_f_mac("OPSEC_MULTI_ENCRYPTED_APPS")]), 2.4),
    ("sip_solo (doctrina B-074)", dict(findings=[_f_mac("SIP_DISABLED")]), 2.4),
    ("guarda anti-FP B-074: sip+enc2", dict(encrypted_apps=_apps(2),
                                            findings=[_f_mac("SIP_DISABLED")]), 2.4),
    ("enc2", dict(encrypted_apps=_apps(2),
                  findings=[_f_mac("OPSEC_MULTI_ENCRYPTED_APPS")]), 2.0),
    ("search+quarantine", dict(findings=[_f_mac("SAFARI_SUSPICIOUS_SEARCH"),
                                         _f_mac("QUARANTINE_SUSPICIOUS_SOURCE")]), 1.8),
    ("search", dict(findings=[_f_mac("SAFARI_SUSPICIOUS_SEARCH")]), 1.6),
    ("findings_solo", dict(findings=[_f_mac("TOR_BROWSER_DETECTED")]), 1.2),
    ("nada", dict(), 0.0),
]


class TestMacOSLadder:
    @pytest.mark.parametrize("branch,kwargs,expected",
                             MAC_LADDER, ids=[b[0] for b in MAC_LADDER])
    def test_branch(self, branch, kwargs, expected):
        assert _z(MacOSAnalysisResult(**kwargs)) == expected

    def test_opsec_bump_tiers(self):
        base = dict(findings=[_f_mac("TOR_BROWSER_DETECTED")])
        assert _z(MacOSAnalysisResult(**base, opsec_indicators=_ops(2))) == 1.4
        assert _z(MacOSAnalysisResult(**base, opsec_indicators=_ops(3))) == 1.6


# ── Cazador de ramas muertas (invariante S2) ───────────────────────────────

_MODULES = {
    "ios_forensics": REPO / "vigia/sift/ios_forensics.py",
    "android_forensics": REPO / "vigia/sift/android_forensics.py",
    "macos_forensics": REPO / "vigia/sift/macos_forensics.py",
}


def _to_signal_body(src: str) -> str:
    m = re.search(r"def to_signal\(self\).*?(?=\n    def |\nclass )", src, re.S)
    assert m, "to_signal no encontrado"
    return m.group(0)


@pytest.mark.parametrize("name", list(_MODULES))
def test_every_ladder_flag_has_an_emitter(name):
    """S2: un finding_type que la escalera LEE sin que ningún analyzer lo
    emita es una rama muerta (la clase de B-073/B-074). Hoy: 0. Este pin
    impide que una edición futura de la escalera reintroduzca la clase."""
    src = _MODULES[name].read_text(encoding="utf-8")
    body = _to_signal_body(src)
    rest = src.replace(body, "")
    read_types = set(re.findall(r'finding_type(?:\.startswith\()?\s*(?:==)?\s*[("]+([A-Z_]+)"', body))
    read_types |= set(re.findall(r'"([A-Z_]+)"\s*(?:,|\))', body)) & set(
        re.findall(r'"([A-Z_]{6,})"', body))
    read_types = {t for t in read_types if "_" in t}  # solo finding_types reales
    assert read_types, f"{name}: la escalera no lee ningún finding_type (regex rota?)"
    dead = {t for t in read_types if t not in rest}
    assert dead == set(), (
        f"{name}: la escalera lee finding_types SIN emisor (ramas muertas): {dead}"
    )
