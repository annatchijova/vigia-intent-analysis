"""
Test R10-1/R10-2 — forma de los campos en el limite UI.

La web UI existe para inspeccionar bundles, y un bundle puede venir de un
tercero: otra pericia, la contraparte, un laboratorio que manda su resultado.
Su contenido es entrada NO confiable, y sin embargo el normalizador lo pasaba
crudo a los renderizadores, que asumian el tipo.

R10-1 — Medido ejecutando las funciones reales de `app.js` con node: seis
campos hacian LANZAR al renderizador.

    toolLogTab / entry.timestamp   (e.timestamp || "").slice is not a function
    toolLogTab / entry.entry_hash  e.entry_hash.slice is not a function
    toolLogTab / audit.timestamp   (e.timestamp || "").slice is not a function
    findingsTab / mitre_ttps       (f.mitre_ttps || []).map is not a function
    findingsTab / artifacts        f.artifacts.join is not a function
    findingsTab / tools_used       f.tools_used.join is not a function

El caso de `artifacts` como string ni siquiera es hostil: es una variante de
esquema plausible en un bundle escrito por otra herramienta. Y `prev_hash`
—el unico campo con `String(...)` puesto a mano— sobrevivia: esa asimetria es
la huella de un arreglo puntual que no barrio la clase.

Fix en el limite (`normalizer.py`), donde un archivo no confiable se convierte
en forma de display: se coacciona y se DECLARA. Nunca se inventa un valor,
nunca se retipa en silencio — el desajuste entra a `warnings[]`, que la UI ya
muestra. Mas `txt()`/`arr()` en el front como defensa en profundidad.

R10-2 — El router atrapaba cualquier excepcion y mostraba "La peticion fallo".
La peticion no habia fallado: el bundle estaba malformado. Para un perito,
"reintenta" y "este archivo tiene un campo con el tipo equivocado" son
diagnosticos distintos. `api()` marca ahora sus propios errores y el banner
distingue.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from vigia.ui import normalizer  # noqa: E402

REAL_BUNDLE = REPO_ROOT / "results" / "kiwi" / "VIGIA-KIWI-006_bundle.json"


def _bundle():
    if not REAL_BUNDLE.exists():
        pytest.skip("bundle de referencia ausente")
    return json.loads(REAL_BUNDLE.read_text())


class TestCoerceText:
    def test_text_passes_through(self):
        w = []
        assert normalizer.coerce_text("hola", "campo", w) == "hola"
        assert w == []

    def test_none_stays_none(self):
        w = []
        assert normalizer.coerce_text(None, "campo", w) is None
        assert w == []

    def test_non_text_is_coerced_and_declared(self):
        w = []
        assert normalizer.coerce_text(42, "campo", w) == "42"
        assert len(w) == 1 and "campo" in w[0] and "int" in w[0]

    def test_never_invents_a_value(self):
        """El desajuste se declara; no se reemplaza por un placeholder."""
        w = []
        assert normalizer.coerce_text({"a": 1}, "campo", w) == "{'a': 1}"
        assert w


class TestCoerceList:
    def test_list_passes_through(self):
        w = []
        assert normalizer.coerce_list(["a"], "campo", w) == ["a"]
        assert w == []

    def test_none_becomes_empty_without_warning(self):
        w = []
        assert normalizer.coerce_list(None, "campo", w) == []
        assert w == []

    def test_scalar_is_wrapped_and_declared(self):
        w = []
        assert normalizer.coerce_list("/un/artefacto", "campo", w) == ["/un/artefacto"]
        assert len(w) == 1 and "str" in w[0]


class TestNormalizerCoercesHostileBundle:
    def test_tool_log_text_fields(self):
        doc = _bundle()
        doc["tool_execution_log"][0].update({"timestamp": 1234567890,
                                             "entry_hash": 42})
        norm = normalizer.normalize(doc, "cases/tercero.json")
        entry = norm["tool_log"]["entries"][0]
        assert entry["timestamp"] == "1234567890"
        assert entry["entry_hash"] == "42"
        assert any("timestamp" in w and "esperaba texto" in w
                   for w in norm["warnings"]), norm["warnings"]

    def test_finding_list_fields(self):
        doc = _bundle()
        if not doc.get("findings"):
            pytest.skip("el bundle de referencia no trae findings")
        doc["findings"][0]["artifacts"] = "/un/solo/artefacto"
        doc["findings"][0]["mitre_ttps"] = 42
        norm = normalizer.normalize(doc, "cases/tercero.json")
        f = norm["findings"][0]
        assert f["artifacts"] == ["/un/solo/artefacto"]
        assert f["mitre_ttps"] == [42]
        assert any("artifacts" in w and "esperaba lista" in w
                   for w in norm["warnings"]), norm["warnings"]

    def test_non_dict_entry_is_dropped_and_declared(self):
        doc = _bundle()
        doc["tool_execution_log"] = ["no soy un objeto"]
        norm = normalizer.normalize(doc, "cases/tercero.json")
        assert norm["tool_log"]["entries"] == []
        assert any("omitido" in w for w in norm["warnings"]), norm["warnings"]

    def test_clean_bundle_gains_no_shape_warnings(self):
        """Control: un bundle bien formado no debe ganar ruido."""
        norm = normalizer.normalize(_bundle(), "cases/limpio.json")
        shape = [w for w in norm["warnings"] if "se esperaba" in w]
        assert shape == [], shape

    @pytest.mark.parametrize("doc", [
        {"bundle_version": "1", "evidence_graph": {}, "integrity": {},
         "decision_trace": {}, "caie_analysis": 7},
        {"agent_verdict": "NOISE", "audit_trail": "not-an-object",
         "pipeline_results": {}},
        {"overall_verdict": "NOISE", "findings": 7},
    ])
    def test_nested_wrong_shapes_degrade_to_warnings(self, doc):
        """The untrusted-bundle boundary must not turn a type mismatch into 500."""
        norm = normalizer.normalize(doc, "cases/hostile-shape.json")
        assert norm["warnings"]
        assert any("se esperaba" in warning for warning in norm["warnings"])


class TestFrontendSurvivesEveryType:
    """Ejecuta los renderizadores reales de app.js — el barrido de R10."""

    def test_no_renderer_throws(self):
        node = shutil.which("node") or shutil.which("nodejs")
        if not node:
            pytest.skip("node no disponible para ejecutar el barrido")
        script = REPO_ROOT / "scripts" / "redteam_round10_render_types.mjs"
        r = subprocess.run([node, str(script)], capture_output=True, text=True,
                           cwd=str(REPO_ROOT), timeout=120)
        assert r.returncode == 0, r.stdout + r.stderr


class TestRenderErrorIsNotCalledARequestFailure:
    """Auditoria de la propia rama: estos asserts eran grep sobre el fuente —
    habrian pasado con el string en un comentario y no probaban conducta
    alguna. Ahora se EJECUTA `errorView` tal como esta en el app.js servido y
    se compara el banner que produce para cada clase de error."""

    def _render_error_view(self, err_js: str) -> str:
        node = shutil.which("node") or shutil.which("nodejs")
        if not node:
            pytest.skip("node no disponible")
        app_js = REPO_ROOT / "vigia" / "ui" / "static" / "app.js"
        src = app_js.read_text()
        esc_body = src.split("function esc(v) {", 1)[1].split("\n}", 1)[0]
        ev_body = src.split("function errorView(err) {", 1)[1].split("\n}", 1)[0]
        script = (
            "const esc = function(v) {" + esc_body + "};\n"
            "const t = (k) => k;\n"
            "let captured = '';\n"
            "const app = { set innerHTML(v) { captured = v; }, "
            "get innerHTML() { return captured; } };\n"
            "const errorView = function(err) {" + ev_body + "};\n"
            "errorView(" + err_js + ");\n"
            "console.log(captured);\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ev.mjs"
            path.write_text(script)
            r = subprocess.run([node, str(path)], capture_output=True,
                               text=True, timeout=60)
            assert r.returncode == 0, r.stderr
            return r.stdout

    def test_request_failure_says_request(self):
        out = self._render_error_view(
            "Object.assign(new Error('500: boom'), {kind: 'request'})")
        assert "err.request" in out and "err.render" not in out, out

    def test_render_failure_does_not_say_request(self):
        """El caso que motivo R10-2: un bundle malformado no es un fallo de red."""
        out = self._render_error_view(
            "new Error('e.timestamp.slice is not a function')")
        assert "err.render" in out and "err.request" not in out, out

    def test_both_locales_have_the_new_key(self):
        i18n = (REPO_ROOT / "vigia" / "ui" / "static" / "i18n.js").read_text()
        assert i18n.count('"err.render"') == 2, "falta EN o ES"
