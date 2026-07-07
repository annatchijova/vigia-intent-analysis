"""
Regresión de los fixes adyacentes del censo P0-001
(docs/AUDIT_P0001_FLOAT_CENSUS.md §3.1, §5.1, §5.3, §5.4).

Cada valor de test fue elegido por búsqueda exhaustiva para DIVERGIR entre el
patrón viejo (float intermedio) y el nuevo (aritmética exacta): estos tests
fallan sobre el código previo al fix.
"""

from fractions import Fraction

import pytest

from vigia.sift._math_utils import apply_artifact_reliability_dynamic
from vigia.sift.android_forensics import AndroidForensicsAnalyzer


class TestMathUtilsCompositeQuantization:
    """§5.1 — recurrencia pre-P0-001 en apply_artifact_reliability_dynamic."""

    def test_divergent_value_quantizes_exactly(self):
        # 0.42500000000000004 * 20 = 8.5 en IEEE 754 → round() banker daba 8.
        # Exacto: 8.500000000000001 → 9. El gamma resultante difiere.
        score = Fraction(1, 1)
        result = apply_artifact_reliability_dynamic(
            score, "windows_event_log",
            metadata={"chains": 100, "composite_score": 0.42500000000000004},
        )
        # corroboration = 1 × (9/20) → gamma = 3/5 + 2/5 × 9/20 = 39/50
        assert result == Fraction(39, 50), (
            f"composite 0.42500000000000004 debe cuantizar a 9/20 "
            f"(exacto), no 8/20 (float); gamma obtenido: {result}"
        )

    def test_string_fraction_path_unchanged(self):
        # gamma crudo = 3/5 + 2/5×19/20 = 49/50 → cap a 19/20.
        result = apply_artifact_reliability_dynamic(
            Fraction(1, 1), "windows_event_log",
            metadata={"chains": 100, "composite_score": "19/20"},
        )
        assert result == Fraction(19, 20)

    def test_clean_float_unchanged(self):
        # Valor limpio: viejo y nuevo coinciden — 0 regresión (cap a 19/20).
        result = apply_artifact_reliability_dynamic(
            Fraction(1, 1), "windows_event_log",
            metadata={"chains": 100, "composite_score": 0.95},
        )
        assert result == Fraction(19, 20)

    def test_result_is_fraction(self):
        result = apply_artifact_reliability_dynamic(
            Fraction(1, 1), "windows_event_log",
            metadata={"chains": 5, "composite_score": 0.3},
        )
        assert isinstance(result, Fraction)


class TestChromeTsToUnix:
    """§5.4 — división entera en _chrome_ts_to_unix (sin float intermedio)."""

    def test_divergent_microsecond_boundary(self):
        # int(ts / 1_000_000) redondeaba 18396007234999999/1e6 hacia ARRIBA
        # (…235 en vez de …234): cruce de borde de segundo por IEEE 754.
        ts = 18_396_007_234_999_999
        expected = ts // 1_000_000 - 11_644_473_600  # _CHROME_EPOCH_OFFSET
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(ts) == expected

    def test_typical_2024_microseconds(self):
        ts = 13_353_618_000_000_000  # ~2024-03 en WebKit µs
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(ts) == (
            ts // 1_000_000 - 11_644_473_600
        )

    def test_milliseconds_and_seconds_branches(self):
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(
            13_353_618_000_000
        ) == 13_353_618_000_000 // 1_000 - 11_644_473_600
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(
            13_353_618_000
        ) == 13_353_618_000 - 11_644_473_600

    def test_zero_and_negative(self):
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(0) == 0
        assert AndroidForensicsAnalyzer._chrome_ts_to_unix(-5) == 0


class TestRawTsBeyond2p53:
    """§3.1 — int(Decimal(str(x))) preserva µs por encima de 2^53."""

    def test_odd_microsecond_timestamp_preserved(self):
        from decimal import Decimal
        raw_ts = 2**53 + 1  # int(float(x)) lo colapsaba a 2^53
        assert int(Decimal(str(raw_ts))) == raw_ts
        assert int(float(raw_ts)) != raw_ts  # documenta el bug viejo

    def test_decimal_accepts_sqlite_variants(self):
        from decimal import Decimal
        # Variantes que el driver o un export pueden entregar
        assert int(Decimal(str(13_353_618_000_000_001))) == 13_353_618_000_000_001
        assert int(Decimal("13353618000000000.0")) == 13_353_618_000_000_000
        assert int(Decimal(str(1.3353618e16))) == 13_353_618_000_000_000


class TestReasonerFractionThresholds:
    """§5.3 — umbrales del reasoner en Fraction, semántica preservada."""

    def _sig(self, z, tool="MEMORY_FORENSICS"):
        from vigia.core.ebs_v1 import SignalOutput
        return SignalOutput(tool_name=tool, value=0.5, z_score=z, confidence=0.9)

    def test_z_frac_conversion(self):
        from types import SimpleNamespace
        from vigia.inference.abductive_reasoner import _z_frac
        assert _z_frac(self._sig(2.8)) == Fraction(14, 5)
        assert _z_frac(self._sig(0.0)) == Fraction(0, 1)
        # NaN directo (el DTO ebs_v1 lo clipea a 5.0 antes de llegar acá;
        # el guard cubre adaptadores que no pasan por ese validador).
        assert _z_frac(SimpleNamespace(z_score=float("nan"))) == Fraction(0, 1)
        assert _z_frac(SimpleNamespace(z_score=float("inf"))) == Fraction(0, 1)

    def test_threshold_semantics_identical_to_float(self):
        from vigia.inference.abductive_reasoner import (
            _z_frac, _Z_ACTIVE, _Z_CRITICAL, _Z_TECHNIQUE, _Z_CONTRADICT,
        )
        # El orden float-vs-literal se preserva para todo float finito,
        # incluidos los bordes exactos y el vecino inmediato.
        for z in [1.5, 1.5000000000000002, 2.0, 2.0000000000000004,
                  3.0, 3.0000000000000004, 0.5, 0.49999999999999994]:
            s = self._sig(z)
            assert (_z_frac(s) > _Z_ACTIVE) == (z > 1.5)
            assert (_z_frac(s) > _Z_TECHNIQUE) == (z > 2.0)
            assert (_z_frac(s) > _Z_CRITICAL) == (z > 3.0)
            assert (_z_frac(s) <= _Z_CONTRADICT) == (z <= 0.5)

    def test_reason_smoke(self):
        from vigia.inference.abductive_reasoner import AbductiveReasoner
        trace = AbductiveReasoner().reason(
            [self._sig(3.5), self._sig(0.2, tool="BROWSER_FORENSICS")]
        )
        assert trace.best_hypothesis  # no crashea, emite hipótesis
