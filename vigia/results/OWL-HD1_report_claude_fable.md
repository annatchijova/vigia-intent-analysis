# VIGIA FORENSIC INTENT ANALYSIS REPORT

```
Case ID      : VIGIA-OWL-2019-HD1  (Project OWL — companion computer)
Investigator : VIGIA Autonomous Agent (Claude Code / Claude Fable, Mode 2)
Evidence     : HD1.E01 (extracted from owl.zip) — HP computer, Windows
Device HW    : Toshiba MQ01ACF050 500GB, serial 16OGCPA5T (per HD1.source_info)
Subject      : Sarah McAvoy (mcavoys87@gmail.com) — SAME subject as OWL-NEXUS5
Mode         : Claude Code (Mode 2), canonical-v2 sealed decision payload
E01 SHA-256  : f3174609fc4bf912824103b2f164922461b9549aa03c4fca8a57b837840cb9cb
Seal         : da4e0867af69d1038d4aa352d18495cf817b5b43d48f3b0f90beb6047ee967e8 (determinism PASS x3)
Tool log     : chain v2 VERIFIED (7 entries, tail anchor OK)
```

## EXECUTIVE SUMMARY

HD1 is the **companion computer** (an HP machine) belonging to **Sarah McAvoy** —
the same subject as the OWL-NEXUS5 phone. Its `Sarah M` profile carries deliberate
**owl-purchase research and acquisition materials**: browsing of specific owl
for-sale listings on `birdtrader.co.uk` (the same marketplace referenced on the
phone), snowy-owl-egg vendors, craigslist owl searches, downloaded owl husbandry
and emergency-care manuals, and a snowy-owl bibliography. Pidgin (account
`mcavoys87@gmail.com`, the subject's identity) ran seven times with automatic chat
logging enabled, yet no conversation logs are present. Six owl images and PDFs were
deleted to the Recycle Bin.

**Emitted verdict: INTENT.** This device supplies the **independent second source**
whose absence had capped OWL-NEXUS5 at SUSPICION under doctrine L-051. Two
independent devices belonging to the same subject, showing the same deliberate
owl-trade preparation, satisfy the two-source corroboration bar; the OWL case as a
whole is graded **INTENT**. **MALICE is not reached**: no completed-payment record
exists, the file deletions are recoverable soft-deletes (not secure erasure), and
the absence of Pidgin logs cannot be proven to be deletion rather than
"launched-but-never-chatted".

## FINDINGS

| ID | Title | Verdict | Conf. | Status |
|----|-------|---------|-------|--------|
| F-001 | Owl-purchase research + acquisition materials (Chrome, Downloads, Desktop) | INTENT | HIGH | CONFIRMED |
| F-002 | Same-subject Pidgin channel; logging enabled but logs absent | SUSPICION | MEDIUM | INFERRED |
| F-003 | Six owl files deleted to Recycle Bin (recoverable) | SUSPICION | MEDIUM | CONFIRMED |
| F-004 | Cross-device corroboration lifts the OWL single-device ceiling | INTENT | HIGH | CONFIRMED |

### F-001 detail — the owl-purchase trail

Chrome history (user Sarah M): `birdtrader.co.uk` specific owl listings
(`breeding-pair-ashy-faced/557508`, `dark-breasted-barn-owls/557507`,
snowy-owl searches), `21food.com` fertile-snowy-owl-eggs-for-sale, craigslist
owls, followed immediately by a Gmail message. Downloads: `Owl_Emergency_Care.pdf`,
`Owl_Keeping.pdf`, `Bibliography - Snowy Owl ... GLOW posting.xls`,
`Sightings2005.xls`. Desktop: saved owl web pages.

### F-002 detail — Pidgin

Ran 7 times (prefetch run_count 7) from a portable location
(`...\AppData\Roaming\Microsoft\Windows\Pidgin`, not Program Files). `accounts.xml`
= one account, `mcavoys87@gmail.com` (prpl-msn). `prefs.xml` has logging enabled
(`log_ims=1`, `log_chats=1`, `log='automatic'`). No `.purple\logs` directory exists;
`blist.xml` is empty. Records are **not recoverable**; whether this reflects
deletion or no completed conversation cannot be resolved from this artifact alone.

### F-003 detail — deleted owl files

Recovered from Recycle Bin (`...-1002`): `Snowy_Owl.pdf`, `Great Horned Owl Info.pdf`,
`Great Horned Owl.jpg`, `Pygmy Owl.jpg`, `Luna Owl.jpg`, `Next pet.jpg`. `$R`
contents present and preserved.

## MANDATORY REFUTATION (Eco's razor)

**Benign hypothesis:** an owl enthusiast/student researching owls, who later changed
their mind and deleted the files. **Test:** a hobby or report does not explain
browsing a live exotic-bird **marketplace** for specific for-sale listings, in
combination with the phone-side negotiation with a named seller (`layster82`) and a
naming convention like `Next pet.jpg`/`Luna Owl.jpg`. The benign reading fails for
the *acquisition* posture. It is **not** refuted, however, for the questions of
completed payment or aggravated destruction — which is why the grade is INTENT, not
MALICE.

## CROSS-DEVICE CORROBORATION (F-004)

The OWL-NEXUS5 phone was capped at SUSPICION under L-051 for want of an independent
second source; the amicus for that case explicitly recommended imaging this
companion computer. HD1 is that source: same subject, same owl marketplace, same
acquisition intent, on a different device. This is the triangulation that lifts the
single-device ceiling.

## MITRE ATT&CK

T1592 (Gather Victim Host Information — target research), T1071.001 (web channel),
T1070 / T1070.004 (Indicator Removal — Recycle Bin deletions; Pidgin logs absent).

## KNOWN LIMITATIONS

- **No completed transaction proven.** No payment or delivery record recovered on
  HD1; the owl-purchase *confirmation* expected "through pidgin" is not present as a
  saved log.
- **Pidgin log absence is ambiguous** (deletion vs never-logged) — reported as
  records-not-recoverable, rated SUSPICION.
- **Recycle-bin deletions are recoverable** soft-deletes, not secure erasure — they
  do not support MALICE.
- **Evidence freed after sealing.** HD1.E01 (68 GB) and owl.zip (65 GB) are deleted
  after this seal; decisive artifacts are preserved under
  `evidence/owl-2019-hd1-windows/` (chrome_history.sqlite, prefetch/, registry,
  evtx, and `hd1_preserved_claude_fable/` with the owl docs, `.purple` config, and
  recovered Recycle-bin `$I`/`$R` files). The E01 SHA-256 above anchors custody.
- **Determinism:** decision payload sealed with canonical v2 + SHA-256; identical
  across 3 seals (repeat + key-reorder). No float in the sealed path; no LLM in the
  seal.

## TOKEN USAGE (this session)

```
Deterministic seal (hashing, prefetch parse, canonical seal, verification): 0 tokens.
Exact input/output token counts: usage.anthropic.com.
```
