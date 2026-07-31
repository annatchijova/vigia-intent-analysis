"""B-224 — vigia_agent.py's own documentation must not claim its
self-correction loop is functioning when it structurally cannot fire.

Before this fix, the module docstring said "automatic re-analysis with
adjusted parameters", the class docstring said "Self-correction is
architectural" with no caveat, and --help said "Self-correction: automatic
— no flags needed" plus "Max iterations: 3 (hard cap, prevents infinite
loops)" — all describing an iterating loop. In reality
CONTRADICTION_THRESHOLD=2 gates a branch that can reach at most 1
contradiction (see tests/test_b224_contradiction_detector_dormancy.py), so
every real run completes in exactly 1 iteration and self_corrections_applied
is always 0.

This locks in the honest replacement text so a future edit doesn't quietly
restore the false "it works" framing.
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

    def test_agent_class_docstring_names_the_gap(self):
        doc = _normalize(vigia_agent.VIGIAAgent.__doc__ or "")
        assert "B-224" in doc
        assert "never actually repeats" in doc

    def test_agent_class_docstring_states_the_real_arithmetic(self):
        doc = _normalize(vigia_agent.VIGIAAgent.__doc__ or "")
        assert "CONTRADICTION_THRESHOLD" in doc
        assert "maximum reachable contradiction count is 1" in doc


class TestContradictionDetectorDocstringIsHonest:
    def test_docstring_no_longer_lists_the_unimplemented_type(self):
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        # TEMPORAL_VS_CONTENT must not be presented as an implemented rule
        # (numbered 1-5 alongside the real ones); it may still be named as
        # the thing that was never implemented.
        assert "was never implemented" in doc

    def test_docstring_names_b224_and_which_rules_are_unreachable(self):
        doc = _normalize(vigia_agent.ContradictionDetector.__doc__ or "")
        assert "B-224" in doc
        assert "unreachable" in doc


class TestHelpOutputIsHonest:
    def _help_text(self) -> str:
        result = subprocess.run(
            [sys.executable, "vigia_agent.py", "--help"],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        return result.stdout

    def test_help_does_not_claim_bare_automatic_self_correction(self):
        help_text = self._help_text()
        assert "Self-correction: automatic — no flags needed." not in help_text

    def test_help_points_at_the_known_limitation(self):
        help_text = self._help_text()
        assert "L-069" in help_text

    def test_help_max_iterations_no_longer_implies_looping_happens(self):
        help_text = self._help_text()
        assert "not reached in practice" in help_text
