"""Initial frozen authoring defects reproduced with new inert owned fixtures only."""
import hashlib,importlib.util,json,os,shutil,sys,tempfile,types
from pathlib import Path
RUN=Path(__file__).resolve().parent;PRE=RUN/'preimages'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
D=module('_T35_initial_driver_review_clone',PRE/'driver.py');C=D.C;cases=[]
root=Path(tempfile.mkdtemp(prefix='cal-T35-review-owned-'));os.chmod(root,0o700)
foreign=Path(tempfile.mkdtemp(prefix='cal-T35-review-foreign-inert-'));os.chmod(foreign,0o700)
def put(path,raw):
 fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'wb') as s:s.write(raw)
put(root/'pending.json',b'owned selected pending marker');put(foreign/'different.json',b'UNSELECTED_INERT_REVIEW_MARKER')
E=D.Episode.__new__(D.Episode);E.roots=[root];E.root_identities={root:D.identity(root.stat())};E.retained=[];E.cohort='review-inert';events=[];E.recorder=types.SimpleNamespace(emit=events.append)
observed={'mutated':False,'retention':None};mid=4

def start(code,offset):
 if code is shutil.copytree.__code__ and not observed['mutated']:
  observed['mutated']=True;(root/'pending.json').rename(root/'selected-retained.json');(root/'pending.json').symlink_to(foreign/'different.json')
def returned(code,offset,value):
 if code is tempfile.mkdtemp.__code__:observed['retention']=str(value)
sys.monitoring.use_tool_id(mid,'T35 own copy race reviewer');sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,start);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_RETURN,returned);sys.monitoring.set_local_events(mid,shutil.copytree.__code__,sys.monitoring.events.PY_START);sys.monitoring.set_local_events(mid,tempfile.mkdtemp.__code__,sys.monitoring.events.PY_RETURN)
try:
 try:E.preserve_pending(root)
 except ValueError:pass
 else:raise AssertionError('expected postcopy mismatch refusal missing')
finally:
 sys.monitoring.set_local_events(mid,shutil.copytree.__code__,0);sys.monitoring.set_local_events(mid,tempfile.mkdtemp.__code__,0);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_START,None);sys.monitoring.register_callback(mid,sys.monitoring.events.PY_RETURN,None);sys.monitoring.free_tool_id(mid)
retention=Path(observed['retention']);copied=retention/'owned-original/pending.json';assert observed['mutated'] and copied.read_bytes()==b'UNSELECTED_INERT_REVIEW_MARKER'
cases.append({'case':'ordinary copytree followed actual replaced owned leaf symlink before later anchored mismatch refused','finding_confirmed':True,'unselected_inert_bytes_copied':True,'retention_root':str(retention),'no_real_keys_or_operator_state_used':True})
# Deliberately fail only monitoring initialization primitive in this isolated
# process. No original API/source callbacks or clock are ever loaded/replaced.
O=module('_T35_initial_observer_review_clone',PRE/'observe.py');observer=O.Observer(RUN,lambda value:None);register=sys.monitoring.register_callback
try:
 def fail(*args,**kwargs):raise RuntimeError('owned reviewer initialization failure')
 sys.monitoring.register_callback=fail
 try:observer.start()
 except RuntimeError:pass
 else:raise AssertionError('expected registration failure')
finally:sys.monitoring.register_callback=register
label=sys.monitoring.get_tool(observer.tool);assert label=='cal-full-learning-qualification';observer.close();assert sys.monitoring.get_tool(5) is None
cases.append({'case':'partial Observer.start leaves reserved tool until explicit close; Episode constructor currently lacks that path','finding_confirmed':True,'tool_retained_after_initialization_exception':True,'reviewer_explicit_cleanup_completed':True,'original_API_or_source_callbacks_replaced':False})
# Strict software pin separation and typed owned observation.
assert C.read_owned(foreign/'different.json',foreign,D.identity(foreign.stat()))==b'UNSELECTED_INERT_REVIEW_MARKER'
try:C.read(foreign/'different.json',None)
except ValueError:pass
else:raise AssertionError('null software pin accepted')
cases.append({'case':'ownedstate typed capture works while software null digest refuses','result':'PASS'})
value={'schema_version':'lab-T35-initial-driver-independent-controls/v1-candidate','reviewed_authoring_manifest_sha256':'fd7ae6b6e096ec95a9bcaa60340dab9a6f0f56f462a5a436552719364d4651a1','cases':cases,'actual_runtime_or_Service_or_Session_or_native_constructed':False,'lease_lock_acquired':False,'new_inert_fixtures_only':True,'production_callbacks_or_clocks_replaced':False,'initial_review_verdict':'REVISE','author_has_acknowledged_findings':True,'authority_effect':'none','task_complete':False}
out=RUN/'initial-counterevidence.json';out.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'INITIAL-FINDINGS-CONFIRMED','cases':len(cases),'report':str(out)}),flush=True)
