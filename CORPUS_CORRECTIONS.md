# CORPUS_CORRECTIONS.md

Ground truth corrections to the VIGIA forensic corpus.
Each entry documents: what the original case said, what the authoritative
source says, why the correction is warranted, and the exact citation.

These are corrections to *case labeling and artifact attribution*, not code
bugs. They affect expected verdicts and case descriptions in
`data/cases/converted/`.

---

## CORRECTION C-001 — VIGIA-REAL-VANKO: two-event misattribution

**Date:** 2026-07-14
**Status:** Applied — original case replaced by two separate cases (see below)
**Applied by:** Anna Tchijova / VIGÍA forensic review

### What the original case said

`data/cases/converted/VIGIA-REAL-VANKO.json` (schema_version: 1.0,
created 2026-06-07):

- **Case framing:** Single event — Anthony Vanko exfiltrated classified
  Stark Enterprises research. `expected_verdict: "MALICE"`.
- **ART-001:** `smallftpd.exe` at `C:\Users\defaultprinter\smallftpd.exe`,
  attributed to Vanko as exfiltration infrastructure. `timestamp:
  2016-06-18T00:00:00Z`.
- **ART-002:** `ftpd.ini` at `C:\Users\defaultprinter\ftpd.ini`,
  attributed to Vanko as persistent exfiltration channel configuration.
  `timestamp: 2016-06-18T00:00:00Z`.
- **ART-003:** `transfers.log` — `Download started by defaultprinter
  [173.73.166.249]` on `2016-06-18T22:21:49Z`, attributed to Vanko.
  `timestamp: 2016-06-18T22:21:49Z`.
- **ART-007:** `NTUSER.DAT` from `defaultprinter` account — user active
  21:55-22:22Z on 2016-06-18, attributed to Vanko ("eliminates hypothesis
  that FTP server was triggered remotely without Vanko's knowledge").

### What the authoritative source says

**Source:** `FOR500HANDOUT_Vanko Master Scenario Solution.pdf`

- **File location at collection time:** Found inside the CyLR extraction
  at `vanko-c-drive.CYLR/FOR500HANDOUT_Vanko Master Scenario Solution.pdf`
  — i.e., present on Vanko's own device when collected.
- **Author:** Mark Hallman
- **Course:** SANS FOR500 — Windows Forensic Analysis
- **Created:** 2018-05-29 (Adobe Acrobat PDFMaker 18)
- **Pages:** 35
- **Related student scenario:** `Vanko Student Scenario_D01_01.docx`
  by Ovie Carroll (same SANS FOR500 course material)

**Two completely separate events are documented:**

#### Event 1 — Nina's attack (2016-06-18) [Pages 11-19]

Nina (last name not given in solution) was hired by competitors. She inserted
a **USB Rubber Ducky** HID attack device into Vanko's workstation while Vanko
was away from his desk. The device automated keystrokes that:

1. Created the hidden `defaultprinter` service account (Windows Event ID 4720)
2. Installed `smallftpd.exe` under that account
3. Configured `ftpd.ini` for persistent external access
4. Created `temp.zip` from classified documents already on the machine

Nina then **remotely connected via RDP** from IP `173.73.166.249` (Arlington,
VA, Verizon FiOS residential) — Windows Event ID 4624, Logon Type 10 — and
downloaded `temp.zip` via FTP at `2016-06-18T22:21:49Z`.

**Vanko was not present during this event. The `defaultprinter` account,
`smallftpd.exe`, `ftpd.ini`, `transfers.log`, and the June 18 FTP transfer
are entirely Nina's work.**

The `NTUSER.DAT` activity attributed to Vanko in ART-007 of the original
case is the `defaultprinter` account's registry — which was Nina's session,
not Vanko's `PC User` account.

#### Event 2 — Vanko's own theft (2016-06-29 to 2016-06-30) [Pages 22-31]

Approximately 11 days after Nina's attack, Bulgakov (via intermediary Merrick)
recruited Vanko to steal classified research. Vanko:

1. Connected a **SanDisk Cruzer USB drive** (volume label "StarkResrch") to
   the StarkResearch shared server
2. Copied Level 5-8 Classified files from the server to `C:\Users\PC User\`
3. Used **PowerShell** to batch-rename classified files as "vacation photos"
   (e.g., `vacation_photo_01.jpg`) for concealment
4. Compressed the renamed files into a ZIP archive
5. Encrypted the archive with **VeraCrypt** (6 recorded runs in Prefetch)
6. Ran **SDelete** on the original classified directories to destroy evidence
7. Walked the USB drive to a meeting with Vladimir at the W Hotel (Washington
   DC), where Vladimir copied the files

**Vanko is MALICE for Event 2. He is not the perpetrator of Event 1.**

### Why the correction is warranted

The original JSON case conflated both events under Vanko's name. Specifically:

| Artifact | Original attribution | Correct attribution |
|----------|----------------------|---------------------|
| ART-001 `smallftpd.exe` | Vanko's exfiltration tool | Nina's RDP session (defaultprinter account) |
| ART-002 `ftpd.ini` | Vanko's persistent config | Nina's RDP session (defaultprinter account) |
| ART-003 `transfers.log` | Vanko's download at 22:21Z | Nina's download from 173.73.166.249 |
| ART-004 classified docs | Present on device | Present on device (true for both events) |
| ART-005 defaultprinter account | Vanko's masquerade account | Nina's account (created by Rubber Ducky) |
| ART-006 WiFi pcaps | Vanko's reconnaissance | Attributable to Vanko (still valid) |
| ART-007 NTUSER_defaultprinter | Vanko's activity 21:55-22:22Z | Nina's RDP session (not Vanko's profile) |

The `expected_verdict: MALICE` is correct *for Vanko's June 29-30 event*, but
the artifacts in the original JSON case are overwhelmingly from Nina's June 18
event. This is a category error: the wrong actor's artifacts are being used to
support a verdict that is correct for the right actor's separate event.

### Correction decision

**Decision: split into two cases** (per maintainer review 2026-07-14).

- **`VIGIA-REAL-VANKO-CORRECTED.json`** — Vanko's Event 2 (June 29-30 theft):
  USB exfiltration, PowerShell renaming, VeraCrypt encryption, SDelete
  anti-forensics. `expected_verdict: MALICE`.
- **`VIGIA-REAL-NINA.json`** — Nina's Event 1 (June 18 RDP attack):
  USB Rubber Ducky, defaultprinter account creation, FTP exfiltration,
  RDP from 173.73.166.249. `expected_verdict: MALICE`.

The original `VIGIA-REAL-VANKO.json` is **retired** (not deleted; kept for
historical reference and to document VIGÍA's original ABSTAIN on that evidence
set).

### VIGÍA behavior note (forensic value)

VIGÍA Mode 1 (deterministic core) emitted **ABSTAIN** on the original case
evidence (CyLR artifact set, 2026-07-14 run). This was the epistemically
correct posture:

- The CyLR collection does not include the StarkResearch server access
  (Event 2) — only the local device filesystem
- The June 18 artifacts (Nina's) are present but not attributable to Vanko
  by deterministic analysis alone
- The CCS tie (1/2) was genuine, not a scoring defect
- The B-132 fix (sdelete detection, z=3.2) correctly elevated the PREFETCH
  signal but could not break the tie without additional corroborating artifacts

VIGÍA's refusal to emit MALICE without sufficient attributable evidence is the
correct Daubert posture. The ABSTAIN result is preserved in
`results/VIGIA-REAL-VANKO-2026_bundle.json` and
`results/VIGIA-REAL-VANKO-2026-v2_bundle.json` as evidence of honest
calibration.

### Mode 2 interactive confirmation (2026-07-14)

Both corrected cases were also investigated in **Mode 2 (Claude Code + MCP
interactive)** with the full Peircean protocol (Firstness/Secondness/Thirdness +
Eco's Razor mandatory refutation) and independent CRONOS traces. Results:

| Case | Mode 2 verdict | Confidence | CRONOS trace | Chain |
|------|----------------|------------|--------------|-------|
| VIGIA-REAL-VANKO-CORRECTED | MALICE | 17/20 (85%) | `0ff8668d-1bc2-4cc8-abce-54fc225c1f86` | OK |
| VIGIA-REAL-NINA | MALICE | 17/20 (85%) | `46d19100-45f1-4123-94b8-8d0c48707a78` | OK |

Both verdicts agree with the deterministic engine (Mode 1). Full comparative
summary: `cronos/cronos_C001_modo2_comparativo_Claude_julio_2026-07-14.md`.
CRONOS audit trails saved to Desktop as `cronos_audit_VANKO-CORRECTED_Claude_julio_2026-07-14.md`
and `cronos_audit_NINA_Claude_julio_2026-07-14.md`.

Key MALICE differentiators confirmed in Mode 2:
- **VANKO-CORRECTED:** SDelete on Level 7-8 Classified server directories post-extraction
  (istat Allocated=0/Actual=0) — destruction of evidence, not mere exfiltration.
  Attributed to PC User account (not defaultprinter), refuting the Nina-planted argument.
- **NINA:** `security.evtx` copied to defaultprinter profile — Nina actively reviewed
  her own Windows Security Event Log traces (deliberate concealment). Corroborated by
  `7-8-USB-Analysis.pptx` (operational anti-detection reference material).

Known limitation: `validate_and_correct_analysis` Ollama backend degraded during Nina
investigation. Structural self-correction applied manually (4 Peirce checks passed).
Documented per Daubert honest-degradation posture.

---

*This file tracks corrections to case ground truth, not code defects.
Code defects are tracked in `BUGS_PENDIENTES.md`.*
