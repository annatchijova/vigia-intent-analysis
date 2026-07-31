"""
B-224: Mode-1's self-correction loop is structurally inert.

`ContradictionDetector.detect()` implements 4 rules. Three of them are keyed to
fields that no production code path ever produces, so they cannot match any
input:

  Rule 1 ENTROPY_VS_BEHAVIORAL  filters on `signal["tool"]`, but Mode-1 signals
                                carry `evidence_type` / `source` and never a
                                `tool` key (196/196 signals across the whole
                                21-case corpus have tool=None).
  Rule 2 SEMIOTIC_VS_TECHNICAL  reads module_results["technical_result"]
                                ["alert_level"], but `technical_result` (and
                                `semiotic_result`) are READ at vigia_agent.py
                                :464-465 and SET nowhere in the repository --
                                not in any module, not even in tests. The
                                .get(..., "LOW") default therefore always wins,
                                while the rule requires HIGH/CRITICAL.
  Rule 4 VERDICT_FLIP           requires `"BENIGN" in best_hypothesis.upper()`,
                                but the producer's complete vocabulary is
                                UNDETERMINED / REASONER_ERROR / ABSTAIN_V2 /
                                MALICIOUS_INTENT_DETECTED / INTENT_DETECTED /
                                SUSPICION_DETECTED / NO_ANOMALY_DETECTED /
                                NO_SEMIOTIC_ANOMALY_DETECTED / PIPELINE_ERROR.
                                Mode-1 spells "benign" as NO_*_ANOMALY_DETECTED,
                                so the substring never appears.

That leaves Rule 3 (CONFIDENCE_COLLAPSE) as the only reachable rule, and it
appends at most ONE contradiction. `CONTRADICTION_THRESHOLD = 2` gates
correction on `len(contradictions) >= 2`. Maximum achievable is therefore 1 < 2:
`_apply_self_correction` returns (False, results) for every possible input, so
no correction is ever applied -- not merely "none on this corpus".

Downstream, structurally and not case-dependently:
  - `self_corrections_applied` is always 0 and `iterations_executed` always 1
    (the documented "max 3 iterations" self-correction loop never iterates);
  - `sans_compliance.self_correction` (= iteration > 0 or corrections > 0) can
    only ever be False;
  - the CLAUDE.md-mandated chained `contradiction_detector` self-correction
    event can never be emitted by Mode-1. Note this is NOT because the chaining
    is unwired -- `reasoning_trace.build_from_agent_bundle` does chain
    `pipeline_results["self_corrections"]` as contradiction_detector entries
    (verified against a live run) -- but because the upstream detector can never
    produce an input for it. B-151(b) attributes the same gap to missing
    wiring; that attribution is stale, the real cause is upstream.

This test pins the dormancy as measured, so it cannot silently drift. Every
assertion here documents CURRENT BROKEN STATE, not desired behaviour: each one
is expected to FAIL the day someone wires a producer for `tool` /
`technical_result`, or aligns Rule 4 with the real vocabulary. That failure is
the point -- it forces whoever revives a rule to confront the
CONTRADICTION_THRESHOLD interaction (reviving exactly one rule still yields
1 < 2 and changes nothing) and to re-validate the corpus, since a live
correction rewrites `best_hypothesis` and can move sealed verdicts.
"""

from __future__ import annotations

import subprocess
from fractions import Fraction
from pathlib import Path

import pytest

from vigia_agent import CONTRADICTION_THRESHOLD, ContradictionDetector

REPO = Path(__file__).resolve().parent.parent


# ── the three structurally unreachable rules ────────────────────────────────

def test_rule1_cannot_match_because_signals_have_no_tool_key():
    """Rule 1 filters on signal["tool"]; production signals use evidence_type/
    source. Feeding it a perfect Rule-1 scenario in the REAL key shape yields
    nothing."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {},
        "signals": [
            # would satisfy "high entropy": z > 2.5 on a memory/disk source
            {"evidence_type": "memory_process", "source": "memory_forensics",
             "z_score": 9.0, "confidence": 0.9},
            # would satisfy "normal behaviour": z < 0.5 on behavioral_fingerprint
            {"evidence_type": "behavioral", "source": "behavioral_fingerprint",
             "z_score": 0.1, "confidence": 0.9},
        ],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


def test_rule1_would_match_if_signals_carried_a_tool_key():
    """Control for the test above: the rule's logic is fine -- only the key name
    is wrong. Same scenario, `tool` instead of `source`, and it fires."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {},
        "signals": [
            {"tool": "memory_forensics", "z_score": 9.0, "confidence": 0.9},
            {"tool": "behavioral_fingerprint", "z_score": 0.1, "confidence": 0.9},
        ],
    }
    assert len(detector.detect(module_results, Fraction(1, 2))) == 1


def test_rule2_technical_result_and_semiotic_result_have_no_producer():
    """Rule 2's two inputs are read in exactly one place and written nowhere, so
    its .get(..., 'LOW') default always wins against a HIGH/CRITICAL condition.
    A grep is the honest check here: the claim is about the whole repository, not
    about one call path."""
    for key in ("technical_result", "semiotic_result"):
        hits = subprocess.run(
            ["grep", "-rn", key, "--include=*.py", "."],
            cwd=REPO, capture_output=True, text=True,
        ).stdout.splitlines()
        # The only permitted occurrences are the two reads in the detector and
        # this test file's own docstring/source naming the keys. Matched on the
        # exact line, not a prefix -- a `:46` prefix would also swallow line 46
        # and anything in the 4600s.
        allowed_reads = {"./vigia_agent.py:464", "./vigia_agent.py:465"}
        offenders = [
            h for h in hits
            if "tests/test_b224_contradiction_detector_dormancy.py" not in h
            and h.rsplit(":", 1)[0] not in allowed_reads
            and ":".join(h.split(":", 2)[:2]) not in allowed_reads
        ]
        assert not offenders, (
            f"{key!r} now has occurrences beyond the two reads at "
            f"vigia_agent.py:464-465: {offenders}. If a PRODUCER was added, "
            f"Rule 2 (SEMIOTIC_VS_TECHNICAL) may have become reachable -- see "
            f"this module's docstring: reviving one rule alone still leaves "
            f"max=1 < CONTRADICTION_THRESHOLD=2, and making corrections live "
            f"changes sealed verdicts, so re-validate the corpus."
        )


def test_rule2_cannot_match_with_the_real_module_results_shape():
    detector = ContradictionDetector()
    # A case that SHOULD be the canonical Rule-2 hit: benign semiotics, critical
    # technical alert. Nothing produces these keys, so the rule never sees them.
    module_results = {
        "abduction": {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED"},
        "signals": [{"evidence_type": "log_entry", "z_score": 1.0, "confidence": 0.9}],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


@pytest.mark.parametrize("benign_hypothesis", [
    "NO_ANOMALY_DETECTED",
    "NO_SEMIOTIC_ANOMALY_DETECTED",
])
def test_rule4_cannot_match_the_real_benign_vocabulary(benign_hypothesis):
    """Rule 4 looks for the substring "BENIGN"; Mode-1 spells benign as
    NO_*_ANOMALY_DETECTED."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": benign_hypothesis, "is_conclusive": True},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 4.0, "confidence": 0.9}],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


def test_rule4_would_match_the_literal_string_BENIGN():
    """Control: the rule works, the vocabulary just never says BENIGN."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "BENIGN", "is_conclusive": True},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 4.0, "confidence": 0.9}],
    }
    assert len(detector.detect(module_results, Fraction(1, 2))) == 1


def test_abductive_vocabulary_never_contains_benign():
    """The producer's side of the Rule-4 mismatch, asserted at the source so it
    is not just an observation about one corpus."""
    reasoner = (REPO / "vigia" / "inference" / "abductive_reasoner.py").read_text()
    assigned = [
        line.split("=", 1)[1].strip().strip('",')
        for line in reasoner.splitlines()
        if "best_hypothesis" in line and "=" in line and '"' in line
    ]
    literals = [a for a in assigned if a and a.isupper()]
    assert literals, "no best_hypothesis literals found -- did the producer move?"
    assert not [lit for lit in literals if "BENIGN" in lit], (
        f"a BENIGN-containing hypothesis literal now exists ({literals}) -- "
        f"Rule 4 may have become reachable; see this module's docstring."
    )


# ── the threshold makes the one reachable rule insufficient ─────────────────

def test_rule3_is_the_only_reachable_rule_and_yields_exactly_one():
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "SUSPICION_DETECTED", "is_conclusive": True},
        # mca high, >70% of signals below confidence 0.3
        "signals": [{"z_score": 1.0, "confidence": 0.1} for _ in range(9)]
                   + [{"z_score": 1.0, "confidence": 0.9}],
    }
    found = detector.detect(module_results, Fraction(8, 10))
    assert len(found) == 1
    assert found[0][0] == ["mcp_aggregator", "individual_modules"]


def test_max_achievable_contradictions_is_below_the_correction_threshold():
    """The whole finding in one assertion: stack every rule's trigger conditions
    at once, using only shapes production actually emits, and the detector still
    returns fewer contradictions than CONTRADICTION_THRESHOLD requires -- so
    _apply_self_correction can never apply a correction."""
    detector = ContradictionDetector()
    module_results = {
        # Rule 4 trigger, real vocabulary (dead). Rule 1 trigger, real keys (dead).
        "abduction": {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED",
                      "is_conclusive": True},
        "signals": [
            {"evidence_type": "memory_process", "source": "memory_forensics",
             "z_score": 9.0, "confidence": 0.1},
        ] + [{"z_score": 4.0, "confidence": 0.1} for _ in range(9)],
    }
    found = detector.detect(module_results, Fraction(9, 10))  # Rule 3 trigger (live)
    assert len(found) < CONTRADICTION_THRESHOLD, (
        f"max achievable contradictions ({len(found)}) reached "
        f"CONTRADICTION_THRESHOLD ({CONTRADICTION_THRESHOLD}) -- Mode-1 "
        f"self-correction is no longer inert. This is the intended eventual "
        f"outcome, but it CHANGES SEALED VERDICTS (a correction rewrites "
        f"best_hypothesis): re-validate the full corpus and update B-224 "
        f"before making this pass."
    )
    assert len(found) == 1  # exact measured value, pinned
