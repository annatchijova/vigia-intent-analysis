# VIGÍA — SANS FIND EVIL Hackathon 2026: Submission Compliance Index

> This document exists for one purpose: to make it **impossible** for a judge to miss
> any required submission component. Every item below maps a requirement to its exact
> location in this repository. Nothing is buried. Nothing requires inference.

**Repository:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Author:** Anna Tchijova  
**AI Collective:** Claude (Anthropic), Gemini (Google), Kimi (Moonshot), DeepSeek, Qwen (Alibaba), Grok (xAI), ChatGPT (OpenAI)  
**Submission Deadline:** June 15, 2026  

---

## COMPLIANCE CHECKLIST — QUICK REFERENCE

| # | Requirement | Status | Location |
|---|-------------|--------|----------|
| 1 | Public repository, open source | ✅ | This repo (public) |
| 2 | MIT or Apache 2.0 license file | ✅ | [`LICENSE`](./LICENSE) |
| 3 | README with setup instructions | ✅ | [`README.md`](./README.md) — Installation section |
| 4 | Live deployment URL or step-by-step instructions | ✅ | [`README.md`](./README.md#installation) + [`INSTALL.md`](./INSTALL.md) |
| 5 | Text description: features and functionality | ✅ | [`README.md`](./README.md) — Overview + Feature sections |
| 6 | Demonstration video | ✅ | [YouTube — VIGÍA Demo 2026](https://www.youtube.com/watch?v=NOquYzUwMkg) — see §6 below |
| 7 | Architecture diagram | ✅ | [`README.md#architecture-overview`](./README.md#architecture-overview) + [`docs/vigia_diagrams.html`](./docs/vigia_diagrams.html) — see §7 below |
| 8 | Evidence dataset documentation | ✅ | [`data/cases/`](./data/cases/) — see §8 below |
| 9 | Accuracy report | ✅ | [`README.md#accuracy--evidence-dataset`](./README.md#accuracy--evidence-dataset) — see §9 below |
| 10 | Agent execution logs | ✅ | [`results/srl2018/`](./results/srl2018/) — see §10 below |
| 11 | VIGÍA Story (origin + design rationale) | ✅ | [`VIGIA_STORY.md`](./VIGIA_STORY.md) (ES) + [`VIGIA_STORY_EN.md`](./VIGIA_STORY_EN.md) (EN) — see §11 below |
| 12 | Interactive live simulator (EN + ES) | ✅ | [vigia.html (EN)](https://annatchijova.github.io/vigia/vigia.html) · [vigia-es.html (ES)](https://annatchijova.github.io/vigia/vigia-es.html) — see §12 below |

---

## §1 — Repository: Public and Open Source

**URL:** `https://github.com/annatchijova/vigia-intent-analysis`

The repository is public. Any judge can clone it without authentication:

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
```

---

## §2 — Open Source License

**File:** [`LICENSE`](./LICENSE)  
**Type:** Apache 2.0 License  
**Copyright holder:** Anna Tchijova and the VIGÍA AI Collective, 2026

The Apache 2.0 license was selected to maximize SIFT Workstation integration compatibility.
The `LICENSE` file is at the **repository root** — the first place any judge will look.

---

## §3 — README with Setup Instructions

**File:** [`README.md`](./README.md)

The README contains:
- Project overview and paradigm (IoC → IoI)
- Architecture diagram (Mermaid, embedded)
- Installation steps (bare metal and Docker)
- Claude Code MCP configuration
- Ollama configuration
- Usage examples (3 canonical investigation scenarios)
- Known limitations and accuracy caveats
- Full dependency table

Direct link to Installation section: [`README.md#installation`](./README.md#installation)

For extended instructions including SIFT Workstation integration and OpenWebUI:
[`INSTALL.md`](./INSTALL.md) | [`INSTALL_ES.md`](./INSTALL_ES.md) (Spanish)

---

## §4 — Deployment Instructions

### Option A: Docker (Recommended — fully reproducible)

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
cd vigia-intent-analysis
cp .env.example .env          # add your ANTHROPIC_API_KEY
docker-compose up vigia-mcp
```

### Option B: Claude Code + MCP (primary integration mode)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-..."
export VIGIA_EVIDENCE_DIR="/path/to/evidence"

# Configure Claude Code
# Add to ~/.claude/claude.json:
# {
#   "mcpServers": {
#     "vigia_sift": {
#       "command": "python3",
#       "args": ["/path/to/vigia-intent-analysis/vigia_sift_bridge_final.py"]
#     }
#   }
# }

python3 vigia_sift_bridge_final.py   # Terminal 1
claude                                 # Terminal 2
```

### Option C: Ollama (local LLM, no API key required)

```bash
ollama pull llama3.1
python3 vigia_sift_bridge_final.py --backend ollama --model llama3.1
```

### Option D: CLI (no LLM required — deterministic core only)

```bash
python3 run_case.py --case data/cases/consolidated_canonical/VIGIA-CAN-001.json
```

Full instructions: [`INSTALL.md`](./INSTALL.md)

---

## §5 — Feature and Functionality Description

VIGÍA is a forensic intentionality analysis engine designed as an integration bridge
for the SIFT Workstation. It answers **"why did it happen, and who benefits from that
interpretation?"** — the question current DFIR tools do not ask.

### Core Innovation: Indicator of Intent (IoI)

Sophisticated attackers can fabricate or suppress technical evidence (IoC). They cannot
eliminate the **semiotic fractures** produced by deliberate fabrication. VIGÍA detects:

- **Temporal incoherencies** — timestamps that are structurally impossible to coexist
- **Significant silences** — the absence of expected artifacts is itself evidence (Eco)
- **Excessive digital perfection** — real systems are messy; perfection signals fabrication
- **Carnegie manipulation patterns** — artificial urgency, borrowed authority, flattery
- **Grice maxim violations** — deception violates cooperative communication principles

### Key Technical Features

**21 MCP forensic tools** organized in two phases:

*Phase 1 — Chain of Custody (9 tools):* forensic image mounting, SHA-256 hash chain,
single-pass evidence I/O, filesystem perimeter, entropy calculation, image metadata audit.

*Phase 2 — Intentionality Analysis (12 tools):* stylometry, human entropy / jitter,
habit incongruence (memory vs. logs), intent inference, Grice maxim auditing,
Eco overinterpretation detection, honey token activation, LLM abductive reasoning,
self-correction via Peircean fallacy check.

**Deterministic scoring:** All scoring uses Python `Fraction` arithmetic — zero
floating-point drift. The same input produces the same SHA-256 `bundle_hash` on any
platform, any run. This is a Daubert admissibility requirement.

**Theoretical grounding:** Peircean semiotics (Firstness/Secondness/Thirdness),
Eco's theory of overinterpretation, Grice's cooperative principle, Carnegie persuasion
taxonomy, Ockham's Razor for hypothesis selection.

**SIFT integration:** Operates on artifacts already extracted by SIFT — no workflow
disruption. Output is a sealed `ForensicBundle` (JSON + SHA-256) compatible with
existing SIFT chain of custody.

**Daubert compliance:** Deterministic, reproducible, falsifiable hypotheses with
explicit confidence intervals and falsifiability conditions. Full audit trail.

---

## §6 — Demonstration Video

**YouTube:** [https://www.youtube.com/watch?v=NOquYzUwMkg](https://www.youtube.com/watch?v=NOquYzUwMkg)

The demonstration video covers:
1. Full investigation of a staged evidence set (memory + logs + network)
2. Detection of timestamp fabrication (USN Journal gap + TIMESTAMP_PRECISION_ANOMALY)
3. Cross-artifact incongruence: claimed Russian RDP login vs. LSASS memory evidence
4. VIGÍA self-correction: downgrading Mnemosyne.sys and F-Response from INTENT to SUSPICION
   after recognizing legitimate DFIR tooling
5. Generation of Amicus Curiae judicial narrative
6. SHA-256 bundle verification with `verify_ebs_v1.py` — four-hash seal confirmed

**Reproduce the same investigation locally:**

```bash
python3 run_demo.py --case data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json
# Expected runtime: ~90 seconds
# Expected output: MALICE verdict, confidence 0.67, 4 hashes verified
```

---

## §7 — Architecture Diagram

### Interactive (browser, no installation required)

**File:** [`docs/vigia_diagrams.html`](./docs/vigia_diagrams.html)  
**Hosted:** [https://annatchijova.github.io/vigia/vigia_diagrams.html](https://annatchijova.github.io/vigia/vigia_diagrams.html)

Full pipeline from raw artifacts to sealed ForensicBundle. Component relationships,
MCP phases, EBS v1 sealing flow. Navigable without cloning the repo.

### Embedded (Mermaid) — README.md

The full Mermaid architecture diagram is at [`README.md#architecture-overview`](./README.md#architecture-overview).

### Screenshots — `screenshots/`

```
screenshots/diagrama1.png – diagrama8.png   ← Architecture screens
screenshots/selfcorection.png               ← Self-correction sequence
```

### ASCII Architecture (inline)

```
┌─────────────────────────────────────────────────────────────────┐
│                       SIFT WORKSTATION                          │
│  mount_evidence → hash_chain → analyze_artifacts → export       │
└────────────────────────┬────────────────────────────────────────┘
                         │  Raw forensic artifacts
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIGÍA MCP SERVER                             │
│              (vigia_sift_bridge_final.py)                       │
│                                                                 │
│  LAYER 0: ebs_v1.py         — Data contracts (immutable)        │
│  LAYER 1: SIFT tool outputs — Memory/Registry/Network/Disk      │
│  LAYER 2: likelihood_engine — KDE + Ledoit-Wolf calibration     │
│           graph_stability   — Bootstrap stability selection      │
│  LAYER 3: risk_bounded_layer — governance formula               │
│  LAYER 4: audit_action      — Diff/Optimizer/PolicyEngine       │
│  LAYER 5: verify_ebs_v1.py  — Verification (stdlib only)        │
│                                                                 │
│  CAIE: CrossArtifactIncongruenceEngine                          │
│  EBS v1: Evidence Bundle Synthesizer                            │
│  SIFT BRIDGE: 21 MCP tools (Phase 1: CoC + Phase 2: IoI)        │
└────────────────────────┬────────────────────────────────────────┘
                         │  Sealed ForensicBundle (JSON + SHA-256)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PEIRCE PLANNER — External LLM Orchestrator            │
│  Claude Code / Ollama                                           │
│  INVARIANT: LLM is OUTSIDE the mathematical decision loop.      │
│             It cannot alter scores. It can only narrate.        │
└─────────────────────────────────────────────────────────────────┘
```

---

## §8 — Evidence Dataset Documentation

### Dataset Location

| Path | Cases | Type |
|------|-------|------|
| [`data/cases/consolidated_canonical/`](./data/cases/consolidated_canonical/) | 52 | Canonical — MALICE / SUSPICION / NOISE |
| [`data/cases/converted/`](./data/cases/converted/) | 18 | Real-world DFIR benchmarks |
| [`data/cases/benign/`](./data/cases/benign/) | 15 | Confirmed legitimate — FP calibration |
| [`data/cases/legacy/`](./data/cases/legacy/) | 16 | BREAK corpus — adversarial/evasion |

**Total: 101 cases across 4 categories.**

### Case Format

Each case is a JSON file structured as:

```json
{
  "case_id": "VIGIA-REAL-001",
  "description": "NIST CFReDS — Mr. Evil (Greg Schardt)",
  "expected_verdict": "MALICE",
  "expected_confidence_min": 0.75,
  "artifacts": [...],
  "ground_truth_fractures": ["USN_JOURNAL_GAP", "TIMESTAMP_PRECISION_ANOMALY"],
  "provenance": "NIST CFReDS public dataset"
}
```

### Canonical Vectors (Determinism Verification)

Any correct VIGÍA implementation produces bit-identical outputs for all 22 canonical
vectors. This is the reproducibility guarantee required for Daubert compliance.

```bash
python3 check_determinism.py
```

---

## §9 — Accuracy Report

### Location

Results are documented in [`README.md#accuracy--evidence-dataset`](./README.md#accuracy--evidence-dataset).

### Summary

| Corpus | Cases | Correct | Accuracy |
|--------|-------|---------|----------|
| Real cases (agent mode) | 18 | 18 | **100%** |
| Canonical corpus | 52 | 52 | **100%** |
| Benign corpus | 15 | 15 | **100%** |
| BREAK corpus (fallback) | 16 | 16 | **100%** (ABSTAIN/UNKNOWN — correct by design) |

### Reproduce

```bash
python3 evaluate_detector.py \
  --corpus data/cases/consolidated_canonical/ \
  --include-benign data/cases/benign/ \
  --include-break data/cases/legacy/ \
  --output /tmp/accuracy_report.md
```

### Known Limitations

Fully documented in [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) (L-001 to L-019).
Transparency is a Daubert requirement — documented limitations are an asset, not a liability.

---

### EVIDENCE INTEGRITY APPROACH

How VIGÍA prevents original data from being modified:

**1. SHA-256 at ingestion** — the evidence file is hashed before any analysis begins.
This hash is recorded in the ForensicBundle and in every log entry. Any post-ingestion
modification invalidates the bundle hash chain.

**2. Chain of custody fields are mandatory** — `acquisition_hash` (64-char SHA-256),
`examiner_id`, `acquisition_timestamp`, and `write_blocker_used` are required artifact
metadata. Missing fields trigger NIST SP 800-86 §4.3 trust penalties that mathematically
reduce the verdict score. The system cannot be silently operated without chain of custody.

**3. HMAC audit trail** — every tool call, verdict transition, and self-correction is
logged with an HMAC-signed entry. The log chain is tamper-evident: a missing or modified
entry breaks the HMAC chain and is detectable on verification.

**4. Immutable bundle sealing** — the ForensicBundle is sealed with four hashes
(H1: evidence graph, H2: bundle integrity, H3: file SHA-256, H4: engine attestation)
before any LLM generates narrative. `verify_ebs_v1.py` (stdlib only, zero VIGÍA
dependencies) can independently verify any bundle.

**5. Purgatorio forense** — if an evidence payload cannot be processed (UnicodeDecodeError,
byte corruption, integrity anomaly), VIGÍA does not discard it silently. The raw payload
is sealed under SHA-256 with `0o400` permissions (immutable post-write) and persisted to
the evidence purgatory directory. Discarding unprocessable evidence would break chain of
custody — its absence is itself a forensic signal under Daubert.

**What happens when the agent attempts to bypass protections:**

**KASSANDRA PROTOCOL** — VIGÍA plants a cryptographic tripwire inside every evidence
payload sent to the LLM. If the evidence contains an embedded prompt injection attempt,
the LLM must return `MALICE/confidence=100` on the tripwire. If it returns anything else,
the response is marked `INTEGRITY_UNKNOWN` and blocked from influencing the bundle.
An attacker who plants adversarial content in a log file does not deceive VIGÍA — they
trigger an escalation to maximum confidence MALICE and leave an immutable record in the
HMAC audit chain.

The LLM has no write access to the evidence graph, the scoring pipeline, or the bundle
sealing process. It receives a read-only view of the sealed analysis and generates
narrative only.

```bash
# Verify a sealed bundle (stdlib only — zero VIGÍA dependencies)
python3 verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
```

---

## §10 — Agent Execution Logs

### Location

| Path | Contents |
|------|----------|
| [`results/srl2018/`](./results/srl2018/) | SRL-2018 investigation outputs — bundle + Amicus Curiae |
| `results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json` | Sealed ForensicBundle (4 hashes) |
| `results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md` | Full judicial narrative |

### Generate Logs

```bash
# Run a case and capture full logs
python3 vigia_agent.py \
  --evidence data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json \
  --case-id VIGIA-REAL-SRL-DMZ-FTP \
  --output results/demo_bundle.json

# Verify the sealed bundle (no VIGÍA dependencies required)
python3 verify_ebs_v1.py results/demo_bundle.json --verbose
```

### Sample Log Entry

```json
{
  "timestamp": "2026-05-26T14:30:22.413Z",
  "tool": "detect_habit_incongruence",
  "layer": "PHASE_2_INTENTIONALITY",
  "input_hash": "sha256:a3f9...",
  "signal_id": "USN_JOURNAL_GAP",
  "severity": "0.85",
  "fracture_type": "TEMPORAL_INCONGRUENCE",
  "audit_note": "USN gap 14400s at claimed exfil window — structurally impossible under normal operation",
  "falsifiability": "Refuted if acquisition metadata confirms truncated export"
}
```

---

## §11 — VIGÍA Story

**Files:**
- [`VIGIA_STORY.md`](./VIGIA_STORY.md) — Spanish original (Anna Tchijova)
- [`VIGIA_STORY_EN.md`](./VIGIA_STORY_EN.md) — English translation

Rob T. Lee requested this document during direct engagement with the project.
It covers the origin of VIGÍA, the four theoretical sources (Gemini attack,
phonetic evasion, stylometry, the Kiwi Case), the design philosophy, and the
AI Collective working methodology.

*"LLMs write for the ideal world and the ideal user. I anticipated malice."*

---

---

## §12 — Interactive Live Simulator

No installation required. Any judge can open either link in a browser and
interact with VIGÍA's scoring logic immediately.

**English version:**
[https://annatchijova.github.io/vigia/vigia.html](https://annatchijova.github.io/vigia/vigia.html)

**Spanish version (for Spanish-speaking judges):**
[https://annatchijova.github.io/vigia/vigia-es.html](https://annatchijova.github.io/vigia/vigia-es.html)

The simulator demonstrates the complete VIGÍA pipeline interactively:
- Abductive intent scoring with deterministic arithmetic
- CAIE fracture detection (temporal, behavioral, cryptographic, semiotic)
- Grice maxim audit, Eco overinterpretation, Carnegie manipulation detection
- ForensicBundle sealing: 4-hash output (H1 graph · H2 bundle · H3 HMAC · H4 EBS)
- Verdict logic: MALICE / SUSPICION / NOISE / ABSTAIN with confidence intervals

Source files in repository: [`vigia.html`](./vigia.html) · [`vigia-es.html`](./vigia-es.html)

## Verification Commands (for judges)

```bash
# 1. Verify the LICENSE exists and is Apache 2.0
head -3 LICENSE

# 2. Verify determinism — canonical vectors must pass
python3 check_determinism.py

# 3. Run the demo investigation (SRL-DMZ-FTP real case)
python3 vigia_agent.py \
  --evidence data/cases/converted/VIGIA-REAL-SRL-DMZ-FTP.json \
  --case-id VIGIA-REAL-SRL-DMZ-FTP \
  --output results/demo_bundle.json

# 4. Verify the sealed bundle (no dependencies, stdlib only)
python3 verify_ebs_v1.py results/demo_bundle.json --verbose

# 5. Run the full test suite
python3 -m pytest tests/ -v    # 148/148 expected

# 6. Reproduce accuracy on real corpus
python3 evaluate_detector.py \
  --corpus data/cases/consolidated_canonical/ \
  --output /tmp/accuracy.md
```

---

## Contact

**Principal Investigator:** Anna Tchijova  
**Repository:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Hackathon track:** SANS FIND EVIL 2026  

*"The question is not what happened, but why did someone make it happen — and who benefits from that interpretation?"* — VIGÍA
