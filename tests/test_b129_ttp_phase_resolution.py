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

    def test_garbage_with_id_prefix_does_not_resolve(self):
        """Adversarial-review finding (2026-08-27): without a boundary
        after the id, 'T1070abc' resolved to DEFENSE_EVASION and cast a
        +40 phase vote. A malformed bundle field must yield None."""
        assert resolve_ttp_phase("T1070abc") is None
        assert resolve_ttp_phase("T1059x99") is None
        assert resolve_ttp_phase("T1070.006extra") is None

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

    def test_non_string_violation_type_does_not_crash(self):
        """Adversarial-review finding (2026-08-27): Rule 2 called
        .upper() on violation['type'] unconditionally — a None/numeric
        type aborted the whole corpus measurement."""
        engine = VisibleVariablesEngine()
        phase, _ = engine.detect_phase(
            signals=[],
            temporal_violations=[{"type": None}, {"type": 7}, {}],
        )
        assert phase is IRPhase.UNKNOWN

    def test_determinism_double_run(self):
        engine = VisibleVariablesEngine()
        args = dict(
            signals=[{"type": "temporal"}],
            temporal_violations=[{"type": "EFFECT_BEFORE_CAUSE"}],
            mitre_ttps=["T1070.006", "T1048"],
        )
        assert engine.detect_phase(**args) == engine.detect_phase(**args)


class TestSingleTacticAdditions:
    """2026-08-27 (second batch): the four highest-frequency unresolved
    TTPs from the corpus census that are SINGLE-tactic in MITRE ATT&CK —
    the unambiguous class the registry update identified. Multi-tactic
    techniques (T1078, T1055, T1053) stay deliberately absent: a
    single-phase table cannot represent them without a design decision."""

    def test_t1027_obfuscated_files_is_defense_evasion(self):
        assert resolve_ttp_phase("T1027") is IRPhase.DEFENSE_EVASION

    def test_t1036_masquerading_is_defense_evasion(self):
        assert resolve_ttp_phase("T1036") is IRPhase.DEFENSE_EVASION
        assert resolve_ttp_phase("T1036.005") is IRPhase.DEFENSE_EVASION

    def test_t1190_exploit_public_facing_is_initial_access(self):
        assert resolve_ttp_phase("T1190") is IRPhase.INITIAL_ACCESS

    def test_t1486_data_encrypted_is_impact(self):
        assert resolve_ttp_phase("T1486") is IRPhase.IMPACT

    def test_multi_tactic_techniques_stay_unmapped(self):
        """Guard: adding any of these requires a design decision first."""
        assert resolve_ttp_phase("T1078") is None
        assert resolve_ttp_phase("T1055") is None
        assert resolve_ttp_phase("T1053") is None

    def test_t1547_001_key_is_valid_mitre_id(self):
        """The table carried "T1547.1" — not a valid MITRE id (the format
        is .001). The corrected key must resolve exactly, and the parent
        fallback covers other T1547 subtechniques."""
        assert "T1547.1" not in MITRE_TTP_TO_PHASE
        assert "T1547.001" in MITRE_TTP_TO_PHASE
        assert resolve_ttp_phase("T1547.001") is IRPhase.PERSISTENCE

    def test_t1547_key_also_fixed_in_picerl_table(self):
        """Adversarial-review finding (2026-08-27): the parallel
        MITRE_TTPS_BY_PHASE table in picerl_mapping.py — which flows
        into generated PICERL reports — still carried the invalid id."""
        from vigia.tools.picerl_mapping import MITRE_TTPS_BY_PHASE
        all_ids = [t for ids in MITRE_TTPS_BY_PHASE.values() for t in ids]
        assert "T1547.1" not in all_ids
        assert "T1547.001" in all_ids


class TestTablesStayFrozen:
    def test_tables_are_read_only(self):
        assert isinstance(MITRE_TTP_TO_PHASE, MappingProxyType)
        assert isinstance(TEMPORAL_VIOLATION_TO_PHASE, MappingProxyType)
