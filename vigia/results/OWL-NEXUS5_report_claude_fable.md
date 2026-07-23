# VIGIA FORENSIC INTENT ANALYSIS REPORT

```
Case ID      : VIGIA-OWL-2019-NEXUS5  (Project OWL — Illegal Owl Trade)
Investigator : VIGIA Autonomous Agent (Claude Code / Claude Fable, Mode 2)
Evidence     : LGE Nexus 5 Full Image.raw (Android 6.0.1, hammerhead, rooted)
Subject      : Sarah McAvoy (mcavoys87@gmail.com; Musical.ly "sarahmcavoy")
Counterparty : Layla Aster (Musical.ly "layster82"; Layster82@gmail.com)
Mode         : Claude Code (Mode 2), deterministic EBS pipeline (no LLM in seal)
Raw SHA-256  : 763e7acde388519940f351bc3c6cc1747ed4f99423ad6c892745553804b6a5de
Acquisition  : Magnet ACQUIRE v2.0.0.5412; MD1; MD5 B334843A..6BC6 / SHA1 F46EE05C..2CCA
Timestamp    : 2026-07-23T02:16Z
Decision hash: 1fc5282832ebba458857717f938fa8b95de918edf45c3d0802dc71ce225264e3 (stable x3)
EBS verify   : PASS — Level 2 (Cryptographically valid), 10/11 checks
```

## EXECUTIVE SUMMARY

The Nexus 5 belonging to **Sarah McAvoy** contains a coherent constellation of
artifacts evidencing **deliberate participation in the illegal trade of a
protected owl**: owl-care research and browsing of specific owl-for-sale listings
on `birdtrader.co.uk`, a negotiation with a known seller (`layster82`) conducted
on Musical.ly, image exchange and identity verification of the specific animal,
and deployment of CM Security AppLock to shield the messaging apps.

**Emitted verdict: SUSPICION.** The deterministic EBS decision pipeline scores the
intentionality hypothesis as statistically **very strong** (likelihood ratio
~4.85e8, ENFSI "very strong", decision REJECT of the benign null, posterior 1.0),
but the human-facing verdict is **capped at SUSPICION by doctrine L-051 / §9.4-LIM**:
a single device and single channel, with no independent triangulation, cannot reach
MALICE. The purchase-confirmation record lives on a companion device (HP laptop)
not present in this acquisition. The CAIE structural layer independently returns
**NOISE** (composite 0.0586, 0 cross-artifact fractures at its threshold). All
three readings are preserved below; none silently overrides another.

## SUBJECT / DEVICE

- Device: LGE Nexus 5 (hammerhead), Android 6.0.1 build M4B30Z, **rooted** (TWRP +
  SuperSU 2.79), **unencrypted**, serial `08ebf545d00af782`, first boot
  2017-02-06T19:53:18Z.
- Subject accounts: Google `mcavoys87@gmail.com`, Musical.ly `sarahmcavoy`
  (uid 190719500932296704), Skype/Twitter `mcavoys87`, phone 1(304)638-8446.

## FINDINGS (22 artifacts / 22 signals)

| Class | Count | Role |
|-------|-------|------|
| account_registration | 4 | Identity linkage across Google/Musical.ly/Skype/Twitter |
| web_search | 5 | Owl-care and owl-purchase research (intent formation) |
| social_media_search | 1 | Locating the seller |
| instant_message (Musical.ly) | 5 | Direct negotiation, image exchange, identity verification |
| musical_ly_activity | 1 | Channel of the illicit discussion |
| installed_app | 2 | CM Security AppLock (anti-forensic shielding) |
| system_event | 2 | Device state |
| sms | 2 | Coordination/confirmation language (see limitations) |

### CAIE fractures (concealment indicators)

1. **Compartmentalization.** Owl trade discussed exclusively on Musical.ly (behind
   AppLock); Skype conversations deliberately excluded trade topics. Channel
   separation indicates awareness the activity was illicit.
2. **Anti-forensic awareness.** CM Security AppLock installed specifically to
   protect Musical.ly and Snapchat; subject deleted a prior email thread with
   Layla ("I accidentally deleted the ...").

## PEIRCEAN REASONING

- **Firstness.** Accounts across Google/Musical.ly/Skype/Twitter/Facebook/Snapchat
  with owl-related search history and browsing of `birdtrader.co.uk` owl listings.
- **Secondness.** Musical.ly chat between `sarahmcavoy` and `layster82`: request
  for email contact to coordinate, exchange of an owl image ("How do you like
  him"), buyer verification ("is that the exact one you have"). AppLock deployed
  to protect the apps. Deviates sharply from lawful pet interest, which does not
  require channel compartmentalization or app shielding.
- **Thirdness.** Researching owl care, browsing specific for-sale listings,
  establishing a protected contact channel with a known owl trader, verifying the
  specific animal's identity, and shielding the communications together reveal a
  deliberate, staged acquisition of a protected species — not idle curiosity.

## VERDICT LAYERS (preserved, per Mode 1/Mode 2 scope rule)

| Layer | Output | Meaning |
|-------|--------|---------|
| EBS decision pipeline | REJECT, posterior 1.0, LR ~4.85e8, ENFSI "very strong" | Strong statistical support for intentionality on this device |
| Doctrine cap (L-051 / §9.4-LIM) | **SUSPICION** | Single device/channel, no independent triangulation → MALICE barred |
| CAIE structural | NOISE (0.0586, 0 fractures at threshold) | Cross-artifact fusion does not, by itself, reach its suspicion floor |

The doctrine cap is the governing emitted verdict. The EBS strength and the CAIE
floor are disclosed as the honest internal disagreement, matching the examiner's
sealed dictum (FORENSIC_REPORT_OWL-NEXUS5.md §7.3, manual override 2026-07-03).

## MANDATORY REFUTATION (Eco's razor)

**Benign hypothesis:** lawful interest in owls as pets. **Test:** lawful interest
does not require compartmentalizing the discussion to a single app behind AppLock,
does not involve deleting the seller correspondence, and does not include buyer
verification of a specific animal from a trader. The benign reading fails to
explain the concealment fractures. **However**, the benign reading of *completion*
is NOT refuted: this device shows negotiation and intent, not a completed,
paid-for transaction. That gap is exactly why the verdict is capped at SUSPICION
rather than elevated. Downgrading here is the system working correctly.

## MITRE ATT&CK (behavioral analogues)

T1070.004 (Indicator Removal — deleted email thread), T1036 (Masquerading /
channel compartmentalization), T1071.001 (Application-layer messaging channel).

## KNOWN LIMITATIONS

- **Single-device ceiling (L-051).** MALICE requires independent corroboration;
  the purchase confirmation is expected on the companion HP laptop, not in this
  image. Verdict correctly capped at SUSPICION.
- **SMS coordination artifacts (B-206).** Two SMS ("...the delivery is today 7
  tonight the confirmation will come later through pidgin" / "Thank you!") were
  added to the case JSON from the verified `mmssms.db`; they still contribute only
  the `raw_score` floor because no semantic extractor is wired for legacy `sms`
  content (deliberately not wired without the full dry-run + adversarial protocol,
  B-207). They do not change the SUSPICION verdict.
- **Prefetch/temporal correlation** between Pidgin execution and the SMS
  confirmation is not available (the Win10-family prefetch parser does not yet
  decompress MAM-compressed prefetch; that evidence is on a different host anyway).
- **CAIE vs EBS disagreement** is real and disclosed, not reconciled by fiat.
- **`bundle_hash` is a per-seal identifier** (embeds a random bundle_id + wall
  timestamp); the determinism guarantee is over `decision_hash` / `graph_hash` /
  `analysis_fingerprint`, all stable across 3 runs.

## TOKEN USAGE (this session)

```
Deterministic seal (pipeline + CAIE + hashing + verification): 0 tokens.
Exact input/output token counts: usage.anthropic.com.
```
