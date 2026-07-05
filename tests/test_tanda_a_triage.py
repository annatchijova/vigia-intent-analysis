"""
tests/test_tanda_a_triage.py
=============================
Regresión de la Tanda A del TRIAGE_BUGS_LIMITACIONES_20260703.md:

  A1  B-017/T-1/T-2 — defusedxml resiliente: su ausencia no mata vigia.sift;
      los XML/EVTX se marcan UNANALYZED (nunca fallback a xml.etree).
  A2  B-026 — prior_trust con Finite Math Shield en el scorer.
  A3  B-027 — is_conclusive coherente con la hipótesis (adaptador EBS +
      guard central en _seal_bundle).
  A4  B-053/T-3 — un pcap corrupto no aborta el caso completo.
  A5  L-023 — escritura atómica del bundle (mkstemp+fsync+replace, hash
      desde disco).
  A6  B-054/F-L040-6 — el fallback de texto importa el módulo real.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────────────────────────────────────
# A1 — B-017/T-1: defusedxml resiliente
# ──────────────────────────────────────────────────────────────────────────

class TestA1DefusedxmlResilient:
    def test_vigia_sift_imports_without_defusedxml(self, tmp_path):
        # T-1: el paquete entero debe importar aunque defusedxml no exista.
        # Se bloquea el import en un subproceso con un paquete falso que
        # lanza ImportError, primero en sys.path.
        fake = tmp_path / "defusedxml"
        fake.mkdir()
        (fake / "__init__.py").write_text(
            "raise ImportError('simulated absence — test A1')\n"
        )
        code = (
            "import sys\n"
            f"sys.path.insert(0, {str(tmp_path)!r})\n"
            f"sys.path.insert(1, {str(REPO)!r})\n"
            "from vigia.sift.sift_orchestrator import SIFTOrchestrator\n"
            "from vigia.sift.event_log_correlator import EventLogCorrelator, ET\n"
            "assert ET is None, 'ET debería ser None sin defusedxml'\n"
            "SIFTOrchestrator('T-A1')\n"
            "print('SIFT-IMPORT-OK')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True,
            cwd=str(REPO), timeout=120,
        )
        assert "SIFT-IMPORT-OK" in proc.stdout, (
            f"vigia.sift no importa sin defusedxml:\n{proc.stderr[-800:]}"
        )

    def test_xml_marked_unanalyzed_when_defusedxml_missing(self, tmp_path, monkeypatch):
        # Sin defusedxml, un .xml presente se reporta UNANALYZED — nunca
        # "0 eventos" silencioso ni fallback a xml.etere.
        import vigia.sift.event_log_correlator as elc
        monkeypatch.setattr(elc, "ET", None)
        xml = tmp_path / "Security.xml"
        xml.write_text("<Events><Event/></Events>")
        result = elc.EventLogCorrelator().analyze([str(xml)])
        assert result.total_events == 0
        joined = " ".join(result.analysis_notes)
        assert "UNANALYZED_ARTIFACT" in joined
        assert "defusedxml" in joined

    def test_defusedxml_in_requirements_ci(self):
        # T-2: el gatillo real del bug era su ausencia en requirements-ci.
        content = (REPO / "requirements-ci.txt").read_text()
        assert "defusedxml" in content

    def test_no_xml_etree_fallback_exists(self):
        # Invariante de seguridad: jamás caer a xml.etree como reemplazo.
        src = (REPO / "vigia/sift/event_log_correlator.py").read_text()
        assert "from xml.etree" not in src
        assert "import xml.etree" not in src


# ──────────────────────────────────────────────────────────────────────────
# A2 — B-026: prior_trust con Finite Math Shield
# ──────────────────────────────────────────────────────────────────────────

class TestA2PriorTrustClamp:
    def _score(self, prior_trust):
        # OJO: el scorer VIVO es el de la raíz (vigia/core/vigia_scorer.py
        # está documentado como stale y sin uso — hallazgo T-6, ambos
        # recibieron el clamp).
        from vigia_scorer import _vigia_score
        case = {
            "case_id": "T-B026",
            "artifacts": [{
                "artifact_id": "A-1", "evidence_type": "log_entry",
                "raw_score": 0.8, "prior_trust": prior_trust,
                "provenance_chain": ["acq", "hash", "seal", "verify"],
            }],
            "provenance_analysis": {"chain_status": "INTACT"},
            "temporal_violations": [],
        }
        return _vigia_score(case)

    @pytest.mark.parametrize("bad", [-1.0, -0.5, float("nan"),
                                     float("inf"), float("-inf"), "1/2", None])
    def test_invalid_prior_trust_never_breaks_scoring(self, bad):
        result = self._score(bad)
        score = float(result.get("score", 0.0))
        assert math.isfinite(score), f"score no finito con prior_trust={bad!r}"
        assert score >= 0.0, f"score negativo con prior_trust={bad!r}"

    def test_above_one_is_clamped(self):
        # prior_trust=5.0 no puede amplificar por encima de trust=1.0.
        inflated = float(self._score(5.0).get("score", 0.0))
        neutral = float(self._score(1.0).get("score", 0.0))
        assert inflated == neutral

    def test_valid_prior_trust_unchanged(self):
        # El clamp no toca valores válidos: 0.5 sigue < 1.0 en efecto.
        half = float(self._score(0.5).get("score", 0.0))
        full = float(self._score(1.0).get("score", 0.0))
        assert half <= full


# ──────────────────────────────────────────────────────────────────────────
# A3 — B-027: is_conclusive coherente con la hipótesis
# ──────────────────────────────────────────────────────────────────────────

class TestA3IsConclusiveCoherent:
    # B-075 (flip 2026-07-05): estos dos tests ejercitan el contrato B-027
    # de la RAMA LEGACY del adaptador (hipótesis derivada de la etiqueta),
    # que quedó como modo explícito de reproducción. Se fijan a legacy; el
    # guard B-027 del camino motor tiene su propio test en
    # tests/test_fase1_resolve.py::TestMotorModeHonesty.
    def test_ebs_abstain_with_high_scores_not_conclusive(self, tmp_path, monkeypatch):
        # El caso exacto de B-027: expected_verdict=ABSTAIN con scores altos
        # sellaba ABSTAIN_DETECTED + is_conclusive=True.
        monkeypatch.setenv("VIGIA_EBS_RESOLVE", "legacy")
        from sift_orchestrator import SIFTOrchestrator
        case = {
            "case_id": "T-B027",
            "expected_verdict": "ABSTAIN",
            "description": "high scores, evidentiary abstain",
            "artifacts": [
                {"artifact_id": "A1", "raw_score": 0.9, "prior_trust": 0.9},
                {"artifact_id": "A2", "raw_score": 0.9, "prior_trust": 0.9},
            ],
        }
        p = tmp_path / "b027.json"
        p.write_text(json.dumps(case))
        result = SIFTOrchestrator("T-B027")._analyze_ebs_json(str(p))
        ab = result["abduction"]
        assert ab["best_hypothesis"] == "ABSTAIN_DETECTED"
        assert ab["is_conclusive"] is False, (
            "ABSTAIN_DETECTED no puede sellar is_conclusive=True (B-027)"
        )

    def test_ebs_malice_keeps_conclusive(self, tmp_path, monkeypatch):
        # Control: el fix no degrada los casos legítimamente conclusivos.
        monkeypatch.setenv("VIGIA_EBS_RESOLVE", "legacy")
        from sift_orchestrator import SIFTOrchestrator
        case = {
            "case_id": "T-B027-M",
            "expected_verdict": "MALICE",
            "artifacts": [
                {"artifact_id": "A1", "raw_score": 0.9, "prior_trust": 0.9},
            ],
        }
        p = tmp_path / "b027m.json"
        p.write_text(json.dumps(case))
        result = SIFTOrchestrator("T-B027-M")._analyze_ebs_json(str(p))
        assert result["abduction"]["is_conclusive"] is True

    def test_seal_bundle_central_guard(self):
        # Guard central: cualquier camino futuro que selle ABSTAIN con
        # is_conclusive=True se degrada en _seal_bundle, anotado.
        from vigia_agent import VIGIAAgent
        agent = VIGIAAgent("T-B027-SEAL", ".")
        results = {
            "signals": [],
            "abduction": {"best_hypothesis": "UNANALYZED_ARTIFACT",
                          "is_conclusive": True, "narrative": "x"},
            "results": {},
        }
        bundle, _t, _d = agent._seal_bundle(results, "narrative", "a" * 64)
        ab = bundle["pipeline_results"]["abduction"]
        assert bundle["agent_verdict"] == "ABSTAIN"
        assert ab["is_conclusive"] is False
        assert "B-027" in ab.get("is_conclusive_downgraded", "")


# ──────────────────────────────────────────────────────────────────────────
# A4 — B-053/T-3: pcap corrupto no aborta el caso
# ──────────────────────────────────────────────────────────────────────────

class TestA4PcapDoesNotAbortCase:
    def test_broken_pcap_yields_unanalyzed_not_pipeline_error(self, monkeypatch):
        import vigia.sift.pcap_parser as pcap_parser
        from sift_orchestrator import SIFTOrchestrator

        def _boom(path):
            raise FileNotFoundError("tshark not found (simulated)")
        monkeypatch.setattr(pcap_parser, "parse_pcap_to_flows", _boom)

        orch = SIFTOrchestrator("T-PCAP")
        # Evidencia mixta: pcap roto + un event_log inexistente (PathGuard
        # lo rechaza pero de forma VISIBLE, no abortando).
        result = orch.analyze(
            pcap_path="/tmp/vigia/broken.pcap",
            event_logs=["/tmp/vigia/missing.evtx"],
        )
        hyp = result["abduction"]["best_hypothesis"]
        assert hyp != "PIPELINE_ERROR", (
            "un pcap roto no puede convertir el caso entero en PIPELINE_ERROR"
        )
        tools = {s.get("tool") for s in result.get("signals", [])}
        assert "PCAP_UNANALYZED" in tools
        assert "pcap" in result.get("results", {}).get("unanalyzed_artifacts", [])
        assert "pcap_error" in result.get("pipeline_meta", {})

    def test_healthy_pcap_path_unaffected(self, monkeypatch):
        # Control: con flujos parseables el camino no cambia.
        import vigia.sift.pcap_parser as pcap_parser
        from sift_orchestrator import SIFTOrchestrator
        monkeypatch.setattr(pcap_parser, "parse_pcap_to_flows", lambda p: [])
        result = SIFTOrchestrator("T-PCAP-OK").analyze(
            pcap_path="/tmp/vigia/ok.pcap",
            event_logs=["/tmp/vigia/missing.evtx"],
        )
        tools = {s.get("tool") for s in result.get("signals", [])}
        assert "PCAP_UNANALYZED" not in tools


# ──────────────────────────────────────────────────────────────────────────
# A5 — L-023: escritura atómica del bundle
# ──────────────────────────────────────────────────────────────────────────

class TestA5AtomicBundleSave:
    def test_save_is_atomic_and_hash_is_from_disk(self, tmp_path):
        from vigia.core.bundle_builder import BundleBuilder
        sealed = {"case_id": "T-L023", "integrity": {"bundle_hash": "x"}}
        out = tmp_path / "nested" / "bundle.json"
        returned_hash = BundleBuilder.save(sealed, str(out))
        # El hash retornado corresponde a los BYTES en disco.
        import hashlib
        disk = hashlib.sha256(out.read_bytes()).hexdigest()
        assert returned_hash == disk
        # Contenido recargable e íntegro.
        assert json.loads(out.read_text())["case_id"] == "T-L023"

    def test_no_orphan_tempfiles_after_save(self, tmp_path):
        from vigia.core.bundle_builder import BundleBuilder
        out = tmp_path / "b.json"
        BundleBuilder.save({"k": 1}, str(out))
        leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".bundle_")]
        assert leftovers == [], f"tempfiles huérfanos: {leftovers}"

    def test_existing_bundle_never_left_half_written(self, tmp_path, monkeypatch):
        # Si el replace nunca ocurre (fallo simulado en fsync), el bundle
        # previo queda INTACTO — nunca un archivo a medio escribir.
        from vigia.core import bundle_builder as bb
        out = tmp_path / "b.json"
        out.write_text('{"previous": true}')

        def _boom(fd):
            raise OSError("simulated fsync failure")
        monkeypatch.setattr(bb.os, "fsync", _boom)
        with pytest.raises(OSError):
            bb.BundleBuilder.save({"new": True}, str(out))
        assert json.loads(out.read_text()) == {"previous": True}
        leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".bundle_")]
        assert leftovers == [], "tempfile huérfano tras fallo"


# ──────────────────────────────────────────────────────────────────────────
# A6 — B-054: fallback de texto importa el módulo real
# ──────────────────────────────────────────────────────────────────────────

class TestA6TextFallbackAlive:
    def test_run_pipeline_import_resolves(self):
        # El import que el fallback usa debe resolver (antes: módulo
        # inexistente → PIPELINE_UNAVAILABLE siempre).
        from vigia.scripts.run_pipeline import run as run_pipeline_fn
        assert callable(run_pipeline_fn)

    def test_text_pipeline_no_longer_unavailable(self, tmp_path):
        # End-to-end del fallback: evidencia de texto por _run_text_pipeline
        # ya no degrada a PIPELINE_UNAVAILABLE.
        from vigia_agent import _run_text_pipeline
        evidence = tmp_path / "note.txt"
        evidence.write_text(
            "urgente: transferí ya los fondos, no consultes con nadie."
        )
        result = _run_text_pipeline(evidence, "T-A6", {})
        assert result["abduction"]["best_hypothesis"] != "PIPELINE_UNAVAILABLE"
