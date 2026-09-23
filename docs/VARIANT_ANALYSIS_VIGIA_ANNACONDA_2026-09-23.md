# Variant analysis: VIGÍA y ANACONDA

Fecha: 2026-09-23  
Método: análisis por primitive, caller y boundary; no por coincidencia textual.

## Alcance y límite

Se buscó la familia derivada de los dos hallazgos corregidos en Zaynor:

1. texto de excepciones o detalles de implementación que crucen un boundary HTTP;
2. creación insegura de temporales con nombre predecible (`mktemp`).

La revisión fue estática sobre los HEAD locales de VIGÍA (`4c406ea5`) y
ANACONDA (`7d3169e`). No se modificó ninguno de esos repositorios, no se
ejecutaron endpoints desplegados y no se volvió a correr un scanner sobre ellos.

## VIGÍA

### Resultado

**No se confirmó un equivalente del hallazgo A1 de Zaynor en el endpoint
principal de análisis.**

`vigia/vigia_api.py` expone dos errores de validación con `HTTPException(422,
str(exc))`, en `/analyze/path` y `/analyze/json`. Los callers sólo entregan
mensajes constantes de las validaciones de transporte:

- `case exceeds the ... API limit`;
- `case JSON must be an object`;
- `case JSON could not be serialized safely`;
- `case path ...` con categorías de confinamiento.

No se observó allí una ruta que devuelva la ruta absoluta temporal, un traceback,
el texto de una excepción inesperada ni un secreto. Las excepciones no
previstas de ambos endpoints se registran y se convierten en `500 Error interno
en el pipeline forense.`

La UI (`vigia/ui/server.py`) también propaga `JobValidationError` y
`JobBusyError`, pero sus callers están construidos a partir de errores de
validación acotados (`EvidencePathError`, regex de `case_id`, disponibilidad de
un slot). El mensaje de allowlist puede revelar la política del producto, no un
detalle interno sensible del proceso.

### Temporales

No apareció `tempfile.mktemp`. Los puntos revisados usan
`NamedTemporaryFile`/`TemporaryDirectory` y eliminan el artefacto temporal.
Eso no prueba por sí solo una política perfecta de disponibilidad, pero no es
la misma primitive insegura de A2.

## BUG PENDIENTES / PENDING BUGS — VIGÍA

Estos puntos quedan explícitamente pendientes; este commit documenta el riesgo
y no modifica el código operativo:

- **V-01 — boundary wording / redacción del boundary (low):** revisar si los
  mensajes de `EvidencePathError` y `CasePathError` deben ser aún más genéricos
  para una instancia expuesta fuera de loopback. No hay impacto remoto probado.
- **V-02 — endpoint validation regression / regresión de validación:** agregar
  tests de contrato que comprueben que los errores permanecen en la taxonomía
  pública y que una excepción inesperada siempre devuelve el mensaje genérico
  `500`.
- **V-03 — deployed verification / verificación desplegada:** probar una
  instancia real detrás de su boundary de autenticación y conservar sólo las
  respuestas HTTP necesarias como evidencia. Esta auditoría no demostró
  impacto en deployment.
- **V-04 — temporary lifecycle / ciclo de vida temporal:** mantener una prueba
  de concurrencia y cleanup para `NamedTemporaryFile` y snapshots, sin
  convertirla en un finding A2 no demostrado.

Finding de variant analysis: **no confirmado**. El informe se publica, pero no
se presenta como un fix aplicado.

## ANACONDA

### Resultado

**Familia A1 confirmada por inspección de boundary, sin remediación.**

`service/app.py` contiene varios callers HTTP que colocan `str(exc)` en
`HTTPException.detail`, entre ellos:

- `GET /catalog`: `catalog.NotPublishedError` → `400`;
- `POST /fleet-investigate`: `PermissionError` → `403`;
- `POST /injection-demo` y `_authorize`: errores de principal/autorización →
  `403`;
- `POST /cases/{case_id}/cycle`: `ConcurrentModificationError` → `409`;
- `POST /cases/{case_id}/escalations/{index}/acknowledge`:
  `MissionError`/`ConcurrentModificationError` → `404`/`409`.

Además, `/investigate` convierte `summary["error"]` y `verdict["error"]` de
capas internas directamente en un `400`. Eso hace que el impacto dependa del
texto producido por esos callers, pero la violación de la invariante de
boundary ya está demostrada por el flujo de datos: una excepción interna no se
normaliza a una categoría pública antes de responder.

No se demostró aquí secreto, traceback ni endpoint desplegado. El hallazgo es
de exposición potencial de detalles de implementación/política y requiere
reproducción contra una instancia antes de graduar severidad.

### Temporales

No se encontró `mktemp`. La creación observada en el flujo de casos usa
`tempfile.mkdtemp(prefix="annaconda-case-")`, que reserva el directorio de
forma atómica. No se reporta A2 como variante confirmada.

### Estado y custodia

Este resultado es **report-only** por instrucción explícita: no se editó
ANACONDA, no se creó commit y no se hizo push. El hallazgo queda deliberadamente
abierto para una revisión posterior; no se debe cerrar ni presentar como
remediado.

## Siguiente paso recomendado

Si se retoma la investigación, reproducir un caller por grupo en una instancia
local controlada, capturar sólo la respuesta HTTP y comparar el texto expuesto
con los logs. Después decidir si la normalización corresponde a `400/403/404`
genéricos o a mensajes de validación diseñados explícitamente para el usuario.
