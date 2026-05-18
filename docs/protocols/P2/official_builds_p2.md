# VIGÍA Official Builds — Epistemological Governance (P1 + P2)

> **Version:** 2.4-Draft
> **Date:** 2026-05-16
> **Authors:** VIGÍA AI Collective (Anna Tchijova, Kimi, Claude, Gemini, DeepSeek, ChatGPT, Qwen, Grok)
> **Active protocols:** P1 (frozen), P2 (draft v2.8)

---

## 1. Founding Principle (unchanged since v1)

**Anyone may fork, modify, and extend VIGÍA.**

But only builds that pass the official semantic fingerprint may claim compatibility.

This is not DRM. It is epistemological honesty.

---

## 2. Determinism Protocols

| Protocol | Date | Status | Key semantics | Canonical Fingerprint |
|----------|------|--------|---------------|----------------------|
| **P1** | 2026-05-16 | **FROZEN** | `float64`, `round(x, 6)`, `uint64` pair encoding, Shannon entropy | ✅ Active |
| **P2** | 2026-05-16 | **DRAFT v2.8** | Markov order-k, Lempel-Ziv, permutation entropy, abstention (open-interval), adversarial, discretization policy, terminology warnings, interpretation safeguards, PRNG binding tiered by compliance level | In development |
| P3 | — | Planned | Hypothesis engine, graph scoring, classifier policy, formal upstream discretization standard | — |

### Protocol Hierarchy

```
P3 (future — see P2 SPEC §20 for P3-01..P3-05 scope)
└── P2 (draft v2.8)
    └── P1 (frozen)
        └── IEEE 754 float64
```

**Golden rule:** You cannot claim P2 without P1. You cannot claim P3 without P2.

---

## 3. Permitted Claims (updated for P2 v2.8)

| Claim | Requires P1 | Requires P2 | Requires signed manifest | Notes |
|-------|-------------|-------------|--------------------------|-------|
| "Built on VIGÍA" | No | No | No | Honest credit |
| "Fork of VIGÍA" | No | No | No | Transparency |
| "VIGÍA-compatible P1" | **Yes** | No | No | Determinism base |
| **"VIGÍA-compatible P2"** | **Yes** | **Yes** | No | Advanced semantics |
| "Official VIGÍA runtime" | Yes | Recommended | **Yes** | Signed build |
| "VIGÍA-certified" | Yes | Yes | Yes + audit | Commercial |

### PROHIBITED Claims

- "VIGÍA" alone (without qualifier)
- "Deterministic VIGÍA" (without passing fingerprint)
- "Daubert-ready VIGÍA" (without independent forensic audit)
- "SANS-approved VIGÍA" (SANS certifies people, not software)
- **"P2-compatible" without P1** (hierarchy violation)
- **Any interpretive claim from the `terminology_warnings.prohibited_interpretive_phrasings` list** — e.g., "AI detector", "bot detector", "humanity index", "authenticity score", "deception score", "intent score". These conflate distributional descriptors with ontological categories and are forbidden in any VIGÍA-compatible build's documentation, marketing, or output labels.

---

## 4. Attestation Architecture

### Level 1 — Cryptographic manifest

```json
{
  "vigia_version": "2.8.0",
  "protocols": ["P1", "P2"],
  "git_commit": "a81f2d...",
  "files": {
    "entropy_kernel.py": "04d3444d...",
    "markov_engine.py": "...",
    "lz_engine.py": "...",
    "pe_engine.py": "..."
  }
}
```

### Level 2 — Runtime attestation

```python
from vigia_attestation import verify_runtime_integrity

result = verify_runtime_integrity()
# VIGIA_RUNTIME_ATTESTATION
# STATUS: VERIFIED | MODIFIED | INCOMPATIBLE
# PROTOCOLS: P1, P2
# FINGERPRINT_P1: a91f3c...
# FINGERPRINT_P2: b82e4d...
```

### Level 3 — Canonical semantic fingerprint

```python
# P1 fingerprint (base)
fingerprint_p1 = {
    "protocol": "P1",
    "entropy_uniform": 0.0,
    "entropy_distinct": 1.0,
    "entropy_shannon_seed42": 7.782633,
    "pair_encoding_collision_free": True
}

# P2 fingerprint (extension)
fingerprint_p2 = {
    "protocol": "P2",
    "schema_version": "2.8",
    "depends_on": "P1",
    "markov_k1_deterministic": 0.0,
    "lz_periodic_low": 0.109718,
    "pe_monotonic_zero": 0.0,
    "pair_fuzz_max_uint32_token": 18446744073709551615,
    "abstention_zone_respected": True,
    "vector_count": 22
}

# Combined
fingerprint = sha256(
    json.dumps({**fingerprint_p1, **fingerprint_p2}, sort_keys=True)
)
# → VIGIA-P2-fp64-b82e4d...
```

---

## 5. Chain of Custody (introduced in v2, extended in v2.1)

P2 introduces forensic traceability. v2.5 requires that the **discretization step** for any non-natively-discrete input be recorded in the manifest:

```json
{
  "evidence_id": "sha256-of-raw-evidence",
  "processing_pipeline": {
    "vigia_version": "2.8.0",
    "protocols": ["P1", "P2"],
    "modules": ["entropy", "markov", "lz", "pe"],
    "canonical_vectors_hash": "f7276a52...",
    "discretization": {
      "function": "uniform_quantizer",
      "parameters": {"bins": 256, "range": [0.0, 1.0]},
      "provenance": "implementer-defined; documented per P2 §4",
      "applies_to": "raw_audio_signal_input"
    }
  },
  "output": {
    "deterministic_hash": "sha256-of-output",
    "reproducible": true
  },
  "audit_trail": [
    {"action": "ingest", "timestamp": "2026-05-16T12:43:00Z"},
    {"action": "discretize", "timestamp": "..."},
    {"action": "entropy_analysis", "timestamp": "..."},
    {"action": "markov_analysis", "timestamp": "..."}
  ]
}
```

**Principle:** Same evidence + same protocol + same discretization = same output = verifiable.

**Failure mode:** If the discretization block is missing for non-discrete input, P2 vectors may still pass, but **forensic reproducibility claims are invalid**. Validators SHOULD warn loudly.

---

## 6. What VIGÍA is NOT (unchanged)

### NOT DRM

- No license keys
- No cloud auth
- No phone-home
- No telemetry
- No secret constants
- No obscure anti-tamper

### NOT anti-fork

Forks are welcome. They must be honest about what they are.

### NOT a detector of anything ontological

P2 metrics describe distributional properties. They do not detect AI vs human, real vs fake, honest vs deceptive, authentic vs synthetic. The `terminology_warnings` block in `canonical_vectors_p2.json` enumerates prohibited interpretive phrasings. Any build whose documentation or output labels violate that list forfeits the right to claim P2 compatibility.

---

## 6a. What P2 Guarantees vs Does NOT Guarantee (single normative summary)

This table is duplicated from P2 SPEC §16 for consistency. The two sources MUST stay in sync; if they diverge, the JSON `canonical_vectors_p2.json` is authoritative.

| ✅ P2 Guarantees | ❌ P2 Does NOT Guarantee |
|------------------|--------------------------|
| Deterministic quantized equivalence across backends | Absolute accuracy — reproducibility ≠ truth |
| Contextual entropy (Markov memory) | Behavioral classification (humans vs bots, real vs synthetic) |
| Complexity semantics (LZ compressibility) | Authorship attribution or intent inference |
| Ordinal invariance (PE under monotonic transformations) | Legal admissibility certification |
| Adversarial rejection (denormals, NaN, Inf, overflow) | Complete adversarial robustness — see SPEC §14 GAP-01..GAP-10 |
| Abstention honesty (formalized as protocol property) | Calibrated decision thresholds — see SPEC §13.4 |
| Symbolization honesty (exact float64 equality) | Upstream discretization correctness — delegated, see SPEC §4 |
| Pair encoding safety (collision-free bijective map) | Forensic conclusions about specific evidence |
| Cross-backend equivalence post-quantization | Score fusion, composition, uncertainty propagation — see SPEC §20 P3 future work |
| Compliance transparency (strict / reference / accelerated) | Ontological claims about "humanity" or "authenticity" |

---

## 7. References

- `docs/protocols/P1/SPEC.md` — P1 Specification
- `docs/protocols/P1/canonical_vectors.json` — P1 vectors
- `docs/protocols/P2/SPEC.md` — P2 Specification v2.8
- `docs/protocols/P2/canonical_vectors_p2.json` — P2 vectors
- `docs/protocols/P2/canonical_vectors_p2.sha256` — P2 canonical hash
- `entropy_kernel.py` — P1 implementation
- `vigia_advanced_semantics.py` — P2 implementation (planned)

---

## 8. Contact / Governance

**VIGÍA AI Collective**
SANS FIND EVIL Hackathon 2026
Open source — available for independent forensic audit

*"Authenticity arises from transparency, not from secrets."*
*"P1 makes measurements comparable. P2 makes measurements contextual."*
