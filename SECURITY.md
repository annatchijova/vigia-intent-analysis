# VIGIA Security Policy

## Reporting Vulnerabilities

**DO NOT** open public issues for security bugs.

| Severity | Contact | Response Time |
|----------|---------|--------------|
| Critical (evidence integrity) | security@vigia-forensics.org | 4 hours |
| High (attribution bypass) | security@vigia-forensics.org | 24 hours |
| Medium/Low | GitHub Issues | 7 days |

## Hardened Security Architecture

### Input Sanitization (Architectural, not prompt-based)

| Function | What it blocks |
|----------|---------------|
| `_sanitize_path()` | Path traversal (`..`), symlinks (every path component), null bytes, blocked system prefixes, confinement to `EVIDENCE_BASE_DIR`, TOCTOU-resistant via resolved-path checks |
| `_sanitize_grep_pattern()` | Homoglyph attacks, shell injection, non-ASCII, dangerous commands -- strict ASCII whitelist |
| `_sanitize_text()` | ReDoS via length cap |
| `_sanitize_text_list()` | OOM via count + byte-volume limits |
| `@rate_limit()` | Per-function sliding-window rate limiting with exponential backoff |

### MCP Transport Security

VIGIA uses MCP-over-stdio by default, where security is enforced by the OS:
only the parent process (Claude Code, Ollama) can read/write the stdin/stdout pipes.

Startup protections (V-002 mitigation):
- **Session token**: generated at startup, printed to stderr for operator verification
- **Stdin pipe check**: warns if stdin is not a pipe (unexpected command source)
- **HTTP/SSE detection**: logs CRITICAL alert if HTTP transport is detected in args, since it exposes 21+ forensic tools to any local process on the network port
- **Parent process logging**: records PPID and parent executable path to audit trail

For HTTP/SSE deployments (NOT recommended without additional auth):
- Use Unix socket with 0o600 permissions instead of TCP port
- Implement token-based authentication at the application layer
- Restrict network binding to localhost only

### Rate Limiting (All MCP Tools)

Every MCP tool is protected by `@rate_limit()` with sliding window + exponential backoff:

| Category | Tools | Limit |
|----------|-------|-------|
| LLM (cost + latency) | `reason_with_llm`, `validate_and_correct_analysis` | 5/min |
| Sensitive (root, mount, honey) | `mount_sift_evidence`, `activate_honey_token`, `reload_phonetic_dict`, `audit_network` | 5/min |
| CPU heavy (entropy, CLIP, OCR) | `calculate_shannon_entropy`, `audit_image_metadata`, `analyze_stylometry`, `calculate_human_entropy` | 10/min |
| Medium I/O (grep, analysis) | `search_pattern`, `infer_intent`, `detect_habit_incongruence`, `detect_human_jitter`, `audit_grice_maxims`, `detect_eco_overinterpretation`, `list_processes` | 30/min |
| Light I/O (read, list, hash) | `list_files`, `read_evidence`, `generate_forensic_hash`, `get_phonetic_dict_stats` | 100/min |

`rate_limit_reset()` is INTERNAL ONLY -- never exposed as MCP tool.

### LLM Prompt Injection Firewall (LLMShield)

Single canonical implementation in `vigia/security.py`. Three-pass scanning:

1. **NFKC-normalised text** -- catches Unicode homoglyph substitution
2. **Leet-decoded text** -- catches 1337 obfuscation
3. **Original text** -- catches patterns that survive normalisation

25+ patterns covering: instruction override, DAN/jailbreak families (contextual -- does NOT false-positive on the name "Dan"), system prompt extraction, role confusion, token-stuffing delimiters.

### Forensic Log Integrity (HMAC Chain)

Every audit log entry contains:
- `_prev_hmac`: HMAC of the previous entry (or "GENESIS" for the first)
- `_hmac`: HMAC-SHA256 of the entry content + `_prev_hmac`

Tampering with any line invalidates all subsequent entries. Verification via `audit_logger.verify_chain()`.

HMAC key resolution:
1. `VIGIA_HMAC_KEY` env var (hex-encoded, >= 32 bytes)
2. `VIGIA_HMAC_KEY_FILE` env var (path to file with raw key bytes)
3. Auto-generated ephemeral key (development only -- logged as WARNING)

### Subprocess Sandbox

All subprocess execution goes through `vigia/sandbox.py`:
- Memory limits via `setrlimit(RLIMIT_AS)`
- CPU time limits via `setrlimit(RLIMIT_CPU)`
- Output truncation (10 MB stdout, 256 KB stderr)
- Hard asyncio timeout with process kill
- Privilege drop: `_drop_privs_if_requested()` aborts child with `os._exit(126)` if `setuid()` fails (never continues as root)

### Honey Token Hardening

Honey tokens use **secure temp files** (never `os.environ`):
- `tempfile.mkstemp()` with permissions `0o600`
- Stored within `EVIDENCE_BASE_DIR` sandbox
- Monitor via: `sudo auditctl -w <path> -p r -k honey_<n>`

### Mount Security

- Magic-byte validation before mounting (`EVF`/`LVF` for E01, script detection for raw)
- `noexec,nosuid,nodev,ro` mount flags (hardened in 2026-04 audit)
- Mount point restricted to `/mnt/analysis/` subtree
- Empty-directory check before mounting
- All mount operations via `sandboxed_execute()` with resource limits

### CLIP Model Integrity

- SHA-256 verification of model files before loading
- Hash sources: `VIGIA_CLIP_HASH_FILE` (JSON), per-model env vars, or hardcoded
- **Strict mode** (`VIGIA_STRICT_MODEL_CHECK=true`): refuses to load models without configured hash
- Prevents supply-chain attacks where a poisoned model classifies forged documents as legitimate

### MCP Transport Security

VIGIA uses stdio transport by default, which inherits OS-level process isolation:
only the parent process (Claude Code, Ollama) can read/write the server's stdin/stdout.

Startup verification (`_verify_transport_security()`):

1. **Session token**: Random 128-bit token printed to stderr for operator verification.
2. **Stdin check**: Warns if stdin is not a pipe (unexpected command source).
3. **HTTP/SSE blocking**: If SSE transport is detected AND `VIGIA_MCP_AUTH_TOKEN` is not set, logs CRITICAL alert. With `VIGIA_ENFORCE_STDIO=true`, aborts startup entirely.
4. **Parent process verification**: Reads `/proc/{ppid}/exe` and compares against allowed executables (claude, node, python3, ollama, etc.). With `VIGIA_ENFORCE_PARENT=true`, aborts if parent is unknown.
5. **Forensic logging**: Parent PID, executable, and trust status logged to the HMAC-chained audit trail.

Environment variables:
- `VIGIA_MCP_AUTH_TOKEN`: Required for HTTP/SSE transport (not needed for stdio)
- `VIGIA_ENFORCE_STDIO=true`: Block startup if HTTP/SSE transport detected without auth
- `VIGIA_ENFORCE_PARENT=true`: Block startup if parent process is not in the allowed list

### Webhook Security

- HTTPS-only by default (override: `VIGIA_WEBHOOK_ALLOW_HTTP=true`)
- TLS verification via `ssl.create_default_context()`
- HMAC-SHA256 payload signature via `X-Vigia-Signature` header (requires `VIGIA_WEBHOOK_SECRET`)

### Anti-Gaslighting Architecture

VIGIA is designed to resist manipulation of its own analysis:

1. **Structural Impossibility Anchors** -- memory-divergence findings cannot be gaslit
2. **Cross-Validation** -- no single tool triggers final MALICE verdict
3. **Epistemic Humility** -- every conclusion includes `what_would_falsify_this`
4. **Self-Correction** -- `validate_and_correct_analysis` checks 4 Peircean fallacies

### Credential Protection

- Anthropic API key errors are sanitized before logging (full key + `sk-ant-*` pattern redacted)
- No secrets in code or default configurations
- All sensitive env vars documented with vault-storage recommendation

### Temp Directory Security

No module falls back to bare `/tmp`. All fallbacks use:
- `tempfile.mkdtemp()` with `0o700` permissions (directories)
- `tempfile.mkstemp()` with `0o600` permissions (files)
- Symlink verification on created paths (defense-in-depth)

### Score Poisoning Protection (Infinity Guard)

All numeric inputs to the CAIE scoring engine pass through `math.isfinite()`.
If an attacker injects `float('inf')`, `float('-inf')`, or `float('nan')` as
a raw score, the artifact is zeroed and a `FORENSIC_POISONING_ATTEMPT` alert
fires. All scores are clamped to `[0.0, 1.0]`. The `adjusted_score` property
has a defense-in-depth `isfinite()` check even after clamping, to guard against
corrupted `EvidenceProfile` values.

### Prompt Vault (OpSec)

The Peirce system prompt is NOT stored in source code. It is loaded at startup
from a protected file (`vigia/data/system_prompt_peirce.md`) via `_load_system_brain()`.

Checks:
- File must exist and not be a symlink
- Permissions must be `0600` or `0640` (POSIX)
- If `VIGIA_PROMPT_HASH` is set, SHA-256 must match (integrity)
- If `VIGIA_STRICT_PROMPT=true`, any failure aborts startup

### Dictionary Integrity

Before parsing `phonetic_dict.json`, the loader verifies its SHA-256 against
`VIGIA_PHONETIC_HASH`. A poisoned dictionary can remove Russian phonetic patterns,
making evasion invisible to VIGIA. Hash mismatch fires `PHONETIC_DICT_TAMPERED`
and blocks the load.

### Grep Pattern Security

`_sanitize_grep_pattern()` uses `re.fullmatch()` (not `re.match()`) to ensure
the ENTIRE pattern conforms to the ASCII whitelist. Null bytes are rejected first.
Every rejection is logged to the forensic audit trail.

### Signal Sanitization (LLM Input)

`_sanitize_llm_input()` strips XML/HTML tags that could trigger LLM role-switching
(`</system>`, `<human>`, `[INST]`, etc.), removes control characters, and truncates
interpretation fields. Applied to all inputs that flow from forensic tools into
LLM prompts via `_build_kwargs`.

### Atomic Image Access

`vision_intent_audit` opens images via `os.open(O_RDONLY | O_NOFOLLOW)` to obtain
a file descriptor. Dimension checks and image loading operate on the same fd,
eliminating the TOCTOU window between validation and processing. `O_NOFOLLOW`
rejects symlinks at the kernel level on POSIX systems.

### Windows Sandbox Fail-Safe

If `VIGIA_ENFORCE_POSIX_SANDBOX=true` and the OS is Windows, startup aborts with
a critical error. Without POSIX `setrlimit`, subprocess execution has no memory
or CPU limits — unacceptable for forensic use. On Windows without enforcement,
`psutil`-based working set limits are applied as best-effort fallback.

### Witness Mode / Dual Custody (Daubert Compliance)

When the investigation verdict is MALICE or INTENT, the report is co-signed
with `VIGIA_HUMAN_OPERATOR_KEY` via HMAC-SHA256. This creates dual custody:
one key from the system (audit log HMAC chain), one from the qualified analyst.

Modes:
- `DUAL_CUSTODY`: Operator key present, report signed. Daubert-admissible.
- `UNSIGNED`: No operator key, soft warning. Report is usable but lacks
  human oversight certification.
- `HARD_FAIL`: `VIGIA_FORENSIC_STRICT=true` and no operator key. Verdict is
  INVALIDATED and the investigation aborts. The system refuses to produce a
  critical verdict without human co-signature.

The `WITNESS_HARD_FAIL` event fires at CRITICAL level in the audit log.
Operator key must be at least 32 characters (weak keys are also rejected
in strict mode).

### CAIE Artifact Limits

The Cross-Artifact Incongruence Engine enforces:
- Maximum 1000 artifacts per evaluation (DoS protection)
- Evidence type whitelist — unknown types rejected to prevent spoofability bypass
- `EvidenceProfile` validation: spoofability and weight must be finite, numeric,
  and in [0.0, 1.0] range
- Non-finite scores (`inf`, `NaN`) zeroed with `FORENSIC_POISONING_ATTEMPT` alert

## Environment Variables

### Required for Production

| Variable | Purpose |
|----------|---------|
| `VIGIA_EVIDENCE_DIR` | Evidence base directory (absolute path) |
| `VIGIA_HMAC_KEY` or `VIGIA_HMAC_KEY_FILE` | HMAC key for audit log integrity |
| `ANTHROPIC_API_KEY` | Anthropic API key (store in vault) |

### Recommended for Production

| Variable | Purpose | Default |
|----------|---------|---------|
| `VIGIA_STRICT_MODEL_CHECK` | Refuse CLIP load without hash | `false` |
| `VIGIA_CLIP_HASH_FILE` | JSON with model SHA-256 hashes | none |
| `VIGIA_WEBHOOK_SECRET` | HMAC secret for webhook signatures | none |
| `VIGIA_DROP_PRIVS_UID` | UID to drop to when running as root | none |
| `VIGIA_ENFORCE_STDIO` | Block HTTP/SSE transport without auth | `false` |
| `VIGIA_ENFORCE_PARENT` | Block startup from unknown parent processes | `false` |
| `VIGIA_MCP_AUTH_TOKEN` | Auth token required for HTTP/SSE transport | none |

### Optional

| Variable | Purpose | Default |
|----------|---------|---------|
| `VIGIA_LLM_BACKEND` | `anthropic`, `ollama`, or `none` | `anthropic` |
| `VIGIA_OLLAMA_HOST` | Ollama API endpoint | `http://127.0.0.1:11434` |
| `VIGIA_OLLAMA_MODEL` | Ollama model name | `llama3` |
| `VIGIA_MAX_FILE_MB` | Max file size for analysis | `500` |
| `VIGIA_GREP_DEPTH` | Max recursive grep depth | `5` |
| `VIGIA_SANDBOX_MEMORY_MB` | Subprocess memory limit | `512` |
| `VIGIA_SANDBOX_CPU_SEC` | Subprocess CPU time limit | `30` |
| `VIGIA_WEBHOOK_ALLOW_HTTP` | Allow non-HTTPS webhooks | `false` |
| `VIGIA_SYSTEM_PROMPT_PATH` | Override path for Peirce system prompt | `vigia/data/system_prompt_peirce.md` |
| `VIGIA_PROMPT_HASH` | SHA-256 of system prompt file (integrity) | none |
| `VIGIA_STRICT_PROMPT` | Abort if prompt vault checks fail | `false` |
| `VIGIA_PHONETIC_HASH` | SHA-256 of phonetic_dict.json (integrity) | none |
| `VIGIA_ENFORCE_POSIX_SANDBOX` | Abort on Windows (no setrlimit) | `false` |
| `VIGIA_FORENSIC_STRICT` | Abort if critical verdict lacks operator key | `false` |
| `VIGIA_HUMAN_OPERATOR_KEY` | HMAC key for witness dual-custody co-signature | none |

## Deployment Checklist

- [ ] `ANTHROPIC_API_KEY` stored in vault, not shell env
- [ ] `VIGIA_EVIDENCE_DIR` set to a dedicated, restricted directory
- [ ] `VIGIA_HMAC_KEY` or `VIGIA_HMAC_KEY_FILE` configured (not ephemeral)
- [ ] `VIGIA_STRICT_MODEL_CHECK=true` if using CLIP
- [ ] `VIGIA_CLIP_HASH_FILE` populated with verified model hashes
- [ ] `/evidence` mounted read-only for acquisition
- [ ] `vigia-mcp` runs as non-root user (`vigia:vigia`)
- [ ] `VIGIA_DROP_PRIVS_UID` set if root execution is unavoidable
- [ ] Audit logging enabled to WORM storage
- [ ] Network egress restricted (air-gapped preferred)
- [ ] `VIGIA_WEBHOOK_SECRET` set if using webhook notifications
- [ ] Periodic `audit_logger.verify_chain()` runs to detect log tampering

## Known Limitations

- `audit_network` requires root; graceful fallback to `list_processes` is implemented
- LLM-based tools (`reason_with_llm`, `validate_and_correct_analysis`) require Anthropic API or Ollama
- Stylometry false positives on texts < 50 words
- Cultural neutrality calibrated for Rioplatense Spanish; other varieties need calibration
- HMAC chain verification requires the same key used to write the log; ephemeral keys are lost on restart

## Audit History

| Date | Auditor | Fixes Applied |
|------|---------|---------------|
| 2025-04 | Security audit (DeepSeek) | P0-1 through P0-4, P1-5 through P1-8, P2-9 through P2-13, P3-14 through P3-16 (16 fixes) |
| 2025-04 | Security audit (round 2) | V-002 MCP transport security, V-003 rate limiting on all 21 tools, V-004 base_dir symlink validation, activate_honey_token env hijack fix, safe_grep total scan volume limit |
| 2025-04 | Kimi integration (round 3) | CrossArtifactIncongruenceEngine (`vigia/tools/caie.py`) implemented and integrated in PeircePlanner (Rule 10), `load_investigation_state` schema+HMAC validation, canonicalizacion forzada via `Path.resolve()` en todos los entry points, symlink guard con `os.lstat` + `stat.S_ISLNK` (atomico). 100% de hallazgos Kimi P0-P3 mitigados. |
| 2025-04 | Gemini + Kimi hardening (round 4) | Grep fullmatch (P0), Infinity Guard / math.isfinite (P0), word_search special char support, Prompt Vault with SHA-256 integrity, Dictionary integrity with VIGIA_PHONETIC_HASH, PNG metadata silence detection (P1-7), Windows sandbox fail-safe (P1-8), Atomic image access via O_NOFOLLOW fd (P1-9), LLM signal sanitization stripping XML/control chars (P1-10). 10 fixes. |

### CAIE — Cross-Artifact Incongruence Engine

Designed by Kimi (Moonshot), implemented by Claude (Anthropic).

Implements authenticity-adjusted scoring: `adjusted = raw_score * (1 - spoofability) * weight`.

Evidence that is structurally hard to fabricate (memory objects, kernel structures, HMAC-chained logs) dominates easily-planted evidence (IPs, cultural markers, log entries) in the composite verdict.

Fracture detection identifies cross-artifact discrepancies:
- `LOG_VS_MEMORY`: logs claim activity that memory contradicts (structural impossibility)
- `FALSE_FLAG_PATTERN`: high cultural attribution + zero technical corroboration (planted evidence)
- `VERDICT_CONFLICT`: contradictory verdicts between tools (requires deeper analysis)

Daubert admissibility assessment included in every CAIE result.
