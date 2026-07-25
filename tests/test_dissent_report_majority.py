"""
vigia/core/dissent_report.py -- F1 (Ronda 2 audit): BENIGN was mathematically
unreachable as a majority verdict, and the module's headline promise (docstring,
line ~7: "9 modules say BENIGN + 1 behavioral module says MALICE = escalation
required") was unenforceable in the live pipeline.

Root cause: _compute_majority() weighted votes by
`op.confidence * _SEVERITY_WEIGHT[op.verdict]`. _SEVERITY_WEIGHT is an
ALARM/severity scale (MALICIOUS=1, SUSPICIOUS=0.5, BENIGN=0, ABSTAIN=0)
correctly used elsewhere in this module to score how alarming a DISSENTING
opinion is -- reusing it for majority-vote weighting made BENIGN's vote
weight exactly 0 regardless of how many modules voted BENIGN or how
confidently. Confirmed by induction: 10 modules unanimously voting BENIGN at
90% confidence produced majority=ABSTAIN with 0% consensus (vote_counts
totalled to 0, hitting the "no votes at all" fallback), and all 10 were then
treated as dissenting from a majority that was never actually computed.

Two other confirmed, compounding facts (not fixed here, both true before
and after this fix -- included so a future reader doesn't have to
rediscover them): generate_dissent_report() has zero callers anywhere in
this repository (grep, not just tests), and its nominal downstream
consumer, QuadripartiteClassifier's "specialist dissent -> ESCALATE" check
(vigia/verdict/quadripartite.py), has exactly one production caller
(vigia_scorer.py, RiskBoundedDecisionLayer wrapper) which passes
dissent_info={} hardcoded -- so escalation_required can never reach that
check even after this fix. Wiring generate_dissent_report() into the live
pipeline is a separate follow-up; this fix only restores the module's own
internal correctness so that follow-up isn't built on a broken foundation.

Fix: weight votes by op.confidence alone (majority determination should
answer "what did modules vote for, weighted by their own confidence" --
orthogonal to how alarming that verdict is). _SEVERITY_WEIGHT's other use
(dissent_weight, line ~244) is untouched and still correct.
"""

from __future__ import annotations

from fractions import Fraction

from vigia.core.dissent_report import (
    ModuleOpinion,
    ModuleVerdict,
    generate_dissent_report,
)


def _opinion(name: str, verdict: ModuleVerdict, confidence: Fraction, **kw) -> ModuleOpinion:
    return ModuleOpinion(module_name=name, verdict=verdict, confidence=confidence,
                          reasoning=kw.pop("reasoning", "test"), **kw)


class TestUnanimousBenignResolvesToBenign:
    def test_five_unanimous_benign_votes_produce_benign_majority(self):
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.BENIGN, Fraction(8, 10))
            for i in range(5)
        ]

        report = generate_dissent_report(opinions)

        assert report.majority_verdict == ModuleVerdict.BENIGN
        assert report.display_consensus_pct() == 100
        assert report.escalation_required is False
        assert report.suspicious_consensus is False
        assert report.dissent_signals == []

    def test_benign_majority_is_not_reported_as_universal_dissent(self):
        """Before the fix, majority resolved to ABSTAIN and every BENIGN
        voter was individually recorded as a dissenting signal."""
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.BENIGN, Fraction(9, 10))
            for i in range(10)
        ]

        report = generate_dissent_report(opinions)

        assert report.majority_verdict != ModuleVerdict.ABSTAIN
        assert len(report.dissent_signals) == 0


class TestSpecialistDissentEscalation:
    """The module's headline scenario: 9 modules BENIGN + 1 hard-to-evade
    specialist MALICIOUS at high confidence -> escalation_required."""

    def test_nine_benign_plus_one_hard_to_evade_malicious_escalates(self):
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.BENIGN, Fraction(9, 10))
            for i in range(9)
        ] + [
            _opinion("SyscallTracer", ModuleVerdict.MALICIOUS, Fraction(85, 100),
                     reasoning="detected process hollowing",
                     evidence_refs=["pid=4812"])
        ]

        report = generate_dissent_report(opinions)

        assert report.escalation_required is True
        assert report.suspicious_consensus is True
        assert len(report.dissent_signals) == 1
        assert report.dissent_signals[0].dissenting_module == "SyscallTracer"
        assert report.dissent_signals[0].is_hard_to_evade is True
        assert "SUSPICIOUS CONSENSUS" in report.forensic_summary

    def test_escalation_requires_high_enough_dissent_confidence(self):
        """A low-confidence MALICIOUS dissent must not force escalation --
        the critical_dissent_threshold gate must still hold post-fix."""
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.BENIGN, Fraction(9, 10))
            for i in range(9)
        ] + [
            _opinion("SyscallTracer", ModuleVerdict.MALICIOUS, Fraction(3, 10),
                     reasoning="weak signal")
        ]

        report = generate_dissent_report(
            opinions, critical_dissent_threshold=Fraction(6, 10)
        )

        assert report.escalation_required is False


class TestGenuineMajorityUnaffected:
    """Sanity: paths that never depended on the BENIGN weighting bug must be
    unchanged."""

    def test_genuine_malicious_majority_still_resolves_correctly(self):
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.MALICIOUS, Fraction(9, 10))
            for i in range(4)
        ] + [
            _opinion("Outlier", ModuleVerdict.BENIGN, Fraction(6, 10))
        ]

        report = generate_dissent_report(opinions)

        assert report.majority_verdict == ModuleVerdict.MALICIOUS
        assert report.display_consensus_pct() == 80

    def test_all_abstain_produces_abstain_majority(self):
        opinions = [
            _opinion(f"Module{i}", ModuleVerdict.ABSTAIN, Fraction(0, 10))
            for i in range(3)
        ]

        report = generate_dissent_report(opinions)

        assert report.majority_verdict == ModuleVerdict.ABSTAIN
        assert report.display_consensus_pct() == 0

    def test_no_opinions_produces_abstain_without_crashing(self):
        report = generate_dissent_report([])

        assert report.majority_verdict == ModuleVerdict.ABSTAIN
        assert report.total_modules == 0
