# VIGÍA — Judicial Admissibility (ISO 27037 / Daubert Standard)

VIGÍA is designed to produce digital evidence admissible in court under the
**Daubert** standard (U.S.) and **ISO 27037:2012** (international). The
following details how each system component satisfies admissibility requirements.

---

## Requirement 1: Reproducible Scientific Methodology

**Daubert requires** that the technique be testable and subject to peer review.

VIGÍA implements:

- **Forced determinism** (`VIGIA_FORENSIC_LOCK=true`): LLM temperature fixed at
  0, fixed seed for Ollama (42). The same evidence always produces the same
  report. Verifiable with `make check-determinism`.
- **Published theoretical framework**: Peirce's semiotics (abduction), Grice's
  maxims (forensic pragmatics), Carnegie's patterns (manipulation detection),
  Eco's filter (overinterpretation). Each tool documents which theory it applies
  and why.
- **Explicit abductive chain**: every investigation step includes a `reasoning`
  field explaining WHY the next tool was selected. An auditor can reconstruct
  the full logic without executing the system.

---

## Requirement 2: Immutable Chain of Custody

**ISO 27037 requires** that digital evidence not be altered during analysis.

VIGÍA implements:

- **Atomic hash during read**: `read_evidence` uses `O_NOFOLLOW` + `os.fstat(fd)`
  + single-pass read. The SHA-256 corresponds exactly to the bytes processed
  (no TOCTOU window).
- **HMAC-chained signed audit log**: every forensic log entry includes
  `_prev_hmac` (hash of the previous entry) and `_hmac` (HMAC-SHA256 of
  content + previous hash). Altering any line invalidates the entire subsequent
  chain. Verifiable with `audit_logger.verify_chain()`.
- **Read-only evidence mount**: Docker mounts the evidence directory with `:ro`.
  Analysis cannot modify the source.
- **WORM enforcement**: `audit_logger.enforce_worm()` applies `chattr +i`
  (Linux ext4/xfs) to the log, making it immutable at the kernel level.

---

## Requirement 3: Qualified Human Operator

**Daubert requires** that the technique be applied by a competent professional.

VIGÍA implements:

- **Witness Mode (Dual Custody)**: when the verdict is MALICE or INTENT, the
  report is signed with a second HMAC key (`VIGIA_HUMAN_OPERATOR_KEY`) proving
  that an authorized analyst was present. Without this co-signature, the report
  is marked `UNSIGNED` with an explicit warning.
- **Explain Mode**: `make investigate MODE=explain` shows what the planner would
  do without executing anything. The operator reviews BEFORE authorizing.
- **Self-correction**: `validate_and_correct_analysis` checks 4 Peircean
  fallacies before issuing a final verdict.

---

## Requirement 4: Known Error Rate

**Daubert requires** that the technique have a known or knowable error rate.

VIGÍA implements:

- **4-level scale** (NOISE / SUSPICION / INTENT / MALICE): not binary. Each
  level requires more evidence than the previous one.
- **Mandatory cross-validation**: no single tool can trigger MALICE. At least
  2 independent sources of evidence are required.
- **Epistemic humility**: every conclusion includes `what_would_falsify_this`
  — the condition under which the hypothesis would be false.
- **`check_determinism.py`**: runs the same analysis N times and compares
  hashes. Any divergence is reported as NON-DETERMINISM.

---

## Requirement 5: General Acceptance by the Scientific Community

**Daubert requires** general acceptance of the technique in the relevant community.

VIGÍA implements:

- **STIX 2.1 export**: findings are exported to the standard format ingestible
  by OpenCTI, MISP, and any compatible platform.
- **MITRE ATT&CK mapping**: every signal is linked to a specific ATT&CK
  technique with its ID and URL.
- **Open source (Apache 2.0)**: the complete system is auditable by any
  expert or counter-expert witness.

---

## Judicial Use Protocol

```bash
# 1. Generate keys
make hmac-key                    # System key
export VIGIA_HUMAN_OPERATOR_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 2. Activate forensic mode
export VIGIA_FORENSIC_LOCK=true
export VIGIA_STRICT_MODEL_CHECK=true

# 3. Analyze evidence (isolated, no network, read-only)
EVIDENCE_PATH=/mnt/case_2025_001 make run

# 4. Verify integrity
make check-integrity             # HMAC chain intact
make check-determinism           # Reproducibility confirmed

# 5. Seal log (WORM)
python3 -c "from vigia.security import audit_logger; print(audit_logger.enforce_worm())"

# 6. Export for the court
cp reports/investigation_*.json /mnt/forensic_delivery/
cp logs/security_audit.log      /mnt/forensic_delivery/
```

---

## ISO 27037:2012 Mapping

| ISO Clause | Requirement | VIGÍA Implementation |
|---|---|---|
| 5.4.1 | Evidence preservation | Read-only mount, atomic hash |
| 5.4.2 | Process documentation | HMAC audit log, `reasoning` field |
| 5.4.3 | Chain of custody | Chained HMAC, WORM, UTC timestamps |
| 6.2 | Operator competence | Witness Mode, HUMAN_OPERATOR_KEY |
| 6.3 | Tool validation | check_determinism.py, E2E tests |
| 7.1.2 | Data integrity | Atomic SHA-256, O_NOFOLLOW, O_EXCL |

---

## Documented Limitations (Expert Witness Transparency)

- LLM-based tools (`reason_with_llm`, `validate_and_correct_analysis`) are not
  100% deterministic even with temperature=0, due to the nature of language
  models. `FORENSIC_LOCK` minimizes but does not eliminate variance.
- Stylometry (`analyze_stylometry`) produces false positives on texts shorter
  than 50 words.
- Cultural calibration is optimized for Rioplatense Spanish. Other dialects or
  languages may require adjustments to gender patterns and official document
  field detection.
- CLIP (`vision_intent_audit`) is a zero-shot classifier — it was not trained
  specifically for document forgery detection.

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
