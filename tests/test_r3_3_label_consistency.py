"""
Test R3-3 — consistencia de etiquetas entre data/cases/ y data/cases/converted/.

Origen: docs/REDTEAM_ROUND3_EMERGENT.md (R3-3). El runner deduplica por stem
tomando el primer directorio de CASES_DIRS; una copia sombra con
expected_verdict divergente quedaba muerta y podia voltear la metrica en
silencio (mismo defecto que el shadow de VIGIA-FP-001 en la Ronda 2.1).

Fix: run_all_agent.check_label_consistency() enumera los stems presentes en
ambas ubicaciones y reporta divergencias de expected_verdict; el runner aborta
fuerte (fail-loud) si hay alguna.
"""

import json

import pytest

import run_all_agent as runner


def test_check_label_consistency_exists():
    assert hasattr(runner, "check_label_consistency"), (
        "run_all_agent debe exponer check_label_consistency()"
    )


def test_real_corpus_has_no_divergent_labels():
    conflicts = runner.check_label_consistency()
    assert conflicts == [], (
        "etiquetas divergentes entre data/cases/ y converted/: "
        + "; ".join(f"{c['stem']}: {c['labels']}" for c in conflicts)
    )


def test_amb_cases_reconciled_to_noise():
    for stem in ("VIGIA-AMB-001", "VIGIA-AMB-002"):
        a = json.load(open(f"data/cases/{stem}.json"))
        b = json.load(open(f"data/cases/converted/{stem}.json"))
        assert a["expected_verdict"] == b["expected_verdict"] == "NOISE", (
            f"{stem}: labels no reconciliadas "
            f"({a['expected_verdict']} vs {b['expected_verdict']})"
        )


def test_checker_detects_a_synthetic_divergence(tmp_path):
    """El checker debe DETECTAR un conflicto, no solo pasar por corpus limpio."""
    base = tmp_path / "cases"
    conv = base / "converted"
    conv.mkdir(parents=True)
    (base / "X.json").write_text(json.dumps({"expected_verdict": "MALICE"}))
    (conv / "X.json").write_text(json.dumps({"expected_verdict": "NOISE"}))
    conflicts = runner.check_label_consistency(base_dir=base, converted_dir=conv)
    assert any(c["stem"] == "X" for c in conflicts)
