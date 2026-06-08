## ENGLISH

**Case Execution Controller (`scripts/run_case.py`)**

**1. Module Purpose and Architectural Role**

Within the VIGÍA forensic framework, `scripts/run_case.py` functions as the deterministic orchestration nucleus for single-case investigative pipelines. Its architectural mandate is to instantiate exactly one forensic case, enforce a totally ordered, sequential processing regime over the evidence object space, and emit a complete, tamper-evident execution metadata record. Unlike general-purpose workflow engines that may tolerate out-of-order execution, speculative parallelism, or dynamic task scheduling, this module is intentionally constrained to eliminate algorithmic uncertainty at the control-plane level. It occupies the stratum between the framework's case-management layer and its evidence-processing micro-modules, translating a declarative case manifest into an imperative, reproducible sequence of computational steps. By binding all case-specific state transitions to an integer-indexed evidence sequence, the module guarantees that independent executions commencing from identical initial conditions traverse bitwise-identical execution paths, thereby satisfying the reproducibility prerequisites stipulated under the Daubert standard for scientific evidence, the traceability mandates of GB/T 29360-2012, and the accountability controls of China's Multi-Level Protection Scheme (MLPS 2.0).

**2. Mathematical Foundations**

The formal semantics of the module can be expressed through a deterministic discrete-state finite automaton operating over an ordered evidence domain.

Let a forensic case $\mathcal{C}$ be defined as a strictly ordered 3-tuple:
$$\mathcal{C} = (\mathcal{P}, \mathcal{E}, \mathcal{M}_0)$$
where:
- $\mathcal{P} \in \mathbb{P}$ denotes the parameter configuration drawn from the VIGÍA policy space $\mathbb{P}$, encompassing a globally unique case identifier, examiner credentials, canonical workspace paths, and forensic policy flags.
- $\mathcal{E} = (e_1, e_2, \ldots, e_n)$ is an evidence sequence of length $n \in \mathbb{N}_0$, strictly indexed by the bijective integer map $idx: \{1, \ldots, n\} \to \mathcal{E}$. Each $e_i$ represents an immutable evidence object.
- $\mathcal{M}_0 = \emptyset$ is the initial metadata accumulator.

The controller implements a deterministic transition system $\mathcal{T} = (S, s_0, \delta)$, where:
- $S$ is the finite state space of the case execution environment.
- $s_0 = \text{INIT}(\mathcal{P})$ is the unique initial state derived exclusively from $\mathcal{P}$ via a pure function.
- $\delta: S \times \mathcal{E} \to S$ is the total state-transition function.

For a given case $\mathcal{C}$, the execution trace $\tau$ is the sequence of states:
$$\tau = (s_0, s_1, \ldots, s_n)$$
such that for each $i \in \{1, \ldots, n\}$:
$$s_i = \delta(s_{i-1}, e_i)$$

**Determinism Axiom.** The module enforces:
$$\forall \mathcal{P} \in \mathbb{P}, \forall \mathcal{E}, |\delta^*(s_0, \mathcal{E})| = 1$$
where $\delta^*$ denotes the reflexive-transitive closure of $\delta$. Consequently, the execution trace $\tau$ and the final metadata accumulator $\mathcal{M}_n$ are unique functions of $(\mathcal{P}, \mathcal{E})$.

Integer indexing is not merely an implementation convenience but a foundational requirement. By decoupling the iteration order from filesystem enumeration semantics or memory-address-dependent data structures (e.g., unhashed set iteration), the module eliminates a prevalent source of non-determinism in forensic pipelines. The evidence sequence $\mathcal{E}$ is materialized through a sorted manifest whose primary key is an unsigned integer, ensuring that the mapping $idx$ remains invariant across executions.

**3. Algorithm Description**

The algorithm proceeds through four strictly ordered phases.

*Phase I: Case Initialization.* The controller ingests the case manifest $\mathcal{M}_f$ (a UTF-8 JSON document conforming to the VIGÍA schema v2.1) and materializes the parameter structure $\mathcal{P}$. It computes a canonical workspace directory $W$ and sets the initial state $s_0$. A pre-execution exclusive lock is acquired on $W$ to preclude concurrent modification, thereby preserving sequential consistency. All dependent VIGÍA modules referenced in $\mathcal{P}$ (e.g., `modules/hash_validator.py`, `modules/chain_of_custody.py`) are probed for availability and version compatibility; any discrepancy triggers a fatal error with exit code 2.

*Phase II: Evidence Ingestion and Manifest Sequencing.* The evidence manifest $\mathcal{E}_f$ is parsed into the sequence $\mathcal{E}$. The parser enforces the integer bijection $idx$; any duplicate or missing index triggers a fatal initialization error. The sequence is loaded into memory as an immutable ordered tuple, not a dynamic array subject to pointer-reallocation variance.

*Phase III: Sequential Processing.* For each $i$ from $1$ to $n$ in strict ascending order:
1. The controller dispatches $e_i$ to `scripts/ingest_evidence.py`, which returns a validated in-memory representation $e'_i$.
2. The hash validation submodule (`modules/hash_validator.py`) computes the cryptographic digest $H(e'_i)$, typically SHA-256, and compares it against the manifest's ground truth.
3. A forensic transformation $\alpha_i$ is applied. This may include file carving, entropy analysis, or feature extraction, delegated to specialized worker modules. The controller itself remains agnostic to $\alpha_i$'s internal mechanics but mandates that all workers operate under the same deterministic contract.
4. The output $o_i$ and associated metadata $m_i$ (including sequence number $i$, digest $H(e'_i)$, and monotonic timestamp $t_i$) are appended to $\mathcal{M}_{i-1}$ to form $\mathcal{M}_i$.
5. State update: $s_i \leftarrow \delta(s_{i-1}, m_i)$.

Error handling within this phase is policy-driven. Under the default strict policy, any exception or hash mismatch aborts the trace, preserving the partial metadata log $\mathcal{M}_{i-1}$ for forensic inspection. Under the permissive policy, the error is logged and the controller proceeds to $i+1$.

*Phase IV: Finalization and Audit-Trail Emission.* Upon completion of the loop, the controller computes an aggregate integrity code:
$$H_{\text{agg}} = \mathcal{H}(m_1 \| m_2 \| \cdots \| m_n)$$
where $\|$ denotes unambiguous concatenation and $\mathcal{H}$ is the configured hash function. The aggregate metadata $\mathcal{M}_n$, execution trace digest, and termination status $\xi$ are written to the audit trail via `lib/audit_logger.py`. If `modules/crypto_signer.py` is available, the trail is cryptographically signed to provide non-repudiation. The workspace lock is released, and the process terminates with exit code $\xi \in \{0, 1, 2\}$.

**4. Input/Output Specifications**

*Inputs:*
- **Case Manifest** (`case_manifest.json`): A UTF-8 encoded JSON document containing $\mathcal{P}$. Mandatory fields include `case_id` (UUIDv4 string), `examiner_did` (decentralized identifier), `policy_profile` (string enum), and `workspace_root` (absolute path).
- **Evidence Manifest** (`evidence_manifest.json` or `evidence_manifest.csv`): A structured listing of evidence objects. Each record must contain an `evidence_id` (unsigned 64-bit integer), `source_path` (string), and `ground_truth_hash` (hexadecimal string).
- **Execution Context** (`context.json`, optional): Read-only environmental overrides, including `PYTHONHASHSEED` and `clock_source`.

*Outputs:*
- **Execution Log** (`execution.log`): JSON Lines format, one record per evidence object, containing $m_i$.
- **Metadata Database** (`metadata.db`): SQLite snapshot of $\mathcal{M}_n$, indexed by `evidence_id`.
- **Audit Trail** (`audit_trail.json`): Cryptographically signed (when `modules/crypto_signer.py` is available) attestation of $H_{\text{agg}}$ and $\xi$.
- **Exit Codes**: `0` indicates successful completion of all $n$ steps; `1` indicates a processing failure during Phase III; `2` indicates an initialization or schema validation failure in Phase I.

**5. Deterministic Guarantees and Forensic Rigor**

The module provides deterministic guarantees at multiple layers:

*Bitwise Reproducibility.* Given identical inputs $(\mathcal{P}, \mathcal{E}, \mathcal{M}_f, \mathcal{E}_f)$ and identical versions of all downstream worker modules, two executions on different host systems produce bit-identical output artifacts ($\mathcal{M}_n$, execution log, audit trail). This property is contingent upon:
- Exclusion of non-deterministic language primitives (e.g., unseeded random number generation, unordered set iteration).
- Canonical serialization order of JSON keys and CSV columns.
- Stable sorting of any intermediate aggregations.

*Temporal Determinism.* Internal control flow never depends on wall-clock time. Sequence ordering is governed by the integer index $i$, while metadata timestamps $t_i$ are either monotonic counters or deterministic mocked values in testing environments. Wall-clock timestamps are recorded solely as non-functional annotations.

*Environmental Isolation.* The