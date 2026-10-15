"""Real production launcher entry with a physical owned-source mutation observer."""
import hashlib,json,os,runpy,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7];HERE=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003'
config,config_sha,mode,result_path=sys.argv[1:];manifest=(HERE/'source-manifest.json').read_bytes();observed={'boundary_reached':False,'child_returncode':None};held=None;injected=None
monitor_id=4

def start(code,offset):
    global held,injected
    if code is subprocess.run.__code__ and not observed['boundary_reached']:
        observed['boundary_reached']=True
        if mode=='leaf':
            original=HERE/'composite.py';held=original.with_name('.T06-original-composite-held');original.rename(held);injected=original
            original.write_text('print("UNAPPROVED_SDK_FILE_EXECUTED",flush=True)\nraise RuntimeError("unapproved source")\n')
        elif mode=='parent':
            held=HERE.with_name('.T06-original-revision3-held');HERE.rename(held);HERE.mkdir();injected=HERE
            for name in ['bootstrap.py','composite.py','control.py','framing.py']:(HERE/name).write_text('print("UNAPPROVED_SDK_FILE_EXECUTED",flush=True)\n')
        else:raise AssertionError('unknown owned replacement mode')
def returned(code,offset,value):
    if code is subprocess.run.__code__:observed['child_returncode']=value.returncode
sys.monitoring.use_tool_id(monitor_id,'T06 real SDK replacement observer');sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,start);sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_RETURN,returned);sys.monitoring.set_local_events(monitor_id,subprocess.run.__code__,sys.monitoring.events.PY_START|sys.monitoring.events.PY_RETURN)
exit_code=None
try:
    sys.argv=[str(HERE/'launch.py'),'--launcher-source-sha256',hashlib.sha256(manifest).hexdigest(),'--config',config,'--config-sha256',config_sha]
    try:runpy.run_path(str(HERE/'launch.py'),run_name='__main__')
    except SystemExit as value:exit_code=value.code
finally:
    sys.monitoring.set_local_events(monitor_id,subprocess.run.__code__,0);sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,None);sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_RETURN,None);sys.monitoring.free_tool_id(monitor_id)
    if held is not None:
        if mode=='leaf':injected.unlink();held.rename(injected)
        else:
            for p in injected.iterdir():p.unlink()
            injected.rmdir();held.rename(HERE)
    observed.update(launcher_returncode=exit_code,production_callbacks_replaced=False,mutation_mode=mode)
    Path(result_path).write_text(json.dumps(observed,indent=2,sort_keys=True)+'\n')
raise SystemExit(exit_code)
