"""
tests/test_prefetch_real.py
============================
Parser de Prefetch (P1-B). Antes: solo aceptaba MAM (y en el offset
equivocado) → todo .pf clásico SCCA se descartaba en silencio; y
stem.replace("-","") nunca matcheaba la blacklist. Ahora: ambos formatos
+ extracción correcta del nombre del ejecutable.
"""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

from vigia.sift.prefetch_analyzer import PrefetchAnalyzer


def _scca(path: Path, name: str, version: int = 30):
    """Prefetch clásico SCCA: version en offset 0, 'SCCA' en offset 4."""
    (path / name).write_bytes(struct.pack("<I", version) + b"SCCA" + b"\x00" * 120)


def _mam(path: Path, name: str):
    """Prefetch comprimido Win10: 'MAM\\x04' en offset 0."""
    (path / name).write_bytes(b"MAM\x04" + b"\x00" * 120)


class TestExecutableName:
    @pytest.mark.parametrize("stem,expected", [
        ("MIMIKATZ.EXE-1A2B3C4D", "MIMIKATZ.EXE"),
        ("PSEXEC.EXE-DEADBEEF", "PSEXEC.EXE"),
        ("NOTEPAD.EXE-11223344", "NOTEPAD.EXE"),
        ("foo-bar", "foo-bar"),             # sufijo no es 8-hex → sin cambios
        ("a.exe-DEADBEEF", "a.exe"),
        ("SINGLE", "SINGLE"),
    ])
    def test_name_extraction(self, stem, expected):
        assert PrefetchAnalyzer._executable_name(stem) == expected


class TestFormatAcceptance:
    def test_scca_classic_detected(self, tmp_path):
        # El formato clásico ANTES se descartaba entero.
        _scca(tmp_path, "MIMIKATZ.EXE-1A2B3C4D.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "mimikatz.exe" in names
        assert r.unparsed_files == 0

    def test_mam_compressed_detected(self, tmp_path):
        _mam(tmp_path, "PSEXEC.EXE-DEADBEEF.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "psexec.exe" in names

    def test_benign_executable_not_flagged(self, tmp_path):
        _scca(tmp_path, "NOTEPAD.EXE-11223344.pf")
        # Añadir relleno para no disparar el heurístico PREFETCH_WIPE (<10)
        for i in range(12):
            _scca(tmp_path, f"APP{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        assert not r.suspicious_executions

    def test_invalid_signature_counts_unparsed(self, tmp_path):
        (tmp_path / "GARBAGE.EXE-00000000.pf").write_bytes(b"\xff" * 100)
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        assert r.unparsed_files == 1

    def test_all_unparseable_marks_unanalyzed(self, tmp_path):
        for i in range(3):
            (tmp_path / f"X{i}.EXE-0000000{i}.pf").write_bytes(b"\xff" * 50)
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        assert r.to_signal().metadata["unanalyzed"] is True

    def test_partial_parse_not_unanalyzed(self, tmp_path):
        _scca(tmp_path, "MIMIKATZ.EXE-1A2B3C4D.pf")
        (tmp_path / "BAD.EXE-00000000.pf").write_bytes(b"\xff" * 50)
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        # Al menos uno parseó → no es "no analizado"
        assert r.to_signal().metadata["unanalyzed"] is False


class TestB132CalibrationFix:
    """B-132: sdelete → anti_forensic_deletions (z=3.2); smallftpd/netstumbler/
    veracrypt → suspicious_executions.  Confirmed missing from lists in
    VIGIA-REAL-VANKO-2026 corrida RAW 2026-07-14, causing PREFETCH_ANALYZER
    to miss anti-forensic evidence and contributing to ABSTAIN verdict."""

    def test_sdelete_goes_to_anti_forensic_not_suspicious(self, tmp_path):
        # sdelete.exe must route to anti_forensic_deletions (z=3.2 path),
        # NOT suspicious_executions (which was already saturated with RUNDLL32 hits).
        _scca(tmp_path, "SDELETE.EXE-FBA93810.pf")
        for i in range(12):  # avoid PREFETCH_WIPE heuristic
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        af_names = [a["filename"].lower() for a in r.anti_forensic_deletions]
        susp_names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "sdelete.exe" in af_names, "sdelete must be in anti_forensic_deletions"
        assert "sdelete.exe" not in susp_names, "sdelete must NOT double-count in suspicious"
        assert any(a["type"] == "ANTI_FORENSIC_TOOL_EXECUTION" for a in r.anti_forensic_deletions)

    def test_sdelete_triggers_z32_path(self, tmp_path):
        # anti_forensic_deletions non-empty → to_signal() must emit z=3.2
        _scca(tmp_path, "SDELETE.EXE-FBA93810.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        sig = r.to_signal()
        assert sig.z_score == 3.2, f"Expected z=3.2 got z={sig.z_score}"

    def test_sdelete64_also_anti_forensic(self, tmp_path):
        _scca(tmp_path, "SDELETE64.EXE-AABBCCDD.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        af_names = [a["filename"].lower() for a in r.anti_forensic_deletions]
        assert "sdelete64.exe" in af_names

    def test_smallftpd_goes_to_suspicious(self, tmp_path):
        _scca(tmp_path, "SMALLFTPD.EXE-CF55BE9B.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        susp_names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "smallftpd.exe" in susp_names

    def test_netstumbler_goes_to_suspicious(self, tmp_path):
        _scca(tmp_path, "NETSTUMBLER.EXE-C14B26F4.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        susp_names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "netstumbler.exe" in susp_names

    def test_veracrypt_format_goes_to_suspicious(self, tmp_path):
        # Stem has a space: "VERACRYPT FORMAT.EXE-6EA86AF5"
        _scca(tmp_path, "VERACRYPT FORMAT.EXE-6EA86AF5.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        susp_names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "veracrypt format.exe" in susp_names

    def test_existing_mimikatz_still_in_suspicious(self, tmp_path):
        # Regression: adding new lists must not remove mimikatz from suspicious_executions
        _scca(tmp_path, "MIMIKATZ.EXE-1A2B3C4D.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        susp_names = [s["filename"].lower() for s in r.suspicious_executions]
        assert "mimikatz.exe" in susp_names

    def test_finding_type_in_metadata(self, tmp_path):
        # to_signal() metadata must include ANTI_FORENSIC_TOOL_EXECUTION
        # and SUSPICIOUS_EXECUTION in finding_types when both fire
        _scca(tmp_path, "SDELETE.EXE-FBA93810.pf")
        _scca(tmp_path, "SMALLFTPD.EXE-CF55BE9B.pf")
        for i in range(12):
            _scca(tmp_path, f"BENIGN{i}.EXE-{i:08X}.pf")
        r = PrefetchAnalyzer().analyze_directory(str(tmp_path))
        meta = r.to_signal().metadata
        assert "ANTI_FORENSIC_TOOL_EXECUTION" in meta["finding_types"]
        assert "SUSPICIOUS_EXECUTION" in meta["finding_types"]


class TestAgentWiring:
    def test_build_kwargs_detects_prefetch_dir(self, tmp_path):
        from vigia_agent import _build_orchestrator_kwargs
        pf = tmp_path / "Prefetch"
        pf.mkdir()
        _scca(pf, "MIMIKATZ.EXE-1A2B3C4D.pf")
        kwargs = _build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("prefetch_dir") == str(pf)
