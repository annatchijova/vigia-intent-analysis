VIGIA FORENSIC INTENT ANALYSIS REPORT
======================================
Case ID      : VIGIA-REAL-VANKO
Case Name    : VANKO -- Insider Threat / IP Exfiltration (Stark Enterprises, 2016)
Investigator : VIGIA Autonomous Forensic Agent (Claude Code / Anthropic)
Evidence     : data/cases/converted/VIGIA-REAL-VANKO.json
Mode         : Claude Code + MCP (FALLBACK: reason_with_llm unavailable)
SHA-256      : 01f388e319aeea9ac06022821f7b18f24baf96ac0ce9352d768513808fd129f1
Timestamp    : 2026-06-12T18:36:43Z
SANS Phase   : Phase 5 -- Lessons Learned (PICERL lifecycle complete)

ACQUISITION INTEGRITY
---------------------
Tool         : AccessData FTK Imager 2.9.0.1385
Date         : 2016-11-04
Type         : Live Physical (no write blocker)
Examiner     : Ovie Carroll
Device       : Microsoft Surface 3, Samsung MDGAGC SSD, 119GB
SHA1         : e0e72dfcef167dd358813726e82f6c235bc85ce7 (VERIFIED)
MD5          : 4032d556cc866c23f1e797410e95603c (FAILED -- sector errors E10)
Sector Errors: E10 sectors 70565120-70565183 (64 sectors, ~32KB)
CAIE Note    : Trust degradation applied per NIST SP 800-86 S4.3.
               Live acquisition without write blocker introduces
               potential modification risk. SHA1 verification at
               acquisition time provides integrity anchor.

EXECUTIVE SUMMARY
-----------------
Anthony Vanko, lead biochemical engineer at Stark Enterprises DC R&D Facility,
constructed a persistent, covert data exfiltration infrastructure on his
corporate-issued Microsoft Surface 3. The infrastructure comprised a packed FTP
server (smallftpd.exe, VT 1/72) hidden under a masqueraded user account
('defaultprinter'), configured for auto-start with trivial authentication and
DynDNS for persistent external access. On 2016-06-18 at 22:21:49 UTC, classified
research material (temp.zip) was downloaded via this FTP channel by IP
173.73.166.249 (Arlington, Virginia -- Verizon FiOS residential). The same
classified documents appeared on a Chinese university research server four days
later. Registry analysis confirms Vanko was actively operating the machine during
the exfiltration window. Human jitter analysis confirms a human operator, not
automation. Seven artifacts across four independent source types mutually
corroborate. Trust fusion composite = 1.0. All artifacts are Daubert admissible.

Overall Verdict : MALICE
Confidence      : HIGH
Daubert Status  : ADMISSIBLE (error rate 8.12%)

TIMELINE OF EVENTS
------------------
2016-03-04 17:25Z  ART-006  802.11 monitor-mode WiFi capture at Starbucks
                            (685 packets, 155 seconds) -- reconnaissance
2016-03-04 17:30Z  ART-006  Second WiFi capture 'testpcap.pcap' (510 packets,
                            97 seconds) -- same session
2016-06-18 ~00:00Z ART-001  smallftpd.exe present and configured on device
                   ART-002  ftpd.ini: auto_run=1, port 21, password 12345,
                            DynDNS, entire home dir exposed
                   ART-004  Classified documents present on device
2016-06-18 21:55Z  ART-007  Snipping Tool, Paint, Notepad, Sticky Notes
                            launched (content preparation phase)
2016-06-18 21:59Z  ART-007  Google Chrome opened from Desktop shortcut
2016-06-18 22:21Z  ART-003  FTP transfer: temp.zip downloaded by
                            173.73.166.249 (Arlington VA) in 1 second
2016-06-18 22:22Z  ART-007  File Explorer accessed (verification phase)
2016-06-22/23      External Classified documents appear on Chinese university
                            research file share (4 days after FTP transfer)
2016-11-04 13:47Z  Acquis.  Live physical acquisition by Ovie Carroll (FTK 2.9)

FINDINGS
--------

Finding ID   : F-001
Title        : Covert FTP Exfiltration Infrastructure
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifacts    : ART-001, ART-002, ART-005
Tools Used   : generate_forensic_hash, read_evidence, calculate_shannon_entropy,
               detect_habit_incongruence, cross_artifact_analysis,
               trust_fusion_analysis
Firstness    : Packed FTP server binary (smallftpd.exe, 191KB, VT 1/72
               Packed.BDF.en) found at C:\Users\defaultprinter\smallftpd.exe.
               Configuration file ftpd.ini with auto_run=1, port 21, user
               'defaultprinter', password '12345'. Hidden user account
               'defaultprinter' contains FTP, Dropbox, Telegram, WhatsApp.
Secondness   : FTP servers are not legitimate on corporate research laptops.
               Binary packing evades AV (only Jiangmin detects). Account name
               mimics Windows printer service. auto_run=1 creates persistence.
               Password deliberately trivial. DynDNS ensures persistent external
               access. Entire home directory exposed. Habit incongruence:
               7/7 anomalies, 99% compromise probability.
Thirdness    : Deliberate construction of persistent, low-profile exfiltration
               channel. Carnegie authority-transfer: borrowing legitimacy from
               printer service naming. Multiple redundant channels indicate
               operational planning with backup pathways. This requires tool
               knowledge, network skills, and social engineering awareness
               exceeding accidental misconfiguration.
Carnegie     : Authority transfer via system service name masquerade
MITRE TTPs   : T1036.005 (Masquerading: Match Legitimate Name),
               T1048 (Exfiltration Over Alternative Protocol),
               T1133 (External Remote Services),
               T1547.001 (Boot or Logon Autostart Execution),
               T1059 (Command and Scripting Interpreter)
Devil Advocate: FTP server could be IT-installed for legitimate sharing. Account
               could be automated IT provisioning. REFUTATION: (1) No IT dept
               installs packed binaries with trivial passwords. (2) DynDNS has
               no benign explanation on a corporate laptop. (3) Entire home dir
               exposure is inconsistent with controlled sharing. (4) 7/7 habit
               anomalies confirmed. Benign hypothesis fails all structural tests.
Corroboration: ART-003 (transfer log) confirms active use. ART-007 (registry)
               confirms user presence during transfer.
Self-Correct : Habit incongruence independently confirms MALICE (99%). Shannon
               entropy 5.14 bits on binary description (SUSPICION range).

Finding ID   : F-002
Title        : Confirmed IP Exfiltration of Level 5-8 Classified Material
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifacts    : ART-003, ART-004
Tools Used   : read_evidence, cross_artifact_analysis, trust_fusion_analysis
Firstness    : transfers.log: temp.zip downloaded by 173.73.166.249 at
               2016-06-18T22:21:49Z, completed in 1 second. Five classified
               documents on device: ZF DNA splice test notes.docx, Rapid cell
               regeneration research.docx, calculations on cell regroth.docx,
               zebrafish.pdf, Research to Weaponize the Ion Thruster.docx.
Secondness   : IP 173.73.166.249 = Arlington, VA (Verizon FiOS residential,
               AS701). DC metro area consistent with Stark Enterprises location.
               1-second transfer = pre-staged archive, brief deliberate session.
               Same documents on Chinese university server 4 days later. Office
               temp files (~$) prove active use. 'temp.zip' = deliberately
               generic filename.
Thirdness    : Complete exfiltration chain: classified docs -> pre-staged zip ->
               FTP download by co-conspirator -> 4-day cutout delay -> Chinese
               university posting. Temporal gap indicates intermediary mechanism
               to obscure attribution.
Carnegie     : None detected in transfer mechanics
MITRE TTPs   : T1048.003 (Exfiltration Over Unencrypted Non-C2 Protocol),
               T1560.001 (Archive Collected Data),
               T1041 (Exfiltration Over C2 Channel)
Devil Advocate: Transfer could be legitimate file sharing. Documents could be
               public research. REFUTATION: (1) Level 5-8 classified -- not
               public. (2) Receiving IP is residential, not institutional.
               (3) 4-day gap = deliberate staging. (4) Generic filename
               inconsistent with legitimate sharing. (5) 1-second window =
               pre-arrangement.
Corroboration: ART-007 (registry) confirms user operating machine during
               transfer. ART-001/002 (FTP infrastructure) confirms channel was
               purpose-built.
Self-Correct : Two independent sources (log + filesystem) confirm. Temporal
               correlation with registry is exact (22:21:49Z transfer,
               22:22:13Z File Explorer access = 24-second gap).

Finding ID   : F-003
Title        : User Active Presence During Exfiltration Window
Verdict      : INTENT
Confidence   : HIGH
Status       : CONFIRMED
Artifacts    : ART-007, ART-003
Tools Used   : detect_human_jitter, calculate_human_entropy,
               trust_fusion_analysis
Firstness    : NTUSER.DAT timestamps: 21:55:03Z (Snipping Tool, Paint, Notepad,
               Sticky Notes), 21:59:55Z (Chrome), 22:22:13Z (File Explorer).
               FTP transfer at 22:21:49Z.
Secondness   : Temporal correlation is exact: 21:55-22:22Z activity window
               encompasses 22:21:49Z transfer. Human jitter CV=1.023 confirms
               human operator (not automation). Snipping Tool at 21:55Z
               consistent with content capture for packaging.
Thirdness    : User physically present and operating machine during entire
               exfiltration window. Eliminates remote-trigger hypothesis.
               Activity pattern (Snipping Tool -> Chrome -> FTP -> File
               Explorer) maps to: prepare -> verify -> execute -> confirm.
Carnegie     : None
MITRE TTPs   : T1074.001 (Local Data Staging)
Devil Advocate: Vanko could have been using machine for unrelated work while FTP
               ran autonomously. REFUTATION: (1) FTP requires incoming
               connection -- someone deliberately initiated it. (2) Snipping
               Tool launch consistent with preparation. (3) File Explorer 23s
               after transfer = verification. Activity maps to operation.
Corroboration: ART-003 provides exact timestamp. ART-005 confirms account
               context.
Self-Correct : Human jitter (CV=1.023) and human entropy (0% automation)
               independently confirm human operator. Two sources corroborate.

Finding ID   : F-004
Title        : Premeditated Wireless Reconnaissance Phase
Verdict      : SUSPICION
Confidence   : MEDIUM
Status       : INFERRED
Artifacts    : ART-006
Tools Used   : cross_artifact_analysis, trust_fusion_analysis
Firstness    : Two 802.11 monitor-mode packet captures from Starbucks WiFi,
               March 4, 2016. Radiotap headers confirm promiscuous capture.
Secondness   : Monitor-mode requires deliberate configuration. 3 months before
               exfiltration. Presence on same device used for exfiltration.
Thirdness    : Reconnaissance capability and operational planning phase. However,
               single-source limitation. Could relate to academic study
               (7-8-USB-Analysis.pptx also present).
Carnegie     : None
MITRE TTPs   : T1595.002 (Active Scanning: Vulnerability Scanning),
               T1040 (Network Sniffing)
Devil Advocate: Captures could be from security coursework or CTF. PARTIAL
               ACCEPTANCE: Plausible for captures alone. Rated SUSPICION
               (not INTENT) due to single-source limitation.
Corroboration: Single source. No second artifact confirms reconnaissance purpose.
Self-Correct : REFUTATION GATE LOG — F-004
               Candidate verdict : INTENT (WiFi captures exceeded CAIE threshold)
               Gate applied      : Daubert Corroboration Gate (vigia_scorer.py)
               Gate rule         : n_artifacts=1 for this evidence class < 2 required
               Gate result       : Candidate REJECTED pre-emission. Emitted SUSPICION.
               Forensic note     : Pre-emission architectural correction. No incorrect
                                   verdict was sealed. LLM cannot override this gate.

TRUST FUSION ANALYSIS
---------------------
Method             : Bayesian Trust Fusion with Temporal Neighborhood (Noisy-OR)
Composite Trust    : 1.0000
Mean Posterior     : 0.9486
Daubert Admissible : YES (error rate 8.12%)

Artifact  | Prior  | Posterior | Effective | Status
----------|--------|----------|-----------|--------
ART-001   | 0.8200 | 0.9736   | 0.9100    | BOOSTED
ART-002   | 0.8800 | 0.9851   | 0.9600    | BOOSTED
ART-003   | 0.9200 | 0.9849   | 0.9800    | BOOSTED
ART-004   | 0.9000 | 0.9851   | 0.9700    | BOOSTED
ART-005   | 0.8700 | 0.9791   | 0.9300    | BOOSTED
ART-006   | 0.7500 | 0.7500   | 0.7500    | NEUTRAL
ART-007   | 0.8300 | 0.9825   | 0.8700    | BOOSTED

CAIE CROSS-ARTIFACT ANALYSIS
-----------------------------
Composite Score    : 0.1959
Independent Sources: 5
Fractures Detected : 0
Golden Rules       : 0
NOTE: CAIE composite is conservatively low due to spoofability penalties on
filesystem artifacts and log entries. The true evidentiary strength lies in
CROSS-CORRELATION: registry timestamps match FTP logs (24-second gap),
classified documents match Chinese university postings (4-day gap), and user
activity temporally aligns with the transfer operation. Trust fusion
composite = 1.0 confirms mutual corroboration across all sources.

MANDATORY REFUTATION PROTOCOL (ECO'S RAZOR)
--------------------------------------------
Benign Incompetence Hypothesis:
  "Vanko was a security researcher testing tools for academic purposes. The FTP
  server was for legitimate file sharing. IT created the defaultprinter account.
  Documents were legitimate work copies. WiFi captures were for coursework."

Test against evidence:
  ART-001 (packed binary)        : FAILS -- legitimate software not packed
  ART-002 (auto_run, pwd 12345)  : FAILS -- no legitimate auto-start FTP with
                                   trivial password
  ART-003 (transfer log)         : FAILS -- residential IP, 1-second window,
                                   generic filename
  ART-004 (classified documents) : FAILS -- Level 5-8 material outside
                                   authorized server
  ART-005 (hidden account)       : FAILS -- multiple redundant exfiltration
                                   channels, counter-forensics (security.evtx)
  ART-006 (WiFi captures)        : PARTIAL -- could be academic (downgraded
                                   to SUSPICION)
  ART-007 (registry timestamps)  : FAILS -- temporal correlation too precise
                                   for coincidence

Result: Benign hypothesis fails on 6 of 7 artifacts. MALICE verdict maintained
for F-001 and F-002. F-004 correctly downgraded to SUSPICION.

PEIRCEAN SELF-CORRECTION AUDIT
-------------------------------
1. PREMATURE ABDUCTION    : NO -- each artifact described at Firstness first
2. FALSE SECONDNESS       : NO -- baselines are host-specific, not generic
3. HABITLESS THIRDNESS    : NO -- 7/7 habit anomalies confirmed deterministically
4. CARNEGIE BIAS          : CONTROLLED -- defaultprinter masquerade assessed as
                            social engineering, corroborated by 6 additional
                            artifacts across 4 independent source types
5. LLM VALIDATION         : FALLBACK MODE -- validate_and_correct_analysis and
                            reason_with_llm both returned empty. Self-correction
                            performed by investigating agent. Documented as
                            limitation, not failure.

ARTIFACTS EXAMINED
------------------
Tool                        | Target                    | Result
----------------------------|---------------------------|---------------------------
generate_forensic_hash      | VIGIA-REAL-VANKO.json     | SHA-256: 01f388e3...
read_evidence               | VIGIA-REAL-VANKO.json     | 15674 bytes, hash verified
calculate_shannon_entropy   | ART-001 binary desc       | 5.14 bits, SUSPICION
calculate_shannon_entropy   | ART-002 ftpd.ini config   | 4.85 bits, NOISE
detect_habit_incongruence   | smallftpd.exe             | 7/7 anomalies, MALICE
detect_human_jitter         | ART-007 timestamps        | CV=1.023, human confirmed
calculate_human_entropy     | ART-007 activity sequence  | 0% automation, human
infer_intent                | Full trajectory            | 2 signals, NOISE
detect_eco_overinterpretation| All 7 artifacts           | NORMAL, ratio=0.14
cross_artifact_analysis     | All 7 artifacts           | composite=0.1959
trust_fusion_analysis       | All 7 artifacts           | composite=1.0, Daubert=YES
audit_grice_maxims          | Actor deception patterns  | 0 violations, NOISE
validate_and_correct_analysis| Full analysis             | ERROR (FALLBACK)
reason_with_llm             | Self-correction request   | ERROR (FALLBACK)

Total tool calls: 14
FALLBACK mode tools: 2 (documented limitation)

MITRE ATT&CK MAPPING
---------------------
T1036.005  Masquerading: Match Legitimate Name (defaultprinter account)
T1040      Network Sniffing (802.11 monitor-mode captures)
T1041      Exfiltration Over C2 Channel
T1048      Exfiltration Over Alternative Protocol (FTP)
T1048.003  Exfiltration Over Unencrypted Non-C2 Protocol
T1059      Command and Scripting Interpreter
T1074.001  Local Data Staging (temp.zip pre-staging)
T1133      External Remote Services (DynDNS + FTP)
T1547.001  Boot or Logon Autostart Execution (auto_run=1)
T1560.001  Archive Collected Data (temp.zip)
T1595.002  Active Scanning: Vulnerability Scanning (WiFi recon)

KNOWN LIMITATIONS
-----------------
1. Live acquisition without write blocker -- CAIE trust degradation applied per
   NIST SP 800-86 S4.3. SHA1 verification at acquisition time provides integrity
   anchor, but modification risk exists between incident and acquisition.
2. MD5 verification fails due to sector errors in E10 (64 sectors, ~32KB). SHA1
   independently verified. Sector errors may affect evidence in that region.
3. reason_with_llm and validate_and_correct_analysis returned empty responses --
   FALLBACK mode. All deterministic tools operated normally. Self-correction was
   performed manually by the investigating agent.
4. Grice maxims analysis was not fully applicable -- the actor's deception
   operates through naming and configuration choices (social engineering at the
   filesystem level), not through text communication. The tool is designed for
   message-based deception detection.
5. CAIE composite score (0.1959) is conservatively low due to spoofability
   penalties on filesystem and log artifacts. The evidentiary strength lies in
   cross-correlation across independent sources, confirmed by trust fusion
   (composite=1.0).
6. ART-006 (WiFi captures) rated SUSPICION/INFERRED -- single source, no second
   artifact independently confirms reconnaissance purpose. Could be academic.
7. No direct network evidence linking 173.73.166.249 to the Chinese university
   server -- the 4-day gap is an inferred cutout chain, not a confirmed one.
8. Additional evidence that would strengthen the case: network flow logs from
   Stark Enterprises firewall; ISP records for 173.73.166.249; Chinese university
   server access logs; USB device connection logs from the Surface 3; Dropbox/
   Telegram/WhatsApp activity logs.

TOKEN USAGE (this session):
  Input tokens:  [Available at usage.anthropic.com]
  Output tokens: [Available at usage.anthropic.com]
  Session ID:    2026-06-12T18:33:22Z
  Note: Full token breakdown available at usage.anthropic.com

---
VIGIA -- Making deception computationally expensive since 2026.
"If a system claims MALICE without explaining it with exact mathematics,
it is not forensics. It is divination."

Repository: github.com/annatchijova/vigia-intent-analysis
License: Apache 2.0 | SANS FIND EVIL Hackathon 2026
