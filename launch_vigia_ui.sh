#!/usr/bin/env bash
# Launch the VIGÍA local web UI (bundle browser + Mode 1 launcher).
#
# 100% offline: the SPA uses system font stacks and a CSP tripwire — the
# browser makes zero external requests. No auth layer exists: the server
# binds loopback only (see INSTALL.md §11); put it behind an authenticated
# boundary before any wider exposure.
#
#   VIGIA_HOST      bind address   (default 127.0.0.1 — keep it)
#   VIGIA_UI_PORT   port           (default 8010; Mode 5 API uses 8000)
#   VIGIA_UI_MAX_JOBS  concurrent Mode 1 investigations (default 1)
set -euo pipefail

cd "$(dirname "$0")"

if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "ERROR: fastapi/uvicorn not installed." >&2
    echo "       pip install -r requirements.txt   (or: pip install fastapi uvicorn)" >&2
    exit 1
fi

mkdir -p results/webui

HOST="${VIGIA_HOST:-127.0.0.1}"
PORT="${VIGIA_UI_PORT:-8010}"
echo "VIGÍA Web UI → http://${HOST}:${PORT}/   (Ctrl-C to stop)"
exec python3 -m vigia.ui
