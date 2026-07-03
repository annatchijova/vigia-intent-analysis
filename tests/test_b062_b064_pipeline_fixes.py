"""
Tests B-062 / B-063 / B-064 — fixes del camino standalone (Modo 4 / CLI `vigia`).

B-062: el CAIE structural veto es una ANOTACIÓN sellada (gate_verdict), no una
       orden — el log ya no dice "verdict overridden" y la decisión de
       gobernanza no cambia.
B-063: SignalOutput.metadata=None (default de ebs_v1) crasheaba el
       ForensicAdapter → "CAIE failed (non-blocking)" → CAIE se salteaba en
       silencio con el formato de entrada documentado del propio CLI.
B-064: escrituras atómicas (patrón L-023) para ledger/manifest/firma/bundle/
       reporte — un crash a mitad de escritura no deja artefactos truncados.
"""

import json
import logging
import os

import pytest

from vigia.core.ebs_v1 import SignalOutput
from vigia.core.forensic_adapter import ForensicAdapter


def _sig(metadata=None, **kw):
    base = dict(tool_name="SDA", value=0.8, z_score=2.3, confidence=0.9)
    base.update(kw)
    return SignalOutput(metadata=metadata, **base)


# ===========================================================================
# B-063 — adapter tolera metadata=None
# ===========================================================================

class TestB063MetadataNone:
    def test_caie_artifact_with_none_metadata(self):
        art = ForensicAdapter.signal_to_caie_artifact(_sig(metadata=None))
        # Paridad: metadata=None se comporta igual que metadata={}
        ref = ForensicAdapter.signal_to_caie_artifact(_sig(metadata={}))
        assert art.source_tool == "SDA"
        assert art.evidence_type == ref.evidence_type

    def test_abductive_record_with_none_metadata(self):
        rec = ForensicAdapter.signal_to_abductive_record(_sig(metadata=None))
        assert rec.source_path == "unknown"

    def test_causal_link_with_none_metadata(self):
        link = ForensicAdapter.signal_to_causal_link(_sig(metadata=None))
        assert link.link_id.startswith("link-SDA")

    def test_build_context_with_none_metadata_does_not_crash(self):
        sigs = [_sig(metadata=None, tool_name=t) for t in ("SDA", "TVD", "MFT")]
        ctx = ForensicAdapter.build_context(sigs, raw_results={})
        assert len(ctx.caie_artifacts) == 3
        assert len(ctx.abductive_records) == 3
        assert len(ctx.causal_links) == 3

    def test_metadata_dict_still_honored(self):
        art = ForensicAdapter.signal_to_caie_artifact(
            _sig(metadata={"evidence_type": "mft", "description": "MFT anomaly"})
        )
        assert art.evidence_type == "file_timestamp"  # mapa legacy "mft"
        assert art.description == "MFT anomaly"

    def test_cli_documented_input_runs_caie(self, caplog):
        """El formato del docstring del CLI (sin metadata) ya no saltea CAIE."""
        from vigia.pipeline.pipeline import run_vigia

        signals = [
            {"tool_name": t, "value": 0.1, "z_score": z, "confidence": 0.9}
            for t, z in (("SDA", 0.2), ("TVD", 0.1), ("MFT", 0.3), ("NET", 0.2))
        ]
        with caplog.at_level(logging.WARNING, logger="vigia.pipeline.pipeline"):
            result = run_vigia(signals_data=signals)
        assert "CAIE failed (non-blocking)" not in caplog.text
        assert result["decision"]  # pipeline completo, no crash


# ===========================================================================
# B-062 — gate_verdict es anotación, no orden; log honesto
# ===========================================================================

class TestB062GateAnnotation:
    @pytest.fixture()
    def golden_rule_caie(self, monkeypatch):
        import vigia.tools.caie as caie_mod

        async def fake(artifacts):
            return {
                "verdict": "MALICE",
                "structural_verdict": "MALICE",
                "composite_score": 0.97,
                "fractures_detected": 1,
                "golden_rules_triggered": 1,
                "fractures": [{
                    "type": "TEMPORAL_CAUSALITY_VIOLATION",
                    "severity": 0.95,
                    "artifact_a": "a", "artifact_b": "b",
                }],
            }

        monkeypatch.setattr(caie_mod, "cross_artifact_analysis", fake)

    def test_gate_annotates_bundle_without_touching_decision(
        self, golden_rule_caie, caplog
    ):
        from vigia.pipeline.pipeline import run_vigia

        signals = [
            {"tool_name": t, "value": 0.1, "z_score": z, "confidence": 0.9}
            for t, z in (("SDA", 0.2), ("TVD", 0.1), ("MFT", 0.3), ("NET", 0.2))
        ]
        with caplog.at_level(logging.WARNING, logger="vigia.pipeline.pipeline"):
            result = run_vigia(signals_data=signals)

        sealed = json.loads(result["bundle_json"])
        caie = sealed.get("caie_analysis") or {}

        # La anotación queda sellada en el bundle
        assert caie.get("gate_verdict") == "MALICE"
        assert "TEMPORAL_CAUSALITY_VIOLATION" in caie.get("gate_override_reason", "")
        # La decisión de gobernanza NO se toca (vocabulario ACCEPT/REJECT/ABSTAIN)
        assert result["decision"] in ("ACCEPT", "REJECT", "ABSTAIN")
        # El log dice lo que pasa de verdad
        assert "verdict overridden" not in caplog.text
        assert "structural veto annotated" in caplog.text


# ===========================================================================
# B-064 — escrituras atómicas
# ===========================================================================

class TestB064AtomicWrites:
    def test_atomic_write_text_roundtrip_no_tempfiles(self, tmp_path):
        from vigia.core.atomic_io import atomic_write_text

        target = tmp_path / "ledger.json"
        atomic_write_text(str(target), '{"ok": true}')
        assert json.loads(target.read_text()) == {"ok": True}
        leftovers = [p for p in os.listdir(tmp_path) if p.endswith(".tmp")]
        assert leftovers == []

    def test_atomic_write_failure_preserves_existing_target(self, tmp_path):
        from vigia.core.atomic_io import atomic_write_text

        target = tmp_path / "manifest.json"
        target.write_text("original")
        with pytest.raises(TypeError):
            atomic_write_text(str(target), {"not": "a string"})  # type: ignore[arg-type]
        assert target.read_text() == "original"
        leftovers = [p for p in os.listdir(tmp_path) if p.endswith(".tmp")]
        assert leftovers == []

    def test_atomic_write_bytes_roundtrip(self, tmp_path):
        from vigia.core.atomic_io import atomic_write_bytes

        target = tmp_path / "report.pdf"
        atomic_write_bytes(str(target), b"%PDF-1.4 fake")
        assert target.read_bytes() == b"%PDF-1.4 fake"

    def test_registry_export_json_atomic_and_valid(self, tmp_path):
        from vigia.pipeline.security_evidence_registry import EvidenceLedger

        reg = EvidenceLedger()
        out = tmp_path / "registry.json"
        reg.export_json(str(out))
        data = json.loads(out.read_text())
        assert "entries" in data and "ledger_length" in data
        leftovers = [p for p in os.listdir(tmp_path) if p.endswith(".tmp")]
        assert leftovers == []
