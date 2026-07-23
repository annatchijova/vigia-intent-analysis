# AMICUS CURIAE — Project OWL (COMPLETE, two devices)

**In the matter of case VIGIA-OWL-2019-COMPLETE**
**Submitted by:** VIGIA Autonomous Forensic Intent Engine (Claude Code / Claude Fable, Mode 2)
**Corpus entry:** `data/cases/VIGIA-OWL-2019-COMPLETE.json` (30 artifacts; schema validates)
**Sealed bundle:** `OWL-COMPLETE_bundle_claude_fable.json`, decision hash `617cd69ca65d531ecd8deea4...` (EBS verify PASS, Level 2)
**Component seals:** `OWL-NEXUS5_bundle_claude_fable.json` (phone), `OWL-HD1_bundle_claude_fable.json` (computer)

---

## I. Purpose

This brief consolidates the two-device Project OWL record into a single, verifiable
corpus case and states its combined disposition with the fact/inference boundary
kept explicit.

## II. Facts established across the two devices

1. Both devices belong to Sarah McAvoy (`mcavoys87@gmail.com`).
2. **Nexus 5:** a Musical.ly negotiation with the seller `layster82` (request to
   move to email, owl image exchange, verification of the specific animal); CM
   Security AppLock protecting the messaging apps; two coordination SMS.
3. **HD1 companion computer:** Chrome browsing of specific owl for-sale listings on
   `birdtrader.co.uk` and snowy-owl-egg vendors; owl husbandry/emergency PDFs and a
   snowy-owl bibliography; Pidgin under the same account run seven times; automatic
   chat logging enabled but no logs present; six owl images/PDFs deleted to the
   Recycle Bin (recovered).

## III. Inference: INTENT by cross-device corroboration

The phone-only case was capped at SUSPICION under doctrine L-051 for want of an
independent second source. HD1 is that source. Two independent devices belonging to
the same subject, showing the same deliberate owl-trade preparation, satisfy the
two-source bar; the deterministic pipeline scores the combined evidence "very
strong" (LR ~4.85e8, REJECT, posterior 1.0). The combined grade is **INTENT**.

## IV. Why NOT MALICE

No completed transaction or payment record exists on either device; the owl-purchase
confirmation expected "through pidgin" is not present as a saved log (its absence is
ambiguous between deletion and never-logged); the HD1 file deletions are recoverable
soft-deletes, not secure erasure. Deliberate restraint keeps the grade at INTENT.

## V. Verification — nothing missing

The corpus case validates (`validate_case_schema`, 30 artifacts). The sealed bundle
reproduces bit-for-bit (`decision_hash` identical across three runs) and passes the
independent `verify_ebs_v1.py` at **Level 2 (cryptographically valid)**, 10 of 11
checks. The single non-OK is `R5_ECL_BINDING` — an optional Level-3 Evidence-Chain-
Ledger anchor requiring the persistent chain database — reported as a WARN, not a
missing element of the case. No floating-point value governs the sealed decision and
no language model influenced it.

## VI. Recommendation

The consolidated record supports treating Project OWL as **INTENT** — deliberate,
coordinated, two-device preparation to acquire a protected owl by the same subject.
Completion (payment, delivery) remains the open question and would require off-device
records; it is the only step separating this case from a higher grade.

*Respectfully submitted. The corroboration is proven; the completed transaction is
not — hence INTENT, by deliberate restraint.*
