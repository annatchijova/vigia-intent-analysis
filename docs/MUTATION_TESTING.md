*English · [Español](./MUTATION_TESTING_ES.md)*

# Mutation Testing — VIGÍA

**Status:** infrastructure active. Scope: the sealed-verdict path.
**Tool:** `mutmut` 3.7. **Configuration:** `[tool.mutmut]` in `pyproject.toml`.

---

## 1. What it measures, and why it is not coverage

Mutation testing does not test the code: it tests **the test suite**. It injects
a small, deliberate defect into the source — a *mutant* — and runs the tests
against that broken version.

- If some test fails, the mutant is **killed**. The suite detects that change
  in logic.
- If every test passes, the mutant **survives**. A real behavioural change
  exists that nobody notices.

**Mutation score = mutants killed / mutants executed.**

The operational distinction against line coverage:

| Metric | Question it answers |
|--------|---------------------|
| Line coverage | Was this line **executed** during the tests? |
| Mutation score | Was it **verified**? If I break it, does anything fail? |

A line can sit at 100 % coverage and 0 % mutation score: if a test runs it but
makes no assertion about its effect, the line is *visited*, not *verified*.

## 2. Why VIGÍA in particular

Three reasons specific to this project, not generic ones:

1. **The verdict path is threshold arithmetic.** `vigia_scorer.py` is ~1,900
   lines of comparisons, `Fraction`, lookup tables and gates
   (`n_artifacts < 2`, `_n_domains >= 2 and (_n_gate_arts >= 4 or ...)`). This
   is code where the mutated operator **is** the business logic. An off-by-one
   here does not crash: it emits a different verdict, and seals it.
2. **The Daubert bar.** If a MALICE verdict can end up in a courtroom, "the
   tests pass" is a weaker claim than it looks. The mutation score is the
   evidence that the suite **discriminates**, not merely that it exists.
3. **Agent-assisted development.** It is the most direct defence against the
   failure that `docs/ENGINEERING_DISCIPLINE.md` and surgical-patching
   discipline try to prevent: a model rewrites more than it intended and the
   suite approves it.

## 3. How to run it

```bash
# Full sweep of the configured scope (long — see §6).
python3 -m mutmut run --max-children 4

# Results: summary and list of survivors.
python3 -m mutmut results

# See the exact diff of one mutant.
python3 -m mutmut show <mutant_id>

# Re-test a single mutant after writing a test that should kill it.
python3 -m mutmut run <mutant_id>
```

`mutmut` copies the source into `mutants/` and injects there. **`mutants/` is
never committed** (`.gitignore`): it holds verdict-path code with deliberate
defects injected — the same class of hazard as the `tests/unit/test_m4_floor.py`
benchmark, and therefore the same treatment.

## 4. Scope — and why it is deliberately narrow

`only_mutate` in `pyproject.toml` lists the mutated modules:

| Module | Line coverage (2026-06-22 baseline) |
|--------|--------------------------------------|
| `vigia_scorer.py` | root verdict path |
| `vigia/tools/caie.py` | 69.55 % |
| `vigia/core/semiotic_detector_v2.py` | 80.94 % |
| `vigia/core/evidence_aggregator.py` | 92.50 % |
| `vigia/core/likelihood_engine.py` | 88.68 % |
| `vigia/core/decision_layer.py` | 86.30 % |
| `vigia/core/causal_closure.py` | 82.76 % |
| `vigia/collapse_decision.py` | 77.94 % |

**Admission criterion: tests must already exist that can bite.** Mutating a
module at 0 % coverage teaches nothing that coverage does not say more cheaply
— the mutant survives trivially and only adds triage noise. With the repository
total at 19.16 %, mutating everything would be mostly noise.

`mutate_only_covered_lines = true` applies the same criterion per line.

Widening the scope means adding modules to `only_mutate` **after** raising
their coverage, not before.

## 5. Tests that are invisible to mutation

Four test modules are excluded from the runner's selection
(`pytest_add_cli_args_test_selection`) for a structural reason, not for
convenience:

- `tests/test_m3_scorer_caie_parity.py`
- `tests/test_registry_integrity.py`
- `tests/test_requirements_ci_contract.py`
- `tests/test_security_md_rate_limit_contract.py`

They are **repo-meta** tests: they do not exercise the verdict path, they
**inspect source text** (regex over `caie.py`, `inspect.getsource`, `rglob` of
`*.md`). Inside `mutants/` the source contains every mutant variant inline
(`x_funcname__mutmut_N`, literals wrapped as `"XXFOOXX"`), so these tests read
harness artefacts and fail for a reason that is not the logic under test.

**They cannot kill a mutant in `only_mutate`** — they do not invoke that code —
so excluding them does not change the score. It is a finding in its own right:
*a test that inspects source instead of exercising behaviour is structurally
invisible to mutation*. It contributes to repository consistency, not to
verification of logic.

Modules importing `vigia/vigia_sift_bridge.py` are also left out. The
load-bearing reason is that they cover the MCP surface, **not** the verdict
path: no mutant in `only_mutate` depends on them, so excluding them does not
change the score.

*Correction (2026-08-01):* this was first justified as "they do not collect
without `mcp`". That was an environment failure, not a repository one — the
missing piece was `fastmcp`, declared in `requirements.txt`, which resolves the
import. With `requirements.txt` fully installed they collect and pass (full
suite: 2176 passed). `KNOWN_LIMITATIONS.md` L-045 describes a narrower case
than was assumed here.

### 5.1 Open anomaly — `test_lr_calibrator_serialization.py`

`vigia/tests/test_lr_calibrator_serialization.py::test_sklearn_backend_roundtrip_matches_before_save`
is excluded for a different reason and **with no confirmed diagnosis**.

Observed (2026-08-01):

| Context | Result |
|---------|--------|
| mutmut `stats` phase | **FAILS** (2 of 2 runs) |
| Isolated, inside `mutants/` | passes (5 passed) |
| Isolated, with `MUTANT_UNDER_TEST=stats` | passes |
| Full suite in a subprocess, inside `mutants/` | passes (2016 passed) |
| Full suite replicating mutmut's **in-process** invocation, same env vars | passes (2023 passed) |

The residual difference not isolated: mutmut runs `list_all_tests`
(`--collect-only`) and then `stats` **in the same process**, with its
`StatsCollector` plugin registered. It has not been confirmed that this is the
mechanism.

Why it is worth recording even though it is excluded: the test is deterministic
in its input (`_synthetic_z_scores(seed=42)`, a local `random.Random`, the
`lbfgs` solver) and what it compares is a `to_dict()`/`from_dict()` round trip
with `abs_tol=1e-6`. A float equality over a serialisation should not depend on
which process runs it. Since this repository treats determinism as a hard
invariant (Invariant 4, `Fraction` at `prec=28`), it is recorded rather than
buried.

It is excluded because mutmut runs with `-x`: the failure aborts the stats
phase and with it the whole sweep. `LRCalibrator` is not in `only_mutate`, so
this module cannot kill any mutant in scope and its exclusion does not change
the score.

## 6. Cost

It is N runs of the suite, one per mutant. With the in-scope suite at ~3.5 min
and several hundred mutants, a full sweep is hours of work. `mutmut` mitigates
with per-function test selection (`track_dependencies`) and a result cache
between runs.

**This is not a pre-commit check.** It is a nightly or release task.

## 7. How to read a survivor

A surviving mutant falls into one of three categories. Triage is manual and is
the part that does not automate:

1. **Genuine test gap.** The logic changed and nobody noticed. Write the test
   that kills it.
2. **Equivalent mutant.** The change does not alter observable behaviour
   (`x = x + 0`, a redundant guard, an unreachable defensive branch). It is not
   a defect of the suite and cannot be killed. Document it.
3. **Dead / defensive code.** The branch is not reachable today. See
   `tests/test_b151a_single_artifact_cap.py`, which pins precisely the
   unreachability of the single-artifact cap: over that branch nearly every
   mutant survives, correctly.

Reporting a mutation score without separating (1) from (2) and (3) inflates or
deflates the figure at will. The triage record lives in §8.

## 8. Run log

See `docs/MUTATION_BASELINE.md` for the reference run, the per-module score and
the survivor triage.

**When comparing two runs, check the denominator as well.** With
`mutate_only_covered_lines = true`, raising coverage **enlarges** the mutant
universe: new tests cover lines nobody touched before, and those lines become
mutable. In the first baseline `collapse_decision.py` went from 4/29 to 35/35 —
numerator and denominator moved together, and reading only the percentage would
have hidden half of what happened.

## 9. Declared limitations

- **Does not apply to the LLM layer.** `reason_with_llm` and the narrative are
  not deterministic; there is no stable oracle to kill mutants.
- **The score depends on the scope.** A high score over 8 hand-picked modules
  says nothing about the ~170 others. The figure must always be cited with its
  `only_mutate`.
- **Excluding the MCP and repo-meta tests is a declared caveat of the score**,
  stated here and in the `pyproject.toml` comments, not a silent omission.
