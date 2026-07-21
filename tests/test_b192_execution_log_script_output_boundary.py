"""B-192 — the standalone execution-log script must preserve B-190's boundary."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.scripts import generate_execution_log


class _NoMatchDetector:
    def analyze(self, text: str, artifact_id: str, timestamp: str) -> dict:
        return {"matches": []}


def test_b192_script_default_uses_private_work_dir_from_an_evidence_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    evidence.mkdir()
    monkeypatch.chdir(evidence)
    monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(evidence))
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.setattr(
        generate_execution_log,
        "aggregate_evidence",
        lambda detector_output: {"mi_final": {"num": 0, "den": 1}},
    )
    monkeypatch.setattr(
        generate_execution_log,
        "decide",
        lambda detector_output, aggregate: {
            "alert_level": "LOW",
            "reason": "FIXTURE",
        },
    )

    log_path = generate_execution_log.process_case(
        {"case_id": "B192-001", "text": "source text"},
        _NoMatchDetector(),
    )

    assert Path(log_path) == work / "logs" / "B192-001_execution.jsonl"
    assert list(evidence.iterdir()) == []
