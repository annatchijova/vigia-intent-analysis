"""
tests/integration/conftest.py
------------------------------
Agrega la raíz del repo al sys.path ANTES de que los tests corran.
Necesario porque test_ebs_v1_integration.py usa @test que ejecuta
funciones inmediatamente al decorarlas — el conftest de pytest
no ayuda para ese patrón. Este archivo funciona solo con pytest.

Para ejecución directa (python3 test_ebs_v1_integration.py),
el PYTHONPATH debe incluir la raíz del repo. El workflow ya lo hace:
PYTHONPATH=${{ github.workspace }} python3 tests/integration/...
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
_root = str(REPO_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)
