"""
Validador schema-aware (WHAT_IS_NEXT §1.1.2, sesión 2026-07-07).

Firstness: el corpus tiene DOS schemas de artefacto legítimos —
  EBS-señales (raw_score/evidence_type/metadata → CAIE ingiere el número) y
  narrativo/semiótico (content/peirce_layer/forensic_anomalies → vía de texto).
Secondness: validate_case.py solo conocía el shape EBS: reportaba 6 errores
  espurios por artefacto narrativo, más "raw_score=-1 fuera de rango" (el
  DEFAULT del propio validador aplicado a artefactos sin raw_score — los 41
  errores del audit AUDITORIA_MOTOR_SIN_LABEL §1 son autogenerados).
Thirdness: un validador que exige el schema equivocado convierte "schema
  distinto" en "caso defectuoso" y el 145/199 FAIL del titular mezclaba
  defectos reales con falsos positivos del validador.

Tests escritos ROJOS contra el validador previo. Se invoca por subprocess
porque validate_case.py acumula en globals module-level.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _run_validator(case: dict, tmp_path: Path) -> tuple[int, str]:
    p = tmp_path / "case.json"
    p.write_text(json.dumps(case, ensure_ascii=False))
    r = subprocess.run(
        [sys.executable, str(REPO / "validate_case.py"), str(p)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    return r.returncode, r.stdout + r.stderr


def _narrative_case() -> dict:
    return {
        "case_id": "TEST-NARR-001",
        "case_name": "narrativo puro",
        "description": "caso con artefactos semióticos",
        "expected_verdict": "NOISE",
        "schema_version": 1,
        "artifacts": [
            {
                "artifact_id": "ART-001",
                "type": "registry_analysis",
                "content": "HKLM\\...\\RegisteredOwner = Greg Schardt",
                "forensic_anomalies": ["alias de atacante"],
                "peirce_layer": "SECONDNESS",
            }
        ],
    }


def _ebs_case(with_acq: bool = True) -> dict:
    meta = {"note": "señal sintética"}
    if with_acq:
        meta.update({
            "acquisition_tool": "vigia converter",
            "acquisition_hash": "sha256:" + "0" * 64,
            "acquisition_timestamp": "2026-07-07T00:00:00Z",
        })
    return {
        "case_id": "TEST-EBS-001",
        "case_name": "ebs puro",
        "description": "caso con señales EBS",
        "expected_verdict": "NOISE",
        "schema_version": 1,
        "artifacts": [
            {
                "artifact_id": "ART-001",
                "evidence_type": "log_entry",
                "source_tool": "test",
                "description": "señal",
                "raw_score": 0.2,
                "prior_trust": 0.7,
                "timestamp": "2026-07-07T00:00:00Z",
                "provenance_chain": ["gen"],
                "metadata": meta,
            }
        ],
    }


class TestNarrativeSchemaAccepted:
    def test_pure_narrative_case_passes(self, tmp_path):
        rc, out = _run_validator(_narrative_case(), tmp_path)
        assert rc == 0, f"caso narrativo válido rechazado:\n{out}"

    def test_narrative_artifact_gets_no_raw_score_error(self, tmp_path):
        rc, out = _run_validator(_narrative_case(), tmp_path)
        assert "raw_score" not in out, (
            "el validador aplicó el default raw_score=-1 a un artefacto "
            f"narrativo (la clase de los 41 errores espurios del audit):\n{out}"
        )

    def test_narrative_artifact_gets_no_acq_error(self, tmp_path):
        rc, out = _run_validator(_narrative_case(), tmp_path)
        assert "acquisition" not in out, (
            f"metadata de adquisición exigida a un artefacto narrativo:\n{out}"
        )

    def test_narrative_with_source_tool_still_narrative(self, tmp_path):
        # Los SRL-MEMORY reales: narrativo + source_tool. El discriminador es
        # raw_score (la señal numérica), no la presencia de source_tool.
        case = _narrative_case()
        case["artifacts"][0]["source_tool"] = "volatility3"
        case["artifacts"][0]["examiner_id"] = "EX-1"
        rc, out = _run_validator(case, tmp_path)
        assert rc == 0, f"narrativo con source_tool rechazado:\n{out}"


class TestEbsContractUnchanged:
    def test_ebs_with_acq_passes(self, tmp_path):
        rc, out = _run_validator(_ebs_case(with_acq=True), tmp_path)
        assert rc == 0, f"caso EBS completo rechazado:\n{out}"

    def test_ebs_missing_acq_still_fails(self, tmp_path):
        rc, out = _run_validator(_ebs_case(with_acq=False), tmp_path)
        assert rc != 0, "EBS sin metadata de adquisición debe seguir fallando"
        assert "acquisition" in out

    def test_ebs_raw_score_out_of_range_still_fails(self, tmp_path):
        case = _ebs_case()
        case["artifacts"][0]["raw_score"] = -1
        rc, out = _run_validator(case, tmp_path)
        assert rc != 0 and "raw_score" in out

    def test_root_fields_still_required(self, tmp_path):
        case = _narrative_case()
        del case["schema_version"]
        rc, out = _run_validator(case, tmp_path)
        assert rc != 0 and "schema_version" in out


class TestNarrativeMinimalContract:
    def test_narrative_without_artifact_id_fails(self, tmp_path):
        case = _narrative_case()
        del case["artifacts"][0]["artifact_id"]
        rc, out = _run_validator(case, tmp_path)
        assert rc != 0, "artefacto narrativo sin artifact_id debe fallar"

    def test_narrative_without_content_fails(self, tmp_path):
        case = _narrative_case()
        del case["artifacts"][0]["content"]
        del case["artifacts"][0]["forensic_anomalies"]
        rc, out = _run_validator(case, tmp_path)
        assert rc != 0, (
            "artefacto sin señal EBS ni contenido narrativo debe fallar"
        )
