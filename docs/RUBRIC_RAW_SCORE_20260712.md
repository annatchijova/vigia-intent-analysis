# raw_score rubric — proposed input for the data re-scoring session (CAN-008/046/047)

## Doctrine (verdict-independent by construction)

`raw_score` answers ONE question: **how strongly does this observation, taken at face
value, indicate a malicious act?** — approximately P(observation | malicious act) vs
P(observation | benign world). It must NOT encode:

- **channel fabricability** — that is `EVIDENCE_PROFILES.spoofability` (the engine
  multiplies by `(1 - spoofability)`); scoring it into raw double-counts the discount;
- **evidentiary importance** — that is `base_weight`;
- **distance to the 0.33 MALICE threshold** — encoding that is circular calibration,
  the exact vice the scope doc forbids.

Derivation sources: (a) the corpus-wide empirical distribution of raw per
evidence_type × expected class (`raw_dist.py` / `raw_dist.json`, 198 cases,
~900 artifacts); (b) same-archetype comparables authored elsewhere in the corpus.

## Empirical grounding (what the corpus already means by raw values)

| Corpus fact | Number | Semantics established |
|---|---|---|
| memory_process in MAL-expected cases | n=117, median 0.92, q25 0.85 | hard technical attack signal ≈ 0.85–0.92 |
| kernel_structure in MAL cases | n=3, median 0.85 | same band |
| file_hash in MAL cases | n=16, median 0.88 [0.82–0.95] | hash-based hard proof ≈ 0.85+ |
| "clean/expected" observations (clean memory 0.05, EWF entropy 0.05, documents 0.00, BEN file_hash med 0.02) | 0.00–0.10 | **raw ≤ 0.10 means "observation is clean or expected"** |
| CAN-008 decoy psexec | 0.65 | noisy-but-ambiguous ≈ 0.6–0.7 |

The inverted artifacts (0.05–0.07) therefore currently *assert cleanliness* of the
very signals their case narrative declares as the attack. This is a data-entry
inversion, not a conservative judgment.

## Anchor bands

| Band | raw | Meaning | Real corpus anchors |
|---|---|---|---|
| Pathognomonic | 0.85–0.97 | No coherent benign generator of this observation | Zeus inline NT hooks 0.97 (VIGIA-REAL-NROMANOFF); ftrace hooking of 18 syscalls 0.96 (VIGIA-LINUX-004); svchost 8MB RWX + PE header unbacked 0.90 (CAN-038); hollowing confirmed 0.88 (case_003/FF-GENUINE-001); 31 RWX unbacked procs 0.93 (VIGIA-REAL-SRL-ADMIN) |
| Strong indicator | 0.65–0.85 | Rare benign alternatives exist but are strained | parent cmd.exe for svchost 0.88 (VIGIA-FN-003); parent explorer.exe 0.85 (case_020); psexec decoy 0.65 (CAN-008); FLARE-On packed PE entropy 7.47 → 0.82 |
| Ambiguous | 0.40–0.65 | Benign generator about as plausible | unknown 'cron' binary entropy 7.4 → 0.62 (VIGIA-LINUX-005, later resolved benign Go) |
| Weak/contextual | 0.10–0.40 | Mostly context; benign default | Nokia sampled entropy 5.2 → 0.20; git 0.16–0.21 (BEN) |
| Near-noise | 0.00–0.10 | Clean or expected observation | clean memory 0.05 (FP-CULTURAL-CLEAN); EWF compression entropy 7.95 → 0.05 (NPS-2010) |

## Assignments for the inverted artifacts

| Case | Artifact | Observation | Current raw | Rubric raw | Justification (comparables, not threshold) |
|---|---|---|---|---|---|
| CAN-008 | a090_03 (→kernel_structure per D-5) | unsigned kernel driver, 12 SSDT hooks, loaded pre-decoy | 0.05 | **0.90** | SSDT hooking has no benign generator; comparables 0.88 (case_111), 0.96 (LINUX-004), 0.97 (NROMANOFF) |
| CAN-046 | a024_hash (→file_hash per D-5) | hash matches no repo package + entropy 7.8 | 0.06 | **0.72** | NOT pathognomonic: in-corpus benign counterexample LINUX-005 (custom Go binary, entropy 7.4, no repo match, authored 0.62). Strong-indicator band, not 0.9. |
| CAN-047 | a026_process | svchost .text RWX, hollowed=true | 0.07 | **0.88** | Twin CAN-038 authored 0.90 for the same physical signal; ROCBA 0.85; case_003 0.88 |
| CAN-047 | a026_parent | parent rundll32 instead of services.exe | 0.07 | **0.80** | FN-003 0.88, case_020 0.85; log-channel discount belongs to the log_entry profile (sp=0.85), not to raw |

## Dry-run results (real engine `_vigia_score`, in-memory, D-5 retypes applied)

| Case | baseline | retype only | retype + rubric | Verdict path |
|---|---|---|---|---|
| CAN-008 | SUSPICION 0.1953 | SUSPICION 0.1874 | **MALICE 0.4359** | cross-domain branch (4 domains, 4 artifacts), 0 fractures, boost 0.0 |
| CAN-046 | SUSPICION 0.2221 | SUSPICION 0.2203 | **SUSPICION 0.3085** (also with timestomp_detected=True: 0.3085) | does NOT reach MALICE — honest result |
| CAN-047 | SUSPICION 0.1909 | SUSPICION 0.1970 | **MALICE 0.4233** | cross-domain branch (4 domains, 4 artifacts), 0 fractures, boost 0.0 |

CAN-046 sensitivity (a024_hash as file_hash): crosses 0.33 only at raw ≥ 0.90 —
inside the pathognomonic band that the LINUX-005 counterexample forbids. Conclusion:
CAN-046 cannot honestly reach MALICE by re-scoring; it is a CAN-026-criterion
candidate (accept SUSPICION / relabel expected), or needs genuinely new evidence.

Trap confirmed empirically: rubric WITHOUT retype gives CAN-046 MALICE at exactly
0.3330 — riding the wrong profile (memory_process w=0.30/sp=0.15 for a hash/static
observation). Retype and re-score must land as one edit, as the scope doc mandates.

Corpus effect if applied: 153/193 → 155/193 (only these 3 case files change; no
engine change, zero side effects on other cases).
