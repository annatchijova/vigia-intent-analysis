"""B-208/B-209 — modules that were dead on import or dead on call (F821 sweep).

Same silent-breakage class as B-115/B-206: code paths with zero production
callers accumulate NameError/UnboundLocalError defects that no test feeds.
Found by `ruff --select F821` sweep, each reproduced before fixing:

- B-208 vigia_planner: module-level `urllib` never imported (NameError on
  import — the whole module was unimportable); duplicate _sanitize_llm_input
  referenced _LLM_DANGEROUS_TAGS/_CONTROL_CHARS moved to security.py by the
  P2-001 unification; _MAX_INTERPRETATION_LEN never existed.
- B-209 visible_variables.analyze_focus: used visible_artifacts before
  assignment (UnboundLocalError on every call) and cited total_rules, a
  detect_phase local that never existed in its scope.
- B-209 temporal_forensics_redteam: statistics/hashlib used, never imported.
"""
from __future__ import annotations


class TestB208PlannerImportable:
    def test_module_imports(self) -> None:
        import vigia.tools.vigia_planner as planner
        assert planner is not None

    def test_sanitizer_is_the_canonical_security_one(self) -> None:
        # __module__ en vez de identidad `is`: otros tests recargan módulos
        # (importlib.reload) y la identidad diverge entre instancias del
        # módulo; el origen de la función es el hecho que importa.
        import vigia.tools.vigia_planner as planner
        assert planner._sanitize_llm_input.__module__ == "vigia.security.security"

    def test_max_interpretation_len_defined_and_enforced(self) -> None:
        import vigia.tools.vigia_planner as planner
        assert planner._MAX_INTERPRETATION_LEN == 500
        out = planner._sanitize_llm_input(
            "x" * 600, max_length=planner._MAX_INTERPRETATION_LEN
        )
        assert out.startswith("[EVIDENCE_PADDING_ANOMALY_DETECTED")

    def test_ssrf_redirect_guard_class_resolves(self) -> None:
        import urllib.request

        import vigia.tools.vigia_planner as planner
        assert issubclass(planner._NoRedirect, urllib.request.HTTPRedirectHandler)


class TestB209AnalyzeFocus:
    def test_analyze_focus_does_not_crash(self) -> None:
        from vigia.tools.visible_variables import VisibleVariablesEngine
        result = VisibleVariablesEngine().analyze_focus(
            "B-209-TEST",
            [{"type": "process", "label": "svchost"}],
            [],
            ["T1055"],
        )
        assert result.bundle_id == "B-209-TEST"
        assert "consistency_score=" in result.consistency_rationale
        assert len(result.focus_hash) == 64

    def test_focus_hash_is_deterministic_and_covers_artifacts(self) -> None:
        from vigia.tools.visible_variables import VisibleVariablesEngine
        engine = VisibleVariablesEngine()
        args = ("B-209-DET", [{"type": "network", "label": "c2"}], [], ["T1071"])
        first = engine.analyze_focus(*args)
        second = engine.analyze_focus(*args)
        assert first.focus_hash == second.focus_hash
        # el hash debe cambiar si cambian los artifacts visibles (P1)
        third = engine.analyze_focus(
            "B-209-DET", [{"type": "network", "label": "otro"}], [], ["T1071"]
        )
        assert third.focus_hash != first.focus_hash


class TestB209TemporalRedteamImports:
    def test_statistics_and_hashlib_resolve_in_module_scope(self) -> None:
        import vigia.forensics.temporal_forensics_redteam as mod
        assert mod.statistics.median([1, 2, 3]) == 2
        assert mod.hashlib.sha256(b"x").hexdigest()
