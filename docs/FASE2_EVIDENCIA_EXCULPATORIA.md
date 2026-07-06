# FASE 2 — EVIDENCIA EXCULPATORIA: INVESTIGACIÓN DE IMPACTO (`semantic_role`)

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-07-06 |
| **Tag de restauración** | `pre-fase2-exculpatoria-20260706-155936` (local) |
| **Alcance** | **Solo investigación y medición — ningún cambio de código ni de datos.** Scripts de censo/simulación en scratchpad de sesión, no en el repo. |
| **Mandato** | Antes de implementar `semantic_role` (incriminatory/exculpatory/contextual, espejo de B-070): ¿cuántos casos tienen artefactos exculpatorios? ¿cuántos veredictos cambiarían? |
| **Baseline** | HEAD `e10a364`, corpus honesto 152/199, motor blind (`_vigia_score` sin etiqueta) |

---

## RESUMEN EJECUTIVO

1. **Censo:** 48/198 casos (24%) contienen ≥1 artefacto exculpatorio-candidato por heurística de contenido; 59/1018 artefactos (5.8%). Tras revisión manual, los **genuinamente exculpatorios son ~27 artefactos en 18 casos** — el resto es **cebo plantado** (tickets lastimeros que SON la firma del ataque) o match incidental de keywords.
2. **El diseño funciona SOLO si `semantic_role` es examiner-declared.** Con clasificación automática por contenido (S1), el cambio es **neto negativo**: degrada 9 casos maliciosos — incluyendo exactamente los casos adversariales que el corpus ya tiene para este ataque (`cebo_falso`, `incompetencia_armamentizada`, `denunciante_humo`). Con clasificación correcta (S2, examiner-declared): **+13 de agree en los casos afectados, 14/15 BEN recuperados a NOISE, cero casos maliciosos reales perdidos**.
3. **Estimación de impacto en el corpus completo: 152/199 → ~165/199** bajo S2 (estimación por composición sobre los 48 casos afectados; a confirmar con `run_all_agent.py` en la fase de implementación).
4. **La semántica correcta es "apartar" (patrón B-070), no "restar".** Las variantes V1 (fuera del composite y del gate) y V2 (score 0) convergen en veredictos cuando la clasificación es correcta; la resta activa (V3) no aporta nada medible y agrega superficie de ataque (cebo exculpatorio plantado suprimiendo señal real activamente).

---

## 1. CENSO — ¿CUÁNTOS CASOS TIENEN ARTEFACTOS EXCULPATORIOS?

**Método:** heurística de 44 patrones ES+EN (autorización/approved/firmado, tickets CHG-/TD-/INF-/SUP-, HR record/RRHH, GDPR/DPO, runbook/CAB, calendar event, kernel doc, verificable, asset tag, dashboard, IAM role, auditoría PASSED…) sobre `description` + `metadata.content_preview` + `forensic_anomalies` de cada artefacto del universo `run_all_agent.find_cases` (198 casos-dict, 1018 artefactos).

| Métrica | Valor |
|---|---|
| Casos con ≥1 candidato | **48/198 (24%)** |
| Artefactos flaggeados | **59/1018 (5.8%)** |
| Por segmento | BEN 15, OTHER 19 (case_0xx sintéticos + DEMO + NGDC + LINUX), KIWI 5, REAL 4, FN/FP 3, BREAK 2 |
| Casos flaggeados con etiqueta **MALICE** | **28** — el dato que define el diseño |

**El patrón que motivó la fase se confirma en los 15 BEN:** en todos, el artefacto de score más alto (ART-003, 0.95, THIRDNESS) es la documentación corroborante de benignidad (HR record, runbook auditado, change board, política GDPR, memo de autorización), y por ser `log_entry`/`file_timestamp` cae en rol **DEVICE** de B-070 — así que no solo suma el score más alto al composite: **además corrobora el gate B-068 hacia MALICE**. Los 3 BEN que dan MALICE limpio (004/008/009) cruzan el gate exactamente por eso.

## 2. REVISIÓN MANUAL — PRECISIÓN DE LA CLASIFICACIÓN POR CONTENIDO

Inspección del texto real de todos los flaggeados no-BEN. Tres categorías:

**A — Exculpatorio genuino (~27 artefactos, 18 casos):** los 24 de BEN-001..015 (ART-002/ART-003, más ART-001 en 012/013), `VIGIA-LINUX-002` (approval real), `VIGIA-FP-002` (CAB-2026-0610 para el backup nocturno), `VIGIA_BREAK_002_VALID_BENIGN` ("authorized pentest window approved").

**B — Cebo plantado / incompetencia armamentizada (~8):** el texto exculpatorio-forme es **parte del ataque** y su score alto es CORRECTO:
- `case_084_cebo_falso_layman` (MALICE, raw 0.92): ticket *"I don't know what I touched, black screen…"*
- `case_004_incompetencia_armamentizada` (MALICE, raw 0.92): ticket *"my screen flickered, I'm hopeless with computers"* — **63 segundos después del PowerShell**. Es el patrón CAN-031, caso estrella del README.
- `case_101_denunciante_humo` (MALICE, raw 0.92): ticket "I think I was hacked" como cortina de humo.
- `case_007_insomnio_tactico` (MALICE): "MFA aprobado" — el login exitoso con credenciales robadas.

**C — Match incidental (~24):** la keyword aparece en contexto no exculpatorio. El ejemplo más peligroso es la **trampa de negación**: `case_018_clonacion_sintactica` (MALICE) flaggea *"DLP rule disabled … **without CISO approval**"* — la AUSENCIA de aprobación es lo incriminatorio, y el regex matchea "approval". También: NGDC-002 (la confesión capturada por keylogger), DEFI-DRAIN (código del drainer), MAGNET-2022 (evento de servicio).

**Precisión de la heurística: ~46%.** Más de la mitad de lo que un auto-clasificador marcaría como exculpatorio no lo es — y una parte fue diseñada por el propio corpus adversarial para explotar exactamente esta mejora.

## 3. SIMULACIÓN — ¿CUÁNTOS VEREDICTOS CAMBIARÍAN?

**Método:** para cada caso afectado, `_vigia_score` blind sobre el caso intacto (baseline) y sobre variantes: **V1** = artefactos exculpatorios removidos (fuera del composite Y del gate — la semántica B-070); **V2** = `raw_score:=0` (neutraliza pero sigue contando para el gate). Escenarios: **S1** = auto-clasificador (los 59 flaggeados), **S2** = oráculo/examiner-declared (solo los ~27 genuinos de la categoría A). Comparador con la doctrina vigente (BENIGN→NOISE, UNKNOWN acepta todo, MALICE-donde-INTENT ok).

| Escenario | Veredictos que cambian | agree en los 48 afectados | Benignos ganados | Maliciosos degradados |
|---|---|---|---|---|
| **S1V1** — auto + apartar | 20 | 27 → **24 (NETO NEGATIVO)** | 6 | **9** |
| **S1V2** — auto + neutralizar | 13 | 27 → 29 | 5 | **3** |
| **S2V1** — examiner + apartar | 15 | 27 → **40 (+13)** | **14** | 1* |
| **S2V2** — examiner + neutralizar | 15 | 27 → **40 (+13)** | **14** | 1* |

Degradaciones de S1V1 (el auto-clasificador): `case_084` MALICE→SUSPICION, `case_004` MALICE→SUSPICION, `case_101` MALICE→SUSPICION, `case_007` MALICE→SUSPICION (×2 variantes), `case_087` MALICE→SUSPICION, `BREAK-016` MALICE→SUSPICION y — la peor — **`case_018` MALICE→NOISE**: remover el artefacto del DLP ("disabled without CISO approval") destruye la detección completa por la trampa de negación.

\* El único "degradado" de S2 es `VIGIA_BREAK_002_VALID_BENIGN` (exp SUSPICION → NOISE): su contenido es un pentest genuinamente autorizado; si eso debe seguir siendo SUSPICION con la autorización apartada es una **cuestión de etiqueta/doctrina del suite BREAK**, no una pérdida de detección — queda para revisión de etiqueta, no computa como daño real.

**Resultado sobre los 15 BEN (el objetivo de la fase):** S2 recupera **14/15 a NOISE**. El único que queda SUSPICION es **BEN-012** (kworker huérfano): ahí el artefacto que puntúa no es la documentación exculpatoria sino el fenómeno mismo (el kernel thread, raw 0.7 por el mapeo Peirce del conversor) — es un problema de *baseline de conocimiento del SO* (kthreadd es normal), no de dirección de la evidencia. `semantic_role` no lo arregla y no debe pretender arreglarlo.

**Estimación de impacto en el corpus completo:** los 151 casos no afectados no cambian; sobre los 48 afectados el agree pasa 27→40 ⇒ **152/199 → ~165/199** (+13). Estimación por composición con la réplica del comparador — el número final debe confirmarse con `run_all_agent.py` al implementar.

## 4. DISEÑO RECOMENDADO (PARA LA FASE DE IMPLEMENTACIÓN — NO APLICADO)

1. **Campo `semantic_role` en el artefacto**, valores `incriminatory` (default), `exculpatory`, `contextual`. Punto de inserción espejo de B-070: en `vigia_scorer.py` los exculpatorios se **apartan** como los `_narrative_artifacts` (líneas 439-445) — fuera del composite **y fuera del conteo del gate B-068** (líneas ~803+, donde hoy corroboran como DEVICE) — y se retienen en el reporte como `refutation_context`. Es exactamente la semántica V1 medida.
2. **`semantic_role=exculpatory` es EXAMINER-DECLARED, jamás derivado del contenido.** La medición S1 es la prueba: el corpus adversarial ya contiene el ataque (cebo falso, incompetencia armamentizada, denunciante humo, espejo de soporte) y el auto-clasificador degrada 9 casos maliciosos. Mismo patrón que los overrides de adquisición L-037. Un `semantic_role` que llegue en el JSON del caso debe tratarse como declaración del examinador bajo su responsabilidad, sellada en el bundle.
3. **NO implementar "resta" (V3).** V1 y V2 convergen con clasificación correcta (tabla §3); la resta activa no aporta nada medible y crea la superficie de ataque inversa: evidencia exculpatoria plantada suprimiendo activamente señal incriminatoria real. "Apartar" es conservador y suficiente.
4. **Ortogonalidad con B-070:** `evidence_role` clasifica la *clase* del artefacto (device/contextual/narrative); `semantic_role` clasifica la *dirección de la inferencia*. Un HR record es DEVICE por clase y exculpatory por dirección — hoy esa combinación es la que rompe los BEN (suma Y corrobora).
5. **Pendiente doctrinal para Anna:** ¿la evidencia exculpatoria requiere su propia barra de corroboración (simetría Daubert: una refutación también necesita dos fuentes / spoofability CAIE aplicada al memo de autorización)? La medición actual no lo necesita para el corpus, pero un memo forjado examiner-declared por error sería un FN sin fricción. Propuesta mínima: los exculpatorios apartados igual pasan por `detect_eco_overinterpretation` (documentación demasiado perfecta = señal).

## 5. WORKLIST DE ETIQUETADO INICIAL (si se aprueba la implementación)

Los ~27 artefactos de la categoría A: `VIGIA-BEN-001..015` → `ART-002`, `ART-003` (y evaluar `ART-001` en 012/013), `VIGIA-LINUX-002` → `linux002_03`, `VIGIA-FP-002` → `fp002_02`, `VIGIA_BREAK_002_VALID_BENIGN` → `ART-002` (sujeto a la revisión de etiqueta de §3). **Ningún caso MALICE lleva etiqueta exculpatory** — los tickets de la categoría B son `incriminatory` por diseño del ataque.

---

*Investigación ejecutada sin modificar código ni datos. Scripts de censo y simulación reproducibles descriptos en §1 y §3; salidas completas en el log de la sesión. La implementación queda pendiente de la decisión de doctrina sobre §4.2 y §4.5.*
