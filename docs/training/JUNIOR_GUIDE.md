# Reading a VIGÍA verdict as a SOC analyst

This guide is for an analyst who has a VIGÍA bundle in front of them for the
first time. It explains what the verdict is, what it is not, and what a junior
report (`*_report_junior_<lang>.md`) shows you, section by section. Spanish
version: [`JUNIOR_GUIDE_ES.md`](./JUNIOR_GUIDE_ES.md).

---

## 1. What you are looking at

VIGÍA does not tell you *what happened*. Every forensic tool does that. It answers
a narrower question: **does the evidence show deliberate behavior, and how much?**
The answer is a single token on a five-rung scale, sealed with a hash before any
human or language model writes a sentence about it.

Three kinds of bundle exist, and the report header names which one you have:

| Family (as printed) | Comes from | Verdict field |
|---|---|---|
| `agent_audit` | `python3 vigia_agent.py` (Mode 1, no LLM) | `agent_verdict` |
| `ebs_v1` | the sealed pipeline (`vigia/core/bundle_builder.py`) | `decision_trace.decision`, sometimes also `caie_analysis.verdict` |
| `mcp_investigation` | a Claude Code / MCP investigation (Mode 2) | `overall_verdict` or `final_verdict` |

The junior report is a **viewer**. It copies the sealed values character by
character and adds explanation around them. It cannot add evidence, and if it
ever disagrees with the bundle, the bundle wins.

## 2. The scale

| Verdict | Means | Does not mean |
|---|---|---|
| `NOISE` | everything observed has an innocent, normal explanation | innocence; artifacts that were never collected are not covered |
| `SUSPICION` | a real structural anomaly, no sign of concealment or coordination | attribution; an untested innocent cause may still exist |
| `INTENT` | deliberate decisions produced this outcome (two sources, refutation passed) | guilt; it is an inference about the analyzed artifacts |
| `MALICE` | the actor is hiding that they are hiding (anti-forensics) | a legal finding, an identification, or a statement about damage |
| `ABSTAIN` | not enough evidence to classify | benign; it means undecided, and the report lists what is missing |

`ERROR` is not a rung. It is the exit label of a run that did not finish.

**Mode 1 has no INTENT rung.** An agent bundle that says `SUSPICION` may sit
where a Mode 2 investigation would say `INTENT`: the deterministic pipeline caps
borderline cases at `SUSPICION` (see `CLAUDE.md`, Verdict Scale). Read the sealed
narrative before deciding how urgent a `SUSPICION` is.

## 3. What to do at each rung

These are generic SOC steps; your runbook wins.

- **NOISE**: close or de-prioritize, keep the bundle with the ticket, write down the
  normal behavior that explained the anomaly.
- **SUSPICION**: keep the case open, do not block yet, look for a second independent
  source (another host, log or sensor), get a senior review before escalating.
- **INTENT**: escalate to incident response, preserve originals read-only, start
  scoping what else the same actor could have touched.
- **MALICE**: escalate now, preserve everything (including what may have been
  deleted), and leave containment decisions to IR and management.
- **ABSTAIN**: do not close as benign. Read the gaps section, collect what it names,
  re-run, compare the two bundles.

## 4. Two verdicts that disagree

An EBS v1 bundle can carry two verdict-bearing fields: the sealed pipeline decision
and the CAIE module's forensic verdict. When they differ, the report shows **both**
and a notice; it never picks one. The worked example
`examples/VIGIA-REAL-SRL-DMZ-FTP_bundle_report_expert_en.md` shows `ABSTAIN` next
to `MALICE`. That is not a bug in the report: the bundle sealed both, and the
examiner's note (`r3_calibration_note`) explains why. Do not act on the more severe
one just because it is more severe.

## 5. Walking through a junior report

Open `examples/VIGIA-KIWI-006_bundle_report_junior_es.md` (Mode 2, Spanish) or
`examples/FF-GENUINE-001_agent_bundle_report_junior_en.md` (Mode 1, English) and
follow the numbered sections:

1. **The verdict.** Each verdict-bearing field, verbatim, with its field name. In an
   agent bundle you also see `best_hypothesis`: that is the winning hypothesis
   label, not a verdict.
2. **What it means.** The scale table with this bundle's rung marked.
3. **What to do next.** The generic steps above for this rung.
4. **What NOT to conclude.** The over-readings that get analysts in trouble.
5. **Findings.** Mode 2: each finding with its three Peircean layers. Firstness is
   the raw observation, Secondness is how it clashes with normal, Thirdness is the
   deliberate pattern that would produce it. The strongest benign explanation
   (`devil_advocate`) sits right under it, and any candidate verdict a gate rejected
   is listed after the findings. Mode 1: a table of signals with exact fractions and
   the pipeline's own sealed narrative.
6. **MITRE ATT&CK.** Technique ids found in the bundle with MITRE's own name and
   description (English, never translated) and a link.
7. **SANS lifecycle.** Where a sealed verdict sits (Identification) and why
   containment is a human decision.
8. **Gaps.** What the bundle does not say. Missing means not recorded, not absent
   from reality.
9. **Glossary.** Every sealed token used above, explained.
10. **How to verify.** The one command that checks this family's integrity.

## 6. Three habits

- **Quote, do not paraphrase.** When you write the ticket, copy the verdict token
  and the source SHA-256 from the report header. Anyone can then regenerate the
  report and check your quote.
- **Numbers are fractions.** `19/20` is exact. It is not "95%": the pipeline uses
  exact arithmetic so two machines get the same result, and the report keeps it.
- **Language is evidence.** Quoted text keeps the language it was sealed in. A
  Spanish narrative inside an English report is the record, not a rendering
  defect.

## 7. Where to go next

- `KNOWN_LIMITATIONS.md`: what the system cannot see (L-001 onward). L-074 covers
  these reports.
- `docs/EXECUTION_MODES.md`: why the three bundle families exist.
- [`EXPERT_GUIDE.md`](./EXPERT_GUIDE.md): verification, hash families, Daubert gates.
