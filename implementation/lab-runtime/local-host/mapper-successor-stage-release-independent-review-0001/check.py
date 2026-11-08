import sys,os,json,hashlib,types,unittest
from pathlib import Path
from unittest import mock
R=Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';C=L/'mapper-successor-stage-release-0001';H=lambda b:hashlib.sha256(b).hexdigest()
f=(C/'freeze.json').read_bytes()
if H(f)!='543f3f21bc0542a73fbcbc5980c353c3a610ef806d4a7942b6839340fb912443':raise RuntimeError('FREEZE')
pins={str(C/'freeze.json'):H(f)}
for row in json.loads(f)['file_bindings']:
 p=R/row['path'];b=p.read_bytes()
 if len(b)!=row['size'] or H(b)!=row['sha256']:raise RuntimeError('PIN')
 pins[str(p)]=H(b)
def audit(e,a):
 if e=='open' and isinstance(a[0],(str,bytes)) and Path(os.fsdecode(a[0])).name=='branch.snapshot':raise RuntimeError('PRIVATE_BODY_FORBIDDEN')
 if e in ('subprocess.Popen','os.system','os.exec','os.fork'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit)
for n in ('release','test_release'):
 m=types.ModuleType(n);m.__file__=str(C/(n+'.py'));sys.modules[n]=m;exec(compile(Path(m.__file__).read_bytes(),m.__file__,'exec'),m.__dict__)
A=sys.modules['release'];T=sys.modules['test_release']
f2=(A.STAGE/'freeze.json').read_bytes()
if H(f2)!=A.STAGE_FREEZE_SHA:raise RuntimeError('STAGE_FREEZE')
pins[str(A.STAGE/'freeze.json')]=H(f2)
for row in json.loads(f2)['file_bindings']:
 p=R/row['path'];b=p.read_bytes()
 if H(b)!=row['sha256'] or len(b)!=row['size']:raise RuntimeError('STAGE_MEMBER')
 pins[str(p)]=H(b)
pins[str(A.STAGE_REVIEW)]=H(A.STAGE_REVIEW.read_bytes())
res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
if not res.wasSuccessful():raise RuntimeError('AUTHOR_TESTS')
pre=A.preflight();cases=[]
# Same checked buffer despite adversarial second path read; reject preloaded substitutes.
orig=Path.read_bytes;reads={};names=('anchored_copy','held_stage','stage');sentinels={n:types.ModuleType(n) for n in names}
for m in sentinels.values():m.FORGED=True
def swapped(p):
 if p.parent==A.STAGE and p.name in {n+'.py' for n in names}:
  reads[p.name]=reads.get(p.name,0)+1
  if reads[p.name]>1:return b'FORGED=True\n'
 return orig(p)
with mock.patch.dict(sys.modules,sentinels),mock.patch.object(Path,'read_bytes',swapped):
 stage=A.basis()
 if hasattr(stage,'FORGED') or stage.HeldAttempt.__module__!='held_stage' or any(sys.modules[n] is not sentinels[n] for n in names):raise RuntimeError('ISOLATION')
if reads!={n+'.py':1 for n in names}:raise RuntimeError('REREAD')
cases.append('exact one-read buffers; forged preloaded module names replaced then restored')
original=A._exact_module
def fail(name,raw,path):
 if name=='held_stage':raise RuntimeError('inert loader failure')
 return original(name,raw,path)
with mock.patch.dict(sys.modules,sentinels),mock.patch.object(A,'_exact_module',fail):
 try:A.basis()
 except RuntimeError as e:
  if str(e)!='inert loader failure':raise
 else:raise RuntimeError('LOADER_ERROR_HIDDEN')
 if any(sys.modules[n] is not sentinels[n] for n in names):raise RuntimeError('RESTORE_ON_FAILURE')
cases.append('module names restored after partial loader failure')
fake=types.SimpleNamespace(STAGE_EFFECT_ENABLED=False);calls=[]
def no_preflight():raise ValueError('inert preflight refusal')
fake.preflight=no_preflight;fake.execute=lambda:calls.append('execute')
with mock.patch.object(A,'basis',return_value=fake):
 try:A.execute_reviewed_one_shot()
 except ValueError:pass
 else:raise RuntimeError('PREFLIGHT_REFUSAL_HIDDEN')
if fake.STAGE_EFFECT_ENABLED or calls:raise RuntimeError('PRE_EFFECT')
cases.append('preflight failure prevents enable and execution')
for error in (OSError('inert final close'),KeyboardInterrupt()):
 fake.preflight=lambda:None
 def fail_execute():raise error
 fake.execute=fail_execute
 with mock.patch.object(A,'basis',return_value=fake):
  try:A.execute_reviewed_one_shot()
  except BaseException as caught:
   if caught is not error:raise RuntimeError('PRIMARY_REPLACED')
  else:raise RuntimeError('FALSE_RETURN')
 if fake.STAGE_EFFECT_ENABLED:raise RuntimeError('FLAG_NOT_RESET')
cases.append('OSError and interruption propagate unchanged without return; enabled flag reset')
for p,dig in pins.items():
 if H(Path(p).read_bytes())!=dig:raise RuntimeError('DRIFT')
if os.path.lexists(pre['attempt']):raise RuntimeError('ATTEMPT_CREATED')
print(json.dumps({'pins':pins,'author_tests':res.testsRun,'independent_cases':cases,'live_preflight':pre,'real_effect':'NOT_RUN','archive_body_opened':False},sort_keys=True,indent=2))
