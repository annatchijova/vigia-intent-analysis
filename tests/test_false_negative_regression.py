"""
tests/test_false_negative_regression.py
=========================================
Regresión de los falsos negativos del modo agente documentados en
AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md.

Invariante central: en modo agente, un error de extracción, una dependencia
ausente, o un artefacto no analizado deben producir ABSTAIN (exit 4), NUNCA
un veredicto benigno (exit 0). Benigno afirma "analizado y limpio"; ABSTAIN
afirma "no se pudo determinar". Confundirlos es el falso-negativo raíz.
"""
from __future__ import annotations

import os

import pytest

from vigia_agent import (
    EXIT_ABSTAIN,
    EXIT_INTENT,
    EXIT_MALICE,
    EXIT_NOISE,
    classify_agent_verdict,
    _VERDICT_EXIT,
)


# ──────────────────────────────────────────────────────────────────────────
# P0-A — ABSTAIN como exit code 4
# ──────────────────────────────────────────────────────────────────────────

class TestVerdictClassification:
    @pytest.mark.parametrize("hyp", [
        "PIPELINE_ERROR",
        "PIPELINE_UNAVAILABLE",
        "FORMAT_NOT_SUPPORTED",
        "BINARY_EVIDENCE_REQUIRES_SIFT_ORCHESTRATOR",
        "SYMLINK_REJECTED",
        "UNANALYZED_ARTIFACT",
        "UNDETERMINED",
        "UNKNOWN",
        "",
    ])
    def test_error_and_unanalyzed_map_to_abstain_not_benign(self, hyp):
        verdict = classify_agent_verdict({"best_hypothesis": hyp}, n_signals=0)
        assert verdict == "ABSTAIN", f"{hyp!r} debería abstener, no ser benigno"
        assert _VERDICT_EXIT[verdict] == EXIT_ABSTAIN

    def test_malice_is_exit_1(self):
        v = classify_agent_verdict(
            {"best_hypothesis": "MALICIOUS_INTENT_DETECTED", "is_conclusive": True}, 5
        )
        assert v == "MALICE" and _VERDICT_EXIT[v] == EXIT_MALICE

    @pytest.mark.parametrize("hyp", ["INTENT_DETECTED", "SUSPICION_DETECTED"])
    def test_intent_is_exit_3(self, hyp):
        v = classify_agent_verdict({"best_hypothesis": hyp}, 4)
        assert v == "INTENT" and _VERDICT_EXIT[v] == EXIT_INTENT

    def test_clean_with_enough_signals_is_noise(self):
        v = classify_agent_verdict(
            {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED", "is_conclusive": True}, 5
        )
        assert v == "NOISE" and _VERDICT_EXIT[v] == EXIT_NOISE

    def test_clean_but_too_few_signals_abstains(self):
        # <3 señales sin conclusión firme: el reasoner no tuvo base para
        # afirmar benignidad → abstener, no NOISE.
        v = classify_agent_verdict(
            {"best_hypothesis": "NO_ANOMALY_DETECTED", "is_conclusive": False}, 1
        )
        assert v == "ABSTAIN"

    def test_malice_precedence_over_intent_substring(self):
        # "MALICIOUS_INTENT_DETECTED" contiene "INTENT" — malicia debe ganar.
        v = classify_agent_verdict({"best_hypothesis": "MALICIOUS_INTENT_DETECTED"}, 5)
        assert v == "MALICE"

    def test_exit_codes_are_distinct(self):
        assert len({EXIT_NOISE, EXIT_MALICE, EXIT_INTENT, EXIT_ABSTAIN}) == 4
        assert EXIT_ABSTAIN == 4


# ──────────────────────────────────────────────────────────────────────────
# P0-B — PathGuard conectado a VIGIA_EVIDENCE_DIR
# ──────────────────────────────────────────────────────────────────────────

class TestPathGuardEvidenceDir:
    def _guard(self, evidence_dir=None):
        from vigia.sift.sift_orchestrator import _evidence_allowlist
        from vigia.core.path_guard import PathGuard
        return PathGuard(allowed_base_paths=_evidence_allowlist())

    def test_configured_evidence_dir_is_allowed(self, tmp_path, monkeypatch):
        artifact = tmp_path / "Security.log"
        artifact.write_text("event log content")
        monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path))
        result = self._guard().validate(str(artifact), for_read=True)
        assert result.valid, f"evidencia configurada rechazada: {result.reason}"

    def test_unconfigured_path_is_rejected(self, tmp_path, monkeypatch):
        # Control: sin VIGIA_EVIDENCE_DIR, la misma ruta cae fuera de la allowlist.
        artifact = tmp_path / "Security.log"
        artifact.write_text("event log content")
        monkeypatch.delenv("VIGIA_EVIDENCE_DIR", raising=False)
        result = self._guard().validate(str(artifact), for_read=True)
        assert not result.valid
        assert result.reason == "OUTSIDE_ALLOWLIST"

    def test_static_deployment_paths_still_allowed(self):
        from vigia.sift.sift_orchestrator import _evidence_allowlist
        from pathlib import Path
        allow = _evidence_allowlist()
        assert Path("/tmp/vigia") in allow
        assert Path("/mnt") in allow


# ──────────────────────────────────────────────────────────────────────────
# P1-C — filtro de IP externa por red real
# ──────────────────────────────────────────────────────────────────────────

class TestExternalIPFilter:
    def _line(self, foreign_ip):
        return (f"0x9a1b TCPv4 172.16.99.5 49233 {foreign_ip} 443 "
                f"ESTABLISHED 4211 evil.exe")

    @pytest.mark.parametrize("ip", [
        "85.10.20.30",       # contiene "10." — antes filtrado como interno
        "45.155.10.99",      # contiene "10." — antes filtrado
        "185.220.101.5",     # nodo Tor real, enrutable
        "8.8.8.8",
        "2606:4700::1111",   # IPv6 externo — antes SIEMPRE filtrado por "::"
    ])
    def test_external_c2_is_kept(self, ip):
        from sift_orchestrator import _netscan_has_external_conn
        assert _netscan_has_external_conn(self._line(ip)), \
            f"C2 externo {ip} descartado como interno (falso negativo)"

    @pytest.mark.parametrize("ip", [
        "10.0.0.9", "192.168.1.5", "172.16.4.2", "127.0.0.1", "fe80::2",
        "203.0.113.10",      # RFC 5737 documentación — no enrutable
    ])
    def test_internal_is_filtered(self, ip):
        from sift_orchestrator import _netscan_has_external_conn
        assert not _netscan_has_external_conn(self._line(ip))

    def test_ambiguous_line_kept_conservatively(self):
        # Sin IPs parseables, conservar (posible C2) en vez de descartar.
        from sift_orchestrator import _netscan_has_external_conn
        assert _netscan_has_external_conn("0x9a1b TCPv4 *:* ESTABLISHED 4211")

    def test_is_external_ip_classifies(self):
        from sift_orchestrator import _is_external_ip
        assert _is_external_ip("8.8.8.8")
        assert not _is_external_ip("10.0.0.1")
        assert not _is_external_ip("not-an-ip")


# ──────────────────────────────────────────────────────────────────────────
# P1-D — dependencias ausentes / vol3 no disponible → ABSTAIN
# ──────────────────────────────────────────────────────────────────────────

class TestVol3Unavailable:
    def test_all_plugins_failed_yields_abstain(self, monkeypatch):
        from sift_orchestrator import SIFTOrchestrator
        orch = SIFTOrchestrator("CASE-VOL3")
        # Simular vol3 ausente: todos los plugins fallan (binario no encontrado)
        monkeypatch.setattr(
            orch, "_vol3_run",
            lambda mp, plugin, timeout=300: {
                "ok": False, "stdout": "",
                "stderr": "[Errno 2] No such file or directory: 'vol3'",
            },
        )
        result = orch._analyze_memory_vol3("/tmp/vigia/mem.raw")
        assert result["abduction"]["best_hypothesis"] == "UNANALYZED_ARTIFACT"
        assert result["pipeline_meta"]["error"] == "VOL3_UNAVAILABLE"
        # Y ese veredicto abstiene, no es benigno:
        v = classify_agent_verdict(result["abduction"], len(result["signals"]))
        assert v == "ABSTAIN"

    def test_clean_analysis_stays_benign(self, monkeypatch):
        # Contraste: si vol3 corre bien y no halla nada, sí es benigno.
        from sift_orchestrator import SIFTOrchestrator
        orch = SIFTOrchestrator("CASE-CLEAN")

        def fake_run(mp, plugin, timeout=300):
            if "info" in plugin:
                return {"ok": True, "stdout": "Windows 10 x64\n" + "x" * 60, "stderr": ""}
            if "pslist" in plugin:
                return {"ok": True, "stdout": "PID PPID Name\n" + "\n".join(
                    f"{i} 4 svchost.exe" for i in range(60)), "stderr": ""}
            return {"ok": True, "stdout": "no anomalies\n" + "y" * 60, "stderr": ""}

        monkeypatch.setattr(orch, "_vol3_run", fake_run)
        result = orch._analyze_memory_vol3("/tmp/vigia/mem.raw")
        assert result["abduction"]["best_hypothesis"] != "UNANALYZED_ARTIFACT"


# ──────────────────────────────────────────────────────────────────────────
# P1-E — event log de formato no soportado → UNANALYZED note
# ──────────────────────────────────────────────────────────────────────────

class TestEventLogUnanalyzed:
    def test_plaintext_log_surfaces_unanalyzed(self, tmp_path):
        from vigia.sift.event_log_correlator import EventLogCorrelator
        log = tmp_path / "app.log"
        log.write_text("2026-07-02 ERROR something happened\nnot xml at all\n")
        result = EventLogCorrelator().analyze([str(log)])
        assert result.total_events == 0
        joined = " ".join(result.analysis_notes)
        assert "UNANALYZED_ARTIFACT" in joined

    def test_unsupported_suffix_surfaces_unanalyzed(self, tmp_path):
        from vigia.sift.event_log_correlator import EventLogCorrelator
        f = tmp_path / "evidence.bin"
        f.write_bytes(b"\x00\x01\x02binary garbage")
        result = EventLogCorrelator().analyze([str(f)])
        assert result.total_events == 0
        assert any("UNANALYZED_ARTIFACT" in n for n in result.analysis_notes)

    def test_absent_file_is_not_flagged_unanalyzed(self, tmp_path):
        # Un archivo que no existe no es "no analizado" — simplemente no está.
        from vigia.sift.event_log_correlator import EventLogCorrelator
        result = EventLogCorrelator().analyze([str(tmp_path / "missing.evtx")])
        assert result.total_events == 0
        assert not any("UNANALYZED_ARTIFACT" in n for n in result.analysis_notes)
