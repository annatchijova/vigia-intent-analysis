"""
vigia/verdict/quadripartite.py -- QuadripartiteClassifier's Check 6
(BENIGN by confidence level) applies a +5% effective-confidence bonus when
adversarial_penalty=True (the system evaluated and discarded the
"too simple" hypothesis per vigia/core/ockham_adversarial.py). This is a
live, correctly-implemented branch with its own logic -- not a bug in
quadripartite.py itself.

The bug (documented as an addendum to B-124 in BUGS_PENDIENTES.md /
BUGS_PENDIENTES_EN.md, discovered as a follow-up to F1/B-217) is one level
up: vigia_scorer.py's _apply_quadripartite (the sole production call site of
QuadripartiteClassifier.classify()) hardcodes adversarial_penalty=False as a
bare literal -- not derived from any computation -- because
ockham_adversarial.py has zero callers anywhere in the repository (confirmed
by exhaustive grep, including tests). So the True branch below is reachable
in the code but unreachable in practice from the live pipeline.

This test locks in the concrete, state-changing consequence: the +5% bonus
is large enough to cross the HIGH/MEDIUM threshold (80%) on its own, so this
isn't a cosmetic gap -- BENIGN cases sitting just under 80% confidence are
classified BENIGN_MEDIUM today and would be BENIGN_HIGH if ockham were wired
and had fired. Not a regression test for a fix (no fix applied here) --
a regression test for the DIAGNOSIS, so if adversarial_penalty ever gets
wired to a real value, this test's "unreachable" half should start failing
and prompt an update.
"""

from __future__ import annotations

from fractions import Fraction

from vigia.verdict.quadripartite import QuadripartiteClassifier, VerdictState


class TestAdversarialPenaltyCrossesConfidenceThreshold:
    def test_penalty_false_stays_benign_medium_at_78_percent(self):
        c = QuadripartiteClassifier()
        v = c.classify(
            raw_verdict="BENIGN", confidence=Fraction(78, 100),
            stability=Fraction(1, 1), integrity_level="FULL_INTEGRITY",
            adversarial_penalty=False,
        )
        assert v.state == VerdictState.BENIGN_MEDIUM
        assert v.confidence == Fraction(78, 100)

    def test_penalty_true_crosses_into_benign_high_at_same_78_percent(self):
        c = QuadripartiteClassifier()
        v = c.classify(
            raw_verdict="BENIGN", confidence=Fraction(78, 100),
            stability=Fraction(1, 1), integrity_level="FULL_INTEGRITY",
            adversarial_penalty=True,
        )
        assert v.state == VerdictState.BENIGN_HIGH
        assert v.confidence == Fraction(83, 100)


class TestProductionCallSiteHardcodesPenaltyFalse:
    """Confirms the diagnosis, not just the isolated classifier behavior:
    vigia_scorer.py's only call to QuadripartiteClassifier.classify() passes
    a bare adversarial_penalty=False literal. If this ever changes (ockham
    gets wired), this test should be revisited alongside the B-124 addendum."""

    def test_apply_quadripartite_source_hardcodes_penalty_false(self):
        import inspect
        import vigia_scorer

        src = inspect.getsource(vigia_scorer._apply_quadripartite)
        assert "adversarial_penalty=False" in src, (
            "adversarial_penalty is no longer hardcoded False in "
            "_apply_quadripartite -- update the B-124 addendum in "
            "BUGS_PENDIENTES.md / BUGS_PENDIENTES_EN.md, this diagnosis "
            "may no longer hold."
        )

    def test_ockham_adversarial_has_no_callers_outside_its_own_module(self):
        """Checks actual import/usage, not bare substring matches -- test
        docstrings elsewhere in this suite legitimately discuss
        ockham_adversarial.py by name (e.g.
        test_config_sentinel_orphaned_module_env_map.py's B-124 addendum
        prose) without importing or calling it. Only a real import or
        attribute-style reference outside tests/ would mean it got wired."""
        import subprocess

        result = subprocess.run(
            [
                "grep", "-rlE",
                r"import ockham_adversarial|ockham_adversarial\.",
                "--include=*.py", ".",
            ],
            cwd=__file__.rsplit("/tests/", 1)[0],
            capture_output=True, text=True,
        )
        callers = [
            line for line in result.stdout.splitlines()
            if not line.endswith("vigia/core/ockham_adversarial.py")
            and "/tests/" not in line
        ]
        assert callers == [], (
            f"ockham_adversarial now has callers outside its own module and "
            f"outside tests/: {callers} -- the 'zero callers' premise of "
            f"this diagnosis no longer holds, update the B-124 addendum."
        )
