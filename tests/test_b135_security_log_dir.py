"""
B-135 — SecurityAudit default log dir must never be the evidence directory.

vigia/security/security.py defaulted _DEFAULT_LOG_DIR to
os.getenv("VIGIA_EVIDENCE_DIR", "/var/log/vigia"), so every default
SecurityAudit() wrote security_audit.log INTO the forensic evidence
directory whenever VIGIA_EVIDENCE_DIR was set — violating Invariant 1
("Evidence is read-only. Never write to VIGIA_EVIDENCE_DIR").

Observed: security_audit.log created inside the evidence tree on both
Mode 1 RAW runs of VIGIA-MAGNET-2022-iOS-JESS (2026-07-14).

Fix: default to os.getenv("VIGIA_LOG_DIR", "/var/log/vigia"), consistent
with vigia/config.py which already resolves log_dir from VIGIA_LOG_DIR.
"""

import importlib
import sys

import pytest


@pytest.fixture
def reload_security(monkeypatch):
    """Reload vigia.security.security with a controlled environment and
    restore the module afterwards so other tests see pristine state."""
    def _reload(env: dict):
        for var in ("VIGIA_EVIDENCE_DIR", "VIGIA_LOG_DIR"):
            monkeypatch.delenv(var, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        import vigia.security.security as sec
        return importlib.reload(sec)

    yield _reload
    # Restore module under the real (test-session) environment.
    import vigia.security.security as sec
    importlib.reload(sec)


class TestB135DefaultLogDir:
    def test_default_log_dir_ignores_evidence_dir(self, reload_security, tmp_path):
        evidence = tmp_path / "evidence"
        evidence.mkdir()
        sec = reload_security({"VIGIA_EVIDENCE_DIR": str(evidence)})
        assert sec._DEFAULT_LOG_DIR != str(evidence), (
            "B-135: _DEFAULT_LOG_DIR resolves to VIGIA_EVIDENCE_DIR — the "
            "audit log would be written into read-only evidence."
        )

    def test_default_log_dir_honors_vigia_log_dir(self, reload_security, tmp_path):
        logs = tmp_path / "logs"
        sec = reload_security({"VIGIA_LOG_DIR": str(logs)})
        assert sec._DEFAULT_LOG_DIR == str(logs)

    def test_default_log_dir_fallback_is_var_log(self, reload_security):
        sec = reload_security({})
        assert sec._DEFAULT_LOG_DIR == "/var/log/vigia"

    def test_security_audit_never_writes_into_evidence(
        self, reload_security, tmp_path
    ):
        """End-to-end: a default SecurityAudit() with VIGIA_EVIDENCE_DIR set
        must leave the evidence directory byte-for-byte untouched."""
        evidence = tmp_path / "evidence"
        evidence.mkdir()
        logs = tmp_path / "logs"
        sec = reload_security({
            "VIGIA_EVIDENCE_DIR": str(evidence),
            "VIGIA_LOG_DIR": str(logs),
        })
        audit = sec.SecurityAudit()
        audit.log_info("B135_TEST", "unit-test", "unit-test entry")
        assert list(evidence.iterdir()) == [], (
            "B-135: SecurityAudit wrote into the evidence directory."
        )
        assert audit.log_path == logs / "security_audit.log"
        assert audit.log_path.exists()

    def test_explicit_log_path_still_wins(self, reload_security, tmp_path):
        sec = reload_security({"VIGIA_LOG_DIR": str(tmp_path / "logs")})
        explicit = tmp_path / "explicit" / "audit.log"
        audit = sec.SecurityAudit(log_path=str(explicit))
        assert audit.log_path == explicit
