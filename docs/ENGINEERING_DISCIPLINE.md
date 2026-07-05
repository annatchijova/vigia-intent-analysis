# CLAUDE.md — Engineering Discipline for AI-Assisted Repository Work

> **Scope of this file.** This is the *development-discipline* guide for any agent
> (Claude Code, Ollama-backed, or otherwise) that has write access to this
> repository. It governs *how work is done here* — reasoning, git hygiene, editing,
> verification. It is deliberately generic and portable across repositories.
>
> It is **not** the runtime manual of any deployed agent. If this repo also ships an
> operational agent manual (e.g. `docs/*_AGENT_MANUAL.md`), that file governs the
> agent's investigative behavior; this file governs the engineer working *on* the code.
> When both exist, do not conflate them.

---

## 0. Working agreement

- **Chat vs. repo language.** Conversation with the maintainer is in Rioplatense
  Spanish (voseo, professional, neutral). Everything committed to the repo — code,
  tests, comments, docstrings, documentation, and commit messages — is in English.
- **No emojis** anywhere in the repository or in generated output.
- **Commit prefix.** Post-hackathon work is committed with the fixed prefix
  `POST HACKATHON` so automated contributions are filterable in `git log`. Keep the
  prefix consistent; provenance is the point.
- **You do not know the repo state until you have read it.** Do not assume paths,
  branch, cleanliness, dependency versions, or that a project-knowledge snapshot
  matches the live tree. Verify, then claim. See §3.

---

## 1. Reasoning method — abduction and the Peircean triad

Engineering here is treated as forensic inference, not pattern-matching. Every
diagnosis, bug hunt, integration decision, and code review passes through the same
disciplined loop. The goal is not to produce *an* explanation quickly; it is to
produce the explanation that survives an attempt to refute it.

### 1.1 The semiotic triad — observation discipline

Before proposing any cause or change, describe the situation through Peirce's three
layers, in order. Do not collapse them.

- **Firstness — "What do I observe?"**
  Pure phenomenological description of the symptom, stripped of interpretation.
  The exact error text, the failing assertion, the diff in behavior, the stack trace,
  the byte-level artifact. No hypothesis yet. Precise technical language only.
  > *Example:* "Test `test_seal_determinism` fails: two runs of the same input produce
  > digests `a3f…` and `9c1…`. The divergence is in the `posterior` field."

- **Secondness — "Is this consistent with its expected context?"**
  The observation in relation to a baseline. An anomaly only exists against a norm.
  State what "correct" looks like and how this deviates. If you cannot state the
  baseline, you do not yet understand the bug — find the baseline first.
  > *Example:* "A sealed result must be bit-for-bit identical across runs by design.
  > A per-run difference in one field means non-determinism entered the decision path.
  > This is a contract violation, not flakiness."

- **Thirdness — "What general rule produces this pattern?"**
  The inferred law: the root cause as a repeatable category, not a one-off patch.
  What class of defect systematically produces this signature?
  > *Example:* "A `float` reached the sealed payload. Float summation is
  > ordering- and platform-dependent, so the digest cannot be stable. The rule:
  > any float in the decision path is a determinism defect regardless of how small."

### 1.2 The inference loop — abduction → deduction → induction

Peirce's actual scientific method. Run it explicitly; name the step you are on.

1. **Abduction (hypothesis).** Generate the *best plausible* explanation of the
   Firstness/Secondness evidence — inference to the best explanation, not proof.
   Prefer the simplest hypothesis that accounts for *all* observed anomalies.
2. **Deduction (prediction).** If the hypothesis were true, what else must be true?
   Derive a concrete, checkable consequence. A hypothesis with no testable
   consequence is not yet an engineering hypothesis.
3. **Induction (test).** Run the check against the live system. Confirm or refute.
   Update the hypothesis. Log the check regardless of outcome.

A cause is not "found" until a deduced prediction has been inductively confirmed
against the real code or a real run. A plausible story is a candidate, not a verdict.

### 1.3 Mandatory refutation — Eco's razor against overinterpretation

Before acting on any non-trivial hypothesis — and *always* before a change framed as a
"fix" — attempt to refute it.

- **Formulate the benign / simpler hypothesis.** Assume the boring explanation:
  it already works and you misread it; the guard is three lines up; the "wrong"
  default is intentional and documented; the failure is environmental, not a code bug.
  Build the strongest version of that innocent explanation.
- **Test it against the full evidence.** Does the simpler explanation account for
  *every* anomaly without contradiction? If yes — stop, you were about to fix a
  non-bug. If no — the deliberate/real-defect explanation survives; proceed.
- **A refuted hypothesis is a real, valuable outcome.** "I looked, and the reported
  bug is not present — the caller already validates this" is a result, not a failure
  to act. Evidence that is *too clean* (a symptom that fits your first guess too
  perfectly) is itself a signal to look harder, not to relax.

---

## 2. Session protocol — git discipline

An agent with write access is fast, occasionally wrong, and feels no loss when work
disappears. The human pays for a scrambled history. These rules are cheap insurance.

- **Tag a restore point before every session.** Before touching anything:
  ```bash
  git tag -a "pre-session-$(date +%Y%m%d-%H%M%S)" -m "restore point before AI session"
  ```
  Recovery is then one command: `git reset --hard <tag>`.

- **Forbidden operations.** `git rebase`, interactive rebase / `git squash`, and
  `git push --force` (including `--force-with-lease`) are prohibited in any agent
  session. They rewrite history and generate unrecoverable loss. Only forward-only
  operations are allowed: `commit`, `merge`, `revert` — they change history by
  *adding* to it, which is always recoverable. If history genuinely needs cleaning,
  a human does it deliberately, outside the agent loop.

- **Verify state before you claim it.** Never report repo state from memory or a
  stale snapshot. Before saying "committed", "pushed", or "on branch X":
  ```bash
  git status --short
  git log --oneline -n 10
  git branch --show-current
  ```
  Report what the output actually says. A confident, wrong status report ("it's
  committed and pushed" when it is staged and local) is exactly the failure to avoid.

---

## 3. Verification-first workflow

- **Propose → wait for output → act.** Do not run speculative multi-turn diagnostic
  loops. Propose one focused command, wait for its real output, then act on the
  evidence. Empirical state beats remembered state, every time.
- **Ask for terminal output before assuming.** When repo state, file content, or an
  environment fact matters, request the exact command output rather than guessing.
- **Command routing.** Investigation, multi-step, or uncertain tasks go to a Claude
  Code prompt. Already-determined terminal commands are handed to the maintainer as
  copy-pasteable lines — do not route a known command through Claude Code; it wastes
  tokens.

---

## 4. Editing discipline

### 4.1 Audit before patch — the finding is a claim, not a fact

Applies to every problem reported by someone other than yourself reading the live
file: a human reviewer, another AI auditor, a linter, a security scan, a handed-over
diff. Auditor findings may be binding — *but only after empirical verification against
the actual current file.*

1. **Read the live file, fully, around the claim** — not the snapshot the auditor saw,
   not your memory. The current bytes on disk, with surrounding context.
2. **Confirm the cited anchor exists** where claimed. Absent → the finding is stale or
   imagined; stop, do not patch. Present in several places → resolve which before
   touching any.
3. **Confirm the bug is real *in this code*.** Check there is not already a guard, that
   the "missing validation" is not done by the caller, that the "wrong default" is not
   intentional and documented. This is where most false positives die.
4. **Reject false positives explicitly**, with the reason ("guard already present on
   line N", "anchor not found in live file", "default intentional per docstring").

The more authoritative and specific the finding sounds, the more deliberately it gets
checked — confident, precise findings are the ones that get applied blind.

### 4.2 Surgical patching — never rewrite what you can patch

Regenerating a file from memory is the single largest source of silent regressions:
the model reproduces 95% correctly and quietly drops a function or flips a default.
Every edit to existing content obeys five invariants:

1. **Anchor on an exact, unique string.** The anchor must occur in the live file
   exactly once. `0` → stale, abort. `>1` → ambiguous, lengthen it until unique.
   Never "apply to the first match".
2. **Dry-run first, always.** Default to *not* writing. Opt into mutation explicitly
   (`--apply`). Read the diff before anything touches disk.
3. **Back up before you write** (`<file>.bak` or timestamped). A patch you cannot undo
   in one command is a patch you should not apply.
4. **Verify after you write.** Parse `.py` with `ast`, load `.json`, and at minimum
   confirm the anchor is gone and the file is non-empty. On failure, restore the
   backup and report.
5. **Re-read immediately before patching.** Anchors go stale the moment anything else
   edits the file. After one patch, re-read before the next.

Do **not** overwrite a repo file from a project-knowledge snapshot or a cached copy —
the snapshot is almost always behind the live file and the overwrite silently reverts
whatever changed in between. Patch the live file; do not replace it. (Creating a
brand-new file is not a patch — write it directly.)

---

## 5. Architectural invariants for consequential outputs

These apply to any code path that produces a verdict, score, classification, risk
number, or result that becomes evidence or triggers an action.

### 5.1 LLM out of the decision path

A language model can read the evidence correctly and still reach the wrong conclusion
under narrative pressure. Therefore the LLM **never touches the decision path.**

- The deterministic engine produces and **seals** the result *before* any LLM is
  called. The model cannot influence a value that was already fixed.
- The model receives a **compressed, read-only summary**, not the full internal state.
- The prompt states explicitly that the figures are fixed and must not be altered; the
  model's only job is to put them into words.
- The narrative is stored **beside** the seal, never inside it, so a verifier can
  confirm the result without trusting the prose.
- **Test:** swapping the narrator backend (Ollama ↔ hosted API) must change only the
  wording — never the verdict, seal, or chain of custody. If it can change the outcome,
  the narrator is in the decision path and the architecture is wrong.

### 5.2 Deterministic core

The decision path must be reproducible bit-for-bit and tamper-evident.

- **No float in the decision path.** Use `fractions.Fraction` for ratios, weights, and
  accumulations; integers for genuine counts. Floats are allowed only in the cosmetic
  narrative layer (display rounding, charts), never in a value that gets sealed.
- **Canonical, typed, versioned serialization.** One canonical encoder, used
  everywhere: type-tagged (so `1`, `"1"`, `1.0`, `True` are distinguishable — check
  `bool` before `int`), recursively key-sorted, and stamped with a
  `CANONICALIZE_VERSION`. Divergent ad-hoc encoders are how one input gets two hashes.
- **Seal with SHA-256 over the canonical bytes**, storing the digest, the version, and
  chain-of-custody metadata (inputs, tool versions, timestamp recorded *outside* the
  sealed payload). The verifier is stdlib-only and independent of the producing code.
- **Prove it.** Produce the result at least twice and assert the seals match; better,
  re-order inputs and run in a fresh process. Common leaks: a stray float, `set`/`dict`
  ordering, an unpinned timestamp or RNG seed, `PYTHONHASHSEED` randomization,
  locale-dependent formatting.

### 5.3 Honest degradation

When correctness cannot be guaranteed, never emit a result that looks correct.

- **A reconstructed value is not the real value — flag it** (`requires_rebuild = True`)
  and have downstream validity checks honor the flag.
- **Three states, not two:** PASS / WARN / FAIL. A best-effort guarantee that a given
  environment did not confirm is a WARN, not a silent PASS. A failed child step must
  never be folded into PASS because a parent ignored its exit code.
- **Name the guarantee level** in the schema, docstring, and any header
  (`"determinism_level": "best_effort"`), so other code can read the honest claim.
- **Warn at the boundary** where degradation enters (the legacy load, the dtype
  coercion), the moment it happens — the caller can only decide if they were told.
- **An absent optional component degrades the feature, never the core** — disable it,
  log the absence once, keep the core path working.
- **A non-critical failure must not destroy valid work** — a persistence error must not
  discard a correctly computed in-memory result; warn and return it.
- **`ABSTAIN` is a valid verdict.** A documented limitation is an asset (the Daubert
  posture): a known WARN is worth more than a false PASS. Honest, scope-bounded claims
  beat impressive metrics.

---

## 6. Multi-AI adversarial audit

Design decisions and non-trivial patches are routed through an independent auditor
model before implementation, to counter confirmation bias. Roles are distinct
(implementer, adversarial auditor, secondary review). Auditor findings are treated as
**binding — but only after empirical verification against the live code** (§4.1). The
implementer is the last line that can catch a confident-but-wrong finding before it
lands; that check is not optional politeness.

---

## 7. Definition of done — pre-commit checklist

Before proposing a commit, confirm:

- [ ] The change was derived from the abductive loop, and the refuting hypothesis was
      tested (§1.3), not skipped.
- [ ] Every applied finding was verified against the live file (§4.1).
- [ ] The edit was a surgical, anchored, backed-up, verified patch — not a rewrite
      (§4.2).
- [ ] No float entered any sealed/decision path; determinism check passes (§5.2).
- [ ] The LLM did not influence any sealed value (§5.1).
- [ ] Limitations, WARNs, and gaps are documented, not hidden (§5.3).
- [ ] Tests run and their real output was read (not assumed).
- [ ] `git status` / `git log` reflect what will actually be committed (§2).
- [ ] Commit message is in English, prefixed `POST HACKATHON`, and describes *why*.

---

## 8. What NOT to do

- Do not claim repo state, test results, or "it's fixed" without having read the real
  output.
- Do not rewrite a file you could have patched; do not overwrite the live file from a
  snapshot.
- Do not apply an auditor's finding without verifying it against the live file first.
- Do not `rebase`, `squash`, or `force-push` in an agent session.
- Do not put a float, an LLM decision, or an unversioned encoder in a sealed path.
- Do not report a uniform green that cannot distinguish "verified correct" from "ran
  without crashing".
- Do not guess when you can check. When in doubt, ask for the command output.

---

*Reasoning is forensic: observe (Firstness), contrast (Secondness), infer the law*
*(Thirdness); abduce, deduce, induce; and refute before you commit.*
