# Test — LRCalibrator serialization round-trip
#
# Origin: confirmed bug in vigia/core/lr_calibration.py.
# SklearnCalibrator.to_dict() did not serialize coef_/intercept_. load()
# silently left _backend=None for sklearn-backed calibrators, and
# calibrated_posterior()/calibrated_log_lr() silently fell back to the
# uncalibrated z²/2 placeholder instead of raising. This is the real
# explanation for coverage gap #9 ("LRCalibrator determinism unverified"):
# it looked deterministic because it was never actually using the trained
# model after a reload — every run used the same hardcoded placeholder.
#
# This test locks in the fix described in BUGS_PENDIENTES.md: round-trip
# fidelity for the sklearn backend, and hard failure (not silent fallback)
# on a corrupted or unrecognized-backend state.
#
# Run: pytest <test_dir>/test_lr_calibrator_serialization.py -v

import json
import math
import tempfile
from pathlib import Path

import pytest

from vigia.core.lr_calibration import LRCalibrator, SklearnCalibrator, PlattCalibrator


def _synthetic_z_scores(n: int = 60, seed: int = 42):
    import random
    rng = random.Random(seed)
    authentic = [rng.gauss(0.5, 1.0) for _ in range(n)]
    fabricated = [rng.gauss(3.0, 1.0) for _ in range(n)]
    return authentic, fabricated


def test_sklearn_backend_roundtrip_matches_before_save():
    """
    calibrated_posterior() before save() and after load() must agree on the
    same z-scores. If this fails, to_dict()/from_dict() are losing model
    parameters and the loaded calibrator is not the one that was fit.
    """
    pytest.importorskip("sklearn")
    authentic, fabricated = _synthetic_z_scores()

    cal = LRCalibrator()
    cal.fit(authentic, fabricated)
    assert cal.meta.get("backend") == "sklearn_logistic", (
        "Test assumes sklearn is available and selected as backend."
    )

    probe_zs = [-2.0, -0.5, 0.0, 0.8, 1.5, 2.5]
    before = [cal.calibrated_posterior(z) for z in probe_zs]

    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "calibrator.json"
        cal.save(str(path))
        raw = json.loads(path.read_text())
        assert "coef" in raw.get("backend", {}), (
            "to_dict() did not serialize 'coef' — the original bug is back."
        )
        assert "intercept" in raw.get("backend", {}), (
            "to_dict() did not serialize 'intercept' — the original bug is back."
        )
        cal2 = LRCalibrator.load(str(path))

    assert cal2.is_fitted
    after = [cal2.calibrated_posterior(z) for z in probe_zs]

    for z, p_before, p_after in zip(probe_zs, before, after):
        assert math.isclose(p_before, p_after, abs_tol=1e-6), (
            f"Round-trip mismatch at z={z}: before={p_before} after={p_after}. "
            f"to_dict()/from_dict() did not preserve the fitted model."
        )


def test_load_with_unrecognized_backend_type_raises():
    """
    load() must fail loudly on an unrecognized backend type instead of
    silently leaving _backend=None (the original failure mode).
    """
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "corrupt.json"
        path.write_text(json.dumps({
            "meta": {"backend": "some_future_backend"},
            "fitted": True,
            "backend": {"type": "some_future_backend", "fitted": True},
        }))
        with pytest.raises(ValueError):
            LRCalibrator.load(str(path))


def test_fitted_true_with_missing_backend_raises_on_use():
    """
    A corrupted state (fitted=True, backend=None) must raise on use, not
    silently fall back to the uncalibrated z²/2 placeholder. Silent
    fallback is exactly what made the production Brier Score report
    meaningless: it measured the in-memory model, not the file that was
    actually loaded and used downstream.
    """
    cal = LRCalibrator()
    cal._fitted = True
    cal._backend = None
    with pytest.raises(RuntimeError):
        cal.calibrated_posterior(1.0)
    with pytest.raises(RuntimeError):
        cal.calibrated_log_lr(1.0)


def test_unfitted_calibrator_uses_documented_placeholder():
    """
    fitted=False is a legitimate, documented state (calibrator never
    trained) — it must still return the z²/2 placeholder, not raise. Only
    fitted=True + backend=None (a corrupted/incomplete load) should raise.
    """
    cal = LRCalibrator()
    assert not cal.is_fitted
    p = cal.calibrated_posterior(1.0)
    assert 0.0 <= p <= 1.0


def test_platt_backend_roundtrip_still_works():
    """
    Regression guard: the fix to the sklearn path must not break the
    existing, already-working Platt manual round-trip.
    """
    authentic = [0.2, 0.4, 0.1, 0.6, 0.3, 0.5]
    fabricated = [2.8, 3.1, 2.5, 3.4, 2.9, 3.0]

    cal = PlattCalibrator()
    cal.fit(authentic, fabricated)
    before = cal.calibrated_posterior(1.0)

    d = cal.to_dict()
    cal2 = PlattCalibrator.from_dict(d)
    after = cal2.calibrated_posterior(1.0)

    assert math.isclose(before, after, abs_tol=1e-9)
