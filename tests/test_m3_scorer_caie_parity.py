"""
M3 parity test — the scorer's fracture-type map must match the live CAIE
catalogue.

Ref: docs/FOSSIL_HUNT_20260711_PASS2.md §2 (M3). The fossil this prevents:
caie.py evolves its fracture catalogue while the scorer's weight map ossifies,
leaving Daubert-strong fracture types score-inert (FALSE_FLAG_ATTRIBUTION_
MISMATCH, LOG_VS_MEMORY, TIMESTAMP_PRECISION_ANOMALY weighed zero) and
phantom types classified (ATTRIBUTION_INCONSISTENCY, never generated).

Both sides are read from source because MALICIOUS_FRACTURE_TYPES and
CREDIBILITY_REDUCING_TYPES are locals of _vigia_score by design.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_FTYPE_RE = re.compile(r'fracture_type\s*=\s*"([A-Z_]+)"')
_SET_RE = {
    "malicious": re.compile(
        r"MALICIOUS_FRACTURE_TYPES\s*=\s*\{(.*?)\}", re.S),
    "credibility": re.compile(
        r"CREDIBILITY_REDUCING_TYPES\s*=\s*\{(.*?)\}", re.S),
}
_MEMBER_RE = re.compile(r'"([A-Z_]+)"')


def caie_generated_types() -> set:
    src = (REPO / "vigia" / "tools" / "caie.py").read_text()
    return set(_FTYPE_RE.findall(src))


def scorer_sets() -> dict:
    src = (REPO / "vigia_scorer.py").read_text()
    out = {}
    for name, rx in _SET_RE.items():
        m = rx.search(src)
        assert m, f"could not locate {name} set in vigia_scorer.py"
        out[name] = set(_MEMBER_RE.findall(m.group(1)))
    return out


def test_caie_catalogue_is_nonempty_and_sane():
    generated = caie_generated_types()
    assert "TEMPORAL_CAUSALITY_VIOLATION" in generated
    assert "FALSE_FLAG_PATTERN" in generated
    assert len(generated) >= 10


def test_every_generated_type_is_classified_by_scorer():
    """A CAIE-generated type unknown to the scorer is score-inert: it fires,
    is sealed into the narrative, and moves nothing. That silent gap is the
    P1-K / M3 fossil family."""
    generated = caie_generated_types()
    sets_ = scorer_sets()
    classified = sets_["malicious"] | sets_["credibility"]
    unclassified = generated - classified
    assert not unclassified, (
        f"CAIE generates fracture types the scorer does not classify "
        f"(score-inert): {sorted(unclassified)}. Add each to "
        f"MALICIOUS_FRACTURE_TYPES or CREDIBILITY_REDUCING_TYPES in "
        f"vigia_scorer.py (or, if intentionally neutral, document it here)."
    )


def test_scorer_classifies_no_phantom_types():
    """A scorer entry CAIE never generates is dead doctrine that reads as
    coverage (the pre-M3 ATTRIBUTION_INCONSISTENCY case)."""
    generated = caie_generated_types()
    sets_ = scorer_sets()
    phantoms = (sets_["malicious"] | sets_["credibility"]) - generated
    assert not phantoms, (
        f"vigia_scorer.py classifies fracture types CAIE v2.0 never "
        f"generates (phantoms): {sorted(phantoms)}"
    )


def test_no_type_in_both_buckets():
    sets_ = scorer_sets()
    both = sets_["malicious"] & sets_["credibility"]
    assert not both, f"types classified as both malicious and credibility: {sorted(both)}"
