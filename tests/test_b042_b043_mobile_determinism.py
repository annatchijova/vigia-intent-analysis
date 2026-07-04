"""
B-042 / B-043 — ¿el borde float de to_signal() rompe el determinismo del
decision path? (test ESCRITO ANTES de tocar código, para zanjar la severidad).

Reclamo B-042/043: to_signal() usa float() para z_score/confidence; cuando el
módulo alimenta el pipeline determinista, floats entran al path Fraction —
posible violación P0 de L-021.

Cómo se decide (ENGINEERING_DISCIPLINE §5.2 "provalo"):
- El decision path del veredicto mobile es el z_score. sift_orchestrator.
  _mobile_hypothesis lo reconstruye con Fraction(str(z_score)) y compara con
  umbrales estrictos (>3, >2). La pregunta P0 es: ¿float(z) -> str -> Fraction
  recupera EXACTAMENTE la z interna (múltiplo de 1/10), o pierde precisión?
- Si el round-trip es exacto y determinista -> el borde es COSMÉTICO (el float
  es solo el contrato de transporte de SignalOutput; el decisor re-parsea a
  Fraction sin pérdida). Si NO -> es P0 (un veredicto puede divergir).

Si estos tests PASAN, B-042/043 es borde cosmético. Si FALLAN, es P0.
"""

import subprocess
import sys
from fractions import Fraction

import pytest

from vigia.sift.ios_forensics import iOSAnalysisResult, iOSFinding
from vigia.sift.android_forensics import AndroidAnalysisResult, AndroidFinding
from vigia.sift.macos_forensics import MacOSAnalysisResult, MacOSFinding


def _mk(cls, ft="X", cg="g"):
    return cls(finding_type=ft, severity=Fraction(1, 2), description="d",
               evidence="e", mitre_technique="T1", rule_ref="r", corr_group=cg)


def _ios_states():
    """Estados que recorren varias ramas de la escalera iOS."""
    out = []
    # sin findings -> z=0
    out.append(iOSAnalysisResult())
    # findings genéricos -> z=1.2
    r = iOSAnalysisResult()
    r.findings = [_mk(iOSFinding)]
    out.append(r)
    # encrypted apps + data minimization (contacts/calls 0) -> ramas altas
    for n_enc in (1, 2, 3):
        r = iOSAnalysisResult()
        r.encrypted_apps = [{"app": f"a{i}"} for i in range(n_enc)]
        r.total_contacts = 0
        r.total_calls = 0
        r.findings = [_mk(iOSFinding)]
        # opsec indicators para disparar el bump (0/2/3)
        r.opsec_indicators = [{"t": f"o{i}"} for i in range(n_enc)]
        r.composite_score = Fraction(n_enc, 10)
        out.append(r)
    return out


def _android_states():
    out = [AndroidAnalysisResult()]
    for n_enc in (1, 2, 3):
        r = AndroidAnalysisResult()
        r.encrypted_apps = [{"app": f"a{i}"} for i in range(n_enc)]
        r.total_contacts = 0
        r.total_calls = 0
        r.is_rooted = bool(n_enc % 2)
        r.findings = [_mk(AndroidFinding)]
        r.opsec_indicators = [{"t": f"o{i}"} for i in range(n_enc)]
        r.composite_score = Fraction(n_enc, 10)
        out.append(r)
    return out


def _macos_states():
    out = [MacOSAnalysisResult()]
    for n_enc in (1, 2, 3):
        r = MacOSAnalysisResult()
        r.encrypted_apps = [{"app": f"a{i}"} for i in range(n_enc)]
        r.findings = [_mk(MacOSFinding)]
        r.opsec_indicators = [{"t": f"o{i}"} for i in range(n_enc)]
        r.composite_score = Fraction(n_enc, 10)
        out.append(r)
    return out


ALL_STATES = [
    ("ios", _ios_states),
    ("android", _android_states),
    ("macos", _macos_states),
]


class TestDecisionValueRoundTrip:
    """La z_score (decision value) debe reconstruirse EXACTA vía Fraction(str(z))
    — que es lo que hace _mobile_hypothesis. Múltiplo de 1/10 => denominador
    divide 10 => decimal limpio => round-trip lossless."""

    @pytest.mark.parametrize("mod,factory", ALL_STATES)
    def test_zscore_reconstructs_exactly_as_fraction(self, mod, factory):
        for r in factory():
            sig = r.to_signal()
            z_float = sig.z_score
            # lo que hace el decisor:
            z_frac = Fraction(str(z_float))
            # invariante: el round-trip float->str->Fraction es identidad exacta
            assert float(z_frac) == z_float, f"{mod}: z_score {z_float} no round-trip exacto"
            # y la z es un múltiplo de 1/10 (la escalera + bump son *_/10)
            assert 10 % z_frac.denominator == 0, (
                f"{mod}: z_score {z_float} -> {z_frac} no es múltiplo de 1/10 "
                f"(denominador {z_frac.denominator}) — el float metió precisión sucia"
            )

    @pytest.mark.parametrize("mod,factory", ALL_STATES)
    def test_value_field_is_clean_fraction(self, mod, factory):
        """value = float(z/5) — múltiplo de 1/50 — también debe round-trip."""
        for r in factory():
            sig = r.to_signal()
            v_frac = Fraction(str(sig.value))
            assert float(v_frac) == sig.value
            assert 50 % v_frac.denominator == 0, f"{mod}: value {sig.value} no es múltiplo de 1/50"


class TestToSignalDeterminism:
    """Mismo input -> bytes idénticos, dos veces en el mismo proceso."""

    @pytest.mark.parametrize("mod,factory", ALL_STATES)
    def test_two_calls_identical(self, mod, factory):
        for r in factory():
            s1 = r.to_signal()
            s2 = r.to_signal()
            assert repr(s1.z_score) == repr(s2.z_score)
            assert repr(s1.value) == repr(s2.value)
            assert repr(s1.confidence) == repr(s2.confidence)


def test_fresh_process_determinism():
    """§5.2: reproducir en un PROCESO FRESCO (PYTHONHASHSEED distinto) y comparar.
    Un leak de orden de set/dict o de hash se manifiesta acá."""
    code = (
        "from fractions import Fraction;"
        "from vigia.sift.ios_forensics import iOSAnalysisResult, iOSFinding;"
        "r=iOSAnalysisResult();"
        "r.encrypted_apps=[{'app':'a'},{'app':'b'},{'app':'c'}];"
        "r.total_contacts=0; r.total_calls=0;"
        "r.opsec_indicators=[{'t':'o1'},{'t':'o2'},{'t':'o3'}];"
        "r.findings=[iOSFinding(finding_type='X',severity=Fraction(1,2),description='d',evidence='e',mitre_technique='T1',rule_ref='r',corr_group='g')];"
        "r.composite_score=Fraction(3,10);"
        "s=r.to_signal();"
        "print(repr(s.z_score), repr(s.value))"
    )
    outs = set()
    for seed in ("0", "1", "42"):
        import os
        env = dict(os.environ, PYTHONHASHSEED=seed)
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
        assert p.returncode == 0, p.stderr
        outs.add(p.stdout.strip())
    assert len(outs) == 1, f"z_score/value divergen entre procesos con PYTHONHASHSEED distinto: {outs}"
