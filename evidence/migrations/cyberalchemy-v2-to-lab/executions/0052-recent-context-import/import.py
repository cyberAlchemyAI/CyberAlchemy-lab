import json,sys,tarfile,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0051-repository-routing-context-import';CAPS=HERE.parent/'0035-definition-card-import';STORE=ROOT/'.local/ontology-context-import-0052';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/agent-routing/capabilities/recent-context/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_graph(ontology,definitions,cap):
 ids=[n['id'] for n in ontology['nodes']];defs=[d['id'] for d in definitions['definitions']]
 if len(ids)!=len(set(ids)) or len(defs)!=len(set(defs)):raise ValueError('Duplicate concept or definition')
 if set(ids)!=set(defs):raise ValueError('Definition coverage mismatch')
 for n in ontology['nodes']:
  if n['definition_ref']!=n['id'] or not tool.text(n.get('meaning')):raise ValueError('Invalid concept definition')
 for e in ontology['relations']:
  if e['source'] not in ids or e['target'] not in ids or not tool.text(e.get('type')):raise ValueError('Dangling or untyped relation')
 if ontology['authority_effect']!='none' or ontology['registered'] is not False:raise ValueError('Ontology authority escalation')
 if cap['query_effect']!='read-only' or cap['maximum_limits']!={'commits':100,'files':1000}:raise ValueError('Query boundary changed')
 if cap['product_approval'] is not None or cap['authority_effect']!='none':raise ValueError('Capability authority escalation')

def model_errors():
 spec=importlib.util.spec_from_file_location('recent_source',PACKAGE/PREFIX/'validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v.model_errors()

def build():
 for folder in [PREV,CAPS]:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(PREV/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
 for b in tool.read(PREV/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Restored package drift')
 errors=model_errors()
 if errors:raise ValueError(errors)
 r=tool.read;p=PACKAGE/PREFIX;profile=r(p/'profile.json');cap=r(p/'capability.json');ontology=r(p/'ontology.json');definitions=r(p/'definitions.json');validate_graph(ontology,definitions,cap)
 imported=next(c for c in r(CAPS/'imports.json') if c['id']==profile['capability_ref'])
 if imported['source_record']!=cap:raise ValueError('Capability source mismatch')
 parent=next(c for c in r(CAPS/'imports.json') if c['id']==cap['parent_capability_ref'])
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['owner']}
 node={**common,'kind':'ontology','node_id':'lab:ontology-contexts/recent-context#ontology','name':'Recent Repository Context','version':'source-qualified-0052','concept_refs':['package/'+PREFIX+'ontology.json#/nodes/'+str(i) for i in range(len(ontology['nodes']))],'relation_ids':['package/'+PREFIX+'ontology.json#/relations/'+str(i) for i in range(len(ontology['relations']))],'boundaries':['Source scaffold remains unregistered; positional relation references preserve source entries without inventing stable relation IDs.','Recent change metadata does not restore task goals, decisions or unfinished work.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/recent-context#context','purpose':cap['outcome'],'identity_boundary':'Bounded committed-change metadata with separate working-tree observations; cache refresh is explicit and hooks remain uninstalled.','profile_ref':'package/'+PREFIX+'profile.json','relevance':[imported['capability']['node_id'],parent['capability']['node_id'],node['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',node)]:
  e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':node,'source_ontology':ontology,'definitions':definitions,'profile':profile,'counts':{'concepts':6,'relations':5,'definitions':6},'source_model_validation':{'result':'PASS','errors':errors},'archive':bind(PREV/'package-snapshot.tar.gz'),'manifest':bind(PREV/'package-inputs.json'),'build_and_test_evidence':bind(PREV/'verification.json'),'capability_binding':bind(CAPS/'imports.json'),'contracts':contracts,'authority_effect':'none','limitations':['Reuses repaired compiler snapshot and 22 Git fixture tests from 0051; tests not rerun for record-only extraction.','No query, cache refresh, hook installation, or task-state restoration performed.','Source scaffold unregistered; stable relation identity and endpoint-kind signatures are not authored.']}
 for name,obj in [('context.json',context),('ontology.json',node),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
