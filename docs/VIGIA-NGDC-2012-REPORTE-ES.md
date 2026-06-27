VIGIA — INFORME FORENSE DE ANALISIS DE INTENCIONALIDAD
=======================================================
ID de Caso      : VIGIA-NGDC-2012
Investigador    : VIGIA — Agente Forense Autonomo (Claude Code / Anthropic)
Evidencia       : /home/labestiadevigia/Downloads/National Gallery DC 2012/
Modo            : Claude Code (Modo 2)
Marca temporal  : 2026-06-27T03:30:00Z
Fase SANS       : Fase 5 — Lecciones Aprendidas (investigacion completa)

INVENTARIO DE EVIDENCIA Y CADENA DE CUSTODIA
---------------------------------------------

| # | Artefacto | SHA-256 | Tamano |
|---|-----------|---------|--------|
| 1 | carry-tablet-2012-07-16-final.E01 | 26a6ea3049c06afdd34862c453fc272a5ab4c64954ae51d23cf9df688473a448 | 1.1 GB |
| 2 | tracy-phone-2012-07-15-final.E01 | 71aed05a86a753dec4ef4033ed7f52d6577ccb534ca0d1e83ffd27683e621607 | 752 MB |
| 3 | Tracy-phone-2012-07-15-1316.L01 | a14525b7ece67131d5943e1db5847cbb51513e384b49b7fa9921480530223f52 | 29 MB |
| 4 | carry-phone-2012-07-15-final.zip | 5cfec4e099e70529072b6934c6f98f97492985e5a48daeb64549f96719792d9e | 191 MB |
| 5 | carry-phone-logical-2012-07-15-0618.zip | cbcee1cb354884ebfa302ad5a6e41c9980fc3ba252b2f74e732b2162540f7357 | 30 MB |
| 6 | Tracy-phone-logical-2012-07-15-1317.zip | 1e4287dff75dd2fb84ff46be3ef5f3152bb894b64030831b442776e522d30329 | 18 MB |
| 7 | carry-tablet-2012-07-16-final.tar | c70762e49db8f95cfd11246a3e84d1fca8a20d7182d1525b462638a28331793f | 779 MB |
| 8 | tracy-phone-2012-07-15-final.tar | b209e812aeeab7b6234f8f6d16be6b63027e02d667d8882104bd52b3aea204a1 | 752 MB |
| 9 | email.zip | d1c4470e9e058f83798b6c0c2856e85df8747783f2105f8c354f366d30ab5505 | 16 KB |
| 10 | ngdc-exterior-2012-07-06.pcap | b2e89885b1c3775ddff8d106cdead6ae1b5331d53b3f539ac9c27010244c0895 | 143 MB |
| 11 | ngdc-exterior-2012-07-09.pcap | dc317d6a9f6942148e726097e95d7f4d3bd0cc95bee0480d0797b60020147a8b | 45 MB |
| 12 | ngdc-exterior-2012-07-10.pcap | 863587be812b9ed6dd184ad0c5960d4ebe4e713b767a07860aec946a5442c73b | 37 MB |
| 13 | ngdc-interior-2012-07-06.pcap | d5f019db5796bd2118d8b917ae26805bb6cb3c978fd983860035f599d8ccb051 | 36 MB |
| 14 | ngdc-interior-2012-07-09.pcap | 67eb2629d2f29ea4b7101f3b03209621294b1bf0909d515927514b0c00dac449 | 39 MB |
| 15 | ngdc-interior-2012-07-10.pcap | d47a9e1144c92a5a818b295546bf5c3219a2bb18a21bb9dcc9702ee48f200548 | 25 MB |
| 16 | exterior-2012-07-12.txt | 25f5f2920a5d403d4a8bbacaad9acb72ea40b916ba8d8f03296d59d419474e81 | 53 MB |
| 17 | interior-2012-07-12.txt | 2b2cbcc969cfa9d7dc7ad1087cc59e456e941c3c7c5d4416ba2a9ce0b83d7e66 | 4.2 MB |

Artefactos NO analizados (descargas incompletas):
- tracy-home-2012-07-16-final.E01 / .E02 — 0 bytes cada uno
- 4x Unconfirmed *.crdownload — descargas parciales

RESUMEN EJECUTIVO
-----------------
Esta investigacion revela una conspiracion multi-actor para robar una exposicion de
estampillas raras de la National Gallery of Art en Washington, DC. La conspiracion
involucra al menos 5 individuos identificados que operan a traves de acceso interno
privilegiado, coordinacion logistica, conexiones de inteligencia extranjera,
exfiltracion de documentos y planificacion de evasion de seguridad fisica. La
evidencia abarca del 19 de junio al 16 de julio de 2012, a traves de capturas de
keylogger, correo electronico, SMS, extracciones de telefonos, forense de tablet,
capturas de red e historial de navegacion.

La investigacion identifica dos actores principales:
- **Tracy SumTwelve** (empleada de la National Gallery, alias "Coral Blue Two"):
  insider que exfiltro documentos de seguro de estampillas, transmitio el horario
  de turnos de seguridad a co-conspiradores, y fisicamente introdujo la tablet de
  Carry pasando los controles de seguridad de la Galeria.
- **Carry** (coordinadora externa, email: cat2welve@gmail.com / carrysum2012@yahoo.com):
  planificadora operativa que coordino una historia de cobertura de "flash mob",
  investigo tecnicas de cegado de camaras y apertura de cerraduras, se comunico con
  un contacto de inteligencia extranjera ("Alex J" de Krasnovia), gestiono documentos
  de pasaporte falsificados, instalo herramientas de esteganografia, e intento
  destruir evidencia.

Veredicto General: **MALICIA** — Ocultamiento activo de intencion a traves de
archivos encriptados, herramientas de esteganografia, destruccion de evidencia
(limpieza con Forever Gone), y seguridad operativa multicapa (emails con alias,
canales de comunicacion encubiertos, historia de cobertura de flash mob).

ACTORES IDENTIFICADOS
---------------------

| Actor | Identificadores | Rol | Veredicto |
|-------|----------------|-----|-----------|
| Tracy SumTwelve | tracysumtwelve (MacBook), coralbluetwo@hotmail.com, coralblue2@yahoo.com, tracy.sumtwelve@nationalgallerydc.org | Insider: robo de documentos, facilitacion de evasion de seguridad, receptora de soborno | MALICIA |
| Carry | cat2welve@gmail.com, carrysum2012@yahoo.com, carry.sums (Skype), +12027252124 | Coordinadora externa: planificacion operativa, enlace con inteligencia extranjera, destruccion de evidencia | MALICIA |
| Perry Patsum | perrypatsum@yahoo.com | Co-conspirador externo: recibe documentos robados, provee cargas esteganograficas | INTENCION |
| Alex J | alex.jfam11@gmail.com, alex.jfam11@krasnovia.org | Contacto de inteligencia extranjera: recomienda esteganografia, coordina entrada de asociados | INTENCION |
| Drex Mustafar ("Mike") | bubbahotep2012@hotmail.com | Coordinador de flash mob: provee logistica de operacion de cobertura | SOSPECHA |
| Pat TeeSumTwelve | patsumtwelve@gmail.com, +15713083236 | Hermano/a de Tracy: consciente de la conversion de formato de documentos para la conspiracion | SOSPECHA |
| Terry SumTwelve | just.terry.22@gmail.com, terrysumtwelve (MacBook) | Hija de Tracy: sin involucramiento directo, contexto de presion financiera como motivo | RUIDO |
| Joe SumTwelve | joe.sum.twelve@gmail.com | Operador del keylogger: recibe todas las capturas de pulsaciones del MacBook de Tracy | INTENCION |

CREDENCIALES CAPTURADAS
------------------------

| Cuenta | Contrasena | Fuente |
|--------|-----------|--------|
| Login MacBook Air de Tracy (tracysumtwelve) | legalBee | Email keylogger #1 |
| coralbluetwo@hotmail.com | legalBee | Email keylogger #1 |
| just.terry.22@gmail.com (Terry) | privateschool | Email keylogger #11 |
| ZIP encriptado (documents.zip) | Hercules ("el nombre de tu viejo perro") | Email keylogger #9-10 |

LINEA TEMPORAL DE EVENTOS
--------------------------

| Fecha | Evento | Fuente | Significado |
|-------|--------|--------|-------------|
| 2012-06-07 | Carry crea Gmail (cat2welve) y Skype (carry.sums); contacta a Alex J | Tablet Carry Gmail | Configuracion inicial de infraestructura operativa |
| 2012-06-19 | Perry envia email a Coral (coralbluetwo@hotmail.com): "Crazydave by the VMs" con adjunto MP3 | Telefono Tracy Hotmail | Sospecha de entrega de carga esteganografica |
| 2012-06-27 | Alex J envia email a Carry: "Krasnovia!" — una sola palabra | Tablet Carry Gmail | Senal de afiliacion extranjera |
| 2012-06-27 | Alex J recomienda apps de esteganografia a Carry | Tablet Carry Gmail | Infraestructura de comunicacion encubierta |
| 2012-06-28 | Keylogger LogKext activo en MacBook de Tracy; Tracy inicia sesion en coralbluetwo@hotmail.com | Email keylogger #1 | Infraestructura de vigilancia operativa |
| 2012-06-29 | Tracy envia email a Perry: "si surge algo en lo que podamos meternos... presto atencion a los memos y papeles en mi escritorio" | Email keylogger #2 | Comienza la recoleccion activa de inteligencia interna |
| 2012-07-02 | Tracy reporta a Perry: "exposicion extranjera viene, gran cosa, mucho papeleo" | Emails keylogger #3-4 | Tracy identifica la exposicion objetivo |
| 2012-07-03 | Tracy a Perry: "coleccion rara de estampillas... tal vez este sea nuestro boleto" | Email keylogger #6 | Objetivo de la conspiracion identificado: estampillas raras |
| 2012-07-04 | Alex J a Carry: "amigos trabajando en un nuevo manuscrito, te interesa?" | Tablet Carry Gmail | Senal de reclutamiento extranjero |
| 2012-07-05 | Alex J envia enlace Dropbox ("funny video.mp4") a Carry; Carry contacta a Tracy via Facebook para almorzar | Tablet Carry Gmail + Yahoo | Sospecha de carga esteganografica + pretexto de ingenieria social para Tracy |
| 2012-07-06 | Carry instala herramienta de esteganografia SDDroid en tablet; Tracy busca "valor de estampillas internacionales" | Tablet Carry apps + keylogger | Preparacion operativa paralela |
| 2012-07-06 | Red: 10.10.1.119 comienza a escanear 10.10.1.169 (puerto 8080 abierto, SNMP, barrido ARP) | PCAP exterior 07-06 | Monitoreo de red automatizado (probablemente NMS, no adversarial) |
| 2012-07-06 | Tracy navega: Louvre, Guggenheim, MOMA, NGA, "Scibec de Carpi ceiling" | PCAP interior 07-06 | Investigacion comparativa de museos |
| 2012-07-08 | Tracy fotografia la National Gallery y area del Mall (30 fotos, GPS confirmado) | Telefono Tracy EXIF | Reconocimiento fisico del objetivo |
| 2012-07-09 | Carry envia email a Drex Mustafar: plan operativo — "dos equipos, entrada este y oeste, reunion segundo piso pasillo principal lado este, 12:00 PM en punto" | Tablet Carry Gmail | Plan operativo documentado |
| 2012-07-09 | Carry pide a Tracy meter tablet pasando seguridad; Tracy navega paginas de planificacion de flash mob | Tablet Carry Yahoo + PCAP | Negociacion de evasion de seguridad fisica |
| 2012-07-09 | Tracy crea ZIP encriptado de documentos de seguro/estampillas (contrasena: Hercules) | Email keylogger #9 | Exfiltracion de documentos |
| 2012-07-10 | Tracy confirma a Carry: "Definitivamente puedo ayudar a meter tu tablet" | Tablet Carry Yahoo | Evasion de seguridad confirmada |
| 2012-07-10 | Carry navega: cegar camaras de vigilancia, bombas de humo, granadas de humo, cunas para candados, apertura de cerraduras, entrada con tarjeta de credito | Tablet Carry navegador | Investigacion tactica para penetracion fisica |
| 2012-07-10 | Carry sube dumps de ePassport y lector de pasaportes JMRTD a Yahoo Mail | Tablet Carry navegador | Documentos de viaje falsificados para asociados extranjeros |
| 2012-07-10 | Tracy envia email a Perry: documentos de estampillas + pista de contrasena "el nombre de tu viejo perro" | Email keylogger #10 | Documentos robados transmitidos a co-conspirador |
| 2012-07-10 | Pat SMS a Tracy: "coral tiene email, el adjunto necesita cambiarse a pdf" | Telefono Tracy SMS | Tercero consciente del esquema de documentos |
| 2012-07-10 | Red: 192.168.1.101 busca "National Gallery East Wing", "I.M. Pei East Building", "cuidado apropiado para estampillas" | PCAP interior 07-10 | Reconocimiento final de distribucion del edificio y manejo de estampillas |
| 2012-07-11 | Tracy envia horario de turnos de seguridad a Carry (descargado como securedownload.pdf a las 19:11) | Tablet Carry descargas | Informacion clasificada de seguridad transmitida |
| 2012-07-11 | Tracy SMS a Carry: "Encuentrame afuera, yo meto la tablet" | Telefono Tracy SMS | Contrabando fisico confirmado |
| 2012-07-11 | Tracy: "Me vendria bien algo de efectivo extra pero por favor ten cuidado" | Tablet Carry Yahoo | Acuerdo de soborno documentado |
| 2012-07-11 | Alex J envia "archivos corregidos" (firmas de pasaporte) a Carry | Tablet Carry Gmail | Coordinacion de falsificacion de documentos extranjeros |
| 2012-07-11 | Carry reenvía archivos de pasaporte a amonous@yahoo.com | Tablet Carry Gmail | Distribucion de pasaportes a terceros |
| 2012-07-12 | Carry ejecuta limpieza Forever Gone: ~250 archivos destruidos 05:03–06:25 | Tablet Carry archivos eliminados | Destruccion anti-forense de evidencia |
| 2012-07-12 | Carry email a Alex: "Tengo nuestro plan armado... que tus asociados se reunan conmigo en la ciudad la proxima semana" | Tablet Carry Gmail | Coordinacion final con contacto extranjero |
| 2012-07-12 | Tracy SMS a Carry: "Como va el flashmob?" | Telefono Tracy SMS | Verificacion post-infiltracion |
| 2012-07-15 | Telefono de Tracy y telefono de Carry incautados (extracciones logicas + fisicas) | Marcas temporales L01/E01 | Adquisicion de evidencia |
| 2012-07-16 | Tablet de Carry incautada (imagen E01) | Metadatos E01 | Adquisicion de evidencia |

HALLAZGOS
---------

Hallazgo ID  : F-001
Titulo       : Exfiltracion de Documentos por Insider (Tracy → Perry)
Veredicto    : MALICIA
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : Emails keylogger #9-10, Telefono Tracy Hotmail (documents.zip, docs.zip)
Herramientas : sha256sum, unzip, fls, icat, sqlite3
Primeridad   : Tracy escribio comandos de terminal `zip -e documents.zip Sta* Ins*` con
               contrasena "Hercules" ingresada dos veces. Tres archivos PDF llamados
               "Stamp Insurance 1/2/3.pdf" encontrados en ZIP encriptado en la bandeja
               de entrada Hotmail del telefono de Tracy.
Segundidad   : Una empleada de la National Gallery creando archivos encriptados con
               contrasena de documentos internos de valuacion de seguros y transmitiendolos
               a una direccion de email externa (perrypatsum@yahoo.com) es estructuralmente
               incompatible con cualquier proceso de negocio legitimo. La pista de
               contrasena ("el nombre de tu viejo perro") agrega una capa deliberada de
               ofuscacion mas alla de la encriptacion misma.
Terceridad   : Tracy armo como arma sus privilegios de acceso a documentos para extraer
               sistematicamente valuaciones de seguros que revelan el valor monetario de la
               exposicion de estampillas. Este es un patron de transferencia de autoridad
               Carnegie: tomar prestada la confianza institucional para facilitar la
               planificacion de un robo.
Carnegie     : Transferencia de autoridad (confianza institucional → ganancia personal)
MITRE TTPs   : T1567.002 (Exfiltracion via Servicio Web), T1560.001 (Archivado de Datos
               Recolectados: via Utilidad)
Abogado del Diablo: Tracy podria haber estado compartiendo documentos de trabajo
               legitimamente con un amigo de confianza para asesoramiento sobre asuntos
               de seguros. Sin embargo, esto falla contra: (a) la encriptacion explicita
               con contrasena no laboral, (b) la pista de contrasena por canal separado,
               (c) los emails precedentes enmarcando esto como "nuestro boleto" para
               ganancia financiera, (d) ninguna razon de negocio legitima para compartir
               valuaciones internas de seguros externamente. Hipotesis benigna RECHAZADA.
Corroboracion: Emails keylogger (fuente 1) + bandeja Hotmail telefono Tracy (fuente 2) +
               hilo email Yahoo tablet Carry (fuente 3)
Auto-Correccion: Inicialmente considerado INTENCION. Elevado a MALICIA basado en
               entrega de contrasena multi-canal y el enmarcado explicito "nuestro boleto"
               demostrando consciencia de culpa.

Hallazgo ID  : F-002
Titulo       : Conspiracion de Evasion de Seguridad Fisica (Tracy + Carry)
Veredicto    : MALICIA
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : Tablet Carry emails Yahoo, Telefono Tracy SMS, Tablet Carry historial
               navegador, Telefono Tracy Hotmail (needs.txt), Tablet Carry descargas
               (securedownload.pdf)
Herramientas : fls, icat, sqlite3, sha256sum
Primeridad   : Hilo de email entre Carry y Tracy muestra negociacion para meter tablet
               pasando seguridad de la Galeria. SMS de Tracy "Encuentrame afuera, yo meto
               la tablet." Historial de navegacion en tablet de Carry muestra busquedas
               sobre cegar camaras de vigilancia, bombas de humo, cunas para candados y
               apertura de cerraduras. Archivo "needs.txt" en telefono de Tracy lista
               pintura en aerosol para camaras y granadas de humo.
Segundidad   : Eventos legitimos de flash mob no requieren cegar camaras de seguridad,
               granadas de humo, herramientas para forzar cerraduras, ni contrabando de
               dispositivos pasando puntos de control de seguridad.
Terceridad   : Carry investigo y documento sistematicamente metodos para derrotar cada
               capa de seguridad fisica de la Galeria. El rol de Tracy como facilitadora
               de acceso interno transforma esto de amenaza externa a ataque habilitado
               por insider. La historia de cobertura del "flash mob" es un patron de
               prueba social Carnegie.
Carnegie     : Prueba social (flash mob como cobertura), Reciprocidad (soborno)
MITRE TTPs   : T1200 (Adiciones de Hardware), T1036 (Enmascaramiento),
               T1562.001 (Deteriorar Defensas)
Abogado del Diablo: Carry podria genuinamente estar planificando un flash mob artistico.
               Sin embargo: "needs.txt" explicitamente incluye granadas de humo "como
               medio de escape si nos atrapan." Hipotesis benigna RECHAZADA.
Corroboracion: 5 fuentes independientes confirman.
Auto-Correccion: Sin degradacion justificada.

Hallazgo ID  : F-003
Titulo       : Contacto de Inteligencia Extranjera e Infraestructura de Esteganografia
Veredicto    : INTENCION
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : Tablet Carry Gmail (alex.jfam11@krasnovia.org), Tablet Carry apps (SDDroid),
               Tablet Carry descargas (funny video.mp4), Tablet Carry Gmail (dumps ePassport)
Herramientas : fls, icat, sqlite3
Primeridad   : Alex J usa dominio krasnovia.org. Recomendo apps de esteganografia a Carry.
               SDDroid instalado en tablet de Carry. Video descargado 4 veces. Carry subio
               archivos dump de ePassport y lector JMRTD a Yahoo Mail.
Segundidad   : Herramientas de esteganografia no tienen uso legitimo en planificacion de
               flash mob. Archivos dump de pasaportes electronicos no tienen explicacion
               benigna para un ciudadano privado.
Terceridad   : Alex J opera como manejador extranjero coordinando con Carry para:
               (a) establecer comunicacion encubierta via esteganografia, (b) preparar
               documentos de viaje falsificados para asociados entrando a EEUU.
Carnegie     : Simpatia (Alex cultiva relacion personal antes de tareas operativas)
MITRE TTPs   : T1027.003 (Esteganografia), T1588.002 (Obtener Capacidades: Herramienta)
Abogado del Diablo: La secuencia recomendacion → instalacion → entrega de carga elimina
               la curiosidad. Los dumps de pasaportes no tienen uso benigno. Hipotesis
               benigna RECHAZADA para la falsificacion de pasaportes. Contenido
               esteganografico no verificable (limitacion documentada).
Corroboracion: 4 fuentes independientes.
Auto-Correccion: Veredicto mantenido en INTENCION (no MALICIA) porque el contenido
               esteganografico de "funny video.mp4" no fue extraido ni verificado.

Hallazgo ID  : F-004
Titulo       : Destruccion Anti-Forense de Evidencia (Carry)
Veredicto    : MALICIA
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : Tablet Carry /media/Forever Gone/ (~250 archivos eliminados)
Herramientas : fls -r (listado recursivo de archivos)
Primeridad   : Directorio contiene ~250 archivos eliminados con marca temporal
               2012-07-12 entre 05:03 y 06:25. "Forever Gone" es una aplicacion Android
               de eliminacion segura.
Segundidad   : Ejecutar una herramienta de eliminacion segura a las 5:03 AM, tres dias
               antes de la incautacion del dispositivo, apuntando a cientos de archivos,
               es estructuralmente incompatible con mantenimiento normal.
Terceridad   : Carry anticipo el examen forense y destruyo evidencia deliberadamente.
               Esta es la capa de ocultamiento que separa MALICIA de INTENCION.
Carnegie     : N/A
MITRE TTPs   : T1070.004 (Eliminacion de Indicadores: Eliminacion de Archivos),
               T1485 (Destruccion de Datos)
Abogado del Diablo: Las 5:03 AM no es hora de limpieza rutinaria. "Forever Gone" es
               especificamente comercializado para prevencion de recuperacion forense.
               Hipotesis benigna RECHAZADA.
Corroboracion: 3 fuentes.
Auto-Correccion: Sin degradacion justificada.

Hallazgo ID  : F-005
Titulo       : Infraestructura de Vigilancia por Keylogger (Joe → Tracy)
Veredicto    : INTENCION
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : email.zip (12 archivos EML), README.txt
Herramientas : sha256sum, unzip
Primeridad   : Daemon LogKext corriendo en MacBook de Tracy captura todas las
               pulsaciones y las envia automaticamente a joe.sum.twelve@gmail.com.
Segundidad   : Un keylogger en MacBook personal transmitiendo a email externo no es
               monitoreo de sistema legitimo. Requiere acceso root e instalacion
               deliberada.
Terceridad   : El rol de Joe es ambiguo: puede ser (a) informante policial,
               (b) conspirador independiente, o (c) familiar controlador.
Carnegie     : N/A
MITRE TTPs   : T1056.001 (Captura de Entrada: Keylogging), T1020 (Exfiltracion Automatizada)
Abogado del Diablo: Joe puede ser una herramienta autorizada de aplicacion de la ley.
               Sin documentacion de autorizacion, la autoridad legal de Joe para instalar
               el keylogger es inverificable. Veredicto mantenido en INTENCION (no MALICIA).
Corroboracion: 12 capturas de email independientes + metadatos README.txt
Auto-Correccion: Inicialmente considerado MALICIA. Degradado a INTENCION porque el
               rol/autorizacion de Joe es ambiguo.

Hallazgo ID  : F-006
Titulo       : Reconocimiento de Red (10.10.1.119 → 10.10.1.169)
Veredicto    : SOSPECHA
Confianza    : MEDIA
Estado       : INFERIDO
Artefacto    : PCAPs exterior 07-06, 07-09, 07-10; log texto exterior 07-12
Herramientas : tcpdump, analisis de texto
Primeridad   : Host 10.10.1.119 realiza barridos ARP persistentes, SNMP GetRequest
               cada ~10 minutos, sondeos de puertos TCP, y conexiones TCP exitosas al
               puerto 8080 en 10.10.1.169 cada ~10 minutos durante tres dias consecutivos.
Segundidad   : La regularidad y persistencia son consistentes con software de gestion
               de red automatizado (SolarWinds, Nagios).
Terceridad   : Sin analisis de payload de las sesiones en puerto 8080, la intencion
               no puede determinarse.
Carnegie     : N/A
MITRE TTPs   : T1046 (Descubrimiento de Servicios de Red) — si es adversarial
Abogado del Diablo: Comportamiento estandar de NMS. Hipotesis benigna es FUERTE.
Corroboracion: Tipo de fuente unico (capturas de red).
Auto-Correccion: REGISTRO DE COMPUERTA DE REFUTACION — F-006
               Veredicto candidato: INTENCION
               Compuerta aplicada: Compuerta de Corroboracion Daubert
               Regla: n_artefactos < 2 para esta clase de evidencia → tope en SOSPECHA
               Resultado: Candidato RECHAZADO pre-emision. Emitido como SOSPECHA.

Hallazgo ID  : F-007
Titulo       : Plan Operativo — Cobertura de Flash Mob para Infiltracion de Galeria
Veredicto    : MALICIA
Confianza    : ALTA
Estado       : CONFIRMADO
Artefacto    : Tablet Carry Gmail (hilo Drex Mustafar), Tablet Carry historial navegador,
               Tablet Carry Yahoo (hilo Tracy), Telefono Tracy SMS
Herramientas : fls, icat, sqlite3
Primeridad   : Carry envia email a Drex Mustafar: "dos equipos, un grupo entrando por
               la entrada este y el otro por el oeste. Los grupos se reunen en el segundo
               piso pasillo principal lado este. Aqui es donde esta la nueva exposicion.
               Quiero que el evento arranque a las 12:00 PM en punto."
Segundidad   : Flash mobs legitimos no especifican entrada estilo militar por multiples
               entradas con punto de reunion en una exposicion especifica.
Terceridad   : El flash mob es una operacion de cobertura. Carry usa el concepto de
               una reunion publica legitima para (a) crear una distraccion, (b) posicionar
               multiples personas en la exposicion de estampillas, y (c) proveer
               negacion plausible para una presencia coordinada cerca del objetivo.
Carnegie     : Prueba social + Autoridad
MITRE TTPs   : T1036.005 (Enmascaramiento: Coincidir con Nombre/Ubicacion Legitima)
Abogado del Diablo: La misma persona investigo bombas de humo, cegado de camaras,
               y apertura de cerraduras. "needs.txt" lista equipo de escape. El hilo con
               Tracy discute explicitamente soborno. Ningun flash mob legitimo requiere
               pasaportes encriptados para participantes. Hipotesis benigna COMPLETAMENTE
               RECHAZADA a traves de 4 fuentes independientes.
Corroboracion: Email a Drex (fuente 1) + hilo email Tracy (fuente 2) + historial
               navegador (fuente 3) + SMS (fuente 4)
Auto-Correccion: Sin degradacion justificada.

HERRAMIENTAS FORENSES UTILIZADAS
---------------------------------

| Herramienta | Proposito | Artefactos procesados |
|-------------|----------|----------------------|
| sha256sum | Hash SHA-256 para cadena de custodia | 17 artefactos primarios |
| ewfinfo | Metadatos de imagen EWF/E01 | carry-tablet E01, tracy-phone E01, Tracy-phone L01 |
| ewfmount | Montar imagenes E01 como dispositivos de bloque | carry-tablet E01 |
| mmls (-i ewf) | Analisis de tabla de particiones (GPT/MBR) | carry-tablet E01, tracy-phone E01 |
| fsstat (-i ewf) | Metadatos de sistema de archivos (Ext4, HFSX) | 7 particiones analizadas |
| fls (-r, -i ewf) | Listado de archivos incluyendo eliminados | Particiones /data y Data |
| icat (-i ewf) | Extraccion de archivos por inodo | Bases de datos, emails, PDFs, archivos |
| sqlite3 | Consulta de bases de datos SQLite | sms.db, browser2.db, mailstore, notes.sqlite, call_history.db |
| tcpdump (-r, -nn) | Analisis de PCAP | 6 archivos PCAP (325 MB total) |
| unzip (-l, -o) | Extraccion de archivos ZIP | email.zip, extracciones logicas de telefonos |
| file | Identificacion de tipo de archivo | Triaje de evidencia |
| strings | Extraccion de cadenas de texto de binarios | Imagenes de disco |
| Analisis EXIF | Extraccion de coordenadas GPS | 30 fotos geoetiquetadas de Tracy |

TOPOLOGIA DE RED
----------------

Dos puntos de captura confirmados como mismo host via NAT:
- Interior: 192.168.1.101 (lado LAN, unico host activo)
- Exterior: 10.10.1.169 (lado WAN/ruteado, MAC VirtualBox 08:00:27:ef:f7:f8)

Hosts internos:
- 10.10.1.13: Acceso SSH exclusivo a .169 (admin/TI — sin actividad web)
- 10.10.1.119: Escaner de red/NMS (monitoreo automatizado)
- 10.10.1.106/114/116/130/152: Sincronizacion LAN de Dropbox, trafico broadcast
- DNS: regis.ncr.vt.edu, roosevelt.nvc.vt.edu (DNS universidad Virginia Tech)

RESUMEN DE DISPOSITIVOS
------------------------

| Dispositivo | Propietario | Tipo | Evidencia clave |
|-------------|-------------|------|----------------|
| Tracys-MacBook-Air | Tracy | MacBook Air, macOS | Keylogger (LogKext), todas las capturas de pulsaciones |
| Google Nexus S (I9020A) | Carry | Android 2.3.4, T-Mobile | SMS/llamadas (en almacenamiento interno, no en extraccion logica) |
| ASUS Transformer TF101 | Carry | Tablet Android, 28GB | Gmail, Yahoo, navegador, apps, horario de seguridad, destruccion de evidencia |
| Apple iPhone 3G | Tracy | iOS | SMS, Hotmail, fotos GPS, contactos |

LIMITACIONES CONOCIDAS
-----------------------

L-001: Imagen de disco de computadora de Tracy (tracy-home-*.E01) no disponible — 0 bytes.
       Contendria su sistema de archivos macOS, aplicaciones y archivos locales.

L-002: Almacenamiento interno del telefono de Carry (mmssms.db, contacts2.db, mailstore,
       browser.db, talk.db) no presente en la extraccion logica ZIP. La imagen fisica
       completa (carry-phone-2012-07-15-final.zip) no fue procesada.

L-003: Contenido esteganografico de "funny video.mp4" no extraido ni analizado.
       Herramientas especializadas (SDDroid, StegDetect, zsteg) serian necesarias.

L-004: "Crazydave1.mp3" de Perry Patsum no analizado para contenido esteganografico.

L-005: Herramientas MCP (Vigia_Sift_Bridge) no disponibles en esta sesion. Analisis
       realizado con herramientas SIFT directas. Pipeline de scoring deterministico
       no ejecutado.

L-006: tshark no instalado. Analisis de PCAP limitado a tcpdump.

L-007: Hosts 10.10.1.119 y 10.10.1.13 sin evidencia basada en host.

L-008: Tablet de Carry rooteada (Superuser-3.0.7 + busybox). Alcance de modificaciones
       habilitadas por root no completamente catalogado.

CONCLUSION
----------

El caso National Gallery DC 2012 presenta una conspiracion de amenaza interna
multicapa con dimensiones de inteligencia extranjera. La evidencia establece mas alla
de duda razonable:

1. Tracy SumTwelve exploto su empleo en la National Gallery para exfiltrar valuaciones
   de seguros de estampillas, transmitir el horario de turnos de seguridad, y
   facilitar fisicamente la entrada no autorizada de dispositivos — motivada por
   presion financiera (matricula de su hija).

2. Carry orquesto el plan operativo usando una cobertura de "flash mob" mientras
   investigaba contramedidas de seguridad fisica, coordinaba con un contacto extranjero
   (Alex J / Krasnovia), gestionaba documentos de pasaporte falsificados, instalaba
   herramientas de esteganografia, y destruia evidencia pre-incautacion.

3. Perry Patsum recibio documentos robados y puede haber proporcionado cargas
   esteganograficas via archivos MP3.

4. Alex J (krasnovia.org) proporciono guia de tradecraft (esteganografia) y coordino
   la entrada de asociados extranjeros usando documentos de pasaporte falsificados.

5. La conspiracion apuntaba a una exposicion de estampillas raras que llegaba a la
   National Gallery, con una operacion fisica coordinada planificada para "la proxima
   semana" al 12 de julio.

Las capas de ocultamiento — archivos encriptados, infraestructura de esteganografia,
emails con alias (Coral Blue Two), destruccion de evidencia (Forever Gone), y
operaciones de cobertura (flash mob) — satisfacen el umbral de MALICIA bajo analisis
Peirciano. Esto no es descuido ni mala configuracion. Cada accion requirio decisiones
tecnicas deliberadas por actores que entendian tanto el entorno objetivo como los
riesgos forenses.

---
*VIGIA — Haciendo la decepcion computacionalmente costosa desde 2026.*
*"Si un sistema reclama MALICIA sin explicarla con matematica exacta,
no es forense. Es adivinacion."*
