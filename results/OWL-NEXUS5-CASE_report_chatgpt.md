# VIGÍA Forensic Intent Analysis Report — OWL-NEXUS5-CASE (ChatGPT)

**Case ID:** `VIGIA-OWL-2019-NEXUS5`  
**Investigator:** ChatGPT / Codex local forensic review  
**Date:** 2026-07-21  
**Mode:** Local, deterministic and manual review; no VIGÍA MCP tool was exposed in this session.  
**Scope:** Read-only review of the original Nexus 5 image, an existing read-only `/data` mount, extracted Chrome/Musical.ly material, and the signed case definition. No original evidence was mounted, altered, copied, or written to.

## Executive conclusion

**Verdict: SUSPICION — CONFIRMED BY INDUCTION.**

The original Nexus 5 image directly contains: (1) repeated browsing of owl-sale listings, including specific Birdtrader advertisements; (2) Musical.ly identities linking `sarahmcavoy` and `layster82` / Layla Aster; and (3) messages discussing an image of an exact animal, contact details, and a possible meeting. This supports a deliberate attempt to evaluate and coordinate around a particular owl.

It does **not** establish that the phone operator was a particular physical person, that a transaction completed, that money or an animal changed hands, or that any conduct was unlawful in the relevant jurisdiction. No companion device, payment record, permit record, delivery record, counterparty acquisition, or external corroboration was in scope. The evidence therefore does not support `INTENT` or `MALICE` under the stated doctrine.

The signed case definition independently states the same ceiling: one device/channel without independent triangulation is capped at `SUSPICION`.

## Threat model and boundaries

- An examiner may read the supplied original image and the already-mounted read-only partition.
- The examiner may write only derived outputs under `results/`.
- The examiner cannot treat duplicated strings in one disk image as independent corroboration.
- The examiner cannot infer a completed or illegal wildlife transaction from interest, messages, or installed applications alone.
- The cryptographic seals below attest bytes and process linkage. They do **not** prove that the sealed conclusion is factually correct.

## Chain of custody anchors

| Object | Observed value | Result |
|---|---|---|
| Original full image | `LGE Nexus 5 Full Image.raw`, 31,268,536,320 bytes | Read only |
| Original image MD5 | `b334843a07a9e16494eebdf3079e6bc6` | Matches Magnet metadata |
| Original image SHA-1 | `f46ee05ce1a2210501ea512ed9e4c7ec59222cca` | Matches Magnet metadata |
| Original image SHA-256 | `763e7acde388519940f351bc3c6cc1747ed4f99423ad6c892745553804b6a5de` | New session anchor |
| Worktree image inode | `30432824` | Matches the original Downloads image inode |
| `data/cases/OWL-NEXUS5-CASE.json` SHA-256 | `7710fe9254f51496a1165cfb68b0d3c94e36d0b56193defc6618a822d61185ce` | Authoritative signed definition used |
| `cases/OWL-NEXUS5-CASE.json` SHA-256 | `4ba85cb2ea8ce555cdb8a4cf51ff5c9d93a751aa733cac870816733059ac16c6` | Not identical; reduced copy, not used as authority |
| Quick logical extraction ZIP SHA-256 | `d649936ca48074fb177f51c6e2e7231d43331c4112e9e29f2a389a80b0fe15b1` | Anchored; not relied upon for owl-trade findings |
| `activity_log.txt` MD5 | `a119658b11f4833fbe6d17dbfd6a6b43` | Matches `image_info.txt` |

The full-image MD5 and SHA-1 were recomputed against the original bytes and match the Magnet ACQUIRE values in `image_info.txt`.

## Directly observed evidence

| ID | Artifact / hash | Observation | Epistemic level |
|---|---|---|---|
| E-01 | `accounts.db` — `42ab39e2…1dbbc` | Accounts include `mcavoys87@gmail.com`, `SarahMcavoy`, `sarahmcavoy`, Skype and Twitter identities. | CODE FACT |
| E-02 | `recent_tasks/95_task.xml` — `e8754b71…59b5` | Google Search task records `Tina and password`. | CODE FACT |
| E-03 | Chrome `History` — `7bde33e0…b5136` | Chrome records repeated visits on 2017-01-25 to owl-sale pages, including Birdtrader ads 557493, 558006 and 557933, plus exotic-animal and owl-pet pages. | CODE FACT |
| E-04 | Chrome `History` — `7bde33e0…b5136` | Search terms and URLs record `owls`, `snowy owl`, and image/search activity. | CODE FACT |
| E-05 | `musically.db` — `04772f57…5c7e` | `T_DIRECT_USER` records `sarahmcavoy` and `layster82`; `T_DIRECT_USER_RELATIONSHIP` names Layla Aster and links those user IDs. | CODE FACT |
| E-06 | Original image — `763e7acd…a5de` | Raw-image strings at offset `2868273424` contain Sarah's question asking whether an image is of the exact animal; adjacent records contain Layla's “How do you like him”, an image URL, and `Layster82gmail`. | CODE FACT |
| E-07 | Original image — `763e7acd…a5de` | The same raw-image region contains Sarah's message about deleted email correspondence and asking to continue information “through here”, followed by “OK could you meet me at Harris river front park?”. | CODE FACT |
| E-08 | Original image — `763e7acd…a5de` | Similar message objects recur around offset `19082080528`. They are duplicate material in one image, not an independent source. | CODE FACT |
| E-09 | `recent_tasks/105_task.xml` — `756999bc…46e1` | Task is a Chrome search for “Green sea turtle”; it is not owl-sale evidence. | CODE FACT |
| E-10 | `SYSTEM_BOOT` / `event_log` — `55b0de61…d627` / `4e89f4b9…ba20` | Nexus 5 build/boot information and a Skype ANR are present. | CODE FACT |

## Peircean reasoning

### Firstness — what was observed

The image contains specific owl-marketplace URLs, account/relationship records for the two Musical.ly identities, and chat JSON referring to an image, an “exact one”, email contact, and a meeting location. The records are recoverable from the original image and relevant application databases.

### Secondness — structural relation to the claimed context

Casual owl interest can explain generic owl searches, image browsing, and even animal-care research. It does not by itself explain the combined sequence of repeated visits to specific sale listings, a direct relationship to a named counterparty, an image described as “him”, a request to determine whether it is the exact animal, and a follow-up proposal to meet.

Conversely, the data does not contain a payment, transfer, receipt, delivery, ownership, species certification, permit, or counterpart-device record. The same device and application channel provide context, but not independent corroboration.

### Thirdness — bounded inference

The most economical explanation is an intentional effort by the operator of the relevant application identities to evaluate and coordinate around a particular owl. That inference supports **suspicion of a prospective transaction**, not a completed transaction, a named person's physical agency, or a legal conclusion.

## Mandatory refutation gate

| Rival hypothesis | Prediction if true | Observation | Result |
|---|---|---|---|
| Ordinary owl fandom / fictional interest | Generic searches and images may occur; sale-listing research and a concrete “exact one” conversation need not occur together. | Specific marketplace listings and direct image/meeting exchange are present. | **Partially refuted** as a complete explanation; it still explains some searches. |
| Legal private purchase or animal-related conversation | The same records could occur without criminal conduct. | No jurisdiction, species status, permit, payment, or transfer record was found. | **Not refuted.** A legal conclusion is unavailable. |
| Another person operated the device/account | Device artifacts may not identify the physical operator. | Accounts and app relationship bind the activity to device identities, not to a verified person at the keyboard. | **Not refuted.** Physical attribution remains open. |
| Completed purchase / delivery | Payment, receipt, logistics, counterpart evidence, or possession should exist. | None was established in the reviewed source set. | **Not corroborated.** Do not infer completion. |
| Deliberate anti-forensics | Reliable evidence should show execution/configuration or independent tampering indicators. | App packages exist, but no reviewed configuration/log proves AppLock use, a wipe, or concealment by the user. | **Falsified as a conclusion from current scope.** |

## Acquisition and anti-forensics cautions

`image_info.txt` identifies Magnet ACQUIRE 2.0.0.5412. Its activity log states that, during acquisition, the tool pushed BusyBox to a temporary device path, made `/system` read-write, installed BusyBox under `/system/xbin/`, streamed data, and deleted the temporary BusyBox afterwards.

Therefore:

- Installed AppLock/CM Locker package directories are **presence observations**, not proof that the owner used them to conceal evidence.
- Root-related application/package artifacts are not sufficient to attribute root activity or anti-forensic motive to the user.
- The image was unencrypted at acquisition. That is a state observation, not evidence that encryption was disabled to facilitate wiping.
- `/system`-side residues require special caution because the acquisition workflow itself modified that partition.

## Deterministic bundle: integrity versus semantic adequacy

Generated artifacts:

- `results/OWL-NEXUS5-CASE_bundle_chatgpt.json`
- `results/OWL-NEXUS5-CASE_bundle_chatgpt.json.sha256`
- `results/OWL-NEXUS5-CASE_bundle_chatgpt_reasoning_trace.json`

**Seal check:** `sha256sum -c` passed.  
**Trace check:** `verify_reasoning_trace(bundle, trace)` returned `valid=True`.

However, the sealed deterministic run emitted `NOISE`. This is not adopted as the forensic conclusion. The run is a **confirmed semantic false-negative on the legacy JSON route**:

1. Prediction: a route that represents twenty case artifacts containing direct message and browser evidence should not silently treat all evidence as clean.
2. Observation: the run logged 20 primary signals all labelled `unknown`, each with `z_score=0`, then emitted `NO_SEMIOTIC_ANOMALY_DETECTED` / `NOISE`.
3. Consequence: the bundle truthfully seals that pipeline output, but the output does not faithfully represent the directly inspected raw-image evidence.

This is a pipeline/input-adaptation finding, **not** a broken SHA-256 seal and not a claim that the sealed bytes were manipulated. No post-seal mutation was made.

The run also warned that no persistent `VIGIA_HMAC_KEY` was configured, so its audit logging used an ephemeral key. The file hash and trace chain verified in this session; persistent keyed verification is a documented limitation of this run.

## Audit trail of this review

1. Created branch `chatgpt-codex` without replacing pre-existing OWL outputs.
2. Hashed both case-definition files; detected they differ and selected `data/cases/` because it includes the signed doctrine and expected verdict.
3. Recomputed original image SHA-256, SHA-1, and MD5; SHA-1/MD5 match Magnet metadata.
4. Confirmed the worktree image and Downloads original share inode `30432824`.
5. Verified artifact existence in the pre-existing read-only `/data` mount; resolved Android logical `/data/...` paths against the mount root.
6. Hashed every directly opened file/database before querying it.
7. Queried SQLite databases with `sqlite3 -readonly`; inspected XML/log artifacts read-only.
8. Hashed Chrome/Musical.ly databases before query and the original image before raw-string search.
9. Searched the already-hashed original image for the exact message phrases and recorded offsets; duplicate occurrences were not promoted to independent corroboration.
10. Ran `vigia_agent.py` only against the signed case JSON, outputting solely under `results/`; verified its bundle and trace after creation.

## What would change the conclusion

Any of the following could discriminate between the remaining explanations:

- the HP companion device or other independently acquired counterparty evidence;
- payment, transfer, delivery, or possession records;
- preservation/metadata for the sent image and associated server-side records;
- jurisdiction-, species-, and permit-specific evidence;
- an independently attributable operator timeline for the device/accounts.

## Final limitation statement

This report concerns evidentiary interpretation of a supplied forensic training/scenario corpus. It is not a legal opinion, does not establish criminality, and must not be used to identify or accuse a real person without independent, lawfully acquired corroboration and qualified human review.
