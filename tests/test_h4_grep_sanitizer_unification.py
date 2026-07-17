"""
H4 / TANDA 2 (2026-07-06) — _sanitize_grep_pattern unificado, fail-closed.

Pre-fix había DOS implementaciones vivas con el mismo nombre y semántica
opuesta:
  - vigia/vigia_sift_bridge.py  — fail-closed: whitelist + ValueError + audit log
  - vigia/security/sandbox.py   — fail-open: strip silencioso de NUL + truncado
    a 512 → el patrón EJECUTADO difería del pedido sin señal alguna.

Canónica (decisión abductiva): la estricta — los tests e2e ya fijaban su
contrato, y una herramienta forense no puede mutar silenciosamente lo que el
analista pidió buscar. Vive en vigia.security.sandbox; el bridge re-exporta.

Colateral descubierto y corregido en esta tanda: `audit_logger` estaba SIN
bindear en sandbox.py → safe_grep crasheaba con NameError en la PRIMERA
llamada real (latente: el corpus JSON no ejercita grep).
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.environ.setdefault("VIGIA_EVIDENCE_DIR", tempfile.mkdtemp(prefix="vigia_grep_test_"))

from vigia.security.sandbox import (  # noqa: E402
    MAX_GREP_PATTERN_LENGTH,
    _sanitize_grep_pattern,
    safe_grep,
)


class TestSingleSource:
    def test_bridge_reexports_canonical(self):
        # L-045: the bridge imports `mcp`, not installable in minimal CI
        # environments — skip this re-export check when absent (B-138).
        pytest.importorskip("mcp")
        from vigia.vigia_sift_bridge import _sanitize_grep_pattern as bridge_fn
        assert bridge_fn is _sanitize_grep_pattern


class TestFailClosedContract:
    """El contrato estricto (el que los tests e2e ya fijaban para el bridge)."""

    def test_accepts_whitelisted_pattern(self):
        assert _sanitize_grep_pattern("malware-scan-2026") == "malware-scan-2026"

    def test_rejects_shell_injection(self):
        with pytest.raises(ValueError):
            _sanitize_grep_pattern("term; rm -rf /")

    def test_rejects_null_byte_instead_of_stripping(self):
        # Pre-fix el sandbox devolvía "term" (strip silencioso) — el grep
        # ejecutado no era el pedido. Ahora rechaza con el motivo exacto.
        with pytest.raises(ValueError, match="null byte"):
            _sanitize_grep_pattern("t\x00erm")

    def test_rejects_homoglyph(self):
        with pytest.raises(ValueError):
            _sanitize_grep_pattern("tеrm")  # 'е' cirílica

    def test_rejects_overlong_instead_of_truncating(self):
        # Pre-fix el sandbox truncaba a 512 en silencio.
        with pytest.raises(ValueError, match="too long"):
            _sanitize_grep_pattern("a" * (MAX_GREP_PATTERN_LENGTH + 1))

    def test_rejects_non_string(self):
        with pytest.raises(ValueError):
            _sanitize_grep_pattern(123)


class TestSafeGrepIntegration:
    @pytest.fixture()
    def evidence_dir(self, tmp_path, monkeypatch):
        # safe_grep confina al evidence dir vía _sanitize_path
        monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path))
        (tmp_path / "a.txt").write_text("hello malware line\nclean line\n")
        return str(tmp_path)

    def test_safe_grep_no_longer_name_errors(self, evidence_dir):
        """Colateral TANDA 2: audit_logger sin bindear → NameError en la
        primera llamada real. Este test falla en el código pre-fix.

        LaBestia fix (2026-07-06): también falla si find/grep no pueden
        siquiera ejecutar (p.ej. RLIMIT_AS insuficiente para el linker
        dinámico en un sistema real con más shared libs que este
        contenedor) — el mensaje de assert vuelca el dict completo para
        no depender de reproducir el entorno exacto para diagnosticar.
        """
        r = asyncio.run(safe_grep("malware", evidence_dir))
        assert r["error"] is None, f"safe_grep devolvió error: {r}"
        assert any("malware" in m for m in r["matches"]), f"sin matches: {r}"

    def test_safe_grep_rejects_invalid_pattern_with_reason(self, evidence_dir):
        r = asyncio.run(safe_grep("term; rm -rf /", evidence_dir))
        assert r["matches"] == []
        assert r["error"] and "disallowed" in r["error"]

    def test_safe_grep_never_executes_mutated_pattern(self, evidence_dir):
        # Pre-fix: "mal\x00ware" → strip → grep de "malware" → 1 match
        # atribuido a un patrón que el analista nunca pidió.
        r = asyncio.run(safe_grep("mal\x00ware", evidence_dir))
        assert r["matches"] == []
        assert r["error"] and "null byte" in r["error"]

    def test_safe_grep_multifile_dir_match_has_no_spurious_error(self, tmp_path, monkeypatch):
        """Sobre un directorio con varios archivos y un match, safe_grep debe
        devolver los matches reales SIN error espurio.

        CORRECCIÓN (2026-07-06): la versión previa afirmaba "ejercitar el split
        de xargs" — es FALSO. Con 13 archivos xargs NO splitea: el split ocurre
        recién cerca de ARG_MAX/len(path) archivos (~decenas de miles en un
        sistema típico). Este test cubre el camino de UN SOLO batch de grep + el
        parseo de returncode; NO ejercita el colapso multi-batch a exit 123.
        El fallo que reproducía en LaBestia NO era el split sino RLIMIT_NPROC=64:
        xargs no podía forkear grep ("cannot fork: Resource temporarily
        unavailable") → la búsqueda no corría → error espurio en vez de matches.
        """
        monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path))
        for i in range(12):
            (tmp_path / f"clean_{i}.txt").write_text("nothing relevant here\n")
        (tmp_path / "hit.txt").write_text("hello malware line\n")
        r = asyncio.run(safe_grep("malware", str(tmp_path)))
        assert r["error"] is None, f"falso error en dir poblado con match: {r}"
        assert any("malware" in m for m in r["matches"]), f"sin matches: {r}"

    def test_safe_grep_multifile_dir_no_match_is_benign(self, tmp_path, monkeypatch):
        """El no-match sobre un directorio con varios archivos NO es un error.

        Con un solo batch de grep, un no-match hace que grep salga 1 y xargs
        colapse a exit 123; safe_grep debe tratarlo como "sin matches" benigno
        (no como fallo). CORRECCIÓN (2026-07-06): 13 archivos = un solo batch —
        NO ejercita el split de xargs (haría falta ~ARG_MAX/len(path) archivos).
        Cubre el manejo benigno de returncode 123 en batch único, no el split.
        """
        monkeypatch.setenv("VIGIA_EVIDENCE_DIR", str(tmp_path))
        for i in range(12):
            (tmp_path / f"f_{i}.txt").write_text("nothing relevant here\n")
        r = asyncio.run(safe_grep("zzz_pattern_absent_zzz", str(tmp_path)))
        assert r["error"] is None, f"no-match tratado como error: {r}"
        assert r["matches"] == []

    def test_make_preexec_does_not_tighten_nproc(self):
        """Regresión LaBestia real (RLIMIT_NPROC): el sandbox NO debe apretar
        RLIMIT_NPROC por debajo del hard heredado. El cap (64,64) previo hacía
        que xargs fallara al forkear grep ('xargs: cannot fork: Resource
        temporarily unavailable') en cualquier host con >64 procesos del uid —
        el fallo REAL de LaBestia (confirmado por stderr). Se verifica en un hijo
        forkeado porque _make_preexec aplica límites al proceso que lo llama."""
        import os
        import resource
        if not hasattr(os, "fork") or not hasattr(resource, "RLIMIT_NPROC"):
            pytest.skip("RLIMIT_NPROC / fork no disponibles en esta plataforma")
        from vigia.security.sandbox import _make_preexec

        _, inherited_hard = resource.getrlimit(resource.RLIMIT_NPROC)
        rfd, wfd = os.pipe()
        pid = os.fork()
        if pid == 0:                       # hijo: aplica límites, reporta NPROC
            os.close(rfd)
            try:
                _make_preexec(512, 30)
                soft, _ = resource.getrlimit(resource.RLIMIT_NPROC)
                os.write(wfd, str(soft).encode())
            finally:
                os._exit(0)
        os.close(wfd)
        child_soft = int(os.read(rfd, 64).decode() or "-1")
        os.close(rfd)
        os.waitpid(pid, 0)
        # Invariante: se eleva al hard heredado, nunca se aprieta a 64.
        assert child_soft == inherited_hard, (
            f"NPROC quedó en {child_soft}, esperado == hard heredado "
            f"{inherited_hard} (no el cap viejo de 64)"
        )
