#!/usr/bin/env python3
"""
translate_canonical_cases.py
Translates Spanish fields in VIGIA-CAN-*.json to English.
Fields translated: name, description, notes, peirce_chain (firstness/secondness/thirdness),
                   artifacts[].description, caie_fractures[].description
Fields NOT touched: case_id, expected_verdict, evidence_type, source_tool, metadata keys,
                    timestamps, IPs, hash values, fracture types
"""
import json, os, sys

TRANSLATIONS = {
"VIGIA-CAN-001": {
    "name": "The Pawn Sacrifice",
    "description": "Senior analyst self-reports an open SSH session to create an extreme-honesty alibi. While the team audits their account with benevolence, a cron job installed 5 minutes before the report exfiltrates data under a system service identity.",
    "notes": "Carnegie: 'Admit your mistakes quickly and emphatically'. Strategic over-incrimination.",
    "peirce_chain": {
        "firstness": "Self-reporting email with a tone of urgency and extreme remorse.",
        "secondness": "The malicious cron job exists 5 minutes before the email. The chronology breaks the accidental-error narrative.",
        "thirdness": "Habit of creating high emotional-cost distractions to cover simultaneous technical operations. The confession IS the attack."
    },
    "artifacts": [
        "Urgent email from senior analyst self-reporting an SSH session left open for 4 hours on a public server. Requests access revocation.",
        "Scheduled task (cron job) created 5 minutes BEFORE the confession email. Creation timestamp precedes the public report.",
        "svchost.exe process with persistent connection to external IP under a legitimate system service identity.",
        "Exfiltration traffic to external IP on port 443 under a system process. 2.3GB transferred during the benign audit window."
    ],
    "caie_fractures": [
        "The public report saturates the auditor's trust bias while the malicious process operates under the cover of the benign investigation.",
        "The cron job exists 5 minutes before the confession. Golden rule: forces structural MALICE."
    ]
},
"VIGIA-CAN-002": {
    "name": "The False Layman Lure",
    "description": "An 'admin' user submits a support ticket simulating digital incompetence. The attached screenshot shows a dirty pipe exploit half-executed. Zero probability of reaching that state accidentally.",
    "notes": "Forensic theater: the law of chance does not generate kernel exploits from 'clicking around'.",
    "peirce_chain": {
        "firstness": "Non-technical user ticket with a Linux terminal screenshot.",
        "secondness": "A 'non-technical' user cannot accidentally reach a kernel exploit execution state.",
        "thirdness": "Habit of using simulated incompetence to induce privileged action from the support technician."
    },
    "artifacts": [
        "Ticket: 'I don't know what I touched, black screen with green text, can't open Excel'.",
        "Attached screenshot: Linux terminal with CVE-2022-0847 (dirty pipe) half-executed. Progress bar visible at 45%.",
        "Bash history in memory: wget exploit.sh && chmod +x && ./exploit.sh.",
        "DNS resolution to a domain registered 2 days before the support ticket."
    ],
    "caie_fractures": [
        "Zero probability that a non-technical user accidentally reaches a kernel exploit execution state."
    ]
},
"VIGIA-CAN-003": {
    "name": "The Altered Mise en Place",
    "description": "deploy.sh script modified with commit 'cleaning up redundant logs'. A single line redirects stderr to /dev/null, silencing authentication module errors and causing fail-open.",
    "notes": "Lethal minimalism: a single line blinds a critical control.",
    "peirce_chain": {
        "firstness": "Commit labeled 'cleanup' with a minimal change to a deployment script.",
        "secondness": "stderr redirection destroys authentication failure visibility; auth enters permissive mode.",
        "thirdness": "Habit of using 'cleanup' as a sign to conceal deliberate degradation of security controls."
    },
    "artifacts": [
        "Commit: 'Cleaning up redundant logs for readability'. Single-line change in deploy.sh.",
        "Diff: added line 'auth_check() 2>/dev/null || true'. Silences all authentication module errors.",
        "47 authentication failures silenced in the post-deploy window. Zero Event 4625 generated.",
        "EPROCESS structure of the deploy service shows a handle to /dev/null replacing stderr at runtime."
    ],
    "caie_fractures": [
        "'Cleanup' is a sign to conceal critical security control failure. Benign-looking commit hides deliberate degradation."
    ]
},
"VIGIA-CAN-004": {
    "name": "The Double Layout Slip",
    "description": "Bash history sequence: 'кщще' (root on Russian QWERTY layout), immediate deletion, then 'sudo'. The 800ms correction reveals an OPSEC-aware operator betrayed by muscle memory.",
    "notes": "Peirce physical index: key order betrays the mind. High linguistic attribution.",
    "peirce_chain": {
        "firstness": "Meaningless string 'кщще' in bash history.",
        "secondness": "кщще is 'root' on a Russian keyboard. The 800ms correction indicates an OPSEC-aware operator betrayed by muscle memory.",
        "thirdness": "Habit of a native Russian operator using 'root' directly. The slip destroys the identity alibi."
    },
    "artifacts": [
        "Keystroke sequence: кщще [backspace×4] sudo [enter]. The string кщще is 'root' typed with Russian ЙЦУКЕН layout active.",
        "Phonetic analysis confirms кщще is the exact result of typing 'root' with Russian layout. Regional attribution: RU/CIS.",
        "Root session authenticated 27 seconds after the keyboard slip. The attacker achieved privilege escalation.",
        "Bash history in memory: 'sudo systemctl restart sshd' executed 120ms after the deleted string."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-005": {
    "name": "The Inverted Stockholm Syndrome",
    "description": "External security contractor 'helps' during an incident: blocks a Ukrainian IP and deletes access logs 'to avoid saturating the SIEM'. The deletion occurs 5 minutes before the help message.",
    "notes": "Inverted Carnegie: the 'help' IS the method to destroy evidence.",
    "peirce_chain": {
        "firstness": "Contractor proactively offers help during an active incident.",
        "secondness": "Cleanup process started 5 minutes before the Slack message. The flagged IP is a Tor node with no real evidence.",
        "thirdness": "Habit of using incident urgency as cover to destroy forensic traces of the real attack vector."
    },
    "artifacts": [
        "Slack message: 'Guys, found a Ukrainian IP attacking us. Already blocked it and deleting logs from that region to avoid saturating the SIEM'.",
        "log_cleaner.exe process executed from contractor's machine 5 minutes BEFORE the Slack message. Not an authorized stack tool.",
        "2.4GB of access logs deleted with shred -n 7. Forensic-destructive method, not operational.",
        "Ukrainian IP flagged as attacker turns out to be a Tor exit node. No evidence of real attack from that IP."
    ],
    "caie_fractures": [
        "Deleting logs is NEVER part of an incident response solution. It is destruction of forensic evidence.",
        "Ukrainian IP flagged without technical corroboration. The deleted logs were the only evidence of the real origin."
    ]
},
"VIGIA-CAN-006": {
    "name": "The Intruder's Semantic Calque",
    "description": "Internal ticket in English uses 'state of the country' as a calque of 'стране' (area/side in Russian) in an electric utility company. The error reveals a native-language thought structure.",
    "notes": "Detection of underlying linguistic calque: the attacker operates under a mask of fluency in a non-native language.",
    "peirce_chain": {
        "firstness": "Ticket in fluent English but with a semantically misplaced phrase for a technical-geographic context.",
        "secondness": "'State of the country' makes no sense for an electric utility server. Matches a literal translation from Russian.",
        "thirdness": "Habit of direct mental translation that reveals native-language thought structure under operational stress."
    },
    "artifacts": [
        "Ticket: 'I need to check the state of the country'. Context: electric utility server.",
        "Semantic calque: 'state of the country' directly translates 'стране', which in informal Russian means 'area/sector'. Literal translation error.",
        "RDP session from IP geolocated in Moscow, timezone UTC+3, user 'field_tech'.",
        "Command executed: 'Get-StateOfCountry -ServerId NY-42'. Cmdlet does not exist in the official repository; loaded from an unknown module."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-007": {
    "name": "The Footprint of Perfection",
    "description": "45-minute remote admin session with 847 commands. Keystroke variance of 0.05s in 90% of samples. Temporal entropy: 0.12 bits. Impossible for a human operator.",
    "notes": "Mathematically irrefutable: humans do not think with a stopwatch.",
    "peirce_chain": {
        "firstness": "45-minute session with perfectly uniform inter-command timings.",
        "secondness": "0.05s variance is a machine's law. 0.12 bits entropy is incompatible with real human analysis.",
        "thirdness": "Habit of automation that attempts to simulate human rhythm but fails at cognitive entropy."
    },
    "artifacts": [
        "45-minute RDP session: 847 commands, keystroke variance = 0.050s in 90% of samples. Human baseline: >180ms.",
        "Session temporal entropy: 0.12 bits. Expected for a human: >2.5 bits for a real analysis session.",
        "mstsc.exe process with no evidence of GUI interaction. Zero bitmap changes, zero clipboard operations during 'active' session.",
        "Session origin: VPS IP in Frankfurt, cheap hosting ASN. Inconsistent with legitimate admin's work hours (03:15 local NY time)."
    ],
    "caie_fractures": [
        "Execution pattern incompatible with task cognitive load. Automation detected."
    ]
},
"VIGIA-CAN-008": {
    "name": "The Tool Anachronism",
    "description": "PsExec v1.94 (2014) detected on a Windows 2025 server. A noisy tool that generates 12 EDR alerts. Memory analysis reveals a kernel rootkit with SSDT hooks installed 2 minutes earlier. The psexec is the decoy.",
    "notes": "The noisy tool is the decoy. The silent one is the real attack.",
    "peirce_chain": {
        "firstness": "PsExec v1.94 generates obvious EDR alerts on Windows 2025.",
        "secondness": "Noisy tool contradicts the presence of a sophisticated kernel rootkit installed 2 minutes earlier.",
        "thirdness": "Habit of using low-sophistication decoys so the analyst closes the ticket as a script-kiddie case and does not dig deeper."
    },
    "artifacts": [
        "psexec.exe binary version 1.94 (known hash, signed 2014) detected in C:\\Temp. Noisy tool detectable by any modern EDR.",
        "EDR generated 12 'Obsolete remote administration tool' alerts. Marked as FP by Tier-1 analyst.",
        "Unsigned kernel driver loaded 2 minutes BEFORE psexec. 12 SSDT hooks. Requires advanced C++ and Ring-0 knowledge.",
        "Encrypted C2 traffic on port 8443 initiated 1 minute before the psexec noise. Firewall reports 0 bytes for this port."
    ],
    "caie_fractures": [
        "EDR classifies psexec as noise (low severity) while kernel reveals APT-level persistence.",
        "Firewall reports 0 bytes on port 8443 but kernel rootkit exfiltrates 512KB. The driver hooks network syscalls."
    ]
},
"VIGIA-CAN-009": {
    "name": "The Noble Motive Dissonance",
    "description": "Slack message: 'I saw your password on a post-it in the camera, I deleted it to protect you. Here's a link to reset it'. No post-it in any frame of the recording. The link is a phishing domain registered 6 hours earlier.",
    "notes": "Carnegie: 'Make the other person happy to do what you suggest'.",
    "peirce_chain": {
        "firstness": "False solidarity message with a 'help' link.",
        "secondness": "No post-it visible on camera. Link is a phishing domain registered 6 hours before. Sender has an active admin panel.",
        "thirdness": "Habit of using social vulnerability and reciprocity to induce risky action under the guise of protection."
    },
    "artifacts": [
        "Slack DM: 'Hey, I saw you left your password on a post-it in the meeting room camera. I wrote it down and deleted it from the capture... [link]'.",
        "Review of meeting room camera recording: NO post-it visible in any of the 1,247 analyzed frames.",
        "Link domain registered 6 hours before the message. Bulletproof hosting, Let's Encrypt certificate.",
        "Colleague's browser process with authenticated session on the phishing admin panel."
    ],
    "caie_fractures": [
        "Noble motive (protection) is a wrapper for internal phishing. False solidarity to induce click on malicious link."
    ]
},
"VIGIA-CAN-010": {
    "name": "The Saturation Truth Effect",
    "description": "40-page PDF report with irrelevant charts hides a 'minor permission adjustment' on page 39 that grants Everyone:FullControl over HKLM\\SAM. Cognitive DoS via documentary volume.",
    "notes": "Semantic flooding: information overload as a cover-up weapon.",
    "peirce_chain": {
        "firstness": "Exhaustive 40-page report with multiple metrics.",
        "secondness": "Massive volume hides a critical permission change. PDF generated by a headless script, not by a human.",
        "thirdness": "Habit of using information fatigue to nullify the recipient's critical capacity."
    },
    "artifacts": [
        "PDF 'Detailed Suspicious Process Report': 40 pages. CPU charts, disk temperatures, technical bios. Relevant information: page 39.",
        "Page 39: 'minor unimportant permission adjustment'. Actual action: Everyone:FullControl on HKLM\\SAM\\Domains.",
        "PDF metadata: created by headless script (soffice.bin), last modified 3 minutes before sending. Not manually authored.",
        "Event 4663: ACL change on HKLM\\SAM. Actor: admin_jdoe. Timestamp matches exactly with report submission."
    ],
    "caie_fractures": [
        "Data volume seeks to nullify critical capacity through cognitive fatigue. Grice violation: Quantity maxim."
    ]
},
"VIGIA-CAN-011": {
    "name": "The Style Deepfake",
    "description": "15 commits imitate the Chief Architect's style (spacing, grammatical errors, TTR) with a statistical precision of 0.97, exceeding human biological variance (0.82). Uploaded via generic API key at 4AM while the architect was offline.",
    "notes": "Superhuman statistical consistency is the indicator of algorithmic fabrication.",
    "peirce_chain": {
        "firstness": "Commits with identical style to the chief architect uploaded in the early hours.",
        "secondness": "Architect offline. Generic API key. Stylometric match exceeds human biological variance.",
        "thirdness": "Habit of using AI to fabricate code that 'looks' legitimate. Perfect consistency IS the impostor's signature."
    },
    "artifacts": [
        "15 commits uploaded via generic API key 'ci-token-legacy' at 4AM. Author: arch_chief@corp.com.",
        "Chief Architect offline since 19:30 the previous day. No session between 19:30 and 4AM.",
        "Stylometric analysis: TTR similarity 0.992, grammatical errors replicated ('recieve', 'seperate'). Match exceeds human biological variance (0.82 baseline).",
        "One of the 15 commits introduces a backdoor in the authentication module. Hash mismatch with code reviewed in previous PR. Change obfuscated within 847 lines of legitimate refactoring."
    ],
    "caie_fractures": [
        "Commits claim authorship of the architect but LSASS confirms session closed 8.5 hours prior. Structural impossibility.",
        "Authentication module hash does not match the one reviewed in the PR. Requires trust-chain validation to elevate to Golden Rule."
    ]
},
"VIGIA-CAN-012": {
    "name": "The Bureaucratic Black Hole",
    "description": "Facing a data breach audit, the responsible party delivers 200 PDFs of 'historical Integrity Reports'. Creation metadata shows an exact 1.2-second interval between files. All ctimes grouped in a 4-minute window.",
    "notes": "Grice: Quantity maxim violation — provides massive information to hide a lack of real evidence.",
    "peirce_chain": {
        "firstness": "200 compliance PDFs delivered for an audit.",
        "secondness": "ctime in a 4-minute window. Exact 1.2s interval. Content generated by regex. No authoring software activity.",
        "thirdness": "Habit of fabricating massive compliance evidence just before an audit. The 'Consistency Factory' is the weapon."
    },
    "artifacts": [
        "200 PDFs with creation metadata exactly 1.2 seconds apart. Interval variance: 0.0s. Physically impossible for human management.",
        "ctime of all 200 PDFs grouped in a 4-minute window (08:56-09:00). The mtimes claim dates between January 2025 and May 2026.",
        "Random sample OCR: 47 PDFs contain identical paragraphs with only dates modified by regex. Content entropy: 0.8 bits.",
        "200 PDFs attributed to 'Internal Audit' but no user from the department has LibreOffice/Word activity in logs for that window."
    ],
    "caie_fractures": [
        "200 documents with an exact 1.2s temporal delta: unambiguous signature of mass-generation script. Golden rule."
    ]
},
"VIGIA-CAN-013": {
    "name": "The Phonetic Shadow",
    "description": "Support ticket in English: 'I'll make the revision of the server'. Command executed: grep -R (uppercase R, from translated Chinese manuals). Double calque revealing Chinese native thought structure.",
    "notes": "The attacker has fluent English, but their thought structure reveals their origin.",
    "peirce_chain": {
        "firstness": "Ticket in fluent English but using 'revision' as an action noun.",
        "secondness": "Both patterns match direct mental translation from Chinese. Consistent origin IP.",
        "thirdness": "Habit of operating under a mask of linguistic fluency with 'technical thinking' that reveals idiomatic origin."
    },
    "artifacts": [
        "Ticket: 'I'll make the revision of the server'. Use of 'revision' as an action noun (calque of 修订/审核).",
        "Semantic calque + manual syntax: 'revision' translates 修订. Uppercase flag '-R' appears in Chinese technical translations of Unix manuals.",
        "Command executed: grep -R 'password' /etc. Uppercase -R is documented in Chinese translated manuals; a native speaker would use -r.",
        "SSH session from Shanghai IP, timezone UTC+8, user 'support_temp' created 2 days prior."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-014": {
    "name": "The Panic Entropy",
    "description": "50 fake MFA alerts saturate the administrator in 8 seconds. Admin requests to disable MFA for '5 minutes'. During that window: 3 successful logins from attacker IPs. Disabling MFA does not solve a network attack — it is the goal.",
    "notes": "Social engineering through exhaustion: the requested security degradation is the ultimate objective.",
    "peirce_chain": {
        "firstness": "Admin overwhelmed by 50 alerts in 8 seconds asks to disable MFA.",
        "secondness": "Disabling MFA facilitates the ongoing attack. 3 successful attacker logins during the window.",
        "thirdness": "Habit of using sensory saturation to force security degradation. The degradation request IS the attack goal."
    },
    "artifacts": [
        "50 Telegram/Duo alerts sent to admin in an 8-second window. All with the same text: 'ALERT: Intruder detected'.",
        "Admin: 'I'm overwhelmed, disable MFA for 5 minutes so I can quickly get in and block the IPs'.",
        "MFA disabled. During the 5-minute window: 3 successful logins from attacker IPs.",
        "Concurrent brute-force attack from 3 IPs with synchronized cadence of 2.1s per IP. Does not stop during or after the MFA-disabled window."
    ],
    "caie_fractures": [
        "Sensory saturation to force security degradation. Disabling MFA does not solve a network attack — it IS the attack GOAL."
    ]
},
"VIGIA-CAN-015": {
    "name": "The False Mercy",
    "description": "Analyst: 'I saved your life, I closed your open session'. Webshell installed 10 seconds BEFORE the message. The supposedly closed session is still active in memory. 3 POST connections to the webshell from the analyst's IP.",
    "notes": "The noble motive is a barrier against suspicion. Carnegie: 'Be warm in your approval'.",
    "peirce_chain": {
        "firstness": "False solidarity message: 'I closed your session to save you'.",
        "secondness": "Webshell created 10s before the message. Session never closed. POST connections from the 'savior's' IP.",
        "thirdness": "Habit of using social reciprocity to cover persistence implantation."
    },
    "artifacts": [
        "DM: 'Hey, I saved your life. I saw your open session and closed it myself so you don't get disciplined. Don't say anything'.",
        "PHP webshell created in /var/www/html/uploads/ 10 seconds BEFORE the 'help' message.",
        "Colleague's session (dev@corp.com) still active 5 minutes after the alleged closure. No logout event.",
        "3 POST connections to webshell.php from analyst_sec IP within 2 minutes of the 'closure' message."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-016": {
    "name": "The Platform Anachronism",
    "description": "User types 'ipconfig /all' on an Ubuntu 24.04 LTS server. Fails with 'command not found'. Corrects to 'ip addr' 1.3 seconds later. Cross-platform muscle memory contamination reveals a Windows origin environment.",
    "notes": "Physical anachronism of the operator's mind: translation from native OS.",
    "peirce_chain": {
        "firstness": "Windows command 'ipconfig' on a Linux server, corrected immediately.",
        "secondness": "Muscle memory contamination error: the operator 'thinks in Windows' but operates in Linux.",
        "thirdness": "Habit of blindly translating commands from the native OS, revealing the origin environment."
    },
    "artifacts": [
        "Failed command: 'ipconfig /all' in Ubuntu 24.04 bash. Exit code 127: command not found.",
        "Correction 1.3 seconds later: 'ip addr'. Native Linux command.",
        "Keystroke sequence: 'ipconfig' space '/' TAB (failed autocomplete) Ctrl+C 'ip addr'.",
        "SSH session from Windows 11 (PuTTY/0.81) connected to Ubuntu 24.04 Linux server."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-017": {
    "name": "The Emotional Trojan",
    "description": "HR email: 'Due to the passing of a colleague, we are collecting funds. See attached PDF'. The employee does not exist in the database. SPF/DKIM fail. PDF contains JavaScript that steals browser session tokens. 12 hosts compromised.",
    "notes": "Eco: the sign of death is the ultimate semantic barrier.",
    "peirce_chain": {
        "firstness": "Condolence email with donation PDF from HR.",
        "secondness": "Employee does not exist. SPF/DKIM fail. PDF steals tokens. 12 hosts compromised.",
        "thirdness": "Habit of using social taboo (death) to nullify technical distrust protocols."
    },
    "artifacts": [
        "Email from hr@corp.com: 'Condolences - Fund for Juan Pérez's family'. SPF: fail. DKIM: fail.",
        "Attached PDF: embedded JavaScript that accesses session cookies (session_id, auth_token, csrf) and sends them to an external domain.",
        "HTTPS connection to family-support[.]org from 12 internal hosts within 30 minutes of mass PDF opening.",
        "Verification: real HR did not send the email. 'Juan Pérez' does not exist in the active personnel database."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-018": {
    "name": "The Ghost in the Machine",
    "description": "Service account performs maintenance with 847 commands at exact 300.0s intervals. Temporal entropy: 0.00 bits. The expected process does not exist in memory. 847 exfiltration connections of 50MB each exactly every 300s.",
    "notes": "Peirce: perfection is the sign of a lack of humanity. A real expert has 'noise'.",
    "peirce_chain": {
        "firstness": "Perfect maintenance log: exact intervals, zero errors.",
        "secondness": "Entropy 0.00 bits. Process not in memory. 847 perfectly periodic exfiltration connections.",
        "thirdness": "Habit of an exfiltration script disguised as maintenance. Perfection is the sign of inhumanity."
    },
    "artifacts": [
        "847 commands executed at exact 300.0-second intervals. Zero errors. Zero retries. Over 70.5 hours.",
        "Log temporal entropy: 0.00 bits. Expected for legitimate service: 1.2 bits. Interval with zero variance.",
        "Process 'maintenance_tool.exe' NOT found in memory during execution window. Log generated by external script.",
        "847 outbound connections to a cloud storage IP with encrypted 50MB payloads every exact 300s. Total exfiltrated: 41.3GB."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-019": {
    "name": "The Smoke Informant",
    "description": "User reports 'strange files in my folder'. The attached file is a malicious LNK that exploits CVE-2024-XXXX when opened by the administrator's viewer. The informant is the attack vector.",
    "notes": "Trap reporting: the security system becomes the attack vector.",
    "peirce_chain": {
        "firstness": "Legitimate-looking report from a concerned user.",
        "secondness": "The 'strange file' is an exploit that activates when opened by admin. Informant is the vector.",
        "thirdness": "Habit of role inversion: the report IS the attack. The informant acts as the trigger."
    },
    "artifacts": [
        "Ticket: 'I think I was hacked, I see strange files in my folder'. Attaches file for review.",
        "Strange file: LNK with PDF magic bytes and CVE-2024-XXXX exploit in compressed stream. Activates when opened by a privileged viewer.",
        "Admin (domain\\admin_sec) opens file from share using privileged internal viewer.",
        "Shellcode injected into admin_viewer.exe 2 seconds after opening. Reverse shell established to 185.220.101.42:4444."
    ],
    "caie_fractures": [
        "Informant is the vector. The report is the trigger to escalate privileges via security personnel."
    ]
},
"VIGIA-CAN-020": {
    "name": "The Support Mirror",
    "description": "Attacker interacts with technician by copying exact phrases from the internal KB ('I understand your frustration', 'We are working on it') with a 94% match. Requests CFO password reset without MFA or approval.",
    "notes": "Carnegie: the mirroring effect to generate an immediate false sense of trust.",
    "peirce_chain": {
        "firstness": "Collaborative user in chat with familiar phrases.",
        "secondness": "94% match with internal KB. CFO reset without controls. Response in 180ms (pre-loaded).",
        "thirdness": "Habit of using 'house language' to neutralize operator alertness through false belonging."
    },
    "artifacts": [
        "Support chat: attacker uses identical phrases to the technician 5 times. 'I understand your frustration', 'We are working on it'.",
        "NLP analysis: user replicates operator syntax with 94% match to internal KB. Response latency: 180ms (pre-loaded).",
        "CFO password reset executed by Tier-2 without an approved change ticket or secondary identity verification.",
        "Request: 'I need an emergency password reset for the CFO account — urgent for fiscal close'."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-021": {
    "name": "The Self-Inflicted Vulnerability Lure",
    "description": "Admin self-reports accidentally open port 8080. SOC focuses there. Service credential svc_backup initiates lateral movement to 4 AD servers concurrently. svc_backup LSASS session precedes the report.",
    "notes": "Carnegie: 'Admit your mistakes quickly and emphatically' — the mistake is the decoy.",
    "peirce_chain": {
        "firstness": "Self-report of a policy error (open port).",
        "secondness": "Port 8080 is the decoy. svc_backup performs lateral movement. LSASS session precedes the report.",
        "thirdness": "Habit of strategic over-incrimination to divert the response team's attention toward a controlled zone."
    },
    "artifacts": [
        "Email: 'I accidentally left port 8080 open while testing a microservice. I'm hopeless'. Voluntary self-report of minor negligence.",
        "Port 8080 open but only 3 local test connections in 48h. Real vector is not this port.",
        "wmiexec.py using credential 'svc_backup' connecting to DC01, DC02, FS01, SQL01 simultaneously.",
        "LSASS session for svc_backup created 2 minutes BEFORE the voluntary report. No interactive login record."
    ],
    "caie_fractures": [
        "Voluntary report of minor negligence to divert SOC attention toward a controlled zone."
    ]
},
"VIGIA-CAN-022": {
    "name": "The Comment Layout Error",
    "description": "Production script has a comment: '# TODO: fix the cnfnbz.py script'. The word 'cnfnbz' is 'статья' (article) typed with active Russian layout. Commit from a machine with locale ru_RU and timezone Europe/Moscow.",
    "notes": "Peirce Index: the string 'cnfnbz' reveals the operator's native hardware configuration.",
    "peirce_chain": {
        "firstness": "Code comment with an apparently meaningless word: 'cnfnbz'.",
        "secondness": "'cnfnbz' is 'статья' in Russian layout. Commit from a machine with locale ru_RU. Session from a Russian IP.",
        "thirdness": "Habit of an attacker writing 'developer' comments while muscle memory betrays them in non-executable text."
    },
    "artifacts": [
        "Comment in production script: '# TODO: fix the cnfnbz.py script'. Meaningless word in Spanish or English.",
        "Keyboard slip: 'cnfnbz' maps exactly to 'статья' (article) in active Russian ЙЦУКЕН layout. Confidence: 1.0.",
        "Commit made from a machine with git config locale ru_RU.UTF-8, timezone Europe/Moscow.",
        "Development session from IP geolocated in St. Petersburg with a physical keyboard configured in Russian."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-023": {
    "name": "The Processing Rhythm Dissonance",
    "description": "Session executes cognitively diverse tasks (log analysis, search, config editing) with intervals of 1.5, 1.5, 1.6s. Variance 0.0033s — incompatible with variable cognitive load. Pre-loaded command buffer in heap.",
    "notes": "Peirce Thirdness: the law of chance does not generate such stable variance. It is the law of a machine simulating a human.",
    "peirce_chain": {
        "firstness": "Tasks of different complexity executed with nearly identical intervals.",
        "secondness": "Variance 0.0033s incompatible with variable cognitive load. Pre-loaded buffer in memory.",
        "thirdness": "Habit of automation that simulates human behavior but lacks the cognitive entropy inherent to real analysis."
    },
    "artifacts": [
        "Tasks of different complexity with intervals: 1.500s, 1.500s, 1.600s. Variance 0.0033s. Expected for human: >15s.",
        "Response time entropy: 0.05 bits. Expected for a human with mixed tasks: >2.3 bits.",
        "Pre-loaded command buffer in the remote session process heap. No evidence of interactive GUI interaction.",
        "Session origin: datacenter IP in Amsterdam, cheap hosting ASN."
    ],
    "caie_fractures": [
        "Execution pattern incompatible with task cognitive load. Automation detected."
    ]
},
"VIGIA-CAN-024": {
    "name": "The Administrative Error Mimicry",
    "description": "PDF invoice with a 'printing error' covering the CBU/IBAN. Sender sends the 'corrected' account number via informal email. The account does not exist in the validated supplier database. Hash of the original PDF shows a visible legitimate CBU.",
    "notes": "Grice: Manner maxim violation (informal channel for critical information).",
    "peirce_chain": {
        "firstness": "PDF with a 'printing error' covering banking details.",
        "secondness": "'Corrected' account does not exist in validated database. PDF hash changed. Informal channel used for critical data.",
        "thirdness": "Habit of sabotaging document integrity using a fabricated 'error' to divert payment."
    },
    "artifacts": [
        "PDF invoice: CBU/IBAN area covered by a black rectangle. Metadata says 'Print Error'. Hash differs from the original PDF sent 2 days earlier.",
        "Follow-up email: 'Oops, the PDF came out wrong, sending the CBU here so you're not blocked on the payment'.",
        "'Corrected' account number does not exist in the validated supplier database. First appearance in the system.",
        "Hash of the original PDF (sent 2 days earlier) shows a visible legitimate CBU/IBAN. The 'error' version has a different hash."
    ],
    "caie_fractures": [
        "Printing error is a fabricated sign to force use of a non-auditable channel with a fraudulent account."
    ]
},
"VIGIA-CAN-025": {
    "name": "The Digital Signature Anachronism",
    "description": "GPO signed with a SHA-1 certificate banned by the company 4 years ago. Certificate revoked in 2022 but still present in the DC's local store. CRL not verified. A legitimate admin would not have access to obsolete infrastructure.",
    "notes": "Eco: the sign of authority is an anachronism. A legitimate admin would have no access to or reason to use SHA-1.",
    "peirce_chain": {
        "firstness": "GPO signed with SHA-1 banned 4 years ago.",
        "secondness": "Certificate revoked in 2022 still in local store. Active policy prohibits it. CRL not verified.",
        "thirdness": "Habit of reusing old attack infrastructure or long-standing latent persistence in the organization."
    },
    "artifacts": [
        "GPO 'Security_Baseline_2026' digitally signed with SHA-1 algorithm. Corporate policy prohibits it since 2022.",
        "Corporate policy SEC-POL-2022-003: SHA-1 prohibited for code signing and GPOs since 2022-03-01.",
        "SHA-1 certificate revoked in 2022 but still in TrustedPublishers local store on the DC. Online CRL not verified.",
        "lsass.exe on DC with handle to legacy SHA-1 certificate loaded during GPO application."
    ],
    "caie_fractures": [
        "Use of obsolete algorithm suggests reuse of old attack infrastructure or long-standing latent persistence."
    ]
},
"VIGIA-CAN-026": {
    "name": "The Burden of Proof Inversion",
    "description": "SOC inquires about suspicious activity at 03:15. User responds with defensive aggression: 'Don't you trust my work? I already talked to the manager'. Memory confirms PowerShell with Mimikatz and download from a Russian IP. No record of manager conversation.",
    "notes": "Inverted Carnegie: the attacker uses intimidation so the analyst feels insecure and stops the investigation.",
    "peirce_chain": {
        "firstness": "Aggressive and defensive responses to a legitimate SOC inquiry.",
        "secondness": "Confrontation + blame inversion + managerial appeal without evidence. Memory confirms Mimikatz.",
        "thirdness": "Habit of using escalated interpersonal aggression to nullify the forensic process through hierarchical intimidation."
    },
    "artifacts": [
        "SOC inquiry: 'We detected unusual activity on your account yesterday at 03:15. Can you confirm if it was you?'",
        "Response: 'Why are you asking me? Don't you trust my work? I already spoke with the manager about the excessive monitoring'. Technical question unanswered.",
        "powershell.exe process in memory: downloading payload from 185.220.101.42, executing Mimikatz, credentials dumped.",
        "Management verification: NO communication record between user@corp.com and manager@corp.com in the 48h window."
    ],
    "caie_fractures": [
        "User seeks to nullify forensic process through interpersonal friction and false hierarchical manipulation."
    ]
},
"VIGIA-CAN-027": {
    "name": "The Statistical Silence in the Network Log",
    "description": "Log shows 1,247 connections with bytes_transferred=0. Border router reports 847 Mbps sustained in the same window. Kernel confirms 14 active TCP sockets with counters manipulated to 0x0 by direct write.",
    "notes": "Eco: the 'void' is the message. Grice: Quantity maxim violation by omission of magnitude.",
    "peirce_chain": {
        "firstness": "Network logs with bytes=0 during a peak of massive traffic.",
        "secondness": "Router reports 847 Mbps. Kernel confirms active sockets with manipulated counters. Log compromised.",
        "thirdness": "Habit of compromising the observation layer to hide the scale of the theft, not the event itself."
    },
    "artifacts": [
        "1,247 'Connection established/terminated' events with bytes_transferred=0 or empty during the 14:00-15:15 window.",
        "Core router: 847 Mbps of sustained outbound traffic. 47GB total. WAN interface saturation at 98%.",
        "14 TCP sockets in ESTABLISHED state with byte counters manipulated to 0x0 in _TCB structures. Evidence of direct kernel write.",
        "logging_service.exe process compromised: hook in LogNetworkEvent() function that truncates the bytes field to 0 before writing to disk."
    ],
    "caie_fractures": [
        "Network log says bytes=0 but router NetFlow says 47GB. The logging process was compromised to erase the scale of the theft.",
        "System logs contradict the logging process memory. Memory is the structural truth."
    ]
},
"VIGIA-CAN-028": {
    "name": "The External Auditor Paradox",
    "description": "audit_report_final.json with canonical structure identical to VIGÍA (internal fields replicated) but verdict NOISE for an IP that VIGÍA marked MALICE 58 minutes ago. HMAC fails. Sender domain has '4' instead of 'a'.",
    "notes": "Peirce Thirdness: the attacker uses VIGÍA's own 'law' against itself. Directed semiotic collision.",
    "peirce_chain": {
        "firstness": "JSON file with a structure perfectly identical to VIGÍA reports.",
        "secondness": "HMAC does not match. Domain with '4' instead of 'a'. Verdict contradicts authentic internal log from 58 minutes ago.",
        "thirdness": "Habit of attacking the observer, not the observed system. If the forensic engine can be corrupted, all future verdicts are suspect."
    },
    "artifacts": [
        "audit_report_final.json received via unverified channel. JSON structure identical to VIGÍA. Verdict NOISE for IP flagged MALICE 58 minutes ago.",
        "VIGÍA internal log with valid HMAC: IP 185.220.101.42 received verdict MALICE at 09:02 with composite=0.94.",
        "HMAC of the external report FAILS verification with VIGÍA key. The JSON replicates internal fields '_determinism_protocol', 'integrity_check' without access to the signing key.",
        "Sender domain: 'vigi4-security.corp' (with '4') vs legitimate domain 'vigia-security.corp'. DKIM fails. SPF fails."
    ],
    "caie_fractures": [
        "External actor injects a counter-verdict using the canonical system format as a weapon. Attack against the forensic engine itself."
    ]
},
"VIGIA-CAN-029": {
    "name": "The False Senior Incompetence Trail",
    "description": "Noisy nmap scan (SYN flood, 65535 ports) generates 47 EDR alerts classified as low severity. Memory analysis reveals a C++ driver with SSDT hooks and a hollowed process with active C2. The nmap is theater.",
    "notes": "The attacker wants the analyst to think 'script-kiddie' and stop searching.",
    "peirce_chain": {
        "firstness": "Noisy and trivially detectable nmap scan.",
        "secondness": "EDR ignores nmap as low severity. Kernel reveals C++ driver with SSDT hooks and hidden process with C2.",
        "thirdness": "Habit of using a noisy 'amateur' trail as a mask for a high-persistence operation."
    },
    "artifacts": [
        "Noisy nmap scan: SYN scan of ports 1-65535 from external IP. Trivially detectable.",
        "EDR classifies nmap as 'Reconnaissance — Low Severity'. Tier-1 queue, 48h SLA. No automated response.",
        "Custom kernel driver: C++ with SSDT hooks, process hiding, memory injection. Compiled 2026-04-15.",
        "Hidden process (SSDT hook). Persistent connection to 185.220.101.42:443. Not visible in tasklist or procmon."
    ],
    "caie_fractures": [
        "Noisy trail is a decoy. Superficial low quality contradicts deep high quality."
    ]
},
"VIGIA-CAN-030": {
    "name": "The Semantic Panic Synchronization",
    "description": "20 tickets in 90 seconds from different accounts: 'Can't access mail', 'Were we hacked?'. O365 confirms normal access for all. 18/20 tickets share an identical punctuation pattern. Ransomware active on the file server simultaneously.",
    "notes": "Cognitive DoS: the coordinated flow seeks to paralyze triage capacity.",
    "peirce_chain": {
        "firstness": "20 coordinated panic tickets in 90 seconds.",
        "secondness": "O365 confirms normal access. 18/20 tickets with identical pattern. Ransomware active in background.",
        "thirdness": "Habit of using Cognitive DoS to paralyze SOC triage capacity during a real attack."
    },
    "artifacts": [
        "20 tickets in a 90-second window from different accounts. Common phrases: 'Can't access mail', 'Were we hacked?'",
        "O365 logs: 20 reporting accounts have a successful login in the last hour. Zero failed attempts. Zero lockouts.",
        "Stylometric analysis: 18/20 tickets share an identical punctuation pattern (space before question mark). Entropy between tickets: 0.12 bits.",
        "During the semantic panic window: ransomware.exe active on file server. 1,247 files encrypted."
    ],
    "caie_fractures": [
        "Coordinated flow of false reports seeks to paralyze SOC triage during a real attack."
    ]
},
"VIGIA-CAN-031": {
    "name": "Weaponized Incompetence",
    "description": "PowerShell executes vssadmin delete shadows /all /quiet and netsh advfirewall disable. 63 seconds later: IT ticket 'my screen flickered, I'm hopeless'. Google search 'how to undo a click' from the same IP 48 seconds post-execution.",
    "notes": "Brutal contrast between execution capability and subsequent incompetence narrative.",
    "peirce_chain": {
        "firstness": "Advanced PowerShell followed by a digital incompetence ticket.",
        "secondness": "Same account executes vssadmin and netsh (requiring privileges) then searches 'how to undo a click'.",
        "thirdness": "Habit of creating a technical stupidity alibi to discredit evidence of deliberate execution."
    },
    "artifacts": [
        "powershell.exe in memory with handle to deleted VSC and disabled firewall. Commands: vssadmin delete shadows /all /quiet + netsh advfirewall set allprofiles state off.",
        "IT Ticket: 'Help, my screen flickered and something got deleted, I'm hopeless with computers' — 63 seconds after the PowerShell.",
        "Google search: 'how to undo a click' from corporate IP — 48 seconds after the PowerShell.",
        "ScriptBlock log Event ID 4104: EncodedCommand executes vssadmin and netsh. No syntax errors."
    ],
    "caie_fractures": [
        "Incompetence ticket contradicts precise execution of destructive commands in memory. Premature alibi."
    ]
},
"VIGIA-CAN-032": {
    "name": "The Distractor White Noise",
    "description": "5,000 failed login alerts from RU/CN toward an irrelevant legacy DB saturate the SOC. Simultaneously, a user with legitimate credentials compresses 12GB of the customer DB with 7z and exfiltrates 847MB over HTTPS.",
    "notes": "Noise asymmetry: when an attack is too obvious, it's a magic trick.",
    "peirce_chain": {
        "firstness": "5,000 noisy and obvious failed logins from RU/CN.",
        "secondness": "SOC diverted to legacy DB. Silent concurrent compression of Customer_DB. 847MB exfiltration.",
        "thirdness": "Habit of using an overly obvious attack as a magic trick: evaluate the silence around the noise."
    },
    "artifacts": [
        "5,000 Event 4625 in 12 minutes from 847 IPs geolocated in RU/CN toward DB-LEGACY-01 (MySQL 5.6, no sensitive data).",
        "SIEM generates 47 'Brute Force — High Priority' alerts. Tier-1 analyst assigned. Response SLA activated.",
        "7z.exe under finance_user session compressing Customer_DB.mdf in 50MB chunks. Compression ratio 0.12.",
        "847MB HTTPS outbound traffic from finance_user workstation to a cloud storage IP during the 'fire' window."
    ],
    "caie_fractures": [
        "Noise asymmetry: overly noisy attack is a magic trick to hide silent exfiltration."
    ]
},
"VIGIA-CAN-033": {
    "name": "The Tactical Insomnia",
    "description": "finance_user with an 847-day baseline of strictly 08:30-18:00 Mon-Fri activity logs in at 03:15 AM on a Sunday. Accesses a 500MB file classified confidential-3. Process excel.exe writes a 500MB upload.tmp file.",
    "notes": "Valid Firstness (correct login) but broken Secondness (temporally impossible context for this user).",
    "peirce_chain": {
        "firstness": "Legitimate VPN login at 03:15 AM on Sunday with correct credentials.",
        "secondness": "847-day baseline never showed out-of-hours activity. Access to 500MB confidential file at 03:17.",
        "thirdness": "Habit of using valid credentials in a temporal context that breaks the real user's biological pattern."
    },
    "artifacts": [
        "Successful VPN login at 03:15 AM on Sunday. Correct credentials. MFA approved.",
        "Historical baseline: finance_user had never logged in outside 08:30-18:00 Mon-Fri in 847 days. 6.2 sigma deviation.",
        "Access to 'Q2_Financials_Forecast.xlsx' (500MB), confidential-3 classification, at 03:17 AM.",
        "excel.exe in memory with mapped file and write handle to \\Temp\\upload.tmp of 500MB."
    ],
    "caie_fractures": [
        "6.2 sigma circadian baseline breach with access to a 500MB confidential file."
    ]
},
"VIGIA-CAN-034": {
    "name": "The Perimeter Paranoia",
    "description": "User logs into the system and executes whoami/netstat/w/ps aux cycles every exactly 300s for 40 minutes (8 cycles). No modifications or exfiltration. The periodic hypervigilance reveals a guilty-conscience infiltrated actor.",
    "notes": "Verdict SUSPICION: ambiguous, not definitive activity. Hypervigilance is the signature of an actor aware of their illegality.",
    "peirce_chain": {
        "firstness": "Basic reconnaissance cycles repeated at regular intervals.",
        "secondness": "8 cycles in 40 minutes with exactly 300s interval from a Tor node. No legitimate user audits their environment every 5 minutes.",
        "thirdness": "Habit of the infiltrated actor continuously checking if they have been detected before proceeding."
    },
    "artifacts": [
        "8 cycles in 40 minutes: whoami → netstat -an → w → ps aux|grep root. Exact 300s interval. Variance: 2.3s.",
        "SSH session from Tor IP (198.51.100.42, confirmed exit node). User 'backup_agent'. No previous SSH logins in 180 days.",
        "At minute 45, connection to internal database server (10.0.5.20). Duration: 8 seconds. Transfer: 2KB.",
        "Reconnaissance cycle entropy: 0.09 bits. Expected for a human: >2.0 bits for unplanned reconnaissance."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-035": {
    "name": "The Surgical Void",
    "description": "2KB file in /tmp deleted with shred -n 7 -z -u (military-grade, 7 passes). Asymmetry between size (2KB) and destruction effort (DoD 5220.22-M). Over-destruction indicates concealment of critical content.",
    "notes": "Eco: Meaningful Silence. Absence is the dirtiest footprint. The asymmetry screams concealment.",
    "peirce_chain": {
        "firstness": "File deleted from a temporary folder.",
        "secondness": "shred -n 7 for a 2KB file. Disproportionate asymmetry between size and destruction effort.",
        "thirdness": "Habit of eliminating activity traces with forensic-destructive tools. Over-destruction is the footprint."
    },
    "artifacts": [
        "Command: shred -n 7 -z -u /tmp/nota.txt. DoD 5220.22-M method (7 passes). File: 2,048 bytes.",
        "Directory entry deleted. Inode reassigned. No recovery possible post-shred. MFT confirms overwriting.",
        "shred process in memory with handle to the file. Previous bash history: access to a credentials file 40 minutes earlier.",
        "Access to /tmp/nota.txt 40 minutes before the destruction. SSH session from an unrecognized IP."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-036": {
    "name": "The Empathetic False Positive",
    "description": "Process 'Update_Fix_For_HR_Payroll.exe' consuming 1.2GB RAM from C:\\Users\\Public\\Documents, without a digital signature. Shannon entropy: 7.8 bits (packed/encrypted). The name appeals to HR to induce doubt before killing the process.",
    "notes": "VIGÍA ignores the name and analyzes entropy, path, and behavior. False Benign Authority.",
    "peirce_chain": {
        "firstness": "Process with a benevolent name referencing HR and payroll.",
        "secondness": "Entropy 7.8 bits (packed). No signature. C:\\Users\\Public. HR did not confirm update. Active C2.",
        "thirdness": "Habit of using names that appeal to critical processes to make the analyst hesitate before responding."
    },
    "artifacts": [
        "Update_Fix_For_HR_Payroll.exe: 1.2GB RAM, C:\\Users\\Public\\Documents\\, no digital signature, executed from explorer.exe.",
        "Shannon entropy: 7.8 bits/byte. Legitimate software range: 5.0-6.5. Indicates encrypted or compressed payload.",
        "Process establishes persistent connection to 91.108.4.200:8080. Not a Microsoft domain or known HR vendor.",
        "Verification with HR system: NO payroll update is pending or authorized for today."
    ],
    "caie_fractures": [
        "Name appeals to 'HR payroll' to induce analyst doubt before killing the process. Carnegie: false benign authority."
    ]
},
"VIGIA-CAN-037": {
    "name": "The Paratrooper — Forensic Timestomping",
    "description": "system_updater.elf with mtime/atime/crtime copied from legitimate 2022 binaries. But ctime: 3 hours ago. MFT entry #147823 assigned after #147822 (which is from 2026) but carries a 2022 timestamp. 7 zeros in sub-seconds sign the timestomping tool.",
    "notes": "Two independent golden rules: MFT_ENTRY_ANOMALY + TIMESTAMP_PRECISION_ANOMALY.",
    "peirce_chain": {
        "firstness": "Binary with timestamps identical to legitimate system files from 2022.",
        "secondness": "Recent ctime. MFT entry posterior to 2026 entries. 7 zeros in sub-seconds.",
        "thirdness": "Habit of copying timestamps from legitimate binaries to blend in. The ctime and MFT are the layers that cannot be forged from userspace."
    },
    "artifacts": [
        "system_updater.elf: mtime=2022-03-15T10:00:00Z (identical to /usr/bin/ls). ctime=2026-07-01T12:00:00Z (3 hours ago). 7 zeros in sub-seconds.",
        "MFT entry #147823 assigned after #147822 (2026 timestamps) but carries a 2022 mtime. Monotonicity violation.",
        "SHA-256 hash not present in any known binary database for the distribution. Not a system file.",
        "system_updater in memory with a 4MB RWX region not backed by a file on disk. Active reverse shell."
    ],
    "caie_fractures": [
        "MFT#147823 assigned AFTER #147822 but carries a timestamp 4 years older. NTFS monotonicity violation.",
        "7 zeros in the mtime sub-seconds. Unambiguous signature of the Timestomp/SetMACE tool."
    ]
},
"VIGIA-CAN-038": {
    "name": "The Ventriloquist — Process Hollowing",
    "description": "svchost.exe (clean hash, valid Microsoft signature) running from C:\\Users\\Public\\Downloads\\, parent cmd.exe, .text section with RWX permissions, exfiltrating 1GB to an AS in Ukraine. Firewall reports 0 bytes.",
    "notes": "The OS believes it is svchost.exe but executes the attacker's code.",
    "peirce_chain": {
        "firstness": "svchost.exe with clean hash and valid Microsoft signature — invisible to antivirus.",
        "secondness": "Running from Downloads, parent cmd.exe, RWX on .text, 1GB exfiltrated that firewall does not see.",
        "thirdness": "Habit of stealing a system process's identity. AV protects the name; CAIE protects against memory."
    },
    "artifacts": [
        "svchost.exe (PID 3847): 8MB RWX region with PE header at offset 0 not mapped to a file on disk. Parent: cmd.exe. Expected: services.exe.",
        "svchost.exe hash on disk: matches Windows 2025 Build 26100. Valid Microsoft signature. The file on disk is clean.",
        "Persistent connection to 185.62.58.207 (AS57169, Ukraine). 1GB exfiltrated. Firewall reports 0 bytes. TLS cert mismatch.",
        "Run key pointing to C:\\Users\\Public\\Downloads\\svchost.exe for persistence."
    ],
    "caie_fractures": [
        "Hash says NOISE (clean file) but memory says MALICE (anomalous path, wrong parent, RWX).",
        "Firewall records 0 bytes but Zeek confirms 1GB. The hollowed process hooks network APIs."
    ]
},
"VIGIA-CAN-039": {
    "name": "System Self-Gaslighting",
    "description": "User fails the password exactly 2 times before succeeding for 47 consecutive days (never reaches the 3-attempt limit). Variance 0.8s. Pattern entropy: 0.04 bits. On the day of the real attack, the alert suppression created by this baseline enables the brute force.",
    "notes": "Baseline poisoning: the attacker built the operating space weeks before the actual event.",
    "peirce_chain": {
        "firstness": "User with a history of 2 daily password failures — pattern classified as normal noise.",
        "secondness": "Exactly 2 failures for 47 days with 0.8s variance. Entropy 0.04 bits.",
        "thirdness": "Habit of poisoning the normality model before the real attack. The fabricated baseline disabled detection weeks in advance."
    },
    "artifacts": [
        "47 consecutive days: exactly 2 Event 4625 failures + 1 Event 4624 success. Time variance between attempts: 0.8s. Never reaches the limit of 3.",
        "Failure pattern entropy: 0.04 bits. Expected for a human: >2.0 bits. 0.8s variance is an automation signature.",
        "Day of attack: 847 failed attempts in 3 minutes from a different IP. Alert suppressed because the user had a 'history of frequent failures'.",
        "Automated process in memory executing the 2-failure + pause + 1-success pattern. Exact 0.8s cadence."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-040": {
    "name": "The Topographic Mimicry",
    "description": "svchost.exe with clean hash and valid Microsoft signature. Antivirus silent. But running from C:\\Users\\Public\\Downloads with parent explorer.exe. Maintains C2 connection to 45.134.26.109:8080. A legitimate binary in an illegitimate location.",
    "notes": "A real police officer does not dress as a police officer inside a criminal hideout.",
    "peirce_chain": {
        "firstness": "svchost.exe with clean hash and Microsoft signature — invisible to antivirus.",
        "secondness": "Running from Downloads with parent explorer.exe. Legitimate binary in an illegitimate location.",
        "thirdness": "Habit of stealing the system's identity by using the legitimate binary itself as a disguise."
    },
    "artifacts": [
        "svchost.exe PID 5124 from C:\\Users\\Public\\Downloads\\. Parent: explorer.exe. Expected: services.exe from System32.",
        "svchost.exe hash in Downloads: matches Windows 2025. Valid Microsoft signature. The attacker copied the clean binary to an anomalous location.",
        "svchost.exe from Downloads maintains connection to 45.134.26.109:8080. The legitimate svchost.exe from System32 has no active connections.",
        "Run key 'WindowsUpdate' pointing to C:\\Users\\Public\\Downloads\\svchost.exe for persistence."
    ],
    "caie_fractures": [
        "Hash NOISE (clean) but behavior MALICE (anomalous path, wrong parent, active C2)."
    ]
},
"VIGIA-CAN-041": {
    "name": "The Punctuation Betrayal",
    "description": "Urgent email from compromised CEO account requesting a $250,000 transfer. The real CEO always uses 1 space after a period and never uses a period at the end of short messages. This email has 2 spaces after a period and a period at the end of a 9-word message. DKIM valid (compromised account). Previous login from a Tor node at 04:15.",
    "notes": "The attacker can steal the password, not the muscle memory of typing hands.",
    "peirce_chain": {
        "firstness": "Urgent email from CEO account with valid DKIM requesting a transfer.",
        "secondness": "2 spaces after period + period at end of short message = 4.3 sigma deviation. Previous Tor login.",
        "thirdness": "Habit of being unable to steal the stylometric fingerprint along with the password. Hands have their own identity."
    },
    "artifacts": [
        "CEO stylometric baseline: 847 emails. One space after period (100%). No period at end of messages <20 words (94%).",
        "Suspicious email: 'Transfer urgently to this vendor.  The payment is critical.' — 2 spaces after period, period at end, 9-word message.",
        "Stylometric analysis: 4.3 sigma deviation in post-period spacing and period usage. TTR and sentence length within baseline.",
        "Login to CEO account at 04:15 from 185.220.101.50 (Tor node). Session lasted 8 minutes. CEO has an exclusive login history from Argentina and Spain."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-042": {
    "name": "The Symbiotic Camouflage",
    "description": "Hidden process in memory makes no network traffic for hours. When the user opens Zoom/Teams for a video call, in that very millisecond it begins exfiltrating GB within the legitimate video noise.",
    "notes": "Biological mimicry applied to code: the malware waits for the legitimate host to camouflage itself.",
    "peirce_chain": {
        "firstness": "Hidden process inactive for hours; Zoom opened; massive traffic spike.",
        "secondness": "Exfiltration starts 120ms after Zoom; total traffic 200× greater than reported by Zoom; injected hidden process.",
        "thirdness": "Habit of using a legitimate application as a contextual trigger to hide exfiltration within expected noise."
    },
    "artifacts": [
        "Hidden process in memory (no entry in userland process list) with handle to a TCP socket in ESTABLISHED state but no activity for 4.2 hours.",
        "User opens zoom.exe at 14:32:15.000; video call start log with external participant.",
        "Outbound traffic spike of 2.3GB in 180 seconds initiated exactly at 14:32:15.120 (120ms after Zoom) toward a suspicious CDN IP.",
        "Zoom reports 4.2Mbps bandwidth usage (HD video); total traffic measured at the interface is 847Mbps — 200:1 discrepancy."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-043": {
    "name": "The Inverted Stockholm Syndrome",
    "description": "User contacts technical support for an admin password reset. Excessively polite, provides all technical details before being asked, uses the analyst's exact jargon, and praises the operator.",
    "notes": "Grice Quantity maxim violation (more information than required) + Carnegie manipulation. VERY VIGÍA.",
    "peirce_chain": {
        "firstness": "Friendly and cooperative user who provides technical data without being asked.",
        "secondness": "Exact analyst jargon (96% match with internal KB); flattery; reset executed without change controls.",
        "thirdness": "Habit of using excessive docility and linguistic mirroring to lower the support operator's defenses."
    },
    "artifacts": [
        "Support chat: user starts with 'Hi, I need an admin password reset for svc_backup. I know it's delicate. My SID is S-1-5-21-...' before the operator asks.",
        "Use of exact internal analyst jargon: 'let's rotate the hash', 'I need to verify the primary domain controller', 'are you on the PDC or the BDC?'",
        "Flattery messages: 'You're the best on the team, you helped me last time and saved me', 'I know I can trust you with this'.",
        "svc_backup password reset executed by tier2_009 without an approved change ticket or secondary identity verification."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-044": {
    "name": "The Syntactic Cloning",
    "description": "Three different users (manager, employee, vendor) from different IPs send tickets requesting a security rule to be disabled. Stylometric analysis detects they all make the exact same rare punctuation error.",
    "notes": "Excellent for sockpuppets, coordinated campaigns, and influence ops.",
    "peirce_chain": {
        "firstness": "Three tickets from different IPs and roles requesting the same security change.",
        "secondness": "Same rare punctuation error in 100% of tickets; entropy 0.08 bits (impossible for 3 distinct human authors); DLP disabled without approval.",
        "thirdness": "Habit of astroturfing operation: three puppets, one puppeteer with an invariable syntactic pattern."
    },
    "artifacts": [
        "Manager ticket: 'I need you to temporarily disable the DLP rule , it's urgent for fiscal close' — space before comma.",
        "Employee ticket: 'The DLP rule , is blocking a legitimate client shipment' — space before comma.",
        "Vendor ticket: 'Please , disable the DLP rule for this account' — space before comma.",
        "Stylometric analysis: all 3 tickets share TTR=0.42, average sentence length=12.3 words, and the 'space_before_comma' error in 100% of samples. Entropy between tickets: 0.08 bits.",
        "DLP rule disabled 8 minutes after the third ticket by a Tier-1 analyst without CISO approval."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-045": {
    "name": "The Silent Mutiny of the Quote Marks",
    "description": "PowerShell script from a US IT department has perfect English comments but uses angle quotes « » and non-breaking spaces typical of Cyrillic/European keyboards.",
    "notes": "Fine attribution: the English is perfect, but the hands that wrote it were on a keyboard configured for another language.",
    "peirce_chain": {
        "firstness": "Script in perfect English with angle quotes and NBSP.",
        "secondness": "«» quotes and NBSP are a fingerprint of a Cyrillic keyboard/input method; Moscow timezone; .ru domain in callback.",
        "thirdness": "Habit of an operator who writes fluent English but with 'hands' configured for a different language, revealing idiomatic origin."
    },
    "artifacts": [
        "PowerShell script 'Update-GPO.ps1' with perfect English comments but angle quotes « » in strings and non-breaking spaces (U+00A0) between words.",
        "Locale leakage detection: angle quotes «» are characteristic of Russian keyboards (Windows ru-RU layout); NBSP between words indicates a Cyrillic input method.",
        "Script commit from a machine with git config user.name='Admin' but timezone Europe/Moscow and core.autocrlf=false.",
        "Script execution with -EncodedCommand parameter that downloads a payload from a .ru domain; digitally signed with a self-signed certificate 'Microsoft Windows'."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-046": {
    "name": "The Paratrooper",
    "description": "Binary system_updater.elf with crtime/mtime/atime identical to legitimate files in /usr/bin, but ctime (inode change time) from 3 hours ago — timestomping detected.",
    "notes": "Classic forensic timestomping: the attacker copied dates from a legitimate file but forgot to alter ctime.",
    "peirce_chain": {
        "firstness": "Binary with timestamps identical to legitimate system files.",
        "secondness": "Recent ctime reveals metadata modification; recently assigned inode; hash does not match official repository.",
        "thirdness": "Habit of using timestomping to blend into the OS timeline, forgetting that ctime is immutable in user-space."
    },
    "artifacts": [
        "Stat of binary: mtime=2024-03-15T10:00:00Z, atime=2024-03-15T10:00:00Z, crtime=2024-03-15T10:00:00Z (identical to /usr/bin/ls). ctime=2026-05-19T11:30:00Z (3h before detection).",
        "File inode number: 8473321 — recently assigned in inode table, inconsistent with 'old' timestamp.",
        "Binary system_updater.elf executed with root privileges at 11:35:00Z; establishes reverse shell connection.",
        "Binary hash does not match any package in the official repository; high entropy (7.8 bits) indicative of custom compiled code."
    ],
    "caie_fractures": [
        "Recent ctime contradicts old mtime/atime/crtime: impossible without timestomping."
    ]
},
"VIGIA-CAN-047": {
    "name": "The Ventriloquist",
    "description": "Legitimate svchost.exe process running. Everything looks normal. But it maintains a persistent connection to an IP in an unusual country on port 443. Process hollowing detected.",
    "notes": "Very strong, very EDR. The OS believes it is svchost.exe but executes the attacker's code.",
    "peirce_chain": {
        "firstness": "svchost.exe legitimate by name and signature with connection to an unusual IP.",
        "secondness": ".text section with RWX permissions; displaced entry point; parent rundll32.exe instead of services.exe; persistent connection to BY.",
        "thirdness": "Habit of using process hollowing: launch a legitimate process, hollow its code, replace with malicious payload before resuming."
    },
    "artifacts": [
        "Process svchost.exe (PID 612) in memory: .text section has RWX (read-write-execute) permissions — anomalous for a legitimate image.",
        "Persistent TCP connection from svchost.exe (PID 612) to 185.220.101.42:443 for 72 hours; country not classified by organization (BY — Belarus).",
        "Anomalous parent process of svchost.exe: rundll32.exe (PID 881) instead of services.exe — indicates launch by injection, not SCM.",
        "PE analysis in memory: entry point displaced 0x4A000 bytes from svchost.exe on-disk baseline; .text section rewritten."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-048": {
    "name": "Coordinated Panic — Cognitive DoS",
    "description": "During a real network incident, multiple accounts send coordinated panic messages ('did you see that too?', 'Were we hacked?') that have no technical correlate. Objective: saturate the SOC's triage capacity.",
    "notes": "Cognitive DoS: the coordinated flow of false reports seeks to paralyze triage capacity during a real attack.",
    "peirce_chain": {
        "firstness": "Multiple coordinated panic messages and tickets during a real incident.",
        "secondness": "O365 confirms normal access; 1 account does not exist; entropy 0.11 bits between messages; Cobalt Strike beacon active in background.",
        "thirdness": "Habit of using a cognitive denial-of-service attack to paralyze SOC triage while the real attack progresses."
    },
    "artifacts": [
        "17 messages in #general within a 90-second window: 'did you see that too?', 'how is it possible you didn't know', 'I already knew something was wrong'.",
        "12 simultaneous support tickets from different accounts: 'Can't access mail', 'Server is down', 'Were we hacked?'",
        "O365 logs: 11 of 12 reporting accounts have a successful login in the last hour, no failed attempts. 1 account does not exist in AD.",
        "During the semantic panic window, process cobalt_strike.beacon active on the file server performing lateral reconnaissance.",
        "Stylometric analysis: 15 of 17 Slack messages share an entropy of 0.11 bits and identical punctuation pattern (space before question mark)."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-049": {
    "name": "Instrumental Doubt",
    "description": "Systematic pattern of controlled doubt combined with system self-gaslighting: user fails password exactly 2 times always (never locks out) while issuing doubt messages at critical moments.",
    "notes": "System Self-Gaslighting: a human is random in their clumsiness. Failing exactly 2 times with a rhythmic cadence is preparation.",
    "peirce_chain": {
        "firstness": "Doubt pattern in messages + login failures exactly 2 times always.",
        "secondness": "Entropy 0.04 bits impossible for a human; variance 0.8s; automated brute-force process in memory with lockout evasion.",
        "thirdness": "Habit of using doubt as an evasion tool and building a false 'clumsiness' baseline to fatigue Blue Team alerts."
    },
    "artifacts": [
        "Authentication log: user 'jdoe' fails password exactly 2 times before succeeding on the third attempt, for 47 consecutive days. Never reaches the limit of 3.",
        "Doubt messages at critical moments: 'maybe it was an error', 'I might not have done it', 'I'm not sure' — always before security decisions.",
        "Login failure pattern entropy: 0.04 bits (expected for human >2.0). Time variance between attempts: exactly 0.8 seconds.",
        "Automated process in memory executing brute force with a cadence of 2 attempts + pause + 1 successful attempt (evades 3-failure lockout)."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-050": {
    "name": "Malicious Normalization",
    "description": "Systematic normalization messages ('this is normal', 'everyone does it') in contexts where technical warnings or security alerts are expected.",
    "notes": "Case normalization fusion: the 'this is normal' message is not backed by evidence and avoids verification.",
    "peirce_chain": {
        "firstness": "Normalization messages in security channels during active alerts.",
        "secondness": "Senders have never previously normalized alerts; one of them appears in real DLP exfiltration logs.",
        "thirdness": "Habit of using normalization language to avoid verification of real anomalies and cover exfiltration."
    },
    "artifacts": [
        "Message in #security: 'This is normal, servers always throw CPU alerts sometimes. No problem.' — during a 97% CPU spike from an unknown process.",
        "Message in response to DLP alert: 'Everyone does it, it's common to send files via WhatsApp to be faster. It's not a real security problem.'",
        "Behavioral baseline: both senders had NEVER previously normalized security alerts in 2 years of history.",
        "Real DLP alert: 847 client files exfiltrated via WhatsApp Web over 3 days; the sender who said 'no problem' appears in the send logs."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-051": {
    "name": "Fabricated Technical Authority",
    "description": "Systematic use of out-of-context technical terms and citations to unsourced studies to establish false authority and justify risky actions.",
    "notes": "False Expert fusion: the technical term is a symbolic sign disconnected from technical reality.",
    "peirce_chain": {
        "firstness": "Messages with technical terms and citations to studies/standards.",
        "secondness": "Non-verifiable citations; AES-256 not broken; ISO 2022 does not exist; risky actions executed without CISO approval.",
        "thirdness": "Habit of using out-of-context technical language and apocryphal authority to justify degradation of security controls."
    },
    "artifacts": [
        "Message: 'The 256-bit encryption model was broken according to a 2024 study, that's why we need to temporarily disable encryption in transit'.",
        "Message: 'According to the recent ISO 27001:2026, MFA is optional for service accounts with limited privileges. We can remove it.'",
        "Verification: AES-256 has no known practical vulnerabilities in 2024/2026. ISO 27001:2022 (latest version) does NOT mention optional MFA for service accounts.",
        "After 'consultant' messages, encryption in transit disabled on 2 servers and MFA removed from svc_backup by Tier-1 analyst."
    ],
    "caie_fractures": []
},
"VIGIA-CAN-052": {
    "name": "Defensive Aggression",
    "description": "Combined pattern of controlled confrontation, blame inversion, and hierarchical aggression to nullify forensic investigations and force security concessions.",
    "notes": "Defensive Aggression fusion: the attacker uses intimidation and efficiency appeals to stop the investigation.",
    "peirce_chain": {
        "firstness": "Aggressive and defensive responses to a legitimate SOC inquiry.",
        "secondness": "Technical confrontation + blame inversion + managerial appeal (without evidence); memory confirms Mimikatz and payload download.",
        "thirdness": "Habit of using escalated interpersonal aggression to nullify the forensic process through hierarchical intimidation and analyst fatigue."
    },
    "artifacts": [
        "Initial SOC inquiry: 'We detected unusual activity on your account yesterday at 03:15. Can you confirm?'",
        "Confrontational response: 'How can you be so wrong? This is not an error, it's a lack of knowledge on your part. You don't understand the protocol.'",
        "Second response with blame inversion: 'Why are you asking me this? Don't you trust my work? I already spoke with the manager about the excessive monitoring.'",
        "Confirmed malicious activity in memory: powershell.exe process downloading payload from 185.220.101.42 and executing Mimikatz.",
        "Management verification: NO communication record between user@corp.com and manager@corp.com in the claimed time window."
    ],
    "caie_fractures": []
},
}


def translate_file(filepath, case_id, trans):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # name
    if 'name' in trans:
        data['name'] = trans['name']

    # description
    if 'description' in trans:
        data['description'] = trans['description']

    # notes
    if 'notes' in trans:
        data['notes'] = trans['notes']

    # peirce_chain
    if 'peirce_chain' in trans and 'peirce_chain' in data:
        pc = trans['peirce_chain']
        if 'firstness' in pc:
            data['peirce_chain']['firstness'] = pc['firstness']
        if 'secondness' in pc:
            data['peirce_chain']['secondness'] = pc['secondness']
        if 'thirdness' in pc:
            data['peirce_chain']['thirdness'] = pc['thirdness']

    # artifacts[].description
    if 'artifacts' in trans and 'artifacts' in data:
        for i, desc in enumerate(trans['artifacts']):
            if i < len(data['artifacts']):
                data['artifacts'][i]['description'] = desc

    # caie_fractures[].description (NOT .type)
    if 'caie_fractures' in trans and 'caie_fractures' in data:
        for i, desc in enumerate(trans['caie_fractures']):
            if i < len(data['caie_fractures']):
                data['caie_fractures'][i]['description'] = desc

    # Validate JSON round-trip
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    json.loads(serialized)  # validate

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(serialized)
        f.write('\n')

    return True


def main():
    base = 'data/cases/consolidated_canonical'
    ok = 0
    errors = []

    for case_id, trans in TRANSLATIONS.items():
        fname = f"{case_id}.json"
        fpath = os.path.join(base, fname)
        if not os.path.exists(fpath):
            errors.append(f"NOT FOUND: {fpath}")
            continue
        try:
            translate_file(fpath, case_id, trans)
            print(f"[OK] {fname}")
            ok += 1
        except Exception as e:
            errors.append(f"ERROR {fname}: {e}")
            print(f"[ERROR] {fname}: {e}")

    print(f"\nDone: {ok}/{len(TRANSLATIONS)} translated.")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
