# VIGÍA — Intentionality Analysis Bridge for the SIFT Workstation

[English](./README.md) · [Español](./README_ES.md) · [Technical README](./docs/VIGIA_TECHNICAL_STATE_EN.md) · Author: Anna Tchijova · License: Apache 2.0

**Index:** [What VIGÍA does](#from-ioc-to-ioi) · [Quick start](#quick-start) · [Accuracy and evaluation](#accuracy-and-evaluation) · [Documentation](#documentation) · [Related DFIR projects](#related-dfir-projects)

> *"Making deception computationally expensive for the attacker."*
> Today, lying in a log or faking an attack is free. VIGÍA charges that price
> by quantifying the logical fractures in the lie.

**VIGÍA is not a detector. It is a deterministic inference engine that quantifies
the fracture between what the evidence says and what the evidence should say.**
If a system claims MALICE without being able to explain why with exact mathematics,
it is not forensics — it is divination.

---

## From IoC to IoI

Current DFIR systems — EDR, SIEM, SOAR — answer **"What happened?"**
VIGÍA answers **"Why did it happen, and who benefits from that interpretation?"**

| Traditional DFIR | VIGÍA |
|------------------|-------|
| IoC (Indicator of Compromise) | IoI (Indicator of Intent) |
| Opaque ML with "87% confidence" | Exact `Fraction` arithmetic with `audit_hash` |
| LLM makes the verdict | LLM narrates *after* the verdict is sealed |
| One hash per report | 4 separate hashes + HMAC chain |
| Ignores silence | Detects absence of expected evidence |

Attackers can fabricate or suppress technical evidence (IoC). They cannot eliminate
the **semiotic fractures** that deliberate fabrication produces: temporal
incoherencies, significant silences (Eco), excessive digital perfection, Carnegie
manipulation patterns, and Grice maxim violations.

### Scale of the work

| | |
|---|---|
| **Production Python** | more than **102,000 lines** (108,805 across 273 files, tests excluded) |
| **Tests** | 46,931 further lines; 2,066 test functions in 255 files |
| **JSON and Markdown** (cases, evidence, sealed bundles, documentation) | more than **540,000 lines** |
| **Total under version control** | more than **713,000 lines** of text |
| **Sealed forensic bundles** | 617, verifiable without VIGÍA's code |
| **Academic documentation** | **193 modules in 4 languages** (EN / ES / RU / ZH) |

The code has gone through 11 in-house red-team rounds, external audits, and weekly
mutation testing of the verdict path. Per-module documentation lives in the
[academic documentation index](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md),
covering all 193 modules in English, Spanish, Russian and Chinese. The breakdown of
every figure and the commands to reproduce it are in the
[Spanish technical README](./docs/VIGIA_ESTADO_TECNICO_ES.md#2-magnitud-del-trabajo).

---

## Quick Start

Mode 1 (Python fallback) produces a sealed, cryptographically verifiable verdict
with zero human input, zero tokens, and no internet required.

```bash
pip install -r requirements.txt --break-system-packages
export VIGIA_EVIDENCE_DIR="/path/to/read-only/evidence"   # required

# Autonomous end-to-end investigation
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-VANKO.json \
  --case-id VIGIA-REAL-VANKO --output results/vanko_bundle.json

# Verify a sealed bundle independently (stdlib only, no VIGÍA code required)
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
```

A local, fully offline web dashboard (bundle browser, verification panel,
Mode 1 launcher) is available with `./launch_vigia_ui.sh` →
`http://127.0.0.1:8010` — see INSTALL.md §11b.

Exit codes: `0` = no evil, `1` = MALICE, `2` = error, `3` = intent/suspicion.
Full setup: [`INSTALL.md`](./INSTALL.md) ([ES](./INSTALL_ES.md)) ·
Command reference: [`vigia_commands_en.html`](https://annatchijova.github.io/vigia/vigia_commands_en.html) ·
VIGÍA (math model): [`vigia.html`](https://annatchijova.github.io/vigia/vigia.html) ·
Simulator: [`simulator.html`](https://annatchijova.github.io/vigia/simulator.html).

---

## Architecture — LLM Isolation

```mermaid
graph LR
    A[EVIDENCE] --> B[MATHEMATICAL ENGINE]
    B --> C[Sealed ForensicBundle]
    C --> D[LLM NARRATOR]
    D --> E[Judicial Report]
    F[LLM CANNOT] -.->|modify| B
    F -.->|alter verdict| C
```

The LLM never touches the scoring pipeline. It receives a sealed, cryptographically
committed bundle and produces a narrative. The verdict is deterministic and
reproducible without the LLM — a design requirement for potential Daubert
admissibility. The engine uses `fractions.Fraction` (zero floating-point in the
critical path), the CAIE weights hard-to-falsify evidence more, and the Daubert
corroboration gate rejects unsubstantiated candidates *before* any verdict is
sealed. `ABSTAIN` is a valid, mathematically justified verdict.

---

## Deployment Modes

Mode 1 is the primary, evaluated forensic core; Modes 2–5 reuse local deterministic
tools but have separately scoped investigation and reporting contracts (a Mode 2
report never mutates a sealed Mode 1 bundle). See [`EXECUTION_MODES.md`](./docs/EXECUTION_MODES.md)
and the Claude Code playbook [`CLAUDE.md`](./CLAUDE.md).

| Mode | Description | LLM |
|------|-------------|-----|
| **1 — Python fallback** | Full scoring pipeline, 0 tokens, no internet. `< 50ms` average. | No |
| **2 — Claude Code + MCP** | 22 forensic tools; interactive Peircean investigation. | Yes |
| **3 — Ollama** | Local LLM; no data leaves the machine. | Yes |
| **4 — Autonomous batch agent** | Corpus processing with self-correcting loop. | Optional |
| **5 — OpenWebUI (experimental)** | MCP server via web interface. | Yes |

---

## Accuracy and evaluation

**Every sealed verdict, in every mode, is produced and gated by the deterministic
Python engine (`vigia_scorer.py`) — an LLM can propose, it cannot decide or
override the gate.** None of the numbers below are "Claude's accuracy"; see
[`docs/ACCURACY.md`](./docs/ACCURACY.md) ([ES](./docs/ACCURACY_ES.md)) for the
full methodology, the gate mechanism, and the three-domain breakdown, and
[`CLAUDE.md` — Refutation Protocol](./CLAUDE.md#refutation-protocol-documentation-requirement)
for the worked example of the gate rejecting an LLM candidate verdict.

- **Agent over JSON (Domain B), Python only, 0 LLM calls** — **158/162 (97.5%)**
  label-blind on the *detection corpus*. The separate **187/199 (94.0%)** figure
  is the mixed-corpus aggregate. It includes 31 adversarial stress cases designed to
  break the system: **16 BREAK**, **7 KIWI**, **3 false-negative (FN)** and **5
  false-positive (FP)** cases. Those results measure resistance and documented
  limits, not ordinary detection accuracy. The 97.5% applies only to the detection
  subset; it is not a raw-evidence or all-modes performance claim.
- **Claude Code / MCP (Domain A), LLM-assisted investigation, same
  deterministic seal** — evaluated per case on real raw evidence, not a
  corpus-wide figure.
- **Agent over raw evidence (Domain C), Python only, 0 LLM calls** — 43 raw
  evidence sources with sealed bundles in `results/`.

Known failure modes — including stale pre-fix figures that are flagged, not
deleted: [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md).

```bash
python3 -m pytest tests/ -v          # deterministic core regression suite
python3 run_all_agent.py --timeout 90  # full corpus, label-blind
```

---

## Documentation

Reference documentation lives in the
[VIGÍA academic documentation index](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md):
193 modules documented in 4 languages (EN / ES / RU / ZH), with indexes in
[Spanish](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX.md),
[Russian](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_RU.md) and
[Chinese](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_ZH.md).

### Repository map

```text
vigia-repo/
├── vigia/          # forensic analysis modules and integrations
├── forensics/      # bundle verification and forensic utilities
├── docs/           # methodology, architecture, audits, and indexes
├── data/cases/     # case inputs and evaluation corpora
├── results/        # generated bundles, reports, and evaluation outputs
└── tests/          # regression and adversarial test suites
```

**Getting started & usage**
- [`INSTALL.md`](./INSTALL.md) · [`INSTALL_ES.md`](./INSTALL_ES.md) — setup and installation
- [`docs/QUICK_START.md`](./docs/QUICK_START.md) — quick integration walkthrough
- [`EXECUTION_MODES.md`](./docs/EXECUTION_MODES.md) — map of every way to run an analysis
- [`CLAUDE.md`](./CLAUDE.md) — Claude Code / MCP investigation playbook (22 tools)
- [Command reference](https://annatchijova.github.io/vigia/vigia_commands_en.html) — all modes, copy-paste examples

**Cases & examples**
- [`docs/PROMPTS_REALCASES_CLAUDE.md`](./docs/PROMPTS_REALCASES_CLAUDE.md) — copy-paste prompts to run full investigations
- [`RAW_CASES_LOG.md`](./docs/RAW_CASES_LOG.md) · [ES](./docs/RAW_CASES_LOG_ES.md) — per-case raw-evidence catalog
- [`docs/readme_benign_cases.md`](./docs/readme_benign_cases.md) — benign / authorized-use cases
- [`docs/digital_corpora_complete_report.md`](./docs/digital_corpora_complete_report.md) · [`docs/nist_cfreds_full_report.md`](./docs/nist_cfreds_full_report.md) — full real-corpus reports
- [`results/`](./results/) — sealed ForensicBundles, amicus curiae, and SHA-256 sidecars

**Accuracy, validation & compliance**
- [`docs/ACCURACY.md`](./docs/ACCURACY.md) · [ES](./docs/ACCURACY_ES.md) — methodology and corpus metrics
- [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) — documented limitations (Daubert transparency)
- [`DAUBERT_JUDICIAL.md`](./docs/DAUBERT_JUDICIAL.md) · [ES](./docs/DAUBERT_JUDICIAL_ES.md) — Daubert admissibility rationale
- [`docs/MUTATION_RUNBOOK.md`](./docs/MUTATION_RUNBOOK.md) — mutation-testing operations guide

**Theory & methodology**
- [`docs/vigia_paper_methodology.md`](./docs/vigia_paper_methodology.md) — the formal methodology paper
- [`docs/EPISTEMIC_KERNEL.md`](./docs/EPISTEMIC_KERNEL.md) — the epistemic kernel (hypothesis generation)
- [`docs/skills/abductive-engineering/SKILL.md`](./docs/skills/abductive-engineering/SKILL.md) — abductive reasoning as a reusable skill

**Architecture & technical state**
- [`docs/VIGIA_TECHNICAL_STATE_EN.md`](./docs/VIGIA_TECHNICAL_STATE_EN.md) · [ES](./docs/VIGIA_ESTADO_TECNICO_ES.md) — full system state
- [`docs/diagrama_pipeline.md`](./docs/diagrama_pipeline.md) — pipeline diagram
- [Architecture diagrams](https://annatchijova.github.io/vigia/vigia_diagrams.html) · [VIGÍA (math model)](https://annatchijova.github.io/vigia/vigia.html) · [Simulator](https://annatchijova.github.io/vigia/simulator.html) · [Demo video](https://www.youtube.com/watch?v=NOquYzUwMkg)

**Development & project**
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) · [`CONTRIBUYENDO.md`](./CONTRIBUYENDO.md) — contribution guide
- [`docs/ENGINEERING_DISCIPLINE.md`](./docs/ENGINEERING_DISCIPLINE.md) — engineering discipline for agents working on the code
- [`SECURITY.md`](./SECURITY.md) — security policy and hardening
- [`BUGS_PENDIENTES.md`](./BUGS_PENDIENTES.md) ([EN](./BUGS_PENDIENTES_EN.md)) · [`BUGS_HISTORICO.md`](./BUGS_HISTORICO.md) ([EN](./BUGS_HISTORICO_EN.md)) — bug registry (open / resolved)
- [`AUTHORS.md`](./AUTHORS.md) · [`docs/VIGIA_THEME_SONG.md`](./docs/VIGIA_THEME_SONG.md) — credits and theme song

> `docs/` also holds the full trail of internal audit, red-team, and design records
> (`AUDITORIA_*`, `REDTEAM_ROUND*`, `FASE*`, `B0*`), preserved as project history.

## Related DFIR projects

I also recommend [Velo](https://github.com/annatchijova/velo),
[Zaynor](https://github.com/annatchijova/zaynor), and
[Annaconda](https://github.com/annatchijova/annaconda), other DFIR projects by the
same author. More DFIR work is in progress, alongside separate red-team and
blue-team repositories under construction.

---

## Theoretical Foundation

VIGÍA rests on Charles S. Peirce's abductive semiotics (Firstness / Secondness /
Thirdness), H. Paul Grice's cooperative principle, Dale Carnegie's manipulation
taxonomy, and Umberto Eco's theory of significant silence and overinterpretation.

---

## License

Apache 2.0 — see [`LICENSE`](./LICENSE).
Copyright (c) 2026 Anna Tchijova and the VIGÍA AI Collective.

*"The question is not what happened, but why did someone make it happen —
and who benefits from that interpretation?"* — VIGÍA
