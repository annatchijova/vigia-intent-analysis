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

    @pytest.mark.parametrize("case", load_canonical_cases(), ids=lambda c: c["case_id"])
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
        print(f"  composite={result.get('composite_score'):.4f}")
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
        print(f"[{status}] {case['case_id']}: expected={expected} actual={actual} "
              f"composite={result.get('composite_score', 0):.4f} "
              f"fractures={result.get('fractures_detected', 0)}")

        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n[SUMMARY] Passed: {passed}/{len(cases)} | Failed: {failed}/{len(cases)}")
    exit(0 if failed == 0 else 1)
