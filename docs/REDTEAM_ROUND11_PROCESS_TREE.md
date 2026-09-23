# Security Audit — VIGÍA web UI job runner

## Red Team Round 11 — The Process Tree

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** `vigia/ui/jobs.py` — ciclo de vida del subproceso del lanzador Modo 1:
timeout, apagado, y el semáforo de concurrencia.
**Fuera de alcance:** los verificadores (R5–R8), la exposición de red (R9), el
renderizado (R10).
**Base:** `claude/team-network-session-eiicdu` @ `acfc510`.
**Runtime:** CPython 3.11.15, Linux
**Evidencia reproducible:** `scripts/redteam_round11_process_tree.py`, `tests/test_r11_process_tree_termination.py`

## Modelo de amenaza

Esta ronda **no** necesita un atacante. La precondición es un job que alcanza su
timeout —30 minutos por defecto, perfectamente normal sobre una imagen de memoria—
o un apagado del servidor. Ambos son operación corriente.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R11-1 | Media | **CONFIRMED BY INDUCTION** | vuln (ciclo de vida) | `start_new_session=True` crea un grupo de procesos a propósito, y `_kill`/`shutdown` llamaban `proc.terminate()`, que señala un solo pid. Las herramientas SIFT (volatility, tshark, regripper) sobrevivían al "process terminated". | **FIXED** |
| R11-2 | **Alta** | **CONFIRMED BY INDUCTION** | vuln (denegación) | Consecuencia que la medición destapó: el huérfano hereda el pipe de stdout, el bucle de lectura nunca ve EOF, el job queda en `running` para siempre y el slot **nunca se libera**. Con `max_jobs=1`, **un solo timeout dejaba el lanzador inutilizable hasta reiniciar el servidor.** | **FIXED** |

---

## R11-1 — El mecanismo estaba puesto y sin usar · FIXED

**Severidad:** Media  **Nivel:** CONFIRMED BY INDUCTION

### Sorpresa

```python
proc = subprocess.Popen(cmd, ..., start_new_session=True)
...
proc.terminate()
```

`start_new_session=True` hace al agente líder de su propia sesión y grupo. Eso
existe **precisamente** para poder señalar al árbol entero sin tocar al servidor.
Y después se señala un pid.

Es la tercera vez en esta sesión que aparece la misma firma: un mecanismo
correctamente montado y no usado por el código que lo necesita (`prev_hash` con
`String()` y sus vecinos sin él en R10-1; `_signal_z_fraction` guardando contra
`bool` y `_to_fraction` no, en R10-4).

### Alcance — verificado por cadena de imports, no supuesto

`vigia_agent.py` → `sift_orchestrator` → `memory_forensics`, `pcap_parser`,
`registry_timeline_reconstructor`, que corren volatility3, tshark y regripper
como subprocesos (timeouts propios de hasta 120 s y, para volatility, un
`vol3_effective_timeout` calculado). Sobre una imagen de memoria, minutos u horas.

### Inducción

Con el `JobRunner` real y un agente de prueba que lanza una herramienta de 300 s:

```
codigo pre-R11:   timeout del job       -> herramienta sigue corriendo: True
                  shutdown del servidor -> herramienta sigue corriendo: True
post-fix:         ambos                 -> False
```

### Un oráculo débil casi invalida la ronda

La primera medición dio un falso *"también sobrevive a `killpg`"*, lo que habría
llevado a descartar el fix correcto. La causa era el oráculo, no el código:
**`os.kill(pid, 0)` tiene éxito sobre un zombie**, así que un proceso ya muerto y
no cosechado se contaba como vivo. El oráculo correcto lee el estado en
`/proc/<pid>/stat` y descarta `'Z'`.

Queda escrito y fijado por test, porque un oráculo que no distingue zombie de
vivo invalida cualquier medición de terminación — y la conclusión que produce es
exactamente la contraria a la verdadera.

### Fix

`_signal_process_tree(proc, sig)` resuelve el pgid y señala al grupo. Lo que lo
hace seguro es `start_new_session=True`: sin eso el grupo sería el del propio
servidor, así que el helper **compara contra `os.getpgid(0)` y cae a señalar el
pid** si el hijo comparte grupo con el servidor. Degradar es mejor que señalar un
grupo equivocado, y hay un test que lo fija.

El alcance efectivo se escribe en el log del job (`SIGTERM a grupo de procesos
N`), para que el perito lea qué se terminó y no una afirmación genérica.

---

## R11-2 — Un timeout dejaba el lanzador inutilizable · FIXED

**Severidad:** Alta  **Nivel:** CONFIRMED BY INDUCTION

### Cómo apareció

No por lectura. Un test de R11-1 falló con `assert 'running' == 'error'`, y ese
estado no tenía explicación bajo mi modelo del código. La causa resultó ser más
grave que el hallazgo que estaba midiendo.

### Cadena causal

```
timeout -> proc.terminate() mata al agente, no al nieto
    ↓ el nieto heredo el pipe de stdout del agente
`for line in proc.stdout` NUNCA ve EOF — el escritor sigue abierto
    ↓
proc.wait() no corre; job.state se queda en "running" para siempre
    ↓
el `finally: self._slots.release()` no se ejecuta jamas
    ↓  max_jobs = 1 por defecto
todo submit posterior -> 409 "an investigation is already running"
```

### Inducción

```
=== pre-R11 ===
  estado del job tras el timeout : running
  herramienta sigue corriendo    : True
  segundo job                    : RECHAZADO 409 — an investigation is already running

=== post-fix ===
  estado del job tras el timeout : error
  herramienta sigue corriendo    : False
  segundo job                    : ACEPTADO
```

**Un solo timeout —operación normal, sin atacante— dejaba el lanzador Modo 1 de
la web UI muerto hasta reiniciar el servidor**, mostrando además un job
eternamente "en curso" que en realidad ya no existía.

Matar el grupo cierra el pipe, así que el fix de R11-1 resuelve éste por
construcción. Se registra aparte porque su severidad y su consecuencia son
distintas, y porque un lector que sólo vea "terminación de árbol de procesos" no
deduciría que el lanzador se bloqueaba.

---

## Vectores descartados

| Vector | Resultado | Por qué |
|--------|-----------|---------|
| Fuga del slot si `thread.start()` lanza en `submit()` | PLAUSIBLE, no ejecutado | El `acquire` ocurre antes de crear el thread y no hay `try` alrededor. Requiere agotamiento de threads del SO; no se reprodujo, así que queda como hipótesis y no se reporta como confirmada |
| Carrera del `threading.Timer` marcando un job completo como "timeout" | PLAUSIBLE, no ejecutado | La ventana entre el EOF de stdout y `timer.cancel()` existe, pero `_kill` sale temprano si `proc.poll()` ya devolvió código. No se logró forzar de forma determinista |
| `self._jobs` crece sin límite | Sin efecto medible | El log por job está acotado (`deque(maxlen=5000)`); el dict de jobs crece, pero sólo con metadatos y a una entrada por investigación |
| Inyección de comandos vía `cmd` | Sin efecto | `argv` de lista, sin shell; `case_id` validado server-side (falsificado ya en R9) |

## Verificación del fix

- `tests/test_r11_process_tree_termination.py` → 9 tests. **Control negativo ejecutado:** 8 fallan contra el código pre-R11; el único que pasa en ambos estados es el control del oráculo (prueba mi instrumento, no el código).
- `scripts/redteam_round11_process_tree.py` → exit 1 contra el checkout anterior, exit 0 post-fix.
- Suite completa: `2360 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** y de causa ambiental.

### Nota sobre el control negativo

La primera versión del archivo importaba `_signal_process_tree` a nivel de
módulo, así que contra el checkout anterior la colección fallaba con
`ImportError` y los tests de comportamiento no llegaban a correr. **Es el mismo
error que cometí en R9 y que allí quedó corregido**; se repitió acá en el primer
intento. Import diferido, y la nota queda en el propio test.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **Envolver el `acquire` del slot en `try/except` en `submit()`**, para cerrar
   la fuga si la creación del thread falla. No se reprodujo, así que se registra
   como endurecimiento y no como bug.
2. **Aplicar el mismo criterio de árbol a los `subprocess.run(..., timeout=N)`**
   de `memory_forensics`, `pcap_parser` y `registry_timeline_reconstructor`: su
   timeout mata al hijo directo, no a lo que ese hijo haya lanzado.
3. Heredadas y aún abiertas: `integrity` sin capa keyed (R6), `bundle_digest`
   dentro de la traza (R7), clave HMAC a `--hmac-key-file` (R8), advertencia de
   bind no-loopback en la API Modo 5 (R9), formato de cable de las fracciones
   (R10-4).
