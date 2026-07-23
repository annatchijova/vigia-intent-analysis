# AMICUS CURIAE — Forensic Intent Analysis

**In the matter of case ROCBA-CDRIVE**
**Submitted by:** VIGIA Autonomous Forensic Intent Engine (Claude Code / Claude Fable, Mode 2)
**Evidence:** `rocba-cdrive.e01`, SHA-256 `ef2c3c0cfbd66fe76a3513e6f84def6cbed281466ddfb561e771155feeb5f657`
**Sealed bundle:** `ROCBA-CDRIVE_bundle_claude_fable.json`, seal `2e7de4de576247ef3e3b2878f6a9f1cfaefcce34891429ebda71910fcfcf1859`
**Cronos trace:** `12a022dc-807e-476b-9c83-77fd03caf34b`

---

## 1. Purpose and posture of this brief

This brief is offered as a neutral forensic aid, not as advocacy for any party.
Its purpose is to state, with explicit separation of *fact* from *inference*,
what the digital evidence on the subject drive supports and — equally important —
what it does **not** support. Every factual assertion traces to a reproducible
artifact identified by path and to a tool output that an independent examiner can
re-run. Where the evidence permits an innocent reading, that reading is stated and
tested rather than suppressed.

## 2. Facts established to a high degree of forensic certainty

1. The drive is a Windows 10 endpoint bearing two profiles, `fredr` and `srl-h`.
   The `fredr` profile is associated with the personal address
   `fred.rocba@outlook.com` (recovery-key file in Downloads).
2. A Sysinternals `SDelete` archive was downloaded into `fredr\Downloads` on
   2020-11-14 at 10:38; the extracted `SDELETE.EXE` was executed. Prefetch records
   two `SDELETE.EXE` execution entries with run counts of 5 and 2.
3. The `SDELETE.EXE-0E837E93` prefetch retains, in its file-reference list, the
   full paths of named Stark Research Labs research documents under
   `Users\fredr\OneDrive` (alloy test results, project research, business plans).
4. `VSSADMIN.EXE` (run count 3) and `WEVTUTIL.EXE` (run count 4) were executed at
   11:03 and 11:18 on 2020-11-14 respectively — within the same window as the
   secure-erase activity.
5. The `fredr` profile co-locates a corporate "Stark Research Labs" cloud sync
   (including folders belonging to other named employees, and a local duplicate
   "SRL-Projects - Megaforce (1)") with personal cloud channels: "ROCBA Dropbox",
   Google Drive, personal OneDrive, iCloudDrive.

These are **observations**, corroborated across independent artifact classes
(prefetch execution metadata, prefetch file references, filesystem timeline, and
directory structure).

## 3. Inference drawn, and the standard applied

From facts (2)-(5) the engine infers **deliberate destruction of the evidentiary
source of a data theft** (the "concealment layer"), and grades this **MALICE**
under the VIGIA scale, corroborated by an insider **exfiltration** posture
(INTENT). This inference was subjected to the Mandatory Refutation Protocol: the
strongest innocent explanation (legitimate off-boarding / IT cleanup) was
constructed and tested, and it fails to explain the targeting of specifically
named proprietary documents together with shadow-copy and event-log activity.
The `detect_eco_overinterpretation` control returned a normal distribution,
indicating the evidence is authentic rather than fabricated or planted.

## 4. Competing account, preserved for the tribunal

The court is owed the fact that **two instruments reached two different grades**:

- The **deterministic CAIE engine** — which is intentionally conservative and
  refuses to grade above a "spoofability floor" absent a cryptographic or
  temporal-causality fracture — returned **SUSPICION** (composite score 0.2005).
- The **Mode-2 analyst reasoning** returned **MALICE**.

This divergence is disclosed, not reconciled by fiat. The deterministic engine's
caution reflects a real evidentiary property: prefetch metadata is, in principle,
falsifiable, and no single artifact here is "structurally irrefutable" in the
engine's sense. The analyst grade rests on the *convergence* of independent
artifacts and the failed refutation, which is a legitimate but distinct standard.
A tribunal should weigh both.

## 5. Matters the evidence does NOT establish

1. **That data actually left the endpoint.** The disk proves collection, staging,
   and the presence of egress channels. It does not prove completed transfer.
   Cloud-tenant, proxy, or DLP logs are required to close this gap.
2. **The exact anti-forensic sub-commands.** Prefetch proves that `vssadmin` and
   `wevtutil` ran and how many times, not what they did. Whether shadow copies
   were *deleted* (vs listed) and whether any log was *cleared* (vs queried) must
   be read from the Security and PowerShell Operational event logs. No event ID
   1102 was confirmed in this pass, and the live Security log is not zeroed.
3. **That the physical person `fredr` performed the acts.** RDP artifacts are
   present. Session attribution to the *account* is supported; attribution to the
   *person* requires corroborating access/authentication records.
4. **Culpability for `srl-h`'s `sdelete64.exe`.** This artifact is retained at
   SUSPICION only; a legitimate administrative explanation is not excluded.

## 6. Chain of custody and reproducibility

The evidence image was hashed before examination (SHA-256 above) and mounted
read-only via `ewfmount` + `ntfs-3g`; nothing was written to the evidence. Every
tool invocation is recorded in a tamper-evident v2 hash chain
(`tool_execution_log`, tail anchor `chain_tip_sha256`
`26cd7db642ccd5cc8b7c661134a9aac69f2258c940943afe679c59e6560a33d1`), independently
verifiable with `verify_tool_log.py` (result: CHAIN VERIFIED, 9 entries). The
sealed decision payload is reproducible bit-for-bit: it was canonicalized and
hashed three times (repeat and key-reorder) with identical digests. No
floating-point value entered the sealed decision path. The LLM narrative layer
did not influence any sealed value; it renders prose beside the seal only.

**Caveat of record:** `VIGIA_HMAC_KEY` was not set for this session, so the chain
carries no `entry_hmac`/`chain_tip_hmac`. The chain is therefore tamper-evident
against edit/insert/reorder/truncate by anyone *without* the key, but a party with
write access who recomputes the entire chain could not be detected by SHA-256
alone. For evidentiary use, re-seal under a managed HMAC key.

## 7. Recommendation

The forensic record supports referring this matter for **insider-threat and
evidence-destruction** review, prioritizing acquisition of the corporate cloud
tenant and endpoint event logs to convert the INFERRED elements (completed
exfiltration; exact anti-forensic sub-commands) to CONFIRMED. The MALICE grade for
the targeted secure-erasure rests on CONFIRMED on-disk facts and a passed
refutation; it is offered as a defensible expert inference, with its limits stated
above.

*Respectfully submitted. VIGIA emits scope-bounded, reproducible findings; a
documented limitation is presented as an asset, not concealed.*
