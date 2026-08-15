"""
B-224: Mode-1's self-correction loop — which rules are live, and why.

`ContradictionDetector.detect()` implements 4 rules. Before this entry was
closed, none of them could contribute enough to trigger a correction, so
`_detect_and_correct` returned (False, results) for every possible input.
That is now fixed, and the reachability of each rule is pinned here.

  Rule 1 ENTROPY_VS_BEHAVIORAL  DORMANT. Filters on `signal["tool"]`, but this
                                path's signals carry `evidence_type` / `source`
                                and never a `tool` key, and nothing in the
                                repository produces behavioral_fingerprint
                                signals. Deliberately NOT re-keyed to `source`:
                                that field holds collection tools
                                (sift_netflow, Plaso/WinEVT, ...), not the
                                analytic module names the rule compares, so a
                                rename would make it look wired while still
                                never matching. It needs a producer.
  Rule 2 SEMIOTIC_VS_TECHNICAL  DORMANT. Reads module_results["technical_result"]
                                ["alert_level"], and neither `technical_result`
                                nor `semiotic_result` is written anywhere in the
                                repository, so the .get(..., "LOW") default
                                always wins against a HIGH/CRITICAL condition.
  Rule 3 CONFIDENCE_COLLAPSE    DORMANT, and unreachable by ARITHMETIC rather
                                than by a missing producer -- this corrects the
                                original B-224 entry, which recorded rule 3 as
                                "the only reachable rule". `_detect_and_correct`
                                derives `mca_score` as the mean of the very
                                confidences the rule thresholds on, so the rule
                                demands mean > 6/10 while more than 7/10 of the
                                terms are < 3/10. With k/n > 7/10 the mean is
                                bounded above by 1 - 7/10*(k/n) < 51/100, which
                                never exceeds 6/10. It fires only if `mca_score`
                                is supplied by a DIFFERENT aggregator, which no
                                caller does.
  Rule 4 VERDICT_FLIP           LIVE, and the only live rule. It previously
                                required the literal "BENIGN" in
                                best_hypothesis while this path spells benign as
                                NO_*_ANOMALY_DETECTED, so it could not match; it
                                now tests BENIGN_HYPOTHESES.

Reachable maximum is therefore 1, which is why CONTRADICTION_THRESHOLD moved
from 2 to 1 in the same change: aligning rule 4's vocabulary without touching
the threshold would have left the loop exactly as unreachable. The two-source
bar is not weakened by that move -- rule 4 already requires >= 2 independent
high-magnitude signals inside its own predicate.

Corpus impact of the whole change, measured over the 21 cases under
`cases/input/`: zero. No case produces even one contradiction, so no sealed
verdict moved. The loop is quiet here, not dead -- and the tests below prove
the difference by driving a correction end to end on synthetic input.
"""

from __future__ import annotations

import subprocess
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

import pytest

from vigia_agent import (
    BENIGN_HYPOTHESES,
    CONTRADICTION_THRESHOLD,
    ContradictionDetector,
    VIGIAAgent,
)

REPO = Path(__file__).resolve().parent.parent


# ── Rule 1: dormant for want of a producer ──────────────────────────────────

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


# ── Rule 2: dormant for want of a producer ──────────────────────────────────

def test_rule2_technical_result_and_semiotic_result_have_no_producer():
    """Rule 2's two inputs are read, never written, so its .get(..., 'LOW')
    default always wins against a HIGH/CRITICAL condition. A grep is the honest
    check here: the claim is about the whole repository, not one call path."""
    for key in ("technical_result", "semiotic_result"):
        hits = subprocess.run(
            # --exclude-dir=mutants: mutation-testing sandbox (gitignored), a
            # copy of the tree with injected defects. Its duplicates of
            # vigia_agent.py would count as new producers of the key.
            ["grep", "-rn", key, "--include=*.py", "--exclude-dir=mutants", "."],
            cwd=REPO, capture_output=True, text=True,
        ).stdout.splitlines()
        # Permitted occurrences, matched by content rather than by line number
        # (which drifts under any surgical edit above the detector):
        #   1. the read itself -- `module_results.get("<key>"...)` or
        #      `module_results["<key>"]` -- in vigia_agent.py.
        #   2. the B-224 dormancy CHECK, which tests for the key's absence in
        #      order to report the rule as unevaluable.
        #   3. documentation prose naming the key as having no producer.
        # None of these is a producer; a write would be.
        def _is_permitted(line: str) -> bool:
            if "tests/test_b224_contradiction_detector_dormancy.py" in line:
                return True
            if not line.startswith("./vigia_agent.py:"):
                return False
            return (
                f'module_results.get("{key}"' in line
                or f'module_results["{key}"]' in line
                or f'"{key}" not in module_results' in line   # dormancy check
                or f"'{key}'" in line                          # dormancy message
                or "no producer" in line                       # B-224 prose
            )

        offenders = [h for h in hits if not _is_permitted(h)]
        assert not offenders, (
            f"{key!r} now has occurrences beyond the read, the dormancy check "
            f"and documentation in vigia_agent.py: {offenders}. If a PRODUCER "
            f"was added, Rule 2 became reachable -- the reachable maximum rises "
            f"above 1 and a correction rewrites best_hypothesis, so re-validate "
            f"the corpus and update B-224/L-069 before letting this pass."
        )


def test_rule2_cannot_match_with_the_real_module_results_shape():
    detector = ContradictionDetector()
    # A case that SHOULD be the canonical Rule-2 hit: benign semiotics, critical
    # technical alert. Nothing produces these keys, so the rule never sees them.
    module_results = {
        "abduction": {"best_hypothesis": "SUSPICION_DETECTED"},
        "signals": [{"evidence_type": "log_entry", "z_score": 1.0, "confidence": 0.9}],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


# ── Rule 3: dormant by arithmetic, not by a missing producer ────────────────

def _mca_like_agent(confidences):
    """Replicates _detect_and_correct's confidence branch exactly."""
    n = Fraction(len(confidences), 1)
    return min(
        Fraction(1, 1),
        max(Fraction(0, 1),
            sum((max(Fraction(0, 1), min(Fraction(1, 1), c)) for c in confidences),
                Fraction(0, 1)) / n),
    )


def test_rule3_conditions_are_jointly_unsatisfiable_when_mca_is_derived():
    """Rule 3 wants mean > 6/10 while > 7/10 of the terms are < 3/10. Since the
    agent derives the mean FROM those terms, the two conditions exclude each
    other. Exhaustive over a 1/20 lattice up to 7 signals -- no counterexample.
    """
    grid = [Fraction(i, 20) for i in range(21)]
    for n in range(1, 8):
        for combo in combinations_with_replacement(grid, n):
            mca = _mca_like_agent(list(combo))
            if mca <= Fraction(6, 10):
                continue
            low = [c for c in combo if c < Fraction(3, 10)]
            assert Fraction(len(low), n) <= Fraction(7, 10), (
                f"counterexample: {combo} gives mca={mca} with "
                f"{len(low)}/{n} below 3/10 -- Rule 3 became reachable "
                f"through the derived MCA. Reachable maximum is no longer 1; "
                f"re-validate the corpus and update B-224/L-069."
            )


def test_rule3_fires_only_when_mca_is_supplied_independently():
    """Control: the rule's logic is fine. Hand it an MCA that did NOT come from
    these confidences and it fires -- which is exactly the aggregator it was
    written for, and which no caller provides."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "SUSPICION_DETECTED", "is_conclusive": True},
        "signals": [{"z_score": 1.0, "confidence": 0.1} for _ in range(9)]
                   + [{"z_score": 1.0, "confidence": 0.9}],
    }
    found = detector.detect(module_results, Fraction(8, 10))
    assert len(found) == 1
    assert found[0][0] == ["mcp_aggregator", "individual_modules"]
    # ...and the same signals, scored the way the agent actually scores them,
    # do not reach the rule's MCA condition at all.
    assert _mca_like_agent([Fraction(1, 10)] * 9 + [Fraction(9, 10)]) <= Fraction(6, 10)


# ── Rule 4: live ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("benign_hypothesis", [
    "NO_ANOMALY_DETECTED",
    "NO_SEMIOTIC_ANOMALY_DETECTED",
])
def test_rule4_now_matches_the_real_benign_vocabulary(benign_hypothesis):
    """The B-224 fix: Mode-1 spells benign as NO_*_ANOMALY_DETECTED, and the
    rule used to look only for the literal "BENIGN"."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": benign_hypothesis, "is_conclusive": True},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 4.0, "confidence": 0.9}],
    }
    found = detector.detect(module_results, Fraction(1, 2))
    assert len(found) == 1
    assert found[0][0] == ["abductive_reasoner", "sift_signals"]


def test_rule4_still_matches_the_literal_string_BENIGN():
    """Other paths in this repository (quadripartite, the integration bridges)
    do emit "BENIGN"; the detector must stay correct for them too."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "BENIGN", "is_conclusive": True},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 4.0, "confidence": 0.9}],
    }
    assert len(detector.detect(module_results, Fraction(1, 2))) == 1


def test_rule4_still_requires_two_independent_high_magnitude_signals():
    """The two-source bar lives inside the rule, which is what makes
    CONTRADICTION_THRESHOLD = 1 defensible. One critical signal is not enough."""
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "NO_ANOMALY_DETECTED", "is_conclusive": True},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 1.0, "confidence": 0.9}],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


def test_rule4_does_not_fire_on_an_inconclusive_hypothesis():
    detector = ContradictionDetector()
    module_results = {
        "abduction": {"best_hypothesis": "NO_ANOMALY_DETECTED", "is_conclusive": False},
        "signals": [{"z_score": 5.0, "confidence": 0.9},
                    {"z_score": 4.0, "confidence": 0.9}],
    }
    assert detector.detect(module_results, Fraction(1, 2)) == []


def test_abductive_vocabulary_still_never_contains_benign():
    """The producer's side of the mismatch, asserted at the source. This is why
    BENIGN_HYPOTHESES has to list the NO_*_ANOMALY_DETECTED spellings: if the
    producer ever starts emitting a literal BENIGN, the constant is redundant
    rather than wrong, but the change should be a deliberate one."""
    reasoner = (REPO / "vigia" / "inference" / "abductive_reasoner.py").read_text()
    assigned = [
        line.split("=", 1)[1].strip().strip('",')
        for line in reasoner.splitlines()
        if "best_hypothesis" in line and "=" in line and '"' in line
    ]
    literals = [a for a in assigned if a and a.isupper()]
    assert literals, "no best_hypothesis literals found -- did the producer move?"
    assert not [lit for lit in literals if "BENIGN" in lit], (
        f"a BENIGN-containing hypothesis literal now exists ({literals}); "
        f"BENIGN_HYPOTHESES already covers it, but confirm the producer change "
        f"was intended."
    )


def test_benign_hypotheses_covers_the_producers_benign_vocabulary():
    assert "BENIGN" in BENIGN_HYPOTHESES
    assert "NO_ANOMALY_DETECTED" in BENIGN_HYPOTHESES
    assert "NO_SEMIOTIC_ANOMALY_DETECTED" in BENIGN_HYPOTHESES


# ── the loop as a whole ─────────────────────────────────────────────────────

def test_reachable_maximum_is_one_and_meets_the_threshold():
    """The finding in one assertion, inverted. Stack every rule's trigger at
    once using only shapes production actually emits: exactly one contradiction
    survives, and the threshold now admits it."""
    detector = ContradictionDetector()
    module_results = {
        # Rule 4 trigger in the real vocabulary (live).
        # Rule 1 trigger in the real key shape (dormant).
        "abduction": {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED",
                      "is_conclusive": True},
        "signals": [
            {"evidence_type": "memory_process", "source": "memory_forensics",
             "z_score": 9.0, "confidence": 0.1},
        ] + [{"z_score": 4.0, "confidence": 0.1} for _ in range(9)],
    }
    # MCA passed the way the agent derives it, not an independent value.
    mca = _mca_like_agent([Fraction(1, 10)] * 10)
    found = detector.detect(module_results, mca)
    assert len(found) == 1, f"expected exactly rule 4, got {found}"
    assert found[0][0] == ["abductive_reasoner", "sift_signals"]
    assert len(found) >= CONTRADICTION_THRESHOLD, (
        f"reachable maximum ({len(found)}) fell below CONTRADICTION_THRESHOLD "
        f"({CONTRADICTION_THRESHOLD}) -- Mode-1 self-correction is inert again, "
        f"which is the B-224 regression."
    )


def test_self_correction_applies_end_to_end():
    """Beyond detect(): the correction actually reaches the verdict. This is the
    assertion that would have failed for every possible input before B-224."""
    agent = VIGIAAgent(case_id="B224-REACHABILITY",
                       evidence_path=str(REPO / "cases/input/VIGIA-REAL-007.json"))
    results = {
        "abduction": {"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED",
                      "is_conclusive": True},
        "signals": [{"evidence_type": "memory_process", "source": "sift_volatility",
                     "z_score": 5.0, "confidence": 0.9},
                    {"evidence_type": "network_flow", "source": "sift_netflow",
                     "z_score": 4.0, "confidence": 0.9}],
    }
    had_corrections, updated = agent._detect_and_correct(results)
    assert had_corrections is True
    assert len(agent.corrections_applied) == 1
    verdict = updated["abduction"]["best_hypothesis"]
    assert verdict.startswith("MALICIOUS_INTENT_SUSPECTED"), verdict
    assert updated["abduction"]["override_applied"] is True


def test_dormant_rules_are_reported_not_silently_skipped():
    """Honest degradation: "no contradictions" must be distinguishable from
    "three rules could not be evaluated"."""
    detector = ContradictionDetector()
    detector.detect(
        {"abduction": {}, "signals": [{"evidence_type": "log_entry", "z_score": 1.0}]},
        Fraction(1, 2),
    )
    reported = " ".join(detector.last_dormant_rules)
    assert "ENTROPY_VS_BEHAVIORAL" in reported
    assert "SEMIOTIC_VS_TECHNICAL" in reported


def test_threshold_is_one():
    """Pinned so the coupled decision cannot drift back silently: at 2, the
    reachable maximum of 1 can never satisfy it and the loop is inert again."""
    assert CONTRADICTION_THRESHOLD == 1
