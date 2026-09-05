"""vigia.report must stay strictly downstream of the sealed verdict path.

Same mechanism as tests/test_epistemic_kernel.py::
test_kernel_is_not_imported_by_the_scoring_pipeline: a ``git grep`` over
production code for any import of the presentation package. The only permitted
importer is ``vigia_agent.py``, whose opt-in hook imports it lazily AFTER the
bundle and its .sha256 sidecar are written (post-seal, fail-soft). Anything
else importing it, above all a scoring module, is an architectural change that
needs deliberate review, not a silent one.

Companion check: importing the package must not pull in the web framework or
the eager SIFT engine package (``vigia/sift/__init__.py`` loads every engine),
so the renderer stays a stdlib-only viewer.
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_IMPORTERS = {"vigia_agent.py"}


def test_report_package_is_not_imported_by_production_code():
    out = subprocess.run(
        ["git", "grep", "-l", "-E",
         r"vigia\.report|from vigia import report",
         "--",
         "vigia/", "*.py",
         ":(exclude)tests/", ":(exclude)vigia/tests/", ":(exclude)vigia/report/"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert out.returncode in (0, 1), out.stderr
    importers = {line for line in out.stdout.splitlines() if line}
    unexpected = importers - ALLOWED_IMPORTERS
    assert not unexpected, f"vigia.report reached production code via: {sorted(unexpected)}"


def test_scoring_modules_do_not_import_report():
    sealed = [
        "vigia_scorer.py", "vigia/tools/caie.py", "vigia/collapse_decision.py",
        "vigia/core/decision_layer.py", "vigia/core/evidence_aggregator.py",
        "vigia/core/likelihood_engine.py", "vigia/core/causal_closure.py",
        "vigia/core/semiotic_detector_v2.py", "vigia/core/bundle_builder.py",
    ]
    for rel in sealed:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            assert "vigia.report" not in fh.read(), rel


def test_import_is_stdlib_clean_in_a_fresh_interpreter():
    code = (
        "import sys\n"
        f"sys.path.insert(0, {REPO!r})\n"
        "import vigia.report, vigia.report.adapter, vigia.report.strings\n"
        "import vigia.report.glossary, vigia.report.picerl, vigia.report.mitre\n"
        "roots = sorted({m.split('.')[0] for m in sys.modules})\n"
        "vig = sorted(m for m in sys.modules if m.startswith('vigia'))\n"
        "print('ROOTS:' + ','.join(roots))\n"
        "print('VIGIA:' + ','.join(vig))\n"
    )
    out = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True, text=True, cwd=REPO,
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )
    assert out.returncode == 0, out.stderr[-2000:]
    roots = set(next(l for l in out.stdout.splitlines() if l.startswith("ROOTS:"))[6:].split(","))
    vig = set(next(l for l in out.stdout.splitlines() if l.startswith("VIGIA:"))[6:].split(","))
    for heavy in ("fastapi", "uvicorn", "numpy", "scipy", "pydantic", "reportlab",
                  "matplotlib", "anthropic", "requests", "httpx"):
        assert heavy not in roots, f"{heavy} imported by vigia.report"
    assert not any(m.startswith("vigia.sift") for m in vig), "eager SIFT package imported"
    assert not any(m.startswith("vigia.security") for m in vig), (
        "audit logger imported at module load (must stay lazy in vigia.report.mitre)"
    )
