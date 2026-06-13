"""
tests/test_audit_false_flag.py
==============================
Red-team audit — Hallazgo H-02: FALSE_FLAG_PATTERN y falsa atribución.

ACTUALIZACIÓN post-run 2026-06-10:
    test_clean_foreign_machine_is_not_malice dio XPASS pero por el motivo
    EQUIVOCADO: los fixtures sin metadatos de adquisición (acquisition_tool,
    acquisition_hash, etc.) activaron las penalizaciones NIST SP 800-86 §4.3,
    degradando base_trust hasta el piso. Con trust destrozado, el score no
    llegó a 0.33 aunque la fractura se generó.

    test_clean_foreign_machine_does_not_trigger_false_flag_rule sigue XFAIL:
    FALSE_FLAG_PATTERN SÍ está en los fractures del engine. La regla está rota.

    Si corremos los casos reales (que sí tienen metadata completa), el trust
    no se degrada y la fractura + boost (0.82 * 0.45 = 0.369) lleva a MALICE.

    SOLUCIÓN: fixtures con acquisition_metadata mínima y válida.
    El test ahora prueba la REGLA, no el sistema de penalización de custodia.

CONTEXTO:
    Falsa atribución ES malicia. La malicia es del que PLANTA, no del idioma.
    Un usuario ruso con la máquina limpia no es un false flag.

    La regla actual dispara: avg_cultural > 0.5 AND avg_technical < 0.2
    Lo correcto:
      - sin ataque real + cultural → NOISE/UNKNOWN (nunca MALICE)
      - ataque real + manipulación positiva → FALSE_FLAG_PATTERN → MALICE
"""
from __future__ import annotations

import pytest

caie = pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie no importable (correr con PYTHONPATH=$(pwd))",
)
CrossArtifactIncongruenceEngine = caie.CrossArtifactIncongruenceEngine
Artifact = caie.Artifact

# ---------------------------------------------------------------------------
# Metadata de adquisición mínima — fixtures honestos
# Sin esto el sistema NIST SP 800-86 degrada base_trust y enmascara el bug.
# ---------------------------------------------------------------------------

_ACQ_META = {
    "acquisition_tool": "FTK Imager 4.7",
    "acquisition_hash": "sha256:" + "a" * 64,
    "acquisition_timestamp": "2026-04-10T08:00:00Z",
    "examiner_id": "EXA-TEST-001",
    "write_blocker_used": True,
}


def _engine_with(artifacts: list[Artifact]) -> CrossArtifactIncongruenceEngine:
    engine = CrossArtifactIncongruenceEngine()
    for a in artifacts:
        engine.add_artifact(a)
    return engine


def _fracture_types(engine: CrossArtifactIncongruenceEngine) -> set[str]:
    return {f.fracture_type for f in engine.detect_fractures()}


# ---------------------------------------------------------------------------
# Fixture: máquina rusa limpia, sin incidente, metadata completa
# ---------------------------------------------------------------------------

def _clean_russian_machine() -> list[Artifact]:
    meta = dict(_ACQ_META)
    return [
        Artifact(
            source_tool="infer_intent",
            evidence_type="cultural_marker",
            raw_score=0.85,
            description=(
                "Cyrillic filenames ('отчет_финансы.docx'), keyboard layout RU, "
                "timezone UTC+3. Native configuration. Normal creation dates."
            ),
            metadata={
                **meta,
                "cyrillic_filenames": 3,
                "keyboard_layout_detected": "RU",
                "timezone_offset": "+03:00",
                "language_confidence": 0.91,
                "organic_user_files": True,
                "normal_creation_dates": True,
                "timestomp_detected": False,
                "backdating_detected": False,
                "mft_inconsistency": False,
                "suspiciously_obvious": False,
                "concentrated_in_single_file": False,
            },
            provenance_chain=["sha256:" + "c" * 64],
            base_trust=0.3,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="memory_process",
            raw_score=0.05,
            description="Memory: no injection, no kernel anomalies, clean state.",
            metadata={**meta, "injections_detected": 0, "kernel_anomalies": 0},
            provenance_chain=["sha256:" + "m" * 64],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="lsass_session",
            raw_score=0.08,
            description="LSASS: no credential dumping. Normal sessions.",
            metadata={**meta, "sessions": 2, "anomalies": 0},
            provenance_chain=["sha256:" + "l" * 64],
            base_trust=0.95,
        ),
    ]


# ---------------------------------------------------------------------------
# Fixture: false flag genuino — ataque real + timestomp probado
# ---------------------------------------------------------------------------

def _genuine_false_flag() -> list[Artifact]:
    meta = dict(_ACQ_META)
    return [
        Artifact(
            source_tool="memory_forensics",
            evidence_type="memory_process",
            raw_score=0.88,
            description="Process hollowing in svchost.exe confirmed. APT-level tooling.",
            metadata={**meta, "injections_detected": 2, "kernel_anomalies": 1, "technique": "T1055.012"},
            provenance_chain=["sha256:" + "M" * 64],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="lsass_session",
            raw_score=0.84,
            description="LSASS credential dumping detected (T1003.001).",
            metadata={**meta, "sessions": 7, "anomalies": 3, "credential_dumping_detected": True},
            provenance_chain=["sha256:" + "L" * 64],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="analyze_mft",
            evidence_type="mft_entry",
            raw_score=0.9,
            description=(
                "Cyrillic files have MFT timestamps predating volume creation "
                "(2023-06-01 vs volume 2024-01-15). $SI modified after $FN. Planted."
            ),
            metadata={
                **meta,
                "timestomp_detected": True,
                "backdating_detected": True,
                "mft_inconsistency": True,
                "mft_si_modified_after_fn": True,
                "volume_creation_time": "2024-01-15T00:00:00Z",
                "file_creation_time": "2023-06-01T00:00:00Z",
                "mft_entry_number": 1234,
            },
            provenance_chain=["sha256:" + "F" * 64],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="infer_intent",
            evidence_type="cultural_marker",
            raw_score=0.80,
            description=(
                "Cyrillic markers concentrated in single dropped file, "
                "no compilation history. Inconsistent with actor OPSEC."
            ),
            metadata={
                **meta,
                "cyrillic_filenames": 3,
                "keyboard_layout_detected": "RU",
                "concentrated_in_single_file": True,
                "no_compilation_history": True,
                "suspiciously_obvious": True,
            },
            provenance_chain=["sha256:" + "C" * 64],
            base_trust=0.3,
        ),
    ]


# ---------------------------------------------------------------------------
# Tests H-02 (1): máquina limpia nunca MALICE
# ---------------------------------------------------------------------------

def test_clean_foreign_machine_is_not_malice():
    engine = _engine_with(_clean_russian_machine())
    result = engine.evaluate()
    verdict = result.get("verdict", "UNKNOWN")
    assert verdict != "MALICE", (
        "Maquina rusa limpia (metadata completa, sin incidente) → MALICE. "
        f"Obtenido: {verdict}."
    )


def test_clean_foreign_machine_does_not_trigger_false_flag_rule():
    engine = _engine_with(_clean_russian_machine())
    types = _fracture_types(engine)
    assert "FALSE_FLAG_PATTERN" not in types, (
        f"FALSE_FLAG_PATTERN activo sobre maquina limpia. Fracturas: {sorted(types)}."
    )


# ---------------------------------------------------------------------------
# Tests H-02 (2): false flag genuino SÍ detectado
# ---------------------------------------------------------------------------

def test_genuine_false_flag_is_malice():
    engine = _engine_with(_genuine_false_flag())
    result = engine.evaluate()
    verdict = result.get("verdict", "UNKNOWN")
    assert verdict in ("MALICE", "SUSPICION"), (
        f"False flag genuino (ataque real + timestomp) no detectado. Obtenido: {verdict}."
    )


def test_genuine_false_flag_triggers_pattern():
    engine = _engine_with(_genuine_false_flag())
    types = _fracture_types(engine)
    assert "FALSE_FLAG_ATTRIBUTION_MISMATCH" in types, (
        f"FALSE_FLAG_ATTRIBUTION_MISMATCH no activo sobre false flag genuino. Fracturas: {sorted(types)}."
    )
