import json,hashlib,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for b in read(HERE/'source-bindings.json'):
 assert sha(HERE/b['snapshot'])==b['sha256'] and sha(ROOT.parent/'cyberAlchemy-v2'/b['path'])==b['sha256']
p=HERE/'source';ontology=read(p/'business-ontology.json');profile=read(p/'profile.json');cap=read(p/'product-capability.json');contract=read(p/'interface-contract.json')
assert profile['product_capability_ref']==cap['capability_id']==ontology['product_capability_ref']
assert profile['business_ontology_ref']==ontology['ontology_id']
assert contract['contract_id'] in cap['output_contract_refs']
assert all(d['authority_effect']=='none' for d in [ontology,profile,cap,contract])
ids=[n['id'] for n in ontology['nodes']];assert len(ids)==len(set(ids))==10
assert len(ontology['relations'])==6 and all(e['source'] in ids and e['target'] in ids for e in ontology['relations'])
assert contract['failure_policy']=='fail-closed-with-causal-reasons-and-zero-automatic-effect-retries'
for r in read(HERE/'evidence-recovery.json'):
 if r['match']:assert sha(HERE/r['snapshot'])==r['sha256']
run=read(HERE/'test-run.json');assert run['exit_code']==0 and run['inputs_unchanged']
text=(HERE/'offline-tests.tap').read_text();assert '# pass 22' in text and '# fail 0' in text and '# skipped 0' in text
for b in read(HERE/'tested-inputs.json'):assert sha(ROOT.parent/'cyberAlchemy-v2'/b['path'])==b['sha256']
for b in read(HERE.parent/'0053-governed-access-context-import/verification.json')['bindings']:assert sha(ROOT/b['path'])==b['sha256']
receipt={'result':'PASS','scope':'read-only preparation and offline fixture evidence; runtime package validation remains pending','authority_effect':'none','checks':['source snapshot integrity','capability and contract identity closure','ten nodes and six relation endpoints close','non-authorizing and no-retry boundaries retained','recovered source versions match original fingerprints','22 offline fixture tests pass against unchanged inputs','predecessor import remains unchanged'],'bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']}
(HERE/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print('PASS: seven preparation checks; 22 offline tests passed. Import remains pending.')
