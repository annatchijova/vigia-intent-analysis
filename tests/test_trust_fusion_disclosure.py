"""
tests/test_trust_fusion_disclosure.py
=====================================
S-1 (docs/PATTERN_HUNT_20260718.md, 2026-07-18): trust_fusion.py reproduced the
two silent-omission triggers already patched in CAIE/bridge (ac48177: present-
but-unparseable timestamp coerced to now(); ad7e41f: non-dict metadata dropped)
plus the H-10 shape (artifact skipped without a counter), all reaching the live
MCP tool output (composite_trust / daubert_admissible) with NO disclosure.

These guards exercise all three vectors end-to-end through the async MCP entry
point trust_fusion_analysis and assert the degradation is surfaced in the
result dict — a composite_trust computed over degraded input must not read as
"analyzed and clean" without saying what was lost.
"""
from __future__ import annotations


import pytest

tf = pytest.importorskip(
    "vigia.core.trust_fusion",
    reason="vigia.core.trust_fusion not importable (run with PYTHONPATH=$(pwd))",
)
trust_fusion_analysis = tf.trust_fusion_analysis
create_artifact_from_caie_result = tf.create_artifact_from_caie_result


def _good_artifact(i: int = 0) -> dict:
    return {
        "artifact_id": f"good_{i}", "evidence_type": "log_entry",
        "source_tool": "read_evidence", "raw_score": 0.4, "prior_trust": 0.9,
        "timestamp": "2026-04-10T10:00:0{}Z".format(i % 10),
        "provenance_chain": [f"sha256:g{i}"], "metadata": {"k": i},
    }


# ---------------------------------------------------------------------------
# Unit level — the coercion sink
# ---------------------------------------------------------------------------

class TestCoercionSink:
    def test_unparseable_timestamp_recorded(self):
        disc: list = []
        create_artifact_from_caie_result(
            {"artifact_id": "a", "timestamp": "not-a-date", "metadata": {}},
            "log_entry", "tool", disclosures=disc,
        )
        assert any(d["field"] == "timestamp" for d in disc), disc

    def test_absent_timestamp_is_not_a_disclosure(self):
        disc: list = []
        create_artifact_from_caie_result(
            {"artifact_id": "a", "metadata": {}}, "log_entry", "tool", disclosures=disc,
        )
        assert not any(d["field"] == "timestamp" for d in disc), (
            "an ABSENT timestamp fell back to now() by design — that is not "
            "degraded data and must not be reported as a loss"
        )

    def test_non_dict_metadata_recorded(self):
        disc: list = []
        create_artifact_from_caie_result(
            {"artifact_id": "a", "metadata": []}, "log_entry", "tool", disclosures=disc,
        )
        assert any(d["field"] == "metadata" for d in disc), disc

    def test_absent_metadata_is_not_a_disclosure(self):
        disc: list = []
        create_artifact_from_caie_result(
            {"artifact_id": "a"}, "log_entry", "tool", disclosures=disc,
        )
        assert not any(d["field"] == "metadata" for d in disc)

    def test_none_sink_preserves_legacy_behavior(self):
        # No sink → no crash, artifact still built (backward compat for any
        # other caller).
        art = create_artifact_from_caie_result(
            {"artifact_id": "a", "timestamp": "bad", "metadata": []},
            "log_entry", "tool",
        )
        assert art.artifact_id == "a"


# ---------------------------------------------------------------------------
# End-to-end — the MCP tool result must disclose
# ---------------------------------------------------------------------------

class TestAnalysisDisclosesDegradation:
    """async tests: the suite runs under pytest-asyncio asyncio_mode=auto, so
    these are driven by the plugin's event loop (a manual run_until_complete
    conflicts with loops opened by other async tests in the full run)."""

    async def test_clean_input_reports_not_degraded(self):
        res = await trust_fusion_analysis([_good_artifact(0), _good_artifact(1)])
        assert res["status"] == "OK"
        assert res["input_degraded"] is False
        assert res["artifacts_rejected"] == 0
        assert res["normalization_disclosures"] == []
        assert res["artifacts_submitted"] == 2

    async def test_unparseable_timestamp_surfaces(self):
        bad = _good_artifact(0)
        bad["timestamp"] = "definitely-not-iso"
        res = await trust_fusion_analysis([bad, _good_artifact(1)])
        assert res["input_degraded"] is True
        assert any(
            d["field"] == "timestamp" for d in res["normalization_disclosures"]
        ), res["normalization_disclosures"]

    async def test_non_dict_metadata_surfaces(self):
        bad = _good_artifact(0)
        bad["metadata"] = []  # the ad7e41f vector
        res = await trust_fusion_analysis([bad, _good_artifact(1)])
        assert res["input_degraded"] is True
        assert any(
            d["field"] == "metadata" for d in res["normalization_disclosures"]
        ), res["normalization_disclosures"]

    async def test_skipped_artifact_is_counted_not_silent(self):
        # A non-mapping artifact makes dict(art_dict) raise → skip branch.
        res = await trust_fusion_analysis([_good_artifact(0), 12345])
        assert res["artifacts_submitted"] == 2
        # Exactly one survived; the other must be COUNTED, not vanished.
        assert res["artifact_count"] == 1
        assert res["artifacts_rejected"] == 1
        assert res["rejected_details"] and res["rejected_details"][0]["index"] == 1
        assert res["input_degraded"] is True

    async def test_all_skipped_error_path_still_discloses(self):
        res = await trust_fusion_analysis([12345, 67890])
        assert res["status"] == "ERROR"
        # The old error path returned blind "No valid artifacts"; now it says
        # how many were submitted and rejected.
        assert res["artifacts_submitted"] == 2
        assert res["artifacts_rejected"] == 2
        assert res["input_degraded"] is True

    async def test_composite_over_degraded_input_carries_the_flag(self):
        """The load-bearing property: a numeric composite_trust /
        daubert_admissible is still returned, but never WITHOUT the
        input_degraded flag beside it."""
        bad = _good_artifact(0)
        bad["metadata"] = ()  # non-dict → dropped
        bad["timestamp"] = "nope"  # unparseable → coerced
        res = await trust_fusion_analysis([bad, _good_artifact(1)])
        assert "composite_trust" in res and "daubert_report" in res
        assert res["input_degraded"] is True
        assert len(res["normalization_disclosures"]) >= 2
