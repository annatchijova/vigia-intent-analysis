"""
Semantic lint — a sealed fracture theory must not contradict the case's own
declared ground truth.

Ref: docs/M2_DISCRIMINATORS_DESIGN_20260711.md section 2.4. This converts the
FOSSIL HUNT's strongest signal (a fracture whose interpretation asserts the
inverse of the case's peirce_chain/notes — MAGNET-2020, FN-001, the A-group)
into a permanent corpus-wide regression: for every case in the canonical
corpus directories, no emitted fracture may assert an evidence-PLANTING
theory when the case's own thirdness declares the signal as a genuine trace
that betrays/attributes the actor.

Deterministic and text-based on purpose: it lints the sealed narrative layer,
which is what a cross-examination reads.
"""

import json
import logging
from pathlib import Path

import pytest

logging.disable(logging.CRITICAL)

REPO = Path(__file__).resolve().parents[1]

CASES_DIRS = [
    REPO / "data/cases",
    REPO / "data/cases/converted",
    REPO / "data/cases/benign",
    REPO / "data/cases/consolidated_canonical",
    REPO / "data/cases/legacy",
]

# A fracture asserting any of these seals a planting/misdirection theory.
PLANTING_MARKERS = (
    "planted", "plant the", "mislead attribution", "misdirect attribution",
    "false-flag", "false flag", "fabricated retroactively",
    "planted retroactively",
)

# A case whose own declared theory says the signal is genuine attribution.
GENUINE_TRUTH_MARKERS = (
    "betray", "betrays", "delata", "delatan", "reveals native",
    "reveals idiomatic", "destroys the identity alibi", "muscle memory",
    "memoria muscular", "genuine", "not planted bait", "native configuration",
)


def _iter_cases():
    seen = set()
    for d in CASES_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            if p.stem in seen:
                continue
            seen.add(p.stem)
            try:
                case = json.loads(p.read_text())
            except Exception:
                continue
            if isinstance(case, dict) and isinstance(case.get("artifacts"), list):
                yield p, case


def _declared_truth(case: dict) -> str:
    chain = case.get("peirce_chain") or {}
    parts = [
        str(chain.get("thirdness", "")),
        str(chain.get("secondness", "")),
        str(case.get("notes", "")),
        str(case.get("description", "")),
        str(case.get("devil_advocate", "")),
    ]
    return " ".join(parts).lower()


def _sealed_fracture_texts(case: dict):
    # Live engine, exactly what the sealed bundle would carry (B-094 exposes
    # caie_fracture_details into the sealed narrative).
    from vigia_scorer import _vigia_score
    result = _vigia_score(json.loads(json.dumps(case)))
    for f in result.get("caie_fracture_details", []):
        yield (str(f.get("fracture_type", "")),
               str(f.get("interpretation", "")).lower())


ALL_CASES = list(_iter_cases())


def test_corpus_is_visible():
    assert len(ALL_CASES) > 150


@pytest.mark.parametrize(
    "path,case", ALL_CASES, ids=[c.get("case_id", p.stem) for p, c in ALL_CASES])
def test_no_planting_theory_on_genuine_attribution_case(path, case):
    truth = _declared_truth(case)
    truth_is_genuine = any(m in truth for m in GENUINE_TRUTH_MARKERS)
    if not truth_is_genuine:
        pytest.skip("case does not declare a genuine-attribution ground truth")
    offenders = [
        (ftype, interp)
        for ftype, interp in _sealed_fracture_texts(case)
        if any(m in interp for m in PLANTING_MARKERS)
    ]
    assert not offenders, (
        f"{path.name}: the case's own declared theory marks the signal as "
        f"GENUINE attribution, but the engine seals a planting/misdirection "
        f"theory: {[(t, i[:120]) for t, i in offenders]}"
    )
