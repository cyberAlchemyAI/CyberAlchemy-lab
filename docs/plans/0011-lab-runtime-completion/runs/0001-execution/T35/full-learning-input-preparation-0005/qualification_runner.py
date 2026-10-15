"""Exact pinned own pure qualification. No Lab runtime/lease constructions."""
import hashlib,importlib.util,json,os,stat,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
D=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DPIN='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def run(pin):
 C=load('_T35_v2_qualification_capture',ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/full-learning-driver-0004/capture.py');manifest=json.loads(C.read(HERE/'source-manifest.json',pin));deps=json.loads(C.read(D,DPIN));fdstart=len(list(Path('/proc/self/fd').iterdir()))
 def guard():
  for row in manifest['files']:
   raw=C.read(ROOT/row['path'],row['sha256']);C.require(len(raw)==row['size_bytes'],'selected source size differs')
  installation={row['destination']:{'sha256':row['sha256'],'size_bytes':row['size_bytes'],'mode':0o755 if row['kind'] in {'interpreter','native-executable'} else 0o644} for row in deps['inputs']}
  installation.update(deps['wheel_members']);installation['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
  for path,row in installation.items():
   raw=C.read(I/path,row['sha256']);C.require(len(raw)==row['size_bytes'] and stat.S_IMODE((I/path).stat().st_mode)==row['mode'],'selected installed bytes/mode differ')
  C.require(len(installation)==1010,'dependency row count differs');return {'source_rows':len(manifest['files']),'installed_rows':len(installation)}
 entry=guard();start=time.monotonic();controls=load('_T35_v5_final_inputs',HERE/'controls.py').check();exit=guard()
 C.require(len(list(Path('/proc/self/fd').iterdir()))==fdstart,'qualification descriptors leaked')
 return {'result':'PASS-pure-selected-component','pid':os.getpid(),'selected_source_manifest_sha256':pin,'dependency_selection_sha256':DPIN,'entry_guard':entry,'exit_guard':exit,
  'controls':controls,'elapsed_seconds':time.monotonic()-start,'FD_delta':0,'actual_runtime_or_lease':False,'authority_effect':'none','whole_T35_complete':False,'task_complete':False}
if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True))
