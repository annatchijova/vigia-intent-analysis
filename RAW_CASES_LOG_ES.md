# RAW_CASES_LOG_ES — VIGIA Agente Forense: Catálogo de Investigaciones sobre Evidencia Real

> **Nota de catálogo:** Este documento es un catálogo por caso de las investigaciones
> del agente autónomo VIGIA sobre corpus forenses reales. NO es un agregado de accuracy.
> Cada caso es una investigación individual con su propio contexto de evidencia,
> método de extracción y hallazgos. Esto refleja la doctrina de Domain C documentada
> en `README.md`: los resultados sobre evidencia real se miden por caso, no como
> número único de corpus.
>
> En la fecha de publicación del README (2026-07-14): **43 fuentes de evidencia real
> distintas** (SRL-2018: 22 imágenes de memoria, MUS2019/Narcos: 13 dumps, M57-Patents: 3,
> NPS-2010/2014, Magnet 2020 CTF, Tuck 2019 macOS, Vanko).
> La tabla incluye esos 43 más todas las corridas sobre evidencia real añadidas después.
> Los casos sintéticos, adversariales y de solo-JSON están excluidos;
> se rastrean en `data/cases/` y el corpus de 199 casos.

> **Documento maestro en inglés:** `RAW_CASES_LOG.md`
> Este archivo es la traducción al español de la misma información.
> Ante cualquier discrepancia, prevalece el archivo en inglés.

## Resumen (generado automáticamente)

- **Bundles totales catalogados:** 79 corridas completadas + 10 pendientes
- **MALICE:** 38 | **SUSPICION:** 30 | **NOISE:** 6 | **ABSTAIN:** 5
- **PENDIENTES (no ejecutados sobre evidencia raw todavía):** 10

---

## Guía de Interpretación

| Veredicto | Significado |
|-----------|-------------|
| **MALICE** | Ocultamiento activo de intención; requiere mínimo dos fuentes corroborantes independientes |
| **SUSPICION** | Anomalía estructural presente; una fuente; hipótesis benigna no completamente refutada |
| **NOISE** | Totalmente explicado por mala configuración, error de software o comportamiento normal |
| **ABSTAIN** | Error de pipeline, formato no soportado, o datos insuficientes para clasificar |
| `PIPELINE_ERROR` | Plugin de Volatility3/SIFT no disponible para este perfil de memoria |
| `FORMAT_NOT_SUPPORTED` | Formato de dump de memoria no parseable con los plugins instalados |
| `supersedes` | Una corrida posterior produjo un resultado más confiable; la anterior se mantiene por registro |

---

## SRL-2018 — Intrusión Corporativa (corridas originales Volatility3)

Corridas Mode 1 originales sobre archivos `.img` de memoria raw. Las entradas
`PIPELINE_ERROR`/`ABSTAIN` indican que el plugin de Volatility3 no estaba disponible
para ese perfil de memoria; las corridas JSON-convertidas que las reemplazan aparecen
en la sección 'SRL-2018 (rerun)' más abajo.

Ver `RAW_CASES_LOG.md` para la tabla completa con todos los campos.

**Síntesis de resultados SRL-2018 (corridas originales):**

| Fuente | Veredicto | Confianza | Fecha |
|--------|-----------|-----------|-------|
| ADMIN-001 | MALICE | 14/25 | 2026-05-29 |
| AV-003 | MALICE | 34/75 | 2026-06-02 |
| DC-MEM-005 | SUSPICION | 3/50 | 2026-06-02 |
| ELF-003 | SUSPICION | 3/50 | 2026-06-02 |
| FILE-003 | SUSPICION | 0 | 2026-06-02 |
| HUNT-005 | SUSPICION | 3/50 | 2026-06-02 |
| MAIL-001 | MALICE | 17/50 | 2026-06-03 |
| MAIL-002 | MALICE | 33/100 | 2026-06-04 |
| RD01-001 | MALICE | 34/75 | 2026-06-03 |
| RD02-001 | SUSPICION | 3/50 | 2026-06-03 |
| RD03-001 | MALICE | 34/75 | 2026-06-03 |
| RD04-001 | MALICE | 34/75 | 2026-06-03 |
| RD05-003 | MALICE | 34/75 | 2026-06-02 |
| RD06-001 | MALICE | 41/150 | 2026-06-03 |
| SP-001 | SUSPICION | 3/50 | 2026-06-03 |
| WKSTN01 a WKSTN06 | SUSPICION (01-03, 05-06) / MALICE (04) | 3/50 / 34/75 | 2026-06-03 |
| DC-MEM-001, ELF-001, FILE-001, HUNT-001, RD05-001 | **ABSTAIN** (PIPELINE_ERROR) | — | 2026-06-01 |

---

## MUS2019 / Narcos — Investigación de Cartel (13 dumps)

| Caso | Fuente / Descripción | Fecha | Veredicto | Confianza | Notas |
|------|---------------------|-------|-----------|-----------|-------|
| `NARCOS-CCLEANER-MEMORY` | Dump de memoria CCleaner | 2026-06-27 | **SUSPICION** | 0 | |
| `NARCOS-JANE-Day2` | Sospechosa Jane — día 2 | 2026-06-27 | **SUSPICION** | 0 | |
| `NARCOS-JANE-Day3` | Sospechosa Jane — día 3 | 2026-06-27 | **SUSPICION** | 0 | |
| `NARCOS-JANE-Day4` | Sospechosa Jane — día 4 | 2026-06-27 | **SUSPICION** | 0 | |
| `NARCOS-JOHN-ALT-DAY1` | John dispositivo alt — día 1 | 2026-06-27 | **MALICE** | 43/100 | |
| `NARCOS-JOHN-ALT-DAY2` | John dispositivo alt — día 2 | 2026-06-27 | **MALICE** | 4/25 | |
| `NARCOS-JOHN-PRIMARY-Day1` | John dispositivo principal — día 1 | 2026-06-27 | **MALICE** | 4/25 | |
| `NARCOS-JOHN-PRIMARY-Day2` | John dispositivo principal — día 2 | 2026-06-27 | **MALICE** | 43/100 | |
| `NARCOS-JOHN-PRIMARY-Day3` | John dispositivo principal — día 3 | 2026-06-27 | **MALICE** | 4/25 | |
| `NARCOS-JOHN-PRIMARY-Day4` | John dispositivo principal — día 4 | 2026-06-27 | **MALICE** | 4/25 | |
| `NARCOS-STEVE-Day1` | Sospechoso Steve — día 1 | 2026-06-27 | **ABSTAIN** | 0/1 | FORMAT_NOT_SUPPORTED: perfil de memoria incompatible |
| `NARCOS-STEVE-Day2` | Sospechoso Steve — día 2 | 2026-06-27 | **ABSTAIN** | 0/1 | FORMAT_NOT_SUPPORTED |
| `NARCOS-STEVE-Day4` | Sospechoso Steve — día 4 | 2026-06-27 | **MALICE** | 9/25 | |

---

## M57-Patents — Robo de Propiedad Intelectual (3 imágenes)

| Caso | Descripción | Fecha | Veredicto | Notas |
|------|-------------|-------|-----------|-------|
| `M57-JO-2009-12-07` (srl2018) | Laptop Jo, 7 Dic 2009 (run original) | 2026-06-27 | **ABSTAIN** | PIPELINE_ERROR; ver VIGIA-REAL-M57-JO-Dec07 |
| `M57-PAT-2009-12-07` (srl2018) | Laptop Pat, 7 Dic 2009 (original) | 2026-06-27 | **ABSTAIN** | PIPELINE_ERROR; ver rerun |
| `M57-PAT-2009-12-11` (srl2018) | Laptop Pat, 11 Dic 2009 (original) | 2026-06-27 | **ABSTAIN** | PIPELINE_ERROR; ver rerun |
| `VIGIA-REAL-M57-JO-Dec07` | M57 Jo, 7 Dic (rerun JSON) | 2026-07-13 | **SUSPICION** | canónico; reemplaza PIPELINE_ERROR |
| `VIGIA-REAL-M57-PAT-Dec07` | M57 Pat, 7 Dic (rerun JSON) | 2026-07-13 | **SUSPICION** | canónico |
| `VIGIA-REAL-M57-PAT-Dec11` | M57 Pat, 11 Dic (rerun JSON) | 2026-07-13 | **MALICE** | canónico |
| `VIGIA-NITROBA-M57-001` | Digital Corpora Nitroba hostigamiento (M57) | 2026-07-13 | **SUSPICION** | |

---

## NPS — Corpus Educativos NIST/CFReDS

| Caso | Descripción | Fecha | Veredicto | Notas |
|------|-------------|-------|-----------|-------|
| `NPS-2010-EMAILS` | NPS 2010 corpus de emails (FAT16 E01) | 2026-07-13 | **NOISE** | |
| `NPS-2009-DOMEXUSERS` | NPS 2009 DomEx usuarios XML | 2026-07-13 | **SUSPICION** | Esperado: NOISE; obtenido: SUSPICION — divergencia documentada |
| `VIGIA-REAL-NPS-2010-EMAILS` | NPS 2010 emails (rerun JSON) | 2026-07-13 | **NOISE** | |
| `VIGIA-REAL-NPS-2014-USB-NONDETERMINISTIC` | NPS 2014 USB adquisición no determinista | 2026-07-13 | **NOISE** | no determinismo de adquisición documentado como L-020 |

---

## Magnet Forensics CTF — 2014 / 2020 / 2021 / 2022

| Caso | Descripción | Fecha | Veredicto | Notas |
|------|-------------|-------|-----------|-------|
| `MAGNET-2020-CTF-WINDOWS` | 2020 CTF Windows memoria (run original) | 2026-06-28 | **SUSPICION** | |
| `VIGIA-MAGNET-2020-WINDOWS` | 2020 CTF Windows (rerun JSON) | 2026-07-13 | **SUSPICION** | |
| `VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT` | 2020 CTF — escenario pagefile ausente | 2026-07-13 | **SUSPICION** | |
| `VIGIA-MAGNET-2014-TIMELINE` | 2014 timeline multidispositivo | 2026-07-13 | **SUSPICION** | |
| `VIGIA-REAL-MAGNET-2021-IOS-ELI` | 2021 iOS — Eli iPhone | 2026-07-13 | **SUSPICION** | |
| `VIGIA-MAGNET-2022-WINDOWS` | 2022 CTF Windows artefactos | 2026-07-13 | **MALICE** | |
| `VIGIA-MAGNET-2022-iOS-JESS` | 2022 iOS Jess (subconjunto JSON) | 2026-07-13 | **SUSPICION** | E01 completo de 8.2 GB PENDIENTE — ver tabla de reruns |
| `VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN` | 2022 iOS Jess keychain | 2026-07-13 | **SUSPICION** | |
| `VIGIA-REAL-MAGNET-2022-ANDROID` | 2022 imagen Android | 2026-07-13 | **SUSPICION** | |
| `VIGIA-CTF-2021-iOS-Eli-iPhone8` | CFReDS iOS CTF 2021 — Eli iPhone 8 | 2026-07-13 | **MALICE** | |

---

## Otros Corpus Públicos

| Caso | Descripción | Fecha | Veredicto | Notas |
|------|-------------|-------|-----------|-------|
| `VIGIA-TUCK-2019` | Digital Corpora Tuck 2019 macOS APFS | 2026-07-13 | **MALICE** | |
| `OWL-NEXUS5-CASE` | Owl Investigation HD1/Nexus 5 | 2026-07-13 | **NOISE** | Esperado SUSPICION; obtenido NOISE — límite L-011 (señal débil) |
| `VIGIA-HMG-99999-11` | HMG Infosec No.5 — caso 99999-11 | 2026-07-13 | **MALICE** | |
| `VIGIA-NOKIA6230-001` | Forense de Nokia 6230 | 2026-07-13 | **NOISE** | |
| `VIGIA-REAL-ROCBA` | Investigación fraude ROCBA | 2026-07-13 | **MALICE** | |
| `VIGIA-REAL-TDUNGAN` | Digital Corpora XP Tdungan | 2026-07-13 | **MALICE** | |
| `VIGIA-REAL-MAGNET-2022-LINUX-RAFAEL` | Magnet 2022 Linux Rafael | 2026-07-13 | **SUSPICION** | |
| `VIGIA-GOOGLE-TAKEOUT-2020` | Forense de exportación Google Takeout 2020 | 2026-07-13 | **MALICE** | |
| `VIGIA-DRIVE-DOWNLOAD-2026` | Descarga Google Drive 2026 | 2026-07-13 | **NOISE** | |

---

## Reruns sobre Evidencia Raw Local — Planificados 2026-07-14

Directorios `evidence/` en cola para rerun Mode 1 (`vigia_agent.py` directamente
sobre artefactos raw, sin conversión JSON). Objetivo de validación: confirmar que
B-127 (corrección de límite `prior_trust` `<` → `<=`) no invirtió ningún veredicto
en casos con `confidence = 0.5` exacto.

| Directorio de Evidencia | Case ID Planificado | Estado | Tipos de Artefacto | Notas |
|------------------------|---------------------|--------|-------------------|-------|
| `evidence/magnet-2020-windows-artifacts/` | `MAGNET-2020-WIN-RAW-20260714` | **HECHO** — SUSPICION 3/5 | evtx, registry hives | [bundle](results/agent_batch/MAGNET-2020-WIN-RAW-20260714_bundle.json) |
| `evidence/magnet-2022-windows-artifacts/` | `MAGNET-2022-WIN-RAW-20260714` | **HECHO** — SUSPICION 3/5 | evtx, hives | [bundle](results/agent_batch/MAGNET-2022-WIN-RAW-20260714_bundle.json) |
| `evidence/magnet-2014-multidevice/` | `MAGNET-2014-RAW-20260714` | **HECHO** — ABSTAIN (UNDETERMINED: gap de evidencia) | prefetch, .docx | [bundle](results/agent_batch/MAGNET-2014-RAW-20260714_bundle.json) |
| `evidence/owl-2019-hd1-windows/` | `OWL-HD1-RAW-20260714` | **HECHO** — ABSTAIN (ABSTAIN_V2: empate CCS 1/2) | evtx, NTUSER.DAT, prefetch, SAM/SYSTEM | [bundle](results/agent_batch/OWL-HD1-RAW-20260714_bundle.json) |
| `evidence/owl-2019-nexus5-quick/` | `OWL-NEXUS5-RAW-20260714` | **HECHO** — ABSTAIN (MOBILE_EVIDENCE_ANALYZED: 1 señal) | artefactos Android | [bundle](results/agent_batch/OWL-NEXUS5-RAW-20260714_bundle.json) |
| `evidence/flare-on/` | `FLAREON-RAW-20260714` | **HECHO** — ABSTAIN (UNDETERMINED) | artefactos malware CTF | [bundle](results/agent_batch/FLAREON-RAW-20260714_bundle.json) |
| `evidence/image-2011-10-19/` | `IMAGE-2011-RAW-20260714` | **HECHO** — ABSTAIN (PIPELINE_ERROR: E01 requiere SIFT) | imagen de disco 2011-10-19-Sample.E01 | [bundle](results/agent_batch/IMAGE-2011-RAW-20260714_bundle.json) |
| `evidence/dfworkbook/` | `DFWORKBOOK-RAW-20260714` | **HECHO** — ABSTAIN (PIPELINE_ERROR: E01 requiere SIFT) | 2011-10-19-Sample.E01 + eventlogs | [bundle](results/agent_batch/DFWORKBOOK-RAW-20260714_bundle.json) |
| `evidence/takeout-2020/` | `TAKEOUT-RAW-20260714` | **HECHO** — SUSPICION 21/25 | exportación Google Takeout | [bundle](results/agent_batch/TAKEOUT-RAW-20260714_bundle.json) |
| `evidence/magnet-2022-ios-jess/` | `MAGNET-2022-IOS-JESS-RAW` | **PENDIENTE** | iOS E01 (8.2 GB) | Requiere extracción del zip primero; no bloquea los demás reruns |

**Resultado de validación B-127:** Ninguno de los reruns completados produce `confidence = 0.5` exacto.
La corrección del límite (`prior_trust < 0.5` → `<= 0.5`) no invirtió ningún veredicto en estos casos de evidencia local.

---

*Generado: 2026-07-14.*
*Ver `README.md` — sección Domain C — para la base doctrinal de este catálogo.*
*Documento maestro en inglés: `RAW_CASES_LOG.md`*
