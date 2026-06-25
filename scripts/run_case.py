import asyncio, json, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv(override=True)
from vigia.vigia_sift_bridge import reason_with_llm

artifacts = json.load(open('data/cases/vigia_input_defcon_nist.json'))
evidence = json.dumps(artifacts, ensure_ascii=False, indent=2)
result = asyncio.run(reason_with_llm(
    evidence,
    context='Real forensic artifacts from DEFCON DFIR CTF 2019 and NIST CFReDS Hacking Case.'
))
print(json.dumps(result, indent=2, ensure_ascii=False))
