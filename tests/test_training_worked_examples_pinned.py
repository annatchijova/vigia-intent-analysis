"""docs/training/examples/*.md are generated, not hand-written — and pinned.

Each example is the renderer's output for a real sealed bundle under
results/. This test regenerates every example from its source bundle and
compares bytes, so the training material can never drift from what the
renderer actually produces.

When a renderer or string-table change is intentional, regenerate the
examples and commit them together with the change:

    for spec in "results/agent_batch/FF-GENUINE-001_agent_bundle.json junior en" \
                "results/kiwi/VIGIA-KIWI-006_bundle.json junior es" \
                "results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json expert en" \
                "results/kiwi/VIGIA-KIWI-006_bundle.json expert es"; do
      set -- $spec
      python3 -m vigia.report "$1" --audience $2 --lang $3 --output-dir docs/training/examples
    done

The diff of the regenerated files is the review artifact for that change.
"""
from __future__ import annotations

import os

import pytest

from vigia.report.adapter import load_view
from vigia.report.renderers import render
from vigia.report.writer import sibling_path

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(REPO, "docs", "training", "examples")

# (source bundle, audience, lang)
SPECS = [
    ("results/agent_batch/FF-GENUINE-001_agent_bundle.json", "junior", "en"),
    ("results/kiwi/VIGIA-KIWI-006_bundle.json", "junior", "es"),
    ("results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json", "expert", "en"),
    ("results/kiwi/VIGIA-KIWI-006_bundle.json", "expert", "es"),
]


@pytest.mark.parametrize("source,audience,lang", SPECS,
                         ids=[f"{os.path.basename(s)}:{a}:{l}" for s, a, l in SPECS])
def test_worked_example_matches_renderer(source, audience, lang):
    bundle_path = os.path.join(REPO, source)
    if not os.path.isfile(bundle_path):
        pytest.skip(f"source bundle missing: {source}")
    example = sibling_path(bundle_path, audience, lang, output_dir=EXAMPLES)
    assert os.path.isfile(example), f"missing worked example {os.path.relpath(example, REPO)}"

    view = load_view(open(bundle_path, "rb").read(), source_name=os.path.basename(bundle_path))
    expected = render(view, audience, lang)
    actual = open(example, encoding="utf-8", newline="").read()
    assert actual == expected, (
        f"{os.path.relpath(example, REPO)} is stale; regenerate it (see module docstring)"
    )


def test_examples_directory_has_no_strays():
    """Every file in examples/ must be one of the pinned specs."""
    expected = {os.path.basename(sibling_path(os.path.join(REPO, s), a, l, output_dir=EXAMPLES))
                for s, a, l in SPECS}
    present = {n for n in os.listdir(EXAMPLES) if n.endswith(".md")}
    assert present == expected, f"unpinned examples: {sorted(present - expected)}; missing: {sorted(expected - present)}"


def test_examples_cover_three_families_and_both_languages():
    families = set()
    langs = set()
    for s, a, l in SPECS:
        p = os.path.join(REPO, s)
        if os.path.isfile(p):
            families.add(load_view(open(p, "rb").read()).schema)
        langs.add(l)
    assert families == {"agent_audit", "mcp_investigation", "ebs_v1"}
    assert langs == {"en", "es"}
