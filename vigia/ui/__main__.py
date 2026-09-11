"""Entry point: ``python3 -m vigia.ui``.

Binds loopback by default (no auth layer exists — see INSTALL.md §11).
Port defaults to 8010 to stay clear of the Mode 5 API on 8000.

R9-1 — ``VIGIA_HOST`` is SHARED with the Mode 5 API (``vigia/vigia_api.py``).
INSTALL.md tells an operator who needs remote access to the API to put it
behind an authenticated reverse proxy; if they also set ``VIGIA_HOST=0.0.0.0``
to do it, this UI — which has NO authentication and can launch subprocesses via
``POST /api/investigations`` — used to follow it onto every interface without
saying a word. Measured: the UI bound ``0.0.0.0`` and an unauthenticated POST
with neither Origin nor Referer reached business validation.

So the UI now reads its OWN ``VIGIA_UI_HOST`` first, and refuses to start on a
non-loopback address unless ``VIGIA_UI_ALLOW_REMOTE`` says the operator meant
it. Refusing is the honest-degradation choice: an exposure nobody asked for is
worse than a server that does not come up and explains why.
"""

from __future__ import annotations

import ipaddress
import os
import sys

import uvicorn

from vigia.api_defaults import DEFAULT_HOST
from vigia.ui.server import create_app

DEFAULT_UI_PORT = 8010

# Hostnames that are loopback by name rather than by literal address.
_LOOPBACK_NAMES = {"localhost", "localhost.localdomain"}

_TRUTHY = {"1", "true", "yes", "on"}


def resolve_host() -> tuple:
    """Return (host, source) — which variable supplied the bind address.

    ``VIGIA_UI_HOST`` wins so an operator can expose the Mode 5 API without
    dragging this UI along; ``VIGIA_HOST`` is still honoured for backward
    compatibility, but `main()` will refuse a non-loopback value from it
    unless the remote opt-in is set.
    """
    for var in ("VIGIA_UI_HOST", "VIGIA_HOST"):
        value = os.environ.get(var, "").strip()
        if value:
            return value, var
    return DEFAULT_HOST, "default"


def is_loopback(host: str) -> bool:
    candidate = host.strip().strip("[]").lower()
    if candidate in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(candidate).is_loopback
    except ValueError:
        # A name we cannot resolve lexically is not assumed safe.
        return False


def remote_bind_refusal(host: str, source: str) -> str:
    """The message shown instead of binding a non-loopback address."""
    shared = (
        "\n  VIGIA_HOST is shared with the Mode 5 API (vigia/vigia_api.py). "
        "Setting it\n  for the API also moves this UI off loopback."
        if source == "VIGIA_HOST" else ""
    )
    return (
        f"REFUSING to bind {host!r} (from {source}): the web UI has no "
        f"authentication layer\n  and POST /api/investigations launches "
        f"vigia_agent.py as a subprocess.{shared}\n"
        "\n  Keep the UI local while the API listens elsewhere:\n"
        "      VIGIA_UI_HOST=127.0.0.1\n"
        "  Or accept the exposure deliberately, behind your own authenticated "
        "boundary:\n"
        "      VIGIA_UI_ALLOW_REMOTE=1\n"
    )


def main() -> None:
    host, source = resolve_host()
    port = int(os.environ.get("VIGIA_UI_PORT", DEFAULT_UI_PORT))
    if not is_loopback(host) and \
            os.environ.get("VIGIA_UI_ALLOW_REMOTE", "").strip().lower() not in _TRUTHY:
        raise SystemExit(remote_bind_refusal(host, source))
    if not is_loopback(host):
        print(f"[VIGIA-UI] WARNING: bound to {host} with VIGIA_UI_ALLOW_REMOTE set. "
              "No authentication layer exists — an authenticated boundary in front "
              "of this port is the operator's responsibility.", file=sys.stderr)
    uvicorn.run(create_app(), host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
