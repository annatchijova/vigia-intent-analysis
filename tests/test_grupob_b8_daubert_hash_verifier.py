"""
B8 (Grupo B / A-1) — verificador de daubert_record_hash.

Firstness (AUDITORIA_INVARIANTES_ASIMETRIAS §A-1, Lente 2):
`signal_adapter.py` embebe `record_hash()` como `daubert_record_hash` "para
peritaje", pero NINGÚN consumidor del árbol lo verificaba — un hash
decorativo: se presenta como garantía de integridad y nada lo chequea. Un
`lr_record` alterado post-export con el hash intacto pasaba invisible.

Fix: `verify_daubert_record_hash(exported)` en likelihood_ratio.py (misma
cuantización U7 que el productor) + SELF-CHECK en signal_adapter al construir
el export (una asimetría de serialización rompe fuerte, no en el peritaje).

Tests escritos ROJOS (el verificador no existía).
"""

import json

import pytest

from vigia.core.likelihood_ratio import ForensicRecord, verify_daubert_record_hash


def _record(**overrides):
    kw = dict(
        record_id="LR-TEST-001",
        timestamp_utc="2026-07-07T00:00:00Z",
        signals_in=[{"tool": "SDA", "z": 2.5}],
        z_scores_clipped=[2.5],
        log_lrs=[1.234567],
        correlation_matrix=[[1.0]],
        mean_correlation=0.0,
        correction_factor=1.0,
        combined_log_lr=1.234567,
        lr_combined=17.16,
        posterior_probability=0.944954,
        enfsi_label="APOYO MODERADO",
    )
    kw.update(overrides)
    return ForensicRecord(**kw)


def _export(record):
    return {
        "document_id": "DOC-1",
        "lr_record": record.to_dict(),
        "daubert_record_hash": record.record_hash(),
    }


class TestVerifier:
    def test_intact_export_verifies(self):
        ok, msg = verify_daubert_record_hash(_export(_record()))
        assert ok, msg

    def test_json_roundtrip_verifies(self):
        # El escenario del perito tercero: el export viajó como JSON.
        exported = json.loads(json.dumps(_export(_record())))
        ok, msg = verify_daubert_record_hash(exported)
        assert ok, msg

    def test_tampered_posterior_detected(self):
        exported = _export(_record())
        exported["lr_record"]["posterior_probability"] = 0.05
        ok, msg = verify_daubert_record_hash(exported)
        assert not ok and "MISMATCH" in msg

    def test_tampered_enfsi_label_detected(self):
        exported = _export(_record())
        exported["lr_record"]["enfsi_label"] = "APOYO FUERTE"
        ok, _ = verify_daubert_record_hash(exported)
        assert not ok

    def test_tampered_hash_detected(self):
        exported = _export(_record())
        exported["daubert_record_hash"] = "0" * 64
        ok, _ = verify_daubert_record_hash(exported)
        assert not ok

    def test_missing_hash_fails_closed(self):
        exported = _export(_record())
        del exported["daubert_record_hash"]
        ok, msg = verify_daubert_record_hash(exported)
        assert not ok and "ausente" in msg

    def test_missing_record_fails_closed(self):
        ok, msg = verify_daubert_record_hash({"daubert_record_hash": "x" * 64})
        assert not ok and "lr_record" in msg


class TestAdapterSelfCheck:
    def test_self_check_wired_in_adapter_source(self):
        # El self-check debe correr en el productor: una asimetría de
        # serialización (p.ej. un tipo no cuantizable nuevo) rompe al
        # construir el export, no años después en el peritaje.
        src = open("vigia/tools/signal_adapter.py").read()
        assert "verify_daubert_record_hash" in src, (
            "signal_adapter no auto-verifica el hash que embebe (A-1: "
            "hash decorativo)"
        )
