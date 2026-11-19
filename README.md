# VIGÍA — AI-Assisted Forensic Investigation Companion

[English](./README.md) · [Español](./README_ES.md) · [FRACTURE (the original VIGÍA)](https://github.com/annatchijova/fracture) · Author: Anna Tchijova · License: Apache 2.0

**Index:** [What changed and why](#what-changed-and-why) · [What the new VIGÍA is](#what-the-new-vigía-is) · [Kassandra Protocol & Hallucination Guard](#kassandra-protocol--hallucination-guard) · [Reproduce it yourself](#reproduce-it-yourself) · [Quality signal: the bug registry](#quality-signal-the-bug-registry) · [MCP, API and the ecosystem](#mcp-api-and-the-ecosystem) · [Cronos MCP](#cronos-mcp) · [Roadmap](#roadmap) · [Scientific rigor](#scientific-rigor) · [For Mozilla](#for-mozilla)

---

## What changed and why

**This is not a new project replacing an old one. It's the same project, split
in two, under two names.**

The system that used to be VIGÍA — a deterministic forensic-intent engine where
the LLM is deliberately locked out of the verdict path, built for advanced
researchers under critical-threat, judicial-grade, low-Daubert-tolerance
conditions — did not stop existing. It kept its full codebase, its 102,000+
lines of production Python, its 617 sealed bundles, its 11 red-team rounds, and
its active maintenance commitment, under a new name: **FRACTURE**
([github.com/annatchijova/fracture](https://github.com/annatchijova/fracture)).
Its original README is preserved at
[`docs/README_FRACTURE_LEGACY_EN.md`](./docs/README_FRACTURE_LEGACY_EN.md)
([ES](./docs/README_FRACTURE_LEGACY_ES.md)) exactly as it was, so nothing about
that work is lost or rewritten.

**This repository (`vigia-intent-analysis`) becomes the new VIGÍA.**

I'm an independent AI/security researcher. I applied to Mozilla with VIGÍA as
my submission. Mozilla's program asks for AI to be the protagonist of the
work — and the VIGÍA that existed was architected around the opposite
principle: the LLM never decides, it only narrates after a deterministic
engine has already sealed the verdict. That is a deliberate, documented,
load-bearing design choice for a Daubert-admissible forensic tool, and I'm not
walking it back by pretending otherwise.

What I told Mozilla is true: VIGÍA exists, and I'm rewriting it so the AI is a
genuine protagonist throughout the investigation — not retrofitting a label
onto the old engine. That rewrite is what this repository now is, and it is
what the funding is for. The full, detailed account of this decision — the
ecosystem it sits in, the honesty constraints I set for myself, and where the
two systems diverge — is in [`docs/MOZILLA_PROPOSAL_EN.md`](./docs/MOZILLA_PROPOSAL_EN.md).

---

## What the new VIGÍA is

An AI-assisted forensic *investigation companion*, end to end — for expert
witnesses (peritos), cybersecurity practitioners, and DFIR investigators who
want an agent that accompanies the whole process, not a black box that only
answers "what happened." Where FRACTURE excludes the LLM from the decision by
design, the new VIGÍA puts it to work across the investigation itself:
proposing hypotheses, driving tool use, and narrating findings — while the
integrity mechanisms below (Kassandra, the hallucination guard) keep that
narration honest and keep adversarial evidence from steering it.

This is an active rewrite, not a finished product. The sections below
distinguish clearly between what already runs today and what is direction,
not delivery.

---

## Kassandra Protocol & Hallucination Guard

Two integrity mechanisms already exist in this codebase, carried over from
FRACTURE and central to why an AI-protagonist VIGÍA can still be trusted. Each
is attributed here to the file that actually implements it:

**Kassandra Protocol** — [`vigia/vigia_sift_bridge.py`](https://github.com/annatchijova/vigia-intent-analysis/blob/main/vigia/vigia_sift_bridge.py)
(`_derive_session_nonce`, `_generate_active_tripwire`, `_process_llm_verdict`).
A semantic tripwire I built because VIGÍA is open source — an attacker can
read all the code and craft evidence specifically to manipulate the LLM
layer. The mechanism is public; the value it protects each session is not.
At the start of an analysis, VIGÍA takes the SHA-256 of the evidence and, with
a secret `KASSANDRA_SALT`, derives a session nonce via HMAC-SHA256. From that
nonce it generates dynamic delimiters for the evidence and a secret
identifier — `PROTOCOLO_KASSANDRA_<hash>` — that acts as a semantic canary:
the LLM is told about it, the evidence should never know about it. If
evidence content tries to mention, reproduce, or impersonate an instruction
containing that identifier, that's a signal that something is trying to cross
the data→instructions boundary. VIGÍA doesn't just trust the model saying "I
detected Kassandra": it externally verifies the returned `tripwire_id` against
the expected contract. A wrong ID or an inconsistent response is logged as
`KASSANDRA_PROTOCOL_VIOLATION` / `INTEGRITY_UNKNOWN`.

Kassandra doesn't prove an attacker exists, and it doesn't turn an anomaly
into a forensic conclusion on its own — it's a semantic-integrity defense for
the channel to the LLM, mainly against prompt injection and evidence
manipulation. And it has a deliberately explicit limitation: without a secret
`KASSANDRA_SALT` configured, the fallback is a public salt
(`VIGIA_FALLBACK_SALT_NO_PRODUCTION`) — an attacker who knows the evidence can
precompute the values, and VIGÍA only logs a warning
(`KASSANDRA_SALT_MISSING`). For environments where that guarantee matters,
`VIGIA_ENFORCE_KASSANDRA_SALT=true` makes it fail **closed**: VIGÍA refuses to
start at all without a secret salt configured.

**Hallucination Guard** — [`vigia/llm/hallucination_guard.py`](https://github.com/annatchijova/vigia-intent-analysis/blob/main/vigia/llm/hallucination_guard.py).
A separate mechanism: it checks the LLM's narration — verdict, score,
fracture type, MITRE TTPs, hashes — against an `AuthorizedFact` set extracted
directly from the deterministic motor's output, comparing with `Decimal`/
`Fraction`, never floats, and redacts any claim the model makes that isn't
backed by that authorized set. Kassandra defends the evidence→LLM boundary;
the hallucination guard defends the LLM→report boundary. Together they're the
reason I feel comfortable letting the LLM be a protagonist here instead of
locking it out entirely, as FRACTURE does.

This is not a finished, audited claim that the new architecture is safe — it's
early, actively being redesigned (see [Roadmap](#roadmap)), and I'm not going
to pretend otherwise for a grant application.

---

## Reproduce it yourself

I'm not asking anyone to take the numbers on faith. The deterministic core
this repository inherited from FRACTURE is still here and still verifiable —
and I want to be precise about which number belongs to which mode, because
conflating them is itself a form of overclaiming:

- **Python-only agent, 0 LLM calls (Domain B)** — **158/162 (97.5%)**
  label-blind on the detection corpus; **187/199 (94.0%)** on the mixed
  corpus (including 16 adversarial BREAK cases, 7 KIWI, 3 false negatives, 5
  false positives). This is the deterministic scorer running alone, without
  the agent's reasoning layer.
- **Claude Code / MCP, LLM-assisted investigation (Domain A)** — **100% of
  verdicts correct on every investigation run to date**, evaluated per case,
  not as a corpus-wide figure. This is the mode the AI-protagonist rewrite
  actually builds on. If a case's signal falls into something VIGÍA doesn't
  contemplate, the architecture is designed to degrade to `ABSTAIN` rather
  than guess — which, left unconfirmed, could later turn out to be a false
  negative. We have not yet found such a case. That is not a guarantee one
  doesn't exist; it is an honest statement of what has and hasn't been
  checked so far.
- Full per-domain methodology and breakdown in
  [`docs/ACCURACY.md`](./docs/ACCURACY.md).
- Real cases from **Digital Corpora** (M57-Jean, Nitroba, Lone Wolf, Tuck 2019)
  and NPS datasets, documented in
  [`docs/digital_corpora_complete_report.md`](./docs/digital_corpora_complete_report.md).
- VIGÍA's own adversarial corpus — the BREAK, KIWI, false-positive and
  false-negative cases built specifically to try to break the system — lives
  in this repository today under `data/cases/` and is being consolidated
  into its own top-level folder, `CORPUS-CASES/`, so it stays easy to find
  and run independently of everything else here.
- Pick any sealed case and verify it bit-for-bit, independently of VIGÍA's own
  code:
  ```bash
  python3 forensics/verify_ebs_v1.py results/<case>_bundle.json --verbose
  python3 show_4_hashes.py results/<case>_bundle.json
  ```
  `show_4_hashes.py` prints the four forensic hashes (graph, bundle, HMAC
  audit chain, independent EBS re-verification) for a sealed case. I'm
  deliberately not quoting a specific "N hashes match, one doesn't" result
  here until I've re-verified that exact claim across a fresh run — see
  [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) for what's confirmed versus
  what's still being checked. Report anything that doesn't reproduce.

---

## Quality signal: the bug registry

I don't erase my own bugs. The full history — 11 red-team rounds, invariant
violations, found and fixed — is in
[`BUGS_HISTORICO_EN.md`](./BUGS_HISTORICO_EN.md). A few of the uglier, more
twisted ones, so this doesn't read as a claim without receipts:

- **[B-150](./BUGS_HISTORICO_EN.md)** — `_parse_iso_timestamp` silently
  interpreted timezone-naive timestamps in the *host machine's local
  timezone*: the same evidence could produce a different verdict and hash
  depending on which examiner's OS clock settings ran the analysis.
- **[B-239](./BUGS_HISTORICO_EN.md)** — `bool` is a subclass of `int` in
  Python. Two parallel copies of the same `Fraction` predicate disagreed
  because one accepted booleans as valid numeric input and the other didn't.
- **[B-218](./BUGS_HISTORICO_EN.md)** — the sealed bundle recorded
  `epsilon_used = epsilon_accept` even on cases where the real decision was
  REJECT via `epsilon_reject` — the audited parameter wasn't the one that
  actually decided the case.
- **[B-215](./BUGS_HISTORICO_EN.md)** — `evidence_graph` was never populated
  in `run_full` bundles, so `graph_hash` was identical across *every* case: a
  cryptographic integrity anchor that looked real and carried zero actual
  information.
- **[B-234](./BUGS_HISTORICO_EN.md)** — nothing ever verified that a reasoning
  trace was actually paired with the sealed bundle it claimed to accompany —
  two artifacts presented as linked, with no check enforcing the link.

All five are marked `RESOLVED` in the registry — the point isn't that the bugs
existed, it's that they're documented instead of quietly disappearing.

---

## MCP, API and the ecosystem

VIGÍA is already usable via MCP (`launch_vigia_mcp.sh`, 22 forensic tools —
see [`CLAUDE.md`](./CLAUDE.md)) and via a FastAPI wrapper. Both are being
actively reworked for the AI-protagonist focus described above. The direction
I'm pulling from: the multi-agent orchestration and telemetry design in
[annaconda](https://github.com/annatchijova/annaconda) and
[zaynor](https://github.com/annatchijova/zaynor), and the broader
[krakadyl](https://github.com/annatchijova/krakadyl) ecosystem — this is where
I want the new VIGÍA's agent architecture to converge, not where it already
is today.

Whether the deterministic Mode 1 engine stays directly reachable from this
repository, or lives purely under FRACTURE going forward, is an open design
question I'm still working through — noted here rather than decided
prematurely.

---

## Cronos MCP

[Cronos](https://github.com/annatchijova/cronos) is a separate MCP server I
built as a black-box recorder for agents: it captures tool calls, retrieved
memories, hypotheses considered and discarded, evidence, and decisions as
they happen, and seals the resulting trace in a SHA-256 hash chain. It
already runs alongside VIGÍA's Claude Code investigations today — this
repository carries dozens of `cronos_*.md` trace files from past sessions as
proof, not a promise.

It matters more now, not less, as the AI becomes a protagonist instead of a
narrator called once at the end. A sealed verdict tells you *what* was
decided; it says nothing about the path the agent actually took to get
there — which hypotheses it floated and dropped, which tool calls it made
and in what order, where it changed its mind. Cronos is the independent,
tamper-evident record of that path, kept separate from the verdict the same
way Kassandra and the hallucination guard are kept separate from the LLM's
narration: none of them trust the agent's own summary of itself.

---

## Roadmap

Explicitly future work, not shipped:

- UI adapted for a wider range of users, including neurodivergent people —
  not yet built.
- Reworked MCP/API surface aligned with the annaconda/zaynor/krakadyl
  multi-agent and telemetry model above.
- Folder and repository restructuring to reflect the VIGÍA/FRACTURE split
  cleanly (planned separately from this documentation pass).

---

## Scientific rigor

Splitting into two names doesn't mean splitting from the standard. Both
**VIGÍA** and **FRACTURE** ship as proper GitHub packages, under the same
Apache 2.0 license, with their own test suites and bug registries. I'm also
formalizing (currently in Spanish, English write-up in progress) ongoing
research into reward hacking as a sociotechnical phenomenon in LLM agents at
[reward-hacking-social](https://github.com/annatchijova/reward-hacking-social) —
mitigation techniques I've already tested informally and now want to
validate properly. I'm naming it here deliberately, not as an incoherent
flex for a project that's about to give an LLM more latitude: it's the
opposite, an attempt to actually reduce that risk before leaning on the
model more. I already have working hypotheses for orchestrating multiple
agents in a way that reduces error rather than compounding it, and that's
part of what informs how much latitude the new VIGÍA architecture gives the
model, and where Kassandra, the hallucination guard, and Cronos sit in that
design.

---

## For Mozilla

I submitted the Mozilla application describing VIGÍA as it existed at the
time, and committed to rewriting it so AI would be the protagonist of the
work — this repository, starting from this documentation pass, is that
rewrite in progress, and the funding is what makes finishing it possible. The
full, unabridged account — the ecosystem this sits in, what's confirmed versus
still being verified, and the honest difference between VIGÍA and FRACTURE —
is in [`docs/MOZILLA_PROPOSAL_EN.md`](./docs/MOZILLA_PROPOSAL_EN.md).

---

## License

Apache 2.0 — see [`LICENSE`](./LICENSE).
Copyright (c) 2026 Anna Tchijova and the VIGÍA AI Collective.
