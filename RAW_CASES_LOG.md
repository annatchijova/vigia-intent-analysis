# RAW_CASES_LOG — VIGIA Forensic Agent: Raw Evidence Investigation Catalog

> **Catalog note:** This document is a per-case catalog of VIGIA autonomous agent
> investigations on real forensic corpora. It is NOT an accuracy aggregate.
> Each case is an individual investigation with its own evidence context,
> extraction method, and findings. This mirrors the Domain C doctrine in
> `README.md`: raw evidence results are measured per case, not as a corpus-wide
> number.
>
> At README publication (2026-07-14): **43 distinct raw evidence sources**
> (SRL-2018: 22 memory images, MUS2019/Narcos: 13 dumps, M57-Patents: 3,
> NPS-2010/2014, Magnet 2020 CTF, Tuck 2019 macOS, Vanko).
> All subsequent raw-evidence runs are also cataloged here.
> Synthetic, adversarial, and JSON-only test cases are excluded;
> those are tracked in `data/cases/` and the 199-case batch corpus.

## SRL-2018 — Corporate Intrusion (original Volatility3 runs)

Original Mode 1 runs on raw `.img` memory files. `PIPELINE_ERROR`/`ABSTAIN`
entries indicate Volatility3 plugin unavailable for that memory profile;
superseding JSON-converted runs appear in the 'SRL-2018 (rerun)' section below.

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `ADMIN-001` | Admin server memory | 2026-05-29 | **MALICE** | 14/25 | Volatility3 memory analysis: 3 signals from base-admin-memory.img. Average inten | [ADMIN-001_bundle.json](results/srl2018/ADMIN-001_bundle.json) | canonical run |
| `AV-001` | AV server memory (first run) | 2026-05-29 | **MALICE** | 14/25 | Volatility3 memory analysis: 3 signals from base-av-memory.img. Average intentio | [AV-001_bundle.json](results/srl2018/AV-001_bundle.json) | superseded by AV-003 |
| `AV-003` | AV server memory (latest) | 2026-06-02 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-av-memory.img. Average intentio | [AV-003_bundle.json](results/srl2018/AV-003_bundle.json) |  |
| `DC-MEM-001` | Domain Controller memory | 2026-06-01 | **ABSTAIN** | N/A | [ERROR] RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta. | [DC-MEM-001_bundle.json](results/srl2018/DC-MEM-001_bundle.json) | PIPELINE_ERROR; see DC-MEM-005 |
| `DC-MEM-005` | Domain Controller memory (run 5) | 2026-06-02 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-dc-memory.img. Average intentio | [DC-MEM-005_bundle.json](results/srl2018/DC-MEM-005_bundle.json) | latest DC run |
| `ELF-001` | ELF server memory | 2026-06-01 | **ABSTAIN** | N/A | [ERROR] RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta. | [ELF-001_bundle.json](results/srl2018/ELF-001_bundle.json) | PIPELINE_ERROR; see ELF-003 |
| `ELF-003` | ELF server memory (run 3) | 2026-06-02 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-elf-memory.img. Average intenti | [ELF-003_bundle.json](results/srl2018/ELF-003_bundle.json) |  |
| `FILE-001` | FILE server | 2026-06-01 | **ABSTAIN** | N/A | [ERROR] RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta. | [FILE-001_bundle.json](results/srl2018/FILE-001_bundle.json) | PIPELINE_ERROR; see FILE-003 |
| `FILE-003` | FILE server (run 3) | 2026-06-02 | **SUSPICION** | 0 | Volatility3 memory analysis: 0 signals from base-file-memory.img. Average intent | [FILE-003_bundle.json](results/srl2018/FILE-003_bundle.json) |  |
| `HUNT-001` | Hunt system memory | 2026-06-01 | **ABSTAIN** | N/A | [ERROR] RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta. | [HUNT-001_bundle.json](results/srl2018/HUNT-001_bundle.json) | PIPELINE_ERROR; see HUNT-005 |
| `HUNT-005` | Hunt system memory (run 5) | 2026-06-02 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-hunt-memory.img. Average intent | [HUNT-005_bundle.json](results/srl2018/HUNT-005_bundle.json) |  |
| `MAIL-001` | Mail server memory | 2026-06-03 | **MALICE** | 17/50 | Volatility3 memory analysis: 3 signals from base-mail-memory.img. Average intent | [MAIL-001_bundle.json](results/srl2018/MAIL-001_bundle.json) |  |
| `MAIL-002` | Mail server memory (latest) | 2026-06-04 | **MALICE** | 33/100 | Volatility3 memory analysis: 2 signals from base-mail-memory.img. Average intent | [MAIL-002_bundle.json](results/srl2018/MAIL-002_bundle.json) |  |
| `RD01-001` | Remote Desktop RD01 | 2026-06-03 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-rd01-memory.img. Average intent | [RD01-001_bundle.json](results/srl2018/RD01-001_bundle.json) |  |
| `RD02-001` | Remote Desktop RD02 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-rd-02-memory.img. Average inten | [RD02-001_bundle.json](results/srl2018/RD02-001_bundle.json) |  |
| `RD03-001` | Remote Desktop RD03 | 2026-06-03 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-rd-03-memory.img. Average inten | [RD03-001_bundle.json](results/srl2018/RD03-001_bundle.json) |  |
| `RD04-001` | Remote Desktop RD04 | 2026-06-03 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-rd-04-memory.img. Average inten | [RD04-001_bundle.json](results/srl2018/RD04-001_bundle.json) |  |
| `RD05-001` | Remote Desktop RD05 | 2026-06-01 | **ABSTAIN** | N/A | [ERROR] RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta. | [RD05-001_bundle.json](results/srl2018/RD05-001_bundle.json) | PIPELINE_ERROR; see RD05-003 |
| `RD05-003` | Remote Desktop RD05 (run 3) | 2026-06-02 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-rd-05-memory.img. Average inten | [RD05-003_bundle.json](results/srl2018/RD05-003_bundle.json) |  |
| `RD06-001` | Remote Desktop RD06 | 2026-06-03 | **MALICE** | 41/150 | Volatility3 memory analysis: 3 signals from base-rd-06-memory.img. Average inten | [RD06-001_bundle.json](results/srl2018/RD06-001_bundle.json) |  |
| `SP-001` | SharePoint server memory | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-sp-memory.img. Average intentio | [SP-001_bundle.json](results/srl2018/SP-001_bundle.json) |  |
| `WKSTN01-001` | Workstation 01 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-wkstn-01-memory.img. Average in | [WKSTN01-001_bundle.json](results/srl2018/WKSTN01-001_bundle.json) |  |
| `WKSTN02-001` | Workstation 02 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-wkstn-02-memory.img. Average in | [WKSTN02-001_bundle.json](results/srl2018/WKSTN02-001_bundle.json) |  |
| `WKSTN03-001` | Workstation 03 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-wkstn-03-memory.img. Average in | [WKSTN03-001_bundle.json](results/srl2018/WKSTN03-001_bundle.json) |  |
| `WKSTN04-001` | Workstation 04 | 2026-06-03 | **MALICE** | 34/75 | Volatility3 memory analysis: 3 signals from base-wkstn-04-memory.img. Average in | [WKSTN04-001_bundle.json](results/srl2018/WKSTN04-001_bundle.json) |  |
| `WKSTN05-001` | Workstation 05 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-wkstn-05-memory.img. Average in | [WKSTN05-001_bundle.json](results/srl2018/WKSTN05-001_bundle.json) |  |
| `WKSTN06-001` | Workstation 06 | 2026-06-03 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from base-wkstn-06-memory.img. Average in | [WKSTN06-001_bundle.json](results/srl2018/WKSTN06-001_bundle.json) |  |

## SRL-2018 — Corporate Intrusion (JSON-converted reruns, 2026-07-13)

Same corpus, re-run via `vigia_agent.py` on JSON-converted case files.
These supersede the `PIPELINE_ERROR` entries above and reflect B-127 fixes.

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `VIGIA-REAL-SRL-ADMIN` | Admin server (JSON rerun) | 2026-07-13 | **MALICE** | 81/100 | SRL-2018 compromised enterprise network. Admin server memory dump (5 GB, 2018-09 | [VIGIA-REAL-SRL-ADMIN_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-ADMIN_agent_bundle.json) | supersedes ADMIN-001 |
| `VIGIA-REAL-SRL-AV` | AV server (JSON rerun) | 2026-07-13 | **MALICE** | 41/50 | SRL-2018 compromised enterprise network. AV server memory dump (9 GB, 2018-09-07 | [VIGIA-REAL-SRL-AV_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-AV_agent_bundle.json) | supersedes AV-003 |
| `VIGIA-REAL-SRL-DC-CDRIVE` | DC C: drive filesystem | 2026-07-13 | **MALICE** | 19/20 | SRL-2018 compromised enterprise network. Domain Controller BASE-DC (shieldbase.l | [VIGIA-REAL-SRL-DC-CDRIVE_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-DC-CDRIVE_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-DC-MEMORY` | DC memory (JSON rerun) | 2026-07-13 | **SUSPICION** | 33/100 | SRL-2018 compromised enterprise network. Domain Controller (172.16.4.4) memory d | [VIGIA-REAL-SRL-DC-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-DC-MEMORY_agent_bundle.json) | supersedes DC-MEM-005 |
| `VIGIA-REAL-SRL-DMZ-FTP` | DMZ FTP server | 2026-07-13 | **MALICE** | 19/20 | IIS 8.5 FTP server in DMZ (172.16.10.12). External attackers attempted malware u | [VIGIA-REAL-SRL-DMZ-FTP_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-DMZ-FTP_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-HUNT-MEMORY` | Hunt memory (JSON rerun) | 2026-07-13 | **MALICE** | 4/5 | Volatility3 memory analysis of base-hunt-memory.img. Windows 10 64-bit. No malic | [VIGIA-REAL-SRL-HUNT-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-HUNT-MEMORY_agent_bundle.json) | supersedes HUNT-005 |
| `VIGIA-REAL-SRL-MAIL-MEMORY` | Mail memory (JSON rerun) | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis of base-mail-memory.img. Windows Exchange Server. LO | [VIGIA-REAL-SRL-MAIL-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-MAIL-MEMORY_agent_bundle.json) | supersedes MAIL-002 |
| `VIGIA-REAL-SRL-RD01-MEMORY` | RD01 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis. 12 LOTL processes + code injection in 12 processes. | [VIGIA-REAL-SRL-RD01-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-RD01-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-RD03-MEMORY` | RD03 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis. 1 LOTL process + code injection in 7 processes. Lig | [VIGIA-REAL-SRL-RD03-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-RD03-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-RD04-MEMORY` | RD04 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis. 30 LOTL processes + code injection in 33 processes. | [VIGIA-REAL-SRL-RD04-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-RD04-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-RD05-MEMORY` | RD05 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis of base-rd-05-memory.img. Windows 10 64-bit. Severe | [VIGIA-REAL-SRL-RD05-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-RD05-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-RD06-MEMORY` | RD06 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis. 0 LOTL processes + code injection in 4 processes. M | [VIGIA-REAL-SRL-RD06-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-RD06-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-SRL-WKSTN04-MEMORY` | WKSTN04 memory | 2026-07-13 | **MALICE** | 19/20 | Volatility3 memory analysis. 2 LOTL + code injection in 24 processes. The only c | [VIGIA-REAL-SRL-WKSTN04-MEMORY_agent_bundle.json](results/agent_batch/VIGIA-REAL-SRL-WKSTN04-MEMORY_agent_bundle.json) |  |
| `VIGIA-REAL-NFURY` | NFury suspect workstation (SRL-2018) | 2026-07-13 | **SUSPICION** | 47/100 | Nick Fury (nfury), Director-level executive at Stark Research Labs (DC=shieldbas | [VIGIA-REAL-NFURY_agent_bundle.json](results/agent_batch/VIGIA-REAL-NFURY_agent_bundle.json) |  |
| `VIGIA-REAL-NROMANOFF` | NRomanoff suspect (SRL-2018) | 2026-07-13 | **MALICE** | 21/25 | Natasha Romanoff (nromanoff), Executive at Stark Research Labs (OU=Executives, D | [VIGIA-REAL-NROMANOFF_agent_bundle.json](results/agent_batch/VIGIA-REAL-NROMANOFF_agent_bundle.json) |  |
| `VIGIA-REAL-VANKO` | Anthony Vanko, Stark Enterprises (FOR500) | 2026-07-13 | **MALICE** | 9/10 | FOR500 case. Anthony Vanko, lead biochemical engineer at Stark Enterprises DC R& | [VIGIA-REAL-VANKO_agent_bundle.json](results/agent_batch/VIGIA-REAL-VANKO_agent_bundle.json) | also counts as the original Vanko source |

## MUS2019 / Narcos — Drug Cartel Investigation (13 dumps)

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `NARCOS-CCLEANER-MEMORY` | CCleaner memory dump | 2026-06-27 | **SUSPICION** | 0 | Volatility3 memory analysis: 0 signals from narcos_ccleaner_mem.raw. Average int | [NARCOS-CCLEANER-MEMORY_bundle.json](results/srl2018/NARCOS-CCLEANER-MEMORY_bundle.json) |  |
| `NARCOS-JANE-Day2` | Jane suspect — day 2 memory | 2026-06-27 | **SUSPICION** | 0 | Volatility3 memory analysis: 0 signals from DESKTOP-QS7L4O9-20190130-015056.dmp. | [NARCOS-JANE-Day2_bundle.json](results/srl2018/NARCOS-JANE-Day2_bundle.json) |  |
| `NARCOS-JANE-Day3` | Jane suspect — day 3 memory | 2026-06-27 | **SUSPICION** | 0 | Volatility3 memory analysis: 0 signals from JELAPTOP-20190131-012114.dmp. Averag | [NARCOS-JANE-Day3_bundle.json](results/srl2018/NARCOS-JANE-Day3_bundle.json) |  |
| `NARCOS-JANE-Day4` | Jane suspect — day 4 memory | 2026-06-27 | **SUSPICION** | 0 | Volatility3 memory analysis: 0 signals from JELAPTOP-20190201-020917.dmp. Averag | [NARCOS-JANE-Day4_bundle.json](results/srl2018/NARCOS-JANE-Day4_bundle.json) |  |
| `NARCOS-JOHN-ALT-DAY1` | John alt device — day 1 | 2026-06-27 | **MALICE** | 43/100 | Volatility3 memory analysis: 4 signals from John Day 1-20190129-041845.dmp. Aver | [NARCOS-JOHN-ALT-DAY1_bundle.json](results/srl2018/NARCOS-JOHN-ALT-DAY1_bundle.json) |  |
| `NARCOS-JOHN-ALT-DAY2` | John alt device — day 2 | 2026-06-27 | **MALICE** | 4/25 | Volatility3 memory analysis: 3 signals from JOHNFLAPTOP-20190130-014821.dmp. Ave | [NARCOS-JOHN-ALT-DAY2_bundle.json](results/srl2018/NARCOS-JOHN-ALT-DAY2_bundle.json) |  |
| `NARCOS-JOHN-PRIMARY-Day1` | John primary device — day 1 | 2026-06-27 | **MALICE** | 4/25 | Volatility3 memory analysis: 3 signals from DESKTOP-EN8JNOM-20190129-041409.dmp. | [NARCOS-JOHN-PRIMARY-Day1_bundle.json](results/srl2018/NARCOS-JOHN-PRIMARY-Day1_bundle.json) |  |
| `NARCOS-JOHN-PRIMARY-Day2` | John primary device — day 2 | 2026-06-27 | **MALICE** | 43/100 | Volatility3 memory analysis: 4 signals from JOHNFLAPTOP1-20190130-020349.dmp. Av | [NARCOS-JOHN-PRIMARY-Day2_bundle.json](results/srl2018/NARCOS-JOHN-PRIMARY-Day2_bundle.json) |  |
| `NARCOS-JOHN-PRIMARY-Day3` | John primary device — day 3 | 2026-06-27 | **MALICE** | 4/25 | Volatility3 memory analysis: 3 signals from JOHNFLAPTOP1-20190131-022415.dmp. Av | [NARCOS-JOHN-PRIMARY-Day3_bundle.json](results/srl2018/NARCOS-JOHN-PRIMARY-Day3_bundle.json) |  |
| `NARCOS-JOHN-PRIMARY-Day4` | John primary device — day 4 | 2026-06-27 | **MALICE** | 4/25 | Volatility3 memory analysis: 3 signals from JOHNFLAPTOP1-20190201-020401.dmp. Av | [NARCOS-JOHN-PRIMARY-Day4_bundle.json](results/srl2018/NARCOS-JOHN-PRIMARY-Day4_bundle.json) |  |
| `NARCOS-STEVE-Day1` | Steve suspect — day 1 | 2026-06-27 | **ABSTAIN** | 0/1 | Image DESKTOP-FGEUJJC-20190129-043144.dmp rejected by Volatility3: not a valid W | [NARCOS-STEVE-Day1_bundle.json](results/srl2018/NARCOS-STEVE-Day1_bundle.json) | FORMAT_NOT_SUPPORTED: memory profile mismatch for this dump |
| `NARCOS-STEVE-Day2` | Steve suspect — day 2 | 2026-06-27 | **ABSTAIN** | 0/1 | Image SK-DESKTOP-20190130-002556.dmp rejected by Volatility3: not a valid Window | [NARCOS-STEVE-Day2_bundle.json](results/srl2018/NARCOS-STEVE-Day2_bundle.json) | FORMAT_NOT_SUPPORTED: memory profile mismatch |
| `NARCOS-STEVE-Day4` | Steve suspect — day 4 | 2026-06-27 | **MALICE** | 9/25 | Volatility3 memory analysis: 2 signals from SK-DESKTOP-20190201-030035.dmp. Aver | [NARCOS-STEVE-Day4_bundle.json](results/srl2018/NARCOS-STEVE-Day4_bundle.json) |  |

## M57-Patents — Insider IP Theft (3 images)

Source: M57-Patents public dataset (NIST/Garfinkel).
Original srl2018 runs returned PIPELINE_ERROR; JSON-converted reruns below are canonical.

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `M57-JO-2009-12-07` | Jo laptop Dec 7 (original run) | 2026-06-27 | **ABSTAIN** | N/A | [ERROR] FIX P2: defusedxml es obligatorio para protección contra XXE/Billion Lau | [M57-JO-2009-12-07_bundle.json](results/srl2018/M57-JO-2009-12-07_bundle.json) | PIPELINE_ERROR; see VIGIA-REAL-M57-JO-Dec07 |
| `M57-PAT-2009-12-07` | Pat laptop Dec 7 (original run) | 2026-06-27 | **ABSTAIN** | N/A | [ERROR] FIX P2: defusedxml es obligatorio para protección contra XXE/Billion Lau | [M57-PAT-2009-12-07_bundle.json](results/srl2018/M57-PAT-2009-12-07_bundle.json) | PIPELINE_ERROR; see VIGIA-REAL-M57-PAT-Dec07 |
| `M57-PAT-2009-12-11` | Pat laptop Dec 11 (original) | 2026-06-27 | **ABSTAIN** | N/A | [ERROR] FIX P2: defusedxml es obligatorio para protección contra XXE/Billion Lau | [M57-PAT-2009-12-11_bundle.json](results/srl2018/M57-PAT-2009-12-11_bundle.json) | PIPELINE_ERROR; see VIGIA-REAL-M57-PAT-Dec11 |
| `VIGIA-REAL-M57-JO-Dec07` | M57 Jo Dec 7 (JSON rerun) | 2026-07-13 | **SUSPICION** | 9/25 | M57-Patents scenario. Jo (CEO, expected benign). Dec-07: python.exe spawned from | [VIGIA-REAL-M57-JO-Dec07_agent_bundle.json](results/agent_batch/VIGIA-REAL-M57-JO-Dec07_agent_bundle.json) | canonical; supersedes PIPELINE_ERROR |
| `VIGIA-REAL-M57-PAT-Dec07` | M57 Pat Dec 7 (JSON rerun) | 2026-07-13 | **SUSPICION** | 37/100 | M57-Patents scenario. Pat (insider threat suspect). Dec-07 baseline: AVG antivir | [VIGIA-REAL-M57-PAT-Dec07_agent_bundle.json](results/agent_batch/VIGIA-REAL-M57-PAT-Dec07_agent_bundle.json) | canonical; supersedes PIPELINE_ERROR |
| `VIGIA-REAL-M57-PAT-Dec11` | M57 Pat Dec 11 (JSON rerun) | 2026-07-13 | **MALICE** | 81/100 | M57-Patents scenario. Pat (insider threat). Dec-11: msimn.exe (Outlook Express) | [VIGIA-REAL-M57-PAT-Dec11_agent_bundle.json](results/agent_batch/VIGIA-REAL-M57-PAT-Dec11_agent_bundle.json) | canonical; supersedes PIPELINE_ERROR |
| `VIGIA-NITROBA-M57-001` | Digital Corpora Nitroba harassment case (M57-derived) | 2026-07-13 | **SUSPICION** | 63/100 | Network packet capture (nitroba.pcap, 56180821 bytes, SHA-256: 2b77a9eaefc1d6af1 | [VIGIA-NITROBA-M57-001_agent_bundle.json](results/agent_batch/VIGIA-NITROBA-M57-001_agent_bundle.json) |  |

## NPS Corpora — NIST/CFReDS Educational Datasets

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `NPS-2010-EMAILS` | NPS 2010 email corpus (FAT16 E01) | 2026-07-13 | **NOISE** | 99/100 | NPS-2010-emails educational forensic corpus. FAT16 E01 disk image containing 26 | [NPS-2010-EMAILS_agent_bundle.json](results/agent_batch/NPS-2010-EMAILS_agent_bundle.json) |  |
| `NPS-2009-DOMEXUSERS` | NPS 2009 DomEx users XML | 2026-07-13 | **SUSPICION** | 29/100 | Windows XP NTFS forensic corpus published by the Naval Postgraduate School (2009 | [NPS-2009-DOMEXUSERS_agent_bundle.json](results/agent_batch/NPS-2009-DOMEXUSERS_agent_bundle.json) | Expected NOISE; got SUSPICION — documented divergence (see BUGS_PENDIENTES.md) |
| `VIGIA-REAL-NPS-2010-EMAILS` | NPS 2010 emails (JSON rerun) | 2026-07-13 | **NOISE** | 99/100 | Digital Corpora NPS-2010-emails corpus. A FAT32 disk image (nps_emails_fs) conta | [VIGIA-REAL-NPS-2010-EMAILS_agent_bundle.json](results/agent_batch/VIGIA-REAL-NPS-2010-EMAILS_agent_bundle.json) |  |
| `VIGIA-REAL-NPS-2014-USB-NONDETERMINISTIC` | NPS 2014 USB nondeterministic acquisition | 2026-07-13 | **NOISE** | 97/100 | NPS-2014 USB non-deterministic corpus. Transcend JetFlash V10 1GB (D33193). Four | [VIGIA-REAL-NPS-2014-USB-NONDETERMINISTIC_agent_bundle.json](results/agent_batch/VIGIA-REAL-NPS-2014-USB-NONDETERMINISTIC_agent_bundle.json) | documented NOISE: acquisition nondeterminism documented as L-020 |

## Magnet Forensics CTF — 2014 / 2020 / 2021 / 2022

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `MAGNET-2020-CTF-WINDOWS` | 2020 CTF Windows memory (original run) | 2026-06-28 | **SUSPICION** | 3/50 | Volatility3 memory analysis: 2 signals from memdump-001.mem. Average intentional | [MAGNET-2020-CTF-WINDOWS_bundle.json](results/srl2018/MAGNET-2020-CTF-WINDOWS_bundle.json) |  |
| `VIGIA-MAGNET-2020-WINDOWS` | 2020 CTF Windows (JSON rerun) | 2026-07-13 | **SUSPICION** | 33/50 | Windows 7 x64 VMware VM (ComputerName: WIN-9H6J4FBP8F7, Volume: TestOS, IP: 192. | [VIGIA-MAGNET-2020-WINDOWS_agent_bundle.json](results/agent_batch/VIGIA-MAGNET-2020-WINDOWS_agent_bundle.json) |  |
| `VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT` | 2020 CTF — pagefile absent scenario | 2026-07-13 | **SUSPICION** | 19/20 | Windows 10 64-bit memory dump. windows.pslist returns 0 processes while windows. | [VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT_agent_bundle.json](results/agent_batch/VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT_agent_bundle.json) |  |
| `VIGIA-MAGNET-2014-TIMELINE` | 2014 multidevice timeline artifacts | 2026-07-13 | **SUSPICION** | 2/5 | Document named Hidden.docx with content 'Super secret document / Trade secrets w | [VIGIA-MAGNET-2014-TIMELINE_agent_bundle.json](results/agent_batch/VIGIA-MAGNET-2014-TIMELINE_agent_bundle.json) |  |
| `VIGIA-REAL-MAGNET-2021-IOS-ELI` | 2021 iOS — Eli iPhone | 2026-07-13 | **SUSPICION** | 57/100 | iPhone 8 forensic extraction. Systematic communication evasion pattern: Wickr wi | [VIGIA-REAL-MAGNET-2021-IOS-ELI_agent_bundle.json](results/agent_batch/VIGIA-REAL-MAGNET-2021-IOS-ELI_agent_bundle.json) |  |
| `VIGIA-MAGNET-2022-WINDOWS` | 2022 CTF Windows artifacts | 2026-07-13 | **MALICE** | 67/100 | Windows workstation compromised via ZeroTier encrypted overlay (C2). Attacker ob | [VIGIA-MAGNET-2022-WINDOWS_agent_bundle.json](results/agent_batch/VIGIA-MAGNET-2022-WINDOWS_agent_bundle.json) |  |
| `VIGIA-MAGNET-2022-iOS-JESS` | 2022 iOS Jess (JSON subset only) | 2026-07-13 | **SUSPICION** | 7/25 | iPhone 8 (iOS 15.0.2) belonging to Patrick Bentley (pbentley0107@gmail.com, +1-9 | [VIGIA-MAGNET-2022-iOS-JESS_agent_bundle.json](results/agent_batch/VIGIA-MAGNET-2022-iOS-JESS_agent_bundle.json) | Full 8.2 GB E01 PENDING extraction — see raw re-run table |
| `VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN` | 2022 iOS Jess keychain subset | 2026-07-13 | **SUSPICION** | 57/100 | Supplement to prior INTENT verdict (VIGIA-MAGNET-2022-IOS-JESS). Three new artif | [VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN_agent_bundle.json](results/agent_batch/VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN_agent_bundle.json) |  |
| `VIGIA-REAL-MAGNET-2022-ANDROID` | 2022 Android image | 2026-07-13 | **SUSPICION** | 41/100 | Android data partition image. Rafael Shell (rafaelshell24@gmail.com), Google Pix | [VIGIA-REAL-MAGNET-2022-ANDROID_agent_bundle.json](results/agent_batch/VIGIA-REAL-MAGNET-2022-ANDROID_agent_bundle.json) |  |
| `VIGIA-CTF-2021-iOS-Eli-iPhone8` | CFReDS iOS CTF 2021 — Eli iPhone 8 | 2026-07-13 | **MALICE** | 83/100 | GrayKey extraction of iPhone 8 (iOS 14.4) belonging to Eli Flatt. Triple encrypt | [VIGIA-CTF-2021-iOS-Eli-iPhone8_agent_bundle.json](results/agent_batch/VIGIA-CTF-2021-iOS-Eli-iPhone8_agent_bundle.json) |  |

## Other Public Forensic Corpora

| Case ID | Source / Description | Run Date | Verdict | Confidence | Key Finding | Bundle | Notes |
|---------|---------------------|----------|---------|------------|-------------|--------|-------|
| `VIGIA-TUCK-2019` | Digital Corpora Tuck 2019 macOS APFS laptop | 2026-07-13 | **MALICE** | 69/100 | macOS APFS laptop of suspect tuckgorge (Digital Corpora 2019, examiner Simson Ga | [VIGIA-TUCK-2019_agent_bundle.json](results/agent_batch/VIGIA-TUCK-2019_agent_bundle.json) |  |
| `OWL-NEXUS5-CASE` | Owl Investigation HD1/Nexus 5 case | 2026-07-13 | **NOISE** | 93/100 | Forensic analysis of LGE Nexus 5 full image belonging to Sarah McAvoy, suspected | [OWL-NEXUS5-CASE_agent_bundle.json](results/agent_batch/OWL-NEXUS5-CASE_agent_bundle.json) | Got NOISE; expected SUSPICION — documented L-011 (low-signal limit) |
| `VIGIA-HMG-99999-11` | HMG Infosec Standard No.5 — case 99999-11 | 2026-07-13 | **MALICE** | 9/10 | Victor Bushell laptop (Windows 7) acquired 2011-10-23 by examiner Craig Wilson ( | [VIGIA-HMG-99999-11_agent_bundle.json](results/agent_batch/VIGIA-HMG-99999-11_agent_bundle.json) |  |
| `VIGIA-NOKIA6230-001` | Nokia 6230 mobile phone forensics | 2026-07-13 | **NOISE** | 93/100 | Forensic image of Nokia 6230 internal flash memory (file Rh-12_352953003422072-b | [VIGIA-NOKIA6230-001_agent_bundle.json](results/agent_batch/VIGIA-NOKIA6230-001_agent_bundle.json) |  |
| `VIGIA-REAL-ROCBA` | ROCBA fraud investigation | 2026-07-13 | **MALICE** | 71/100 | User 'fredr', Windows 10 x64 build 19041 (20H2), hostname unknown. IP 192.168.1. | [VIGIA-REAL-ROCBA_agent_bundle.json](results/agent_batch/VIGIA-REAL-ROCBA_agent_bundle.json) |  |
| `VIGIA-REAL-TDUNGAN` | Digital Corpora XP Tdungan case | 2026-07-13 | **MALICE** | 4/5 | Timothy Dungan (tdungan), employee of Stark Research Labs, domain SHIELDBASE, au | [VIGIA-REAL-TDUNGAN_agent_bundle.json](results/agent_batch/VIGIA-REAL-TDUNGAN_agent_bundle.json) |  |
| `VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL` | Magnet 2022 Linux Rafael | 2026-07-13 | **SUSPICION** | 61/100 | Ubuntu 21.10 disk image. User rafael has Log4Shell (CVE-2021-44228) attack tools | [VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL_agent_bundle.json](results/agent_batch/VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL_agent_bundle.json) |  |
| `VIGIA-GOOGLE-TAKEOUT-2020` | Google Takeout 2020 export forensics | 2026-07-13 | **MALICE** | 77/100 | Google Takeout export from Chester Russell (king.chester.802@gmail.com), Champla | [VIGIA-GOOGLE-TAKEOUT-2020_agent_bundle.json](results/agent_batch/VIGIA-GOOGLE-TAKEOUT-2020_agent_bundle.json) |  |
| `VIGIA-DRIVE-DOWNLOAD-2026` | Google Drive download 2026 | 2026-07-13 | **NOISE** | 99/100 | ZIP export from Google Drive (drive-download-20260123T060931Z-3-001.zip, SHA-256 | [VIGIA-DRIVE-DOWNLOAD-2026_agent_bundle.json](results/agent_batch/VIGIA-DRIVE-DOWNLOAD-2026_agent_bundle.json) |  |

---

## Local Raw Evidence Re-runs — Planned 2026-07-14

Evidence directories in `evidence/` queued for Mode 1 re-run (`vigia_agent.py`
directly on the raw artifacts, no JSON conversion). Validation goal: confirm
B-127 (`prior_trust` boundary `<` → `<=`) did not flip any verdict at
`confidence = 0.5` exactly.

| Evidence Directory | Planned Case ID | Status | Artifact Types | Notes |
|-------------------|-----------------|--------|---------------|-------|
| `evidence/magnet-2020-windows-artifacts/` | `MAGNET-2020-WIN-RAW-20260714` | **DONE** — SUSPICION 3/5 | evtx, registry hives | [bundle](results/agent_batch/MAGNET-2020-WIN-RAW-20260714_bundle.json) |
| `evidence/magnet-2022-windows-artifacts/` | `MAGNET-2022-WIN-RAW-20260714` | **DONE** — SUSPICION 3/5 | evtx, hives | [bundle](results/agent_batch/MAGNET-2022-WIN-RAW-20260714_bundle.json) |
| `evidence/magnet-2014-multidevice/` | `MAGNET-2014-RAW-20260714` | **DONE** — ABSTAIN (UNDETERMINED: evidence gap) | prefetch, .docx | [bundle](results/agent_batch/MAGNET-2014-RAW-20260714_bundle.json) |
| `evidence/owl-2019-hd1-windows/` | `OWL-HD1-RAW-20260714` | **DONE** — ABSTAIN (ABSTAIN_V2: CCS tie 1/2) | evtx, NTUSER.DAT, prefetch, SAM/SYSTEM | [bundle](results/agent_batch/OWL-HD1-RAW-20260714_bundle.json) |
| `evidence/owl-2019-nexus5-quick/` | `OWL-NEXUS5-RAW-20260714` | **DONE** — ABSTAIN (MOBILE_EVIDENCE_ANALYZED: 1 signal) | Android artifacts | [bundle](results/agent_batch/OWL-NEXUS5-RAW-20260714_bundle.json) |
| `evidence/flare-on/` | `FLAREON-RAW-20260714` | **DONE** — ABSTAIN (UNDETERMINED) | CTF malware artifacts | [bundle](results/agent_batch/FLAREON-RAW-20260714_bundle.json) |
| `evidence/image-2011-10-19/` | `IMAGE-2011-RAW-20260714` | **DONE** — ABSTAIN (PIPELINE_ERROR: E01 requires SIFT) | 2011-10-19-Sample.E01 disk image | [bundle](results/agent_batch/IMAGE-2011-RAW-20260714_bundle.json) |
| `evidence/dfworkbook/` | `DFWORKBOOK-RAW-20260714` | **DONE** — ABSTAIN (PIPELINE_ERROR: E01 requires SIFT) | 2011-10-19-Sample.E01 + eventlogs | [bundle](results/agent_batch/DFWORKBOOK-RAW-20260714_bundle.json) |
| `evidence/takeout-2020/` | `TAKEOUT-RAW-20260714` | **DONE** — SUSPICION 21/25 | Google Takeout export | [bundle](results/agent_batch/TAKEOUT-RAW-20260714_bundle.json) |
| `evidence/magnet-2022-ios-jess/` | `MAGNET-2022-IOS-JESS-RAW` | **PENDING** | iOS E01 (8.2 GB) | Requires zip extraction first; does not block other re-runs |

**B-127 validation result:** None of the completed re-runs produced `confidence = 0.5` exactly.
The boundary fix (`prior_trust < 0.5` → `<= 0.5`) had no verdict-flipping effect on any of these local evidence cases.

---

## Verdict Scale Reference

| Verdict | Meaning |
|---------|---------|
| **MALICE** | Active concealment of intent; two independent corroborating sources required |
| **SUSPICION** | Structural anomaly; single-source; benign hypothesis not fully refuted |
| **NOISE** | Fully explained by misconfiguration, software error, or normal behavior |
| **ABSTAIN** | Pipeline error, unsupported format, or insufficient data |
| `PIPELINE_ERROR` | Volatility3/SIFT plugin unavailable for this memory profile |
| `FORMAT_NOT_SUPPORTED` | Memory dump format not parseable by installed plugin set |
| `supersedes` | Later run produced more reliable result; earlier kept for record |

---

*Generated: 2026-07-14.
See `README.md` — Domain C section — for the doctrinal basis of this catalog.*