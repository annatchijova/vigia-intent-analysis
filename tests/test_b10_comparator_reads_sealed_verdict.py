"""
B10 (recomendación B-058) — el comparador batch DEBE leer el `agent_verdict`
SELLADO del bundle, no re-derivarlo heurísticamente desde `best_hypothesis`.

Método abductivo:
  Hipótesis  : `extract_verdict_from_bundle` re-deriva el veredicto vía un mapeo
               + prefix-matching sobre `best_hypothesis` / el AGENT_EXIT del
               audit_trail, ambos PRE-gate. El campo top-level `agent_verdict`
               es el veredicto POST-gate — la auto-corrección pre-emisión de
               VIGÍA (classify_agent_verdict, el "camino único que sella
               agent_verdict y decide el exit", CLAUDE.md). Cuando el gate ajusta
               el veredicto del reasoner, las dos fuentes divergen y el
               comparador reporta el equivocado.
  Deducción  : un bundle con `agent_verdict="INTENT"` sellado pero
               `best_hypothesis="SUSPICION_DETECTED"` (forma REAL medida en
               results/agent_batch/VIGIA-FN-001) debe reportarse INTENT.
  Inducción  : medido sobre el corpus sellado — 60/209 bundles divergían
               (sealed=INTENT→SUSPICION, sealed=ABSTAIN/NOISE→UNKNOWN) antes de
               este fix.

Invariante de compatibilidad: los bundles legacy SIN `agent_verdict` (medidos:
82/291) deben seguir resolviéndose por la heurística previa, byte por byte.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import run_all_agent as R


def _write(tmp_path: Path, bundle: dict) -> Path:
    p = tmp_path / "case_agent_bundle.json"
    p.write_text(json.dumps(bundle))
    return p


# ── El defecto: sellado post-gate ≠ best_hypothesis pre-gate ────────────────

class TestReadsSealedVerdict:
    def test_sealed_intent_over_pregate_suspicion(self, tmp_path):
        """Forma real de VIGIA-FN-001: sellado INTENT, reasoner SUSPICION."""
        p = _write(tmp_path, {
            "agent_verdict": "INTENT",
            "audit_trail": {"entries": [
                {"action": "AGENT_EXIT",
                 "inputs_summary": {"verdict": "SUSPICION_DETECTED"}}]},
            "pipeline_results": {"abduction": {
                "best_hypothesis": "SUSPICION_DETECTED"}},
        })
        # Antes del fix: el paso 1 (AGENT_EXIT) devolvía SUSPICION.
        assert R.extract_verdict_from_bundle(p) == "INTENT"

    def test_sealed_abstain_over_unknown_fallthrough(self, tmp_path):
        """sealed=ABSTAIN pero sin best_hypothesis mapeable → heurística caía a
        UNKNOWN (forma real de VIGIA-MAGNET-2014-MULTIDEVICE)."""
        p = _write(tmp_path, {
            "agent_verdict": "ABSTAIN",
            "audit_trail": {"entries": []},
            "pipeline_results": {"abduction": {"best_hypothesis": ""}},
        })
        assert R.extract_verdict_from_bundle(p) == "ABSTAIN"

    def test_sealed_noise_over_unknown_fallthrough(self, tmp_path):
        p = _write(tmp_path, {
            "agent_verdict": "NOISE",
            "audit_trail": {"entries": []},
            "pipeline_results": {"abduction": {"best_hypothesis": ""}},
        })
        assert R.extract_verdict_from_bundle(p) == "NOISE"

    def test_sealed_verdict_is_canonicalized_through_map(self, tmp_path):
        """Un sellado con vocabulario del agente (BENIGN) se normaliza igual que
        cualquier otra fuente: BENIGN → NOISE."""
        p = _write(tmp_path, {
            "agent_verdict": "BENIGN",
            "audit_trail": {"entries": []},
            "pipeline_results": {"abduction": {"best_hypothesis": ""}},
        })
        assert R.extract_verdict_from_bundle(p) == "NOISE"


# ── Invariante de compatibilidad: bundles legacy sin sellado ────────────────

class TestLegacyFallbackUnchanged:
    def test_legacy_no_sealed_field_uses_agent_exit(self, tmp_path):
        """Sin `agent_verdict`: cae al AGENT_EXIT del audit_trail (paso 1)."""
        p = _write(tmp_path, {
            "audit_trail": {"entries": [
                {"action": "AGENT_EXIT",
                 "inputs_summary": {"verdict": "MALICIOUS_INTENT_DETECTED"}}]},
            "pipeline_results": {"abduction": {
                "best_hypothesis": "MALICIOUS_INTENT_DETECTED"}},
        })
        assert R.extract_verdict_from_bundle(p) == "MALICE"

    def test_legacy_no_sealed_field_uses_best_hypothesis(self, tmp_path):
        """Sin sellado ni AGENT_EXIT: cae a best_hypothesis (paso 2)."""
        p = _write(tmp_path, {
            "audit_trail": {"entries": []},
            "pipeline_results": {"abduction": {
                "best_hypothesis": "SUSPICION_DETECTED"}},
        })
        assert R.extract_verdict_from_bundle(p) == "SUSPICION"

    def test_legacy_no_sealed_field_prefix_match(self, tmp_path):
        """Sin sellado, best_hypothesis no en _MAP: prefix matching (paso 3)."""
        p = _write(tmp_path, {
            "audit_trail": {"entries": []},
            "pipeline_results": {"abduction": {
                "best_hypothesis": "MALICIOUS_WEIRD_VARIANT"}},
        })
        assert R.extract_verdict_from_bundle(p) == "MALICE"

    def test_null_sealed_field_treated_as_legacy(self, tmp_path):
        """agent_verdict presente pero None (no un string canónico) → legacy."""
        p = _write(tmp_path, {
            "agent_verdict": None,
            "audit_trail": {"entries": [
                {"action": "AGENT_EXIT",
                 "inputs_summary": {"verdict": "NO_THREAT_DETECTED"}}]},
            "pipeline_results": {"abduction": {"best_hypothesis": ""}},
        })
        assert R.extract_verdict_from_bundle(p) == "NOISE"

    def test_unmapped_sealed_value_falls_back_not_crash(self, tmp_path):
        """Un sellado con vocabulario desconocido no debe romper: cae a la
        heurística en vez de propagar un valor no canónico."""
        p = _write(tmp_path, {
            "agent_verdict": "SOME_FUTURE_VERDICT",
            "audit_trail": {"entries": [
                {"action": "AGENT_EXIT",
                 "inputs_summary": {"verdict": "SUSPICION_DETECTED"}}]},
            "pipeline_results": {"abduction": {"best_hypothesis": ""}},
        })
        assert R.extract_verdict_from_bundle(p) == "SUSPICION"


def test_corrupt_bundle_still_error(tmp_path):
    p = tmp_path / "corrupt_agent_bundle.json"
    p.write_text("{not valid json")
    assert R.extract_verdict_from_bundle(p) == "ERROR"


# ── Segunda ubicación del mismo defecto (code-review, altitud) ──────────────
# run_llm_cases._fallback_verdict leía best_hypothesis (pre-gate) del bundle
# sellado en vez del agent_verdict sellado (post-gate) — misma clase que B10.

class TestLlmFallbackReadsSealedVerdict:
    @pytest.fixture(autouse=True)
    def _requires_mcp(self):
        # L-045: run_llm_cases imports the bridge, which imports `mcp` —
        # not installable in minimal CI environments; skip there (B-138).
        pytest.importorskip("mcp.server.fastmcp")

    def _bundle(self, tmp_path, case_id, body):
        (tmp_path / f"{case_id}_agent_bundle.json").write_text(json.dumps(body))

    def test_fallback_prefers_sealed_over_best_hypothesis(self, tmp_path, monkeypatch):
        import run_llm_cases as L
        monkeypatch.setattr(L, "AGENT_DIR", tmp_path)
        self._bundle(tmp_path, "C1", {
            "agent_verdict": "INTENT",
            "pipeline_results": {"abduction": {
                "best_hypothesis": "SUSPICION_DETECTED"}},
        })
        # sellado INTENT → _HYP_MAP['INTENT']='MALICE' (bucketing propio del
        # harness LLM). Antes del fix devolvía SUSPICION (best_hypothesis).
        assert L._fallback_verdict("C1") == "MALICE"

    def test_fallback_legacy_uses_best_hypothesis(self, tmp_path, monkeypatch):
        import run_llm_cases as L
        monkeypatch.setattr(L, "AGENT_DIR", tmp_path)
        self._bundle(tmp_path, "C2", {
            "pipeline_results": {"abduction": {
                "best_hypothesis": "SUSPICION_DETECTED"}},
        })
        assert L._fallback_verdict("C2") == "SUSPICION"

    def test_fallback_missing_bundle_unknown(self, tmp_path, monkeypatch):
        import run_llm_cases as L
        monkeypatch.setattr(L, "AGENT_DIR", tmp_path)
        assert L._fallback_verdict("NOPE") == "UNKNOWN"

    def test_fallback_unmapped_sealed_falls_back(self, tmp_path, monkeypatch):
        import run_llm_cases as L
        monkeypatch.setattr(L, "AGENT_DIR", tmp_path)
        self._bundle(tmp_path, "C3", {
            "agent_verdict": "SOME_FUTURE_VERDICT",
            "pipeline_results": {"abduction": {
                "best_hypothesis": "SUSPICION_DETECTED"}},
        })
        assert L._fallback_verdict("C3") == "SUSPICION"
