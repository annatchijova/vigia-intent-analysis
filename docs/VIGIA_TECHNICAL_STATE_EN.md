# VIGÍA — Complete Technical System State
## Forensic Intentionality Analysis for SIFT Workstation
### SANS FIND EVIL Hackathon 2026

**Principal Investigator:** Anna Tchijova  
**Audit Collective:** Claude (Anthropic), Kimi (Moonshot), Gemini (Google), DeepSeek, Qwen, ChatGPT (adversarial red team)  
**Repository:** `github.com/annatchijova/vigia-intent-analysis`  
**Document Version:** 1.0 — May 18, 2026  
**Classification:** Technical-forensic — Audience: Rob T. Lee, SANS judges, independent auditors

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Paradigm: From IoC to IoI](#2-paradigm-from-ioc-to-ioi)
3. [Theoretical Foundations](#3-theoretical-foundations)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [EBS v1 Pipeline Layers](#5-ebs-v1-pipeline-layers)
6. [Abductive Reasoning Engine and Hypotheses](#6-abductive-reasoning-engine-and-hypotheses)
7. [MITRE ATT&CK Integration](#7-mitre-attck-integration)
8. [Protocols P1 and P2](#8-protocols-p1-and-p2)
9. [Security Subsystem](#9-security-subsystem)
10. [Calibration Engine and Likelihood Ratio](#10-calibration-engine-and-likelihood-ratio)
11. [MCP Forensic Tools](#11-mcp-forensic-tools)
12. [Claude Code and Ollama Integration](#12-claude-code-and-ollama-integration)
13. [Daubert Compliance](#13-daubert-compliance)
14. [Case Corpus and Dataset](#14-case-corpus-and-dataset)
15. [Implemented Modules — Complete Inventory](#15-implemented-modules--complete-inventory)
16. [Known Limitations and Adversarial Gaps](#16-known-limitations-and-adversarial-gaps)
17. [Git Repository Status](#17-git-repository-status)
18. [Pending Work Through June 15](#18-pending-work-through-june-15)
19. [Bibliography and Technical References](#19-bibliography-and-technical-references)

---

## 1. Executive Summary

VIGÍA is a digital forensic intentionality analysis system designed as an integration bridge for the SIFT Workstation. Unlike conventional DFIR systems that answer "what happened?", VIGÍA answers "why did it happen, and who benefits from that interpretation?"

The system introduces the concept of **Indicator of Intent (IoI)** as a natural evolution of the Indicator of Compromise (IoC). The central premise is that sophisticated attackers can fabricate or suppress technical evidence, but cannot eliminate the semiotic fractures produced by deliberate fabrication: temporal incoherencies, significant silences, excessive digital perfection, Carnegie influence patterns, Grice maxim violations.

The three technical pillars are:

1. **Operationalized Peircean semiotics**: abductive reasoning (Thirdness) is the central inference engine, not a decorative post-processor.
2. **Strict determinism**: every execution over the same input produces the same SHA-256 `bundle_hash`. This is a Daubert admissibility requirement, not an implementation convenience.
3. **Zero-Trust layer isolation**: the LLM (PeircePlanner/Ollama) is explicitly excluded from the mathematical decision loop. Its sole function is to translate the sealed `ForensicBundle` into human narrative. The decision is already closed when the LLM enters.

The system comprises 151 active Python modules, 33+ abductive hypotheses covering 13 IR phases, MITRE ATT&CK Enterprise v14.1 integration, a cryptographic P2 protocol with 22 canonical vectors, and Daubert Level 3 compliance.

---

## 2. Paradigm: From IoC to IoI

### 2.1 The Problem with Current Systems

Current EDR, SIEM, and SOAR systems operate on the implicit premise that attackers do not manipulate the evidence they leave behind. They respond correctly when the attacker is negligent. They fail when the attacker is deliberate.

A sophisticated attacker can:
- Selectively suppress log entries (Significant Silence — Eco)
- Fabricate convincing timestamps (with statistical fractures)
- Use native OS tools (Living-off-the-Land) to evade signature-based detection
- Inject false evidence implicating a third party (False Flag)
- Create documents that appear legitimate but are semantically incoherent

None of these attacks triggers an IoC. All of them leave IoI.

### 2.2 The VIGÍA Proposal

VIGÍA does not replace the existing forensic infrastructure. It augments it with an intentionality analysis layer that operates on the same artifacts already processed by SIFT.

The integration flow:

```
SIFT extracts artifacts
        ↓
VIGÍA receives ForensicBundle with normalized signals
        ↓
Abductive engine evaluates intent hypotheses
        ↓
ForensicBundle sealed with SHA-256 chain
        ↓
Daubert-admissible verdict + narrative
```

Deception has a computational cost. VIGÍA charges it.

---

## 3. Theoretical Foundations

### 3.1 Peirce: Firstness, Secondness, Thirdness

The system applies Charles Sanders Peirce's semiotic triad (1839–1914) as the operational structure of forensic reasoning:

**Firstness:** The signal as it appears, without interpretation. Raw data. A timestamp anomaly, an orphaned memory process, a Shannon entropy outside the expected range. No hypothesis yet. Only observation.

**Secondness:** The signal in relation to a baseline or expectation. The anomaly acquires relational meaning: this timestamp is inconsistent *with respect to* the other artifacts in the same case. This process does not exist in the known habit database. This entropy is too high *compared to* authentic human text.

**Thirdness:** The emergent hypothesis explaining the relationship. Not deduction (not derived from a universal). Not induction (not generalized from a sample). *Abduction*: inference to the best available explanation, falsifiable, with explicit conditions of refutation.

The `AbductionTrace` in each `ForensicBundle` formally records all three stages for each analysis. The forensic expert can audit each step without access to the system's source code.

### 3.2 Eco: Significant Silence and Overinterpretation

Umberto Eco (1932–2016) contributes two operationalized concepts in VIGÍA:

**Significant Silence:** The absence of expected evidence is, in itself, evidence. If a malicious process typically leaves traces in the Windows registry and those traces are absent, the absence is a first-order forensic signal. VIGÍA explicitly detects and evaluates silences.

**Eco's Razor:** The abductive falsification engine. If the available evidence is *too perfect*, if it fits *too well* with the most obvious hypothesis, that is suspicious. An attacker who constructs a perfect crime scene is leaving a different kind of fingerprint. The simplest alternative hypothesis may be that the evidence was fabricated to frame someone else.

### 3.3 Grice: Conversational Maxims Applied to Evidence

H. Paul Grice (1913–1988) postulated that cooperative communication follows four maxims (quantity, quality, relation, manner). VIGÍA applies them to digital evidence:

- **Quantity maxim:** A log that omits the critical period violates the quantity maxim. A document with 500 pages of irrelevant detail does too.
- **Quality maxim:** An unverifiable claim in the artifact.
- **Relation maxim:** Artifacts that bear no relation to the declared context.
- **Manner maxim:** Deliberate ambiguity, unnecessary obscurity.

### 3.4 Carnegie: Manipulation Patterns

Dale Carnegie (1888–1955) documented interpersonal influence patterns. VIGÍA uses them as a manipulation taxonomy in text artifacts: artificial urgency, borrowed authority, access flattery, normalization pressure. The `CarnegieMatcher` detects these patterns with weights calibrated on the VIGÍA v1 corpus.

### 3.5 Ockham: Hypothesis Selection

Ockham's Razor guides selection between competing hypotheses of equal explanatory power. The `OckhamAdversarialEngine` evaluates alternative hypotheses and reports their relative explanatory power.

---

## 4. System Architecture Overview

### 4.1 High-Level View

```
┌─────────────────────────────────────────────────────────────────┐
│                       SIFT WORKSTATION                          │
│  mount_evidence → hash_chain → analyze_artifacts → export       │
└────────────────────────┬────────────────────────────────────────┘
                         │  ForensicBundle (JSON + SHA-256)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIGÍA MCP SERVER                             │
│                                                                 │
│  LAYER 0: ebs_v1.py       — Data contracts (immutable)         │
│  LAYER 1: external signals — SDA/CLI/GCI/SIFT tools            │
│  LAYER 2: likelihood_engine + graph_stability — inference       │
│  LAYER 3: risk_bounded_layer — governance r=(1-P)·(1+λD)·(1+γ) │
│  LAYER 4: audit_action    — Diff/Optimizer/PolicyEngine         │
│  LAYER 5: verify_ebs_v1.py — verification, stdlib only         │
│                                                                 │
│  SIFT BRIDGE: vigia_sift_bridge_final.py (21+ MCP tools)       │
└────────────────────────┬────────────────────────────────────────┘
                         │  Sealed ForensicBundle
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PEIRCE PLANNER (Narrative — external LLM)          │
│  Claude Code / Ollama — ONLY translates bundle to narrative     │
│  DOES NOT participate in the mathematical decision              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Zero-Trust Layer Isolation Principle

Each layer has a strictly defined dependency direction. No layer may import from a higher layer. The dependency graph is a DAG. This guarantees that a compromised component cannot contaminate the attestation process.

The golden rule: **the LLM is outside the mathematical decision loop**. This invariant is non-negotiable. It was proposed by the audit collective and accepted as a fundamental Daubert requirement.

### 4.3 ForensicBundle as Delivery Unit

The `ForensicBundle` is the sealed artifact VIGÍA delivers to SIFT. It contains:

- `evidence_graph`: probabilistic dependency graph between artifacts
- `decision_trace`: posterior / risk / decision with full traceability
- `policy_spec`: active policy verifiable externally
- `actions`: history of executed interventions
- `system_state`: adaptive parameters at sealing time
- `abduction_trace`: Peircean reasoning traceability
- `integrity`: chained SHA-256 hashes (external cryptographic sealing)

The bundle is portable, self-contained, and auditable without access to the runtime.

---

## 5. EBS v1 Pipeline Layers

### 5.1 Layer 0 — Data Contracts (`ebs_v1.py`)

Contains all system data structures. It is the only layer that imports nothing from upper layers. Implemented as pure dataclasses with fallback to Pydantic v2 if available.

Implemented contracts:
- `SignalOutput`: canonical output of all forensic tools
- `EvidenceEdge`: graph edge with bootstrap stability (π ≥ 0.85)
- `EvidenceGraph`: emergent dependency graph
- `DecisionTrace`: posterior/risk/decision triad with verdict
- `PolicyRule` / `PolicySpec`: externally verifiable governance policy
- `ActionRecord`: executed action with full traceability
- `SystemState`: adaptive parameters (λ, γ, ε)
- `IntegrityBlock`: chained SHA-256 hashes
- `AbductionTrace`: Peircean reasoning traceability
- `ForensicBundle`: EBS v1 sealed artifact

**Critical invariant:** `ForensicBundle` has no `seal()` method. Sealing is the exclusive responsibility of `BundleBuilder` (external process). A compromised engine cannot seal its own lie.

### 5.2 Layer 2 — Inference Engine

**`likelihood_engine.py`** — Multivariate KDE with Ledoit-Wolf covariance estimation. Produces the probabilistic posterior over normalized signals. Implements:
- Multivariate KDE with automatic bandwidth
- Ledoit-Wolf covariance shrinkage for small datasets
- `_round_floats()` applied before all hashing for cross-OS determinism
- `decimal.Decimal` arithmetic in critical paths

**`graph_stability.py`** — Stability Selection via Bootstrap (B=500). The evidence graph emerges from data, not hardcoded. An edge (i,j) exists iff π_ij = freq(edge in bootstrap) ≥ τ = 0.85.

Dependency criteria:
- Spearman ρ ≥ threshold_rho (robust to non-normality)
- Mutual Information ≥ threshold_mi (captures non-linearity)
- An edge requires BOTH criteria

This is statistically defensible under Daubert: "This dependency appears in X% of the statistically possible worlds of the calibration dataset."

### 5.3 Layer 3 — Governance and Risk

**`risk_bounded_layer.py`** — Risk function:

```
r = (1 - P) · (1 + λ·D) · (1 + γ·(1 - S))
```

Where:
- `P`: probabilistic posterior (LikelihoodEngine)
- `D`: drift score (divergence from baseline)
- `S`: evidence graph stability
- `λ`, `γ`: adaptive parameters (SelfAdaptiveRiskPolicy)

Thresholds are read from `PolicySpec` via `from_policy_spec()`. **No hardcodes exist**.

### 5.4 Layer 4 — Audit and Action

**`audit_action.py`** — Four components:
- `EvidenceGraphDiff`: detects divergences between runs
- `InterventionOptimizer`: recommends minimal interventions
- `FormalPolicyEngine`: evaluates actions against policy
- `SafeActionExecutor`: executes with complete logging

### 5.5 Layer 5 — Independent Verification

**`verify_ebs_v1.py`** — Independent bundle verifier. **Uses Python stdlib only** (confirmed by AST inspection). Imports nothing from the production runtime. This separation is deliberate: the verifier can validate any bundle without access to the system that produced it.

`BundleBuilder` is not imported by `verify_ebs_v1.py`. They implement the same hashing protocol independently. If they diverge, the protocol is the failure, not the modules.

---

## 6. Abductive Reasoning Engine and Hypotheses

### 6.1 Implemented Hypotheses

The `AbductiveIntentEngine` implements 33 abductive hypotheses across 13 IR phases:

**RECONNAISSANCE:** H_RE_001 (passive OSINT), H_RE_002 (active scanning), H_RE_003 (social engineering recon)

**RESOURCE_DEVELOPMENT:** H_RD_001 (infrastructure acquisition)

**INITIAL_ACCESS:** H_IA_001 (phishing document), H_IA_002 (credential stuffing), H_IA_003 (supply chain compromise)

**EXECUTION:** H_EX_001 (command line abuse), H_EX_002 (scheduled task abuse), H_EX_003 (PowerShell LOtL)

**PERSISTENCE:** H_PE_001 (single persistence), H_PE_002 (multi-mechanism), H_PE_003 (bootkit)

**PRIVILEGE_ESCALATION:** H_PA_001 (token manipulation), H_PA_002 (kernel exploit)

**DEFENSE_EVASION:** H_DE_001 (log fabrication), H_DE_002 (timestamp manipulation), H_DE_003 (anti-forensics tools), H_SE_001 (false security theater — Jevons Paradox applied to security)

**CREDENTIAL_ACCESS:** H_CA_001 (credential dumping), H_CA_002 (keylogging)

**LATERAL_MOVEMENT:** H_LM_001 (pass the hash)

**COLLECTION:** H_CO_001 (data staging for exfil), H_CO_002 (clipboard/screen capture), H_CO_003 (audio/video surveillance)

**COMMAND_AND_CONTROL:** H_C2_001 (domain fronting beacon), H_C2_002 (DNS tunnel C2)

**EXFILTRATION:** H_XF_001 (slow exfil pattern), H_XF_002 (cloud exfil)

**IMPACT:** H_IM_001 (ransomware pattern), H_IM_002 (wiper pattern), H_IM_003 (false flag operation)

### 6.2 Explicit Falsifiability

Each hypothesis has documented falsifiability conditions. This is a Daubert requirement: a forensic hypothesis that cannot be refuted is not scientifically valid. The `OckhamAdversarialEngine` evaluates alternative hypotheses for each verdict.

### 6.3 Five Semantic Intent Clusters

The `MITREClusterer` maps hypotheses to five intent clusters:

| ID | Name | Attacker Rationale |
|----|------|-------------------|
| IC_01 | STEALTH | Operate without detection |
| IC_02 | PERSISTENCE | Maintain access |
| IC_03 | EXFILTRATION | Extract value |
| IC_04 | DISRUPTION | Destroy or interrupt |
| IC_05 | ESCALATION | Expand capability |

---

## 7. MITRE ATT&CK Integration

### 7.1 Master TTP Dictionary

`mitre_mapping.py` implements the centralized master TTP dictionary based on MITRE ATT&CK Enterprise v14.1. Each TTP includes:
- `technique_id`: MITRE ATT&CK ID
- `base_severity`: intrinsic severity [0.0, 1.0]
- `spoofability_score`: ease of fabrication (0.0 = nearly impossible, 1.0 = trivial)
- `evidence_types`: VIGÍA evidence types mapping to this TTP

The `spoofability_score` is an original contribution from VIGÍA to the MITRE framework. Memory evidence (T1055 — Process Injection) has `spoofability=0.10` because it requires real kernel access. Network log evidence (`T1071`) has `spoofability=0.80` because logs are trivially falsifiable.

**This allows forensic experts to weight evidence credibility by its fabrication capability, not just its type.**

### 7.2 STIX 2.1 Export

`mitre_mapping.py` includes `to_stix_sdo()` converting VIGÍA artifacts to valid STIX 2.1 SDOs for direct interoperability with OpenCTI, MISP, and other STIX-consuming DFIR platforms.

### 7.3 Coverage Verification

The `MITREClustering Milestone 2.2` verifies complete coverage:
- `coverage_ratio`: fraction of hypotheses with assigned MITRE technique
- `tables_frozen`: flag ensuring table immutability in production
- All 33 hypotheses have at least one mapped MITRE technique

---

## 8. Protocols P1 and P2

### 8.1 Protocol P1 (Frozen)

P1 answers: "Does the entropy kernel produce the same results everywhere?"

Properties:
- Deterministic Shannon entropy on any backend
- `entropy_uniform = 0.0` (trivial case verified)
- `entropy_distinct = 1.0` (maximum entropy verified)
- `entropy_shannon_seed42 = 7.782633` (fixed reference value)
- Collision-free pair encoding: `token = (uint64(a) << 32) | uint64(b)`

P1 is frozen and immutable. Any change invalidates compatibility.

### 8.2 Protocol P2 (Draft v2.8 — target freeze: June 15, 2026)

P2 answers: "Is the system mathematically consistent, adversarially robust, and epistemologically honest?"

New modules relative to P1:
- **Markov Order-k**: H_k = -Σ P(w) · Σ P(s|w) · log₂(P(s|w)), no smoothing (pure MLE)
- **Lempel-Ziv LZ76**: compressibility complexity, O(n²) naive / O(n) suffix-tree
- **Permutation Entropy**: PE = -Σ p(π) · log₂(p(π)) / log₂(d!), tie-breaking via stable sort
- **Abstention Policy**: honest zone [0.15, 0.85] with `Decimal.quantize()` HALF_EVEN
- **Chain of Custody**: mandatory discretization block for non-discrete inputs

22 canonical vectors with SHA-256: `f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`

### 8.3 P2 Compliance Levels

| Level | Description | Permitted Claim |
|-------|-------------|----------------|
| Strict | Pure Python, `Decimal.quantize()` HALF_EVEN, sequential | "VIGÍA-compatible P2 (strict)" |
| Reference | NumPy/CuPy permitted, float64 accumulator, parallel OK | "VIGÍA-compatible P2" |
| Accelerated | Any backend, float32 permitted, P2 subset | "VIGÍA-accelerated" — CANNOT claim full P2 |

### 8.4 P2 Guarantees and Non-Guarantees

P2 **guarantees**:
- Deterministic quantized equivalence across backends
- Contextual entropy (Markov memory)
- Complexity semantics (LZ compressibility)
- Ordinal invariance (PE under monotonic transformations)
- Adversarial rejection (denormals, NaN, Inf, overflow)
- Abstention honesty

P2 **does NOT guarantee**:
- Absolute accuracy (reproducibility ≠ truth)
- Behavioral classification (human vs. bot, real vs. synthetic)
- Authorship attribution or intent inference
- Legal admissibility certification
- Upstream discretization correctness

### 8.5 Documented Adversarial Gaps (P2 §14)

Ten gaps identified and documented honestly:

| ID | Name | Description |
|----|------|-------------|
| GAP-01 | entropy_inflation_attack | Low-rate uniform noise pushes metrics toward high-variability zone |
| GAP-02 | symbolic_explosion_attack | Sub-ULP float perturbations inflate Shannon entropy |
| GAP-03 | calibration_drift | Threshold semantics degrade as upstream distributions shift |
| GAP-04 | backend_divergence_under_stress | Parallel reductions under high core count |
| GAP-05 | heterogeneous_hardware | Cross-vendor GPU determinism not empirically validated |
| GAP-06 | false_structure_induction | Pathological inputs with low LZ without real structure |
| GAP-07 | dataset_leakage_in_calibration | Overlap between calibration corpus and deployment data |
| GAP-08 | upstream_discretization_attack | Adversary controls discretization step outside P2 scope |
| GAP-09 | tie_break_exploitation | PE stable-sort adversarially exploitable |
| GAP-10 | lz_period_aliasing | LZ76 asymptotic — imprecise for short sequences |

---

## 9. Security Subsystem

### 9.1 LLMShield — Prompt Injection Firewall

`security.py` implements `LLMShield` with three passes:
1. NFKC-normalized text — catches Unicode homoglyph substitution
2. Leet-decoded text — catches 1337 obfuscation
3. Original text — catches patterns surviving normalization

25+ patterns covering: instruction override, DAN/jailbreak families (contextual — does NOT false-positive on the name "Dan"), system prompt extraction, role confusion, token-stuffing delimiters.

### 9.2 Kassandra Protocol — Semantic Tripwire

The `KassandraProtocol` implements a cryptographic tripwire derived deterministically via HMAC(KASSANDRA_SALT, session_nonce + counter):

```
session_nonce → fixed at the FIRST evidence processed
tripwire → deterministic HMAC per session
legitimate evidence → wrapped in <<<EVIDENCE_DATA_{nonce}>>>
injection → nonce mismatch → KASSANDRA_TRIPWIRE_TRIGGERED
```

### 9.3 HMAC Chain — Log Integrity

Each audit log entry contains:
- `_prev_hmac`: HMAC of the previous entry ("GENESIS" for the first)
- `_hmac`: HMAC-SHA256 of entry content + `_prev_hmac`

Tampering with any line invalidates all subsequent entries. Key resolution:
1. `VIGIA_HMAC_KEY` (env var, hex-encoded, ≥ 32 bytes)
2. `VIGIA_HMAC_KEY_FILE` (path to file with key bytes)
3. Auto-generated ephemeral key (development only — logs WARNING)

### 9.4 Subprocess Sandbox

`sandbox.py` implements:
- Memory limits via `setrlimit(RLIMIT_AS)`
- CPU time limits via `setrlimit(RLIMIT_CPU)`
- Output truncation (10 MB stdout, 256 KB stderr)
- Hard asyncio timeout with process kill
- Privilege drop: `_drop_privs_if_requested()` aborts with `os._exit(126)` if `setuid()` fails — never continues as root

**Critical security note:** Direct `subprocess` was removed from the main bridge in fix P2-11. All calls migrated to `sandboxed_execute()`.

### 9.5 TOCTOU Mitigations

Implemented in `vigia_sift_bridge.py`:
1. Temporary files created with `tempfile.mkstemp()` — unique, unpredictable name
2. Post-write verification: `os.lstat()` (does not follow symlinks) confirms temp file was not converted to symlink between write and rename
3. If symlink detected: immediate `_IntegrityViolation`, operation aborted

### 9.6 MCP Transport Security

`_verify_transport_security()` at startup:
1. Session token (128-bit random) to stderr for operator verification
2. stdin pipe verification (expected for stdio transport)
3. HTTP/SSE detection: without `VIGIA_MCP_AUTH_TOKEN` → CRITICAL alert
4. With `VIGIA_ENFORCE_STDIO=true`: abort on startup if insecure transport

VIGÍA exposes 21+ forensic tools including root-level operations. HTTP without authentication is an unacceptable attack surface.

### 9.7 CLIP Model Integrity

For the visual forensic tool:
- SHA-256 verification of model files before loading
- Strict mode (`VIGIA_STRICT_MODEL_CHECK=true`): refuses models without configured hash
- Prevents supply-chain attacks where a poisoned model classifies forged documents as legitimate

---

## 10. Calibration Engine and Likelihood Ratio

### 10.1 LikelihoodRatio and ENFSI Scale

VIGÍA uses the standard ENFSI forensic probability scale (European Network of Forensic Science Institutes):

| LR | ENFSI Scale | Label |
|----|------------|-------|
| 1–10 | Limited | NOISE |
| 10–100 | Moderate | SUSPICION |
| 100–1000 | Moderate-Strong | SUSPICION_STRONG |
| 1000–10000 | Strong | MALICE |
| >10000 | Very Strong | MALICE_STRONG |

### 10.2 Isotonic Calibration

`lr_calibration.py` implements isotonic calibration with:
- Sklearn logistic regression (`backend: sklearn_logistic`)
- Calibration corpus: 105 cases (corpus hash: `025aacafd60...`)
- Split: 80% train / 20% test, `seed=42`
- Test metrics: `brier_score=0.0813`, `tpr_at_0.5=1.0`, `fpr_at_0.5=1.0`

**Honesty note:** The calibration corpus is currently synthetic (bootstrap v1). P2 thresholds (0.15/0.85) are heuristic pending empirical validation. `calibration_metadata.json` documents this explicitly.

### 10.3 `_round_floats()` — Cross-OS Determinism

Applied before all hashing. Problem: JSON does not distinguish int from float (1 vs 1.0 → different strings). This function recursively converts any float equal to an integer to int, or rounds to 6 decimal places otherwise. This preserves EBS v1 Invariant I2.

---

## 11. MCP Forensic Tools

### 11.1 Chain of Custody Tools (9 tools)

| Tool | Function |
|------|---------|
| `mount_sift_evidence` | Forensic mounting with magic-byte validation, `noexec,nosuid,nodev,ro` flags |
| `generate_forensic_hash` | SHA-256 chain of custody |
| `read_evidence` | Single-pass read with inline hash |
| `list_files` | Filesystem perimeter |
| `search_pattern` | Pure Python search (no direct grep) |
| `list_processes` | Memory persistence detection |
| `audit_network` | Exfiltration channel mapping |
| `calculate_shannon_entropy` | Payload/cipher detection |
| `detect_eco_overinterpretation` | Excessive digital perfection |

### 11.2 Intentionality Analysis Tools

| Tool | Function |
|------|---------|
| `calculate_human_entropy` | Block-local entropy — distinguishes human from generated text |
| `detect_human_jitter` | Temporal jitter analysis — human habits vs. automation |
| `analyze_stylometry` | Multi-vector stylometry |
| `infer_intent` | Main abductive engine — produces full AbductionTrace |
| `audit_grice_maxims` | Detection of Grice's 4 maxim violations |
| `detect_habit_incongruence` | Memory vs. log incoherence (Volatility: LSASS) |
| `cross_artifact_analysis` | CAIE — Cross-Artifact Incongruence Engine |
| `trust_fusion_analysis` | Bayesian fusion: Temporal → Provenance → Effective Trust |
| `investigate_autonomous` | Autonomous loop: plan → execute → evaluate → repeat |

### 11.3 Document Integrity Tools

| Tool | Function |
|------|---------|
| `audit_document_integrity` | PDF/DOCX: fonts, producer, gender/role coherence |
| `analyze_image_layers` | ELA (Error Level Analysis) for paste-in detection |
| `detect_document_geometry` | Margins, alignment, folio consistency |
| `ocr_semantic_validator` | OCR + semantic validation of mandatory fields |
| `vision_intent_audit` | CLIP zero-shot: visual intentionality in images |

### 11.4 CAIE — Cross-Artifact Incongruence Engine

The CAIE (`caie.py`) implements 8 forensic fracture rules:

1. **MEMORY_VS_DISK**: process in memory without executable on disk
2. **LOG_VS_MEMORY**: log records event that memory contradicts
3. **TEMPORAL_PARADOX**: effect before cause
4. **CULTURAL_MARKER_MISMATCH**: linguistic markers inconsistent with declared origin
5. **PERFECTION_ANOMALY**: statistically too-perfect artifact
6. **SILENCE_PATTERN**: absence of expected evidence
7. **DOCUMENT_FORGERY**: multi-layer incoherence in document
8. **MULTI_TENANT_ISOLATION_BREACH**: isolation violation in cloud environments

---

## 12. Claude Code and Ollama Integration

### 12.1 Claude Code (MCP)

Configuration in `~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-sift/vigia_sift_bridge_final.py"]
    }
  }
}
```

Claude Code calls VIGÍA tools via MCP protocol over stdio. Stdio transport inherits OS-level process isolation — only the parent process (Claude Code) can read/write the server's stdin/stdout.

### 12.2 Ollama (LLM Backend for Narrative)

`llm_backend.py` / `llm_backend_v2.py` implement a pluggable backend:
- Anthropic API (`claude-*`) for high-quality reasoning
- Ollama (local) for offline operation in SIFT field deployments
- Automatic fallback with logging

Backend selection via `VIGIA_LLM_BACKEND` env var. The ForensicBundle is already sealed before calling the LLM. The LLM only receives the bundle as context to produce the narrative — it cannot modify the decision.

### 12.3 FastAPI Wrapper (`vigia_api.py`)

REST wrapper for OpenWebUI integration. Exposes:
- `POST /analyze/path`: analyses a declared repository case through a
  descriptor-bound snapshot.
- `POST /analyze/json`: analyses a supplied JSON case.
- OpenAI-compatible `GET /v1/models` and `POST /v1/chat/completions` endpoints.

The wrapper returns the deterministic standalone scorer's forensic verdict and
seals that exact scorer payload. Its composite intent score is not a calibrated
EBS fabrication-risk posterior: the EBS envelope therefore records `ABSTAIN`
with `STANDALONE_SCORER_UNCALIBRATED_EBS_RISK`, while `caie_analysis` preserves
the forensic verdict, score, confidence, and reason. API responses expose both
fields so a valid seal is never presented as proof of a different decision.

Caller-supplied case JSON is bounded to 1 MiB and 1,024 artifacts before any
temporary file is created or scoring begins. Descriptor-bound repository case
snapshots are likewise capped at 1 MiB, including a post-open copy guard. These
are HTTP availability boundaries, not forensic-schema validation and not
limits on local evidence acquisition or binary ingestion.

---

## 13. Daubert Compliance

### 13.1 The Four Daubert Criteria

*Daubert v. Merrell Dow Pharmaceuticals* (1993) established four criteria for scientific evidence admissibility in U.S. federal courts:

1. **Testability**: can the methodology be — and has it been — tested?
2. **Peer review**: has it been subjected to peer review and publication?
3. **Known error rate**: is there a known or potential error rate?
4. **General acceptance**: is it generally accepted in the relevant scientific community?

### 13.2 VIGÍA Implementation

| Criterion | VIGÍA Implementation |
|-----------|---------------------|
| Testability | 22 P2 canonical vectors, stdlib-only verifier, independent `verify_ebs_v1.py` |
| Peer review | 7-AI collective with defined roles, binding audit findings documented |
| Error rate | `calibration_metadata.json`: brier_score, AUC, FPR/TPR documented |
| Acceptance | MITRE ATT&CK v14.1, ENFSI scale, STIX 2.1, ISO 27037 |

### 13.3 EBS v1 Invariants (Non-Negotiable)

- **I1 — Determinism**: same input → same bundle
- **I2 — Chained integrity**: `bundle_hash` covers ALL content
- **I3 — Verifiable policy**: `policy_spec` is independent of runtime
- **I4 — Explicit actions**: no implicit effects exist
- **I5 — Explainable decision**: risk and posterior ALWAYS present

### 13.4 Amicus Curiae Narrative

The `AmicusCuriaeNarrative` generates reports that explicitly distinguish between:
- Confirmed findings (with direct technical evidence)
- Inferred findings (abduction with falsifiability conditions)
- Documented uncertainties (abstention zones)

---

## 14. Case Corpus and Dataset

### 14.1 Current State

The system works with three types of cases:

**Synthetic cases (VIGÍA Internal Corpus):**
- 186 cases in JSON format
- Generated by `convert_synthetic_cases.py` and `convert_md_cases.py`
- Cover all 5 intent clusters and all 33 hypotheses

**Breakage cases (BREAK_001 through BREAK_009):**
- 9 stress cases designed to explore system limits
- Documented in `known_limitations.md`

**Calibration cases:**
- 105 cases, 80/20 split (84 train, 21 test)
- `n_authentic: 16`, `n_fabricated: 89`

### 14.2 Corpus Limitations

The calibration corpus is currently synthetic (bootstrap v1). This affects:
- LR thresholds (pending empirical validation)
- Reliability of `brier_score` and AUC metrics in real production
- Calibration of `spoofability_score` by evidence type

Calibration with real forensic corpus (`fit_calibration.py` + real SIFT dataset) is a critical pending task before June 15.

---

## 15. Implemented Modules — Complete Inventory

The project comprises 151 Python modules classified by function:

**Core Pipeline (14):** `ebs.py`, `ebs_v1.py`, `pipeline.py`, `run_pipeline.py`, `run_vigia_full.py`, `bundle_builder.py`, `verify_ebs_v1.py`, `signal_contract.py`, `signal_mapper.py`, `signal_adapter.py`, `signal_quality_gate.py`, `vigia_integration_bridge.py`, `vigia_case_adapter.py`, `vigia_scorer.py`

**Inference Engines (8):** `likelihood_engine.py`, `likelihood_ratio.py`, `lr_calibration.py`, `graph_stability.py`, `risk_bounded_layer.py`, `risk_bounded_layer_v2.py`, `abductive_reasoner.py`, `abductive_reasoner_v2.py`

**Forensic Analysis (18):** `abductive_intent_engine.py`, `visible_variables.py`, `semiotic_detector.py`, `semiotic_detector_v2.py`, `forensic_technical_detector.py`, `vigia_core_forensic_technical_detector.py`, `vigia_core_semiotic_detector.py`, `pattern_detector.py`, `entropy_locality.py`, `behavioral_fingerprint.py`, `temporal_forensics.py`, `temporal_forensics_redteam.py`, `temporal_drift.py`, `cross_artifact_resonance.py`, `coherence_validator.py`, `causal_closure.py`, `trust_fusion.py`, `trust_levels.py`

**SIFT Tools (12):** `sift_orchestrator.py`, `mft_timeline_analyzer.py`, `registry_timeline_reconstructor.py`, `prefetch_analyzer.py`, `memory_forensics.py`, `shellbag_analyzer.py`, `usb_device_tracker.py`, `browser_forensics.py`, `event_log_correlator.py`, `disk_forensics.py`, `amcache_shimcache.py`, `network_forensics.py`

**Bridge and API (7):** `vigia_sift_bridge.py`, `vigia_sift_bridge_final.py`, `BRIDGE_PATCH_FINAL.py`, `vigia_api.py`, `vigia_server.py`, `vigia_namespace_shim.py`, `cli.py`

**Security (6):** `security.py`, `sandbox.py`, `shadow_mode.py`, `path_guard.py`, `config_sentinel.py`, `normalization_layer.py`

**MITRE ATT&CK (4):** `mitre_mapping.py`, `mitre_clustering.py`, `picerl_mapping.py`, `sans_phase.py`

**Reports (8):** `forensic_reporter.py`, `report_builder.py`, `report_exporter.py`, `report_exporter_v2.py`, `narrative_auditor.py`, `dissent_report.py`, `generate_report.py`, `generate_execution_log.py`

**Calibration (9):** `fit_calibration.py`, `run_calibration.py`, `generate_calibration.py`, `build_calibration_dataset.py`, `calibration_metadata.json`, `lr_calibration.py`, `check_determinism.py`, `compare_runs.py`, `evaluate_detector.py`

**Audit and Governance (10):** `audit_action.py`, `decision_layer.py`, `evidence_aggregator.py`, `evidence_bundle.py`, `explainable_governance.py`, `execution_logger.py`, `chain_of_custody.py`, `hypothesis_lineage.py`, `negation_handler.py`, `adversarial_silence.py`

---

## 16. Known Limitations and Adversarial Gaps

### 16.1 Documented Limitations (`known_limitations.md`)

| ID | Case | VIGÍA Verdict | Expected | Type |
|----|------|--------------|---------|------|
| L-001 | BREAK_006 (advanced LOtL) | SUSPICION | MALICE | Real limitation |
| L-002 | BREAK_004 (staged persistent access) | SUSPICION | MALICE | Real limitation |
| L-003 | BREAK_007 (fog of war + false flag) | SUSPICION | MALICE | Real limitation |
| L-004 | BREAK_009 (deceptive free text) | UNKNOWN | MALICE | Real limitation |
| L-005 | BREAK_002/005 (authorized pentest) | UNKNOWN/SUSPICION | NOISE/UNKNOWN | Debatable |
| L-006 | BREAK_001 (single temporal inconsistency) | MALICE | UNKNOWN | Design decision |

**L-004** is the most critical limitation: LLMShield filters direct injections but does not neutralize deceptive narratives embedded in free-text artifacts. All free-text artifacts must be treated with reduced trust.

**L-006** is a deliberate design decision: in forensics, it is preferable to investigate a case that turned out benign than to ignore one that turned out malicious.

---

## 17. Git Repository Status

**Repository:** `github.com/annatchijova/vigia-intent-analysis` (private)  
**Planned public release:** June 7–10, 2026  
**Status:** Initial push completed, SSH/git workflow established

**Pending:**
- Resolve version chaos (proliferated suffixes: `_v2`, `_v3`, `_P0`, `_UPDATED`, `_GIT`, `_WIRED_P0`)
- Establish clean `main` branch with audited code
- Verify `verify_ebs_v1.py` uses only stdlib (confirmed by AST, maintain)
- Integration tests: 55/55 passing in current state

---

## 18. Pending Work Through June 15

### 18.1 Critical (blocks release)

1. Git synchronization: resolve version chaos before any further development
2. Real corpus calibration: `fit_calibration.py` over real forensic data
3. P2 freeze: freeze 22 canonical vectors before June 15 (deadline coincides with target freeze)
4. Final README: technical, English-only, for SANS audience
5. Release bundle: `generate_release_bundle.py` for public release

### 18.2 High Priority

6. Convert 50 additional cases from MD to JSON using `convert_md_cases.py`
7. RFC documentation updates for P1/P2 protocols
8. Complete integration tests: verify 55/55 post-sync
9. Docker image: `docker-compose.yml` exists, validate full build

### 18.3 Closing Tasks

10. Final audit by collective before public release
11. Verify no sensitive data leaked in public repository
12. LICENSE and SECURITY.md verified and updated

---

## 19. Bibliography and Technical References

**Semiotics and Philosophy:**
- Peirce, C.S. (1868–1914). *Collected Papers*. Harvard University Press.
- Eco, U. (1990). *The Limits of Interpretation*. Indiana University Press.
- Grice, H.P. (1975). "Logic and Conversation." *Syntax and Semantics* 3.
- Carnegie, D. (1936). *How to Win Friends and Influence People*.

**Digital Forensics:**
- Casey, E. (2011). *Digital Evidence and Computer Crime* (3rd ed.).
- Carrier, B. (2005). *File System Forensic Analysis*.
- SANS Institute. *DFIR Curriculum* — FOR 508, FOR 558.

**Forensic Frameworks:**
- MITRE ATT&CK Enterprise v14.1: https://attack.mitre.org
- ENFSI Guideline for Evaluative Reporting in Forensic Science (2015)
- STIX 2.1 Specification (OASIS)
- ISO/IEC 27037:2012 — Digital Evidence Handling
- RFC 3161 — Internet X.509 PKI Timestamping

**Judicial Standards:**
- *Daubert v. Merrell Dow Pharmaceuticals*, 509 U.S. 579 (1993)
- *Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999)

**Mathematics and Statistics:**
- Ledoit, O. & Wolf, M. (2004). "A well-conditioned estimator for large-dimensional covariance matrices."
- Bandt, C. & Pompe (2002). "Permutation entropy." *Physical Review Letters*.
- Lempel, A. & Ziv, J. (1976). "On the complexity of finite sequences." *IEEE Transactions on IT*.
- Meinshausen & Bühlmann (2010). "Stability Selection." *JRSS-B*.

**Implementation:**
- FastMCP: Anthropic MCP Framework
- Volatility 3: The Volatility Foundation
- Plaso / log2timeline: Google

---

*"Deception has a computational cost. VIGÍA charges it."*

*Document generated: May 18, 2026. VIGÍA AI Collective.*
