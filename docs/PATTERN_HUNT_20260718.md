# Cacería de patrones — clases S/T/U/V derivadas de los commits del 17-07 (2026-07-18)

**Método.** Los commits mergeados a `main` el 17-07 (dos P1 de omisión silenciosa
`ac48177`/`ad7e41f`, el benchmark mutante `d0c953c`, la attestation sub-cubierta
`31bba81`, los phantom imports L-061, y la Tanda 1 del XFail Reduction Protocol)
definen un meta-patrón común: **el sistema reporta más completitud de la que
tiene**. Esta cacería buscó instancias restantes de las cuatro clases, con
cuatro exploraciones paralelas independientes + verificación empírica propia de
cada hallazgo top (disciplina audit-before-patch: nada entra acá sin cita
file:line, y los marcados VERIFICADO fueron además reproducidos/leídos
directamente en esta sesión).

Etiquetas: **VERIFICADO** = reproducido o leído directamente en esta sesión;
**CONFIRMED** = trazado por exploración con cita de código; **INFERRED** =
plausible, consumo no trazado hasta el final.

Las clases:

| Clase | Patrón | Origen (commit del 17-07) |
|---|---|---|
| **S** | Descarte/coerción silenciosa en path de veredicto | `ac48177`, `ad7e41f` |
| **T** | Input con autoridad de veredicto confiado verbatim | L-062 |
| **U** | Tests que no testean | `d0c953c`, Tanda 1 |
| **V** | Auto-verificación con alcance menor al declarado | `31bba81`, L-061 |

---

## Clase S — descartes silenciosos en el path de veredicto

### S-1 [VERIFICADO consumo MCP; CONFIRMED mecanismo] — `trust_fusion.py` reproduce LOS DOS triggers de los P1 del 17-07, sin ninguno de los disclosures

`vigia/core/trust_fusion.py` es un segundo motor temporal que repite exactamente
los dos vectores ya parchados en CAIE/bridge, sin parche:

- **`:416-420`** — timestamp presente-pero-imparseable → coercionado a
  `datetime.now(timezone.utc)` (¡peor que descartar: fabrica proximidad
  temporal falsa con el reloj de la corrida!). Es el trigger de `ac48177`.
- **`:425-428`** — metadata no-dict → `frozenset()` vacío silencioso. Es el
  trigger de `ad7e41f`.
- **`:446-472`** — artefacto que falla la construcción → `except Exception` +
  log, sin contador; `artifact_count` reporta solo sobrevivientes. Es la forma
  H-10.

Sin equivalente de `temporal_pairs_skipped`/`normalization_failures` en el
resultado. **Resolución del caveat de consumo (verificado en esta sesión):**
`trust_fusion_analysis` está registrada como herramienta MCP viva
(`vigia/vigia_sift_bridge.py:3221-3222`, gate `VIGIA_TRUST_FUSION_ENABLED`,
default habilitado) — sus salidas `composite_trust` y **`daubert_admissible`**
llegan al investigador en Modo 2. No toca el bundle sellado de Modo 1, pero un
"admisible bajo Daubert" computado sobre timestamps coercionados a `now()` y
artefactos descartados sin contador es la misma clase de falso "analizado y
limpio", un anillo afuera del núcleo.

### S-2 [VERIFICADO] — H-10 sigue vivo en el wiring del scorer, y el fix es un espejo de patrón ya existente

`vigia_scorer.py:656-663`: `except Exception → logging.warning → continue` al
construir artefactos CAIE en el **path de scoring vivo**; ningún
`artifacts_rejected` llega a `base_result`, y `caie_fractures_source` queda
`"live_caie"` — el resultado lee como totalmente analizado. Dato nuevo que
abarata la Tanda 3: **el path público `caie.evaluate()` YA tiene el patrón de
disclosure** (`caie.py:2861-2913`: contador `rejected`, claves
`artifacts_rejected`/`rejected_count` en el resultado). El fix de H-10 no
inventa contrato: replica el existente en el wiring del scorer.

### S-3 [CONFIRMED] — regla MFT: coerción `int()` sin guard (`caie.py:1955-1968`)

(a) `mft_entry_number` ausente → `0`; dos artefactos sin el campo colapsan a
entry 0 y `MFT_ENTRY_ANOMALY` (sev 0.90) **no puede disparar jamás** — supresión
silenciosa de fractura. (b) valor presente-pero-imparseable (`"abc"`) →
`ValueError` sin guard local → tumba `detect_fractures` entero → el scorer cae a
`json_fallback` (disclosure parcial: el flag de source cambia, pero el modo
entero degrada por un campo — la clase que `ac48177` resolvió con skip
por-par + registro).

### S-4 [VERIFICADO] — crash de formato sobre severity en `compare_baseline.py:68,72`

`f"{v.get('severity'):.2f}"` sin default: severity `None` → `TypeError`;
severity string (clase B-057, input real documentado: `"alto"`, `"nan"`) →
`ValueError`. Reproducido en esta sesión. Display-only (CLI de comparación),
severidad baja — misma clase que el `composite_score:.4f` del runner canonical
arreglado el 17-07.

### S-menor [INFERRED] — `trust_fusion.py:296-297`: type/severity malformados → default 0.5 silencioso (dirección mixta/harsher, prioridad baja).

**Limpios (falsabilidad):** el parser TCV y ambos consumidores
(`_parse_ts_tcv` + red/proceso + MFT temporal) disclosean vía
`temporal_pairs_skipped`; `evaluate()` público disclosea rechazos; los dos
sitios del normalizador legacy registran `normalization_failures`; los
orquestadores SIFT emiten marcadores `unanalyzed` (remediación previa
explícita); `bundle_builder` re-empaqueta post-veredicto sin ablandar;
`abductive_reasoner_v2` registra `broken`/`missing` estructurados.

---

## Clase T — inputs con autoridad de veredicto confiados verbatim

**Hallazgo estructural (VERIFICADO):** el núcleo lee exactamente **dos canales
con autoridad de veredicto sin productor validante en runtime**:
`temporal_violations` (entero, en todos los modos) y `caie_fractures` (solo en
fallback). Todo lo demás está clampeado, whitelisteado, recomputado o sin
influencia (inventario completo abajo).

### T-1 [VERIFICADO] — `caie_fractures` en modo fallback/standalone: el hermano mayor de L-062

`vigia_scorer.py:682-685`: si el import de CAIE falla, `fractures =
case.get("caie_fractures", [])` — fracturas del JSON del examinador fluyen
directo a `fracture_malice_boost` (`:1088-1097`, hasta +0.5) y a la rama
SUSPICION de cadena rota (`:1206`). En modo live CAIE recomputa y descarta el
JSON (correcto). Pero el modo standalone es **soportado y documentado** (header
del archivo): ahí, entradas de fractura fabricadas portan autoridad de
veredicto. Mitigante: `caie_fractures_source="json_fallback"` sí queda sellado
(disclosure de modo), pero el disclosure no quita la autoridad.

### T-2 [VERIFICADO] — `STATISTICAL_UNIFORMITY`: boost de malicia con productor fantasma, **en todos los modos**

`vigia_scorer.py:1103-1110`: cada violación `STATISTICAL_UNIFORMITY` suma
`sev×0.35` al `fracture_malice_boost` (cap 0.5), incondicionalmente — a
diferencia de T-1, **no** está gateado por disponibilidad de CAIE. El comentario
en `:1099` dice "from the temporal engine (not CAIE) — valid signal". Verificado
en esta sesión: **ese motor no existe**. Ningún módulo runtime lo emite; los
únicos escritores son scripts de conversión de corpus
(`scripts/convert_break_cases.py:79,98`, `convert_synthetic_cases.py:116`) que
lo autorean dentro de los JSONs. Es L-062 con productor fantasma documentado en
el propio código. Misma familia: todo `temporal_violations` alimenta además
`_compute_temporal_factor` (`:308-345`) bajando `effective_trust` por artefacto,
verbatim.

### T-3 [VERIFICADO] — `provenance_chain`: solo se consulta `len()`, jamás se verifica un hash

`vigia_scorer.py:721-728`: cadena ausente/`BROKEN` → `epc_factor=1/10`; si no,
factor por `len(chain)`. CAIE ídem (`caie.py:790-795`, `len<2` decae). Ninguna
ruta recomputa o compara los hashes contra contenido. Un examinador puede
suministrar N strings arbitrarios para maximizar la confianza de custodia (o
vaciarla). Autoridad de veredicto, cero validación criptográfica. Nota: el
bridge además **fabrica** un placeholder si falta (`bridge:447-448`).

### T-4 [CONFIRMED] — `semantic_role="exculpatory"`: supresión declarada por el examinador, guard parcial

Declarado-por-diseño (documentado en `:539-543`), puede apartar toda la
evidencia device → NOISE forzado (`:621-635`). Mitigante real: el filtro Eco
fail-closed (`:561-616`) retiene refutaciones "demasiado perfectas". Riesgo en
dirección opuesta a L-062 (suprimir en vez de fabricar). Ya parcialmente
cubierto por doctrina FASE 2; queda anotado como superficie, no como bug.

**Inventario de cierre (campos SAFE, verificados por la exploración):**
`expected_verdict` (echo, label-blind confirmado), `peirce_chain` (echo),
`raw_score`/`prior_trust`/`base_trust` (clamp + Finite Math Shield),
`evidence_type` (whitelist CAIE; unknown degrada a peor clase, B-067),
timestamps de evento (parseados + range-guard R3-1 por el productor CAIE),
`metadata.reliability` (no consumido por el núcleo), gates de intake/
normalización/temporal-skip (unidireccionales: solo NOISE→ABSTAIN, jamás
ablandan). `grice_*` es verbatim con autoridad (NOISE→SUSPICION) pero **tiene
productor real** (`audit_grice_maxims` vía `sift_orchestrator.py:1124-1140`) —
no es clase T.

---

## Clase U — tests que no testean

### U-1 [VERIFICADO] — `tests/integration/test_ebs_v1_integration.py`: 55 checks, todos tragados bajo pytest

El decorador casero (`:32-45`) ejecuta cada check **en el import** y captura
`except Exception` (incluye `AssertionError`) en una lista `FAILED` que solo se
consulta bajo `if __name__ == "__main__"` (`:1353`). Reproducido en esta
sesión: bajo pytest **colecta 0 items** — los 55 checks corren como efecto
secundario de la colección, cualquier fallo se imprime y se descarta, y la
corrida queda verde. El propio `tests/integration/conftest.py` documenta el
patrón sin marcar el riesgo. Como script manual (`python3 tests/integration/...`,
el modo en que se corrió el 17-07 con "55/55") el gate SÍ funciona. Es decir:
el archivo es un runner honesto disfrazado de test module — la mentira aparece
solo cuando pytest lo colecta (cosa que `run_all_tests.sh` hace: ver V-2).
Fix mínimo preservando el modo manual: una función real
`def test_ebs_v1_suite_all_passed(): assert not FAILED` al final del archivo.

### U-2 [VERIFICADO] — `tests/caie/test_batch_cases.py`, `test_batch_cases_v2.py`, `test_real_cases.py`: batch runners a nivel de módulo (clase `test_m4_floor`)

Cero funciones de test, cero asserts, **sin guard `__main__`**: un loop
`subprocess.run(["python3", "scripts/run_vigia_full.py", ...])` corre en la
colección de pytest (`test_batch_cases.py:21-68`). No mutan source (a
diferencia de m4_floor) pero spawnnean subprocesos en colección y dependen de
globs relativos al cwd. Son exactamente la clase que `d0c953c` destrackeó.

### U-3 [VERIFICADO] — `tests/test_2_vs_1_pipeline.py`: asserts a nivel de módulo + contradicción interna

Cero funciones de test; el pipeline entero corre en el import con los dos
únicos asserts a nivel de módulo (`:110-112`) — un fallo sería error de
colección, no de test. Además `sys.path.insert(0, '/mnt/agents/output')`
hardcodeado (`:16`) y la contradicción: el comentario dice "dominante debería
ser REGISTRY" y el assert exige `MEMORY_FORENSICS` — razonamiento fósil.

### U-4 [VERIFICADO] — `tests/test_red_team.py`: dos tests print-only y un gate 6× más débil que su banner

`test_rt_008_contrastive_detected` (`:257`) y `test_direct_destruction_detected`
(`:269`): sin assert — solo `print`. El primero lo admite en comentario
("documenta el comportamiento actual"); el segundo dice "debe detectarse" y no
asserta detección: pasa incondicionalmente. Y `test_full_suite_metrics`
(`:196-241`): el banner imprime "min required: 0.60" pero el assert real es
`recall >= 0.10` — control con confianza falsa (misma clase que el FIXME del
control temporal del 17-07).

### U-5 [VERIFICADO] — `test_b1c_memory_mixed_routing.py:159`: `json.dumps(result, default=str)` — un check de serializabilidad estructuralmente infalible

`default=str` da fallback a CUALQUIER objeto no serializable: el test no puede
fallar. Quitar `default=str` lo convierte en test real.

### U-6 [CONFIRMED, por diseño con erosión] — `test_semantic_lint_fractures.py`: 187 de los ~188 skips del suite

201 casos parametrizados, 187 skip, 14 corren. El skip es doctrinalmente
correcto (el lint solo aplica a casos con ground truth de atribución genuina)
pero el gate es una lista de substrings EN/ES hardcodeada
(`GENUINE_TRUTH_MARKERS`, `:43-47`): un caso genuine-attribution redactado
distinto se salta silenciosamente — cobertura que se erosiona con el corpus.
Los directorios `benign/` y `legacy/` aportan 0 corridas. No es bug; es
superficie de erosión a vigilar (¿marker estructurado en el schema del caso en
vez de substring de texto libre?).

### U-7 [CONFIRMED] — inertes agrupados: 8 archivos `test_*.py` con toda la lógica bajo `__main__`

`tests/caie/test_caie_break.py`, `test_caie_direct_raw.py`,
`test_caie_directo.py`, `test_caie_tcv_fixed.py`, `test_caie_temporal.py`,
`test_caie_temporal_fixed.py`, `test_pipeline_real.py`,
`tests/test_adversarial_suite.py` — colectados, 0 tests, sin efectos
secundarios (guardados). Peso muerto que infla el conteo aparente; candidatos a
renombrar (`scripts/` o sin prefijo `test_`).

**Limpios (falsabilidad):** cero escrituras al árbol del repo desde tests (la
clase m4_floor no tiene más instancias); cero `pytest.xfail` imperativos
restantes (el fix de Tanda 1 se sostiene); los 15 `pytest.skip` imperativos
restantes son guards de disponibilidad al inicio (legítimos), salvo los 4 de
`test_bypass_vectors.py` que merecen confirmación de que el CI realmente los
ejecuta (una suite de seguridad que se salta en verde es indistinguible de una
que pasa); suites adversarial/aggregator/dominance con asserts reales
(falsos positivos descartados explícitamente).

---

## Clase V — auto-verificación con alcance menor al declarado

### V-1 [VERIFICADO] — la "frontera residual" de la attestation subdeclara: 2 de los 3 módulos de decisión de raíz quedan sin atestar y sin disclosure

El fix `31bba81` documenta UNA frontera residual (`vigia_scorer.py` fuera del
árbol `vigia/`). Pero `pyproject.toml` declara TRES módulos de raíz como "the
sealed verdict pipeline" (`--cov=vigia_scorer --cov=vigia_agent
--cov=sift_orchestrator`, con el comentario "measuring only vigia/ hid the
primary core"). La attestation (`bundle_builder.py:397`, walk desde
`_ROOT=<repo>/vigia`) excluye los tres, pero solo uno está documentado:
**`sift_orchestrator.py` (82KB, CasePatternLibrary + mapeo de veredicto) y
`vigia_agent.py` (101KB, path de veredicto del agente) cambian sin mover
`engine_attestation_hash`**, sin mención. También fuera: `caie_legacy_root.py`
(91KB, CAIE legacy). Misma clase que el propio `31bba81` cerró, un directorio
más ancha.

### V-2 [VERIFICADO] — el "full suite" silenciosamente no corre `vigia/tests/`, y el wrapper diverge del comando documentado en ambas direcciones

- `run_all_tests.sh:8` → `pytest tests/` (sin `vigia/tests/`, sin
  `--ignore=tests/integration`).
- `pyproject.toml:88` → `testpaths = ["tests"]` (un `pytest` pelado tampoco
  colecta `vigia/tests/`).
- `vigia/tests/` contiene 2 módulos de test reales
  (`test_b047_correlation_groups.py`, `test_lr_calibrator_serialization.py`)
  que solo corren si alguien tipea el comando completo de CLAUDE.md.
- Intersección con U-1: el wrapper SÍ colecta `tests/integration/`, donde el
  archivo de 99 checks tragados corre en colección y reporta 0 — el wrapper
  ejecuta lo excluido y excluye lo incluido, ambas cosas en silencio.

### V-3 [VERIFICADO] — `decision_hash`: campo de integridad sellado que ningún verificador re-deriva

Sellado en cada bundle (`bundle_builder.py:219`, `IntegrityBlock`), pero:
`quick_verify` chequea solo `graph_hash`+`bundle_hash`;
`forensics/verify_ebs_v1.py` tiene `_check_graph_hash`/`_check_policy_hash`/
`_check_bundle_hash` y **ningún `_check_decision_hash`** (verificado contra la
lista de checks). Garbage de 64 hex en `integrity.decision_hash` pasa todos los
verificadores. Mitigante fuerte: el CONTENIDO (`decision_trace`) sí está dentro
de `bundle_hash` — no es un agujero de contenido, es un **campo decorativo
presentado como verificado**. O se re-deriva en R1, o se documenta como
no-verificado.

### V-4 [CONFIRMED código; INFERRED explotabilidad] — `engine_attestation_hash` se verifica solo por FORMA y gatea "Level 3 — Fully compliant"

`verify_ebs_v1.py:380-386`: `_check_engine_attestation` valida presencia + 64
hex minúsculas, jamás re-deriva. Un hash plausible-pero-bogus pasa R4 y alcanza
Level 3. Defensa razonable: un verificador stdlib-only no puede recomputar el
hash del motor sin el source pinneado — pero entonces la garantía debe
declararse como "formato verificado, origen no verificable independientemente",
no implicarse como compliance total.

### V-5 [CONFIRMED divergencia] — tres copias divergentes del verificador "independiente"

`forensics/verify_ebs_v1.py`, `tests/forensics/verify_ebs_v1.py`,
`tests/integration/verify_ebs.py` — copias con offsets ya distintos (el check
de attestation en `:381` vs `:373`). Si los tests ejercitan la copia y
producción shippea el original, un test verde no prueba nada del verificador
shippeado — la clase dead-duplicate que `31bba81` acaba de remover en pipeline.

**Limpios (falsabilidad):** `hash_chain.verify_chain` (todos los campos
no-estructurales en el preimage, tail-anchor y HMAC verificados);
`verify_tool_log.py` v2 (completo, con caveats v1 honestamente declarados);
`bundle_hash` (cubre todo el contenido; tampering de `decision_trace` detectado
— verificado por test existente); el walk de attestation DENTRO de `vigia/`
(unreadable → perturba el hash, matchea su test).

---

## Priorización global y mapeo a acciones

| # | Hallazgo | Clase | Estado | Acción propuesta | Decide |
|---|---|---|---|---|---|
| 1 | trust_fusion: 2 triggers P1 + drop sin contador (S-1) | S | VERIFICADO/CONFIRMED | Portar los 3 disclosures ya diseñados (`ac48177`/`ad7e41f`/H-10) al segundo motor; es espejo de patrón, no diseño nuevo | código (tanda) |
| 2 | Attestation: `sift_orchestrator`/`vigia_agent`/`caie_legacy_root` sin atestar ni declarar (V-1) | V | VERIFICADO | Ampliar walk o ampliar la declaración de frontera residual; corto plazo: documentar los 3 (no solo 1) | código + doc |
| 3 | `run_all_tests.sh`/`testpaths` pierden `vigia/tests/`; wrapper diverge del doc (V-2) | V | VERIFICADO | `testpaths = ["tests","vigia/tests"]` + alinear wrapper con el comando de CLAUDE.md | código (chico) |
| 4 | 99 checks tragados en integration (U-1) + wrapper los colecta (V-2) | U | VERIFICADO | Gate pytest real (`assert not FAILED`) preservando modo manual; MEDIDO en esta sesión: hoy los 55 pasan en modo manual (55/55) — el tragado es LATENTE, no oculta fallos activos; el fix evita la degradación futura | código (tanda) |
| 5 | `STATISTICAL_UNIFORMITY` boost con productor fantasma (T-2) | T | VERIFICADO | Candidato L-* hermano de L-062 (mismo canal, distinto type); corregir el comentario fantasma ya | Anna (L-*) |
| 6 | `caie_fractures` fallback con autoridad (T-1) | T | VERIFICADO | Candidato L-*; decisión: ¿fallback degrada autoridad de fracturas JSON (cap SUSPICION?) o solo disclosure? | Anna (doctrina) |
| 7 | `provenance_chain` len-only (T-3) | T | VERIFICADO | Candidato L-* (documentar que custodia = longitud declarada, no hash verificado) o verificación real | Anna (doctrina) |
| 8 | H-10 espejo de `evaluate()` (S-2) | S | VERIFICADO | Ya planeado (Tanda 3 del protocolo); este hallazgo lo abarata: copiar patrón existente | código (tanda 3) |
| 9 | Batch runners en colección (U-2) + módulo-level asserts (U-3) + inertes (U-7) | U | VERIFICADO | Mover a `scripts/` o guard `__main__`; U-3 además resolver la contradicción comentario/assert | código (chico) |
| 10 | red_team print-only + gate 0.10 vs banner 0.60 (U-4) | U | VERIFICADO | Decidir el umbral honesto y assertarlo, o marcar xfail documentado; alinear banner | Anna (umbral) |
| 11 | `decision_hash` decorativo (V-3) + attestation shape-only L3 (V-4) | V | VERIFICADO | Re-derivar en verificador o degradar el claim (doc + label del Level) | código + doc |
| 12 | 3 copias del verificador (V-5) | V | CONFIRMED | Deduplicar o test de identidad byte-a-byte entre copias | código (chico) |
| 13 | MFT `int()` (S-3), `default=str` (U-5), severity format crash (S-4), skip-gate substring (U-6), bypass_vectors skips en CI (U-7-bis) | varios | mixto | Menores; lote de higiene | código (lote) |

**Regla del protocolo aplicada:** nada de esto se fixea en esta pasada — la
cacería es inventario adjudicado, no ejecución. Los ítems "código (chico/tanda)"
son clase A/C del protocolo (ejecutables sin doctrina); los "Anna" fijan
autoridad de veredicto o umbrales y siguen el mismo trigger-model que H-01.
Ningún número L-* fue asignado acá (para no colisionar con la numeración de
main, como pasó con L-061: la asigna quien mergea).

**Nota de estabilidad:** suites mergeadas verificadas verdes en esta rama antes
de la cacería (67 passed, 28 xfailed en los archivos tocados por el merge del
17-07); identidad de la rama = `origin/main` reiniciada post-merge.


---

## Estado de ejecución (actualizado 2026-07-18, segunda pasada)

Prioridad elegida por Anna: **primero el cluster del verificador "independiente"**
(V-3 / V-4 / V-5). Ejecutado en esta rama:

- **V-3 CERRADO** — `_check_decision_hash` agregado a `forensics/verify_ebs_v1.py`,
  cableado como `R1_DECISION_HASH` (severidad ERROR, bloquea Level 2), con
  backward-compat dual-canon v2/v1. Verificado: los 3 bundles históricos
  EBS-shaped de `results/` conservan su nivel exacto (SRL-DMZ-FTP L2, NINA L3,
  VANKO-CORRECTED L3) y su `decision_hash` re-deriva; el tamper de 64-hex que
  antes era invisible ahora falla. Header R1 actualizado (los CUATRO hashes).
- **V-4 CERRADO (como honestidad, no como re-derivación)** — R4 documenta en
  header, docstring y MENSAJE DE ÉXITO que verifica presencia+formato
  solamente y que el origen no se re-deriva en modo standalone (eso vive en
  `test_attestation_coverage_integrity.py`). El mensaje es load-bearing: un
  test asserta las palabras para que el overclaim no pueda volver en silencio.
  La frontera queda pineada como HECHO: una attestation fabricada de 64 hex
  pasa R4 por diseño (test explícito de la frontera).
- **V-5 CERRADO** — las 3 copias borradas (`tests/forensics/verify_ebs_v1.py`
  ya había perdido el dual-canon R3-2: habría rechazado bundles históricos;
  `tests/integration/verify_ebs.py` era la versión pre-v1 baneada por
  `pre_release_check`; `verify_ebs_v1_parcheado.py`, variante vieja).
  Arqueología previa: ningún consumidor fuera del lockstep de `_canonicalize`.
  Lockstep actualizado + tripwire `TestRetiredCopiesStayDeleted` (si una copia
  reaparece sin re-registrarse, el suite rompe).
- **Guards nuevos en pytest real**: `tests/test_verify_ebs_v1_contract.py`
  (21 checks colectados de verdad — deliberadamente FUERA del archivo de
  integración tragado U-1).
- **Bonus (clase A, entorno)**: `test_unreadable_source_perturbs_hash...`
  fallaba como root (chmod 000 no bloquea a root — preexistente de main,
  invisible hasta hoy porque la base de ayer era anterior a 31bba81). Migrado
  de chmod a inyección de `PermissionError` vía monkeypatch: determinista en
  todo entorno.

### Segunda tanda del cluster V (2026-07-18, continuación)

- **V-2 CERRADO** — `testpaths = ["tests", "vigia/tests"]` + `addopts`
  `--ignore=tests/integration` (matchea el comando autoritativo de CLAUDE.md);
  `run_all_tests.sh` alineado y su `Exit code: $?` (reportaba `tee`, no pytest)
  → `${PIPESTATUS[0]}`. El default ahora colecta los ~40 de `vigia/tests/` que
  antes solo alcanzaba el comando completo. `tests/e2e` NO se silencia (depende
  de mcp / L-045; silenciarlo sería el mismo scope-drop). Verificado: scope
  autoritativo = 1538 passed.

- **V-1 CERRADO (ampliando el walk, no solo declarando)** — la attestation
  ahora pliega los TRES módulos de decisión de la raíz
  (`vigia_scorer.py`, `vigia_agent.py`, `sift_orchestrator.py` = el `--cov` de
  pyproject), solo en modo default, con degradación honesta
  (ausente → `MISSING_ROOT_MODULE`, ilegible → `UNREADABLE_ROOT_MODULE`, nunca
  desaparición silenciosa). `caie_legacy_root.py` excluido a propósito: código
  muerto (ningún runtime lo importa). Docstring de `compute_engine_attestation`
  y la "frontera residual" de `pipeline.py` actualizados (nombraban solo
  vigia_scorer.py, ocultando los otros dos). Tres guards nuevos en
  `test_attestation_coverage_integrity.py`: tocar un root module perturba el
  hash, un root module ausente lo perturba, y `source_dirs` explícito NO hereda
  los root modules (contrato preservado). Bundles históricos intactos (su hash
  está sellado; ampliar el productor no los toca — verificado NINA L3,
  SRL-DMZ-FTP L2). Determinismo preservado.

### Clase S — primera tanda (2026-07-18)

- **S-1 CERRADO** — `trust_fusion.py` ya no reproduce los triggers sin
  disclosure. `create_artifact_from_caie_result` acepta un sink opcional
  `disclosures` (backward-compat: `None` = comportamiento previo, único llamador
  interno) y registra las dos coerciones decision-relevantes: timestamp
  presente-pero-imparseable coercionado a `now()` (distingue ausente, que cae en
  `_utcnow()` por diseño y NO es pérdida) y metadata presente-pero-no-dict
  vaciada (distingue ausente). `trust_fusion_analysis` acumula los descartes de
  artefactos (rama `except`, antes solo log) en `rejected_details` con contador,
  y superficie en el resultado: `artifacts_submitted`, `artifacts_rejected`,
  `rejected_details`, `normalization_disclosures`, y el flag `input_degraded`
  que un consumidor puede gatear junto a `daubert_admissible`. La rama de error
  temprana ("No valid artifacts") también deja de ser ciega. Guard nuevo:
  `tests/test_trust_fusion_disclosure.py` (unit del sink + e2e async por los
  tres vectores, incluido "clean input → not degraded" y "composite sobre input
  degradado nunca sin el flag"). El motor no toca el bundle sellado de Modo 1;
  el fix es honestidad del anillo MCP (Modo 2), no cambio de la matemática de
  trust (eso sería doctrina, fuera de scope).

### Clase S — segunda tanda (2026-07-18)

- **S-2 / H-10 CERRADO (cierra un xfail del protocolo original)** — el
  `except: continue` del wiring del scorer (vigia_scorer.py) descartaba
  artefactos sin contador; además ignoraba el `return False` de add_artifact
  (rechazo por whitelist/límite, B-067). Ahora ambos mecanismos se registran y
  el resultado superficie `artifacts_rejected` + `rejected_details`. Decisión
  clave verificada con datos: NO se agrega gate ABSTAIN — un intento inicial de
  espejar el gate temporal regresionó test_ebs_adapter_label_malice_but_low_score
  (rechazar un tipo desconocido es NOISE legítimo por B-067/L-018, no
  indeterminación). Disclosure only. Convierte el xfail
  test_rejected_artifact_is_surfaced_in_verdict (H-10) en guard real — su vector
  original (raw_score="not_a_number") estaba obsoleto (CAIE lo acepta hoy);
  reescrito con evidence_type fuera de whitelist (rechazo determinista). Cierra
  la Tanda 3 del XFail Reduction Protocol. Total xfail 31→30.


- **S-3 CERRADO** — regla MFT_ENTRY_ANOMALY (caie.py). `int(mft_entry_number,
  0)` tenía dos fallos silenciosos: missing→entry 0 (dos colapsan a 0, la
  fractura sev-0.90 no puede disparar) y unparseable ("abc")→ValueError sin
  guard que tumbaba detect_fractures entero al json_fallback. Fix: parseo
  seguro que EXCLUYE el artefacto y registra el skip en `temporal_pairs_skipped`
  (ya surfaced al resultado + leído por el gate ABSTAIN del scorer), nunca
  fabrica entry 0. Verificado: no crashea, la anomalía real sigue disparando
  limpia (sin falsos skips), missing/unparseable se disclosean. Guard:
  tests/test_caie_mft_entry_guard.py.
- **S-4 CERRADO** — crash de formato severity en compare_baseline.py (`:68,72`).
  `f"{sev:.2f}"` moría con None (TypeError) y string ("alto"/B-057, ValueError).
  Helper `_fmt_sev` (float con fallback que superficie el valor malformado en
  vez de crashear). Display-only (CLI comparador); verificado en aislamiento
  — el módulo no es importable standalone por un acoplamiento de import
  preexistente (`run_vigia_case` vive en tests/), separado de S-4.
- **S-menor** (`trust_fusion.py:296-297`, default 0.5 en dirección mixta):
  queda como el único S abierto, prioridad baja (no reads-cleaner).

### Clase U — primera tanda (2026-07-18)

- **U-2 CERRADO (impacto de performance real)** — los tres batch runners
  (`test_batch_cases.py`, `test_batch_cases_v2.py`, `test_real_cases.py`)
  corrían un loop `subprocess.run` A NIVEL DE MÓDULO en la colección de pytest:
  **~60s de subprocess en cada corrida de la suite** (colección de tests/caie/
  bajó de 64s a 0.08s; suite completa de ~86s a ~25s). Cero funciones de test,
  cero referencias externas, redundantes con run_all_agent.py. Renombrados
  (sin `test_` → no colectados; conservador, reversibles, no borrados como el
  m4_floor de d0c953c porque no mutan source). Igual `test_2_vs_1_pipeline.py`
  (U-3: 0 tests, asserts a nivel módulo, `sys.path` /mnt hardcodeado) →
  `manual_2_vs_1_pipeline_probe.py`.
- **U-5 CERRADO — y reveló que default=str NO era una mentira.**
  `test_merge_is_json_serializable` no asertaba nada (`json.dumps(result,
  default=str)` sin assert). Al investigar: `default=str` ES el contrato de
  serialización real del sistema — el orquestador trabaja en Fraction
  internamente (invariante 4) y TODA serialización de producción usa default=str
  (pipeline.py:1477, bridge:1248/1282). Quitarlo (mi hipótesis inicial)
  sobre-ajustaba a un contrato nativo que el sistema deliberadamente no usa. Fix
  correcto: mantener default=str (producción) + aserción real de round-trip a
  dict no vacío. El "hallazgo" se corrigió a sí mismo con el dato.
- **U-1 CERRADO (belt-and-suspenders)** — el archivo de integración traga sus
  55 checks bajo pytest (decorador que captura AssertionError a lista solo leída
  bajo `__main__`). Estado real: CI lo corre STANDALONE
  (`python3 tests/integration/...`, gate correcto, vigia-forensic-ci.yml) y V-2
  lo --ignore-a de la suite pytest (sin polución). Agregado un gate pytest real
  (`test_ebs_v1_integration_all_checks_passed`: `assert not FAILED`) para que SI
  alguna vez se colecta, un fallo tragado salga rojo. Verificado: gate pasa bajo
  pytest, standalone sigue 55/55.

Pendientes: **U-4** (red_team: 2 tests print-only sin assert + gate real
recall>=0.10 vs banner "min required 0.60" — el umbral es decisión de Anna),
**U-6/U-7** (skip-gate de substrings, inertes agrupados — higiene menor). Y la
**clase T** entera (T-1/T-2/T-3: candidatos L-* hermanos de L-062 — autoridad
de veredicto, decisión de doctrina de Anna, no de un agente). Todo según "y
luego todo lo que dijiste".
