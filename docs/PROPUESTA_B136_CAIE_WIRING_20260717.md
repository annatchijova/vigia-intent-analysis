# Propuesta B-136 — Cableado de las inyecciones CAIE (Opción 1)

**Estado:** PROPUESTA — requiere aprobación del colectivo antes de tocar el
decision path. Este documento NO modifica código de scoring.
**Fecha:** 2026-07-17
**Origen:** verificación adversaria de Kimi (Finding 6 / B-136), que confirmó
por inducción que los cuatro sitios de inyección CAIE fuera del scorer son
no-ops estructurales, y endosó la Opción 1 con cuatro condiciones.
**Disciplina aplicable:** §5 (valores en el decision path) y §6 (revisión
adversaria) de CLAUDE.md. Los números de spoofability/weight de abajo son
RECOMENDACIONES calibradas por analogía, no decisiones tomadas: entran al
decision path solo tras sign-off del colectivo + corrida comparativa de corpus.

---

## 1. Qué arregla la Opción 1

Hoy, cuatro sitios instancian un `CrossArtifactIncongruenceEngine` local,
le agregan artefactos y lo descartan sin llamar `detect_fractures()`. El
resultado es señal forense real (estilometría, entanglement de lote, fraude
temporal) que se pierde, con logs de éxito engañosos en la audit trail.

| Sitio | evidence_type | Estado hoy | Dominio de la señal |
|-------|---------------|-----------|---------------------|
| `vigia/tools/adversarial_nlp.py:1599` | `linguistic_forensics` | kwargs correctos, engine descartado, log `CAIE_INJECTION_FAILED` en except | Estilometría / incongruencia lingüística de un documento |
| `vigia/core/entanglement.py:601` | `batch_forensics` | kwargs erróneos → TypeError, log `ENTANGLEMENT_CAIE_FAILED` | Entanglement cross-documento (factory production) |
| `vigia/forensics/temporal_forensics_redteam.py:743` | `temporal_fraud` | kwargs erróneos → TypeError, `log_error` | Fraude temporal intra-documento |
| `vigia/tools/vision_audit.py:543/552` | `document_visual` / `document_geometry` | kwargs correctos, tipos válidos, engine descartado, log `CAIE_ARTIFACT_INJECTED` (falso éxito) | Ya tienen perfil (P3) |

Opción 1: enrutar estas fracturas al stream de artefactos/señales del caso
(el que consume el scorer), borrar los cuatro bloques de engine local y sus
logs de éxito falsos.

**Por qué NO el fix mecánico de kwargs (refutado por Kimi, verificado):**
corregir solo los kwargs convierte el fallo honesto en éxito falso. El sitio
`vision_audit` lo prueba hoy: kwargs correctos + tipo válido → el artefacto
es ACEPTADO y aterriza en un engine que se descarta → el log de éxito es una
afirmación falsa. El cableado real (Opción 1) es lo único que produce señal.

---

## 2. Los tres tipos nuevos son dominio-DOCUMENTO, no dominio-DISPOSITIVO

`document_visual` (0.40) y `document_geometry` (0.45) ya existen como tipos P3
y hoy caen en rol DEVICE por defecto (no están en `_EVIDENCE_ROLE`). Los tres
tipos nuevos son de la misma familia documental. El riesgo que Kimi señaló:
enrutarlos como DEVICE los mete en el **gate de corroboración**
("dos fuentes DEVICE independientes"), y una fractura estilométrica de
single-modality no debería, por sí sola, sacar un veredicto de ABSTAIN.

**Recomendación de rol epistémico (B-070): los tres como `CONTEXTUAL`.**
CONTEXTUAL = cuenta en el composite de malicia (puede portar anomalía real,
ej. un lote de documentos fabricados es sospechoso) pero NO es fuente
independiente de dispositivo → NO corrobora en el gate. Es exactamente la
semántica correcta para forensia documental: informa el score, no desbloquea
el veredicto.

**Asimetría a resolver por el colectivo:** `document_visual`/`document_geometry`
hoy son DEVICE. Si los tres nuevos son CONTEXTUAL, conviene evaluar re-
clasificar también los dos existentes a CONTEXTUAL por consistencia — pero
eso mueve artefactos ya en el corpus (impacto retroactivo, clase B-067/B-092),
así que es una decisión aparte que debe correr su propia comparación. La
propuesta conservadora para AHORA: tipos nuevos = CONTEXTUAL; los dos
existentes se dejan como están y se anota la asimetría.

---

## 3. Calibración propuesta (por analogía con la escala existente)

Anclas de la escala vigente (`EVIDENCE_PROFILES`, `vigia/tools/caie.py`):
`document_visual` 0.40 · `document_geometry` 0.45 ("harder to fake than
**text**") · `file_timestamp` 0.70 · `timestamp_precision` 0.05 (device,
tool-signature) · fallback legacy 0.50/0.20.

| Tipo nuevo | spoofability | base_weight | rol B-070 | ¿gate? | Razonamiento |
|-----------|:---:|:---:|:---:|:---:|--------------|
| `linguistic_forensics` | **0.60** | **0.18** | CONTEXTUAL | no | El propio comentario de `document_geometry` marca el texto como la capa MÁS falsificable de un documento (estilo se imita; un LLM lo lava). Más spoofable que visual(0.40)/geometry(0.45). Una incongruencia DETECTADA es señal real, pero de una sola modalidad. |
| `batch_forensics` | **0.45** | **0.22** | CONTEXTUAL | no | Entanglement estructural cross-documento: la independencia es difícil de falsificar retroactivamente a lo largo de un lote (propiedad estadística/estructural). Más robusto que texto; análogo a `document_geometry`. |
| `temporal_fraud` | **0.55** | **0.20** | CONTEXTUAL | no | Fraude temporal INTRA-documento (claims de fecha del documento), distinto del `timestamp_precision` (0.05) de filesystem que es device-level y casi irrefutable. Los claims documentales son spoofables (cf. `file_timestamp` 0.70), pero una CONTRADICCIÓN detectada es más difícil de ingeniar que un timestamp único. |

Estos valores son un PUNTO DE PARTIDA calibrado, no un veredicto. El colectivo
debe confirmarlos; la clase B-092 (banda mobile) y B-067 (tipos sin calibrar)
son el precedente de que calibrar un perfil es una decisión forense por tipo,
no un default.

---

## 4. Condiciones de implementación (las cuatro de Kimi, operacionalizadas)

1. **Perfiles nuevos aprobados.** Agregar las tres entradas a
   `EVIDENCE_PROFILES` con los valores que el colectivo apruebe, y las tres
   entradas a `_EVIDENCE_ROLE` como CONTEXTUAL. Sin esto, el whitelist
   `_VALID_EVIDENCE_TYPES` rechaza los tres tipos (hoy no existen) y el
   cableado sería rechazado por el guardrail — el fix mecánico moriría ahí.

2. **Metadata de adquisición obligatoria (ley B-131/B-137).** Kimi verificó
   por inducción que un artefacto document-shape sin metadata de custodia
   dispara `ACQUISITION_METADATA_MISSING_CRITICAL` y degrada `base_trust`
   1.00 → 0.10. Las fracturas ruteadas DEBEN portar la metadata de adquisición
   del documento origen o llegan autodestruidas. El cableado tiene que
   propagar custody metadata igual que los seis sitios post-Gamma de B-131.

3. **Corrida comparativa de corpus (gate `fixed>=1 AND broken==0`).** Cablear
   introduce fracturas nuevas que mueven veredictos. Correr `run_all_agent.py
   --rerun` completo, comparar por caso contra el baseline, y NO aplicar si
   hay un solo flip contra `expected_verdict`. Restaurar bundles con
   `git checkout --` tras la corrida (disciplina del reporte).

4. **Borrar los logs de éxito falsos.** `CAIE_ARTIFACT_INJECTED` (vision_audit)
   y `ENTANGLEMENT_CAIE_INJECTED` (entanglement) afirman inyección exitosa
   sobre un engine descartado. Al cablear, o bien pasan a reflejar el ruteo
   real, o se eliminan. No pueden sobrevivir como afirmaciones falsas.

---

## 5. Qué NO decide esta propuesta

- **raw_score domain:** `verdict.mcp` (adversarial_nlp) y `fracture["severity"]`
  (entanglement/temporal) deben verificarse en rango [0,1] antes de alimentar
  la fórmula `raw × (1-spoofability) × weight × trust`. Ítem de verificación,
  no calibrado aquí.
- **Reclasificar `document_visual`/`document_geometry` a CONTEXTUAL:** anotado
  como asimetría; decisión aparte con su propia corrida (impacto retroactivo).
- **Ruteo por layout de directorios (relación con B-133/B-137):** fuera de
  alcance; este documento es solo el cableado CAIE.

---

## 6. Resumen para el colectivo

Endoso la Opción 1 de Kimi. Antes de tocar el decision path pido sign-off
sobre: (a) los tres perfiles de la tabla §3 (spoofability/weight), (b) el rol
CONTEXTUAL para los tres, (c) la asimetría con document_visual/geometry
(dejar como está por ahora, sí/no). Con eso aprobado, la implementación es:
tres entradas en `EVIDENCE_PROFILES` + tres en `_EVIDENCE_ROLE`, propagación
de custody metadata en el ruteo, borrado de los cuatro bloques de engine
local y sus logs falsos, y corrida comparativa de corpus con gate
`fixed>=1 AND broken==0` como condición de merge.
