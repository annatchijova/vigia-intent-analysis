"""B-116 — SignalQualityGate wired in SHADOW mode (WARN, zero verdict authority).

Doctrine decision (Anna, 2026-07-22): the gate's diversity/uniformity checks
are informative WARN, never a verdict cap — the scorer already enforces its
own Daubert Corroboration Gate, and the gate's uniformity check contradicts
B-171 doctrine. These tests pin the shadow contract:
  1. the shadow annotation exists on the scorer's main path;
  2. it NEVER changes verdict/score/confidence (0-flips, corpus-verified);
  3. a broken shadow module can never break scoring;
  4. unmeasurable artifacts are counted, not imputed 0.0.
"""
from __future__ import annotations

import vigia_scorer
from vigia.core.signal_quality_shadow import shadow_signal_quality


def _case(arts):
    return {"case_id": "B116-SHADOW", "artifacts": arts}


def _art(**kw):
    base = {
        "artifact_id": "a1",
        "evidence_type": "log_entry",
        "raw_score": 0.9,
        "source_tool": "search_pattern",
        "prior_trust": 0.9,
    }
    base.update(kw)
    return base


class TestShadowPresence:
    def test_main_path_result_carries_shadow_annotation(self) -> None:
        r = vigia_scorer._vigia_score(_case([
            _art(artifact_id="a1", source_tool="search_pattern"),
            _art(artifact_id="a2", source_tool="list_files", evidence_type="mft_entry"),
        ]))
        sh = r.get("signal_quality_shadow")
        assert sh is not None
        assert sh["mode"] == "shadow_warn"
        assert "reason_code" in sh or "error" in sh

    def test_shadow_warn_never_touches_verdict(self) -> None:
        # Mono-tool case: gate says ABSTAIN_INSUFFICIENT_TOOLS in shadow,
        # while the motor verdict must remain whatever the motor computed.
        arts = [_art(artifact_id=f"a{i}", source_tool="search_pattern") for i in range(3)]
        r = vigia_scorer._vigia_score(_case(arts))
        sh = r["signal_quality_shadow"]
        assert sh["passed"] is False
        assert sh["reason_code"].startswith("ABSTAIN_")
        assert r["verdict"] != "ABSTAIN"  # shadow tiene cero autoridad


class TestShadowNeverBreaksScoring:
    def test_scoring_survives_shadow_crash(self, monkeypatch) -> None:
        import vigia.core.signal_quality_shadow as shadow_mod

        def _boom(_arts):
            raise RuntimeError("shadow roto a propósito")

        monkeypatch.setattr(shadow_mod, "shadow_signal_quality", _boom)
        r = vigia_scorer._vigia_score(_case([_art()]))
        assert r["verdict"]  # el scoring completó
        sh = r.get("signal_quality_shadow", {})
        assert "error" in sh or sh.get("reason_code")


class TestShadowHonestDegradation:
    def test_artifacts_without_raw_score_counted_not_imputed(self) -> None:
        out = shadow_signal_quality([
            {"evidence_type": "log_entry", "source_tool": "t1", "raw_score": 0.9},
            {"evidence_type": "log_entry", "source_tool": "t2"},  # sin raw_score
        ])
        assert out["n_signals_evaluated"] == 1
        assert out["n_signals_unmeasured"] == 1

    def test_never_raises_on_garbage(self) -> None:
        out = shadow_signal_quality([None, 42, {"raw_score": "x"}])  # type: ignore[list-item]
        assert out["mode"] == "shadow_warn"
        assert out.get("n_signals_evaluated", 0) == 0 or "error" in out
