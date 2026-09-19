import json,sys,tarfile,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STORE=ROOT/'.local/ontology-context-import-0059';PACKAGE=STORE/'package';CAPS=HERE.parent/'0035-definition-card-import';PREV=HERE.parent/'0058-continuous-construction-context-import'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
spec=importlib.util.spec_from_file_location('offline_candidate',HERE/'validate_candidate.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
PREFIX=validator.PREFIX

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def build():
 for folder in [PREV,CAPS]:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
 for b in tool.read(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 validation=validator.validate(PACKAGE)
 if validation!=tool.read(HERE/'candidate-validation.json'):raise ValueError('Candidate validation drift')
 r=tool.read;p=PACKAGE/PREFIX;business=r(p/'business-ontology.json');system=r(p/'domainspec/generated/system-ontology.json');profile=r(p/'profile.json');cap=next(c for c in r(CAPS/'imports.json') if c['id']==profile['product_capability_ref'])
 if cap['source_record']!=r(p/'product-capability.json'):raise ValueError('Capability changed')
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':cap['capability']['owner_ref']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/dependency-relevance#ontology','name':'Dependency Relevance','version':'source-qualified-0059','concept_refs':['package/'+PREFIX+'business-ontology.json#/nodes/'+str(i) for i in range(len(business['nodes']))]+['package/'+PREFIX+'domainspec/generated/system-ontology.json#/nodes/'+str(i) for i in range(len(system['nodes']))],'relation_ids':['package/'+PREFIX+'business-ontology.json#/relations/'+str(i) for i in range(len(business['relations']))],'boundaries':['Source-qualified business and generated system models; source relation entries use positional references.','Explicit dependency closure only; candidate input selections do not alter admitted digests or activate enforcement.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/dependency-relevance#context','purpose':cap['capability']['outcome'],'identity_boundary':'Evaluate exactly the declared dependency roots and their transitive dependencies; treat unrelated drift as diagnostic only.','profile_ref':'package/'+PREFIX+'profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'counts':validation['counts'],'candidate_validation':validation,'contracts':contracts,'package_archive':bind(HERE/'package-snapshot.tar.gz'),'package_manifest':bind(HERE/'package-inputs.json'),'successor_changes':bind(HERE/'successor-changes.json'),'runtime_tests':bind(HERE/'runtime-validation.json'),'candidate_evaluation':bind(HERE/'candidate-evaluation.json'),'test_evidence':bind(HERE/'candidate-validation.json'),'capability_binding':bind(CAPS/'imports.json'),'authority_effect':'none','limitations':['Candidate dependency evaluation only; no enforcement activation or operational effect.','D65 and changed construction artifacts are explicitly selected as candidate inputs; admitted digests remain unchanged.','Original package archived separately; current successor evidence does not assert historical semantic equivalence.','Other archived governance contexts are dependency copies, not revalidated contexts.']}
 for name,d in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,d)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
