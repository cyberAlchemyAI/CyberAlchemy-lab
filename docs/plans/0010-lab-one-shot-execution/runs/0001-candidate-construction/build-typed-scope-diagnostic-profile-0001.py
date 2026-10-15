"""Freeze a synthetic diagnostic group independently of its replay invocation.

This is not a genuine semantic review, operational policy or owner decision.
The predecessor/source pins come from the completed guarded signed replay009.
"""
import hashlib,importlib.util,importlib,json,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
TYPED=BASE/'typed-extension-preparation-v11'
SOURCE='56a9db7a496302d1811d55df2c217dadef01af9ee6b60889e7771e8b103f8674'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def guard():
 assert sha((TYPED/'source-manifest.json').read_bytes())==SOURCE
 for r in load(TYPED/'source-manifest.json')['files']:assert sha((ROOT/r['path']).read_bytes())==r['sha256']
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 guard()
 original=RUN/'typed-actual-source-comparison-0009.json';v=load(original)
 assert v['original_reader_guarded_exit_completed'] and v['actual_public_predecessor_binding']['result']=='PASS'
 assert v['actual_preimage_candidate_postimage']['reason']=='target outside authorized scope'
 name='_cal_typed_scope_profile_fixture_v11'
 s=importlib.util.spec_from_file_location(name,TYPED/'__init__.py',submodule_search_locations=[str(TYPED)])
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 F=importlib.import_module(name+'.test_postimage');F.PostimageTests.setUpClass();f=F.PostimageTests();f.setUp();C=f.C
 proposal=f.proposal;storage=v['actual_preimage_candidate_postimage']['transaction_scope_ref']
 proposal['scope_ref']=storage
 for target in proposal['targets']:
  target['artifact']['scope_ref']=storage
  prior=target['predecessor']
  if prior is not None:
   bound=v['actual_public_predecessor_binding']['predecessors'][prior['version_ref']]
   target['predecessor']=bound['public_header']
 b=v['runtime_catalog_binding']
 profile={'schema_version':'lab-exact-typed-scope-preparation-profile/v1-candidate',
  'storage_scope_ref':storage,'semantic_scope_ref':v['actual_preimage_candidate_postimage']['semantic_record_scopes'][0],
  'source_bindings':{'catalog_snapshot_digest':b['independent_catalog_snapshot_digest'],'catalog_profile_sha256':b['independent_catalog_profile_sha256'],
   'runtime_baseline_digest':b['actual_runtime_baseline_digest'],'runtime_projection_digest':b['actual_runtime_projection_digest'],
   'runtime_config_digest':b['actual_runtime_config_digest'],'runtime_head':b['actual_runtime_HEAD'],
   'representation_profile_sha256':v['actual_public_predecessor_binding']['representation_profile_sha256']},
  'proposal_structural_sha256':C.digest(proposal),'inspection_structural_sha256':C.digest(f.inspection),'impact_structural_sha256':C.digest(f.impact),
  'ordered_target_version_refs':[t['artifact']['version_ref'] for t in proposal['targets']],
  'ordered_decision_core_bindings':[t['decision_core_binding'] for t in proposal['targets']],
  'schema_bindings':proposal['schema_bindings'],'runtime_admission_authorized':False,'actual_owner_outcome':None,'authority_effect':'none'}
 path=RUN/'typed-scope-diagnostic-profile-0001.json';put(path,profile)
 put(RUN/'typed-scope-diagnostic-profile-envelope-0001.json',{'schema_version':'lab-isolated-scope-diagnostic-profile-envelope/v1-candidate',
  'result':'FROZEN-SYNTHETIC-DIAGNOSTIC','profile_binding':bind(path),'typed_source_binding':bind(TYPED/'source-manifest.json'),
  'signed_preimage_evidence_binding':bind(original),'generator_binding':bind(Path(__file__).resolve()),
  'synthetic_candidate_targets':True,'genuine_semantic_review_provided':False,'operational_scope_grant':False,
  'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'purpose':'Complete coupled hypothetical postimage against separately selected signed preimage; not admission-ready model change.'})
 guard()
 print(json.dumps({'result':'FROZEN-SYNTHETIC-DIAGNOSTIC','profile_binding':bind(path)}),flush=True)
if __name__=='__main__':main()
