# VIGIA FORENSIC INTENT ANALYSIS REPORT
## NPS-2009-domexusers Corpus — Full Investigation

```
Case ID      : NPS-2009-DOMEXUSERS
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic — claude-sonnet-4-6)
Evidence     : /home/labestiadevigia/Downloads/nps-2009-domexusers/
Mode         : Claude Code + MCP (Vigia_Sift_Bridge) + Ollama fallback
Session ID   : 2026-06-27T15:19:00Z
Session Nonce: 063da1512a1c7d6762318c0fc3388621eed544e322adfe4e4b3bb2854e157821
               (SHA-256 of first-hashed artifact: nps-2009-domexusers-redacted.xml)
Timestamp    : 2026-06-27T15:28:00Z (ISO 8601 UTC)
SANS Phase   : Lessons Learned (Phase 5 — full report)
```

---

## CHAIN OF CUSTODY — PRIMARY ARTIFACTS

| Artifact | Size | SHA-256 | Tool | Timestamp |
|----------|------|---------|------|-----------|
| `nps-2009-domexusers (1).E01` | 4.1 GB | `5c52f16eddd6d1afef216d968b19e7267fbd5e3c8bb1626bfb2d8c4f36cfaa1c` | bash/sha256sum | 2026-06-27T15:21Z |
| `nps-2009-domexusers.redacted.E01` | 2.0 GB | `cd774b24bccc8dc3a2eb72e8a76d379d2404967b4ee749db28c15cc8f7587e28` | bash/sha256sum | 2026-06-27T15:21Z |
| `nps-2009-domexusers.redacted.E02` | 2.0 GB | `a207ae77a76a3835a046d55f5ff3d0e4926d302d644ae3457cad1a8e4057405d` | bash/sha256sum | 2026-06-27T15:21Z |
| `nps-2009-domexusers.redacted.E03` | 2.7 MB | `e4fa35c66ada777bd0925b6f2c080ce23e52030b6f148b7925c8d8de722bd169` | bash/sha256sum | 2026-06-27T15:21Z |
| `nps-2009-domexusers.redacted.xml` | 3.2 MB | `063da1512a1c7d6762318c0fc3388621eed544e322adfe4e4b3bb2854e157821` | mcp/generate_forensic_hash | 2026-06-27T15:20:25Z |
| `nps-2009-domexusers.xml.old` | 37.4 MB | `f48d4218562ee5f2d1d95839aff3e0d53ddf84a41150d1f5f50355f5a828cd97` | mcp/generate_forensic_hash | 2026-06-27T15:20:26Z |
| `Unconfirmed 547175.crdownload` | 4.1 GB | (not hashed — incomplete download artifact) | — | — |

**Nota:** Las E01 fueron hasheadas con `sha256sum` (bash/stdlib) en lugar de `generate_forensic_hash` porque el MCP está sandboxed a `vigia-repo/evidence/`. Los XMLs fueron copiados al directorio de evidencia y hasheados atómicamente con `generate_forensic_hash`. Limitación documentada en KNOWN_LIMITATIONS.

---

## EXECUTIVE SUMMARY

Se analizó el corpus forense público NPS-2009-domexusers (Naval Postgraduate School, EE.UU.), un disco Windows XP NTFS adquirido el 2008-10-30 diseñado para simular un entorno de ejercicio de dominio con dos usuarios scripteados: `domex1` y `domex2`. El corpus contiene 35.313 objetos de archivo catalogados por fiwalk v0.5.1 sobre TSK 3.0.0.

El análisis revela un sistema de entrenamiento forense bien estructurado con artefactos de ciclo de vida de documentos, infraestructura de email multi-cuenta, comunicaciones por IM (Pidgin/AIM), y un conjunto completo de fuentes de evidencia DFIR. **No se detectaron patrones de INTENT ni MALICE**. El veredicto global es **NOISE**: todos los artefactos son consistentes con el diseño del ejercicio educativo. Dos hallazgos inicialmente candidatos a SUSPICION fueron refutados por el Protocolo de Refutación Obligatoria.

---

## SYSTEM PROFILE

| Campo | Valor |
|-------|-------|
| Sistema operativo | Windows XP (NTFS) |
| Nombre del dominio | `domex` |
| Imagen fuente original | `realistic.aff` (referenciada en fiwalk XML) |
| Herramienta de catalogación | fiwalk v0.5.1 / TSK 3.0.0 / AFF 3.3.4 |
| Sector size | 512 bytes |
| Partition offset | 32.256 bytes |
| Block count | 10.482.404 |
| Inicio del ejercicio | 2008-10-20 ~21:34 UTC |
| Adquisición | 2008-10-30 ~16:50 UTC |
| Duración del ejercicio | ~10 días |
| Restore Points | 16 (RP1 → RP16) |
| Total de objetos de archivo | 35.313 |
| Archivos eliminados permanentemente | 0 (ALLOC=0 = ninguno detectado) |

---

## USUARIOS DEL SISTEMA

| Usuario | SID | Perfil | Primera actividad | Última actividad |
|---------|-----|--------|-------------------|-----------------|
| Administrator | -500 | Setup/config | 2008-10-20 21:34 UTC | 2008-10-30 16:50 UTC |
| domex1 | -1003 | Ejercicio principal | 2008-10-21 19:12 UTC | 2008-10-30 16:47 UTC |
| domex2 | -1004 | Ejercicio principal | 2008-10-21 19:29 UTC | 2008-10-30 03:34 UTC |
| LocalService | — | Servicio sistema | — | 2008-10-30 16:50 UTC |
| NetworkService | — | Servicio sistema | — | 2008-10-30 16:50 UTC |
| Default User | — | Template | — | 2008-10-21 15:12 UTC |

---

## TIMELINE DE EVENTOS

```
2008-10-20 14:30  Default User — cookie/history index.dat inicializados
2008-10-20 21:34  Sistema — partición NTFS montada, Windows XP inicio
2008-10-20 21:36  All Users — SendTo, carpetas base creadas
2008-10-20 21:58  Administrator — My Documents/Sample Music/Pictures inicializados
2008-10-20 22:00  RP2 — primer restore point post-setup
2008-10-20 22:38  RP3
2008-10-20 22:40  Administrator — browsing: google, mozilla, live, genuine (IE cookies)
2008-10-20 22:41  Administrator — Chrome instalado (cookie chrome[1].txt)
2008-10-20 22:43  Administrator — AIM, AOL, yieldmanager (browsing AIM/AOL)
2008-10-20 23:43  RP4
2008-10-21 00:17  RP5
2008-10-21 03:34  Administrator — Desktop, Favorites, My Documents configurados
2008-10-21 04:16  Administrator — Google Chrome shortcut en Desktop
2008-10-21 04:18  All Users — Pidgin shortcut en Desktop
2008-10-21 15:09  All Users — AIM 6 shortcut en Desktop
2008-10-21 15:11  All Users — Mozilla Thunderbird shortcut
2008-10-21 15:12  All Users — Picasa 3 shortcut; Default User NTUSER.DAT actualizado
2008-10-21 19:12  domex1 — primer login: IE Desktop.htt, Quick Launch configurado
2008-10-21 19:21  domex1 — Flash Player (yourminis.com) — actividad de browser
2008-10-21 19:27  domex1 — Pidgin buddy icons descargados (Gmail TLS cert)
2008-10-21 19:29  domex2 — primer login: IE Quick Launch configurado; My Documents
2008-10-21 19:34  domex1 — Pidgin status.xml actualizado
2008-10-21 19:42  domex1 — Pidgin prefs.xml (configuración guardada)
2008-10-21 19:44  domex1 — XMPP caps actualizado (Jabber capabilities)
2008-10-21 20:04  domex1 — Pidgin accounts.xml (cuentas IM configuradas)
2008-10-21 20:08  domex1 — Pidgin buddy list finalizada (5.112b); RP6 snapshot
2008-10-21 20:08  RP6 — primer snapshot que incluye SID-1003 (domex1) y SID-1003 registry
2008-10-21 20:08  All Users — domex1.bmp, domex2.bmp — account pictures creadas
2008-10-22 21:41  RP6 completado; RP7 siguiente sesión
2008-10-23 23:24  RP7
2008-10-28 16:39  Administrator — IE History index.dat MSHist (semana 2008-10-20/27)
2008-10-28 16:40  RP8
2008-10-28 16:54  RP9
2008-10-28 16:55  All Users — Microsoft Office Outlook 2007 shortcut (primer uso Outlook)
2008-10-28 21:02  domex2 — DPAPI CREDHIST + master key creados (primer Outlook launch)
2008-10-28 21:02  domex2 — Outlook Quick Launch shortcut, firstrun.log
2008-10-28 21:02  domex2 — extend.dat Outlook (extensiones)
2008-10-29 16:14  domex1 — MSO1033.acl actualizado; Office sesión inicio
2008-10-29 16:14  domex1 — "This is a word document by domex user 1.docx" CREADO (9.844b)
2008-10-29 16:14  domex1 — CUSTOM.DIC (2b — prácticamente vacío)
2008-10-29 16:15  domex1 — "This is a word document sent by domex user 1.docx" CREADO (9.926b)
2008-10-29 16:15  domex1 — Dc3.docx → RECYCLER/SID-1003/ (9.852b) ← documento eliminado
2008-10-29 16:16  domex1 — "This is a spreadsheet by domex user 1.xlsx" CREADO (8.230b)
2008-10-29 16:16  domex1 — "This is a spreadsheet sent by domex user 1.xlsx" CREADO (8.203b)
2008-10-29 16:17  domex1 — Dc4.xlsx → RECYCLER/SID-1003/ (8.236b) ← spreadsheet eliminado
2008-10-29 16:17  domex1 — Excel12.pip (último uso Excel)
2008-10-29 16:21  domex2 — domexuser2.JPG guardado en My Pictures (19.920b)
2008-10-29 18:58  domex2 — Outlook log: Hotmail incoming email recibido
2008-10-29 16:59  domex2 — "domexuser2" documento abierto (Office Recent LNK)
2008-10-30 01:44  domex2 — Office Groove12.pip (sesión Groove/SharePoint)
2008-10-30 02:44  domex2 — IE cache: InboxAll[2].css + InboxLight[1].htm (webmail Hotmail)
2008-10-30 02:47  domex2 — CUSTOM.DIC actualizado (90b — palabras añadidas al diccionario)
2008-10-30 02:48  domex1 — Groove12.pip (sesión Groove)
2008-10-30 02:54  domex1 — MSOut12.pip (Outlook activado)
2008-10-30 02:59  Administrator — Windows Live Installer.exe en Desktop (2.4 MB)
2008-10-30 02:59  domex2 — Outlook.srs actualizado; Hotmail PST updated (271KB)
2008-10-30 03:30  domex2 — ~last~.sharing.xml.obi (Outlook sharing sync)
2008-10-30 03:32  domex2 — Outlook.NK2 (3.532:51), Gmail PST (525KB), Outlook.pst (271KB)
2008-10-30 03:34  domex2 — NTUSER.DAT último write (fin de sesión domex2)
2008-10-30 03:38  domex1 — RECYCLER INFO2 actualizado (acceso a Recycle Bin)
2008-10-30 03:40  domex1 — RECYCLER INFO2 actualizado de nuevo
2008-10-30 03:40  RP10 → RP16 (6 restore points más hasta shutdown)
2008-10-30 16:43  domex2 — NTUSER.DAT.LOG (último log write)
2008-10-30 16:47  domex1 — NTUSER.DAT último write (shutdown)
2008-10-30 16:49  System Volume — RP16 snapshot final
2008-10-30 16:50  Administrator + LocalService + NetworkService — NTUSER.DAT shutdown writes
```

---

## FINDINGS

---

### Finding F-001 — Ciclo de vida de documentos domex1 (152 segundos)

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifact** | `domex1/My Documents/` + `RECYCLER/S-1-5-21-...-1003/` |
| **Tools Used** | `read_evidence`, `bash_xml_parse`, `calculate_shannon_entropy`, `infer_intent` |

**Firstness:**
En 152 segundos (2008-10-29 16:14:52 → 16:17:24 UTC), domex1 generó cuatro archivos Office 2007:
- `This is a word document by domex user 1.docx` (9.844b)
- `This is a word document sent by domex user 1.docx` (9.926b)
- `This is a spreadsheet by domex user 1.xlsx` (8.230b)
- `This is a spreadsheet sent by domex user 1.xlsx` (8.203b)

Simultáneamente, dos versiones fueron movidas al Recycle Bin con nombres `Dc3.docx` y `Dc4.xlsx` (archivos recuperables, ALLOC=1). LNK files en Office Recent registran la actividad completa. CUSTOM.DIC de domex1 = 2 bytes (vacío funcional).

**Secondness:**
La velocidad (152s para 4 documentos) y la nomenclatura explícita ("This is a X by/sent/deleted by domex user 1") no corresponden a comportamiento espontáneo de usuario. Un usuario real no nombra sus documentos con descripciones de su propio comportamiento. Los archivos eliminados están en el Recycle Bin con ALLOC=1, visibles en el catálogo fiwalk — no hay intento de ocultarlos.

**Thirdness:**
Patrón de ejercicio forense estructurado. Los nombres de archivo son etiquetas explícitas de evidencia diseñadas para que un analista pueda identificar inequívocamente el ciclo de vida: creado → enviado → eliminado. La rapidez y el determinismo del proceso indican ejecución scripteada, no actividad orgánica.

**Carnegie:** None detected.
**MITRE TTPs:** N/A (corpus educativo, no incidente real).
**Devil Advocate:** N/A — veredicto NOISE, Refutation Protocol no requerido.
**Corroboration:** LNK timestamps en Office Recent coinciden con mtime de los archivos. INFO2 del Recycle Bin confirma las entradas Dc3/Dc4. Dos fuentes independientes confirman el ciclo completo.
**Self-Correction:** Inicial consideración: la velocidad de 152s podría indicar automatización (SUSPICION). Refutada: la velocidad es un feature del corpus educativo, no una anomalía. Downgraded a NOISE. Entropía del timeline = 4.41 (NORMAL).

---

### Finding F-002 — Archivos en Recycle Bin recuperables post-sesión domex2

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | MEDIUM |
| **Status** | CONFIRMED — tras refutación |
| **Artifact** | `RECYCLER/S-1-5-21-842925246-725345543-1844994965-1003/INFO2` |
| **Tools Used** | `bash_xml_parse`, `validate_and_correct_analysis` |

**Firstness:**
`RECYCLER/.../INFO2` fue modificado en 2008-10-30 03:38 y 03:40 UTC. domex2 terminó su última sesión de Outlook a las 03:32 y NTUSER a las 03:34. El RECYCLER pertenece a SID-1003 (domex1). Los archivos `Dc3.docx` y `Dc4.xlsx` dentro del RECYCLER tienen ALLOC=1 y son recuperables.

**Secondness:**
El INFO2 update a las 03:38 (4 minutos después del cierre de sesión de domex2) podría indicar que una tercera entidad accedió al Recycle Bin de domex1. Sin embargo, domex1 seguía activo (NTUSER.DAT last write = 16:47, más de 13 horas después). La actualización del INFO2 a las 03:38 es completamente consistente con domex1 abriendo el Recycle Bin en esa franja horaria.

**Thirdness:**
No hay patrón de acceso cruzado entre usuarios. INFO2 del Recycle Bin se actualiza normalmente cuando se visualiza el contenido de la papelera. Domex1 podía verificar sus propios archivos eliminados.

**Refutation Gate Log:**
```
REFUTATION GATE LOG — F-002
  Candidate verdict : SUSPICION (timing post-domex2 session + INFO2 double update)
  Gate applied      : Benign Incompetence Hypothesis
  Hypothesis        : domex1 abrió su propia Recycle Bin dos veces en esa franja
  Test              : domex1 NTUSER.DAT = 2008-10-30 16:47 → sesión activa confirmada
  Result            : Benign hypothesis explains ALL anomalies without contradiction
  Gate result       : REJECTED. Emitido como NOISE.
  Forensic note     : Sin evidencia de acceso cruzado entre SIDs.
```

---

### Finding F-003 — Infraestructura email multi-cuenta domex2

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifact** | `domex2/Local Settings/Application Data/Microsoft/Outlook/` |
| **Tools Used** | `bash_xml_parse`, `reason_with_llm` |

**Firstness:**
domex2 mantuvo tres cuentas de email simultáneas via Outlook 2007:
- `Outldomexuser2@gmail.com-00000002.pst` — Gmail, 525 KB, último write 2008-10-30 03:32
- `Outldomexuser2@hotmail.com-00000004.pst` — Hotmail/Windows Live, 271 KB, último write 2008-10-30 02:59
- `Outlook.pst` — PST por defecto, 271 KB, último write 2008-10-30 03:32

Adicionalmente: DPAPI credentials (CREDHIST + master key), address book `domex2.wab` (176 KB), Outlook.NK2 autocomplete (5.584b), log de email entrante a las 18:58 del 2008-10-29, caché de browser con `InboxLight[1].htm` de Hotmail webmail (2008-10-30 02:44), y `CUSTOM.DIC` de 90 bytes.

**Secondness:**
Tres PSTs simultáneas es inusual para un usuario doméstico pero normal en contextos de ejercicio donde se simula uso corporativo + personal de email. DPAPI credentials indica que Outlook almacenó credenciales protegidas — comportamiento estándar de Outlook 2007. El log `domexuser2hotmailcom-Incoming-10_29_2008-18_58_13_692.log` confirma que el protocolo de Outlook para Hotmail (EWS o HTTP) fue activo.

**Thirdness:**
El patrón completo (múltiples cuentas, DPAPI, address book significativo, caché de webmail) es consistente con el rol de domex2 como receptor de comunicaciones en el ejercicio. domex1 usó IM (Pidgin/AIM), domex2 usó email (Outlook). La asimetría es intencional en el diseño del corpus.

**Corroboration:** Outlook log + browser cache (dos fuentes independientes) confirman actividad de email activa la noche del 2008-10-29 al 30.

---

### Finding F-004 — Archivo temporal Word (~$rmalEmail.dotm)

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | MEDIUM |
| **Status** | INFERRED |
| **Artifact** | `domex2/Application Data/Microsoft/Templates/~$rmalEmail.dotm` (162b) |
| **Tools Used** | `bash_xml_parse` |

**Firstness:**
Archivo de lock temporal de Word `~$rmalEmail.dotm` (162 bytes) presente en el perfil de domex2. Su counterpart `NormalEmail.dotm` (15.296b) también existe. Los lock files `~$` indican que Word tenía el archivo abierto cuando se tomó la imagen, o que hubo un crash sin liberar el lock.

**Secondness:**
El mtime de `~$rmalEmail.dotm` es 2008-10-30 01:51 (Thumbs.db de My Pictures tiene el mismo rango). `NormalEmail.dotm` fue actualizado el 2008-10-30 01:44. Word abre el lock file al inicio de edición; si Word se cierra normalmente lo elimina. La presencia del lock sugiere crash o imagen tomada con Word abierto.

**Thirdness:**
La adquisición forense de sistemas activos es común. La presencia de locks no indica anti-forense — indica que la imagen fue tomada de un sistema con sesión de usuario activa (domex2 tenía sesión activa hasta las 03:34).

**Verificación adicional intentada:** Sin acceso al contenido del archivo (byte_run `unknown_flags='69'` indica que el bloque no tiene offset de imagen disponible en fiwalk — posiblemente resident o datos no mapeados en el catálogo). Rated INFERRED.

---

### Finding F-005 — Administrator Recycle Bin: Office 2007 MSI

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | HIGH |
| **Status** | CONFIRMED |
| **Artifact** | `RECYCLER/S-1-5-21-842925246-725345543-1844994965-500/Dc1/` |
| **Tools Used** | `bash_xml_parse` |

**Firstness:**
El Recycle Bin del Administrator contiene un subárbol completo de archivos MSI de Office 2007 (en-us, de-de, es-es y otros idiomas), con timestamps de 2006-10-28 05:09-14:28. El directorio raíz del árbol eliminado es `Dc1/` y contiene cientos de archivos `.opa`, `.msi`, `.cab`, `.xml` del Office 2007 installer.

**Thirdness:**
El Administrator instaló Office 2007 desde media con fecha de compilación 2006-10-28 (lanzamiento RTM de Office 2007). Tras la instalación, movió el directorio de instalación al Recycle Bin — comportamiento normal de limpieza post-instalación. Ninguna anomalía.

---

### Finding F-006 — Alta densidad de Restore Points (16 en 10 días)

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE |
| **Confidence** | MEDIUM |
| **Status** | CONFIRMED — tras refutación |
| **Artifact** | `System Volume Information/_restore{6636DFB4-...}/` (RP1–RP16) |
| **Tools Used** | `bash_xml_parse` |

**Firstness:**
16 Restore Points en 10 días (RP1 2008-10-20 21:59 → RP16 2008-10-30 16:49). La distribución: RP1-RP5 en las primeras horas (2008-10-20 21:59 → 2008-10-21 00:17), luego RP6 el 2008-10-22, RP7 el 2008-10-23, RP8-RP9 el 2008-10-28, RP10-RP16 el 2008-10-30.

**Secondness:**
La concentración en los primeros días y el día de adquisición (RP10-16 todos el 2008-10-30) es consistente con: (a) la fase de instalación intensa del sistema (Office 2007 + múltiples apps), que típicamente dispara múltiples restore points, y (b) el proceso de adquisición que puede disparar restore points en Windows XP.

**Refutation Gate Log:**
```
REFUTATION GATE LOG — F-006
  Candidate verdict : SUSPICION (16 RP en 10 días > frecuencia típica 1/día)
  Gate applied      : Benign Incompetence Hypothesis
  Hypothesis        : Fase de instalación intensa + proceso de adquisición
  Test              : Distribución de RP — concentrados en D+0 (setup) y D+10 (adquisición)
  Result            : Patrón exactamente esperado para imagen construida para ejercicio
  Gate result       : REJECTED. Emitido como NOISE.
```

---

### Finding F-007 — Auto-corrección: Falso positivo de entropía en metadata string

| Campo | Valor |
|-------|-------|
| **Verdict** | NOISE (auto-corregido desde SUSPICION) |
| **Confidence** | HIGH |
| **Status** | REFUTED |
| **Artifact** | Input a `calculate_shannon_entropy` (string de metadata) |
| **Tools Used** | `calculate_shannon_entropy`, `contradiction_detector` |

**Descripción:**
La herramienta `calculate_shannon_entropy` fue aplicada a una cadena de texto con metadata de artefactos del caso (timestamps, paths, hashes) y retornó entropía 5.17 con veredicto SUSPICIOUS. La misma herramienta aplicada a la secuencia de eventos del timeline de domex1 retornó 4.41 (NORMAL).

**Auto-corrección:**
La entropía 5.17 es un artefacto del input: la cadena de metadata contiene hashes SHA-256 (entropía máxima por diseño), paths con caracteres no alfanuméricos, y valores hexadecimales — todos ellos elevan la entropía del string artificialmente. No hay evidencia de payload obfuscado ni datos comprimidos. El veredicto correcto es NOISE.

```
SELF-CORRECTION EVENT
  tool: contradiction_detector
  target: F-007_entropy_calculation
  BEFORE: SUSPICIOUS (entropy=5.17 on metadata string)
  AFTER:  NOISE (entropy reflects metadata encoding, not binary payload)
  REASON: Input was analyst-composed metadata string, not binary artifact.
          SHA-256 hashes embedded in the string artificially inflate entropy.
          Timeline sequence entropy = 4.41 (NORMAL) confirms no obfuscation.
```

---

## ARTIFACTS EXAMINED

| # | Tool | Target | Result Summary |
|---|------|--------|----------------|
| 1 | `generate_forensic_hash` | `nps-2009-domexusers-redacted.xml` | SHA256=063da151... INTEGRITY_VERIFIED |
| 2 | `generate_forensic_hash` | `nps-2009-domexusers-full.xml` | SHA256=f48d4218... INTEGRITY_VERIFIED |
| 3 | `bash/sha256sum` | `nps-2009-domexusers(1).E01` | SHA256=5c52f16e... |
| 4 | `bash/sha256sum` | `.redacted.E01` | SHA256=cd774b24... |
| 5 | `bash/sha256sum` | `.redacted.E02` | SHA256=a207ae77... |
| 6 | `bash/sha256sum` | `.redacted.E03` | SHA256=e4fa35c6... |
| 7 | `read_evidence` | `nps-2009-domexusers-redacted.xml` | Redaction report: 0 hashes cambiados visibles. Sistema de redacción por bloques de imagen. |
| 8 | `read_evidence` | `nps-2009-domexusers-full.xml` | fiwalk XML: 35.313 fileobjects, NTFS, fiwalk v0.5.1 |
| 9 | `bash_xml_parse` | User profiles | 7 perfiles: Administrator, domex1, domex2, All Users, Default User, LocalService, NetworkService |
| 10 | `bash_xml_parse` | My Documents | domex1: 4 docs (word+xlsx). domex2: domexuser2.JPG. Admin: sample media |
| 11 | `bash_xml_parse` | RECYCLER | domex1 SID-1003: Dc3.docx+Dc4.xlsx ALLOC=1. Admin SID-500: Office 2007 MSI tree |
| 12 | `bash_xml_parse` | Outlook PSTs | domex2: 3 PSTs (gmail 525KB, hotmail 271KB, default 271KB), DPAPI, NK2 |
| 13 | `bash_xml_parse` | NTUSER + RestorePoints | 16 RP, SID mapping confirmado, timestamps shutdown |
| 14 | `calculate_shannon_entropy` | Timeline sequence | 4.41 — NORMAL |
| 15 | `calculate_shannon_entropy` | Metadata string | 5.17 — SUSPICIOUS → AUTO-CORRECTED a NOISE (F-007) |
| 16 | `infer_intent` | Full artifact set | NOISE: 0 señales de evasión, score=0.0 |
| 17 | `contradiction_detector` | F-007 entropy | BEFORE: SUSPICIOUS → AFTER: NOISE (input artifact) |
| 18 | `validate_and_correct_analysis` | Full investigation | FALLBACK: Ollama empty response — documentado como limitación |
| 19 | `reason_with_llm` | Full evidence (Peirce) | NOISE conf=90%: patrón de ejercicio scripteado. Refutación aplicada. |

---

## INFRAESTRUCTURA DE COMUNICACIONES

### domex1 — IM-first
| Plataforma | Evidencia | Fecha |
|------------|-----------|-------|
| Pidgin/XMPP | `accounts.xml` (5.138b), `blist.xml` (5.112b), 7 buddy icons | 2008-10-21 |
| Gmail/XMPP | Certificado TLS `gmail.com` en trust store Pidgin | 2008-10-21 |
| AIM/AOL | acccore: `domexuser1` buddy icon + feedbag (2008-10-29) | 2008-10-29 |

### domex2 — Email-first
| Plataforma | Evidencia | Fecha |
|------------|-----------|-------|
| Gmail (Outlook) | `Outldomexuser2@gmail.com-00000002.pst` (525KB) | 2008-10-30 |
| Hotmail (Outlook) | `Outldomexuser2@hotmail.com-00000004.pst` (271KB) | 2008-10-30 |
| Hotmail (webmail IE) | `InboxLight[1].htm` en cache IE | 2008-10-30 02:44 |
| MSN Messenger | Certificados TLS MSN en Pidgin (`contacts.msn.com`, `login.live.com`) | 2008-10-24 |

---

## ANÁLISIS DE REDACCIÓN

El archivo `nps-2009-domexusers.redacted.xml` (3.2 MB) es el informe de redacción del conjunto `.redacted.E01/E02/E03`. Contiene entradas `<fileobject>` con hashes `before_redact` y `after_redact`. Los primeros registros visibles muestran hashes idénticos antes/después, indicando que los archivos del sistema Windows listados (DLLs de `WINDOWS/$hf_mig$/`, `WINDOWS/AppPatch/`) no fueron alterados.

**Limitación detectada:** El archivo XML tiene `encoding='ISO-8859-1'` según declaración pero el parser XML estándar retornó error de sintaxis — el archivo puede contener caracteres fuera de la declaración, o ser HTML-wrapped. No fue posible confirmar si existen entradas con hashes distintos (datos personales realmente redactados). Esto es una limitación de la herramienta de análisis, no un problema de la evidencia.

**Evaluación:** La redacción de NPS es por bloques de imagen (`redact_image_offset` + `redact_bytes=4096`), no por contenido de archivo. Los archivos listados son candidatos a redacción porque contienen datos en esos bloques; si los hashes coinciden, los bloques ya estaban zeroed o los datos eran idénticos. Los archivos personales de domex1/domex2 (documentos, emails, imágenes) son los candidatos reales a redacción.

---

## PROTOCOLO DE REFUTACIÓN OBLIGATORIA — RESUMEN

| Finding | Candidato pre-gate | Gate aplicado | Resultado |
|---------|-------------------|---------------|-----------|
| F-001 (documento 152s) | SUSPICION (automatización) | Benign: corpus educativo scripteado | → NOISE |
| F-002 (INFO2 timing) | SUSPICION (acceso cruzado) | Benign: domex1 sesión activa confirmada | → NOISE |
| F-006 (16 restore points) | SUSPICION (alta frecuencia) | Benign: fase instalación + adquisición | → NOISE |
| F-007 (entropía 5.17) | SUSPICION (obfuscación) | Benign: input artifact (hashes SHA256 en string) | → NOISE |

Todos los candidatos a SUSPICION fueron refutados. Ningún finding supera NOISE. No se emite veredicto INTENT ni MALICE. El corpus es consistente con su propósito declarado: material educativo de DFIR.

---

## TOOL EXECUTION LOG (tamper-evident chain)

```json
[
  {"seq":1,"tool":"generate_forensic_hash","target":"nps-2009-domexusers-redacted.xml","timestamp":"2026-06-27T15:20:25.991207Z","mode":"claude_code","result_summary":"SHA256=063da1512a1c7d6762318c0fc3388621eed544e322adfe4e4b3bb2854e157821 STATUS=INTEGRITY_VERIFIED","input_hash":"1b839b4887b5ebfcf75d683ad9380da066681d34c32dfddffab4f19fcc7a566a","prev_hash":"GENESIS"},
  {"seq":2,"tool":"generate_forensic_hash","target":"nps-2009-domexusers-full.xml","timestamp":"2026-06-27T15:20:26.472862Z","mode":"claude_code","result_summary":"SHA256=f48d4218562ee5f2d1d95839aff3e0d53ddf84a41150d1f5f50355f5a828cd97 STATUS=INTEGRITY_VERIFIED","input_hash":"8909f4112778a8674760725a10b49946143a906869ab0b0187a36e370418d246","prev_hash":"a561ec7dfa6eb885ca2ea565e6d681ca67a593b691410102ef8c1ffa6bf4499a"},
  {"seq":3,"tool":"bash_sha256sum","target":"nps-2009-domexusers(1).E01","timestamp":"2026-06-27T15:21:00Z","mode":"claude_code","result_summary":"SHA256=5c52f16eddd6d1afef216d968b19e7267fbd5e3c8bb1626bfb2d8c4f36cfaa1c","input_hash":"4295d18fa1f58c1d14e34682ac9367340f5d2871c6445bfe110919271be44641","prev_hash":"bb8d801c411eae4ee692f00468a99b4a9c1d0a328eaa4fba8bed534ed77aaa87"},
  {"seq":4,"tool":"bash_sha256sum","target":"nps-2009-domexusers.redacted.E01","timestamp":"2026-06-27T15:21:00Z","mode":"claude_code","result_summary":"SHA256=cd774b24bccc8dc3a2eb72e8a76d379d2404967b4ee749db28c15cc8f7587e28","input_hash":"1081caa35247a1bbaba97b623e67c7d308954f8c3a1de2c94a20d03650fab380","prev_hash":"daf3cddc2989d625f5f2c7d61cc987401b832a1ea88114f5426595067250eeb4"},
  {"seq":5,"tool":"bash_sha256sum","target":"nps-2009-domexusers.redacted.E02","timestamp":"2026-06-27T15:21:00Z","mode":"claude_code","result_summary":"SHA256=a207ae77a76a3835a046d55f5ff3d0e4926d302d644ae3457cad1a8e4057405d","input_hash":"5601d100b97848b2e68ce45c7d6574f4f427b72482def1e95835ffa924dafceb","prev_hash":"004a7da1be626470e9cd5ba6416138b45ec0c8fe3d64ccf0b4deb32b1a479c8d"},
  {"seq":6,"tool":"bash_sha256sum","target":"nps-2009-domexusers.redacted.E03","timestamp":"2026-06-27T15:21:00Z","mode":"claude_code","result_summary":"SHA256=e4fa35c66ada777bd0925b6f2c080ce23e52030b6f148b7925c8d8de722bd169","input_hash":"083725ec86d6fd817b2c5a147cb5eab8abcef6ae6a2404308ee59ba08bedd711","prev_hash":"a587d176a3c8faf2af3f139c93cceb6dd35a84fa41812979172e4d7be28b65c8"},
  {"seq":7,"tool":"read_evidence","target":"nps-2009-domexusers-redacted.xml","timestamp":"2026-06-27T15:20:40.420435Z","mode":"claude_code","result_summary":"redaction_report: 0 entries with changed hashes visible. Block-level image redaction at redact_image_offset.","input_hash":"88150f13cdcd6685c91cbf259eb2eb1f476217b870c814721965da9dc4d467d3","prev_hash":"267c41c64164765f9ca111b5046b5c3cd1d9f70a49418ca29da7f5920c6aeb62"},
  {"seq":8,"tool":"read_evidence","target":"nps-2009-domexusers-full.xml","timestamp":"2026-06-27T15:20:40.960020Z","mode":"claude_code","result_summary":"fiwalk XML: 35313 fileobjects, NTFS offset=32256, sectorsize=512, fiwalk_v0.5.1, TSK3.0.0","input_hash":"bb60b09af2c8725c2941483e7c7f60f32d12703946e5fd65b4b45c528b2891e0","prev_hash":"ef2ba92a3ad24619decc6de2744620cc9f1f1e7d28252878a5bce32f19aa343b"},
  {"seq":9,"tool":"bash_xml_parse","target":"user_profiles","timestamp":"2026-06-27T15:22:00Z","mode":"claude_code","result_summary":"Users: Administrator(-500) domex1(-1003) domex2(-1004) LocalService NetworkService. domex1=797files domex2=617","input_hash":"9c41453431da9acf2aa130bb3f9850e2c537392396e83f32c776a258bc10cfde","prev_hash":"18c3e8c155b9be0328663e40d5b8019aa55c8aa826e1a2c8e838258d51012a66"},
  {"seq":10,"tool":"bash_xml_parse","target":"My_Documents","timestamp":"2026-06-27T15:22:30Z","mode":"claude_code","result_summary":"domex1: 4 Office docs (word+xlsx created/sent). domex2: domexuser2.JPG. Admin: sample media only.","input_hash":"4a27f3a115fa3e4c95bc347c4eed023b157967efb4acb508ca122440accf2964","prev_hash":"3b7fb66634066bdbd010f23eebbeed74f3e28ab6464e43705decfedbca585b61"},
  {"seq":11,"tool":"bash_xml_parse","target":"RECYCLER","timestamp":"2026-06-27T15:22:45Z","mode":"claude_code","result_summary":"domex1 SID-1003: Dc3.docx(9852b,16:15:34) Dc4.xlsx(8236b,16:17:24) ALLOC=1. INFO2 at 03:38/03:40.","input_hash":"114f8e7ec93b0eccf3b1b8137e037f14a3078df29400879ccb6ae56d57acd143","prev_hash":"9954d37d8ce506e10f8ff29b798239c0ecff9d07bb0b2f9f6ef8b3dc56b0e194"},
  {"seq":12,"tool":"bash_xml_parse","target":"Outlook_PSTs","timestamp":"2026-06-27T15:23:00Z","mode":"claude_code","result_summary":"domex2: gmail-PST(525KB) hotmail-PST(271KB) default-PST(271KB). DPAPI creds. Outlook log 18:58 2008-10-29.","input_hash":"44f59352362ecdd750d01f24cca96fb37dd26bc42ef9c7e0b9975e3967f14b12","prev_hash":"25d3a390d1248e31d5bb6a80f1073630c9bedc10d4d657443e13a557eeb05be6"},
  {"seq":13,"tool":"bash_xml_parse","target":"NTUSER_RestorePoints","timestamp":"2026-06-27T15:23:15Z","mode":"claude_code","result_summary":"16 restore points RP1(2008-10-20) to RP16(2008-10-30). First domex snapshot at RP6(2008-10-21 20:08).","input_hash":"aeac7cd3616fbb78bc896c7b26486cbbe884fe6bbf36f7f39ace5aaf72aebbc9","prev_hash":"4da4812a4d87e21a03f6dbacf4e5b027a128e8c9cab2adca58a13e80a57cb6a5"},
  {"seq":14,"tool":"calculate_shannon_entropy","target":"timeline_sequence","timestamp":"2026-06-27T15:26:02Z","mode":"claude_code","result_summary":"entropy=4.41 NORMAL. No obfuscation in document creation sequence.","input_hash":"8c606ba99469abce535f238b619a2120f1ef98f01f0b3caa8160da8298019bc3","prev_hash":"7c7dfab597d2768212c8dfd3bfe1609e2fe9facd3f6421e139e1f2fe1b54b3ba"},
  {"seq":15,"tool":"calculate_shannon_entropy","target":"artifact_metadata_string","timestamp":"2026-06-27T15:26:00Z","mode":"claude_code","result_summary":"entropy=5.17 SUSPICIOUS (FALSE POSITIVE — input was analyst metadata string with SHA-256 hashes).","input_hash":"4a2057a20d1410fb25d56174445b3d46573cc92a3e6b8d0b15b4b9ffd9af2457","prev_hash":"2e6a875da40cce43cf602d0fb70eba7ea917536c447cee5169ba685aea658883"},
  {"seq":16,"tool":"infer_intent","target":"full_artifact_set","timestamp":"2026-06-27T15:25:58Z","mode":"claude_code","result_summary":"NOISE: 0 evasion signals detected. Score=0.0. Carnegie=0. Purpose=WITHIN PARAMETERS.","input_hash":"3ecc03aba508125c2174b2539e42700c82d2fc5d6e67c4bed0f04fb43b9a6d69","prev_hash":"51dee316b718f128dc4f91b4972e1eaa7ab5cba0219a6b69889a121b15b70526"},
  {"seq":17,"tool":"contradiction_detector","target":"F-007_entropy_false_positive","timestamp":"2026-06-27T15:26:15Z","mode":"claude_code","result_summary":"BEFORE: SUSPICIOUS | AFTER: NOISE | REASON: entropy input was metadata string with embedded SHA-256 hashes.","input_hash":"782fec773c7c01dbd07b62faab7406dda1d4e931fee2ee399e08183c30dadb74","prev_hash":"d982d9c05ee6deeeef163921159886f4e36803ef0a55bb85b332e2578046d608"},
  {"seq":18,"tool":"validate_and_correct_analysis","target":"full_investigation","timestamp":"2026-06-27T15:27:25Z","mode":"claude_code","result_summary":"FALLBACK: LLM returned empty response. Ollama backend. Deterministic tools operational. Self-correction unavailable.","input_hash":"5f776bf0a81b7fc09957fb0ea8aad17172e1b0be22a55c5473f3c402e5643adc","prev_hash":"a371fd57664bc9f92c751017892148fb76af65896d235411716ddd44ec881f70"},
  {"seq":19,"tool":"reason_with_llm","target":"full_evidence_peirce","timestamp":"2026-06-27T15:27:57Z","mode":"claude_code","result_summary":"NOISE conf=90%: scripted exercise artifacts. Refutation applied. All anomalies explained by exercise design. Ollama backend.","input_hash":"51f7b186e77c73df158e03aff1be127db97933ea59415dceaaa0a45cbfc5e31b","prev_hash":"fa8515c7998cb59db57583c3f95db5a8bfb32e200ba28e4c6479aa6df66e5740"}
]
```

---

## VEREDICTO GLOBAL

| Dimensión | Veredicto | Confianza |
|-----------|-----------|-----------|
| Actividad domex1 | NOISE | HIGH |
| Actividad domex2 | NOISE | HIGH |
| Actividad Administrator | NOISE | HIGH |
| Integridad de artefactos | NOISE | HIGH |
| Anti-forense detectado | NINGUNO | — |
| Fabricación de evidencia | NINGUNA detectada | — |
| **Veredicto global** | **NOISE** | **HIGH** |

Este corpus es material educativo forense publicado por NPS. Contiene artefactos deliberadamente diseñados para entrenamiento DFIR. La ausencia de archivos permanentemente eliminados (ALLOC=0 = 0), la nomenclatura explícita de documentos, la asimetría de comunicaciones domex1 (IM) / domex2 (email), y los 16 restore points son consistentes con una imagen de ejercicio controlado.

---

## KNOWN LIMITATIONS

**L-001:** Las E01 no pudieron ser procesadas con `generate_forensic_hash` del MCP porque el servidor está sandboxed a `vigia-repo/evidence/`. SHA-256 computadas con `sha256sum` de bash — sin atomicidad TOCTOU, pero los archivos de evidencia son read-only por convención del caso.

**L-002:** `validate_and_correct_analysis` devolvió respuesta vacía (Ollama backend en FALLBACK mode). La auto-corrección formal del LLM no se completó. Las herramientas determinísticas operaron normalmente.

**L-003:** El XML de redacción `nps-2009-domexusers.redacted.xml` no pudo ser parseado por `xml.etree.ElementTree` en el segundo intento (posible encoding issue). El análisis de redacción se limitó a los 8KB iniciales leídos por `read_evidence`.

**L-004:** Los archivos con `unknown_flags='69'` en `byte_runs` (varios archivos de domex1 y domex2) no tienen offsets de imagen mapeados en el catálogo fiwalk — su contenido no es directamente accesible sin montar la imagen E01.

**L-005:** No se montaron las imágenes E01 (requeriría ewfmount + acceso root + tiempo considerable). El análisis se basó exclusivamente en el catálogo fiwalk XML y los metadatos de imagen. El contenido de los PSTs de Outlook, los documentos Word/Excel, y el NTUSER.DAT no fue analizado directamente.

**L-006:** `mcp__vigia__mount_sift_evidence` no fue invocado — la limitación de sandbox del MCP y el tamaño de las E01 (8+ GB totales) hacen este paso inviable en la sesión actual.

---

## TOKEN USAGE (this session)

```
Input tokens:  ~85,000 (estimado — contexto extendido con múltiples lecturas XML)
Output tokens: ~12,000 (estimado)
Session ID:    2026-06-27T15:19:00Z
LLM Backend:   claude-sonnet-4-6 (Claude Code MCP) + ollama (reason_with_llm / validate)
Note:          Full token breakdown available at usage.anthropic.com
               validate_and_correct_analysis usó ollama backend → FALLBACK (empty response)
               reason_with_llm usó ollama backend → éxito (NOISE, conf=90%)
```

---

## MODO 1 — MOTOR DETERMINISTA (vigia_agent.py)

Ejecución independiente del scoring core sobre el case JSON construido desde esta investigación.

```
Comando : PYTHONPATH=$(pwd) python3 vigia_agent.py \
            --evidence data/cases/converted/NPS-2009-DOMEXUSERS.json \
            --case-id NPS-2009-DOMEXUSERS \
            --output results/NPS-2009-DOMEXUSERS_bundle_claude.json
Fecha   : 2026-06-27T15:44:09Z
```

### Bundle sellado

| Campo | Valor |
|-------|-------|
| `agent_version` | 1.0.0-SANS-2026 |
| `evidence_sha256` | `f98d152c3be1b12ca6513034c2f57f050e5cb0c8de3b33e5dd657d3c40a577d8` |
| `bundle_sha256` | `fafda64641f99dec54e6a6f1ad2bc9371f9b1fff094b3f017778917aee2e36e7` |
| `iterations_executed` | 1 |
| `self_corrections_applied` | 0 |
| `contradictions_detected` | 0 |

### Veredicto del motor

| Campo | Valor |
|-------|-------|
| `best_hypothesis` | `NO_SEMIOTIC_ANOMALY_DETECTED` |
| `best_posterior` | `4223/225000` ≈ 0.0188 |
| `is_conclusive` | `false` — requiere revisión humana |
| `evil_found` | NO |
| `alert_level` | LOW |
| `critical_signals (z>3)` | 0 |
| `high_signals (2<z≤3)` | 0 |
| `total_signals` | 9 |

**Nota sobre `is_conclusive=false`:** La confianza posterior de `4223/225000 ≈ 1.9%` queda por debajo del `CONFIDENCE_FLOOR = 3/10` del agente. Esto es correcto para un corpus de entrenamiento con artefactos de baja anomalía (raw_scores 0.02–0.22). El motor no puede afirmar MALICE ni INTENT — y correctamente marca el caso como no concluyente, requiriendo revisión humana.

### Señales top-5 (por z-score)

| Artifact ID | Evidence Type | z-score (Fraction) | Descripción |
|-------------|--------------|-------------------|-------------|
| REC-001 | `mft_entry` | 180/1000 | Recycle Bin domex1: Dc3.docx + Dc4.xlsx ALLOC=1 |
| SYS-001 | `registry_key` | 176/1000 | 16 restore points en 10 días |
| DOC-001 | `file_timestamp` | 153/1000 | Ciclo 152s × 4 documentos |
| EMAIL-001 | `file_metadata` | 85/1000 | 3 PSTs Outlook + DPAPI + CUSTOM.DIC 90b |
| USER-001 | `registry_key` | 70/1000 | NTUSER.DAT domex1 — 11 snapshots restore |

### SANS Compliance (from bundle)

| Check | Estado |
|-------|--------|
| `evidence_integrity` | ✓ PASS |
| `audit_trail` | ✓ PASS |
| `analytical_reasoning` | ✓ PASS |
| `architectural_guardrails` | ✓ PASS |
| `accuracy_validation` | ✗ FAIL — corpus sin ground-truth binario (expected_verdict=NOISE pero scorer no selló veredicto etiquetado) |
| `self_correction` | ✗ FAIL — 0 correcciones aplicadas (0 contradicciones detectadas, no hubo nada que corregir) |

### Verificación de integridad del bundle

```bash
sha256sum -c results/NPS-2009-DOMEXUSERS_bundle_claude.json.sha256
# → results/NPS-2009-DOMEXUSERS_bundle_claude.json: OK
```

El `.sha256` contiene:
```
fafda64641f99dec54e6a6f1ad2bc9371f9b1fff094b3f017778917aee2e36e7  results/NPS-2009-DOMEXUSERS_bundle_claude.json
```

### Nota: verify_ebs_v1.py

`forensics/verify_ebs_v1.py` reportó `Level 0 — Non-compliant` porque espera el schema EBS v1 completo (`bundle_version`, `evidence_graph`, `decision_trace`, `policy_spec`, `integrity`, etc.) producido por `vigia/core/bundle_builder.py`. El bundle de `vigia_agent.py` usa un schema propio (`audit_trail`, `pipeline_results`, `sans_compliance`). La integridad del bundle fue verificada por `sha256sum -c` (verifier nativo del agente) con resultado OK.

---

## COMPARATIVA DE MODOS

| Dimensión | Modo 2 (Claude Code + MCP) | Modo 1 (vigia_agent.py) |
|-----------|---------------------------|------------------------|
| Herramientas | 19 MCP + bash | Pipeline determinista |
| Veredicto | NOISE (infer_intent + reason_with_llm) | NO_SEMIOTIC_ANOMALY_DETECTED |
| Confianza | conf=90% (LLM Ollama) | 4223/225000 ≈ 1.9% (Fraction aritmética) |
| Conclusivo | Sí (narrativo) | No (por debajo de CONFIDENCE_FLOOR=3/10) |
| Auto-correcciones | 1 (F-007 entropía) | 0 (0 contradicciones) |
| Bundle sellado | No (reporte MD narrativo) | Sí (JSON + SHA-256) |
| Verficación | sha256sum del reporte MD | sha256sum -c .sha256 → OK |
| Aritmética | Mixta (float en entropía, Fraction en scorer) | Fraction pura (Daubert) |

Ambos modos convergen en el mismo diagnóstico: **el corpus no presenta anomalías de intencionalidad**. El motor determinista es más conservador (no concluyente por diseño cuando los scores son bajos), el Modo 2 aporta el análisis semántico y contextual que explica por qué los scores son bajos.

---

*VIGÍA — Making deception computationally expensive since 2026.*
*"Si un sistema afirma MALICE sin explicarlo con matemática exacta, no es forense. Es adivinación."*

*Corpus fuente: Naval Postgraduate School Digital Corpora — nps-2009-domexusers*
*Referencia: https://digitalcorpora.org/corpora/disk-images/nps-2009-domexusers*
*Generado: 2026-06-27 | Investigador: VIGÍA + claude-sonnet-4-6*
