"""
B7 (Grupo B / B-061) — clamp de confidence unificado en ambas rutas.

Firstness (AUDITORIA_INVARIANTES_ASIMETRIAS §B-061): el mismo input
confidence=2.0 CRASHEABA en un despliegue con pydantic (Field le=1.0 →
ValidationError) y se corregía EN SILENCIO en otro sin pydantic (dataclass
clampea) — determinismo cross-deployment comprometido para inputs inválidos.

Resolución (la recomendada por el audit): CLAMP en ambas rutas — coherente
con z_score, que las dos rutas clampean sin rechazar. La frontera fail-closed
de B-083/B-083b NO cambia: no-finito (NaN/±inf) sigue rechazando con error en
las cuatro implementaciones; el clamp aplica solo a finitos fuera de [0,1].

Tests escritos ROJOS contra las variantes Pydantic previas.
"""

import pytest

from vigia.core.ebs_v1 import SignalOutput as EbsSignal
from vigia.tools.signal_contract import SignalOutput as ContractSignal


def _ebs(confidence):
    return EbsSignal(tool_name="T", value=0.5, z_score=1.0, confidence=confidence)


def _contract(confidence):
    return ContractSignal(tool_name="T", signal_id="x", value=0.5, z_score=1.0,
                          confidence=confidence)


class TestFiniteOutOfRangeClamps:
    """B-061: mismo input → mismo resultado, con o sin pydantic."""

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    def test_above_one_clamps_to_one(self, make):
        assert make(1.7).confidence == 1.0

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    def test_two_point_zero_clamps(self, make):
        # El valor exacto del audit: confidence=2.0 crasheaba bajo pydantic.
        assert make(2.0).confidence == 1.0

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    def test_below_zero_clamps_to_zero(self, make):
        assert make(-0.3).confidence == 0.0

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    def test_in_range_passthrough(self, make):
        assert make(0.9).confidence == 0.9
        assert make(0.0).confidence == 0.0
        assert make(1.0).confidence == 1.0


class TestNonFiniteStillRejected:
    """La frontera B-083/B-083b no se relaja al quitar los bounds de Field."""

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_confidence_rejected(self, make, bad):
        with pytest.raises(Exception):
            make(bad)

    @pytest.mark.parametrize("make", [_ebs, _contract], ids=["ebs_v1", "signal_contract"])
    def test_non_finite_z_score_rejected(self, make):
        with pytest.raises(Exception):
            _ebs(0.9) if False else None
            make.__wrapped__ if hasattr(make, "__wrapped__") else None
            # construir con z_score no-finito
            if make is _ebs:
                EbsSignal(tool_name="T", value=0.5, z_score=float("nan"), confidence=0.9)
            else:
                ContractSignal(tool_name="T", signal_id="x", value=0.5,
                               z_score=float("nan"), confidence=0.9)


class TestFallbackVariantsAgree:
    """Las dataclass fallback ya clampeaban — pin de que siguen igual y que
    ahora las CUATRO implementaciones coinciden para 1.7/-0.3/2.0."""

    @pytest.fixture(scope="class")
    def fallbacks(self):
        import importlib.util
        import sys

        def load(path, name):
            saved = sys.modules.get("pydantic", "__absent__")
            sys.modules["pydantic"] = None
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[name] = mod
                try:
                    spec.loader.exec_module(mod)
                finally:
                    sys.modules.pop(name, None)
            finally:
                if saved == "__absent__":
                    sys.modules.pop("pydantic", None)
                else:
                    sys.modules["pydantic"] = saved
            return mod

        return (load("vigia/core/ebs_v1.py", "_ebs_nopyd_b7"),
                load("vigia/tools/signal_contract.py", "_sc_nopyd_b7"))

    def test_all_four_agree(self, fallbacks):
        ebs_fb, sc_fb = fallbacks
        for conf, expected in [(1.7, 1.0), (2.0, 1.0), (-0.3, 0.0), (0.9, 0.9)]:
            got = [
                _ebs(conf).confidence,
                _contract(conf).confidence,
                ebs_fb.SignalOutput(tool_name="T", value=0.5, z_score=1.0,
                                    confidence=conf).confidence,
                sc_fb.SignalOutput(tool_name="T", signal_id="x", value=0.5,
                                   z_score=1.0, confidence=conf).confidence,
            ]
            assert got == [expected] * 4, f"confidence={conf}: {got}"
