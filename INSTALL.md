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

**`PermissionError: /var/lib/vigia`**
Verificar que `.env` tiene `VIGIA_EVIDENCE_DIR` apuntando a un directorio
local, no a `/var/lib/vigia/evidence`. Puede haber duplicados en el `.env`
si se editó varias veces — limpiar con:
```bash
python3 -c "
lines = open('.env').readlines()
seen = {}
result = []
for line in lines:
    key = line.split('=')[0].strip()
    if key.startswith('#') or '=' not in line:
        result.append(line)
    elif key not in seen:
        seen[key] = True
        result.append(line)
open('.env', 'w').writelines(result)
print('OK')
"
```
