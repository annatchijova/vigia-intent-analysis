# SAFARI_WAL_FIX_ANALYSIS.md — Auditoría del hallazgo WAL de Safari (tuck-2019-macos)

> **Estado: INVESTIGACIÓN — cero código de producto tocado.** Verificación
> empírica del hallazgo de `docs/MACOS_MODULES_DESIGN.md` (rama
> `claude/macos-modules-design-xk5ecq`) §2.1/§6.1, ejecutada 2026-07-09
> sobre COPIA de la evidencia en scratchpad. Originales verificados
> intactos por hash antes y después (§6).
>
> Tag de restauración: `pre-safari-wal-analysis-20260709-200840`.
> Método: skill `abductive-engineering` (bucle A–D–I, audit-before-patch);
> redacción bajo skill `daubert-defensible-writing`.

---

## 0. Resumen ejecutivo

Tres resultados, en orden de sorpresa:

1. **El delta WAL es real y exacto** (observación, reproducida): `History.db`
   abierto ignorando el WAL rinde 150 URLs / 196 visitas; con el WAL aplicado,
   198 / 264. Las **48 URLs / 68 visitas** solo-WAL existen y su contenido es
   investigación de tunneling VPN-sobre-HTTP (softether, chisel, crowbar,
   httptunnel, openvpn — §2).
2. **La premisa del encargo es falsa en HEAD** (observación de código):
   `_analyze_safari` **sí usa** `safe_sqlite_connect` — el wrapper
   `macos_forensics.py:420-423` delega a `vigia/sift/_sql_utils.py:57` desde
   la creación del archivo (commit `06edb302`, 2026-07-05). **No hay fix
   mínimo que aplicar en `macos_forensics.py`: ya está aplicado.** El hueco
   que el diseño describe es real pero su causa es otra: el bundle sellado
   del caso se generó en Mode 2 (MCP/strings) sin invocar nunca el módulo
   nativo (§3). La conexión legacy `immutable=1` que la premisa describe
   sobrevive en OTRO archivo: `browser_forensics.py:198-203` (ruta Windows,
   §5).
3. **Las 48 URLs no cambian el veredicto sellado de Mode 1 hoy** (inducción,
   corrida A/B): con WAL y sin WAL el agente emite **ABSTAIN (exit 4)**. Lo
   que sí cambia es todo lo anterior al veredicto: 23 findings vs 0,
   composite 19/20 vs 0, z 1.6 vs 0.0, hipótesis `MOBILE_EVIDENCE_ANALYZED`
   vs `UNDETERMINED` (§4). El techo no es el WAL — es el diseño mono-señal
   mobile (B-052: 1 señal agregada por engine, gate del reasoner ≥3 fuentes
   primarias). El expected del caso es INTENT y **ninguna** de las dos
   corridas lo alcanza.

Implicación: la inversión correcta no es tocar la conexión SQLite (ya
correcta) sino el módulo 1 del diseño macOS (`to_signals()` multi-dominio,
B-052-P2) — el WAL ya entra gratis por `safe_sqlite_connect` cuando ese
módulo exista.

---

## 1. El bucle A–D–I aplicado a la premisa

**Sorpresa registrada:** el diseño afirma que ~48 URLs del WAL "NUNCA entran
al análisis estructurado", y el encargo abduce como causa única:
"`_analyze_safari` no usa `safe_sqlite_connect`".

**Hipótesis rivales generadas (abducción):**

- **H1** — La causa es la conexión: `_analyze_safari` abre con
  `mode=ro&immutable=1` (que ignora el WAL). *Predicción deducida:* el código
  de `_analyze_safari` en HEAD contiene una conexión propia sin la familia de
  sidecars.
- **H2** — La conexión ya es correcta y la causa del hueco es de **ruta**: el
  bundle sellado del caso nunca ejecutó el módulo nativo (se generó en Mode 2
  leyendo strings). *Predicción:* HEAD delega en `safe_sqlite_connect`, y el
  bundle sellado declara `investigation_mode: claude_code_mcp`.
- **H3** — La conexión es correcta pero algo aguas abajo descarta los rows
  del WAL (LIMIT, filtro, orden). *Predicción:* contar rows dentro del
  analizador daría 150, no 198.

**Inducción (tests corridos, resultados):**

| Test | Resultado | H1 | H2 | H3 |
|------|-----------|----|----|----|
| Lectura de `macos_forensics.py:420-423,576` + import línea 30 | delega a `_sql_utils.safe_sqlite_connect` | ✗ refutada | consistente | — |
| `git log -S "_sql_utils"` sobre el archivo | así nació el archivo (`06edb302`, 2026-07-05; solo 2 commits en su historia) | ✗ | consistente | — |
| Bundle sellado `cases/VIGIA-TUCK-2019-MACOS_bundle_claude.json` | `investigation_mode: claude_code_mcp`, commiteado en el MISMO `06edb302` | — | ✓ corroborada | — |
| Corrida A del analizador (§3) | `total_safari_entries = 198` y 23 findings con timestamps del WAL | ✗ | ✓ | ✗ refutada |

**Conclusión de la auditoría de premisa (inferencia):** H2 es la única
hipótesis superviviente. La nota del propio wrapper ayuda a explicar el error
de premisa: su docstring dice "read-only + immutable"
(`macos_forensics.py:421`) mientras la implementación delega a la working
copy con WAL — un signo cuyo interpretante contradice a su objeto. Ese
docstring es candidato a fix documental de una línea (no aplicado — cero
código tocado).

---

## 2. Confirmación empírica del delta WAL (pregunta 1 del encargo)

Protocolo: copia completa de `cases/tuck-2019-macos/` a scratchpad
(`step1_wal_delta.py`); toda conexión sobre la copia; originales hasheados
antes y verificados después (§6).

| Apertura | history_items | history_visits |
|----------|---------------|----------------|
| `mode=ro&immutable=1` (ignora WAL) | 150 | 196 |
| `safe_sqlite_connect` (working copy + WAL) | 198 | 264 |
| **Delta (solo en el WAL de 4.099 KB)** | **+48** | **+68** |

Coincide exactamente con los números del diseño (§6.1 de
MACOS_MODULES_DESIGN). Las 48 URLs solo-WAL, observadas (lista completa en la
salida del script; muestra):

- `github.com/jpillora/chisel`, `github.com/q3k/crowbar`,
  `nocrew.org/software/httptunnel.html` — herramientas de túnel TCP/HTTP
- `softether.org` (7 URLs, incl. `VPN_Server_Behind_NAT_or_Firewall`),
  `openvpn.net`, `radmin-vpn.com`, `freelan.org`
- búsqueda Google: `"vpn software that runs over http"` + su cadena completa
  de resultados (16 redirects `google.com/url?...`)
- ruido benigno entrelazado: alta de Office 365 trial (12 URLs `office.com`/
  `login.live.com`), 2 unsubscribe de LinkedIn

**Lectura Peirce (inferencia, etiquetada como tal):** la sesión solo-WAL es
*consistente con* investigación de evasión de firewall/NAT traversal
(T1090/T1572); también es *consistente con* trabajo IT legítimo (la misma
sesión da de alta un Office 365 trial). La polaridad la decide el contexto
del caso (Tuck: aspirante a organización terrorista), no la URL aislada —
exactamente el tipo de juicio que pertenece al reasoner con corroboración,
no a un patrón por señal.

---

## 3. A/B del analizador nativo: el WAL ES la señal de este caso

`step2_analyzer_ab.py`: dos corridas de `MacOSForensicsAnalyzer().analyze()`
sobre la copia. B simula la conexión legacy vía monkeypatch **en memoria**
(el árbol de producto no se modificó).

| Métrica | A — HEAD (WAL aplicado) | B — simulación `immutable=1` |
|---------|-------------------------|------------------------------|
| `total_safari_entries` | 198 | 150 |
| Findings | **23 × `SAFARI_SUSPICIOUS`** (sev 9/20, patrón `(?i)vpn\|proxy\|tor\s+browser`, T1090) | **0** |
| `composite_score` | 19/20 (0.95) | 0 |
| Señal: z / confidence | **1.6 / 0.95** | **0.0 / 0.0** |

Observación central: en este artefacto, **el 100% de los findings del
analizador Safari proviene de rows que solo existen en el WAL**. Las 150
URLs del DB principal no disparan ningún patrón; las 48 del WAL disparan 23
matches (23 de las 68 visitas solo-WAL casan `vpn|proxy`). Alcance de la
afirmación: este caso, este catálogo de patrones — no generaliza a DBs
checkpointeadas.

Nota de mecánica verificada: el `LIMIT 500` de `_analyze_safari` no trunca
(264 visitas < 500), y el matching corre por visita con `break` al primer
patrón — de ahí 23 y no 48.

---

## 4. Impacto en el veredicto (pregunta 3): NO cambia — y el porqué importa

Mode 1 completo (`vigia_agent.py`) sobre la copia, A/B
(`step3_agent_b.py` para B, mismo monkeypatch en memoria):

| Campo sellado | A — WAL aplicado (HEAD) | B — `immutable=1` |
|---------------|--------------------------|-------------------|
| `agent_verdict` | **ABSTAIN** (exit 4) | **ABSTAIN** (exit 4) |
| `best_hypothesis` | `MOBILE_EVIDENCE_ANALYZED` | `UNDETERMINED` |
| Señales primarias | 1 (z=1.60, conf 0.95) | 0 |
| Alert level | LOW | LOW |
| CAIE | 1 artefacto | 0 señales |

**Respuesta directa:** analizar las 48 URLs adicionales **no cambia el
veredicto sellado de tuck-2019-macos hoy** (ABSTAIN en ambas corridas). El
expected del corpus para este caso es **INTENT** — ninguna corrida lo
alcanza.

**Por qué (cadena observada en la corrida, no especulada):**

1. El engine macOS emite **una** señal agregada (diseño B-052); con findings
   solo-SAFARI la escalera `to_signal` da z=1.6 — bajo el umbral crítico
   (z>3) y bajo el umbral de señal alta (z>2).
2. El AbductiveReasoner v2 exige ≥3 fuentes primarias independientes; con 1
   señal, la ruta mobile-only ni lo ejecuta (limitación documentada B-052 /
   `AUDITORIA_MACOS_NARRATIVA.md`, impresa por el propio agente en la
   corrida).
3. → ABSTAIN estructural, con o sin WAL.

**Dónde SÍ pega el WAL hoy:** una capa antes del veredicto. Sin WAL el caso
queda literalmente vacío (0 señales, `UNDETERMINED`, CAIE sin artefactos);
con WAL hay una señal primaria trazable con 23 findings T1090 que el bundle
narra. Para un investigador humano — y para el módulo 1 del diseño macOS
cuando emita `to_signals()` multi-dominio — esa diferencia es la materia
prima del caso.

**Impacto en el corpus 166/199: ninguno.** El caso del corpus
(`data/cases/VIGIA-TUCK-2019.json`) corre sobre señales ya codificadas en el
JSON convertido, no sobre el disco crudo; ninguna corrida batch invoca
`_analyze_safari` para este caso.

**Y el bundle sellado histórico:** `cases/VIGIA-TUCK-2019-MACOS_bundle_claude.json`
(Mode 2, `claude_code_mcp`, veredicto INTENT vía `reason_with_llm`) se
selló leyendo `History.db-wal` solo como strings crudos — el módulo nativo
nació en el mismo commit que ese bundle y nunca participó de esa
investigación. El hallazgo del diseño describe ese bundle, no el HEAD del
código.

---

## 5. El fix mínimo (pregunta 2) — dónde sí y dónde no

### 5.1 `macos_forensics.py`: NADA que arreglar (el fix hipotetizado ya existe)

`_analyze_safari` → `self._safe_sqlite_connect` (línea 576) →
`safe_sqlite_connect(db_path, "MACOS", logger)` (líneas 420-423) → working
copy + sidecars + WAL (`_sql_utils.py:57-93`, B-071). Verificado por lectura
y por ejecución (§3, corrida A: 198 entries). Único residuo en este archivo:
el **docstring** del wrapper dice "read-only + immutable" y la implementación
es working-copy-con-WAL — corrección documental de 1 línea, sin efecto de
runtime.

### 5.2 Donde el bug descrito SÍ vive: `browser_forensics.py` (ruta Windows)

La conexión que la premisa atribuía a macOS existe textual en
`vigia/sift/browser_forensics.py:198-203`:

```python
@staticmethod
def _connect_ro(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path}?mode=ro&immutable=1"
```

usada por `_parse_chromium` (línea 215) y `_parse_downloads` (línea 260).
Chrome/Edge usan SQLite en modo WAL igual que Safari: una `History` de
Chromium con WAL no-checkpointeado sufre exactamente el falso negativo aquí
cuantificado (hasta el 100% de la señal invisible, §3).

**Fix mínimo diseñado (NO aplicado):**

```python
# browser_forensics.py — reemplazar _connect_ro por el helper B-071:
from vigia.sift._sql_utils import safe_sqlite_connect
...
conn = safe_sqlite_connect(db_path, "BROWSER", logger)   # en los 2 call-sites
if conn is None: ...  # manejar el None (hoy _connect_ro lanza; safe_… retorna None)
```

Alcance: ~6 líneas + manejo del retorno `None` en 2 call-sites + borrar
`_connect_ro`. Protocolo de aplicación (cuando se decida): test rojo primero
(fixture Chromium con rows solo-WAL — se puede generar en laboratorio y
declararse como tal), suite completa, y gate comparativo del corpus
(patrón B-069: los casos Windows con browser podrían mover señal; si algo
empeora, NOT APPLIED).

### 5.3 El vehículo del impacto de veredicto: módulo 1 del diseño macOS

Para que las 48 URLs muevan el veredicto de tuck-2019 hace falta lo que el
diseño ya especifica: emisión multi-dominio (`to_signals()`, B-052-P2) para
que Safari/quarantine/plists cuenten como fuentes separadas ante el gate ≥3
del reasoner — con el arnés de pins B-086 puesto y re-corrida de corpus
completa (cambia todos los veredictos mobile). El WAL no requiere trabajo
adicional ahí: `safe_sqlite_connect` ya lo aplica.

---

## 6. Cadena de custodia de esta verificación

- Evidencia original: `cases/tuck-2019-macos/` — **no abierta jamás por
  SQLite en este análisis**; solo `sha256sum` y `cp`.
- SHA-256 de los 6 archivos registrados ANTES de copiar
  (`scratchpad/originals_before.sha256`) y re-verificados DESPUÉS de todas
  las corridas: `sha256sum -c` → **6/6 OK** (incluye `History.db-wal`
  `0f32202d…`, `History.db` `b5d0d9df…`).
- Todas las conexiones SQLite ocurrieron sobre `scratchpad/tuck-copy/` o
  sobre las working copies efímeras que `safe_sqlite_connect` crea y borra.
- Scripts de reproducción (scratchpad de la sesión): `step1_wal_delta.py`,
  `step2_analyzer_ab.py`, `step3_agent_b.py`; bundles A/B:
  `bundle_A.json`, `bundle_B.json`. Los monkeypatches viven solo en la
  memoria de esos procesos: `git status` del repo limpio salvo este
  documento.

---

## 7. Claim audit (formato daubert-defensible-writing)

| Claim | Capa | Evidencia | Nivel |
|-------|------|-----------|-------|
| 48 URLs / 68 visitas viven solo en el WAL | Observación | step1 sobre la copia; coincide con MACOS_MODULES_DESIGN §6.1 | Confirmado por ejecución (2 corridas independientes, misma cifra) |
| `_analyze_safari` usa `safe_sqlite_connect` en HEAD | Observación | `macos_forensics.py:30,420-423,576`; `git log -S` | Hecho de código |
| 23 findings/z=1.6 con WAL; 0/z=0 sin WAL | Observación | step2, salida completa | Confirmado por ejecución |
| El veredicto sellado no cambia (ABSTAIN ambos) | Observación | step3, bundles A/B, exit codes | Confirmado por ejecución (1 corrida por brazo, determinista por diseño del pipeline) |
| El techo del veredicto es B-052 (mono-señal + gate ≥3), no el WAL | Inferencia | mensaje del propio agente en la corrida + `AUDITORIA_MACOS_NARRATIVA.md` | Corroborada — mecanismo impreso por el pipeline, no deducido por fuera |
| La sesión WAL es investigación de evasión | Inferencia | contenido de las 48 URLs | Consistente-con; rival benigno (trabajo IT + Office trial) NO eliminado |
| `browser_forensics._connect_ro` sufre el mismo falso negativo | Inferencia | lectura de código + analogía con §3 | **No ejecutada** — predicción falsable con fixture Chromium-WAL; ese es su test |

**Bounds:** todo lo cuantificado aplica a este artefacto y este catálogo de
patrones; "100% de la señal en el WAL" no generaliza a DBs checkpointeadas.
La corrida B simula la conexión legacy por monkeypatch — asume que el único
efecto relevante de `_connect_ro` es `immutable=1` (verificado contra su
código, 5 líneas).

**Falsificadores:** (a) una corrida futura de Mode 1 sobre tuck-2019 que NO
sea ABSTAIN sin cambios en B-052 reabriría §4; (b) un fixture Chromium con
WAL que `_connect_ro` lea completo refutaría §5.2; (c) si el docstring de
`_safe_sqlite_connect` resulta describir un modo real configurable y no un
texto desactualizado, §1 pierde su explicación del error de premisa.

**Limitaciones:** no se corrió la suite (cero código tocado — nada que
regresar); no se midió Chrome real (el caso no tiene Chrome en disco, solo
la inferencia F-003 vía QuarantineEvents); `_analyze_quarantine` produjo 0
findings en ambos brazos y no se investigó por qué (fuera de alcance).

---

*SAFARI_WAL_FIX_ANALYSIS — 2026-07-09 | premisa auditada antes de parchear:
el parche ya existía; el hueco real está en la ruta del bundle (B-052-P2) y
en `browser_forensics._connect_ro` | originales intactos 6/6.*
