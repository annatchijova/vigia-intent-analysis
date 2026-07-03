"""
tests/test_tanda_b.py
======================
Regresión de la Tanda B (PROPUESTA_TANDA_B.md, aprobada 2026-07-03).

Commit B1 (sin efecto en veredictos):
  1. B-055 — vigia/core/vigia_scorer es re-export del scorer canónico.
  4. B-028-A — floor de alerta para INTENT conclusivo.
  5. L-024 — /mnt restringido a prefijos forenses (vigia_*, ewf*, evidence).
  6. P2-E — timestamps en to_signal (eventlog + MFT).
  7. N11-B — marca engines_not_run_no_event_stream en pipeline_meta.
  9. U7 — record_hash cuantizado (estable cross-arch).

Commit B2 (mueven el scorer, corrida comparativa):
  2. P2-D — provenance_collapsed → ABSTAIN (no NOISE).
  3. L-037b — artifact_reliability → CAIE base_trust.
  9. U3 — tabla exp en trust_fusion.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest


# ──────────────────────────────────────────────────────────────────────────
# B1-1 — B-055: re-export del scorer canónico
# ──────────────────────────────────────────────────────────────────────────

class TestB055ScorerReexport:
    def test_core_copy_is_same_object_as_root(self):
        from vigia.core.vigia_scorer import _vigia_score as core_fn
        from vigia_scorer import _vigia_score as root_fn
        assert core_fn is root_fn, (
            "vigia/core/vigia_scorer debe re-exportar el scorer de la raíz, "
            "no divergir (B-055)"
        )

    def test_epc_table_present_via_core_import(self):
        # El NameError latente original: _EPC_FACTOR_TABLE no existía en la
        # copia stale.
        from vigia.core.vigia_scorer import _EPC_FACTOR_TABLE
        assert len(_EPC_FACTOR_TABLE) == 16
        assert _EPC_FACTOR_TABLE[0] == Fraction(1, 1)

    def test_core_import_scores_without_nameerror(self):
        from vigia.core.vigia_scorer import _vigia_score
        case = {
            "case_id": "T-B055",
            "artifacts": [{"artifact_id": "A", "evidence_type": "log_entry",
                           "raw_score": 0.5, "prior_trust": 0.8,
                           "provenance_chain": ["a", "b", "c", "d", "e"]}],
            "provenance_analysis": {"chain_status": "INTACT"},
            "temporal_violations": [],
        }
        result = _vigia_score(case)  # pre-fix: NameError con cadena no-BROKEN
        assert "verdict" in result


# ──────────────────────────────────────────────────────────────────────────
# B1-4 — B-028 opción A: floor de alerta para INTENT conclusivo
# ──────────────────────────────────────────────────────────────────────────

class TestB028IntentAlertFloor:
    def _narrative(self, is_conclusive: bool) -> str:
        from vigia_agent import VIGIAAgent
        agent = VIGIAAgent("T-B028", ".")
        results = {
            # Señales bajas: sin críticas ni altas → alert base LOW.
            "signals": [{"tool": f"T{i}", "z_score": 0.5, "confidence": 0.7,
                         "value": 0.5, "metadata": {}} for i in range(4)],
            "abduction": {"best_hypothesis": "INTENT_DETECTED",
                          "is_conclusive": is_conclusive,
                          "best_posterior": "1/2", "narrative": "x"},
            "results": {},
        }
        return agent._generate_narrative(results, "a" * 64)

    def test_conclusive_intent_floors_alert_to_medium(self):
        narrative = self._narrative(is_conclusive=True)
        assert "No significant anomalies" not in narrative
        assert "B-028" in narrative
        assert "MEDIUM — INTENT verdict" in narrative

    def test_non_conclusive_intent_also_floors(self):
        # B-065: el piso se calcula sobre el veredicto final, no sobre
        # is_conclusive. INTENT no-concluyente con 4 primarias clasifica
        # INTENT → también pisa a MEDIUM (antes quedaba LOW — ese era el bug).
        narrative = self._narrative(is_conclusive=False)
        assert "MEDIUM — INTENT verdict" in narrative
        assert "Reconciliation: verdict INTENT" in narrative

    def test_malice_floor_unchanged(self):
        # El floor MALICE mantiene los umbrales de B-028 (posterior >= 1/8
        # → HIGH), ahora keyed en el veredicto final (B-065).
        from vigia_agent import VIGIAAgent
        agent = VIGIAAgent("T-B028-M", ".")
        results = {
            "signals": [{"tool": "T", "z_score": 0.5, "confidence": 0.7,
                         "value": 0.5, "metadata": {}} for _ in range(3)],
            "abduction": {"best_hypothesis": "MALICIOUS_INTENT_DETECTED",
                          "is_conclusive": True,
                          "best_posterior": "1/2", "narrative": "x"},
            "results": {},
        }
        narrative = agent._generate_narrative(results, "b" * 64)
        assert "HIGH — MALICE verdict" in narrative


# ──────────────────────────────────────────────────────────────────────────
# B1-5 — L-024: /mnt restringido a prefijos forenses
# ──────────────────────────────────────────────────────────────────────────

class TestL024MntPrefixes:
    def test_generic_mnt_not_in_allowlist(self):
        from vigia.sift.sift_orchestrator import _evidence_allowlist
        assert Path("/mnt") not in _evidence_allowlist()

    def test_forensic_mounts_expansion(self, tmp_path):
        from vigia.sift.sift_orchestrator import _forensic_mounts
        (tmp_path / "vigia_case1").mkdir()
        (tmp_path / "ewf1").mkdir()
        (tmp_path / "evidence").mkdir()
        (tmp_path / "nfs-corporativo").mkdir()   # NO forense
        (tmp_path / "vigia_link").symlink_to(tmp_path / "nfs-corporativo")
        mounts = _forensic_mounts(base=tmp_path)
        names = {p.name for p in mounts}
        assert names == {"vigia_case1", "ewf1", "evidence"}, (
            "solo los prefijos aprobados (vigia_*, ewf*, evidence), "
            "sin symlinks ni montajes ajenos"
        )

    def test_missing_mnt_dir_is_empty(self, tmp_path):
        from vigia.sift.sift_orchestrator import _forensic_mounts
        assert _forensic_mounts(base=tmp_path / "noexiste") == []


# ──────────────────────────────────────────────────────────────────────────
# B1-6 — P2-E: timestamps en to_signal
# ──────────────────────────────────────────────────────────────────────────

class TestP2ETimestamps:
    def test_eventlog_signal_carries_timestamp(self):
        from vigia.sift.event_log_correlator import EventLogAnalysisResult
        r = EventLogAnalysisResult(
            source_files=["x.evtx"], total_events=5, time_range=(100, 250),
        )
        meta = r.to_signal().metadata
        assert meta["timestamp"] == 250
        assert meta["time_range"] == [100, 250]

    def test_mft_signal_carries_latest_anomaly_ts(self):
        from vigia.sift.disk_forensics import MFTAnalysisResult
        r = MFTAnalysisResult(
            mft_hash="h" * 64, total_entries=10,
            timestomp_entries=[{"type": "MODIFIED_MISMATCH",
                                "si": "2020-01-01T00:00:00Z",
                                "fn": "2021-06-01T12:00:00Z"}],
            hardlink_anomalies=[], ads_entries=[], slack_suspects=[],
            recreation_gaps=[],
            sequence_anomalies=[{"modified": 1500000000}],
        )
        ts = r.to_signal().metadata["timestamp"]
        # El más reciente entre 1500000000 (2017) y 2021-06-01 (1622548800).
        assert ts == 1622548800

    def test_mft_no_anomalies_keeps_zero(self):
        from vigia.sift.disk_forensics import MFTAnalysisResult
        r = MFTAnalysisResult(
            mft_hash="h" * 64, total_entries=0, timestomp_entries=[],
            hardlink_anomalies=[], ads_entries=[], slack_suspects=[],
            recreation_gaps=[], sequence_anomalies=[],
        )
        assert r.to_signal().metadata["timestamp"] == 0


# ──────────────────────────────────────────────────────────────────────────
# B1-7 — N11 opción B: marca NOT_RUN
# ──────────────────────────────────────────────────────────────────────────

class TestN11NotRunMark:
    def test_pipeline_meta_declares_engines_not_run(self):
        from vigia.sift.sift_orchestrator import SIFTOrchestrator as V4
        result = V4("T-N11").run_full_analysis()  # sin event_stream
        not_run = result["pipeline_meta"].get("engines_not_run_no_event_stream")
        assert not_run is not None, (
            "sin event_stream, metabolic/behavioral deben declararse NOT_RUN"
        )
        assert "metabolic" in not_run and "behavioral" in not_run


# ──────────────────────────────────────────────────────────────────────────
# B1-9 — U7: record_hash cuantizado, estable cross-arch
# ──────────────────────────────────────────────────────────────────────────

class TestU7QuantizedRecordHash:
    def _record(self, posterior: float):
        from vigia.core.likelihood_ratio import ForensicRecord
        return ForensicRecord(
            record_id="LR-fixed-000", timestamp_utc="2026-07-03T00:00:00Z",
            signals_in=[], z_scores_clipped=[2.0], log_lrs=[2.0],
            correlation_matrix=None, mean_correlation=0.0,
            correction_factor=1.0, combined_log_lr=2.0,
            lr_combined=7.389056098930650, posterior_probability=posterior,
            enfsi_label="limited",
        )

    def test_one_ulp_divergence_collapses_to_same_hash(self):
        # La divergencia bit-52 (x86 vs ARM) es ~1e-16 — el hash cuantizado
        # debe ser idéntico.
        base = self._record(0.5)
        perturbed = self._record(0.5 + 1e-15)
        assert base.record_hash() == perturbed.record_hash()

    def test_material_difference_changes_hash(self):
        # La cuantización no borra diferencias reales (>= 1e-6).
        assert self._record(0.5).record_hash() != \
            self._record(0.50001).record_hash()

    def test_display_dict_unchanged_schema(self):
        # to_dict() (display) sigue emitiendo floats — solo el hash cuantiza.
        d = self._record(0.5).to_dict()
        assert isinstance(d["posterior_probability"], float)


# ──────────────────────────────────────────────────────────────────────────
# B2-1 — P2-D: provenance_collapsed → ABSTAIN
# ──────────────────────────────────────────────────────────────────────────

class TestP2DProvenanceCollapsedAbstain:
    def _collapsed_case(self):
        # Trust efectivo colapsado: cadena BROKEN (epc=0.1) × prior bajísimo,
        # sin fracturas → mean_effective < 0.01.
        return {
            "case_id": "T-P2D",
            "artifacts": [{"artifact_id": "A", "evidence_type": "log_entry",
                           "raw_score": 0.4, "prior_trust": 0.05,
                           "provenance_chain": []}],
            "provenance_analysis": {"chain_status": "BROKEN"},
            "temporal_violations": [],
        }

    def test_collapsed_provenance_abstains_not_noise(self):
        from vigia_scorer import _vigia_score
        result = _vigia_score(self._collapsed_case())
        assert result["verdict"] == "ABSTAIN", (
            "cadena de custodia colapsada = 'no puedo confiar en la "
            "evidencia' → ABSTAIN, nunca NOISE confiado (P2-D)"
        )
        assert float(result["confidence"]) == 0.0, (
            "sin base epistémica la confianza no puede derivarse de "
            "1 - mean_effective"
        )

    def test_intact_provenance_unaffected(self):
        from vigia_scorer import _vigia_score
        case = self._collapsed_case()
        case["artifacts"][0]["prior_trust"] = 0.9
        case["artifacts"][0]["provenance_chain"] = ["a", "b", "c", "d"]
        case["provenance_analysis"] = {"chain_status": "INTACT"}
        result = _vigia_score(case)
        assert result["verdict"] != "ABSTAIN" or "PROVENANCE" not in str(
            result.get("reason", ""))


# ──────────────────────────────────────────────────────────────────────────
# B2-2 — L-037b: artifact_reliability → CAIE base_trust
# ──────────────────────────────────────────────────────────────────────────

class TestL037bBaseTrustPropagation:
    # CAIE degrada base_trust en __post_init__ si faltan metadatos de
    # adquisición (NIST SP 800-86) — para testear la PROPAGACIÓN (L-037b)
    # sin mezclarla con esa degradación, se provee metadata completa.
    _FULL_ACQ = {
        "acquisition_tool": "ftk imager",
        "acquisition_hash": "sha256:" + "a" * 64,
        "acquisition_timestamp": "2026-07-03T00:00:00+00:00",
        "examiner_id": "tester",
        "write_blocker_used": True,
    }

    def _artifact_for(self, metadata):
        from vigia.core.forensic_adapter import ForensicAdapter
        from vigia.core.ebs_v1 import SignalOutput
        meta = {**self._FULL_ACQ, **metadata}
        sig = SignalOutput(tool_name="EVENT_LOG", value=0.5, z_score=2.0,
                           confidence=0.8, metadata=meta)
        return ForensicAdapter.signal_to_caie_artifact(sig)

    # CAIE aplica además decays propios post-init (p.ej. un factor e⁻¹ por
    # la cadena de provenance corta) — se asserta el RATIO contra el caso
    # base (reliability ausente = 1.0), que aísla exactamente la propagación.
    def _ratio(self, metadata):
        base = self._artifact_for({"artifact_type": "event_log"})
        art = self._artifact_for(metadata)
        return float(art.base_trust) / float(base.base_trust)

    def test_reliability_propagates(self):
        ratio = self._ratio({"artifact_type": "event_log",
                             "artifact_reliability": "39/50"})
        assert ratio == pytest.approx(0.78, abs=1e-4)

    def test_missing_reliability_defaults_to_one(self):
        ratio = self._ratio({"artifact_type": "event_log"})
        assert ratio == pytest.approx(1.0, abs=1e-6)

    def test_garbage_reliability_defaults_to_one(self):
        ratio = self._ratio({"artifact_type": "event_log",
                             "artifact_reliability": "not-a-fraction"})
        assert ratio == pytest.approx(1.0, abs=1e-6)

    def test_out_of_range_clamped(self):
        ratio = self._ratio({"artifact_type": "event_log",
                             "artifact_reliability": "7/2"})
        assert ratio == pytest.approx(1.0, abs=1e-6)

    def test_lower_reliability_yields_lower_trust_end_to_end(self):
        # Propiedad de orden aun CON degradación por metadata ausente:
        # menor artifact_reliability nunca produce mayor base_trust.
        from vigia.core.forensic_adapter import ForensicAdapter
        from vigia.core.ebs_v1 import SignalOutput
        def bt(meta):
            sig = SignalOutput(tool_name="EVENT_LOG", value=0.5, z_score=2.0,
                               confidence=0.8, metadata=meta)
            return float(ForensicAdapter.signal_to_caie_artifact(sig).base_trust)
        low = bt({"artifact_type": "event_log", "artifact_reliability": "1/5"})
        high = bt({"artifact_type": "event_log", "artifact_reliability": "1"})
        assert low <= high


# ──────────────────────────────────────────────────────────────────────────
# B2-3 — U3: tabla exp en trust_fusion
# ──────────────────────────────────────────────────────────────────────────

class TestU3TrustFusionExpTable:
    def test_temporal_factor_uses_table_no_native_exp(self):
        import inspect
        from vigia.core import trust_fusion
        src = inspect.getsource(trust_fusion.TrustFusionEngine.compute_temporal_trust_factor)
        assert "math.exp(" not in src, (
            "U3: compute_temporal_trust_factor no debe usar math.exp nativa "
            "(bit 52 x86/ARM) — tabla precomputada como _EXP_NEG2_TABLE"
        )

    def test_table_matches_scorer_buckets(self):
        # Consistencia numérica con la tabla canónica del scorer.
        from vigia.core.trust_fusion import TrustFusionEngine
        from vigia_scorer import _EXP_NEG2_TABLE
        for bucket in (0, 5, 10, 20):
            severity = bucket * 0.05
            violations = [{"type": "EFFECT_BEFORE_CAUSE", "severity": severity,
                           "cause": {"artifact_id": "X"},
                           "effect": {"artifact_id": "Y"}}]
            got = TrustFusionEngine.compute_temporal_trust_factor(violations, "X")
            expected = float(_EXP_NEG2_TABLE[bucket])
            assert got == pytest.approx(expected, abs=1e-6), (
                f"bucket {bucket}: {got} != {expected}"
            )

    def test_no_violations_stays_one(self):
        from vigia.core.trust_fusion import TrustFusionEngine
        assert TrustFusionEngine.compute_temporal_trust_factor([], "X") == 1.0
