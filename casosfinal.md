Caso 083: El "Sacrificio del Peón" – Carnegie: Admisión de Culpa Instrumental
Signals: Un analista senior envía un mail urgente: "Me acabo de dar cuenta de que por error dejé mi sesión de SSH abierta en un servidor público durante 4 horas. Soy un irresponsable, por favor revóquenme los accesos hasta que termine la auditoría de mi cuenta".

Carnegie Appeal: "Admita sus errores rápida y enfáticamente". El atacante se auto-denuncia por una falta de política (dejar sesión abierta) para ganar una coartada de "honestidad extrema".

Peirce: Segundidad. Mientras el equipo de seguridad "audita" su cuenta con benevolencia, una tarea programada (cron job) instalada 5 minutos antes de la denuncia empieza a exfiltrar datos bajo la identidad de un servicio de sistema.

Grice: Violación del máximo de calidad. La denuncia es real, pero el motivo es falso: no es un error, es el pretexto para que nadie sospeche de la actividad posterior del sistema.

Interpretación de VIGÍA: "Detección de sobre-incriminación estratégica. El usuario busca saturar el sesgo de confianza del auditor. El timing entre la confesión y la creación del cron job indica una maniobra de distracción. Veredicto: MALICE (97%)".

Caso 084: El "Cebo del Falso Layman" – Inversión de Autoridad
Signals: Un ticket de soporte técnico: "Hola, soy de administración. No sé qué toqué, pero me sale una pantalla negra con letras verdes y no me deja entrar al Excel. Adjunto captura". La captura es un tty de Linux con un exploit de escalada de privilegios (dirty pipe) a medio ejecutar.

Carnegie Appeal: "Haga que la otra persona se sienta importante" (pedir ayuda desde la ignorancia para que el técnico baje la guardia).

Eco: Falso rastro. El atacante simula ser un usuario analfabeto digital para que el técnico, al intentar "arreglarlo" remotamente, ejecute inadvertidamente el último paso del exploit.

Peirce: Terceridad. La ley del azar no genera un exploit de kernel por "tocar cualquier cosa".

Interpretación de VIGÍA: "Detección de teatro forense. La probabilidad de que un usuario no técnico llegue accidentalmente a un estado de ejecución de exploit es nula. El mensaje busca inducir una acción de administrador sobre un proceso malicioso. Veredicto: MALICE (99%)".

Caso 085: La "Mise en Place" Alterada – Sabotaje de Entorno
Signals: Un script de despliegue (deploy.sh) es modificado. El cambio es mínimo: se agregó una sola línea que redirige los errores (stderr) a /dev/null. El mensaje de commit dice: "Limpiando logs redundantes para mejorar la legibilidad".

Grice: Violación del máximo de cantidad (omisión de información crítica).

Peirce: Segundidad (Fricción). Al silenciar los errores, el atacante oculta que un módulo de autenticación está fallando y cayendo en modo "permisivo" (fail-open).

Eco: El cambio parece una mejora de "limpieza", pero es una ceguera inducida.

Interpretación de VIGÍA: "Detección de opacidad deliberada en el flujo de errores. La 'limpieza' es un signo para ocultar el fallo de un control de seguridad crítico. Veredicto: INTENT (94%)".

Caso 086: El "Doble Salto de Layout" – Peirce: Index (Física del Error)
Signals: En una consola se registra: кщще, luego un borrado rápido, y después sudo.

Peirce: Primeridad (Rastro físico). кщще es root en el teclado ruso. El hecho de que el atacante se haya dado cuenta y haya borrado inmediatamente para poner sudo indica que es un operador humano consciente de su OPSEC, pero traicionado por su memoria muscular inicial.

Eco: El uso posterior de sudo (comando más común en entornos modernos) es un intento de normalización tras el error que delató su layout nativo.

Interpretación de VIGÍA: "Detección de Keyboard Slip (Layout ЙЦУКЕН). La corrección inmediata indica un operador con alta disciplina de ocultamiento que falló en la fase de inicialización. Atribución lingüística: Ruso. Veredicto: MALICE (98%)".

Caso 087: El "Síndrome de Estocolmo Inverso" – Cooperación Agresiva
Signals: Durante una respuesta a incidentes, un empleado externo contratado para seguridad empieza a "ayudar" de más: "Chicos, encontré esta IP de Ucrania atacándonos. Ya la bloqueé y estoy borrando los logs de acceso de esa región para que no nos saturen el SIEM".

Carnegie Appeal: "Interésese genuinamente en los demás" (ayudar a aliviar la carga de trabajo del equipo).

Grice: Violación del máximo de relación. Borrar logs nunca es parte de la solución de un incidente.

Peirce: Terceridad. La "ayuda" es el método para destruir la evidencia del origen real del ataque, usando una IP de Ucrania como chivo expiatorio (Red Herring).

Interpretación de VIGÍA: "Detección de asistencia obstructiva. El colaborador usa la urgencia del incidente para legitimar la destrucción de trazas forenses. Veredicto: MALICE (96%)".

Caso 088: El "Calco Semántico del Intruso" – Grice: Máximo de Manera
Signals: Un ticket interno dice: "I need to check the state of the country". El servidor es de una empresa de servicios eléctricos.

Peirce: Terceridad. En ruso, la palabra para "país" (стране - strane) se usa a menudo como sinónimo de "lado" o "área" en contextos informales. Un hablante nativo de inglés diría "area" o "section".

Eco: El atacante tiene un inglés fluido, pero su estructura de pensamiento (calco semántico) delata su origen.

Interpretación de VIGÍA: "Detección de calco lingüístico subyacente. La elección de términos no coincide con el contexto técnico-geográfico del sistema, pero sí con una traducción directa del ruso. Veredicto: INTENT (91%)".

Caso 089: La "Huella de la Perfección" – Jitter Sintético
Signals: Una sesión de administración remota dura 45 minutos. Los tiempos entre comandos tienen una varianza de exactamente 0.05 segundos en el 90% de la sesión.

Peirce: Terceridad (Ley). Los humanos no piensan con cronómetro. Una varianza tan estable es ley de máquina intentando simular el ritmo de un humano (Anti-Forensics).

Grice: N/A.

Interpretación de VIGÍA: "Detección de aleatoriedad artificial. El patrón temporal carece de la entropía cognitiva propia de un operador humano analizando resultados. Veredicto: INTENT (95%)".

Caso 090: El "Anacronismo de la Herramienta" – Falla de Terceridad
Signals: Se detecta el uso de psexec versión 1.94 en un servidor con Windows 2025. Esa versión tiene más de una década y es conocida por ser detectada por cualquier EDR moderno.

Peirce: Segundidad (Contradicción). Un atacante sofisticado no usaría una herramienta tan ruidosa y vieja en un sistema tan nuevo, a menos que...

Eco: Falso rastro. El atacante usa una herramienta "de manual" para que el analista piense que se trata de un "script-kiddie" y no busque el rootkit de nivel de kernel que se instaló silenciosamente por otra vía.

Interpretación de VIGÍA: "Detección de teatro de competencia técnica inferior. El uso de herramientas ruidosas y obsoletas es un signo de distracción para desviar la atención de una persistencia sofisticada. Veredicto: MALICE (98%)".

Caso 091: La "Disonancia del Motivo Noble" – Carnegie: Apelación a la Moral
Signals: Un mensaje de Slack: "Che, vi que dejaste tu contraseña en un post-it en la cámara de la reunión. La anoté y la borré de la captura de pantalla para que nadie te denuncie a seguridad. Te la paso por acá para que no te la olvides: [Link_Malicioso]".

Carnegie Appeal: "Haga que la otra persona se sienta feliz de hacer lo que usted sugiere" (salvarla de una sanción).

Grice: Violación del máximo de calidad. No hay evidencia de tal post-it en los logs de la cámara.

Peirce: Terceridad. La "protección" del compañero es el vehículo para el robo de credenciales.

Interpretación de VIGÍA: "Uso de vulnerabilidad social y falsa solidaridad para inducir una acción de riesgo. El motivo noble es el envoltorio de un ataque de phishing interno. Veredicto: MALICE (95%)".

Caso 092: El "Efecto de Verdad por Saturación" – Grice: Máximo de Cantidad
Signals: Ante una pregunta del SOC sobre un proceso extraño, el administrador envía un reporte de 40 páginas con gráficos de uso de CPU, temperatura de los discos, estado de la red en 10 ciudades y bios de los técnicos de guardia.

Grice: Violación del máximo de cantidad. Provee información masiva e irrelevante para que el analista se canse y no llegue a la página 39, donde se menciona "un pequeño ajuste de permisos sin importancia".

Carnegie: "Sea caluroso en su aprobación" (mostrando lo "buen profesional" que es al ser tan detallista).

Interpretación de VIGÍA: "Detección de inundación informativa (Semantic Flooding). El volumen de datos busca anular la capacidad crítica del receptor mediante la fatiga. Veredicto: INTENT (93%)".

Caso 093: El "Deepfake de Estilo" – Mimesis Algorítmica
Signals: Commits de código que imitan a la perfección el estilo del Arquitecto Jefe (espaciado, nombres de variables, incluso los mismos errores gramaticales en los comentarios). Pero los metadatos muestran que se subieron vía una clave API genérica a las 4:00 AM, mientras el log del arquitecto dice que estaba desconectado.

Peirce: Terceridad (Hábito). El hábito es demasiado perfecto. Carece de la variabilidad orgánica del pensamiento humano.

Eco: El estilo es un signo fabricado (Doble).

Interpretación de VIGÍA: "Detección de mimesis estilística artificial. La consistencia es estadística, no biográfica. El atacante usó una IA para redactar código que 'parezca' legítimo. Veredicto: MALICE (98%)".

Caso 094: El "Agujero Negro Burocrático" – Inundación por Cumplimiento
Signals: Ante una auditoría por una fuga de datos, el responsable entrega 200 PDFs de "Reportes de Integridad". VIGÍA detecta que todos los metadatos de creación de esos 200 archivos tienen una diferencia exacta de 1.2 segundos entre sí.

Grice: Violación del máximo de cantidad. Provee información masiva para ocultar la falta de la información real.

Peirce: Segundidad (Index). La física de la creación de los archivos delata un script de generación masiva ("Fábrica de Consistencia"), no una gestión humana de meses.

Interpretación de VIGÍA: "Detección de entrelazamiento documental. La narrativa de 'cumplimiento histórico' es una fabricación temporal de último minuto. Veredicto: MALICE (99%)".

Caso 095: La "Sombra Fonética" – Calco del Pensamiento
Signals: Un ticket de soporte dice: "I'll make the revision of the server". En la terminal, el usuario intenta ejecutar grep -R (recursivo) de una forma que solo aparece en manuales traducidos del chino (usar -R en lugar del -r estándar de un nativo).

Peirce: Terceridad. El uso de "revision" es un calco semántico de "revisión/auditoría" que delata que el atacante está traduciendo mentalmente de su idioma nativo.

Grice: Violación del máximo de relación entre el lenguaje natural y el contexto técnico.

Interpretación de VIGÍA: "Detección de calco semántico y sintaxis de manual. El atacante opera bajo una máscara de fluidez, pero su 'pensamiento técnico' delata un origen idiomático externo. Veredicto: INTENT (92%)".

Caso 096: La "Entropía de Pánico" – Sabotaje de MFA
Signals: Durante un ataque de fuerza bruta, el "Administrador" recibe 50 alertas falsas de Telegram simultáneas. El administrador escribe en el chat: "Estoy desbordado, desactiven el MFA 5 minutos para que pueda entrar rápido y bloquear las IPs".

Carnegie: Generar compasión y urgencia ante el estrés para forzar una concesión.

Grice: Violación del máximo de relación. Desactivar el MFA no soluciona un ataque de red, lo facilita.

Interpretación de VIGÍA: "Detección de ingeniería social por saturación sensorial. La solicitud de degradar la seguridad es la meta del ataque, no la solución. Veredicto: MALICE (97%)".

Caso 097: La "Falsa Misericordia" – Carnegie: El Salvador Secreto
Signals: Un analista de seguridad le escribe a un compañero: "Che, te salvé la vida. Vi que dejaste tu sesión abierta y te la cerré yo para que no te sancionen. No digas nada". VIGÍA detecta que, 10 segundos antes de cerrar la sesión, ese analista instaló una web shell oculta.

Carnegie Appeal: "Sea caluroso en su aprobación y generoso en sus elogios" (en este caso, en su "ayuda" secreta).

Peirce: Terceridad. La "lealtad entre pares" es el signo usado para evitar que el compañero audite su propio cierre de sesión.

Interpretación de VIGÍA: "Uso de reciprocidad social para encubrir la implantación de persistencia. El motivo noble es una barrera contra la sospecha. Veredicto: MALICE (96%)".

Caso 098: El "Anacronismo de Plataforma" – Eco: Signo Desubicado
Signals: Un usuario en un servidor Linux ultra-moderno de repente tipea ipconfig /all o route print. Al fallar, corrige inmediatamente a ip addr.

Peirce: Segundidad. El atacante "piensa en Windows" pero opera en Linux. Es un error de contaminación de entorno.

Eco: El rastro técnico es un anacronismo físico de la mente del operador.

Interpretación de VIGÍA: "Detección de contaminación de memoria muscular multiplataforma. El operador está traduciendo comandos de su SO nativo a ciegas. Veredicto: INTENT (90%)".

Caso 099: El "Troyano Emocional" – Eco: El Tabú de la Muerte
Signals: Mail de "Recursos Humanos": "Debido al fallecimiento de un colega, estamos recolectando fondos. Revisen el PDF adjunto para las donaciones". El PDF tiene un script que roba tokens de sesión de navegador.

Carnegie: Apelar a la simpatía y al dolor ajeno para anular el juicio crítico.

Eco: El signo de la "muerte" es la barrera semántica definitiva; nadie se atreve a cuestionar la seguridad de un pedido de condolencias.

Interpretación de VIGÍA: "Detección de secuestro de narrativa emocional. El atacante usa un tabú social para anular el protocolo de desconfianza técnica. Veredicto: MALICE (99%)".

Caso 100: El "Fantasma en la Máquina" – Perfección No-Humana
Signals: Una cuenta de servicio realiza mantenimiento. El log es perfecto: intervalos de tiempo exactos, comandos en orden de manual, cero errores, cero reintentos.

Peirce: Terceridad. La perfección es el signo de la falta de humanidad. Un experto real tiene "ruido" (un ls de más, una pausa para pensar).

Interpretación de VIGÍA: "Detección de anomalía por falta de entropía. El proceso es demasiado 'limpio' para ser un operador humano; es un script de exfiltración disfrazado de mantenimiento. Veredicto: INTENT (95%)".

Caso 101: El "Denunciante de Humo" – Trap Reporting
Signals: Un usuario reporta: "Creo que me hackearon, veo archivos raros en mi carpeta". El equipo de seguridad (con privilegios de Admin) entra a mirar. El usuario es el atacante: el archivo "raro" es un exploit que se activa al ser abierto por el visor del administrador.

Carnegie: "Haga que la otra persona se sienta importante" (pedir ayuda al "experto").

Eco: El reporte es un cebo semántico diseñado para elevar privilegios mediante el uso del personal de seguridad.

Interpretación de VIGÍA: "Detección de ataque de inversión de roles (Trap Reporting). El denunciante es el vector y la denuncia es el disparador. Veredicto: MALICE (98%)".

Caso 102: El "Espejo del Soporte" – Mimesis Lingüística
Signals: Un atacante interactúa con un técnico. Copia y pega las muletillas exactas del técnico ("Entiendo su frustración", "Estamos trabajando en ello") para pedir un "reset de contraseña de emergencia" de una cuenta de alto nivel.

Carnegie: El efecto espejo (mirroring) para generar una falsa sensación de pertenencia y confianza inmediata.

Peirce: Terceridad (Mimesis).

Interpretación de VIGÍA: "Detección de mimetismo lingüístico táctico. El atacante usa el 'lenguaje de la casa' para anular la alerta del operador. Veredicto: MALICE (94%)".


Caso 103: El "Cebo de la Vulnerabilidad Autoinfligida" – Carnegie: Admisión Táctica
Signals: Un administrador de sistemas reporta: "Dejé un puerto abierto por error mientras probaba un nuevo microservicio. Soy un desastre, por favor ciérrenlo y verifiquen si alguien entró". Mientras el SOC se enfoca en ese puerto (el señuelo), el atacante usa una credencial de servicio legítima para mover datos lateralmente.

Carnegie Appeal: "Admita sus errores rápida y enfáticamente". El atacante se sobre-incrimina en una negligencia menor para obtener una "carta de honestidad" y desviar la mirada del equipo de respuesta hacia una zona controlada.

Peirce: Segundidad. El rastro físico (el puerto abierto) es el signo usado para ocultar el rastro real (la sesión de servicio anómala).

Interpretación de VIGÍA: "Detección de sobre-incriminación estratégica. El reporte voluntario actúa como una contramedida de sospecha para ocultar un movimiento lateral concurrente. Veredicto: MALICE (98%)".

Caso 104: El "Error de Layout en el Comentario" – Peirce: Index (Física del Error)
Signals: Un script de mantenimiento en producción tiene un comentario nuevo: # TODO: arreglar el script cnfnbz.py.

Peirce: Primeridad (Index). La palabra cnfnbz no tiene sentido en español ni en inglés. Al mapear el teclado, cnfnbz es el resultado de escribir статья (artículo/reporte) con el layout ruso activo.

Eco: Falso rastro. El atacante intentó mimetizarse escribiendo comentarios de "desarrollador", pero su memoria muscular lo traicionó en la cadena de texto no ejecutable.

Interpretación de VIGÍA: "Detección de desliz de teclado (Keyboard Slip) en comentarios de código. La cadena 'cnfnbz' delata la configuración de hardware nativa del operador. Veredicto: MALICE (97%)".

Caso 105: La "Disonancia del Ritmo de Procesamiento" – Terceridad (Ley Matemática)
Signals: Una sesión de administración remota ejecuta una serie de tareas complejas (análisis de logs, búsqueda de archivos, edición de configs). Los intervalos entre comandos son de exactamente 1.5, 1.5 y 1.6 segundos.

Peirce: Terceridad. La ley del azar dice que un humano, ante tareas de distinta complejidad cognitiva, tiene tiempos de respuesta variables. Una varianza tan baja (Jitter < 0.1s) es ley de máquina simulando ser humana.

Grice: Violación del máximo de manera. La ejecución es "demasiado ordenada" para la naturaleza del problema planteado.

Interpretación de VIGÍA: "Detección de entropía temporal nula. El patrón de ejecución es incompatible con la carga cognitiva de las tareas realizadas. Automatización detectada. Veredicto: INTENT (96%)".

Caso 106: La "Mimesis del Error Administrativo" – Grice: Máximo de Cantidad
Signals: Una factura en PDF enviada a finanzas tiene una "falla de impresión" que cubre justo el CBU/IBAN original. El remitente envía un mail: "Uy, salió mal el PDF, te paso el número de cuenta por acá para que no te trabes con el pago".

Grice: Violación del máximo de cantidad (información incompleta en el canal oficial) y violación del máximo de manera (uso de un canal informal para corregir un dato crítico).

Carnegie: "Haga que la otra persona se sienta feliz de hacer lo que usted sugiere" (facilitar el pago rápido).

Interpretación de VIGÍA: "Detección de sabotaje de integridad documental. El error de impresión es un signo fabricado para forzar el uso de un canal no auditable. Veredicto: MALICE (94%)".

Caso 107: El "Anacronismo de la Firma Digital" – Eco: Signo Desfasado
Signals: Un controlador de dominio recibe una actualización de política de grupo firmada por un certificado que, aunque válido, utiliza un algoritmo (SHA-1) que la empresa prohibió hace 4 años por debilidad criptográfica.

Eco: El signo de autoridad (el certificado) es un anacronismo. Un administrador legítimo no tendría acceso ni motivo para usar una infraestructura de firma obsoleta.

Peirce: Segundidad. El objeto técnico contradice la ley de cumplimiento actual.

Interpretación de VIGÍA: "Detección de anacronismo criptográfico. El uso de protocolos obsoletos sugiere la reutilización de herramientas de ataque antiguas o una persistencia latente de larga data. Veredicto: INTENT (92%)".

Caso 108: La "Inversión de la Carga de Prueba" – Carnegie: Desafío de Autoridad
Signals: Un analista del SOC contacta a un usuario por una actividad sospechosa. El usuario (el atacante) responde: "¿Por qué me preguntas esto? ¿Acaso no confías en mi trabajo? Ya hablé con el gerente sobre el exceso de control, me estás haciendo perder tiempo valioso de producción".

Carnegie Appeal: Inversión de la culpa. El atacante usa la intimidación y la apelación a la eficiencia para que el analista se sienta inseguro y detenga la investigación.

Grice: Violación del máximo de relación. La queja sobre el "tiempo perdido" no responde a la pregunta técnica sobre el log.

Interpretación de VIGÍA: "Detección de agresión defensiva y manipulación jerárquica. El usuario busca anular el proceso forense mediante la creación de fricción interpersonal. Veredicto: MALICE (95%)".

Caso 109: El "Silencio Estadístico en el Log de Red" – Grice: Máximo de Cantidad
Signals: Durante un pico de tráfico de salida masivo, el log de red muestra "Conexión establecida" y "Conexión finalizada", pero el campo de bytes_transferred es 0 o está vacío, a pesar de que el router reporta saturación de banda.

Grice: Violación del máximo de cantidad (omisión de la magnitud de la acción).

Peirce: Segundidad. El silencio del log contradice la realidad física del ancho de banda agotado.

Eco: El "vacío" es el mensaje. El atacante logró comprometer el servicio de logging para que registre el evento pero no la escala del robo.

Interpretación de VIGÍA: "Detección de lagunas informativas selectivas (Data Gapping). La discrepancia entre el sensor de red y el log de auditoría confirma manipulación de trazas. Veredicto: MALICE (99%)".

Caso 110: La "Paradoja del Auditor Externo" – El Espejo Final
Signals: Se recibe un archivo audit_report_final.json que contiene exactamente los mismos hashes y estructuras que VIGÍA genera, pero con un veredicto de NOISE para una IP que VIGÍA marcó como MALICE hace una hora.

Peirce: Terceridad. El atacante está intentando usar la propia "ley" de VIGÍA (su estructura de reporte) para anular un hallazgo previo. Es una colisión semántica dirigida contra el motor.

Eco: Mimesis total del observador.

Interpretación de VIGÍA: "Detección de colisión semiótica dirigida. Un actor externo está intentando inyectar un contra-veredicto utilizando el formato canónico del sistema. Veredicto: MALICE (100%)".

Caso 111: El "Falso Rastro de Incompetencia Senior" – Eco: Teatro Forense
Signals: Un atacante deja rastros de un exploit muy conocido y fácil de detectar (como un escaneo de nmap ruidoso). Al mismo tiempo, el análisis de memoria revela que se cargó un driver de kernel personalizado que solo alguien con conocimientos profundos de C++ podría escribir.

Eco: El rastro de "aficionado" es una máscara. El atacante quiere que el analista crea que se trata de un "script-kiddie" y deje de buscar.

Peirce: Segundidad (Fricción). La baja calidad del ataque superficial contradice la alta calidad del ataque profundo.

Interpretación de VIGÍA: "Detección de estratificación de competencia técnica. El rastro ruidoso es un señuelo para ocultar una operación de alta persistencia. Veredicto: MALICE (98%)".

Caso 112: La "Sincronización del Pánico Semántico" – Grice: Máximo de Manera
Signals: En medio de un incidente real de red, aparecen 20 tickets de soporte de cuentas distintas diciendo: "No puedo entrar al mail", "El servidor está caído", "¿Nos hackearon?". Ninguna de esas cuentas tiene problemas reales de acceso al mail según los logs de O365.

Grice: Violación del máximo de manera (caos informativo deliberado).

Carnegie: "Haga que la otra persona se sienta feliz de hacer lo que usted sugiere" (en este caso, unirse al pánico para saturar al equipo de seguridad).

Interpretación de VIGÍA: "Detección de ataque de denegación de servicio cognitivo (Cognitive DoS). El flujo coordinado de reportes falsos busca paralizar la capacidad de triaje del SOC durante un ataque real. Veredicto: MALICE (97%)".
