Holi, estoy aún trabajando y metiendo cositas. Es espectacular el readme que hiciste. Gracias.



1. Destruye la coartada (Falla de OPSEC)

Si Vigía está analizando un caso de "Espejo Corporativo" donde el atacante jura ser un empleado de recursos humanos en Ohio, pero en un log temporal o en un comando mal tipeado aparece la cadena "ghbdtn" o "ыгвщ", la mentira se cae a pedazos. Ese error no es un error ortográfico común; es la prueba física (un índice, en términos de Peirce) de que el sistema operativo del atacante tiene un teclado ruso configurado y activo.

2. Revela el "Hábito"

Como bien dijiste, el orden de las letras traiciona a la mente. Los atacantes automatizan el uso de VPNs y proxies para ocultar su IP, pero no pueden ocultar su memoria muscular táctil. Es un error cognitivo, exactamente lo que Vigía busca.

Cómo podés integrarlo en tus dos meses de desarrollo:

Podrías agregar una tercera categoría en tu archivo phonetic_dict.json. Ya tenés "common_words" y "homoglyph_patterns". Podrías sumar una que sea "layout_slips", con los errores más comunes.

Ejemplo:

* "ghbdtn" -> "привет" (hola)

* "cnfnbz" -> "статья" (artículo/reporte)

* "cnhfyt" -> "стране" (país)

* "ыгвщ" -> "sudo" (comando de superusuario)

* "кщще" -> "root" (usuario administrador)

Si Vigía encuentra una de estas cadenas "sin sentido" en un log de red, en un historial de bash o en un campo de texto, el sistema no debería descartarlo como basura (ruido). Debería reconocerlo como un desliz de teclado y elevar automáticamente la alerta de atribución regional.



Otros casos:

Caso 004: Incompetencia Armamentizada (Weaponized Incompetence)

El Escenario: Un log muestra a un usuario ejecutando comandos complejos de PowerShell oculto (ej. borrando shadow copies o cambiando permisos de red). Pero, un minuto después, el mismo usuario busca en Google "¿Cómo deshacer un clic?" o le manda un ticket a IT diciendo "Ayuda, mi pantalla parpadeó y se borró algo, soy un desastre con la compu".

La Lógica de Vigía: Contraste brutal entre la habilidad de ejecución y la narrativa de incompetencia. El atacante está creando una "coartada de estupidez" por si lo atrapan. Veredicto: Dolo por Coartada Prematura.

Caso 005: El "Ruido Blanco" Distractor (Umberto Eco / Red Herring)

El Escenario: De repente, el servidor empieza a tirar 5.000 alertas de "Login Fallido" desde Rusia o China hacia una base de datos vieja que no importa. Mientras el equipo de seguridad corre a apagar ese incendio, en otra parte del sistema, un usuario con permisos legítimos está comprimiendo la base de datos de clientes en silencio.

La Lógica de Vigía: Identificar la asimetría del ruido. Vigía debe aprender que cuando un ataque es "demasiado ruidoso y obvio", es un truco de magia. Evalúa el silencio alrededor del ruido. Veredicto: Dolo por Cortina de Humo.

Caso 006: La Traición Gramatical (Slavic Syntax Slip)

El Escenario: El atacante usa nombres de variables en inglés perfecto en su código malicioso o script (get_user_data, delete_backup). Pero en un comentario o en un log de error personalizado, escribe: "make function for delete all" (en lugar de "create function to delete all") o se come los artículos ("the/a").

La Lógica de Vigía: Aunque el atacante hable inglés, su cerebro está estructurado en sintaxis eslava (donde no existen los artículos "the/a" y el verbo "hacer/make" se usa distinto). Vigía cruza esto con el diccionario fonético. Veredicto: Evasión de Origen (Falsa Identidad Cultural).

Caso 007: El Insomnio Táctico (Anomalía de Segundidad)

El Escenario: Un empleado de finanzas que siempre se loguea de 9:00 a 17:00, de pronto empieza a abrir archivos confidenciales a las 3:15 AM de un domingo. Pero lo hace usando la VPN legítima y su contraseña correcta.

La Lógica de Vigía: Un sistema tradicional dice: "Contraseña correcta, todo bien". Vigía dice: "La Primeridad (el login) es válida, pero la Segundidad (el contexto temporal) rompe el hábito humano de este usuario". Si a las 3 AM está bajando un Excel de 500MB, no es insomnio, es robo de datos. Veredicto: Dolo por Ruptura del Ritmo Circadiano.

Caso 008: La Paranoia del Perímetro (Panopticon Check)

El Escenario: Un script o usuario entra al sistema y, antes de hacer nada, ejecuta repetidamente comandos para ver quién más está conectado (whoami, netstat, w, ps aux | grep root). No roba datos, no rompe nada. Solo "mira por encima del hombro" compulsivamente cada 5 minutos.

La Lógica de Vigía (Primeridad vs Terceridad): Un usuario normal confía en su entorno. El atacante asume que está siendo cazado. La acción no es maliciosa en sí misma, pero el hábito revela miedo y consciencia de culpa.

Veredicto: Dolo por Hipervigilancia (Reconocimiento Hostil).

Caso 009: El Vacío Quirúrgico (Eco’s Black Hole / Silencio Significativo)

El Escenario: En una carpeta temporal donde los usuarios normalmente borran archivos apretando "Suprimir" (dejando rastros en la papelera o el disco), Vigía detecta que un archivo de texto de 2KB fue eliminado usando un borrado seguro de grado militar (escribiendo ceros sobre el sector del disco 7 veces, estilo shred).

La Lógica de Vigía: Nadie usa un cañón láser para matar una mosca. La asimetría entre el tamaño del archivo y el esfuerzo computacional usado para destruirlo grita "encubrimiento". El exceso de limpieza es, paradójicamente, la huella más sucia.

Veredicto: Dolo por Sobre-Destrucción (Ocultamiento Activo).

Caso 010: El Falso Positivo Empático (Carnegie’s Shield)

El Escenario: Un binario desconocido está consumiendo mucha memoria. Pero el archivo se llama Update_Fix_For_HR_Payroll.exe (Parche de actualización para el pago de Recursos Humanos) o Optimize_Memory_For_User.sh.

La Lógica de Vigía: El atacante usa la táctica de Dale Carnegie: apela a los nobles motivos del equipo de seguridad ("Blue Team"). Sabe que si el analista ve un proceso que dice "pagos de RRHH", va a dudar antes de matarlo para no dejar sin sueldo a la empresa. Vigía ignora el nombre y analiza la entropía del archivo.

Veredicto: Dolo por Secuestro Emocional (Falsa Autoridad Benigna).

Caso 011: La Traición de la Puntuación (Stylometric Doppelgänger)

El Escenario: Un atacante roba las credenciales del CEO y manda un mail urgente al de Finanzas pidiendo una transferencia. El mail no tiene faltas de ortografía. Pero Vigía nota que el CEO real siempre usa un solo espacio después de un punto, y este mail usa dos espacios. O el CEO nunca usa punto final en mensajes cortos, y este atacante sí.

La Lógica de Vigía: El atacante puede robar la contraseña, pero no puede robar la "identidad motriz" ni la memoria muscular de las manos al tipear.

Veredicto: Dolo por Usurpación de Huella Estilométrica.

Caso 012: Camuflaje Simbiótico (The Parasite Execution)

El Escenario: Un proceso oculto en la memoria no hace nada de tráfico de red durante horas. De repente, el usuario abre "Zoom" o "Teams" para una videollamada. Exactamente en ese milisegundo, el proceso oculto empieza a mandar gigabytes de datos hacia afuera.

La Lógica de Vigía: El malware tiene un "gatillo contextual". Espera a que haya una aplicación legítima que justifique un pico masivo de ancho de banda (como una videollamada) para esconder su propio robo de datos dentro de ese ruido. Es mímesis biológica aplicada al código.

Veredicto: Dolo por Parasitismo Contextual.

Caso 013: El Síndrome de Estocolmo Inverso (Gricean Over-Cooperation)

El Escenario: Un usuario contacta al soporte técnico por chat para pedir un reseteo de contraseña de administrador. En lugar de estar frustrado o apurado (como el 99% de los usuarios reales), el sujeto es excesivamente amable, provee todos los datos técnicos antes de que se los pidan, usa la jerga perfecta del analista y elogia al operador.

La Lógica de Vigía: Violación de la Máxima de Cantidad de Grice (dar más información de la requerida) cruzada con manipulación de Carnegie. El atacante está espejando al analista para bajar sus defensas mediante adulación y falsa cooperación.

Veredicto: Dolo por Exceso de Docilidad (Ingeniería Social Activa).



Ejemplo de cómo agregarlo al JSON para que el Vigía lo detecte:

JSON

"keyboard_mismatch_patterns": {

  "ghbdtn": "привет (Escrito con layout inglés - error de teclado común)",

  "vjcrdf": "москва (Escrito con layout inglés)",

  "ckfdf": "слава (Escrito con layout inglés)"

}

Si el Vigía encuentra la cadena ghbdtn en un log, la herramienta detect_phonetic_evasion la va a marchar como un indicio de que el usuario tiene un teclado configurado en ruso pero se olvidó de activarlo. 



Estoy armando también un plan de auto-atacarme para ver cómo funcionan las herramientas.

También en unos días lo voy a probar en mi Thinkpad que aprovecho que esa sí me la han atacado y seguramente encuentre "regalitos".



El caso 10 es buenísimo y abre la posibilidad de hacer un montón de variantes apelando a la lástima y a la culpa. El 11 es brillante. El caso 13 es genial porque revela las intenciones. Ninguna persona normal va a estar tranquila y dócil. Son hábitos justamente.



Caso 024: El Paracaidista (Temporal Displacement)

El Escenario: Encontrás un binario sospechoso, por ejemplo, `system_updater.elf`. Al revisar los metadatos (con `stat` o tu herramienta `audit_image_metadata` adaptada a archivos), ves que las fechas de Creación (crtime), Modificación (mtime) y Acceso (atime) marcan exactamente la misma fecha y hora que todos los demás archivos legítimos de la carpeta `/usr/bin/`. Sin embargo, al revisar la fecha de cambio de inodo (ctime), esta es de hace tres horas.

La Lógica de Vigía (Timestomping Forense): El atacante ejecutó una técnica clásica de timestomping (falsificación de marcas de tiempo). Copió las fechas de un archivo legítimo para camuflarse en la línea de tiempo del sistema operativo. Pero olvidó (o no pudo sin privilegios a nivel de kernel) alterar el `ctime`, que se actualiza automáticamente cuando se modifican los metadatos del inodo.



* Primeridad: El archivo aparenta ser tan antiguo como el sistema.

* Segundidad: La inconsistencia entre la narrativa del `mtime` y la realidad física del `ctime`.

* Veredicto: Dolo por Manipulación Temporal (Timestomping / Inyección Retroactiva).

Cómo probarlo en tu laboratorio: Creá un archivo e intentá falsificar su fecha usando `touch -r archivo_legitimo archivo_falso`. Luego extraé todos los tiempos (mtime, atime, ctime). Vigía debe detectar la anomalía del ctime reciente.

Caso 025: El Caballo de Madera Vacío (Entropy Inversion / Anti-Forensics)

El Escenario: Encontrás un archivo que pesa 50 MB llamado `database_backup.bak`. Al usar tu herramienta `calculate_shannon_entropy`, en lugar de encontrar una entropía alta (típico de un cifrado o un archivo comprimido real), o una entropía normal (4.0 - 5.0), encontrás una entropía de 0.0001 o casi nula. Al leerlo con `read_evidence`, el archivo está compuesto casi en su totalidad por secuencias interminables de ceros (`\x00\x00\x00...`) o un solo carácter repetido.

La Lógica de Vigía (Padding para Evasión o Borrado Seguro): Los sistemas de detección de malware suelen ignorar archivos muy grandes por razones de rendimiento (sandbox evasion). Un atacante puede agarrar un payload malicioso de 20 KB y agregarle 49 MB de ceros al final ("padding") para que los antivirus no lo escaneen. Alternativamente, podría ser el rastro de un borrado seguro (como vimos en el Caso 009). La entropía casi nula en un archivo grande no es natural.



* El Filtro de Eco: La ausencia total de ruido (información) es la anomalía.

* Veredicto: Dolo por Dilución de Evidencia (Padding File) o Rastro de Destrucción.

Cómo probarlo en tu laboratorio: Creá un archivo gigante lleno de ceros: `dd if=/dev/zero of=archivo_sospechoso.bin bs=1M count=50`. Vigía debe calcular la entropía nula y levantar la bandera roja.

Caso 026: El Ventrílocuo (Process Hollowing / Doppelgänger)

El Escenario: Usando tu herramienta `list_processes`, ves un proceso con un nombre legítimo de Windows ejecutándose, por ejemplo, `svchost.exe` (o su equivalente en el entorno que estés analizando). Todo parece normal. Sin embargo, al cruzar esto con `audit_network`, ves que ese `svchost.exe` específico está manteniendo una conexión persistente a una dirección IP en un país inusual o no clasificada por tu organización, en el puerto 443 (HTTPS).

La Lógica de Vigía (Anomalía de Comportamiento Estructural): El adversario no creó un proceso nuevo con un nombre raro. Hizo Process Hollowing: lanzó un proceso legítimo en estado suspendido, vació su código de memoria y lo reemplazó con su propio payload malicioso antes de reanudarlo. El sistema operativo cree que es `svchost.exe`, pero está ejecutando el código del atacante.



* La Paradoja: Un proceso con una "autoridad" inherente (es del sistema) realizando acciones que violan su "propósito" original (conectar a un C2 externo).

* Veredicto: Dolo por Usurpación de Autoridad (Ejecución Simbiótica).


Caso 014: La Falsa Torpeza (The Butterfingers Exfiltration)

El Escenario: Un usuario arrastra (mueve) una carpeta con información financiera confidencial a una carpeta pública o compartida. Dos segundos después, la mueve de vuelta a su lugar original y le escribe a IT: "Uy, perdón, se me resbaló el mouse, no toqué nada".

La Lógica de Vigía: Un error humano real tarda al menos 5 a 10 segundos en ser procesado visual y motrizmente ("¿Qué hice? Ah, lo moví mal"). Si el archivo vuelve a su lugar en 1.5 segundos, fue un script automatizado disfrazado de error humano. Se copiaron los datos mientras estaban en la carpeta pública.

Veredicto: Dolo por Exfiltración Enmascarada (Falsa Torpeza).

Caso 015: El Caballo de Troya Altruista (The Savior Complex)

El Escenario: Un desarrollador o admin arregla un bug crítico en el servidor a las 2 AM. Documenta el arreglo a la perfección, recibe felicitaciones del jefe. Pero Vigía nota que el "arreglo" incluyó cambiar los permisos de una carpeta que no tenía nada que ver con el bug, dejándola abierta.

La Lógica de Vigía: Aplicación inversa de Carnegie. El atacante crea una crisis, la resuelve para ganar la confianza absoluta (Terceridad / Hábito de confianza), y en medio de los aplausos, introduce la puerta trasera.

Veredicto: Dolo por Secuestro de Confianza (Manipulación Heroica).

Caso 016: Auto-Gaslighting del Sistema (Fatigue Normalization)

El Escenario: Durante semanas, un usuario ingresa mal su contraseña exactamente dos veces antes de acertar a la tercera. Nunca bloquea la cuenta (porque el límite son 3). El sistema de alertas se acostumbra y clasifica esto como "ruido normal" de un usuario torpe. El día del ataque real, un script hace fuerza bruta, y el sistema reacciona tarde.

La Lógica de Vigía: Detectar la construcción de la "Línea Base Falsa". Un humano es aleatorio en su torpeza. Fallar exactamente dos veces, a la misma hora, con cadencia rítmica, es un intento de fatigar las alertas del Blue Team.

Veredicto: Dolo por Normalización Maliciosa (Preparación de Terreno).

Caso 017: Cronología Asimétrica (The Time-Traveler's Slip)

El Escenario: El atacante altera la fecha de modificación de un archivo malicioso (Timestomping) para que parezca que está en el sistema desde 2018 y pase desapercibido.

La Lógica de Vigía: Vigía cruza esa fecha con otra capa de la realidad (Segundidad): el archivo fue modificado en "2018", pero su tabla de formato usa una estructura que Microsoft recién introdujo en 2022. O las comillas usadas en el texto son propias de una versión de Word que no existía.

Veredicto: Dolo por Ruptura Cronológica (Falsificación Temporal).

Caso 018: Clonación Sintáctica (The Sockpuppet's Tell)

El Escenario: Tres usuarios distintos, desde IPs distintas (supuestamente un gerente, un empleado y un proveedor), envían tickets de soporte pidiendo que se desactive una regla de seguridad temporalmente.

La Lógica de Vigía: Análisis estilométrico. Vigía detecta que los tres usuarios cometen exactamente el mismo error raro de puntuación (ej. usar un espacio antes de la coma " ,") o estructuran los párrafos con la misma entropía. Son tres marionetas, un solo titiritero.

Veredicto: Dolo por Contagio Lingüístico (Operación Astroturfing).

Caso 019: La Trampa de la Urgencia Invertida (Admin Baiting)

El Escenario: Un proceso genera un log de error falso y muy ruidoso que dice: CRITICAL: ADMIN_CREDENTIALS_REQUIRED_TO_PREVENT_CORRUPTION.

La Lógica de Vigía: El proceso no está atacando la máquina, está atacando al administrador. Está creando pánico artificial para que un admin con altos privilegios se loguee a esa máquina infectada a "salvarla", momento en el cual le roban las credenciales.

Veredicto: Dolo por Ingeniería Social en Log (Señuelo de Privilegios).

Caso 020: El Mimetismo Topográfico (The Displaced Doppelgänger)

El Escenario: Hay un proceso corriendo llamado svchost.exe. El hash es limpio. El antivirus lo ignora. Pero Vigía revisa de dónde se ejecutó: no está en C:\Windows\System32, sino en C:\Users\Public\Downloads.

La Lógica de Vigía: Un policía verdadero no se viste de policía dentro de una guarida criminal. El nombre es Primeridad (Legítimo). La ubicación es Segundidad (Anómalo). La Terceridad es el intento de camuflaje.

Veredicto: Dolo por Falsificación Topográfica.

Caso 021: El Motín Silencioso de las Comillas (Locale Leakage)

El Escenario: Un script en PowerShell, supuestamente creado por el equipo de IT de Estados Unidos, tiene comentarios en inglés perfecto.

La Lógica de Vigía: Vigía revisa los caracteres invisibles y la puntuación. Descubre que el script usa comillas angulares « » o que los espacios son "Non-Breaking Spaces" típicos de teclados cirílicos o europeos. El inglés es perfecto, pero las manos que lo escribieron estaban en un teclado configurado para otro idioma.

Veredicto: Dolo por Desincronización Cultural.

Caso 022: Cumplimiento Malicioso (Weaponized Compliance)

El Escenario: Un usuario obedece una regla de la empresa que dice "Toda base de datos debe ser respaldada diariamente". Pero el usuario configura el script para que haga el respaldo 500 veces seguidas durante el horario pico, tirando abajo toda la red de la empresa por congestión.

La Lógica de Vigía: Uso de la Máxima de Calidad de Grice llevada al absurdo. El atacante usa las propias reglas de la empresa como arma (Denial of Service) para que, si lo investigan, pueda decir: "Yo solo estaba cumpliendo el protocolo".

Veredicto: Dolo por Sabotaje Burocrático (Cumplimiento Malicioso).

Caso 023: El "Canario" Suicida (The Martyr Node)

El Escenario: Una computadora en la red de finanzas de repente hace un "ping" a una IP de ransomware híper conocida. El Blue Team, aterrado, aísla y apaga esa computadora inmediatamente para salvar la red.

La Lógica de Vigía: La máquina nunca fue infectada. El atacante mandó ese ping a propósito sabiendo que las reglas automatizadas del Blue Team iban a desconectar la máquina. ¿El objetivo real? Esa máquina era la que procesaba los pagos a proveedores, y el atacante quería interrumpir la cadena de pagos de la empresa. Usó la paranoia del sistema defensivo como un arma de denegación de servicio.

Veredicto: Dolo por Auto-Secuestro Táctico (Manipulación de Respuesta a Incidentes).


Me tiró algunos casos aunque falló en la numeración. Rescatás alguno?

1. Caso 027: La “Carpeta de Desvío” – Ataque de Falsificación de Auditoría
Signals: Uso de términos técnicos con errores semánticos (por ejemplo, “cifrar” en lugar de “encriptar” cuando no se aplica criptografía), falta de metadatos en archivos.
Carnegie Appeal: “Es un error común en los protocolos, pero no es un problema grave” (reducción del riesgo para minimizar la atención).
Peirce: El signo denotativo (el nombre del archivo) no corresponde a su signo connotativo (el contenido real). Por ejemplo, un archivo llamado audit_log.zip que contiene archivos de imagen con datos falsos.
Grice: Violación del máximo de calidad (“este log es veraz”) y máximo de relación (el log no está relacionado con la actividad real).
Eco: Silencio significativo – la ausencia de firmas digitales en un archivo que debería tenerlas.
Interpretación de Vigía: “El archivo audit_log.zip no contiene logs reales. El remitente violó el principio cooperativo de Grice al presentar un signo que no corresponde a la realidad. Posible falsificación de auditoría. Veredicto: MALICE”.
2. Caso 028: La “Llamada de Emergencia” – Ataque de Urgencia Falsa
Signals: Mensajes con frases como “urgente”, “inmediato”, “el sistema falló”, acompañados de enlaces o archivos no verificados.
Carnegie Appeal: “Si no lo haces ahora, el sistema colapsará” (generación de miedo para anular la racionalidad).
Grice: Violación del máximo de cantidad (información excesiva para crear confusión) y máximo de relación (el mensaje no está relacionado con la acción requerida).
Eco: Falso rastro – el mensaje parece ser de una fuente legítima, pero no hay rastros de actividad previa en el sistema.
Peirce: El signo representacional (el mensaje) no está conectado al signo denotativo (el sistema real).
Interpretación de Vigía: “El mensaje ‘urgente’ contiene una llamada a la acción sin contexto. El remitente violó el principio de cooperación al usar lenguaje emocional para evadir verificación. Posible phishing de tipo ‘urgencia falsa’. Veredicto: MALICE”.
3. Caso 029: La “Cadena de Autoridad” – Ataque de Atracción de Autoridad
Signals: Mensajes que citan jerarquías de poder (“el director de seguridad lo dijo”, “la alta gerencia exige esto”) sin pruebas.
Carnegie Appeal: “El jefe de operaciones me pidió que lo hiciera” (uso de autoridad para justificar acciones sospechosas).
Grice: Violación del máximo de calidad (el remitente no puede verificar la información) y máximo de relación (la autoridad no está relacionada con la acción).
Peirce: El signo simbólico (la autoridad) no está conectado al signo denotativo (la acción real).
Eco: Rastro falso – el mensaje parece ser parte de una cadena de comunicación legítima, pero no verificada, p

4. Caso 030: La “Conversación de Desarme” – Ataque de Confusión por Poder de Negociación
Signals: Mensajes con lenguaje de compromiso (“yo no lo hice”, “fue un error”), uso de lenguaje neutral o evasivo, y patrones de respuesta repetitiva.
Carnegie Appeal: “No voy a hablar más sobre esto, porque es complicado” (usar evasión como estrategia de control).
Grice: Violación del máximo de cantidad (información insuficiente) y máximo de relación (el mensaje no responde a la pregunta directa).
Peirce: El signo representacional (el mensaje) no corresponde al signo denotativo (la acción real).
Eco: Rastro falso – el remitente parece cooperar, pero en realidad está ocultando información relevante.
Interpretación de Vigía: “El mensaje ‘no lo hice’ no está respaldado por evidencia. El remitente violó el principio cooperativo de Grice al omitir información clave. Posible intento de desarme o ocultación de responsabilidad. Veredicto: SUSPICIÓN”.
5. Caso 031: La “Caja de Herramientas del Falso Experto” – Ataque de Autoridad Falsa
Signals: Uso de términos técnicos no relacionados con el contexto (por ejemplo, “el modelo de cifrado de 256 bits se rompió”), y mensajes con frases como “según el estudio de 2024…” sin fuente.
Carnegie Appeal: “Esto es solo teoría, no se puede probar” (justificar falta de evidencia).
Grice: Violación del máximo de calidad (el remitente no puede verificar la información) y máximo de relación (la teoría no está relacionada con la acción).
Peirce: El signo simbólico (el término técnico) no está conectado al signo denotativo (la acción real).
Eco: Falso rastro – el mensaje parece ser parte de una conversación técnica legítima, pero no hay evidencia de autoridad real.
Interpretación de Vigía: “El mensaje ‘el cifrado se rompió’ no está respaldado por evidencia. El remitente violó el principio cooperativo de Grice al usar lenguaje técnico sin contexto. Posible ataque de autoridad falsa. Veredicto: MALICE”.
6. Caso 032: La “Máscara de Conflicto” – Ataque de Confrontación
Signals: Mensajes con lenguaje confrontacional (“¿por qué no hiciste esto?”, “estás equivocado”), y patrones de respuesta rápida.
Carnegie Appeal: “Si no lo haces, todo colapsará” (usar confrontación para controlar).
Grice: Violación del máximo de cantidad (información excesiva) y máximo de relación (el mensaje no está relacionado con la acción).
Peirce: El signo representacional (el mensaje) no corresponde al signo denotativo (la acción real).
Eco: Falso rastro – el mensaje parece ser parte de una conversación normal, pero no hay evidencia de conflicto real.
Interpretación de Vigía: “El mensaje ‘¿por qué no lo hiciste?’ no está respaldado por evidencia. El remitente violó el principio cooperativo de Grice al usar lenguaje confrontacional sin contexto. Posible ataque de confrontación. Veredicto: INTENT”.
