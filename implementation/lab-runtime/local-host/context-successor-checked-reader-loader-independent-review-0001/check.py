from pathlib import Path
import sys,hashlib,json,unittest,types,importlib,os
from unittest.mock import patch
C=Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-successor-checked-reader-loader-0001');E=Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(C/'freeze.json')=='34dc11dc1977b47ef67f7ab9b900945e86cb8afa618b8c8845af3b56f90e979c';f=json.loads((C/'freeze.json').read_bytes())
for n,d in f['members'].items():assert h(C/n)==d
sys.path.insert(0,str(C));sys.path.append('/usr/lib/python3/dist-packages')
def audit(event,args):
 if event=='open' and str(args[0]).endswith('branch.snapshot'):raise RuntimeError('PRIVATE_ARCHIVE_DISABLED')
 if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.fork','os.exec','os.mkdir','os.remove','os.rename','os.rmdir'):raise RuntimeError('EFFECT_DISABLED')
sys.addaudithook(audit)
import checked_loader as c,test_checked_loader as T
class Extra(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.capture=c.capture()
 def test_full_counts_and_exact_reader_bytes(self):
  x=self.capture;self.assertEqual((len(x.source_manifest['files']),len(x.reader_rows),len(x.code),len(x.metadata_buffers)),(940,948,40,85))
  self.assertEqual(c.sha(x.code[str(c.ROOT/c.READER_ROLE/'reader.py')]),c.READER_CODE_SHA)
 def test_preloaded_module_is_refused_not_removed(self):
  sentinel=types.ModuleType(c.READER_NAME)
  with patch.dict(sys.modules,{c.READER_NAME:sentinel}):
   with self.assertRaisesRegex(c.Refused,'SELECTED_MODULE_ALREADY_LOADED'):
    with c.checked_modules(self.capture):pass
   self.assertIs(sys.modules[c.READER_NAME],sentinel)
 def test_os_code_reopen_forbidden_and_cleanup(self):
  real=c.os.open
  def blocked(path,*args,**kw):
   if str(path).endswith('.py') and (str(path).startswith(str(c.ROOT)) or not Path(path).is_absolute()):raise AssertionError('STAGED_CODE_OPEN')
   return real(path,*args,**kw)
  old=importlib.util.spec_from_file_location;meta=list(sys.meta_path)
  with patch.object(c.os,'open',blocked):
   with c.checked_modules(self.capture) as (r,finder):
    self.assertTrue(callable(r.SelectedReader.open_signed));self.assertGreaterEqual(len(finder.executed),13)
  self.assertIs(importlib.util.spec_from_file_location,old);self.assertEqual(sys.meta_path,meta);self.assertNotIn(c.READER_NAME,sys.modules)
 def test_post_context_metadata_failure_refuses_and_unloads(self):
  x=c.capture();key=next(iter(x.metadata_buffers));old=importlib.util.spec_from_file_location
  with self.assertRaisesRegex(c.Refused,'CAPTURED_METADATA_BUFFER_DRIFT'):
   with c.checked_modules(x):x.metadata_buffers[key]+=b'x'
  self.assertIs(importlib.util.spec_from_file_location,old);self.assertNotIn(c.READER_NAME,sys.modules)
 def test_all_named_dynamic_paths_closed(self):
  x=self.capture
  for name,path in [(c.SOURCE_NAME,c.ROOT/c.SOURCE_ROLE/'__init__.py'),(c.ENGINE_LOADER_NAME,c.ROOT/c.CORRECTION_ROLE/'loader.py'),(c.BRIDGE_NAME,c.ROOT/c.CORRECTION_ROLE/'reader_adapter.py')]:
   finder=c.CheckedFinder(x);kw={'submodule_search_locations':[str(path.parent)]} if name==c.SOURCE_NAME else {}
   spec=finder.checked_spec_from_file_location(name,path,**kw);self.assertEqual(c.sha(spec.loader.raw),x.code_digests[str(path)])
   with self.assertRaises(c.Refused):finder.checked_spec_from_file_location(name,path.parent/'wrong.py',**kw)
 def test_host_mismatch_and_no_actual_open(self):
  s=self.capture.summary();self.assertFalse(s['host_environment_matches']);self.assertEqual(s['source_required_environment']['jsonschema'],'4.23.0');self.assertEqual(s['host_environment']['jsonschema'],'4.19.2')
  with self.assertRaisesRegex(c.Refused,'EFFECT_DISABLED'):c.open_actual_signed()
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(T),unittest.defaultTestLoader.loadTestsFromTestCase(Extra)])
r=unittest.TextTestRunner(verbosity=2).run(suite)
for n,d in f['members'].items():assert h(C/n)==d
print(json.dumps({'tests':r.testsRun,'success':r.wasSuccessful(),'summary':Extra.capture.summary(),'private_archive':'UNOPENED','reader_instantiated':False},sort_keys=True));sys.exit(not r.wasSuccessful())
