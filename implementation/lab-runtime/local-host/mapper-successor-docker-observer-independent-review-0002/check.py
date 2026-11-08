import hashlib,json,os,pathlib,sys,tempfile,types,unittest
from unittest.mock import patch
D=pathlib.Path(__file__).parent;L=D.parent;C=L/'mapper-successor-docker-observer-0002';R=L.parents[2]
h=lambda b:hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes()
if h(fraw)!='356a3abd41a28a3400f22f8e1aac35f33e7176893090c3a27783cd51b99b4a07':raise RuntimeError('FREEZE_DRIFT')
f=json.loads(fraw);pins={str(C/'freeze.json'):h(fraw)};raws={}
for row in f['file_bindings']:
 p=R/row['path'];raw=p.read_bytes()
 if h(raw)!=row['sha256'] or len(raw)!=row['size']:raise RuntimeError('MEMBER_DRIFT')
 pins[str(p)]=h(raw);raws[p.name]=raw
m=types.ModuleType('observer');m.__file__=str(C/'observer.py');sys.modules['observer']=m
exec(compile(raws['observer.py'],m.__file__,'exec'),m.__dict__)
t=types.ModuleType('tests');t.__file__=str(C/'tests.py')
exec(compile(raws['tests.py'],t.__file__,'exec'),t.__dict__)
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).endswith('branch.snapshot'):raise RuntimeError('NO_ARCHIVE')
 if event=='subprocess.Popen':
  argv=args[1]
  ok=(argv[0]==sys.executable and ('-c' in argv or argv==[sys.executable,'-B',str(C/'observer.py'),'--execute-reviewed-one-shot']))
  ok=ok or argv==m.PREFLIGHT
  if not ok:raise RuntimeError('UNSELECTED_PROCESS')
 if event in ('os.system','os.fork','os.exec'):raise RuntimeError('NO_EFFECT')
sys.addaudithook(audit)
original_temp=tempfile.TemporaryDirectory
# All disposable author fixtures live in reviewer-owned evidence, not candidate.
def temp(*args,**kw):
 kw['dir']=D
 return original_temp(*args,**kw)
with patch.object(tempfile,'TemporaryDirectory',temp):
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t))
 if not result.wasSuccessful():raise RuntimeError('AUTHOR_TEST_FAILURE')
findings=[]
with original_temp(dir=D) as scratch:
 root=pathlib.Path(scratch)/'observation';original_create=m.Observation.create_stream;held=[]
 def create(self,name):
  if name=='stderr':raise OSError('inert second-stream failure')
  fd=original_create(self,name);held.append(fd);return fd
 with patch.object(m.Observation,'create_stream',create):
  try:m._run_once(observation=root,preflight_fn=t.selected,spawn=lambda *a,**k:(_ for _ in ()).throw(AssertionError('NO_SPAWN')))
  except m.Refused:pass
  else:raise AssertionError('expected refusal')
 try:os.fstat(held[0])
 except OSError:pass
 else:os.close(held[0]);raise RuntimeError('R01_LEAK')
 findings.append({'id':'R01','case':'second stream creation failed before spawn; first stdout FD closed exactly once','capture':json.loads((root/'capture.json').read_bytes())['status']})

with original_temp(dir=D) as scratch:
 root=pathlib.Path(scratch)/'observation';foreign=pathlib.Path(scratch)/'foreign';held=[];original_close=os.close;state={'injected':False,'foreign_closed':False};foreign_fd=[]
 def create(self,name):
  fd=original_create(self,name);held.append(fd);return fd
 def close(fd):
  if held and fd==held[0] and not state['injected']:
   state['injected']=True;original_close(fd)
   replacement=os.open(foreign,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);foreign_fd.append(replacement)
   if replacement!=fd:raise AssertionError('fixture reuse failed')
   raise OSError('inert close succeeded then reported failure')
  if foreign_fd and fd==foreign_fd[0]:state['foreign_closed']=True
  return original_close(fd)
 class Pipe:
  def close(self):pass
 class Process:
  stdout=Pipe();stderr=Pipe()
  def poll(self):return 0
  def wait(self):return 0
 def capture(*args,**kw):return {'exit_code':1,'counts':[0,0],'retained':[0,0],'stdout_sha256':h(b''),'stderr_sha256':h(b''),'overflow':False,'capture_error_class':None,'pipe_tail_timeout':False,'signals':[],'child_preserved_after_signal':False}
 with patch.object(m.Observation,'create_stream',create),patch.object(m,'capture_process',capture),patch.object(m.os,'close',close):
  try:m._run_once(observation=root,preflight_fn=t.selected,spawn=lambda *a,**k:Process())
  except m.Refused:pass
  else:raise AssertionError('expected refusal')
 if state['foreign_closed']:raise RuntimeError('R02_FOREIGN_CLOSED')
 os.fstat(foreign_fd[0]);os.close(foreign_fd[0])
 findings.append({'id':'R02','case':'first stream close then raise; replacement fd stays open; reviewer closes own replacement after check','state':state})

with original_temp(dir=D) as scratch:
 root=pathlib.Path(scratch)/'observation';owned=m.Observation(root);owned.claim();ident=owned.identity;owned.close()
 original_close=os.close;closed=[];state={'failed':False}
 # Track only descriptors opened during postclose publication, then inject first leaf close.
 original_open=os.open;opened=[]
 def op(*args,**kw):
  fd=original_open(*args,**kw);opened.append(fd);return fd
 def cl(fd):
  closed.append(fd);original_close(fd)
  if not state['failed']:state['failed']=True;raise OSError('inert first postclose leaf-close failure')
 with patch.object(m.os,'open',op),patch.object(m.os,'close',cl):
  try:m.postclose_write(root,ident,'observation.json',b'{"status":"PROVISIONAL_OS_ZERO_FINAL_JOIN"}\n')
  except OSError:pass
  else:raise AssertionError('expected failure')
 live=[]
 for fd in opened:
  try:os.fstat(fd)
  except OSError:continue
  live.append(fd);original_close(fd)
 if live:raise RuntimeError('R03_LEAK')
 findings.append({'id':'R03','case':'postclose leaf-close failure attempts every directory/ancestor close; provisional file alone is not success','remaining_owned_fds':len(live)})
# Only selected read-only preflight; it may inspect Docker image/name, never create/start.
pre=m.preflight();pre.pop('preflight_stdout',None)
for p,pin in pins.items():
 if h(pathlib.Path(p).read_bytes())!=pin:raise RuntimeError('POSTDRIFT')
if m.OBSERVATION.exists() or m.ATTEMPT.exists():raise RuntimeError('REAL_ATTEMPT_APPEARED')
print(json.dumps({'author_tests':result.testsRun,'findings':findings,'preflight':pre,'pins':pins,'effect':'NOT_RUN','archive_body':'UNOPENED'},sort_keys=True))
