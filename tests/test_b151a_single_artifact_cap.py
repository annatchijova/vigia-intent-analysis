"""
tests/test_b151a_single_artifact_cap.py
=======================================
B-151a: the single-artifact corroboration cap in vigia_scorer.py
(`if n_artifacts < 2 and final_score > 0.65: final_score = 0.65`) rewrote the
sealed score with no auditable trace. The fix surfaces a
`single_artifact_score_cap` marker (+ a reason note) into base_result when it
fires — a probative-strength reduction must never be silent.

Finding while verifying: the cap is currently UNREACHABLE. A single signal
artifact is suppressed to ~0.04 (single-artifact non-corroboration), far below
the 0.65 cap, so the silent-downgrade risk B-151a named is not live — the clamp
is defensive dead code and the marker is forward-looking disclosure.

This test PINS that unreachability. If a single artifact ever scores >= 0.65 the
assertion fails, flagging that the B-151a marker path has become live and must be
verified end-to-end (cap fires -> marker present, verdict unchanged).
"""
from __future__ import annotations

from vigia_scorer import _vigia_score

_CAP = 0.65


def _strong_single_artifact_result() -> dict:
    art = {
        "source_tool": "t", "evidence_type": "cryptographic_hash",
        "raw_score": 0.99, "base_trust": 1.0, "prior_trust": 1.0,
        "metadata": {
            "pid": 1, "injections_detected": True, "kernel_anomalies": True,
            "dest_ip": "8.8.8.8", "examiner_id": "E", "verdict": "MALICE",
        },
    }
    return _vigia_score({"case_id": "B151A-CAP", "artifacts": [art]})


def test_single_artifact_cap_is_currently_unreachable():
    r = _strong_single_artifact_result()
    score = float(r["score"])
    assert score < _CAP, (
        f"A single artifact scored {score} >= {_CAP}: the B-151a single-artifact "
        f"cap is now REACHABLE. Verify single_artifact_score_cap surfaces and the "
        f"verdict is unchanged."
    )
    # Cap did not fire -> the marker must be ABSENT (no false disclosure).
    assert "single_artifact_score_cap" not in r
