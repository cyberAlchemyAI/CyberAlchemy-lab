import json,sys,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STORE=ROOT/'.local/ontology-context-import-0053';CAPS=HERE.parent/'0035-definition-card-import';PREFIX='cyberAlchemy-v2/commercial-agent-access/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_source(root):
 spec=importlib.util.spec_from_file_location('access_source',root/PREFIX/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 errors=v.validate(root/PREFIX,root)
 if errors:raise ValueError(errors)
 return v

def build():
 for folder in [CAPS,HERE.parent/'0052-recent-context-import']:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();snapshots=[]
 for b in tool.read(HERE/'snapshot-manifest.json'):
  p=HERE/'source-root'/b['path']
  if tool.sha(p)!=b['sha256']:raise ValueError('Snapshot drift')
  t=STORE/'source-root'/b['path'];t.parent.mkdir(parents=True,exist_ok=True)
  if t.exists() and t.read_bytes()!=p.read_bytes():raise ValueError('Store drift')
  t.write_bytes(p.read_bytes());snapshots.append(bind(p))
 validate_source(STORE/'source-root');r=tool.read;p=HERE/'source-root'/PREFIX;profile=r(p/'profile.json');nodes=r(p/'nodes.json');relations=r(p/'relations.json');cap=next(c for c in r(CAPS/'imports.json') if c['id']==profile['product_capability_ref'])
 if cap['source_record']!=r(p/'product-capability.json'):raise ValueError('Capability source changed')
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':profile['meaning_owner']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/governed-access#ontology','name':'Governed System-Building Access','version':'candidate-successor-0053','concept_refs':['source-root/'+PREFIX+'nodes.json#/nodes/'+str(i) for i in range(len(nodes['nodes']))],'relation_ids':[e['relation_id'] for e in relations['relations']],'boundaries':['Candidate business meaning with separate entitlement, authorization and generation boundaries.','No service realization, KEP adapter adoption, deployment, sale or conformance claim.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/governed-access#context','purpose':cap['capability']['outcome'],'identity_boundary':'Customer-controlled generation of inspectable artifacts; an agent request never authorizes itself.','profile_ref':'source-root/'+PREFIX+'profile.json','relevance':[cap['product']['node_id'],cap['capability']['node_id'],ontology['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'source_graph':{'nodes':nodes['nodes'],'relations':relations['relations']},'counts':{'concepts':36,'relations':37,'definitions':16,'sources':16,'residue':8},'contracts':contracts,'snapshots':snapshots,'source_validation':r(HERE/'source-validation.json'),'capability_binding':bind(CAPS/'imports.json'),'evidence_successor':bind(HERE/'successor-bindings.json'),'authority_effect':'none','limitations':['Four CLI references are explicit successors to current interface evidence, not recovered original versions.','Source relationship conditions remain; endpoint-kind signatures are not inferred.','Eight source residue items and blocked realization posture remain.','No service or CLI runtime executed by this context import.']}
 for name,d in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,d)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
