---
name: reverse-engineering
description: Disciplined reconstruction of how an undocumented, closed, or unfamiliar system works when you do NOT have its design — a binary, a network protocol, a file or wire format, an undocumented or third-party API, a firmware image, a memory dump, an opaque database, or a model whose behavior you can only infer from inputs and outputs. Use this skill whenever the user asks to reverse engineer, decode, decompile, disassemble, sniff, or figure out an unknown format/protocol/binary/API; understand "what this thing does" from the outside; infer an undocumented schema or wire format; analyze a suspicious or unknown sample for defense; or build an interoperable client against a system with no spec. Trigger even when the user only says "what is this file", "decode this dump", "how does this API actually work", "figure out this protocol", "what does this binary do", or pastes hex/packets/opaque bytes with a "what is this?" — ESPECIALLY when there is no source, because that absence is exactly the condition this skill is built for. Sibling of software-archaeology (which assumes you HAVE the source); this one is for when you do not. Fifth member of the family — abductive-engineering (inquiry), secure-by-construction (building new), red-team-auditing (attacking finished), software-archaeology (changing existing source).
---

# Reverse Engineering

A methodology for *reconstructing* a system you did not design and whose source you may not have. It is the sibling of `software-archaeology`, and the difference is the whole point: archaeology holds the code and abduces the author's *intent*; reverse engineering often holds only the artifact — a binary, a capture, a format, a live black box — and must reconstruct the *mechanism*. `abductive-engineering` supplies the engine (A–D–I loop, semiotic triad); `secure-by-construction` supplies the hostile-input battery; `red-team-auditing` supplies the standard of proof (`CONFIRMED` is earned by a discriminating experiment, never asserted). This skill points all of them at a system whose interior is dark.

It exists because a language model reconstructing an unknown system has three strong and dangerous default habits:

1. **It narrates a design it cannot see.** Given a sliver of surface — a magic number, an export table, a handful of strings — it emits a confident, complete architecture, backfilling the enormous unobserved interior from training priors. A fluent story about the internals is indistinguishable, on the page, from a measurement of them.
2. **It psychologizes instead of characterizing.** It "explains" a byte by inventing what the programmer *wanted* — a motive it has no access to — when the only thing on the table is behavior it could have measured. In an adversarial target the author's apparent intent is often a *deliberate lie*.
3. **It interprets at the instant of observation.** It cannot see a string, a symbol, or an opcode without immediately assigning it a meaning, so the raw observation arrives already contaminated by a guess — and the guess is never separated back out for testing.

The three prime directives that answer them:

> **You do not have the object; you have only what the system does.** Every claim about design is a hypothesis about a *mechanism*, never a fact about a *mind*. **Reconstruct evidence, not intent.**
> **Observe before you interpret; characterize before you reconstruct.** The order is a ratchet — a meaning assigned too early poisons every measurement downstream.
> **A hypothesis that predicts nothing you can perturb is decoration.** The system is present and runnable; make it testify. If flipping the byte doesn't do what the story requires, the story is wrong.

A note on scope, up front and non-negotiable: reverse engineering is legitimate and often essential — interoperability, security research, defensive malware analysis, recovering an undocumented format, understanding legacy you inherited. It is also bounded by law, licence, and authorization (EULAs, anti-circumvention statutes, terms of service, clean-room requirements, scope of engagement). Establish that the target is yours to examine, or that you are authorized to examine it, *before* the first probe. This skill reconstructs a system in order to understand or defend it — never to enable piracy, unauthorized access, or attack. When the goal or the authorization is unclear, ask; don't proceed on assumption. (The obligation does not end at the first probe — see Part 5 on discovery responsibility.)

### Which sibling, when

The five skills partition the lifecycle; a single session often crosses between them. Route by what you have and what you want:

| You have… | You want… | Reach for |
|---|---|---|
| Nothing yet | To build it correctly | `secure-by-construction` |
| The source | To understand or change it safely | `software-archaeology` |
| The source (or a running system) | To break it / prove it unsafe | `red-team-auditing` |
| **Only the artifact — no source** | **To reconstruct how it works** | **`reverse-engineering`** |
| Any of the above, and something is surprising | To find out *why* | `abductive-engineering` |

The frequent mistake is reaching for `software-archaeology` when you don't actually have readable source — a decompiler's guesswork or a minified blob is not source, it is a degraded sign, and it belongs here. Conversely, the moment you *do* recover trustworthy source and shift to editing it, hand off to archaeology; this skill's job is done when the model is built.

---

## Part 1 — The Absent Object

Peirce: a sign stands for an object to an interpretant. Writing new code, you own the object (the intent) and choose the sign. Doing archaeology, you hold the sign (the source) and abduce the object. **Reverse engineering is the extreme case: the sign itself is degraded** — compiled, minified, encrypted, packed, or reduced to a wire capture — and the object is doubly inaccessible, because the author is not only absent but sometimes *hostile*. You are reconstructing from shadows on the wall.

This forces one hard renunciation. In archaeology, "why did the author write line 217?" is a productive question, because the code is honest testimony from an absent-but-cooperative author. In reverse engineering, **that question is a trap.** The author's intent is not observable, and in an adversarial artifact the surface is engineered to suggest a false one (a function named `checkLicense` that does nothing; strings planted to mislead; control flow obfuscated to imply structure that isn't load-bearing). So substitute the answerable question:

> Not *"what did the author mean?"* but *"what does this system **do**, and what is the smallest experiment that would make it lie less?"*

Everything you assert lands in exactly one of three tiers, and the tier must be stated with every claim. This is the spine of the whole method — the same discipline `red-team-auditing` uses for `CONFIRMED` and archaeology uses for `dead`:

- **OBSERVED** — you saw it directly, with no interpretation added. "Bytes 0–3 are `89 50 4E 47`." "The endpoint returns HTTP 429 after 100 calls in 60 s." A fact, not a meaning.
- **INFERRED** — a hypothesis consistent with observation but not yet perturbed. "Bytes 0–3 *appear* to be a magic number identifying the format." Plausible; unproven. Cap your language here at *appears / consistent with / suggests* — never *is*.
- **CONFIRMED** — a prediction derived from the hypothesis was tested by perturbation and held. "Changing byte 12 from `04` to `05` changes the decoded width from 4 to 5, as predicted → byte 12 is the width field." Earned by a discriminating experiment, exactly once, per claim.

The commonest failure of an LLM here is silently promoting INFERRED to CONFIRMED because the inference *feels* complete. Refuse the promotion until an experiment pays for it.

---

## Part 2 — Surface Mapping (observe, do not interpret)

First pass: inventory every observable sign **without assigning it an object.** The temptation is to read `encrypt` in the symbol table and write "this module does encryption." You have observed a *symbol*; you have not observed *encryption*. Record the sign; withhold the meaning.

Depending on the artifact, the cheap surface indices are:

| Artifact | Observable surface (record as OBSERVED) |
|---|---|
| Binary / executable | magic bytes, headers, sections, imports/exports, symbol table (if present), strings, entropy per section, linked libraries, embedded resources, compiler/toolchain fingerprints |
| File / wire format | magic number, length fields, offsets, repeated structures, byte histograms, entropy, alignment/padding, endianness clues, delimiters |
| Network protocol | packet sizes and cadence, handshake sequence, ports, TLS/plaintext, field boundaries that recur, request/response pairing, retransmission behavior |
| API (undocumented) | endpoints, methods, status codes, headers, rate-limit signals, error bodies, auth scheme, pagination shape, field names in responses |
| Firmware / dump | load address hints, string tables, vector tables, memory-mapped regions, recognizable constants (crypto S-boxes, protocol magics), architecture |
| Opaque model | the input space it accepts, the output space it emits, refusal/edge behaviors, latency envelope, sensitivity to perturbation |

Discipline for this pass:

- **A symbol is a *symbolic* sign — meaning by convention you may not share.** `getUserData`, `AES`, `is_admin` are the author's claims, not the system's behavior. In an honest codebase the convention usually holds; in a stripped, obfuscated, or adversarial artifact it is unreliable and sometimes weaponized. Treat every human-readable name as a hypothesis to be confirmed in Part 3, not as a fact.
- **Entropy and structure are *indexical* signs — they don't lie, and they don't explain.** High entropy indicates compression or encryption (an index, causally connected). It does not tell you *which*, or *why*. Note the index; don't narrate past it.
- **The adversarial surface lies on purpose.** Packers, fake imports, planted strings, anti-debug and anti-VM checks, timing traps, control-flow flattening — these exist to make Part 2 produce a false map. When the target may be hostile, *nothing* in the surface graduates past OBSERVED until behavior corroborates it, and you assume the surface was arranged to mislead until proven otherwise.

Output of this part is a pure inventory: signs, tiers all OBSERVED, zero architecture. If you have written a sentence containing "so this must be…", you have left Part 2 early.

---

## Part 3 — Behavioral Characterization (make it testify)

Now measure what the system *does*, black-box, before reconstructing how. This is the reverse-engineering analogue of archaeology's characterization tests, with one change: you are pinning the behavior of a system you cannot read, so the inputs must be *chosen to discriminate*, not merely to demonstrate.

**Passive before active — preserve before you perturb.** Exhaust observation before you touch anything: watch the traffic, log the behavior, capture the state, *then* start modifying inputs. This is the forensic order (preserve before modify), and it exists because the first active experiment can destroy the very information you needed — a single write triggers a one-time migration, trips an anti-tamper wipe, exhausts a nonce, advances a state machine you can't rewind, or alerts an adversary that they're being studied. On a live or irreplaceable target, snapshot first and perturb a copy. Ask before every active step: *is this reversible, and have I already extracted everything the passive phase can give?*

**Hold it still first.** You cannot characterize a system you cannot reproduce. Before drawing conclusions from any run, establish determinism: same input, same environment, same output? Determinism cuts two ways here, and both are useful: (1) if the system *should* be deterministic (a parser, a codec, a pure function) but isn't, **that non-determinism is itself a finding** — hidden state, a clock, a seed, uninitialized memory, or order-dependence you must locate and name; (2) once established, determinism becomes your instrument — it is precisely what licenses differential observation (vary one byte, attribute the whole delta to that byte, because nothing else moved). If runs don't reproduce, find the source of variance (time, randomness, network, uninitialized state, order) and control it, or your "observations" are noise wearing the costume of data. This is the reproducibility contract shared with `red-team-auditing` and `deterministic-core`; here it is a precondition for every downstream claim.

**Probe with the hostile-input battery, not the happy input.** Reuse the table from `secure-by-construction` Part 1, but adapted to the black box: there you were deciding which classes to *defend against*; here you feed each class deliberately to make the system *reveal* how it reacts. A system's edges expose its internals far more than its center. The classes that pay off most when you have no source:

| Axis | Probe (feed it, watch the reaction) |
|---|---|
| Format | 0 bytes, 1 byte, truncated mid-field, `MAX_INT` size, negative/overflowing length field, length that disagrees with actual payload |
| Structure | missing required field, duplicated field, fields out of order, infinite/recursive nesting, extra trailing bytes |
| Content | null bytes mid-string, invalid UTF-8, over-long escapes, embedded path traversal, magic-number collisions |
| Sequence | packets out of order, duplicated, replayed, arriving after a reset, with future/past timestamps, mid-handshake abort |

Each probe is a question the system answers in the language of its own structure: a length field one past the maximum tells you where the bounds check lives (or that there isn't one); a replayed packet tells you whether there's a nonce or sequence number; an out-of-order field tells you whether the parser is positional or tag-driven.

**Vary one thing; observe the delta.** Differential observation is the core move. Change a single byte, a single field, a single header, and record exactly what changed in the output, the error, the timing, the side effects. A field you cannot perturb-and-observe you have not characterized — you have only seen it. Record for each probe: input → output, error behavior, side effects (files, network, state), and the timing envelope (timing is an observable; Hyrum's Law from `software-archaeology` applies to systems you're decoding too — someone depends on it).

Output of this part is a behavioral map: input/output pairs, error responses, the determinism verdict, and the deltas from perturbation. Still no committed architecture — but now every future claim can be checked against a measurement.

---

## Part 4 — Structural Reconstruction and Validation

Only now, on top of a surface inventory and a behavioral map, build the model: the format grammar, the state machine, the data flow, the module decomposition, the implicit contracts and invariants. And build it the way `abductive-engineering` demands — with rival hypotheses, never one.

**Generate competing hypotheses (aim for 3) for every structural claim, and rank them by economy of research.** "Bytes 8–11 are a length" competes with "bytes 8–11 are a checksum" competes with "bytes 8–11 are a timestamp." Do not fall in love with the first fit; the first fit is the one your priors handed you, and priors are exactly what an unknown system is built to violate.

Peirce's *economy of research* — spend the cheapest experiment that discriminates the most hypotheses — has a concrete cost ladder in reverse engineering. Climb it from the top; a cheap probe that eliminates two rivals is worth more than an expensive one that confirms your favorite:

| Cost | Probe | Example |
|---|---|---|
| Low | Flip a byte, observe the delta | Change one payload bit → does it get rejected? |
| Medium | Recompute a field and re-patch | Recalculate the candidate CRC → is the record now accepted? |
| High | Reimplement from the model | Write your own parser/encoder and round-trip against the real system |
| Very high | Instrument the execution | Attach a debugger, hook calls, run in a sandbox, trace syscalls |

Run the lowest rung that can still discriminate. Save instrumentation for what perturbation alone cannot resolve — it is the most powerful and the most expensive (and, on a hostile target, the most likely to trip anti-analysis).

**Every structural hypothesis must emit a perturbation prediction — then run the cheapest discriminating one.** This is where a claim earns CONFIRMED:

> **Hypothesis:** bytes 8–11 are a CRC32 over the payload.
> **Prediction:** flip one payload bit → the record is rejected as corrupt; recompute the CRC over the mutated payload and patch bytes 8–11 → it is accepted again.
> **Experiment:** do both.
> **Outcome:** rejected-then-accepted → CONFIRMED checksum (and you've identified the polynomial by matching). Accepted regardless → **refuted**; it is not a validated checksum. Register the surprise and re-abduce.

The rejected hypotheses are not waste — they are the reverse-engineering equivalent of the *discarded vectors* table in `red-team-auditing`, and reporting them is what proves the reconstruction was tested rather than imagined.

**The reconstructed model is itself a sign — do not mistake your map for the territory.** A clean diagram of "the protocol" is an interpretant you produced; it is CONFIRMED only where a perturbation has exercised it. Mark the model's regions by tier: the parts you've perturbed (CONFIRMED), the parts merely consistent with what you've seen (INFERRED), and the parts you're frankly guessing (label them, don't launder them). A reconstruction that is 20% CONFIRMED and honestly says so is worth more than one that is 100% fluent and untested.

**Validate by construction.** The strongest confirmation of a reconstructed format or protocol is a *second implementation*: write an encoder/parser/client from your model and run it against the real system (parse what it emits; get it to accept what you emit). This is the parallel-run idea from `software-archaeology` turned into an oracle — the real system grades your understanding on every round-trip, and disagreement is a precise, located finding.

### Worked micro-example (use this shape when demonstrating)

An unknown file. The whole method in miniature — surface to confirmed, with rivals killed by the cheapest probe:

> **OBSERVED:** bytes 0–3 are `89 50 4E 47`. (No meaning assigned — just the bytes.)
> **Abduce (rivals):** H1 — this is the PNG magic number (`50 4E 47` = "PNG"). H2 — it's a generic file signature I'm pattern-matching too eagerly. H3 — it's encrypted/compressed content that happens to collide with a known magic.
> **Deduce a discriminating prediction (H1):** if it's the PNG signature, a PNG decoder will parse the following chunks (`IHDR`, dimensions, etc.); and corrupting byte 1 `50`→`51` will make any PNG tool reject it as an invalid signature — while under H3, a one-byte change to a header it doesn't actually use should leave decoding unaffected.
> **Induce (cheapest probe — a byte flip, the low rung):** patch byte 1 to `51`; `file` now reports a corrupt/unknown type and `pngcheck` rejects the signature; restore it and both accept and read a coherent `IHDR`.
> **CONFIRMED:** H1 — it is PNG. H2 and H3 **refuted** (the byte *is* load-bearing to a PNG parser, and a real PNG structure decodes after it). Cost paid: one byte flip.

Notice the tiers never skip a rung: `89 50 4E 47` was OBSERVED, "PNG magic" was INFERRED until the flip, and only the perturbation earned CONFIRMED.

---

## Part 5 — Coverage, Provisionality, and Responsibility

Three disciplines that govern the reconstruction as a whole, not any single stage.

**Coverage — absence of evidence is evidence only of search coverage.** The gravest risk in reverse engineering is rarely a false hypothesis; it is an *unknown unknown* — a whole subsystem, code path, protocol state, or capability you never observed because you never searched where it lives. "I didn't find authentication" is not "there is no authentication"; it is "the inputs I sent didn't exercise it." So separate the two claims explicitly and never let one masquerade as the other:

> Absence of evidence is evidence only of search coverage, never of absence.

Record what search spaces you explored and which remain dark: inputs tried vs. input classes untried; code paths reached vs. reachable-but-unreached; protocol states visited vs. states the machine implies exist; the packed section you never unpacked; the config-gated branch you never triggered. A reconstruction that names its blind spots is trustworthy; one that is silent about them is quietly claiming total coverage it never had.

**Provisionality — every model is held, never proven.** A reconstruction is an abduction that has so far survived its experiments; that is the *most* that can ever be true of it. It is never proven correct — the next input, the next firmware version, the next captured packet can refine or overturn it. This is Peirce's fallibilism, and it is not a hedge but an operating instruction:

> Every reconstruction is provisional. A model survives experiments; it is never proven true. Future evidence may refine or replace it.

State, in the deliverable, what observation would falsify or extend the model — the input you'd send next, the version you'd diff against. A model that cannot say what would surprise it has stopped being science.

**Discovery responsibility — what to do when you find more than you were looking for.** Reconstruction routinely surfaces things beyond the mechanism: personal data, credentials or keys, another party's proprietary material, or evidence of illicit activity, sometimes in a system that is not fully yours. When that happens, the correct move is often to **stop and report**, not to keep digging. Do not exfiltrate, retain, or exploit what you find; narrow or halt the work; escalate to the owner, your engagement contact, or the appropriate authority as the situation and your legal obligations require. This skill reconstructs a system to understand or defend it — the instant the work turns up something that belongs to someone else or exposes them to harm, understanding stops and responsibility takes over.

---

## Part 6 — Anti-Patterns to Name and Correct

- **Hallucinated architecture** — a complete internal design narrated from a fragment of surface. The unobserved interior filled with priors and presented at the confidence of measurement.
- **Symbol-as-truth** — believing `decrypt()` decrypts, `is_admin` gates admin, `harmless.dll` is harmless, because the name says so. Names are the author's claims; in adversarial targets they are bait.
- **Intent psychology** — "the developer probably wanted to…" A story about a mind you cannot observe, standing in for behavior you could have measured. Reconstruct evidence, not intent.
- **Interpretation at first sight** — assigning meaning during Part 2, so the observation is contaminated before it's recorded. The map is drawn before the ground is walked.
- **The confirmatory probe** — feeding only inputs the favored hypothesis predicts, never the input that would refute it. A checksum "confirmed" without ever flipping a bit.
- **INFERRED laundered to CONFIRMED** — a plausible inference stated as fact because it felt complete. The single most common failure; no experiment paid for the promotion.
- **Nondeterminism ignored** — drawing conclusions from runs that don't reproduce, treating variance as signal.
- **Trusting the surface of a hostile artifact** — reading a packed/obfuscated sample's planted strings and fake imports as if the author were cooperating. The author is absent *and* adversarial; the surface is a weapon.
- **The single hypothesis** — one explanation, never a rival, so nothing discriminates and the first guess wins by default.
- **Active before passive** — the first move is a perturbation, and it destroys the state, trips a wipe, or alerts the target. Information you could have had for free is gone because you modified before you observed.
- **Absence as proof** — "I didn't find X" reported as "X isn't there." A claim about coverage smuggled out as a claim about the system. The unsearched space is treated as empty.
- **The finished model** — presenting the reconstruction as proven rather than as an abduction that has so far survived, with no statement of what would falsify it or what regions remain unexplored.

---

## Deliverable format

```markdown
## Scope & authorization
What the target is; the basis for examining it (ownership / authorization / legal scope).
What was deliberately left untouched, and why.

## Surface inventory
Observable signs only — headers, symbols, strings, formats, endpoints, entropy, timing envelope.
Tier: OBSERVED throughout. No meanings assigned. (Hostile surface flagged as possibly deceptive.)

## Behavioral map
Determinism verdict (reproducible? variance controlled how?).
Input → output / error / side-effect / timing pairs. Probes run (hostile-input battery).
What was varied, what changed (the deltas).

## Reconstructed model
Format grammar / state machine / data flow / module decomposition / implicit contracts.
Each element tagged OBSERVED | INFERRED | CONFIRMED (by which perturbation).
Rival hypotheses still live, and the cheapest experiment that would discriminate them.

## Confidence ledger
CONFIRMED — prediction P, perturbation X, observed Y as predicted: …
INFERRED — consistent with observation, not yet perturbed: …
OBSERVED — raw, uninterpreted: …
Refuted hypotheses (the discarded-vectors table): what they were, what killed them.
Guessing / not tested: where the model is fiction, said plainly.

## Validation
Second-implementation round-trip results (parser/encoder/client vs. the real system), if built.
Disagreements found — each a located finding.

## Coverage & residual uncertainty
Search spaces explored vs. left dark (input classes untried, code paths unreached,
protocol states unvisited, sections not unpacked).
What would falsify or extend the model — the next input / version to try.
Absence-of-evidence claims stated as coverage claims, not as claims about the system.

## Honest status
- % of the model CONFIRMED by perturbation: __
- % INFERRED (consistent, not yet perturbed): __
- % guessed (untested — fiction, said plainly): __
- Probes / experiments not run, and why: __
- Findings that refuted my own earlier reconstruction: __
- Discovery-responsibility events (anything found that triggered stop/report): __
```

---

## How to respond when this skill is active

- Reconstruct the mechanism, not the mind. Never explain a byte by the author's supposed intent; explain it by an experiment. **Reconstruct evidence, not intent.**
- Keep the stages in order and don't collapse them: map the surface without interpreting, characterize behavior before reconstructing structure. A meaning assigned early is a measurement poisoned late.
- Establish determinism before believing any run. Uncontrolled variance is noise, not evidence.
- Every claim carries its tier — OBSERVED / INFERRED / CONFIRMED — and INFERRED never graduates to CONFIRMED without a discriminating perturbation. Cap unproven claims at *appears / consistent with*.
- Generate rival hypotheses (aim for 3) for every structural guess; rank by economy of research; run the cheapest discriminating probe first. Report the refuted rivals — they prove the work was tested.
- Probe with the hostile-input battery from `secure-by-construction`, not the demo input. Edges reveal internals.
- Treat a hostile artifact's surface as engineered to mislead until behavior proves otherwise; a symbol is a claim, not a fact.
- Validate by building a second implementation and letting the real system grade it. Round-trip disagreement is your sharpest finding.
- Observe and preserve before you perturb: exhaust the passive phase, snapshot irreplaceable state, and check reversibility before any active experiment. The first perturbation can erase what you needed.
- Declare coverage, not just findings: separate "I did not observe X" from "X is absent," and name the search spaces still dark. Absence of evidence is evidence only of search coverage.
- Hold every reconstruction as provisional — an abduction that has survived, never a proof. State what would falsify or extend it.
- State scope and authorization before the first probe; if either is unclear, ask. Stay inside what's yours or authorized to examine. If the work turns up personal data, secrets, or evidence of wrongdoing — especially in a system that isn't yours — stop and report rather than dig further.
- When an experiment refutes your earlier reconstruction, say so at once and correct the model — the corrected map is the deliverable, not the confident first story.
