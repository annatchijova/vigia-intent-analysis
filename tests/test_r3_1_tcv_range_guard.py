"""
Test R3-1 — guard de rango absoluto en la regla TCV del CAIE.

Origen: docs/REDTEAM_ROUND3_EMERGENT.md (R3-1, CONFIRMADO POR INDUCCION sobre
1d84c84). Script: scripts/redteam_round3_emergent.py R3-1.

Defecto: _parse_ts_tcv parseaba cualquier fecha ISO valida sin validar rango
absoluto. Un artefacto con network_log_time=1970-01-01 (el sentinela clasico
de "fecha no parseada") fabricaba un TEMPORAL_CAUSALITY_VIOLATION severity=1.0
en vivo -> boost 0.45 -> volteaba NOISE->SUSPICION. Idem 2099 sobre el evento
posterior.

Fix: fechas fuera de la ventana forense plausible [2000, 2038) se leen como
DATO AUSENTE (return None), no como evidencia temporal. Una violacion real
DENTRO de rango sigue detectandose.
"""

from vigia_scorer import _vigia_score


def _art(i, etype, raw, ts, meta):
    return {
        "artifact_id": f"R31-A{i}", "evidence_type": etype, "raw_score": raw,
        "prior_trust": 0.85, "source_tool": f"t{i}",
        "description": f"{etype} artifact {i}", "timestamp": ts,
        "provenance_chain": ["acq"], "metadata": meta,
    }


def _net(ts):
    return _art(0, "network_flow", 0.2, ts, {"network_log_time": ts})


def _proc(ts):
    return _art(1, "memory_process", 0.2, ts, {"process_creation_time": ts})


def _score(arts):
    return _vigia_score({"case_id": "R31", "artifacts": arts})


class TestR31OutOfRangeIsInert:
    def test_1970_epoch_sentinel_does_not_fabricate_tcv(self):
        r = _score([_net("1970-01-01T00:00:00Z"), _proc("2026-03-01T09:00:00Z")])
        assert r["caie_fractures"] == 0, "1970 sentinel fabrico una fractura TCV"
        assert r["fracture_malice_boost"] == 0.0
        assert r["verdict"] == "NOISE", f"1970 movio el veredicto: {r['verdict']}"

    def test_2099_future_on_later_event_does_not_fabricate_tcv(self):
        r = _score([_net("2026-03-01T10:00:00Z"), _proc("2099-01-01T00:00:00Z")])
        assert r["caie_fractures"] == 0
        assert r["verdict"] == "NOISE", f"2099 movio el veredicto: {r['verdict']}"

    def test_windows_filetime_1601_epoch_is_inert(self):
        r = _score([_net("1601-01-01T00:00:00Z"), _proc("2026-03-01T09:00:00Z")])
        assert r["caie_fractures"] == 0
        assert r["verdict"] == "NOISE"


class TestR31InRangeStillDetects:
    def test_real_in_range_causality_violation_still_fires(self):
        # network activity (08h) BEFORE the process that caused it (10h),
        # both plausible 2026 timestamps -> genuine TCV, must still fire.
        r = _score([_net("2026-03-01T08:00:00Z"), _proc("2026-03-01T10:00:00Z")])
        assert r["caie_fractures"] >= 1, "el guard mato una violacion TCV legitima"
        assert r["fracture_malice_boost"] > 0.0

    def test_lower_boundary_2000_is_in_range(self):
        # 2000 (in range) before a 2026 process -> real violation fires.
        r = _score([_net("2000-06-01T00:00:00Z"), _proc("2026-03-01T09:00:00Z")])
        assert r["caie_fractures"] >= 1

    def test_just_below_2000_is_out_of_range(self):
        r = _score([_net("1999-12-31T23:59:59Z"), _proc("2026-03-01T09:00:00Z")])
        assert r["caie_fractures"] == 0
