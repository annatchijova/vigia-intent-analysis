# FOSSIL HUNT — Barrido sistemático de razonamiento pre-Daubert (2026-07-11)

**Tipo:** cacería y diagnóstico. **NO contiene fixes.** Ninguna decisión de remediación
está tomada en este documento — cada fósil se decide caso por caso, como B-114.

**Restore tag:** `restore-fossil-hunt-20260711` (creado antes de iniciar el barrido).

**Disparador:** el hallazgo VIGIA-MAGNET-2020-WINDOWS durante B-114 — un veredicto
MALICE sostenido por fracturas TCV que comparaban claves de registro de instalación
(2020-02-14) contra el snapshot de memoria (2020-04-20) y contra la política de
auditoría default del SO (LastWrite 2009-07-14, gap de 11 años), mientras las notes
del propio caso declaran "No external compromise detected... Memory analysis confirms
all legitimate processes and network connections".

**Pregunta del barrido:** ¿cuántos otros veredictos del corpus se sostienen por
fracturas o boosts que un cross-examination real destruiría en 30 segundos?

---

## 1. Metodología

Barrido determinístico sobre el motor real (`_vigia_score`), no lectura humana del JSON:

1. **Corpus:** los 199 casos de `find_cases(CASES_DIRS)` (`run_all_agent.py`:
   `data/cases` + `converted` + `benign` + `consolidated_canonical` + `legacy`,
   dedup por stem). 198 evaluados (VIGIA_BREAK_001-010.json es una lista de 10
   sub-casos, fuera del contrato de `_vigia_score`; sus variantes individuales
   VIGIA-BREAK-011..016 sí están en el corpus).
2. **Baseline:** `_vigia_score(case)` con CAIE vivo → veredicto, score,
   `caie_fracture_details`.
3. **Ablación por instancia:** monkeypatch quirúrgico sobre
   `CrossArtifactIncongruenceEngine.detect_fractures` que remueve UNA fractura
   (clave `tipo+artifact_a+artifact_b`) y re-puntúa. El resto del pipeline queda
   intacto — es el equivalente del harness scorer_gate en modo `--filter`.
4. **Ablación por tipo:** ídem removiendo TODAS las fracturas de un tipo (necesario
   porque un caso con 2+ TCVs no cae removiendo una sola — exactamente el caso
   MAGNET-2020, con 4).
5. **Ablación de `temporal_violations`:** las violations vienen pre-computadas del
   JSON del caso (no se recalculan); se ablacionan removiéndolas de una copia del
   caso.
6. **Criterio de candidato:** el veredicto **cae de categoría** al remover la
   fractura/violación (MALICE→SUSPICION, SUSPICION→NOISE, etc.).
7. Para cada candidato: verificación manual del sentido forense de la comparación
   (qué par de artefactos disparó la regla y por qué), búsqueda de contradicción en
   `notes`/`audit_note`/`devil_advocate`/`peirce_chain`, y datación (git + metadata
   interna `_consolidation`; el historial git arranca en el import squasheado del
   2026-07-05, así que la datación fina es por metadata interna y por los comentarios
   fechados de las reglas).

Distribución de fracturas disparadas en el corpus (199 casos): TCV 34 instancias,
FALSE_FLAG_PATTERN 22, FALSE_FLAG_ATTRIBUTION_MISMATCH 2, NARRATIVE_POISONING 1,
CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED 1, TIMESTAMP_PRECISION_ANOMALY 1,
USN_JOURNAL_GAP 1.

**Resultado global: 29 casos cuyo veredicto depende de una sola familia de
señal (28 por fractura CAIE, 1 por temporal_violation).** De ellos, 28 son fósiles
(8 confirmados + 20 semánticos) y 1 se descarta tras revisión (case_002,
STATISTICAL_UNIFORMITY legítima).

---

## 2. Los dos mecanismos fósiles

Los 26 fósiles se explican por **dos reglas**, ambas anteriores a la disciplina
Daubert (los gates B-068/R4-3/R3-1 son de fines de junio–julio; estas reglas
conservan lógica de mayo 2026 o anterior, retenida como "compatibilidad backward").

### M1 — TCV: filtro "network" por substring + timestamps heterogéneos
`vigia/tools/caie.py`, Rule 6 (~líneas 1472–1611).

Tres defectos compuestos:

1. **Clasificación por substring en texto libre** (`caie.py:1476-1479`): un artefacto
   es "actividad de red" si su descripción contiene `network`, `red`, `conexión` o
   `conexion`. `"red" in desc.lower()` matchea registe**red**, flicke**red**,
   unanswe**red**, c**red**entials, sto**red**, measu**red**, hund**red**… En el
   barrido, 5 de los 6 casos
   TCV-dependientes dispararon por esta vía. El propio comentario del código (fix
   2026-05-18) reconoce que el filtro por texto libre "no es reproducible" bajo
   Daubert — pero lo retiene por compatibilidad.
2. **Fallback al `timestamp` genérico del artefacto** (`caie.py:1582,1588`): si no hay
   `network_log_time` / `process_creation_time` en metadata, la regla compara
   `artifact.timestamp` — que para un `memory_process` es la hora del **snapshot de
   adquisición**, y para una `registry_key` la hora de **instalación**. Comparar
   instalación vs adquisición es el fósil MAGNET-2020 textual.
3. **Default `_utcnow()`** (`caie.py:724`): un artefacto sin timestamp recibe la hora
   de scoring. Dos artefactos sin timestamp quedan separados por el skew de creación
   de objetos (~2 ms) y pueden fabricar una TCV sev=1.0 de la nada (VIGIA-REAL-006).
   Además de fabricar la fractura, esto es una violación del invariante de
   determinismo (la fractura sellada cambia con el reloj de pared).

La fractura resultante siempre lleva `severity=1.0` (máxima) y sella la
interpretación *"structurally impossible without log fabrication… the evidence was
planted retroactively"* — texto que entra al bundle vía `caie_fracture_details`
(B-094). El guard R3-1 (2026-07-07) acota el **rango** de fechas plausibles
[2000, 2038), pero no valida que la comparación tenga sentido forense: un gap de
104 días entre eventos no relacionados pasa el guard sin ruido.

### M2 — FALSE_FLAG_PATTERN: `avg_cultural > 0.5 ∧ avg_technical < 0.2` ⇒ "plantado"
`vigia/tools/caie.py`, Rule 1, Case B (~líneas 1252–1312).

- `cultural` = artefactos `cultural_marker`/`ip_geolocation`/`user_agent`;
  `technical` = `memory_process`/`lsass_session`/`kernel_structure`/`usn_journal`/
  `hmac_audit_log`. La regla infiere: señal cultural alta sin corroboración de
  memoria ⇒ *"cultural evidence planted to mislead attribution… the HABIT is to
  disguise origin, not to act"* (sev=0.8 → boost 0.36, suficiente para cruzar solo
  el umbral MALICE de 0.33 desde casi cualquier base).
- El fix H-02 agregó el guard `confirmed_clean`, pero exige flags **explícitos**
  (`timestomp_detected: false`, etc.) que **los archivos FP-CULTURAL-CLEAN del corpus
  no tienen** — el comentario del código afirma "FP-CULTURAL-CLEAN sets
  timestomp_detected=False" y es falso para los dos archivos reales. El fix protege
  al caso de test sintético, no a los casos del corpus que motivaron el fix.
- En el corpus canónico, `cultural_marker` se usa de facto como contenedor genérico
  de "señal lingüística/conductual" (estilometría, mirroring, tickets, e-mails, hasta
  un reverse shell — ver §4.3), de modo que la regla dispara en ~20 casos donde no
  hay ninguna cuestión de bandera falsa, y sella una teoría del caso **inversa** a la
  que el propio caso declara.

---

## 3. Tabla resumen (ordenada por confianza)

Umbral MALICE = 0.33, SUSPICION = 0.10. "Sin fractura" = score tras ablación de la
familia completa.

### FÓSIL CONFIRMADO (fractura sin sentido forense; el veredicto depende de ella)

| # | Caso | Veredicto motor (exp.) | Score → sin fractura | Mecanismo | Contradicción interna |
|---|------|------------------------|----------------------|-----------|------------------------|
| F-01 | VIGIA-MAGNET-2020-WINDOWS | MALICE (INTENT) | 0.830 → 0.330 SUSPICION | M1 ×4: install keys (feb) y audit policy (2009!) vs psscan (abr); matches "registered"/"credential"/"network" | notes: "No external compromise detected… all legitimate processes and network connections" |
| F-02 | VIGIA-FN-001 | SUSPICION (MALICE) | 0.464 → 0.020 NOISE | M1: registro de **vacaciones** ("registe**red** vacation") 14-jun tratado como "network log" vs upload a Drive 15-jun | notes: "no technical errors. Everything is 'normal'" vs interpretación sellada "planted retroactively" |
| F-03 | VIGIA-CAN-031 (case_004_incompetencia_armamentizada) | MALICE (MALICE) | 0.739 → 0.289 SUSPICION | M1: ticket IT "screen flicke**red**" (14-ene) vs powershell (28-abr), gap 104 d; la narrativa dice que el ticket llegó **63 segundos** después | timestamps del propio caso contradicen su descripción (ene vs abr) |
| F-04 | VIGIA-CAN-026 (case_108_inversion_carga_prueba) | MALICE (MALICE) | 0.779 → 0.279 SUSPICION | M1 ×3: testimonios/respuestas verbales ("unanswe**red**", "c**red**entials") tipados `memory_process`, gap 90 d | la "respuesta" del usuario está fechada 3 meses ANTES de la consulta del SOC que responde |
| F-05 | VIGIA-CAN-012 (case_094_agujero_negro_burocratico) | MALICE (MALICE) | 0.766 → 0.266 SUSPICION | M1 ×2: muestreo OCR de PDFs (con `network_log_time`!) vs ctime de PDFs, gap 45 d — ninguno es red ni proceso | los 4 artefactos son análisis de metadata documental; 3 tipados `memory_process`, 1 como log de red |
| F-06 | VIGIA-CAN-042 (case_012_camuflaje_simbiotico) | MALICE (MALICE) | 0.770 → 0.270 SUSPICION | M1 ×2: medición de bandwidth del episodio-1 (5-may) vs procesos Zoom/exfil del episodio-2 (19-may) — cross-episodio | la discrepancia 200:1 ocurre DURANTE la llamada Zoom según la narrativa, pero está fechada 14 días antes |
| F-07 | FP-CULTURAL-CLEAN-001 | MALICE (NOISE) | 0.421 → 0.066 NOISE | M2: dev ruso en Torzhok, sistema limpio ⇒ "false flag" | audit_note: control negativo H-02; descripción: "The absence of a malicious event is not evidence of a staged one" |
| F-08 | FP-CULTURAL-CLEAN (benign/) | MALICE (NOISE) | 0.445 → 0.085 UNKNOWN | M2: ídem | audit_note: "con la regla actual (avg_technical < 0.2 = culpa) este caso falla" — el caso documenta su propio fósil |

### FÓSIL SEMÁNTICO (veredicto esperado correcto, pero sostenido por una fractura cuya teoría sellada es indefendible en cross-examination)

Los 20 casos siguientes son MALICE esperado y motor; sin FALSE_FLAG_PATTERN caen a
SUSPICION/UNKNOWN/NOISE. El problema no es la etiqueta — es que el bundle sella
*"classic false-flag pattern: cultural evidence planted to mislead attribution"*
en casos donde esa teoría es inversa o ajena a la verdad declarada del caso.

| # | Caso (case_id) | Score → sin fractura | Subgrupo | Por qué la teoría sellada no sobrevive |
|---|------|----------------------|----------|----------------------------------------|
| F-09 | VIGIA-CAN-004 (doble_salto_layout) | 0.473 → 0.113 SUSP | A: atribución genuina | El caso declara la señal cultural como **genuina** (memoria muscular rusa delata al actor); la fractura la sella como **plantada para desviar** — teorías opuestas |
| F-10 | VIGIA-CAN-006 (calco_semantico) | 0.437 → 0.077 NOISE | A | Ídem: calco de 'стране' como huella genuina, no cebo |
| F-11 | VIGIA-CAN-013 (sombra_fonetica) | 0.440 → 0.080 NOISE | A | Doble calco chino genuino |
| F-12 | VIGIA-CAN-022 (error_layout_comentario) | 0.568 → 0.207 SUSP | A | 'cnfnbz' = 'статья' con layout RU activo — genuino |
| F-13 | VIGIA-CAN-041 (traicion_puntuacion) | 0.455 → 0.095 UNKNOWN | A | Estilometría del CEO real vs impostor — no hay marcador cultural plantado |
| F-14 | VIGIA-CAN-044 (clonacion_sintactica) | 0.411 → 0.051 NOISE | A | Astroturfing: 3 títeres, 1 autor — atribución genuina |
| F-15 | VIGIA-CAN-045 (motin_comillas) | 0.513 → 0.153 SUSP | A | Comillas angulares «» genuinas del teclado del operador |
| F-16 | VIGIA-CAN-020 (espejo_soporte) | 0.413 → 0.053 NOISE | B: Carnegie/social | Mirroring de frases del KB — no existe cuestión de atribución cultural |
| F-17 | VIGIA-CAN-030 (sincronizacion_panico_semantico) | 0.444 → 0.084 UNKNOWN | B | DoS cognitivo al SOC |
| F-18 | VIGIA-CAN-043 (estocolmo_inverso) | 0.385 → 0.025 NOISE | B | Docilidad excesiva en soporte |
| F-19 | VIGIA-CAN-048 (fusion_panico_coordinado) | 0.398 → 0.038 NOISE | B | Pánico coordinado |
| F-20 | VIGIA-CAN-049 (fusion_duda_instrumental) | 0.438 → 0.078 NOISE | B | Duda instrumental |
| F-21 | VIGIA-CAN-050 (fusion_normalizacion_maliciosa) | 0.420 → 0.060 NOISE | B | Mensajes de normalización |
| F-22 | VIGIA-CAN-051 (fusion_autoridad_tecnica_fabricada) | 0.420 → 0.060 NOISE | B | Falsa autoridad técnica |
| F-23 | VIGIA-CAN-052 (fusion_agresion_defensiva) | 0.412 → 0.052 NOISE | B | Agresión jerárquica |
| F-24 | VIGIA-CAN-008 (anacronismo_herramienta) | 0.555 → 0.195 SUSP | C: tipado roto | Las alertas EDR están tipadas `cultural_marker` (raw 0.91) y el **rootkit de kernel** `memory_process` con raw **0.05** — la regla ve "cultura alta, técnica nula" en un caso 100 % técnico |
| F-25 | VIGIA-CAN-011 (deepfake_estilo) | 0.624 → 0.264 SUSP | C | Commits vía API key tipados `cultural_marker`; "sin sesión del arquitecto" = memory_process raw 0.05 |
| F-26 | VIGIA-CAN-024 (mimesis_error_administrativo) | 0.581 → 0.221 SUSP | C | E-mail de seguimiento del fraude tipado `cultural_marker`; hash del PDF original raw 0.05 |
| F-27 | VIGIA-CAN-046 (paracaidista) | 0.582 → 0.222 SUSP | C | Un **reverse shell ejecutado como root** tipado `cultural_marker`; el hash-mismatch con entropía 7.8 tipado `memory_process` raw **0.06**. Caso de timestomping sellado como "bandera falsa cultural" |
| F-28 | VIGIA-CAN-047 (ventrilocuo) | 0.551 → 0.191 SUSP | C | Process hollowing; la señal fuerte es `ip_geolocation` 0.82 (bucket "cultural") y los indicadores de memoria llevan raw 0.07 |

> Nota sobre el subgrupo C: ahí el fósil es doble — regla M2 + **datos mal tipados**
> (la señal técnica fuerte fue cargada en tipos del bucket "cultural" y los artefactos
> de memoria llevan raw ~0.05). Cross-examination: *"¿Su motor dice que el reverse
> shell fue 'evidencia cultural plantada para desviar la atribución'?"*

### SOSPECHOSO (misma mecánica fósil, pero el veredicto NO depende de ella — inflan score/narrativa)

| Caso | Fractura | Nota |
|------|----------|------|
| VIGIA-REAL-006 (m57 Jean) | M1: TCV sev=1.0 fabricada de `_utcnow()` — "sto**red**" matcheó el filtro y ambos artefactos carecen de timestamp (gap: **1.9 ms de skew de creación de objetos**) | No decide (0.903 con corroboración real), pero la fractura sellada depende del reloj de pared: violación del invariante de determinismo y narrativa "planted retroactively" en un caso de phishing 2008 |
| case_085, case_087, case_092, case_103, case_109, case_007, case_008_paranoia, case_016, case_020_mimetismo (consolidated_canonical) | M1: TCVs cross-epoch con gaps de 45–169 días entre artefactos de episodios distintos | El veredicto sobrevive sin ellas, pero cada una añade al bundle una interpretación "log fabrication / planted retroactively" que el caso no sostiene |

### DESCARTADO TRAS REVISIÓN (fractura/violación legítima)

| Caso | Señal | Por qué es legítima |
|------|-------|---------------------|
| case_002_log_fabrication | STATISTICAL_UNIFORMITY (sev 0.85) del JSON; SUSPICION depende de ella | 50 eventos con std de intervalo 0.001 s — regularidad inhumana es exactamente lo que la regla debe medir; comparación homogénea (mismo artefacto, misma serie) |
| case_001_temporal, case_083, case_087 (EFFECT_BEFORE_CAUSE / PREPARATION_BEFORE_EXCUSE), case_097, case_009, VIGIA-LINUX-003, VIGIA-REAL-TDUNGAN, VIGIA-BREAK-016 | TCVs/violations con deltas de segundos-a-horas dentro del mismo episodio | Comparaciones de eventos causalmente relacionados con gaps operacionalmente plausibles; por diseño del caso; además ninguna decide el veredicto por sí sola |

---

## 4. Dossiers (formato B-114 Grupo 1)

### F-02 — VIGIA-FN-001 (el fósil que enmascara un falso negativo)

1. **Evidencia real sin la fractura:** casi nula — logs de login legítimos, RDP/SMB
   normales, upload de 500 MB a Drive con raw bajo. Score residual 0.020 → NOISE.
2. **Distancia al umbral:** queda a 0.08 de SUSPICION y a 0.31 de MALICE. El
   SUSPICION sellado (0.464) es 95 % boost de la TCV.
3. **Nota de diseño contradictoria:** sí, doble. `notes`: *"False negative test: no
   technical errors. Everything is 'normal'. The only anomaly is the user's absence
   (HR)"*. `devil_advocate`: *"There are no technical errors… all legitimate"*. La
   TCV sella lo contrario: *"log fabrication… planted retroactively"*.
4. **Lectura:** **fósil confirmado, y el más instructivo del corpus.** La TCV se
   dispara porque "marketing_user **registered** vacation" contiene 'red'. El
   "registro de vacaciones antes del upload" no solo no es una violación causal —
   es la premisa del caso (el atacante usa credenciales del empleado ausente). El
   caso fue diseñado para medir si VIGÍA abstiene/falla sin fuentes HR; el fósil le
   regala un SUSPICION por la razón equivocada, ocultando el falso negativo que el
   caso debía revelar. Es el ejemplo perfecto de fósil que **mejora la métrica del
   corpus mientras degrada la integridad del motor**.

### F-01 — VIGIA-MAGNET-2020-WINDOWS (referencia, ya conocido de B-114)

1. **Evidencia real:** toolkit de piratería coordinado (KMSAuto + trashreg + Office
   Tab en ventana de 155 s) + RDP sin NLA en Win7 EOL — INTENT sin ocultamiento,
   exactamente lo que dice `expected_verdict: INTENT`.
2. **Distancia:** 0.830 → 0.330 = exactamente en el borde SUSPICION/MALICE (el
   umbral es "> 0.33"). Sin las 4 TCVs el caso NO es MALICE.
3. **Contradicción:** notes: "No external compromise detected… Memory analysis
   confirms all legitimate processes and network connections". Además
   `devil_advocate` plantea el contexto CTF-lab.
4. **Lectura:** **fósil confirmado** (el arquetipo). Las 4 TCVs comparan: 3 claves
   de instalación de febrero contra el listado psscan de la adquisición de abril
   (matches: "registered" ×2, texto "network" en la descripción del RDP), y la
   política de auditoría default de 2009 ("c**red**ential") contra el mismo psscan —
   gap de 3.934 días.

### F-03/F-04/F-05/F-06 — Los cuatro CAN con TCV cross-epoch

Patrón común: casos canónicos sintéticos cuyos artefactos llevan **fechas
internamente incoherentes con su propia narrativa** (eventos que el texto describe
separados por segundos están fechados con meses de diferencia — probable secuela del
consolidador/generador de casos), más artefactos de testimonio/documento **tipados
`memory_process` o con `network_log_time`**. La TCV cruza esos pares y sella
"planted retroactively" con sev=1.0.

1. **Evidencia real sin la fractura:** en los cuatro, la señal narrativa/técnica
   diseñada (PowerShell+vssadmin, Mimikatz en memoria, factory de PDFs, exfil bajo
   Zoom) deja score residual 0.27–0.29 → SUSPICION sólido, no MALICE.
2. **Distancia:** los cuatro quedan a 0.04–0.06 del umbral MALICE sin la TCV.
3. **Contradicción:** no vía `notes` (describen malicia real), sino **interna**: los
   timestamps del JSON contradicen la propia descripción del caso (F-03: "63
   segundos después" vs 104 días; F-04: la respuesta precede a la pregunta por 3
   meses; F-06: la medición del 5-may pertenece al evento del 19-may).
4. **Lectura:** **fósiles confirmados.** La etiqueta MALICE es correcta por diseño,
   pero el motor la alcanza mediante una comparación que no existe en la realidad
   del caso. Si un fix de datos corrigiera las fechas (o un fix de regla exigiera
   pares proceso→su-propia-red), estos cuatro caerían a SUSPICION: hoy su MALICE es
   deuda del fósil, no mérito de la evidencia.

### F-07/F-08 — FP-CULTURAL-CLEAN ×2 (el fósil documentado que el fix no cubrió)

1. **Evidencia real:** ninguna maliciosa — por diseño (controles negativos H-02:
   máquina rusa limpia).
2. **Distancia:** 0.421/0.445 → 0.066/0.085. Sin la fractura son NOISE/UNKNOWN,
   como exige la etiqueta.
3. **Contradicción:** la más explícita del corpus: el `audit_note` de
   `benign/FP-CULTURAL-CLEAN.json` dice textualmente *"con la regla actual
   (avg_technical < 0.2 = culpa) este caso falla"*.
4. **Lectura:** **fósil confirmado y además re-abierto.** El guard `confirmed_clean`
   (H-02/L-019) existe en el código, pero exige `timestomp_detected: false` etc.
   explícitos que estos dos archivos no tienen — el comentario en `caie.py` que
   afirma "FP-CULTURAL-CLEAN sets timestomp_detected=False" describe el caso de
   test, no los archivos reales del corpus. El fix quedó validado contra su propio
   test y no contra los casos que lo motivaron. (Ambos casos están excluidos del
   "corpus verde" por su audit_note, así que no contaminan la métrica — pero el
   motor sigue sellando MALICE sobre un usuario por su idioma, que es la clase de
   veredicto que L-019 declara inaceptable.)

### F-09…F-28 — El bloque FALSE_FLAG_PATTERN (fósil semántico masivo)

1. **Evidencia real sin la fractura:** en los 20 casos, la señal diseñada está en
   artefactos del bucket "cultural" (estilometría, calcos, mirroring — o señal
   técnica mal tipada, subgrupo C). Sin el boost: 10 caen a NOISE, 2 a UNKNOWN, 8 a
   SUSPICION. Ninguno sostiene MALICE.
2. **Distancia:** el boost fijo de la regla (0.8×0.45 = 0.36) es en la práctica el
   **único** camino de estos casos al umbral 0.33 — la regla funciona como "puente
   a MALICE" universal para señal lingüística.
3. **Contradicción:** en el subgrupo A es frontal: `peirce_chain.thirdness` declara
   la señal cultural como huella genuina que delata al actor ("The slip destroys
   the identity alibi") y la fractura sella la teoría opuesta ("planted to mislead
   attribution; MALICE belongs to the planter, not to whoever writes in the
   indicated language"). En B y C la teoría sellada es simplemente ajena al caso.
4. **Lectura:** **fósil semántico** (no "fractura falsa" sino teoría-del-caso falsa).
   La regla pre-Daubert "cultura alta + técnica baja = bandera falsa" quedó
   funcionando como scorer genérico de evidencia lingüística. Los veredictos
   esperados se cumplen, pero cada bundle sella una explicación que la defensa
   destruye leyendo el propio caso en voz alta. Bajo el estándar del proyecto
   ("If a system claims MALICE without explaining it with exact mathematics, it is
   not forensics"), la explicación sellada es matemáticamente exacta y
   semánticamente falsa. Decisión pendiente caso-por-caso: es un problema de regla
   (M2), no de 20 casos individuales.

### VIGIA-REAL-006 — mención especial (no decide, pero viola determinismo)

TCV sev=1.0 entre "File… **sto*red*** unencrypted on Desktop" (file_metadata, sin
timestamp) y el artefacto de proceso (sin timestamp): ambos reciben `_utcnow()` al
crearse y la "violación causal" es el orden de instanciación de objetos Python,
con gap de 1.9 ms. La fractura cambia con cada corrida (timestamps de pared en el
detalle sellado). No altera el veredicto (0.903 con corroboración genuina m57),
pero es la demostración límite del mecanismo M1: una TCV puede nacer de **cero**
información temporal en la evidencia.

---

## 5. Datación (hipótesis "primeros días" — parcialmente confirmada)

- El historial git empieza en el import squasheado `dbba7ca` (2026-07-05); la
  datación fina es interna.
- **Reglas:** el filtro substring de TCV y su fallback preceden al fix comentado
  "session 2026-05-18" (que amplió el filtro, reconociendo por escrito que el
  matching sobre texto libre no es reproducible — y reteniéndolo). FALSE_FLAG
  Case B es "original Rule 1 behavior", anterior al fix H-02. Ambas reglas son
  pre-disciplina-Daubert (los gates B-068/R4-3 v2/R3-1 son de fines de junio–julio).
- **Casos:** VIGIA-REAL-006 consolidado 2026-04-28 (corpus temprano,
  `vigia_forensic_cases.json`); VIGIA-FN-001 2026-06-05; el bloque
  consolidated_canonical (case_001…case_112 → VIGIA-CAN-*) es de la era de
  consolidación masiva de mayo–junio.
- Conclusión: los fósiles no están tanto en *casos* viejos como en **reglas** viejas
  que la disciplina posterior blindó por fuera (guards de rango, gates de
  corroboración) sin revisar la premisa semántica de la comparación. R3-1 acotó
  QUÉ fechas puede comparar TCV; nadie preguntó todavía si los dos artefactos
  comparados tienen relación causal alguna.

## 6. Límite del barrido (honestidad sobre completitud)

- El barrido cubre las fracturas CAIE vivas y las `temporal_violations` del JSON.
  No ablacioné señales del composite base (raw_scores, pesos por dominio) — otra
  familia posible de fósiles, fuera del alcance de esta cacería.
- "Veredicto sellado" aquí = veredicto del motor determinístico sobre el corpus
  (idéntico al que sella `vigia_agent.py`); no re-verifiqué bundle por bundle en
  `results/` salvo MAGNET-2020 (B-114).
- Los 9 casos "SOSPECHOSOS" con TCV cross-epoch no decisivas merecerían la misma
  revisión de datos que F-03…F-06 si alguna vez se recalibra el umbral o se
  fortalece el gate: hoy no deciden, mañana pueden decidir.
- VIGIA_BREAK_001-010.json (lista de 10 sub-casos) quedó fuera del contrato de
  `_vigia_score`; sus derivados individuales sí se barrieron.

---

*Barrido ejecutado con `_vigia_score` real + ablación por monkeypatch sobre
`detect_fractures` (harness en scratchpad de sesión, equivalente scorer_gate
`--filter`). Corpus: 199 casos, 198 evaluados. Cero escrituras fuera de este
documento. Restore tag: `restore-fossil-hunt-20260711`.*
