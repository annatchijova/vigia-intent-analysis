"""Rendered reports pass the repository's narrative injection auditor.

vigia.core.narrative_auditor.NarrativeAuditor is the independent validator the
pipeline runs on generated prose before sealing. The audience reports are not
sealed, but they are prose a human will read next to a verdict, so the same
gate applies. Audited here at test time only: the auditor pulls in the
security audit logger, which the renderer itself must never import.

Corpus renders are audited too, in permissive mode: a threat there would come
from sealed bundle content quoted verbatim (a real finding about that bundle,
not about the renderer), so it is reported, not asserted away.
"""
from __future__ import annotations

import json
import os

import pytest

from tests.test_report_adapter import make_mcp_doc_kiwi
from tests.test_webui_normalizer import make_agent_doc, make_ebs_doc, make_mcp_doc_nested
from vigia.core.narrative_auditor import NarrativeAuditor
from vigia.report.adapter import load_view
from vigia.report.glossary import GLOSSARY
from vigia.report.renderers import render
from vigia.report.strings import STRINGS

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _audit(text: str, case_id: str):
    return NarrativeAuditor(strict_mode=True).audit(text.splitlines(), case_id, source_agent="vigia.report")


@pytest.mark.parametrize("factory", [make_ebs_doc, make_agent_doc, make_mcp_doc_nested, make_mcp_doc_kiwi])
@pytest.mark.parametrize("audience", ["junior", "expert"])
@pytest.mark.parametrize("lang", ["en", "es"])
def test_fixture_renders_are_clean(factory, audience, lang):
    view = load_view(json.dumps(factory()).encode(), "fixture.json")
    result = _audit(render(view, audience, lang), view.case_id or "fixture")
    assert result.is_clean, [t.pattern_type for t in result.threats_detected]


def test_static_text_is_clean():
    lines = []
    for table in STRINGS.values():
        lines.extend(table.values())
    for entry in GLOSSARY.values():
        lines.extend([entry.en, entry.es])
    result = NarrativeAuditor(strict_mode=True).audit(lines, "static", source_agent="vigia.report")
    assert result.is_clean, [(t.pattern_type, t.line_index) for t in result.threats_detected]
