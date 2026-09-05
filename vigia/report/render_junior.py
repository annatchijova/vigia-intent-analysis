"""Junior SOC analyst view of a sealed bundle.

Plain language around verbatim values: the verdict and what it does and does
not mean, generic next steps per rung, findings with each Peircean layer
explained in one line, MITRE techniques with MITRE's own text, PICERL context,
explicit gaps, a glossary of every sealed term used, and how to verify.
"""

from __future__ import annotations

from vigia.report import adapter
from vigia.report.adapter import BundleView, render_scalar
from vigia.report.glossary import GlossaryCollector
from vigia.report.mitre import describe_ttp
from vigia.report.picerl import phase_rows
from vigia.report.renderers import (
    EXIT_LABEL,
    SCALE,
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


def _s1_verdict(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    entries = adapter.verdict_entries(view)
    blocks: Blocks = [f"## {t(lang, 'junior.s1.title')}", t(lang, "junior.s1.intro")]
    if not entries:
        blocks.append(t(lang, "junior.s1.none"))
        return blocks
    lines = []
    for e in entries:
        gl.mark_verdict(e.get("verdict"))
        source = str(e.get("source", ""))
        field = source.split(" ")[0]
        gl.mark(field)
        conf = render_scalar(e.get("confidence"))
        line = f"- {code(field)}: **{render_scalar(e.get('verdict')) or gap(lang, None)}**"
        if conf is not None:
            line += f" ({t(lang, 'finding.confidence').lower()}: {code(conf)})"
        lines.append(line)
    blocks.append(lines)
    if view.normalized.get("verdict_disagreement"):
        gl.mark("verdict_disagreement")
        blocks.append(f"> {t(lang, 'junior.s1.disagreement')}")
    if view.schema == SCHEMA_AGENT_AUDIT and any(
        e.get("source", "").startswith("pipeline_results.abduction.best_hypothesis") for e in entries
    ):
        gl.mark("best_hypothesis", "agent_verdict")
        blocks.append(t(lang, "junior.s1.hypothesis_note"))
    return blocks


def _s2_meaning(view: BundleView, lang: str, gl: GlossaryCollector, verdicts: list[str]) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'junior.s2.title')}", t(lang, "junior.s2.scale_intro")]
    rows = []
    for rung in SCALE:
        marker = f" **({t(lang, 'junior.s2.this_one')})**" if rung in verdicts else ""
        rows.append((code(rung) + marker, t(lang, f"scale.{rung}.meaning"), t(lang, f"scale.{rung}.bar")))
    blocks.append(table(
        (t(lang, "junior.s2.col_verdict"), t(lang, "junior.s2.col_meaning"), t(lang, "junior.s2.col_bar")),
        rows,
    ))
    if view.schema == SCHEMA_AGENT_AUDIT:
        blocks.append(t(lang, "junior.s2.mode1_note"))
    return blocks


def _s3_next(lang: str, verdicts: list[str], has_entries: bool) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'junior.s3.title')}", t(lang, "junior.s3.intro")]
    if not verdicts:
        key = "next.UNKNOWN"
        blocks.append(t(lang, key))
        return blocks
    for v in verdicts:
        if len(verdicts) > 1:
            blocks.append(f"**{code(v)}**")
        blocks.append(t(lang, f"next.{v}"))
    return blocks


def _s4_not(lang: str, verdicts: list[str]) -> Blocks:
    items = [f"- {t(lang, f'notnot.{v}')}" for v in verdicts]
    items.append(f"- {t(lang, 'notnot.generic')}")
    return [f"## {t(lang, 'junior.s4.title')}", items]


def _finding_block(f: dict, lang: str, gl: GlossaryCollector) -> Blocks:
    title = render_scalar(f.get("title")) or t(lang, "finding.untitled")
    fid = render_scalar(f.get("id"))
    head = f"### {code(fid) + ' ' if fid else ''}{title}"
    facts = []
    for key, label in (("verdict", "finding.verdict"), ("confidence", "finding.confidence"),
                       ("status", "finding.status")):
        val = render_scalar(f.get(key))
        if val is not None:
            gl.mark(val)
            facts.append(f"- {t(lang, label)}: **{val}**")
    for key, label in (("artifacts", "finding.artifacts"), ("tools_used", "finding.tools")):
        vals = f.get(key) or []
        if vals:
            facts.append(f"- {t(lang, label)}: " + ", ".join(code(render_scalar(v)) for v in vals))
    blocks: Blocks = [head, facts]
    peirce = f.get("peirce")
    if isinstance(peirce, dict):
        gl.mark("Firstness", "Secondness", "Thirdness")
        for layer, key in (("firstness", "junior.s5.peirce_first"),
                           ("secondness", "junior.s5.peirce_second"),
                           ("thirdness", "junior.s5.peirce_third")):
            val = render_scalar(peirce.get(layer))
            blocks.append(f"*{t(lang, key)}*")
            blocks.append(fenced(val) if val is not None else gap(lang, None))
    if f.get("carnegie") is not None:
        gl.mark("Carnegie")
        blocks.append(f"- {t(lang, 'finding.carnegie')}: {render_scalar(f['carnegie'])}")
    if f.get("devil_advocate") is not None:
        gl.mark("devil_advocate")
        blocks.append(f"**{t(lang, 'finding.devil_advocate')}**")
        blocks.append(fenced(render_scalar(f["devil_advocate"])))
    if f.get("corroboration") is not None:
        blocks.append(f"- {t(lang, 'finding.corroboration')}: {render_scalar(f['corroboration'])}")
    return blocks


def _gates_block(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    """Pre-emission corrections a junior should notice: a candidate verdict that
    a Daubert gate rejected before anything was sealed."""
    gates = adapter.refutation_gate_entries(view)
    if not gates:
        return []
    gl.mark("refutation_gate_log", "Daubert")
    items = []
    for g in gates:
        parts = []
        for key in ("candidate_verdict", "gate_applied", "gate_rule", "gate_result"):
            val = render_scalar(g.get(key))
            if val is not None:
                gl.mark_verdict(val)
                parts.append(f"{code(key)}: {val}")
        if not parts:
            parts.append(code(g.get("_pointer", "")))
        items.append("- " + "; ".join(parts))
    return [f"**{t(lang, 'junior.s5.gates_title')}**", t(lang, "junior.s5.gates_intro"), items]


def _s5_findings(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'junior.s5.title')}"]
    findings = adapter.finding_entries(view)
    if view.schema == SCHEMA_MCP:
        blocks.append(t(lang, "junior.s5.intro_mcp"))
        summary = adapter.executive_summary(view)
        if summary is not None:
            blocks.append(f"**{t(lang, 'junior.s5.summary_label')}**")
            blocks.append(fenced(summary))
        if not findings:
            blocks.append(t(lang, "junior.s5.no_findings"))
        for f in findings:
            blocks.extend(_finding_block(f, lang, gl))
        blocks.extend(_gates_block(view, lang, gl))
    elif view.schema == SCHEMA_AGENT_AUDIT:
        blocks.append(t(lang, "junior.s5.intro_agent"))
        signals = [f for f in findings if f.get("kind") == "pipeline_signal"]
        if signals:
            gl.mark("Fraction", "z_score")
            blocks.append(table(
                (t(lang, "signals.col_artifact"), t(lang, "signals.col_type"),
                 t(lang, "signals.col_source"), t(lang, "signals.col_confidence"),
                 t(lang, "signals.col_z")),
                [(render_scalar(s.get("id")), render_scalar(s.get("evidence_type")),
                  render_scalar(s.get("source")), render_scalar(s.get("confidence")),
                  render_scalar(s.get("z_score"))) for s in signals],
            ))
            blocks.append(t(lang, "signals.exact_note"))
            blocks.append(t(lang, "junior.s5.no_signal_verdict"))
        else:
            blocks.append(t(lang, "junior.s5.no_findings"))
        narrative = adapter.narrative_text(view)
        if narrative is not None:
            blocks.append(f"**{t(lang, 'junior.s5.narrative_label')}**")
            blocks.append(fenced(narrative))
    elif view.schema == SCHEMA_EBS_V1:
        blocks.append(t(lang, "junior.s5.intro_ebs"))
        reason = adapter.narrative_text(view)
        if reason is not None:
            gl.mark("CAIE")
            blocks.append(f"**{t(lang, 'junior.s5.narrative_label')}**")
            blocks.append(fenced(reason))
        peirce = (view.raw.get("caie_analysis") or {}).get("peirce_chain")
        if isinstance(peirce, dict) and peirce:
            gl.mark("Firstness", "Secondness", "Thirdness")
            for layer, key in (("firstness", "junior.s5.peirce_first"),
                               ("secondness", "junior.s5.peirce_second"),
                               ("thirdness", "junior.s5.peirce_third")):
                if layer in peirce:
                    blocks.append(f"*{t(lang, key)}*")
                    blocks.append(fenced(render_scalar(peirce[layer])))
        if reason is None and not (isinstance(peirce, dict) and peirce):
            blocks.append(t(lang, "junior.s5.no_findings"))
    return blocks


def _s6_mitre(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    blocks: Blocks = [f"## {t(lang, 'junior.s6.title')}", t(lang, "junior.s6.intro")]
    ids = adapter.mitre_ids(view)
    if not ids:
        blocks.append(t(lang, "junior.s6.none"))
        return blocks
    gl.mark("MITRE ATT&CK")
    rows = []
    notes = []
    for tid, where in ids:
        d = describe_ttp(tid)
        if d.in_local_dictionary:
            name = f"[{d.name}]({d.url})"
        else:
            name = f"[{tid}]({d.url}) ({t(lang, 'mitre.not_local')})"
        rows.append((code(tid), name, code(where)))
        if d.description:
            notes.append(f"- {code(tid)}: {d.description}")
    blocks.append(table((t(lang, "mitre.col_id"), t(lang, "mitre.col_name"), t(lang, "mitre.col_where")), rows))
    if notes:
        blocks.append(notes)
    return blocks


def _s7_picerl(view: BundleView, lang: str, gl: GlossaryCollector) -> Blocks:
    gl.mark("PICERL")
    blocks: Blocks = [f"## {t(lang, 'junior.s7.title')}", t(lang, "junior.s7.intro")]
    blocks.append(table((t(lang, "picerl.col_phase"), t(lang, "picerl.col_desc")), phase_rows(lang)))
    phase = adapter.sans_phase_text(view)
    if phase is not None:
        gl.mark("sans_phase")
        blocks.append(f"- {t(lang, 'junior.s7.phase_in_bundle')}: {code(phase)}")
    if view.schema == SCHEMA_AGENT_AUDIT and view.raw.get("sans_compliance") is not None:
        gl.mark("sans_compliance")
        blocks.append(t(lang, "junior.s7.sans_compliance_note"))
        blocks.append(fenced(render_scalar(view.raw.get("sans_compliance"))))
    return blocks


def render_junior(view: BundleView, lang: str) -> str:
    gl = GlossaryCollector()
    entries = adapter.verdict_entries(view)
    verdicts = on_scale_verdicts(entries)
    if any(e.get("verdict") == EXIT_LABEL for e in entries):
        verdicts.append(EXIT_LABEL)
        gl.mark(EXIT_LABEL)

    blocks: Blocks = header(view, "junior", lang, gl)
    blocks.extend(_s1_verdict(view, lang, gl))
    blocks.extend(_s2_meaning(view, lang, gl, verdicts))
    blocks.extend(_s3_next(lang, verdicts, bool(entries)))
    blocks.extend(_s4_not(lang, verdicts))
    blocks.extend(_s5_findings(view, lang, gl))
    blocks.extend(_s6_mitre(view, lang, gl))
    blocks.extend(_s7_picerl(view, lang, gl))
    blocks.append(f"## 8. {t(lang, 'section.gaps')}")
    blocks.append(t(lang, "junior.s8.intro"))
    blocks.extend(gaps_block(view, lang, adapter.known_limitations(view)))
    blocks.extend(glossary_section(gl, lang, 9))
    blocks.extend(verify_section(view, lang, 10))
    blocks.extend(footer(view, lang))
    return join_blocks(blocks)


__all__ = ["render_junior"]
