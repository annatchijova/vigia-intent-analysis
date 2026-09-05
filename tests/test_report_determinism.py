"""Same bundle bytes -> same report bytes, across fresh interpreters.

Mirrors tests/test_determinism_sealed_verdict.py::
test_deterministic_across_fresh_processes: two subprocesses with different
PYTHONHASHSEED values render all four variants of one bundle per family and
print a SHA-256 per variant. Any set/dict-order leak, clock read or
environment-dependent string would show up as a hash mismatch.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys

import pytest

from vigia.report.adapter import load_view
from vigia.report.renderers import render

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _one_per_family() -> dict[str, str]:
    picks: dict[str, str] = {}
    candidates = sorted(
        glob.glob(os.path.join(REPO, "results/agent_batch/*_agent_bundle.json"))
        + glob.glob(os.path.join(REPO, "results/kiwi/*_bundle.json"))
        + glob.glob(os.path.join(REPO, "results/srl2018/*_bundle.json"))
    )
    for p in candidates:
        schema = load_view(open(p, "rb").read()).schema
        picks.setdefault(schema, p)
    return picks


PICKS = _one_per_family()

_PROBE = """
import hashlib, sys
sys.path.insert(0, {repo!r})
from vigia.report.adapter import load_view
from vigia.report.renderers import render
for path in {paths!r}:
    view = load_view(open(path, "rb").read(), source_name=path)
    for audience in ("junior", "expert"):
        for lang in ("en", "es"):
            digest = hashlib.sha256(render(view, audience, lang).encode("utf-8")).hexdigest()
            print("RESULT:" + path + ":" + audience + ":" + lang + ":" + digest)
"""


def _run(seed: str, paths: list[str]) -> list[str]:
    code = _PROBE.format(repo=REPO, paths=paths)
    env = {"PYTHONHASHSEED": seed, "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "LANG": "C" if seed == "0" else "en_US.UTF-8", "TZ": "UTC" if seed == "0" else "America/Argentina/Buenos_Aires"}
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True,
                         env=env, cwd=REPO)
    assert out.returncode == 0, f"probe failed (seed={seed}): {out.stderr[-3000:]}"
    lines = [ln for ln in out.stdout.splitlines() if ln.startswith("RESULT:")]
    assert len(lines) == 4 * len(paths), out.stdout[-2000:]
    return lines


@pytest.mark.skipif(len(PICKS) < 3, reason="need one real bundle per family under results/")
def test_render_is_byte_identical_across_fresh_processes():
    paths = [PICKS[k] for k in sorted(PICKS)]
    assert _run("0", paths) == _run("1", paths)


@pytest.mark.skipif(not PICKS, reason="no bundles under results/")
def test_render_is_idempotent_in_process():
    for path in PICKS.values():
        raw = open(path, "rb").read()
        a = render(load_view(raw, "x.json"), "expert", "es")
        b = render(load_view(raw, "x.json"), "expert", "es")
        assert a == b


def test_no_clock_or_random_in_report_package():
    """The renderer must not read time or randomness; grep the package source."""
    pkg = os.path.join(REPO, "vigia", "report")
    for name in sorted(os.listdir(pkg)):
        if not name.endswith(".py"):
            continue
        src = open(os.path.join(pkg, name), encoding="utf-8").read()
        for forbidden in ("import time", "import datetime", "from datetime", "import random",
                          "datetime.now", "time.time(", "uuid4"):
            assert forbidden not in src, f"{name} uses {forbidden!r}"
