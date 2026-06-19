# VIGÍA Execution Modes —

VIGÍA grew fast, across many sessions as a result it has more
than one way to run an analysis and seal a result, and they don't all
produce the same kind of output. This document exists so nobody else has to
reverse-engineer that the hard way.

## Two output families today

**1. EBS v1 sealed bundles** — `bundle_version`, `evidence_graph`,
`decision_trace`, `policy_spec`, `actions`, `system_state`, `integrity`,
optionally `caie_analysis`. Produced by `vigia/core/bundle_builder.py`
(`seal()` / `build_bundle()`) and `vigia/pipeline/pipeline.py`. Verified
independently, stdlib-only, by `forensics/verify_ebs_v1.py`.

**2. Agent audit-trail bundles** — `audit_trail`, `narrative`,
`pipeline_results` (one top-level `abduction` hypothesis plus a flat list of
`signals`), `sans_compliance`. Produced by `vigia_agent.py::_seal_bundle()`
when you run `python3 vigia_agent.py --evidence ... --case-id ...` directly.
Not the EBS v1 schema — `verify_ebs_v1.py` correctly reports it as
non-compliant structure if you point it there. That's expected, not a
verifier bug.

These two were never reconciled into one schema. As of 2026-06-19, family
(1) gained a deterministic Devil's-Advocate / counter-hypothesis field
(`vigia/core/devil_advocate_gen.py` — see `KNOWN_LIMITATIONS.md`, L-026).
Family (2) doesn't have an equivalent yet.

## Update — closed the same day (2026-06-19)

Family (2) now has a deterministic devil_advocate too, at
`results["abduction"]["devil_advocate"]` inside `vigia_agent.py`, right
before `_seal_bundle()` is called — same composer as family (1)
(`devil_advocate_gen.py`), with an honest `scope_note` explaining this path
never has pattern-match data to begin with.

Next concrete contribution, if you want one: confirm whether any evidence
type handled by `vigia_agent.py` could realistically reach
`vigia/sift/sift_orchestrator.py`'s `CasePatternLibrary` matching, and if
so, wire `missing_signals_by_pattern` through so this path gets the richer
counter-hypothesis instead of always falling back to "no pattern data
available."

## Why this happened

We're not hiding the duplication — a project that's honest about how it
grew is more useful to learn from than one that pretends it arrived fully
formed.
