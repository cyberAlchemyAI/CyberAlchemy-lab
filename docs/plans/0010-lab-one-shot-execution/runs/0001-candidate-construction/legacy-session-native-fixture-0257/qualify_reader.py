"""Actual independent cold native/reader proof; no common API qualification."""
import fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
PRODUCER=BASE/'legacy-session-fixture-source-v1-action-0148';READER=BASE/'legacy-session-fixture-reader-v1-action-0148'
SOURCE='f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2';PACKAGE='8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def bootstrap(n,p):
 spec=importlib.util.spec_from_file_location(n,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(spec);sys.modules[n]=m;spec.loader.exec_module(m)
def main():
 assert not (OUT/'reader-proof.json').exists() and not (READER/'source-manifest.json').exists()
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 start=time.monotonic();checks=[];entry=False;exit_ok=False
 try:
  bootstrap('_cal_legacy_native_api14_guard',BASE/'api-integration-v14');G=__import__('_cal_legacy_native_api14_guard.guard',fromlist=['verify']);G.verify('aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240');entry=True
  assert bind(PRODUCER/'source-manifest.json')['sha256']==SOURCE and bind(PRODUCER/'packages/0001/manifest.json')['sha256']==PACKAGE
  rows={}
  for p in [PRODUCER/'source-manifest.json',PRODUCER/'packages/0001/manifest.json']:
   for row in json.loads(p.read_bytes())['files']:rows[row['path']]=row
   rows[bind(p)['path']]=bind(p)
  for p in READER.iterdir():
   if p.is_file():rows[bind(p)['path']]=bind(p)
  value={'schema_version':'lab-distinct-legacy-reader-source/v1-candidate','files':[rows[k] for k in sorted(rows)],'producer_source_binding':bind(PRODUCER/'source-manifest.json'),'producer_package_binding':bind(PRODUCER/'packages/0001/manifest.json'),
   'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'authority_effect':'none','actual_owner_outcome':None,'fixture_only':True,'qualification':False}
  with (READER/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
  pin=bind(READER/'source-manifest.json')['sha256'];name='_cal_legacy_native_fixture_reader_0257';bootstrap(name,READER);R=__import__(name+'.reader',fromlist=['SelectedReader']);reader=R.SelectedReader(pin,SOURCE,PACKAGE)
  cuts=[]
  for index in range(2):
   with reader.open_signed(SOURCE,PACKAGE) as selected:
    assert type(selected) is reader.adapter.SignedSources and type(selected.view) is reader.Inspection
    assert selected.source_cut==reader.adapter.source.cut(selected.view)
    assignment=selected.sources.resolve(reader.records.ASSIGNMENT+'@'+reader.records.VERSION)[0]
    assert assignment.artifact['identity_ref']==reader.records.ASSIGNMENT
    assert assignment.body['payload']['eligible_agent_ref']==reader.records.PROFILE+'@'+reader.records.VERSION
    assert not any('typed-relation' in c for c in selected.sources.schemas)
    selected.guard();cuts.append(selected.source_cut)
    checks.append({'case':'independent-native-cold-'+str(index+1),'result':'PASS','domain_record_count':len(selected.records),'typed_v3_connection_count':sum(s['carrier_ref']=='cal.artifact-type.typed-relation/v3' for s in selected.view.subjects.values()),'source_cut':selected.source_cut})
  assert cuts[0]==cuts[1];reader.guard();status='PASS'
 except BaseException as error:status='FAIL';checks.append({'case':'reader-proof','result':'FAIL','error_class':type(error).__name__,'error':str(error)[:700]})
 finally:
  try:
   if 'G' in locals():G.verify('aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240');exit_ok=True
  finally:
   result={'schema_version':'lab-independent-native-legacy-reader-proof/v1-candidate','result':status,'construction_only':True,'common_API_qualified':False,'checks':checks,'reader_source_binding':bind(READER/'source-manifest.json') if (READER/'source-manifest.json').exists() else None,'producer_source_binding':bind(PRODUCER/'source-manifest.json'),'producer_package_binding':bind(PRODUCER/'packages/0001/manifest.json'),'full14entry':entry,'full14exit':exit_ok,'duration_seconds':time.monotonic()-start,'authority_effect':'none','actual_owner_outcome':None}
   with (OUT/'reader-proof.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':status,'proof_binding':bind(OUT/'reader-proof.json')}),flush=True)
 return 0 if status=='PASS' and exit_ok else 1
if __name__=='__main__':raise SystemExit(main())
