"""
Pins S4/S5 — helpers _safe_* de los módulos mobile
(AUDITORIA_COBERTURA_MOBILE_SIFT §C; WHAT_IS_NEXT §1.3.3/§1.3.4).

S4 — `_safe_rglob`: el contrato observable (primeros N en orden global
determinista, symlinks excluidos, no-dir → []) queda pineado. El fix de esta
sesión cambia la IMPLEMENTACIÓN (heapq.nsmallest: memoria O(limit) en vez de
materializar y ordenar el árbol entero) sin cambiar una sola salida — los
pins son el testigo de esa equivalencia.

S5 — `_safe_plist_load`: un plist VÁLIDO pero gigante se cargaba entero (la
bomba de expansión/memoria del audit). Test escrito ROJO: post-fix, un plist
que excede el límite de tamaño devuelve None SIN intentar parsearlo, y el
contrato existente (malformado → None, válido → dict) no cambia.
"""

import plistlib

import pytest

from vigia.sift.android_forensics import AndroidForensicsAnalyzer
from vigia.sift.ios_forensics import iOSForensicsAnalyzer
from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

RGLOBS = [
    ("ios", iOSForensicsAnalyzer._safe_rglob),
    ("android", AndroidForensicsAnalyzer._safe_rglob),
    ("macos", MacOSForensicsAnalyzer._safe_rglob),
]
_IDS = [r[0] for r in RGLOBS]
_FNS = [r[1] for r in RGLOBS]


@pytest.fixture()
def tree(tmp_path):
    (tmp_path / "sub" / "deeper").mkdir(parents=True)
    for name in ["b.db", "a.db", "z.db", "m.db"]:
        (tmp_path / name).write_text("x")
    (tmp_path / "sub" / "c.db").write_text("x")
    (tmp_path / "sub" / "deeper" / "d.db").write_text("x")
    return tmp_path


class TestSafeRglobContract:
    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_first_n_in_global_sorted_order(self, rglob, tree):
        got = rglob(tree, "*.db", limit=3)
        expected = sorted(tree.rglob("*.db"), key=lambda p: str(p))[:3]
        assert got == expected

    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_limit_larger_than_matches(self, rglob, tree):
        assert len(rglob(tree, "*.db", limit=50)) == 6

    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_symlinks_excluded(self, rglob, tree):
        (tree / "link.db").symlink_to(tree / "a.db")
        got = rglob(tree, "*.db", limit=50)
        assert all(not p.is_symlink() for p in got)
        assert (tree / "link.db") not in got

    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_directories_excluded(self, rglob, tree):
        (tree / "dir.db").mkdir()
        got = rglob(tree, "*.db", limit=50)
        assert (tree / "dir.db") not in got

    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_non_dir_base_returns_empty(self, rglob, tree):
        assert rglob(tree / "no-existe", "*.db") == []
        assert rglob(tree / "a.db", "*.db") == []

    @pytest.mark.parametrize("rglob", _FNS, ids=_IDS)
    def test_deterministic_across_calls(self, rglob, tree):
        assert rglob(tree, "*.db", limit=4) == rglob(tree, "*.db", limit=4)


class TestSafePlistLoad:
    def _loader(self):
        return MacOSForensicsAnalyzer.__new__(MacOSForensicsAnalyzer)._safe_plist_load

    def test_valid_binary_plist_loads(self, tmp_path):
        p = tmp_path / "ok.plist"
        p.write_bytes(plistlib.dumps({"k": "v"}, fmt=plistlib.FMT_BINARY))
        assert self._loader()(p) == {"k": "v"}

    def test_valid_xml_plist_loads(self, tmp_path):
        p = tmp_path / "ok.plist"
        p.write_bytes(plistlib.dumps({"k": 1}, fmt=plistlib.FMT_XML))
        assert self._loader()(p) == {"k": 1}

    def test_malformed_returns_none(self, tmp_path):
        p = tmp_path / "bad.plist"
        p.write_bytes(b"\x00garbage-not-a-plist")
        assert self._loader()(p) is None

    def test_missing_returns_none(self, tmp_path):
        assert self._loader()(tmp_path / "no-existe.plist") is None

    def test_oversized_valid_plist_rejected(self, tmp_path):
        # S5 (ROJO pre-fix): un plist VÁLIDO de >8MB se cargaba entero —
        # sin límite, un artefacto atacante infla la memoria del analyzer.
        # Post-fix: None sin intentar el parseo.
        p = tmp_path / "big.plist"
        p.write_bytes(plistlib.dumps({"blob": "x" * 9_000_000},
                                     fmt=plistlib.FMT_BINARY))
        assert p.stat().st_size > 8 * 1024 * 1024
        assert self._loader()(p) is None

    def test_size_limit_documented_constant(self):
        # El límite es parte del contrato: debe existir y ser razonable.
        import vigia.sift.macos_forensics as m
        limit = getattr(m, "_PLIST_MAX_BYTES", None)
        assert limit is not None and 1024 * 1024 <= limit <= 64 * 1024 * 1024
