# PROPUESTA L-029 — Qué hacer con DARVO: dossier de decisión para firma

**Fecha:** 2026-07-17 · **Sesión:** investigación abductiva multi-agente post-B-140
**Estado:** PROPUESTA — requiere decisión de la mantenedora en los puntos marcados FIRMA
**Método:** 5 investigadores paralelos (superficie de veredictos, ruta CAIE, censo
empírico con simulación, arquitectura de pareo, doctrina Daubert) → 3 propuestas
rivales (evidence-first / court-first / minimal-risk) → 6 refutadores adversariales
(Daubert + ingeniería, por propuesta) → verificación final de cada hallazgo judicial
contra el árbol vivo por el sintetizador. ~1.4M tokens de subagentes, 368 lecturas y
ejecuciones. Todo claim citado abajo fue verificado contra código o ejecutado.

---

## 0. Resumen ejecutivo — las tres respuestas

| Ítem abierto de L-029 | Recomendación | Base |
|---|---|---|
| (1) ¿Efecto del patrón DARVO sobre el veredicto del motor? | **NO ahora, y NUNCA vía keywords de descripción.** Reapertura pre-registrada solo con detector v2 device-class + corpus independiente (§4). | Simulado en ambas direcciones: 0 ganancias, solo regresiones (§2.2). Precedente E2 (−38). Dirección depende del POV, que el scorer no puede leer (§2.3). |
| (2) ¿`false_flag` como veredicto sellado? | **NO — rechazo con firma y condición de reapertura.** El claim relacional viaja en anotación + campo cuadripartito + narrativa. | Error de categoría (escalar total-order vs claim direccional); 3 rutas de fallo silencioso; freeze de SUBMISSION_COMPLIANCE; N=1 real (§3). |
| (3) ¿Revisión pareada cross-bundle? | **SÍ — construir ya, como arquitectura SIN autoridad de veredicto.** Tool MCP + registro de linkage firmado. Scoring pareado completo: diferido (bloqueador fatal N=1 auto-referencial). | La inversión de roles es una relación ENTRE bundles; KIWI-002 nunca dispara el detector — el agresor escribe su propia narrativa (§2.4). |

**Las tres respuestas sobrevivieron a los 6 refutadores adversariales.** Lo que NO
sobrevivió fueron varias premisas de implementación de las propuestas — corregidas
en el plan de fases (§5) — y dos claims de la propia sesión B-140 (§1).

---

## 1. Correcciones honestas a B-140 (verificadas por ejecución)

1. **ELI es un falso positivo del detector.** `VIGIA-REAL-MAGNET-2021-IOS-ELI`
   está anotado por coincidencia pura de substrings: `'server'` matchea dentro de
   "Psiphon proxy configured with **4 S3 server list URLs**" (A02) y `'no contact'`
   dentro de "no messages, **no contacts** database" (A04) — un plural inglés.
   El caso es de evasión de comunicaciones mono-actor: no hay denunciante, no hay
   estructura de dos actores, no hay infraestructura de vigilancia. El comentario
   in-code "exactamente los 5 casos correctos" (`darvo_detector.py`) es **falso**
   y el registro B-140 debe corregirse a "4 verdaderos + 1 FP corregido" — nunca
   en silencio (es exactamente la frase que la contraparte leería en voz alta).
   Tasa observada: 1 FP / 5 disparos = 20% sobre los únicos datos existentes.
2. **Los "5 casos" son en realidad N=1 expediente.** KIWI-001/003 son dos
   detecciones del MISMO expediente MPF7779408; KIWI-004/005 son copias
   byte-idénticas declaradas de KIWI-003 (inmunidad a narrative-injection, no
   DARVO); ELI es el FP. Muestras independientes reales: **1**.

---

## 2. Evidencia empírica central (censo + simulación, 201 casos)

### 2.1 Estado actual
- Exactamente 5 bundles anotados; **los 5 ya aciertan su expected_verdict**
  (KIWI-001 SUSP 0.2696, KIWI-003/4/5 MALICE 0.4360, ELI SUSP 0.2872).
  **Un efecto de veredicto no tiene nada que arreglar en el corpus actual.**

### 2.2 Simulación de candidatos (post-proceso sobre score sellado + réplica del gate de corroboración)
| Candidato | Flips | Resultado |
|---|---|---|
| boost `+p·k`, k∈{0.05, 0.10} | 0 | peso muerto |
| boost `+p·0.20` | 2 | **2 regresiones**: ELI y KIWI-001 SUSP→MALICE selladas (el gate cross-domain ABRE para los 5) — una MALICE acuñada desde el FP de un plural inglés |
| penalidad `−p·k`, k≤0.10 | 0 | peso muerto |
| penalidad `−p·0.20` | 3 | **3 regresiones**: degrada las MALICE verdaderas del POV víctima |
| floor NOISE→SUSPICION (forma B-126) | 0 | inerte: ningún caso anotado es NOISE; el bundle que apuntaría (agresor scrubbed) es justo el que no tiene keywords |
| fractura CAIE simétrica sev 0.8 (ambas direcciones) | 2 / 5 | mismas regresiones, 0 ganancias. Precedente: FASE2 E2 ya refutó fractura-como-veredicto con −38 de accuracy |

### 2.3 El problema estructural de dirección
El signo correcto del efecto depende de QUIÉN autoría el bundle (en el POV víctima
los marcadores DARVO SON la evidencia inculpatoria correcta; en el POV agresor
serían descrédito del denunciante) — y el POV es **ilegible para el scorer por
esquema**: `framing` es campo top-level que el whitelist `_valid_fields`
(vigia_scorer.py:648-651) descarta; el `Artifact` de CAIE no tiene campo de actor
(caie.py:736-757); `semantic_role` es examiner-declared-only porque el
auto-clasificador degradó 9 casos maliciosos medidos. Un canal POV nuevo sería un
campo narrativo que EN EL MODELO DE AMENAZA escribe el propio agresor (L-004).

### 2.4 La ceguera que ningún mecanismo single-bundle puede cerrar
KIWI-002 (bundle POV-agresor, la denuncia del acusador): `surveillance_count=0`,
sin anotación — **el agresor controla su propia narrativa y no describe su
infraestructura**. Verificado en vivo. El detector mide la narración de la
conducta, no la conducta. Por eso el ítem 3 (pareo) es la única arquitectura donde
la inversión de roles es siquiera expresable.

### 2.5 Doctrina que prohíbe el efecto por keywords (tres vías independientes)
- **B-070**: evidencia narrativa fuera del composite y del gate (cerró NGDC-003).
- **Simetría Austin L-004/L-054**: "una descripción que dice 'honeypot' no hace
  de la evidencia un honeypot". No se puede atenuar `authorized=true` y a la vez
  escalar por la palabra `bloqueado` — regla de confianza asimétrica indefendible.
- **L-016/L-049/L-067-§9.4**: todas las descripciones KIWI fluyen por UN canal
  (una examinadora, un paquete judicial): N hits de keyword = una fuente autoral
  contada N veces. Y el gate de corroboración NO intercepta: los tipos DARVO
  lucen multi-dominio (D1a/D3/D5) aunque toda descripción tenga un solo narrador.

---

## 3. Ítem 2 — `false_flag`: por qué NO (síntesis del mapa de superficie)

- **Error de categoría**: el ladder es un orden total sobre un escalar; false_flag
  es relacional y direccional (MALICE hacia el denunciante + exculpación hacia la
  acusada, simultáneas). El comparador no tiene regla ⊆ defendible ("¿false_flag
  es superconjunto de MALICE? ¿contra quién?") — la doctrina de over-severity se
  re-deriva, no se extiende.
- **Tres rutas de fallo silencioso en migración parcial** (verificadas):
  `_apply_quadripartite` ValueError → el caso entero degrada a ABSTAIN
  (vigia_scorer.py:394-399 → sift_orchestrator.py:1149-1155); `bundle_builder`
  mapea veredicto desconocido → ABSTAIN en silencio (:511) **con devil_advocate
  salteado** (:570-579); `run_all_agent` lo relee como UNKNOWN. Y el clasificador
  substring: una hipótesis `FALSE_FLAG_MALICIOUS_*` matchearía `"MALICIOUS"` y
  sellaría MALICE contra el bundle de la víctima (vigia_agent.py:197).
- **Trampa Daubert del verificador de terceros**: R6/R7 solo exigen
  devil_advocate para MALICE/INTENT (forensics/verify_ebs_v1.py:413,426) — la
  acusación más pesada del sistema sellaría SIN paso de falsación y las copias
  viejas del verificador en circulación la certificarían para siempre.
- **Freeze**: SUBMISSION_COMPLIANCE.md:449 y DAUBERT_JUDICIAL.md:71 sellan el
  vocabulario públicamente; L-029 reserva el cambio a firma.
- **Dónde vive el claim relacional** (portadores sancionados, en orden):
  (a) anotación `darvo_pattern` sellada (ya existe, B-140); (b) campo
  `role_inversion: Optional[dict]` en `QuadripartiteVerdict` — CAMPO, no estado
  nuevo (el cuadripartito codifica confianza, no atribución) — FIRMA; (c) Amicus
  Curiae / narrativa. **Descartado**: la ruta hypothesis-string
  (`DARVO_ROLE_INVERSION_SUSPECTED`→SUSPICION) — mueve veredictos, es el ítem 1
  disfrazado de ítem 2.
- **Reapertura**: necesidad documentada de consumidor (p.ej. orden judicial que
  exija la atribución dentro del campo de veredicto sellado) que los tres
  portadores demostradamente no puedan cargar + bump de esquema firmado +
  claims versionados como superseded-not-altered.

---

## 4. Ítem 1 — condiciones de reapertura del efecto de veredicto (pre-registradas)

Se reabre SOLO cuando TODAS:
1. **Criterio B-112**: ≥2 expedientes independientes adicionales con inversión de
   roles confirmada por ground truth, distintos de MPF7779408.
2. **Upgrade evidencial**: logs de vigilancia como artefactos DEVICE-class cuyo
   `acquisition_hash` cubre los BYTES del log, con campos parseados tipados
   (IPs, conteos, timestamps) — nunca `description`; cero-contacto como negativo
   verificado de dispositivo (reporte de extracción propio, hasheado), no como
   aserción de `temporal_context`. La ruta B-112 SELF_INCRIMINATION_LOG (logs
   aportados voluntariamente por el acusador al expediente) es la única posición
   epistémica que disuelve la objeción "el autor controla la narrativa" — y es
   exactamente el patrón de KIWI-003-A04.
3. **Pisos de calibración**: L-033 ≥20 señales etiquetadas independientes (piso
   duro); §9.4-LIM ≥50 (barra creíble); set de polaridad negativa (denunciantes
   genuinos con vocabulario de vigilancia legítimo — expandir desde
   FF-GENUINE-001) donde NINGUNO dispare; par adversarial L-049 (caso con
   keywords inyectadas que NO debe escalar + caso true-DARVO scrubbed que
   documenta el FN honestamente).
Mecanismo si se reabre: primero floor NOISE→SUSPICION forma B-126 sobre detector
v2 (≥2 canales de provenance), después fractura CAIE CONTEXTUAL (nunca corrobora
el gate MALICE) bajo un contrato A1 de L-051 formalizado. Gate pre-registrado
`fixed>=1 AND broken==0` + demo red-team obligatoria: tipear keywords en
descripciones NO debe mover ningún veredicto sellado, o no se shipea.

---

## 5. Plan de fases propuesto (síntesis post-refutación)

> Los refutadores tumbaron premisas de implementación de las 3 propuestas; este
> plan incorpora esas correcciones. Hallazgos judiciales verificados por el
> sintetizador contra el árbol vivo: ver §6.

**F0 — Higiene del detector y del canal muerto (UNA sola tanda firmada).**
Los jueces demostraron que separar "fix de anotación" y "fix de pipeline" en dos
fases viola el propio contrato de firmas: el matcher es compartido con
`compute_darvo_penalty`. En una tanda:
1. Matching con word-boundaries / tokenizado (mata ELI: 'server' en "S3 server
   list", 'no contact' en "no contacts database"). ELI queda des-anotado y eso
   ES el fix (FP corregido pre-emisión — protocolo de autocorrección funcionando,
   documentado con los substrings verbatim, no en silencio).
2. **Retirar (no estrechar) el canal de penalidad del pipeline**: verificado por
   ejecución que es código muerto en runtime — `SignalOutput` no tiene campos
   `description`/`evidence_type`, así que `adjust_consistency_score` devuelve
   siempre base (penalidad 0 incondicional). Mantener un canal muerto que se
   despertaría con cualquier refactor del contrato de señales es superficie de
   ataque gratuita (la contraparte: "¿por qué su sistema carga un camino de
   scoring que ustedes admiten que no hace nada?"). Retiro + test de regresión
   que fije que keywords en descripciones NUNCA mueven `consistency_score`.
3. Corregir el comentario falso de `darvo_detector.py` y el registro B-140 en
   trackers + L-029 ("exactamente 5" → "4 + 1 FP corregido").
4. **B-141 (bug real nuevo, P1)**: `run_vigia` (pipeline.py:1382-1388) pasa
   `description=` a un `SignalOutput` que no acepta el kwarg → TypeError → el
   `try/except` por señal loguea "Señal inválida ignorada" y **descarta TODAS
   las señales en silencio** — `run_vigia` corre con cero señales en este
   deployment. Verificado por ejecución. Fix + test rojo primero.
   GATE F0: censo de anotación == exactamente {KIWI-001, 003, 004, 005}; 201
   casos 0 flips; test ELI-no-anotado; suite verde.

**F1 — Endurecimiento de la anotación (0-flip gate; sin firma).**
Incorporando las refutaciones FF-1/F2 de los jueces (la anotación sellada SÍ
porta fuerza prejudicial ante un jurado aunque `verdict_effect: none`):
1. Caveat L-004 legible por máquina DENTRO del bloque sellado: "trigger class:
   examiner-authored free text; no assertion force; L-004 applies".
2. `devil_advocate` del bloque **obligatorio, no voluntario** (el Protocolo de
   Refutación del repo aplicado a la única salida apuntada a un rol humano):
   la hipótesis benigna ("jerga de seguridad reutilizada por denunciante
   descuidado / honeypot defensivo de víctima genuina") se genera y sella junto
   al bloque.
3. **NO** agregar `attributed_actor` ni atribución nominal al bloque sellado
   (refutación F1 del juez Daubert: un registro HMAC-sellado atribuyendo el rol
   de vigilante a un actor nombrado, generado desde texto libre, es el vector de
   difamación realizado). La atribución queda en la narrativa, etiquetada como
   testimonio pericial.
4. Trade-off documentado, decisión FIRMA: publicar `matched_spans` verbatim da
   trazabilidad Daubert pero publica la lista de scrubbing a futuros agresores.
   Recomendación: spans SÍ (la transparencia gana; el scrubbing ya es trivial
   dado que las keywords son públicas en el repo).

**F2 — Pareo como arquitectura (dos entregables, autoridad de veredicto CERO).**
1. **Tool MCP `compare_paired_bundles(path_a, path_b)`** (Modo 2; sin gate de
   corpus — no toca camino de veredicto): sub-métricas deterministas primero
   (igualdad de `case_origin`; delta de `prior_trust` en Fraction — 0.3 vs 0.8
   ES la señal L-029; `detect_darvo_pattern` sobre la unión; solapamiento/
   disyunción de provenance-chains — la disyunción ES la señal de asimetría);
   narrativa Thirdness LLM después, explícitamente fuera del loop de decisión
   (invariante 3), con el caveat L-004 en el output del propio tool.
2. **Pase de linkage determinista en el batch runner** (junto a
   `check_label_consistency`): agrupa por `case_origin`, `framing` complementario
   (¡campo TOP-LEVEL, no de artifact — error de spec detectado por el juez 12!),
   emite REGISTRO DE LINKAGE FIRMADO standalone referenciando ambos
   `bundle_hash` (doctrina R3-5: fuera de la estructura editable). Correcciones
   de los jueces incorporadas: (a) **regla de dedup de copias** — KIWI-004/005
   son byte-idénticos a 003; sin dedup el grupo MPF7779408 emitiría 3 linkages
   de UN expediente, dos contra evidencia duplicada (la violación L-016 que el
   propio diseño lista como trigger de demote); (b) **scoping de corpus
   pinneado** — `RT-FN-COLLUSION-001` (red-team) YA porta `case_origin:
   MPF7779408` con artifact_ids de KIWI-006 reusados: el ataque de join-key
   forjado no es hipotético, existe en el repo; queda como fixture permanente
   del gate (el linkage sobre red-team debe emitir el registro CON su caveat de
   colisión, no certificar limpieza); (c) label-blind por construcción (test:
   leer `expected_verdict` levanta).
   FIRMA: formato del registro nuevo. GATE: 0 flips; census de linkage esperado;
   round-trip HMAC.
3. **Scoring pareado completo / tipo de bundle nuevo: DIFERIDO** con bloqueador
   nombrado: el corpus tiene UN par POV genuino y ambas mitades las escribió la
   misma examinadora (AT-001) — par auto-referencial; calibrar un veredicto
   relacional sellado sobre eso falla el prong de error-rate de Daubert de
   plano y lavaría narrativa pericial dentro de un sello determinista.

**F3 — Adquisición de datos (bloquea F4; sin código).** Los cuatro ítems de §4.3.

**F4 — Efecto de veredicto (solo si §4 completo; FIRMA).**

---

## 6. Hallazgos colaterales verificados (para trackers)

| ID propuesto | Hallazgo | Severidad |
|---|---|---|
| **B-141** | `run_vigia` dropea TODAS las señales por TypeError silencioso (`description=` a `SignalOutput` sin ese campo; pipeline.py:1382-1388, except al :1391 "Señal inválida ignorada") | P1 — camino `run_vigia` corre vacío en el deployment dataclass |
| **B-142** | Canal DARVO del pipeline es código muerto en runtime (SignalOutput sin `description`/`evidence_type` → penalidad siempre 0) + ELI FP + comentario in-code falso "exactamente los 5" | P2 — integridad del registro B-140 + superficie latente |
| (fixture) | `RT-FN-COLLUSION-001` colisiona `case_origin` MPF7779408 con artifact_ids KIWI-006 reusados — ataque de join-key preexistente; fixture obligatoria del gate de linkage F2 | doc |

## 7. Scores de los refutadores (transparencia)

| Propuesta | Juez Daubert | Juez ingeniería | Qué tumbaron |
|---|---|---|---|
| Evidence-first | 6/10 | 6/10 | role_attribution sellado sin firma (vector de difamación); "the hash IS the direction" (hash prueba integridad, no autoría); premisa "leak vivo" (era latente); "fixed≥10 BEN" inmedible (son 6) |
| Court-first | 6/10 | 7/10 | auto-refutación anotación-inerte vs FP-como-liability-P1; el FP ELI ya ES la atribución errónea sellada en un caso real; N=1 circular infecta lo que se shipea; F0/F1 sin fusionar viola su propio contrato de firmas; "zero collisions" falso (RT-FN-COLLUSION) |
| Minimal-risk | 5/10 | 6/10 | P0b "defecto vivo" empíricamente falso (canal muerto en runtime); gate inmedible sobre población que el pipeline nunca ve; matched_spans publica la lista de scrubbing; framing no está en artifacts[].metadata |

Las tres recomendaciones de cabecera fueron confirmadas por los seis; toda
refutación fatal fue de premisas de implementación, todas incorporadas en §5.

## 8. Fallibilismo — qué reabre cada decisión

- **Anotación-only (ítem 1)**: (a) criterio B-112 disparado; (b) upgrade
  evidencial §4.2 existente; (c) daño de dirección documentado — caso real donde
  la anotación presente y correcta no evitó un resultado erróneo contra la
  víctima verdadera. (a)+(b) juntos abren prototipo F4.
- **Rechazo false_flag (ítem 2)**: necesidad de consumidor/corte documentada que
  los tres portadores no puedan cargar.
- **Pareo sin autoridad (ítem 3)**: se RESTRINGE si un counter-bundle forjado
  induce un pareo que diluya/invierta un veredicto correcto; se DEMOTE a
  tool-only si una conclusión pareada se rastrea a un bundle miembro fabricado.
- **Standing falsifier de todo lo shipeado**: una sola demo estilo L-049 de que
  tipear keywords en descripciones mueve CUALQUIER veredicto sellado o decisión
  → rollback inmediato del mecanismo ofensor. Post-F0 debe ser imposible por
  construcción; la demo vive en la suite red-team como regresión permanente.

---

*Dossier generado por investigación abductiva multi-agente (bucle A-D-I completo:
abducción por 3 lentes rivales, deducción de consecuencias por 5 investigadores,
inducción por censo/simulación de 201 casos y 6 refutaciones adversariales
verificadas por ejecución). Las decisiones FIRMA quedan abiertas para Anna.*

---

## ADDENDUM 2026-07-17 — Auditoría adversarial independiente (Kimi) — CONFIRMADO

Veredicto completo: `docs/VEREDICTO_KIMI_L029_20260717.md`. Las tres respuestas de
cabecera sobrevivieron; la espina empírica §2.1/§2.2 fue **reproducida de forma
independiente con el gate B-068 REAL** (no una réplica): scores base exactos
(0.2872 / 0.2696 / 0.4360) y las filas boost/penalty fila por fila (2 regresiones
en boost k=0.20 atravesando el gate real; 3 en penalty k=0.20). Correcciones que
este addendum incorpora al registro (la sustancia de las decisiones no cambia):

1. **B-141 son dos síntomas del mismo defecto, por deployment.** Dataclass (sin
   pydantic): TypeError incondicional → todas las señales descartadas con log
   "Señal inválida ignorada". Pydantic v2 (extra='ignore' default): sin error —
   la señal sobrevive pero `description` se pierde EN SILENCIO, sin log. El fix
   correcto es dejar de pasar `description=` (el canal que la quería se retira
   por B-142) y el test debe cubrir ambos modos.
2. **Ancla stale en §3**: `sift_orchestrator.py:1149-1155` no existe en main
   post-merges. La ruta 1 real: `vigia_api.py` no atrapa el ValueError → crash
   RUIDOSO (no ABSTAIN silencioso); las rutas silenciosas reales son
   bundle_builder (default ABSTAIN + devil_advocate salteado) y la re-lectura
   UNKNOWN del runner — ambas verificadas verbatim.
3. **Precisión de wording §1.2**: KIWI-004/005 son copias byte-idénticas **al
   nivel de artifacts** (la evidencia, que es lo que cuenta para N); los archivos
   difieren en case_id/wrapper.
4. **Trampa de implementación F2 (nueva, de Kimi)**: `case_origin` vive en
   `artifacts[].metadata.case_origin`, NO top-level (top-level es None en todos
   los KIWI); `framing` SÍ es top-level. El pase de linkage debe leer la join-key
   de metadata; test obligatorio del gate F2: leerla de top-level debe fallar.
5. **Observación colateral de Kimi (P3, fuera de L-029)**: `_VERDICT_MAP` de
   bundle_builder tampoco contiene INTENT (cae al default ABSTAIN en ese path);
   puede ser intencional (vocabulario EBS) — para revisión del colectivo.
6. Capa honesta compartida: la fila "fractura CAIE simétrica" de §2.2 queda
   PLAUSIBLE (mecanismo + precedente E2), no re-ejecutada por el auditor.
