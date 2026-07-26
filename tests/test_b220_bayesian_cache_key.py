"""
B-220: TrustFusionEngine.bayesian_update()'s cache was keyed by artifact_id
alone, ignoring the custom_window parameter -- a documented, public part of
the method's signature. A second call for the same artifact_id with a
different custom_window silently returned whatever was cached from the
first call's window, regardless of order.

Confirmed empirically before fixing (git stash comparison): with a1(prior
0.9) at t=0, a3(prior 0.5) at t=10s, and a5(prior 0.1, contaminated) at
t=200s -- inside the default 300s window but outside a 30s custom window --
bayesian_update('a3') then bayesian_update('a3', custom_window=30s) returned
the SAME object both times (posterior 0.15 leaked into the 30s-window call,
which should have seen only a1 and computed posterior 0.9).

Confirmed latent in production before this fix (grep, still true after):
no caller anywhere in the repository passes a non-default custom_window --
every production call site uses the implicit None default. This fix has
zero behavioral effect on any real call path; it only changes what happens
if/when custom_window is ever actually used.

Fix: cache key is (artifact_id, custom_window) instead of artifact_id alone.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from vigia.core.trust_fusion import TemporalArtifact, TrustFusionEngine


def _artifact(artifact_id: str, timestamp: datetime, prior_trust: float) -> TemporalArtifact:
    return TemporalArtifact(
        artifact_id=artifact_id, timestamp=timestamp, evidence_type="log_entry",
        source_tool="test", raw_score=0.5, prior_trust=prior_trust,
        provenance_chain=("t1",),
    )


def _build_engine() -> TrustFusionEngine:
    engine = TrustFusionEngine()
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    engine.add_artifact(_artifact("a1", base, 0.9))
    engine.add_artifact(_artifact("a3", base + timedelta(seconds=10), 0.5))
    # a5 is inside the default 300s window but outside a 30s custom window,
    # and contaminated (low prior) -- makes the two windows' results diverge
    # visibly, not just by object identity.
    engine.add_artifact(_artifact("a5", base + timedelta(seconds=200), 0.1))
    return engine


class TestCacheKeyIncludesCustomWindow:
    def test_default_then_custom_window_produce_distinct_results(self):
        engine = _build_engine()
        default_result = engine.bayesian_update("a3")
        custom_result = engine.bayesian_update("a3", custom_window=timedelta(seconds=30))

        assert default_result is not custom_result
        assert default_result.posterior_trust != custom_result.posterior_trust
        assert custom_result.posterior_trust == 0.9  # only a1 in the 30s window
        assert default_result.posterior_trust == 0.15  # a1 + contaminated a5

    def test_custom_then_default_window_also_produce_distinct_results(self):
        """Order must not matter -- neither call may be poisoned by the other."""
        engine = _build_engine()
        custom_result = engine.bayesian_update("a3", custom_window=timedelta(seconds=30))
        default_result = engine.bayesian_update("a3")

        assert custom_result is not default_result
        assert custom_result.posterior_trust == 0.9
        assert default_result.posterior_trust == 0.15

    def test_same_window_value_is_still_cached(self):
        """The fix must not disable caching -- identical calls should still
        hit the cache and return the same object."""
        engine = _build_engine()
        r1 = engine.bayesian_update("a3", custom_window=timedelta(seconds=30))
        r2 = engine.bayesian_update("a3", custom_window=timedelta(seconds=30))
        assert r1 is r2

    def test_repeated_default_calls_still_cached(self):
        engine = _build_engine()
        r1 = engine.bayesian_update("a3")
        r2 = engine.bayesian_update("a3")
        assert r1 is r2

    def test_add_artifact_still_clears_cache_with_tuple_keys(self):
        engine = _build_engine()
        r1 = engine.bayesian_update("a3")
        engine.add_artifact(_artifact("a6", datetime(2026, 1, 1, tzinfo=timezone.utc), 0.9))
        r2 = engine.bayesian_update("a3")
        assert r1 is not r2  # cache was invalidated by the new artifact


class TestNoProductionCallerPassesCustomWindow:
    def test_bayesian_update_has_no_non_default_custom_window_callers(self):
        import subprocess

        repo_root = __file__.rsplit("/tests/", 1)[0]
        result = subprocess.run(
            ["grep", "-rn", r"bayesian_update(.*custom_window", "--include=*.py", "."],
            cwd=repo_root, capture_output=True, text=True,
        )
        callers = [
            line for line in result.stdout.splitlines()
            if "/tests/" not in line and "def bayesian_update" not in line
        ]
        assert callers == [], (
            f"bayesian_update is now called with custom_window outside tests: "
            f"{callers} -- this fix's behavioral change is no longer latent, "
            f"update the B-220 BUGS_HISTORICO entry to reflect the real impact."
        )
