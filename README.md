# VIGÍA — Intentionality Analysis Bridge for SIFT Workstation

> *"Making deception computationally expensive for the attacker."*
>
> Today, lying in a log or faking an attack is free. VIGÍA charges that price by evaluating the logical fractures in the lie.

**SANS FIND EVIL Hackathon 2026** | Author: Anna Tchijova | Architects: VIGÍA AI Collective (Gemini, Claude, Kimi) | License: MIT

---

## The Paradigm Shift: From IoC to IoI

Current DFIR systems — EDR, SIEM, SOAR — answer: **"What happened?"**

VIGÍA answers: **"Why did it happen, and who benefits?"**

This shift — from **Indicator of Compromise (IoC)** to **Indicator of Intent (IoI)** — is the core innovation of this project.

---

## Architecture Overview

```
EVIDENCE (logs, disk images, memory, network)
         │
         ▼
    SIFT WORKSTATION (forensic extraction)
         │
         ▼
    VIGÍA MCP SERVER ─────────────────────────────────────────────
    │                                                             │
    │  PHASE 1: Chain of Custody (9 tools)                       │
    │  ┌────────────────────────────────────────────────────┐    │
    │  │ mount_sift_evidence  → forensic image mounting      │    │
    │  │ generate_forensic_hash → SHA-256 chain of custody   │    │
    │  │ read_evidence        → single-pass I/O + hash       │    │
    │  │ list_files           → filesystem perimeter         │    │
    │  │ search_pattern       → Python pure search (no grep) │    │
    │  │ list_processes       → memory persistence detection │    │
    │  │ audit_network        → exfiltration channel mapping │    │
    │  │ calculate_shannon_entropy → payload/cipher detect.  │    │
    │  │ audit_image_metadata → GPS + timestamp validation   │    │
    │  └────────────────────────────────────────────────────┘    │
    │                                                             │
    │  PHASE 2: Cognitive Analysis (12 tools)                    │
    │  ┌────────────────────────────────────────────────────┐    │
    │  │ analyze_stylometry      → astroturfing detection    │    │
    │  │ calculate_human_entropy → bot vs. human             │    │
    │  │ infer_intent            → Peirce + Carnegie + RU    │    │
    │  │ detect_habit_incongruence → Living-off-the-Land     │    │
    │  │ detect_human_jitter     → sleep(2) signature        │    │
    │  │ audit_grice_maxims      → linguistic deception      │    │
    │  │ detect_eco_overinterpretation → planted evidence    │    │
    │  │ activate_honey_token    → active exfil trap         │    │
    │  │ reason_with_llm         → novel case abduction      │    │
    │  │ validate_and_correct_analysis → self-correction     │    │
    │  │ reload_phonetic_dict    → hot-reload dictionary     │    │
    │  │ get_phonetic_dict_stats → dictionary diagnostics    │    │
    │  └────────────────────────────────────────────────────┘    │
    └──────────────────────────────────────────────────────────────
         │
         ▼
    CLAUDE CODE (orchestrator)
    Autonomous investigation → Amicus Curiae judicial narrative
```

---

## Theoretical Foundation

### Charles S. Peirce — Abductive Semiotics

Every tool applies the triadic reasoning structure:

- **Firstness** — What is the raw phenomenon? *(the sign itself)*
- **Secondness** — Is this normal here? *(the sign in context)*
- **Thirdness** — What habit does this reveal? *(the inferred law / intent)*

### Dale Carnegie — Manipulation Pattern Recognition

- Authority establishment · Flattery to system · Emotional appeal · Lesser-evil negotiation · False familiarity

### H. Paul Grice — Cooperative Principle Forensics

Honest communication follows four maxims (Quality, Quantity, Relation, Manner). Deception violates at least one. VIGÍA also measures **evaluative adjective density** — emotionally overloaded language is a manipulation signature.

### Umberto Eco — Red Herring and Significant Silence

> "The perfect conspiracy leaves no obvious traces. If there are too many, someone planted them."

**Significant Silence**: The absence of expected artifacts is itself evidence.

---

## Key Technical Differentiators

### Russian Phonetic Evasion Detection

| Phonetic | Cyrillic | Meaning |
|----------|----------|---------|
| `rasia` | Россия | Russia (unstressed О→А) |
| `maskva` | Москва | Moscow (same reduction) |
| `ghbdtn` | привет | hello (keyboard layout slip) |
| `vzlom` | взлом | hack/breach |
| `bomba` | бомба | bomb **[HIGH RISK]** |

The dictionary (`phonetic_dict.json`) is **hot-reloadable** without restarting the server.

### Living-off-the-Land Detection

Standard tools look for unknown processes. VIGÍA looks for **known processes doing unknown things**. `calc.exe` opening an internet connection is not a known malware signature — it is a legitimate tool with anomalous behavior. When the Habit (Thirdness) breaks, intentionality is behind it.

### The Digital Fingerprint of Doubt

A human hesitates, makes typos, varies. A script has `sleep(2)`.

If timing is 2.001s, 2.002s, 1.999s — that is not a person. VIGÍA measures coefficient of variation (CV < 0.05 = automation).

### Memory Habit Incongruence (Volatility integration)

| Claimed (Logs) | Reality (Memory) | Fracture Type |
|----------------|------------------|---------------|
| "Russian RDP login" | LSASS: zero sessions from external IPs | `AUTHENTICATION_WITHOUT_MEMORY_EVIDENCE` |
| "C2 beacon to Russia" | NetScan: no matching connection | `NETWORK_CONNECTION_WITHOUT_MEMORY_EVIDENCE` |

Windows kernel architecture makes these **structurally impossible** to coexist. The fracture proves fabrication.

### Cross-Artifact Discrepancy — ADN Técnico

Authenticity-adjusted score: `score × (1 - spoofability) × weight`

Evidence that is hard to falsify weighs more than evidence that is easy to plant:

| Evidence Type | Spoofability | Effective Weight |
|---------------|-------------|-----------------|
| IP geolocation (cultural) | 0.90 | 1.5% |
| USN journal omission (silence) | 0.20 | 24% |

### Tooling Incoherence (Supply Chain Attribution)

The "technical accent" is harder to fake than the "surface flag":

- Mimikatz en-US, unmodified (entropy 4.2) + claimed Russian APT = contradiction
- Real APTs use custom packers (entropy > 6.5) and localized builds

---

## Installation

### Prerequisites

```bash
python3 --version          # 3.10+
node --version             # 18+ (for Claude Code)
# SIFT Workstation: https://github.com/teamdfir/sift-cli
```

### Install VIGÍA

```bash
git clone https://github.com/[your-username]/vigia-sift.git
cd vigia-sift

pip install -r requirements.txt --break-system-packages

export ANTHROPIC_API_KEY="your_key_here"
export VIGIA_EVIDENCE_DIR="/evidence"   # evidence sandbox
```

### Docker (Recommended for Reproducibility)

```bash
docker build -t vigia:latest .
docker-compose up vigia-mcp

# Run tests inside container
docker run vigia python3 -m pytest tests/ -v
```

### Configure Claude Code

`~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-sift/vigia_sift_bridge.py"]
    }
  }
}
```

### Run

```bash
# Terminal 1 — MCP server
python3 vigia_sift_bridge.py

# Terminal 2 — Claude Code
claude
```

---

## Usage Examples

### Autonomous Investigation (single command)

```
Analyze the evidence at /evidence/case_001/ and determine whether there is
malicious intent. Use VIGÍA tools to calculate entropy, detect habit anomalies,
and generate a forensic narrative explaining the PURPOSE of each finding.
```

### Astroturfing Detection

```
I have three forum accounts. Analyze whether they belong to the same entity.
Texts are in /evidence/forum_posts/. Use "vectores_incidencia" as the honeypot term.
```

### Memory vs. Log Staging Detection

```
Mount the image at /evidence/server.E01. Logs claim a Russian RDP login at 03:00 UTC.
Compare against memory to determine if the login actually happened.
```

---

## Investigation Flow

```
INITIAL SUSPICION
      │
      ├─ Evidence too perfect?   → detect_eco_overinterpretation
      │                             → go to memory FIRST (skip logs)
      │
      ├─ Is it human?            → calculate_human_entropy
      │                             detect_human_jitter
      │
      ├─ Is it one identity?     → analyze_stylometry
      │
      ├─ What does it want?      → infer_intent
      │                             audit_grice_maxims
      │
      ├─ Is memory consistent?   → detect_habit_incongruence
      │                             (Volatility: LSASS vs logs)
      │
      ├─ Tooling consistent?     → analyze tooling entropy
      │                             check cultural vs. technical match
      │
      └─ Before reporting        → validate_and_correct_analysis
                                    (Peircean fallacy check)
```

---

## Judging Criteria Alignment

| Criterion | VIGÍA Implementation |
|-----------|---------------------|
| **Autonomous Execution** | PeircePlanner decides next tool, handles failures with `FALLBACK_TOOLS`, self-corrects via `validate_and_correct_analysis` |
| **IR Accuracy** | Probabilistic verdicts (0.0–0.99, never binary); hallucinations blocked by structural impossibility; confirmed vs. inferred distinguished in output |
| **Breadth & Depth** | 21 tools; `AbductiveHuntingStrategy` prioritizes depth via `value / (cost × spoofability)` formula |
| **Constraint Implementation** | Architectural guards: `_sanitize_path`, `_sanitize_grep_pattern`, `@_rate_limit`, magic-byte validation — tested in `test_integration_end_to_end.py` |
| **Audit Trail** | `chain_of_custody_hash` (SHA-256), `evidence_graph` with timestamps, full trazability in `AmicusCuriaeNarrative` |
| **Usability** | Docker deployment, one-command investigation, judicial narrative output, reproducible SIFT integration |

---

## File Structure

```
vigia-sift/
├── vigia_sift_bridge.py         ← MCP server (21 tools, hardened)
├── phonetic_loader.py           ← Dynamic dictionary loader
├── phonetic_dict.json           ← Russian phonetic evasion dictionary
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── AUTHORS.md                   ← Anna Tchijova + VIGÍA AI Collective
├── SECURITY.md                  ← Anti-gaslighting policy + hardening
├── tests/
│   └── test_integration_end_to_end.py  ← VIGIA-004, 023, Tooling, Security
└── evidence/                    ← (your evidence datasets here)
    └── .gitkeep
```

---

## Self-Correction Architecture

`validate_and_correct_analysis` checks for four Peircean fallacies:

1. **Premature Abduction** — skipped Firstness, jumped to conclusions
2. **False Secondness** — used generic context instead of host-specific
3. **Habitless Thirdness** — inferred pattern without supporting artifacts
4. **Carnegie Bias** — confused operational error with intentional manipulation

---

## Accuracy & Limitations

**Strengths:**
- Phonetic detection performs well on informal Russian text
- Jitter analysis reliable when timestamps available
- Shannon entropy local block detection catches embedded payloads
- Memory habit incongruence provides structurally irrefutable evidence

**Known Limitations:**
- Stylometry can false-positive on texts < 50 words
- Cultural neutrality calibrated for Rioplatense Spanish
- LLM tools require Anthropic API availability
- Living-off-the-Land habit database covers common Windows processes

**False positive mitigation:** Every tool returns a probability score (0.0–0.99), never a binary verdict. Final narrative is generated after cross-correlation of multiple tools.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastmcp` / `mcp` | MCP server framework |
| `anthropic` | Claude API for LLM reasoning |
| `psutil` | Process monitoring |
| `Pillow` | EXIF metadata extraction |
| `volatility3` | Memory forensics (SIFT) |
| `plaso` | Timeline analysis (SIFT) |
| `yara-python` | Pattern matching (SIFT) |

---

## License

MIT License. See LICENSE.

This project was created for the SANS FIND EVIL Hackathon 2026. The novel contribution is the intentionality analysis framework (Phase 2 tools) built on top of the existing SIFT forensic stack, grounded in Peircean semiotics and Eco's theory of overinterpretation.

---

*"The question is not what happened, but why did someone make it happen — and who benefits from that interpretation?"* — VIGÍA
