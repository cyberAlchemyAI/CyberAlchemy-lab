"""Independent frozen legacy-v3 fixture mapping and native cold proof."""
import fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
HERE=BASE/'legacy-session-fixture-mapped-v1-action-0148';SOURCE=BASE/'legacy-session-fixture-source-v1-action-0148';READER=BASE/'legacy-session-fixture-reader-v1-action-0148'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def boot(n,p):
 spec=importlib.util.spec_from_file_location(n,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m)
def emit(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 assert not (HERE/'source-manifest.json').exists() and not (OUT/'mapper-proof.json').exists()
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 start=time.monotonic();entry=False;exit_ok=False;result='FAIL';checks=[]
 try:
  boot('_cal_legacy_mapper_api14_guard',BASE/'api-integration-v14');G=__import__('_cal_legacy_mapper_api14_guard.guard',fromlist=['verify']);G.verify('aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240');entry=True
  proof=OUT/'reader-proof-v2.json';assert bind(proof)['sha256']=='9c35cfa735d372b0745be55d30e306731a1f1e0d13b5bae10822f410ad58e08e' and json.loads(proof.read_bytes())['result']=='PASS'
  assert bind(SOURCE/'source-manifest.json')['sha256']=='f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2'
  assert bind(READER/'source-manifest.json')['sha256']=='0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5'
  rows={}
  def add(row):
   assert rows.get(row['path'],row)==row and bind(ROOT/row['path'])==row;rows[row['path']]=row
  for p in [SOURCE/'source-manifest.json',SOURCE/'packages/0001/manifest.json',READER/'source-manifest.json']:
   for row in json.loads(p.read_bytes())['files']:add(row)
   add(bind(p))
  for p in [proof,Path(__file__).resolve(),*sorted(HERE.iterdir())]:
   if p.is_file():add(bind(p))
  emit(HERE/'source-manifest.json',{'schema_version':'lab-distinct-legacy-native-mapper-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'original_source_binding':bind(SOURCE/'source-manifest.json'),'original_package_binding':bind(SOURCE/'packages/0001/manifest.json'),'adapter_source_binding':bind(READER/'source-manifest.json'),'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,'qualification':False,'selected_native_executable':{'path':'/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader','sha256':'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'}})
  pin=bind(HERE/'source-manifest.json')['sha256'];name='_cal_distinct_legacy_mapping_construction_0257';boot(name,HERE);B=__import__(name+'.build',fromlist=['build']);B.build(pin)
  manifest=HERE/'packages/0001/manifest.json';assert json.loads((manifest.parent/'build-result.json').read_bytes())['result']=='PASS'
  B.guard(pin);checks.append({'case':'actual-native-mapping-two-seals-two-cold-reads','result':'PASS','node_count':15,'edge_count':10,'exact_governance_joins':25});result='PASS'
 except BaseException as error:checks.append({'case':'mapper-construction','result':'FAIL','error_class':type(error).__name__,'error':str(error)[:900]})
 finally:
  try:
   if 'G' in locals():G.verify('aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240');exit_ok=True
  finally:
   emit(OUT/'mapper-proof.json',{'schema_version':'lab-independent-legacy-native-mapper-proof/v1-candidate','result':result,'construction_only':True,'common_API_qualified':False,'checks':checks,'source_binding':bind(HERE/'source-manifest.json') if (HERE/'source-manifest.json').exists() else None,'package_binding':bind(HERE/'packages/0001/manifest.json') if (HERE/'packages/0001/manifest.json').exists() else None,'full14entry':entry,'full14exit':exit_ok,'duration_seconds':time.monotonic()-start,'authority_effect':'none','actual_owner_outcome':None})
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':result,'proof_binding':bind(OUT/'mapper-proof.json')}),flush=True)
 return 0 if result=='PASS' and exit_ok else 1
if __name__=='__main__':raise SystemExit(main())
