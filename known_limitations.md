# VIGÍA — Known Limitations

## Versión: EBS v1 | Actualizado: 2026-05-03

Estas limitaciones son documentadas deliberadamente como parte del estándar
Daubert de falsificabilidad. VIGÍA no pretende ser infalible — pretende ser
auditable.

---

## L-001 — Ataque Perfecto Sin Anomalías (BREAK_006)

**Descripción:** Cuando un atacante ejecuta una operación sin errores
técnicos (credenciales válidas, timestamps consistentes, sin herramientas
detectables), VIGÍA tiende a emitir SUSPICION en lugar de MALICE.

**Causa:** El motor de scoring depende de anomalías estructurales y
fractures CAIE. Sin inconsistencias, el score no supera el umbral MALICE.

**Implicación forense:** VIGÍA es más efectivo detectando ataques con
errores operacionales que APT de nivel alto con OPSEC perfecto.

**Workaround:** Combinar con análisis de comportamiento basal
(baselines_institucionales.yaml) para detectar desvíos estadísticos.

---

## L-002 — Señal Crítica Ahogada en Ruido (BREAK_004)

**Descripción:** Cuando hay muchos artefactos irrelevantes y pocos
artefactos críticos, el score promedio baja y VIGÍA emite SUSPICION
en lugar de MALICE.

**Causa:** El agregador de evidencia no implementa aún ponderación
dinámica por tipo de artefacto. Todos los artefactos tienen peso inicial
similar antes de ajuste por trust.

**Implicación forense:** En casos con mucho ruido, se recomienda
pre-filtrar artefactos por relevancia antes de ingresar al pipeline.

---

## L-003 — Ausencia de Logs Como Evidencia (BREAK_007)

**Descripción:** La ausencia de registros donde deberían existir (e.g.,
sesión SSH presente en netflow pero sin entrada en auth.log) no genera
suficiente señal para alcanzar MALICE.

**Causa:** El modelo actual trata evidencia ausente como ruido neutro,
no como señal positiva de manipulación.

**Implicación forense:** La detección de "silencio significativo" requiere
comparación contra baselines institucionales. Sin baseline configurado,
VIGÍA no puede evaluar ausencias.

---

## L-004 — Prompt Poison / Narrativa Engañosa (BREAK_009)

**Descripción:** Cuando un artefacto de texto contiene afirmaciones
como "caso ya confirmado benigno por el equipo", VIGÍA no distingue
entre texto narrativo no verificado y evidencia técnica estructurada.

**Causa:** El LLMShield filtra inyecciones directas al motor de
razonamiento, pero no neutraliza narrativas engañosas embebidas en
artefactos de tipo texto libre.

**Implicación forense:** Todo artefacto de tipo texto libre debe ser
tratado con trust reducido manualmente. No confiar en afirmaciones
no verificables dentro de evidencia.

**Referencia:** Austin (1962) — actos de habla performativos falsos.
Un texto que dice "esto es benigno" no convierte la evidencia en benigna.

---

## L-005 — Umbral de Veredicto vs. Evidencia Ambigua (BREAK_002, BREAK_005)

**Descripción:** Casos con actividad sospechosa pero autorizada (pentest
documentado) o eventos simultáneos sin relación causal producen SUSPICION
o UNKNOWN en lugar de veredictos más precisos.

**Causa:** VIGÍA no tiene acceso a contexto organizacional externo
(tickets, autorizaciones, políticas) durante el análisis automático.

**Implicación forense:** Para casos con contexto de autorización, el
analista debe revisar el veredicto SUSPICION/UNKNOWN manualmente e
incorporar el contexto en el reporte final.

---

## L-006 — Inconsistencia Temporal Única (BREAK_001)

**Descripción:** Un único artefacto con timezone inconsistente entre
tres artefactos alineados produce MALICE, cuando el esperado podría
ser mayor incertidumbre.

**Causa:** El hard gate EFFECT_BEFORE_CAUSE y la penalización por
inconsistencia temporal son agresivos por diseño — priorizan falsos
positivos sobre falsos negativos en contexto forense.

**Decisión de diseño:** En forense, es preferible investigar un caso
que resultó benigno que ignorar uno que resultó malicioso. Este
comportamiento es intencional.

---

## Resumen

| ID | Caso | VIGÍA | Esperado | Tipo |
|----|------|-------|----------|------|
| L-001 | BREAK_006 | SUSPICION | MALICE | Limitación real |
| L-002 | BREAK_004 | SUSPICION | MALICE | Limitación real |
| L-003 | BREAK_007 | SUSPICION | MALICE | Limitación real |
| L-004 | BREAK_009 | UNKNOWN | MALICE | Limitación real |
| L-005 | BREAK_002/005 | UNKNOWN/SUSPICION | NOISE/UNKNOWN | Discutible |
| L-006 | BREAK_001 | MALICE | UNKNOWN | Decisión de diseño |

