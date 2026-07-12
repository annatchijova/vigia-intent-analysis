# AUDITORIA — Shim routing: memory-first discards evtx/hives silently (B1)

Investigation of why the **agent** sometimes extracts fewer signals than the **motor**
on raw evidence, while the LLM never decides the verdict. Root cause is in the routing
layer of the compatibility shim (`sift_orchestrator.py`, the module the agent imports),
not in the LLM and not in the deterministic engine.

The original investigation below was verified against live code and one inductive routing
test. This document reports measurements only.

**Status (updated):**
- **B1** — fixed at the visibility level by **B1-a** (commit `3de3b29`): the memory-only
  branch now marks the dropped artifacts as `unanalyzed` (F7) instead of dropping them
  silently, so the verdict degrades `NOISE -> ABSTAIN` instead of sealing a spurious
  benign result. It does **not** yet recover those signals — that is **B1-c**, deferred
  as a larger architecture decision (route the other artifacts to `run_full_analysis`
  while keeping vol3 as the memory engine, merged without double-counting).
- **B2** — found **already fixed** in `_analyze_memory_vol3` (lines 774-816, prior P1-D
  fix); no code change was needed. See the B2 section for the correction.
- **B3** — unchanged; already degrades honestly (visible error, not silent).

- **Scope:** Mode 1 raw-evidence path. Agent
  (`vigia_agent.py` -> root `sift_orchestrator.py` shim -> `SIFTOrchestrator.analyze`)
  vs motor (`vigia/sift/sift_orchestrator.py::run_full_analysis`, which processes all
  artifacts together).
- **Method:** Peircean — observe the routing code (Firstness), contrast against the
  motor's all-artifacts behavior (Secondness), infer the rule (Thirdness); abduce a
  hypothesis, deduce a checkable consequence, induce with a controlled run.

---

## Firstness — the exact guard (live code)

`sift_orchestrator.py`, `SIFTOrchestrator.analyze()`, lines 164-171 (comment on 163):

```python
163  # Evidencia de memoria sin disco -> vol3 local, no necesita rip.pl
164  if memory_path and not disk_path:
165      logger.info("[SIFT_SHIM] Memory-only evidence -> vol3 local adapter")
166      try:
167          result = self._analyze_memory_vol3(str(memory_path))
168      except Exception as e:
169          logger.error("[SIFT_SHIM] vol3 memory analysis failed: %s", e)
170          result = self._error_result(str(e))
171      return self._merge_mobile_signals(result, mobile_signals)
```

The branch condition is `memory_path and not disk_path`. It does **not** test whether
`event_logs`, `registry_hives`, `mft_path`, `pcap_path`, `browser_profile`, or
`prefetch_dir` are also present. When memory is present (and there is no `disk_path`),
the shim calls `_analyze_memory_vol3(memory_path)` and `return`s immediately —
`run_full_analysis` (the motor path that consumes the other artifacts) is never reached.

## Secondness — contrast with the motor

The real orchestrator `run_full_analysis` (in `vigia/sift/sift_orchestrator.py`) consumes
the **union** of artifacts. The shim routes by **mutually-exclusive type precedence**:
memory-present short-circuits to the memory-only adapter and returns. So on the same
mixed raw directory, the motor would see evtx + registry + memory; the agent sees only
memory. The divergence is not random — it is a function of the evidence composition.

## Thirdness — the rule

The shim routes by exclusive precedence instead of by union. As soon as a memory image is
detected (and no disk image), it collapses to the vol3-only branch and returns, silently
dropping every other artifact type in the same evidence set. This produces the observed
"sometimes the agent finds less than the motor": mono-type or pre-extracted evidence ->
agent and motor agree; mixed raw evidence containing a memory image -> agent < motor.

Memory + evtx + registry hives together is exactly what a Windows triage collector
(e.g. KAPE) produces, so the dropping condition is the common composition, not an edge
case.

---

## Inductive test that confirmed H1 (dummy directory, routing only)

**Abduction (H1):** the agent detects all artifacts in the directory, but the shim's
routing processes only the memory image when one is present, discarding evtx/registry.

**Deduction:** a directory `{memory.raw, Security.evtx, SYSTEM}` must yield agent kwargs
with all three keys, yet `analyze()` must enter the memory-only branch and never call
`run_full_analysis`.

**Induction (run):** empty files were used because the target is the routing decision,
not the parsing. `_analyze_memory_vol3` and `run_full_analysis` were spied.

```python
import sys, os, shutil
from pathlib import Path
REPO = Path("/home/user/vigia-intent-analysis"); sys.path.insert(0, str(REPO))

ev = Path("rawdir"); shutil.rmtree(ev, ignore_errors=True); ev.mkdir()
(ev/"memory.raw").write_bytes(b"")      # -> memory_path
(ev/"Security.evtx").write_bytes(b"")   # -> event_logs
(ev/"SYSTEM").write_bytes(b"")          # -> registry_hives
os.environ["VIGIA_EVIDENCE_DIR"] = str(ev.absolute())

import vigia_agent as VA
kwargs = VA._build_orchestrator_kwargs(ev, {})   # what the agent detects

import sift_orchestrator as SH
calls = []
def spy_vol3(self, mp):
    calls.append(("_analyze_memory_vol3", mp))
    return {"case_id": self.case_id, "signals": [{"tool": "MEMORY_ONLY", "z_score": 0}],
            "abduction": {"best_hypothesis": "X", "is_conclusive": False}, "pipeline_meta": {}}
SH.SIFTOrchestrator._analyze_memory_vol3 = spy_vol3

import vigia.sift.sift_orchestrator as REAL
def spy_run(self, **rk):
    calls.append(("run_full_analysis", sorted(rk.keys())))
    return {"case_id": self.case_id, "signals": [], "abduction": {"best_hypothesis": "REAL"}, "pipeline_meta": {}}
REAL.SIFTOrchestrator.run_full_analysis = spy_run

res = SH.SIFTOrchestrator("H1-TEST").analyze(**kwargs)
```

**Observed output:**

```
[Deduccion 1] kwargs detectados por el agente:
    event_logs: ['rawdir/Security.evtx']
    memory_path: ['rawdir/memory.raw']
    registry_hives: ['rawdir/SYSTEM']
[SIFT_SHIM] Memory-only evidence -> vol3 local adapter
[Induccion] llamadas que hizo el shim:
    ('_analyze_memory_vol3', 'rawdir/memory.raw')
[Resultado] señales devueltas: ['MEMORY_ONLY']
```

- The agent **detected all three** artifact types (`event_logs`, `memory_path`,
  `registry_hives`).
- The shim called **only** `_analyze_memory_vol3(memory.raw)`; `run_full_analysis` was
  **never** called.
- Only the memory signal was returned. The evtx and registry hive were dropped with no
  error and no `unanalyzed` marker.

**Refutation attempts (Eco's razor), both rejected:**
- "vol3 processes the rest internally" — the spy shows `_analyze_memory_vol3` receives
  only `memory.raw`; nothing else is passed to it.
- "nobody mixes memory + evtx in one directory" — that is the standard output of a
  Windows triage collector (KAPE), i.e. the common case.

---

## Secondary findings

### B2 — vol3 is an external binary; absent/failed -> ALREADY handled (no fix needed)

`_analyze_memory_vol3` runs Volatility3 via `_vol3_run`, which shells out to the `_VOL3`
binary:

```python
71  _VOL3 = str(Path(sys.executable).parent / "vol")
     ... (fallback) ...
73  _VOL3 = "vol3"
```

In this environment no `vol`/`vol3`/`volatility3` binary is on PATH
(`which vol vol3 volatility3` -> none).

**Correction (verified in live code, §4.1):** the "zero signals looking benign" risk is
**already handled**. `_analyze_memory_vol3` lines 774-816 (prior fix, "auditoria FN,
P1-D") compute `any_plugin_ok = info["ok"] or pslist["ok"] or netscan["ok"] or
malfind["ok"]`; when no plugin ran it returns `best_hypothesis="UNANALYZED_ARTIFACT"`
(`error="VOL3_UNAVAILABLE"` when stderr shows "no such file"/"not found"), which maps to
ABSTAIN in the agent — not to a benign NOISE. The earlier draft of this section flagged
B2 as an open finding because that guard had not been read to completion; it is closed.
No code change was made for B2.

Note on composition with B1: on a mixed directory where vol3 is unavailable, the memory
branch now yields `UNANALYZED_ARTIFACT` (from the P1-D guard) **and** the B1-a marks flag
the dropped evtx/registry as `unanalyzed` — so the whole directory degrades to ABSTAIN
with an explicit list of what was not analyzed, instead of a silent benign verdict.

### B3 — E01 disk image without prior mounting -> zero signals

`analyze()`, lines ~320-331: a bare `.E01` reaching `disk_path` with no extractable
`run_kwargs` returns an `_error_result` ("E01 requires prior mounting") with no signals.
The agent cannot analyze an unmounted E01 directly; it needs `ewfmount` + hive/log
extraction first, then the artifacts passed explicitly.

---

## Field test to confirm on LaBestia (falsifiable, real evidence)

On a real raw case where the agent "finds nothing" or less than the motor:

1. Run the agent on the full directory (memory + evtx + hives). Expect: only
   memory-derived signals (or zero if vol3 is unavailable / image not a RAM dump).
2. Run the agent again pointing `--evidence` at **only** the evtx file (a directory with
   just the logs, no memory image). Expect: evtx-derived signals appear.
3. Run once more pointing at **only** the registry hives. Expect: registry-derived
   signals appear.

If steps 2-3 surface signals that step 1 did not, B1 is confirmed on real evidence: the
artifacts are analyzable, and it is the memory-first routing in step 1 that suppressed
them. The asymmetry (whole-directory < sum-of-parts) is the signature of B1.

---

## Honest limitation

This was verified at the **routing** level (which branch runs, which downstream function
is called), which is pure deterministic code, using dummy files. It was **not** verified
end-to-end with real raw evidence through the parsers, because no raw evidence
(memory image, evtx, hives, E01) is present in this repository — the corpus is JSON.
The field test above closes that gap on LaBestia. B2's "binary absent" leg was confirmed
here (no vol3 on PATH); the "image rejected" leg is read from code, not exercised.
