"""Root current Source/installed guards only; never retroqualifies interrupted run."""
import os,fcntl
def fds():
    out={}
    for n in os.listdir('/proc/self/fd'):
        try:
            d=int(n);s=os.fstat(d);out[n]=[s.st_dev,s.st_ino,s.st_mode,fcntl.fcntl(d,fcntl.F_GETFL),fcntl.fcntl(d,fcntl.F_GETFD)]
        except OSError:continue
    return out
before=fds()
import datetime,hashlib,importlib.util,json,sys,time,traceback,uuid
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE=Path(__file__).parent
packet=json.loads((RUN/'T32/native-node-recovery-root-0004/qualification-selection.json').read_bytes())
SOURCE=packet['api_source_binding']['sha256']
def sha(b):return hashlib.sha256(b).hexdigest()
def emit(name,v):
    with (HERE/name).open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def load(name,row):
    p=ROOT/row['path'];raw=p.read_bytes();assert sha(raw)==row['sha256'],str(p)
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    exec(compile(raw,str(p),'exec'),m.__dict__)
    return m
mods=packet['module_bindings'];phases=[];errors=[];missing=[];guard=None;executor=None
def phase(label,fn):
    start=time.monotonic();fn();row={'phase':label,'result':'PASS','seconds':time.monotonic()-start};phases.append(row);emit('phase-%02d.json'%len(phases),row)
try:
    guard=load('_Root_current_guard_'+uuid.uuid4().hex,mods['api_guard'])
    phase('full-current-Source-entry',lambda:guard.verify(SOURCE))
    for k in ['checked_io','stage_io','closure']:load(k,mods[k])
    deps=load('_Root_dependencies_'+uuid.uuid4().hex,mods['dependencies'])
    control=load('_Root_control_'+uuid.uuid4().hex,mods['control'])
    native=load('_Root_native_'+uuid.uuid4().hex,mods['executor'])
    row=packet['ontology_execution_selection_binding'];raw=control.capture(ROOT/row['path'],row['sha256'])
    executor=native.SelectedOntologyExecutor(raw,row['sha256'],deps,control)
    phase('complete-current-827-executor-guard',executor.guard)
    def present_scope():
        localmissing=[];count=0
        for key in ['adoption_manifest','execution_manifest']:
            selected=packet['reference_bindings'][key]
            table=json.loads(control.capture(ROOT/selected['path'],selected['sha256']))['files']
            for row in table:
                p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
                if not p.exists():
                    assert str(p)=='/tmp/cal-T32-rust-provenance-root-0001/observations/result.json'
                    assert row['sha256']=='b126e629fc314325391dffcf3a93609196ad6218e6efaf54ff4e98ffaae0fe5a'
                    localmissing.append(row);continue
                body=control.capture(p,row['sha256'],limit=max(1,row['size_bytes']),size=row['size_bytes'])
                assert len(body)==row['size_bytes'];count+=1
        assert len(localmissing)==1 and count==328
        missing[:]=localmissing
    phase('all-present-guard153-and-execution175-with-explicit-one-historical-gap',present_scope)
    row=packet['api_profile_binding'];phase('current-profile',lambda:control.capture(ROOT/row['path'],row['sha256']))
except BaseException as e:errors.append({'class':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()})
finally:
    for label,fn in ([('full-current-Source-exit',lambda:guard.verify(SOURCE))]if guard else [])+([('complete-current-827-executor-exit',executor.guard)]if executor else []):
        try:phase(label,fn)
        except BaseException as e:errors.append({'phase':label,'class':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()})
    after=fds()
    result={'schema_version':'lab-current-guards-after-interruption/v1-candidate','authority_effect':'none',
     'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runtime_guards_pass':not errors,
     'phases':phases,'errors':errors,'historical_missing_selected_declarations':missing,
     'old176_current_physical_closure_pass':False,'FD_delta':len(after)-len(before),'FD_map_unchanged':after==before,
     'actual_native_or_lease_executed':False,'interrupted_attempt_retroqualified':False,
     'old_missing_locator_restored_or_identity_aliased':False,'whole_task_complete':False}
    emit('result.json',result)
    print(json.dumps({'runtime_guards_pass':not errors,'errors':errors,'historical_missing':len(missing),'phases':len(phases),'FD_delta':result['FD_delta'],'FD_map_unchanged':result['FD_map_unchanged']},sort_keys=True))
raise SystemExit(0 if not errors else 1)

