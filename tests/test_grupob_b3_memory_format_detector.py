"""
B3 (Grupo B / B-016 residual) — detector de formato stderr portado al motor V4.

Firstness: el shim del agente (sift_orchestrator.py:810-843) ya detecta en
stderr los marcadores de "no es un RAM dump válido" (InvalidAddressException,
no valid kernel, vmware, snapshot, ...) y degrada a FORMAT_NOT_SUPPORTED →
ABSTAIN. El motor V4 (vigia/sift/memory_forensics.py::_run_plugin) devolvía
[] SILENCIOSO ante el mismo stderr → 0 procesos → 0 findings → la señal leía
"limpio" (falso negativo de la familia P0-A: incapacidad de análisis
presentada como benignidad).

Test escrito ROJO: con vol3 fallando por formato, el resultado V4 debe quedar
marcado format_not_supported/unanalyzed — no limpio.
"""

from fractions import Fraction

import pytest

import vigia.sift.memory_forensics as mf


@pytest.fixture()
def engine(monkeypatch):
    """MemoryForensicsEngine sin binario vol real."""
    monkeypatch.setattr(mf.Volatility3Interface, "_validate_binary",
                        staticmethod(lambda b: "/fake/vol"))
    monkeypatch.setattr(mf.Volatility3Interface, "_detect_version",
                        lambda self: "2.7.0")
    return mf.MemoryForensicsEngine(vol_binary="/fake/vol", hash_dump=False)


_VMWARE_STDERR = (
    "volatility3.framework.exceptions.InvalidAddressException: "
    "Offset outside of the buffer boundaries — no valid kernel found. "
    "Is this a VMware snapshot?"
)


def _fail_format(*a, **k):
    return {"returncode": 1, "stdout": "", "stderr": _VMWARE_STDERR}


class TestStderrClassifier:
    def test_format_markers_detected(self):
        assert mf.classify_vol3_stderr(_VMWARE_STDERR) == "FORMAT_NOT_SUPPORTED"
        assert mf.classify_vol3_stderr(
            "Unable to determine the memory layout") == "FORMAT_NOT_SUPPORTED"

    def test_ordinary_errors_not_format(self):
        assert mf.classify_vol3_stderr("plugin crashed: KeyError") is None
        assert mf.classify_vol3_stderr("") is None


class TestEngineDegradation:
    def test_format_failure_marks_unanalyzed_not_clean(self, engine, monkeypatch, tmp_path):
        dump = tmp_path / "evil.img"
        dump.write_bytes(b"\x00" * 128)
        monkeypatch.setattr(mf, "ALLOWED_BASE_PATHS", [tmp_path])

        def fake_run(cmd, **kw):
            class R:
                returncode = 1
                stdout = ""
                stderr = _VMWARE_STDERR
            return R()

        monkeypatch.setattr(mf.subprocess, "run", fake_run)
        result = engine.analyze(str(dump))

        # El defecto exacto: antes esto era un resultado "limpio" (0 findings,
        # sin marca) — indistinguible de un dump genuinamente benigno.
        assert result.format_not_supported, (
            "vol3 rechazó el formato y el motor V4 lo presentó como analizado"
        )
        assert any("FORMAT_NOT_SUPPORTED" in n for n in result.analysis_notes)

        sig = result.to_signal()
        assert sig.metadata.get("unanalyzed") is True, (
            "la señal debe marcar unanalyzed=True — 0 hallazgos aquí NO es "
            "evidencia de benignidad (contrato del orchestrator)"
        )
        assert sig.metadata.get("format_error") == "FORMAT_NOT_SUPPORTED"
        assert sig.z_score == 0.0 and sig.confidence == 0.0

    def test_ordinary_plugin_failure_still_soft(self, engine, monkeypatch, tmp_path):
        # Un fallo NO-formato conserva el contrato previo: [] blando por
        # plugin, resultado normal (puede haber señales de otros plugins).
        dump = tmp_path / "ok.img"
        dump.write_bytes(b"\x00" * 128)
        monkeypatch.setattr(mf, "ALLOWED_BASE_PATHS", [tmp_path])

        def fake_run(cmd, **kw):
            class R:
                returncode = 1
                stdout = ""
                stderr = "KeyError: 'layer'"
            return R()

        monkeypatch.setattr(mf.subprocess, "run", fake_run)
        result = engine.analyze(str(dump))
        assert not result.format_not_supported
        assert result.to_signal().metadata.get("unanalyzed") is not True

    def test_clean_result_unaffected(self, engine, monkeypatch, tmp_path):
        dump = tmp_path / "clean.img"
        dump.write_bytes(b"\x00" * 128)
        monkeypatch.setattr(mf, "ALLOWED_BASE_PATHS", [tmp_path])

        def fake_run(cmd, **kw):
            class R:
                returncode = 0
                stdout = '{"columns": [], "rows": []}'
                stderr = ""
            return R()

        monkeypatch.setattr(mf.subprocess, "run", fake_run)
        result = engine.analyze(str(dump))
        assert not result.format_not_supported
        assert result.composite_score == Fraction(0)
