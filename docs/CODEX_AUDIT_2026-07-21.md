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
