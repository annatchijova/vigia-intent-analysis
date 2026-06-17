# QUE_SIGUE.md — Theoretical Deepening Track (Post-Hackathon)

> **Status: NOT part of the SANS FIND EVIL Hackathon 2026 submission.**
> The hackathon is closed. Nothing in this document is evaluated by judges,
> required for compliance, or tied to the submitted accuracy claims. This is
> a pure-interest research track on the philosophical/logical foundations of
> abduction, pursued because VIGÍA's design deserves a deeper theoretical
> floor than "inspired by Peirce and Eco." Any commits produced from this
> track must be tagged `POST HACKATHON` in the commit message.

## 0. Why this track exists

VIGÍA's abductive engine currently rests on two pillars:

- **Peirce**: the formal shape of abduction (the surprising fact C, the rule
  that would explain it, the adoption of that rule as hypothesis worth
  testing) and the original IoC→IoI inversion.
- **Eco**: the semiotic reading of clues as a chain of interpretants, and the
  "detective" model of evidence interpretation.

Neither author gives VIGÍA a *computational* or *logically formal* account of
abduction. Three authors close that gap, each addressing a different layer
of the stack:

| Author   | Layer addressed                                  | VIGÍA component it speaks to              |
|----------|---------------------------------------------------|--------------------------------------------|
| Magnani  | Abduction as physical/embodied action, not just inference | Forensic technical detectors (disk, registry, memory) |
| Aliseda  | Logical formalization: generation vs. selection of hypotheses | The missing `resolve(ccs, risk, epsilon)` function |
| Nishida  | Early computational implementation: multi-hypothesis tracking, contradiction detection, plausibility update | The Fraction-based scoring pipeline, likelihood_ratio.py, trust_fusion.py |

This document is the plan for studying each one and deciding, deliberately,
whether and how their ideas get absorbed into VIGÍA's architecture.

## 1. Magnani — Manipulative Abduction

**Core idea to study**: Magnani's distinction between *theoretical* abduction
(sentential or model-based, purely symbolic) and *manipulative* abduction,
where acting on external representations and physical/epistemic mediators is
itself part of generating a hypothesis — not just a step before or after
reasoning about it.

**Why it matters for VIGÍA**: every forensic technical detector
(`shellbag_analyzer.py`, `prefetch_analyzer.py`, `amcache_shimcache.py`,
`mft_timeline_analyzer.py`) does not merely *read* artifacts — it manipulates
disk structures, parses binary formats, and reconstructs timelines through
that manipulation. Magnani's framework gives a theoretical name to what these
modules are actually doing: manipulative abduction over digital artifacts,
not pure symbolic inference over a log file. This could reframe how
`KNOWN_LIMITATIONS.md` and the architecture docs describe the technical
detector layer versus the semiotic/narrative layer.

**Reading plan**:
- Magnani, *Abductive Cognition: The Epistemological and Eco-Cognitive
  Dimensions of Hypothetical Reasoning* (2009) — chapter 1, on external
  representations and epistemic mediators.
- Magnani, "Model-Based and Manipulative Abduction in Science" (2004).

**Concrete next action**: write a short internal note (`notes/magnani_manipulative.md`,
not part of the submission tree) mapping each technical detector module to
either theoretical or manipulative abduction, and flag whether any detector
is mislabeled in current docs as "pure inference" when it is actually
manipulative.

## 2. Aliseda — Logical Formalization of Abduction

**Core idea to study**: Aliseda's *Abductive Reasoning: Logical
Investigations into Discovery and Explanation* (2006) formalizes abduction
using semantic tableaux and AGM belief revision, and — critically — draws a
sharp line between abduction as **generation** of new hypotheses and
abduction as **selection** among hypotheses already on the table.

**Why it matters for VIGÍA**: this is the most direct theoretical fit for the
single most important open item in the technical debt list — the absent
`resolve(ccs, risk, epsilon) → final_verdict` function. Right now VIGÍA
generates candidate hypotheses (via `abductive_reasoner.py`,
`abductive_intent_engine.py`) but the step that *selects* MALICE over
SUSPICION over ABSTAIN given a CCS/risk/epsilon triple is not formalized as
a discrete, citable selection function. Aliseda's selection-vs-generation
distinction gives a vocabulary and a logical structure (tableaux-based
consistency checking) to formalize that missing function in a way that is
defensible under cross-examination, not just "the code happens to do this."

**Reading plan**:
- Aliseda (2006), chapters on semantic tableaux and the generation/selection
  distinction.
- Aliseda (2000), "Abduction as Epistemic Change: A Peircean Model in
  Artificial Intelligence" — directly bridges Peirce to AI implementation,
  which is VIGÍA's exact lineage claim.

**Concrete next action**: draft a formal specification of `resolve()` as a
selection function over the hypothesis set, citing Aliseda's
generation/selection split explicitly in the docstring and in
`DAUBERT_JUDICIAL.md` (as a future revision, post-hackathon, not touching the
submitted version).

## 3. Nishida — Computational Precedent

**Core idea to study**: Nishida's early work (Kyoto University, with Doshita)
on an "integrated parsing engine" for natural language understanding — a
uniform abductive inference mechanism able to generate plausible assumptions,
reason over multiple alternatives simultaneously, switch search toward the
most plausible alternative, detect contradictions that invalidate
conclusions resting on inconsistent assumptions, and update the plausibility
of each belief as new evidence arrives.

**Why it matters for VIGÍA**: this is close to a functional description of
what VIGÍA's Fraction-based scoring pipeline already does — and it predates
VIGÍA by decades, which means VIGÍA can be positioned as a forensic
specialization of a known computational-abduction lineage rather than a
novel, unverified approach. The plausibility-update mechanism is directly
relevant to `likelihood_ratio.py` and `trust_fusion.py`.

**Reading plan**:
- Nishida & Doshita, work on abductive inference for NLU and the integrated
  parsing engine (locate primary sources, originally Japanese-language AI
  literature with some English translations/citations — verify access before
  committing to deep reading).

**Concrete next action**: confirm primary-source availability (some of
Nishida's foundational work may only exist in Japanese-language venues or
hard-to-access proceedings). If primary sources are not accessible, rely on
secondary citations and be explicit about that limitation in any note that
references him — same evidentiary discipline VIGÍA applies to forensic
claims applies here.

## 4. Sequencing

This is exploratory and unscheduled by design — no hackathon deadline
pressure applies. Suggested order, lightest-to-heaviest:

1. Aliseda first — most directly actionable (resolve() formalization).
2. Magnani second — reframes existing detector documentation, no new code.
3. Nishida third — depends on source accessibility, may take longer.

## 5. Explicit non-goals

- This track does **not** modify any file inside the submitted hackathon
  scope without separate, explicit confirmation.
- This track does **not** change any accuracy claim, test count, or BREAK
  case framing already locked in `SUBMISSION_COMPLIANCE.md`.
- Any code change arising from this track ships as its own commit batch,
  clearly tagged `POST HACKATHON`, never silently folded into prior commits.

## 6. References (working list, not yet verified against full-text access)

- Magnani, L. (2009). *Abductive Cognition: The Epistemological and
  Eco-Cognitive Dimensions of Hypothetical Reasoning*.
- Magnani, L. (2004). "Model-Based and Manipulative Abduction in Science."
- Aliseda, A. (2006). *Abductive Reasoning: Logical Investigations into
  Discovery and Explanation*. Springer.
- Aliseda, A. (2000). "Abduction as Epistemic Change: A Peircean Model in
  Artificial Intelligence." In Flach & Kakas (eds.), *Abductive and Inductive
  Reasoning*.
- Nishida, T. & Doshita, S. — early work on abductive inference mechanisms
  for natural language understanding, Kyoto University.
