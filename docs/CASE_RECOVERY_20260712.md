# Recuperación de casos — caracterización de los 29 in-scope + implementación (2026-07-12)

Objetivo: hacer que VIGÍA pase más casos **sin forzar** (empezando por los que
no son BREAK ni FP/FN), sin quitar golden rules, escribiendo detectores nuevos
donde haga falta. Método: workflow de caracterización (5 sondas, 17 agentes,
1.37M tokens) con verificación adversarial de FP-safety por detector, más
medición propia corpus-wide. Convención de conteo: **/193 case_ids únicos**
(referencia oficial; el /199 son archivos, incluye la lista BREAK_001-010 y 5
case_id duplicados).

**Baseline al empezar la sesión: 155/193. Tras este trabajo: 163/193 (+8).**

> **Actualización (segunda tanda, misma sesión):** se agregaron 2 detectores
> TTP más (§3.1, commit `c64cf5c`): `CLAIM_VS_RECORD_FABRICATION` (case_108) y
> extensión de `DOCUMENT_FORGERY` por date-regex-substitution (case_094).
> 161 → 163, cero roturas, ambos verificados FP-safe. Quedan como **decisión
> tuya, no aplicados** los data-fixes MAGNET-2020 y DEMO — ver §3.2 (razones
> abajo). Suite 1243 passed.

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

### 3.1 Dos TTP nuevos más estrechos (B-115) — IMPLEMENTADO (commit c64cf5c)

| Fractura | Keys on | Recupera | Nota |
|---|---|---|---|
| `CLAIM_VS_RECORD_FABRICATION` (nuevo) | `claimed_*==True ∧ *_found==False` en el mismo artefacto | case_108 | Patrón general de coartada fabricada; FP-safe (fusion_agresion ya pasaba, sigue) |
| `DOCUMENT_FORGERY` (extendido, sin tipo nuevo) | `modification_pattern=='date_regex_substitution'` | case_094 | Se unificó con el tipo existente en vez de crear `DOCUMENT_FORGERY_MASS` — evita duplicar catálogo |

Ambos verificados FP-safe (161→163, cero roturas). Recuperan por la señal real
(coartada refutada por el registro / masa de docs con fechas reescritas por
script), no por el TCV fósil removido. Salieron de KNOWN_PENDING.

### 3.2 Data-fixes — DECISIÓN TUYA (medidos, NO aplicados)

Los dejé sin aplicar a propósito: son ediciones de datos sellados con
sensibilidad que preferí no resolver solo (mismo criterio que CAN-008/047:
medir → presentar → tu aprobación → aplicar).

| Caso | Defecto | Fix medido | Por qué NO lo apliqué solo |
|---|---|---|---|
| **MAGNET-2020** | La tabla Volatility `netscan` (MAG2020W-007, conexiones de red en memoria) está tipada `log_entry` por pérdida de conversión | retipar `MAG2020W-007` a `network_flow` → **MALICE 0.3546** (rama cross-domain; INTENT acepta MALICE). FP-safe (1 solo cambio) | Es el **caso gatillo de B-114** con historia sensible: su propia narrativa dice *"INTENT sin ocultamiento… no external compromise"*. El retipo es legítimo (netscan ES red), pero empujarlo a MALICE contradice la doctrina declarada del caso. Vos decidís si el retipo correcto justifica la over-severity que el comparador tolera. |
| **DEMO-004/007/009** | Enredo de duplicados: `converted/VIGIA-2026-DEMO-00X.json` y un gemelo canónico con OTRO stem (`case_006_false_flag_demo`, `case_009_insomnio_tactico_es`) comparten `case_id`; find_cases dedupea por stem, el snapshot por case_id last-wins | elegir el gemelo canónico (no-lossy) como ganador, o borrar las copias converted/ lossy | Es **higiene de corpus**, no motor — el dossier (§4) ya marcó "decidir cuál duplicado es canónico antes de cualquier freeze". Requiere resolver los 5 duplicados de forma consistente, no caso por caso. Merece su propia mini-sesión de hygiene. |
| LINUX-008 | Mismo masquerade del hermano 006, pero en **texto libre** de la descripción, no en metadata | agregar `malicious_path`/`legitimate_path` a su metadata (mirroring 006) | Autoría de metadata NUEVA (no corrección de tipo) — más cerca de fitting. Diferido. |
| MAGNET-2014-TIMELINE | 4 artefactos `file_timestamp` → un solo dominio; RECOVERABLE-RISKY | retipar docx/prefetch | Retipo debatible; diferido. |

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

## 7. Resumen de decisiones que te quedan (para las próximas sesiones)

1. **MAGNET-2020 netscan retype** (+1): retipo legítimo, pero el caso tiene
   doctrina INTENT-sin-ocultamiento — ¿aplico el retipo aunque empuje a MALICE?
   (§3.2). Tu decisión por la sensibilidad B-114.
2. **DEMO-004/007/009 hygiene** (+3): resolver los 5 case_id duplicados de forma
   consistente (mini-sesión de higiene de corpus, §3.2).
3. **B-115 data repair (D-2)**: re-anclar `metadata.*_time` en los ~26 casos
   canonical_v2. Independiente; algunos B-115 restantes solo se recuperan así.
4. **Reetiquetas de doctrina** (case_024→SUSPICION, CTF-Eli→etiqueta,
   JESS/RAFAEL como INTENT-honesto-SUSPICION): anotación, no motor.
5. **Dejar quietos** los UNFIXABLE (§5) — recuperarlos sería forzar.

Techo realista sin forzar y sin tocar labels: **~167/193** (163 actual + 1
MAGNET-2020 + 3 DEMO). El resto son decisiones de doctrina/etiqueta o
genuinamente ABSTAIN/SUSPICION correctos. **Implementado esta sesión: +8
(155→163), 5 detectores TTP nuevos + 1 gate ABSTAIN + rúbrica CAN-008/047, todo
FP-safe verificado, cero golden rules removidas.**

---

*Detectores verificados FP-safe por el workflow wf_58d740be-8ce (verificación
adversarial independiente por detector) + medición combinada corpus-wide del
agente principal. Cero golden rules removidas. Restore tag de sesión:
`pre-session-20260712-005232`.*
