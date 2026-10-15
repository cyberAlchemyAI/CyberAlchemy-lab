"""Verify closed routing shape through the original offline protocol registry.

These cases use explicit shape-only bytes; no route, grant or public call exists.
"""
import copy,hashlib,importlib.util,json
from pathlib import Path
from jsonschema import Draft202012Validator
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
PACKAGE=ROOT/'product/lab/release-candidates/v1/interface/typed-host-composition-v1'
PIN='baf5b9bcf1331501b038a82a27fb2bab3c46ec2e5932718478e341b6bbf27188'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def guard():
 assert bind(PACKAGE/'source-manifest.json')['sha256']==PIN
 v=json.loads((PACKAGE/'source-manifest.json').read_bytes())
 for r in v['files']+v['input_bindings']:assert bind(ROOT/r['path'])==r
 return v
def main():
 manifest=guard();schema=json.loads((PACKAGE/'routing.schema.json').read_bytes());Draft202012Validator.check_schema(schema)
 builder=ROOT/'docs/proposals/0007-lab-integrated-schema-package/resources.py'
 spec=importlib.util.spec_from_file_location('_cal_typed_host_routing_shape_resources',builder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 validator=Draft202012Validator(schema,registry=module.build_registry())
 b={'ref':'fixture:shape-only:original-bytes','sha256':hashlib.sha256(b'{}').hexdigest()}
 signed=json.loads((RUN/'typed-actual-source-comparison-0010.json').read_bytes())
 good={'schema_version':'lab-typed-preparation-routing/v1-candidate','scope_ref':'project:shape-only-no-grant','source_cut':signed['selected_source_cut'],'proposal_binding':b,'inspection_binding':b,'helper_source_binding':b,'helper_proof_binding':b,'catalog_profile_binding':b,'catalog_review_binding':b,'catalog_snapshot_digest':signed['independent_C04_snapshot_digest'],'representation_profile_binding':b,'canonical_writable_authority_ref':'cal.artifact-type.typed-relation/v3','schema_destinations':[{'schema_binding':b,'runtime_schema_path':'runtime/schemas/shape-only.json'}],'scope_preparation_profile_binding':None,'record_basis':'complete-current-and-exact-prospective-postimage','actual_owner_outcome':None,'authority_effect':'none'}
 cases=[]
 def check(name,value,expected):
  actual=validator.is_valid(value);assert actual is expected,(name,list(validator.iter_errors(value)))
  cases.append({'case':name,'result':'PASS','expected_shape_valid':expected,'actual_shape_valid':actual})
 check('closed route shape',good,True)
 for key,value in [('actual_runtime_grant',True),('actor',{}),('runtime_admission_authorized',True)]:
  x=copy.deepcopy(good);x[key]=value;check('undeclared '+key,x,False)
 x=copy.deepcopy(good);x.pop('helper_source_binding');check('missing helper source',x,False)
 x=copy.deepcopy(good);x['schema_destinations']*=2;check('duplicated destination row',x,False)
 x=copy.deepcopy(good);x['helper_source_binding']['sha256']='invalid';check('malformed source pin',x,False)
 x=copy.deepcopy(good);x['schema_destinations'][0]['runtime_schema_path']='/tmp/absolute.json';check('absolute schema destination',x,False)
 guard();rows={r['path']:r for r in manifest['files']+manifest['input_bindings']}
 for p in [PACKAGE/'source-manifest.json',builder,Path(__file__).resolve(),RUN/'typed-actual-source-comparison-0010.json']:
  r=bind(p);rows[r['path']]=r
 for p in (builder.parent/'schemas').glob('*.json'):
  r=bind(p);rows[r['path']]=r
 value={'schema_version':'lab-typed-host-routing-shape-checks/v1-candidate','result':'PASS','actual_cases':len(cases),'cases':cases,'source_binding':bind(PACKAGE/'source-manifest.json'),'files':[rows[k] for k in sorted(rows)],'shape_only_fixture':True,'schema_regex_does_not_establish_semantic_path_or_inventory_safety':True,'original_offline_protocol_registry_used':True,'actual_public_calls':0,'public_handler_registered':False,'runtime_qualified':False,'actual_runtime_grant':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'claim_ceiling':'Eight closed routing shape checks only. Semantic selection, path uniqueness/no-dot checks, signed policy, actual host composition, source/Actor guards, journals and full original public qualification remain open.'}
 with (RUN/'typed-host-routing-shape-checks-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'PASS','actual_cases':len(cases),'runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
