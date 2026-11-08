import sys,pathlib,json,hashlib,types,unittest,tempfile,os,stat,errno
from unittest import mock
L=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host');C=L/'context-signed-scope-public-topology-probe-0002'
F='4298005af963791b5ff3b12a4440a26ab10f136b86cfda1b1998a854b2ac7d57'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok):
 if not ok:raise RuntimeError('PIN_DRIFT')
f=json.loads((C/'freeze.json').read_bytes());need(sha((C/'freeze.json').read_bytes())==F)
for n,h in f['members'].items():need(sha((C/n).read_bytes())==h)
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)) and 'branch.snapshot' in str(args[0]) and 'fixture-signed-scope-topology-' not in str(args[0]):raise RuntimeError('PRIVATE_READ_FORBIDDEN')
 if event in ('subprocess.Popen','os.system'):raise RuntimeError('DOCKER_OR_PROCESS_FORBIDDEN')
sys.addaudithook(audit)
def load(name,file):
 m=types.ModuleType(name);m.__file__=str(C/file);sys.modules[name]=m;exec(compile((C/file).read_bytes(),m.__file__,'exec'),m.__dict__);return m
p=load('probe','probe.py');c=load('child','child.py');t=load('author_tests','test_probe.py')
class Independent(unittest.TestCase):
 def test_prior_short_read_nested_counterexample_now_refuses(self):
  line=lambda target:f'1 0 0:1 / {target} ro - ext4 /dev/x ro\n'.encode()
  prefix=b''.join(line(target) for target in c.TARGETS);tail=line(c.TARGETS[0]+'/nested')
  with tempfile.TemporaryDirectory(prefix='review-public-topology-') as tmp:
   path=pathlib.Path(tmp)/'mountinfo';path.write_bytes(prefix+tail);real=os.read
   observed=c.read_bounded(path,128*1024,read_fn=lambda fd,n:real(fd,min(n,len(prefix))))
   self.assertEqual(observed,prefix+tail)
   with self.assertRaisesRegex(RuntimeError,'NESTED_MOUNT'):c.mountinfo_ro(observed)
   with self.assertRaisesRegex(RuntimeError,'NESTED_MOUNT'):c.mountinfo_ro(path.read_bytes())
 def test_prior_full_child_short_read_counterexample_now_refuses(self):
  line=lambda target:f'1 0 0:1 / {target} ro - ext4 /dev/x ro\n'.encode()
  prefix=b''.join(line(target) for target in c.TARGETS);tail=line(c.TARGETS[1]+'/nested')
  config={'claim_dev':1,'claim_ino':2,'stage_marker_sha256':sha(p.STAGE_MARKER),'claim_marker_sha256':sha(p.CLAIM_MARKER)}
  with tempfile.TemporaryDirectory(prefix='review-public-topology-') as tmp:
   tmp=pathlib.Path(tmp);stage=tmp/'stage';claim=tmp/'claim';mount=tmp/'mount';stage.write_bytes(p.STAGE_MARKER);claim.write_bytes(p.CLAIM_MARKER);mount.write_bytes(prefix+tail)
   realopen=os.open;realread=os.read;mountfds=set()
   def opened(path,*a,**kw):
    mapped={str(c.STAGE/c.MARKER):stage,str(c.CLAIM):claim,'/proc/self/mountinfo':mount}[str(path)]
    fd=realopen(mapped,*a,**kw)
    if mapped==mount:mountfds.add(fd)
    else:mountfds.discard(fd)
    return fd
   def read(fd,n):return realread(fd,min(n,len(prefix)) if fd in mountfds else n)
   original_read=c.read_bounded
   def bounded(path,maximum):return original_read(path,maximum,read_fn=read,open_fn=opened)
   with mock.patch.object(c,'read_bounded',side_effect=bounded), mock.patch.object(c.os,'open',side_effect=opened),mock.patch.object(c.os,'read',side_effect=read),mock.patch.object(c.os,'stat',return_value=types.SimpleNamespace(st_mode=stat.S_IFREG|0o600,st_dev=1,st_ino=2)),mock.patch.object(c.os,'getuid',return_value=1000),mock.patch.object(c.os,'getgid',return_value=1000),mock.patch.object(c.os,'listdir',side_effect=lambda path:[c.MARKER] if path==c.STAGE else ['manifest.json','blobs']),mock.patch.object(c.importlib.metadata,'version',side_effect=lambda name:{'jsonschema':'4.23.0','cryptography':'46.0.5'}[name]),mock.patch.object(c,'erofs_create',return_value=errno.EROFS),mock.patch.object(c,'erofs_claim_write',return_value=errno.EROFS):
    with self.assertRaisesRegex(RuntimeError,'NESTED_MOUNT'):c.run(config)
 def test_three_fixed_targets_reject_all_simple_nested_and_rw(self):
  line=lambda target,mode='ro':f'1 0 0:1 / {target} {mode} - ext4 /dev/x rw\n'.encode()
  good=b''.join(line(x) for x in c.TARGETS)
  for target in c.TARGETS:
   for bad in [good+line(target+'/nested'),good.replace(line(target),line(target,'rw')),good.replace(line(target),b'')]:
    with self.subTest(target=target),self.assertRaises(RuntimeError):c.mountinfo_ro(bad)
 def test_complete_chunked_and_exact_byte_budget(self):
  closed=[];parts=iter([b'a'*65536,b'b'*65536,b''])
  raw=c.read_bounded('/public',128*1024,read_fn=lambda *_:next(parts),open_fn=lambda *_:91,close_fn=closed.append,clock_fn=lambda:0)
  self.assertEqual(len(raw),128*1024);self.assertEqual(closed,[91])
  for blocks in [[b'a'*65536,b'b'*65536,b'c'],[b''],[bytearray(b'bad')]]:
   closed=[];parts=iter(blocks)
   with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_BOUND|PUBLIC_READ_TYPE'):
    c.read_bounded('/public',128*1024,read_fn=lambda *_:next(parts),open_fn=lambda *_:91,close_fn=closed.append,clock_fn=lambda:0)
   self.assertEqual(closed,[91])
 def test_calls_time_and_close_uncertainty(self):
  closed=[];calls=[]
  def endless(*_):calls.append(1);return b'a'
  with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_INCOMPLETE'):
   c.read_bounded('/public',128*1024,read_fn=endless,open_fn=lambda *_:91,close_fn=closed.append,clock_fn=lambda:0)
  self.assertEqual(len(calls),4096);self.assertEqual(closed,[91])
  closed=[];clock=iter([0,0,2.001])
  with self.assertRaisesRegex(RuntimeError,'PUBLIC_READ_INCOMPLETE'):
   c.read_bounded('/public',10,read_fn=lambda *_:b'abc',open_fn=lambda *_:91,close_fn=closed.append,clock_fn=lambda:next(clock))
  self.assertEqual(closed,[91])
  def close_fault(fd):closed.append(fd);raise OSError('inert close uncertainty')
  parts=iter([b'a',b'']);closed=[]
  with self.assertRaises(OSError):c.read_bounded('/public',10,read_fn=lambda *_:next(parts),open_fn=lambda *_:91,close_fn=close_fault,clock_fn=lambda:0)
  self.assertEqual(closed,[91])
 def test_basis_and_effect_refusal(self):
  self.assertEqual(p.basis()['effect'],'NOT_RUN')
  with self.assertRaisesRegex(p.Refused,'EFFECT_DISABLED'):p.dispatch()
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(t),unittest.defaultTestLoader.loadTestsFromTestCase(Independent)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
for n,h in f['members'].items():need(sha((C/n).read_bytes())==h)
raise SystemExit(0 if result.wasSuccessful() else 1)
