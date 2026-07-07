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


# ---------------------------------------------------------------------------
# R3-3b — cobertura TOTAL: el guard original solo comparaba data/cases/ contra
# converted/, pero el censo completo (2026-07-07) encontró la divergencia viva
# en legacy/: case_008_multi_source_fraud_demo SUSPICION (canónica, relabel
# doctrinal documentado en _notes) vs MALICE (legacy, nunca recibió el
# relabel). Tests escritos ROJOS contra el corpus y el guard previos.
# ---------------------------------------------------------------------------


def test_checker_covers_all_cases_dirs(tmp_path):
    """El guard debe detectar divergencias en CUALQUIER par de CASES_DIRS."""
    base = tmp_path / "cases"
    legacy = base / "legacy"
    legacy.mkdir(parents=True)
    (base / "Y.json").write_text(json.dumps({"expected_verdict": "SUSPICION"}))
    (legacy / "Y.json").write_text(json.dumps({"expected_verdict": "MALICE"}))
    conflicts = runner.check_label_consistency(
        dirs=[base, base / "converted", legacy]
    )
    assert any(c["stem"] == "Y" for c in conflicts), (
        "divergencia en legacy/ no detectada — el guard no cubre todos los dirs"
    )


def test_real_corpus_no_divergence_in_any_dir():
    """Censo total sobre las CASES_DIRS reales del runner."""
    conflicts = runner.check_label_consistency(dirs=runner.CASES_DIRS)
    assert conflicts == [], (
        "etiquetas divergentes en el corpus: "
        + "; ".join(f"{c['stem']}: {c['labels']}" for c in conflicts)
    )


def test_case_008_relabel_applied_to_both_copies():
    """La lección de la Ronda 2.1: el relabel debe llegar a TODAS las copias."""
    a = json.load(open("data/cases/case_008_multi_source_fraud_demo.json"))
    b = json.load(open("data/cases/legacy/case_008_multi_source_fraud_demo.json"))
    assert a["expected_verdict"] == b["expected_verdict"] == "SUSPICION", (
        f"case_008 divergente: {a['expected_verdict']} vs {b['expected_verdict']} "
        "(el relabel MALICE→SUSPICION de cdeb32f no llegó a la copia legacy)"
    )


# ---------------------------------------------------------------------------
# R3-3c — dedup física (censo clasificado 2026-07-07). De 70 copias sombra:
# 36 con schema distinto (fuente vs derivado: benign/ y legacy/ alimentan los
# conversores) y 13 variantes de contenido se CONSERVAN — comparten stem
# legítimamente y el guard de etiquetas las vigila. Las 20 byte-idénticas son
# copias muertas sin consumidor (censo de consumidores en el commit) y se
# retiran. El bundle malformado VIGIA_BREAK_001-010 (lista JSON pre-migración
# de 10 casos que ya existen individualmente en converted/) double-contaba y
# auto-pasaba como UNKNOWN: se excluye vía SKIP_STEMS, el archivo se conserva
# como historia. Tests escritos ROJOS contra el corpus previo.
# ---------------------------------------------------------------------------


def _corpus_stem_map():
    """stem -> [paths], honrando la misma vista de no-casos que find_cases."""
    by_stem = {}
    for d in runner.CASES_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if runner._is_skipped(f.stem):
                continue
            by_stem.setdefault(f.stem, []).append(f)
    return by_stem


def test_skip_stems_is_prefix_match_not_substring():
    """R3-3c: el matching por substring se tragaba
    VIGIA_BREAK_005_FALSE_CORRELATION (contiene "correlation") — un caso real
    excluido en silencio del corpus desde su creación."""
    assert not runner._is_skipped("VIGIA_BREAK_005_FALSE_CORRELATION")
    assert runner._is_skipped("VIGIA_BREAK_001-010")
    assert runner._is_skipped("dataset_test_cases")
    assert runner._is_skipped("vigia_cases_canonical_v2")
    assert runner._is_skipped("vigia_input_defcon_nist")
    stems = {c.stem for c in runner.find_cases(runner.CASES_DIRS)}
    assert "VIGIA_BREAK_005_FALSE_CORRELATION" in stems


def test_no_byte_identical_dead_copies():
    """Una copia byte-idéntica de un stem ya ganador es ground truth muerto:
    editarla es un no-op silencioso. Post-R3-3c no debe quedar ninguna."""
    dead = []
    for stem, paths in _corpus_stem_map().items():
        if len(paths) < 2:
            continue
        try:
            winner = json.loads(paths[0].read_text())
        except Exception:
            continue
        for shadow in paths[1:]:
            try:
                if json.loads(shadow.read_text()) == winner:
                    dead.append(str(shadow))
            except Exception:
                continue
    assert dead == [], f"copias muertas byte-idénticas: {dead}"


def test_malformed_break_bundle_excluded_from_corpus():
    """El bundle pre-migración VIGIA_BREAK_001-010 (lista JSON) double-contaba
    sus 10 casos —que existen individualmente— y auto-pasaba como UNKNOWN."""
    cases = runner.find_cases(runner.CASES_DIRS)
    stems = {c.stem for c in cases}
    assert "VIGIA_BREAK_001-010" not in stems, (
        "el bundle malformado sigue entrando al corpus como caso auto-pass"
    )
    # Los 10 casos individuales (canónicos, migrados) sí están.
    for i, suffix in enumerate([
        "001_SILENT_INCONSISTENCY", "002_VALID_BENIGN",
        "003_CULTURAL_TRUE_POSITIVE", "004_SIGNAL_DROWNING",
        "005_FALSE_CORRELATION", "006_PERFECT_ATTACK", "007_MISSING_LOGS",
        "008_AMBIGUOUS", "009_PROMPT_POISON", "010_OVERPERFECT",
    ], start=1):
        assert f"VIGIA_BREAK_{suffix}" in stems, f"falta el caso individual {suffix}"
