"""Render every real bundle under results/ in all four variants.

Invariants checked on the corpus (agent, EBS v1, Mode 2 and unrecognized
documents alike):
  * rendering never raises, output ends with exactly one newline;
  * every verdict string the normalizer copied out of the bundle appears
    verbatim in every variant (verdicts are never translated or restated);
  * no decimal number appears in the output unless it is in the bundle bytes
    or in the static string tables: the renderer introduces no float;
  * no emoji, no absolute path the bundle did not already contain;
  * the parsed bundle dict is byte-identical before and after (mirrors
    tests/test_reasoning_trace_bundle_gate.py).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re

import pytest

from vigia.report import REPORT_VERSION
from vigia.report.adapter import load_view
from vigia.report.glossary import GLOSSARY
from vigia.report.renderers import render
from vigia.report.strings import STRINGS

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PATTERNS = (
    "results/agent_batch/*.json",
    "results/kiwi/*_bundle*.json",
    "results/srl2018/*_bundle.json",
    "results/real/*_bundle*.json",
    "results/real/bundle_*.json",
    "results/llm_mode/*.json",
)
BUNDLES = sorted({p for pat in _PATTERNS for p in glob.glob(os.path.join(REPO, pat))})

_DECIMAL = re.compile(r"\d+\.\d+")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
_ABS_PATH = re.compile(r"(?:/home/|/root/|/tmp/|/var/|/Users/|[A-Z]:\\\\)[^\s`|)]*")

VARIANTS = [(a, l) for a in ("junior", "expert") for l in ("en", "es")]


def _static_decimals() -> set[str]:
    tokens = {REPORT_VERSION}
    for table in STRINGS.values():
        for value in table.values():
            tokens.update(_DECIMAL.findall(value))
    for entry in GLOSSARY.values():
        tokens.update(_DECIMAL.findall(entry.en + entry.es))
    return tokens


STATIC_DECIMALS = _static_decimals()


def _digest(doc) -> str:
    return hashlib.sha256(
        json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()


@pytest.mark.skipif(not BUNDLES, reason="no bundles under results/")
@pytest.mark.parametrize("path", BUNDLES, ids=[os.path.relpath(p, REPO) for p in BUNDLES])
def test_render_all_variants_verbatim_and_float_free(path):
    raw = open(path, "rb").read()
    view = load_view(raw, source_name=os.path.basename(path))
    before = _digest(view.raw)
    # Bundles are written with ensure_ascii=True, so sealed text may carry
    # "\u00a7" escapes; compare against the decoded document as well as the
    # raw bytes so an escaped digit sequence is not misread as a new decimal.
    source_text = raw.decode("utf-8", errors="replace") + json.dumps(view.raw, ensure_ascii=False)

    verdicts = [v["verdict"] for v in view.normalized["verdicts"] if isinstance(v.get("verdict"), str)]
    source_decimals = set(_DECIMAL.findall(source_text))

    for audience, lang in VARIANTS:
        out = render(view, audience, lang)
        assert out.endswith("\n") and not out.endswith("\n\n"), (audience, lang)
        assert out.startswith("# "), (audience, lang)

        for v in verdicts:
            assert v in out, f"verdict {v!r} missing from {audience}/{lang}"

        introduced = {d for d in _DECIMAL.findall(out)} - source_decimals - STATIC_DECIMALS
        assert not introduced, f"renderer introduced decimals {sorted(introduced)} in {audience}/{lang}"

        assert not _EMOJI.search(out), (audience, lang)

        for m in _ABS_PATH.findall(out):
            assert m in source_text, f"absolute path {m!r} not from the bundle ({audience}/{lang})"

        # Source hash and family are always stated so a reader can bind the file.
        assert view.source_sha256 in out
        assert f"`{view.schema}`" in out

    assert _digest(view.raw) == before, "rendering mutated the parsed bundle"


def test_corpus_covers_every_family():
    families = {load_view(open(p, "rb").read()).schema for p in BUNDLES}
    assert {"agent_audit", "ebs_v1", "mcp_investigation"} <= families, families


def test_unknown_document_renders_honestly():
    view = load_view(b'{"foo": 1, "case_id": "X"}', "x.json")
    for audience, lang in VARIANTS:
        out = render(view, audience, lang)
        assert "`unknown`" in out
        assert "MALICE" not in out and "NOISE" not in out


def test_render_rejects_unknown_audience_or_lang():
    view = load_view(b'{"foo": 1}')
    with pytest.raises(ValueError):
        render(view, "manager", "en")
    with pytest.raises(ValueError):
        render(view, "junior", "fr")


def test_devil_advocate_gap_is_flagged_not_filled():
    """A sealed INTENT/MALICE without devil_advocate must be reported as a gap,
    never patched with generated prose, and the verdict must be untouched."""
    doc = {
        "case_id": "DA-GAP", "overall_verdict": "MALICE", "findings": [
            {"finding_id": "F-1", "title": "x", "verdict": "MALICE", "confidence": "HIGH",
             "status": "CONFIRMED", "firstness": "a", "secondness": "b", "thirdness": "c"},
        ], "tool_execution_log": [],
    }
    view = load_view(json.dumps(doc).encode())
    out = render(view, "expert", "en")
    assert "GAP: a verdict of MALICE is sealed but no `devil_advocate` is present" in out
    assert out.count("**MALICE**") >= 1
