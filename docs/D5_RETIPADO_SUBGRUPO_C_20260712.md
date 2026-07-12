# D-5 — Retipado del subgrupo C con medición aislada por caso (2026-07-12)

**Protocolo:** el de CAN-026 — cada caso se retipa en una variante en memoria,
se mide contra el motor real (`_vigia_score`) ANTES de aceptar, y si el caso no
se recupera con el retipado, NO se fuerza: se reporta para decisión caso por
caso. No se asume que los 5 se comportan igual por compartir el síntoma.

**Criterio de recuperación:** (a) `FALSE_FLAG_PATTERN` deja de disparar en la
variante retipada, (b) el veredicto sigue MALICE con rama de corroboración
R4-3 abierta, (c) el MALICE resultante no cuelga de una fractura fósil nueva.

**Alcance del retipado:** solo `evidence_type` de artefactos claramente mal
tipados. Sin cambios de `raw_score`, descripciones ni metadata (re-puntuar
evidencia es re-autoría, fuera del mandato D-5).

---

## Resultado: 1 de 5 se recupera

| Caso | Retipado probado | Antes | Después | ¿Recupera? | Acción tomada |
|---|---|---|---|---|---|
| VIGIA-CAN-024 (mimesis_error_administrativo) | a106_01 file_hash→document_visual; a106_02 cultural_marker→log_entry; a106_03 dns_record→log_entry; a106_04 memory_process→file_hash | MALICE 0.5807 vía FALSE_FLAG_PATTERN | **MALICE 0.5834 vía DOCUMENT_FORGERY** (sev 0.9), rama cross-domain (3 dominios, 4 artefactos) | **SÍ** | **APLICADO** al archivo del caso, con `_retype_note`; `signals` intacto como snapshot pre-retipado |
| VIGIA-CAN-008 (anacronismo_herramienta) | a090_02 cultural_marker→log_entry; a090_03 memory_process→kernel_structure; a090_04 dns_record→network_flow | MALICE 0.5553 | SUSPICION 0.1874, 0 fracturas | **NO** | Sin tocar — reporte abajo |
| VIGIA-CAN-011 (deepfake_estilo) | a093_01 cultural_marker→log_entry; a093_02 memory_process→log_entry | MALICE 0.6237 | SUSPICION 0.2420, 0 fracturas | **NO** | Sin tocar — reporte abajo |
| VIGIA-CAN-046 (paracaidista) | a024_exec cultural_marker→log_entry; a024_hash memory_process→file_hash | MALICE 0.5821 | SUSPICION 0.2203, 0 fracturas | **NO** | Sin tocar — reporte abajo |
| VIGIA-CAN-047 (ventrilocuo) | a026_network ip_geolocation→network_flow | MALICE 0.5509 | SUSPICION 0.1970, 0 fracturas | **NO** | Sin tocar — reporte abajo |

CAN-024 verificado desde disco tras aplicar: bit-idéntico a la medición aislada
(0.5834, DOCUMENT_FORGERY, cross-domain). La fractura que ahora sostiene el
veredicto es la teoría verdadera del caso (documento adulterado con
`digital_perfection_detected` declarado por el análisis) — sobrevive
cross-examination.

## Por qué NO recuperan los otros 4 (diagnóstico caso por caso)

**Raíz común, pero no idéntica:** el retipado corrige el TIPO, pero en estos 4
los `raw_score` están autorados **al revés de su propia narrativa** — la señal
que el caso declara como central lleva raw 0.05–0.07, y los señuelos/context
llevan 0.65–0.92. Corregir eso es re-puntuar evidencia (re-autoría), no
retipado. Detalle:

- **CAN-008:** el rootkit de kernel (12 SSDT hooks — la historia del caso) es
  `a090_03` con raw **0.05**; el señuelo psexec lleva 0.65 y las alertas EDR
  0.91. Con raw realista en `kernel_structure` (w=0.35, sp=0.10) el caso
  probablemente cruza 0.33 con rama hard-mass. Nota adicional: `a090_04` trae
  `firewall_claim=true` pero sin `traffic_type`/`open_sockets`, así que la
  regla legítima NETWORK_VS_HOST tampoco puede disparar con la metadata actual.
- **CAN-011:** el más cerca del umbral (0.242 vs 0.33). Su evidencia central es
  **estilometría** (TTR 0.992 vs varianza humana 0.82) — no existe tipo
  canónico para señal estilométrica; es exactamente la clase
  `attribution_genuine` de la taxonomía M2. **Recuperación natural: la
  fractura nueva `LINGUISTIC_ATTRIBUTION_SIGNAL` del diseño M2, no el
  retipado.** Recomiendo no tocar datos y dejar que M2 lo levante mañana;
  si tras M2 no llega, recién ahí decidir dato.
- **CAN-046:** doble causa. (a) raw invertido: hash sin match en repo +
  entropía 7.8 lleva raw **0.06**. (b) El motor tiene TRES reglas específicas
  para timestomping (Rule 1b, TIMESTAMP_PRECISION_ANOMALY, MFT_ENTRY_ANOMALY)
  y la metadata del caso no alimenta ninguna (sin `timestomp_detected`, sin
  `mft_entry_number`, sin patrón de 7 ceros) — y la que podría disparar via
  Rule 1b emite FALSE_FLAG_ATTRIBUTION_MISMATCH, que hoy pesa 0 en el scorer
  (M3). Camino de recuperación: fix M3 + completar flags de metadata (dato
  menor pero dato al fin) — decisión tuya.
- **CAN-047:** las tres señales duras del hollowing (sección RWX, parent
  rundll32, PE desplazado) llevan raw 0.07/0.07/0.85 — dos de tres invertidas.
  Sin re-puntuación no hay camino: es el caso más dependiente de re-autoría
  del grupo.

## Estado interino y pendientes

- Los 4 no-recuperados quedan **sin tocar**: hoy siguen MALICE vía el fósil M2
  (aún activo). Cuando el fix M2 aterrice, caerán a SUSPICION salvo decisión
  previa. Opciones por caso: re-puntuar raw (re-autoría de dato), reetiquetar
  expected (criterio CAN-026), o —solo CAN-011— esperar la fractura nueva de M2.
- El mapa de retipado probado de los 4 queda documentado arriba: si decidís
  re-puntuar, el retipado ya medido se aplica en la misma operación.
- Reproducibilidad: mediciones con `_vigia_score` real; ablaciones con
  `scripts/experiments/scorer_gate.py`. Corpus fuera de estos 5 casos: sin
  cambios (la edición es local al dato de CAN-024).

**Actualización 2026-07-12 (post-M2):** M2 aterrizó (ver
`docs/IMPL_20260712_M1_M3_M2.md`). Resultado por caso:

- **CAN-011:** recuperado sin re-autoría — `LINGUISTIC_ATTRIBUTION_SIGNAL` lo
  levanta a MALICE con score bit-idéntico. Cerrado.
- **CAN-046:** re-medido específicamente post-M3 (a pedido explícito) — NO se
  recupera, ni siquiera completando `timestomp_detected=True`. Se une a
  CAN-008/CAN-047 en el punto siguiente.
- **CAN-008 y CAN-047:** cayeron a SUSPICION como efecto automático de M2 (el
  fósil que los sostenía ya no dispara). **Esto no es un veredicto final
  aceptado sobre estos dos casos** — es un estado transitorio mientras el
  raw_score siga sin corregir (inversión flagrante ya diagnosticada arriba:
  rootkit con 12 SSDT hooks / sección RWX del hollowing a raw 0.05-0.07).
  Quedan para la sesión de re-puntuación de datos, aparte, con su propio
  criterio de revisión — no decidir por omisión que "son SUSPICION porque así
  es el caso".
