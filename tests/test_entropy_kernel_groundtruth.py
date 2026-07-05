"""
tests/test_entropy_kernel_groundtruth.py
========================================
Ground-truth tests for vigia/tools/entropy_kernel.py (was 0% covered).

entropy_kernel is a determinism-critical module: its docstrings promise
bit-for-bit cross-architecture reproducibility (round(x, 6), float64) because
its output feeds the CAIE fracture scores that end up in a sealed bundle.
That makes it a high-value target for ground-truth testing — the entropy of a
known distribution has one correct value, so a numerical regression cannot
hide behind "looks plausible".

Most tests here pin the correct behavior. TestSignedZeroRegression guards
against BUG-ENTROPY-001, a real determinism defect found while writing these
tests (the entropy functions returned IEEE-754 -0.0 for zero-entropy inputs,
which canonicalizes differently from 0.0 and breaks seal reproducibility). It
is now fixed at the source (+0.0 at the rounded return sites); that class is
the regression guard. See its docstring for the full analysis.
"""
from __future__ import annotations

import math

import pytest

from vigia.tools import entropy_kernel as ek


# ---------------------------------------------------------------------------
# entropy_shannon — Shannon entropy (bits) over the value-frequency histogram
# ---------------------------------------------------------------------------

class TestEntropyShannonGroundTruth:
    def test_empty_is_zero(self):
        assert ek.entropy_shannon([]) == 0.0

    def test_single_value_is_zero(self):
        assert ek.entropy_shannon([5]) == 0.0

    def test_constant_sequence_is_zero(self):
        assert ek.entropy_shannon([5, 5, 5, 5]) == 0.0

    def test_two_equiprobable_values_is_one_bit(self):
        assert ek.entropy_shannon([1, 2]) == pytest.approx(1.0, abs=1e-6)

    def test_four_equiprobable_values_is_two_bits(self):
        assert ek.entropy_shannon([1, 2, 3, 4]) == pytest.approx(2.0, abs=1e-6)

    def test_eight_equiprobable_values_is_three_bits(self):
        assert ek.entropy_shannon([1, 2, 3, 4, 5, 6, 7, 8]) == pytest.approx(3.0, abs=1e-6)

    def test_skewed_distribution_matches_closed_form(self):
        # [1,1,1,2] -> p={0.75, 0.25} -> H = 0.8112781...
        expected = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
        assert ek.entropy_shannon([1, 1, 1, 2]) == pytest.approx(expected, abs=1e-6)

    def test_is_deterministic(self):
        seq = [1, 1, 2, 3, 5, 8, 13]
        assert ek.entropy_shannon(seq) == ek.entropy_shannon(list(seq))


# ---------------------------------------------------------------------------
# entropy_normalized — Shannon entropy scaled to [0, 1]
# ---------------------------------------------------------------------------

class TestEntropyNormalized:
    def test_constant_is_zero(self):
        assert ek.entropy_normalized([5, 5, 5, 5]) == 0.0

    def test_uniform_distinct_is_one(self):
        assert ek.entropy_normalized([1, 2, 3, 4]) == pytest.approx(1.0, abs=1e-6)

    @pytest.mark.parametrize(
        "seq",
        [[1, 1, 1, 2, 3, 9, 4, 7], [1, 2, 2, 2], [10, 20, 30], [0, 0, 1]],
    )
    def test_always_within_unit_interval(self, seq):
        v = ek.entropy_normalized(seq)
        assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# entropy_rate — normalized entropy of the consecutive-pair token distribution
# ---------------------------------------------------------------------------

class TestEntropyRate:
    def test_too_short_is_zero(self):
        assert ek.entropy_rate([5]) == 0.0
        assert ek.entropy_rate([]) == 0.0

    def test_constant_series_is_zero(self):
        # All pairs are identical -> a single token -> zero entropy.
        assert ek.entropy_rate([5, 5, 5, 5, 5]) == 0.0

    def test_within_unit_interval(self):
        assert 0.0 <= ek.entropy_rate([1, 2, 1, 2, 1, 2]) <= 1.0

    def test_is_deterministic(self):
        seq = [3, 1, 4, 1, 5, 9, 2, 6]
        assert ek.entropy_rate(seq) == ek.entropy_rate(list(seq))


# ---------------------------------------------------------------------------
# GCI / integration-bridge drop-in patch helpers
# ---------------------------------------------------------------------------

class TestPatchHelpers:
    def test_log_n_is_log2(self):
        assert ek.patch_gci_log_n(8) == pytest.approx(3.0, abs=1e-6)
        assert ek.patch_gci_log_n(16) == pytest.approx(4.0, abs=1e-6)

    def test_log_n_clamps_below_two(self):
        # max(n, 2) -> log2(2) == 1.0 for n in {0, 1}
        assert ek.patch_gci_log_n(1) == pytest.approx(1.0, abs=1e-6)
        assert ek.patch_gci_log_n(0) == pytest.approx(1.0, abs=1e-6)

    def test_log_lr_natural_log(self):
        assert ek.patch_integration_bridge_log_lr(math.e) == pytest.approx(1.0, abs=1e-6)

    def test_log_lr_non_positive_is_zero(self):
        assert ek.patch_integration_bridge_log_lr(0.0) == 0.0
        assert ek.patch_integration_bridge_log_lr(-5.0) == 0.0


# ---------------------------------------------------------------------------
# Module self-diagnostics
# ---------------------------------------------------------------------------

class TestSelfDiagnostics:
    def test_self_test_passes(self):
        ok, msg = ek.self_test()
        assert ok, msg

    def test_backend_info_has_core_fields(self):
        info = ek.get_backend_info()
        for key in ("backend", "float_precision", "hash_round_decimals"):
            assert key in info

    def test_batch_matches_scalar(self):
        batch = [[1, 2, 3, 4], [5, 5, 5, 5], [1, 1, 2, 3]]
        got = ek.entropy_batch(batch, mode="shannon")
        assert got == [ek.entropy_shannon(s) for s in batch]


# ---------------------------------------------------------------------------
# REGRESSION GUARD — BUG-ENTROPY-001, now fixed at the source (see class docstring)
# ---------------------------------------------------------------------------

class TestSignedZeroRegression:
    """
    BUG-ENTROPY-001 (FIXED) — signed-zero leak broke seal canonicalization.
    This class is now the regression guard for the fix.

    Every zero-entropy input made entropy_shannon / entropy_normalized /
    entropy_rate return -0.0 (IEEE 754 negative zero) rather than 0.0. The two
    are equal under `==`, so it is invisible to normal comparisons, but the
    bundle canonicalizer (vigia/core/bundle_builder._canonicalize) formats
    floats with `f"{x:.8f}"`:

        _canonicalize(-0.0) -> "-0.00000000"
        _canonicalize( 0.0) -> "0.00000000"

    Those are distinct strings, so _sha256_dict({"e": -0.0}) differs from
    _sha256_dict({"e": 0.0}). Two mathematically identical zero-entropy
    results therefore seal to different bundle hashes — a violation of EBS
    invariant I2 in a module whose docstring explicitly promises cross-arch
    bit-for-bit determinism.

    Scope of confirmation: CONFIRMED at the kernel + canonicalizer boundary
    (proven above). Whether a raw entropy float reaches a sealed bundle field
    unrounded end-to-end is PLAUSIBLE but not yet traced through eml_gci/CAIE.

    Fix applied: signed zero is normalized at the rounded return sites in
    entropy_kernel (`round(value, _HASH_PRECISION) + 0.0`, which maps
    -0.0 -> 0.0). These tests assert every zero-entropy result is +0.0.
    """

    @pytest.mark.parametrize(
        "fn, args",
        [
            (ek.entropy_shannon, ([5, 5, 5, 5],)),
            (ek.entropy_normalized, ([5, 5, 5, 5],)),
            (ek.entropy_rate, ([5, 5, 5, 5, 5],)),
        ],
    )
    def test_zero_entropy_is_positive_zero(self, fn, args):
        v = fn(*args)
        assert math.copysign(1.0, v) > 0.0, (
            f"{fn.__name__} returned signed-zero {v!r}; canonicalizes to "
            f'"-0.00000000" != "0.00000000", so identical zero-entropy results '
            f"seal to different hashes (BUG-ENTROPY-001, EBS I2)."
        )
