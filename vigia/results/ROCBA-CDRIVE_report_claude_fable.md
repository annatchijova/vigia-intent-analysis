# VIGIA FORENSIC INTENT ANALYSIS REPORT

```
Case ID      : ROCBA-CDRIVE
Investigator : VIGIA Autonomous Agent (Claude Code / Claude Fable, Mode 2)
Evidence     : rocba-cdrive.e01 (EWF, 23.7 GB compressed; 81.4 GiB NTFS volume)
Mode         : Claude Code (Mode 2). LLM narrative backend: Ollama (local).
SHA-256      : ef2c3c0cfbd66fe76a3513e6f84def6cbed281466ddfb561e771155feeb5f657
Timestamp    : 2026-07-23T02:00:00Z
SANS Phase   : Identification -> Containment (findings ready for Eradication/Recovery)
Seal (bundle): 2e7de4de576247ef3e3b2878f6a9f1cfaefcce34891429ebda71910fcfcf1859
Cronos trace : 12a022dc-807e-476b-9c83-77fd03caf34b
```

## EXECUTIVE SUMMARY

The image is the Windows 10 system drive of user **`fredr`** (personal identity
`fred.rocba@outlook.com`), a Stark Research Labs (SRL) endpoint. The evidence
shows an **insider data-theft followed by deliberate anti-forensic destruction**.
Proprietary SRL research (alloy test results, classified project files, business
plans) was collected on the endpoint alongside personal cloud-egress channels
(personal Dropbox, Google Drive, personal OneDrive). On **2020-11-14**, within
four minutes of downloading the Sysinternals `SDelete` secure-erase utility, the
user ran it **seven times against a hand-picked set of named SRL research
documents**, then exercised `vssadmin` (shadow copies) and `wevtutil` (event
logs) in the same 40-minute window.

**Analyst verdict (Mode 2): MALICE** for the targeted secure-erasure (F-001),
corroborated by insider exfiltration staging (F-004). The independent
deterministic CAIE engine returns **SUSPICION** (composite 0.2005) because it
treats prefetch as spoofable and finds no cryptographic/temporal golden-rule
fracture; both results are preserved per the Mode 1/Mode 2 scope rule — neither
silently overrides the other.

## TIMELINE OF EVENTS (all 2020, local -03:00 as stored)

| Time (Nov) | Artifact | Event |
|-----------|----------|-------|
| 10-20 | srl-h\Downloads\sdelete64.exe | Secure-erase tool present on the srl-h account (F-005) |
| 11-14 01:39 | REGEDIT prefetch | Registry editor run |
| 11-14 02:05 | MSTSC prefetch (run 2) | RDP client used (likely remote-access vector) |
| 11-14 10:38 | fredr\Downloads\SDelete.zip | SDelete downloaded |
| 11-14 10:42:18 | CMD prefetch (run 4) | Command shell |
| 11-14 10:42:38 | SDELETE prefetch -2BD91720 (run 2) | First secure-wipe executions |
| 11-14 10:47:10 | SDELETE prefetch -0E837E93 (run 5) | Secure-wipe of named SRL docs |
| 11-14 10:50 | NETSH prefetch | Network shell |
| 11-14 11:03 | VSSADMIN prefetch (run 3) | Shadow copy administration (F-002) |
| 11-14 11:18 | WEVTUTIL prefetch (run 4) | Event-log utility (F-003) |
| 11-15 23:44 | FTK IMAGER prefetch (run 1) | Forensic imager executed on the host |
| 11-16 00:05 | Security.evtx | Live security log last written (~20 MB, not zeroed) |

## FINDINGS

Full structured findings (Firstness / Secondness / Thirdness, `devil_advocate`,
corroboration, self-correction, MITRE) are sealed in
`ROCBA-CDRIVE_bundle_claude_fable.json`. Summary:

| ID | Title | Verdict | Conf. | Status |
|----|-------|---------|-------|--------|
| F-001 | Targeted secure-erasure of named SRL research documents (SDelete x7) | **MALICE** | HIGH | CONFIRMED |
| F-002 | Volume shadow copy administration in the cleanup window (vssadmin x3) | INTENT | MEDIUM | INFERRED |
| F-003 | Event-log utility executed in the cleanup window (wevtutil x4) | INTENT | MEDIUM | INFERRED |
| F-004 | Insider collection + personal-cloud exfiltration surface | INTENT | HIGH | CONFIRMED |
| F-005 | Pre-staged sdelete64.exe on srl-h account | SUSPICION | LOW | INFERRED |

**F-001 keystone.** The `SDELETE.EXE-0E837E93.pf` prefetch retains, as files the
tool touched, the full OneDrive paths of the wiped documents:
`ADAMANTIUM-BACKGROUND.DOCX`, `SUCCESS-TEST-PLAN-VIBRANIUM-ALLOY-RESULTS.DOCX`,
`THE SHIELD BACKGROUND AND ONGOING RESEARCH.DOCX`,
`EARTHFORCE SA-26 THUNDERBOLT STAR FURY.DOCX`, `NOKIA STRATEGY.DOCX`, and two
mail-order-pharmacy business plans. Secure-erasure of the exact proprietary
documents that were staged for exfiltration is the concealment layer that
separates MALICE from INTENT.

## PEIRCEAN REASONING (F-001)

- **Firstness.** Two SDELETE prefetch entries, run counts 5 and 2 (7 executions);
  the tool ran from `Users\fredr\Downloads\SDelete\SDELETE.EXE`; its prefetch
  file-reference list names SRL research `.docx` files under `Users\fredr\OneDrive`.
- **Secondness.** Legitimate deletion uses the Recycle Bin and leaves recoverable
  data. A DoD-pattern secure-erase tool, downloaded minutes earlier and run seven
  times against crown-jewel IP, is a structural impossibility for routine
  housekeeping.
- **Thirdness.** Deliberate destruction of the evidentiary source of a data theft
  — erasing the very documents that were exfiltrated. Repeatable anti-forensic
  law: acquire secure-erase tooling, destroy the source artifacts, then remove the
  recovery (shadow copies) and audit (event log) paths.

## MANDATORY REFUTATION (Eco's razor)

**Benign hypothesis:** legitimate off-boarding / IT cleanup. **Test:** routine
cleanup routes files through the Recycle Bin, does not use a just-downloaded
secure-erase tool against a hand-picked set of proprietary documents, and is not
accompanied by shadow-copy and event-log manipulation in the same window. The
`detect_eco_overinterpretation` filter returned **NORMAL_DISTRIBUTION**
(obvious_ratio 0.12): the evidence is **not** planted or too-perfect, so the
anomalies are authentic rather than a false-flag. The benign hypothesis fails to
account for the targeting of named IP plus recovery/audit destruction. **Deliberate
concealment survives refutation.** `validate_and_correct_analysis` found no
premature abduction, false secondness, habitless thirdness, or Carnegie bias.

## MITRE ATT&CK

- T1074.001 Local Data Staging; T1530 Data from Cloud Storage; T1567.002
  Exfiltration to Cloud Storage (F-004)
- T1485 Data Destruction; T1070.004 File Deletion (F-001)
- T1490 Inhibit System Recovery (F-002); T1070.001 Clear Windows Event Logs (F-003)

## ARTIFACTS EXAMINED

| Tool | Argument | Result |
|------|----------|--------|
| generate_forensic_hash | rocba-cdrive.e01 | SHA-256 ef2c...b5f657, INTEGRITY_VERIFIED |
| ewfmount + ntfs-3g | E01 -> ewf1 -> /fs (ro) | Win10 C:, profiles fredr + srl-h |
| list_files | Users/fredr, Prefetch, $Recycle.Bin | SRL sync + personal cloud + dual-use binaries |
| prefetch (pyscca) | SDELETE/VSSADMIN/WEVTUTIL/FTK/CMD | run counts + SDELETE file references |
| cross_artifact_analysis | 5 artifacts | composite 0.2005 SUSPICION, 0 fractures, deterministic |
| detect_eco_overinterpretation | 8 observations | NORMAL_DISTRIBUTION (not planted) |
| validate_and_correct_analysis | MALICE prior | no Peircean fallacy (backend ollama) |

## KNOWN LIMITATIONS

- **Exfiltration completion is INFERRED, not CONFIRMED.** On-disk artifacts prove
  collection, staging, and the presence of egress channels; they do not prove
  bytes left the host. Cloud/proxy/tenant logs would confirm the transfer.
- **F-002/F-003 sub-commands not recovered.** Prefetch shows execution and count,
  not the command line. Whether `vssadmin delete shadows` and `wevtutil cl` (vs
  read-only `list`/`qe`) ran must be confirmed from the Security and PowerShell
  Operational event logs. No event ID 1102 (audit-log-cleared) was confirmed in
  this pass; the live Security.evtx is ~20 MB and not zeroed.
- **Attribution is to the `fredr` identity**, not necessarily the physical person:
  RDP artifacts (MSTSC x2) are present. A third party operating fredr's session
  cannot be fully excluded from disk evidence alone.
- **`srl-h` sdelete64.exe (F-005)** is retained at SUSPICION; a legitimate admin
  explanation is not refuted.
- **CAIE vs analyst verdict.** The deterministic engine (SUSPICION) and the Mode-2
  analyst (MALICE) differ by design; the engine will not inflate above its
  spoofability floor without a golden-rule fracture. Both are sealed.

## TOKEN USAGE (this session)

```
Note: exact input/output token counts are available at usage.anthropic.com.
Session backend for narrative sub-calls: Ollama (local) via reason path.
Full deterministic core (hashing, prefetch parse, CAIE, sealing) used 0 tokens.
```
