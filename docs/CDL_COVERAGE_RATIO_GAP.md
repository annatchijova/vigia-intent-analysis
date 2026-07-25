# CDL `coverage_ratio` gap — investigated, partially fixed

**Status:** unbounded-ratio bug fixed (`vigia/tools/caie.py`, `CrossArtifactIncongruenceEngine.evaluate()`); the deeper membership-validation gap is documented here but deliberately **not** fixed yet — it needs a reviewed taxonomy, not a quick patch.

## Background

The Collapse Decision Layer (`vigia/collapse_decision.py`, "Kimi P0 audit") is meant to force `CollapseVerdict.INCONCLUSIVE` when a case's evidence is too narrow to trust a confident verdict:

```python
if ctx.coverage_ratio < 0.3:
    return CollapseVerdict.INCONCLUSIVE
```

`coverage_ratio` is computed in `caie.py` right before the CDL call:

```python
total_expected_layers = ["memory", "process", "auth", "filesystem", "network", "kernel"]
observed_layers = set()
for a in self._artifacts:
    layer = a.metadata.get("layer", a.evidence_type)
    observed_layers.add(layer)
coverage_ratio = len(observed_layers) / len(total_expected_layers)
```

This is the same failure class as the `independent_sources` bug fixed earlier on this branch (see `git log --grep="independent_sources materiality"`): a count of *distinct labels*, standing in for a count of *substantive coverage*, with no check that the labels mean what the metric assumes they mean.

## What's confirmed broken

1. **Unbounded ratio (fixed).** `observed_layers` counts every distinct label seen with no cap and no membership check. 10 distinct `evidence_type` values were enough to produce `coverage_ratio = 1.667` (167%) — a value `CollapseDecisionLayer.explain()` formats as a percentage in the Daubert-facing narrative. Fixed by capping the numerator: `min(len(observed_layers), len(total_expected_layers))`.

2. **Not actually membership-tested (not fixed).** `metadata.get("layer", a.evidence_type)` is designed so a producer can explicitly declare one of the 6 canonical layers via `metadata["layer"]`, falling back to `evidence_type` otherwise.
   - `grep -rn '"layer"'` across `vigia/` found **zero** producers that ever set `metadata["layer"]`. The two `"layer"` hits that exist (`pattern_detector.py`, `semiotic_detector_v2.py`) are `"peirce_layer"` (Firstness/Secondness/Thirdness) — an unrelated concept.
   - `_VALID_EVIDENCE_TYPES ∩ {"memory", "process", "auth", "filesystem", "network", "kernel"} = ∅` — none of the 70+ whitelisted `evidence_type` strings (`memory_process`, `file_metadata`, `network_flow`, ...) are literal members of `total_expected_layers`.
   - Consequence: in 100% of current real usage, `coverage_ratio` measures "how many distinct `evidence_type` labels were used, capped at 6/6" — not genuine cross-domain coverage. The `< 0.3` gate is cleared by just **2** distinct `evidence_type` labels (2/6 = 0.333), regardless of whether they represent genuinely diverse forensic domains. `memory_process` + `kernel_structure` both being memory/kernel-adjacent still counts as "2 of 6 layers observed."

## Why this isn't fixed here too

A real fix needs an explicit, reviewed `evidence_type -> {memory, process, auth, filesystem, network, kernel, other}` mapping. That's a separate, larger task:

- Most of the 70+ `_VALID_EVIDENCE_TYPES` don't fit a 6-layer *host-forensics* taxonomy at all (`chat_message`, `social_media`, `osint`, `document_visual`, `linguistic_forensics`, `email_content`, ...) — CAIE's evidence-type whitelist clearly grew well past the scope the 6-layer list was designed for, and a mapping needs to decide what to do with all of those (a 7th "other" bucket? exclude them from the denominator entirely? something else?).
- Any mapping must be validated against the full canonical case corpus (`tests/caie/test_canonical_cases.py`) before landing — the same discipline the `independent_sources` fix required after its first (adjusted-score) attempt broke a real corpus case (`case_107_anacronismo_firma_digital`). A naive or rushed mapping here risks the opposite failure: silently downgrading real MALICE/SUSPICION verdicts to INCONCLUSIVE for a reason that has nothing to do with actual evidentiary breadth, which is a worse failure mode for a Daubert-facing tool than the current over-lenient gate.

## Suggested next steps (not started)

1. Build the `evidence_type -> layer` mapping as a standalone, reviewed table (not inline in `evaluate()`), with an explicit "unmapped" bucket for types outside the 6-layer scope, excluded from both numerator and denominator rather than silently miscounted.
2. Decide the semantics of "unmapped" evidence in the ratio — do communications/document/OSINT-heavy cases need their own coverage taxonomy entirely, or should `total_expected_layers` grow to include those domains?
3. Run the full corpus before and after; any case whose verdict flips must be individually reviewed, not just diffed.
