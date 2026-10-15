"""Build real Source8 native mapping; original Source5/Source8 stay immutable."""
import fcntl,hashlib,importlib.metadata,importlib.util,json,os,platform,sys
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';MAPPER=BASE/'source8-mapped-context-v2-action-0148'
SOURCE='cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36'
PACKAGE='c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f'
ADAPTER='78d8150086ed41f6f2c2218805a2387caab1e5931b2619a894330557cb30d23c'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 assert not (MAPPER/'source-manifest.json').exists()
 rows={}
 for path in [BASE/'current-participation-v8/source-manifest.json',BASE/'current-participation-v8/packages/0001/manifest.json',BASE/'current-source-adapter-v7/source-manifest.json']:
  for r in json.loads(path.read_bytes())['files']:rows[r['path']]=r
  rows[str(path.relative_to(ROOT))]=bind(path)
 for path in MAPPER.glob('*'):
  if path.is_file() and path.suffix in ('.py','.json'):rows[str(path.relative_to(ROOT))]=bind(path)
 value={'schema_version':'lab-Source8-native-mapper-source/v1-candidate','files':[rows[k] for k in sorted(rows)],
  'original_source_binding':bind(BASE/'current-participation-v8/source-manifest.json'),'original_package_binding':bind(BASE/'current-participation-v8/packages/0001/manifest.json'),
  'adapter_source_binding':bind(BASE/'current-source-adapter-v7/source-manifest.json'),
  'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
  'authority_effect':'none','actual_owner_outcome':None,'fixture_only':False,'qualification':False}
 assert value['original_source_binding']['sha256']==SOURCE and value['original_package_binding']['sha256']==PACKAGE and value['adapter_source_binding']['sha256']==ADAPTER
 with (MAPPER/'source-manifest.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
 pin=bind(MAPPER/'source-manifest.json')['sha256']
 fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 try:
  fcntl.flock(fd,fcntl.LOCK_SH)
  name='_cal_Source8_mapper_action_0148';spec=importlib.util.spec_from_file_location(name,MAPPER/'__init__.py',submodule_search_locations=[str(MAPPER)])
  m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
  b=__import__(name+'.build',fromlist=['build']);b.build(pin)
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'source_binding':bind(MAPPER/'source-manifest.json'),'package_binding':bind(MAPPER/'packages/0001/manifest.json'),'qualification':False}),flush=True)
if __name__=='__main__':main()
