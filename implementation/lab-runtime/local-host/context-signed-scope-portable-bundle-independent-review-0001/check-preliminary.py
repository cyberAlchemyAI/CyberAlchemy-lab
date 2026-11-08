import sys, pathlib, hashlib, json, types, unittest, os, tempfile, shutil
from unittest import mock
L=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
C=L/'context-signed-scope-portable-bundle-0001'
F='47f593a19daaa0f3c74735b1d478650c7281100a4f5c243a88a9348c3bcacad3'
def sha(b):return hashlib.sha256(b).hexdigest()
raw=(C/'freeze.json').read_bytes();assert sha(raw)==F
freeze=json.loads(raw)
for name,digest in freeze['members'].items():assert sha((C/name).read_bytes())==digest
sys.path.insert(0,'/usr/lib/python3/dist-packages')
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)) and 'branch.snapshot' in str(args[0]):raise RuntimeError('REVIEW_PRIVATE_OPEN_REFUSED')
 if event in ('subprocess.Popen','os.system'):raise RuntimeError('REVIEW_PROCESS_EFFECT_REFUSED')
sys.addaudithook(audit)
p=types.ModuleType('portable');p.__file__=str(C/'portable.py');sys.modules['portable']=p
exec(compile((C/'portable.py').read_bytes(),p.__file__,'exec'),p.__dict__)
t=types.ModuleType('test_portable');t.__file__=str(C/'test_portable.py');exec(compile((C/'test_portable.py').read_bytes(),t.__file__,'exec'),t.__dict__)
class Independent(unittest.TestCase):
 def test_current_bundle_exact(self):
  p.audit_bundle()
  root=p.DEFAULT_BUNDLE
  self.assertEqual({x.name for x in root.iterdir()},{'manifest.json','blobs'})
  for f in [root/'manifest.json',*list((root/'blobs').iterdir())]:self.assertEqual(f.stat().st_mode&0o777,0o600)
 def test_extra_root_entry_is_accepted_counterexample(self):
  with tempfile.TemporaryDirectory(prefix='review-public-bundle-') as tmp:
   dest=pathlib.Path(tmp)/'bundle';shutil.copytree(p.DEFAULT_BUNDLE,dest)
   (dest/'unselected.txt').write_bytes(b'inert public extra')
   self.assertEqual(p.audit_bundle(dest)['blobs'],105)
 def test_blob_mode_drift_is_accepted_counterexample(self):
  with tempfile.TemporaryDirectory(prefix='review-public-bundle-') as tmp:
   dest=pathlib.Path(tmp)/'bundle';shutil.copytree(p.DEFAULT_BUNDLE,dest)
   (dest/'blobs'/p.LOADER_CODE_SHA).chmod(0o644)
   self.assertEqual(p.audit_bundle(dest)['blobs'],105)
 def test_publish_omits_parent_fsync_counterexample(self):
  with tempfile.TemporaryDirectory(prefix='fixture-portable-bundle-',dir=p.FAMILY) as tmp:
   dest=pathlib.Path(tmp)/'bundle';seen=[];real=os.fsync
   def record(fd):
    seen.append(os.readlink('/proc/self/fd/'+str(fd)));return real(fd)
   with mock.patch.object(os,'fsync',record):p.publish(dest,t.NOW)
   self.assertIn(str(dest),seen);self.assertIn(str(dest/'blobs'),seen)
   self.assertNotIn(str(dest.parent),seen)
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(t),unittest.defaultTestLoader.loadTestsFromTestCase(Independent)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
for name,digest in freeze['members'].items():
 if sha((C/name).read_bytes())!=digest:raise RuntimeError('POST_DRIFT')
raise SystemExit(0 if result.wasSuccessful() else 1)
