# Handoff para revisión externa — rama `claude/team-network-session-eiicdu`

**Fecha:** 2026-09-11  **Autor de los cambios:** Claude (rondas 5–12 de esta sesión)
**Destinatario:** revisor externo (Codex u otro), antes del merge a `main`
**Rango:** `origin/main` … `1db6823` — 9 commits

Este documento existe para que la revisión gaste tiempo donde vale. Contiene tres
cosas: el estado verificable de la rama, **dónde atacar primero**, y —tan importante
como lo anterior— **qué ya se falsificó**, para no re-derivarlo.

Todo lo que sigue es reproducible con los scripts citados. Donde un hallazgo no se
ejecutó, dice que no se ejecutó.

---

## 1. Estado de la rama (verificable)

| Medición | Resultado | Cómo reproducir |
|----------|-----------|-----------------|
| Suite en la rama | **2368 passed, 0 failed**, 211 skipped, 28 xfailed | `pytest tests/ vigia/tests/ --ignore=tests/integration` |
| Suite en `origin/main` | **2248 passed, 0 failed** | ídem sobre un worktree de main |
| Tests agregados | +120, todos verdes | — |
| Veredictos alterados en el corpus | **0 sobre 793 bundles** | comparar `verify_ebs_v1.py` y `verify_tool_log.py` en main vs rama |
| Conflictos con `main` | 0 | `git merge-tree` |
| `seal()` determinista | `analysis_fingerprint` idéntico main↔rama | ver §5 |

### Dependencias de CI — dos huecos cerrados en este commit

Auditando la pregunta *"¿están actualizados los requirements?"* aparecieron dos
faltantes **pre-existentes** en `requirements-ci.txt`, que golpeaban justo a los tests
de conducta de esta rama:

| Faltaba | Efecto medido |
|---------|---------------|
| `httpx` | `fastapi.testclient.TestClient` lo exige en tiempo de import. Sin él, los 3 archivos que lo usan levantan `RuntimeError` — **no es un skip, es un error de colección** |
| `uvicorn` | `tests/test_r9_ui_bind_exposure.py` hace `importorskip("uvicorn")`: sin él, los dos tests que comprueban que la UI **se niega** a ligar fuera de loopback **se saltean en silencio** |

El job principal (`pytest.yml`) los tenía por instalar también `requirements.txt`, así
que el hueco estaba enmascarado; pero el propio comentario de B-212 declara que
`requirements-ci.txt` es *"el archivo que el contrato S-1 garantiza completo para la
suite"*, y no lo era.

**Por qué el contrato no lo detectaba:** `test_all_test_imports_resolve_with_requirements_ci`
resuelve con `importlib.util.find_spec`, que **localiza** un módulo sin ejecutarlo. Un
módulo que se localiza bien pero lanza al importarse por una dependencia transitiva
ausente es invisible. Y `httpx` no aparece entre las raíces third-party porque ningún
test lo importa por nombre: lo exige starlette por dentro. Es la clase *"dependencia
transitiva por uso"*. El límite quedó documentado dentro del propio test; cerrar la
clase exigiría importar de verdad cada raíz, con los efectos secundarios que eso trae.

**Node:** ningún workflow tenía `setup-node`, así que los 3 tests que ejecutan el
`app.js` servido —incluido el barrido que encontró los 6 campos que hacían explotar el
render y el lockstep que encontró la divergencia `1.0`— **se salteaban en CI**. Se
agregó `actions/setup-node@v4` a `pytest.yml`.

La rama **no introduce ninguna dependencia Python nueva**: todo lo agregado en código de
producción es stdlib (`ipaddress`, `signal`, `os`). Verificado sobre el diff completo.

### Advertencia sobre las dependencias

Durante casi toda la sesión la suite mostró **7 fallos** que reporté como
"ambientales". Eso era una afirmación a medio verificar: probaba que eran
pre-existentes (fallan igual en `main`), no que fueran ambientales. Al diagnosticarlos
de verdad:

- **6** son tests `async def` que fallan sin `pytest-asyncio` — declarado en
  `pyproject.toml`, `requirements.txt` y `requirements-ci.txt`, con un comentario que
  dice que es obligatorio. Instalándolo, pasan los 11.
- **1** es `test_all_test_imports_resolve_with_requirements_ci`, que detectaba la
  ausencia de `psutil` (también declarado). **Estaba haciendo su trabajo.**

Ninguno era un defecto de código. **Instalar `requirements-ci.txt` antes de correr la
suite** o volverán a aparecer.

---

## 2. Dónde atacar primero

Ordenado por dónde tengo **menos** confianza, no por severidad de lo ya corregido.

### 2.1 `_signal_process_tree` (R11) — el cambio con mayor radio

`vigia/ui/jobs.py`. Pasa de señalar un pid a señalar un **grupo de procesos**. Eso
agranda el radio del error si el grupo resuelto no es el que se cree.

- **Residual que declaré y no cerré:** entre `proc.poll()` y `os.killpg` hay una
  ventana; si el pid se reutiliza ahí, se señala el grupo de un proceso ajeno. No lo
  reproduje (exige wraparound de pids), así que está rotulado como **hipótesis**.
- **Qué probaría yo:** que la guarda contra señalar el grupo del propio servidor
  (`pgid != os.getpgid(0)`) no tenga un camino en el que falle. Hay un test
  (`test_never_signals_the_servers_own_group`) pero cubre un solo escenario.
- **Sugerencia:** `pidfd_open` (Linux ≥5.3) elimina la clase entera.

### 2.2 El esquema doble de payload (R6) — el cambio más sutil

`vigia/core/bundle_builder.py`, `forensics/verify_ebs_v1.py`,
`vigia/forensics/vigia_chain_of_custody.py`. Los verificadores prueban **dos**
definiciones de payload porque existen bundles sellados de ambas épocas.

- Verifiqué que no amplía lo que verifica (§4), pero es el cambio donde un error
  sería más difícil de ver y más caro: toca las tres copias que deben quedar en
  lockstep.
- **Qué probaría yo:** que las tres copias de `_PRESENTATION_FIELDS` y
  `_LEGACY_HASHED_FIELDS` no puedan divergir sin que falle un test. Hay un test de
  lockstep (`TestR6PresentationLockstep`) que lee las constantes por regex del fuente
  — funciona, pero es frágil ante un reformateo.

### 2.3 El vector que introduje yo (R6-5)

Excluir `tool_execution_log` del hash permite **adjuntar un log fabricado** a un bundle
legítimamente sellado sin romper el sello. No se puede cerrar sin romper R6-1. Está
mitigado con un WARNING (`R1_SEAL_SCOPE`), no con un ERROR.

- **Es una decisión, no un descuido**, y está documentada en
  `docs/REDTEAM_ROUND6_PERIMETER.md`. Si la revisión discrepa del nivel (WARNING vs
  ERROR), ése es el lugar para discutirlo.

### 2.4 Cuatro asserts que siguen siendo grep sobre el fuente

Declarados uno por uno en `docs/REDTEAM_ROUND12_SELF_AUDIT.md` §A-6, con su razón.
Habrían pasado con el string dentro de un comentario. Dos ya se elevaron a conducta
real; estos cuatro no.

### 2.5 Alcance de la medición de R9

Confirmé el bind a `0.0.0.0` y la ausencia de autenticación **desde loopback, dentro
del sandbox**. **No** demostré un atacante remoto en una LAN. Si la revisión tiene un
entorno de red real, ése es el hueco de evidencia.

---

## 3. Lo que ya se falsificó — no re-derivar

Cada uno se midió y dio negativo. Está el detalle en el informe de la ronda citada.

| Hipótesis | Resultado | Ronda |
|-----------|-----------|-------|
| XSS almacenado desde un bundle de terceros | FALSIFICADA — `esc()` consistente, `esc(JSON.stringify(o))` en el visor crudo, CSP `script-src 'self'` sin `unsafe-inline` | R10 |
| La UI es un cuarto verificador que diverge | FALSIFICADA — shellea a los verificadores reales, no reimplementa, no anula exit codes | R8 |
| Traversal en `evidence_path` | FALSIFICADA — compara tuplas de `parts` (no prefijos de string), rechaza `..`, absolutas y symlinks | R9 |
| `case_id` validado sólo en el cliente | FALSIFICADA — `jobs.submit` aplica `CASE_ID_RE` server-side | R9 |
| CSRF vía formulario cross-site | FALSIFICADA — el requisito `application/json` fuerza preflight que el servidor no habilita | R9 |
| Degradación de esquema en `verify_ebs_v1.py` (portar R5-1) | NO APLICA — EBS no tiene capa keyed ni selección de esquema por dato | R7 |
| El fallback de canon v1 en `_entry_hash_matches` es un oráculo de colisión | FALSIFICADA — `prev_hash` es linkage-checked crudo **y** cubierto por el hash: fija el esquema | R5 |
| `bool` como `int` alcanza el camino del sello | FALSIFICADA — las tres copias de la canonicalización chequean `bool` antes que `int` | R10-4 |
| El esquema doble deja pasar un bundle legacy alterado | FALSIFICADA — borrar, truncar o alterar el log se detecta | R12 |
| `is_loopback` acepta una dirección no-loopback | FALSIFICADA — 0 falsos positivos sobre 20 formas hostiles | R12 |

---

## 4. Residuales abiertos, con su nivel epistémico

Ninguno está cerrado. Todos están declarados en su informe.

| # | Residual | Nivel | Origen |
|---|----------|-------|--------|
| 1 | Borrar *todos* los marcadores v2 es indistinguible de un bundle legacy si el verificador corre **sin** clave | CONFIRMADO, con test | R5-1 |
| 2 | `integrity` de EBS no tiene capa keyed: es SHA-256 recomputable | CODE FACT | R6 |
| 3 | Adjuntar un log fabricado a un bundle moderno no rompe el sello | CONFIRMADO, mitigado con WARNING | R6-5 |
| 4 | El emparejamiento traza↔bundle compara dos campos que un atacante con escritura puede igualar | CODE FACT | R7 |
| 5 | La clave HMAC por entorno no cierra "mismo usuario o root" | CODE FACT | R8-1 |
| 6 | Atacante remoto en LAN no demostrado | Límite de evidencia | R9 |
| 7 | Divergencia `1.0` entre el predicado Python y el JS: irreducible sin cambiar el formato de cable | CONFIRMADO, con test | R10-4 |
| 8 | `subprocess.run(..., timeout=N)` en los módulos SIFT mata al hijo directo, no al árbol | PLAUSIBLE, no ejecutado | R11 |
| 9 | Reutilización de pid entre `poll()` y `killpg` | PLAUSIBLE, no ejecutado | R12 |

---

## 5. Mis propios errores en esta sesión

Se listan porque indican **qué tipo de error buscar** en este trabajo. Los tres son de
instrumento, no de sistema, y los tres se detectaron antes de reportar — pero el patrón
importa.

1. **Oráculo zombie (R11).** `os.kill(pid, 0)` tiene éxito sobre un zombie, así que mi
   chequeo de "sigue vivo" dio un falso *"killpg tampoco alcanza al nieto"*. Si le
   hubiera creído, habría descartado el fix correcto y reportado el problema como
   irreparable.
2. **Colección que falla por `ImportError` (R9, repetido en R11).** El control negativo
   fallaba al importar, no por conducta: probaba que la función no existía, no que los
   tests atraparan el bug. Corregido con import diferido en ambos.
3. **Campo equivocado en la comparación de sellos (R12).** `bundle_hash` difiere corrida
   a corrida **por diseño** (es un sello de custodia por corrida); el identificador
   estable es `analysis_fingerprint`. Casi reporto "mis cambios rompen el sello".

Los tres salieron de preguntar *"¿este resultado es posible?"* antes de escribirlo.

---

## 6. Inventario reproducible

| Script | Qué mide | Contra el checkout anterior |
|--------|----------|-----------------------------|
| `scripts/redteam_round5_downgrade.py` | 12 vectores de degradación de esquema | 6 divergen |
| `scripts/redteam_round10_render_types.mjs` | 5 tipos × 27 campos en los renderizadores | 6 campos lanzan |
| `scripts/redteam_round11_process_tree.py` | timeout y shutdown del runner | exit 1 |

Informes por ronda: `docs/REDTEAM_ROUND5_DOWNGRADE.md`, `..._ROUND6_PERIMETER.md`,
`..._ROUND7_PAIRING.md`, `..._ROUND8_UI.md`, `..._ROUND9_EXPOSURE.md`,
`..._ROUND10_RENDER_TYPES.md`, `..._ROUND11_PROCESS_TREE.md`,
`..._ROUND12_SELF_AUDIT.md`.

Registros de bugs: **B-228 … B-241**, en `BUGS_HISTORICO.md` y `BUGS_HISTORICO_EN.md`.

---

## 7. Decisiones de formato pendientes — no aplicadas a propósito

Ninguna se tocó porque cambian el formato sellado o el contrato de cable, y ésa es una
decisión de la dueña del proyecto, no del auditor.

1. `integrity_hmac` sobre `bundle_hash` (R6).
2. `bundle_digest` dentro de la reasoning trace, para que el emparejamiento sea
   criptográfico y no declarativo (R7).
3. Clave HMAC a `--hmac-key-file` con permisos 0600 (R8).
4. Advertencia de bind no-loopback en la API Modo 5 (R9).
5. `num`/`den` como strings, para cerrar la divergencia `1.0` (R10-4).
6. Árbol de procesos en los `subprocess.run` de los módulos SIFT (R11).
7. `pidfd_open` para el residual de reutilización de pid (R12).
