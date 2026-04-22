# VIGÍA Forensic Suite — Dockerfile
# SANS FIND EVIL Hackathon 2026
#
# Build:
#   docker build -t vigia-forensic:latest .
#
# Run demo end-to-end:
#   docker run --rm vigia-forensic:latest
#
# Run verificador sobre bundle externo:
#   docker run --rm -v /ruta/local:/data vigia-forensic:latest \
#       python3 forensics/verify_ebs_v1.py /data/bundle.json
#
# NOTAS DE SEGURIDAD:
#   - Usuario no-root (vigia:1000) — sin escalada de privilegios
#   - Sin credenciales hardcodeadas — PKI via env vars
#   - PYTHONDONTWRITEBYTECODE evita .pyc en el contenedor
#   - Sin caché de pip en la imagen final

FROM python:3.10-slim

LABEL maintainer="anna.tchijova@gmail.com"
LABEL org.opencontainers.image.title="VIGÍA Forensic Suite"
LABEL org.opencontainers.image.description="Intentionality Analysis for DFIR — SANS FIND EVIL 2026"
LABEL org.opencontainers.image.source="https://github.com/annatchijova/vigia"

# Variables de entorno — sin buffering, sin bytecodes
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIGIA_ENV=production

WORKDIR /app

# ── Dependencias del sistema ────────────────────────────────────────────────
# build-essential: compilación de extensiones C (scikit-learn, numpy)
# libgomp1: OpenMP para paralelismo de scikit-learn
# Limpieza en el mismo RUN para minimizar capas y tamaño
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Usuario no-root ──────────────────────────────────────────────────────────
# Crear usuario dedicado — los contenedores forenses no deben correr como root
RUN groupadd -r vigia --gid 1000 && \
    useradd -r -g vigia --uid 1000 --home /app --shell /bin/bash vigia

# ── Dependencias Python ──────────────────────────────────────────────────────
# Instalar numpy/scikit-learn primero (más pesadas, cachean mejor en layers)
RUN pip install --no-cache-dir \
    numpy>=1.24 \
    scipy>=1.11 \
    scikit-learn>=1.3

# ── Código fuente ────────────────────────────────────────────────────────────
COPY . /app/

# Instalar paquete VIGÍA en modo editable
# pyproject__1_.toml es la versión de proyecto — copiarlo como pyproject.toml
RUN cp pyproject__1_.toml pyproject.toml 2>/dev/null || true
RUN pip install --no-cache-dir pydantic>=2.0 matplotlib
RUN pip install --no-cache-dir -e . 2>/dev/null || \
    echo "[WARN] pip install -e falló — continuando en modo flat"

# ── Calibración sintética ─────────────────────────────────────────────────────
# Generar baseline KDE + Ledoit-Wolf con 180 muestras sintéticas
# Estos .pkl se incluyen en la imagen — reproducibilidad garantizada
RUN python3 vigia_prod/scripts/fit_calibration.py \
    --generate-synthetic \
    --n 180 \
    --output vigia_prod/models/ \
    && echo "[OK] Calibración sintética completada"

# ── Verificación de integridad pre-entrega ───────────────────────────────────
# Correr test de smoke: si el pipeline no arranca, el build falla
RUN python3 -c "
import sys
sys.path.insert(0, '/app/vigia_prod')
sys.path.insert(0, '/app')
from pipeline import run_vigia
result = run_vigia(
    signals_data=[
        {'tool_name': 'SDA', 'value': 0.8, 'z_score': 2.1, 'confidence': 0.9},
    ],
    calibration_path='vigia_prod/models/calibrated_lr_models.pkl',
    covariance_path='vigia_prod/models/nlp_covariance.pkl',
)
assert result['verify']['passed'], 'Smoke test FAILED: bundle inválido'
print(f'[OK] Smoke test: mode={result[\"mode\"]} decision={result[\"decision\"]}')
"

# ── Permisos ──────────────────────────────────────────────────────────────────
RUN chown -R vigia:vigia /app
USER vigia

# ── Directorio de salida ──────────────────────────────────────────────────────
RUN mkdir -p /app/output

# ── Entrypoint por defecto ────────────────────────────────────────────────────
# Demo completa con todos los casos — produce bundles Level 3
CMD ["python3", "demo_case.py", "--all-cases", "--output", "output/"]
