import json,hashlib
from pathlib import Path
PREFIX='cyberAlchemy-v2/development/agent-reasoning-engine/codex-integration/coding-agent-runtime/'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_graph(b,s):
 ids=[n['id'] for n in b['nodes']];system=[n['node_id'] for n in s['nodes']]
 if len(ids)!=len(set(ids)) or len(system)!=len(set(system)) or set(ids)&set(system):raise ValueError('Duplicate identity')
 for e in b['relations']:
  if e['source'] not in ids or e['target'] not in ids:raise ValueError('Dangling business endpoint')
 for e in s['edges']:
  if e['from'] not in system or e['to'] not in system:raise ValueError('Dangling system endpoint')
 if b['authority_effect']!='none' or s['authority_effect']!='none':raise ValueError('Graph grants authority')
def validate(root):
 p=root/PREFIX;b=read(p/'business-ontology.json');s=read(p/'domainspec/generated/system-ontology.json');cap=read(p/'product-capability.json');profile=read(p/'profile.json');contract=read(p/'interface-contract.json');validate_graph(b,s)
 if profile['product_capability_ref']!=cap['capability_id'] or b['product_capability_ref']!=cap['capability_id'] or profile['business_ontology_ref']!=b['ontology_id']:raise ValueError('Identity mismatch')
 if contract['contract_id'] not in cap['output_contract_refs']:raise ValueError('Output contract mismatch')
 if any(d['authority_effect']!='none' for d in [profile,cap,contract]):raise ValueError('Authority escalation')
 if profile['live_model_transport']!='not-live-validated-by-this-candidate' or profile['verification_scope']!='offline-fixtures-and-injected-clients' or profile['production_sandbox'] is not False:raise ValueError('Scope exceeds evidence')
 if contract['failure_policy']!='fail-closed-with-causal-reasons-and-zero-automatic-effect-retries':raise ValueError('Retry policy changed')
 if set(contract['terminal_statuses'])!={'AWAITING_APPROVAL','BLOCK','EFFECT_AMBIGUOUS','PATCH_CANDIDATE'}:raise ValueError('Terminal boundary changed')
 for name in ['sources.json','sources.l2.json']:
  for ref in read(p/name)['sources']:
   if sha(root/ref['path'])!=ref['sha256']:raise ValueError('Source fingerprint drift')
 if s['construction_inputs']!=read(p/'sources.json')['sources']:raise ValueError('Construction inputs drift')
 if sha(p/'domainspec/generated/graph.json')!=s['source_graph_digest']:raise ValueError('Graph digest drift')
 receipt=read(p/'domainspec/generated/system-ontology-receipt.json')
 if sha(p/'domainspec/generated/system-ontology.json')!=receipt['system_ontology_digest']:raise ValueError('Projection digest drift')
 if receipt['profile_release_admission']!='not-granted' or receipt['deterministic_runs']!=2:raise ValueError('Projection posture changed')
 for ref in s['implementation_contract']['implementation_files']:
  if sha(root/ref['path'])!=ref['sha256']:raise ValueError('Implementation drift')
 return {'result':'PASS','scope':'offline fixture candidate coherence; live canary not revalidated','counts':{'business_concepts':len(b['nodes']),'business_relations':len(b['relations']),'system_concepts':len(s['nodes']),'system_relations':len(s['edges'])},'authority_effect':'none'}
