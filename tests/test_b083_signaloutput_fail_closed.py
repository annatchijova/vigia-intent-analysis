"""
B-083 (observación menor del censo P0-001): el clip de ebs_v1.SignalOutput
convertía NaN → 5.0 en silencio (semántica de min() con NaN: min(5.0, nan)
retorna 5.0 porque nan < 5.0 es False). Un z_score corrupto entraba al
pipeline como señal CRÍTICA (z=5.0, el máximo) en vez de ser rechazado.

Contrato unificado al patrón fail-closed de vigia/tools/signal_contract.py:
z_score y value no-finitos (NaN, ±inf) → ValueError en construcción.
El clip a ±Z_CLIP_MAX y el clamp de confidence sobre valores FINITOS no cambian.

Tests escritos ROJOS contra el código previo al fix.
"""

import math

import pytest

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX


def _make(z=0.0, value=0.5, confidence=0.9):
    return SignalOutput(tool_name="T", value=value, z_score=z, confidence=confidence)


class TestNonFiniteRejected:
    """Fail-closed: no-finito → ValueError, nunca clip silencioso."""

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_z_score_non_finite_raises(self, bad):
        with pytest.raises(ValueError):
            _make(z=bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_value_non_finite_raises(self, bad):
        with pytest.raises(ValueError):
            _make(value=bad)

    def test_nan_never_becomes_max_critical(self):
        # El bug exacto: NaN entraba como z=5.0 (señal crítica máxima).
        try:
            s = _make(z=float("nan"))
        except ValueError:
            return  # fail-closed: correcto
        pytest.fail(f"NaN aceptado en silencio como z_score={s.z_score}")


class TestFiniteBehaviorUnchanged:
    """El contrato sobre valores finitos no cambia con el fix."""

    def test_clip_above(self):
        assert _make(z=7.3).z_score == Z_CLIP_MAX

    def test_clip_below(self):
        assert _make(z=-9.9).z_score == -Z_CLIP_MAX

    def test_in_range_passthrough(self):
        assert _make(z=2.8).z_score == 2.8
        assert _make(z=0.0).z_score == 0.0

    def test_confidence_never_leaves_range(self):
        # Variante Pydantic: Field(ge=0, le=1) rechaza fuera-de-rango ANTES
        # del clamp (comportamiento preexistente); variante dataclass: clampea.
        # Contrato común: confidence nunca sale de [0, 1] en silencio.
        for bad in (1.7, -0.3):
            try:
                s = _make(confidence=bad)
            except Exception:
                continue  # rechazo estricto: aceptable
            assert 0.0 <= s.confidence <= 1.0

    def test_confidence_in_range_passthrough(self):
        assert _make(confidence=0.9).confidence == 0.9

    def test_value_finite_passthrough(self):
        assert _make(value=0.56).value == 0.56

    def test_to_dict_roundtrip(self):
        d = _make(z=1.5).to_dict()
        assert d["z_score"] == 1.5 and math.isfinite(d["value"])


# ---------------------------------------------------------------------------
# B-083b — confidence NaN/±inf también fail-closed.
# En las variantes Pydantic, Field(ge/le) ya rechazaba NaN (comparación con
# NaN falla) — esos tests son pins. El gap real estaba en los fallbacks
# dataclass: max(0.0, min(1.0, nan)) → 1.0 (confianza MÁXIMA silenciosa) e
# inf/-inf clampeaban a 1.0/0.0. Tests del fallback escritos ROJOS.
# ---------------------------------------------------------------------------

try:
    from pydantic import ValidationError as _PydanticValidationError
    _REJECTED = (ValueError, _PydanticValidationError)
except ImportError:
    _REJECTED = (ValueError,)


class TestConfidenceNonFinitePydantic:
    """Pin: la variante Pydantic (activa en esta suite) rechaza no-finitos."""

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_confidence_non_finite_rejected(self, bad):
        with pytest.raises(_REJECTED):
            _make(confidence=bad)


def _load_no_pydantic_variant(module_path, name):
    """Carga un módulo con pydantic bloqueado → fuerza el fallback dataclass."""
    import importlib.util
    import sys
    saved = sys.modules.get("pydantic", "__absent__")
    sys.modules["pydantic"] = None  # ImportError en `from pydantic import ...`
    try:
        spec = importlib.util.spec_from_file_location(name, module_path)
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


@pytest.fixture(scope="module")
def ebs_v1_fallback():
    mod = _load_no_pydantic_variant("vigia/core/ebs_v1.py", "_ebs_v1_nopyd_b083b")
    assert not mod._USE_PYDANTIC
    return mod


@pytest.fixture(scope="module")
def signal_contract_fallback():
    mod = _load_no_pydantic_variant(
        "vigia/tools/signal_contract.py", "_signal_contract_nopyd_b083b"
    )
    assert not mod._PYDANTIC_AVAILABLE
    return mod


class TestConfidenceNonFiniteDataclassFallbacks:
    """El gap real: los fallbacks clampeaban NaN→1.0 (confianza máxima)."""

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_ebs_v1_fallback_rejects(self, ebs_v1_fallback, bad):
        with pytest.raises(ValueError):
            ebs_v1_fallback.SignalOutput(
                tool_name="T", value=0.5, z_score=1.0, confidence=bad
            )

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_signal_contract_fallback_rejects(self, signal_contract_fallback, bad):
        with pytest.raises(ValueError):
            signal_contract_fallback.SignalOutput(
                tool_name="T", signal_id="x", value=0.5, z_score=1.0, confidence=bad
            )

    def test_ebs_v1_fallback_finite_clamp_unchanged(self, ebs_v1_fallback):
        s = ebs_v1_fallback.SignalOutput(
            tool_name="T", value=0.5, z_score=1.0, confidence=1.7
        )
        assert s.confidence == 1.0

    def test_signal_contract_fallback_finite_clamp_unchanged(
        self, signal_contract_fallback
    ):
        s = signal_contract_fallback.SignalOutput(
            tool_name="T", signal_id="x", value=0.5, z_score=1.0, confidence=-0.3
        )
        assert s.confidence == 0.0
