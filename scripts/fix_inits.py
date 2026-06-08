# License, or (at your option) any later version.

"""vigia.tools — Herramientas MCP individuales."""

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
