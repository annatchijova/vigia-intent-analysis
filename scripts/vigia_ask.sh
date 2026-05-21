#!/bin/bash
# vigia_ask.sh — Consulta VIGÍA en lenguaje natural
CASE_FILE="$1"
if [ ! -f "$CASE_FILE" ]; then
    echo "Archivo no encontrado: $CASE_FILE"
    exit 1
fi
cd ~/vigia-repo
source .venv/bin/activate
python3 -c "
import json
with open('$CASE_FILE') as f:
    case = json.load(f)
desc = case.get('description', 'Sin descripción')
artifacts = []
for a in case.get('artifacts', []):
    anomalies = ' | '.join(a.get('forensic_anomalies', []))
    artifacts.append(f\"- {a['artifact_id']} ({a['type']}): {anomalies}\")
prompt = f\"\"\"Caso: {case.get('case_name', 'Desconocido')}
Descripción: {desc}
Artefactos forenses:
{chr(10).join(artifacts)}
Analizá este caso usando el marco Peirceano:
- Firstness: lo que se observa
- Secondness: lo que no encaja
- Thirdness: el patrón que revela la intención\"\"\"
print(prompt)
" | ollama run deepseek-r1:8b
