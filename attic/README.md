# attic/ — retired, non-executing artifacts

Files here are **dormant** — verified to have zero references from live code, tests,
or CI at the time of retirement. They are kept (not deleted) for provenance. Paths
mirror the original repo layout.

## 2026-07-23 — calibration fossils

Retired the empirical-calibration exploration that was never wired into the
deterministic decision path (VIGÍA runs uncalibrated `z²/2` by design; the
signal-quality gate is SHADOW/WARN). Full assessment and per-file evidence:
`docs/CALIBRATION_ARCHAEOLOGY_20260723.md`.

Moved (each had zero test/CI/live references — verified before moving):
- `data/calibration_ladder_dataset_20260705.json` — ladder study dataset; only its
  own generator referenced it.
- `scripts/generate_ladder_dataset.py` — standalone generator for the above.
- `vigia/tools/generate_calibration.py` — never invoked; not imported by the package.
- `vigia/tools/build_calibration_dataset.py` — never invoked; not imported.
- `models/calibrated_lr_models.pkl` — KDE/Ledoit-Wolf models; no live loader (only
  written by `vigia/core/fit_calibration.py`, which stays and can regenerate).

NOT moved (retained because tests validate them or the pipeline can load them
opt-in): `data/calibration_dataset.json`, `data/signal_calibration_dataset_20260709.json`,
`data/vigia_60_cases_dataset.json`, `data/dataset_test_cases.json`,
`scripts/fit_calibration.py`, `scripts/run_calibration.py`,
`scripts/build_signal_calibration_dataset.py`, `models/calibrated_lr.json`,
`models/nlp_covariance*.{pkl,json}`, `models/calibration_metadata.json`.
