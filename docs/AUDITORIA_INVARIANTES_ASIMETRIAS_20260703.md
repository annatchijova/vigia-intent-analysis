# Auditoría — Invariantes, asimetrías y estados imposibles (9 lentes)

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Método:** barrido dirigido por 9 lentes de auditoría (invariantes, asimetrías,
ramas imposibles, inconsistencias semánticas, estados imposibles, algoritmos
duplicados, dependencias ocultas, acoplamiento accidental, nombres engañosos),
cada hallazgo **verificado por lectura + reproducción**. VIGÍA es open source
y forense: la barra es cero bugs que puedan producir un veredicto incorrecto o
comprometer la cadena de custodia.
**Acción:** los dos hallazgos P1 se corrigieron en esta sesión (commits
citados). Los P2/P3 se documentan con propuesta — varios son decisiones de
doctrina (como B-013) que no corresponde que resuelva el auditor solo.

---

## Resumen

| ID | Lente | Severidad | Estado | Título |
|----|-------|-----------|--------|--------|
| **B-057** | 4/5 | **P1** | ✅ FIXED | `Decimal * float` crashea el scorer con fracturas CAIE vivas |
| **B-058** | 1/4/6 | **P1** | ✅ FIXED | `ABSTAIN_DETECTED` clasificaba NOISE; el batch lo enmascaraba |
| **B-059** | 4/6 | P2 | 📋 DOC | Etiqueta ENFSI divergente entre bundle sellado y reporte judicial (3 impls) |
| **B-060** | 7/8 | P3 | 📋 DOC | Tipos mobile ausentes de los mapas CAIE/adapter → default silencioso |
| **B-061** | 4 | P3 | 📋 DOC | `confidence` fuera de rango: rechazo (pydantic) vs clamp (fallback) |
| **A-1** | 2 | P3 | 📋 DOC | `daubert_record_hash` creado, nunca verificado por ningún consumidor |
| **A-2** | 2 | P3 | 📋 DOC | `activate_honey_token` sin desactivación/reset (modo MCP) |

Nota metodológica: este barrido fue dirigido, no exhaustivo sobre todo el
árbol. Áreas de mayor riesgo (path de veredicto, sellado, boundaries de tipo)
recibieron foco; `vigia/pipeline/`, `engine/` y las tools MCP recibieron
cobertura parcial.

---

## P1 — CORREGIDOS

### B-057 — `Decimal * float` crashea `_vigia_score` (Lente 4/5)

`vigia_scorer.py:636` (y `:646`). Las fracturas del **CAIE vivo** llevan
`severity` como `decimal.Decimal` (aritmética interna de `caie.py`); las del
fallback JSON llevan `float`. `sev * 0.45` con `sev` Decimal → `TypeError:
unsupported operand type(s) for *: 'decimal.Decimal' and 'float'` → crash de
`_vigia_score` **entero** en cuanto CAIE emite una fractura maliciosa.

- **Invariante violada:** ningún boundary de tipo del path de scoring debe
  mezclar Decimal y float en aritmética cruda (misma familia B-024/B-026).
- **Escenario:** `[REPRODUCIDO]` con `VIGIA-BREAK-016` (expected MALICE). El
  caso **siempre** devolvió `MALICIOUS_INTENT_DETECTED` / exit code 1,
  verificado contra el bundle del 15 de junio (analysis_timestamp 01:18 UTC).
  El crash no enmascaraba el veredicto: el TypeError se activa sólo cuando
  CAIE emite fracturas maliciosas y el scorer llega a la multiplicación
  `sev * 0.45` — el path de scoring puede terminar antes si las condiciones
  de corte se cumplen antes. El fix es **preventivo**, no correctivo de un
  veredicto erróneo existente: sin él, cualquier caso nuevo donde el scorer
  alcance esa línea con severity Decimal haría crash.
- **Fix (commit posterior a Tanda B):** helper `_sev_float()` (coerción +
  Finite Math Shield: `float()`, `isfinite`, clamp [0,1]) en el boundary de
  fracturas y violations. Comparativa 198 casos: sin flips de veredicto (el
  corpus ya era correcto). Tests: `test_b057_decimal_severity.py` (6).

### B-058 — `ABSTAIN_DETECTED` sellaba NOISE; el batch lo ocultaba (Lente 1/4/6)

`vigia_agent.py:160` (`classify_agent_verdict`). El match era **exacto**
contra `ABSTAIN_HYPOTHESES`, pero el adaptador EBS emite `"ABSTAIN_DETECTED"`
(`sift_orchestrator.py:625`, cuando `expected_verdict == "ABSTAIN"`), que **no
estaba** en el frozenset → caía a `NOISE` (exit 0).

- **Invariante violada (Lente 1):** toda hipótesis que el sistema etiqueta
  ABSTAIN debe clasificar ABSTAIN, nunca NOISE. Es la familia P0-A:
  incapacidad de determinar presentada como benignidad.
- **Divergencia semántica (Lente 4/6):** `run_all_agent.py:86` mapea
  `ABSTAIN_DETECTED → ABSTAIN` en **su propio** comparador (leyendo
  `best_hypothesis`, NO el `agent_verdict` sellado). Dos caminos de mapeo de
  veredicto: el batch daba **PASS** sobre un bundle cuyo `agent_verdict` era
  NOISE. El bug era invisible en el corpus 198/198.
- **Escenario:** `[REPRODUCIDO]` — `VIGIA-AMB-001` (expected ABSTAIN, 3
  señales): bundle sellado `agent_verdict=NOISE`, exit 0. `VIGIA-FP-002` se
  salvaba solo por accidente (2 señales < 3 → gate de corroboración).
- **Fix:** match por **substring** `"ABSTAIN"` (simétrico a MALICE/INTENT).
  Tests: `test_b058_abstain_classification.py` (4). Corpus sigue 198/198,
  ahora VIGIA-AMB-001 sella ABSTAIN por la vía correcta.
- **Recomendación adicional (no aplicada):** el comparador de
  `run_all_agent.py` debería leer `agent_verdict` sellado, no re-derivar el
  veredicto de `best_hypothesis` — así el batch nunca podría enmascarar una
  divergencia del clasificador. Candidato a fix P2.

---

## P2 — DOCUMENTADOS (decisión de doctrina)

### B-059 — Etiqueta ENFSI divergente: bundle sellado vs reporte judicial (Lente 4/6)

**Tres** implementaciones de `enfsi_label` con umbrales distintos:

1. `vigia/core/ebs_v1.py:786` — 8 buckets, inglés. Alimenta
   `ForensicRecord.enfsi_label` (**sellado en el bundle**) vía
   `likelihood_ratio.py:300`, y `vigia_integration_bridge.py:961`.
2. `vigia/tools/signal_contract.py:222` — 5 buckets, español.
3. `forensics/evidence_narrative_gen.py:73` (`_enfsi_label`, `ENFSI_SCALE`
   `:55`) — 7 buckets bilingüe. Genera el **reporte que lee un tribunal**
   (`:781`).

`[REPRODUCIDO]` — mismo LR, etiqueta distinta entre el bundle sellado y el
reporte judicial:

| LR | bundle sellado (ebs_v1) | reporte judicial (narrative_gen) |
|----|-------------------------|----------------------------------|
| 5 | **limited** | **weak** support |
| 500 | **moderately strong** | **strong** support |
| 50 / 5000 / 50000 | (coinciden por casualidad) | |

- **Riesgo Daubert:** un perito contrario cruza el bundle sellado
  ("limited") contra el reporte firmado ("weak") para el mismo likelihood
  ratio. Para una herramienta forense open source cuyo valor es la
  admisibilidad, es una inconsistencia citable.
- **Propuesta (decisión de doctrina, no la resuelve el auditor):** definir
  UNA escala ENFSI canónica (la escala verbal estándar ENFSI 2015 tiene
  límites específicos) en un solo módulo y que las tres la consuman.
  Requiere decidir cuál es la correcta — probablemente un `enfsi.py` con la
  tabla oficial + los tres call sites delegando. Sin cambiar el número, es
  una unificación de ~40 líneas.

---

## P3 — DOCUMENTADOS

### B-060 — Tipos mobile ausentes de los mapas CAIE/adapter (Lente 7/8)

`vigia/core/forensic_adapter.py:76,85,114` (`_LAYER_MAP`, `_EVIDENCE_MAP`,
`_ONTOLOGY_MAP`) NO contienen `macos_forensic`, `android_forensic`,
`ios_forensic`, `google_takeout`. Cuando una señal mobile entra a CAIE:
- `_LAYER_MAP.get("macos_forensic", EvidenceLayer.DISK_MFT)` → default
  silencioso a DISK_MFT (capa epistémica equivocada).
- `_EVIDENCE_MAP.get(...)` → usa el tipo crudo, que no matchea
  `EVIDENCE_PROFILES` → perfil default (spoofability 0.50).

- **Dependencia oculta (Lente 7):** el productor (motor mobile) y el
  consumidor (CAIE) coinciden solo por convención, sin contrato.
- **Acoplamiento accidental (Lente 8):** agregar un motor nuevo requiere
  tocar ≥4 mapas separados (adapter ×3, `reasoner.layer_map`, CAIE profiles)
  sin ningún enforcement — la fuente exacta del bug B-052/macOS.
- **Mitigante:** en Mode 1 la evidencia mobile va por la ruta mobile-only del
  shim y no llega a CAIE (solo en evidencia mixta). Degradación conservadora.
- **Propuesta:** un registro único `ARTIFACT_TYPE_REGISTRY` (tipo → layer,
  evidence_type, ontology, gamma) que todos consuman, o al menos un test que
  falle si un `artifact_type` emitido por algún motor no está en todos los
  mapas.

### B-061 — `confidence` fuera de rango: rechazo vs clamp según config (Lente 4)

`vigia/core/ebs_v1.py`: con pydantic (`_USE_PYDANTIC`), `SignalOutput.confidence`
tiene `Field(le=1.0)` → **rechaza** con `ValidationError`. Sin pydantic, el
dataclass fallback (`:130-133`) **clampea** `max(0, min(1, ...))`.

- **Inconsistencia semántica:** el mismo input (`confidence=2.0`) crashea en
  un despliegue y se corrige en silencio en otro. `[REPRODUCIDO]`: pydantic →
  ValidationError; fallback → 1.0.
- **Riesgo:** código que asume el clamp (2.0→1.0) rompe bajo pydantic; código
  que asume el rechazo acepta datos corruptos bajo el fallback. Determinismo
  cross-deployment comprometido para inputs inválidos.
- **Propuesta:** unificar a clamp en ambos (fail-safe, coherente con `z_score`
  que ambos clampean), o a rechazo en ambos (fail-loud). Recomiendo **clamp**
  en ambos — coherente con el tratamiento de `z_score`, que las dos rutas
  clampean sin rechazar.

### A-1 — `daubert_record_hash` creado, nunca verificado (Lente 2)

`vigia/tools/signal_adapter.py:624` embebe `record_hash()` como
`"daubert_record_hash"` "para peritaje". Ningún consumidor en el árbol lo
**verifica** (grep: solo la definición en `likelihood_ratio.py:140` y este
call site). Asimetría hash-creado-sin-verificar: es un hash decorativo — se
presenta como garantía de integridad pero nada lo chequea.

- **Propuesta:** o un verificador (aunque sea el runner stdlib de
  `verify_tool_log.py`) que recompute y compare, o documentar explícitamente
  que es un anchor para verificación externa manual (como hace el bundle
  `.sha256`). Sin verificador ni doc, aparenta una garantía que no da.

### A-2 — `activate_honey_token` sin desactivación (Lente 2)

`vigia/vigia_sift_bridge.py:2629` activa un tripwire (estado); no hay
`deactivate_honey_token` / reset / expiry. En modo MCP de larga vida, los
tripwires se acumulan sin forma de limpiarlos. Severidad baja (Mode 2,
fuera del core determinista), pero es una asimetría add-sin-remove sobre
estado.

---

## Invariantes verificadas que SÍ se cumplen (para el registro)

Para no dar falsa alarma, estas se chequearon y están bien:
- `SignalOutput.z_score` se clampea a `[-Z_CLIP_MAX, Z_CLIP_MAX]` en **ambas**
  rutas (pydantic y fallback). ✅
- El guard B-027 (`_seal_bundle`) degrada `is_conclusive` en veredictos
  ABSTAIN — verificado que es el único punto de sellado del agente. ✅
- Las dos `_EXP_NEG2_TABLE` (scorer y trust_fusion, agregada en Tanda B)
  son **idénticas** bucket a bucket. ✅
- El write atómico del bundle (L-023, Tanda A) verifica hash-desde-disco. ✅
- `_forensic_mounts` (L-024) excluye symlinks correctamente. ✅

---

## Limitaciones de esta auditoría

1. Barrido dirigido a las áreas de mayor riesgo, no exhaustivo sobre todo el
   árbol. `vigia/pipeline/`, `engine/`, `vigia/governance/` y varias tools
   MCP recibieron cobertura parcial.
2. Los tres agentes de exploración paralela lanzados para los 9 lentes fueron
   cancelados a mitad de corrida (interrupciones de sesión); los hallazgos de
   este documento provienen del barrido directo del auditor principal, que ya
   había producido B-057 y B-058 de forma independiente.
3. B-059 (escala ENFSI) requiere decisión de doctrina forense sobre cuál
   escala es la canónica — no corresponde resolverla unilateralmente.

---

*Auditoría de invariantes — dos P1 corregidos (un crash que enmascaraba un
MALICE, un ABSTAIN que se sellaba NOISE mientras el batch decía PASS), y cinco
hallazgos menores documentados. Para un forense open source, el más grave era
el silencioso: el batch verde sobre un veredicto incorrecto.*
