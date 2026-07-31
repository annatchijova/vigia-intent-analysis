# VIGÍA — Epistemic Kernel

**Modules:** `vigia/core/ontology.py`, `vigia/core/reasoning/abduction.py`
**Tests:** `tests/test_epistemic_kernel.py`
**Status:** integrated, tested, deliberately **outside** the sealed verdict path.

---

## Attribution

This layer is not a Claude design. It is integrated here with its authorship intact.

| Contributor | Organization | Contribution |
|---|---|---|
| **Kimi** | Moonshot AI | Architecture and original implementation of both modules — the epistemic constitution (`ontology.py`) and the abductive tribunal (`abduction.py`). |
| **ChatGPT** | OpenAI | Design review of the previous revision (graded 8.5/10) that identified the residual forensic-engineering gaps, four of which are repaired below and two of which are recorded here as open questions. |
| **Claude** | Anthropic | Integration into the repository, repair of eight defects (D-1..D-8), determinism hardening, and the regression suite. |

### What Kimi actually contributed

The valuable part was not syntax. It was refusing to let categories collapse.

- **`Domain` as a typed enum** instead of a dictionary of arbitrary strings, so the
  ontology cannot be extended by typo.
- **`OriginKind` separated from `JustificationMode`.** "Where a claim was born" and
  "why we accept it as justified" are different dimensions. Merging them looks like
  a simplification and is a regression: it makes *"this claim was born from a
  formalization"* indistinguishable from *"this claim is justified by a formal
  proof."*
- **`TemporalScope` reframed as temporal coverage.** Temporal coverage is not
  temporal truth. A claim's interval covering an event says nothing about whether
  the claim is true of it.
- **Full canonical hashing** instead of a hash that ignored fields, so two
  conceptually distinct kernel states cannot collide.
- **Removal of implicit `utcnow()`** from auditable paths, so a snapshot is
  reproducible by a third party.
- **Removal of `EpistemicStatus`**, which silently mixed epistemic force with the
  engine's operational state, and its replacement by `HypothesisMode` (what kind of
  explanation this is) and `EvaluationState` (where it sits in the lifecycle).
- **`AbductivePattern`** as an intermediate layer between raw observation and
  generated hypothesis, so rules recognize patterns instead of degenerating into
  stimulus-response reflexes.

And the constraint the whole design exists to enforce:

> **An observation does not destroy a claim. It modifies the abductive space.**

That is the Peircean reading. A sign does not kill its object nor replace the
theory; it generates a possible inference, which must then enter a process of
evaluation. `AbductiveVerdict` accordingly has no refutation member, and the
registry has no delete.

### What ChatGPT actually contributed

Four findings that became repairs (D-3, D-4, D-8, and the ARCHIVED semantics), and
two that are recorded below as open design questions rather than silently
"resolved" by guessing at the maintainer's taxonomy.

---

## Scope: this layer does not decide anything

The epistemic kernel **generates hypotheses. It never produces a verdict, score, or
sealed output.** Nothing in the scoring pipeline imports it, and
`tests/test_epistemic_kernel.py::test_kernel_is_not_imported_by_the_scoring_pipeline`
fails if that changes.

This is deliberate, and it is the same invariant that keeps the LLM out of the
decision loop (`CLAUDE.md` Invariant 3, `docs/ENGINEERING_DISCIPLINE.md` §5.1). Mode
1's deterministic motor and its sealed bundles are unaffected by this integration:
no existing verdict changes, and no existing bundle hash moves.

Wiring this layer into the decision path would be an architectural decision for the
maintainer, taken deliberately and with corpus re-validation. It is not something to
do incidentally.

---

## Defects repaired on integration

The two files as received could not run. D-1 and D-2 are unconditional; the
remainder are correctness or determinism defects found while integrating. Each has a
regression test that fails if the fix is reverted (verified by mutation).

### D-1 — `TemporalCoverage` name collision made `assess()` always raise

`ontology.py` defined `TemporalCoverage` twice: first as the enum of coverage
results, then as the frozen dataclass holding the validity interval. The second
binding shadowed the first, so `assess()`'s `return TemporalCoverage.UNKNOWN`
resolved to the dataclass and raised `AttributeError` on every call.

This is the exact failure the design warns about, in the design itself: the interval
and the assessment of that interval are two categories that ended up sharing one
name.

**Fix:** the dataclass is `TemporalWindow`; the enum keeps `TemporalCoverage`. The
field on `OntologyClaim` and `Observation` is `temporal_window`. Both categories
survive, distinctly named.

### D-2 — `AbductivePattern` was a `TypeError` at import time

`causal_template: str` (no default) followed two defaulted fields, which Python
rejects when the dataclass is defined. `abduction.py` could not be imported at all.

**Fix:** required fields precede defaulted ones. No field was removed.

### D-3 — Generated hypotheses discarded their required-context key names

`_generate_hypothesis` built `required_context=tuple(ClaimContext() for _ in
rule.required_context)` — one *empty* `ClaimContext` per declared key. The count
survived; every name was thrown away. A hypothesis could report "I need two things"
without being able to say which two, which is precisely the information an audit
needs.

**Fix:** `Hypothesis.required_context_keys: Tuple[str, ...]` carries the declared
names.

### D-4 — Cascade invalidation was announced but not implemented

`OntologyRegistry.register()` built `_dependents` and documented it as supporting
cascade invalidation, but no traversal existed. A caller who questioned a
foundational claim would reasonably believe its dependents had been marked. They had
not.

**Fix:** `cascade_question(claim_id, reason, clock)` — breadth-first, dependents
visited in sorted `claim_id` order, returning the questioned ids in order.

Semantics chosen deliberately:
- Only `ACTIVE` claims are questioned. `SUPERSEDED`, `ARCHIVED` and `SUSPENDED` carry
  information that `QUESTIONED` would overwrite.
- An inactive claim does **not** sever the graph — dependents beyond it are still
  reached.
- Already-questioned claims are not re-questioned, which also terminates cycles.
- Cascaded entries record their origin in the history reason
  (`"... (cascade from c.root)"`), so the provenance of a status is auditable rather
  than inferred.

### D-5 — `ClaimGraph.dependents()` and `.dependencies()` were transposed

With `add_dependency(from_id, to_id)` read as "from depends on to", `dependents()`
returned the forward edge set and `dependencies()` the reverse one — each returning
the other's answer, and inverted relative to `OntologyRegistry._dependents`, which
is unambiguous. `subgraph()` consequently walked the graph backwards, extracting
what depends on the roots rather than what the roots need.

**Fix:** accessors aligned with the registry's reading; `subgraph()` walks real
dependencies. Both return sorted tuples — traversal order is contractual.

### D-6 — Claim hashing used a lossy authority representation

`_canonical_bytes` used `str(claim.authority)`, and `AuthoritySource.__str__` omits
`jurisdiction` and `url_or_ref`. Two authorities differing only in jurisdiction —
the same standard adopted in two countries — hashed identically.

**Fix:** `AuthoritySource.canonical_parts()` returns every field for hashing.
`__str__` remains the human label and remains deliberately lossy.

### D-7 — Canonical serialization was not injective

Fields were joined with `"|"`. A claim whose statement contains that separator can
produce the same byte string as a different claim with the field boundary elsewhere.
For a hash anchoring a forensic snapshot, "unlikely in practice" is not the standard.

**Fix:** length-prefixed encoding (`len:bytes` per field), which is unambiguous
regardless of content.

### D-8 — `ObservationPayload.value_type` was a free string

The permitted values existed only in a trailing comment. A payload whose encoding is
a typo is a payload whose meaning is unknown — and this value describes evidence.

**Fix:** `PayloadEncoding` enum (`RAW`, `HASH`, `CANONICAL`, `SIGNATURE`).

---

## Determinism hardening

The project's sealing invariants forbid non-reproducible ordering in anything that
may be serialized (`CLAUDE.md` Invariant 4).

- **Registry accessors return sorted tuples, not sets.** `by_domain()`, `by_layer()`
  and `dependents()` previously returned `Set[OntologyClaim]`. `OntologyClaim`
  hashes on `claim_id`, so set iteration order depends on `PYTHONHASHSEED` and
  varies between runs. `evaluate_all()` built its result dict from that order, so
  any downstream serialization of the mapping would have hashed differently run to
  run. `test_kernel_hash_is_stable_under_hash_randomization` runs the same kernel in
  three subprocesses with different seeds and requires one digest.
- **`suspend_runtime_prunable()`** iterates claims in sorted order, so its returned
  list and the resulting history are stable.
- **`EpistemicReport.evaluated_at` is required, not `default_factory=datetime.utcnow`.**
  The implicit clock read had survived in the report layer. Two runs over identical
  evidence produced two different reports, neither reproducible by a verifier.
  (`datetime.utcnow` is also deprecated from Python 3.12.)

## One behavioral change beyond defect repair

`AbductiveTribunal.evaluate()` already abstained when matching rules disagreed on
the verdict, then took `matches[0]`. Two rules that both say
`GENERATES_HYPOTHESIS` but propose *different explanations* passed that check, and
the first-registered one won silently — discarding a rival abduction, which is the
collapse this engine exists to prevent.

Agreement is now checked on the proposal as well as the verdict. This extends the
file's own stated rule ("if they disagree: ABSTAIN") to the level where the
disagreement actually lives; it does not introduce a new policy.

---

## Open design questions — deliberately not answered here

These are real, they come from the ChatGPT review, and answering them means
inventing taxonomy that belongs to the maintainer. They are recorded rather than
guessed.

1. **`ClaimContext.prerequisites` is still `FrozenSet[str]`.** "Typed to the bone"
   argues for an enum. But the admissible prerequisites of a forensic claim are
   domain facts, not engine concepts; enumerating them here would be inventing the
   ontology rather than representing it.

2. **`Hypothesis.statement` is still prose.** An auditable machine will eventually
   need a causal structure — cause / condition / effect nodes — with the prose
   *derived* from it rather than primary. That is a design decision with real
   consequences for every rule that generates a hypothesis, not a repair to make in
   passing.

3. **Missing-dependency policy — answered, and worth revisiting.** The review asked
   whether a missing dependency should block registration, produce an incomplete
   state, or remain an external reference. Implemented as: **registration is
   permitted, the claim stays `ACTIVE`, and the gap is enumerable** via
   `dangling_dependencies()`. Rationale: this registry never deletes and never
   judges, so refusing a registration would be a judgement, and accepting a phantom
   edge silently would be the dishonest option. Making the gap queryable lets the
   caller decide and lets an audit see what the kernel does not know. If the
   maintainer wants a strict mode, this is where it goes.

4. **`AssessmentMatrix` has no builder.** Callers construct cells themselves. A
   deterministic `evaluate_all -> AssessmentMatrix` helper is an obvious
   convenience, but it is new API rather than integration, so it was not added.

---

## A note for whoever refactors this next

The complexity in these two modules is not accidental; it is the representation of
the domain. A model or engineer optimizing for "fewer classes, less indirection" can
produce something that looks cleaner and is conceptually a regression — it will not
break the program, it will break the meaning, which is worse because nothing fails.

These separations are load-bearing:

```
authority            != evidence
observation          != interpretation
interpretation       != hypothesis
hypothesis           != verdict
operational state    != epistemic force
origin of a claim    != justification of a claim
temporal coverage    != temporal truth
```

The test of having understood this layer is not adding classes or removing them. It
is being able to state **which error becomes unrepresentable if a given class is
deleted.** If you cannot name that error, the class is load-bearing and you have not
finished reading.
