import sys,pathlib,json,hashlib,types,unittest,tempfile,shutil,os,stat
from unittest import mock
L=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host');C=L/'context-signed-scope-portable-bundle-0002'
B=pathlib.Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-signed-scope-portable-bundle-0001')
F='b6a57791f21464e5b3bb8b568cd9cbbf42c96288528fc68e622cb7d70afd2d7f'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok):
 if not ok:raise RuntimeError('PIN_DRIFT')
fraw=(C/'freeze.json').read_bytes();need(sha(fraw)==F);f=json.loads(fraw)
for n,h in f['members'].items():need(sha((C/n).read_bytes())==h)
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)) and 'branch.snapshot' in str(args[0]):raise RuntimeError('PRIVATE_ARCHIVE_FORBIDDEN')
 if event in ('subprocess.Popen','os.system'):raise RuntimeError('PROCESS_EFFECT_FORBIDDEN')
sys.addaudithook(audit);sys.path.insert(0,'/usr/lib/python3/dist-packages')
p=types.ModuleType('portable');p.__file__=str(C/'portable.py');sys.modules['portable']=p;exec(compile((C/'portable.py').read_bytes(),p.__file__,'exec'),p.__dict__)
t=types.ModuleType('author_tests');t.__file__=str(C/'test_portable.py');exec(compile((C/'test_portable.py').read_bytes(),t.__file__,'exec'),t.__dict__)
manifest=p.parse((B/'manifest.json').read_bytes());need(sha((B/'manifest.json').read_bytes())==p.BUNDLE_MANIFEST_SHA)
loader_raw=(p.LOADER/'checked_loader.py').read_bytes();need(sha(loader_raw)==p.LOADER_CODE_SHA)
@classmethod
def setup(cls):
 cls.bundle_tmp=tempfile.TemporaryDirectory(prefix='review-public-bundle-')
 cls.stage_tmp=tempfile.TemporaryDirectory(prefix='fixture-portable-stage-')
 cls.bundle=pathlib.Path(cls.bundle_tmp.name)/'bundle';shutil.copytree(B,cls.bundle)
 cls.stage=pathlib.Path(cls.stage_tmp.name)/'root'
 p.materialize_synthetic_stage(cls.bundle,p.BUNDLE_MANIFEST_SHA,cls.stage)
 cls.result={'manifest_sha256':p.BUNDLE_MANIFEST_SHA}
t.PortableTests.setUpClass=setup
class Independent(unittest.TestCase):
 def test_retained_old_bundle_and_future_absence(self):
  self.assertEqual(p.audit_bundle(B)['blobs'],105);self.assertFalse(os.path.lexists(p.DEFAULT_BUNDLE))
 def test_exact_blob_missing_type_link_negatives(self):
  for kind in ['missing','symlink','directory','fifo','hardlink']:
   with self.subTest(kind=kind),tempfile.TemporaryDirectory(prefix='review-public-bundle-') as tmp:
    dest=pathlib.Path(tmp)/'bundle';shutil.copytree(B,dest);blob=dest/'blobs'/p.LOADER_CODE_SHA;raw=blob.read_bytes();blob.unlink()
    if kind=='symlink':blob.symlink_to(B/'blobs'/p.LOADER_CODE_SHA)
    elif kind=='directory':blob.mkdir(mode=0o600)
    elif kind=='fifo':os.mkfifo(blob,0o600)
    elif kind=='hardlink':
     other=pathlib.Path(tmp)/'other';other.write_bytes(raw);other.chmod(0o600);os.link(other,blob)
    with self.assertRaises((p.Refused,OSError)):p.audit_bundle(dest)
 def test_manifest_links_and_root_alias_refuse(self):
  for kind in ['symlink','hardlink','root-symlink']:
   with self.subTest(kind=kind),tempfile.TemporaryDirectory(prefix='review-public-bundle-') as tmp:
    dest=pathlib.Path(tmp)/'bundle';shutil.copytree(B,dest);target=dest
    if kind=='root-symlink':target=pathlib.Path(tmp)/'alias';target.symlink_to(dest,target_is_directory=True)
    else:
     leaf=dest/'manifest.json';raw=leaf.read_bytes();leaf.unlink()
     if kind=='symlink':leaf.symlink_to(B/'manifest.json')
     else:
      other=pathlib.Path(tmp)/'other';other.write_bytes(raw);other.chmod(0o600);os.link(other,leaf)
    with self.assertRaises((p.Refused,OSError)):p.audit_bundle(target)
 def virtual_publish(self,fault=None):
  target=pathlib.Path('/tmp/fixture-portable-bundle-virtual/bundle');events=[];created=set();fds={};closed=[]
  def mkdir(path,*args,**kw):created.add(str(path));events.append(('mkdir',str(path)))
  def opened(path,*args,**kw):fd=100+len(fds);fds[fd]=str(path);events.append(('open',str(path)));return fd
  def synced(fd):
   events.append(('fsync',fds[fd]))
   if fault=='sync' and fds[fd]==str(target.parent):raise OSError('inert-sync')
  def closed_fd(fd):
   closed.append(fd);events.append(('close',fds[fd]))
   if fault=='close' and fds[fd]==str(target.parent):raise OSError('inert-close')
  capture=types.SimpleNamespace(code={},metadata_buffers={})
  with mock.patch.object(p,'reviewed_loader',return_value=types.SimpleNamespace(capture=lambda _:capture)),mock.patch.object(p,'export_manifest',return_value=manifest),mock.patch.object(p,'held_file',return_value=loader_raw),mock.patch.object(p,'write_exclusive',side_effect=lambda *a:events.append(('write',str(a[0])))),mock.patch.object(p,'audit_bundle',side_effect=lambda _:events.append(('audit',str(target)))),mock.patch.object(p.os,'stat',return_value=types.SimpleNamespace(st_mode=stat.S_IFDIR|0o700,st_uid=os.getuid())),mock.patch.object(p.os.path,'lexists',side_effect=lambda x:str(x) in created),mock.patch.object(p.os,'mkdir',side_effect=mkdir),mock.patch.object(p.os,'open',side_effect=opened),mock.patch.object(p.os,'fsync',side_effect=synced),mock.patch.object(p.os,'close',side_effect=closed_fd):
   if fault:
    with self.assertRaisesRegex(p.Refused,'PARENT_FSYNC_UNKNOWN_CONSUMED_NO_RETRY'):p.publish(target,t.NOW)
    with self.assertRaisesRegex(p.Refused,'BUNDLE_PARENT_OR_EXISTING'):p.publish(target,t.NOW)
   else:self.assertEqual(p.publish(target,t.NOW)['manifest_sha256'],p.BUNDLE_MANIFEST_SHA)
  self.assertEqual(len(closed),len(set(closed)));self.assertEqual(set(closed),set(fds))
  self.assertLess(events.index(('audit',str(target))),events.index(('fsync',str(target.parent))))
  self.assertEqual(events[-1],('close',str(target.parent)))
 def test_parent_sync_order_virtual(self):self.virtual_publish()
 def test_parent_sync_failure_unknown_no_retry_virtual(self):self.virtual_publish('sync')
 def test_parent_close_failure_unknown_no_retry_virtual(self):self.virtual_publish('close')
author=unittest.TestSuite(t.PortableTests(n) for n in unittest.defaultTestLoader.getTestCaseNames(t.PortableTests) if n not in {'test_publish_fsyncs_containing_parent_after_bundle','test_parent_fsync_failure_is_unknown_and_no_retry'})
result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([author,unittest.defaultTestLoader.loadTestsFromTestCase(Independent)]))
for n,h in f['members'].items():need(sha((C/n).read_bytes())==h)
need(not os.path.lexists(p.DEFAULT_BUNDLE));need(p.audit_bundle(B)['blobs']==105)
raise SystemExit(0 if result.wasSuccessful() else 1)
