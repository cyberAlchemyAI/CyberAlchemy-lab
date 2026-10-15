"""Actual immutable SDK main; observer mutates only an owned inert config."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[8]
HERE=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003'
INSTALL=HERE.parents[1]/'runtime-dependencies-v2-completion-0001/installations/0004'
sys.path[:0]=[str(INSTALL/'deps'),str(HERE)]
import composite as C
import control as K
path_text,pin,mode,output=sys.argv[1:];path=Path(path_text);root=path.parent;observed={'read_checkpoint_count':0,'parse_calls':0,'preflight_calls':0,'mutation_performed':False};held=None;injected=None
original=path.read_bytes();monitor_id=4

def mutation():
    global held,injected
    observed['mutation_performed']=True
    if mode in ['leaf-replace','leaf-symlink','leaf-symlink-before']:
        held=path.with_name('owned-original-config-retained.json');path.rename(held);injected=path
        if mode=='leaf-replace':
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as s:s.write(original)
        else:path.symlink_to(held)
    elif mode in ['parent-replace','parent-symlink-before']:
        held=root.with_name(root.name+'-owned-retained');root.rename(held);injected=root
        if mode=='parent-replace':
            root.mkdir(mode=0o700);fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as s:s.write(original)
        else:root.symlink_to(held,target_is_directory=True)
    else:raise AssertionError('unknown owned mutation')

def start(code,offset):
    if code is K._read_exact.__code__:
        observed['read_checkpoint_count']+=1
        if mode in ['leaf-replace','leaf-symlink','parent-replace'] and not observed['mutation_performed']:mutation()
    elif code is K.parse.__code__:observed['parse_calls']+=1
    elif code is C.preflight.__code__:observed['preflight_calls']+=1
sys.monitoring.use_tool_id(monitor_id,'T06 actual main owned config observer');sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,start)
for target in [K._read_exact.__code__,K.parse.__code__,C.preflight.__code__]:sys.monitoring.set_local_events(monitor_id,target,sys.monitoring.events.PY_START)
try:
    if mode.endswith('-before'):mutation()
    sys.argv=[str(HERE/'composite.py'),'--config',path_text,'--config-sha256',pin]
    result=C.main()
finally:
    for target in [K._read_exact.__code__,K.parse.__code__,C.preflight.__code__]:sys.monitoring.set_local_events(monitor_id,target,0)
    sys.monitoring.register_callback(monitor_id,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(monitor_id)
    if held is not None:
        if mode.startswith('leaf'):injected.unlink();held.rename(injected)
        else:
            if injected.is_symlink():injected.unlink()
            else:
                for p in injected.iterdir():p.unlink()
                injected.rmdir()
            held.rename(root)
observed.update(returncode=result,main_origin=str(HERE/'composite.py'),main_code_filename=C.main.__code__.co_filename,production_callbacks_replaced=False,mode=mode,selected_config_bytes_restored=path.read_bytes()==original)
Path(output).write_text(json.dumps(observed,indent=2,sort_keys=True)+'\n')
raise SystemExit(result)
