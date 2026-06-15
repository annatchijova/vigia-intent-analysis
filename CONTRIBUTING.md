# CONTRIBUTING TO VIGÍA

**Repository:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Author:** Anna Tchijova  
**Last updated:** June 2026

> Este documento también está disponible en español: [CONTRIBUYENDO.md](./CONTRIBUYENDO.md)

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

- Mobile device forensics (iOS/Android artifacts)
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
- **L-019:** False flag rule logic in `caie.py`. The current implementation
  may not correctly handle all genuine false flag cases. Any contribution
  here requires careful reading of the false flag semantics documented in
  `KNOWN_LIMITATIONS.md` — the failure mode is subtle.
- **Domain expansion:** New case categories, especially IoT, cloud-native,
  and mobile forensics environments.
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
