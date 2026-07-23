# Security & Integrity Audit — zone38 (formerly `slopguard`)

**Date:** 2026-07-23
**Method:** Abductive Engineering (abduction → deduction → induction) + Red-Team Auditing
**Target:** `github.com/semanticRig/zone38` @ `60f42e2` (full history unshallowed; 110 commits)
**Runtime:** Node v20.20.2. FORGE self-audit fingerprint `1e49a17f9eecfaf2`.
**Scope:** Static reading of the decision path + end-to-end induction against the real CLI. Read-only: zero writes to the target across all runs (`git status --short` clean throughout).
**Reproducible evidence:** `poc-inv4.js`, `poc-inv4-e2e.js`, `poc-inv8-sweep.js`, `poc-minified-bypass.js` (kept in the working scratchpad).

---

## Threat model

- **Attacker CAN:** control the content of a JS/TS file that zone38 scans in CI (a PR author, or anyone trying to hide a secret from the scanner).
- **Attacker CANNOT:** modify zone38's source, its thresholds, or the CI configuration.
- **Question under test:** can a real secret pass the CI gate without zone38 blocking it, and does zone38 deliver on its headline claim (detect AI-generated code by mathematical structure)?

## Epistemic legend

`CODE FACT` (observed in source) · `PLAUSIBLE HYPOTHESIS` (abduction, not executed) · `CONFIRMED BY INDUCTION` (prediction executed, held) · `FALSIFIED` (prediction executed, failed) · `CONFIRMED BY EVIDENCE` (external artifact, e.g. git history).

---

## Executive summary

| ID | Severity | Level | Finding |
|----|----------|-------|---------|
| INV-9 | **HIGH** | CONFIRMED BY INDUCTION | "Minified-skip" optimization disables the entire entropy pipeline → total secret-detection bypass |
| INV-4 | Medium | CONFIRMED BY INDUCTION | Purely representational change (hex vs base64) flips the CI decision in a density window |
| INV-8 | Medium | CONFIRMED BY INDUCTION | A single detected secret does not fail CI; axis B saturates at ~45 |
| INV-2 | Medium | CONFIRMED BY INDUCTION | Real confirmation gate ≠ the model the README describes (documentation integrity) |
| INV-10 | Medium | CONFIRMED BY EVIDENCE | The AI-slop detector was itself AI-agent-built; its thesis is refuted by its own case |
| INV-11 | Medium | CONFIRMED BY INDUCTION | "Clean" verdict emitted over 0 analyzed files (false PASS / broken honest-degradation) |
| INV-1 | Low | CODE FACT | Namesake threshold (IC 0.038) is not the operative one (code gates at 0.045) |
| INV-3 | Low-Med | CODE FACT | Short strings structurally suppressed by design |
| INV-6 | Low-Med | CODE FACT | Axis C (Quality) can never block CI at default thresholds |
| INV-5 | — | PLAUSIBLE HYPOTHESIS | Cross-Node-version determinism (not executed; only Node 20 available) |
| INV-7 | — | PLAUSIBLE HYPOTHESIS | `--since` with empty scope passes green (not executed) |

---

## Findings

### INV-9 — "Minified-skip" is a total detection bypass  ·  HIGH  ·  vulnerability

- **CODE FACT:** `runner.js:81-88` — if `record.surface.minified` is true, the entire L05–L08 candidate pipeline is skipped: `record.findings = []`, `record.review = []`. Only URL analysis (L09) and regex rules (L10) run. `L02-surface.js:120-121`: `minified = (1 line && length > 500) || (<=10 lines && avgLineLength >= 200)`.
- **Abduction:** the skip exists to suppress false positives from bundled/minified files. Composed with regex-blind naming (which the README itself admits defeats regex), it becomes a detection hole.
- **Deduction (stated before result):** 25 base64 secrets with regex-blind names `d0..d24` that fail CI (exit 1) in a normal file will pass (exit 0) when concatenated onto a single line.
- **Induction (`poc-minified-bypass.js`):**
  - NORMAL (29 lines): `minified=false`, 25 secrets reported, axis B = 45, **exit 1**.
  - MINIFIED (1 line, avgLineLen 1478): `minified=true`, **0 secrets reported**, axis B = 0, **exit 0**.
- **Causal chain:** one long line → `minified=true` → runner zeroes findings → entropy pipeline skipped → regex-blind names → L10 empty → `secrets=0`, `exit 0`.
- **Note:** on a minified file zone38's secret detection collapses to regex-only — i.e. it degrades into exactly the "regex-based scanner" its README mocks. Real minifiers rename variables to short tokens, so secrets in a genuine minified bundle are doubly invisible.

### INV-4 — Representational evasion flips the CI decision (density window)  ·  Medium  ·  vulnerability

- **Hypothesis (neutral):** two representations of the same secret bytes produce a different CI decision.
- **Induction (`poc-inv4.js`, `poc-inv4-e2e.js`, `poc-inv8-sweep.js`):** for identical 32-byte secrets, hex vs base64/base32 materially change every signal. `icSignal` is deterministically 0 for hex (16-symbol alphabet → IC ≈ 0.064 > the 0.045 gate) and 1 for base64/base32. hex is **not** fully suppressed (yield ~72% of secrets still confirmed via CTF+another signal — this **corrects** an earlier 2-sample estimate of "hex always drops to review"). Effect on CI: with regex-blind names, base64 crosses B>25 at N≈15, hex at N≈25; in the window **N ∈ [15,24], base64 → exit 1 while hex → exit 0** (same bytes, opposite CI decision).
- **Scope (honest):** existence result, not a universal bypass; the flip only occurs inside the density window.
- **Collateral (strengthens INV-2):** NCD anti-correlates with the verdict — hex has the highest NCD (0.899, "most alien") yet the weakest verdict, and NCD is not counted by the gate at all.

### INV-8 — Detection is not blocking; the security axis saturates low  ·  Medium

- **CODE FACT:** `L13` axis B = `0.45·findings + 0.25·patterns + 0.20·urls + 0.10·compression`, each sub-score capped at 100. `DEFAULT_THRESHOLDS.B = 25`.
- **Induction:** a single detected hardcoded secret yields axis B ≈ 10.6 (with the regex firing) — reported (`secrets=1`) but **exit 0**. The gate is crossed only at ~15 base64 / ~25 hex secrets in one file; axis B **saturates at ~45** even with 100 secrets (findings capped). Detection ≠ blocking: the default gate tolerates a detected secret.

### INV-2 — The decision model differs from the README  ·  Medium  ·  documentation integrity

- **Claim:** "all three [Shannon, IC, NCD] must agree… only strings that fail all three thresholds simultaneously are confirmed."
- **CODE FACT:** the real gate is `L08.arbitrate` — `HIGH: effectivePipeline ≥ 0.65 AND ≥2 of {icSignal, ctfSignal, egsSpike, uniformity}`; `MEDIUM: ≥ 0.50 AND ≥2`. NCD is **not** among the four counted signals.
- **Induction:** `secret#2` in hex is confirmed MEDIUM with `icSignal = 0` — a secret confirmed **without** the IC signal, refuting "all three must agree." The user's mental model built from the README does not match the implementation.

### INV-10 — The AI-slop detector is AI-agent-built; its thesis refutes itself  ·  Medium  ·  CONFIRMED BY EVIDENCE

- **Tool's self-verdict (worthless as evidence):** scanning itself yields axis A = 9.2 "Minimal" (clears itself), while reporting 98 "secrets" at exit 0. Same weak detector as INV-1…9.
- **Objective git evidence:** the project was originally `slopguard`; **110 commits over 5 weeks** (2026-04-07 → 05-13), single author `cloakedcpu@proton.me`, `feature/phase-N` branches. History contains **`CLAUDE.md`** (Claude Code project instructions) and **`planner.instructions.md`** (an agent planner: "building slopguard from scratch… phased, branch-based… explicit user approval… reply 'merge and next'"). `.gitignore` scrubs `CLAUDE.md`, `PHASES.md`, `planner.instructions.md`, `solution/`, `solutionV2/` from the published tree.
- **Level:** `CONFIRMED BY EVIDENCE` that AI coding agents were used (human-directed, phase-gated). The crude "written 100% by AI in one shot" framing is `FALSIFIED` by the 110-commit cadence.
- **Methodological punchline:** the decisive evidence of AI authorship lives in git history and gitignored planning files — **outside** the `.js` the tool scans. zone38's core thesis (detect AI origin from code texture) is refuted by its own case: the ground truth was procedural/historical, not textural.

### INV-10b — zone38 does not measure authorship (it is not stylometry)  ·  CODE FACT + CONFIRMED

- **CODE FACT:** 39 rules are per-line regex (`test(line, ctx)`); **no AST/parser** anywhere (no acorn/esprima/babel). Rules do **not** grep for assistant names (no claude/copilot/gpt/cursor). Axis A = 0.40 compression (NCD vs `corpus/{ai,human}.js.gz`, two reference files) + 0.35 regex smells + 0.25 entropy. No per-author model, no function-word or n-gram analysis, no Burrows's Delta.
- **Induction:** AI-assisted repos (janus, phylo, forge-nuevo) all score "Minimal"; Python-only repos are not read at all.
- **Verdict:** zone38 is a regex code-smell linter + a compression-texture heuristic marketed as cryptanalysis. It cannot answer "who wrote this" — it lacks the machinery. Real stylometry (function words, n-grams, parsed syntax, per-author models) is a different discipline.

### INV-11 — "Clean" emitted over 0 analyzed files  ·  Medium  ·  broken honest-degradation

- **CODE FACT:** `L13._aggregateProject` returns `{A:0,B:0,C:0}` when `perFile.length === 0`. zone38 analyzes JS/TS only; a repo with no JS/TS yields 0 files → axes 0 → verdict "Clean". There is no third `not-analyzed / ABSTAIN` state.
- **Induction:** five Python-only repos (raven-memory, stigmergy, mneme, cronos, corvus) → `analyzed=0`, `A=0 "Clean"`, exit 0. A CI running zone38 on a non-JS project gets an empty green that certifies nothing — absence of a check reported as absence of a problem.

### INV-1 / INV-3 / INV-6 (CODE FACT, lower severity)

- **INV-1 — namesake threshold:** the tagline "Below 0.038, nothing is innocent" and the "Why the Name" section claim IC 0.038 is the operating boundary, but `L07-deep.js:139` gates at `ic < 0.045`; 0.038 is nowhere operative. Two truths: which is correct?
- **INV-3 — short-string suppression:** `compression.js:13` returns null ≤50 chars; `:35` clamps the signal into the twilight band for ≤80; `L08._lengthMultiplier` is 0 at ≤6 and linear to 1.0 at ≥12. Short secrets are structurally hard to confirm.
- **INV-6 — axis C never blocks CI:** `DEFAULT_THRESHOLDS = {A:50, B:25, C:100}`; scores cap at 100; `exitCode` uses strict `>`. A C score of 100 ("Critical" per the README's own band) still exits 0.

### INV-5 / INV-7 — open hypotheses (capped at PLAUSIBLE; not executed)

- **INV-5 — cross-version determinism:** `isSecret` compares a raw float mean to a fixed 0.50, and the pipeline depends on `zlib.gzipSync(level:9).length`; the project's own CI runs Node 16/18/20/22/24. gzip output can differ across zlib versions → boundary flips. Requires two Node versions to confirm (only Node 20 available here). Note: the "worker races break determinism" sub-hypothesis was **FALSIFIED** by reading — `vector.score` is per-value pure and merged by index.
- **INV-7 — `--since` empty scope:** a PR touching no scanned files yields an empty scope → axes 0 → exit 0. Requires a real git PR of renames-only to confirm.

---

## Self-corrections made during the audit (method has teeth)

1. **"There is no AND-gate; everything is a mean"** → **corrected** after reading `L08`: a conjunctive gate *does* exist (`pipeline ∧ 2-of-4`); the real finding is INV-2 (mis-described), not "absent".
2. **"hex secrets always drop to review (bFind=0)"** (2-sample estimate) → **corrected** by the 25-sample sweep: hex yield ≈ 72%, not 0%.
3. **"the repo is a single-commit AI dump"** → **FALSIFIED**: that was an artifact of a `--depth 1` shallow clone; the real history is 110 commits over 5 weeks.

## Discarded (non-exploitable) vectors

| Vector | Result | Why |
|--------|--------|-----|
| Zip-bomb via `gunzipSync` on a scanned file | DISCARDED | `L03:44-49`: `gunzipSync` only touches the shipped `corpus/*.gz`, never attacker input — out of the threat model. The only compression-DoS surface is `gzipSync` on a huge file (CPU) → generic hygiene, not a specific bug. |

## Open hypotheses for a next round (capped at PLAUSIBLE)

- **H-mono — broken monotonicity:** `L13._patternAxisScore` normalizes by `lineCount`, so adding benign lines *lowers* axis B ("more content → less detected risk"). Padding as a dilution weapon.
- **H-uni — Unicode evasion:** the char classifier uses `c>='A'&&c<='Z'` etc.; all non-ASCII falls into the `symbol` bucket; `_entropy` iterates UTF-16 units (surrogate pairs split).
- **H-det — intra-process non-determinism:** `Object.keys(freq)` reorders numeric-like (digit) keys vs insertion order → different float summation order in `Σ p·log2(p)` → possible flip at the `s ≈ 0.50` boundary. Likeliest to be FALSIFIED — and a falsification here is still a result.

---

## Conclusion (calibrated — not "useless")

The precise charge is **claim/mechanism mismatch**, not total uselessness:

- **As an AI-authorship detector:** it fails, and structurally *cannot* succeed — it has no author model and is not stylometry. For that purpose it does not work.
- **As a code-smell linter:** it partially works — the 39 regex rules flag real quality issues (console.log, empty catch, `any`, TODOs) regardless of author.
- **As a secret scanner:** weak — noisy (98–199 false positives on real repos), evadable (INV-4, INV-9), and non-blocking (INV-8).

The deepest defect is epistemic: AI-authorship detection — especially of *AI-assisted* code (mixed human/machine) — is a genuinely hard, near-unsolved problem even for real stylometry. zone38's sin is not failing it; it is **asserting confidence** ("below 0.038, nothing is innocent") with a method (regex + compression texture) that cannot deliver it. The honest posture toward such input is **ABSTAIN**, not a confident "Minimal" — the same PASS/WARN/ABSTAIN discipline it violates in INV-11.

**Bottom line:** as the thing it advertises, it does not work; as what it actually is (a mediocre linter plus a compression heuristic), it works a little and noisily. "Useless — full stop" overstates it; "mis-marketed and weak at its headline claim" is what the evidence supports.
