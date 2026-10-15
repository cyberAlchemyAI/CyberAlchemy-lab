"""Distinct signed typed-v3 fixture source; original Source5 stays immutable."""
import ast,fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
HERE=BASE/'legacy-session-fixture-source-v1-action-0148';READER=BASE/'legacy-session-fixture-reader-v1-action-0148'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 assert not (HERE/'source-manifest.json').exists(),'frozen source cannot be replaced'
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 try:
  prior=BASE/'current-participation-v5/source-manifest.json';raw=prior.read_bytes();assert hashlib.sha256(raw).hexdigest()=='dc0462ce29d24bf571b56c0c0eeafad0511812a8464ce66e52914671256e7cb4'
  rows={r['path']:r for r in json.loads(raw)['files']};rows[bind(prior)['path']]=bind(prior)
  for p in [*HERE.iterdir(),*READER.iterdir(),Path(__file__).resolve()]:
   assert p.is_file()
   if p.suffix=='.py':ast.parse(p.read_bytes())
   rows[bind(p)['path']]=bind(p)
  value={'schema_version':'lab-distinct-legacy-typed-v3-fixture-source/v1-candidate','files':[rows[k] for k in sorted(rows)],
   'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
   'implementation_code_binding':bind(READER/'reader.py'),'implementation_entrypoint_ref':str((READER/'reader.py').relative_to(ROOT))+'#SelectedReader.open_signed',
   'original_Source5_binding':bind(prior),'fixed_new_episode_binding':bind(HERE/'episode-contract.json'),
   'original_Source5_period_binding':bind(BASE/'current-participation-v5/packages/0001/period.json'),
   'distinct_fixture_only':True,'original_Assignment_renewed':False,'original_signer_restored':False,'Session_memory_rehydrated':False,
   'qualification':False,'authority_effect':'none','actual_owner_outcome':None}
  with (HERE/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
  name='_cal_legacy_session_native_fixture_source_0257';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
  module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
  build=__import__(name+'.build',fromlist=['main']);build.main(bind(HERE/'source-manifest.json')['sha256'])
  print(json.dumps({'source_binding':bind(HERE/'source-manifest.json'),'package_binding':bind(HERE/'packages/0001/manifest.json'),'construction_only':True}),flush=True)
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
if __name__=='__main__':main()
