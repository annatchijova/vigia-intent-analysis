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
| 6 | Demonstration video | ✅ | [`docs/demo/`](./docs/demo/) — see §6 below |
| 7 | Architecture diagram | ✅ | [`README.md`](./README.md#architecture-overview) + [`docs/architecture/`](./docs/architecture/) |
| 8 | Evidence dataset documentation | ✅ | [`docs/evidence/`](./docs/evidence/) — see §8 below |
| 9 | Accuracy report | ✅ | [`docs/accuracy/`](./docs/accuracy/) — see §9 below |
| 10 | Agent execution logs | ✅ | [`docs/logs/`](./docs/logs/) — see §10 below |

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
- Architecture diagram (ASCII, embedded)
- Installation steps (bare metal and Docker)
- Claude Code MCP configuration
- Ollama configuration
- Usage examples (3 canonical investigation scenarios)
- Known limitations and accuracy caveats
- Full dependency table

Direct link to Installation section: [`README.md#installation`](./README.md#installation)

For extended instructions including SIFT Workstation integration and OpenWebUI:
[`INSTALL.md`](./INSTALL.md)

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
#       "args": ["/path/to/vigia-intent-analysis/vigia_sift_bridge.py"]
#     }
#   }
# }

python3 vigia_sift_bridge.py   # Terminal 1
claude                          # Terminal 2
```

### Option C: Ollama (local LLM, no API key required)

```bash
ollama pull llama3.1
python3 vigia_sift_bridge.py --backend ollama --model llama3.1
```

### Option D: CLI (no LLM required — deterministic core only)

```bash
python3 run_case.py --case data/cases/VIGIA_CASE_001.json
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

**Location:** [`docs/demo/`](./docs/demo/)

The demonstration video covers:
1. Full investigation of a staged evidence set (memory + logs + network)
2. Detection of timestamp fabrication (USN Journal gap + TIMESTAMP_PRECISION_ANOMALY)
3. Cross-artifact incongruence: claimed Russian RDP login vs. LSASS memory evidence
4. Generation of Amicus Curiae judicial narrative
5. SHA-256 bundle verification with `verify_ebs_v1.py`

**Direct link:** `docs/demo/vigia_demo_2026.mp4`

> If video is not yet uploaded at review time, the judge can reproduce the identical
> investigation with: `python3 run_demo.py --case data/cases/VIGIA_CASE_DEMO.json`
> Expected runtime: ~90 seconds. Expected output: `MALICE` verdict, confidence 0.87.

---

## §7 — Architecture Diagram

### Embedded (ASCII) — README.md

The full architecture diagram is embedded in [`README.md#architecture-overview`](./README.md#architecture-overview).

### High-Resolution Diagram

**File:** [`docs/architecture/vigia_architecture.png`](./docs/architecture/vigia_architecture.png)

```
┌─────────────────────────────────────────────────────────────────┐
│                       SIFT WORKSTATION                          │
│  mount_evidence → hash_chain → analyze_artifacts → export       │
└────────────────────────┬────────────────────────────────────────┘
                         │  Raw forensic artifacts
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIGÍA MCP SERVER                             │
│                  (vigia_sift_bridge.py)                         │
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
│        (temporal fractures, cryptographic inconsistency,        │
│         staging artifacts, USN journal gaps)                    │
│                                                                 │
│  EBS v1: Evidence Bundle Synthesizer                            │
│        (Noisy-OR composite, Fraction arithmetic, SHA-256 seal)  │
│                                                                 │
│  SIFT BRIDGE: 21 MCP tools                                      │
│        Phase 1: Chain of Custody (9 tools)                      │
│        Phase 2: Intentionality Analysis (12 tools)              │
└────────────────────────┬────────────────────────────────────────┘
                         │  Sealed ForensicBundle (JSON + SHA-256)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PEIRCE PLANNER — External LLM Orchestrator            │
│  Claude Code / Ollama                                           │
│  Role: translate sealed bundle → Amicus Curiae narrative        │
│  INVARIANT: LLM is OUTSIDE the mathematical decision loop.      │
│             It cannot alter scores. It can only narrate.        │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              Amicus Curiae Judicial Narrative
              (confirmed findings vs. inferred hypotheses
               clearly distinguished — Daubert compliant)
```

---

## §8 — Evidence Dataset Documentation

**Location:** [`docs/evidence/`](./docs/evidence/) and [`data/cases/`](./data/cases/)

### Dataset Summary

| Dataset | Cases | Type | Purpose |
|---------|-------|------|---------|
| Canonical corpus v2 | 57 | Synthetic + real-world patterns | Evaluation ground truth |
| Break cases | 10 | Adversarial / evasion attempts | Robustness testing |
| Benign cases | 15 | Legitimate activity | False positive calibration |

### Case Format

Each case is a JSON file with the following structure:

```json
{
  "case_id": "VIGIA_CASE_001",
  "description": "Staged Russian APT false flag — timestamp fabrication",
  "expected_verdict": "MALICE",
  "expected_confidence_min": 0.75,
  "artifacts": {
    "memory_dump": "evidence/case_001/memory.raw",
    "event_logs": "evidence/case_001/evtx/",
    "network_capture": "evidence/case_001/traffic.pcap",
    "mft": "evidence/case_001/mft.bin"
  },
  "ground_truth_fractures": ["USN_JOURNAL_GAP", "TIMESTAMP_PRECISION_ANOMALY"],
  "provenance": "Synthetic — VIGÍA AI Collective, May 2026"
}
```

### Canonical Vectors (Determinism Verification)

**File:** [`docs/protocols/P2/canonical_vectors_p2.json`](./docs/protocols/P2/canonical_vectors_p2.json)  
**Hash manifest:** [`docs/protocols/P2/canonical_vectors_p2_sha256.txt`](./docs/protocols/P2/canonical_vectors_p2_sha256.txt)

These 22 canonical vectors verify determinism: any correct implementation produces
bit-identical outputs for all 22 vectors. This is the reproducibility guarantee
required for Daubert compliance.

---

## §9 — Accuracy Report

**Location:** [`docs/accuracy/`](./docs/accuracy/)  
**Primary file:** [`docs/accuracy/ACCURACY_REPORT.md`](./docs/accuracy/ACCURACY_REPORT.md)

### Summary Results (Canonical Corpus v2 — 57 cases)

| Verdict | Cases | Correct | Accuracy |
|---------|-------|---------|----------|
| MALICE | 32 | 28 | 87.5% |
| SUSPICION | 10 | 8 | 80.0% |
| NOISE/UNKNOWN | 15 | 14 | 93.3% |
| **Overall** | **57** | **50** | **87.7%** |

### Known Limitations Affecting Accuracy

Documented in [`known_limitations.md`](./known_limitations.md). Key items:

- **L-001 through L-004:** 4 BREAK cases return SUSPICION instead of MALICE —
  evasion-by-minimal-signal attacks that defeat single-artifact detection. Conservative
  by design: false negatives preferred over false positives in forensic context.

- **L-009:** `NETWORK_VS_HOST` fracture is categorical MALICE — may over-classify
  legitimate split-tunnel/NAT scenarios. Deferred post-hackathon.

- **L-010:** `TIMESTAMP_PRECISION_ANOMALY` severity 0.95 — may over-classify
  API-normalized timestamps. Deferred post-hackathon.

All limitations are documented with rationale, workarounds, and post-hackathon
remediation plans. Transparency is a Daubert requirement.

### Reproduce Accuracy Report

```bash
python3 evaluate_detector.py \
  --corpus data/cases/ \
  --include-benign data/cases/benign/ \
  --include-break data/cases/converted/ \
  --output docs/accuracy/ACCURACY_REPORT.md
```

---

## §10 — Agent Execution Logs

**Location:** [`docs/logs/`](./docs/logs/)

### Log Types

**Chain of Custody Log** — generated by every investigation:
```
docs/logs/chain_of_custody_CASE_001_20260526T143022Z.json
```

**Execution Log** — full audit trail with timestamps, tool calls, intermediate scores:
```
docs/logs/execution_log_CASE_001_20260526T143022Z.jsonl
```

**Bundle Hash Manifest** — SHA-256 seal for reproducibility verification:
```
docs/logs/bundle_manifest_CASE_001_20260526T143022Z.txt
```

### Generate Logs

```bash
# Run a case and capture logs
python3 run_case.py \
  --case data/cases/VIGIA_CASE_001.json \
  --log-dir docs/logs/ \
  --chain-of-custody

# Verify a bundle (stdlib only, no VIGÍA dependencies)
python3 verify_ebs_v1.py docs/logs/bundle_CASE_001.json
```

### Sample Execution Log Entry

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

## Verification Commands (for judges)

```bash
# 1. Verify the LICENSE exists and is MIT
head -3 LICENSE

# 2. Verify determinism — canonical vectors must pass
python3 check_determinism.py

# 3. Run the demo investigation
python3 run_demo.py --case data/cases/VIGIA_CASE_DEMO.json

# 4. Verify a sealed bundle (no dependencies, stdlib only)
python3 verify_ebs_v1.py docs/logs/demo_bundle.json

# 5. Reproduce accuracy report
python3 evaluate_detector.py --corpus data/cases/ --output /tmp/accuracy.md
```

---

## Contact

**Principal Investigator:** Anna Tchijova  
**Repository:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Hackathon track:** SANS FIND EVIL 2026  

*"The question is not what happened, but why did someone make it happen — and who benefits from that interpretation?"* — VIGÍA
