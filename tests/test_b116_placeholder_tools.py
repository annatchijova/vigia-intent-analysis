"""
B-116 (condition 4) — acquisition/conversion placeholders are not analysis tools.

Kimi's audit reproduced the B-116 dry-run census exactly: of the 66
ABSTAIN_INSUFFICIENT_TOOLS cases, the dominant source_tool values are
None(91), legacy_converter(88), manual_forensic_review(43),
generate_forensic_hash(35) and read_evidence(8) — all acquisition or
conversion utilities, none of them an analysis tool. Counting them as
distinct tools made the diversity check measure conversion pipelines, not
analytic independence; 31/66 of those cases have >= 2 distinct
evidence_type values and can satisfy diversity through the fallback chain.

Decision (Kimi-endorsed, maintainer-delegated): the four placeholder
strings must not count as tools. They are treated exactly like the literal
"unknown": skipped in the tool_name -> source_tool -> evidence_type
fallback chain. The set lives in ONE place (this gate module), not
replicated in the dry-run script.

The gate remains unwired (zero production callers), so this moves no
verdict today; the dry-run re-measurement quantifies the effect.
"""

import pytest

from vigia.core.signal_quality_gate import (
    _NON_ANALYSIS_PLACEHOLDERS,
    SignalQualityGate,
)


class _Sig:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


@pytest.fixture
def gate():
    return SignalQualityGate()


class TestPlaceholderSet:
    def test_the_four_approved_placeholders(self):
        """Invariant: exactly the census-approved set, in one place.
        Mutation caught: silently widening/narrowing the set."""
        assert _NON_ANALYSIS_PLACEHOLDERS == frozenset({
            "legacy_converter",
            "manual_forensic_review",
            "generate_forensic_hash",
            "read_evidence",
        })


class TestFallbackChain:
    @pytest.mark.parametrize("placeholder", sorted(_NON_ANALYSIS_PLACEHOLDERS))
    def test_placeholder_source_tool_falls_back_to_evidence_type(
            self, gate, placeholder):
        """A placeholder source_tool must not become the tool identity —
        the chain falls through to evidence_type, exactly as it already
        does for the literal "unknown"."""
        sig = _Sig(tool_name=None, source_tool=placeholder,
                   evidence_type="usn_journal")
        assert gate._get_tool_name(sig) == "usn_journal"

    def test_placeholders_do_not_create_fake_tool_diversity(self, gate):
        """Two signals whose only difference is WHICH conversion utility
        wrote them share one analytic identity. Before this fix they
        counted as two distinct tools and satisfied the diversity check."""
        a = _Sig(tool_name=None, source_tool="legacy_converter",
                 evidence_type="log_entry")
        b = _Sig(tool_name=None, source_tool="generate_forensic_hash",
                 evidence_type="log_entry")
        assert gate._get_tool_name(a) == gate._get_tool_name(b) == "log_entry"

    def test_real_tool_names_still_win(self, gate):
        """A genuine analysis tool keeps its identity — the placeholder set
        must not swallow real tools."""
        sig = _Sig(tool_name=None, source_tool="vol3_windows_pslist",
                   evidence_type="memory_process")
        assert gate._get_tool_name(sig) == "vol3_windows_pslist"

    def test_placeholder_with_no_evidence_type_is_unknown(self, gate):
        """Fail closed: a placeholder with nothing behind it counts as
        absent, never as a distinct tool."""
        sig = _Sig(tool_name=None, source_tool="read_evidence",
                   evidence_type=None)
        assert gate._get_tool_name(sig) == "unknown"

    def test_dict_signals_follow_the_same_rule(self, gate):
        sig = {"source_tool": "manual_forensic_review",
               "evidence_type": "file_hash"}
        assert gate._get_tool_name(sig) == "file_hash"
