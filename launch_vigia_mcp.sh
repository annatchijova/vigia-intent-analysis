#!/bin/bash
cd /home/labestiadevigia/vigia-repo
export VIGIA_EVIDENCE_DIR=/home/labestiadevigia/vigia-repo/evidence
exec /home/labestiadevigia/vigia-repo/.venv/bin/python3 \
    /home/labestiadevigia/vigia-repo/vigia/vigia_sift_bridge_final.py "$@"
