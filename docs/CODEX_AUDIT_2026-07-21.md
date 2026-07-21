# Codex audit — 2026-07-21

**Branch:** `codex`
**Restore point:** `pre-codex-vigia-audit-20260721`
**Scope:** pending limitations, live scorer boundaries, and the experimental
FastAPI wrappers. This is an audit record, not a claim that every documented
limitation is a newly discovered defect.

## Method

The review applied all twenty documented governance skills: abductive
engineering, red-team auditing, secure-by-construction, software archaeology,
diagnosing bugs, codebase health assessment, reverse engineering,
Daubert-defensible writing, deterministic core, LLM out of the loop,
tamper-evident audit chain, atomic state mutation, versioned schema evolution,
surgical patcher, audit before patch, validate at the boundary, honest
degradation, SQL aggregation not materialization, git discipline, and claim
provenance discipline.

No product code was patched before the documented state, live callers, and a
bounded reproduction were checked.

## C-01 — FastAPI case-path escape [RESOLVED on `codex`]

**Severity:** P1 *when either FastAPI wrapper is exposed to an untrusted
network*. It has no remote attacker if the wrapper is not running or is
independently restricted to loopback/private infrastructure.

### Code facts

Both wrappers accept `CasePath.case_path` and use it directly:

```python
case_path = REPO / payload.case_path
if not case_path.exists():
    raise HTTPException(404, ...)
pipeline = _run_pipeline(case_path)
```

- `vigia_api.py:251-263`
- `vigia/vigia_api.py:112-124`

`pathlib.Path` discards the left operand when the right operand is absolute.
Neither wrapper rejects absolute paths, `..`, symlinks, directories, or paths
outside the declared case locations. The selected path is passed to
`_run_pipeline()`, which opens and parses it, and then to optional narration
after a successful analysis.

There is no request authentication. The package wrapper allows all CORS
origins, and both startup blocks default to `0.0.0.0`. CORS is a browser
policy, not authentication. The repository's technical-state document itself
says HTTP without authentication is an unacceptable attack surface; its MCP
transport guard does not protect these REST routes.

### Controlled induction

No server was opened and no personal data was read. Each wrapper was imported
in-process; `_run_pipeline` and `_run_narrative` were replaced with inert
stubs. Supplying the existing outside path
`/tmp/vigia-forge-codex-audit/cronos.sqlite3` produced:

```text
root_wrapper    accepted_outside=True
package_wrapper accepted_outside=True
```

This proves the path-boundary failure. It does **not** prove arbitrary-file
content exfiltration: the real pipeline expects a case-shaped JSON document,
and output depends on its schema and deployment configuration.

### Impact

An unauthenticated reachable client can request an existing readable,
case-shaped JSON file outside the intended VIGÍA case directories. This
violates the documented endpoint contract and contaminates case scope and
chain-of-custody, even where no secret is returned verbatim.

### Remediation — implemented on `codex`

`vigia/api_case_paths.py` now supplies one pure shared resolver for both
wrappers. It rejects absolute paths and raw `..`, restricts selection to
`data/cases/` and `cases/`, and requires a regular non-symlink `.json` file.
The endpoint maps every resolver failure to the same 404 so it is not a local
path oracle. Both startup paths now default to `127.0.0.1`; both file-backed
pipelines validate and normalize case JSON before scoring. The 15 direct API
regressions cover allowed input, absolute and traversal attempts, prefix-like
relative path, symlink, directory, wrong extension, scalar chat JSON, and the
package-root default. The 38 end-to-end tests also pass.

Authentication remains a product/deployment decision for any deliberate
non-loopback bind. This patch makes that exposure opt-in; it does not pretend
an invented authentication scheme is a reviewed access policy.

## C-02 — OpenAI-compatible chat crashes on scalar JSON [RESOLVED on `codex`]

**Severity:** P3 availability/protocol degradation. No scorer decision or
evidence is changed; a single malformed-but-valid chat request receives a
server error instead of the endpoint's normal usage guidance.

`vigia_api.py:146-212` parses the last user message with `json.loads(text)`
and then immediately evaluates `"artifacts" in case_data`. JSON scalars such
as `42` and `null` parse successfully but are not containers, so that membership
test raises an uncaught `TypeError`. `ChatRequest.messages` is an untyped list,
so this boundary does not reject or normalize message content first.

Controlled direct calls, without a server or pipeline execution:

```text
'42'  -> TypeError: argument of type 'int' is not iterable
'null' -> TypeError: argument of type 'NoneType' is not iterable
'[]'   -> normal usage guidance
```

The root wrapper now accepts only a JSON object with `artifacts` for
forensic-case handling. Scalars, lists, `null`, invalid JSON, and non-text
message content return usage guidance rather than a server error. A valid
object still reaches the inert test pipeline. The package wrapper has no
OpenAI-compatible chat route, so C-02 remains root-wrapper specific.

## C-03 — PathGuard allowlist accepts prefix collisions and `..` escapes [CONFIRMED]

**Severity:** P1 forensic-integrity boundary. This is not remote code execution;
it becomes exploitable when a caller can supply a path to a SIFT input. It can
make the live SIFT pipeline read evidence outside the configured allowlist,
which is precisely the boundary the guard claims to enforce.

`vigia/core/path_guard.py:89-93` authorizes a path with a raw string prefix:

```python
allowed = any(str(abs_path).startswith(str(base)) for base in self._allowed)
```

That is not a directory-containment relation. With allowed base `/tmp/vigia`,
the sibling `/tmp/vigia-forge-codex-audit/cronos.sqlite3` passes. A second
controlled probe, using
`/tmp/vigia-forge-codex-audit/../vigia-codex-pytest.log` under base
`/tmp/vigia-forge-codex-audit`, also passed despite resolving outside the base.

This is not only a validation-reporting error. `safe_open()` validates and then
calls `os.open()` using the same unnormalized path (`path_guard.py:212-232`).
Against the controlled SQLite file outside `/tmp/vigia`, `safe_open()` actually
opened a nonempty regular file. No content was emitted. The focused existing
PathGuard tests passed 6/6 because they cover a plainly outside path and valid
directories, not prefix collision or `..` cases.

The guard is instantiated by `vigia/sift/sift_orchestrator.py:223` and its
`_safe_path()` result is passed to memory, registry, event-log, prefetch,
browser, USB, and shellbag engines. `vigia_agent.py` builds those inputs from
the selected evidence path. C-03 is therefore distinct from the FastAPI
wrapper finding and affects the forensic acquisition layer.

### Remediation — implemented on `codex`

`PathGuard` now rejects raw `..` components before authorization and compares
the lexically normalized candidate against lexically normalized trusted roots
by path component. A sibling such as `/tmp/vigia-evil` is no longer a
descendant of `/tmp/vigia`. `safe_open()` uses the same representation, while
the existing symlink, regular-file, descriptor `fstat`, lock, and post-read
TOCTOU checks remain intact. `tests/test_path_confinement_regression.py`
covers the former prefix collision, traversal vector, positive in-root read,
and `safe_read` rejection. Root-policy review remains a separate product
decision.

## C-04 — Memory and registry engine allowlists fail open [CONFIRMED]

**Severity:** P1 defense-in-depth and direct-consumer boundary. The standalone
memory and registry interfaces advertise allowlist enforcement but accept any
existing path outside their roots.

Both `Volatility3Interface._validate_path()`
(`vigia/sift/memory_forensics.py:313-322`) and
`RegRipperInterface._validate_path()`
(`vigia/sift/registry_timeline_reconstructor.py:176-182`) compute a proper
component-aware `allowed` boolean. Their rejection block, however, raises only
when the path is outside **and does not exist**:

```python
if not allowed:
    if not p.exists():
        raise FileNotFoundError(...)
return p
```

The default roots include `/tmp/vigia` but not
`/tmp/vigia-forge-codex-audit`. With the controlled existing SQLite fixture
outside every declared root, both validators returned that outside path:

```text
memory_validator_returns_outside=True
registry_validator_returns_outside=True
```

This is separate from C-03. SIFT normally puts PathGuard in front of these
engines, but C-03 can bypass that layer, and direct Python consumers can call
the interfaces without it. The intended “if no allowlist is configured”
fallback was not implemented: the defaults ensure an allowlist is always
configured.

### Remediation — implemented on `codex`

Both interfaces now delegate their input boundary to `PathGuard` configured
with their own `ALLOWED_BASE_PATHS`. An existing outside path raises
`PermissionError`; a missing path remains `FileNotFoundError`; traversal,
symlink, and non-regular-file rejections remain explicit. The same regression
module covers both engine interfaces for an existing outside fixture and a
regular in-root fixture. There is still no implicit unrestricted mode.

## C-05 — Packaged FastAPI wrapper has an incorrect default repository root [RESOLVED on `codex`]

**Severity:** P2 local availability. This does not affect verdict authority,
evidence content, or network exposure. It prevents the packaged API entrypoint
from finding the assets it is documented to serve unless an operator sets an
otherwise optional environment variable.

`vigia/vigia_api.py` sets `REPO` to `Path(__file__).parent` when `VIGIA_REPO`
is unset. That resolves to `checkout/vigia/`; its `/cases`, narration, and EBS
verification paths expect assets under `checkout/data/cases`, `checkout/cases`,
`checkout/scripts`, and `checkout/forensics`. None exists beneath `vigia/` in
this checkout. The root wrapper does not have this defect because its file is
already at checkout root.

### Remediation — implemented on `codex`

The wrapper now defaults to `Path(__file__).resolve().parent.parent`, the
checkout root, rather than the package directory. `VIGIA_REPO` remains an
explicit override. The API boundary regression imports the module with the
environment variable absent and asserts that root.

## Checked, not relabeled as new

`L-063`, `L-064`, and `L-065` are already accurately documented doctrine
questions: fallback JSON CAIE fracture authority, the
`STATISTICAL_UNIFORMITY` producer gap, and unverified provenance-chain hashes.
Their characterization tests passed and remain known, not duplicate Codex
findings. The same applies to `L-062`, `B-149`/`L-066`, `L-057`, and `B-151(b)`.

## Test evidence

| Command / probe | Result | Meaning |
|---|---:|---|
| `pytest -q tests/test_bypass_vectors.py` | 5 passed | Existing bypass guards hold; they do not cover this HTTP boundary. |
| `pytest -q tests/characterization/test_verdict_authority_inputs.py tests/test_r4_boundaries.py` | 18 passed | Documented authority and scorer-boundary behavior reproduced. |
| `pytest -q tests/e2e/test_integration_end_to_end.py` | 38 passed | Checked end-to-end module passed. |
| Full-suite attempt | **not claimed green** | The execution channel lost final process status. |
| Optional FORGE run | **not evidence** | Discovery reached ~8.7 GiB RSS and did not produce a closed artifact before triage. |

## Next decision

The smallest safe repair is a shared tested path resolver plus loopback default.
Authentication for deliberately remote use is a separate explicit decision.
No product behavior has changed in this audit record.
