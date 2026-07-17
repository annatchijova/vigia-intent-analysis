"""
B-116 (partial unblock) — SignalQualityGate tool-name fallback chain.

The gate expected `tool_name` on every signal; the scorer's artifacts carry
`source_tool` (frequently the literal "unknown" in legacy conversions) and a
reliably populated `evidence_type`. Under the old lookup, 67/199 corpus cases
failed ABSTAIN_INSUFFICIENT_TOOLS purely because the field was never
populated during conversion — not because the evidence lacked provenance
diversity (2026-07-14 dry-run, B-116 registry entry).

Unblocking condition 3 of B-116 prescribes the fallback:
tool_name -> source_tool -> evidence_type, treating "unknown" as absent.

The gate remains UNWIRED (zero production callers) — this change only makes
future dry-runs measure real diversity instead of a data-quality artifact.
Also covered here: the byte-identical duplicate vigia/signal_quality_gate.py
was removed; vigia.core.signal_quality_gate is the only copy.
"""

import importlib

import pytest

from vigia.core.signal_quality_gate import SignalQualityGate


class _Sig:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


@pytest.fixture
def gate():
    return SignalQualityGate()


class TestB116ToolNameFallback:
    def test_tool_name_still_wins(self, gate):
        assert gate._get_tool_name({"tool_name": "vol3", "source_tool": "x"}) == "vol3"

    def test_source_tool_fallback_for_dicts(self, gate):
        assert gate._get_tool_name({"source_tool": "prefetch_analyzer"}) == "prefetch_analyzer"

    def test_evidence_type_fallback_when_source_tool_unknown(self, gate):
        sig = {"source_tool": "unknown", "evidence_type": "registry_key"}
        assert gate._get_tool_name(sig) == "registry_key"

    def test_unknown_never_counts_as_distinct_tool(self, gate):
        assert gate._get_tool_name({"source_tool": "unknown"}) == "unknown"

    def test_attribute_style_signals(self, gate):
        sig = _Sig(source_tool="unknown", evidence_type="memory_process")
        assert gate._get_tool_name(sig) == "memory_process"

    def test_diversity_check_uses_fallback(self, gate):
        """Two signals with source_tool=unknown but distinct evidence_types
        must count as 2 tools for the diversity check (they were 1 'unknown'
        before, failing ABSTAIN_INSUFFICIENT_TOOLS)."""
        signals = [
            {"source_tool": "unknown", "evidence_type": "registry_key", "z_score": 2.5},
            {"source_tool": "unknown", "evidence_type": "event_log", "z_score": 3.1},
        ]
        check = gate._check_tool_diversity(signals)
        assert check["unique_tools"] == 2
        assert check["passed"] is True


class TestB116DuplicateRemoved:
    def test_root_duplicate_gone(self):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("vigia.signal_quality_gate")

    def test_core_copy_importable(self):
        mod = importlib.import_module("vigia.core.signal_quality_gate")
        assert hasattr(mod, "SignalQualityGate")
