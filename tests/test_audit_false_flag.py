"""
tests/test_audit_false_flag.py
==============================
Red-team audit — Finding H-02: FALSE_FLAG_PATTERN and false attribution.

DESIGN DECISION (not an implementation bug):
    False attribution IS malicious. Planting flags to blame a third party is a
    deliberate, deceptive act. But the malice belongs to the PLANTER, not to
    whoever writes in Russian. Russian is spoken in many places; a machine with
    Cyrillic/UTC+3 configuration is not, by itself, evidence of anything.

    The current CAIE rule fires FALSE_FLAG_PATTERN on:
        avg_cultural > 0.5  AND  avg_technical < 0.2
    i.e., it infers "planted" from the ABSENCE of technical evidence.
    This is doubly wrong:

      (1) It marks as MALICE a foreign user with a clean machine
          (no attack occurred; the markers are their native configuration).
      (2) It FAILS to detect the REAL false flag, which has HIGH technical
          evidence (the attack DID occur) with attribution that is too
          convenient or contradictory relative to the technical profile.

    A genuine false flag = (real malicious event) AND (attribution that
    contradicts the technical profile of that event). The fracture is in the
    MISMATCH, not in the language.

THESE TESTS:
    - test_clean_foreign_machine_is_not_malice:
        Clean Russian machine, no attack → NEVER MALICE. This is the test that
        proves to a panel that VIGÍA does not accuse someone for writing in Russian.
        xfail until the rule fix (currently fires MALICE).

    - test_genuine_false_flag_is_malice:
        Real attack (high technical) + contradictory attribution → MALICE.
        xfail until the fix (the current rule requires LOW technical, so it
        misses the genuine false flag).

When you apply the rule fix, these transition from xfail to XPASS. That is the
indicator that the fix is correct. At that point, change strict=False to
strict=True to make them a hard guard.
"""
from __future__ import annotations

import pytest

caie = pytest.importorskip(
    "vigia.tools.caie",
    reason="vigia.tools.caie not importable in this environment (run with PYTHONPATH=$(pwd))",
)
CrossArtifactIncongruenceEngine = caie.CrossArtifactIncongruenceEngine
Artifact = caie.Artifact


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _engine_with(artifacts: list[Artifact]) -> CrossArtifactIncongruenceEngine:
    engine = CrossArtifactIncongruenceEngine()
    for a in artifacts:
        engine.add_artifact(a)
    return engine


def _fracture_types(engine: CrossArtifactIncongruenceEngine) -> set[str]:
    return {f.fracture_type for f in engine.detect_fractures()}


# ---------------------------------------------------------------------------
# Evidence fixtures
# ---------------------------------------------------------------------------

def _clean_russian_machine() -> list[Artifact]:
    """
    A Russian developer from Torzhok. Cyrillic filenames, RU keyboard, UTC+3
    timezone. The system is spotless: no injection, no dumping, healthy kernel.
    NO incident occurred.
    """
    return [
        Artifact(
            source_tool="infer_intent",
            evidence_type="cultural_marker",
            raw_score=0.85,
            description=(
                "Cyrillic filenames ('отчет_финансы.docx'), keyboard layout RU, "
                "timezone UTC+3, comments in Russian. Native configuration."
            ),
            metadata={
                "cyrillic_filenames": 3,
                "keyboard_layout_detected": "RU",
                "timezone_offset": "+03:00",
                "language_confidence": 0.91,
            },
            provenance_chain=["sha256:cultural_chain_001"],
            base_trust=0.3,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="memory_process",
            raw_score=0.05,
            description="Memory: no process injection, no kernel anomalies, clean state.",
            metadata={"injections_detected": 0, "kernel_anomalies": 0, "suspicious_handles": 0},
            provenance_chain=["sha256:mem_chain_001", "sha256:mem_chain_002"],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="lsass_session",
            raw_score=0.08,
            description="LSASS: no credential dumping. Normal session count.",
            metadata={"sessions": 2, "anomalies": 0},
            provenance_chain=["sha256:lsass_chain_001"],
            base_trust=0.95,
        ),
    ]


def _genuine_false_flag() -> list[Artifact]:
    """
    REAL false flag: an attack occurred (injection + credential dumping,
    HIGH technical evidence that is hard to fake) and, on top of that, someone
    left Russian markers that are too neat, whose profile contradicts the
    observed technical TTPs. The malice is in the attribution/technical mismatch.
    """
    return [
        Artifact(
            source_tool="list_processes",
            evidence_type="memory_process",
            raw_score=0.88,
            description=(
                "Process hollowing in svchost.exe confirmed in memory. "
                "Reflective DLL injection. Hard-to-fake structural evidence."
            ),
            metadata={"injections_detected": 2, "kernel_anomalies": 1, "technique": "T1055.012"},
            provenance_chain=["sha256:mem_real_001", "sha256:mem_real_002"],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="list_processes",
            evidence_type="lsass_session",
            raw_score=0.84,
            description="LSASS credential dumping detected (T1003.001). Active compromise.",
            metadata={"sessions": 7, "anomalies": 3, "technique": "T1003.001"},
            provenance_chain=["sha256:lsass_real_001"],
            base_trust=0.95,
        ),
        Artifact(
            source_tool="infer_intent",
            evidence_type="cultural_marker",
            raw_score=0.90,
            description=(
                "Suspiciously pristine Russian-language strings injected into the "
                "dropper, inconsistent with the actor's actual toolchain and OPSEC. "
                "Attribution markers contradict the technical TTP profile."
            ),
            metadata={
                "cyrillic_strings": 12,
                "attribution_consistency_with_ttps": "LOW",
                "placement": "too_clean",
            },
            provenance_chain=["sha256:cultural_real_001"],
            base_trust=0.3,
        ),
    ]


# ---------------------------------------------------------------------------
# H-02 (1): absence must not accuse
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="H-02: the current rule fires FALSE_FLAG_PATTERN on cultural-high + "
           "technical-low. A clean foreign machine must NOT be MALICE. "
           "Transitions to XPASS when the rule requires a real malicious event.",
    strict=False,
)
def test_clean_foreign_machine_is_not_malice():
    engine = _engine_with(_clean_russian_machine())
    result = engine.evaluate()
    verdict = result.get("verdict", "UNKNOWN")

    assert verdict != "MALICE", (
        "A clean Russian machine (no incident) was classified as MALICE. "
        "That is wrongful accusation by language/origin. Expected: NOISE/UNKNOWN. "
        f"Got: {verdict}."
    )


@pytest.mark.xfail(
    reason="H-02: same — the false flag pattern must not activate solely on "
           "absence of technical evidence.",
    strict=False,
)
def test_clean_foreign_machine_does_not_trigger_false_flag_rule():
    engine = _engine_with(_clean_russian_machine())
    types = _fracture_types(engine)

    assert "FALSE_FLAG_PATTERN" not in types, (
        "FALSE_FLAG_PATTERN fired on a clean machine with foreign configuration. "
        "Absence of technical evidence is NOT evidence of planting. "
        f"Fractures detected: {sorted(types)}."
    )


# ---------------------------------------------------------------------------
# H-02 (2): the genuine false flag MUST be detected
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="H-02: the current rule requires LOW technical, so it FAILS to detect "
           "the real false flag (which has HIGH technical). Transitions to XPASS "
           "when detection is based on attribution/technical-profile mismatch.",
    strict=False,
)
def test_genuine_false_flag_is_malice():
    engine = _engine_with(_genuine_false_flag())
    result = engine.evaluate()
    verdict = result.get("verdict", "UNKNOWN")

    assert verdict in ("MALICE", "SUSPICION"), (
        "A genuine false flag (real attack + contradictory attribution) was not "
        "flagged. The malice of the planter must be detected. "
        f"Got: {verdict}."
    )
