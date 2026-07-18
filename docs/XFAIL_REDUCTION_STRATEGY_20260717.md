# Protocolo de reducción de xfails (XFail Reduction Protocol) — 2026-07-17

**Estado de este documento y del código asociado:**
- Rama: `claude/xfail-reduction-strategy-cawyv2` (rama de feature; **sin PR
  abierto todavía, sin review externo mergeado**). Base: `main` post-hackathon.
- Commits: Tanda 1 = `43384b3`, Tanda 1.5 (caracterización H-01) = `4649568`,
  Tanda 1.6 (governance: triggers, L-061, FIXME, este header) — ver `git log`
  de la rama. Cuando se abra el PR, anotar aquí su número y quién lo revisa.
- Nota de nomenclatura: "Tanda 1.5" ya se usó para la caracterización de la
  curva temporal; el endurecimiento de governance de esta pasada es **Tanda
  1.6** para no colisionar. Ambas viven en la misma rama.

> El objetivo NO es bajar un contador. Es que el suite no mienta: cada test
> que hoy no pasa debe tener una causa raíz clasificada y un criterio de
> cierre explícito. Bajar de 33 a 20 xfails marcando tests o relajando
> aserciones sería un retroceso, no un avance. El nombre del documento
> cambió por eso (era "Estrategia de reducción"): lo que sigue es un
> protocolo de ingeniería reutilizable, no una campaña contra un número.

Investigación sobre la corrida `pytest tests/` del 2026-07-17
(`1 failed, 1502 passed, 188 skipped, 33 xfailed, 1 xpassed`) y el batch
`run_all_agent.py` (187/201). Objetivo: que los tests que hoy no pasan vayan
desapareciendo **por tandas y con decisiones explícitas**, sin ocultar cambios
de doctrina ni forzar datos.

Todo lo afirmado abajo fue reproducido empíricamente en esta sesión (mismo
estado: 33 xfailed + 1 xpassed antes de los cambios de esta tanda).

Registro de la discusión que refinó este protocolo (auditoría externa Kimi +
contrapunto con datos del repo): `docs/REVIEWS/XFAIL_REDUCTION_REVIEW_20260717.md`.

---

## 0. El protocolo (reutilizable)

Seis pasos. Si dentro de seis meses aparecen otros 20 xfails, el procedimiento
sigue siendo válido — no depende de este corpus ni de esta corrida.

1. **Clasificar cada test por causa raíz** (clases A–D, §1). Nunca mezclar
   deuda técnica con deuda epistemológica.
2. **Reparar primero la infraestructura** (harness, CI, mecanismos de xfail).
   Un bug del harness contamina toda métrica aguas abajo.
3. **Convertir propiedades ya implementadas en guards permanentes** (retirar
   el xfail, no relajar la aserción).
4. **Implementar únicamente features autocontenidas** (sin consumidores de
   producción o con contrato de salida acotado).
5. **Posponer decisiones doctrinales hasta que exista una especificación
   explícita** — y cuando haga falta, generar el dato antes de decidir
   (test de caracterización), no decidir por intuición.
6. **Medir de nuevo y reclasificar antes de la siguiente tanda.** El estado
   cambia con cada tanda; la clasificación de ayer puede estar obsoleta.

### Mecanismo de protección — cableado, no solo escrito

La defensa contra "cerrar xfails bajo presión" no es una advertencia en prosa:
está **en el código**. `strict=True` en `test_canonical_cases.py` hace que
reparar datos (D-2) **rompa el suite** hasta que alguien retire la entrada de
`KNOWN_PENDING` caso por caso. No existe un camino mecánico de 33 → 0 sin
adjudicación explícita: el suite lo impide. Lo mismo aplica al guard H-05
(exige que el score cruce el umbral antes de testear el gate: una
recalibración que lo baje falla ruidosamente en vez de dejar de testear).

---

## 1. Diagnóstico — el FAIL, el XPASS y los 33 xfails no son un solo problema

Son **cuatro clases** distintas:

| Clase | Ítems | Naturaleza |
|---|---|---|
| A. Falso positivo del propio harness | 1 FAIL (`test_requirements_ci_contract`) + mecanismo xfail imperativo | Bug del test, no del motor |
| B. Propiedad ya implementada, test desactualizado | 1 XPASS (H-05) + 2 canonical que ya pasaban | Deuda de mantenimiento de markers |
| C. Feature/contrato pendiente, chico y autocontenido | H-04 (2), H-10 (1), H-01 (2) | Fix de código con decisión menor |
| D. Decisión de datos/doctrina pendiente | 23 × D-2 (B-115), 2 × D-G, 1 × BUG-NLP-002, 14 FAILs del batch | No se arregla tocando tests |

---

## 2. Tanda 1 — ejecutada en esta rama (clases A y B)

### 2.1 FAIL del contrato CI (`annotationlib`, `apport_python_hook`) — RESUELTO

No era una dependencia faltante y **no había que agregar nada a
requirements-ci.txt**. Causa raíz: el venv del entorno local vive dentro del
repo (`~/vigia-repo/.venv`), y el clasificador del scanner usaba
"origen dentro del repo ⇒ módulo local a recorrer". Con eso recorría
`site-packages` como si fuera código propio y escaneaba fuentes third-party,
donde el AST walker ve como incondicionales los imports condicionados por
versión/plataforma:

- `annotationlib`: stdlib de Python ≥ 3.14, importado bajo
  `if sys.version_info >= (3, 14):` (p.ej. typing_extensions) — irresoluble
  en 3.12.
- `apport_python_hook`: hook específico de Ubuntu, presente solo en algunos
  árboles de sistema.

Fix aplicado (cuarta ocurrencia de deriva documentada en el docstring del
test): `_is_repo_local()` excluye `site-packages`/`dist-packages` y cualquier
ancestro con `pyvenv.cfg`, tanto en la clasificación de specs como en el
fallback `rglob` de módulos bare. Regresión cubierta por
`test_is_repo_local_excludes_in_repo_virtualenvs` (venv sintético dentro de
un repo de prueba). Ninguno de los dos nombres aparece en el código del repo;
la clase entera de imports condicionales queda fuera del alcance del scanner.

### 2.2 El mecanismo de xfail canonical estaba roto — RESUELTO

`test_canonical_cases.py` usaba `pytest.xfail(reason)` **imperativo dentro del
cuerpo**: eso aborta el test antes de ejecutar el motor. Consecuencia: ningún
caso de `KNOWN_PENDING` podía jamás llegar a XPASS, contradiciendo el contrato
documentado ("when the underlying data is repaired the case flips to XPASS and
must be removed from this map"). El mapa acumulaba entradas muertas sin que
nadie lo viera.

Verificación empírica (los 52 casos ejecutados de verdad): de los 27
"pendientes", **2 ya pasaban hoy** —

- `case_111_falso_rastro_incompetencia` (MALICE esperado, CAIE da SUSPICION —
  aceptado por la regla del test),
- `case_024_paracaidista` (ídem; consistente con la resolución "honest
  SUSPICION" de la sesión de re-scoring 2026-07-12).

Fix aplicado: parametrización con `pytest.param(..., marks=pytest.mark.xfail(
reason, strict=True))`. Ahora los pendientes **se ejecutan** y `strict=True`
hace que el suite falle en cuanto un caso reparado empiece a pasar, forzando a
retirar su entrada (exactamente la disciplina que el comentario pedía). Las 2
entradas muertas fueron retiradas. Estado del archivo: 28 passed, 25 xfailed.

### 2.3 El XPASS de H-05 era GENUINO — test reescrito como guard

`test_malice_requires_independent_sources` no estaba pasando "de casualidad
por score bajo": el caso de 4 clones (mismo tool, mismo tipo) puntúa
**0.4638 > 0.33** (umbral MALICE) y es el **gate de corroboración B-068 /
R4-3 v2** el que capa el veredicto en SUSPICION ("volume within a single soft
collection domain does not corroborate MALICE"). Es decir: la propiedad que el
hallazgo H-05 exigía ya está implementada y funcionando.

Fix aplicado: se quitó el xfail y el test es ahora un guard directo con tres
aserciones: (1) el score cruza el umbral (si una recalibración lo baja, el
test avisa que hay que subir los raw_scores del fixture — cierra la trampa que
la nota del xfail describía), (2) el veredicto no es MALICE, (3) el `reason`
atribuye el cap al gate de corroboración.

**Balance Tanda 1: 1 FAIL → 0; 1 XPASS → 0; 33 xfails → 31; y los 25
canonical restantes ahora se ejecutan bajo strict.**

---

## 3. Tandas siguientes (clase C) — fixes chicos con decisión menor

### Tanda 2 — H-04: CCS debe ABSTAIN sin información (−2 xfails, riesgo ~nulo)

`vigia/core/causal_closure.py` sustituye cada dimensión `None` por `1/2`; con
las 4 en `None`, CCS = 1/2 ≥ threshold y habilita `MALICE_HIGH` con cero
información. Los dos xfails (`test_ccs_no_information_forces_abstain`,
`test_ccs_insufficient_coverage_abstains`) piden: cobertura mínima antes de
evaluar el gate.

Hallazgo clave de esta investigación: **`compute_causal_closure` no tiene
consumidores de producción** (solo el runner adversarial referencia nombres de
métricas). El cambio es autocontenido: contar dimensiones provistas
(`not None`) y, si `provided < 2` (o el criterio que se decida),
`verdict_cap = "ABSTAIN"` sin importar el score. `test_ccs_all_none_sits_exactly_on_threshold`
ya pinea la frontera actual y habrá que actualizarlo junto con el fix — está
diseñado para eso ("pins the boundary so the fix is visible").

Decisión requerida: umbral de cobertura (recomendado: ≥ 2 dimensiones reales;
con 0–1 dimensiones, ABSTAIN).

### Tanda 3 — H-10: `artifacts_rejected` en el veredicto (−1 xfail)

En la rama CAIE viva, un artefacto malformado se descarta con
`except Exception: continue` sin dejar rastro. El fix es de contrato de
salida: contar los descartes y exponer `artifacts_rejected` en el dict del
veredicto (y en la narrativa). No cambia ningún score; cambia la
reproducibilidad/completitud Daubert. Riesgo: bajo — agregar una clave nueva
al resultado; verificar que el sellado/canonicalización la incluya de forma
determinista.

### Tanda 4 — H-01: ventana de tolerancia temporal (−2 xfails, decisión doctrinal)

Dos paths: el hard gate del scorer (EFFECT_BEFORE_CAUSE ⇒ MALICE
incondicional, confidence 0.95) y la regla TCV de CAIE (severity 1.0 para
cualquier delta negativo). 2 segundos de drift NTP entre relojes distintos no
es una violación de las leyes de la física.

Lo que ya existe a favor: el control positivo **no-xfail**
`test_large_negative_delta_still_flags` (−3600s debe seguir detectándose)
protege contra sobre-corrección, y los tests pasan `delta_seconds` y
`clock_source` en los fixtures — el dato para decidir está disponible.

Decisión requerida (explícita, sellada en PolicySpec como piden los tests):
el tamaño de la ventana. Referencias razonables: 5–30 s cubre drift NTP
degradado; elegir, documentar en KNOWN_LIMITATIONS y aplicar en ambos paths
(escalar severity con |delta| en vez de binario 1.0 es la variante más
defendible: dentro de ventana → severity baja/no fracture; fuera → como hoy).

**Dato ya generado (Tanda 1.5, ejecutada):**
`tests/characterization/test_temporal_gate_curve.py` pinea la curva actual
(deltas −3600 s … +2 s × `clock_source` ∈ {host_ntp, ids_sensor}, ambos
paths). Resultados que fijan el diseño del fix, no la intuición:

- **`clock_source` es metadata muerta:** ningún path de producción la lee.
  La distinción "mismo reloj vs relojes distintos" que la ventana necesita
  hoy no existe como concepto operativo; hay que introducirla.
- **Path (a) — scorer hard gate — no lee los timestamps en absoluto.** Da
  MALICE para *todo* delta, incluido `0` y `+2` (evento después del proceso,
  sin violación real), porque confía verbatim en la lista
  `temporal_violations` pre-computada (L1120-1122). Corolario duro: la
  ventana de tolerancia **no puede vivir en el hard gate del scorer** — no
  tiene delta que testear. Debe vivir donde se *puebla* `temporal_violations`
  aguas arriba, o el gate debe empezar a validar el par contra los
  timestamps reales.
- **Path (b) — CAIE TCV — computa el signo bien pero la severity es binaria
  1.0** para cualquier delta negativo (L1790): −0.1 s y −3600 s son
  indistinguibles. Ahí sí vive el escalado por |delta|.
- **Control positivo confirmado plano:** `test_large_negative_delta_still_flags`
  (−3600 s) pasa hoy trivialmente porque la curva es binaria, no porque
  proteja contra sobre-corrección. Cuando la ventana escale la severity, ese
  control recién empieza a tener sentido.

El test es un **pin, no una aspiración**: cuando la ventana se implemente,
esas 35 celdas fallan a propósito y obligan a actualizarlas junto con el
cambio (misma disciplina que `strict=True`). La decisión de ventana ahora
espera con datos en la mano, no con intuición.

**Trigger de desbloqueo (para que la decisión no se pudra en el limbo).** La
decisión de ventana H-01 está BLOQUEADA hasta que se cumplan las dos
condiciones, en orden:

1. **Prerrequisito arquitectónico (path a):** resolver *dónde* vive la
   validación. La caracterización probó que el hard gate del scorer no puede
   alojar la ventana (no lee el delta). Hay que decidir entre: (a) el gate
   valida el par `EFFECT_BEFORE_CAUSE` contra los timestamps reales antes de
   disparar, o (b) `temporal_violations` se puebla solo vía un productor que
   valida (la ruta CAIE TCV es el productor validado que ya existe). Esta es
   la misma cuestión que L-061 — resolver L-061 ES resolver el prerrequisito.
2. **Valor de ventana + topología de reloj:** elegir el tamaño (5–30 s de
   referencia) y la regla mismo-reloj/relojes-distintos, sellarlos en
   PolicySpec. Requiere introducir `clock_source` como concepto operativo
   (hoy es metadata muerta).

Owner de la decisión: doctrina (Anna / quien sostenga la doctrina del scorer)
— NO es una decisión de código que un agente tome solo, porque fija umbrales
que van a un veredicto sellado presentable en corte. Condición mínima para
convocar la decisión: la curva de `test_temporal_gate_curve.py` revisada + una
referencia defendible de drift NTP forense (evita elegir 5–30 s por intuición;
si no hay literatura a mano, documentar el número como provisional y sujeto a
revisión, nunca como establecido). Hasta entonces, L-061 queda como limitación
documentada y el gate se comporta como hoy (conservador: sobre-detecta, no
sub-detecta — falla del lado seguro para un motor forense).

### Pendiente deliberado — BUG-NLP-002 (tokenizer): NO tocar en estas tandas

`test_analyze_surfaces_l33tspeak_as_oov` ya está en el estado correcto:
`strict=True`, documentado como D4 diferido, con su gemelo no-xfail que
caracteriza el hueco. Arreglarlo cambia la salida del tokenizer y exige
revalidar umbrales del corpus NLP — es un proyecto, no una tanda. Se queda
como xfail estricto hasta esa revalidación.

---

## 4. Clase D — los 25 canonical restantes y los 14 FAILs del batch

### 4.1 D-2 (B-115): 23 casos con `metadata.*_time` rotos

Los veredictos CAIE-layer de esos casos estaban sostenidos por TCV fósiles
sobre timestamps de metadata escritos ~90 días fuera de la línea temporal
coherente (docs/FOSSIL_HUNT_20260711_PASS2.md §3). No es un fix de motor: es
**reparación de datos** (re-anclar `metadata.*_time` en canonical_v2 + re-sello)
pendiente de la decisión D-2 (docs/CASE_RECOVERY_20260712.md §7.3,
docs/IMPL_20260712_M1_M3_M2.md). Cuando se ejecute, los casos que se
recuperen romperán el suite vía `strict=True` — ese es el mecanismo correcto:
cada recuperación obliga a retirar su entrada de `KNOWN_PENDING` en el mismo
commit que repara el dato.

Advertencia de esta investigación: no asumir que D-2 recupera los 23. Varios
esperan MALICE y hoy dan NOISE con composite ~0.09 contra umbrales Noisy-OR
0.5/0.2 — parte del residuo es D-G (escala), no timestamps. Ejecutar D-2 y
medir; lo que no flipee se re-clasifica honestamente como D-G.

### 4.2 D-G: divergencia de modos (case_090, case_026 + residuo de 4.1)

El dossier (docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-G) ya decidió la
dirección: unificar hacia el motor — `evaluate()` de CAIE deja de emitir
veredicto standalone y delega en la capa de decisión del motor (costo estimado
3–4 h). Cuando eso ocurra, `test_canonical_cases.py` debe dejar de comparar
contra el veredicto tool-layer y comparar contra el sellado — los 2 xfails
D-G (y el residuo D-2 que no flipee) se resuelven ahí. No intentar "calibrar"
los umbrales 0.5/0.2 para que alcancen: el dossier documenta que esa escala es
estructuralmente inalcanzable tras el ajuste — sería tuning cosmético.

### 4.3 Los 14 FAILs del batch (187/201) — adjudicación caso por caso

Denominadores distintos, no confundir: el batch es **201 casos** (14 FAILs);
el "~167/193" del dossier es una cifra de corpus in-sample con su propio
denominador y su propia advertencia (accuracy in-sample,
docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md §3). Abajo se adjudican los 14
FAILs concretos del batch, cada uno contra su procedencia documentada. Ninguno
es un xfail de pytest ni debe serlo: son ground-truth en disputa o modos
distintos del motor, no contratos de código.

| Caso | got/exp | Clase | Referencia |
|---|---|---|---|
| OWL-NEXUS5-CASE | NOISE/SUSPICION | Etiqueta (20 artefactos narrativos sin `artifact_id`) | BUGS_PENDIENTES §4152 |
| VIGIA-BREAK-011 | NOISE/SUSPICION | Doctrina — límite epistemológico | KNOWN_LIMITATIONS L-015 |
| VIGIA-BREAK-015 | SUSPICION/MALICE | Doctrina — tensión "evidencia abrumadora" | KNOWN_LIMITATIONS L-016; BUGS_PENDIENTES §4948 |
| VIGIA-BEN-014 | SUSPICION/NOISE | Doctrina — frontera NOISE vs ABSTAIN (design decision) | KNOWN_LIMITATIONS L-012 |
| VIGIA-FP-002 | NOISE/ABSTAIN | UNFIXABLE-NO-FORCE — ambigüedad de autorización | CASE_RECOVERY §5 |
| FP-CULTURAL-CLEAN | ABSTAIN/NOISE | UNFIXABLE-NO-FORCE — gemelo `n_signals<3` de NOISE correctos | CASE_RECOVERY §5 |
| VIGIA-FP-003 | SUSPICION/BENIGN | Deuda de calibración — floor effect (shared password, 0.176) | KNOWN_LIMITATIONS §2174 |
| NPS-2009-DOMEXUSERS | SUSPICION/NOISE | Deuda de calibración — floor B-028/B-065 (9 art., top z=0.18) | KNOWN_LIMITATIONS §2339 |
| VIGIA-BEN-012 | SUSPICION/NOISE | Deuda de calibración — floor (kworker, 0.125) | KNOWN_LIMITATIONS §2172 |
| VIGIA-FN-001 | NOISE/MALICE | Deuda de detector — exige contexto externo (RRHH) | BUGS_PENDIENTES §4940 |
| VIGIA-FN-002 | NOISE/MALICE | Deuda de detector — exige contexto externo | BUGS_PENDIENTES §4941 |
| VIGIA-FN-003 | SUSPICION/MALICE | Deuda de detector — exige análisis de memoria profundo (RWX) | BUGS_PENDIENTES §4955 |
| VIGIA_KIWI_006 | NOISE/SUSPICION | Deuda de detector — señal de concealment sin detector (score 0.0294) | BUGS_PENDIENTES §5452 |
| VIGIA_KIWI_007 | NOISE/SUSPICION | Deuda de detector — señal de concealment sin detector (score 0.0518) | BUGS_PENDIENTES §5453 |

Consolidado por acción:

- **Doctrina / etiqueta (anotación, no motor) — 6:** OWL-NEXUS5, BREAK-011,
  BREAK-015, BEN-014, FP-002, FP-CULTURAL-CLEAN. Acción: formalizar como
  entradas L-* donde falte; no tocar el motor. Los dos UNFIXABLE ya están en
  CASE_RECOVERY §5 (recuperarlos rompería 4 NOISE correctos).
- **Deuda de calibración (floor effect) — 3:** FP-003, NPS-2009, BEN-012.
  Acción: ticket de calibración del piso B-028/B-065; NO es xfail.
- **Deuda de detector — 5:** FN-001, FN-002, FN-003, KIWI-006, KIWI-007.
  Acción: ticket en BUGS_PENDIENTES. FN-001/002 exigen contexto externo,
  FN-003 análisis de memoria profundo. KIWI-006/007 reproducidos en modo
  motor aislado el 2026-07-17 (corrige la nota previa "testimony-path / sin
  adjudicar", que era errónea en dos frentes): NO son testimonio puro —
  KIWI-006 es `cultural_marker`+`log_entry`, KIWI-007 es
  `document_geometry`+`log_entry` — y puntúan **0.0294 / 0.0518**, muy por
  debajo del piso 0.10. Eso descarta floor calibration (el piso solo levanta
  hipótesis intent-class, no señal cero) y descarta la alucinación Ollama de
  BUGS_PENDIENTES §5452 como causa del NOISE en modo motor (es una observación
  de un modo distinto). Diagnóstico: la señal de concealment que el caso
  pretende portar no tiene detector que dispare en el motor. Única sub-pista
  que amerita código de detector nuevo.

Nota sobre estabilidad del batch (respuesta al riesgo de "race conditions en
el batch, no en el motor"): 199/201 casos leen bundles sellados
(`[CACHED:motor]`), así que la salida es cache-estable por construcción — la
inestabilidad entre corridas es casi imposible salvo `--rerun`. El diff entre
corridas **ya es factible sin trabajo nuevo de motor**:
`vigia/scripts/compare_runs.py` es un comparador determinista con etiquetado
IMPROVEMENT / REGRESSION / VERDICT_SHIFT y deltas en fracciones; lo único que
falta es cablear un snapshot de `_batch_summary.json` + un flag `--diff` que
delegue en él. Tarea chica, no proyecto.

---

## 5. Orden recomendado y balance proyectado

| Tanda | Contenido | Costo | xfails/fails que cierra | Decisión previa |
|---|---|---|---|---|
| 1 (esta rama) | Scanner CI, mecanismo xfail canonical, guard H-05 | hecho | FAIL 1→0, XPASS 1→0, 33→31 | ninguna |
| 1.5 (esta rama) | Caracterización curva temporal H-01 (pin, no juzga) | hecho | 0 (genera el dato para Tanda 4) | ninguna |
| 2 | CCS coverage → ABSTAIN (H-04) | ~1 h | 31→29 | umbral de cobertura |
| 3 | `artifacts_rejected` (H-10) | ~1–2 h | 29→28 | ninguna |
| 4 | Tolerancia temporal (H-01), ambos paths | ~2–3 h | 28→26 | ventana en PolicySpec (dato ya en Tanda 1.5) |
| 5 | D-2 data repair + retiro strict de recuperados | 2 h + re-sello | 26→~10±? (medir) | D-2 (datos) |
| 6 | D-G unificación de modos | 3–4 h código + ~igual validación | resto canonical | doctrina decidida; validación con harness corpus-wide (ya corrido 1 vez a mano en el dossier) |
| — | BUG-NLP-002 | proyecto D4 | 1 (queda último) | revalidación tokenizer |

Nota sobre la Tanda 6: "3–4 h" es estimación de código, no de validación.
Cuando `evaluate()` deje de emitir veredicto standalone y delegue en la capa
de decisión del motor, hay que correr el corpus completo contra ambas
versiones y **explicar y aceptar cada divergencia** — el dossier ya corrió esa
comparación una vez a mano (55/193 de acuerdo, 40 flips duros unidireccionales,
docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-G), ese es el harness de
migración. Duplicar la estimación: código + validación de divergencias.

Qué **no** hacer (confirmado por esta investigación): agregar `annotationlib`/
`apport_python_hook` a requirements-ci.txt (ocultaría el bug del scanner y no
instalaría nada útil); forzar los 33 de golpe (23 dependen de una decisión de
datos y 2 de una unificación de doctrina); convertir los FAILs del batch en
xfails de pytest (son disputas de etiqueta, no contratos).

---

## Backlog — Tanda 1.7 (DIFERIDA por decisión del revisor, 2026-07-17)

El revisor identificó que este documento entró en un loop de governance (cada
pasada de pulido genera nuevos pedidos) y decidió: la Tanda 1.6 es suficiente
para operar; abrir el PR y dejar que el review real decida si la 1.7 hace
falta. Estos 5 ítems quedan **guardados, no ejecutados** — para que no se
pierdan y para que el review pueda priorizarlos:

1. **Mecanismo de convocatoria de la decisión H-01.** El trigger define la
   *condición* de desbloqueo pero no el *canal/proceso* de convocatoria
   (¿thread del colectivo? ¿sesión de scoring? ¿issue?). Definirlo cuando el
   colectivo acuerde su proceso de decisión doctrinal.
2. **Reevaluación de severidad de L-061 (P2 → ¿P1?).** PREGUNTA ABIERTA DE
   SEGURIDAD, no resuelta aquí a propósito: la clasificación P2 asume que el
   JSON del caso es input confiable. Si un actor puede manipular el JSON antes
   del scorer (examinador malicioso, compromiso de cuenta), el hard gate
   dispara MALICE 0.95 sobre input controlado por el atacante — eso sería una
   superficie de integridad de evidencia (P1). Requiere modelar el trust
   boundary del input de construcción del caso. Decisión de seguridad, no de
   un agente solo.
3. **Referenciar los tickets de deuda de detector** (FN-001/002/003,
   KIWI-006/007) en `BUGS_PENDIENTES.md` con ID explícito; crearlos si no
   existen. Hoy la deuda está adjudicada (§4.3) pero sin ID de ticket.
4. **Changelog de commits en el header** (hash · tanda · descripción) para no
   depender de `git log`.
5. **Matriz de riesgo tandas × superficie** (motor / datos / doctrina / solo
   harness), para que la línea roja "qué toca el motor" sea legible de un
   vistazo. Adelanto: Tandas 1/1.5/1.6 = solo harness+docs; Tanda 2/3/4 =
   motor; Tanda 5 = datos; Tanda 6 = motor+doctrina.

Regla del protocolo aplicada aquí (§0, paso 6 + anti-parálisis): el pulido de
governance se detiene cuando el documento es operable por un tercero sin el
autor presente. Ese umbral se alcanzó en 1.6. Lo demás se decide con feedback
de review, no con otra pasada de auto-crítica.
