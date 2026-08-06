## Admisibilidad Judicial (ISO 27037 / Daubert Standard)

VIGIA esta disenada para producir evidencia digital admisible en tribunales bajo
el estandar **Daubert** (EE.UU.) y la norma **ISO 27037:2012** (internacional).
A continuacion se detalla como cada componente del sistema satisface los
requisitos de admisibilidad.

### Requisito 1: Metodologia Cientifica Reproducible

**Daubert exige** que la tecnica sea testeable y haya sido sometida a revision.

VIGIA implementa:

- **Determinismo forzado** (`VIGIA_FORENSIC_LOCK=true`): temperatura del LLM
  fijada en 0, seed fijo para Ollama (42). La misma evidencia produce el
  mismo reporte. Verificable con `make check-determinism`.
- **Marco teorico publicado**: semiotica de Peirce (abduccion), maximas de
  Grice (pragmatica forense), patrones de Carnegie (deteccion de manipulacion),
  filtro de Eco (sobreinterpretacion). Cada herramienta documenta que teoria
  aplica y por que.
- **Cadena abductiva explicita**: cada paso de la investigacion incluye un
  campo `reasoning` que explica POR QUE se eligio la herramienta siguiente.
  Un auditor puede reconstruir toda la logica sin ejecutar el sistema.

### Requisito 2: Cadena de Custodia Inmutable

**ISO 27037 exige** que la evidencia digital no sea alterada durante el analisis.

VIGIA implementa:

- **Hash atomico durante lectura**: `read_evidence` usa `O_NOFOLLOW` +
  `os.fstat(fd)` + lectura en un solo pass. El SHA-256 corresponde exactamente
  a los bytes procesados (sin ventana TOCTOU).
- **Audit log firmado con HMAC encadenado**: cada entrada del log forense
  incluye `_prev_hmac` (hash de la entrada anterior) y `_hmac` (HMAC-SHA256
  del contenido + hash previo). Alterar cualquier linea invalida toda la
  cadena posterior. Verificable con `audit_logger.verify_chain()`.
- **Evidencia montada en solo lectura**: Docker monta el directorio de
  evidencia con `:ro`. El analisis no puede modificar la fuente.
- **WORM enforcement**: `audit_logger.enforce_worm()` aplica `chattr +i`
  (Linux ext4/xfs) al log, haciendolo inmutable a nivel kernel.

### Base Legal para Autenticacion por Hash

Los mecanismos de cadena de custodia de arriba no son solo una decision
de diseno interna — la autenticacion de evidencia digital por hash es
practica probatoria reconocida, no solo la logica propia de VIGIA.

- **Estados Unidos — FRE 902(13) y 902(14)** (vigentes desde el 1 de
  diciembre de 2017): estas reglas permiten la auto-autenticacion de un
  registro electronico via un "proceso de identificacion digital" — un
  valor hash — sin requerir testimonio pericial de base en el juicio. Una
  coincidencia de hash entre un original y una copia se acepta como
  autenticacion de que el dato es el que dice ser.
- **Argentina**: no hay un articulo unico codificado equivalente a la
  902(14). El equivalente existe como doctrina y jurisprudencia: el hash
  se trata como huella digital — si no cambia, evidencia que contenido,
  fecha de creacion y cadena de custodia se preservaron. La cadena de
  custodia digital suele describirse en tres fases: obtencion,
  incorporacion al proceso, y valoracion. La alteracion de metadatos o
  una cadena de custodia rota tipicamente derivan en exclusion
  probatoria por falta de confiabilidad.

**Nota de alcance:** este precedente cubre autenticacion por hash de la
integridad — es lo que respalda el SHA-256 atomico de `read_evidence` y
el audit log encadenado con HMAC de arriba. No cubre, en ninguna de las
dos jurisdicciones, pruebas de conocimiento cero (ZK) u otros sistemas de
prueba criptografica como metodo de autenticacion; eso sigue siendo
derecho no asentado. No presentar mecanismos basados en ZK en otra parte
de este proyecto como si tuvieran el mismo respaldo legal que los
mecanismos de cadena de hash descriptos en esta seccion.

### Requisito 3: Operador Humano Cualificado

**Daubert exige** que la tecnica sea aplicada por un profesional competente.

VIGIA implementa:

- **Witness Mode (Dual Custody)**: cuando el veredicto es MALICE o INTENT,
  el reporte se firma con una segunda clave HMAC (`VIGIA_HUMAN_OPERATOR_KEY`)
  que prueba que un analista autorizado estaba presente. Sin esta co-firma,
  el reporte se marca como `UNSIGNED` con una advertencia.
- **Explain Mode**: `make investigate MODE=explain` muestra que haria el
  planner sin ejecutar nada. El operador revisa ANTES de autorizar.
- **Self-correction**: `validate_and_correct_analysis` chequea 4 falacias
  peirceanas antes de emitir un veredicto final.

### Requisito 4: Tasa de Error Conocida

**Daubert exige** que la tecnica tenga una tasa de error conocida o conocible.

VIGIA implementa:

- **Escala de 4 niveles** (NOISE / SUSPICION / INTENT / MALICE): no es
  binario. Cada nivel requiere mas evidencia que el anterior.
- **Cross-validation obligatoria**: ningun tool individual puede disparar
  MALICE. Se requieren al menos 2 fuentes independientes de evidencia.
- **Humildad epistemica**: cada conclusion incluye `what_would_falsify_this`
  — la condicion bajo la cual la hipotesis seria falsa.
- **`check_determinism.py`**: ejecuta N veces el mismo analisis y compara
  hashes. Cualquier divergencia se reporta como NO-DETERMINISMO.

### Requisito 5: Aceptacion por la Comunidad Cientifica

**Daubert exige** aceptacion general de la tecnica en la comunidad relevante.

VIGIA implementa:

- **Exportacion STIX 2.1**: los hallazgos se exportan a formato estandar
  ingestable por OpenCTI, MISP, y cualquier plataforma compatible.
- **Mapeo MITRE ATT&CK**: cada senal se vincula a una tecnica ATT&CK
  especifica con su ID y URL.
- **Codigo abierto (Apache 2.0)**: el sistema completo es auditable por cualquier
  perito o contrapericia.

### Protocolo de Uso en Contexto Judicial

```
# 1. Generar claves
make hmac-key                    # Clave del sistema
export VIGIA_HUMAN_OPERATOR_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 2. Activar modo forense
export VIGIA_FORENSIC_LOCK=true
export VIGIA_STRICT_MODEL_CHECK=true

# 3. Analizar evidencia (aislado, sin red, read-only)
EVIDENCE_PATH=/mnt/caso_2025_001 make run

# 4. Verificar integridad
make check-integrity             # HMAC chain intacta
make check-determinism           # Reproducibilidad confirmada

# 5. Sellar log (WORM)
python3 -c "from vigia.security import audit_logger; print(audit_logger.enforce_worm())"

# 6. Exportar para el tribunal
cp reports/investigation_*.json /mnt/entrega_pericial/
cp logs/security_audit.log      /mnt/entrega_pericial/
```

### Mapeo ISO 27037:2012

| Clausula ISO | Requisito | Implementacion VIGIA |
|---|---|---|
| 5.4.1 | Preservacion de evidencia | Montaje read-only, hash atomico |
| 5.4.2 | Documentacion de procesos | Audit log HMAC, campo `reasoning` |
| 5.4.3 | Cadena de custodia | HMAC encadenado, WORM, timestamps UTC |
| 6.2 | Competencia del operador | Witness Mode, HUMAN_OPERATOR_KEY |
| 6.3 | Validacion de herramientas | check_determinism.py, tests E2E |
| 7.1.2 | Integridad de datos | SHA-256 atomico, O_NOFOLLOW, O_EXCL |

### Limitaciones Documentadas (Transparencia Pericial)

- Las herramientas basadas en LLM (`reason_with_llm`, `validate_and_correct_analysis`)
  no son deterministicas al 100% incluso con temperature=0, debido a la naturaleza
  de los modelos de lenguaje. `FORENSIC_LOCK` minimiza pero no elimina varianza.
- La estilometria (`analyze_stylometry`) tiene falsos positivos en textos menores
  a 50 palabras.
- La calibracion cultural esta optimizada para espanol rioplatense. Otros
  dialectos pueden requerir ajustes en los patrones de genero y los campos
  obligatorios de documentos oficiales.
- CLIP (`vision_intent_audit`) es un clasificador zero-shot — no fue entrenado
  especificamente para deteccion de falsificacion documental.
