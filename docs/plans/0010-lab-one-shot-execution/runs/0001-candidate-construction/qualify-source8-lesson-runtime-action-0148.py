"""Actual native Source8 construction; common host qualification follows its freeze."""
import fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys,time
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
D=BASE/'source8-context-delivery-v1-action-0148'
M=BASE/'source8-mapped-context-v2-action-0148'
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 try:
  fcntl.flock(fd,fcntl.LOCK_SH)
  assert not (D/'source-manifest.json').exists()
  rows={}
  for parent in [M/'source-manifest.json',M/'packages/0001/manifest.json',BASE/'api-v25/source-manifest.json']:
   for row in json.loads(parent.read_bytes())['files']:rows[row['path']]=row
   rows[binding(parent)['path']]=binding(parent)
  for p in D.rglob('*'):
   if p.is_file() and p.suffix in ('.py','.json'):rows[binding(p)['path']]=binding(p)
  source={'schema_version':'lab-Source8-context-source/v1-candidate','files':[rows[k] for k in sorted(rows)],
    'external_dependency_bindings':[rows[k] for k in sorted(rows) if Path(k).is_absolute()],
    'qualified_mapper_source_binding':binding(M/'source-manifest.json'),
    'qualified_mapper_package_binding':binding(M/'packages/0001/manifest.json'),
    'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
    'authority_effect':'none','actual_owner_outcome':None,'common_host_qualification':False}
  save(D/'source-manifest.json',source)
  name='_cal_Source8_context_action_0148';spec=importlib.util.spec_from_file_location(name,D/'__init__.py',submodule_search_locations=[str(D)])
  m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
  b=__import__(name+'.build',fromlist=['build'])
  b.build(binding(D/'source-manifest.json')['sha256'],binding(M/'packages/0001/manifest.json')['sha256'])
  report={'schema_version':'lab-Source8-native-construction-proof/v1-candidate','result':'PASS',
    'mapper_source_binding':binding(M/'source-manifest.json'),'mapper_package_binding':binding(M/'packages/0001/manifest.json'),
    'context_source_binding':binding(D/'source-manifest.json'),'context_package_binding':binding(D/'packages/0001/manifest.json'),
    'source_file_count':len(rows),'unique_source_file_count':len(set(rows)),
    'source_total_bytes':sum((Path(r['path']) if Path(r['path']).is_absolute() else ROOT/r['path']).stat().st_size for r in rows.values()),
    'original_Source8_binding':binding(BASE/'current-participation-v8/source-manifest.json'),
    'original_Source8_period_binding':binding(BASE/'current-participation-v8/packages/0001/period.json'),
    'actual_common_API_calls':0,'qualification_ceiling':'native mapper/context construction only; actual common host proof still required',
    'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
  save(RUN/'Source8-lesson-runtime-action-0148.json',report);print(json.dumps(report),flush=True)
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
if __name__=='__main__':main()
