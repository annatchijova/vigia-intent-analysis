# VIGÍA FORENSIC INTENT ANALYSIS REPORT — v2 (corrected after external audit)

> **This is a correction, not a replacement.** `results/OWL-NEXUS5-CASE_bundle_claude.json` (v1) and
> `results/OWL-NEXUS5-CASE_report_claude.md` (v1) are kept as-is for the audit trail. This v2 documents
> what an external adversarial review (ChatGPT, relayed by the operator) found wrong in v1, what this
> agent verified directly against the live evidence in response, and what changed. Forward-only, per
> this project's git-discipline doctrine — nothing in v1 was deleted or silently overwritten.

```
VIGIA FORENSIC INTENT ANALYSIS REPORT — v2
======================================
Case ID      : VIGIA-OWL-2019-NEXUS5
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic, Sonnet 5)
Bundle       : results/OWL-NEXUS5-CASE_bundle_claude_v2.json (37-entry tool_execution_log,
               chain v2, verified: CHAIN VERIFIED (37 entries, schema v2))
Supersedes   : results/OWL-NEXUS5-CASE_bundle_claude.json (v1, NOT deleted)
```

---

## WHAT THE EXTERNAL AUDIT FOUND, AND WHAT I VERIFIED

The operator ran a separate adversarial review of the v1 bundle/report. Every claim below was
re-checked directly against the live evidence before being accepted — none is taken on the auditor's
word alone (per this project's audit-before-patch discipline).

### 1. v1 claim "no purchase/delivery/payment confirmation exists in the evidence" — **FALSE, corrected**

`mmssms.db` (quick extraction, `evidence/owl-2019-nexus5-quick/Agent Data/`) contains 21 SMS rows.
The original session queried it with `SELECT ... LIMIT 5` and never read the rest. The full table
contains:

```
+13045184333 | 2017-02-01T00:41:15Z UTC | "Sarah, the delivery is today 7 tonight
                                            the confirmation will come later through pidgin"
```

This is a real delivery/confirmation message. It directly contradicts the v1 report's stated basis
for capping the verdict at SUSPICION ("no payment/logistics artifact corroborates a completed
transaction"). **This was a methodological failure (a `LIMIT 5` query treated as if it were the full
table), not a fabrication — but its effect on the report's conclusion is the same either way, and it
is now corrected.**

### 2. `evidence/owl-2019-hd1-windows` was wrongly "ruled out" — **reclassified UNRESOLVED**

v1 dismissed this case as unrelated based only on zero ASCII hits for `owl`/`mcavoy`. Following the
SMS correction above, this agent re-examined it specifically for **Pidgin** — the exact IM client
named in the SMS ("confirmation will come later through pidgin"):

- `list_files` on `evidence/owl-2019-hd1-windows/prefetch` confirms **three** Pidgin prefetch entries:
  `PIDGIN.EXE-86E18E41.pf`, `PIDGIN-2.11.0.EXE-93DF4765.pf`, `PIDGIN-2.11.0 (1).EXE-138939A7.pf`
  (install + two runs).
- Their headers begin with `MAM\x04` — a Windows 10 MAM-compressed prefetch container. **No
  decompressor is available in this toolset**, so the embedded last-run FILETIME could not be
  extracted, and the exact execution timestamp could **not** be correlated against the SMS's
  2017-02-01T00:41:15Z.
- `search_pattern` for `mcavoy` / `Sarah` / `layster` across the entire `owl-2019-hd1-windows` tree
  (browser history, `NTUSER.DAT`, `SAM`, `SOFTWARE`, `SYSTEM`, event logs): **zero ASCII hits**. This
  is **inconclusive, not a refutation** — Windows registry hives commonly store strings as UTF-16LE,
  which a plain ASCII grep will not match even if the name is present.

**Status changed: `owl-2019-hd1-windows` is UNRESOLVED, not ruled out.** The Daubert Corroboration
Gate's premise ("no second independent device/channel in evidence") is therefore **unconfirmed**, not
affirmatively established as v1 stated.

### 3. v1 report language overclaimed what the audit chain proves — **corrected**

v1 said the bundle was "HMAC-sealed, independently verified with `verify_tool_log.py`," in a way that
implied real-time capture of 29 actual MCP calls. Checking this directly: the 29 (now 37) entries in
`tool_execution_log` were written by this agent, in a Python script, **after** each batch of real MCP
tool calls completed in the conversation — not by instrumentation inside the MCP server at each call
site. Measured span of the first 29 entries: **0.00075 seconds**. The 8 correction entries added for
this v2: **0.000414 seconds**. Both are single-process, back-to-back writes, not live captures.

**What this chain actually proves:** the `entry_hash`/`entry_hmac` chaining is real — no entry was
altered relative to its neighbours after being written, and every cited SHA-256 (Bookmarks,
musically.db, mmssms.db) is real and independently reproducible against the actual files.
**What it does not prove:** that the entries reflect the literal wall-clock moment, order, or exact
tool-response text of each real MCP call. `verify_tool_log.py` verifies **chain integrity**, not
**contemporaneity**. Running it without `--hmac-key-file` (as the external audit did) also cannot
confirm the HMAC layer — that requires the key file, which is deliberately access-restricted by
design, not a gap, but this must be stated rather than assumed.

**Root cause, and the actual fix:** `vigia_sift_bridge.py` does not currently call
`ToolExecutionLogChain.append()` at each tool's entry/exit. Doing that — instrumenting the MCP server
itself, not the calling agent — is the correct fix, and is out of scope for resolving this one case.
Flagged as follow-up work below.

---

## VERDICT (unchanged: SUSPICION, but the basis is now different)

**SUSPICION.** Not "no second source exists" (v1's claim, now corrected) but "a second source may
exist (Pidgin on `owl-2019-hd1-windows`) and could not be confirmed or refuted with the tools available
in this session." The gate is held open, not resolved in either direction. Upgrading to INTENT/MALICE
would require confirming the identity link on the Windows machine; this agent did not do that, and
does not claim to have.

---

## FOLLOW-UP WORK (not done in this session)

1. Decompress the 3 Pidgin `.pf` files (Windows 10 MAM container) and extract the embedded last-run
   FILETIME(s); compare against `2017-02-01T00:41:15Z`.
2. Search `SAM`/`SOFTWARE`/`SYSTEM`/`NTUSER.DAT` with a UTF-16LE-aware string extractor (not plain
   ASCII grep) for `McAvoy`, `Sarah`, `layster`, `Layla`.
3. Check Pidgin's own config/log/buddy-list files under the imaged user profile, if present.
4. Instrument `vigia_sift_bridge.py` to call `chain.append()` at each tool's entry/exit, so future
   `tool_execution_log`s are live-captured rather than agent-reconstructed after the fact.

---

## ARTIFACTS

- `results/OWL-NEXUS5-CASE_bundle_claude_v2.json` (+ `.sha256`) — corrected bundle, 37-entry chain,
  `CHAIN VERIFIED`.
- `results/OWL-NEXUS5-CASE_bundle_claude.json` (v1, unmodified) — kept for the audit trail.
- `results/OWL-NEXUS5-CASE_report_claude.md` (v1, unmodified) — kept for the audit trail.
