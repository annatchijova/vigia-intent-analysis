# Auditoría L-040 — math.exp/math.log en likelihood_ratio.py: análisis formal

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Tag de restauración:** `pre-l040-audit-20260703-012151`
**Alcance:** `vigia/core/likelihood_ratio.py` y todo camino por el que su salida
(float IEEE 754) alimenta un veredicto, una etiqueta ENFSI o un registro sellado.
**Motivación:** L-040 está documentado como "empíricamente seguro en 21 casos
reales (0 verdict flips), monitoring only" sin análisis formal. Post-tanda 1
(reasoner funcionando), se pidió el análisis exhaustivo.
**Método:** lectura de código + referencia exacta `Decimal` (prec=50, misma
fórmula) + reproducción empírica. Todo hallazgo cita `archivo:línea`; toda
divergencia tiene valores exactos reproducibles.
**Acción tomada:** NINGUNA sobre el código. Solo investigación y este documento.

---

## Resumen ejecutivo

1. **La afirmación empírica de L-040 se confirma y se extiende.** Sobre los 33
   casos reales que hoy matchean los prefijos de la evaluación original (eran
   21 el 2026-06-30): **0 verdict flips**, máxima divergencia float-vs-exacto
   `|Δposterior| = 1.39×10⁻¹⁶` (≈1 ulp). El sweep aleatorio de 3.000
   inferencias (hasta 60 señales) tampoco produce ningún flip
   (max Δ = 1.70×10⁻¹⁶).

2. **Pero los flips son construibles — y se construyeron.** Con búsqueda
   adversarial 2D (z × confidence) se encontraron inputs concretos donde float
   y exacto **discrepan de veredicto**:
   - etiqueta ENFSI: `'limited'` vs `'weak'` (borde LR=2) y `'limited'` vs
     `'moderate'` (borde LR=10);
   - **decisión del risk layer: ACCEPT vs ABSTAIN** — el float aterriza
     exactamente en el punto medio de cuantización (posterior 0.9499995) y el
     ROUND_HALF_EVEN decide distinto que el valor exacto.
   Son puntos de medida cero (hay que fabricar el input al ulp), pero para
   Daubert importa que *existen* y están ahora documentados con reproducción.

3. **Hallazgo nuevo, más grave que L-040: `math.exp` sin guard crashea el
   pipeline** (`likelihood_ratio.py:218`). Con 158+ señales z=3/conf=1 (o **57
   señales z=5** vía el adaptador de `pipeline.py`, que usa `z_cap=10` por
   defecto), `combined_log_lr > 709.78` → `OverflowError: math range error` →
   la fase de Segundidad de Mode 4 muere. El corpus ya tiene un caso de 101
   artefactos (VIGIA-BREAK-014). Propuesto como **B-051**.

4. **P0-001 NO cubre L-040.** Son fronteras distintas: P0-001 cuantizó la
   reconversión float→Fraction en el boundary SIFT→gamma y en el timeline;
   `likelihood_ratio.py` consume `SignalOutput.z_score` crudo por un camino
   que no pasa por ninguno de esos dos puntos. Además hay al menos 5 paths
   float adicionales no cubiertos que alimentan veredicto/registro (§4).

5. **Alcance real de L-040, corregido:** `likelihood_ratio.py` **no participa
   del camino de veredicto de Mode 1** (`vigia_agent.py` → shim → V4 →
   AbductiveReasoner → scorer: **cero** referencias). Vive en el camino de
   **Mode 4 / API / scripts** (`vigia/pipeline/pipeline.py` → posterior →
   `RiskBoundedDecisionLayer.decide` → `decision_trace.decision` sellado por
   `bundle_builder`) y en `shadow_mode` (monitoring). La evaluación de los 21
   casos ejercita un cableado sintético que Mode 1 nunca ejecuta — el número
   "0 flips en 21 casos" era correcto pero medía un camino distinto al que el
   lector de BUGS_PENDIENTES probablemente asume.

**Veredicto de la auditoría:** L-040 puede seguir en severidad BAJA para
*exactitud de valores* (errores ~1e-16, no se acumulan, saturan hacia 1.0),
pero debe (a) reclasificarse el overflow como bug propio P1 (B-051, crash
determinista), (b) anotar los flips construibles como limitación Daubert con
reproducción, y (c) corregir el texto de la limitación (los umbrales "0.55 /
0.75" citados no existen en este camino — ver §2.4).

---

## 1. Inventario de puntos float y traza hasta el veredicto

### 1.1 Puntos float dentro de `likelihood_ratio.py`

| # | Línea | Operación | Nota |
|---|-------|-----------|------|
| P1 | `:192` / `:257-259` | `_clip_z` — min/max sobre float | sin error propio |
| P2 | `:201` / `:262-270` | `log_lr = z²/2` en float | ~1 ulp por señal |
| P3 | `:206-207` | `log_lrs[i] *= s.confidence` | ~1 ulp por señal |
| P4 | `:215` | `combined_log_lr = sum(log_lrs) * correction_factor` | suma float izquierda-a-derecha; el orden ES determinista (misma lista → mismo resultado) |
| P5 | **`:218`** | `lr_combined = math.exp(combined_log_lr)` | **sin guard: OverflowError si el argumento > 709.78** (§2.3); FPU nativa — bit 52 puede variar x86/ARM (precedente P1-005 en `vigia/security/security.py:129-135`) |
| P6 | `:219` | `posterior = lr / (1.0 + lr)` | 1 ulp; satura a 1.0 con log_lr ≳ 37 |
| P7 | `:222` | `enfsi_label(lr_combined)` | comparaciones float contra enteros exactos 1/2/10/100/1000/10000 (`ebs_v1.py:786-801`) — borde de flip |
| P8 | `:305-306` | `mean_corr = sum(vals)/len(vals)`; `correction_factor = 1-mean_corr` | float |
| P9 | `:110-117` | `ForensicRecord.to_dict` — `round(x, 6)` | el registro sellado (y `record_hash()`, `:125-128`) dependen del `repr` float → estabilidad cross-plataforma no garantizada (ver F-L040-4) |

En el **adaptador** `vigia/core/likelihood_engine.py` (el que usa `pipeline.py`):

| # | Línea | Operación | Nota |
|---|-------|-----------|------|
| A1 | `:94` | `z_cap: float = 10.0` **por defecto** | el motor base usa 3.0; el adaptador amplía a 10 → log_lr hasta 12.5 por señal con `Z_CLIP_MAX=5.0` de `SignalOutput` |
| A2 | `:124` | `lr = exp(clamp(log_lr, ±20))` | clampea SU `lr`, pero llama primero a `super().infer()` que ejecuta P5 **sin clamp** — el guard del adaptador no protege nada (§2.3) |
| A3 | `:142-146` | `decision_hint` = comparaciones float de posterior vs 0.05/0.95 | hint, no veredicto |
| A4 | `:175` | `_correlation_penalty` con `math.exp` | solo referenciado por tests de integración |

### 1.2 Traza del flujo hasta el veredicto

```
SignalOutput.z_score / .confidence  (float crudo — NO pasa por P0-001)
        │
        ▼
LikelihoodEngine.infer()                    vigia/core/likelihood_ratio.py
        │  P2-P6: z²/2 · conf → Σ → math.exp → posterior       (float)
        │  P7: enfsi_label(lr)  →  ForensicRecord (sellado, round 6)
        ▼
[H28] LRCalibrator.calibrated_posterior()   vigia/core/lr_calibration.py:50-51
        │  sigmoide float 1/(1+exp(-x)) — si hay calibración, REEMPLAZA el
        │  posterior que sigue al risk layer (pipeline.py:470-485)
        ▼
RiskBoundedDecisionLayer.decide()           vigia/core/risk_bounded_layer.py:460-534
        │  compute_risk: interno Decimal prec-28 desde Decimal(str(posterior)),
        │  quantize 1e-6 ROUND_HALF_EVEN → float r  (:446-458)
        │  r <= ε_accept(0.05) → ACCEPT ; r >= 0.95 → REJECT ; sino ABSTAIN
        ▼
DecisionTrace.decision  →  bundle_builder (sellado: decision_trace.decision)
```

Caminos paralelos que consumen el mismo posterior float:
- `vigia/core/shadow_mode.py:89-99` — bandas 0.85 / 0.60 / 0.40 →
  `lr_verdict` (FABRICATED/SUSPICIOUS/BORDERLINE/AUTHENTIC). Monitoring only:
  no altera el veredicto MCP, pero `diverges` (`:102-106`) alimenta el log de
  divergencias.
- `scripts/run_calibration.py`, `scripts/run_demo.py`, `vigia/vigia_core.py` —
  offline/demo.

### 1.3 Alcance por modo de despliegue

| Camino | ¿Usa likelihood_ratio? | Evidencia |
|---|---|---|
| **Mode 1** — `vigia_agent.py` → shim → V4 → AbductiveReasoner → L-036 | **NO** | `grep likelihood` sobre `vigia_agent.py`, ambos `sift_orchestrator.py`, `vigia/sift/*`, `vigia/inference/*`, `vigia_scorer.py`: 0 coincidencias |
| Mode 1 fallback texto (`_run_text_pipeline`) | NO (muerto) | `from run_pipeline import run` → el módulo `run_pipeline` no existe en el root → `PIPELINE_UNAVAILABLE` siempre (hallazgo lateral F-L040-6) |
| **Mode 4 / API** — `vigia/pipeline/pipeline.py:455-531`, `vigia_api.py` | **SÍ** — es el camino de veredicto ACCEPT/REJECT/ABSTAIN | `pipeline.py:163,455` |
| MCP scorer (`vigia_scorer.py`) | NO — ya de-floateado con tablas (`_EXP_NEG2_TABLE`, `:167`; `_SUPPORT_SCORE_TABLE`, `:451`) | precedente de fix correcto |
| Shadow mode | SÍ (monitoring only) | `shadow_mode.py:91` |

**Corrección al texto de L-040:** los "21 casos reales" de la evaluación
2026-06-30 son casos EBS-JSON que en producción van por el adaptador del shim
(`_analyze_ebs_json`) — camino que **no invoca** `LikelihoodEngine`. La
evaluación cableó los z de esos casos al engine sintéticamente (igual que esta
auditoría, para ser comparables). El "0 flips" es correcto pero no describe
exposición de producción de Mode 1; describe la del camino Mode 4 si esos
mismos z llegaran por `pipeline.py`.

---

## 2. Casos de prueba con diferencia float↔exacto maximizada

Referencia exacta: `Decimal` prec=50, réplica 1:1 de la fórmula del engine
(clip → z²/2 → ×conf → Σ → `Decimal.exp()` → p=lr/(1+lr)). Harness completo
reproducible con los snippets de §5.

### 2.1 Magnitud del error en operación normal — NO acumula

- Sweep determinista (seed=42), 3.000 inferencias, n∈[1,60], z∈[-5,5],
  conf∈[0,1]: **max |Δposterior| = 1.70×10⁻¹⁶, 0 flips** (ENFSI, bandas
  shadow, decisión risk-layer).
- Acumulación (n copias de z=1.245, conf=0.7): el error **decrece** al crecer
  n — el posterior satura hacia 1.0 y la derivada dp/d(log_lr) → 0:

  | n | posterior float | \|Δ\| |
  |---|---|---|
  | 1 | 0.632395823696196 | 1.2×10⁻¹⁶ |
  | 10 | 0.995614635395609 | 1.1×10⁻¹⁷ |
  | 100 | 1.000000000000000 | 2.7×10⁻²⁴ |
  | 500 | 1.000000000000000 | 0 |

  Conclusión: **la acumulación de error de suma float NO es un mecanismo de
  flip realista** — donde más señales hay, menos sensible es el posterior.
  La zona sensible es n bajo con posterior en zona media (0.4–0.96), y ahí el
  error es ~1 ulp (10⁻¹⁶).

### 2.2 Flips construidos — sí existen `[REPRODUCIDO]`

Búsqueda adversarial 2D: para cada z aleatorio, se calcula la confidence que
pone el resultado exactamente en un borde de decisión, y se escanean ±ulps.
Una señal, sin matriz de correlación, engine con defaults (`z_cap=3.0`).

**Flip de etiqueta ENFSI (borde LR=2):**

| z | confidence | LR float → label | LR exacto → label |
|---|---|---|---|
| `1.9857491472497435` | `0.3515658538994868` | `2.0` → **limited** | `1.99999999999999994…` → **weak** |
| `1.7262737608867529` | `0.4651961565878651` | `2.0` → **limited** | `1.99999999999999987…` → **weak** |

**Flip de etiqueta ENFSI (borde LR=10) — en ambas direcciones:**

| z | confidence | LR float → label | LR exacto → label |
|---|---|---|---|
| `2.476401709559781` | `0.7509369839952681` | `9.999999999999998` → **limited** | `10.0000000000000009…` → **moderate** |
| `2.26115359978413` | `0.9007111823770336` | `10.000000000000002` → **moderate** | `9.9999999999999986…` → **limited** |

**Flip de decisión del risk layer (ACCEPT vs ABSTAIN):** el borde real no es
posterior=0.95 sino el punto medio de la cuantización a 1e-6 del riesgo
(`compute_risk`, `risk_bounded_layer.py:457`): r=0.0500005 ⇔ posterior
0.9499995, donde ROUND_HALF_EVEN baja a 0.050000 (par) → ACCEPT.

| z | confidence | posterior float → decisión | posterior exacto → decisión |
|---|---|---|---|
| `2.4717268632965954` | `0.9638957074827289` | `0.9499995` → **ACCEPT** | `0.94999949999999995…` → **ABSTAIN** |
| `2.9090527008284752` | `0.6958695345770735` | `0.9499995` → **ACCEPT** | `0.94999949999999996…` → **ABSTAIN** |

Mecánica: el error de ~1 ulp del camino float redondea el posterior
exactamente AL punto medio; la cuantización banker's del midpoint (baja al
par) produce ACCEPT, mientras el valor verdadero está por debajo del midpoint
y cuantiza a 0.050001 → ABSTAIN. **Es un flip de veredicto sellable en un
bundle de Mode 4** (`decision_trace.decision`).

**Lectura correcta de estos hallazgos:** cada flip requiere que el input caiga
en una ventana de ~1 ulp alrededor de un borde (probabilidad ≈ 0 para datos
reales; la búsqueda necesitó ~10³–10⁴ candidatos dirigidos por borde). No son
un riesgo operativo espontáneo — son la prueba formal de que el "0 flips" de
L-040 es una propiedad del corpus, no del código. Bajo cross-examination
("¿puede el redondeo de su software cambiar un veredicto?") la respuesta
honesta ahora es: "sí, en inputs construidos al ulp; medido, documentado y
acotado a 1e-16; nuestro corpus real opera a >10 órdenes de magnitud de esos
bordes".

### 2.3 Hallazgo nuevo — OverflowError sin guard (propuesto **B-051**, P1) `[REPRODUCIDO]`

`likelihood_ratio.py:218` ejecuta `math.exp(combined_log_lr)` sin acotar el
argumento. `math.exp` desborda en ~709.78:

| Configuración | Señales para crashear | Resultado |
|---|---|---|
| Engine base (`z_cap=3.0`), z=3, conf=1 | **n ≥ 158** (bisección exacta: 158) | `OverflowError: math range error` |
| Adaptador `pipeline.py` (**`z_cap=10.0` default**), z=5 (`Z_CLIP_MAX`), conf=1 | **n ≥ 57** | `OverflowError` — el clamp ±20 del adaptador (`likelihood_engine.py:124`) llega tarde: `super().infer()` ya crasheó |

Impacto: la Segundidad de Mode 4 (`pipeline.py:455`) muere con excepción ante
un caso con suficientes señales de alta z — no ABSTAIN, no error controlado:
**crash**. El corpus ya contiene VIGIA-BREAK-014 con 101 artefactos; un caso
de batch con ~60 señales z≈5 de alta confianza es plausible, y un adversario
que pueda inyectar señales tiene un DoS determinista del pipeline.
Contraste: el propio archivo vecino `vigia/abduction/vigia_counter_fact.py:814-827`
ya captura `OverflowError` para el mismo patrón, y `shadow_mode`/`counter_fact`
documentan el límite 709 — el conocimiento existía, el guard no.

### 2.4 Los umbrales "posterior ~0.55 o 0.75" de L-040 no existen en este camino

El texto de L-040 dice revisar "si los z caen cerca de umbrales de decisión
(posterior ~0.55 o 0.75)". Ningún consumidor de `likelihood_ratio` usa esos
valores: los bordes reales son las bandas shadow **0.40 / 0.60 / 0.85**
(`shadow_mode.py:93-99`), los enteros ENFSI **1/2/10/100/1000/10000**
(`ebs_v1.py:786-801`) y el riesgo **ε=0.05 / 0.95** post-cuantización 1e-6
(`risk_bounded_layer.py:494-534` + `make_default_policy`, `ebs_v1.py:742-766`).
0.75 es el umbral MALICE de `vigia_scorer.py` — un camino que no consume este
posterior. El texto de la limitación debe corregirse.

---

## 3. Los 21 (hoy 33) casos reales: float vs Decimal+ROUND_HALF_EVEN

Los prefijos de la evaluación original (`VIGIA-AMB-*, VIGIA-BREAK-*,
VIGIA-FN-*, VIGIA-FP-*, VIGIA-REAL-*`) hoy matchean 52 casos, de los cuales
**33 tienen artefactos con `raw_score`/`prior_trust`** (los otros 19 usan el
esquema narrativo sin scores — z=0 para todos, sin información float).
Construcción de señales idéntica al adaptador EBS del shim:
`z = Fraction(raw_score) × Fraction(prior_trust)` → float; `conf = prior_trust`.

**Resultados (float vs referencia Decimal prec=50):**

| Métrica | Valor |
|---|---|
| Casos evaluados | 33 |
| Verdict flips (ENFSI / bandas shadow / decisión risk-layer) | **0 / 0 / 0** |
| Máx \|Δposterior\| | **1.389×10⁻¹⁶** (VIGIA-FN-002, 3 señales) |
| Mediana \|Δposterior\| | ~7×10⁻¹⁷ |

**Reproducción de la metodología original 2026-06-30** (float A vs z
cuantizado a 0.01 con `Decimal.quantize(ROUND_HALF_EVEN)` B): **0 flips en los
33 casos** — coincide con el resultado histórico de 21.

Nota: la metodología original (A vs B con z *cuantizado*) mide otra cosa que
esta auditoría (float vs *aritmética exacta* con los mismos z). Ambas dan 0
flips, pero la comparación contra referencia exacta es la que acota el error
del camino float en sí (~1 ulp) y no el efecto de cuantizar el input.

Distancia al borde más cercana observada en el corpus: el caso más "cerca" de
un borde de decisión queda a >10⁻³ del mismo — 13 órdenes de magnitud por
encima del error float. Un flip espontáneo en este corpus es imposible en la
práctica.

---

## 4. ¿P0-001 cubre L-040? — No, y hay paths adicionales

### 4.1 Qué cubrió P0-001

P0-001 (FIXED 2026-06-30) reemplazó `Fraction(int(round(val*100)), 100)` por
`Fraction(Decimal(str(val)).quantize(Decimal("0.01"), ROUND_HALF_EVEN))` en
exactamente dos puntos:
- `vigia/sift/sift_orchestrator.py:611` (gamma, boundary SIFT→scorer), y
- `vigia/sift/unified_timeline_engine.py:100-102`.

Ambos son el boundary **SIFT→Fraction** del camino Mode 1/V4. El camino de
`likelihood_ratio.py` (Mode 4/API/scripts) consume `SignalOutput.z_score`
**crudo, antes y por fuera** de esos dos puntos: **cobertura de L-040 = 0%**.
Son riesgos hermanos (float en el path de veredicto) pero fronteras disjuntas.

### 4.2 Paths float adicionales que alimentan veredicto/registro (no cubiertos)

| # | Path | Archivo:línea | Riesgo | Estado |
|---|---|---|---|---|
| U1 | Sigmoide/logit del calibrador H28 — su salida **reemplaza** el posterior que decide | `lr_calibration.py:50-51,144,238` | mismo perfil que L-040 (1 ulp) + `math.exp` sin guard (overflow imposible aquí: argumento acotado por ±6 en `pipeline.py:475`) | no cubierto |
| U2 | `math.exp` de `likelihood_ratio.py:218` | — | **overflow B-051** (§2.3) | no cubierto |
| U3 | `trust_fusion.compute_temporal_trust_factor` — `math.exp(-2·sev)` → effective_trust → scorer | `trust_fusion.py:271` | mitigado parcialmente por `_dround` (redondeo decimal post-exp), pero la exp es FPU nativa; contrasta con `security.py` P1-005 que la reemplazó por tabla Decimal por el bit 52 x86/ARM | parcial |
| U4 | `eml_gci` — agregación log-sum-exp float → produce el `z_score` de la señal GCI que TODO el sistema consume | `eml_gci.py:301` | el z resultante sí pasa por P0-001 al entrar a gamma (cuantización 0.01 absorbe 1e-16), pero en Mode 4 entra crudo al engine | parcial |
| U5 | `vigia_integration_bridge` — `math.log(lr)` para el lr_record del bundle | `vigia_integration_bridge.py:989` | solo registro | no cubierto |
| U6 | `graph_stability` — MI/entropías float → `graph_stability` → input de `compute_risk` | `graph_stability.py:164,494` | entra al risk layer vía `Decimal(str(s))` — determinista pero float-derivado | no cubierto |
| U7 | `ForensicRecord.record_hash()` — hash sobre floats `round(...,6)` | `likelihood_ratio.py:110-128` | **reproducibilidad cross-plataforma**: `math.exp` puede diferir en el bit 52 entre x86/ARM (reconocido por el propio repo en `security.py:129-135`, P1-005). Mismo input → distinto `record_hash` entre arquitecturas es posible; y si el flip de §2.2 cae en el bit redondeado, distinta etiqueta sellada | no cubierto |

### 4.3 Lo que SÍ está bien por diseño (para no duplicar trabajo)

- `compute_risk` ya es Decimal interno con quantize 1e-6 (`risk_bounded_layer.py:446-458`)
  — la cuantización absorbe errores < 5×10⁻⁷ del posterior **excepto** en los
  midpoints exactos (el flip de §2.2 explota precisamente eso).
- `vigia_scorer.py` ya eliminó `math.exp`/`math.log` con tablas
  (`_EXP_NEG2_TABLE`, `_SUPPORT_SCORE_TABLE`) — es el precedente de fix
  correcto si algún día se de-floatea el engine.
- La suma float de `:215` es determinista (mismo orden de lista → mismo
  resultado bit a bit en la misma plataforma).

---

## 5. Reproducción empírica

Todos los números de esta auditoría se regeneran con estos snippets (stdlib +
repo, sin dependencias):

**Flip ENFSI (borde LR=10):**
```bash
python3 -c "
from decimal import Decimal, localcontext
from vigia.core.likelihood_ratio import LikelihoodEngine
from vigia.core.ebs_v1 import SignalOutput, enfsi_label
z, c = 2.476401709559781, 0.7509369839952681
rec = LikelihoodEngine().infer([SignalOutput(tool_name='T', value=z, z_score=z, confidence=c)])
with localcontext() as ctx:
    ctx.prec = 50
    lr = ((Decimal(str(z))**2/2) * Decimal(str(c))).exp()
print('float :', repr(rec.lr_combined), '->', rec.enfsi_label)
print('exacto:', str(lr)[:26], '-> moderate' if lr >= 10 else '-> limited')
"
# float : 9.999999999999998 -> limited
# exacto: 10.00000000000000099095575 -> moderate
```

**Flip de decisión risk-layer (ACCEPT vs ABSTAIN):**
```bash
python3 -c "
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from vigia.core.likelihood_ratio import LikelihoodEngine
from vigia.core.ebs_v1 import SignalOutput
z, c = 2.4717268632965954, 0.9638957074827289
p_f = LikelihoodEngine().infer([SignalOutput(tool_name='T', value=z, z_score=z, confidence=c)]).posterior_probability
with localcontext() as ctx:
    ctx.prec = 50
    lr = ((Decimal(str(z))**2/2) * Decimal(str(c))).exp(); p_d = lr/(1+lr)
q = lambda p: (Decimal(1)-p).quantize(Decimal('0.000001'), rounding=ROUND_HALF_EVEN)
dec = lambda r: 'ACCEPT' if r <= Decimal('0.05') else ('REJECT' if r >= Decimal('0.95') else 'ABSTAIN')
print('float :', repr(p_f), '->', dec(q(Decimal(str(p_f)))))
print('exacto:', str(p_d)[:24], '->', dec(q(p_d)))
"
# float : 0.9499995 -> ACCEPT
# exacto: 0.94999949999999995186 -> ABSTAIN
```

**OverflowError (B-051):**
```bash
python3 -c "
from vigia.core.likelihood_ratio import LikelihoodEngine
from vigia.core.ebs_v1 import SignalOutput
sigs = [SignalOutput(tool_name=f'T{i}', value=3.0, z_score=3.0, confidence=1.0) for i in range(158)]
LikelihoodEngine().infer(sigs)
"
# OverflowError: math range error   (idem: adaptador z_cap=10 con 57 señales z=5)
```

**Corpus 33 casos + sweep + acumulación:** harness completo ejecutado en esta
sesión (`l040_harness.py`, `l040_boundary2d.py` — scratchpad de sesión); la
construcción de señales replica `_analyze_ebs_json` del shim
(`z = Fraction(raw_score)·Fraction(prior_trust)`).

---

## 6. Conclusiones y recomendación (sin implementar)

1. **Mantener L-040 en severidad BAJA para exactitud de valores**, con el
   texto corregido: (a) el error float es ~1 ulp y NO se acumula (satura);
   (b) los umbrales citados (0.55/0.75) no existen en este camino — los reales
   son ENFSI {1,2,10,100,1000,10000}, shadow {0.40,0.60,0.85} y risk
   {0.05,0.95} post-quantize 1e-6; (c) el "0 flips en 21 casos" describe un
   cableado sintético, no exposición de Mode 1 (que no usa el engine).

2. **Abrir B-051 (P1): guard de overflow en `likelihood_ratio.py:218`** —
   clamp del argumento (p.ej. ±700, o el ±20 que el adaptador ya usa) o
   `try/except OverflowError → lr=inf → posterior=1.0` documentado. Es un
   crash determinista alcanzable con corpus real grande y un DoS trivial para
   un adversario que controle señales. Un test de regresión: 158 señales z=3
   no debe lanzar.

3. **Anotar en KNOWN_LIMITATIONS los flips construibles de §2.2** (valores
   exactos incluidos) como respuesta preparada para cross-examination: existen
   en ventanas de ~1 ulp alrededor de bordes exactos; el corpus real opera a
   ≥10 órdenes de magnitud de distancia.

4. **Si algún día se de-floatea el engine**, el patrón correcto ya existe en
   el repo: tablas/Decimal como `vigia_scorer.py` (`_EXP_NEG2_TABLE`) y
   `security.py` (P1-005) — no `Fraction` (exp/log no son racionales). El
   punto de mayor retorno no es el engine sino U7: cuantizar ANTES de sellar
   `record_hash` para garantizar reproducibilidad cross-plataforma del bit 52.

5. **Hallazgo lateral (F-L040-6):** el fallback de texto de Mode 1
   (`vigia_agent.py:1329`, `from run_pipeline import run`) importa un módulo
   que no existe en el root del repo → ese camino siempre degrada a
   `PIPELINE_UNAVAILABLE`. No afecta L-040 (de hecho lo aísla de Mode 1), pero
   es código muerto que aparenta ser una red de seguridad.

---

*Auditoría L-040 — el análisis formal que faltaba: el float no miente en el
corpus, pero ahora sabemos exactamente dónde, cuánto y cómo podría hacerlo.*
