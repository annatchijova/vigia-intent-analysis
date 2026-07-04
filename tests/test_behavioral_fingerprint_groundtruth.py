"""
tests/test_behavioral_fingerprint_groundtruth.py
================================================
Ground-truth tests for vigia/inference/behavioral_fingerprint.py (was ~31%
covered).

CANONICAL MODULE SELECTION
--------------------------
Two modules share the name ``behavioral_fingerprint``:

  * ``vigia/inference/behavioral_fingerprint.py`` -- class ``BehavioralFingerprint``.
    Imported by ``vigia/sift/sift_orchestrator.py`` (the live pipeline). This is
    the CANONICAL module and the one exercised here.
  * ``vigia/tools/behavioral_fingerprint.py`` -- class
    ``BehavioralFingerprintAnalyzer``. A divergent duplicate with a completely
    different API (``learn_profile`` / ``analyze_deviation``, naming/timing/
    software/vocabulary heuristics). It is imported nowhere in the package
    (0% covered, flagged as a dead engine in KNOWN_LIMITATIONS L-044) and is
    NOT tested here. Its existence is recorded as a structural finding
    (FINDING-FP-DUP below).

WHAT THIS MODULE DOES
---------------------
``BehavioralFingerprint`` builds a distribution fingerprint of system events by
computing Shannon entropy (in bits) over three token streams -- process names,
network targets (dst_ip and dst_port pooled), and timestamps -- then compares a
"current" profile against a trained baseline. Entropy has one correct value for
a known distribution, which makes it a good ground-truth target: a regression
cannot hide behind "looks plausible". The scoring formulas
(deviation weights 0.5/0.3/0.2, severity = min(2*dev, 0.95), composite cap 0.95,
confidence = composite * 1.1 * 0.70) are closed-form and pinned exactly here.

OUTCOME
-------
All tests PASS. Probing did not surface a defect that violates a documented
contract in the canonical module: entropy matches the closed form to ~1e-14,
the pipeline is deterministic, and the scoring arithmetic is exact.

One test class (TestDistributionBlindSpotCharacterization) documents an
INHERENT limitation rather than a code bug: because the fingerprint measures
distribution shape and never token identity, a total content swap that
preserves the shape yields zero deviation and evades detection. That is a real
false-negative weakness (scope: PLAUSIBLE, see the class docstring) but it is
by-design for an entropy detector and violates no stated contract, so it is
pinned as observed behavior, NOT left failing.
"""
from __future__ import annotations

import math
from fractions import Fraction

import pytest

from vigia.inference.behavioral_fingerprint import (
    BehavioralFingerprint,
    BehavioralProfile,
    BehavioralFingerprintResult,
)
from vigia.sift._math_utils import _entropy_shannon


def _ev(process=None, dst_ip=None, dst_port=None, timestamp=None):
    """Build an event dict including only the keys explicitly provided."""
    e = {}
    if process is not None:
        e["process_name"] = process
    if dst_ip is not None:
        e["dst_ip"] = dst_ip
    if dst_port is not None:
        e["dst_port"] = dst_port
    if timestamp is not None:
        e["timestamp"] = timestamp
    return e


# ---------------------------------------------------------------------------
# _compute_profile -- entropy math over the three token streams
# ---------------------------------------------------------------------------

class TestComputeProfileEntropy:
    def test_constant_behavior_is_zero_entropy(self):
        # One repeated process/ip/port/timestamp -> no variety -> H = 0 on all axes.
        events = [_ev("chrome", "1.1.1.1", 443, 5)] * 4
        p = BehavioralFingerprint()._compute_profile(events)
        assert p.process_entropy == Fraction(0)
        assert p.temporal_entropy == Fraction(0)
        # network stream is [1.1.1.1, 443, 1.1.1.1, 443, ...]: two equiprobable
        # tokens -> exactly 1 bit.
        assert p.network_entropy == Fraction(1)

    def test_process_entropy_matches_closed_form(self):
        # process names a,b,a,c -> p = {0.5, 0.25, 0.25} -> H = 1.5 bits.
        events = [_ev(n) for n in ("a", "b", "a", "c")]
        p = BehavioralFingerprint()._compute_profile(events)
        assert float(p.process_entropy) == pytest.approx(1.5, abs=1e-9)

    def test_temporal_entropy_is_log2_of_distinct_count(self):
        # four distinct timestamps -> H = log2(4) = 2 bits.
        events = [_ev(timestamp=t) for t in (100, 200, 300, 400)]
        p = BehavioralFingerprint()._compute_profile(events)
        assert float(p.temporal_entropy) == pytest.approx(2.0, abs=1e-9)

    def test_composite_uses_documented_weights(self):
        # composite = 0.4*process + 0.3*network + 0.3*temporal.
        events = [
            _ev("a", "1.1.1.1", 80, 100),
            _ev("b", "2.2.2.2", 443, 200),
            _ev("a", "1.1.1.1", 80, 300),
            _ev("c", "3.3.3.3", 22, 400),
        ]
        p = BehavioralFingerprint()._compute_profile(events)
        expected = (
            p.process_entropy * Fraction(4, 10)
            + p.network_entropy * Fraction(3, 10)
            + p.temporal_entropy * Fraction(3, 10)
        )
        assert p.composite_entropy == expected

    def test_missing_keys_do_not_crash_and_yield_zero(self):
        # No process_name/dst_* anywhere; timestamps default to 0 (constant).
        p = BehavioralFingerprint()._compute_profile([{"foo": 1}, {"bar": 2}])
        assert p.process_entropy == Fraction(0)
        assert p.network_entropy == Fraction(0)
        assert p.temporal_entropy == Fraction(0)

    def test_empty_events_is_all_zero_profile(self):
        p = BehavioralFingerprint()._compute_profile([])
        assert p == BehavioralProfile(
            process_entropy=Fraction(0),
            network_entropy=Fraction(0),
            temporal_entropy=Fraction(0),
            composite_entropy=Fraction(0),
        )

    def test_all_entropy_fields_are_exact_fractions(self):
        # Invariant #4: scoring stays in Fraction, no float leakage in the profile.
        events = [_ev("a", "1.1.1.1", 80, 100), _ev("b", "2.2.2.2", 443, 200)]
        p = BehavioralFingerprint()._compute_profile(events)
        for field in (p.process_entropy, p.network_entropy,
                      p.temporal_entropy, p.composite_entropy):
            assert isinstance(field, Fraction)


# ---------------------------------------------------------------------------
# Determinism -- same input must fingerprint identically
# ---------------------------------------------------------------------------

class TestDeterminism:
    events = [
        _ev("a", "1.1.1.1", 80, 100),
        _ev("b", "2.2.2.2", 443, 200),
        _ev("a", "1.1.1.1", 80, 300),
        _ev("c", "3.3.3.3", 22, 400),
    ]

    def test_same_input_same_profile(self):
        a = BehavioralFingerprint()._compute_profile(self.events)
        b = BehavioralFingerprint()._compute_profile(list(self.events))
        assert a == b

    def test_identical_event_sets_fingerprint_identically(self):
        set_a = [_ev("x", "10.0.0.1", 1, 1), _ev("y", "10.0.0.2", 2, 2)]
        set_b = [_ev("x", "10.0.0.1", 1, 1), _ev("y", "10.0.0.2", 2, 2)]
        bf = BehavioralFingerprint()
        assert (bf._compute_profile(set_a).composite_entropy
                == bf._compute_profile(set_b).composite_entropy)

    def test_analyze_is_repeatable(self):
        bf = BehavioralFingerprint()
        bf.train_baseline([_ev("chrome", "1.1.1.1", 443, 1000)] * 5)
        r1 = bf.analyze(self.events)
        r2 = bf.analyze(self.events)
        assert r1.deviation_score == r2.deviation_score
        assert r1.to_signal().z_score == r2.to_signal().z_score


# ---------------------------------------------------------------------------
# train_baseline / analyze -- baseline lifecycle and deviation detection
# ---------------------------------------------------------------------------

class TestAnalyzeAgainstBaseline:
    def test_train_baseline_returns_and_stores_profile(self):
        bf = BehavioralFingerprint()
        events = [_ev("a", "1.1.1.1", 1, 1), _ev("a", "1.1.1.1", 1, 1)]
        ret = bf.train_baseline(events)
        assert isinstance(ret, BehavioralProfile)
        assert ret == bf._baseline

    def test_analyze_without_baseline_is_neutral(self):
        # Docstring/code: no baseline -> deviation 0, no anomalies, composite 0,
        # and baseline_profile is set equal to current_profile.
        bf = BehavioralFingerprint()
        r = bf.analyze([_ev("a", "1.1.1.1", 1, 1)])
        assert r.deviation_score == Fraction(0)
        assert r.anomalies == []
        assert r.composite_score == Fraction(0)
        assert r.baseline_profile == r.current_profile

    def test_identical_to_baseline_produces_no_anomaly(self):
        events = [_ev("chrome", "1.1.1.1", 443, 1000)] * 10
        bf = BehavioralFingerprint()
        bf.train_baseline(events)
        r = bf.analyze(events)
        assert r.deviation_score == Fraction(0)
        assert r.anomalies == []

    def test_clear_deviation_fires_all_three_anomalies(self):
        # baseline: constant (all entropies 0). attack: 8 distinct on every axis
        # (~3 bits each). Every per-axis deviation crosses the 0.3 threshold.
        bf = BehavioralFingerprint()
        bf.train_baseline([_ev("chrome", "1.1.1.1", 443, 1000)] * 10)
        attack = [_ev(str(i), f"{i}.0.0.1", i, i) for i in range(8)]
        r = bf.analyze(attack)
        types = {a["type"] for a in r.anomalies}
        assert types == {
            "PROCESS_ENTROPY_DEVIATION",
            "NETWORK_ENTROPY_DEVIATION",
            "TEMPORAL_ENTROPY_DEVIATION",
        }

    def test_single_axis_deviation_scoring_is_exact(self):
        # Only process entropy moves: baseline 0 bits, current exactly 1 bit,
        # network/temporal held identical between baseline and current.
        base = [_ev("p", "1.1.1.1", 1, 5), _ev("p", "1.1.1.1", 1, 5)]
        cur = [_ev("a", "1.1.1.1", 1, 5), _ev("b", "1.1.1.1", 1, 5)]
        bf = BehavioralFingerprint()
        bf.train_baseline(base)
        r = bf.analyze(cur)
        # dev_process = 1 -> deviation = 0.5*1 = 1/2.
        assert r.deviation_score == Fraction(1, 2)
        # severity = min(2*dev, 0.95) = 0.95 ; composite = min(sum, 0.95) = 0.95.
        assert len(r.anomalies) == 1
        assert r.anomalies[0]["type"] == "PROCESS_ENTROPY_DEVIATION"
        assert Fraction(r.anomalies[0]["severity"]) == Fraction(95, 100)
        assert r.composite_score == Fraction(95, 100)

    def test_deviation_uses_process_weighted_051(self):
        # Deviation weights are 0.5/0.3/0.2 (process weighted highest) -- pin the
        # exact linear combination against a hand-computed baseline/current pair.
        base = [_ev("p", "1.1.1.1", 1, 5)] * 2          # p/n/t entropy = 0/1/0
        cur = [_ev("a", "9.9.9.9", 7, 3), _ev("b", "8.8.8.8", 6, 4)]
        bf = BehavioralFingerprint()
        b = bf._compute_profile(base)
        c = bf._compute_profile(cur)
        bf.train_baseline(base)
        r = bf.analyze(cur)
        expected = (
            abs(c.process_entropy - b.process_entropy) * Fraction(5, 10)
            + abs(c.network_entropy - b.network_entropy) * Fraction(3, 10)
            + abs(c.temporal_entropy - b.temporal_entropy) * Fraction(2, 10)
        )
        assert r.deviation_score == expected


# ---------------------------------------------------------------------------
# BehavioralFingerprintResult.to_signal -- SignalOutput mapping
# ---------------------------------------------------------------------------

class TestToSignal:
    def _result_with(self, bf, base, cur):
        bf.train_baseline(base)
        return bf.analyze(cur)

    def test_neutral_result_maps_to_zero_signal(self):
        r = BehavioralFingerprint().analyze([_ev("a", "1.1.1.1", 1, 1)])
        sig = r.to_signal()
        assert sig.z_score == 0.0
        assert sig.value == 0.0
        assert sig.confidence == 0.0

    def test_z_score_bands_follow_deviation_thresholds(self):
        # deviation 1/2 -> exactly the 0.5 band -> z = 2.0.
        bf = BehavioralFingerprint()
        r = self._result_with(
            bf,
            [_ev("p", "1.1.1.1", 1, 5), _ev("p", "1.1.1.1", 1, 5)],
            [_ev("a", "1.1.1.1", 1, 5), _ev("b", "1.1.1.1", 1, 5)],
        )
        assert r.deviation_score == Fraction(1, 2)
        assert r.to_signal().z_score == 2.0

    def test_high_deviation_maps_to_z_three(self):
        bf = BehavioralFingerprint()
        r = self._result_with(
            bf,
            [_ev("chrome", "1.1.1.1", 443, 1000)] * 10,
            [_ev(str(i), f"{i}.0.0.1", i, i) for i in range(8)],
        )
        assert r.deviation_score >= Fraction(8, 10)
        sig = r.to_signal()
        assert sig.z_score == 3.0
        # value = z / Z_CLIP_MAX = 3.0 / 5.0.
        assert sig.value == pytest.approx(0.6, abs=1e-12)

    def test_confidence_formula_is_exact(self):
        # confidence = min(composite * 1.1 * 0.70, 0.95). With composite = 0.95:
        # 0.95 * 1.1 * 0.70 = 0.7315.
        bf = BehavioralFingerprint()
        r = self._result_with(
            bf,
            [_ev("p", "1.1.1.1", 1, 5), _ev("p", "1.1.1.1", 1, 5)],
            [_ev("a", "1.1.1.1", 1, 5), _ev("b", "1.1.1.1", 1, 5)],
        )
        assert r.composite_score == Fraction(95, 100)
        assert r.to_signal().confidence == pytest.approx(0.7315, abs=1e-9)

    def test_signal_metadata_is_consistent(self):
        bf = BehavioralFingerprint()
        r = self._result_with(
            bf,
            [_ev("chrome", "1.1.1.1", 443, 1000)] * 10,
            [_ev(str(i), f"{i}.0.0.1", i, i) for i in range(8)],
        )
        sig = r.to_signal()
        md = sig.metadata
        assert md["anomaly_count"] == len(r.anomalies)
        assert md["artifact_type"] == "behavioral"
        # finding_types is the sorted unique set of anomaly types.
        assert md["finding_types"] == sorted({a["type"] for a in r.anomalies})
        assert md["current_entropy"] == str(r.current_profile.composite_entropy)


# ---------------------------------------------------------------------------
# Cross-check the entropy kernel this module relies on
# ---------------------------------------------------------------------------

class TestUnderlyingEntropyKernel:
    def test_two_equiprobable_tokens_is_one_bit(self):
        assert float(_entropy_shannon(["a", "b"])) == pytest.approx(1.0, abs=1e-9)

    def test_three_equiprobable_tokens_matches_log2_3(self):
        assert float(_entropy_shannon(["a", "b", "c"])) == pytest.approx(
            math.log2(3), abs=1e-9
        )

    def test_skewed_distribution_matches_closed_form(self):
        expected = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
        assert float(_entropy_shannon(["a", "a", "a", "b"])) == pytest.approx(
            expected, abs=1e-9
        )

    def test_returns_exact_fraction(self):
        assert isinstance(_entropy_shannon(["a", "b"]), Fraction)


# ---------------------------------------------------------------------------
# CHARACTERIZATION -- inherent entropy blind spot (documented, NOT a failure)
# ---------------------------------------------------------------------------

class TestDistributionBlindSpotCharacterization:
    """
    FINDING-FP-BLINDSPOT -- distribution-only fingerprint is content-blind.

    The fingerprint compares Shannon entropy of the current profile against the
    baseline. Entropy captures the SHAPE of a distribution, never the identity
    of the tokens. Consequently an attacker who replaces every baseline
    process/IP/port/timestamp with different values but preserves the same
    counts and shape produces a profile whose per-axis entropy is byte-for-byte
    identical to the baseline -- deviation 0.0, zero anomalies, z = 0.0. A full
    process/network substitution (e.g. chrome/word -> mimikatz/cobalt on new
    C2 IPs) is therefore invisible to this detector.

    Scope: PLAUSIBLE as a detection weakness. It is a genuine false-negative
    surface for a component described as a "behavioral fingerprint" for a
    forensic pipeline. It is NOT scored as a code bug and is NOT left failing
    because it is inherent to any entropy-of-distribution metric and violates
    no formula or contract stated in the module -- the code computes exactly
    what it claims to compute. This test pins the observed behavior so that any
    future move to an identity-aware fingerprint (which WOULD flag this case)
    surfaces as an intentional change rather than a silent one.

    Suggested hardening (not applied here): incorporate token-set membership
    (e.g. Jaccard distance between baseline and current process/IP sets)
    alongside entropy so that "same shape, different contents" is detectable.
    """

    def test_content_swap_preserving_shape_is_not_detected(self):
        baseline = [
            _ev("chrome", "1.1.1.1", 443, 10),
            _ev("word", "2.2.2.2", 80, 20),
        ]
        attacker = [
            _ev("mimikatz", "9.9.9.9", 4444, 99),
            _ev("cobalt", "8.8.8.8", 5555, 88),
        ]
        bf = BehavioralFingerprint()
        bf.train_baseline(baseline)
        r = bf.analyze(attacker)
        # Documented blind spot: totally different malicious behavior, zero signal.
        assert r.deviation_score == Fraction(0)
        assert r.anomalies == []
        assert r.to_signal().z_score == 0.0
