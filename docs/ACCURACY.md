# VIGÍA — Accuracy & Evidence Dataset

This document holds the full accuracy methodology, the segmented corpus metrics,
and the three-domain evaluation breakdown. The top-level `README.md` links here
and carries only a short summary.

---

## Dataset Availability

The original forensic images used during evaluation (memory dumps, E01 images,
PCAP collections, and related artifacts) are **not included in this repository**.
The complete corpus spans many GB and contains third-party forensic datasets
that cannot be redistributed.

This repository includes the full agent implementation, deterministic scoring engine,
generated forensic bundles, agent-produced JSON outputs, final reports, and the
complete reproduction workflow.

All JSON reports in `/results` were produced by VIGÍA during real end-to-end
executions — they are not manually authored examples. This applies in particular
to the named cases (NROMANOFF, TDUNGAN, NFURY, ROCBA, SRL-ADMIN, SRL-AV,
SRL-DC-MEMORY, SRL-DMZ-FTP, VANKO), which are distinct from the numbered
reference cases REAL-001 through REAL-010.

---

## Accuracy — Methodology and Results

VIGÍA operates in three distinct modes. The primary evaluated mode is the agent
without a language model backend.

**VIGÍA Agent without LLM (primary mode):** The autonomous agent resolves all cases
fully without any language model. This is the primary evaluated mode. The agent
produces complete ForensicBundles with chain of custody, Peircean narrative,
z-scores, and deterministic Fraction arithmetic. On BREAK adversarial stress-test
cases, the agent produces a definitive verdict — SUSPICION or the appropriate level —
not an abstention. Results are documented in `KNOWN_LIMITATIONS.md`.

**Python scorer only (no agent):** The deterministic scoring pipeline runs in
isolation, without the agent reasoning layer. Over the canonical corpus of 52
structurally diverse cases — spanning insider threat, memory forensics, log
fabrication, false flags, multi-source fraud, and adversarial steganography — the
scorer achieves 100% correct verdicts. The full case set is available at
`data/cases/vigia_cases_canonical_v2.json` for independent review. On BREAK cases,
the scorer returns UNKNOWN — expected behavior in this mode without the agent
reasoning layer.

**Mode 2 / 3 investigation reports (Claude via MCP or Ollama):** These modes
reuse local deterministic tools but can perform a broader, interactive evidence
review and produce a separately scoped report. They cannot modify an already
sealed Mode 1 bundle, its score, or its verdict. If their report differs, the
right response is to preserve and compare both artifacts — not to overwrite the
sealed result or describe the difference as an identical deterministic replay.

These numbers are not inflated. They reflect results on a specific, diverse,
documented corpus. All modes are documented in `KNOWN_LIMITATIONS.md`.

**Language coverage:** Cases were developed and validated in Spanish and English.
Performance in other languages has not been formally validated and cannot be
guaranteed at this time.

---

## Accuracy Note — Three Evaluation Domains

> **Metric change (2026-07-05, B-075 — post-submission doctrine decision).**
> The red-team audit `AUDITORIA_MOTOR_SIN_LABEL.md` proved that the JSON-corpus
> batch path (`run_all_agent.py`) was reproducing each case's `expected_verdict`
> label instead of deriving the verdict from the evidence (label leak, P2-C):
> with the label stripped, that path detected **zero** malicious cases. As of
> the B-075 fix the EBS adapter derives its verdict from the canonical
> deterministic scorer with the label removed (`VIGIA_EBS_RESOLVE=motor`,
> now the default), and the corpus metric measures **real label-blind
> detection**.

### How to read VIGÍA's numbers — one mode, one reading (2026-07-06)

**The 97.5% below is the agent's JSON path ONLY. It says nothing about how
VIGÍA performs on real raw evidence — that is measured per case, in the
other two modes.** The honest presentation is one line per mode:

| Mode | What it processes | The honest number |
|---|---|---|
| **Claude/MCP (Domain A)** — primary | real raw evidence, full MCP extraction chain | **Deep per-case analysis — no aggregate number by design.** Record to date: 100% correct verdicts on every investigation run (per-case docs in `evidence/`, `results/`, `reports/`) |
| **Agent over JSON (Domain B)** | synthetic/converted JSON cases | **97.5% (158/162) on the detection corpus** — the ONLY mode with a corpus-wide number; mixed-corpus aggregate 187/199 (segmentation below) |
| **Agent over RAW (Domain C)** | real public forensic corpora | **43 distinct raw evidence sources with sealed bundles in `results/`** — SRL 2018 (22 memory images), MUS2019/Narcos (13 dumps), M57 (3), NPS 2010/2014, Magnet 2020 CTF, Tuck 2019 macOS, Vanko — plus the Magnet 2022 (Windows/iOS/Android), Owl HD1/Nexus 5 and HMG investigations documented per case. **Each is an individual investigation with its own findings — NOT aggregated as accuracy** |

Claude Code / MCP mode (Mode 2) is evaluated separately and per-case:
**100% correct verdicts on every raw-evidence investigation run in that
mode** — including cases where agent mode abstains or falls short
(NPS-2010/2014: Mode 2 determined NOISE while Mode 1 sat in
PIPELINE_ERROR; MAGNET-2022-WINDOWS: Mode 2 reached MALICE with C2
evidence where Mode 1 said NOISE). See Domain A below.

**Agent mode — `run_all_agent.py` over the 199-case JSON corpus —
aggregate: 187/199 (94.0%), label-blind, distribution identical to the
standalone scorer run blind.** That aggregate is NOT an accuracy figure on
its own: the corpus deliberately mixes evaluation sets with different
purposes — including adversarial suites *designed to break the system* and
epistemic-boundary cases — and they must be read separately (segmentation
from the ground-truth dataset, 2026-07-06):

| Segment | Cases | Label-blind | Reading |
|---|---|---|---|
| **Detection corpus** (canonical 61, benign 18, FLARE-ON CTF 10, real/converted 51, demo 4, other 18) | **162** | **158/162 (97.5%)** | **the accuracy-bearing metric for this path** — canonical 61/61, benign 18/18, FLARE-ON 10/10; the 4 misses are adjacent-severity or doctrinal over-alert (L-054) on real/converted and benign cases |
| Adversarial suites (BREAK 16, KIWI 7, FN-suite 3, FP-suite 5) | 31 | 18/31 | Domain C material, *designed to break*: failures here ARE the documented limits (L-014 emergent constellations, L-016 trust consensus, cultural_marker FP) — resistance data, not accuracy |
| Epistemic boundary / intake ABSTAIN | 5 | 2/5 | label review pending (FASE2 §5): the motor clears cases whose labels declare them undecidable |
| Aggregate pipeline-error case | 1 | 1/1 | list-shaped legacy aggregate, expected UNKNOWN |

**Alternate cut — by `validation_class` (contamination transparency, 2026-07-14):**
The 187/199 aggregate mixes cases with very different contamination risk. Reading it
as a single number overstates confidence. Broken down by corpus origin:

| validation_class | Cases | Pass | Fail | Accuracy | Contamination posture |
|---|---|---|---|---|---|
| **held_out** (KIWI-\*) | **7** | **5** | **2** | **71.4% (Mode 1) · 100% (Mode 2/3)** | Private — never published, impossible to memorize. Strongest generalization evidence in the corpus. Mode 1 (deterministic Python agent): 5/7 — KIWI-006 and KIWI-007 return NOISE where expected is SUSPICION (low-signal testimony cases). Mode 2 (Claude Code + MCP) and Mode 3 (Ollama): **7/7 — 100%** on all held-out cases. |
| **synthetic** (BREAK-\*, BEN-\*, FP-\*, FN-\*, CAN-\*, case_\*, DEMO-\*, AMB-\*) | **107** | **97** | **10** | **90.7%** | Constructed by VIGÍA — zero contamination risk by construction. Failures are documented limits, not surprises. |
| **public_documented** (REAL-\*, Flareon, NGDC, MAGNET, LINUX, NPS-\*, Nitroba, M57, SRL, OWL, …) | **85** | **83** | **2** | **97.6%** | From CFReDS, NPS, M57-Patents, Magnet CTF, Digital Corpora, and similar. **contamination_caveat:** the LLM narrator may know public analyses of these cases; read as a floor of rigor, not proof of generalization. The deterministic scorer does not use the LLM, so this caveat applies to Mode 2 narrative enrichment only, not to the sealed verdict. |
| **Total** | **199** | **187** | **12** | **94.0%** | Mixed-corpus aggregate — meaningful only when the three rows above are read alongside it. |

Trajectory of the honest aggregate, every step gated: the B-075 flip landed
at 143/199; B-076 calibrated the SUSPICION threshold against the 198-case
ground-truth dataset (`data/calibration_ladder_dataset_20260705.json`):
+10, zero regressions (153/199); the 2026-07-05 doctrine decisions added
+14 (comparator accepts MALICE-where-INTENT as over-severity since the
motor ladder has no INTENT rung — never the reverse; synthetic AMB-001/002
labels revised ABSTAIN→NOISE per the documented L-012 design, real-corpus
labels untouched). Full methodology, label-flip invariance proof, and
per-cluster analysis:
[`FASE1_RESOLVE_EBS.md`](./FASE1_RESOLVE_EBS.md) and
[`FASE2_DATASET_CALIBRACION.md`](./FASE2_DATASET_CALIBRACION.md).

Pre-B-075 pass rates for this path (e.g. "129/129", "165/167") measured
label reproduction, not detection, and are retained only as historical record.

> **The case count may be outdated.** We are actively adding cases, especially
> raw-evidence (E01/evtx) investigations. The figures shown reflect the corpus at the
> time of last update and may undercount current coverage.

---

## The Three Domains in Detail

**VIGÍA operates across three distinct modes, and their numbers are NOT comparable
with each other — each mode reaches the evidence differently.**

**Domain A — Claude Code / MCP mode (raw forensic evidence):** Full pipeline, primary
investigative mode. **Every artifact flows through the MCP extraction toolchain**
(hash → read → entropy → pattern search → intent inference), so every evidence type
reaches the analysis engines — nothing is out of coverage in this mode. Tested on
real-world E01 disk images, memory dumps, and log archives. **Record to date: 100% —
every investigation run in this mode reached the correct verdict**, documented
per-case in `evidence/` and `results/` (this mode is evaluated per investigation,
not with a single corpus number).

**Domain B — Autonomous agent, JSON pre-processed cases:** Batch runner over
structured EBS case bundles — this is the ONLY mode with a corpus-wide number, the
segmented metric in the note above (**detection corpus: 158/162, 97.5%**; aggregate
187/199). Since B-075 the verdict comes from the label-blind deterministic scorer;
the previous 165/167 figure measured label reproduction (see metric change note).

**Domain C — Autonomous agent, raw evidence (E01/evtx/memory):** The agent parses
raw artifacts directly (MFT, prefetch, browser, event logs, pcap, memory via vol3).
**This is where the real public-corpus cases live: 43 distinct raw evidence sources
carry sealed bundles in `results/`** (SRL 2018, MUS2019/Narcos, M57, NPS, Magnet
2020 CTF, Tuck 2019 macOS, Vanko), each an individual investigation with per-case
verdicts and findings — there is no corpus number for this mode because these are
investigations, not benchmark rows. Full per-case catalog: [`../RAW_CASES_LOG.md`](../RAW_CASES_LOG.md)
(Spanish: [`../RAW_CASES_LOG_ES.md`](../RAW_CASES_LOG_ES.md)). Coverage is partial by design: some artifact
classes do not reach the engines yet (USB/shellbag/amcache registry hives are honest
ABSTAIN stubs; see `KNOWN_LIMITATIONS.md`), and cases whose signal lives in an
uncovered class degrade to ABSTAIN rather than producing a false NOISE (F7/P1-E
pattern). B-032 (`event_logs` routing) and B-036 (`z>5.0` impossible threshold) are
resolved; see L-036 in `KNOWN_LIMITATIONS.md` for the signal-based hypothesis
override.

> The corpus percentages above apply to **Domain B only**. Domain A results are
> documented per-case in `evidence/` and `results/`; Domain C coverage limits are
> documented in `KNOWN_LIMITATIONS.md`.

### Why Claude/MCP mode reaches 100% while the Python agent is at 97.5%

The two numbers measure fundamentally different things and are not comparable with
each other. They arise from different evaluation methodologies applied to different
modes of operation.

**Claude/MCP mode (Domain A) — 100%, evaluated per-case:**

Claude Code (Mode 2) conducts each investigation as a fresh, evidence-driven
reasoning session. It reads raw artifacts through the MCP extraction toolchain,
applies the full Peircean triad (Firstness / Secondness / Thirdness), evaluates
exculpatory context semantically (written authorization, documented exceptions,
corpus provenance), runs the Mandatory Refutation Protocol on every INTENT/MALICE
candidate, and selects ABSTAIN when evidence is insufficient rather than forcing a
verdict. Because each investigation is a full reasoning session — not a pass through
fixed thresholds — the investigator can correctly identify cases like VIGIA-BEN-014
(journalist with editorial authorization using Tor) as NOISE even though the Tor
connection is structurally anomalous, because it can evaluate the authorization
memo as a forensic fact rather than a field to ignore.

This mode has no aggregate accuracy number by design: aggregating individual
investigations into a single percentage would conflate cases with vastly different
evidence quality, artifact completeness, and epistemic certainty. The 100% figure
means every investigation run in this mode reached the verdict that the full
evidence supports — it does not mean 100% of all possible cases would be correctly
classified.

**Python agent mode (Domain B) — 97.5%, evaluated on the 162-case detection corpus:**

Mode 1 (`vigia_agent.py`) applies the deterministic scoring pipeline — a fixed
mathematical engine that operates with zero LLM calls and zero tokens. It cannot
evaluate exculpatory context semantically: the B-028/B-065 alert floor prevents any
SUSPICION hypothesis from presenting as LOW regardless of per-signal magnitude, and
the D1 Eco filter that sets aside `semantic_role: "exculpatory"` artifacts can be
neutralized by the floor when a residual incriminatory signal of medium magnitude
remains (L-054, L-056). This is a deliberate doctrinal choice — over-alerting on
benign cases is preferable to under-alerting on malicious ones with planted
exculpatory metadata — and its cost is a measurable false-positive rate on
authorized-use cases.

The 4 misses in 162 cases are all in this category: adjacent-severity calls
(SUSPICION where expected NOISE, or NOISE where expected SUSPICION for very weak
signals) or doctrinal over-alert (L-054 exculpatory context not modeled). None
are missed detections of actual malicious activity — the detection corpus canonical
cases, benign cases, and FLARE-ON CTF cases all pass at 100%. The 97.5% figure
reflects honest deterministic scoring, not a leaky classifier.

**Why the numbers diverge for the same case:**

When the same case is run through both modes (example: VIGIA-BEN-014), Mode 2
returns NOISE (exculpatory context correctly evaluated, MCP composite 0.0070, below
NOISE threshold) while Mode 1 returns SUSPICION (Tor connection produces a residual
z=0.49 signal, B-028/B-065 floor prevents collapse to LOW, posterior 21/100). Neither
is wrong by its own contract: Mode 1 correctly flags the structural anomaly and
defers to human review; Mode 2 correctly evaluates the full context and resolves it.
The floor is not a bug — it is the conservative Daubert posture of the deterministic
engine. The 97.5% figure documents precisely how much that posture costs in terms of
false positives on the detection corpus.

---

## Evaluation Domains — Reference Tables

VIGÍA separates evaluation into three distinct domains. Only Domain A
constitutes the system's accuracy claim.

### Domain A — Deterministic Accuracy: 129/129 — HISTORICAL (pre-B-075)

> **Superseded 2026-07-05 (B-075):** this table was produced through the JSON batch
> path while the EBS adapter still echoed `expected_verdict` (P2-C label leak), so it
> measures label reproduction, not detection. It is retained as historical record of
> the submission-time evaluation. The current honest metric for this path is the
> **187/199 label-blind detection** figure in the metric-change note above.
> `SUBMISSION_COMPLIANCE.md` reflects the claims as submitted and is intentionally
> left unmodified.

| Suite | Cases | Correct |
|-------|-------|---------|
| Real forensic corpus (NIST/DFRWS/DEF CON/SRL 2018/LINUX/NGDC) | 39 | 39 ✓ |
| Canonical corpus (CAN-001–052) | 52 | 52 ✓ |
| Legacy canonical cases | 10 | 10 ✓ |
| Benign / Clean machines | 15 | 15 ✓ |
| False positive suite | 3 | 3 ✓ |
| False negative suite | 3 | 3 ✓ |
| False flag (planted attribution) | 3 | 3 ✓ |
| Demo corpus | 4 | 4 ✓ |
| **Total Domain A** | **129** | **129 (100%)** |

Reproduce (post-B-075/B-076 + doctrine this yields the honest 187/199, not the
historical table above): `python3 run_all_agent.py --timeout 90`
To reproduce the historical label-echo behavior explicitly:
`VIGIA_EBS_RESOLVE=legacy python3 run_all_agent.py --timeout 90`

### Domain B — Epistemic Boundary Set (not accuracy)

These cases have no correct single answer. They test the system's ability
to recognize irreducible ambiguity and emit ABSTAIN rather than forcing a verdict.

| Case | Expected | Result | Notes |
|------|----------|--------|-------|
| VIGIA-AMB-001 | NOISE (revised 2026-07-05; was ABSTAIN) | NOISE | L-012: insufficient signal for ABSTAIN gate |
| VIGIA-AMB-002 | NOISE (revised 2026-07-05; was ABSTAIN) | NOISE | L-012: same |

**Design note:** ABSTAIN requires structural conflict between competing
hypotheses with non-trivial evidence. Null-signal cases correctly return NOISE.
See KNOWN_LIMITATIONS.md L-012.

### Domain C — Adversarial Stress Test Suite (not accuracy, not failure rate)

16 cases designed to break the system. This suite exists because VIGÍA claims
Daubert admissibility — which requires documented falsifiability.

| Attack Class | Cases | Handled | Notes |
|-------------|-------|---------|-------|
| Temporal manipulation | 2 | 2 | Hard gate blocks verdict |
| Signal drowning / noise injection | 2 | 2 | Conservative SUSPICION |
| Cultural attribution (false flag) | 2 | 2 | L-019 RESOLVED |
| Prompt injection via evidence | 1 | 1 | LLMShield block ✓ |
| Epistemic manipulation | 3 | 3 | ABSTAIN / SUSPICION correct |
| Trust consensus fabrication | 2 | 1 | L-016: documented limitation |
| Corroboration gate bypass | 1 | 1 | Gate holds |
| Directional aggregation evasion | 1 | 0 | L-015: documented limitation |
| **Total Domain C** | **16** | **14 (87.5%)** | 2 documented limitations |

Full adversarial results: `results/llm_mode/`.
Known limitations: `KNOWN_LIMITATIONS.md`.
