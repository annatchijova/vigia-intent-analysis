"""
tests/test_mft_parser_real.py
==============================
Parser de $MFT binario (P0-C). Antes: MFTTimelineAnalyzer esperaba JSON
pre-extraído que nada producía en modo agente → disco/MFT ciego (falso
negativo). Ahora: parser stdlib de $MFT → JSON, cableado en el agente.
"""
from __future__ import annotations

import json
import struct

import pytest

from vigia.sift.mft_parser import parse_mft_bytes, parse_mft_file, _filetime_to_iso

_FT_EPOCH = 11644473600
_HNS = 10_000_000


def _to_ft(unix: int) -> int:
    return int((unix + _FT_EPOCH) * _HNS)


def _build_record(name: str, si_unix, fn_unix, hardlinks=1, ads=None, in_use=True):
    """Construye un registro FILE de 1024 bytes con SI + FN (+ ADS opcional)."""
    rec = bytearray(1024)
    rec[0:4] = b"FILE"
    struct.pack_into("<H", rec, 0x12, hardlinks)
    first_attr = 0x38
    struct.pack_into("<H", rec, 0x14, first_attr)
    struct.pack_into("<H", rec, 0x16, 0x01 if in_use else 0x00)
    off = first_attr
    hdr_len = 24

    # $STANDARD_INFORMATION
    si = struct.pack("<QQQQ", *[_to_ft(t) for t in si_unix])
    total = hdr_len + len(si)
    struct.pack_into("<I", rec, off, 0x10)
    struct.pack_into("<I", rec, off + 4, total)
    rec[off + 8] = 0
    struct.pack_into("<I", rec, off + 16, len(si))
    struct.pack_into("<H", rec, off + 20, hdr_len)
    rec[off + 24:off + 24 + len(si)] = si
    off += total

    # $FILE_NAME
    nb = name.encode("utf-16-le")
    fn = bytearray(66 + len(nb))
    struct.pack_into("<QQQQ", fn, 8, *[_to_ft(t) for t in fn_unix])
    fn[64] = len(name)
    fn[65] = 1  # namespace Win32
    fn[66:66 + len(nb)] = nb
    total = hdr_len + len(fn)
    struct.pack_into("<I", rec, off, 0x30)
    struct.pack_into("<I", rec, off + 4, total)
    rec[off + 8] = 0
    struct.pack_into("<I", rec, off + 16, len(fn))
    struct.pack_into("<H", rec, off + 20, hdr_len)
    rec[off + 24:off + 24 + len(fn)] = fn
    off += total

    # $DATA con nombre (ADS): asignar espacio suficiente para el nombre
    if ads:
        an = ads.encode("utf-16-le")
        name_off = 24
        total = name_off + len(an) + 8
        struct.pack_into("<I", rec, off, 0x80)
        struct.pack_into("<I", rec, off + 4, total)
        rec[off + 8] = 0
        rec[off + 9] = len(ads)
        struct.pack_into("<H", rec, off + 10, name_off)
        rec[off + name_off:off + name_off + len(an)] = an
        off += total

    struct.pack_into("<I", rec, off, 0xFFFFFFFF)  # fin de atributos
    return bytes(rec)


class TestFiletime:
    def test_epoch_conversion(self):
        # 2020-01-01T00:00:00Z = unix 1577836800
        assert _filetime_to_iso(_to_ft(1577836800)).startswith("2020-01-01T00:00:00")

    def test_zero_is_empty(self):
        assert _filetime_to_iso(0) == ""

    def test_corrupt_out_of_range_empty(self):
        assert _filetime_to_iso(1) == ""


class TestParse:
    def test_basic_record(self):
        mft = _build_record("evil.exe", [1577836800] * 4, [1577836800] * 4)
        out = parse_mft_bytes(mft)
        assert len(out["entries"]) == 1
        e = out["entries"][0]
        assert e["filename"] == "evil.exe"
        assert e["record_number"] == 0
        assert len(e["si_times"]) == 4 and len(e["fn_times"]) == 4
        assert e["si_times"][0].startswith("2020-01-01")

    def test_timestomp_si_fn_mismatch_detected(self):
        # SI created=2020 pero FN created=2024 → timestomping clásico
        mft = _build_record("MFT", [1577836800] * 4, [1577836800] * 4) + \
              _build_record("evil.exe", [1577836800] * 4, [1704067200] * 4)
        out = parse_mft_bytes(mft)
        from vigia.sift.disk_forensics import MFTTimelineAnalyzer
        res = MFTTimelineAnalyzer().analyze(mft, json.dumps(out))
        assert res.total_entries == 2
        assert len(res.timestomp_entries) >= 1
        assert res.to_signal().z_score > 0

    def test_ads_extracted(self):
        mft = _build_record("evil.exe", [1577836800] * 4, [1577836800] * 4, ads="hidden")
        out = parse_mft_bytes(mft)
        assert out["entries"][0]["ads"] == ["hidden"]

    def test_hardlink_count(self):
        mft = _build_record("evil.exe", [1577836800] * 4, [1577836800] * 4, hardlinks=5)
        assert parse_mft_bytes(mft)["entries"][0]["hardlink_count"] == 5

    def test_non_file_records_skipped(self):
        good = _build_record("a.txt", [1577836800] * 4, [1577836800] * 4)
        junk = b"\x00" * 1024        # registro libre (no 'FILE')
        out = parse_mft_bytes(good + junk + good)
        assert len(out["entries"]) == 2   # solo los FILE

    def test_empty_input(self):
        assert parse_mft_bytes(b"") == {"entries": []}

    def test_deterministic(self):
        mft = _build_record("x", [1577836800] * 4, [1577836800] * 4)
        assert parse_mft_bytes(mft) == parse_mft_bytes(mft)

    def test_parse_file(self, tmp_path):
        mft = _build_record("evil.exe", [1577836800] * 4, [1704067200] * 4)
        p = tmp_path / "$MFT"
        p.write_bytes(mft)
        result = json.loads(parse_mft_file(str(p)))
        assert result["entries"][0]["filename"] == "evil.exe"


class TestAgentWiring:
    def test_build_kwargs_detects_mft(self, tmp_path):
        from vigia_agent import _build_orchestrator_kwargs
        mft = _build_record("evil.exe", [1577836800] * 4, [1704067200] * 4)
        (tmp_path / "$MFT").write_bytes(mft)
        kwargs = _build_orchestrator_kwargs(tmp_path, {})
        assert kwargs.get("mft_path", "").endswith("$MFT")

    def test_shim_parses_mft_to_json(self, tmp_path):
        # El shim debe parsear el $MFT y alimentar el analyzer (timestomp).
        from sift_orchestrator import SIFTOrchestrator
        mft = _build_record("MFT", [1577836800] * 4, [1577836800] * 4) + \
              _build_record("evil.exe", [1577836800] * 4, [1704067200] * 4)
        p = tmp_path / "$MFT"
        p.write_bytes(mft)
        r = SIFTOrchestrator("MFT-CASE").analyze(mft_path=str(p))
        disk = r.get("results", {}).get("disk", {})
        # El motor de disco produjo señal a partir del MFT parseado.
        assert disk.get("artifact_type") == "mft"
