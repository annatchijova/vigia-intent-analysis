"""The documented full-suite command must still collect in a minimal CI env.

Companion to ``tests/test_requirements_ci_contract.py``.  That test enforces
the *forward* half of the dependency contract: every third-party import
reachable from the suite is covered by ``requirements-ci.txt``, with ``mcp``
as the single allowlisted gap (KNOWN_LIMITATIONS.md L-045).

This test enforces the half that was missing: an *allowlisted* gap must
degrade honestly.  A test module that cannot import ``mcp`` has to SKIP, not
raise at import time -- because a collection error is not a skip.  pytest
aborts the whole session on collection errors ("Interrupted: N errors during
collection"), so a handful of unguarded modules take the entire suite down
with them and zero tests run.

Measured on 2026-08-12, before the guards were restored: in an environment
built from ``requirements-ci.txt`` alone, the authoritative command from
CLAUDE.md ::

    pytest tests/ vigia/tests/ --ignore=tests/integration

collected 4 errors and executed **no tests at all**.  The convention that
prevents this already existed and was applied in three sibling modules
(``test_mount_magic_bytes.py``, ``test_mcp_confused_deputy.py``,
``vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py``); four
later modules that import the bridge simply did not carry it.  This is the
same drift class ``test_requirements_ci_contract.py`` was written to close,
one layer down.

The property is checked empirically rather than syntactically: a child
interpreter runs the real collection with ``mcp`` forced unimportable.  That
makes the test environment-independent -- it holds whether or not ``mcp``
happens to be installed on the machine running it -- and it pins the outcome
that actually matters instead of a proxy for it (a module could satisfy any
"has an importorskip line" grep and still fail to collect).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Distributions that ``test_requirements_ci_contract.KNOWN_CI_GAPS`` allows to
# be absent from a minimal CI environment and that the suite imports at module
# scope. Blocking them reproduces that environment exactly.
BLOCKED_DISTRIBUTIONS = ("mcp",)

# Mirrors the authoritative full-suite invocation documented in CLAUDE.md.
COLLECT_ARGS = [
    "tests/",
    "vigia/tests/",
    "--ignore=tests/integration",
    "--collect-only",
    "-q",
    "--no-cov",
    "-p",
    "no:cacheprovider",
]

_CHILD = """
import sys

BLOCKED = {blocked!r}


class _BlockedFinder:
    def find_spec(self, fullname, path=None, target=None):
        root = fullname.split(".")[0]
        if root in BLOCKED:
            raise ModuleNotFoundError(
                "No module named %r" % fullname, name=fullname
            )
        return None


for name in list(sys.modules):
    if name.split(".")[0] in BLOCKED:
        del sys.modules[name]

sys.meta_path.insert(0, _BlockedFinder())

import pytest

sys.exit(pytest.main({args!r}))
"""


def _collect_with_blocked_imports() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", _CHILD.format(blocked=BLOCKED_DISTRIBUTIONS, args=COLLECT_ARGS)],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
        timeout=900,
    )


def test_full_suite_collects_when_allowlisted_gaps_are_absent() -> None:
    completed = _collect_with_blocked_imports()
    combined = completed.stdout + completed.stderr

    assert "errors during collection" not in combined, combined[-4000:]
    assert "error" not in combined.splitlines()[-1].lower(), combined[-4000:]
    assert completed.returncode == 0, combined[-4000:]


def test_blocking_actually_takes_effect() -> None:
    """Control: the blocker must really make the distributions unimportable.

    Without this, a silently ineffective blocker would make the test above
    pass for the wrong reason on any machine where ``mcp`` is installed.
    """
    prelude, _, _ = _CHILD.format(
        blocked=BLOCKED_DISTRIBUTIONS, args=[]
    ).partition("import pytest")

    for distribution in BLOCKED_DISTRIBUTIONS:
        probe = subprocess.run(
            [sys.executable, "-c", prelude + f"import {distribution}"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )

        assert probe.returncode != 0, distribution
        assert "ModuleNotFoundError" in probe.stderr, probe.stderr
