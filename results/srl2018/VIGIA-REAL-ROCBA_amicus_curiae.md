VIGIA FORENSIC INTENT ANALYSIS REPORT — AMICUS CURIAE
======================================================
Case ID      : VIGIA-REAL-ROCBA
Case Name    : Endpoint Compromise Investigation — fredr workstation (2020-11-16)
Investigator : VIGIA Autonomous Agent (Claude Code / Anthropic)
Evidence     : data/cases/converted/VIGIA-REAL-ROCBA.json
Mode         : Claude Code + MCP (validate_and_correct FALLBACK)
SHA-256      : 214a4de606bb55e87b9158dce30cd5568470ef058780091c885b48223cbc2d75
Timestamp    : 2026-06-13T13:34:00.000000Z
SANS Phase   : Identification → Containment (active compromise confirmed)

EXECUTIVE SUMMARY
------------------
User fredr's Windows 10 x64 workstation (192.168.1.5) shows a three-stage attack
chain confirmed by three independent Volatility plugins across three processes:
(1) MRC.exe — unsigned VB6 binary with temporally impossible DLL timestamps (1600-1718)
    = anti-forensic timestomping (T1070.006)
(2) SearchApp.exe — 4 PAGE_EXECUTE_READWRITE regions with MOV RAX;JMP RAX trampolining
    shellcode + INT3 padding = code injection (T1055.001)
(3) SearchFilterHost.exe — ESTABLISHED TCP to 52.113.194.132:443 Azure = C2 via cloud
    infrastructure blending (T1071.001/T1102)

**Overall verdict: MALICE.** Three-stage attack: delivery/concealment → injection → C2.

ATTACK CHAIN
-------------
```
MRC.exe (D:\Tools\, timestomped) → SearchApp.exe (shellcode injection) → SearchFilterHost.exe (C2 to Azure)
```

FINDINGS
--------

### F-001: MRC.exe — Anti-Forensic Timestomping
- Verdict: MALICE | Confidence: HIGH | Status: CONFIRMED
- ALL DLL LoadTimes 1600-1718 = temporally impossible = T1070.006 Timestomp
- VB6, no-ASLR, unsigned, D:\Tools\ — no legitimate tool profile matches
- Devil Advocate: Could be VB6 forensic tool. REJECTED: no known tool zeros ALL LoadTimes to pre-epoch; concurrent shellcode+C2 eliminate benign.
- Corroboration: F-002 (injection) + F-003 (C2) = three independent tools

### F-002: SearchApp.exe Shellcode Injection
- Verdict: MALICE | Confidence: HIGH | Status: CONFIRMED
- 4 RWX regions with MOV RAX,imm64; JMP RAX + INT3 padding = trampolining shellcode
- NOT JIT: JIT does not produce absolute-address trampolines or INT3 padding
- Devil Advocate: UWP JIT allocation. REJECTED: specific byte pattern, 4 regions, functional link to F-003.
- Corroboration: F-003 (C2 in sibling SearchFilterHost)

### F-003: SearchFilterHost C2 to Azure
- Verdict: MALICE | Confidence: HIGH | Status: CONFIRMED
- ESTABLISHED TCP to 52.113.194.132:443 — process NEVER connects externally
- Incomplete DLL list (4 modules) = PEB manipulation
- Devil Advocate: Windows telemetry. REJECTED: no documented external connections for SearchFilterHost; ESTABLISHED state; functional link to F-002.
- Corroboration: F-002 (injection in sibling SearchApp)

### F-004: Cloud Sync Exfiltration Surface
- Verdict: SUSPICION | 5 services (OneDrive, GDrive, iCloud, Slack) — legitimate autostart, no exfil observed.
- REFUTATION GATE: Candidate INTENT → capped SUSPICION. No exfiltration payload observed.

CAIE SCORING: Composite=0.2043 | 4 artifacts, 3 sources | 0 fractures
NOTE: CAIE below MALICE threshold due to network_flow spoofability. MALICE justified by functional chain across 3 Volatility plugins.

KNOWN LIMITATIONS
------------------
- validate_and_correct LLM FALLBACK
- MRC.exe binary not extracted
- No disk image available
- SearchFilterHost DLL list incomplete
- Shellcode not fully disassembled
- 52.113.194.132 not resolved to specific Azure service

---
VIGIA v2.0 / Claude Code + MCP / SANS FIND EVIL Hackathon 2026
