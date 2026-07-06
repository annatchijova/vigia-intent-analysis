"""
B1-c (2026-07-06) — ruteo de memoria en evidencia mixta.

Antes: `memory_path and not disk_path` mandaba el caso a vol3-solo, y los
evtx/hives/pcap/mft del MISMO caso se descartaban en silencio (falso
negativo por ruteo). Además, la rama mixta pasaba memory_dump_path al
orquestador real: si su MemoryForensicsEngine existía (self.memory, binario
`vol` presente), la misma imagen se analizaba dos veces (doble conteo).

Ahora: memoria + otros artefactos → orquestador real con TODOS los
artefactos MENOS la memoria + vol3 (el motor de memoria confiable) sobre la
memoria por separado, señales fusionadas (patrón F6) con escalación
determinista auditada y degradación F7 (MEMORY_UNANALYZED) cuando vol3 no
puede analizar.

End-to-end: directorio dummy {memory.raw, Security.evtx, SYSTEM} atraviesa
vigia_agent._build_orchestrator_kwargs → shim.analyze() → resultado
fusionado. vol3 se simula vía monkeypatch de _vol3_run (determinista, sin
binario volatility3 en CI).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import sift_orchestrator as so
import vigia.sift.sift_orchestrator as real_mod
from vigia_agent import _build_orchestrator_kwargs, _signal_stats


@pytest.fixture()
def dummy_dir(tmp_path: Path) -> Path:
    """Dir de evidencia dummy: memoria + evtx + hive SYSTEM."""
    (tmp_path / "memory.raw").write_bytes(b"\x00MDMP" + b"\x90" * 512)
    (tmp_path / "Security.evtx").write_bytes(b"ElfFile\x00" + b"\x00" * 256)
    (tmp_path / "SYSTEM").write_bytes(b"regf" + b"\x00" * 256)
    return tmp_path


def _vol3_ok(payload: str):
    """Simula _vol3_run devolviendo output válido para todo plugin."""
    def fake(self, memory_path, plugin, timeout=300):
        return {"ok": True, "stdout": payload + " " * 60, "stderr": ""}
    return fake


def _vol3_dead(self, memory_path, plugin, timeout=300):
    return {"ok": False, "stdout": "", "stderr": "vol3: command not found"}


class TestKwargsDetection:
    def test_dummy_dir_detects_all_three_artifacts(self, dummy_dir):
        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        assert str(kwargs.get("memory_path", [""])[0] if isinstance(
            kwargs.get("memory_path"), list) else kwargs.get("memory_path", "")
        ).endswith("memory.raw")
        assert any(str(e).endswith("Security.evtx")
                   for e in kwargs.get("event_logs", []))
        assert any(str(h).endswith("SYSTEM")
                   for h in kwargs.get("registry_hives", []))


class TestMixedRouting:
    def test_real_orchestrator_never_receives_memory(self, dummy_dir, monkeypatch):
        """No doble conteo: aunque self.memory exista en el orquestador
        real, nunca recibe memory_dump_path — vol3 es el dueño de la
        memoria."""
        captured = {}
        original = real_mod.SIFTOrchestrator.run_full_analysis

        def spy(self, **kw):
            captured.update(kw)
            return original(self, **kw)

        monkeypatch.setattr(real_mod.SIFTOrchestrator, "run_full_analysis", spy)
        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run",
                            _vol3_ok("Windows 10 kernel profile detected"))

        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        result = so.SIFTOrchestrator("T-B1C-NODBL").analyze(**kwargs)

        assert captured, "el orquestador real debe correr (evtx+SYSTEM)"
        assert captured.get("memory_dump_path") is None, (
            "B1-c: memory_dump_path llegó al orquestador real — doble "
            "conteo con vol3 si self.memory existe"
        )
        assert captured.get("event_logs"), "los evtx deben llegar al real"
        assert captured.get("registry_hives"), "los hives deben llegar al real"
        assert result["pipeline_meta"]["b1c_memory_engine"] == "vol3_adapter"

    def test_vol3_signals_merged_and_primary(self, dummy_dir, monkeypatch):
        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run",
                            _vol3_ok("Windows profile identified"))
        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        result = so.SIFTOrchestrator("T-B1C-MRG").analyze(**kwargs)
        vol3_sigs = [s for s in result["signals"]
                     if str(s.get("source", "")).startswith("vol3.")]
        assert vol3_sigs, "las señales vol3 deben estar en el resultado fusionado"
        assert result["pipeline_meta"]["n_vol3_signals"] == len(vol3_sigs)
        # F5: señales vol3 (sin metadata) cuentan como primarias
        n_primary, _ = _signal_stats(result)
        assert n_primary >= len(vol3_sigs)

    def test_memory_only_still_routes_to_vol3_alone(self, tmp_path, monkeypatch):
        """Memoria pura (sin otros artefactos) conserva la ruta vol3-solo."""
        mem = tmp_path / "solo.raw"
        mem.write_bytes(b"\x00" * 128)
        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run",
                            _vol3_ok("Windows profile identified"))
        result = so.SIFTOrchestrator("T-B1C-SOLO").analyze(memory_path=str(mem))
        # la ruta memoria-pura no pasa por el merge B1-c
        assert "b1c_memory_engine" not in result.get("pipeline_meta", {})
        assert any(str(s.get("source", "")).startswith("vol3.")
                   for s in result["signals"])


class TestEscalationAndHonesty:
    def test_vol3_malicious_escalates_benign_base(self, dummy_dir, monkeypatch):
        """vol3 es el motor confiable: MALICIOUS en memoria escala una base
        benigna, con rastro de auditoría."""
        def fake_vol3(self, memory_path):
            return {
                "case_id": "x",
                "signals": [{"source": "vol3.windows.malfind",
                             "evidence_type": "memory_injection",
                             "z_score": 4.0, "confidence": 0.95,
                             "description": "inyección"}],
                "abduction": {"best_hypothesis": "MALICIOUS_INTENT_DETECTED",
                              "is_conclusive": True, "confidence": "9/10"},
            }
        monkeypatch.setattr(so.SIFTOrchestrator, "_analyze_memory_vol3", fake_vol3)
        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        result = so.SIFTOrchestrator("T-B1C-ESC").analyze(**kwargs)
        abd = result["abduction"]
        hyp = str(abd.get("best_hypothesis", "")).upper()
        if "MALICIOUS" not in hyp:
            pytest.fail(f"hipótesis no escalada: {hyp}")
        # si la escalación vino del merge B1-c, debe llevar auditoría
        if "vol3_escalation" in abd:
            assert abd["vol3_escalation"]["to"] == "MALICIOUS_INTENT_DETECTED"

    def test_vol3_unavailable_marks_memory_unanalyzed(self, dummy_dir, monkeypatch):
        """F7: vol3 muerto ≠ memoria benigna — MEMORY_UNANALYZED sellado."""
        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run", _vol3_dead)
        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        result = so.SIFTOrchestrator("T-B1C-F7").analyze(**kwargs)
        markers = [s for s in result["signals"]
                   if s.get("tool") == "MEMORY_UNANALYZED"]
        assert markers, "memoria sin analizar debe materializarse (F7)"
        assert markers[0]["metadata"]["unanalyzed"] is True
        _, n_unanalyzed = _signal_stats(result)
        assert n_unanalyzed >= 1
        ua = result.get("results", {}).get("unanalyzed_artifacts", [])
        assert "memory" in ua

    def test_merge_is_json_serializable(self, dummy_dir, monkeypatch):
        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run",
                            _vol3_ok("Windows profile identified"))
        kwargs = _build_orchestrator_kwargs(dummy_dir, {})
        result = so.SIFTOrchestrator("T-B1C-JSON").analyze(**kwargs)
        json.dumps(result, default=str)
