"""B-116 MODE C — `type` as last link of the gate's tool-identity fallback.

The VIGIA-REAL-*/SRL-* series (the project's most validated corpus)
declares its acquisition channel in a `type` field (`registry`,
`network_flow`, `bash_history`, ...) that the conversion never mapped to
`evidence_type`. Without this link, 16 real MALICE cases looked
mono-tool to the gate (class C1 of docs/B116_CONDITION4_DESIGN.md).
The gate remains UNWIRED — this guards the pending capability only.
"""
from __future__ import annotations

from vigia.core.signal_quality_gate import SignalQualityGate


def _sig(type_value: str, z: float) -> dict:
    # REAL-series shape: no tool_name, no source_tool, no evidence_type.
    return {"type": type_value, "z_score": z}


class TestTypeFallback:
    def test_diverse_type_field_counts_as_tool_diversity(self) -> None:
        sigs = [_sig("registry", 2.5), _sig("network_flow", 3.0), _sig("bash_history", 2.2)]
        result = SignalQualityGate().evaluate(sigs)
        assert result.reason_code != "ABSTAIN_INSUFFICIENT_TOOLS"

    def test_single_type_still_insufficient(self) -> None:
        sigs = [_sig("registry", 2.5), _sig("registry", 3.0)]
        result = SignalQualityGate().evaluate(sigs)
        assert result.reason_code == "ABSTAIN_INSUFFICIENT_TOOLS"

    def test_explicit_fields_still_win_over_type(self) -> None:
        sigs = [
            {"source_tool": "volatility", "type": "x", "z_score": 2.5},
            {"source_tool": "log2timeline", "type": "x", "z_score": 3.0},
        ]
        result = SignalQualityGate().evaluate(sigs)
        assert result.reason_code != "ABSTAIN_INSUFFICIENT_TOOLS"
