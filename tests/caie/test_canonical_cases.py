"""
Test runner for VIGIA Canonical Cases (VIGIA-CAN-*.json).
Runs ONLY the 52 consolidated canonical cases against CAIE.
Does NOT touch synthetic or legacy cases.
"""

import json
import glob
import pytest
from pathlib import Path

# Import CAIE
from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact

CASES_DIR = Path("data/cases/consolidated_canonical")

# Known-pending canonical cases (post M1/M2, 2026-07-12).
# These verdicts at the CAIE-tool layer were previously sustained by fossil
# TCV fractures fired from free-text substring matching and B-115-broken
# metadata timestamps (metadata.*_time authored ~90 days off the coherent
# top-level timeline — see docs/FOSSIL_HUNT_20260711_PASS2.md section 3), or
# by the FALSE_FLAG_PATTERN catch-all on mis-typed artifacts (subgroup C,
# docs/D5_RETIPADO_SUBGRUPO_C_20260712.md). Each entry is xfail with its
# pending remediation; when the underlying data is repaired (B-115 decision
# D-2) or the case is re-scored (raw-inversion session), the case flips to
# XPASS and must be removed from this map.
_B115 = ("CAIE-layer verdict was sustained by fossil TCV on B-115-broken "
         "metadata timestamps; pending data repair decision D-2")
# Re-scoring session outcome (2026-07-12, docs/RESCORING_SESSION_SCOPE_20260712.md):
# case_090 and case_026 were retyped+re-scored per the rubric and now seal
# MALICE at the MOTOR layer on clean composite (0.4359 / 0.4233, zero
# fractures). They still read NOISE at the CAIE-TOOL layer (composite ~0.095
# vs the 0.5/0.2 Noisy-OR thresholds) — that residue is the D-G mode
# divergence (fusion scale, not data): see
# docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-G. case_024 was resolved as
# honest SUSPICION (no re-score; CAN-026 criterion applies, expected_verdict
# relabel decision pending).
_MODE_DIVERGENCE = ("data repaired (retype+rubric 2026-07-12): motor seals "
                    "MALICE on clean composite; CAIE-tool layer still NOISE "
                    "because its 0.5/0.2 Noisy-OR thresholds are structurally "
                    "unreachable on the adjusted scale — pending D-G mode "
                    "unification, not a data fix")
KNOWN_PENDING = {
    # case_004_incompetencia_armamentizada and case_012_camuflaje_simbiotico
    # were removed from this list on 2026-07-12: the new canonical TTP
    # detectors (DEFENSE_EVASION_ARTIFACT / PROCESS_INJECTION_ANTIFORENSIC,
    # docs/CASE_RECOVERY_20260712.md) now fire on their real attack signal, so
    # they seal MALICE at the motor layer and SUSPICION at the CAIE-tool layer
    # (both accepted for MALICE-expected). They pass; they must NOT be xfail.
    #
    # case_111_falso_rastro_incompetencia and case_024_paracaidista were
    # removed on 2026-07-17: both seal SUSPICION at the CAIE-tool layer today,
    # which the MALICE-expected acceptance already admits. They had been
    # invisible passes: the old imperative `pytest.xfail(...)` aborted the
    # test BEFORE running the engine, so no entry in this map could ever
    # reach XPASS (see the marker-based parametrization below, which fixed
    # the mechanism).
    **{cid: _B115 for cid in (
        "case_005_ruido_blanco_distractor",
        "case_007_insomnio_tactico",
        "case_008_paranoia_perimetro",
        "case_009_vacio_quirurgico",
        "case_010_falso_positivo_empatico",
        "case_016_auto_gaslighting_sistema",
        "case_020_mimetismo_topografico",
        "case_083_sacrificio_del_peon",
        "case_084_cebo_falso_layman",
        "case_085_mise_en_place_alterada",
        "case_087_estocolmo_inverso",
        "case_089_huella_perfeccion",
        "case_091_disonancia_motivo_noble",
        "case_092_verdad_por_saturacion",
        "case_096_entropia_panico",
        "case_097_falsa_misericordia",
        "case_098_anacronismo_plataforma",
        "case_099_troyano_emocional",
        "case_100_fantasma_maquina",
        "case_101_denunciante_humo",
        "case_103_cebo_vulnerabilidad_autoinfligida",
        "case_105_disonancia_ritmo_procesamiento",
        "case_109_silencio_estadistico_log",
    )},
    "case_090_anacronismo_herramienta": _MODE_DIVERGENCE,
    "case_026_ventrilocuo": _MODE_DIVERGENCE,
}


def canonical_case_params():
    """One pytest.param per case, with KNOWN_PENDING as a real xfail MARKER.

    The previous mechanism called `pytest.xfail(reason)` imperatively inside
    the test body, which aborts the test immediately: pending cases never
    executed, so a repaired case could never surface as XPASS and stale
    entries accumulated silently (case_111 and case_024 were passing
    unnoticed). strict=True enforces the documented contract: the moment a
    pending case passes (e.g. after the D-2 data repair), the suite fails
    until its entry is removed from KNOWN_PENDING.
    """
    for case in load_canonical_cases():
        marks = []
        if case["case_id"] in KNOWN_PENDING:
            marks.append(
                pytest.mark.xfail(reason=KNOWN_PENDING[case["case_id"]], strict=True)
            )
        yield pytest.param(case, id=case["case_id"], marks=marks)

def load_canonical_cases():
    """Load all VIGIA-CAN-*.json files."""
    pattern = CASES_DIR / "VIGIA-CAN-*.json"
    files = sorted(glob.glob(str(pattern)))
    cases = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            case = json.load(fh)
        case["_source_file"] = Path(f).name
        cases.append(case)
    return cases


def case_to_artifacts(case: dict) -> list[Artifact]:
    """Convert case artifacts to CAIE Artifact objects."""
    artifacts = []
    for art in case.get("artifacts", []):
        try:
            a = Artifact(
                source_tool=art["source_tool"],
                evidence_type=art["evidence_type"],
                raw_score=float(art["raw_score"]),
                description=art["description"],
                metadata=art.get("metadata", {}),
                provenance_chain=art.get("provenance_chain", []),
                base_trust=float(art.get("prior_trust", 1.0)),
            )
            artifacts.append(a)
        except Exception as e:
            print(f"[WARN] Failed to parse artifact {art.get('artifact_id')}: {e}")
    return artifacts


class TestCanonicalCases:
    """Pytest class for canonical case validation."""

    @pytest.fixture(scope="class")
    def canonical_cases(self):
        return load_canonical_cases()

    def test_all_cases_load(self, canonical_cases):
        """Verify all canonical cases load without errors."""
        assert len(canonical_cases) == 52, f"Expected 52 cases, got {len(canonical_cases)}"
        for case in canonical_cases:
            assert "case_id" in case
            assert "artifacts" in case
            assert len(case["artifacts"]) > 0

    @pytest.mark.parametrize("case", canonical_case_params())
    def test_case_caie_verdict(self, case):
        """Run each case through CAIE and compare with expected_verdict."""
        engine = CrossArtifactIncongruenceEngine()
        artifacts = case_to_artifacts(case)

        for a in artifacts:
            engine.add_artifact(a)

        result = engine.evaluate()
        actual = result.get("verdict", "UNKNOWN")
        expected = case.get("expected_verdict", "UNKNOWN")

        # Log details for debugging
        print(f"\n[{case['case_id']}] expected={expected} actual={actual}")
        print(f"  composite={result.get('composite_score')}")
        print(f"  fractures={result.get('fractures_detected')}")
        print(f"  golden_rules={result.get('golden_rules_triggered')}")

        # For MALICE cases, we expect MALICE or SUSPICION (CAIE might downgrade)
        if expected == "MALICE":
            assert actual in ("MALICE", "SUSPICION"),                 f"{case['case_id']}: expected MALICE/SUSPICION, got {actual}"
        elif expected == "SUSPICION":
            assert actual in ("SUSPICION", "MALICE"),                 f"{case['case_id']}: expected SUSPICION/MALICE, got {actual}"
        else:
            assert actual == expected,                 f"{case['case_id']}: expected {expected}, got {actual}"


if __name__ == "__main__":
    # Manual run without pytest
    cases = load_canonical_cases()
    print(f"[RUNNER] Loaded {len(cases)} canonical cases")

    passed = 0
    failed = 0

    for case in cases:
        engine = CrossArtifactIncongruenceEngine()
        artifacts = case_to_artifacts(case)
        for a in artifacts:
            engine.add_artifact(a)

        result = engine.evaluate()
        actual = result.get("verdict", "UNKNOWN")
        expected = case.get("expected_verdict", "UNKNOWN")

        ok = (expected == "MALICE" and actual in ("MALICE", "SUSPICION")) or              (expected == "SUSPICION" and actual in ("SUSPICION", "MALICE")) or              (actual == expected)

        status = "PASS" if ok else "FAIL"
        # composite_score is serialized as a string in current CAIE output;
        # print it verbatim instead of assuming a float (crashed with ':.4f').
        print(f"[{status}] {case['case_id']}: expected={expected} actual={actual} "
              f"composite={result.get('composite_score', 0)} "
              f"fractures={result.get('fractures_detected', 0)}")

        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n[SUMMARY] Passed: {passed}/{len(cases)} | Failed: {failed}/{len(cases)}")
    exit(0 if failed == 0 else 1)
