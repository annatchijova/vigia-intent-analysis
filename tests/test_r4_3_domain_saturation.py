"""
R4-3 — saturación por dominio de recolección en el scorer EBS.

Diseño aprobado (colectivo, 6 modelos) sobre dos investigaciones previas:
- docs/TAXA_DOMINIOS_RECOLECCION.md (taxonomía v2, CR-001..004 de Kimi):
  5 dominios por MODO DE FABRICACIÓN compartido + sub-bandas D1/D5 + D0.
- docs/BASELINE_TRIPLE_CASTIGO.md: el path EBS tenía CERO atenuación de
  redundancia — 95 logs irrelevantes (raw 0.05) movían BREAK-014 de
  SUSPICION 0.2324 a MALICE 0.3867 (dos bandas), y 50 logs de nada
  fabricaban SUSPICION. FRS (path V4) satura perfecto pero el motor no lo
  usaba.

Implementación fijada acá:
1. classify_domain() revivido en caie.py con la taxonomía v2 (era código
   muerto con log_entry→"network").
2. Decaimiento geométrico posicional r=1/2 por grupo de dominio, aplicado
   DESPUÉS del decay por tipo (M2-1): misma asíntota que FRS medido
   (≈2× dominante), pero MONÓTONO por inserción — la fórmula FRS cruda
   (redundantes × 1/N) viola M2-1 al agregar un duplicado débil.
   Cross-domain con 1 artefacto por dominio = no-op bit a bit.
3. Gate B-068 cuenta DOMINIOS activos (≥2), no tipos/artefactos.

Tests escritos ROJOS contra el scorer previo.
"""

import contextlib
import copy
import io
import json

import pytest

from vigia.tools.caie import classify_domain
from vigia_scorer import _vigia_score


def _score(case):
    with contextlib.redirect_stdout(io.StringIO()), \
         contextlib.redirect_stderr(io.StringIO()):
        return _vigia_score(copy.deepcopy(case))


def _case(artifacts, **root):
    base = {
        "case_id": "R43-TEST",
        "case_name": "r43",
        "description": "synthetic",
        "expected_verdict": "UNKNOWN",
        "schema_version": 1,
        "artifacts": artifacts,
    }
    base.update(root)
    return base


def _art(evidence_type="log_entry", raw=0.5, trust=0.8, aid="A"):
    return {
        "artifact_id": aid,
        "evidence_type": evidence_type,
        "source_tool": "t",
        "description": "d",
        "raw_score": raw,
        "prior_trust": trust,
        "timestamp": "2026-07-07T00:00:00Z",
        "provenance_chain": ["gen"],
        "metadata": {
            "acquisition_tool": "test",
            "acquisition_hash": "sha256:" + "0" * 64,
            "acquisition_timestamp": "2026-07-07T00:00:00Z",
            "write_blocker_used": False,
            "examiner_id": "EX-1",
        },
    }


# ── 1. Taxonomía v2 en classify_domain ─────────────────────────────────────

class TestClassifyDomainV2:
    def test_log_entry_is_log_symbolic_not_network(self):
        # El _DOMAIN_MAP muerto decía "network" — el eje correcto es el modo
        # de fabricación (TAXA §resumen): un syslog no es telemetría de red.
        assert classify_domain("log_entry") == "log_symbolic"

    def test_core_mappings(self):
        assert classify_domain("memory_process") == "memory_kernel"
        assert classify_domain("kernel_structure") == "memory_kernel"
        assert classify_domain("file_timestamp") == "filesystem_metadata"
        assert classify_domain("registry_key") == "filesystem_metadata"
        assert classify_domain("network_flow") == "network_telemetry"
        assert classify_domain("ip_geolocation") == "network_telemetry"
        assert classify_domain("binary") == "content_artifact"
        assert classify_domain("cultural_marker") == "content_artifact"

    def test_kimi_cr_resolutions(self):
        # CR-001: el buffer lo produce un implante VIVO.
        assert classify_domain("keylogger_capture") == "memory_kernel"
        # CR-003: contenido probatorio criptográfico, no metadata.
        assert classify_domain("TPM_attestation") == "content_artifact"
        # CR-002: sigue en D1 (la sub-banda es intra-dominio).
        assert classify_domain("windows_event_log") == "log_symbolic"

    def test_assurance_context_domain(self):
        assert classify_domain("acquisition_context") == "assurance_context"
        assert classify_domain("behavioral_context") == "assurance_context"

    def test_unknown_type_gets_own_domain(self):
        # Conservador: un tipo desconocido no satura contra otros desconocidos
        # distintos, pero N copias del MISMO tipo desconocido sí comparten grupo.
        d = classify_domain("tipo_inventado_2027")
        assert d.startswith("UNKNOWN:"), d
        assert classify_domain("tipo_inventado_2027") == d
        assert classify_domain("otro_tipo_raro") != d

    def test_full_corpus_coverage(self):
        # Los 53 tipos del censo (TAXA §2) clasifican a un dominio real.
        census = [
            "log_entry", "memory_process", "binary", "file_timestamp",
            "cultural_marker", "file_hash", "file_metadata", "registry_key",
            "ip_geolocation", "binary_executable", "document", "container_zip",
            "network_flow", "lsass_session", "cryptographic_hash",
            "document_geometry", "malware_static_analysis", "dns_record",
            "email_content", "document_visual", "kernel_structure", "archive",
            "network_traffic", "network_capture", "keylogger_capture",
            "filesystem_artifact", "disk_image", "osint", "mft_entry",
            "windows_event_log", "shimcache", "pe_executable", "git_forensics",
            "spreadsheet", "event_log", "web_artifact", "file_text",
            "acquisition_context", "memory_os_profile", "registry_hive",
            "email_account_creation", "network_communication_pattern",
            "deleted_file_recovery", "device_acquisition_timeline",
            "binary_diff", "TPM_attestation", "malware_infrastructure",
            "behavioral_context", "outcome_signal", "behavioral_profile",
            "plaintext_credential", "elf_executable", "user_agent",
        ]
        for et in census:
            assert not classify_domain(et).startswith("UNKNOWN:"), (
                f"{et} sin dominio en la taxonomía v2"
            )


# ── 2. Criterios de aceptación sobre BREAK-014 ─────────────────────────────

class TestBreak014Acceptance:
    @pytest.fixture(scope="class")
    def case(self):
        return json.load(open("data/cases/VIGIA-BREAK-014.json"))

    def test_verdict_is_suspicion(self, case):
        r = _score(case)
        assert r["verdict"] == "SUSPICION", (
            f"BREAK-014 (100× log_entry) debe ser SUSPICION, dio "
            f"{r['verdict']} score={r['score']} — el drowning por volumen "
            f"del mismo dominio sigue comprando MALICE"
        )

    def test_score_and_confidence_dropped_vs_baseline(self, case):
        # Baseline medido (BASELINE_TRIPLE_CASTIGO §1): MALICE 0.3867 conf 0.77.
        r = _score(case)
        assert float(r["score"]) < 0.3867
        assert float(r["confidence"]) < 0.77

    def test_pure_noise_volume_cannot_buy_suspicion(self, case):
        # Baseline §2: 95 logs de raw 0.05 SOLOS daban SUSPICION 0.1888.
        noise = [a for a in case["artifacts"]
                 if float(a.get("raw_score", 0)) == 0.05]
        r = _score(_case(copy.deepcopy(noise)))
        assert r["verdict"] == "NOISE", (
            f"95 logs de raw 0.05 sin un solo artefacto decisivo: "
            f"{r['verdict']} score={r['score']}"
        )

    def test_saturation_bounded_tail(self, case):
        # La cola de 95 irrelevantes no puede aportar más que ~el doble del
        # mejor log (asíntota geométrica): score(95) - score(0) acotado.
        noise = [a for a in case["artifacts"]
                 if float(a.get("raw_score", 0)) == 0.05]
        decisive = [a for a in case["artifacts"]
                    if float(a.get("raw_score", 0)) != 0.05]
        s0 = float(_score(_case(copy.deepcopy(decisive)))["score"])
        s95 = float(_score(_case(copy.deepcopy(decisive + noise)))["score"])
        assert s95 - s0 < 0.05, (
            f"la cola de 95 logs irrelevantes aporta {s95 - s0:.4f} "
            f"(baseline pre-fix: +0.1543) — no satura"
        )


# ── 3. Gate B-068 por dominios ─────────────────────────────────────────────

class TestDomainGate:
    def _high_score_arts(self, types):
        return [_art(evidence_type=t, raw=0.9, trust=0.9, aid=f"A{i}")
                for i, t in enumerate(types)]

    def test_single_domain_volume_cannot_open_gate(self):
        # 4 artefactos fuertes, TODOS D3 (3 tipos distintos — el gate viejo
        # abría por n_types >= 3): un solo dominio de recolección no puede
        # corroborar MALICE.
        r = _score(_case(self._high_score_arts(
            ["file_timestamp", "registry_key", "mft_entry", "file_hash"])))
        assert float(r["score"]) > 0.33, "el setup debe cruzar el umbral"
        assert r["verdict"] == "SUSPICION", (
            f"4 artefactos de UN dominio (D3) abrieron el gate: {r['verdict']}"
        )

    def test_two_domains_open_gate(self):
        r = _score(_case(self._high_score_arts(
            ["file_timestamp", "memory_process", "registry_key", "mft_entry"])))
        assert float(r["score"]) > 0.33
        assert r["verdict"] == "MALICE", (
            f"2 dominios activos (D3+D2) deben corroborar: {r['verdict']}"
        )

    def test_gate_trace_exposed(self):
        r = _score(_case(self._high_score_arts(
            ["file_timestamp", "memory_process"])))
        assert "r43_active_domains" in r, "trazabilidad Daubert del gate"


# ── 4. Invariantes M2 preservados bajo el decaimiento por dominio ──────────

class TestMonotonicityPreserved:
    def test_same_domain_addition_never_lowers_score(self):
        base = [_art("log_entry", raw=0.6, aid="A0")]
        s_prev = float(_score(_case(copy.deepcopy(base)))["score"])
        for i, raw in enumerate([0.5, 0.3, 0.1, 0.05], start=1):
            base.append(_art("log_entry", raw=raw, aid=f"A{i}"))
            s = float(_score(_case(copy.deepcopy(base)))["score"])
            assert s >= s_prev - 1e-9, (
                f"agregar log #{i} (raw={raw}) bajó el score: {s_prev} → {s}"
            )
            s_prev = s

    def test_cross_domain_single_artifacts_are_noop(self):
        # 1 artefacto por dominio: el decaimiento posicional es peso 1.0 en
        # todos — el composite no puede diferir del esquema por-tipo previo
        # (compatibilidad bit a bit para el caso regular del corpus).
        arts = [_art("log_entry", raw=0.4, aid="A0"),
                _art("memory_process", raw=0.4, aid="A1"),
                _art("network_flow", raw=0.4, aid="A2")]
        r = _score(_case(arts))
        doms = r.get("r43_domain_scores", {})
        assert len([d for d, s in doms.items() if float(s) > 0]) == 3
