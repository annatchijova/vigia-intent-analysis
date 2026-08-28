# VIGÍA — Precisión y Dataset de Evidencia

> Este documento contiene la metodología de precisión completa, las métricas
> segmentadas del corpus y el desglose por dominios. El `README_ES.md` de nivel
> superior enlaza aquí y solo lleva un resumen breve.

---

## Precisión y Dataset de Evidencia

> **Disponibilidad del Dataset**
>
> Las imágenes forenses originales utilizadas durante la evaluación (volcados de memoria,
> imágenes E01, colecciones PCAP y artefactos relacionados) **no están incluidas en este
> repositorio**. El corpus completo ocupa muchos GB y contiene datasets forenses de
> terceros que no pueden redistribuirse.
>
> Este repositorio incluye la implementación completa del agente, el motor de puntuación
> determinístico, los bundles forenses generados, los outputs JSON producidos por el agente,
> los informes finales y el flujo de reproducción completo.
>
> Todos los reportes JSON en `/results` fueron producidos por VIGÍA durante ejecuciones
> reales de extremo a extremo — no son ejemplos elaborados manualmente. Esto aplica en
> particular a los casos con nombre (NROMANOFF, TDUNGAN, NFURY, ROCBA, SRL-ADMIN, SRL-AV,
> SRL-DC-MEMORY, SRL-DMZ-FTP, VANKO), que son distintos de los casos de referencia
> numerados REAL-001 al REAL-010.

## Precisión

**Precisión — Metodología y Resultados**

VIGÍA opera en tres modos distintos. El modo principal evaluado es el agente sin backend de modelo de lenguaje.

**Agente VIGÍA sin LLM (modo principal):** El agente autónomo resuelve todos los casos de forma completamente autónoma, sin ningún modelo de lenguaje. Este es el modo principal evaluado. El agente produce ForensicBundles completos con cadena de custodia, narrativa Peirciana, z-scores y aritmética determinista con Fraction. En los casos adversariales BREAK, el agente produce un veredicto definitivo — SUSPICION o el nivel apropiado — no una abstención. Los resultados están documentados en `KNOWN_LIMITATIONS.md`.

**Solo scorer Python (sin agente):** El pipeline de puntuación determinista se ejecuta en aislamiento, sin la capa de razonamiento del agente. Sobre el corpus canónico de 52 casos estructuralmente diversos — que abarca amenaza interna, forense de memoria, fabricación de logs, falsas banderas, fraude multi-fuente y esteganografía adversarial — el scorer logra el 100% de veredictos correctos. El conjunto completo de casos está disponible en `data/cases/vigia_cases_canonical_v2.json` para revisión independiente. En casos BREAK, el scorer devuelve UNKNOWN — comportamiento esperado en este modo sin la capa de razonamiento del agente.

**Agente + LLM (Claude vía MCP u Ollama offline):** Con un backend de modelo de lenguaje, Claude u Ollama opera exclusivamente sobre la capa narrativa de ForensicBundles ya sellados. No puede modificar veredictos ni puntuaciones. Este modo proporciona una ventaja adicional — narrativa Peirciana enriquecida y desambiguación de casos estructuralmente ambiguos — pero no es el modo principal evaluado.

Estos números no están inflados. Reflejan resultados en un corpus específico, diverso y documentado. Todos los modos están documentados en `KNOWN_LIMITATIONS.md`.

**Cobertura de idiomas:** Los casos fueron desarrollados y validados en español e inglés. El rendimiento en otros idiomas no ha sido validado formalmente y no puede garantizarse en este momento.

---

## ⚠ NOTA DE PRECISIÓN — TRES DOMINIOS DE EVALUACIÓN

> **CAMBIO DE MÉTRICA (2026-07-05, B-075 — decisión de doctrina post-envío).**
> La auditoría red-team `AUDITORIA_MOTOR_SIN_LABEL.md` demostró que el camino batch
> del corpus JSON (`run_all_agent.py`) reproducía la etiqueta `expected_verdict` de
> cada caso en vez de derivar el veredicto de la evidencia (fuga de etiqueta, P2-C):
> con la etiqueta removida, ese camino detectaba **cero** casos maliciosos. Desde el
> fix B-075 el adaptador EBS deriva su veredicto del scorer determinista canónico con
> la etiqueta removida (`VIGIA_EBS_RESOLVE=motor`, ahora el default), y la métrica del
> corpus mide **detección real ciega a la etiqueta**:
>
> ## ⚠ CÓMO LEER LOS NÚMEROS DE VIGÍA — un modo, una lectura (2026-07-06)
>
> **El 97.5% de abajo es SOLO el camino JSON del agente. No dice nada de cómo
> le va a VIGÍA sobre evidencia raw real — eso se mide por caso, en los otros
> dos modos.** La presentación honesta es una línea por modo:
>
> | Modo | Qué procesa | El número honesto |
> |---|---|---|
> | **Claude/MCP (Dominio A)** — principal | evidencia raw real, cadena de extracción MCP completa | **Análisis profundo por caso — sin número agregado por diseño.** Registro a la fecha: 100% de veredictos correctos en todas las investigaciones corridas (docs por caso en `evidence/`, `results/`, `reports/`) |
> | **Agente sobre JSON (Dominio B)** | casos JSON sintéticos/convertidos | **97.5% (158/162) en el corpus de detección** — el ÚNICO modo con número de corpus; agregado del corpus mixto 187/199 (segmentación abajo) |
> | **Agente sobre RAW (Dominio C)** | corpus forense público real | **43 fuentes de evidencia raw distintas con bundles sellados en `results/`** — SRL 2018 (22 imágenes de memoria), MUS2019/Narcos (13 dumps), M57 (3), NPS 2010/2014, Magnet 2020 CTF, Tuck 2019 macOS, Vanko — más las investigaciones Magnet 2022 (Windows/iOS/Android), Owl HD1/Nexus 5 y HMG documentadas por caso. **Cada una es una investigación individual con sus propios findings — NO se agrega como precisión** |
>
> El modo Claude Code / MCP (Modo 2) se evalúa aparte y por caso: **100% de
> veredictos correctos en todas las investigaciones sobre evidencia raw
> corridas en ese modo** — incluyendo casos donde el modo agente abstiene o
> no llega (NPS-2010/2014: el Modo 2 determinó NOISE mientras el Modo 1
> quedaba en PIPELINE_ERROR; MAGNET-2022-WINDOWS: el Modo 2 llegó a MALICE
> con evidencia de C2 donde el Modo 1 decía NOISE). Ver Dominio A abajo.
>
> **Modo agente — `run_all_agent.py` sobre el corpus JSON de 199 casos —
> agregado: 187/199 (94.0%), ciego a la etiqueta, distribución idéntica a la del
> scorer standalone corriendo ciego.** Ese agregado NO es una cifra de precisión
> por sí solo: el corpus mezcla deliberadamente conjuntos de evaluación con
> propósitos distintos — incluyendo suites adversariales *diseñadas para romper el
> sistema* y casos de frontera epistémica — y deben leerse por separado
> (segmentación desde el dataset de ground truth, 2026-07-06):
>
> | Segmento | Casos | Ciego a etiqueta | Lectura |
> |---|---|---|---|
> | **Corpus de detección** (canónico 61, benigno 18, FLARE-ON CTF 10, real/convertido 51, demo 4, otros 18) | **162** | **158/162 (97.5%)** | **la métrica de precisión de este camino** — canónico 61/61, benigno 18/18, FLARE-ON 10/10; los 4 fallos son severidad adyacente o sobre-alerta doctrinal (L-054) en casos reales/convertidos y benignos |
> | Suites adversariales (BREAK 16, KIWI 7, suite FN 3, suite FP 5) | 31 | 18/31 | Material del Dominio C, *diseñado para romper*: sus fallos SON los límites documentados (L-014 constelaciones emergentes, L-016 consenso de confianza, FP de cultural_marker) — datos de resistencia, no precisión |
> | Frontera epistémica / intake ABSTAIN | 5 | 2/5 | revisión de etiquetas pendiente (FASE2 §5): el motor limpia casos cuyas etiquetas los declaran indecidibles |
> | Caso agregado pipeline-error | 1 | 1/1 | agregado legacy con forma de lista, expected UNKNOWN |
>
> **Corte alternativo — por `validation_class` (transparencia de contaminación, 2026-07-14):**
> El agregado 187/199 mezcla casos con riesgo de contaminación muy distinto. Leerlo
> como un único número sobreestima la confianza. Desglosado por origen del corpus:
>
> | validation_class | Casos | PASS | FAIL | Precisión | Postura de contaminación |
> |---|---|---|---|---|---|
> | **held_out** (KIWI-\*) | **7** | **5** | **2** | **71.4% (Modo 1) · 100% (Modos 2 y 3)** | Privado — nunca publicado, imposible de memorizar. La evidencia más sólida de generalización del corpus. |
> | **synthetic** (BREAK-\*, BEN-\*, FP-\*, FN-\*, CAN-\*, case_\*, DEMO-\*, AMB-\*) | **107** | **97** | **10** | **90.7%** | Construido por VIGÍA — riesgo de contaminación cero por construcción. Los fallos son límites documentados, no sorpresas. |
> | **public_documented** (REAL-\*, Flareon, NGDC, MAGNET, LINUX, NPS-\*, Nitroba, M57, SRL, OWL, …) | **85** | **83** | **2** | **97.6%** | De CFReDS, NPS, M57-Patents, Magnet CTF, Digital Corpora y similares. **contamination_caveat:** el narrador LLM puede conocer los análisis públicos de estos casos; leer como piso de rigor, no como prueba de generalización. El scorer determinístico no usa el LLM, así que este caveat aplica solo a la capa narrativa del Modo 2, no al veredicto sellado. |
> | **Total** | **199** | **187** | **12** | **94.0%** | Agregado del corpus mixto — significativo solo si se leen las tres filas de arriba al mismo tiempo. |
>
> **Por qué la diferencia entre 71.4% (Modo 1) y 100% (Modos 2 y 3) en los casos held_out:**
> Los dos números miden cosas distintas y ambos son honestos — ninguno es "más real" que el otro.
>
> El **Modo 1 (agente autónomo Python)** corre sin intervención humana: el motor determinístico
> decide solo, con señales matemáticas, sin razonamiento contextual. Es la prueba más dura
> y la más honesta sobre las capacidades reales del motor. Cuando falla en KIWI-006 y KIWI-007,
> eso revela el límite real del sistema determinístico en casos de testimonio de señal baja:
> la evidencia existe pero no supera el umbral de scoring sin contexto adicional.
>
> Los **Modos 2 y 3 (Claude Code + MCP y Ollama)** incorporan razonamiento semántico con
> un investigador humano en el loop. Ese pipeline completo — herramientas MCP + motor
> determinístico + narrador LLM + juicio del analista — refleja cómo se usa VIGÍA en la
> práctica real: un investigador que guía la herramienta, no un sistema desatendido.
> El 100% en casos held_out bajo estos modos prueba que el pipeline completo detecta
> correctamente incluso señales débiles, cuando el razonamiento contextual está disponible.
>
> **Conclusión:** reportar solo el 93.0% sería deshonesto (esconde la fortaleza de los
> Modos 2/3); reportar solo el 100% sería igualmente deshonesto (esconde el límite real
> del motor autónomo). Los dos números deben aparecer juntos, con su explicación.
>
> Trayectoria del agregado honesto, cada paso con gate: el flip B-075 quedó en
> 143/199; B-076 calibró el umbral SUSPICION contra el dataset de ground truth de
> 198 casos (`data/calibration_ladder_dataset_20260705.json`): +10, cero
> regresiones (153/199); las decisiones de doctrina del 2026-07-05 sumaron +14 (el
> comparador acepta MALICE-donde-INTENT como sobre-severidad — el ladder del motor
> no tiene escalón INTENT — nunca al revés; etiquetas sintéticas de AMB-001/002
> revisadas ABSTAIN→NOISE según el diseño documentado L-012, corpus real intacto).
> Metodología completa, prueba de invariancia al label-flip y análisis por
> cluster: [`docs/FASE1_RESOLVE_EBS.md`](./docs/FASE1_RESOLVE_EBS.md) y
> [`docs/FASE2_DATASET_CALIBRACION.md`](./docs/FASE2_DATASET_CALIBRACION.md).
>
> Las tasas pre-B-075 de este camino (p.ej. "129/129", "165/167") medían
> reproducción de etiqueta, no detección, y se conservan abajo solo como registro
> histórico.

> **La cantidad de casos puede estar desactualizada.** Estamos agregando casos
> activamente, especialmente investigaciones sobre evidencia raw (E01/evtx). Las
> cifras mostradas reflejan el corpus al momento de la última actualización y pueden
> subestimar la cobertura actual.

**VIGÍA opera en tres modos distintos, y sus números NO son comparables entre sí —
cada modo llega a la evidencia de manera diferente:**

**Dominio A — Claude Code / MCP (evidencia forense raw):** Pipeline completo, modo de
investigación principal. **Todo artefacto pasa por la cadena de extracción MCP**
(hash → lectura → entropía → búsqueda de patrones → inferencia de intención), así que
todo tipo de evidencia alcanza los motores de análisis — nada queda fuera de
cobertura en este modo. Probado en imágenes E01 reales, volcados de memoria y
archivos de logs. **Registro a la fecha: 100% — todas las investigaciones corridas
en este modo llegaron al veredicto correcto**, documentadas por caso en `evidence/`
y `results/` (este modo se evalúa por investigación, no con un número único de
corpus).

**Dominio B — Agente autónomo, casos pre-procesados en JSON:** Runner batch sobre
bundles EBS estructurados — es el ÚNICO modo con número de corpus, la métrica
segmentada de la nota de arriba (**corpus de detección: 158/162, 97.5%**; agregado
187/199). Desde B-075 el veredicto sale del scorer determinista ciego a la etiqueta;
la cifra anterior 165/167 medía reproducción de etiqueta (ver la nota de cambio de
métrica).

**Dominio C — Agente autónomo, evidencia raw (E01/evtx/memoria):** El agente parsea
artefactos raw directamente (MFT, prefetch, browser, event logs, pcap, memoria vía
vol3). **Acá viven los casos reales de corpus público: 43 fuentes de evidencia raw
distintas llevan bundles sellados en `results/`** (SRL 2018, MUS2019/Narcos, M57,
NPS, Magnet 2020 CTF, Tuck 2019 macOS, Vanko), cada una una investigación individual
con veredictos y findings por caso — este modo no tiene número de corpus porque son
investigaciones, no filas de benchmark. La cobertura es parcial por diseño: algunas
clases de artefacto todavía no alcanzan los motores (los hives de registro
USB/shellbag/amcache son stubs honestos que abstienen; ver `KNOWN_LIMITATIONS.md`),
y un caso cuya señal vive en una clase no cubierta degrada a ABSTAIN en vez de
producir un NOISE falso (patrón F7/P1-E). B-032 (routing de `event_logs`) y B-036
(threshold `z>5.0` imposible) están resueltos; ver [L-036](./KNOWN_LIMITATIONS.md)
para el override de hipótesis basado en señales.

> Los porcentajes de corpus de arriba aplican **solo al Dominio B**. Los resultados
> del Dominio A están documentados por caso en `evidence/` y `results/`; los límites
> de cobertura del Dominio C están documentados en `KNOWN_LIMITATIONS.md`.

---

VIGÍA separa la evaluación en tres dominios distintos. Solo el Dominio A
constituye la métrica de precisión del sistema.

### Dominio A — Precisión Determinística: 129/129 — HISTÓRICO (pre-B-075)

> **Superado el 2026-07-05 (B-075):** esta tabla se produjo por el camino batch JSON
> cuando el adaptador EBS todavía eco-reproducía `expected_verdict` (fuga P2-C), así
> que mide reproducción de etiqueta, no detección. Se conserva como registro
> histórico de la evaluación de envío. La métrica honesta vigente para este
> camino es el **187/199 de detección ciega** en la nota de cambio de métrica de
> arriba.

| Suite | Casos | Correctos |
|-------|-------|-----------|
| Corpus forense real (NIST/DFRWS/DEF CON/SRL 2018/LINUX/NGDC) | 39 | 39 ✓ |
| Corpus canónico (CAN-001–052) | 52 | 52 ✓ |
| Casos canónicos legacy | 10 | 10 ✓ |
| Máquinas benignas / limpias | 15 | 15 ✓ |
| Suite de falsos positivos | 3 | 3 ✓ |
| Suite de falsos negativos | 3 | 3 ✓ |
| Falsa atribución (planted attribution) | 3 | 3 ✓ |
| Corpus de demostración | 4 | 4 ✓ |
| **Total Dominio A** | **129** | **129 (100%)** |

> **Corrección 2026-06-17:** El total del Dominio A fue corregido de 117 a 118 para
> coincidir con el conteo empírico de casos producido por find_cases() en run_all_agent.py.
> Dos entradas fantasma identificadas durante la auditoría: VIGIA-REAL-SRL-RD02-MEMORY.json
> (contado pero nunca creado, la secuencia salta de RD01 a RD03) y un cuarto caso de
> falsa atribución (contado pero nunca creado — solo existen 3: FF-GENUINE-001,
> FP-CULTURAL-CLEAN-001, FP-CULTURAL-CLEAN).

Reproducir (post-B-075/B-076 + doctrina esto da el 187/199 honesto, no la tabla
histórica de arriba): `python3 run_all_agent.py --timeout 90`
Para reproducir explícitamente el comportamiento histórico de eco de etiqueta:
`VIGIA_EBS_RESOLVE=legacy python3 run_all_agent.py --timeout 90`

---

### Dominio B — Conjunto de Frontera Epistémica (no es precisión)

Estos casos no tienen una respuesta correcta única. Evalúan la capacidad
del sistema de reconocer ambigüedad irreducible y emitir ABSTAIN en lugar
de forzar un veredicto.

| Caso | Esperado | Resultado | Notas |
|------|----------|-----------|-------|
| VIGIA-AMB-001 | NOISE (revisado 2026-07-05; era ABSTAIN) | NOISE | L-012: señal insuficiente para la compuerta ABSTAIN |
| VIGIA-AMB-002 | NOISE (revisado 2026-07-05; era ABSTAIN) | NOISE | L-012: ídem |

**Nota de diseño:** ABSTAIN requiere conflicto estructural entre hipótesis
competidoras con evidencia no trivial. Los casos de señal nula retornan
correctamente NOISE. Ver [KNOWN_LIMITATIONS.md L-012](./KNOWN_LIMITATIONS.md).
**Revisión de etiquetas (2026-07-05, Fase 2):** las etiquetas sintéticas de
AMB-001/002 se actualizaron ABSTAIN→NOISE para coincidir con esta doctrina
documentada — las etiquetas originales contradecían la nota de diseño de
arriba (los archivos de caso llevan un campo de auditoría `_label_revision`).
Las etiquetas del corpus real no se tocaron.

---

### Dominio C — Suite de Pruebas de Estrés Adversarial (no es precisión ni tasa de fallo)

16 casos diseñados para romper el sistema. Esta suite existe porque VIGÍA
reclama admisibilidad Daubert — lo que requiere falsificabilidad documentada.

| Clase de ataque | Casos | Manejados | Notas |
|----------------|-------|-----------|-------|
| Manipulación temporal | 2 | 2 | Compuerta dura bloquea el veredicto |
| Ahogamiento de señal / inyección de ruido | 2 | 2 | SUSPICION conservador |
| Atribución cultural (falsa bandera) | 2 | 2 | L-019 RESUELTO |
| Inyección de prompt vía evidencia | 1 | 1 | Bloqueo LLMShield ✓ |
| Manipulación epistémica | 3 | 3 | ABSTAIN / SUSPICION correcto |
| Fabricación de consenso por confianza | 2 | 1 | L-016: limitación documentada |
| Bypass de compuerta de corroboración | 1 | 1 | Compuerta mantiene |
| Evasión por agregación direccional | 1 | 0 | L-015: limitación documentada |
| **Total Dominio C** | **16** | **14 (87,5%)** | 2 limitaciones documentadas |

Resultados adversariales completos: `results/llm_mode/`
Limitaciones conocidas: [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md)
