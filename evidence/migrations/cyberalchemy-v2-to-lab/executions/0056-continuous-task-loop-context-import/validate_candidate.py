import json,hashlib
from pathlib import Path
PREFIX='cyberAlchemy-v2/development/agent-reasoning-engine/codex-integration/continuous-construction-task-loop/'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_graph(b,s):
 ids=[n['id'] for n in b['nodes']];system=[n['node_id'] for n in s['nodes']]
 if len(ids)!=len(set(ids)) or len(system)!=len(set(system)) or set(ids)&set(system):raise ValueError('Duplicate identity')
 for e in b['relations']:
  if e['source'] not in ids or e['target'] not in ids:raise ValueError('Dangling relation')
 for e in s['edges']:
  if e['from'] not in system or e['to'] not in system:raise ValueError('Dangling system relation')
 if b['authority_effect']!='none' or s['authority_effect']!='none':raise ValueError('Authority escalation')
def validate(root):
 p=root/PREFIX;b=read(p/'business-ontology.json');s=read(p/'domainspec/generated/system-ontology.json');profile=read(p/'profile.json');cap=read(p/'product-capability.json');interface=read(p/'interface-contract.json');validate_graph(b,s)
 if profile['product_capability_ref']!=cap['capability_id'] or cap['business_ontology_ref']!=b['ontology_id'] or interface['contract_id'] not in cap['output_contract_refs']:raise ValueError('Identity mismatch')
 if profile['effect_authorized'] is not False or profile['live_proxy_integration'] is not False or interface['execution_policy']!='result-proposes-no-successor-execution':raise ValueError('Effect boundary changed')
 if any(d['authority_effect']!='none' for d in [profile,cap,interface]) or interface['output']['effect_authorized'] is not False:raise ValueError('Authority boundary changed')
 for ref in read(p/'sources.json')['sources']:
  if sha(root/ref['path'])!=ref['sha256']:raise ValueError('Source drift')
 if s['construction_inputs']!=read(p/'sources.json')['sources'] or s['source_graph_digest']!=sha(p/'domainspec/generated/graph.json'):raise ValueError('Construction drift')
 contract=s['implementation_contract']
 for key,name in [('product_capability_sha256','product-capability.json'),('business_ontology_sha256','business-ontology.json'),('interface_contract_sha256','interface-contract.json'),('decision_implementation_sha256','runtime/composed-continuation-decision.mjs'),('c19_adapter_sha256','runtime/continuous-construction-adapter.mjs')]:
  if contract[key]!=sha(p/name):raise ValueError('Implementation binding drift')
 if contract['composition_policy']!='C19-CONTINUE-and-ARE-direct-and-exact-first-pending-stage' or contract['successor_execution_authorized'] is not False:raise ValueError('Continuation policy changed')
 projection=read(p/'domainspec/generated/system-ontology-receipt.json')
 if projection['system_ontology_digest']!=sha(p/'domainspec/generated/system-ontology.json'):raise ValueError('Projection drift')
 receipt=read(p/'receipts/l0-validation.json')
 paths=sorted(f for f in p.rglob('*') if f.is_file() and 'generated' not in f.relative_to(p).parts and 'receipts' not in f.relative_to(p).parts and f.name not in {'construction-binding.json','conformance-candidate.json'})
 materials={str(f.relative_to(root)):sha(f) for f in paths}
 digest=hashlib.sha256(json.dumps(materials,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if receipt['status']!='PASS' or receipt['material_digest']!=digest:raise ValueError('Validation receipt is stale')
 return {'result':'PASS','scope':'source offline L0 tests and exact restored package coherence','counts':{'business_concepts':len(b['nodes']),'business_relations':len(b['relations']),'system_concepts':len(s['nodes']),'system_relations':len(s['edges'])},'authority_effect':'none'}
