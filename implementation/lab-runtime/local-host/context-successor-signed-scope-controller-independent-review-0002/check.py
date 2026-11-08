from pathlib import Path
import os,sys,json,hashlib,stat,tempfile,unittest
from unittest.mock import patch
CAND=Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-successor-signed-scope-controller-0002');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(CAND/'freeze.json')=='be4fad673eb559ddf810fae4b0bfa8e288c46c8c68b1e90902310d8deb8c8bc7';f=json.loads((CAND/'freeze.json').read_bytes())
for n,d in f['members'].items():assert h(CAND/n)==d
sys.path.insert(0,str(CAND));sys.path.append('/usr/lib/python3/dist-packages')
def guard(event,args):
 if event=='open' and str(args[0]).endswith('branch.snapshot'):raise RuntimeError('PRIVATE_ARCHIVE_FORBIDDEN')
 if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.fork','os.exec'):raise RuntimeError('EFFECT_FORBIDDEN')
sys.addaudithook(guard)
import controller as C,test_controller as T
class Extra(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s=C.preflight(T.NOW)['selected']
 def fixture(self):return tempfile.TemporaryDirectory(prefix='fixture-signed-scope-review-',dir='/tmp')
 def test_exact_created_inode_bound(self):
  with self.fixture() as root:
   real=os.open;ids=[]
   def track(name,flags,*args,**kw):
    fd=real(name,flags,*args,**kw)
    if name=='attempt.claim' and flags&os.O_EXCL:ids.append((os.fstat(fd).st_dev,os.fstat(fd).st_ino))
    return fd
   with patch.object(C.os,'open',side_effect=track):r=C.run_fixture_once(root,self.s)
   marker=json.loads((Path(root)/'attempt.claim').read_bytes());att=json.loads((Path(root)/'signed-scope.attestation.json').read_bytes())
   self.assertEqual(ids,[(marker['attempt_dev'],marker['attempt_ino'])]);self.assertEqual(ids,[(att['attempt_dev'],att['attempt_ino'])]);self.assertEqual(r['marker_sha256'],att['consumed_marker_sha256'])
 def test_marker_fsync_failure_blocks_open_no_retry(self):
  with self.fixture() as root:
   real=os.fsync;r=C.SyntheticSelectedReader(self.s)
   def fail(fd):
    if stat.S_ISREG(os.fstat(fd).st_mode):raise OSError('fixture fsync')
    return real(fd)
   with patch.object(C.os,'fsync',side_effect=fail),self.assertRaises(C.Unknown):C.run_fixture_once(root,self.s,reader=r)
   self.assertEqual(r.calls,[])
   with self.assertRaises(C.Refused):C.run_fixture_once(root,self.s)
 def test_marker_readback_failure_blocks_open(self):
  with self.fixture() as root:
   real=os.read;r=C.SyntheticSelectedReader(self.s)
   def bad(fd,n):
    data=real(fd,n)
    if os.readlink('/proc/self/fd/'+str(fd))==str(Path(root)/'attempt.claim'):return b'wrong'
    return data
   with patch.object(C.os,'read',side_effect=bad),self.assertRaises(C.Unknown):C.run_fixture_once(root,self.s,reader=r)
   self.assertEqual(r.calls,[]);self.assertFalse((Path(root)/'signed-scope.attestation.json').exists())
 def test_postmarker_parent_detach_blocks_open(self):
  with self.fixture() as root:
   root=Path(root);detached=root.with_name(root.name+'-detached');real=C._write_claim_held;r=C.SyntheticSelectedReader(self.s)
   def swap(*args):
    digest=real(*args);root.rename(detached);root.mkdir(mode=0o700);return digest
   try:
    with patch.object(C,'_write_claim_held',side_effect=swap),self.assertRaises(C.Unknown):C.run_fixture_once(root,self.s,reader=r)
    self.assertEqual(r.calls,[]);self.assertEqual(list(root.iterdir()),[]);self.assertTrue((detached/'attempt.claim').is_file())
   finally:
    root.rmdir();detached.rename(root)
 def test_ambiguous_final_claim_close_keeps_unknown_and_closes_parent(self):
  with self.fixture() as root:
   realopen=os.open;realclose=os.close;claim=[];parent=[];counts={}
   def opened(name,*a,**kw):
    fd=realopen(name,*a,**kw)
    if str(name)==str(root):parent.append(fd)
    if name=='attempt.claim':claim.append(fd)
    return fd
   def close(fd):
    counts[fd]=counts.get(fd,0)+1;realclose(fd)
    if claim and fd==claim[0]:raise OSError('fixture real-close-then-raise')
   with patch.object(C.os,'open',side_effect=opened),patch.object(C.os,'close',side_effect=close),self.assertRaises(C.Unknown):C.run_fixture_once(root,self.s)
   self.assertEqual(counts[claim[0]],1)
   with self.assertRaises(OSError):os.fstat(parent[-1])
   self.assertTrue((Path(root)/'signed-scope.attestation.json').exists())
   with self.assertRaises(C.Refused):C.run_fixture_once(root,self.s)
 def test_changed_public_review_before_open_refuses(self):
  with self.fixture() as root:
   real=C.preflight;calls=[];r=C.SyntheticSelectedReader(self.s)
   def changed(now=None):
    result=real(now);calls.append(1)
    if len(calls)>1:result['selected']['mapper_effect_review_sha256']='0'*64
    return result
   with patch.object(C,'preflight',side_effect=changed),self.assertRaises(C.Unknown):C.run_fixture_once(root,self.s,reader=r)
   self.assertEqual(r.calls,[])
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(T),unittest.defaultTestLoader.loadTestsFromTestCase(Extra)]);r=unittest.TextTestRunner(verbosity=2).run(suite)
for n,d in f['members'].items():assert h(CAND/n)==d
v=C.preflight();print(json.dumps({'tests':r.testsRun,'success':r.wasSuccessful(),'current_status':v['status'],'period_end':v['source_period_end'],'real_attempt_absent':not C.ATTEMPT.exists(),'attestation_absent':not C.ATTESTATION.exists(),'private_archive':'UNOPENED'}));sys.exit(not r.wasSuccessful())
