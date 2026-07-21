"""B-191 — generated logs must consume the detector's canonical match schema."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vigia.scripts import generate_execution_log


class _DetectorWithCanonicalMatch:
    """Minimal detector double shaped like ``SemioticDetectorV2.analyze``."""

    def analyze(self, text: str, artifact_id: str, timestamp: str) -> dict:
        return {
            "matches": [
                {
                    "pattern_name": "CANONICAL_PATTERN",
                    "peirce_layer": "SECONDNESS",
                    "weight_num": 7,
                    "weight_den": 10,
                    "matched_text": "observed source text",
                    "description": "canonical detector match",
                }
            ]
        }


def test_b191_generator_logs_a_canonical_detector_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A normal match must not crash the SANS execution-log generator."""
    work = tmp_path / "work"
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.setattr(
        generate_execution_log,
        "aggregate_evidence",
        lambda detector_output: {"mi_final": {"num": 1, "den": 2}},
    )
    monkeypatch.setattr(
        generate_execution_log,
        "decide",
        lambda detector_output, aggregate: {
            "alert_level": "MEDIUM",
            "reason": "FIXTURE",
        },
    )

    log_path = generate_execution_log.process_case(
        {"case_id": "B191-001", "text": "source text"},
        _DetectorWithCanonicalMatch(),
    )

    events = [json.loads(line) for line in Path(log_path).read_text().splitlines()]
    finding = next(event for event in events if event["event_type"] == "FORENSIC_FINDING")
    assert finding["_pattern_weight"] == {"num": "7:int", "den": "10:int"}
