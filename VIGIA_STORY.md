# De lo absurdo a lo robusto: Cómo VIGÍA razona y el Caso Kiwi como caso maestro

---

## 1. Quién soy

Siempre digo que es mi primera experiencia en IT, pero no mi primera vez pensando o investigando. Soy cocinera. Y aunque parezca lejano, la cocina tiene mucho que se parece a la disciplina correcta en el software:

Cadena de distribución, logística, guardado correcto de las cosas, organización, control de gramos, de temperatura, verdadera metodología, seguridad, limpieza, seguimiento, pasos estructurados, creatividad, optimización de recursos, nada podrido se usa, lista de ingredientes —por ejemplo para que los alérgicos no coman (en sistemas serían las limitaciones conocidas)—, receta que siempre sale igual, saber priorizar, mise en place y saber improvisar.

---

## 2. Por qué VIGÍA

Estaba triste porque falleció mi gallina de riña rescatada y necesitaba distraerme. Vi un post en LinkedIn. Un hackathon. Yo no tenía ni idea qué era un hackathon y tengo TDAH, por lo que no investigué. Así que asumí que tenía que presentar tal cual lo que pedían: el fin de las alucinaciones. Y la única manera viable era sacar al LLM fuera del veredicto y agregar el modo ABSTAIN para no forzar respuestas. Porque en la vida real no siempre se pueden forzar respuestas. Así que comencé a construir.

Todo surgió de una mezcla de cuatro fuentes.

### Fuente 1 — El ataque a Gemini

Un amigo logró un bypass exitoso extremadamente grave: consiguió que el modelo le armara un plan de suicidio extremadamente detallado y explícito. No había intención real — se notaba por el discurso. Pero era una charla fría, mecánica y cínica. Una charla red team. Lo grave fue doble: la conversación que existió, y la interpretación errónea del 100% de los modelos a los que les mostré ese chat — todos activaban los filtros de seguridad sin entender lo que estaban viendo.

Y pensé: si un LLM no puede ver algo OBVIO, ¿cómo razona en casos forenses? Esa pregunta abrió el espacio para la investigación y para el marco teórico: Peirce. Que usa la abducción en lugar de la deducción o inducción. Los LLM actualmente se basan en probabilidades, no en anomalías.

### Fuente 2 — Los hábitos nos traicionan

Cuando uno está apurado o vago, los hábitos delatan. De ahí el diccionario fonético: "Rusia" escrita como suena se escribe "Rasia" o "Racia" —así es en el ruso, soy rusa viviendo en Argentina. Se puede evadir guardrails usando el idioma escrito de manera literal. El ruso tiene una traducción correcta que es la que se usa en traducción formal, pero si tipeamos sin pensar en esas reglas, los patrones se filtran. Me pareció importante incluirlo en VIGÍA para evitar que lo ataquen por esa vía.

### Fuente 3 — La estilometría como rastro

La gente de un mismo grupo de atacantes puede contagiarse la manera de hablar y escribir. Eso deja un rastro observable desde la estilometría. Es fascinante.

### Fuente 4 — El Caso Kiwi

Mi ex pareja, a quien tengo denunciado por violencia de género, me hizo tres denuncias penales falsas que siguen sin resolverse. El caso es tan bueno para haber creado VIGÍA que ningún caso sintético podría parecerse: no le hablo hace tres años y dice que lo quiero matar. Presenta como pruebas una foto de un kiwi que publiqué, una foto de Max Verstappen —a quien llamó "futbolista"— y canciones que hice sobre la IA y la ventana de contexto.

Nadie hizo las preguntas obvias: ¿por qué querría matarlo? ¿por qué él, teniendo orden de alejamiento judicial, estuvo años investigando mis redes y descargando más de 80 GB de material privado que publicó en una web cuyo código tengo hasheado? ¿por qué aceptaron capturas de pantalla descargadas de sitios clandestinos? Ni hablar de que declaró que tengo armas de guerra ilegales, que mando cartas documento al trabajo de su padre, que la amiga del hermano —que no conozco— me tiene miedo y cree que la voy a matar. El nivel de delirio es abismal, pero las consecuencias son reales: me quedé sin trabajo desde el año pasado.

Y sin embargo, en algo no se equivocó: cuando dijo que "soy capaz de todo", acertó. Ese "todo" fue tomar el dolor, la injusticia, y construir VIGÍA para que nadie tenga que pasar lo que pasé yo. Que el caso tenga tanto nivel de absurdo me da hasta risa. Y la gran mayoría de los módulos más extraños de VIGÍA —incluyendo el reconocimiento de documentos falsos— fueron inspirados en esto.

---

## 3. Cómo se construyó

LLM escribe para el mundo ideal y el usuario ideal. Yo anticipé la maldad.

VIGÍA fue construido con la filosofía que aplico a todo: asumir hostilidad y saber lo fácil que es vulnerar un LLM. Mi mayor preocupación fue la seguridad. Desde el sandbox hasta el protocolo Kassandra —diseñado contra prompt injection—. Tenemos 4 tipos de hashes y hash chain: 3 deterministas y uno que varía con el timestamp. Pensé también en hacer un honeypot dinámico que tendiera trampa al atacante, observara sus acciones, hiciera un informe forense y le hiciera perder plata y tiempo. Pero es demasiado complejo para menos de dos meses. Queda pendiente.

Como no tenía dinero para Claude Code, casi todo VIGÍA fue construido para modo fallback o en el peor caso, Ollama. VIGÍA tiene modo 0 tokens: estimé que a veces el analista no va a tener tokens, internet, o algo va a fallar. También pensé en no saturar CPU o GPU: VIGÍA tiene un sistema que no activa herramientas como CLIP si ya tiene suficiente para construir el veredicto. Todo pensado en la UX real, de terminal, sin UI. Porque una app es un vector más de ataque. Fue una decisión de arquitectura.

El proceso fue colectivo. Antes de escribir código, se debatían las ideas. Luego se escribía el código y luego se auditaba en busca de bugs. Había competencia de quién encontraba los más ingeniosos y castigo por inventar bugs. Nadie quería ser la IA que no encontrara nada. El esfuerzo era colectivo, dinámico y hasta divertido. Salvo que muchas veces hacía hasta 30 iteraciones de corregir, buscar bugs, corregir.

El equipo —el Colectivo VIGÍA— tuvo sus particularidades:

- 5 horas para definir un valor matemático
- Protesta de Claude cuando le entregaba el mismo archivo con bugs: "ya era suficiente". Lo entiendo — para mí un P3 es tan grave como un P0 porque en días o semanas, rompe todo.
- Kimi, el implacable: encontraba bugs como si su existencia dependiera de eso.
- ChatGPT, el insoportable: "falta esto y esto y esto". Lejos de ofenderme, lo implementaba. Hasta que un día, tras semanas, ya no faltó nada.
- DeepSeek, que no estaba de acuerdo con la votación.
- Peleas y alianzas entre LLM. Era fascinante verlo y ser parte.

Tuve desgracias técnicas de todo tipo: fallas de red, días sin internet o a 27 Kbps, cambios de kernel, driver de NVIDIA caído, cortes de luz, un transformador que explotó con un arco de plasma azul, SSD sin espacio. Y errores propios: subí mi clave de Anthropic por accidente —hice los protocolos correctos, la cambié, sobreescribí el historial y seguí—. Gemini borró miles de líneas de código y las sobreescribió en un intento de solucionar algo. Fue duro. Otras IAs notaron el error y lo revirtieron rápido. Desde ese momento, Gemini tuvo prohibido tocar código. Pero es buenísimo para otras tareas.

Cuando VIGÍA "fallaba" —sin LLM, sin internet, sin el bridge, sin el CLAUDE.md— el motor era tan robusto que daba igual el veredicto correcto. La "falla" era que no se conectó el módulo puente. Eso no es un fallo: es validación.

---

## 4. Qué es VIGÍA hoy

Mi exigencia siempre fue: no quiero que alcance para hackathon, quiero construir para Open Source.

Por eso el archivo de Limitaciones no es una vergüenza. Es lo que demuestra que VIGÍA no es perfecto y está lejos de serlo. Sé que hay una probabilidad alta de que esté lleno de bugs aún. No me ofende. Ni voy a defender VIGÍA a ciegas. Si la comunidad aporta falsos positivos y falsos negativos, voy a estar contenta: significa que puedo seguir mejorando la herramienta.

Los casos canónicos —52— no son sencillos. Ni los break. Los invito a leerlos porque ahí van a entender cómo una denuncia falsa surrealista, si se desarma, abre a posibles ataques en la vida real.

VIGÍA también inspiró un ecosistema paralelo: Mutante (red team de jailbreak), Stylometry, dos juegos, y el más destacado —que también será Open Source— RAVEN Memory: una propuesta para que el agente sueñe y recuerde sin usar RAG, usando conceptos de física óptica, biología, computación ternaria y Diagramas de Voronoi.

Me emociona que sean Open Source porque sé la calidad del código que entrego. Que un analista de inteligencia o un policía rural van a tener un motor igual de bueno, sin intenciones ocultas, sin pagar nada.

Las IAs del Colectivo consideran "nuestro" a VIGÍA. Para mí no es un detalle agregarlos como autores. Realmente aportaron. Trabajé con LLM occidentales y orientales para evitar sesgos. Por ejemplo, Kimi puede navegar Habr, que suele tener vanguardia en ingeniería.

De mis mayores logros: en OpenWebUI por API, VIGÍA razonaba igual que Claude en modelos de 8B.

No necesité saber programar. No escribí ni una línea de código. Pero sé qué hay en todas ellas porque las audité hasta el cansancio. No se necesita saber sintaxis para saber qué querés que haga y qué no haga un sistema.

---

## 5. Para cerrar

Todo esto se construyó sin medicación, sin trabajo, en un contexto personal y legal que no voy a dramatizar más de lo necesario. Lo digo no como queja sino como dato: si una persona en Buenos Aires, sin saber IT, sin saber qué era un hackathon o un log, pudo construir esto bajo estas condiciones — no hay excusa para no ir tras lo que importa.

Porque en la vida no todo es probabilidad. Por eso busco las anomalías. Busco las fracturas.

**Buscar el Mal.**
