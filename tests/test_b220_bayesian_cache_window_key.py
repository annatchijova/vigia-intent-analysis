"""B-220 — bayesian_update's cache key must include custom_window.

`TrustFusionEngine.bayesian_update(artifact_id, custom_window=None)` accepts
`custom_window` and uses it to compute the temporal neighbourhood, but the
cache was keyed on `artifact_id` alone. A second call with a different window
returned the first call's cached object without recomputing — so the answer
depended only on call order, not on the window requested.

Latent today (no production caller passes custom_window), but the parameter
is documented and MCP-exposed, so a future caller would silently get the
wrong window. Regression guard, red-first against the pre-fix code.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from vigia.core.trust_fusion import TemporalArtifact, TrustFusionEngine


def _engine_with_offset_neighbor() -> TrustFusionEngine:
    """center 'a3' at t0+100s, neighbour 'a2' 40s earlier — inside a wide
    window, outside a narrow one."""
    t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    eng = TrustFusionEngine(temporal_window_seconds=300)
    eng.add_artifact(TemporalArtifact("a2", t0 + timedelta(seconds=60),
                                      "log", "toolX", 0.9, 0.1, ()))
    eng.add_artifact(TemporalArtifact("a3", t0 + timedelta(seconds=100),
                                      "log", "toolX", 0.5, 0.5, ()))
    return eng


class TestBayesianCacheWindowKey:
    def test_narrow_window_recomputes_after_default(self) -> None:
        eng = _engine_with_offset_neighbor()
        r_default = eng.bayesian_update("a3")  # 300s window: a2 is a neighbour
        r_narrow = eng.bayesian_update("a3", custom_window=timedelta(seconds=10))
        # 10s window excludes a2 (40s away) → no neighbours → likelihood 0.5.
        assert r_default is not r_narrow
        assert r_default.posterior_trust != r_narrow.posterior_trust

    def test_default_window_recomputes_after_narrow(self) -> None:
        # order-independence: the bug made the FIRST call win regardless.
        eng = _engine_with_offset_neighbor()
        r_narrow = eng.bayesian_update("a3", custom_window=timedelta(seconds=10))
        r_default = eng.bayesian_update("a3")
        assert r_default is not r_narrow
        assert r_default.posterior_trust != r_narrow.posterior_trust

    def test_identical_calls_still_share_cache(self) -> None:
        eng = _engine_with_offset_neighbor()
        first = eng.bayesian_update("a3", custom_window=timedelta(seconds=10))
        second = eng.bayesian_update("a3", custom_window=timedelta(seconds=10))
        assert first is second  # same key → cached, no wasted recompute

    def test_add_artifact_still_clears_cache(self) -> None:
        eng = _engine_with_offset_neighbor()
        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        before = eng.bayesian_update("a3")
        eng.add_artifact(TemporalArtifact("a4", t0 + timedelta(seconds=101),
                                          "log", "toolX", 0.9, 0.1, ()))
        after = eng.bayesian_update("a3")
        assert before is not after  # cache invalidated by the new artifact
