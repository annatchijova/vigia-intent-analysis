"""
tests/test_metabolic_profiler_groundtruth.py
============================================
Ground-truth tests for vigia/tools/metabolic_profiler.py (was 0% covered).

metabolic_profiler detects malicious artifacts by their "metabolic" cost:
object density (parser bombs), parse cost (obfuscation), reference depth
(pathological nesting), circular references, and object fragmentation. The
scoring core `_evaluate_metabolism` is a pure, deterministic function of its
inputs (Fraction arithmetic, fixed weight/threshold tables), so each verdict
and confidence has exactly one correct value that can be pinned from the code.

Most tests here pin that correct behavior. TestMicroObjectsBranchRegression
guards against BUG-METAB-001, a real defect found while writing these tests:
SIGNAL 5 (micro-object attack) referenced an out-of-scope `file_size`, raising
NameError on any artifact with >1000 objects. It is now fixed by threading
file_size into _evaluate_metabolism; that class is the regression guard. See
its docstring for the full analysis.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from vigia.tools.metabolic_profiler import MetabolicProfiler, MetabolicSignature


# Baseline efficiency for 'pdf' is 40 objects/KB; parse-cost baseline 50_000 ns.
# Thresholds in _evaluate_metabolism are multiples of these baselines.
PDF = "pdf"
EFF_BASE = Fraction(40, 1)
COST_BASE = Fraction(50_000, 1)
NORMAL = Fraction(1, 1)          # neutral depth_anomaly / non-tripping cost/eff
VALID_VERDICTS = {"BENIGN", "SUSPICIOUS", "MALICIOUS"}


@pytest.fixture()
def profiler():
    return MetabolicProfiler()


def _eval(profiler, *, eff=EFF_BASE, cost=COST_BASE, depth=NORMAL,
          circular=0, object_count=100, parse_time_ns=1, file_size=100_000):
    """Thin wrapper to call the pure scoring core with named signals.

    file_size only feeds SIGNAL 5 (object_count > 1000); with the default
    object_count=100 it never trips, so callers that do not set it are
    unaffected.
    """
    return profiler._evaluate_metabolism(
        PDF, eff, cost, depth, circular, object_count, parse_time_ns, file_size
    )


# ---------------------------------------------------------------------------
# _evaluate_metabolism -- pure deterministic scoring core
# ---------------------------------------------------------------------------

class TestEvaluateMetabolismGroundTruth:
    def test_no_signals_is_benign_with_high_confidence(self, profiler):
        verdict, conf, reasoning, evidence = _eval(profiler)
        assert verdict == "BENIGN"
        assert conf == Fraction(8, 10)
        assert reasoning == "Metabolic profile within normal parameters"
        # Benign branch reports the baselines it compared against.
        assert evidence == {"baseline_efficiency": 40.0, "baseline_cost": 50_000}

    def test_object_explosion_5x_is_suspicious(self, profiler):
        # efficiency > baseline*5 -> single 0.6 weight signal.
        verdict, conf, _, _ = _eval(profiler, eff=EFF_BASE * 6)
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(6, 10)

    def test_object_explosion_3x_is_suspicious_boundary(self, profiler):
        # efficiency > baseline*3 (not *5) -> weight 0.4 -> exactly the
        # SUSPICIOUS lower boundary (>= 0.4).
        verdict, conf, _, _ = _eval(profiler, eff=Fraction(150, 1))
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(4, 10)

    def test_object_explosion_2x_fires_signal_but_stays_benign(self, profiler):
        # efficiency > baseline*2 (not *3) -> weight 0.2 -> below the 0.4
        # SUSPICIOUS threshold, so verdict is BENIGN even though a signal fired
        # and the reasoning is tagged METABOLIC_ANOMALY. Characterization test.
        verdict, conf, reasoning, evidence = _eval(profiler, eff=Fraction(90, 1))
        assert verdict == "BENIGN"
        assert conf == Fraction(2, 10)
        assert reasoning.startswith("METABOLIC_ANOMALY")
        assert evidence["total_signals"] == 1

    def test_circular_over_five_is_malicious(self, profiler):
        # circular > 5 -> weight 0.8 -> MALICIOUS threshold (>= 0.8).
        verdict, conf, _, _ = _eval(profiler, circular=6)
        assert verdict == "MALICIOUS"
        assert conf == Fraction(8, 10)

    def test_circular_one_to_five_is_suspicious(self, profiler):
        verdict, conf, _, _ = _eval(profiler, circular=3)
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(6, 10)

    def test_pathological_depth_over_five_is_suspicious_alone(self, profiler):
        verdict, conf, _, _ = _eval(profiler, depth=Fraction(6, 1))
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(6, 10)

    def test_obfuscation_parse_cost_10x_is_suspicious(self, profiler):
        # parse_cost > baseline*10 -> weight 0.7 (still < 0.8 -> SUSPICIOUS).
        verdict, conf, _, _ = _eval(profiler, cost=COST_BASE * 11)
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(7, 10)

    def test_confidence_saturates_at_one(self, profiler):
        # Multiple critical signals sum to > 1.0 but confidence is capped.
        verdict, conf, _, _ = _eval(
            profiler, eff=Fraction(300, 1), cost=COST_BASE * 11,
            depth=Fraction(6, 1), circular=6
        )
        assert verdict == "MALICIOUS"
        assert conf == Fraction(1, 1)

    def test_unknown_type_uses_default_baselines(self, profiler):
        # Unknown type -> default efficiency baseline 50; 300 > 50*5 -> 0.6.
        verdict, conf, _, _ = profiler._evaluate_metabolism(
            "unknown", Fraction(300, 1), Fraction(100_000, 1),
            NORMAL, 0, 100, 1, 100_000
        )
        assert verdict == "SUSPICIOUS"
        assert conf == Fraction(6, 10)

    def test_signal_evidence_records_raw_confidence_and_count(self, profiler):
        _, _, _, evidence = _eval(profiler, eff=Fraction(300, 1))
        assert evidence["total_signals"] == 1
        assert evidence["confidence_raw"] == 0.6
        assert evidence["object_explosion"]["severity"] == "CRITICAL"

    def test_scoring_is_deterministic(self, profiler):
        a = _eval(profiler, eff=Fraction(300, 1), depth=Fraction(6, 1), circular=6)
        b = _eval(profiler, eff=Fraction(300, 1), depth=Fraction(6, 1), circular=6)
        assert a[0] == b[0]
        assert a[1] == b[1]
        assert a[2] == b[2]


# ---------------------------------------------------------------------------
# Helper methods -- type detection and expected-depth model
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_detect_type_by_magic_bytes(self, profiler, tmp_path):
        f = tmp_path / "a.pdf"
        f.write_bytes(b"%PDF-1.4\n...")
        assert profiler._detect_type(f) == "pdf"

    def test_detect_type_zip_variant_by_extension(self, profiler, tmp_path):
        # PK magic + .docx extension -> docx, not generic zip.
        f = tmp_path / "d.docx"
        f.write_bytes(b"PK\x03\x04rest")
        assert profiler._detect_type(f) == "docx"

    def test_detect_type_unknown(self, profiler, tmp_path):
        f = tmp_path / "x.bin"
        f.write_bytes(b"")
        assert profiler._detect_type(f) == "unknown"

    def test_expected_depth_pdf_is_logarithmic(self, profiler):
        # pdf: max(3, int(obj_count ** 0.3)); 1000**0.3 ~= 7.94 -> 7.
        assert profiler._calculate_expected_depth("pdf", 1000) == 7
        # small object counts clamp to the floor of 3.
        assert profiler._calculate_expected_depth("pdf", 1) == 3

    def test_expected_depth_fixed_and_default(self, profiler):
        assert profiler._calculate_expected_depth("docx", 5) == 5
        assert profiler._calculate_expected_depth("unknown", 10) == 3


# ---------------------------------------------------------------------------
# profile() -- end-to-end on real files (deterministic fields only)
# ---------------------------------------------------------------------------

class TestProfileEndToEnd:
    def _make_pdf(self, tmp_path: Path, n_objects: int) -> Path:
        # Pad heavily so object density stays well below the 2x baseline,
        # keeping the density signals dormant regardless of exact byte count.
        body = b"%PDF-1.4\n%" + b" " * 5000 + b"\n"
        for i in range(1, n_objects + 1):
            body += b"%d 0 obj\n<<>>\nendobj\n" % i
        p = tmp_path / "sample.pdf"
        p.write_bytes(body)
        return p

    def test_returns_signature_dataclass(self, profiler, tmp_path):
        sig = profiler.profile(self._make_pdf(tmp_path, 20))
        assert isinstance(sig, MetabolicSignature)
        assert sig.verdict in VALID_VERDICTS

    def test_signature_is_frozen(self, profiler, tmp_path):
        sig = profiler.profile(self._make_pdf(tmp_path, 20))
        import dataclasses
        with pytest.raises(dataclasses.FrozenInstanceError):
            sig.verdict = "TAMPERED"

    def test_pdf_fallback_counts_objects(self, profiler, tmp_path):
        # Without fitz the fallback counts "N 0 obj" markers exactly.
        sig = profiler.profile(self._make_pdf(tmp_path, 20))
        assert sig.object_count == 20

    def test_efficiency_ratio_matches_closed_form(self, profiler, tmp_path):
        # efficiency = object_count / (file_size / 1024), exact Fraction.
        p = self._make_pdf(tmp_path, 20)
        sig = profiler.profile(p)
        expected = Fraction(sig.object_count, 1) / Fraction(sig.file_size, 1024)
        assert sig.efficiency_ratio == expected
        assert isinstance(sig.efficiency_ratio, Fraction)

    def test_empty_file_yields_zero_ratios(self, profiler, tmp_path):
        # file_size == 0 -> the object_count>0 guard fails -> ratios are 0.
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        sig = profiler.profile(f)
        assert sig.file_size == 0
        assert sig.efficiency_ratio == Fraction(0)
        assert sig.parse_cost == Fraction(0)
        assert sig.verdict == "BENIGN"

    def test_deterministic_structural_fields(self, profiler, tmp_path):
        # parse_time_ns is wall-clock and may differ, but the structural
        # metrics must be identical across runs on the same bytes.
        p = self._make_pdf(tmp_path, 20)
        a = profiler.profile(p)
        b = profiler.profile(p)
        assert a.object_count == b.object_count
        assert a.file_size == b.file_size
        assert a.efficiency_ratio == b.efficiency_ratio
        assert a.depth_anomaly == b.depth_anomaly


# ---------------------------------------------------------------------------
# KNOWN DEFECT -- left failing on purpose (do not xfail; see docstring)
# ---------------------------------------------------------------------------

class TestMicroObjectsBranchRegression:
    """
    BUG-METAB-001 (FIXED) -- micro-objects signal crashed on any artifact with
    >1000 objects because it referenced an out-of-scope name. This class is now
    the regression guard for the fix.

    In _evaluate_metabolism, SIGNAL 5 (fragmentation / micro-object attack) was:

        if object_count > 1000:
            avg_size = file_size / object_count   # <-- NameError
            if avg_size < 10:
                ...

    `file_size` is NOT a parameter of _evaluate_metabolism (its parameters are
    file_type, efficiency, parse_cost, depth_anomaly, circular, object_count,
    parse_time_ns) and it is not a module/class global. The value exists only
    in the caller `profile()` and was never threaded into this method. So the
    moment `object_count > 1000`, evaluating `file_size / object_count` raises
    NameError("name 'file_size' is not defined") -- before the avg_size test is
    even reached, so it fires for EVERY high-object-count artifact.

    Impact: `profile()` does not catch this (only _parse_structure has a
    try/except), so the NameError propagates out of the public API and aborts
    the whole analysis. This is precisely the parser-bomb / object-explosion
    regime the profiler exists to flag: the detector is dead exactly where it
    is needed most.

    Scope of confirmation: CONFIRMED end-to-end. Proven both by calling
    _evaluate_metabolism directly with object_count=2000 and by driving
    profile() on a fallback-parsed PDF carrying >1000 "N 0 obj" markers -- both
    raise NameError.

    Refutation considered: not an intentional guard (there is no bare except
    swallowing it, and the branch clearly intends to compute avg object size),
    not a test misunderstanding (the parameter list provably omits file_size).
    It is a genuine defect.

    Fix applied: file_size was added to the _evaluate_metabolism signature and
    is passed from profile(), so `avg_size = file_size / object_count` now
    resolves. These tests assert the >1000-object path completes and returns a
    valid verdict instead of raising.
    """

    def test_scoring_handles_over_1000_objects(self, profiler):
        verdict, conf, _, _ = _eval(profiler, object_count=2000)
        assert verdict in VALID_VERDICTS

    def test_profile_survives_high_object_count(self, profiler, tmp_path):
        body = b"%PDF-1.4\n"
        for i in range(1, 1201):
            body += b"%d 0 obj\n<<>>\nendobj\n" % i
        p = tmp_path / "bomb.pdf"
        p.write_bytes(body)
        sig = profiler.profile(p)
        assert sig.verdict in VALID_VERDICTS
