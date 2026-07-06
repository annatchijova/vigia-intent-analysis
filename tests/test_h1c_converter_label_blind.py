"""
H1c / TANDA 4 (2026-07-06) — Puerta de datos: el conversor de casos legacy
ya no puede moldear scores con la etiqueta, y el corpus convertido quedó
regenerado sin la reducción persistida.

Pre-fix: convert_case() leía expected_verdict y, para NOISE/BENIGN, escribía
A DISCO raw_score×0.25 + prior_trust=0.3 (data/cases/converted/VIGIA-BEN-*).
La fuga sobrevivía a todos los fixes runtime (B-075, fix P1) porque vivía en
los datos: el run "ciego" acertaba los 15 BEN porque el conversor conocía la
respuesta. Medido en AUDITORIA_FUGA_INDIRECTA (Addendum 1-2).
"""

import copy
import glob
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from convert_legacy_cases import convert_case  # noqa: E402

_BASE_CASE = {
    "case_id": "SYNTH-T4",
    "artifacts": [
        {"artifact_id": "A1", "type": "bash_history", "peirce_layer": "FIRSTNESS",
         "content": "x", "forensic_anomalies": ["a", "b"]},
        {"artifact_id": "A2", "type": "auth_log", "peirce_layer": "SECONDNESS",
         "content": "y"},
        {"artifact_id": "A3", "type": "file_metadata", "peirce_layer": "THIRDNESS",
         "content": "z"},
    ],
}


def _scores(case_out):
    return [(a["raw_score"], a["prior_trust"]) for a in case_out["artifacts"]]


class TestConverterLabelBlind:
    @pytest.mark.parametrize("verdict", ["MALICE", "INTENT", "SUSPICION",
                                         "UNKNOWN", "NOISE", "BENIGN", "ABSTAIN"])
    def test_default_conversion_ignores_label(self, verdict):
        """Label-flip a nivel conversor: los 7 veredictos → scores idénticos."""
        c = copy.deepcopy(_BASE_CASE)
        c["expected_verdict"] = verdict
        base = copy.deepcopy(_BASE_CASE)
        base["expected_verdict"] = "MALICE"
        assert _scores(convert_case(c)) == _scores(convert_case(base))

    def test_no_reduction_fingerprint_by_default(self):
        c = copy.deepcopy(_BASE_CASE)
        c["expected_verdict"] = "NOISE"
        out = convert_case(c)
        for raw, pt in _scores(out):
            assert pt != 0.3, "huella de reducción benigna en conversión default"
            assert raw >= 0.6, f"score reducido ({raw}) en conversión default"

    def test_optin_flag_reproduces_historical_corpus(self):
        """Pin del comportamiento histórico bajo el opt-in explícito."""
        c = copy.deepcopy(_BASE_CASE)
        c["expected_verdict"] = "NOISE"
        out = convert_case(c, legacy_benign_reduction=True)
        clean = convert_case(copy.deepcopy(c))
        for (raw_r, pt_r), (raw_c, _) in zip(_scores(out), _scores(clean)):
            assert raw_r == round(raw_c * 0.25, 4)
            assert pt_r == 0.3

    def test_optin_flag_inert_for_malicious(self):
        c = copy.deepcopy(_BASE_CASE)
        c["expected_verdict"] = "MALICE"
        assert _scores(convert_case(c, legacy_benign_reduction=True)) == \
            _scores(convert_case(copy.deepcopy(c)))


class TestCorpusRegenerated:
    """Los 15 archivos del corpus ya no portan la reducción persistida."""

    def test_no_ben_file_carries_reduction_fingerprint(self):
        files = sorted(glob.glob(str(REPO / "data/cases/converted/VIGIA-BEN-*.json")))
        assert len(files) == 15
        for f in files:
            case = json.loads(Path(f).read_text(encoding="utf-8"))
            for a in case["artifacts"]:
                assert a["prior_trust"] != 0.3, f"{Path(f).name}: prior_trust=0.3 (huella)"
                assert a["raw_score"] >= 0.6, f"{Path(f).name}: raw_score={a['raw_score']} (reducido)"

    def test_derived_signals_consistent_with_clean_artifacts(self):
        """El campo `signals` (metadata derivada, inerte para scoring) quedó
        recomputado con la fórmula del adaptador: z = raw × prior."""
        from fractions import Fraction
        for f in sorted(glob.glob(str(REPO / "data/cases/converted/VIGIA-BEN-*.json"))):
            case = json.loads(Path(f).read_text(encoding="utf-8"))
            if not isinstance(case.get("signals"), list):
                continue
            by_id = {a["artifact_id"]: a for a in case["artifacts"]}
            for s in case["signals"]:
                a = by_id.get(s.get("artifact_id"))
                if a is None:
                    continue
                z = s["z_score"]
                expected = Fraction(str(a["raw_score"])) * Fraction(str(a["prior_trust"]))
                assert Fraction(z["num"], z["den"]) == expected, (
                    f"{Path(f).name}/{s['artifact_id']}: signals desincronizado "
                    f"de los artifacts limpios"
                )

    def test_regenerated_ben_scores_honestly(self):
        """El scoring ciego del corpus regenerado muestra los FPs reales del
        motor (Addendum 2/4): ya no hay NOISE fabricado por la etiqueta."""
        from vigia_scorer import _vigia_score, _normalize_case

        case = json.loads((REPO / "data/cases/converted/VIGIA-BEN-001.json")
                          .read_text(encoding="utf-8"))
        blind = {k: v for k, v in case.items() if k != "expected_verdict"}
        r = _vigia_score(_normalize_case(copy.deepcopy(blind)))
        assert r["verdict"] in ("SUSPICION", "MALICE"), (
            "BEN-001 regenerado volvió a NOISE — ¿reducción reintroducida?"
        )
