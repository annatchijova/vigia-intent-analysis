"""
Tanda C — guard del dataset de calibración a nivel señal (precondición A3/A4).

Verifica (a) la lógica pura del generador y (b) la integridad del artefacto
commiteado `data/signal_calibration_dataset_*.json`:

  · gamma se anota con la función REAL (no una tabla duplicada);
  · el dataset es REAL, no sintético;
  · `dataset_sha256` es reproducible sobre los records;
  · los flags de readiness L-033 (≥20 reales + ambas polaridades) son
    CONSISTENTES con los conteos — sin hard-codear el estado del corpus, que
    puede cambiar cuando entre más evidencia cruda.

No re-corre el build de 203 casos (lento); ejercita helpers + valida el JSON.
"""
from __future__ import annotations

import glob
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "build_signal_calibration_dataset.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_signal_calib", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load_module()


# ── helpers puros ───────────────────────────────────────────────────────────

def test_to_float_handles_all_encodings():
    assert M._to_float(1.5) == 1.5
    assert M._to_float(3) == 3.0
    assert M._to_float("0.25") == 0.25
    assert M._to_float({"__fraction__": True, "num": 361, "den": 400}) == 0.9025
    assert M._to_float(None) is None
    assert M._to_float("no-numérico") is None


def test_gamma_for_matches_real_function():
    from vigia.sift._math_utils import apply_artifact_reliability as g
    # gamma-class: coincide con la función real
    assert M._gamma_for("windows_event_log") == float(g(Fraction(1, 1), "windows_event_log"))
    assert M._gamma_for("event_log") == float(g(Fraction(1, 1), "event_log"))
    # no gamma-class (tipo EBS): None
    assert M._gamma_for("memory_process") is None
    assert M._gamma_for("log_entry") is None


def test_gamma_types_disjoint_from_ebs_types():
    # Los tipos EBS más comunes NO son gamma-class (substratos disjuntos).
    assert "memory_process" not in M.GAMMA_TYPES
    assert "log_entry" not in M.GAMMA_TYPES
    # Los tipos SIFT SÍ.
    assert "windows_event_log" in M.GAMMA_TYPES
    assert "event_log" in M.GAMMA_TYPES


def test_dataset_hash_is_deterministic():
    recs = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    assert M.dataset_sha256(recs) == M.dataset_sha256(list(recs))
    assert M.dataset_sha256(recs) != M.dataset_sha256(recs[:1])


# ── artefacto commiteado ────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def dataset():
    matches = sorted(glob.glob(str(REPO / "data" / "signal_calibration_dataset_*.json")))
    assert matches, "no hay dataset de calibración de señal commiteado"
    return json.loads(Path(matches[-1]).read_text())


def test_schema_and_provenance(dataset):
    for k in ("schema_version", "purpose", "provenance", "coverage",
              "dataset_sha256", "records"):
        assert k in dataset, f"falta clave {k}"
    assert dataset["provenance"]["synthetic"] is False
    assert len(dataset["records"]) > 0


def test_committed_hash_matches_records(dataset):
    assert M.dataset_sha256(dataset["records"]) == dataset["dataset_sha256"]


def test_records_have_ground_truth_and_source(dataset):
    valid_src = {"ebs_scorer", "sift_raw"}
    for r in dataset["records"][:50]:
        assert r["signal_source"] in valid_src
        assert "ground_truth" in r
        assert "evidence_type" in r


def test_sift_records_are_gamma_class_with_annotation(dataset):
    sift = [r for r in dataset["records"] if r["signal_source"] == "sift_raw"]
    for r in sift:
        assert r["is_gamma_class"] is True
        assert r["evidence_type"] in M.GAMMA_TYPES
        assert r["gamma_static"] is not None
        # z_post_gamma == z * gamma cuando ambos existen
        if r["z_score"] is not None:
            assert abs(r["z_post_gamma"] - r["z_score"] * r["gamma_static"]) < 1e-9


def test_readiness_flags_consistent_with_counts(dataset):
    """Los flags L-033 deben derivarse de los conteos, no hard-codearse."""
    cov = dataset["coverage"]
    for part, flag_key, ready_field in (
        ("ebs_scorer", "L033_ready_for_A4_profiles", "A4"),
        ("sift_raw", "L033_ready_for_A3_gamma", "A3"),
    ):
        p = cov[part]
        expected = (p["n_labeled"] >= 20
                    and p["polarity"]["inculpatory"] >= 1
                    and p["polarity"]["benign"] >= 1)
        assert p[flag_key] == expected, (
            f"{ready_field}: flag {p[flag_key]} incoherente con "
            f"n_labeled={p['n_labeled']} polarity={p['polarity']}"
        )
