# MACOS_MODULES_DESIGN — Diseño de handlers nativos macOS

**Fecha**: 2026-07-09
**Branch**: `claude/macos-modules-design-xk5ecq`
**Restore tag**: `pre-session-20260709-194058`
**Alcance**: investigación y diseño exclusivamente. **Cero código de producto tocado.**
**Módulos objetivo**: (1) Safari/Chrome history macOS, (2) plist parsing, (3) FSEvents,
(4) Spotlight metadata.

---

## 0. Resumen ejecutivo

De las cuatro familias objetivo, hoy solo Safari History está parcialmente cubierta por
`vigia/sift/macos_forensics.py`; plists solo en su subconjunto de persistencia
(LaunchAgents/Daemons + login items); FSEvents **ya implementado** (2026-07-10, `vigia/sift/fsevents_parser.py` +
`_analyze_fsevents`, ver §4); Spotlight aparece como marker (`.Spotlight-V100`,
`macos_forensics.py:103`) pero **no existe ningún método de análisis**; y Chrome-en-macOS
está **excluido explícitamente** (`macos_forensics.py:303-305`, `if "Safari" not in str(db): continue`).

El diseño correcto no es solo "añadir parsers": está condicionado por dos huecos
arquitectónicos ya documentados (B-052, `docs/AUDITORIA_MACOS_NARRATIVA.md`):

1. **Routing**: la evidencia macOS entra por la rama mobile-only del shim
   (`/sift_orchestrator.py:201-267`) y **nunca llega al AbductiveReasoner**.
2. **Granularidad**: `MacOSAnalysisResult.to_signal()` colapsa todos los hallazgos en
   **una** `SignalOutput` (`macos_forensics.py:142-233`). Con una sola señal:
   `n_artifacts=1` → cap 0.65 (`vigia_scorer.py:991-992`) y nunca MALICE
   (gate `n_arts >= 4 OR n_types >= 3`, `vigia_scorer.py:1047`).

Por tanto los cuatro handlers se diseñan como **dominios emisores de señal propia**
(patrón `to_signals()` por dominio, B-052-P2), cada uno con `evidence_type` canónico
distinto, de modo que un caso macOS multi-artefacto pueda satisfacer el gate Daubert de
corroboración sin tocar la matemática del scorer.

**Nota sobre la taxonomía solicitada** *(actualizada 2026-07-09)*: al momento de la
investigación original, `TAXA_DOMINIOS_RECOLECCION.md` no existía en este clon (estaba
solo en la rama `float-census-atomic-writes-dsv61x`, nunca mergeada). Fue recuperado a
`docs/TAXA_DOMINIOS_RECOLECCION.md` (commit `7a86ce1`) junto con R4-3, que implementa
esa taxonomía en `_DOMAIN_MAP` / `classify_domain_subband()` (`caie.py`). **La
verificación de este diseño contra la taxonomía v2 está en §9.** Las demás taxonomías
vigentes contra las que se mapeó originalmente:

- `EVIDENCE_PROFILES` — registro canónico de `evidence_type` (spoofability, base_weight):
  `vigia/tools/caie.py:246-336`.
- Registro de rol epistémico (B-070): `device` / `contextual` / `narrative`,
  `vigia/tools/caie.py:366-387`.
- Familias `corr_group` (dominio informal de artefacto): `browser_suspicious`,
  `quarantine_suspicious`, `antiforensic`, `persistence`, `encrypted_apps`
  (`macos_forensics.py`, discutido como semilla del split por dominio en
  `docs/AUDITORIA_MACOS_NARRATIVA.md` §3 y `BUGS_PENDIENTES.md` B-052).

Si `TAXA_DOMINIOS_RECOLECCION.md` existe fuera del repo, debe incorporarse y este
documento re-mapearse contra ella antes de implementar.

---

## 1. Contexto arquitectónico (estado actual verificado)

### 1.1 Cómo se enruta la evidencia macOS hoy

- `vigia_agent.py:1386-1525` (`_build_orchestrator_kwargs`): detección por conjunto de
  marker files. `_MACOS_MARKER_FILES` (`macos_forensics.py:89-108`) ya incluye las
  cuatro familias (`History.db`, plists, `.fseventsd`, `.Spotlight-V100`) más
  `knowledgeC.db`, `TCC.db`, QuarantineEventsV2. Guard de colisión iOS:
  `all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES)` → `macos_evidence_path`
  (`vigia_agent.py:1494-1498`).
- Shim `/sift_orchestrator.py:490-516`: `MacOSForensicsAnalyzer().analyze(path)` →
  `result.to_signal()` → **una** señal `signal_class="primary"`.
- Artefacto **sin handler nativo**: no se enruta y no genera señal alguna (silencio).
  Solo si un engine emparejado *falla* se emite `{ENGINE}_UNANALYZED` con z=0
  (`vigia/sift/sift_orchestrator.py:323-343`). No hay ruta genérica de entropía.
  Consecuencia: hoy un `.fseventsd` o un `store.db` presentes en la evidencia
  **desaparecen del bundle sin rastro** — contradice la degradación honesta (§5.3).

### 1.2 Cómo se tipifica la señal aguas abajo

- `to_signal()` actual emite `metadata["artifact_type"]="macos_forensic"`
  (`macos_forensics.py:226`).
- `vigia/core/forensic_adapter.py`: `_LAYER_MAP["macos_forensic"]=DISK_MFT` (`:91`) y
  `_EVIDENCE_MAP["macos_forensic"]="app_data"` (`:130`, comentado como placeholder
  "hasta que B-052-P2 tipifique por hallazgo").
- Resultado: todo macOS puntúa como `app_data` (spoof 0.50 / weight 0.22), un solo tipo,
  un solo artefacto → techo estructural en SUSPICION.

### 1.3 El patrón de módulo canónico (plantilla a seguir)

La plantilla vigente es el patrón mobile/macOS (`ios_forensics.py` /
`macos_forensics.py`), que es la evolución del patrón de los módulos Windows
(`browser_forensics.py`, `prefetch_analyzer.py`, `shellbag_analyzer.py`,
`amcache_shimcache.py`). Invariantes compartidos:

| Elemento | Convención | Referencia |
|---|---|---|
| Constantes | `TOOL_NAME` (str mayúsculas), `ARTIFACT_RELIABILITY` (`Fraction`) | `macos_forensics.py:34-35` |
| Finding | `@dataclass(frozen=True)` con `severity: Fraction`, `mitre_technique`, `rule_ref`, `timestamp: int`, `corr_group: str` | `macos_forensics.py:115-124` |
| Result | dataclass mutable con contadores, `findings`, `composite_score: Fraction`, `analysis_notes` | `macos_forensics.py:127-140` |
| `analyze()` | `analyze(self, evidence_path, chain: Optional[ChainOfCustody] = None, timestamp_utc: str = "1970-01-01T00:00:00Z")` | `browser_forensics.py:114-119`, `macos_forensics.py:257` |
| Descubrimiento | `_safe_rglob` (heapq.nsmallest, filtra symlinks, O(limit) memoria, orden determinista) | `macos_forensics.py:374-390` |
| SQLite | `safe_sqlite_connect(db, TAG, logger)` — copia DB + sidecars `-wal/-shm/-journal` a workdir efímero y aplica el WAL (B-071). **Nunca** el `_connect_ro` legacy de browser_forensics (`mode=ro&immutable=1` ignora el WAL, `_sql_utils.py:13-15`) | `vigia/sift/_sql_utils.py:57-93` |
| plist | `_safe_plist_load` con techo `_PLIST_MAX_BYTES = 8 MiB` (S5) | `macos_forensics.py:844-863` |
| composite | `noisy_or_correlated([f.severity...], build_correlation_groups([f.corr_group...]), Fraction(15,100))` | `macos_forensics.py:360-368`, `_math_utils.py:219-287` |
| to_signal | escalera z en `Fraction` (múltiplos de 1/10), `conf = min(composite*11/10, 95/100)`, cast a float SOLO en el constructor `SignalOutput` | `macos_forensics.py:142-233` |
| Metadata mínima | `artifact_type`, `artifact_reliability=str(...)`, `chains`, `composite_score=str(...)`, `finding_types` ordenado | `macos_forensics.py:216-232` |

Contrato `SignalOutput` (`vigia/core/ebs_v1.py`): `value/z_score/confidence` float
finitos (fail-closed B-083), `z_score` clipped a ±`Z_CLIP_MAX=5.0`, `confidence`
clampada [0,1]. Tests de determinismo que los nuevos módulos deben pasar:
`tests/test_b042_b043_mobile_determinism.py` exige que `z_score` reconstruya exacto vía
`Fraction(str(z))` y sea múltiplo de 1/10, y que `value = float(z/5)` sea múltiplo de
1/50. Todo el camino de verdicto en `Fraction`; float solo en la frontera.

### 1.4 Gates que el diseño debe satisfacer

- **Cap mono-fuente**: `n_artifacts < 2 → final_score ≤ 0.65` (`vigia_scorer.py:991-992`).
- **Gate MALICE**: `final_score > 0.33` requiere `n_arts >= 4 OR n_types >= 3` contando
  solo artefactos con señal, `evidence_role == device`, no contextuales
  (`vigia_scorer.py:1017-1058`).
- **AbductiveReasoner**: requiere ≥3 señales primarias (`abductive_reasoner.py:90-91`)
  y `layer_map` resoluble por `artifact_type` — hoy los dominios macOS no están en el
  `layer_map` del reasoner.

**Decisión de diseño derivada**: los 4 handlers emiten señales separadas con
`artifact_type` y `evidence_type` propios (patrón `to_signals()`), de modo que un caso
macOS rico produzca 3-5 señales device de tipos distintos. Esto ES B-052-P2, y hereda su
advertencia: *"no tocar sin re-ejecutar el corpus — cambia el resultado de todos los
verdictos mobile"* (`docs/AUDITORIA_MACOS_NARRATIVA.md` §4).

---

## 2. Módulo 1 — Safari/Chrome history (macOS)

### 2.1 Formato del artefacto real

**Safari** — `~/Library/Safari/History.db` (SQLite 3, WAL activado):

- `history_items(id, url, domain_expansion, visit_count, daily_visit_counts BLOB, …)`
- `history_visits(id, history_item → history_items.id, visit_time REAL, title,
  load_successful, redirect_source, redirect_destination, origin, …)`
  - `visit_time`: **Core Data epoch** (segundos desde 2001-01-01 UTC; offset
    `978307200`, ya implementado: `_coredata_to_unix`, `macos_forensics.py:397-409`).
  - `origin`: 0 = visita local, 1 = sincronizada de iCloud (relevante para atribución
    de dispositivo — una visita `origin=1` NO prueba actividad en esta máquina).
  - `redirect_source/destination`: distingue navegación deliberada de redirección
    (Peirce: Secondness — el mismo URL con redirect_source poblado es un signo distinto).
- **Sidecar crítico**: `History.db-wal`. Verificado sobre el corpus (§6): en
  `cases/tuck-2019-macos` el WAL de 4 MB contiene **~48 URLs y ~68 visitas** que no
  están en el DB principal. `safe_sqlite_connect` ya copia y aplica el WAL — la ruta
  nativa lo resuelve gratis; la ruta actual del bundle (strings) no.
- Satélites en el mismo directorio: `Bookmarks.plist` (bplist, árbol
  `Children[]`/`WebBookmarkType`), `LastSession.plist` (bplist NSKeyedArchiver),
  `TopSites.plist`, `Downloads.plist` (Safari antiguos), `CloudTabs.db` (SQLite).

**Chrome/Chromium (incl. Brave/Edge)** —
`~/Library/Application Support/Google/Chrome/<Profile>/History` (SQLite, **sin
extensión**; Brave: `BraveSoftware/Brave-Browser/...`):

- `urls(id, url, title, visit_count, typed_count, last_visit_time, hidden)`
- `visits(id, url → urls.id, visit_time, from_visit, transition, visit_duration)`
  - `transition & 0xFF`: 0=LINK, 1=TYPED, 2=AUTO_BOOKMARK, 5=START_PAGE, 6=FORM_SUBMIT,
    7=RELOAD, 8=KEYWORD… `TYPED` = navegación deliberada (señal de intención de primer
    orden; los módulos actuales no lo explotan).
- `downloads(id, target_path, tab_url, total_bytes, danger_type, opened, start_time,
  end_time, …)` + `downloads_url_chains(id, chain_index, url)`
- `keyword_search_terms(keyword_id, url_id, term, normalized_term)` — **búsquedas
  tecleadas literales**, el artefacto de intencionalidad más denso del navegador.
- Timestamps: **WebKit epoch** (microsegundos desde 1601-01-01 UTC, offset
  11644473600 s). Helper determinista ya existente y auditado (P0-001 §5.4, división
  entera, nunca float): `_chrome_ts_to_unix`, `vigia/sift/android_forensics.py:344-359`
  — extraer a `_math_utils` o duplicar con la misma disciplina.

### 2.2 Herramientas de parseo existentes en Python

| Opción | Estado | Veredicto |
|---|---|---|
| `sqlite3` stdlib + `safe_sqlite_connect` (B-071) | ya en repo | **Elegida.** Cubre Safari y Chrome, aplica WAL, cero dependencias |
| `_analyze_safari` existente (`macos_forensics.py:569-657`) | parcial | Reutilizar: añadir `origin`, redirects, y el hecho de que el WAL ya se aplica |
| `browser_forensics._parse_chromium` (`browser_forensics.py:208-251`) | Windows | Reutilizable como referencia de queries (`downloads`+`downloads_url_chains`+`urls`), pero: usa `_connect_ro` legacy (ignora WAL), no lee `visits` ni `keyword_search_terms`, no convierte timestamps, y su catálogo de extensiones es Windows-céntrico (`.exe/.dll/.ps1`) — para macOS: `.dmg`, `.pkg`, `.app`, `.sh`, `.command`, Mach-O |
| `_chrome_ts_to_unix` (`android_forensics.py:344`) | ya en repo | Reutilizar tal cual |

No se necesita ninguna dependencia externa.

### 2.3 evidence_type y dominio de recolección

| Campo | Valor propuesto | Justificación |
|---|---|---|
| `artifact_type` (señal) | `macos_browser` | nuevo, por dominio (B-052-P2); alta en `_LAYER_MAP` → `DISK_MFT` y en el `layer_map` del reasoner |
| `evidence_type` canónico | **`web_search`** (spoof 0.45 / weight 0.24, `caie.py:299`) | tipo canónico ya calibrado para historial/búsquedas (lo usa la vía mobile); evita el colapso actual a `app_data` y el `log_entry` (0.85) al que cae el browser Windows |
| Rol epistémico | `device` (default B-070) | cuenta para el gate MALICE |
| `corr_group` | `browser_suspicious` (existente) + `antiforensic` para búsquedas de borrado | familias ya definidas en el módulo |
| Dominio de recolección (TAXA v2) | `web_search` **sin entrada en `_DOMAIN_MAP`** → `UNKNOWN:web_search`; dominio correcto por modo de fabricación: **D3** | ver §9.1 — gap pre-existente de toda la banda mobile |

### 2.4 Esqueleto de `to_signal()`

```python
TOOL_NAME = "MACOS_BROWSER"
ARTIFACT_RELIABILITY = Fraction(65, 100)   # igual que BROWSER_FORENSICS (Windows)

@dataclass(frozen=True)
class MacOSBrowserFinding:
    finding_type: str          # SAFARI_* | CHROME_* | BROWSER_ANTIFORENSIC_SEARCH ...
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""       # "browser_suspicious" | "antiforensic"

@dataclass
class MacOSBrowserResult:
    source_path: str = ""
    browser: str = ""                      # "safari" | "chrome" | "brave" | ...
    total_history_entries: int = 0
    total_typed_visits: int = 0            # Chrome transition TYPED
    total_search_terms: int = 0            # keyword_search_terms
    wal_applied: bool = False              # honestidad: el WAL entró al análisis
    icloud_synced_hits: int = 0            # Safari origin=1 (atribución degradada)
    findings: List[MacOSBrowserFinding] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        has_exploit = any(f.finding_type.endswith("_EXPLOIT_RESEARCH") for f in self.findings)
        has_antiforensic = any(f.corr_group == "antiforensic" for f in self.findings)
        n_susp = sum(1 for f in self.findings if f.corr_group == "browser_suspicious")
        has_typed_susp = any(                       # navegación DELIBERADA a hallazgo
            f.finding_type == "CHROME_TYPED_SUSPICIOUS" for f in self.findings)

        # Escalera z — múltiplos de 1/10 (test_b042_b043), sin floats
        if has_exploit and has_antiforensic:
            z = Fraction(38, 10)
        elif has_exploit:
            z = Fraction(35, 10)
        elif has_antiforensic and n_susp >= 3:
            z = Fraction(30, 10)
        elif has_typed_susp:                        # typed_count>0 = Thirdness fuerte
            z = Fraction(26, 10)
        elif n_susp >= 3:
            z = Fraction(22, 10)
        elif n_susp >= 1:
            z = Fraction(16, 10)
        elif self.findings:
            z = Fraction(12, 10)

        z = min(z, Fraction(int(Z_CLIP_MAX), 1))
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip),
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "artifact_type": "macos_browser",
                "evidence_type": "web_search",          # tipificación B-052-P2
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "browser": self.browser,
                "total_history_entries": self.total_history_entries,
                "total_typed_visits": self.total_typed_visits,
                "total_search_terms": self.total_search_terms,
                "wal_applied": self.wal_applied,
                "icloud_synced_hits": self.icloud_synced_hits,
                "composite_score": str(self.composite_score),
                "findings_count": len(self.findings),
                "finding_types": sorted({f.finding_type for f in self.findings}),
            },
        )
```

Notas de diseño:
- Una señal **por navegador** encontrado (Safari y Chrome del mismo usuario = 2 señales
  del mismo `evidence_type`; suman a `n_arts`, no a `n_types` — correcto: son la misma
  clase de evidencia).
- `icloud_synced_hits` alimenta el devil_advocate automáticamente: hallazgos con
  `origin=1` no prueban actividad local.
- Los catálogos `SUSPICIOUS_SEARCH_PATTERNS` / `ANTIFORENSIC_SEARCH_PATTERNS` existentes
  (`macos_forensics.py:64-86`) se comparten sin cambios.

---

## 3. Módulo 2 — plist parsing

### 3.1 Formato del artefacto real

Tres sub-formatos, todos con extensión `.plist` (o ninguna):

1. **XML plist** (`<?xml` + `<!DOCTYPE plist`): texto, `plistlib` directo.
2. **Binary plist** (`bplist00`): binario con tabla de offsets; `plistlib` lo
   autodetecta desde Python 3.4. (Variantes `bplist15/16` de streaming son internas de
   Apple y no aparecen en artefactos de disco relevantes — si se detectan, degradación
   honesta.)
3. **NSKeyedArchiver** (bplist con `$archiver="NSKeyedArchiver"`, `$objects[]`, `$top`):
   grafo de objetos serializado con referencias `plistlib.UID`. `plistlib` lo carga pero
   devuelve el grafo crudo; hay que **desreferenciar UIDs** para reconstruir el objeto.
   Artefactos que lo usan: `LastSession.plist`, los `*.sfl2` de recent items
   (`~/Library/Application Support/com.apple.sharedfilelist/*.sfl2`, macOS 10.13+),
   `com.apple.spotlight.Shortcuts`.

Cobertura actual vs objetivo:

| Artefacto | Hoy | Objetivo |
|---|---|---|
| LaunchAgents/LaunchDaemons | ✅ `_analyze_launch_plists` (`:865-948`) | mantener |
| `com.apple.loginitems.plist` | ✅ `_analyze_loginitems_plists` (`:950-983`) | mantener |
| `SystemVersion.plist`, `nvram.plist` (SIP) | ✅ | mantener |
| `Bookmarks.plist` / `LastSession.plist` (Safari) | ❌ (en el corpus quedaron QUARANTINED, ver §6) | bplist plano + NSKeyedArchiver |
| Recent items `*.sfl2` | ❌ | NSKeyedArchiver → rutas de documentos recientes |
| `com.apple.TimeMachine.plist` | ❌ | **exclusiones de backup = anti-forense** (T1490-adyacente) |
| `com.apple.Bluetooth.plist`, `com.apple.airport.preferences.plist` | ❌ | dispositivos emparejados / redes conocidas (correlación) |
| `com.apple.finder.plist` (FXRecentFolders), `com.apple.sidebarlists.plist` | ❌ | huella de actividad |

### 3.2 Herramientas de parseo existentes en Python

| Opción | Estado | Veredicto |
|---|---|---|
| `plistlib` stdlib | ya usado (`_safe_plist_load`, techo 8 MiB S5) | **Elegida** para XML/bplist planos |
| Desreferenciador NSKeyedArchiver propio (~60 líneas sobre `plistlib.UID`, con guard de ciclos y profundidad máxima) | no existe | **Elegida** — determinista, Apache-2.0, sin deps |
| `nska_deserialize` / `ccl_bplist` (pip) | no en requirements | Descartada: dependencia externa evitable; el subconjunto necesario (SFL2, LastSession) es pequeño |

### 3.3 evidence_type y dominio de recolección

El dominio plist es heterogéneo; se parte en **dos señales** con tipos canónicos
distintos (esto es lo que permite `n_types >= 3` en un caso macOS completo):

| Sub-dominio | artifact_type | evidence_type canónico | corr_group |
|---|---|---|---|
| Persistencia (LaunchAgents/Daemons, login items) | `macos_plist_persistence` | **`registry_key`** (0.55/0.20, `caie.py:258`) — análogo funcional exacto de las Run keys de Windows: config de arranque escribible por el usuario/root | `persistence` |
| Actividad/configuración (recent items, bookmarks, session, TimeMachine, Bluetooth, WiFi) | `macos_plist_activity` | **`file_metadata`** (0.65/0.20, `caie.py:288`) | `plist_activity` (nuevo) / `antiforensic` para exclusiones TimeMachine |

Ambos rol `device`. Alternativa considerada y descartada por ahora: crear
`plist_config` como evidence_type nuevo en `EVIDENCE_PROFILES` — requiere calibración de
spoofability/weight con corpus; reutilizar tipos calibrados es el camino sin riesgo
(misma decisión que tomó B-060/B-070 al mapear a `app_data`, pero con granularidad).

Dominio de recolección (TAXA v2): ambos sub-dominios caen en **D3
`filesystem_metadata`** — `registry_key` y `file_metadata` están mapeados
explícitamente a D3 en `_DOMAIN_MAP` y en TAXA §4. Verificación en §9.1 (✅ coherente).

### 3.4 Esqueleto de `to_signal()` (señal de persistencia; la de actividad es isomorfa)

```python
TOOL_NAME = "MACOS_PLIST"
ARTIFACT_RELIABILITY = Fraction(70, 100)

@dataclass(frozen=True)
class PlistFinding:
    finding_type: str          # PERSISTENCE_* | TIMEMACHINE_EXCLUSION | RECENT_ITEM_SUSP ...
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str       # T1543.001 launchd, T1547.015 login items, T1490 TM
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""

@dataclass
class PlistPersistenceResult:
    source_path: str = ""
    total_launch_jobs: int = 0
    total_login_items: int = 0
    nska_parse_failures: int = 0          # honestidad: NSKeyedArchiver no desreferenciado
    findings: List[PlistFinding] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        has_hidden_exe = any(
            f.finding_type == "PERSISTENCE_SUSPICIOUS_LAUNCHAGENT" for f in self.findings)
        has_hidden_login = any(
            f.finding_type == "PERSISTENCE_HIDDEN_LOGIN_ITEM" for f in self.findings)
        has_tm_exclusion = any(
            f.finding_type == "TIMEMACHINE_EXCLUSION_SUSP" for f in self.findings)
        n_resilient = sum(
            1 for f in self.findings
            if f.finding_type == "PERSISTENCE_RESILIENT_LAUNCHAGENT")

        if has_hidden_exe and has_tm_exclusion:      # persistencia + anti-backup
            z = Fraction(34, 10)
        elif has_hidden_exe:
            z = Fraction(28, 10)
        elif has_hidden_login and n_resilient >= 1:
            z = Fraction(24, 10)
        elif has_tm_exclusion:
            z = Fraction(20, 10)
        elif has_hidden_login or n_resilient >= 2:
            z = Fraction(18, 10)
        elif self.findings:
            z = Fraction(12, 10)

        z = min(z, Fraction(int(Z_CLIP_MAX), 1))
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip),
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "artifact_type": "macos_plist_persistence",
                "evidence_type": "registry_key",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "total_launch_jobs": self.total_launch_jobs,
                "total_login_items": self.total_login_items,
                "nska_parse_failures": self.nska_parse_failures,
                "composite_score": str(self.composite_score),
                "findings_count": len(self.findings),
                "finding_types": sorted({f.finding_type for f in self.findings}),
            },
        )
```

La lógica de detección de LaunchAgents ya existe y se **migra** (no se duplica) desde
`_analyze_launch_plists` / `_analyze_loginitems_plists`.

---

## 4. Módulo 3 — FSEvents

> **ESTADO: IMPLEMENTADO (2026-07-10).** Parser autocontenido en
> `vigia/sift/fsevents_parser.py` (DLS1/DLS2, gzip, techo S5, degradación
> honesta ante DLS3/corrupción) cableado en `macos_forensics._analyze_fsevents`.
> Detecciones: borrado masivo (`ANTIFORENSIC_FSEVENTS_MASS_DELETION`,
> T1070.004), purga de papelera (`ANTIFORENSIC_FSEVENTS_TRASH_PURGE`, T1485),
> rutas sospechosas (`FSEVENTS_SUSPICIOUS_PATH`, T1564). Los dos primeros usan
> corr_group `antiforensic` (listos como dominio B-052-P2). NO se implementa
> detección de gap por secuencia de event_id (los IDs no son contiguos — sería
> overclaim). 18 tests (`test_fsevents_parser.py`), 0 flips de corpus (0 casos
> macOS rutean al engine), tuck-2019 sin cambio (no tiene `.fseventsd`).
> **Nota de calibración pendiente (doctrina, no incluida):** un borrado masivo
> FSEvents standalone queda en z=1.2 en la escalera agregada actual (mismo
> trato que `ANTIFORENSIC_QUARANTINE_EMPTY`); darle una rama propia es una
> decisión de recalibración acoplada a B-052-P2, no tomada aquí.


### 4.1 Formato del artefacto real

- Ubicación: `/.fseventsd/` en la **raíz de cada volumen** (incluidos USB/externos —
  un `.fseventsd` de un pendrive registra actividad de esa unidad en otras máquinas).
- Contenido: archivos gzip cuyo nombre son 16 dígitos hex (event stream ID) +
  `fseventsd-uuid` (UUID del store; cambia si el volumen se reformatea — señal en sí).
- Al descomprimir, páginas con magic:
  - `DLS1` — V1 (≤ macOS 10.12): registro = ruta completa null-terminated (sin `/`
    inicial) + `event_id` uint64 LE + `flags` uint32 LE.
  - `DLS2` — V2 (10.13+): añade `node_id` uint64 LE (número de inodo/CNID) al registro.
  - `DLS3` — V3 (observado en macOS recientes): variante con campo adicional; el parser
    debe **sniffear el magic y degradar honesto** (`analysis_notes` + señal
    `unanalyzed`) ante versiones no soportadas, nunca adivinar el layout.
- `flags` es un bitmask **no documentado por Apple** (ingeniería inversa de la
  comunidad DFIR; mapeo de referencia: FSEventsParser de G-C Partners). Bits relevantes:
  `Created`, `Removed`, `Renamed`, `Modified`, `InodeMetaMod`, `FinderInfoMod`,
  `XattrModified/Removed`, `HardLink/SymbolicLink`, `ItemCloned`, `FolderCreated`,
  `Mount/Unmount`, `EndOfTransaction`. **Nota Daubert**: el reporte debe citar el mapeo
  como derivado de ingeniería inversa reproducible, no como especificación del vendor.
- **Sin timestamp por registro.** El tiempo solo se acota por rango (mtime del archivo
  de log, eventos Mount/Unmount, correlación con otros artefactos). Los findings de
  FSEvents deben emitir `timestamp=0` + rango en `evidence`, y la corroboración
  temporal viene de cruzar con Safari/quarantine (regla 3 del protocolo de
  verificación: anomalía de timeline exige segunda fuente).

Valor forense (señales de intencionalidad):
- **Clusters de `Removed`** sobre rutas de usuario en ventana estrecha = borrado masivo.
- Actividad `.Trash` / `.Trashes` seguida de vaciado.
- Eventos sobre `/private/tmp`, `/Users/Shared`, rutas ocultas (`/.`).
- **Hueco en la secuencia de event IDs** o `.fseventsd` casi vacío en un volumen con
  actividad = purga del journal (análogo exacto de `usn_journal_gap`; MITRE T1070.004).
- Presencia de nombres de herramientas anti-forenses en rutas (srm, bleachbit, CleanMyMac).

### 4.2 Herramientas de parseo existentes en Python

| Opción | Licencia | Veredicto |
|---|---|---|
| Parser propio mínimo: `gzip` + `struct` stdlib (~150-200 líneas: walk de páginas DLS1/DLS2, registros, bitmask) | Apache-2.0 (propio) | **Elegida.** Formato simple, determinista, sin deps, techo de tamaño tipo S5 |
| `dlcowen/FSEventsParser` | **GPLv3** | Descartada como dependencia/copia (incompatible con Apache-2.0 del repo); útil solo como oráculo de validación cruzada en tests |
| `mac_apt` (módulo fsevents) | MIT | Compatible como referencia de layout; no como dependencia (arrastra framework entero) |
| `plaso` (parser fseventsd) | Apache-2.0 | Referencia limpia de formato, licencia compatible; no importar plaso completo |

### 4.3 evidence_type y dominio de recolección

| Campo | Valor propuesto | Justificación |
|---|---|---|
| `artifact_type` | `macos_fsevents` | nuevo dominio |
| `evidence_type` | **`usn_journal`** (spoof 0.20 / weight 0.30, `caie.py:261`) — análogo funcional directo: journal de filesystem, binario, requiere root para manipular | actividad normal |
| `evidence_type` para huecos/purga | **`usn_journal_gap`** (spoof 0.10 / weight 0.38, `caie.py:285`) | la purga es más difícil de fabricar que de ejecutar; ya calibrado |
| Rol | `device` | — |
| `corr_group` | `fsevents_activity` (nuevo) para clusters; `antiforensic` para purga/gaps | la purga debe correlacionar con SIP/quarantine-empty existentes |
| Dominio de recolección (TAXA v2) | **D3 `filesystem_metadata`** — `usn_journal` y `usn_journal_gap` mapeados explícitamente a D3 (TAXA §4 y `_DOMAIN_MAP`) | ver §9.1 (✅ coherente); ambos son "duros" (spoof ≤0.30) → rama hard-mass del gate |

Invariante 6 de CLAUDE.md aplica directamente: la purga del journal es fractura CAIE y
**sube** el peso MALICE, no es ruido.

### 4.4 Esqueleto de `to_signal()`

```python
TOOL_NAME = "MACOS_FSEVENTS"
ARTIFACT_RELIABILITY = Fraction(75, 100)   # journal de kernel: más fiable que app data

@dataclass(frozen=True)
class FSEventsFinding:
    finding_type: str          # FSEVENTS_MASS_DELETION | FSEVENTS_TRASH_PURGE |
                               # FSEVENTS_JOURNAL_GAP | FSEVENTS_STORE_RESET |
                               # FSEVENTS_SUSPICIOUS_PATH | FSEVENTS_UNSUPPORTED_VERSION
    severity: Fraction
    description: str
    evidence: str              # incluye rango de event IDs y ventana temporal acotada
    mitre_technique: str       # T1070.004, T1485
    rule_ref: str
    timestamp: int = 0         # SIN timestamp por registro — siempre 0 + rango en evidence
    corr_group: str = ""

@dataclass
class FSEventsResult:
    source_path: str = ""
    volumes_seen: int = 0
    total_records: int = 0
    total_files_parsed: int = 0
    unsupported_pages: int = 0            # DLS3/desconocido — degradación honesta
    store_uuid: str = ""
    findings: List[FSEventsFinding] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        has_gap = any(f.finding_type == "FSEVENTS_JOURNAL_GAP" for f in self.findings)
        has_store_reset = any(f.finding_type == "FSEVENTS_STORE_RESET" for f in self.findings)
        n_mass_del = sum(1 for f in self.findings
                         if f.finding_type == "FSEVENTS_MASS_DELETION")
        has_trash_purge = any(f.finding_type == "FSEVENTS_TRASH_PURGE" for f in self.findings)

        if has_gap and n_mass_del >= 1:            # purga + borrado = ocultar que ocultas
            z = Fraction(36, 10)
        elif has_gap or has_store_reset:
            z = Fraction(28, 10)
        elif n_mass_del >= 2:
            z = Fraction(26, 10)
        elif n_mass_del == 1 and has_trash_purge:
            z = Fraction(24, 10)
        elif n_mass_del == 1 or has_trash_purge:
            z = Fraction(18, 10)
        elif self.findings:
            z = Fraction(12, 10)

        z = min(z, Fraction(int(Z_CLIP_MAX), 1))
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip),
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "artifact_type": "macos_fsevents",
                # gap/purga presente → el tipo dominante del dominio es el gap
                "evidence_type": "usn_journal_gap" if (has_gap or has_store_reset)
                                 else "usn_journal",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "volumes_seen": self.volumes_seen,
                "total_records": self.total_records,
                "unsupported_pages": self.unsupported_pages,
                "store_uuid": self.store_uuid,
                "composite_score": str(self.composite_score),
                "findings_count": len(self.findings),
                "finding_types": sorted({f.finding_type for f in self.findings}),
            },
        )
```

Nota: el umbral de "cluster de borrado masivo" (N archivos / ventana) es un parámetro de
calibración con corpus — dejarlo como constante `Fraction`/int de módulo documentada,
nunca mágica inline.

---

## 5. Módulo 4 — Spotlight metadata

### 5.1 Formato del artefacto real

Dos capas con costes radicalmente distintos:

1. **`store.db` / `.store.db`** — `/.Spotlight-V100/Store-V2/<UUID>/` por volumen, y
   nivel usuario en `~/Library/Metadata/CoreSpotlight/index.spotlightV3/` (10.13+).
   Formato binario **propietario y no documentado**: bloques comprimidos (zlib/LZ4
   según versión), tablas de propiedades, registros por inodo con atributos `kMDItem*`
   codificados con varints. Valor forense: `kMDItemLastUsedDate`, `kMDItemUseCount`,
   `kMDItemWhereFroms` (**URL de origen de descarga**), `kMDItemDownloadedDate`,
   `kMDItemContentTypeTree`, nombre y parent-inode — incluye **residuo de archivos ya
   borrados** cuyo registro no se ha compactado. Complejidad de parser: alta
   (miles de líneas; múltiples versiones de formato entre 10.13 y macOS 14+).
2. **`com.apple.spotlight.Shortcuts`** (plist, nivel usuario; en versiones nuevas
   `com.apple.spotlight.Shortcuts.v3`) — mapa de **consultas tecleadas por el usuario**
   → app/resultado lanzado + timestamp. Es el equivalente Spotlight de
   `keyword_search_terms`: intención de usuario pura, coste de parseo trivial
   (plistlib, sub-formato NSKeyedArchiver en algunas versiones).

### 5.2 Herramientas de parseo existentes en Python

| Opción | Licencia | Veredicto |
|---|---|---|
| `spotlight_parser` (Yogesh Khatri) | MIT | Único parser Python maduro y standalone de `store.db`. MIT es compatible con Apache-2.0. Candidato a **vendor/opcional** en Fase 2 |
| `mac_apt` (usa spotlight_parser internamente) | MIT | framework completo; no como dependencia |
| `plaso` (`spotlight_storedb`) | Apache-2.0 | referencia de formato compatible |
| Parser propio | — | **Descartado para store.db**: el coste/riesgo de un formato no documentado multi-versión no se justifica; violaría la regla de honestidad si se hace a medias |
| `plistlib` para Shortcuts | stdlib | **Elegida para Fase 1** |

**Diseño en dos fases (degradación honesta):**
- **Fase 1** (sin dependencias): parsear Shortcuts; para `store.db` detectar presencia,
  hashear, registrar tamaño/UUID/mtimes y emitir señal con
  `metadata["unanalyzed"]=True` y nota explícita — visible en el bundle, no puntúa.
  Exactamente el contrato de `_unanalyzed_signal` (§1.1), pero emitido de forma
  proactiva en vez de silencio.
- **Fase 2** (dependencia opcional gated por `VIGIA_SPOTLIGHT_STOREDB_ENABLED`):
  integración de `spotlight_parser` como enrichment (mismo patrón que los módulos
  opcionales del MCP: presente → se registra; ausente → limitación documentada).

### 5.3 evidence_type y dominio de recolección

| Sub-artefacto | artifact_type | evidence_type canónico | corr_group |
|---|---|---|---|
| Shortcuts (búsquedas tecleadas) | `macos_spotlight` | **`web_search`** (0.45/0.24) — semánticamente es búsqueda deliberada de usuario, igual que el historial; alternativa conservadora: `app_data` (0.50/0.22) | `spotlight_intent` (nuevo) o `browser_suspicious` si matchea los mismos patrones |
| store.db (metadatos por inodo, Fase 2) | `macos_spotlight` | **`file_metadata`** (0.65/0.20, `caie.py:288`) | `spotlight_metadata` |
| Índice deshabilitado/purgado (`mdutil -E`/`-i off` residual, store vacío en volumen activo) | `macos_spotlight` | `file_metadata` con finding `antiforensic` | `antiforensic` |

Decisión a validar en calibración: si Shortcuts emite como `web_search`, un caso
Safari+Spotlight produce 2 señales del mismo tipo (suma `n_arts`, no `n_types`). Si se
prefiere maximizar `n_types`, usar `app_data` para Shortcuts. Recomendación: `app_data`
(más conservador en spoofability y diversifica tipos).

Dominio de recolección (TAXA v2): `file_metadata` (store.db) → **D3** explícito
(✅ coherente); `app_data` (Shortcuts) → **sin entrada en `_DOMAIN_MAP`**
(`UNKNOWN:app_data`), mismo gap de banda mobile que `web_search` — dominio correcto por
modo de fabricación: **D3**. Ver §9.1.

### 5.4 Esqueleto de `to_signal()`

```python
TOOL_NAME = "MACOS_SPOTLIGHT"
ARTIFACT_RELIABILITY = Fraction(70, 100)

@dataclass(frozen=True)
class SpotlightFinding:
    finding_type: str          # SPOTLIGHT_SUSPICIOUS_QUERY | SPOTLIGHT_ANTIFORENSIC_QUERY |
                               # SPOTLIGHT_INDEX_DISABLED | SPOTLIGHT_DELETED_FILE_RESIDUE |
                               # SPOTLIGHT_WHEREFROM_SUSPICIOUS
    severity: Fraction
    description: str
    evidence: str
    mitre_technique: str       # T1083, T1070.004 (index purge), T1105 (wherefroms)
    rule_ref: str
    timestamp: int = 0
    corr_group: str = ""

@dataclass
class SpotlightResult:
    source_path: str = ""
    total_shortcuts: int = 0
    storedb_present: bool = False
    storedb_parsed: bool = False           # False en Fase 1 — honestidad estructural
    storedb_sha256: str = ""
    total_metadata_records: int = 0        # Fase 2
    findings: List[SpotlightFinding] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        has_af_query = any(
            f.finding_type == "SPOTLIGHT_ANTIFORENSIC_QUERY" for f in self.findings)
        has_index_off = any(
            f.finding_type == "SPOTLIGHT_INDEX_DISABLED" for f in self.findings)
        n_susp_query = sum(1 for f in self.findings
                           if f.finding_type == "SPOTLIGHT_SUSPICIOUS_QUERY")
        has_residue = any(
            f.finding_type == "SPOTLIGHT_DELETED_FILE_RESIDUE" for f in self.findings)

        if has_index_off and (has_af_query or n_susp_query >= 1):
            z = Fraction(32, 10)
        elif has_af_query:
            z = Fraction(26, 10)
        elif has_index_off:
            z = Fraction(24, 10)
        elif has_residue and n_susp_query >= 1:
            z = Fraction(22, 10)
        elif n_susp_query >= 2:
            z = Fraction(20, 10)
        elif n_susp_query == 1 or has_residue:
            z = Fraction(16, 10)
        elif self.findings:
            z = Fraction(12, 10)

        z = min(z, Fraction(int(Z_CLIP_MAX), 1))
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        z_clip = Fraction(int(Z_CLIP_MAX), 1)
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z / z_clip),
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "artifact_type": "macos_spotlight",
                "evidence_type": "app_data",           # Shortcuts; store.db → file_metadata
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "total_shortcuts": self.total_shortcuts,
                "storedb_present": self.storedb_present,
                "storedb_parsed": self.storedb_parsed,
                "storedb_sha256": self.storedb_sha256,
                "unanalyzed": self.storedb_present and not self.storedb_parsed,
                "composite_score": str(self.composite_score),
                "findings_count": len(self.findings),
                "finding_types": sorted({f.finding_type for f in self.findings}),
            },
        )
```

---

## 6. Corpus: artefactos macOS presentes sin analizar

Búsqueda exhaustiva sobre `cases/`, `evidence/`, `data/`, `results/`, `resultados/`,
`reports/`: **`cases/tuck-2019-macos/` es el único directorio con artefactos macOS
reales en disco** en todo el repo. Toda otra mención macOS del corpus
(`data/cases/VIGIA-TUCK-2019.json`, VIGIA-GOOGLE-TAKEOUT-2020, casos iOS/Android) es
narrativa EBS, no artefacto parseable.

### 6.1 VIGIA-TUCK-2019-MACOS — inventario y huecos

| Archivo | Tamaño | Handler nativo hoy | Estado en el bundle sellado |
|---|---|---|---|
| `Safari/History.db` | 147 KB | ✅ capaz (`_analyze_safari`) | `QUARANTINED_BINARY_OK` — leído vía strings + SQLite externo, no parse nativo |
| `Safari/History.db-wal` | **4.099 KB** | ✅ solo vía `safe_sqlite_connect` (aplica WAL) | **solo strings** — nunca parseado estructuradamente |
| `Safari/History.db-shm` | 32 KB | sidecar | — |
| `Safari/Bookmarks.plist` | 50 KB (bplist) | ❌ `_analyze_plists` no lo cubre | `QUARANTINED_BPLIST_OK` |
| `Safari/LastSession.plist` | 85 B (bplist NSKeyedArchiver) | ❌ | `QUARANTINED_BPLIST_OK` |
| `Preferences/com.apple.LaunchServices.QuarantineEventsV2` | 20 KB | ✅ capaz (`_analyze_quarantine`) | leído vía SQLite externo |

**Hallazgo cuantificado (verificado en esta investigación, lectura read-only sobre
copia en scratchpad; originales intactos):**

- `History.db` abierto con `immutable=1` (WAL ignorado): **150 history_items / 196
  history_visits**.
- Con WAL aplicado: **198 history_items / 264 history_visits**.
- → **~48 URLs y ~68 visitas viven solo en el WAL no-checkpointeado** y no entraron al
  análisis estructurado del bundle sellado. Es el hueco de mayor valor inmediato del
  corpus: el módulo 1 (browser) lo cierra sin trabajo extra porque
  `safe_sqlite_connect` ya aplica sidecars.

Referenciados en la narrativa del caso pero **ausentes del disco** (nada que parsear):
Chrome history (el reporte F-003 lo infiere solo desde QuarantineEventsV2), Firefox,
FSEvents, Spotlight, KnowledgeC, TCC, SystemVersion.plist.

### 6.2 Implicación para validación

- Los módulos 1 (WAL + Bookmarks/LastSession) y 2 (plists Safari) tienen caso de
  regresión real inmediato: re-ejecutar Mode 1 sobre tuck-2019 y comparar verdicto/
  señales contra el bundle sellado actual.
- Los módulos 3 (FSEvents) y 4 (Spotlight) **no tienen artefacto en el corpus**: se
  necesita o (a) adquirir una imagen pública con `.fseventsd`/`.Spotlight-V100`
  (p. ej. corpus tipo Digital Corpora / CFReDS con imagen APFS completa), o (b) generar
  evidencia sintética de laboratorio documentada como tal. Sin esto, la calibración de
  sus escaleras z es provisional y debe declararse en KNOWN_LIMITATIONS.

---

## 7. Cambios de integración requeridos (inventario, NO implementados)

1. `vigia/sift/macos_forensics.py` — pasar de `to_signal()` único a emisión por dominio
   (`to_signals()` o sub-analyzers); migrar Safari/plists a los nuevos dominios.
2. `/sift_orchestrator.py:490-516` — consumir N señales macOS en vez de 1; revisar la
   rama mobile-only para que ≥3 señales primarias macOS puedan alcanzar el
   AbductiveReasoner (B-052-P2, decisión de routing).
3. `vigia/core/forensic_adapter.py` — `_LAYER_MAP` y `_EVIDENCE_MAP`: altas de
   `macos_browser`, `macos_plist_persistence`, `macos_plist_activity`,
   `macos_fsevents`, `macos_spotlight`.
4. `abductive_reasoner.py` `layer_map` — alta de los dominios macOS.
5. `vigia_agent.py` — sin cambios de routing (markers ya cubren las 4 familias);
   opcional: marker Chrome-on-macOS (`Application Support/Google/Chrome`).
6. Tests: replicar `test_b042_b043_mobile_determinism.py` para cada `to_signal()` nuevo;
   caso de regresión tuck-2019; oráculo cruzado FSEvents (validar contra salida de un
   parser de referencia en fixtures, sin dependerlo).
7. Re-ejecución de corpus completa antes de sellar (advertencia B-052: cambia todos los
   verdictos mobile).
8. `KNOWN_LIMITATIONS.md` — altas: Spotlight store.db Fase 1 unanalyzed; FSEvents DLS3;
   flags FSEvents por ingeniería inversa; Safari `origin=1` (iCloud) y atribución.

---

## 8. Fuentes internas

- `vigia/sift/macos_forensics.py` (estado actual, TODOs líneas 327-350)
- `vigia/sift/_sql_utils.py` (B-071, manejo WAL), `vigia/sift/_math_utils.py` (B-047)
- `vigia/tools/caie.py:246-387` (EVIDENCE_PROFILES + roles B-070)
- `vigia_scorer.py:991-1058` (cap mono-fuente y gate MALICE)
- `vigia_agent.py:1386-1525` (routing por markers)
- `/sift_orchestrator.py:150-518` (shim, rama mobile-only)
- `docs/AUDITORIA_MACOS_NARRATIVA.md` (B-052, diseño por dominios)
- `docs/AUDITORIA_COBERTURA_MOBILE_SIFT.md` (S4/S5, límites de parseo)
- `BUGS_PENDIENTES.md` — B-048, B-052, B-060, B-070, B-074, B-086
- Corpus: `cases/tuck-2019-macos/`, `cases/VIGIA-TUCK-2019-MACOS_bundle_claude.json`,
  `results/VIGIA-TUCK-2019-MACOS_report_claude.md`

Referencias externas de formato (para el implementador): esquemas SQLite de
Safari/Chrome (observables directamente en los DBs del corpus); FSEvents
DLS1/DLS2 según FSEventsParser (G-C Partners; solo como referencia de layout — GPLv3,
no copiar código) y el parser fseventsd de plaso (Apache-2.0); Spotlight store.db según
spotlight_parser (Y. Khatri, MIT) y mac_apt.

---

## 9. Verificación contra TAXA_DOMINIOS_RECOLECCION (2026-07-09)

`docs/TAXA_DOMINIOS_RECOLECCION.md` (taxonomía v2, CR-001..004) fue recuperado
post-diseño y R4-3 la implementó como código vivo: `_DOMAIN_MAP` +
`classify_domain()` / `classify_domain_subband()` (`vigia/tools/caie.py:~155-243`),
consumidos por el decay de cola por sub-banda y por el gate B-068 v2 de tres ramas
(`vigia_scorer.py:~1133-1229`). Esta sección verifica cada `evidence_type` propuesto
en §§2-5 contra esa taxonomía. **Veredicto global: el diseño se sostiene sin cambios**
— 4 de los 6 tipos propuestos son coherentes y explícitos en TAXA; los otros 2
exponen un gap pre-existente de la taxonomía (no de este diseño), documentado en
§9.1-b. Una expectativa de §1.4 quedó superada por el gate v2 y se corrige en §9.2.

### 9.1 Tabla de verificación por módulo

| Señal propuesta | evidence_type | TAXA doc §4 | `_DOMAIN_MAP` (código) | ¿Sub-banda correcta según modo de fabricación? |
|---|---|---|---|---|
| `macos_browser` (§2) | `web_search` | **no censado** (banda mobile ausente) | **sin entrada** → `UNKNOWN:web_search` / banda `UNKNOWN` | Gap — ver (b). Dominio correcto: **D3** (ver a) |
| `macos_plist_persistence` (§3) | `registry_key` | D3 explícito (§4: "registry_key (18)") | `("filesystem_metadata", "D3")` | ✅ — la descripción de D3 cita literalmente "reg add" como el acto de fabricación de la capa blanda; un LaunchAgent plist es su análogo macOS exacto (user-space con privilegios) |
| `macos_plist_activity` (§3) | `file_metadata` | D3 explícito (§4: "file_metadata (29)") | `("filesystem_metadata", "D3")` | ✅ — metadata de disco leída por parser sobre la misma imagen; spoof 0.65 dentro de la banda D3 (0.20–0.70) |
| `macos_fsevents` (§4) | `usn_journal` / `usn_journal_gap` | D3 explícito (§4: "+ los tipos de código sin uso en corpus: usn_journal, usn_journal_gap…") | `("filesystem_metadata", "D3")` ambos | ✅ — capa DURA de D3 ("MFT/USN… spoofability 0.05… armas anti-timestomp"); FSEvents es el journal análogo en APFS/HFS+. Con spoof 0.20/0.10 ≤ 0.30 ambos cuentan para la rama hard-mass del gate v2 — exactamente el rol doctrinal que §4.3 les asigna |
| `macos_spotlight` — store.db (§5) | `file_metadata` | D3 explícito | D3 | ✅ — mismo caso que plist_activity |
| `macos_spotlight` — Shortcuts (§5) | `app_data` | **no censado** (banda mobile ausente) | **sin entrada** → `UNKNOWN:app_data` / `UNKNOWN` | Gap — ver (b). Dominio correcto: **D3** (ver a) |

**(a) Dominio correcto de `web_search`/`app_data` bajo el principio rector de TAXA
(§1: "quién/qué la produce y qué se necesita comprometer para fabricarla"):**
un historial de navegador y un plist de Shortcuts son registros estructurados en
disco, escritos por una app en user-space y leídos por un parser sobre la misma
imagen — fabricables con privilegios de usuario editando el archivo (un loop puede
insertar 100 filas en el SQLite: replicabilidad D1/D3, no costo por-artefacto D5).
Sus spoofability (0.45 / 0.50) caen dentro de la banda D3 (0.20–0.70) y fuera de
D1a (≥0.85) y D4 (canal de red). No califican como D1b: el criterio de esa
sub-banda es tamper-evidence del formato (record IDs, checksums EVTX) y ni el
SQLite de historial ni un plist la tienen. **Propuesta: D3.** No son D4 aunque
"hablen de" URLs — mismo argumento que TAXA usa contra `log_entry: "network"`
(el contenido no define el dominio; el canal de fabricación sí).

**(b) Gap pre-existente — la banda mobile completa está fuera de `_DOMAIN_MAP`:**
TAXA declara "53/53 tipos del corpus + los 6 tipos definidos en `EVIDENCE_PROFILES`
que el corpus aún no usa. Ningún tipo queda en UNKNOWN" (§4). Pero `EVIDENCE_PROFILES`
define además la banda mobile calibrada (bloque mobile de `EVIDENCE_PROFILES`,
`caie.py`): `chat_message`, `sms`,
`call_log`, `web_search`, `app_data`, `social_media`, `location_data`,
`contact_data` — **8 tipos sin entrada en `_DOMAIN_MAP`**, censo hecho sobre
`data/cases/` donde no aparecen. No es una incoherencia introducida por este diseño:
es el estado actual de TODA la vía mobile (hoy `ios_forensic`/`android_forensic`/
`macos_forensic`/`google_takeout` emiten `app_data` vía `_EVIDENCE_MAP` y clasifican
`UNKNOWN:app_data`). Consecuencias operativas hoy:

1. **Exentos del decay de cola R4-3** (el loop de saturación salta banda `UNKNOWN`,
   `vigia_scorer.py:894-897`): un flood de N señales `web_search` NO satura — el
   vector drowning de BREAK-014 sigue abierto para la banda mobile. Con los
   `to_signals()` por dominio propuestos aquí el riesgo es acotado (una señal
   agregada por navegador, no una por URL), pero el gap existe.
2. **En el gate v2 cuentan como dominio propio cada uno** (doctrina explícita,
   comentario `vigia_scorer.py:1139-1140` — "conservador con evidencia genuinamente
   nueva"): `UNKNOWN:web_search` + `UNKNOWN:app_data` + D3 = 3 dominios. Eso hace el
   gate cross-domain MÁS fácil de abrir para un caso macOS de un solo disco que si
   los tipos estuvieran correctamente mapeados a D3 — un sesgo pro-MALICE no
   intencional que la corrección del gap eliminaría.

**Follow-up recomendado (código, fuera del alcance de este documento — candidato a
bug nuevo o a incluirse en B-052-P2):** completar `_DOMAIN_MAP` con la banda mobile.
Propuesta coherente con el principio rector: `web_search`, `app_data`,
`contact_data`, `call_log`, `sms`, `chat_message` → D3 (registros locales en disco,
user-space; nota: sms/chat con tamper-evidence de backend serían D1b-analogía, pero
el artefacto extraído es el DB local); `location_data` → D3 (cache local) o D4 si la
fuente es telemetría de operador; `social_media` → D4 (registro del lado del
servicio, no fabricable editando el disco local) o D5-soft si llega como captura
interpretativa. Cada asignación requiere la corrida comparativa de corpus (misma
advertencia B-052).

> **CERRADO — B-092 (2026-07-09):** este follow-up se implementó con el protocolo
> completo (test rojo primero, gate comparativo B-069 sobre los 199 casos: 0 flips
> de verdict, 0 flips de score — 199/199 resultados idénticos, pass-rate invariante
> en 167/199). Los 8 tipos mobile tienen entrada en `_DOMAIN_MAP`: los 7 registros
> locales → D3, `social_media` → D4. Curva post-fix plana (flood web_search raw
> 0.85: 0.3776 → 0.3903 → 0.3903) y el ruido puro vuelve a NOISE para los tres
> tipos representativos medidos. Las consecuencias (1) saturación y (2) dominios
> fantasma quedan eliminadas. **Residuales de gate que B-092 NO cierra** (medidos,
> ver "Alcance restante" de B-092): `location_data` sigue abriendo la rama
> hard-mass (spoof 0.30 en el borde ≤0.30 — 4× raw 0.85 → MALICE) y un mix D3+D4
> (`web_search`+`social_media`) sigue abriendo la rama cross-domain; ambos son
> doctrina de calibración pendiente, no regresiones. Ver B-092 en
> `BUGS_PENDIENTES.md` y `tests/test_r4_3_domain_saturation.py::TestMobileBandDomainMap`.

### 9.2 Corrección de expectativa: gate v2 supersede el análisis de §1.4

§1.4 y §0 citan el gate legado "`n_arts >= 4 OR n_types >= 3`" — correcto cuando se
escribió el diseño, superado por el merge de R4-3: el gate v2 cuenta **dominios de
recolección**, con tres ramas (`vigia_scorer.py:1206-1212`): (1) cross-domain: ≥2
dominios Y masa legada (n_arts≥4 o n_types≥3); (2) hard-mass: ≥3 tipos duros o ≥4
artefactos duros (spoof ≤0.30); (3) costo por-artefacto: ≥4 D5-hard/media.

Implicación para el diseño (con los 6 tipos correctamente mapeados a D3, per §9.1-a):
**las 5-6 señales macOS de un caso de un solo disco viven todas en D3** → 1 dominio →
la rama cross-domain NO abre por sí sola. Esto es doctrinalmente correcto según TAXA
(§1: una sola imagen de disco comprometida = un solo acto de fabricación puede
producir todos los artefactos blandos), y NO invalida la estrategia de granularidad
por dominio de este diseño — la emisión de señales separadas sigue siendo necesaria
para el AbductiveReasoner (≥3 primarias), para el cap mono-fuente (`n_artifacts≥2`) y
para la trazabilidad por dominio. Pero la ruta a MALICE de un caso macOS queda así:

- **Rama hard-mass**: FSEvents (`usn_journal` 0.20 / `usn_journal_gap` 0.10) es el
  único de los 4 módulos que aporta tipos duros. Un caso con journal-gap + borrado
  masivo + (p.ej.) hash criptográfico de un binario aporta 2-3 tipos duros — la purga
  anti-forense es, correctamente, el camino más corto a MALICE (invariante 6).
- **Rama cross-domain**: exige evidencia de OTRO canal — telemetría de red (D4),
  memoria (D2), o contenido D5 (un binario analizado del quarantine, p.ej.
  `malware_static_analysis` D5-media). Coincide con la doctrina SIFT del repo:
  macOS-disk-only corrobora SUSPICION; MALICE requiere segundo canal.
- La escalera z de cada `to_signal()` (§§2-5) no cambia: opera aguas arriba del gate.

Nada de esto exige cambiar los esqueletos ni los `evidence_type` elegidos: la única
incoherencia real encontrada (banda mobile sin dominio) es un gap del mapa de código,
pre-existente, y su corrección es un cambio de scorer/CAIE fuera del alcance de este
documento de diseño.

### 9.3 Resumen

| Tipo propuesto | Dominio TAXA | Estado |
|---|---|---|
| `registry_key` | D3 | ✅ coherente (explícito en TAXA §4 y `_DOMAIN_MAP`) |
| `file_metadata` (×2 usos) | D3 | ✅ coherente (explícito) |
| `usn_journal` / `usn_journal_gap` | D3 (capa dura) | ✅ coherente (explícito; alimentan rama hard-mass) |
| `web_search` | D3 | ✅ coherente — gap §9.1-b **cerrado por B-092** (2026-07-09) |
| `app_data` | D3 | ✅ coherente — gap §9.1-b **cerrado por B-092** (2026-07-09) |

Diseño sin cambios. Follow-up (1) — completar la banda mobile en `_DOMAIN_MAP` —
**cerrado por B-092** (ver recuadro en §9.1-b). Queda fuera de alcance el follow-up
(2): al implementar B-052-P2, validar con la corrida comparativa que las señales
macOS D3 no queden dobles-castigadas por decay de cola intra-D3 +
`noisy_or_correlated` intra-módulo (la misma advertencia de triple castigo de TAXA
§5.3 aplica una capa más arriba).
