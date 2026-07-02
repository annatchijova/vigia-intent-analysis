"""
tests/test_hash_chain_hardening.py
===================================
Red-team del hash chain unificado (vigia/core/hash_chain.py,
vigia/core/tool_log_chain.py, vigia/forensics/vigia_chain_of_custody.py).

Cada test modela un ataque concreto que ANTES del hardening pasaba en
silencio:

  A1 — editar timestamp/tool/target de una entrada del tool log (v1 solo
       protegía result_summary)
  A2 — editar el result_summary de la ÚLTIMA entrada (v1: nada encadena
       después)
  A3 — recomputar la cadena completa sin clave (SHA-256 puro es
       recomputable; el HMAC dual lo detecta)
  A4 — appendear un bundle con integrity.bundle_hash fabricado (el ledger
       confiaba en el hash declarado)
  A5 — truncation: borrar las últimas N entradas del ledger (cadena
       internamente válida; el checkpoint de punta lo detecta)
  A6 — alterar el checkpoint para ocultar A5 (HMAC del checkpoint)
  A7 — alterar un bundle en disco conservando su integrity.bundle_hash
       original (C4 confiaba en el declarado)
"""
from __future__ import annotations

import copy
import json
import sqlite3

import pytest

from vigia.core.hash_chain import (
    GENESIS_HASH,
    ChainLink,
    build_link,
    compute_entry_hash,
    verify_chain,
)
from vigia.core.tool_log_chain import (
    ToolExecutionLogChain,
    detect_chain_version,
    verify_bundle_tool_log,
    verify_tool_execution_log,
)
from vigia.forensics.vigia_chain_of_custody import (
    ChainOfCustody,
    _recompute_sealed_bundle_hash,
)

KEY = b"k" * 32
OTHER_KEY = b"x" * 32


# ──────────────────────────────────────────────────────────────────────────
# Primitiva genérica
# ──────────────────────────────────────────────────────────────────────────

def _build_chain(n: int, hmac_key: bytes | None = None) -> list[ChainLink]:
    links: list[ChainLink] = []
    prev = GENESIS_HASH
    for seq in range(1, n + 1):
        link = build_link(seq, prev, {"data": f"evento-{seq}"}, hmac_key=hmac_key)
        links.append(link)
        prev = link.entry_hash
    return links


class TestPrimitive:
    def test_valid_chain(self):
        r = verify_chain(_build_chain(5))
        assert r.valid and r.length == 5 and r.first_invalid_seq is None

    def test_empty_chain_valid(self):
        assert verify_chain([]).valid

    def test_tampered_content(self):
        links = _build_chain(5)
        links[2] = ChainLink(
            seq=links[2].seq, prev_hash=links[2].prev_hash,
            entry_hash=links[2].entry_hash, payload={"data": "ALTERADO"},
        )
        r = verify_chain(links)
        assert not r.valid
        assert r.first_invalid_seq == 3
        assert len(r.tampered_content) == 1

    def test_deleted_middle_link(self):
        links = _build_chain(5)
        del links[2]
        r = verify_chain(links)
        assert not r.valid
        assert r.seq_discontinuities
        assert r.broken_links  # el linkage también se rompe en el hueco

    def test_error_accumulation_reports_all(self):
        # Dos entradas alteradas en posiciones distintas: ambas reportadas
        links = _build_chain(6)
        for idx in (1, 4):
            links[idx] = ChainLink(
                seq=links[idx].seq, prev_hash=links[idx].prev_hash,
                entry_hash=links[idx].entry_hash, payload={"data": "X"},
            )
        r = verify_chain(links)
        assert len(r.tampered_content) == 2
        assert r.first_invalid_seq == 2

    def test_hmac_valid(self):
        r = verify_chain(_build_chain(4, hmac_key=KEY), hmac_key=KEY)
        assert r.valid and r.hmac_checked

    def test_hmac_missing_detected(self):
        r = verify_chain(_build_chain(3), hmac_key=KEY)
        assert not r.valid
        assert len(r.hmac_failures) == 3

    def test_a3_full_recompute_without_key_detected(self):
        """A3: recomputar toda la cadena tras editar contenido — hashes
        consistentes, pero el HMAC no recomputa sin la clave."""
        links = _build_chain(4, hmac_key=KEY)
        # Atacante edita seq=2 y recomputa hashes hacia adelante SIN clave
        # (o con una clave que no es la del servidor)
        payloads = [dict(l.payload) for l in links]
        payloads[1]["data"] = "REESCRITO"
        forged: list[ChainLink] = []
        prev = GENESIS_HASH
        for seq, (payload, orig) in enumerate(zip(payloads, links), start=1):
            link = build_link(seq, prev, payload, hmac_key=OTHER_KEY)
            forged.append(link)
            prev = link.entry_hash
        # Sin clave la estructura es válida — límite documentado del hash puro
        assert verify_chain(forged).valid
        # Con la clave del servidor, el HMAC delata la recomputación
        r = verify_chain(forged, hmac_key=KEY)
        assert not r.valid and r.hmac_failures


# ──────────────────────────────────────────────────────────────────────────
# tool_execution_log v1 / v2
# ──────────────────────────────────────────────────────────────────────────

def _v2_log(n: int = 3, hmac_key: bytes | None = KEY) -> list[dict]:
    chain = ToolExecutionLogChain(
        mode="claude_code", hmac_key=hmac_key, use_env_key=False
    )
    return [
        chain.append(
            tool=f"tool_{i}", target=f"/evidence/art_{i}",
            result_summary=f"resultado {i}", arguments={"i": i},
        )
        for i in range(1, n + 1)
    ]


def _v1_log(n: int = 3) -> list[dict]:
    import hashlib
    log = []
    prev_summary = None
    for seq in range(1, n + 1):
        log.append({
            "seq": seq,
            "timestamp": f"2026-07-02T00:0{seq}:00+00:00",
            "mode": "claude_code",
            "tool": f"tool_{seq}",
            "target": f"art_{seq}",
            "result_summary": f"resultado {seq}",
            "input_hash": "ab" * 32,
            "prev_hash": (
                "GENESIS" if seq == 1
                else hashlib.sha256(prev_summary.encode()).hexdigest()
            ),
        })
        prev_summary = f"resultado {seq}"
    return log


class TestToolLogChain:
    def test_v2_roundtrip_valid(self):
        log = json.loads(json.dumps(_v2_log()))  # roundtrip JSON como en un bundle
        r = verify_tool_execution_log(log, hmac_key=KEY)
        assert r.valid and r.hmac_checked

    def test_v1_legacy_still_verifies(self):
        assert detect_chain_version(_v1_log()) == "1"
        assert verify_tool_execution_log(_v1_log()).valid

    def test_v1_broken_detected(self):
        log = _v1_log()
        log[1]["result_summary"] = "EDITADO"  # rompe prev_hash de seq=3
        assert not verify_tool_execution_log(log).valid

    def test_a1_metadata_tamper_detected_in_v2(self):
        """A1: en v1 editar timestamp/tool/target era invisible."""
        for field_name in ("timestamp", "tool", "target", "input_hash"):
            log = copy.deepcopy(_v2_log())
            log[1][field_name] = "TAMPERED"
            r = verify_tool_execution_log(log)
            assert not r.valid, f"tamper de {field_name} no detectado"
            assert r.first_invalid_seq == 2

    def test_a2_last_entry_edit_detected_in_v2(self):
        """A2: en v1 la última entrada era editable (nada encadena después)."""
        log = copy.deepcopy(_v2_log())
        log[-1]["result_summary"] = "MALICE confirmed"
        assert not verify_tool_execution_log(log).valid

    def test_a3_tool_log_recompute_needs_key(self):
        log = _v2_log(hmac_key=None)  # atacante regenera el log sin clave
        assert verify_tool_execution_log(log).valid
        r = verify_tool_execution_log(log, hmac_key=KEY)
        assert not r.valid and r.hmac_failures

    def test_bundle_report_v1_carries_caveat(self):
        report = verify_bundle_tool_log({"tool_execution_log": _v1_log()})
        assert report["chain_version"] == "1"
        assert "v1_caveat" in report

    def test_result_summary_truncated_to_schema_limit(self):
        chain = ToolExecutionLogChain(hmac_key=None, use_env_key=False)
        entry = chain.append("t", "x", "R" * 500, {})
        assert len(entry["result_summary"]) == 120


# ──────────────────────────────────────────────────────────────────────────
# Ledger de bundles (ChainOfCustody)
# ──────────────────────────────────────────────────────────────────────────

def _sealed_bundle(bid: str, verdict: str = "SUSPICION") -> dict:
    bundle = {
        "bundle_id": bid,
        "timestamp": "2026-07-02T03:00:00+00:00",
        "evidence_graph": {"nodes": [1, 2, 3]},
        "decision_trace": {"verdict": verdict},
    }
    bundle["integrity"] = {"bundle_hash": _recompute_sealed_bundle_hash(bundle)}
    return bundle


@pytest.fixture()
def ledger(tmp_path):
    chain = ChainOfCustody(str(tmp_path / "chain.db"))
    yield chain
    chain.close()


class TestLedger:
    def test_genuine_bundle_appends_and_verifies(self, ledger):
        for i in range(3):
            ledger.append(_sealed_bundle(f"B-{i}"))
        ok, result = ledger.verify(verify_files=False)
        assert ok and result.total_entries == 3

    def test_a4_fabricated_declared_hash_rejected(self, ledger):
        fake = _sealed_bundle("B-FAKE")
        fake["integrity"]["bundle_hash"] = "f" * 64
        with pytest.raises(ValueError, match="no.*recomputa"):
            ledger.append(fake)

    def test_a4_content_edit_after_seal_rejected(self, ledger):
        bundle = _sealed_bundle("B-EDIT")
        bundle["decision_trace"]["verdict"] = "NOISE"  # editar post-sellado
        with pytest.raises(ValueError):
            ledger.append(bundle)

    def test_unsealed_bundle_still_accepted_legacy(self, ledger):
        # Bundles sin integrity block usan el hash legacy — compatibilidad
        entry = ledger.append({"bundle_id": "B-LEGACY", "data": [1, 2]})
        assert entry.sequence == 1

    def test_a5_truncation_detected_by_checkpoint(self, ledger):
        for i in range(4):
            ledger.append(_sealed_bundle(f"B-{i}"))
        ledger.checkpoint(hmac_key=KEY)
        db_path = ledger.db_path
        ledger.close()

        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM chain_entries WHERE sequence > 2")
        conn.commit()
        conn.close()

        reopened = ChainOfCustody(db_path)
        ok, result = reopened.verify(verify_files=False, hmac_key=KEY)
        reopened.close()
        assert not ok
        assert result.truncation_findings
        assert "TRUNCATION" in result.truncation_findings[0]["note"]

    def test_a5_without_checkpoint_truncation_is_invisible(self, ledger):
        """Documenta el límite: sin checkpoint, truncar la cola pasa.
        Este test es la justificación de exigir checkpoints periódicos."""
        for i in range(4):
            ledger.append(_sealed_bundle(f"B-{i}"))
        db_path = ledger.db_path
        ledger.close()
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM chain_entries WHERE sequence > 2")
        conn.commit()
        conn.close()
        ok, _ = ChainOfCustody(db_path).verify(verify_files=False)
        assert ok  # límite conocido — el checkpoint existe para esto

    def test_a6_checkpoint_tamper_detected(self, ledger):
        for i in range(3):
            ledger.append(_sealed_bundle(f"B-{i}"))
        ledger.checkpoint(hmac_key=KEY)
        db_path = ledger.db_path
        ledger.close()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE chain_checkpoints SET at_sequence = 1")
        conn.commit()
        conn.close()
        ok, result = ChainOfCustody(db_path).verify(
            verify_files=False, hmac_key=KEY
        )
        assert not ok
        assert any("checkpoint" in f["note"] for f in result.truncation_findings)

    def test_checkpoint_on_empty_chain_raises(self, ledger):
        with pytest.raises(ValueError, match="vacía"):
            ledger.checkpoint()

    def test_a7_disk_edit_keeping_declared_hash_detected(self, ledger, tmp_path):
        bundle = _sealed_bundle("B-DISK")
        path = tmp_path / "bundle.json"
        path.write_text(json.dumps(bundle))
        ledger.append(bundle, bundle_path=str(path))

        # Atacante edita el veredicto en disco pero conserva el
        # integrity.bundle_hash original (antes: C4 pasaba)
        tampered = json.loads(path.read_text())
        tampered["decision_trace"]["verdict"] = "NOISE"
        path.write_text(json.dumps(tampered))

        ok, result = ledger.verify(verify_files=True)
        assert not ok
        assert result.tampered_bundles

    def test_verify_result_to_dict_has_truncation_summary(self, ledger):
        ledger.append(_sealed_bundle("B-0"))
        _, result = ledger.verify(verify_files=False)
        d = result.to_dict()
        assert "truncation_findings" in d
        assert "truncations" in d["summary"]


# ──────────────────────────────────────────────────────────────────────────
# execution_logger — digests completos
# ──────────────────────────────────────────────────────────────────────────

class TestExecutionLoggerFullDigests:
    def test_hashes_are_full_sha256(self, tmp_path):
        from vigia.core.execution_logger import VigiaExecutionLogger

        logger = VigiaExecutionLogger(
            "TEST-CHAIN", output_dir=str(tmp_path),
            deterministic_timestamp="2026-07-02T00:00:00+00:00",
        )
        logger.log_tool_call("read_evidence", {"p": 1}, "ok")
        lines = [
            json.loads(line)
            for line in open(logger.log_file, encoding="utf-8")
        ]
        assert lines[0]["log_version"] == "1.1"
        for event in lines:
            assert len(event["_event_hash"]) == 64
            assert len(event["_bundle_hash_partial"]) == 64
        assert len(lines[1]["parameters_hash"]) == 64
