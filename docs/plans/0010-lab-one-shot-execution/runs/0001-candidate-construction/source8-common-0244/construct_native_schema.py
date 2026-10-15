"""Real native schema reader construction proof; no API14 qualification."""
import copy,fcntl,hashlib,importlib,importlib.util,json,os,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v14'
REPORT=OUT/'native-schema-construction.json'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
def main():
 assert not REPORT.exists() and not (API/'source-manifest.json').exists(),'construction requires unpublished unfrozen candidate'
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
 started=time.monotonic();cases=[];entry=False;exit_ok=False
 try:
  load('_cal_source13_schema_guard_0244',BASE/'api-integration-v13');G=importlib.import_module('_cal_source13_schema_guard_0244.guard')
  G.verify('213ebd20742b8f7c8af0aa6614b71f735d574e89d22c92c094c3657c0d189322');entry=True
  package='_cal_source14_native_schema_construction_0244';load(package,API)
  P=importlib.import_module(package+'.protocol');N=importlib.import_module(package+'.native_schema')
  for name in ('source8-session-participation','source8-lesson-fixture-participation'):
   D=P.source.source8_delivery_for(name)
   with D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE) as selected:
    v=selected.view;v.source8_context_producer=D;v.integrated_reader=D.reader;v.custody_signed_sources=selected
    before=set(selected.sources.schemas)
    raw,binding=N.original_schema(selected,'cal.artifact-type.typed-relation/v4')
    assert raw and P.source.sha(raw)==binding['schema_sha256']
    assert binding['source_cut']==selected.source_cut and 'cal.artifact-type.typed-relation/v4' not in before
    assert before==set(selected.sources.schemas)
    cases.append({'case':name+':actual-native-original-schema','result':'PASS','native_binding':binding,'original_bytes':len(raw)})
    for field,value in [('schema_sha256','0'*64),('schema_path','unselected:native-schema')]:
     wrong=copy.deepcopy(binding);wrong[field]=value
     try:N.original_schema(selected,'cal.artifact-type.typed-relation/v4',expected_binding=wrong)
     except ValueError as error:assert str(error)=='independent native schema binding differs'
     else:raise AssertionError('wrong independently selected native binding accepted')
     cases.append({'case':name+':wrong-'+field,'result':'actual-refusal'})
    try:N.original_schema(selected,'cal.artifact-type.typed-relation/v999')
    except ValueError as error:assert str(error)=='unselected native connection carrier'
    else:raise AssertionError('unselected native carrier accepted')
    cases.append({'case':name+':unselected-carrier','result':'actual-refusal'})
    assert before==set(selected.sources.schemas);selected.guard()
  status='PASS'
 except BaseException as error:
  status='FAIL';cases.append({'case':'construction-completion','result':'FAIL','error_class':type(error).__name__,'error':str(error)[:600]})
 finally:
  try:
   if 'G' in locals():G.verify('213ebd20742b8f7c8af0aa6614b71f735d574e89d22c92c094c3657c0d189322');exit_ok=True
  finally:
   result={'schema_version':'lab-real-native-schema-construction/v1-candidate','result':status,'construction_only':True,
    'API14_qualification':False,'native_helper_binding':bind(API/'native_schema.py'),'caller_binding':bind(Path(__file__).resolve()),
    'cases':cases,'full_source13_entry':entry,'full_source13_exit':exit_ok,'duration_seconds':time.monotonic()-started,
    'authority_effect':'none','actual_owner_outcome':None}
   with REPORT.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':status,'report_binding':bind(REPORT)}),flush=True)
 return 0 if status=='PASS' and exit_ok else 1
if __name__=='__main__':raise SystemExit(main())
