import asyncio, json, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv(override=True)
from vigia.tools.vigia_sift_bridge import reason_with_llm

# Cargar caso específico del dataset
cases = json.load(open('data/dataset_test_cases.json'))
case = next(c for c in cases if c['case_id'] == 'VIGIA-LAYOUT-001')

evidence = json.dumps({
    'case_id': case['case_id'],
    'case_name': case['name'],
    'artifacts': case.get('evidence_log', case.get('evidence', []))
}, ensure_ascii=False, indent=2)

result = asyncio.run(reason_with_llm(evidence, context=case.get('notes', '')))
print(json.dumps(result, indent=2, ensure_ascii=False))
