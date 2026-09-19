"""Import source-qualified People and Teams meaning only. Open questions: README.md."""
import json,os,subprocess,sys,tarfile
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0071-essays-implementation-context-import';STORE=ROOT/'.local/ontology-context-import-0072';PACKAGE=STORE/'package';PREFIX='cyberAlchemy-v2/people-and-teams'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
r=tool.read
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 content=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=content:raise ValueError('Artifact drift')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def build():
 for folder in [PREV,CAPS]:
  for entry in r(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Predecessor drift')
 PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as a:a.extractall(PACKAGE,filter='data')
 for entry in r(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/entry['path'])!=entry['sha256']:raise ValueError('Snapshot drift')
 p=PACKAGE/PREFIX
 for name,script in [('source-validation','scripts/validate.py'),('source-negative-tests','tests/test_negative_mutations.py')]:
  c=subprocess.run([sys.executable,str(p/script)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  if c.returncode or c.stdout!=r(HERE/(name+'.json'))['stdout']:raise ValueError('Source validation drift')
 cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-MODEL-PEOPLE-AND-TEAMS')
 if cap['source_record']!=r(p/'product-capability.json'):raise ValueError('Capability drift')
 nodes=r(p/'nodes.json')['nodes'];relations=r(p/'relations.json')['relations'];registry=tool.load_registry();common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/people-and-teams#ontology','name':'People and Teams Business Model','version':'source-qualified-0072','concept_refs':['package/'+PREFIX+'/nodes.json#/nodes/'+str(i) for i in range(len(nodes))],'relation_ids':['people-and-teams:'+x['id'] for x in relations],'boundaries':['Person and Team are definition bindings; no real people or team instances are imported.','Membership, role, responsibility, ownership and authority remain distinct.','Exact historical definition selections remain source-qualified; they do not replace current global definitions.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/people-and-teams#context','purpose':'Describe people, teams, membership and responsibilities without requiring a real roster.','identity_boundary':'Candidate business meaning only; no identity verification, permissions or runtime implementation.','profile_ref':'package/'+PREFIX+'/profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
 headers=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  entry=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/entry['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);headers.append({'target_id':ident,'binding':entry['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'counts':json.loads(r(HERE/'source-validation.json')['stdout'])['counts'],'contracts':headers,'source_archive':bind(HERE/'package-snapshot.tar.gz'),'source_manifest':bind(HERE/'package-inputs.json'),'source_bindings':bind(HERE/'source-bindings.json'),'source_validation':bind(HERE/'source-validation.json'),'source_negative_tests':bind(HERE/'source-negative-tests.json'),'capability_binding':bind(CAPS/'imports.json'),'relation_bindings':[{'relation_id':'people-and-teams:'+e['id'],'source_ref':'package/'+PREFIX+'/relations.json#/relations/'+str(i)} for i,e in enumerate(relations)],'authority_effect':'none','limitations':['All eight obligation assessments remain not_evaluable; business structure is not proof of runtime behavior.','Six source residue items remain open; local membership/role/responsibility terms remain candidate terms.','No Person or Team instances, personal data, authentication or authorization service is imported.','Historical D65, parent thesis and capability schema versions are recovered exactly, not promoted to current global authority.']}
 for name,obj in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,obj)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
