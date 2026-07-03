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
