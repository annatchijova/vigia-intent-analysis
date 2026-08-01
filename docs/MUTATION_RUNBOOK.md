*English · [Español](./MUTATION_RUNBOOK_ES.md)*

# Mutation testing runbook — operation and failures

A **self-contained** document. It is written so that any person or agent
arriving with no prior context can run, read and repair the mutation sweep
without asking anyone.

- **What it is and why**: `docs/MUTATION_TESTING.md`
- **Measured results and triage**: `docs/MUTATION_BASELINE.md`
- **This document**: how it is operated and what to do when it fails.

Every failure in §3 **actually happened** while building this on 2026-08-01.
They are not hypotheticals: they are the record of what broke, how it was
diagnosed and how it was fixed.

---

## 1. Normal operation

Nothing to do. `.github/workflows/mutation.yml` runs by itself every **Monday
at 03:00 UTC**: one job per module, in parallel.

To read the result: **Actions** tab → *VIGÍA Mutation Testing* run. Each job
writes its summary:

```
killed=172 survived=250 total=422 score=40%
```

Each job also publishes a `mutation-<module>` artifact with two files:

| File | Contents |
|------|----------|
| `survivors.txt` | Survivors only. **This is the work list.** |
| `all.txt` | Every mutant with its status. Use it to re-count. |

To trigger it manually: **Actions → VIGÍA Mutation Testing → Run workflow**.
The `only_mutate` field takes one module path (e.g. `vigia_scorer.py`); leave
it empty to measure all of them.

### How to read it without getting it wrong

1. **Compare the total, not only the percentage.** With
   `mutate_only_covered_lines = true`, writing tests **enlarges** the mutant
   universe: previously uncovered lines become mutable. In the first baseline
   `collapse_decision.py` went from `4/29` to `35/35` — numerator and
   denominator moved together.
2. **A survivor is not always a defect.** Three classes, and separating them is
   the real work: genuine test gap / equivalent mutant (does not alter
   observable behaviour) / unreachable defensive branch. See
   `MUTATION_TESTING.md` §7.
3. **A low score does not mean bad code.** It means "weak tests in that area".

---

## 2. Running it locally

### 2.1 Environment from scratch

```bash
pip install -r requirements.txt -r requirements-ci.txt
pip install scipy mutmut
```

**Install `requirements.txt` in full.** If the modules importing
`vigia/vigia_sift_bridge.py` fail to collect with
`ModuleNotFoundError: No module named 'mcp'` — or worse, with
`TypeError: issubclass() arg 1 must be a class` — the cause is almost certainly
a missing `fastmcp`, not an `mcp` version problem. Installing `mcp` on its own
and hunting versions is a dead end: several 1.x releases fail on PEP 604
annotations and 2.x dropped `mcp.server.fastmcp` entirely. `fastmcp` pulls a
compatible pair.

If `pip install` fails with `Cannot uninstall PyJWT ... RECORD file not found`,
the interpreter has PyJWT from the system package manager
(`KNOWN_LIMITATIONS.md` L-045). Two ways out:

- use a clean virtualenv (recommended), or
- `pip install --ignore-installed PyJWT fastmcp`.

These modules are excluded from the mutation runner anyway, because they cover
the MCP surface and not the verdict path — but the full suite needs them to
collect, and CI runs the full suite as its green-baseline gate.

### 2.2 Prerequisite — a green suite

```bash
python3 -m pytest tests/ vigia/tests/ -q --tb=short --no-cov
```

**Over a red suite the mutation score means nothing**: every mutant is declared
killed by the pre-existing failure and the result comes out at ~100 %. The
workflow has a `baseline` job that checks this before mutating. Locally it must
be checked by hand.

### 2.3 Sweep

```bash
python3 -m mutmut run --max-children 4   # note: all 8 modules is ~6 hours
python3 -m mutmut results                # survivors
python3 -m mutmut results --all true     # all, with status
python3 -m mutmut show <mutant_name>     # the exact diff of one mutant
```

### 2.4 Narrowing to one module

**`mutmut run <pattern>` does NOT narrow anything** — verified: with five
module patterns it ran all 7,043 mutants anyway. The only mechanism that works
is `only_mutate` in `pyproject.toml`. The cycle:

1. edit `only_mutate`, leaving only the desired module;
2. `rm -rf mutants && python3 -m mutmut run --max-children 4`;
3. **restore `pyproject.toml`** as soon as generation finishes — the `mutants/`
   sandbox already has its own copy and does not read it again.

Step 3 matters: `tests/test_mutation_config_contract.py` requires
`vigia_scorer.py` to stay in `only_mutate`, so a forgotten narrowing leaves the
suite red. That is deliberate — the contract exists so that a temporary
narrowing does not silently become the permanent scope.

### 2.5 Disk space

`mutants/` takes **~300 MB** with all 8 modules (137 MB for the mutated scorer
alone: mutmut writes every variant inline). It is in `.gitignore`. It can be
deleted at any time; the only cost is regenerating it.

---

## 3. Known failures

### 3.1 `failed to collect stats. runner returned 1`

**What it means.** Before mutating, mutmut runs the whole suite to map which
test covers which function. It runs with `-x`: **a single failing test aborts
the entire sweep**. The message does not say which one.

**How to find the culprit.** The log shows the `FAILED` just above the
traceback. If it does not appear, turn on verbose mode by adding `debug = true`
to the `[tool.mutmut]` section of `pyproject.toml`, re-run, and **remove it
afterwards** (it prints the entire suite).

**Causes seen, in order of frequency:**

**a) Tests that inspect source text instead of exercising behaviour.** Inside
`mutants/`, the source contains *every* mutant variant inline
(`x_funcname__mutmut_N`, literals wrapped as `"XXFOOXX"`). A test doing regex
over `caie.py`, `inspect.getsource`, or `rglob` of `*.md` reads harness
artefacts and fails for a reason that is not the logic under test. Four are
already excluded for this (`MUTATION_TESTING.md` §5). **If a new one appears:
exclude it only if it cannot kill any mutant in `only_mutate`** — that is, if
it does not execute that code. If it does, excluding it falsifies the score and
the test must be fixed instead.

**b) Missing data files.** If the suite fails inside `mutants/` with
`FileNotFoundError`, something is missing from `also_copy`. Add it. The
dangerous symptom is the opposite one: if this goes unnoticed, **every** mutant
is declared killed and the score comes out at a false 100 %.
`tests/test_mutation_config_contract.py` covers this.

**c) A failure that only occurs under mutmut.** See §3.4.

### 3.2 `BadTestExecutionCommandsException` / pytest exits with code 4

**What it means.** pytest exit code 4 = usage error. Almost always: mutmut
passed a test identifier that no longer resolves (`ERROR: not found: ...`).

**Real case and its root cause.** It happened because
`tests/caie/test_canonical_cases.py` passed a **generator** to
`@pytest.mark.parametrize`. A generator is exhausted when consumed and the
object is captured in the marker, at module level. mutmut collects several
times in the same process (`list_all_tests`, `stats`, `clean run`), so the
second collection received an empty generator: the 52 canonical cases ceased to
exist and their identifiers did not resolve.

**How to diagnose it:** `debug = true` in `[tool.mutmut]` makes pytest's real
error print, naming the identifier that does not resolve.

**Active prevention:** `tests/test_parametrize_argvalues_are_reiterable.py`
closes this class — including an AST sweep against generator expressions used
as `argvalues`. If that test fails, the defect is back.

### 3.3 The suite turns red *after* running mutmut

Symptom: tests that used to pass start failing without any code being touched.

**Cause:** `mutants/` exists, and some test sweeps the whole tree
(`grep -r .`, `rglob`) counting the mutated copy as repository code. It
happened with `test_b117_stale_formula_sweep` and — more seriously —
`test_b224_contradiction_detector_dormancy`, whose sole purpose is to assert
that a given rule has no producer *anywhere in the repository*: it counted
`mutants/vigia_agent.py` as a new producer.

**Fix:** add `--exclude-dir=mutants` to the `grep`, or `"mutants" not in
p.parts` to the `rglob`. There are three precedents in the tree.

**Diagnostic shortcut:** `rm -rf mutants` and re-run. If it goes green, this
was it.

### 3.4 A test fails only inside mutmut and does not reproduce outside

Before excluding anything, check the five contexts — this is how a harness
problem was told apart from a real defect:

| Context | Command |
|---------|---------|
| Isolated, in the sandbox | `cd mutants && pytest <test_path>` |
| Isolated, with the stats environment | `MUTANT_UNDER_TEST=stats MUTMUT_DEPENDENCY_DEPTH=-1 pytest <path>` |
| Full suite, subprocess | `cd mutants && pytest <full selection>` |
| Full suite, **in-process** | `python3 -c "import os,pytest; os.chdir('mutants'); pytest.main([...])"` |
| Real mutmut | `python3 -m mutmut run` |

The fourth is closest to mutmut: it runs pytest **inside the same process**,
which is where failures from global state that does not survive a second
collection appear. If it fails there, it is a real defect of the suite (this
was the generator case, §3.2). If it only fails in the fifth, it is an
interaction with the harness.

**Open anomaly:** `vigia/tests/test_lr_calibrator_serialization.py` fails only
under the `stats` phase (2 of 2 runs) and passes in the other four contexts.
Undiagnosed. Excluded, with the full reasoning in `MUTATION_TESTING.md` §5.1.
**If someone diagnoses it, update that section and remove the exclusion.**

### 3.5 The CI job is cancelled on time

The **hard** limit for a job on GitHub Actions is 360 minutes; it cannot be
raised.

To re-size after adding modules, with the measured rate (19.5 mutants/min with
`--max-children 4` on 4 CPU):

```
mutants ≈ (number of lines containing "__mutmut_" in mutants/<module>) × 0.49
minutes ≈ mutants / 19.5
```

All 8 modules in a single job is ~359 min: **they do not fit**. That is why the
workflow uses `strategy.matrix` with one job per module.
`tests/test_mutation_config_contract.py` verifies that the timeout stays under
360 and that the matrix covers exactly `only_mutate` — two lists that must
match drift apart on their own, and a module declared but missing from the
matrix would never be measured without anything failing.

---

## 4. How to widen the scope

1. Raise the module's **line coverage** first. Mutating untested code produces
   trivial survivors and only adds triage noise.
2. Add it to `only_mutate` in `pyproject.toml`.
3. Add it to `strategy.matrix.module` in `.github/workflows/mutation.yml`. The
   contract fails if this step is forgotten.
4. Recompute the time with the formula in §3.5.
5. Measure, triage, and record the result in `docs/MUTATION_BASELINE.md`.

## 5. How to remove all of this

If it is ever decided that it is not worth it, the **whole set** must go, not
just the tool:

- `[tool.mutmut]` in `pyproject.toml`
- `.github/workflows/mutation.yml`
- `tests/test_mutation_config_contract.py`
- `docs/MUTATION_TESTING.md`, `docs/MUTATION_BASELINE.md`, this file, and their
  `_ES` counterparts
- the `mutants/`, `.mutmut-cache`, `mutmut-stats.json` entries in `.gitignore`

**Do not remove** `tests/test_parametrize_argvalues_are_reiterable.py`,
`tests/test_collapse_decision_boundaries.py`, or the `--exclude-dir=mutants`
guards: they are fixes for real repository defects, independent of the tool
that exposed them.
