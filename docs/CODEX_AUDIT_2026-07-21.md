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

## C-01 — FastAPI case-path escape [CONFIRMED]

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

### Repair proposal — not implemented

1. Add one pure shared `resolve_case_path()` boundary; do not duplicate guards.
2. Reject absolute input; resolve and require explicit roots `data/cases/` and
   `cases/`, not merely any path below the repository.
3. Require a regular, non-symlink `.json` file and open the validated path.
4. Test absolute path, `..` escape, symlink escape, directory, and an allowed
   fixture against both public wrappers.
5. Bind the experimental API to `127.0.0.1` by default. Remote operation must
   require explicit authentication before binding beyond loopback.
6. Validate and normalize inbound JSON before scoring. Today it is scored
   before later EBS validation; no false-clean verdict was observed, so this is
   a defense-in-depth repair rather than a separate confirmed defect.

Authentication and remote deployment are owner decisions, so this audit does
not choose or implement them.

## C-02 — OpenAI-compatible chat crashes on scalar JSON [CONFIRMED]

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

The repair is small and should be covered by a regression test: accept only a
JSON object for forensic-case handling (`isinstance(case_data, dict)`), return
the existing usage guidance for all other JSON values, and validate the outer
message contract at the boundary. The package wrapper has no OpenAI-compatible
chat route, so C-02 is root-wrapper specific.

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
