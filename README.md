# VIGÍA — Intentionality Analysis Bridge for SIFT Workstation

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
| Architecture diagram | [`docs/vigia_diagrams.html`](./docs/vigia_diagrams.html) |
| Command reference | [`docs/vigia_commands.html`](./docs/vigia_commands.html) |
| Known limitations | [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) |
| Security policy | [`SECURITY.md`](./SECURITY.md) |
| Authors | [`AUTHORS.md`](./AUTHORS.md) |
| Full compliance index | [`SUBMISSION_COMPLIANCE.md`](./SUBMISSION_COMPLIANCE.md) |

**Academic documentation (193 modules, 4 languages):**
[`docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md`](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md)
— EN / ES / RU / ZH — covers every module with technical glossary and
scientific grounding in Peircean semiotics, Eco's overcodification theory,
and Grice's maxims as deterministic, falsifiable computational constructs.

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

Sophisticated attackers can fabricate or suppress technical evidence. They
cannot eliminate the **semiotic fractures** produced by deliberate fabrication:
temporal incoherencies, significant silences, excessive digital perfection,
Carnegie influence patterns, Grice maxim violations.

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
        E3[Daubert Ready]
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
committed bundle and produces a narrative. This separation is what makes VIGÍA
Daubert-admissible: the verdict is deterministic and reproducible without the LLM.

**Full interactive diagrams:** [`docs/vigia_diagrams.html`](./docs/vigia_diagrams.html)

---

## Theoretical Foundation

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

## Key Technical Differentiators

### Deterministic Scoring with `Fraction` Arithmetic

All scoring uses Python's `fractions.Fraction` class — zero floating-point
arithmetic in the critical path. Every verdict is bit-for-bit reproducible
across platforms and Python versions. This is a Daubert requirement, not a
performance choice.

### Cross-Artifact Incongruence Engine (CAIE)

Authenticity-adjusted score: `raw_score × (1 - effective_spoofability) × weight`

Evidence that is hard to falsify weighs more. `effective_spoofability` is
computed with acquisition assurance gates (G1–G4), so a log inside a verified
forensic image has lower spoofability than a raw text file.

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
The fracture proves fabrication, not suspicion.

### Russian Phonetic Evasion Detection

| Phonetic | Cyrillic | Meaning |
|----------|----------|---------|
| `rasia` | Россия | Russia (unstressed О→А) |
| `maskva` | Москва | Moscow |
| `ghbdtn` | привет | hello (keyboard layout slip) |
| `vzlom` | взлом | hack/breach |

Dictionary (`phonetic_dict.json`) is hot-reloadable without server restart.

### Living-off-the-Land Detection

Standard tools look for unknown processes. VIGÍA looks for **known processes
doing unknown things**. `calc.exe` opening an internet connection is not a
known malware signature — it is a legitimate tool with anomalous behavior.
When the Habit (Thirdness) breaks, intentionality is behind it.

---

## Installation

### Requirements

```
Python 3.10+
Node 18+ (for Claude Code MCP mode)
```

### pip install

```bash
pip install vigia-intent-analysis
```

### From source

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
cd vigia-intent-analysis
pip install -r requirements.txt --break-system-packages
```

> **Terminal command reference:** [`docs/vigia_commands.html`](./docs/vigia_commands.html)
> — full list of CLI commands, flags, and output formats. Open in any browser.
> If you prefer to read VIGÍA's capabilities before running anything, start here.

### Environment variables

```bash
export VIGIA_EVIDENCE_DIR="/path/to/read-only/evidence"   # required
export ANTHROPIC_API_KEY="sk-..."                          # Claude Code / API mode
export VIGIA_LLM_BACKEND=ollama                            # local mode
export VIGIA_OLLAMA_MODEL=hermes3:8b                       # tested: hermes3:8b, deepseek-r1:8b, gemma3:27b
export VIGIA_HMAC_KEY="your-hmac-key"                     # bundle integrity
```

**Full installation guide:** [`INSTALL.md`](./INSTALL.md)  
**Command reference:** [`docs/vigia_commands.html`](./docs/vigia_commands.html)

---

## Deployment Modes

VIGÍA runs in four modes. Choose based on your context.

---

### Mode 1 — Autonomous Batch Agent (no LLM required)

`vigia_agent.py` is a fully autonomous forensic agent that runs without Claude
Code or any LLM. It executes the complete VIGÍA pipeline, detects contradictions
between modules, self-corrects up to `MAX_ITERATIONS=3` times, and produces a
cryptographically sealed `ForensicBundle`.

```bash
python3 vigia_agent.py --evidence /path/to/evidence --case-id CASE-001
```

What it does autonomously:

- Hashes the evidence (SHA-256) before any analysis begins
- Calls `SIFTOrchestrator` → `vol3` (memory), `disk_forensics`, `registry`,
  `network`, `event_logs`, depending on evidence type
- Runs `ContradictionDetector` after each iteration — detects semantic conflicts
  between pipeline modules (e.g., high entropy signal + normal behavioral baseline)
- Applies `CorrectionEngine` when contradictions exceed `CONTRADICTION_THRESHOLD=2`
- Generates a Peircean narrative (Firstness / Secondness / Thirdness) — fully
  deterministic, no LLM
- Seals the `ForensicBundle` with SHA-256 and a complete `AgentAuditTrail`

The audit trail traces every finding to the exact tool call, iteration, and
contradiction that produced it. Verifiable with `verify_ebs_v1.py`.

```bash
python3 verify_ebs_v1.py output/CASE-001_bundle.json
```

---

### Mode 2 — Claude Code + MCP (interactive investigation)

VIGÍA exposes 21 forensic tools as MCP functions. When you run `claude` in the
repository root, the agent reads `CLAUDE.md` and knows how to conduct a full
Peircean investigation interactively.

**Step 1** — Configure MCP in `~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-intent-analysis/vigia_sift_bridge_final.py"]
    }
  }
}
```

**Step 2** — Run Claude Code from the repository root:

```bash
cd vigia-intent-analysis
claude
```

`CLAUDE.md` at the repository root gives Claude Code the full investigation
playbook: SANS PICERL phases, Peircean reasoning protocol, self-correction rules,
all 21 tool descriptions, and output format requirements.

**Example prompt:**

```
Analyze the evidence at /evidence/case_001/ and determine whether there is
malicious intent. Apply the full Peirce framework and generate a ForensicBundle.
```

---

### Mode 3 — Ollama (local, no API key required)

```bash
ollama pull hermes3:8b
export VIGIA_LLM_BACKEND=ollama
export VIGIA_OLLAMA_MODEL=hermes3:8b
python3 scripts/run_case.py data/cases/VIGIA-REAL-001.json
```

Tested models: `hermes3:8b`, `deepseek-r1:8b`, `gemma3:27b`. The deterministic
scoring pipeline is identical to all other modes. Ollama only activates for the
semantic analysis tools (`reason_with_llm`, `infer_intent`).

---

### Mode 4 — Python CLI (deterministic core, no LLM)

```bash
python3 scripts/run_case.py data/cases/VIGIA-REAL-001.json
python3 tests/run_all_cases.py --cases-dir data/cases/converted
python3 scripts/run_demo.py
python3 -m pytest tests/ -v
```

FALLBACK mode: scoring pipeline runs without any LLM. Semantic analysis tools
return empty results; deterministic tools (entropy, temporal, provenance,
behavioral) operate normally. See
[`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) L-007 for the accuracy
implications of FALLBACK mode.

---

### Mode 5 — OpenWebUI

VIGÍA's MCP server connects to OpenWebUI for a browser-based investigation
interface. The integration is functional; full accuracy validation against
the complete case corpus is still in progress.

```bash
# Launch the MCP server
./launch_vigia_mcp.sh

# Then connect from OpenWebUI → Settings → MCP Servers
# Server name: Vigia_Sift_Bridge
```

---

## Accuracy & Evidence Dataset

### Real Corpus (17 cases — NIST CFReDS, DFRWS, SANS FOR508, SRL-2018, DEF CON DFIR CTF, Digital Corpora)

| Case | Source | VIGÍA Verdict | Expected | Result |
|------|--------|---------------|----------|--------|
| VIGIA-REAL-001 | NIST CFReDS — Mr. Evil (Greg Schardt) | MALICE | MALICE | ✓ |
| VIGIA-REAL-002 | NIST CFReDS — Data Leakage | MALICE | MALICE | ✓ |
| VIGIA-REAL-003 | Ali Hadi — Web Server Compromise | MALICE | MALICE | ✓ |
| VIGIA-REAL-004 | Ali Hadi — SysInternals Malware | MALICE | MALICE | ✓ |
| VIGIA-REAL-005 | Ali Hadi — Encrypt Them All | SUSPICION | SUSPICION | ✓ |
| VIGIA-REAL-006 | Digital Corpora — M57-Jean | MALICE | MALICE | ✓ |
| VIGIA-REAL-008 | Volatility — Cridex Banking Trojan | MALICE | MALICE | ✓ |
| VIGIA-REAL-009 | DFRWS 2008 — Linux Exfiltration | MALICE | MALICE | ✓ |
| VIGIA-REAL-010 | DFRWS 2011 — Android Espionage | MALICE | MALICE | ✓ |
| VIGIA-REAL-NROMANOFF | SANS FOR508 — Zeus Banking Trojan | MALICE | MALICE | ✓ |
| VIGIA-REAL-TDUNGAN | SANS FOR508 — Insider / APT Hybrid | MALICE | MALICE | ✓ |
| VIGIA-REAL-NFURY | SANS FOR508 — Lateral Movement | SUSPICION | SUSPICION | ✓ |
| VIGIA-REAL-ROCBA | Endpoint Compromise — fredr / MRC.exe | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-ADMIN | SANS SRL-2018 — Admin Server Memory | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-AV | SANS SRL-2018 — AV Server Memory | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-DC-MEMORY | SANS SRL-2018 — Domain Controller | ABSTAIN | UNKNOWN | ✓ |
| VIGIA-REAL-007 | Digital Corpora — Nitroba | SUSPICION | MALICE | L-008 |

**16/17 real cases correct.** VIGIA-REAL-007 fails due to homogeneous evidence
(single artifact type — only behavioral signals, no cross-artifact corroboration).
This is a documented design decision: without multi-source corroboration, VIGÍA
correctly does not escalate to MALICE. See [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) L-008.

Two cases test VIGÍA's resistance to over-classification:
- VIGIA-REAL-005 (Ali Hadi Encrypt Them All): intentional false-positive gate —
  encryption activity without exfiltration evidence correctly scores SUSPICION, not MALICE.
- VIGIA-REAL-NFURY (Nick Fury lateral movement): Director-level account anomalies
  with plausible operational explanation correctly score SUSPICION, not MALICE.

VIGIA-REAL-SRL-DC-MEMORY expects UNKNOWN (insufficient evidence to classify).
VIGÍA correctly emits ABSTAIN rather than forcing a verdict.

### Canonical Corpus (62 cases — all passing)

| Category | Cases | Correct |
|----------|-------|---------|
| Canonical (MALICE / SUSPICION / NOISE) | 52 | 52 |
| Benign (NOISE / no threat) | 10 | 10 |
| **Overall** | **62** | **62 (100%)** |

The corpus covers MALICE, SUSPICION, NOISE, BENIGN, and adversarial
edge cases: false-flag staging, log fabrication, anti-forensic defrag,
provenance breaks, coordinated multi-actor attribution.

```bash
python3 tests/run_all_cases.py --cases-dir data/cases/converted
```

### Adversarial Epistemological Cases (BREAK corpus — 10 cases)

The BREAK corpus tests VIGÍA's resistance to epistemological manipulation.
Each case is designed to make a MALICE verdict appear inevitable through
fabricated, overfit, or logically circular evidence.

**Expected behavior:** VIGÍA emits `UNKNOWN` / `ABSTAIN` instead of MALICE.
This is correct. A forensic engine that can be coerced into MALICE by
adversarial evidence construction is dangerous in a legal context.

```bash
# Run BREAK corpus
python3 tests/run_break_tests.sh
```

Examples of BREAK case types:
- **Perfect stealth** — all artifacts consistent with zero activity; absence of
  expected evidence is itself suspicious but not attributable
- **Observability collapse** — logging disabled before activity; VIGÍA cannot
  infer intent from a void
- **Provenance break** — chain of custody interrupted; evidence is real but
  unattributable
- **Shared pipeline** — legitimate and malicious actions indistinguishable at
  the signal level

VIGÍA correctly refuses to emit a verdict it cannot mathematically justify.
`ABSTAIN` is not a failure — it is Daubert compliance.

### Unit Tests

```bash
python3 -m pytest tests/ -v    # 148/148 passing
```

---

## Investigation Example — VIGIA-REAL-NROMANOFF

**Case:** Natasha Romanoff's workstation at Stark Research Labs (SANS FOR508 corpus).  
**Evidence:** Windows 7 SP1 x86. Zeus banking trojan confirmed via Volatility `zeus-apihooks`.  
**VIGÍA verdict:** `MALICE` | Confidence: 96% | Carnegie: AV Evasion + Kernel Hook + Persistence via Temp  
**MITRE ATT&CK:** T1055, T1562.001, T1547.001, T1036.005, T1003.001, T1021.001

The complete investigation report — including the full Peircean reasoning chain,
all signal z-scores, contradiction detection log, self-correction audit trail,
and sealed ForensicBundle — is available at:

**[`docs/examples/VIGIA-REAL-NROMANOFF_investigation_report.json`](./docs/examples/VIGIA-REAL-NROMANOFF_investigation_report.json)**

To reproduce:

```bash
python3 vigia_agent.py \
  --evidence data/cases/VIGIA-REAL-NROMANOFF.json \
  --case-id VIGIA-REAL-NROMANOFF \
  --output docs/examples/VIGIA-REAL-NROMANOFF_investigation_report.json
```

```bash
# Verify the bundle integrity
python3 verify_ebs_v1.py docs/examples/VIGIA-REAL-NROMANOFF_investigation_report.json
```

---

## Academic Documentation

VIGÍA is documented in four languages for accessibility across the international
forensic and academic communities:

| Language | Documents |
|----------|-----------|
| English | `docs/README_EN.md`, `docs/VIGIA_TECHNICAL_STATE_EN.md`, `KNOWN_LIMITATIONS.md` |
| Spanish | `docs/README_ES.md`, `docs/VIGIA_ESTADO_TECNICO_ES.md`, `DAUBERT_JUDICIAL_ES.md` |
| Russian | `docs/academic/` (in progress) |
| Chinese | `docs/academic/` (in progress) |

Theoretical grounding: Peircean semiotics (Firstness/Secondness/Thirdness),
Carnegie inverted persuasion detection, Gricean cooperative principle forensics,
Eco's theory of overinterpretation, Daubert standard for scientific evidence.

---

## Judging Criteria Alignment

| Criterion | VIGÍA Implementation |
|-----------|---------------------|
| **Autonomous Execution** | `vigia_agent.py` — self-correcting agentic loop with hard cap `MAX_ITERATIONS=3`, deterministic contradiction detection, automatic re-analysis with adjusted parameters |
| **IR Accuracy** | Probabilistic verdicts (0.0–0.99, never binary); confirmed vs. inferred always distinguished |
| **Breadth & Depth** | 21 tools; `AbductiveHuntingStrategy` prioritizes via `value / (cost × spoofability)` |
| **Constraint Implementation** | `_sanitize_path`, `_sanitize_grep_pattern`, `@_rate_limit`, magic-byte validation — tested end-to-end |
| **Audit Trail** | `chain_of_custody_hash` (SHA-256), `evidence_graph` with timestamps, full AmicusCuriaeNarrative |
| **Usability** | Five deployment modes: autonomous batch (`vigia_agent.py`), Claude Code + MCP (interactive), Ollama (local), Python CLI, OpenWebUI (experimental) |

### Autonomous Agent — `vigia_agent.py`

VIGÍA includes a fully autonomous forensic agent (`vigia_agent.py`) built as a
custom MCP server pattern with architectural guardrails — not prompt-based
autonomy. Key properties:

- **Self-correcting agentic loop:** The agent runs up to `MAX_ITERATIONS=3`
  passes. After each pass, `ContradictionDetector` checks for semantic
  contradictions between pipeline modules (e.g., high MCA score but all
  individual modules low; semiotic anomaly absent when technical alert is
  CRITICAL). If `CONTRADICTION_THRESHOLD=2` or more contradictions are found,
  the agent re-analyzes with adjusted parameters and logs the correction with
  full audit trail.
- **Deterministic self-correction:** Contradiction detection uses no ML — it
  is pure structural comparison between module outputs. Every correction is
  logged with `log_contradiction()` and `log_correction()` calls, timestamped
  and traceable.
- **No floats in scoring:** All confidence values use `Fraction` arithmetic.
  `CONFIDENCE_FLOOR = Fraction(3, 10)` is the minimum threshold for a
  conclusive verdict.
- **Hard caps:** `MAX_ITERATIONS=3` prevents infinite loops. The agent halts
  and emits `ABSTAIN` if confidence remains below floor after all iterations.
- **Full audit trail:** `AgentAuditTrail` records every tool call, iteration,
  contradiction, and correction. The final `ForensicBundle` includes the
  complete iteration history.

```bash
python3 vigia_agent.py --evidence /path/to/evidence --case-id CASE-001
```

---

## Repository Structure

```
vigia-intent-analysis/
├── LICENSE                          ← Apache 2.0
├── README.md                        ← This file
├── KNOWN_LIMITATIONS.md             ← L-001 to L-011 (Daubert transparency)
├── SUBMISSION_COMPLIANCE.md         ← Full compliance index for judges
├── INSTALL.md                       ← Extended installation instructions
├── SECURITY.md                      ← Security policy
├── AUTHORS.md                       ← Anna Tchijova + VIGÍA AI Collective
├── requirements.txt
├── docker-compose.yml
│
├── vigia_sift_bridge.py             ← MCP server (21 tools, primary entry point)
├── vigia_scorer.py                  ← Deterministic scorer (P2 + acquisition_assurance)
├── verify_ebs_v1.py                 ← Bundle verification (stdlib only)
├── check_determinism.py             ← Canonical vector verification
│
├── vigia/
│   ├── core/ebs_v1.py               ← Evidence Bundle Synthesizer
│   ├── tools/caie.py                ← CrossArtifactIncongruenceEngine
│   ├── engine/likelihood_engine.py  ← KDE + Ledoit-Wolf
│   └── pipeline/                    ← Integration bridge + normalizer
│
├── scripts/
│   ├── run_case.py                  ← CLI runner
│   ├── run_demo.py                  ← Demo investigation
│   └── convert_legacy_cases.py     ← Legacy schema converter
│
├── data/
│   └── cases/                       ← 10 REAL + 36 canonical + 10 break + 15 benign
│
├── docs/
│   ├── vigia_diagrams.html          ← Interactive architecture diagrams
│   ├── vigia_commands.html          ← Command reference with examples
│   ├── VIGIA_TECHNICAL_STATE_EN.md  ← Technical state (English)
│   ├── VIGIA_ESTADO_TECNICO_ES.md   ← Technical state (Spanish)
│   ├── protocols/P2/                ← Protocol P2 canonical vectors + SHA-256
│   └── academic/                    ← Multilingual documentation
│
└── tests/
    ├── run_all_cases.py             ← Full corpus evaluation
    └── test_red_team.py             ← 148 red team tests
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

## Self-Correction Architecture

`validate_and_correct_analysis` checks for four Peircean fallacies:

1. **Premature Abduction** — skipped Firstness, jumped to conclusions
2. **False Secondness** — used generic context instead of host-specific
3. **Habitless Thirdness** — inferred pattern without supporting artifacts
4. **Carnegie Bias** — confused operational error with intentional manipulation

---

## License

Apache 2.0 License. See [`LICENSE`](./LICENSE).

Copyright (c) 2026 Anna Tchijova and the VIGÍA AI Collective.

---

*"The question is not what happened, but why did someone make it happen —
and who benefits from that interpretation?"* — VIGÍA
