from pathlib import Path
import json,sys,hashlib,subprocess,time
ROOT=Path(__file__).resolve().parents[6]
RUN=Path(__file__).resolve().parent
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001'
PIN='c90dab117bd4eaa3c93afcac0155b1d817e4fa8ffd1b9951ed609a5adbf56c9a'
def guard():
 raw=(COMPONENT/'source-manifest.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN
 value=json.loads(raw)
 for row in value['files']+value['host_abi_inputs']:
  p=Path(row['path']);assert not any(x.is_symlink() for x in [p,*p.parents]) and p.stat().st_size==row['size_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 for row in value['original_source_files']:
  p=ROOT/row['path'];assert p.stat().st_size==row['size_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 return value
guard();results=[]
for name in ['probe_original_guarded.py','test_recovery.py','test_controls.py']:
 start=time.monotonic();command=[sys.executable,'-I','-B','-c',"import sys;sys.path.insert(0,sys.argv[1]);import runpy;runpy.run_path(sys.argv[2],run_name='__main__')",str(COMPONENT),str(COMPONENT/name)]
 child=subprocess.run(command,capture_output=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},timeout=180)
 (RUN/(name+'.qualified.stdout')).write_bytes(child.stdout);(RUN/(name+'.qualified.stderr')).write_bytes(child.stderr)
 row={'script':name,'command':command,'exit_code':child.returncode,'elapsed_seconds':time.monotonic()-start,'stdout_sha256':hashlib.sha256(child.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(child.stderr).hexdigest()};results.append(row);print(json.dumps(row),flush=True)
 if child.returncode:break
guard();report={'schema_version':'lab-T32-task-local-qualified/v1-candidate','result':'PASS' if len(results)==3 and all(r['exit_code']==0 for r in results) else 'FAIL','manifest_sha256':PIN,'entry_guard':'PASS','exit_guard':'PASS','terminals':results,'task_complete':False,'goal_complete':False,'authority_effect':'none'}
with (RUN/'qualified-terminal-0001.json').open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
raise SystemExit(0 if report['result']=='PASS' else 1)
