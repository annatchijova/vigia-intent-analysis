"""
B-059 (TANDA 1, 2026-07-06) — Escala ENFSI unificada en vigia/core/enfsi.

Pre-fix existían 4 implementaciones divergentes (ebs_v1 8-buckets/EN sellada
en el bundle, signal_contract 5-buckets/ES, evidence_narrative_gen 7-buckets
bilingüe del reporte judicial, y un fallback inline en el bridge). Divergencia
reproducida: LR=5 → "limited" (bundle) vs "weak support" (reporte); LR=500 →
"moderately strong" vs "strong support".

Contrato post-fix:
  1. Un solo bucketing: todos los entry points delegan en vigia.core.enfsi.
  2. Semántica del bundle sellado preservada bit a bit para LR finito
     (ningún bundle histórico cambia de etiqueta).
  3. El reporte judicial deriva su frase del MISMO bucket canónico — los
     casos de divergencia del audit ahora coinciden por construcción.
"""

import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia.core import enfsi  # noqa: E402
from vigia.core.enfsi import ENFSI_NARRATIVE, enfsi_label, enfsi_narrative  # noqa: E402


class TestSingleSource:
    def test_ebs_v1_reexports_canonical(self):
        from vigia.core.ebs_v1 import enfsi_label as ebs_label
        assert ebs_label is enfsi_label

    def test_signal_contract_reexports_canonical(self):
        from vigia.tools.signal_contract import enfsi_label as sc_label
        assert sc_label is enfsi_label

    def test_likelihood_ratio_import_chain_is_canonical(self):
        from vigia.core.likelihood_ratio import enfsi_label as lr_label
        assert lr_label is enfsi_label

    def test_narrative_gen_delegates_to_canonical(self):
        sys.path.insert(0, str(REPO / "forensics"))
        import evidence_narrative_gen as gen
        for lr in [0, 0.5, 1, 5, 50, 500, 5000, 50000]:
            for lang in ("es", "en"):
                assert gen._enfsi_label(lr, lang) == enfsi_narrative(lr, lang)

    def test_no_other_enfsi_scale_definitions_remain(self):
        """Ninguna otra tabla ENFSI_SCALE viva fuera del módulo canónico."""
        import subprocess
        r = subprocess.run(
            ["grep", "-rln", "ENFSI_SCALE = [", "--include=*.py",
             str(REPO / "vigia"), str(REPO / "forensics")],
            capture_output=True, text=True,
        )
        offenders = [l for l in r.stdout.splitlines() if l.strip()]
        assert offenders == [], f"Escalas ENFSI duplicadas: {offenders}"


class TestSealedBundleSemanticsPreserved:
    """Pin bit a bit de la escala histórica de ebs_v1 (la sellada en bundles)."""

    @pytest.mark.parametrize("lr,expected", [
        (0, "inconclusive"),
        (0.5, "supports_H0"),
        (1, "weak"),
        (1.99, "weak"),
        (2, "limited"),
        (5, "limited"),
        (9.99, "limited"),
        (10, "moderate"),
        (99.9, "moderate"),
        (100, "moderately strong"),
        (500, "moderately strong"),
        (1000, "strong"),
        (9999, "strong"),
        (10000, "very strong"),
        (1e9, "very strong"),
        (float("inf"), "very strong"),
    ])
    def test_canonical_buckets(self, lr, expected):
        assert enfsi_label(lr) == expected

    def test_nan_guard(self):
        """NaN no es un LR — pre-fix caía silenciosamente en 'very strong'."""
        assert enfsi_label(float("nan")) == "inconclusive"


class TestAuditDivergenceCasesNowConsistent:
    """Los dos casos [REPRODUCIDO] del audit B-059, ahora coherentes."""

    @pytest.mark.parametrize("lr", [5, 500, 50, 5000, 50000])
    def test_bundle_and_report_share_bucket(self, lr):
        label = enfsi_label(lr)
        frase_es, frase_en = ENFSI_NARRATIVE[label]
        assert enfsi_narrative(lr, "es") == frase_es
        assert enfsi_narrative(lr, "en") == frase_en

    def test_lr5_no_longer_weak_in_report(self):
        # Pre-fix: bundle "limited" / reporte "provides weak support"
        assert enfsi_label(5) == "limited"
        assert "limited" in enfsi_narrative(5, "en")

    def test_lr500_no_longer_strong_in_report(self):
        # Pre-fix: bundle "moderately strong" / reporte "provides strong support"
        assert enfsi_label(500) == "moderately strong"
        assert "moderately strong" in enfsi_narrative(500, "en")

    def test_every_canonical_label_has_narrative(self):
        for lr in [0, 0.5, 1, 3, 20, 200, 2000, 20000]:
            assert enfsi_label(lr) in ENFSI_NARRATIVE
