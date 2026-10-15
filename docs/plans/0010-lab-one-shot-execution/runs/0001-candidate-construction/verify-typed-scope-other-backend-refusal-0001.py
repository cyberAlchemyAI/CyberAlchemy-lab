"""Verify the scope helper cannot reinterpret an original effect-authority refusal.

Pure hypothetical copies only; original backend/source guards remain unchanged.
"""
import hashlib,importlib.util,json,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
TYPED=ROOT/'product/lab/release-candidates/v1/interface/typed-extension-preparation-v11'
SOURCE='56a9db7a496302d1811d55df2c217dadef01af9ee6b60889e7771e8b103f8674'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def guard():
 assert bind(TYPED/'source-manifest.json')['sha256']==SOURCE
 for row in json.loads((TYPED/'source-manifest.json').read_bytes())['files']:
  path=ROOT/row['path'];assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
def main():
 guard();name='_cal_typed_scope_other_refusal_diagnostic'
 spec=importlib.util.spec_from_file_location(name,TYPED/'__init__.py',submodule_search_locations=[str(TYPED)])
 package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
 module=__import__(name+'.test_scope_preparation',fromlist=['ScopePreparationTests'])
 module.ScopePreparationTests.setUpClass();fixture=module.ScopePreparationTests();fixture.setUp();C=fixture.f.C
 # Independently repin this deliberately unauthorized hypothetical config so
 # the complete original backend is reached instead of an earlier hash refusal.
 fixture.f.config['allowed_effects']=[]
 fixture.f.expected_config_digest=C.digest(fixture.f.config)
 fixture.profile['source_bindings']['runtime_config_digest']=C.digest(fixture.f.config)
 before=[C.digest(x) for x in [fixture.f.projection,fixture.f.config,fixture.f.proposal]]
 try:fixture.check()
 except module.A.WireFault as error:
  assert str(error)=='original backend error is not the exact declared scope refusal'
  assert isinstance(error.__context__,C.RuntimeFault)
  original_refusal=str(error.__context__)
  assert original_refusal=='effect outside provisioned authority'
 else:raise AssertionError('effect-authority refusal was reinterpreted as a scope hypothesis')
 assert before==[C.digest(x) for x in [fixture.f.projection,fixture.f.config,fixture.f.proposal]]
 guard()
 value={'schema_version':'lab-typed-scope-original-error-boundary/v1-candidate','result':'PASS','actual_cases':1,'original_backend_refusal':original_refusal,'scope_hypothesis_not_returned':True,'actual_inputs_unchanged':True,'original_backend_and_source_guards_unchanged':True,'typed_source_binding':bind(TYPED/'source-manifest.json'),'runner_binding':bind(Path(__file__).resolve()),'actual_public_calls':0,'actual_transactions_written':0,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'claim_ceiling':'One pure hypothetical original-backend refusal check; no public handler, current authenticated source, operational grant or admission.'}
 with (RUN/'typed-scope-other-backend-refusal-0001.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'PASS','original_backend_refusal':original_refusal,'actual_cases':1,'actual_transactions_written':0}),flush=True)
if __name__=='__main__':main()
