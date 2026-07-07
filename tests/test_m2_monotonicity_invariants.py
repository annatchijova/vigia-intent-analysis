"""
Tests M2-1 / M2-2 — invariantes de monotonicidad (Red-Team Round 2).

Origen: docs/REDTEAM_ROUND2_MONOTONICITY.md (auditoría 2026-07-07, ambos
CONFIRMADOS POR INDUCCIÓN sobre e78d94b). Script reproducible:
scripts/redteam_round2_monotonicity.py.

M2-1 — Monotonicidad positiva: agregar un artefacto INCRIMINATORIO nunca
       puede bajar final_score. El esquema legacy de correlation decay
       (source_penalty = (count-1)*0.15 aplicado a TODOS los artefactos del
       tipo) violaba esto en 29/30 celdas de la matriz z_score × prior_trust.

M2-2 — No Dilution: evidencia sin señal (raw_score=0 — README.txt, foto,
       manual.pdf) es INERTE: no corrobora el gate B-068 (n_arts/n_types),
       no suma diversity_bonus ni support_score, no cambia el veredicto.
       El gate legacy contaba cardinalidad sin consultar raw_score: un
       documento vacío de tipo nuevo volteaba SUSPICION → MALICE.
"""

import itertools

from vigia_scorer import _vigia_score


def _art(i, etype, raw=0.85, prior=0.85):
    return {
        "artifact_id": f"M2-A{i}",
        "evidence_type": etype,
        "raw_score": raw,
        "prior_trust": prior,
        "source_tool": f"tool_{i}",
        "description": f"artifact {i} ({etype})",
        "timestamp": f"2026-01-{(i % 27) + 1:02d}T10:00:00Z",
        "provenance_chain": ["acquire"],
        "metadata": {},
    }


def _score(arts):
    return _vigia_score({"case_id": "M2-CASE", "artifacts": arts})


_Z_GRID = (0, 1, 2, 3, 4, 5)                # raw = z/5
_TRUST_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)


class TestM21PositiveMonotonicity:
    """Agregar evidencia incriminatoria nunca baja el score."""

    def test_same_type_incriminating_addition_never_lowers_score(self):
        """Matriz z×trust completa: la celda peor del hallazgo M2-1 era
        Δ=-0.093 (z=0, prior=0.0) sobre 3× cryptographic_hash raw=1.0."""
        base = [_art(i, "cryptographic_hash", raw=1.0, prior=1.0) for i in range(3)]
        s0 = _score(base)["score"]
        for z, pt in itertools.product(_Z_GRID, _TRUST_GRID):
            arts = base + [_art(99, "cryptographic_hash", raw=z / 5.0, prior=pt)]
            s1 = _score(arts)["score"]
            assert s1 >= s0 - 1e-9, (
                f"monotonicidad violada: z={z} prior={pt} — {s0} -> {s1}"
            )

    def test_crisp_counterexample_from_audit_is_fixed(self):
        """El contraejemplo nítido del informe: +1 cryptographic_hash débil
        (raw=0.05) bajaba 0.6234 → 0.5350."""
        base = [_art(i, "cryptographic_hash", raw=1.0, prior=1.0) for i in range(3)]
        s0 = _score(base)["score"]
        s1 = _score(base + [_art(3, "cryptographic_hash", raw=0.05)])["score"]
        assert s1 >= s0 - 1e-9, f"{s0} -> {s1}"

    def test_new_type_incriminating_addition_never_lowers_score(self):
        """Control (verde pre-fix — guard de regresión): tipo NUEVO."""
        base = [_art(0, "file_hash", raw=0.6)]
        s0 = _score(base)["score"]
        for z, pt in itertools.product(_Z_GRID, _TRUST_GRID):
            arts = base + [_art(1, "memory_process", raw=z / 5.0, prior=pt)]
            s1 = _score(arts)["score"]
            assert s1 >= s0 - 1e-9, f"z={z} prior={pt}: {s0} -> {s1}"


class TestM22NoDilution:
    """Evidencia sin señal (raw_score=0) es inerte."""

    def test_zero_raw_document_cannot_open_b068_gate(self):
        """Exp 2A del informe: 3 device / 2 tipos, score>0.33, gateado a
        SUSPICION. manual.pdf (document, raw=0) NO debe abrir el gate."""
        before = [
            _art(0, "malware_infrastructure", raw=0.95),
            _art(1, "keylogger_capture", raw=0.95),
            _art(2, "keylogger_capture", raw=0.95),
        ]
        rb = _score(before)
        assert rb["verdict"] == "SUSPICION", f"baseline movida: {rb['verdict']}"
        ra = _score(before + [_art(3, "document", raw=0.0)])
        assert ra["verdict"] == "SUSPICION", (
            f"un documento con raw_score=0 abrió el gate B-068: "
            f"{rb['verdict']} -> {ra['verdict']}"
        )

    def test_zero_raw_document_cannot_cross_band_edge(self):
        """Sonda de borde de banda del informe (H3): 2× log_entry raw=0.49 en
        NOISE; +document raw=0 volteaba a UNKNOWN vía diversity_bonus."""
        before = [_art(0, "log_entry", raw=0.49), _art(1, "log_entry", raw=0.49)]
        rb = _score(before)
        ra = _score(before + [_art(2, "document", raw=0.0)])
        assert ra["verdict"] == rb["verdict"], (
            f"dilución volteó el veredicto: {rb['verdict']} -> {ra['verdict']}"
        )
        assert ra["score"] == rb["score"], (
            f"un artefacto sin señal movió el score: {rb['score']} -> {ra['score']}"
        )

    def test_zero_raw_same_type_artifact_is_fully_inert(self):
        """Exp 2B del informe: mismo tipo, raw=0 — ni score ni veredicto."""
        before = [_art(i, "malware_infrastructure", raw=0.97) for i in range(3)]
        rb = _score(before)
        ra = _score(before + [_art(3, "malware_infrastructure", raw=0.0)])
        assert ra["verdict"] == rb["verdict"]
        assert ra["score"] == rb["score"], (
            f"raw=0 del mismo tipo diluyó el score: {rb['score']} -> {ra['score']}"
        )

    def test_zero_raw_artifact_does_not_lift_single_artifact_cap(self):
        """El cap n<2 → 0.65 cuenta señal, no cardinalidad: un README vacío
        no convierte un caso mono-artefacto en 'corroborado'."""
        one = [_art(0, "cryptographic_hash", raw=1.0, prior=1.0)]
        padded = one + [_art(1, "document", raw=0.0)]
        r_one, r_pad = _score(one), _score(padded)
        assert r_pad["score"] == r_one["score"]
        assert r_pad["verdict"] == r_one["verdict"]
