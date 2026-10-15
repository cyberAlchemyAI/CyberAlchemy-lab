"""Root selected whole authored inert suite, no original Lab effects."""
import os, fcntl
def fds():
    out={}
    for name in os.listdir('/proc/self/fd'):
        try:
            fd=int(name);s=os.fstat(fd);out[name]=[s.st_dev,s.st_ino,s.st_mode,fcntl.fcntl(fd,fcntl.F_GETFL),fcntl.fcntl(fd,fcntl.F_GETFD)]
        except OSError:continue
    return out
before=fds()
import contextlib, datetime, hashlib, io, json, runpy, sys, traceback
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0005'
OUT=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
mf=P/'source-manifest.json'
assert sha(mf.read_bytes())=='15e99f08c061cac75938a37a20e98952187e1979355426a8501e3c67df74df05'
rows=json.loads(mf.read_bytes())['files']
assert len(rows)==58
def selected():
    for row in rows:
        p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
        b=p.read_bytes();assert sha(b)==row['sha256']and len(b)==row['size_bytes'],str(p)
selected()
captured=io.StringIO();failure=None;exit_error=None
try:
    with contextlib.redirect_stdout(captured):runpy.run_path(str(P/'controls.py'),run_name='__main__')
except BaseException as e:failure={'class':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
finally:
    try:selected()
    except BaseException as e:exit_error={'class':type(e).__name__,'message':str(e)}
raw=captured.getvalue()
with (OUT/'stdout.txt').open('x')as f:f.write(raw)
after=fds()
result={'schema_version':'lab-T31-Root-authored-inert-controls/v1','authority_effect':'none',
    'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'result':'PASS-whole-authored-inert-suite'if failure is None and exit_error is None else 'FAIL-preserved-inert-suite',
    'failure':failure,'exit_error':exit_error,'all58_entry_exit_checked':True,
    'FD_delta':len(after)-len(before),'FD_map_unchanged':after==before,
    'actual_producer_WorkflowRun_Source_API_native_lease_or_authority':False,
    'full_genuine_T31_or_runtime_complete':False}
if raw.strip():
    try:result['suite_result']=json.loads(raw.strip())
    except Exception:result['suite_result_unparsed']=True
with (OUT/'result.json').open('x')as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(result,sort_keys=True))
raise SystemExit(0 if failure is None and exit_error is None else 1)

