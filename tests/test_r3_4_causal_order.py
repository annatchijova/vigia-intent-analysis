"""
Test R3-4 — validación de orden causal en el verificador de la cadena.

Origen: docs/REDTEAM_ROUND3_EMERGENT.md (R3-4). El verificador v2 validaba seq
monotónico + integridad de contenido + linkage, pero NUNCA el orden/rango de
los timestamps: una cadena con timestamps hacia atrás, en 1970 y con evento
duplicado sellaba y verificaba como CHAIN VERIFIED.

Fix: se agrega un chequeo de PLAUSIBILIDAD TEMPORAL, reportado por SEPARADO del
resultado criptográfico (una historia causalmente imposible no es una ruptura
del sello — el sello funciona; la cadena prueba orden de inserción e
integridad, no causalidad). `valid` sigue siendo integridad criptográfica;
`timeline_plausible` es el eje nuevo, advisory.
"""

from vigia.core.hash_chain import ChainLink, build_link, verify_chain
from vigia.core.tool_log_chain import (
    ToolExecutionLogChain, verify_tool_execution_log,
)


def _chain(timestamps):
    """Construye una cadena v2 criptográficamente válida con los timestamps dados."""
    chain = ToolExecutionLogChain(mode="claude_code", use_env_key=False)
    log = []
    for i, ts in enumerate(timestamps):
        log.append(chain.append(
            tool=f"tool_{i}", target=f"t{i}", result_summary="ok",
            arguments={"i": i}, event_id=f"e{i}", timestamp=ts,
        ))
    return log


class TestCryptoIntegrityUnaffected:
    def test_causally_impossible_chain_is_still_cryptographically_valid(self):
        # backwards + 1970 + futuro: el sello NO se rompe (integridad intacta).
        log = _chain([
            "2026-03-01T12:00:00Z",
            "2026-03-01T08:00:00Z",   # antes que el anterior
            "1970-01-01T00:00:00Z",   # sentinela epoch
            "2099-12-31T23:59:59Z",   # futuro
        ])
        r = verify_tool_execution_log(log)
        assert r.valid is True, "el sello NO debe romperse por timestamps implausibles"


class TestTimelinePlausibility:
    def test_backwards_timestamps_flagged(self):
        log = _chain(["2026-03-01T12:00:00Z", "2026-03-01T08:00:00Z"])
        r = verify_tool_execution_log(log)
        assert r.timeline_plausible is False
        assert any(a.get("type") == "NON_MONOTONIC_TIMESTAMP" for a in r.temporal_anomalies)

    def test_out_of_range_epoch_flagged(self):
        log = _chain(["2026-03-01T12:00:00Z", "1970-01-01T00:00:00Z"])
        r = verify_tool_execution_log(log)
        assert r.timeline_plausible is False
        # 1970 es a la vez fuera de rango y no-monotónico; basta con detectarlo.
        assert any(a.get("type") in ("OUT_OF_RANGE_TIMESTAMP", "NON_MONOTONIC_TIMESTAMP")
                   for a in r.temporal_anomalies)

    def test_future_2099_flagged_out_of_range(self):
        log = _chain(["2026-03-01T12:00:00Z", "2099-12-31T23:59:59Z"])
        r = verify_tool_execution_log(log)
        assert r.timeline_plausible is False
        assert any(a.get("type") == "OUT_OF_RANGE_TIMESTAMP" for a in r.temporal_anomalies)

    def test_monotonic_in_range_chain_is_plausible(self):
        log = _chain([
            "2026-03-01T08:00:00Z",
            "2026-03-01T09:00:00Z",
            "2026-03-01T09:00:00Z",   # igual (no-decreciente) — OK
            "2026-03-01T10:00:00Z",
        ])
        r = verify_tool_execution_log(log)
        assert r.timeline_plausible is True
        assert r.temporal_anomalies == []
        assert r.valid is True

    def test_to_dict_exposes_timeline_fields(self):
        log = _chain(["2026-03-01T12:00:00Z", "2026-03-01T08:00:00Z"])
        d = verify_tool_execution_log(log).to_dict()
        assert "timeline_plausible" in d
        assert "temporal_anomalies" in d
        assert d["timeline_plausible"] is False


class TestVerifyChainDirect:
    def test_verify_chain_low_level_flags_backwards(self):
        links = []
        prev = "0" * 64
        for seq, ts in enumerate(["2026-03-01T12:00:00Z", "2026-03-01T08:00:00Z"], start=1):
            link = build_link(seq, prev, {"timestamp": ts, "tool": f"t{seq}"})
            links.append(link)
            prev = link.entry_hash
        r = verify_chain(links)
        assert r.valid is True
        assert r.timeline_plausible is False
