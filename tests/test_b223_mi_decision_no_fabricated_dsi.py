"""B-223 — generate_execution_log.py must not fabricate D/S/I for a
RISK_CALCULATION entry shaped for an engine (risk_bounded_layer) it never
runs. The script actually calls decision_layer.decide() (MI-threshold
based, no drift/graph_stability/consistency_score at all), so its log
entry must describe that engine honestly instead.

Regression guard, red-first against the pre-fix code: before the fix,
process_case() emitted an event_type=RISK_CALCULATION entry with
D=0.1 (hardcoded), S and I derived from ad-hoc formulas of mi_float that
correspond to no real calculation, alongside the risk_bounded_layer
formula string "r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))" — describing a
different decision engine as if it were the one that actually decided.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from vigia.core.decision_layer import DEFAULT_HIGH, DEFAULT_LOW, DEFAULT_MEDIUM
from vigia.scripts import generate_execution_log


class _DetectorWithOneMatch:
    def analyze(self, text: str, artifact_id: str, timestamp: str) -> dict:
        return {"matches": []}


def _run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mi_num: int, mi_den: int) -> list[dict]:
    work = tmp_path / "work"
    monkeypatch.setenv("VIGIA_WORK_DIR", str(work))
    monkeypatch.setattr(
        generate_execution_log,
        "aggregate_evidence",
        lambda detector_output: {"mi_final": {"num": mi_num, "den": mi_den}},
    )
    log_path = generate_execution_log.process_case(
        {"case_id": "B223-001", "text": "source text"},
        _DetectorWithOneMatch(),
    )
    return [json.loads(line) for line in Path(log_path).read_text().splitlines()]


def test_no_risk_calculation_event_is_emitted(monkeypatch, tmp_path) -> None:
    """The risk_bounded_layer-shaped event type must not appear at all —
    this script never runs that engine."""
    events = _run(monkeypatch, tmp_path, mi_num=1, mi_den=2)
    types = {e["event_type"] for e in events}
    assert "RISK_CALCULATION" not in types


def test_mi_decision_event_has_no_dsi_fields(monkeypatch, tmp_path) -> None:
    events = _run(monkeypatch, tmp_path, mi_num=1, mi_den=2)
    mi_event = next(e for e in events if e["event_type"] == "MI_DECISION")
    assert "variables" not in mi_event
    assert "formula" not in mi_event
    # No D/S/I anywhere in the payload — decision_layer computes none of them.
    flat = json.dumps(mi_event)
    for fabricated_key in ('"D"', '"S"', '"I"'):
        assert fabricated_key not in flat, f"{fabricated_key} leaked into MI_DECISION: {mi_event}"


def test_mi_decision_reports_the_real_engine_and_thresholds(monkeypatch, tmp_path) -> None:
    events = _run(monkeypatch, tmp_path, mi_num=1, mi_den=2)
    mi_event = next(e for e in events if e["event_type"] == "MI_DECISION")
    assert mi_event["engine"] == "vigia.core.decision_layer.RiskBoundedDecisionLayer"
    # _write() canonicalizes floats to "%.8f" strings (execution_logger's
    # deterministic encoder) — assert on the canonicalized values, not raw floats.
    assert mi_event["mi"] == f"{0.5:.8f}"
    assert mi_event["thresholds"] == {
        "low": f"{float(DEFAULT_LOW):.8f}",
        "medium": f"{float(DEFAULT_MEDIUM):.8f}",
        "high": f"{float(DEFAULT_HIGH):.8f}",
    }


def test_mi_decision_reason_comes_from_the_real_decide_output(monkeypatch, tmp_path) -> None:
    """reason must be decision_layer's own generated reason string, not a
    borrowed risk_bounded_layer reason_code shape."""
    events = _run(monkeypatch, tmp_path, mi_num=1, mi_den=2)
    mi_event = next(e for e in events if e["event_type"] == "MI_DECISION")
    assert "MI" in mi_event["reason"]  # decision_layer._generate_reason() always names MI
    assert mi_event["reason"] != ""
