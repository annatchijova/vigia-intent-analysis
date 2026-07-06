"""
Fix P1 — AUDITORIA_FUGA_INDIRECTA (2026-07-06): fuga de etiqueta en
normalize_case_schema (familia B-075, puerta runtime).

El bloque is_benign leía `expected_verdict` (ground truth) y, para casos
legacy benignos, reducía raw_score ×0.25 y fijaba prior_trust=0.3 — el input
del scoring quedaba moldeado por la respuesta esperada. Medido pre-fix:
15/15 casos VIGIA-BEN-* cambiaban de veredicto según la etiqueta estuviera
presente (NOISE con etiqueta ↔ SUSPICION/MALICE sin ella).

Contrato post-fix:
  1. normalize_case_schema es ciega a expected_verdict por default
     (label-flip no cambia ni un artefacto).
  2. _vigia_score produce el mismo veredicto/score con y sin etiqueta.
  3. La reducción histórica solo existe tras opt-in explícito
     (legacy_benign_reduction=True) — pin de reproducción de bundles viejos.
"""

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia.pipeline.vigia_integration_bridge import normalize_case_schema  # noqa: E402


def _legacy_benign_case() -> dict:
    """Caso 100% legacy (sin evidence_type) con etiqueta benigna y sin MITRE —
    la combinación exacta que disparaba la reducción."""
    return {
        "case_id": "TEST-LEAK-001",
        "expected_verdict": "NOISE",
        "expected_mitre_ttps": [],
        "artifacts": [
            {"artifact_id": "A1", "type": "bash_history", "peirce_layer": "FIRSTNESS",
             "content": "comando inocuo"},
            {"artifact_id": "A2", "type": "auth_log", "peirce_layer": "SECONDNESS",
             "content": "login normal"},
            {"artifact_id": "A3", "type": "file_metadata", "peirce_layer": "THIRDNESS",
             "content": "ticket verificable"},
        ],
    }


def _strip_label(case: dict) -> dict:
    return {k: v for k, v in case.items() if k != "expected_verdict"}


def _score_fields(case_out: dict) -> list:
    return [(a.get("raw_score"), a.get("prior_trust")) for a in case_out["artifacts"]]


class TestLabelBlindNormalization:
    def test_label_flip_does_not_change_artifacts(self):
        """Contrato 1: mismo caso con y sin etiqueta → artefactos idénticos."""
        labeled = normalize_case_schema(copy.deepcopy(_legacy_benign_case()))
        blind = normalize_case_schema(copy.deepcopy(_strip_label(_legacy_benign_case())))
        assert _score_fields(labeled) == _score_fields(blind), (
            "normalize_case_schema modificó raw_score/prior_trust según la "
            "etiqueta — fuga de etiqueta reintroducida (fix P1 roto)"
        )

    def test_verdict_label_does_not_reduce_scores(self):
        """La combinación benigna exacta (NOISE + MITRE vacío) ya no reduce."""
        out = normalize_case_schema(copy.deepcopy(_legacy_benign_case()))
        for art in out["artifacts"]:
            assert art["prior_trust"] != 0.3 or art["raw_score"] > 0.25, (
                f"{art['artifact_id']}: huella de reducción benigna "
                f"(raw_score={art['raw_score']}, prior_trust={art['prior_trust']})"
            )

    @pytest.mark.parametrize("verdict", ["NOISE", "BENIGN", "ABSTAIN", "MALICE", "SUSPICION"])
    def test_all_labels_produce_identical_normalization(self, verdict):
        """Ninguna etiqueta (benigna o no) altera la normalización."""
        base = _legacy_benign_case()
        case = copy.deepcopy(base)
        case["expected_verdict"] = verdict
        out = normalize_case_schema(case)
        blind = normalize_case_schema(copy.deepcopy(_strip_label(base)))
        assert _score_fields(out) == _score_fields(blind)

    def test_label_flip_does_not_change_vigia_score(self):
        """Contrato 2: el veredicto sellado del scorer es invariante a la etiqueta."""
        from vigia_scorer import _vigia_score, _normalize_case

        labeled = _vigia_score(_normalize_case(copy.deepcopy(_legacy_benign_case())))
        blind = _vigia_score(_normalize_case(copy.deepcopy(_strip_label(_legacy_benign_case()))))
        assert labeled["verdict"] == blind["verdict"]
        assert labeled["score"] == blind["score"]

    def test_ben_corpus_case_label_invariant(self):
        """Regresión sobre el corpus real: BEN-001 (el caso medido en la auditoría)."""
        import json

        path = REPO / "data/cases/benign/VIGIA-BEN-001.json"
        if not path.exists():
            pytest.skip("corpus BEN no presente")
        from vigia_scorer import _vigia_score, _normalize_case

        case = json.loads(path.read_text(encoding="utf-8"))
        labeled = _vigia_score(_normalize_case(copy.deepcopy(case)))
        blind = _vigia_score(_normalize_case(copy.deepcopy(_strip_label(case))))
        assert labeled["verdict"] == blind["verdict"], (
            "VIGIA-BEN-001 sigue flipeando de veredicto con la etiqueta "
            "(pre-fix: NOISE con etiqueta / SUSPICION sin ella)"
        )
        assert labeled["score"] == blind["score"]


class TestLegacyReproductionPin:
    def test_explicit_flag_reproduces_historical_reduction(self):
        """Contrato 3 (pin histórico): el opt-in explícito reproduce el
        comportamiento pre-fix exacto (×0.25, redondeo a 4, prior_trust=0.3)."""
        base = normalize_case_schema(copy.deepcopy(_legacy_benign_case()))
        reduced = normalize_case_schema(
            copy.deepcopy(_legacy_benign_case()), legacy_benign_reduction=True
        )
        for art_base, art_red in zip(base["artifacts"], reduced["artifacts"]):
            assert art_red["raw_score"] == round(art_base["raw_score"] * 0.25, 4)
            assert art_red["prior_trust"] == 0.3

    def test_flag_is_inert_for_nonbenign_labels(self):
        """El opt-in no toca casos con etiqueta no benigna (asimetría intacta)."""
        case = copy.deepcopy(_legacy_benign_case())
        case["expected_verdict"] = "MALICE"
        out_flag = normalize_case_schema(copy.deepcopy(case), legacy_benign_reduction=True)
        out_base = normalize_case_schema(copy.deepcopy(case))
        assert _score_fields(out_flag) == _score_fields(out_base)

    def test_flag_is_inert_for_canonical_schema(self):
        """La rama canónica retorna antes del bloque: el flag no la afecta."""
        case = {
            "case_id": "TEST-CANON-001",
            "expected_verdict": "NOISE",
            "expected_mitre_ttps": [],
            "artifacts": [
                {"artifact_id": "A1", "evidence_type": "log_entry",
                 "raw_score": 0.8, "prior_trust": 0.85,
                 "provenance_chain": ["sha256:x"]},
            ],
        }
        out = normalize_case_schema(copy.deepcopy(case), legacy_benign_reduction=True)
        assert out["artifacts"][0]["raw_score"] == 0.8
        assert out["artifacts"][0]["prior_trust"] == 0.85
