"""Expert forensic examiner view of a sealed bundle.

Custody anchors with explicit absences, every verdict-bearing field with its
JSON pointer, Peircean triads verbatim, exact sealed literals (Fractions as
N/D, floats as their own JSON text), gate / refutation / devil_advocate
records, the execution record summarized with sorted histograms, independent
verification commands, known limitations and a field-name glossary.
"""

from __future__ import annotations

from vigia.report import adapter
from vigia.report.adapter import TOOL_LOG_LISTING_CAP, BundleView, render_scalar
from vigia.report.glossary import GlossaryCollector
from vigia.report.renderers import (
    code,
    fenced,
    footer,
    gap,
    gaps_block,
    glossary_section,
    header,
    join_blocks,
    on_scale_verdicts,
    table,
    verify_section,
)
from vigia.report.strings import t
from vigia.ui.normalizer import SCHEMA_AGENT_AUDIT, SCHEMA_EBS_V1, SCHEMA_MCP

Blocks = list


def _s1_custody(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'expert.s1.title')}", t(lang, "expert.s1.intro")]
    rows = []
    for name, value in adapter.custody_fields(view):
        gl.mark(name.split(".")[-1])
        rows.append((code(name), code(value) if value is not None else gap(lang, None)))
    blocks.append(table((t(lang, "custody.col_field"), t(lang, "custody.col_value")), rows))
    if view.schema == SCHEMA_AGENT_AUDIT:
        blocks.append(t(lang, "expert.s1.sidecar_note"))
    blocks.append(t(lang, "gap.hash_note"))
    return blocks


def _s2_verdicts(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'expert.s2.title')}"]
    entries = adapter.verdict_entries(view)
    if not entries:
        blocks.append(t(lang, "expert.s2.none"))
        return blocks
    rows = []
    for e in entries:
        gl.mark_verdict(e.get("verdict"))
        field = str(e.get("source", "")).split(" ")[0]
        gl.mark(field)
        rows.append((code(field), f"**{render_scalar(e.get('verdict')) or ''}**",
                     code(render_scalar(e.get("confidence"))) if e.get("confidence") is not None else gap(lang, None),
                     code(e.get("raw_pointer"))))
    blocks.append(table(
        (t(lang, "expert.s2.col_source"), t(lang, "expert.s2.col_verdict"),
         t(lang, "expert.s2.col_confidence"), t(lang, "expert.s2.col_pointer")),
        rows,
    ))
    if view.normalized.get("verdict_disagreement"):
        gl.mark("verdict_disagreement")
        blocks.append(f"> {t(lang, 'expert.s2.disagreement')}")
    return blocks


def _triad(peirce: dict, lang: str) -> Blocks:
    blocks: Blocks = []
    for layer, key in (("firstness", "expert.s3.layer_first"),
                       ("secondness", "expert.s3.layer_second"),
                       ("thirdness", "expert.s3.layer_third")):
        val = render_scalar(peirce.get(layer))
        blocks.append(f"**{t(lang, key)}**")
        blocks.append(fenced(val) if val is not None else gap(lang, None))
    return blocks


def _s3_peirce(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'expert.s3.title')}"]
    if view.schema == SCHEMA_MCP:
        any_triad = False
        for f in adapter.finding_entries(view):
            peirce = f.get("peirce")
            if not isinstance(peirce, dict):
                continue
            any_triad = True
            gl.mark("Firstness", "Secondness", "Thirdness")
            for key in ("verdict", "status", "confidence"):
                gl.mark(str(f.get(key)))
            fid = render_scalar(f.get("id"))
            blocks.append(f"### {code(fid) + ' ' if fid else ''}{render_scalar(f.get('title')) or ''}"
                          f" ({render_scalar(f.get('verdict')) or gap(lang, None)})")
            blocks.extend(_triad(peirce, lang))
        if not any_triad:
            blocks.append(t(lang, "expert.s3.none"))
    elif view.schema == SCHEMA_EBS_V1:
        peirce = (view.raw.get("caie_analysis") or {}).get("peirce_chain")
        if isinstance(peirce, dict) and peirce:
            gl.mark("Firstness", "Secondness", "Thirdness", "CAIE")
            blocks.extend(_triad(peirce, lang))
        else:
            blocks.append(t(lang, "expert.s3.none"))
    else:
        blocks.append(t(lang, "expert.s3.none_agent"))
        narrative = adapter.narrative_text(view)
        if narrative is not None:
            blocks.append(fenced(narrative))
    return blocks


def _s4_scores(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'expert.s4.title')}", t(lang, "expert.s4.intro")]
    scores = adapter.exact_scores(view)
    if not scores:
        blocks.append(t(lang, "expert.s4.none"))
        return blocks
    gl.mark("Fraction")
    for ptr, _ in scores:
        gl.mark(ptr.rsplit("/", 1)[-1])
    blocks.append(table((t(lang, "expert.s4.col_pointer"), t(lang, "expert.s4.col_value")),
                        [(code(p), code(v)) for p, v in scores]))
    return blocks


def _s5_gates(view: BundleView, lang: str, gl: GlossaryCollector, verdicts: list[str]) -> Blocks:
    gl.mark("Daubert")
    blocks: Blocks = [f"## {t(lang, 'expert.s5.title')}", t(lang, "expert.s5.intro")]
    gates = adapter.refutation_gate_entries(view)
    if not gates:
        blocks.append(t(lang, "expert.s5.gates_none"))
    for g in gates:
        pointer = g.get("_pointer", "")
        top = pointer.strip("/").split("/")[0]
        gl.mark(top)
        blocks.append(f"### {code(pointer)}")
        rows = []
        for k in sorted(g):
            if k == "_pointer":
                continue
            gl.mark(k)
            rows.append((code(k), render_scalar(g[k]) if g[k] is not None else gap(lang, None)))
        blocks.append(table((t(lang, "custody.col_field"), t(lang, "expert.s5.col_value")), rows))
    blocks.append(f"### {t(lang, 'expert.s5.da_title')}")
    da = adapter.devil_advocate_entries(view)
    if da:
        gl.mark("devil_advocate")
        for pointer, value in da:
            blocks.append(code(pointer))
            blocks.append(fenced(render_scalar(value)))
    else:
        blocks.append(t(lang, "expert.s5.da_none"))
        flagged = [v for v in verdicts if v in ("INTENT", "MALICE")]
        if flagged:
            blocks.append(f"> {t(lang, 'expert.s5.da_missing_for_intent', verdict=', '.join(flagged))}")
    return blocks


def _s6_execution(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'expert.s6.title')}"]
    s = adapter.tool_log_summary(view)
    kind = s["kind"]
    if kind == "none":
        blocks.append(t(lang, "expert.s6.none"))
        return blocks
    gl.mark(kind)
    facts = [f"- {t(lang, 'expert.s6.kind')}: {code(kind)}"]
    if kind == "tool_execution_log":
        gl.mark("chain_version", "chain_tip_sha256")
        present, absent = t(lang, "expert.s6.present"), t(lang, "expert.s6.absent")
        facts.append(f"- {t(lang, 'expert.s6.entries')}: {s['entry_count']}")
        facts.append(f"- {t(lang, 'expert.s6.chain_version')}: "
                     f"{code(s['chain_version']) if s['chain_version'] is not None else gap(lang, None)}")
        facts.append(f"- {t(lang, 'expert.s6.chain_tip')}: {present if s['chain_tip_present'] else absent}")
        facts.append(f"- {t(lang, 'expert.s6.chain_tip_hmac')}: {present if s['chain_tip_hmac_present'] else absent}")
    elif kind == "audit_trail":
        facts.append(f"- {t(lang, 'expert.s6.entries')}: {s['entry_count']}")
        facts.append(f"- {t(lang, 'expert.s6.start')}: {code(render_scalar(s['start_time'])) if s['start_time'] is not None else gap(lang, None)}")
        facts.append(f"- {t(lang, 'expert.s6.end')}: {code(render_scalar(s['end_time'])) if s['end_time'] is not None else gap(lang, None)}")
        facts.append(f"- {t(lang, 'expert.s6.sha256_entries')}: {s['entries_with_sha256']}")
    blocks.append(facts)
    if kind == "system_state":
        gl.mark("system_state")
        blocks.append(f"**{t(lang, 'expert.s6.system_state')}**")
        blocks.append(table((t(lang, "custody.col_field"), t(lang, "custody.col_value")),
                            [(code(k), code(v)) for k, v in s["fields"]]))
        return blocks
    if s["histogram"]:
        blocks.append(f"**{t(lang, 'expert.s6.histogram')}**")
        blocks.append(table((t(lang, "expert.s6.col_label"), t(lang, "expert.s6.col_count")),
                            [(code(label), str(n)) for label, n in s["histogram"]]))
    if s["listing"]:
        blocks.append(f"**{t(lang, 'expert.s6.listing', cap=TOOL_LOG_LISTING_CAP)}**")
        cols = list(s["listing"][0].keys())
        blocks.append(table([code(c) for c in cols],
                            [[render_scalar(e.get(c)) for c in cols] for e in s["listing"]]))
        if s["truncated"]:
            blocks.append(t(lang, "expert.s6.truncated", cap=TOOL_LOG_LISTING_CAP, total=s["entry_count"]))
    return blocks


def render_expert(view: BundleView, lang: str) -> str:
    gl = GlossaryCollector()
    verdicts = on_scale_verdicts(adapter.verdict_entries(view))

    blocks: Blocks = header(view, "expert", lang, gl)
    blocks.extend(_s1_custody(view, lang, gl))
    blocks.extend(_s2_verdicts(view, lang, gl))
    blocks.extend(_s3_peirce(view, lang, gl))
    blocks.extend(_s4_scores(view, lang, gl))
    blocks.extend(_s5_gates(view, lang, gl, verdicts))
    blocks.extend(_s6_execution(view, lang, gl))
    blocks.extend(verify_section(view, lang, 7))
    blocks.append(f"## {t(lang, 'expert.s8.title')}")
    blocks.append(t(lang, "expert.s8.intro"))
    blocks.extend(gaps_block(view, lang, adapter.known_limitations(view)))
    blocks.append(t(lang, "expert.s8.pointers"))
    blocks.extend(glossary_section(gl, lang, 9))
    blocks.extend(footer(view, lang))
    return join_blocks(blocks)


__all__ = ["render_expert"]
