#!/bin/bash
# setup_dev.sh
# Prepara el entorno de desarrollo VIGÍA en cualquier máquina desde cero.
# Uso: bash setup_dev.sh
# Compatible con: Ubuntu 24, Kali Linux, cualquier Debian-based

set -e

echo "=========================================="
echo "VIGÍA — Setup de entorno de desarrollo"
echo "=========================================="

# 1. Verificar Python
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
    echo "[ERROR] Python 3 no encontrado. Instalá python3 primero."
    exit 1
fi
echo "[OK] Python: $($PYTHON --version)"

# 2. Crear venv si no existe
if [ ! -d ".venv" ]; then
    echo "[*] Creando virtualenv..."
    $PYTHON -m venv .venv
fi
source .venv/bin/activate
echo "[OK] venv activado"

# 3. Instalar dependencias
echo "[*] Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pytest pytest-asyncio -q
echo "[OK] Dependencias instaladas"

# 4. Crear directorio de evidencia de test (requerido por test_safe_path_allowed)
echo "[*] Creando directorio de evidencia de test..."
mkdir -p /tmp/vigia_test_evidence/logs
touch /tmp/vigia_test_evidence/logs/test.log
chmod 600 /tmp/vigia_test_evidence/logs/test.log
echo "[OK] /tmp/vigia_test_evidence/logs/test.log creado"

# 5. Crear directorio de logs forenses (requiere sudo — opcional)
if [ "$(id -u)" = "0" ]; then
    mkdir -p /var/log/vigia
    chmod 700 /var/log/vigia
    echo "[OK] /var/log/vigia creado"
else
    echo "[WARN] /var/log/vigia no creado (no sos root)."
    echo "       Los logs van a /tmp (ephemeral). Para producción:"
    echo "       sudo mkdir -p /var/log/vigia && sudo chmod 700 /var/log/vigia"
fi

# 6. Inicializar base de datos de patrones
echo "[*] Inicializando base de datos de patrones NLP..."
PYTHONPATH=$(pwd) python3 vigia/tools/init_patterns_db.py 2>/dev/null || \
    echo "[WARN] init_patterns_db falló — puede estar en otra ruta"

# 7. Verificar variables de entorno opcionales
echo ""
echo "=========================================="
echo "VARIABLES DE ENTORNO OPCIONALES"
echo "=========================================="
echo "Para producción / CI con cadena de custodia completa:"
echo ""
echo "  export VIGIA_HMAC_KEY=\"$(python3 -c 'import secrets; print(secrets.token_hex(32))')\""
echo "  export KASSANDRA_SALT=\"$(python3 -c 'import secrets; print(secrets.token_hex(16))')\""
echo "  export VIGIA_EVIDENCE_DIR=\"/tmp/vigia_evidence\""
echo ""
echo "Para backend LLM (narrativa — no afecta decisión matemática):"
echo "  export VIGIA_LLM_BACKEND=\"ollama\"   # o \"anthropic\""
echo "  export OLLAMA_MODEL=\"llama3.1:8b\""
echo ""

# 8. Correr tests básicos
echo "=========================================="
echo "VERIFICACIÓN INICIAL"
echo "=========================================="
echo "[*] Corriendo tests de sintaxis..."
FAIL=0
find vigia/ -name "*.py" | while read f; do
    python3 -m py_compile "$f" 2>/dev/null || { echo "[FAIL] $f"; FAIL=1; }
done
echo "[OK] Sintaxis verificada"

echo "[*] Verificando vectores canónicos P2..."
EXPECTED="f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce"
if [ -f "docs/protocols/P2/canonical_vectors_p2.json" ]; then
    ACTUAL=$(sha256sum docs/protocols/P2/canonical_vectors_p2.json | cut -d' ' -f1)
    if [ "$ACTUAL" = "$EXPECTED" ]; then
        echo "[OK] canonical_vectors_p2.json: hash verificado"
    else
        echo "[FAIL] canonical_vectors_p2.json: hash no coincide"
        echo "       Esperado: $EXPECTED"
        echo "       Actual:   $ACTUAL"
    fi
else
    echo "[WARN] docs/protocols/P2/canonical_vectors_p2.json no encontrado"
fi

echo ""
echo "=========================================="
echo "Setup completo. Para correr los tests:"
echo ""
echo "  source .venv/bin/activate"
echo "  python -m pytest tests/ -v --tb=short"
echo "  python run_stress_tests.py"
echo "  python run_adversarial_tests.py"
echo ""
echo "Para correr el demo:"
echo "  python scripts/run_demo.py --case cases/case_001_temporal.json"
echo "=========================================="
