# VIGIA CAIE v2.0 - Known Limitations

## Adversarial Test Results

### Summary
- Total adversarial cases: 25
- Passed: 22
- Failed: 3
- High risk false confidence: 0

### Failed Cases

The following cases fail because CAIE v2.0 does not detect sensor independence violations:

1. ASSUMPTION_BREAK_timestamp_comparability_AND_sensor_independence
2. ASSUMPTION_BREAK_sensor_independence_AND_memory_ground_truth
3. ASSUMPTION_BREAK_sensor_independence_AND_log_completeness

### Root Cause

CAIE v2.0 has no native detection for sensor independence. The system assumes that different source_tool values indicate independent evidence sources. It does not detect when multiple source_tools actually represent the same underlying sensor or acquisition pipeline.

### Why This Matters

In real adversarial scenarios, an attacker who compromises a single EDR sensor can fabricate evidence appearing to come from multiple independent sources. CAIE v2.0 cannot detect this and may produce overconfident verdicts (SUSPICION instead of INCONCLUSIVE).

### Mitigation for v2.0

Operators should be aware that CAIE v2.0 assumes sensor independence. When multiple evidence sources may originate from the same compromised sensor, manual review is required.

### Roadmap for v3.0

- EvidenceDependencyGraph with sensor_fingerprint tracking
- AcquisitionContext.provenance_trust field
- Collapse Decision Layer rules for sensor independence
- INCONCLUSIVE verdict for dependency detection

### Epistemological Limit

No closed system can distinguish between "no evidence" and "perfectly hidden attack" without an external trust anchor (TPM, hypervisor attestation, hardware root of trust). This is a fundamental limit, not a bug.

---
Last updated: 2026-05-18
