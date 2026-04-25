#!/usr/bin/env python3
"""
Crea los __init__.py faltantes en vigia/security y vigia/forensics.
Correr desde la raíz del repo: python3 fix_inits.py
"""
import os

SECURITY_INIT = """\
# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

\"\"\"vigia.security — Hardening, sandbox y auditoria de integridad.\"\"\"

from vigia.security.security import (
    SecurityAudit,
    audit_logger,
    _utcnow,
    _sanitize_path,
)

from vigia.security.sandbox import (
    sandboxed_execute,
    safe_grep,
)

__all__ = [
    "SecurityAudit",
    "audit_logger",
    "_utcnow",
    "_sanitize_path",
    "sandboxed_execute",
    "safe_grep",
]
"""

FORENSICS_INIT = """\
# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

\"\"\"vigia.forensics — Analisis forense de artefactos.\"\"\"
"""

TOOLS_INIT = """\
# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

\"\"\"vigia.tools — Herramientas MCP individuales.\"\"\"
"""

files = {
    "vigia/security/__init__.py": SECURITY_INIT,
    "vigia/forensics/__init__.py": FORENSICS_INIT,
}

# Solo sobreescribir tools/__init__.py si está vacío o es placeholder
tools_init = "vigia/tools/__init__.py"
if os.path.exists(tools_init):
    content = open(tools_init).read().strip()
    if len(content) < 10:
        files[tools_init] = TOOLS_INIT
else:
    files[tools_init] = TOOLS_INIT

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

print("\nVerificando imports...")
import ast
for path in files:
    try:
        ast.parse(open(path).read())
        print(f"  Sintaxis OK: {path}")
    except SyntaxError as e:
        print(f"  ERROR: {path}: {e}")
