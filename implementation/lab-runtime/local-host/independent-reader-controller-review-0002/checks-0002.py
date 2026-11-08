import sys,pathlib,hashlib,json,unittest,tempfile,os,io
from unittest.mock import patch
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');C=R/'implementation/lab-runtime/local-host/reader-only-docker-controller-0002'
def sha(b):return hashlib.sha256(b).hexdigest()
fraw=(C/'freeze.json').read_bytes();f=json.loads(fraw)
def verify():
 for r in f['file_bindings']:
  b=(C/r['path']).read_bytes()
  if len(b)!=r['size'] or sha(b)!=r['sha256']:raise RuntimeError('freeze drift')
verify();children=[]
allowed={"import sys;sys.stdout.write('x'*100);sys.stderr.write('y'*100)","print('would-be-log')","import sys;sys.stdout.write('x'*100000)"}
def guard(event,args):
 if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)) and os.fsdecode(args[0]).endswith('branch.snapshot'):raise RuntimeError('archive open prohibited')
 if event in ('subprocess.Popen','os.posix_spawn'):
  executable,argv=args[:2]
  if executable!=sys.executable or argv[1:3]!=['-B','-c'] or argv[3] not in allowed:raise RuntimeError('unselected process launch prohibited')
  if event=='subprocess.Popen':children.append(argv)
 if event in ('os.system','os.fork'):raise RuntimeError('process launch prohibited')
sys.addaudithook(guard);sys.path.insert(0,str(C));import controller as c,test_controller as t
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t));obs=[]
# All inputs owned; no real process belongs to the fake client below.
class Child:
 def __init__(self):self.stdout=io.BytesIO();self.stderr=io.BytesIO();self.calls=[]
 def poll(self):return None
 def terminate(self):self.calls.append('terminate');raise OSError('synthetic terminate fault')
 def kill(self):self.calls.append('kill')
 def wait(self,**kwargs):self.calls.append('wait');return 0
child=Child();primary=ValueError('synthetic selector setup');raised=None
with patch.object(c.subprocess,'Popen',return_value=child),patch.object(c.selectors,'DefaultSelector',side_effect=primary):
 try:c.cli(['unexecuted-fake'])
 except BaseException as error:raised=error
obs.append({'case':'cli_cleanup_terminate_fault','primary_preserved':raised is primary,'raised_type':type(raised).__name__,'stdout_closed':child.stdout.closed,'stderr_closed':child.stderr.closed,'calls':child.calls,'fake_child_no_real_pid':True})
child.stdout.close();child.stderr.close()
with tempfile.TemporaryDirectory(prefix='review-controller-') as temp:
 realclose=os.close;realopen=os.open;opened=[];attempted=[]
 def op(*args,**kwargs):
  fd=realopen(*args,**kwargs);opened.append(fd);return fd
 def cl(fd):
  attempted.append(fd);realclose(fd)
  if len(attempted)==1:raise OSError('synthetic close after actual close')
 try:
  with patch.object(c.os,'open',op),patch.object(c.os,'close',cl):
   with c.held_directory(pathlib.Path(temp)):pass
 except OSError:pass
 leaked=[]
 for fd in opened:
  try:os.fstat(fd)
  except OSError:continue
  leaked.append(fd);realclose(fd)
 obs.append({'case':'held_directory_close_fault','opened':len(opened),'attempted':len(attempted),'remaining':len(leaked),'reviewer_closed_remaining':True})
verify();print(json.dumps({'tests':result.testsRun,'passed':result.wasSuccessful(),'freeze_sha256':sha(fraw),'members':len(f['file_bindings']),'observations':obs,'selected_local_python_children':len(children),'docker_launched':False,'archive_body_opened':False,'candidate_modified':False,'post_verified':True},sort_keys=True));sys.exit(0 if result.wasSuccessful() else 1)
