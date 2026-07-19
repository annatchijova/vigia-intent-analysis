"""
tests/test_caie_b154_network_absence.py
=======================================
B-154 — absence of network fields (memory NEVER network-analyzed) must NOT be
emitted as `memory_shows_no_network_activity` (a positive "analyzed, found no
activity" observation). That assertion is the sole input to the LOG_VS_MEMORY
fabrication rule (caie.py:1528-1558, severity 0.75-0.95): letting ABSENCE feed
it means "I did not analyze the network layer" is used to accuse a log of
fabrication — the exact absence≡negative conflation that Forge's disposition.py
("Findings and audit completeness are separate dimensions") and Cronos's
detect_negation ("absence ... attenuating context, not positive confirmation")
were built to prevent. Both were ported from VIGÍA's own abstention doctrine;
this CAIE path regressed from it.

Four-state model (NetworkObservation), at the assertion level:
  ANALYZED_WITH_ACTIVITY -> memory_shows_network_activity
  ANALYZED_NO_ACTIVITY   -> memory_shows_no_network_activity     (may feed the rule)
  NOT_ANALYZED           -> memory_network_not_analyzed          (must NOT accuse)
  ANALYSIS_FAILED        -> memory_network_analysis_failed       (must NOT accuse)

Red-first: tests 1 and 3 fail against the current else-branch (caie.py:1072-1073);
test 2 is the regression guard that must stay green (no over-correction).
"""
from __future__ import annotations

from vigia.tools.caie import Artifact, _extract_assertions

_MEM = "memory_process"


def _assertions(metadata: dict) -> frozenset:
    return _extract_assertions(Artifact("mem_tool", _MEM, 0.5, "memory artifact", metadata=metadata))


# ── Test 1 — NOT_ANALYZED: no network fields at all ────────────────────────────
def test_absent_network_fields_not_asserted_as_no_activity():
    a = _assertions({"pid": 1234})  # memory present, network layer never analyzed
    assert "memory_shows_no_network_activity" not in a   # RED before fix
    assert "memory_network_not_analyzed" in a            # epistemic state preserved


# ── Test 2 — ANALYZED_NO_ACTIVITY: field present, empty (regression guard) ─────
def test_present_empty_network_field_is_analyzed_no_activity():
    a = _assertions({"pid": 1234, "network_connections": []})
    assert "memory_shows_no_network_activity" in a       # must stay GREEN
    assert "memory_network_not_analyzed" not in a


# ── Test 3 — ANALYSIS_FAILED: field present but malformed ──────────────────────
def test_malformed_network_field_degrades_not_accuses():
    a = _assertions({"pid": 1234, "network_connections": "none"})  # string, not a list
    assert "memory_shows_no_network_activity" not in a   # RED before fix (no accusation)
    assert "memory_network_analysis_failed" in a


# ── ANALYZED_WITH_ACTIVITY still works ─────────────────────────────────────────
def test_present_populated_network_field_shows_activity():
    a = _assertions({"pid": 1234, "network_connections": [{"dst": "8.8.8.8"}]})
    assert "memory_shows_network_activity" in a
    assert "memory_shows_no_network_activity" not in a


# ── dest_ip present-but-empty is analyzed-no-activity (not "not analyzed") ──────
def test_present_empty_dest_ip_is_analyzed_no_activity():
    a = _assertions({"pid": 1234, "dest_ip": ""})
    assert "memory_shows_no_network_activity" in a
    assert "memory_network_not_analyzed" not in a
