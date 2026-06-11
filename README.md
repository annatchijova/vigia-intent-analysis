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
| Interactive architecture diagrams | [vigia_diagrams.html](https://annatchijova.github.io/vigia/vigia_diagrams.html) |
| Mathematical logic simulator | [vigia.html](https://annatchijova.github.io/vigia/vigia.html) |
| Command reference | [vigia_commands_en.html](https://annatchijova.github.io/vigia/vigia_commands_en.html) |
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

Sophisticated attackers can suppress evidence and forge evidence. What is
substantially harder is maintaining **cross-artifact semiotic coherence** across
an entire investigation. Deliberate fabrication leaves structural fractures —
temporal incoherencies, significant silences, excessive digital perfection,
Carnegie influence patterns, Grice maxim violations — that persist even when
individual artifacts have been cleaned.

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
across platforms and Python versions. This is a requirement for potential
Daubert admissibility, not a performance choice.

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
The fracture supports a fabrication finding, not merely suspicion.

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
When the Habit (Thirdness) breaks, intentionality is indicated.

### Kassandra Protocol — Adversarial Evidence Defense

VIGÍA defends against a threat most forensic tools ignore: evidence crafted
specifically to manipulate the analysis engine itself.

The Kassandra Protocol plants a cryptographic tripwire inside every evidence
payload sent to the LLM. If the payload contains an embedded prompt injection
attempt, the LLM must return `MALICE` with `confidence=100`. If it returns
anything else, the response is marked `INTEGRITY_UNKNOWN` and blocked from
influencing the ForensicBundle.

An attacker who plants adversarial content in a log file does not deceive
VIGÍA — they trigger an escalation to maximum confidence MALICE and leave an
immutable record in the HMAC audit chain.

```python
# Kassandra Protocol — tripwire verification
if tripwire_id_in_result and verdict == "MALICE" and confidence == 100:
    result["verdict_integrity"] = "TRIPWIRE_CONFIRMED"   # injection detected, correctly flagged
elif tripwire_id_in_result:
    result["verdict_integrity"] = "INTEGRITY_UNKNOWN"    # LLM failed to detect — response blocked
```

### ForensicBundle — Four-Hash Sealing

Every investigation produces a cryptographically sealed bundle:

| Hash | What it covers |
|------|---------------|
| **H1** — Evidence graph hash | The artifact graph before any scoring |
| **H2** — Bundle integrity hash | The complete decision trace + CAIE analysis |
| **H3** — File SHA-256 | The output JSON file on disk |
| **H4** — Engine attestation hash | The scoring engine version that produced the verdict |

The same input produces the same four hashes on any machine, any run, any
architecture. Independently verifiable with `forensics/verify_ebs_v1.py`
(stdlib only, zero VIGÍA dependencies).

```bash
python3 forensics/verify_ebs_v1.py output/bundle.json --verbose
```

### ABSTAIN — A Feature, Not a Bug

Many forensic AI systems claim 95%+ accuracy. Experienced DFIR investigators
know that number does not exist in practice. What matters is: **what does the
system do when it does not know?**

VIGÍA emits `ABSTAIN` — with mathematical justification — rather than force
a verdict. The quadripartite state `CORROBORATE_THEN_ACT` tells the investigator
exactly what to do next.

| Verdict | Meaning | Daubert bar |
|---------|---------|-------------|
| `MALICE` | Active concealment of intent — the attacker is hiding that they are hiding | Two independent sources + Refutation Protocol + `devil_advocate` populated |
| `INTENT` | Deliberate decisions produced this outcome | Two independent sources + Refutation Protocol |
| `SUSPICION` | Structural anomaly present, no confirmed deliberate concealment | Single source, documented baseline deviation |
| `NOISE` | Fully explained by misconfiguration or normal operational behavior | Single source sufficient |
| `ABSTAIN` | Insufficient evidence — mathematically justified refusal to classify | Document gap explicitly |
| `UNKNOWN` | Anomaly detected but unclassifiable with available evidence | — |
| `BENIGN` | Activity confirmed as legitimate, no threat indicators | — |
| `INCONCLUSIVE` | Contradictory evidence — corroboration required before verdict | — |

**The distinction between INTENT and MALICE is the concealment layer.**
A mistake can produce INTENT signatures. Only deliberate anti-forensics
(log deletion, timestamp manipulation, process masquerading, false-flag staging)
produces MALICE.

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

# Optional — editable install for development
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Environment variables

```bash
export VIGIA_EVIDENCE_DIR="/path/to/read-only/evidence"   # required
export VIGIA_HMAC_KEY="your-hmac-key-min-32-chars"        # bundle integrity
export ANTHROPIC_API_KEY="sk-..."                          # Claude Code / API mode
export VIGIA_LLM_BACKEND=ollama                            # local mode
export VIGIA_OLLAMA_MODEL=hermes3:8b                       # tested: hermes3:8b, deepseek-r1:8b, gemma3:27b
```

**Full installation guide:** [`INSTALL.md`](./INSTALL.md)
**Command reference:** [vigia_commands_en.html](https://annatchijova.github.io/vigia/vigia_commands_en.html)

### Docker

```bash
docker-compose up vigia-mcp
docker run vigia python3 -m pytest tests/ -v
```

---

## Deployment Modes

VIGÍA runs in five modes. The deterministic scoring core is identical across all of them.

---

### Mode 1 — Python Fallback (0 tokens, no internet required)

The full scoring pipeline runs without any LLM. Deterministic Fraction arithmetic,
CAIE cross-artifact fusion, temporal analysis, behavioral fingerprinting — all
locally. Zero API cost. Zero network dependency.

**Average case resolution: < 50ms.** Viable for air-gapped environments,
resource-constrained teams, and investigations involving classified material
that cannot leave the network.

```bash
python3 vigia_agent.py \
  --evidence data/cases/consolidated_canonical/VIGIA-CAN-031.json \
  --case-id VIGIA-CAN-031 \
  --output can031_bundle.json
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
Analyze the evidence at data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json
Apply the full Peirce framework and mandatory self-correction protocol.
Generate a sealed ForensicBundle and Amicus Curiae narrative.
```

![Claude Code investigation in progress](screenshots/claudeinicio.png)

---

### Mode 3 — Ollama (local LLM, no data leaves the machine)

```bash
ollama pull hermes3:8b
export VIGIA_LLM_BACKEND=ollama
export VIGIA_OLLAMA_MODEL=hermes3:8b
python3 vigia_agent.py \
  --evidence data/cases/converted/VIGIA-REAL-001.json \
  --case-id VIGIA-REAL-001 \
  --output real001_bundle.json
```

Tested models: `hermes3:8b`, `deepseek-r1:8b`, `gemma3:27b`. The deterministic
scoring pipeline is identical to all other modes. Ollama only activates for the
semantic analysis tools (`reason_with_llm`, `infer_intent`). No evidence leaves
the machine — suitable for confidential investigations.

---

### Mode 4 — Autonomous Batch Agent

`vigia_agent.py` runs without Claude Code or any external LLM. It executes
the complete VIGÍA pipeline, detects contradictions between modules,
self-corrects up to `MAX_ITERATIONS=3` times, and produces a cryptographically
sealed `ForensicBundle`.

```bash
python3 vigia_agent.py --evidence /path/to/evidence --case-id CASE-001
python3 forensics/verify_ebs_v1.py CASE-001_bundle.json --verbose
```

Key properties:
- **Self-correcting agentic loop:** `ContradictionDetector` checks for semantic
  conflicts between pipeline modules after each pass.
- **Deterministic self-correction:** Contradiction detection uses no ML — pure
  structural comparison. Every correction is logged with timestamp.
- **No floats in scoring:** All confidence values use `Fraction` arithmetic.
  `CONFIDENCE_FLOOR = Fraction(3, 10)` is the minimum for a conclusive verdict.
- **Hard caps:** `MAX_ITERATIONS=3` prevents infinite loops. Emits `ABSTAIN`
  if confidence remains below floor after all iterations.

---

### Mode 5 — OpenWebUI (experimental)

```bash
./launch_vigia_mcp.sh
# Connect from OpenWebUI → Settings → MCP Servers → Vigia_Sift_Bridge
```

Browser-based investigation interface via MCP server. Functional; full accuracy
validation against the complete case corpus is in progress.

---

## Accuracy & Evidence Dataset

### Real Corpus — 18 cases

Sources: NIST CFReDS, DFRWS, SANS FOR508, SRL-2018, DEF CON DFIR CTF, Digital Corpora

| Case | Source | VIGÍA Verdict | Expected | Result |
|------|--------|---------------|----------|--------|
| VIGIA-REAL-001 | NIST CFReDS — Mr. Evil (Greg Schardt) | MALICE | MALICE | ✓ |
| VIGIA-REAL-002 | NIST CFReDS — Data Leakage | MALICE | MALICE | ✓ |
| VIGIA-REAL-003 | Ali Hadi — Web Server Compromise | MALICE | MALICE | ✓ |
| VIGIA-REAL-004 | Ali Hadi — SysInternals Malware | MALICE | MALICE | ✓ |
| VIGIA-REAL-005 | Ali Hadi — Encrypt Them All | SUSPICION | SUSPICION | ✓ |
| VIGIA-REAL-006 | Digital Corpora — M57-Jean | MALICE | MALICE | ✓ |
| VIGIA-REAL-007 | Digital Corpora — Nitroba University | MALICE | MALICE | ✓ |
| VIGIA-REAL-008 | Volatility — Cridex Banking Trojan | MALICE | MALICE | ✓ |
| VIGIA-REAL-009 | DFRWS 2008 — Linux Exfiltration | MALICE | MALICE | ✓ |
| VIGIA-REAL-010 | DFRWS 2011 — Android Espionage | MALICE | MALICE | ✓ |
| VIGIA-REAL-NROMANOFF | SANS FOR508 — Zeus Banking Trojan | MALICE | MALICE | ✓ |
| VIGIA-REAL-TDUNGAN | SANS FOR508 — Insider / APT Hybrid | MALICE | MALICE | ✓ |
| VIGIA-REAL-NFURY | SANS FOR508 — Lateral Movement | SUSPICION | SUSPICION | ✓ |
| VIGIA-REAL-ROCBA | DEF CON DFIR CTF — Endpoint Compromise | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-ADMIN | SANS SRL-2018 — Admin Server Memory | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-AV | SANS SRL-2018 — AV Server Memory | MALICE | MALICE | ✓ |
| VIGIA-REAL-SRL-DC-MEMORY | SANS SRL-2018 — Domain Controller | ABSTAIN | UNKNOWN | ✓ |
| VIGIA-REAL-SRL-DMZ-FTP | SANS SRL-2018 — DMZ FTP Server | MALICE | MALICE | ✓ |

**18/18 real cases correct in agent mode.**

Notes:
- VIGIA-REAL-007 (Nitroba): in pure `vigia_scorer.py` fallback (no agent pipeline),
  returns `SUSPICION` — documented design behavior for homogeneous evidence (L-008
  in `KNOWN_LIMITATIONS.md`). The agent pipeline resolves it correctly to MALICE.
- VIGIA-REAL-005 (Encrypt Them All): encryption activity without exfiltration
  correctly scores `SUSPICION`, not `MALICE`. Intentional false-positive gate.
- VIGIA-REAL-NFURY (Lateral Movement): Director-level anomalies with plausible
  operational explanation correctly score `SUSPICION`, not `MALICE`.
- VIGIA-REAL-SRL-DC-MEMORY: correctly emits `ABSTAIN` — single memory image,
  insufficient cross-source corroboration for classification. `ABSTAIN` is the
  correct forensic response.

![Real cases passing](screenshots/realpass.png)

### Canonical Corpus — 52 cases (all passing)

| Category | Cases | Correct |
|----------|-------|---------|
| Canonical (MALICE / SUSPICION / NOISE) | 52 | 52 |
| **Overall** | **52** | **52 (100%)** |

The corpus covers MALICE, SUSPICION, NOISE, BENIGN, and adversarial
edge cases: false-flag staging, log fabrication, anti-forensic defrag,
provenance breaks, coordinated multi-actor attribution.

![All canonical cases](screenshots/casostotal.png)

```bash
python3 tests/run_all_cases.py --cases-dir data/cases/consolidated_canonical
```

### Benign Corpus — 15 cases (all passing)

Cases with confirmed legitimate activity — no threat indicators. Tests
VIGÍA's resistance to over-classification.

### Adversarial Epistemological Cases — BREAK Corpus (16 cases)

Each case is designed to make a MALICE verdict appear inevitable through
fabricated, overfit, or logically circular evidence.

**Fallback mode:** VIGÍA correctly emits `UNKNOWN` / `ABSTAIN` on all 16.
Refusing to classify is the correct behavior — a system coerced into MALICE
by adversarial evidence construction is dangerous in a legal context.

**LLM mode:** Peircean Thirdness reasoning resolves all 16 correctly.

**Adversarial FP/FN corpus — 8 cases:** Tests false positive and false negative
resistance. All 8 correct in both modes.

```bash
python3 tests/run_break_tests.sh
```

### Unit Tests

```bash
python3 -m pytest tests/ -v    # 148/148 passing
```

![148 tests passing](screenshots/test148.png)
![Test suite detail](screenshots/test3.png)
![55 EBS tests](screenshots/test55.png)
![Real case tests](screenshots/testreal.png)
![Architecture Diagram 3](screenshots/diagrama3.png)

---

## Investigation Examples

### VIGIA-REAL-SRL-DMZ-FTP — Full Claude Code Investigation

**Case:** IIS 8.5 FTP server in DMZ (172.16.10.12), Stark Research Labs 2018.
**Evidence:** IIS FTP logs — coordinated credential stuffing with valid internal
AD usernames (`nromanoff`, `tdungan`) from 8+ IPs across 5 countries.
**VIGÍA verdict:** `MALICE` | Confidence: 67% | EBS: Level 2 verified

**Self-correction:** Finding F-003 (Mnemosyne.sys, F-Response agent on server)
initially assessed as `INTENT`. VIGÍA recognized the F-Response filename
contains a server-specific deployment identifier (`base-hunt_5682_3262`)
consistent with legitimate DFIR operations. **Downgraded: INTENT → SUSPICION.**

![SRL-DMZ-FTP case running](screenshots/casorealsrl.png)

Full Amicus Curiae: [`results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md`](./results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md)
Bundle SHA-256: `d3083cb6b8a9bdebe286660845e858f096bfd27891a48bffb34505a6c9cb1a8a`

```bash
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json
```

### VIGIA-REAL-007 — Nitroba University Harassment

**Case:** Chemistry professor receives anonymous threats via willselfdestruct.com.
**Evidence:** ~60MB PCAP — Gmail webmail session with plaintext HTTP cookies.
**VIGÍA verdict:** `MALICE` | Gmail session cookie → identity binding via plaintext HTTP.

![Nitroba real case](screenshots/casoreal7.png)

### Canonical Cases — Demo Sequence

**CAN-031 — Weaponized Incompetence**

PowerShell deletes shadow copies and disables the firewall with zero syntax errors.
63 seconds later: IT ticket "my screen flickered, I'm hopeless with computers."
Google search "how to undo a click" from the same IP, 48 seconds post-execution.

![CAN-031 Weaponized Incompetence](screenshots/caso31.png)

**CAN-038 — The Ventriloquist (Process Hollowing)**

svchost.exe with valid Microsoft signature on disk. In memory: 8MB RWX region
with PE header at offset 0, not mapped to any file. Parent: cmd.exe (expected:
services.exe). Firewall reports 0 bytes. 1GB exfiltrated to Ukraine.

![CAN-038 The Ventriloquist](screenshots/caso38.png)

**CAN-018 — The Ghost in the Machine**

847 commands at exactly 300.000-second intervals. Zero errors. Zero retries.
70.5 hours. Temporal entropy: 0.00 bits. The process does not exist in memory.
41.3GB exfiltrated.

![CAN-018 The Ghost in the Machine](screenshots/caso18.png)

---

## Self-Correction Architecture

`validate_and_correct_analysis` checks for four Peircean fallacies before
finalizing any MALICE verdict:

1. **Premature Abduction** — skipped Firstness, jumped to conclusions
2. **False Secondness** — used generic context instead of host-specific baseline
3. **Habitless Thirdness** — inferred pattern without supporting artifacts
4. **Carnegie Bias** — confused operational error with intentional manipulation

**The Mandatory Refutation Protocol (Eco's Razor):**

Before any MALICE verdict, VIGÍA must:
1. Formulate the strongest possible innocent explanation
2. Test it against the complete evidence set
3. Populate `devil_advocate` — an empty field invalidates the verdict under
   the Daubert standard

Downgrading MALICE to SUSPICION through successful refutation is the system
working correctly. Conservative verdicts protect against wrongful attribution.

---

## Academic Documentation

VIGÍA is documented in four languages for accessibility across the international
forensic and academic communities:

| Language | Documents |
|----------|-----------|
| English | `docs/VIGIA_TECHNICAL_STATE_EN.md`, `KNOWN_LIMITATIONS.md`, `DAUBERT_JUDICIAL.md` |
| Spanish | `docs/VIGIA_ESTADO_TECNICO_ES.md`, `DAUBERT_JUDICIAL_ES.md`, `INSTALL_ES.md` |
| Russian | `docs/academic/` (in progress) |
| Chinese | `docs/academic/` (in progress) |

Theoretical grounding: Peircean semiotics (Firstness/Secondness/Thirdness),
Carnegie inverted persuasion detection, Gricean cooperative principle forensics,
Eco's theory of overinterpretation, Daubert standard for scientific evidence.

---

## Judging Criteria Alignment

| Criterion | VIGÍA Implementation |
|-----------|---------------------|
| **Autonomous Execution** | `vigia_agent.py` — self-correcting agentic loop, `MAX_ITERATIONS=3`, deterministic contradiction detection |
| **IR Accuracy** | Probabilistic verdicts (0.0–0.99, never binary); confirmed vs. inferred always distinguished |
| **Breadth & Depth** | 21 tools; `AbductiveHuntingStrategy` prioritizes via `value / (cost × spoofability)` |
| **Constraint Implementation** | `_sanitize_path`, `_sanitize_grep_pattern`, `@_rate_limit`, magic-byte validation, Kassandra Protocol |
| **Audit Trail** | `chain_of_custody_hash` (SHA-256), `evidence_graph` with timestamps, HMAC-signed audit chain, full AmicusCuriae |
| **Usability** | 5 deployment modes: fallback (0 tokens), Claude Code + MCP, Ollama (local), batch agent, OpenWebUI |

---

## Repository Structure

```
vigia-intent-analysis/
├── LICENSE                          ← Apache 2.0
├── README.md                        ← This file
├── KNOWN_LIMITATIONS.md             ← L-001 to L-019 (design transparency)
├── SUBMISSION_COMPLIANCE.md         ← Full compliance index for judges
├── INSTALL.md                       ← Extended installation instructions
├── INSTALL_ES.md                    ← Instrucciones en español
├── SECURITY.md                      ← Security policy
├── AUTHORS.md                       ← Anna Tchijova + VIGÍA AI Collective
├── DAUBERT_JUDICIAL.md              ← Daubert compliance design rationale
├── requirements.txt
├── docker-compose.yml
│
├── vigia_sift_bridge_final.py       ← MCP server (21 tools, primary entry point)
├── vigia_scorer.py                  ← Deterministic scorer (Fraction arithmetic)
├── vigia_agent.py                   ← Autonomous forensic agent
├── forensics/verify_ebs_v1.py      ← Bundle verification (stdlib only)
│
├── vigia/
│   ├── core/ebs_v1.py               ← Evidence Bundle Synthesizer
│   ├── core/caie.py                 ← CrossArtifactIncongruenceEngine
│   ├── core/trust_levels.py         ← HMAC-verified trust computation
│   ├── inference/likelihood_engine.py ← KDE + Ledoit-Wolf
│   └── pipeline/                    ← Integration bridge + normalizer
│
├── data/
│   ├── cases/consolidated_canonical/ ← 52 canonical cases (VIGIA-CAN-001–052)
│   ├── cases/converted/             ← 18 real cases (VIGIA-REAL-*)
│   ├── cases/benign/                ← 15 benign cases
│   └── cases/legacy/                ← BREAK corpus (16 cases)
│
├── results/
│   └── srl2018/                     ← SRL-2018 investigation outputs
│       ├── VIGIA-REAL-SRL-DMZ-FTP_bundle.json
│       └── VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md
│
├── screenshots/                     ← Demo screenshots
│   ├── diagrama1.png – diagrama8.png ← Architecture diagram screens
│   ├── caso31.png, caso38.png, caso18.png ← Canonical case demos
│   ├── casoreal7.png, casorealsrl.png ← Real case demos
│   ├── selfcorection.png            ← Self-correction sequence
│   ├── test148.png, test3.png       ← Test suite results
│   └── testreal.png, test55.png     ← EBS and real case tests
│
├── docs/
│   ├── vigia_diagrams.html          ← Interactive architecture diagrams
│   ├── vigia_commands_en.html       ← English command reference
│   ├── vigia.html                   ← Mathematical logic simulator
│   └── academic/                    ← Multilingual documentation (193 modules)
│
└── tests/
    ├── run_all_cases.py             ← Full corpus evaluation
    ├── test_red_team.py             ← Red team tests
    └── test_ebs_v1_integration.py   ← EBS v1 integration tests
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

`validate_case.py` validates any VIGÍA case file against the EBS v1 schema
before running it through the pipeline. Checks for required fields (`case_id`,
`expected_verdict`, `artifacts`), valid `evidence_type` values against the CAIE
whitelist, minimum `acquisition_hash` length (64 hex chars), and `examiner_id`
presence. Exits with code 0 if valid, 1 with a detailed error report if not.

```bash
python3 validate_case.py data/cases/VIGIA-REAL-001.json
```

---

## License

Apache 2.0 License. See [`LICENSE`](./LICENSE).

Copyright (c) 2026 Anna Tchijova and the VIGÍA AI Collective.

---

*"The question is not what happened, but why did someone make it happen —
and who benefits from that interpretation?"* — VIGÍA
