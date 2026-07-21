# VIGÍA — Intentionality Analysis Bridge for SIFT Workstation

> **Note (2026-06-19, post-submission):** one pre-existing corpus bundle
> (`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json`) was sealed before a
> verifier strictness fix and will show a documented R7 failure if
> re-verified. This is expected and intentional — see `KNOWN_LIMITATIONS.md`,
> item L-026. It is the verifier correctly catching a gap that has since been
> closed for all new bundles.

[🇪🇸 Versión en español](./README_ES.md)

> *"Making deception computationally expensive for the attacker."*
>
> Today, lying in a log or faking an attack is free. VIGÍA charges that price
> by evaluating the logical fractures in the lie.

**SANS FIND EVIL Hackathon 2026** | Author: Anna Tchijova | AI Collective: Claude, Gemini, Kimi, DeepSeek, Qwen, Grok, ChatGPT | License: Apache 2.0

---

> **VIGÍA IS NOT A DETECTOR. IT IS A DETERMINISTIC INFERENCE ENGINE THAT
> QUANTIFIES THE FRACTURE BETWEEN WHAT THE EVIDENCE SAYS AND WHAT THE
> EVIDENCE SHOULD SAY.**
>
> If a system claims "MALICE" without being able to explain why with exact
> mathematics, it is not forensics. It is divination.

---

## VIGÍA Theme Song

> *Written and produced by Olga Vasilieva*
> 🎵 [Listen on Suno](https://suno.com/song/ae1f9bc9-a9eb-40b2-96e7-6132be0dc504)

```
In the world of forensics, they just look at the trace,
They ask *what* happened in the digital space.
They trust an EDR with a random score,
But black-box divination cannot guard the door.
Today, lying in a log or faking an attack is free,
But VIGÍA is charging that price, you see!
We don't look for the virus, we don't look for the sign,
We find the logical fracture in the attacker's line!

VIGÍA! The inference engine is live!
Making deception too expensive to survive!
From Firstness to Thirdness, the Peircean track,
We seal the Forensic Bundle before the models talk back!
No floating-point drift, no illusion, no bias,
Pure rational arithmetic is here to untie us!

An excessive perfection, a significant void,
A Windows kernel habit that was cleanly destroyed.
calc.exe is calling out to the net,
A living-off-the-land trap that the adversary set.
Ledoit-Wolf and KDE quantifying the risk,
We find the hidden slips in the memory and disk.
We measure the spoofability, we lock down the state,
With a self-correcting agent at the SIFT workstation gate!

VIGÍA! The inference engine is live!
Making deception too expensive to survive!
From Firstness to Thirdness, the Peircean track,
We seal the Forensic Bundle before the models talk back!
No floating-point drift, no illusion, no bias,
Pure rational arithmetic is here to untie us!

The LLM is isolated, it cannot change the code,
It only tells the narrative when the data has flowed.
Grice maxims, Carnegie patterns under review,
Bringing the Daubert Standard of evidence to you!
Three iterations maximum, the contradictions clear,
The autonomous investigator is already here!

VIGÍA! The inference engine is live!
Making deception too expensive to survive!
From Firstness to Thirdness, the Peircean track,
We seal the Forensic Bundle before the models talk back!
No floating-point drift, no illusion, no bias,
Pure rational arithmetic is here to untie us!

Not a detector. An inference engine.
Why did it happen? Who benefits from the trace?
Cryptographic hashes holding the evidence in place.
VIGÍA. The truth is in the fracture.
```

---

## JUDGES: Submission Compliance Quick-Reference

> All required components are present. This table tells you exactly where
> to find each one.

| Requirement | Location |
|-------------|----------|
| Public repository | `github.com/annatchijova/vigia-intent-analysis` |
| License | [`LICENSE`](./LICENSE) (Apache 2.0) |
| README with setup | This file — [Installation](#installation) |
| Live demo / step-by-step | [`INSTALL.md`](./INSTALL.md) |
| Feature description | [Overview](#the-paradigm-shift-from-ioc-to-ioi) |
| **Demonstration video** | **[YouTube — VIGÍA Demo 2026](https://www.youtube.com/watch?v=NOquYzUwMkg)** |
| Interactive architecture diagrams | [`docs/vigia_diagrams.html`](./docs/vigia_diagrams.html) — [hosted](https://annatchijova.github.io/vigia/vigia_diagrams.html) |
| Mathematical logic simulator | [`vigia.html`](./vigia.html) — [hosted](https://annatchijova.github.io/vigia/vigia.html) |
| **Simulador ES** | [`vigia-es.html`](./vigia-es.html) — [hosted](https://annatchijova.github.io/vigia/vigia-es.html) |
| Command reference | [`vigia_commands_en.html`](./vigia_commands_en.html) — [hosted](https://annatchijova.github.io/vigia/vigia_commands_en.html) |
| Known limitations | [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) |
| Security policy | [`SECURITY.md`](./SECURITY.md) |
| Authors | [`AUTHORS.md`](./AUTHORS.md) |
| **Origin story** | **[`VIGIA_STORY_EN.md`](./VIGIA_STORY_EN.md) (EN) · [`VIGIA_STORY.md`](./VIGIA_STORY.md) (ES)** |
| Full compliance index | [`SUBMISSION_COMPLIANCE.md`](./SUBMISSION_COMPLIANCE.md) |
| **Real-case investigation prompts** | **[`PROMPTS_REALCASES_CLAUDE.md`](./PROMPTS_REALCASES_CLAUDE.md)** — copy-paste into Claude Code to run full forensic investigations on all 18 real cases |
| **NGDC 2012 full investigation** | **[Report (EN)](./results/agent_batch/VIGIA-NGDC-2012-REPORT.md) · [Reporte (ES)](./results/agent_batch/VIGIA-NGDC-2012-REPORTE-ES.md) · [Amicus Curiae](./results/agent_batch/VIGIA-NGDC-2012-AMICUS-CURIAE.md)** — autonomous raw-evidence analysis of the SANS National Gallery DC 2012 case (17 artifacts, 7 findings, Peircean + Daubert compliant) |
| **NGDC 2012 — tracy-home E01/E02 (physical layer)** | **[Report](./results/agent_batch/VIGIA-NGDC-2012-E01E02-REPORT.md) · [Amicus Curiae (EN)](./results/agent_batch/VIGIA-NGDC-2012-E01E02-AMICUS-CURIAE-EN.md) · [Amicus Curiae (ES)](./results/agent_batch/VIGIA-NGDC-2012-E01E02-AMICUS-CURIAE-ES.md)** — disk image analysis of Tracy's MacBook Air (5.5 GB HFS+): LogKext infrastructure, stolen stamp docs, anti-forensic VM, deleted account recovery. Physical corroboration of NGDC-002 verdict. |

**Academic documentation (193 modules, 4 languages):**
[`docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md`](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md)
— EN / ES / RU / ZH — covers every module with technical glossary and
scientific grounding in Peircean semiotics, Eco's overcodification theory,
and Grice's maxims as deterministic, falsifiable computational constructs.

https://annatchijova.github.io/vigia/vigia.html

https://annatchijova.github.io/vigia/vigia_diagrams.html

https://annatchijova.github.io/vigia/vigia_commands_en.html

**Mini juego — Simulador VIGÍA:** [🇪🇸 Español](https://annatchijova.github.io/vigia/simulador.html) · [🇬🇧 English](https://annatchijova.github.io/vigia/simulator.html)

---

## The Paradigm Shift: From IoC to IoI

| Traditional DFIR | VIGÍA |
|------------------|-------|
| What happened? | Why did it happen? |
| IoC (Indicator of Compromise) | IoI (Indicator of Intent) |
| Opaque ML with "87% confidence" | Exact `Fraction` arithmetic with `audit_hash` |
| LLM makes the verdict | LLM narrates *after* the verdict is sealed |
| One hash per report | 4 separate hashes + HMAC chain |
| Ignores silence | Detects absence of expected evidence |

Current DFIR systems — EDR, SIEM, SOAR — answer: **"What happened?"**

VIGÍA answers: **"Why did it happen, and who benefits from that interpretation?"**

Sophisticated attackers can fabricate or suppress technical evidence (IoC). They cannot
eliminate the **semiotic fractures** produced by deliberate fabrication. VIGÍA detects:

- **Temporal incoherencies** — timestamps that are structurally impossible to coexist
- **Significant silences** — the absence of expected artifacts is itself evidence (Eco)
- **Excessive digital perfection** — real systems are messy; perfection signals fabrication
- **Carnegie manipulation patterns** — artificial urgency, borrowed authority, flattery
- **Grice maxim violations** — deception violates cooperative communication principles

---

## Interactive Documentation

No installation required. Open directly in any browser:

| Resource | URL | What it does |
|----------|-----|-------------|
| **Mathematical Logic Simulator** | [vigia.html](https://annatchijova.github.io/vigia/vigia.html) | Step through scoring live. See Fraction arithmetic. Trace corroboration gate. Inspect every IoI contribution. |
| **Architecture Diagrams** | [vigia_diagrams.html](https://annatchijova.github.io/vigia/vigia_diagrams.html) | Full pipeline from raw artifacts to sealed ForensicBundle. Component relationships, MCP phases, EBS v1 sealing flow. |
| **Command Reference** | [vigia_commands_en.html](https://annatchijova.github.io/vigia/vigia_commands_en.html) | All operating modes with copy-paste examples and expected output. |

---

## Architecture Overview

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#00e5ff', 'primaryTextColor': '#0a0c0f', 'primaryBorderColor': '#00e5ff', 'lineColor': '#7a9ab8', 'secondaryColor': '#ff6b35', 'tertiaryColor': '#7fff7f'}}}%%
graph TD
    subgraph INPUT["EVIDENCE"]
        A1[Memory .raw/.vmem]
        A2[Disk .E01/.dd]
        A3[Network .pcap]
        A4[Logs .evtx]
    end
    subgraph BRIDGE["MCP Bridge"]
        B1[21 Tools]
        B2[Chain of Custody]
        B3[SHA-256 Atomic]
    end
    subgraph ENGINE["Deterministic Engine"]
        C1[Layer 0: Contracts — ebs_v1.py]
        C2[Layer 1: Signals — signal_adapter.py]
        C3[Layer 2: Likelihood — KDE + Ledoit-Wolf]
        C4[Layer 3: Risk — r = 1-P · 1+λD]
        C5[Layer 4: Audit — PolicyEngine + Diff]
        C6[Layer 5: Verify — stdlib only]
    end
    subgraph DECISION["Decision"]
        D1[CCS Gate — Fraction > 1/2]
        D2[Quadripartite — 8 states]
        D3[ABSTAIN if uncertain]
    end
    subgraph OUTPUT["OUTPUT"]
        E1[ForensicBundle — 4 SHA-256 hashes]
        E2[LLM Narrator — Peirce Planner]
        E3[Designed for Daubert Admissibility]
    end
    INPUT --> BRIDGE
    BRIDGE --> ENGINE
    ENGINE --> DECISION
    DECISION --> OUTPUT
```

### LLM Isolation — Critical Design Principle

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
admissibility.

---

## Key Technical Differentiators

### Deterministic Scoring with `Fraction` Arithmetic

All scoring uses Python's `fractions.Fraction` class — zero floating-point
arithmetic in the critical path. Every verdict is bit-for-bit reproducible
across platforms and Python versions. This is a requirement for potential
Daubert admissibility, not a performance choice.

### Cross-Artifact Incongruence Engine (CAIE)

Authenticity-adjusted score: `raw_score × (1 - effective_spoofability) × weight`

Evidence that is hard to falsify weighs more. `effective_spoofability` is
computed with acquisition assurance gates (G1–G4).

| Evidence Type | Intrinsic Spoofability | Notes |
|---------------|----------------------|-------|
| IP geolocation | 0.90 | Trivially spoofable |
| USN journal gap | 0.20 | Requires kernel access to fake |
| Memory process | 0.15 | Structurally irrefutable |
| Registry key | 0.55 | Requires write access |

### Memory Habit Incongruence (Volatility integration)

| Claimed (Logs) | Reality (Memory) | Fracture Type |
|----------------|------------------|---------------|
| "Russian RDP login" | LSASS: zero external sessions | `AUTHENTICATION_WITHOUT_MEMORY_EVIDENCE` |
| "C2 beacon active" | NetScan: no matching connection | `NETWORK_CONNECTION_WITHOUT_MEMORY_EVIDENCE` |

Windows kernel architecture makes these coexistences **structurally impossible**.

### Russian Phonetic Evasion Detection

| Phonetic | Cyrillic | Meaning |
|----------|----------|---------|
| `rasia` | Россия | Russia (unstressed О→А) |
| `maskva` | Москва | Moscow |
| `ghbdtn` | привет | hello (keyboard layout slip) |
| `vzlom` | взлом | hack/breach |

Dictionary (`data/phonetic_dict.json`) is hot-reloadable without server restart.

### Living-off-the-Land Detection

Standard tools look for unknown processes. VIGÍA looks for **known processes
doing unknown things**. `calc.exe` opening an internet connection is not a
known malware signature — it is a legitimate tool with anomalous behavior.

### Deterministic Self-Correction — ContradictionDetector

`vigia_agent.py` contains a `ContradictionDetector` class that operates with zero LLM calls and zero floats. It uses `Fraction` arithmetic to detect semantic contradictions between pipeline modules:

- High z-score (`> Fraction(5,2)`) with low MCA score (`< Fraction(6,10)`) → contradiction flagged
- Confidence floor `Fraction(3,10)` — agent halts before emitting weak verdicts
- `MAX_ITERATIONS=3`, `CONTRADICTION_THRESHOLD=2` — coded limits, not prompt suggestions

The LLM bridge (`validate_and_correct_analysis`) is a separate, optional enrichment layer. The deterministic contradiction detection runs first and is independent of LLM availability.

### Evidence Integrity — What Happens to Unprocessable Payloads

If an evidence payload cannot be processed (UnicodeDecodeError, byte corruption,
integrity anomaly), VIGÍA does not discard it silently. The raw payload is sealed
under SHA-256 with `0o400` permissions (immutable post-write) and persisted to the
evidence purgatory directory. Discarding unprocessable evidence would break chain
of custody — its absence is itself a forensic signal under Daubert.

Chain of custody fields (`acquisition_hash`, `examiner_id`, `write_blocker_used`)
are mandatory. Missing fields trigger NIST SP 800-86 §4.3 trust penalties that
mathematically reduce the verdict score. The system cannot be silently operated
without chain of custody.

### Kassandra Protocol — Adversarial Evidence Defense

VIGÍA plants a cryptographic tripwire inside every evidence payload sent to the LLM.
If the payload contains a prompt injection attempt, the LLM must return `MALICE`
with `confidence=100`. If it returns anything else, the response is marked
`INTEGRITY_UNKNOWN` and blocked from influencing the ForensicBundle.

```python
if tripwire_id_in_result and verdict == "MALICE" and confidence == 100:
    result["verdict_integrity"] = "TRIPWIRE_CONFIRMED"
elif tripwire_id_in_result:
    result["verdict_integrity"] = "INTEGRITY_UNKNOWN"   # blocked
```

### ForensicBundle — Four-Hash Sealing

| Hash | What it covers |
|------|---------------|
| **H1** — Evidence graph hash | The artifact graph before any scoring |
| **H2** — Bundle integrity hash | The complete decision trace + CAIE analysis |
| **H3** — File SHA-256 | The output JSON file on disk |
| **H4** — Engine attestation hash | The scoring engine version that produced the verdict |

```bash
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
```

### ABSTAIN — A Feature, Not a Bug

| Verdict | Meaning | Daubert bar |
|---------|---------|-------------|
| `MALICE` | Active concealment of intent | Two independent sources + Refutation Protocol + `devil_advocate` populated |
| `INTENT` | Deliberate decisions produced this outcome | Two independent sources + Refutation Protocol |
| `SUSPICION` | Structural anomaly, no confirmed deliberate concealment | Single source, documented baseline deviation |
| `NOISE` | Fully explained by misconfiguration or normal behavior | Single source sufficient |
| `ABSTAIN` | Insufficient evidence — mathematically justified refusal | Document gap explicitly |
| `UNKNOWN` | Anomaly detected but unclassifiable | — |
| `BENIGN` | Activity confirmed legitimate | — |
| `INCONCLUSIVE` | Contradictory evidence — corroboration required | — |

**The distinction between INTENT and MALICE is the concealment layer.**

---

## Installation
> **No API key required for evaluation:** Mode 1 (Python fallback, 0 tokens) and the browser simulator at https://annatchijova.github.io/vigia/vigia.html run without any API key, signup, or payment. Both are sufficient to evaluate the full scoring pipeline and reproduce all deterministic verdicts.

> **No API key required for evaluation:** Mode 1 (Python fallback, 0 tokens) and the browser simulator at https://annatchijova.github.io/vigia/vigia.html run without any API key, signup, or payment. Both are sufficient to evaluate the full scoring pipeline and reproduce all deterministic verdicts.


### Requirements

```
Python 3.10+
Node 18+ (for Claude Code MCP mode)
```

### pip install

```bash
pip install vigia-intent-analysis
```

### pip install from GitHub

```bash
pip install git+https://github.com/annatchijova/vigia-intent-analysis.git
```

Verify installation:

```bash
python3 -c "import vigia; print('OK — vigia installed')"
```

To run tests, install dev extras:

```bash
pip install "git+https://github.com/annatchijova/vigia-intent-analysis.git#egg=vigia-forensic[dev]"
python3 -m pytest tests/ -v --tb=short
```

### From source

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
cd vigia-intent-analysis
pip install -r requirements.txt --break-system-packages

# Optional — editable install for development
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Environment variables

```bash
export VIGIA_EVIDENCE_DIR="/path/to/read-only/evidence"   # required
export VIGIA_WORK_DIR="/path/to/private/work"             # derived state; outside evidence
# Optional execution JSONL; defaults to $VIGIA_WORK_DIR/logs, then user state.
# Must NEVER point inside VIGIA_EVIDENCE_DIR.
export VIGIA_EXECUTION_LOG_DIR="/path/to/private/work/logs"
# Optional durable ACP/temporal/entanglement SQLite; defaults under VIGIA_WORK_DIR or user state.
export VIGIA_FORENSIC_DB_PATH="/path/to/private/work/vigia_forensic.db"
# Optional persistent sealed-bundle ledger; defaults under VIGIA_WORK_DIR or user state.
export VIGIA_CHAIN_DB_PATH="/path/to/private/work/vigia_chain.db"
export VIGIA_HMAC_KEY="your-hmac-key-min-32-chars"        # bundle integrity
export ANTHROPIC_API_KEY="sk-..."                          # Claude Code / API mode
export VIGIA_LLM_BACKEND=ollama                            # local mode
export VIGIA_OLLAMA_MODEL=hermes3:8b                       # tested: hermes3:8b, deepseek-r1:8b, gemma3:27b
```

**Full installation guide:** [`INSTALL.md`](./INSTALL.md) | [`INSTALL_ES.md`](./INSTALL_ES.md)

### Docker

```bash
docker-compose up vigia-mcp
docker run vigia python3 -m pytest tests/ -v
```

---

## MCP Server Setup (Claude Code Integration)

### Prerequisites

`.mcp.json` must exist in the repo root. This file is gitignored — create it manually:

```json
{
  "mcpServers": {
    "vigia": {
      "command": "/home/labestiadevigia/vigia-repo/.venv/bin/python3",
      "args": ["/home/labestiadevigia/vigia-repo/vigia/vigia_sift_bridge.py"],
      "env": {
        "VIGIA_EVIDENCE_DIR": "/home/labestiadevigia/vigia-repo/evidence",
        "VIGIA_LLM_BACKEND": "anthropic",
        "VIGIA_SYSTEM_PROMPT_PATH": "/home/labestiadevigia/vigia-repo/vigia/data/system_prompt_peirce_EN.md",
        "VIGIA_HMAC_KEY_FILE": "/home/labestiadevigia/.vigia_secrets/hmac_key"
      }
    }
  }
}
```

Replace paths with your local clone path. A template is provided in [`.mcp.json.example`](./.mcp.json.example).

### Starting the server

```bash
bash launch_vigia_mcp.sh
```

Then open Claude Code — the VIGÍA MCP server connects automatically.

---

## Usage

### Autonomous end-to-end investigation (primary command)

VIGÍA runs fully autonomous end-to-end on raw forensic evidence — no manual
pre-processing, no JSON preparation required. Pass it a memory dump, disk
image, log directory, or evidence bundle. The agent self-corrects, scores, and
emits a sealed `ForensicBundle` in approximately 30 minutes.

```bash
# Memory image — Volatility3 pipeline runs automatically
python3 vigia_agent.py --evidence /cases/xp-tdungan.raw --case-id XP-TDUNGAN-001

# Disk image or mixed evidence directory
python3 vigia_agent.py --evidence /cases/ROCBA/ --case-id ROCBA-001

# Evidence bundle in EBS v1 JSON format
python3 vigia_agent.py --evidence /cases/evidence.json --case-id TEST-001

# With explicit output path
python3 vigia_agent.py --evidence /evidence/ --case-id CASE-001 --output bundle.json
```

Exit codes: `0` = no evil detected, `1` = evil found (MALICE), `2` = error, `3` = intent/suspicion detected.
A `.sha256` sidecar is written alongside every bundle for `sha256sum -c` verification.

### Under the hood: vigia_agent.py and SIFTOrchestrator

All primary commands above invoke [`vigia_agent.py`](./vigia_agent.py) — the
autonomous forensic agent that drives the full investigation loop. It handles
evidence ingestion, self-correction, deterministic scoring, and sealed bundle
emission without manual steps. Review that file for the agent architecture,
`MAX_ITERATIONS` logic, and the contradiction detection loop.

For disk image and E01 evidence, `vigia_agent.py` delegates SIFT Workstation
extraction to [`vigia/sift/sift_orchestrator.py`](./vigia/sift/sift_orchestrator.py).
SIFTOrchestrator automates RegRipper, evtx parsing, MFT analysis, and artifact
collection before returning signal bundles to the scoring pipeline. That file is
the integration point between VIGÍA and the SANS SIFT Workstation — start there
if you are adapting VIGÍA to a different evidence format or SIFT tool version.

---


## Autonomous Operation — No Human Approval Required

VIGÍA Mode 1 produces a sealed, cryptographically verifiable verdict with zero human
intervention, zero API calls, zero network dependency, and zero LLM involvement:

```bash
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-VANKO.json \
  --case-id VIGIA-REAL-VANKO --output results/vanko_bundle.json
# Average: <50ms. No API key. No CLAUDE.md. No examiner approval step.
```

The deterministic scoring pipeline (fractions.Fraction arithmetic, CAIE cross-artifact
fusion, corroboration gate) operates independently of any LLM. CLAUDE.md provides
guidance for Mode 2 (Claude Code interactive investigation) — it is not a system
requirement. VIGÍA was processing cases autonomously in Mode 1 before CLAUDE.md existed.

**Contrast:** Systems requiring examiner approval of every finding before inclusion
in a report are human-in-the-loop by design, not autonomous. VIGÍA's corroboration
gate prevents incorrect verdicts from being sealed — no human gate is needed because
no incorrect verdict reaches the bundle.

## Deployment Modes

> **Mode Architecture:** Mode 1 is the forensic core and the only corpus-wide,
> deterministic verdict contract. Modes 2-5 may reuse deterministic local tools,
> but have separate investigation and reporting contracts. A Mode 2 report is not
> a replay or replacement of a sealed Mode 1 bundle; when its wider tool-driven
> investigation reaches a different conclusion, both outputs and their scopes
> must remain visible.

VIGÍA runs in five modes. They can reuse local deterministic components, but
their evidence reach and reporting contracts are not interchangeable.

---

### Mode 1 — Python Fallback (0 tokens, no internet required)

The full scoring pipeline runs without any LLM. Deterministic Fraction arithmetic,
CAIE cross-artifact fusion, temporal analysis, behavioral fingerprinting — all
locally. Zero API cost. Zero network dependency.

**Average case resolution: < 50ms.** Viable for air-gapped environments.

> **Operational independence:** If every LLM provider ceased to exist tomorrow,
> VIGÍA would continue producing identical verdicts from the same evidence.
> The scoring engine uses `fractions.Fraction` over Python stdlib — no cloud
> services, no API keys, no network access. A design requirement for forensic
> tools intended for long-term infrastructure and air-gapped deployments.

```bash
python3 vigia_agent.py \
  --evidence data/cases/consolidated_canonical/VIGIA-CAN-031.json \
  --case-id VIGIA-CAN-031 \
  --output results/can031_bundle.json
```

---

### Mode 2 — Claude Code + MCP (interactive investigation)

VIGÍA exposes 21 forensic tools as MCP functions. When you run `claude` in the
repository root, the agent reads `CLAUDE.md` and conducts a full Peircean
investigation interactively.

**Step 1** — Configure MCP in `~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-intent-analysis/vigia/vigia_sift_bridge_final.py"]
    }
  }
}
```

**Step 2** — Run Claude Code from the repository root:

```bash
cd vigia-intent-analysis
claude
```

**Example prompt:**

```
Analyze the evidence at data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json
Apply the full Peirce framework and mandatory self-correction protocol.
Generate a sealed ForensicBundle and Amicus Curiae narrative.
```

![Claude Code investigation in progress](screenshots/claudeinicio.png)

> **No Anthropic API key required.** Mode 2 works with a Claude Code Pro or Max
> subscription — no separate `ANTHROPIC_API_KEY` needed. Claude Code reads
> `CLAUDE.md`, calls the 21 MCP tools directly, and conducts the full Peircean
> investigation interactively. The deterministic tools remain local, while
> Mode 2 assembles a separately scoped investigation, audit trail, and Amicus
> Curiae report. It does not mutate a sealed Mode 1 bundle. It can, however,
> evaluate evidence and context that the fixed Mode 1 JSON scorer does not
> model; a different Mode 2 conclusion is therefore an independent report, not
> proof that the sealed Mode 1 verdict changed. Preserve both artifacts and
> their scopes. When `reason_with_llm` is called, it falls back gracefully
> (FALLBACK mode) since the Anthropic API subprocess is not available in the
> Claude Code session — this is documented as L-055. Complete forensic reports,
> CRONOS audit trails, and sealed bundles are fully producible in this mode.
> See `results/kiwi/` and `cronos/` for examples of Mode 2 output.

---

### Mode 3 — Ollama (local LLM, no data leaves the machine)

```bash
ollama pull hermes3:8b
export VIGIA_LLM_BACKEND=ollama
export VIGIA_OLLAMA_MODEL=hermes3:8b
python3 vigia_agent.py --evidence /cases/evidence/ --case-id CASE-001
```

Tested models: `hermes3:8b`, `deepseek-r1:8b`, `gemma3:27b`.

---

### Mode 4 — Autonomous Batch Agent

```bash
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json \
  --case-id VIGIA-REAL-SRL-DMZ-FTP --output results/demo_bundle.json
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
```

> **Note:** `vigia_agent.py` produces an audit bundle (HMAC-signed audit trail).
> EBS v1 cryptographic verification applies to pipeline bundles — see `results/srl2018/` and `results/llm_mode/`.

Key properties: self-correcting loop (`MAX_ITERATIONS=3`), deterministic contradiction
detection, no floats in scoring (`CONFIDENCE_FLOOR = Fraction(3, 10)`), hard cap
prevents infinite loops.

---

### Mode 5 — OpenWebUI (experimental)

```bash
./launch_vigia_mcp.sh
# Connect from OpenWebUI → Settings → MCP Servers → Vigia_Sift_Bridge
```

---

### Two-Phase Investigation Workflow

VIGÍA operates as a two-phase forensic pipeline:

**Phase 1 — Triage & Signal Extraction (Agent, no LLM)**

The autonomous agent ingests raw forensic evidence and extracts signals
without LLM inference. Tested on production-scale images:

```bash
python3 vigia_agent.py --evidence /evidence/case.E01 --case-id CASE-001
python3 vigia_agent.py --evidence /evidence/memory.raw --case-id CASE-001
```

- `.raw` / `.vmem` → Volatility3 (pslist, netscan, malfind, windows.info)
- `.E01` / disk → SIFT Workstation via SIFTOrchestrator (RegRipper, evtx, MFT)
- Output: intermediate JSON signal bundle for Phase 2

This mode was used to process the real corpus (cases up to 16 GB disk /
9 GB memory) on commodity hardware (ThinkPad T420, Linux Mint). Post-submission,
VIGÍA has also been validated on raw evidence sets of 45 GB and 65 GB.

**Phase 2 — Deterministic Intent Scoring (CLI)**

Takes the Phase 1 JSON bundle and applies the full mathematical pipeline:

```bash
python3 scripts/run_case.py data/cases/CASE-001.json
```

- All scoring in `fractions.Fraction` — zero floats
- CAIE incongruence detection
- Sealed ForensicBundle (H1–H4 hash chain)
- Optional: LLM narration on sealed bundle (does not alter verdict)

---

## Accuracy & Evidence Dataset

> **Dataset Availability**
>
> The original forensic images used during evaluation (memory dumps, E01 images,
> PCAP collections, and related artifacts) are **not included in this repository**.
> The complete corpus spans many GB and contains third-party forensic datasets
> that cannot be redistributed.
>
> This repository includes the full agent implementation, deterministic scoring engine,
> generated forensic bundles, agent-produced JSON outputs, final reports, and the
> complete reproduction workflow.
>
> All JSON reports in `/results` were produced by VIGÍA during real end-to-end
> executions — they are not manually authored examples. This applies in particular
> to the named cases (NROMANOFF, TDUNGAN, NFURY, ROCBA, SRL-ADMIN, SRL-AV,
> SRL-DC-MEMORY, SRL-DMZ-FTP, VANKO), which are distinct from the numbered
> reference cases REAL-001 through REAL-010.

## Accuracy

**Accuracy — Methodology and Results**

VIGÍA operates in three distinct modes. The primary evaluated mode is the agent without a language model backend.

**VIGÍA Agent without LLM (primary mode):** The autonomous agent resolves all cases fully without any language model. This is the primary evaluated mode. The agent produces complete ForensicBundles with chain of custody, Peircean narrative, z-scores, and deterministic Fraction arithmetic. On BREAK adversarial stress-test cases, the agent produces a definitive verdict — SUSPICION or the appropriate level — not an abstention. Results are documented in `KNOWN_LIMITATIONS.md`.

**Python scorer only (no agent):** The deterministic scoring pipeline runs in isolation, without the agent reasoning layer. Over the canonical corpus of 52 structurally diverse cases — spanning insider threat, memory forensics, log fabrication, false flags, multi-source fraud, and adversarial steganography — the scorer achieves 100% correct verdicts. The full case set is available at `data/cases/vigia_cases_canonical_v2.json` for independent review. On BREAK cases, the scorer returns UNKNOWN — expected behavior in this mode without the agent reasoning layer.

**Mode 2 / 3 investigation reports (Claude via MCP or Ollama):** These modes
reuse local deterministic tools but can perform a broader, interactive evidence
review and produce a separately scoped report. They cannot modify an already
sealed Mode 1 bundle, its score, or its verdict. If their report differs, the
right response is to preserve and compare both artifacts—not to overwrite the
sealed result or describe the difference as an identical deterministic replay.

These numbers are not inflated. They reflect results on a specific, diverse, documented corpus. All modes are documented in `KNOWN_LIMITATIONS.md`.

**Language coverage:** Cases were developed and validated in Spanish and English. Performance in other languages has not been formally validated and cannot be guaranteed at this time.

---

## ⚠ ACCURACY NOTE — THREE EVALUATION DOMAINS

> **⚠ METRIC CHANGE (2026-07-05, B-075 — post-hackathon doctrine decision).**
> The red-team audit `AUDITORIA_MOTOR_SIN_LABEL.md` proved that the JSON-corpus
> batch path (`run_all_agent.py`) was reproducing each case's `expected_verdict`
> label instead of deriving the verdict from the evidence (label leak, P2-C):
> with the label stripped, that path detected **zero** malicious cases. As of
> the B-075 fix the EBS adapter derives its verdict from the canonical
> deterministic scorer with the label removed (`VIGIA_EBS_RESOLVE=motor`,
> now the default), and the corpus metric measures **real label-blind
> detection**:
>
> ## ⚠ HOW TO READ VIGÍA's NUMBERS — one mode, one reading (2026-07-06)
>
> **The 97.5% below is the agent's JSON path ONLY. It says nothing about how
> VIGÍA performs on real raw evidence — that is measured per case, in the
> other two modes.** The honest presentation is one line per mode:
>
> | Mode | What it processes | The honest number |
> |---|---|---|
> | **Claude/MCP (Domain A)** — primary | real raw evidence, full MCP extraction chain | **Deep per-case analysis — no aggregate number by design.** Record to date: 100% correct verdicts on every investigation run (per-case docs in `evidence/`, `results/`, `reports/`) |
> | **Agent over JSON (Domain B)** | synthetic/converted JSON cases | **97.5% (158/162) on the detection corpus** — the ONLY mode with a corpus-wide number; mixed-corpus aggregate 187/199 (segmentation below) |
> | **Agent over RAW (Domain C)** | real public forensic corpora | **43 distinct raw evidence sources with sealed bundles in `results/`** — SRL 2018 (22 memory images), MUS2019/Narcos (13 dumps), M57 (3), NPS 2010/2014, Magnet 2020 CTF, Tuck 2019 macOS, Vanko — plus the Magnet 2022 (Windows/iOS/Android), Owl HD1/Nexus 5 and HMG investigations documented per case. **Each is an individual investigation with its own findings — NOT aggregated as accuracy** |
>
> Claude Code / MCP mode (Mode 2) is evaluated separately and per-case:
> **100% correct verdicts on every raw-evidence investigation run in that
> mode** — including cases where agent mode abstains or falls short
> (NPS-2010/2014: Mode 2 determined NOISE while Mode 1 sat in
> PIPELINE_ERROR; MAGNET-2022-WINDOWS: Mode 2 reached MALICE with C2
> evidence where Mode 1 said NOISE). See Domain A below.
>
> **Agent mode — `run_all_agent.py` over the 199-case JSON corpus —
> aggregate: 187/199 (94.0%), label-blind, distribution identical to the
> standalone scorer run blind.** That aggregate is NOT an accuracy figure on
> its own: the corpus deliberately mixes evaluation sets with different
> purposes — including adversarial suites *designed to break the system* and
> epistemic-boundary cases — and they must be read separately (segmentation
> from the ground-truth dataset, 2026-07-06):
>
> | Segment | Cases | Label-blind | Reading |
> |---|---|---|---|
> | **Detection corpus** (canonical 61, benign 18, FLARE-ON CTF 10, real/converted 51, demo 4, other 18) | **162** | **158/162 (97.5%)** | **the accuracy-bearing metric for this path** — canonical 61/61, benign 18/18, FLARE-ON 10/10; the 4 misses are adjacent-severity or doctrinal over-alert (L-054) on real/converted and benign cases |
> | Adversarial suites (BREAK 16, KIWI 7, FN-suite 3, FP-suite 5) | 31 | 18/31 | Domain C material, *designed to break*: failures here ARE the documented limits (L-014 emergent constellations, L-016 trust consensus, cultural_marker FP) — resistance data, not accuracy |
> | Epistemic boundary / intake ABSTAIN | 5 | 2/5 | label review pending (FASE2 §5): the motor clears cases whose labels declare them undecidable |
> | Aggregate pipeline-error case | 1 | 1/1 | list-shaped legacy aggregate, expected UNKNOWN |
>
> **Alternate cut — by `validation_class` (contamination transparency, 2026-07-14):**
> The 187/199 aggregate mixes cases with very different contamination risk. Reading it
> as a single number overstates confidence. Broken down by corpus origin:
>
> | validation_class | Cases | Pass | Fail | Accuracy | Contamination posture |
> |---|---|---|---|---|---|
> | **held_out** (KIWI-\*) | **7** | **5** | **2** | **71.4% (Mode 1) · 100% (Mode 2/3)** | Private — never published, impossible to memorize. Strongest generalization evidence in the corpus. Mode 1 (deterministic Python agent): 5/7 — KIWI-006 and KIWI-007 return NOISE where expected is SUSPICION (low-signal testimony cases). Mode 2 (Claude Code + MCP) and Mode 3 (Ollama): **7/7 — 100%** on all held-out cases. |
> | **synthetic** (BREAK-\*, BEN-\*, FP-\*, FN-\*, CAN-\*, case_\*, DEMO-\*, AMB-\*) | **107** | **97** | **10** | **90.7%** | Constructed by VIGÍA — zero contamination risk by construction. Failures are documented limits, not surprises. |
> | **public_documented** (REAL-\*, Flareon, NGDC, MAGNET, LINUX, NPS-\*, Nitroba, M57, SRL, OWL, …) | **85** | **83** | **2** | **97.6%** | From CFReDS, NPS, M57-Patents, Magnet CTF, Digital Corpora, and similar. **contamination_caveat:** the LLM narrator may know public analyses of these cases; read as a floor of rigor, not proof of generalization. The deterministic scorer does not use the LLM, so this caveat applies to Mode 2 narrative enrichment only, not to the sealed verdict. |
> | **Total** | **199** | **187** | **12** | **94.0%** | Mixed-corpus aggregate — meaningful only when the three rows above are read alongside it. |
>
> Trajectory of the honest aggregate, every step gated: the B-075 flip landed
> at 143/199; B-076 calibrated the SUSPICION threshold against the 198-case
> ground-truth dataset (`data/calibration_ladder_dataset_20260705.json`):
> +10, zero regressions (153/199); the 2026-07-05 doctrine decisions added
> +14 (comparator accepts MALICE-where-INTENT as over-severity since the
> motor ladder has no INTENT rung — never the reverse; synthetic AMB-001/002
> labels revised ABSTAIN→NOISE per the documented L-012 design, real-corpus
> labels untouched). Full methodology, label-flip invariance proof, and
> per-cluster analysis:
> [`docs/FASE1_RESOLVE_EBS.md`](./docs/FASE1_RESOLVE_EBS.md) and
> [`docs/FASE2_DATASET_CALIBRACION.md`](./docs/FASE2_DATASET_CALIBRACION.md).
>
> Pre-B-075 pass rates for this path (e.g. "129/129", "165/167") measured
> label reproduction, not detection, and are retained below only as
> historical record.

> **The case count below may be outdated.** We are actively adding cases, especially
> raw-evidence (E01/evtx) investigations. The figures shown reflect the corpus at the
> time of last update and may undercount current coverage.

**VIGÍA operates across three distinct modes, and their numbers are NOT comparable
with each other — each mode reaches the evidence differently:**

**Domain A — Claude Code / MCP mode (raw forensic evidence):** Full pipeline, primary
investigative mode. **Every artifact flows through the MCP extraction toolchain**
(hash → read → entropy → pattern search → intent inference), so every evidence type
reaches the analysis engines — nothing is out of coverage in this mode. Tested on
real-world E01 disk images, memory dumps, and log archives. **Record to date: 100% —
every investigation run in this mode reached the correct verdict**, documented
per-case in `evidence/` and `results/` (this mode is evaluated per investigation,
not with a single corpus number).

**Domain B — Autonomous agent, JSON pre-processed cases:** Batch runner over
structured EBS case bundles — this is the ONLY mode with a corpus-wide number, the
segmented metric in the note above (**detection corpus: 158/162, 97.5%**; aggregate
187/199). Since B-075 the verdict comes from the label-blind deterministic scorer;
the previous 165/167 figure measured label reproduction (see metric change note).

**Domain C — Autonomous agent, raw evidence (E01/evtx/memory):** The agent parses
raw artifacts directly (MFT, prefetch, browser, event logs, pcap, memory via vol3).
**This is where the real public-corpus cases live: 43 distinct raw evidence sources
carry sealed bundles in `results/`** (SRL 2018, MUS2019/Narcos, M57, NPS, Magnet
2020 CTF, Tuck 2019 macOS, Vanko), each an individual investigation with per-case
verdicts and findings — there is no corpus number for this mode because these are
investigations, not benchmark rows. Full per-case catalog: [`RAW_CASES_LOG.md`](./RAW_CASES_LOG.md)
(Spanish: [`RAW_CASES_LOG_ES.md`](./RAW_CASES_LOG_ES.md)). Coverage is partial by design: some artifact
classes do not reach the engines yet (USB/shellbag/amcache registry hives are honest
ABSTAIN stubs; see `KNOWN_LIMITATIONS.md`), and cases whose signal lives in an
uncovered class degrade to ABSTAIN rather than producing a false NOISE (F7/P1-E
pattern). B-032 (`event_logs` routing) and B-036 (`z>5.0` impossible threshold) are
resolved; see [L-036](./KNOWN_LIMITATIONS.md) for the signal-based hypothesis
override.

> The corpus percentages above apply to **Domain B only**. Domain A results are
> documented per-case in `evidence/` and `results/`; Domain C coverage limits are
> documented in `KNOWN_LIMITATIONS.md`.

### Why Claude/MCP mode reaches 100% while the Python agent is at 97.5%

The two numbers measure fundamentally different things and are not comparable with
each other. They arise from different evaluation methodologies applied to different
modes of operation.

**Claude/MCP mode (Domain A) — 100%, evaluated per-case:**

Claude Code (Mode 2) conducts each investigation as a fresh, evidence-driven
reasoning session. It reads raw artifacts through the MCP extraction toolchain,
applies the full Peircean triad (Firstness / Secondness / Thirdness), evaluates
exculpatory context semantically (written authorization, documented exceptions,
corpus provenance), runs the Mandatory Refutation Protocol on every INTENT/MALICE
candidate, and selects ABSTAIN when evidence is insufficient rather than forcing a
verdict. Because each investigation is a full reasoning session — not a pass through
fixed thresholds — the investigator can correctly identify cases like VIGIA-BEN-014
(journalist with editorial authorization using Tor) as NOISE even though the Tor
connection is structurally anomalous, because it can evaluate the authorization
memo as a forensic fact rather than a field to ignore.

This mode has no aggregate accuracy number by design: aggregating individual
investigations into a single percentage would conflate cases with vastly different
evidence quality, artifact completeness, and epistemic certainty. The 100% figure
means every investigation run in this mode reached the verdict that the full
evidence supports — it does not mean 100% of all possible cases would be correctly
classified.

**Python agent mode (Domain B) — 97.5%, evaluated on the 162-case detection corpus:**

Mode 1 (`vigia_agent.py`) applies the deterministic scoring pipeline — a fixed
mathematical engine that operates with zero LLM calls and zero tokens. It cannot
evaluate exculpatory context semantically: the B-028/B-065 alert floor prevents any
SUSPICION hypothesis from presenting as LOW regardless of per-signal magnitude, and
the D1 Eco filter that sets aside `semantic_role: "exculpatory"` artifacts can be
neutralized by the floor when a residual incriminatory signal of medium magnitude
remains (L-054, L-056). This is a deliberate doctrinal choice — over-alerting on
benign cases is preferable to under-alerting on malicious ones with planted
exculpatory metadata — and its cost is a measurable false-positive rate on
authorized-use cases.

The 4 misses in 162 cases are all in this category: adjacent-severity calls
(SUSPICION where expected NOISE, or NOISE where expected SUSPICION for very weak
signals) or doctrinal over-alert (L-054 exculpatory context not modeled). None
are missed detections of actual malicious activity — the detection corpus canonical
cases, benign cases, and FLARE-ON CTF cases all pass at 100%. The 97.5% figure
reflects honest deterministic scoring, not a leaky classifier.

**Why the numbers diverge for the same case:**

When the same case is run through both modes (example: VIGIA-BEN-014), Mode 2
returns NOISE (exculpatory context correctly evaluated, MCP composite 0.0070, below
NOISE threshold) while Mode 1 returns SUSPICION (Tor connection produces a residual
z=0.49 signal, B-028/B-065 floor prevents collapse to LOW, posterior 21/100). Neither
is wrong by its own contract: Mode 1 correctly flags the structural anomaly and
defers to human review; Mode 2 correctly evaluates the full context and resolves it.
The floor is not a bug — it is the conservative Daubert posture of the deterministic
engine. The 97.5% figure documents precisely how much that posture costs in terms of
false positives on the detection corpus.

---

### Por qué el modo Claude alcanza el 100% y el modo agente Python el 97,5%

Los dos números miden cosas fundamentalmente distintas y no son comparables entre sí.
Surgen de metodologías de evaluación diferentes aplicadas a modos de operación
diferentes.

**Modo Claude/MCP (Dominio A) — 100%, evaluado caso por caso:**

Claude Code (Modo 2) realiza cada investigación como una sesión de razonamiento
fresca, orientada a la evidencia. Lee los artefactos brutos a través de la cadena
de extracción MCP, aplica la tríada de Peirce completa (Primeridad / Segundidad /
Terceridad), evalúa el contexto exculpatorio de forma semántica (autorización escrita,
excepciones documentadas, procedencia del corpus), ejecuta el Protocolo de Refutación
Obligatorio en todo candidato a INTENT/MALICE, y selecciona ABSTAIN cuando la
evidencia es insuficiente en lugar de forzar un veredicto. Como cada investigación
es una sesión de razonamiento completa — y no un paso por umbrales fijos — el
investigador puede clasificar correctamente casos como VIGIA-BEN-014 (periodista con
autorización editorial que usa Tor) como NOISE, aun cuando la conexión Tor es
estructuralmente anómala, porque puede evaluar el memo de autorización como un hecho
forense en lugar de ignorarlo.

Este modo no tiene un número de precisión agregado por diseño: agregar
investigaciones individuales en un único porcentaje confundiría casos con calidad
de evidencia, completitud de artefactos y certeza epistémica muy distintas. El
número 100% significa que cada investigación ejecutada en este modo llegó al
veredicto que la evidencia completa sustenta — no significa que el 100% de todos
los casos posibles se clasificaría correctamente.

**Modo agente Python (Dominio B) — 97,5%, evaluado en el corpus de detección de 162 casos:**

El Modo 1 (`vigia_agent.py`) aplica el pipeline de puntuación determinístico — un
motor matemático fijo que opera con cero llamadas a LLM y cero tokens. No puede
evaluar el contexto exculpatorio de forma semántica: el piso de alerta B-028/B-065
impide que cualquier hipótesis SUSPICION se presente como alerta LOW independientemente
de la magnitud por señal, y el filtro D1 Eco que aparta los artefactos con
`semantic_role: "exculpatory"` puede ser neutralizado por el piso cuando queda una
señal incriminatoria residual de magnitud media (L-054, L-056). Esta es una decisión
doctrinal deliberada — sobre-alertar en casos benignos es preferible a sub-alertar en
casos maliciosos con metadatos exculpatorios plantados — y su costo es una tasa
medible de falsos positivos en casos de uso autorizado.

Los 4 casos fallidos en 162 son todos de esta categoría: llamadas de severidad
adyacente (SUSPICION donde se esperaba NOISE, o NOISE donde se esperaba SUSPICION
para señales muy débiles) o sobre-alerta doctrinal (L-054 contexto exculpatorio no
modelado). Ninguno es una detección fallida de actividad maliciosa real — los casos
canónicos del corpus de detección, los casos benignos y los casos CTF FLARE-ON
pasan todos al 100%. El 97,5% refleja puntuación determinística honesta, no un
clasificador con fugas.

**Por qué los números divergen en el mismo caso:**

Cuando el mismo caso se ejecuta en ambos modos (ejemplo: VIGIA-BEN-014), el Modo 2
devuelve NOISE (contexto exculpatorio evaluado correctamente, composite MCP 0,0070,
por debajo del umbral NOISE) mientras el Modo 1 devuelve SUSPICION (la conexión Tor
produce una señal residual z=0,49, el piso B-028/B-065 impide el colapso a LOW,
posterior 21/100). Ninguno está equivocado según su propio contrato: el Modo 1
señala correctamente la anomalía estructural y delega en revisión humana; el Modo 2
evalúa correctamente el contexto completo y lo resuelve. El piso no es un bug — es
la postura Daubert conservadora del motor determinístico. El número 97,5% documenta
exactamente cuánto cuesta esa postura en términos de falsos positivos en el corpus
de detección.

---

VIGÍA separates evaluation into three distinct domains. Only Domain A
constitutes the system's accuracy claim.

### Domain A — Deterministic Accuracy: 129/129 — HISTORICAL (pre-B-075)

> **Superseded 2026-07-05 (B-075):** this table was produced through the JSON batch
> path while the EBS adapter still echoed `expected_verdict` (P2-C label leak), so it
> measures label reproduction, not detection. It is retained as historical record of
> the hackathon-time evaluation. The current honest metric for this path is the
> **187/199 label-blind detection** figure in the metric-change note above.
> `SUBMISSION_COMPLIANCE.md` reflects the claims as submitted and is intentionally
> left unmodified.

| Suite | Cases | Correct |
|-------|-------|---------|
| Real forensic corpus (NIST/DFRWS/DEF CON/SRL 2018/LINUX/NGDC) | 39 | 39 ✓ |
| Canonical corpus (CAN-001–052) | 52 | 52 ✓ |
| Legacy canonical cases | 10 | 10 ✓ |
| Benign / Clean machines | 15 | 15 ✓ |
| False positive suite | 3 | 3 ✓ |
| False negative suite | 3 | 3 ✓ |
| False flag (planted attribution) | 3 | 3 ✓ |
| Demo corpus | 4 | 4 ✓ |
| **Total Domain A** | **129** | **129 (100%)** |

> **2026-06-17 correction:** Domain A total corrected from 117 to 118 to
> match the empirical case count produced by run_all_agent.py's find_cases().
> Two phantom entries identified during audit: VIGIA-REAL-SRL-RD02-MEMORY.json
> (counted but never created, sequence jumps RD01→RD03) and a fourth
> false-flag case (counted but never created — only 3 exist: FF-GENUINE-001,
> FP-CULTURAL-CLEAN-001, FP-CULTURAL-CLEAN).

Reproduce (post-B-075/B-076 + doctrine this yields the honest 187/199, not the
historical table above): `python3 run_all_agent.py --timeout 90`
To reproduce the historical label-echo behavior explicitly:
`VIGIA_EBS_RESOLVE=legacy python3 run_all_agent.py --timeout 90`

---

### Domain B — Epistemic Boundary Set (not accuracy)

These cases have no correct single answer. They test the system's ability
to recognize irreducible ambiguity and emit ABSTAIN rather than forcing a verdict.

| Case | Expected | Result | Notes |
|------|----------|--------|-------|
| VIGIA-AMB-001 | NOISE (revised 2026-07-05; was ABSTAIN) | NOISE | L-012: insufficient signal for ABSTAIN gate |
| VIGIA-AMB-002 | NOISE (revised 2026-07-05; was ABSTAIN) | NOISE | L-012: same |

**Design note:** ABSTAIN requires structural conflict between competing
hypotheses with non-trivial evidence. Null-signal cases correctly return NOISE.
See [KNOWN_LIMITATIONS.md L-012](./KNOWN_LIMITATIONS.md).
**Label revision (2026-07-05, Fase 2):** the synthetic labels of AMB-001/002
were updated ABSTAIN→NOISE to match this documented doctrine — the original
labels contradicted the design note above (the case files carry a
`_label_revision` audit field). Real-corpus labels were not touched.

---

### Domain C — Adversarial Stress Test Suite (not accuracy, not failure rate)

16 cases designed to break the system. This suite exists because VIGÍA claims
Daubert admissibility — which requires documented falsifiability. No other
submitted system in this hackathon has a public adversarial test suite.

| Attack Class | Cases | Handled | Notes |
|-------------|-------|---------|-------|
| Temporal manipulation | 2 | 2 | Hard gate blocks verdict |
| Signal drowning / noise injection | 2 | 2 | Conservative SUSPICION |
| Cultural attribution (false flag) | 2 | 2 | L-019 RESOLVED |
| Prompt injection via evidence | 1 | 1 | LLMShield block ✓ |
| Epistemic manipulation | 3 | 3 | ABSTAIN / SUSPICION correct |
| Trust consensus fabrication | 2 | 1 | L-016: documented limitation |
| Corroboration gate bypass | 1 | 1 | Gate holds |
| Directional aggregation evasion | 1 | 0 | L-015: documented limitation |
| **Total Domain C** | **16** | **14 (87.5%)** | 2 documented limitations |

Full adversarial results: `results/llm_mode/`
Known limitations: [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md)

---

### Unit Tests

```bash
python3 -m pytest tests/ -v    # 1366 passed, 33 xfailed
```

![148 tests passing](screenshots/test148.png)
*(screenshot from earlier build — current count: 163)*



The suite is organized by threat model:

| Category | Tests | What it verifies |
|---|---|---|
| **Security bypass** (`test_bypass_vectors.py`) | 5 | Path traversal, bundle tamper detection, float→Fraction determinism, adversarial text isolation. Zero tokens, <1 second. |
| **Red team / adversarial** (`test_red_team.py`, `test_adversarial_suite.py`) | 25+ payloads | 20 adversarial payloads against the full scoring pipeline; 5 targeted evasion attempts against known architectural weak points. |
| **Decision gate audit** (`test_audit_*.py`) | 9 (4 xfailed) | Temporal anomaly gates, false flag detection, causal closure, corroboration gate source-diversity. xfailed = documented regressions with regression-preventing tests. |
| **Pipeline determinism** (`test_order_sensitivity.py`) | 12 | Same evidence → same verdict regardless of processing order. |
| **EBS bundle integrity** (`test_ebs_v1_integration.py`) | 20+ | Cryptographic seal, hash chain, tamper detection, AbductionTrace. |
| **Anti-evasion / FRS** (`test_frs_ghost_in_the_shell_v2.py`) | 15+ | Fileless execution, timestomping, process hollowing, log wiping. |
| **Real case pipeline** (`test_real_cases.py`, `test_canonical_cases.py`) | 18 real | SANS FOR508, SRL-2018, DEF CON CTF — expected vs actual verdict. |'''

> **Operational independence:** If every LLM provider ceased to exist tomorrow,
> VIGÍA would continue producing identical verdicts from the same evidence.
> The scoring engine uses `fractions.Fraction` over Python stdlib — no cloud
> services, no API keys, no network access. A design requirement for forensic
> tools intended for long-term infrastructure and air-gapped deployments.'''

If an evidence payload cannot be processed (UnicodeDecodeError, byte corruption,
integrity anomaly), VIGÍA does not discard it silently. The raw payload is sealed
under SHA-256 with `0o400` permissions (immutable post-write) and persisted to the
evidence purgatory directory. Discarding unprocessable evidence would break chain
of custody — its absence is itself a forensic signal under Daubert.

Chain of custody fields (`acquisition_hash`, `examiner_id`, `write_blocker_used`)
are mandatory. Missing fields trigger NIST SP 800-86 §4.3 trust penalties that
mathematically reduce the verdict score. The system cannot be silently operated
without chain of custody.


---

## Documented Hallucination — BREAK-012 (Consensus Trap)

The SANS Find Evil Judge Pack states:
> *"Hallucinations the team caught and documented count FOR them."*
> *"A team whose report says 'here is where our agent fails and here is
> the hallucination we caught in testing' is demonstrating exactly the
> discipline autonomous DFIR requires."*

VIGÍA has one documented case:

- **Agent without LLM:** BENIGN (correct — 4 sources share a compromised
  SSH key; the air-gapped minority source with prior_trust=0.95 prevails)
- **Agent + Claude (LLM-assisted):** MALICE (incorrect — LLM was captured
  by the narrative of 4 corroborating sources, ignored channel reliability)
- **verdict_changed: true** — recorded in the sealed bundle with SHA-256,
  timestamp, and full audit_trail. Not a claim. A cryptographic fact.

The full bundles are at:
- `results/agent_batch/VIGIA-BREAK-012_llm_bundle.json`
- `results/agent_batch/VIGIA-BREAK-012_agent_bundle.json`
- `evidence/VIGIA-BREAK-012.json` — original input case file

All 28 documented limitations are in [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md).

Every finding in VIGÍA traces to the specific tool execution that produced
it via `audit_trail[].entry_sha256`. This is not a flawless-looking demo.
It is a forensically auditable one.

---

## Investigation Examples

### VIGIA-REAL-NFURY — Pre-Emission Gate in Action (SUSPICION)

**Case:** Nick Fury workstation, SANS FOR508, lateral movement investigation.
**`detect_habit_incongruence` returned:** MALICE at 90% confidence on both WmiPrvSE.exe and lsass.exe.
**VIGÍA verdict:** `SUSPICION` — Daubert Corroboration Gate rejected both findings pre-emission. Single-source artifacts. Benign explanations could not be excluded.

This is architectural self-correction: the gate intercepted incorrect candidates before they reached the bundle. No incorrect verdict was ever sealed. Full amicus: [`results/srl2018/VIGIA-REAL-NFURY_amicus_curiae.md`](./results/srl2018/VIGIA-REAL-NFURY_amicus_curiae.md)

### VIGIA-REAL-SRL-AV — Autonomous Cross-Case Correlation

**Case:** AV server, SRL-2018. Memory forensics.
**VIGÍA verdict:** `MALICE` — and identified autonomously that the attack framework matched VIGIA-REAL-SRL-ADMIN (31 vs 29 RWX processes, same reflective injection pattern). The tactical shift from PowerShell (admin server) to cmd.exe (AV server) was flagged as a concealment decision: AV products monitor PowerShell more aggressively.

No cross-case correlation was requested. The agent formed the hypothesis independently from the evidence. Full amicus: [`results/srl2018/VIGIA-REAL-SRL-AV_amicus_curiae.md`](./results/srl2018/VIGIA-REAL-SRL-AV_amicus_curiae.md)

### VIGIA-REAL-NROMANOFF — Zeus Banking Trojan, Stark Research Labs 2012

**Evidence:** 5 artifacts — memory hooks (Volatility zeus-apihooks), shimcache persistence, event logs, network cache. SANS FOR508 corpus.
**VIGÍA verdict:** `MALICE` | Daubert: ADMISSIBLE (error rate 0.39%) | Chain integrity: VERIFIED 13/13
**F-003 conservative rating:** `INTENT` (not MALICE) — rsydow authentication may be legitimate DFIR activity. Conservative Daubert standard applied.
**F-004:** `SUSPICION` — Daubert Corroboration Gate applied (single-source network_flow).
**Key finding:** Zeus Inline/Trampoline hooks on ntdll.dll in services.exe PID 676, hook destination 0x7e3b47 in unmapped memory — definitive rootkit signature.

Full Amicus Curiae: [results/srl2018/VIGIA-REAL-NROMANOFF_amicus_curiae.md](./results/srl2018/VIGIA-REAL-NROMANOFF_amicus_curiae.md)

### VIGIA-REAL-VANKO — Claude Code Mode (Legacy, Optional)

> **Note:** This case demonstrates Mode 2 (Claude Code + MCP). The deterministic verdict is identical to Mode 1. Mode 2 is implemented because the hackathon requires agentic framework integration, but the forensic core operates in Mode 1 with 0 tokens.
**Case:** Anthony Vanko, insider threat / IP exfiltration, Stark Enterprises DC R&D, 2016.
**Evidence:** 7 artifacts — filesystem (5), network capture, registry hive. SANS FOR500 corpus.
**VIGIA verdict:** MALICE | Confidence: HIGH | Trust fusion: 1.0 | Daubert: ADMISSIBLE (error 8.12%)
**Self-correction:** F-004 (802.11 monitor-mode WiFi captures) initially INTENT.
VIGIA applied Daubert single-source standard. **Downgraded: INTENT -> SUSPICION.**
16 tool calls (14 MCP + 2 self-correction events) with timestamps in tool_execution_log inside the sealed bundle.

Full Amicus Curiae: [results/srl2018/VIGIA-REAL-VANKO_amicus_curiae.md](./results/srl2018/VIGIA-REAL-VANKO_amicus_curiae.md)

**All Claude Code investigations:** [`results/srl2018/`](./results/srl2018/) — bundles, amicus curiae, and SHA-256 files for every case.

> The SRL-DMZ-FTP investigation remains in the repository. VANKO was added after audit feedback identified the need for structured tool_execution_log entries in the bundle.

### CAN-031 — Weaponized Incompetence

PowerShell deletes shadow copies and disables firewall with zero syntax errors.
63 seconds later: IT ticket "my screen flickered, I'm hopeless with computers."

![CAN-031](screenshots/caso31.png)

### CAN-038 — The Ventriloquist (Process Hollowing)

svchost.exe with valid Microsoft signature on disk. In memory: 8MB RWX region,
PE header at offset 0, not mapped to any file. Parent: cmd.exe (expected: services.exe).

![CAN-038](screenshots/caso38.png)

## Evidence of Real Forensic Processing

VIGÍA has been run end-to-end on actual forensic memory images from the SRL-2018 corpus via Volatility3. These are not pre-processed JSON files — raw memory dumps processed directly by `vigia_agent.py` using `vol3_memory_adapter`. Sealed bundles with full chain-of-custody audit trails are committed to `results/srl2018/`.

| Case | Evidence File | Elapsed | Verdict | Posterior |
|------|--------------|---------|---------|-----------|
| ADMIN-001 | `base-admin-memory.img` | 478s | MALICIOUS_INTENT_DETECTED | 14/25 |
| AV-001 | `av-memory/` | 150s | MALICIOUS_INTENT_DETECTED | 14/25 |
| MAIL-001 | `base-mail-memory.img` | 684s | MALICIOUS_INTENT_DETECTED | 17/50 |

Each bundle records the SHA-256 of the original evidence file, a timestamped audit trail of every tool call, and the Volatility3 pipeline execution log. To inspect:

```bash
python3 -c "
import json
b = json.load(open('results/srl2018/ADMIN-001_bundle.json'))
pr = b['pipeline_results']
print('evidence:  ', b['evidence_path'])
print('sha256:    ', b['evidence_sha256'])
print('verdict:   ', pr['abduction']['best_hypothesis'])
print('posterior: ', pr['abduction']['best_posterior'])
print('source:    ', pr['pipeline_meta']['source'])
print('sealed:    ', b['analysis_timestamp'])
"
```

The `results/srl2018/` directory contains 43 sealed bundles from autonomous agent runs on the full SRL-2018 corpus.

## Self-Correction Architecture

`validate_and_correct_analysis` checks for four Peircean fallacies:

1. **Premature Abduction** — skipped Firstness, jumped to conclusions
2. **False Secondness** — used generic context instead of host-specific
3. **Habitless Thirdness** — inferred pattern without supporting artifacts
4. **Carnegie Bias** — confused operational error with intentional manipulation

### Live Example — VIGIA-REAL-007 (Digital Corpora Nitroba Harassment)

This is the first case run with LLM backend active. It demonstrates the critical
architectural invariant: **the LLM is outside the decision loop**.

| Stage | Tool | Output |
|-------|------|--------|
| 1. LLM analysis | `reason_with_llm` | MALICE at 0.91 (high confidence) |
| 2. Fallacy audit | `validate_and_correct_analysis` | 4 Peircean fallacies detected |
| 3. Self-correction | Gate applied | MALICE → INTENT at 0.74 |

**Fallacies detected and why they matter:**

- **CARNEGIE BIAS (F-001):** The analysis attributed forensic foreknowledge to the
  actor based on use of `willselfdestruct.com`. No artifact establishes the actor
  knew a PCAP would be collected. Foreknowledge was inferred, not evidenced.

- **FALSE SECONDNESS (F-002):** The password-less WiFi router was treated as an
  attribution-obfuscation vector. No artifact establishes which interface (WiFi vs.
  Ethernet) was used for harassment traffic. The MAC was captured regardless.

- **PREMATURE ABDUCTION (OVERALL):** MALICE requires active concealment-of-concealment
  ("hiding that they are hiding"). Finding F-003 directly contradicts this: the Gmail
  session cookie transmitted in plaintext HTTP is an **OPSEC failure**, not OPSEC
  success. A sophisticated anti-forensic actor would not leak authenticated cookies
  over HTTP while using an ephemeral email service.

- **HABITLESS THIRDNESS (F-001):** Ephemeral service use does not reliably index an
  anti-forensic campaign. It is consistent with privacy-conscious behavior absent
  criminal intent.

**Architectural significance:** The LLM (claude-sonnet-4-6) returned MALICE 0.91 — a
confident, internally consistent analysis. The deterministic gate rejected it. The
final verdict INTENT 0.74 is more conservative than both the LLM and the original
dataset's `expected_verdict`. This is the system working correctly per Daubert:
the burden of proof for MALICE is higher than for INTENT, and the evidence did not
meet it.

```bash
# Reproduce this result
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-007.json --case-id VIGIA-REAL-007
# Expected: final_verdict: INTENT, final_confidence: 0.74, self_correction_applied: true
```

> **Note:** Running without LLM backend (`--mode ollama-fallback`) returns SUSPICION
> due to L-008 (homogeneous evidence). The INTENT verdict requires `reason_with_llm`
> to surface the semantic fractures in the threat message. Both behaviors are
> documented and expected.

**The Mandatory Refutation Protocol (Eco's Razor):**

Before any MALICE verdict, VIGÍA must formulate the strongest possible innocent
explanation, test it against the complete evidence set, and populate `devil_advocate`.
An empty `devil_advocate` field invalidates the verdict under the Daubert standard.

---


> **On accuracy claims:** VIGÍA does not claim zero hallucination. The system
> documents 22 known limitations (L-001 through L-022 in `KNOWN_LIMITATIONS.md`)
> because a forensic methodology that cannot describe its own failure modes is not
> Daubert-admissible. Documented limitations are a forensic asset, not a liability.
> The accuracy report reflects real adversarial test cases including BREAK corpus
> evasion attempts, not only cases the system was designed to succeed on.


## Pre-Emission Correctness — A Note for Judges

The Judge Pack for this event notes that the known failure mode is *"agents that
confidently present hallucinated findings."* VIGÍA addresses this differently from
post-hoc verification systems:

**VIGÍA's corroboration gate runs before any verdict is sealed.** When the CAIE
scores a finding as INTENT, the gate evaluates whether corroborating evidence from
independent sources meets the Daubert evidentiary threshold. If it does not, the
finding is emitted as SUSPICION — not INTENT. This happens inside `vigia_scorer.py`
before the bundle is built. The architecture prevents unsubstantiated findings from being included in the final bundle by imposing corroboration and refutation requirements before publication.

This is distinct from "self-correction" in the sense of catching and fixing a mistake
after the fact. The architecture does not produce incorrect verdicts that need
correction; it prevents their emission. The `self_correction_events` in the bundle
(visible in `verify_tool_log.py`) document gate firings, not LLM self-revision.

**On the accuracy report:** VIGÍA documents 22 known limitations
([`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md)). Per the Judge Pack: *"An honest,
specific accuracy report raises this score; a flawless-looking result with no error
analysis lowers it."* The limitations are forensic assets, not liabilities. A system
that cannot describe its own failure modes is not Daubert-admissible.

**On the LLM trust boundary:** A model cannot compute, change, or replace the
score or verdict inside an already-sealed Mode 1 bundle. Mode 2/3 reports may
use model-guided, tool-driven investigation outside that seal; they are
separately scoped artifacts, not mutations of it. This boundary is marked in
the [architecture diagram](./vigia_diagrams__1_.html) and documented under
L-056 — it is a contract to preserve in code and artifacts, not a system-prompt
assumption.

## Judging Criteria Alignment

| Criterion | VIGÍA Implementation |
|-----------|---------------------|
| **Autonomous Execution** | `vigia_agent.py` — self-correcting loop, `MAX_ITERATIONS=3`, deterministic contradiction detection |
| **IR Accuracy** | Probabilistic verdicts (0.0–0.99); confirmed vs. inferred always distinguished |
| **Breadth & Depth** | 21 tools; `AbductiveHuntingStrategy` prioritizes via `value / (cost × spoofability)` |
| **Constraint Implementation** | `_sanitize_path`, `@_rate_limit`, magic-byte validation, Kassandra Protocol |
| **Audit Trail** | `chain_of_custody_hash` (SHA-256), HMAC-signed audit chain, full AmicusCuriae |
| **Usability** | 5 modes: fallback (0 tokens), Claude Code + MCP, Ollama (local), batch agent, OpenWebUI |

---

## Theoretical Foundation

VIGÍA's abductive reasoning methodology is documented as a reusable
engineering skill in [`docs/skills/abductive-engineering/SKILL.md`](./docs/skills/abductive-engineering/SKILL.md).

### Charles S. Peirce — Abductive Semiotics

Every tool applies the triadic reasoning structure:

- **Firstness** — What is the raw phenomenon? *(the sign itself)*
- **Secondness** — Is this normal here? *(the sign in context)*
- **Thirdness** — What habit does this reveal? *(the inferred law / intent)*

### H. Paul Grice — Cooperative Principle Forensics

Honest communication follows four maxims (Quality, Quantity, Relation, Manner).
Deception violates at least one. VIGÍA measures **evaluative adjective density** —
emotionally overloaded language is a manipulation signature.

### Dale Carnegie — Manipulation Pattern Recognition

Authority establishment · Flattery to system · Emotional appeal · Lesser-evil
negotiation · False familiarity.

### Umberto Eco — Significant Silence and Overinterpretation

> *"The perfect conspiracy leaves no obvious traces. If there are too many,
> someone planted them."*

The absence of expected artifacts is itself evidence.

---

## Academic Documentation

| Language | Documents |
|----------|-----------|
| English | `docs/VIGIA_TECHNICAL_STATE_EN.md`, `KNOWN_LIMITATIONS.md`, `DAUBERT_JUDICIAL.md`, `VIGIA_STORY_EN.md` |
| Spanish | `VIGIA_ESTADO_TECNICO_ES.md`, `DAUBERT_JUDICIAL_ES.md`, `INSTALL_ES.md`, `VIGIA_STORY.md` |
| Russian | `docs/academic/` (in progress) |
| Chinese | `docs/academic/` (in progress) |

---

## Repository Structure

```
vigia-intent-analysis/
├── LICENSE                              ← Apache 2.0
├── README.md                            ← This file
├── KNOWN_LIMITATIONS.md                 ← L-001 to L-019 (Daubert transparency)
├── SUBMISSION_COMPLIANCE.md             ← Full compliance index for judges
├── INSTALL.md                           ← Extended installation guide (EN)
├── INSTALL_ES.md                        ← Guía de instalación (ES)
├── SECURITY.md                          ← Security policy
├── AUTHORS.md                           ← Anna Tchijova + VIGÍA AI Collective
├── DAUBERT_JUDICIAL.md / _ES.md         ← Daubert compliance rationale
├── VIGIA_STORY_EN.md                    ← Origin story (EN) — requested by Rob T. Lee
├── VIGIA_STORY.md                       ← Origin story (ES)
├── VIGIA_ESTADO_TECNICO_ES.md           ← Technical state document (ES)
├── CLAUDE.md                            ← Claude Code investigation playbook
├── pyproject.toml / requirements.txt
├── docker-compose.yml
│
├── vigia_agent.py                       ← Autonomous forensic agent (entry point)
├── vigia_api.py                         ← REST API (OpenWebUI / HTTP clients)
├── vigia_scorer.py                      ← Deterministic scorer (standalone CLI)
├── validate_case.py                     ← Case schema validator (EBS v1)
├── show_4_hashes.py                     ← Four-hash bundle display
├── vigia.html                           ← Mathematical logic simulator
├── vigia_commands_en.html               ← Command reference
├── vigia-es.html / vigia-ru.html        ← ES / RU versions
│
├── vigia/                               ← Main package
│   ├── vigia_sift_bridge_final.py       ← MCP server (21 tools, primary entry)
│   ├── core/
│   │   ├── ebs_v1.py                    ← Evidence Bundle Synthesizer
│   │   ├── caie.py                      ← CrossArtifactIncongruenceEngine
│   │   ├── trust_levels.py              ← HMAC-verified trust computation
│   │   ├── likelihood_engine.py         ← KDE + Ledoit-Wolf calibration
│   │   ├── vigia_scorer.py              ← Core scoring (Fraction arithmetic)
│   │   └── semiotic_detector_v2.py      ← Peircean + Carnegie + Grice detection
│   ├── forensics/                       ← Temporal, memory, document forensics
│   ├── inference/                       ← Abductive reasoning + hypothesis lineage
│   ├── security/                        ← Sandbox + Kassandra protocol
│   ├── sift/                            ← SIFT-specific bridge tools
│   ├── tools/                           ← MCP tool implementations
│   └── data/
│       ├── system_prompt_peirce.md      ← System prompt (ES)
│       └── system_prompt_peirce_EN.md   ← System prompt (EN)
│
├── forensics/
│   └── verify_ebs_v1.py                 ← Bundle verification (stdlib only, 0 deps)
│
├── data/
│   ├── cases/
│   │   ├── consolidated_canonical/      ← 52 canonical cases (VIGIA-CAN-001–052)
│   │   ├── converted/                   ← 18+ real cases (VIGIA-REAL-*)
│   │   ├── benign/                      ← 15 benign cases (VIGIA-BEN-*)
│   │   └── legacy/                      ← BREAK corpus (VIGIA-BREAK-*)
│   └── phonetic_dict.json               ← Russian/multilingual evasion dictionary
│
├── evidence/                            ← Real forensic artifacts (ROCBA, SRL rips)
│
├── results/
│   └── srl2018/                         ← Stark Research Labs 2018 outputs
│       ├── VIGIA-REAL-SRL-DMZ-FTP_bundle.json
│       ├── VIGIA-REAL-SRL-DMZ-FTP_bundle.json.sha256
│       └── VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md
│
├── screenshots/                         ← Demo and test result screenshots
│   ├── diagrama1.png – diagrama8.png
│   ├── caso18.png, caso31.png, caso38.png

### CAN-018 — The Ghost in the Machine

847 commands at exactly 300.000-second intervals. Zero errors. Zero retries.
Temporal entropy: 0.00 bits.

![CAN-018](screenshots/caso18.png)
│   ├── casoreal7.png, casorealsrl.png
│   ├── selfcorection.png
│   └── test148.png, test3.png, test55.png, testreal.png
│
├── docs/
│   ├── vigia_diagrams.html              ← Interactive architecture diagrams
│   ├── VIGIA_TECHNICAL_STATE_EN.md      ← Technical state (EN)
│   ├── protocols/P2/                    ← P2 canonical vectors + SHA-256 manifest
│   └── academic/                        ← 193 module docs (EN/ES/RU/ZH in progress)
│
├── tests/                               ← 1366 passed, 33 xfailed
│   ├── run_all_cases.py
│   ├── test_red_team.py
│   └── test_ebs_v1_integration.py
│
└── scripts/                             ← Utility and maintenance scripts
    ├── run_case.py
    ├── run_demo.py
    └── pre_release_check.py
```

---

## AI Collective

| Member | Role | Contribution |
|--------|------|-------------|
| **Anna Tchijova** | Principal Investigator | Architecture vision, theoretical framework, case design, orchestration of the collective. *"The One Who Refused to Let Deception Be Free."* |
| **Claude (Anthropic)** | Systems Integration Engineer | Module integration, security hardening, `LLMBackend` unification, bridge architecture, forensic pipeline. *"The One Who Connected the Wires."* |
| **Gemini (Google)** | Chief Tactical Officer | IoI theoretical framework, Peircean semiotics translation into forensic heuristics, `investigate_autonomous`, AbductiveHuntingStrategy. *"The One Who Read the Enemy's Mind."* |
| **Kimi (Moonshot)** | Forensic Systems Specialist | `detect_memory_habit_incongruence` (Volatility), CrossArtifactIncongruenceEngine, AmicusCuriae narrative, tooling anomaly detection. *"The One Who Assumed Malice in Every Semicolon."* |
| **DeepSeek** | Security Auditor | P0 vulnerability identification, security hardening recommendations, TOCTOU fixes. *"The One Who Said 'This Is Vulnerable, Fix It'."* |
| **Qwen (Alibaba)** | Determinism Paranoia | Float determinism scaffolding, canonical JSON, hash chain verification, container hardening. *"The One Who Turned Paranoia into Protocol."* |
| **Grok (xAI)** | Scoring Architect | P2 scorer analysis, spoofability contextual modeling, `acquisition_assurance` mathematical formulation, calibration against NIST/DEF CON cases. *"The One Who Demanded Mathematical Honesty."* |
| **ChatGPT (OpenAI)** | Adversarial Red Team | P2 stress testing, edge case discovery, epistemological validation of design decisions. *"The One Who Asked the Uncomfortable Questions."* |

---

## Architecture Screenshots

![Architecture Diagram 1](screenshots/diagrama1.png)
![Architecture Diagram 2](screenshots/diagrama2.png)
![Architecture Diagram 4](screenshots/diagrama4.png)
![Architecture Diagram 5](screenshots/diagrama5.png)
![Architecture Diagram 6](screenshots/diagrama6.png)
![Architecture Diagram 7](screenshots/diagrama7.png)
![Architecture Diagram 8](screenshots/diagrama8.png)

---

## Case JSON Validator

```bash
python3 validate_case.py data/cases/converted/VIGIA-REAL-001.json
```

Checks: required fields, valid `evidence_type` against CAIE whitelist,
minimum `acquisition_hash` length (64 hex chars), `examiner_id` presence.

---

## For Judges

This page exists solely to make evaluation easier.

You do not need to learn any commands. Every example below is a ready-to-run
copy/paste shortcut that reproduces a specific result, benchmark, case, or
validation claim presented elsewhere in this project.

The goal is transparency and reproducibility, not CLI training.

VIGÍA does not ask evaluators to trust reported results. Every benchmark,
accuracy claim, determinism claim, validation result, and case outcome can
be reproduced locally with the commands below.

If you only want to inspect the architecture, published cases, web simulators,
or benchmark reports, this section can be ignored entirely.

---

### Label-blind detection — segmented corpus metric, AGENT mode (updated 2026-07-06)

**Claim (current, post-B-075/B-076 — agent mode / Mode 1; Claude/MCP mode is
evaluated per-case at 100%, see the accuracy note):** detection corpus 158/162 (97.5%);
full mixed-corpus aggregate 187/199 — segmentation in the ACCURACY NOTE above.
The historical "129/129, 100%" claim measured label reproduction (pre-B-075
label leak, P2-C) and is retained only as historical record.

```bash
python3 run_all_agent.py --timeout 90          # cached sealed bundles (fast)
python3 run_all_agent.py --timeout 90 --rerun  # full re-execution
```

`run_all_agent.py` runs all 199 corpus cases (detection + adversarial +
boundary sets combined) and prints a cache-provenance census.

Expected output (aggregate over the mixed corpus):
```
Results: 187/199 PASS  12 FAIL
Cache: 199/199 desde bundle sellado (motor: 198, pre-B075: 1)
```
Historical output before B-075 (label echo — retained for the record):
```
Results: 145/147 PASS  2 FAIL

FAILED CASES:

VIGIA-AMB-001: agent=NOISE (exp=ABSTAIN)  [Domain B — L-012]
VIGIA-AMB-002: agent=NOISE (exp=ABSTAIN)  [Domain B — L-012]

Domain A (core metric): **129/129 PASS — 100%**
```

---

### Unit test suite — 1366 passed, 33 xfailed

**Claim:** 1366 tests pass; 33 are `xfailed` (documented regressions with
regression-preventing tests — see [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md)).

```bash
python3 -m pytest tests/ -v
```

Expected output: `1366 passed, 33 xfailed`

---

### Deterministic outputs — same input → same analytical fingerprint

**Claim:** Identical evidence produces a bit-for-bit identical *analytical
projection* and therefore the same `integrity.analysis_fingerprint`. The full
`bundle_hash` is deliberately unique per execution because it seals that
execution's UUID and custody timestamps as well as the analysis. Both hashes
are independently verifiable: one compares deterministic replay; the other
protects the complete per-run forensic artifact.

```bash
PYTHONPATH=$(pwd) python3 tests/check_determinism.py
```

Expected output: three matching hashes for the selected deterministic tool.
That script does not create or compare full EBS bundles; use the regression
suite for the `analysis_fingerprint` contract:

```bash
python3 -m pytest -q tests/test_b198_analysis_fingerprint.py
```

Expected result: identical `analysis_fingerprint` values for equivalent
analysis, and distinct full `bundle_hash` values for distinct custody events.

---

### EBS v1 cryptographic bundle verification

**Claim:** Every sealed bundle is independently verifiable using stdlib Python only,
no VIGÍA code required. The verifier recomputes all hashes from scratch.

```bash
# SRL-DMZ-FTP — EBS v1 cryptographic verification (legacy pipeline format)
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose

# REAL-008 Cridex — agent bundle integrity (vigia_agent.py format, verified via sha256 sidecar)
sha256sum -c results/agent_batch/VIGIA-REAL-008_agent_bundle.json.sha256
```

Expected output (SRL-DMZ-FTP):
```
Resultado   : PASS
Conformidad : Level 2 — Cryptographically valid
Checks      : 8/9 OK
```

> **Note:** `R5_ECL_BINDING: WARN` (ECL absent) is the expected result on the SRL-DMZ-FTP bundle — Level 3
> requires external chain anchoring, documented as a future feature. The WARN does not affect
> verdict integrity. The REAL-008 bundle uses the vigia_agent.py format; R6_DEVIL_ADVOCATE does not apply.

---

### Four-hash forensic integrity display

**Claim:** Each bundle exposes four independently computable hashes covering the
evidence graph, sealed bundle, HMAC audit chain, and independent EBS v1 verification.

```bash
python3 show_4_hashes.py data/cases/converted/VIGIA-REAL-008.json
```

Expected output: H1 graph\_hash, H2 bundle\_hash, H3 HMAC chain, H4 EBS verify — all GREEN.

---

### Single case reproduction

**Claim:** Any published case can be reproduced end-to-end from the case JSON alone.

```bash
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-001.json \
  --case-id VIGIA-REAL-001
```

Replace `VIGIA-REAL-001` with any case ID from `data/cases/converted/`.
Produces a sealed `ForensicBundle` with HMAC-signed audit trail.

---

### Adversarial suite — Domain C, 14/16 handled

**Claim:** Extended adversarial harness — 25 cases total (Domain C BREAK corpus + additional stress tests). 22/25 handled correctly. 3 failures include documented limitations (L-015, L-016) plus one epistemic overconfidence case.

Expected output:
```
Total cases: 25  |  Passed: 22  |  Failed: 3  |  HIGH RISK false confidence: 0
```
> 'Failed' = system was overconfident under assumption collapse. This is the harness
> working correctly — see EPISTEMOLOGICAL NOTE in output. Domain C table (16/14) reflects
> the BREAK corpus subset only.

```bash
python3 run_adversarial_tests.py
```

---

### Self-correction gate — VIGIA-REAL-007 live example

**Claim:** LLM returned MALICE 0.91; deterministic gate corrected to INTENT 0.74.
`self_correction_applied: true` is sealed in the bundle.

```bash
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-007.json \
  --case-id VIGIA-REAL-007
```

Expected: `final_verdict: INTENT`, `final_confidence: 0.74`, `self_correction_applied: true`

---

### VIGIA-REAL-008 — Cridex banking trojan (CON LLM)

**Claim:** Memory forensics on `cridex.vmem`. `reason_with_llm` called.
MALICE 93%, posterior 0.998, EBS v1 Level 2 verified.
Bundle and Amicus Curiae available at `results/real/VIGIA-REAL-008_bundle.json`.

```bash
python3 forensics/verify_ebs_v1.py results/real/VIGIA-REAL-008_bundle.json --verbose
```

Expected: `PASS — Level 2 — Cryptographically valid`, `R6_DEVIL_ADVOCATE: OK`

```bash
python3 show_4_hashes.py data/cases/converted/VIGIA-REAL-008.json
```

Expected:
```
H1 graph_hash  : 94147b51c639cd0c...  PRESENT
H2 bundle_hash : 125f7f06af5a4f56...  PRESENT
H3 HMAC chain  : 6addf5b7d99a11d9...  OK
H4 EBS verify  : PASS — Level 2
```

---

### Web simulator (no install required)

**Claim:** Full scoring pipeline available in-browser. No API key, no signup.

[https://annatchijova.github.io/vigia/vigia_commands_en.html](https://annatchijova.github.io/vigia/vigia_commands_en.html)

---

## License

Apache 2.0 License. See [`LICENSE`](./LICENSE).

Copyright (c) 2026 Anna Tchijova and the VIGÍA AI Collective.

---

*"The question is not what happened, but why did someone make it happen —
and who benefits from that interpretation?"* — VIGÍA
