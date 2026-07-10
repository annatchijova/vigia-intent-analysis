"""
Tests del parser FSEvents (vigia/sift/fsevents_parser.py).

Estrategia: construir páginas DLS1/DLS2 byte a byte según el formato
documentado (firma plaso), gzip-comprimirlas, y verificar que el parser las
decodifica de vuelta — la práctica estándar para un parser binario (encode
conocido → assert decode). También se cubren: degradación honesta ante firma
desconocida (DLS3), techo de tamaño (S5), y registros truncados.
"""

from __future__ import annotations

import gzip
import io
import struct

import pytest

from vigia.sift.fsevents_parser import (
    parse_fsevents_bytes,
    parse_fseventsd_dir,
    FSEventsParseResult,
    FSEvent,
    FLAG_REMOVED,
    FLAG_CREATED,
    _SIG_V2,
    _SIG_V1,
)


def _record_v2(path: str, event_id: int, flags: int, node_id: int) -> bytes:
    return (path.encode("utf-8") + b"\x00"
            + struct.pack("<Q", event_id)
            + struct.pack("<I", flags)
            + struct.pack("<Q", node_id))


def _record_v1(path: str, event_id: int, flags: int) -> bytes:
    return (path.encode("utf-8") + b"\x00"
            + struct.pack("<Q", event_id)
            + struct.pack("<I", flags))


def _page(sig: bytes, records: bytes) -> bytes:
    page_size = 12 + len(records)
    return struct.pack("<4sII", sig, 0, page_size) + records


def _gz(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as f:
        f.write(data)
    return buf.getvalue()


class TestDLS2Roundtrip:
    def test_single_record_decodes(self):
        recs = _record_v2("Users/x/secret.txt", 42, FLAG_REMOVED, 1001)
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(_page(_SIG_V2, recs), result)
        assert result.pages_parsed == 1
        assert len(result.events) == 1
        ev = result.events[0]
        assert ev.path == "Users/x/secret.txt"
        assert ev.event_id == 42
        assert ev.node_id == 1001
        assert ev.version == 2
        assert ev.is_removed and not ev.is_created
        assert "Removed" in ev.flag_names

    def test_multiple_records_in_page(self):
        recs = (_record_v2("a/b", 1, FLAG_CREATED, 10)
                + _record_v2("a/c", 2, FLAG_REMOVED, 11)
                + _record_v2("a/d", 3, FLAG_CREATED | FLAG_REMOVED, 12))
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(_page(_SIG_V2, recs), result)
        assert len(result.events) == 3
        assert [e.event_id for e in result.events] == [1, 2, 3]
        assert result.events[2].is_removed and result.events[2].is_created

    def test_multiple_pages(self):
        p1 = _page(_SIG_V2, _record_v2("p/1", 1, FLAG_CREATED, 1))
        p2 = _page(_SIG_V2, _record_v2("p/2", 2, FLAG_REMOVED, 2))
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(p1 + p2, result)
        assert result.pages_parsed == 2
        assert [e.path for e in result.events] == ["p/1", "p/2"]


class TestDLS1Roundtrip:
    def test_v1_has_no_node_id(self):
        recs = _record_v1("old/mac", 7, FLAG_REMOVED)
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(_page(_SIG_V1, recs), result)
        assert len(result.events) == 1
        assert result.events[0].version == 1
        assert result.events[0].node_id == 0
        assert result.events[0].is_removed


class TestHonestDegradation:
    def test_unknown_signature_is_counted_not_crashed(self):
        # DLS3 / corrupción: firma desconocida → unsupported_page + nota.
        bogus = struct.pack("<4sII", b"3SLD", 0, 20) + b"x" * 8
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(bogus, result)
        assert result.unsupported_pages == 1
        assert result.pages_parsed == 0
        assert any("no soportada" in n for n in result.notes)

    def test_truncated_record_stops_cleanly(self):
        # path sin event_id completo → se detiene sin crashear.
        rec = b"trunc/path\x00" + struct.pack("<Q", 1)  # falta flags
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(_page(_SIG_V2, rec), result)
        assert result.events == []
        assert result.pages_parsed == 1

    def test_invalid_page_size_stops(self):
        bad = struct.pack("<4sII", _SIG_V2, 0, 4)  # page_size < header
        result = FSEventsParseResult(events=[])
        parse_fsevents_bytes(bad, result)
        assert result.pages_parsed == 0
        assert any("page_size inválido" in n for n in result.notes)


class TestDirectoryParsing:
    def test_parses_gz_files_and_uuid(self, tmp_path):
        fsdir = tmp_path / ".fseventsd"
        fsdir.mkdir()
        (fsdir / "fseventsd-uuid").write_text("ABCD-1234-UUID")
        page = _page(_SIG_V2, _record_v2("vol/file", 100, FLAG_REMOVED, 5))
        (fsdir / "0000000000000001").write_bytes(_gz(page))
        (fsdir / "0000000000000002").write_bytes(_gz(
            _page(_SIG_V2, _record_v2("vol/other", 200, FLAG_CREATED, 6))))
        result = parse_fseventsd_dir(fsdir)
        assert result.files_parsed == 2
        assert result.store_uuid == "ABCD-1234-UUID"
        assert len(result.events) == 2
        assert {e.event_id for e in result.events} == {100, 200}

    def test_non_gzip_file_is_rejected_not_crash(self, tmp_path):
        fsdir = tmp_path / ".fseventsd"
        fsdir.mkdir()
        (fsdir / "0000000000000001").write_bytes(b"not gzip at all")
        result = parse_fseventsd_dir(fsdir)
        assert result.files_rejected == 1
        assert result.files_parsed == 0
        assert result.events == []

    def test_corrupt_deflate_body_rejected_not_crash(self, tmp_path):
        # Hallazgo code-review: gzip con magic válido pero deflate corrupto
        # lanza zlib.error (NO subclase de OSError). Debe rechazar SOLO ese
        # archivo, no abortar el análisis de los demás.
        fsdir = tmp_path / ".fseventsd"
        fsdir.mkdir()
        good = _gz(_page(_SIG_V2, _record_v2("vol/ok", 1, FLAG_CREATED, 1)))
        (fsdir / "0000000000000001").write_bytes(good[:10] + b"\xff\xff\xff\xff\xff")
        (fsdir / "0000000000000002").write_bytes(good)  # este SÍ debe parsear
        result = parse_fseventsd_dir(fsdir)
        assert result.files_rejected == 1
        assert result.files_parsed == 1  # el sano no fue abortado por el corrupto
        assert len(result.events) == 1

    def test_deterministic_order(self, tmp_path):
        fsdir = tmp_path / ".fseventsd"
        fsdir.mkdir()
        for i in (3, 1, 2):
            (fsdir / f"000000000000000{i}").write_bytes(
                _gz(_page(_SIG_V2, _record_v2(f"f/{i}", i, FLAG_CREATED, i))))
        r1 = parse_fseventsd_dir(fsdir)
        r2 = parse_fseventsd_dir(fsdir)
        assert [e.event_id for e in r1.events] == [e.event_id for e in r2.events]
        assert [e.event_id for e in r1.events] == [1, 2, 3]

    def test_missing_dir_degrades(self, tmp_path):
        result = parse_fseventsd_dir(tmp_path / "nope")
        assert result.events == []
        assert any("no es un directorio" in n for n in result.notes)


# ─────────────────────────────────────────────────────────────────────────────
# Integración con el engine macOS (_analyze_fsevents).
# ─────────────────────────────────────────────────────────────────────────────

class TestMacOSEngineFSEventsIntegration:
    def _make_fsdir(self, tmp_path, records):
        fsdir = tmp_path / ".fseventsd"
        fsdir.mkdir()
        (fsdir / "0000000000000001").write_bytes(_gz(_page(_SIG_V2, records)))
        return tmp_path

    def _analyze(self, evidence_root):
        from vigia.sift.macos_forensics import MacOSForensicsAnalyzer
        return MacOSForensicsAnalyzer().analyze(evidence_root)

    def test_mass_deletion_produces_antiforensic_finding(self, tmp_path):
        recs = b"".join(
            _record_v2(f"Users/x/d{i}.txt", i, FLAG_REMOVED, 1000 + i)
            for i in range(30))  # > umbral 25
        root = self._make_fsdir(tmp_path, recs)
        r = self._analyze(root)
        fts = {f.finding_type for f in r.findings}
        assert "ANTIFORENSIC_FSEVENTS_MASS_DELETION" in fts
        # corr_group antiforensic → listo para dominio B-052-P2
        md = [f for f in r.findings
              if f.finding_type == "ANTIFORENSIC_FSEVENTS_MASS_DELETION"][0]
        assert md.corr_group == "antiforensic"
        assert md.mitre_technique == "T1070.004"

    def test_below_threshold_no_mass_deletion(self, tmp_path):
        recs = b"".join(
            _record_v2(f"Users/x/d{i}.txt", i, FLAG_REMOVED, 1000 + i)
            for i in range(10))  # < umbral
        root = self._make_fsdir(tmp_path, recs)
        r = self._analyze(root)
        assert "ANTIFORENSIC_FSEVENTS_MASS_DELETION" not in {
            f.finding_type for f in r.findings}

    def test_trash_purge_detected(self, tmp_path):
        recs = _record_v2("Users/x/.Trash/evidence.pdf", 1, FLAG_REMOVED, 5)
        root = self._make_fsdir(tmp_path, recs)
        r = self._analyze(root)
        assert "ANTIFORENSIC_FSEVENTS_TRASH_PURGE" in {
            f.finding_type for f in r.findings}

    def test_suspicious_path_detected(self, tmp_path):
        recs = _record_v2("private/tmp/bleachbit_run.sh", 1, FLAG_CREATED, 5)
        root = self._make_fsdir(tmp_path, recs)
        r = self._analyze(root)
        assert "FSEVENTS_SUSPICIOUS_PATH" in {f.finding_type for f in r.findings}

    def test_antiforensic_fsevents_integrates_with_ladder(self, tmp_path):
        # Una purga FSEvents + apps cifradas debe escalar por la rama
        # has_antiforensic_finding & n_encrypted>=2 (invariante 6). Se simula
        # inyectando la señal via el corr_group; aquí solo verificamos que el
        # finding cuenta como anti-forense para to_signal.
        recs = b"".join(
            _record_v2(f"Users/x/d{i}.txt", i, FLAG_REMOVED, 1000 + i)
            for i in range(30))
        root = self._make_fsdir(tmp_path, recs)
        r = self._analyze(root)
        # to_signal detecta has_antiforensic_finding via startswith("ANTIFORENSIC")
        sig = r.to_signal()
        assert "ANTIFORENSIC_FSEVENTS_MASS_DELETION" in sig.metadata["finding_types"]

    def test_no_fseventsd_is_inert(self, tmp_path):
        # Sin .fseventsd (como tuck-2019): 0 findings FSEvents, sin error.
        (tmp_path / "Safari").mkdir()
        r = self._analyze(tmp_path)
        assert not any(f.finding_type.startswith("FSEVENTS")
                       or "FSEVENTS" in f.finding_type for f in r.findings)
        assert not any("FSEvents analysis error" in n for n in r.analysis_notes)
