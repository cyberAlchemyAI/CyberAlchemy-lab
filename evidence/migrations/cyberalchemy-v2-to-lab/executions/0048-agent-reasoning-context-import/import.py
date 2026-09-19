import json,sys,tarfile,hashlib,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STORE=ROOT/'.local/ontology-context-import-0048';PACKAGE=STORE/'package';CAPS=HERE.parent/'0035-definition-card-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_graph(business,system,bridge):
 groups=[(business['nodes'],'id'),(system['nodes'],'node_id')];ids=[]
 for nodes,key in groups:
  values=[n[key] for n in nodes]
  if len(values)!=len(set(values)):raise ValueError('Duplicate concept')
  ids.append(set(values))
 if ids[0]&ids[1]:raise ValueError('Branch identity collision')
 rels=[]
 for edges,key,source,target,left,right in [(business['relations'],'id','source','target',ids[0],ids[0]),(system['edges'],'edge_id','from','to',ids[1],ids[1]),(bridge['edges'],'id','source','target',ids[0],ids[1])]:
  for e in edges:
   if e[source] not in left or e[target] not in right:raise ValueError('Wrong branch or missing endpoint')
   rels.append(e[key])
 if len(rels)!=len(set(rels)):raise ValueError('Duplicate relation')
 if any(d['authority_effect']!='none' for d in [business,system,bridge]):raise ValueError('Authority escalation')
 return rels

def build():
 for folder in [CAPS,HERE.parent/'0047-agent-reasoning-runtime-evidence']:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
 for b in tool.read(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 p=PACKAGE/'cyberAlchemy-v2/agent-reasoning-engine';r=tool.read
 spec=importlib.util.spec_from_file_location('restored_are',p/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 validation=v.evaluate()
 if validation!=r(HERE/'source-validation.json') or validation['status']!='PASS':raise ValueError(validation)
 business=r(p/'business-ontology.json');system=r(p/'domainspec/generated/system-ontology.json');bridge=r(p/'bridge.json');rels=validate_graph(business,system,bridge)
 cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-REASON-AND-MANAGE-CONTEXT')
 if cap['source_record']!=r(p/'product-capability.json'):raise ValueError('Capability binding changed')
 prefix='package/cyberAlchemy-v2/agent-reasoning-engine/'
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':r(p/'profile.json')['meaning_owner']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/agent-reasoning-engine#ontology','name':'Agent Reasoning Engine business-system model','version':'candidate-successor-0048','concept_refs':[prefix+'business-ontology.json#/nodes/'+str(i) for i in range(len(business['nodes']))]+[prefix+'domainspec/generated/system-ontology.json#/nodes/'+str(i) for i in range(len(system['nodes']))],'relation_ids':rels,'boundaries':['Business, system and bridge branches remain explicit in source records.','Candidate successor schema capacity; no ontology contract admission or whole-engine conformance.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/agent-reasoning-engine#context','purpose':cap['capability']['outcome'],'identity_boundary':'Request-relative reasoning and context management; judgments confer no permission.','profile_ref':prefix+'profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
 entry=next(e for e in registry['entries'] if e['target_id']=='type.context');schema=(ROOT/entry['binding']['path']).parent/'schema.json'
 Draft202012Validator(r(schema)).validate(context);Draft202012Validator(r(HERE/'ontology.schema.json')).validate(ontology)
 bundle={'context':context,'ontology':ontology,'counts':{'business_concepts':136,'business_relations':153,'system_concepts':77,'system_relations':101,'bridge_links':67},'source_validation':validation,'authority_effect':'none','ontology_schema':{'binding':bind(HERE/'ontology.schema.json'),'admission':'not-granted','posture':'candidate-successor; existing admitted registry unchanged'},'context_schema':bind(schema),'capability_binding':bind(CAPS/'imports.json'),'package_archive':bind(HERE/'package-snapshot.tar.gz'),'package_manifest':bind(HERE/'package-inputs.json'),'evidence_repair':bind(HERE/'repair-delta.json'),'limitations':['Candidate model import under an explicitly unadmitted ontology schema successor.','81 local fixture tests support the two replacement evidence versions, not whole-engine conformance.','Source six gaps and ten residue items remain; no external action authorization.']}
 dump(HERE/'context.json',context);dump(HERE/'ontology.json',ontology);dump(HERE/'bundle.json',bundle);dump(STORE/'bundle.json',bundle)
 return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
