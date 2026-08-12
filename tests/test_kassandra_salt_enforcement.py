"""
KASSANDRA_SALT fail-open gap.

_derive_session_nonce() / _generate_active_tripwire() fall back to a
hardcoded, publicly-known salt ("VIGIA_FALLBACK_SALT_NO_PRODUCTION") when
KASSANDRA_SALT is unset, and the server keeps running with only a stderr
warning. Since an attacker who plants the evidence artifact knows its
SHA-256 in advance, the fallback salt lets them precompute the session
nonce and ghost_protocol id offline from public source alone — defeating
the tripwire's evidentiary claim that triggering it requires
session-specific insider knowledge.

These tests cover the new VIGIA_ENFORCE_KASSANDRA_SALT opt-in, which mirrors
the existing VIGIA_ENFORCE_STDIO / VIGIA_ENFORCE_PARENT pattern in
_verify_transport_security(): fail-open by default (unchanged behavior),
fail-closed (sys.exit(1)) when explicitly requested for production.
"""

from __future__ import annotations

import pytest

pytest.importorskip("mcp.server.fastmcp")

import vigia.vigia_sift_bridge as bridge


@pytest.fixture(autouse=True)
def _clean_kassandra_env(monkeypatch):
    monkeypatch.delenv("KASSANDRA_SALT", raising=False)
    monkeypatch.delenv("VIGIA_ENFORCE_KASSANDRA_SALT", raising=False)


class TestKassandraSaltEnforcement:
    def test_missing_salt_aborts_when_enforced(self, monkeypatch):
        monkeypatch.setenv("VIGIA_ENFORCE_KASSANDRA_SALT", "true")

        with pytest.raises(SystemExit) as exc_info:
            bridge._verify_transport_security()

        assert exc_info.value.code == 1

    def test_missing_salt_warns_but_continues_by_default(self, monkeypatch, capsys):
        # Default posture is unchanged: no KASSANDRA_SALT, no enforcement flag
        # -> server keeps running (fail-open), only a CRITICAL warning is printed.
        bridge._verify_transport_security()

        captured = capsys.readouterr()
        assert "KASSANDRA_SALT" in captured.err
        assert "NOT recommended for production" in captured.err

    def test_present_salt_does_not_abort_even_when_enforced(self, monkeypatch):
        monkeypatch.setenv("KASSANDRA_SALT", "a-real-production-secret")
        monkeypatch.setenv("VIGIA_ENFORCE_KASSANDRA_SALT", "true")

        # Must not raise.
        bridge._verify_transport_security()

    def test_fallback_salt_nonce_is_publicly_precomputable(self):
        """
        Documents the actual exploit: without KASSANDRA_SALT, the nonce and
        ghost_protocol are pure functions of public constants + an
        attacker-known evidence hash — no session secret is required.
        """
        evidence_hash = "deadbeef" * 8  # attacker-crafted content, hash known in advance

        nonce = bridge._derive_session_nonce(evidence_hash)
        tripwire = bridge._generate_active_tripwire(nonce)

        # An attacker reproduces this off of the public repo alone.
        import hmac
        fallback_salt = "VIGIA_FALLBACK_SALT_NO_PRODUCTION"
        expected_raw = f"{fallback_salt}_{evidence_hash}".encode("utf-8")
        expected_nonce = hmac.new(
            fallback_salt.encode("utf-8"), expected_raw, "sha256"
        ).hexdigest()[:16].upper()
        expected_protocol = "PROTOCOLO_KASSANDRA_" + hmac.new(
            fallback_salt.encode("utf-8"), nonce.encode("utf-8"), "sha256"
        ).hexdigest()[:16].upper()

        assert nonce == expected_nonce
        assert tripwire["protocol"] == expected_protocol
        assert tripwire["salt_source"] == "missing"
