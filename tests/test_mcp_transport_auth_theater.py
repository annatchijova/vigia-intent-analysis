"""
MCP transport "auth theater": VIGIA_MCP_AUTH_TOKEN never actually gated
anything.

__main__ calls `mcp.run()` with no transport argument, so the server always
serves over stdio regardless of any --transport flag on the command line.
_verify_transport_security() used to detect "--transport=sse" in argv and
warn (or, with VIGIA_ENFORCE_STDIO=true, abort) if VIGIA_MCP_AUTH_TOKEN was
unset -- implying that setting the token made HTTP/SSE transport safe. It
never did: nowhere in this codebase is VIGIA_MCP_AUTH_TOKEN's value ever
compared against an incoming request. SECURITY.md documented this as a real
control ("Required for HTTP/SSE transport"). A documented-but-nonfunctional
auth check is worse than none -- it invites exposing 21+ forensic tools
(several root-level) believing a token gates access when nothing does.

Fix: requesting any transport other than stdio now hard-aborts startup
unconditionally (no opt-in, no token can make it "safe" since no HTTP/SSE
serving or auth code exists in this repo). These tests cover the new
_parse_requested_transport() helper and the updated abort behavior, and
guard the default (stdio, no flags) path that every real invocation uses.
"""

from __future__ import annotations

import pytest

pytest.importorskip("mcp.server.fastmcp")

import vigia.vigia_sift_bridge as bridge


class TestParseRequestedTransport:
    def test_no_args_defaults_to_stdio(self):
        assert bridge._parse_requested_transport([]) == "stdio"

    def test_unrelated_args_default_to_stdio(self):
        assert bridge._parse_requested_transport(["--evidence", "/tmp/x"]) == "stdio"

    def test_equals_form(self):
        assert bridge._parse_requested_transport(["--transport=sse"]) == "sse"

    def test_space_separated_form(self):
        assert (
            bridge._parse_requested_transport(["--transport", "streamable-http"])
            == "streamable-http"
        )

    def test_explicit_stdio_is_stdio(self):
        assert bridge._parse_requested_transport(["--transport=stdio"]) == "stdio"

    def test_case_insensitive(self):
        assert bridge._parse_requested_transport(["--transport=SSE"]) == "sse"


class TestVerifyTransportSecurity:
    def test_default_argv_does_not_abort(self, monkeypatch):
        """The path every real stdio invocation takes must never abort."""
        monkeypatch.setattr(bridge.sys, "argv", ["vigia_sift_bridge.py"])
        bridge._verify_transport_security()  # must not raise

    def test_explicit_stdio_transport_does_not_abort(self, monkeypatch):
        monkeypatch.setattr(
            bridge.sys, "argv", ["vigia_sift_bridge.py", "--transport=stdio"]
        )
        bridge._verify_transport_security()  # must not raise

    def test_sse_transport_aborts_even_with_auth_token(self, monkeypatch):
        """No token can make this safe -- there is no auth middleware to
        validate it against. This must abort regardless of the token."""
        monkeypatch.setattr(
            bridge.sys, "argv", ["vigia_sift_bridge.py", "--transport=sse"]
        )
        monkeypatch.setenv("VIGIA_MCP_AUTH_TOKEN", "some-token-that-does-nothing")

        with pytest.raises(SystemExit) as exc_info:
            bridge._verify_transport_security()

        assert exc_info.value.code == 1

    def test_streamable_http_transport_aborts(self, monkeypatch):
        monkeypatch.setattr(
            bridge.sys, "argv", ["vigia_sift_bridge.py", "--transport=streamable-http"]
        )

        with pytest.raises(SystemExit) as exc_info:
            bridge._verify_transport_security()

        assert exc_info.value.code == 1
