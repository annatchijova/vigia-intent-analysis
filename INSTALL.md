# VIGÍA — Installation Guide

> Tested on Ubuntu 22.04 / Linux Mint with Python 3.12.

---

## Prerequisites

```bash
python3 --version   # 3.10 or higher
pip3 --version
openssl version
```

---

## Install from GitHub (without cloning)

If you only want to install the package without cloning the full repository:

```bash
pip install git+https://github.com/annatchijova/vigia-intent-analysis.git
```

### Verify installation

```bash
python3 -c "import vigia; print('OK — vigia installed')"
```

### To run tests, install dev extras

```bash
pip install "git+https://github.com/annatchijova/vigia-intent-analysis.git#egg=vigia-forensic[dev]"
python3 -m pytest tests/ -v --tb=short
```

> **Note:** For active development or to use the full system features (MCP server,
> environment variables, evidence directory), it is recommended to clone the
> repository and follow steps 1–12 below.

---

## 1. Clone the repository

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis.git
cd vigia-intent-analysis
```

---

## 2. Update setuptools before installing

```bash
pip install --upgrade setuptools --break-system-packages
```

> **Why:** Ubuntu 22.04 ships with setuptools 68.x which does not support the
> modern build backend. Without this step, `pip install -e .` fails with
> `BackendUnavailable`.

---

## 3. Install VIGÍA in editable mode

```bash
pip install -e . --break-system-packages
```

---

## 4. Create subpackage __init__.py files

The `vigia/security/` and `vigia/forensics/` subpackages need their
`__init__.py` files for Python to recognize them. Run this script from the root:

```bash
python3 fix_inits.py
```

> **Why:** The repo reorganization left these files pending automatic generation.
> This is a known step that will be automated in v2.1.

---

## 5. Create the evidence directory

```bash
mkdir -p evidence
```

---

## 6. Copy the system prompt to the data directory

```bash
mkdir -p vigia/data
cp docs/system_prompt_peirce.md vigia/data/system_prompt_peirce.md
chmod 640 vigia/data/system_prompt_peirce.md
```

---

## 7. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Required fields:

```
ANTHROPIC_API_KEY=sk-ant-...           # Get it at console.anthropic.com
VIGIA_HMAC_KEY=                        # Generate: openssl rand -hex 32
KASSANDRA_SALT=                        # Generate: openssl rand -hex 16
VIGIA_EVIDENCE_DIR=/path/to/your/repo/evidence
VIGIA_SYSTEM_PROMPT_PATH=/path/to/your/repo/vigia/data/system_prompt_peirce.md
VIGIA_LLM_BACKEND=anthropic
```

> **Warning:** The `VIGIA_EVIDENCE_DIR` value in `.env.example` points to
> `/var/lib/vigia/evidence` which requires root permissions. Always replace it
> with a path inside the repo directory for development.

---

## 8. Verify the installation

```bash
export $(grep -v '^#' .env | xargs)
python3 -c "import vigia.security; print('OK')"
```

You should see:

```
[VIGIA][SecurityAudit] WARNING: Using ephemeral HMAC key...
OK
```

Permission warnings for `/var/log/vigia` are normal in development —
the system automatically falls back to a safe temporary directory.

---

## 9. Start the MCP server

```bash
export $(grep -v '^#' .env | xargs)
python3 vigia/tools/vigia_sift_bridge.py
```

You should see the session token and nonce prefix:

```
[VIGIA] Session token: ...
[VIGIA][SECURITY] Session nonce prefix: ...
```

---

## 10. Run a demo case

```bash
export $(grep -v '^#' .env | xargs)
python3 run_case.py
```

Demo cases are in `data/cases/`. The `run_case.py` script in the root points
to the active case — edit it to switch cases.

---

## Known warnings (non-blocking)

| Warning | Cause | Impact |
|---|---|---|
| `Cannot write to /var/log/vigia` | No root permissions | None — uses safe temp directory |
| `Using ephemeral HMAC key` | `VIGIA_HMAC_KEY` not set | Log chain not verifiable across restarts |
| `KASSANDRA_SALT not set` | Variable not configured | Predictable nonce — development only |
| `caie unavailable (trust_decay)` | Module under development | CAIE disabled — rest works |
| `adversarial_nlp unavailable` | `vigia.tools.forensic_db` pending | NLP disabled — rest works |
| `entanglement unavailable` | Module pending | Disabled — rest works |

---

## Ollama (offline alternative)

If you prefer to run without an Anthropic API key:

```bash
# Install Ollama: https://ollama.com
ollama pull llama3
```

In `.env`:
```
VIGIA_LLM_BACKEND=ollama
VIGIA_OLLAMA_HOST=http://127.0.0.1:11434
VIGIA_OLLAMA_MODEL=llama3
```

---

## Known issues

**`ModuleNotFoundError: No module named 'vigia.sandbox'`**
```bash
# Create compatibility shim
nano vigia/sandbox.py
# Contents: from vigia.security.sandbox import sandboxed_execute, safe_grep
```

**`ModuleNotFoundError: No module named 'vigia.tools.document_integrity'`**
```bash
# The correct file is in vigia/forensics/ — create shim:
nano vigia/tools/document_integrity.py
# Contents: from vigia.forensics.document_integrity import audit_document_integrity, analyze_image_layers, detect_document_geometry, ocr_semantic_validator
```

**`ModuleNotFoundError: No module named 'vigia.tools.vision_audit'`**
```bash
nano vigia/tools/vision_audit.py
# Contents: from vigia.forensics.vision_audit import vision_intent_audit
```

---

## 11. Start the REST API (for OpenWebUI and Claude Code)

VIGÍA exposes a REST API in `vigia_api.py` that allows integration with
OpenWebUI, Claude Code, and any HTTP client.

### Default port

```bash
export $(grep -v '^#' .env | xargs)
python3 vigia_api.py
# Starts at http://0.0.0.0:8000
```

### Change the port

If port 8000 is in use (for example, OpenWebUI runs on 8080 and you need
to avoid conflicts), use environment variables:

```bash
VIGIA_PORT=8001 python3 vigia_api.py
# Or also:
VIGIA_HOST=127.0.0.1 VIGIA_PORT=8001 python3 vigia_api.py
```

Or add it to `.env`:
```
VIGIA_PORT=8001
VIGIA_HOST=127.0.0.1
```

### OpenWebUI integration

OpenWebUI allows connecting external models via "OpenAI-compatible API".

1. Start VIGÍA first: `python3 vigia_api.py`
2. In OpenWebUI → **Settings → Connections → OpenAI API**
3. URL: `http://127.0.0.1:8000` (or whichever port you configured)
4. API Key: any string (VIGÍA does not validate the key in development mode)

> **Note for non-standard OpenWebUI port installations:**
> OpenWebUI installed via `pipx` runs on the port passed to
> `open-webui serve --port XXXX`. If your installation runs on 8080,
> VIGÍA doesn't conflict — they are separate services on separate ports.
> Just make sure to point OpenWebUI to the correct VIGÍA API URL.

### Verify the API is responding

```bash
curl http://127.0.0.1:8000/health
# Expected response: {"status":"ok"}
```

---

## 12. Claude Code integration

Claude Code can call VIGÍA directly as an MCP tool.
See `docs/claude_code_integration.md` for full configuration.

Quick start:
```bash
# In one terminal: start VIGÍA
python3 vigia_api.py

# In another terminal: point Claude Code to http://127.0.0.1:8000
claude mcp add vigia http://127.0.0.1:8000
```
