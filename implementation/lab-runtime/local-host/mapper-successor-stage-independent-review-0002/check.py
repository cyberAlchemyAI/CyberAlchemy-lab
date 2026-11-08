import os,sys,json,hashlib,types,tempfile,unittest
from pathlib import Path
from unittest import mock
from contextlib import ExitStack
R=Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';C=L/'mapper-successor-stage-0002';h=lambda b:hashlib.sha256(b).hexdigest()
f=(C/'freeze.json').read_bytes()
if h(f)!='c214e06c122186124a11f16e456257a1f800cfea8b05361da9d18247ece60311':raise RuntimeError('FREEZE')
pins={str(C/'freeze.json'):h(f)}
for row in json.loads(f)['file_bindings']:
 p=R/row['path'];b=p.read_bytes()
 if len(b)!=row['size'] or h(b)!=row['sha256']:raise RuntimeError('MEMBER')
 pins[str(p)]=h(b)
def audit(e,a):
 if e=='open' and isinstance(a[0],(bytes,str)) and Path(os.fsdecode(a[0])).name=='branch.snapshot':raise RuntimeError('ARCHIVE_OPEN_FORBIDDEN')
 if e in ('subprocess.Popen','os.system','os.exec','os.fork'):raise RuntimeError('PROCESS_EFFECT_FORBIDDEN')
sys.addaudithook(audit)
for name in ('anchored_copy','held_stage','stage','release','test_stage'):
 m=types.ModuleType(name);m.__file__=str(C/(name+'.py'));sys.modules[name]=m;exec(compile(Path(m.__file__).read_bytes(),m.__file__,'exec'),m.__dict__)
S=sys.modules['stage'];H=sys.modules['held_stage'];T=sys.modules['test_stage'];observed=[]
res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
if not res.wasSuccessful():raise RuntimeError('AUTHOR_SUITE')
pre=S.preflight()
# Independent preserved old R01 mechanism, expected refusal to perform a second read.
orig=Path.read_bytes;n=[0]
def race(p):
 if p==S.ADAPTER/'adapter.py':
  n[0]+=1
  if n[0]>1:return b'UNVERIFIED_EXECUTED=True\n'
 return orig(p)
with mock.patch.object(Path,'read_bytes',race):m=S._reviewed_adapter()
if n!=[1] or hasattr(m,'UNVERIFIED_EXECUTED'):raise RuntimeError('R01')
observed.append({'case':'R01','result':'one verified source read; second read never used'})
# mkdir success/open failure keeps consumed pathname without opening/adopting it again.
with tempfile.TemporaryDirectory(prefix='mapper-stage-openfail-') as d:
 attempt=Path(d)/'attempt';realopen=os.open;calls=[0];claims=[]
 class Capture(H.HeldAttempt):
  def __init__(self,p):super().__init__(p);claims.append(self)
 def fail_open(path,*a,**kw):
  if path=='attempt' and kw.get('dir_fd') is not None:
   calls[0]+=1;raise OSError('inert post-mkdir open fault')
  return realopen(path,*a,**kw)
 before=len(os.listdir('/proc/self/fd'))
 with ExitStack() as stack:
  for name,value in [('STAGE_EFFECT_ENABLED',True),('HeldAttempt',Capture)]:stack.enter_context(mock.patch.object(S,name,value))
  for name,value in [('preflight',{}),('selected',({}, {'attempt':str(attempt),'destination_root':str(attempt/'root')}, {})),('source_inventory',{}),('metadata',os.stat(__file__))]:stack.enter_context(mock.patch.object(S,name,return_value=value))
  stack.enter_context(mock.patch.object(os,'open',side_effect=fail_open))
  try:S.execute()
  except OSError:pass
  else:raise RuntimeError('OPENFAIL_DID_NOT_REFUSE')
 if calls!=[1] or not claims[0].claimed or claims[0].fd is not None or list(attempt.iterdir()) or len(os.listdir('/proc/self/fd'))!=before:raise RuntimeError('OPENFAIL_CUSTODY')
 observed.append({'case':'mkdir-success/open-failure','result':'claimed empty path retained; no UNKNOWN write without fd; all other owned fds closed; no reopen'})
# Close reports after actual release: all held fds attempted exactly once, no blind numeric retry.
with tempfile.TemporaryDirectory(prefix='mapper-stage-close-') as d:
 c=H.HeldAttempt(Path(d)/'attempt');c.claim();c.write('consumed.json',b'inert');c.mkdir('root',0o755)
 owned=[c.root_fd,c.fd,c.parent_fd];closed=[];realclose=os.close
 def close_fault(fd):
  realclose(fd);closed.append(fd)
  if fd==owned[0]:raise OSError('inert real-close-then-raise')
 with mock.patch.object(os,'close',side_effect=close_fault):
  try:c.close()
  except BaseExceptionGroup:pass
  else:raise RuntimeError('CLOSE_FAULT_HIDDEN')
  c.close()
 if closed!=owned or any(x is not None for x in (c.fd,c.root_fd,c.parent_fd)):raise RuntimeError('CLOSE_RETRY_OR_SKIP')
 observed.append({'case':'once-only close fault','result':'all three handles attempted; uncertainty raised; repeat close retries none'})
# Primary failure survives a cleanup fault and every remaining fd is closed.
with tempfile.TemporaryDirectory(prefix='mapper-stage-primary-') as d:
 c=H.HeldAttempt(Path(d)/'attempt');c.claim();c.mkdir('root',0o755);owned=[c.root_fd,c.fd,c.parent_fd];closed=[];primary=ValueError('selected primary')
 with mock.patch.object(os,'close',side_effect=close_fault):c.close(primary)
 if closed!=owned or not getattr(primary,'secondary_close_errors',()):raise RuntimeError('PRIMARY_CLEANUP')
 observed.append({'case':'primary plus close fault','result':'primary retained with secondary; all held handles attempted'})
# Losing-claim race occurs inside mkdir, after preflight, no writes to foreign claim.
with tempfile.TemporaryDirectory(prefix='mapper-stage-loser-') as d:
 attempt=Path(d)/'attempt';realmkdir=os.mkdir
 def competing(path,mode=0o777,*a,**kw):
  if path=='attempt':realmkdir(path,mode,*a,**kw);(attempt/'foreign').write_bytes(b'unchanged');raise FileExistsError('race')
  return realmkdir(path,mode,*a,**kw)
 with ExitStack() as stack:
  stack.enter_context(mock.patch.object(S,'STAGE_EFFECT_ENABLED',True))
  for name,value in [('preflight',{}),('selected',({}, {'attempt':str(attempt),'destination_root':str(attempt/'root')}, {})),('source_inventory',{}),('metadata',os.stat(__file__))]:stack.enter_context(mock.patch.object(S,name,return_value=value))
  stack.enter_context(mock.patch.object(os,'mkdir',side_effect=competing))
  try:S.execute()
  except FileExistsError:pass
  else:raise RuntimeError('NO_RACE_REFUSAL')
 if {p.name for p in attempt.iterdir()}!={'foreign'}:raise RuntimeError('FOREIGN_WRITE')
 observed.append({'case':'R02 losing claim race','result':'foreign original unchanged; no UNKNOWN or body writes'})
for p,digest in pins.items():
 if h(Path(p).read_bytes())!=digest:raise RuntimeError('DRIFT')
if os.path.lexists(pre['attempt']):raise RuntimeError('REAL_ATTEMPT_CREATED')
print(json.dumps({'pins':pins,'author_tests':res.testsRun,'independent_cases':observed,'preflight':pre,'archive_body_opened':False,'real_stage':'NOT_RUN'},indent=2,sort_keys=True))
