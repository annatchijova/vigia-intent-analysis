# VIGÍA for Mozilla — the honest, extended account

This document exists because a submission form can't be edited after the
fact, and a short pitch can't carry the full context a technical reviewer —
or a curious grant committee — deserves. If you're reading this because you
reviewed the Mozilla application, this is the detailed version of what that
form said, written where it can be verified against real code instead of
taken on faith.

## What I told Mozilla, and what I'm actually doing about it

I told Mozilla that VIGÍA exists, and that I would rewrite it so AI is a
genuine protagonist of the work, because that's what the program asks for and
because it's true: as it stood, VIGÍA was architected so the LLM *never*
touches the verdict. That's not an oversight to patch — it's the entire point
of the system, a deliberate design choice for a forensic tool meant to be
usable in judicial contexts under something close to the Daubert standard.
Removing that constraint to "comply" with an AI-protagonist program and
calling it the same project would have been dishonest in the other direction.

So instead of rewriting VIGÍA in place and quietly dropping the rigor that
made it worth building, I split it:

- **FRACTURE** — [github.com/annatchijova/fracture](https://github.com/annatchijova/fracture) —
  is VIGÍA exactly as it was when I applied: the deterministic engine, the
  102,000+ lines of production Python, the 617 sealed forensic bundles, the
  11 red-team rounds, the full academic documentation in four languages. It
  stays in active maintenance. Nothing about it is deprecated, hidden, or
  quietly abandoned — its original README lives on, unedited, at
  [`docs/README_FRACTURE_LEGACY_EN.md`](./README_FRACTURE_LEGACY_EN.md) in
  this very repository, and the repository itself is a full, independent
  clone with its own GitHub remote.
- **VIGÍA** (this repository, `vigia-intent-analysis`) — becomes the
  AI-protagonist rewrite I committed to. It keeps VIGÍA's forensic domain,
  its theoretical foundations (Peirce, Eco, Grice, Carnegie), and the
  integrity mechanisms that make trusting an LLM in this context defensible
  (Kassandra Protocol, the hallucination guard — detailed below) — but
  restructures the investigation itself around an AI agent that proposes,
  drives tool use, and narrates throughout, instead of being locked out of
  the decision entirely.

This is not me pretending the old VIGÍA was always AI-protagonist, and it's
not me abandoning the rigor that made it worth funding in the first place.
It's a fork with an honest name on each half, done in the open, with both
halves staying on GitHub under the same Apache 2.0 license.

## Why the split instead of a rewrite-in-place

A forensic intent-analysis engine aimed at judicial admissibility and an
AI-assisted investigation companion aimed at helping peritos, cybersecurity
practitioners, and DFIR investigators move faster are not the same product,
even though they share a domain and a theoretical foundation. Collapsing them
into one README would force a false choice: either keep overselling the old
system as "AI-protagonist" when its architecture explicitly isn't, or quietly
throw away eleven red-team rounds and a determinism guarantee that took real
engineering discipline to build. Splitting the identity lets both things be
true at once, legibly, without either one borrowing credibility from the
other under false pretenses.

## What actually carries over, and what's genuinely new

**Carries over, unchanged in substance:**

- The forensic domain: Indicators of Intent (IoI), not just Indicators of
  Compromise (IoC) — the question "why did this happen, and who benefits from
  that interpretation," not just "what happened."
- The theoretical foundation: Peircean abduction (Firstness/Secondness/
  Thirdness), Eco's theory of overinterpretation and significant silence,
  Grice's cooperative principle, Carnegie's manipulation taxonomy.
- The Kassandra Protocol (`vigia/vigia_sift_bridge.py`) and the Hallucination
  Guard (`vigia/llm/hallucination_guard.py`) — both detailed in the main
  [`README.md`](../README.md) with correct file attribution. These aren't
  decorative; they're the specific reason an AI-protagonist VIGÍA doesn't
  have to mean an unverifiable one.
- The commitment to a public bug registry (`BUGS_HISTORICO.md`) instead of
  erasing found defects — carried into this repository's own future work,
  not just inherited as a historical artifact.

**Genuinely new, and genuinely unfinished:**

- An agent architecture where the LLM drives the investigation loop, instead
  of narrating after the fact. This is in active development; see the main
  README's Roadmap section for what's shipped versus what's direction.
- A reworked MCP/API surface, inspired by the multi-agent orchestration and
  telemetry patterns in two other projects of mine, [annaconda](https://github.com/annatchijova/annaconda)
  and [zaynor](https://github.com/annatchijova/zaynor), and situated within
  the broader agent ecosystem I've been building under
  [krakadyl](https://github.com/annatchijova/krakadyl) and the MCP registry
  [cuartel](https://github.com/annatchijova/cuartel). None of this is a claim
  that VIGÍA already uses that architecture — it's the direction I'm pulling
  it toward, named explicitly so it can be checked against what actually
  ships.
- UI work aimed at a wider range of users, including neurodivergent people —
  explicitly future work, not something to imply exists today.
- An open question I haven't resolved yet and am not going to pretend I have:
  whether the deterministic Mode 1 engine stays directly reachable from this
  repository or lives purely under FRACTURE. I'd rather say "undecided" than
  invent an answer for a grant document.

## The part that matters most to me: not lying by omission

I have an explicit personal rule, independent of this application: I don't
publish results that look more finished than they are, and I don't let a
pitch's persuasive pressure quietly inflate a claim past what I can actually
back with a reproducible check. That rule produced some specific, slightly
awkward decisions in this document and in the main README:

- I did not invent a "200 independent cases" or "war mode" figure, even
  though it would have made for a cleaner sentence. The real, documented
  numbers are 158/162 (97.5%) on the label-blind detection corpus and
  187/199 (94.0%) on the mixed adversarial corpus — both in
  [`docs/ACCURACY.md`](./ACCURACY.md), both reproducible with the commands in
  the README.
- I did not assert "three hashes match, the fourth differs because of a
  timestamp" as a settled fact, because I have not personally re-verified
  that exact claim against the current code in this session. The four-hash
  mechanism (`show_4_hashes.py`) is real and documented; the specific
  match/mismatch pattern is flagged as pending re-verification rather than
  stated as given.
- I corrected my own earlier framing of where the Kassandra Protocol lives in
  the code (`vigia_sift_bridge.py`, not `hallucination_guard.py`) once I
  checked it against the live file, instead of letting the more convenient
  framing stand.

None of this is about hedging for its own sake. It's the same discipline that
produced the bug registry in the first place: a known limitation, stated
plainly, is worth more than an impressive claim that doesn't survive someone
actually running the code.

## The ecosystem this sits in

VIGÍA/FRACTURE isn't a standalone artifact — it's one node in a body of work
on deterministic, verifiable, and adversarially-tested systems that keep AI
out of (or honestly bounded within) consequential decisions:

- **[krakadyl](https://github.com/annatchijova/krakadyl)** — an
  active-investigation agent where the AI proposes and a deterministic engine
  decides and seals every verdict before any model is called.
- **[annaconda](https://github.com/annatchijova/annaconda)** — endpoint and
  fleet forensic acquisition; a fleet of agents investigate and delegate,
  while deterministic code seals and adjudicates before any model narrates.
- **[zaynor](https://github.com/annatchijova/zaynor)** — local AI-assisted
  DFIR that normalizes and freezes evidence before VIGÍA's deterministic
  analysis, then lets an agent explain sealed findings through read-only
  queries.
- **[cuartel](https://github.com/annatchijova/cuartel)** — an MCP registry
  tying this fleet of forensic tools together across Claude Code, Codex, and
  OpenCode.
- **[velo](https://github.com/annatchijova/velo)** — zero-knowledge forensic
  attestation: the verdict is public, the evidence stays private, with a
  mandatory Devil's Advocate step before any MALICE verdict is allowed.

The pattern across all of them is the same one VIGÍA is built on: the model
can propose, investigate, or narrate; it does not get unilateral authority
over a conclusion that will be relied upon. The new VIGÍA doesn't abandon that
pattern — it's rebuilding the investigation experience *around* an AI
protagonist while keeping that authority boundary intact through Kassandra
and the hallucination guard.

## Related, ongoing research: reward hacking

Separately from VIGÍA itself, I've been researching reward hacking as a
sociotechnical phenomenon in LLM agents — currently written up in Spanish, at
[reward-hacking-social](https://github.com/annatchijova/reward-hacking-social),
with an English write-up in progress. The core question I'm working through:
whether we're actually measuring *how much* reward hacking happens in agentic
systems, or only how much of it we're currently capable of recognizing — and
what that gap implies for any system, including VIGÍA's AI-protagonist
rewrite, that gives a model more latitude over the course of an
investigation. I've already tested mitigation techniques informally; this
research line is where I'm validating them properly, and it directly informs
how much latitude the new VIGÍA agent architecture should actually give the
model.

## Why the funding matters

The deterministic core, the bug registry discipline, and the integrity
mechanisms above weren't built in a weekend, and the AI-protagonist rewrite
described here — a real agent architecture, not a relabeled README — isn't
either. What I'm asking Mozilla to fund is exactly the gap between "the
direction is named and the integrity mechanisms already exist" and "the
agent architecture is built, tested through red-team rounds the way FRACTURE
was, and documented with the same discipline." That gap is real engineering
work, and it's the same standard of rigor — abductive method, adversarial
self-audit, a public bug registry, no claim without a reproducible check —
that produced FRACTURE in the first place.

---

*This document is maintained alongside the rewrite it describes. Where it
says something is unfinished or unverified, check the dated commit history
and [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) before assuming it still
is.*
