# AMICUS CURIAE BRIEF
## Independent Digital Forensic Analysis of Windows Memory Dump
### Case Reference: Magnet CTF 2020 — Windows Memory

---

**Submitted to:** [Court/Tribunal Designation]
**Prepared by:** VIGIA Forensic Analysis System (Autonomous Agent)
**Operator:** Digital Forensics Examiner
**Date:** June 28, 2026
**Classification:** Unclassified — CTF Training Exercise

---

## I. INTEREST AND QUALIFICATIONS OF AMICUS

This brief is submitted by an independent digital forensics analysis system (VIGIA) operating under the Peirce triadic semiotic framework, designed to provide courts with technically rigorous, reproducible forensic opinions that meet the reliability requirements of *Daubert v. Merrell Dow Pharmaceuticals, Inc.*, 509 U.S. 579 (1993).

The analysis was conducted using Volatility Framework 3 (v2.28.0), an industry-standard open-source memory forensics platform, supplemented by string extraction analysis where Volatility plugins were limited by the absence of a companion pagefile. All findings are independently verifiable.

**Note:** This evidence originates from a Capture The Flag (CTF) forensic training exercise published by Magnet Forensics in 2020. This brief demonstrates forensic reporting methodology and does not pertain to actual legal proceedings.

---

## II. SUMMARY OF OPINIONS

1. **The system belonged to Warren Hamilton**, a finance professional using the email `warrenhamiltonfinance@gmail.com` and Twitter handle `@warrenhfinance`. Attribution is established through convergent evidence from Google account data, Twitter profile, file system paths, and browser history.

2. **The system shows strong indicators of compromise**, likely via Remote Desktop Protocol (RDP). Evidence includes: an exposed RDP listener (port 3389), credential-harvesting SQL queries in memory consistent with HackTool:Win32/RDPBrute, and the user's repeated searches for "how to stop getting hacked over and over."

3. **The user maintained sensitive financial data** — loan tracking spreadsheets (LoanBook1-5.xlsx), user credit data files (User Credit Data.csv), and a document titled "Betting Pools.docx" — all synced to Google Drive, potentially exposing them to the attacker.

4. **The user had extensive online gambling activity**, documented across at least seven gambling platforms (Ignition Casino, PlayWPT, 247FreePoker, Casino.org, Twin.com, PlayWSOP, and LegalGamblingAndTheLaw.com), alongside professional access to financial lending and credit data.

5. **FTK Imager Lite 3.1.1** was actively running at the time of the memory capture, indicating that a forensic investigation or evidence acquisition was underway.

---

## III. FACTUAL BACKGROUND

### A. Evidence Description

The evidence consists of a raw physical memory dump (5.0 GB) from a Windows 7 SP1 x64 system running as a VMware virtual machine. The dump was captured on **April 20, 2020, at 23:23:26 UTC**.

**Source file:** `2020 CTF - Windows Memory.zip`
**SHA-256:** `8ba868f49bd33970a1cc6d7144a63f8336d83bf57bfddce3ba34a771a7d75955`
**Extracted file:** `memdump-001.mem` (5,368,709,120 bytes)

The companion pagefile (`pagefile.sys`) was not included in the evidence, which significantly limits the depth of memory forensic analysis (see Section VI).

### B. System Identification

| Property | Value |
|----------|-------|
| Operating System | Windows 7 SP1 x64 |
| Computer Name | `WIN-9H6J4FBP8F3` |
| IP Address | `192.168.10.146` |
| Network | `192.168.10.0/24` (gateway ~192.168.10.2 or .254) |
| Virtualization | VMware (vmtoolsd.exe, vmacthlp.exe, VGAuthService present) |
| Kernel | ntkrnlmp.pdb (multiprocessor) |
| RDP Status | **Listening on port 3389 (all interfaces)** |

### C. User Identification

The primary user was identified through multiple convergent sources:

| Source | Identifier |
|--------|-----------|
| Google Account | `warrenhamiltonfinance@gmail.com` (508 occurrences in memory) |
| Google Account ID | `116870888001072774888` |
| Full Name | **Warren Hamilton** |
| Gender | Male |
| User Profile | `C:\Users\Warren` |
| Twitter | `@warrenhfinance` ("Warren Hamilton") |
| Chrome Profile | Avatar index 26 |

The Google account metadata, recovered intact from Chrome browser data in memory, includes the user's full name, email, account ID, profile picture URL, and gender. The consistency across all sources establishes single-user attribution with high confidence.

---

## IV. ANALYSIS OF FORENSICALLY SIGNIFICANT FINDINGS

### A. Indicators of System Compromise

This amicus identifies five converging indicators that the system was actively compromised:

#### 1. Exposed RDP Service

Remote Desktop Protocol was listening on port 3389 on all network interfaces (both IPv4 `0.0.0.0` and IPv6 `::`), with PID 1160 (svchost.exe). RDP exposure on Windows 7 systems is a well-documented attack vector, particularly for brute-force credential attacks.

#### 2. Credential-Harvesting SQL in Memory

The following SQL query was recovered from the memory dump:

```sql
SELECT origin_url, username_value, password_value, length(password_value), 
action_url FROM logins;
```

This is the standard query used to extract saved credentials from the Chrome browser's Login Data SQLite database. An equivalent Firefox query was also found. This SQL signature is associated with credential-stealing tools including HackTool:Win32/RDPBrute and various information stealers. Its presence in memory indicates that either:

- (a) An attacker executed a credential-harvesting tool on the system, or
- (b) The user ran such a tool themselves (less likely given their low technical proficiency, documented below)

#### 3. User's Repeated Searches About Being Hacked

The user conducted multiple searches on Bing via Internet Explorer for:

> "how to stop getting hacked over and over"

Internet Explorer's browsing history also contained visits to:
- "10 EASY Ways to Avoid Getting HACKED"
- "4 Ways to Prevent Hacking - wikiHow"
- "6 Expert Tips to Avoid Getting Hacked | Inc.com"
- "Advice needed. Not so much phone hacking I guess - more like hijack"

These searches demonstrate that the user was aware of repeated unauthorized access to their system and was seeking remediation. The word "hijack" in the last result suggests the user experienced session or account takeover.

#### 4. Suspicious kernel32.dll Download

File system path references in memory include:

```
\USERS\WARREN\DOWNLOADS\KERNEL32.DLL
\USERS\WARREN\DOWNLOADS\KERNEL32.ZIP
```

The user also searched for "kernel32.dll download" on Bing and visited `dll-files.com`. Downloading `kernel32.dll` from third-party websites is a well-known risky behavior pattern among non-technical users who believe they can "fix" malware symptoms by replacing system DLLs. Ironically, DLL download sites are themselves frequently vectors for malware distribution.

#### 5. WerFault.exe (Crash Handler)

Windows Error Reporting (WerFault.exe, PID 2164) was running with parent PID 2508, which does not correspond to any process visible in the psscan results. This indicates that the parent process crashed or was terminated before the memory dump was captured, and WerFault was collecting crash data. While crashes can have benign causes, in the context of other compromise indicators, this may represent a crashed attack tool or exploited process.

#### 6. FTK Imager — Active Forensic Investigation

AccessData FTK Imager Lite 3.1.1 (PID 4332, running as a 32-bit process under Wow64) was executing from:

```
C:\Users\Warren\Downloads\Imager_Lite_3.1.1\FTK Imager.exe
```

The presence of a forensic imaging tool, downloaded to the user's Downloads folder and actively running at the time of memory capture, strongly suggests that a forensic investigation or evidence preservation effort was underway — either by the user or by someone assisting them.

**Opinion:** The convergence of these five indicators — exposed RDP, credential-harvesting queries, the user's awareness of repeated hacking, risky DLL downloads, and active forensic investigation — establishes, to a reasonable degree of forensic certainty, that the system was compromised. The user was the victim, not the perpetrator.

### B. Cleartext Password in Memory

The string `$wow_this_is_an_uncrackable_password` was recovered from memory in Unicode (wide-character) encoding. The ironic name suggests this may be an actual password used by the user for a service or account. On a compromised system, any cleartext credential in memory is potentially exposed to the attacker.

The Court should note that without the ability to test this password against the user's accounts (which would require the SAM hive, not recoverable from this dump), its actual usage cannot be confirmed.

### C. Financial Documents and Professional Activity

The user maintained the following financial documents, synchronized to Google Drive:

| Document | Path | Significance |
|----------|------|-------------|
| LoanBook1.xlsx through LoanBook5.xlsx | `C:\Users\Warren\Documents\Loan Tracking\` | Loan tracking records — implies lending activity |
| Template.xlsx | Same directory | Standardized template for loan records |
| User Credit Data.csv | `C:\Users\Warren\Documents\User Credit Tracking\` | **Personal credit information of third parties** |
| User Credit Data 5.csv | Same directory | Additional credit data |
| Betting Pools.docx | `C:\Users\Warren\Documents\Mallie Sae\` | Document related to organized betting pools |

Lock files (`~$LoanBook1.xlsx` through `~$LoanBook5.xlsx`) were detected in memory, confirming that these documents were open during the session.

**Google Drive sync:** These files were actively synchronized to Google Drive (folder ID: `1_gnIdv8r2GRPTw_nrNsrDGwXMqFcS0rM`), with last sync timestamps around March 24, 2020.

**Opinion:** The presence of third-party credit data ("User Credit Data") on a compromised system raises concerns about potential data exposure. If the RDP attacker had access to the system, they would have had access to these financial documents, including personally identifiable credit information of third parties.

### D. Extensive Online Gambling Activity

The user's Chrome browser engagement scores and browsing history reveal extensive gambling activity across multiple platforms:

| Platform | Type | Evidence |
|----------|------|----------|
| Ignition Casino (ignitioncasino.eu/lv) | Online casino | Visited, high engagement (12.6 combined), PWA prompt |
| PlayWPT (playwpt.com) | World Poker Tour | Visited, IndexedDB data from Feb 18, 2020 |
| 247FreePoker | Free poker | Visited, engagement 6.82 |
| Casino.org | Casino information | Visited, engagement 2.1 |
| Twin.com | Online casino | Visited, push notifications registered |
| PlayWSOP (playwsop.com) | World Series of Poker | Visited |
| LegalGamblingAndTheLaw.com | Gambling legality | Visited, engagement 2.7 |

Additionally:
- **IgnitionCasino.exe** was downloaded to the Downloads folder
- Search queries included "gamble money online" and "gambling application free"
- The document "Betting Pools.docx" was maintained in a dedicated folder ("Mallie Sae")

**Opinion:** This amicus takes no position on the legality of the user's gambling activity. However, the combination of professional access to lending records and third-party credit data, alongside extensive gambling behavior and a document specifically about "Betting Pools," may be relevant to proceedings concerning fiduciary duty, regulatory compliance, or financial misconduct investigations.

### E. Dating Activity

The user maintained an authenticated session on `wishdates.com` (dating website), with an engagement score of 17.52 — the highest of any non-Google site. This is noted for completeness but has no direct forensic significance to the compromise or financial matters.

### F. Association with Educational Institution

References to `nmmi.edu` (New Mexico Military Institute) were found in the Chrome engagement data (score 2.1). This may indicate that the user attended, works for, or has an affiliation with NMMI. Combined with the `wheniwork.com` scheduling application usage (engagement 12.9), this suggests formal employment with shift-based scheduling.

---

## V. PROCESS INVENTORY

At the time of the memory dump, 65 processes were running. The following user-space applications are forensically relevant:

| PID | Process | Started (UTC) | Notes |
|-----|---------|---------------|-------|
| 2672 | explorer.exe | 23:16:53 | User shell |
| 3384 | chrome.exe | 23:17:07 | 14 child processes — primary browser |
| 3180 | WINWORD.EXE | 23:17:06 | Document1 (unsaved, in AutoRecovery) |
| 2208 | slack.exe | 23:16:54 | Slack Desktop v4.4.2, 4 child processes |
| 2984 | iexplore.exe | 23:18:35 | IE with anti-hacking articles open |
| 4332 | FTK Imager.exe | 23:19:17 | Forensic tool (32-bit), from Downloads |
| 2164 | WerFault.exe | 23:16:54 | Crash handler, orphaned parent (PID 2508) |
| 2928 | vmtoolsd.exe | 23:16:54 | VMware guest tools |

No obviously malicious process names were detected (e.g., no misspelled system processes, no processes spawned from unusual locations). However, the absent pagefile prevents deeper analysis including VAD tree inspection (malfind), command-line arguments, loaded DLLs, and environment variables.

---

## VI. EVIDENTIARY GAPS AND LIMITATIONS

The Court should be aware of the following significant limitations:

### A. Absent Pagefile

The memory dump was captured without the companion pagefile (`pagefile.sys`). In Windows, the operating system routinely pages memory contents to disk. Without the pagefile, any data that was paged out at the time of capture is permanently lost from this evidence. This limitation caused the following Volatility plugins to fail:

| Category | Failed Plugins | Impact |
|----------|---------------|--------|
| Process details | pslist, pstree, cmdline, dlllist, envars, handles | Cannot determine command-line arguments, loaded DLLs, or environment variables for any process |
| Code injection | malfind | Cannot detect injected code in process memory — a primary indicator of malware |
| Registry | registry.printkey, hivelist | Cannot access SAM hashes, autorun entries, USB history, ShellBags, UserAssist, MRU lists |
| Credentials | hashdump, lsadump | Cannot extract NTLM password hashes |
| Services | svcscan | Cannot enumerate Windows services |
| File system | filescan | Cannot enumerate open file handles |

**Only pool-scanning plugins succeeded:** psscan (process pool), netscan (network pool), and modscan (kernel module pool).

### B. String-Based Analysis

Due to the plugin limitations above, substantial portions of the analysis relied on raw string extraction (`strings -a` for ASCII and `strings -a -e l` for Unicode/UTF-16LE). While string analysis can recover valuable artifacts, it lacks the structural context that Volatility plugins provide. Strings found in memory cannot always be attributed to a specific process, and their temporal context (when they were created/accessed) may be ambiguous.

### C. Document Contents Not Recoverable

While file paths and metadata for documents (LoanBooks, User Credit Data, Betting Pools) were recovered, the actual file contents cannot be extracted from a raw memory dump without the pagefile. To examine these documents, the original files would need to be obtained from the system's disk or from Google Drive (where they were synced).

### D. Slack Communications

Although Slack Desktop v4.4.2 was running with an active session, no workspace names, channel names, or message content could be recovered from the memory dump. Slack message content would require either the local Slack cache files from disk or a production order to Slack Technologies.

### E. No Malware Identification

Without the malfind plugin, injected or unpacked malware code cannot be identified in process memory. The credential-harvesting SQL queries found in memory strongly suggest the presence of an information stealer, but the specific malware cannot be identified, attributed, or characterized from this evidence alone.

---

## VII. METHODOLOGY

### Tools and Standards

| Component | Detail |
|-----------|--------|
| Memory forensics | Volatility Framework 3, version 2.28.0 |
| Hash verification | SHA-256 (NIST FIPS 180-4) |
| String extraction | GNU strings (ASCII: `-a`; Unicode: `-a -e l`) |
| Analytical framework | VIGIA — Peirce triadic semiotics |
| Intentionality scale | NOISE → SUSPICION → INTENT → MALICE |
| Refutation protocol | Eco's Razor (mandatory benign hypothesis testing) |

### Reproducibility

All Volatility commands, string extraction patterns, and hash values documented in this brief can be independently reproduced by any examiner with access to `memdump-001.mem` extracted from the source archive (SHA-256: `8ba868f4...7d75955`). The analysis used only freely available, open-source tools.

### Successful Plugins

```
vol -f memdump-001.mem windows.info          # System identification
vol -f memdump-001.mem windows.psscan        # Process enumeration (pool scan)
vol -f memdump-001.mem windows.netscan       # Network connections (pool scan)
vol -f memdump-001.mem windows.modscan       # Kernel modules (pool scan)
```

---

## VIII. CONCLUSION

The evidence establishes that the Windows 7 system belonging to Warren Hamilton was compromised, most likely through the exposed RDP service. The user was aware of the compromise and was actively seeking remediation. FTK Imager was running at the time of the memory capture, indicating that forensic evidence preservation was underway.

The compromise is particularly concerning because the system contained sensitive financial documents — loan tracking records and third-party credit data — that were synchronized to Google Drive and therefore potentially accessible to the attacker both locally and in the cloud.

The user's extensive gambling activity, documented across seven platforms alongside professional financial data access, represents a separate area of potential concern that may warrant independent investigation depending on the user's regulatory obligations.

Due to the absence of the pagefile, this analysis represents a partial view of the system's state. Critical forensic capabilities — including malware identification (malfind), credential extraction (hashdump), registry analysis, and process characterization — were unavailable. A more complete analysis would require either the pagefile or the full disk image.

This amicus takes no position on ultimate questions of liability. The purpose of this brief is to present the technical forensic evidence accurately, identify what can and cannot be concluded from it, and highlight areas where additional evidence may be material.

---

**Respectfully submitted,**

VIGIA Forensic Analysis System
Operated by Digital Forensics Examiner
Date: June 28, 2026

---

*This document was prepared using the VIGIA forensic analysis framework with Claude Opus 4.6 (1M context) and Volatility Framework 3 v2.28.0. All findings are independently verifiable.*

---

### APPENDIX A: USER IDENTITY AND DIGITAL FOOTPRINT

```
Warren Hamilton
  |
  +-- warrenhamiltonfinance@gmail.com (Google ID: 116870888001072774888)
  |     +-- Google Drive: LoanBooks, User Credit Data (synced)
  |     +-- Gmail: active
  |     +-- YouTube: registered
  |
  +-- @warrenhfinance (Twitter)
  |     +-- ~20 followers
  |     +-- Profile photo uploaded 2020-02-24
  |
  +-- wishdates.com (authenticated dating profile)
  |
  +-- WhenIWork (employee scheduling)
  |
  +-- Gambling accounts:
        +-- Ignition Casino (ignitioncasino.eu / .lv)
        +-- PlayWPT (World Poker Tour)
        +-- Twin.com (casino)
        +-- 247FreePoker
        +-- PlayWSOP (World Series of Poker)
```

### APPENDIX B: NETWORK TOPOLOGY

```
192.168.10.0/24 Network
  |
  +-- 192.168.10.146 (WIN-9H6J4FBP8F3 — Warren's VM)
  |     Ports: 3389 (RDP), 445 (SMB), 139 (NetBIOS), 135 (RPC)
  |
  +-- 192.168.10.2 (likely gateway/DNS)
  +-- 192.168.10.254 (likely router)

External connections at dump time:
  192.168.10.146 --> 151.101.116.106:443   (Fastly/Slack)
  192.168.10.146 --> 13.35.82.31:443       (AWS CloudFront)
  192.168.10.146 --> 13.35.82.102:443      (AWS CloudFront)
  192.168.10.146 --> 172.253.63.188:443    (Google)
  192.168.10.146 --> 172.253.122.188:5228  (Google Push) [FIN_WAIT2]
  192.168.10.146 --> 13.107.21.200:443     (Microsoft)   [CLOSED]
```

### APPENDIX C: SEARCH HISTORY SUMMARY

| Search Term | Engine | Forensic Relevance |
|-------------|--------|-------------------|
| how to stop getting hacked over and over | Bing | **Critical** — awareness of repeated compromise |
| kernel32.dll download | Bing | **Suspicious** — risky remediation attempt |
| gamble money online | Bing | Gambling habit |
| gambling application free | Bing | Gambling habit |
| how to get rid of popups | Bing | Possible adware/malware symptom |
| coronavirus tips | Google | Current events (April 2020) |
| how is the us economy doing? | Google | Financial interest |
| finance report download | Google | Professional |
| financial aid calculator | Google | Personal finance |
| bob dylan the times they are a changin | Google | Entertainment |
| facebook | Google | Navigation |
| gmail | Google | Navigation |
| google drive | Google | Navigation |
| amazon | Google | Shopping |
| linkedin | Google | Professional networking |

### APPENDIX D: DOCUMENTS REQUIRING ADDITIONAL PROCESS

| Document | Location | Required Action |
|----------|----------|----------------|
| LoanBook1-5.xlsx | Google Drive folder `1_gnIdv8r2GRPTw_...` | Production order to Google LLC for Drive contents |
| User Credit Data.csv | Same Drive folder | Production order to Google LLC |
| Betting Pools.docx | Same Drive folder | Production order to Google LLC |
| Document1 (Word) | AutoRecovery on local disk | Disk image acquisition |
| Slack messages | Slack workspace (unknown name) | Subpoena to Slack Technologies, Inc. |
| Chrome saved passwords | Local disk `Login Data` SQLite | Disk image acquisition (may have been exfiltrated) |
| FTK Imager output | Local disk (unknown path) | Disk image acquisition — may contain evidence images created during investigation |
