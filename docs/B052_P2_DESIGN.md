# B052_P2_DESIGN — Diseño de la señal por dominio para los engines mobile

**Fecha**: 2026-07-10
**Branch**: `claude/macos-modules-design-xk5ecq`
**Restore tag**: `pre-session-20260710-022710`
**Alcance**: investigación y diseño exclusivamente. **Cero código de producto tocado.**
**Método**: `docs/skills/abductive-engineering` + `docs/skills/daubert-defensible-writing`.
Toda afirmación separa OBSERVACIÓN (medida, reproducible) de INFERENCIA y de
DECISIÓN DE DOCTRINA (que requiere firma humana antes de implementar).

---

## 0. Resumen ejecutivo — y la conclusión que cambia el encuadre de riesgo

B-052-P2 propone que los 4 engines mobile SIFT (`macos`/`ios`/`android`/
`google_takeout`) pasen de emitir **una** señal agregada por dispositivo
(`to_signal()`) a emitir **una por dominio de recolección** (`to_signals()`),
para que un caso mobile pueda (a) alcanzar el gate ≥3 primarias del
AbductiveReasoner y (b) satisfacer el gate de corroboración MALICE (≥2 tipos
críticos).

**Hallazgo que reencuadra el riesgo (OBSERVACIÓN, medido 2026-07-10):**

1. **Ningún caso del corpus estándar (199) rutea a los engines mobile.**
   Verificado ejecutando `vigia_agent._build_orchestrator_kwargs` sobre los 199
   JSON de `data/cases/` + `cases/input/`: **0** produjeron
   `android_evidence_path`/`ios_evidence_path`/`takeout_evidence_path`/
   `macos_evidence_path`. Todos van por el path motor JSON (`_analyze_ebs_json`
   → `_vigia_score`). Los 18 casos cuya narrativa menciona "mobile/android/iOS"
   tipifican sus artefactos como `log_entry`/genéricos, no como los tipos
   canónicos mobile.
2. **El único artefacto que ejercita los engines mobile es el directorio
   on-disk `cases/tuck-2019-macos/`** — que NO está en el corpus de 199 (es un
   directorio, no un JSON).

**Consecuencia (INFERENCIA):** el gate comparativo estándar de 199 casos sería
**vacuo** para B-052-P2 — 0 flips garantizados porque 0 casos tocan el código
modificado. Es el mismo caveat de B-092 pero más severo: allá la banda mobile
no aparecía en el corpus; acá **toda la vía de engines mobile** está fuera del
corpus. La advertencia histórica de `AUDITORIA_MACOS_NARRATIVA.md` ("no tocar
sin re-ejecutar el corpus — cambia todos los veredictos mobile") describe un
riesgo que el corpus **no puede medir**. La superficie de validación real es
`tuck-2019-macos` + casos sintéticos multi-dominio.

3. **B-052-P2 es NECESARIO pero NO SUFICIENTE para el único caso mobile real.**
   OBSERVACIÓN (medida sobre `tuck-2019-macos`): las 23 findings del caso están
   **todas en un solo `corr_group`** (`browser_suspicious`,
   `SAFARI_SUSPICIOUS`, severidad 9/20 cada una). Un split por dominio produciría
   **1 señal / 1 dominio** — sigue sin alcanzar ni ≥3 señales ni ≥2 dominios. El
   caso seguiría en ABSTAIN. Para que tuck-2019 cruce el gate hacen falta MÁS
   parsers (los dominios FSEvents/Spotlight/plist/quarantine de
   `MACOS_MODULES_DESIGN.md`), no solo el split. **B-052-P2 y la expansión de
   módulos macOS están acopladas.**

**Recomendación de alto nivel:** implementar B-052-P2 con la postura
conservadora (§4.1, opción 1 + capa DISK_MFT única) es un cambio de bajo riesgo
sobre el corpus (inerte) y arquitectónicamente correcto, PERO no debe venderse
como "arregla los veredictos mobile": no hay evidencia de corpus que lo
respalde, y el único caso real necesita primero más dominios. Las decisiones de
recalibración (§4) sí mueven veredictos y requieren firma.

---

## 1. Los dos gates que el split desbloquea (OBSERVACIÓN, con citas)

1. **Gate ≥3 primarias del reasoner** — `abductive_reasoner.py:114`:
   `primary = [s for s if _is_primary_signal(s)]; if len(primary) < 3 → UNDETERMINED`.
   Un dispositivo mobile aporta ≤1 primaria por engine → nunca llega a 3 → siempre
   abstiene. Medido en tuck-2019: `pipeline_meta.abductive_reasoner =
   "NOT_RUN_MOBILE_SINGLE_SOURCE"`, `n_primary_signals: 1`, veredicto ABSTAIN.
2. **Gate MALICE ≥2 tipos críticos** — `abductive_reasoner.py:354-365`:
   `critical_types = {artifact_type for s if z>3}; if len(critical_types) >= 2 →
   MALICIOUS`. Un engine = un `artifact_type` → mobile nunca presenta 2 tipos
   críticos → techo en `INTENT_DETECTED`.

El split (N dominios → N primarias con N `artifact_type` distintos) desbloquea
ambos **estructuralmente**. Si además cruza los umbrales es cuestión de
calibración (§4).

---

## 2. Mapa de dominios por engine (OBSERVACIÓN — `corr_group` ya existentes)

`corr_group` es la clave natural de split: es la etiqueta de familia de
recolección ya adjunta a cada finding y ya alimenta `build_correlation_groups`
(`_math_utils.py:255-287`).

| Engine | corr_groups (familias) | # |
|---|---|---|
| macOS | `antiforensic`, `browser_suspicious`, `quarantine_suspicious`, `persistence`, `encrypted_apps` | 5 |
| iOS | `sms_phishing`, `encrypted_apps`, `data_minimization`, `browser_suspicious`, `credential_patterns` | 5 |
| Android | `root`, `encrypted_apps`, `data_minimization`, `browser_suspicious` | 4 |
| Google Takeout | `location_gaps`, `browser_suspicious`, `suspicious_apps` | 3 |

(Detalle finding_type→corr_group por engine en el apéndice A.)

---

## 3. Tipificación propuesta por dominio (evidence_type canónico + capa)

Cada dominio emite una `SignalOutput` con `artifact_type` propio y
`evidence_type` canónico de la banda mobile de `EVIDENCE_PROFILES`
(`caie.py:393-400`), ya mapeada a `_DOMAIN_MAP` por B-092.

### macOS
| Dominio | artifact_type | evidence_type | perfil (spoof/weight) | dominio TAXA |
|---|---|---|---|---|
| browser_suspicious | `macos_browser` | `web_search` | 0.45/0.24 | D3 |
| antiforensic | `macos_antiforensic` | `file_metadata` | 0.65/0.20 | D3 |
| quarantine_suspicious | `macos_quarantine` | `app_data` | 0.50/0.22 | D3 |
| persistence | `macos_persistence` | `file_metadata` | 0.65/0.20 | D3 |
| encrypted_apps | `macos_apps` | `app_data` | 0.50/0.22 | D3 |

### iOS
| Dominio | artifact_type | evidence_type |
|---|---|---|
| browser_suspicious | `ios_browser` | `web_search` |
| sms_phishing | `ios_messaging` | `sms` |
| encrypted_apps | `ios_apps` | `app_data` |
| data_minimization | `ios_pim` | `contact_data` |
| credential_patterns | `ios_credentials` | `app_data` |

### Android
| Dominio | artifact_type | evidence_type |
|---|---|---|
| browser_suspicious | `android_browser` | `web_search` |
| root | `android_root` | `app_data` |
| encrypted_apps | `android_apps` | `app_data` |
| data_minimization | `android_pim` | `contact_data` / `call_log` |

### Google Takeout
| Dominio | artifact_type | evidence_type |
|---|---|---|
| browser_suspicious | `takeout_browser` | `web_search` |
| location_gaps | `takeout_location` | `location_data` |
| suspicious_apps | `takeout_apps` | `app_data` |

**Registro requerido:** los nuevos `artifact_type` deben darse de alta en
`forensic_adapter._LAYER_MAP` / `_EVIDENCE_MAP` / `_ONTOLOGY_MAP`
(`forensic_adapter.py:76-148`; hoy solo tienen las 4 etiquetas agregadas). Los
`evidence_type` canónicos ya son claves de `_EVIDENCE_MAP` → si el split setea
`metadata["evidence_type"]` al tipo canónico, la conversión CAIE
(`signal_to_caie_artifact:166-171`) funciona sin cambios.

**Caveat CAIE (INFERENCIA):** todos los dominios propuestos caen en
`filesystem_metadata`/D3 (`social_media`→D4 no lo emite ningún finding hoy). El
decay de saturación de CAIE (`classify_domain`) los colapsa como UNA familia D3
— NO son corroboración independiente *dentro de CAIE*. El gate MALICE del
reasoner (que cuenta `artifact_type` distintos) SÍ se satisface, pero el modelo
de fabricación de CAIE los trata como un canal. Es **correcto** (todos son
SQLite/plist on-disk del mismo dispositivo) y debe declararse como límite
deliberado, no bug.

---

## 4. Escalera z por dominio — la decisión de doctrina que mueve veredictos

### 4.0 OBSERVACIÓN: la escalera actual es device-wide y cross-dominio
Cada `to_signal()` computa UNA z de booleanos del dispositivo entero. El
`composite_score` (noisy_or sobre TODAS las findings) alimenta solo la
**confianza**, no la z. Las ramas MÁS ALTAS de cada escalera son **conjunciones
cross-dominio**:

- macOS `exploit & antiforensic → 3.8` (browser Y antiforensic)
- Android `exploit & root → 3.8` (browser Y root)
- iOS `n_enc≥3 & data_min & hacking → 3.4` (apps Y pim Y browser)
- Takeout `root_tool & susp_search & loc_gap → 3.0` (apps Y browser Y location)

**MEDICIÓN CONCRETA (2026-07-10, `tests/test_macos_multidomain_integration.py`):**
tras implementar los parsers FSEvents/Safari-plists/Spotlight (esta sesión), un
caso macOS RICO (Safari exploit + bookmark exploit + FSEvents borrado masivo +
Spotlight anti-forense + LaunchAgent en /tmp) produce **3 dominios distintos**
(`browser_suspicious`, `antiforensic`, `persistence`) y el `to_signal()`
agregado alcanza **z=3.8** — por la rama cross-dominio `exploit & antiforensic`.
Esto CUANTIFICA D1: la Opción 1 (z por dominio ≤ techo individual) **bajaría ese
3.8** porque solo `browser` llega a >3 solo (exploit 3.5); `antiforensic` y
`persistence` standalone quedan en ~1.2. El split, sin recalibrar, cambiaría un
caso que hoy es INTENT/MALICE (z=3.8) a uno donde el reasoner recibe 3 primarias
pero ninguna crítica → probable SUSPICION. **Este es el trade-off exacto de D1,
ahora con número.** El fixture es el test de aceptación de B-052-P2 (§8.3).

**INFERENCIA (riesgo portante):** ninguna señal de un solo dominio puede
observar dos dominios a la vez. Splitear **destruye el tope de cada escalera**.
El único dominio que alcanza z>3 por sí solo hoy es `browser` (rama exploit
research, 3.5). Ningún dominio no-browser llega a >3 solo (SIP=2.4, root=2.0,
n_enc≥3=2.4). Consecuencia: tras el split, el gate MALICE ≥2 tipos críticos
**casi nunca abre** por vía mobile — haría falta que un segundo dominio cruce
>3, y hoy ninguno lo hace.

### 4.1 DECISIÓN DE DOCTRINA #1 — dónde vive la escalación cross-dominio
Dos opciones, mutuamente excluyentes; **requiere firma**:

- **Opción 1 (recomendada — conservadora):** las z por dominio quedan ≤ su techo
  de dominio único; la escalación cross-dominio se **relocaliza al reasoner**,
  que ahora recibe ≥3 primarias diversas y hace la coherencia/CCS cross-layer
  que la escalera device-wide atajaba. Doctrinalmente más limpio (el engine deja
  de pre-juzgar intención cross-dominio). Costo: MALICE por vía mobile se vuelve
  raro. **0 recalibración de umbrales**; los tests de pin device-level siguen
  verdes porque `to_signal()` no cambia (§5).
- **Opción 2 (recrea sensibilidad — recalibración real):** elevar techos de
  dominios individuales para que un acto deliberado cruce >3 solo (p.ej.
  antiforensic macOS: SIP + quarantine-vacío → 3.x). Recrea la sensibilidad
  vieja pero **es recalibración genuina**: mueve valores pineados y exige
  re-validación. Sin corpus que la valide (§0), la validación sería solo
  sintética + tuck-2019.

**Recomendación con evidencia:** Opción 1. La razón Daubert: sin corpus que
mida el efecto, subir techos (Opción 2) es "cambiar un comportamiento no
calibrado por otro no calibrado" (mismo argumento que difirió B-041b). La
Opción 1 desbloquea el gate ≥3 (el win barato y seguro) sin tocar umbrales.

### 4.2 DECISIÓN DE DOCTRINA #2 — `opsec_bump` por dominio
El `opsec_bump` device-wide cuenta `opsec_indicators` del dispositivo entero.
Al splitear, **aplicarlo solo al dominio dueño de cada indicador** (correcto),
NUNCA sumar el bump completo a cada dominio (multiplicaría la misma evidencia N
veces — exactamente el fallo "un artefacto disfrazado de N señales" que el
comentario F5 advierte, `abductive_reasoner.py:111-113`). Esto no es opcional;
es requisito de corrección.

### 4.3 Cómo computar cada z por dominio
Por dominio: `composite_score = noisy_or_correlated(severidades_del_dominio,
grupos, 15/100)` sobre **solo** las findings de ese dominio (comparten
corr_group → una clique). Luego z de una **sub-escalera booleana local** que
lee solo booleanos del dominio (p.ej. browser: `exploit→3.5`, `suspicious→1.8`,
`findings→1.2`). Se recomienda mantener la forma de sub-escalera booleana
(no `z = composite*escala`) porque los umbrales están calibrados a los cortes
>2/>3 del pipeline y los tests pinean valores exactos.

---

## 5. Superficie de compatibilidad — qué debe preservar `to_signal()`

`.to_signal()` sobre resultados mobile lo llaman directamente:
- **Shim raíz** `sift_orchestrator.py::_analyze_mobile` (497 Android, 537 iOS,
  567 Takeout, 597 macOS) — **el consumidor de producción a migrar**.
- `apply_b048.py:133` (script de wiring).
- `vigia/sift/sift_orchestrator.py:324` (`_to_signal_safe` genérico).
- **Tests que pinean z/confianza device-level** (deben seguir verdes salvo
  recalibración intencional): `test_mobile_pins_s2_ladder.py`,
  `test_b072_b074_mobile_verdict_fixes.py` (~20 asserts),
  `test_b042_b043_mobile_determinism.py`, `test_b066_b067_mobile_whitelist.py`,
  `test_b047_correlation_groups.py`.

**Recomendación (bajo riesgo):** **mantener `to_signal()` byte-idéntico**
(señal agregada, misma escalera, `artifact_type=*_forensic`) y **agregar**
`to_signals() -> List[SignalOutput]`. Migrar solo `_analyze_mobile` a consumir
`to_signals()`; `to_signal()` sigue sirviendo a `apply_b048.py`, el path
genérico, el override L-036 device-level y todos los pines. Preservar el guard
de precedencia B-048 (iOS suprimido si el directorio matchea markers macOS,
`_analyze_mobile:524-531`) **a nivel engine**, no por dominio — la superficie
compartida es justo el dominio `browser_suspicious`.

---

## 6. La capa del reasoner — el bloqueador oculto (OBSERVACIÓN)

Aunque el split dé N `artifact_type` distintos, el reasoner **no los mira para
la capa**: `_signals_to_artifacts` (`abductive_reasoner.py:191-220`) deriva la
capa de un `layer_map` **keyed por `tool_name`** (194-205) sin entradas mobile
→ todo cae a `DISK_MFT` (208). Y **todas las señales por dominio de un engine
comparten el mismo `tool_name`** (`MACOS_FORENSICS`) → splitear por
`artifact_type` NO cambia la capa. Dos fixes:

- **Opción A (recomendada, menos código):** que `_signals_to_artifacts` lea la
  capa de `metadata["artifact_type"]` vía el mismo `_LAYER_MAP` del adaptador,
  no de `tool_name`. Alinea el reasoner con `signal_to_abductive_record`
  (`forensic_adapter.py:199-200`) que ya lo hace así.
- **Opción B:** dar a cada dominio un `tool_name` distinto (`MACOS_BROWSER`…) y
  extender el `layer_map`. Más strings.

### 6.1 DECISIÓN DE DOCTRINA #3 — ¿capas distintas para dominios mobile?
`EvidenceLayer` es un enum **fijo de 4 miembros** (MEMORY 0.9 / NETWORK 0.8 /
REGISTRY 0.6 / DISK_MFT 0.4). Agregar un miembro es invasivo (toca
`LAYER_EPISTEMIC_WEIGHT`, `INVERSION_TIER_1_LAYERS`, el stub de
forensic_adapter). Reusar los 4 existentes para dar diversidad
(`persistence/root/antiforensic`→REGISTRY, `location`→NETWORK) **infla el peso
epistémico** por encima del 0.4 que la evidencia D3-spoofable honestamente
merece (todos ~0.55 de spoofability en `EVIDENCE_PROFILES`).

**Recomendación con evidencia:** para desbloquear SOLO los dos gates (≥3
primarias + ≥2 tipos críticos), **mantener TODOS los dominios en DISK_MFT**
(peso honesto 0.4): el gate ≥3 se satisface por CONTEO (no requiere diversidad
de capa) y el gate MALICE por `artifact_type` distintos. **0 recalibración de
pesos.** Solo si la inversión cross-layer para mobile fuera un objetivo
explícito, introducir un miembro `MOBILE_*` con peso ~0.4 (distinto para
identidad, no para peso). La diversidad forzada NETWORK/REGISTRY es un falso
positivo epistémico y se desaconseja.

---

## 7. Checklist de edición (para la sesión de implementación)

1. Agregar `to_signals()` a los 4 `*AnalysisResult`; `to_signal()` byte-idéntico.
2. Por dominio: `composite_score` local vía `noisy_or_correlated`; sub-escalera
   z booleana local; `opsec_bump` solo al dominio dueño (§4.2 — corrección, no
   opción).
3. Alta de `artifact_type` (o `evidence_type` canónico directo) en
   `forensic_adapter._LAYER_MAP`/`_EVIDENCE_MAP`/`_ONTOLOGY_MAP`.
4. Migrar `_analyze_mobile` a iterar `to_signals()`; preservar el guard B-048 a
   nivel engine.
5. Reasoner: `_signals_to_artifacts` keyed por `artifact_type` (Opción A) si se
   quiere capa; si no, dejar DISK_MFT (recomendado §6.1).
6. Fijar postura de recalibración (§4.1) y re-pinear
   `test_mobile_pins_s2_ladder.py`/`test_b072_b074_mobile_verdict_fixes.py`.

---

## 8. Estrategia de validación (dado que el corpus no puede)

El gate comparativo de 199 casos es **necesario pero vacuo** (0 casos rutean a
mobile). La validación real, en orden:

1. **Regresión pin:** `to_signal()` byte-idéntico → toda la pin-suite mobile
   verde SIN cambios (prueba que el split no tocó la señal agregada).
2. **tuck-2019-macos:** medir before/after. Predicción (OBSERVACIÓN §0.3): sigue
   ABSTAIN (1 dominio) — el split NO lo cambia. Documentarlo como esperado.
3. **Casos sintéticos multi-dominio (YA CONSTRUIDO para macOS):**
   `tests/test_macos_multidomain_integration.py` compone Safari+FSEvents+
   Spotlight+persistencia → 3 dominios, z agregado 3.8. Es el test de
   aceptación listo para B-052-P2. Falta el equivalente para iOS/Android.
   Construir fixtures mobile con ≥3
   corr_groups poblados (p.ej. macOS con browser + antiforensic + persistence)
   y verificar: (a) `to_signals()` emite N señales, (b) el reasoner corre
   (no `NOT_RUN_MOBILE_SINGLE_SOURCE`), (c) el veredicto sube de ABSTAIN a
   INTENT/SUSPICION según la postura §4.1. Estos fixtures son la ÚNICA prueba
   positiva del cambio y deben acompañar el PR.
4. **Gate comparativo 199:** correr igual, para probar la NO-regresión (0 flips
   esperado, y si algo flipea es un bug — el corpus no debería tocar el código).

---

## 9. Decisiones que requieren firma antes de implementar

| # | Decisión | Recomendación | Mueve veredictos |
|---|---|---|---|
| D1 (§4.1) | Escalación cross-dominio: reasoner (op.1) vs techos individuales (op.2) | Opción 1 | Op.2 sí; Op.1 no |
| D2 (§4.2) | opsec_bump por dominio dueño | Obligatorio (corrección) | Evita inflación |
| D3 (§6.1) | Capas mobile: DISK_MFT único vs diversidad forzada vs miembro nuevo | DISK_MFT único | Diversidad sí |
| D4 (§0) | ¿B-052-P2 solo, o acoplado a la expansión de módulos macOS? | Acoplado (tuck-2019 necesita más dominios) | — |

**Postura recomendada global (la más defendible sin corpus):** Opción 1 + opsec
por dominio + DISK_MFT único. Es **desbloqueo estructural puro** (gate ≥3 +
gate MALICE por tipos) con **cero recalibración de umbrales o pesos**, inerte
sobre el corpus, y honesto sobre su límite: no "arregla" tuck-2019 (necesita
más parsers), solo remueve el bypass arquitectónico
`NOT_RUN_MOBILE_SINGLE_SOURCE` para casos que sí tengan ≥3 dominios poblados.

---

## 10. DECISIÓN FINAL §9.4 — SELLADA POR EL COLECTIVO + FIRMA DE ANNA (2026-07-10)

> **Opción (ii) pura, adoptada:**
> - SUSPICION es el techo honesto para casos macOS/mobile D3-only.
> - NO se implementa split por dominios lógicos (B-052-P2 original).
> - NO se adopta densidad causal (descartado por experimento, r=0.9185).
> - Queda documentado como **§9.4-LIM**: límite estructural conocido.

Consecuencia sobre las decisiones de §9: D1–D4 quedan **cerradas por
superación** — el split no se adopta, así que no hay opción que firmar. La
rama `claude/b052-p2-domain-signals-xk5ecq` (implementación del split,
`c5c8d38`) queda como **registro histórico — NO MERGEAR**.

### 10.1 §9.4-LIM — límite estructural conocido

Un caso cuyo canal físico de evidencia es únicamente D3 (filesystem local: el
dispositivo mismo) no puede escalar más allá de SUSPICION por doctrina:
todos sus dominios lógicos comparten el mismo canal de fabricación, así que
la multiplicidad de dominios D3 no constituye corroboración independiente.
**Criterio de cierre del límite:** engines de canal D2/D4 para evidencia
mobile (memoria/red del dispositivo), o validación con corpus real ≥50 casos
macOS/mobile etiquetados.

**Discrepancia observada (medida 2026-07-10, pre-extensión) — RESUELTA:** el
pipeline de la ruta mobile-only sellaba **INTENT** para el fixture D3-rico
(`_mobile_hypothesis` F6: max_z=3.8 → INTENT_DETECTED, is_conclusive=True →
`classify_agent_verdict` → INTENT con n_primary=1) — el techo SUSPICION de
la doctrina (ii) no estaba enforced en el camino del veredicto.

**ENFORCEMENT (firmado y aplicado 2026-07-10 "mañana"):**
- Hallazgo de la investigación: `classify_agent_verdict` tenía un espacio de
  4 veredictos y colapsaba `"SUSPICION" in hyp → INTENT` — capear la
  *hipótesis* (sketch original) habría sido inerte. El cambio mínimo real:
  introducir el veredicto sellado **SUSPICION** (5º de la escala documentada
  en CLAUDE.md) vía un mecanismo genérico de techo.
- Implementación: cuando cond2 (§10.2) se cumple y la hipótesis es
  INTENT/MALICIOUS, el shim declara `abduction.verdict_ceiling="SUSPICION"`
  (+ razón + REFUTATION GATE LOG en narrativa +
  `pipeline_meta.s94_lim_enforced`). `classify_agent_verdict` aplica el
  techo pre-emisión: MALICE/INTENT → SUSPICION; **nunca eleva** ABSTAIN/
  NOISE; campo ausente o valor desconocido → byte-idéntico (fail-safe).
  La hipótesis cruda del engine NO se falsea.
- Alerting preservado: `_VERDICT_EXIT["SUSPICION"] = EXIT_INTENT` (contrato
  documentado "3=intent/suspicion"; sin entrada explícita caería al fallback
  EXIT_ABSTAIN) y el piso de alerta B-065 de INTENT se extiende a SUSPICION.
- Gate comparativo (el más sensible de la sesión): **0 flips en 291
  bundles; corpus 167/199 idéntico en ambos mundos; output del runner
  byte-idéntico salvo timing** (el ceiling solo se declara en la ruta
  mobile-only, que 0 casos del corpus ejercitan). Fixture D3-rico:
  INTENT → **SUSPICION** (el cambio buscado). vpn-solo y débil-multi:
  sin cambio (ABSTAIN).
- Observación registrada (fuera de alcance): ~10 fallos pre-existentes del
  corpus son `agent=INTENT exp=SUSPICION` del path motor — el colapso
  SUSPICION→INTENT de classify les cuesta accuracy. El nuevo veredicto
  SUSPICION abre la puerta a recuperarlos (dejar que el motor SUSPICION
  selle SUSPICION), pero eso mueve ~10 veredictos reales y es una decisión
  doctrinal separada que requiere firma.

### 10.2 Extensión aprobada — dos clases de SUSPICION en el output

Detección (implementada en el shim `sift_orchestrator.py`,
`_mobile_suspicion_class` — narrativa + `pipeline_meta`, cero cambio de
score/veredicto):

```
cond2 := ruta mobile-only (reasoner NOT_RUN_MOBILE_SINGLE_SOURCE)
         AND >=1 señal analizada (los marcadores unanalyzed no cuentan)
         AND TODAS las señales analizadas resuelven dominio D3
             (evidence_type|artifact_type → _EVIDENCE_MAP → _DOMAIN_MAP)
         AND max_z > 3          (umbral crítico pre-existente, Fraction)
         AND n_finding_types_distintos >= 2 (unión de metadata.finding_types)

cond2  → pipeline_meta.suspicion_class = "D3_RICH_NO_TRIANGULATION"
         + nota doctrinal en narrativa (texto exacto de la decisión)
!cond2 → pipeline_meta.suspicion_class = "GENERIC" (sin texto adicional)
```

Notas de diseño:
- Umbral `> 3` estricto: reutiliza el umbral crítico pre-existente
  (`_mobile_hypothesis` is_conclusive y tipos críticos del reasoner) — cero
  umbrales nuevos.
- `breadth_tactics >= 2` se consideró y se descartó por ahora: las señales
  mobile no llevan táctica MITRE en metadata (el mapeo MITRE ocurre aguas
  abajo); `finding_types >= 2` es el proxy disponible hoy.
- **Fail-closed:** dominio no resoluble, mapas no importables, o cualquier
  señal fuera de D3 → GENERIC (la nota solo aparece cuando el confinamiento
  D3 es *probado*).
- 12 tests en `tests/test_s94_lim_suspicion_class.py` (E2E con fixtures +
  unidad de la regla + pin de invariancia de veredicto).

### 10.3 Anexo — registro de la inquiry (evidencia de proceso adversarial)

1. **Experimento de discriminación** (regla pre-registrada, fail-closed):
   r(densidad_causal_D3, z_agregado_D3) = **0.9185** sobre 6 fixtures → zona
   gris [0.70, 0.95] → NOT ADOPTED por default. Detalle completo por fixture
   en §9.4.1 del design doc de la rama `claude/b052-p2-domain-signals-xk5ecq`
   (commit `a74d360`); script reproducible en
   `scripts/experiments/b052_discriminacion.py` (misma rama).
2. **Decisión sellada** (verbatim arriba, §10) — transmitida por Anna
   2026-07-10 tras 3 rondas de debate del colectivo.
3. **Registro completo de las 3 rondas del colectivo:** NO disponible en la
   sesión que produjo este documento — el agente no lo recibió y no lo
   fabrica. **[PENDIENTE: Anna pega aquí el registro completo]**. Hasta
   entonces, la evidencia de proceso adversarial disponible es (1) + (2) +
   la regla pre-registrada aplicada sin excepción.

---

## Apéndice A — finding_type → corr_group (verbatim, con líneas)

**macOS** (`macos_forensics.py`): `antiforensic` = SIP_DISABLED(527,551),
ANTIFORENSIC_SEARCH(641), ANTIFORENSIC_QUARANTINE_EMPTY(759),
OPSEC_ANTIFORENSIC_POSTURE(1017); `browser_suspicious` =
SAFARI_SUSPICIOUS/SAFARI_EXPLOIT_RESEARCH(622); `quarantine_suspicious` =
QUARANTINE_CLI_DOWNLOAD(728), QUARANTINE_SUSPICIOUS_SOURCE(742); `persistence` =
PERSISTENCE_SUSPICIOUS_LAUNCHAGENT(916), PERSISTENCE_RESILIENT_LAUNCHAGENT(934),
PERSISTENCE_HIDDEN_LOGIN_ITEM(975); `encrypted_apps` = TOR_BROWSER_DETECTED(808),
OPSEC_MULTI_ENCRYPTED_APPS(996).

**iOS** (`ios_forensics.py`): `sms_phishing` = SMS_PHISHING_RECEIVED(427);
`encrypted_apps` = SMS_ENCRYPTED_RECRUITMENT(442), PSIPHON_TUNNELING_DETECTED(656),
OPSEC_MULTI_ENCRYPTED_APPS(736); `data_minimization` = EMPTY_CONTACTS(496),
EMPTY_CALL_HISTORY(530), OPSEC_DATA_MINIMIZATION(753); `browser_suspicious` =
SAFARI_SUSPICIOUS/SAFARI_EXPLOIT_RESEARCH(589); `credential_patterns` =
CREDENTIAL_REUSE_PATTERN(688), WEAK_PASSCODE(712).

**Android** (`android_forensics.py`): `root` = DEVICE_ROOTED(386,401,655),
OPSEC_ROOT_PLUS_ENCRYPTED(761); `encrypted_apps` = SMS_ENCRYPTED_RECRUITMENT(448),
OPSEC_MULTI_ENCRYPTED_APPS(738); `data_minimization` = EMPTY_CONTACTS(496),
EMPTY_CALL_LOG(533), OPSEC_DATA_MINIMIZATION(749); `browser_suspicious` =
BROWSER_SUSPICIOUS/BROWSER_EXPLOIT_RESEARCH(584), BROWSER_EXPLOIT_BOOKMARKED(613).

**Google Takeout** (`google_takeout_forensics.py`): `location_gaps` =
LOCATION_HISTORY_GAP(475); `browser_suspicious` =
BROWSER_EXPLOIT_RESEARCH/BROWSER_SUSPICIOUS(596); `suspicious_apps` =
SUSPICIOUS_INSTALLED_APP/ROOT_TOOL_INSTALLED(668), OPSEC_ROOT_TOOLCHAIN(706).

---

## Apéndice B — medición tuck-2019-macos (OBSERVACIÓN verbatim 2026-07-10)

Señal agregada actual: `findings=23`, `by corr_group=Counter({browser_suspicious:23})`,
`by finding_type=Counter({SAFARI_SUSPICIOUS:23})`, `composite_score=19/20`,
`SIGNAL z=1.6 value=0.32 conf=0.95 artifact_type=macos_forensic`.

Mode 1 hoy: `agent_verdict=ABSTAIN` (exit 4), `abductive_reasoner=
NOT_RUN_MOBILE_SINGLE_SOURCE`, `source=mobile_forensics_adapter`,
`n_primary=1`. Bundle sellado (modo MCP, no Mode 1):
`overall_verdict=INTENT/HIGH`. La divergencia ABSTAIN(automático)/INTENT(MCP) es
el síntoma que B-052-P2 + más parsers apunta a cerrar — pero NO con el split
solo (1 dominio).

---

*VIGÍA — B-052-P2 design | 2026-07-10 | cero código de producto tocado.*
