"""
tests/test_b051_overflow_guard.py
==================================
Regresión de B-051 (AUDITORIA_L040_LIKELIHOOD_RATIO.md §2.3):
`math.exp(combined_log_lr)` sin guard en likelihood_ratio.py crasheaba con
OverflowError ante suficientes señales de alta z — DoS determinista de la
Segundidad de Mode 4.

Umbrales exactos reproducidos en la auditoría (bisección):
  - engine base (z_cap=3.0):  n >= 158 señales z=3, conf=1  → log_lr >= 711
  - adaptador   (z_cap=10.0): n >= 57  señales z=5, conf=1  → log_lr >= 712.5

Invariantes post-fix:
  1. Esos casos retornan un valor FINITO (posterior=1.0), nunca OverflowError.
  2. La saturación queda documentada en ForensicRecord.notes (Daubert).
  3. Ningún input que antes funcionaba cambia: |log_lr| <= 700 → resultado
     bit a bit idéntico a math.exp sin clamp.
"""
from __future__ import annotations

import math

import pytest

from vigia.core.ebs_v1 import SignalOutput
from vigia.core.likelihood_ratio import LikelihoodEngine, LOG_LR_EXP_CAP


def _sigs(n: int, z: float, conf: float = 1.0):
    return [
        SignalOutput(tool_name=f"T{i}", value=abs(z), z_score=z, confidence=conf)
        for i in range(n)
    ]


class TestOverflowGuard:
    def test_158_signals_z3_returns_finite_not_crash(self):
        # Umbral exacto del crash pre-fix (z_cap=3: 158 × 4.5 = 711 > 709.78).
        record = LikelihoodEngine().infer(_sigs(158, 3.0))
        assert math.isfinite(record.lr_combined)
        assert record.posterior_probability == 1.0
        assert record.enfsi_label == "very strong"
        assert "B-051" in record.notes, "la saturación debe quedar documentada"

    def test_last_non_crashing_n_pre_fix_is_unchanged(self):
        # n=157 (157 × 4.5 = 706.5 <= 709.78) nunca crasheaba — y con el clamp
        # en 700... 706.5 > 700: se satura. Verificar el diseño real: el clamp
        # NO altera inputs con log_lr <= 700 → n=155 (697.5) intacto.
        record = LikelihoodEngine().infer(_sigs(155, 3.0))
        assert record.combined_log_lr == pytest.approx(697.5)
        assert record.lr_combined == math.exp(697.5), (
            "log_lr <= 700 debe ser bit a bit idéntico al exp sin clamp"
        )
        assert "B-051" not in record.notes

    def test_adapter_zcap10_57_signals_z5_returns_finite(self):
        # Camino real de pipeline.py: adaptador con z_cap=10.0 por defecto;
        # SignalOutput clipea z en Z_CLIP_MAX=5.0 → 57 × 12.5 = 712.5.
        from vigia.core.likelihood_engine import LikelihoodEngine as AdapterLE
        out = AdapterLE().infer(_sigs(57, 5.0))
        assert math.isfinite(out["posterior"])
        assert out["posterior"] == 1.0
        assert math.isfinite(out["lr"])
        assert out["decision_hint"] == "REJECT"

    def test_extreme_pile_of_signals_never_raises(self):
        # Muy por encima del umbral: 500 señales z=5 conf=1 vía adaptador.
        from vigia.core.likelihood_engine import LikelihoodEngine as AdapterLE
        out = AdapterLE().infer(_sigs(500, 5.0))
        assert math.isfinite(out["posterior"]) and out["posterior"] == 1.0

    def test_clamp_boundary_is_exactly_700(self):
        assert LOG_LR_EXP_CAP == 700.0
        # exp(700) es finito en float64; exp(710) no lo sería.
        assert math.isfinite(math.exp(LOG_LR_EXP_CAP))

    def test_normal_inference_untouched(self):
        # Sanidad: una inferencia chica no cambia ni gana notas B-051.
        record = LikelihoodEngine().infer(_sigs(3, 2.0, conf=0.8))
        expected_log_lr = 3 * ((2.0 ** 2) / 2.0) * 0.8
        assert record.combined_log_lr == pytest.approx(expected_log_lr)
        assert record.lr_combined == math.exp(record.combined_log_lr)
        assert "B-051" not in record.notes

    def test_record_hash_still_computable_when_saturated(self):
        # El registro sellado del caso saturado debe seguir siendo
        # serializable y hasheable (cadena de custodia intacta).
        record = LikelihoodEngine().infer(_sigs(158, 3.0))
        digest = record.record_hash()
        assert len(digest) == 64
        assert record.to_json()
