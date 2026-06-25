#!/bin/bash
cd /home/labestiadevigia/vigia-repo
export VIGIA_EVIDENCE_DIR=/home/labestiadevigia/vigia-repo/evidence
export VIGIA_SYSTEM_PROMPT_PATH=/home/labestiadevigia/vigia-repo/vigia/data/system_prompt_peirce_EN.md
export VIGIA_HMAC_KEY_FILE=/home/labestiadevigia/.vigia_secrets/hmac_key
[ -f /home/labestiadevigia/vigia-repo/.env ] && set -a && source /home/labestiadevigia/vigia-repo/.env && set +a
# Forzar Ollama DESPUÉS de sourcear .env para garantizar prioridad
export VIGIA_LLM_BACKEND=ollama
export VIGIA_OLLAMA_MODEL=deepseek-r1:8b
export VIGIA_OLLAMA_HOST=http://127.0.0.1:11434
# Eliminar ANTHROPIC_VERTEX_PROJECT_ID para evitar que el SDK use Vertex AI
unset ANTHROPIC_VERTEX_PROJECT_ID
unset GOOGLE_CLOUD_PROJECT
unset CLOUD_ML_REGION
exec /home/labestiadevigia/vigia-repo/.venv/bin/python3 \
    /home/labestiadevigia/vigia-repo/vigia/vigia_sift_bridge.py "$@"
