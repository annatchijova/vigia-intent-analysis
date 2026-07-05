# Auditoría abductiva — cobertura de tests de los módulos SIFT mobile

**Fecha:** 2026-07-04
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Alcance:** `vigia/sift/ios_forensics.py`, `android_forensics.py`, `macos_forensics.py`.
**Método:** protocolo peirciano (Firstness → Secondness → Thirdness + Refutación
de Eco) sobre cobertura **medida** (pytest-cov), mapeo per-módulo + análisis
sistémico cross-módulo por un workflow de 43 subagentes, verificación
adversarial de cada hallazgo, y confirmación empírica propia de las
afirmaciones sistémicas. **Solo documentación — ningún test implementado.**

---

## Resumen ejecutivo

Los tres módulos mobile están cubiertos al **~15 %** mientras sus hermanos SIFT
del mismo dominio superan el 77 %. El 85 % sin cubrir **no es aleatorio**: es
exactamente la superficie de mayor riesgo forense — el canal de veredicto
(`to_signal`), la frontera de determinismo (conversores de timestamp) y la
frontera de evidencia hostil (`_safe_sqlite_connect`/`_safe_plist_load`/
`_safe_rglob`). La auditoría **ya encontró defectos latentes** en esa zona sin
test: ramas de veredicto muertas (`has_sip_disabled` siempre False; `has_phishing`
nunca usado) y una frontera de seguridad que no protege (`sqlite3.connect` es
lazy — una DB malformada la atraviesa). La cobertura del 15 % no es el hallazgo;
es el síntoma. El hallazgo es **qué** 85 % falta y **por qué**.

---

## FIRSTNESS — qué observo (medición, sin interpretar)

Cobertura medida (`pytest-cov`, suite completa `tests/` + `vigia/tests/`):

| Módulo | Cobertura | Stmts sin cubrir | Branches |
|--------|-----------|------------------|----------|
| `ios_forensics.py` | **15.63 %** | 255 / 323 | 112, 0 parciales |
| `android_forensics.py` | **14.69 %** | 290 / 362 | 128, 0 parciales |
| `macos_forensics.py` | **15.11 %** | 265 / 336 | 134, 0 parciales |

`0 branches parciales` = de las ~370 ramas de los tres módulos, **ninguna** es
ejercitada a medias: o se testea entera (casi ninguna) o nunca. El único método
con cobertura real es `_build_correlation_groups` (+ las dataclasses e imports),
por el test de regresión `test_b047_correlation_groups.py`. Los **48 métodos
restantes** — todo `to_signal`, todo `analyze`, todos los `_analyze_*`,
`_detect_*`, `_assess_opsec`, los `_safe_*` y los conversores de timestamp —
figuran en la columna *Missing*.

Hechos empíricos verificados (no inferidos):

1. **`sqlite3.connect()` es lazy.** Sobre una DB con cabecera `SQLite format 3\0`
   válida y cuerpo basura, `connect()` **abre sin error**; el `DatabaseError`
   surge en el primer `SELECT` — **fuera** del `try/except` de
   `_safe_sqlite_connect`. El wrapper "safe" no captura evidencia malformada.
2. **`connect()` a un path inexistente crea una DB vacía** en disco (comportamiento
   default de SQLite).
3. **`has_sip_disabled` (macOS) es siempre False.** El literal `"SIP_DISABLED"`
   aparece **solo** en `macos_forensics.py:152` (donde se lee); ningún analyzer
   lo emite como `finding_type`.
4. **`has_phishing` (iOS) se computa (`:127`) y nunca se usa** en la escalera z.

---

## SECONDNESS — anomalía estructural contra la línea base

**Contra los hermanos del mismo dominio** (módulos SIFT, misma clase de código —
parsers de artefactos forenses):

| Módulo SIFT | Cobertura |
|-------------|-----------|
| `browser_forensics.py` | 89.14 % |
| `disk_forensics.py` | 77.39 % |
| `memory_forensics.py` | 32.04 % |
| **`ios_forensics.py`** | **15.63 %** |
| **`macos_forensics.py`** | **15.11 %** |
| **`android_forensics.py`** | **14.69 %** |
| `google_takeout_forensics.py` | 15.12 % (mobile-adyacente) |

No es cobertura baja generalizada del repo: es un **clúster mobile** en ~15 %
mientras el browser forensics del mismo autor y estilo está al 89 %. La
desviación es específica de la familia mobile+takeout.

**Contra lo que "cobertura adecuada" significa para este código:** el `z_score`
de `to_signal` es el **canal de veredicto** — `sift_orchestrator._mobile_hypothesis`
(`:102-113`) lo mapea con desigualdad **estricta**: `≥2 señales z>3 → MALICIOUS_INTENT`,
`max_z>3 → INTENT`, `max_z>2 → SUSPICION`. La escalera `to_signal` de iOS tiene
**11 ramas** con umbrales `Fraction` (3.5 … 1.2) más un `opsec_bump` de ±0.4.
Cada umbral es la línea entre veredictos que van a un tribunal. **Cero de esas
ramas tiene un test que la fije.** Cambiar `Fraction(30,10)` a `Fraction(31,10)`,
o el corte de severidad 80/100 que alimenta `has_exploit_research`, mueve el
veredicto en silencio y ninguna prueba se rompe.

El contraste más agudo: el **único** método testeado
(`_build_correlation_groups`) fue cubierto porque **causó un bug** (B-047,
type mismatch `List[List[int]]` vs `Dict[int,Set]`). Se testeó lo que ya había
roto; el canal de veredicto, que nunca "rompió" de forma visible, nunca se testeó.

---

## THIRDNESS — la ley que explica el hueco

**Por qué estos módulos, y por qué esta superficie.** Historial de bugs de esta
misma familia: `B-045` (Android/iOS "nunca invocados"), `B-046` (Takeout "nunca
invocado"), `B-048` (macOS "nunca invocado"). Los cuatro se **cablearon** en esta
campaña — pasaron de *código muerto* a *ejecutable*. Pero **"make it run" ≠ "make
it verifiable"**: la deuda de verificación se concentra exactamente donde los
motores se atornillaron tarde. Es el mismo patrón que ya surfaceó
`AUDITORIA_MOBILE_WHITELIST` (los tipos mobile existían pero sin perfil).

**La ley más profunda — el hueco no es aleatorio.** Un módulo puede estar al
15 % de dos maneras: (a) le falta el 85 % *cosmético* (logging, getters), o (b)
le falta el 85 % *crítico*. Aquí es (b): las tres superficies de mayor apuesta de
un motor forense —

1. **el canal de veredicto** (`to_signal`): produce el número que decide MALICE,
2. **la frontera de determinismo** (conversores de timestamp): el invariante
   Daubert de reproducibilidad cross-arquitectura,
3. **la frontera de evidencia hostil** (`_safe_*`): parsea una SQLite/plist de un
   teléfono incautado, controlada por el atacante,

— son precisamente las tres **menos** testeadas. La cobertura del 15 % es un
proxy; la ley es que la verificación ausente coincide con el riesgo máximo. Y ya
produjo defectos latentes (ver ramas muertas abajo) que sobreviven **porque**
nadie ejercita la escalera.

---

## REFUTACIÓN (razor de Eco) — ¿la cobertura real es mayor vía integración?

Hipótesis benigna a refutar: *"el 15 % es artefacto de medición; los módulos se
ejercitan indirectamente por el corpus / la integración."* Refutada en tres ejes:

1. **El corpus (198 casos) no contiene imágenes de disco mobile reales.** Estos
   motores solo corren sobre un filesystem de dispositivo real (`sms.db`,
   `contacts2.db`, `History.db`, plists de LaunchAgents). El corpus son casos
   EBS-JSON, no volcados de teléfono.
2. **El único test que toca los 3** (`test_b047_correlation_groups.py`)
   **inyecta `_findings` a mano** y llama solo `_build_correlation_groups()`;
   nunca invoca `.analyze()`, `to_signal()`, ni un `_analyze_*`.
3. **El único call-site de producción** (`sift_orchestrator.py:376` etc.)
   instancia los analyzers **solo en runtime**, en ningún test. No hay e2e que
   plante una `mmssms.db` y corra `.analyze()`.

No hay cobertura indirecta. El 15 % es real. **Verdict: la anomalía se sostiene.**

---

## Hallazgos verificados — paths críticos sin test

Mapa: 42 paths (30 CRITICAL / 9 HIGH / 3 MEDIUM). Verificación adversarial:
**16 CONFIRMED, 14 DOWNGRADED** (la mayoría a "untested pero no crítico" — la
verificación hizo su trabajo). macOS: 9 verificaciones no completaron (límite de
sesión del workflow); se cubren por los patrones sistémicos + lectura directa +
confirmación empírica propia.

### A. Canal de veredicto — `to_signal` (CRITICAL, confirmado iOS/Android)

La escalera z sin un solo test. Dos **defectos latentes ya presentes** en la
zona sin cubrir, verificados empíricamente:

- **macOS: ramas de veredicto MUERTAS.** `has_sip_disabled` (`:151-153`) lee un
  `finding_type "SIP_DISABLED"` que **ningún analyzer emite** → siempre False →
  las ramas `z=3.4` (`:167`) y `z=2.4` (`:175`) son **inalcanzables**. Un macOS
  con SIP deshabilitado + anti-forense **nunca** recibe la escalación codificada
  para ese escenario. Un test que fijara la escalera lo habría cazado.
- **iOS: flag muerto.** `has_phishing` (`:127`) se computa desde
  `SMS_PHISHING` y **nunca** entra al ladder → un caso de phishing puro cae al
  piso `z=1.2`. La detección existe pero no mueve el veredicto.
- **Interacción `opsec_bump` no fijada:** `n_encrypted=3 + contactos=0 + llamadas=0`
  cae en `z=3.0`; `_assess_opsec` suma 3 indicadores → `+0.4` → `z=3.4` → en
  `_mobile_hypothesis` (estricto `>3`) esto **cruza SUSPICION→INTENT**. Ninguna
  prueba fija ese cruce.

### B. Frontera de determinismo — conversores de timestamp (HIGH, confirmado los 3)

`_coredata_to_unix` (iOS/macOS), `_chrome_ts_to_unix` (Android), `_cocoa_ts_to_unix`
(macOS): bucketing heurístico por magnitud (umbrales `1e17/1e14/1e11` en macOS,
`1e15/1e12/1e10` en Android — **distintos entre módulos**) para adivinar
nanos/micros/millis/segundos, más colapso `ts≤0 → 0`. Cero tests.

- **Riesgo confirmado:** un `visit_time` cuya magnitud roza un borde de banda se
  divide por el factor equivocado → epoch off por ~1000× (décadas) → **timeline
  forense corrompido** en cada finding de Safari. Los bordes no están fijados.
- **Aclaración honesta (matiz que mi verificación bajó):** `_chrome_ts_to_unix`
  usa **división float** (`int(ts/1_000_000)`) donde el invariante CLAUDE.md pide
  entero/`Fraction`. Es un **smell** de determinismo (float en un conversor), pero
  **no logré producir divergencia** vs `//` en magnitudes de timestamp reales
  (los floats de Python son exactos hasta 2⁵³). Se reporta como riesgo latente de
  invariante, **no** como divergencia demostrada — a diferencia de las bandas, que
  sí son un error alcanzable.

### C. Frontera de evidencia hostil — `_safe_*` (CRITICAL sistémico, confirmado)

- **`_safe_sqlite_connect` no protege** (verificado empíricamente): `connect()` es
  lazy; una DB atacante con header válido la atraviesa y el error surge en el
  `SELECT`, fuera del `try`. Además abre **read-write** sin `mode=ro&immutable=1`
  → una DB con journal/WAL sucio dispara auto-recovery que **escribe** `-wal`/
  `-journal` de vuelta en `VIGIA_EVIDENCE_DIR` → **viola el invariante de
  evidencia read-only** y rompe la cadena de custodia. Y a path inexistente crea
  una DB vacía → 0 hallazgos → lee "limpio".
- **`_safe_rglob` bypasseado:** aplica `[:limit]` pero **materializa y ordena
  `base.rglob(pattern)` entero antes** del slice → el límite no protege del OOM.
  Peor: la mayoría de call-sites (validación de marcadores con `rglob('*')`,
  `_detect_root` con `rglob('*magisk*')`) llaman `Path.rglob` **directo, sin
  `_safe_rglob`** → walk no acotado + descenso por directorios symlinkeados.
- **`_safe_plist_load` (macOS):** captura `Exception` genérico y loguea a DEBUG
  (silencioso); sin límite de tamaño → un plist malformado o bomba de expansión →
  `None` → "sin persistencia" (lee limpio).

### D. Detección → veredicto — conflación "no-parseable == vacío" (CRITICAL, confirmado)

Patrón repetido en `_analyze_contacts`/`_analyze_call_history`/`_analyze_call_log`
(iOS/Android): si la tabla esperada no existe (`ABPerson`, `ZCALLRECORD`,
`calls`), el `OperationalError` se traga y el contador queda en su **default 0**
→ se emite `EMPTY_CONTACTS`/`EMPTY_CALL_HISTORY` → alimenta `data_minimization`
→ escala el veredicto. **Un fallo de parseo inocente se puntúa idéntico a una
agenda deliberadamente borrada** → falso INTENT/MALICE. Es la familia P0-A del
proyecto ("incapacidad de análisis presentada como señal"), sin test.

### E. Orquestación — `analyze()` (DOWNGRADED a no-crítico, pero confirmado sin test)

- iOS: `_detect_installed_apps` (`:286`) y `_assess_opsec` (`:305`) se invocan
  **sin** el `try/except` que sí protege a SMS/contacts/calls/safari → una excepción
  ahí **aborta el caso entero** sin bundle sellado, mientras un error de SMS se
  habría degradado a `analysis_notes`. Contención de errores asimétrica, sin test.
- El manejo de errores es **por-artefacto** (outer try en `analyze()`), no
  **por-fila**: un `int(row['date'] or 0)` sin guardia en un loop de parsing
  (`_analyze_sms:421`) sobre una columna atacante `date='abc'` tira `ValueError`
  → cae al except externo → **dropea el artefacto completo** (falso negativo),
  no solo la fila.

---

## Patrones sistémicos (el mismo defecto latente en los 3 a la vez)

| # | Patrón | Módulos | Criticidad |
|---|--------|---------|------------|
| S1 | `_safe_sqlite_connect` idéntico: error handling solo en connect (lazy) + sin `mode=ro` → DB malformada escapa + escritura en evidencia | ios/android/macos | **CRITICAL** |
| S2 | `to_signal`: la escalera referencia flags/`finding_types` que el módulo nunca emite → ramas muertas justo en el borde z>3/z>2 | ios/android/macos | **CRITICAL** |
| S3 | Conversores de timestamp: contaminación float (android) + bucketing por magnitud + colapso `ts≤0→0`, sin test → smell de invariante de determinismo | android/ios/macos | HIGH |
| S4 | `rglob` sin cota: el `limit` de `_safe_rglob` se bypassa en la validación de marcadores y en detección de apps/root | ios/android/macos | HIGH |
| S5 | Contención de errores por-artefacto (no por-fila) + `int()`/`float()` sin guardia en loops sobre columnas atacantes → drop silencioso del artefacto (falso negativo) | android/ios/macos | HIGH |

Que sean **sistémicos** multiplica el costo: un solo test de contrato compartido
(ej. "todo `finding_type` referenciado en `to_signal` debe ser emitido por algún
`_analyze_*`", o "`_safe_sqlite_connect` sobre DB malformada no debe propagar al
query") cerraría la clase entera en los tres módulos — el mismo tipo de "test de
contrato" que cerró B-060 en `test_b066`.

---

## Dónde apuntar primero (si se decide implementar — fuera de este alcance)

Prioridad por apuesta forense, no por facilidad:

1. **`to_signal` — pin de la escalera completa** (los 3). Fija cada umbral y el
   `opsec_bump`, y **caza las ramas muertas** S2 (has_sip_disabled/has_phishing).
   Es el canal de veredicto: máximo retorno.
2. **`_safe_sqlite_connect` — test de contrato S1**: DB malformada no propaga al
   query; apertura `mode=ro`; path inexistente no crea archivo. Cierra la
   frontera de seguridad en los 3.
3. **Conflación no-parseable==vacío (D)**: un test por módulo con una DB de schema
   desconocido debe **ABSTENER**, no emitir `EMPTY_*`.
4. **Conversores de timestamp — bordes de banda (S3)** y **rglob acotado (S4)**.

---

## Metodología y reproducibilidad

- Cobertura: `pytest --cov=vigia.sift.{ios,android,macos}_forensics --cov-report=term-missing`.
- Mapeo + verificación: workflow de 43 subagentes (34 completados, 9 fallidos por
  límite de sesión — todos en la fase de verificación de macOS, cubierta por los
  patrones sistémicos + lectura directa). Map completo para los 3 módulos;
  verify 16 CONFIRMED / 14 DOWNGRADED.
- Confirmaciones empíricas propias (independientes de los agentes): lazy-connect
  sobre DB malformada, creación de DB en path inexistente, `has_sip_disabled`
  siempre False (grep de emisión de `SIP_DISABLED`), `has_phishing` sin uso en el
  ladder, no-divergencia de la división float en magnitudes reales.
- **Ningún archivo de código ni de test modificado.** Solo este documento.
