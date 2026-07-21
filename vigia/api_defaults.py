"""Conservative network defaults shared by VIGÍA's HTTP entry points.

The HTTP gateway intentionally has no application authentication layer.  It
must therefore listen only on loopback unless an operator deliberately puts it
behind an authenticated network boundary.
"""

from __future__ import annotations


DEFAULT_CORS_ORIGINS = ("https://your-openwebui-domain.com",)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
