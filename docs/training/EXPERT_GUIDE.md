# Reviewing a sealed VIGÍA bundle as an expert

This guide is for a forensic examiner who has to defend, attack or reproduce a
VIGÍA verdict. It covers the three bundle families and what each seals, the
verification workflow, how Daubert gates are recorded, and how to read the expert
report (`*_report_expert_<lang>.md`). Spanish version:
[`EXPERT_GUIDE_ES.md`](./EXPERT_GUIDE_ES.md). The report is a viewer: everything
below can be checked against the bundle without trusting the prose.

---

## 1. Three families, three seals

The repository grew three bundle layouts (`docs/EXECUTION_MODES.md`). Their hashes
are **not comparable across families** (`KNOWN_LIMITATIONS.md` L-030, L-031); the
expert report prints each family's anchors and marks the others as absent rather
than substituting.

| Family | Seal | Anchors printed | Verifier |
|---|---|---|---|
| `ebs_v1` | `integrity.bundle_hash` over every payload key except `integrity` (Invariant I2); `analysis_fingerprint` over the payload minus timestamps and ids | `bundle_hash`, `analysis_fingerprint`, `graph_hash`, `decision_hash`, `policy_hash`, `engine_attestation_hash`, `ecl_hash`, `sealed_at` | `python3 forensics/verify_ebs_v1.py <bundle>` (stdlib only) |
| `agent_audit` | SHA-256 of the **whole file**, stored in the `.sha256` sidecar, never inside the file (self-reference) | `evidence_sha256`, `runtime_fingerprint`, `analysis_timestamp`, `audit_trail.total_entries` | `sha256sum -c <bundle>.sha256`; `vigia.core.reasoning_trace.verify_reasoning_trace` for the trace sibling |
| `mcp_investigation` | investigator-recorded `bundle_sha256`; hash-chained `tool_execution_log` (`prev_hash`, `entry_hash`, optional `entry_hmac`) with a `chain_tip_sha256` tail anchor | `bundle_sha256`, `primary_evidence_sha256`, `chain_tip_sha256`, `timestamp_sealed` | `python3 verify_tool_log.py <bundle> [--hmac-key-file F]` |

Consequence for any presentation: nothing can be added *inside* a bundle without
changing its seal. The reports are sibling files, exactly like
`<stem>_reasoning_trace.json`.

## 2. Verification workflow

1. **Bind the file.** The report header carries the SHA-256 of the exact bytes it
   was rendered from. `sha256sum <bundle>` must match; if not, the report is stale.
2. **Run the family's verifier** (table above). Running the wrong one reports
   non-compliance by design; that is not a finding against the bundle.
3. **Regenerate the report** and diff it: `python3 -m vigia.report <bundle>
   --audience expert --lang en --stdout`. Same bundle bytes, same report bytes, on
   any machine, under any `PYTHONHASHSEED`, locale or timezone.
4. **Read the gaps.** Anything the reader could not find is listed, never filled.
5. **Cross-check the exact literals** (report section 4) against the JSON pointers.
   Serialized Fractions print as `numerator/denominator`; sealed floats print as
   their own JSON literal. If you see a float in a sealed path, that is itself a
   recorded limitation (L-021, L-073), not a rendering artifact.

## 3. Verdict-bearing fields and disagreement

Report section 2 lists every field the normalizer treats as verdict-bearing, with
its JSON pointer. EBS v1 bundles can carry `decision_trace.decision` and
`caie_analysis.verdict`; agent bundles carry `agent_verdict` and the hypothesis
label `best_hypothesis`. When two on-scale values differ, `verdict_disagreement` is
flagged and both are shown. The worked example
`examples/VIGIA-REAL-SRL-DMZ-FTP_bundle_report_expert_en.md` shows `ABSTAIN` from the
R3 coherence check next to `MALICE` from the scorer; `r3_calibration_note` records
the reconciliation the pipeline itself made. The report does not arbitrate.

## 4. Daubert gates as recorded

VIGÍA's self-correction is **pre-emission**: a gate intercepts a candidate before it
is sealed, and the record of that interception is part of the bundle.

- **Mode 2**: `refutation_gate_log` entries (`candidate_verdict`, `gate_applied`,
  `gate_rule`, `gate_result`, `benign_hypothesis_tested`). Example: an `INTENT`
  candidate from `reason_with_llm` rejected by the Daubert Corroboration Gate
  because `n_independent_sources < 2`, emitted as `SUSPICION`
  (`examples/VIGIA-KIWI-006_bundle_report_expert_es.md`).
- **Agent audit**: `audit_trail.entries` whose `action` names a gate, downgrade or
  contradiction, plus `self_corrections_applied`.
- **EBS v1**: `decision_trace.reason_code`, `abstain_reason`,
  `caie_analysis.hard_temporal_gate`, `r3_calibration_note`,
  `caie_fractures_source` (`live_caie` means fractures were computed, not declared).

`devil_advocate` is the strongest benign explanation the analysis had to defeat.
The Refutation Protocol makes it mandatory for `INTENT` and `MALICE`. When such a
verdict is sealed without one, the report prints a GAP notice (L-022) and leaves the
verdict untouched.

## 5. The execution record

Section 6 summarizes the process evidence without listing everything: entry counts,
`chain_version` (v1 protects only `result_summary`; v2 covers the whole entry), tip
anchor presence, and a histogram sorted by count then name. The verbatim listing is
capped and says so; open the bundle for the rest.

## 6. What the reports deliberately do not do

- No derived label, not even an ENFSI bucket from `lr`: a derived label is a
  computed value, and this layer computes nothing.
- No verifier execution: the report prints the command, it does not run it, so the
  render stays a pure function of the bundle bytes.
- No translation of sealed tokens, field names or quoted text.
- No generation timestamp.

## 7. Where to go next

- `docs/DAUBERT_JUDICIAL.md` (and `_ES`): the admissibility argument in full.
- `docs/EXECUTION_MODES.md`: why the families diverged and how the web UI treats them.
- `KNOWN_LIMITATIONS.md`: L-004 (narrative as input), L-020 (no granular audit trail
  in Mode 2), L-022, L-030/L-031, L-056, L-074 (this presentation layer).
- `docs/ENGINEERING_DISCIPLINE.md` section 5: the LLM-out-of-the-loop and
  deterministic-core rules these reports are built to respect.
