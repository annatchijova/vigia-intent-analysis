"""B-204: legacy reproduction mode must average the RAW artifact fields.

B-163 normalizes the case once at the adapter boundary so presentation and
the default motor path share one label-blind representation.  That
normalization synthesizes ``raw_score`` / ``prior_trust`` for legacy-schema
artifacts (score clamped to >= 0.05, trust 0.70-0.90 by Peirce layer).  The
explicit ``VIGIA_EBS_RESOLVE=legacy`` mode exists solely to reproduce
pre-B-163 bundles, whose average was computed over the raw JSON fields
(defaults 0 and 1/2 when a field is absent).  After B-163 landed, legacy
mode silently averaged the synthesized values instead, so a historical
reproduction of a legacy-schema case no longer reproduced its bundle.

The fix keeps one arithmetic with two explicit inputs: normalized artifacts
for presentation and the default motor path, raw artifacts only under the
explicit legacy reproduction mode.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sift_orchestrator as so
from vigia.pipeline.vigia_integration_bridge import normalize_case_schema

LEGACY_SCHEMA_CASE = {
    "case_id": "B204-LEGACY",
    "artifacts": [
        {
            "artifact_id": "A1",
            "type": "log",
            "content": "plain legacy line without anomalies",
            "forensic_anomalies": [],
            "analyst_flags": [],
        }
    ],
}

CANONICAL_CASE = {
    "case_id": "B204-CANON",
    "artifacts": [
        {
            "artifact_id": "C1",
            "evidence_type": "log_entry",
            "raw_score": 0.6,
            "prior_trust": 0.5,
            "source_tool": "unit_fixture",
            "description": "canonical artifact with explicit fields",
        }
    ],
}


def _adapter(monkeypatch, mode: str, case: dict, tmp_path: Path) -> dict:
    monkeypatch.setenv("VIGIA_EBS_RESOLVE", mode)
    path = tmp_path / f"{case['case_id']}__{mode}.json"
    path.write_text(json.dumps(case), encoding="utf-8")
    orch = so.SIFTOrchestrator(case_id=case["case_id"])
    return orch._analyze_ebs_json(str(path))


def _normalized_avg(case: dict) -> Fraction:
    arts = normalize_case_schema(case)["artifacts"]
    return sum(
        Fraction(str(a["raw_score"])) * Fraction(str(a["prior_trust"]))
        for a in arts
    ) / Fraction(len(arts), 1)


class TestLegacyAvgRawReproduction:
    def test_fixture_representations_actually_diverge(self):
        """Precondition: raw and normalized arithmetic differ for this case.

        If normalization ever stops synthesizing scores for legacy-schema
        artifacts, the other tests here would pass vacuously — fail loudly
        instead so the fixture gets redesigned.
        """
        assert _normalized_avg(LEGACY_SCHEMA_CASE) != Fraction(0, 1), (
            "fixture degenerated: normalization no longer synthesizes a "
            "nonzero raw_score*prior_trust for legacy-schema artifacts"
        )

    def test_legacy_mode_averages_raw_fields(self, monkeypatch, tmp_path):
        """Raw legacy artifacts carry no raw_score/prior_trust: avg must be 0."""
        res = _adapter(monkeypatch, "legacy", LEGACY_SCHEMA_CASE, tmp_path)
        assert res["pipeline_meta"]["ebs_adapter_mode"] == "legacy"
        assert res["pipeline_meta"]["avg_score"] == "0", (
            "legacy reproduction averaged the B-163-normalized artifacts "
            f"(avg={res['pipeline_meta']['avg_score']}) instead of the raw "
            "pre-B-163 fields"
        )

    def test_motor_mode_still_averages_normalized_fields(self, monkeypatch, tmp_path):
        res = _adapter(monkeypatch, "motor", LEGACY_SCHEMA_CASE, tmp_path)
        assert res["pipeline_meta"]["ebs_adapter_mode"] == "motor"
        assert res["pipeline_meta"]["avg_score"] == str(
            _normalized_avg(LEGACY_SCHEMA_CASE)
        )

    def test_modes_agree_on_canonical_case(self, monkeypatch, tmp_path):
        """Canonical artifacts are normalization-idempotent: same avg both ways."""
        legacy = _adapter(monkeypatch, "legacy", CANONICAL_CASE, tmp_path)
        motor = _adapter(monkeypatch, "motor", CANONICAL_CASE, tmp_path)
        assert (
            legacy["pipeline_meta"]["avg_score"]
            == motor["pipeline_meta"]["avg_score"]
            == str(Fraction(3, 10))
        )

    def test_legacy_mode_presentation_stays_normalized(self, monkeypatch, tmp_path):
        """Only the scoring arithmetic switches input — B-163's normalized
        presentation (signals) must not regress to raw projection."""
        res = _adapter(monkeypatch, "legacy", LEGACY_SCHEMA_CASE, tmp_path)
        [signal] = res["signals"]
        assert signal["artifact_id"] == "A1"
        assert signal["evidence_type"] != "unknown"
