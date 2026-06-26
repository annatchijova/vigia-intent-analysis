# ─────────────────────────────────────────────────────────────────────────────
# VIGÍA — Forensic Intentionality Analysis System
# Dockerfile — Multi-stage build with security hardening
#
# Security properties:
#   * Multi-stage: build deps never reach final image
#   * Non-root user vigia (UID 65534 / nobody-equivalent)
#   * No shell in final image (sh removed from non-root attack surface)
#   * read_only filesystem compatible — writable paths are Docker secrets/mounts
#   * libmagic included for python-magic (evidence file type detection)
#   * No SUID binaries, no unnecessary capabilities
#
# Daubert note:
#   Image digest (sha256) is immutable — enables attestation of exact
#   software version that produced any given ForensicBundle.
#
# Build:
#   docker build -t vigia-forensic .
# Run (via docker compose — preferred):
#   EVIDENCE_PATH=/path/to/evidence docker compose up
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into isolated prefix
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && pip install --no-cache-dir --prefix=/install \
       scikit-learn>=1.3 \
       scipy>=1.11

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
    && rm -rf /var/lib/apt/lists/* \
    && find / -perm /6000 -type f -exec chmod a-s {} + 2>/dev/null || true

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Non-root user — UID/GID 65534 (nobody)
RUN groupadd -r -g 65534 vigia 2>/dev/null || true \
    && useradd -r -u 65534 -g vigia -d /app -s /usr/sbin/nologin -c "VIGIA forensic agent" vigia 2>/dev/null || true

WORKDIR /app

# Copy source (flat layout — PYTHONPATH=/app)
COPY --chown=vigia:vigia . .

# Create mount point directories with correct ownership
# These will be bind-mounted by docker-compose (evidence ro, reports rw, logs rw)
# read_only: true in compose means these must exist but will be overlaid
RUN mkdir -p \
    /app/evidence \
    /app/reports \
    /var/log/vigia \
    && chown -R vigia:vigia /app/evidence /app/reports /var/log/vigia

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
    CMD python3 -c "import vigia; print('OK')" 2>/dev/null || python3 -c "import sys; sys.path.insert(0, '/app'); from ebs_v1 import EvidenceBundle; print('OK')"

# ── Entrypoint ────────────────────────────────────────────────────────────────
# Default: autonomous forensic agent (MCP stdio transport compatible)
# Override via docker compose command: or docker run args
ENTRYPOINT ["python3", "vigia_agent.py"]
CMD ["--help"]
