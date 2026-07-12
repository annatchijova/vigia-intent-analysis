# Alcance — Sesión de re-puntuación de datos (CAN-008, CAN-046, CAN-047)

**Estado:** planificado, NO iniciado. Este documento es el punto de partida
para arrancar esa sesión como bloque aparte, sin re-derivar el diagnóstico.
Ningún `raw_score` fue tocado hoy — motor y datos siguen como quedaron tras
`docs/IMPL_20260712_M1_M3_M2.md`.

**Por qué es una sesión distinta:** M1/M3/M2 (hoy) corrigieron reglas del
motor — código, sin re-autoría de evidencia. Esto es lo opuesto: cambiar
`raw_score` en artefactos ya sellados es una decisión de **contenido**
forense (¿qué tan fuerte es esta señal, realmente?), no de mecánica del
scorer. Requiere su propio criterio de revisión, explícitamente separado del
de hoy (pedido del usuario, D-5).

**Por qué no se resuelve solo:** los tres casos cayeron a SUSPICION como
efecto automático de M2 (el fósil `FALSE_FLAG_PATTERN` que los sostenía dejó
de disparar sobre datos mal tipados). Eso es correcto y no se revierte. Pero
SUSPICION no es el veredicto final aceptado — es el estado mientras el
`raw_score` de la señal central de cada caso siga invertido respecto de su
propia narrativa (ver diagnóstico por caso abajo, ya completo desde
`docs/D5_RETIPADO_SUBGRUPO_C_20260712.md`).

---

## Los 3 casos, diagnóstico ya cerrado (no re-derivar)

### CAN-008 (case_090_anacronismo_herramienta) — exp. MALICE

> "PsExec v1.94 (2014) detected on a Windows 2025 server... Memory analysis
> reveals a kernel rootkit with SSDT hooks installed 2 minutes earlier. **The
> psexec is the decoy.**" — notes: "The noisy tool is the decoy. The silent
> one is the real attack."

| Artefacto | Tipo actual | raw actual | Rol narrativo | Inversión |
|---|---|---|---|---|
| a090_01 | file_hash | 0.65 | psexec.exe — el señuelo ruidoso | correcto (señuelo, score medio-alto por ruido EDR, no por peligrosidad) |
| a090_02 | cultural_marker | 0.91 | 12 alertas EDR marcadas FP por Tier-1 | ok como señal de "ruido", tipo ya corregido por D-5 a `log_entry` |
| **a090_03** | **memory_process** | **0.05** | **el rootkit de kernel con 12 SSDT hooks — el ataque real** | **SÍ — señal central del caso a raw casi cero** |
| a090_04 | dns_record | 0.82 | C2 cifrado 1 min antes del ruido psexec | correcto |

Retipado ya medido y disponible (D-5, no aplicado — depende de esta sesión):
`a090_02 cultural_marker→log_entry`; `a090_03 memory_process→kernel_structure`;
`a090_04 dns_record→network_flow`.

Nota adicional diagnosticada: `a090_04` trae `firewall_claim=true` sin
`traffic_type`/`open_sockets` — la regla legítima NETWORK_VS_HOST tampoco
puede disparar con la metadata actual. Revisar si corresponde completarla en
la misma sesión (dato menor, no re-autoría de score).

### CAN-046 (case_024_paracaidista) — exp. MALICE

> "Binary system_updater.elf with crtime/mtime/atime identical to legitimate
> files in /usr/bin, but ctime (inode change time) from 3 hours ago —
> **timestomping detected**." — notes: "the attacker copied dates from a
> legitimate file but forgot to alter ctime."

| Artefacto | Tipo actual | raw actual | Rol narrativo | Inversión |
|---|---|---|---|---|
| a024_stat | file_timestamp | 0.92 | stat mtime/atime/crtime idénticos a /usr/bin/ls | correcto |
| a024_inode | file_timestamp | 0.88 | inode recién asignado, inconsistente con timestamp "viejo" | correcto |
| a024_exec | cultural_marker | 0.91 | ejecución root + reverse shell | tipo mal puesto (ya corregido por D-5 a `log_entry`), score razonable como evento |
| **a024_hash** | **memory_process** | **0.06** | **hash sin match + entropía 7.8 (código custom compilado) — la prueba técnica dura del binario malicioso** | **SÍ — señal central a raw casi cero** |

Retipado ya medido (D-5, no aplicado): `a024_exec cultural_marker→log_entry`;
`a024_hash memory_process→file_hash`.

Complicación adicional (ya diagnosticada, PASS2/IMPL): el motor tiene 3
reglas específicas de timestomping (Rule 1b, `TIMESTAMP_PRECISION_ANOMALY`,
`MFT_ENTRY_ANOMALY`) y la metadata de este caso no alimenta ninguna de las
tres (sin `timestomp_detected`, sin `mft_entry_number`, sin patrón de 7
ceros en el timestamp). Re-medido específicamente post-M3: **no se recupera
ni completando `timestomp_detected=True`** en los artefactos de timestamp —
la Rule 1b exige que el bucket técnico (memoria/kernel) tenga avg>0.5, y hoy
ese bucket es solo `a024_hash` a raw 0.06. Esta sesión probablemente necesita
decidir DOS cosas, no una: el raw_score Y si corresponde completar flags de
metadata de timestomping.

### CAN-047 (case_026_ventrilocuo) — exp. MALICE

> "Legitimate svchost.exe process running. Everything looks normal. But it
> maintains a persistent connection to an IP in an unusual country on port
> 443. **Process hollowing detected**." — notes: "Very strong, very EDR. The
> OS believes it is svchost.exe but executes the attacker's code."

| Artefacto | Tipo actual | raw actual | Rol narrativo | Inversión |
|---|---|---|---|---|
| **a026_process** | **memory_process** | **0.07** | **sección .text con permisos RWX — anómalo para un proceso legítimo** | **SÍ** |
| a026_network | ip_geolocation | 0.82 | conexión TCP persistente 72h a IP no clasificada (Bielorrusia) | correcto, ya retipado por D-5 a `network_flow` |
| **a026_parent** | **log_entry** | **0.07** | **parent process anómalo (rundll32 en vez de services.exe) — indicador de inyección** | **SÍ** |
| a026_pe | file_hash | 0.85 | entry point desplazado, sección .text reescrita | correcto |

Retipado ya medido (D-5, no aplicado): `a026_network
ip_geolocation→network_flow`. **Este caso es el más dependiente de
re-puntuación del grupo**: dos de las tres señales técnicas duras del
hollowing (RWX, parent anómalo) están invertidas, no solo una.

---

## Qué NO es esta sesión

- No es "subir los raw_score hasta que dé MALICE otra vez". Eso sería
  calibración circular a la etiqueta esperada — exactamente el vicio que
  toda la cacería de fósiles vino a erradicar. El criterio tiene que ser
  independiente del veredicto de salida: ¿qué raw_score refleja honestamente
  la fuerza de ESTA evidencia según la doctrina de `EVIDENCE_PROFILES`
  (spoofability/weight por tipo), no cuánto hace falta para cruzar 0.33?
- No es tocar `evidence_type` de nuevo — eso ya está medido y documentado en
  `docs/D5_RETIPADO_SUBGRUPO_C_20260712.md`; esta sesión hereda esos mapas.
- No es reetiquetar `expected_verdict` — esa es la salida del criterio CAN-026
  (aceptar SUSPICION si el caso genuinamente no llega), a considerar SOLO si
  tras re-puntuar honestamente el caso sigue sin alcanzar MALICE.

## Qué SÍ es esta sesión

1. Para cada uno de los 3 (más CAN-046 con su complicación de flags), decidir
   un `raw_score` para el artefacto de señal central que refleje su rol
   narrativo, con criterio explícito y documentado (no solo "un número que
   funcione").
2. Aplicar el retipado ya medido (D-5) junto con el nuevo raw_score, en una
   sola edición por caso.
3. Medir en aislamiento con `_vigia_score` ANTES de aceptar (mismo protocolo
   CAN-026/D-5) — puede que incluso con dato honesto alguno no cruce el
   umbral; ese resultado también es válido y se documenta, no se fuerza.
4. Para CAN-046 específicamente: decidir además si corresponde completar
   `timestomp_detected`/metadata de MFT, con su propio razonamiento (no
   "porque hace falta para que dispare la regla").
5. Actualizar `tests/caie/test_canonical_cases.py::KNOWN_PENDING` — sacar del
   mapa xfail los casos que efectivamente se resuelvan, dejar los que no con
   su nueva razón documentada.

## Herramientas ya listas para usar

- `scripts/experiments/scorer_gate.py` — ablación/diff narrativo sobre el
  motor real.
- Protocolo de medición aislada de `docs/D5_RETIPADO_SUBGRUPO_C_20260712.md`
  (variante en memoria → `_vigia_score` → aceptar solo si mide bien).
- `EVIDENCE_PROFILES` en `vigia/tools/caie.py` como referencia de
  spoofability/weight por tipo, para calibrar el nuevo raw_score contra la
  doctrina existente en vez de a ojo.
