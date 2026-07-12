"""
Guard del harness de medición A4 (`scripts/experiment_a4_profile_refit.py`).

Es una herramienta de MEDICIÓN, no código de veredicto. Este test verifica:
  · importar el script NO muta EVIDENCE_PROFILES (efecto global prohibido);
  · `derive_candidates` devuelve spoofability acotada en [0.15, 0.85] y solo
    para tipos legacy con ≥ min_signals señales.
No re-corre el gate comparativo (lento); ejercita la función pura.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "experiment_a4_profile_refit.py"


def _snapshot_profiles():
    from vigia.tools.caie import EVIDENCE_PROFILES
    return {k: (float(v.spoofability), float(v.base_weight)) for k, v in EVIDENCE_PROFILES.items()}


def test_import_does_not_mutate_profiles():
    before = _snapshot_profiles()
    spec = importlib.util.spec_from_file_location("a4_exp", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    after = _snapshot_profiles()
    assert before == after, "importar el harness mutó EVIDENCE_PROFILES (efecto global)"


def test_derive_candidates_are_bounded_and_legacy_only():
    spec = importlib.util.spec_from_file_location("a4_exp2", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from vigia.tools.caie import EVIDENCE_PROFILES as P

    cand, base_rate, n_legacy = mod.derive_candidates(k=0.6, min_signals=5)
    assert 0.0 <= base_rate <= 1.0
    assert n_legacy > 0
    for t, spoof in cand.items():
        assert 0.15 <= spoof <= 0.85, f"{t}: spoof {spoof} fuera de rango"
        # candidato solo sobre perfiles legacy (0.50/0.20)
        prof = P[t]
        assert abs(float(prof.base_weight) - 0.20) < 1e-9
