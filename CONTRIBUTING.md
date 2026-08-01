# CONTRIBUTING TO VIGÍA

**Repository:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Author:** Anna Tchijova  
**Last updated:** June 2026

> Esta guía también está disponible en español: [CONTRIBUYENDO.md](CONTRIBUYENDO.md)

---

## Protocol P2 Compliance — Required Reading for Forks

VIGÍA's mathematical core operates under **Protocol P2**, the deterministic
entropy specification that governs all scoring reproducibility claims. If you
are forking this repository, porting the entropy kernel to another language,
or building a tool that claims VIGÍA compatibility, **you must read P2 before
writing a single line of scoring code.**

The full specification is at `docs/protocols/P2/SPEC.md`. The canonical
vectors are at `canonical_vectors_p2.json`, accompanied by
`canonical_vectors_p2.sha256`. The SHA-256 of the vectors file is normative:
any modification — including whitespace — invalidates the fingerprint and the
compatibility claim.

### What P2 Governs

P2 defines the reproducibility contract for: Shannon entropy, normalized
entropy, entropy rate, Markov order-k conditional entropy, Lempel-Ziv
complexity (LZ76 variant), permutation entropy, pair encoding, abstention
thresholds, and adversarial rejection (NaN, Inf, denormals).

P2 does **not** define: semantic interpretation of evidence, authorship
attribution, intent inference, legal admissibility, or ontological claims
about "authenticity." These are explicitly out of scope and documented as
such in the spec's non-goals section.

### Compliance Levels

| Level | Who it's for | Claim permitted |
|-------|-------------|-----------------|
| **Strict** | Forensic audit, legal proceedings | `VIGÍA-compatible P2 (strict)` |
| **Reference** | Production DFIR, research, cross-platform | `VIGÍA-compatible P2` |
| **Accelerated** | Real-time, embedded, high-volume | `VIGÍA-accelerated` — **cannot claim P2 compatibility** |

Strict compliance requires pure Python, sequential reduction, and
`Decimal.quantize()` HALF_EVEN canonicalization. Reference compliance permits
NumPy/CuPy with float64 accumulators. Accelerated permits float32 but forfeits
the compatibility claim entirely — this is non-negotiable and documented in
the spec's compliance levels section.

### The Revocation Clause

P2 §3 contains a revocation clause that applies to forks and derivative works.
If your documentation, UI labels, CLI output, API field names, or any
user-facing material uses any of the following phrases, **you automatically
forfeit the right to claim P2 compatibility**, regardless of whether your
vectors pass:

- "AI detector" / "bot detector" / "human-vs-machine classifier"
- "authenticity score" / "deception score" / "intent score" / "humanity index"

These are ontological claims that P2's mathematical measurements cannot
support. A high-entropy sequence is not "more human." A low-entropy sequence
is not "more synthetic." If your tool needs to make those claims, it needs
an independently validated decision layer above P2, and it cannot use VIGÍA's
compatibility mark to do it.

### Known Adversarial Gaps

P2 documents 10 known gaps (GAP-01 through GAP-10) — adversarial scenarios
not yet covered by canonical vectors. These include entropy inflation attacks,
symbolic explosion via sub-ULP float perturbations, calibration drift,
and LZ period aliasing on short sequences. Read §14 of the spec before
claiming robustness properties. These gaps are append-only: once assigned,
a GAP-NN identifier is never reused.

### P2 Status

P2 is **frozen**. Thresholds are normative. P1 is frozen and immutable.
P2 depends on P1. Validators must pass P1 first.

### P3 Roadmap

P2 is infrastructure, not a forensic system. The following capabilities are
explicitly deferred to P3: formal discretization standard, score fusion and
weighting, uncertainty propagation, calibration protocol, and Peircean
inference closure. P2 measures. P3 will reason.

---

## A Note From the Author

I want to be direct about something before anything else: **VIGÍA is not
perfect, and I know it.**

This is not a disclaimer written under legal pressure. It is a design
principle. A forensic system that cannot document its own failure modes is
untrustworthy by definition. The same epistemological standard I apply to
evidence, I apply to this codebase.

If you find something wrong — a bug, a logical inconsistency, a case where
the scoring produces a clearly incorrect verdict, a coverage gap, a
theoretical flaw — I genuinely want to know. I will not be defensive about
it. Criticism is not an attack on the project. Criticism *is* the project
working as intended.

Please be direct. The threat model I work against does not reward politeness
over precision.

---

## What VIGÍA Does Not Cover (and Probably Never Will Fully)

The case corpus was designed around a specific threat landscape: enterprise
insider threats, APT-style intrusions, credential abuse, log tampering, and
memory-resident malware patterns documented in public forensic datasets
(NIST, DFRWS, DEF CON DFIR CTF, Digital Corpora).

**This is not all of human life.** Forensic investigation spans domains
this system has not touched:

- IoT and embedded systems evidence
- Cloud-native environments (containers, serverless, managed identity)
- Industrial control systems (ICS/SCADA)
- Social media and open-source intelligence (OSINT) chains
- Physical access control integration
- Non-English language environments at the lexical level
- Low-and-slow APT campaigns spanning multiple years
- Criminal cases involving non-technical perpetrators

The CAIE scoring model was calibrated on the cases that exist in the corpus.
If you bring a case type that is structurally different from those — different
artifact signatures, different attack primitives, different cultural or
organizational context — the weights may not reflect your reality.

**Document your domain.** If you contribute cases from an area not covered,
the most valuable thing you can include is an explanation of *why* existing
weights are wrong for your domain, not just a patch that makes the test pass.

---

## On Cooperation

VIGÍA was built by a human and seven AI models working together, which means
it was built on the premise that no single perspective is sufficient.

That same principle extends to human contributors. I do not believe in the
heroic lone-genius model of open source. I believe that a forensic tool
reviewed by a former law enforcement investigator, a defense attorney, a
red team operator, and a behavioral psychologist will be more reliable than
one reviewed only by people who think like me.

If your background is different from mine — if you come from DFIR, from
academia, from legal practice, from a jurisdiction I have not considered —
your perspective has disproportionate value here, precisely because it is
different.

Contributions are welcome from any background. The minimum requirement is
not expertise: it is intellectual honesty about what you know and what you
do not.

---

## Current Limitations Under Active Development

Before contributing, read [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md).
It documents every known failure mode in detail, including root causes and
forensic implications.

Key items still open for contribution:

- **FW-008:** Full `Fraction` conversion of intermediate scoring values.
  Currently the verdict decision path is deterministic, but some intermediate
  float operations remain. Full rationalization is the target.
- **Domain expansion:** New case categories, especially IoT and cloud-native
  environments. Mobile (Android and iOS) already has coverage via
  `vigia/sift/android_forensics.py`, `vigia/sift/ios_forensics.py`, and
  validated corpus cases; contributions that extend mobile artifact depth are
  welcome but the domain is not a gap.
- **Language coverage:** The NLP layer operates primarily on English-language
  artifacts. Extending pattern coverage to other languages requires domain
  expertise in both the language and its forensic artifact signatures.

---

## Future Projects

VIGÍA is one project in a larger research trajectory. If any of the following
interests you, explore the full repository list at:

**`https://github.com/annatchijova`**

### RAVEN-MEMORY

RAVEN-MEMORY is an adaptive memory architecture for agentic AI systems,
currently under development as a standalone project. The design target is
persistent, structured episodic memory for agents operating across long
sessions — the kind of memory that allows a forensic agent to maintain
case context across interrupted investigations.

The planned integration path is VIGÍA → RAVEN-MEMORY as the memory backend
for the agentic pipeline. Currently VIGÍA's agent (`vigia_agent.py`) operates
statelessly across cases. RAVEN-MEMORY would allow the system to track
hypothesis lineage, accumulate contextual evidence across sessions, and
maintain an auditable investigation log that is itself a forensic artifact.

This integration is not promised on any timeline. It depends on RAVEN-MEMORY
reaching production stability. But it is the direction I am building toward,
and contributions to the memory interface design in VIGÍA are welcome with
that future in mind.

### Other Active Projects

- **MUTANTE:** Adversarial LLM red-teaming via evolutionary prompt mutation.
  Relevant to VIGÍA's adversarial robustness testing pipeline.
- **STYLOMETRY-CI:** Forensic identity gate for GitLab CI/CD pipelines.
  Orthogonal to VIGÍA but shares the behavioral fingerprinting theoretical
  foundation.
- **WormGame:** C. elegans connectome-based optimization algorithm. Bimodal
  solver distribution maps to documented behavioral states. Designated for
  a future ML/bio-inspired computing context — not integrated with VIGÍA.

---

## How to Contribute

### Reporting Issues

Open a GitHub issue. Include:

- VIGÍA version or commit hash
- The specific input (case JSON, evidence path, or command) that triggers
  the issue
- Observed output vs. expected output
- Whether this is a correctness issue (wrong verdict), a determinism issue
  (inconsistent output on identical input), or a usability issue

For security vulnerabilities, read [`SECURITY.md`](./SECURITY.md) first.

### Submitting Case Contributions

New cases must follow the canonical case schema. See
[`data/cases/`](./data/cases/) for examples and the schema definition in
[`fsv_schema.json`](./fsv_schema.json).

Each submitted case must include:

- A `ground_truth` field with the expected verdict
- A `rationale` field explaining *why* that verdict is correct
- A `domain` field identifying the forensic domain
- A `source` field documenting where the evidence pattern originates
  (public dataset, synthetic construction, sanitized real case, etc.)
- If synthetic: an explicit statement that it is synthetic

Cases that return ABSTAIN are not failures. Do not submit cases designed to
"break" the system and then classify those as accuracy deficits. Read the
accuracy framing in [`README.md`](./README.md#accuracy--evidence-dataset)
before opening issues about verdict counts.

### Code Contributions

1. Fork the repository
2. Create a branch with a descriptive name
3. Run the full test suite before submitting: `pytest tests/ -v`
4. Zero regressions are acceptable. If your patch introduces a regression,
   explain why in the PR description and what the tradeoff is
5. All new code touching the scoring pipeline must include a determinism
   test — identical input must produce identical output across platforms
6. If your contribution modifies verdict logic, include a corresponding
   update to `KNOWN_LIMITATIONS.md` if it resolves a documented limitation,
   or a new entry if it introduces one
7. Tests must **discriminate**, not merely execute. A test that runs a
   threshold check without pinning its exact cut-off point verifies nothing:
   `base_score = 0.9` passes whether the threshold is `0.5` or `0.8`. Pin the
   boundary itself. Mutation testing measures this and runs weekly — see
   `docs/MUTATION_RUNBOOK.md`. If you add a module to `[tool.mutmut]`
   `only_mutate`, add it to the CI matrix in
   `.github/workflows/mutation.yml` too; a contract test enforces the pair.
8. Repository-sweep tests (those that `grep -r .` or `rglob` the tree) must
   exclude `mutants/`. It is the mutation-testing sandbox: a full copy of the
   source with deliberate defects injected. A sweep that counts it is
   reporting on a build directory, not on the repository.

### Registry status — how to read it without getting it wrong

`BUGS_HISTORICO.md` and `BUGS_PENDIENTES.md` express an entry's status in four
coexisting conventions (a `| **Estado** |` row, a plain `| Estado |` row, a
`[TAG]` at the end of the heading, and split statuses like
`(a) RESUELTO ... (b) ABIERTO`). Three independent audits of this registry —
two by external models, one in-house — produced **false numbers** because each
wrote its own regex and caught only one convention. Reported open bugs that
were closed; reported "41% of fixes had side effects" when the real figure is
3% (the parser had counted every cross-reference to another `B-NNN` as a side
effect, and 71% of entries carry one).

Do not write another regex. Import the shared parser:

```python
from tests.test_registry_status_contract import parse_status, _entries

for bug_id, fname, heading, body in _entries():
    state, text = parse_status(heading, body)   # CLOSED | OPEN | PARTIAL
```

`PARTIAL` is not decoration: it marks entries where one sub-item closed and
another stayed open. Collapsing it into `CLOSED` is exactly how an open
remainder disappears from view.

`tests/test_registry_status_contract.py` enforces that every entry stays
machine-readable. A new status token fails the test on purpose — classifying
it is a decision, not a formatting detail.

### Documentation Contributions

The codebase contains comments in Spanish. Translations to English are
welcome and needed, particularly in `caie.py`, `vigia_scorer.py`, and the
scoring modules. Maintain technical precision — do not simplify terminology
to make translation easier.

---

## What I Will Not Merge

- Anything that introduces floating-point operations into the verdict
  decision path without a documented justification and a determinism proof
- Anything that allows the LLM backend to influence scoring or verdicts
- Evidence fabrication utilities — tools designed to generate plausible
  fake forensic artifacts for evasion testing are out of scope for this
  repository
- Patches that "fix" ABSTAIN verdicts on epistemically ambiguous cases
  by forcing a MALICE or SUSPICION verdict

---

## License

All contributions are accepted under the project's Apache 2.0 license.
By submitting a pull request, you confirm that you have the right to
license your contribution under these terms.

---

*"A system that cannot be criticized cannot be trusted."*

*— Anna Tchijova, VIGÍA Project*
