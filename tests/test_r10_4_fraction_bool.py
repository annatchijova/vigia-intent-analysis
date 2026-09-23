"""
Test R10-4 — `bool` es subclase de `int`: las dos copias del predicado
"esto es una Fraction serializada" no decian lo mismo.

En Python `isinstance(True, int)` es True. En JS `Number.isInteger(true)` es
False. `vigia/ui/normalizer.py::is_serialized_fraction` usaba `isinstance(..., int)`
a secas, asi que aceptaba booleanos; la copia de `app.js` los rechazaba.

Medido sobre el codigo vivo antes del fix:

    {"__fraction__": true, "num": true, "den": 1}  -> display 'True/1'
    {"__fraction__": true, "num": 1, "den": true}  -> display '1/True'
    {"__fraction__": true, "num": 1, "den": false} -> denominador cero semantico

En un sistema cuya propiedad declarada es la aritmetica exacta (`Fraction` con
`prec=28`, invariante 4 de CLAUDE.md), `{"num": true}` no es la fraccion 1/1:
es un campo con el tipo equivocado, y mostrarlo como `True/1` lo presenta como
si fuera un valor — exactamente lo que el docstring del normalizador prohibe
("never an invented value").

ALCANCE, medido y acotado: la clase NO alcanza el camino del sello. Las tres
copias de la canonicalizacion (`vigia/core/canonicalize.py`,
`vigia/models/ebs.py`, `verify_tool_log.py`) chequean `isinstance(obj, bool)`
ANTES que `isinstance(obj, int)`, asi que `True` y `1` canonicalizan distinto y
ningun hash cambia. Eso se fija aca abajo para que no pueda regresionar.

Variante encontrada en el mismo barrido: `planner_adapter._to_fraction` no
guardaba contra `bool` (mientras `_signal_z_fraction`, quince lineas mas abajo
en el mismo modulo, si lo hacia) y dejaba la rama del dict fuera de su `try`.
Endurecimiento de un helper SIN llamadores en este commit — no la reparacion
de un camino vivo; el modulo es observation-only (B-129).
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

CASES = [
    ("entero legitimo",  {"__fraction__": True, "num": 3, "den": 5}, True),
    ("num=True",         {"__fraction__": True, "num": True, "den": 1}, False),
    ("den=True",         {"__fraction__": True, "num": 1, "den": True}, False),
    ("num=False",        {"__fraction__": True, "num": False, "den": 1}, False),
    ("den=False",        {"__fraction__": True, "num": 1, "den": False}, False),
    # IRREDUCIBLE: JS no puede ver esta diferencia — ver
    # test_the_float_case_is_an_irreducible_divergence.
    ("num float",        {"__fraction__": True, "num": 1.0, "den": 2}, False),
    ("num string",       {"__fraction__": True, "num": "1", "den": 2}, False),
    ("negativos",        {"__fraction__": True, "num": -3, "den": 5}, True),
    ("cero",             {"__fraction__": True, "num": 0, "den": 1}, True),
]


class TestPredicateRejectsBool:
    @pytest.mark.parametrize("label,obj,expected",
                             CASES, ids=[c[0] for c in CASES])
    def test_is_serialized_fraction(self, label, obj, expected):
        assert normalizer.is_serialized_fraction(obj) is expected

    def test_exact_int_helper(self):
        assert normalizer._is_exact_int(3)
        assert normalizer._is_exact_int(-3)
        assert not normalizer._is_exact_int(True)
        assert not normalizer._is_exact_int(False)
        assert not normalizer._is_exact_int(1.0)

    def test_display_no_longer_invents_a_fraction(self):
        assert normalizer.fraction_display(
            {"__fraction__": True, "num": True, "den": 1}) is None


class TestMismatchIsDeclaredNotInvented:
    def test_tagged_but_untyped_stays_raw_and_warns(self):
        w = []
        obj = {"__fraction__": True, "num": True, "den": 1}
        out = normalizer.decode_fractions(obj, w, "confidence")
        assert out == obj, "no debe convertirse a una fraccion falsa"
        assert len(w) == 1
        assert "__fraction__" in w[0] and "bool" in w[0]

    def test_legitimate_fraction_still_decodes(self):
        w = []
        out = normalizer.decode_fractions(
            {"__fraction__": True, "num": 3, "den": 5}, w, "confidence")
        assert out["display"] == "3/5" and out["is_fraction"] is True
        assert w == []

    def test_nested_mismatch_is_labelled_by_path(self):
        w = []
        normalizer.decode_fractions(
            {"a": [{"__fraction__": True, "num": True, "den": 1}]}, w, "extra")
        assert w and "extra.a[0]" in w[0], w

    def test_warnings_optional_keeps_old_callers_working(self):
        out = normalizer.decode_fractions({"__fraction__": True, "num": 3, "den": 5})
        assert out["display"] == "3/5"

    def test_clean_bundle_gains_no_fraction_noise(self):
        real = REPO_ROOT / "results" / "kiwi" / "VIGIA-KIWI-006_bundle.json"
        if not real.exists():
            pytest.skip("bundle de referencia ausente")
        norm = normalizer.normalize(json.loads(real.read_text()), "cases/x.json")
        assert [w for w in norm["warnings"] if "__fraction__" in w] == []


class TestLockstepWithTheJavaScriptCopy:
    """El defecto era una DIVERGENCIA entre dos copias, asi que el test que
    importa es que coincidan — evaluando el predicado tal como esta en el
    app.js que se sirve, no una reimplementacion."""

    def test_both_predicates_agree(self):
        node = shutil.which("node") or shutil.which("nodejs")
        if not node:
            pytest.skip("node no disponible")
        app_js = REPO_ROOT / "vigia" / "ui" / "static" / "app.js"
        src = app_js.read_text()
        needle = "Number.isInteger(o.num) && Number.isInteger(o.den)"
        assert needle in src, (
            "el predicado de app.js cambio de forma — revisar este lockstep")

        script = (
            "import fs from 'node:fs';\n"
            f"const src = fs.readFileSync({json.dumps(str(app_js))}, 'utf8');\n"
            f"const cond = {json.dumps(needle)};\n"
            "const pred = new Function('o',\n"
            "  \"return !!(o && typeof o === 'object' && o.__fraction__ === true && \" + cond + ');');\n"
            "const cases = JSON.parse(process.argv[2]);\n"
            "console.log(JSON.stringify(cases.map(pred)));\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pred.mjs"
            path.write_text(script)
            payload = json.dumps([c[1] for c in CASES])
            r = subprocess.run([node, str(path), payload],
                               capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, r.stderr
            js = json.loads(r.stdout)

        py = [normalizer.is_serialized_fraction(c[1]) for c in CASES]
        divergentes = [CASES[i][0] for i in range(len(CASES)) if js[i] != py[i]]
        # "num float" es la unica divergencia que NO se puede cerrar: ver
        # test_the_float_case_is_an_irreducible_divergence mas abajo.
        assert divergentes == ["num float"], (
            f"las dos copias del predicado divergen en: {divergentes}\n"
            f"  python: {py}\n  js:     {js}")

    def test_the_float_case_is_an_irreducible_divergence(self):
        """Este test lo encontro el lockstep, no la lectura previa.

        `isinstance(1.0, int)` es False en Python; `Number.isInteger(1.0)` es
        true en JS, porque JS no tiene tipo entero separado y
        `JSON.parse("1.0")` produce exactamente el mismo Number que
        `JSON.parse("1")`. El lado JS NO PUEDE ver la diferencia: no es un
        descuido que se pueda corregir sin cambiar el formato de cable
        (p. ej. serializando num/den como strings).

        Consecuencia observable, dicha en vez de escondida: un bundle ajeno con
        `{"num": 1.0, "den": 2}` se muestra como `1/2` en la pestaña de JSON
        crudo —que lee el archivo sin pasar por el normalizador— y como un dict
        sin convertir, con su warning, en las vistas normalizadas.

        Se deja a Python del lado estricto a proposito: el productor
        (`vigia_agent.py`) emite `obj.numerator`, siempre un int exacto, asi que
        un `1.0` significa que el bundle lo escribio otra cosa. En un sistema
        cuya propiedad declarada es la aritmetica exacta, rechazar es el lado
        correcto del error.
        """
        assert not normalizer.is_serialized_fraction(
            {"__fraction__": True, "num": 1.0, "den": 2})
        w = []
        obj = {"__fraction__": True, "num": 1.0, "den": 2}
        assert normalizer.decode_fractions(obj, w, "z_score") == obj
        assert w and "float" in w[0]


class TestSealPathIsUnaffected:
    """Falsificacion registrada: la clase no alcanza la canonicalizacion.
    Se fija para que no pueda regresionar en silencio."""

    def test_canonicalize_distinguishes_true_from_one(self):
        from vigia.core import canonicalize as canon
        fn = getattr(canon, "canonicalize", None) or canon._canonicalize_v2
        assert fn(True) != fn(1), (
            "True y 1 deben canonicalizar distinto o el hash colisiona")
        assert fn(False) != fn(0)

    def test_standalone_verifier_copy_agrees(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "vtl", REPO_ROOT / "verify_tool_log.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for fn in (m._canonicalize_v1, m._canonicalize_v2):
            assert fn(True) != fn(1)
            assert fn(False) != fn(0)


class TestPlannerAdapterVariant:
    """Endurecimiento de un helper sin llamadores — no un camino vivo."""

    @pytest.mark.parametrize("obj", [
        {"__fraction__": True, "num": True, "den": 1},
        {"__fraction__": True, "num": 1, "den": False},
        {"__fraction__": True, "num": 1, "den": 0},
        {"__fraction__": True, "num": "x", "den": 1},
        {"__fraction__": True, "den": 1},
    ])
    def test_no_longer_raises(self, obj):
        from fractions import Fraction
        from vigia.core.planner_adapter import _to_fraction
        assert _to_fraction(obj) == Fraction(1, 10)

    def test_legitimate_value_unchanged(self):
        from fractions import Fraction
        from vigia.core.planner_adapter import _to_fraction
        assert _to_fraction({"__fraction__": True, "num": 3, "den": 5}) == Fraction(3, 5)
