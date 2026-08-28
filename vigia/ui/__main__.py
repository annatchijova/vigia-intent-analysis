"""Entry point: ``python3 -m vigia.ui``.

Binds loopback by default (no auth layer exists — see INSTALL.md §11).
Port defaults to 8010 to stay clear of the Mode 5 API on 8000.
"""

from __future__ import annotations

import os

import uvicorn

from vigia.api_defaults import DEFAULT_HOST
from vigia.ui.server import create_app

DEFAULT_UI_PORT = 8010


def main() -> None:
    host = os.environ.get("VIGIA_HOST", DEFAULT_HOST)
    port = int(os.environ.get("VIGIA_UI_PORT", DEFAULT_UI_PORT))
    uvicorn.run(create_app(), host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
