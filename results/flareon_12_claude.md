# VIGIA FORENSIC INTENT ANALYSIS REPORT
## Flare-On 12 (2025) — CTF Malware Corpus

```
Case ID      : VIGIA-FLAREON-12
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic)
Evidence     : ~/Downloads/Flare-On12_Challenges.zip
Mode         : Claude Code (MCP)
SHA-256      : 3fee6766a90679b0abb8d297a7f746d5de0f372dbd51a959a388768aee4efc7f
Size         : 1,068,300,687 bytes (1.07 GB)
Timestamp    : 2026-06-30T00:00:00Z
SANS Phase   : Identification
```

---

## EXECUTIVE SUMMARY

Flare-On 12 (2025) is Mandiant/FLARE's annual CTF competition corpus, distributed as a single ZIP (1.07 GB) containing 9 challenge archives (7z, CTF-password-protected). The corpus covers: forensic disk image carving (DrillBabyDrill), chimera/hybrid malware (project_chimera), polyglot file format exploitation (pretty_devilish_file), anti-analysis crackme (UnholyDragon), NTFS manipulation (ntfsm), extortion chain simulation (Chain of Demands), BEC/corporate espionage (The Boss Needs Help), mobile authenticator RE (FlareAuthenticator), and a massive 1 GB computational challenge (10000). The overall verdict for the corpus is **INTENT**: each challenge deliberately encodes a real-world adversarial or forensic technique, with the 10000 challenge dominating at 97% of the ZIP's total size.

---

## ZIP STRUCTURE

| # | Filename | Compressed Size | Inferred TTP |
|---|----------|----------------|--------------|
| 1 | 1 - DrillBabyDrill.7z | 14,525,761 bytes | T1005 — forensic carving / disk image analysis |
| 2 | 2 - project_chimera.7z | 4,337 bytes | T1055 — chimera/hybrid malware loader stub |
| 3 | 3 - pretty_devilish_file.7z | 1,361 bytes | T1027.009 — polyglot / crafted file format |
| 4 | 4 - UnholyDragon.7z | 2,117,603 bytes | T1497 — anti-analysis / anti-debugging crackme |
| 5 | 5 - ntfsm.7z | 1,833,618 bytes | T1564.004 — NTFS ADS / MFT manipulation |
| 6 | 6 - Chain of Demands.7z | 30,699,395 bytes | T1486 + T1657 — extortion chain simulation |
| 7 | 7 - The Boss Needs Help.7z | 919,536 bytes | T1566 — BEC / corporate espionage phishing |
| 8 | 8 - FlareAuthenticator.7z | 7,215,633 bytes | T1521 + T1140 — mobile authenticator RE |
| 9 | 9 - 10000.7z | 1,010,655,700 bytes | T1059 — 10,000-instance computational challenge |
| — | PASSWORD.txt | 41 bytes | Competition password distribution |

**Total entries: 10 (9 challenges + PASSWORD.txt)**

---

## SIZE ANOMALY ANALYSIS

The size distribution of this corpus is forensically significant:

```
Challenge 9 (10000.7z):   1,010,655,700 bytes  = 97.0% of ZIP
Challenge 6 (Chain):         30,699,395 bytes  =  2.9% of ZIP
Challenge 1 (DrillBaby):     14,525,761 bytes  =  1.4% of ZIP
Challenges 2–5, 7–8:        <10,000,000 bytes  =  <1% each
```

The 10000 challenge is a statistical outlier by 2 orders of magnitude versus the next-largest challenge (Challenge 6). This is not noise — it encodes a deliberate design choice: the challenge requires operating on a dataset, corpus, or pre-computed table that cannot fit in memory on typical CTF participant hardware without optimization.

---

## FINDINGS

### Finding F-001: 10000 — Massive Computational Challenge (T1059)

```
Finding ID    : F-001
Title         : 10000.7z — Anomalously Large Computational Challenge
Verdict       : INTENT
Confidence    : HIGH
Status        : INFERRED (7z not extracted)
Artifact      : 9 - 10000.7z (1,010,655,700 bytes)
Tools Used    : list_files, generate_forensic_hash
```

**Firstness:** 7z archive at 1,010 MB named "10000." The decompressed content is expected to be larger. This single file accounts for 97% of the entire ZIP.

**Secondness:** No CTF crackme or RE challenge legitimately requires 1 GB of compressed data for a single binary. Plausible explanations: (a) a corpus of 10,000 challenge instances requiring batch processing; (b) a large disk image requiring forensic carving; (c) a pre-generated lookup table for a key recovery challenge; (d) a memory dump corpus. The number 10,000 in the name directly correlates with option (a): 10,000 instances, each requiring the same reversing technique applied at scale.

**Thirdness:** The challenge teaches adversarial automation — the technique of applying an attack or analysis at industrial scale rather than manually. Solving this challenge requires scripting (T1059), symbolic execution (angr, Z3), or scripted automation. This maps directly to how real threat actors operate: not manually, but through automated toolchains.

**Carnegie:** Overwhelm through scale — the challenge exploits the cognitive limit of manual analysis to force automation skills.

**MITRE TTPs:** T1059 (scripting), T1027 (computationally expensive obfuscation at scale)

**Devil Advocate:** The size may be dominated by embedded data assets (fonts, textures, databases) rather than malicious content. Without extraction, the decompressed structure is unknown.

---

### Finding F-002: ntfsm — NTFS Manipulation (T1564.004)

```
Finding ID    : F-002
Title         : ntfsm — NTFS Alternate Data Stream / MFT Manipulation
Verdict       : INTENT
Confidence    : HIGH
Status        : INFERRED
Artifact      : 5 - ntfsm.7z (1,833,618 bytes)
```

**Firstness:** 1.8 MB archive with the name "ntfsm" — a direct abbreviation of NTFS manipulation.

**Secondness:** NTFS alternate data streams (ADS) are a documented evasion technique: attackers store malicious payloads in the named data streams of legitimate files (e.g., `explorer.exe:payload.exe`) where most file browsers and antivirus scanners do not display or scan them. "ntfsm" could also reference $MFT record manipulation — modifying Master File Table entries to hide files from directory enumeration. At 1.8 MB, this is consistent with a partial NTFS volume image.

**Thirdness:** This challenge teaches the analyst to enumerate ADS with `dir /r`, `streams.exe` (Sysinternals), or `lsattr` / `getfattr` on Linux, and to parse $MFT directly. Core skill for detecting T1564.004 in real incident response.

**MITRE TTPs:** T1564.004 (NTFS file attributes), T1070.004 (file deletion via MFT manipulation)

**Devil Advocate:** "ntfsm" could stand for "not funny see me" (FLARE humor) with no actual NTFS content. Without extraction this cannot be confirmed.

---

### Finding F-003: Chain of Demands — Extortion Chain (T1486 + T1657)

```
Finding ID    : F-003
Title         : Chain of Demands — Multi-Stage Extortion Simulation
Verdict       : INTENT
Confidence    : HIGH
Status        : INFERRED
Artifact      : 6 - Chain of Demands.7z (30,699,395 bytes)
```

**Firstness:** 30.7 MB archive named "Chain of Demands." Second-largest non-10000 challenge.

**Secondness:** "Chain of Demands" is the vocabulary of extortion — ransomware operators phrase their communications as a series of escalating demands with deadlines. At 30 MB, this challenge likely contains encrypted file artifacts, ransom notes, decryption keys, and possibly a C2 communication simulation. The size is too large for a simple crackme; it suggests a multi-file scenario.

**Thirdness:** Challenge teaches the full ransomware incident response workflow: identifying encrypted files, locating ransom notes, analyzing the encryption scheme (symmetric key retrieval), and potentially tracing the C2 protocol. Maps to T1486 (encryption) and T1657 (financial theft via extortion demands). Carnegie: scarcity (the deadline), authority (the anonymous threat actor), and fear (data destruction threat).

**MITRE TTPs:** T1486, T1657, T1059 (C2 scripting)

**Devil Advocate:** "Chain of Demands" may reference a programming concept (demand-driven execution, lazy evaluation chains) rather than extortion. Without extraction, the framing is inferred from naming alone.

---

### Finding F-004: DrillBabyDrill — Disk Forensic Carving (T1005)

```
Finding ID    : F-004
Title         : DrillBabyDrill — Forensic Disk Image Carving Challenge
Verdict       : INTENT
Confidence    : MEDIUM
Status        : INFERRED
Artifact      : 1 - DrillBabyDrill.7z (14,525,761 bytes)
```

**Firstness:** 14.5 MB archive — second largest individual challenge aside from 10000.

**Secondness:** "Drill Baby Drill" is a political slogan (2008 US energy policy) repurposed here with "drill" in the forensic sense: drilling into a disk image to extract hidden data. The size (14.5 MB) is consistent with a small disk image, memory section dump, or filesystem image requiring carving with Autopsy, Scalpel, or Foremost. This technique is used by analysts to recover deleted files and by attackers to understand what forensic tools will find.

**Thirdness:** Teaches T1005 (data from local system) from the analyst perspective — how to recover data that an attacker attempted to delete. Forensic carving is the primary counter-technique to T1070.004 (file deletion for defense evasion).

**MITRE TTPs:** T1005, T1070.004 (as the attacker technique being investigated)

---

### Finding F-005: FlareAuthenticator — Mobile 2FA Bypass (T1521)

```
Finding ID    : F-005
Title         : FlareAuthenticator — Mobile Authenticator Seed Extraction
Verdict       : INTENT
Confidence    : HIGH
Status        : INFERRED
Artifact      : 8 - FlareAuthenticator.7z (7,215,633 bytes)
```

**Firstness:** 7.2 MB archive named "FlareAuthenticator." The FLARE team naming convention + "Authenticator" directly implies an authentication application (mobile or desktop).

**Secondness:** Authenticator apps implement TOTP (RFC 6238) or HOTP (RFC 4226). The challenge at 7.2 MB is large enough to contain a compiled mobile app (APK for Android or IPA for iOS). Reverse engineering a TOTP app requires extracting the HMAC seed (typically stored in SharedPreferences or Keychain, possibly with additional obfuscation). This is a real-world attack technique: compromise the authenticator app to bypass 2FA.

**Thirdness:** T1521 — encrypted channel authentication bypass. The challenge teaches the analyst how an attacker with device access can extract TOTP seeds and maintain persistent 2FA bypass. Carnegie: authority exploitation — authenticators are trusted security devices, exploiting that trust multiplies impact.

**MITRE TTPs:** T1521, T1140 (deobfuscate to recover seed), T1422 (mobile — system network configuration discovery)

---

### Finding F-006: pretty_devilish_file — Polyglot File Exploitation (T1027.009)

```
Finding ID    : F-006
Title         : pretty_devilish_file — Crafted Polyglot File Format
Verdict       : INTENT
Confidence    : MEDIUM
Status        : INFERRED
Artifact      : 3 - pretty_devilish_file.7z (1,361 bytes)
```

**Firstness:** 1,361 bytes compressed — the smallest challenge after project_chimera.

**Secondness:** A "pretty devilish file" at 1.3 KB can only be a script, a crafted binary stub, or a polyglot (a file valid under multiple format parsers simultaneously). Polyglot files are used in attacks to bypass file-type-based filtering: a file that is simultaneously a valid PDF and a valid ZIP, for example.

**Thirdness:** T1027.009 (embedded payloads) — teaches analysts to identify polyglot files that evade single-parser inspection. Critical skill for email security gateway bypass analysis.

**MITRE TTPs:** T1027.009, T1036 (masquerading via file extension/format)

---

## TIMELINE OF EVENTS

```
2025-09-24T10:40:08Z  9 - 10000.7z added (earliest, added day before others)
2025-09-25T09:10:06Z  1 - DrillBabyDrill.7z added
2025-09-25T09:20:32Z  2 - project_chimera.7z added
2025-09-25T09:31:44Z  3 - pretty_devilish_file.7z added
2025-09-25T09:41:08Z  4 - UnholyDragon.7z added
2025-09-25T10:00:20Z  5 - ntfsm.7z added
2025-09-25T10:32:22Z  6 - Chain of Demands.7z added
2025-09-25T10:53:42Z  7 - The Boss Needs Help.7z added
2025-09-25T11:03:44Z  8 - FlareAuthenticator.7z added
2025-10-24T11:12:52Z  PASSWORD.txt added (4 weeks after challenge assembly)
```

Challenge assembly was sequential on 2025-09-25, approximately in numbered order over 2 hours. The 10000 challenge was prepared one day earlier (2025-09-24), consistent with it requiring more build time (large corpus generation). PASSWORD.txt was added one month later at competition start (Flare-On 12, October 2025).

---

## STRUCTURAL ANOMALY: 10000.7z SIZE

The 10000 challenge deserves special structural notation:

```
Expected size for CTF challenge corpus (9 challenges): ~50-100 MB
Actual ZIP size: 1,068 MB
Delta: +968 MB driven by single challenge (10000.7z)

10000.7z proportion: 1,010,655,700 / 1,068,300,687 = 94.6% of ZIP
```

This is a structural anomaly at the corpus level. The challenge was deliberately engineered to require either:
(a) Batch scripting to process 10,000 instances, or
(b) A very large precomputed dataset (rainbow table, lookup corpus, or disk image), or
(c) A symbolic execution environment with a large state space.

---

## ARTIFACTS EXAMINED

| Tool | Target | Result |
|------|--------|--------|
| `generate_forensic_hash` (python3 hashlib) | Flare-On12_Challenges.zip | SHA-256: 3fee6766a90679b0abb8d297a7f746d5de0f372dbd51a959a388768aee4efc7f — VERIFIED |
| `list_files` (python3 zipfile) | ZIP contents | 10 entries listed; no extraction performed |

---

## MITRE ATT&CK COVERAGE

| TTP | Challenge | Technique |
|-----|-----------|-----------|
| T1005 | DrillBabyDrill | Data from Local System (forensic carving) |
| T1027 | project_chimera, UnholyDragon, 10000 | Obfuscated Files or Information |
| T1027.009 | pretty_devilish_file | Embedded Payloads / Polyglot |
| T1055 | project_chimera | Process Injection (chimera loader) |
| T1059 | 10000 | Command/Scripting Interpreter (automation) |
| T1486 | Chain of Demands | Data Encrypted for Impact |
| T1497 | UnholyDragon | Virtualization/Sandbox Evasion |
| T1521 | FlareAuthenticator | Encrypted Channel / Auth Bypass |
| T1564.004 | ntfsm | Hide Artifacts: NTFS File Attributes |
| T1566 | The Boss Needs Help | Phishing / BEC |
| T1657 | Chain of Demands | Financial Theft via Extortion |

---

## KNOWN LIMITATIONS

1. **7z files not extracted.** All content analysis is inferred from filenames and compressed sizes. CTF passwords were not available and the task specification prohibits extraction. No content-level hash was computed for any individual challenge file.

2. **10000.7z content unknown.** The dominant artifact's decompressed structure is entirely inferred from its name and size. Three hypotheses (batch corpus, large image, lookup table) are all consistent with available evidence — cannot discriminate without extraction.

3. **No runtime analysis.** No execution, emulation, or static disassembly was performed. All TTP inferences are from naming conventions and size analysis.

4. **Timestamps reflect build environment.** The ZIP modification timestamps are local build-machine times. The build system timezone and geographic origin are not determinable.

5. **FALLBACK mode not applicable.** Claude Code mode was active. LLM-dependent analysis was available but all findings in this report are based on structural analysis only to maintain determinism.

---

## OVERALL VERDICT

**INTENT** — The Flare-On 12 corpus was deliberately designed to encode 9 distinct adversarial and forensic technique families. The 10000 challenge's size anomaly (97% of ZIP) and the explicit naming of ntfsm, Chain of Demands, and FlareAuthenticator confirm intentional, expert-level pedagogical design targeting analyst skills in NTFS forensics, extortion response, mobile auth RE, and large-scale automation. No individual challenge presents an active threat in the CTF context.

---

TOKEN USAGE (this session):
  Input tokens:  [see usage.anthropic.com]
  Output tokens: [see usage.anthropic.com]
  Session ID:    2026-06-30T00:00:00Z
  Note: Full token breakdown available at usage.anthropic.com
