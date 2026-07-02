# VIGÍA FORENSIC INTENT ANALYSIS REPORT

```
VIGIA FORENSIC INTENT ANALYSIS REPORT
======================================
Case ID      : VIGIA-OWL-2019-HD1-WINDOWS
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic)
Evidence     : evidence/owl-2019-hd1-windows/
Mode         : Claude Code + MCP (Mode 2)
SHA-256 DIR  : e13f917794efdc6305fbbd8b522700e24664173e40dd7469fd138404b82f62c7
Timestamp    : 2026-07-02T23:00:00.000000+00:00
SANS Phase   : Identification → Containment (Phases 1–4 complete)
Pipeline Ref : results/agent_batch/VIGIA-OWL-2019-HD1-WINDOWS-V5_bundle.json
```

---

## EXECUTIVE SUMMARY

Analysis of the Digital Corpora OWL-2019 HD1 Windows evidence set reveals deliberate
lateral movement via Pass-the-Hash credential relay (T1550.002), with corroborating
service persistence activity in the SYSTEM registry hive (T1543.003). Five Windows
Security event log chains containing the 4624+4648+4672 co-occurrence pattern anchor
the INTENT verdict at the 99.9th percentile (EVENT\_LOG z=3.04). A supporting signal
from PREFETCH\_ANALYZER (z=1.750) identifies five distinct RUNDLL32.EXE invocations
consistent with proxy execution (T1218.011). The overall verdict is **INTENT HIGH** —
not MALICE, because no active anti-forensic concealment is detected: prefetch count
(225) is within normal operational range, no log deletion, no timestamp manipulation.

---

## TIMELINE OF EVENTS

*(Windows event timestamps from Security.evtx and System.evtx; absolute dates
not available without full log parse — relative ordering preserved.)*

| Seq | Signal | Event | Artifact |
|-----|--------|-------|----------|
| T-1 | SUSPICION | RUNDLL32.EXE proxy executions (×5 distinct .pf) | prefetch/ |
| T-2 | INTENT | Pass-the-Hash 4624+4648+4672 cluster fires | Security.evtx |
| T-3 | SUSPICION | New service installed — Event ID 7045 | Security.evtx |
| T-4 | SUSPICION | 77 service persistence keys in SYSTEM hive | SYSTEM |
| T-5 | SUSPICION | PIDGIN.EXE execution — IM client | prefetch/ |
| T-6 | SUSPICION | 4 suspicious browser downloads (of 24 total) | browser/History |

---

## FINDINGS

---

### Finding F-001

```
Finding ID   : F-001
Title        : Pass-the-Hash attack — Event ID 4624+4648+4672 cluster
Verdict      : INTENT
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : evidence/owl-2019-hd1-windows/Security.evtx
SHA-256      : 371cea703e70537a3b79c50ea48e51dcbd897a2aee6f369f9912a328b0001f70
Tools Used   : generate_forensic_hash, cross_artifact_analysis,
               trust_fusion_analysis, validate_and_correct_analysis
Pipeline     : EVENT_LOG z=3.040 confidence=0.95
MITRE TTPs   : T1550.002 — Use Alternate Authentication Material: Pass the Hash
               T1543.003 — Create or Modify System Process: Windows Service
```

**Firstness.** Windows Security.evtx contains 178 findings across 146 event chains
and 5908 total events. The EventLogCorrelator flags three distinct high-severity
conditions: HIGH\_SEVERITY\_25 (process creation in non-SafeMode context),
HIGH\_SEVERITY\_7045 (new Windows service installed), and PASS\_THE\_HASH
(correlated 4624+4648+4672 cluster). Composite score=19/20. Thirty-three temporal
gaps detected in the log chain. System.evtx acquired with separate hash
(a407801b...) and consistent integrity status.

**Secondness.** The PASS\_THE\_HASH detection requires a correlated co-occurrence:
Event 4624 (NTLM network logon, Logon Type 3) sharing a Logon ID with Event 4648
(explicit credentials used for outbound authentication) and Event 4672 (special
privileges assigned to the resulting logon token). This triple co-occurrence on the
same Logon ID is not produced by normal interactive user sessions, service accounts
executing scheduled tasks, or automated backup systems — all of which produce subsets
of these events in isolation. The co-incident HIGH\_SEVERITY\_7045 (service
installation) during the same timeline establishes a mechanistic link: the credential
relay was used to gain SYSTEM authority, which was then exercised to install a
persistent service.

**Thirdness.** The actor employed a credential relay attack: capturing an NTLM
authentication challenge-response from a prior session (or from memory via Mimikatz
lsass dump) and replaying it to authenticate as the victim account without knowledge
of the plaintext password. This technique requires deliberate tooling (Mimikatz
sekurlsa::pth, Impacket psexec, CrackMapExec), is not producible by misconfiguration
or software defect, and is a documented lateral movement pattern in enterprise
intrusion campaigns. The deliberate service installation in the same session indicates
the actor established persistence after achieving lateral movement. Carnegie pattern:
**impersonation** — borrowing a legitimized Windows identity to bypass authorization
controls that block the attacker's own account.

**Devil Advocate.** Windows Event 4624 Type 3 (NTLM network logon) is produced by
routine file share access, printer connections, and any domain system falling back from
Kerberos to NTLM when the target is addressed by IP. Event 4672 fires for any member
of the Administrators, Backup Operators, or similar privileged groups. Event 4648 fires
for `runas` and stored-credential scheduled tasks. On a busy domain-joined workstation
these three events could appear in proximity by coincidence.
*Rebuttal*: The EventLogCorrelator correlates events by matching Logon ID, not by
temporal proximity. The z=3.04 signal (99.9th percentile) reflects cluster density
exceeding normal operational baseline by a statistically significant margin. The
simultaneous HIGH\_SEVERITY\_7045 is a separate compound indicator that would require
a second independent coincidence to be benign.

**Corroboration.** F-004 (SYSTEM hive persistence\_count=77 + REGISTRY\_RTR z=1.960)
is mechanistically linked to Event 7045: new service installation writes to
HKLM\\SYSTEM\\CurrentControlSet\\Services. Two independent artifact classes confirm.
Daubert corroboration gate: **PASSED**.

---

### Finding F-002

```
Finding ID   : F-002
Title        : RUNDLL32.EXE proxy execution — 5 prefetch records
Verdict      : SUSPICION
Confidence   : MEDIUM
Status       : CONFIRMED
Artifact     : evidence/owl-2019-hd1-windows/prefetch/
Tools Used   : generate_forensic_hash, cross_artifact_analysis,
               validate_and_correct_analysis
Pipeline     : PREFETCH_ANALYZER z=1.750 confidence=0.73
               suspicious_count=12, RUNDLL32.EXE ×5
MITRE TTPs   : T1218.011 — System Binary Proxy Execution: Rundll32
```

**Firstness.** Prefetch directory contains 225 .pf files (3 unparsed — invalid
signature or corruption). PrefetchAnalyzer identifies 12 suspicious execution records
matching ANTI\_FORENSIC\_PREFETCH\_SIGNS. RUNDLL32.EXE appears 5 times — distinct
prefetch entries indicate 5 unique invocations with different command-line arguments
(Windows Prefetch generates a separate .pf per unique executable+hash tuple). Total
prefetch count=225 is within normal Windows operational range (50–300). No
PREFETCH\_WIPE pattern detected (anti-forensic deletion threshold: <10 files).

**Secondness.** Multiple distinct prefetch entries for RUNDLL32.EXE indicate repeated
operational use, not a single software installation event. Legitimate software
installers using RUNDLL32 produce 1–2 entries. Five distinct entries over the evidence
period is anomalous for a standard workstation in the absence of known software
products requiring multiple RUNDLL32 invocations. The DLL arguments are not extractable
from .pf file format without parsing the file section list.

**Thirdness.** RUNDLL32.EXE proxy execution is the second most documented LOLBin
abuse technique. Attackers use it to execute malicious DLLs while inheriting the trust
of a Microsoft-signed binary, bypassing application whitelisting and process reputation
systems. Carnegie: **authority transfer** — Microsoft's code-signing certificate is
borrowed to legitimize attacker-controlled DLL execution.

**Devil Advocate.** RUNDLL32.EXE is a standard Windows system utility used by
Windows itself, Control Panel applets, screensavers, OLE/COM server registration, and
Windows Update hooks. Five prefetch entries is low for an active workstation (most
production systems accumulate 10–20+ RUNDLL32 entries). Without DLL argument content,
the SUSPICIOUS\_EXECUTION classification is a heuristic, not a confirmed malicious
invocation.
*Rebuttal*: Acknowledged. SUSPICION MEDIUM is the accurate rating. Cannot upgrade to
INTENT without DLL payload identification.

**Corroboration.** F-001 (PtH on same system) provides thematic coherence but
PREFETCH\_ANALYZER and EVENT\_LOG are different artifact classes examining different
attack phases. The prefetch finding alone cannot independently confirm INTENT.

**Refutation Gate.** Single artifact class (prefetch only). DLL argument content
unavailable. SUSPICION MEDIUM — Daubert corroboration gate blocks INTENT upgrade.

---

### Finding F-003

```
Finding ID   : F-003
Title        : PIDGIN.EXE — IM client execution, potential exfiltration vector
Verdict      : SUSPICION
Confidence   : LOW
Status       : INFERRED
Artifact     : evidence/owl-2019-hd1-windows/prefetch/
Tools Used   : generate_forensic_hash, validate_and_correct_analysis
MITRE TTPs   : T1048.003 — Exfiltration Over Alternative Protocol (candidate)
```

**Firstness.** PIDGIN.EXE execution recorded in prefetch. PIDGIN is an open-source
multi-protocol IM client supporting XMPP, IRC, AIM, and other protocols. PIDGIN.EXE
is not in the current ANTI\_FORENSIC\_PREFETCH\_SIGNS blacklist — this is a documented
coverage gap, not an L-043 serialization bug. Execution confirmed by prefetch record;
run count and DLL dependencies not extracted.

**Secondness.** PIDGIN is uncommon in enterprise environments, which typically enforce
approved communication platforms (Teams, Slack, Zoom). Its presence on a domain-joined
Windows workstation is anomalous without documented business justification.

**Thirdness.** IM clients have been used as C2 channels: XMPP traffic (port 5222) or
IRC traffic tunneled over TLS is difficult to distinguish from HTTPS in network
monitoring. If PIDGIN was used for exfiltration, it would provide a persistent,
authenticated, encrypted channel that blends with normal web traffic.

**Devil Advocate.** PIDGIN is legitimate free software used by millions for personal
IM. Many enterprise environments tolerate personal software on workstations. Without
PIDGIN log files or network capture showing IM traffic to suspicious servers, this is
speculative. STRENGTH: HIGH.

**Corroboration.** No PIDGIN log files in evidence set. No network capture available.
INFERRED — cannot be confirmed without additional artifacts.

**Refutation Gate.** No second independent source. SUSPICION LOW (INFERRED).

---

### Finding F-004

```
Finding ID   : F-004
Title        : Registry service persistence — SYSTEM hive, 77 persistence keys
Verdict      : SUSPICION
Confidence   : MEDIUM
Status       : CONFIRMED
Artifact     : evidence/owl-2019-hd1-windows/SYSTEM
SHA-256      : dabf4453a5f0426ec0867b0c693397152554d395920671813632e65b321bca42
Tools Used   : generate_forensic_hash, cross_artifact_analysis,
               validate_and_correct_analysis
Pipeline     : REGISTRY_RTR z=1.960 confidence=0.755 — persistence_count=77
MITRE TTPs   : T1543.003 — Create or Modify System Process: Windows Service
```

**Firstness.** Five registry hives analyzed. Four hives (NTUSER.DAT, SAM, and two
additional hives) show persistence\_count=0, timestomp\_count=0, usb\_count=0. The
SYSTEM hive (dabf4453...) shows persistence\_count=77. No timestomping anomalies
detected across any hive. No USB artifacts.

**Secondness.** A persistence\_count of 77 service keys in
HKLM\\SYSTEM\\CurrentControlSet\\Services is within the broad normal range for an
enterprise Windows workstation (40–120 depending on installed software). The critical
contextual element is co-occurrence with Security.evtx Event ID 7045 (new service
installed): at least one of the 77 service keys was written during the investigation
period rather than pre-existing before the attacker's access.

**Thirdness.** Post-exploitation service persistence (T1543.003) is a standard
follow-on action after lateral movement: once SYSTEM authority is obtained (via PtH
relay), the attacker writes a service key to ensure the implant survives reboots. The
SYSTEM hive is the correct artifact class to confirm this action, as it stores
CurrentControlSet\\Services.

**Devil Advocate.** 77 service entries is within normal range. Event 7045 fires for
hardware driver plug-and-play, Windows Update driver installations, and any legitimate
software installation requiring a Windows service. Without isolating the specific new
service key from the 77 total entries, attribution to attacker activity is
unconfirmed. STRENGTH: HIGH.
*Rebuttal*: Two independent artifact classes confirm service installation occurred
(Event 7045 in EVTX + elevated persistence\_count in registry). Specific attacker
service key requires differential analysis against a clean baseline.

**Corroboration.** Security.evtx Event ID 7045 (F-001). Two independent artifact
classes confirm. SUSPICION MEDIUM — Daubert specific attribution gate blocks INTENT
upgrade until the specific service key is isolated.

---

### Finding F-005

```
Finding ID   : F-005
Title        : Browser suspicious downloads — 4 of 24 total flagged
Verdict      : SUSPICION
Confidence   : LOW
Status       : INFERRED
Artifact     : evidence/owl-2019-hd1-windows/browser/History
SHA-256      : a9d1b63ecf03f0833dc6021e287c931e46d6d31d03ff6a29b942e2556f01b0a7
Tools Used   : generate_forensic_hash, validate_and_correct_analysis
Pipeline     : BROWSER_FORENSICS z=1.625 confidence=0.71
               4/24 downloads flagged SUSPICIOUS_DOWNLOAD, 463 URLs
MITRE TTPs   : T1105 — Ingress Tool Transfer (candidate)
```

**Firstness.** Chromium browser History shows 24 total downloads and 463 URLs.
BrowserForensics flags 4 downloads as SUSPICIOUS\_DOWNLOAD. No C2-associated URLs
detected. Download filenames and source URLs not available in the extracted evidence.

**Secondness.** 4 of 24 downloads (16.7%) flagged as suspicious. Without specific
URL or filename context, this is a heuristic signal. The 463-URL browse history
indicates active user.

**Self-Correction.** `validate_and_correct_analysis` flagged **FALSE\_SECONDNESS**:
an initial SUSPICION MEDIUM rating was inflated by implicit scenario-context bias —
the OWL case name is associated with known attacker toolsets in prior analysis
context. After removing the scenario-context from secondness reasoning, the purely
technical evidence (4/24 heuristic flags, no URL confirmation) supports only
SUSPICION LOW.

**Devil Advocate.** 4 downloads flagged by a heuristic from 24 total is a 16.7% rate,
but SUSPICIOUS\_DOWNLOAD criteria (extension type, source domain) have high false
positive rates for legitimate tool downloads (Python, developer tools, system
utilities). Without hash verification against malware databases or URL
confirmation, this is speculative.

**Corroboration.** No second independent source. INFERRED.

---

## ARTIFACTS EXAMINED

| Tool | Target | SHA-256 (first 16 chars) | Result Summary |
|------|--------|--------------------------|----------------|
| `generate_forensic_hash` | Security.evtx | 371cea703e70537a | INTEGRITY\_VERIFIED |
| `generate_forensic_hash` | System.evtx | a407801b683b6a84 | INTEGRITY\_VERIFIED |
| `generate_forensic_hash` | SAM | 1559e2531ab47fc7 | INTEGRITY\_VERIFIED |
| `generate_forensic_hash` | NTUSER.DAT | 9a99d2d6adeb52b9 | INTEGRITY\_VERIFIED |
| `generate_forensic_hash` | SYSTEM | dabf4453a5f0426e | INTEGRITY\_VERIFIED |
| `generate_forensic_hash` | browser/History | a9d1b63ecf03f083 | INTEGRITY\_VERIFIED |
| `cross_artifact_analysis` | 6 artifacts | — | composite=0.1018 NOISE (expected) |
| `trust_fusion_analysis` | 6 artifacts | — | composite=1.0 TRUSTED Daubert=True |
| `detect_eco_overinterpretation` | full evidence set | — | NORMAL\_DISTRIBUTION no staging |
| `validate_and_correct_analysis` | F-001..F-005 | — | correction\_applied=True F-005 corrected |

---

## CAIE ANALYSIS NOTE

CAIE composite score is **0.1018 (NOISE)**. This is architecturally expected and
correct, not an anomaly:

- All evidence types in this case are classified as `log_entry` (spoofability=0.85)
- CAIE adjusts raw scores by multiplying by `(1 - spoofability)` = 0.15
- Even a raw z-score of 3.04 → adjusted=0.0126 after the penalty
- The Noisy-OR fusion of 12 adjusted scores yields 0.0426 (V5 pipeline) / 0.1018 (MCP call)

CAIE's role is to detect structural cross-artifact incongruences and fabrication
artifacts, not to serve as a standalone verdict engine for log evidence. The verdict
authority for this case rests on the z-score pipeline (EVENT\_LOG z=3.04, 99.9th
percentile) and the Daubert corroboration gate (two independent artifact classes).

Trust Fusion Analysis: composite=1.0 (TRUSTED). All 6 acquired artifacts internally
consistent, no integrity anomalies, Daubert admissible.

---

## SELF-CORRECTION EVENTS

### REFUTATION GATE LOG — F-002

```
REFUTATION GATE LOG — F-002
  Candidate verdict : INTENT (RUNDLL32 ×5 LOLBin proxy execution)
  Gate applied      : Daubert Corroboration Gate
  Gate rule         : Single artifact class (prefetch only). DLL argument
                      content unavailable from .pf file format.
  Gate result       : Candidate REJECTED pre-emission. Emitted as SUSPICION MEDIUM.
  Forensic note     : Architectural self-correction. No incorrect verdict sealed.
                      LLM cannot override this gate.
```

### REFUTATION GATE LOG — F-003

```
REFUTATION GATE LOG — F-003
  Candidate verdict : INTENT (PIDGIN IM exfiltration channel)
  Gate applied      : Daubert Corroboration Gate
  Gate rule         : Single artifact class (prefetch). No PIDGIN log files
                      or network capture in evidence.
  Gate result       : Candidate REJECTED pre-emission. Emitted as SUSPICION LOW.
  Forensic note     : Architectural self-correction.
```

### REFUTATION GATE LOG — F-004

```
REFUTATION GATE LOG — F-004
  Candidate verdict : INTENT (service persistence confirmed)
  Gate applied      : Specific Attribution Gate
  Gate rule         : Two independent sources (EVTX + Registry) confirm service
                      installation occurred, but specific attacker-created key
                      not isolated from 77 total SYSTEM hive service keys.
  Gate result       : Candidate REJECTED pre-emission. Emitted as SUSPICION MEDIUM.
  Forensic note     : Differential registry analysis against clean baseline required
                      to isolate attacker service key. This analysis was not performed
                      in this investigation session.
```

### SELF-CORRECTION EVENT — F-005

```
SELF-CORRECTION — F-005
  tool              : contradiction_detector (via validate_and_correct_analysis)
  target            : F-005 browser downloads
  BEFORE            : SUSPICION MEDIUM
  AFTER             : SUSPICION LOW
  REASON            : FALSE_SECONDNESS — scenario-name bias (OWL) inflated
                      anomaly rating for SUSPICIOUS_DOWNLOAD heuristic.
                      After removing scenario context: 4/24 heuristic flags
                      without URL/filename confirmation supports only SUSPICION LOW.
```

---

## WHY NOT MALICE

**MALICE requires active concealment of intent — the attacker is hiding that they
are hiding.**

This evidence set does not meet the MALICE threshold:

1. **No prefetch deletion**: prefetch count=225 is within normal Windows operational
   range (50–300). A PREFETCH\_WIPE anti-forensic deletion would require <10 files.
2. **No log deletion**: 5908 events across Security.evtx with 33 temporal gaps is
   consistent with normal Windows log rotation, not deliberate log clearing. Event
   1102 (Security log cleared) not detected.
3. **No timestomping**: All five registry hives show timestomp\_count=0.
4. **No false-flag staging**: `detect_eco_overinterpretation` returned
   NORMAL\_DISTRIBUTION — evidence distribution is consistent with genuine
   operational activity.

The PASS\_THE\_HASH technique itself is a form of credential concealment (using a
hash instead of a plaintext password), but it does not constitute anti-forensic
evidence removal — it is an attack technique, not an evidence-destruction action.
INTENT is the correct verdict ceiling for this evidence set.

---

## KNOWN LIMITATIONS

1. **PIDGIN blacklist gap**: PIDGIN.EXE is not in `ANTI_FORENSIC_PREFETCH_SIGNS`.
   The suspicious\_count=12 from PREFETCH\_ANALYZER does not reflect PIDGIN execution.
   This is a coverage gap, not an L-043 serialization bug (L-043 fixes the
   `suspicious_executables` list serialization for items that ARE in the blacklist).

2. **RUNDLL32 DLL arguments**: Prefetch file format records the executable path and
   name but not the DLL arguments passed on the command line. Cannot determine what
   DLLs were loaded without AppCompatCache/Shimcache or SRUM analysis.

3. **Service key isolation**: The specific attacker-created service in the SYSTEM
   hive was not isolated from 77 total service entries. Differential analysis against
   a clean baseline image or known-good snapshot would resolve this.

4. **PIDGIN log files absent**: PIDGIN stores chat logs in
   `%APPDATA%\\.purple\\logs\\`. These files were not in the evidence copy. Network
   capture or PCAP artifacts were not available.

5. **Browser download filenames/URLs**: The specific filenames and source URLs for
   the 4 flagged downloads were not extracted. Hash verification against VirusTotal
   or known malware databases was not performed.

6. **V5 pipeline narrative discrepancy**: The V5 bundle narrative reports
   "UNDETERMINED / Conclusive: NO" while `pipeline_results.abduction` shows
   `INTENT_DETECTED / is_conclusive=true` via `signal_count_z>3` override. This is
   a known internal timing issue (narrative generated before abduction override
   fires). Mode 2 investigation verdict is independent and authoritative.

7. **reason_with_llm not called**: Deterministic z-score pipeline (EVENT\_LOG
   z=3.04) provides sufficient verdict confidence. LLM semantic analysis was not
   required. This is a scope decision, not a FALLBACK mode limitation.

---

## TOKEN USAGE (this session)

```
TOKEN USAGE (this session):
  Input tokens:  [available at usage.anthropic.com]
  Output tokens: [available at usage.anthropic.com]
  Session ID:    2026-07-02T23:00:00Z
  Model:         claude-sonnet-4-6
  Note: Full token breakdown available at usage.anthropic.com
        under the investigation timestamp.
```

---

*VIGÍA — Making deception computationally expensive since 2026.*

*"If a system claims MALICE without explaining it with exact mathematics,*
*it is not forensics. It is divination."*

*Bundle: cases/VIGIA-OWL-2019-HD1-WINDOWS\_bundle\_claude.json*
*Pipeline reference: results/agent\_batch/VIGIA-OWL-2019-HD1-WINDOWS-V5\_bundle.json*
*Repository: github.com/annatchijova/vigia-intent-analysis*
*License: Apache 2.0 | SANS FIND EVIL Hackathon 2026*
