# Security Audit — VIGÍA web UI rendering of untrusted bundles

## Red Team Round 10 — Shape at the Boundary

**Date:** 2026-09-11  **Method:** Abductive Engineering (A–D–I) + Red-Team Auditing (epistemic ladder)
**Scope:** cómo la web UI renderiza el contenido de un bundle — escapado, tipos, y qué
dice cuando no puede. **Fuera de alcance:** los verificadores (R5–R8), la exposición de
red (R9).
**Base:** `claude/team-network-session-eiicdu` @ `c64fde7`.
**Runtime:** CPython 3.11.15, Node v22.22.2
**Evidencia reproducible:** `scripts/redteam_round10_render_types.mjs`, `tests/test_r10_render_type_coercion.py`

## Modelo de amenaza

- El atacante **PUEDE**: entregar un archivo de bundle que el perito copia a `cases/` o
  `results/` para inspeccionarlo. Ése es el caso de uso de la UI, no un abuso de ella.
- El atacante **NO PUEDE**: ejecutar código en la estación, ni alcanzar la UI por red
  (R9 cerró eso).
- **Frontera cruzada:** el borde entre un archivo JSON no confiable y la forma de
  display que consume el frontend.

## Leyenda epistémica

CODE FACT · PLAUSIBLE HYPOTHESIS · **CONFIRMED BY INDUCTION** · FALSIFIED

## Resumen ejecutivo

| ID | Severidad | Nivel | Bucket | Hallazgo | Estado |
|----|-----------|-------|--------|----------|--------|
| R10-1 | Media | **CONFIRMED BY INDUCTION** | vuln (robustez) | Seis campos de un bundle con el tipo equivocado hacen **lanzar** al renderizador. Uno de ellos (`artifacts` como string) ni siquiera es hostil: es una variante de esquema plausible. | **FIXED** |
| R10-2 | Baja | **CONFIRMED BY INDUCTION** | honest degradation | El fallo se mostraba como **"La petición falló"**. La petición no había fallado: el bundle estaba malformado. Misatribución de causa en una herramienta forense. | **FIXED** |
| R10-3 | — | **FALSIFIED** | — | Hipótesis de entrada: XSS almacenado desde un bundle de terceros. El frontend escapa de forma consistente y la CSP no tiene `unsafe-inline`. | Refutada |
| R10-4 | Baja | **CONFIRMED BY INDUCTION** | vuln (valor inventado) | `bool` es subclase de `int` en Python: `is_serialized_fraction` aceptaba `{"num": true}` y lo mostraba como `True/1`. La copia de `app.js` lo rechazaba. **No alcanza el camino del sello** — la canonicalización chequea `bool` antes que `int` en sus tres copias. | **FIXED** |

---

## R10-3 — FALSIFICADO: no hay XSS desde un bundle

**Nivel:** FALSIFIED

La hipótesis de entrada era la obvia para una UI que renderiza archivos ajenos:
inyección de HTML desde un campo del bundle. Se descartó midiendo, no suponiendo.

- Todo valor derivado del bundle pasa por `esc()`, que escapa `& < > " '`. El barrido de
  interpolaciones sin `esc()` en `app.js` devuelve sólo constantes, claves de i18n y
  plantillas anidadas cuyo interior sí escapa.
- El visor de JSON crudo termina en `return esc(JSON.stringify(o))` para todo escalar.
- El renderizado de Fractions —el único sitio que interpola en un atributo con comillas
  simples— está **tipado en ambos lados**: `isinstance(obj.get("num"), int)` en Python y
  `Number.isInteger(o.num)` en JS. Un payload de string no toma esa rama.
- La CSP del documento es `default-src 'self'; img-src 'self' data:; style-src 'self';
  script-src 'self'` — sin `unsafe-inline`, con todo el JS en archivos externos.

La afirmación de INSTALL.md ("100% offline, tripwire CSP, apto para estaciones
air-gapped") se sostiene en lo que se pudo verificar por lectura del documento servido.

Buscando esa vía apareció otra cosa.

---

## R10-1 — Seis campos con el tipo equivocado hacen explotar el render · FIXED

**Severidad:** Media  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad (robustez)

### Sorpresa

En `toolLogTab`, tres campos vecinos, una línea de distancia:

```js
${esc((e.timestamp || "").slice(0, 23))}
${e.entry_hash ? " · entry " + esc(e.entry_hash.slice(0, 16)) + "…" : ""}
${e.prev_hash  ? " · prev "  + esc(String(e.prev_hash).slice(0, 16)) + "…" : ""}
```

`prev_hash` está envuelto en `String(...)`. Sus dos vecinos no. Esa asimetría no es
casual: es la huella de un arreglo puntual —alguien se topó con el caso una vez y
parcheó el campo que tenía delante— sin barrer la clase.

### Deducción → Inducción (ejecutando las funciones reales con node)

Predicción: si el normalizador pasa los campos crudos, un tipo no-string en
`timestamp` o `entry_hash` hace lanzar al renderizador.

Primero se midió el normalizador: un bundle real con `"timestamp": 1234567890` y
`"entry_hash": 42` llega al frontend **tal cual**, como `int`. Después se extrajeron
`esc`, `toolLogTab` y `findingsTab` de `app.js` y se ejecutaron contra cada tipo
hostil en cada campo — variant sweep, no un caso suelto:

```
toolLogTab / entry.timestamp   LANZA  (e.timestamp || "").slice is not a function
toolLogTab / entry.entry_hash  LANZA  e.entry_hash.slice is not a function
toolLogTab / entry.prev_hash   ok            <- el que tenía String()
toolLogTab / audit.timestamp   LANZA  (e.timestamp || "").slice is not a function
findingsTab / mitre_ttps       LANZA  (f.mitre_ttps || []).map is not a function
findingsTab / artifacts        LANZA  f.artifacts.join is not a function
findingsTab / tools_used       LANZA  f.tools_used.join is not a function
```

**Seis sitios, una sola clase:** un método de string o de array invocado sobre lo que
el bundle haya puesto ahí.

El caso de `artifacts` merece nombre propio: el tipo que lo rompe es **string**, no un
payload. Un bundle escrito por otra herramienta que ponga `"artifacts": "/a, /b"` en
vez de una lista rompe la pestaña. Esto no es sólo adversarial — es interoperabilidad.

### Fix — en el límite, no campo por campo

`normalizer.py` es el borde entre un archivo no confiable y la forma de display, y su
propio docstring ya tenía la doctrina: *"Missing fields become None plus an entry in
warnings[] — never an invented value"*. El fix la extiende de campos ausentes a campos
con la forma equivocada:

```python
def coerce_text(value, label, warnings)   # no-texto → texto, y se declara
def coerce_list(value, label, warnings)   # escalar → lista de 1, y se declara
def coerce_entry_text(entries, fields, label, warnings)
```

Nunca se inventa un valor y nunca se retipa en silencio: el desajuste entra a
`warnings[]`, que la UI ya muestra arriba del bundle.

```
⚠ tool_execution_log[0].timestamp: se esperaba texto, se encontro int — mostrado como texto
⚠ finding[0].artifacts: se esperaba lista, se encontro str — envuelto en una lista de un elemento
```

En el frontend, `txt()` y `arr()` como **defensa en profundidad** — no como el
arreglo. Un renderizador de una herramienta forense no debería explotar por el tipo de
un campo ajeno aunque el normalizador falle.

Una entrada que no es un objeto se **omite y se declara**, en vez de romper la lista.

---

## R10-2 — El banner misatribuía la causa · FIXED

**Severidad:** Baja  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** honest degradation

El router atrapa toda excepción y llama `errorView(err)`, que decía:

```
La petición falló — e.timestamp.slice is not a function
```

Falla visible, que es lo correcto. Pero la petición **no** falló: devolvió 200 con un
bundle malformado. Para un perito, "reintentá, la red falló" y "este archivo tiene un
campo con el tipo equivocado" mandan a mirar lugares distintos. En una herramienta
cuyo valor es la trazabilidad de por qué algo no se pudo determinar, atribuir a la red
un defecto del archivo es el error más caro de los dos.

`api()` marca ahora sus propios errores (`err.kind = "request"`) y el banner distingue,
en ambos idiomas:

```
No se pudo mostrar este bundle (campo malformado) — …
```

---

## Vectores descartados (no explotables)

| Vector | Resultado | Por qué falló |
|--------|-----------|---------------|
| XSS almacenado desde un campo del bundle (R10-3) | FALSIFICADO | `esc()` consistente, `esc(JSON.stringify(o))` en el visor crudo, CSP sin `unsafe-inline` |
| Inyección en el atributo `title` del render de Fractions | FALSIFICADO | Tipado en ambos lados: `isinstance(int)` y `Number.isInteger` |
| `seq`, `tool`, `target`, `result_summary`, `action`, `note` con tipos hostiles | Sin efecto | Pasan por `esc()`, que hace `String(v)` antes de reemplazar |
| `prev_hash` con tipo hostil | Sin efecto | Es el único campo que ya tenía `String(...)` — y por eso mismo delató al resto |

## Verificación del fix

- `scripts/redteam_round10_render_types.mjs` → barrido de 5 tipos × 27 campos sobre los renderizadores reales. **0 lanzan** post-fix; **6 lanzan** contra el `app.js` pre-R10 (el script acepta cualquier checkout).
- `tests/test_r10_render_type_coercion.py` → 15 tests. **Control negativo ejecutado:** 14 fallan contra el código pre-R10; el único que pasa en ambos estados es el control (un bundle limpio no debe ganar ruido). Honestidad sobre el control: los tests unitarios de `coerce_*` fallan allí por `AttributeError` (la función no existía), no por conducta — los que fallan por conducta son el barrido de node, los tres del banner y `test_tool_log_text_fields`.
- Suite completa: `2325 passed, 211 skipped, 28 xfailed`. Los 7 fallos restantes son **pre-existentes** y de causa ambiental.

---

## R10-4 — Las dos copias del predicado de Fraction no decían lo mismo · FIXED

**Severidad:** Baja  **Nivel:** CONFIRMED BY INDUCTION  **Bucket:** vulnerabilidad (valor inventado)

Registrado primero como recomendación 2 de esta ronda y corregido a continuación.

### Sorpresa

`isinstance(True, int)` es `True` en Python. `Number.isInteger(true)` es `false`
en JS. Dos copias del mismo predicado, dos respuestas distintas:

```
{"__fraction__": true, "num": true, "den": 1}  ->  display 'True/1'
{"__fraction__": true, "num": 1, "den": true}  ->  display '1/True'
{"__fraction__": true, "num": 1, "den": false} ->  denominador cero semántico
```

Mostrar `True/1` como si fuera una fracción es inventar un valor, que es
exactamente lo que el docstring del normalizador prohíbe.

### Alcance — lo primero que se midió, porque decide la severidad

**La clase no alcanza el camino del sello.** Las tres copias de la
canonicalización —`vigia/core/canonicalize.py`, `vigia/models/ebs.py` y
`verify_tool_log.py`— chequean `isinstance(obj, bool)` **antes** que
`isinstance(obj, int)`, así que `True` y `1` canonicalizan distinto y ningún
hash cambia. Eso es una falsificación, no una suposición, y queda fijada por
test para que no regresione en silencio.

El barrido de `isinstance(..., int)` en el repositorio devolvió cuatro
consumidores del predicado `__fraction__`, con cuatro estricteces distintas.
Sólo uno estaba mal en un camino que se muestra a un humano.

### Fix

`_is_exact_int` rechaza `bool`. Un dict etiquetado `__fraction__` que no pasa el
predicado se deja **crudo** y se declara con su ruta, en línea con R10-1:

```
⚠ extra.a[0]: lleva la etiqueta __fraction__ pero num/den no son enteros exactos
  (num=bool, den=int) — mostrado sin convertir
```

Variante del mismo barrido: `planner_adapter._to_fraction` no guardaba contra
`bool` —mientras `_signal_z_fraction`, quince líneas más abajo **en el mismo
módulo**, sí lo hacía; la misma asimetría que delató a `prev_hash` en R10-1— y
dejaba la rama del dict fuera de su `try`. Honestamente: `_to_fraction` no tiene
llamadores en este commit, así que es endurecimiento de un helper sin cablear,
no la reparación de un camino vivo.

### La divergencia que encontró el propio test

El lockstep entre las dos copias encontró un segundo caso que la lectura previa
**no** había predicho: `{"num": 1.0}`. Python lo rechaza; JS lo acepta, porque
no tiene tipo entero separado y `JSON.parse("1.0")` produce el mismo Number que
`JSON.parse("1")`. El lado JS **no puede** ver la diferencia sin cambiar el
formato de cable.

Consecuencia observable, documentada en vez de escondida: un bundle con
`{"num": 1.0, "den": 2}` se muestra como `1/2` en la pestaña de JSON crudo —que
lee el archivo sin pasar por el normalizador— y como un dict sin convertir, con
su warning, en las vistas normalizadas. Python queda del lado estricto a
propósito: el productor emite `obj.numerator`, siempre un int exacto, así que un
`1.0` significa que el bundle lo escribió otra cosa.

Un test de lockstep que encuentra una divergencia que el autor no había previsto
es el argumento entero a favor de escribirlo en vez de asumir que dos copias
coinciden.

### Verificación

`tests/test_r10_4_fraction_bool.py` → 26 tests; **16 rojos** contra el código
previo. Los que pasan en ambos estados son los controles (enteros legítimos, el
bundle limpio sin ruido) y las dos falsificaciones del camino del sello.

---

## Recomendaciones (fuera del alcance de este cambio — sólo registradas)

1. **Extender la coerción a los normalizadores EBS v1 y agent_audit.** El fix cubre los
   campos que hoy rompen el render, medidos. Los otros dos normalizadores construyen su
   propia forma de display y no fueron barridos con el mismo rigor.
2. ~~`isinstance(obj.get("num"), int)` acepta `True`~~ — **corregido**, ver R10-4
   arriba. La medición mostró que era algo más que cosmético (`'1/True'`, y un
   denominador cero semántico con `den=false`) y destapó una divergencia
   irreducible con la copia de JS que quedó documentada.
3. **Formato de cable para las fracciones.** La divergencia de `1.0` sólo se
   cierra serializando `num`/`den` como strings, para que el lado JS pueda ver
   lo que el lado Python ve. Es un cambio de formato — decisión, no parche.
4. Heredadas y aún abiertas: `integrity` sin capa keyed (R6), `bundle_digest` dentro de
   la traza (R7), clave HMAC a `--hmac-key-file` (R8), advertencia de bind no-loopback en
   la API Modo 5 (R9).
