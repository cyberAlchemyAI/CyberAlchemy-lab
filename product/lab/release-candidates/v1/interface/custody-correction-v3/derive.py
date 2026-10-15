"""Preserve failed prototype; repair declaration locators and owned fixture refs."""
import json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'custody-correction-v2'
def edit(p,a,b):
    s=p.read_text();assert a in s,(p,a);p.write_text(s.replace(a,b))
assert not (HERE/'runtime').exists()
shutil.copytree(OLD/'runtime',HERE/'runtime',ignore=shutil.ignore_patterns('__pycache__'))
for p in OLD.glob('*.py'):
    if p.name!='author.py':shutil.copyfile(p,HERE/p.name)
shutil.copyfile(OLD/'CONTRACT.md',HERE/'CONTRACT.md')
p=HERE/'runtime/profile.json';s=p.read_text();p.write_text(s.replace('custody-correction-v2/','custody-correction-v3/'))
edit(HERE/'runtime/lab_runtime/cli.py','custody-correction-v2/store','custody-correction-v3/store')
edit(HERE/'test_exact_schemas.py',"'decision_ref':'decision:local:exact-schema',","'decision_ref':'decision:local:exact-schema-registration',")
edit(HERE/'freeze.py',"'mapping_binding':bind(runtime/'endpoint-mapping.json'),'correction_profile_binding':bind(runtime/'write-profile.json')", "'mapping_binding':json.loads((OLD/'engine-manifest.json').read_bytes())['mapping_binding'],\n        'correction_profile_binding':json.loads((OLD/'engine-manifest.json').read_bytes())['correction_profile_binding']")
edit(HERE/'freeze.py',"for p in [OLD/'source-manifest.json'", "failed=HERE.parent/'custody-correction-v2'\n    for row in json.loads((failed/'source-manifest.json').read_bytes())['files']:inputs[row['path']]=row\n    for p in [failed/'source-manifest.json',failed/'receipts/0001/guards.json',failed/'receipts/0001/schemas.json',failed/'guards-0001.log',failed/'schemas-0001.log',\n        RUN/'context-R03-custody-correction-0003.json',RUN/'custody-prototype-terminal-0001.json',OLD/'source-manifest.json'")
(HERE/'regression-sources').mkdir()
print(json.dumps({'authored':str(HERE),'runtime_semantic_delta':'none from v2; locator/profile successor','assertion_delta':'none','fixture_delta':'distinct required Decision refs','authority_effect':'none'}))
