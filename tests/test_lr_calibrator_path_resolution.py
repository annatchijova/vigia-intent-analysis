"""Regression tests for B-098 — dead H28 calibrator path and silent excepts.

The H28 enrichment derived '<name>_isotonic.json' from calibration_path via a
naive str.replace and looked ONLY for that file. No tool in this repo produces
it (scripts/run_calibration.py writes 'calibrated_lr.json'), so H28 was dead
with the documented flow, and the surrounding except blocks either swallowed
the real cause or logged a false one ("no encontrado" for a corrupt file).

Fixed behavior under test:
- _candidate_calibrator_paths tries the legacy isotonic variant first, then
  calibration_path itself.
- VigiaPipeline(calibration_path='models/calibrated_lr.json') actually loads
  a calibrator (H28 alive with the documented flow).
- A corrupt candidate is reported as a WARNING with its real cause and does
  not block the next candidate.
- LikelihoodEngine logs a WARNING (not a bare pass) when the calibrator
  cannot be loaded and it degrades to FALLBACK mode.
"""

import json
import logging
import os
import shutil
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from vigia.pipeline.pipeline import VigiaPipeline, _candidate_calibrator_paths

CANONICAL_CALIBRATOR = os.path.join(REPO_ROOT, "models", "calibrated_lr.json")


class TestCandidatePaths:
    def test_documented_flow_includes_the_path_itself(self):
        cands = _candidate_calibrator_paths("models/calibrated_lr.json")
        assert cands == [
            os.path.join("models", "calibrated_lr_isotonic.json"),
            "models/calibrated_lr.json",
        ]

    def test_empty_and_none_yield_no_candidates(self):
        assert _candidate_calibrator_paths("") == []
        assert _candidate_calibrator_paths(None) == []

    def test_pathological_names_do_not_explode(self):
        # Old str.replace produced 'a_isotonic.json_isotonic.json' for
        # 'a.json.json' and a no-op for '.pkl' (then tried json.load on a
        # pickle). The new derivation is suffix-aware and always keeps the
        # original path as a candidate.
        for name in ("model.json.bak", "config", "a.json.json", "cal.pkl"):
            cands = _candidate_calibrator_paths(name)
            assert cands[-1] == name
            assert 1 <= len(cands) <= 2


class TestH28Resurrection:
    def test_documented_flow_loads_calibrator(self):
        # run_calibration.py documents:
        #   VigiaPipeline(calibration_path='models/calibrated_lr.json')
        # Before the fix this never loaded anything (only *_isotonic.json was
        # tried), silently.
        assert os.path.isfile(CANONICAL_CALIBRATOR), (
            "repo fixture models/calibrated_lr.json missing"
        )
        pipeline = VigiaPipeline(calibration_path=CANONICAL_CALIBRATOR)
        assert pipeline._lr_calibrator is not None, (
            "H28 calibrator not loaded from the documented calibration_path "
            "(B-098 regression)"
        )
        assert pipeline._lr_calibrator.is_fitted

    def test_corrupt_isotonic_falls_back_with_warning(self, tmp_path, caplog):
        cal_path = tmp_path / "cal.json"
        shutil.copy(CANONICAL_CALIBRATOR, cal_path)
        iso_path = tmp_path / "cal_isotonic.json"
        iso_path.write_text("{not valid json", encoding="utf-8")

        with caplog.at_level(logging.INFO, logger="vigia.pipeline.pipeline"):
            pipeline = VigiaPipeline(calibration_path=str(cal_path))

        assert pipeline._lr_calibrator is not None, (
            "corrupt isotonic candidate must not block the valid fallback"
        )
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert any("existe pero no se pudo cargar" in r.getMessage() for r in warnings), (
            "a corrupt (existing) candidate must be logged as WARNING with "
            "its real cause, not as 'not found' at INFO"
        )

    def test_missing_calibrator_stays_uncalibrated_without_warning(self, tmp_path, caplog):
        with caplog.at_level(logging.INFO, logger="vigia.pipeline.pipeline"):
            pipeline = VigiaPipeline(calibration_path=str(tmp_path / "nope.json"))
        assert pipeline._lr_calibrator is None
        # Absent optional component: documented degradation, not a warning.
        assert not [
            r for r in caplog.records
            if r.levelno >= logging.WARNING and "H28" in r.getMessage()
        ]


class TestLikelihoodEngineLogging:
    def test_fallback_cause_is_logged(self, caplog):
        from vigia.core.likelihood_engine import LikelihoodEngine

        with caplog.at_level(logging.WARNING, logger="vigia.core.likelihood_engine"):
            engine = LikelihoodEngine(calibration_path="/nonexistent/cal.json")
        assert engine._mode == "FALLBACK"
        assert any(
            "calibrador no cargado" in r.getMessage() for r in caplog.records
        ), "FALLBACK degradation must log its cause (was a bare except: pass)"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
