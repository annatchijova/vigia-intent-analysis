"""
Test R3-3 — consistencia de etiquetas entre TODAS las carpetas de casos.

Origen: docs/REDTEAM_ROUND3_EMERGENT.md (R3-3). El runner deduplica por stem
tomando el primer directorio de CASES_DIRS; una copia sombra en CUALQUIER
carpeta (converted/, legacy/, consolidated_canonical/, benign/) con
expected_verdict divergente quedaba muerta y podia voltear la metrica en
silencio (shadow de VIGIA-FP-001 en la Ronda 2.1; shadow legacy/ de case_008).

Fix: run_all_agent.check_label_consistency() hace el censo COMPLETO — agrupa
por stem todas las copias en todas las carpetas y reporta divergencias de
expected_verdict; el runner aborta fuerte (fail-loud) si hay alguna.
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
        "etiquetas divergentes entre carpetas de casos: "
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


def test_case_008_legacy_shadow_reconciled():
    """El shadow legacy/ de case_008 (data/cases SUSPICION vs legacy MALICE)
    quedaba fuera del alcance converted-only original; el censo completo lo
    cierra."""
    a = json.load(open("data/cases/case_008_multi_source_fraud_demo.json"))
    b = json.load(open("data/cases/legacy/case_008_multi_source_fraud_demo.json"))
    assert a["expected_verdict"] == b["expected_verdict"] == "SUSPICION"


def test_checker_censuses_all_dirs_not_just_converted(tmp_path):
    """El censo debe detectar una divergencia en CUALQUIER carpeta, no solo
    converted/ — regresion del alcance converted-only."""
    d0 = tmp_path / "cases"
    d_legacy = d0 / "legacy"
    d_legacy.mkdir(parents=True)
    (d0 / "X.json").write_text(json.dumps({"expected_verdict": "MALICE"}))
    (d_legacy / "X.json").write_text(json.dumps({"expected_verdict": "NOISE"}))
    conflicts = runner.check_label_consistency(dirs=[d0, d_legacy])
    conflict = next((c for c in conflicts if c["stem"] == "X"), None)
    assert conflict is not None, "no detecto el shadow en legacy/"
    # el ganador es el primero en el orden de dirs (precedencia del runner)
    assert conflict["winner"].endswith(f"cases{__import__('os').sep}X.json")


def test_checker_ignores_skip_stems(tmp_path):
    """Un no-caso (SKIP_STEMS) duplicado con etiquetas distintas NO es un
    conflicto — el runner nunca lo carga como caso."""
    d0 = tmp_path / "cases"
    d1 = d0 / "converted"
    d1.mkdir(parents=True)
    # 'dataset' esta en SKIP_STEMS
    (d0 / "dataset.json").write_text(json.dumps({"expected_verdict": "MALICE"}))
    (d1 / "dataset.json").write_text(json.dumps({"expected_verdict": "NOISE"}))
    conflicts = runner.check_label_consistency(dirs=[d0, d1])
    assert all(c["stem"] != "dataset" for c in conflicts)
