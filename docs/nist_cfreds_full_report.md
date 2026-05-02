# NIST CFReDS (Computer Forensic Reference Data Sets) - Reporte Forense Completo

**Fecha de generacion**: 2025
**Fuente**: https://cfreds.nist.gov/ y https://cfreds-archive.nist.gov/
**Total de datasets identificados**: 17 datasets principales de NIST + datasets de contribuyentes externos

---

## RESUMEN EJECUTIVO

El portal CFReDS (Computer Forensic Reference Data Sets) del NIST es el repositorio mas completo de datasets forenses documentados para pruebas de herramientas, entrenamiento de investigadores, y evaluacion de competencia. Contiene aproximadamente 160 entradas de datasets de multiples contribuyentes, con 17 datasets principales desarrollados por NIST.

Los datasets cubren areas como:
- Analisis de escenarios completos (Hacking Case, Data Leakage Case)
- Analisis de componentes especificos (Registry, Memory, File Carving)
- Sistemas operativos (Windows XP-10, Mac OS, Linux)
- Dispositivos moviles (Android, iOS, Samsung)
- Dispositivos IoT y drones
- Redes y trafico de red
- Contenedores y sistemas de archivos

---

## Fuente: NIST CFReDS - Hacking Case (El caso mas famoso)

**URL**: https://cfreds.nist.gov/all/NIST/HackingCase
**URL Archivo**: https://cfreds-archive.nist.gov/Hacking_Case.html
**Autor**: NIST
**Fecha**: 2004 (caso), 2020 (publicado en portal)
**Descargas**: 61,112+
**Tags**: Data Forensic Related, Simulated Cases Scenarios

### Descripcion del caso

On 09/20/04, a Dell CPi notebook computer, serial # VLQLW, was found abandoned along with a wireless PCMCIA card and an external homemade 802.11b antennae. It is suspected that this computer was used for hacking purposes, and can be tied to a hacking suspect, Greg Schardt (fictional). Schardt also goes by the online nickname of "Mr. Evil" and some of his associates have said that he would park his vehicle within range of Wireless Access Points (like Starbucks and other T-Mobile Hotspots) where he would then intercept internet traffic, attempting to get credit card numbers, usernames & passwords.

**Objetivo**: Find any hacking software, evidence of their use, and any data that might have been generated. Attempt to tie the computer to the suspect, Greg Schardt.

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| SCHARDT.001 - SCHARDT.008 | DD Image (split) | Imagen DD dividida en 8 partes del disco del Dell Latitude CPi |
| Dell Latitude CPi.E01 | EnCase Image | Imagen EnCase del mismo disco |
| Dell Latitude CPi.E02 | EnCase Image | Continuacion de la imagen EnCase |
| SCHARDT.LOG | Log file | Log de adquisicion |
| Google Drive link | Answer Key | Enlace a clave de respuestas y guia del investigador |

### Sistema objetivo
- **Dispositivo**: Dell Latitude CPi notebook
- **Sistema Operativo**: Windows XP Professional
- **Serial**: VLQLW
- **IP asignada**: 192.168.1.111 (Look@LAN config)
- **MAC Address**: 00:10:a4:93:3e:09 (Xircom CardBus Ethernet 100 + Modem 56)
- **WiFi**: Compaq WL110 Wireless LAN PC Card

### Investigator Guide disponible: SI
La guia del investigador incluye 31 preguntas forenses especificas que deben responderse:

1. What is the image hash? Does the acquisition and verification hash match?
2. What operating system was used on the computer?
3. When was the install date?
4. What is the timezone settings?
5. Who is the registered owner?
6. What is the computer account name?
7. What is the primary domain name?
8. When was the last recorded computer shutdown date/time?
9. How many accounts are recorded (total number)?
10. What is the account name of the user who mostly uses the computer?
11. Who was the last user to logon to the computer?
12. Search for "Greg Schardt" - what file proves he is Mr. Evil and administrator?
13. List the network cards used by this computer
14. What is the IP address and MAC address?
15. Which NIC card was used during installation of LOOK@LAN?
16. Find 6 installed programs that may be used for hacking
17. What is the SMTP email address for Mr. Evil?
18. What are the NNTP settings for Mr. Evil?
19. What two installed programs show email information?
20. List 5 newsgroups that Mr. Evil subscribed to
21. What are the user settings in MIRC (IRC program)?
22. List 3 IRC channels that the user accessed
23. What is the name of the file with intercepted data (Ethereal)?
24. What type of wireless computer was the victim using?
25. What websites was the victim accessing?
26. Search for the main user's web based email address
27. Yahoo mail saves copies under what file name?
28. How many executable files are in the recycle bin?
29. Are these files really deleted?
30. How many files are actually reported to be deleted?
31. Are there any viruses on the computer?

### Answer Key disponible: SI
- Hash MD5: `aee4fcd9301c03b3b054623ca261959a`
- OS: Windows XP Professional
- Install Date: Thursday, August 19, 2004 22:48:27 GMT
- Timezone: Central Standard Time (CST) / Central Daylight Time
- Registered Owner: Greg Schardt
- Computer Name: N-1A9ODN6ZXK4LQ
- Primary User: Mr. Evil (15 logins)
- Email: mrevilrulez@yahoo.com
- SMTP: whoknowsme@sbcglobal.net
- IRC: User "Mini Me", Nick "Mr", Alt "mrevilrulez"

### Técnicas MITRE ATT&CK aplicables
- T1040 - Network Sniffing (Ethereal packet capture)
- T1110 - Brute Force (Cain & Abel password cracker)
- T1552 - Unsecured Credentials (123WASP password finder)
- T1098 - Account Manipulation
- T1567 - Exfiltration Over Web Service (Yahoo Mail)
- T1071 - Application Layer Protocol (IRC channels)
- T1018 - Remote Access Software (Look@LAN)
- T1083 - File and Directory Discovery

### Artefactos textuales especificos

**Archivos de configuracion encontrados**:
- `C:\Program Files\Look@LAN\irunin.ini` - Contiene `REGOWNER=Greg Schardt`, `LANUSER=Mr. Evil`, `ISUSERNTADMIN=true`, IP=192.168.1.111, MAC=00:10:a4:93:3e:09
- `C:\Program Files\mIRC\mirc.ini` - User=Mini Me, email=none@of.ya, nick=Mr, anick=mrevilrulez
- `C:\Documents and Settings\Mr. Evil\interception` - Archivo pcap con trafico interceptado (victima usando Windows CE Pocket PC accediendo mobile.msn.com y MSN Hotmail)
- `C:\Documents and Settings\Mr. Evil\Application Data\Ethereal\recent` - Referencia a archivo de captura

**Canales IRC accedidos (logs encontrados)**:
- #Chataholics.UnderNet
- #CyberCafe.UnderNet
- #Elite.Hackers.UnderNet
- #evilfork.EFnet
- #ISO-WAREZ.EFnet
- #thedarktower.AfterNET

**Software de hacking instalado**:
1. Cain & Abel v2.5 beta45 - Password recovery/sniffer
2. Ethereal - Packet sniffer
3. 123 Write All Stored Passwords (123WASP)
4. Anonymizer - Proxy/hide IP tracks
5. NetStumbler - Wireless access point discovery
6. Look@LAN - Network monitoring/discovery
7. CuteFTP - FTP client

**Websites visitados por la victima** (del pcap):
- login.passport.com
- login.passport.net
- mobile.msn.com
- www.passportimages.com
- MSN Hotmail

**Archivos en Recycle Bin**:
- Dc1.exe (lalsetup250.exe - Look@LAN installer)
- Dc2.exe (netstumblerinstaller_0_4_0.exe)
- Dc3.exe (WinPcap_3_01_a.exe)
- Dc4.exe (ethereal-setup-0.10.6.exe)

### Artefactos de registro de Windows

**Claves relevantes**:
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\RegisteredOwner` = "Greg Schardt"
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\InstallDate` = 0x41252e3b (Aug 19, 2004)
- `HKLM\SYSTEM\ControlSet001\Control\TimeZoneInformation\StandardName` = "Central Standard Time"
- `HKLM\SYSTEM\ControlSet001\Control\ComputerName\ComputerName` = "N-1A9ODN6ZXK4LQ"
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\DefaultUserName` = "Mr. Evil"
- `HKLM\SAM\Users\Names` - 5 cuentas: Administrator, Guest, HelpAssistant, Mr. Evil, SUPPORT_388945a0
- `HKU\informant\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU` - Ejecuciones recientes
- `HKU\informant\Software\Microsoft\Internet Explorer\TypedURLs` - URLs visitadas

### Conclusion forense
El caso demuestra un atacante (Greg Schardt / "Mr. Evil") que utiliza un notebook Dell para realizar actividades de hacking wireless, incluyendo sniffing de paquetes con Ethereal, cracking de passwords con Cain & Abel, y monitoreo de red con Look@LAN y NetStumbler. Los artefactos muestran comunicacion via IRC, email (Yahoo Mail), y newsgroups relacionados con hacking. Se encontraron herramientas de hacking y evidencia de intercepcion de trafico wireless de victimas.

---

## Fuente: NIST CFReDS - Data Leakage Case

**URL**: https://cfreds.nist.gov/all/NIST/DataLeakageCase
**URL Archivo**: https://cfreds-archive.nist.gov/data_leakage_case/data-leakage-case.html
**Autor**: NIST
**Fecha**: 2015 (caso), 2020 (publicado)
**Descargas**: 24,191+
**Tags**: Mac, Mac OS Version, Mac Artifacts, Mac Plists, Snow Leopard

### Descripcion del caso

**Personaje**: "Iaman Informant" (nombre ficticio: informant / jaman.informant@nist.gov)

El Sr. Informant trabajaba como gerente de la division de desarrollo de tecnologia en una famosa compania internacional "OOO" que desarrollaba tecnologias y gadgets de ultima generacion.

Un dia, en un lugar que visito por negocios, recibio una oferta de "Spy Conspirator" (spy.conspirator@nist.gov) para filtrar informacion confidencial relacionada con la tecnologia mas nueva. El Sr. Conspirator era empleado de una empresa rival, y el Sr. Informant decidio aceptar la oferta por grandes cantidades de dinero.

El Sr. Informant hizo un esfuerzo deliberado por ocultar el plan de filtracion:
- Discutio con el Sr. Conspirator usando un servicio de correo electronico como si fuera una relacion comercial
- Envio muestras de informacion confidencial a traves de almacenamiento en la nube personal (Google Drive)
- El conspirador pidio la entrega directa de dispositivos de almacenamiento con los datos restantes
- Fue detectado en el punto de control de seguridad con un USB memory stick y un CD-R

**Politicas de seguridad de la compania**:
1. Archivos confidenciales deben almacenarse en dispositivos externos autorizados y unidades de red seguras
2. Solo accesibles entre 10:00 AM y 16:00 PM con permisos apropiados
3. Dispositivos electronicos no autorizados no pueden ingresar
4. Todos los empleados deben pasar por el Security Checkpoint
5. Todos los dispositivos de almacenamiento estan prohibidos bajo las reglas del Security Checkpoint

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| cfreds_2015_data_leakage_pc.7z.001-003 | 7z split | Imagen del PC de la oficina (3 partes) |
| cfreds_2015_data_leakage_rm#2.7z | 7z | Imagen USB "RM#2" |
| cfreds_2015_data_leakage_rm#2.E01 | EnCase | Imagen EnCase del USB |
| (archivos adicionales) | - | Imagen CD-R "RM#3", Answer Key |

### Investigator Guide disponible: SI
Incluye **60 preguntas forenses** detalladas organizadas en categorias:

**Categoria A: Informacion del Sistema (Preguntas 1-12)**
1. Hash values (MD5 & SHA-1) de todas las imagenes
2. Informacion de particiones del PC
3. Informacion detallada del OS (nombre, fecha instalacion, owner)
4. Timezone setting
5. Computer name
6. List all accounts (except system accounts)
7. Last user to logon
8. Last recorded shutdown date/time
9. Network interface info (DHCP)
10. Applications installed after OS
11. Application execution logs
12. System on/off and user logon/logoff traces (09:00-18:00)

**Categoria B: Navegacion Web (Preguntas 13-17)**
13. Web browsers used
14. Browser history file paths
15. Websites accessed (timestamp, URL)
16. Search keywords (timestamp, URL, keyword)
17. Windows Explorer search keywords

**Categoria C: Email (Preguntas 18-21)**
18. Email application used
19. Email file location
20. Email account
21. All emails incluyendo deleted items

**Categoria D: Dispositivos de Almacenamiento (Preguntas 22-27)**
22. External storage devices attached to PC
23. File renaming traces in Windows Desktop (2015-03-23 to 2015-03-24)
24. IP address of company's shared network drive
25. Directories traversed in RM#2
26. Files opened from network drive
27. Directories traversed in company's network drive

**Categoria E: Cloud Services (Preguntas 28-30)**
28. Cloud service traces
29. Files deleted from Google Drive
30. Cloud storage file paths

**Categoria F: Anti-forensics (Preguntas 31-57)**
31-52. Actividades anti-forenses en cada dispositivo
53. Recover deleted files from USB RM#2
54. Anti-forensics actions on RM#2
55. Files copied from PC to RM#2
56. Recover hidden files from CD-R RM#3
57. Anti-forensics actions on CD-R RM#3

**Categoria G: Timeline y Conclusiones (Preguntas 58-60)**
58. Detailed timeline of data leakage processes
59. Methodologies of data leakage
60. Visual diagram summary

### Answer Key disponible: SI
URL: https://cfreds-archive.nist.gov/data_leakage_case/leakage-answers.pdf

**Respuestas clave**:
- **Timezone**: Eastern Time (US & Canada) (UTC-05:00) + DST
- **Computer Name**: INFORMANT-PC
- **Accounts**: informant (SID 1000, 10 logins), admin11 (SID 1001, 2 logins), ITechTeam (SID 1002, 0 logins), Temporary (SID 1003, 1 login)
- **Last User**: informant
- **Last Shutdown**: 2015-03-25 11:31:05 Eastern Time+DST
- **Network IP**: 10.11.11.129 / DHCP Server: 10.11.11.254
- **Email**: Outlook 2013, archivo OST, cuenta informant
- **Network Drive**: \\\\10.11.11.128\\secured_drive

### Técnicas MITRE ATT&CK aplicables
- T1048 - Exfiltration Over Alternative Protocol (Google Drive)
- T1567 - Exfiltration Over Web Service
- T1030 - Data Transfer Size Limits
- T1071 - Application Layer Protocol (email)
- T1105 - Ingress Tool Transfer
- T1078 - Valid Accounts (compromised insider)
- T1564 - Hide Artifacts (file renaming, CD-R session manipulation)
- T1027 - Obfuscated Files or Information
- T1070 - Indicator Removal on Host
- T1083 - File and Directory Discovery

### Artefactos textuales especificos - Timeline del incidente

**2015-03-23**:
- 16:26 - Recibe email de spy.conspirator@nist.gov: "Okay, I get it. TB be in touch."
- 16:26 - Recibe email: "[Subject: important request] -> conformal But, I need a more data. Do your best."
- 16:26 - Envia email: "Umm...I need time to think."
- Busqueda y descarga apps de cloud storage (Chrome)
- Instala Google Drive y Apple iCloud
- Login a Google Drive con aman.informat.personall@gmail.com
- Conecta a unidad de red segura (\\\\10.11.11.128\\secured_drive)
- Recorre directorios buscando archivos:
  - `[secret_project]_pricing_decision.docx`
  - `[secret_project]_final_meeting.pptx`
- Copia archivos confidenciales a PC (Desktop\\$ data)
- Desconecta unidad de red
- **Renombra archivos**: nombres y extensiones cambiados (.docx -> .mp3, etc.)
- Sube archivos a Google Drive y los comparte
- Envia email a conspirator: "[Subject: It's me] Login is below."
- Borra archivos de Google Drive
- Navegacion web personal usando IE

**2015-03-24**:
- Recibe email: "[Subject: Last request] This is the last request. I want to get the remaining data."
- Envia email: "Stop it! It is very hard to transfer all data over the internet!"
- Recibe: "No problem. U can directly deliver storage devices that stored it."
- Envia: "This is the last time."
- Conecta USB "RM#2"
- Copia archivos confidenciales de PC a USB
- Borra archivos (Shift+Delete durante ~4 horas)
- Crea carta de renuncia
- Recibe email: "Watch out! USB device may be easily detected. So, try another method."
- Envia email: "I am trying."
- Conecta USB "RM#2" nuevamente
- Prueba quemar CD-R con archivos sin sentido (anti-forensics)
- Copia archivos confidenciales de USB a CD-R con renombrado
- Quema archivos confidenciales a CD-R (Windows CD Burning Type 1)
- Verifica archivos en CD-R usando Windows Explorer
- Formatea CD-R como disco vacio (anti-forensics)
- Crea nueva sesion en CD-R copiando archivos sin sentido

**2015-03-25**:
- 10:45 - Logoff
- 10:50 - Logon multiple
- 11:30 - Logoff
- 11:31 - Shutdown

**2015-03-26**:
- Recibe email del conspirator
- Actividades adicionales de preparacion

### Artefactos de email recuperados

**Emails encontrados (OST file parsing)**:

| Timestamp | From | To | Subject | Body |
|-----------|------|----|---------|------|
| 2015-03-23 | spy.conspirator@nist.gov | jaman.informant@nist.gov | (important request) | "conformal But, I need a more data. Do your best." |
| 2015-03-23 | jaman.informant@nist.gov | spy.conspirator@nist.gov | - | "Umm...I need time to think." |
| 2015-03-23 | jaman.informant@nist.gov | spy.conspirator@nist.gov | "It's me" | "Login is below." |
| 2015-03-24 09:26 | spy.conspirator@nist.gov | jaman.informant@nist.gov | "Last request" | "This is the last request. I want to get the remaining data." |
| 2015-03-24 09:30 | jaman.informant@nist.gov | spy.conspirator@nist.gov | RE: Last request | "Stop it! It is very hard to transfer all data over the internet!" |
| 2015-03-24 09:33 | spy.conspirator@nist.gov | jaman.informant@nist.gov | RE: Last request | "No problem. U can directly deliver storage devices that stored it." |
| 2015-03-24 09:34 | jaman.informant@nist.gov | spy.conspirator@nist.gov | RE: Last request | "This is the last time." |
| 2015-03-24 15:33 | spy.conspirator@nist.gov | jaman.informant@nist.gov | "Watch out!" | "USB device may be easily detected. So, try another method." |
| 2015-03-24 15:34 | jaman.informant@nist.gov | spy.conspirator@nist.gov | RE: Watch out! | "I am trying." |
| 2015-03-24 17:05 | jaman.informant@nist.gov | spy.conspirator@nist.gov | "Done" | "It's done. See you tomorrow." |

### Registro de eventos de logon/logoff (Event IDs)

| Timestamp | Event ID | Tipo |
|-----------|----------|------|
| 2015-03-22 11:00:08 | 4624 | Logon |
| 2015-03-22 12:00:08 | 4647 | Logoff |
| 2015-03-22 12:00:09 | 1100 | Shutdown |
| 2015-03-23 13:24:23 | 4608 | Starting up |
| 2015-03-23 14:36:07 | 4624 | Logon |
| 2015-03-23 16:00:22 | 4624 | Logon |
| 2015-03-23 17:02:53 | 4647 | Logoff |
| 2015-03-23 17:02:59 | 1100 | Shutdown |
| 2015-03-24 09:21:29 | 4608 | Starting up |
| 2015-03-24 09:23:40 | 4624 | Logon |
| 2015-03-24 11:14:30 | 4624 | Logon |
| 2015-03-24 17:07:25 | 4647 | Logoff |
| 2015-03-24 17:07:26 | 1100 | Shutdown |
| 2015-03-25 09:05:41 | 4608 | Starting up |
| 2015-03-25 10:45:59 | 4637 | Logoff |
| 2015-03-25 11:30:57 | 4647 | Logoff |
| 2015-03-25 11:31:00 | 1100 | Shutdown |

### Anomalias documentadas
1. **Renombrado de archivos**: El sospechoso renombro archivos cambiando extensiones (.docx a .mp3, .pptx a .jpg) para ocultar el contenido
2. **Uso de cloud storage personal**: Instalo Google Drive y iCloud para exfiltrar datos
3. **Borrado selectivo**: Uso Shift+Delete para eliminacion permanente durante ~4 horas
4. **Manipulacion de CD-R**: Formateo CD-R como disco vacio y creo nueva sesion como tecnica anti-forense
5. **Exfiltracion por multiples canales**: Email, cloud storage, USB, y CD-R
6. **Acceso fuera de horario**: Actividad de exfiltracion fuera del rango permitido (10:00-16:00)

### Conclusion forense
El caso documenta un incidente completo de filtracion de datos por un insider (empleado gerente). El sospechoso utilizo multiples tecnicas de exfiltracion (email, Google Drive, USB, CD-R) y aplico tecnicas anti-forenses basicas (renombrado de archivos, borrado permanente, manipulacion de sesiones CD-R). Los artefactos digitales proporcionan evidencia concluyente de la intencion, los metodos y la secuencia temporal completa del incidente.

---

## Fuente: NIST CFReDS - Rhino Hunt

**URL**: https://cfreds.nist.gov/all/NIST/RhinoHunt
**URL Archivo**: https://cfreds-archive.nist.gov/dfrws/DFRWS2005-RODEO.zip
**Autor**: NIST (DFRWS 2005 Rodeo)
**Fecha**: 2005
**Descargas**: 11,596+
**Tags**: Rhino Hunt

### Descripcion del caso
Look for images (of a rhinoceros) in an image file and network traces.

**Escenario**: Basado en el DFRWS 2005 Rodeo. Se proporciona una imagen USB y trazas de red (network traces) para encontrar imagenes de un rinoceronte.

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| DFRWS2005-RODEO.zip | ZIP | Paquete completo con imagen USB y trazas de red |
| DFRWS2005-answers.pdf | PDF | Clave de respuestas con las ubicaciones de las imagenes |
| rhino.log | Log | Logs de actividad |
| rhino2.log | Log | Logs adicionales |
| rhino3.log | Log | Logs adicionales |
| Rhino Hunt.pdf | PDF | Documento del caso |

### Investigator Guide disponible: SI
Answer Key PDF con la ubicacion de las imagenes encontradas.

### Artefactos textuales especificos
- **Imagenes encontradas**: f0106393.jpg, f0106409.jpg, f0106865.jpg, f0106889.jpg (fotos borradas del USB)
- **Acciones del sospechoso**: download, hiding, deleting files/images
- **Herramienta de recuperacion**: PhotoRec 7.1

### Conclusion forense
Dataset basico para practicar busqueda de imagenes en discos y recuperacion de archivos borrados. Las imagenes del rinoceronte fueron eliminadas del USB pero recuperables.

---

## Fuente: NIST CFReDS - Registry Forensics

**URL**: https://cfreds.nist.gov/all/NIST/RegistryForensics
**URL Archivo**: https://cfreds-archive.nist.gov/winreg/cfreds-2017-winreg/cfreds-2017-winreg.html
**Autor**: NIST
**Fecha**: 2017
**Descargas**: 1,306+
**Tags**: Windows, Databases, Windows 10, Windows 7, Windows 95, Windows Artifacts, Windows OS Versions, Windows Registry, Windows XP

### Descripcion
Data Set for testing MS Windows Registry Extraction Tools.

NIST/CFReDS desarrollo un dataset de referencia del registro de Windows (cfreds-2017-winreg). El dataset comprende:
- **User-generated registry files**: Creados experimentalmente basados en el formato de archivos hive
- **System-generated registry files**: Extraidos de sistemas Windows modernos desde Vista hasta Windows 10
- **Ground truth data**: Datos de verdad de campo para todos los archivos de registro de referencia

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| cfreds-2017-winreg_ugrd-nr.7z | 7z | User-generated registry - non-resident data |
| cfreds-2017-winreg_ugrd-nrd.7z | 7z | User-generated registry - non-resident deleted |
| cfreds-2017-winreg_ugrd-cr.7z | 7z | User-generated registry - cache records |
| cfreds-2017-winreg_ugrd-mr.7z | 7z | User-generated registry - memory records |
| cfreds-2017-winreg_sgrd-vista.7z | 7z | System-generated registry - Windows Vista |
| (archivos adicionales) | 7z | System-generated registry - Windows 7, 8, 8.1, 10 |

### Technical Report
Documento v1.10 disponible (actualizado May 17, 2018) con informacion detallada sobre procesos de desarrollo y ground truth.

### Investigator Guide disponible: SI
Technical report con ground truth para cada archivo de registro.

### Artefactos de registro incluidos
- NTUSER.DAT (perfiles de usuario)
- SYSTEM (configuracion del sistema)
- SOFTWARE (software instalado)
- SAM (cuentas de usuario y hashes)
- SECURITY (politicas de seguridad)
- Amcache.hve (Windows 8+)
- UserAssist keys
- ShellBag information
- MRU lists
- USB device history
- Network configuration

### Conclusion
Dataset especializado para validar herramientas de analisis de registro de Windows y para entrenamiento en interpretacion de artefactos del registro.

---

## Fuente: NIST CFReDS - Russian Tea Room

**URL**: https://cfreds.nist.gov/all/NIST/RussianTeaRoom
**URL Archivo**: https://cfreds-archive.nist.gov/utf-16-russ.html
**Autor**: NIST
**Fecha**: 2007
**Descargas**: 2,116+
**Tags**: Normal Browsers, Private Browsers, TOR, Browser, Chrome, Internet Explorer

### Descripcion
This data set is for Russian language string searching in unicode UTF16BE encoding. Since the text is bilingual English and Russian, this data set can be used for searching English also.

**Escenario**: The evil Boris and Natasha have escaped from jail and are up to their old tricks. They have stolen the new menu from The Little Russian Tea Room. Your task is to reconstruct the menu from an image (EnCase, iLook) of their hard drive.

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| CFReDS001.E01 | EnCase | Imagen del disco duro con texto en ruso |
| CFReDS001001.asb | ASB | Formato iLook |

### Investigator Guide disponible: Parcial
Desafio de 8 secciones para encontrar y reconstruir el menu ruso.

### Artefactos textuales especificos
- Texto bilingue: Ingles y Ruso
- Codificaciones: Unicode UTF-16BE (big-endian), UTF-16LE, UTF-8
- Debe encontrar 8 secciones del menu

### Técnicas aplicables
- Unicode string searching
- Multi-language text recovery
- Hexadecimal analysis
- Text encoding identification

### Conclusion
Dataset enfocado en habilidades de busqueda de texto Unicode y manejo de multiples idiomas/encodings en entornos forenses.

---

## Fuente: NIST CFReDS - Memory Images

**URL**: https://cfreds.nist.gov/all/NIST/MemoryImages
**URL Archivo**: https://cfreds-archive.nist.gov/mem/memory-images.rar
**Autor**: NIST
**Fecha**: 2020
**Descargas**: 1,662+
**Tags**: Memory

### Descripcion
Live memory capture of images. Contiene capturas de memoria RAM de sistemas en vivo para analisis de memoria forense.

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| memory-images.rar | RAR | Paquete de imagenes de memoria |

### Artefactos tipicos en memoria
- Process lists (lista de procesos activos)
- Network connections (conexiones de red activas)
- Running programs (programas en ejecucion)
- Encryption keys (claves de cifrado en memoria)
- Password strings (contraseñas en texto plano)
- Browser sessions (sesiones de navegador activas)
- Malware artifacts (artefactos de malware en memoria)
- Command history (historial de comandos)
- Registry hives loaded in memory

### Herramientas recomendadas
- Volatility Framework
- Rekall
- MemProcFS

### Conclusion
Dataset para practicar analisis forense de memoria RAM, incluyendo extraccion de procesos, conexiones de red, y artefactos volatiles.

---

## Fuente: NIST CFReDS - Deleted Files Recovery

**URL**: https://cfreds.nist.gov/all/NIST/DeletedFilesRecovery
**URL Archivo**: https://cfreds-archive.nist.gov/dfr-test-images.html
**Autor**: NIST
**Fecha**: 2017
**Descargas**: 1,450+
**Tags**: File Recovery, Imaging, DFR, Database Carving, File Carving, Image Carving, Other Carving, Video Carving

### Descripcion
Compressed dd images used to test metadata-based deleted file recovery forensic tools.

**NOTA**: Estas imagenes NO son para probar herramientas de file carving (herramientas que escanean bloques no asignados para encontrar headers y trailers). La pagina contiene un documento describiendo la creacion y layout de cada imagen.

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| dfr-01-fat.dd.bz2 | bz2 | Imagen FAT con archivos eliminados |
| dfr-01-xfat.dd.bz2 | bz2 | Imagen exFAT |
| dfr-01-ntfs.dd.bz2 | bz2 | Imagen NTFS |
| dfr-01-ext.dd.bz2 | bz2 | Imagen ext (Linux) |
| dfr-01-osx.dd.bz2 | bz2 | Imagen HFS+ (Mac OS X) |
| (85 archivos adicionales) | bz2 | Variaciones con diferentes escenarios |

**Total**: 90 archivos de imagen

### Investigator Guide disponible: SI
Documento describiendo la creacion y layout de cada imagen.

### Sistemas de archivo cubiertos
- FAT12/16/32
- exFAT
- NTFS
- ext2/3/4
- HFS+ (Mac OS X)

### Conclusion
Dataset exhaustivo para probar herramientas de recuperacion de archivos basadas en metadatos en multiples sistemas de archivos.

---

## Fuente: NIST CFReDS - File Carving

**URL**: https://cfreds.nist.gov/all/NIST/FileCarving
**URL Archivo**: https://cfreds-archive.nist.gov/FileCarving/index.html
**Autor**: NIST
**Fecha**: 2022
**Descargas**: 1,608+
**Tags**: File Carving, Database Carving, Image Carving, Other Carving, Video Carving

### Descripcion
This data set has a variety of files in unallocated space with no metadata to locate the files so that software applications with file carving capabilities can be evaluated.

Collection of 30 image files for testing file carving on several types of files (Graphic, Video, Document, Audio and Archive) in several scenarios (contiguous, fragmented, and nested).

### Artefactos disponibles

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| index.html | HTML | Pagina con descripcion completa y enlaces a 30 imagenes |
| (30 imagenes) | DD | Imagenes con archivos en unallocated space |

### Tipos de archivos para carving
- **Graphic**: JPEG, PNG, GIF, BMP
- **Video**: AVI, MP4, MOV
- **Document**: PDF, DOC, DOCX
- **Audio**: MP3, WAV
- **Archive**: ZIP, RAR

### Escenarios de carving
- **Contiguous**: Archivos sin fragmentacion
- **Fragmented**: Archivos divididos en multiples fragmentos
- **Nested**: Archivos dentro de otros archivos

### Conclusion
Dataset completo para evaluar capacidades de file carving en diferentes tipos de archivos y escenarios.

---

## Fuente: NIST CFReDS - String Search V1.1 (Federated Testing)

**URL**: Referenciado desde https://cfreds.nist.gov
**Autor**: NIST/CFTT
**Fecha**: 2020
**Descargas**: 256+

### Descripcion
String Search Test Data for use with Federated Testing 4.0 and later.

Package includes two DD files with known content for testing string search forensic tools.

### Artefactos disponibles

| Archivo | Contenido |
|---------|-----------|
| Windows DD Image | Target strings en FAT, ExFAT, NTFS + unallocated space |
| Unix-like DD Image | Target strings en HFS+ journaled (case insensitive/sensitive), ext4, APFS |

### Caracteristicas de las cadenas
- Cada cadena codificada en ASCII
- Localizada en archivos activos y archivos eliminados recuperables
- Algunas en Unicode UTF-8, UTF-16BE, UTF-16LE con byte-order-mark
- Cada instancia tiene un String ID unico
- Incluye casos especiales: UTF-16 sin BOM, combining characters, ligatures
- Formatted strings, strings spanning fragments

### Casos de prueba especiales
- FT-SS-07: Unicode sin BOM, combining characters (diacritics), ligatures ("fi")
- FT-SS-09: Formatted strings, strings spanning fragments, areas inaccesibles

### Conclusion
Dataset estandarizado para pruebas formales de herramientas de busqueda de cadenas en diferentes encodings y sistemas de archivos.

---

## Fuente: NIST CFReDS - Container Files

**Descripcion**: String searching on container and nested container files.
Dataset para probar busqueda de cadenas en archivos contenedores y contenedores anidados.

---

## Fuente: NIST CFReDS - Drone Images

**Descripcion**: Images from 60 drones and associated controllers, connected mobile devices and computers.
Dataset con imagenes de 60 drones incluyendo DJI Phantom 4, controladores, dispositivos moviles conectados y computadoras.

---

## Fuente: NIST CFReDS - Mobile Device Images

**Descripcion**: Chip-off / JTAG binary images.
Dataset con imagenes binarias de dispositivos moviles para practica de extraccion fisica (chip-off y JTAG).

---

## Fuente: NIST CFReDS - Basic Mac Image

**Descripcion**: Mac File Systems (HFS+ OS Extended Journaling, HFS+ OS Extended, HFS+ OS Standard & Unix).
Dataset basico para analisis de sistemas de archivos Mac.

---

## Fuente: NIST CFReDS - DCFL Control Image

**Descripcion**: DCFL Control image.
Imagen de control del Defense Cyber Crime Forensic Laboratory para verificacion de herramientas.

---

## Fuente: NIST CFReDS - Create a Reference Drive

**Descripcion**: Create a drive with known hash values. The creation process also verifies that the computer hardware and the drive are working as expected.
Procedimiento para crear unidades de referencia con valores hash conocidos.

---

## Fuente: NIST CFReDS - ASB Image, DD, E01 (Russian UTF-8)

**Descripcion**: Unicode string search in Russian (UTF-8).
Variante del Russian Tea Room con codificacion UTF-8 en lugar de UTF-16BE.

---

## Fuente: NIST CFReDS - File Carving CFTT Images

**Descripcion**: Images used for CFTT file carving test reports.
Imagenes utilizadas para reportes de pruebas de file carving del CFTT.

---

## OTROS DATASETS DESTACADOS EN CFReDS (Contribuyentes Externos)

### CyberDefenders Challenges
- **URL**: https://cfreds.nist.gov/all/CyberDefenders/CyberDefenderschallenges
- Desafios practicos de forense digital

### Mjolnir Security - 2025 Threat Hunting Workshop
- **URL**: https://cfreds.nist.gov/all/MjolnirSecurity/2025ThreatHuntingWorkshop
- **Tags**: Memory
- Dataset para taller de threat hunting (528 descargas)

### Cellebrite CTF 2025 / 2024
- Datasets para competencias de forense movil (iOS)

### 2026 MSAB CTF - Android / iOS
- Datasets para competencias MSAB

### LOTL APT Red Team Dataset (Sunny Thur, 2026)
- **Tags**: Databases, Cloud & Remote Systems, Windows
- Dataset de simulacion de APT usando tecnicas Living Off The Land

### LOTL APT Red Team Dataset
- Dataset para practicar deteccion de tecnicas APT y Living Off The Land

---

## TABLA RESUMEN DE TODOS LOS DATASETS NIST CFReDS

| # | Dataset | Escenario | Artefactos | Preguntas | Answer Key |
|---|---------|-----------|------------|-----------|------------|
| 1 | **Hacking Case** | Laptop hacker + WiFi sniffing | DD Image, EnCase, Logs | 31 | SI |
| 2 | **Data Leakage Case** | Insider theft + exfiltracion | PC Image, USB Image, CD-R | 60 | SI |
| 3 | **Rhino Hunt** | Busqueda de imagenes borradas | USB Image, Network Traces | N/A | SI (PDF) |
| 4 | **Registry Forensics** | Analisis de registro Windows | Registry Hives multiples | N/A | SI (Ground Truth) |
| 5 | **Russian Tea Room** | Busqueda Unicode ruso | EnCase Image | 8 secciones | Parcial |
| 6 | **ASB Image/DD/E01** | Russian UTF-8 | Multiple formats | N/A | N/A |
| 7 | **Memory Images** | Capturas de memoria RAM | RAR con memory dumps | N/A | N/A |
| 8 | **Deleted File Recovery** | Recuperacion archivos borrados | 90 imagenes DD (multi-FS) | N/A | SI (Layout doc) |
| 9 | **File Carving** | Carving de archivos | 30 imagenes DD | N/A | N/A |
| 10 | **String Search V1.1** | Busqueda de cadenas | 2 DD images (Windows/Unix) | Test cases | SI |
| 11 | **Container Files** | Contenedores anidados | Container images | N/A | N/A |
| 12 | **Drone Images** | Forense de drones | 60 drone images | N/A | N/A |
| 13 | **Mobile Device Images** | Chip-off/JTAG | Binary images | N/A | N/A |
| 14 | **Basic Mac Image** | Sistemas Mac | Mac filesystem images | N/A | N/A |
| 15 | **DCFL** | Control image | Control image | N/A | N/A |
| 16 | **Create Reference Drive** | Hash verification | Reference drive | N/A | N/A |
| 17 | **File Carving CFTT** | Carving para CFTT | CFTT test images | N/A | SI |

---

## GLOSARIO DE ARTEFACTOS TEXTUALES IDENTIFICADOS

### Logs de autenticacion
- Windows Event IDs 4624 (Logon), 4625 (Logon Failure), 4634/4637 (Logoff), 4647 (User-initiated logoff), 1100 (Shutdown), 4608 (Startup)
- Encontrados en: Data Leakage Case, Hacking Case

### Bash history / Command history
- Windows RunMRU registry keys
- Prefetch files
- LNK files (Jump Lists)

### Network flows
- PCAP captures (interception file en Hacking Case)
- DHCP logs (registry: TimeZoneInformation, NetworkCards)
- DNS queries (browser history)

### File metadata / timestamps
- MFT entries (NTFS)
- $STANDARD_INFORMATION, $FILE_NAME attributes
- MACB timestamps (Modification, Access, Creation, Birth)

### Registry entries
- HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion
- HKLM\SYSTEM\CurrentControlSet\Control
- HKU\{SID}\Software\Microsoft\Windows\CurrentVersion\Explorer
- SAM hives (user accounts)
- Amcache.hve (program execution Windows 8+)

### Process lists
- Volatile data from memory images
- Prefetch files (Windows)

### Memory strings
- Passwords in plaintext
- Encryption keys
- Running process information
- Network connection tables

### Email headers
- OST/PST file parsing
- SMTP, NNTP settings in registry
- Webmail artifacts (browser cache)

### DNS logs
- Browser history (index.dat, TypedURLs)
- Network packet captures

---

*Reporte generado a partir de la exploracion exhaustiva del portal NIST CFReDS*
*URLs principales: https://cfreds.nist.gov/ y https://cfreds-archive.nist.gov/*
