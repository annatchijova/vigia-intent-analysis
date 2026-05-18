"""
tests/conftest.py
-----------------
Fixtures globales para la suite de tests VIGÍA.

Garantiza que el directorio de evidencia de test exista antes de correr
cualquier test, independientemente de la máquina o entorno.

El test test_safe_path_allowed espera que /tmp/vigia_test_evidence/logs/test.log
exista porque _sanitize_path() tiene must_exist=True por defecto.
Sin este fixture, el test falla en cualquier clon limpio.
"""

import os
import pytest


# ---------------------------------------------------------------------------
# Fixture: directorio de evidencia de test
# Scope session: se crea una vez por corrida, no por test.
# ---------------------------------------------------------------------------

VIGIA_TEST_EVIDENCE_DIR = "/tmp/vigia_test_evidence"
VIGIA_TEST_LOG_FILE = "/tmp/vigia_test_evidence/logs/test.log"


def pytest_configure(config):
    """
    Hook de pytest que corre antes de cualquier fixture o test.
    Crea la estructura de directorios que los tests de seguridad esperan.
    """
    _ensure_test_evidence_dir()


def _ensure_test_evidence_dir():
    """Crea el directorio y archivo de evidencia de test si no existen."""
    log_dir = os.path.join(VIGIA_TEST_EVIDENCE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = VIGIA_TEST_LOG_FILE
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("VIGIA test evidence fixture\n")
        # Permisos seguros: solo el owner puede leer/escribir
        os.chmod(log_file, 0o600)


@pytest.fixture(scope="session", autouse=True)
def vigia_test_evidence_dir():
    """
    Fixture de sesión que garantiza que el directorio de evidencia de test
    exista durante toda la corrida de tests.
    """
    _ensure_test_evidence_dir()
    yield VIGIA_TEST_EVIDENCE_DIR
    # No limpiamos en teardown — el directorio es efímero en /tmp
    # y se limpia con el reboot del sistema.
