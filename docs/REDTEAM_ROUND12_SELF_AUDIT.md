# Security Audit — la propia rama `claude/team-network-session-eiicdu`

## Red Team Round 12 — Auditoría de las Rondas 5–11

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing, §9 *"Auditing Another Agent's Audit"*
**Objeto:** los ocho commits de esta rama y las afirmaciones de sus siete informes.
**Base:** `origin/main` … `98bbf73`
**Runtime:** CPython 3.11.15, Node v22.22.2

El otro agente soy yo. La regla de §9 aplica igual: **se ataca el método, no al autor**
— pero sin la indulgencia que uno se tiene. Las preguntas son las de la lista: ¿en qué
nivel epistémico está realmente cada hallazgo? ¿Dónde está la inducción? ¿Cuál es el
modelo de amenaza? ¿En qué bucket cae? ¿El lenguaje es preciso?

## Resumen ejecutivo

| ID | Qué se auditó | Resultado |
|----|---------------|-----------|
| A-1 | ¿Algún cambio alteró un veredicto sellado? | **793 bundles, 0 veredictos cambiados** (medición más amplia que la de cada ronda) |
| A-2 | ¿`seal()` sigue siendo determinista? | **Sí.** Primera medición dio falsa alarma — instrumento mío defectuoso, ver abajo |
| A-3 | ¿El ancla de R6-2 está realmente dentro del sello? | **Confirmado** por `analysis_fingerprint` |
| A-4 | ¿`is_loopback` (R9) tiene falsos positivos? | **Ninguno** sobre 20 formas hostiles |
| A-5 | ¿El esquema doble de R6 amplía lo que verifica? | **No** más allá de R6-5, ya documentado |
| A-6 | ¿Los tests pueden fallar de verdad? | **9 asserts eran grep sobre el fuente.** 2 elevados a conducta; el resto declarado |
| A-7 | ¿La rama mergea con main? | Sin conflictos |
| A-8 | Residual no cerrado en mi propio fix de R11 | Registrado, no corregido |

---

## A-2 — Falsa alarma propia: el instrumento comparaba el campo equivocado

**Nivel:** FALSIFIED (la alarma, no el código)

Al comparar `seal()` entre main y la rama sobre la misma entrada, `bundle_hash`
**difería**. Bajo la invariante 4 de CLAUDE.md eso habría sido el hallazgo más grave de
toda la sesión: mis cambios rompiendo el sello.

Antes de reportarlo corrí **la misma rama dos veces**:

```
misma rama, corrida 1 : bundle_hash 1b34585e…
misma rama, corrida 2 : bundle_hash 7f63d82a…
main,        corrida 1 : bundle_hash f8f46d53…
main,        corrida 2 : bundle_hash d7c80483…
```

`bundle_hash` difiere corrida a corrida **en main también**. Es el diseño declarado
(B-198, comentado en `seal()`): es un sello de custodia *por corrida* que incluye
`generated_at` / `created_at` / `timestamp`; el identificador estable es
`analysis_fingerprint`, que la proyección analítica calcula sin esos campos. Y ése es
**idéntico** entre main y la rama.

Mi comparación miraba el campo que por diseño cambia siempre. Es el mismo tipo de error
que el oráculo zombie de R11 y el `ImportError` de colección de R9: **el instrumento, no
el sistema**. Tres veces en una sesión, todas detectadas antes de reportar, ninguna por
suerte — las tres salieron de preguntar "¿este resultado es posible?" en vez de
aceptarlo.

Se registra porque un informe que dijera "mis cambios alteran el sello" habría sido
falso y muy caro.

---

## A-3 — El ancla de R6-2 sí está dentro del sello

**Nivel:** CONFIRMED BY INDUCTION

La afirmación central de R6-2 era que el tip de la cadena entra al payload sellado. Se
re-verificó con el identificador correcto:

```
sin tip, dos corridas iguales : True     <- determinismo del fingerprint
con tip cambia el fingerprint : True     <- el ancla SI entra al sello
otro tip, otro fingerprint    : True
```

---

## A-5 — El esquema doble de R6 no amplía lo que verifica

**Nivel:** CONFIRMED BY INDUCTION

R6-1 hizo que los verificadores probaran dos definiciones de payload. La objeción obvia
contra mi propio fix: *¿un atacante elige la que le conviene?* Medido sobre el bundle
legacy real (`VIGIA-REAL-009`, cuyo log SÍ está dentro del hash):

```
control                     : True
borrarle el log             : False
truncarle el log            : False
alterarle una entrada       : False
agregar forensic_chain      : True   (R6-1, intencional)
```

En un bundle legacy el log **sigue protegido**. El atacante no elige el esquema: el
SHA-256 debe coincidir exactamente con uno de los dos. La única ampliación real es
R6-5 —adjuntar un log fabricado a un bundle moderno—, que ya estaba declarada y se
reporta como `R1_SEAL_SCOPE` WARNING.

---

## A-6 — Nueve asserts no probaban conducta

**Nivel:** CODE FACT · **PARCIALMENTE CORREGIDO**

Censo de mis propios tests: nueve asserts eran `assert "<string>" in src` sobre el
código fuente. Habrían pasado con el string dentro de un comentario, y no prueban que
el código haga nada.

Dos elevados a oráculo real:

- **R10-2 (banner):** ahora se **ejecuta** `errorView` tal como está en el `app.js`
  servido, con un error de petición y con uno de renderizado, y se compara el banner
  producido. Control negativo: falla contra el `app.js` de main.
- **R8 (endpoint):** ahora se levanta la app FastAPI real y se hace `POST` a
  `/api/bundles/{id}/verify` con `verifier: reasoning_trace` sobre un par cruzado,
  comprobando que despacha y devuelve `BROKEN`; más un caso que verifica que un nombre
  inventado sigue rechazado con 422. Control negativo: falla contra el `server.py` de main.

Los que quedan como grep, declarados en vez de disimulados:

| Test | Por qué se deja |
|------|-----------------|
| `test_r7::test_agent_calls_verify_reasoning_trace` | El llamado vive dentro del `main()` de `vigia_agent.py`; ejercerlo requiere una corrida completa del agente. La conducta **sí** está cubierta por `test_diverging_trace_is_not_written`, que ejecuta la función de verificación |
| `test_r8::test_frontend_offers_it_and_has_both_locales` | Paridad de claves i18n: la ausencia de una clave es exactamente lo que se quiere detectar |
| `test_r9::test_shell_launcher_prefers_the_ui_variable` | El `HOST` del launcher sólo alimenta el `echo` de la URL; un test de conducta exigiría ejecutar el script |
| `test_r10_4::test_both_predicates_agree` | No es un grep suelto: es un **tripwire** que aborta si el predicado JS cambió de forma, seguido de la evaluación real del predicado |

---

## A-8 — Residual en mi propio fix de R11, no cerrado

**Nivel:** PLAUSIBLE HYPOTHESIS (no ejecutado — forzarlo exige wraparound de pids)

`_signal_process_tree` resuelve `os.getpgid(proc.pid)` y señala ese grupo. Entre el
`proc.poll()` que lo antecede y el `killpg` hay una ventana: si el proceso muere ahí y
el sistema **reutiliza su pid**, se señalaría el grupo de un proceso ajeno.

No se reproduce (requiere agotar el espacio de pids), así que **no se reporta como
confirmado**. Se registra porque es una consecuencia directa de mi cambio y el lector
de R11 no la deduciría: pasar de señalar un pid a señalar un grupo agranda el radio del
error si el pid ya no es el que se cree.

Mitigación posible, registrada y no aplicada: `pidfd_open` (Linux ≥5.3) da una
referencia inmune a reutilización.

---

## Lo que la auditoría NO encontró

Registrarlo importa tanto como lo demás: una auditoría que sólo produce hallazgos es
sospechosa de buscarlos.

| Hipótesis contra mi propio trabajo | Resultado |
|------------------------------------|-----------|
| Algún cambio alteró un veredicto sellado del corpus | FALSIFICADA — 793 bundles, 0 cambios |
| `seal()` dejó de ser determinista | FALSIFICADA — el fingerprint estable es idéntico; la alarma era mi instrumento |
| `is_loopback` acepta alguna dirección no-loopback | FALSIFICADA — 0 falsos positivos sobre 20 formas hostiles (2 sobre-rechazos, del lado seguro) |
| El esquema doble de R6 deja pasar un bundle alterado | FALSIFICADA — el log sigue protegido en bundles legacy |
| La rama entra en conflicto con main | FALSIFICADA — 0 conflictos |
| R6-2 no ancla realmente el tip | FALSIFICADA — el fingerprint cambia con el tip |

## Sobre los siete informes

Re-leídos contra la lista de §9. No se encontró ningún `CONFIRMED` sin inducción
ejecutada. Los hallazgos que no se corrieron están rotulados como hipótesis (la fuga de
slot por `thread.start()` en R11, la carrera del `Timer`), y las limitaciones están en
el cuerpo y no al final: el residual sin clave de R5-1, el vector R6-5 que introduje
yo, el emparejamiento declarativo y no criptográfico de R7, el "no cierra mismo
usuario ni root" de R8-1, el alcance de la medición de R9 (bind confirmado, atacante
remoto no), la divergencia irreducible de R10-4.

Dos frases se revisaron por precisión de lenguaje (§7) y se sostienen: R5 dice *"se
selló un veredicto equivocado"* y no *"el sello es manipulable"*; R9 dice *"se confirmó
el bind y la ausencia de auth desde loopback"* y no *"explotado remotamente"*.

## Verificación

- Suite completa: `2361 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** (`test_requirements_ci_contract`, `test_trust_fusion_disclosure`), reproducidos idénticos sobre `origin/main`, de causa ambiental.
- Los dos tests elevados fallan contra `origin/main` y pasan sobre la rama.

## Pendientes acumulados (decisiones de formato — no aplicadas)

1. `integrity` sin capa keyed (R6).
2. `bundle_digest` dentro de la traza, para que el emparejamiento sea criptográfico (R7).
3. Clave HMAC a `--hmac-key-file` con permisos 0600 (R8).
4. Advertencia de bind no-loopback en la API Modo 5 (R9).
5. Formato de cable de las fracciones, para cerrar la divergencia `1.0` (R10-4).
6. Árbol de procesos en los `subprocess.run(..., timeout=N)` de `memory_forensics`, `pcap_parser` y `registry_timeline_reconstructor` (R11).
7. `pidfd_open` para cerrar el residual de reutilización de pid (A-8).
