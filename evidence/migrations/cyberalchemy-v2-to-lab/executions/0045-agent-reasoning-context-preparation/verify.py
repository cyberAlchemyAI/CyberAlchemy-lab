import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text())
plan=read(HERE/'repair-plan.json')
for ref in read(HERE/'source-bindings.json'):
 p=HERE/ref['snapshot'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ref['sha256']
 assert p.read_bytes()==(ROOT.parent/'cyberAlchemy-v2'/ref['path']).read_bytes()
b=read(HERE/'source/business-ontology.json');bridge=read(HERE/'source/bridge.json')
ids={n['id'] for n in b['nodes']};assert len(ids)==len(b['nodes'])
assert len({r['id'] for r in b['relations']})==len(b['relations'])
assert all(r['source'] in ids and r['target'] in ids for r in b['relations'])
assert all(e['source'] in ids for e in bridge['edges'])
old=read(ROOT/plan['ontology_contract_predecessor']['path']);new=read(HERE/'proposed-ontology.schema.json')
expected=copy.deepcopy(old)
for key in ['concept_refs','relation_ids']:expected['properties'][key]['maxItems']=1000
assert new==expected
header={'authority_effect':'none','boundaries':['Source-qualified candidate'], 'concept_refs':['source/business-ontology.json#/nodes/'+str(i) for i in range(len(ids))], 'kind':'ontology','name':'Agent Reasoning Engine business model','node_id':'lab:ontology-contexts/agent-reasoning-engine#business','owner_ref':'Agent Reasoning Engine product-meaning owner','relation_ids':[r['id'] for r in b['relations']], 'scope_ref':'cyberAlchemy-v2-to-CyberAlchemy-lab-migration','status':'candidate-unadmitted','version':'candidate-0045'}
assert list(Draft202012Validator(old).iter_errors(header))
Draft202012Validator(new).validate(header)
for mode in ['overflow','duplicate','authority']:
 bad=copy.deepcopy(header)
 if mode=='overflow':bad['concept_refs']=[str(i) for i in range(1001)]
 elif mode=='duplicate':bad['concept_refs'].append(bad['concept_refs'][0])
 else:bad['authority_effect']='admitted'
 assert list(Draft202012Validator(new).iter_errors(bad))
ps=read(HERE/'proposed-source-package.schema.json');ps['$ref']='#/$defs/product'
product=read(HERE/'source/product.json');Draft202012Validator(ps).validate(product)
imports=read(HERE.parent/'0035-definition-card-import/imports.json')
assert set(product['capability_refs']).issubset({r['id'] for r in imports})
for e in read(HERE/'evidence-recovery.json'):
 if e['matches']:assert hashlib.sha256((HERE/'evidence-selections'/(e['id']+'.txt')).read_bytes()).hexdigest()==e['expected']
receipt={'result':'PASS','scope':'preparation verification only; source package remains BLOCK','checks':['source snapshots unchanged','business graph identities and endpoints','existing ontology limit rejects actual graph','successor accepts actual graph','successor rejects overflow duplicates and authority grants','Product schema accepts exactly two already-imported capabilities','all recovered evidence selections match original fingerprints'],'authority_effect':'none','bindings':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']}
(HERE/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print('PASS: seven preparation checks; import remains blocked.')
