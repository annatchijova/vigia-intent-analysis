# Cómo revisar un bundle sellado de VIGÍA como experto

Esta guía es para un perito forense que tiene que defender, atacar o reproducir
un veredicto de VIGÍA. Cubre las tres familias de bundle y qué sella cada una, el
flujo de verificación, cómo quedan registrados los gates Daubert, y cómo leer el
reporte experto (`*_report_expert_<lang>.md`). Versión en inglés:
[`EXPERT_GUIDE.md`](./EXPERT_GUIDE.md). El reporte es un visor: todo lo de abajo se
puede chequear contra el bundle sin confiar en la prosa.

---

## 1. Tres familias, tres sellos

El repositorio desarrolló tres formatos de bundle (`docs/EXECUTION_MODES.md`). Sus
hashes **no son comparables entre familias** (`KNOWN_LIMITATIONS.md` L-030, L-031);
el reporte experto imprime las anclas de cada familia y marca las otras como
ausentes en vez de sustituirlas.

| Familia | Sello | Anclas impresas | Verificador |
|---|---|---|---|
| `ebs_v1` | `integrity.bundle_hash` sobre cada clave del payload salvo `integrity` (Invariante I2); `analysis_fingerprint` sobre el payload sin timestamps ni ids | `bundle_hash`, `analysis_fingerprint`, `graph_hash`, `decision_hash`, `policy_hash`, `engine_attestation_hash`, `ecl_hash`, `sealed_at` | `python3 forensics/verify_ebs_v1.py <bundle>` (sólo stdlib) |
| `agent_audit` | SHA-256 del **archivo completo**, guardado en el sidecar `.sha256`, nunca dentro del archivo (autorreferencia) | `evidence_sha256`, `runtime_fingerprint`, `analysis_timestamp`, `audit_trail.total_entries` | `sha256sum -c <bundle>.sha256`; `vigia.core.reasoning_trace.verify_reasoning_trace` para el hermano de traza |
| `mcp_investigation` | `bundle_sha256` registrado por el investigador; `tool_execution_log` encadenado por hashes (`prev_hash`, `entry_hash`, `entry_hmac` opcional) con ancla de cola `chain_tip_sha256` | `bundle_sha256`, `primary_evidence_sha256`, `chain_tip_sha256`, `timestamp_sealed` | `python3 verify_tool_log.py <bundle> [--hmac-key-file F]` |

Consecuencia para cualquier presentación: nada puede agregarse *dentro* de un bundle
sin cambiar su sello. Los reportes son archivos hermanos, igual que
`<stem>_reasoning_trace.json`.

## 2. Flujo de verificación

1. **Atá el archivo.** La cabecera del reporte lleva el SHA-256 de los bytes exactos
   desde los que se generó. `sha256sum <bundle>` tiene que coincidir; si no, el
   reporte quedó viejo.
2. **Corré el verificador de la familia** (tabla de arriba). Correr el equivocado
   reporta no conformidad por diseño; eso no es un hallazgo contra el bundle.
3. **Regenerá el reporte** y compará: `python3 -m vigia.report <bundle> --audience
   expert --lang es --stdout`. Mismos bytes de bundle, mismos bytes de reporte, en
   cualquier máquina, bajo cualquier `PYTHONHASHSEED`, locale o zona horaria.
4. **Leé los huecos.** Todo lo que el lector no pudo encontrar se lista, nunca se
   completa.
5. **Cruzá los literales exactos** (sección 4 del reporte) contra los JSON pointers.
   Las Fractions serializadas se imprimen como `numerador/denominador`; los floats
   sellados, como su propio literal JSON. Si ves un float en un camino sellado, eso es
   en sí una limitación registrada (L-021, L-073), no un artefacto de presentación.

## 3. Campos con veredicto y desacuerdo

La sección 2 del reporte lista cada campo que el normalizador trata como portador
de veredicto, con su JSON pointer. Los bundles EBS v1 pueden llevar
`decision_trace.decision` y `caie_analysis.verdict`; los de agente llevan
`agent_verdict` y la etiqueta de hipótesis `best_hypothesis`. Cuando dos valores en
escala difieren, se activa `verdict_disagreement` y se muestran ambos. El ejemplo
`examples/VIGIA-REAL-SRL-DMZ-FTP_bundle_report_expert_en.md` muestra `ABSTAIN` del
chequeo de coherencia R3 al lado de `MALICE` del scorer; `r3_calibration_note`
registra la reconciliación que hizo el propio pipeline. El reporte no arbitra.

## 4. Gates Daubert tal como quedan registrados

La autocorrección de VIGÍA es **previa a la emisión**: un gate intercepta un
candidato antes de sellarlo, y el registro de esa intercepción es parte del bundle.

- **Modo 2**: entradas de `refutation_gate_log` (`candidate_verdict`,
  `gate_applied`, `gate_rule`, `gate_result`, `benign_hypothesis_tested`). Ejemplo:
  un candidato `INTENT` de `reason_with_llm` rechazado por el Daubert Corroboration
  Gate porque `n_independent_sources < 2`, emitido como `SUSPICION`
  (`examples/VIGIA-KIWI-006_bundle_report_expert_es.md`).
- **Agente**: entradas de `audit_trail.entries` cuyo `action` nombra un gate, un
  downgrade o una contradicción, más `self_corrections_applied`.
- **EBS v1**: `decision_trace.reason_code`, `abstain_reason`,
  `caie_analysis.hard_temporal_gate`, `r3_calibration_note`,
  `caie_fractures_source` (`live_caie` significa que las fracturas se calcularon, no
  se declararon).

`devil_advocate` es la explicación benigna más fuerte que el análisis tuvo que
vencer. El Protocolo de Refutación lo hace obligatorio para `INTENT` y `MALICE`.
Cuando un veredicto así está sellado sin uno, el reporte imprime un aviso de HUECO
(L-022) y deja el veredicto intacto.

## 5. El registro de ejecución

La sección 6 resume la evidencia de proceso sin listar todo: cantidad de entradas,
`chain_version` (v1 protege sólo `result_summary`; v2 cubre toda la entrada),
presencia del ancla de cola, y un histograma ordenado por cantidad y luego por
nombre. El listado textual está acotado y lo dice; abrí el bundle para el resto.

## 6. Lo que los reportes deliberadamente no hacen

- Ninguna etiqueta derivada, ni siquiera un bucket ENFSI a partir de `lr`: una
  etiqueta derivada es un valor calculado, y esta capa no calcula nada.
- No ejecutan verificadores: el reporte imprime el comando, no lo corre, para que el
  render siga siendo una función pura de los bytes del bundle.
- No traducen tokens sellados, nombres de campo ni texto citado.
- No llevan fecha de generación.

## 7. Para seguir

- `docs/DAUBERT_JUDICIAL_ES.md` (y la versión EN): el argumento de admisibilidad
  completo.
- `docs/EXECUTION_MODES.md`: por qué divergieron las familias y cómo las trata la
  web UI.
- `KNOWN_LIMITATIONS.md`: L-004 (narrativa como input), L-020 (sin audit trail
  granular en Modo 2), L-022, L-030/L-031, L-056, L-074 (esta capa de presentación).
- `docs/ENGINEERING_DISCIPLINE.md` sección 5: las reglas de LLM fuera del loop y de
  núcleo determinista que estos reportes respetan.
