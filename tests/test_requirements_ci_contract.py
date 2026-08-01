"""
S-1 — Test de contrato de dependencias de CI (Fase 0, 2026-07-05).

Tercera ocurrencia de la misma clase de deriva: una dependencia usada por los
tests vive en requirements.txt/pyproject.toml pero falta en requirements-ci.txt,
y el entorno mínimo de CI arranca sin ella:

  1. defusedxml — T-2 del triage 2026-07-03 (B-017): mataba los 14 motores V4.
  2. psutil    — reproducido 2026-07-05: dos módulos de test no colectaban.
  3. pytest-cov — reproducido 2026-07-05: pyproject.toml lo exige vía addopts
     (--cov) y sin él pytest aborta antes de colectar nada.

Este test cierra la clase entera: construye el grafo transitivo de imports
alcanzable desde tests/ y vigia/tests/ (los imports locales se siguen hasta
sus archivos, porque psutil entra vía módulos intermedios, no directo en los
tests), clasifica cada raíz como stdlib / local / third-party, y exige que
toda distribución third-party esté cubierta por requirements-ci.txt — sea
directamente o como dependencia transitiva de una entrada (p.ej. numpy vía
scikit-learn).

Excepción única permitida: `mcp` (KNOWN_LIMITATIONS.md L-045 — no instalable
donde PyJWT fue provisto por el gestor de paquetes del sistema). La excepción
debe seguir documentada: si L-045 desaparece de KNOWN_LIMITATIONS.md, este
test también falla.

Limitación conocida: los imports dinámicos (importlib.import_module con
string, __import__) no se detectan estáticamente. Ninguno de los tres casos
históricos era dinámico.

Cuarta ocurrencia de deriva (2026-07-17, falso positivo del propio scanner):
si el virtualenv vive DENTRO del repo (p.ej. ./.venv), el clasificador
"origen dentro del repo == módulo local" trataba site-packages como código
local y recorría fuentes third-party. Ahí encontraba imports condicionados
por versión/plataforma que el AST walker ve como incondicionales
(`annotationlib` bajo `sys.version_info >= (3, 14)` en typing_extensions;
`apport_python_hook`, hook de Ubuntu) y los declaraba irresolubles. Fix:
`_is_repo_local` excluye site-packages/dist-packages y cualquier directorio
con pyvenv.cfg — un venv dentro del repo es third-party, no repo.
"""

from __future__ import annotations

import ast
import re
import sys
from importlib import metadata, util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Única excepción: import third-party que los tests usan pero que NO puede ir
# en requirements-ci.txt. Cada entrada exige una entrada L-* documentada.
KNOWN_CI_GAPS: dict[str, str] = {
    "mcp": "L-045",
    # Env-injected phantom imports: the scan follows modules whose origin is
    # inside the repo, and a virtualenv at <repo>/.venv puts installed
    # third-party packages under that root. Some carry forward-compat / platform
    # imports — annotationlib (Python 3.14 stdlib) and apport_python_hook (Ubuntu
    # system module) — that do not resolve in an isolated 3.12 venv. Neither is a
    # project dependency; they are environment noise, not a broken test import.
    "annotationlib": "L-061",
    "apport_python_hook": "L-061",
}

_REQ_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _canon(name: str) -> str:
    """Nombre de distribución canónico PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirements_ci_entries() -> set[str]:
    entries = set()
    for line in (REPO / "requirements-ci.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _REQ_NAME_RE.match(line)
        if m:
            entries.add(_canon(m.group(1)))
    return entries


def _covered_distributions(entries: set[str]) -> set[str]:
    """Entradas de requirements-ci + su clausura de dependencias instaladas.

    Los extras (marker `extra ==`) se excluyen: no se instalan con la entrada
    pelada, así que contarlos sobre-cubriría.
    """
    covered: set[str] = set()
    stack = list(entries)
    while stack:
        dist = stack.pop()
        if dist in covered:
            continue
        covered.add(dist)
        try:
            requires = metadata.requires(dist) or []
        except metadata.PackageNotFoundError:
            continue  # no instalada aquí: cuenta como cubierta, sin clausura
        for req in requires:
            if "extra ==" in req:
                continue
            m = _REQ_NAME_RE.match(req)
            if m:
                stack.append(_canon(m.group(1)))
    return covered


_ENV_DIR_MARKERS = frozenset({"site-packages", "dist-packages"})


def _is_repo_local(origin: Path, repo: Path) -> bool:
    """¿`origin` es código DEL repo (a recorrer) o de un entorno instalado?

    Un venv creado dentro del repo (./.venv) queda bajo la raíz del repo,
    pero su contenido es third-party: recorrerlo produce falsos positivos
    con imports condicionados por versión/plataforma (annotationlib,
    apport_python_hook — ver docstring del módulo).
    """
    resolved = origin.resolve()
    try:
        rel = resolved.relative_to(repo.resolve())
    except ValueError:
        return False
    if _ENV_DIR_MARKERS.intersection(rel.parts):
        return False
    # Cualquier ancestro (dentro del repo) que contenga pyvenv.cfg es un venv.
    probe = repo.resolve()
    for part in rel.parts[:-1]:
        probe = probe / part
        if (probe / "pyvenv.cfg").exists():
            return False
    return True


def _module_files(spec) -> list[Path]:
    """Archivos .py que representan un módulo/paquete local resuelto."""
    files = []
    if spec.origin and spec.origin.endswith(".py"):
        files.append(Path(spec.origin))
    elif spec.submodule_search_locations:
        for loc in spec.submodule_search_locations:
            init = Path(loc) / "__init__.py"
            if init.exists():
                files.append(init)
    return files


_GUARD_EXCEPTIONS = {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}


def _is_import_guard(node: ast.Try) -> bool:
    """¿El Try captura la ausencia del módulo? (patrón import-opcional)."""
    for handler in node.handlers:
        types = []
        if handler.type is None:
            return True  # bare except
        if isinstance(handler.type, ast.Tuple):
            types = list(handler.type.elts)
        else:
            types = [handler.type]
        for t in types:
            name = t.id if isinstance(t, ast.Name) else getattr(t, "attr", None)
            if name in _GUARD_EXCEPTIONS:
                return True
    return False


def _imports_of(path: Path, pkg: str | None) -> set[str]:
    """Nombres punteados (absolutos) importados SIN guard por un archivo.

    Solo cuentan los imports que romperían la COLECCIÓN si el módulo falta:
    - los envueltos en try/except ImportError (patrón import-opcional —
      torch, clip, cv2… deliberadamente fuera de requirements-ci),
    - los bloques `if TYPE_CHECKING:`, y
    - los imports a nivel de función (lazy imports: solo ejecutan si esa
      ruta se llama, y las rutas que los llaman están detrás de guards)
    se excluyen. Es exactamente la clase de fallo observada: defusedxml y
    psutil rompían a nivel de módulo.

    `pkg` es el paquete del archivo, para resolver imports relativos.
    Para `from X import y`, se registra tanto `X` como `X.y` — `y` puede ser
    submódulo (hay que seguirlo) o atributo (find_spec lo descarta solo).
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()

    names: set[str] = set()

    def visit(node: ast.AST, guarded: bool) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.iter_child_nodes(node):
                visit(child, True)  # lazy import: no corre al colectar
            return
        if isinstance(node, ast.Try) and _is_import_guard(node):
            for child in node.body:
                visit(child, True)
            for part in (node.handlers, node.orelse, node.finalbody):
                for child in part:
                    visit(child, guarded)
            return
        if isinstance(node, ast.If):
            test = node.test
            is_tc = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
                isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
            )
            if is_tc:
                for child in node.orelse:
                    visit(child, guarded)
                return
        if isinstance(node, ast.Import):
            if not guarded:
                for alias in node.names:
                    names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if not guarded:
                if node.level == 0:
                    base = node.module or ""
                else:
                    if pkg is None:
                        return
                    parts = pkg.split(".")
                    if node.level - 1 >= len(parts):
                        return
                    anchor = parts[: len(parts) - (node.level - 1)]
                    base = ".".join(anchor + ([node.module] if node.module else []))
                if base:
                    names.add(base)
                    for alias in node.names:
                        if alias.name != "*":
                            names.add(f"{base}.{alias.name}")
        for child in ast.iter_child_nodes(node):
            visit(child, guarded)

    visit(tree, False)
    return names


def test_all_test_imports_resolve_with_requirements_ci():
    ci_entries = _requirements_ci_entries()
    covered = _covered_distributions(ci_entries)
    dist_map = metadata.packages_distributions()

    local_roots = {p.stem for p in REPO.glob("*.py")} | {
        p.name for p in REPO.iterdir() if p.is_dir() and not p.name.startswith(".")
    }
    stdlib = set(sys.stdlib_module_names)

    # Semillas: todos los archivos de test de ambas suites.
    queue: list[tuple[Path, str | None]] = []
    for suite in ("tests", "vigia/tests"):
        for f in sorted((REPO / suite).rglob("*.py")):
            rel = f.relative_to(REPO)
            pkg = ".".join(rel.parts[:-1]) if len(rel.parts) > 1 else None
            queue.append((f, pkg))

    seen_files: set[Path] = set()
    seen_modules: set[str] = set()
    third_party_roots: set[str] = set()
    unresolvable: set[str] = set()

    while queue:
        path, pkg = queue.pop()
        if path in seen_files:
            continue
        seen_files.add(path)
        for dotted in _imports_of(path, pkg):
            if dotted in seen_modules:
                continue
            seen_modules.add(dotted)
            root = dotted.split(".")[0]
            if root in stdlib:
                continue
            if root in third_party_roots or root in KNOWN_CI_GAPS:
                third_party_roots.add(root)
                continue
            try:
                spec = util.find_spec(dotted)
            except (ImportError, ValueError, ModuleNotFoundError):
                spec = None
            if spec is None:
                # `from X import atributo` produce candidatos X.atributo sin
                # spec — solo es problema si NI el módulo base resuelve.
                if "." not in dotted and root not in local_roots:
                    # Módulos locales importados bare vía sys.path en runtime
                    # (p.ej. bundle_builder, fit_calibration): buscarlos en
                    # el árbol del repo antes de declararlos irresolubles.
                    hits = [
                        p
                        for pat in (f"{root}.py", f"{root}/__init__.py")
                        for p in REPO.rglob(pat)
                        # "mutants": sandbox de mutation testing (gitignorado).
                        # Resolver un módulo a su copia mutada haría que este
                        # contrato clasifique imports leyendo fuente con
                        # defectos inyectados, y obliga a recorrer ~300 MB.
                        if ".git" not in p.parts
                        and "mutants" not in p.parts
                        and _is_repo_local(p, REPO)
                    ]
                    if hits:
                        local_roots.add(root)
                        queue.append((hits[0], None))
                    else:
                        unresolvable.add(dotted)
                continue
            origin = spec.origin or (
                spec.submodule_search_locations[0]
                if spec.submodule_search_locations
                else None
            )
            if origin and _is_repo_local(Path(origin), REPO):
                mod_pkg = (
                    dotted
                    if spec.submodule_search_locations
                    else dotted.rsplit(".", 1)[0] if "." in dotted else None
                )
                for f in _module_files(spec):
                    queue.append((f, mod_pkg))
            else:
                third_party_roots.add(root)

    assert not unresolvable, (
        f"Imports de tests que no resuelven en este entorno: {sorted(unresolvable)}. "
        "O falta la dependencia o el import está roto (clase BUG-EML-001)."
    )

    missing: dict[str, list[str]] = {}
    for root in sorted(third_party_roots):
        if root in KNOWN_CI_GAPS:
            continue
        dists = [_canon(d) for d in dist_map.get(root, [root])]
        if not any(d in covered for d in dists):
            missing[root] = dists

    assert not missing, (
        "Dependencias third-party alcanzables desde tests/ y vigia/tests/ que "
        f"requirements-ci.txt NO cubre (ni directo ni transitivo): {missing}. "
        "Agregarlas a requirements-ci.txt o, si son legítimamente no "
        "instalables en CI, documentarlas en KNOWN_LIMITATIONS.md y sumarlas "
        "a KNOWN_CI_GAPS con su L-*. (Clase S-1: defusedxml/T-2, psutil, "
        "pytest-cov.)"
    )

    # La excepción no puede quedar huérfana: cada gap exige su L-* documentada.
    known_limitations = (REPO / "KNOWN_LIMITATIONS.md").read_text(encoding="utf-8")
    for gap, lim in KNOWN_CI_GAPS.items():
        assert lim in known_limitations, (
            f"KNOWN_CI_GAPS permite '{gap}' citando {lim}, pero {lim} no "
            "existe en KNOWN_LIMITATIONS.md — la excepción quedó sin respaldo "
            "documental."
        )


def test_is_repo_local_excludes_in_repo_virtualenvs(tmp_path):
    """Regresión del falso positivo 2026-07-17 (annotationlib/apport_python_hook).

    Reproduce sintéticamente un venv dentro del repo: sus fuentes NO deben
    clasificarse como locales (recorrerlas escanea third-party con imports
    condicionados por versión/plataforma), mientras el código real del repo
    sí debe recorrerse.
    """
    repo = tmp_path / "repo"
    # Código genuino del repo — local.
    real = repo / "vigia" / "tools" / "caie.py"
    real.parent.mkdir(parents=True)
    real.write_text("", encoding="utf-8")
    assert _is_repo_local(real, repo)

    # Venv dentro del repo (marcador site-packages) — third-party.
    sp = repo / ".venv" / "lib" / "python3.12" / "site-packages"
    sp.mkdir(parents=True)
    (repo / ".venv" / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")
    te = sp / "typing_extensions.py"
    te.write_text("import annotationlib\n", encoding="utf-8")
    assert not _is_repo_local(te, repo)

    # Venv sin el layout site-packages pero con pyvenv.cfg — third-party.
    odd = repo / "env" / "weird_layout" / "mod.py"
    odd.parent.mkdir(parents=True)
    odd.write_text("", encoding="utf-8")
    (repo / "env" / "pyvenv.cfg").write_text("home = /usr/bin\n", encoding="utf-8")
    assert not _is_repo_local(odd, repo)

    # Fuera del repo — nunca local.
    outside = tmp_path / "elsewhere" / "x.py"
    outside.parent.mkdir(parents=True)
    outside.write_text("", encoding="utf-8")
    assert not _is_repo_local(outside, repo)
