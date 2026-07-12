# AUDITORIA — Coverage gap between agent and motor (raw path)

Deeper analysis of why the **agent** extracts fewer signals than the **motor** on raw
evidence, while the LLM never decides the verdict. Four parts, each verified by running
the code on this repository state. Measurements only; this document proposes no
architecture (that is B1-c, deferred).

- **Scope:** Mode 1 raw-evidence path. Agent
  (`vigia_agent.py` -> root `sift_orchestrator.py` shim -> `SIFTOrchestrator.analyze`)
  vs motor (`vigia/sift/sift_orchestrator.py::run_full_analysis`).
- **Environment note:** in this repo no `vol`/`rip.pl` binaries are on PATH, so
  `SIFTOrchestrator.__init__` builds with `self.memory = None` and `self.registry = None`
  (via `_safe_engine`, which disables an engine whose constructor fails). This is not a
  contrived state — it is the default here, and Part 4 exercises exactly that condition.

Related: `docs/AUDITORIA_SHIM_RUTEO.md` (B1 memory-first routing + B1-a fix).

---

## Part 1 + 2 — Data-loss map, quantified per evidence composition

The shim routes by **mutually-exclusive type precedence**. Measured: what the agent
**detects** (`_build_orchestrator_kwargs`) vs what it actually **processes** (which
downstream function the shim calls), per directory composition. `_analyze_memory_vol3`
and `run_full_analysis` were spied; empty files were used because the target is the
routing decision, not parsing.

| Directory | Agent **detects** | Agent **processes** | Lost |
|---|---|---|---|
| `{memory.raw}` | `memory_path` | `vol3(memory.raw)` | — |
| `{memory.raw, Security.evtx}` | `event_logs`, `memory_path` | `vol3(memory.raw)` only | evtx |
| `{memory.raw, Security.evtx, SYSTEM}` | `event_logs`, `memory_path`, `registry_hives` | `vol3(memory.raw)` only | evtx + registry |
| `{Security.evtx, SYSTEM}` | `event_logs`, `registry_hives` | `run_full_analysis(event_logs, registry_hives)` | — |
| `{Security.evtx}` | `event_logs` | `run_full_analysis(event_logs)` | — |
| `{disk.E01}` | `disk_path` | (nothing) | all (E01 not mounted) |

**Rule:** the agent-vs-motor divergence is deterministic in the evidence composition. It
appears exactly on the rows with **mixed evidence containing a memory image** (B1, the
memory-only branch short-circuits — see AUDITORIA_SHIM_RUTEO.md) and **a bare E01** (B3,
returns an error result). Without a memory image, the agent routes everything to the
motor correctly.

Additional pre-routing loss points in `_build_orchestrator_kwargs`
(`vigia_agent.py`): `maxdepth 3` (`if depth > 3: continue`), `100 files per pattern`
cap, exact hive names (`SAM`/`SYSTEM`/`SOFTWARE`/`SECURITY`/`NTUSER.DAT`), exact
extensions (`*.evtx`, `*.raw`, ...), symlinks skipped. An artifact that does not match a
glob (deep subdir, renamed hive, other extension) is never detected, so the motor never
sees it.

---

## Part 3 — Corroboration gate >=3 vs the L-036 override that compensates it

Two corroboration gates disagree. Measured with the abductive reasoner directly and with
the full agent flow (reasoner -> `_generate_narrative` L-036 override -> classify):

| Input signals | Reasoner (`_v2`) | Agent final (with L-036 override) |
|---|---|---|
| 2 primary, z = 4.5, 4.0 | `UNDETERMINED` | **MALICE** (rescued) |
| 2 primary, 2 < z <= 3 (2.5, 2.4) | `UNDETERMINED` | **INTENT** (rescued) |
| 3 primary | `MALICIOUS_INTENT_DETECTED` | MALICE |

- The reasoner requires **>=3 primary signals** (`abductive_reasoner.py:90`,
  `if len(primary) < 3: return AbductionTrace(...UNDETERMINED...)`), stricter than the
  "two independent sources" the verdict table in the runtime CLAUDE.md states for
  INTENT/MALICE.
- The agent's **L-036 override** (`vigia_agent.py::_generate_narrative`) rescues the
  2-signal cases, but only by **z-score** (>=2 signals with z>3 -> MALICE; >=2 with z>2
  -> SUSPICION). Residual zone: 2 high-**confidence** signals with z<=2 -> reasoner
  UNDETERMINED, override does not apply -> ABSTAIN.
- Using the **motor directly** (no agent), there is no override: 2 strong signals ->
  UNDETERMINED.

The system relies on a patch (L-036) to compensate a gate that is stricter than the
documented doctrine. **Severity: medium** — it fails toward ABSTAIN, not toward benign.

---

## Part 4 — Remaining silent gap: an absent engine swallows its artifact with no F7 mark

The motor marks `unanalyzed` (F7) when an engine **raises an exception**
(`run_full_analysis`, lines 415-569, one per engine). But every engine block is guarded
by `if <artifact> and self.<engine>:`. When `self.<engine>` is **None** (dependency
absent, disabled by `_safe_engine`), the block is skipped **without entering the `try`**,
so `_unanalyzed_signal` is never emitted. Example (memory, lines 402-415):

```python
402  if memory_dump_path and self.memory:
403      v = self._safe_path(memory_dump_path)
404      if v:
405          try:
406              mem_result = self.memory.analyze(...)
              ...
412          except Exception as e:
415              raw_signals.append(self._unanalyzed_signal("memory", "memory", e))
```

If `self.memory is None`, line 402 is False and nothing runs — no analysis, no
`_unanalyzed_signal`. Same pattern for `registry` (418), `eventlog` (439), `disk` (459),
`network` (474), etc.

**Measured:** `run_full_analysis(memory_dump_path=<real file>)` with `self.memory = None`:

```
signals: []
MEMORY_UNANALYZED present? False
pipeline_meta.n_pathguard_rejects: 0
```

The memory artifact disappeared with no F7 marker. In this environment `self.memory` and
`self.registry` are None by default (no `vol`/`rip.pl` on PATH), so the gap is active,
not hypothetical.

**Asymmetry:** engine present but failing -> visible (`_unanalyzed_signal` -> ABSTAIN);
engine absent + artifact present -> invisible. If other live engines contribute >=3
benign primary signals, the whole case can seal as **NOISE (exit 0)** without reflecting
that an artifact type was never processed — the "looks clean" failure mode the rest of
the project guards against.

**Severity: high** — same false-negative class as the prior P0-A/P0-B fixes, via the
"engine None" door those fixes did not cover.

---

## What the motor already does correctly (to bound the finding)

- Engine that raises an exception -> `_unanalyzed_signal` (visible). Lines 415-569.
- PathGuard reject -> `_rejected_paths` -> materialized as unanalyzed. Lines 295-300, 606-607.
- SignalOutput conversion failure -> `_signal_drops`, exposed in `results`. Lines 320, 882-885.
- Derived engines (resonance / timeline / patterns / adversarial-robust) -> `_mark_derived`,
  so they do not inflate the >=3 gate. Lines 708-773.

The gap is specific: **engine disabled by an absent dependency + a matching artifact
present = silent skip.**

---

## Priority

| Finding | Severity | Status |
|---|---|---|
| Part 4 — absent engine swallows artifact with no F7 | **High** (possible spurious NOISE) | open |
| B1 — memory-first discards mixed evidence | Medium (now ABSTAIN via B1-a) | visibility fixed; recovery = B1-c (deferred) |
| Part 3 — reasoner >=3 gate vs L-036 override | Medium (fails to ABSTAIN) | compensated by a fragile patch |
| B3 — bare E01 not mounted | Low (already visible) | honest |

---

## Honest limitation

Part 4 was verified end-to-end in the real orchestrator to the point that the artifact
disappears with no F7 mark; the "spurious NOISE" consequence is the structural result
when >=3 benign signals from other engines are present, a composition not exercised
end-to-end with real evidence (none exists in this repo). Parts 1-2 were verified at the
routing level with dummy files (which branch runs, which function is called), not through
the parsers. Part 3 and the Part 4 disappearance were run against live code.
