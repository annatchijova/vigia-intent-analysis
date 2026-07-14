"""
tests/test_pipeline_robustness_narrative.py
============================================
Regresión de AUDITORIA_PIPELINE_ROBUSTEZ.md (tandas F1-F9).

Invariante central: la narrativa Peircean debe ser informativa en TODOS los
casos donde hay señales — nunca el genérico "[FIRSTNESS] Pipeline error." —
y el veredicto sellado nunca puede divergir de la narrativa del mismo bundle.

Cobertura (F9):
  1. reason() con 3/5/10 señales mixtas no lanza y emite las tres capas.
  2. Empate exacto de CCS → ABSTAIN_V2, nunca H2-BENIGN por orden alfabético.
  3. Señales todas z=0 → hipótesis benigna con narrativa coherente.
  4. 1 primaria + 4 derivadas → gate de corroboración NO satisfecho (ABSTAIN);
     una meta-señal derivada z>3 no fabrica INTENT (caso VANKO).
  5. Mobile con z>3 → veredicto ≠ NOISE; merge escalado en evidencia mixta.
  6. Coherencia bundle↔narrativa: hipótesis post-override citada en narrativa,
     sin "Pipeline error" cuando hay señales.
  7. Propiedad: INTENT/MALICE sellado ⇒ la narrativa contiene la hipótesis y
     al menos una señal citada.
"""
from __future__ import annotations

import pytest

from vigia.core.ebs_v1 import SignalOutput
from vigia.inference.abductive_reasoner import AbductiveReasoner

from vigia_agent import (
    VIGIAAgent,
    classify_agent_verdict,
    _signal_stats,
    _VERDICT_EXIT,
    EXIT_ABSTAIN,
    EXIT_INTENT,
)


def _sig(tool: str, z: float, artifact_type: str = None,
         signal_class: str = None, unanalyzed: bool = False,
         conf: float = 0.8) -> SignalOutput:
    meta = {}
    if artifact_type:
        meta["artifact_type"] = artifact_type
    if signal_class:
        meta["signal_class"] = signal_class
    if unanalyzed:
        meta["unanalyzed"] = True
    return SignalOutput(tool_name=tool, value=abs(z), z_score=z,
                        confidence=conf, metadata=meta or None)


def _sig_dict(tool: str, z: float, signal_class: str = None,
              unanalyzed: bool = False, conf: float = 0.8) -> dict:
    meta = {}
    if signal_class:
        meta["signal_class"] = signal_class
    if unanalyzed:
        meta["unanalyzed"] = True
    return {"tool": tool, "z_score": z, "confidence": conf,
            "value": abs(z), "metadata": meta}


# ──────────────────────────────────────────────────────────────────────────
# F9-1/F9-3 — el reasoner nunca crashea y siempre narra las tres capas (N1)
# ──────────────────────────────────────────────────────────────────────────

class TestReasonerNeverCrashes:
    @pytest.mark.parametrize("n", [3, 5, 10])
    def test_mixed_signals_no_crash_three_layers(self, n):
        # Mezcla de activas (z=3.2) e inactivas (z=0) — el patrón que antes
        # violaba INVARIANTE 4 en el 100% de las corridas con >=3 señales.
        signals = [
            _sig(f"TOOL{i}", 3.2 if i % 2 == 0 else 0.0, "registry")
            for i in range(n)
        ]
        trace = AbductiveReasoner().reason(signals)
        assert "Pipeline error" not in trace.peirce_narrative
        for layer in ("[FIRSTNESS]", "[SECONDNESS]", "[THIRDNESS]"):
            assert layer in trace.peirce_narrative, (
                f"capa {layer} ausente con n={n}: {trace.peirce_narrative}"
            )
        assert trace.best_hypothesis != "UNDETERMINED" or n < 3

    def test_all_zero_signals_yield_coherent_benign(self):
        signals = [_sig(f"T{i}", 0.0, "registry") for i in range(4)]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "NO_ANOMALY_DETECTED"
        assert "[THIRDNESS]" in trace.peirce_narrative
        # NO_ANOMALY con >=3 señales primarias y conclusivo → NOISE honesto.
        v = classify_agent_verdict(
            {"best_hypothesis": trace.best_hypothesis,
             "is_conclusive": trace.is_conclusive}, 4)
        assert v == "NOISE"

    def test_reasoner_is_reentrant_no_state_pollution(self):
        # N17: la misma instancia debe dar el mismo resultado en llamadas
        # sucesivas — antes selected_hypothesis/phase_log contaminaban.
        r = AbductiveReasoner()
        tie = [_sig("A", 3.0), _sig("B", 3.0), _sig("C", 0.0), _sig("D", 0.0)]
        active = [_sig(f"T{i}", 3.0, "registry") for i in range(5)]
        first = r.reason(tie).best_hypothesis
        r.reason(active)  # corrida intermedia con otro resultado
        second = r.reason(tie).best_hypothesis
        assert first == second == "ABSTAIN_V2"


# ──────────────────────────────────────────────────────────────────────────
# F9-2 — empate de CCS → ABSTAIN, nunca desempate lexicográfico (N2/N3)
# ──────────────────────────────────────────────────────────────────────────

class TestTieBreak:
    def test_exact_ccs_tie_yields_abstain_v2(self):
        # 2 activas / 2 inactivas → CCS 1/2 para ambas hipótesis.
        signals = [_sig("A", 3.0), _sig("B", 3.0), _sig("C", 0.0), _sig("D", 0.0)]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "ABSTAIN_V2", (
            "el empate debe abstener, no elegir H2-BENIGN por alfabeto"
        )
        assert not trace.is_conclusive

    def test_abstain_v2_maps_to_abstain_verdict(self):
        v = classify_agent_verdict({"best_hypothesis": "ABSTAIN_V2"}, 4)
        assert v == "ABSTAIN" and _VERDICT_EXIT[v] == EXIT_ABSTAIN

    def test_reasoner_error_maps_to_abstain_verdict(self):
        v = classify_agent_verdict({"best_hypothesis": "REASONER_ERROR"}, 4)
        assert v == "ABSTAIN"

    def test_h2_win_with_critical_signal_is_not_conclusive_noise(self):
        # Guard anti-swallow: mayoría quieta + 1 crítica z=3.5 → SUSPICION,
        # nunca NOISE conclusivo por dilución.
        signals = [_sig("A", 3.5, "mft")] + [
            _sig(f"Q{i}", 0.0, "registry") for i in range(4)
        ]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "SUSPICION_DETECTED"
        assert not trace.is_conclusive

    def test_two_critical_artifact_types_reach_malicious(self):
        # Gate Daubert: MALICIOUS requiere >=2 tipos de artefacto con z>3.
        signals = [
            _sig("MFT_ANALYZER", 3.5, "mft"),
            _sig("EVENT_LOG", 3.5, "windows_event_log"),
            _sig("REGISTRY_RTR", 2.0, "registry"),
        ]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "MALICIOUS_INTENT_DETECTED"

    def test_single_critical_type_caps_at_intent(self):
        signals = [_sig(f"T{i}", 3.5, "registry") for i in range(3)]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "INTENT_DETECTED"


# ──────────────────────────────────────────────────────────────────────────
# F9-4 — señales derivadas no cuentan para gates ni override (N4)
# ──────────────────────────────────────────────────────────────────────────

class TestDerivedSignalsDoNotCount:
    def test_one_primary_four_derived_is_insufficient(self):
        signals = [_sig("EVENT_LOG", 0.5, "windows_event_log")] + [
            _sig(f"D{i}", 3.5, signal_class="derived") for i in range(4)
        ]
        trace = AbductiveReasoner().reason(signals)
        assert trace.best_hypothesis == "UNDETERMINED"
        assert "primarias insuficientes" in trace.peirce_narrative.lower()
        v = classify_agent_verdict({"best_hypothesis": trace.best_hypothesis}, 1)
        assert v == "ABSTAIN"

    def test_derived_z_above_3_does_not_trigger_l036_override(self):
        # Caso VANKO: ADV_ROBUST (derivada) z=3.5 no puede fabricar INTENT.
        results = {
            "signals": [
                _sig_dict("EVENT_LOG", 0.0),
                _sig_dict("ADV_ROBUST", 3.5, signal_class="derived"),
                _sig_dict("CROSS_RESONANCE", 0.0, signal_class="derived"),
            ],
            "abduction": {"best_hypothesis": "UNDETERMINED",
                          "is_conclusive": False, "narrative": "x"},
            "results": {},
        }
        agent = VIGIAAgent("T-DERIVED", ".")
        agent._generate_narrative(results, "a" * 64)
        assert results["abduction"]["best_hypothesis"] == "UNDETERMINED", (
            "una señal derivada z>3 no debe disparar el override L-036"
        )
        v = classify_agent_verdict(
            results["abduction"], *_signal_stats(results))
        assert v == "ABSTAIN"

    def test_primary_z_above_3_does_trigger_l036_override(self):
        results = {
            "signals": [
                _sig_dict("MFT_ANALYZER", 3.5),
                _sig_dict("EVENT_LOG", 0.0),
                _sig_dict("ADV_ROBUST", 3.5, signal_class="derived"),
            ],
            "abduction": {"best_hypothesis": "UNDETERMINED",
                          "is_conclusive": False, "narrative": "x"},
            "results": {},
        }
        agent = VIGIAAgent("T-PRIMARY", ".")
        narrative = agent._generate_narrative(results, "a" * 64)
        assert results["abduction"]["best_hypothesis"] == "INTENT_DETECTED"
        assert "OVERRIDE L-036" in narrative

    def test_signal_stats_counts_only_primary(self):
        results = {
            "signals": [
                _sig_dict("A", 1.0),
                _sig_dict("B", 1.0, signal_class="derived"),
                _sig_dict("C", 0.0, unanalyzed=True),
            ],
            "results": {"unanalyzed_artifacts": ["amcache", "usb"]},
        }
        n_primary, n_unanalyzed = _signal_stats(results)
        assert n_primary == 1
        assert n_unanalyzed == 2


# ──────────────────────────────────────────────────────────────────────────
# F9-5 — mobile: veredicto por señal, no etiqueta fija (N5/N6)
# ──────────────────────────────────────────────────────────────────────────

class TestMobileVerdicts:
    def test_mobile_critical_signal_is_not_noise(self):
        from sift_orchestrator import _mobile_hypothesis
        hyp, max_z, concl, n_crit = _mobile_hypothesis([{"z_score": 4.0}])
        assert hyp == "INTENT_DETECTED"
        v = classify_agent_verdict(
            {"best_hypothesis": hyp, "is_conclusive": concl}, 1)
        assert v == "INTENT" and _VERDICT_EXIT[v] == EXIT_INTENT

    def test_two_critical_mobile_signals_reach_malicious(self):
        from sift_orchestrator import _mobile_hypothesis
        hyp, _, _, _ = _mobile_hypothesis([{"z_score": 4.0}, {"z_score": 3.5}])
        assert hyp == "MALICIOUS_INTENT_DETECTED"

    def test_clean_mobile_single_source_abstains_not_noise(self):
        # 1 señal limpia = fuente única sin corroboración → ABSTAIN honesto,
        # no NOISE ("analizado y limpio" requiere base).
        from sift_orchestrator import _mobile_hypothesis
        hyp, _, concl, _ = _mobile_hypothesis([{"z_score": 0.4}])
        assert hyp == "MOBILE_EVIDENCE_ANALYZED"
        assert concl is False
        v = classify_agent_verdict(
            {"best_hypothesis": hyp, "is_conclusive": concl}, 1)
        assert v == "ABSTAIN"

    def test_merge_escalates_benign_windows_verdict_on_mobile_critical(self):
        # N6: evidencia mixta — hallazgo mobile z>3 no puede quedar silenciado
        # por una abducción benigna computada antes del merge.
        from sift_orchestrator import SIFTOrchestrator
        result = {
            "case_id": "T-MIX",
            "signals": [],
            "abduction": {"best_hypothesis": "NO_ANOMALY_DETECTED",
                          "is_conclusive": True, "narrative": "clean"},
            "pipeline_meta": {"n_total_signals": 0},
        }
        mobile = [{"tool": "ANDROID_FORENSICS", "z_score": 4.2,
                   "confidence": 0.9, "value": 4.2,
                   "metadata": {"signal_class": "primary"}}]
        merged = SIFTOrchestrator._merge_mobile_signals(result, mobile)
        assert merged["abduction"]["best_hypothesis"] == "INTENT_DETECTED"
        assert "[MOBILE]" in merged["abduction"]["narrative"]
        assert merged["abduction"]["mobile_escalation"]["from"] == "NO_ANOMALY_DETECTED"

    def test_merge_does_not_downgrade_existing_malice(self):
        from sift_orchestrator import SIFTOrchestrator
        result = {
            "case_id": "T-MAL",
            "signals": [],
            "abduction": {"best_hypothesis": "MALICIOUS_INTENT_DETECTED",
                          "is_conclusive": True, "narrative": "evil"},
            "pipeline_meta": {"n_total_signals": 0},
        }
        mobile = [{"tool": "IOS_FORENSICS", "z_score": 4.0,
                   "confidence": 0.9, "value": 4.0, "metadata": {}}]
        merged = SIFTOrchestrator._merge_mobile_signals(result, mobile)
        assert merged["abduction"]["best_hypothesis"] == "MALICIOUS_INTENT_DETECTED"
        assert "mobile_escalation" not in merged["abduction"]


# ──────────────────────────────────────────────────────────────────────────
# F9-6/F9-7 — coherencia narrativa ↔ bundle sellado (N10)
# ──────────────────────────────────────────────────────────────────────────

class TestNarrativeBundleCoherence:
    def _agent_results_reasoner_error(self):
        # El estado que antes producía "[FIRSTNESS] Pipeline error." + exit 3
        # con narrativa stale UNDETERMINED (síntoma raíz de la auditoría).
        return {
            "signals": [
                _sig_dict("MFT_ANALYZER", 3.5),
                _sig_dict("EVENT_LOG", 1.0),
                _sig_dict("ADV_ROBUST", 3.5, signal_class="derived"),
            ],
            "abduction": {
                "best_hypothesis": "REASONER_ERROR",
                "is_conclusive": False,
                "best_posterior": "0",
                "narrative": (
                    "[FIRSTNESS] 3 señales recibidas (2 primarias) — extracción completada.\n"
                    "[SECONDNESS] Error en pipeline v2: AssertionError: INVARIANTE 4.\n"
                    "[THIRDNESS] Sin inferencia abductiva."
                ),
                "reasoner_error": "AssertionError: INVARIANTE 4",
            },
            "results": {},
        }

    def test_no_pipeline_error_string_and_hypothesis_in_narrative(self):
        agent = VIGIAAgent("T-COHER", ".")
        results = self._agent_results_reasoner_error()
        narrative = agent._generate_narrative(results, "a" * 64)
        assert "Pipeline error" not in narrative
        # F3: la hipótesis citada en la narrativa es la POST-override.
        final_hyp = results["abduction"]["best_hypothesis"]
        assert final_hyp == "INTENT_DETECTED"  # override sobre REASONER_ERROR
        assert final_hyp in narrative
        assert "OVERRIDE L-036" in narrative

    def test_sealed_verdict_matches_narrative_hypothesis(self):
        agent = VIGIAAgent("T-SEAL", ".")
        results = self._agent_results_reasoner_error()
        narrative = agent._generate_narrative(results, "a" * 64)
        bundle, _text, _digest = agent._seal_bundle(results, narrative, "a" * 64)
        assert bundle["agent_verdict"] == "INTENT"
        assert bundle["pipeline_results"]["abduction"]["best_hypothesis"] in narrative

    def test_property_intent_or_malice_narrative_cites_evidence(self):
        # F9-7: todo bundle INTENT/MALICE debe citar hipótesis + >=1 señal.
        agent = VIGIAAgent("T-PROP", ".")
        for zs in ([3.5, 3.5, 1.0], [3.2, 0.0, 0.0]):
            results = {
                "signals": [_sig_dict(f"TOOL{i}", z) for i, z in enumerate(zs)],
                "abduction": {"best_hypothesis": "UNDETERMINED",
                              "is_conclusive": False, "narrative": "n/a"},
                "results": {},
            }
            narrative = agent._generate_narrative(results, "b" * 64)
            bundle, _t, _d = agent._seal_bundle(results, narrative, "b" * 64)
            if bundle["agent_verdict"] in ("INTENT", "MALICE"):
                assert results["abduction"]["best_hypothesis"] in narrative
                assert "TOP SIGNALS" in narrative
                assert any(f"TOOL{i}" in narrative for i in range(len(zs)))

    def test_unanalyzed_artifacts_surface_in_narrative_and_verdict(self):
        # F7 (N8): NOISE + artefactos no analizados → ABSTAIN, y la sección
        # de no-analizados aparece en la narrativa.
        agent = VIGIAAgent("T-UNAN", ".")
        results = {
            "signals": [_sig_dict(f"T{i}", 0.2) for i in range(4)],
            "abduction": {"best_hypothesis": "NO_ANOMALY_DETECTED",
                          "is_conclusive": True, "narrative": "clean"},
            "results": {"unanalyzed_artifacts": ["amcache", "pathguard_reject"]},
        }
        narrative = agent._generate_narrative(results, "c" * 64)
        assert "ARTEFACTOS NO ANALIZADOS" in narrative
        assert "amcache" in narrative
        v = classify_agent_verdict(results["abduction"], *_signal_stats(results))
        assert v == "ABSTAIN", "limpio con pérdidas de análisis no es NOISE"

    def test_caie_error_surfaces_in_narrative(self):
        # F8 (N9): CAIE status=ERROR era invisible.
        agent = VIGIAAgent("T-CAIE", ".")
        results = {
            "signals": [_sig_dict("A", 1.0)],
            "abduction": {"best_hypothesis": "SUSPICION_DETECTED",
                          "is_conclusive": False, "narrative": "x"},
            "results": {"caie": {"status": "ERROR", "error": "boom"}},
        }
        narrative = agent._generate_narrative(results, "d" * 64)
        assert "CAIE" in narrative and "ERROR" in narrative


# ──────────────────────────────────────────────────────────────────────────
# End-to-end orquestador V4: la narrativa nunca es "Pipeline error"
# ──────────────────────────────────────────────────────────────────────────

class TestOrchestratorV4Narrative:
    def test_empty_run_narrates_insufficient_not_pipeline_error(self):
        from vigia.sift.sift_orchestrator import SIFTOrchestrator as V4
        result = V4("T-V4-EMPTY").run_full_analysis()
        narrative = result["abduction"]["narrative"]
        assert "Pipeline error" not in narrative
        assert "[FIRSTNESS]" in narrative
        assert result["abduction"]["best_hypothesis"] == "UNDETERMINED"
        assert result["pipeline_meta"]["n_primary_signals"] == 0

    def test_reasoner_hard_crash_produces_detailed_narrative(self, monkeypatch):
        # Segunda red (F2): si reason() mismo explota, el orquestador narra
        # el error con tipo+mensaje y marca REASONER_ERROR.
        from vigia.sift.sift_orchestrator import SIFTOrchestrator as V4
        orch = V4("T-V4-CRASH")

        def _boom(signals):
            raise RuntimeError("synthetic reasoner crash")
        monkeypatch.setattr(orch.reasoner, "reason", _boom)
        result = orch.run_full_analysis()
        ab = result["abduction"]
        assert ab["best_hypothesis"] == "REASONER_ERROR"
        assert "RuntimeError" in ab["narrative"]
        assert "synthetic reasoner crash" in ab["narrative"]
        assert "Pipeline error" not in ab["narrative"]
        assert result["results"]["reasoner_error"].startswith("RuntimeError")
        # Y clasifica ABSTAIN, nunca benigno:
        v = classify_agent_verdict(ab, 0)
        assert v == "ABSTAIN"


# ──────────────────────────────────────────────────────────────────────────
# B-052 P1 — narrativa mobile honesta (AUDITORIA_MACOS_NARRATIVA.md §4)
# ──────────────────────────────────────────────────────────────────────────

class TestB052MobileNarrative:
    def _mobile_only_result(self, monkeypatch, mobile):
        from sift_orchestrator import SIFTOrchestrator
        orch = SIFTOrchestrator("T-B052")
        monkeypatch.setattr(orch, "_analyze_mobile", lambda kw: mobile)
        # macos_evidence_path no está en la lista has_windows_evidence →
        # rama mobile-only.
        return orch.analyze(macos_evidence_path="/evidence/macos")

    def test_narrative_declares_reasoner_not_run_by_design(self, monkeypatch):
        mobile = [{
            "tool": "MACOS_FORENSICS", "z_score": 1.6, "confidence": 0.95,
            "value": 0.32,
            "metadata": {"signal_class": "primary", "findings_count": 23,
                         "finding_types": ["SAFARI_SUSPICIOUS"]},
        }]
        result = self._mobile_only_result(monkeypatch, mobile)
        narr = result["abduction"]["narrative"]
        for layer in ("[FIRSTNESS]", "[SECONDNESS]", "[THIRDNESS]"):
            assert layer in narr
        # La ausencia del reasoner se declara como diseño, no como error.
        assert "Motor abductivo v2: NO ejecutado" in narr
        assert "B-052" in narr
        assert "Pipeline error" not in narr
        # FIRSTNESS enriquecido con los hallazgos reales del engine.
        assert "23 finding(s)" in narr
        assert "SAFARI_SUSPICIOUS" in narr
        # Estado consultable en pipeline_meta.
        assert result["pipeline_meta"]["abductive_reasoner"] == \
            "NOT_RUN_MOBILE_SINGLE_SOURCE"

    def test_narrative_without_findings_metadata_still_complete(self, monkeypatch):
        # Señal mobile sin findings_count (engines viejos / metadata parcial):
        # la narrativa no debe romperse ni inventar hallazgos.
        mobile = [{"tool": "IOS_FORENSICS", "z_score": 4.0, "confidence": 0.9,
                   "value": 4.0, "metadata": {"signal_class": "primary"}}]
        result = self._mobile_only_result(monkeypatch, mobile)
        narr = result["abduction"]["narrative"]
        assert "Hallazgos:" not in narr
        assert "Motor abductivo v2: NO ejecutado" in narr
        # F6 intacto: z=4 → INTENT, no NOISE.
        assert result["abduction"]["best_hypothesis"] == "INTENT_DETECTED"

    def test_verdict_and_scoring_unchanged_by_p1(self, monkeypatch):
        # P1 es solo presentación: hipótesis/posterior idénticos a F6.
        mobile = [{"tool": "MACOS_FORENSICS", "z_score": 1.6, "confidence": 0.95,
                   "value": 0.32, "metadata": {"signal_class": "primary"}}]
        result = self._mobile_only_result(monkeypatch, mobile)
        ab = result["abduction"]
        assert ab["best_hypothesis"] == "MOBILE_EVIDENCE_ANALYZED"
        assert ab["is_conclusive"] is False
        assert ab["best_posterior"] == "8/25"  # 1.6/5 — igual que pre-P1


# ─────────────────────────────────────────────────────────────────────────────
# B-088 / B-089 / B-090 — hallazgos huérfanos de AUDITORIA_PIPELINE_ROBUSTEZ
# (N13, N14, P2-E) verificados contra HEAD 2026-07-10.
# ─────────────────────────────────────────────────────────────────────────────

class TestB088AccuracyValidationSourceAlias:
    """B-088 (N13): los adaptadores del shim (vol3, EBS-JSON, mobile) emiten
    `source` en lugar de `tool`; el flag sans_compliance.accuracy_validation
    debe aceptar ambos (F8). Pin de regresión — el fix ya estaba en HEAD;
    este test lo fija para que no se revierta."""

    def test_accepts_source_alias(self):
        from vigia_agent import _accuracy_validation
        assert _accuracy_validation(
            [{"source": "vol3_adapter", "z_score": 1.2}]) is True

    def test_accepts_native_tool_field(self):
        from vigia_agent import _accuracy_validation
        assert _accuracy_validation(
            [{"tool": "MEMORY_FORENSICS", "z_score": 0.0}]) is True

    def test_mixed_adapter_and_native_signals(self):
        from vigia_agent import _accuracy_validation
        assert _accuracy_validation(
            [{"source": "ebs_json", "z_score": 0.4},
             {"tool": "BROWSER_FORENSICS", "z_score": 1.1}]) is True

    def test_fails_closed_without_tool_or_zscore(self):
        from vigia_agent import _accuracy_validation
        assert _accuracy_validation([]) is False
        assert _accuracy_validation([{"z_score": 1.2}]) is False
        assert _accuracy_validation([{"source": "x"}]) is False


class TestB089ToSignalCrashVisible:
    """B-089 (N14): una excepción en to_signal() no puede hacer desaparecer
    el artefacto en silencio. F8 ya contabilizaba el drop en pipeline_meta;
    el fix completo emite además la señal sintética *_UNANALYZED (mismo
    mecanismo F7) para que el artefacto entre en n_unanalyzed_artifacts y
    en la sección de la narrativa. Test escrito ROJO contra el HEAD que
    retornaba None a secas."""

    class _Boom:
        def to_signal(self):
            raise RuntimeError("kaputt")

    def _orch(self):
        from vigia.sift.sift_orchestrator import SIFTOrchestrator
        return SIFTOrchestrator(case_id="B089-TEST")

    def test_crash_yields_unanalyzed_signal_not_none(self):
        orch = self._orch()
        sig = orch._to_signal_safe(self._Boom(), "memory")
        assert sig is not None, (
            "to_signal() crash devolvió None — el artefacto desaparece "
            "del bundle sin marca unanalyzed (B-089/N14)"
        )
        assert sig.metadata.get("unanalyzed") is True
        assert sig.metadata.get("signal_class") == "derived"
        assert sig.z_score == 0.0 and sig.confidence == 0.0
        assert sig.tool_name == "MEMORY_UNANALYZED"

    def test_crash_still_counts_in_signal_drops(self):
        # F8 se conserva: ambos mecanismos, contador + señal visible.
        orch = self._orch()
        orch._to_signal_safe(self._Boom(), "registry")
        assert any("registry" in d for d in orch._signal_drops)

    def test_unanalyzed_signal_never_counts_as_primary(self):
        # La señal sintética no puede inflar el gate <3 (invariante F5/F7).
        from vigia_agent import _is_primary_signal
        orch = self._orch()
        sig = orch._to_signal_safe(self._Boom(), "memory")
        assert _is_primary_signal({"metadata": sig.metadata}) is False

    def test_healthy_result_path_unchanged(self):
        orch = self._orch()
        healthy = type("R", (), {"to_signal": lambda self: _sig(
            "MEMORY_FORENSICS", 2.0, artifact_type="memory")})()
        sig = orch._to_signal_safe(healthy, "memory")
        assert sig is not None and sig.tool_name == "MEMORY_FORENSICS"
        assert not sig.metadata.get("unanalyzed")
        assert orch._signal_drops == []

    def test_derived_conversion_crash_does_not_emit_stub(self):
        # Doctrina F7: los crashes de motores DERIVADOS (síntesis sobre
        # señales ya emitidas) no marcan artefactos sin analizar — "falló
        # una síntesis" no es "evidencia sin analizar" y no puede degradar
        # NOISE→ABSTAIN. El drop sí se contabiliza (F8).
        orch = self._orch()
        for engine in ("timeline", "resonance", "metabolic",
                       "behavioral", "patterns", "adversarial"):
            assert orch._to_signal_safe(self._Boom(), engine) is None, engine
        assert len(orch._signal_drops) == 6


class TestB090EmptyTimelineExcludedFromGates:
    """B-090 (P2-E): UNIFIED_TIMELINE emite señal derivada aun con
    timestamps=0. Verificado contra HEAD: la señal SÍ se emite (z=0), pero
    el wiring la marca signal_class=derived (F5) y _is_primary_signal la
    excluye del gate <3 y del override L-036. Cerrado como RESUELTO-por-F5;
    este pin reproduce el caso exacto de la auditoría para que el tag no se
    pierda en el wiring."""

    def _empty_timeline_signal(self):
        from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine
        from vigia.sift.sift_orchestrator import SIFTOrchestrator
        sigs = [_sig("MEMORY_FORENSICS", 2.0), _sig("BROWSER_FORENSICS", 1.0)]
        tl = UnifiedTimelineEngine().build_timeline(sigs)  # sin timestamps
        return SIFTOrchestrator._mark_derived(tl.to_signal())

    def test_empty_timeline_is_emitted_but_derived(self):
        sig = self._empty_timeline_signal()
        assert sig is not None
        assert sig.metadata.get("signal_class") == "derived"

    def test_empty_timeline_never_counts_as_primary(self):
        from vigia_agent import _is_primary_signal
        sig = self._empty_timeline_signal()
        assert _is_primary_signal({"metadata": sig.metadata}) is False

    def test_counterfactual_without_f5_tag_would_count(self):
        # Documenta POR QUÉ el tag es imprescindible: sin él, la timeline
        # vacía contaría como primaria (el hueco que P2-E temía).
        from vigia_agent import _is_primary_signal
        assert _is_primary_signal(
            {"metadata": {"artifact_type": "timeline"}}) is True

    def test_signal_stats_gate_excludes_empty_timeline(self):
        # Gate real: 2 primarias + timeline vacía derivada = n_primary 2 (<3).
        sig = self._empty_timeline_signal()
        results = {"signals": [
            _sig_dict("MEMORY_FORENSICS", 2.0),
            _sig_dict("BROWSER_FORENSICS", 1.0),
            {"tool": "UNIFIED_TIMELINE", "z_score": sig.z_score,
             "metadata": sig.metadata},
        ]}
        n_primary, _ = _signal_stats(results)
        assert n_primary == 2

    def test_none_metadata_signal_does_not_crash_timeline(self):
        # B-108 (ex B-093, renumerado 2026-07-11; hallazgo adyacente en la reproducción de B-090):
        # metadata=None es legal en SignalOutput; sin el guard, UNA señal sin
        # metadata crasheaba build_timeline entero y el wiring tragaba el
        # error — la timeline desaparecía del bundle en silencio. Test
        # escrito ROJO contra el engine sin guard.
        from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine
        sigs = [
            SignalOutput(tool_name="MEMORY_FORENSICS", value=0.4,
                         z_score=2.0, confidence=0.7, metadata=None),
            _sig("BROWSER_FORENSICS", 1.0, artifact_type="browser"),
        ]
        tl = UnifiedTimelineEngine().build_timeline(sigs)
        sig = tl.to_signal()
        assert sig is not None
        assert sig.metadata.get("total_events") == 2

    def test_int_epoch_timestamp_does_not_crash_timeline(self):
        # B-130: Prefetch/Registry metadata carries epoch timestamps as int,
        # not ISO strings.  metadata.get("timestamp") returns the int AS-IS
        # (the default only applies when the key is absent).  Passing an int
        # to _parse_iso_timestamp raised AttributeError (no .replace()) —
        # not caught by the ValueError except, so build_timeline crashed and
        # was silently swallowed by the orchestrator's outer except, removing
        # one evidence source from the verdict.
        # Confirmed in VIGIA-REAL-VANKO-2026 corrida RAW 2026-07-14.
        from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine
        sigs = [
            SignalOutput(
                tool_name="PREFETCH_ANALYZER",
                value=0.5,
                z_score=2.5,
                confidence=0.8,
                metadata={"artifact_type": "prefetch", "timestamp": 1700000000},
            ),
            SignalOutput(
                tool_name="REGISTRY_RTR",
                value=0.3,
                z_score=1.5,
                confidence=0.7,
                metadata={"artifact_type": "registry", "timestamp": 1700003600},
            ),
        ]
        tl = UnifiedTimelineEngine().build_timeline(sigs)
        sig = tl.to_signal()
        assert sig is not None, "build_timeline must not crash on int timestamps"
        assert sig.metadata.get("total_events") == 2
        # Both events must land at the correct epoch value, not 0 (fallback).
        assert tl.timeline[0].timestamp == 1700000000
        assert tl.timeline[1].timestamp == 1700003600

    def test_float_epoch_timestamp_does_not_crash_timeline(self):
        # B-130 extension: float epoch (e.g. from json.load of a real bundle)
        # must also be handled without crash and truncated to int.
        from vigia.sift.unified_timeline_engine import UnifiedTimelineEngine
        sigs = [
            SignalOutput(
                tool_name="EVENT_LOG",
                value=0.4,
                z_score=2.0,
                confidence=0.75,
                metadata={"artifact_type": "eventlog", "timestamp": 1700000000.5},
            ),
        ]
        tl = UnifiedTimelineEngine().build_timeline(sigs)
        assert tl.total_events == 1
        assert tl.timeline[0].timestamp == 1700000000


class TestShimMobileUnanalyzed:
    """B-089 alcance restante (N14, superficie shim): un crash de un analyzer
    mobile en /sift_orchestrator.py::_analyze_mobile hacía desaparecer TODA la
    evidencia mobile sin marca — el caso caía al orquestador real con 0
    señales y sellaba n_unanalyzed_artifacts=0 (medido pre-fix: verdict
    UNDETERMINED, "0 artefactos sin analizar" con el 100% de la evidencia sin
    analizar). Tests escritos ROJOS contra el shim log-only.

    Doctrina: el marcador es dict (formato de señal del shim), z=0,
    unanalyzed=True, signal_class=derived — visible en el bundle y en
    n_unanalyzed_artifacts, invisible para los gates. El veredicto NO cambia
    (ABSTAIN en ambos mundos); cambia la trazabilidad de la pérdida (§5.3).
    """

    def _shim(self):
        import importlib, sift_orchestrator as shim_mod
        return shim_mod.SIFTOrchestrator(case_id="N14-SHIM-TEST")

    def _crash_macos(self):
        from unittest.mock import patch
        return patch(
            "vigia.sift.macos_forensics.MacOSForensicsAnalyzer.analyze",
            side_effect=RuntimeError("kaputt"),
        )

    def test_mobile_crash_emits_unanalyzed_marker(self):
        with self._crash_macos():
            r = self._shim().analyze(macos_evidence_path="cases/tuck-2019-macos")
        markers = [s for s in r.get("signals", [])
                   if (s.get("metadata") or {}).get("unanalyzed")]
        assert markers, (
            "crash del analyzer macOS no dejó marcador — la evidencia "
            "mobile desapareció del bundle (N14 superficie shim)"
        )
        m = markers[0]
        assert m["tool"] == "MACOS_UNANALYZED"
        assert m["z_score"] == 0.0
        assert m["metadata"]["signal_class"] == "derived"
        assert "kaputt" in m["metadata"]["error"]

    def test_mobile_crash_counts_in_signal_stats(self):
        # El marcador debe llegar a n_unanalyzed_artifacts vía la misma vía
        # que el orquestador real (results.unanalyzed_artifacts).
        with self._crash_macos():
            r = self._shim().analyze(macos_evidence_path="cases/tuck-2019-macos")
        n_primary, n_unanalyzed = _signal_stats(r)
        assert n_primary == 0
        assert n_unanalyzed >= 1, (
            f"n_unanalyzed={n_unanalyzed} — el bundle vuelve a afirmar '0 "
            f"artefactos sin analizar' con toda la evidencia sin analizar"
        )

    def test_mobile_crash_verdict_stays_abstain(self):
        # Invariante del fix: NO cambia el veredicto (era ABSTAIN vía
        # UNDETERMINED con 0 señales; sigue ABSTAIN) — solo la trazabilidad.
        with self._crash_macos():
            r = self._shim().analyze(macos_evidence_path="cases/tuck-2019-macos")
        n_primary, n_unanalyzed = _signal_stats(r)
        v = classify_agent_verdict(r.get("abduction", {}), n_primary, n_unanalyzed)
        assert v == "ABSTAIN"

    def test_mobile_crash_narrative_mentions_loss(self):
        with self._crash_macos():
            r = self._shim().analyze(macos_evidence_path="cases/tuck-2019-macos")
        narrative = str(r.get("abduction", {}).get("narrative", ""))
        assert "[FIRSTNESS-LOSS]" in narrative, (
            "la narrativa no menciona la pérdida de evidencia mobile"
        )
        # Sin contradicción clase N12: el marcador NO puede contarse como
        # señal extraída ni listarse como engine que analizó.
        assert "0 señales mobile analizadas" in narrative
        assert "engines: MACOS_UNANALYZED" not in narrative

    def test_healthy_mobile_has_no_marker(self):
        r = self._shim().analyze(macos_evidence_path="cases/tuck-2019-macos")
        markers = [s for s in r.get("signals", [])
                   if (s.get("metadata") or {}).get("unanalyzed")]
        assert markers == []
        n_primary, n_unanalyzed = _signal_stats(r)
        assert n_primary == 1 and n_unanalyzed == 0

    def test_mixed_path_merge_carries_marker(self, tmp_path):
        # Camino mixto: EBS-JSON + crash mobile → el marcador sobrevive el
        # merge y n_unanalyzed lo ve.
        import json as _json
        case = {"case_id": "N14-MIX", "artifacts": [{
            "artifact_id": "A1", "evidence_type": "log_entry",
            "source_tool": "t", "description": "d", "raw_score": 0.4,
            "prior_trust": 0.8, "timestamp": "2026-01-01T00:00:00Z",
            "provenance_chain": ["acq"], "metadata": {},
        }]}
        p = tmp_path / "case.json"
        p.write_text(_json.dumps(case))
        with self._crash_macos():
            r = self._shim().analyze(
                log_path=str(p), macos_evidence_path="cases/tuck-2019-macos")
        markers = [s for s in r.get("signals", [])
                   if (s.get("metadata") or {}).get("unanalyzed")]
        assert markers and markers[0]["tool"] == "MACOS_UNANALYZED"
        _, n_unanalyzed = _signal_stats(r)
        assert n_unanalyzed >= 1

    def test_marker_never_triggers_mobile_escalation(self):
        # z=0: el marcador no puede disparar la escalación del merge (>3).
        import sift_orchestrator as shim_mod
        marker = shim_mod._unanalyzed_marker("macos", RuntimeError("x"))
        base = {"signals": [], "abduction": {"best_hypothesis": "NO_ANOMALY_DETECTED"},
                "pipeline_meta": {}}
        merged = shim_mod.SIFTOrchestrator._merge_mobile_signals(base, [marker])
        assert merged["abduction"]["best_hypothesis"] == "NO_ANOMALY_DETECTED"
        assert "mobile_escalation" not in merged["abduction"]
