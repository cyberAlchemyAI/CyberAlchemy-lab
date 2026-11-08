import sys,os,json,hashlib,types,unittest,time
from pathlib import Path
from unittest import mock
R=Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/mapper-successor-docker-controller-0001';h=lambda b:hashlib.sha256(b).hexdigest()
f=(C/'freeze.json').read_bytes()
if h(f)!='d9e435c8caee9e97887d69e8602504ceb31eebac48032b75f2e7c54077916108':raise RuntimeError('FREEZE')
pins={str(C/'freeze.json'):h(f)}
for row in json.loads(f)['file_bindings']:
 p=R/row['path'];b=p.read_bytes()
 if len(b)!=row['size'] or h(b)!=row['sha256']:raise RuntimeError('PIN')
 pins[str(p)]=h(b)
commands=[]
def audit(e,a):
 if e=='open' and isinstance(a[0],(bytes,str)) and Path(os.fsdecode(a[0])).name=='branch.snapshot':raise RuntimeError('ARCHIVE_FORBIDDEN')
 if e=='subprocess.Popen':
  argv=a[1]
  if not (argv[0]=='/usr/bin/docker' and argv[1:3] in (['image','inspect'],['container','inspect'])):raise RuntimeError('NON_READONLY_SUBPROCESS')
  commands.append(argv)
 if e in ('os.system','os.exec','os.fork'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(audit)
for n in ('anchored_copy','held_stage','root_guard','output_verifier','docker_protocol','controller','tests'):
 m=types.ModuleType(n);m.__file__=str(C/(n+'.py'));sys.modules[n]=m;exec(compile(Path(m.__file__).read_bytes(),m.__file__,'exec'),m.__dict__)
P=sys.modules['docker_protocol'];T=sys.modules['tests'];S=sys.modules['controller']
res=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(T))
if not res.wasSuccessful():raise RuntimeError('AUTHOR_SUITE')
pre=S.preflight();found=[]
# Subprocess adapter finalization ordering, using inert pipe/proc objects only.
class Pipe:
 def __init__(self,label,fail=False):self.label=label;self.fail=fail;self.closed=False
 def fileno(self):return 901 if self.label=='out' else 902
 def close(self):
  self.closed=True
  if self.fail:raise OSError('inert stream close fault')
class Proc:
 pid=99999999
 def __init__(self,fail):self.stdout=Pipe('out',fail);self.stderr=Pipe('err');self.waits=0
 def wait(self,**kw):self.waits+=1;return 0
 def poll(self):return 0
class Selector:
 def register(self,*a):pass
 def get_map(self):return {}
 def close(self):pass
proc=Proc(True)
with mock.patch.object(P.subprocess,'Popen',return_value=proc),mock.patch.object(P.selectors,'DefaultSelector',return_value=Selector()),mock.patch.object(P.os,'set_blocking'):
 try:P.SubprocessDocker._run(['/usr/bin/docker','inspect'],deadline=time.monotonic()+5)
 except OSError:pass
 else:raise RuntimeError('MISSING_CLOSE_ERROR')
if not proc.stdout.closed or proc.stderr.closed:raise RuntimeError('COUNTEREXAMPLE_NOT_REPRODUCED')
found.append({'id':'R01a','result':'stdout.close failure skips stderr.close; owned stream remains open','process_waited':proc.waits})
proc=Proc(False)
with mock.patch.object(P.subprocess,'Popen',return_value=proc),mock.patch.object(P.selectors,'DefaultSelector',side_effect=OSError('inert selector allocation failure')):
 try:P.SubprocessDocker._run(['/usr/bin/docker','inspect'],deadline=time.monotonic()+5)
 except OSError:pass
 else:raise RuntimeError('MISSING_SELECTOR_ERROR')
if proc.stdout.closed or proc.stderr.closed or proc.waits:raise RuntimeError('SETUP_COUNTEREXAMPLE_NOT_REPRODUCED')
found.append({'id':'R01b','result':'selector setup failure after Popen skips both pipe closes and any process reap/cleanup'})
for p,digest in pins.items():
 if h(Path(p).read_bytes())!=digest:raise RuntimeError('POST_DRIFT')
if os.path.lexists(S.DOCKER_ATTEMPT):raise RuntimeError('DOCKER_ATTEMPT_CREATED')
print(json.dumps({'author_tests':res.testsRun,'preflight':pre,'pins':pins,'findings':found,'readonly_commands':commands,'actual_docker_effect':'NOT_RUN','archive_body_opened':False},sort_keys=True,indent=2))
