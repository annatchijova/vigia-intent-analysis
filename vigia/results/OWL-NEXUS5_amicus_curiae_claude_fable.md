# AMICUS CURIAE — Forensic Intent Analysis

**In the matter of case VIGIA-OWL-2019-NEXUS5 (Project OWL — Illegal Owl Trade)**
**Submitted by:** VIGIA Autonomous Forensic Intent Engine (Claude Code / Claude Fable, Mode 2)
**Evidence:** `LGE Nexus 5 Full Image.raw`, raw SHA-256 `763e7acde388519940f351bc3c6cc1747ed4f99423ad6c892745553804b6a5de` (acquisition MD5 `B334843A07A9E16494EEBDF3079E6BC6` / SHA1 `F46EE05CE1A2210501EA512ED9E4C7EC59222CCA`, Magnet ACQUIRE)
**Sealed bundle:** `OWL-NEXUS5_bundle_claude_fable.json`, decision hash `1fc5282832ebba458857717f938fa8b95de918edf45c3d0802dc71ce225264e3` (EBS verify PASS, Level 2)

---

## I. Purpose and posture

This brief is a neutral forensic aid, not advocacy. It states, with explicit
separation of fact from inference, what the Nexus 5 image supports regarding the
subject Sarah McAvoy's participation in the illegal trade of a protected owl, and
— equally — what it does not support. Every fact traces to a reproducible artifact
in the imaged device.

## II. Facts established on the device

1. The device is Sarah McAvoy's rooted, unencrypted LGE Nexus 5 (Android 6.0.1),
   bearing her linked accounts across Google, Musical.ly (`sarahmcavoy`), Skype,
   and Twitter.
2. The browser and search history show owl-care research and visits to specific
   owl-for-sale listings on `birdtrader.co.uk`.
3. Musical.ly instant messages record a direct negotiation between `sarahmcavoy`
   and the seller `layster82` (Layla Aster): a request to move to email to
   coordinate, exchange of an owl photograph ("How do you like him"), and buyer
   verification of the specific animal ("is that the exact one you have").
4. CM Security AppLock was installed and configured to protect the messaging apps
   (Musical.ly, Snapchat).
5. A prior email thread with Layla was deleted by the subject.

These are **observations**, corroborated across artifact classes (account
registrations, web history, instant messages, installed-app inventory, system
events).

## III. Inference and the standard applied

From II, the engine infers **deliberate, staged intent to acquire a protected
owl**, with two concealment fractures — channel compartmentalization (trade kept
to one AppLock-protected app while Skype was kept clean) and anti-forensic
awareness (deletion of the seller correspondence). The Mandatory Refutation
Protocol was applied: the benign "lawful pet interest" hypothesis fails to explain
compartmentalization, app-shielding, and correspondence deletion.

## IV. Why the verdict is SUSPICION, not MALICE

The tribunal is owed the precise reason the grade is bounded:

- The **deterministic EBS decision pipeline** rates the intentionality hypothesis
  as **very strong** (likelihood ratio ~4.85e8; ENFSI verbal equivalent "very
  strong"; decision REJECT of the benign null; posterior 1.0).
- Nevertheless, the emitted verdict is **SUSPICION**, applied by governing doctrine
  **L-051 / §9.4-LIM**: a single device and a single communication channel, absent
  independent triangulation, cannot support MALICE. The negotiation and the intent
  are on the phone; the **purchase confirmation and any payment record are expected
  on a companion device (an HP laptop) that is not part of this acquisition**.
  Without that corroboration, no completed transaction is proven on this evidence.
- The **CAIE structural fusion** independently returns **NOISE** (composite 0.0586,
  no cross-artifact fracture at its threshold).

This divergence is disclosed rather than reconciled by fiat. It reflects a genuine
evidentiary boundary: strong intent on one device is not the same as a proven,
corroborated, completed offense. The conservative cap protects against
over-attribution and matches the examiner's sealed dictum (FORENSIC_REPORT_OWL-
NEXUS5.md §7.3, manual override 2026-07-03).

## V. Matters the evidence does NOT establish

1. **A completed, paid-for transaction.** No payment record or delivery
   confirmation exists on this device. The SMS coordination language ("the delivery
   is today ... the confirmation will come later through pidgin") points beyond the
   device; it is not itself proof of completion.
2. **Corroboration from a second source.** The companion HP laptop was not imaged;
   until it is, the offense stands at the intent/negotiation stage on this record.
3. **Possession of the animal.** Nothing on the phone establishes that the owl was
   received.

## VI. Chain of custody and reproducibility

The image carries recorded acquisition hashes (MD5/SHA1 above, Magnet ACQUIRE);
this analysis additionally computed SHA-256 `763e7acd…b6a5de` over the raw. The
case was scored through the repository's deterministic EBS pipeline; the decision
content is reproducible bit-for-bit — `decision_hash`, `graph_hash`, and the
`analysis_fingerprint` were identical across three independent runs. No
floating-point value governs the sealed decision (the pipeline uses exact
arithmetic), and no language model influenced the sealed verdict; the LLM layer
renders prose beside the seal only. The bundle passed the independent
`verify_ebs_v1.py` verifier at **Level 2 (cryptographically valid)**.

**Caveat of record:** the bundle-level `bundle_hash` embeds a per-seal random
identifier and wall-clock timestamp, so it varies between seals by design; the
determinism guarantee attaches to the decision-content hashes, not to that
envelope hash.

## VII. Recommendation

The record supports referring this matter for **illegal wildlife-trade** review at
the **intent/negotiation** stage, and prioritizing **acquisition and imaging of the
companion HP laptop** to convert the completed-transaction question from unproven
to determinable. The SUSPICION grade rests on CONFIRMED on-device facts and a
passed refutation; its ceiling is a documented evidentiary limitation, not a
weakness of the finding.

*Respectfully submitted. A documented limitation is presented as an asset; VIGIA
emits scope-bounded, reproducible findings and declines to over-attribute.*
