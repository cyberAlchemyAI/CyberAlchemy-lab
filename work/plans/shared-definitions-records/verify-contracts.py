from pathlib import Path
import json,hashlib,subprocess,tempfile,copy
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def bind(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def check(name,p):assert p,name;checks.append(name)
base=read(O/'BASELINE.json'); targets=read(O/'FIVE-DEFINITION-REVIEW.json')['targets'];props=read(O/'DEFINITION-SUCCESSOR-PROPOSALS.json')['proposals']
for k in ['root_workspace','registry','native_admission']:
 b=base[k];check('unchanged-baseline-'+k,bind(R/b['path'])==b)
schemas={v:Draft202012Validator(read(R/f'authority/artifact-types/definition/{v}/schema.json'))for v in ['v1','v2']}
for v in schemas: Draft202012Validator.check_schema(schemas[v].schema)
reg=read(R/'authority/definitions/registry.json');ids=set()
for e in reg['entries']:
 check('original-registry-body:'+e['definition_id']+'@'+e['version'],bind(R/e['path'])['sha256']==e['sha256']);ids.add(e['definition_id']+'@'+e['version'])
check('retained-189-versions-183-current',len(reg['entries'])==189 and len(reg['current_lookup'])==183)
for t in targets:
 check('pending-exact:'+t['definition_ref'],bind(R/t['source']['path'])==t['source'])
 schemas['v2'].validate(read(R/t['source']['path']))
 check('five-target-not-in-canonical-registry:'+t['definition_ref'],t['definition_ref'] not in ids)
for p in props:
 body=read(R/p['source']['path']);parent=read(R/p['parent']['path'])
 check('proposal-bound:'+p['definition_ref'],bind(R/p['source']['path'])==p['source'])
 schemas['v2'].validate(body)
 check('unchanged-normative-values:'+p['definition_ref'],all(body[k]==parent[k] for k in ['boundaries','scope']) and body['voices']['scientific_formal']==parent['voices']['scientific_formal'])
 with tempfile.TemporaryDirectory() as d:
  out=Path(d)/'DEFINITION.md'
  subprocess.run(['python3','-B',str(R/'authority/artifact-types/definition/v2/generator.py'),str(R/p['source']['path']),'--output',str(out)],check=True,capture_output=True)
  check('deterministic-projection:'+p['definition_ref'],out.read_bytes()==(R/p['source']['path']).with_name('DEFINITION.md').read_bytes())
v1=read(R/reg['entries'][0]['path']);v2=read(R/targets[0]['source']['path'])
schemas['v1'].validate(v1);schemas['v2'].validate(v2)
check('actual-v1-not-already-v2',not schemas['v2'].is_valid(v1));check('actual-v2-not-v1',not schemas['v1'].is_valid(v2))
e1=schemas['v1'].schema['$defs']['typedRelation']['properties']['relation_kind_ref']['enum'];e2=schemas['v2'].schema['$defs']['typedRelation']['properties']['relation_kind_ref']['enum']
check('supersedes-removed-not-automatic-successor','relation.supersedes' in e1 and 'relation.supersedes' not in e2)
check('relation-v2-expands-and-removes',len(e1)==4 and len(e2)==23 and len(set(e2)-set(e1))==20)
carrier=read(R/'authority/admissions/definition-complete-lab-model/v1/artifact-type-admission.json')
check('carrier-admission-not-ordinary-instance-admission',carrier['ordinary_instances_admitted']==0)
creation=(R/'implementation/lab-runtime/alchlang/ports/creation.py').read_text()
check('public-creation-selects-v2',"cal.artifact-type.definition/v2" in creation)
compiled=(R/'implementation/lab-runtime/alchlang/modules/definitions/use-cases/create-definition.alch').read_text()
check('compiled-creation-selects-v2',"cal.artifact-type.definition/v2" in compiled)
schema=read(O/'contracts/definition-registry-v2.schema.json');Draft202012Validator.check_schema(schema)
fixture={'schema_version':'cyberalchemy-lab-definition-registry/v2','artifact_type_ref':'cal.artifact-type.definition-registry/v2','expected_predecessor':base['registry'],'entries':[],'current_lookup':{},'publication_decision':base['registry']}
Draft202012Validator(schema).validate(fixture)
check('registry-v2-schema-shape-only-not-admission',True)
broken=copy.deepcopy(fixture);broken['definition_artifact_type_ref']='cal.artifact-type.definition/v2'
check('registry-v2-refuses-implicit-global-carrier',not Draft202012Validator(schema).is_valid(broken))
proto=read(O/'DESIGN-VERIFICATION.json');check('original-source-model-57-planning-checks',proto['status']=='PASS' and proto['check_count']==57 and not proto['active_runtime_wired'] and not proto['stateful_join_initialization_executed'])
check('no-tracked-file-mutations',subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True)=='')
result={'status':'PASS','scope':'Source/schema/projection/compatibility checks; no actual admission, authority or active runtime qualification','check_count':len(checks),'checks':checks,'canonical_definitions_changed':0,'proposed_successors':len(props)}
(O/'CONTRACT-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','check_count':len(checks)}))
