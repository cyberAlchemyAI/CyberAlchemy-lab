"""Bounded Root-owned T31 pure check; real API and Source guards never import."""
import hashlib,importlib.util,json,os,sys,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0002'
HERE=Path(__file__).absolute().parent
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable)==INSTALL/'bin/python'
def verify():
 raw=(BASE/'source-manifest.json').read_bytes();assert hashlib.sha256(raw).hexdigest()=='bd3df70ad187016da65bd6c3a73ac77c4e815a744102153ae72b0f90ae645241'
 rows=json.loads(raw)['files']
 originals=json.loads((BASE/'original-input-conservation.json').read_bytes())['declarations']
 for r in rows+originals:
  p=ROOT/r['path'];assert p.stat().st_size<=32*1024*1024 and not any(q.is_symlink()for q in(p,*p.parents));body=p.read_bytes();assert hashlib.sha256(body).hexdigest()==r['sha256']
  if 'size_bytes'in r:assert len(body)==r['size_bytes']
 return len(rows),len(originals)
before=verify();fd0=len(os.listdir('/proc/self/fd'));out={'schema_version':'lab-T31-Root-bounded-pure-controls/v1-candidate','authority_effect':'none','entry_rows':before,'actual_API_Source_native_installed_guard_or_live_lease':False,'known_independent_implementation_findings_remain_open':True,'task_complete':False};error=None
try:
 name='_Root_T31_bounded_controls_'+uuid.uuid4().hex;path=BASE/'controls.py';spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);module.main();out['result']='PASS-bounded-pure-controls-only'
except BaseException as exc:
 error=exc;out['result']='FAIL-preserved-pure-controls';out['exception_class']=type(exc).__name__
finally:
 out['exit_rows']=verify();out['FD_delta']=len(os.listdir('/proc/self/fd'))-fd0;assert out['FD_delta']==0
 path=HERE/'result.json';raw=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode();fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
 try:os.write(fd,raw);os.fsync(fd)
 finally:os.close(fd)
 print(json.dumps(out,sort_keys=True))
if error is not None:raise error
