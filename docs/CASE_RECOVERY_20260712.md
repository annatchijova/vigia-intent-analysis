# Recuperación de casos — caracterización de los 29 in-scope + implementación (2026-07-12)

Objetivo: hacer que VIGÍA pase más casos **sin forzar** (empezando por los que
no son BREAK ni FP/FN), sin quitar golden rules, escribiendo detectores nuevos
donde haga falta. Método: workflow de caracterización (5 sondas, 17 agentes,
1.37M tokens) con verificación adversarial de FP-safety por detector, más
medición propia corpus-wide. Convención de conteo: **/193 case_ids únicos**
(referencia oficial; el /199 son archivos, incluye la lista BREAK_001-010 y 5
case_id duplicados).

**Baseline al empezar la sesión: 155/193. Tras este trabajo: 161/193 (+6).**

---

## 1. Clasificación de los 29 casos in-scope

Excluidos por instrucción (son para romper el sistema): 3 BREAK + 6 FP/FN.

| Clasificación | N | Casos |
|---|---|---|
| RECOVERABLE-SAFE (implementado) | 6 | LINUX-006, ANDROID11, SEP800, SET68I, case_004, case_012 |
| RECOVERABLE — TTP nuevo estrecho (diferido) | 2 | case_108, case_094 |
| RECOVERABLE-RISKY / DATA-FIX (diferido, decisión) | 6 | MAGNET-2020, MAGNET-2014-TIMELINE, DEMO-004, DEMO-007, DEMO-009, LINUX-008 |
| ALREADY-CORRECT-DOCTRINE (dejar como está) | 7 | RAFAEL, JESS-KEYCHAIN, JESS, case_024, DEMO-008, case_007, REAL-007 |
| UNFIXABLE-NO-FORCE | 4 | ASCIISTUDIO, PAGINA-WEB-PAPA, WEDLM, FP-002 |
| Sin etiqueta (data) | 1 | CTF-2021-iOS-Eli-iPhone8 |

Cada afirmación abajo tiene su medición contra el motor real; cada detector
propuesto fue verificado adversarialmente como FP-safe y label-leak-free.

---

## 2. IMPLEMENTADO esta sesión (+6, cero roturas)

Todo en `vigia/tools/caie.py` (3 fracturas nuevas), `vigia_scorer.py`
(frozenset MALICIOUS + gate), `tests/caie/test_ttp_detectors.py` (16 tests).
Medición combinada corpus-wide: exactamente los 6 objetivos flipean a su
etiqueta esperada, **cero veredictos correctos se rompen**, sin interacción
entre detectores. Commit `1790a70`.

### 2.1 Tres detectores TTP canónicos (fracturas nuevas)

Todos keyean en metadata **estructurada** (nunca texto libre, nunca anotación)
y mapean a un TTP MITRE que cualquier motor DFIR debería detectar
independientemente de este corpus:

| Fractura | Keys on | TTP | Recupera |
|---|---|---|---|
| `PROCESS_MASQUERADE` | `basename(malicious_path)==basename(legitimate_path)` con dir distinto | T1036.005 | LINUX-006 → MALICE 0.68 (rama cross-domain, gate-corroborado) |
| `DEFENSE_EVASION_ARTIFACT` | `deleted_vsc==True` o `firewall_state=='off'` | T1490 / T1562.004 | case_004 → MALICE (por la señal real: vssadmin delete shadows, NO el TCV fósil removido) |
| `PROCESS_INJECTION_ANTIFORENSIC` | `injection_technique∈{hollowing,…}` o `pid_hidden==True` | T1055.012 | case_012 → MALICE |

Nota importante sobre case_004/012: eran B-115 (timestamps de metadata rotos)
y su MALICE previo a M1 lo cargaba el **TCV fósil**. Estos detectores los
recuperan por la **señal de ataque real** (VSS deletion, hollowing), que es el
motivo correcto — no reintroducen el fósil. Salieron de `KNOWN_PENDING` (ahora
pasan en ambas capas). Los otros 3 B-115 (case_108/094 recuperables, case_089/
099/etc. no) siguen pendientes de D-2 o de un detector estrecho (§3).

### 2.2 Intake-abstain gate (llena el gap de ABSTAIN del dossier)

`vigia_scorer.py`, post-veredicto, **solo cuando el veredicto ya es NOISE**:
reclasifica a ABSTAIN si la evidencia declara que el análisis no ocurrió
(`status: INTAKE_ONLY`/`EXTRACTION PENDING`, `analysis_status: PENDING`, o
`user_data_found`/`user_content_found`/`user_partition == False`). Certificar
NOISE sobre un registro intake-only es un certificado de limpieza falso; la
doctrina de VIGÍA dice que eso es ABSTAIN. Recupera ANDROID11, SEP800, SET68I.
Como solo dispara sobre NOISE, **jamás ablanda un SUSPICION/MALICE** (test
explícito). El dossier había marcado ABSTAIN como arquitectónicamente
inalcanzable — esto lo hace alcanzable vía evidencia real, sin label-leak.

---

## 3. DIFERIDO — recuperable pero requiere tu decisión / próxima sesión

### 3.1 Dos TTP nuevos más estrechos (B-115), verificados FP-safe

| Fractura candidata | Keys on | Recupera | Por qué diferido |
|---|---|---|---|
| `CLAIM_VS_RECORD_FABRICATION` | `claimed_*==True ∧ *_found==False` | case_108 (+ fusion_agresion) | Patrón real (corroboración afirmada refutada por el registro) pero más estrecho; decidir si vale como golden rule general |
| `DOCUMENT_FORGERY_MASS` | `modification_pattern=='date_regex_substitution'` | case_094 | **Solapa** el tipo existente `DOCUMENT_FORGERY`; conviene unificar en vez de agregar tipo nuevo |

Ambos FP-safe (N=1/2, cero roturas). Los dejé fuera del batch por ser más
específicos y (el segundo) por solapamiento — no por riesgo. Decisión tuya si
entran tal cual o refactorizados.

### 3.2 Data-fixes (ediciones de datos, no de motor) — verificados

| Caso | Defecto | Fix medido | Resultado |
|---|---|---|---|
| MAGNET-2020 | La tabla Volatility `netscan` (red en memoria) está tipada `log_entry` por pérdida de conversión | retipar a tipo de red | → MALICE (score 0.3297→cruza; INTENT acepta MALICE). FP-safe (1 solo cambio) |
| DEMO-004/007/009 | La copia ganadora bajo dedupe es `converted/` (lossy: aplanó `evidence_type` a log_entry, perdió dominio de red) | dedupe canonical-first, o borrar las copias converted/ lossy | +3, FP-safe (verificado: agreement 156→159 en ese harness) |
| LINUX-008 | Mismo masquerade del hermano 006, pero declarado en **texto libre** de la descripción, no en metadata | agregar `malicious_path`/`legitimate_path` a su metadata (mirroring 006) → PROCESS_MASQUERADE dispara | Autoría de metadata nueva — más discutible; NO aplicado |
| MAGNET-2014-TIMELINE | 4 artefactos tipados `file_timestamp` → un solo dominio; RECOVERABLE-RISKY | retipar docx/prefetch | FP-safe pero retipo debatible; diferido |

Recomendación: MAGNET-2020 y DEMO-004/007/009 son data-fixes limpios (corrigen
pérdida de conversión, como el subgrupo C) — aplicables con el mismo protocolo
de medición aislada. LINUX-008 y TIMELINE son más discutibles (autoría de
metadata / retipo dudoso) — tu decisión.

---

## 4. DEJAR COMO ESTÁ — el SUSPICION/NOISE es la llamada correcta

- **VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL** (SUSPICION 0.30): la evidencia es
  posesión de herramientas de ataque en `bash_history` de la propia máquina del
  atacante — un solo canal blando. La doctrina de dos fuentes (B-068) dice que
  eso no corrobora MALICE. SUSPICION es defendible bajo cross-examination.
- **JESS-KEYCHAIN, JESS** (INTENT→SUSPICION): un solo dominio de recolección;
  el motor no tiene escalón INTENT (over-severity a MALICE es cómo INTENT
  pasa). SUSPICION honesto.
- **case_024** (CAN-046): ya adjudicado SUSPICION honesto; reetiqueta CAN-026
  pendiente (sin apuro, tu decisión).
- **REAL-007** (SUSPICION 0.29): NO es data-fix — `_vigia_score` ya normaliza
  los artefactos legacy null internamente. Caso de atribución genuinamente en
  banda SUSPICION (identificación de acosador por correlación de red).
- **DEMO-008, case_007**: diferencia de score entre copias, no de veredicto; ya
  correctos.

## 5. UNFIXABLE sin forzar (documentado, no tocar)

- **ASCIISTUDIO, PAGINA-WEB-PAPA, WEDLM** (ABSTAIN esperado, dan NOISE): ZIPs de
  código fuente de 2 artefactos, analizados y limpios, **estructuralmente
  idénticos** a gemelos etiquetados NOISE (RELAY-MAIN-2026, SKILL-EVALS-2026).
  El único separador es `n_signals<3`, que aplicado corpus-wide **rompe 4 NOISE
  correctos** (verificado, detector rechazado). El NOISE de VIGÍA acá es la
  misma llamada correcta que hace en los gemelos.
- **FP-002** (ABSTAIN esperado): no es intake — es ambigüedad de autorización
  (exfil rsync 500GB + log de aprobación del CISO). Recuperarlo necesitaría
  detección de autorización por texto libre o label-leak.

## 6. CTF-2021-iOS-Eli-iPhone8 — sin etiqueta

`expected_verdict` ausente en el caso Y en el dataset de calibración. Da MALICE
0.417; cuenta como desacuerdo solo porque no hay etiqueta con qué comparar. Es
un **hueco de ground-truth**, no un error de motor. Decisión: etiquetar el caso
(¿MALICE? es un caso iOS real) o excluirlo del conteo.

---

## 7. Resumen de decisiones que te quedan (para las próximas 2 sesiones)

1. **Data-fixes limpios** (MAGNET-2020 netscan retype; DEMO-004/007/009 dedupe
   canonical-first): +4 más, mismo protocolo de medición aislada. ¿Aplico?
2. **case_108 / case_094**: ¿agrego CLAIM_VS_RECORD_FABRICATION y unifico
   DOCUMENT_FORGERY_MASS con el DOCUMENT_FORGERY existente? +2.
3. **B-115 data repair (D-2)**: re-anclar `metadata.*_time` en los ~26 casos
   canonical_v2. Independiente de esto; algunos B-115 solo se recuperan así.
4. **Reetiquetas de doctrina** (case_024→SUSPICION, CTF-Eli→etiqueta,
   JESS/RAFAEL como INTENT-honesto-SUSPICION): decisiones de anotación, no de
   motor.
5. **Dejar quietos** los UNFIXABLE (§5) — recuperarlos sería forzar.

Techo realista de agreement sin forzar y sin tocar labels: **~165-167/193**
(161 actual + 4 data-fixes + 2 TTP estrechos). El resto son decisiones de
doctrina/etiqueta o genuinamente ABSTAIN/SUSPICION correctos.

---

*Detectores verificados FP-safe por el workflow wf_58d740be-8ce (verificación
adversarial independiente por detector) + medición combinada corpus-wide del
agente principal. Cero golden rules removidas. Restore tag de sesión:
`pre-session-20260712-005232`.*
