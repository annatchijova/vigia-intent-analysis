# Auditoría — Whitelist de tipos de evidencia y mobile forensics

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Tag de restauración:** `pre-mobile-whitelist-audit-20260703-173314`
**Alcance:** solo lectura + experimentos reproducibles en scratchpad — **ningún archivo de código fue modificado**.
**Disparador:** caso `VIGIA-OWL-2019-NEXUS5-QUICK` (Digital Corpora, Nexus 5,
Magnet ACQUIRE): la evidencia mobile dio NOISE y requirió override manual.

---

## Resumen ejecutivo

El "whitelist del scorer" son en realidad **cuatro puntos de enforcement
distintos con tres comportamientos distintos** (rechazo, skip silencioso,
fallback puntuado). La causa del NOISE de OWL-NEXUS5 es **compuesta**: los
tipos mobile no existen en `EVIDENCE_PROFILES`, pero el experimento controlado
muestra que el fallback por sí solo no aplasta el veredicto — lo aplasta la
combinación con la degradación de custodia y, en Modo 1, con la agregación en
una sola señal (B-052). La extensión mínima viable son **8 perfiles nuevos con
cero apariciones en el corpus** (riesgo de flip: cero por construcción) más
las entradas de mapa del adapter (B-060). Colateralmente, la auditoría
encontró una **inversión del whitelist**: un tipo desconocido puntúa MÁS ALTO
que un tipo conocido trivialmente spoofeable — exactamente el bypass que el
propio comentario de CAIE dice prevenir.

---

## 1. Mapa del whitelist actual

### 1.1 La fuente única de verdad

**`vigia/tools/caie.py:246-289` — `EVIDENCE_PROFILES`** (25 tipos, cada uno
`EvidenceProfile(spoofability, base_weight, descripción)`):

| Clase | Tipos (spoofability / weight) |
|-------|-------------------------------|
| Trivialmente spoofeable | `ip_geolocation` (.90/.15), `cultural_marker` (.90/.15), `log_entry` (.85/.15), `user_agent` (.85/.15) |
| Tamper-evident intermedio | `windows_event_log` (.55/.25) |
| Moderado | `file_timestamp` (.70/.20), `file_hash` (.50/.25), `dns_record` (.60/.20), `registry_key` (.55/.20), `network_flow` (.75/.18), `file_metadata` (.65/.20) |
| Difícil de spoofear | `usn_journal` (.20/.30), `memory_process` (.15/.30), `lsass_session` (.15/.30), `prefetch` (.25/.28) |
| Estructuralmente irrefutable | `kernel_structure` (.10/.35), `hmac_audit_log` (.05/.40), `hardware_serial` (.05/.40) |
| Documento | `document_visual` (.40/.25), `document_geometry` (.45/.22) |
| Criptográfico | `cryptographic_hash` (.05/.45), `digital_signature` (.10/.40) |
| Anti-forense (TCV) | `timestamp_precision` (.05/.40), `mft_entry` (.05/.42), `usn_journal_gap` (.10/.38) |

**Cero tipos mobile.** Ni `chat_message`, ni `sms`, ni `web_search`, ni
`app_data`, ni `social_media`, ni `call_log`, ni `location_data`, ni
`contact_data`.

`_VALID_EVIDENCE_TYPES = frozenset(EVIDENCE_PROFILES.keys())` —
`vigia/tools/caie.py:292`.

### 1.2 Los cuatro puntos de enforcement (tres comportamientos)

| # | Punto | Archivo:línea | Comportamiento con tipo desconocido |
|---|-------|---------------|--------------------------------------|
| E1 | `CAIE.add_artifact` | `vigia/tools/caie.py:897-908` | **RECHAZA** (return False) + audit log `CAIE_INVALID_EVIDENCE_TYPE` |
| E2 | `cross_artifact_analysis` | `vigia/tools/caie.py:2201-2213` | **SKIP silencioso** del artefacto + `CAIE_UNKNOWN_TYPE_SKIPPED` — el artefacto no participa de fracturas ni del composite CAIE |
| E3 | Scorer `_vigia_score` | `vigia_scorer.py:513` (lookup), `:470-472` (fórmula), `:529` (fallback) | **FALLBACK PUNTUADO**: `spoofability=0.50, weight=0.20` — el artefacto SÍ se puntúa, con perfil no calibrado (limitación declarada en `:473`) |
| E4 | Adapter EBS→CAIE | `vigia/core/forensic_adapter.py:85-112` (`_EVIDENCE_MAP`), `:76-83` (`_LAYER_MAP`), `:114-121` (`_ONTOLOGY_MAP`) | **Passthrough + defaults silenciosos**: tipo desconocido pasa crudo (`_EVIDENCE_MAP.get(t, t)`) y cae en E1/E2/E3; layer default `DISK_MFT`, ontología default `TECHNIQUE` (B-060) |

**Asimetría E3 vs E4 (colateral):** el adapter remapea etiquetas legacy
(`event_log` → `windows_event_log`, `mft` → `file_timestamp`), pero el scorer
E3 busca el tipo **crudo** en `EVIDENCE_PROFILES` sin pasar por ese remapeo.
Un caso JSON con `evidence_type: "event_log"` (3 apariciones en el corpus)
recibe el fallback en el scorer aunque su equivalente canónico esté
whitelisteado.

**Gemelo divergente:** `caie_legacy_root.py:216-254` contiene una copia
vieja de `EVIDENCE_PROFILES` **sin** `windows_event_log`, `network_flow` ni
`file_metadata` (misma familia que B-055, copia stale). Cualquier extensión
debe decidir qué hacer con ese archivo (recomendación: no tocarlo — está
fuera del camino vivo — pero dejar constancia).

### 1.3 Cuánto del corpus ya vive fuera del whitelist

Censo sobre `data/cases/**/*.json` (267 casos con `artifacts`, script
reproducible en la metodología):

- **53 tipos distintos** en uso; solo **18 están whitelisteados**.
- **~980 artefactos** usan tipos whitelisteados; **~193 artefactos (~16%)**
  ya viajan hoy con el fallback E3 / skip E2: `binary` (59),
  `binary_executable` (17), `document` (16), `container_zip` (15),
  `malware_static_analysis` (7), `email_content` (6), `archive` (6),
  `network_traffic` (5), `keylogger_capture` (5), etc.
- **Los 8 tipos mobile propuestos: 0 apariciones.** Ningún caso del corpus
  los usa hoy.

### 1.4 El camino Modo 1 (agente) NO pasa por este whitelist

En evidencia mobile-only, el shim usa la ruta `_mobile_hypothesis()`
(`sift_orchestrator.py:76-113`, fix F6): la hipótesis se deriva de los
z-scores de las señales mobile, **sin CAIE ni `EVIDENCE_PROFILES`** (mitigante
ya documentado en B-060). El cuello de botella ahí es otro: cada motor mobile
emite **una sola señal agregada** (`android_forensics.py:121-193`,
`to_signal()`, `artifact_type: "android_forensic"`) — es B-052-P2, pendiente.
Con una sola señal primaria y `is_conclusive=False`, el gate `<3` del
clasificador da hoy **ABSTAIN** (la corrida histórica de 2026-06-30 dio NOISE
porque precedía a F6/Tanda A; los bundles committeados
`VIGIA-OWL-2019-NEXUS5-QUICK*` muestran la evolución: 0 señales/UNDETERMINED
→ 1 señal `android_forensic`/`MOBILE_EVIDENCE_ANALYZED`).

---

## 2. Tipos nuevos para mobile forensics real

Propuesta de perfiles, calibrados **por analogía con la escala existente**
(referencias: `registry_key` 0.55 = "editable con privilegios";
`log_entry` 0.85 = "editable por admin"; `memory_process` 0.15 = "requiere
compromiso live"). En Android/iOS, "editable con root" es la analogía de
"editable con privilegios"; lo que sube el peso forense es la
**correlacionabilidad externa** (carrier, servidor, cell towers).

| Tipo | Spoofability | Weight | Justificación forense | Módulo SIFT que lo alimenta hoy |
|------|-------------|--------|----------------------|--------------------------------|
| `chat_message` | 0.35 | 0.28 | SQLite de apps (msgstore.db, Signal DB): WAL + integridad FK + correlación server-side. Falsificar una conversación coherente con timestamps WAL consistentes exige herramientas + root | `android_forensics._analyze_sms()` (parcial, L-041); detección de apps: `_analyze_accounts()` |
| `sms` | 0.40 | 0.26 | `mmssms.db` editable con root, pero correlacionable con CDR del carrier — la evidencia clave de OWL-NEXUS5 es exactamente un SMS | `android_forensics._analyze_sms()` (`:400`); iOS `sms.db` en `ios_forensics` |
| `call_log` | 0.40 | 0.26 | `calllog.db` editable con root; correlación CDR idéntica a sms | `android_forensics._analyze_call_log()` (`:480`) |
| `web_search` | 0.45 | 0.24 | History SQLite de Chrome/Safari: editable con root, pero visit_count/timestamps encadenados son cross-checkeables | `android_forensics._analyze_chrome()` (`:512`, ya distingue BROWSER_EXPLOIT_RESEARCH/BOOKMARKED) |
| `app_data` | 0.50 | 0.22 | Storage privado de apps genérico — heterogéneo, sin garantía uniforme | `android_forensics._analyze_accounts()` (`:646`), `_analyze_bluetooth()` (`:676`) |
| `social_media` | 0.55 | 0.22 | Cache cliente editable; correlación server-side posible pero fuera del alcance del examen local | `google_takeout` module; `_analyze_accounts()` |
| `location_data` | 0.30 | 0.30 | Historial de ubicación (Takeout/GPS): falsificarlo de forma *consistente* con cell towers y actividad de apps es difícil — análogo a `usn_journal` en la escala | `google_takeout` (Location History); iOS significant locations |
| `contact_data` | 0.60 | 0.20 | `contacts2.db` trivialmente editable; su valor es estructural (EMPTY_CONTACTS, sender-not-in-contacts de L-041) | `android_forensics._analyze_contacts()` (`:444`) |

Sobre `bird_trade` (mencionado en el pedido): **no es un tipo de evidencia** —
es contenido/semántica del caso OWL (comercio ilegal de aves). El contenido
pertenece a las reglas de detección (L-041: transaction-language), no al
whitelist de tipos. Mezclar semántica de caso en el whitelist lo convertiría
en una lista de escenarios (el anti-patrón que L-041 explícitamente prohíbe:
"must NOT be a hardcoded 'owl' keyword list").

---

## 3. Riesgo de extender el whitelist

### 3.1 ¿Puede romper el corpus? — No, por construcción (con una condición)

- Los 8 tipos propuestos tienen **0 apariciones** en los 267 casos con
  artifacts. Agregar perfiles que ningún caso usa no puede mover ningún
  veredicto existente: el lookup `EVIDENCE_PROFILES.get(...)` de cada caso
  del corpus resuelve exactamente igual que antes.
- **Condición de scope:** la extensión debe limitarse a los 8 tipos mobile.
  Agregar perfiles para tipos que el corpus SÍ usa hoy con fallback
  (`binary` ×59, `document` ×16, `network_traffic` ×5…) **sí movería
  ~193 artefactos** y exigiría corrida comparativa completa. Es tentador
  "aprovechar el viaje" — no hacerlo en el mismo cambio.

### 3.2 Cuantificación experimental (reproducible)

Caso sintético: 5 artefactos mobile, `raw_score=0.85`, 3 `source_tool`
distintos, metadata de adquisición NIST completa. Corrido contra
`_vigia_score` real (los números C usan monkeypatch de perfiles en memoria,
sin tocar código):

| Variante | Procedencia intacta (`provenance_chain` válida) | Procedencia degradada (sin chain → `epc=1/10`) |
|----------|--------------------------------------------------|--------------------------------------------------|
| A) Whitelist actual (fallback 0.50/0.20) | **MALICE** 0.6555 | NOISE 0.0501 / UNKNOWN 0.0851 |
| B) Remapeo manual a `log_entry`/`file_metadata` | **SUSPICION** 0.3218 | NOISE |
| C) Perfiles mobile propuestos | **MALICE** 0.76 | UNKNOWN 0.105 |

Tres conclusiones que corrigen la intuición inicial:

1. **El fallback solo no explica el NOISE.** Con custodia intacta, hasta el
   fallback da MALICE. El NOISE de OWL-NEXUS5 es compuesto: tipos fuera del
   whitelist (E2 los excluye de CAIE → sin fracturas) × degradación de
   custodia (caso quick-triage sin `provenance_chain`/adquisición completa →
   trust 0.1) × en Modo 1, la agregación B-052 (una sola señal).
2. **Inversión del whitelist (hallazgo colateral, candidato a bug):** el
   fallback "conservador" (0.50/0.20) puntúa **más alto** que `log_entry`
   (0.85/0.15) — fila A > fila B. Un tipo *desconocido* rinde mejor que un
   tipo *conocido trivialmente spoofeable*. El comentario de E1
   (`caie.py:905`: "Unknown types could bypass spoofability weighting")
   describe exactamente este bypass — CAIE lo cierra rechazando, pero el
   scorer E3 lo deja abierto: un caso JSON adversarial puede inventar
   `evidence_type: "foo"` para esquivar el perfil 0.85 de su tipo real.
   Propuesta: fallback ≥ 0.85 de spoofability (peor clase conocida), no 0.50.
3. **El efecto de C sobre A es al alza (+0.10 de score en este sintético):**
   los perfiles propuestos pesan más que el fallback. Para casos futuros con
   tipos mobile, C cruza umbrales antes que A. Ningún caso existente los usa,
   pero los casos nuevos deben calibrarse contra esta tabla, no contra el
   fallback.

### 3.3 Riesgos indirectos

- **Noisy-OR / independencia:** CAIE agrupa por `(source_tool,
  evidence_type)` (`caie.py:1734-1737`). Tipos nuevos = más grupos
  independientes = composite más alto y menos penalidad `<3 fuentes`
  (`:1770-1775`). Es el comportamiento deseado (la evidencia mobile ES
  heterogénea), pero explica por qué C > A: no es solo el weight.
- **Gate de corroboración del scorer** (`vigia_scorer.py:747-753`): MALICE
  exige `n_artifacts ≥ 4 OR n_unique_types ≥ 3`. Tipificar mobile ayuda a
  cruzarlo legítimamente (hoy 5 artefactos `android_forensic` = 1 tipo único).
- **Mapas del adapter (B-060):** sin entradas en `_LAYER_MAP`/`_ONTOLOGY_MAP`,
  los tipos nuevos caen a `DISK_MFT`/`TECHNIQUE` en silencio. La extensión
  del whitelist sin la extensión de los mapas deja la capa epistémica
  equivocada.
- **Golden rules / fracturas:** ninguna regla de fractura actual está keyed
  por estos tipos — la extensión no habilita ni deshabilita fracturas. Las
  fracturas cross-mobile (p.ej. SMS que refiere una ubicación contradicha por
  location_data) serían trabajo futuro, no MVP.
- **Gemelo legacy** (`caie_legacy_root.py`): si se extiende solo el vivo, la
  divergencia crece; si se extienden ambos, se perpetúa la copia. Decisión
  explícita requerida (recomendación: solo el vivo + nota).

---

## 4. Extensión mínima viable (para OWL-NEXUS5 honesto sin override)

Dos fases porque el whitelist **no es el único** cuello de botella — la fase 1
sola arregla el camino scorer (Modo 4 / case JSON), no el camino agente.

### Fase 1 — Whitelist + mapas (cero riesgo de corpus, ~30 líneas)

1. `EVIDENCE_PROFILES` += los 8 perfiles de la tabla §2
   (`vigia/tools/caie.py:246-289`). `_VALID_EVIDENCE_TYPES` se actualiza solo
   (deriva del dict).
2. `forensic_adapter.py`: entradas mobile en `_LAYER_MAP` (nueva capa o
   `DISK_MFT` explícito con comentario), `_EVIDENCE_MAP` (identidad),
   `_ONTOLOGY_MAP` — y las 4 etiquetas de motor (`android_forensic`,
   `ios_forensic`, `macos_forensic`, `google_takeout`) mapeadas a algo
   razonable mientras B-052-P2 no exista (cierra B-060).
3. **Test de contrato** (propuesta B-060): test que falle si algún
   `artifact_type`/`evidence_type` emitido por un motor no resuelve en
   `EVIDENCE_PROFILES` y en los 3 mapas del adapter — convierte la convención
   en contrato.
4. Validación: suite completa + corpus 198/198 + corrida comparativa
   (esperado: **0 flips, 0 moves** — ningún caso usa los tipos).

**Resultado fase 1:** un case JSON de OWL-NEXUS5 con artefactos tipificados
(`sms`, `web_search`, `contact_data`…) y custodia declarada se puntúa con
perfiles calibrados y CAIE lo acepta (fracturas posibles). El experimento §3.2
fila C muestra el efecto: UNKNOWN→ honesto en degradado, MALICE alcanzable con
custodia intacta y corroboración.

### Fase 2 — Señales tipificadas en Modo 1 (es B-052-P2, decisión aparte)

El agente no verá los tipos nuevos hasta que los motores mobile emitan
señales **por categoría** en vez del agregado único: `to_signal()` →
`to_signals()` con `evidence_type` por hallazgo (sms/contact_data/
web_search/app_data). Con ≥3 señales primarias tipificadas, el gate `<3` deja
de forzar ABSTAIN y `_mobile_hypothesis` (F6) deriva el veredicto de los z
reales.

**Advertencia de honestidad:** fase 1+2 hacen el veredicto *honesto*, no
necesariamente *MALICE*. Para que OWL-NEXUS5 produzca el hallazgo que su
ground truth documenta (el SMS de coordinación), falta además la regla de
contenido de **L-041** (transaction-language + sender-not-in-contacts), que
tiene su propia advertencia de calibración. Sin L-041, el veredicto honesto
probable es SUSPICION/ABSTAIN con narrativa correcta — que ya es
estrictamente mejor que NOISE con override manual.

### Orden recomendado

1. Fase 1 (whitelist + mapas + test de contrato) — riesgo cero, cierra B-060.
2. Fix del fallback invertido (§3.2 hallazgo 2) — una línea + corrida
   comparativa **obligatoria** (los ~193 artefactos con fallback del corpus
   SÍ se mueven a la baja; hay que medir flips antes de decidir).
3. Fase 2 (B-052-P2) — decisión de diseño con su propia auditoría.
4. L-041 (reglas de contenido SMS) — requiere calibración multi-caso, último.

---

## Metodología y reproducibilidad

- Censo de tipos: script inline sobre `data/cases/**/*.json` (§1.3).
- Experimento §3.2: `_vigia_score` real; variante C con monkeypatch en memoria
  de `EVIDENCE_PROFILES` (proceso efímero — el código en disco no se tocó).
- Bundles históricos consultados:
  `results/agent_batch/VIGIA-OWL-2019-NEXUS5-QUICK{,-FIXED}_bundle.json`.
- Referencias cruzadas: B-045 (wiring), B-052 (señal agregada, P1 hecho / P2
  pendiente), B-060 (mapas), L-041 (reglas SMS), L-037 (acquisition
  overrides), B-055 (copias stale).
- **Ningún archivo de código modificado.** Working tree limpio salvo este
  documento.
