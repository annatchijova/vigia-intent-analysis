# Plan — VIGÍA mínimo: núcleo determinista + MCP para Claude Code + web UI opcional

Estado: **plan, no ejecutado**. Redactado el 2026-09-05 sobre la rama
`claude/modo-vogia-juniors-expertos-h0tjrl`, después de medir el árbol real (no
de leer la documentación, que en varios puntos contradice al código). Cada
afirmación de la sección 1 tiene archivo y línea; las cifras de tamaño se
midieron en el contenedor de esta sesión.

---

## 0. Objetivo

Que VIGÍA se pueda instalar y usar en tres capas acumulativas, cada una con el
mínimo de dependencias que realmente necesita, sin tocar el motor determinista ni
el sello:

| Capa | Qué da | Dependencias de terceros reales |
|------|--------|---------------------------------|
| **core** | `python3 vigia_agent.py` (Modo 1), verificadores stdlib, `python3 -m vigia.report` | **ninguna obligatoria**; recomendadas `defusedxml` (EVTX/XML, si no ABSTAIN honesto) y `pydantic` (si no, fallback a dataclasses) |
| **+ mcp** | servidor `Vigia_Sift_Bridge` por stdio para Claude Code, con un toolset mínimo determinista | `mcp>=1.0,<2`, `psutil` |
| **+ web** | dashboard local `python3 -m vigia.ui` (visor de bundles, verificación, lanzador de Modo 1, reportes de audiencia) | `fastapi`, `uvicorn`, `pydantic` |

Todo lo demás (Anthropic/Ollama, Pillow, numpy, scipy, scikit-learn, reportlab,
matplotlib, torch/CLIP, PyMuPDF, PyYAML) pasa a extras opcionales o se declara
donde falta. El Modo 1 no importa nada de eso.

---

## 1. Lo que se midió (base del plan)

### 1.1 Huella real del núcleo

- `import vigia_agent` carga **cero** paquetes de terceros. El bloque de imports
  de módulo (`vigia_agent.py:37-53`) es stdlib más
  `vigia.core.runtime_fingerprint`; todo lo demás es lazy dentro de funciones
  (líneas 838, 1945, 2155, 2308, 2355).
- La cadena completa del Modo 1 (`vigia.scripts.run_pipeline`,
  `sift_orchestrator`, `vigia_scorer`, `vigia.tools.caie`) carga sólo
  `defusedxml` y `pydantic`, ambos guardados con `try/except` y fallback
  (`vigia/sift/event_log_correlator.py:26`, `vigia/config.py:43`,
  `vigia/core/ebs_v1.py:61`, `vigia/models/ebs.py:56`,
  `vigia/tools/signal_contract.py:31`).
- `_CRITICAL_RUNTIME_DEPS` (`vigia_agent.py:2068-2071`) declara exactamente dos
  dependencias degradables, `defusedxml` y `psutil`, y sólo avisa por stderr.
- Costo de import: 132 ms en total, de los cuales 47 ms son `vigia/__init__.py`.

### 1.2 Lo que declaran los manifiestos (y no coincide)

- `requirements.txt` (24 paquetes) trae `numpy`, `scikit-learn` (que arrastra
  scipy), `Pillow`, `anthropic`, `fastmcp`, y herramientas de desarrollo
  (`pytest`, `black`, `mypy`, líneas 48-52). El propio archivo admite en las
  líneas 10-11 que **ningún módulo importa `fastmcp`**.
- `pyproject.toml` `[project].dependencies` (líneas 32-52) declara 14 paquetes
  como núcleo, incluidos `numpy`, `reportlab`, `anthropic`, `mcp`, `Pillow`.
  Extras existentes: `full`, `prefetch`, `dev`. **No hay extra `web`, `mcp` ni
  `llm`**; `fastapi`/`uvicorn` no están declarados en pyproject aunque
  `vigia/ui/server.py:23-26` y `vigia_api.py:28` los importan sin guarda.
- Imports duros no declarados en ningún manifiesto: `matplotlib`
  (`vigia/pipeline/report_builder.py:7`) y `rich`
  (`vigia/vigia_command_center.py`). `reportlab` está en pyproject pero no en
  requirements.txt.
- La wheel no incluye los módulos raíz (`vigia_agent.py`, `vigia_scorer.py`,
  `sift_orchestrator.py`): `packages.find` sólo toma `vigia*`
  (`pyproject.toml:87-93`). Hoy el Modo 1 requiere clonar.

### 1.3 Servidor MCP

- Arranque duro: `psutil` (`vigia/vigia_sift_bridge.py:48`) y
  `mcp.server.fastmcp` (línea 49). `anthropic` y Ollama se importan sólo al
  llamar (`vigia/config.py:315`, `337`). Pillow es opcional (líneas 93-98).
- **No existe mecanismo para exponer un subconjunto de herramientas.** Las 22
  base más 5 de documentos se registran incondicionalmente vía
  `_register_mcp_tool` (línea 212); sólo 5 enriquecimientos tienen flag
  `VIGIA_*_ENABLED` (líneas 3475-3585). `_PLANNER_TOOL_WHITELIST` (línea 3591)
  no filtra el registro y además omite `deactivate_honey_token`.
- `SYSTEM_PROMPT_PEIRCE = _load_system_brain()` corre **en import** (línea 629)
  con chequeos de modo 0600/0640 y hash; con `VIGIA_STRICT_PROMPT=true` un
  archivo mal chmodeado aborta el servidor aunque las dos únicas herramientas
  que usan el prompt (`reason_with_llm`, `validate_and_correct_analysis`) no se
  usen.
- Transporte: sólo stdio, sin auth, por diseño (`_verify_transport_security`,
  línea 3635; `SECURITY.md:94-125`). Correcto para Claude Code, que lanza el
  proceso él mismo.
- `launch_vigia_mcp.sh` está clavado a `/home/labestiadevigia/vigia-repo` y
  fuerza Ollama; `.mcp.json.example` usa las mismas rutas ajenas y fuerza
  Anthropic. `INSTALL.md:399` manda lanzar el servidor a mano antes de abrir
  `claude`, lo que crea una segunda instancia que Claude Code no usa.
- Dependencias por herramienta (tabla completa en el informe de exploración):
  las herramientas puramente deterministas son stdlib; `list_processes` necesita
  `psutil`; `audit_network` necesita `ss` y root; `mount_sift_evidence` necesita
  `ewfmount`/`mount` y root; `audit_image_metadata` necesita Pillow;
  `analyze_stylometry` es stdlib (no usa sklearn pese a lo que sugiere
  requirements.txt).

### 1.4 Web UI

- Paquete `vigia/ui/`: sólo `server.py` (fastapi, pydantic) y `__main__.py`
  (uvicorn) tocan terceros; `normalizer`, `bundle_index`, `jobs`, `verify`,
  `evidence_paths` son stdlib. SPA vanilla de 51 KiB con CSP estricta, sin
  build.
- El índice de bundles (`vigia/ui/bundle_index.py:28-32, 61`) escanea sólo
  `*.json` en `results/`, `cases/`, `vigia/results/`: los reportes
  `<stem>_report_<audience>_<lang>.md` que ya se escriben al lado del bundle
  quedan invisibles. Agregar una pestaña "Reports" son unas 60-100 líneas en 4
  archivos sin dependencias nuevas (índice, un endpoint, `app.js`, `i18n.js`).
- Tests: 4 de los 6 módulos `tests/test_webui_*.py` no necesitan fastapi; los
  dos que sí (`endpoints`, `security`) importan `fastapi.testclient` sin
  `importorskip` y necesitan `httpx`, que falta en `requirements-ci.txt`.
- `INSTALL_ES.md` no tiene el §11b de la web UI.

### 1.5 Docker

- `Dockerfile:33-36` instala `requirements.txt` más `scikit-learn` y `scipy`
  explícitos: el trío numpy/scipy/sklearn pesa **≈266 MB** sobre una base de
  ≈130 MB, y el Modo 1 no importa ninguno de los tres. El `gcc` del builder
  existe sólo para esas wheels.
- `.dockerignore:24` excluye `*.html`, así que la imagen no lleva
  `vigia/ui/static/index.html`; `.dockerignore:23` excluye `*.md`.
- La imagen no expone puertos; `docker-compose.yml` usa `network_mode: "none"`
  (aislamiento deliberado). La UI en Docker requiere un perfil aparte, no tocar
  el default.

---

## 2. Decisiones de diseño

1. **Una sola fuente de verdad para dependencias: `pyproject.toml`.**
   `dependencies = []`; extras `core-recommended`, `mcp`, `web`, `llm`, `pdf`,
   `full`, `dev`. `requirements.txt` pasa a ser generado/equivalente a
   `.[dev,full,mcp,web,llm,pdf]` y `requirements-ci.txt` a `.[dev,web]` sin
   sklearn, con un test de contrato que los mantiene alineados (patrón de
   `tests/test_mcp_dependency_contract.py` y
   `tests/test_requirements_ci_contract.py`).
2. **El Modo 1 se instala desde clon, no desde wheel, en este plan.** Meter los
   módulos raíz en la wheel (`py-modules`) implica revisar imports planos como
   `from sift_orchestrator import ...`; se deja como fase opcional al final.
3. **Toolset MCP mínimo por variable de entorno, gateado en el único punto de
   registro.** `VIGIA_MCP_TOOLSET=minimal|full` (default `full`, así nada cambia
   para quien ya lo usa) evaluado dentro de `_register_mcp_tool`. El toolset
   mínimo es el conjunto determinista sin root, sin binarios externos, sin LLM.
4. **Sin LLM en el perfil mínimo.** Claude Code es quien razona; el servidor le
   da herramientas deterministas y hechos sellados. `reason_with_llm` y
   `validate_and_correct_analysis` quedan en `full`. Coherente con el Invariante
   3 de CLAUDE.md: el LLM narra, no decide.
5. **Los reportes de audiencia entran en las tres capas.** Como herramienta MCP
   `render_audience_report` (visor, cero autoridad de veredicto, escribe
   hermanos fuera de la evidencia) y como pestaña de la web UI. Es la unión
   natural con el trabajo ya hecho en `vigia/report/`.
6. **Docker: dos imágenes, no una hinchada.** `Dockerfile` default = core (sin
   numpy/scipy/sklearn, sin gcc), `Dockerfile.web` o target `web` para la UI con
   `EXPOSE 8010` y un perfil de compose propio; el compose aislado no se toca.
7. **Degradación honesta, no fallos silenciosos.** Sin `defusedxml`, EVTX/XML
   sigue dando `UNANALYZED_ARTIFACT` → ABSTAIN (ya es así); el plan lo documenta
   en la tabla de perfiles en vez de instalarlo a la fuerza.

---

## 3. Fases (un commit por fase, convención `<área>: <resumen imperativo>`)

### Fase 1 — `packaging: declare install profiles as extras and align manifests`

Archivos: `pyproject.toml`, `requirements.txt`, `requirements-ci.txt`,
`tests/test_install_profiles_contract.py` (nuevo).

- `[project].dependencies = []`. Extras:
  - `recommended = ["defusedxml>=0.7.1", "pydantic>=2.0"]`
  - `mcp = ["mcp>=1.0,<2", "psutil>=5.9.0"]` (mantener el tope `<2`: `mcp` 2.0
    quitó `mcp.server.fastmcp`; `tests/test_mcp_dependency_contract.py` lo pinea)
  - `web = ["fastapi>=0.100.0", "uvicorn>=0.23", "pydantic>=2.0"]`
  - `llm = ["anthropic>=0.18.0", "httpx>=0.25.0"]`
  - `images = ["Pillow>=10.0.0", "python-magic>=0.4.27"]`
  - `pdf = ["reportlab>=4.0", "matplotlib>=3.7"]`
  - `full = ["numpy>=1.24.0", "scipy>=1.11", "scikit-learn>=1.3", "PyYAML>=6.0",
    "rich", "aiofiles>=23.0.0", "aiohttp>=3.9.0", "python-evtx>=0.7.4",
    "python-dateutil>=2.8.0", "iso8601>=2.0.0"]` más los extras anteriores
  - `dev` = el actual más `httpx` (lo necesita `fastapi.testclient`)
- Quitar `fastmcp` de todos lados (nadie lo importa).
- Sacar `pytest`/`black`/`mypy` de `requirements.txt`.
- Declarar `matplotlib` y `rich` donde corresponde (hoy no están en ningún
  manifiesto).
- Test de contrato nuevo: (a) `python3 -I -c "import vigia_agent"` en
  subproceso no carga ningún paquete fuera de stdlib + `vigia*`; (b) la cadena
  Modo 1 carga como máximo `{pydantic, defusedxml}` y sus dependencias
  transitivas; (c) `requirements*.txt` ⊆ unión de extras declarados.

Verificación: en un venv limpio, `pip install -e .` (sin extras) y
`python3 vigia_agent.py --evidence data/cases/FF-GENUINE-001.json --case-id X
--output /tmp/x/X_bundle.json` sella el bundle, exit code 1 (MALICE), y
`sha256sum -c` pasa. Con `pip install -e .[web]` la UI levanta.

### Fase 2 — `mcp: minimal toolset for Claude Code, lazy prompt vault, portable launcher`

Archivos: `vigia/vigia_sift_bridge.py`, `launch_vigia_mcp.sh`,
`.mcp.json.example`, `scripts/make_mcp_json.py` (nuevo),
`tests/test_mcp_toolset_profiles.py` (nuevo).

- `VIGIA_MCP_TOOLSET` (`minimal`|`full`, default `full`). Set mínimo,
  evaluado en `_register_mcp_tool` (línea 212), que es el único embudo por el
  que pasan las 27 registraciones incondicionales:
  `generate_forensic_hash, list_files, read_evidence, search_pattern,
  calculate_shannon_entropy, infer_intent, detect_habit_incongruence,
  detect_human_jitter, calculate_human_entropy, audit_grice_maxims,
  detect_eco_overinterpretation, analyze_stylometry, cross_artifact_analysis,
  trust_fusion_analysis, compare_paired_bundles, reload_phonetic_dict,
  get_phonetic_dict_stats, render_audience_report`. Fuera del mínimo:
  `list_processes` (psutil), `audit_network` y `mount_sift_evidence` (root,
  binarios), `audit_image_metadata` (Pillow), honey tokens (estado en
  `VIGIA_WORK_DIR`), `reason_with_llm` y `validate_and_correct_analysis` (LLM),
  las 5 de documentos/visión, `analyze_document_register` (PyYAML) y
  `analyze_document_entanglement` (SQLite operacional).
- Loguear al arrancar qué toolset quedó activo y cuántas herramientas expone
  (hoy los docs dicen 22, 21 y "21+" en tres lugares; la cifra real es 27 a 32).
- Nueva herramienta `render_audience_report(bundle_path, audience, lang,
  output_dir=None)`: llama a `vigia.report.writer.write_all`, devuelve las
  rutas escritas y el SHA-256 del bundle fuente. Se registra vía
  `_register_mcp_tool`, se agrega a `_PLANNER_TOOL_WHITELIST` junto con
  `deactivate_honey_token` (hoy ausente por descuido). Docstring: cero
  autoridad de veredicto, nunca escribe dentro del bundle ni en evidencia.
- `_load_system_brain()` deja de correr en import: se convierte en una función
  cacheada llamada desde `_get_session_prompt()` y desde
  `validate_and_correct_analysis`. En toolset `minimal` el prompt no se lee
  nunca, así que un chmod incorrecto no impide arrancar; en `full` el
  comportamiento (y `VIGIA_STRICT_PROMPT`) se conserva, sólo se mueve al primer
  uso. Test: importar el bridge con un prompt de modo 0644 y
  `VIGIA_STRICT_PROMPT=true` no aborta en `minimal`, sí al llamar
  `reason_with_llm` en `full`.
- `import psutil` pasa a ser lazy dentro de `list_processes` (y sigue lazy en
  `sandbox.py`), para que el toolset mínimo arranque con `mcp` solo. Ajustar
  `_CRITICAL_RUNTIME_DEPS`/docs en consecuencia.
- `launch_vigia_mcp.sh`: `cd "$(dirname "$0")"`, sin rutas absolutas, sin forzar
  Ollama; respeta `.env`. `scripts/make_mcp_json.py` genera `.mcp.json` con la
  ruta real del clon y `VIGIA_MCP_TOOLSET=minimal` por defecto para Claude
  Code. `.mcp.json.example` con placeholders `/path/to/vigia` coherentes con
  `INSTALL.md`.
- Test de toolset: con `mcp` instalado, `VIGIA_MCP_TOOLSET=minimal` produce
  exactamente el set anterior vía `list_tools` del servidor FastMCP (hoy ningún
  test ejercita el protocolo; `tests/e2e` llama las corrutinas a mano). Si `mcp`
  no está, `importorskip`, como hacen los tests existentes.

Verificación: en un venv con `.[mcp]` únicamente, `claude` con el `.mcp.json`
generado lista las 18 herramientas mínimas, `generate_forensic_hash` responde y
`render_audience_report` escribe los cuatro `.md` junto a un bundle de `results/`.

### Fase 3 — `webui: reports tab, optional install profile, ES install docs`

Archivos: `vigia/ui/bundle_index.py`, `vigia/ui/server.py`,
`vigia/ui/static/app.js`, `vigia/ui/static/i18n.js`, `launch_vigia_ui.sh`,
`INSTALL_ES.md`, `tests/test_webui_reports.py` (nuevo),
`tests/test_webui_endpoints.py` y `tests/test_webui_security.py`
(`importorskip("fastapi")`).

- `_summarize` agrega `available_reports` sondeando las 4 combinaciones con el
  mismo patrón `with_name()` de `has_reasoning_trace` (líneas 78-81).
- `GET /api/bundles/{id}/report?audience=&lang=` con ambos parámetros
  restringidos por regex a los valores válidos; resuelve por id opaco, devuelve
  `text/plain`. Sin lectura de rutas arbitrarias: se preserva la propiedad de
  `bundle_index.py:5-7`.
- Pestaña `reports` en `app.js:231` renderizada con `textContent` (Markdown
  como texto preformateado; nada de HTML, coherente con la CSP y con la regla
  de `app.js:1-3`). Claves nuevas en ambas tablas de `i18n.js` (el test de
  paridad ya lo exige).
- `launch_vigia_ui.sh`: el preflight sugiere `pip install -e .[web]`.
- `INSTALL_ES.md`: agregar §11b (hoy la guía en español no documenta la UI).
- Los dos tests que importan `fastapi.testclient` pasan a `importorskip`, para
  que un perfil sin `web` no rompa la colección.

### Fase 4 — `docker: slim core image, separate web target, fix dockerignore`

Archivos: `Dockerfile`, `Dockerfile.web` (o target multi-etapa `web`),
`docker-compose.yml` (perfil `web`), `.dockerignore`,
`.github/workflows/docker-publish.yml`.

- Core: `pip install .[recommended]` (sin numpy/scipy/sklearn, sin `gcc`); una
  sola etapa. Healthcheck corregido a `from vigia.core.ebs_v1 import ...`
  (hoy importa `ebs_v1` plano, `Dockerfile:83`). ENTRYPOINT sin cambios.
- Web: `pip install .[recommended,web]`, `EXPOSE 8010`, `CMD python3 -m
  vigia.ui`, `VIGIA_HOST=0.0.0.0` sólo dentro del contenedor y publicado en
  `127.0.0.1:8010` desde compose (perfil `web`, `network_mode: bridge`). El
  servicio default conserva `network_mode: "none"`.
- `.dockerignore`: `!vigia/ui/static/index.html`, `!docs/training/**/*.md` (los
  ejemplos fijados son parte del producto).
- Workflow: construir y verificar ambas imágenes; medir tamaño y fallar si el
  core supera un umbral (propuesto 250 MB comprimido; ajustar tras la primera
  medición real).

### Fase 5 — `docs: install profiles, Claude Code setup, tool counts, execution modes`

Archivos: `INSTALL.md`, `INSTALL_ES.md`, `README.md`, `README_ES.md`,
`docs/EXECUTION_MODES.md`, `SECURITY.md`, `CLAUDE.md`,
`KNOWN_LIMITATIONS.md`, `cronos/`.

- `INSTALL.md`: nueva sección inicial "Perfiles de instalación" con la tabla de
  la sección 0 y un comando por perfil; §12 reescrito para Claude Code (generar
  `.mcp.json`, **no** lanzar el servidor a mano, `VIGIA_MCP_TOOLSET`); agregar
  el paso `VIGIA_PROMPT_HASH=$(sha256sum ...)` que `SECURITY.md:164-173`
  documenta y `INSTALL.md` omite; unificar la cifra de herramientas expuestas.
- `README.md` / `README_ES.md`: fila "Web UI (visor local)" en la tabla de
  modos o nota explícita de que es un visor, y el comando de instalación por
  perfil en Quick Start.
- `docs/EXECUTION_MODES.md`: párrafo "Perfiles de instalación son capas, no
  modos".
- `CLAUDE.md`: `VIGIA_MCP_TOOLSET` en el bloque de env; nota de que en toolset
  mínimo `reason_with_llm` no existe (FALLBACK documentado, no fallo);
  `render_audience_report` en la tabla de herramientas dinámicas.
- `KNOWN_LIMITATIONS.md`: actualizar L-045 (`mcp` en CI) con el perfil `mcp`, y
  nueva L-075 "Perfil mínimo: sin `defusedxml`, EVTX/XML produce ABSTAIN; sin
  `psutil`, `list_processes` no se registra" si se considera limitación y no
  sólo degradación documentada.
- Traza CRONOS de la sesión que ejecute el plan (§9 de
  `docs/ENGINEERING_DISCIPLINE.md`).

### Fase 6 (opcional) — `packaging: ship root entry points in the wheel`

`py-modules = ["vigia_agent", "vigia_scorer", "sift_orchestrator"]` y un
`[project.scripts] vigia-agent = "vigia_agent:main"`. Requiere auditar los
imports planos (`from sift_orchestrator import`, `from vigia_scorer import`) y
el fallback `run_pipeline` (`vigia_agent.py:1945-1947`). Sólo si se quiere
`pip install vigia-forensic` sin clonar.

---

## 4. Tests y CI que agrega el plan

| Test | Qué fija |
|------|----------|
| `test_install_profiles_contract.py` | `import vigia_agent` sin terceros; cadena Modo 1 ⊆ {pydantic, defusedxml}; requirements ⊆ extras |
| `test_mcp_toolset_profiles.py` | set exacto de `minimal` vía `list_tools`; `full` ⊇ `minimal`; prompt vault no se lee en `minimal` |
| `test_webui_reports.py` | `available_reports` en el índice; endpoint devuelve el `.md` por id opaco; parámetros fuera de enum → 422; nunca lee fuera del directorio del bundle |
| Job CI `minimal-profile` (`vigia-forensic-ci.yml`) | venv con `pip install -e .` sin extras: corre Modo 1 sobre un caso del corpus, `sha256sum -c`, y el subconjunto de tests stdlib (`tests/test_determinism_sealed_verdict.py`, `tests/test_report_*.py`, `tests/test_webui_normalizer.py`, `bundle_index`, `jobs`, `verify`) |
| Job CI `docker-size` | falla si la imagen core supera el umbral |

Los tests existentes que ya protegen los bordes y deben seguir verdes:
`test_mcp_dependency_contract.py`, `test_requirements_ci_contract.py`,
`test_mcp_transport_auth_theater.py`, `test_b100_b101_abstain_alert_and_deps.py`,
`test_b168_api_contract_parity.py`, `test_webui_*`, `test_report_*`.

---

## 5. Riesgos y preguntas abiertas

1. **`_load_system_brain()` lazy cambia cuándo falla el servidor.** Hoy un
   prompt ausente con `VIGIA_STRICT_PROMPT=true` aborta al arrancar; con el
   cambio aborta en la primera llamada LLM. En `minimal` es lo deseado; en
   `full` hay que decidir si se conserva el chequeo en arranque (propuesta:
   sí, se ejecuta en `__main__` sólo cuando el toolset incluye herramientas
   LLM).
2. **¿CAIE en el toolset mínimo?** Es stdlib y determinista, pero pesa 3469
   líneas y su flag `VIGIA_CAIE_ENABLED=false` hoy imprime SECURITY ALERT. La
   propuesta lo incluye por ser el corazón cross-artefacto; sacarlo dejaría al
   perfil mínimo sin fracturas.
3. **Docker web expone la UI sin auth.** Sólo publicada en loopback del host
   desde compose; hay que decir explícitamente que no se publique en `0.0.0.0`
   (mismo aviso que `INSTALL.md:300-304` da para la API).
4. **Mover deps a extras rompe a quien hacía `pip install -r requirements.txt`
   esperando todo.** Se mitiga manteniendo `requirements.txt` como el perfil
   completo y documentándolo en el header del archivo.
5. **`vigia_api.py` (Modo 5, puerto 8000)** queda fuera del perfil `web`
   propuesto; usa CORS abierto y OpenAI-compat. Se documenta como perfil aparte
   (`api`) o se marca experimental, pero no se instala por defecto. Decisión
   pendiente.
6. **`docs/QUICK_START.md` es un fósil** (guía "Hito 1" con nombres de layout
   plano). Fuera de alcance de este plan salvo un aviso al inicio del archivo
   señalando a `INSTALL.md`.

---

## 6. Orden sugerido de ejecución y tamaño estimado

| Fase | Archivos | Estimación |
|------|----------|------------|
| 1 packaging | 4 | chica; riesgo bajo, todo contractual |
| 2 mcp | 5 | mediana; requiere `mcp` instalado para probar `list_tools` |
| 3 webui | 8 | chica; patrón ya existente en 4 archivos |
| 4 docker | 5 | mediana; la medición de tamaño necesita una build real |
| 5 docs | 9 | chica pero transversal |
| 6 wheel | 2 + auditoría de imports | opcional |

Cada fase termina con la suite completa verde
(`PYTHONPATH=$(pwd) python3 -m pytest tests/ vigia/tests/ -q --tb=short --no-cov
--ignore=tests/integration`) y push a la rama de trabajo.
