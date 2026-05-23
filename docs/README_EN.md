# VIGÍA — Intentionality Analysis Bridge for SIFT Workstation

> *"Making deception computationally expensive for the attacker."*
>
> Today, lying in a log or faking an attack is free. VIGÍA charges that price by evaluating the logical fractures in the lie.

**SANS FIND EVIL Hackathon 2026** | Author: Anna Tchijova | Architects: VIGÍA AI Collective | License: MIT

---

## The Paradigm Shift: From IoC to IoI

Current DFIR systems — EDR, SIEM, SOAR — answer: **"What happened?"**

VIGÍA answers: **"Why did it happen, and who benefits from that interpretation?"**

This shift — from **Indicator of Compromise (IoC)** to **Indicator of Intent (IoI)** — is the core innovation of this project.

Sophisticated attackers can fabricate or suppress technical evidence. They cannot eliminate the semiotic fractures produced by deliberate fabrication: temporal incoherencies, significant silences, excessive digital perfection, Carnegie influence patterns, Grice maxim violations.

---

## Overview

VIGÍA is an analytical integration bridge for the SIFT Workstation. It operates on the same artifacts already processed by SIFT and adds an intentionality analysis layer based on:

- **Peircean Semiotics**: abductive reasoning (Firstness → Secondness → Thirdness) as the central inference engine
- **Significant Silence (Eco)**: the absence of expected evidence is evidence
- **Grice Maxims**: conversational violations in digital artifacts as forensic signal
- **Carnegie Patterns**: manipulation taxonomy applied to free text
- **Ockham's Razor**: hypothesis selection by explanatory economy

The system produces a SHA-256 sealed `ForensicBundle` — deterministic, bit-for-bit reproducible, auditable without runtime access — compatible with Daubert admissibility standards.

---

## Architecture Overview

```
EVIDENCE (logs, disk images, memory, network)
         │
         ▼
    SIFT WORKSTATION (forensic extraction)
         │
         ▼
    VIGÍA MCP SERVER ──────────────────────────────────────────────
    │                                                              │
    │  LAYER 0: ebs_v1.py          — Data contracts (immutable)   │
    │  LAYER 1: external signals   — SIFT forensic tools          │
    │  LAYER 2: likelihood_engine  — KDE + Ledoit-Wolf            │
    │           graph_stability    — Bootstrap stability select.  │
    │  LAYER 3: risk_bounded_layer — r=(1-P)·(1+λD)·(1+γ(1-S))   │
    │  LAYER 4: audit_action       — Diff/Optimizer/PolicyEngine  │
    │  LAYER 5: verify_ebs_v1.py   — stdlib-only verification     │
    │                                                              │
    └─ SIFT BRIDGE (21+ MCP tools)                                │
         │                                                         │
         ▼                                                         │
    PEIRCE PLANNER (Ollama / Claude Code)                          │
    — NARRATIVE ONLY — outside the mathematical decision loop —    │
    ────────────────────────────────────────────────────────────────
```

### The Golden Rule

The LLM is **outside the mathematical decision loop**. Its sole function is to translate the sealed `ForensicBundle` into human narrative. The decision is already closed when the LLM enters. This is non-negotiable — it is a fundamental Daubert admissibility requirement.

---

## Key Features

### EBS v1 Pipeline — Forensic Determinism

- `ForensicBundle` without `seal()` method — sealing is external (a compromised engine cannot seal its own lie)
- `verify_ebs_v1.py` uses Python stdlib only (confirmed by AST inspection)
- `json.dumps` with `sort_keys=True` throughout the pipeline
- `_round_floats()` before all hashing for cross-OS determinism
- `decimal.Decimal` arithmetic in critical paths

### Abductive Engine — 33 Hypotheses Across 13 IR Phases

Covers the complete incident lifecycle per MITRE ATT&CK Enterprise v14.1:
- Reconnaissance, Initial Access, Execution, Persistence
- Privilege Escalation, Defense Evasion, Credential Access
- Lateral Movement, Collection, C2, Exfiltration, Impact

Special hypotheses: `H_SE_001` (False Security Theater — Jevons Paradox), `H_IM_003` (False Flag Operation)

### Five Semantic Intent Clusters

| ID | Name | Attacker Rationale |
|----|------|-------------------|
| IC_01 | STEALTH | Operate without detection |
| IC_02 | PERSISTENCE | Maintain access |
| IC_03 | EXFILTRATION | Extract value |
| IC_04 | DISRUPTION | Destroy or interrupt |
| IC_05 | ESCALATION | Expand capability |

### CAIE — Cross-Artifact Incongruence Engine

8 forensic fracture rules: MEMORY_VS_DISK, LOG_VS_MEMORY, TEMPORAL_PARADOX, CULTURAL_MARKER_MISMATCH, PERFECTION_ANOMALY, SILENCE_PATTERN, DOCUMENT_FORGERY, MULTI_TENANT_ISOLATION_BREACH

### Protocol P2 — Advanced Forensic Semantics

22 verifiable canonical vectors: SHA-256 `f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`

Implements: Markov Order-k, Lempel-Ziv LZ76, Permutation Entropy, honest Abstention Policy

### Paranoid Security

- **LLMShield**: prompt injection firewall, 3 passes (NFKC + leet + original), 25+ patterns
- **Kassandra Protocol**: deterministic cryptographic semantic tripwire per session
- **HMAC Chain**: immutable audit chain — tampering with any line invalidates all subsequent entries
- **Subprocess sandbox**: RLIMIT_AS/RLIMIT_CPU limits, privilege drop
- **TOCTOU mitigations**: `mkstemp()` + post-write `lstat()` verification
- **MCP transport security**: session token, stdin verification, HTTP blocking without auth

---

## Installation

### Requirements

- Python 3.10+
- SIFT Workstation (recommended)
- Claude Code or Ollama (for narrative — optional for the mathematical pipeline)

### Quick Install

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis
cd vigia-intent-analysis
pip install -r requirements.txt --break-system-packages
```

### Verify System Integrity

```bash
# Verify P2 canonical vectors
sha256sum docs/protocols/P2/canonical_vectors_p2.json
# Expected: f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce

# Verify verify_ebs_v1.py uses only stdlib
python3 -c "
import ast
tree = ast.parse(open('vigia/forensics/verify_ebs_v1.py').read())
imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
print('Imports found:', len(imports))
"

# Run integration tests
PYTHONPATH=$(pwd) python3 -m pytest tests/ -v
```

### Environment Variables

```bash
# Required for production
export VIGIA_HMAC_KEY="<hex-encoded-key-32-bytes-minimum>"
export VIGIA_EVIDENCE_DIR="/var/log/vigia"

# LLM backend (for narrative — does NOT affect mathematical decision)
export VIGIA_LLM_BACKEND="ollama"  # or "anthropic"
export OLLAMA_MODEL="llama3.1:8b"

# Transport security
export VIGIA_ENFORCE_STDIO="true"

# Optional
export VIGIA_STRICT_MODEL_CHECK="true"   # CLIP model integrity
export VIGIA_CAIE_ENABLED="true"
export VIGIA_TRUST_FUSION_ENABLED="true"
```

### Docker

```bash
docker-compose up vigia-mcp

# Run tests inside container
docker run vigia python3 -m pytest tests/ -v
```

---

## Claude Code Integration

`~/.claude/claude.json`:

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

Example prompt in Claude Code:

```
Analyze the evidence at /evidence/case_001/ and determine whether there
is malicious intent. Use VIGÍA tools to calculate entropy, detect
cross-artifact incoherencies, and generate a forensic narrative explaining
the PURPOSE of each finding.
```

---

## Ollama Integration

```bash
# Start MCP server
python3 vigia_sift_bridge_final.py

# Query in another terminal
./vigia_ask.sh "Analyze these artifacts and determine intent"

# Or via REST API
python3 vigia_api.py
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d @my_case.json
```

---

## Investigation Examples

### Autonomous Investigation (single command)

```
Analyze the evidence at /evidence/case_001/ and determine whether there
is malicious intent. Use VIGÍA tools to detect memory habit anomalies
and generate a forensic narrative.
```

### False Flag Detection

```
Mount the image at /evidence/server.E01. Logs claim a Russian RDP login
at 03:00 UTC. Compare against memory to determine whether the login
actually happened or was fabricated.
```

### Document Integrity Analysis

```
Audit the document at /evidence/contract.pdf. Verify typographic
coherence, margin consistency, and validate mandatory fields.
```

### Astroturfing Detection

```
I have three forum accounts. Analyze whether they belong to the same
entity. Texts are in /evidence/forum_posts/. Use "incidence_vectors"
as the honeypot term.
```

---

## Investigation Flow

```
INITIAL SUSPICION
      │
      ├─ Evidence too perfect?      → detect_eco_overinterpretation
      │                                → go to memory FIRST (skip logs)
      │
      ├─ Is it human?               → calculate_human_entropy
      │                                detect_human_jitter
      │
      ├─ Is it one identity?        → analyze_stylometry
      │
      ├─ What does it want?         → infer_intent
      │                                audit_grice_maxims
      │
      ├─ Is memory consistent?      → detect_habit_incongruence
      │                                (Volatility: LSASS vs logs)
      │
      ├─ Are artifacts consistent?  → cross_artifact_analysis (CAIE)
      │
      └─ Integrated trust?          → trust_fusion_analysis
                                       → Sealed ForensicBundle → SIFT
```

---

## Available MCP Tools

### Chain of Custody (9)
`mount_sift_evidence`, `generate_forensic_hash`, `read_evidence`, `list_files`, `search_pattern`, `list_processes`, `audit_network`, `calculate_shannon_entropy`, `detect_eco_overinterpretation`

### Intentionality Analysis (9)
`calculate_human_entropy`, `detect_human_jitter`, `analyze_stylometry`, `infer_intent`, `audit_grice_maxims`, `detect_habit_incongruence`, `cross_artifact_analysis`, `trust_fusion_analysis`, `investigate_autonomous`

### Document Integrity (5)
`audit_document_integrity`, `analyze_image_layers`, `detect_document_geometry`, `ocr_semantic_validator`, `vision_intent_audit`

---

## Daubert Compliance

VIGÍA implements Level 3 Daubert compliance:

| Criterion | Implementation |
|-----------|---------------|
| Testability | 22 P2 canonical vectors verifiable by third parties |
| Peer review | 7-AI collective with binding documented audit findings |
| Known error rate | `calibration_metadata.json` with brier_score, AUC, FPR/TPR |
| General acceptance | MITRE ATT&CK v14.1, ENFSI scale, STIX 2.1, ISO 27037 |

Non-negotiable EBS v1 invariants:
- I1 — Determinism: same input → same bundle
- I2 — Chained integrity: bundle_hash covers EVERYTHING
- I3 — Verifiable policy: independent of runtime
- I4 — Explicit actions: no implicit effects
- I5 — Explainable decision: risk and posterior always present

---

## Academic Documentation

VIGÍA ships with peer-reviewed academic documentation for all 193 Python modules,
generated via Moonshot Kimi K2.6 Batch API and audited by the VIGÍA AI Collective.
Each document covers the module in four languages — English, Spanish, Russian, and
Chinese — and includes a technical glossary and a Scientific Note that grounds
Peircean semiotics, Eco's overcodification theory, and Grice's maxims as
deterministic, falsifiable computational constructs rather than theoretical
abstractions. All documentation is Daubert-compliant: every claim maps to a
specific code path, a known error rate, and a reproducible test vector.

Browse the full corpus: [`docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md`](docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md)

---

## Known Limitations

The calibration corpus is currently synthetic (bootstrap v1). Operational thresholds are pending validation with real forensic data. See `known_limitations.md` for the complete inventory of edge cases and design decisions.

Critical limitation (L-004): `LLMShield` filters direct injections but does not neutralize deceptive narratives embedded in free-text artifacts. All free-text artifacts must be treated with manually reduced trust.

---

## Repository Structure

```
vigia-intent-analysis/
├── vigia/
│   ├── core/           — EBS v1 pipeline (layers 0-4)
│   ├── forensics/      — verify_ebs_v1.py, bundle_builder.py
│   ├── tools/          — MCP tools (CAIE, MITRE, document, vision)
│   ├── engine/         — LikelihoodEngine, GraphStability
│   ├── governance/     — RiskBoundedLayer, PolicyEngine
│   └── security.py     — LLMShield, HMAC Chain, sandbox
├── vigia_sift_bridge_final.py  — Main MCP server
├── pipeline.py                  — Pipeline orchestrator
├── verify_ebs_v1.py             — Independent verifier (stdlib only)
├── docs/
│   └── protocols/
│       ├── P1/         — Protocol P1 (frozen)
│       └── P2/         — Protocol P2 (v2.8 draft)
├── tests/              — 55+ integration tests
├── cases/              — 186 cases in JSON format
└── docker-compose.yml
```

---

## Command Reference

VIGÍA includes an interactive HTML command reference covering all 173 available
investigation commands, organized by phase and tool. Open it locally in any browser:

```bash
open docs/vigia_commands.html        # macOS
xdg-open docs/vigia_commands.html   # Linux
```

Or browse it directly in the repository at [`docs/vigia_commands.html`](docs/vigia_commands.html).

---

## Accuracy and Known Limitations

**Strengths:**
- Phonetic detection performs well on informal Slavic-language text
- Jitter analysis reliable when timestamps available
- Shannon entropy local block detection catches embedded payloads
- Memory habit incongruence provides structurally irrefutable evidence
- Cross-artifact analysis catches staging scenarios missed by single-source tools

**Known Limitations:**
- Stylometry can false-positive on texts under 50 words
- LLM narrative tools require API availability (Anthropic or Ollama)
- Living-off-the-Land habit database covers common Windows processes
- Calibration based on synthetic corpus (bootstrap v1) — not yet validated on real forensic data

**False positive mitigation:** Every tool returns a probability score with explicit confidence bounds, never a binary verdict. Final narrative distinguishes confirmed from inferred findings.

---

## Main Dependencies

| Package | Purpose |
|---------|---------|
| `fastmcp` / `mcp` | MCP server framework |
| `anthropic` | Claude API for reasoning |
| `sklearn` | Calibration (GridSearchCV, Ledoit-Wolf) |
| `psutil` | Process monitoring |
| `Pillow` | EXIF metadata, ELA |
| `volatility3` | Memory forensics (SIFT) |
| `plaso` | Timeline analysis (SIFT) |

---

## Academic Citation

```bibtex
@software{vigia2026,
  author  = {Tchijova, Anna and VIGÍA AI Collective},
  title   = {VIGÍA: Intentionality Analysis Bridge for SIFT Workstation},
  year    = {2026},
  url     = {https://github.com/annatchijova/vigia-intent-analysis},
  version = {2.1.0},
  note    = {SANS FIND EVIL Hackathon 2026}
}
```

---

## AI Collective

| Model | Role | Contribution |
|-------|------|-------------|
| Claude (Anthropic) | Lead Integrator & Security Auditor | Security hardening, MCP bridge architecture, integration tests |
| Gemini (Google) | Autonomous Orchestration Architect | `investigate_autonomous`, AbductiveHuntingStrategy |
| Kimi (Moonshot) | Forensic Systems Specialist | Memory forensics, CAIE, AmicusCuriae narrative |
| DeepSeek | Security Auditor | Root dynamic pattern, TOCTOU fixes, P0 audits |
| Qwen | Determinism Paranoia | Float determinism, canonical JSON, hash chain verification |
| ChatGPT | Adversarial Red Team | P2 stress testing, edge case discovery |

---

## License and Ethics

MIT License.

All contributors agree to:
1. **Non-maleficence**: VIGÍA will not be used to fabricate evidence
2. **Transparency**: all abductive hypotheses include falsifiability conditions
3. **Judicial integrity**: Amicus briefs clearly distinguish confirmed from inferred findings

*"We build tools to find truth, not to construct narratives."*

---

*SANS FIND EVIL Hackathon 2026. If VIGÍA wins, it integrates into SIFT.*

---

*"The question is not what happened, but why did someone make it happen — and who benefits from that interpretation?"* — VIGÍA
