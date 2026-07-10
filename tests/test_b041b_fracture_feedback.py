"""
Test B-041b — cierre por SUPERACIÓN: las fracturas CAIE retroalimentan el
veredicto en el scorer autoritativo.

Contexto (daubert-defensible, separando capas):

  OBSERVACIÓN (reproducible por inducción, ver abajo): en el path autoritativo
  `vigia_scorer._vigia_score` (el scorer label-blind de B-075/B-076, fuente
  del veredicto desde entonces), una fractura CAIE viva aplica
  `fracture_malice_boost` (hasta +0.5) al composite ANTES de emitir el
  veredicto (`vigia_scorer.py:1053`). Un caso idéntico salvo por la presencia
  de la fractura cambia de clase de veredicto.

  INFERENCIA: el mecanismo que B-041b pedía — "upgrade automático hacia MALICE
  cuando CAIE detecta fracturas" — ya existe, en forma mejor (continua,
  determinista, pre-emisión) que el upgrade discreto INTENT→MALICE original.

  CONCLUSIÓN: B-041b (diagnosticado 2026-06-30 contra el path viejo donde CAIE
  corría DESPUÉS de la abducción) quedó SUPERADO por B-075/B-076, no pendiente.
  Su preocupación de "sería dead code con la metadata actual" queda REFUTADA:
  el mecanismo dispara sobre fracturas genuinas (este test) y permanece
  correctamente inerte sobre el corpus (0 fracturas — no hay artefactos de
  fabricación), que es el comportamiento conservador deseado, no código muerto.

Este archivo PINEA esa clausura: si el feedback fractura→veredicto se
rompiera, B-041b se reabriría y estos tests fallarían.
"""

import contextlib
import io

from vigia_scorer import _vigia_score


def _art(i, etype, raw, ts, meta=None):
    return {
        "artifact_id": f"B041B-A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": 0.85, "source_tool": f"t{i}",
        "description": f"{etype} artifact {i}", "timestamp": ts,
        "provenance_chain": ["acq"], "metadata": meta or {},
    }


def _score(arts):
    with contextlib.redirect_stdout(io.StringIO()), \
         contextlib.redirect_stderr(io.StringIO()):
        return _vigia_score({"case_id": "B041B", "artifacts": arts})


# Par mínimo que produce una TEMPORAL_CAUSALITY_VIOLATION viva: tráfico de red
# (08h) ANTES del proceso que lo habría causado (10h), con la metadata de
# enlace que la regla TCV consume. El control invierte el orden temporal.
def _net(ts):
    return _art(0, "network_flow", 0.2, ts, {"network_log_time": ts})


def _proc(ts):
    return _art(1, "memory_process", 0.2, ts, {"process_creation_time": ts})


class TestFractureFeedsVerdict:
    def test_tcv_fracture_boosts_score_and_flips_verdict(self):
        control = _score([_net("2026-03-01T11:00:00Z"),
                          _proc("2026-03-01T10:00:00Z")])
        violated = _score([_net("2026-03-01T08:00:00Z"),
                           _proc("2026-03-01T10:00:00Z")])
        # Observación: sin fractura → NOISE; con fractura → boost y salto de clase.
        assert control["caie_fractures"] == 0
        assert control["fracture_malice_boost"] == 0.0
        assert control["verdict"] == "NOISE"
        assert violated["caie_fractures"] >= 1
        assert violated["fracture_malice_boost"] > 0.0
        assert float(violated["score"]) > float(control["score"]) + 0.3
        assert violated["verdict"] != "NOISE"

    def test_boost_is_bounded(self):
        # El boost está acotado (vigia_scorer.py:1005/1013: min(0.5, ...)) —
        # una fractura no puede saturar el veredicto por sí sola sin base.
        violated = _score([_net("2026-03-01T08:00:00Z"),
                           _proc("2026-03-01T10:00:00Z")])
        assert 0.0 < violated["fracture_malice_boost"] <= 0.5

    def test_fracture_contributes_to_malice_magnitude(self):
        # Con una base ya corroborada (≥4 artefactos duros → gate MALICE),
        # la fractura eleva la MAGNITUD del score (aporta al veredicto, no es
        # dead code): B-041b pedía exactamente este acoplamiento.
        base = [
            _proc_hard(1), _proc_hard(2, "mft_entry"),
            _proc_hard(3, "lsass_session"), _proc_hard(4, "kernel_structure"),
        ]
        net_ok = _net("2026-03-01T11:00:00Z")
        net_bad = _net("2026-03-01T08:00:00Z")
        clean = _score(base + [net_ok])
        fractured = _score(base + [net_bad])
        assert fractured["fracture_malice_boost"] > 0.0
        assert float(fractured["score"]) > float(clean["score"])


def _proc_hard(i, etype="memory_process"):
    return _art(i, etype, 0.85, "2026-03-01T10:00:00Z",
                {"process_creation_time": "2026-03-01T10:00:00Z"})


# ─────────────────────────────────────────────────────────────────────────────
# B-094 — las fracturas del scorer que MUEVEN el veredicto deben ser visibles
# en el bundle/narrativa del path motor (JSON/EBS, default post-B-075).
#
# B-041a expuso la CAIE del ORQUESTADOR (results["caie"], path disk/mixed). El
# path motor — que es el default de Mode 1 desde B-075 — corre su propia CAIE
# viva en _vigia_score y aplica fracture_malice_boost, pero descartaba TODA la
# info de fracturas: caie_fractures/boost ausentes del bundle, y la SECONDNESS
# de la narrativa afirmaba "sin desviación estructural" aun cuando una fractura
# volteó NOISE→INTENT. Anti-patrón Daubert explícito (CLAUDE.md): "MALICE sin
# explicarlo con matemática exacta es adivinación". Tests ROJOS contra ese path.
# ─────────────────────────────────────────────────────────────────────────────

import json as _json
import os as _os
from pathlib import Path as _Path


class TestB094MotorPathSurfacesFractures:
    def _run_motor(self, tmp_path, artifacts, case_id="B094"):
        import sift_orchestrator as shim
        case = {"case_id": case_id, "case_name": case_id, "schema_version": 1,
                "description": "B-094 motor CAIE visibility",
                "expected_verdict": "UNKNOWN", "artifacts": artifacts}
        p = tmp_path / f"{case_id}.json"
        p.write_text(_json.dumps(case))
        orch = shim.SIFTOrchestrator(case_id=case_id)
        return orch.analyze(log_path=str(p))

    @staticmethod
    def _net(ts):
        return {"artifact_id": "N", "evidence_type": "network_flow",
                "source_tool": "t", "description": "net", "raw_score": 0.2,
                "prior_trust": 0.85, "timestamp": ts,
                "provenance_chain": ["acq"], "metadata": {"network_log_time": ts}}

    @staticmethod
    def _proc(ts):
        return {"artifact_id": "P", "evidence_type": "memory_process",
                "source_tool": "t", "description": "proc", "raw_score": 0.2,
                "prior_trust": 0.85, "timestamp": ts,
                "provenance_chain": ["acq"],
                "metadata": {"process_creation_time": ts}}

    def test_fracture_present_in_result_caie(self, tmp_path):
        r = self._run_motor(tmp_path, [self._net("2026-03-01T08:00:00Z"),
                                       self._proc("2026-03-01T10:00:00Z")])
        inner = r.get("results") or {}
        caie = inner.get("caie") or {}
        assert caie.get("status") == "OK", f"CAIE ausente del path motor: {caie}"
        assert caie.get("fractures_detected", 0) >= 1
        types = [f.get("type") for f in caie.get("fractures", [])]
        assert any("TEMPORAL" in str(t) for t in types), types
        assert float(caie.get("fracture_malice_boost", 0)) > 0.0

    def test_control_no_fracture_no_caie_noise(self, tmp_path):
        r = self._run_motor(tmp_path, [self._net("2026-03-01T11:00:00Z"),
                                       self._proc("2026-03-01T10:00:00Z")])
        inner = r.get("results") or {}
        caie = inner.get("caie") or {}
        # Sin fractura: o no hay bloque CAIE, o reporta 0 fracturas — nunca
        # inventa una.
        assert caie.get("fractures_detected", 0) == 0

    def test_verdict_unchanged_by_visibility(self, tmp_path):
        # El fix es SOLO visibilidad: el veredicto ya usaba la fractura.
        from vigia_agent import classify_agent_verdict, _signal_stats
        r = self._run_motor(tmp_path, [self._net("2026-03-01T08:00:00Z"),
                                       self._proc("2026-03-01T10:00:00Z")])
        n_primary, n_unanalyzed = _signal_stats(r)
        v = classify_agent_verdict(r.get("abduction", {}), n_primary, n_unanalyzed)
        assert v in ("INTENT", "MALICE", "SUSPICION")  # fractura → no-NOISE
        # el marcador de visibilidad no fabrica artefactos no analizados
        assert n_unanalyzed == 0

    def test_narrative_end_to_end_explains_verdict(self, tmp_path):
        # Daubert: el bundle no puede sellar un veredicto no-NOISE por fractura
        # y presentar una narrativa que diga "sin desviación estructural" sin
        # mención de la fractura. Verifica el path COMPLETO shim→narrativa.
        from vigia_agent import VIGIAAgent
        r = self._run_motor(tmp_path, [self._net("2026-03-01T08:00:00Z"),
                                       self._proc("2026-03-01T10:00:00Z")],
                            case_id="B094-NARR")
        agent = VIGIAAgent("B094-NARR", ".")
        narrative = agent._generate_narrative(r, "a" * 64)
        assert "TEMPORAL_CAUSALITY_VIOLATION" in narrative, (
            "la fractura que movió el veredicto no aparece en la narrativa "
            "sellada (anti-patrón Daubert 'divination')"
        )
        assert "boost" in narrative.lower()
        # SECONDNESS ya no puede afirmar SOLO 'sin desviación' sin la CAIE.
        sec = [l for l in narrative.split("\n") if "SECONDNESS" in l][0]
        assert "CAIE" in sec

    def test_narrative_control_no_fracture_line(self, tmp_path):
        from vigia_agent import VIGIAAgent
        r = self._run_motor(tmp_path, [self._net("2026-03-01T11:00:00Z"),
                                       self._proc("2026-03-01T10:00:00Z")],
                            case_id="B094-CTRL")
        agent = VIGIAAgent("B094-CTRL", ".")
        narrative = agent._generate_narrative(r, "a" * 64)
        assert "TEMPORAL_CAUSALITY_VIOLATION" not in narrative
        assert "CAIE (viva)" not in narrative
