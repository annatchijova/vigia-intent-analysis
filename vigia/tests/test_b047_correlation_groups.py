"""
vigia/tests/test_b047_correlation_groups.py

Regresión B-047 — _build_correlation_groups() formato List[List[int]] vs
Dict[int, Set[int]].

Cubre:
  1. Semántica del helper canónico build_correlation_groups().
  2. Equivalencia exacta contra la implementación de referencia
     (google_takeout_forensics pre-B-047, congelada acá como oráculo).
  3. Delegación de los cuatro módulos + paso completo por noisy_or_correlated.
     android va vía duck typing (SimpleNamespace): el analyzer está confirmado
     (AndroidForensicsAnalyzer, B-045) pero el nombre de su dataclass de
     finding no fue verificado, y _build_correlation_groups solo lee
     f.corr_group — no hace falta inventar nombres.
  4. Monotonía: score correlacionado <= score independiente.
  5. Guard fail-loud: lista rechazada con TypeError (requiere
     apply_b047_mathutils.py aplicado — si se posterga el guard, marcar ese
     test xfail, no borrarlo).
"""

from fractions import Fraction

import pytest

from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated

RHO = Fraction(15, 100)  # mismo rho que usan los call sites reales


# ──────────────────────────────────────────────────────────────────────────
# 1. Semántica del helper
# ──────────────────────────────────────────────────────────────────────────

def test_helper_basic_semantics():
    tags = ["a", "b", "a", "", "b", "c"]
    result = build_correlation_groups(tags)
    assert result == {0: {2}, 2: {0}, 1: {4}, 4: {1}}
    # singleton ("c") y tag vacío no aparecen
    assert 3 not in result and 5 not in result


def test_helper_empty_and_all_independent():
    assert build_correlation_groups([]) == {}
    assert build_correlation_groups(["x", "y", "z"]) == {}
    assert build_correlation_groups(["", "", ""]) == {}


def test_helper_triple_group_full_peers():
    result = build_correlation_groups(["g", "g", "g"])
    assert result == {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}


def test_helper_never_includes_self():
    result = build_correlation_groups(["g"] * 5)
    for idx, peers in result.items():
        assert idx not in peers


# ──────────────────────────────────────────────────────────────────────────
# 2. Equivalencia contra la implementación de referencia (takeout pre-B-047)
# ──────────────────────────────────────────────────────────────────────────

def _takeout_reference(corr_tags):
    """Copia congelada de google_takeout_forensics._build_correlation_groups
    tal como estaba antes de B-047 — la implementación correcta original.
    Es el oráculo: el helper debe producir exactamente lo mismo."""
    tag_groups = {}
    for i, tag in enumerate(corr_tags):
        if tag:
            tag_groups.setdefault(tag, []).append(i)
    result = {}
    for indices in tag_groups.values():
        if len(indices) < 2:
            continue
        for idx in indices:
            peers = {j for j in indices if j != idx}
            if idx in result:
                result[idx] |= peers
            else:
                result[idx] = peers
    return result


@pytest.mark.parametrize("tags", [
    [],
    ["a"],
    ["a", "a"],
    ["a", "b", "a", "b", ""],
    ["x"] * 7,
    ["", "", "g", "g", "h", "g", "h"],
    ["browser_suspicious", "antiforensic", "browser_suspicious",
     "encrypted_apps", "antiforensic", "persistence"],
])
def test_helper_matches_takeout_reference(tags):
    assert build_correlation_groups(tags) == _takeout_reference(tags)


# ──────────────────────────────────────────────────────────────────────────
# 3. Delegación de módulos + paso por noisy_or_correlated
# ──────────────────────────────────────────────────────────────────────────

def _two_correlated_macos_findings():
    from vigia.sift.macos_forensics import MacOSFinding
    return [
        MacOSFinding(
            finding_type="SAFARI_SUSPICIOUS", severity=Fraction(60, 100),
            description="t", evidence="e", mitre_technique="T1595",
            rule_ref="R", corr_group="browser_suspicious",
        ),
        MacOSFinding(
            finding_type="SAFARI_SUSPICIOUS", severity=Fraction(50, 100),
            description="t", evidence="e", mitre_technique="T1595",
            rule_ref="R", corr_group="browser_suspicious",
        ),
    ]


def test_macos_delegates_and_survives_noisy_or():
    """Pre-B-047 este escenario (>=2 findings, mismo corr_group) era
    exactamente el que explotaba o inflaba en silencio."""
    from vigia.sift.macos_forensics import MacOSForensicsAnalyzer
    a = MacOSForensicsAnalyzer()
    a._findings = _two_correlated_macos_findings()
    groups = a._build_correlation_groups()
    assert isinstance(groups, dict)
    assert groups == {0: {1}, 1: {0}}
    score = noisy_or_correlated(
        [f.severity for f in a._findings], groups, RHO
    )
    assert isinstance(score, Fraction)
    assert Fraction(0) <= score <= Fraction(1)


def test_ios_delegates_and_survives_noisy_or():
    from vigia.sift.ios_forensics import iOSForensicsAnalyzer, iOSFinding
    a = iOSForensicsAnalyzer()
    a._findings = [
        iOSFinding(
            finding_type="EMPTY_CONTACTS", severity=Fraction(45, 100),
            description="t", evidence="e", mitre_technique="T1070",
            rule_ref="R", corr_group="data_minimization",
        ),
        iOSFinding(
            finding_type="EMPTY_CALL_HISTORY", severity=Fraction(40, 100),
            description="t", evidence="e", mitre_technique="T1070",
            rule_ref="R", corr_group="data_minimization",
        ),
    ]
    groups = a._build_correlation_groups()
    assert isinstance(groups, dict)
    assert groups == {0: {1}, 1: {0}}
    score = noisy_or_correlated(
        [f.severity for f in a._findings], groups, RHO
    )
    assert isinstance(score, Fraction)


def test_android_delegates_via_duck_typing():
    """android_forensics verificado por grep en repo vivo (2026-07-01,
    líneas 320-326): método idéntico al patrón de ios/macos. Este test usa
    SimpleNamespace porque el nombre del dataclass de finding de android no
    fue confirmado y el método bajo test solo lee f.corr_group."""
    from types import SimpleNamespace
    from vigia.sift.android_forensics import AndroidForensicsAnalyzer
    a = AndroidForensicsAnalyzer()
    a._findings = [
        SimpleNamespace(corr_group="g"),
        SimpleNamespace(corr_group="g"),
        SimpleNamespace(corr_group=""),
    ]
    groups = a._build_correlation_groups()
    assert isinstance(groups, dict)
    assert groups == {0: {1}, 1: {0}}


def test_takeout_still_delegates_identically():
    """Takeout ya era correcto; el fix no debe cambiar su output."""
    from vigia.sift.google_takeout_forensics import (
        GoogleTakeoutForensicsAnalyzer, TakeoutFinding,
    )
    a = GoogleTakeoutForensicsAnalyzer()
    a._findings = [
        TakeoutFinding(
            finding_type="ROOT_TOOL_INSTALLED", severity=Fraction(60, 100),
            description="t", evidence="e", mitre_technique="T1398",
            rule_ref="R", corr_group="suspicious_apps",
        ),
        TakeoutFinding(
            finding_type="SUSPICIOUS_INSTALLED_APP", severity=Fraction(55, 100),
            description="t", evidence="e", mitre_technique="T1059",
            rule_ref="R", corr_group="suspicious_apps",
        ),
        TakeoutFinding(
            finding_type="LOCATION_HISTORY_GAP", severity=Fraction(35, 100),
            description="t", evidence="e", mitre_technique="T1070",
            rule_ref="R", corr_group="location_gaps",
        ),
    ]
    groups = a._build_correlation_groups()
    tags = [f.corr_group for f in a._findings]
    assert groups == _takeout_reference(tags)


# ──────────────────────────────────────────────────────────────────────────
# 4. Monotonía — la correlación descuenta, nunca suma
# ──────────────────────────────────────────────────────────────────────────

def test_correlated_score_not_above_independent():
    """Confirmado contra el código real (grep 2026-07-01): con mapa vacío o
    None, noisy_or_correlated salta el bloque de penalización y computa el
    Noisy-OR independiente puro; con correlación, multiplica al miembro de
    menor severidad de cada par por (1 - penalty). Correlacionado <= independiente
    por construcción."""
    sevs = [Fraction(60, 100), Fraction(50, 100)]
    corr = build_correlation_groups(["g", "g"])
    s_corr = noisy_or_correlated(sevs, corr, RHO)
    s_indep = noisy_or_correlated(sevs, {}, RHO)
    assert s_corr <= s_indep


# ──────────────────────────────────────────────────────────────────────────
# 5. Guard fail-loud (requiere Paso 2 del patchset)
# ──────────────────────────────────────────────────────────────────────────

def test_noisy_or_correlated_rejects_list_format():
    """El formato viejo debe morir con TypeError explícito. Pre-fix
    confirmado (grep 2026-07-01): con lista no vacía, la línea
    sorted(correlation_groups.items()) revienta con AttributeError
    'list' object has no attribute 'items' — fail-loud accidental, sin
    mensaje útil. Requiere el guard aplicado (apply_b047_mathutils.py);
    si se posterga, marcar xfail."""
    with pytest.raises(TypeError):
        noisy_or_correlated(
            [Fraction(1, 2), Fraction(1, 2)], [[0, 1]], RHO
        )
