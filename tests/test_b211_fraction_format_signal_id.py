"""B-211 — signal_id material must format Fraction scores on Python < 3.12.

`f"{Fraction:.8f}"` requires Python >= 3.12 (Fraction.__format__ with float
presentation types). On the CI-pinned 3.11 every artifact conversion in
CaseAdapter.artifact_to_signal() raised TypeError, was swallowed by the
generic except, and to_signals() ended in CaseSchemaError — the whole
integration bridge was inoperative. `_decimal_8f` replicates the 3.12+
formatting (half-even rounding at 8 decimals) in exact Fraction arithmetic.
"""
from __future__ import annotations

import sys
from fractions import Fraction

from vigia.pipeline.vigia_integration_bridge import CaseAdapter, _decimal_8f


class TestDecimal8f:
    def test_exact_values(self) -> None:
        assert _decimal_8f(Fraction(1, 2)) == "0.50000000"
        assert _decimal_8f(Fraction(0)) == "0.00000000"
        assert _decimal_8f(Fraction(1, 3)) == "0.33333333"
        assert _decimal_8f(Fraction(2, 3)) == "0.66666667"
        assert _decimal_8f(Fraction(-10)) == "-10.00000000"

    def test_half_even_ties(self) -> None:
        # 0.000000005 → tie → half-even → 0
        assert _decimal_8f(Fraction(1, 200_000_000)) == "0.00000000"
        # 0.000000015 → tie → half-even → 2e-8
        assert _decimal_8f(Fraction(3, 200_000_000)) == "0.00000002"

    def test_float_passthrough_keeps_historic_behavior(self) -> None:
        assert _decimal_8f(0.5) == f"{0.5:.8f}"
        assert _decimal_8f(-1.25) == f"{-1.25:.8f}"

    def test_parity_with_native_fraction_format_on_312_plus(self) -> None:
        if sys.version_info < (3, 12):
            return  # native format spec unsupported — that is the bug itself
        samples = [
            Fraction(0), Fraction(1, 2), Fraction(1, 3), Fraction(-7, 9),
            Fraction(1, 200_000_000), Fraction(3, 200_000_000),
            Fraction(123456789, 10_000_000), Fraction(-5, 8),
        ]
        for value in samples:
            assert _decimal_8f(value) == format(value, ".8f"), value


class TestAdapterConvertsFractionScores:
    def test_artifact_with_fraction_scores_translates(self) -> None:
        adapter = CaseAdapter()
        sig = adapter.artifact_to_signal(
            {
                "artifact_id": "synthetic-artifact",
                "evidence_type": "log_entry",
                "raw_score": 0.5,
                "source_tool": "synthetic",
            },
            case_id="b206",
        )
        assert sig is not None
        assert sig.signal_id

    def test_signal_id_is_deterministic(self) -> None:
        adapter = CaseAdapter()
        art = {
            "artifact_id": "synthetic-artifact",
            "evidence_type": "log_entry",
            "raw_score": 0.5,
            "source_tool": "synthetic",
        }
        first = adapter.artifact_to_signal(dict(art), case_id="b206")
        second = adapter.artifact_to_signal(dict(art), case_id="b206")
        assert first is not None and second is not None
        assert first.signal_id == second.signal_id
