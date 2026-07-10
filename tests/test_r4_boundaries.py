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

    @staticmethod
    def _art_isolated(i, etype="log_entry", raw=0.85, prior=0.85):
        """Variante de _art() SOLO para el guard de timing de abajo — NO usar
        en tests de score (rompe los snapshots bit-identical de arriba, que
        dependen de la degradacion de base_trust por metadata de adquisicion
        ausente via el _art() de modulo).

        CI investigation (2026-07-10): perfilado con cProfile mostro que
        _art() (metadata={}) hace que CADA Artifact dispare 2 escrituras de
        auditoria NIST SP 800-86 (ACQUISITION_METADATA_MISSING_CRITICAL +
        _WARNING, caie.py:733-828) via audit_logger.log_block ->
        security.py:_write_entry -> posix.fsync(). Ese fsync() dominaba
        70-95% del wall-clock medido (1.44s de 2.00s a n=700; 3.35s de
        4.58s a n=1400) — el test media latencia de syscall de disco, NO
        la complejidad del best-prefix decay que dice guardar. fsync() en
        storage efimero de CI (ubuntu-latest, GH-hosted) tiene latencia de
        cola variable e impredecible por causas ajenas a carga de CPU —
        reproducido: 10x aislado + 10x bajo estres de CPU (oversubscripcion
        8x en 2 CPUs via taskset) NUNCA superaron ratio 2.5; la falla de CI
        fue ratio 4.62 (t1=0.86 t2=3.98) — inexplicable por contencion de
        CPU (que escala t1 y t2 proporcionalmente), consistente con
        variacion de latencia de fsync no relacionada a CPU.

        Fix (test-only, scorer intacto): metadata de adquisicion completa
        evita el path de auditoria; ver tambien el cambio de n abajo."""
        return {
            "artifact_id": f"A{i}", "evidence_type": etype, "raw_score": raw,
            "prior_trust": prior, "source_tool": f"t{i}", "description": f"a{i}",
            "timestamp": f"2026-01-01T10:00:{i % 60:02d}Z",
            "provenance_chain": ["acq"],
            "metadata": {
                "acquisition_tool": "dd", "acquisition_hash": f"sha256:{i:064x}",
                "acquisition_timestamp": "2026-01-01T09:00:00Z",
                "examiner_id": "test", "write_blocker_used": True,
            },
        }

    def test_best_prefix_component_is_subquadratic(self):
        """Guarda de regresion del O(n^2): el TIEMPO del scoring de un flood de
        un solo tipo debe crecer de forma ~lineal, no cuadratica. Se compara el
        costo incremental n vs 2n.

        n1/n2 elegidos por debajo de _MAX_ARTIFACTS (caie.py:502, =1000): el
        test original (700/1400) cruzaba ese umbral DoS entre las dos
        mediciones, asi que a n=1400 ademas se rechazaban 400 artefactos con
        SU PROPIA escritura de auditoria (CAIE_ARTIFACT_LIMIT,
        caie.py:1099-1108) — codigo CUALITATIVAMENTE distinto ejecutado solo
        en t2, no comparable con t1. Con ambos n del mismo lado del umbral,
        las dos mediciones ejercitan el mismo camino de codigo (ver
        docstring de _art_isolated arriba para el detalle completo)."""
        def t(n):
            arts = [self._art_isolated(i) for i in range(n)]
            t0 = time.perf_counter()
            _vigia_score({"artifacts": arts})
            return time.perf_counter() - t0
        t(200)  # warmup (CAIE import / caches)
        t1 = t(400)
        t2 = t(800)
        # x4 seria cuadratico puro; exigimos < x3 (holgado por el costo lineal
        # de CAIE que domina y no crece cuadraticamente).
        assert t2 < t1 * 3.0, f"crecimiento super-lineal sospechoso: {t1:.2f}s -> {t2:.2f}s"
