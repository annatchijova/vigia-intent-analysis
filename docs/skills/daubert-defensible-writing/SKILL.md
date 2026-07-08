---
name: daubert-defensible-writing
description: Writing reports, documentation, findings, and explanations that survive cross-examination — separating fact from inference, admitting uncertainty without weakening the conclusion, never overclaiming. Use this skill whenever the user is writing or reviewing a report, audit deliverable, postmortem, technical doc, executive summary, research writeup, forensic or expert-style analysis, README claims, or any prose that asserts findings; whenever they ask to "write up the results", "document this", "make it convincing", or "make it sound solid" — especially then, because persuasion pressure is where overclaiming enters; and whenever a draft needs review for inflated certainty, unsupported claims, or buried limitations. Trigger even for a single paragraph if it states conclusions someone might challenge. Fifth member of the family (abductive-engineering, secure-by-construction, software-archaeology, red-team-auditing) — this one governs how their outputs get written down.
---

# Daubert-Defensible Writing

A methodology for *writing claims down* — the last mile where honest work gets ruined. The rest of the family produces disciplined epistemics; this skill ensures the prose does not launder them back into confident mush. Its namesake is the *Daubert* standard for expert testimony: a conclusion is admissible only if its method is testable, its error rate is known, and its reasoning can be examined by a hostile party. That is not a legal curiosity — it is the correct standard for any technical document, because every serious document eventually meets its hostile party: the reviewer, the auditor, the incident retro, the competitor's engineer, the judge.

It exists because a language model writing prose has three strong and dangerous default habits:

1. **It writes for the persuaded reader.** Fluent, confident, adjective-rich prose is what the training data rewarded. The skeptical reader — the one who asks "how do you know that?" after every sentence — is absent from the prompt, so the prose collapses at first contact.
2. **It converts inference into fact by phrasing.** "The service crashed because the pool was exhausted" states, in one grammatical breath, an observation (crashed), an inference (pool exhaustion), and a causal claim (because) — three different epistemic levels wearing one costume.
3. **It hedges everything or nothing.** Either bulletproof-sounding absolutes, or a fog of "might possibly perhaps" that protects the author while informing no one. Both are failures of the same kind: confidence language decoupled from evidence.

The three prime directives that answer them:

> **The adversarial reader is the default reader.** Write every sentence to survive the question "¿y usted cómo lo sabe?"
> **Fact, inference, and opinion never share a sentence unlabeled.** The epistemic level is part of the claim, not a footnote to it.
> **Bounded beats absolute.** The precisely scoped claim is the strong claim; the absolute claim is a gift to the cross-examiner.

---

## Part 1 — The Three Layers, Always Separated

Every assertive sentence in a technical document is one of three things. The central discipline of this skill is refusing to let them blend:

| Layer | What it is | What earns it | Signature phrasing |
|---|---|---|---|
| **Observation** | What was directly seen, measured, logged. Peirce's index — causally connected to its object. | You looked. It is reproducible by pointing. | "The log shows…", "In 47 of 50 runs…", "Line 212 calls…" |
| **Inference** | A conclusion derived from observations by a stated method. An abduction or deduction — only as strong as its method and its rivals. | You reasoned, and you can show the chain and the alternatives you excluded. | "Consistent with…", "The best explanation among {A,B,C} is…", "This implies, assuming X…" |
| **Opinion / judgment** | An assessment involving values, priorities, or expertise beyond the evidence shown. Legitimate — when labeled. | Your expertise, declared as such. | "In my assessment…", "I would prioritize…", "I consider this acceptable because…" |

The most common defect in technical writing is **layer smuggling**: an inference dressed in observation grammar. "The attacker exploited the race condition" (observation costume) when the evidence supports "the timing pattern is consistent with exploitation of the race condition; direct evidence of an attacker was not found" (honest inference with its bound). Under cross-examination, the first version dies and takes the author's credibility with it; the second is unattackable *because it claims exactly what the evidence carries*.

**The mechanical test:** for each sentence, ask which layer it is. If the answer is "two of them", split the sentence. Causal words — *because, caused, due to, led to* — are inference words; they may never appear without their method being nearby ("confirmed by reverting commit K", "the only rival surviving the A–D–I loop in §3").

---

## Part 2 — The Cross-Examination Test

Before a document ships, subject every conclusion to the five questions a competent hostile examiner will ask. If the text does not already contain the answer, the examiner will supply one for you, and it will not be flattering:

1. **"How do you know?"** — Every claim traces to its evidence: the log, the experiment, the citation, the reproducible script. A claim whose provenance is "it is known" or "obviously" is an orphan; adopt it (find the evidence) or delete it. This is chain of custody for assertions.
2. **"Always? Every? Never?"** — Universal quantifiers are cross-examination bait. One counterexample destroys "never fails"; nothing destroys "0 failures in 10⁶ randomized trials; untested beyond that". Replace every universal with its actual tested scope.
3. **"Did you test that, or does it just make sense?"** — The red-team-auditing ladder, applied to prose: reading earns "the code does X", reasoning earns "this should/would X", only execution earns "this does X — here is the run". CONFIRMED, PROVEN, GUARANTEED, DEMONSTRATED are induction words; using them on un-run reasoning is symbol abuse, and the first reviewer who asks "confirmed against what?" voids the whole document.
4. **"What would change your mind?"** — A conclusion with no stated falsifier reads as faith. One sentence — "this conclusion would be reopened by evidence that…" — converts it into method. Fallibilism on the page.
5. **"What did you not examine?"** — Scope limits, untested inputs, assumptions taken from others. If the examiner discovers a limitation you knew and omitted, everything else you wrote becomes suspect. If *you* state it first, it becomes evidence of rigor. The limitation you disclose inoculates; the limitation they unearth convicts.

The Daubert factors, translated: state the **method** (so it can be tested by someone else), the **error rate or bounds** (so the confidence is quantified, not performed), and the **standards followed** (the protocol, the skill, the checklist). A conclusion carrying those three survives; naked conclusions do not.

---

## Part 3 — Admitting Uncertainty Without Weakening the Conclusion

The false dilemma to reject: *either* sound confident *or* sound honest. The resolution is that uncertainty has two completely different grammars, and only one of them is weak:

**Weasel hedging (banned):** uncertainty smeared over the whole claim — "it seems that the system might potentially be somewhat vulnerable in certain cases." Protects the author, informs no one, and *invites* attack because it signals the author does not know where their own claim's edges are.

**Precision bounding (required):** uncertainty located exactly at the claim's edges, leaving the interior at full strength — "Under the threat model where the attacker controls the label field, the verdict degrades from MALICE to NOISE — reproduced in 12/12 runs (script in `poc/`). Outside that threat model, no degradation vector was found in this round." Nothing in that is hedged; everything in it is bounded. It concedes territory the author never held and defends the rest absolutely.

Techniques:

- **Scope, then commit.** State the boundary conditions first, then assert without qualifiers inside them. "Within X, Y holds" is stronger than "Y mostly holds".
- **Quantify or rank.** "High confidence" is theater; "12/12 reproductions", "the only hypothesis of three surviving falsification", "±4% at 95%" are evidence. Where numbers don't exist, use the family's ordinal ladder explicitly (code fact / plausible hypothesis / confirmed / falsified) — a shared ordinal beats a private adjective.
- **Separate confidence in the method from confidence in the conclusion.** "The method is standard and was followed exactly; the sample was small" is an honest sentence no hedge can produce.
- **One uncertainty, one location.** Central claims carry their bound at first statement; a "Limitations" section collects the global ones. An uncertainty mentioned nowhere is a landmine; mentioned everywhere, it is fog.
- **Never let the summary outrun the body.** Executive summaries are where earned bounds go to die — the body says "consistent with", the abstract says "caused by". The summary may compress the claims; it may not promote them. Audit the summary against the body last, sentence by sentence.

---

## Part 4 — Word Discipline

Words are signs; the reader's interpretant must match the evidential object. Some maintain that mapping only under strict rationing:

- **Induction-only words** — *proves, confirmed, demonstrated, guaranteed, verified, always, never, impossible, eliminates*: each appearance must sit next to its executed evidence, or be downgraded (→ *indicates, is consistent with, is designed to, no case found in scope X*).
- **Causality words** — *because, caused, due to*: only with the discriminating experiment or the surviving-rival argument in view.
- **Self-praise adjectives** — *robust, rigorous, comprehensive, thorough, extensive, state-of-the-art*: these describe the author's wish, not the work. Delete them; let the method section make the reader think them. An adjective doing the work of evidence is the prose version of validation theatre.
- **Passive-voice authority** — "it was determined that", "it is understood": determined *by whom, from what?* The passive erases the chain of custody. Restore the agent and the evidence, or the sentence is testimony from nobody.
- **Precision theater** — "99.97% reliable" from a sample of 30, "approximately 12,847 records": false precision is overclaiming with decimals. Significant figures are confidence claims; earn them.

---

## Part 5 — Anti-Patterns to Name and Correct

- **Layer smuggling** — inference in observation grammar; the causal "because" with no method attached.
- **The confident abstract** — summary claims stronger than any sentence in the body supports. Conclusion drift is where honest documents become dishonest.
- **The buried limitation** — the fatal caveat on page 14, paragraph 3, discovered by the reader's counsel instead of disclosed by yours.
- **Citation laundering** — citing a source that cites a source that speculates; the claim gains a footnote and loses its uncertainty in transit. Cite the origin, at the origin's own confidence level.
- **The unfalsifiable conclusion** — no stated evidence could reopen it; indistinguishable from faith, and reads as such.
- **Hedge fog** — qualifiers on every sentence as liability armor. If everything is uncertain, the document asserts nothing and the reader supplies their own (wrong) certainties.
- **The adjective résumé** — "a rigorous, comprehensive analysis" announced rather than exhibited.
- **Symmetric-sounding asymmetry** — "some say X, others say Y" when the evidence is 12/12 on one side. False balance is also miscalibration; under-claiming a confirmed result misleads exactly like overclaiming a hypothesis.
- **The silent assumption import** — conclusions inheriting an upstream report's assumptions without restating them; your document is now liable for testimony it never examined.

---

## Deliverable format

When producing or reviewing a document under this skill, close with (or apply as review lens):

```markdown
## Claim audit
Each major claim → layer (observation / inference / opinion) → evidence pointer → epistemic level.
Induction-words check: every proves/confirmed/never sits next to its executed evidence, or was downgraded.

## Bounds
Threat model / scope / sample for each central claim, stated at the claim.
Limitations section: what was not examined, assumptions imported, and from whom.

## Falsifiers
For each main conclusion: the evidence that would reopen it.

## Summary integrity
Abstract/exec-summary audited sentence-by-sentence against the body — compression yes, promotion no.

## Honest status of this document itself
Claims resting on un-run reasoning, flagged. Sources cited at origin confidence. Numbers carrying earned precision only.
```

---

## How to respond when this skill is active

- Write for the cross-examiner, not the persuaded reader; every sentence must carry or point to its answer to "how do you know?".
- Keep the three layers separate and visibly labeled — observation, inference, opinion — and split any sentence that mixes them.
- Replace universals with tested scope; replace adjectives with method; replace passive authority with agent + evidence.
- Bound, don't hedge: state the claim's edges precisely and assert with full strength inside them. Refuse hedge fog as firmly as overclaiming — calibration errs in both directions.
- Ration induction-only vocabulary (proves, confirmed, guaranteed, never) to executed evidence; downgrade everything else out loud.
- Disclose every known limitation before the reader can discover it; give every main conclusion its falsifier.
- Audit the summary against the body last: compression is allowed, promotion never.
- When reviewing someone else's document, attack the standard of evidence, not the author — re-label each claim to its honest layer and level, and phrase findings as questions the D–I cycle can answer.
