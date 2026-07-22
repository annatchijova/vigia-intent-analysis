"""B-208: recover real last_execution_time/run_count from MAM-compressed
(Win10+) prefetch via pyscca (libscca-python), instead of the fixed
"unknown"/1 placeholders _parse_pf previously returned for every modern
prefetch file. pyscca already implements XPRESS Huffman decompression and
SCCA-structure parsing correctly (the reference implementation real
forensic tools use) — it is an OPTIONAL enrichment (compiled extension, not
pure pip), so Mode 1 stays offline/zero-dependency without it, degrading
only these two fields, never the signature-based detection path.

These tests mock pyscca rather than depend on evidence/ (gitignored, local
forensic data only) — the FILETIME conversion is checked against the
well-known constant 116444736000000000 (100ns ticks from 1601-01-01 to the
Unix epoch), independently verifiable without trusting this module's own math.
"""

from __future__ import annotations

import struct
from pathlib import Path
from unittest import mock

import pytest

import vigia.sift.prefetch_analyzer as pf_mod
from vigia.sift.prefetch_analyzer import PrefetchAnalyzer, _enrich_via_pyscca

# 100ns ticks between the FILETIME epoch (1601-01-01) and the Unix epoch —
# a widely-cited, independently verifiable constant.
_UNIX_EPOCH_AS_FILETIME = 116444736000000000


def _write_mam(path: Path) -> None:
    path.write_bytes(b"MAM\x04" + b"\x00" * 120)


class _FakeSccaFile:
    """Stands in for pyscca.file() with controllable run_count/last-run-times."""

    def __init__(self, run_count: int, last_run_times: dict):
        self._run_count = run_count
        self._last_run_times = last_run_times
        self.run_count = run_count

    def open(self, path):
        pass

    def get_last_run_time_as_integer(self, slot: int) -> int:
        return self._last_run_times.get(slot, 0)

    def close(self):
        pass


class TestFiletimeConversion:
    def test_known_filetime_constant_maps_to_unix_epoch(self, tmp_path, monkeypatch):
        pf = tmp_path / "APP.EXE-11223344.pf"
        _write_mam(pf)
        fake = _FakeSccaFile(run_count=3, last_run_times={0: _UNIX_EPOCH_AS_FILETIME})
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", True)
        monkeypatch.setattr(pf_mod, "pyscca", mock.Mock(file=lambda: fake))
        result = _enrich_via_pyscca(pf)
        assert result == ("1970-01-01T00:00:00.000Z", 3)

    def test_takes_the_most_recent_of_multiple_slots(self, tmp_path, monkeypatch):
        pf = tmp_path / "APP.EXE-11223344.pf"
        _write_mam(pf)
        earlier = _UNIX_EPOCH_AS_FILETIME
        later = _UNIX_EPOCH_AS_FILETIME + 10_000_000  # +1 second in 100ns ticks
        fake = _FakeSccaFile(run_count=2, last_run_times={0: later, 1: earlier})
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", True)
        monkeypatch.setattr(pf_mod, "pyscca", mock.Mock(file=lambda: fake))
        result = _enrich_via_pyscca(pf)
        assert result == ("1970-01-01T00:00:01.000Z", 2)


class TestGracefulDegradation:
    def test_pyscca_unavailable_returns_none(self, tmp_path, monkeypatch):
        pf = tmp_path / "APP.EXE-11223344.pf"
        _write_mam(pf)
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", False)
        assert _enrich_via_pyscca(pf) is None

    def test_pyscca_raising_on_garbage_returns_none_not_crash(self, tmp_path, monkeypatch):
        pf = tmp_path / "APP.EXE-11223344.pf"
        _write_mam(pf)

        class _RaisingSccaFile:
            def open(self, path):
                raise OSError("simulated: unable to read compressed blocks")

        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", True)
        monkeypatch.setattr(pf_mod, "pyscca", mock.Mock(file=lambda: _RaisingSccaFile()))
        assert _enrich_via_pyscca(pf) is None

    def test_all_zero_slots_returns_none(self, tmp_path, monkeypatch):
        pf = tmp_path / "APP.EXE-11223344.pf"
        _write_mam(pf)
        fake = _FakeSccaFile(run_count=0, last_run_times={})
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", True)
        monkeypatch.setattr(pf_mod, "pyscca", mock.Mock(file=lambda: fake))
        assert _enrich_via_pyscca(pf) is None


class TestParsePfIntegration:
    def test_parse_pf_uses_enrichment_when_available(self, tmp_path, monkeypatch):
        pf = tmp_path / "PIDGIN.EXE-11223344.pf"
        _write_mam(pf)
        fake = _FakeSccaFile(run_count=7, last_run_times={0: _UNIX_EPOCH_AS_FILETIME})
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", True)
        monkeypatch.setattr(pf_mod, "pyscca", mock.Mock(file=lambda: fake))
        record = PrefetchAnalyzer()._parse_pf(pf)
        assert record.filename == "PIDGIN.EXE"
        assert record.run_count == 7
        assert record.last_execution_time == "1970-01-01T00:00:00.000Z"

    def test_parse_pf_falls_back_to_placeholders_without_pyscca(self, tmp_path, monkeypatch):
        pf = tmp_path / "PIDGIN.EXE-11223344.pf"
        _write_mam(pf)
        monkeypatch.setattr(pf_mod, "_PYSCCA_AVAILABLE", False)
        record = PrefetchAnalyzer()._parse_pf(pf)
        # Signature-valid file still parses — only the two enriched fields degrade.
        assert record.filename == "PIDGIN.EXE"
        assert record.last_execution_time == "unknown"
        assert record.run_count == 1

    def test_synthetic_garbage_scca_still_parses_via_signature_check(self, tmp_path, monkeypatch):
        # Regression guard: a signature-valid but structurally-garbage file
        # (as used by tests/test_prefetch_real.py's fixtures) must not be
        # counted as unparsed just because pyscca cannot read its internals.
        pf = tmp_path / "MIMIKATZ.EXE-1A2B3C4D.pf"
        pf.write_bytes(struct.pack("<I", 30) + b"SCCA" + b"\x00" * 120)
        record = PrefetchAnalyzer()._parse_pf(pf)
        assert record.filename == "MIMIKATZ.EXE"


@pytest.mark.skipif(not pf_mod._PYSCCA_AVAILABLE, reason="pyscca not installed in this environment")
class TestPysccaActuallyInstalled:
    def test_real_pyscca_module_exposes_expected_api(self):
        # Sanity check against the real library (when present) — confirms
        # the mocked interface above matches the real one. run_count is a
        # property that requires an opened file to read, so it is checked
        # via dir() rather than hasattr() (which would evaluate it eagerly).
        f = pf_mod.pyscca.file()
        assert hasattr(f, "open")
        assert "run_count" in dir(f)
        assert hasattr(f, "get_last_run_time_as_integer")
