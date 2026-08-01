*English · [Español](./MUTATION_BASELINE_ES.md)*

# Mutation testing baseline — 2026-08-01

First measurement. Method, scope and limitations: `docs/MUTATION_TESTING.md`.

**Tool:** `mutmut` 3.7.0 · **Python:** 3.11.15 · **Base commit:** `3bf7a8e`
**Reference suite:** 2042 passed, 0 failed (excluding modules requiring `mcp`, L-045)

---

## 1. What was measured — and what was not

**3 of the 8 modules** in `only_mutate` were measured:

| Module | Measured |
|--------|----------|
| `vigia/collapse_decision.py` | yes |
| `vigia/core/likelihood_engine.py` | yes |
| `vigia/core/decision_layer.py` | yes |
| `vigia_scorer.py` | **no** |
| `vigia/tools/caie.py` | **no** |
| `vigia/core/semiotic_detector_v2.py` | **no** |
| `vigia/core/evidence_aggregator.py` | **no** |
| `vigia/core/causal_closure.py` | **no** |

**Why not all eight.** The full sweep generates 7,043 mutants. Rate measured on
this machine (4 CPU, `--max-children 4`): **19.5 mutants/min**, i.e. **~5.3
hours**. A sweep interrupted halfway is not a baseline: the number would depend
on where it stopped. A **complete measurement of a declared scope** was
preferred. The remaining five are the weekly job's work
(`.github/workflows/mutation.yml`).

The figures below hold **for those three modules**. They are not VIGÍA's
mutation score and must not be cited as such.

---

## 2. Result — initial run

| Module | Killed | Survived | Total | Score |
|--------|-------:|---------:|------:|------:|
| `vigia/collapse_decision.py` | 4 | 25 | 29 | **13.8 %** |
| `vigia/core/decision_layer.py` | 96 | 131 | 227 | **42.3 %** |
| `vigia/core/likelihood_engine.py` | 72 | 94 | 166 | **43.4 %** |
| **TOTAL** | **172** | **250** | **422** | **40.8 %** |

Worst hot spots by function:

| Score | Killed / Surv | Function |
|------:|--------------:|----------|
| 0.0 % | 0 / 14 | `CollapseDecisionLayer.explain` |
| 26.2 % | 17 / 48 | `RiskBoundedDecisionLayer._generate_reason` |
| 26.7 % | 4 / 11 | `CollapseDecisionLayer.resolve` |
| 28.6 % | 6 / 15 | `RiskBoundedDecisionLayer.__init__` |
| 35.7 % | 41 / 74 | `LikelihoodEngine.infer` |
| 50.9 % | 59 / 57 | `RiskBoundedDecisionLayer.decide` |
| 56.0 % | 14 / 11 | `decision_layer._decide` |
| 62.0 % | 31 / 19 | `LikelihoodEngine.__init__` |

---

## 3. Triage — `vigia/collapse_decision.py`

The only module triaged mutant by mutant in this first pass.

**Line coverage: 77.94 %. Mutation score: 13.8 %.** This is the textbook
demonstration of what the metric is for: the lines were executed, the behaviour
was not verified.

Of the 25 survivors, **none turned out to be equivalent**. All 25 were real
gaps. Breakdown derived from the diffs, one by one:

| Class | # | Example |
|-------|--:|---------|
| Compared string (rule sentinel) | 8 | `"sensor_independence"` → `"XXsensor_independenceXX"` |
| Comparison operator | 9 | `>=` → `>`, `<` → `<=`, `in` → `not in`, `==` → `!=` |
| Numeric threshold constant | 5 | `base_score >= 0.5` → `>= 1.5` |
| Returned string (narrative text) | 3 | `"Standard verdict"` → `"STANDARD VERDICT"` |
| **Total** | **25** | |

The three findings that weigh most:

**Sentinels.** `"sensor_independence"` → `"XXsensor_independenceXX"` survived.
That comparison is the module's declared key rule ("any break of
`sensor_independence` → INCONCLUSIVE"). Nobody checked that the rule fires with
the string actually in use.

**Thresholds.** `base_score >= 0.5` → `>= 1.5` survived: the MALICE threshold
could be moved to an unreachable value with nothing failing.

**Operators.** They change the verdict exactly at the cut-off point, which is
where a forensic decision is decided.

### Correction

`tests/test_collapse_decision_boundaries.py` — 22 tests, each aimed at named
mutants.

| | Before | After |
|---|---:|---:|
| Killed | 4 | **35** |
| Survived | 25 | **0** |
| Total | 29 | 35 |
| Score | 13.8 % | **100 %** |

**The denominator rose from 29 to 35, and that is correct**, not a counting
error: `mutate_only_covered_lines = true` only mutates lines some test
executes. The new tests cover lines nobody touched before, so those lines
become mutable. Raising coverage **enlarges** the mutant universe. Comparing
scores across runs requires checking the denominator too.

### The discipline it imposed

You must land on the **exact cut-off point** (0.5, 0.2, 0.3, `len == 2`), not a
comfortable value in the middle of the interval. A test with `base_score = 0.9`
passes whether the threshold is 0.5 or 0.8: it does not discriminate, therefore
it kills nothing. That is precisely the difference line coverage cannot see.

---

## 4. Outstanding

- Triage of the 131 survivors in `decision_layer.py` and the 94 in
  `likelihood_engine.py`. Hot spots are in §2; unlike `collapse_decision`,
  equivalent mutants are to be expected here (defensive branches, `__init__`
  with default values), and they must be separated out before writing a single
  test.
- Measurement of the remaining 5 modules, including `vigia_scorer.py`. Weekly
  job's work.

---

## 5. Defects found while building the measurement

They are not part of the score, but they are the real yield of this first pass.
All four belong to the same family: **tests that inspect the repository instead
of exercising behaviour break, or lie, when a second copy of the tree exists.**

| Defect | Commit |
|--------|--------|
| **Canonical corpus that silently evaporated.** `tests/caie/test_canonical_cases.py` passed a generator to `@pytest.mark.parametrize`. A generator is consumed once and the object is captured in the marker: in any process that collects twice, the second collection yields **zero** parameters and the 52 canonical cases cease to exist — not as a failure, as an absence. pytest was already warning about it (`PytestRemovedIn10Warning`) and it would have stopped working in pytest 10. | `ef1201b` |
| **Tree sweeps that counted the sandbox.** `test_b224_contradiction_detector_dormancy` asserts that a given rule has no producer *anywhere in the repository*; with `mutants/` present it counted the mutated copy of `vigia_agent.py` as a new producer. A sweep that does not tell repository code from a build directory does not support the claim it says it supports. Same in `test_b117_stale_formula_sweep` and, latently, in `test_requirements_ci_contract`. | `1a5638a` |
| **The config contract itself, inside the sandbox.** `test_mutation_config_contract` validates the declared scope by reading `pyproject.toml`; inside `mutants/` it read the narrowed copy and failed against a deliberate narrowing. The test is correct; the sandbox is not its place. | `624bd41` |
| **Open anomaly**, undiagnosed: `test_lr_calibrator_serialization` fails only under mutmut's `stats` phase (2 of 2) and passes in the other four contexts tried. See `MUTATION_TESTING.md` §5.1. | `7403e71` |

---

## 6. Harness limitation

`mutmut run <pattern>` accepts mutant-name filters, but passing them **did not
narrow the sweep**: it ran all 7,043 anyway. The mechanism that does work is
`only_mutate` in `pyproject.toml`, which is what `mutation.yml`'s
`workflow_dispatch` uses. Narrowing by hand requires the cycle: edit
`only_mutate` → launch → wait for generation to finish → restore the config
(the sandbox keeps its own copy).
