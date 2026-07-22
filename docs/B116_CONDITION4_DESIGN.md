# B-116 — Diseño y medición de la condición 4 (MODE C: z-scores reales)

**Fecha:** 2026-07-22
**Rama:** `claude/pending-bugs-resolution-ream8s`
**Estado:** MEDICIÓN + PROPUESTA. El gate sigue **SIN cablear** — cero callers
de producción. Nada de este documento mueve un veredicto.
**Alcance:** condición de desbloqueo 4 de B-116 ("un dry-run confirma 0 casos
MALICE verdaderos degradados") medida con unidades honestas por primera vez.

---

## 1. Qué faltaba

Los dry-runs previos alimentaban al gate con ficciones de unidad:

- **MODE A**: `z = raw_score` (raw ∈ [0,1] contra umbral z≥2.0 — inutilizable).
- **MODE B**: `z = raw_score * 4` (rescalado generoso, sin justificación
  estadística; era una cota superior optimista, no una medición).

La condición 1 de B-116 pedía z-scores reales por señal. El insumo ya existía
en el repo y no estaba conectado a esta medición:
`data/signal_calibration_dataset_20260709.json` (Tanda C — 1.004 señales
etiquetadas con ground truth por caso, construido bajo la regla L-033).

## 2. Método MODE C (`scripts/dryrun_b116_mode_c.py`)

```
z = (raw_score − mediana_benigna[evidence_type]) / (1.4826 · MAD_benigna[evidence_type])
```

- **Población benigna:** `ground_truth ∈ {NOISE, BENIGN}` → 106 señales.
- **Baseline propia** solo para tipos con n≥5 benignos: `document`,
  `file_hash`, `file_metadata`, `log_entry`, `memory_process`.
- **Fallback declarado** (sin caps silenciosos): el resto usa la baseline
  agrupada (mediana=0.050, MAD=0.050) y queda listado en el output.
- **Piso MAD=0.05** contra denominadores degenerados.
- Estadística robusta (mediana/MAD·1.4826), no media/σ: la población benigna
  es chica y con colas.
- Script de observación pura: exit 0 siempre, no escribe estado.

## 3. Resultados (corpus 202 casos evaluables)

| | MODE A (z=raw) | MODE B (z=raw·4) | **MODE C (z real)** |
|---|---|---|---|
| Pasan gate | 0 | 87 | **117** |
| Degradados | 202 | 125 | **85** |
| Degradados con expected=MALICE | 104 | 42 | **27** |

Desglose de los 27 MALICE degradados por causa raíz:

| Clase | Causa | Casos | Diagnóstico |
|---|---|---|---|
| **C1 — metadata degenerada** | `ABSTAIN_INSUFFICIENT_TOOLS` (16) | serie VIGIA-REAL-*/SRL-* y demos | TODOS los artefactos de estos casos tienen `evidence_type` ausente (cae a `default`) y `source_tool=unknown` — la cadena de fallback del gate colapsa a 1 "tool" único. Es calidad de conversión del corpus, NO doctrina del gate. Ya diagnosticado así en la entrada original de B-116. |
| **C2 — señales débiles bajo baseline agrupada** | `ABSTAIN_WEAK_SIGNALS` (5) | SRL-MAIL/RD01/RD03/RD06/WKSTN04 | raw_scores < ~0.20 → z < 2.0 contra la baseline agrupada. Puede ser debilidad real o desalineación del bucket `default`; indistinguible hasta resolver C1 (con evidence_type reales, estos casos usarían baselines propias). |
| **C3 — estructura mono-canal** | `ABSTAIN_DEPENDENT_SIGNALS` (4) + `ABSTAIN_LOW_Z_VARIANCE` (2) | FF-GENUINE-001, HMG-99999-11, CAN-009/018/046, case_003 | Casos de 3-4 señales dominadas por un canal. Tensión doctrinal real: el corpus espera MALICE donde la doctrina de diversidad (cf. techo D3-only L-051/§9.4) apunta a cap. No es un bug — es una decisión de metodología. |

**Conclusión de la medición:** la condición 4 NO se cumple hoy (27 ≠ 0), pero
por primera vez el residuo tiene causas separables y accionables, y ninguna es
"faltan z-scores" — esa condición (la 1) queda demostrada como resuelta en
modo medición por este script.

## 4. Camino propuesto al desbloqueo (en orden, cada paso con gate propio)

1. **Backfill de metadata del corpus REAL/SRL** (resuelve C1, probablemente
   reduce C2): poblar `evidence_type`/`source_tool` de esos ~20 casos desde
   los bundles/narrativas originales. Toca el corpus más validado del
   proyecto → **requiere tu autorización explícita**, con diff caso por caso
   y sin tocar `raw_score` ni labels.
2. **Re-medición MODE C post-backfill.** Gate pre-registrado: C1 = 0 y
   C2 re-clasificada (débil real vs artefacto de baseline).
3. **Decisión doctrinal sobre C3** (tuya, no de código): ¿el gate de calidad
   actúa como cap de veredicto (choca con expected=MALICE mono-canal) o sus
   checks de diversidad se degradan a WARN informativo cuando el scorer ya
   aplicó su propio Daubert Corroboration Gate? Nota: el scorer YA tiene
   corroboración de dos fuentes (vigia_scorer:1194-1240) — cablear el gate
   con caps duplicaría esa doctrina con umbrales distintos.
4. **Si y solo si 1-3 cierran:** cableo en **modo sombra** (shadow: el gate
   evalúa y LOGUEA en pipeline_meta, sin tocar veredictos) por período de
   observación, estilo B-129. Promoción a gate real solo con corrida
   comparativa 0-flips y tu firma.

## 5. Qué NO propone este documento

- No cablear nada hoy (condición 4 no cumplida; hacerlo degradaría 27 MALICE
  verdaderos a ABSTAIN).
- No "arreglar" los umbrales del gate para que pasen los 27 (eso sería
  calibrar el instrumento contra el resultado deseado — exactamente lo que
  Daubert prohíbe).
- No tocar la serie REAL/SRL sin autorización: es el corpus más validado.

## 6. Reproducibilidad

```bash
PYTHONPATH=. python3 scripts/dryrun_b116_mode_c.py
```

Baseline: `data/signal_calibration_dataset_20260709.json`
(`dataset_sha256` interno en el archivo). Política de fallback y piso MAD
declarados en el script y en §2.
