# VIGÍA — Known Limitations

## Version: EBS v1 | Updated: 2026-05-24

These limitations are documented deliberately as part of the Daubert
standard of falsifiability. VIGÍA does not claim to be infallible —
it claims to be auditable.

---

## L-001 — Perfect Attack Without Anomalies (BREAK_006)

**Description:** When an attacker executes an operation without technical
errors (valid credentials, consistent timestamps, no detectable tooling),
VIGÍA tends to emit SUSPICION rather than MALICE.

**Root cause:** The scoring engine depends on structural anomalies and
CAIE fractures. Without inconsistencies, the score does not cross the
MALICE threshold.

**Forensic implication:** VIGÍA is more effective detecting attacks with
operational errors than high-tier APTs with perfect OPSEC.

**Workaround:** Combine with baseline behavioral analysis
(baselines_institucionales.yaml) to detect statistical deviations.

---

## L-002 — Critical Signal Drowned in Noise (BREAK_004)

**Description:** When there are many irrelevant artifacts and few critical
ones, the average score drops and VIGÍA emits SUSPICION rather than MALICE.

**Root cause:** The evidence aggregator does not yet implement dynamic
weighting by artifact type. All artifacts carry similar initial weight
before trust adjustment.

**Forensic implication:** In high-noise cases, it is recommended to
pre-filter artifacts by relevance before ingesting into the pipeline.

---

## L-003 — Log Absence as Evidence (BREAK_007)

**Description:** The absence of records where they should exist (e.g., an
SSH session present in netflow but with no entry in auth.log) does not
generate enough signal to reach MALICE.

**Root cause:** The current model treats absent evidence as neutral noise,
not as a positive signal of tampering.

**Forensic implication:** Detection of "significant silence" requires
comparison against institutional baselines. Without a configured baseline,
VIGÍA cannot evaluate absences.

---

## L-004 — Prompt Poison / Misleading Narrative (BREAK_009)

**Description:** When a text artifact contains assertions such as "case
already confirmed benign by the team," VIGÍA does not distinguish between
unverified narrative text and structured technical evidence.

**Root cause:** LLMShield filters direct injections into the reasoning
engine but does not neutralize misleading narratives embedded in free-text
artifacts.

**Forensic implication:** All free-text artifacts must be manually treated
with reduced trust. Do not rely on unverifiable assertions embedded within
evidence.

**Reference:** Austin (1962) — false performative speech acts. A text that
says "this is benign" does not make the evidence benign.

---

## L-005 — Verdict Threshold vs. Ambiguous Evidence (BREAK_002, BREAK_005)

**Description:** Cases involving suspicious but authorized activity
(documented pentest) or simultaneous unrelated events produce SUSPICION
or UNKNOWN rather than more precise verdicts.

**Root cause:** VIGÍA has no access to external organizational context
(tickets, authorizations, policies) during automated analysis.

**Forensic implication:** For cases with authorization context, the analyst
must manually review the SUSPICION/UNKNOWN verdict and incorporate that
context into the final report.

---

## L-006 — Single Temporal Inconsistency (BREAK_001)

**Description:** A single artifact with an inconsistent timezone among
three aligned artifacts produces MALICE, when greater uncertainty might
be expected.

**Root cause:** The EFFECT_BEFORE_CAUSE hard gate and the temporal
inconsistency penalty are aggressive by design — they prioritize false
positives over false negatives in a forensic context.

**Design decision:** In forensics, it is preferable to investigate a case
that turned out to be benign than to ignore one that turned out to be
malicious. This behavior is intentional.

---

## L-007 — Kernel-Level or Root Compromise (Trusted Execution Environment Failure)

**Description:** If an attacker has achieved kernel-level access or root
privileges on the host being analyzed — or on the host running VIGÍA itself —
the integrity of all evidence VIGÍA processes must be considered suspect.
VIGÍA operates entirely in userspace and has no mechanism to detect or
compensate for a compromised kernel, hypervisor, or firmware layer.

**Concrete attack vectors:**

- **Rootkit / LKM injection:** A kernel module can intercept syscalls and
  return falsified data to any userspace process, including VIGÍA's artifact
  collectors. File hashes, timestamps, process lists, and network state can
  all be spoofed transparently.
- **Direct kernel memory manipulation:** An attacker with root access can
  alter in-memory data structures (e.g., process table, file descriptor
  table) without leaving traces in userspace-visible logs.
- **eBPF weaponization:** Malicious eBPF programs loaded by a root-level
  attacker can intercept and modify data at the kernel-userspace boundary
  before VIGÍA reads it.
- **Hypervisor or firmware compromise:** At levels below the OS kernel,
  all host evidence is untrustworthy regardless of VIGÍA's controls.
- **VIGÍA host compromise:** If the machine running VIGÍA (not the machine
  being analyzed) is under adversarial control, the entire analysis
  pipeline — including chain-of-custody sealing, HMAC generation, and
  audit logs — is compromised. A sealed `ForensicBundle` produced under
  these conditions is cryptographically valid but evidentially worthless.

**Forensic implication:** VIGÍA's Daubert guarantees — determinism,
reproducibility, chain-of-custody integrity — apply strictly to the
software layer. They do not extend downward to the OS kernel, hypervisor,
or hardware. Any analysis conducted on a live system where root compromise
cannot be excluded should be treated as **preliminary** and confirmed
against a forensic image acquired from a known-clean environment.

**Detection boundary:** VIGÍA may detect *artifacts consistent with* a
rootkit (e.g., USN Journal gaps, MFT anomalies, process/network
incongruences via CAIE) but cannot confirm kernel integrity from
userspace. A clean VIGÍA verdict on a live compromised host is not
exculpatory.

**Recommended mitigations (outside VIGÍA's scope):**

1. Acquire a forensic image with a hardware write blocker before running
   any analysis. Run VIGÍA against the image, not the live system.
2. Verify the integrity of the acquisition host (VIGÍA host) before
   sealing any `ForensicBundle`.
3. For high-stakes cases, supplement with out-of-band kernel integrity
   checks (e.g., Secure Boot attestation, TPM PCR validation, or a
   trusted hypervisor snapshot) prior to analysis.
4. Document explicitly in the forensic report whether analysis was
   performed on a live system or a verified forensic image.

**Design decision:** This limitation is intentional and permanent.
Extending VIGÍA into kernel space would require a privileged agent
(kernel module or eBPF probe) that itself becomes an attack surface —
contrary to VIGÍA's threat model. The correct defense is procedural:
acquire clean images, analyze offline.

**References:** NIST SP 800-86 §4.1 (live vs. dead analysis trade-offs);
RFC 3227 §2.3 (order of volatility); MITRE ATT&CK T1014 (Rootkit),
T1601 (Modify System Image).

---

## Summary

| ID    | Case                        | VIGÍA verdict        | Expected         | Type                    |
|-------|-----------------------------|----------------------|------------------|-------------------------|
| L-001 | BREAK_006                   | SUSPICION            | MALICE           | Real limitation         |
| L-002 | BREAK_004                   | SUSPICION            | MALICE           | Real limitation         |
| L-003 | BREAK_007                   | SUSPICION            | MALICE           | Real limitation         |
| L-004 | BREAK_009                   | UNKNOWN              | MALICE           | Real limitation         |
| L-005 | BREAK_002/005               | UNKNOWN/SUSPICION    | NOISE/UNKNOWN    | Debatable               |
| L-006 | BREAK_001                   | MALICE               | UNKNOWN          | Design decision         |
| L-007 | Kernel/root compromise      | N/A (blind)          | —                | Permanent design boundary |
