# VIGIA FORENSIC INTENT ANALYSIS REPORT — OWL (COMPLETE)

```
Case ID      : VIGIA-OWL-2019-COMPLETE  (Project OWL — two devices)
Corpus file  : data/cases/VIGIA-OWL-2019-COMPLETE.json (30 artifacts, schema validates)
Investigator : VIGIA Autonomous Agent (Claude Code / Claude Fable, Mode 2)
Subject      : Sarah McAvoy (mcavoys87@gmail.com)
Devices      : LGE Nexus 5 (phone) + HD1 HP companion computer
Mode         : deterministic EBS pipeline (VigiaPipeline.run_full); no LLM in the seal
Nexus5 raw   : (deleted; sealed as OWL-NEXUS5) — Magnet ACQUIRE MD1
HD1 E01 SHA  : f3174609fc4bf912824103b2f164922461b9549aa03c4fca8a57b837840cb9cb
Decision hash: 617cd69ca65d531ecd8deea4... (stable x3)
EBS verify   : PASS — Level 2 (Cryptographically valid), 10/11 (R5 ECL is Level-3-only)
Combined LR  : 485,165,195 (ENFSI "very strong"); decision REJECT, posterior 1.0
```

## EXECUTIVE SUMMARY

This is the consolidated Project OWL case, combining both of subject **Sarah
McAvoy**'s devices into a single corpus entry of **30 artifacts**. The **Nexus 5**
carries the negotiation with a known owl seller (`layster82`) over Musical.ly with
app compartmentalization; the **HD1 HP companion computer** carries owl-purchase
research on `birdtrader.co.uk` (the same marketplace), owl husbandry materials,
Pidgin under the same account, and deleted owl files.

**Emitted verdict: INTENT.** The deterministic EBS pipeline scores the combined
evidence as REJECT / posterior 1.0 / LR ~4.85e8 ("very strong"). Because two
**independent devices** belonging to the same subject show the same deliberate
owl-trade preparation, the two-source corroboration bar is met and the L-051
single-device ceiling — which had capped the phone-only case at SUSPICION — no
longer applies. **MALICE is not reached**: no completed transaction or payment
record exists on either device, and the HD1 deletions are recoverable soft-deletes.

## COMPOSITION (30 artifacts)

- **Nexus 5 (22 artifacts):** account registrations (Google/Musical.ly/Skype/
  Twitter), owl-purchase web searches, Musical.ly negotiation with layster82
  (image exchange, identity verification), AppLock installation, and the two
  coordination SMS.
- **HD1 companion (8 artifacts, ART-101..ART-108):** same-account Pidgin
  registration; birdtrader.co.uk owl for-sale browsing (specific listings
  557508/557507) and snowy-owl-egg vendors; owl husbandry/emergency PDFs and a
  snowy-owl bibliography; Pidgin portable install; Pidgin prefetch (run_count 7);
  logging-enabled-but-logs-absent system event; six owl files deleted to the
  Recycle Bin.

## PEIRCEAN THIRDNESS (combined)

Across two of the subject's own devices, the same deliberate owl-trade preparation
appears — negotiation with a known seller on the phone, marketplace browsing and
acquisition materials on the computer, both under one identity. Two independent
devices for the same subject and objective establish deliberate, premeditated
participation in illegal wildlife trade (INTENT).

## REFUTATION (Eco's razor)

The benign "owl hobby across two devices" reading fails: a hobby does not include
negotiating with a named seller on one device while browsing a live sales
marketplace on the other. It is **not** refuted, however, for completion — no paid
transaction is proven — which is exactly why the grade is INTENT, not MALICE.

## VERIFICATION ("nothing missing")

- `validate_case_schema(normalize_case_schema(case))` → OK (30 artifacts).
- Deterministic seal: `decision_hash` identical across 3 runs.
- `verify_ebs_v1.py` → PASS, **Level 2 (Cryptographically valid)**, 10/11 checks.
  The single non-OK is **R5_ECL_BINDING (WARN)**: `ecl_hash` absent — an optional
  **Level-3** Evidence-Chain-Ledger anchor that requires the persistent chain DB
  (`VIGIA_CHAIN_DB_PATH`). It is a WARN, not a failure, and is identical across all
  four sealed OWL/ROCBA/JESS bundles this session. Nothing is missing from the case
  itself.

## MITRE ATT&CK

T1074.001, T1530, T1567.002 (staging/exfil, phone), T1592 (target research, HD1),
T1071.001 (messaging channels), T1070.004 (Recycle-bin deletions).

## RELATION TO THE PER-DEVICE SEALS

This combined entry does not replace the per-device bundles; all are preserved:
`OWL-NEXUS5_bundle_claude_fable.json` (phone, SUSPICION under L-051) and
`OWL-HD1_bundle_claude_fable.json` (computer, INTENT). The COMPLETE case is the
corpus-level fusion that records why the OWL matter as a whole is INTENT.

## KNOWN LIMITATIONS

- No completed transaction / payment proven on either device.
- HD1 Pidgin logs absent (deletion vs never-logged unresolved); deletions
  recoverable.
- HD1 raw image freed after sealing; decisive artifacts preserved under
  `evidence/owl-2019-hd1-windows/`. E01 SHA-256 anchors custody.
- `bundle_hash` varies per seal (random id + timestamp); `decision_hash` is the
  reproducible anchor.
```
TOKEN USAGE (this session): deterministic seal used 0 tokens; see usage.anthropic.com.
```
