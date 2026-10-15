"""Owned inert destination ancestor race against preserved revision-0002 bytes."""
import hashlib,json,os,sys,tempfile,types,uuid
from pathlib import Path
OUT=Path(__file__).resolve().parent;HERE=OUT.parent/'full-learning-driver-0001';PRE=OUT/'revision2-preimages'
PRE.mkdir(exist_ok=False)
pins={'driver.py':'8cac7378563241cf8aab0cca822e34414738db6385bc86ff7c52bf57770b9968','capture.py':'979c76d1f974430044b7c266b09482a256bde8d03bac081c876728a2be49285c','observe.py':'c10eb6975a593876507880630259009cde98094c2c685dc22f076a6369aa7e8c','source-manifest-0002.json':'f8f22c679ab2cd46b951f0ffb2f2faa6919da7e0ebabd8df5eb5e1360af37d36','HANDOFF-0002.json':'ae4117f7f02b937483cd46147e935dacfaed808e66a8486406eb01ec8b552ed3'}
def sha(body):return hashlib.sha256(body).hexdigest()
for name,pin in pins.items():
 body=(HERE/name).read_bytes();assert sha(body)==pin;target=PRE/name
 with target.open('xb') as handle:handle.write(body)
D=types.ModuleType('_T35_revision2_owned_destination_'+uuid.uuid4().hex);D.__file__=str(PRE/'driver.py');sys.modules[D.__name__]=D
exec(compile((PRE/'driver.py').read_bytes(),D.__file__,'exec'),D.__dict__)
E=D.Episode.__new__(D.Episode);E.root_managers={};E.root_identities={};E.roots=[];E.retained=[];E.cohort='destination-inert-review';E.recorder=types.SimpleNamespace(emit=lambda value:None)
manager=D.OwnedTemporary(E,'cal-T35-write-review-original-');root=manager.path
E.roots.append(root);E.root_identities[root]=D.identity(root.stat())
foreign=Path(tempfile.mkdtemp(prefix='cal-T35-write-review-foreign-inert-'));foreign.chmod(0o700)
marker=b'PRIVATE_INERT_REVIEW_CAPTURED_MARKER'
(root/'journal').mkdir(mode=0o700)
fd=os.open(root/'journal/pending.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb') as stream:stream.write(marker)
state={'retention':None,'mutated':False};monitor=sys.monitoring;tool=next(i for i in [4,5] if monitor.get_tool(i) is None)
def returned(code,offset,value):
 if code is tempfile.mkdtemp.__code__:state['retention']=Path(value)
 elif code is Path.mkdir.__code__ and state['retention'] is not None and not state['mutated']:
  target=state['retention']/'captured-owned-evidence/journal'
  if target.exists():
   state['mutated']=True;target.rename(target.with_name('journal-preserved'));target.symlink_to(foreign,target_is_directory=True)
monitor.use_tool_id(tool,'T35 owned destination race')
monitor.register_callback(tool,monitor.events.PY_RETURN,returned)
for code in [tempfile.mkdtemp.__code__,Path.mkdir.__code__]:monitor.set_local_events(tool,code,monitor.events.PY_RETURN)
try:
 try:E.preserve_pending(root)
 except (ValueError,OSError):denied=True
 else:denied=False
finally:
 for code in [tempfile.mkdtemp.__code__,Path.mkdir.__code__]:monitor.set_local_events(tool,code,0)
 monitor.register_callback(tool,monitor.events.PY_RETURN,None);monitor.free_tool_id(tool)
manager.__exit__(None,None,None)
assert state['mutated'] and denied and (foreign/'pending.json').read_bytes()==marker and root.exists() and manager.keep
report={'schema_version':'lab-T35-optional-copy-destination-independent-counterevidence/v1-candidate','finding_confirmed':True,'reviewed_manifest_sha256':pins['source-manifest-0002.json'],'preserved_true_review_clone_origin':D.__file__,'actual_destination_parent_replaced_with_symlink':True,'captured_inert_private_marker_written_outside_retention_before_postcheck_refused':True,'postwrite_capture_refused':True,'original_uncertain_journal_retained':True,'fixture_roots':{'original':str(root),'retention':str(state['retention']),'foreign_new_inert_only':str(foreign)},'no_actual_private_bytes_or_keys_used':True,'real_Lab_Service_Session_native_or_lease_constructed':False,'original_Lab_callback_or_clock_substitution':False,'verdict':'REVISE-authoring-component','authority_effect':'none','task_complete':False}
target=OUT/'destination-counterevidence.json';target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':'DESTINATION-ANCESTOR-FINDING-CONFIRMED','report':str(target),'sha256':sha(target.read_bytes())}),flush=True)
