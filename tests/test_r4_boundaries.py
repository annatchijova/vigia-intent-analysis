"""
Test Round 4 — boundary conditions del scorer.

Origen: scripts/redteam_round4_boundaries.py + docs/REDTEAM_ROUND4_BOUNDARIES.md.

Cubre los fixes implementados:
  R4-1  best-prefix decay O(n^2) -> O(n) (bit-identico; candidatos {1,2,3,4,n}).
  R4-4  caso None / no-dict -> ERROR limpio, sin crash.
Y guarda de robustez de los boundaries (0 artefactos, artefacto vacio,
malformados) — que ya estaban protegidos y NO deben regresionar.
"""

import time

from vigia_scorer import _vigia_score


def _art(i, etype="log_entry", raw=0.85, prior=0.85):
    return {
        "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": prior, "source_tool": f"t{i}", "description": f"a{i}",
        "timestamp": f"2026-01-01T10:00:{i % 60:02d}Z",
        "provenance_chain": ["acq"], "metadata": {},
    }


class TestR44NonDictCase:
    def test_none_case_returns_error_not_crash(self):
        r = _vigia_score(None)
        assert r["verdict"] == "ERROR", r

    def test_non_dict_case_returns_error(self):
        for bad in ("string", 123, [1, 2, 3], 3.14, True):
            r = _vigia_score(bad)
            assert r["verdict"] == "ERROR", f"{bad!r} -> {r}"


class TestZeroAndEmpty:
    def test_zero_artifacts_is_error(self):
        assert _vigia_score({"case_id": "z", "artifacts": []})["verdict"] == "ERROR"

    def test_empty_dict_case(self):
        assert _vigia_score({})["verdict"] == "ERROR"

    def test_artifacts_none(self):
        assert _vigia_score({"artifacts": None})["verdict"] == "ERROR"

    def test_single_empty_artifact_no_crash(self):
        r = _vigia_score({"artifacts": [{}]})
        assert 0.0 <= r["score"] <= 0.99


class TestMalformedArtifactsShielded:
    def test_finite_math_and_type_shields(self):
        cases = [
            {"evidence_type": "log_entry", "raw_score": None},
            {"evidence_type": "log_entry", "raw_score": "high"},
            {"evidence_type": "log_entry", "raw_score": float("inf")},
            {"evidence_type": "log_entry", "raw_score": float("nan")},
            {"evidence_type": None, "raw_score": 0.9},
            {"evidence_type": 123, "raw_score": 0.9},
            {"evidence_type": "log_entry", "raw_score": 0.9, "provenance_chain": "nope"},
            {"evidence_type": "log_entry", "raw_score": 0.9, "prior_trust": -5},
        ]
        for c in cases:
            r = _vigia_score({"artifacts": [c]})
            assert "verdict" in r and 0.0 <= r.get("score", 0.0) <= 0.99, (c, r)


class TestR41BestPrefixBitIdentical:
    """R4-1: la optimizacion O(n) del best-prefix debe dar los MISMOS scores
    que se snapshotearon con la implementacion O(n^2) verificada."""
    # Snapshots re-capturados 2026-07-09 post-R4-3: el pipeline ahora aplica
    # decay geometrico de cola por sub-banda (log_entry -> D1a, r=0.5) DESPUES
    # de la etapa 1, asi que el output pineado incluye ambas etapas. La
    # bit-identidad de la etapa 1 (R4-1) sigue verificada: neutralizando solo
    # la cola (classify_domain_subband -> banda UNKNOWN) se recuperan exactos
    # los snapshots pre-R4-3 {10: 0.3393, 50: 0.8741, 100: 0.9842}. La
    # convergencia 50 -> 100 (mismo score) es la asintota de la cola
    # geometrica: un flood de un solo tipo ya no crece sin limite
    # (docs/BASELINE_TRIPLE_CASTIGO.md). Si cambian, regresiono la etapa 1
    # (R4-1) o la saturacion (R4-3).
    EXPECTED = {10: 0.1861, 50: 0.1866, 100: 0.1866}

    def test_same_type_flood_scores_match_snapshot(self):
        for n, exp in self.EXPECTED.items():
            r = _vigia_score({"case_id": f"f{n}",
                              "artifacts": [_art(i, "log_entry", 0.85) for i in range(n)]})
            assert r["score"] == exp, f"n={n}: {r['score']} != {exp}"

    def test_score_stays_bounded_and_deterministic(self):
        a = [_art(i, "log_entry", 0.85) for i in range(300)]
        r1 = _vigia_score({"artifacts": a})
        r2 = _vigia_score({"artifacts": [_art(i, "log_entry", 0.85) for i in range(300)]})
        assert r1["score"] == r2["score"]
        assert 0.0 <= r1["score"] <= 0.99

    def test_best_prefix_component_is_subquadratic(self):
        """Guarda de regresion del O(n^2): el TIEMPO del scoring de un flood de
        un solo tipo debe crecer de forma ~lineal, no cuadratica. Se compara el
        costo incremental n vs 2n. Umbral holgado (x3) para no ser flaky pero
        atrapar un retorno a O(n^2) (que daria ~x4)."""
        def t(n):
            arts = [_art(i, "log_entry", 0.85) for i in range(n)]
            t0 = time.perf_counter()
            _vigia_score({"artifacts": arts})
            return time.perf_counter() - t0
        t(200)  # warmup (CAIE import / caches)
        t1 = t(700)
        t2 = t(1400)
        # x4 seria cuadratico puro; exigimos < x3 (holgado por el costo lineal
        # de CAIE que domina y no crece cuadraticamente).
        assert t2 < t1 * 3.0, f"crecimiento super-lineal sospechoso: {t1:.2f}s -> {t2:.2f}s"
