# VIGÍA — Known Limitations

## General Principle

> *"When a Red Team has to resort to 'the attacker simulates the fractal distribution of Zipf errors', it means the code has no more real bugs to offer."*
> — Kimi, Principal Auditor, May 2026

This document enumerates the epistemological and design limitations of VIGÍA that **are not bugs** but necessary consequences of conscious architectural decisions. It fulfills the Daubert requirement of methodological transparency.

---

## L-001: Exploitable Ockham's Razor

**Description:** An attacker who knows the cost function can design an incident whose simplest explanation is benign incompetence, forcing VIGÍA to prefer ERROR over MALICE.

**Cause:** The abductive engine selects hypotheses by minimum cost of unobserved assumptions (Ockham's Razor). This is a fundamental epistemological principle, not an error.

**Forensic implication:** In court, if the defense demonstrates that VIGÍA ignored evidence because it was "mathematically expensive", the expert must explain that the system always chooses the most parsimonious explanation, and that this is a methodological virtue, not a weakness.

**Mitigation:** For production, implement a dynamic risk matrix that penalizes unverifiable assumptions more than verifiable ones.

**Status:** Accepted design limitation. Does not block hackathon.

---

## L-002: HMAC without TPM at Acquisition

**Description:** VIGÍA guarantees integrity of the sealed bundle via HMAC-SHA256, but cannot guarantee that evidence was not modified before entering the pipeline.

**Cause:** Hardware signing (TPM/HSM) at capture time requires infrastructure integration not available in all environments.

**Forensic implication:** If an attacker with system access modifies evidence before processing, VIGÍA will certify a perfect HMAC over false data. Pre-pipeline chain of custody depends on the operator.

**Mitigation:** Integrate TPM/HSM for timestamping at acquisition (code prepared in `TrustLevelVerifier`, `HSMConnector`).

**Status:** Accepted for MVP. Critical for production with MLPS 2.0 Level 4.

---

## L-003: Cryptographic Signature Placeholder

**Description:** Modules `report_exporter_v2.py` and `evidence_registry.py` use `"SIGNED(...)"` as a placeholder instead of a real cryptographic signature with HSM.

**Cause:** HSM integration requires physical infrastructure beyond MVP scope.

**Forensic implication:** PDF reports and manifests lack cryptographically verifiable origin authenticity.

**Mitigation:** Integrate with real HSM via PKCS#11 (code prepared in `pki_tools.py`, `HSMConnector`).

**Status:** Accepted for hackathon. Blocking for production.

---

## L-004: PeircePlanner without Iteration Limit

**Description:** The abduction cycle of `PeircePlanner` has no `max_iterations`. With contradictory Thirdness signals, it could recalculate indefinitely.

**Cause:** Initial design without anticipation of semantic saturation attacks.

**Forensic implication:** A maliciously designed case with contradictory signals could hang the inference engine through CPU exhaustion.

**Mitigation:** Implement breaker after N failed attempts to reduce entropy.

**Status:** P1. To be resolved in current sprint.

---

## L-005: Synthetic Zipf Attack

**Description:** If an attacker uses a language model configured to follow a fractal error distribution that exactly mimics Zipf's Law, the artificiality detector will return false negative.

**Cause:** VIGÍA seeks human imperfection as an authenticity signal. Current generative AI can simulate that imperfection.

**Forensic implication:** Epistemological limit, not a bug.

**Mitigation:** Complement with other detectors (temporal, stylometric, entanglement).

**Status:** Documented epistemological limitation. No immediate technical fix.

---

## L-006: Eco Bypass (Paranoia Manipulation)

**Description:** An attacker can inject terms like "mimikatz" or "admin123" in >50% of artifacts to force a `POSSIBLE_SCENE_STAGING` verdict, causing the analyst to ignore real signals.

**Cause:** Eco detector assumes high density of "obvious signals" implies planted evidence.

**Mitigation:** Implement minimum additional signal threshold for `POSSIBLE_SCENE_STAGING`.

**Status:** Design limitation. Human analyst always signs final verdict (Dual Custody).

---

## L-007: Silent Deactivation via Environment Variables

**Description:** Critical modules like CAIE and Trust Fusion are activated/deactivated via environment variables (`VIGIA_CAIE_ENABLED`). An attacker with environment access can silently degrade the system.

**Cause:** Configuration design intended for development flexibility.

**Mitigation:** Replace environment variables with signed configuration inside the bundle.

**Status:** P1. To be resolved before production.

---

## L-008: fitz vs pypdf Divergence

**Description:** `audit_document_integrity` uses `fitz` as primary parser with fallback to `pypdf`. The same PDF may produce different verdicts depending on which library is installed.

**Forensic implication:** Breaks determinism between environments.

**Mitigation:** Remove fallback. If `fitz` is unavailable, tool should fail loudly.

**Status:** P1. Must be resolved before SIFT integration.

---

## L-009: Type Collision in Canonicalization

**Description:** The `_canonicalize` function uses prefixes like `"1:int"`. If an artifact literally contains that string, it may collide with a real integer.

**Forensic implication:** Potential integrity hash collision between distinct data types.

**Mitigation:** Use non-printable characters or nested structures for type prefixes.

**Status:** P1. Low exploitation probability, high criticality if it occurs. Requires unified refactoring across 12 copies.

---

## L-010: Fraction Growth in Complex Aggregations

**Description:** VIGÍA uses `Fraction` for cross-arch determinism. In complex aggregations with multiple synergies, numerators and denominators can grow exponentially.

**Mitigation:** Implement truncated division for fractions with numerator/denominator > 10^6.

**Status:** P2. Not observed in real cases.

---

## Summary

| ID | Limitation | Impact | Status |
|----|-----------|--------|--------|
| L-001 | Exploitable Ockham's Razor | Evidentiary | Accepted |
| L-002 | HMAC without TPM at acquisition | Chain of custody | Accepted for MVP |
| L-003 | Signature placeholder | Authenticity | Accepted for MVP |
| L-004 | PeircePlanner without iteration limit | DoS | P1 |
| L-005 | Synthetic Zipf | Epistemological | Documented |
| L-006 | Eco Bypass | False positive | Documented |
| L-007 | Silent deactivation via env vars | Degradation | P1 |
| L-008 | fitz/pypdf divergence | Determinism | P1 |
| L-009 | Canonicalization type collision | Hash | P1 |
| L-010 | Fraction growth | Performance | P2 |

---

*Document generated May 4, 2026 by the VIGÍA Collective.*
*Fulfills Daubert methodological transparency requirement.*
