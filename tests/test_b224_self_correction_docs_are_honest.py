"""B-224 — vigia_agent.py's own documentation must describe the
self-correction loop's real reachability, in either direction.

The first version of this test guarded against overclaiming: the docs said
"automatic re-analysis with adjusted parameters" and "Max iterations: 3"
while CONTRADICTION_THRESHOLD=2 gated a branch that could reach at most 1
contradiction, so the loop could not fire for any possible input.

The loop is now reachable (threshold lowered to 1, rule 4's vocabulary
aligned — see tests/test_b224_contradiction_detector_dormancy.py), and the
risk has inverted: the docs must no longer say the loop is inert, but they
must also not swing back to implying it routinely iterates. It does not. It
is reachable and quiet: 3 of the 4 rules are dormant, and no case in the
shipped corpus produces a contradiction, so real runs still complete in one
iteration. This locks in that specific, narrow claim.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import vigia_agent

REPO = Path(__file__).resolve().parent.parent


def _normalize(text: str) -> str:
    """Collapse whitespace/newlines so a docstring re-wrap doesn't break a
    phrase-substring check that spans a line boundary."""
    return re.sub(r"\s+", " ", text)


class TestModuleAndClassDocstringsAreHonest:
    def test_module_docstring_names_b224(self):
        src = Path(vigia_agent.__file__).read_text(encoding="utf-8")
        header = src.split('"""', 1)[0]  # module header comment block, pre-docstring
        assert "B-224" in header
        assert "L-069" in header

    def test_module_header_does_not_claim_automatic_correction(self):
        src = Path(vigia_agent.__file__).read_text(encoding="utf-8")
        header = src.split('"""', 1)[0]
        assert "automatic re-analysis with adjusted parameters" not in header

    def test_module_header_no_longer_claims_the_loop_is_inert(self):
        """The pre-B-224 framing must not survive the fix."""
        src = Path(vigia_agent.__file__).read_text(encoding="utf-8")
        header = _normalize(src.split('"""', 1)[0])
        assert "structurally inert" not in header
        assert "architecturally unreachable" not in header

    def test_agent_class_docstring_names_the_gap(self):
        doc = _normalize(vigia_agent.VIGIAAgent.__doc__ or "")
        assert "B-224" in doc
        assert "never actually repeats" not in doc, (
            "stale pre-B-224 claim: the loop is reachable now"
        )

    def test_agent_class_docstring_states_the_real_arithmetic(self):
        doc = _normalize(vigia_agent.VIGIAAgent.__doc__ or "")
        assert "CONTRADICTION_THRESHOLD" in doc
        assert "maximum reachable contradiction count is 1" in doc

    def test_agent_class_docstring_does_not_imply_routine_iteration(self):
        """Reachable is not the same as active. The corpus produces zero
        contradictions, and the docstring has to keep saying so."""
        doc = _normalize(vigia_agent.VIGIAAgent.__doc__ or "")
        assert "1 of 1" in doc


class TestContradictionDetectorDocstringIsHonest:
    def test_docstring_no_longer_lists_the_unimplemented_type(self):
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        # TEMPORAL_VS_CONTENT must not be presented as an implemented rule
        # (numbered 1-5 alongside the real ones); it may still be named as
        # the thing that was never implemented.
        assert "was never implemented" in doc

    def test_docstring_names_b224_and_which_rules_are_dormant(self):
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        assert "B-224" in doc
        assert "DORMANT" in doc

    def test_docstring_records_the_corrected_rule3_diagnosis(self):
        """B-224 originally named rule 3 as the only reachable rule. That was
        wrong, and the correction must stay visible at the code, not only in
        the bug registry."""
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        assert "CONFIDENCE_COLLAPSE" in doc
        assert "arithmetic" in doc

    def test_docstring_explains_why_rule1_was_not_simply_re_keyed(self):
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        assert "needs a producer, not a rename" in doc


class TestHelpOutputIsHonest:
    def _help_text(self) -> str:
        result = subprocess.run(
            [sys.executable, "vigia_agent.py", "--help"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        return result.stdout

    def test_help_points_at_the_known_limitation(self):
        help_text = self._help_text()
        assert "L-069" in help_text

    def test_help_states_how_many_rules_are_live(self):
        help_text = _normalize(self._help_text())
        assert "1 of the 4" in help_text

    def test_help_does_not_promise_routine_looping(self):
        """"Max iterations: 3" on its own reads as "it iterates up to 3 times"."""
        help_text = _normalize(self._help_text())
        assert "1 iteration in practice" in help_text
