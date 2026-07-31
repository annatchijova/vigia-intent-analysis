"""
B-117 fixed an inverted risk formula in risk_bounded_layer.py on 2026-07-14
(r used (1-P) instead of P, which inverted verdicts: a fabricated case
scored low risk, a genuine one scored high risk). The live implementation
has been correct since that fix, but the STALE formula string kept
resurfacing in comments, docstrings, and narrative-generation code across
the repo -- found 2026-07-26 while resolving B-214, in 9 separate
locations across both code and docs:

  vigia/pipeline/pipeline.py (two separate docstrings: module header and
    run_full()), vigia/models/ebs.py, VIGIA_ESTADO_TECNICO_ES.md and its
  docs/ mirror, docs/VIGIA_TECHNICAL_STATE_EN.md,
  docs/vigia_paper_methodology.md (diagram + prose explanation -- which
  also had the formula's *meaning* backwards: "r=0 when P=1, certain
  fabrication" is the exact inverted-decision bug B-117 fixed, stated as
  if it were the intended design), docs/vigia-real-006_execution_summary.md
  (a worked example whose own shown arithmetic, r=0.1734, already
  contradicted its own displayed threshold check and final decision --
  fixed by recomputing with the correct formula, which resolves that
  internal contradiction too), forensics/evidence_narrative_gen.py (a
  narrative-generation label shown next to the REAL, correctly-computed
  risk score -- an examiner reading the generated narrative and trying to
  reproduce the number by hand from the stated formula would get the wrong
  answer).

One occurrence needed its own investigation before touching (B-223,
2026-07-26): vigia/scripts/generate_execution_log.py:227 passed this
formula string (plus fabricated placeholder D/S/I values) to a
RISK_CALCULATION log entry, but the script actually calls
vigia.core.decision_layer.decide() -- an entirely different,
MI-threshold-based decision engine that has no P/D/S/I risk formula at
all. That was a deeper "wrong subsystem describing itself" problem, not a
simple stale-string fix. Resolved 2026-07-31: the script now logs via
VigiaExecutionLogger.log_mi_decision() (event_type MI_DECISION), which
records only what decision_layer.decide() actually computes -- mi,
alert_level, the real DEFAULT_LOW/MEDIUM/HIGH thresholds, and the engine's
own reason string -- with no D/S/I fabrication and no risk_bounded_layer
formula string. log_risk_calculation() (the P/D/S/I, risk_bounded_layer-
shaped method) is untouched and still available for its real caller.

This test sweeps the whole repo (excluding generated/vendored corpora) for
the exact inverted substring and fails if it reappears anywhere outside the
one documented, deliberately-unfixed exception and this test's own
docstring.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

STALE_FORMULA = "(1-P)·(1+λD)"  # "(1-P)·(1+λD)"

# Paths that are allowed to contain the stale string, with the reason why.
ALLOWED = {
    "tests/test_b117_stale_formula_sweep.py": "this test's own docstring names the exact string it looks for",
    "tests/test_b214_run_full_docstring_warning.py": (
        "asserts the string is ABSENT (`assert ... not in doc`) -- the "
        "literal substring appears in the test source as part of that "
        "negative assertion, not as a live claim"
    ),
    "BUGS_HISTORICO.md": "documents the historical bug and this sweep's fix -- quotes the stale formula as what was wrong, not a live claim",
    "BUGS_HISTORICO_EN.md": "documents the historical bug and this sweep's fix -- quotes the stale formula as what was wrong, not a live claim",
    "BUGS_PENDIENTES.md": "B-223 entry quotes generate_execution_log.py's own stale formula string as evidence of the bug being described, not a live claim",
    "BUGS_PENDIENTES_EN.md": "B-223 entry quotes generate_execution_log.py's own stale formula string as evidence of the bug being described, not a live claim",
    "tests/test_b223_mi_decision_no_fabricated_dsi.py": "module docstring quotes the pre-fix stale formula string as historical evidence of the fixed defect, not a live claim",
}


def test_no_stale_inverted_formula_outside_the_one_documented_exception():
    result = subprocess.run(
        ["grep", "-rl", STALE_FORMULA,
         "--include=*.py", "--include=*.md",
         "--exclude-dir=docs_merged", "--exclude-dir=academic",
         "."],
        cwd=REPO, capture_output=True, text=True,
    )
    hits = {line.lstrip("./") for line in result.stdout.splitlines() if line}
    unexpected = hits - set(ALLOWED)
    assert not unexpected, (
        f"Stale pre-B-117 inverted formula '(1-P)·(1+λD)' found in "
        f"files not covered by the B-117 sweep: {sorted(unexpected)} -- fix "
        f"it there (r = P·(...), not (1-P)·(...)), or add it to "
        f"ALLOWED with a reason if it's a new instance of the documented "
        f"generate_execution_log.py exception."
    )
