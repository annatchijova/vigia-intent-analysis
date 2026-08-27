"""
B-129 / L-027 groundwork — deterministic TTP-to-phase resolution.

The 2026-08-27 phase-distribution measurement
(scripts/dryrun_b129_phase_distribution.py) found that detect_phase()
Rule 1 only matched exact MITRE_TTP_TO_PHASE keys, so:

- subtechniques never mapped even when their parent technique is in the
  table (live-run census over results/: T1562.001 x43, T1070.001/.002/
  .006 x121 combined, T1566.003 x40 — all unmapped, parents mapped);
- TTP strings carrying prose suffixes emitted by narrative bundles
  ("T1070.002 (Indicator Removal ...)") never mapped;
- only 13 of 190 distinct TTPs observed in real result bundles resolved.

And TEMPORAL_VIOLATION_TO_PHASE lacked EFFECT_BEFORE_CAUSE — the one
violation type the scorer validates as authoritative (B-172), whose
semantic class (retroactive timestamp manipulation) the table already
maps via RETROACTIVE_MODIFICATION -> DEFENSE_EVASION.

These tests are red against the pre-fix module (verified) and pin the
resolution order: exact table hit > extracted-id hit > parent-technique
fallback > None. detect_phase() has zero production callers (the
pipeline only consumes get_visible_tools with an externally supplied
phase), so no sealed verdict changes.
"""
from __future__ import annotations

from types import MappingProxyType

from vigia.tools.visible_variables import (
    IRPhase,
    MITRE_TTP_TO_PHASE,
    TEMPORAL_VIOLATION_TO_PHASE,
    VisibleVariablesEngine,
    resolve_ttp_phase,
)


class TestResolveTtpPhase:
    def test_exact_match_unchanged(self):
        assert resolve_ttp_phase("T1070") is IRPhase.DEFENSE_EVASION
        assert resolve_ttp_phase("T1565.001") is IRPhase.DEFENSE_EVASION

    def test_subtechnique_falls_back_to_parent(self):
        assert resolve_ttp_phase("T1562.001") is IRPhase.DEFENSE_EVASION
        assert resolve_ttp_phase("T1070.006") is IRPhase.DEFENSE_EVASION
        assert resolve_ttp_phase("T1566.003") is IRPhase.INITIAL_ACCESS
        assert resolve_ttp_phase("T1071.001") is IRPhase.COMMAND_AND_CONTROL

    def test_exact_subtechnique_entry_has_priority_over_parent(self):
        """T1056.004 is CREDENTIAL_ACCESS in the table; its parent T1056 is
        absent — the exact entry must resolve, no parent needed."""
        assert resolve_ttp_phase("T1056.004") is IRPhase.CREDENTIAL_ACCESS

    def test_prose_suffix_is_normalized(self):
        assert (
            resolve_ttp_phase("T1070.002 (Indicator Removal — clear logs)")
            is IRPhase.DEFENSE_EVASION
        )
        assert (
            resolve_ttp_phase("T1566.001 (Spear Phishing Attachment)")
            is IRPhase.INITIAL_ACCESS
        )

    def test_unknown_technique_returns_none(self):
        assert resolve_ttp_phase("T9999") is None
        assert resolve_ttp_phase("T9999.001") is None

    def test_non_ttp_strings_return_none(self):
        assert resolve_ttp_phase("") is None
        assert resolve_ttp_phase("not a ttp") is None
        assert resolve_ttp_phase("1070.006") is None

    def test_non_string_returns_none(self):
        assert resolve_ttp_phase(None) is None
        assert resolve_ttp_phase(1070) is None

    def test_whitespace_is_tolerated(self):
        assert resolve_ttp_phase("  T1562.001  ") is IRPhase.DEFENSE_EVASION


class TestDetectPhaseUsesResolution:
    def test_subtechnique_ttp_detects_parent_phase(self):
        """RED pre-fix: T1562.001 (43 occurrences in live result bundles)
        yielded UNKNOWN because only exact keys matched."""
        engine = VisibleVariablesEngine()
        phase, consistency = engine.detect_phase(
            signals=[], mitre_ttps=["T1562.001"],
        )
        assert phase is IRPhase.DEFENSE_EVASION
        assert consistency > 0

    def test_effect_before_cause_maps_to_defense_evasion(self):
        """RED pre-fix: the scorer's only authoritative violation type
        (B-172) was absent from TEMPORAL_VIOLATION_TO_PHASE."""
        assert (
            TEMPORAL_VIOLATION_TO_PHASE["EFFECT_BEFORE_CAUSE"]
            is IRPhase.DEFENSE_EVASION
        )
        engine = VisibleVariablesEngine()
        phase, _ = engine.detect_phase(
            signals=[],
            temporal_violations=[{"type": "EFFECT_BEFORE_CAUSE"}],
        )
        assert phase is IRPhase.DEFENSE_EVASION

    def test_no_inputs_still_unknown(self):
        engine = VisibleVariablesEngine()
        phase, consistency = engine.detect_phase(signals=[])
        assert phase is IRPhase.UNKNOWN
        assert consistency == 0

    def test_determinism_double_run(self):
        engine = VisibleVariablesEngine()
        args = dict(
            signals=[{"type": "temporal"}],
            temporal_violations=[{"type": "EFFECT_BEFORE_CAUSE"}],
            mitre_ttps=["T1070.006", "T1048"],
        )
        assert engine.detect_phase(**args) == engine.detect_phase(**args)


class TestTablesStayFrozen:
    def test_tables_are_read_only(self):
        assert isinstance(MITRE_TTP_TO_PHASE, MappingProxyType)
        assert isinstance(TEMPORAL_VIOLATION_TO_PHASE, MappingProxyType)
