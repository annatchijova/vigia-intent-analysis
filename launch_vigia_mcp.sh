#!/bin/bash
cd /home/labestiadevigia/vigia-repo
export VIGIA_EVIDENCE_DIR=/home/labestiadevigia/vigia-repo/evidence
export VIGIA_LLM_BACKEND=anthropic
export VIGIA_SYSTEM_PROMPT_PATH=/home/labestiadevigia/vigia-repo/vigia/data/system_prompt_peirce_EN.md
export VIGIA_HMAC_KEY_FILE=/home/labestiadevigia/.vigia_secrets/hmac_key
exec /home/labestiadevigia/vigia-repo/.venv/bin/python3 \
    /home/labestiadevigia/vigia-repo/vigia/vigia_sift_bridge.py "$@"
