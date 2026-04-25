import asyncio, json, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv(override=True)
from vigia.tools.vigia_sift_bridge import reason_with_llm
case = json.load(open('data/cases/case_009_insomnio_tactico_es.json'))
evidence = json.dumps({'case_id': case['case_id'], 'case_name': case['case_name'], 'artifacts': case['artifacts']}, ensure_ascii=False, indent=2)
result = asyncio.run(reason_with_llm(evidence, context='Analisis forense de posible false flag'))
print(json.dumps(result, indent=2, ensure_ascii=False))
