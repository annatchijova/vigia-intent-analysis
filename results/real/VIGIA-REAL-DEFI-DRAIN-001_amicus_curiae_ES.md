# VIGÍA — ANÁLISIS FORENSE DE INTENCIÓN — Amicus Curiae

## Caso: VIGIA-REAL-DEFI-DRAIN-001

```
VIGÍA — INFORME FORENSE DE INTENCIÓN
======================================
ID de Caso      : VIGIA-REAL-DEFI-DRAIN-001
Nombre          : DeFi Wallet Drainer — trustspendcards.net
Investigador    : Agente Autónomo VIGÍA (Claude Code / Anthropic)
Evidencia       : data/cases/VIGIA-REAL-DEFI-DRAIN-001.json
SHA-256 evidencia: 919e68ed68710d55ec5f3aba7ff72566b777879bea253b975936dc664095904f
SHA-256 bundle  : 09597ed33565cd1390234b0356b2ca933ded0c2ddb2fd387a9ccca294bd30be4
SHA-256 agente  : 95f2da2a3bdcb4ca106059e2b06f58fd0ec414c887fec07ac7a0d5edfeb097a1
Sellado         : 2026-06-27T19:57:42Z
Origen SOC      : SOC-2026-DRAIN-001_ES (merabytes_soc_sandbox)
Fase SANS       : Fase 5 — Lecciones aprendidas (generación de informe)
```

---

## RESUMEN EJECUTIVO

VIGÍA analizó cuatro artefactos forenses capturados mediante sandbox Playwright/CDP
del sitio `trustspendcards.net`, activo al momento del análisis (2026-06-21).
El sitio opera como un **vaciador multi-cadena de billeteras DeFi** distribuido
mediante publicidad paga en Instagram, suplantando la identidad visual de
Trust Wallet para atraer víctimas con la promesa de una tarjeta de débito USDT.

El hallazgo forense central es una **falla crítica de OPSEC**: el bundle JavaScript
de la aplicación (index-BJT51uc1.js, 578 KB), generado con Vite y accesible
públicamente, contiene en texto plano la clave secreta del drainer, las billeteras
del atacante en EVM y TRON, y una clave de API de NowNodes. Esto permite la
reconstrucción forense completa del backend del atacante sin necesidad de interactuar
con las billeteras comprometidas.

La cadena de inferencia bayesiana devolvió veredicto **MALICE** con score compuesto
0.4964 (umbral: 0.33), confianza del 95% y posterior agregado 34.901/200.000 sobre
cuatro fuentes de evidencia independientes con confianza efectiva media de 0.9275.
La evidencia demuestra una infraestructura de fraude DeFi de múltiples capas que
abarca ingeniería social, abuso de protocolos legítimos, drenaje automatizado
multi-cadena y manipulación Carnegie documentada en el propio código fuente.

**Veredicto global: MALICE** — El atacante embebió el aviso legal *"We never access
your private keys"* en el mismo archivo JavaScript que implementa exactamente esa
acción. Esta contradicción es deliberada y documenta la intención de engaño.

---

## CRONOLOGÍA DE EVENTOS

| Marca de tiempo | Evento | Fuente |
|---|---|---|
| Anterior al análisis | Registro del dominio `trustspendcards.net` | OSINT de dominio |
| Anterior al análisis | Despliegue del bundle Vite con secretos expuestos | DRAIN-001-A01 |
| Anterior al análisis | Configuración de endpoints de backend `/api/tron-drain`, `/api/register-approved` | DRAIN-001-A02 |
| Anterior al análisis | Registro del proyecto WalletConnect ID `5816c5bba...` para abuso de UI | DRAIN-001-A04 |
| Anterior al análisis | Instalación del pixel de conversión de Facebook `1695678144955877` | DRAIN-001-A03 |
| 2026-06-21T20:48:00Z | Captura de campaña activa en Instagram Ads (utm_id: 52525097425042) | DRAIN-001-A03 |
| 2026-06-21T20:48:00Z | Intercepción del flujo de red: modal WalletConnect auto-activa al cargar | DRAIN-001-A02 |
| 2026-06-21T20:48:00Z | Intercepción: `explorerapi.walletconnect.com` llamado en page load para poblar UI | DRAIN-001-A04 |
| 2026-06-21T20:49:00Z | Análisis estático del bundle JS: extracción de secretos en plaintext | DRAIN-001-A01 |
| 2026-06-27T19:57:42Z | Agente VIGÍA sella el bundle forense. Veredicto: MALICE | Bundle |

---

## HALLAZGOS

### Hallazgo H-001: Backend del atacante expuesto en bundle público

```
ID de Hallazgo  : H-001
Título          : Bundle Vite público contiene credenciales del atacante en texto plano
Veredicto       : MALICE
Confianza       : ALTA
Estado          : CONFIRMADO
Artefacto       : DRAIN-001-A01 (document_visual)
Herramienta     : playwright_cdp_sandbox / static_analysis_vite_bundle
Confianza efect.: 0.9500
Z-score         : 0.931

Primeridad (el signo):
  El archivo index-BJT51uc1.js (578 KB), bundle JavaScript
  de producción de trustspendcards.net, contiene en texto plano:
  — Variable VITE_DRAINER_SECRET (clave de autenticación del backend)
  — Billetera EVM del atacante: 0xD4d6A26Dc84516FF9e1AC8837Dd347Ebe5bCb0c7
  — Billetera TRON del atacante: TSxfbXySDAtoEyDDAHZxYA6X6dY2nB4P29
  — Clave de API NowNodes: fc94c112-d3c2-4202-8f08-e236870e1e4b
  — Aviso legal embebido: "We never access your private keys"

Segundidad (la anomalía estructural):
  Una aplicación financiera legítima no expone credenciales de backend en
  su bundle de cliente. VITE_DRAINER_SECRET es semánticamente explícito:
  la variable lleva la palabra "drainer" en su nombre, documentando el
  propósito en el código. La coexistencia del aviso legal con el código
  que lo viola no es un error de desarrollo — es una técnica de
  manipulación deliberada. El fallo de OPSEC no altera la intención; la confirma.

Terceridad (la ley inferida):
  El atacante construyó la infraestructura de drenaje, la desplegó con
  secretos expuestos por error operacional, pero la intención maliciosa
  está documentada en el propio código. La exposición de las billeteras
  destino permite atribución forense directa sin necesidad de honeypot
  ni interacción. El aviso legal falso constituye manipulación Carnegie
  del tipo "transferencia de autoridad": el actor crea la apariencia de
  legitimidad negando exactamente lo que está haciendo.

Carnegie         : authority_transfer — el disclaimer invierte la realidad
                   ("nunca accedemos a tus claves privadas") en el mismo
                   contexto donde el código implementa ese acceso.
MITRE TTPs       : T1583 (Acquire Infrastructure),
                   T1027 (Obfuscated Files or Information)

Hipótesis alternativa:
  El bundle podría pertenecer a un investigador de seguridad que construyó
  un PoC para documentar técnicas de drainer. REFUTACIÓN: (1) El dominio
  trustspendcards.net está activo y sirviendo contenido a usuarios reales.
  (2) La campaña de Instagram Ads (DRAIN-001-A03) está activa y pagada.
  (3) Los endpoints /api/tron-drain y /api/register-approved son funcionales
  (DRAIN-001-A02). Un PoC de investigación no requiere infraestructura de
  conversión con pixel de Facebook ni publicidad paga.

Corroboración    : DRAIN-001-A02 confirma que el VITE_DRAINER_SECRET es
                   utilizado como cabecera x-drainer-secret en las peticiones
                   POST de drenaje — el secreto no está inerte en el código,
                   está operacional.
```

### Hallazgo H-002: Drenaje automatizado multi-cadena en flujo de red

```
ID de Hallazgo  : H-002
Título          : connectWallet() implementa drenaje USDT en 7 redes simultáneas
Veredicto       : MALICE
Confianza       : ALTA
Estado          : CONFIRMADO
Artefacto       : DRAIN-001-A02 (network_flow)
Herramienta     : playwright_cdp_network_intercept
Confianza efect.: 0.9500
Z-score         : 0.921

Primeridad (el signo):
  Al cargar la página, el modal WalletConnect v2 se activa sin acción
  del usuario. La función connectWallet() ejecuta las siguientes acciones:
  1. Enumeración de saldos USDT del usuario en ETH, BSC, POL, AVAX, ARB,
     BASE y TRON mediante RPC de NowNodes (clave expuesta en DRAIN-001-A01).
  2. Solicitud de firma de transacciones mediante eth_sendTransaction,
     personal_sign y eth_signTypedData.
  3. POST de transacciones firmadas a /api/tron-drain y /api/register-approved,
     autenticados con la cabecera x-drainer-secret.

Segundidad (la anomalía estructural):
  Una tarjeta de débito legítima no requiere acceso a siete redes de
  blockchain simultáneamente al momento de la conexión inicial. La
  enumeración inmediata de saldos antes de cualquier proceso de KYC,
  onboarding o verificación de identidad revela que el objetivo es la
  cuantificación de activos disponibles, no la provisión de un servicio
  financiero. La activación automática del modal WalletConnect elimina
  la fricción deliberadamente — el atacante no quiere que la víctima
  tenga tiempo para evaluar el permiso que está otorgando.

Terceridad (la ley inferida):
  La arquitectura técnica implementa el ciclo completo de un drainer DeFi:
  (i) Atracción vía publicidad paga → (ii) Conexión de billetera inducida →
  (iii) Enumeración de activos multi-cadena → (iv) Solicitud de firma →
  (v) Exfiltración a billeteras del atacante via API autenticada.
  Cada paso está documentado en tráfico de red capturable sin wallet real.
  El uso de x-drainer-secret como autenticación confirma que el endpoint
  de backend es exclusivo del atacante y no una API pública abusada.

Carnegie         : urgency / commitment trap — la activación automática del
                   modal obliga a la víctima a tomar una decisión de firma
                   sin contexto previo. El diseño elimina deliberadamente
                   el tiempo de reflexión.
MITRE TTPs       : T1204.001 (User Execution: Malicious Link),
                   T1566 (Phishing),
                   T1071.001 (Application Layer Protocol: Web Protocols)

Hipótesis alternativa:
  Las peticiones a /api/tron-drain podrían ser de una integración legítima
  de terceros con nomenclatura interna desafortunada. REFUTACIÓN: (1) El
  nombre del endpoint es semánticamente inequívoco ("tron-drain").
  (2) La autenticación es mediante un secreto propio (x-drainer-secret),
  no una API key de proveedor externo. (3) Las firmas solicitadas incluyen
  eth_sendTransaction, que transfiere fondos de forma irreversible.
  (4) El contexto publicitario (suplantación de marca, DRAIN-001-A03)
  excluye el uso legítimo por definición.

Corroboración    : DRAIN-001-A01 (VITE_DRAINER_SECRET coincide exactamente
                   con el secreto usado en x-drainer-secret), DRAIN-001-A03
                   (el flujo de red es el destino de la campaña de Instagram).
```

### Hallazgo H-003: Campaña activa de Instagram Ads con suplantación de marca

```
ID de Hallazgo  : H-003
Título          : Publicidad paga en Instagram suplanta Trust Wallet con branding real
Veredicto       : MALICE
Confianza       : ALTA
Estado          : CONFIRMADO
Artefacto       : DRAIN-001-A03 (cultural_marker)
Herramienta     : playwright_cdp_sandbox / instagram_ad_capture
Confianza efect.: 0.9000
Z-score         : 0.828

Primeridad (el signo):
  Campaña de Instagram Ads activa (utm_id: 52525097425042) que publicita
  una "Trust Wallet VISA USDT Debit Card" utilizando el logotipo real
  y la identidad visual de Trust Wallet. El pixel de conversión de Facebook
  1695678144955877 registra los eventos de los usuarios que completan
  la conexión de billetera — el atacante está midiendo el retorno sobre
  la inversión publicitaria.

Segundidad (la anomalía estructural):
  Trust Wallet (Binance) no opera tarjetas VISA de débito USDT mediante
  un dominio de terceros (trustspendcards.net). El uso de branding real
  en publicidad paga constituye tanto una violación de marca registrada
  como una técnica de ingeniería social documentable: la plataforma de
  Instagram valida implícitamente el anuncio al mostrarlo, creando un
  halo de legitimidad que el atacante explota de forma deliberada.
  El pixel de Facebook convierte el fraude en un negocio optimizado:
  el atacante sabe exactamente cuántas víctimas completan el flujo.

Terceridad (la ley inferida):
  La existencia de una campaña publicitaria paga implica: (i) inversión
  económica previa por parte del atacante, (ii) selección de audiencia
  basada en intereses en criptomonedas, y (iii) optimización del embudo
  de conversión mediante pixel de tracking. Este no es un sitio phishing
  estático — es una operación de fraude DeFi con estructura de marketing
  digital. La campaña activa al momento del análisis indica que el
  atacante considera la operación rentable y continúa invirtiéndose en ella.

Carnegie         : social_proof — la marca Trust Wallet actúa como
                   transferencia de autoridad. La plataforma Instagram
                   actúa como validador implícito por el mero hecho
                   de aceptar y mostrar el anuncio.
MITRE TTPs       : T1566.002 (Spearphishing Link — via redes sociales),
                   T1036 (Masquerading)

Hipótesis alternativa:
  Un tercero podría haber creado la campaña publicitaria sin el conocimiento
  del operador del sitio (anuncio fraudulento colocado por afiliado).
  REFUTACIÓN: (1) El pixel de Facebook 1695678144955877 mide conversiones
  en el sitio, lo que requiere acceso al código fuente del sitio para
  instalar el pixel. (2) El dominio, la publicidad y el backend comparten
  la misma infraestructura de tracking. (3) El utm_id apunta directamente
  al dominio de destino — no existe intermediario.

Corroboración    : DRAIN-001-A02 (el flujo de red documenta qué ocurre
                   cuando la víctima llega desde el anuncio y conecta
                   su billetera).
```

### Hallazgo H-004: Abuso de WalletConnect para construir apariencia de legitimidad

```
ID de Hallazgo  : H-004
Título          : Proyecto WalletConnect legítimo usado para desplegar UI de billeteras reales
Veredicto       : INTENT
Confianza       : ALTA
Estado          : CONFIRMADO
Artefacto       : DRAIN-001-A04 (log_entry)
Herramienta     : playwright_cdp_network_intercept
Confianza efect.: 0.9200
Z-score         : 0.810

Primeridad (el signo):
  Al cargar la página, se realiza una petición a
  explorerapi.walletconnect.com para poblar la lista de billeteras
  compatibles, utilizando el project ID 5816c5bba147eba277e1575494697210.
  El modal resultante muestra iconos y nombres reales de MetaMask,
  Trust Wallet, Coinbase Wallet, Rainbow y otras billeteras reconocidas.

Segundidad (la anomalía estructural):
  La API de WalletConnect Explorer está diseñada para aplicaciones DeFi
  legítimas que integran el protocolo. El atacante la utiliza para
  delegar en WalletConnect la carga de construir una interfaz que parece
  oficial: iconos reales, nombres reales, flujo de conexión familiar.
  Una víctima que ha usado WalletConnect antes reconoce el modal como
  "el proceso normal de conexión". Esta familiaridad es el activo que
  el atacante está explotando — no está falsificando la UI de WalletConnect,
  está usando la UI real de WalletConnect para propósitos maliciosos.

Terceridad (la ley inferida):
  El abuso de WalletConnect constituye un ataque de legitimidad indirecta:
  en lugar de construir una UI falsa (fácilmente detectable), el atacante
  usa infraestructura real cuya aparición es per se una señal de
  legitimidad para usuarios familiarizados con DeFi. La distinción entre
  "usar WalletConnect legítimamente" y "usar WalletConnect para drenar"
  no es visible en la UI — ambos flujos son idénticos hasta el momento
  de la firma. Este hallazgo se clasifica INTENT (no MALICE autónomo)
  porque el uso de WalletConnect no es ilegal en sí mismo; la intención
  maliciosa está acreditada por los demás hallazgos.

Carnegie         : authority_transfer — se delega la apariencia de
                   legitimidad en una tercera parte (WalletConnect/
                   billeteras reconocidas) cuya presencia el atacante
                   no puede controlar, pero sí puede invocar.
MITRE TTPs       : T1036.005 (Masquerading: Match Legitimate Name or Location)

Hipótesis alternativa:
  El project ID podría estar siendo usado por el desarrollador legítimo
  de una aplicación DeFi real que fue comprometida. REFUTACIÓN: (1) El
  resto del código (DRAIN-001-A01) no contiene lógica de aplicación
  financiera legítima — solo lógica de drenaje. (2) El dominio
  trustspendcards.net no corresponde a ningún proyecto DeFi documentado.
  (3) La clave VITE_DRAINER_SECRET y los endpoints /api/tron-drain
  son incompatibles con una aplicación comprometida — son parte del
  diseño original.

Corroboración    : DRAIN-001-A01 (el project ID forma parte del bundle
                   original) y DRAIN-001-A02 (la petición a explorerapi
                   precede directamente al despliegue del modal de firma).
```

---

## CADENA ABDUCTIVA PEIRCEANA (Compuesta)

**PRIMERIDAD — Los signos:**

Un sitio web activo (`trustspendcards.net`) sirve una aplicación React/Vite que
promete una tarjeta de débito USDT de Trust Wallet. Al cargar, activa un modal de
WalletConnect construido con datos reales de `explorerapi.walletconnect.com`. Si el
usuario conecta su billetera, la función `connectWallet()` enumera sus saldos USDT
en 7 redes de blockchain y solicita firmas de transacciones. El bundle JavaScript
público contiene en texto plano la clave secreta del drainer, las billeteras destino
en EVM y TRON, y la clave de API de NowNodes. El mismo bundle contiene el aviso
legal "We never access your private keys". Una campaña activa de Instagram Ads lleva
tráfico al sitio con branding de Trust Wallet. El pixel de Facebook mide conversiones.

**SEGUNDIDAD — Las anomalías estructurales:**

Cada elemento del sistema viola su baseline legítimo de una manera diferente:

- **Bundle JS**: Las variables de entorno de producción no contienen "drainer" en su nombre en aplicaciones legítimas.
- **Flujo de red**: El modal de conexión de billetera no se activa automáticamente en aplicaciones DeFi legítimas — requiere acción explícita del usuario.
- **Publicidad**: Trust Wallet no opera tarjetas de débito VISA a través de dominios de terceros.
- **WalletConnect**: El protocolo es legítimo; su uso para drenar transfiere la apariencia de legitimidad sin heredar la intención legítima.
- **Aviso legal**: Una empresa que nunca accede a claves privadas no necesita declararlo en el mismo archivo que lo hace.

La anomalía más significativa no es ningún elemento aislado, sino su combinación:
la infraestructura técnica (drainer), la distribución (Instagram Ads), la legitimidad
prestada (WalletConnect) y la manipulación psicológica (aviso legal falso) forman
un sistema integrado de fraude. No existen interpretaciones benignas que expliquen
el conjunto sin contradicción.

**TERCERIDAD — La ley inferida:**

El actor construyó una operación de fraude DeFi con cuatro capas diferenciadas:

1. **Capa de adquisición**: Campaña paga en Instagram con suplantación de marca para atraer usuarios con saldos USDT reales.
2. **Capa de engaño técnico**: UI de WalletConnect legítima y aviso legal falso para eliminar fricción cognitiva en el momento de la firma.
3. **Capa de drenaje**: `connectWallet()` automatiza la enumeración de activos y la solicitud de firmas en 7 redes simultáneamente.
4. **Capa de exfiltración**: Endpoints de backend autenticados con clave expuesta en bundle público reciben las transacciones firmadas y las envían a billeteras del atacante en EVM y TRON.

La falla de OPSEC (exposición de secretos en bundle público) no contradice la
intención maliciosa — la confirma al permitir reconstrucción forense completa.
El sistema fue diseñado para engañar a víctimas, no para resistir auditorías forenses.

---

## PROTOCOLO OBLIGATORIO DE REFUTACIÓN (Navaja de Eco)

### Paso 1 — Hipótesis benigna de máxima caridad

**Hipótesis A**: `trustspendcards.net` es un proyecto legítimo de fintech que integra
wallets cripto para una tarjeta de débito USDT real, con errores de seguridad en el
bundle (secretos expuestos por accidente) y una campaña de marketing agresiva (uso
de branding de Trust Wallet por confusión sobre licencias de marca).

**Hipótesis B**: El sitio es un PoC de investigación de seguridad publicado por un
investigador que documenta técnicas de drainer DeFi activas.

### Paso 2 — Prueba contra el conjunto completo de evidencia

**Hipótesis A falla** en cuatro puntos independientes:

1. **VITE_DRAINER_SECRET**: Un fintech legítimo no nombra su variable de autenticación
   con la palabra "drainer". El nombre documenta el propósito con precisión lexical.

2. **Endpoint `/api/tron-drain`**: Un servicio de tarjeta de débito legítimo no implementa
   un endpoint de backend con ese nombre. La nomenclatura es internamente consistente
   con el propósito de drenaje, no con la oferta de servicios financieros.

3. **Activación automática del modal**: Una aplicación legítima pide consentimiento
   explícito antes de conectar la billetera. La activación automática al cargar la página
   elimina la oportunidad de evaluación — es una técnica de presión cognitiva.

4. **Pixel de conversión activo**: Un servicio legítimo mide conversiones. Un drainer
   también. La diferencia es que en el drainer, "conversión" = víctima que firmó.
   La presencia del pixel implica optimización activa del embudo de fraude.

**Hipótesis B falla** en dos puntos:

1. La campaña activa de Instagram Ads (con presupuesto publicitario real) no es
   compatible con un PoC de investigación. Los investigadores no pagan para
   llevar tráfico real a sus demostraciones.

2. Un PoC de investigación publicaría el código fuente con aviso explícito.
   La producción activa del sitio, la campaña paga y el pixel de conversión
   indican una operación dirigida a víctimas reales, no a lectores técnicos.

### Paso 3 — Confirmación del veredicto

Ninguna hipótesis benigna explica el conjunto sin contradicción. El elemento decisivo
es la combinación de **campaña publicitaria activa con presupuesto real** +
**pixel de conversión midiendo éxito** + **endpoint de drenaje funcional**.
Un error o un PoC no requieren los tres elementos simultáneamente.

**Veredicto MALICE sostenido.**

La táctica Carnegie documentada en código fuente eleva la clasificación: el atacante
no solo comete fraude, sino que invierte en construir una narrativa de inocencia
dentro del mismo sistema que implementa el delito. Esto no es negligencia — es diseño.

---

## REGISTRO DE PUERTAS DE REFUTACIÓN (Daubert)

```
PUERTA DE REFUTACIÓN — H-001 (Bundle JS con secretos expuestos)
    Veredicto candidato : MALICE
    Puerta aplicada     : Puerta de Corroboración Daubert (vigia_scorer.py)
    Regla               : n_artefactos >= 2 para esta clase de evidencia
    Resultado           : ACEPTADO. Corroborado por DRAIN-001-A02
                          (VITE_DRAINER_SECRET usado operacionalmente como
                          x-drainer-secret en peticiones POST reales).
    Nota forense        : Corroboración entre fuentes alcanzada. MALICE sostenido.

PUERTA DE REFUTACIÓN — H-002 (Flujo de red multi-cadena)
    Veredicto candidato : MALICE
    Puerta aplicada     : Puerta de Corroboración Daubert (vigia_scorer.py)
    Regla               : Evidencia de drenaje activo requiere confirmación
                          de infraestructura de recepción
    Resultado           : ACEPTADO. Las billeteras destino están confirmadas
                          en DRAIN-001-A01. Los endpoints están documentados
                          con autenticación propia (x-drainer-secret).
    Nota forense        : Ciclo completo documentado: solicitud de firma →
                          POST autenticado → billeteras del atacante.

PUERTA DE REFUTACIÓN — H-003 (Campaña Instagram)
    Veredicto candidato : MALICE
    Puerta aplicada     : Puerta de Corroboración Daubert (vigia_scorer.py)
    Regla               : Evidencia cultural requiere corroboración técnica
    Resultado           : ACEPTADO. La campaña de publicidad es el vector
                          de distribución confirmado del drainer técnico
                          documentado en DRAIN-001-A01 y DRAIN-001-A02.
                          El pixel de Facebook confirma operación activa.
    Nota forense        : La inversión publicitaria es incompatible con
                          hipótesis benigna de error o investigación.

PUERTA DE REFUTACIÓN — H-004 (Abuso de WalletConnect)
    Veredicto candidato : INTENT (candidato rechazado para MALICE autónomo)
    Puerta aplicada     : Techo de artefacto único (vigia_scorer.py)
    Regla               : El uso de WalletConnect no es ilegal en sí mismo.
                          El veredicto MALICE requiere evidencia de intención
                          maliciosa en el uso, no solo en el protocolo.
    Resultado           : Emitido como INTENT. Alcanza MALICE solo en
                          combinación con H-001, H-002 y H-003, lo que
                          efectivamente ocurre en el veredicto compuesto.
    Nota forense        : Corrección arquitectónica conservadora preservada.
                          El hallazgo contribuye al posterior bayesiano
                          sin ser clasificado MALICE de forma autónoma.
```

---

## DOCUMENTACIÓN DEL PROTOCOLO DE AUTOCORRECCIÓN

### Sin contradicciones detectadas — convergencia en iteración 1

El detector de contradicciones retornó 0 contradicciones entre las 4 señales (umbral
de corrección: 2). El agente convergió en la primera iteración sin aplicar ninguna
autocorrección. Esto es coherente con la naturaleza del caso: los cuatro artefactos
apuntan en la misma dirección con mecanismos de evidencia independientes entre sí
(análisis estático de bundle, intercepción de red, captura de campaña, log de API).

La ausencia de correcciones no es un indicador de análisis superficial — es la
consecuencia esperada cuando la evidencia es internamente consistente y no contradictoria.

### Limitación documentada: modo de ruta autónoma

El pipeline ejecutó en modo `agent audit-trail (vigia_agent.py — JSON-replay / autonomous path)`.
En esta ruta, la `CasePatternLibrary` no se invoca por diseño, lo que implica que el
componente `devil_advocate` generó una narrativa determinista en lugar de basarse en
patrones de casos históricos comparables. Esto está documentado en `KNOWN_LIMITATIONS.md`
y no afecta la validez del veredicto, que descansa en el pipeline bayesiano principal.

### HMAC efímero (entorno de desarrollo)

El bundle fue sellado con clave HMAC efímera (sin `VIGIA_HMAC_KEY` configurada).
La cadena H3 es válida dentro de esta sesión pero no verificable externamente.
Para uso en procedimientos judiciales, regenerar el bundle con clave HMAC persistente.

---

## ARTEFACTOS EXAMINADOS

| # | Herramienta | Argumento | Resultado |
|---|---|---|---|
| 1 | sha256_hasher | data/cases/VIGIA-REAL-DEFI-DRAIN-001.json | 919e68ed... |
| 2 | vigia_pipeline | Caso completo — 4 artefactos | MALICE, score=0.4964, conf=95% |
| 3 | contradiction_detector | 4 señales | 0 contradicciones — sin corrección |
| 4 | bundle_sealer | Resultado del pipeline | Bundle sellado — SHA-256: 09597ed3... |
| 5 | validate_case.py | VIGIA-REAL-DEFI-DRAIN-001.json | PASS — 0 errores, 0 advertencias |
| 6 | tests/run_vigia_case.py | VIGIA-REAL-DEFI-DRAIN-001.json | PASS — veredicto MALICE confirmado |
| 7 | EBS H4 verify | VIGIA-REAL-DEFI-DRAIN-001_bundle.json | PASS — bundle íntegro |

---

## BUNDLE FORENSE — 4 HASHES

```
H1 graph_hash   : e995e17df6b64bbb35ad43538dcc0b0d6046df2f3d5949e429956547c06fbbe0
H2 bundle_hash  : e2a3fe20e20da854bd5b53c4535e11af94cff1e9ec1938525d266c3f958544e9
H3 HMAC chain   : 5360c7b3af9aa8813ee0235ebed882aa025f69c09d76a26739529cffeae06a80
                  (clave efímera — dev — configurar VIGIA_HMAC_KEY para producción)
H4 EBS verify   : PASS — OK — bundle íntegro
```

**Verificación**: `sha256sum -c results/real/VIGIA-REAL-DEFI-DRAIN-001_bundle.json.sha256`

---

## MAPEO MITRE ATT&CK

| TTP | Nombre | Evidencia | Confianza |
|---|---|---|---|
| T1583 | Acquire Infrastructure | DRAIN-001-A01 (dominio, bundle, backend propios) | ALTA |
| T1027 | Obfuscated Files or Information | DRAIN-001-A01 (bundle minificado Vite) | ALTA |
| T1566 | Phishing | DRAIN-001-A02, DRAIN-001-A03 (vector Instagram Ads) | ALTA |
| T1566.002 | Spearphishing Link | DRAIN-001-A03 (enlace en anuncio Instagram) | ALTA |
| T1036 | Masquerading | DRAIN-001-A03 (branding Trust Wallet) | ALTA |
| T1036.005 | Match Legitimate Name or Location | DRAIN-001-A04 (UI WalletConnect real) | ALTA |
| T1204.001 | User Execution: Malicious Link | DRAIN-001-A02 (modal auto-activa al cargar) | ALTA |
| T1071.001 | Application Layer Protocol: Web | DRAIN-001-A02 (exfiltración via HTTPS POST) | ALTA |

---

## LIMITACIONES CONOCIDAS

1. **Sin wallet honey pot**: El análisis no interactuó con ninguna billetera real.
   Las transacciones finales (envío de fondos a las billeteras del atacante) no
   fueron ejecutadas ni monitoreadas en blockchain. El análisis documenta la
   infraestructura de drenaje, no el drenaje consumado.

2. **Bundle minificado**: El análisis estático se realizó sobre código minificado.
   La lógica de drenaje es identificable por nombres de variables semánticamente
   explícitos (VITE_DRAINER_SECRET, /api/tron-drain), pero el análisis de flujo
   completo requeriría deobfuscación del bundle.

3. **Estado del dominio al momento de este informe**: Los dominios activos en el
   momento del análisis SOC (2026-06-21) pueden haber sido dados de baja. Los IOCs
   (billeteras, claves) permanecen válidos para investigación blockchain posterior.

4. **HMAC efímero**: Bundle sellado en entorno de desarrollo. No utilizable para
   cadena de custodia judicial sin regeneración con clave persistente.

5. **CasePatternLibrary no invocada**: El componente devil_advocate operó en modo
   determinista en la ruta de agente autónomo. El protocolo de refutación fue
   aplicado manualmente en este informe.

6. **Atribución de identidad del atacante**: Las billeteras EVM y TRON están documentadas,
   pero no se realizó análisis de clustering en blockchain para vincularlas con
   identidades conocidas o patrones de lavado previos. Esto queda fuera del alcance
   del análisis de intención de VIGÍA.

---

## INDICADORES DE COMPROMISO (IOCs)

| Tipo | Valor | Fuente |
|---|---|---|
| Dominio | trustspendcards.net | DRAIN-001-A01, A02, A03 |
| Wallet EVM | 0xD4d6A26Dc84516FF9e1AC8837Dd347Ebe5bCb0c7 | DRAIN-001-A01 |
| Wallet TRON | TSxfbXySDAtoEyDDAHZxYA6X6dY2nB4P29 | DRAIN-001-A01 |
| API Key (NowNodes) | fc94c112-d3c2-4202-8f08-e236870e1e4b | DRAIN-001-A01 |
| WalletConnect Project ID | 5816c5bba147eba277e1575494697210 | DRAIN-001-A04 |
| Facebook Pixel ID | 1695678144955877 | DRAIN-001-A03 |
| Instagram utm_id | 52525097425042 | DRAIN-001-A03 |
| Endpoint | /api/tron-drain | DRAIN-001-A02 |
| Endpoint | /api/register-approved | DRAIN-001-A02 |
| Header de autenticación | x-drainer-secret | DRAIN-001-A02 |
| Nombre de bundle | index-BJT51uc1.js | DRAIN-001-A01 |

---

## TABLA RESUMEN DE VEREDICTOS

| Hallazgo | Veredicto | Confianza | Estado |
|---|---|---|---|
| H-001: Secretos del atacante en bundle público | MALICE | ALTA | CONFIRMADO |
| H-002: Drenaje automatizado multi-cadena | MALICE | ALTA | CONFIRMADO |
| H-003: Campaña Instagram con suplantación de marca | MALICE | ALTA | CONFIRMADO |
| H-004: Abuso de WalletConnect para UI legítima | INTENT | ALTA | CONFIRMADO |
| **COMPUESTO** | **MALICE** | **95% — ALTA** | **CONFIRMADO** |

**Estado cuadripartita**: MALICE — CONFIANZA ALTA  
Acción recomendada: `IMMEDIATE_CONTAINMENT`  
Confianza cuadripartita: 91% · Estabilidad del grafo: 93%  
Posterior bayesiano: 34.901/200.000 — conclusivo

---

*VIGÍA — Haciendo que el engaño sea computacionalmente costoso desde 2026.*

*"El atacante publicó el arma, las claves del arma y el manual de uso en texto plano.*
*No se necesitó honeypot. No se necesitó interacción con la billetera.*
*El código habla. El código siempre habla."*

```
Integridad del bundle:
  Evidence SHA-256 : 919e68ed68710d55ec5f3aba7ff72566b777879bea253b975936dc664095904f
  Bundle SHA-256   : 09597ed33565cd1390234b0356b2ca933ded0c2ddb2fd387a9ccca294bd30be4
  Agente SHA-256   : 95f2da2a3bdcb4ca106059e2b06f58fd0ec414c887fec07ac7a0d5edfeb097a1
  Sellado          : 2026-06-27T19:57:42Z
  H4 EBS verify    : PASS — bundle íntegro
```
