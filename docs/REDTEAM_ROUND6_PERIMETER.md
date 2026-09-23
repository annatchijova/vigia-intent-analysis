# Security Audit — VIGÍA sealed-bundle perimeter

## Red Team Round 6 — The Sealed Perimeter

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `forensics/verify_ebs_v1.py`, `BundleBuilder.seal` / `quick_verify`,
`vigia/forensics/vigia_chain_of_custody` — qué cubre el sello del bundle y quién decide
si un bundle está íntegro. **Fuera de alcance:** el scorer, la cadena del
`tool_execution_log` en sí (Round 5).
**Base:** `claude/team-network-session-eiicdu` @ `96461cc` (estado auditado).
**Runtime:** CPython 3.11.15
**Evidencia reproducible:** `tests/test_r6_seal_perimeter.py`

## Modelo de amenaza

- El atacante **PUEDE**: reescribir el bundle JSON después del sellado.
- El atacante **NO PUEDE**: obtener la clave HMAC del ledger de custodia, modificar
  código, ni modificar los verificadores.
- **Frontera cruzada:** el borde del payload sellado — qué parte del archivo respalda
  `bundle_hash` y qué parte no.

Nota de alcance, dicha de entrada para no sobre-declarar: `integrity` en EBS v1 es
**SHA-256 pelado, sin HMAC**. Cualquiera con acceso de escritura puede recomputarlo
entero. Su autenticidad no viene del bundle sino del ledger de custodia
(`chain_hash` + `checkpoint_hmac`). Eso es una propiedad del diseño, no un hallazgo de
esta ronda; se enuncia porque es la precondición que decide la severidad de todo lo
demás.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R6-1 | **Alta** | **CONFIRMED BY INDUCTION** | vuln (autoridad) | Un bundle producido por el propio `seal_with_chain()` de VIGÍA era **íntegro** para el ledger e **inválido** para `verify_ebs_v1.py` y `quick_verify`. Notarizar con un receipt RFC 3161 (`pki`) rompía su propia verificación. | **FIXED** |
| R6-2 | **Media-Alta** | **CONFIRMED BY INDUCTION** | vuln (frontera) | El `tool_execution_log` no estaba cubierto por `bundle_hash` y **no podía estarlo**: adjuntar cualquier clave hermana rompía el sello. Las dos conductas que CLAUDE.md documenta componían un bundle inválido. | **FIXED** |
| R6-3 | Baja | **CONFIRMED BY INDUCTION** | vuln (silencio) | Borrar el log entero daba exit 2 ("bundle sin log") con el sello intacto: ausencia silenciosa. | **FIXED** |
| R6-4 | Baja | **CONFIRMED BY INDUCTION** | hygiene | Borrar `integrity.analysis_fingerprint` saltea su check y el bundle sigue PASS. | Registrado, no corregido |
| R6-5 | — | **Introducido por el fix** | vuln | Excluir el log del hash permite adjuntar un log **fabricado** a un bundle legítimo sin romper el sello. | Mitigado (WARNING explícito) |

---

## R6-1 — Conflicto de autoridad entre los tres verificadores · FIXED

**Severidad:** Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad

### Sorpresa

`seal()` arma `bundle_payload` desde una **lista fija** de nueve claves. Los
verificadores recomponen el payload como "todo menos `integrity`". Esas dos
definiciones sólo coinciden si el archivo en disco no tiene ninguna clave de más — y
VIGÍA tiene dos rutas documentadas que agregan exactamente eso.

### CODE FACT

`vigia_chain_of_custody.py` ya lo tenía resuelto y lo documentaba:

```python
# Campos agregados FUERA del payload hasheado por BundleBuilder.seal():
#   integrity, forensic_chain, pki
_PRESENTATION_FIELDS = ("integrity", "forensic_chain", "pki")
```

`verify_ebs_v1._check_bundle_hash` y `BundleBuilder.quick_verify`, en cambio:

```python
payload = {k: v for k, v in bundle.items() if k != "integrity"}
```

Tres componentes, tres conjuntos de exclusión distintos. Y `seal_with_chain()`
documenta explícitamente: *"el bundle_hash original NO cambia — el campo
`forensic_chain` se agrega FUERA del payload hasheado"*.

### Deducción → Inducción

Predicción: un bundle EBS válido al que se le agregue el bloque `forensic_chain` que
`seal_with_chain()` inyecta debe ser aceptado por el ledger y rechazado por los otros
dos. Ejecutado sobre `vigia/results/OWL-COMPLETE_bundle_claude_fable.json`:

```
caso              verify_ebs_v1   quick_verify   ledger_intacto
control           PASS            True           True
+forensic_chain   FAIL            False          True      <- desacuerdo
+pki              FAIL            False          True      <- desacuerdo
```

**La predicción se cumple.** El ledger de custodia dice íntegro; el verificador
independiente de terceros dice inválido. Para un juez, dos componentes del mismo
sistema contradiciéndose sobre el mismo archivo.

### Fix

Una sola noción de campos de presentación, con copia local en cada verificador
stdlib-only (por diseño, igual que la canonicalización) y test de lockstep:

```python
PRESENTATION_FIELDS = ("integrity", "forensic_chain", "pki", "tool_execution_log")
```

Hay una complicación medida, no supuesta: **existen dos esquemas de payload
históricos.** `results/real/VIGIA-REAL-009_bundle.json` tiene un
`tool_execution_log` que SÍ está dentro de su `bundle_hash`. Excluirlo sin más lo
rompía — lo detectó la regresión (1 de 15 bundles cambió de PASS a FAIL). Se prueban
**ambos** esquemas y el SHA-256 debe coincidir exactamente con uno.

Esto **no** es una degradación al estilo R5-1: ahí el atacante elegía el algoritmo
borrando un campo y con eso apagaba el HMAC; acá no elige nada — se prueban las dos
definiciones de payload y el hash tiene que coincidir con una, sin margen de forja.
Lo que sí cambia es el **alcance** del sello, y eso se reporta (ver R6-5).

---

## R6-2 — El audit trail estaba fuera del perímetro, y no podía entrar · FIXED

**Severidad:** Media-Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** frontera de confianza

### Sorpresa

Round 5 dejó anotado que `tool_execution_log` no está en `bundle_payload`. La
pregunta obvia era "¿por qué no?". Respuesta medida: **no puede estarlo.** `seal()`
hashea una lista fija, así que cualquier hermano agregado después rompe la
verificación. Medido sobre un bundle real: agregar `tool_execution_log`, o una clave
inocua cualquiera (`case_notes`), baja el bundle de Level 2 a FAIL.

Es decir: CLAUDE.md le indica al agente escribir el log y el `chain_tip_sha256` como
hermanos, y `seal()` produce el `integrity`. **Hacer las dos cosas, tal como están
documentadas, produce un bundle que falla su propio verificador.** Cada contrato se
cumple por separado; la composición es inválida.

### Fix

El arreglo de entradas viaja como campo de presentación; la **punta** de la cadena
entra dentro del payload sellado:

```python
sealed = BundleBuilder.seal(fb, tool_log_tip=chain.bundle_fields())
sealed["tool_execution_log"] = log
```

`chain_tip_sha256` no cambia de lugar — sigue siendo una clave de nivel bundle, donde
`verify_tool_log.py` ya la busca. Lo que cambia es que ahora está **cubierta** por
`bundle_hash`.

### Cadena causal del cierre

```
truncar tool_execution_log
    ↓ verify_tool_log recomputa la punta y la compara contra chain_tip_sha256
CHAIN BROKEN
    ↓ el atacante recomputa chain_tip_sha256 para taparlo (no necesita clave)
el tip está DENTRO del payload sellado
    ↓
bundle_hash deja de recomputar  →  y el bundle_hash está anclado en el
ledger de custodia con checkpoint HMAC, que el atacante no puede recomputar
```

### Inducción (ejecutada)

```
caso                             bundle_hash   cadena
E0 sellado + log intacto         OK            exit 0
E1 truncar el log                OK            exit 1   <- el tip lo detecta
E2 truncar + recomputar el tip   FAIL          exit 1   <- el sello lo detecta
E3 borrar el log entero          OK            exit 1   <- R6-3
```

E1 y E2 son las dos mitades del cierre: no queda una jugada que truncue el log y
además tape el rastro.

---

## R6-3 — Borrar el log entero era una ausencia silenciosa · FIXED

**Severidad:** Baja  **Nivel:** CONFIRMED BY INDUCTION

Borrar el arreglo completo devolvía exit **2** (`NO tool_execution_log —
fallback/EBS bundle`) con el sello intacto. Exit 2 no es "roto": es "este bundle no
tiene log", que es una afirmación distinta y, en ese caso, falsa. CLAUDE.md declara
que una investigación sin entradas de audit trail está incompleta bajo Daubert; el
verificador no tenía forma de distinguir "nunca tuvo log" de "se lo borraron".

Con el tip sellado (R6-2) sí la tiene: un bundle que declara `chain_tip_sha256` y no
trae el arreglo perdió algo que se selló → exit 1, cadena rota.

---

## R6-4 — `analysis_fingerprint` ausente saltea su propio check · registrado, no corregido

**Severidad:** Baja  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** threat-model

`_check_analysis_fingerprint` devuelve `True, "legacy bundle; not required"` cuando el
campo no está. Borrarlo deja el bundle en PASS (medido). Es el mismo patrón que R5-2
—la ausencia de un detector lo desactiva— pero **la severidad no se traslada**: en
EBS no hay capa keyed, así que quien puede borrar el campo puede también recomputarlo,
y no gana nada borrándolo. No se corrigió porque el fix honesto no es un check nuevo
sino la pregunta de fondo de la recomendación 1.

Se registra para que no se lea como no visto.

---

## R6-5 — Vector introducido por el fix de R6-1 · mitigado, no cerrado

**Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad (nueva)

Excluir `tool_execution_log` del hash tiene un costo que hay que decir en voz alta:
**antes, adjuntar un log a un bundle sellado rompía el sello; ahora no.** Un atacante
puede tomar un bundle legítimamente sellado, adjuntarle un audit trail **fabricado**
("todo limpio") y el sello sigue verificando.

No se puede cerrar sin romper R6-1 (los bundles con `forensic_chain` legítimo tienen
que verificar). Lo que sí se puede es no callarlo. Nuevo check `R1_SEAL_SCOPE`:

```
[WARN] R1_SEAL_SCOPE
       NO cubiertos por bundle_hash: tool_execution_log -> SIN ANCLA: el log no
       esta cubierto por bundle_hash ni por chain_tip_sha256. El sello no
       respalda este audit trail
```

Y cuando el log **sí** está anclado, lo dice también, nombrando de dónde viene la
autenticidad de cada campo de presentación (ledger para `forensic_chain`, receipt
RFC 3161 para `pki`, cadena anclada por el tip para el log).

Es WARNING y no ERROR deliberadamente: un log sin anclar no prueba que el bundle esté
alterado, y hoy ningún productor pasa `tool_log_tip`. Promoverlo a ERROR es la
decisión que queda pendiente — ver recomendación 2.

---

## Vectores descartados (no explotables)

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| Claves extra de nivel superior como divergencia seal-vs-verificador | Hipótesis inicial no confirmada | Los bundles que la mostraban (`VIGIA-REAL-ROCBA`, etc.) fallan antes, en `L1_STRUCTURE`: son reportes, no bundles EBS |
| `decision_trace.decision` alterado como control negativo | Control inválido, rehecho | El valor ya era `REJECT`: la mutación era un no-op. Rehecho con cuatro mutaciones reales, las cuatro detectadas por los tres verificadores |
| Recomputar `integrity` completo | Fuera del modelo de amenaza declarado | EBS v1 es SHA-256 sin HMAC por diseño; la autenticidad la da el ledger |

## Verificación del fix

- `tests/test_r6_seal_perimeter.py` → 13 tests. **Control negativo ejecutado:** 11 fallan contra el código pre-R6; los 2 que pasan en ambos estados son los controles (detección de manipulación, bundle legacy).
- Regresión sobre los **15 bundles con `integrity`** del repositorio: **0 veredictos cambiados** (la primera versión del fix cambiaba 1 — `VIGIA-REAL-009` — y eso obligó a soportar los dos esquemas de payload).
- Regresión sobre los **35 bundles con `tool_execution_log`**: 0 cambios de exit code.
- Cuatro controles negativos (`decision`, `epsilon_used`, `bundle_id`, `bundle_hash` falso) siguen fallando en los tres verificadores.
- Suite completa: `2265 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** (`test_requirements_ci_contract`, `test_trust_fusion_disclosure`), reproducidos idénticos sobre `HEAD` limpio, de causa ambiental.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **`integrity` no tiene capa keyed.** El `tool_execution_log` tiene `entry_hmac` y
   `chain_tip_hmac`; el bloque `integrity` del bundle, que lleva el veredicto, no tiene
   ninguno. Su autenticidad depende enteramente de que el ledger de custodia esté
   presente y sea confiable. Un `integrity_hmac` sobre `bundle_hash` cerraría R6-4 y
   haría el bundle auto-suficiente. Es un cambio de formato: decisión, no parche.
2. **Promover `R1_SEAL_SCOPE` a ERROR** cuando haya `tool_execution_log` sin
   `chain_tip_sha256`, una vez que todos los productores pasen `tool_log_tip` a
   `seal()`. Hoy sería un falso positivo masivo.
3. **Cablear `tool_log_tip` en los productores** (`sift_orchestrator`, pipeline Modo 4,
   el agente Modo 2 vía CLAUDE.md). El mecanismo está, falta que lo usen; hasta
   entonces R6-2 protege sólo a quien lo pase explícitamente.
4. **Actualizar CLAUDE.md**: hoy indica escribir `chain_tip_sha256` como hermano sin
   mencionar que debe pasar por `seal(tool_log_tip=...)` para quedar sellado.
