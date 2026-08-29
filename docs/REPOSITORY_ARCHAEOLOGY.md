# Repository Archaeology — How VIGÍA Came to Exist

> [Versión en español](./REPOSITORY_ARCHAEOLOGY_ES.md) ·
> Companion HTML dossier: [`repository_archaeology.html`](./repository_archaeology.html)

**Date:** 2026-08-29
**Scope:** the whole repository at `claude/archaeologist-architecture-analysis-r48jxg`
(HEAD descends from `4c406ea`, the PR #22 merge).
**Question answered:** not *what the system does* — the technical-state docs cover
that — but *how it came to be shaped this way*: which architectural facts are
deliberate, which are historical accident, which invariants exist only in tests,
which APIs were designed around constraints that no longer exist, and what the
code preserves that nobody would reconstruct from the documentation alone.

**Method.** Every claim below is tagged:

- **[OBS]** — read directly from a cited file/line, commit, or command output.
- **[INF]** — inference from cross-referenced observations; the discriminating
  evidence is named.

Three parallel excavation sweeps were run (verdict path and invariants;
redundant abstractions and fossils; historical narrative from the documents),
and the highest-impact claims from each sweep were independently re-verified
against the live files before inclusion. Where a claim could not be
discriminated, both hypotheses are preserved — per this project's own doctrine
that a refuted or undecidable hypothesis is a result, not a failure
(`docs/ENGINEERING_DISCIPLINE.md` §1.3).

A methodological note: this repository documents its own fossils better than
most repositories document their live code. `attic/README.md`,
`docs/FOSSIL_HUNT_20260711.md`, `docs/CALIBRATION_ARCHAEOLOGY_20260723.md`,
`docs/B123_EXCAVATION_20260723.md` and the 11,000-line bug ledger are primary
sources written by the project about itself. This report cross-examines them
against the code rather than repeating them.

---

## 1. Formation history: the strata

### 1.1 Three git resets — the history is younger than the project

**[OBS]** This repository's git history contains 125 commits spanning
2026-07-21 → 2026-08-28, with **three independent root commits**
(`6e5eb7f`, `ccd3e33`, `69da100`), each a full snapshot of ~3,000 files
(3034 / 3039 / 3046 respectively), joined by ordinary merges (PR #11,
`Merge remote-tracking branch 'origin/main'`).

**[OBS]** The documents cite commits that do not exist here. Of 85
seven-hex-digit strings cited as commits across `docs/*.md` and
`BUGS_HISTORICO.md`, **77 resolve to nothing in this repository** — e.g.
`BUGS_HISTORICO.md:4085` cites fix commits `03f6c10`, `22f6edc`, `b981803`,
`e0e7be0` dated 2026-07-07, two weeks before this repo's first commit.

**[OBS]** The project itself records an even earlier horizon:
`docs/FOSSIL_HUNT_20260711.md:307` — "El historial git empieza en el import
squasheado `dbba7ca` (2026-07-05)" — a commit absent here too. And
`BUGS_HISTORICO.md` (B-145) records that fine-grained history was only
recoverable "tras des-shallowear el clon".

**[INF]** So there were at least three history horizons: a working repo whose
commits survive only as orphaned hashes in the ledger; a squashed import on
2026-07-05 (`dbba7ca`); and the GitHub import of 2026-07-21, itself assembled
from three parallel full-tree snapshots. Development ran simultaneously on the
maintainer's machine (`/home/labestiadevigia/vigia-repo`, a path still
hardcoded in `launch_vigia_mcp.sh:2` and `scripts/clean_thinking_artifacts.py:15`)
and in remote agent sessions that each started from an uploaded snapshot with
no shared ancestry. The consequence for any future archaeologist: **the bug
registry, not git, is the project's true chronology** — the first GitHub commit
already references B-171..B-205.

Two hypotheses on the resets are discriminated in §10 (P5).

### 1.2 Timeline of eras

All dates 2026. Sources: file-embedded dates, the `Detectado en` field of the
bug ledger, `SECURITY.md`'s audit table, and git.

| Period | Era | Key evidence |
|---|---|---|
| Feb 22 | Origin scene: RSAC, Rob T. Lee's "find evil" demo; Protocol SIFT | `docs/academic/VIGIA_RESEARCH_REPORT.md:14` |
| Apr 24 | Earliest dated artifact: "Hito 1 COMPLETADO" | `docs/hito_1_estado.md:3` |
| Apr 28 | Pattern DB generated ("Standard: SANS_FIND_EVIL_2026", "110+ forensic cases") | `vigia_patterns_migration.sql:2-4` |
| Apr | Four security-audit rounds (DeepSeek 16 fixes; CAIE born in Kimi's round 3) | `SECURITY.md:305-308` |
| Apr–May | Calibration wave 1: KDE + Ledoit-Wolf empirical-LR track — never wired | `docs/CALIBRATION_ARCHAEOLOGY_20260723.md:73-78` |
| May 2 | **The prior incarnation**: recommendation engine v3.1, Kubernetes containment vocabulary | `vigia_recommendation_engine_v3.1_SAFE.sql:20-23` (§5.3) |
| May 18 | Technical dossier v1.0; the TCV substring filter widened with a comment admitting it is not Daubert-reproducible | `docs/FOSSIL_HUNT_20260711.md:79` |
| ~Jun 14 | **SANS FIND EVIL 2026 submission closes** — [INF] from "2026-06-28, día 14 post-hackathon" | `BUGS_HISTORICO.md:2186` |
| Jun 23–27 | Post-hackathon crash sweep: B-001..B-018 (UnboundLocalError, import plumbing, missing deps) | `BUGS_HISTORICO.md` |
| Jun 28 | Epistemic State Fuzzing session: B-019..B-030 (ABSTAIN collapsing to NOISE, verdict-state contradictions) | `BUGS_HISTORICO.md:2186-2320` |
| Jul 3–11 | Doctrine era: corroboration gates, monotonicity, the label-leak discovery and metric rebuild (B-075) | `docs/ACCURACY.md:67-77` |
| Jul 5 | Squashed import `dbba7ca` — first history reset | `docs/FOSSIL_HUNT_20260711.md:307` |
| Jul 10 | L-067 SUSPICION-ceiling doctrine sealed "collective + Anna's signature" | `KNOWN_LIMITATIONS.md:2187` |
| Jul 11–14 | Fossil hunts I/II; module-archaeology audit (B-117 inverted verdicts; −5,491 lines) | `docs/FOSSIL_HUNT_20260711*.md`, `SECURITY.md:311` |
| Jul 12 | Fraction accumulator gate: two sealed-verdict flips from float emission order, fixed under a byte-identity corpus gate | `docs/FRACTION_GATE_RECORD_20260712.md:41-72` |
| Jul 13 | Ollama demoted after the blind experiment (B-111, N=2, stochastic output) | `BUGS_PENDIENTES.md:79-135` |
| Jul 21 | **GitHub import (second visible reset)**; Codex audit lands B-153..B-205 in one day | `git log`; `docs/CODEX_AUDIT_2026-07-21.md` |
| Jul 23 | Triple archaeology day: calibration archaeology, B-123 excavation, zone38 outward audit; ES/EN parity sentinel promoted to hard guard | three docs; `tests/test_registry_integrity.py:146-160` |
| Jul 25 | Bug ledger split HISTORICO/PENDIENTES; "Ronda 2" epistemological audit | `BUGS_HISTORICO.md:1-12` |
| Jul 31 | Epistemic kernel integrated (Kimi architecture, ChatGPT review, Claude integration) — deliberately outside the verdict path | `docs/EPISTEMIC_KERNEL.md` |
| Aug 1 | Mutation-testing infrastructure; baseline 40.8% over 3 modules; the only Spanish-language commit-message cluster | `docs/MUTATION_BASELINE.md`; git log |
| Aug 9 | DeepSeek returns: 3 of 5 findings refuted; scorer left unmodified "per its own delicacy" | `docs/DEEPSEEK_AUDIT_20260809.md` |
| Aug 12 | B-227: the full suite ran **zero tests** in the documented minimal environment | `BUGS_HISTORICO.md:10524` |
| Aug 15 | `POST HACKATHON` commit prefix retired | `docs/ENGINEERING_DISCIPLINE.md:21-23` |
| Aug 27–28 | Docs consolidation; **web UI** (PR #22) — the first GUI, from an author on record that "una app es un vector más de ataque" | git log; `docs/academic/VIGIA_RESEARCH_REPORT.md:592` |

**[OBS]** The character of the bugs changes across the strata, and this is the
single clearest signal of the project's maturation: early entries are crashes
(`UnboundLocalError`, missing imports); late entries are *epistemic* — a sealed
log that fabricates the formula it claims to have used (B-223), a
self-correction loop that is structurally inert (B-224), a JSON field that
quietly held verdict authority (B-225), a test suite that silently ran nothing
(B-227). The failure mode the project came to fear was not breaking — it was
**appearing to work**.

### 1.3 Who built it

**[OBS]** `AUTHORS.md` documents an unusual formation process: one human
principal investigator (Anna Tchijova — per `docs/academic/VIGIA_RESEARCH_REPORT.md:592`,
a professional cook with no formal IT background, working from Argentina)
directing a "VIGÍA AI Collective" of seven different LLMs with named roles and
attributed subsystems: Claude (integration, MCP bridge), Gemini (the IoI
framework), Kimi (CAIE and the epistemic kernel), DeepSeek (security audit),
Qwen (float determinism, container hardening), Grok (scorer mathematics),
ChatGPT (adversarial review). **[OBS]** An eighth model, Codex, authored the
largest single audit tranche in the ledger (B-153..B-205, 2026-07-21) yet
appears nowhere in `AUTHORS.md` — [INF] a late arrival never back-filled.

This polyglot authorship explains structural facts that would otherwise look
like carelessness: divergent twins of the same function, two unreconciled
sealing schemas, and an audit culture in which every model's finding is treated
as "a claim, not a fact" until verified against the live file
(`docs/ENGINEERING_DISCIPLINE.md` §4.1, §6).

---

## 2. What is deliberate

These decisions have contemporaneous written rationale, enforcement mechanisms,
and in several cases measured acceptance gates. They are design, not accident.

### 2.1 The LLM is outside the decision path — and the enforcement is real

**[OBS]** Mode 1 contains no LLM call at all. `vigia_scorer.py` has zero
occurrences of `llm`/`anthropic`/`ollama`; the only such occurrences in
`sift_orchestrator.py` and `vigia_agent.py` are *negative assertions*
("el LLM no puede anular este gate", `sift_orchestrator.py:476`; "Narrative:
100% deterministic — no LLMs in core analysis", `vigia_agent.py:2155`).

**[OBS]** Where LLM-adjacent outputs threatened to leak authority back in, the
project closed the channel with provenance stamps rather than trust: the B-225
fix (`vigia_scorer.py:1590-1617`) escalates on a Grice verdict only when
`grice_source == "live_grice"` — stamped *after* the live auditor runs
(`sift_orchestrator.py:1176-1186`) — and routes any unverified declared claim
to an authority gate that forces ABSTAIN rather than ignoring it. The
narrative layer has its own guard: `vigia/llm/hallucination_guard.py:9-14`
("the narrative cannot amplify the evidence") and the C3 narrative auditor's
`ROLE_OVERRIDE`/`VERDICT_COERCION` detectors (B-124).

**[OBS]** The phrase **"zero verdict authority"** recurs verbatim across at
least five independent modules (`vigia/tools/paired_review.py:9`,
`vigia/core/case_linkage.py:25`, `vigia/vigia_sift_bridge.py:3540`,
`vigia/core/signal_quality_shadow.py`, `vigia/pipeline/vigia_integration_bridge.py:390`)
— an architectural principle that became a house idiom.

**[INF]** Deliberate — but see §10 (P1) for the layered origin story: the
principle, the economics, and the enforcement have three different birthdays.

### 2.2 External sealing: an engine must not be able to seal its own lie

**[OBS]** `vigia/core/ebs_v1.py:20-36`: "**ABSOLUTE RULE: This module contains
DATA ONLY** … A bundle that hashes itself allows a compromised engine to seal
its own lie." Mirrored in `vigia/core/bundle_builder.py:12-16`. The
third-party verifier is deliberately outside the package and stdlib-only:
`forensics/verify_ebs_v1.py:7-12` — "GARANTIA DE INDEPENDENCIA TOTAL … Si el
verificador necesita importar el codigo de produccion, el sistema no es
auditable por terceros."

### 2.3 The tamper-evident tool log evolved against an enumerated attack taxonomy

**[OBS]** `vigia/core/tool_log_chain.py:8-14` documents v1's weakness in the
module itself ("solo `result_summary` está protegido … NO usar para escribir"),
and `tests/test_hash_chain_hardening.py:1-24` names seven concrete attacks
(A1..A7) that "ANTES del hardening pasaban en silencio" — field edits, last-entry
edits, keyless chain recomputation, fabricated bundle hashes, tail truncation,
checkpoint tampering. The residual v2 gap (deleting the last N entries leaves
the chain internally consistent) was found later, reproduced, and closed with a
bundle-level tip anchor (`tests/test_r3_5_chain_tip_truncation.py:1-30`;
`docs/REDTEAM_ROUND3_EMERGENT.md:338-345`). Verification emits machine-readable
*caveats* for legacy or anchorless chains instead of silently passing
(`tool_log_chain.py:284-297`).

### 2.4 The SUSPICION ceiling is sealed doctrine, applied only after measurement

**[OBS]** Three distinct mechanisms are often conflated:

1. The scorer's vocabulary simply has no INTENT rung — the string `INTENT`
   does not occur in `vigia_scorer.py`. Above the MALICE threshold with no
   corroboration branch open, the verdict falls to SUSPICION
   (`vigia_scorer.py:1534-1543`, the B-068 anti-drowning gate).
2. The Daubert corroboration gate rejects single-source candidates
   *pre-emission* (`CLAUDE.md:555-562`).
3. L-067, the doctrinal ceiling for evidence confined to one fabrication
   channel: "Whoever controls the disk controls all of those sources at once"
   (`KNOWN_LIMITATIONS.md:2201-2207`) — sealed 2026-07-10 with the maintainer's
   signature, and enforced only after a measured gate: "0 flips across 291
   bundles, corpus 167/199 identical, byte-identical runner output."

**[OBS]** The ceiling caps only downward — "nunca eleva un ABSTAIN/NOISE"
(`vigia_agent.py:226-229`). The same discipline appears in B-097's history:
the pre-registered recovery rule was measured, found to expose 3 cases, and
**not applied** (fail-closed) until a triple-source validation existed
(`vigia_agent.py:236-247`).

### 2.5 Provenance retention instead of deletion

**[OBS]** `attic/README.md` defines a retirement protocol: files move only
after zero-reference verification, keep their original layout, and carry
per-file justifications plus — unusually — a NOT-moved list with reasons.
Fossil hunts are labeled "cacería y diagnóstico. NO contiene fixes" and open
with a restore tag. The bug ledger is append-only ("los bugs resueltos no se
eliminan, solo se archivan", `BUGS_HISTORICO.md:1-12`) and explicitly framed as
red-team reading. **[INF]** Several fossils survive *because* an audit document
or test cites them as evidence — deleting them would break an audit trail, not
a build (see §9).

### 2.6 Honest degradation as a system-wide posture

**[OBS]** Recurring, enforced patterns: ABSTAIN when provenance collapses
rather than a confident NOISE (`vigia_scorer.py:1401-1414`, "un veredicto
inadmisible no puede presentarse como NOISE confiado"); ABSTAIN ⊥
`is_conclusive=True` (B-027, `vigia_agent.py:1483-1496`); anything
uncalibrated wired in SHADOW/WARN mode with "cero autoridad de veredicto"
(`vigia/core/signal_quality_shadow.py`, B-116); a missing
`baselines_institucionales.yaml` *downgrades* the bundle level with a warning
instead of failing or faking (`vigia/pipeline/vigia_integration_bridge.py:937`).

---

## 3. What is historical accident

### 3.1 The flat→package migration was never finished — in either direction

**[OBS]** Top-level `engine/`, `governance/`, `models/`, and part of
`forensics/` are one-line `from vigia.core.X import *` shims; simultaneously,
`vigia/core/vigia_scorer.py` re-exports *outward* to the root `vigia_scorer.py`,
and `vigia/tools/vigia_entanglement.py` / `vigia_adversarial_nlp.py` are
"COMPATIBILITY STUB" shims for modules that assumed the other layout.
**[OBS]** The canonical modules still carry their pre-move path in their own
docstrings — `vigia/core/resource_optimizer.py:2` says
`vigia/engine/resource_optimizer.py`, a directory that **never existed**.
**[INF]** The migration ran module-by-module in both directions, was never
completed, and the intermediate state froze because tests now depend on it:
CI runs `tests/integration/test_ebs_v1_integration.py` directly (40+ imports of
the flat names, `.github/workflows/vigia-forensic-ci.yml:55`) while the pytest
suite excludes it.

**[OBS]** The duplicate hierarchy caused a real production bug: `vigia/forensics/`
shadows top-level `forensics/` on `sys.path` depending on import order (B-097),
fixed with an importlib-by-absolute-path workaround and a regression test that
deliberately re-creates the shadow
(`vigia/pipeline/pipeline.py:60-100`; `tests/test_pipeline_verify_import_shadowing.py:40`).
And the Docker healthcheck still imports the flat layout:
`Dockerfile:83` runs `from ebs_v1 import EvidenceBundle` — a module that no
longer exists at root and a class name (`EvidenceBundle`) that exists nowhere
in the tree. **[INF]** The container healthcheck has been failing since the
migration; nothing noticed because nothing consumes it.

### 3.2 Exit codes numbered by chronology, not severity

**[OBS]** `vigia_agent.py:100-105`: `0=NOISE, 1=MALICE, 2=ERROR, 3=INTENT,
4=ABSTAIN, 5=SUSPICION`. The 0/1/2 band is the classic Unix triad for a tool
whose hackathon was literally named FIND EVIL ("0=no evil, 1=evil, 2=error");
3, 4, 5 were appended as verdicts entered the vocabulary — B-097 gave SUSPICION
the *new* code 5 because "INTENT conserva el 3 (contrato histórico)"
(`vigia_agent.py:93-102`). Severity order and numeric order have permanently
diverged, and `README.md:57` still documents only codes 0–3.

### 3.3 A dependency bound held by accident for months

**[OBS]** `requirements.txt` (B-227 comment): the MCP bridge does
`from mcp.server.fastmcp import FastMCP`, which `mcp` 2.0 removed. "Until this
bound was declared, the only thing holding the line was `fastmcp`'s own
transitive `mcp<2`, which is an accident: **no module in this repo imports
`fastmcp`**, so a cleanup dropping it would have broken the MCP surface
silently." Now pinned by `tests/test_mcp_dependency_contract.py`.

### 3.4 Divergent twins that drifted apart

- **[OBS]** `phonetic_dict.json` exists at the root and in `data/` **with
  different content** (distinct md5s). The consolidating loader
  (`vigia/phonetic_loader.py:22-38`) documents the two-path history, but its
  priority-2 path (`vigia/data/phonetic_dict.json`) does not exist, and
  `vigia/tools/document_integrity.py:54` still hardcodes that missing path.
  [INF] The consolidation was written; one reader was never migrated; the
  copies have since drifted.
- **[OBS]** `initial_templates.sql` and `initial_templates_v2.sql` are
  **byte-identical** (same md5) — a copy-then-rename never reconciled.
- **[OBS]** `_sanitize_grep_pattern` exists twice with different bodies —
  `vigia/vigia_sift_bridge.py:174` vs `vigia/security/sandbox.py:353` — "dos
  validadores de seguridad con semánticas divergentes para la misma superficie"
  (`docs/AUDITORIA_FUGA_INDIRECTA.md:170`). Both live.

### 3.5 Output directories from three conventions

**[OBS]** `results/` (1,437 files, live), `vigia/results/` (agent-session
outputs, live), and `resultados/` — four files from a single case, referenced
by no code, [INF] a snapshot from before the English naming convention.
`vigia/ui/normalizer.py:3` concedes the corpus holds "three [schema
generations]". Likewise `docs_merged/` (193 hash-named files) is the
superseded staging input of a documentation reorganization whose manifest is
committed (`docs/academic/_reorganization_manifest.json`); one orphaned
cleaner still points at it with an absolute path from the author's machine.

### 3.6 The `prec=28` ceremony

**[OBS]** `vigia/tools/caie.py:120`: "prec=28 matches the Directiva 4
requirement." No document named "Directiva 4" survives in the repository (the
comment trail says "Qwen P0 + Red Team P0_CRITICO Directiva 4",
`caie.py:103`) — and **28 is `decimal`'s default precision in Python**: the
requirement mandates what the language does anyway. Meanwhile the scorer's own
`_dround` (`vigia_scorer.py:174-182`) configures the Decimal context and then
uses built-in `round()` on floats, bypassing it. **[INF]** The comment
preserves a vanished authority; the mechanism it mandates is partly unused.
This is the purest fossil in the codebase: ceremony outliving both its
lawgiver and its law.

### 3.7 Registry collisions from parallel sessions

**[OBS]** B-206/207/208 had to be renumbered to B-211/212/213 (commit
`c5fec4f`); L-051 collided and became L-067, with the renumbering scar
documented in place (`KNOWN_LIMITATIONS.md:2192-2198`); B-031..B-044 are
retrospective back-fills ("[entrada retrospectiva 2026-07-23]") and B-057 is a
genuinely vanished ID with zero references. **[INF]** Parallel AI sessions
allocated IDs without seeing each other — the ledger is a secondary source for
the pre-July era, reconciled after the fact.

---

## 4. Invariants that exist only in tests

These are load-bearing rules a contributor learns about from a red CI run, not
from any prose document.

| Invariant | Enforced by | Documented in prose? |
|---|---|---|
| ES and EN bug registries must contain the identical B-* set, and the 2026-07-25 split must remain a true partition | `tests/test_registry_integrity.py:143,173,190` | No — the test docstring is the only statement ("Un registro espejo que diverge en contenido deja de ser espejo") |
| Both FastAPI wrappers (`vigia_api`, `vigia.vigia_api`) must expose identical protocol and boundary behavior | `tests/test_b168_api_contract_parity.py` + 4 siblings | Only in the tests ("A caller must not get a weaker protocol … merely by choosing the package import path") |
| The scoring pipeline must not import the epistemic kernel | `tests/test_epistemic_kernel.py:443-464` (a `git grep` in a test) | Yes (`CLAUDE.md`, `docs/EPISTEMIC_KERNEL.md`) — the rare case where prose and test agree |
| `mcp<2` and the CI dependency set must match what the code imports | `tests/test_mcp_dependency_contract.py`, `tests/test_requirements_ci_contract.py` | Only as comments inside the requirements files |
| Every reachable canonicalizer copy — including the stdlib-only verifiers loaded *by file path* — must encode identically | `tests/test_canonicalize_lockstep.py:1-26` | No ("a divergence between verifier copies is a court-facing contradiction") |
| The reasoning trace's DECISION step must equal the sealed verdict, and building the trace must leave `bundle_digest` byte-identical | `tests/test_reasoning_trace_bundle_gate.py:9-16` | Module docstring only |
| Determinism is asserted as equality **between runs**, never against a hardcoded score | `tests/test_determinism_sealed_verdict.py:16-23` | No — and it is arguably the project's deepest testing doctrine |
| Decision boundaries and sentinel strings are pinned at the exact cut point | `tests/test_collapse_decision_boundaries.py` | Yes — `CLAUDE.md:444-450` cites the motivating mutation result (77.94% coverage, 13.8% mutation score) |
| Self-correction documentation must tell the truth about its own dormancy | `tests/test_b224_self_correction_docs_are_honest.py` | The test *is* the doc-honesty mechanism |
| An unset enrichment flag must not report an orphaned module as active integrity | `tests/test_config_sentinel_orphaned_module_env_map.py:6-27` | No — "a sealed integrity report that would lie about its own subject" |

**[INF]** The pattern: after being burned twice by registry drift and once by a
suite that silently ran nothing (B-227), the project converted documentation
promises into executable contracts. The tests are the constitution; the prose
is commentary.

---

## 5. APIs designed around constraints that no longer exist

### 5.1 The 0-token primary mode

**[OBS]** `docs/academic/VIGIA_RESEARCH_REPORT.md:592` quotes the author: "como
no tenía dinero para Claude Code, casi todo VIGIA fue construido para modo
fallback o Ollama" — the economic constraint that made the deterministic,
LLM-free Mode 1 the *primary evaluated mode*. The constraint was later
formalized as limitation L-055 ("API and subscription are separate
authentication products … Ollama fills that role"). See §10 (P1) for how this
scarcity origin coexists with the Daubert rationale.

### 5.2 Hackathon-rule fossils still in force

**[OBS]** `CLAUDE.md:530-538` still mandates a token-usage block in every
report "required for audit trail completeness under **SANS submission rules**"
— for a competition that closed in June. `KNOWN_LIMITATIONS.md` defines the
status tag `[FIX DESIGNED]` as "Application is deferred **post-hackathon**" — a
freeze-window artifact now permanent vocabulary. The `POST HACKATHON` commit
prefix outlived the event by two months before being retired (2026-08-15).
Exit codes 0/1/2 encode the hackathon's own name ("0=no evil, 1=evil").

### 5.3 The Kubernetes incarnation

**[OBS]** `vigia_recommendation_engine_v3.1_SAFE.sql` (2026-05-02) creates
`recommendation_policies`/`recommendation_ledger` tables whose action
vocabulary is Kubernetes incident response — `ISOLATE_POD`,
`QUARANTINE_NAMESPACE`, `REVOKE_SA_TOKEN` — gated by a mandatory human
`operator_hmac_signature`, with a verdict vocabulary
(`REJECT`/`ABSTAIN`/`ESCALATE`) that matches nothing in today's engine. Its
Python twin survives at `vigia/inference/recommendation_engine_v3.1.py` — a
filename containing a dot, which **cannot be imported as a Python module at
all**; zero importers. The `_SAFE` suffix marks hazard removal (no
auto-executing triggers, no signature bypass). **[INF]** VIGÍA was, for at
least one May 2026 iteration, an auto-containment recommender for a K8s
estate; the `RiskBoundedDecisionLayer` it consumed is the one component that
survived the pivot — and the one B-117 later caught emitting inverted verdicts.

### 5.4 The Ollama-primary era

**[OBS]** `docs/DAUBERT_JUDICIAL.md:15-17` argues forced determinism via "fixed
seed for Ollama (42)" — the determinism case was originally written for a
local-LLM deployment. Mode 3 was then demoted to non-primary on the strength
of a two-run blind experiment in which `hermes3:8b` hallucinated schema fields
and returned truncated JSON (B-111, `BUGS_PENDIENTES.md:79-135`; "El
comportamiento es estocástico, no determinista").

### 5.5 Environment fossils

**[OBS]** `README.md:42` installs with `--break-system-packages` (the SIFT
Workstation's Ubuntu/PEP-668 reality); `launch_vigia_mcp.sh` hardcodes every
path to `/home/labestiadevigia/` and is unrunnable on any other machine
without editing; `CLAUDE.md` caps investigations at 40 tool calls and had its
tool count corrected from a stale 21 to 22 (commit `266fd03`).

---

## 6. Redundant abstractions

| Abstraction | Duplicate of | Status | Why it persists |
|---|---|---|---|
| `engine/`, `governance/`, `models/`, `forensics/*` shims | `vigia/core/*` | Live only for one legacy integration test CI runs directly | Frozen half-migration (§3.1) |
| `caie_legacy_root.py` (1,884 lines) | `vigia/tools/caie.py` (3,469 lines) | Dead — zero importers, excluded from engine attestation *in two places with matching comments* (`vigia/core/bundle_builder.py:463`, `vigia/pipeline/pipeline.py:1399`) | Provenance: it preserves the original B-001 bug at `caie_legacy_root.py:1464`, cited by the ledger (§10, P7) |
| `vigia_api.py` vs `vigia/vigia_api.py` | each other | Both live; five parity tests police the copy | Accident promoted to contract (§10, P6) |
| Root `sift_orchestrator.py` (88 KB "shim de compatibilidad") | `vigia/sift/sift_orchestrator.py` (the rich one) | Both live; the shim is on the Mode-1 path | Two orchestrator generations, confirmed distinct by diff on 2026-06-19 (`docs/EXECUTION_MODES.md`) |
| Agent bundle schema vs EBS v1 sealed bundles | two sealing families | Both live, "never reconciled into one schema, and probably won't be short-term" | Admitted openly (`docs/EXECUTION_MODES.md:72-76`) |
| `vigia/core/vigia_scorer.py` | root `vigia_scorer.py` | Frozen re-export after the copy diverged with a latent `NameError` (B-055) | "Se congela como re-export para que NO pueda volver a divergir" |
| `vigia/abductive_intent_engine.py` + `vigia/tools/abductive_intent_engine.py` | one shim, duplicated | Both live | The L-052 consolidation shim was itself copied into two locations |
| `initial_templates.sql` / `_v2.sql` | byte-identical | Dead ×2 | Nothing loads any root SQL file |

**[OBS]** The repo's own census counted **144 names defined in more than one
file with different bodies** (`docs/AUDITORIA_FUGA_INDIRECTA.md:166`). Most
were resolved; the two named as still-live divergences
(`_sanitize_grep_pattern`, `to_caie_fracture`) remain so.

---

## 7. De facto API — behavior depended on but never promised

Hyrum's Law instances, each with evidence of real consumption:

1. **Exit codes 4 and 5.** `EXIT_ABSTAIN=4` and `EXIT_SUSPICION=5` exist and
   are relied on by wrappers, yet `README.md:57` documents only 0–3.
2. **`gate_verdict`.** The pipeline notes its only in-repo consumer is
   `show_4_hashes.py` "(demo)" (`vigia/pipeline/pipeline.py:882`) — yet that
   demo's output is quoted in shipped court-facing artifacts
   (`results/real/VIGIA-REAL-008_amicus_curiae.md:46`). A demo script became a
   de facto reporting interface.
3. **Case-JSON fields as covert inputs.** Until B-225, a case file could
   *declare* `grice_verdict` and acquire verdict authority — an output field
   functioning as an undocumented input API. The fix (provenance stamps +
   authority gate) is effectively a formal deprecation of that accidental API,
   done fail-closed: the declaration now forces ABSTAIN rather than being
   ignored (`vigia_scorer.py:1601-1604`). L-072 records that `semantic_role`
   remains an open instance of the same class.
4. **`results/` is sealed under chain v1 forever.** All bundles in `results/`
   were sealed under the weaker v1 log chain (`vigia/core/canonicalize.py:57-59`);
   verification of the archive is possible only to the v1 standard. Stated in
   code comments; absent from any operator-facing document.
5. **`blind_cases_for_mcp/`** — generated once by a now-orphaned script,
   then registered as a first-class evidence root
   (`vigia/ui/evidence_paths.py:27`, both INSTALL guides). The corpus outlived
   its generator.
6. **Mode 1 can seal INTENT.** `CLAUDE.md:320-322` says Mode 1's motor has no
   INTENT rung — true of `vigia_scorer.py`. But the agent layer's L-036
   override manufactures `INTENT_DETECTED` when primary signals exceed z>3
   over an undetermined hypothesis (`vigia_agent.py:1072`), and
   `classify_agent_verdict` seals it as INTENT with exit code 3. Corpus
   bundles carry it; tests pin it (`tests/test_b058_abstain_classification.py:74`).
   The de facto verdict surface is wider than the documented one.

---

## 8. Requirements encoded only in tests

Beyond the invariant table in §4, three test files deserve archaeological note:

- **`tests/test_collapse_decision_boundaries.py`** pins exact sentinel strings
  (`"sensor_independence"`), exact threshold cut points, and exact `explain()`
  message text — requirements that exist nowhere else. Its docstring records
  the origin: mutation testing proved the MALICE threshold "podía moverse a un
  valor inalcanzable sin que nada fallara". It also honestly notes an unfixed
  design smell it deliberately did not correct (`explain()` recomputes its
  reason independently of `resolve()`).
- **`tests/test_b097_motor_suspicion_verdict.py`** encodes a *process*
  requirement: its tests "eran sentinelas `xfail(strict=True)` mientras estuvo
  NO APLICADO" — tests as a pre-registration mechanism for a fix awaiting its
  acceptance gate.
- **`tests/test_b224_self_correction_docs_are_honest.py`** tests the
  *documentation*, not the code — the requirement that VIGÍA's docs not
  overclaim its self-correction capability is itself executable.

**[OBS]** One stated falsifier remains unimplemented: `docs/ENGINEERING_DISCIPLINE.md:209-211`
declares the architecture's own test — "swapping the narrator backend (Ollama ↔
hosted API) must change only the wording — never the verdict" — and no test in
the tree performs that swap. [INF] The doctrine's flagship falsifier is, as of
this excavation, prose.

---

## 9. Refactor survivors and why they persist

Survivors whose reason for existence is no longer obvious from the code alone:

- **`apply_b047*.py`, `apply_b048.py`** — surgical-patch scripts, already
  applied, dead as executables. Load-bearing as *documentation*: a live test
  requires their effect ("Requiere el guard aplicado (apply_b047_mathutils.py)",
  `vigia/tests/test_b047_correlation_groups.py:231`) and design docs cite
  their anchors.
- **`scratchpad/q2_induction.py`** — the sole committed file of an explicitly
  ephemeral directory, kept because a sealed security audit cites it as its
  reproducibility anchor (`docs/AUDIT_SEALED_VERDICT_SECURITY.md:6`).
- **`coverage_baseline_20260622.txt`** — a raw pytest transcript from the
  author's machine; zero references. It has become an accidental index of
  deleted modules (it lists `vigia/pipeline/report_exporter.py`, since
  removed) and a growth marker: 169 collected tests then, 2,176+ passing now.
- **`scripts/pre_release_check.py`** — contains `BANNED_FILENAMES`, **an empty
  dict whose entire content is a comment** explaining why it is empty (the
  banned v2 was deleted; v1 is canonical). Several `BANNED_MODULES` entries
  outlived their targets; one (`ebs`) bans a module that still exists. The
  enforcement script itself is invoked by nothing. A ban registry as pure
  sediment.
- **`vigia/core/risk_bounded_layer.py:35-39`** — the docstring preserves the
  bug report of a *deleted* file (the orphaned v2 that documented fix P0-001
  but "nunca se cableó"). The survivor carries its dead twin's epitaph.
- **`docs/VIGIA_THEME_SONG.md:26`** — still sings "Ledoit-Wolf and KDE
  quantifying the risk": machinery the 2026-07-23 calibration archaeology
  proved was never in the decision path. The song is the last active reference
  to the retired calibration wave.
- **`CollapseDecisionLayer`** — the best-tested module in the repo
  (boundary-pinned after the mutation baseline) is reachable only via
  `evaluate()`, which the Mode-1 scorer never calls (`_vigia_score` calls
  `detect_fractures()` directly, `vigia_scorer.py:832-869`). Its
  `independent_sources` context field is populated by CAIE and read by
  nothing. [INF] A verdict layer that migrated out of the verdict path while
  its test suite — and its citation in `CLAUDE.md` as the verdict-path
  exemplar — stayed put.

---

## 10. Competing historical hypotheses

For each significant pattern: at least two rival explanations, the evidence
that discriminates, and a verdict with the project's own confidence
vocabulary. Following the house method: the most obvious explanation was not
assumed correct.

### P1 — Why is the LLM outside the decision loop?

- **H-A (doctrine-first):** designed from first principles for Daubert
  admissibility.
- **H-B (scarcity-first):** no API budget forced an LLM-free build; the
  necessity was later elevated to principle.
- **H-C (incident-driven):** the boundary was hardened in response to
  concrete authority leaks.

**Discriminating evidence.** H-B has a direct attestation: "como no tenía
dinero para Claude Code, casi todo VIGIA fue construido para modo fallback o
Ollama" (`VIGIA_RESEARCH_REPORT.md:592`). H-A has early theory documents and
the April-era architecture. H-C has the record: the enforcement mechanisms all
post-date the principle — B-225 (August) closed a JSON field carrying verdict
authority, B-124 (July) added coercion detection, the confused-deputy scan
landed in July (`e0033f5`), and the declared backend-swap falsifier is still
unimplemented (§8).

**Verdict: all three, at different layers — CONFIRMED.** The *principle* is
early and genuine; the *primacy of the 0-token mode* is economic in origin by
the author's own words; the *enforcement* accreted incident-by-incident for
two months after the principle was declared. The architecture docs narrate the
outcome as if born whole; the ledger shows it was earned.

### P2 — Why exact-arithmetic determinism?

- **H-A:** a day-one design requirement ("zero floating-point in the critical
  path", `README.md:78`).
- **H-B:** a property retrofitted after concrete nondeterminism incidents,
  never fully achieved, whose documentation overclaims.

**Discriminating evidence.** For H-B: the float purge is a two-month campaign
across the ledger (B-007/8/9, B-024, B-042/43, B-083, B-104/105, L-021 in
phases); the decisive incident is dated and quantified — float accumulation
order flipped two sealed verdicts at a 5e-5 rounding cliff
(`docs/FRACTION_GATE_RECORD_20260712.md:41-47`); and the live scorer *today*
rounds through built-in `round()` on floats (`vigia_scorer.py:174-182`),
directly under a comment explaining why Decimal was introduced. L-073 — the
only document that states the real invariant — frames it correctly:
boundary-exact, platform-stable reproducibility, **not** float-free purity.
For H-A: only the aspirational claims themselves.

**Verdict: H-B — CONFIRMED.** The determinism that actually holds
(bit-identical between runs and platforms) was earned late, incrementally, and
against the codebase's own grain; the README's stronger claim is false as
written and contradicted by the project's own L-073.

### P3 — Why does Mode 1 stop at SUSPICION?

- **H-A (epistemic doctrine):** independence of sources cannot be certified by
  an unattended engine; "whoever controls the disk controls all of those
  sources at once" (L-067).
- **H-B (calibration artifact):** the ceiling fell out of accuracy tuning —
  the B-068 anti-drowning gate that stopped same-domain volume from buying
  MALICE — and was rationalized afterward.

**Discriminating evidence.** For H-A: L-067 is sealed doctrine with the
maintainer's signature (2026-07-10) and a philosophical argument that predates
its enforcement; enforcement waited for a measured 0-flip gate — doctrine
first, wiring later. For H-B: the corroboration branches
(`vigia_scorer.py:1454-1471`) were added inside the R4-3/B-068 accuracy
recovery, and thresholds were recalibrated in the same era (B-076). Crucially,
the scorer never had an INTENT rung to remove — the "cap" is a documentation
metaphor — while the agent layer above it mints INTENT via L-036
(`vigia_agent.py:1072`), so the ceiling is not even airtight.

**Verdict: co-evolution — CONFIRMED for doctrine, with a documented leak.**
The doctrine is real and was applied with unusual discipline (fail-closed
until measured), but it crystallized *during* the accuracy-recovery campaign,
not before it, and the sealed-verdict surface contradicts the "no INTENT"
shorthand. The honest statement is L-067's, not `CLAUDE.md:320`'s.

### P4 — Why is everything bilingual ES/EN?

- **H-A (market):** designed for Spanish-speaking judicial systems.
- **H-B (biography + submission):** the maintainer works in Rioplatense
  Spanish; the hackathon and public repo required English; a parity test then
  ratcheted the duplication into law.

**Discriminating evidence.** For H-B: the working-agreement rule itself
("Conversation with the maintainer is in Rioplatense Spanish … Everything
committed … is in English", `docs/ENGINEERING_DISCIPLINE.md:17-19`) —
imperfectly enforced, since the ledger and half of `docs/` are Spanish; the
parity sentinel was promoted to a hard guard only after drift was detected
twice (`tests/test_registry_integrity.py:146-160`); the English registry had
to be back-filled in bulk (root commit `69da100`, "201 = 201"). For H-A: the
*detection substrate* is genuinely bilingual by design — Spanish-language
deception regexes in the pattern DB, the Grice detector "bilingual EN+ES",
cultural neutrality "calibrated for Rioplatense Spanish" (`SECURITY.md:300`).

**Verdict: H-B for the documentation duplication, H-A for the detector —
CONFIRMED.** Two different bilingualisms with two different causes that happen
to look like one policy.

### P5 — Why does git history start at 2026-07-21 with three roots?

- **H-A (deliberate scrub):** history removed intentionally.
- **H-B (workflow artifact):** parallel development lines (local machine +
  remote agent sessions seeded from snapshots) merged without shared ancestry.

**Discriminating evidence.** For H-B: the three roots are near-identical
full-tree snapshots differing by a handful of files; the house rules *forbid*
history rewriting in agent sessions (`docs/ENGINEERING_DISCIPLINE.md` §2); the
orphaned commit hashes were left in the documents (a scrub would have removed
the project's own audit trail, which the project treats as sacred); and the
project *complains* about its own resets — the fossil hunt calls the squashed
import an obstacle, and B-145 records having to un-shallow a clone to recover
history. For H-A: nothing — no motive, no cleanup of references.

**Verdict: H-B — CONFIRMED.** The resets were tooling events the project
itself experienced as losses. Ironic footnote: the project's threat model
literature treats git-history scrubbing as an Indicator of Intent
(`docs/DAY_ZERO_NORMAL_VIGIA_NOTES.md`); its own history gaps are the benign
twin of that signal — an object lesson in its own Refutation Protocol.

### P6 — Why do two copies of the FastAPI wrapper survive with five parity tests?

- **H-A (deliberate redundancy):** two import paths as a supported public
  contract.
- **H-B (frozen accident):** an unresolved duplicate whose deletion risk,
  under the "no unrequested improvement" and surgical-patch doctrines,
  exceeded its maintenance cost — so it was fenced with tests instead.

**Discriminating evidence.** The parity tests frame both paths as "supported"
(H-A language) — but the twins still *differ*: the root copy carries two
security improvements the package copy lacks, including the 404-oracle fix
(`vigia_api.py:195-196`), which true contract-parity would have propagated.
The newest UI generation explicitly refuses to touch them
(`vigia/ui/server.py:3-5`). A deliberate two-path contract would have one
source and a re-export shim — the pattern this same repo uses elsewhere
(`vigia/core/vigia_scorer.py`).

**Verdict: H-B — CONFIRMED BY INDUCTION.** The duplication is an accident
promoted to a test-guarded invariant; the surviving behavioral drift is the
discriminator.

### P7 — Why is `caie_legacy_root.py` still at the repository root?

- **H-A (Hyrum compatibility):** something might still import it.
- **H-B (provenance):** the historical record cites it, and deleting it would
  orphan the audit trail.

**Discriminating evidence.** Against H-A: zero importers (grep-verified by the
project's own audit, `docs/AUDITORIA_FUGA_INDIRECTA.md:166`); the one latent
import fallback names plain `caie`, not this file. For H-B: the ledger cites
`caie_legacy_root.py:1464` as the site of the original B-001 bug — the file
*preserves the bug* as evidence; the engine attestation excludes it
deliberately in two places with matching comments; and the mutation config
copies it only so tests that reference it import cleanly.

**Verdict: H-B — CONFIRMED.** It is a museum specimen with a catalog number,
not a compatibility shim.

### P8 — Why five deployment modes and five entry-point generations?

- **H-A (product design):** deliberate deployment tiers.
- **H-B (accretion):** entry points accumulated under deadline pressure and
  multi-model authorship, then were catalogued after the fact.

**Discriminating evidence.** The project answers this itself:
`docs/EXECUTION_MODES.md:1-8` — "built by one person … with a multi-AI
collective … under a tight deadline. As a result it has more than one way to
run an analysis and seal a result, and they don't all produce the same kind of
output. This document exists so nobody else has to reverse-engineer that the
hard way" — and `:72-76`: "We're not hiding the duplication — a project that's
honest about how it grew is more useful to learn from than one that pretends
it arrived fully formed." Physical evidence agrees: two unreconciled sealing
schemas, a Docker healthcheck broken since the layout migration, a launcher
hardcoded to the author's home directory.

**Verdict: H-B — CONFIRMED, by confession.** The five-mode table in the README
is descriptive taxonomy, not design intent.

---

## 11. Findings not acted on

Doc/code divergences and hazards surfaced by this excavation, reported per the
house rule (findings are claims for the maintainer, not silent patches):

> **Update 2026-08-29:** at the maintainer's request, these findings are now
> registered in `BUGS_PENDIENTES.md` / `BUGS_PENDIENTES_EN.md` — item 1 as
> **B-228**, item 2 as **B-229**, items 3, 4 and 7 as **B-230**, item 5 as
> **B-231**, item 6 as **B-232**, item 9 as **B-233**, and item 10 as
> **B-234**. Item 8 (git tags) is a process observation with no repo-side
> fix and was not converted.

1. **`README.md:78` / `CLAUDE.md` Invariant 4 float overclaim** — "zero
   floating-point in the critical path" is false as written;
   `vigia_scorer._dround` returns floats via built-in `round()`. L-073 states
   the correct invariant. The README should say what L-073 says.
2. **`CLAUDE.md:320` INTENT wording** — true of the motor, misleading for the
   sealed surface (L-036 mints INTENT at the agent layer with exit code 3).
3. **`README.md:57` exit codes** — documents 0–3; codes 4 (ABSTAIN) and
   5 (SUSPICION, B-097) are absent.
4. **`KNOWN_LIMITATIONS.md:2222` stale** — still says SUSPICION shares
   `EXIT_INTENT`; B-097 gave it code 5.
5. **`Dockerfile:83` healthcheck** — imports a nonexistent module and class;
   failing since the flat→package migration.
6. **`vigia/tools/document_integrity.py:54`** — reads
   `vigia/data/phonetic_dict.json`, which does not exist; root and `data/`
   copies of the dictionary have divergent content.
7. **`KNOWN_LIMITATIONS.md:1158`** — cites `vigia/tools/caie_legacy_root.py`,
   a path that does not exist (the file is at repo root).
8. **Zero git tags on the remote** despite `docs/ENGINEERING_DISCIPLINE.md` §2
   mandating pre-session restore tags — either unpracticed or local-only
   (indiscriminable from this clone; git does not push tags by default).
9. **Unimplemented flagship falsifier** — the narrator backend-swap test
   declared in `docs/ENGINEERING_DISCIPLINE.md:209-211` has no implementation.
10. **Zero-reference cleanup candidates** (each still needs its own
    discriminating experiment before deletion, per the fossil doctrine):
    `initial_templates_v2.sql` (byte-identical twin),
    `vigia/inference/recommendation_engine_v3.1.py` (unimportable filename) +
    its SQL, `resultados/`, `coverage_baseline_20260622.txt`,
    `tools/vigia_prepare_evidence.py`, `c3_pattern_compare.py`,
    `c3_role_verdict_probe.py`, `convert_mans_to_ebs.py`,
    `vigia/core/geopolitical_v2.py`.

---

## 12. Limitations of this excavation

- The pre-April 2026 record is thin: the RSAC origin and the earliest design
  debates survive only in the retrospective research report.
- All pre-2026-07-21 chronology rests on the project's own documents, which
  §3.7 shows were partially back-filled; dates from the ledger are
  secondary-source dates.
- The three sweep reports were spot-checked against live files at their
  highest-impact claims (float rounding, INTENT override, parity test,
  healthcheck, SQL twins, orphaned hashes, "Directiva 4"), not re-verified
  line-by-line in full.
- No code was executed; "dead" statuses rest on reference analysis (grep,
  imports, CI configs) plus the project's own zero-reference audits — the
  same standard `attic/README.md` uses, with the same caveat that reflection
  or external consumers cannot be fully excluded from a single repo.
- The git-tag question (§11.8) is genuinely indiscriminable from a clone.

---

*Prepared as a read-only excavation on branch
`claude/archaeologist-architecture-analysis-r48jxg`. No product code was
modified. Method: rival-hypothesis abduction with index consultation before
conclusion — the repository's own discipline, applied to the repository
itself.*
