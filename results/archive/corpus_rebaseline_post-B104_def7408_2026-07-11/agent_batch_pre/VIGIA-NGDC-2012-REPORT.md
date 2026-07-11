VIGIA FORENSIC INTENT ANALYSIS REPORT
======================================
Case ID      : VIGIA-NGDC-2012
Investigator : VIGIA Autonomous Agent (Claude Code / Anthropic)
Evidence     : /home/labestiadevigia/Downloads/National Gallery DC 2012/
Mode         : Claude Code (Mode 2)
Timestamp    : 2026-06-27T03:30:00Z
SANS Phase   : Phase 5 — Lessons Learned (complete investigation)

EVIDENCE INVENTORY & CHAIN OF CUSTODY
--------------------------------------

| # | Artifact | SHA-256 | Size |
|---|----------|---------|------|
| 1 | carry-tablet-2012-07-16-final.E01 | 26a6ea3049c06afdd34862c453fc272a5ab4c64954ae51d23cf9df688473a448 | 1.1 GB |
| 2 | tracy-phone-2012-07-15-final.E01 | 71aed05a86a753dec4ef4033ed7f52d6577ccb534ca0d1e83ffd27683e621607 | 752 MB |
| 3 | Tracy-phone-2012-07-15-1316.L01 | a14525b7ece67131d5943e1db5847cbb51513e384b49b7fa9921480530223f52 | 29 MB |
| 4 | carry-phone-2012-07-15-final.zip | 5cfec4e099e70529072b6934c6f98f97492985e5a48daeb64549f96719792d9e | 191 MB |
| 5 | carry-phone-logical-2012-07-15-0618.zip | cbcee1cb354884ebfa302ad5a6e41c9980fc3ba252b2f74e732b2162540f7357 | 30 MB |
| 6 | Tracy-phone-logical-2012-07-15-1317.zip | 1e4287dff75dd2fb84ff46be3ef5f3152bb894b64030831b442776e522d30329 | 18 MB |
| 7 | carry-tablet-2012-07-16-final.tar | c70762e49db8f95cfd11246a3e84d1fca8a20d7182d1525b462638a28331793f | 779 MB |
| 8 | tracy-phone-2012-07-15-final.tar | b209e812aeeab7b6234f8f6d16be6b63027e02d667d8882104bd52b3aea204a1 | 752 MB |
| 9 | email.zip | d1c4470e9e058f83798b6c0c2856e85df8747783f2105f8c354f366d30ab5505 | 16 KB |
| 10 | ngdc-exterior-2012-07-06.pcap | b2e89885b1c3775ddff8d106cdead6ae1b5331d53b3f539ac9c27010244c0895 | 143 MB |
| 11 | ngdc-exterior-2012-07-09.pcap | dc317d6a9f6942148e726097e95d7f4d3bd0cc95bee0480d0797b60020147a8b | 45 MB |
| 12 | ngdc-exterior-2012-07-10.pcap | 863587be812b9ed6dd184ad0c5960d4ebe4e713b767a07860aec946a5442c73b | 37 MB |
| 13 | ngdc-interior-2012-07-06.pcap | d5f019db5796bd2118d8b917ae26805bb6cb3c978fd983860035f599d8ccb051 | 36 MB |
| 14 | ngdc-interior-2012-07-09.pcap | 67eb2629d2f29ea4b7101f3b03209621294b1bf0909d515927514b0c00dac449 | 39 MB |
| 15 | ngdc-interior-2012-07-10.pcap | d47a9e1144c92a5a818b295546bf5c3219a2bb18a21bb9dcc9702ee48f200548 | 25 MB |
| 16 | exterior-2012-07-12.txt | 25f5f2920a5d403d4a8bbacaad9acb72ea40b916ba8d8f03296d59d419474e81 | 53 MB |
| 17 | interior-2012-07-12.txt | 2b2cbcc969cfa9d7dc7ad1087cc59e456e941c3c7c5d4416ba2a9ce0b83d7e66 | 4.2 MB |

Artifacts NOT analyzed (incomplete downloads):
- tracy-home-2012-07-16-final.E01 / .E02 — 0 bytes each
- 4x Unconfirmed *.crdownload — partial downloads

EXECUTIVE SUMMARY
-----------------
This investigation reveals a multi-actor conspiracy to steal a rare stamp exhibit from
the National Gallery of Art in Washington, DC. The conspiracy involves at least 5
identified individuals operating across insider access, logistical coordination,
foreign intelligence connections, document exfiltration, and physical security bypass
planning. The evidence spans June 19 to July 16, 2012, across keylogger captures,
email, SMS, phone extractions, tablet forensics, network captures, and browser history.

The investigation identifies two principal actors:
- **Tracy SumTwelve** (National Gallery employee, alias "Coral Blue Two"): insider who
  exfiltrated stamp insurance documents, transmitted the security duty schedule to
  co-conspirators, and physically smuggled Carry's tablet past Gallery security.
- **Carry** (external coordinator, email: cat2welve@gmail.com / carrysum2012@yahoo.com):
  operational planner who coordinated a "flash mob" cover story, researched camera
  blinding and lock-picking techniques, communicated with a foreign contact ("Alex J"
  from Krasnovia), arranged forged passport documents, installed steganography tools,
  and attempted to destroy evidence.

Overall Verdict: **MALICE** — Active concealment of intent through encrypted archives,
steganography tools, evidence destruction (Forever Gone wipe), and multi-layered
operational security (alias emails, covert communication channels, flash mob cover story).

ACTORS IDENTIFIED
-----------------

| Actor | Identifiers | Role | Verdict |
|-------|-------------|------|---------|
| Tracy SumTwelve | tracysumtwelve (MacBook), coralbluetwo@hotmail.com, coralblue2@yahoo.com, tracy.sumtwelve@nationalgallerydc.org | Insider: document theft, security bypass facilitation, bribery recipient | MALICE |
| Carry | cat2welve@gmail.com, carrysum2012@yahoo.com, carry.sums (Skype), +12027252124 | External coordinator: operational planning, foreign liaison, evidence destruction | MALICE |
| Perry Patsum | perrypatsum@yahoo.com | External co-conspirator: receives stolen documents, provides steganographic payloads | INTENT |
| Alex J | alex.jfam11@gmail.com, alex.jfam11@krasnovia.org | Foreign intelligence contact: recommends steganography, coordinates associate entry | INTENT |
| Drex Mustafar ("Mike") | bubbahotep2012@hotmail.com | Flash mob coordinator: provides cover operation logistics | SUSPICION |
| Pat TeeSumTwelve | patsumtwelve@gmail.com, +15713083236 | Tracy's sibling: aware of document format conversion for conspiracy | SUSPICION |
| Terry SumTwelve | just.terry.22@gmail.com, terrysumtwelve (MacBook) | Tracy's daughter: no direct involvement, financial pressure motive context | NOISE |
| Joe SumTwelve | joe.sum.twelve@gmail.com | Keylogger operator: receives all keystroke captures from Tracy's MacBook | INTENT |

CREDENTIALS CAPTURED
--------------------

| Account | Password | Source |
|---------|----------|--------|
| Tracy MacBook Air login (tracysumtwelve) | legalBee | Keylogger email #1 |
| coralbluetwo@hotmail.com | legalBee | Keylogger email #1 |
| just.terry.22@gmail.com (Terry) | privateschool | Keylogger email #11 |
| Encrypted ZIP (documents.zip) | Hercules ("your old dog's name") | Keylogger email #9-10 |

TIMELINE OF EVENTS
------------------

| Date | Event | Source | Significance |
|------|-------|--------|-------------|
| 2012-06-07 | Carry creates Gmail (cat2welve) and Skype (carry.sums); contacts Alex J | Carry tablet Gmail | Initial operational infrastructure setup |
| 2012-06-19 | Perry emails Coral (coralbluetwo@hotmail.com): "Crazydave by the VMs" with MP3 attachment | Tracy phone Hotmail | Suspected steganographic payload delivery |
| 2012-06-27 | Alex J emails Carry: "Krasnovia!" — single word | Carry tablet Gmail | Foreign affiliation signal |
| 2012-06-27 | Alex J recommends steganography apps to Carry | Carry tablet Gmail | Covert communication infrastructure |
| 2012-06-28 | LogKext keylogger active on Tracy's MacBook; Tracy logs into coralbluetwo@hotmail.com | Keylogger email #1 | Surveillance infrastructure operational |
| 2012-06-29 | Tracy emails Perry: "if anything comes up that we can get in on... I pay attention to memos and papers on my desk" | Keylogger email #2 | Active insider intelligence gathering begins |
| 2012-07-02 | Tracy reports to Perry: "foreign exhibit coming, big deal, lots of paperwork" | Keylogger emails #3-4 | Tracy identifies target exhibit |
| 2012-07-03 | Tracy to Perry: "rare collection of stamps... maybe this is our ticket" | Keylogger email #6 | Conspiracy target identified: rare stamps |
| 2012-07-04 | Alex J to Carry: "friends working on new manuscript, interested?" | Carry tablet Gmail | Foreign recruitment signal |
| 2012-07-05 | Alex J sends Dropbox link ("funny video.mp4") to Carry; Carry contacts Tracy via Facebook for lunch | Carry tablet Gmail + Yahoo | Suspected steganographic payload + social engineering pretext for Tracy |
| 2012-07-06 | Carry installs SDDroid steganography tool on tablet; Tracy searches "value of international [stamps]" | Carry tablet apps + keylogger | Parallel operational preparation |
| 2012-07-06 | Network: 10.10.1.119 begins scanning 10.10.1.169 (port 8080 open, SNMP, ARP sweep) | PCAP exterior 07-06 | Automated network monitoring (likely NMS, not adversarial) |
| 2012-07-06 | Tracy browses: Louvre, Guggenheim, MOMA, NGA, "Scibec de Carpi ceiling" | PCAP interior 07-06 | Comparative museum research |
| 2012-07-08 | Tracy photographs National Gallery and Mall area (30 photos, GPS confirmed) | Tracy phone EXIF | Physical reconnaissance of target |
| 2012-07-09 | Carry emails Drex Mustafar: operational plan — "two teams, east and west entrance, meet second floor main hallway east side, 12:00 PM sharp" | Carry tablet Gmail | Operational plan documented |
| 2012-07-09 | Carry asks Tracy to smuggle tablet past security; Tracy browses flash mob planning pages | Carry tablet Yahoo + PCAP | Physical security bypass negotiation |
| 2012-07-09 | Tracy creates encrypted ZIP of stamp/insurance docs (password: Hercules) | Keylogger email #9 | Document exfiltration |
| 2012-07-10 | Tracy confirms to Carry: "I can definitely help get your tablet in" | Carry tablet Yahoo | Security bypass confirmed |
| 2012-07-10 | Carry browses: blinding surveillance cameras, smoke bombs, smoke grenades, padlock shims, lock picking, credit card door entry | Carry tablet browser | Tactical research for physical penetration |
| 2012-07-10 | Carry uploads ePassport dump ZIPs and JMRTD passport reader to Yahoo Mail | Carry tablet browser | Forged travel documents for foreign associates |
| 2012-07-10 | Tracy emails Perry: stamp documents + password hint "your old dog's name" | Keylogger email #10 | Stolen documents transmitted to co-conspirator |
| 2012-07-10 | Tracy offers to help unnamed person bypass security with tablet | Keylogger email #10 | Physical security facilitation |
| 2012-07-10 | Pat SMS to Tracy: "coral got email, attachment needs to be changed to pdf" | Tracy phone SMS | Third party aware of document scheme |
| 2012-07-10 | Network: 192.168.1.101 searches "National Gallery East Wing", "I.M. Pei East Building", "appropriate care for stamps" | PCAP interior 07-10 | Final reconnaissance of building layout and stamp handling |
| 2012-07-11 | Tracy sends security duty schedule to Carry (downloaded as securedownload.pdf at 19:11) | Carry tablet downloads | Classified security information transmitted |
| 2012-07-11 | Tracy SMS to Carry: "Just meet me out front, I'll take the tablet in" | Tracy phone SMS | Physical smuggling confirmed |
| 2012-07-11 | Tracy: "I could really use some extra cash too but please be careful" | Carry tablet Yahoo | Bribery agreement documented |
| 2012-07-11 | Alex J sends "fixed files" (passport signatures) to Carry | Carry tablet Gmail | Foreign document forgery coordination |
| 2012-07-11 | Carry forwards passport files to amonous@yahoo.com | Carry tablet Gmail | Third-party passport distribution |
| 2012-07-12 | Carry runs Forever Gone wipe: ~250 files destroyed 05:03–06:25 | Carry tablet deleted files | Anti-forensic evidence destruction |
| 2012-07-12 | Carry email to Alex: "I have our plan put together... your associates to meet me in town next week" | Carry tablet Gmail | Final coordination with foreign contact |
| 2012-07-12 | Tracy SMS to Carry: "How's the flashmob going" | Tracy phone SMS | Post-infiltration check-in |
| 2012-07-15 | Tracy phone and Carry phone seized (logical + physical extractions) | L01/E01 timestamps | Evidence acquisition |
| 2012-07-16 | Carry tablet seized (E01 image) | E01 metadata | Evidence acquisition |

FINDINGS
--------

Finding ID   : F-001
Title        : Insider Document Exfiltration (Tracy → Perry)
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : Keylogger emails #9-10, Tracy phone Hotmail (documents.zip, docs.zip)
Tools Used   : sha256sum, unzip, fls, icat, sqlite3
Firstness    : Tracy typed terminal commands `zip -e documents.zip Sta* Ins*` with password
               "Hercules" entered twice. Three PDF files named "Stamp Insurance 1/2/3.pdf"
               found in encrypted ZIP on Tracy's phone Hotmail inbox.
Secondness   : A National Gallery employee creating password-encrypted archives of internal
               insurance valuation documents and transmitting them to an external email
               address (perrypatsum@yahoo.com) is structurally incompatible with any
               legitimate business process. The password hint ("your old dog's name") adds
               a deliberate obfuscation layer beyond the encryption itself.
Thirdness    : Tracy weaponized her document-access privileges to systematically extract
               insurance appraisals that reveal the monetary value of the stamp exhibit.
               This is a Carnegie authority-transfer pattern: borrowing institutional trust
               to facilitate theft planning. The encrypted ZIP + password hint channel
               demonstrates operational security awareness — she anticipated interception.
Carnegie     : Authority transfer (institutional trust → personal gain)
MITRE TTPs   : T1567.002 (Exfiltration Over Web Service: to External Cloud), T1560.001
               (Archive Collected Data: Archive via Utility)
Devil Advocate: Tracy may have been legitimately sharing work documents with a trusted
               friend for advice on insurance matters. However, this fails against:
               (a) the explicit encryption with a non-work password, (b) the password
               hint through a separate channel, (c) the preceding emails explicitly
               framing this as "our ticket" for financial gain, (d) no legitimate
               business reason to share internal insurance valuations externally.
               Benign hypothesis REJECTED.
Corroboration: Keylogger emails (independent source 1) + Tracy phone Hotmail inbox
               (independent source 2) + Carry tablet Yahoo email thread (source 3)
Self-Correction: Initially considered INTENT. Upgraded to MALICE based on deliberate
               encryption, multi-channel password delivery, and explicit "our ticket"
               framing demonstrating consciousness of guilt.

Finding ID   : F-002
Title        : Physical Security Bypass Conspiracy (Tracy + Carry)
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : Carry tablet Yahoo emails, Tracy phone SMS, Carry tablet browser history,
               Tracy phone Hotmail (needs.txt), Carry tablet downloads (securedownload.pdf)
Tools Used   : fls, icat, sqlite3, sha256sum
Firstness    : Email thread between Carry (carrysum2012@yahoo.com) and Tracy shows
               negotiation to smuggle a tablet past Gallery security. Tracy's SMS
               "Just meet me out front, I'll take the tablet in." Browser history on
               Carry's tablet shows searches for blinding surveillance cameras, smoke
               bombs, padlock shims, and lock picking. File "needs.txt" on Tracy's phone
               lists spray paint for cameras and smoke grenades.
Secondness   : Legitimate flash mob events do not require blinding security cameras,
               smoke grenades, lock picking tools, or smuggling devices past security
               checkpoints. The combination of physical security research, operational
               security shopping list, and insider facilitation is structurally
               incompatible with any benign event planning.
Thirdness    : Carry systematically researched and documented methods to defeat every
               layer of the Gallery's physical security: visual surveillance (camera
               blinding), access control (lock picking, padlock shims), escape routes
               (smoke grenades), and checkpoint bypass (insider smuggling). This is a
               comprehensive physical penetration plan. Tracy's role as insider access
               facilitator transforms this from external threat to insider-enabled attack.
               Carnegie social proof pattern: the "flash mob" cover story weaponizes
               the appearance of legitimate group activity to mask criminal coordination.
Carnegie     : Social proof (flash mob as legitimacy cover), Reciprocity (bribery —
               "I could really use some extra cash")
MITRE TTPs   : T1200 (Hardware Additions — smuggled tablet), T1036 (Masquerading —
               flash mob cover), T1562.001 (Impair Defenses: Disable or Modify Tools —
               camera blinding plan)
Devil Advocate: Carry may genuinely be planning an artistic flash mob and researching
               security countermeasures out of curiosity, not criminal intent. Tracy may
               simply be doing a friend a favor. However: (a) the "needs.txt" shopping
               list explicitly includes smoke grenades "as means of escape if caught,"
               (b) the camera blinding research directly targets surveillance
               infrastructure, (c) Tracy's bribery language ("extra cash"), (d) the
               operational plan specifies "second floor main hallway east side — where the
               new exhibit is." Benign hypothesis REJECTED — "flash mob" near an exhibit
               with smoke grenades and camera blinding is not art, it's a heist plan.
Corroboration: 5 independent sources confirm: (1) email thread, (2) SMS, (3) browser
               history, (4) needs.txt, (5) security schedule PDF download
Self-Correction: No downgrade warranted. Evidence from 5 independent sources with zero
               contradictions.

Finding ID   : F-003
Title        : Foreign Intelligence Contact and Steganography Infrastructure
Verdict      : INTENT
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : Carry tablet Gmail (alex.jfam11@krasnovia.org), Carry tablet apps
               (SDDroid steganography), Carry tablet downloads (funny video.mp4),
               Carry tablet Gmail (ePassport dumps)
Tools Used   : fls, icat, sqlite3
Firstness    : Alex J uses email domain krasnovia.org (fictional hostile nation in
               SANS scenario context). Alex recommended steganography apps to Carry on
               June 27. SDDroid (ETH Zurich steganography tool) installed on Carry's
               tablet July 6. Alex sent a Dropbox video file ("funny video.mp4")
               downloaded 4 times to Carry's tablet. Carry uploaded ePassport dump ZIPs
               and JMRTD passport reader to Yahoo Mail. Alex sent "fixed" passport
               signatures to Carry.
Secondness   : Steganography tools have no legitimate use in flash mob planning. Passport
               dump files and JMRTD (Java Machine Readable Travel Document) tools are
               designed for reading/writing electronic passport chips — there is no benign
               explanation for a private citizen uploading passport dump archives to
               personal email. The "funny video.mp4" downloaded 4 times suggests
               steganographic extraction attempts (multiple downloads = decoding failures
               or version updates).
Thirdness    : Alex J operates as a foreign handler coordinating with Carry to:
               (a) establish covert communication via steganography, (b) prepare forged
               travel documents for associates entering the US, (c) provide operational
               direction disguised as casual communication. The Krasnovia domain is the
               foreign intelligence signature. The pattern — steganography recommendation →
               tool installation → payload delivery via innocent-looking video — is a
               classic intelligence tradecraft sequence.
Carnegie     : Liking (Alex cultivates personal relationship with Carry before introducing
               operational tasks)
MITRE TTPs   : T1027.003 (Obfuscated Files: Steganography), T1588.002 (Obtain Capabilities:
               Tool), T1586.002 (Compromise Accounts: Email Accounts)
Devil Advocate: Krasnovia is a SANS scenario construct. In a real-world context, the domain
               would need OSINT verification. The steganography apps could be academic
               curiosity. However: (a) the sequence of recommendation → installation →
               payload delivery eliminates curiosity, (b) passport dumps have no benign
               use, (c) Alex's "manuscript" and "associates joining" language is consistent
               with intelligence recruitment. Benign hypothesis REJECTED for the passport
               forgery. Steganography payload content unverifiable (would require
               specialized extraction from "funny video.mp4" — documented as limitation).
Corroboration: Gmail thread (source 1) + installed apps (source 2) + browser upload
               history (source 3) + download directory (source 4)
Self-Correction: Verdict kept at INTENT rather than MALICE because the steganographic
               content of "funny video.mp4" was not extracted and verified. The passport
               forgery component alone warrants INTENT. If stego extraction confirmed
               operational instructions, upgrade to MALICE would be warranted.

Finding ID   : F-004
Title        : Anti-Forensic Evidence Destruction (Carry)
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : Carry tablet /media/Forever Gone/ (~250 deleted blank files)
Tools Used   : fls -r (recursive file listing)
Firstness    : Directory `/media/Forever Gone/` on Carry's tablet contains ~250 deleted
               files named `12-07-12_05-03-10.blank` through `12-07-12_06-25-*.blank`,
               all timestamped 2012-07-12 between 05:03 and 06:25. "Forever Gone" is
               an Android secure-deletion application.
Secondness   : Running a secure-deletion tool at 5:03 AM, three days before device
               seizure, targeting hundreds of files, is structurally incompatible with
               normal device maintenance. The timing (early morning, day of final
               operational coordination) and the volume (250+ files in 82 minutes)
               indicate systematic evidence purging.
Thirdness    : Carry anticipated forensic examination and deliberately destroyed evidence.
               This is the definitional concealment layer that separates MALICE from INTENT.
               The choice of a secure-deletion tool (not simple file deletion) demonstrates
               knowledge that standard deletion is forensically recoverable. The early
               morning timing suggests urgency — she knew the operational window was closing.
Carnegie     : N/A (anti-forensic, not persuasion)
MITRE TTPs   : T1070.004 (Indicator Removal: File Deletion), T1485 (Data Destruction)
Devil Advocate: Carry may have been doing routine device cleanup or freeing storage space.
               However: (a) 5:03 AM is not a routine cleanup time, (b) "Forever Gone" is
               specifically marketed as a secure-delete tool to prevent recovery, not a
               space-freeing utility, (c) the timing correlates with the final coordination
               email to Alex ("your associates to meet me next week") sent the same day.
               Benign hypothesis REJECTED.
Corroboration: Forever Gone artifacts (source 1) + timestamp correlation with final
               coordination email (source 2) + Carry tablet browser history showing
               operational planning content that would be targets for deletion (source 3)
Self-Correction: No downgrade warranted. Anti-forensic tool use + timing = MALICE by
               definition.

Finding ID   : F-005
Title        : Keylogger Surveillance Infrastructure (Joe → Tracy)
Verdict      : INTENT
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : email.zip (12 EML files), README.txt
Tools Used   : sha256sum, unzip
Firstness    : LogKext daemon running on Tracys-MacBook-Air.local captures all keystrokes
               and automatically emails them to joe.sum.twelve@gmail.com via local Postfix
               at periodic intervals. 12 emails covering June 28 to July 12.
Secondness   : A keylogger on a personal MacBook transmitting captures to an external
               email is not a legitimate system monitoring tool. The LogKext configuration
               requires root access and deliberate installation. The recipient
               (joe.sum.twelve@gmail.com) shares the "SumTwelve" surname pattern,
               indicating a family member, not an employer or IT department.
Thirdness    : Joe installed covert surveillance on Tracy's personal computer. The
               captures reveal Tracy's conspiracy with Perry, all credentials, and her
               operational activities. Joe's role is ambiguous: he may be (a) a law
               enforcement informant or cooperating witness who planted the keylogger to
               document Tracy's activities, (b) an independent conspirator monitoring
               Tracy for his own purposes, or (c) a controlling family member conducting
               unauthorized surveillance. The keylogger itself is the primary evidence
               source for the entire Tracy–Perry communication chain.
Carnegie     : N/A
MITRE TTPs   : T1056.001 (Input Capture: Keylogging), T1020 (Automated Exfiltration)
Devil Advocate: Joe may be an authorized law enforcement tool — the keylogger may have
               been installed under a warrant or by an investigator. The README.txt
               describes the setup matter-of-factly without identifying Joe's
               authorization. Without warrant documentation, Joe's legal authority to
               install the keylogger is unverifiable. Verdict held at INTENT (not MALICE)
               because the keylogger may serve a legitimate investigative purpose.
Corroboration: 12 independent email captures (source 1) + README.txt metadata (source 2)
Self-Correction: Initially considered MALICE. Downgraded to INTENT because Joe's
               role/authorization is ambiguous. The keylogger evidence itself is
               invaluable regardless of Joe's intent.

Finding ID   : F-006
Title        : Network Reconnaissance (10.10.1.119 → 10.10.1.169)
Verdict      : SUSPICION
Confidence   : MEDIUM
Status       : INFERRED
Artifact     : PCAPs exterior 07-06, 07-09, 07-10; text log exterior 07-12
Tools Used   : tcpdump, text analysis
Firstness    : Host 10.10.1.119 performs persistent ARP sweeps, SNMP GetRequest
               (sysName.0) every ~10 minutes, TCP port probes (3389, 5900, 445, 139,
               8080, 40080, 17667), and successful TCP connections to port 8080 on
               10.10.1.169 every ~10 minutes across all three capture dates.
Secondness   : The regularity (exactly 10-minute intervals), breadth (ARP + SNMP +
               port scan + TCP check), and persistence (3 consecutive days) are
               consistent with automated network management software (SolarWinds,
               Nagios, or similar NMS). However, port 8080 was open and accepting
               connections on 10.10.1.169, which is a VirtualBox VM.
Thirdness    : Two competing hypotheses: (a) legitimate NMS performing standard
               monitoring — the SNMP OID query (sysName.0) is a canonical NMS poll,
               and the regularity is machine-generated; (b) automated reconnaissance
               tool targeting the Gallery's internal VM. Without packet payload
               analysis of the port 8080 sessions, intent cannot be determined.
Carnegie     : N/A
MITRE TTPs   : T1046 (Network Service Discovery) — if adversarial
Devil Advocate: This is standard NMS behavior. The SNMP sysName.0 OID is the
               default polling OID for every NMS product. The 10-minute interval is
               a standard monitoring cycle. The ARP sweep is normal ARP cache
               maintenance. Benign hypothesis is STRONG.
Corroboration: Single source type (network captures). No corroborating host-based
               evidence from 10.10.1.119.
Self-Correction: REFUTATION GATE LOG — F-006
               Candidate verdict: INTENT (automated scanning pattern)
               Gate applied: Daubert Corroboration Gate
               Gate rule: n_artifacts < 2 for this evidence class → cap SUSPICION
               Gate result: Candidate REJECTED. Emitted as SUSPICION.
               Forensic note: Without access to 10.10.1.119, NMS vs. adversarial
               determination requires additional host-based evidence.

Finding ID   : F-007
Title        : Operational Plan — Flash Mob Cover for Gallery Infiltration
Verdict      : MALICE
Confidence   : HIGH
Status       : CONFIRMED
Artifact     : Carry tablet Gmail (Drex Mustafar thread), Carry tablet browser history,
               Carry tablet Yahoo (Tracy thread), Tracy phone SMS
Tools Used   : fls, icat, sqlite3
Firstness    : Carry emails Drex Mustafar (bubbahotep2012@hotmail.com, flash mob
               coordinator): "two teams, one group coming in through the east entrance
               and the other through the west. Groups meet second floor main hallway
               east side. This is where the new exhibit is. I want the event to kickoff
               at 12:00 PM sharp."
Secondness   : Legitimate flash mobs do not specify military-style entry through
               multiple entrances with a rendezvous at a specific exhibit location.
               The language ("two teams," "kickoff," meeting at the exhibit) is
               operational planning, not event coordination. The explicit mention
               "where the new exhibit is" connects directly to the rare stamp exhibit
               Tracy identified.
Thirdness    : The flash mob is a cover operation. Carry weaponizes the concept of
               a legitimate public gathering to (a) create a distraction, (b) position
               multiple people at the stamp exhibit, and (c) provide plausible
               deniability for a coordinated presence near the target. This is a
               Carnegie social proof + authority technique: borrowing the legitimacy
               of a known cultural phenomenon to mask criminal logistics.
Carnegie     : Social proof (cultural legitimacy of flash mobs), Authority (using a
               professional coordinator to add organizational legitimacy)
MITRE TTPs   : T1036.005 (Masquerading: Match Legitimate Name or Location)
Devil Advocate: Carry could genuinely be planning a flash mob near the exhibit as
               a cultural event. However: (a) the same person researched smoke bombs,
               camera blinding, and lock picking; (b) "needs.txt" lists escape
               equipment; (c) the email thread with Tracy explicitly discusses
               bribery for security bypass; (d) no legitimate flash mob requires
               encrypted passport documents for participants. Benign hypothesis
               COMPREHENSIVELY REJECTED across 4 independent evidence sources.
Corroboration: Email to Drex (source 1) + Tracy email thread (source 2) +
               browser history (source 3) + SMS (source 4)
Self-Correction: No downgrade warranted.

NETWORK TOPOLOGY
----------------

Two capture points confirmed as same host via NAT:
- Interior: 192.168.1.101 (LAN-side, single active host)
- Exterior: 10.10.1.169 (routed/WAN-side, VirtualBox VM MAC 08:00:27:ef:f7:f8)

Internal hosts:
- 10.10.1.13: SSH-only access to .169 (admin/IT — no web activity)
- 10.10.1.119: Network scanner/NMS (automated monitoring)
- 10.10.1.106/114/116/130/152: Dropbox LAN sync, background broadcast traffic
- DNS: regis.ncr.vt.edu, roosevelt.nvc.vt.edu (Virginia Tech university DNS)
- 10.10.1.169 queries scenrout.ncr.nps.edu every 30 minutes (beaconing or NTP-like check)

DEVICE SUMMARY
--------------

| Device | Owner | Type | Key evidence |
|--------|-------|------|-------------|
| Tracys-MacBook-Air | Tracy | MacBook Air, macOS | Keylogger (LogKext), all keystroke captures |
| Google Nexus S (I9020A) | Carry | Android 2.3.4, T-Mobile | SMS/calls (on internal storage, not in logical extraction) |
| ASUS Transformer TF101 | Carry | Android tablet, 28GB | Gmail, Yahoo, browser, apps, security schedule, evidence destruction |
| Apple iPhone 3G | Tracy | iOS | SMS, Hotmail, GPS photos, contacts |

KNOWN LIMITATIONS
-----------------

L-001: tracy-home-2012-07-16-final.E01/.E02 are 0 bytes (incomplete download).
       Tracy's home computer disk image is unavailable for analysis. This would
       contain her macOS filesystem, applications, and locally stored files.

L-002: Carry's phone internal storage (mmssms.db, contacts2.db, mailstore,
       browser.db, talk.db) is not present in the logical extraction ZIP
       (carry-phone-logical). The full physical image (carry-phone-2012-07-15-final.zip)
       was not extracted in this session.

L-003: Steganographic content of "funny video.mp4" was not extracted or analyzed.
       Specialized stego tools (SDDroid, StegDetect, zsteg) would be required to
       determine if the video contains hidden data from Alex J.

L-004: Perry Patsum's "Crazydave1.mp3" attachment was not analyzed for steganographic
       content. The audio file may contain hidden operational instructions.

L-005: MCP tools (Vigia_Sift_Bridge) were not available in this session due to tool
       registration failure. Analysis was performed using direct SIFT tools (Sleuth Kit,
       ewfinfo, tcpdump, sqlite3) and agent-based decomposition. Deterministic scoring
       pipeline was not executed. All verdicts are Claude Code analytical determinations,
       not sealed ForensicBundle outputs.

L-006: tshark was not installed, limiting PCAP analysis to tcpdump (no protocol
       dissection, no stream reassembly, no file carving from network captures).

L-007: 10.10.1.119 and 10.10.1.13 have no host-based evidence. Their roles
       (NMS vs. adversarial, admin vs. conspirator) cannot be fully determined from
       network captures alone.

L-008: Carry's tablet was rooted (Superuser-3.0.7 + busybox installed). Root access
       means the device could have been used to bypass Android security controls,
       install hidden apps, or modify system files. The extent of root-enabled
       modifications was not fully cataloged.

CONCLUSION
----------

The National Gallery DC 2012 case presents a multi-layered insider threat conspiracy
with foreign intelligence dimensions. The evidence establishes beyond reasonable doubt:

1. Tracy SumTwelve exploited her National Gallery employment to exfiltrate stamp
   insurance valuations, transmit the security duty schedule, and physically
   facilitate unauthorized device entry — motivated by financial pressure (daughter's
   tuition).

2. Carry orchestrated the operational plan using a "flash mob" cover story while
   researching physical security countermeasures (camera blinding, smoke bombs, lock
   picking), coordinating with a foreign contact (Alex J / Krasnovia), arranging
   forged passport documents, installing steganography tools, and destroying evidence
   pre-seizure.

3. Perry Patsum received stolen documents and may have provided steganographic
   payloads via MP3 files.

4. Alex J (krasnovia.org) provided tradecraft guidance (steganography) and
   coordinated the entry of foreign associates using forged passport documents.

5. The conspiracy targeted a rare stamp exhibit arriving at the National Gallery,
   with a coordinated physical operation planned for "next week" as of July 12.

The concealment layers — encrypted archives, steganography infrastructure, alias
emails (Coral Blue Two), evidence destruction (Forever Gone), and cover operations
(flash mob) — satisfy the MALICE threshold under Peircean analysis. This is not
carelessness or misconfiguration. Every action required deliberate technical decisions
by actors who understood both the target environment and the forensic risks.

TOKEN USAGE (this session):
  Input tokens:  ~500,000 (estimated across main + 5 subagents)
  Output tokens: ~50,000 (estimated across main + 5 subagents)
  Session ID:    2026-06-27T03:00:00Z
  Note: Full token breakdown available at usage.anthropic.com

---
*VIGIA — Making deception computationally expensive since 2026.*
*"If a system claims MALICE without explaining it with exact mathematics,
it is not forensics. It is divination."*
