# ─────────────────────────────────────────────────────────────────────────────
# VIGÍA — Forensic Intentionality Analysis System
# Dockerfile — Multi-stage build with security hardening
#
# Security properties:
#   * Multi-stage: build deps never reach final image
#   * Non-root user vigia (UID 10001 — no conflict with nobody/65534)
#   * read_only filesystem compatible — writable paths are Docker mounts
#   * libmagic included for python-magic (evidence file type detection)
#   * No SUID binaries, no unnecessary capabilities
#
# Daubert note:
#   Image digest (sha256) es inmutable — permite attestation del software
#   exacto que produjo un ForensicBundle dado.
#
# Build:
#   docker build -t vigia-forensic .
# Run (via docker compose — preferido):
#   EVIDENCE_PATH=/path/to/evidence docker compose up
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && pip install --no-cache-dir --prefix=/install \
       "scikit-learn>=1.3" \
       "scipy>=1.11"

# ── Stage 2: Final image ──────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL org.opencontainers.image.title="VIGÍA Forensic Analysis"
LABEL org.opencontainers.image.description="Deterministic forensic intentionality analysis — SANS FIND EVIL 2026"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/annatchijova/vigia-intent-analysis"
LABEL org.opencontainers.image.authors="Anna Tchijova"

# Runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Non-root user — UID/GID 10001 (no collision con nobody/65534 ni con UID 1000)
# Fail-loud: sin || true — si falla acá el build falla, no silencia el error
RUN groupadd -r -g 10001 vigia \
    && useradd -r -u 10001 -g vigia -d /app -s /usr/sbin/nologin \
       -c "VIGIA forensic agent" vigia

WORKDIR /app

# Directorios de montaje con ownership correcto
# (evidence ro, reports rw, logs rw — bind-mounted por docker-compose)
RUN mkdir -p /app/evidence /app/reports /var/log/vigia \
    && chown vigia:vigia /app/evidence /app/reports /var/log/vigia

# Código fuente (flat layout)
COPY --chown=vigia:vigia . .

USER vigia

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIGIA_EVIDENCE_DIR=/app/evidence
ENV VIGIA_LOG_DIR=/var/log/vigia
ENV VIGIA_LLM_BACKEND=none

# ── Healthcheck ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from fractions import Fraction; from ebs_v1 import EvidenceBundle; print('OK')"

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["python3", "vigia_agent.py"]
CMD ["--help"]
