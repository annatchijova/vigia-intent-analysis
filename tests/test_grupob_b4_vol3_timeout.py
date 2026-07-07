"""
B4 (Grupo B / B-018 residual) — VIGIA_VOL3_TIMEOUT + escalado por tamaño,
registrado en pipeline_meta.

Firstness: los timeouts de vol3 estaban hardcodeados (120/300/300/600 en el
shim; 300 en el motor V4) y un dump ≥4 GB los agota → plugins truncados →
señales perdidas SIN rastro en el bundle (B-018: "0 señales por timeout" era
indistinguible de "0 señales porque está limpio"; el caso NARCOS-Jane).

Contrato nuevo:
  - VIGIA_VOL3_TIMEOUT=<segundos> fija el timeout EXACTO (el perito manda;
    sin escalado encima).
  - Sin env: el base por-plugin se escala por tamaño del dump (≥4 GiB ×2,
    ≥16 GiB ×4) — los números de B-018 (malfind ~25-40s en 4 GB con base
    pensada para dumps chicos).
  - pipeline_meta registra qué plugins expiraron (vol3_plugin_timeouts) y
    pipeline_status completed/timeout_partial — el investigador VE la pérdida.

Tests escritos ROJOS contra el código previo.
"""

import pytest

import vigia.sift.memory_forensics as mf


class TestEffectiveTimeoutHelper:
    def test_env_var_wins_exactly(self, monkeypatch, tmp_path):
        p = tmp_path / "d.img"
        p.write_bytes(b"\x00" * 64)
        monkeypatch.setenv("VIGIA_VOL3_TIMEOUT", "77")
        assert mf.vol3_effective_timeout(300, str(p)) == 77

    def test_env_invalid_falls_back(self, monkeypatch, tmp_path):
        p = tmp_path / "d.img"
        p.write_bytes(b"\x00" * 64)
        monkeypatch.setenv("VIGIA_VOL3_TIMEOUT", "no-numerico")
        assert mf.vol3_effective_timeout(300, str(p)) == 300

    def test_small_dump_uses_base(self, monkeypatch, tmp_path):
        monkeypatch.delenv("VIGIA_VOL3_TIMEOUT", raising=False)
        p = tmp_path / "d.img"
        p.write_bytes(b"\x00" * 64)
        assert mf.vol3_effective_timeout(300, str(p)) == 300

    def test_4gib_dump_doubles(self, monkeypatch, tmp_path):
        monkeypatch.delenv("VIGIA_VOL3_TIMEOUT", raising=False)
        p = tmp_path / "d.img"
        p.write_bytes(b"\x00")
        monkeypatch.setattr(mf.os.path, "getsize", lambda _: 4 * 2**30)
        assert mf.vol3_effective_timeout(300, str(p)) == 600

    def test_16gib_dump_quadruples(self, monkeypatch, tmp_path):
        monkeypatch.delenv("VIGIA_VOL3_TIMEOUT", raising=False)
        p = tmp_path / "d.img"
        p.write_bytes(b"\x00")
        monkeypatch.setattr(mf.os.path, "getsize", lambda _: 16 * 2**30)
        assert mf.vol3_effective_timeout(300, str(p)) == 1200

    def test_missing_file_uses_base(self, monkeypatch, tmp_path):
        monkeypatch.delenv("VIGIA_VOL3_TIMEOUT", raising=False)
        assert mf.vol3_effective_timeout(300, str(tmp_path / "no-existe")) == 300


class TestV4InterfaceEnvDefault:
    def _iface(self, monkeypatch, **kw):
        monkeypatch.setattr(mf.Volatility3Interface, "_validate_binary",
                            staticmethod(lambda b: "/fake/vol"))
        monkeypatch.setattr(mf.Volatility3Interface, "_detect_version",
                            lambda self: "2.7.0")
        return mf.Volatility3Interface(vol_binary="/fake/vol", **kw)

    def test_env_sets_default_timeout(self, monkeypatch):
        monkeypatch.setenv("VIGIA_VOL3_TIMEOUT", "45")
        assert self._iface(monkeypatch)._timeout == 45

    def test_explicit_param_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("VIGIA_VOL3_TIMEOUT", "45")
        assert self._iface(monkeypatch, timeout_seconds=120)._timeout == 120

    def test_no_env_default_300(self, monkeypatch):
        monkeypatch.delenv("VIGIA_VOL3_TIMEOUT", raising=False)
        assert self._iface(monkeypatch)._timeout == 300


class TestPipelineMetaVisibility:
    """El shim del agente (sift_orchestrator raíz) debe DEJAR RASTRO."""

    def _orch(self):
        import sift_orchestrator as so
        return so.SIFTOrchestrator(case_id="B4-TEST")

    def test_partial_timeout_recorded_in_meta(self, monkeypatch, tmp_path):
        import sift_orchestrator as so
        dump = tmp_path / "big.img"
        dump.write_bytes(b"\x00" * 128)

        def fake_run(self, memory_path, plugin, timeout=300):
            if plugin == "windows.info":
                return {"ok": True, "stdout": "Windows 10 x64 kernel", "stderr": "",
                        "timed_out": False, "timeout_used": timeout}
            return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s",
                    "timed_out": True, "timeout_used": timeout}

        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run", fake_run)
        result = self._orch()._analyze_memory_vol3(str(dump))
        meta = result["pipeline_meta"]
        assert meta.get("pipeline_status") == "timeout_partial", (
            "plugins expirados sin rastro en pipeline_meta — el B-018 exacto"
        )
        timeouts = meta.get("vol3_plugin_timeouts", [])
        assert "windows.pslist.PsList" in timeouts
        assert "windows.malfind.Malfind" in timeouts
        assert meta.get("vol3_timeout_config"), "config de timeout no registrada"

    def test_all_timeouts_reads_timeout_all(self, monkeypatch, tmp_path):
        # El caso NARCOS exacto: TODOS los plugins expiran → UNANALYZED_ARTIFACT
        # con pipeline_status=timeout_all — distinguible de binario ausente.
        import sift_orchestrator as so
        dump = tmp_path / "narcos.img"
        dump.write_bytes(b"\x00" * 128)

        def fake_run(self, memory_path, plugin, timeout=300):
            return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s",
                    "timed_out": True, "timeout_used": timeout}

        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run", fake_run)
        result = self._orch()._analyze_memory_vol3(str(dump))
        assert result["abduction"]["best_hypothesis"] == "UNANALYZED_ARTIFACT"
        meta = result["pipeline_meta"]
        assert meta["pipeline_status"] == "timeout_all"
        assert len(meta["vol3_plugin_timeouts"]) == 4

    def test_no_timeout_reads_completed(self, monkeypatch, tmp_path):
        import sift_orchestrator as so
        dump = tmp_path / "ok.img"
        dump.write_bytes(b"\x00" * 128)

        def fake_run(self, memory_path, plugin, timeout=300):
            return {"ok": True, "stdout": "x" * 60, "stderr": "",
                    "timed_out": False, "timeout_used": timeout}

        monkeypatch.setattr(so.SIFTOrchestrator, "_vol3_run", fake_run)
        result = self._orch()._analyze_memory_vol3(str(dump))
        assert result["pipeline_meta"].get("pipeline_status") == "completed"
        assert result["pipeline_meta"].get("vol3_plugin_timeouts") == []
