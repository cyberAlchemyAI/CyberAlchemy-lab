from pathlib import Path
import hashlib,json,sys,subprocess,time
ROOT=Path(__file__).resolve().parents[6]
RUN=Path(__file__).resolve().parent
COMPONENT=ROOT/'product/lab/release-candidates/v1/interface/scope-routing-v1-completion-0001'
PIN='d3ce1094eb29d0634bc4c9ec3ea7ab217a43957c86385dad5985c5c9c62995eb'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
def guard():
 raw=(COMPONENT/'source-manifest.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN
 for row in json.loads(raw)['files']:
  p=Path(row['path']);assert not any(x.is_symlink() for x in [p,*p.parents]);assert p.stat().st_size==row['size_bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
guard();start=time.monotonic()
command=[str(INSTALL/'lib/abi/ld-linux-x86-64.so.2'),'--inhibit-cache','--library-path',str(INSTALL/'lib/abi'),str(INSTALL/'bin/python'),'-I','-X','utf8','-B','-S','-c',"import sys,runpy;sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2]);runpy.run_path(sys.argv[3],run_name='__main__')",str(INSTALL/'deps'),str(COMPONENT),str(COMPONENT/'checks.py')]
child=subprocess.run(command,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,timeout=180)
(RUN/'qualified.stdout').write_bytes(child.stdout);(RUN/'qualified.stderr').write_bytes(child.stderr);guard()
report={'result':'PASS' if child.returncode==0 else 'FAIL','exit_code':child.returncode,'elapsed_seconds':time.monotonic()-start,'command':command,'manifest_sha256':PIN,'entry_guard':'PASS','exit_guard':'PASS','stdout_sha256':hashlib.sha256(child.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(child.stderr).hexdigest(),'task_complete':False,'authority_effect':'none'}
with (RUN/'qualified-terminal-0001.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(child.stdout.decode(),child.stderr.decode());raise SystemExit(child.returncode)
