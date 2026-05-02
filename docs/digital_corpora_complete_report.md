# REPORTE COMPLETO: DIGITAL CORPORA SCENARIOS
## Proyecto de Análisis Forense Digital

---

# ESCENARIO PRINCIPAL: M57-JEAN (2008)

## Información General
| Campo | Valor |
|-------|-------|
| **Nombre** | M57-Jean |
| **Año** | 2008/2009 |
| **Tipo** | Single disk image scenario |
| **Categoría** | Corporate exfiltration / Spear-phishing |
| **Plataforma** | Windows XP |
| **Formato imagen** | EnCase E01 (multi-volumen: .E01 + .E02) |
| **MD5 Hash** | 78a52b5bac78f4e711a607707ac0e3f93 |
| **URL** | https://digitalcorpora.org/corpora/scenarios/m57-jean/ |
| **Autor** | Simson Garfinkel / NIST |

---

## Narrativa Completa

### La Empresa: M57.Biz
M57.biz es una startup de tecnología "hip" que desarrolla un catálogo de body art (arte corporal). La empresa:
- Recibió **$3M en seed funding** y estaba cerrando una ronda de **$10M**
- Tenía **2 fundadores/dueños** y **10 empleados** contratados en el primer año
- Era una **corporación virtual**: empleados trabajaban remotamente, con reuniones semanales o quincenales
- La mayoría de documentos se intercambiaban por **email**

### Personal de M57.Biz
| Nombre | Cargo | Email | Password |
|--------|-------|-------|----------|
| Alison Smith | Presidenta | alison@m57.biz | ab=8989 |
| Jean Jones | CFO (Chief Financial Officer) | jean@m57.biz | gick*1212 |
| Bob, Carole, David, Emmy | Programadores | - | - |
| Gina, Harris | Marketing | - | - |
| Indy | BizDev | - | - |

### El Incidente
A pocas semanas de la creación de la empresa, una **hoja de cálculo confidencial** que contenía los nombres, salarios y Números de Seguridad Social (SSN) de los empleados clave fue encontrada publicada en la sección de "comentarios" del sitio web de uno de los competidores de la firma.

**La hoja de cálculo SOLO existía en la computadora de Jean**, la CFO de la empresa.

### Las Declaraciones
- **Jean (CFO)** afirma que:
  - Alison (Presidenta) le pidió preparar la hoja de cálculo como parte de una nueva ronda de financiación
  - Alison le pidió enviar la hoja de cálculo por email
  - No tiene idea cómo los datos llegaron al competidor
  
- **Alison (Presidenta)** afirma que:
  - No sabe de qué habla Jean
  - Nunca pidió la hoja de cálculo
  - Nunca recibió la hoja de cálculo por email

### Tu Misión
Eres un investigador forense digital. Te han dado una imagen de disco del laptop de Jean. Tu trabajo es:
1. **¿Cuándo creó Jean esta hoja de cálculo?**
2. **¿Cómo llegó desde su computadora al sitio del competidor?**
3. **¿Quién más de la empresa está involucrado?**

---

## Timeline Completo de Eventos

### Eventos Previos (07/07/2008)
| Fecha | Hora (PDT) | Evento |
|-------|------------|--------|
| 07/07/2008 | 09:32:01 AM | Jean recibe emails de Alison con el nombre configurado como "Alison57" en el email client |
| 07/07/2008 | ~09:32 AM | En un segundo email, Alison pide explícitamente a Jean que NO le reenvíe enlaces de spam |

### El Día del Incidente: Sábado 19 de Julio / Domingo 20 de Julio de 2008

| Fecha | Hora (PDT) | Evento | Detalle |
|-------|------------|--------|---------|
| **07/19/2008** | **16:39:57** | **Email #1: "background checks"** | Jean recibe email spoofeado aparentemente de alison@m57.biz. **Return-Path real: simsong@xy.dreamhostps.com**. Reply-To: alison@m57.biz (legítimo). Contenido: Solicita hoja con empleados, salarios y SSN para "background checks de potenciales inversores". Incluye nota sospechosa: "por favor no incluyas el texto de este email en tu respuesta" |
| **07/19/2008** | **16:44:00** | **Respuesta de Jean #1** | Jean responde "Sure thing." Esta respuesta va al Reply-To legítimo (alison@m57.biz) |
| **07/19/2008** | **16:50:20** | **Alison responde** | Alison recibe la respuesta inesperada y responde "What's a sure thing?" - mostrando confusión |
| **07/19/2008** | **18:22:45** | **Email #2: "Please send me the information now"** | Jean recibe SEGUNDO email spoofeado. **Mismo Return-Path: simsong@xy.dreamhostps.com** pero ahora **Reply-To: tuckergorge@gmail.com** (MALICIOSO) |
| **07/19/2008** | **~18:28** | **Jean crea m57biz.xls** | Jean crea la hoja de cálculo confidencial con los datos de empleados |
| **07/19/2008** | **18:28:45** | **EXFILTRACIÓN** | Jean responde al email #2 adjuntando **m57biz.xls**. El email se envía a **tuckergorge@gmail.com** (atacante) en lugar de a Alison |
| **07/19/2008** | **22:03:40** | **Email #3: "Thanks!"** | El atacante envía email final de agradecimiento. Return-Path: simsong@xy.dreamhostps.com, Reply-To: tuckergorge@gmail.com |

> **Nota sobre las fechas**: Algunos reportes indican las fechas como "July 20, 2008" debido a que Outlook las muestra en la zona horaria del usuario. El análisis forense del filesystem confirma que los eventos ocurrieron en la madrugada/tarde del 19-20 de julio de 2008.

### Timeline Alternativa (según offsets de zona horaria)
| Fecha | Hora | Evento |
|-------|------|--------|
| Domingo 07/20/2008 | 10:39 AM | Email #1 "background checks" recibido por Jean |
| Domingo 07/20/2008 | 10:44 AM | Jean responde "Sure thing" |
| Domingo 07/20/2008 | 10:50 AM | Alison responde confundida |
| Domingo 07/20/2008 | 12:22 PM | Email #2 "Please send me the information now" - Reply-To cambiado a tuckergorge@gmail.com |
| Domingo 07/20/2008 | 12:28 PM | Jean envía m57biz.xls al atacante |
| Domingo 07/20/2008 | 04:03 PM | Email #3 "Thanks!" del atacante |

---

## Artefactos por Categoría

### 1. EMAILS

#### Email #1: "background checks" (Solicitud Inicial)
```
From: alison@m57.biz <alison@m57.biz>
To: jean@m57.biz
Date: July 19/20, 2008
Subject: background checks
Return-Path: simsong@xy.dreamhostps.com  [SPOOFED]
Reply-To: alison@m57.biz  [legítimo en este primer email]

Content:
"Jean,

One of the potential investors that I've been dealing with has asked me 
to get a background check of our current employees. Apparently they 
recently had some problems at some other company they funded.

Could you please put together for me a spreadsheet specifying each of 
our employees, their current salary, and their SSN?

Please do not mention this to anybody.

Thanks.

(ps: because of the sensitive nature of this, please do not include 
the text of this email in your message to me. Thanks.)"
```
**Anomalías:**
- El Return-Path real es `simsong@xy.dreamhostps.com`, NO `alison@m57.biz`
- La nota "no incluyas el texto de este email" es altamente sospechosa - intento de ocultar el rastro
- Solicitud de información extremadamente sensible (SSN + salarios) por email
- Sentido de urgencia artificial

#### Email de Respuesta #1: Jean → Alison (legítimo)
```
From: Jean User <jean@m57.biz>
To: alison@m57.biz
Subject: RE: background checks
Content: "Sure thing."
```

#### Email de Confusión: Alison → Jean
```
From: alison@m57.biz <alison@m57.biz>
To: Jean User
Subject: RE: background checks
Content: "What's a 'sure thing.'?"
```
**Indicador clave**: Alison está genuinamente confundida, demostrando que NO envió el email original.

#### Email #2: "Please send me the information now" (Exfiltración)
```
From: alison@m57.biz <alison@m57.biz>
To: jean@m57.biz
Date: July 19/20, 2008
Subject: Please send me the information now
Return-Path: simsong@xy.dreamhostps.com  [SPOOFED]
Reply-To: tuckergorge@gmail.com  [MALICIOSO - CAMBIADO]
```
**Anomalías críticas:**
- Mismo Return-Path spoofeado: `simsong@xy.dreamhostps.com`
- **Reply-To ahora apunta a `tuckergorge@gmail.com`** - esta es la clave del ataque
- El atacante redirige las respuestas de Jean a una cuenta externa de Gmail

#### Email de Exfiltración: Jean → Atacante
```
From: Jean User <jean@m57.biz>
To: tuckergorge@gmail.com (vía Reply-To spoofeado)
Attachment: M57biz.xls
Date: July 20, 2008 ~12:28 PM
```
**Contenido del archivo adjunto:**
- Hoja de cálculo Excel con: Nombre, Posición, Salario, SSN de todos los empleados

| Name | Position | Salary | SSN |
|------|----------|--------|-----|
| Alison Smith | President | $140,000 | 103-44-3134 |
| Jean Jones | CFO | $120,000 | 432-34-6432 |
| Bob Brackman | Apps | $90,000 | 94-332-9345 |
| Carlefred Daubert | I Q&A | $110,000 | 34-550-1020 |
| Emmy Arlington | - | $67,000 | 404-98-4079 |
| Gina Tangers | Creative | $80,000 | 980-97-3311 |
| Harris Jenkins | G&C | $105,000 | 887-33-5532 |
| Indy Counterching | Outreach | $240,000 | 123-45-6789 |
| **Total** | | **$1,009,000** | |

#### Email #3: "Thanks!" (Confirmación del Atacante)
```
From: alison@m57.biz <alison@m57.biz>
To: jean@m57.biz
Subject: Thanks!
Return-Path: simsong@xy.dreamhostps.com
Reply-To: tuckergorge@gmail.com
```

### 2. NETWORK / WEB ARTIFACTS

#### Actividad Web Encontrada
- **Acceso a Gmail personal** - potencial comunicación no autorizada
- **Visita a sitios de empleo/job portals** - posible intención de dejar la empresa
- **Descarga de herramientas de compresión** (7zip, tar.gz) - posible empaquetado de archivos para exfiltración
- **Google Alert emails** en la bandeja de entrada - posible seguimiento de competidores

#### Artefactos de Navegador Sospechosos
- **Archivos HTML cached en Internet Explorer** con prompts falsos de Microsoft UI:
  - `rcstatus.htm`
  - `InstallStatus[1].htm`
- **Indicadores de session hijacking** basado en navegador
- **Scripts de JavaScript de vigilancia** incluyendo funciones como `syncUserData()`, tracking cookies, UID tokens
- **Artefactos de Remote Assistance** ocultos en directorios de Windows Help

### 3. FILE SYSTEM

#### Archivo Principal: m57biz.xls
| Atributo | Valor |
|----------|-------|
| **Ubicación** | Desktop de Jean (C:/Documents and Settings/Jean/Desktop/) |
| **Nombre** | m57biz.xls |
| **Fecha de creación** | 07/20/2008 1:28:03 AM (GMT) / July 19, 2008 9:28 PM (PDT) |
| **Fecha de modificación** | 07/20/2008 1:28:03 AM |
| **Encriptado** | No |
| **Comprimido** | No |
| **Archivo real** | Sí |
| **Sector inicial** | 5,160,295 |

#### Otros Archivos Encontrados
- **M57-PatentStrategy.docx** - Documento confidencial de estrategia de patentes
- **PDFs borrados** con términos sensibles
- **Carpetas sospechosas** en `/home/jean/.mozilla/`
- **Archivos readme.txt** con referencias BMP - identificados como red herrings (falsas pistas)
  - `toolbart.bmp`, `toolbarb.bmp` - assets de UI de toolbar installations

### 4. USB / DISPOSITIVOS

#### Indicadores de Dispositivos USB
- **Metadatos de USB Kingston** encontrados en el sistema - potencial método de exfiltración alternativo
- No se confirmó uso de USB para este archivo específico, pero los artefactos sugieren que Jean utilizaba dispositivos USB

### 5. AUTH / LOGS / SYSTEM ARTIFACTS

#### Artefactos de Sistema Windows XP
- **Archivo Outlook PST** ubicado en: `C:/Documents and Settings/Jean/Local Settings/Application Data/Microsoft/Outlook/Outlook.pst`
- **Prefetch files** - potencialmente eliminados (indicador de anti-forense)

#### Artefactos de Anti-Forense Detectados
- **Binarios del sistema eliminados**: `ipconfig.exe`, `net.exe`, y otros
  - Posiblemente eliminados con herramienta anti-forense o script
  - Indica intento de ocultar actividad de red
- **Instalación de AIM6 con toolbar bundles sospechosos**
  - Ejecutables tipo telemetry embebidos
  - Payloads post-instalación
- **Tiempos de modificación/borrado inconsistentes** - posible técnica anti-forense

---

## Análisis Técnico Detallado

### Análisis de Headers de Email

El análisis de headers reveló el mecanismo del ataque:

```
Return-Path: simsong@xy.dreamhostps.com
From: alison@m57.biz
Reply-To: [VARIABLE]
```

**Mecanismo del spoofing:**
1. El atacante envía emails desde `simsong@xy.dreamhostps.com`
2. El campo "From" se configura para mostrar `alison@m57.biz`
3. Jean ve el email como proveniente de Alison en su cliente de email
4. El Reply-To se manipula para redirigir respuestas

### Cadena de Ataque Reconstruida

```
[Attacker: simsong@xy.dreamhostps.com]
    |
    v
[Spoofs alison@m57.biz identity]
    |
    v
[Sends "background checks" email to jean@m57.biz]
    |--> Reply-To: alison@m57.biz (legit)
    |
    v
[Jean replies "Sure thing" → goes to real Alison]
    |
    v
[Alison confused: "What's a sure thing?"]
    |
    v
[Attacker sends 2nd email]
    |--> Reply-To: tuckergorge@gmail.com (ATTACKER)
    |
    v
[Jean creates m57biz.xls]
    |
    v
[Jean replies with attachment → goes to ATTACKER]
    |
    v
[Attacker: "Thanks!"]
    |
    v
[Data posted to competitor's website]
```

---

## Anomalías Detectadas (Resumen Completo)

### Anomalías de Email
1. **Return-Path spoofeado**: Los emails mostraban `alison@m57.biz` como remitente pero el Return-Path real era `simsong@xy.dreamhostps.com`
2. **Reply-To manipulado**: Cambio de Reply-To legítimo a `tuckergorge@gmail.com` en el segundo email
3. **Nota sospechosa**: "No incluyas el texto de este email en tu respuesta" - intento de destruir evidencia
4. **Dominio del atacante**: `xy.dreamhostps.com` - hosting compartido potencialmente comprometido

### Anomalías de Comportamiento
5. **Solicitud inusual**: Pedir SSN y salarios por email va contra cualquier política de seguridad
6. **Inconsistencia en testimonios**: Alison genuinamente confundida vs. Jean convencida de haber seguido órdenes
7. **Timing sospechoso**: Toda la comunicación ocurrió en un período de ~6 horas

### Anomalías de Sistema
8. **Archivos de sistema eliminados**: `ipconfig.exe`, `net.exe` - signo de anti-forense
9. **Instalación de AIM6/toolbars**: Software potencialmente malicioso instalado
10. **HTML payloads cached**: Archivos como `rcstatus.htm` con prompts falsos de Microsoft
11. **Artefactos de Remote Assistance**: Posible acceso remoto no autorizado
12. **Tiempos inconsistentes**: Mismatched modify/delete times

### Anomalías del Documento
13. **Documento no encriptado**: Hoja con SSNs sin protección
14. **Ubicación en Desktop**: Archivo altamente sensible en ubicación visible
15. **Metadatos de autor**: Algunos reportes indican "Alison" como autor del archivo (inconsistente)

---

## Técnicas MITRE ATT&CK Aplicables

| Técnica ID | Técnica | Descripción en el Caso |
|------------|---------|----------------------|
| **T1566.002** | Phishing: Spearphishing Attachment | Emails spoofeados dirigidos específicamente a Jean como CFO |
| **T1566.001** | Phishing: Spearphishing Link | Posible phishing vía navegador (html cached, AIM toolbars) |
| **T1589.002** | Gather Victim Host Information | El atacante sabía que Jean era la CFO y tenía acceso a datos financieros |
| **T1589.003** | Gather Victim Identity Information | Conocimiento de la relación jerárquica Alison→Jean |
| **T1585.001** | Establish Accounts: Email Accounts | Uso de cuenta tuckergorge@gmail.com |
| **T1585.002** | Establish Accounts: Social Media Accounts | Posible uso de múltiples identidades |
| **T1078** | Valid Accounts | Compromiso/aprovechamiento de cuenta de email legítima |
| **T1567.001** | Exfiltration Over Web Service | Exfiltración vía email a Gmail (servicio web) |
| **T1567.002** | Exfiltration Over Web Service: Exfiltration to Cloud Storage | Datos enviados a cuenta Gmail del atacante |
| **T1070** | Indicator Removal on Host | Eliminación de binarios de sistema (ipconfig.exe, net.exe) |
| **T1070.004** | File Deletion | Borrado de archivos de sistema |
| **T1070.005** | Network Share Connection Removal | Posible limpieza de conexiones |
| **T1565.001** | Data Manipulation: Stored Data Manipulation | Modificación de Reply-To en headers |
| **T1083** | File and Directory Discovery | El atacante sabía qué archivo buscar |
| **T1114** | Email Collection | Recolección de información vía manipulación de email |
| **T1560** | Archive Collected Data | Posible uso de herramientas de compresión (7zip) |
| **T1204.002** | User Execution: Malicious File | Ejecución de instaladores AIM6/toolbar potencialmente maliciosos |

---

## Conclusión del Caso

### Determinación Forense

**Jean NO actuó maliciosamente. Fue víctima de un ataque de spear-phishing con spoofing de email.**

### Evidencia que Soporta la Conclusión

1. **El email de Alison fue spoofeado**: El Return-Path `simsong@xy.dreamhostps.com` demuestra que los emails NO provenían del servidor de correo legítimo de M57.biz
2. **El Reply-To fue manipulado**: El cambio de `alison@m57.biz` a `tuckergorge@gmail.com` entre el primer y segundo email es la firma del ataque
3. **La confusión de Alison es genuina**: Su respuesta "What's a sure thing?" demuestra que no tenía conocimiento de la solicitud
4. **Jean actuó de buena fe**: Creyó estar siguiendo órdenes legítimas de su superior
5. **No hay evidencia de que Jean publicara los datos**: El archivo fue enviado a `tuckergorge@gmail.com`, no a un foro web
6. **Binarios de sistema eliminados**: Indican que el sistema de Jean fue comprometido, no que ella fuera la atacante

### Recomendaciones
1. **Training de concienciación de seguridad** para todo el personal
2. **Implementar SPF, DKIM, DMARC** en el servidor de correo
3. **Política de verificación** para solicitudes sensibles (confirmación telefónica)
4. **Cifrado de datos sensibles** (SSN, salarios)
5. **Restricción de acceso** a información confidencial

---

# OTROS ESCENARIOS DE DIGITAL CORPORA

---

## Escenario: 2008 Nitroba University Harassment
**URL**: https://digitalcorpora.org/corpora/scenarios/nitroba-university-harassment-scenario/

### Narrativa
Eres un administrador de seguridad en la ficticia Nitroba State University. La profesora de Química Lily Tuckrige ha estado recibiendo emails de acoso y sospecha que provienen de un estudiante en su clase Chemistry 109.

### Evidencia Disponible
- **Archivo PCAP**: ~60MB de tráfico de red capturado
- **Slides**: Presentación del problema (PDF, PPT, Keynote)
- **Roster**: Lista de estudiantes de Chem 109
- **Screenshots**: Capturas de pantalla de los emails de Yahoo Mail

### Detalles Técnicos
- **IP origen inicial**: 140.247.62.34 (dormitorio estudiantil)
- **Setup**: Tres mujeres comparten el dormitorio (Alice, Barbara, Candice)
- **Red**: Ethernet provisto por la universidad + Wi-Fi router sin password instalado por un amigo
- **Servicio de destrucción**: willselfdestruct.com (el perpetrador envió un email a través de este servicio)

### Timeline de Eventos
| Fecha | Evento |
|-------|--------|
| Julio 13 | Primer email de acoso recibido desde badguy@hotmail.com |
| Julio 21 | Segundo email enviado vía willselfdestruct.com con mensaje: "you can't find us and you can't hide from us. Stop teaching. Start running." |

### Hallazgos del Análisis
- **IP pública**: 140.247.62.34 → Resuelve a habitación G24 del dormitorio
- **IP interna NAT**: 192.168.15.4
- **MAC address**: 00:17:f2:e2:c0:ce (dispositivo Apple)
- **User Agent**: Internet Explorer 6 en Windows XP SP2
- **Email del sospechoso**: jcoach@gmail.com → **Johnny Coach** (estudiante de Chem 109)
- **Metodología**: Los emails se enviaron vía Gmail webmail, con cookies enviadas en plaintext sobre HTTP

### Conclusión
**Johnny Coach**, estudiante de Chemistry 109, fue identificado como el perpetrador del acoso por correo electrónico. La evidencia se obtuvo del análisis de paquetes PCAP mostrando sesiones de Gmail webmail desde la IP interna 192.168.15.4, con cookies en plaintext que revelaban la cuenta jcoach@gmail.com.

### MITRE ATT&CK
- T1566.001: Phishing
- T1585.001: Establish Accounts: Email Accounts
- T1071.001: Application Layer Protocol: Web Protocols

---

## Escenario: 2009 M57-Patents
**URL**: https://digitalcorpora.org/corpora/scenarios/m57-patents-scenario/

### Narrativa
Este escenario rastrea las **primeras cuatro semanas** de la historia corporativa de M57 Patents. La empresa comenzó operaciones el viernes 13 de noviembre de 2009 y cesó operaciones el sábado 12 de diciembre de 2009.

### Datos Disponibles
- **Disk forensics exercise**: Imágenes de disco de todos los sistemas al último día
- **Network forensics exercise**: Todos los paquetes de red entrantes y salientes
- **Imágenes diarias**: Cada computadora fue imageada todos los días (para investigación)
- **Memory dumps**: Volcados de memoria diarios

### Sub-escenarios
El escenario incluye tres ejercicios separados:

#### 1. M57-Patents-Illegal
Actividades ilegales dentro de la empresa de búsqueda de patentes.

#### 2. M57-Patents-Exfiltration
Exfiltración de información confidencial de patentes.

#### 3. M57-Patents-Eavesdropping
Escucha/ interceptación de comunicaciones corporativas.

### Materiales Disponibles
- Instructor packet (encriptado)
- Hash sets
- Scenario emails
- Detective reports (1-4)
- Affidavit and warrant
- Redacted drive images
- USB drive images

### Periodo del Escenario
**13 de noviembre - 12 de diciembre de 2009**

---

## Escenario: 2012 National Gallery DC Attack
**URL**: https://digitalcorpora.org/corpora/scenarios/national-gallery-dc-2012-attack/

### Narrativa
Escenario que abarca aproximadamente **10 días** con dos historias entrelazadas:

### Trama 1: Defacing de Arte Extranjero
- **Alex**: Hombre de negocios con lazos krasnovianos. Quiere avergonzar a EE.UU. dañando arte extranjero de Majavia exhibido en la National Gallery.
- **Carry**: Partidaria krasnoviana en EE.UU. Contactada por Alex para organizar el ataque. Técnicamente competente, usa esteganografía y encriptación.
- **Tracy**: Supervisora de la National Gallery, conocida de Carry. Contactada bajo la fachada de organizar un "flash mob" en la galería.

### Trama 2: Robo de Sellos
- **Tracy**: En problemas financieros (custodia de hija, escuela privada). Conspira con su hermano **Pat** (policía) para robar sellos valiosos de la galería.
- **Pat**: Detective del D.C. Enforcers Bureau. Coordina con **King** (criminal) para el robo.
- **Joe**: Ex-esposo de Tracy. Instaló un keylogger en la MacBook Air familiar para espiar. Descubre la conspiración y denuncia a Tracy.

### Personajes
| Personaje | Rol | Email/Teléfono |
|-----------|-----|----------------|
| Tracy | Acusada (supervisora galería) | tracysumtwelve@gmail.com, tracy.sumtwelve@nationalgallerydc.org, (703) 340-9961 |
| Pat | Hermano de Tracy (policía) | perrypatsum@yahoo.com, patsumtwelve@gmail.com, (571) 308-3236 |
| Terry | Hija de Tracy y Joe | (703) 829-6071 |
| Joe | Ex-esposo de Tracy (descubrió conspiración) | - |
| Alex | Krasnovian (organizador del ataque) | - |
| Carry | Co-conspiradora (conexión con Alex) | (202) 725-2124 |
| King | Criminal contactado por Pat | throne1966@hotmail.com |

### Evidencia Disponible
#### Dispositivos Almacenados
- Carry's phone (2012-07-15) - FTK Logical Dump
- Carry's tablet (2012-07-16) - E01 + TAR
- Tracy's phone (2012-07-15) - L01 + E01
- Tracy's external hard drive - E01
- Tracy's home computer - E01 + E02
- Email spyware de MacBook Air (keylogger de Joe)

#### Capturas de Red
- Exterior network dumps: 2012-07-06, 07-09, 07-10, 07-12
- Interior network dumps: 2012-07-06, 07-09, 07-10, 07-12
- Capturas con SSLstrip (tráfico con y sin encriptación SSL)

### Timeline de Eventos
| Fecha | Evento |
|-------|--------|
| Jun 19, 2012 | Pat envía email a Tracy con MP3 (instrucciones para instalar VirtualBox) |
| Jul 5, 2012 | Tracy y Carry acuerdan reunión en Bubba's Grill vía SMS |
| Jul 6, 2012 | Pat organiza "proposición" con King (throne1966@hotmail.com) |
| Jul 7, 2012 | Tracy recibe Target Gift Card de $1000 (posible pago de Alex) |
| Jul 9, 2012 | Tracy se envía email a sí misma describiendo sellos a robar |
| Jul 10, 2012 | Pat reenvía lista a Tracy |
| Jul 11, 2012 | Tracy y Carry acuerdan entrega de tablet vía SMS |
| Jul 12, 2012 | Tracy pregunta a Carry sobre el flash mob |

### Artefactos Digitales
- Archivos esteganográficos
- Archivos encriptados
- Comunicaciones SMS
- Emails entre aliases (coralbluetwo@hotmail.com, patsumtwelve@gmail.com)
- Datos de localización WiFi/GPS del iPhone
- Email keylogger logs enviados periódicamente a Joe

### MITRE ATT&CK
- T1566: Phishing
- T1020: Automated Exfiltration
- T1027: Obfuscated Files or Information (esteganografía)
- T1052: Input Capture (keylogger)
- T1589: Gather Victim Identity Information
- T1593: Search Open Websites/Domains

---

## Escenario: 2018 Lone Wolf
**URL**: https://digitalcorpora.org/corpora/scenarios/2018-lone-wolf-scenario/

### Narrativa
Escenario de materiales de una **ficticia incautación del laptop de un individuo que planeaba un mass shooting**. El hermano del individuo alertó a la policía sobre el comportamiento cada vez más preocupante de su hermano.

### Evidencia Disponible
| Archivo | Tamaño | Descripción |
|---------|--------|-------------|
| FTK Imager Log.txt | - | Log del proceso de imagen |
| LoneWolf.E01-E09 | ~1.5GB cada uno | Imagen de disco (EnCase) |
| memdump.mem | 17GB | Volcado de memoria RAM |
| pagefile.sys | 2.9GB | Archivo de paginación |

### Características
- Escenario creado por Thomas Moore (George Mason University) para curso CFRS 780: Cloud Forensics
- **Enfoque**: Cloud artifacts dejados en clientes
- Incluye reportes de múltiples herramientas forenses comerciales

### MITRE ATT&CK Aplicables
- T1491.001: Defacement: Internal Defacement
- T1589: Gather Victim Identity Information
- T1614: Location Tracking

---

## Escenario: 2019 Narcos
**URL**: https://digitalcorpora.org/corpora/scenarios/2019-narcos/

### Narrativa (Versión Compleja)
Dos pasajeros fueron interceptados por Aduanas al llegar a Wellington, Nueva Zelanda desde Brisbane:
- **Jane Esteban** y **John Fredricksen**: Sospechosos de actividad ilegal
- En la maleta de Fredricksen se encontró **1 kg de metanfetamina**

### Interrogatorios
- **John Fredricksen**: Se negó a responder preguntas
- **Jane Esteban**: Reveló que debía entregar la maleta a:
  - Primera opción: Eastbourne Library
  - Plan B: 666 Rewera Avenue, Petone

### Redada
- Aduanas y policía allanaron 666 Rewera Avenue
- No había nadie presente
- Se encontraron: **drogas, armas de fuego y una computadora de escritorio**

### Tu Misión
Como investigador forense de Aduanas, analizar:
- Imagen forense y volcado de memoria de la computadora de escritorio (versión simplificada)
- Imágenes de los 2 laptops y 1 desktop + memoria (versión compleja)

### Determinar
1. Relación entre John Fredricksen y el sospechoso
2. Intenciones futuras
3. Cualquier otra evidencia de apoyo

### Evidencia Disponible
- Imágenes de 2 laptops (Windows 10) + 1 desktop
- Memory dumps
- Los 3 dispositivos tienen diferentes builds de Windows 10
- Los artefactos pueden estar en diferentes ubicaciones o no estar presentes en todos los dispositivos

---

## Escenario: 2019 Owl
**URL**: https://digitalcorpora.org/corpora/scenarios/2019-owl/

### Narrativa
En una jurisdicción donde el **comercio de búhos es ilegal**, dos usuarios están discutiendo el comercio ilegal de búhos.

- La computadora y dispositivo móvil incautados pertenecen a un usuario que intenta **comprar búhos ilegalmente**
- El usuario contactó a otro usuario que puede proporcionar un búho a cambio de dinero en efectivo
- Se acordó un búho específico y se programó un intercambio
- Después del intercambio, se envió un mensaje de confirmación

### Evidencia Disponible
- Directorio de evidencia de nivel superior
- Imágenes de computadora y dispositivo móvil

---

## Escenario: 2019 Tuck
**URL**: https://digitalcorpora.org/corpora/scenarios/2019-tuck/

### Narrativa
**Nota**: Este escenario está pendiente de ser documentado por completo.

Un escenario que involucra a una persona que intenta unirse a una **organización terrorista**.

### Evidencia Disponible
- Directorio de descargas: https://downloads.digitalcorpora.org/corpora/scenarios/2019-tuck/

---

## RESUMEN COMPARATIVO DE ESCENARIOS

| Escenario | Año | Tipo | Dispositivos | Red | Móvil | Complejidad |
|-----------|-----|------|-------------|-----|-------|-------------|
| M57-Jean | 2008 | Disk Forensics | 1 laptop | No | No | Baja |
| Nitroba | 2008 | Network Forensics | - | PCAP | No | Media |
| M57-Patents | 2009 | Disk+Network | Múltiples | PCAP | No | Alta |
| National Gallery DC | 2012 | Multi-device | PCs, phones, tablets | PCAP (SSLstrip) | Sí | Muy Alta |
| Lone Wolf | 2018 | Disk+Memory | 1 laptop | No | No | Media |
| Narcos | 2019 | Disk+Memory | 2 laptops + 1 desktop | No | No | Media |
| Owl | 2019 | Disk+Mobile | PC + móvil | No | Sí | Baja |
| Tuck | 2019 | Disk | Desconocido | No | No | Media |

---

## ARCHIVOS GENERADOS

| Archivo | Ruta |
|---------|------|
| Reporte completo | /mnt/agents/output/digital_corpora_complete_report.md |
| PDF del ejercicio M57-Jean | /mnt/agents/output/M57-Jean.pdf |

---

*Reporte generado a partir del análisis de digitalcorpora.org y fuentes de investigación forense digital*
*Fecha: Abril 2025*
