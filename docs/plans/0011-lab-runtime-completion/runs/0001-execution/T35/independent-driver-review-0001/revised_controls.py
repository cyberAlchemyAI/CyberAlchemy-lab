"""Independent owned controls; no Lab constructors, lease, keys or native calls."""
import ast,hashlib,json,os,shutil,sys,tempfile,types,uuid
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
OUT=Path(__file__).resolve().parent
HERE=OUT.parent/'full-learning-driver-0001'
PIN='f8f22c679ab2cd46b951f0ffb2f2faa6919da7e0ebabd8df5eb5e1360af37d36'
HPIN='ae4117f7f02b937483cd46147e935dacfaed808e66a8486406eb01ec8b552ed3'
def sha(raw):return hashlib.sha256(raw).hexdigest()
raw=(HERE/'source-manifest-0002.json').read_bytes();assert sha(raw)==PIN
assert sha((HERE/'HANDOFF-0002.json').read_bytes())==HPIN
manifest=json.loads(raw);selected={}
def guard():
 for row in manifest['files']:
  body=(ROOT/row['path']).read_bytes()
  assert len(body)==row['size_bytes'] and sha(body)==row['sha256'],row['path']
  selected[row['path']]=body
guard()
def load(name,path):
 body=selected[str(path.relative_to(ROOT))]
 module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
 exec(compile(body,str(path),'exec'),module.__dict__);return module
D=load('_T35_independent_revised_'+uuid.uuid4().hex,HERE/'driver.py');C=D.C;O=D._observer_module
cases=[];fixtures=[]
def passed(name,**facts):cases.append({'case':name,'result':'PASS',**facts})
def put(path,body):
 path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as handle:handle.write(body)
def episode():
 E=D.Episode.__new__(D.Episode)
 E.roots=[];E.root_identities={};E.root_managers={};E.retained=[];E.cohort='independent-inert';E.recorder=types.SimpleNamespace(emit=lambda event:None)
 manager=D.OwnedTemporary(E,'cal-T35-independent-owned-');root=manager.path
 E.roots.append(root);E.root_identities[root]=D.identity(root.stat());fixtures.append(str(root))
 return E,manager,root
def watch(code,callback,operation):
 monitor=sys.monitoring;tool=next(i for i in [4,5] if monitor.get_tool(i) is None)
 monitor.use_tool_id(tool,'T35 independent inert race')
 monitor.register_callback(tool,monitor.events.PY_START,callback)
 monitor.set_local_events(tool,code,monitor.events.PY_START)
 try:return operation()
 finally:
  monitor.set_local_events(tool,code,0);monitor.register_callback(tool,monitor.events.PY_START,None);monitor.free_tool_id(tool)
def refuses(callback):
 try:callback()
 except (ValueError,OSError):return
 raise AssertionError('expected refusal')

# Actual current preservation function, with new inert state and fake credential
# marker only. The copy must contain selected permitted bytes, never credentials.
E,manager,root=episode();put(root/'journal/pending.json',b'approved pending fixture');put(root/'reader.pem',b'INERT_NOT_A_KEY')
E.preserve_pending(root);manager.__exit__(None,None,None)
copy=Path(E.retained[-1]['protected_copy_root'])/'captured-owned-evidence'
assert root.exists() and (root/'reader.pem').exists()
assert (copy/'journal/pending.json').read_bytes()==b'approved pending fixture' and not (copy/'reader.pem').exists()
assert E.retained[-1]['credential_files_copied'] is False
passed('actual preserve_pending retains original and copies only captured permitted bytes',original_retained=True,credential_marker_not_copied=True)

# Same actual read_owned boundary after first inventory read, before the actual
# second capture of the selected leaf. Symlink body must never be read/copied.
E,manager,root=episode();put(root/'pending.json',b'approved selected marker')
foreign=Path(tempfile.mkdtemp(prefix='cal-T35-independent-foreign-inert-'));foreign.chmod(0o700);fixtures.append(str(foreign));put(foreign/'different.json',b'UNSELECTED_INERT_MARKER')
count=[0]
def leaf_race(code,offset):
 count[0]+=1
 if count[0]==2:
  (root/'pending.json').rename(root/'retained-original.json');(root/'pending.json').symlink_to(foreign/'different.json')
watch(C.read_owned.__code__,leaf_race,lambda:refuses(lambda:E.preserve_pending(root)))
manager.__exit__(None,None,None)
assert count[0]==2 and manager.keep and root.exists() and (root/'retained-original.json').read_bytes()==b'approved selected marker'
assert len(E.retained)==1 and 'protected_copy_root' not in E.retained[0]
passed('actual selected leaf replacement refuses before copying and uncertain original survives',original_retained=True,unselected_body_copied=False)

# Ancestor attachment replacement at the same real capture boundary must refuse
# against the original root inode; both newly owned directories are preserved.
E,manager,root=episode();put(root/'pending.json',b'original inode selected marker');count=[0];old=root.with_name(root.name+'-retained-inode')
def parent_race(code,offset):
 count[0]+=1
 if count[0]==2:
  root.rename(old);root.mkdir(mode=0o700);put(root/'pending.json',b'foreign replacement inode marker')
watch(C.read_owned.__code__,parent_race,lambda:refuses(lambda:E.preserve_pending(root)))
manager.__exit__(None,None,None);fixtures.append(str(old))
assert count[0]==2 and manager.keep and (old/'pending.json').read_bytes()==b'original inode selected marker' and len(E.retained)==1
passed('actual root replacement refuses original inode selection and keeps uncertainty directories',original_inode_journal_retained=True)

# Actual retention-directory creation starts only after all allowed byte strings
# were captured. Replace original leaf then: destination must still use the
# approved captured bytes, not reread the new symlink or marker.
E,manager,root=episode();put(root/'pending.json',b'captured approved marker');changed=[False]
def after_capture(code,offset):
 if not changed[0]:
  changed[0]=True;(root/'pending.json').rename(root/'retained-before-write.json');(root/'pending.json').symlink_to(foreign/'different.json')
watch(tempfile.mkdtemp.__code__,after_capture,lambda:E.preserve_pending(root))
copy=Path(E.retained[-1]['protected_copy_root'])/'captured-owned-evidence';manager.__exit__(None,None,None)
assert changed[0] and manager.keep and (copy/'pending.json').read_bytes()==b'captured approved marker'
passed('actual retention write uses captured bytes after source replacement',unselected_body_copied=False,original_retained=True)

E,manager,root=episode();put(root/'pending.json',b'custody failure retained marker');root.chmod(0o755)
refuses(lambda:E.preserve_pending(root));manager.__exit__(None,None,None);assert manager.keep and root.exists()
root.chmod(0o700)
passed('capture custody failure after preserve selection keeps original before context exit')

E,manager,root=episode();put(root/'pending.json',b'nonpending disposable marker');manager.__exit__(None,None,None)
assert not root.exists();passed('ordinary new owned root cleanup remains effective')

# Partial instrumentation failures are scoped to this pure reviewer process.
# No Lab/source callback or clock is loaded or substituted.
register=sys.monitoring.register_callback
for fail_at,persistent in [(1,False),(2,False),(3,False),(2,True)]:
 observer=O.Observer(ROOT,lambda value:None,False);calls=[0];slot=next(i for i in [5,4] if sys.monitoring.get_tool(i) is None)
 def interrupted(*args):
  calls[0]+=1
  if calls[0]==fail_at or (persistent and calls[0]>=fail_at):raise RuntimeError('owned initialization failure')
  return register(*args)
 sys.monitoring.register_callback=interrupted
 try:
  try:observer.start()
  except RuntimeError:pass
  else:raise AssertionError('instrumentation interruption did not occur')
 finally:sys.monitoring.register_callback=register
 assert observer.tool is None and sys.monitoring.get_tool(slot) is None
 passed('actual Observer.start frees tool after registration failure',failure_stage=fail_at,persistent=persistent)

# Strict independent software pin and separately typed owned capture.
for label,callback in [
 ('software null digest',lambda:C.read(foreign/'different.json',None)),
 ('software wrong digest',lambda:C.read(foreign/'different.json','0'*64)),
 ('software malformed digest',lambda:C.read(foreign/'different.json','self-derived')),
 ('owned wrong root inode',lambda:C.read_owned(foreign/'different.json',foreign,[0,0,os.getuid(),0o700])),
 ('owned foreign pathname',lambda:C.read_owned(Path('/etc/hostname'),foreign,D.identity(foreign.stat()))),
 ('owned credentials',lambda:C.read_owned(foreign/'reader.pem',foreign,D.identity(foreign.stat())))]:
 refuses(callback);passed(label+' refuses')
assert C.read(foreign/'different.json',sha(b'UNSELECTED_INERT_MARKER'))==b'UNSELECTED_INERT_MARKER'
assert C.read_owned(foreign/'different.json',foreign,D.identity(foreign.stat()))==b'UNSELECTED_INERT_MARKER'
passed('explicit pinned software and exact owned custody succeed separately')

# Controlled qualification-module code does not create any Lab resource.
module_path=foreign/'inert-module.py';module_raw=b'VALUE=42\n';put(module_path,module_raw);name='_T35_independent_origin_'+uuid.uuid4().hex
m=C.module(name,module_path,C.read(module_path,sha(module_raw)))
assert m.__file__==str(module_path) and m.VALUE==42
refuses(lambda:C.module(name,module_path,module_raw))
passed('captured qualification module has true origin and cached collision refuses')

events=[];observer=O.Observer(ROOT,events.append,False);observer.start()
try:
 def primary():raise RuntimeError('PRIVATE_PRIMARY_CANARY')
 def metadata_failure():raise LookupError('PRIVATE_METADATA_CANARY')
 try:observer.measure('independent-pure-metadata-failure',primary,metadata_failure)
 except RuntimeError:pass
 else:raise AssertionError('primary exception swallowed')
 assert observer.metadata_errors>0 and observer.callback_errors==0
 rendered=json.dumps(events);assert 'PRIVATE_PRIMARY_CANARY' not in rendered and 'PRIVATE_METADATA_CANARY' not in rendered
 assert any(e.get('event')=='trusted-exception' and e.get('exception_class')=='RuntimeError' for e in events)
 passed('diagnostic metadata failures preserve primary exception and private arguments stay absent')
finally:observer.close()

# Independent exact body comparison against original selected caller, not the
# author's generated delta string alone. All former inline negatives retained
# in the security helper; positive removes precisely that declared block.
caller=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-0275/caller.py'
lines=selected[str(caller.relative_to(ROOT))].decode().splitlines(keepends=True)
assert ''.join(lines[321:411])==(HERE/'caller-lines-322-411-preimage.txt').read_text()
pre=''.join(lines[321:408]);assert pre==(HERE/'lifecycle-preimage.py').read_text()
expected=pre.replace("'source8-lesson-fixture-participation'",'SOURCE_NAME').replace("P.ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v3-action-0148/preparation.py'",'APPLICATION_METHOD').replace("method.parent.parent/'lesson-assessment-v2-action-0148/preparation.py'",'ASSESSMENT_METHOD').replace('tempfile.TemporaryDirectory(','OWNED_TEMPORARY(')
security=(HERE/'security_lifecycle.py').read_text();assert security[security.index('def source8_lifecycle'):]==expected
start=expected.index(' bad=copy.deepcopy(attachment)');end=expected.index(' application=M[',start)
positive=(expected[:start]+expected[end:]).replace("return ['foreign-Session-attachment',",'return [')
actual=(HERE/'positive_lifecycle.py').read_text();assert actual[actual.index('def source8_lifecycle'):]==positive
for path in HERE.glob('*.py'):ast.parse(selected[str(path.relative_to(ROOT))])
passed('original complete 87-line function and 90-line excerpt exact; security and positive only declared deltas')
guard()
report={'schema_version':'lab-T35-revised-driver-independent-controls/v1-candidate','result':'PASS-owned-authoring-controls','reviewed_source_manifest_sha256':PIN,'reviewed_handoff_sha256':HPIN,'fresh_manifest_rows_verified_entry_exit':len(manifest['files']),'checks_count':len(cases),'checks':cases,'fixture_paths':fixtures,'real_Lab_Source_Service_Session_or_native_constructed':False,'lease_lock_acquired':False,'original_Lab_callbacks_or_clocks_replaced':False,'monitor_primitive_failures_only_in_isolated_review_process':True,'no_task_or_runtime_qualification_claim':True,'authority_effect':'none','task_complete':False}
out=OUT/'revised-controls-result.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':report['result'],'checks':len(cases),'manifest_rows':len(manifest['files']),'report':str(out),'report_sha256':sha(out.read_bytes())}),flush=True)
