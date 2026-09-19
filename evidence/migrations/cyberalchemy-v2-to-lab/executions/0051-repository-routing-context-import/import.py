import json,sys,tarfile,importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];STORE=ROOT/'.local/ontology-context-import-0051';PACKAGE=STORE/'package';CAPS=HERE.parent/'0035-definition-card-import';PREFIX='cyberAlchemy-v2/agent-routing/'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,d):
 text=json.dumps(d,indent=2,sort_keys=True)+'\n'
 if p.exists() and p.read_text()!=text:raise ValueError('Existing artifact differs')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def validate_source(root):
 spec=importlib.util.spec_from_file_location('restored_router',root/PREFIX/'scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);result=v.evaluate()
 if result['status']!='PASS':raise ValueError(result)
 return result,v

def build():
 for folder in [CAPS,HERE.parent/'0050-repository-routing-preparation']:
  for b in tool.read(folder/'verification.json')['bindings']:
   if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Predecessor drift')
 registry=tool.load_registry();PACKAGE.mkdir(parents=True,exist_ok=True)
 with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:archive.extractall(PACKAGE,filter='data')
 for b in tool.read(HERE/'package-inputs.json'):
  if tool.sha(PACKAGE/b['path'])!=b['sha256']:raise ValueError('Snapshot drift')
 validation,v=validate_source(PACKAGE)
 if validation!=tool.read(HERE/'source-validation.json'):raise ValueError('Validation drift')
 p=PACKAGE/PREFIX;r=tool.read;business=r(p/'ontology.json');system=r(p/'domainspec/generated/system-ontology.json');routes=r(p/'routes.json');cap=next(c for c in r(CAPS/'imports.json') if c['id']=='CA2-CAP-ROUTE-REPOSITORY-WORK')
 if cap['source_record']!=r(p/'product-capability.json'):raise ValueError('Capability drift')
 ids=[n['id'] for n in business['nodes']]+[n['node_id'] for n in system['nodes']]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate concept')
 common={'authority_effect':'none','status':'candidate-unadmitted','scope_ref':registry['scope'],'owner_ref':r(p/'profile.json')['package_owner']}
 ontology={**common,'kind':'ontology','node_id':'lab:ontology-contexts/repository-routing#ontology','name':'Repository Work Routing','version':'candidate-successor-0051','concept_refs':['package/'+PREFIX+'ontology.json#/nodes/'+str(i) for i in range(len(business['nodes']))]+['package/'+PREFIX+'domainspec/generated/system-ontology.json#/nodes/'+str(i) for i in range(len(system['nodes']))],'relation_ids':[e['id'] for e in business['relations']],'boundaries':['Source business and generated system concepts retain their separate source shapes; no bridge edges inferred.','Session route remains blocked and ontology enforcement remains suspended.']}
 context={**common,'kind':'context','node_id':'lab:ontology-contexts/repository-routing#context','purpose':cap['capability']['outcome'],'identity_boundary':'Explicit repository objective routing with required authority and evidence; no silent fallback.','profile_ref':'package/'+PREFIX+'profile.json','relevance':[cap['capability']['node_id'],ontology['node_id']]}
 contracts=[]
 for ident,obj in [('type.context',context),('type.ontology',ontology)]:
  e=next(e for e in registry['entries'] if e['target_id']==ident);schema=(ROOT/e['binding']['path']).parent/'schema.json';Draft202012Validator(r(schema)).validate(obj);contracts.append({'target_id':ident,'binding':e['binding'],'schema':bind(schema)})
 bundle={'context':context,'ontology':ontology,'routes':routes,'source_validation':validation,'counts':{'business_concepts':6,'business_relations':4,'system_concepts':4,'system_relations':0,'routes':18},'authority_effect':'none','contracts':contracts,'package_archive':bind(HERE/'package-snapshot.tar.gz'),'package_manifest':bind(HERE/'package-inputs.json'),'capability_binding':bind(CAPS/'imports.json'),'build_evidence':bind(HERE/'build-verification.json'),'limitations':['Rebuilt isolated candidate; no route activation or replacement of Lab instructions.','Compiler refresh preserves Recent Context generated model bytes; receipt now binds current compiler.','Full package coherence and local tests do not establish runtime or implementation admission.']}
 for name,d in [('context.json',context),('ontology.json',ontology),('bundle.json',bundle)]:dump(HERE/name,d)
 dump(STORE/'bundle.json',bundle);return bundle
if __name__=='__main__':print(json.dumps(build()['counts']))
