"""Dispatch and shared Markdown blocks for the audience reports.

``render(view, audience, lang)`` is a pure function of the bundle bytes behind
``view``: no clock, no filesystem, no randomness, no dict-order dependence
beyond the bundle's own (JSON object order is preserved by ``json.loads`` and is
part of the bytes). Same bundle, same audience, same language -> same bytes.
"""

from __future__ import annotations

from typing import Iterable, Optional

from vigia.report import AUDIENCES, LANGS, REPORT_VERSION
from vigia.report.adapter import BundleView
from vigia.report.glossary import GlossaryCollector
from vigia.report.strings import t
from vigia.ui.normalizer import (
    SCHEMA_AGENT_AUDIT,
    SCHEMA_EBS_V1,
    SCHEMA_MCP,
    SCHEMA_UNKNOWN,
)

SCALE: tuple[str, ...] = ("NOISE", "SUSPICION", "INTENT", "MALICE", "ABSTAIN")
EXIT_LABEL = "ERROR"


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def cell(text: Optional[str]) -> str:
    """One table cell: pipes escaped, newlines collapsed, None -> empty."""
    if text is None:
        return ""
    return str(text).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def code(text: Optional[str]) -> str:
    """Inline code span that survives backticks inside the text."""
    if text is None:
        return ""
    s = str(text)
    if s == "":
        return '`""`'  # a sealed empty string is a value, not a gap
    if "`" not in s:
        return f"`{s}`"
    fence = "`" * (max(len(run) for run in s.split("`")[:-1] or [""]) + 1)
    return f"{fence} {s} {fence}"


def fenced(text: Optional[str]) -> list[str]:
    """Fenced block whose fence is longer than any backtick run in ``text``."""
    s = "" if text is None else str(text)
    longest = 0
    run = 0
    for ch in s:
        run = run + 1 if ch == "`" else 0
        longest = max(longest, run)
    fence = "`" * max(3, longest + 1)
    return [f"{fence}text", s, fence]


def table(headers: Iterable[str], rows: Iterable[Iterable[Optional[str]]]) -> list[str]:
    hdr = [cell(h) for h in headers]
    out = ["| " + " | ".join(hdr) + " |", "|" + "|".join(" --- " for _ in hdr) + "|"]
    for row in rows:
        out.append("| " + " | ".join(cell(c) for c in row) + " |")
    return out


def gap(lang: str, value: Optional[str], key: str = "gap.absent") -> str:
    """The value, or the localized gap marker in italics."""
    return value if value is not None else f"*{t(lang, key)}*"


def join_blocks(blocks: Iterable[str | list[str]]) -> str:
    """Join paragraphs / line-lists with blank lines; single trailing newline."""
    parts: list[str] = []
    for b in blocks:
        if isinstance(b, list):
            if b:
                parts.append("\n".join(b))
        elif b:
            parts.append(b)
    return "\n\n".join(parts).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Shared sections
# ---------------------------------------------------------------------------

def header(view: BundleView, audience: str, lang: str, gl: GlossaryCollector) -> list[str | list[str]]:
    gl.mark(view.schema)
    title_key = "doc.title_junior" if audience == "junior" else "doc.title_expert"
    meta = table(
        (t(lang, "custody.col_field"), t(lang, "header.col_value")),
        [
            (t(lang, "header.case"), code(view.case_id) if view.case_id else gap(lang, None)),
            (t(lang, "header.schema"), code(view.schema)),
            (t(lang, "header.source"), code(view.source_name) if view.source_name else gap(lang, None)),
            (t(lang, "header.source_sha256"), code(view.source_sha256)),
            (t(lang, "header.audience"), t(lang, f"audience.{audience}")),
            (t(lang, "header.report_version"), code(REPORT_VERSION)),
        ],
    )
    return [
        f"# {t(lang, title_key)}",
        meta,
        f"> {t(lang, 'header.disclaimer')}",
        f"> {t(lang, 'header.verbatim_note')}",
        t(lang, f"schema.{view.schema}"),
    ]


def footer(view: BundleView, lang: str) -> list[str | list[str]]:
    return ["---", t(lang, "footer.note", version=REPORT_VERSION, sha256=view.source_sha256)]


def verify_section(view: BundleView, lang: str, number: int) -> list[str | list[str]]:
    name = view.source_name or "<bundle.json>"
    blocks: list[str | list[str]] = [f"## {number}. {t(lang, 'section.verify')}", t(lang, "verify.intro")]
    if view.schema == SCHEMA_EBS_V1:
        blocks.append(t(lang, "verify.ebs", name=name))
    elif view.schema == SCHEMA_AGENT_AUDIT:
        blocks.append(t(lang, "verify.agent", name=name))
    elif view.schema == SCHEMA_MCP:
        blocks.append(t(lang, "verify.mcp", name=name))
    else:
        blocks.append(t(lang, "verify.unknown"))
    if view.schema != SCHEMA_UNKNOWN:
        blocks.append(t(lang, "verify.family_note"))
    return blocks


def glossary_section(gl: GlossaryCollector, lang: str, number: int) -> list[str | list[str]]:
    rows = gl.rows(lang)
    blocks: list[str | list[str]] = [f"## {number}. {t(lang, 'section.glossary')}", t(lang, "glossary.intro")]
    if rows:
        blocks.append([f"- {code(term)}: {text}" for term, text in rows])
    return blocks


def gaps_block(view: BundleView, lang: str, limitations: list[str]) -> list[str | list[str]]:
    blocks: list[str | list[str]] = []
    if view.gaps:
        blocks.append(f"**{t(lang, 'junior.s8.reader_gaps')}**")
        blocks.append([f"- {g}" for g in view.gaps])
    else:
        blocks.append(t(lang, "junior.s8.none"))
    if limitations:
        blocks.append(f"**{t(lang, 'junior.s8.bundle_limitations')}**")
        blocks.append([f"- {x}" for x in limitations])
    return blocks


def on_scale_verdicts(entries: list[dict]) -> list[str]:
    """Distinct verdict tokens that are on the five-rung scale, in bundle order."""
    seen: list[str] = []
    for e in entries:
        v = e.get("verdict")
        if isinstance(v, str) and v in SCALE and v not in seen:
            seen.append(v)
    return seen


def unknown_document(view: BundleView, audience: str, lang: str) -> str:
    gl = GlossaryCollector()
    blocks = header(view, audience, lang, gl)
    blocks.append(t(lang, "unknown.body"))
    blocks.extend(verify_section(view, lang, 1))
    blocks.extend(glossary_section(gl, lang, 2))
    blocks.extend(footer(view, lang))
    return join_blocks(blocks)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def render(view: BundleView, audience: str, lang: str) -> str:
    if audience not in AUDIENCES:
        raise ValueError(f"unknown audience {audience!r}; expected one of {AUDIENCES}")
    if lang not in LANGS:
        raise ValueError(f"unknown language {lang!r}; expected one of {LANGS}")
    if view.schema == SCHEMA_UNKNOWN:
        return unknown_document(view, audience, lang)
    # Local imports keep the module graph acyclic (renderers import this module).
    if audience == "junior":
        from vigia.report.render_junior import render_junior
        return render_junior(view, lang)
    from vigia.report.render_expert import render_expert
    return render_expert(view, lang)


__all__ = [
    "SCALE", "EXIT_LABEL", "cell", "code", "fenced", "table", "gap", "join_blocks",
    "header", "footer", "verify_section", "glossary_section", "gaps_block",
    "on_scale_verdicts", "unknown_document", "render",
]
