"""
B9 (Grupo B / A-2) — ciclo de vida del honey token: deactivate + expiry.

Firstness (AUDITORIA_INVARIANTES_ASIMETRIAS §A-2): existía
`activate_honey_token` pero NO había forma de retirar un token — ni tool de
desactivación ni expiración. Los tripwires huérfanos se acumulan en
_HONEY_TOKEN_DIR para siempre, y un retiro manual (rm) no deja rastro en el
audit log: el ciclo de custodia del tripwire quedaba abierto.

Contrato nuevo:
  - deactivate_honey_token(file_path): retira el token CON auditoría;
    contención estricta (realpath dentro de _HONEY_TOKEN_DIR, basename
    honey_*) — no es un rm arbitrario.
  - activate_honey_token(..., ttl_hours=N): expiración opcional persistida
    en sidecar .meta.json; el sweep perezoso (en cada activate/deactivate)
    retira los vencidos con auditoría.

Tests escritos ROJOS (nada de esto existía).
"""

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

import pytest

# L-045: the bridge imports `mcp`, which is not installable in minimal CI
# environments. Skip instead of breaking the whole collection run (B-138).
pytest.importorskip("mcp")

import vigia.vigia_sift_bridge as bridge


@pytest.fixture()
def honey_dir(tmp_path, monkeypatch):
    d = tmp_path / "honey_tokens"
    d.mkdir()
    monkeypatch.setattr(bridge, "_HONEY_TOKEN_DIR", str(d))
    return d


def _plant(honey_dir, name="honey_VIGIA_HONEY_X_abc", content="fake"):
    p = honey_dir / name
    p.write_text(content)
    return p


class TestDeactivate:
    def test_deactivate_removes_token_with_audit(self, honey_dir):
        p = _plant(honey_dir)
        r = bridge._deactivate_honey_token_impl(str(p))
        assert r["status"] == "HONEY_TOKEN_DEACTIVATED"
        assert not p.exists()

    def test_path_outside_honey_dir_blocked(self, honey_dir, tmp_path):
        outside = tmp_path / "honey_fuera.txt"
        outside.write_text("x")
        r = bridge._deactivate_honey_token_impl(str(outside))
        assert r.get("security_block") is True
        assert outside.exists(), "un archivo fuera del dir NO debe borrarse"

    def test_traversal_blocked(self, honey_dir, tmp_path):
        victim = tmp_path / "victima.txt"
        victim.write_text("x")
        r = bridge._deactivate_honey_token_impl(
            str(honey_dir / ".." / "victima.txt"))
        assert r.get("security_block") is True
        assert victim.exists()

    def test_non_honey_basename_blocked(self, honey_dir):
        p = _plant(honey_dir, name="otra_cosa.txt")
        r = bridge._deactivate_honey_token_impl(str(p))
        assert r.get("security_block") is True
        assert p.exists()

    def test_missing_token_honest_error(self, honey_dir):
        r = bridge._deactivate_honey_token_impl(str(honey_dir / "honey_no_existe"))
        assert "error" in r and not r.get("security_block")

    def test_sidecar_removed_with_token(self, honey_dir):
        p = _plant(honey_dir)
        meta = honey_dir / (p.name + ".meta.json")
        meta.write_text(json.dumps({"expires_at": None}))
        bridge._deactivate_honey_token_impl(str(p))
        assert not meta.exists()

    def test_mcp_tool_registered(self):
        assert hasattr(bridge, "deactivate_honey_token"), (
            "A-2: el tool MCP de desactivación no existe"
        )


class TestExpiry:
    def _iso(self, dt):
        return dt.isoformat()

    def test_expired_token_swept(self, honey_dir):
        p = _plant(honey_dir)
        meta = honey_dir / (p.name + ".meta.json")
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        meta.write_text(json.dumps({"expires_at": self._iso(past)}))
        removed = bridge._sweep_expired_honey_tokens()
        assert str(p) in removed
        assert not p.exists() and not meta.exists()

    def test_unexpired_token_stays(self, honey_dir):
        p = _plant(honey_dir)
        meta = honey_dir / (p.name + ".meta.json")
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        meta.write_text(json.dumps({"expires_at": self._iso(future)}))
        assert bridge._sweep_expired_honey_tokens() == []
        assert p.exists()

    def test_token_without_sidecar_never_expires(self, honey_dir):
        p = _plant(honey_dir)
        assert bridge._sweep_expired_honey_tokens() == []
        assert p.exists()

    def test_activate_with_ttl_writes_sidecar(self, honey_dir):
        r = asyncio.run(bridge.activate_honey_token(
            "VIGIA_HONEY_TTL_TEST", "fake-secret", ttl_hours=2.0))
        assert r.get("status") == "HONEY_TOKEN_PLANTED"
        assert r.get("expires_at"), "el TTL debe reflejarse en la respuesta"
        meta = r["file_path"] + ".meta.json"
        assert os.path.exists(meta)
        assert json.loads(open(meta).read())["expires_at"] == r["expires_at"]

    def test_activate_without_ttl_no_sidecar(self, honey_dir):
        r = asyncio.run(bridge.activate_honey_token(
            "VIGIA_HONEY_NO_TTL", "fake-secret"))
        assert r.get("status") == "HONEY_TOKEN_PLANTED"
        assert r.get("expires_at") is None
        assert not os.path.exists(r["file_path"] + ".meta.json")
