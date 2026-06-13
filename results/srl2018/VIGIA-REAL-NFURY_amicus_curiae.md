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
F-Response Enterprise live memory acquisition on 2012-04-06 — same day as confirmed
Zeus infection on adjacent workstation nromanoff (10.3.58.5). Two structural anomalies
identified: (1) WmiPrvSE.exe without filesystem path, highest MRI score, already exited;
(2) lsass.exe CLOSED RPC connections to unknown workstation 10.3.58.4.

**Overall verdict: SUSPICION.** No Zeus hooks, no hidden processes, no persistence
binaries. CAIE composite 0.1381 (NOISE). Two findings capped at SUSPICION by
Daubert Corroboration Gate — single-artifact evidence with strong benign alternatives.

FINDINGS
--------

### F-001: WmiPrvSE.exe without path (MRI 61, exited)
- Verdict: SUSPICION | Confidence: MEDIUM | Status: INFERRED
- Artifact: ART-001 | Tools: detect_habit_incongruence, cross_artifact_analysis
- Firstness: PID=2508, parent svchost 656, MRI 61, EXITED, no path
- Secondness: Missing path for exited process can be memory acquisition artifact
- Thirdness: WMI lateral movement (T1047) indistinguishable from legitimate WMI
- Devil Advocate: WmiPrvSE exits normally after queries. Path loss documented for exited processes. SCCM/GPO could produce identical pattern.
- Corroboration: None. Single-source INFERRED.

REFUTATION GATE: Candidate INTENT → capped SUSPICION. Single artifact, no payload/persistence corroboration.

### F-002: PPID anomaly csrss/winlogon → spoolsv
- Verdict: NOISE | Status: REFUTED
- PID reuse artifact. smss terminated, PID 432 recycled to spoolsv. Documented behavior.

### F-003: lsass.exe RPC to unknown 10.3.58.4
- Verdict: SUSPICION | Confidence: MEDIUM | Status: INFERRED
- Artifact: ART-003 | Tools: detect_habit_incongruence, cross_artifact_analysis
- Firstness: CLOSED connections to 10.3.58.4:135 and :49156
- Secondness: Normal for domain auth if 10.3.58.4 is a DC. Anomalous if peer workstation.
- Devil Advocate: Every Kerberos/NTLM request generates lsass RPC. 10.3.58.4 may be DC. Connections CLOSED. F-Response examiner also connected to 10.3.58.4:5681.
- Corroboration: None. Identity of 10.3.58.4 unknown.

REFUTATION GATE: Candidate INTENT → capped SUSPICION. Destination unknown, connections CLOSED.

### F-004: RDP 3389 listening
- Verdict: NOISE | Standard enterprise config. No active sessions.

CAIE SCORING: Composite=0.1381 | 4 artifacts, 3 sources | 0 fractures
NEGATIVE EVIDENCE: No Zeus hooks, no hidden processes, no persistence binaries, PPID explained.

KNOWN LIMITATIONS
------------------
- validate_and_correct LLM FALLBACK
- 10.3.58.4 identity unknown (critical gap)
- E01 disk image not processed
- Event logs not populated in .mans
- Prefetch not analyzed

---
VIGIA v2.0 / Claude Code + MCP / SANS FIND EVIL Hackathon 2026
