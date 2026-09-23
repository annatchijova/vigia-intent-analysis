# Security Audit — VIGÍA reasoning trace ↔ sealed bundle

## Red Team Round 7 — Artifact Binding

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** el vínculo entre los dos artefactos que VIGÍA emite por caso — el bundle
sellado y su `*_reasoning_trace.json`. **Fuera de alcance:** el contenido del veredicto,
la cadena del log (Round 5), el perímetro del sello (Round 6).
**Base:** `claude/team-network-session-eiicdu` @ `51053a4`.
**Runtime:** CPython 3.11.15
**Evidencia reproducible:** `tests/test_r7_trace_bundle_pairing.py`

## Modelo de amenaza

- El atacante **PUEDE**: reemplazar archivos en el directorio de resultados — sustituir
  la reasoning trace de un caso por la de otro, o entregar un par cruzado.
- El atacante **NO PUEDE**: romper SHA-256, obtener la clave HMAC, modificar código.
- **Frontera cruzada:** el vínculo entre dos artefactos con integridad **separada**.
  Cada uno puede estar perfectamente intacto y aun así no pertenecerse.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R7-1 | **Alta** | **CONFIRMED BY INDUCTION** | vuln (invariante no cableado) | El invariante que ata traza y bundle está declarado como obligatorio, correctamente implementado, y no lo hacía cumplir nadie fuera del test suite. La traza de un caso SUSPICION presentada junto al bundle de un caso MALICE verificaba limpio con los comandos documentados. | **FIXED** |

Un solo hallazgo, y no es un defecto de criptografía: es un invariante correcto que
nadie llamaba. La clase importa — no se encuentra leyendo funciones de hash, se
encuentra preguntando *quién hace cumplir esto*.

---

## R7-1 — El emparejamiento traza ↔ bundle no lo hacía cumplir ningún verificador · FIXED

**Severidad:** Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad

### Sorpresa

Round 6 terminó preguntando dónde se produce el `tool_execution_log`. La respuesta
llevó a `vigia/core/reasoning_trace.py`, que emite un **archivo aparte**, hermano del
bundle. Y ahí el propio módulo declara el invariante, en su docstring:

> *"The wiring and any verifier MUST assert this equals the sealed bundle verdict.
> A divergence is a WIRING BUG and MUST fail here — it is never silently reconciled."*

Y lo implementa bien. `verify_reasoning_trace()` compara `case_id` y veredicto, y su
docstring explica por qué tiene que ser estricto:

> *"The trace lives OUTSIDE the bundle_digest (a sibling artifact with its own
> integrity), so this pairing check is the only thing binding the two."*

La pregunta obvia no es si el chequeo es correcto. Es **quién lo llama.**

### CODE FACT

`grep -rn 'verify_reasoning_trace'` sobre todo el repositorio, excluyendo el propio
módulo:

```
tests/test_reasoning_trace_bundle_gate.py:27:  from ... import verify_reasoning_trace
tests/test_reasoning_trace_bundle_gate.py:53:  result = verify_reasoning_trace(bundle, trace)
vigia_agent.py:2306:  # ... verify_reasoning_trace() binds the two
```

Un test, y un **comentario**. `vigia_agent.py` afirmaba en prosa que esa función ata
los dos artefactos, y no la invocaba. Ningún CLI la exponía: `verify_tool_log.py`
verifica la cadena de la traza en aislamiento, `forensics/verify_ebs_v1.py` verifica el
bundle, y ninguno de los dos mira al otro archivo.

### Deducción (predicción, enunciada antes del resultado)

Si el emparejamiento sólo se comprueba en un test, entonces dos artefactos de casos
distintos, cada uno con su cadena intacta, deben pasar los comandos documentados sin
que nada señale que no van juntos.

### Inducción (ejecutada, sobre artefactos reales del repositorio)

`vigia/results/mode1_crosscheck/` tiene cinco pares legítimos:

```
FLAREON-2017-M1   bundle.agent_verdict=MALICE     trace.verdict=MALICE
JESS-M1           bundle.agent_verdict=SUSPICION  trace.verdict=SUSPICION
```

Se presentó la traza de JESS-M1 junto al bundle de FLAREON-2017-M1:

```
verify_tool_log.py  : Result: CHAIN VERIFIED (3 entries, schema v2)   exit 0
Timeline            : PLAUSIBLE (timestamps monotonos y en rango)

verify_reasoning_trace()   [solo librería, ningún CLI la expone]:
  valid: False
  - case_id mismatch: trace='JESS-M1' bundle='FLAREON-2017-M1'
  - VERDICT DIVERGENCE (wiring bug): trace recorded 'SUSPICION' but the sealed
    bundle verdict is 'MALICE'
```

**La predicción se cumple.** El razonamiento de un caso SUSPICION, presentado como la
explicación del veredicto MALICE de otro caso, pasa toda la verificación documentada.

### Por qué importa más de lo que parece

La reasoning trace es el artefacto de **evidencia de proceso**: es lo que responde
"¿cómo llegó VIGÍA a este veredicto?". Un bundle sellado dice *qué* se decidió; la
traza dice *por qué*. Que el *por qué* pueda pertenecer a otro caso sin que ningún
verificador lo note es exactamente el tipo de brecha que el sistema entero existe para
cerrar — y no aparece mirando funciones de hash, porque todas funcionan bien.

### Fix — los dos extremos

**Producción.** `vigia_agent.py` llama ahora `verify_reasoning_trace()` antes de
escribir la traza y no la escribe si diverge. Se mantiene el fail-soft respecto del
bundle (§5.3: un problema con la traza nunca descarta un bundle ya sellado), pero se
separa de un fallo de escritura con una excepción propia y nivel `error`:
`[TRACE] WIRING BUG — reasoning trace NO escrita`. Una divergencia de veredicto no es
ruido operativo.

**Verificación.** `verify_tool_log.py` reconoce una reasoning trace (`trace_id` +
`verdict`), busca el bundle hermano `<stem>.json` — o acepta `--paired-bundle` — y
compara `case_id` y veredicto:

```
Pairing traza <-> bundle: .../FLAREON-2017_mode1_bundle.json
  [FAIL] case_id | traza='JESS-M1' bundle='FLAREON-2017-M1'
  [FAIL] veredicto | la traza registro 'SUSPICION' pero el bundle sellado dice
         'MALICE' — la traza se construyo a partir de otro resultado que el que se sello

Result: CHAIN BROKEN
```

La autodetección del hermano importa: un perito corre `verify_tool_log.py trace.json` a
secas, sin flags, y el emparejamiento tiene que ocurrir igual.

**Honest degradation.** Cuando no hay bundle con qué comparar, se dice:

```
[NOTE] Reasoning trace verificada EN AISLAMIENTO: no se encontro el bundle
hermano. La cadena prueba que la traza no fue alterada, NO que explique el
bundle que la acompana. Pasar --paired-bundle <path>.
```

Sin eso, "CHAIN VERIFIED" sobre una traza se lee como si probara más de lo que prueba.

---

## Defecto propio, corregido durante la sesión

La primera versión del flag se llamó `--bundle`, chocando con el `dest` del argumento
posicional (que ya se llama `bundle`). El flag pisaba la ruta del archivo a verificar:
el verificador terminaba verificando el bundle en vez de la traza (exit 2, `NO
tool_execution_log`) y el chequeo de emparejamiento comparaba la traza contra sí misma
—dando `[OK] case_id` por construcción. Tres síntomas, una causa. Renombrado a
`--paired-bundle` con `dest` propio.

Se registra porque un `[OK]` que sale de comparar un archivo consigo mismo es
exactamente el tipo de verificación vacía que esta ronda fue a buscar.

## Vectores descartados (no explotables)

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| Degradación de esquema en `verify_ebs_v1.py` (portar R5-1) | No aplica | EBS v1 no tiene capa keyed ni selección de esquema por dato: no hay nada que degradar |
| Shim `BundleBuilder` de `vigia/models/ebs.py` como ruta alternativa de sellado | Precondición inexistente | `pipeline.py` importa `vigia.core.bundle_builder`; el shim no está en ninguna ruta viva (su docstring, que afirma que pipeline.py lo usa, quedó obsoleto) |
| `verify_reasoning_trace()` incorrecto | FALSIFICADO | La función es correcta y estricta. El defecto no estaba en el chequeo sino en que nadie lo invocaba |

## Verificación del fix

- `tests/test_r7_trace_bundle_pairing.py` → 9 tests. **Control negativo ejecutado:** 6 fallan contra el código pre-R7; los 3 que pasan en ambos estados son los de librería (`verify_reasoning_trace` nunca fue el bug) y la regresión de pares legítimos.
- Los **5 pares reales** de `mode1_crosscheck/` siguen verificando en verde.
- Regresión sobre los **35 bundles con `tool_execution_log`**: 0 cambios de exit code.
- `scripts/redteam_round5_downgrade.py`: 12 vectores, 0 divergentes.
- Suite completa: `2275 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** y de causa ambiental.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **Vínculo criptográfico, no sólo declarativo.** El emparejamiento compara `case_id`
   y veredicto: dos campos que un atacante con acceso de escritura puede igualar. Un
   `bundle_digest` dentro de la traza lo haría criptográfico. Es un cambio al formato de
   la traza — decisión, no parche.
2. **`integrity` sin capa keyed** (heredada de Round 6, sigue abierta).
3. **Cablear `tool_log_tip` en los productores** (heredada de Round 6). El pipeline
   Modo 1 no emite `tool_execution_log` dentro del bundle, así que hoy R6-2 aplica sólo
   al agente Modo 2; conviene decidir si la traza debería sellarse con el mismo
   mecanismo.
4. **El shim `BundleBuilder` de `vigia/models/ebs.py`** declara en su docstring que
   `pipeline.py` lo usa. Ya no es cierto. Candidato a `codebase-health-assessment`.
