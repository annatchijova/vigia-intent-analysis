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
        primera llamada real. Este test falla en el código pre-fix."""
        r = asyncio.run(safe_grep("malware", evidence_dir))
        assert r["error"] is None
        assert any("malware" in m for m in r["matches"])

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
