# TAXA_DOMINIOS_RECOLECCION — Censo de evidence_type y taxonomía de dominios de recolección

| Campo | Valor |
|-------|-------|
| **Contexto** | Investigación previa a R4-3 — diagnóstico del colectivo (6 modelos): Noisy-OR asume independencia, y 100 logs del mismo tipo no son 100 fuentes independientes |
| **Fecha** | 2026-07-07 |
| **Base** | tag `restore-point-r43-taxa-f30f9aa` |
| **Alcance** | `data/cases/**/*.json` (263 archivos, 201 con `evidence_type`) — solo investigación, 0 cambios de código |

---

## Resumen ejecutivo

El corpus usa **53 `evidence_type` distintos** (censo completo en §2). El
escenario del diagnóstico es literal, no hipotético: **`VIGIA-BREAK-014` tiene
exactamente 100 artefactos `log_entry`** (expected SUSPICION — es el BREAK de
drowning por volumen), y 9 casos tienen ≥10 repeticiones del mismo tipo.
`log_entry` domina el corpus (376 artefactos en 133 casos, 2.3× el segundo).

Dos hallazgos de código que condicionan el diseño de R4-3:

1. **Ya existe un clasificador de dominios — y es código muerto.**
   `caie.py:143-163` define `_DOMAIN_MAP` + `classify_domain()` con dominios
   memory/network/filesystem/hardware, pero **ningún consumidor lo invoca**
   (misma clase de asimetría que A-1/B8: capacidad creada, nunca usada).
   Cubre 16 de los 53 tipos; el resto caería a `"UNKNOWN"`.
2. **`_DOMAIN_MAP` clasifica `log_entry` como "network"** — para el propósito
   de R4-3 eso fusionaría el canal más fabricable y más voluminoso (syslog:
   spoofability 0.85, escribible por admin) con la telemetría de red. La
   taxonomía propuesta los separa: el eje correcto para independencia no es
   "de qué habla la evidencia" sino **quién/qué la produce y qué se necesita
   comprometer para fabricarla** (el modo de fallo compartido).

**Propuesta: 5 dominios + 1 pseudo-dominio** (§3), con mapeo completo de los
53 tipos (§4) y consecuencias de diseño para Noisy-OR (§5).

---

## 1. Principio rector de la taxonomía

Para corregir la independencia de Noisy-OR, dos artefactos pertenecen al
MISMO dominio si comparten el **canal de recolección y el modo de
fabricación**: si un solo acto del atacante (o un solo defecto del sensor)
puede producir/corromper a ambos, su corroboración mutua vale menos que la de
dos artefactos de dominios distintos. Criterios usados, en orden:

1. **¿Qué hay que comprometer para fabricarlo?** (user-space con privilegios /
   live compromise del kernel / acceso físico / nada — es texto declarativo).
2. **¿Qué herramienta/sensor lo recolecta?** (parser de logs, Volatility,
   parser NTFS, captura de red, análisis de documento).
3. Coherencia con las estructuras existentes: `EVIDENCE_PROFILES`
   (spoofability, caie.py:245), `_DOMAIN_MAP` (caie.py:143), `EvidenceLayer`
   (forensic_adapter/abductive_reasoner_v2: MEMORY/NETWORK/REGISTRY/DISK_MFT).

La spoofability ya codifica el criterio 1 numéricamente: los dominios
propuestos son casi bandas de spoofability, lo que confirma que el eje es el
mismo que el motor ya usa para trust — solo que nunca se aplicó a la
independencia.

---

## 2. Censo completo (263 archivos, 53 tipos, 1.007 artefactos tipados)

| evidence_type | artefactos | casos | máx. repetición en un caso |
|---|---|---|---|
| log_entry | 376 | 133 | **100** (VIGIA-BREAK-014) |
| memory_process | 173 | 109 | 3 |
| binary | 59 | 6 | 11 |
| file_timestamp | 53 | 41 | 3 |
| cultural_marker | 50 | 36 | 4 |
| file_hash | 36 | 30 | 4 |
| file_metadata | 29 | 17 | 5 |
| registry_key | 18 | 10 | 5 |
| ip_geolocation | 17 | 17 | 1 |
| binary_executable | 17 | 2 | 10 |
| document | 16 | 1 | 16 |
| container_zip | 15 | 2 | 9 |
| network_flow | 10 | 8 | 2 |
| lsass_session | 10 | 10 | 1 |
| cryptographic_hash | 8 | 6 | 2 |
| document_geometry | 7 | 4 | 2 |
| malware_static_analysis | 7 | 6 | 2 |
| dns_record | 7 | 7 | 1 |
| email_content | 6 | 3 | 3 |
| document_visual | 6 | 4 | 2 |
| kernel_structure | 6 | 6 | 1 |
| archive | 6 | 3 | 3 |
| network_traffic | 5 | 5 | 1 |
| network_capture | 5 | 5 | 1 |
| keylogger_capture | 5 | 2 | 4 |
| filesystem_artifact | 5 | 1 | 5 |
| disk_image | 4 | 3 | 2 |
| osint | 4 | 3 | 2 |
| mft_entry | 4 | 4 | 1 |
| windows_event_log | 4 | 1 | 4 |
| shimcache | 4 | 1 | 4 |
| pe_executable | 3 | 2 | 2 |
| git_forensics | 3 | 2 | 2 |
| spreadsheet | 3 | 1 | 3 |
| event_log | 3 | 1 | 3 |
| web_artifact | 2 | 1 | 2 |
| file_text | 2 | 1 | 2 |
| acquisition_context | 2 | 2 | 1 |
| memory_os_profile | 2 | 2 | 1 |
| registry_hive | 2 | 2 | 1 |
| email_account_creation, network_communication_pattern, deleted_file_recovery, device_acquisition_timeline, binary_diff, TPM_attestation, malware_infrastructure, behavioral_context, outcome_signal, behavioral_profile, plaintext_credential, elf_executable, user_agent | 1 c/u | 1 c/u | 1 |

Distribución de repetición máxima del mismo tipo por caso: 1 → 41 casos;
2–4 → 141; 5–9 → 10; **≥10 → 9 casos**. La cola ≥10 es exactamente la
población que Noisy-OR trata mal.

---

## 3. Taxonomía propuesta: 5 dominios + 1 pseudo-dominio

### D1 — `log_symbolic` (registro simbólico/declarativo)

**Qué se necesita para fabricarlo:** nada estructural — es texto que un admin
(o el atacante con sus privilegios) escribe. Spoofability 0.85–0.90.
**Sensor:** parsers de texto/log.
**Por qué es SU PROPIO dominio y no "network"** (contra el `_DOMAIN_MAP`
actual): un syslog que *habla* de conexiones de red no es telemetría de red —
comparte modo de fabricación con cualquier otro log, no con un pcap. 100
entradas de log las produce un solo `for` del atacante; el drowning de
BREAK-014 vive acá.

### D2 — `memory_kernel` (memoria volátil y estructuras de kernel)

**Qué se necesita:** compromiso live (Ring-0 para las estructuras).
Spoofability 0.05–0.15. **Sensor:** Volatility3 sobre el dump — un solo dump:
100 procesos del mismo dump comparten TODA la cadena de adquisición.

### D3 — `filesystem_metadata` (metadata de disco y registro del OS)

**Qué se necesita:** user-space con privilegios (touch, reg add) para la capa
blanda; Ring-0 para la dura (MFT/USN — que por eso llevan spoofability 0.05 y
son las armas anti-timestomp). Spoofability 0.20–0.70. **Sensor:** parsers
NTFS/registry sobre la MISMA imagen de disco.

### D4 — `network_telemetry` (telemetría de red observada)

**Qué se necesita:** control del canal en el momento del tráfico (spoofing
de IP, tunneling) — no se fabrica retroactivamente editando un archivo local.
Spoofability 0.60–0.90 pero con modo de fabricación DISTINTO al de D1.
**Sensor:** captura/flow records/resolución externa.

### D5 — `content_artifact` (contenido y análisis de artefactos)

**Qué se necesita:** habilidad de fabricación de contenido (compilar un
binario señuelo, falsificar un documento) — costo por-artefacto alto, no
replicable con un loop. Spoofability 0.05 (hash criptográfico) a 0.90
(marcador cultural) — es el dominio más heterogéneo; ver nota en §5.
**Sensor:** análisis estático/visual/criptográfico del objeto.

### D0 — `assurance_context` (pseudo-dominio, fuera de Noisy-OR)

Artefactos que describen la ADQUISICIÓN, no el ataque
(`acquisition_context`, `device_acquisition_timeline`, `TPM_attestation`,
`outcome_signal`, `behavioral_context/profile`). Ya existe el precedente:
el validador los excluye vía `ACQUISITION_CONTEXT_NOT_ATTACK_EVIDENCE`.
No deben corroborar hipótesis de malicia — alimentan trust, no score.

---

## 4. Mapeo completo de los 53 tipos

| Dominio | evidence_types (artefactos) |
|---|---|
| **D1 log_symbolic** | log_entry (376), windows_event_log (4), event_log (3), keylogger_capture (5), plaintext_credential (1), email_account_creation (1) — *windows_event_log tiene spoofability 0.55 (EVTX binario, tamper-evident): es el miembro DURO del dominio, sigue siendo registro simbólico pero su factor de fabricación difiere; candidato a sub-banda* |
| **D2 memory_kernel** | memory_process (173), lsass_session (10), kernel_structure (6), memory_os_profile (2) |
| **D3 filesystem_metadata** | file_timestamp (53), file_hash (36), file_metadata (29), registry_key (18), registry_hive (2), mft_entry (4), shimcache (4), filesystem_artifact (5), deleted_file_recovery (1), disk_image (4) — *+ los tipos de código sin uso en corpus: usn_journal, usn_journal_gap, timestamp_precision, prefetch* |
| **D4 network_telemetry** | network_flow (10), network_traffic (5), network_capture (5), dns_record (7), ip_geolocation (17), user_agent (1), network_communication_pattern (1), malware_infrastructure (1) |
| **D5 content_artifact** | binary (59), binary_executable (17), pe_executable (3), elf_executable (1), binary_diff (1), malware_static_analysis (7), document (16), document_visual (6), document_geometry (7), spreadsheet (3), file_text (2), email_content (6), web_artifact (2), archive (6), container_zip (15), git_forensics (3), cryptographic_hash (8), cultural_marker (50), osint (4) |
| **D0 assurance_context** | acquisition_context (2), device_acquisition_timeline (1), TPM_attestation (1), behavioral_context (1), behavioral_profile (1), outcome_signal (1) |

Cobertura: 53/53 tipos del corpus + los 6 tipos definidos en
`EVIDENCE_PROFILES` que el corpus aún no usa. Ningún tipo queda en "UNKNOWN".

Casos borde argumentados:

- **`cultural_marker` → D5, no D1:** es interpretación de contenido (idioma,
  layout de teclado), no una entrada de registro; su fabricación es
  por-artefacto. Comparte con D1 la spoofability alta pero no el canal.
- **`ip_geolocation` → D4, no D1:** derivada de la observación de red aunque
  llegue tabulada; su fabricación es del canal (VPN/proxy), no del archivo.
- **`cryptographic_hash` → D5:** verifica el CONTENIDO de un objeto; su
  irrefutabilidad (0.05) lo hace el ancla del dominio, no un dominio aparte.
- **`disk_image` → D3:** es el contenedor de adquisición del filesystem;
  comparte cadena con lo que contiene.
- **`keylogger_capture` → D1:** output textual de un proceso de registro —
  fabricable escribiendo el archivo, como cualquier log.

---

## 5. Consecuencias de diseño para R4-3 (para la sesión de implementación)

1. **La corrección de Noisy-OR es intra-dominio, no global.** N señales del
   mismo dominio deben agregarse con rendimiento decreciente (las N compartem
   modo de fabricación); la corroboración ENTRE dominios es la que debe pesar
   — es la misma intuición del gate Daubert de 2 fuentes, formalizada.
   BREAK-014: 100×log_entry = esencialmente UNA fuente D1 gorda, no 100.
2. **Hay infraestructura muerta lista para revivir:** `classify_domain()`
   (caie.py:161) no tiene consumidores. R4-3 puede extender su `_DOMAIN_MAP`
   con esta taxonomía en lugar de crear otro mapa — pero corrigiendo
   `log_entry: "network"` → `log_symbolic`, que es un CAMBIO DE COMPORTAMIENTO
   si algo llega a consumirlo (hoy nada; verificado por grep).
3. **Riesgo de doble castigo:** FRS (`build_redundancy_groups` +
   `process_all_groups`) ya atenúa redundancia por entidad (pid/ip/tool), y
   la correlación de CAIE ya modula. La corrección por dominio debe medirse
   contra ambas para no atenuar tres veces la misma señal — gate comparativo
   obligatorio y mapa de interacción ANTES de tocar el scorer.
4. **D5 es heterogéneo a propósito** (spoofability 0.05–0.90): el dominio
   captura el canal (análisis de contenido), no la dureza. Si la
   implementación necesita bandas de dureza intra-dominio, la spoofability de
   `EVIDENCE_PROFILES` ya la provee — no duplicarla en la taxonomía.
5. **D0 no entra al Noisy-OR.** Precedente ya operativo en el validador
   (`_is_ctx`). Formalizarlo evita que la metadata de adquisición "corrobore"
   malicia.
6. **Un solo tipo domina el problema:** con log_entry al 37% de todos los
   artefactos tipados, el impacto de corpus de cualquier corrección será casi
   todo vía D1. La corrida comparativa debe reportar el delta por dominio.

---

## 6. Método

1. Tag `restore-point-r43-taxa-f30f9aa`.
2. Censo: walk de `data/cases/**/*.json` (263 archivos), extracción de
   `artifacts[].evidence_type`, conteo por tipo/caso/repetición-máxima.
3. Contraste contra las estructuras vivas: `EVIDENCE_PROFILES` (spoofability),
   `_DOMAIN_MAP`/`classify_domain` (dominios embrionarios, sin consumidores —
   verificado por grep), `_LAYER_MAP`/`EvidenceLayer` (capas del razonador).
4. Cero cambios de código. Este documento es el único artefacto.

*VIGÍA — investigación previa a R4-3 | 2026-07-07*
