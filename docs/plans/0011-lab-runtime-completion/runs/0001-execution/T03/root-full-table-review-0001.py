"""Check all four retained exact family file tables using selected kernel bytes."""
import hashlib,importlib.abc,importlib.util,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).absolute().parents[6]
HERE=Path(__file__).absolute().parent
KERNEL=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001/capture.py'
PIN='748a605d1ed0a6ac68de2fd87c407c49a9723e60bd3941c9f8498e702729ea3c'
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/source-input-capture-v1-completion-0001/source-manifest.json'
COMPONENT_PIN='227af612b244dcc860d18f57f47ca8e8f1b6657b51bd4e90e169a3b118c11549'
FAMILY=ROOT/'product/lab/release-candidates/v1/interface/current-session-fixtures-v1-completion-0001/instances/diagnostic-0004'
ROLES={
 'source':('2a13711a7acae4983cd32904ac4c2ced1cab4e83c32ae96c51462d1226bcf887',1263),
 'reader':('04081f3d717c5b94178e399a58217e055e3f860fa5062fbb01f30b3c135bc07a',1330),
 'mapped':('d1d216af2ae305f68f933111dd67b0b93be95c538a74b5943fd4a0bd46d50b2f',1336),
 'context':('6f1fb3fcd9f487b76f5e1708a7bda1b157a4bbbb42bfef1e3baae9f350410071',2438),
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def component_guard():
 raw=COMPONENT.read_bytes();assert sha(raw)==COMPONENT_PIN
 for row in json.loads(raw)['files']:
  value=(ROOT/row['path']).read_bytes();assert sha(value)==row['sha256'] and len(value)==row['size_bytes']
component_guard();raw=KERNEL.read_bytes();assert sha(raw)==PIN
class Loader(importlib.abc.SourceLoader):
 selected_source_sha256=PIN
 def get_filename(self,name):return str(KERNEL)
 def get_data(self,path):
  assert path==str(KERNEL)
  return raw
 def get_code(self,name):return compile(raw,str(KERNEL),'exec',dont_inherit=True)
name='_cal_root_T03_full_tables_0001';assert name not in sys.modules
spec=importlib.util.spec_from_file_location(name,KERNEL,loader=Loader());module=importlib.util.module_from_spec(spec)
sys.modules[name]=module;spec.loader.exec_module(module)
observations=[]
for role,(pin,count) in ROLES.items():
 path=FAMILY/role/'source-manifest.json';body=module.capture_one(ROOT,{'path':str(path.relative_to(ROOT)),'sha256':pin},code_sha256=PIN)
 manifest=json.loads(body);assert len(manifest['files'])==count
 start=time.monotonic();actual=module.verify_all(ROOT,manifest['files'],code_sha256=PIN,selected_external=manifest.get('external_dependency_bindings',()))
 assert actual==count
 observations.append({'role':role,'manifest_sha256':pin,'rows_read_and_hashed_fresh':actual,'elapsed_seconds':time.monotonic()-start})
component_guard();assert sha(KERNEL.read_bytes())==PIN
result={'schema_version':'lab-T03-root-full-table-review/v1-candidate','status':'PASS-four-exact-file-tables',
 'kernel_sha256':PIN,'component_sha256':COMPONENT_PIN,'observations':observations,
 'total_row_occurrences_verified':sum(x['rows_read_and_hashed_fresh'] for x in observations),
 'authority_effect':'none','task_complete':False,'original_callbacks_replaced':False,
 'scope':'Exact selected helper at its actual true origin, checking all four original current family file tables. No new family, schema/permission/native-history/Session/effect or complete timing-margin qualification.',
 'checked_at':datetime.now(timezone.utc).isoformat()}
out=HERE/'root-full-table-review-0001.json'
with out.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'status':result['status'],'rows':result['total_row_occurrences_verified'],'output':str(out)}))
