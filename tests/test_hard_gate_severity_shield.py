"""
Regression — the EFFECT_BEFORE_CAUSE hard gate coerces severity through
_sev_float instead of comparing raw JSON against a float.

Ref: docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-E. The hard gate is the
highest-authority branch (unconditional MALICE), yet it read examiner-supplied
severity directly: a string ("high") or None crashed the whole scorer on the
`>= 0.9` comparison. After the fix, a malformed severity is treated as 0.0 and
the gate does not fire (a bad value must not fabricate an unconditional MALICE);
a valid numeric severity still fires exactly as before.
"""

import logging

logging.disable(logging.CRITICAL)

from vigia_scorer import _vigia_score  # noqa: E402


def _case(severity):
    return {
        "case_id": "HARD-GATE-TEST",
        "artifacts": [
            {"artifact_id": "a1", "evidence_type": "log_entry", "source_tool": "t",
             "raw_score": 0.5, "provenance_chain": ["sha256:x"],
             "description": "effect artifact", "metadata": {}},
            {"artifact_id": "a2", "evidence_type": "memory_process", "source_tool": "t",
             "raw_score": 0.5, "provenance_chain": ["sha256:y"],
             "description": "cause artifact", "metadata": {}},
        ],
        "temporal_violations": [
            {"type": "EFFECT_BEFORE_CAUSE", "severity": severity,
             "cause": {"artifact_id": "a2"}, "effect": {"artifact_id": "a1"}},
        ],
    }


class TestHardGateSeverityShield:

    def test_string_severity_does_not_crash(self):
        r = _vigia_score(_case("high"))
        assert r["verdict"] != "ERROR"
        # malformed severity -> 0.0 -> gate does not fire
        assert r.get("hard_temporal_gate") is False

    def test_none_severity_does_not_crash(self):
        r = _vigia_score(_case(None))
        assert r["verdict"] != "ERROR"
        assert r.get("hard_temporal_gate") is False

    def test_valid_high_severity_still_fires(self):
        r = _vigia_score(_case(1.0))
        assert r["verdict"] == "MALICE"
        assert r.get("hard_temporal_gate") is True

    def test_valid_low_severity_does_not_fire(self):
        r = _vigia_score(_case(0.5))
        assert r.get("hard_temporal_gate") is False
