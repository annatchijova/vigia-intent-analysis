A continuación tienes un **diagrama formal del pipeline VIGÍA**, con flujo de datos, separación de capas y puntos explícitos de decisión. Está estructurado para ser defendible (Daubert), auditable y modular.

---

# 🧭 VIGÍA — Pipeline Forense Completo

```text
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Raw Artifacts                                              │
│  ─────────────                                              │
│  • Disk (files, timestamps, hashes)                         │
│  • Memory (processes, LSASS, injections)                    │
│  • Network (DNS, IP, flows)                                 │
│  • Logs (system, cloud, audit)                              │
│  • Hardware (TPM, keys)                                     │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                 NORMALIZATION LAYER (P0)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Artifact Structuring                                       │
│  ─────────────────────                                       │
│  • evidence_type assignment                                 │
│  • metadata extraction (timestamp, source, etc.)            │
│  • spoofability profiling                                   │
│                                                             │
│  Output:                                                    │
│  → Structured Artifacts                                     │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              TEMPORAL VALIDATION LAYER (P1)                 │
│        (PHYSICAL CONSTRAINT ENFORCEMENT - TCV)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TemporalCausalityValidator                                 │
│                                                             │
│  Detects:                                                   │
│  • EFFECT_BEFORE_CAUSE   ← HARD VIOLATION                   │
│  • TOO_FAST              ← PHYSICAL LIMIT BREACH            │
│  • CLOCK_SKEW            ← ENVIRONMENTAL ISSUE             │
│  • STATISTICAL_UNIFORMITY ← AUTOMATION SIGNAL              │
│                                                             │
│  Output:                                                    │
│  → Temporal Violations                                      │
│  → Timeline Summary                                         │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              PROVENANCE LAYER (P2)                          │
│        (CHAIN OF CUSTODY - EPC)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ProvenanceChain                                            │
│                                                             │
│  Validates:                                                 │
│  • Lineage continuity                                       │
│  • Hash integrity                                           │
│  • Parent-child relationships                               │
│  • Temporal consistency                                     │
│                                                             │
│  Output:                                                    │
│  → Trust Score (0.0–1.0)                                    │
│  → Chain Status (PRISTINE / BROKEN / etc.)                  │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│               TRUST FUSION LAYER                            │
│        (SEMANTIC TRUST SYNTHESIS)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TrustFusionEngine                                          │
│                                                             │
│  Inputs:                                                    │
│  • Provenance Trust                                         │
│  • Temporal Violations                                      │
│                                                             │
│  Formula:                                                   │
│  effective_trust = base * exp(-2 * penalty)                 │
│                                                             │
│  Output:                                                    │
│  → Effective Trust per Artifact                             │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│        CROSS-ARTIFACT ANALYSIS LAYER (CAIE)                 │
│        (LOGICAL INCONSISTENCY DETECTION)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CrossArtifactIncongruenceEngine                            │
│                                                             │
│  Detects Fractures:                                         │
│  • LOG vs MEMORY mismatch                                   │
│  • FALSE_FLAG patterns                                      │
│  • NETWORK vs HOST inconsistencies                          │
│  • CRYPTOGRAPHIC anomalies                                  │
│                                                             │
│  Scoring:                                                   │
│  raw_score                                                  │
│    ↓                                                        │
│  spoofability adjustment                                    │
│    ↓                                                        │
│  trust weighting (from TrustFusion)                         │
│                                                             │
│  Output:                                                    │
│  → Fractures                                                │
│  → Weighted Evidence Scores                                 │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│          CORRELATION DECAY LAYER (P2 FINAL)                 │
│      (EVIDENCE DEPENDENCY NORMALIZATION)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CorrelationDecayEngine                                     │
│                                                             │
│  Handles:                                                   │
│  • Same-source redundancy                                   │
│  • Type correlation                                         │
│  • Temporal clustering                                      │
│                                                             │
│  Key Mechanism:                                             │
│  • Trust-weighted correlation                               │
│    corr * sqrt(T_A * T_B)                                   │
│                                                             │
│  Output:                                                    │
│  → Adjusted Scores                                          │
│  → Composite Score                                          │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                DECISION LAYER                               │
│           (FINAL FORENSIC VERDICT)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Inputs:                                                    │
│  • Composite Score                                          │
│  • Fractures                                                │
│  • Trust Levels                                             │
│                                                             │
│  Decision Thresholds:                                       │
│                                                             │
│  IF critical temporal violation → MALICE                    │
│  ELSE IF score > 0.8 → MALICE                              │
│  ELSE IF score > 0.5 → SUSPICION                           │
│  ELSE → NOISE                                               │
│                                                             │
│  Output:                                                    │
│  → Verdict                                                  │
│  → Confidence                                               │
│  → Explanation (Peirce Chain)                               │
│                                                             │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                ORCHESTRATION LAYER                          │
│                (PEIRCE PLANNER)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Controls execution flow:                                   │
│                                                             │
│  Rule-based triggers:                                       │
│  • If timestamps → run TCV                                  │
│  • If verdict critical → run Provenance                     │
│  • If enough artifacts → run CAIE                           │
│                                                             │
│  Ensures:                                                   │
│  • Step sequencing                                          │
│  • No redundant analysis                                    │
│  • Explainable reasoning path                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

