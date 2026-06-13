VIGIA FORENSIC INTENT ANALYSIS REPORT — AMICUS CURIAE
======================================================
Case ID      : VIGIA-REAL-NFURY
Case Name    : Stark Research Labs — Nick Fury / Lateral Movement Investigation (2012)
Investigator : VIGIA Autonomous Agent (Claude Code / Anthropic)
Evidence     : data/cases/converted/VIGIA-REAL-NFURY.json
Mode         : Claude Code + MCP (validate_and_correct FALLBACK)
SHA-256      : 2824eaaff943b5937a7653aaf1f157537c11c69a87faa32dce97db4d0a1c8596
Timestamp    : 2026-06-13T04:50:00.000000Z
SANS Phase   : Identification → Containment (lateral movement surface assessment)

EXECUTIVE SUMMARY
------------------
Nick Fury's executive workstation WKS-WIN764BITA (10.3.58.6) was analyzed via
F-Response Enterprise live memory acquisition on 2012-04-06 — the same day as a
confirmed Zeus banking trojan infection on the adjacent workstation nromanoff
(10.3.58.5). Two structural anomalies were identified: (1) WmiPrvSE.exe without
a filesystem path, highest MRI score, already exited — consistent with WMI-based
lateral movement but also with benign WMI administration; (2) lsass.exe CLOSED RPC
connections to an unknown third workstation 10.3.58.4 — consistent with credential
relay but also with normal domain authentication.

**Overall verdict: SUSPICION.** No Zeus hooks, no hidden processes, no persistence
binaries, and no active malicious sessions were detected. The CAIE deterministic
pipeline scored a composite of 0.1381 (NOISE threshold). Two findings were candidates
for INTENT but were capped at SUSPICION by the Daubert Corroboration Gate due to
single-artifact evidence with strong benign alternatives.

TIMELINE OF EVENTS
-------------------
| Timestamp (UTC)         | Event                                                    |
|-------------------------|----------------------------------------------------------|
| 2012-04-06T21:29:31Z    | F-Response Enterprise live memory acquisition of nfury   |
| 2012-04-06 (same day)   | Confirmed Zeus infection on nromanoff (10.3.58.5)        |
| 2012-04-06 (pre-acq)    | WmiPrvSE.exe PID=2508 executed and EXITED                |
| 2012-04-06 (pre-acq)    | lsass.exe PID=552 RPC to 10.3.58.4:135/49156 (CLOSED)   |
| 2012-04-06T21:29:31Z    | RDP 3389 LISTENING, no active sessions at snapshot        |
| 2012-04-09T17:07:13Z    | AccessData FTK Imager disk acquisition (E01)             |

FINDINGS
--------

### Finding F-001
Title          : WmiPrvSE.exe without filesystem path — highest MRI score, already exited
Verdict        : SUSPICION
Confidence     : MEDIUM
Status         : INFERRED
Artifact       : ART-001 (memory_process)
Tools Used     : detect_habit_incongruence, cross_artifact_analysis, detect_eco_overinterpretation
Firstness      : WmiPrvSE.exe (PID=2508) observed with parent svchost.exe (PID=656).
                 MRI score 61.0 — highest in system. Process had already EXITED at time
                 of memory acquisition. No filesystem path recorded in memory structures.
Secondness     : WmiPrvSE.exe normally resides at C:\Windows\System32\wbem\WmiPrvSE.exe
                 and spawns from svchost.exe (DcomLaunch group). Parent relationship is
                 NORMAL. Missing path for an exited process CAN be a memory acquisition
                 artifact — Windows may reclaim EPROCESS path information after process
                 termination. MRI score of 61 is elevated but reflects the missing-path
                 anomaly itself.
Thirdness      : WMI-based lateral movement (T1047) uses WmiPrvSE.exe as execution host
                 for remote payloads. Pattern: attacker executes via WMI, payload runs
                 inside WmiPrvSE, process exits after completion. However, this SAME
                 pattern occurs with legitimate WMI queries (SCCM, GPO, monitoring).
                 Single artifact insufficient to distinguish attack from administration.
Carnegie       : None detected — system-level artifact
MITRE TTPs     : T1047 (Windows Management Instrumentation)
Devil Advocate : WmiPrvSE.exe exits normally after completing WMI queries. Missing
                 filesystem path is documented behavior for exited processes in Windows 7
                 memory — the kernel reclaims EPROCESS structures. MRI score of 61 reflects
                 the missing-path anomaly itself, not independent evidence of compromise.
                 SCCM inventory, GPO enforcement, or enterprise monitoring could produce
                 this exact pattern. Without process memory dump or corroborating persistence
                 artifact, benign WMI activity cannot be excluded.
Corroboration  : No corroborating artifact found. No persistence binaries in Temp. No
                 shimcache data available. No prefetch analyzed. Single-source INFERRED.
Self-Correction: Daubert Corroboration Gate applied — see Refutation Gate Log below.

### Finding F-002
Title          : PPID anomaly — csrss.exe/winlogon.exe parent shows spoolsv.exe
Verdict        : NOISE
Confidence     : HIGH
Status         : REFUTED
Artifact       : ART-002 (memory_process)
Tools Used     : cross_artifact_analysis
Firstness      : csrss.exe (PID=440, MRI=58) and winlogon.exe (PID=480, MRI=47) both
                 show ParentPID=432, currently occupied by spoolsv.exe (print spooler).
Secondness     : csrss.exe and winlogon.exe are always spawned by smss.exe. This is a
                 DOCUMENTED Windows 7 memory forensics artifact: smss session process
                 creates csrss/winlogon then terminates; kernel recycles PID 432 to
                 spoolsv.exe. PPID field retains the original (now-stale) value.
Thirdness      : No deliberate pattern. Well-documented PID reuse artifact.
Carnegie       : None
MITRE TTPs     : None
Devil Advocate : N/A — NOISE verdict, refutation not required.
Corroboration  : PID reuse independently documented in Windows 7 memory forensics literature.
Self-Correction: Initial MRI scores (58, 47) flagged as elevated; full analysis confirmed
                 benign PID reuse. No further investigation warranted.

### Finding F-003
Title          : lsass.exe RPC connections to unknown workstation 10.3.58.4
Verdict        : SUSPICION
Confidence     : MEDIUM
Status         : INFERRED
Artifact       : ART-003 (network_flow)
Tools Used     : detect_habit_incongruence, cross_artifact_analysis, infer_intent
Firstness      : lsass.exe (PID=552) has CLOSED TCP connections to 10.3.58.4:135 (RPC
                 endpoint mapper) and 10.3.58.4:49156 (RPC dynamic endpoint). Connection
                 state is CLOSED — activity completed before acquisition.
Secondness     : lsass.exe outbound RPC to peer IP in same /24 as confirmed Zeus host
                 (nromanoff 10.3.58.5). Port 135 → dynamic port is standard Windows RPC
                 handshake. This is NORMAL for domain authentication (NTLM/Kerberos).
                 It is ALSO consistent with pass-the-hash (T1550.002) or credential relay.
                 Critical unknown: is 10.3.58.4 a domain controller? If yes, entirely
                 normal. If peer workstation, anomalous.
Thirdness      : In an active breach environment, lsass.exe RPC to unidentified lateral
                 IP raises the lateral movement hypothesis. Without identifying 10.3.58.4
                 and without authentication payload content, this is single-source with
                 strong benign alternative.
Carnegie       : None detected
MITRE TTPs     : T1550.002 (Pass the Hash), T1021.006 (Windows Remote Management)
Devil Advocate : lsass.exe connects to other hosts via RPC as part of NORMAL domain
                 authentication. Every Kerberos ticket request, NTLM challenge-response,
                 and group policy lookup generates lsass.exe outbound RPC. 10.3.58.4 may
                 be a domain controller, file server, or any domain member. Connections
                 are CLOSED — no active suspicious session. F-Response examiner also
                 connected to 10.3.58.4:5681, suggesting the IR team knew about this host
                 and may have acquired it as well.
Corroboration  : No corroborating artifact. No authentication logs. No shimcache or
                 prefetch for lateral tools. Event logs not populated in .mans.
Self-Correction: Daubert Corroboration Gate applied — see Refutation Gate Log below.

### Finding F-004
Title          : RDP TCP 3389 listening — lateral movement surface
Verdict        : NOISE
Confidence     : HIGH
Status         : CONFIRMED
Artifact       : ART-005 (network_flow)
Tools Used     : cross_artifact_analysis
Firstness      : TCP port 3389 (RDP) actively LISTENING on svchost.exe (PID=408). No
                 active RDP sessions in memory snapshot.
Secondness     : RDP listening is standard enterprise Windows configuration. No active
                 sessions means no RDP connection at acquisition time.
Thirdness      : RDP as lateral movement surface (T1021.001) is contextually relevant
                 during active breach but listening port alone is not an IoC.
Carnegie       : None
MITRE TTPs     : T1021.001 (Remote Desktop Protocol)
Devil Advocate : N/A — NOISE verdict.
Corroboration  : Standard Windows enterprise configuration confirmed.
Self-Correction: None required.

REFUTATION GATE LOG — F-001
----------------------------
  Candidate verdict : INTENT (habit_incongruence scored MALICE at 90%)
  Gate applied      : Daubert Corroboration Gate (CAIE cross-artifact analysis)
  Gate rule         : n_artifacts < 2 for WMI execution evidence class AND no
                      corroborating persistence/payload artifact → cap at SUSPICION
  Gate result       : Candidate REJECTED pre-emission. Emitted as SUSPICION.
  CAIE adjusted     : 0.0826 (memory_process spoofability=0.15, weight=0.30)
  CAIE composite    : 0.1381 (NOISE threshold)
  Forensic note     : Architectural self-correction. The habit_incongruence tool
                      treats all observed actions as anomalies without weighting
                      against benign baselines or requiring corroboration. The CAIE
                      deterministic pipeline applies spoofability penalties and
                      Noisy-OR fusion across independent sources, producing a score
                      well below the INTENT threshold. WmiPrvSE.exe without path
                      for an exited process is a documented memory analysis artifact.
                      No incorrect verdict was sealed. LLM cannot override this gate.

REFUTATION GATE LOG — F-003
----------------------------
  Candidate verdict : INTENT (habit_incongruence scored MALICE at 90%)
  Gate applied      : Daubert Corroboration Gate (CAIE cross-artifact analysis)
  Gate rule         : n_artifacts < 2 for credential relay evidence class AND
                      destination identity unknown AND connections CLOSED → cap
                      at SUSPICION
  Gate result       : Candidate REJECTED pre-emission. Emitted as SUSPICION.
  CAIE adjusted     : 0.0121 (network_flow spoofability=0.75, weight=0.18)
  CAIE composite    : 0.1381 (NOISE threshold)
  Forensic note     : Architectural self-correction. lsass.exe RPC to 10.3.58.4
                      carries extremely high spoofability (0.75) because network
                      flow data is trivially explained by normal domain operations.
                      The identity of 10.3.58.4 is unknown — if it is a domain
                      controller, this finding collapses entirely. CLOSED connection
                      state means the activity was not caught in-act. Without
                      authentication logs, shimcache of lateral tools, or event log
                      correlation, benign domain authentication cannot be excluded.
                      No incorrect verdict was sealed.

CONTRADICTION DETECTOR LOG
---------------------------
  Target: F-001/F-003 cross-tool consistency

  Check 1: detect_habit_incongruence MALICE (WmiPrvSE) vs CAIE NOISE (0.1381)
  Result : TOOL_SENSITIVITY_LIMITATION
  Reason : habit_incongruence treats all observed actions as anomalies without
           weighting against benign baselines. CAIE applies spoofability penalties
           and Noisy-OR fusion. CAIE adjusted score for WmiPrvSE=0.0826. Habit
           tool over-reports when input descriptions contain contextual metadata.

  Check 2: detect_habit_incongruence MALICE (lsass.exe) vs CAIE NOISE (0.1381)
  Result : TOOL_SENSITIVITY_LIMITATION
  Reason : lsass.exe RPC to peer workstations is within normal domain auth.
           CAIE network_flow spoofability=0.75 heavily penalizes this class.
           Habit tool lacks domain authentication baseline context.

  Check 3: infer_intent NOISE vs habit_incongruence MALICE
  Result : NO_CONTRADICTION
  Reason : infer_intent analyzes message-based communication trajectories.
           System-level forensic artifacts are outside tool applicability boundary.

  Check 4: Eco NORMAL_DISTRIBUTION vs habit_incongruence MALICE
  Result : CORROBORATING_NOISE
  Reason : No evidence staging detected. Normal distribution supports genuine
           operational artifacts, not attack fabrication.

  Contradictions found: 0
  Tool limitations documented: 2

NEGATIVE EVIDENCE (Eco's Significant Silence)
-----------------------------------------------
The following expected indicators of compromise are ABSENT from this system:

1. **No Zeus API hooks** — nromanoff (10.3.58.5) had confirmed Zeus with API
   hooking. This system shows NO hooked APIs in memory analysis.
2. **No hidden processes** — No DKOM or process unlinking detected.
3. **No persistence binaries** — Temp directories clean. No suspicious executables.
4. **No active malicious sessions** — RDP listening but no connections. lsass RPC
   connections CLOSED, not active.
5. **No shimcache anomalies** — Not available in .mans, but absence of positive
   indicators in available data is noted.
6. **PPID anomaly fully explained** — PID reuse artifact, not process injection.

This negative evidence is significant: if lateral movement had succeeded and
established persistence, we would expect at least some of these indicators. Their
collective absence supports SUSPICION (the system was a potential target surface)
rather than INTENT or MALICE (active compromise).

ARTIFACTS EXAMINED
-------------------
| Seq | Tool                         | Target                    | Result                           |
|-----|------------------------------|---------------------------|----------------------------------|
|  1  | generate_forensic_hash       | VIGIA-REAL-NFURY.json     | SHA-256 verified, chain intact   |
|  2  | read_evidence                | VIGIA-REAL-NFURY.json     | 5 artifacts loaded               |
|  3  | detect_habit_incongruence    | WmiPrvSE.exe (ART-001)    | MALICE 90% (overridden→SUSPICION)|
|  4  | detect_habit_incongruence    | lsass.exe (ART-003)       | MALICE 90% (overridden→SUSPICION)|
|  5  | detect_eco_overinterpretation| All 5 artifacts           | NORMAL_DISTRIBUTION, no staging  |
|  6  | infer_intent                 | ART-001/003/005 trajectory| NOISE, 0 signals                 |
|  7  | cross_artifact_analysis      | 4 artifacts, 3 sources    | NOISE, composite=0.1381          |
|  8  | validate_and_correct_analysis| Full evidence + analysis   | LLM empty (FALLBACK documented)  |

CAIE SCORING DETAIL
---------------------
| Artifact      | Type           | Raw Score | Spoofability | Weight | Adjusted |
|---------------|----------------|-----------|-------------|--------|----------|
| WmiPrvSE.exe  | memory_process | 0.72      | 0.15        | 0.30   | 0.0826   |
| PPID anomaly  | memory_process | 0.35      | 0.15        | 0.30   | 0.0402   |
| lsass RPC     | network_flow   | 0.60      | 0.75        | 0.18   | 0.0121   |
| RDP 3389      | network_flow   | 0.45      | 0.75        | 0.18   | 0.0091   |

Noisy-OR fusion: 3 independent groups → composite = 0.1381
Structural verdict: NOISE | Probabilistic verdict: NOISE
Fractures: 0 | Golden Rules: 0

RECOMMENDATIONS FOR FURTHER INVESTIGATION
-------------------------------------------
1. **Identify 10.3.58.4** — This is the highest-priority gap. If this IP is a
   domain controller, F-003 collapses to NOISE. If it is a peer workstation,
   F-003 escalates to INTENT.
2. **Process E01 disk image** — Registry hives (shimcache, amcache), MFT
   timeline, and event logs would provide corroboration or refutation for both
   F-001 and F-003.
3. **Analyze prefetch** — WmiPrvSE.exe execution count and timestamps would
   distinguish routine WMI activity from anomalous single execution.
4. **Cross-reference with nromanoff investigation** — If the Zeus C2 on
   nromanoff contacted 10.3.58.4 or 10.3.58.6, the lateral movement hypothesis
   strengthens significantly.
5. **Review F-Response acquisition of 10.3.58.4** — The examiner connected to
   10.3.58.4:5681, suggesting that system was also acquired. Its analysis may
   resolve the identity question.

KNOWN LIMITATIONS
------------------
1. validate_and_correct_analysis returned empty — LLM backend limitation.
   Deterministic pipeline results are authoritative.
2. Redline .mans has limited IOC coverage — no APT1 IOC set loaded.
3. Prefetch not analyzed — WmiPrvSE.exe execution history incomplete.
4. Event logs not populated in .mans — logon/authentication timeline unavailable.
5. E01 disk image not processed — registry, shimcache, MFT timeline pending.
6. 10.3.58.4 identity unknown — critical gap for F-003 assessment.
7. WmiPrvSE.exe process memory not dumped — payload content unverifiable.
8. No write blocker for memory acquisition (F-Response live) — documented.
9. infer_intent tool boundary — designed for communication analysis, not
   system-level artifacts. NOISE result reflects tool applicability, not
   absence of threat.

TOKEN USAGE (this session):
  Input tokens:  See usage.anthropic.com
  Output tokens: See usage.anthropic.com
  Session ID:    2026-06-13T04:50:00Z
  Note: Full token breakdown available at usage.anthropic.com

---
VIGIA v2.0 / Claude Code + MCP / SANS FIND EVIL Hackathon 2026
Sealed bundle: results/srl2018/VIGIA-REAL-NFURY_bundle.json
Evidence hash: 2824eaaff943b5937a7653aaf1f157537c11c69a87faa32dce97db4d0a1c8596
"If a system claims MALICE without explaining it with exact mathematics,
it is not forensics. It is divination."
