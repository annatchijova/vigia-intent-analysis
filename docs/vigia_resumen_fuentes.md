# Resumen de Fuentes Forenses - Dataset VIGIA

## Fuentes Revisadas y Casos Extraidos

Se analizaron 10 casos forenses reales provenientes de 6 fuentes públicas distintas. A continuacion se detalla el origen, cantidad de casos y caracteristicas de cada dataset.

---

### 1. NIST CFReDS (Computer Forensic Reference Data Sets)

**URL**: https://cfreds.nist.gov/
**Casos extraidos**: 2
**Calidad**: Alta - Datasets forenses con evidencia real y documentacion detallada

| Case ID | Nombre | Veredicto |
|---------|--------|-----------|
| VIGIA-REAL-001 | NIST Hacking Case (Greg Schardt / Mr. Evil) | MALICE |
| VIGIA-REAL-002 | NIST Data Leakage Case (Sr. Informant) | MALICE |

**Notas**: El Hacking Case incluye una imagen completa de disco de una laptop Dell usada para war driving, con herramientas de hacking (NetStumbler, Ethereal), capturas pcap de trafico interceptado, y registros que vinculan al sospechoso. El Data Leakage Case documenta un insider threat con secuencia completa de exfiltracion via Google Drive, renombrado de archivos y uso de herramientas anti-forenses.

---

### 2. Ali Hadi DFIR Challenges

**URL**: https://www.ashemery.com/dfir.html / https://www.binary-zone.com/
**Casos extraidos**: 4
**Calidad**: Muy Alta - Escenarios creados por un profesional de DFIR con artefactos realistas

| Case ID | Nombre | Veredicto |
|---------|--------|-----------|
| VIGIA-REAL-003 | Ali Hadi Web Server Compromise | MALICE |
| VIGIA-REAL-004 | Ali Hadi SysInternals Malware Case | MALICE |
| VIGIA-REAL-005 | Ali Hadi Encrypt Them All Case | SUSPICION |

**Notas**: Los challenges de Ali Hadi son reconocidos en la comunidad DFIR. El Web Server Case muestra un ataque completo SQLi→webshell→RDP. El SysInternals Case demuestra masquerading y tecnicas anti-forenses. El Encrypt Them All Case presenta un escenario de sospecha con multiples capas de cifrado sin evidencia de delito concreto.

---

### 3. Digital Corpora

**URL**: https://digitalcorpora.org/
**Casos extraidos**: 2
**Calidad**: Muy Alta - Datasets forenses con discos completos, trafico de red y emails reales

| Case ID | Nombre | Veredicto |
|---------|--------|-----------|
| VIGIA-REAL-006 | Digital Corpora M57-Jean Spear-Phishing | NOISE |
| VIGIA-REAL-007 | Digital Corpora Nitroba Harassment | MALICE |

**Notas**: Digital Corpora proporciona escenarios completos con multiples discos, capturas de red y documentacion. El caso M57-Jean es interesante porque la victima (Jean) actuo de buena fe, por lo que el veredicto es NOISE. El caso Nitroba incluye un pcap de ~60MB con cookies en plaintext.

---

### 4. Volatility Foundation

**URL**: https://github.com/volatilityfoundation/volatility/
**Casos extraidos**: 1
**Calidad**: Alta - Volcados de memoria RAM de sistemas reales infectados

| Case ID | Nombre | Veredicto |
|---------|--------|-----------|
| VIGIA-REAL-008 | Volatility Cridex Banking Trojan | MALICE |

**Notas**: La muestra cridex.vmem es un clasico en analisis de memoria. Muestra process injection, hidden processes, conexiones C&C y robo de credenciales bancarias. Ideal para probar deteccion de malware bancario.

---

### 5. DFRWS (Digital Forensics Research Workshop)

**URL**: https://dfrws.org/forensic-challenges/
**Casos extraidos**: 2
**Calidad**: Alta - Desafios forenses de conferencias academicas reconocidas

| Case ID | Nombre | Veredicto |
|---------|--------|-----------|
| VIGIA-REAL-009 | DFRWS 2008 Linux Exfiltration | MALICE |
| VIGIA-REAL-010 | DFRWS 2011 Android Espionage | MALICE |

**Notas**: Los desafios de DFRWS incluyen volcados de memoria Linux y discos Android. El caso 2008 muestra exfiltracion via script Perl con proxy externo. El caso 2011 combina espionaje industrial con malware movil y un elemento criminal (asesinato del sospechoso).

---

## Datasets Evaluados pero Descartados

### NIST CFReDS - Other Cases
Los casos adicionales de NIST CFReDS (Router, Honeynet, etc.) fueron revisados pero no incluidos porque:
- **Router Case**: Foco en configuracion de red, menos artefactos forenses de endpoint
- **Honeynet Case**: Demasiado orientado a trafico de red sin artefactos de host

### MUS2018 / MUS2019 (Michigan)
Revisados en https://digitalcorpora.org/ pero descartados porque:
- Los casos son menos documentados que M57-Jean
- Falta informacion detallada sobre artefactos especificos
- Menos variedad de tipos de artefactos

### NIST CFReDS - Windows 10 Case
Descartado porque:
- El dataset es mas reciente pero tiene menos detalle publico sobre artefactos
- La documentacion es menos especifica que los casos seleccionados

### SANS DFIR Challenges
Evaluados pero no incluidos porque:
- Requieren membresia SANS para acceso completo
- La informacion publica es insuficiente para construir artefactos detallados

---

## Resumen por Veredicto

| Veredicto | Cantidad | Casos |
|-----------|----------|-------|
| MALICE | 8 | 001, 002, 003, 004, 007, 008, 009, 010 |
| SUSPICION | 1 | 005 |
| NOISE | 1 | 006 |

---

## Distribucion de Artefactos

| Tipo de Artefacto | Cantidad Total |
|-------------------|----------------|
| file_metadata | 11 |
| bash_history | 7 |
| network_flow | 8 |
| email_header | 7 |
| process_list | 5 |
| registry | 2 |
| auth_log | 1 |
| timestamp | 1 |
| memory_string | 1 |

**Total de artefactos**: 43 (promedio 4.3 por caso, rango: 3-5)

---

## Lista Completa de Casos

1. **VIGIA-REAL-001** - NIST Hacking Case (Greg Schardt / Mr. Evil) [MALICE]
2. **VIGIA-REAL-002** - NIST Data Leakage Case (Sr. Informant) [MALICE]
3. **VIGIA-REAL-003** - Ali Hadi Web Server Compromise [MALICE]
4. **VIGIA-REAL-004** - Ali Hadi SysInternals Malware Case [MALICE]
5. **VIGIA-REAL-005** - Ali Hadi Encrypt Them All Case [SUSPICION]
6. **VIGIA-REAL-006** - Digital Corpora M57-Jean Spear-Phishing [NOISE]
7. **VIGIA-REAL-007** - Digital Corpora Nitroba Harassment [MALICE]
8. **VIGIA-REAL-008** - Volatility Cridex Banking Trojan [MALICE]
9. **VIGIA-REAL-009** - DFRWS 2008 Linux Exfiltration [MALICE]
10. **VIGIA-REAL-010** - DFRWS 2011 Android Espionage [MALICE]

---

*Generado para el motor VIGIA - Dataset forense de referencia*
