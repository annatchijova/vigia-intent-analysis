# Security Audit — VIGÍA web UI verification surface

## Red Team Round 8 — The UI as a Verifier

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `vigia/ui/` — cómo la web UI invoca los verificadores, qué les pasa y qué
afirma al humano que la mira. **Fuera de alcance:** los verificadores en sí (R5–R7), el
scorer, `jobs.py` (ejecución de investigaciones).
**Base:** `claude/team-network-session-eiicdu` @ `b5b2e22`.
**Runtime:** CPython 3.11.15
**Evidencia reproducible:** `tests/test_r8_ui_verification.py`

## Modelo de amenaza

- El atacante **PUEDE**: (R8-1) ejecutar un proceso local sin privilegios en la misma
  máquina que el servidor de la UI; (R8-2) colocar archivos en el directorio de
  resultados que la UI indexa.
- El atacante **NO PUEDE**: ser root, leer la memoria del servidor, modificar código.
- **Frontera cruzada:** (R8-1) el borde proceso↔proceso por el que viaja un secreto;
  (R8-2) el borde entre lo que la UI *muestra* y lo que efectivamente *verificó*.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R8-1 | Media | **CONFIRMED BY INDUCTION** | vuln (exposición de secreto) | La clave HMAC que el usuario pega en la web viajaba por **argv** del subproceso, legible en `/proc/<pid>/cmdline` por cualquier proceso local. El comentario del código afirmaba lo contrario. | **FIXED** |
| R8-2 | Media-Alta | **CONFIRMED BY INDUCTION** | vuln (afirmación no verificada) | La UI mostraba badge "trace" y "traza: presente" por la sola existencia del archivo hermano. Un bundle MALICE con la traza de otro caso (SUSPICION) al lado se veía idéntico a un par legítimo. | **FIXED** |

Lo que **no** apareció, y vale registrarlo: la arquitectura de la UI es correcta en lo
grande. Invoca los verificadores reales como subprocesos stdlib-only, nunca los importa
y nunca anula un exit code. Eso evita por construcción el conflicto de autoridad que
R6-1 encontró entre los otros tres verificadores. Los dos defectos están en los bordes
de esa arquitectura, no en ella.

---

## R8-1 — La clave HMAC viajaba por argv · FIXED

**Severidad:** Media  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** exposición de secreto

### Sorpresa

El código lo comenta explícitamente:

```python
cmd = [sys.executable, str(verifier), str(bundle_path)]
if hmac_key_hex:
    # passed as argv, never logged and never echoed back in the response
    cmd += ["--hmac-key-hex", hmac_key_hex]
```

"Never logged and never echoed back" es cierto — y además irrelevante. El problema no
es el log de la aplicación: en Linux `/proc/<pid>/cmdline` es legible por cualquier
proceso del sistema. El comentario describe una defensa contra la amenaza equivocada.

La clave llega desde un formulario del browser → cuerpo HTTP → argv de un hijo. El
camino completo es alcanzable por un usuario de la UI.

### Deducción → Inducción

Predicción: un proceso local sin privilegios que lea `/proc/*/cmdline` en bucle
mientras corre la verificación debe encontrar la clave completa.

```
verificacion  : BROKEN exit 1
clave visible en /proc/<pid>/cmdline : True
  leido desde : /proc/798/cmdline
  argv        : /usr/local/bin/python3 .../verify_tool_log.py .../ROCBA-CDRIVE_bundle...
```

**La predicción se cumple.** La clave aparece completa.

### Fix

La clave va por el **entorno** del hijo; `verify_tool_log._resolve_hmac_key` ya lee
`VIGIA_HMAC_KEY`. `_run` acepta `extra_env` y sólo construye un entorno propio cuando
hay algo que agregar (sin clave, el hijo hereda el del servidor, como antes).

### Límite honesto

`/proc/<pid>/environ` está restringido al usuario dueño del proceso, no al mundo. Esto
**no** cierra el caso "mismo usuario o root" — nada que no sea un keyring o pasar la
clave por archivo con permisos lo cierra. Saca la clave del alcance de *cualquier
usuario local*, que es lo que se puede cerrar sin tocar el verificador. El verificador
acepta también `--hmac-key-file`; migrar a eso es una mejora posterior, no un parche.

### Un test afirmaba la conducta vieja

`tests/test_webui_verify.py::test_tool_log_hmac_key_in_argv_not_in_response` aseveraba
`assert "--hmac-key-hex" in seen["cmd"]`. No era un test malo: describía fielmente la
implementación de entonces. Se invirtió la mitad que cambió y se conservó la que sigue
siendo cierta ("no vuelve en la respuesta"), con el porqué escrito en el test. Se
registra porque un test verde sobre una conducta insegura es exactamente lo que impide
notarla.

---

## R8-2 — La UI afirmaba una asociación que nunca verificó · FIXED

**Severidad:** Media-Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** afirmación no verificada

### Sorpresa

R7-1 mostró que una reasoning trace puede tener su cadena intacta y aun así explicar
otro caso. La UI muestra un badge "trace" y una fila "traza: presente". ¿Con base en qué?

```python
"has_reasoning_trace": path.with_name(
    path.name.replace(".json", "_reasoning_trace.json")
).exists(),
```

Existencia de un nombre de archivo al lado. La UI nunca abre la traza.

El candidato obvio a descartar era `verdict_disagreement`, que la UI sí muestra con un
"≠". No cubre este caso: compara campos portadores de veredicto **dentro de un mismo
bundle** (`decision_trace.decision` vs `caie_analysis.verdict`), no bundle contra traza.

### Inducción (ejecutada, con artefactos reales)

Bundle de FLAREON-2017-M1 (MALICE) con la traza de JESS-M1 (SUSPICION) puesta como su
hermana:

```
Lo que la UI muestra:
  case_id              : FLAREON-2017-M1
  verdicts             : [MALICE, MALICIOUS_INTENT_DETECTED]
  verdict_disagreement : False
  has_reasoning_trace  : True      <- badge "trace" en la tabla
```

**Indistinguible de un par legítimo.** Y a diferencia de R7-1, acá lo lee un humano en
una pantalla que dice "Verificación independiente".

### Fix

Un verificador más, expuesto como los otros: `reasoning_trace` corre
`verify_tool_log.py <traza> --paired-bundle <bundle>` — que desde R7-1 comprueba la
cadena de la traza **y** el emparejamiento — y reporta su exit code verbatim, sin
interpretarlo.

```
par legitimo          : VERIFIED  exit=0
traza de OTRO caso    : BROKEN    exit=1
     [FAIL] case_id | traza='JESS-M1' bundle='FLAREON-2017-M1'
     [FAIL] veredicto | la traza registro 'SUSPICION' pero el bundle dice 'MALICE'
sin traza hermana     : ABSENT    exit=None
```

La bandera del índice sigue siendo lo que siempre fue —existencia de archivo— y eso está
bien: es un dato de inventario. Lo que faltaba era poder pedir la verificación. El botón
se ofrece como aplicable sólo cuando hay traza hermana, en EN y ES.

---

## Vectores descartados (no explotables)

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| La UI como cuarto verificador divergente (portar R6-1) | FALSIFICADO por lectura | No reimplementa nada: shellea a los verificadores reales y reporta su exit code verbatim. La arquitectura evita la clase entera |
| La UI oculta el `R1_SEAL_SCOPE` WARNING de R6-5 | No confirmado | El front renderiza cada check con `c.passed ? "✓" : "✗"`, así que un check en falso se ve. Queda el matiz de que el sello global sigue en verde — es el diseño WARNING≠ERROR decidido en R6, no un defecto de la UI |
| `check_sidecar` presenta MATCH como autenticidad | Ya documentado | Un SHA-256 pelado contra un sidecar pelado: ambos recomputables. Mismo límite que `integrity` (recomendación abierta de R6) |
| Clave HMAC devuelta al browser en la respuesta | FALSIFICADO | Medido: no aparece en la respuesta. Esa mitad del comentario era correcta |

## Verificación del fix

- `tests/test_r8_ui_verification.py` → 9 tests. **Control negativo ejecutado:** 6 fallan contra el código pre-R8; los 3 que pasan en ambos estados son los controles (la clave nunca volvió en la respuesta; la bandera del índice sigue siendo existencia de archivo; la clave sigue llegando al verificador).
- `tests/test_webui_verify.py` actualizado y verde (17 tests entre ambos archivos).
- Suite completa: `2285 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** (`test_requirements_ci_contract`, `test_trust_fusion_disclosure`), de causa ambiental.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **Migrar la clave a `--hmac-key-file`** con un archivo temporal mode-0600, o a un
   keyring. El entorno cierra "cualquier usuario local", no "mismo usuario".
2. **Que la UI corra el verificador de emparejamiento sola** cuando hay traza hermana,
   en vez de esperar un click: hoy el badge sigue apareciendo antes de cualquier
   verificación. Es una decisión de UX con costo de latencia.
3. Heredadas y aún abiertas: `integrity` sin capa keyed (R6), `bundle_digest` dentro de
   la traza para que el emparejamiento sea criptográfico y no declarativo (R7).
