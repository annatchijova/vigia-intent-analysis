# Security Audit — VIGÍA `tool_execution_log` chain verifier

## Red Team Round 5 — Schema Downgrade

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `verify_tool_log.py` — el verificador standalone stdlib-only que un tercero
(perito, contraparte, juzgado) corre sobre un bundle sellado. **Fuera de alcance:**
`vigia/core/hash_chain.verify_chain` (la copia de librería), el scorer, `bundle_builder.seal`.
**Base:** `claude/team-network-session-eiicdu` @ `4c406ea` (estado vulnerable auditado).
**Runtime:** CPython 3.11.15
**Evidencia reproducible:** `scripts/redteam_round5_downgrade.py`, `tests/test_r5_schema_downgrade.py`

## Modelo de amenaza

- El atacante **PUEDE**: reescribir el bundle JSON completo después del sellado —
  agregar, borrar o modificar cualquier campo, dentro y fuera de `tool_execution_log`.
- El atacante **NO PUEDE**: obtener la clave HMAC (`VIGIA_HMAC_KEY`), modificar el
  código de VIGÍA, ni modificar el verificador que corre el tercero.
- **Frontera de confianza cruzada:** el archivo del bundle. Todo lo que está adentro es
  dato no autenticado hasta que el verificador lo autentica con la clave.
- **El test del juez:** *"si un juez me pidiera probar que este log no fue alterado,
  ¿qué tengo que asumir como cierto?"* Respuesta pre-fix: que el atacante no borró
  un campo concreto. Eso no es una suposición aceptable.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R5-1 | **Alta** | **CONFIRMED BY INDUCTION** | vuln | Degradación de esquema v2→v1: el dato no autenticado elegía el algoritmo de verificación. Apaga a la vez el hashing de entrada completa, la verificación HMAC y el ancla de cola. Un veredicto MALICE se reescribe como NOISE y el verificador imprime `CHAIN VERIFIED`, exit 0, **con la clave HMAC en mano**. | **FIXED** |
| R5-2 | **Media-Alta** | **CONFIRMED BY INDUCTION** | vuln | Borrar `chain_tip_sha256`/`chain_tip_hmac` devuelve la truncación de cola a indetectable, incluso bajo v2 keyed: la ausencia del ancla se trataba como retrocompatibilidad, no como borrado. | **FIXED** |
| R5-3 | Baja | **CONFIRMED BY INDUCTION** | hygiene | Entradas malformadas (no-dict, log no-lista) producían traceback en vez de diagnóstico. Exit code ya era fail-safe. | **FIXED** |
| R5-4 | — | **FALSIFIED** | — | Hipótesis propia: el fallback de canonicalización v1 en `_entry_hash_matches` sería un oráculo de colisión. Refutada por experimento. | Refutada |

Tres fixes aplicados sobre `verify_tool_log.py`, con 12 tests de regresión nuevos
(9 de ellos rojos contra el código pre-fix — control negativo ejecutado) y cero
cambios de exit code sobre los 35 bundles reales del repositorio.

---

## R5-1 — Degradación de esquema v2→v1 · FIXED

**Severidad:** Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad

### Sorpresa / expectativa violada

Tres rondas de endurecimiento apilaron defensas sobre esta cadena: R3-2 hizo
tamper-evident **cada campo de cada entrada** (`entry_hash` sobre la entrada completa),
A3 agregó `entry_hmac` para que una cadena íntegramente recomputada sin la clave fuera
detectable, y R3-5 ancló la cola con `chain_tip_sha256` / `chain_tip_hmac`. Las tres
viven en la vía v2 del verificador. La sorpresa: **las tres se apagan juntas con un
borrado que no requiere la clave.**

### Abducción (rivales, ordenados por economía de investigación)

1. *(a)* La selección de esquema depende de un campo que el atacante controla.
2. *(b)* La vía v1 recibe la clave HMAC pero la ignora.
3. *(c)* El sello exterior del bundle (`bundle_hash`) cubre `tool_execution_log` y
   cualquiera de las dos anteriores es irrelevante en la práctica.

Rival *(c)* se descarta primero por lectura (es la más barata y la que decidiría la
severidad): `BundleBuilder.seal` arma `bundle_payload` con nueve claves fijas —
`bundle_id`, `bundle_version`, `timestamp`, `evidence_graph`, `decision_trace`,
`policy_spec`, `actions`, `system_state`, `config_attestation` (+ `abduction_trace` /
`caie_analysis` opcionales). **`tool_execution_log` no está entre ellas.** El log vive
fuera del perímetro criptográfico del bundle sellado; `verify_tool_log.py` es su único
verificador. La severidad no se atenúa por un sello exterior que no lo cubre.

### CODE FACT

`verify_tool_log.py:verify_chain` (pre-fix):

```python
version = "2" if log[0].get("entry_hash") else "1"
...
if version == "2":
    hmac_key = _resolve_hmac_key(args) if args else None
    ok = _verify_v2(log, verbose, hmac_key, expected_tip, expected_tip_hmac)
else:
    ok = _verify_v1(log, verbose)          # <- sin hmac_key, sin expected_tip
```

Rival *(a)* confirmado por lectura: **un solo campo borrable, dentro del arreglo que el
atacante edita, seleccionaba el algoritmo de verificación.** Rival *(b)* es más fuerte de
lo supuesto: `_verify_v1` ni siquiera tenía parámetro de clave — no la ignora, no la
recibe. Y `expected_tip` sólo se lee dentro de la rama v2, así que bajo v1 el ancla de
cola no se consulta aunque esté presente.

Es el patrón clásico de **downgrade de suite criptográfica**: el dato no autenticado
negocia el algoritmo que debería autenticarlo.

### Deducción (predicción, enunciada antes del resultado)

Si *(a)* y *(b)* son ciertas, entonces un atacante **sin la clave** puede: reescribir el
log con el esquema v1, cambiar `VERDICT: MALICE` por `VERDICT: NOISE`, reescribir
`target` y `timestamp` de otra entrada, y el verificador — **corrido con la clave HMAC
correcta** — debe imprimir `CHAIN VERIFIED` y salir 0.

### Inducción (ejecutada)

`scripts/redteam_round5_downgrade.py`, clave fija `a`*32:

```
ID      pre-fix        post-fix      vector
E0      0 (v2)         0 (v2)        control: bundle intacto, keyed
E1      1 (v2)         1 (v2)        control: MALICE->NOISE bajo v2
R5-1a   0 CHAIN VERIFIED (v1)  1 BROKEN (v2)   degradación + MALICE->NOISE + target reescrito
R5-1b   0 CHAIN VERIFIED (v1)  1 BROKEN (v2)   ídem, con el ancla PRESENTE y obsoleta
R5-1d   0 CHAIN VERIFIED (v1)  1 BROKEN (v1)   strip total de marcadores, con clave
```

**La predicción se cumple.** R5-1a: veredicto invertido, `target` y `timestamp`
reescritos, verificado **con la clave**, salida `CHAIN VERIFIED (4 entries, schema v1)`,
exit 0. R5-1b agrega el dato que más importa para R3-5: el ancla de cola podía quedarse
en el bundle, obsoleta, y la vía v1 ni la mencionaba en la salida.

Matiz medido, no supuesto: borrar **sólo** `entry_hash` de `seq=1` (R5-1c) fallaba ya
pre-fix, pero por el motivo equivocado — la vía v1 exige `prev_hash == "GENESIS"` en
seq=1 y ahí seguía el génesis v2. El atacante debe además reescribir `prev_hash` en
todas las entradas: trivial, sin clave, y es exactamente R5-1a. Post-fix, R5-1c falla
por el motivo correcto: el bundle declara v2, y a la entrada sin `entry_hash` se la
reporta como contenido alterado.

### Cadena causal

```
log[0]["entry_hash"] borrado  (dato controlado por el atacante)
    ↓ version = "1"
_verify_v1(log, verbose)          sin hmac_key, sin expected_tip
    ↓ sólo se chequea prev_hash == SHA-256(result_summary anterior)
timestamp / tool / target / input_hash quedan sin cubrir
entry_hmac nunca se verifica      ← la clave del perito no participa
chain_tip_sha256 nunca se consulta ← el ancla R3-5 no participa
    ↓
"CHAIN VERIFIED (schema v1)", exit 0, sobre un log con el veredicto invertido
```

### Fix

`_detect_schema(log, bundle)` deduce el esquema de **todos** los marcadores v2 —
`chain_version == "2"`, `entry_hash` o `entry_hmac` en cualquier entrada, y
`chain_tip_sha256` / `chain_tip_hmac` a nivel bundle. Si algo declara v2, se verifica
como v2; la entrada a la que le falte `entry_hash` falla como contenido alterado, que es
lo que es. La cabecera imprime ahora cuántos marcadores v2 se detectaron y cuáles.

Residual cerrado parcialmente: `_verify_v1` recibe la clave y, si hay clave provista,
reporta el log v1 como **degradación** (v1 no lleva `entry_hmac`, así que no puede
autenticarse) salvo `--allow-legacy-v1`, la vía explícita para bundles históricos.

### Límite honesto (no se sobre-declara)

Un atacante que borre **todos** los marcadores v2 produce un bundle indistinguible de
uno legacy v1 genuino **cuando el verificador corre sin clave** (R5-1e: exit 0, post-fix
igual que pre-fix). Con clave, R5-1d lo marca. El fix eleva el costo de "borrar un
campo" a "reescribir cada entrada y borrar todo marcador, y aun así fallar ante
cualquiera que tenga la clave", pero no cierra el caso sin clave. Ese residual está
medido, no estimado, y tiene test: `test_full_marker_strip_is_flagged_only_when_keyed`.

---

## R5-2 — Borrar el ancla de cola reactiva la truncación · FIXED

**Severidad:** Media-Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad

### Sorpresa

R3-5 cerró la truncación de cola con `chain_tip_sha256`, y `chain_tip_hmac` cerró el
residual de que un SHA-256 pelado es recomputable por cualquiera con acceso de
escritura. Pero **la presencia del ancla también la decide el atacante**, y su ausencia
se trataba como retrocompatibilidad:

```python
else:
    print("\n  [NOTE] Sin chain_tip_sha256 en el bundle: truncar la cola ... ")
```

Un `[NOTE]`, no un `[FAIL]`. El mismo ataque que R3-5 detecta se vuelve a esconder
borrando el detector.

### Deducción → Inducción

Predicción: truncar el log a las 2 primeras entradas (descartando la entrada del
veredicto MALICE) **y** borrar `chain_tip_sha256` + `chain_tip_hmac` → exit 0 aun con la
clave provista. Observado (R5-2a pre-fix): exit 0, `CHAIN VERIFIED (2 entries, schema
v2)`. El control R5-2b (truncar dejando el ancla) da exit 1 pre y post — R3-5 funciona
cuando su ancla sigue ahí.

### Fix

El hecho de que un bundle *fue sellado con clave* es observable dentro de la propia
lista: `entry_hmac` presente en alguna entrada. `ToolExecutionLogChain.bundle_fields()`
emite `chain_tip_sha256` y `chain_tip_hmac` **juntos** siempre que hay clave. Entonces
`entry_hmac` presente + ancla ausente = borrado, no bundle viejo → `[FAIL]`. Ídem para
`chain_tip_hmac` ausente con `chain_tip_sha256` presente (R5-2c).

El contrato de R3-5 queda intacto para bundles **sin clave**: sin `entry_hmac`, la
ausencia de ancla sigue siendo `[NOTE]` y exit 0 — lo fija
`test_cli_notes_absence_of_tip` (R3-5) y lo re-verifica
`test_unkeyed_bundle_without_anchor_still_only_a_note` (R5).

---

## R5-3 — Log malformado produce traceback · FIXED

**Severidad:** Baja  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** hygiene

`log[0].get(...)` sobre una entrada string/`None`, o sobre un `tool_execution_log` que es
un dict, levanta `AttributeError` / `KeyError`. El exit code resultante es 1, o sea
fail-safe — no hay `VERIFIED` falso — pero un traceback no le dice a un perito qué
mirar. Mismo tipo que R4-4. Fix: guarda de forma con diagnóstico explícito que nombra
los índices malformados.

---

## R5-4 — FALSIFICADO: el fallback de canonicalización v1 no es un oráculo de colisión

**Nivel:** FALSIFIED

**Abducción.** `_entry_hash_matches` acepta el `entry_hash` almacenado si recomputa bajo
canonicalización **v2 o v1** (compat R3-2). v1 no escapa strings y v2 les antepone `s:`
tras normalizar NFC/CRLF. Hipótesis: entonces la transformación
`T(s) = "s:" + NFC(LF(s))` aplicada a cada string de una entrada produce una entrada
**distinta** cuyo hash v1 iguala el hash v2 de la original — colisión que además
sobrevive al HMAC, porque `entry_hmac` se calcula sobre `entry_hash`, que no cambia.

**Predicción.** El vector E4 debe dar exit 0 con la clave provista.

**Inducción.** Exit **1**, `CHAIN BROKEN`. Hipótesis **refutada**.

**Por qué falla, que es lo interesante.** `prev_hash` participa de dos chequeos a la vez:
`_entry_hash_v2` lo reinyecta crudo en el payload hasheado, y la verificación de linkage
lo compara crudo contra el `entry_hash` anterior. Para que el canon v1 reprodujera el
canon v2, `prev_hash` tendría que estar transformado a `"s:"+hash`; para que el linkage
cierre, tiene que quedar crudo. Un solo valor no puede ser las dos cosas. **La doble
función de `prev_hash` fija el esquema de canonicalización**, y el fallback v1 no es
alcanzable para ninguna entrada encadenada — sólo para bundles de esquema v2 sellados
antes del cambio de canon de R3-2, que es exactamente su propósito.

No se aplicó ningún cambio por R5-4: no hay defecto. Se documenta porque el próximo
auditor va a mirar ese fallback y pensar lo mismo.

---

## Vectores descartados (no explotables)

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| Colisión por canon v1 en `_entry_hash_matches` (R5-4) | FALSIFICADO por inducción | `prev_hash` es linkage-checked crudo **y** cubierto por el hash: fija el esquema de canon |
| Reescribir `entry_hmac` sin la clave, bajo v2 | Predicho sin efecto, no ejecutado | HMAC-SHA256 con clave de 32 bytes; queda fuera del modelo de amenaza declarado |
| Truncar la cola dejando el ancla (R5-2b) | Sin efecto | R3-5 lo detecta: es su caso de diseño |
| Sello exterior del bundle como mitigación de R5-1 | Precondición inexistente | `bundle_payload` de `BundleBuilder.seal` no incluye `tool_execution_log` |

## Verificación del fix

- `scripts/redteam_round5_downgrade.py` → 12 vectores, 0 divergentes post-fix; **6 divergentes** contra el verificador pre-fix (`--verifier` acepta la versión vulnerable).
- `tests/test_r5_schema_downgrade.py` → 12 tests. **Control negativo ejecutado:** 9 fallan contra `verify_tool_log.py` @ `4c406ea`; los 3 que pasan en ambos estados son los controles (E0, E1, el NOTE sin clave de R3-5).
- Regresión sobre los **35 bundles reales** del repositorio (`results/`, `vigia/results/`, `cases/`, `audits/`): **0 cambios de exit code** y 0 reclasificaciones de esquema.
- Suite completa: `2253 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes
  (`test_requirements_ci_contract`, `test_trust_fusion_disclosure`) son **pre-existentes**
  — reproducidos idénticos sobre `HEAD` limpio, causa ambiental (dependencias ausentes),
  ajenos a este cambio.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **`tool_execution_log` fuera del perímetro sellado.** `BundleBuilder.seal` no lo
   cubre. Hoy su única protección es su propia cadena; un bundle cuyo log sea eliminado
   por completo pierde el audit trail sin romper `bundle_hash`, y CLAUDE.md declara que
   "una investigación sin entradas de audit_trail está incompleta bajo Daubert". Evaluar
   incluir `chain_tip_sha256` (no el log entero) dentro de `bundle_payload`: ancla la
   cadena al sello del bundle con un solo campo.
2. **Aplicar la misma detección anti-degradación en `forensics/verify_ebs_v1.py`**, que
   comparte el patrón de copia propia de la canonicalización. No auditado en esta ronda.
3. **Considerar `chain_version` como campo obligatorio** en el writer, y rechazar en el
   verificador todo log v2 en el que falte — hoy `_detect_schema` lo usa como marcador,
   pero su ausencia no es en sí un error.
