# Auditoría — Falsos Negativos en Modo Agente vs Modo Claude Code

**Fecha:** 2026-07-02
**Alcance:** ruta de extracción de evidencia raw y mapeo señal→veredicto del
modo agente (`vigia_agent.py`, Mode 1/4) comparada con el modo Claude Code / MCP
(Mode 2).
**Motivación:** el usuario observa **falsos negativos sistemáticos en modo agente**
(evidencia maliciosa → veredicto benigno / "NO EVIL DETECTED") que **no ocurren
en modo Claude Code** sobre los mismos artefactos.
**Método:** lectura de código + reproducción empírica de los mecanismos donde fue
posible. Cada hallazgo cita `archivo:línea`. Los reproducidos se marcan
`[REPRODUCIDO]`.

---

## Estado de correcciones (2026-07-02, rama `claude/vigia-hash-chain-hardening`)

| Hallazgo | Estado | Corrección |
|---|---|---|
| **P0-A** ABSTAIN inexistente | ✅ CORREGIDO | `classify_agent_verdict()` + exit code 4 = ABSTAIN. Error/ausencia de señal → ABSTAIN, no benigno. Veredicto embebido y sellado en el bundle (`agent_verdict`). |
| **P0-B** PathGuard vs `VIGIA_EVIDENCE_DIR` | ✅ CORREGIDO | `_evidence_allowlist()` incluye `VIGIA_EVIDENCE_DIR`; el agente publica el dir de `--evidence` en esa variable. Reproducción invertida en test. |
| **P1-C** filtro de IP por substring | ✅ CORREGIDO | `_is_external_ip()` usa `ipaddress.is_global`; ya no descarta C2 externos con subcadena de red privada, ni todo IPv6. |
| **P1-D** dependencia ausente → benigno | ✅ CORREGIDO (memoria) | Adaptador vol3: si ningún plugin corre → `UNANALYZED_ARTIFACT` (→ABSTAIN). Resto de dependencias ausentes → 0 señales → UNDETERMINED → ABSTAIN vía P0-A. |
| **P1-E** `.log` muere por sufijo | ✅ CORREGIDO | `event_log_correlator` intenta `.log/.txt`, marca `UNANALYZED_ARTIFACT` en `analysis_notes` para formatos no soportados y `.evtx` sin librería `Evtx`. |
| **P1-A** browser_forensics stub | ✅ CORREGIDO | Parser SQLite real (Chromium `History` + Firefox `places.sqlite`), read-only inmutable, basename Windows/POSIX, cableado en el agente por marcador. DB ilegible → `unanalyzed` (→ABSTAIN). |
| **P1-A** amcache/shellbag/usb stub | ✅ HONESTO | Emiten `unanalyzed=True` (0 hallazgos = "no analizado", no "limpio"). Implementación real diferida (requiere `regipy` + hives de test). |
| **P1-D** orquestador frágil | ✅ CORREGIDO | Construcción resiliente (`_safe_engine`): una dependencia ausente (`vol`/`rip.pl`) deshabilita solo su motor, no tumba el pipeline. Motores core guardados con `if self.X`. |
| **P0-C** PathGuard rechaza directorios | ✅ CORREGIDO | `validate(..., allow_dir=True)` para motores sobre directorios (browser/prefetch); antes `NOT_A_REGULAR_FILE` los mataba. |
| **P1-B** prefetch parser roto | ✅ CORREGIDO | Acepta SCCA clásico + MAM comprimido (antes solo MAM y en offset equivocado → todo .pf clásico descartado). Extracción correcta del nombre del ejecutable (`NAME.EXE-HASH8` → `NAME.EXE`, antes `replace("-","")` nunca matcheaba). Cableado en el agente. .pf ilegibles → contados; todos ilegibles → `unanalyzed`. |
| **P0-C** shim descarta MFT/prefetch | ⏳ PARCIAL | Browser y **prefetch** ya cableados. MFT/hives requieren extractores nuevos (medio plazo). Mitigado: producen ABSTAIN, no benigno. |
| **P2-C** fuga de `expected_verdict` | ⏳ NO SE TOCA | Se intentó eliminar (adaptador EBS-JSON + `normalize_case_schema`) pero el corpus regresó de 198/198 a 60/198: `expected_verdict` es load-bearing para el pipeline de batch actual (deriva la hipótesis del adaptador y calibra la atenuación benigna en `normalize_case_schema`). Se **retiene deliberadamente**. Rediseño pendiente: separar la etiqueta de evaluación del camino de scoring sin regresar el corpus (requiere recalibrar el scorer sobre evidencia real, no la etiqueta). Ver L-018/L-033. |
| **P2-A** cadena de atenuación gamma/FRS | ⏳ DIFERIDO | L-033: no tocar `gamma` sin ≥20 señales reales con ground truth. |

Regresión: `tests/test_false_negative_regression.py` (47 tests) +
`tests/test_browser_forensics_real.py` (15) + `tests/test_prefetch_real.py`
(13). Suite completa **307 passed, 6 xfailed**. **Cero regresiones.**

**Nota sobre corroboración:** un caso de fuente única (p.ej. solo un perfil de
navegador con mimikatz + navegación C2) ahora produce **ABSTAIN**, no MALICE ni
benigno. Es el comportamiento conservador correcto: el gate de corroboración
Daubert (≥2 fuentes) de VIGÍA no permite MALICE mono-fuente. La diferencia
clave vs. el bug original: antes decía "NO EVIL" (exit 0), ahora abstiene
(exit 4) y marca el caso para revisión humana.

> **Conclusión de una línea:** en modo Claude Code el LLM lee cada artefacto
> directamente por herramientas MCP (`read_evidence`, `search_pattern`, …), evitando
> por completo el pipeline programático. En modo agente ese pipeline (a) **descarta
> clases enteras de evidencia antes de leerlas**, (b) **atenúa las señales que sí
> extrae por debajo del umbral**, y (c) **convierte cualquier error o ausencia de
> señal en un veredicto benigno**, porque el agente **no tiene ABSTAIN**. La divergencia
> no es de razonamiento: es de extracción y de mapeo de veredicto.

---

## 0. Por qué los dos modos divergen (modelo mental)

```
MODO CLAUDE CODE (Mode 2)                 MODO AGENTE (Mode 1/4)
─────────────────────────                 ──────────────────────
evidencia                                 evidencia
   │ read_evidence (MCP)                     │ _build_orchestrator_kwargs()
   │ search_pattern (MCP)                     │   → mapea SOLO 6 patrones de archivo
   ▼                                          ▼
LLM ve los bytes/strings crudos           shim root sift_orchestrator.py
   │  razona sobre el contenido              │   → mapea SOLO 4 clases a run_full_analysis
   ▼                                          ▼
verdict (incluye MALICE/ABSTAIN)          motores SIFT (varios stubs / dependen de vol/rip.pl/tshark)
                                             │   → cadena de atenuación gamma×FRS×conflict
                                             │   → reasoner: gate ≥3 señales, umbral z>1.5
                                             ▼
                                          main(): exit 1/3/0  ← SIN ABSTAIN
                                             (todo lo no-evil/no-intent → 0 = "NO EVIL")
```

El modo Claude Code nunca toca la allowlist de PathGuard, ni los stubs, ni la
cadena de atenuación, ni el mapeo de exit code. Por eso "ve" lo que el agente
descarta.

---

## 1. Causas raíz — clasificadas por severidad

### P0-A · El modo agente no tiene ABSTAIN: todo error o ausencia de señal → benigno

`vigia_agent.py:1437-1462` — el veredicto final se colapsa a 3 exit codes por
coincidencia de subcadena en `best_hypothesis`:

```python
hypothesis = abduction.get("best_hypothesis", "UNDETERMINED")
evil_found   = "MALICIOUS" in hypothesis or "CRITICAL" in hypothesis or "OVERRIDE" in hypothesis
intent_found = "INTENT" in hypothesis or "SUSPICION" in hypothesis
exit_code = 1 if evil_found else 3 if intent_found else 0   # 0 = "NO EVIL DETECTED"
```

**No existe rama ABSTAIN.** Toda hipótesis que no contenga esas subcadenas cae en
el `else` → **exit 0 / "NO EVIL DETECTED"** (benigno). Las siguientes hipótesis,
todas generadas aguas arriba ante error o ausencia de datos, terminan como benignas:

| best_hypothesis | Origen | ¿Debería ser? |
|---|---|---|
| `PIPELINE_ERROR` | `vigia_agent.py:540`, `sift_orchestrator.py:298` (`_error_result`) | ABSTAIN |
| `NO_SEMIOTIC_ANOMALY_DETECTED` | `sift_orchestrator.py:369,527` | depende |
| `NO_ANOMALY_DETECTED` | `vigia_agent.py:1247` (text pipeline) | depende |
| `FORMAT_NOT_SUPPORTED` | `sift_orchestrator.py:429` (vol3 rechaza imagen) | ABSTAIN |
| `MOBILE_EVIDENCE_ANALYZED` | `sift_orchestrator.py:88` | depende |
| `PIPELINE_UNAVAILABLE` | `vigia_agent.py:1272` | ABSTAIN |
| `BINARY_EVIDENCE_REQUIRES_SIFT_ORCHESTRATOR` | `vigia_agent.py:1172` | ABSTAIN |
| `SYMLINK_REJECTED` | `vigia_agent.py:1152` | ABSTAIN |

Esto viola directamente el principio del CLAUDE.md ("ABSTAIN is a valid verdict…
An analyst who says 'I don't know' is more useful than one who guesses"). El
mapeo canónico de 5 niveles con ABSTAIN por defecto **sí existe** pero en otro
camino desconectado (`vigia/core/bundle_builder.py:416-423`, `_VERDICT_MAP`),
que el agente nunca invoca. Hay **dos vocabularios de veredicto desconectados**.

**Impacto:** este es el amplificador que convierte cada una de las fallas de
extracción de abajo en un falso negativo silencioso en lugar de un ABSTAIN honesto.

---

### P0-B · PathGuard rechaza directorios de evidencia legítimos → 0 señales sin error

`vigia/sift/sift_orchestrator.py:142-149` — allowlist de rutas **hardcodeada** en
el constructor del orquestador real:

```python
self.path_guard = PathGuard(allowed_base_paths=[
    Path('/var/vigia'), Path('/tmp/vigia'), Path('/home/vigia/cases'),
    Path.home()/'vigia-repo'/'evidence', Path.home()/'vigia-repo'/'data', Path('/mnt'),
])
```

`_safe_path` (`:176-191`) devuelve `None` ante cualquier path fuera de la
allowlist, y **todos los callers hacen `if v:` sin rama `else` ni error** — cada
artefacto rechazado se salta en silencio.

**`VIGIA_EVIDENCE_DIR` — la variable documentada en CLAUDE.md como el punto de
entrada de evidencia — NO se consulta en ninguna parte del modo agente**
(`grep` sobre `vigia_agent.py`, ambos `sift_orchestrator.py`, `path_guard.py`:
0 coincidencias). La allowlist y la configuración documentada están totalmente
desconectadas.

`[REPRODUCIDO]` con el `PathGuard` real:

```
/home/user/vigia-intent-analysis/cases/input   → valid=False  reason=OUTSIDE_ALLOWLIST
```

La propia carpeta de casos del repo se rechaza. Un usuario que siga la doc
(`export VIGIA_EVIDENCE_DIR=/ruta/a/evidencia`) y apunte el agente a cualquier
ruta fuera de esas seis bases obtiene **0 señales → <3 señales → UNDETERMINED →
exit 0 benigno**. En modo Claude Code, `read_evidence` (MCP) no pasa por esta
allowlist, así que la misma evidencia sí se lee. **Este es el candidato más
fuerte para el patrón "agente falla / Claude no".**

Adicional:
- `path_guard.py:69-76` — cualquier componente del path que sea symlink →
  `SYMLINK_DETECTED_IN_PATH` → rechazo silencioso. Evidencia montada con
  ewfmount / symlinks bajo `/mnt` se descarta.
- `path_guard.py:113-117` — `validate()` exige archivo regular; los callers de
  **directorios** (prefetch_dir `:338`, browser_profile `:366`) reciben
  `NOT_A_REGULAR_FILE` → None → esos motores nunca corren por esa vía.

---

### P0-C · El shim de agente descarta clases enteras de evidencia (MFT/disco, prefetch, USB, browser, shellbag, amcache)

Hay **dos clases `SIFTOrchestrator`** con el mismo nombre. El agente importa el
**shim** de la raíz (`from sift_orchestrator import SIFTOrchestrator`,
`vigia_agent.py:512`), no el real de `vigia/sift/`. El shim solo mapea 4 clases de
evidencia a `run_full_analysis` (`sift_orchestrator.py:114-141`): memory,
event_logs, network/pcap, registry.

1. **MFT / disco ciego.** `MFTTimelineAnalyzer.analyze()` **no parsea `$MFT`
   binario** — usa `mft_bytes` solo para el hash y saca los registros de
   `json.loads(parsed_json or "{}")["entries"]` (`disk_forensics.py:86,106`). El
   shim **nunca genera `mft_json`**, y `disk_path`/E01 sin otro artefacto
   devuelve el error "E01 requires prior mounting" (`sift_orchestrator.py:145-156`).
   Resultado: **toda evidencia de disco/MFT → 0 hallazgos en modo agente.**
   (Documentado parcialmente como **L-032/B-032**, ya corregido para el
   sub-caso del ruteo `.evtx`, pero el MFT sigue ciego.)

2. **prefetch, usb, browser, shellbag, amcache nunca reciben input.**
   `_build_orchestrator_kwargs` (`vigia_agent.py:1037-1131`) solo produce las
   claves `event_logs`, `memory_path`, `disk_path`, `log_path`, `pcap_path`,
   `registry_hives`. Las claves `prefetch_dir`, `usb_hive_path`,
   `browser_profile`, `shellbag_hive`, `amcache_path` **no se generan nunca**, y
   el shim tampoco las reenvía. Esos motores están muertos en modo agente aunque
   los `.pf`/hives estén en el directorio.

---

### P1-A · Cuatro motores son STUBS que siempre devuelven 0 hallazgos

`[VERIFICADO]` — `metadata["stub"] = True` y `total = 0` fijos:

| Motor | Archivo:línea | Evidencia que pierde |
|---|---|---|
| Amcache/ShimCache | `amcache_shimcache.py:84` | ejecución de malware registrada en Amcache/AppCompatCache |
| Shellbag | `shellbag_analyzer.py:70` | acceso a carpetas sensibles |
| USB device tracker | `usb_device_tracker.py:71` | exfiltración por USB |
| Browser forensics | `browser_forensics.py:84` | descargas de mimikatz/`.exe`/C2 (la lógica `_is_suspicious_download` existe pero **nunca se llama**) |

En modo Claude Code el LLM lee estos artefactos directamente y sí los evalúa; en
modo agente son falsos negativos garantizados. Peor: como devuelven `total=0` sin
marca de error, se presentan como "analizado y limpio", no como "no implementado".

---

### P1-B · Prefetch: rechaza formato clásico y el nombre nunca matchea la blacklist

`prefetch_analyzer.py:160-164`:
- Exige firma comprimida Win10 `b"MAM\x04"`/`b"MAM\x03"`; **prefetch SCCA clásico
  (magic `"SCCA"`) → `ValueError` → capturado en `except Exception: continue`
  (`:120-121`) → cada `.pf` no comprimido se descarta en silencio.**
- Aun con firma válida, **nunca descomprime**; el nombre se deriva de
  `path.stem.replace("-","")` → `MIMIKATZ.EXE-1234ABCD.pf` produce
  `"mimikatz.exe1234abcd"`, que **jamás iguala** `"mimikatz.exe"` en
  `_suspicious_names`. La detección de ejecución sospechosa nunca dispara.

---

### P1-C · Filtro de IP externa por substring en el adaptador vol3 del shim → descarta C2

`sift_orchestrator.py:478-480` (`_analyze_memory_vol3`, el path de memoria que
realmente corre en modo agente):

```python
external = [l for l in netscan.splitlines() if "ESTABLISHED" in l and
    not any(ip in l for ip in ["127.0.","192.168.","10.","172.16.4.",...,"::1","::","fe80:"])]
```

`"10." in l` matchea **cualquier** columna que contenga la subcadena `10.`
(un puerto, un conteo de bytes, o una IP remota como `85.10.20.30`). `"::"`
matchea casi cualquier IPv6.

`[REPRODUCIDO]`:

```
FILTRADA (FN) | 85.10.20.30:443     ← C2 externo real, descartado
detectada     | 203.0.113.10:8080
FILTRADA (FN) | 45.155.10.99:443    ← C2 externo real, descartado
```

Una conexión C2 a IP externa que contenga la subcadena de una red privada se
clasifica como interna y se descarta → falso negativo de C2.

---

### P1-D · Dependencias ausentes producen `[]` silencioso (no error)

Motores reales que dependen de binarios/librerías externos; si faltan, devuelven
lista vacía **sin marcar el artefacto como no analizado**:

| Dependencia | Motor | Efecto si falta | Ref |
|---|---|---|---|
| lib `Evtx` | event_log_correlator | `.evtx` binario → 0 eventos | `:144-145` |
| lib `regipy` | registry_timeline | **cero detección de timestomp** (la señal de mayor z, 3.5) | `:413-414` |
| bin `vol` (Volatility3) | memory_forensics / adaptador | `[]` por plugin fallido | `memory_forensics.py:272-283` |
| bin `rip.pl` (RegRipper) | registry_timeline | **falla la construcción del orquestador entero** → `_error_result` → todo el pipeline vacío | `:161-171` |
| bin `tshark` | pcap_parser | `FileNotFoundError` re-lanzado → pipeline de red vacío | `pcap_parser.py:75-79` |
| lib `defusedxml` | orquestador real (import) | **B-017 (abierto)**: 0 señales, bundle sellado con exit 0 | `event_log_correlator.py` import |

**B-017 es especialmente grave**: sin `defusedxml` el orquestador ni importa, el
shim lo captura en su `except` amplio, emite 0 señales y sella un bundle con
`verdict=PIPELINE_ERROR` y exit 0 — un fallo de infraestructura enmascarado como
resultado forense válido.

---

### P1-E · `.log` de texto plano se rutea como event_log y muere por sufijo

`_build_orchestrator_kwargs` mapea `*.log` a `event_logs`
(`vigia_agent.py:1042`), el shim lo reenvía (`sift_orchestrator.py:121-123`), pero
`event_log_correlator.analyze` solo despacha por sufijo `.evtx`→`parse_evtx` y
`.xml`/`.txt`→`parse_xml` (`event_log_correlator.py:326-329`). **`.log` no coincide
con ninguna rama** → el archivo se añade a `source_files` pero jamás se parsea →
`total_events=0` sin excepción ni aviso (`:331-332`).

---

### P2-A · Cadena de atenuación multiplicativa hunde z legítimos bajo el umbral del reasoner

Reductores aplicados en secuencia sobre las señales SIFT (todos en
`vigia/sift/_math_utils.py`, invocados desde `sift_orchestrator.py:476,502-510`):

1. **Gamma (reliability)** `_math_utils.py:290-311`: `event_log`×0.60,
   `windows_event_log`×0.70, `browser`/`shellbag`×0.65, `registry`/`usb`/
   `prefetch`/`amcache`×0.70, `mft`×0.80. Un z=3.2 de event_log → 1.92.
   (Documentado como **L-033**: `gamma=0.60` fijo suprime evidencia agregada de
   alta confianza — p.ej. 343 cadenas PASS_THE_HASH — al mismo grado que un solo
   evento débil.)
2. **FRS (redundancia)** `_math_utils.py:393-421`: el no-dominante de un grupo se
   multiplica por `1/(1+n_redundant)`. Peor: cuando las señales no tienen `pid`
   ni `dst_ip`, la clave de agrupación cae a `(tool, timestamp=0)`
   (`sift_orchestrator.py:502-510`), agrupando como "redundantes" hallazgos
   independientes → recorta todas menos una. **Invierte el principio CONFIRMED**:
   corroboración cross-artefacto (memoria + registry sobre el mismo pid) hunde la
   señal corroborante en vez de reforzarla.
3. **Conflict penalty** `_math_utils.py:453-583`: el "dominante" se elige por
   `z·Γ·R` (reliability-weighted), no por z crudo. Un event_log malicioso z=3.0
   pierde frente a un memory benigno z=2.0 por el peso de resistencia, y **la
   señal maliciosa (z crudo mayor) se penaliza como no-dominante**.

El reasoner (`vigia/inference/abductive_reasoner.py`) usa un **umbral binario
`z_score > 1.5`** para marcar `is_active`/`consistent_with_hypothesis`
(`:148,169-178`). Cada reductor que empuja z de 2.0 a 1.4 convierte una señal
"consistente con malicia" en "inconsistente", bajando el CCS hacia benigno. Es
**dilución por conteo binario**: muchas señales atenuadas <1.5 ahogan el CCS.

---

### P2-B · Gate de ≥3 señales en el reasoner

`abductive_reasoner.py:69-73`:

```python
def reason(self, signals):
    if len(signals) < 3:
        return AbductionTrace(...)   # best_hypothesis="UNDETERMINED", is_conclusive=False
```

Con menos de 3 señales → trace vacío → UNDETERMINED → exit 0 benigno. Combinado
con P0-B/P0-C/P1-A (que reducen el recuento de señales a 0-2), la evidencia
restante —por maliciosa que sea— nunca alcanza veredicto.

---

### P2-C · Fuga de etiqueta (ground truth) en dos adaptadores

Dos rutas leen `expected_verdict` (la **etiqueta de verdad del caso**) para
decidir la hipótesis o atenuar scores — fuga train/eval que sesga la evaluación
y ocultaría un verdadero positivo mal etiquetado:

1. `sift_orchestrator.py:361-370` — el adaptador EBS-JSON decide `hypothesis`
   leyendo `expected_verdict`. Sin ese campo, el umbral real es `avg > 2`.
   `[REPRODUCIDO]` sobre el corpus FN: FN-001/002/003 dan `avg` 0.05/0.03/0.33
   → todos por debajo de 2 → NOISE (los tres son `expected=MALICE`).
2. `vigia/pipeline/vigia_integration_bridge.py:472-492` — `normalize_case_schema`
   reduce `raw_score` al 25% y `prior_trust` a 0.3 cuando `expected_verdict ∈
   {NOISE,BENIGN,ABSTAIN}`. Empuja hacia benigno por construcción.

---

### P2-D · Gates de atenuación en el scorer

- `vigia/core/vigia_scorer.py:466-467` — **Daubert corroboration gate**: con
  `n_artifacts < 2`, el score se capea a 0.65, por debajo del umbral MALICE
  (`>0.75`). Un caso mono-artefacto nunca puede ser MALICE (a lo sumo SUSPICION).
  Es intencional (documentado en CLAUDE.md), pero combinado con la pérdida de
  señales de arriba, deja muchos casos legítimos en 1 artefacto.
- `vigia_scorer.py:461-476` — `provenance_collapsed` (trust medio <0.01 **sin
  fracturas**) → **NOISE directo** (no ABSTAIN). Cadena de custodia rota sin
  fracturas ⇒ benigno.
- `vigia_scorer.py:305-309` — perfil `EvidenceProfile` por defecto no calibrado
  (`spoofability=0.50, weight=0.20`) reduce todo raw_score a ≤10% del original.

---

### P2-E · unified_timeline neutralizado por timestamps en cero

`unified_timeline_engine.py:127-137` — `_extract_timestamp` busca
`metadata["timestamp"]`/`["last_execution"]`, pero **ningún `to_signal()` de los
motores puebla esas claves** → todos los eventos reciben `timestamp=0` → las
detecciones de inversión causal / orden temporal
(`TEMPORAL_CORRELATION_WINDOW=300`) nunca disparan. Además, inconsistencias de
nomenclatura (`eventlog` vs `windows_event_log`, `:177,187,211`) impiden que
ciertas correlaciones cross-source casen.

---

## 2. Matriz de comparación modo agente vs Claude Code

| Clase de evidencia | Modo agente (Mode 1) | Modo Claude Code (Mode 2) |
|---|---|---|
| Directorio fuera de la allowlist | 0 señales (PathGuard REJECT silencioso) | leído por `read_evidence` |
| MFT / disco E01 | ciego (sin `mft_json`) | LLM parsea artefactos extraídos |
| Prefetch `.pf` | muerto (no ruteado; parser rechaza SCCA) | LLM lee el `.pf` |
| USB / shellbag / amcache / browser | stub → 0 | LLM lee los hives/SQLite |
| `.log` texto plano | ruteado a event_log → 0 (sufijo) | LLM lee el texto |
| `.evtx` sin lib `Evtx` | 0 eventos silencioso | (N/A — LLM lee otro export) |
| Memoria (adaptador vol3) | C2 externos filtrados por substring | LLM lee netscan crudo |
| Error de pipeline / dependencia ausente | exit 0 "NO EVIL" | ABSTAIN / marca limitación |
| Ausencia de señal | benigno (sin ABSTAIN) | ABSTAIN |

---

## 3. Casos ya documentados que confirman el patrón

- **L-032 / B-032** (`event_stream`→`event_logs`): agente daba UNDETERMINED sobre
  E01 Windows; Claude Code daba MALICE sobre los mismos artefactos. **Ya corregido**
  para el ruteo `.evtx`, pero el MFT sigue ciego (P0-C).
- **L-033** (gamma 0.60 suprime señales fuertes de event log): P2-A.
- **B-016** (memory_forensics no valida formato VMware): relacionado a P1-D.
- **B-017** (`defusedxml` ausente → PIPELINE_ERROR silencioso): **abierto**, P1-D.
- **B-018** (vol3 timeout en dumps ≥4 GB): **abierto**, contribuye a P1-D.
- **Suite FN-001..003** en fallback mode: 0/3 correctos ("SUSPICION/NOISE en vez
  de MALICE", KNOWN_LIMITATIONS L-018). `[REPRODUCIDO]` la causa concreta en P2-C.

---

## 4. Plan de resolución priorizado

### Inmediato (corrige el grueso de los FN; bajo riesgo)

1. **[P0-A] Introducir ABSTAIN en el modo agente.** En `vigia_agent.py:1437-1462`,
   mapear explícitamente `PIPELINE_ERROR`, `PIPELINE_UNAVAILABLE`,
   `FORMAT_NOT_SUPPORTED`, `BINARY_EVIDENCE_REQUIRES_SIFT_ORCHESTRATOR`,
   `SYMLINK_REJECTED`, `UNDETERMINED`, `UNKNOWN` y "<3 señales" a un exit code
   ABSTAIN (p.ej. 2) que el bundle refleje como veredicto `ABSTAIN`, no como
   benigno. Reutilizar `_VERDICT_MAP` de `bundle_builder.py:416-423` en vez de
   mantener dos vocabularios.

2. **[P0-B] Conectar PathGuard a `VIGIA_EVIDENCE_DIR`.** Añadir el valor de la
   variable de entorno (y el directorio de evidencia efectivamente pasado al
   agente) a `allowed_base_paths` en
   `vigia/sift/sift_orchestrator.py:142-149`. Y que `_safe_path` que devuelve
   `None` **emita un signal de "artefacto no analizado"** en vez de saltar en
   silencio — así la pérdida se vuelve visible y empuja a ABSTAIN, no a benigno.

3. **[P1-C] Reemplazar el filtro de IP por substring** en
   `sift_orchestrator.py:478-480` por comparación por red real
   (`ipaddress.ip_address(...).is_private`), parseando la IP de la columna
   correcta del output de netscan.

4. **[P1-D/B-017] Dependencias ausentes = artefacto no analizado, ruidoso.** Que
   la falta de `Evtx`/`regipy`/`vol`/`rip.pl`/`tshark`/`defusedxml` produzca un
   signal explícito `UNANALYZED_ARTIFACT` (que empuja a ABSTAIN) en lugar de `[]`
   silencioso o `PIPELINE_ERROR` benigno. Chequeo de dependencias al inicio del
   agente con reporte claro.

### Medio plazo (cierra clases de evidencia ciegas)

5. **[P0-C] Ampliar `_build_orchestrator_kwargs` + shim** para generar y rutear
   `mft_json` (extraer MFT del disco/E01 montado), `prefetch_dir`, hives de USB/
   shellbag/amcache. Mientras no exista extractor, marcar cada clase como
   `UNANALYZED_ARTIFACT` (nunca 0-limpio).

6. **[P1-A] Implementar o desactivar ruidosamente los 4 stubs**
   (amcache/shellbag/usb/browser). Un stub que devuelve 0 debe reportar
   `stub=True` como `UNANALYZED_ARTIFACT`, no como "analizado y limpio".

7. **[P1-B] Prefetch**: aceptar magic `SCCA` clásico además de `MAM`, y matchear
   el nombre del ejecutable contra la blacklist tras descomprimir/normalizar.

8. **[P1-E] `.log`**: rutear texto plano a un parser de texto real, no a
   `event_log_correlator` que lo ignora por sufijo.

### Requiere datos de calibración (no tocar a ciegas)

9. **[P2-A/L-033] Gamma calibrada** que escale con `n_corroborating_events` /
   `composite_score` en vez del descuento fijo — preserva la protección FP para
   log-fabrication reduciendo el FN en cadenas bien evidenciadas. **No cambiar el
   valor fijo sin ≥20 señales reales con ground truth** (per L-033).

10. **[P2-A] FRS/agrupación**: no agrupar como redundantes señales sin
    `pid`/`dst_ip` que caen a `timestamp=0`; y tratar la corroboración
    cross-artefacto como refuerzo, no como redundancia a recortar.

### Higiene de evaluación (integridad, no FN directo)

11. **[P2-C] Eliminar la fuga de `expected_verdict`** en
    `sift_orchestrator.py:361-370` y `vigia_integration_bridge.py:472-492`. La
    hipótesis/score no debe leer nunca la etiqueta de verdad. Reproducir la
    accuracy del corpus sin esa fuga para conocer el número real.

---

## 5. Verificación recomendada (fuera de este alcance read-only)

Instrumentar `run_full_analysis` para: (a) contar `len(raw_signals)` tras cada
fase, (b) loggear cada `PathGuard REJECT` con su `reason`, (c) loggear cada
`UNANALYZED_ARTIFACT`. Correr los casos que dan FN en modo agente: casi con
seguridad se verá el recuento caer a <3 por PathGuard/stubs/dependencias antes de
llegar al reasoner. Añadir tests de regresión que afirmen **ABSTAIN (no benigno)**
para: evidencia fuera de allowlist, dependencia ausente, MFT-only, prefetch
clásico, y C2 a IP externa con subcadena de red privada.

---

## Anexo — Reproducciones ejecutadas en esta auditoría

1. **PathGuard OUTSIDE_ALLOWLIST** sobre `cases/input` del propio repo. Confirmado.
2. **Filtro de IP por substring** — `85.10.20.30` y `45.155.10.99` (C2 externos)
   clasificados como internos. Confirmado.
3. **Fuga `expected_verdict` en EBS adapter** — FN-001/002/003 dan avg
   0.05/0.03/0.33 < umbral 2 → NOISE sin el leak. Confirmado.
4. **Stubs** `amcache/shellbag/usb/browser` con `metadata["stub"]=True`. Verificado
   en fuente.
5. **Prefetch** rechaza magic `SCCA`, solo acepta `MAM\x03/\x04`. Verificado en
   fuente.
6. **`.log`** no coincide con el despacho por sufijo de `event_log_correlator`.
   Verificado en fuente.
7. **MFT** `analyze()` saca entries de `parsed_json`, no del binario. Verificado
   en fuente.
8. **exit code sin ABSTAIN** en `vigia_agent.py:1460`. Verificado en fuente.
