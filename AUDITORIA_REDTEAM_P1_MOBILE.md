# Red-team de los fixes P1 mobile — ¿cosmético o real?

**Fecha:** 2026-07-04
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Método:** refutación adversarial (ENGINEERING_DISCIPLINE §1.3) de mis PROPIOS
cambios P1 (B-071/B-072/B-073/B-074 + test B-042/B-043). Para cada uno, el
objetivo NO fue confirmar que funciona sino **construir el caso de que es
cosmético** y testearlo empíricamente. Todo reproducido con código en vivo.

**Veredicto global (honesto):** de 5 cambios, **1 es sólido**, **1 es
verdict-cosmético**, **1 es parcialmente cosmético con un bug real que queda
abierto**, **1 es real pero de baja cobertura**, y **1 arregló un problema pero
introdujo otro potencialmente peor**. Ninguno debe venderse como "resuelto" sin
estos matices.

| Fix | Veredicto red-team | Acción |
|-----|--------------------|--------|
| B-071 sqlite ro+immutable | REAL pero **introduce falso negativo grave** (pierde datos del WAL) | **Rework o revert** |
| B-072 conflación parsed | **PARCIALMENTE COSMÉTICO** (el ladder sigue escalando) | Fix real pendiente |
| B-073 has_phishing | **VERDICT-COSMÉTICO** (nunca cruza umbral) | Decisión de doctrina |
| B-074 SIP detection | REAL pero **baja recall** (fuente equivocada) | NVRAM pendiente |
| B-042/B-043 test | SÓLIDO; cobertura de ramas parcial | Fortalecer test (menor) |

---

## B-071 — sqlite read-only + immutable: REAL, pero introduce un falso negativo grave → ✅ RESUELTO (fix v2 copy-to-working-dir)

> **Actualización 2026-07-04:** corregido con el rework recomendado (c).
> `safe_sqlite_connect` copia la familia `db`+`-wal`+`-shm`+`-journal` a un
> working dir efímero y abre la COPIA read-write. Verificado: los datos del
> `-wal` ahora son visibles (FN cerrado) y la evidencia original queda intacta
> (hash idéntico tras escribir en la copia). El working dir se limpia al cerrar.
> Tests: `test_wal_data_is_visible`, `test_writes_to_copy_do_not_touch_evidence`,
> `test_working_dir_cleaned_on_close`. El detalle de abajo queda como registro.


**Lo que arregla (verificado):** `mode=ro&immutable=1` sí impide la escritura
en evidencia (rechaza INSERT, no crea `-wal`/`-journal`) y sí se niega a crear
una DB vacía en un path inexistente. Esos dos agujeros están cerrados.

**Lo que ROMPE (refutación, reproducido):** `immutable=1` le dice a SQLite que
el archivo no cambia, así que **ignora el `-wal`**. Una `sms.db` en modo WAL con
los mensajes recientes en el `-wal` (estado normal de un teléfono vivo) se lee
como **tabla inexistente** — todos los datos invisibles:

```
DB WAL con datos en el -wal:
  immutable=1 → "no such table: msg"   (pierde TODO)
```

Un teléfono incautado real leería "0 hallazgos" = limpio, o peor, dispararía
`EMPTY_CONTACTS`/`data_minimization` (ver B-072) sobre evidencia que SÍ existe.
Cambié un problema de custodia (escribir en evidencia) por uno de completitud
(perder evidencia inculpatoria) — que en términos forenses puede ser **peor**.

**Y `mode=ro` solo tampoco sirve (reproducido):** sin `immutable`, `mode=ro`
lee el WAL pero **crea `sms.db-shm` (32 KB) en el directorio de evidencia** →
vuelve a violar el invariante read-only.

**Conclusión:** las tres formas de "solo abrir el archivo en su lugar" son
incorrectas para una DB WAL sobre evidencia read-only:
- `connect()` crudo → auto-recovery escribe + crea DB en path ausente.
- `mode=ro` → crea `-shm` (escribe en evidencia).
- `mode=ro&immutable=1` → no escribe pero pierde el WAL.

**Fix correcto (no aplicado — decisión requerida):** el patrón forense estándar
es **copiar la familia `db` + `-wal` + `-shm` a un working dir y abrir la
copia** (read-write sobre la copia, nunca sobre el original). Eso satisface
ambos: cero escritura en evidencia Y lectura completa del WAL. Es un cambio
mayor (los módulos hoy abren el path de evidencia directo; necesitarían un
working dir + copia de la familia de archivos).

**Decisión para Anna:** (a) revertir B-071 al estado previo (lee WAL pero
escribe en evidencia), (b) mantener B-071 como está (no escribe pero pierde
WAL — documentado como limitación honesta §5.3), o (c) implementar el fix
copy-to-working-dir correcto. Recomiendo (c); mientras tanto, (b) con la
limitación documentada es más defendible que (a) bajo el invariante #1.

---

## B-072 — conflación no-parseable==vacío: PARCIALMENTE COSMÉTICO → ✅ RESUELTO (fix v2)

> **Actualización 2026-07-04:** corregido de verdad. Centinela
> `contacts_parsed`/`calls_parsed`: `to_signal` computa `empty_contacts =
> contacts_parsed and total_contacts == 0`. El escenario de abajo ahora da
> z=2.4 (no escala); una agenda realmente parseada-y-vacía sí escala (z=3.0).
> Tests: `TestB072DataMinimizationEscalation` (4). El detalle de abajo queda
> como registro de por qué el fix v1 era cosmético.


**Lo que hice:** un flag `parsed` para que el *finding* `EMPTY_CONTACTS`/
`EMPTY_CALL_LOG` no se emita cuando el parseo falla.

**Lo que NO arregla (refutación, reproducido):** `to_signal` NO lee el finding
— computa la señal directo del contador crudo:
```python
empty_contacts = self.total_contacts == 0
data_minimization = empty_contacts and empty_calls
```
Tras un fallo de parseo, `total_contacts`/`total_calls` quedan en su **default
0**, así que `empty_contacts=True` y `data_minimization=True` **igual**. El
ladder escala idéntico:

```
contacts+calls NO-parseables (schema desconocido):  z = 3.0
mismo caso con contactos reales (50/30):            z = 2.4
```

**Removí el finding pero NO la escalación del veredicto.** El falso INTENT/MALICE
que el fix decía cerrar **sigue vivo** por la vía `data_minimization`. Cosmético
para el path que importa.

**Fix real (no aplicado):** los contadores necesitan un centinela de "no
determinado" distinto de 0 (ej. `total_contacts = None`/`-1` cuando el parseo
falla), y `to_signal` debe computar `empty_contacts = (total_contacts == 0)`
solo cuando el conteo fue exitoso — o `data_minimization` debe exigir que ambos
conteos hayan sido *parseados*. Es un cambio en la dataclass + to_signal +
los tres sitios de parseo.

---

## B-073 — has_phishing al ladder: VERDICT-COSMÉTICO

**Lo que hice:** rama `elif has_phishing: z=1.6` — el flag deja de estar muerto.

**Lo que NO cambia (refutación, reproducido):** `_mobile_hypothesis` usa
umbral **estricto** `>2` para SUSPICION. z=1.6 (phishing) y z=1.2 (finding
genérico) **ambos** quedan sub-SUSPICION. Ni siquiera phishing + 3 opsec
(z=2.0) cruza, porque `>2` es estricto y 2.0 no es `>2`:

```
phishing solo:      z=1.6 → sub-SUSPICION
phishing + 3 opsec: z=2.0 → sub-SUSPICION (2.0 no es >2)
```

**Ningún veredicto cambia.** El fix es real solo como remoción de código muerto;
en el veredicto es cosmético. Si la doctrina quiere que phishing importe, el
tier tiene que ser >2 o combinar con otra señal — decisión de calibración (que
ya marqué como abierta, pero el red-team confirma que HOY no mueve nada).

---

## B-074 — detección de SIP disabled: REAL pero de baja recall → ✅ RESUELTO (fix v2 NVRAM)

> **Actualización 2026-07-04:** recall real cerrado. Se agregó la fuente
> autoritativa NVRAM `csr-active-config` (`_parse_csr_config` + `_CSR_FLAGS`):
> lee `nvram.plist`, interpreta el flag de 32 bits (0x0 = SIP ON; ≠0 =
> SIP_DISABLED con los flags concretos). NVRAM gana sobre el shell-history (que
> queda como fallback). Verificado: 0x77 → SIP_DISABLED con flags; 0x0 → note
> autoritativo; NVRAM 0x0 override sobre un `csrutil disable` en history. Tests:
> `TestB074NvramAuthoritative` (4) + `TestB074CsrParser` (4). Queda abierta solo
> la nota de doctrina (has_antiforensic). El detalle de abajo queda como registro.


**Lo que hice:** `_detect_sip_status` emite `SIP_DISABLED` al ver
`csrutil disable`/`enable --without` en un shell history → las ramas z=3.4/z=2.4
dejan de estar estructuralmente muertas (verificado: con SIP_DISABLED +
ANTIFORENSIC la rama z=2.4 fira).

**El agujero (análisis de dominio):** `csrutil disable` **solo corre desde
Recovery OS** — falla en el OS booteado ("This tool needs to be executed from
Recovery OS"). Los shell histories que las herramientas forenses capturan son
del volumen principal (OS booteado), donde el comando **rara vez aparece**. Así
que la detección, aunque correcta, tiene **baja recall en evidencia real**:
va a perder la mayoría de los Macs que SÍ tienen SIP deshabilitado.

**La fuente autoritativa** es la NVRAM `csr-active-config` (un flag de 32 bits;
!=0 = SIP debilitado), que **diferí como trabajo futuro**. Sin ella, la rama
está viva pero se dispara casi solo en el test, no en el campo.

**Real, no cosmético** (la rama se revive de verdad y el finding es correcto),
pero incompleto: para recall real hace falta el parser de NVRAM. Más la
decisión de doctrina ya anotada (ambas ramas exigen `has_antiforensic`; disable-
SIP es en sí T1562.001).

---

## B-042/B-043 — test de determinismo: SÓLIDO, cobertura de ramas parcial → ✅ REFORZADO

> **Actualización 2026-07-04:** gap de cobertura cerrado. Se agregó
> `TestLadderDomainExhaustive.test_all_tenths_roundtrip_lossless` (prueba el
> invariante para TODO múltiplo de 1/10 en [0, Z_CLIP_MAX] — superset de lo que
> el ladder emite) + `TestLadderCoverage` (grid combinatorio por módulo).
> Cobertura real ahora: iOS 18 / Android 19 / macOS 22 valores z distintos
> (antes 5), incluyendo las ramas altas (3.5/3.8) que el test original perdía,
> todos round-trip lossless. El detalle de abajo queda como registro.


**Refutación intentada:** ¿el test realmente prueba el determinismo o solo las
ramas que construí? Verificado: el test ejercitó z ∈ {0.0, 1.2, 1.6, 2.2, 3.4}
— incluye una rama alta (3.4) pero NO `SAFARI_EXPLOIT_RESEARCH` (3.5) ni
`has_hacking_search`.

**Por qué el veredicto se sostiene igual:** el invariante probado es "z es
múltiplo de 1/10 → `Fraction(str(float(z)))` es exacto". TODAS las ramas del
ladder producen múltiplos de 1/10 (3.8/3.5/3.4/.../1.2 + bumps 0.2/0.4), así que
el round-trip lossless vale **por construcción** para las 11, se hayan tocado o
no. El determinismo (dos corridas + proceso fresco) también es genérico.

**Único matiz:** es cobertura de ramas incompleta, no un gap de determinismo. El
test se puede fortalecer enumerando explícitamente las 11 salidas del ladder. La
conclusión (borde cosmético, no P0) **se mantiene**.

---

## Resumen de acciones propuestas (en orden de gravedad)

1. **B-071 (grave):** decidir revert / mantener-con-limitación / rework
   copy-to-working-dir. Es el único con potencial de perder evidencia real.
2. **B-072 (real, abierto):** centinela "no determinado" en los contadores para
   que `data_minimization` no escale sobre parseo fallido.
3. **B-074 (recall):** parser de NVRAM `csr-active-config` para recall real.
4. **B-073 (doctrina):** decidir si phishing debe mover el veredicto; hoy no.
5. **B-042/B-043 (menor):** enumerar las 11 ramas en el test de determinismo.

**Nada de esto se implementó en este pase** — es análisis. Sin cambios de código.
