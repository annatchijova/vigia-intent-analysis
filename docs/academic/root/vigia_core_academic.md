---
doc_hash: 0642d009
module: vigia/vigia_core.py
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

**Module:** `vigia/vigia_core.py` — Forensic Semiotic Inference Core

**1. Module Purpose**
The `vigia/vigia_core.py` module constitutes the central evidentiary-reasoning engine of the VIGÍA forensic platform. Encapsulated within the `VigiaCore` class, the module orchestrates a deterministic, six-stage semiotic verification cycle grounded in the phenomenology of Charles Sanders Peirce, the sign theory of Umberto Eco, and the cooperative-pragmatic maxims of H. Paul Grice. Its principal function is to ingest normalized digital evidence artifacts, subject them to exhaustive integer-based confidence aggregation, and emit a formal admissibility verdict. Unlike conventional probabilistic inference frameworks that rely upon floating-point stochasticity and Bayesian posteriors, VIGÍA enforces a fully deterministic evaluation pipeline in which every state transition, penalty assignment, and threshold comparison operates exclusively over the integer domain \( \mathbb{Z} \). This architectural commitment to exact arithmetic eliminates representation error, platform-dependent rounding, and non-reproducible entropy, thereby satisfying the falsifiability and known-error-rate prerequisites of the *Daubert* standard for scientific evidence in United States federal procedure. Furthermore, the module’s tamper-evident audit architecture conforms to the evidentiary-integrity requirements of GB/T 29360-2012 (Electronic Data Forensics General Principles), while its role-based access granularity satisfies the controlled-access stipulations of MLPS 2.0 Level 3 (Multi-Level Protection Scheme). Within the broader VIGÍA ecosystem, `vigia_core.py` serves as the adjudicative kernel that mediates between ingestion pipelines, cryptographic integrity services, and reporting interfaces.

**2. Mathematical Foundations**
The module formalizes evidence processing as a deterministic finite-state transducer \( \mathcal{M} = (\mathcal{S}, \mathcal{E}, \delta, s_0, \mathcal{F}) \), where:
- The state space is \( \mathcal{S} = \{ F, S, T, G, D, V \} \), denoting respectively Firstness, Secondness, Thirdness, Geopolitical validation, Devil's Advocate refutation, and Verdict.
- The evidence space \( \mathcal{E} = \{ e_1, e_2, \dots, e_n \} \) comprises normalized digital artifacts supplied by the related `vigia_preprocess` module.
- The initial state is \( s_0 = F \).
- The set of accepting states is \( \mathcal{F} = \{ V \} \).
- The transition function \( \delta: \mathcal{S} \times \mathcal{E} \to \mathcal{S} \) is a total function deterministically computed by the `analyze_case()` method; no stochastic transitions are permitted.

Confidence aggregation is defined as a weighted integer sum with bounded saturation:
\[
C_{\text{final}} = \operatorname{clamp}_{[0,100]}\left( \sum_{i=1}^{k} w_i \cdot c_i \right), \quad w_i, c_i \in \mathbb{Z}.
\]
The clamping operator \( \operatorname{clamp}_{[L,U]}(x) = \min(U, \max(L, x)) \) ensures closure within the admissible integer interval \( [0, 100] \cap \mathbb{Z} \), forming a commutative monoid under saturated addition. The constant `MIN_CONFIDENCE` is formally an integer threshold \( \tau \in \mathbb{Z} \), operationally set to \( \tau = 75 \). The verdict function \( V: \mathbb{Z} \to \{ \text{ADMISSIBLE}, \text{INADMISSIBLE} \} \) is defined by:
\[
V(C_{\text{final}}) = \begin{cases} \text{ADMISSIBLE}, & \text{if } C_{\text{final}} \geq \tau, \\ \text{INADMISSIBLE}, & \text{if } C_{\text{final}} < \tau. \end{cases}
\]
All arithmetic operations—addition, scalar multiplication, and comparison—are performed in two's-complement integer representation, guaranteeing bitwise reproducibility across heterogeneous hardware architectures and compiler optimizations.

**3. Algorithm Description**
The `analyze_case()` function executes the following deterministic sequence, each stage producing exactly one transition record:

1. **Ingestion and Cryptographic Verification.** The input `case_bundle` is validated against SHA-256 cryptographic hashes maintained by `vigia_hash`. Any digest mismatch triggers an immediate abort, returning a `HASH_FAILURE` terminal state. This step ensures that only integrity-verified artifacts enter the semiotic cycle.
2. **Firstness (State \( F \)).** Raw artifact features are extracted as an integer vector \( \mathbf{a} \in \mathbb{Z}^m \). No floating-point normalization is permitted; all scaling is effected through fixed-point integer multiplication by pre-calibrated rational denominators stored as integer pairs \( (p, q) \) with \( q \neq 0 \). This stage corresponds to the pure phenomenological reception of the sign-vehicle.
3. **Secondness (State \( S \)).** Each extracted feature is differentially compared against a calibrated ground-truth baseline vector \( \mathbf{b} \in \mathbb{Z}^m \) residing in the forensic knowledge base. A binary-relation matrix \( \mathbf{R} \in \{0,1\}^{m \times m} \) is populated, where \( R_{ij} = 1 \) if and only if \( |a_i - b_j| \leq \epsilon_{ij} \) for an integer tolerance \( \epsilon_{ij} \in \mathbb{Z}_{\geq 0} \), and \( 0 \) otherwise. A logical rupture is declared if any mandatory feature yields a zero row in \( \mathbf{R} \).
4. **Thirdness (State \( T \)).** Synthetic mediation combines the differential signals into an intermediate confidence score \( C_T \). This stage applies a rule-based integer matrix operation or a weighted sum of violation counts, yielding \( C_T \in [0, 100] \cap \mathbb{Z} \). The operation is referentially transparent: identical inputs always produce identical \( C_T \).
5. **Geopolitical (State \( G \)).** Contextual metadata—including timezone offsets, language locale codes, and jurisdictional tagging—are validated against the `jurisdiction_profile`. Integer rule-matching predicates \( G_j: \mathcal{M} \to \{0, 1\} \) determine compliance with regional evidentiary standards. Each non-compliance event applies an integer penalty \( p_{G,j} \in \mathbb{Z} \) subtracted from the running score.
6. **Devil's Advocate (State \( D \)).** An adversarial stress-test applies Gricean maxim evaluation (Quantity, Quality, Relation, Manner) to the artifact's semantic payload. Each detected maxim violation decrements the score by an integer penalty \( p_k \in \mathbb{Z} \), formalized as:
   \[
   C_D = C_T - \sum_{k=1}^{4} p_k \cdot \mathbb{I}(\text{violation}_k),
   \]
   where \( \mathbb{I} \) is the indicator function returning \( 1 \) if the violation is present and \( 0 \) otherwise.
7. **Verdict (State \( V \)).** The final score is computed as \( C_V = \operatorname{clamp}_{[0,100]}(C_D) \). The function evaluates \( C_V \geq \text{MIN\_CONFIDENCE} \). If true, the verdict is `ADMISSIBLE`; otherwise `INADMISSIBLE`. The terminal state and all intermediate scores are sealed into the output record.
8. **Audit Logging.** Every state transition \( (s_i, s_{i+1}, C_i, h_i) \), together with its integer Unix timestamp and SHA-256 digest \( h_i \), is appended to the tamper-evident log managed by `vigia_chain_of_custody`.

**4. Input / Output Specifications**
- **Inputs:**
  - `case_bundle`: `dict` containing artifact payloads (byte sequences or integer feature vectors), acquisition timestamps expressed as Unix epoch integers, examiner credentials as integer-coded identifiers, and provenance metadata.
  - `jurisdiction_profile`: `dict` encoding regional evidentiary rules as integer-coded flag sets and mandatory field masks.
  - `audit_context`: `object` referencing the active chain-of-custody session identifier and the previous log hash for linked-list integrity.
- **Outputs:**
  - `verdict_record`: `dict` with strictly defined keys:
    - `final_state`: terminal state identifier from \( \mathcal{S} \).
    - `integer_score`: \( C_V \in [0, 100] \cap \mathbb{Z} \).
    - `admissibility`: categorical string, either `ADMISSIBLE` or `INADMISSIBLE`.
    - `transition_log`: ordered list of tuples \( (\text{state}, \text{integer\_score}, \text{hash\_digest}) \) documenting the Peircean cycle traversal.
    - `hash_digest`: SHA-256 fingerprint of the canonicalized `verdict_record`.

**5. Deterministic Guarantees**
- **Bit-exact Reproducibility:** For any two invocations with identical `case_bundle`, `jurisdiction_profile`, and `audit_context`, the module produces identical `integer_score`, `admissibility`, and `hash_digest`. Formally, the inference function \( f: \mathcal{X} \to \mathcal{Y} \) satisfies \( \forall x, y \in \mathcal{X},\, x = y \implies f(x) = f(y) \).
- **Integer Domain Closure:** All confidence values, penalties, weights, and tolerances are elements of \( \mathbb{Z} \). The saturated addition operator ensures closure under the algebraic structure \( (\mathbb{Z}_{[0,100]}, \oplus) \), where \( a \oplus b = \operatorname{clamp}_{[0,100]}(a + b) \).
- **Entropy Exclusion:** No pseudo-random number generators, hardware entropy sources, Monte Carlo sampling, or floating-point operations participate in the inference path. The algorithm is entirely deterministic and traceable.
- **Audit Completeness:**