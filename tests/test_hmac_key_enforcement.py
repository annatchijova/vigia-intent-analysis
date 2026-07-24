"""
VIGIA_ENFORCE_HMAC_KEY — fail-open HMAC key gap in the security audit log.

SecurityAudit._resolve_hmac_key() falls through to an auto-generated,
never-persisted 32-byte ephemeral key whenever VIGIA_HMAC_KEY /
VIGIA_HMAC_KEY_FILE are unset, with only a stderr warning. Since the key
is lost on every restart, the security_audit.log HMAC chain resets to a
fresh key each time the process starts -- a legitimate restart and an
attacker who truncated/forged the log and let it reinitialize are
indistinguishable, because nothing durable exists to check the new chain
against. This is the same fail-open shape as the KASSANDRA_SALT gap
(vigia_sift_bridge.py's _verify_transport_security): a security-critical
random default with only a warning, no opt-in to fail closed.

VIGIA_ENFORCE_HMAC_KEY mirrors VIGIA_ENFORCE_STDIO / VIGIA_ENFORCE_PARENT /
VIGIA_ENFORCE_KASSANDRA_SALT / VIGIA_ENFORCE_POSIX_SANDBOX: fail-open by
default (unchanged behavior), fail-closed (sys.exit(1)) when requested.

_ENFORCE_HMAC_KEY is a module-level Final[bool] resolved at import time,
and SecurityAudit() is constructed at module import too (`audit_logger =
SecurityAudit()`), so these tests reload vigia.security.security under a
controlled environment, following the same pattern as
tests/test_b135_security_log_dir.py.
"""

import importlib

import pytest


@pytest.fixture
def reload_security(monkeypatch):
    """Reload vigia.security.security with a controlled environment and
    restore the module afterwards so other tests see pristine state."""
    def _reload(env: dict):
        for var in (
            "VIGIA_HMAC_KEY", "VIGIA_HMAC_KEY_FILE", "VIGIA_ENFORCE_HMAC_KEY",
            "VIGIA_EVIDENCE_DIR", "VIGIA_LOG_DIR",
        ):
            monkeypatch.delenv(var, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        import vigia.security.security as sec
        return importlib.reload(sec)

    yield _reload
    # Restore module under the real (test-session) environment. Must clear
    # VIGIA_ENFORCE_HMAC_KEY here explicitly -- monkeypatch only reverts env
    # vars in its own teardown, which runs AFTER this fixture's teardown
    # (reload_security depends on monkeypatch), so a test that set
    # VIGIA_ENFORCE_HMAC_KEY=true without a key would otherwise make this
    # restore-reload itself abort with SystemExit.
    for var in ("VIGIA_HMAC_KEY", "VIGIA_HMAC_KEY_FILE", "VIGIA_ENFORCE_HMAC_KEY"):
        monkeypatch.delenv(var, raising=False)
    import vigia.security.security as sec
    importlib.reload(sec)


class TestHmacKeyEnforcement:
    def test_default_falls_through_to_ephemeral_with_warning(
        self, reload_security, tmp_path, capsys
    ):
        sec = reload_security({"VIGIA_LOG_DIR": str(tmp_path)})

        assert sec._ENFORCE_HMAC_KEY is False
        assert len(sec.audit_logger._hmac_key) == 32
        captured = capsys.readouterr()
        assert "ephemeral HMAC key" in captured.err

    def test_enforced_aborts_without_any_key(self, reload_security, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            reload_security({
                "VIGIA_ENFORCE_HMAC_KEY": "true",
                "VIGIA_LOG_DIR": str(tmp_path),
            })

        assert exc_info.value.code == 1

    def test_enforced_does_not_abort_when_key_env_present(
        self, reload_security, tmp_path
    ):
        key_hex = "ab" * 32  # 32 bytes, hex-encoded
        sec = reload_security({
            "VIGIA_ENFORCE_HMAC_KEY": "true",
            "VIGIA_HMAC_KEY": key_hex,
            "VIGIA_LOG_DIR": str(tmp_path),
        })

        assert sec.audit_logger._hmac_key == bytes.fromhex(key_hex)

    def test_enforced_does_not_abort_when_key_file_present(
        self, reload_security, tmp_path
    ):
        key_file = tmp_path / "hmac.key"
        key_file.write_bytes(b"\x42" * 32)
        sec = reload_security({
            "VIGIA_ENFORCE_HMAC_KEY": "true",
            "VIGIA_HMAC_KEY_FILE": str(key_file),
            "VIGIA_LOG_DIR": str(tmp_path),
        })

        assert sec.audit_logger._hmac_key == b"\x42" * 32
