# Security Audit — VIGÍA web UI network exposure

## Red Team Round 9 — The Shared Variable

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** la superficie expuesta de `vigia/ui/` — confinamiento de rutas de evidencia,
guard cross-site, validación del lanzador de investigaciones, y dirección de escucha.
**Fuera de alcance:** los verificadores (R5–R8), el scorer.
**Base:** `claude/team-network-session-eiicdu` @ `8a2863d`.
**Runtime:** CPython 3.11.15
**Evidencia reproducible:** `tests/test_r9_ui_bind_exposure.py`

## Modelo de amenaza

- El atacante **PUEDE**: hablar HTTP con el puerto de la UI desde otra máquina, si el
  puerto está alcanzable.
- El atacante **NO PUEDE**: ejecutar código local, leer el filesystem del servidor por
  otros medios, ni obtener credenciales (no hay ninguna que obtener — ese es el punto).
- **Frontera cruzada:** el borde de red de un servicio sin capa de autenticación que
  lanza subprocesos.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R9-1 | **Alta** | **CONFIRMED BY INDUCTION** | vuln (acoplamiento de configuración) | `VIGIA_HOST` es leída por **dos** servicios. La remediación que INSTALL.md documenta para la API Modo 5 mueve también la web UI —sin auth y con lanzador de subprocesos— a todas las interfaces, en silencio. | **FIXED** |

Tres hipótesis previas quedaron **falsificadas** al medirlas, y eso es la mitad del
valor de la ronda: el confinamiento de rutas, la validación del `case_id` y el guard
cross-site son correctos. El defecto no estaba en ninguna de las defensas que se
revisan primero, sino en una variable de entorno compartida entre dos servicios con
consecuencias distintas.

---

## R9-1 — Una variable, dos servicios, una exposición silenciosa · FIXED

**Severidad:** Alta  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad (acoplamiento de configuración)

### Sorpresa

`vigia/ui/__main__.py` documenta lo correcto: *"Binds loopback by default (no auth
layer exists)"*. `vigia/api_defaults.py` lo refuerza: *"The HTTP gateway intentionally
has no application authentication layer. It must therefore listen only on loopback."*
Y `INSTALL.md` avisa explícitamente:

> **Security boundary:** by default the API listens only on `127.0.0.1`.
> Do not set `VIGIA_HOST=0.0.0.0` [...] If remote access is required, place it behind
> an authenticated reverse proxy and a deliberate network access policy.

Todo correcto — y todo escrito en la sección de la **API**. La sorpresa es quién más
lee esa variable.

### CODE FACT

```
vigia/vigia_api.py:216:   host=os.environ.get("VIGIA_HOST", DEFAULT_HOST)   # Modo 5, puerto 8000
vigia/ui/__main__.py:20:  host = os.environ.get("VIGIA_HOST", DEFAULT_HOST) # web UI, puerto 8010
```

Un operador que sigue la salida documentada —exponer la API detrás de un proxy inverso
autenticado en el 8000— setea `VIGIA_HOST=0.0.0.0`. El 8010 se va con ella, sin proxy
y sin nada que lo anuncie.

### Deducción → Inducción (ejecutada con el servidor real)

Predicción: con `VIGIA_HOST=0.0.0.0`, la UI escucha en todas las interfaces y sus
endpoints responden sin credencial alguna.

```
INFO: Uvicorn running on http://0.0.0.0:8099

POST /api/investigations  (sin Origin, sin Referer, JSON)  -> HTTP 422
     {"detail":"evidence path does not exist"}
GET  /api/evidence        (sin credencial)                 -> inventario completo
```

**La predicción se cumple.** El 422 es validación de negocio: la petición atravesó el
guard cross-site y llegó al lanzador. Con una ruta de evidencia válida habría lanzado
`vigia_agent.py` como subproceso. No hay puerta de autenticación en ningún punto.

### Alcance honesto de la medición

Se confirmó el bind a `0.0.0.0` y la ausencia de autenticación desde loopback, dentro
del sandbox. **No** se demostró un atacante remoto en una LAN — eso no es reproducible
acá. El bind más la ausencia de auth alcanzan para establecer la exposición; afirmar
"explotado remotamente" no.

### Cadena causal

```
INSTALL.md §11 (API): "if remote access is required, place it behind a proxy"
    ↓ el operador setea VIGIA_HOST=0.0.0.0 y proxifica el 8000
vigia/ui/__main__.py lee la MISMA variable
    ↓ la UI liga 0.0.0.0:8010, sin proxy
sin capa de auth  +  POST /api/investigations lanza vigia_agent.py
    ↓
ejecución de subprocesos y lectura del inventario de evidencia, sin credencial
```

### Fix

Dos cambios, y el segundo importa más que el primero.

1. **Desacoplar la variable.** La UI lee `VIGIA_UI_HOST` primero. Un operador puede
   ahora exponer la API sin arrastrar la UI: `VIGIA_HOST=0.0.0.0 VIGIA_UI_HOST=127.0.0.1`.
   `VIGIA_HOST` se sigue leyendo como fallback (retrocompatibilidad).

2. **Negarse, no advertir.** Una dirección no-loopback —venga de donde venga— aborta el
   arranque con un mensaje que nombra la variable culpable, explica por qué importa y da
   las dos salidas. Es la elección honest-degradation del repositorio: una exposición que
   nadie pidió es peor que un servidor que no levanta y explica por qué. El escape
   deliberado existe: `VIGIA_UI_ALLOW_REMOTE=1`, que además imprime una advertencia en
   cada arranque.

```
REFUSING to bind '0.0.0.0' (from VIGIA_HOST): the web UI has no authentication layer
  and POST /api/investigations launches vigia_agent.py as a subprocess.
  VIGIA_HOST is shared with the Mode 5 API (vigia/vigia_api.py). Setting it
  for the API also moves this UI off loopback.

  Keep the UI local while the API listens elsewhere:
      VIGIA_UI_HOST=127.0.0.1
  Or accept the exposure deliberately, behind your own authenticated boundary:
      VIGIA_UI_ALLOW_REMOTE=1
```

`is_loopback` no da por local un nombre que no puede evaluar léxicamente: sin
resolución DNS, `mi-workstation` se rechaza. Sobre-rechazar es el lado correcto del error.

---

## Vectores falsificados — las defensas que sí funcionan

Los tres candidatos que uno revisa primero resultaron correctos. Se registran con su
razón para que el próximo auditor no repita el barrido.

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| **Traversal en `evidence_path`** | FALSIFICADO por lectura | `evidence_paths.resolve_evidence_path` rechaza rutas absolutas y `..`, exige que el prefijo coincida con una raíz allowlisteada **comparando tuplas de `parts`** (no prefijos de string, así que `cases2/` no cuela), rechaza cualquier componente symlink entre raíz y hoja, y exige `lstat` de archivo regular o directorio. El TOCTOU está declarado como limitación en el propio docstring — no se vende como hallazgo |
| **`case_id` validado sólo en el cliente** | FALSIFICADO | El modelo Pydantic sólo pone `max_length=64` y el regex vive en `app.js`, lo que parecía validación client-side. Pero `jobs.submit` aplica `CASE_ID_RE` del lado del servidor antes de construir la ruta de salida. Es colocación de la defensa, no ausencia |
| **CSRF vía formulario cross-site** | FALSIFICADO por razonamiento | El middleware exige `Content-Type: application/json` en todo POST/PUT/PATCH/DELETE. Un formulario HTML no puede fijar ese content-type, y un `fetch` que sí puede dispara preflight CORS que el servidor no responde con cabeceras permisivas. El guard de Origin/Referer permite la ausencia de ambas cabeceras, pero eso no es alcanzable desde un browser cross-site |
| **Inyección de argumentos vía `examiner_id` / `acquisition_tool`** | Sin efecto | Van a un `argv` de lista, sin shell, en una posición de valor fija. Un valor que empieza con `-` hace fallar el job (argparse), que es un DoS del propio job, no una inyección |

## Verificación del fix

- `tests/test_r9_ui_bind_exposure.py` → 25 tests. **Control negativo ejecutado:** los tres tests de comportamiento (`TestEntryPointRefuses`, `TestLauncherScript`) fallan contra el código pre-R9 — el proceso arranca y liga en vez de negarse.
- Los tres caminos legítimos, medidos con el servidor real: sin variables → `127.0.0.1`; `VIGIA_HOST=0.0.0.0` + `VIGIA_UI_HOST=127.0.0.1` → `127.0.0.1` (el desacople funciona); `VIGIA_UI_ALLOW_REMOTE=1` → `0.0.0.0` con advertencia en cada arranque.
- Suite completa: ver el commit. Los 7 fallos restantes son **pre-existentes** y de causa ambiental.

### Nota sobre el control negativo

La primera versión del archivo importaba las funciones nuevas a nivel de módulo, así que
contra el código pre-R9 la colección fallaba con `ImportError`. Eso prueba que las
funciones no existían, no que los tests atrapen la conducta vieja. Se pasó a import
diferido para que los tests de comportamiento corran de verdad contra el checkout
anterior y fallen por el motivo correcto.

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **Aplicar el mismo criterio a la API Modo 5.** `vigia_api.py` sigue ligando lo que
   `VIGIA_HOST` diga, sin negarse. Ahí la exposición es *intencional* en el flujo
   documentado (proxy autenticado delante), así que la decisión es distinta: una
   advertencia ruidosa en cada arranque no-loopback, más que una negativa.
2. **Un token local para la UI.** El guard cross-site protege contra el browser de un
   tercero, no contra un cliente HTTP directo. Con `VIGIA_UI_ALLOW_REMOTE=1` el operador
   queda entero a cargo del borde. Un token compartido en el arranque sería defensa en
   profundidad barata.
3. Heredadas y aún abiertas: `integrity` sin capa keyed (R6), `bundle_digest` dentro de
   la traza (R7), clave HMAC a `--hmac-key-file` (R8).
