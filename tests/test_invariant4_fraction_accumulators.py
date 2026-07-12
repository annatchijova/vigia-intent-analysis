"""
Invariant-4 regression — fracture boost/penalty accumulation is emission-order
invariant and bit-compatible with the historical per-term float values.

Ref: docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-E. The pre-fix accumulator
(plain float `+=`) made the sealed verdict depend on fracture EMISSION ORDER:
a constructed reproduction through the real engine flipped UNKNOWN<->SUSPICION
at a rounding cliff from order alone (2 real-engine flips; 0 after the fix).
The fix lifts each per-term float product exactly into Fraction and sums
exactly, so:

  (a) any permutation of emitted fractures yields a bit-identical score and
      verdict (exact addition is associative/commutative);
  (b) each term keeps the exact float value the old code produced (single
      multiplication has no ordering), so 0-2-term cases — the entire corpus —
      are bit-identical to the pre-fix engine (verified corpus-wide by
      scripts/experiments/fraction_gate.py);
  (c) cap semantics are unchanged: CAIE-fracture sum capped at 0.5 FIRST,
      then STATISTICAL_UNIFORMITY terms added, then capped again.
"""

import copy
import itertools
import logging

import pytest

logging.disable(logging.CRITICAL)

import vigia.tools.caie as caie_mod  # noqa: E402
from vigia_scorer import _vigia_score  # noqa: E402

_ORIG_DETECT = caie_mod.CrossArtifactIncongruenceEngine.detect_fractures


class _FakeFracture:
    def __init__(self, severity, ftype="DOCUMENT_FORGERY"):
        self.fracture_type = ftype
        self.severity = severity
        self.artifact_a = "synthetic-a"
        self.artifact_b = "synthetic-b"
        self.interpretation = "synthetic fracture for order-invariance test"
        self.ttp_id = None


CASE = {
    "case_id": "INV4-ORDER-TEST",
    "expected_verdict": "UNKNOWN",
    "artifacts": [
        {
            "artifact_id": "a1", "evidence_type": "log_entry",
            "source_tool": "test", "raw_score": 0.30,
            "description": "synthetic log artifact", "provenance_chain": ["sha256:x1"],
        },
        {
            "artifact_id": "a2", "evidence_type": "file_metadata",
            "source_tool": "test", "raw_score": 0.25,
            "description": "synthetic metadata artifact", "provenance_chain": ["sha256:x2"],
        },
    ],
}


@pytest.fixture
def emit(monkeypatch):
    """Score CASE with a forced fracture emission list (in the given order)."""
    def _run(severities, ftype="DOCUMENT_FORGERY"):
        def patched(self):
            return [_FakeFracture(s, ftype) for s in severities]
        monkeypatch.setattr(
            caie_mod.CrossArtifactIncongruenceEngine, "detect_fractures", patched)
        try:
            return _vigia_score(copy.deepcopy(CASE))
        finally:
            monkeypatch.setattr(
                caie_mod.CrossArtifactIncongruenceEngine, "detect_fractures",
                _ORIG_DETECT)
    return _run


TRIPLES = [
    # The historical flip family: two small severities plus a third tuned near
    # a rounding cliff (the exact cliff value is platform-searched, but exact
    # summation must be order-invariant for EVERY value, so representative
    # awkward floats are sufficient to lock the property).
    (0.03, 0.007, 0.12844444444444444),
    (0.1, 0.2, 0.30000000000000004),
    (0.8, 0.85, 0.9),
    (1e-06, 0.4999999, 0.25),
]


class TestEmissionOrderInvariance:

    @pytest.mark.parametrize("sevs", TRIPLES, ids=lambda s: repr(s)[:40])
    def test_all_permutations_bit_identical(self, emit, sevs):
        outcomes = set()
        for order in itertools.permutations(sevs):
            r = emit(list(order))
            outcomes.add((r["verdict"], repr(r["score"]),
                          repr(r["fracture_malice_boost"])))
        assert len(outcomes) == 1, (
            f"emission order changed the sealed result: {sorted(outcomes)}"
        )

    def test_penalty_accumulator_also_invariant(self, emit):
        outcomes = set()
        for order in itertools.permutations((0.6, 0.31, 0.055)):
            r = emit(list(order), ftype="VERDICT_CONFLICT")
            outcomes.add((r["verdict"], repr(r["score"]),
                          repr(r["fracture_credibility_penalty"])))
        assert len(outcomes) == 1


class TestBitCompatibilityWithLegacyTerms:

    def test_single_term_equals_legacy_float_product(self, emit):
        # The exposed field is _dround'ed to 4 decimals (unchanged semantics);
        # internal bit-compatibility with the legacy accumulator is proven
        # corpus-wide by scripts/experiments/fraction_gate.py.
        r = emit([0.8])
        assert float(r["fracture_malice_boost"]) == round(0.8 * 0.45, 4)

    def test_two_terms_equal_legacy_single_rounding_sum(self, emit):
        r = emit([0.8, 0.1])
        assert float(r["fracture_malice_boost"]) == round((0.8 * 0.45) + (0.1 * 0.45), 4)

    def test_cap_still_binds_at_exactly_half(self, emit):
        # The CAN-037 shape: two heavy fractures saturate the 0.5 cap.
        r = emit([0.95, 1.0])
        assert r["fracture_malice_boost"] == 0.5

    def test_su_terms_add_after_first_cap_then_recap(self, emit):
        # Fracture mass alone saturates the cap; SU on top must not exceed it.
        case = copy.deepcopy(CASE)
        case["temporal_violations"] = [
            {"type": "STATISTICAL_UNIFORMITY", "severity": 0.85},
        ]
        def patched(self):
            return [_FakeFracture(0.95), _FakeFracture(1.0)]
        caie_mod.CrossArtifactIncongruenceEngine.detect_fractures = patched
        try:
            r = _vigia_score(case)
        finally:
            caie_mod.CrossArtifactIncongruenceEngine.detect_fractures = _ORIG_DETECT
        assert r["fracture_malice_boost"] == 0.5
