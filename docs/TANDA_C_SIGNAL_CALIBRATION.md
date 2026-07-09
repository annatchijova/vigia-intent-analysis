# Tanda C — Dataset de calibración a nivel señal (precondición A3/A4)

**Generado:** 2026-07-09 · **Estado:** dataset construido; A4 desbloqueado, A3 bloqueado por escasez de datos (cuantificada).
**Artefacto:** `data/signal_calibration_dataset_20260709.json`
**Generador:** `scripts/build_signal_calibration_dataset.py` (reproducible, `dataset_sha256`)
**Test:** `tests/test_signal_calibration_dataset.py`

---

## 1. Por qué existe

Cuatro ítems del Grupo A declaran el mismo bloqueo — *"no tocar sin dataset
etiquetado"* (regla **L-033**: ≥20 señales reales con ground truth antes de
mover gamma o re-fitear perfiles). La hipótesis económica del plan
(`PLAN_ABDUCTIVO_PENDIENTES_20260705.md` §Fase 2) es que **el dataset es el
ítem**, no los cuatro fixes. Este es ese dataset, a nivel señal.

No se fabrica ningún dato: se extraen las señales que el motor determinista
realmente produce sobre el corpus (199 casos) + los 4 fixtures red-team, cada
una etiquetada con el `expected_verdict` de su caso.

## 2. Dos substratos disjuntos

La cadena gamma×FRS y los perfiles de evidencia operan en caminos distintos del
motor, sobre conjuntos de `evidence_type` **disjuntos**. El dataset los separa
por `signal_source`:

| `signal_source` | Fuente | evidence_types | Sirve a |
|---|---|---|---|
| `ebs_scorer` | `vigia_scorer._vigia_score(...)["effective_trusts"]` (salida fiel del motor) | `log_entry`, `memory_process`, `cultural_marker`, `file_timestamp`, … | **A4** — re-fit de `EVIDENCE_PROFILES` (spoofability/weight), B-069 |
| `sift_raw` | `results/agent_batch/*_agent_bundle.json` → `pipeline_results.signals`, filtrado a clases con gamma | `windows_event_log`, `event_log`, `memory`, `mft`, `registry`, `prefetch`, `browser`, `usb`, `shellbag`, `amcache`, `network` | **A3** — gamma×FRS (L-033/L-034/L-038) |

`gamma` se anota importando la función real
`vigia.sift._math_utils.apply_artifact_reliability` — **no** se re-lista la
tabla (evita drift). Los registros `sift_raw` incluyen `z_score`, `gamma_static`
y `z_post_gamma = z · gamma`, más `n_same_type_in_case` (tamaño del grupo FRS).

## 3. Cobertura medida (2026-07-09)

| Substrato | Registros etiquetados | Polaridad (incul./benigna) | L-033 ≥20 + ambas polaridades |
|---|---|---|---|
| `ebs_scorer` (A4) | **979** | 858 / 121 | ✅ **LISTO** |
| `sift_raw` (A3) | **7** | 7 / 0 | ❌ **NO listo** |

- **EBS (A4):** 979 señales sobre 8+ tipos (`log_entry` 337, `memory_process`
  162, `binary` 59, `cultural_marker` 45, …), ambas polaridades. Distribución de
  ground truth: MALICE 482 / SUSPICION 234 / INTENT 142 / NOISE 97 / ABSTAIN 15
  / BENIGN 9.
- **SIFT (A3):** solo 7 señales, en 2 casos (`VIGIA-MAGNET-2022-WINDOWS`,
  `VIGIA-MAGNET-2020-WINDOWS`), **todas MALICE** — sin clase benigna.

## 4. Hallazgo y consecuencia (honesto)

> **Construir el dataset desbloquea A4, pero confirma que A3 (gamma) sigue
> bloqueado — no por falta de ingeniería de datos, sino por escasez de evidencia
> cruda real en el corpus.**

- **A4 (B-069, re-fit de perfiles):** la precondición L-033 está satisfecha. Se
  puede proceder al re-fit conjunto perfiles+umbrales **detrás del gate
  comparativo obligatorio** (patrón B-069: medir; si empeora, NO aplicar).
- **A3 (gamma×FRS, L-033/L-034):** **permanece bloqueado**. 7 señales de una sola
  polaridad no permiten calibrar el descuento gamma sin sobreajustar. Calibrar
  ahora violaría la propia regla L-033. La vía de desbloqueo es de
  **adquisición de datos**, no de ingeniería: el corpus necesita más casos de
  disco crudo con evidencia `event_log`/`windows_event_log` etiquetada (idealmente
  con casos benignos y de baja severidad, no solo MALICE), no más código.

Esto no es una regresión ni un fracaso: es la regla L-033 funcionando. El
dataset transformó un bloqueo declarado ("no hay dataset") en un bloqueo
**cuantificado y direccionable** ("faltan ~13+ señales gamma reales, con clase
benigna").

## 5. Cómo consumirlo

```bash
# Regenerar (idempotente salvo timestamp/hash si cambió el corpus):
PYTHONPATH=$(pwd) python3 scripts/build_signal_calibration_dataset.py \
    --output data/signal_calibration_dataset_YYYYMMDD.json
```

Cada registro trae `case_id`, `ground_truth`, `evidence_type`, los scores
relevantes y — para `sift_raw` — la anotación gamma. El bloque `coverage`
declara los flags `L033_ready_for_A4_profiles` y `L033_ready_for_A3_gamma`
derivados de los conteos (el test los verifica coherentes, no hard-codeados).

## 6. Relación con otros datasets

- `data/calibration_ladder_dataset_20260705.json` — per-**caso** (motor ciego vs
  expected), para el **umbral del ladder** (B-076). Distinto nivel.
- `data/calibration_dataset.json` — formato NLP KDE/Ledoit-Wolf de
  `fit_calibration.py` (LikelihoodEngine), hoy **sintético**. Distinto motor.
- Este dataset — per-**señal**, para gamma (A3) y perfiles (A4).
