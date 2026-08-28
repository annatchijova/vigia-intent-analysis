# VIGÍA — Guía de Instalación

> Probada en Ubuntu 22.04 / Linux Mint con Python 3.12.

---

## Requisitos previos

```bash
python3 --version   # 3.10 o superior
pip3 --version
openssl version
```

---

## Instalación desde GitHub (sin clonar)

Si solo querés instalar el paquete sin clonar el repositorio completo:

```bash
pip install git+https://github.com/annatchijova/vigia-intent-analysis.git
```

### Verificar instalación

```bash
python3 -c "import vigia; print('OK — vigia instalado')"
```

### Para ejecutar tests, instalar extras dev

```bash
pip install "git+https://github.com/annatchijova/vigia-intent-analysis.git#egg=vigia-forensic[dev]"
python3 -m pytest tests/ -v --tb=short
```

> **Nota:** Para desarrollo activo o para usar las funciones completas del sistema
> (servidor MCP, variables de entorno, directorio de evidencia), se recomienda
> clonar el repositorio y seguir los pasos 1–12 a continuación.

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
cd vigia-intent-analysis
```

---

## 2. Actualizar setuptools antes de instalar

```bash
pip install --upgrade setuptools --break-system-packages
```

> **Por qué:** Ubuntu 22.04 trae setuptools 68.x que no soporta el build backend
> moderno. Sin este paso, `pip install -e .` falla con `BackendUnavailable`.

---

## 3. Instalar VIGÍA en modo editable

```bash
pip install -e . --break-system-packages
```

---

## 4. Crear los __init__.py de los subpaquetes

Los subpaquetes `vigia/security/` y `vigia/forensics/` necesitan sus archivos
`__init__.py` para que Python los reconozca. Corré este script desde la raíz:

```bash
python3 fix_inits.py
```

> **Por qué:** La reorganización del repo dejó estos archivos pendientes de
> generación automática. Es un paso conocido que se automatizará en v2.1.

---

## 5. Crear el directorio de evidencia

```bash
mkdir -p evidence
```

---

## 6. Copiar el system prompt al directorio de datos

```bash
mkdir -p vigia/data
cp docs/system_prompt_peirce.md vigia/data/system_prompt_peirce.md
chmod 640 vigia/data/system_prompt_peirce.md
```

---

## 7. Configurar las variables de entorno

```bash
cp .env.example .env
nano .env
```

Completar obligatoriamente:

```
ANTHROPIC_API_KEY=sk-ant-...           # Obtener en console.anthropic.com
VIGIA_HMAC_KEY=                        # Generar: openssl rand -hex 32
KASSANDRA_SALT=                        # Generar: openssl rand -hex 16
VIGIA_EVIDENCE_DIR=/ruta/a/tu/repo/evidence
VIGIA_SYSTEM_PROMPT_PATH=/ruta/a/tu/repo/vigia/data/system_prompt_peirce.md
VIGIA_LLM_BACKEND=anthropic
```

> **Advertencia:** El valor de `VIGIA_EVIDENCE_DIR` en `.env.example` apunta
> a `/var/lib/vigia/evidence` que requiere permisos de root. Reemplazarlo
> siempre por un path dentro del directorio del repo para desarrollo.

---

## 8. Verificar la instalación

```bash
export $(grep -v '^#' .env | xargs)
python3 -c "import vigia.security; print('OK')"
```

Deberías ver:

```
[VIGIA][SecurityAudit] WARNING: Using ephemeral HMAC key...
OK
```

Los warnings de permisos en `/var/log/vigia` son normales en desarrollo —
el sistema cae automáticamente a un directorio temporal seguro.

---

## 9. Levantar el servidor MCP

```bash
export $(grep -v '^#' .env | xargs)
python3 vigia/tools/vigia_sift_bridge.py
```

Deberías ver el session token y el nonce prefix:

```
[VIGIA] Session token: ...
[VIGIA][SECURITY] Session nonce prefix: ...
```

---

## 10. Correr un caso de demo

```bash
export $(grep -v '^#' .env | xargs)
python3 run_case.py
```

Los casos de demo están en `data/cases/`. El script `run_case.py` en la raíz
apunta al caso activo — editarlo para cambiar de caso.

---

## Warnings conocidos (no bloquean el sistema)

| Warning | Causa | Impacto |
|---|---|---|
| `Cannot write to /var/log/vigia` | Sin permisos root | Ninguno — usa temp seguro |
| `Using ephemeral HMAC key` | `VIGIA_HMAC_KEY` no configurada | Log chain no verificable entre reinicios |
| `KASSANDRA_SALT not set` | Variable no configurada | Nonce predecible — solo en desarrollo |
| `caie unavailable (trust_decay)` | Módulo en desarrollo | CAIE desactivado — resto funciona |
| `adversarial_nlp unavailable` | `vigia.tools.forensic_db` pendiente | NLP desactivado — resto funciona |
| `entanglement unavailable` | Módulo pendiente | Desactivado — resto funciona |

---

## Ollama (alternativa offline)

Si preferís correr sin API key de Anthropic:

```bash
# Instalar Ollama: https://ollama.com
ollama pull llama3
```

En `.env`:
```
VIGIA_LLM_BACKEND=ollama
VIGIA_OLLAMA_HOST=http://127.0.0.1:11434
VIGIA_OLLAMA_MODEL=llama3
```

---

## Problemas conocidos

**`ModuleNotFoundError: No module named 'vigia.sandbox'`**
```bash
# Crear shim de compatibilidad
nano vigia/sandbox.py
# Contenido: from vigia.security.sandbox import sandboxed_execute, safe_grep
```

**`ModuleNotFoundError: No module named 'vigia.tools.document_integrity'`**
```bash
# El archivo correcto está en vigia/forensics/ — crear shim:
nano vigia/tools/document_integrity.py
# Contenido: from vigia.forensics.document_integrity import audit_document_integrity, analyze_image_layers, detect_document_geometry, ocr_semantic_validator
```

**`ModuleNotFoundError: No module named 'vigia.tools.vision_audit'`**
```bash
nano vigia/tools/vision_audit.py
# Contenido: from vigia.forensics.vision_audit import vision_intent_audit
```


---

## 11. Levantar la API REST (para OpenWebUI y Claude Code)

VIGÍA expone una API REST en `vigia_api.py` que permite integración con
OpenWebUI, Claude Code, y cualquier cliente HTTP.

### Puerto por defecto

```bash
export $(grep -v '^#' .env | xargs)
python3 vigia_api.py
# Levanta en http://127.0.0.1:8000 (solo loopback)
```

### Cambiar el puerto

Si el puerto 8000 está ocupado (por ejemplo, OpenWebUI corre en 8080 y
necesitás evitar conflictos), usar las variables de entorno:

```bash
VIGIA_PORT=8001 python3 vigia_api.py
# O también:
VIGIA_HOST=127.0.0.1 VIGIA_PORT=8001 python3 vigia_api.py
```

O agregarlo al `.env`:
```
VIGIA_PORT=8001
VIGIA_HOST=127.0.0.1
```

### Integración con OpenWebUI

OpenWebUI permite conectar modelos externos via "OpenAI-compatible API".

1. Levantá VIGÍA primero: `python3 vigia_api.py`
2. En OpenWebUI → **Settings → Connections → OpenAI API**
3. URL: `http://127.0.0.1:8000` (o el puerto que hayas configurado)
4. API Key: cualquier string (VIGÍA no la valida; este gateway local no tiene
   una capa de autenticación de aplicación)

> **Límite de seguridad:** por defecto la API escucha solo en `127.0.0.1`.
> No fijes `VIGIA_HOST=0.0.0.0` ni publiques el puerto directamente: CORS no es
> autenticación y el gateway no valida API keys. Si necesitás acceso remoto,
> usá un reverse proxy autenticado y una política de acceso de red deliberada.

> **Nota para instalaciones con OpenWebUI en puerto no estándar:**
> OpenWebUI instalado via `pipx` corre por defecto en el puerto que se
> le pase al comando `open-webui serve --port XXXX`. Si tu instalación
> corre en 8080, VIGÍA no compite — son servicios distintos en puertos
> distintos. Solo asegurate de apuntar OpenWebUI a la URL correcta de
> la API de VIGÍA.

### Verificar que la API responde

```bash
curl http://127.0.0.1:8000/health
# Respuesta esperada: {"status":"VIGÍA operativo"}
```

---

## 11b. Interfaz web (panel local)

VIGÍA incluye un panel web local: navegador de solo lectura sobre todos los
bundles sellados en disco (las tres familias de salida), un panel de
verificación independiente y un lanzador de investigaciones Modo 1 con log
en vivo.

```bash
./launch_vigia_ui.sh
# Se abre en http://127.0.0.1:8010 (solo loopback)
```

Propiedades clave:

- **100% offline.** Sin CDNs, sin fuentes externas, sin peticiones
  salientes — un tripwire CSP `default-src 'self'` bloquea cualquier
  referencia externa accidental. Apto para estaciones forenses aisladas.
- **Veredictos verbatim.** La UI nunca calcula, reformula ni reconcilia un
  veredicto. Los bundles con más de un campo de veredicto (p. ej.
  `decision_trace.decision` sellado junto a `caie_analysis.verdict` en
  EBS v1) muestran todos lado a lado con un aviso de desacuerdo.
- **Verificación independiente.** La pestaña Verify ejecuta
  `forensics/verify_ebs_v1.py` y `verify_tool_log.py` como subprocesos
  stdlib-only (nunca importados) y reporta su salida verbatim, más una
  comprobación pura del sidecar SHA-256.
- **Lanzador Modo 1.** La vista Investigate ejecuta
  `python3 vigia_agent.py --evidence … --case-id …` con evidencia confinada
  a raíces permitidas (`cases/`, `data/cases/`, `evidence/`,
  `blind_cases_for_mcp/`, `results/input/`). Los bundles sellados van a
  `results/webui/` con sufijo de job para que una re-ejecución nunca
  sobrescriba un bundle sellado. Al terminar se muestran exit code, su
  etiqueta documentada y el `agent_verdict` del bundle, lado a lado.
- **Sin capa de autenticación** — misma postura deliberada que la API REST:
  el servidor escucha solo en `127.0.0.1`. Ponlo detrás de una frontera
  autenticada antes de cualquier exposición mayor. El texto de la UI es
  bilingüe (español/inglés) con selector persistente, por defecto el idioma
  del navegador; el vocabulario sellado (valores de veredicto) y el contenido
  de los bundles se muestran siempre verbatim, sin traducir.

Configuración: `VIGIA_HOST` (por defecto `127.0.0.1`), `VIGIA_UI_PORT`
(por defecto `8010`), `VIGIA_UI_MAX_JOBS` (por defecto `1`).

---

## 12. Integración con Claude Code

Claude Code puede llamar a VIGÍA directamente como herramienta MCP.
Ver `docs/claude_code_integration.md` para la configuración completa.

Inicio rápido:
```bash
# En una terminal: levantar VIGÍA
python3 vigia_api.py

# En otra terminal: Claude Code apunta a http://127.0.0.1:8000
claude mcp add vigia http://127.0.0.1:8000
```
