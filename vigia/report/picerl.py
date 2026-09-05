"""SANS PICERL phase table for the audience reports.

The canonical enumeration is ``vigia.sift.sans_phase.SANSPhase``. It is not
imported here on purpose: ``vigia/sift/__init__.py`` eagerly loads every SIFT
engine (and prints dependency warnings), which a stdlib-only viewer must not
drag in. The labels below reproduce ``SANSPhase.label`` exactly and
``tests/test_report_glossary_coverage.py`` asserts they stay in lockstep.
The bilingual one-liners live in ``vigia.report.strings`` under
``picerl.<phase>``.
"""

from __future__ import annotations

from vigia.report.strings import t

# (string key suffix, label as SANSPhase.label renders it)
PHASES: tuple[tuple[str, str], ...] = (
    ("preparation", "Preparation [1/6]"),
    ("identification", "Identification [2/6]"),
    ("containment", "Containment [3/6]"),
    ("eradication", "Eradication [4/6]"),
    ("recovery", "Recovery [5/6]"),
    ("lessons_learned", "Lessons Learned [6/6]"),
)


def phase_rows(lang: str) -> list[tuple[str, str]]:
    """``(label, localized one-line description)`` for the six phases, in order."""
    return [(label, t(lang, f"picerl.{key}")) for key, label in PHASES]


__all__ = ["PHASES", "phase_rows"]
