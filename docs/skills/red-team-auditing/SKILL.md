---
name: red-team-auditing
description: Adversarial security auditing and red-teaming of your own systems with strict epistemic discipline. Use this skill whenever the user is red-teaming, doing a security audit, adversarial review, threat modeling, or "trying to break" their own code or system; whenever they ask you to find bugs, vulnerabilities, invariant violations, or architectural fractures; whenever they want to audit another agent's audit or check whether a finding is real; and whenever a report labels something "CONFIRMED / EXPLOITABLE / bypass" and the certainty needs to be earned rather than asserted. Trigger even if the user only says "find more", "attack this", "poke holes", "cuchi cuchi red team", or pastes an audit/finding table for review. Pairs with the abductive-engineering skill — this is its adversarial application.
---

# Red-Team Auditing

A methodology for adversarial security auditing that refuses to inflate certainty. It is the adversarial application of `abductive-engineering`: the A–D–I loop (abduction → deduction → induction) is the engine, and this skill adds the discipline that separates a real finding from a plausible story dressed up as a fact.

The central failure mode of security audits is **not** missing bugs. It is **overclaiming** — writing "EXPLOITABLE — CONFIRMED" on top of an architectural hypothesis that was never executed. An audit that overclaims is worse than useless: it launders a guess into evidence, and the first competent reviewer who asks "confirmed against what?" destroys the credibility of every other finding in the document.

So the prime directive of this skill: **certainty must be earned by induction, never asserted by confidence.**

---

## Part 1 — The Epistemic Ladder (the core discipline)

Every finding carries an explicit epistemic level. Never let a finding float without one. The label is a *sign* (Peirce): its interpretant in the reader's mind must match its object (the actual evidence). A finding labeled CONFIRMED that rests on code-reading is symbol abuse — the conventional meaning of the word contradicts what was actually done.

| Label | What it means | What earns it |
|-------|---------------|---------------|
| **CODE FACT** | Directly observable in the source; no inference needed. | Reading the code. `write_text()` is on this line; the enum is validated but not signed. |
| **PLAUSIBLE HYPOTHESIS** | An abduction with architectural evidence. The mechanism *could* produce the effect. | Reasoning from the code. **Not run.** This is the ceiling for anything you have not executed. |
| **CONFIRMED BY INDUCTION** | A prediction was deduced, executed, and observed to hold. | A reproducible experiment with before/after. |
| **FALSIFIED** | A prediction was executed and did **not** hold. The hypothesis is rejected. | The same experiment, producing a negative. |

**The one rule that matters most:** a plausible abduction is not a finding. Reading code and deducing a consequence gets you to PLAUSIBLE HYPOTHESIS. The word CONFIRMED (and its cousins EXPLOITABLE, bypass, race condition *demonstrated*) requires the induction step — you ran it, you watched the prediction come true. If you did not run it, the maximum honest level is "plausible hypothesis with architectural evidence."

**Falsification is a first-class result, not a failure.** The strongest thing an audit can contain is a hypothesis the auditor tried to confirm and instead *falsified*. It proves the method has teeth. When an experiment refutes your own earlier claim, say so loudly and correct the vector — that is where credibility is manufactured.

> **Worked example (real shape).** An audit claimed a filter was bypassable by *injecting* a crafted exculpatory artifact, labeled EXPLOITABLE — CONFIRMED, on code-reading alone. Induction: run it on real cases. Result — injection **FALSIFIED** (0/N degraded, because the "set-aside" mechanism *removes* the artifact, so an extra one is net zero). The real vector turned out to be *relabeling* an existing incriminating artifact (the label field is input-controlled). Corrected finding: CONFIRMED BY INDUCTION for relabel, FALSIFIED for injection. The audit got *stronger* by admitting the first framing was wrong.

---

## Part 2 — Separate the Three Things Audits Conflate

Most bad audit findings are one of three different things wearing a "vulnerability" costume. Sort every finding into exactly one bucket before assigning severity:

1. **Software vulnerability** — a defect in the code that an attacker within the threat model can exploit. This is the only bucket that earns a severity rating on its own.
2. **Threat-model assumption** — "if the attacker is already root / already controls the input / already has the HMAC key, then…". Often true and often *uninteresting*: if the precondition is already game-over, the finding downstream of it is not the bug. Name the precondition and ask whether it is reachable.
3. **Generic best practice / hygiene** — "rotate keys", "sign binaries", "use constant-time compare", "add a size cap". Real, worth a ticket, but it is hardening, not an exploit. Do not dress hygiene as a breach.

A related distinction the skill enforces constantly: **an implementation being minimal is not the same as a protocol having a bypass.** "The mandatory-refutation step is currently a presence-check auto-filled by template" is a true CODE FACT about *implementation*. "The refutation protocol has a bypass" is a stronger, different claim about *design*. They are not equivalent. Keep them apart.

And the criticism that sounds deep but is actually universal: **a hash proves integrity, not truth.** A signature certifies that bytes did not change after signing; it never certifies that the signed conclusion is correct. This is how every signed system on Earth works. Note it if relevant, but do not present a property of digital signatures as a vulnerability of *this* system.

---

## Part 3 — The Threat Model Is Mandatory and Explicit

No finding is CONFIRMED in the abstract. It is confirmed **under a stated threat model.** Open every audit (and qualify every high-severity finding) with the model explicitly:

- What can the attacker do? (e.g. *modify the input JSON*)
- What can they **not** do? (*cannot modify code; does not hold the HMAC key; does not compromise the kernel; cannot alter the bundle after sealing*)
- Which trust boundary does the finding cross?

Then phrase confirmations as: **"Confirmed under the threat model where the attacker controls X."** This single habit eliminates most of the noise in a security report, because a huge fraction of "findings" quietly assume a capability that, if the attacker had it, would make the finding irrelevant.

The sharpest framing to reach for — the "judge test": *If a judge asked me to prove this system's guarantee can never be violated, what would I have to assume as true?* Then attack each assumption. That is where the real findings live.

---

## Part 4 — The Escalation Ladder

Audits get more interesting as they climb. Do not keep hunting local defects once a codebase has passed that stage — move up the ladder. Each round targets a different *kind* of failure.

**Round 1 — Local defects.** The classic bug hunt: TOCTOU, symlink traversal, injection, unhandled overflow, non-constant-time compare, import smells, missing size caps. Objective, verifiable, cheap. Necessary but shallow. Exhaust it, then leave it.

**Round 2 — Invariants.** Stop asking "is this function buggy?" and start asking "what property does the system *promise*, and where can it stop holding?" Targets: atomicity (crash between two writes), idempotence (running twice ≠ running once), monotonicity (adding evidence should never *lower* confidence; adding a relevant document should never *worsen* recall), temporal consistency (clock skew, future/negative timestamps, DST, leap seconds), determinism (same state → same output).

**Round 3 — Emergent / architectural.** The deepest and most valuable. Each module is individually correct; the *composition* is not. Targets:
- **Composition breaks** — module A's contract and module B's contract are each satisfied, but their combination violates a system invariant (e.g. `store()` succeeds, process crashes, `audit.append()` never runs → "every memory has provenance" is now false).
- **Trust-boundary gaps** — a critical piece of state lives *outside* the cryptographic perimeter (the index is sealed but the content DB is not; modify it without breaking the audit trail).
- **Authority conflicts** — when component X, the audit log, and the vault disagree, *who wins?* Can that disagreement even arise?
- **Unbounded growth / runaway dynamics** — a score with no ceiling reaching `inf` after N reinforcements; an unbounded vocabulary; a weight loop with no damping (hysteresis, oscillation, runaway potentiation).

The signal that you have graduated a codebase from Round 1 to Round 3: your findings stop being "there's a bug on line 42" and start being "the system can reach a state its specification says is impossible."

---

## Part 5 — The Attack Taxonomy

A working checklist for Rounds 2–3. Not exhaustive; a prompt for hypotheses. For each, run the A–D–I loop — do not stop at "this looks attackable."

- **Semantic integrity** — can the system preserve, perfectly and verifiably, a *wrong* payload? Contradictory documents, two conflicting testaments, an old memory that contradicts a new one. Not a crypto bug — an identity-of-knowledge bug.
- **State / memory poisoning** — can you reinforce a false memory, make a true one be forgotten, saturate the weights? Is there hysteresis, oscillation, runaway potentiation? Who is authorized to call `reinforce()` / `forget()`? (If anyone/any plugin can, it escalates; if only an authenticated owner can, it is hardening — *state the precondition.*)
- **Retrieval robustness** — thousands of near-identical documents, empty documents, colliding embeddings, unicode noise, degenerate TF-IDF. Does ranking stay stable?
- **Identity** — "Juan Pérez", "Juan A. Pérez", "J. Pérez", "Juan Perez". One person or five? What does the system decide, and can that decision be forced?
- **Temporal** — clock backward/forward, timezone, DST, leap second, future timestamp, negative timestamp, epoch edges. Especially anything gating on time (inactivity/date conditions).
- **Monotonicity** — the property-based lens: adding evidence must never reduce confidence; adding a relevant document must never worsen recall. Find the input that breaks the monotone.
- **Canonicalization fuzzing** — NFC vs NFD, CRLF vs LF, tabs vs spaces, float vs Decimal, dict ordering, emoji, UTF-16, surrogate pairs. Hunt for *two distinct objects → one canonical form* (collision) or *one object → two canonical forms* (instability).
- **Audit-chain plausibility** — hashes can be perfectly valid over a history that is *semantically impossible*: events out of causal order (A→C→B), duplicates, gaps. A chain proves insertion order and integrity, not causality — note that boundary honestly rather than selling it as a break.
- **Recovery / crash** — cut power / sqlite / write / fsync / rename at every point. What state remains? Is it recoverable, or is the artifact truncated and the payload lost?
- **Concurrency** — two owners, two heirs, owner and heir at once, two processes on one vault. Last-write-wins silently eating data is the classic.
- **Cumulative degradation** — after 100k records, after years, after thousands of reinforce/forget cycles. Does a correct system stay correct at scale?

---

## Part 6 — The Reproducibility Contract

Every finding labeled CONFIRMED BY INDUCTION ships with the evidence to reproduce it. No exceptions. The goal is to make "well, it didn't repro for me" impossible.

A confirmed finding includes:
- **A runnable script** (or exact command sequence) that executes the induction and prints the before/after.
- **The commit SHA** the experiment ran against, and whether the fix was present or absent (audit the *vulnerable* state).
- **Runtime versions** — language/interpreter version, key library versions.
- **A hash or identifier of the corpus / fixtures** used, so the input set is pinned.
- **The prediction, stated before the result** — "predict `hits == []`; observed `[]`; holds." The prediction must precede the observation in the write-up, or it reads as post-hoc.

For Q4-style "the fix is independent / complete" claims, independence is itself a claim that needs evidence, not assertion: enumerate *all* consumers of the changed code path, show the test suite is identical to baseline before/after, and state explicitly what you did **not** verify. "I reviewed the write sites" is not "I enumerated every consumer."

---

## Part 7 — Precision of Language

Findings are signs addressed to a reader who will act on them — sometimes a judge, sometimes an external red team. Word them so the natural interpretant matches the object exactly. Small imprecisions read as overclaims and invite easy rebuttals.

- Not **"the sealed verdict is manipulable"** (sounds like the seal broke) — but **"a wrong verdict can be sealed"** or **"a wrong verdict can be induced before sealing."** The seal works perfectly; the *input* was poisoned. For a judge, that difference is enormous.
- Not **"confirmed on the sealed verdict"** — but **"reproduced experimentally on the execution path that produces the sealed bundle."** You demonstrated the pipeline *reaches* another verdict before sealing; you did not break sealing.
- Not **"CONFIRMED"** bare — but **"CONFIRMED under the threat model where the attacker controls X."**

When a finding demonstrates *that* something happens, also show *why* — the causal chain, not just the outcome. A mechanism the reader can follow is far harder to dismiss than a result they have to take on faith:

```
input-controlled label
    ↓ set as "exculpatory"
set_aside() removes artifact from scoring
    ↓
composite recomputed without it
    ↓
corroboration gate flips
    ↓
verdict degrades  (MALICE → NOISE)
```

---

## Part 8 — Discarded Vectors Are Part of the Deliverable

The vectors you *tried and could not exploit* belong in the report, in their own table. They show the audit was adversarial rather than confirmatory, they save the next auditor from re-running dead ends, and they demonstrate the falsification step actually happened. Record what was tested, the result, and the reason it failed (deduction predicted no effect / induction produced no effect / precondition unreachable).

---

## Part 9 — Auditing Another Agent's Audit

When reviewing a finding produced by another model (or your own earlier pass), **attack the method, not the author.** A critique aimed at the writer invites defensiveness and a status fight; a critique aimed at the standard of evidence invites revision. It is also simply the more correct move — the question is never "are you embarrassed?" but "confirmed against what evidence?"

Ask, in order:
1. **What epistemic level is this actually at?** Re-label every finding CODE FACT / PLAUSIBLE HYPOTHESIS / CONFIRMED / FALSIFIED honestly. Most inflation lives here.
2. **Where is the induction?** If a finding says CONFIRMED, demand the reproduction, the PoC, the before/after. Absent that, downgrade to plausible hypothesis — no exceptions for a persuasive narrative.
3. **What's the threat model?** If "confirmed" omits the attacker's assumed capability, the finding is under-specified.
4. **Which bucket (Part 2)?** Is this a vulnerability, a threat-model assumption, or hygiene wearing a costume?
5. **Is the language precise (Part 7)?** "Manipulated the sealed verdict" vs "sealed a wrong verdict."

Frame every note as a hypothesis, not a verdict — "If the label is input-controlled here, this degrades; is that reachable in the real acquisition chain?" — which invites the D–I cycle instead of a defense.

---

## Report Structure

Use this template. Adjust depth to the audit, but keep the epistemic column and the threat-model section always.

```markdown
# Security Audit — <system> <version>
## Red Team Round <N>
**Date:** <date>  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing
**Scope:** <what was and was not in scope>
**Base:** <branch> @ <commit SHA>  **Reproducible evidence:** <script paths>

## Threat model
- Attacker CAN: <capabilities>
- Attacker CANNOT: <explicit exclusions>

## Epistemic legend
CODE FACT · PLAUSIBLE HYPOTHESIS · CONFIRMED BY INDUCTION · FALSIFIED

## Executive summary
| ID | Severity | Level | Module | Finding |
|----|----------|-------|--------|---------|

## Findings (each one)
### <ID> — <title>
**Severity:** …  **Epistemic level:** …  **Bucket:** vuln / threat-model / hygiene
- **Surprise / expectation violated:** …
- **Abduction:** … (multiple rivals, ranked by economy of research)
- **Deduction:** falsifiable prediction, stated *before* the result
- **Induction:** experiment + before/after (or: not run → level capped at hypothesis)
- **Causal chain:** … (mechanism, not just outcome)
- **Threat-model precondition:** …

## Discarded (non-exploitable) vectors
| Vector | Result | Why it failed |

## Recommendations (out of scope of this change — record only)
```

---

## How to respond when this skill is active

- Generate **multiple rival hypotheses** per surprise, ranked by cost-to-test (economy of research), then run the cheapest discriminating experiment first.
- Never write CONFIRMED/EXPLOITABLE/bypass without an executed induction. Cap un-run findings at PLAUSIBLE HYPOTHESIS out loud.
- Treat a self-falsification as a win and correct the vector immediately.
- Always state the threat model; always sort each finding into the vuln/assumption/hygiene bucket.
- Climb the ladder: once local defects are exhausted, hunt invariants, then emergent/architectural fractures.
- Keep confidence language tracking the evidence exactly: suspected → corroborated → confirmed by discriminating test. Fallibilism stays on — a confirmed root cause does not close the search for a second contributing cause.
