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
